# Startup Social Launcher (Python + Qt)

Simple desktop launcher that shows only shortcut names (not URLs), lets you choose which browser opens each site, and can auto-run at system startup.

## Features

- Modern Qt desktop UI.
- URL hidden from end-user UI; only site name is shown.
- Built-in `Manage shortcuts` screen (add/edit/delete without manual JSON editing).
- Per-shortcut browser selection:
  - System Default
  - Chrome / Firefox / Edge / Brave / Opera (Safari on macOS)
- Auto-start support:
  - Windows: `HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`
  - Linux: `~/.config/autostart/NimaStartupSocial.desktop`
  - macOS: `~/Library/LaunchAgents/NimaStartupSocial.plist`
- Editable shortcuts config file.

## Requirements

- Python 3.8+ recommended.
- For **Windows 7 32-bit**, use **Python 3.8 (32-bit)** and build with PyInstaller from that environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

## Configure Shortcuts

Use `Manage shortcuts` button in the app for normal editing.

Advanced/manual editing is still available in the config file:

The app creates:

- Windows: `%APPDATA%\\NimaStartupSocial\\shortcuts.json`
- Linux: `~/.config/NimaStartupSocial/shortcuts.json`
- macOS: `~/Library/Application Support/NimaStartupSocial/shortcuts.json`

Example:

```json
{
  "shortcuts": [
    { "name": "GitHub", "url": "https://github.com", "browser": "default" },
    { "name": "Docs", "url": "https://docs.python.org", "browser": "firefox" }
  ]
}
```

`browser` accepts: `default`, `chrome`, `firefox`, `edge`, `brave`, `opera`, `safari` (macOS).

## Build Executable (optional)

Install:

```bash
pip install pyinstaller
```

Build:

```bash
pyinstaller --noconfirm --windowed --name StartupSocial app.py
```

This creates a desktop executable in `dist/StartupSocial`.

## Notes

- Hiding URLs in UI is for user experience only. Admins or power users can still read the config file.
- Cross-platform binaries must be built on each target OS separately.
