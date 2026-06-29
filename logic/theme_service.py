"""
ThemeService - Manages light/dark/custom themes for the application.
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

THEMES = {
    "dark": {
        "name": "داكن",
        "bg_primary": "rgba(15, 23, 42, 230)",
        "bg_secondary": "rgba(255, 255, 255, 10)",
        "bg_card": "rgba(255, 255, 255, 25)",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "accent": "#0d9488",
        "accent_hover": "#0f766e",
        "border": "rgba(255, 255, 255, 20)",
        "border_hover": "rgba(13, 148, 136, 150)",
        "blur_color": QColor(15, 23, 42, 220),
    },
    "light": {
        "name": "فاتح",
        "bg_primary": "rgba(255, 255, 255, 240)",
        "bg_secondary": "rgba(255, 255, 255, 100)",
        "bg_card": "rgba(255, 255, 255, 60)",
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "accent": "#0d9488",
        "accent_hover": "#0f766e",
        "border": "rgba(203, 213, 225, 80)",
        "border_hover": "rgba(13, 148, 136, 150)",
        "blur_color": QColor(255, 255, 255, 40),
    },
    "midnight": {
        "name": "منتصف الليل",
        "bg_primary": "rgba(0, 0, 0, 240)",
        "bg_secondary": "rgba(255, 255, 255, 5)",
        "bg_card": "rgba(255, 255, 255, 10)",
        "text_primary": "#e2e8f0",
        "text_secondary": "#64748b",
        "accent": "#8b5cf6",
        "accent_hover": "#7c3aed",
        "border": "rgba(255, 255, 255, 10)",
        "border_hover": "rgba(139, 92, 246, 150)",
        "blur_color": QColor(0, 0, 0, 230),
    },
    "ocean": {
        "name": "محيط",
        "bg_primary": "rgba(15, 23, 42, 220)",
        "bg_secondary": "rgba(59, 130, 246, 15)",
        "bg_card": "rgba(59, 130, 246, 20)",
        "text_primary": "#e0f2fe",
        "text_secondary": "#7dd3fc",
        "accent": "#0ea5e9",
        "accent_hover": "#0284c7",
        "border": "rgba(59, 130, 246, 30)",
        "border_hover": "rgba(14, 165, 233, 150)",
        "blur_color": QColor(15, 23, 42, 220),
    },
}


class ThemeService:
    _current_theme = "dark"

    @classmethod
    def get_theme(cls, name: str = None) -> dict:
        if name is None:
            name = cls._current_theme
        return THEMES.get(name, THEMES["dark"])

    @classmethod
    def set_theme(cls, name: str):
        if name in THEMES:
            cls._current_theme = name

    @classmethod
    def get_theme_names(cls) -> list:
        return list(THEMES.keys())

    @classmethod
    def get_theme_display_names(cls) -> list:
        return [t["name"] for t in THEMES.values()]

    @classmethod
    def get_qss(cls, name: str = None) -> str:
        t = cls.get_theme(name)
        return f"""
            QWidget#launcherContainer {{
                background-color: {t['bg_primary']};
                border: 1px solid {t['border']};
                border-radius: 20px;
            }}
            QLabel {{
                color: {t['text_primary']};
                background: transparent;
            }}
            QLineEdit {{
                background: {t['bg_secondary']};
                color: {t['text_primary']};
                border: 1px solid {t['border']};
                border-radius: 10px;
                padding: 8px 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {t['border_hover']};
                background: {t['bg_secondary']};
            }}
            QTabBar::tab {{
                background: {t['bg_secondary']};
                border: 1px solid {t['border']};
                border-radius: 8px;
                padding: 6px 10px;
                margin: 2px;
                color: {t['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background: {t['accent']};
                color: #ffffff;
                border-color: {t['accent']};
            }}
        """
