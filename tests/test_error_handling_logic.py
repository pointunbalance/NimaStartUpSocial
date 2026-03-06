import unittest
from unittest.mock import patch, MagicMock
from logic.browser_service import BrowserService
import subprocess

class TestErrorHandlingLogic(unittest.TestCase):
    @patch('subprocess.Popen')
    def test_browser_launch_failure_logging(self, mock_popen):
        # Force an error when Popen is called
        mock_popen.side_effect = Exception("Injected launch failure")
        
        # We need to mock logger to check if it's called
        with patch('utils.logger_service.logger.error') as mock_log_error:
            result = BrowserService.open_url("http://test.com", "chrome", {"chrome": "C:\\fake\\chrome.exe"})
            
            self.assertFalse(result)
            mock_log_error.assert_called()
            args, _ = mock_log_error.call_args
            self.assertIn("Injected launch failure", args[0])

    def test_missing_browser_path(self):
        # Should return False if browser key not in installed dict
        result = BrowserService.open_url("http://test.com", "opera", {"chrome": "C:\\fake\\chrome.exe"})
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
