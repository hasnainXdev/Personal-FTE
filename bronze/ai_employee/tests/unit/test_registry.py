"""Unit tests for IdempotencyRegistry."""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from src.ai_employee.services.registry import IdempotencyRegistry
from src.ai_employee.errors import RegistryCorruption, RegistryWriteError


@pytest.fixture
def temp_registry():
    """Create temporary registry file."""
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir) / "processed.json"
    yield registry_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def registry(temp_registry):
    """Create IdempotencyRegistry for testing."""
    return IdempotencyRegistry(str(temp_registry))


class TestIdempotencyRegistry:
    """Tests for IdempotencyRegistry service."""

    def test_create_registry(self, temp_registry):
        """Verify registry is created."""
        registry = IdempotencyRegistry(str(temp_registry))
        assert registry is not None

    def test_is_processed_new_hash(self, registry):
        """Verify is_processed() returns False for new hash."""
        result = registry.is_processed("new-hash-123")
        assert result is False

    def test_mark_processed(self, registry):
        """Verify mark_processed() records hash."""
        registry.mark_processed(
            content_hash="test-hash",
            item_id="item-123",
            source="filesystem"
        )
        assert registry.is_processed("test-hash") is True

    def test_is_processed_after_mark(self, registry):
        """Verify is_processed() returns True after marking."""
        registry.mark_processed("hash-1", "item-1", "gmail")
        assert registry.is_processed("hash-1") is True
        assert registry.is_processed("hash-2") is False

    def test_get_stats_empty(self, registry):
        """Verify get_stats() for empty registry."""
        stats = registry.get_stats()
        assert stats["total_processed"] == 0
        assert stats["today_count"] == 0

    def test_get_stats_with_entries(self, registry):
        """Verify get_stats() with entries."""
        registry.mark_processed("hash-1", "item-1", "filesystem")
        registry.mark_processed("hash-2", "item-2", "gmail")
        
        stats = registry.get_stats()
        assert stats["total_processed"] == 2
        assert stats["today_count"] == 2

    def test_registry_persists(self, temp_registry):
        """Verify registry persists to disk."""
        # Create and populate registry
        registry1 = IdempotencyRegistry(str(temp_registry))
        registry1.mark_processed("persist-hash", "item-1", "filesystem")
        
        # Create new registry instance
        registry2 = IdempotencyRegistry(str(temp_registry))
        assert registry2.is_processed("persist-hash") is True

    def test_registry_file_format(self, temp_registry):
        """Verify registry file is valid JSON."""
        registry = IdempotencyRegistry(str(temp_registry))
        registry.mark_processed("test-hash", "item-1", "filesystem")
        
        # Read and parse file
        content = temp_registry.read_text()
        data = json.loads(content)
        
        assert "test-hash" in data
        assert data["test-hash"]["vault_item_id"] == "item-1"

    def test_clear_old_entries(self, registry):
        """Verify clear_old_entries() removes old entries."""
        # Add entries
        registry.mark_processed("hash-1", "item-1", "filesystem")
        registry.mark_processed("hash-2", "item-2", "gmail")
        
        # Clear entries older than 0 days (all of them)
        removed = registry.clear_old_entries(days_to_keep=0)
        
        # All entries should be removed
        assert removed == 2
        assert registry.get_stats()["total_processed"] == 0
