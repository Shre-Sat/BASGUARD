"""
GUI Layer — ISRO Mission Control Theme & Styles
=================================================
Professional dark space theme inspired by real ISRO/NASA
mission control centers. Scanline HUD aesthetic with
precision typography and telemetry colors.
"""

# ── ISRO Color Palette ──────────────────────────────────────────
COLORS = {
    # Backgrounds — deep layered darks
    "bg_primary":       "#060A13",    # Near-black deep space
    "bg_secondary":     "#0C1220",    # Dark panel surface
    "bg_panel":         "#0F1729",    # Panel body
    "bg_card":          "#141E33",    # Elevated card
    "bg_input":         "#0A1020",    # Input wells
    "bg_hover":         "#1A2744",    # Hover state
    "bg_header":        "#080E1A",    # Header bar

    # ISRO Brand Colors
    "isro_orange":      "#FF6B00",    # Primary ISRO saffron
    "isro_orange_dark": "#CC5500",    # Darker orange
    "isro_orange_glow": "#FF8C33",    # Orange glow
    "isro_orange_dim":  "rgba(255,107,0,0.15)",  # Subtle orange wash

    # Accent Colors — telemetry palette
    "accent_blue":      "#00B4D8",    # Telemetry blue
    "accent_cyan":      "#00E5FF",    # HUD cyan
    "accent_green":     "#00E676",    # Nominal / success
    "accent_yellow":    "#FFD600",    # Caution
    "accent_red":       "#FF1744",    # Critical / alert
    "accent_purple":    "#7C4DFF",    # Secondary accent

    # Text
    "text_primary":     "#E0E6F0",    # High contrast text
    "text_secondary":   "#7B8BA8",    # Muted labels
    "text_accent":      "#FF6B00",    # Orange text
    "text_dim":         "#3A4A64",    # Very dim / disabled

    # Borders
    "border_subtle":    "#1E2D45",    # Panel borders
    "border_active":    "#FF6B00",    # Active borders
    "border_glow":      "rgba(255,107,0,0.25)",  # Glow

    # Status
    "status_online":    "#00E676",
    "status_warning":   "#FFD600",
    "status_error":     "#FF1744",
    "status_offline":   "#3A4A64",

    # Scanline / grid
    "grid_line":        "#0F1F35",
    "scanline":         "rgba(0,229,255,0.03)",
}

# ── Font Configuration ──────────────────────────────────────────
FONTS = {
    "header": "Rajdhani, Orbitron, Segoe UI, sans-serif",
    "body": "Inter, Segoe UI, Roboto, sans-serif",
    "mono": "JetBrains Mono, Fira Code, Consolas, monospace",
    "size_title": "20px",
    "size_header": "14px",
    "size_body": "12px",
    "size_small": "10px",
    "size_tiny": "9px",
}


