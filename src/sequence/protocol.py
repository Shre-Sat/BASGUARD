"""
Sequence Reasoning Layer — Experiment Protocol Definition
==========================================================
Defines the BAS experiment as a directed graph of steps
with preconditions and valid transitions.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ExperimentStep:
    """Definition of a single experiment step."""
    id: str
    name: str
    description: str
    expected_duration_range: tuple = (2.0, 30.0)  # (min_seconds, max_seconds)
    preconditions: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    is_terminal: bool = False


class ExperimentProtocol:
    """
    Defines the experiment as a directed graph of steps.
    
    The red/yellow box experiment:
    ─────────────────────────────
    IDLE → OPEN_OUTER_BOX → IDENTIFY_RED_BOX → PLACE_RED_BOX
                          ↘                      ↓
                           IDENTIFY_YELLOW_BOX → PLACE_YELLOW_BOX
                                                  ↓
                                          CLOSE_OUTER_BOX → EXPERIMENT_COMPLETE
    
    Note: Red and yellow boxes can be handled in either order.
    """

    def __init__(self, protocol_name: str = "red_yellow_box"):
        self.name = protocol_name
        self.steps: Dict[str, ExperimentStep] = {}
        self._build_protocol()

    def _build_protocol(self):
        """Build the red/yellow box experiment protocol."""
        steps = [
            ExperimentStep(
                id="IDLE",
                name="Idle",
                description="Operator is idle, experiment not started",
                next_steps=["OPEN_OUTER_BOX"],
                expected_duration_range=(0.0, 60.0)
            ),
            ExperimentStep(
                id="OPEN_OUTER_BOX",
                name="Open Outer Box",
                description="Open the lid of the outer box to reveal inner boxes",
                next_steps=["IDENTIFY_RED_BOX", "IDENTIFY_YELLOW_BOX"],
                expected_duration_range=(2.0, 15.0)
            ),
            ExperimentStep(
                id="IDENTIFY_RED_BOX",
                name="Identify Red Box",
                description="Pick up and identify the red box from inside the outer box",
                next_steps=["PLACE_RED_BOX"],
                expected_duration_range=(2.0, 20.0),
                preconditions=["outer_box_open"]
            ),
            ExperimentStep(
                id="PLACE_RED_BOX",
                name="Place Red Box",
                description="Place the red box at its designated location",
                next_steps=["IDENTIFY_YELLOW_BOX", "CLOSE_OUTER_BOX"],
                expected_duration_range=(2.0, 15.0),
                preconditions=["outer_box_open"]
            ),
            ExperimentStep(
                id="IDENTIFY_YELLOW_BOX",
                name="Identify Yellow Box",
                description="Pick up and identify the yellow box from inside the outer box",
                next_steps=["PLACE_YELLOW_BOX"],
                expected_duration_range=(2.0, 20.0),
                preconditions=["outer_box_open"]
            ),
            ExperimentStep(
                id="PLACE_YELLOW_BOX",
                name="Place Yellow Box",
                description="Place the yellow box at its designated location",
                next_steps=["IDENTIFY_RED_BOX", "CLOSE_OUTER_BOX"],
                expected_duration_range=(2.0, 15.0),
                preconditions=["outer_box_open"]
            ),
            ExperimentStep(
                id="CLOSE_OUTER_BOX",
                name="Close Outer Box",
                description="Close the lid of the outer box",
                next_steps=["EXPERIMENT_COMPLETE"],
                expected_duration_range=(2.0, 15.0),
                preconditions=["red_box_placed", "yellow_box_placed"]
            ),
            ExperimentStep(
                id="EXPERIMENT_COMPLETE",
                name="Experiment Complete",
                description="All steps completed successfully",
                next_steps=[],
                is_terminal=True,
                expected_duration_range=(0.0, 0.0)
            ),
        ]

        for step in steps:
            self.steps[step.id] = step

    def get_step(self, step_id: str) -> Optional[ExperimentStep]:
        """Get a step by ID."""
        return self.steps.get(step_id)

    def get_valid_next_steps(self, current_step_id: str) -> List[str]:
        """Get valid next step IDs from current step."""
        step = self.steps.get(current_step_id)
        return step.next_steps if step else []

    def get_all_step_ids(self) -> List[str]:
        """Get all step IDs in protocol order."""
        return list(self.steps.keys())

    def get_step_index(self, step_id: str) -> int:
        """Get the index of a step in the protocol."""
        ids = self.get_all_step_ids()
        return ids.index(step_id) if step_id in ids else -1

    def is_valid_transition(self, from_step: str, to_step: str) -> bool:
        """Check if a transition from one step to another is valid."""
        step = self.steps.get(from_step)
        if step is None:
            return False
        return to_step in step.next_steps

    def get_preconditions(self, step_id: str) -> List[str]:
        """Get preconditions for a step."""
        step = self.steps.get(step_id)
        return step.preconditions if step else []

    def to_dot(self, current_step: str = "", completed_steps: set = None) -> str:
        """
        Generate Graphviz DOT representation of the protocol.
        
        Args:
            current_step: Current active step (highlighted in orange)
            completed_steps: Set of completed step IDs (shown in green)
        """
        if completed_steps is None:
            completed_steps = set()

        lines = [
            'digraph ExperimentProtocol {',
            '    rankdir=LR;',
            '    bgcolor="transparent";',
            '    node [shape=box, style="rounded,filled", fontname="Inter", fontsize=11];',
            '    edge [fontname="Inter", fontsize=9, color="#4a5568"];',
            ''
        ]

        for step_id, step in self.steps.items():
            # Determine node styling
            if step_id == current_step:
                color = '#FF6B00'  # ISRO orange — current step
                fontcolor = 'white'
                penwidth = '3'
            elif step_id in completed_steps:
                color = '#00E676'  # Green — completed
                fontcolor = '#1a1a2e'
                penwidth = '2'
            elif step.is_terminal:
                color = '#00B4D8'  # Blue — terminal
                fontcolor = 'white'
                penwidth = '2'
            else:
                color = '#2d3748'  # Dark grey — pending
                fontcolor = '#e2e8f0'
                penwidth = '1'

            label = f"{step.name}\\n({step_id})"
            lines.append(
                f'    {step_id} [label="{label}", fillcolor="{color}", '
                f'fontcolor="{fontcolor}", penwidth={penwidth}];'
            )

        lines.append('')

        # Edges
        for step_id, step in self.steps.items():
            for next_step in step.next_steps:
                edge_color = '#FF6B00' if step_id == current_step else '#4a5568'
                lines.append(
                    f'    {step_id} -> {next_step} [color="{edge_color}"];'
                )

        lines.append('}')
        return '\n'.join(lines)

    @property
    def total_steps(self) -> int:
        """Total number of steps (including IDLE and COMPLETE)."""
        return len(self.steps)

    @property
    def actionable_steps(self) -> int:
        """Number of actionable steps (excluding IDLE and COMPLETE)."""
        return len([s for s in self.steps.values() if not s.is_terminal and s.id != "IDLE"])
