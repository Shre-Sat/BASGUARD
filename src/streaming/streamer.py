"""
Streaming & Storage Layer — Video Streamer
============================================
Simultaneous local video recording and network streaming.
Upgraded to use GStreamer for RTSP streaming and ring-buffer storage,
with fallback to OpenCV VideoWriter if GStreamer is unavailable.
"""

import cv2
import os
import time
import json
import subprocess
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class VideoStreamer:
    """
    Handles simultaneous video recording, streaming, and per-frame logging.
    
    - GStreamer backend: RTSP streaming and splitmuxsink ring-buffer MP4s.
    - OpenCV backend (fallback): Simple MP4 recording.
    - Integrated JSONL frame logging for anomaly tracking.
    """

    def __init__(self, config: dict):
        self.config = config
        self.backend = config.get("backend", "opencv")
        self.local_save = config.get("local_save", True)
        self.local_path = config.get("local_path", "recordings/")
        self.stream_enabled = config.get("enabled", False)
        
        # RTSP settings
        self.rtsp_enabled = config.get("rtsp_enabled", False)
        self.rtsp_url = config.get("rtsp_url", "rtsp://localhost:8554/basguard")
        
        # Storage settings
        self.codec = config.get("codec", "x264")
        self.ring_buffer_minutes = config.get("ring_buffer_minutes", 30)
        self.segment_duration = config.get("segment_duration", 300)
        self.frame_log_enabled = config.get("frame_log", True)

        # Create recording directory
        Path(self.local_path).mkdir(parents=True, exist_ok=True)

        self._recording = False
        self._frame_count = 0
        self._recording_start_time = 0.0
        self._base_filename = ""
        self._lock = threading.Lock()

        # OpenCV Fallback Writer
        self._cv_writer: Optional[cv2.VideoWriter] = None
        
        # GStreamer Subprocess
        self._gst_process = None
        self._gst_writer = None  # Using OpenCV's GStreamer backend for appsrc input

        # Frame Logger
        self._frame_logger = None

        # Anomaly clip tracking
        self._anomaly_clips: list = []

    def start_recording(self, fps: float = 30.0, resolution: tuple = (1280, 720)):
        """Start recording video and optionally streaming."""
        if not self.local_save and not self.stream_enabled:
            return

        with self._lock:
            if self._recording:
                logger.warning("Already recording")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._base_filename = os.path.join(self.local_path, f"experiment_{timestamp}")
            
            # Start Frame Logger
            if self.frame_log_enabled:
                self._frame_logger = open(f"{self._base_filename}.frames.jsonl", "w")

            # Try GStreamer first if configured
            if self.backend == "gstreamer":
                if self._start_gstreamer(fps, resolution):
                    self._recording = True
                    self._recording_start_time = time.time()
                    self._frame_count = 0
                    logger.info(f"GStreamer recording started: {self._base_filename}")
                    return
                else:
                    logger.warning("GStreamer failed. Falling back to OpenCV.")
                    self.backend = "opencv"

            # OpenCV Fallback
            if self.backend == "opencv" and self.local_save:
                filename = f"{self._base_filename}.mp4"
                
                # If x264 isn't supported by standard OpenCV, fallback to mp4v
                codec = "mp4v" if self.codec == "x264" else self.codec
                fourcc = cv2.VideoWriter_fourcc(*codec)
                
                self._cv_writer = cv2.VideoWriter(
                    filename, fourcc, fps, resolution
                )

                if self._cv_writer.isOpened():
                    self._recording = True
                    self._recording_start_time = time.time()
                    self._frame_count = 0
                    logger.info(f"OpenCV recording started: {filename}")
                else:
                    logger.error(f"Failed to open OpenCV VideoWriter: {filename}")
                    self._cv_writer = None

    def _start_gstreamer(self, fps: float, resolution: tuple) -> bool:
        """Start GStreamer appsrc pipeline."""
        w, h = resolution
        
        # Build GStreamer pipeline string for cv2.VideoWriter
        # We push to an appsrc, encode to h264, then tee to file and/or rtsp
        
        pipeline_parts = [
            f"appsrc ! videoconvert ! video/x-raw,format=I420,width={w},height={h},framerate={int(fps)}/1",
            "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast",
            "tee name=t"
        ]
        
        # Local storage branch (Ring-buffer via splitmuxsink)
        if self.local_save:
            # Keep max N files based on ring_buffer_minutes / segment_duration
            max_files = max(1, int((self.ring_buffer_minutes * 60) / self.segment_duration))
            file_pattern = f"{self._base_filename}_%03d.mp4"
            
            pipeline_parts.append(
                f"t. ! queue ! splitmuxsink "
                f"location={file_pattern} "
                f"max-size-time={self.segment_duration * 1000000000} "  # ns
                f"max-files={max_files}"
            )
            
        # RTSP streaming branch
        if self.rtsp_enabled:
            # We assume a local rtsp server like mediamtx is running
            # We use rtspclientsink to push to it
            pipeline_parts.append(
                f"t. ! queue ! rtspclientsink location={self.rtsp_url} protocols=tcp"
            )
            
        pipeline = " ! ".join(pipeline_parts)
        
        try:
            self._gst_writer = cv2.VideoWriter(
                pipeline, cv2.CAP_GSTREAMER, 0, fps, resolution, True
            )
            return self._gst_writer.isOpened()
        except Exception as e:
            logger.error(f"GStreamer initialization error: {e}")
            return False

    def write_frame(self, frame: np.ndarray, current_step: str = "", anomaly_flag: bool = False):
        """Write a frame to the recording and log its metadata."""
        if not self._recording:
            return

        with self._lock:
            try:
                # Write video frame
                if self.backend == "gstreamer" and self._gst_writer:
                    self._gst_writer.write(frame)
                elif self.backend == "opencv" and self._cv_writer:
                    self._cv_writer.write(frame)
                    
                self._frame_count += 1
                
                # Write frame log
                if self._frame_logger:
                    log_entry = {
                        "frame_id": self._frame_count,
                        "timestamp": time.time(),
                        "step_id": current_step,
                        "anomaly": anomaly_flag
                    }
                    self._frame_logger.write(json.dumps(log_entry) + "\n")
                    
            except Exception as e:
                logger.error(f"Error writing frame: {e}")

    def stop_recording(self):
        """Stop recording and finalize files."""
        with self._lock:
            if not self._recording:
                return

            if self._cv_writer is not None:
                self._cv_writer.release()
                self._cv_writer = None
                
            if self._gst_writer is not None:
                self._gst_writer.release()
                self._gst_writer = None
                
            if self._frame_logger is not None:
                self._frame_logger.close()
                self._frame_logger = None

            self._recording = False
            duration = time.time() - self._recording_start_time
            logger.info(
                f"Recording stopped: {self._base_filename} "
                f"({self._frame_count} frames, {duration:.1f}s)"
            )

    def mark_anomaly(self, event_type: str, timestamp: float = None):
        """Mark current timestamp as anomaly for clip retention."""
        if timestamp is None:
            timestamp = time.time()
        self._anomaly_clips.append({
            "timestamp": timestamp,
            "event_type": event_type,
            "base_file": self._base_filename
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
        return self._base_filename

    def close(self):
        """Clean up resources."""
        self.stop_recording()
