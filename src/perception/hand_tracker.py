"""
Perception Layer — Hand Tracking Module
=========================================
MediaPipe Hands integration for real-time hand landmark detection.
"""

import cv2
import numpy as np
import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class HandLandmark:
    """Single hand landmark point."""
    x: float  # Normalized [0, 1]
    y: float  # Normalized [0, 1]
    z: float  # Depth (relative)
    pixel_x: int = 0  # Pixel coordinates
    pixel_y: int = 0


@dataclass
class HandState:
    """Complete state of a detected hand."""
    handedness: str  # "Left" or "Right"
    confidence: float
    landmarks: List[HandLandmark] = field(default_factory=list)
    # Key landmark positions (pixel coords) for quick access
    wrist: Tuple[int, int] = (0, 0)
    thumb_tip: Tuple[int, int] = (0, 0)
    index_tip: Tuple[int, int] = (0, 0)
    middle_tip: Tuple[int, int] = (0, 0)
    ring_tip: Tuple[int, int] = (0, 0)
    pinky_tip: Tuple[int, int] = (0, 0)
    palm_center: Tuple[int, int] = (0, 0)
    # Derived features
    is_pinching: bool = False       # Thumb-index close together
    is_grasping: bool = False       # All fingers curled
    finger_spread: float = 0.0     # Average distance between fingertips
    thumb_index_dist: float = 0.0  # Distance between thumb tip and index tip


# MediaPipe hand landmark indices
class LandmarkIdx:
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


