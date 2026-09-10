"""
GUI Layer — Step Sequence Timeline Panel
==========================================
Horizontal progress bar showing experiment steps with
color-coded status and pulsing current-step indicator.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient

from .styles import COLORS

import logging
logger = logging.getLogger(__name__)


class StepNode(QFrame):
    """A single step node in the timeline."""

    def __init__(self, step_id: str, step_name: str, index: int, parent=None):
        super().__init__(parent)
        self.step_id = step_id
        self.step_name = step_name
        self.index = index
        self._status = "pending"  # pending, current, completed, error
        self._glow_opacity = 0

        self.setFixedSize(90, 70)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Step number
        self._number_label = QLabel(f"{self.index + 1}")
        self._number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._number_label.setFont(QFont("Rajdhani", 14, QFont.Weight.Bold))
        self._number_label.setStyleSheet("background: transparent;")
        layout.addWidget(self._number_label)

        # Step name (abbreviated)
        short_name = self.step_name
        if len(short_name) > 12:
            short_name = short_name[:11] + "…"
        self._name_label = QLabel(short_name)
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_label.setFont(QFont("Inter", 8))
        self._name_label.setWordWrap(True)
        self._name_label.setStyleSheet("background: transparent;")
        layout.addWidget(self._name_label)

        self._update_style()

    def set_status(self, status: str):
        """Set node status: 'pending', 'current', 'completed', 'error'."""
        self._status = status
        self._update_style()

    def _update_style(self):
        styles = {
            "pending": {
                "bg": COLORS["bg_card"],
                "border": COLORS["border_subtle"],
                "text": COLORS["text_dim"],
                "number_color": COLORS["text_dim"],
            },
            "current": {
                "bg": COLORS["isro_orange"],
                "border": COLORS["isro_orange_glow"],
                "text": "white",
                "number_color": "white",
            },
            "completed": {
                "bg": "#0d3320",
                "border": COLORS["accent_green"],
                "text": COLORS["accent_green"],
                "number_color": COLORS["accent_green"],
            },
            "error": {
                "bg": "#3d0d0d",
                "border": COLORS["accent_red"],
                "text": COLORS["accent_red"],
                "number_color": COLORS["accent_red"],
            },
        }

        s = styles.get(self._status, styles["pending"])

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {s["bg"]};
                border: 2px solid {s["border"]};
                border-radius: 10px;
            }}
        """)
        self._number_label.setStyleSheet(f"color: {s['number_color']}; background: transparent;")
        self._name_label.setStyleSheet(f"color: {s['text']}; background: transparent;")

    @property
    def status(self) -> str:
        return self._status


class TimelinePanel(QWidget):
    """
    Horizontal step-sequence timeline with progress visualization.
    
    Shows all experiment steps as connected nodes:
    [1]✓ ──── [2]✓ ──── [3]● ──── [4] ──── [5] ──── [6]
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._step_nodes: dict = {}  # step_id → StepNode
        self._connector_labels: list = []
        self._current_step = ""
        self._next_step = ""

        self._setup_ui()

        # Pulsing animation timer for current step
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_current)
        self._pulse_visible = True

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(4)

        # Title
        title = QLabel("EXPERIMENT PROGRESS")
        title.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent; letter-spacing: 1px;")
        main_layout.addWidget(title)

        # Progress info
        self._progress_label = QLabel("Status: IDLE  |  Progress: 0%")
        self._progress_label.setFont(QFont("JetBrains Mono", 10))
        self._progress_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        main_layout.addWidget(self._progress_label)

        # Suggestion label
        self._suggestion_label = QLabel("")
        self._suggestion_label.setFont(QFont("Inter", 11))
        self._suggestion_label.setStyleSheet(f"""
            color: {COLORS['accent_cyan']};
            background: transparent;
            padding: 2px;
        """)
        main_layout.addWidget(self._suggestion_label)

        # Timeline container
        self._timeline_layout = QHBoxLayout()
        self._timeline_layout.setContentsMargins(0, 0, 0, 0)
        self._timeline_layout.setSpacing(0)
        self._timeline_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(self._timeline_layout)

    def setup_steps(self, steps: list):
        """
        Initialize the timeline with experiment steps.
        
        Args:
            steps: List of (step_id, step_name) tuples in order
        """
        # Clear existing
        while self._timeline_layout.count():
            item = self._timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._step_nodes.clear()
        self._connector_labels.clear()

        for i, (step_id, step_name) in enumerate(steps):
            # Add step node
            node = StepNode(step_id, step_name, i)
            self._step_nodes[step_id] = node
            self._timeline_layout.addWidget(node)

            # Add connector between nodes (except after last)
            if i < len(steps) - 1:
                connector = QLabel("───")
                connector.setAlignment(Qt.AlignmentFlag.AlignCenter)
                connector.setFont(QFont("monospace", 10))
                connector.setStyleSheet(f"color: {COLORS['border_subtle']}; background: transparent;")
                connector.setFixedWidth(30)
                self._timeline_layout.addWidget(connector)
                self._connector_labels.append(connector)

    def update_state(
        self,
        current_step: str,
        completed_steps: set,
        next_suggestion: str = "",
        progress: float = 0.0,
        errors: set = None
    ):
        """Update the timeline to reflect current experiment state."""
        self._current_step = current_step
        self._next_step = next_suggestion
        errors = errors or set()

        for step_id, node in self._step_nodes.items():
            if step_id in errors:
                node.set_status("error")
            elif step_id == current_step:
                node.set_status("current")
            elif step_id in completed_steps:
                node.set_status("completed")
            else:
                node.set_status("pending")

        # Update connector colors
        step_ids = list(self._step_nodes.keys())
        for i, connector in enumerate(self._connector_labels):
            if i < len(step_ids) - 1:
                if step_ids[i] in completed_steps:
                    connector.setStyleSheet(
                        f"color: {COLORS['accent_green']}; background: transparent;"
                    )
                elif step_ids[i] == current_step:
                    connector.setStyleSheet(
                        f"color: {COLORS['isro_orange']}; background: transparent;"
                    )
                else:
                    connector.setStyleSheet(
                        f"color: {COLORS['border_subtle']}; background: transparent;"
                    )

        # Update progress label
        pct = int(progress * 100)
        self._progress_label.setText(
            f"Current: {current_step}  |  Progress: {pct}%"
        )

        # Update suggestion
        if next_suggestion:
            self._suggestion_label.setText(f"NEXT: {next_suggestion}")
        else:
            self._suggestion_label.setText("")

        # Start pulsing animation
        if not self._pulse_timer.isActive():
            self._pulse_timer.start(600)

    def _pulse_current(self):
        """Pulse the current step node for visual attention."""
        if self._current_step in self._step_nodes:
            node = self._step_nodes[self._current_step]
            self._pulse_visible = not self._pulse_visible
            if self._pulse_visible:
                node.setStyleSheet(f"""
                    QFrame {{
                        background-color: {COLORS['isro_orange']};
                        border: 2px solid {COLORS['isro_orange_glow']};
                        border-radius: 10px;
                    }}
                """)
            else:
                node.setStyleSheet(f"""
                    QFrame {{
                        background-color: {COLORS['isro_orange_dark']};
                        border: 2px solid {COLORS['isro_orange']};
                        border-radius: 10px;
                    }}
                """)
