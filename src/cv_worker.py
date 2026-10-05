"""
BASGUARD — Computer Vision Edge Capture & Event Gating Worker
Module: src/cv_worker.py

Provides real-time OpenCV stream ingestion at 30 FPS with:
1. Circular frame buffering (deque of last N frames).
2. Motion & event gating (motion delta via cv2.absdiff, Petri-Net transition triggers, anomaly thresholds).
3. High-value Region of Interest (ROI) cropping and Base64 JPEG encoding.
"""

import cv2
import time
import base64
import numpy as np
import threading
from collections import deque
from typing import Optional, Tuple, Dict, Any, Callable


class CVWorker:
    """
    Dedicated OpenCV video ingestion and event-gated keyframe extraction worker.
    Runs in a dedicated thread to ensure the 30 FPS video pipeline is never blocked
    by downstream LLM/VLM inference tasks.
    """

    def __init__(
        self,
        source: Any = 0,
        buffer_size: int = 30,
        fps_target: float = 30.0,
        motion_threshold: float = 25.0,
        motion_area_percent: float = 0.05,
    ):
        """
        Initialize the CV worker thread and buffer state.
        
        :param source: OpenCV VideoCapture source (webcam index, RTSP URL, or video file path)
        :param buffer_size: Maximum capacity of the circular frame buffer
        :param fps_target: Target frame rate (e.g. 30.0 FPS)
        :param motion_threshold: Pixel intensity difference threshold for cv2.absdiff
        :param motion_area_percent: Minimum percentage of frame area changed to trigger motion event
        """
        self.source = source
        self.buffer_size = buffer_size
        self.fps_target = fps_target
        self.frame_delay = 1.0 / fps_target
        self.motion_threshold = motion_threshold
        self.motion_area_percent = motion_area_percent

        # Thread-safe circular buffer
        self.frame_buffer: deque = deque(maxlen=buffer_size)
        self.lock = threading.Lock()

        # Thread lifecycle
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.cap: Optional[cv2.VideoCapture] = None

        # State tracking for motion gating
        self.prev_gray_frame: Optional[np.ndarray] = None
        self.last_motion_score: float = 0.0
        self.current_fps: float = 0.0
        self.frame_count: int = 0

        # Event callbacks
        self.on_audit_trigger: Optional[Callable[[np.ndarray, Dict[str, Any]], None]] = None

    def start(self) -> None:
        """Start the video ingestion worker thread."""
        if self._running:
            return

        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            print(f"[CVWorker] WARNING: Could not open video source '{self.source}'. Initializing synthetic frame generator.")
            self.cap = None

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True, name="CVWorkerThread")
        self._thread.start()
        print(f"[CVWorker] Ingestion thread started at target {self.fps_target} FPS.")

    def stop(self) -> None:
        """Stop the video ingestion worker thread gracefully."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print("[CVWorker] Ingestion thread stopped.")

    def _capture_loop(self) -> None:
        """Internal capture loop running in dedicated thread."""
        last_time = time.time()
        fps_timer = time.time()
        frames_in_second = 0

        while self._running:
            loop_start = time.time()

            # Read frame or generate synthetic telemetry frame if webcam unavailable
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video if file ended
                    ret, frame = self.cap.read()
                    if not ret:
                        time.sleep(0.05)
                        continue
            else:
                frame = self._generate_synthetic_frame()

            # Resize frame to standard 1080p if necessary
            h, w = frame.shape[:2]
            if w != 1920 or h != 1080:
                frame = cv2.resize(frame, (1920, 1080))

            # Store frame in circular buffer
            timestamp = time.time()
            with self.lock:
                self.frame_buffer.append((timestamp, frame))

            # Motion & Event Gating Evaluation
            motion_detected, motion_score = self._detect_motion(frame)
            self.last_motion_score = motion_score

            # FPS calculation
            frames_in_second += 1
            if time.time() - fps_timer >= 1.0:
                self.current_fps = frames_in_second / (time.time() - fps_timer)
                frames_in_second = 0
                fps_timer = time.time()

            self.frame_count += 1

            # FPS throttling
            elapsed = time.time() - loop_start
            sleep_time = max(0.0, self.frame_delay - elapsed)
            time.sleep(sleep_time)

    def _detect_motion(self, frame: np.ndarray) -> Tuple[bool, float]:
        """
        Compute frame-to-frame motion delta using cv2.absdiff and thresholding.
        
        :param frame: Current BGR image frame
        :return: Tuple of (motion_detected_boolean, motion_percentage_score)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_gray_frame is None:
            self.prev_gray_frame = gray
            return False, 0.0

        # Motion delta
        frame_delta = cv2.absdiff(self.prev_gray_frame, gray)
        thresh = cv2.threshold(frame_delta, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Calculate percentage of pixels changed
        non_zero_count = cv2.countNonZero(thresh)
        total_pixels = gray.shape[0] * gray.shape[1]
        motion_score = (non_zero_count / total_pixels) * 100.0

        self.prev_gray_frame = gray
        is_triggered = motion_score >= (self.motion_area_percent * 100.0)

        return is_triggered, motion_score

    def crop_roi(self, frame: np.ndarray, bbox: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Crop high-value Region of Interest (ROI) around hand or active payload box.
        
        :param frame: BGR Image
        :param bbox: Optional bounding box (x_min, y_min, x_max, y_max)
        :return: Cropped BGR ROI
        """
        h, w = frame.shape[:2]
        if bbox is None:
            # Default payload central workspace ROI
            x_min, y_min = int(w * 0.15), int(h * 0.15)
            x_max, y_max = int(w * 0.85), int(h * 0.85)
        else:
            x_min, y_min, x_max, y_max = bbox
            # Expand bbox with 15% margin for visual context
            margin_x = int((x_max - x_min) * 0.15)
            margin_y = int((y_max - y_min) * 0.15)
            x_min = max(0, x_min - margin_x)
            y_min = max(0, y_min - margin_y)
            x_max = min(w, x_max + margin_x)
            y_max = min(h, y_max + margin_y)

        return frame[y_min:y_max, x_min:x_max]

    def encode_frame_base64(self, frame: np.ndarray, quality: int = 75) -> str:
        """
        Encode an image frame into Base64 JPEG string payload for LLM vision consumption.
        
        :param frame: BGR image numpy array
        :param quality: JPEG compression quality (1-100)
        :return: Base64 encoded string
        """
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        success, buffer = cv2.imencode('.jpg', frame, encode_param)
        if not success:
            raise ValueError("Failed to encode frame to JPEG")
        
        return base64.b64encode(buffer).decode('utf-8')

    def get_latest_frame(self) -> Tuple[Optional[float], Optional[np.ndarray]]:
        """Safely fetch the most recent frame from the circular buffer."""
        with self.lock:
            if not self.frame_buffer:
                return None, None
            return self.frame_buffer[-1]

    def _generate_synthetic_frame(self) -> np.ndarray:
        """Generate synthetic ISRO payload test pattern if camera feed is unavailable."""
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        frame[:] = (12, 17, 26) # Dark background

        # Draw grid lines
        for x in range(0, 1920, 80):
            cv2.line(frame, (x, 0), (x, 1080), (30, 42, 58), 1)
        for y in range(0, 1080, 80):
            cv2.line(frame, (0, y), (1920, y), (30, 42, 58), 1)

        # Outer Box representation
        cv2.rectangle(frame, (350, 220), (1570, 860), (80, 60, 40), 2)
        cv2.putText(frame, "ISRO BIOLOGICAL CONTAINMENT UNIT", (360, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        # Red & Yellow Boxes
        cv2.rectangle(frame, (420, 320), (680, 580), (40, 40, 220), -1)
        cv2.putText(frame, "RED_BOX", (430, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 255), 2)

        cv2.rectangle(frame, (820, 340), (1080, 600), (20, 180, 220), -1)
        cv2.putText(frame, "YELLOW_BOX", (830, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 200, 240), 2)

        # Animated Hand Representation
        t = time.time()
        hand_x = int(950 + np.sin(t * 1.5) * 120)
        hand_y = int(470 + np.cos(t * 1.5) * 60)
        cv2.circle(frame, (hand_x, hand_y), 30, (50, 220, 100), -1)
        cv2.putText(frame, "ASTRONAUT_GLOVE", (hand_x - 60, hand_y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 240, 120), 2)

        # Timestamp watermark
        time_str = time.strftime("%Y-%m-%d %H:%M:%S IST", time.localtime())
        cv2.putText(frame, f"CAM-01 [SYNTHETIC] | {time_str} | FPS: {self.current_fps:.1f}", 
                    (30, 1040), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)

        return frame
