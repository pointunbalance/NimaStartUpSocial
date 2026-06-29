from typing import List, Optional
from models.shortcut import Shortcut
from logic.catalog_service import SiteCatalog
from database.config_manager import ConfigManager
from utils.constants import TITLE_MAX_LENGTH


class ShortcutService:

    def __init__(self):
        self.shortcuts: List[Shortcut] = []
        self.global_browser: str = "default"
        self.load()

    def load(self) -> None:
        self.shortcuts, self.global_browser = ConfigManager.load()

    def save(self) -> None:
        ConfigManager.save(self.shortcuts, self.global_browser)

    def add(self, url: str) -> Optional[Shortcut]:
        if self.find_by_url(url):
            return None
        info = SiteCatalog.find_by_url(url)
        if info:
            name, name_en = info[1], info[2]
        else:
            host = SiteCatalog.get_host(url)
            name = name_en = host or url[:30]
        shortcut = Shortcut(name=name, url=url, browser="default", name_en=name_en)
        self.shortcuts.append(shortcut)
        self.save()
        return shortcut

    def remove(self, index: int) -> None:
        if 0 <= index < len(self.shortcuts):
            self.shortcuts.pop(index)
            self.save()

    def update(self, index: int, **kwargs) -> None:
        if 0 <= index < len(self.shortcuts):
            s = self.shortcuts[index]
            for key, value in kwargs.items():
                if hasattr(s, key):
                    setattr(s, key, value)
            self.save()

    def reorder(self, src_idx: int, target_idx: int) -> bool:
        if 0 <= src_idx < len(self.shortcuts) and 0 <= target_idx < len(self.shortcuts) and src_idx != target_idx:
            item = self.shortcuts.pop(src_idx)
            self.shortcuts.insert(target_idx, item)
            self.save()
            return True
        return False

    def apply_edit(self, index: int, name: str, url: str, name_en: str, category: str, hotkey: str) -> None:
        if 0 <= index < len(self.shortcuts):
            n1, n2 = SiteCatalog.normalize(name, name_en, url)
            s = self.shortcuts[index]
            self.shortcuts[index] = Shortcut(
                n1, url, s.browser, n2,
                category or "General",
                hotkey,
                s.clicks
            )
            self.save()

    def increment_clicks(self, shortcut: Shortcut) -> None:
        shortcut.clicks += 1
        self.save()

    def find_by_url(self, url: str) -> Optional[Shortcut]:
        for s in self.shortcuts:
            if s.url == url:
                return s
        return None

    def update_title(self, url: str, title: str) -> bool:
        s = self.find_by_url(url)
        if s:
            host = SiteCatalog.get_host(url)
            if s.name == host:
                s.name = title[:TITLE_MAX_LENGTH] + ("..." if len(title) > TITLE_MAX_LENGTH else "")
                self.save()
                return True
        return False

    def filter(self, query: str = "", category: str = "") -> List[Shortcut]:
        result = sorted(self.shortcuts, key=lambda x: x.clicks, reverse=True)
        if query:
            q = query.lower()
            result = [s for s in result if q in s.name.lower() or q in s.name_en.lower() or q in s.url.lower()]
        if category:
            result = [s for s in result if s.category == category]
        return result

    def get_popular(self, limit: int = 10) -> List[Shortcut]:
        return [s for s in sorted(self.shortcuts, key=lambda x: x.clicks, reverse=True) if s.clicks > 0][:limit]

    def get_categories(self) -> List[str]:
        return sorted(set(s.category for s in self.shortcuts if s.category))

    def replace_all(self, new_shortcuts: List[Shortcut]) -> None:
        self.shortcuts = new_shortcuts
        self.save()
