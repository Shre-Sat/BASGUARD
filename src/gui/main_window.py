"""
GUI Layer — Main Window
========================
ISRO Mission Control styled main window that assembles all panels
into a unified monitoring dashboard.

Layout:
┌──────────────────────────────────────────────────────────────────┐
│  🇮🇳  ISRO BAS EXPERIMENT MONITOR              [Start] [Reset]  │
├────────────────────────────────┬─────────────────────────────────┤
│                                │  EXPERIMENT PROGRESS            │
│   LIVE VIDEO FEED              │  [1]✓ ─── [2]● ─── [3] ───    │
│   (annotated with detections,  ├─────────────────────────────────┤
│    hand landmarks,             │  FSM STATE DIAGRAM              │
│    interaction states)         │  ┌────┐   ┌────┐               │
│                                │  │IDLE│──▶│OPEN│──▶ ...        │
│                                │  └────┘   └────┘               │
├────────────────────────────────┼─────────────────────────────────┤
│  🔔 ALERTS                     │  📋 EVENT LOG                   │
│  ⚠ OUT_OF_SEQUENCE 11:30      │  [00:15] ✓ OPEN_OUTER_BOX      │
│  ✓ STEP_COMPLETED  11:29      │  [00:22] ✓ IDENTIFY_RED_BOX    │
├────────────────────────────────┴─────────────────────────────────┤
│  ● REC 02:15 │ FPS: 24 │ CPU: 45% │ MEM: 2.1G │ Pipeline: ACT │
└──────────────────────────────────────────────────────────────────┘
"""

import sys
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QFrame, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QAction

from .styles import COLORS, FONTS, get_main_stylesheet
from .video_panel import VideoPanel
from .timeline_panel import TimelinePanel
from .alert_panel import AlertPanel
from .log_panel import LogPanel
from .health_panel import HealthPanel
from .metrics_panel import MetricsGraphPanel

import logging
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    ISRO Mission Control — Main Application Window.
    
    Assembles all dashboard panels and manages the processing loop
    that connects the camera → perception → reasoning → GUI pipeline.
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
                "ISRO BAS Experiment Monitor — HAR System"
            )
        )
        self.setMinimumSize(1280, 800)

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

        # ── Main Content Area ───────────────────────────────────
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        content_splitter.setHandleWidth(3)

        # Top section: Video + Timeline/FSM
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        top_splitter.setHandleWidth(3)

        # Left: Video Feed
        video_container = QWidget()
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(8, 8, 4, 4)
        self.video_panel = VideoPanel()
        video_layout.addWidget(self.video_panel)
        top_splitter.addWidget(video_container)

        # Right: Timeline + FSM
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(4, 8, 8, 4)
        right_layout.setSpacing(8)

        self.timeline_panel = TimelinePanel()
        right_layout.addWidget(self.timeline_panel)

        self.metrics_panel = MetricsGraphPanel()
        right_layout.addWidget(self.metrics_panel, 1)

        top_splitter.addWidget(right_container)
        top_splitter.setSizes([600, 400])

        content_splitter.addWidget(top_splitter)

        # Bottom section: Alerts + Log
        bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        bottom_splitter.setHandleWidth(3)

        # Left: Alert Panel
        alert_container = QWidget()
        alert_layout = QVBoxLayout(alert_container)
        alert_layout.setContentsMargins(8, 4, 4, 4)
        self.alert_panel = AlertPanel()
        alert_layout.addWidget(self.alert_panel)
        bottom_splitter.addWidget(alert_container)

        # Right: Log Panel
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(4, 4, 8, 4)
        self.log_panel = LogPanel()
        log_layout.addWidget(self.log_panel)
        bottom_splitter.addWidget(log_container)

        bottom_splitter.setSizes([400, 600])
        content_splitter.addWidget(bottom_splitter)
        content_splitter.setSizes([500, 300])

        main_layout.addWidget(content_splitter, 1)

        # ── Health Panel (Bottom Bar) ───────────────────────────
        self.health_panel = HealthPanel()
        main_layout.addWidget(self.health_panel)

    def _build_header(self) -> QFrame:
        """Build the ISRO-branded header bar."""
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 2px solid {COLORS['isro_orange']};
            }}
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # ISRO Logo / Flag
        flag_label = QLabel("ISRO")
        flag_label.setFont(QFont("Rajdhani", 16, QFont.Weight.Bold))
        flag_label.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent;")
        layout.addWidget(flag_label)

        # Title
        title = QLabel("BAS EXPERIMENT MONITOR")
        title.setFont(QFont("Rajdhani", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            background: transparent;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("AI-Based Human Activity Recognition System")
        subtitle.setFont(QFont("Inter", 10))
        subtitle.setStyleSheet(f"color: {COLORS['text_secondary']}; background: transparent;")
        layout.addWidget(subtitle)

        layout.addStretch()

        # Action buttons
        self._start_btn = QPushButton("START")
        self._start_btn.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        self._start_btn.setFixedSize(120, 36)
        self._start_btn.setObjectName("primaryButton")
        self._start_btn.clicked.connect(self._on_start_clicked)
        self._start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_green']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00C853;
            }}
        """)
        layout.addWidget(self._start_btn)

        self._reset_btn = QPushButton("RESET")
        self._reset_btn.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        self._reset_btn.setFixedSize(100, 36)
        self._reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addWidget(self._reset_btn)

        return header

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
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #00C853;
                }}
            """)
            self.health_panel.update_pipeline_status("IDLE")
            logger.info("Pipeline stopped by user")
        else:
            self._pipeline_running = True
            self._start_btn.setText("STOP")
            self._start_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_red']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
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
        self._start_btn.setText("START")
        self._start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_green']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
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
