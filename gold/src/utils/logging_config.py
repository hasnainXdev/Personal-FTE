"""
Logging Configuration

Centralized logging setup for the AI Employee.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from pythonjsonlogger import jsonlogger


def setup_logging(
    log_path: str,
    level: str = 'INFO',
    json_format: bool = False,
) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_path: Path to log directory
        level: Logging level
        json_format: Use JSON format for logs
        
    Returns:
        Root logger
    """
    log_dir = Path(log_path)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    if json_format:
        console_formatter = jsonlogger.JsonFormatter()
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler for errors
    error_file = log_dir / f'error_{datetime.now().strftime("%Y-%m-%d")}.log'
    error_handler = logging.FileHandler(error_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    logger.addHandler(error_handler)
    
    # File handler for all logs
    all_file = log_dir / f'all_{datetime.now().strftime("%Y-%m-%d")}.log'
    all_handler = logging.FileHandler(all_file)
    all_handler.setLevel(logging.DEBUG)
    all_handler.setFormatter(console_formatter)
    logger.addHandler(all_handler)
    
    logger.info(f'Logging initialized. Level: {level}')
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
