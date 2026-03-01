"""Tests for Bronze Tier AI Employee."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.watchers import FileSystemWatcher, BaseWatcher


class TestBaseWatcher:
    """Tests for the base watcher class."""
    
    def test_base_watcher_is_abstract(self):
        """BaseWatcher cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseWatcher("/tmp/test")
    
    def test_base_watcher_creates_directories(self, tmp_path):
        """Watcher creates required directories."""
        vault = tmp_path / "test_vault"
        watcher = FileSystemWatcher(str(vault))
        
        assert (vault / "Needs_Action").exists()
        assert (vault / "Inbox").exists()
        assert (vault / "Logs").exists()


class TestFileSystemWatcher:
    """Tests for the file system watcher."""
    
    @pytest.fixture
    def watcher(self, tmp_path):
        """Create a watcher with temporary vault."""
        vault = tmp_path / "test_vault"
        vault.mkdir()
        return FileSystemWatcher(str(vault), check_interval=1)
    
    def test_init(self, watcher):
        """Watcher initializes correctly."""
        assert watcher.vault_path.exists()
        assert watcher.needs_action.exists()
        assert watcher.inbox.exists()
    
    def test_check_for_updates_empty(self, watcher):
        """Returns empty list when inbox is empty."""
        items = watcher.check_for_updates()
        assert len(items) == 0
    
    def test_check_for_updates_detects_file(self, watcher):
        """Detects new files in inbox."""
        # Create a test file
        test_file = watcher.inbox / "test.txt"
        test_file.write_text("test content")
        
        items = watcher.check_for_updates()
        assert len(items) == 1
        assert items[0] == test_file
    
    def test_check_for_updates_no_duplicates(self, watcher):
        """Does not report same file twice."""
        test_file = watcher.inbox / "test.txt"
        test_file.write_text("test content")
        
        # First check
        items1 = watcher.check_for_updates()
        assert len(items1) == 1
        
        # Second check (same file)
        items2 = watcher.check_for_updates()
        assert len(items2) == 0
    
    def test_create_action_file(self, watcher):
        """Creates action file and metadata."""
        test_file = watcher.inbox / "test.txt"
        test_file.write_text("test content")
        
        meta_path = watcher.create_action_file(test_file)
        
        assert meta_path.exists()
        assert meta_path.suffix == '.md'
        assert "type: file_drop" in meta_path.read_text()
        
        # Check file was copied
        copied_files = list(watcher.needs_action.glob("FILE_*_test.txt"))
        assert len(copied_files) == 1


class TestIntegration:
    """Integration tests for the complete flow."""
    
    @pytest.fixture
    def vault(self, tmp_path):
        """Create a temporary vault."""
        vault = tmp_path / "test_vault"
        vault.mkdir()
        (vault / "Dashboard.md").write_text("# Dashboard")
        (vault / "Company_Handbook.md").write_text("# Handbook")
        return vault
    
    def test_end_to_end_flow(self, vault):
        """Test complete file drop to action flow."""
        # Create watcher
        watcher = FileSystemWatcher(str(vault), check_interval=1)
        
        # Drop a file
        test_file = watcher.inbox / "test_drop.txt"
        test_file.write_text("Process this file")
        
        # Watcher detects and creates action
        items = watcher.check_for_updates()
        assert len(items) == 1
        
        # Create action file
        meta_path = watcher.create_action_file(items[0])
        
        # Verify action file structure
        content = meta_path.read_text()
        assert "---" in content  # Has frontmatter
        assert "type: file_drop" in content
        assert "pending" in content
        assert "test_drop.txt" in content
        
        # Verify file was copied
        copied = list(watcher.needs_action.glob("FILE_*_test_drop.txt"))
        assert len(copied) == 1
