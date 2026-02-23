"""
Base Watcher - Abstract class for all watchers

Provides common functionality for polling, duplicate detection,
state persistence, and restart safety.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class Watcher(ABC):
    """
    Abstract base class for all watchers.
    
    Subclasses must implement:
    - _fetch_items(): Fetch new items from the source
    - _extract_id(item): Extract unique ID from an item
    - _process_item(item): Process a single item (e.g., save to Inbox)
    """
    
    def __init__(
        self,
        name: str,
        state_dir: Path,
        inbox_dir: Path,
        interval_seconds: int = 60,
    ):
        """
        Initialize watcher.
        
        Args:
            name: Unique watcher identifier
            state_dir: Directory for state persistence
            inbox_dir: Directory to write processed items
            interval_seconds: Polling interval (default: 60)
        """
        self.name = name
        self.interval_seconds = max(30, interval_seconds)  # Minimum 30s
        self.state_dir = state_dir
        self.inbox_dir = inbox_dir
        
        # State file paths
        self.state_file = state_dir / f"watcher_{name}_state.md"
        self.processed_ids_file = state_dir / f"watcher_{name}_processed.md"
        
        # Ensure directories exist
        state_dir.mkdir(parents=True, exist_ok=True)
        inbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Load state
        self.last_check = self._load_timestamp()
        self.processed_ids = self._load_processed_ids()
        
        logger.info(f"Watcher '{name}' initialized (interval: {interval_seconds}s)")
    
    def _load_timestamp(self) -> datetime:
        """Load last check timestamp from state file"""
        if self.state_file.exists():
            content = self.state_file.read_text(encoding="utf-8")
            # Parse timestamp from markdown
            for line in content.split("\n"):
                if line.startswith("last_check:"):
                    ts_str = line.split(":", 1)[1].strip()
                    try:
                        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    except ValueError:
                        pass
        
        # Default to 30 days ago if no state
        from datetime import timedelta
        return datetime.now(timezone.utc) - timedelta(days=30)
    
    def _save_timestamp(self, ts: datetime):
        """Save timestamp to state file"""
        content = f"""# Watcher State: {self.name}

last_check: {ts.isoformat().replace('+00:00', 'Z')}
interval_seconds: {self.interval_seconds}
status: idle
"""
        self.state_file.write_text(content, encoding="utf-8")
    
    def _load_processed_ids(self) -> set[str]:
        """Load processed IDs from file"""
        if not self.processed_ids_file.exists():
            return set()
        
        ids = set()
        content = self.processed_ids_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") and not line.startswith("- ["):
                ids.add(line[2:])
        
        return ids
    
    def _save_processed_ids(self):
        """Save processed IDs to file (prune to last 1000)"""
        # Convert to list and prune
        ids_list = list(self.processed_ids)
        if len(ids_list) > 1000:
            ids_list = ids_list[-1000:]
            self.processed_ids = set(ids_list)
        
        # Write to file
        content = f"# Processed IDs: {self.name}\n\n"
        for item_id in sorted(ids_list):
            content += f"- {item_id}\n"
        
        self.processed_ids_file.write_text(content, encoding="utf-8")
    
    def _is_duplicate(self, item_id: str) -> bool:
        """Check if item was already processed"""
        return item_id in self.processed_ids
    
    def _mark_processed(self, item_id: str):
        """Mark item as processed"""
        self.processed_ids.add(item_id)
        self._save_processed_ids()
    
    @abstractmethod
    def _fetch_items(self, since: datetime) -> list:
        """
        Fetch items from source since the given timestamp.
        
        Returns:
            List of items to process
        """
        pass
    
    @abstractmethod
    def _extract_id(self, item) -> str:
        """Extract unique ID from an item"""
        pass
    
    @abstractmethod
    def _process_item(self, item, item_id: str):
        """
        Process a single item (e.g., save to Inbox).
        
        Should create a markdown file in inbox_dir.
        """
        pass
    
    def poll(self) -> int:
        """
        Execute a polling cycle.
        
        Returns:
            Number of items processed
        """
        start_time = time.time()
        logger.info(f"Watcher '{self.name}' starting poll")
        
        try:
            # Fetch new items
            items = self._fetch_items(self.last_check)
            logger.info(f"Watcher '{self.name}' fetched {len(items)} items")
            
            # Process new items (skip duplicates)
            processed_count = 0
            for item in items:
                item_id = self._extract_id(item)
                
                if self._is_duplicate(item_id):
                    logger.debug(f"Skipping duplicate: {item_id}")
                    continue
                
                # Process item
                self._process_item(item, item_id)
                self._mark_processed(item_id)
                processed_count += 1
            
            # Update last check timestamp
            self.last_check = datetime.now(timezone.utc)
            self._save_timestamp(self.last_check)
            
            duration = time.time() - start_time
            logger.info(
                f"Watcher '{self.name}' completed: {processed_count} items in {duration:.2f}s"
            )
            
            return processed_count
        
        except Exception as e:
            logger.error(f"Watcher '{self.name}' poll failed: {e}", exc_info=True)
            # Update state file with error
            self._save_timestamp(self.last_check)
            raise
    
    def restart(self):
        """
        Restart watcher (reload state, handle missed executions).
        
        Called on system restart to ensure no items are missed.
        """
        logger.info(f"Watcher '{self.name}' restarting")
        
        # Reload state from disk
        self.last_check = self._load_timestamp()
        self.processed_ids = self._load_processed_ids()
        
        # Check for missed executions
        now = datetime.now(timezone.utc)
        time_since_last_check = (now - self.last_check).total_seconds()
        
        if time_since_last_check > (self.interval_seconds * 2):
            logger.warning(
                f"Watcher '{self.name}' missed executions "
                f"(last check: {time_since_last_check:.0f}s ago)"
            )
            # Will catch up on next poll
        
        logger.info(f"Watcher '{self.name}' restarted successfully")
    
    def get_status(self) -> dict:
        """Get watcher status"""
        return {
            "name": self.name,
            "interval_seconds": self.interval_seconds,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "processed_ids_count": len(self.processed_ids),
            "status": "idle"
        }
