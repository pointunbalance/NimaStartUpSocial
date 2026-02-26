import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

class LoggerService:
    _logger = None

    @classmethod
    def initialize(cls):
        if cls._logger:
            return cls._logger

        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"

        cls._logger = logging.getLogger("NimaStartUpSocial")
        cls._logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        if cls._logger.hasHandlers():
            cls._logger.handlers.clear()

        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File Handler (Rotate at 5MB, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)

        cls._logger.info("--- Logger Initialized (Enterprise Mode) ---")
        return cls._logger

    @classmethod
    def get_logger(cls):
        if not cls._logger:
            return cls.initialize()
        return cls._logger

# Global convenience instance
logger = LoggerService.initialize()
