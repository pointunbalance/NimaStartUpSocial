"""
NimaStartupSocial - Enterprise Desktop Application
Main entry point with global error handling and logging.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from utils.logger_service import logger


def _global_exception_handler(exc_type, exc_value, exc_tb):
    """Global safety net: log unhandled exceptions instead of crashing silently."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))


def main():
    sys.excepthook = _global_exception_handler

    logger.info("Application starting...")
    app = QApplication(sys.argv)

    qss_path = Path(__file__).resolve().parent / "assets" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    from ui.launcher_screen import LauncherScreen
    launcher = LauncherScreen()
    launcher.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
