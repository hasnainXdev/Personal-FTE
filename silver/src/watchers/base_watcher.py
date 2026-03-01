"""Base Watcher class for all watchers to inherit from."""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib


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
        self.logs_extended = self.vault_path / 'Logs_Extended'
        self.check_interval = check_interval
        
        # Ensure directories exist
        for directory in [self.needs_action, self.inbox, self.logs, self.logs_extended]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
        
        # State file for persistence
        self.state_file = self.logs_extended / f'watcher_{self._get_name()}_state.md'
        self._load_state()
    
    def _get_name(self) -> str:
        """Get watcher name for state file."""
        return self.__class__.__name__.lower().replace('watcher', '')
    
    def _load_state(self):
        """Load state from file."""
        if self.state_file.exists():
            content = self.state_file.read_text()
            # Parse processed IDs from state file
            for line in content.split('\n'):
                if line.startswith('- '):
                    self.processed_ids.add(line[2:].strip())
    
    def _save_state(self):
        """Save state to file."""
        content = f"""---
watcher: {self._get_name()}
last_updated: {datetime.now().isoformat()}
processed_count: {len(self.processed_ids)}
---

# Watcher State

## Processed IDs

"""
        for item_id in sorted(self.processed_ids):
            content += f"- {item_id}\n"
        
        self.state_file.write_text(content)
    
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
                self._save_state()
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
        timestamp = datetime.now().isoformat()
        hash_id = hashlib.md5(timestamp.encode()).hexdigest()[:12]
        return f"{prefix}_{hash_id}"
    
    def get_priority(self, content: str, keywords: dict) -> str:
        """Determine priority based on keywords."""
        content_lower = content.lower()
        for priority, words in keywords.items():
            for word in words:
                if word in content_lower:
                    return priority
        return 'medium'
