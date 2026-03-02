"""
Watcher Module - Multi-channel input processing

Provides independent watchers that poll external sources
and route inputs to Bronze Inbox without interference.
"""

from .base_watcher import Watcher
from .gmail_watcher import GmailWatcher
from .filesystem_watcher import FilesystemWatcher

__all__ = [
    "Watcher",
    "GmailWatcher",
    "FilesystemWatcher",
]
