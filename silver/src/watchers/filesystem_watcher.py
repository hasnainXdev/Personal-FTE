"""File System Watcher - Monitors Inbox folder for new files."""

import logging
import shutil
from pathlib import Path
from datetime import datetime

from .base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """Watches the Inbox folder for new files and creates action files.
    
    This is the simplest watcher for Bronze/Silver Tier:
    1. Monitors /Inbox folder for new files
    2. Copies files to /Needs_Action with metadata
    3. Creates accompanying .md metadata file
    """
    
    # Priority keywords for file content
    PRIORITY_KEYWORDS = {
        'high': ['urgent', 'asap', 'emergency', 'invoice', 'payment', 'contract'],
        'medium': ['report', 'meeting', 'deadline', 'review'],
        'low': ['reference', 'archive', 'backup', 'log']
    }
    
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
        
        # Also check Inbox_Drop for Silver tier
        inbox_drop = self.vault_path / 'Inbox_Drop'
        inbox_drop.mkdir(parents=True, exist_ok=True)
        
        for inbox in [self.inbox, inbox_drop]:
            if not inbox.exists():
                continue
                
            # Get all files in inbox (not directories, not .md files)
            for file_path in inbox.iterdir():
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
        
        # Try to read file content for priority detection
        content_preview = ""
        try:
            if file_path.suffix in ['.txt', '.md', '.csv', '.json']:
                content_preview = file_path.read_text()[:500]
        except:
            pass
        
        # Determine priority
        priority = self.get_priority(content_preview, self.PRIORITY_KEYWORDS)
        
        # Create metadata file
        meta_path = self.needs_action / f"{file_id}.md"
        
        content = f"""---
type: file_drop
file_id: {file_id}
original_name: {file_path.name}
size: {file_path.stat().st_size}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
source: inbox
---

# File Drop for Processing

## File Details

- **Original Name**: {file_path.name}
- **Size**: {self._format_size(file_path.stat().st_size)}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Copied To**: `{dest_path.name}`
- **Priority**: {priority}

## Content Preview

```
{content_preview[:300] if content_preview else "Binary file or unable to preview"}
```

## Instructions for Qwen

1. Read the attached file
2. Determine what action is needed
3. Process according to Company_Handbook.md rules
4. Create Plan.md if multi-step task (3+ steps)
5. Request approval if sensitive action needed
6. Move to /Done/ when complete
7. Update Dashboard.md

## Suggested Actions

- [ ] Read and understand file content
- [ ] Classify file type and priority
- [ ] Take appropriate action
- [ ] Document results
- [ ] Move to /Done/

---

*Created by FileSystemWatcher*
*Silver Tier*
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
