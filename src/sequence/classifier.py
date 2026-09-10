"""
Sequence Reasoning Layer — Step Classifier
=============================================
Rule-based step classifier that maps SceneState features
to experiment step labels. Designed to be replaceable with
a learned model (e.g., MS-TCN++) in later phases.
"""

import logging
from typing import Tuple, Dict, Optional

from src.fusion.scene_state import SceneState, BoxState
from src.perception.interaction import InteractionState

logger = logging.getLogger(__name__)


class StepClassifier:
    """
    Maps SceneState to the most likely current experiment step.
    
    This is a rule-based classifier for the initial prototype.
    It analyzes object detections, hand states, and interaction
    patterns to determine which step is being performed.
    
    Returns (predicted_step_id, confidence).
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self._confidence_base = 0.7

    def classify(self, scene_state: SceneState) -> Tuple[str, float]:
        """
        Classify the current experiment step from scene state.
        
        Returns:
            Tuple of (step_id, confidence)
        """
        # Collect evidence for each possible step
        scores: Dict[str, float] = {}

        scores["IDLE"] = self._score_idle(scene_state)
        scores["OPEN_OUTER_BOX"] = self._score_open_outer_box(scene_state)
        scores["IDENTIFY_RED_BOX"] = self._score_identify_red(scene_state)
        scores["PLACE_RED_BOX"] = self._score_place_red(scene_state)
        scores["IDENTIFY_YELLOW_BOX"] = self._score_identify_yellow(scene_state)
        scores["PLACE_YELLOW_BOX"] = self._score_place_yellow(scene_state)
        scores["CLOSE_OUTER_BOX"] = self._score_close_outer_box(scene_state)
        scores["EXPERIMENT_COMPLETE"] = self._score_experiment_complete(scene_state)

        # Get the step with highest score
        best_step = max(scores, key=scores.get)
        best_score = scores[best_step]

        return best_step, best_score

    def get_preconditions_met(self, scene_state: SceneState) -> Dict[str, bool]:
        """
        Evaluate which preconditions are currently met.
        
        Returns dict mapping precondition names to boolean values.
        """
        return {
            "outer_box_open": scene_state.outer_box_open,
            "red_box_placed": scene_state.red_box_state == BoxState.PLACED,
            "yellow_box_placed": scene_state.yellow_box_state == BoxState.PLACED,
            "red_box_detected": scene_state.red_box_detected,
            "yellow_box_detected": scene_state.yellow_box_detected,
        }

    # ── Scoring functions for each step ─────────────────────────

    def _score_idle(self, state: SceneState) -> float:
        """Score for IDLE state."""
        score = 0.0

        # No objects detected → likely idle
        if not state.objects:
            score += 0.6

        # No hands detected → likely idle
        if state.hands_detected == 0:
            score += 0.3

        # No interactions → likely idle
        if not state.interactions:
            score += 0.2

        # Outer box NOT open and not interacting with it
        if not state.outer_box_open:
            score += 0.2

        return min(score, 0.95)

    def _score_open_outer_box(self, state: SceneState) -> float:
        """Score for OPEN_OUTER_BOX step."""
        score = 0.0

        # Outer box detected
        if state.outer_box_detected:
            score += 0.2

        # Hand interacting with outer box
        outer_interaction = state.active_interactions.get("outer_box")
        if outer_interaction in (InteractionState.TOUCHING, InteractionState.GRASPING):
            score += 0.4

        # Hands are near the outer box area
        if state.hands_detected > 0 and state.outer_box_bbox:
            score += 0.2

        # The box is becoming open (we start seeing inner boxes)
        if state.outer_box_open and not state.red_box_detected and not state.yellow_box_detected:
            score += 0.3

        return min(score, 0.95)

    def _score_identify_red(self, state: SceneState) -> float:
        """Score for IDENTIFY_RED_BOX step."""
        score = 0.0

        # Red box is detected
        if state.red_box_detected:
            score += 0.2

        # Hand is interacting with red box
        red_interaction = state.active_interactions.get("red_box")
        if red_interaction == InteractionState.GRASPING:
            score += 0.5
        elif red_interaction == InteractionState.HOLDING:
            score += 0.6
        elif red_interaction == InteractionState.TOUCHING:
            score += 0.3

        # Red box is in BEING_PICKED or IN_HAND state
        if state.red_box_state == BoxState.IN_HAND:
            score += 0.4
        elif state.red_box_state == BoxState.BEING_PICKED:
            score += 0.3

        # Outer box must be open
        if state.outer_box_open:
            score += 0.1

        return min(score, 0.95)

    def _score_place_red(self, state: SceneState) -> float:
        """Score for PLACE_RED_BOX step."""
        score = 0.0

        # Red box is being released
        red_interaction = state.active_interactions.get("red_box")
        if red_interaction == InteractionState.RELEASING:
            score += 0.5

        # Red box has been placed (displaced from original position)
        if state.red_box_state == BoxState.PLACED:
            score += 0.6

        # Red box is detected but no hand interaction
        if state.red_box_detected and red_interaction in (None, InteractionState.NONE):
            if state.red_box_state == BoxState.PLACED:
                score += 0.3

        return min(score, 0.95)

    def _score_identify_yellow(self, state: SceneState) -> float:
        """Score for IDENTIFY_YELLOW_BOX step."""
        score = 0.0

        # Yellow box detected
        if state.yellow_box_detected:
            score += 0.2

        # Hand interacting with yellow box
        yellow_interaction = state.active_interactions.get("yellow_box")
        if yellow_interaction == InteractionState.GRASPING:
            score += 0.5
        elif yellow_interaction == InteractionState.HOLDING:
            score += 0.6
        elif yellow_interaction == InteractionState.TOUCHING:
            score += 0.3

        # Yellow box in hand
        if state.yellow_box_state == BoxState.IN_HAND:
            score += 0.4
        elif state.yellow_box_state == BoxState.BEING_PICKED:
            score += 0.3

        if state.outer_box_open:
            score += 0.1

        return min(score, 0.95)

    def _score_place_yellow(self, state: SceneState) -> float:
        """Score for PLACE_YELLOW_BOX step."""
        score = 0.0

        yellow_interaction = state.active_interactions.get("yellow_box")
        if yellow_interaction == InteractionState.RELEASING:
            score += 0.5

        if state.yellow_box_state == BoxState.PLACED:
            score += 0.6

        if state.yellow_box_detected and yellow_interaction in (None, InteractionState.NONE):
            if state.yellow_box_state == BoxState.PLACED:
                score += 0.3

        return min(score, 0.95)

    def _score_close_outer_box(self, state: SceneState) -> float:
        """Score for CLOSE_OUTER_BOX step."""
        score = 0.0

        # Both boxes must be placed first
        if state.red_box_state == BoxState.PLACED:
            score += 0.15
        if state.yellow_box_state == BoxState.PLACED:
            score += 0.15

        # Hand interacting with outer box (to close it)
        outer_interaction = state.active_interactions.get("outer_box")
        if outer_interaction in (InteractionState.TOUCHING, InteractionState.GRASPING):
            score += 0.4

        # Outer box no longer appears open
        if not state.outer_box_open and state.outer_box_detected:
            score += 0.3

        # Inner boxes no longer visible (lid closed)
        if not state.red_box_detected and not state.yellow_box_detected:
            if state.red_box_state == BoxState.PLACED and state.yellow_box_state == BoxState.PLACED:
                score += 0.3

        return min(score, 0.95)

    def _score_experiment_complete(self, state: SceneState) -> float:
        """Score for EXPERIMENT_COMPLETE step."""
        score = 0.0

        # All boxes placed
        if state.red_box_state == BoxState.PLACED:
            score += 0.2
        if state.yellow_box_state == BoxState.PLACED:
            score += 0.2

        # Outer box closed
        if not state.outer_box_open:
            score += 0.2

        # No active interactions
        has_active = any(
            s not in (InteractionState.NONE, None)
            for s in state.active_interactions.values()
        )
        if not has_active:
            score += 0.2

        # No hands detected (operator stepped back)
        if state.hands_detected == 0:
            score += 0.1

        return min(score, 0.95)
