from dataclasses import dataclass
from typing import Optional, Tuple
from urllib.parse import urlparse

@dataclass
class Shortcut:
    name: str
    url: str
    browser: str = "default"
    name_en: str = ""
    category: str = "General"
    hotkey: str = ""
    clicks: int = 0

class SiteCatalog:
    # (domain, Arabic name, English name, Icon letters, Color, FontAwesome Icon)
    KNOWN = [
        ("github.com", "جيت هب", "GitHub", "GH", "#24292F", "fa5b.github"),
        ("linkedin.com", "لينكد إن", "LinkedIn", "IN", "#0A66C2", "fa5b.linkedin"),
        ("youtube.com", "يوتيوب", "YouTube", "YT", "#FF0000", "fa5b.youtube"),
        ("youtu.be", "يوتيوب", "YouTube", "YT", "#FF0000", "fa5b.youtube"),
        ("gemini.google.com", "جيمني", "Gemini", "GM", "#1a73e8", "fa5s.magic"),
        ("mail.google.com", "جيميل", "Gmail", "GM", "#EA4335", "fa5.envelope"),
        ("gmail.com", "جيميل", "Gmail", "GM", "#EA4335", "fa5.envelope"),
        ("google.com", "جوجل", "Google", "GO", "#4285F4", "fa5b.google"),
        ("facebook.com", "فيسبوك", "Facebook", "FB", "#1877F2", "fa5b.facebook-f"),
        ("twitter.com", "تويتر", "Twitter", "TW", "#1DA1F2", "fa5b.twitter"),
        ("instagram.com", "انستجرام", "Instagram", "IG", "#E4405F", "fa5b.instagram"),
        ("whatsapp.com", "واتساب", "WhatsApp", "WA", "#25D366", "fa5b.whatsapp"),
        ("telegram.org", "تليجرام", "Telegram", "TG", "#0088CC", "fa5b.telegram"),
        ("discord.com", "ديسكورد", "Discord", "DC", "#5865F2", "fa5b.discord"),
        ("chatgpt.com", "شات جي بي تي", "ChatGPT", "GPT", "#10a37f", "fa5s.robot"),
        ("openai.com", "شات جي بي تي", "ChatGPT", "GPT", "#10a37f", "fa5s.robot"),
        ("deepseek.com", "ديب سيك", "DeepSeek", "DS", "#000000", "fa5s.brain"),
        ("grok.com", "جروك", "Grok", "GR", "#000000", "fa5s.terminal"),
        ("perplexity.ai", "بيربليكسييتي", "Perplexity", "PX", "#20b2aa", "fa5s.search"),
        ("claude.ai", "كلود", "Claude", "CL", "#d97757", "fa5s.feather"),
        ("canva.com", "كانفا", "Canva", "CV", "#00C4CC", "fa5s.palette"),
        ("copilot.microsoft.com", "كوبيلوت", "CoPilot", "CP", "#0078D4", "fa5s.robot"),
    ]

    @staticmethod
    def get_host(url: str) -> str:
        host = urlparse(url.strip()).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host

    @staticmethod
    def find_by_url(url: str) -> Optional[Tuple[str, str, str, str, str, str]]:
        host = SiteCatalog.get_host(url)
        for domain, ar, en, icon, color, fa in SiteCatalog.KNOWN:
            if host == domain or host.endswith(f".{domain}"):
                return domain, ar, en, icon, color, fa
        return None

    @staticmethod
    def normalize(name: str, name_en: str, url: str) -> Tuple[str, str]:
        name = name.strip()
        name_en = name_en.strip()
        item = SiteCatalog.find_by_url(url)
        if item:
            _, ar, en, _, _, _ = item
            if name == en:
                name = ar
            if not name_en:
                name_en = en
        if not name_en:
            name_en = name
        return name, name_en

    @staticmethod
    def get_icon_meta(shortcut: Shortcut) -> Tuple[str, str, Optional[str]]:
        """Returns (Letters, Color, Optional FontAwesome Icon Name)"""
        if "id=61585982617699" in shortcut.url:
            return "", "#ffffff", "APP_ICON"
        
        item = SiteCatalog.find_by_url(shortcut.url)
        if item:
            return item[3], item[4], item[5]
        host = SiteCatalog.get_host(shortcut.url).replace(".", "")
        letters = "".join(ch for ch in host.upper() if ch.isalnum())[:2]
        return (letters or "WB"), "#0F766E", "fa5s.globe"
