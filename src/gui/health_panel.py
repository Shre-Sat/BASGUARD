"""
GUI Layer — System Health Panel (Bottom Telemetry Bar)
=======================================================
Real-time system metrics: FPS, CPU, Memory, Latency,
Recording status, and Pipeline state.
"""

import psutil
import time
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from .styles import COLORS

import logging
logger = logging.getLogger(__name__)


class MetricChip(QFrame):
    """Compact inline metric chip: LABEL value."""

    def __init__(self, label: str, unit: str = "", parent=None):
        super().__init__(parent)
        self.unit = unit
        self._setup_ui(label)

    def _setup_ui(self, label: str):
        self.setStyleSheet(f"""
            MetricChip {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border_subtle']};
                border-radius: 3px;
                padding: 2px 6px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(4)

        self._label = QLabel(label)
        self._label.setFont(QFont("Rajdhani", 9, QFont.Weight.Bold))
        self._label.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent; border: none;")
        layout.addWidget(self._label)

        self._value = QLabel("--")
        self._value.setFont(QFont("JetBrains Mono", 11, QFont.Weight.Bold))
        self._value.setStyleSheet(f"color: {COLORS['accent_cyan']}; background: transparent; border: none;")
        layout.addWidget(self._value)

    def set_value(self, value: str, color: str = None):
        """Update the displayed value."""
        display = f"{value}{self.unit}" if self.unit else value
        self._value.setText(display)
        if color:
            self._value.setStyleSheet(f"color: {color}; background: transparent; border: none;")


class HealthPanel(QWidget):
    """
    System health bar at the very bottom of the GUI.
    Shows: Recording, FPS, Latency, CPU%, Memory, Storage, Pipeline.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

        # Auto-refresh system metrics every 2 seconds
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_system_metrics)
        self._refresh_timer.start(2000)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(6)

        # Recording indicator (dot + text)
        self._status_dot = QFrame()
        self._status_dot.setFixedSize(10, 10)
        self._status_dot.setStyleSheet(
            f"background-color: {COLORS['status_offline']}; border-radius: 5px;"
        )
        layout.addWidget(self._status_dot)

        self._status_text = QLabel("STANDBY")
        self._status_text.setFont(QFont("JetBrains Mono", 10, QFont.Weight.Bold))
        self._status_text.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")
        layout.addWidget(self._status_text)

        self._add_separator(layout)

        # Metrics
        self._fps_chip = MetricChip("FPS")
        layout.addWidget(self._fps_chip)

        self._latency_chip = MetricChip("LAT", "ms")
        layout.addWidget(self._latency_chip)

        self._cpu_chip = MetricChip("CPU", "%")
        layout.addWidget(self._cpu_chip)

        self._mem_chip = MetricChip("MEM")
        layout.addWidget(self._mem_chip)

        self._storage_chip = MetricChip("DISK")
        layout.addWidget(self._storage_chip)

        self._add_separator(layout)

        # Pipeline status
        self._pipeline_label = QLabel("PIPELINE: --")
        self._pipeline_label.setFont(QFont("Rajdhani", 10, QFont.Weight.Bold))
        self._pipeline_label.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent; letter-spacing: 1px;")
        layout.addWidget(self._pipeline_label)

        layout.addStretch()

        # Branding
        branding = QLabel("BASGUARD v1.0")
        branding.setFont(QFont("Rajdhani", 9, QFont.Weight.Bold))
        branding.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent; letter-spacing: 1px;")
        layout.addWidget(branding)

        self.setStyleSheet(f"""
            HealthPanel {{
                background-color: {COLORS['bg_header']};
                border-top: 1px solid {COLORS['border_subtle']};
            }}
        """)
        self.setFixedHeight(40)

    def _add_separator(self, layout):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedHeight(20)
        sep.setStyleSheet(f"color: {COLORS['border_subtle']};")
        layout.addWidget(sep)

    def update_fps(self, fps: float):
        """Update the FPS metric."""
        color = COLORS["accent_green"] if fps >= 20 else (
            COLORS["accent_yellow"] if fps >= 10 else COLORS["accent_red"]
        )
        self._fps_chip.set_value(f"{fps:.0f}", color)

    def update_latency(self, latency_ms: float):
        """Update the inference latency metric."""
        color = COLORS["accent_green"] if latency_ms < 50 else (
            COLORS["accent_yellow"] if latency_ms < 100 else COLORS["accent_red"]
        )
        self._latency_chip.set_value(f"{latency_ms:.0f}", color)

    def update_recording_status(self, is_recording: bool, duration: float = 0):
        """Update recording indicator."""
        if is_recording:
            self._status_dot.setStyleSheet(
                f"background-color: {COLORS['accent_red']}; border-radius: 5px;"
            )
            mins = int(duration // 60)
            secs = int(duration % 60)
            self._status_text.setText(f"REC {mins:02d}:{secs:02d}")
            self._status_text.setStyleSheet(f"color: {COLORS['accent_red']}; background: transparent;")
        else:
            self._status_dot.setStyleSheet(
                f"background-color: {COLORS['status_offline']}; border-radius: 5px;"
            )
            self._status_text.setText("STANDBY")
            self._status_text.setStyleSheet(f"color: {COLORS['text_dim']}; background: transparent;")

    def update_pipeline_status(self, status: str):
        """Update pipeline status label."""
        color_map = {
            "ACTIVE": COLORS["accent_green"],
            "IDLE": COLORS["text_dim"],
            "ERROR": COLORS["accent_red"],
            "LOADING": COLORS["accent_yellow"],
        }
        color = color_map.get(status, COLORS["text_dim"])
        self._pipeline_label.setText(f"PIPELINE: {status}")
        self._pipeline_label.setStyleSheet(f"color: {color}; background: transparent; letter-spacing: 1px;")

    def _refresh_system_metrics(self):
        """Refresh CPU, memory, and storage metrics."""
        try:
            cpu_pct = psutil.cpu_percent(interval=None)
            cpu_color = COLORS["accent_green"] if cpu_pct < 60 else (
                COLORS["accent_yellow"] if cpu_pct < 85 else COLORS["accent_red"]
            )
            self._cpu_chip.set_value(f"{cpu_pct:.0f}", cpu_color)

            mem = psutil.virtual_memory()
            mem_gb = mem.used / (1024 ** 3)
            mem_color = COLORS["accent_green"] if mem.percent < 60 else (
                COLORS["accent_yellow"] if mem.percent < 85 else COLORS["accent_red"]
            )
            self._mem_chip.set_value(f"{mem_gb:.1f}G", mem_color)

            disk = psutil.disk_usage('/')
            disk_free_gb = disk.free / (1024 ** 3)
            disk_color = COLORS["accent_green"] if disk.percent < 80 else (
                COLORS["accent_yellow"] if disk.percent < 90 else COLORS["accent_red"]
            )
            self._storage_chip.set_value(f"{disk_free_gb:.0f}G", disk_color)

        except Exception as e:
            logger.debug(f"Error refreshing system metrics: {e}")
