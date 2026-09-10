"""
GUI Layer — Main Window
========================
ISRO Mission Control styled main window with professional
command center layout. Three-column design with telemetry.

Layout:
+================================================================+
|  ISRO  |  BASGUARD - BAS EXPERIMENT MONITOR  |  START  RESET   |
+================================================================+
|                    |  EXPERIMENT PROGRESS      | TELEMETRY      |
|   LIVE VIDEO       |  [1]--[2]--[3]--[4]--[5] | Confidence     |
|   FEED             |                           | Graph          |
|                    +---------------------------+                |
|                    |  ALERTS                   |                |
|                    |  [C] OUT_OF_SEQ  11:30    |                |
+--------------------+---------------------------+----------------+
|  EVENT LOG                                                      |
|  [00:15] [OK] OPEN_OUTER_BOX — Step completed                  |
+=================================================================+
| REC 02:15  FPS: 24  CPU: 45%  MEM: 2.1G   Pipeline: ACTIVE    |
+=================================================================+
"""

import sys
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QFrame, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient

from .styles import COLORS, FONTS, get_main_stylesheet, get_panel_title_style
from .video_panel import VideoPanel
from .timeline_panel import TimelinePanel
from .alert_panel import AlertPanel
from .log_panel import LogPanel
from .health_panel import HealthPanel
from .metrics_panel import MetricsGraphPanel

import logging
logger = logging.getLogger(__name__)


class SectionFrame(QFrame):
    """A styled panel frame with optional title bar accent."""

    def __init__(self, accent_color: str = None, parent=None):
        super().__init__(parent)
        border = accent_color or COLORS["border_subtle"]
        self.setStyleSheet(f"""
            SectionFrame {{
                background-color: {COLORS["bg_panel"]};
                border: 1px solid {border};
                border-radius: 4px;
            }}
        """)


