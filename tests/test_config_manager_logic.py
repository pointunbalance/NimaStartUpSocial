import unittest
import json
import os
import shutil
from pathlib import Path
from database.config_manager import ConfigManager
from models.shortcut import Shortcut

class TestConfigManagerLogic(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for config tests
        self.test_dir = Path("temp_test_config")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.test_dir / "shortcuts.json"
        
        # Patch ConfigManager to use our test directory
        self.original_get_data_dir = ConfigManager.get_data_dir
        ConfigManager.get_data_dir = staticmethod(lambda: self.test_dir)
        
        # Ensure file doesn't exist at start
        if self.config_file.exists():
            self.config_file.unlink()

    def tearDown(self):
        # Restore original method
        ConfigManager.get_data_dir = self.original_get_data_dir
        # Cleanup temp directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_load_defaults_when_missing(self):
        shortcuts, browser = ConfigManager.load()
        self.assertTrue(len(shortcuts) > 0)
        self.assertEqual(browser, "default")
        self.assertTrue(self.config_file.exists())

    def test_save_and_load(self):
        test_shortcuts = [
            Shortcut("Test", "https://test.com", "chrome", "TestEN", "TestCat", "Ctrl+T", 5)
        ]
        ConfigManager.save(test_shortcuts, "firefox")
        
        loaded_shortcuts, loaded_browser = ConfigManager.load()
        self.assertEqual(loaded_browser, "firefox")
        self.assertEqual(len(loaded_shortcuts), 1)
        self.assertEqual(loaded_shortcuts[0].name, "Test")
        self.assertEqual(loaded_shortcuts[0].clicks, 5)

    def test_export_import(self):
        test_shortcuts = [
            Shortcut("ExportTest", "https://export.com", "default", "ExportEN", "ExportCat")
        ]
        export_path = self.test_dir / "exported.json"
        ConfigManager.export_shortcuts(export_path, test_shortcuts, "edge")
        
        imported_shortcuts, imported_browser = ConfigManager.import_shortcuts(export_path)
        self.assertEqual(imported_browser, "edge")
        self.assertEqual(len(imported_shortcuts), 1)
        self.assertEqual(imported_shortcuts[0].name, "ExportTest")

    def test_load_corrupt_json(self):
        self.config_file.write_text("{ invalid json }", encoding="utf-8")
        # Should fallback to defaults
        shortcuts, browser = ConfigManager.load()
        self.assertTrue(len(shortcuts) > 0)
        self.assertEqual(browser, "default")

if __name__ == "__main__":
    unittest.main()
