import os
import platform
import sys
from pathlib import Path

class PathUtils:
    APP_NAME = "NimaStartupSocial"

    @staticmethod
    def get_app_dir() -> Path:
        """
        Get the base application directory.
        Handles PyInstaller's _MEIPASS for one-file bundles.
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def get_data_dir() -> Path:
        """
        Get the user data directory (AppData/Library/Config).
        """
        system = platform.system().lower()
        if system == "windows":
            base = Path(os.environ.get("APPDATA", str(Path.home())))
        elif system == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".config"
        
        data_dir = base / PathUtils.APP_NAME
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @staticmethod
    def get_logs_dir() -> Path:
        """
        Get the directory for log files.
        """
        logs_dir = PathUtils.get_data_dir() / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    @staticmethod
    def get_backups_dir() -> Path:
        """
        Get the directory for database backups.
        """
        backups_dir = PathUtils.get_data_dir() / "backups"
        backups_dir.mkdir(parents=True, exist_ok=True)
        return backups_dir
