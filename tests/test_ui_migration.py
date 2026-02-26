import sys
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
import pytest

@pytest.fixture
def app():
    # Only one QApplication can exist per process
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)
    yield qapp

def test_main_window_instantiation(app):
    """Test that MainWindow can be instantiated without crashing."""
    window = MainWindow()
    assert window is not None
    assert window.windowTitle() != ""
    window.close()

def test_window_blur_service_attribute():
    """Test that MainWindow has the WA_TranslucentBackground attribute set."""
    window = MainWindow()
    from PyQt6.QtCore import Qt
    assert window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    window.close()
