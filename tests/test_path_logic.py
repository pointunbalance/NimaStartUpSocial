import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from utils.path_utils import PathUtils
from utils.logger_service import LoggerService
from database.config_manager import ConfigManager

def test_path_resolution():
    print("Testing Path Resolution Logic...")
    
    data_dir = PathUtils.get_data_dir()
    logs_dir = PathUtils.get_logs_dir()
    backups_dir = PathUtils.get_backups_dir()
    
    print(f"Data Dir: {data_dir}")
    print(f"Logs Dir: {logs_dir}")
    print(f"Backups Dir: {backups_dir}")
    
    assert "NimaStartupSocial" in str(data_dir)
    assert logs_dir.parent == data_dir
    assert backups_dir.parent == data_dir
    
    # Check if directories were actually created
    assert data_dir.exists()
    assert logs_dir.exists()
    assert backups_dir.exists()
    
    print("Path resolution test PASSED.")

def test_logger_initialization():
    print("\nTesting Logger Initialization...")
    logger = LoggerService.initialize()
    logger.info("Test log message from path verification script.")
    
    log_file = PathUtils.get_logs_dir() / "app.log"
    assert log_file.exists()
    print(f"Log file created at: {log_file}")
    print("Logger initialization test PASSED.")

def test_config_manager_paths():
    print("\nTesting ConfigManager Paths...")
    config_dir = ConfigManager.get_data_dir()
    config_file = ConfigManager.get_config_file()
    
    print(f"Config Dir: {config_dir}")
    print(f"Config File: {config_file}")
    
    assert config_dir == PathUtils.get_data_dir()
    assert config_file == config_dir / "shortcuts.json"
    print("ConfigManager path test PASSED.")

if __name__ == "__main__":
    try:
        test_path_resolution()
        test_logger_initialization()
        test_config_manager_paths()
        print("\nALL TESTS PASSED SUCCESSFULLY.")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
