#!/usr/bin/env python3
"""
ISRO BAS Experiment Monitor — Main Entry Point
=================================================
AI-Based Human Activity Recognition for On-board BAS Experiments

Launches the full pipeline:
  Camera → Perception → Fusion → Sequence Reasoning → Alerting → GUI

Usage:
    python main.py                    # Run with default config
    python main.py --config my.yaml   # Run with custom config
    python main.py --source video.mp4 # Run with a video file instead of webcam
    python main.py --no-gui           # Run headless (CLI only)
"""

import sys
import os
import argparse
import logging
import time
import threading
import signal

import yaml
import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.capture.camera import CameraCapture
from src.perception.object_detector import ObjectDetector
from src.perception.hand_tracker import HandTracker
from src.perception.interaction import InteractionClassifier
from src.fusion.scene_state import SceneStateFusion
from src.sequence.protocol import ExperimentProtocol
from src.sequence.fsm import ExperimentFSM, EventType
from src.sequence.classifier import StepClassifier
from src.alerting.tts_manager import TTSManager
from src.logging_layer.logger import ExperimentLogger
from src.streaming.streamer import VideoStreamer


# ── Logging Setup ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)-20s] %(levelname)-7s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("main")


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from: {config_path}")
        return config
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}. Using defaults.")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config: {e}. Using defaults.")
        return {}


