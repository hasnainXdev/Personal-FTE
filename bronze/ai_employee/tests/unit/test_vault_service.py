"""Unit tests for VaultService."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.ai_employee.models.vault import VaultItem, VaultState, Source
from src.ai_employee.services.vault import VaultService
from src.ai_employee.errors import (
    InvalidMarkdown,
    ItemNotFound,
    InvalidTransition,
    FileLockTimeout,
)


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory for testing."""
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir) / "AI_Employee_Vault"
    yield vault_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def vault_service(temp_vault):
    """Create a VaultService with temporary vault."""
    service = VaultService(str(temp_vault))
    service.create_vault_structure()
    return service


class TestVaultCreation:
    """Tests for T021: create_vault_structure() functionality."""

    def test_create_vault_structure_creates_directories(self, vault_service, temp_vault):
        """T021: Verify create_vault_structure() creates Inbox/, Needs_Action/, Done/."""
        assert (temp_vault / "Inbox").exists()
        assert (temp_vault / "Needs_Action").exists()
        assert (temp_vault / "Done").exists()

    def test_create_vault_structure_creates_dashboard(self, vault_service, temp_vault):
        """T021: Verify Dashboard.md is created."""
        dashboard_path = temp_vault / "Dashboard.md"
        assert dashboard_path.exists()
        content = dashboard_path.read_text()
        assert "# Operational Dashboard" in content
        assert "| Timestamp | Trigger Event |" in content

    def test_create_vault_structure_creates_handbook(self, vault_service, temp_vault):
        """T021: Verify Company_Handbook.md is created."""
        handbook_path = temp_vault / "Company_Handbook.md"
        assert handbook_path.exists()
        content = handbook_path.read_text()
        assert "# Company Handbook" in content

    def test_create_vault_structure_creates_skills(self, vault_service, temp_vault):
        """T021: Verify Agent_Skills.md is created."""
        skills_path = temp_vault / "Agent_Skills.md"
        assert skills_path.exists()
        content = skills_path.read_text()
        assert "# Agent Skills" in content
        assert "## Skill: ProcessFile" in content

    def test_create_vault_structure_idempotent(self, vault_service, temp_vault):
        """T021: Verify create_vault_structure() can be called multiple times."""
        # Call again - should not raise
        result = vault_service.create_vault_structure()
        assert result is True


class TestWriteItem:
    """Tests for T022: write_item() functionality."""

    def test_write_item_creates_valid_markdown_file(self, vault_service, temp_vault):
        """T022: Verify write_item() creates valid markdown file in Inbox."""
        item = VaultItem(
            id="test-hash-123",
            title="Test Item",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.INBOX,
            content="# Test Content\n\nThis is test content."
        )

        file_path = vault_service.write_item(item, VaultState.INBOX)

        assert Path(file_path).exists()
        assert file_path == str(temp_vault / "Inbox" / "test-hash-123.md")

        # Verify content
        written_content = Path(file_path).read_text()
        assert written_content == item.content

    def test_write_item_validates_markdown(self, vault_service):
        """T022: Verify write_item() validates markdown content."""
        item = VaultItem(
            id="test-hash-456",
            title="Invalid Item",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.INBOX,
            content="Valid markdown content"
        )

        # Should not raise - content is valid
        vault_service.write_item(item, VaultState.INBOX)

    def test_write_item_to_different_states(self, vault_service, temp_vault):
        """T022: Verify write_item() can write to any state folder."""
        for state in [VaultState.INBOX, VaultState.NEEDS_ACTION, VaultState.DONE]:
            item = VaultItem(
                id=f"test-{state.value}",
                title=f"Test {state.value}",
                source=Source.FILESYSTEM,
                source_path="/test/path.md",
                current_state=state,
                content=f"# Test {state.value}"
            )

            file_path = vault_service.write_item(item, state)
            assert Path(file_path).exists()
            assert state.value in file_path


