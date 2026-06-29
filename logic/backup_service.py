"""
BackupService - Automatic backup of configuration files.
"""
import shutil
from datetime import datetime
from pathlib import Path
from utils.path_utils import PathUtils
from utils.logger_service import logger


class BackupService:
    _max_backups = 10

    @classmethod
    def get_backups_dir(cls) -> Path:
        return PathUtils.get_backups_dir()

    @classmethod
    def create_backup(cls, label: str = "") -> Path:
        config_file = PathUtils.get_data_dir() / "shortcuts.json"
        if not config_file.exists():
            logger.warning("No config file to backup")
            return None

        backups_dir = cls.get_backups_dir()
        backups_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{label}" if label else ""
        backup_name = f"shortcuts_{timestamp}{suffix}.json"
        backup_path = backups_dir / backup_name

        try:
            shutil.copy2(config_file, backup_path)
            logger.info(f"Backup created: {backup_path}")
            cls._cleanup_old_backups()
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    @classmethod
    def restore_backup(cls, backup_path: Path) -> bool:
        config_file = PathUtils.get_data_dir() / "shortcuts.json"
        try:
            if backup_path.exists():
                shutil.copy2(backup_path, config_file)
                logger.info(f"Backup restored from: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
        return False

    @classmethod
    def list_backups(cls) -> list:
        backups_dir = cls.get_backups_dir()
        if not backups_dir.exists():
            return []
        return sorted(
            [f for f in backups_dir.iterdir() if f.suffix == ".json"],
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

    @classmethod
    def _cleanup_old_backups(cls):
        backups = cls.list_backups()
        if len(backups) > cls._max_backups:
            for old_backup in backups[cls._max_backups:]:
                try:
                    old_backup.unlink()
                    logger.debug(f"Removed old backup: {old_backup}")
                except Exception as e:
                    logger.warning(f"Failed to remove old backup: {e}")

    @classmethod
    def auto_backup(cls):
        config_file = PathUtils.get_data_dir() / "shortcuts.json"
        if not config_file.exists():
            return

        backups = cls.list_backups()
        if not backups:
            cls.create_backup("auto")
            return

        last_backup_time = datetime.fromtimestamp(backups[0].stat().st_mtime)
        hours_since_last = (datetime.now() - last_backup_time).total_seconds() / 3600

        if hours_since_last >= 24:
            cls.create_backup("auto")
