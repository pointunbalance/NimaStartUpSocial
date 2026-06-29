import sys
from pathlib import Path


def _get_app_dir() -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


APP_DIR = _get_app_dir()
ASSETS_DIR = APP_DIR / "assets"


def get_icon(name: str):
    """
    Load an icon from the assets folder.
    Supports .ico and .png.
    Returns QIcon or None if not found.
    """
    try:
        from PyQt6.QtWidgets import QApplication
        if QApplication.instance() is None:
            return None

        from PyQt6.QtGui import QIcon
        extensions = [".ico", ".png", ".svg"]
        for ext in extensions:
            path = ASSETS_DIR / f"{name}{ext}"
            if path.exists():
                icon = QIcon(str(path))
                if not icon.isNull():
                    return icon
    except Exception:
        pass
    return None


def get_app_icon():
    """
    Helper to get the main application icon.
    """
    icon = get_icon("app_icon")
    if icon is None:
        from PyQt6.QtGui import QIcon
        return QIcon()
    return icon
