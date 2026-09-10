"""
GUI Layer — Log Viewer Panel
==============================
Live-tailing structured log viewer with summary generation.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat

from .styles import COLORS

import json
import logging
logger = logging.getLogger(__name__)


class LogPanel(QWidget):
    """
    Live-tailing log viewer showing experiment events.
    
    Features:
    - Auto-scrolling log display with syntax highlighting
    - Generate Summary Report button
    - Export log functionality
    """

    MAX_LOG_LINES = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self._log_lines = 0
        self._logger_ref = None  # Reference to ExperimentLogger
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("EVENT LOG")
        title.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent; letter-spacing: 1px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._line_count_label = QLabel("0 events")
        self._line_count_label.setFont(QFont("JetBrains Mono", 10))
        self._line_count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        header_layout.addWidget(self._line_count_label)

        layout.addLayout(header_layout)

        # Log text area
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFont(QFont("JetBrains Mono", 10))
        self._log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_subtle']};
                border-radius: 6px;
                padding: 8px;
                selection-background-color: {COLORS['isro_orange']};
            }}
        """)
        layout.addWidget(self._log_text)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self._summary_btn = QPushButton("GENERATE SUMMARY")
        self._summary_btn.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        self._summary_btn.setObjectName("primaryButton")
        self._summary_btn.clicked.connect(self._generate_summary)
        btn_layout.addWidget(self._summary_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setFont(QFont("Inter", 10))
        self._clear_btn.clicked.connect(self._clear_log)
        btn_layout.addWidget(self._clear_btn)

        layout.addLayout(btn_layout)

    def set_logger(self, experiment_logger):
        """Set reference to the ExperimentLogger for summary generation."""
        self._logger_ref = experiment_logger

    def append_log(self, event: dict):
        """
        Append a log event to the viewer.
        
        Args:
            event: Dictionary with event data (timestamp, step_id, status, etc.)
        """
        self._log_lines += 1

        # Format the log line with color coding
        timestamp = event.get("elapsed_seconds", 0)
        step_id = event.get("step_id", "?")
        status = event.get("status", "?")
        confidence = event.get("confidence", 0)
        message = event.get("message", "")

        # Choose color based on status
        color_map = {
            "COMPLETED": COLORS["accent_green"],
            "step_completed": COLORS["accent_green"],
            "experiment_complete": COLORS["accent_cyan"],
            "experiment_started": COLORS["accent_cyan"],
            "STARTED": COLORS["accent_blue"],
            "SKIPPED": COLORS["accent_red"],
            "skipped_step": COLORS["accent_red"],
            "OUT_OF_SEQUENCE": COLORS["accent_red"],
            "out_of_sequence": COLORS["accent_red"],
            "uncertain": COLORS["accent_yellow"],
            "ERROR": COLORS["accent_red"],
            "next_step_suggestion": COLORS["text_secondary"],
        }
        color = color_map.get(status, COLORS["text_primary"])

        # Format time as MM:SS
        mins = int(timestamp // 60)
        secs = int(timestamp % 60)
        time_str = f"{mins:02d}:{secs:02d}"

        # Status icon
        icon_map = {
            "COMPLETED": "[OK]",
            "step_completed": "[OK]",
            "experiment_complete": "[DONE]",
            "experiment_started": "[START]",
            "STARTED": "[>>]",
            "SKIPPED": "[SKIP]",
            "skipped_step": "[SKIP]",
            "OUT_OF_SEQUENCE": "[ERR]",
            "out_of_sequence": "[ERR]",
            "uncertain": "[?]",
            "next_step_suggestion": "[NEXT]",
        }
        icon = icon_map.get(status, "[-]")

        line = f'<span style="color: {COLORS["text_dim"]}">[{time_str}]</span> '
        line += f'<span style="color: {color}">{icon} {step_id}</span> '
        if message:
            line += f'<span style="color: {COLORS["text_secondary"]}">— {message}</span>'
        if confidence > 0:
            line += f' <span style="color: {COLORS["text_dim"]}">({confidence:.0%})</span>'

        self._log_text.append(line)

        # Auto-scroll to bottom
        cursor = self._log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._log_text.setTextCursor(cursor)

        # Update count
        self._line_count_label.setText(f"{self._log_lines} events")

        # Trim old lines
        if self._log_lines > self.MAX_LOG_LINES:
            cursor = self._log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(
                QTextCursor.MoveOperation.Down,
                QTextCursor.MoveMode.KeepAnchor,
                self._log_lines - self.MAX_LOG_LINES
            )
            cursor.removeSelectedText()

    def _generate_summary(self):
        """Generate and display the summary report."""
        if self._logger_ref is None:
            self._log_text.append(
                f'<span style="color: {COLORS["accent_yellow"]}">'
                f'⚠ No logger connected. Cannot generate summary.</span>'
            )
            return

        try:
            summary = self._logger_ref.generate_summary()
            # Show summary in a separator
            self._log_text.append(f'<br><span style="color: {COLORS["accent_cyan"]}">')
            for line in summary.split('\n'):
                self._log_text.append(f'{line}')
            self._log_text.append('</span><br>')

            # Auto-scroll
            cursor = self._log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self._log_text.setTextCursor(cursor)

        except Exception as e:
            self._log_text.append(
                f'<span style="color: {COLORS["accent_red"]}">Error: {e}</span>'
            )

    def _clear_log(self):
        """Clear the log display."""
        self._log_text.clear()
        self._log_lines = 0
        self._line_count_label.setText("0 events")
