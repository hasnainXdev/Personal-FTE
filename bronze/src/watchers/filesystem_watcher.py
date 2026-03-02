"""File System Watcher - Monitors Inbox folder for new files."""

import logging
import shutil
from pathlib import Path
from datetime import datetime

from .base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """Watches the Inbox folder for new files and creates action files.
    
    This is the simplest watcher for Bronze Tier:
    1. Monitors /Inbox folder for new files
    2. Copies files to /Needs_Action with metadata
    3. Creates accompanying .md metadata file
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Track processed files by name + size
        self.processed_files = set()
    
    def check_for_updates(self) -> list:
        """Check Inbox for new files.
        
        Returns:
            List of new file paths to process
        """
        new_files = []
        
        if not self.inbox.exists():
            self.inbox.mkdir(parents=True, exist_ok=True)
            return []
        
        # Get all files in inbox (not directories)
        for file_path in self.inbox.iterdir():
            if file_path.is_file() and not file_path.name.endswith('.md'):
                # Create unique identifier
                file_id = f"{file_path.name}_{file_path.stat().st_size}"
                
                if file_id not in self.processed_files:
                    new_files.append(file_path)
                    self.processed_files.add(file_id)
                    self.logger.info(f"New file detected: {file_path.name}")
        
        return new_files
    
    def create_action_file(self, file_path: Path) -> Path:
        """Create action file and copy the dropped file.
        
        Args:
            file_path: Path to the new file in Inbox
            
        Returns:
            Path to the created metadata file
        """
        # Generate unique ID
        file_id = self.generate_unique_id("FILE")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Copy file to Needs_Action
        dest_path = self.needs_action / f"{file_id}_{file_path.name}"
        shutil.copy2(file_path, dest_path)
        
        # Create metadata file
        meta_path = self.needs_action / f"{file_id}.md"
        
        content = f"""---
type: file_drop
file_id: {file_id}
original_name: {file_path.name}
size: {file_path.stat().st_size}
received: {datetime.now().isoformat()}
priority: medium
status: pending
source: inbox
---

# File Drop for Processing

## File Details

- **Original Name**: {file_path.name}
- **Size**: {self._format_size(file_path.stat().st_size)}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Copied To**: `{dest_path.name}`

## Instructions for Qwen

1. Read the attached file
2. Determine what action is needed
3. Process according to Company_Handbook.md rules
4. Move to /Done/ when complete
5. Update Dashboard.md

## Suggested Actions

- [ ] Read and understand file content
- [ ] Classify file type and priority
- [ ] Take appropriate action
- [ ] Document results
- [ ] Move to /Done/

---

*Created by FileSystemWatcher*
"""
        
        meta_path.write_text(content)
        self.logger.info(f"Created action file: {meta_path.name}")
        
        return meta_path
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
