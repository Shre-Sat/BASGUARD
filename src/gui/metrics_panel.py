"""
GUI Layer — Real-time Metrics Graph Panel
===========================================
Live scrolling telemetry graph for model confidence
using pyqtgraph with mission-control HUD styling.
"""

import pyqtgraph as pg
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .styles import COLORS

import logging
logger = logging.getLogger(__name__)


class MetricsGraphPanel(QWidget):
    """
    Live scrolling telemetry plot.
    Shows Model Confidence over time with a glowing trace.
    """

    MAX_DATAPOINTS = 120

    def __init__(self, parent=None):
        super().__init__(parent)
        self._confidence_data = np.zeros(self.MAX_DATAPOINTS)
        self._time_data = np.arange(-self.MAX_DATAPOINTS, 0, 1)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("TELEMETRY")
        title.setFont(QFont("Rajdhani", 11, QFont.Weight.Bold))
        title.setStyleSheet(
            f"color: {COLORS['isro_orange']}; background: transparent; letter-spacing: 2px;"
        )
        header_layout.addWidget(title)

        header_layout.addStretch()

        self._latest_label = QLabel("CONF: --%")
        self._latest_label.setFont(QFont("JetBrains Mono", 10, QFont.Weight.Bold))
        self._latest_label.setStyleSheet(
            f"color: {COLORS['accent_cyan']}; background: transparent;"
        )
        header_layout.addWidget(self._latest_label)

        layout.addLayout(header_layout)

        # Threshold label row
        thresh_row = QHBoxLayout()
        thresh_row.addStretch()
        thresh_label = QLabel("THRESHOLD 0.60")
        thresh_label.setFont(QFont("JetBrains Mono", 8))
        thresh_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; background: transparent;"
        )
        thresh_row.addWidget(thresh_label)
        layout.addLayout(thresh_row)

        # Plot Widget
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(COLORS["bg_input"])
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('bottom')

        # Style axes
        self.plot_widget.getAxis('left').setPen(COLORS["border_subtle"])
        self.plot_widget.getAxis('left').setTextPen(COLORS["text_dim"])
        self.plot_widget.getAxis('left').setWidth(30)

        self.plot_widget.setYRange(0, 1.05, padding=0)

        # Threshold line
        threshold_line = pg.InfiniteLine(
            pos=0.6, angle=0,
            pen=pg.mkPen(color=COLORS['accent_yellow'], width=1, style=Qt.PenStyle.DashLine)
        )
        self.plot_widget.addItem(threshold_line)

        # Main trace curve
        pen = pg.mkPen(color=COLORS['accent_cyan'], width=2)
        self.curve = self.plot_widget.plot(
            self._time_data, self._confidence_data, pen=pen
        )

        # Fill under curve
        brush = pg.mkBrush(color=(0, 229, 255, 20))
        self.fill = pg.FillBetweenItem(
            curve1=self.curve,
            curve2=pg.PlotCurveItem(self._time_data, np.zeros(self.MAX_DATAPOINTS)),
            brush=brush
        )
        self.plot_widget.addItem(self.fill)

        # Grid
        self.plot_widget.showGrid(x=False, y=True, alpha=0.15)

        self.plot_widget.setStyleSheet(f"""
            border: 1px solid {COLORS['border_subtle']};
            border-radius: 4px;
        """)

        layout.addWidget(self.plot_widget, 1)

    def update_metrics(self, confidence: float):
        """Update the plot with a new confidence metric (0.0 to 1.0)."""
        self._confidence_data[:-1] = self._confidence_data[1:]
        self._confidence_data[-1] = confidence

        self.curve.setData(self._time_data, self._confidence_data)

        # Recreate fill
        self.plot_widget.removeItem(self.fill)
        brush = pg.mkBrush(color=(0, 229, 255, 20))
        self.fill = pg.FillBetweenItem(
            curve1=self.curve,
            curve2=pg.PlotCurveItem(self._time_data, np.zeros(self.MAX_DATAPOINTS)),
            brush=brush
        )
        self.plot_widget.addItem(self.fill)

        # Update label with color coding
        pct = int(confidence * 100)
        if confidence >= 0.6:
            color = COLORS['accent_green']
        elif confidence >= 0.4:
            color = COLORS['accent_yellow']
        else:
            color = COLORS['accent_red']
        self._latest_label.setText(f"CONF: {pct}%")
        self._latest_label.setStyleSheet(f"color: {color}; background: transparent;")
