# Technical Specifications - NimaStartupSocial

## Tech Stack

- **Language**: Python 3.14
- **GUI Framework**: PyQt6
- **Styling**: Centralized QSS (Glassmorphism Light Theme)
- **Icons**: FontAwesome 5 via `qtawesome` + text-based badges
- **Data Storage**: JSON (`shortcuts.json`)

## Architecture (MVC)

- **Model**: `database/config_manager.py` (Handles data persistence)
- **View**: `ui/` directory containing PyQt6 widgets and windows.
- **Controller/Logic**: `logic/` directory containing business rules (Browser resolution, Auto-start, Cataloging, System Tray).

## Key Components

- **BrowserService**: Resolves executable paths for common browsers across Windows, Linux, and macOS. Uses `@lru_cache` for detection.
- **AutostartService**: Handles OS-specific autostart registration (Registry for Windows, .desktop for Linux, launchd for macOS).
- **SiteCatalog**: Mapping of domains to localized names, colors, and FontAwesome icons.
- **ShortcutCard**: Atomic UI unit for displaying a shortcut with drag-and-drop support.
- **DashboardWidget**: Real-time clock/date display with system username.
- **ToastWidget**: Non-blocking notification overlay with fade-in/out animations.
- **SystemTrayService**: System tray integration for background operation.
- **WindowBlurService**: Windows Acrylic/Mica blur effects via ctypes.

## Data Model

Each shortcut contains 7 fields: `name`, `url`, `browser`, `name_en`, `category`, `hotkey`, `clicks`.

## Constraints

- **PyInstaller**: Single-file exe packaging supported.
- **RTL**: Supports Right-to-Left (Arabic) and Left-to-Right (English) concurrently.
- **Stability**: Background operations for I/O (TitleFetcher QThread) to avoid UI freezing.
- **Cross-Platform**: Windows, Linux, macOS support for autostart and browser detection.
