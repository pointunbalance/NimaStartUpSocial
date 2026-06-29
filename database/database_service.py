"""
DatabaseService - SQLite database for shortcuts storage.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from models.shortcut import Shortcut
from utils.path_utils import PathUtils
from utils.logger_service import logger


class DatabaseService:
    _db_path = None

    @classmethod
    def get_db_path(cls) -> Path:
        if cls._db_path is None:
            cls._db_path = PathUtils.get_data_dir() / "shortcuts.db"
        return cls._db_path

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(str(cls.get_db_path()))
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def initialize(cls):
        conn = cls._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS shortcuts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    browser TEXT DEFAULT 'default',
                    name_en TEXT DEFAULT '',
                    category TEXT DEFAULT 'General',
                    hotkey TEXT DEFAULT '',
                    clicks INTEGER DEFAULT 0,
                    last_opened TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
        finally:
            conn.close()

    @classmethod
    def load_shortcuts(cls) -> List[Shortcut]:
        cls.initialize()
        conn = cls._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM shortcuts ORDER BY clicks DESC")
            rows = cursor.fetchall()
            return [
                Shortcut(
                    name=row["name"],
                    url=row["url"],
                    browser=row["browser"],
                    name_en=row["name_en"],
                    category=row["category"],
                    hotkey=row["hotkey"],
                    clicks=row["clicks"],
                    last_opened=row["last_opened"],
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to load shortcuts: {e}")
            return []
        finally:
            conn.close()

    @classmethod
    def save_shortcuts(cls, shortcuts: List[Shortcut]):
        cls.initialize()
        conn = cls._get_connection()
        try:
            conn.execute("DELETE FROM shortcuts")
            for s in shortcuts:
                conn.execute("""
                    INSERT INTO shortcuts (name, url, browser, name_en, category, hotkey, clicks, last_opened)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (s.name, s.url, s.browser, s.name_en, s.category, s.hotkey, s.clicks, s.last_opened))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save shortcuts: {e}")
        finally:
            conn.close()

    @classmethod
    def update_shortcut(cls, url: str, **kwargs):
        cls.initialize()
        conn = cls._get_connection()
        try:
            sets = []
            values = []
            for key, value in kwargs.items():
                if key in ("name", "browser", "name_en", "category", "hotkey", "clicks", "last_opened"):
                    sets.append(f"{key} = ?")
                    values.append(value)
            if sets:
                sets.append("updated_at = CURRENT_TIMESTAMP")
                values.append(url)
                conn.execute(f"UPDATE shortcuts SET {', '.join(sets)} WHERE url = ?", values)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update shortcut: {e}")
        finally:
            conn.close()

    @classmethod
    def get_setting(cls, key: str, default: str = "") -> str:
        cls.initialize()
        conn = cls._get_connection()
        try:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default
        except Exception as e:
            logger.error(f"Failed to get setting: {e}")
            return default
        finally:
            conn.close()

    @classmethod
    def set_setting(cls, key: str, value: str):
        cls.initialize()
        conn = cls._get_connection()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
            """, (key, value))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to set setting: {e}")
        finally:
            conn.close()

    @classmethod
    def migrate_from_json(cls, json_path: Path) -> bool:
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            shortcuts = []
            for item in data.get("shortcuts", []):
                shortcuts.append(Shortcut(
                    name=item.get("name", ""),
                    url=item.get("url", ""),
                    browser=item.get("browser", "default"),
                    name_en=item.get("name_en", ""),
                    category=item.get("category", "General"),
                    hotkey=item.get("hotkey", ""),
                    clicks=item.get("clicks", 0),
                    last_opened=item.get("last_opened", ""),
                ))
            cls.save_shortcuts(shortcuts)
            global_browser = data.get("global", {}).get("browser", "default")
            cls.set_setting("global_browser", global_browser)
            logger.info(f"Migrated {len(shortcuts)} shortcuts from JSON")
            return True
        except Exception as e:
            logger.error(f"Failed to migrate from JSON: {e}")
            return False
