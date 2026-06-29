import sys
import pytest
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.widgets.shortcut_card import ShortcutCard


@pytest.fixture
def app():
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)
    yield qapp


def _wait(ms):
    import time
    end = time.time() + ms / 1000.0
    while time.time() < end:
        QApplication.processEvents()
        time.sleep(0.005)


def test_ui_reorder_simulation(app):
    window = MainWindow()
    window.show()
    _wait(400)

    if len(window.service.shortcuts) < 2:
        window.close()
        pytest.skip("Not enough shortcuts")

    assert window.grid_layout.count() > 0, "Grid should have widgets"

    source_card = window.grid_layout.itemAt(0).widget()
    source_url = source_card.shortcut.url

    target_card = window.grid_layout.itemAt(1).widget()
    target_url_before = target_card.shortcut.url

    src_idx = next((i for i, s in enumerate(window.service.shortcuts) if s.url == source_url), -1)
    target_idx = next((i for i, s in enumerate(window.service.shortcuts) if s.url == target_url_before), -1)

    assert src_idx != -1, "Source should be found in shortcuts"
    assert target_idx != -1, "Target should be found in shortcuts"

    window.service.reorder(src_idx, target_idx)
    window._refresh_grid(animate=False)
    _wait(200)

    assert window.grid_layout.count() > 0, "Grid should have widgets after reorder"
    assert window.service.shortcuts[target_idx].url == source_url, "Source shortcut should be at target index"

    for i in range(window.grid_layout.count()):
        widget = window.grid_layout.itemAt(i).widget()
        assert isinstance(widget, ShortcutCard), f"Grid item {i} should be ShortcutCard"
        assert widget.isVisible(), f"Card {i} should be visible"

    window.close()
