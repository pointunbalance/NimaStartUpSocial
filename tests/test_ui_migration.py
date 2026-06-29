import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
import pytest

@pytest.fixture
def app():
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

def test_window_blur_service_attribute(app):
    """Test that MainWindow has the WA_TranslucentBackground attribute set."""
    window = MainWindow()
    assert window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    window.close()
