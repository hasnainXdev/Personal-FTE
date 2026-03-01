"""Base Watcher class for all watchers to inherit from."""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations.
    
    All watchers follow the same pattern:
    1. Check for updates periodically
    2. Create action files in Needs_Action folder
    3. Log all activities
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
        
    @abstractmethod
    def check_for_updates(self) -> list:
        """Check for new items to process.
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create a .md action file in Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file
        """
        pass
    
    def run(self):
        """Main run loop for the watcher."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f'Created action file: {filepath}')
            except Exception as e:
                self.logger.error(f'Error processing items: {e}')
                self._log_error(e)
            
            time.sleep(self.check_interval)
    
    def _log_error(self, error: Exception):
        """Log errors to the Logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'error_{today}.md'
        
        content = f"""---
type: error
date: {datetime.now().isoformat()}
watcher: {self.__class__.__name__}
---

# Error Log

## Error Details

```
{str(error)}
```

## Stack Trace

```
{self._get_stack_trace()}
```
"""
        # Append to existing log or create new
        if log_file.exists():
            existing = log_file.read_text()
            log_file.write_text(existing + "\n\n" + content)
        else:
            log_file.write_text(content)
    
    def _get_stack_trace(self) -> str:
        """Get the current stack trace."""
        import traceback
        return traceback.format_exc()
    
    def generate_unique_id(self, prefix: str = "ITEM") -> str:
        """Generate a unique ID for an item."""
        import hashlib
        timestamp = datetime.now().isoformat()
        hash_id = hashlib.md5(timestamp.encode()).hexdigest()[:12]
        return f"{prefix}_{hash_id}"
