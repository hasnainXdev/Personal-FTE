"""
Base Watcher Class

Abstract base class for all watcher implementations.
All watchers follow the same pattern:
1. Check for new items periodically
2. Create action files in Needs_Action folder
3. Log all activities
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """Abstract base class for all watchers"""
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize base watcher
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running = False
        self.processed_ids: set = set()
        
        # Ensure needs_action folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check for new items to process
        
        Returns:
            List of new items to process
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create action file in Needs_Action folder
        
        Args:
            item: Item to create action file for
            
        Returns:
            Path to created file or None if failed
        """
        pass
    
    def run(self) -> None:
        """Main watcher loop"""
        self.running = True
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        while self.running:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    if filepath:
                        self.logger.info(f'Created action file: {filepath.name}')
            except Exception as e:
                self.logger.error(f'Error in watcher loop: {e}', exc_info=True)
            
            time.sleep(self.check_interval)
    
    def stop(self) -> None:
        """Stop the watcher"""
        self.running = False
        self.logger.info(f'Stopping {self.__class__.__name__}')
    
    def generate_unique_id(self, prefix: str) -> str:
        """
        Generate unique ID for action file
        
        Args:
            prefix: Prefix for the ID (e.g., 'EMAIL', 'FILE')
            
        Returns:
            Unique ID string
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{prefix}_{timestamp}'
    
    def create_metadata_file(self, action_path: Path, metadata: dict) -> Path:
        """
        Create metadata file alongside action file
        
        Args:
            action_path: Path to action file
            metadata: Metadata dictionary
            
        Returns:
            Path to metadata file
        """
        meta_path = action_path.with_suffix('.meta.md')
        content = f'''---
{self._format_frontmatter(metadata)}
---
'''
        meta_path.write_text(content)
        return meta_path
    
    def _format_frontmatter(self, metadata: dict) -> str:
        """Format metadata dictionary as YAML frontmatter"""
        lines = []
        for key, value in metadata.items():
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, bool):
                value = str(value).lower()
            elif isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            lines.append(f'{key}: {value}')
        return '\n'.join(lines)
    
    def is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        now = datetime.now()
        # Weekend check
        if now.weekday() >= 5:
            return False
        # Business hours check (9 AM - 6 PM)
        return 9 <= now.hour < 18
