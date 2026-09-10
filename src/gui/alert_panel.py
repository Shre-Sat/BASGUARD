"""
GUI Layer — Alert Panel
========================
Command-center style alert history with color-coded severity,
timestamps, and clear indicators.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .styles import COLORS

import time
import logging
logger = logging.getLogger(__name__)


class AlertItem(QFrame):
    """A single alert entry in the alert panel."""

    SEVERITY_CONFIG = {
        "critical": {"icon": "[C]", "color": COLORS["accent_red"], "label": "CRIT"},
        "warning":  {"icon": "[W]", "color": COLORS["accent_yellow"], "label": "WARN"},
        "info":     {"icon": "[I]", "color": COLORS["accent_green"], "label": "INFO"},
        "suggestion": {"icon": "[S]", "color": COLORS["accent_blue"], "label": "SUGG"},
    }

    def __init__(self, severity: str, message: str, timestamp: float = None, parent=None):
        super().__init__(parent)
        self.severity = severity
        self.message = message
        self.timestamp = timestamp or time.time()
        self._setup_ui()

    def _setup_ui(self):
        config = self.SEVERITY_CONFIG.get(self.severity, self.SEVERITY_CONFIG["info"])

        # Raw telemetry aesthetic: transparent bg, sharp bottom border only
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {COLORS['border_subtle']};
                margin: 0;
                padding: 4px 0;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Header row: timestamp + severity block
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        time_str = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        time_label = QLabel(f"T+ {time_str}")
        time_label.setFont(QFont("JetBrains Mono", 8))
        time_label.setStyleSheet(f"color: {COLORS['text_dim']}; border: none;")
        header_layout.addWidget(time_label)
        
        header_layout.addStretch()

        severity_label = QLabel(f" {config['label']} ")
        severity_label.setFont(QFont("JetBrains Mono", 8, QFont.Weight.Bold))
        # Hard colored block for severity
        severity_label.setStyleSheet(f"""
            background-color: {config['color']};
            color: #060A13;
            border: none;
            border-radius: 0px;
        """)
        header_layout.addWidget(severity_label)

        layout.addLayout(header_layout)

        # Message - strict monospace
        msg_label = QLabel(self.message.upper())
        msg_label.setFont(QFont("JetBrains Mono", 9))
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none; letter-spacing: 1px;")
        layout.addWidget(msg_label)


class AlertPanel(QWidget):
    """
    Scrollable alert history panel with color-coded severity.
    Displays alerts in reverse chronological order (newest first).
    """

    MAX_ALERTS = 50

    def __init__(self, parent=None):
        super().__init__(parent)
        self._alerts: list = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("ALERTS")
        title.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent; letter-spacing: 2px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._count_label = QLabel("0 ALERTS")
        self._count_label.setFont(QFont("JetBrains Mono", 9))
        self._count_label.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")
        header_layout.addWidget(self._count_label)

        clear_btn = QPushButton("CLR")
        clear_btn.setFixedSize(40, 20)
        clear_btn.setFont(QFont("JetBrains Mono", 8))
        clear_btn.clicked.connect(self.clear_alerts)
        clear_btn.setStyleSheet(f"""
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
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Scrollable alert list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border_subtle']};
                border-radius: 4px;
            }}
        """)

        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll_layout.setSpacing(4)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._scroll_content)

        layout.addWidget(self._scroll, 1)

        # No alerts placeholder
        self._placeholder = QLabel("NO ALERTS")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setFont(QFont("JetBrains Mono", 10))
        self._placeholder.setStyleSheet(f"""
            color: {COLORS['text_dim']};
            padding: 20px;
            background: transparent;
        """)
        self._scroll_layout.addWidget(self._placeholder)

    def add_alert(self, severity: str, message: str, timestamp: float = None):
        """Add a new alert to the panel."""
        if self._placeholder.isVisible():
            self._placeholder.hide()

        alert_item = AlertItem(severity, message, timestamp)
        self._alerts.insert(0, alert_item)
        self._scroll_layout.insertWidget(0, alert_item)

        while len(self._alerts) > self.MAX_ALERTS:
            old = self._alerts.pop()
            self._scroll_layout.removeWidget(old)
            old.deleteLater()

        self._count_label.setText(f"{len(self._alerts)} ALERTS")
        self._scroll.verticalScrollBar().setValue(0)

    def clear_alerts(self):
        """Clear all alerts."""
        for alert in self._alerts:
            self._scroll_layout.removeWidget(alert)
            alert.deleteLater()
        self._alerts.clear()
        self._count_label.setText("0 ALERTS")
        self._placeholder.show()
