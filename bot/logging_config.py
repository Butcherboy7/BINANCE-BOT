"""
Logging configuration helper.
Configures a dedicated file logger for logging API requests, responses, and failures.
"""
import logging
import os
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE_PATH = LOGS_DIR / "bot.log"

def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Configures and returns a logger instance that writes to logs/bot.log
    without spamming the console standard output.
    
    Args:
        name (str): Name of the logger.
        
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        
        # Format logs with timestamps, levels, and modules
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # We deliberately don't add a ConsoleHandler to this logger
        # to ensure the CLI remains clean and styled exclusively by Rich.
        # But we can add a high-priority Error Console handler if desired.
        logger.propagate = False
        
    return logger