class HARPipeline:
    """
    Main AI-HAR Pipeline orchestrator.
    
    Manages the flow:
    Camera → Perception → Fusion → Sequence Reasoning → Alerting/Logging → GUI
    """

    def __init__(self, config: dict, gui_window=None):
        self.config = config
        self.gui = gui_window
        self._running = False

        # ── Initialize all layers ────────────────────────────────
        logger.info("=" * 60)
        logger.info("  ISRO BAS HAR System — Initializing")
        logger.info("=" * 60)

        # Layer 1: Capture
        self.camera = CameraCapture(config.get("capture", {}))
        logger.info("✓ Capture layer initialized")

        # Layer 2: Perception
        perception_cfg = config.get("perception", {})
        self.detector = ObjectDetector(perception_cfg)
        self.hand_tracker = HandTracker(perception_cfg)
        self.interaction_classifier = InteractionClassifier(perception_cfg)
        logger.info("✓ Perception layer initialized")

        # Layer 3: Fusion
        self.fusion = SceneStateFusion()
        logger.info("✓ Fusion layer initialized")

        # Layer 4: Sequence Reasoning
        self.protocol = ExperimentProtocol(
            config.get("sequence", {}).get("protocol", "red_yellow_box")
        )
        self.fsm = ExperimentFSM(
            self.protocol,
            config.get("sequence", {})
        )
        self.classifier = StepClassifier(config.get("sequence", {}))
        logger.info("✓ Sequence reasoning layer initialized")

        # Layer 5: Alerting
        self.tts = TTSManager(config.get("alerting", {}))
        logger.info("✓ Alerting layer initialized")

        # Layer 6: Logging
        self.experiment_logger = ExperimentLogger(config.get("logging", {}))
        logger.info("✓ Logging layer initialized")

        # Layer 7: Streaming
        self.streamer = VideoStreamer(config.get("streaming", {}))
        logger.info("✓ Streaming layer initialized")

        # Connect FSM events to alerting and logging
        self.fsm.add_listener(self._on_fsm_event)

        # Initialize GUI timeline if available
        if self.gui:
            steps = [
                (step_id, step.name)
                for step_id, step in self.protocol.steps.items()
            ]
            self.gui.timeline_panel.setup_steps(steps)
            self.gui.log_panel.set_logger(self.experiment_logger)

        # Processing thread
        self._process_thread = None
        self._frame_count = 0
        self._last_fsm_update = 0

        logger.info("=" * 60)
        logger.info("  System ready. Press START to begin.")
        logger.info("=" * 60)

    def start(self):
        """Start the full pipeline."""
        if self._running:
            return

        logger.info("Starting pipeline...")

        # Start camera
        if not self.camera.start():
            logger.error("Failed to start camera. Check video source.")
            if self.gui:
                self.gui.video_panel.show_placeholder(
                    "⚠ Camera failed to start.\n"
                    "Check your webcam connection or set a video file in config.yaml"
                )
            return

        # Start TTS
        self.tts.start()

        # Start recording
        resolution = tuple(self.config.get("capture", {}).get("resolution", [1280, 720]))
        fps = self.config.get("capture", {}).get("fps", 30)
        self.streamer.start_recording(fps=fps, resolution=resolution)

        # Start processing loop
        self._running = True
        self._process_thread = threading.Thread(
            target=self._processing_loop, daemon=True
        )
        self._process_thread.start()

        if self.gui:
            self.gui.health_panel.update_pipeline_status("ACTIVE")
            self.gui.health_panel.update_recording_status(True)

        logger.info("Pipeline started successfully")

    def stop(self):
        """Stop the pipeline."""
        logger.info("Stopping pipeline...")
        self._running = False

        if self._process_thread:
            self._process_thread.join(timeout=5.0)
            self._process_thread = None

        self.camera.stop()
        self.tts.stop()
        self.streamer.stop_recording()

        # Generate final summary
        summary = self.experiment_logger.generate_summary()
        log_hash = self.experiment_logger.compute_log_hash()
        logger.info(f"Log file hash (SHA-256): {log_hash}")

        self.experiment_logger.close()
        self.hand_tracker.close()

        if self.gui:
            self.gui.health_panel.update_pipeline_status("IDLE")
            self.gui.health_panel.update_recording_status(False)

        logger.info("Pipeline stopped")

    def reset(self):
        """Reset the pipeline for a new experiment."""
        self.fsm.reset()
        self.fusion.reset()
        self.interaction_classifier.reset()
        self._frame_count = 0

        self.experiment_logger.log_event(
            step_id="SYSTEM",
            status="RESET",
            message="System reset for new experiment"
        )

        if self.gui:
            self.gui.timeline_panel.update_state("IDLE", set(), "", 0.0)

        logger.info("Pipeline reset for new experiment")

    def _processing_loop(self):
        """Main frame processing loop running in background thread."""
        logger.info("Processing loop started")

        while self._running:
            # Check if GUI says we should be running
            if self.gui and not self.gui.is_pipeline_running:
                time.sleep(0.05)
                continue

            # Get frame
            result = self.camera.get_frame(timeout=0.1)
            if result is None:
                continue

            success, frame = result
            if not success or frame is None:
                continue

            self._frame_count += 1
            process_start = time.monotonic()

            try:
                # ── Layer 2: Perception ──────────────────────────
                detections = self.detector.detect(frame)
                hand_states = self.hand_tracker.detect(frame)
                interactions = self.interaction_classifier.classify(
                    hand_states, detections
                )

                # ── Layer 3: Fusion ──────────────────────────────
                scene_state = self.fusion.fuse(detections, hand_states, interactions)

                # ── Layer 4: Sequence Reasoning ──────────────────
                predicted_step, confidence = self.classifier.classify(scene_state)
                preconditions = self.classifier.get_preconditions_met(scene_state)

                # Process step prediction through FSM
                self.fsm.process_step_prediction(
                    predicted_step, confidence, preconditions
                )

                # Check if current event is an anomaly
                anomaly = self.fsm._candidate_step is None and self.fsm.current_step in [
                    EventType.SKIPPED_STEP, EventType.OUT_OF_SEQUENCE, EventType.DURATION_ANOMALY
                ]
                
                # ── Layer 7: Streaming ───────────────────────────
                self.streamer.write_frame(
                    frame, 
                    current_step=self.fsm.current_step,
                    anomaly_flag=anomaly
                )

                # ── Layer 8: GUI Update ──────────────────────────
                process_time = (time.monotonic() - process_start) * 1000

                if self.gui:
                    # Update video (every frame)
                    self.gui.update_frame_signal.emit(
                        frame, detections, hand_states, interactions,
                        self.fsm.current_step
                    )

                    # Update health metrics
                    self.gui.health_panel.update_fps(self.camera.fps)
                    self.gui.health_panel.update_latency(process_time)
                    self.gui.health_panel.update_recording_status(
                        self.streamer.is_recording,
                        self.streamer.recording_duration
                    )

                    # Update metrics diagram (every second)
                    now = time.monotonic()
                    if now - self._last_fsm_update > 0.1:
                        self._last_fsm_update = now
                        self.gui.update_metrics_signal.emit(confidence)

                        # Update timeline
                        valid = self.fsm.get_valid_transitions()
                        next_suggestion = valid[0] if valid else ""
                        self.gui.update_timeline_signal.emit(
                            self.fsm.current_step,
                            self.fsm.completed_steps,
                            next_suggestion,
                            self.fsm.progress_fraction
                        )

            except Exception as e:
                logger.error(f"Processing error at frame {self._frame_count}: {e}")
                import traceback
                traceback.print_exc()

        logger.info("Processing loop stopped")

    def _on_fsm_event(self, event):
        """Handle FSM events — dispatch to alerting, logging, and GUI."""
        # Map event types to alert types and severities
        event_map = {
            EventType.STEP_COMPLETED: ("step_completed", "info"),
            EventType.EXPERIMENT_STARTED: ("experiment_start", "info"),
            EventType.EXPERIMENT_COMPLETE: ("experiment_done", "info"),
            EventType.SKIPPED_STEP: ("skipped_step", "critical"),
            EventType.OUT_OF_SEQUENCE: ("out_of_sequence", "critical"),
            EventType.UNCERTAIN: ("uncertain", "warning"),
            EventType.PRECONDITION_FAILED: ("precondition", "warning"),
            EventType.NEXT_STEP_SUGGESTION: ("next_step", "suggestion"),
        }

        alert_type, severity = event_map.get(
            event.event_type, ("info", "info")
        )

        # Layer 5: Alerting (voice)
        if event.event_type != EventType.NEXT_STEP_SUGGESTION:
            self.tts.alert(alert_type, event.message)

        # Layer 6: Logging
        self.experiment_logger.log_event(
            step_id=event.step_id,
            status=event.event_type.value,
            confidence=event.confidence,
            alert_type=alert_type,
            message=event.message,
            details=event.details
        )

        # Layer 8: GUI alerts and log
        if self.gui:
            if event.event_type != EventType.NEXT_STEP_SUGGESTION:
                self.gui.update_alert_signal.emit(severity, event.message)

            self.gui.update_log_signal.emit({
                "elapsed_seconds": time.time() - self.experiment_logger._start_time,
                "step_id": event.step_id,
                "status": event.event_type.value,
                "confidence": event.confidence,
                "message": event.message,
            })

            # Mark anomaly in recording
            if event.event_type in (EventType.SKIPPED_STEP, EventType.OUT_OF_SEQUENCE):
                self.streamer.mark_anomaly(event.event_type.value)


