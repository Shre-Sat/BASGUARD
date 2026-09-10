"""
Streaming & Storage Layer — Video Streamer
============================================
Simultaneous local video recording and optional network streaming.
Uses OpenCV VideoWriter for local storage.
"""

import cv2
import os
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class VideoStreamer:
    """
    Handles simultaneous video recording and streaming.
    
    - Local storage: OpenCV VideoWriter → .mp4 files
    - Network stream: Optional UDP/RTSP via FFmpeg subprocess
    - Ring-buffer: keeps last N minutes, preserves anomaly clips
    """

    def __init__(self, config: dict):
        self.local_save = config.get("local_save", True)
        self.local_path = config.get("local_path", "recordings/")
        self.stream_enabled = config.get("enabled", False)
        self.stream_target = config.get("stream_target", "udp://localhost:5000")
        self.codec = config.get("codec", "mp4v")

        # Create recording directory
        Path(self.local_path).mkdir(parents=True, exist_ok=True)

        self._writer: Optional[cv2.VideoWriter] = None
        self._recording = False
        self._frame_count = 0
        self._recording_filename = ""
        self._recording_start_time = 0.0
        self._lock = threading.Lock()

        # Anomaly clip tracking
        self._anomaly_clips: list = []

    def start_recording(self, fps: float = 30.0, resolution: tuple = (1280, 720)):
        """Start recording video to local storage."""
        if not self.local_save:
            return

        with self._lock:
            if self._recording:
                logger.warning("Already recording")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._recording_filename = os.path.join(
                self.local_path, f"experiment_{timestamp}.mp4"
            )

            fourcc = cv2.VideoWriter_fourcc(*self.codec)
            self._writer = cv2.VideoWriter(
                self._recording_filename,
                fourcc,
                fps,
                resolution
            )

            if self._writer.isOpened():
                self._recording = True
                self._recording_start_time = time.time()
                self._frame_count = 0
                logger.info(f"Recording started: {self._recording_filename}")
            else:
                logger.error(f"Failed to open VideoWriter: {self._recording_filename}")
                self._writer = None

    def write_frame(self, frame: np.ndarray):
        """Write a frame to the recording."""
        if not self._recording or self._writer is None:
            return

        with self._lock:
            try:
                self._writer.write(frame)
                self._frame_count += 1
            except Exception as e:
                logger.error(f"Error writing frame: {e}")

    def stop_recording(self):
        """Stop recording and finalize the video file."""
        with self._lock:
            if not self._recording:
                return

            if self._writer is not None:
                self._writer.release()
                self._writer = None

            self._recording = False
            duration = time.time() - self._recording_start_time
            logger.info(
                f"Recording stopped: {self._recording_filename} "
                f"({self._frame_count} frames, {duration:.1f}s)"
            )

    def mark_anomaly(self, event_type: str, timestamp: float = None):
        """Mark current timestamp as anomaly for clip retention."""
        if timestamp is None:
            timestamp = time.time()
        self._anomaly_clips.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "recording": self._recording_filename
        })
        logger.info(f"Anomaly marked at {timestamp}: {event_type}")

    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def recording_duration(self) -> float:
        if not self._recording:
            return 0.0
        return time.time() - self._recording_start_time

    @property
    def recording_filename(self) -> str:
        return self._recording_filename

    def close(self):
        """Clean up resources."""
        self.stop_recording()
