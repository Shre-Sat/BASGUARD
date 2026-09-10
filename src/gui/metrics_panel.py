"""
GUI Layer — Real-time Metrics Graph Panel
===========================================
Displays live graphs for inference confidence and pipeline metrics
using pyqtgraph for a professional telemetry look.
"""

import pyqtgraph as pg
import time
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from .styles import COLORS

import logging
logger = logging.getLogger(__name__)


class MetricsGraphPanel(QWidget):
    """
    Live scrolling telemetry plot.
    Shows Model Confidence over time.
    """
    
    MAX_DATAPOINTS = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self._confidence_data = np.zeros(self.MAX_DATAPOINTS)
        self._time_data = np.arange(-self.MAX_DATAPOINTS, 0, 1)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("TELEMETRY :: CONFIDENCE")
        title.setFont(QFont("Rajdhani", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['isro_orange']}; background: transparent; letter-spacing: 1px;")
        header_layout.addWidget(title)

        header_layout.addStretch()
        
        self._latest_label = QLabel("CONF: --%")
        self._latest_label.setFont(QFont("JetBrains Mono", 10))
        self._latest_label.setStyleSheet(f"color: {COLORS['accent_cyan']}; background: transparent;")
        header_layout.addWidget(self._latest_label)

        layout.addLayout(header_layout)

        # Plot Widget
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(COLORS["bg_secondary"])
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('bottom')
        
        # Style axes
        styles = {'color': COLORS['text_dim'], 'font-size': '10px'}
        self.plot_widget.getAxis('left').setPen(COLORS["border_subtle"])
        self.plot_widget.getAxis('left').setTextPen(COLORS["text_dim"])
        
        self.plot_widget.setYRange(0, 1.05, padding=0)

        # Main trace curve
        pen = pg.mkPen(color=COLORS['accent_cyan'], width=2)
        self.curve = self.plot_widget.plot(self._time_data, self._confidence_data, pen=pen)

        # Fill under curve
        brush = pg.mkBrush(color=(0, 229, 255, 30)) # Cyan with alpha
        self.fill = pg.FillBetweenItem(curve1=self.curve, curve2=pg.PlotCurveItem(self._time_data, np.zeros(self.MAX_DATAPOINTS)), brush=brush)
        self.plot_widget.addItem(self.fill)

        # Grid
        self.plot_widget.showGrid(x=False, y=True, alpha=0.3)

        self.plot_widget.setStyleSheet(f"""
            border: 1px solid {COLORS['border_subtle']};
            border-radius: 6px;
        """)

        layout.addWidget(self.plot_widget)

    def update_metrics(self, confidence: float):
        """Update the plot with a new confidence metric (0.0 to 1.0)."""
        # Shift data
        self._confidence_data[:-1] = self._confidence_data[1:]
        self._confidence_data[-1] = confidence

        # Update curve and fill
        self.curve.setData(self._time_data, self._confidence_data)
        
        # Re-create fill (pg workaround for updating fill)
        self.plot_widget.removeItem(self.fill)
        brush = pg.mkBrush(color=(0, 229, 255, 30))
        self.fill = pg.FillBetweenItem(curve1=self.curve, curve2=pg.PlotCurveItem(self._time_data, np.zeros(self.MAX_DATAPOINTS)), brush=brush)
        self.plot_widget.addItem(self.fill)

        # Update label
        self._latest_label.setText(f"CONF: {int(confidence * 100)}%")
