"""
Alerting Layer — Offline Text-to-Speech Manager
=================================================
Priority-queue based TTS using Piper for offline voice alerts.
Provides sub-300ms latency audio with pre-caching.
Falls back to pyttsx3 if Piper is not available.
"""

import threading
import queue
import logging
import time
import io
import wave
import os
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Try to import piper and sounddevice
try:
    from piper.voice import PiperVoice
    import sounddevice as sd
    import numpy as np
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logger.warning("piper-tts or sounddevice not installed. Will fallback to pyttsx3.")

# Fallback
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class AlertPriority(IntEnum):
    """Alert priority levels (lower number = higher priority)."""
    CRITICAL = 1        # Skipped step, out-of-sequence
    WARNING = 2         # Low confidence, precondition failed
    INFO = 3            # Step completed
    SUGGESTION = 4      # Next step suggestion
    STATUS = 5          # Experiment complete, status updates


@dataclass(order=True)
class AlertMessage:
    """A prioritized alert message for TTS."""
    priority: int
    timestamp: float = field(compare=False)
    message: str = field(compare=False)
    alert_type: str = field(compare=False, default="info")
    prefix: str = field(compare=False, default="")


class TTSManager:
    """
    Non-blocking, priority-queued Text-to-Speech manager.
    
    Uses Piper TTS for fast neural speech generation.
    Pre-caches common prefixes to reduce latency.
    """

    # Voice properties per alert type
    ALERT_CONFIGS = {
        "skipped_step":     {"priority": AlertPriority.CRITICAL, "rate": 1.2, "prefix": "Warning!"},
        "out_of_sequence":  {"priority": AlertPriority.CRITICAL, "rate": 1.2, "prefix": "Alert!"},
        "precondition":     {"priority": AlertPriority.WARNING,  "rate": 1.1, "prefix": "Cannot proceed."},
        "duration_anomaly": {"priority": AlertPriority.WARNING,  "rate": 1.1, "prefix": "Timing anomaly."},
        "uncertain":        {"priority": AlertPriority.WARNING,  "rate": 1.0, "prefix": "Please verify."},
        "step_completed":   {"priority": AlertPriority.INFO,     "rate": 1.0, "prefix": "Step completed."},
        "experiment_start": {"priority": AlertPriority.INFO,     "rate": 1.0, "prefix": "Experiment started."},
        "next_step":        {"priority": AlertPriority.SUGGESTION, "rate": 1.0, "prefix": "Next step:"},
        "experiment_done":  {"priority": AlertPriority.STATUS,   "rate": 0.9, "prefix": "Experiment complete."},
    }

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.engine_type = config.get("engine", "piper")
        self.piper_model = config.get("piper_model", "en_US-lessac-medium.onnx")
        self.volume = config.get("voice_volume", 0.9)
        self.cooldown = config.get("alert_cooldown", 3.0)

        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_alert_times: dict = {}
        self._engine_available = False
        
        # Audio cache for Piper
        self._audio_cache: Dict[str, np.ndarray] = {}
        self._sample_rate = 22050

    def start(self):
        """Start the TTS background thread."""
        if not self.enabled:
            logger.info("TTS alerts disabled in config")
            return

        self._running = True
        self._thread = threading.Thread(target=self._tts_loop, daemon=True)
        self._thread.start()
        logger.info("TTSManager started")

    def stop(self):
        """Stop the TTS thread."""
        self._running = False
        self._queue.put(AlertMessage(
            priority=99, timestamp=time.time(), message="__STOP__"
        ))
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None
        logger.info("TTSManager stopped")

    def alert(self, alert_type: str, message: str):
        """Queue an alert for speaking."""
        if not self.enabled or not self._running:
            return

        now = time.time()
        last_time = self._last_alert_times.get(alert_type, 0)
        if now - last_time < self.cooldown:
            logger.debug(f"Alert '{alert_type}' on cooldown, skipping")
            return

        config = self.ALERT_CONFIGS.get(alert_type, {
            "priority": AlertPriority.STATUS,
            "rate": 1.0,
            "prefix": ""
        })

        full_message = f"{config['prefix']} {message}" if config.get("prefix") else message

        alert = AlertMessage(
            priority=config["priority"],
            timestamp=now,
            message=full_message,
            alert_type=alert_type,
            prefix=config.get("prefix", "")
        )

        self._queue.put(alert)
        self._last_alert_times[alert_type] = now
        logger.debug(f"Queued alert: [{alert_type}] {full_message}")

    def _tts_loop(self):
        """Background thread loop for processing TTS queue."""
        if self.engine_type == "piper" and PIPER_AVAILABLE:
            self._run_piper_loop()
        elif PYTTSX3_AVAILABLE:
            logger.info("Piper not available, falling back to pyttsx3")
            self._run_pyttsx3_loop()
        else:
            logger.error("No TTS engine available (piper or pyttsx3). Audio alerts disabled.")
            self._engine_available = False
            self._running = False

    def _run_piper_loop(self):
        """Run Piper TTS engine with sounddevice."""
        try:
            # Look for model in standard locations or download dir
            model_path = self.piper_model
            if not os.path.exists(model_path):
                # Check data directory
                model_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", self.piper_model)
                
            if not os.path.exists(model_path):
                logger.warning(f"Piper model {self.piper_model} not found. Ensure it's downloaded.")
                self._run_pyttsx3_loop()
                return
                
            voice = PiperVoice.load(model_path)
            self._sample_rate = voice.config.sample_rate
            self._engine_available = True
            logger.info(f"Piper TTS engine initialized (Model: {self.piper_model})")
            
            # Pre-cache prefixes
            self._precache_prefixes(voice)
            
        except Exception as e:
            logger.error(f"Failed to initialize Piper TTS: {e}")
            self._run_pyttsx3_loop()
            return

        while self._running:
            try:
                alert = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if alert.message == "__STOP__":
                break

            try:
                t0 = time.time()
                
                # Check if we have this exact message cached
                if alert.message in self._audio_cache:
                    audio_data = self._audio_cache[alert.message]
                else:
                    # Generate audio stream
                    audio_stream = io.BytesIO()
                    with wave.open(audio_stream, "wb") as wav_file:
                        voice.synthesize(alert.message, wav_file)
                    
                    # Convert to numpy array
                    audio_stream.seek(0)
                    with wave.open(audio_stream, "rb") as wav_file:
                        n_frames = wav_file.getnframes()
                        raw_data = wav_file.readframes(n_frames)
                        audio_data = np.frombuffer(raw_data, dtype=np.int16)
                
                latency = (time.time() - t0) * 1000
                logger.debug(f"Piper TTS generation took {latency:.1f}ms")
                
                # Apply volume and play
                if self.volume != 1.0:
                    audio_data = (audio_data * self.volume).astype(np.int16)
                    
                sd.play(audio_data, self._sample_rate)
                sd.wait()  # Wait until audio finishes playing

            except Exception as e:
                logger.error(f"Piper TTS error: {e}")

    def _precache_prefixes(self, voice):
        """Pre-generate audio for common prefixes to eliminate latency."""
        logger.info("Pre-caching common TTS alerts...")
        for config in self.ALERT_CONFIGS.values():
            prefix = config.get("prefix", "")
            if prefix and prefix not in self._audio_cache:
                try:
                    audio_stream = io.BytesIO()
                    with wave.open(audio_stream, "wb") as wav_file:
                        voice.synthesize(prefix, wav_file)
                    
                    audio_stream.seek(0)
                    with wave.open(audio_stream, "rb") as wav_file:
                        n_frames = wav_file.getnframes()
                        raw_data = wav_file.readframes(n_frames)
                        self._audio_cache[prefix] = np.frombuffer(raw_data, dtype=np.int16)
                except Exception as e:
                    logger.debug(f"Failed to pre-cache '{prefix}': {e}")
        
        logger.info(f"Pre-cached {len(self._audio_cache)} alerts")

    def _run_pyttsx3_loop(self):
        """Fallback pyttsx3 loop."""
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty('volume', self.volume)
            self._engine_available = True
            logger.info("pyttsx3 engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 engine: {e}")
            self._engine_available = False
            self._running = False
            return

        while self._running:
            try:
                alert = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if alert.message == "__STOP__":
                break

            try:
                config = self.ALERT_CONFIGS.get(alert.alert_type, {})
                # scale rate for pyttsx3 which expects WPM (default ~150)
                rate = config.get("rate", 1.0) * 150
                engine.setProperty('rate', rate)

                engine.say(alert.message)
                engine.runAndWait()
            except Exception as e:
                logger.error(f"pyttsx3 error: {e}")
                
        if engine:
            try:
                engine.stop()
            except Exception:
                pass

    @property
    def is_available(self) -> bool:
        return self._engine_available

    @property
    def queue_size(self) -> int:
        return self._queue.qsize()
