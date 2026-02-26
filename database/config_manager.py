import json
import os
import platform
from pathlib import Path
from typing import List
from dataclasses import asdict
from logic.catalog_service import Shortcut, SiteCatalog

class ConfigManager:
    APP_NAME = "NimaStartupSocial"

    @staticmethod
    def get_data_dir() -> Path:
        system = platform.system().lower()
        if system == "windows":
            return Path(os.environ.get("APPDATA", str(Path.home()))) / ConfigManager.APP_NAME
        if system == "darwin":
            return Path.home() / "Library" / "Application Support" / ConfigManager.APP_NAME
        return Path.home() / ".config" / ConfigManager.APP_NAME

    @staticmethod
    def get_config_file() -> Path:
        return ConfigManager.get_data_dir() / "shortcuts.json"

    @staticmethod
    def _ensure_dir() -> None:
        ConfigManager.get_data_dir().mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_defaults() -> List[Shortcut]:
        return [
            # AI Assistant Tools
            Shortcut("شات جي بي تي", "https://chatgpt.com", "default", "ChatGPT", "AI"),
            Shortcut("جيمني", "https://gemini.google.com", "default", "Gemini", "AI"),
            Shortcut("كلود", "https://claude.ai", "default", "Claude", "AI"),
            Shortcut("بيربليكسييتي", "https://www.perplexity.ai", "default", "Perplexity", "AI"),
            Shortcut("كوبيلوت", "https://copilot.microsoft.com", "default", "CoPilot", "AI"),
            Shortcut("ديب سيك", "https://www.deepseek.com", "default", "DeepSeek", "AI"),
            Shortcut("جروك", "https://grok.com", "default", "Grok", "AI"),
            
            # Communication & Chat
            Shortcut("واتساب", "https://web.whatsapp.com", "default", "WhatsApp", "Social"),
            Shortcut("تليجرام", "https://web.telegram.org", "default", "Telegram", "Social"),
            Shortcut("ديسكورد", "https://discord.com/app", "default", "Discord", "Social"),
            Shortcut("جيميل", "https://mail.google.com", "default", "Gmail", "Work"),
            
            # Social Media
            Shortcut("فيسبوك", "https://www.facebook.com", "default", "Facebook", "Social"),
            Shortcut("يوتيوب", "https://www.youtube.com", "default", "YouTube", "Social"),
            Shortcut("لينكد إن", "https://www.linkedin.com", "default", "LinkedIn", "Social"),
            
            # Productivity & Creative
            Shortcut("كانفا", "https://www.canva.com", "default", "Canva", "Work"),
            Shortcut("جيت هب", "https://github.com", "default", "GitHub", "Work"),
        ]

    @staticmethod
    def load() -> tuple[List[Shortcut], str]:
        ConfigManager._ensure_dir()
        path = ConfigManager.get_config_file()
        default_browser = "default"
        
        if not path.exists():
            data = ConfigManager.get_defaults()
            ConfigManager.save(data, default_browser)
            return data, default_browser

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            global_settings = raw.get("global", {})
            global_browser = global_settings.get("browser", "default")
            
            result: List[Shortcut] = []
            changed = False
            for item in raw.get("shortcuts", []):
                name = str(item.get("name", "")).strip()
                name_en = str(item.get("name_en", "")).strip()
                url = str(item.get("url", "")).strip()
                browser = str(item.get("browser", "default")).strip() or "default"
                category = str(item.get("category", "General")).strip()
                hotkey = str(item.get("hotkey", "")).strip()
                clicks = int(item.get("clicks", 0))
                if not name or not url:
                    continue
                n1, n2 = SiteCatalog.normalize(name, name_en, url)
                if n1 != name or n2 != name_en:
                    changed = True
                result.append(Shortcut(n1, url, browser, n2, category, hotkey, clicks))
            
            if result:
                if changed:
                    ConfigManager.save(result, global_browser)
                return result, global_browser
        except Exception:
            pass

        data = ConfigManager.get_defaults()
        ConfigManager.save(data, default_browser)
        return data, default_browser

    @staticmethod
    def save(shortcuts: List[Shortcut], global_browser: str = "default") -> None:
        ConfigManager._ensure_dir()
        payload = {
            "global": {
                "browser": global_browser
            },
            "shortcuts": [asdict(x) for x in shortcuts]
        }
        ConfigManager.get_config_file().write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    @staticmethod
    def export_shortcuts(path: Path, shortcuts: List[Shortcut], global_browser: str = "default") -> None:
        payload = {
            "global": {"browser": global_browser},
            "shortcuts": [asdict(x) for x in shortcuts]
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def import_shortcuts(path: Path) -> tuple[List[Shortcut], str]:
        raw = json.loads(path.read_text(encoding="utf-8"))
        global_settings = raw.get("global", {})
        global_browser = global_settings.get("browser", "default")
        
        result: List[Shortcut] = []
        for item in raw.get("shortcuts", []):
            name = str(item.get("name", "")).strip()
            name_en = str(item.get("name_en", "")).strip()
            url = str(item.get("url", "")).strip()
            browser = str(item.get("browser", "default")).strip() or "default"
            category = str(item.get("category", "General")).strip()
            hotkey = str(item.get("hotkey", "")).strip()
            clicks = int(item.get("clicks", 0))
            if name and url:
                result.append(Shortcut(name, url, browser, name_en, category, hotkey, clicks))
        return result, global_browser
