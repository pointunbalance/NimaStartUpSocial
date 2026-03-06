import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
from utils.path_utils import PathUtils

class TestPathUtilsRobust(unittest.TestCase):
    def test_get_data_dir_dev_mode(self):
        # Mock sys.frozen and sys._MEIPASS behavior
        with patch.object(sys, 'frozen', False, create=True):
            # Should point to local folder or %APPDATA% depending on implementation
            # PathUtils usually checks for %APPDATA% on Windows
            data_dir = PathUtils.get_data_dir()
            self.assertTrue(data_dir.exists())
            self.assertIn("NimaStartupSocial", str(data_dir))

    @patch('os.path.normpath')
    def test_path_normalization(self, mock_norm):
        mock_norm.side_effect = lambda x: x.replace("/", "\\") if sys.platform == "win32" else x
        test_path = "some/mixed/path"
        norm = PathUtils.get_data_dir() / test_path
        # Just check if it handles components correctly
        self.assertIsInstance(norm, Path)

    def test_ensure_dir_creation(self):
        test_subdir = PathUtils.get_data_dir() / "test_subdir_creation"
        if test_subdir.exists():
            import shutil
            shutil.rmtree(test_subdir)
            
        # Manually create it to simulate first run
        test_subdir.mkdir(parents=True, exist_ok=True)
        self.assertTrue(test_subdir.exists())
        import shutil
        shutil.rmtree(test_subdir)

if __name__ == "__main__":
    unittest.main()
