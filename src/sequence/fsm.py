"""
Sequence Reasoning Layer — Finite State Machine Engine
========================================================
Deterministic FSM that tracks experiment progress, detects
errors (skipped/out-of-sequence steps), and suggests next steps.
"""

import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Set, Callable

from .protocol import ExperimentProtocol

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of FSM events."""
    STEP_COMPLETED = "step_completed"
    STEP_STARTED = "step_started"
    SKIPPED_STEP = "skipped_step"
    OUT_OF_SEQUENCE = "out_of_sequence"
    NEXT_STEP_SUGGESTION = "next_step_suggestion"
    UNCERTAIN = "uncertain"
    EXPERIMENT_STARTED = "experiment_started"
    EXPERIMENT_COMPLETE = "experiment_complete"
    PRECONDITION_FAILED = "precondition_failed"


@dataclass
class FSMEvent:
    """An event emitted by the FSM."""
    event_type: EventType
    step_id: str
    message: str
    confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)
    details: Dict = field(default_factory=dict)


class ExperimentFSM:
    """
    Finite State Machine for experiment sequence validation.
    
    Tracks the current state, validates transitions, detects
    skipped/out-of-sequence steps, and suggests next steps.
    """

    def __init__(self, protocol: ExperimentProtocol, config: dict = None):
        config = config or {}
        self.protocol = protocol
        self.confidence_threshold = config.get("confidence_threshold", 0.6)
        self.step_hold_frames = config.get("step_hold_frames", 10)

        # State tracking
        self._current_step = "IDLE"
        self._completed_steps: Set[str] = set()
        self._step_history: List[tuple] = []  # (step_id, timestamp)
        self._step_start_time: float = time.time()
        self._experiment_started = False
        self._experiment_complete = False

        # For step stability: candidate step must be stable for N frames
        self._candidate_step: Optional[str] = None
        self._candidate_count: int = 0

        # Event listeners
        self._listeners: List[Callable[[FSMEvent], None]] = []

        logger.info(f"FSM initialized with protocol: {protocol.name}")

    def process_step_prediction(
        self,
        predicted_step: str,
        confidence: float,
        preconditions_met: Dict[str, bool] = None
    ) -> Optional[FSMEvent]:
        """
        Process a step prediction from the classifier.
        
        Args:
            predicted_step: The step ID predicted by the classifier
            confidence: Confidence score (0-1)
            preconditions_met: Dict of precondition flags
            
        Returns:
            FSMEvent if a state transition or error occurred, else None
        """
        if self._experiment_complete:
            return None

        if preconditions_met is None:
            preconditions_met = {}

        # Low confidence → uncertain
        if confidence < self.confidence_threshold:
            event = FSMEvent(
                event_type=EventType.UNCERTAIN,
                step_id=predicted_step,
                message=f"Low confidence ({confidence:.2f}) for step: {predicted_step}",
                confidence=confidence
            )
            self._emit_event(event)
            return event

        # Same step as current → no transition needed
        if predicted_step == self._current_step:
            self._candidate_step = None
            self._candidate_count = 0
            return None

        # Candidate stability check
        if predicted_step == self._candidate_step:
            self._candidate_count += 1
        else:
            self._candidate_step = predicted_step
            self._candidate_count = 1

        # Not stable enough yet
        if self._candidate_count < self.step_hold_frames:
            return None

        # Step is stable — validate the transition
        return self._attempt_transition(predicted_step, confidence, preconditions_met)

    def _attempt_transition(
        self,
        target_step: str,
        confidence: float,
        preconditions_met: Dict[str, bool]
    ) -> FSMEvent:
        """Attempt to transition to a new step."""

        # Check if transition is valid
        is_valid = self.protocol.is_valid_transition(self._current_step, target_step)

        if not is_valid:
            # Check if it's a skipped step or out-of-sequence
            event_type = self._classify_error(target_step)
            event = FSMEvent(
                event_type=event_type,
                step_id=target_step,
                message=self._build_error_message(event_type, target_step),
                confidence=confidence,
                details={
                    "current_step": self._current_step,
                    "attempted_step": target_step,
                    "valid_transitions": self.protocol.get_valid_next_steps(self._current_step)
                }
            )
            self._emit_event(event)
            return event

        # Check preconditions
        required_preconditions = self.protocol.get_preconditions(target_step)
        unmet = [p for p in required_preconditions if not preconditions_met.get(p, False)]

        if unmet:
            event = FSMEvent(
                event_type=EventType.PRECONDITION_FAILED,
                step_id=target_step,
                message=f"Cannot proceed to {target_step}: unmet preconditions: {', '.join(unmet)}",
                confidence=confidence,
                details={"unmet_preconditions": unmet}
            )
            self._emit_event(event)
            return event

        # Valid transition — execute it
        return self._execute_transition(target_step, confidence)

    def _execute_transition(self, target_step: str, confidence: float) -> FSMEvent:
        """Execute a valid state transition."""
        old_step = self._current_step

        # Mark current step as completed
        self._completed_steps.add(old_step)
        self._step_history.append((old_step, time.time()))

        # Transition
        self._current_step = target_step
        self._step_start_time = time.time()
        self._candidate_step = None
        self._candidate_count = 0

        # Determine event type
        if target_step == "EXPERIMENT_COMPLETE":
            self._experiment_complete = True
            self._completed_steps.add(target_step)
            event = FSMEvent(
                event_type=EventType.EXPERIMENT_COMPLETE,
                step_id=target_step,
                message="Experiment completed successfully! All steps done.",
                confidence=confidence,
                details={
                    "total_steps": len(self._step_history),
                    "completed": list(self._completed_steps)
                }
            )
        elif old_step == "IDLE":
            self._experiment_started = True
            event = FSMEvent(
                event_type=EventType.EXPERIMENT_STARTED,
                step_id=target_step,
                message=f"Experiment started. First step: {target_step}",
                confidence=confidence
            )
        else:
            event = FSMEvent(
                event_type=EventType.STEP_COMPLETED,
                step_id=target_step,
                message=f"Step completed: {old_step}. Now at: {target_step}",
                confidence=confidence,
                details={
                    "previous_step": old_step,
                    "current_step": target_step
                }
            )

        self._emit_event(event)

        # Also emit next-step suggestion
        self._suggest_next_step()

        return event

    def _classify_error(self, attempted_step: str) -> EventType:
        """
        Classify an invalid transition as skipped or out-of-sequence.
        
        - SKIPPED: if the attempted step is reachable from current step
          by skipping one or more intermediate steps
        - OUT_OF_SEQUENCE: if the attempted step is not in the forward path at all
        """
        # Check if attempted step is "ahead" in the protocol
        valid_next = self.protocol.get_valid_next_steps(self._current_step)

        # BFS to see if we can reach the attempted step
        visited = set()
        frontier = list(valid_next)

        while frontier:
            candidate = frontier.pop(0)
            if candidate == attempted_step:
                return EventType.SKIPPED_STEP
            if candidate not in visited:
                visited.add(candidate)
                frontier.extend(self.protocol.get_valid_next_steps(candidate))

        return EventType.OUT_OF_SEQUENCE

    def _build_error_message(self, event_type: EventType, target_step: str) -> str:
        """Build a human-readable error message."""
        step_info = self.protocol.get_step(target_step)
        step_name = step_info.name if step_info else target_step
        current_info = self.protocol.get_step(self._current_step)
        current_name = current_info.name if current_info else self._current_step

        if event_type == EventType.SKIPPED_STEP:
            valid_next = self.protocol.get_valid_next_steps(self._current_step)
            next_names = []
            for s in valid_next:
                si = self.protocol.get_step(s)
                next_names.append(si.name if si else s)
            return (
                f"Warning! Step skipped. You are at '{current_name}' "
                f"but attempted '{step_name}'. "
                f"Expected next: {', '.join(next_names)}"
            )
        else:
            return (
                f"Alert! Out of sequence. '{step_name}' is not valid "
                f"from current step '{current_name}'. "
                f"Please follow the correct sequence."
            )

    def _suggest_next_step(self):
        """Emit a next-step suggestion event."""
        valid_next = self.protocol.get_valid_next_steps(self._current_step)
        if valid_next:
            # Suggest the first valid next step
            next_step = valid_next[0]
            step_info = self.protocol.get_step(next_step)
            step_name = step_info.name if step_info else next_step

            event = FSMEvent(
                event_type=EventType.NEXT_STEP_SUGGESTION,
                step_id=next_step,
                message=f"Next step: {step_name}",
                details={"all_valid_next": valid_next}
            )
            self._emit_event(event)

    def add_listener(self, listener: Callable[[FSMEvent], None]):
        """Add an event listener callback."""
        self._listeners.append(listener)

    def _emit_event(self, event: FSMEvent):
        """Emit an event to all listeners."""
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in FSM event listener: {e}")

    def force_transition(self, step_id: str):
        """Force a transition (for manual override / testing)."""
        self._completed_steps.add(self._current_step)
        self._step_history.append((self._current_step, time.time()))
        self._current_step = step_id
        self._step_start_time = time.time()
        logger.info(f"Forced transition to: {step_id}")

    def reset(self):
        """Reset the FSM to initial state."""
        self._current_step = "IDLE"
        self._completed_steps.clear()
        self._step_history.clear()
        self._step_start_time = time.time()
        self._experiment_started = False
        self._experiment_complete = False
        self._candidate_step = None
        self._candidate_count = 0
        logger.info("FSM reset to IDLE")

    # ── Properties ──────────────────────────────────────────────

    @property
    def current_step(self) -> str:
        return self._current_step

    @property
    def completed_steps(self) -> Set[str]:
        return self._completed_steps.copy()

    @property
    def step_history(self) -> List[tuple]:
        return list(self._step_history)

    @property
    def is_complete(self) -> bool:
        return self._experiment_complete

    @property
    def is_started(self) -> bool:
        return self._experiment_started

    @property
    def current_step_duration(self) -> float:
        """Seconds spent in the current step."""
        return time.time() - self._step_start_time

    @property
    def progress_fraction(self) -> float:
        """Completion progress as a fraction (0.0 to 1.0)."""
        total = self.protocol.actionable_steps
        done = len([
            s for s in self._completed_steps
            if s not in ("IDLE", "EXPERIMENT_COMPLETE")
        ])
        return min(done / total, 1.0) if total > 0 else 0.0

    def get_valid_transitions(self) -> List[str]:
        """Get valid transitions from current step."""
        return self.protocol.get_valid_next_steps(self._current_step)

    def get_graph_dot(self) -> str:
        """Get DOT representation of the FSM with current state highlighted."""
        return self.protocol.to_dot(
            current_step=self._current_step,
            completed_steps=self._completed_steps
        )
