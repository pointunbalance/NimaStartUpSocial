# NimaStartUpSocial - Smart Shortcut Launcher

Modern desktop launcher with glassmorphism UI, multi-browser support, and smart features.

## Features

### Core
- **Launcher Screen** - Vertical Start Menu-style interface (340x700)
- **MainWindow** - Full management interface with dashboard
- **Drag-and-Drop** - Reorder shortcuts by dragging
- **Multi-Browser** - Per-shortcut or global browser selection
- **Auto-Start** - Windows/Linux/macOS support
- **System Tray** - Run in background

### UI/UX
- **Glassmorphism** - Modern acrylic blur effects
- **4 Themes** - Dark, Light, Midnight, Ocean
- **Smooth Animations** - Hover effects with QPropertyAnimation
- **Card Sizes** - Adjustable from 100px to 240px
- **Color Customization** - Accent color picker
- **RTL Support** - Full Arabic interface

### Smart Features
- **Smart Search** - Autocomplete suggestions
- **Category Tabs** - All, Popular, Recent, AI, Social, Work
- **Click Tracking** - Usage statistics
- **Statistics Widget** - Pie chart of most used shortcuts
- **Auto Backup** - Daily backups (max 10)
- **Smart Notifications** - Toast notifications
- **Recent Tab** - Last opened shortcuts

### Technical
- **Clean Architecture** - models/logic/database/ui/utils layers
- **SQLite Database** - Fast local storage
- **Favicon Service** - Auto-fetch website icons
- **JSON Migration** - Import from legacy config
- **29 Tests** - All passing

## Requirements

- Python 3.10+
- PyQt6
- qtawesome
- requests
- beautifulsoup4

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

## Build

```bash
pyinstaller --clean NimaStartUpSocial.spec
```

## Project Structure

```
models/           → Shortcut dataclass
logic/            → Business logic services
  shortcut_service.py  (CRUD, filter, sort)
  theme_service.py     (4 themes)
  notification_service.py (Smart notifications)
  backup_service.py    (Auto backup)
  favicon_service.py   (Favicon fetching)
  browser_service.py   (Browser detection)
  catalog_service.py   (Site identification)
  title_service.py     (Title fetching)
  autostart_service.py (OS autostart)
  tray_service.py      (System tray)
database/         → Persistence layer
  config_manager.py    (JSON config)
  database_service.py  (SQLite database)
ui/               → PyQt6 interface
  launcher_screen.py   (Start Menu launcher)
  main_window.py       (Management window)
  shortcuts_dialog.py  (Shortcuts editor)
  settings_dialog.py   (Settings)
  widgets/
    shortcut_card.py   (Draggable tile)
    stats_widget.py    (Statistics chart)
    dashboard_widget.py (Clock/date)
    toast_widget.py    (Notifications)
utils/            → Shared utilities
  path_utils.py        (Paths)
  constants.py         (Constants)
  frameless_drag.py    (Drag mixin)
  strings.py           (i18n Arabic/English)
  window_blur.py       (Acrylic effects)
  resource_loader.py   (Icons)
  logger_service.py    (Logging)
data/             → Static data
  catalog.json         (22 known sites)
```

## Configuration

### Windows
`%APPDATA%\NimaStartupSocial\shortcuts.json`

### Linux
`~/.config/NimaStartupSocial/shortcuts.json`

### macOS
`~/Library/Application Support/NimaStartupSocial/shortcuts.json`

## Themes

| Theme | Description |
|-------|-------------|
| Dark | Default dark glassmorphism |
| Light | Light glassmorphism |
| Midnight | Pure black with purple accent |
| Ocean | Deep blue with cyan accent |

## License

Private - NimaTechVibe
