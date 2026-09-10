"""
Capture Layer — Camera/Video Capture Module
============================================
Handles webcam or video file input with threaded frame reading,
automatic reconnection, and Qt signal integration.
"""

import cv2
import time
import threading
import queue
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class CameraCapture:
    """
    Threaded video capture from webcam or video file.
    
    Pushes frames into a queue for downstream consumers.
    Handles camera disconnection with exponential backoff retry.
    """

    def __init__(self, config: dict):
        self.source = config.get("source", 0)
        self.target_fps = config.get("fps", 30)
        self.resolution = tuple(config.get("resolution", [1280, 720]))
        self.reconnect_delay = config.get("reconnect_delay", 2.0)
        self.max_reconnect = config.get("max_reconnect_attempts", 10)

        self._cap: Optional[cv2.VideoCapture] = None
        self._frame_queue: queue.Queue = queue.Queue(maxsize=3)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_count = 0
        self._fps = 0.0
        self._last_fps_time = time.monotonic()
        self._fps_frame_count = 0
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Start the capture thread. Returns True if camera opened successfully."""
        if self._running:
            logger.warning("CameraCapture already running")
            return True

        if not self._open_camera():
            return False

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info(f"CameraCapture started (source={self.source}, "
                    f"resolution={self.resolution}, target_fps={self.target_fps})")
        return True

    def stop(self):
        """Stop the capture thread and release the camera."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=3.0)
            self._thread = None
        self._release_camera()
        logger.info("CameraCapture stopped")

    def get_frame(self, timeout: float = 0.1) -> Optional[Tuple[bool, any]]:
        """
        Get the latest frame from the queue.
        
        Returns:
            Tuple of (success: bool, frame: np.ndarray) or None if timeout.
        """
        try:
            return self._frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_frame_nowait(self) -> Optional[Tuple[bool, any]]:
        """Get a frame without waiting. Returns None if no frame available."""
        try:
            return self._frame_queue.get_nowait()
        except queue.Empty:
            return None

    @property
    def fps(self) -> float:
        """Current measured FPS."""
        return self._fps

    @property
    def frame_count(self) -> int:
        """Total frames captured since start."""
        return self._frame_count

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_file_source(self) -> bool:
        """True if source is a video file rather than a webcam."""
        return isinstance(self.source, str)

    def _open_camera(self) -> bool:
        """Open the video capture device/file."""
        self._release_camera()

        try:
            if isinstance(self.source, str):
                # Video file
                self._cap = cv2.VideoCapture(self.source)
                logger.info(f"Opening video file: {self.source}")
            else:
                # Webcam
                self._cap = cv2.VideoCapture(self.source)
                if self._cap.isOpened():
                    self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                    self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                    self._cap.set(cv2.CAP_PROP_FPS, self.target_fps)
                    # Reduce buffer size for lower latency
                    self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                logger.info(f"Opening webcam: index {self.source}")

            if not self._cap.isOpened():
                logger.error(f"Failed to open video source: {self.source}")
                return False

            actual_w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self._cap.get(cv2.CAP_PROP_FPS)
            logger.info(f"Camera opened: {actual_w}x{actual_h} @ {actual_fps:.1f} FPS")
            return True

        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False

    def _release_camera(self):
        """Release the video capture device."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def _capture_loop(self):
        """Main capture loop running in a background thread."""
        frame_interval = 1.0 / self.target_fps if self.target_fps > 0 else 0
        reconnect_attempts = 0

        while self._running:
            loop_start = time.monotonic()

            if self._cap is None or not self._cap.isOpened():
                # Try to reconnect
                if reconnect_attempts >= self.max_reconnect:
                    logger.error("Max reconnection attempts reached. Stopping capture.")
                    self._running = False
                    break

                delay = self.reconnect_delay * (2 ** min(reconnect_attempts, 5))
                logger.warning(f"Camera disconnected. Retrying in {delay:.1f}s "
                             f"(attempt {reconnect_attempts + 1}/{self.max_reconnect})")
                time.sleep(delay)
                reconnect_attempts += 1

                if self._open_camera():
                    reconnect_attempts = 0
                    logger.info("Camera reconnected successfully")
                continue

            ret, frame = self._cap.read()

            if not ret:
                if self.is_file_source:
                    # Loop video file
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    logger.info("Video file looped")
                    continue
                else:
                    logger.warning("Failed to read frame from camera")
                    self._release_camera()
                    continue

            # Resize if needed
            h, w = frame.shape[:2]
            if (w, h) != self.resolution:
                frame = cv2.resize(frame, self.resolution)

            # Update FPS counter
            self._frame_count += 1
            self._fps_frame_count += 1
            now = time.monotonic()
            elapsed = now - self._last_fps_time
            if elapsed >= 1.0:
                self._fps = self._fps_frame_count / elapsed
                self._fps_frame_count = 0
                self._last_fps_time = now

            # Push to queue (drop oldest if full for low latency)
            if self._frame_queue.full():
                try:
                    self._frame_queue.get_nowait()
                except queue.Empty:
                    pass
            self._frame_queue.put((True, frame))

            # Maintain target FPS
            elapsed = time.monotonic() - loop_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        self._release_camera()
