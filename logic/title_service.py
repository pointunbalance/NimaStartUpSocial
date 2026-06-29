from PyQt6.QtCore import QThread, pyqtSignal


class TitleFetcher(QThread):
    finished = pyqtSignal(str, str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            import requests
            from bs4 import BeautifulSoup
            from utils.logger_service import logger

            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(self.url, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = (soup.title.string or "").strip() if soup.title else ""
                if title:
                    self.finished.emit(self.url, title)
        except Exception as e:
            logger.debug(f"Title fetch failed for {self.url}: {e}")
