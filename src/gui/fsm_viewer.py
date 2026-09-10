"""
GUI Layer — FSM State Diagram Viewer
======================================
Renders the experiment FSM as a visual graph showing
current state, completed steps, and valid transitions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QImage, QPainter, QColor

from .styles import COLORS

import subprocess
import tempfile
import os
import logging
logger = logging.getLogger(__name__)


class FSMViewer(QWidget):
    """
    Visual FSM state diagram viewer.
    
    Renders the experiment protocol graph using Graphviz,
    highlighting current state and completed transitions.
    Falls back to a text-based representation if Graphviz is not installed.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._graphviz_available = self._check_graphviz()
        self._current_dot = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🔀 FSM STATE DIAGRAM")
        title.setFont(QFont("Rajdhani", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        if not self._graphviz_available:
            warn = QLabel("⚠ Graphviz not installed")
            warn.setFont(QFont("Inter", 9))
            warn.setStyleSheet(f"color: {COLORS['accent_yellow']}; background: transparent;")
            header_layout.addWidget(warn)

        layout.addLayout(header_layout)

        # Graph display area
        self._graph_label = QLabel()
        self._graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._graph_label.setMinimumSize(300, 200)
        self._graph_label.setStyleSheet(f"""
            background-color: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border_subtle']};
            border-radius: 6px;
            padding: 8px;
        """)
        self._graph_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self._graph_label)

        # State info
        self._state_info = QLabel("Current: IDLE")
        self._state_info.setFont(QFont("JetBrains Mono", 10))
        self._state_info.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        layout.addWidget(self._state_info)

    def update_graph(self, dot_source: str, current_step: str = "", valid_next: list = None):
        """
        Update the FSM visualization.
        
        Args:
            dot_source: DOT format string for the graph
            current_step: Currently active step
            valid_next: List of valid next step IDs
        """
        self._current_dot = dot_source
        valid_next = valid_next or []

        if self._graphviz_available:
            self._render_graphviz(dot_source)
        else:
            self._render_text_fallback(current_step, valid_next)

        # Update state info
        next_str = ", ".join(valid_next) if valid_next else "none"
        self._state_info.setText(
            f"Current: {current_step}  |  Valid next: {next_str}"
        )

    def _render_graphviz(self, dot_source: str):
        """Render DOT source to an image using Graphviz."""
        try:
            # Write DOT to temp file
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.dot', delete=False
            ) as f:
                f.write(dot_source)
                dot_path = f.name

            # Render to PNG
            png_path = dot_path + '.png'
            result = subprocess.run(
                ['dot', '-Tpng', '-Gdpi=120', dot_path, '-o', png_path],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0 and os.path.exists(png_path):
                pixmap = QPixmap(png_path)
                if not pixmap.isNull():
                    # Scale to fit
                    scaled = pixmap.scaled(
                        self._graph_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self._graph_label.setPixmap(scaled)
            else:
                logger.warning(f"Graphviz render failed: {result.stderr}")
                self._graph_label.setText("Graph render failed")

            # Cleanup
            try:
                os.unlink(dot_path)
                if os.path.exists(png_path):
                    os.unlink(png_path)
            except OSError:
                pass

        except subprocess.TimeoutExpired:
            logger.warning("Graphviz render timed out")
            self._graph_label.setText("Graph render timed out")
        except Exception as e:
            logger.error(f"Graphviz render error: {e}")
            self._graph_label.setText(f"Render error: {e}")

    def _render_text_fallback(self, current_step: str, valid_next: list):
        """Render a text-based FSM representation."""
        steps = [
            "IDLE", "OPEN_OUTER_BOX",
            "IDENTIFY_RED_BOX", "PLACE_RED_BOX",
            "IDENTIFY_YELLOW_BOX", "PLACE_YELLOW_BOX",
            "CLOSE_OUTER_BOX", "EXPERIMENT_COMPLETE"
        ]

        lines = ['<div style="font-family: JetBrains Mono; font-size: 11px;">']
        for step in steps:
            if step == current_step:
                color = COLORS["isro_orange"]
                marker = "▶"
            elif step in valid_next:
                color = COLORS["accent_cyan"]
                marker = "○"
            else:
                color = COLORS["text_dim"]
                marker = "·"

            lines.append(
                f'<span style="color: {color}">{marker} {step}</span><br>'
            )
        lines.append('</div>')

        self._graph_label.setText('\n'.join(lines))

    @staticmethod
    def _check_graphviz() -> bool:
        """Check if Graphviz is installed."""
        try:
            result = subprocess.run(
                ['dot', '-V'],
                capture_output=True, text=True, timeout=3
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
