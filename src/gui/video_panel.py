"""
GUI Layer — Live Annotated Video Panel
========================================
Displays the camera feed with overlaid bounding boxes,
hand landmarks, interaction state labels, and HUD elements.
"""

import cv2
import numpy as np
import time
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QFont

from .styles import COLORS

import logging
logger = logging.getLogger(__name__)


class VideoPanel(QWidget):
    """
    Live video feed panel with perception overlay annotations.

    Displays:
    - Camera frames with bounding boxes for detected objects
    - Hand landmark skeletons
    - Interaction state labels
    - HUD-style step overlay and FPS counter
    """

    frame_processed = pyqtSignal()

    # Colors for different object types (BGR for OpenCV)
    OBJECT_COLORS = {
        "red_box":    (0, 0, 255),
        "yellow_box": (0, 255, 255),
        "outer_box":  (139, 90, 43),
        "person":     (255, 165, 0),
    }

    INTERACTION_COLORS = {
        "none":        (128, 128, 128),
        "approaching": (255, 255, 0),
        "touching":    (0, 255, 255),
        "grasping":    (0, 165, 255),
        "holding":     (0, 255, 0),
        "releasing":   (255, 0, 255),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_frame = None
        self._fps = 0.0
        self._frame_count = 0
        self._last_fps_time = time.monotonic()
        self._fps_count = 0

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Video display
        self._video_label = QLabel("AWAITING FEED")
        self._video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_label.setMinimumSize(640, 360)
        self._video_label.setStyleSheet(f"""
            background-color: {COLORS['bg_input']};
            color: {COLORS['text_dim']};
            font-size: 14px;
            font-family: JetBrains Mono, monospace;
            letter-spacing: 2px;
            border: 1px solid {COLORS['border_subtle']};
            border-radius: 4px;
        """)
        layout.addWidget(self._video_label, 1)

        # Status bar
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(4, 2, 4, 2)

        self._fps_label = QLabel("FPS: --")
        self._fps_label.setStyleSheet(f"""
            color: {COLORS['accent_cyan']};
            font-family: JetBrains Mono, monospace;
            font-size: 10px;
            background: transparent;
        """)
        status_layout.addWidget(self._fps_label)

        status_layout.addStretch()

        self._resolution_label = QLabel("--x--")
        self._resolution_label.setStyleSheet(f"""
            color: {COLORS['text_dim']};
            font-family: JetBrains Mono, monospace;
            font-size: 10px;
            background: transparent;
        """)
        status_layout.addWidget(self._resolution_label)

        layout.addLayout(status_layout)

    def update_frame(
        self,
        frame: np.ndarray,
        detections=None,
        hand_states=None,
        interactions=None,
        current_step: str = ""
    ):
        """
        Update the video panel with a new annotated frame.

        Args:
            frame: Raw BGR frame from camera
            detections: List of Detection objects
            hand_states: List of HandState objects
            interactions: List of Interaction objects
            current_step: Current experiment step for overlay
        """
        if frame is None:
            return

        annotated = frame.copy()

        # Draw HUD border frame
        annotated = self._draw_hud_frame(annotated)

        # Draw detections
        if detections:
            annotated = self._draw_detections(annotated, detections)

        # Draw hand landmarks
        if hand_states:
            annotated = self._draw_hands(annotated, hand_states)

        # Draw interactions
        if interactions:
            annotated = self._draw_interactions(annotated, interactions)

        # Draw current step overlay
        if current_step:
            annotated = self._draw_step_overlay(annotated, current_step)

        # Draw FPS
        self._update_fps()
        cv2.putText(
            annotated, f"FPS: {self._fps:.0f}",
            (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (0, 229, 255), 1, cv2.LINE_AA
        )

        # Convert and display
        self._display_frame(annotated)
        self._current_frame = annotated

    def _draw_hud_frame(self, frame: np.ndarray) -> np.ndarray:
        """Draw subtle HUD corner brackets on the video frame."""
        h, w = frame.shape[:2]
        color = (0, 107, 255)  # ISRO orange in BGR
        corner = 40
        thickness = 1

        # Top-left
        cv2.line(frame, (0, 0), (corner, 0), color, thickness)
        cv2.line(frame, (0, 0), (0, corner), color, thickness)
        # Top-right
        cv2.line(frame, (w - 1, 0), (w - 1 - corner, 0), color, thickness)
        cv2.line(frame, (w - 1, 0), (w - 1, corner), color, thickness)
        # Bottom-left
        cv2.line(frame, (0, h - 1), (corner, h - 1), color, thickness)
        cv2.line(frame, (0, h - 1), (0, h - 1 - corner), color, thickness)
        # Bottom-right
        cv2.line(frame, (w - 1, h - 1), (w - 1 - corner, h - 1), color, thickness)
        cv2.line(frame, (w - 1, h - 1), (w - 1, h - 1 - corner), color, thickness)

        return frame

    def _draw_detections(self, frame: np.ndarray, detections) -> np.ndarray:
        """Draw bounding boxes and labels for detected objects."""
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            color = self.OBJECT_COLORS.get(det.class_name, (0, 255, 0))

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw corner accents (mission-control style)
            corner_len = 15
            # Top-left
            cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, 3)
            cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, 3)
            # Top-right
            cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color, 3)
            cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color, 3)
            # Bottom-left
            cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color, 3)
            cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color, 3)
            # Bottom-right
            cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, 3)
            cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, 3)

            # Label with background
            label = f"{det.class_name} {det.confidence:.0%}"
            (tw, th), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1
            )
            cv2.rectangle(
                frame,
                (x1, max(0, y1 - th - 6)),
                (x1 + tw + 6, max(0, y1)),
                color, -1
            )
            cv2.putText(
                frame, label,
                (x1 + 3, max(0, y1 - 3)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                (0, 0, 0) if sum(color) > 400 else (255, 255, 255),
                1, cv2.LINE_AA
            )

        return frame

    def _draw_hands(self, frame: np.ndarray, hand_states) -> np.ndarray:
        """Draw hand landmarks with connections."""
        from src.perception.hand_tracker import LandmarkIdx

        CONNECTIONS = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

        for hand in hand_states:
            color = (0, 255, 128) if hand.handedness == "Right" else (255, 128, 0)

            for start_idx, end_idx in CONNECTIONS:
                if start_idx < len(hand.landmarks) and end_idx < len(hand.landmarks):
                    start = hand.landmarks[start_idx]
                    end = hand.landmarks[end_idx]
                    cv2.line(
                        frame,
                        (start.pixel_x, start.pixel_y),
                        (end.pixel_x, end.pixel_y),
                        color, 2, cv2.LINE_AA
                    )

            for lm in hand.landmarks:
                cv2.circle(frame, (lm.pixel_x, lm.pixel_y), 3, color, -1)

            cv2.circle(frame, hand.palm_center, 5, (0, 255, 255), -1)
            cv2.circle(frame, hand.palm_center, 7, (0, 255, 255), 1)

            state_text = hand.handedness
            if hand.is_grasping:
                state_text += ":GRASP"
            elif hand.is_pinching:
                state_text += ":PINCH"

            (tw, th), _ = cv2.getTextSize(state_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            hx, hy = hand.wrist[0] - 20, hand.wrist[1] - 20
            cv2.rectangle(frame, (hx - 2, hy - th - 2), (hx + tw + 2, hy + 2), (0, 0, 0), -1)
            cv2.putText(
                frame, state_text,
                (hx, hy),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA
            )

        return frame

    def _draw_interactions(self, frame: np.ndarray, interactions) -> np.ndarray:
        """Draw interaction indicators between hands and objects."""
        for interaction in interactions:
            state_name = interaction.state.value
            color = self.INTERACTION_COLORS.get(state_name, (128, 128, 128))

            if interaction.hand_state and interaction.object_detection:
                hand_pos = interaction.hand_state.palm_center
                obj_pos = interaction.object_detection.center

                cv2.line(frame, hand_pos, obj_pos, color, 2, cv2.LINE_AA)

                mid_x = (hand_pos[0] + obj_pos[0]) // 2
                mid_y = (hand_pos[1] + obj_pos[1]) // 2

                label = f"[{state_name.upper()}]"
                (tw, th), _ = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1
                )
                cv2.rectangle(
                    frame,
                    (mid_x - tw // 2 - 2, mid_y - th // 2 - 2),
                    (mid_x + tw // 2 + 2, mid_y + th // 2 + 2),
                    (0, 0, 0), -1
                )
                cv2.putText(
                    frame, label,
                    (mid_x - tw // 2, mid_y + th // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    color, 1, cv2.LINE_AA
                )

        return frame

    def _draw_step_overlay(self, frame: np.ndarray, current_step: str) -> np.ndarray:
        """Draw current step overlay in the top-right corner."""
        h, w = frame.shape[:2]
        label = f"STEP: {current_step}"
        (tw, th), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )

        pad = 6
        x1 = w - tw - pad * 3
        y1 = 8

        # Semi-transparent dark background
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x1, y1),
            (w - 8, y1 + th + pad * 2),
            (0, 0, 0), -1
        )
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Orange accent bar
        cv2.rectangle(
            frame,
            (x1, y1),
            (x1 + 3, y1 + th + pad * 2),
            (0, 107, 255), -1  # ISRO orange BGR
        )

        cv2.putText(
            frame, label,
            (x1 + pad + 2, y1 + th + pad),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (255, 255, 255), 1, cv2.LINE_AA
        )

        return frame

    def _display_frame(self, frame: np.ndarray):
        """Convert an OpenCV frame to QPixmap and display it."""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        qt_image = QImage(
            rgb_frame.data, w, h,
            bytes_per_line, QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qt_image)
        scaled = pixmap.scaled(
            self._video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._video_label.setPixmap(scaled)

        self._resolution_label.setText(f"{w}x{h}")

    def _update_fps(self):
        """Update FPS counter."""
        self._fps_count += 1
        now = time.monotonic()
        elapsed = now - self._last_fps_time
        if elapsed >= 1.0:
            self._fps = self._fps_count / elapsed
            self._fps_count = 0
            self._last_fps_time = now
            self._fps_label.setText(f"FPS: {self._fps:.1f}")

    def show_placeholder(self, message: str = "AWAITING FEED"):
        """Show a placeholder message when no video is available."""
        self._video_label.clear()
        self._video_label.setText(message)
