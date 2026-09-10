"""
Alerting Layer — Offline Text-to-Speech Manager
=================================================
Priority-queue based TTS using pyttsx3 for offline voice alerts.
Higher-priority alerts pre-empt lower-priority ones.
"""

import pyttsx3
import threading
import queue
import logging
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

logger = logging.getLogger(__name__)


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
    
    Runs pyttsx3 in a dedicated background thread.
    Higher-priority alerts pre-empt lower-priority ones in the queue.
    Cooldown prevents repeated alerts of the same type.
    """

    # Voice properties per alert type
    ALERT_CONFIGS = {
        "skipped_step":     {"priority": AlertPriority.CRITICAL, "rate": 180, "prefix": "Warning!"},
        "out_of_sequence":  {"priority": AlertPriority.CRITICAL, "rate": 180, "prefix": "Alert!"},
        "precondition":     {"priority": AlertPriority.WARNING,  "rate": 160, "prefix": "Cannot proceed."},
        "uncertain":        {"priority": AlertPriority.WARNING,  "rate": 150, "prefix": "Please verify."},
        "step_completed":   {"priority": AlertPriority.INFO,     "rate": 140, "prefix": "Step completed."},
        "experiment_start": {"priority": AlertPriority.INFO,     "rate": 140, "prefix": "Experiment started."},
        "next_step":        {"priority": AlertPriority.SUGGESTION, "rate": 130, "prefix": "Next step:"},
        "experiment_done":  {"priority": AlertPriority.STATUS,   "rate": 120, "prefix": "Experiment complete."},
    }

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.base_rate = config.get("voice_rate", 150)
        self.volume = config.get("voice_volume", 0.9)
        self.cooldown = config.get("alert_cooldown", 3.0)

        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_alert_times: dict = {}  # alert_type → last timestamp
        self._engine_available = False

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
        # Push a sentinel to unblock the queue
        self._queue.put(AlertMessage(
            priority=99, timestamp=time.time(), message="__STOP__"
        ))
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None
        logger.info("TTSManager stopped")

    def alert(self, alert_type: str, message: str):
        """
        Queue an alert for speaking.
        
        Args:
            alert_type: One of the keys in ALERT_CONFIGS
            message: The message text to speak
        """
        if not self.enabled or not self._running:
            return

        # Check cooldown
        now = time.time()
        last_time = self._last_alert_times.get(alert_type, 0)
        if now - last_time < self.cooldown:
            logger.debug(f"Alert '{alert_type}' on cooldown, skipping")
            return

        config = self.ALERT_CONFIGS.get(alert_type, {
            "priority": AlertPriority.STATUS,
            "rate": self.base_rate,
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
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty('volume', self.volume)
            engine.setProperty('rate', self.base_rate)
            self._engine_available = True
            logger.info("TTS engine initialized (pyttsx3)")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
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
                # Adjust rate based on alert type
                config = self.ALERT_CONFIGS.get(alert.alert_type, {})
                rate = config.get("rate", self.base_rate)
                engine.setProperty('rate', rate)

                engine.say(alert.message)
                engine.runAndWait()
                logger.debug(f"Spoke: [{alert.alert_type}] {alert.message}")

            except Exception as e:
                logger.error(f"TTS error: {e}")
                # Try to reinitialize engine
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('volume', self.volume)
                except Exception:
                    logger.error("Failed to reinitialize TTS engine")
                    time.sleep(1.0)

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
