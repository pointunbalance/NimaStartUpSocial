from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Shortcut:
    name: str
    url: str
    browser: str = "default"
    name_en: str = ""
    category: str = "General"
    hotkey: str = ""
    clicks: int = 0
    last_opened: str = ""

    def mark_opened(self):
        self.last_opened = datetime.now().isoformat()