class TestMoveItem:
    """Tests for T023: move_item() functionality."""

    def test_move_item_inbox_to_needs_action(self, vault_service):
        """T023: Verify move_item() transitions inbox→needs_action."""
        # Create item in Inbox
        item = VaultItem(
            id="move-test-1",
            title="Move Test",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.INBOX,
            content="# Move Test Content"
        )
        vault_service.write_item(item, VaultState.INBOX)

        # Move to Needs_Action
        result = vault_service.move_item(item.id, VaultState.INBOX, VaultState.NEEDS_ACTION)
        assert result is True

        # Verify file moved
        assert not (vault_service.inbox_path / "move-test-1.md").exists()
        assert (vault_service.needs_action_path / "move-test-1.md").exists()

    def test_move_item_needs_action_to_done(self, vault_service):
        """T023: Verify move_item() transitions needs_action→done."""
        # Create item in Needs_Action
        item = VaultItem(
            id="move-test-2",
            title="Move Test",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.NEEDS_ACTION,
            content="# Move Test Content"
        )
        vault_service.write_item(item, VaultState.NEEDS_ACTION)

        # Move to Done
        result = vault_service.move_item(item.id, VaultState.NEEDS_ACTION, VaultState.DONE)
        assert result is True

        # Verify file moved
        assert not (vault_service.needs_action_path / "move-test-2.md").exists()
        assert (vault_service.done_path / "move-test-2.md").exists()

    def test_move_item_inbox_to_done_direct(self, vault_service):
        """T023: Verify move_item() allows inbox→done direct transition."""
        # Create item in Inbox
        item = VaultItem(
            id="move-test-3",
            title="Move Test",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.INBOX,
            content="# Move Test Content"
        )
        vault_service.write_item(item, VaultState.INBOX)

        # Move directly to Done
        result = vault_service.move_item(item.id, VaultState.INBOX, VaultState.DONE)
        assert result is True

        # Verify file moved
        assert (vault_service.done_path / "move-test-3.md").exists()

    def test_move_item_invalid_transition_done_to_inbox(self, vault_service):
        """T023: Verify move_item() rejects invalid transitions (done→inbox)."""
        # Create item in Done
        item = VaultItem(
            id="move-test-4",
            title="Move Test",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.DONE,
            content="# Move Test Content"
        )
        vault_service.write_item(item, VaultState.DONE)

        # Attempt invalid transition
        with pytest.raises(InvalidTransition):
            vault_service.move_item(item.id, VaultState.DONE, VaultState.INBOX)

    def test_move_item_not_found(self, vault_service):
        """T023: Verify move_item() raises ItemNotFound when item doesn't exist."""
        with pytest.raises(ItemNotFound):
            vault_service.move_item("non-existent-id", VaultState.INBOX, VaultState.DONE)


class TestListItems:
    """Tests for listing items by state."""

    def test_list_items_empty_state(self, vault_service):
        """Verify list_items() returns empty list for empty state."""
        items = vault_service.list_items(VaultState.INBOX)
        assert items == []

    def test_list_items_with_items(self, vault_service):
        """Verify list_items() returns all items in state."""
        # Create multiple items in Inbox
        for i in range(3):
            item = VaultItem(
                id=f"list-test-{i}",
                title=f"List Test {i}",
                source=Source.FILESYSTEM,
                source_path="/test/path.md",
                current_state=VaultState.INBOX,
                content=f"# Test {i}"
            )
            vault_service.write_item(item, VaultState.INBOX)

        items = vault_service.list_items(VaultState.INBOX)
        assert len(items) == 3
        assert all(item.current_state == VaultState.INBOX for item in items)


class TestItemExists:
    """Tests for item existence checks."""

    def test_item_exists_true(self, vault_service):
        """Verify item_exists() returns True for existing item."""
        item = VaultItem(
            id="exists-test",
            title="Exists Test",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.INBOX,
            content="# Test"
        )
        vault_service.write_item(item, VaultState.INBOX)

        assert vault_service.item_exists("exists-test") is True

    def test_item_exists_false(self, vault_service):
        """Verify item_exists() returns False for non-existing item."""
        assert vault_service.item_exists("non-existent") is False


class TestGetItemState:
    """Tests for getting item state."""

    def test_get_item_state(self, vault_service):
        """Verify get_item_state() returns correct state."""
        item = VaultItem(
            id="state-test",
            title="State Test",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.INBOX,
            content="# Test"
        )
        vault_service.write_item(item, VaultState.INBOX)

        state = vault_service.get_item_state("state-test")
        assert state == VaultState.INBOX

    def test_get_item_state_not_found(self, vault_service):
        """Verify get_item_state() returns None for non-existing item."""
        state = vault_service.get_item_state("non-existent")
        assert state is None
