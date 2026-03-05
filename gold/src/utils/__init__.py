"""
Gold Tier AI Employee - Utils Module

Utility functions and helpers.
"""

from .retry_handler import with_retry, TransientError
from .audit_logger import AuditLogger
from .ralph_wiggum import RalphWiggumLoop, ralph_loop

# Optional logging config (requires pythonjsonlogger)
try:
    from .logging_config import setup_logging, get_logger
    __all__ = [
        'setup_logging',
        'get_logger',
        'with_retry',
        'TransientError',
        'AuditLogger',
        'RalphWiggumLoop',
        'ralph_loop',
    ]
except ImportError:
    # Fallback when pythonjsonlogger not installed
    import logging
    def setup_logging(log_path: str, level: str = 'INFO', json_format: bool = False):
        logging.basicConfig(level=getattr(logging, level.upper()))
        return logging.getLogger()
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
    __all__ = [
        'setup_logging',
        'get_logger',
        'with_retry',
        'TransientError',
        'AuditLogger',
        'RalphWiggumLoop',
        'ralph_loop',
    ]
