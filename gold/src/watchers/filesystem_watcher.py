"""
File System Watcher

Monitors a drop folder for new files and creates action files
in the Needs_Action folder.
"""

import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from .base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    """Handler for file drop events"""
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        self.watcher = watcher
        self.logger = watcher.logger
    
    def on_created(self, event) -> None:
        """Handle file creation events"""
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        self.logger.info(f'New file detected: {source.name}')
        
        try:
            self.watcher.process_file(source)
        except Exception as e:
            self.logger.error(f'Error processing file {source.name}: {e}')


class FileSystemWatcher(BaseWatcher):
    """Watcher for file system drop folder"""
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None):
        """
        Initialize file system watcher
        
        Args:
            vault_path: Path to the Obsidian vault
            drop_folder: Path to drop folder (defaults to vault/Inbox)
        """
        super().__init__(vault_path, check_interval=1)  # 1 second for real-time
        
        self.drop_folder = Path(drop_folder) if drop_folder else self.vault_path / 'Inbox'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        self.observer = Observer()
        self.handler = DropFolderHandler(self)
        self.processed_files: set = set()
        
    def start(self) -> None:
        """Start the file system observer"""
        self.observer.schedule(self.handler, str(self.drop_folder), recursive=False)
        self.observer.start()
        self.logger.info(f'Watching folder: {self.drop_folder}')
        
    def stop(self) -> None:
        """Stop the file system observer"""
        super().stop()
        self.observer.stop()
        self.observer.join()
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in drop folder
        
        This is handled by the event-driven observer,
        so we return an empty list here.
        """
        return []
    
    def process_file(self, source: Path) -> Optional[Path]:
        """
        Process a new file
        
        Args:
            source: Path to the new file
            
        Returns:
            Path to created action file
        """
        # Generate unique ID
        file_hash = hashlib.md5(str(source).encode()).hexdigest()[:8]
        action_id = f'FILE_{source.stem}_{file_hash}'
        
        # Check if already processed
        if action_id in self.processed_files:
            self.logger.debug(f'File already processed: {source.name}')
            return None
        
        # Copy file to vault
        dest = self.needs_action / source.name
        try:
            shutil.copy2(source, dest)
        except Exception as e:
            self.logger.error(f'Error copying file: {e}')
            return None
        
        # Create action file
        action_file = self.create_action_file({
            'source': source,
            'dest': dest,
            'action_id': action_id,
        })
        
        self.processed_files.add(action_id)
        return action_file
    
    def create_action_file(self, item: dict) -> Optional[Path]:
        """
        Create action file for dropped file
        
        Args:
            item: Dictionary with file info
            
        Returns:
            Path to created action file
        """
        source = item['source']
        dest = item['dest']
        action_id = item['action_id']
        
        # Get file info
        try:
            stat = source.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
        except Exception as e:
            self.logger.error(f'Error getting file info: {e}')
            size = 0
            modified = datetime.now()
        
        content = f'''---
type: file_drop
action_id: {action_id}
original_name: {source.name}
size: {size}
received: {modified.isoformat()}
status: pending
priority: normal
---

# File Dropped for Processing

## File Information
- **Original Name**: {source.name}
- **Size**: {self._format_size(size)}
- **Received**: {modified.strftime('%Y-%m-%d %H:%M:%S')}
- **Location**: `{dest}`

## Content Preview
[Read the file content to understand what action is needed]

## Suggested Actions
- [ ] Review file content
- [ ] Determine required action
- [ ] Execute action or create plan
- [ ] Move to /Done when complete

## Notes
[Add any relevant notes here]

---
*Created by FileSystemWatcher*
'''
        
        action_path = self.needs_action / f'{action_id}.md'
        action_path.write_text(content)
        self.logger.info(f'Created action file: {action_path.name}')
        
        return action_path
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'
