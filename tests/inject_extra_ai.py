from database.config_manager import ConfigManager
from logic.catalog_service import Shortcut

def inject_extra_ai():
    current = ConfigManager.load()
    existing_urls = [s.url.lower() for s in current]
    
    extra_ai = [
        Shortcut("بيربليكسييتي", "https://www.perplexity.ai", "default", "Perplexity"),
        Shortcut("كلود", "https://claude.ai", "default", "Claude"),
    ]
    
    added = False
    for s in extra_ai:
        if s.url.lower() not in existing_urls:
            current.append(s)
            added = True
    
    if added:
        ConfigManager.save(current)
        print("Extra AI shortcuts injected.")
    else:
        print("Shortcuts already exist.")

if __name__ == "__main__":
    inject_extra_ai()
