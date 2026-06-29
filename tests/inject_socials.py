from database.config_manager import ConfigManager
from models.shortcut import Shortcut

def inject_shortcuts():
    current, global_browser = ConfigManager.load()
    existing_urls = [s.url.lower() for s in current]
    
    new_sites = [
        Shortcut("فيسبوك", "https://www.facebook.com", "default", "Facebook"),
        Shortcut("واتساب", "https://web.whatsapp.com", "default", "WhatsApp"),
        Shortcut("تليجرام", "https://web.telegram.org", "default", "Telegram"),
        Shortcut("ديسكورد", "https://discord.com/app", "default", "Discord"),
    ]
    
    added = False
    for s in new_sites:
        if s.url.lower() not in existing_urls:
            current.append(s)
            added = True
    
    if added:
        ConfigManager.save(current, global_browser)
        print("Social shortcuts injected successfully.")
    else:
        print("Shortcuts already exist.")

if __name__ == "__main__":
    inject_shortcuts()
