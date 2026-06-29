from database.config_manager import ConfigManager

def resort_shortcuts():
    # Force use categorized defaults
    defaults = ConfigManager.get_defaults()
    ConfigManager.save(defaults, "default")
    print("Shortcuts reordered and categorized successfully.")

if __name__ == "__main__":
    resort_shortcuts()
