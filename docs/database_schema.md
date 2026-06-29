# Database Schema - NimaStartupSocial

The application uses a JSON-based configuration file (`shortcuts.json`) stored in the user's application data directory.

## File Location

- **Windows**: `%APPDATA%/NimaStartupSocial/shortcuts.json`
- **Linux**: `~/.config/NimaStartupSocial/shortcuts.json`
- **macOS**: `~/Library/Application Support/NimaStartupSocial/shortcuts.json`

## Schema Structure

The file contains a `global` settings object and a `shortcuts` array.

### Global Settings

| Field | Type | Description |
| :--- | :--- | :--- |
| `browser` | String | Default browser key (`default`, `chrome`, `firefox`, `edge`, `brave`, `opera`). |

### Shortcut Object

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | The display name in Arabic (or English). |
| `name_en` | String | The display name in English. |
| `url` | String | The full URL (including http/https). |
| `browser` | String | Key for the browser to use (`default`, `chrome`, `firefox`, `edge`, `brave`, `opera`, `safari`). |
| `category` | String | Category grouping (`AI`, `Social`, `Work`, `General`, or custom). |
| `hotkey` | String | Optional keyboard shortcut (e.g., `Ctrl+1`). |
| `clicks` | Integer | Number of times the shortcut has been opened (for popularity sorting). |

### Example

```json
{
  "global": {
    "browser": "default"
  },
  "shortcuts": [
    {
      "name": "جيت هب",
      "name_en": "GitHub",
      "url": "https://github.com",
      "browser": "default",
      "category": "Work",
      "hotkey": "",
      "clicks": 12
    }
  ]
}
```
