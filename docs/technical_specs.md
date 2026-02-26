# Technical Specifications - NimaStartupSocial

## Tech Stack

- **Language**: Python 3.8 / 3.9 (Recommended for Win7 stability)
- **GUI Framework**: PyQt5 (For Windows 7 32-bit compatibility)
- **Styling**: Centralized QSS (Modern Light Theme)
- **Icons**: Text-based badges and SVG assets
- **Data Storage**: JSON (`shortcuts.json`)

## Architecture (MVC)

- **Model**: `database/config_manager.py` (Handles data persistence)
- **View**: `ui/` directory containing PyQt5 widgets and windows.
- **Controller/Logic**: `logic/` directory containing business rules (Browser resolution, Auto-start, Cataloging).

## Key Components

- **BrowserResolver**: Resolves executable paths for common browsers across Windows, Linux, and macOS.
- **AutoStartManager**: Handles OS-specific autostart registration (Registry for Windows, .desktop for Linux, launchd for macOS).
- **SiteCatalog**: Mapping of domains to localized names and colors.
- **ShortcutCard**: Atomic UI unit for displaying a shortcut.

## Constraints

- **PyInstaller**: Target platform is Windows 7 32-bit (Single-file exe).
- **RTL**: Must support Left-to-Right (English) and Right-to-Left (Arabic) concurrently.
- **Stability**: Background operations for I/O to avoid UI freezing.
