import os
import platform
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List

class BrowserService:
    PATHS = {
        "windows": {
            "chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ],
            "firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ],
            "edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "brave": [
                r"C:\Program Files\Bravesoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\Bravesoftware\Brave-Browser\Application\brave.exe",
            ],
            "opera": [
                r"C:\Program Files\Opera\launcher.exe",
                r"C:\Program Files (x86)\Opera\launcher.exe",
            ],
        },
        "linux": {
            "chrome": ["google-chrome", "google-chrome-stable", "chromium-browser", "chromium"],
            "firefox": ["firefox"],
            "edge": ["microsoft-edge", "microsoft-edge-stable"],
            "brave": ["brave-browser", "brave"],
            "opera": ["opera"],
        },
        "darwin": {
            "chrome": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
            "firefox": ["/Applications/Firefox.app/Contents/MacOS/firefox"],
            "edge": ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
            "brave": ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"],
            "opera": ["/Applications/Opera.app/Contents/MacOS/Opera"],
            "safari": ["/Applications/Safari.app/Contents/MacOS/Safari"],
        },
    }

    @staticmethod
    def get_installed_browsers() -> Dict[str, str]:
        system = platform.system().lower()
        out: Dict[str, str] = {}
        for key, candidates in BrowserService.PATHS.get(system, {}).items():
            for c in candidates:
                if os.path.isabs(c):
                    if Path(c).exists():
                        out[key] = c
                        break
                else:
                    found = shutil.which(c)
                    if found:
                        out[key] = found
                        break
        return out

    @staticmethod
    def open_url(url: str, browser_key: str, installed: Dict[str, str]) -> bool:
        if browser_key == "default":
            return webbrowser.open(url)
        path = installed.get(browser_key)
        if not path:
            return False
        try:
            subprocess.Popen([path, url])
            return True
        except OSError:
            return False
