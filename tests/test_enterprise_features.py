"""
Verification script for Enterprise Features:
- System Tray logic
- Search Filter logic
- Async Title Fetching
"""
import sys
import time
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from models.shortcut import Shortcut


class TestEnterpriseFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_search_filter(self):
        window = MainWindow()
        window.service.shortcuts = [
            Shortcut("جوجل", "http://google.com", "default", "Google", "General"),
            Shortcut("جيت هب", "http://github.com", "default", "GitHub", "General"),
            Shortcut("شات جي بي تي", "http://chatgpt.com", "default", "ChatGPT", "General"),
        ]
        
        window.filter_query = "git"
        visible_items = window.service.filter(window.filter_query)
        self.assertEqual(len(visible_items), 1)
        self.assertEqual(visible_items[0].name_en, "GitHub")

    def test_title_fetcher(self):
        from logic.title_service import TitleFetcher
        fetcher = TitleFetcher("https://www.google.com")
        
        received_title = []
        def on_finished(url, title):
            received_title.append(title)
        
        fetcher.finished.connect(on_finished)
        fetcher.start()
        
        for _ in range(100):
            QApplication.processEvents()
            if received_title:
                break
            time.sleep(0.1)
            
        self.assertTrue(len(received_title) > 0, "Title should be fetched")
        self.assertIn("Google", received_title[0])

    def test_tray_logic(self):
        window = MainWindow()
        self.assertIsNotNone(window.tray)
        self.assertTrue(window.tray.isVisible())

    def test_global_browser_selection(self):
        window = MainWindow()
        initial = window.service.global_browser
        
        idx = window.browser_combo.findData("chrome")
        if idx != -1:
            window.browser_combo.setCurrentIndex(idx)
            self.assertEqual(window.service.global_browser, "chrome")


if __name__ == "__main__":
    unittest.main()
