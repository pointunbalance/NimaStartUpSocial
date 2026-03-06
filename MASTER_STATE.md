# MASTER STATE LEDGER - NimaStartupSocial

## Current Architecture

The application follows a strict MVC (Model-View-Controller) pattern:

- **Model (`database/`)**: `ConfigManager` handles JSON-based persistence of shortcuts and global settings.
- **View (`ui/`)**: Built with `PyQt6`, featuring a glassmorphism (Acrylic) interface. Custom widgets are located in `ui/widgets/`.
- **Controller (`logic/`)**: Services for browser detection (`BrowserService`), autostart (`AutostartService`), catalog management (`CatalogService`), and system tray (`TrayService`).
- **Utilities (`utils/`)**: Path resolution, logging, string localization (Arabic/English), and window blur effects.

## Features Catalog

### Completed Features (v1.7.1)

- [x] **Glassmorphism UI**: Modern Acrylic blur interface with modern typography.
- [x] **Drag-and-Drop Reordering**: Users can reorder shortcuts on the grid.
- [x] **Smart Catalog**: Automatic site identification and title fetching for dropped URLs.
- [x] **System Tray Integration**: Application runs in background with a tray icon.
- [x] **Multi-Browser Support**: Detects installed browsers (Chrome, Firefox, Edge, etc.) and allows per-shortcut or global selection.
- [x] **Search & Filtering**: Fast real-time filtering of shortcuts.
- [x] **Usage Analytics**: Click tracking for shortcuts and a "Popular" category tab.
- [x] **Error Handling System**: Proactive toast notifications for browser and internet issues.
- [x] **Comprehensive Testing**: 23+ unit and logic tests covering all components.
- [x] **Easy Installer**: Inno Setup based installer for v1.7.1.

## UI Map

- **Main Window**: Grid of `ShortcutCard` widgets, search bar, category tabs, dashboard, and footer with global browser selection.
- **Shortcuts Manager (Dialog)**: Detailed management of shortcuts (Add, Edit, Delete, Import/Export).
- **Toast Notifications**: Overlays for success/error feedback.

## Last Known State (v1.7.1)

- Version: v1.7.1
- Status: **STABLE & VERIFIED**.
- Verification: All 19 unit/logic tests passed (2026-02-27 08:15).
- Last Change: Implemented comprehensive tests and proactive error handling.