def run_gui(config: dict):
    """Launch the GUI application with the full pipeline."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont
    from src.gui.main_window import MainWindow

    app = QApplication(sys.argv)

    # Set application-wide font
    app.setFont(QFont("Inter", 11))

    # Create main window
    window = MainWindow(config)

    # Create pipeline
    pipeline = HARPipeline(config, gui_window=window)

    # Connect start/stop buttons to pipeline
    original_start = window._on_start_clicked

    def enhanced_start():
        original_start()
        if window.is_pipeline_running:
            pipeline.start()
        else:
            pipeline.stop()

    window._start_btn.clicked.disconnect()
    window._start_btn.clicked.connect(enhanced_start)

    original_reset = window._on_reset_clicked

    def enhanced_reset():
        if pipeline._running:
            pipeline.stop()
        pipeline.reset()
        original_reset()

    window._reset_btn.clicked.disconnect()
    window._reset_btn.clicked.connect(enhanced_reset)

    # Show window
    window.showMaximized()

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda *args: (pipeline.stop(), app.quit()))

    # Run event loop
    exit_code = app.exec()

    # Cleanup
    if pipeline._running:
        pipeline.stop()

    sys.exit(exit_code)


def run_headless(config: dict):
    """Run pipeline without GUI (CLI mode)."""
    pipeline = HARPipeline(config)
    pipeline.start()

    logger.info("Running in headless mode. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
            status = (
                f"Step: {pipeline.fsm.current_step} | "
                f"FPS: {pipeline.camera.fps:.0f} | "
                f"Progress: {pipeline.fsm.progress_fraction:.0%}"
            )
            logger.info(status)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        pipeline.stop()


def main():
    parser = argparse.ArgumentParser(
        description="ISRO BAS Experiment Monitor — AI-Based HAR System"
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--source", "-s",
        default=None,
        help="Video source: webcam index (0,1,...) or path to video file"
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without GUI (headless mode)"
    )
    parser.add_argument(
        "--no-tts",
        action="store_true",
        help="Disable voice alerts"
    )

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # Override source if provided
    if args.source is not None:
        try:
            config.setdefault("capture", {})["source"] = int(args.source)
        except ValueError:
            config.setdefault("capture", {})["source"] = args.source

    # Override TTS
    if args.no_tts:
        config.setdefault("alerting", {})["enabled"] = False

    # Run
    if args.no_gui:
        run_headless(config)
    else:
        run_gui(config)


if __name__ == "__main__":
    main()
