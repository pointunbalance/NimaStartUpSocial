"""
Automated UI-level drag-and-drop test.
Simulates a drop event and verifies widget reordering and visibility.
"""
import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QMimeData, QPointF, QTimer
from PyQt6.QtGui import QDropEvent
from ui.main_window import MainWindow
from ui.widgets.shortcut_card import ShortcutCard


class TestUIDragDrop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_ui_reorder_simulation(self):
        window = MainWindow()
        window.show()
        
        # Process events to allow deferred grid refresh (QTimer.singleShot(300))
        for _ in range(50):
            QApplication.processEvents()
            import time; time.sleep(0.01)
        
        if len(window.shortcuts) < 2:
            print("Skipping: Not enough shortcuts")
            return

        # Verify grid has widgets
        self.assertGreater(window.grid_layout.count(), 0, "Grid should have widgets")

        source_card = window.grid_layout.itemAt(0).widget()
        source_url = source_card.shortcut.url
        
        target_card = window.grid_layout.itemAt(1).widget()
        target_pos = target_card.mapTo(window.grid_widget, target_card.rect().center())
        
        # Simulate Drop Event
        mime = QMimeData()
        mime.setText(source_url)
        
        drop_event = QDropEvent(
            QPointF(target_pos),
            Qt.DropAction.MoveAction,
            mime,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        
        window._grid_drop(drop_event)
        
        # Process events for deferred refresh
        for _ in range(20):
            QApplication.processEvents()
            import time; time.sleep(0.01)
            
        new_second_card = window.grid_layout.itemAt(1).widget()
        
        self.assertEqual(new_second_card.shortcut.url, source_url, "Source card should be at target index")
        self.assertTrue(new_second_card.isVisible(), "Card should be visible after drop")
        
        print("Success: UI-level reordering verified and icons are visible.")
        window.close()


if __name__ == "__main__":
    unittest.main()
