# Database Schema - NimaStartupSocial

The application uses a JSON-based configuration file (`shortcuts.json`) stored in the user's application data directory.

## File Location

- **Windows**: `%APPDATA%/NimaStartupSocial/shortcuts.json`
- **Linux**: `~/.config/NimaStartupSocial/shortcuts.json`
- **macOS**: `~/Library/Application Support/NimaStartupSocial/shortcuts.json`

## Schema Structure

The file contains an object with a `shortcuts` key, which is a list of shortcut objects.

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | The display name in Arabic (or English). |
| `name_en` | String | The display name in English. |
| `url` | String | The full URL (including http/https). |
| `browser` | String | Key for the browser to use (`default`, `chrome`, `firefox`, etc.). |

### Example

```json
{
  "shortcuts": [
    {
      "name": "جيت هب",
      "name_en": "GitHub",
      "url": "https://github.com",
      "browser": "default"
    }
  ]
}
```
