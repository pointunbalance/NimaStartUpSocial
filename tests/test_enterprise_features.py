"""
Verification script for Enterprise Features:
- System Tray logic
- Search Filter logic
- Async Title Fetching
"""
import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from ui.main_window import MainWindow


class TestEnterpriseFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_search_filter(self):
        window = MainWindow()
        # Mock initial state with known shortcuts
        window.shortcuts = [
            type('S', (), {'name': 'Google', 'name_en': 'Google', 'url': 'http://google.com', 'clicks': 0, 'category': 'General', 'hotkey': '', 'browser': 'default'})(),
            type('S', (), {'name': 'GitHub', 'name_en': 'GitHub', 'url': 'http://github.com', 'clicks': 0, 'category': 'General', 'hotkey': '', 'browser': 'default'})(),
            type('S', (), {'name': 'ChatGPT', 'name_en': 'ChatGPT', 'url': 'http://chatgpt.com', 'clicks': 0, 'category': 'General', 'hotkey': '', 'browser': 'default'})()
        ]
        
        # Filter for "Git"
        window._on_search_changed("Git")
        visible_items = [s for s in window.shortcuts if not window.filter_query or window.filter_query in f"{s.name} {s.name_en} {s.url}".lower()]
        self.assertEqual(len(visible_items), 1)
        self.assertEqual(visible_items[0].name, "GitHub")
        print("Success: Search filter logic verified.")

    def test_title_fetcher(self):
        from ui.main_window import TitleFetcher
        # Note: This requires internet access. If blocked, this might fail or timeout.
        fetcher = TitleFetcher("https://www.google.com")
        
        received_title = []
        def on_finished(url, title):
            received_title.append(title)
        
        fetcher.finished.connect(on_finished)
        fetcher.start()
        
        # Wait for thread to finish (max 10s)
        for _ in range(100):
            QApplication.processEvents()
            if received_title:
                break
            import time; time.sleep(0.1)
            
        self.assertTrue(len(received_title) > 0, "Title should be fetched")
        self.assertIn("Google", received_title[0])
        print(f"Success: Title fetcher verified. Fetched: {received_title[0]}")

    def test_tray_logic(self):
        # Verify tray is initialized
        window = MainWindow()
        self.assertIsNotNone(window.tray)
        self.assertTrue(window.tray.isVisible())
        print("Success: System Tray initialization verified.")

    def test_global_browser_selection(self):
        window = MainWindow()
        # Initial state (should load from config, default if not changed)
        self.assertEqual(window.global_browser, "default")
        
        # Change state
        idx = window.browser_combo.findData("chrome")
        if idx != -1:
            window.browser_combo.setCurrentIndex(idx)
            self.assertEqual(window.global_browser, "chrome")
            print("Success: Global browser selection logic verified.")
        else:
            print("Skipping Chrome test: Chrome not detected on system.")


if __name__ == "__main__":
    unittest.main()
