import os
import platform
import sys
from pathlib import Path

class AutostartService:
    APP_NAME = "NimaStartupSocial"

    @staticmethod
    def _get_command() -> str:
        if getattr(sys, "frozen", False):
            return str(Path(sys.executable).resolve())
        return f'"{Path(sys.executable).resolve()}" "{Path(__file__).resolve().parent.parent / "app.py"}"'

    @staticmethod
    def is_enabled() -> bool:
        system = platform.system().lower()
        if system == "windows":
            return AutostartService._is_enabled_windows()
        if system == "linux":
            return AutostartService._get_linux_desktop_file().exists()
        if system == "darwin":
            return AutostartService._get_macos_plist_file().exists()
        return False

    @staticmethod
    def set_enabled(enabled: bool) -> bool:
        system = platform.system().lower()
        if system == "windows":
            return AutostartService._set_windows(enabled)
        if system == "linux":
            return AutostartService._set_linux(enabled)
        if system == "darwin":
            return AutostartService._set_macos(enabled)
        return False

    @staticmethod
    def _is_enabled_windows() -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, AutostartService.APP_NAME)
                return True
        except Exception:
            return False

    @staticmethod
    def _set_windows(enabled: bool) -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                if enabled:
                    winreg.SetValueEx(key, AutostartService.APP_NAME, 0, winreg.REG_SZ, AutostartService._get_command())
                else:
                    try:
                        winreg.DeleteValue(key, AutostartService.APP_NAME)
                    except FileNotFoundError:
                        pass
            return True
        except Exception:
            return False

    @staticmethod
    def _get_linux_desktop_file() -> Path:
        return Path.home() / ".config" / "autostart" / f"{AutostartService.APP_NAME}.desktop"

    @staticmethod
    def _set_linux(enabled: bool) -> bool:
        path = AutostartService._get_linux_desktop_file()
        try:
            if enabled:
                path.parent.mkdir(parents=True, exist_ok=True)
                content = "\n".join([
                    "[Desktop Entry]",
                    "Type=Application",
                    f"Name={AutostartService.APP_NAME}",
                    f"Exec={AutostartService._get_command()}",
                    "X-GNOME-Autostart-enabled=true"
                ])
                path.write_text(content, encoding="utf-8")
            elif path.exists():
                path.unlink()
            return True
        except OSError:
            return False

    @staticmethod
    def _get_macos_plist_file() -> Path:
        return Path.home() / "Library" / "LaunchAgents" / f"{AutostartService.APP_NAME}.plist"

    @staticmethod
    def _set_macos(enabled: bool) -> bool:
        path = AutostartService._get_macos_plist_file()
        try:
            if enabled:
                path.parent.mkdir(parents=True, exist_ok=True)
                content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>{AutostartService.APP_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/sh</string>
        <string>-c</string>
        <string>{AutostartService._get_command()}</string>
    </array>
    <key>RunAtLoad</key><true/>
</dict>
</plist>"""
                path.write_text(content, encoding="utf-8")
            elif path.exists():
                path.unlink()
            return True
        except OSError:
            return False