class HandTracker:
    """
    Real-time hand tracking using MediaPipe Hands.
    
    Detects up to 2 hands, extracts 21 landmarks per hand,
    and computes derived features (pinch, grasp, finger spread).
    """

    def __init__(self, config: dict):
        self.max_hands = config.get("mediapipe_max_hands", 2)
        self.detection_confidence = config.get("mediapipe_detection_confidence", 0.6)
        self.tracking_confidence = config.get("mediapipe_tracking_confidence", 0.5)
        self.grasp_threshold = config.get("grasp_finger_threshold", 40)

        self._hands = None
        self._mp_hands = None
        self._mp_drawing = None
        self._inference_time = 0.0
        self._available = False

        self._init_mediapipe()

    def _init_mediapipe(self):
        """Initialize MediaPipe Hands solution."""
        try:
            import mediapipe as mp
            self._mp_hands = mp.solutions.hands
            self._mp_drawing = mp.solutions.drawing_utils
            self._mp_drawing_styles = mp.solutions.drawing_styles

            self._hands = self._mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=self.max_hands,
                min_detection_confidence=self.detection_confidence,
                min_tracking_confidence=self.tracking_confidence
            )
            self._available = True
            logger.info(f"MediaPipe Hands initialized (max_hands={self.max_hands})")
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe Hands: {e}")
            self._available = False

    def detect(self, frame: np.ndarray) -> List[HandState]:
        """
        Detect hands in a frame and return hand states.
        
        Args:
            frame: BGR image from OpenCV
            
        Returns:
            List of HandState objects for each detected hand
        """
        if not self._available:
            return []

        start_time = time.monotonic()
        h, w = frame.shape[:2]

        # MediaPipe expects RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self._hands.process(rgb_frame)
        rgb_frame.flags.writeable = True

        hand_states = []

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness_info in zip(
                results.multi_hand_landmarks,
                results.multi_handedness
            ):
                hand_state = self._process_hand(
                    hand_landmarks, handedness_info, w, h
                )
                hand_states.append(hand_state)

        self._inference_time = (time.monotonic() - start_time) * 1000
        return hand_states

    def _process_hand(
        self, hand_landmarks, handedness_info, frame_w: int, frame_h: int
    ) -> HandState:
        """Process a single hand's landmarks into a HandState."""
        handedness = handedness_info.classification[0].label
        confidence = handedness_info.classification[0].score

        landmarks = []
        for lm in hand_landmarks.landmark:
            px = int(lm.x * frame_w)
            py = int(lm.y * frame_h)
            landmarks.append(HandLandmark(
                x=lm.x, y=lm.y, z=lm.z,
                pixel_x=px, pixel_y=py
            ))

        # Extract key landmarks
        wrist = (landmarks[LandmarkIdx.WRIST].pixel_x,
                 landmarks[LandmarkIdx.WRIST].pixel_y)
        thumb_tip = (landmarks[LandmarkIdx.THUMB_TIP].pixel_x,
                     landmarks[LandmarkIdx.THUMB_TIP].pixel_y)
        index_tip = (landmarks[LandmarkIdx.INDEX_TIP].pixel_x,
                     landmarks[LandmarkIdx.INDEX_TIP].pixel_y)
        middle_tip = (landmarks[LandmarkIdx.MIDDLE_TIP].pixel_x,
                      landmarks[LandmarkIdx.MIDDLE_TIP].pixel_y)
        ring_tip = (landmarks[LandmarkIdx.RING_TIP].pixel_x,
                    landmarks[LandmarkIdx.RING_TIP].pixel_y)
        pinky_tip = (landmarks[LandmarkIdx.PINKY_TIP].pixel_x,
                     landmarks[LandmarkIdx.PINKY_TIP].pixel_y)

        # Compute palm center (average of MCP joints)
        mcp_indices = [
            LandmarkIdx.INDEX_MCP, LandmarkIdx.MIDDLE_MCP,
            LandmarkIdx.RING_MCP, LandmarkIdx.PINKY_MCP
        ]
        palm_x = int(np.mean([landmarks[i].pixel_x for i in mcp_indices]))
        palm_y = int(np.mean([landmarks[i].pixel_y for i in mcp_indices]))
        palm_center = (palm_x, palm_y)

        # Compute thumb-index distance
        thumb_index_dist = np.sqrt(
            (thumb_tip[0] - index_tip[0]) ** 2 +
            (thumb_tip[1] - index_tip[1]) ** 2
        )

        # Is pinching? (thumb and index close together)
        is_pinching = thumb_index_dist < self.grasp_threshold

        # Compute finger spread (average distance between consecutive fingertips)
        tips = [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]
        spreads = []
        for i in range(len(tips) - 1):
            dist = np.sqrt(
                (tips[i][0] - tips[i + 1][0]) ** 2 +
                (tips[i][1] - tips[i + 1][1]) ** 2
            )
            spreads.append(dist)
        finger_spread = np.mean(spreads) if spreads else 0.0

        # Is grasping? (all fingers curled — tips close to palm)
        tip_indices = [
            LandmarkIdx.INDEX_TIP, LandmarkIdx.MIDDLE_TIP,
            LandmarkIdx.RING_TIP, LandmarkIdx.PINKY_TIP
        ]
        tip_to_palm_dists = []
        for idx in tip_indices:
            dist = np.sqrt(
                (landmarks[idx].pixel_x - palm_x) ** 2 +
                (landmarks[idx].pixel_y - palm_y) ** 2
            )
            tip_to_palm_dists.append(dist)
        avg_tip_to_palm = np.mean(tip_to_palm_dists)

        # Wrist to MCP distance as reference for hand size
        wrist_to_middle_mcp = np.sqrt(
            (wrist[0] - landmarks[LandmarkIdx.MIDDLE_MCP].pixel_x) ** 2 +
            (wrist[1] - landmarks[LandmarkIdx.MIDDLE_MCP].pixel_y) ** 2
        )
        # Grasping if tips are within 60% of wrist-to-MCP distance
        is_grasping = (
            avg_tip_to_palm < wrist_to_middle_mcp * 0.6
            if wrist_to_middle_mcp > 0 else False
        )

        return HandState(
            handedness=handedness,
            confidence=confidence,
            landmarks=landmarks,
            wrist=wrist,
            thumb_tip=thumb_tip,
            index_tip=index_tip,
            middle_tip=middle_tip,
            ring_tip=ring_tip,
            pinky_tip=pinky_tip,
            palm_center=palm_center,
            is_pinching=is_pinching,
            is_grasping=is_grasping,
            finger_spread=finger_spread,
            thumb_index_dist=thumb_index_dist
        )

    def draw_landmarks(self, frame: np.ndarray, hand_states: List[HandState]) -> np.ndarray:
        """
        Draw hand landmarks on the frame for visualization.
        Returns the annotated frame.
        """
        annotated = frame.copy()

        for hand in hand_states:
            # Draw connections between landmarks
            connections = self._mp_hands.HAND_CONNECTIONS if self._mp_hands else []

            color = (0, 255, 128) if hand.handedness == "Right" else (255, 128, 0)

            # Draw landmark points
            for lm in hand.landmarks:
                cv2.circle(annotated, (lm.pixel_x, lm.pixel_y), 3, color, -1)

            # Draw connections
            for connection in connections:
                start_idx, end_idx = connection
                if start_idx < len(hand.landmarks) and end_idx < len(hand.landmarks):
                    start = hand.landmarks[start_idx]
                    end = hand.landmarks[end_idx]
                    cv2.line(
                        annotated,
                        (start.pixel_x, start.pixel_y),
                        (end.pixel_x, end.pixel_y),
                        color, 2
                    )

            # Draw palm center
            cv2.circle(annotated, hand.palm_center, 6, (0, 255, 255), -1)

            # Draw state labels
            label_parts = [hand.handedness]
            if hand.is_grasping:
                label_parts.append("GRASP")
            elif hand.is_pinching:
                label_parts.append("PINCH")
            label = " | ".join(label_parts)

            cv2.putText(
                annotated, label,
                (hand.wrist[0] - 30, hand.wrist[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )

        return annotated

    @property
    def inference_time_ms(self) -> float:
        return self._inference_time

    @property
    def is_available(self) -> bool:
        return self._available

    def close(self):
        """Release MediaPipe resources."""
        if self._hands:
            self._hands.close()
