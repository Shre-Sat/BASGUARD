"""
GUI Layer — Alert Panel
========================
Color-coded alert history with severity indicators,
timestamps, and acknowledgement controls.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont

from .styles import COLORS, get_alert_style

import time
import logging
logger = logging.getLogger(__name__)


class AlertItem(QFrame):
    """A single alert entry in the alert panel."""

    SEVERITY_CONFIG = {
        "critical": {"icon": "[C]", "color": COLORS["accent_red"], "label": "CRITICAL"},
        "warning":  {"icon": "[W]", "color": COLORS["accent_yellow"], "label": "WARNING"},
        "info":     {"icon": "[I]", "color": COLORS["accent_green"], "label": "INFO"},
        "suggestion": {"icon": "[S]", "color": COLORS["accent_blue"], "label": "SUGGEST"},
    }

    def __init__(self, severity: str, message: str, timestamp: float = None, parent=None):
        super().__init__(parent)
        self.severity = severity
        self.message = message
        self.timestamp = timestamp or time.time()
        self._acknowledged = False
        self._setup_ui()

    def _setup_ui(self):
        config = self.SEVERITY_CONFIG.get(self.severity, self.SEVERITY_CONFIG["info"])

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-left: 3px solid {config['color']};
                border-radius: 4px;
                padding: 4px;
                margin: 2px 0;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        # Severity icon
        icon_label = QLabel(config["icon"])
        icon_label.setFont(QFont("JetBrains Mono", 11, QFont.Weight.Bold))
        icon_label.setStyleSheet(f"color: {config['color']}; background: transparent;")
        layout.addWidget(icon_label)

        # Content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        # Header: severity + timestamp
        header_layout = QHBoxLayout()
        severity_label = QLabel(config["label"])
        severity_label.setFont(QFont("Rajdhani", 10, QFont.Weight.Bold))
        severity_label.setStyleSheet(f"color: {config['color']}; background: transparent;")
        header_layout.addWidget(severity_label)

        header_layout.addStretch()

        time_str = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        time_label = QLabel(time_str)
        time_label.setFont(QFont("JetBrains Mono", 9))
        time_label.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")
        header_layout.addWidget(time_label)

        content_layout.addLayout(header_layout)

        # Message
        msg_label = QLabel(self.message)
        msg_label.setFont(QFont("Inter", 11))
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        content_layout.addWidget(msg_label)

        layout.addLayout(content_layout, 1)


class AlertPanel(QWidget):
    """
    Scrollable alert history panel with color-coded severity.
    
    Displays alerts in reverse chronological order (newest first).
    Supports severity: critical, warning, info, suggestion.
    """

    MAX_ALERTS = 100  # Maximum alerts to keep in history

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
        title.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent; letter-spacing: 1px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._count_label = QLabel("0 alerts")
        self._count_label.setFont(QFont("JetBrains Mono", 10))
        self._count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        header_layout.addWidget(self._count_label)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedSize(60, 26)
        clear_btn.setFont(QFont("Inter", 9))
        clear_btn.clicked.connect(self.clear_alerts)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Scrollable alert list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_subtle']};
                border-radius: 6px;
            }}
        """)

        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setContentsMargins(4, 4, 4, 4)
        self._scroll_layout.setSpacing(4)
        self._scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._scroll.setWidget(self._scroll_content)

        layout.addWidget(self._scroll)

        # No alerts placeholder
        self._placeholder = QLabel("No alerts yet")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet(f"""
            color: {COLORS['text_dim']};
            font-style: italic;
            padding: 20px;
            background: transparent;
        """)
        self._scroll_layout.addWidget(self._placeholder)

    def add_alert(self, severity: str, message: str, timestamp: float = None):
        """
        Add a new alert to the panel.
        
        Args:
            severity: "critical", "warning", "info", or "suggestion"
            message: Alert message text
            timestamp: Optional timestamp (defaults to now)
        """
        # Remove placeholder if present
        if self._placeholder.isVisible():
            self._placeholder.hide()

        # Create alert item
        alert_item = AlertItem(severity, message, timestamp)
        self._alerts.insert(0, alert_item)

        # Insert at top of scroll layout
        self._scroll_layout.insertWidget(0, alert_item)

        # Trim old alerts
        while len(self._alerts) > self.MAX_ALERTS:
            old = self._alerts.pop()
            self._scroll_layout.removeWidget(old)
            old.deleteLater()

        # Update count
        self._count_label.setText(f"{len(self._alerts)} alerts")

        # Scroll to top
        self._scroll.verticalScrollBar().setValue(0)

    def clear_alerts(self):
        """Clear all alerts."""
        for alert in self._alerts:
            self._scroll_layout.removeWidget(alert)
            alert.deleteLater()
        self._alerts.clear()
        self._count_label.setText("0 alerts")
        self._placeholder.show()

    @property
    def alert_count(self) -> int:
        return len(self._alerts)
