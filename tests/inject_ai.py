from database.config_manager import ConfigManager
from models.shortcut import Shortcut

def inject_ai_shortcuts():
    current, global_browser = ConfigManager.load()
    existing_urls = [s.url.lower() for s in current]
    
    new_ai_sites = [
        Shortcut("شات جي بي تي", "https://chatgpt.com", "default", "ChatGPT"),
        Shortcut("جيمني", "https://gemini.google.com", "default", "Gemini"),
        Shortcut("ديب سيك", "https://www.deepseek.com", "default", "DeepSeek"),
        Shortcut("جروك", "https://grok.com", "default", "Grok"),
    ]
    
    added = False
    for s in new_ai_sites:
        if s.url.lower() not in existing_urls:
            current.append(s)
            added = True
    
    if added:
        ConfigManager.save(current, global_browser)
        print("AI shortcuts injected successfully.")
    else:
        print("AI shortcuts already exist.")

if __name__ == "__main__":
    inject_ai_shortcuts()