class MainWindow(QMainWindow):
    """
    ISRO Mission Control — Main Application Window.

    Professional three-column dashboard that assembles all panels
    into a unified monitoring interface.
    """

    # Signals for thread-safe GUI updates
    update_frame_signal = pyqtSignal(object, object, object, object, str)
    update_alert_signal = pyqtSignal(str, str)
    update_log_signal = pyqtSignal(dict)
    update_timeline_signal = pyqtSignal(str, set, str, float)
    update_metrics_signal = pyqtSignal(float)

    def __init__(self, config: dict = None):
        super().__init__()
        self.config = config or {}
        self._pipeline_running = False

        self.setWindowTitle(
            self.config.get("gui", {}).get(
                "window_title",
                "BASGUARD — BAS Experiment Monitor"
            )
        )
        self.setMinimumSize(1366, 800)

        # Apply global stylesheet
        self.setStyleSheet(get_main_stylesheet())

        # Build UI
        self._build_ui()

        # Connect signals
        self.update_frame_signal.connect(self._on_update_frame)
        self.update_alert_signal.connect(self._on_update_alert)
        self.update_log_signal.connect(self._on_update_log)
        self.update_timeline_signal.connect(self._on_update_timeline)
        self.update_metrics_signal.connect(self._on_update_metrics)

        logger.info("MainWindow initialized")

    def _build_ui(self):
        """Build the complete dashboard UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header Bar ──────────────────────────────────────────
        header = self._build_header()
        main_layout.addWidget(header)

        # ── Main Content ────────────────────────────────────────
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(6, 6, 6, 4)
        content_layout.setSpacing(4)

        # Top row: Video | (Timeline + Alerts) | Telemetry
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.setHandleWidth(2)

        # ── LEFT: Video Feed ────────────────────────────────────
        video_frame = SectionFrame()
        video_inner = QVBoxLayout(video_frame)
        video_inner.setContentsMargins(4, 4, 4, 4)
        video_inner.setSpacing(2)

        video_title = QLabel("LIVE FEED")
        video_title.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        video_title.setStyleSheet(get_panel_title_style())
        video_inner.addWidget(video_title)

        self.video_panel = VideoPanel()
        video_inner.addWidget(self.video_panel, 1)
        top_splitter.addWidget(video_frame)

        # ── CENTER: Timeline + Alerts ───────────────────────────
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(4)

        # Timeline section
        timeline_frame = SectionFrame()
        timeline_inner = QVBoxLayout(timeline_frame)
        timeline_inner.setContentsMargins(4, 4, 4, 4)
        self.timeline_panel = TimelinePanel()
        timeline_inner.addWidget(self.timeline_panel)
        center_layout.addWidget(timeline_frame)

        # Alert section
        alert_frame = SectionFrame(accent_color=COLORS["accent_red"])
        alert_inner = QVBoxLayout(alert_frame)
        alert_inner.setContentsMargins(4, 4, 4, 4)
        self.alert_panel = AlertPanel()
        alert_inner.addWidget(self.alert_panel)
        center_layout.addWidget(alert_frame, 1)

        top_splitter.addWidget(center_widget)

        # ── RIGHT: Telemetry graph ──────────────────────────────
        telemetry_frame = SectionFrame(accent_color=COLORS["accent_cyan"])
        telemetry_inner = QVBoxLayout(telemetry_frame)
        telemetry_inner.setContentsMargins(4, 4, 4, 4)
        self.metrics_panel = MetricsGraphPanel()
        telemetry_inner.addWidget(self.metrics_panel)
        top_splitter.addWidget(telemetry_frame)

        top_splitter.setSizes([520, 440, 340])
        content_layout.addWidget(top_splitter, 1)

        # Bottom row: Log Panel (full-width)
        log_frame = SectionFrame()
        log_inner = QVBoxLayout(log_frame)
        log_inner.setContentsMargins(4, 4, 4, 4)
        self.log_panel = LogPanel()
        log_inner.addWidget(self.log_panel)
        content_layout.addWidget(log_frame, 0)

        main_layout.addWidget(content, 1)

        # ── Health Panel (Bottom Bar) ───────────────────────────
        self.health_panel = HealthPanel()
        main_layout.addWidget(self.health_panel)

    def _build_header(self) -> QFrame:
        """Build the ISRO-branded header bar."""
        header = QFrame()
        header.setFixedHeight(52)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_header']};
                border-bottom: 2px solid {COLORS['isro_orange']};
            }}
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # ISRO wordmark
        isro_label = QLabel("ISRO")
        isro_label.setFont(QFont("Rajdhani", 18, QFont.Weight.Bold))
        isro_label.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent;")
        layout.addWidget(isro_label)

        # Separator dot
        dot = QLabel("//")
        dot.setFont(QFont("JetBrains Mono", 12))
        dot.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")
        layout.addWidget(dot)

        # Title
        title = QLabel("BASGUARD")
        title.setFont(QFont("Rajdhani", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            background: transparent;
            letter-spacing: 3px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("BAS Experiment Monitor")
        subtitle.setFont(QFont("Inter", 10))
        subtitle.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")
        layout.addWidget(subtitle)

        layout.addStretch()

        # Mission clock
        self._clock_label = QLabel("T+ 00:00:00")
        self._clock_label.setFont(QFont("JetBrains Mono", 13, QFont.Weight.Bold))
        self._clock_label.setStyleSheet(f"color: {COLORS['accent_cyan']}; background: transparent;")
        layout.addWidget(self._clock_label)

        self._mission_start = None
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

        layout.addSpacing(16)

        # Action buttons
        self._start_btn = QPushButton("START")
        self._start_btn.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        self._start_btn.setFixedSize(110, 34)
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.clicked.connect(self._on_start_clicked)
        self._start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_green']};
                color: #0a0e1a;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: #00C853;
            }}
        """)
        layout.addWidget(self._start_btn)

        self._reset_btn = QPushButton("RESET")
        self._reset_btn.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        self._reset_btn.setFixedSize(90, 34)
        self._reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reset_btn.clicked.connect(self._on_reset_clicked)
        self._reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border_subtle']};
                border-radius: 4px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent_red']};
                color: {COLORS['accent_red']};
            }}
        """)
        layout.addWidget(self._reset_btn)

        return header

    # ── Clock ───────────────────────────────────────────────────

    def _update_clock(self):
        """Update mission elapsed time clock."""
        if self._mission_start and self._pipeline_running:
            elapsed = time.time() - self._mission_start
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            s = int(elapsed % 60)
            self._clock_label.setText(f"T+ {h:02d}:{m:02d}:{s:02d}")
            self._clock_label.setStyleSheet(
                f"color: {COLORS['accent_green']}; background: transparent;"
            )
        elif not self._pipeline_running:
            self._clock_label.setStyleSheet(
                f"color: {COLORS['text_dim']}; background: transparent;"
            )

    # ── Signal handlers (thread-safe GUI updates) ───────────────

    def _on_update_frame(self, frame, detections, hand_states, interactions, current_step):
        """Handle frame update signal."""
        self.video_panel.update_frame(
            frame, detections, hand_states, interactions, current_step
        )

    def _on_update_alert(self, severity, message):
        """Handle alert signal."""
        self.alert_panel.add_alert(severity, message)

    def _on_update_log(self, event):
        """Handle log event signal."""
        self.log_panel.append_log(event)

    def _on_update_timeline(self, current_step, completed, next_suggestion, progress):
        """Handle timeline update signal."""
        self.timeline_panel.update_state(
            current_step, completed, next_suggestion, progress
        )

    def _on_update_metrics(self, confidence):
        """Handle metrics update signal."""
        self.metrics_panel.update_metrics(confidence)

    # ── Button handlers ─────────────────────────────────────────

    def _on_start_clicked(self):
        """Handle Start/Stop button click."""
        if self._pipeline_running:
            self._pipeline_running = False
            self._start_btn.setText("START")
            self._start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_green']};
                    color: #0a0e1a;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                    letter-spacing: 2px;
                }}
                QPushButton:hover {{
                    background-color: #00C853;
                }}
            """)
            self.health_panel.update_pipeline_status("IDLE")
            logger.info("Pipeline stopped by user")
        else:
            self._pipeline_running = True
            self._mission_start = time.time()
            self._start_btn.setText("STOP")
            self._start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_red']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                    letter-spacing: 2px;
                }}
                QPushButton:hover {{
                    background-color: #D50000;
                }}
            """)
            self.health_panel.update_pipeline_status("ACTIVE")
            logger.info("Pipeline started by user")

    def _on_reset_clicked(self):
        """Handle Reset button click."""
        self._pipeline_running = False
        self._mission_start = None
        self._clock_label.setText("T+ 00:00:00")
        self._start_btn.setText("START")
        self._start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_green']};
                color: #0a0e1a;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: #00C853;
            }}
        """)
        self.alert_panel.clear_alerts()
        self.health_panel.update_pipeline_status("IDLE")
        self.video_panel.show_placeholder("System reset. Press START to begin.")
        logger.info("System reset by user")

    @property
    def is_pipeline_running(self) -> bool:
        return self._pipeline_running

    @is_pipeline_running.setter
    def is_pipeline_running(self, value: bool):
        self._pipeline_running = value
