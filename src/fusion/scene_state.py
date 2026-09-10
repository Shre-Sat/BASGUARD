"""
Fusion Layer — Scene State Fusion
===================================
Merges perception outputs (object detections, hand states,
interactions) into a unified SceneState for downstream reasoning.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum

from src.perception.object_detector import Detection
from src.perception.hand_tracker import HandState
from src.perception.interaction import Interaction, InteractionState

logger = logging.getLogger(__name__)


class BoxState(Enum):
    """State of a box in the experiment."""
    UNKNOWN = "unknown"
    INSIDE_OUTER = "inside_outer"
    BEING_PICKED = "being_picked"
    IN_HAND = "in_hand"
    PLACED = "placed"


@dataclass
class SceneState:
    """
    Unified scene state combining all perception outputs.
    This is the single input to the Sequence Reasoning layer.
    """
    timestamp: float = 0.0
    frame_id: int = 0

    # Raw perception data
    objects: List[Detection] = field(default_factory=list)
    hands: List[HandState] = field(default_factory=list)
    interactions: List[Interaction] = field(default_factory=list)

    # Inferred high-level states
    outer_box_detected: bool = False
    outer_box_open: bool = False
    red_box_detected: bool = False
    red_box_state: BoxState = BoxState.UNKNOWN
    yellow_box_detected: bool = False
    yellow_box_state: BoxState = BoxState.UNKNOWN
    hands_detected: int = 0

    # Positions for spatial reasoning
    outer_box_bbox: Optional[tuple] = None
    red_box_bbox: Optional[tuple] = None
    yellow_box_bbox: Optional[tuple] = None

    # Interaction summaries
    active_interactions: Dict[str, InteractionState] = field(default_factory=dict)
    # e.g., {"red_box": InteractionState.GRASPING, "yellow_box": InteractionState.NONE}


class SceneStateFusion:
    """
    Fuses perception layer outputs into a coherent SceneState.
    
    Runs at ~10-15 Hz, computing derived/inferred features
    from raw detection + hand + interaction data.
    """

    def __init__(self, config: dict = None):
        self._frame_count = 0
        self._last_scene_state = SceneState()

        # Track box positions over time for placement detection
        self._red_box_initial_pos = None
        self._yellow_box_initial_pos = None
        self._outer_box_initial_area = None
        self._placement_threshold = 150  # pixels displacement for "placed"

    def fuse(
        self,
        detections: List[Detection],
        hands: List[HandState],
        interactions: List[Interaction]
    ) -> SceneState:
        """
        Create a unified SceneState from perception outputs.
        
        Args:
            detections: Object detections from ObjectDetector
            hands: Hand states from HandTracker
            interactions: Hand-object interactions from InteractionClassifier
            
        Returns:
            SceneState with both raw data and inferred high-level states
        """
        self._frame_count += 1

        state = SceneState(
            timestamp=time.time(),
            frame_id=self._frame_count,
            objects=detections,
            hands=hands,
            interactions=interactions,
            hands_detected=len(hands)
        )

        # Analyze detected objects
        for det in detections:
            if det.class_name == "outer_box":
                state.outer_box_detected = True
                state.outer_box_bbox = det.bbox
                # Check if outer box is open (compare area to initial)
                if self._outer_box_initial_area is None:
                    self._outer_box_initial_area = det.area
                state.outer_box_open = self._check_outer_box_open(det)

            elif det.class_name == "red_box":
                state.red_box_detected = True
                state.red_box_bbox = det.bbox
                if self._red_box_initial_pos is None:
                    self._red_box_initial_pos = det.center

            elif det.class_name == "yellow_box":
                state.yellow_box_detected = True
                state.yellow_box_bbox = det.bbox
                if self._yellow_box_initial_pos is None:
                    self._yellow_box_initial_pos = det.center

        # Determine box states from interactions
        state.red_box_state = self._determine_box_state("red_box", interactions, detections)
        state.yellow_box_state = self._determine_box_state("yellow_box", interactions, detections)

        # Build interaction summary
        for interaction in interactions:
            obj_name = interaction.object_name
            # Keep the most active interaction state for each object
            if obj_name not in state.active_interactions:
                state.active_interactions[obj_name] = interaction.state
            else:
                current = state.active_interactions[obj_name]
                if self._interaction_priority(interaction.state) > self._interaction_priority(current):
                    state.active_interactions[obj_name] = interaction.state

        # Infer outer box open state from seeing inner boxes
        if state.red_box_detected or state.yellow_box_detected:
            state.outer_box_open = True

        self._last_scene_state = state
        return state

    def _determine_box_state(
        self,
        box_name: str,
        interactions: List[Interaction],
        detections: List[Detection]
    ) -> BoxState:
        """Determine the high-level state of a specific box."""

        # Find interactions involving this box
        box_interactions = [
            i for i in interactions if i.object_name == box_name
        ]

        if not box_interactions:
            # No interaction — check if box is detected and where
            box_det = next(
                (d for d in detections if d.class_name == box_name),
                None
            )
            if box_det is None:
                return BoxState.UNKNOWN

            # Check if displaced from initial position
            initial_pos = (
                self._red_box_initial_pos if box_name == "red_box"
                else self._yellow_box_initial_pos
            )
            if initial_pos and self._is_displaced(box_det.center, initial_pos):
                return BoxState.PLACED
            return BoxState.INSIDE_OUTER

        # Get the most active interaction
        max_interaction = max(
            box_interactions,
            key=lambda i: self._interaction_priority(i.state)
        )

        if max_interaction.state in (InteractionState.HOLDING, InteractionState.GRASPING):
            return BoxState.IN_HAND
        elif max_interaction.state == InteractionState.TOUCHING:
            return BoxState.BEING_PICKED
        elif max_interaction.state == InteractionState.RELEASING:
            return BoxState.PLACED

        return BoxState.INSIDE_OUTER

    def _check_outer_box_open(self, det: Detection) -> bool:
        """
        Check if the outer box appears to be open.
        Heuristic: aspect ratio changes when lid is up,
        or area changes significantly.
        """
        if self._outer_box_initial_area is None:
            return False

        # If the box area changed significantly, the lid might be open
        area_ratio = det.area / self._outer_box_initial_area if self._outer_box_initial_area > 0 else 1.0
        return area_ratio > 1.3 or area_ratio < 0.7

    def _is_displaced(
        self,
        current_pos: tuple,
        initial_pos: tuple
    ) -> bool:
        """Check if an object has moved significantly from its initial position."""
        import math
        dist = math.sqrt(
            (current_pos[0] - initial_pos[0]) ** 2 +
            (current_pos[1] - initial_pos[1]) ** 2
        )
        return dist > self._placement_threshold

    @staticmethod
    def _interaction_priority(state: InteractionState) -> int:
        """Priority ordering for interaction states."""
        priority = {
            InteractionState.NONE: 0,
            InteractionState.APPROACHING: 1,
            InteractionState.TOUCHING: 2,
            InteractionState.GRASPING: 3,
            InteractionState.HOLDING: 4,
            InteractionState.RELEASING: 5,
        }
        return priority.get(state, 0)

    def reset(self):
        """Reset all tracked positions for a new experiment run."""
        self._frame_count = 0
        self._red_box_initial_pos = None
        self._yellow_box_initial_pos = None
        self._outer_box_initial_area = None
        self._last_scene_state = SceneState()

    @property
    def last_state(self) -> SceneState:
        return self._last_scene_state
