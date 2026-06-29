"""
FaviconService - Automatically fetches favicons for websites.
"""
import requests
from pathlib import Path
from urllib.parse import urlparse
from logic.catalog_service import SiteCatalog
from utils.path_utils import PathUtils
from utils.logger_service import logger


class FaviconService:
    _cache_dir = None

    @classmethod
    def get_cache_dir(cls) -> Path:
        if cls._cache_dir is None:
            cls._cache_dir = PathUtils.get_data_dir() / "favicons"
            cls._cache_dir.mkdir(parents=True, exist_ok=True)
        return cls._cache_dir

    @classmethod
    def get_favicon_path(cls, url: str) -> Path:
        host = SiteCatalog.get_host(url)
        safe_name = host.replace(".", "_").replace("/", "_")
        return cls.get_cache_dir() / f"{safe_name}.ico"

    @classmethod
    def fetch_favicon(cls, url: str) -> Path:
        cache_path = cls.get_favicon_path(url)
        if cache_path.exists():
            return cache_path

        host = SiteCatalog.get_host(url)
        favicon_urls = [
            f"https://{host}/favicon.ico",
            f"https://www.google.com/s2/favicons?domain={host}&sz=64",
        ]

        for favicon_url in favicon_urls:
            try:
                response = requests.get(favicon_url, timeout=5, stream=True)
                if response.status_code == 200 and len(response.content) > 0:
                    cache_path.write_bytes(response.content)
                    logger.debug(f"Favicon cached for {host}")
                    return cache_path
            except Exception as e:
                logger.debug(f"Failed to fetch favicon from {favicon_url}: {e}")
                continue

        return None

    @classmethod
    def get_favicon(cls, url: str) -> Path:
        cache_path = cls.get_favicon_path(url)
        if cache_path.exists():
            return cache_path
        return cls.fetch_favicon(url)

    @classmethod
    def clear_cache(cls):
        cache_dir = cls.get_cache_dir()
        if cache_dir.exists():
            for f in cache_dir.iterdir():
                try:
                    f.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete favicon cache: {e}")
