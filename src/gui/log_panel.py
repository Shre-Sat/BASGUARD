"""
GUI Layer — Log Viewer Panel
==============================
Mission-control style event log with color-coded entries
and auto-scrolling terminal aesthetic.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor

import os
import time as _time

from .styles import COLORS

import logging
logger = logging.getLogger(__name__)


class LogPanel(QWidget):
    """
    Live-tailing log viewer showing experiment events.

    Features:
    - Auto-scrolling log with color-coded entries
    - Generate Summary Report button
    - Clear log functionality
    """

    MAX_LOG_LINES = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self._log_lines = 0
        self._logger_ref = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("EVENT LOG")
        title.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {COLORS['isro_orange']}; background: transparent; letter-spacing: 2px;"
        )
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._line_count_label = QLabel("0 EVENTS")
        self._line_count_label.setFont(QFont("JetBrains Mono", 9))
        self._line_count_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; background: transparent;"
        )
        header_layout.addWidget(self._line_count_label)

        # Summary button
        self._summary_btn = QPushButton("SUMMARY")
        self._summary_btn.setFont(QFont("JetBrains Mono", 8))
        self._summary_btn.setFixedHeight(20)
        self._summary_btn.clicked.connect(self._generate_summary)
        self._summary_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['isro_orange']};
                color: white;
                border: none;
                border-radius: 2px;
                padding: 0 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['isro_orange_glow']};
            }}
        """)
        header_layout.addWidget(self._summary_btn)

        # Export button
        self._export_btn = QPushButton("EXPORT")
        self._export_btn.setFont(QFont("JetBrains Mono", 8))
        self._export_btn.setFixedHeight(20)
        self._export_btn.clicked.connect(self._export_log)
        self._export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_cyan']};
                color: #060A13;
                border: none;
                border-radius: 2px;
                padding: 0 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #33ECFF;
            }}
        """)
        header_layout.addWidget(self._export_btn)

        # Clear button
        self._clear_btn = QPushButton("CLR")
        self._clear_btn.setFont(QFont("JetBrains Mono", 8))
        self._clear_btn.setFixedSize(36, 20)
        self._clear_btn.clicked.connect(self._clear_log)
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {COLORS['border_subtle']};
                color: {COLORS['text_secondary']};
                border-radius: 2px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_red']};
                color: {COLORS['accent_red']};
            }}
        """)
        header_layout.addWidget(self._clear_btn)

        layout.addLayout(header_layout)

        # Log text area
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setFont(QFont("JetBrains Mono", 9))
        self._log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_input']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_subtle']};
                border-radius: 4px;
                padding: 4px;
                selection-background-color: {COLORS['isro_orange']};
            }}
        """)
        self._log_text.setFixedHeight(120)
        layout.addWidget(self._log_text)

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

        timestamp = event.get("elapsed_seconds", 0)
        step_id = event.get("step_id", "?")
        status = event.get("status", "?")
        confidence = event.get("confidence", 0)
        message = event.get("message", "")

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
            "next_step_suggestion": COLORS["text_dim"],
        }
        color = color_map.get(status, COLORS["text_secondary"])

        mins = int(timestamp // 60)
        secs = int(timestamp % 60)
        time_str = f"{mins:02d}:{secs:02d}"

        icon_map = {
            "COMPLETED": "[OK]",
            "step_completed": "[OK]",
            "experiment_complete": "[DONE]",
            "experiment_started": "[>>]",
            "STARTED": "[>>]",
            "SKIPPED": "[SKIP]",
            "skipped_step": "[SKIP]",
            "OUT_OF_SEQUENCE": "[ERR]",
            "out_of_sequence": "[ERR]",
            "uncertain": "[??]",
            "next_step_suggestion": "[>>]",
        }
        icon = icon_map.get(status, "[-]")

        line = f'<span style="color: {COLORS["text_dim"]}">[{time_str}]</span> '
        line += f'<span style="color: {color}">{icon} {step_id}</span>'
        if message:
            line += f' <span style="color: {COLORS["text_secondary"]}">-- {message}</span>'
        if confidence > 0:
            line += f' <span style="color: {COLORS["text_dim"]}">({confidence:.0%})</span>'

        self._log_text.append(line)

        cursor = self._log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._log_text.setTextCursor(cursor)

        self._line_count_label.setText(f"{self._log_lines} EVENTS")

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
                f'[WARN] No logger connected. Cannot generate summary.</span>'
            )
            return

        try:
            summary = self._logger_ref.generate_summary()
            self._log_text.append(f'<br><span style="color: {COLORS["accent_cyan"]}">')
            for line in summary.split('\n'):
                self._log_text.append(f'{line}')
            self._log_text.append('</span><br>')

            cursor = self._log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self._log_text.setTextCursor(cursor)

        except Exception as e:
            self._log_text.append(
                f'<span style="color: {COLORS["accent_red"]}">[ERR] {e}</span>'
            )

    def _export_log(self):
        """Export the log to a text file via save dialog."""
        default_name = f"basguard_log_{_time.strftime('%Y%m%d_%H%M%S')}.log"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Event Log",
            os.path.expanduser(f"~/{default_name}"),
            "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )
        if not filepath:
            return

        try:
            plain_text = self._log_text.toPlainText()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"BASGUARD Event Log\n")
                f.write(f"Exported: {_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Events: {self._log_lines}\n")
                f.write("=" * 60 + "\n\n")
                f.write(plain_text)

            self._log_text.append(
                f'<span style="color: {COLORS["accent_green"]}">[OK] Log exported to {filepath}</span>'
            )
            logger.info(f"Log exported to {filepath}")
        except Exception as e:
            self._log_text.append(
                f'<span style="color: {COLORS["accent_red"]}">[ERR] Export failed: {e}</span>'
            )
            logger.error(f"Log export failed: {e}")

    def _clear_log(self):
        """Clear the log display."""
        self._log_text.clear()
        self._log_lines = 0
        self._line_count_label.setText("0 EVENTS")
