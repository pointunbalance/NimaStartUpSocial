import sys
from pathlib import Path
from PyQt6.QtGui import QIcon

# Handle PyInstaller's _MEIPASS for one-file bundles
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    APP_DIR = Path(sys._MEIPASS)
else:
    APP_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = APP_DIR / "assets"

def get_icon(name: str) -> QIcon:
    """
    Load an icon from the assets folder.
    Supports .ico and .png.
    """
    extensions = [".ico", ".png", ".svg"]
    for ext in extensions:
        path = ASSETS_DIR / f"{name}{ext}"
        if path.exists():
            icon = QIcon(str(path))
            if not icon.isNull():
                return icon
    return QIcon()

def get_app_icon() -> QIcon:
    """
    Helper to get the main application icon.
    """
    return get_icon("app_icon")
