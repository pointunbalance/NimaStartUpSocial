import unittest
import sys
from PyQt6.QtWidgets import QApplication
from ui.shortcuts_dialog import ShortcutsDialog
from logic.catalog_service import Shortcut

class TestShortcutsDialogLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_dialog_initialization(self):
        # Testing logic without full exec_() loop
        dialog = ShortcutsDialog(shortcuts=[])
        self.assertIsNotNone(dialog.name_input)
        self.assertEqual(dialog.name_input.text(), "")
        
    def test_load_shortcut_data(self):
        dialog = ShortcutsDialog(shortcuts=[])
        s = Shortcut("TestName", "https://test.com", "chrome", "TestEN", "Social", "Ctrl+S")
        
        # Manually trigger the pick logic (which loads data into inputs)
        # We simulate adding it and picking it
        dialog.shortcuts = [s]
        dialog._refresh(0)
        dialog._on_pick(0)
        
        self.assertEqual(dialog.name_input.text(), "TestName")
        self.assertEqual(dialog.url_input.text(), "https://test.com")

if __name__ == "__main__":
    unittest.main()
