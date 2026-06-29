# MASTER STATE LEDGER - NimaStartupSocial

## Current Architecture (v2.0)

Clean architecture with separated concerns:

```
models/           → Data models (Shortcut dataclass)
  shortcut.py
logic/            → Business logic services
  shortcut_service.py  (CRUD, filter, sort, click tracking)
  title_service.py     (Async title fetching)
  catalog_service.py   (Site identification from catalog.json)
  browser_service.py   (Browser detection)
  autostart_service.py (OS autostart)
  tray_service.py      (System tray)
database/         → Persistence layer
  config_manager.py    (JSON config load/save/export/import)
ui/               → PyQt6 glassmorphism interface
  main_window.py       (Primary window)
  shortcuts_dialog.py  (Manager dialog)
  widgets/
    shortcut_card.py   (Draggable tile)
    dashboard_widget.py (Clock/date)
    toast_widget.py    (Notifications)
utils/            → Shared utilities
  path_utils.py        (Paths, APP_NAME, APP_VERSION)
  constants.py         (All magic numbers)
  frameless_drag.py    (Reusable drag mixin)
  strings.py           (i18n)
  window_blur.py       (Acrylic effects)
  resource_loader.py   (Icons)
  logger_service.py    (Logging)
data/             → Static data
  catalog.json         (22 known sites: domain, names, icons, colors)
```

## Features Catalog

### Completed Features (v2.0)

- [x] **Glassmorphism UI**: Modern Acrylic blur interface.
- [x] **Drag-and-Drop Reordering**: Grid and list reordering.
- [x] **Smart Catalog**: Auto-identify sites from `catalog.json`.
- [x] **System Tray**: Background with tray icon.
- [x] **Multi-Browser**: Per-shortcut or global browser selection.
- [x] **Search & Filtering**: Real-time filtering by name/URL.
- [x] **Usage Analytics**: Click tracking with "Popular" tab.
- [x] **Error Handling**: Proactive toast notifications.
- [x] **Comprehensive Testing**: 29 passing tests.
- [x] **Easy Installer**: Inno Setup based.
- [x] **Clean Architecture (v2.0)**: Service layer, constants, mixins.

## UI Map

- **Main Window**: `ShortcutCard` grid, search bar, category tabs, dashboard, footer.
- **Shortcuts Manager**: Add, Edit, Delete, Import/Export, Drag-reorder list.
- **Toast Notifications**: Non-blocking overlay feedback.

## Last Known State (v2.0)

- Version: v2.0
- Status: **STABLE & VERIFIED**.
- Verification: 29/29 tests passed (2026-06-29).
- Last Change: Full architecture refactor - ShortcutService, catalog.json, FramelessDragMixin, constants.
