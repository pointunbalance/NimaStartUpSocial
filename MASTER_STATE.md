# MASTER STATE LEDGER - NimaStartupSocial

## Current Architecture (v2.4.1)

Clean architecture with separated concerns:

```
models/           → Data models (Shortcut dataclass)
  shortcut.py
logic/            → Business logic services
  shortcut_service.py  (CRUD, filter, sort, click tracking)
  theme_service.py     (4 themes: dark/light/midnight/ocean)
  notification_service.py (Smart notifications)
  backup_service.py    (Auto backup, max 10)
  favicon_service.py   (Favicon fetching + cache)
  title_service.py     (Async title fetching)
  catalog_service.py   (Site identification from catalog.json)
  browser_service.py   (Browser detection)
  autostart_service.py (OS autostart)
  tray_service.py      (System tray)
database/         → Persistence layer
  config_manager.py    (JSON config load/save/export/import)
  database_service.py  (SQLite database)
ui/               → PyQt6 glassmorphism interface
  launcher_screen.py   (Start Menu launcher - vertical 340x700)
  main_window.py       (Management window)
  shortcuts_dialog.py  (Shortcuts editor)
  settings_dialog.py   (Settings: theme, size, color)
  widgets/
    shortcut_card.py   (Draggable tile with hover animation)
    stats_widget.py    (Statistics pie chart)
    dashboard_widget.py (Clock/date)
    toast_widget.py    (Notifications)
utils/            → Shared utilities
  path_utils.py        (Paths, APP_NAME, APP_VERSION)
  constants.py         (All magic numbers)
  frameless_drag.py    (Reusable drag mixin)
  strings.py           (i18n Arabic/English)
  window_blur.py       (Acrylic effects with platform guard)
  resource_loader.py   (Icons)
  logger_service.py    (Logging)
data/             → Static data
  catalog.json         (22 known sites: domain, names, icons, colors)
```

## Features Catalog

### Completed Features (v2.4.1)

#### Phase 1: UI/UX
- [x] **Smooth Hover Animations** - QPropertyAnimation on ShortcutCard
- [x] **4 Themes** - Dark, Light, Midnight, Ocean
- [x] **Card Size Control** - Adjustable 100-240px
- [x] **Color Customization** - Accent color picker
- [x] **Smart Notifications** - NotificationService

#### Phase 2: Functionality
- [x] **Smart Search** - QCompleter autocomplete
- [x] **Statistics Widget** - Pie chart of most used shortcuts
- [x] **Auto Backup** - Daily backups, max 10
- [x] **Recent Tab** - Last opened shortcuts tracking
- [x] **Hotkeys** - Per-shortcut hotkey support

#### Phase 3: Technical
- [x] **SQLite Database** - Fast local storage
- [x] **Favicon Service** - Auto-fetch website icons
- [x] **JSON Migration** - Import from legacy config
- [x] **API Ready** - DatabaseService for external access

#### Core Features
- [x] **Glassmorphism UI** - Modern Acrylic blur interface
- [x] **Drag-and-Drop** - Grid and list reordering
- [x] **Smart Catalog** - Auto-identify sites from catalog.json
- [x] **System Tray** - Background with tray icon
- [x] **Multi-Browser** - Per-shortcut or global browser selection
- [x] **Search & Filtering** - Real-time filtering by name/URL
- [x] **Usage Analytics** - Click tracking with "Popular" tab
- [x] **Error Handling** - Proactive toast notifications
- [x] **Comprehensive Testing** - 29 passing tests
- [x] **Easy Installer** - Inno Setup based

## UI Map

- **Launcher Screen**: Vertical Start Menu (340x700) with theme support
- **Main Window**: Full management with dashboard
- **Shortcuts Manager**: Add, Edit, Delete, Import/Export
- **Settings Dialog**: Theme, card size, accent color
- **Statistics Widget**: Pie chart of usage
- **Toast Notifications**: Non-blocking overlay feedback

## Last Known State (v2.4.1)

- Version: v2.4.1
- Status: **STABLE & VERIFIED**.
- Verification: 29/29 tests passed (2026-06-29).
- Last Bugfix: Fixed access violation when loading app icon at startup.
