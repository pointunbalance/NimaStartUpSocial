import json
from typing import Optional, Tuple
from urllib.parse import urlparse
from pathlib import Path


class SiteCatalog:
    _KNOWN = None

    @classmethod
    def _load(cls):
        if cls._KNOWN is None:
            catalog_path = Path(__file__).parent.parent / "data" / "catalog.json"
            cls._KNOWN = json.loads(catalog_path.read_text(encoding="utf-8"))
        return cls._KNOWN

    @staticmethod
    def get_host(url: str) -> str:
        host = urlparse(url.strip()).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host

    @classmethod
    def find_by_url(cls, url: str) -> Optional[Tuple[str, str, str, str, str, str]]:
        host = SiteCatalog.get_host(url)
        for entry in cls._load():
            domain = entry["domain"]
            if host == domain or host.endswith(f".{domain}"):
                return domain, entry["ar"], entry["en"], entry["icon"], entry["color"], entry["fa"]
        return None

    @classmethod
    def normalize(cls, name: str, name_en: str, url: str) -> Tuple[str, str]:
        name = name.strip()
        name_en = name_en.strip()
        item = cls.find_by_url(url)
        if item:
            _, ar, en, _, _, _ = item
            if name == en:
                name = ar
            if not name_en:
                name_en = en
        if not name_en:
            name_en = name
        return name, name_en

    @classmethod
    def get_icon_meta(cls, shortcut) -> Tuple[str, str, Optional[str]]:
        if "id=61585982617699" in shortcut.url:
            return "", "#ffffff", "APP_ICON"
        item = cls.find_by_url(shortcut.url)
        if item:
            return item[3], item[4], item[5]
        host = cls.get_host(shortcut.url).replace(".", "")
        letters = "".join(ch for ch in host.upper() if ch.isalnum())[:2]
        return (letters or "WB"), "#0F766E", "fa5s.globe"
