"""Idempotency registry for tracking processed items."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from ..models.vault import Source
from ..errors import RegistryWriteError, RegistryCorruption


class IdempotencyRegistry:
    """
    Tracks processed items to prevent duplicate processing.
    
    Uses content hashing (SHA256) to ensure idempotency:
    - Before processing, check if content hash already exists
    - If exists, skip processing and log as "duplicate skipped"
    - If not exists, process and register the hash
    """
    
    def __init__(self, registry_path: str):
        """
        Initialize the idempotency registry.
        
        Args:
            registry_path: Path to the registry JSON file
        """
        self.registry_path = Path(registry_path)
        self._ensure_dir_exists()
        self._registry: Dict[str, dict] = self._load_registry()
    
    def _ensure_dir_exists(self) -> None:
        """Ensure the directory for the registry file exists."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_registry(self) -> Dict[str, dict]:
        """Load registry from disk or create empty registry."""
        if not self.registry_path.exists():
            return {}
        
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RegistryCorruption(
                f"Registry file is corrupted: {e}",
                {"path": str(self.registry_path)}
            )
        except (IOError, OSError) as e:
            raise RegistryCorruption(
                f"Cannot read registry file: {e}",
                {"path": str(self.registry_path)}
            )
    
    def _save_registry(self) -> None:
        """Save registry to disk atomically."""
        try:
            temp_path = self.registry_path.with_suffix('.json.tmp')
            with open(temp_path, 'w') as f:
                json.dump(self._registry, f, indent=2, default=str)
            temp_path.rename(self.registry_path)
        except (IOError, OSError) as e:
            if temp_path.exists():
                temp_path.unlink()
            raise RegistryWriteError(
                f"Failed to save registry: {e}",
                {"path": str(self.registry_path)}
            )
    
    def is_processed(self, content_hash: str) -> bool:
        """
        Check if content has already been processed.
        
        Args:
            content_hash: SHA256 hash of content
            
        Returns:
            True if already processed
        """
        return content_hash in self._registry
    
    def mark_processed(
        self,
        content_hash: str,
        item_id: str,
        source: str
    ) -> None:
        """
        Mark content as processed.
        
        Args:
            content_hash: SHA256 hash
            item_id: VaultItem ID
            source: 'gmail' or 'filesystem'
            
        Raises:
            RegistryWriteError: If cannot update registry
        """
        self._registry[content_hash] = {
            "vault_item_id": item_id,
            "source": source,
            "processed_at": datetime.utcnow().isoformat()
        }
        self._save_registry()
    
    def get_stats(self) -> dict:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with total_processed, today_count, oldest_entry, storage_size_bytes
        """
        if not self._registry:
            return {
                "total_processed": 0,
                "today_count": 0,
                "oldest_entry": None,
                "storage_size_bytes": 0
            }
        
        today = datetime.utcnow().date().isoformat()[:10]
        today_count = sum(
            1 for entry in self._registry.values()
            if entry.get("processed_at", "").startswith(today)
        )
        
        dates = [
            entry.get("processed_at", "")
            for entry in self._registry.values()
            if entry.get("processed_at")
        ]
        oldest_entry = min(dates) if dates else None
        
        # Estimate storage size
        storage_size = self.registry_path.stat().st_size if self.registry_path.exists() else 0
        
        return {
            "total_processed": len(self._registry),
            "today_count": today_count,
            "oldest_entry": oldest_entry,
            "storage_size_bytes": storage_size
        }
    
    def clear_old_entries(self, days_to_keep: int = 90) -> int:
        """
        Remove entries older than specified days.
        
        Args:
            days_to_keep: Number of days to retain entries
            
        Returns:
            Number of entries removed
        """
        cutoff = datetime.utcnow().timestamp() - (days_to_keep * 24 * 60 * 60)
        initial_count = len(self._registry)
        
        self._registry = {
            hash_key: entry for hash_key, entry in self._registry.items()
            if datetime.fromisoformat(entry.get("processed_at", "1970-01-01")).timestamp() > cutoff
        }
        
        removed_count = initial_count - len(self._registry)
        if removed_count > 0:
            self._save_registry()
        
        return removed_count
