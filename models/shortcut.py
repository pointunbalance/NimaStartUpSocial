from dataclasses import dataclass


@dataclass
class Shortcut:
    name: str
    url: str
    browser: str = "default"
    name_en: str = ""
    category: str = "General"
    hotkey: str = ""
    clicks: int = 0
