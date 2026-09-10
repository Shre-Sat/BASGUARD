"""
GUI Layer — ISRO Mission Control Theme & Styles
=================================================
Centralized dark space theme inspired by ISRO mission control.
QSS (Qt Style Sheets) for the entire application.
"""

# ── ISRO Color Palette ──────────────────────────────────────────
COLORS = {
    # Backgrounds
    "bg_primary":       "#0a0e1a",    # Deep space navy
    "bg_secondary":     "#111827",    # Dark panel background
    "bg_panel":         "#1a1f35",    # Panel background
    "bg_card":          "#1e2442",    # Card/widget background
    "bg_input":         "#0f1629",    # Input field background
    "bg_hover":         "#252d4a",    # Hover state

    # ISRO Brand Colors
    "isro_orange":      "#FF6B00",    # Primary ISRO orange
    "isro_orange_dark": "#CC5500",    # Darker orange for hover
    "isro_orange_glow": "#FF8C33",    # Orange glow

    # Accent Colors
    "accent_blue":      "#00B4D8",    # Mission blue
    "accent_cyan":      "#00E5FF",    # Bright cyan
    "accent_green":     "#00E676",    # Success green
    "accent_yellow":    "#FFD600",    # Warning yellow
    "accent_red":       "#FF1744",    # Error/alert red
    "accent_purple":    "#7C4DFF",    # Purple accent

    # Text
    "text_primary":     "#E8ECF4",    # Primary text
    "text_secondary":   "#8892B0",    # Secondary/muted text
    "text_accent":      "#FF6B00",    # Accent text (orange)
    "text_dim":         "#4A5568",    # Very dim text

    # Borders
    "border_subtle":    "#2D3748",    # Subtle border
    "border_active":    "#FF6B00",    # Active/focused border
    "border_glow":      "rgba(255, 107, 0, 0.3)",  # Orange glow border

    # Status
    "status_online":    "#00E676",
    "status_warning":   "#FFD600",
    "status_error":     "#FF1744",
    "status_offline":   "#4A5568",
}

# ── Font Configuration ──────────────────────────────────────────
FONTS = {
    "header": "Rajdhani, Orbitron, Segoe UI, sans-serif",
    "body": "Inter, Segoe UI, Roboto, sans-serif",
    "mono": "JetBrains Mono, Fira Code, Consolas, monospace",
    "size_title": "22px",
    "size_header": "16px",
    "size_body": "13px",
    "size_small": "11px",
    "size_tiny": "9px",
}


def get_main_stylesheet() -> str:
    """Generate the complete QSS stylesheet for the application."""
    return f"""
    /* ═══════════════════════════════════════════════════════════
       ISRO MISSION CONTROL — GLOBAL STYLES
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
        width: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS["border_subtle"]};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS["isro_orange"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {COLORS["bg_secondary"]};
        height: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS["border_subtle"]};
        min-width: 30px;
        border-radius: 4px;
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
        border-radius: 8px;
        margin-top: 14px;
        padding: 12px 8px 8px 8px;
        font-family: {FONTS["header"]};
        font-size: {FONTS["size_header"]};
        font-weight: bold;
        color: {COLORS["isro_orange"]};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 12px;
        background-color: {COLORS["bg_panel"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 4px;
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
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-family: {FONTS["header"]};
        min-height: 32px;
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
        font-size: 14px;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {COLORS["isro_orange_glow"]};
    }}

    /* ── Text Edit / Log Views ──────────────────────────────────── */
    QTextEdit, QPlainTextEdit {{
        background-color: {COLORS["bg_input"]};
        color: {COLORS["text_primary"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 6px;
        padding: 8px;
        font-family: {FONTS["mono"]};
        font-size: {FONTS["size_small"]};
        selection-background-color: {COLORS["isro_orange"]};
    }}

    /* ── Progress Bar ──────────────────────────────────────────── */
    QProgressBar {{
        background-color: {COLORS["bg_secondary"]};
        border: 1px solid {COLORS["border_subtle"]};
        border-radius: 6px;
        text-align: center;
        color: {COLORS["text_primary"]};
        font-weight: bold;
        min-height: 20px;
    }}
    QProgressBar::chunk {{
        background-color: {COLORS["isro_orange"]};
        border-radius: 5px;
    }}

    /* ── Splitter ───────────────────────────────────────────────── */
    QSplitter::handle {{
        background: {COLORS["border_subtle"]};
        width: 2px;
        height: 2px;
    }}
    QSplitter::handle:hover {{
        background: {COLORS["isro_orange"]};
    }}

    /* ── Tab Widget ─────────────────────────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid {COLORS["border_subtle"]};
        background-color: {COLORS["bg_panel"]};
        border-radius: 6px;
    }}
    QTabBar::tab {{
        background-color: {COLORS["bg_secondary"]};
        color: {COLORS["text_secondary"]};
        border: 1px solid {COLORS["border_subtle"]};
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
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
        border-radius: 4px;
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


def get_header_style() -> str:
    """Style for the header bar."""
    return f"""
    background-color: {COLORS["bg_secondary"]};
    border-bottom: 2px solid {COLORS["isro_orange"]};
    padding: 8px 16px;
    """


def get_panel_style(accent_color: str = None) -> str:
    """Style for content panels."""
    border_color = accent_color or COLORS["border_subtle"]
    return f"""
    background-color: {COLORS["bg_panel"]};
    border: 1px solid {border_color};
    border-radius: 8px;
    padding: 8px;
    """


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
    border-radius: 4px;
    padding: 6px 10px;
    margin: 2px 0;
    """


def get_status_dot_style(status: str) -> str:
    """Get style for a status indicator dot."""
    color_map = {
        "online": COLORS["status_online"],
        "recording": COLORS["accent_red"],
        "warning": COLORS["status_warning"],
        "error": COLORS["status_error"],
        "offline": COLORS["status_offline"],
    }
    color = color_map.get(status, COLORS["status_offline"])
    return f"""
    background-color: {color};
    border-radius: 5px;
    min-width: 10px;
    max-width: 10px;
    min-height: 10px;
    max-height: 10px;
    """
