"""
Perception Layer — Hand-Object Interaction Classifier
======================================================
Combines object detections and hand landmarks to classify
interaction states between each hand and each object.
"""

import numpy as np
import logging
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional

from .object_detector import Detection
from .hand_tracker import HandState

logger = logging.getLogger(__name__)


class InteractionState(Enum):
    """Hand-object interaction states."""
    NONE = "none"
    APPROACHING = "approaching"
    TOUCHING = "touching"
    GRASPING = "grasping"
    HOLDING = "holding"
    RELEASING = "releasing"


@dataclass
class Interaction:
    """Represents the interaction between one hand and one object."""
    hand_label: str           # "Left" or "Right"
    object_name: str          # e.g., "red_box"
    state: InteractionState
    distance: float           # pixels between hand center and object center
    confidence: float
    hand_state: Optional[HandState] = None
    object_detection: Optional[Detection] = None


class InteractionClassifier:
    """
    Classifies hand-object interaction states by combining:
    - Spatial proximity between hand landmarks and object bounding boxes
    - Hand pose features (pinch, grasp, finger spread)
    - Temporal smoothing to eliminate flicker
    
    State transitions:
    NONE → APPROACHING → TOUCHING → GRASPING → HOLDING
    HOLDING → RELEASING → NONE
    """

    def __init__(self, config: dict):
        self.proximity_threshold = config.get("interaction_proximity_px", 100)
        self.grasp_threshold = config.get("grasp_finger_threshold", 40)
        self.smooth_window = config.get("temporal_smooth_window", 5)

        # History for temporal smoothing: key = (hand_label, object_name)
        self._history: Dict[Tuple[str, str], deque] = {}
        self._inference_time = 0.0

    def classify(
        self,
        hands: List[HandState],
        detections: List[Detection]
    ) -> List[Interaction]:
        """
        Classify interactions between all detected hands and objects.
        
        Returns list of Interaction objects for each (hand, object) pair
        where a meaningful interaction is detected.
        """
        start_time = time.monotonic()
        interactions = []

        # Filter out "person" detections — we only want objects
        objects = [d for d in detections if d.class_name != "person"]

        for hand in hands:
            for obj in objects:
                interaction = self._classify_pair(hand, obj)
                if interaction.state != InteractionState.NONE:
                    interactions.append(interaction)

        # Temporal smoothing
        interactions = self._smooth_interactions(interactions, hands, objects)

        self._inference_time = (time.monotonic() - start_time) * 1000
        return interactions

    def _classify_pair(
        self, hand: HandState, obj: Detection
    ) -> Interaction:
        """Classify the interaction between a single hand and object."""

        # Compute distance between hand palm center and object center
        dist = np.sqrt(
            (hand.palm_center[0] - obj.center[0]) ** 2 +
            (hand.palm_center[1] - obj.center[1]) ** 2
        )

        # Check if hand is inside or overlapping the object bbox
        hand_in_bbox = self._point_in_bbox(hand.palm_center, obj.bbox)
        fingertips_in_bbox = self._count_fingertips_in_bbox(hand, obj.bbox)

        # Determine state based on spatial and pose features
        state = InteractionState.NONE
        confidence = 0.0

        if dist > self.proximity_threshold * 2:
            state = InteractionState.NONE
            confidence = 0.9
        elif dist > self.proximity_threshold:
            state = InteractionState.APPROACHING
            confidence = 0.7
        elif hand_in_bbox or fingertips_in_bbox >= 2:
            if hand.is_grasping or hand.is_pinching:
                state = InteractionState.GRASPING
                confidence = 0.85
            else:
                state = InteractionState.TOUCHING
                confidence = 0.75
        elif dist <= self.proximity_threshold:
            state = InteractionState.APPROACHING
            confidence = 0.65

        return Interaction(
            hand_label=hand.handedness,
            object_name=obj.class_name,
            state=state,
            distance=dist,
            confidence=confidence,
            hand_state=hand,
            object_detection=obj
        )

    def _smooth_interactions(
        self,
        current_interactions: List[Interaction],
        hands: List[HandState],
        objects: List[Detection]
    ) -> List[Interaction]:
        """
        Apply temporal smoothing to stabilize interaction states.
        Uses a sliding window majority vote.
        """
        smoothed = []

        # Build current state map
        current_map: Dict[Tuple[str, str], Interaction] = {}
        for interaction in current_interactions:
            key = (interaction.hand_label, interaction.object_name)
            current_map[key] = interaction

        # Update histories and compute smoothed states
        all_keys = set(current_map.keys()) | set(self._history.keys())

        for key in all_keys:
            # Get or create history
            if key not in self._history:
                self._history[key] = deque(maxlen=self.smooth_window)

            if key in current_map:
                self._history[key].append(current_map[key].state)
            else:
                self._history[key].append(InteractionState.NONE)

            # Majority vote
            history = self._history[key]
            if len(history) > 0:
                state_counts: Dict[InteractionState, int] = {}
                for s in history:
                    state_counts[s] = state_counts.get(s, 0) + 1
                smoothed_state = max(state_counts, key=state_counts.get)

                # Check for HOLDING: if GRASPING is sustained
                if smoothed_state == InteractionState.GRASPING:
                    grasp_count = state_counts.get(InteractionState.GRASPING, 0)
                    if grasp_count >= self.smooth_window * 0.7:
                        smoothed_state = InteractionState.HOLDING

                # Check for RELEASING: was HOLDING/GRASPING, now TOUCHING/NONE
                prev_states = list(history)
                if len(prev_states) >= 3:
                    recent_holding = any(
                        s in (InteractionState.HOLDING, InteractionState.GRASPING)
                        for s in prev_states[-3:-1]
                    )
                    now_not_holding = prev_states[-1] in (
                        InteractionState.NONE, InteractionState.TOUCHING,
                        InteractionState.APPROACHING
                    )
                    if recent_holding and now_not_holding:
                        smoothed_state = InteractionState.RELEASING

                if smoothed_state != InteractionState.NONE:
                    if key in current_map:
                        interaction = current_map[key]
                        interaction.state = smoothed_state
                        smoothed.append(interaction)
                    else:
                        # Create a synthetic interaction for the smoothed state
                        smoothed.append(Interaction(
                            hand_label=key[0],
                            object_name=key[1],
                            state=smoothed_state,
                            distance=0.0,
                            confidence=0.6
                        ))

        # Clean up stale history entries
        stale_keys = [
            k for k, v in self._history.items()
            if len(v) == self.smooth_window
            and all(s == InteractionState.NONE for s in v)
        ]
        for k in stale_keys:
            del self._history[k]

        return smoothed

    @staticmethod
    def _point_in_bbox(
        point: Tuple[int, int],
        bbox: Tuple[int, int, int, int]
    ) -> bool:
        """Check if a point is inside a bounding box."""
        x, y = point
        x1, y1, x2, y2 = bbox
        return x1 <= x <= x2 and y1 <= y <= y2

    @staticmethod
    def _count_fingertips_in_bbox(
        hand: HandState,
        bbox: Tuple[int, int, int, int]
    ) -> int:
        """Count how many fingertips are inside the object's bounding box."""
        x1, y1, x2, y2 = bbox
        tips = [
            hand.thumb_tip, hand.index_tip, hand.middle_tip,
            hand.ring_tip, hand.pinky_tip
        ]
        count = 0
        for tx, ty in tips:
            if x1 <= tx <= x2 and y1 <= ty <= y2:
                count += 1
        return count

    @property
    def inference_time_ms(self) -> float:
        return self._inference_time

    def reset(self):
        """Clear all interaction history."""
        self._history.clear()
