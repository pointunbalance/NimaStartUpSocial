import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from pathlib import Path

def test_boot():
    app = QApplication(sys.argv)
    
    # Load Styles
    qss_path = Path("assets/styles.qss")
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        print("Styles loaded.")
    
    try:
        window = MainWindow()
        print("MainWindow instantiated successfully.")
        # We don't show it here to avoid hanging
        return True
    except Exception as e:
        print(f"Error during instantiation: {e}")
        return False

if __name__ == "__main__":
    if test_boot():
        sys.exit(0)
    else:
        sys.exit(1)
