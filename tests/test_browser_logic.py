import unittest
from unittest.mock import patch
from logic.browser_service import BrowserService

class TestBrowserLogic(unittest.TestCase):
    @patch('os.path.exists')
    def test_detection_logic(self, mock_exists):
        # Clear cache to ensure fresh detection
        BrowserService.get_installed_browsers.cache_clear()
        
        # Simulate Chrome exists. convert path to str to avoid AttributeError with Path objects
        mock_exists.side_effect = lambda path: "chrome.exe" in str(path).lower()
        browsers = BrowserService.get_installed_browsers()
        
        # Check if chrome is detected
        self.assertIn("chrome", browsers)

    def test_open_url_default(self):
        with patch('webbrowser.open') as mock_open:
            BrowserService.open_url("https://test.com", "default", {})
            mock_open.assert_called_with("https://test.com")

if __name__ == "__main__":
    unittest.main()
