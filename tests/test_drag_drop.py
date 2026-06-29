import sys
import unittest
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from database.config_manager import ConfigManager


class TestDragDrop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_reorder_logic(self):
        window = MainWindow()
        initial_shortcuts = list(window.service.shortcuts)

        if len(initial_shortcuts) < 2:
            print("Skipping: Not enough shortcuts.")
            return

        src_url = initial_shortcuts[0].url

        window.service.reorder(0, 1)

        verified_shortcuts, _ = ConfigManager.load()
        self.assertEqual(verified_shortcuts[1].url, src_url)
        print("Test Passed: State reordered and persisted.")


if __name__ == "__main__":
    unittest.main()
