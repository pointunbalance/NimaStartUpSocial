import sys
from pathlib import Path

from utils.path_utils import PathUtils
from utils.logger_service import LoggerService
from database.config_manager import ConfigManager

def test_path_resolution():
    data_dir = PathUtils.get_data_dir()
    logs_dir = PathUtils.get_logs_dir()
    backups_dir = PathUtils.get_backups_dir()
    
    assert "NimaStartupSocial" in str(data_dir)
    assert logs_dir.parent == data_dir
    assert backups_dir.parent == data_dir
    
    assert data_dir.exists()
    assert logs_dir.exists()
    assert backups_dir.exists()

def test_logger_initialization():
    logger = LoggerService.initialize()
    logger.info("Test log message from path verification script.")
    
    log_file = PathUtils.get_logs_dir() / "app.log"
    assert log_file.exists()

def test_config_manager_paths():
    config_dir = ConfigManager.get_data_dir()
    config_file = ConfigManager.get_config_file()
    
    assert config_dir == PathUtils.get_data_dir()
    assert config_file == config_dir / "shortcuts.json"

if __name__ == "__main__":
    try:
        test_path_resolution()
        test_logger_initialization()
        test_config_manager_paths()
        print("\nALL TESTS PASSED SUCCESSFULLY.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
