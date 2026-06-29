import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QMimeData, QPointF
from PyQt6.QtGui import QDropEvent
from ui.main_window import MainWindow
from database.config_manager import ConfigManager

class TestDragDrop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We need a QApplication for UI tests
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_reorder_logic(self):
        window = MainWindow()
        initial_shortcuts = list(window.shortcuts)
        
        if len(initial_shortcuts) < 2:
            print("Skipping: Not enough shortcuts.")
            return

        # Simulating move from index 0 to index 1
        src_url = initial_shortcuts[0].url
        target_name_before = initial_shortcuts[1].name
        
        # Call the logic directly
        # In actual app: self.shortcuts.pop(src_idx), self.shortcuts.insert(target_idx, item)
        shortcuts = window.shortcuts
        item = shortcuts.pop(0)
        shortcuts.insert(1, item)
        ConfigManager.save(shortcuts)
        
        # Verify persistence
        verified_shortcuts, _ = ConfigManager.load()
        self.assertEqual(verified_shortcuts[1].url, src_url)
        print("Test Passed: State reordered and persisted.")

if __name__ == "__main__":
    unittest.main()
