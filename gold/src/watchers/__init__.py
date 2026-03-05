"""
Gold Tier AI Employee - Watchers Module

Watchers monitor external systems and create action files.
Silver features: FileSystem, Gmail
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FileSystemWatcher, DropFolderHandler
from .gmail_watcher import GmailWatcher

__all__ = [
    'BaseWatcher',
    'FileSystemWatcher',
    'DropFolderHandler',
    'GmailWatcher',
]