def get_main_stylesheet() -> str:
    """Generate the complete QSS stylesheet for the application."""
    return f"""
    /* ═══════════════════════════════════════════════════════════
       ISRO MISSION CONTROL — BASGUARD GLOBAL STYLES
       ═══════════════════════════════════════════════════════════ */

    /* ── Global Defaults ──────────────────────────────────────── */
    QWidget {{
        background-color: {COLORS["bg_primary"]};
        color: {COLORS["text_primary"]};
        font-family: {FONTS["body"]};
        font-size: {FONTS["size_body"]};
    }}

    QMainWindow {{
        background-color: {COLORS["bg_primary"]};
    }}

    /* ── Scroll Bars ──────────────────────────────────────────── */
    QScrollBar:vertical {{
        background: {COLORS["bg_secondary"]};
        width: 6px;
        margin: 0;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS["border_subtle"]};
        min-height: 30px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS["isro_orange"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {COLORS["bg_secondary"]};
        height: 6px;
        margin: 0;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS["border_subtle"]};
        min-width: 30px;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS["isro_orange"]};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ── Group Boxes (Panels) ─────────────────────────────────── */
    QGroupBox {{
        background-color: {COLORS["bg_panel"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 4px;
        margin-top: 14px;
        padding: 10px 6px 6px 6px;
        font-family: {FONTS["header"]};
        font-size: {FONTS["size_header"]};
        font-weight: bold;
        color: {COLORS["isro_orange"]};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 10px;
        background-color: {COLORS["bg_panel"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 3px;
        color: {COLORS["isro_orange"]};
    }}

    /* ── Labels ────────────────────────────────────────────────── */
    QLabel {{
        background-color: transparent;
        color: {COLORS["text_primary"]};
    }}

    /* ── Buttons ───────────────────────────────────────────────── */
    QPushButton {{
        background-color: {COLORS["bg_card"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: bold;
        font-family: {FONTS["header"]};
        min-height: 28px;
    }}
    QPushButton:hover {{
        background-color: {COLORS["isro_orange"]};
        border-color: {COLORS["isro_orange"]};
        color: white;
    }}
    QPushButton:pressed {{
        background-color: {COLORS["isro_orange_dark"]};
    }}
    QPushButton:disabled {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_dim"]};
        border-color: {COLORS["bg_secondary"]};
    }}

    /* ── Primary Action Button ─────────────────────────────────── */
    QPushButton#primaryButton {{
        background-color: {COLORS["isro_orange"]};
        color: white;
        border: none;
        font-size: 13px;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {COLORS["isro_orange_glow"]};
    }}

    /* ── Text Edit / Log Views ──────────────────────────────────── */
    QTextEdit, QPlainTextEdit {{
        background-color: {COLORS["bg_input"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 4px;
        padding: 6px;
        font-family: {FONTS["mono"]};
        font-size: {FONTS["size_small"]};
        selection-background-color: {COLORS["isro_orange"]};
    }}

    /* ── Progress Bar ──────────────────────────────────────────── */
    QProgressBar {{
        background-color: {COLORS["bg_secondary"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 3px;
        text-align: center;
        color: {COLORS["text_primary"]};
        font-weight: bold;
        font-family: {FONTS["mono"]};
        min-height: 16px;
        max-height: 16px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS["isro_orange_dark"]},
            stop:1 {COLORS["isro_orange"]});
        border-radius: 2px;
    }}

    /* ── Splitter ───────────────────────────────────────────────── */
    QSplitter::handle {{
        background: {COLORS["border_subtle"]};
        width: 1px;
        height: 1px;
    }}
    QSplitter::handle:hover {{
        background: {COLORS["isro_orange"]};
    }}

    /* ── Tab Widget ─────────────────────────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid {COLORS["border_subtle"]};
        background-color: {COLORS["bg_panel"]};
        border-radius: 4px;
    }}
    QTabBar::tab {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_secondary"]};
        border: 1px solid {COLORS["border_subtle"]};
        padding: 6px 14px;
        margin-right: 1px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-family: {FONTS["header"]};
    }}
    QTabBar::tab:selected {{
        background-color: {COLORS["bg_panel"]};
        color: {COLORS["isro_orange"]};
        border-bottom-color: {COLORS["bg_panel"]};
    }}
    QTabBar::tab:hover {{
        background-color: {COLORS["bg_hover"]};
        color: {COLORS["text_primary"]};
    }}

    /* ── Tool Tips ──────────────────────────────────────────────── */
    QToolTip {{
        background-color: {COLORS["bg_card"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["isro_orange"]};
        border-radius: 3px;
        padding: 4px 8px;
        font-size: {FONTS["size_small"]};
    }}

    /* ── Status Bar ─────────────────────────────────────────────── */
    QStatusBar {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_secondary"]};
        border-top: 1px solid {COLORS["border_subtle"]};
        font-family: {FONTS["mono"]};
        font-size: {FONTS["size_small"]};
    }}

    /* ── Menu Bar ───────────────────────────────────────────────── */
    QMenuBar {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_primary"]};
        border-bottom: 1px solid {COLORS["border_subtle"]};
    }}
    QMenuBar::item:selected {{
        background-color: {COLORS["isro_orange"]};
    }}
    """


def get_panel_frame_style(title_color: str = None) -> str:
    """Style for a panel frame with subtle border and background."""
    border = title_color or COLORS["border_subtle"]
    return f"""
    QFrame {{
        background-color: {COLORS["bg_panel"]};
        border: 1px solid {border};
        border-radius: 4px;
    }}
    """


def get_panel_title_style(color: str = None) -> str:
    """Style for panel section titles."""
    c = color or COLORS["isro_orange"]
    return f"color: {c}; background: transparent; letter-spacing: 2px;"


def get_alert_style(severity: str) -> str:
    """Get style for an alert based on severity."""
    color_map = {
        "critical": COLORS["accent_red"],
        "warning": COLORS["accent_yellow"],
        "info": COLORS["accent_green"],
        "suggestion": COLORS["accent_blue"],
    }
    color = color_map.get(severity, COLORS["text_secondary"])
    return f"""
    background-color: {COLORS["bg_card"]};
    border-left: 3px solid {color};
    border-radius: 3px;
    padding: 5px 8px;
    margin: 1px 0;
    """
