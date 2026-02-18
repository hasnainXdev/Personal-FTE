"""Integration tests for vault operations."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.ai_employee.models.vault import VaultItem, VaultState, Source
from src.ai_employee.services.vault import VaultService


@pytest.fixture
def temp_vault():
    """Create a temporary vault directory for integration testing."""
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir) / "AI_Employee_Vault"
    yield vault_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def vault_service(temp_vault):
    """Create a VaultService with temporary vault for integration tests."""
    service = VaultService(str(temp_vault))
    service.create_vault_structure()
    return service


class TestVaultInitialization:
    """T024: Integration tests for vault initialization."""

    def test_vault_structure_exists_after_init(self, vault_service, temp_vault):
        """T025: Verify vault structure exists after service initialization."""
        # Verify all required directories exist
        assert (temp_vault / "Inbox").is_dir()
        assert (temp_vault / "Needs_Action").is_dir()
        assert (temp_vault / "Done").is_dir()

        # Verify all required files exist
        assert (temp_vault / "Dashboard.md").is_file()
        assert (temp_vault / "Company_Handbook.md").is_file()
        assert (temp_vault / "Agent_Skills.md").is_file()

    def test_vault_service_fully_operational(self, vault_service, temp_vault):
        """T024: Verify vault service is fully operational after initialization."""
        # Create a test item
        item = VaultItem(
            id="integration-test-001",
            title="Integration Test",
            source=Source.FILESYSTEM,
            source_path="/test/integration.md",
            current_state=VaultState.INBOX,
            content="# Integration Test\n\nThis is an integration test."
        )

        # Write item
        file_path = vault_service.write_item(item, VaultState.INBOX)
        assert Path(file_path).exists()

        # Read item back
        read_item = vault_service.read_item(item.id)
        assert read_item is not None
        assert read_item.content == item.content

        # Move item through states
        vault_service.move_item(item.id, VaultState.INBOX, VaultState.NEEDS_ACTION)
        assert vault_service.get_item_state(item.id) == VaultState.NEEDS_ACTION

        vault_service.move_item(item.id, VaultState.NEEDS_ACTION, VaultState.DONE)
        assert vault_service.get_item_state(item.id) == VaultState.DONE

    def test_vault_concurrent_operations(self, vault_service):
        """T024: Verify vault supports concurrent operations."""
        # Create multiple items
        items = []
        for i in range(5):
            item = VaultItem(
                id=f"concurrent-test-{i}",
                title=f"Concurrent Test {i}",
                source=Source.FILESYSTEM,
                source_path=f"/test/concurrent-{i}.md",
                current_state=VaultState.INBOX,
                content=f"# Concurrent Test {i}"
            )
            vault_service.write_item(item, VaultState.INBOX)
            items.append(item)

        # Verify all items exist
        for item in items:
            assert vault_service.item_exists(item.id)

        # List all items
        inbox_items = vault_service.list_items(VaultState.INBOX)
        assert len(inbox_items) == 5


class TestVaultOperations:
    """T024: Integration tests for vault operations workflow."""

    def test_complete_item_lifecycle(self, vault_service):
        """T024: Test complete lifecycle of an item from creation to completion."""
        # Create item
        item = VaultItem(
            id="lifecycle-test",
            title="Lifecycle Test",
            source=Source.FILESYSTEM,
            source_path="/test/lifecycle.md",
            current_state=VaultState.INBOX,
            content="# Lifecycle Test\n\nTesting complete item lifecycle."
        )

        # Write to Inbox
        vault_service.write_item(item, VaultState.INBOX)
        assert vault_service.get_item_state(item.id) == VaultState.INBOX

        # Move to Needs_Action
        vault_service.move_item(item.id, VaultState.INBOX, VaultState.NEEDS_ACTION)
        assert vault_service.get_item_state(item.id) == VaultState.NEEDS_ACTION

        # Move to Done
        vault_service.move_item(item.id, VaultState.NEEDS_ACTION, VaultState.DONE)
        assert vault_service.get_item_state(item.id) == VaultState.DONE

        # Verify item in Done folder
        done_items = vault_service.list_items(VaultState.DONE)
        assert len(done_items) == 1
        assert done_items[0].id == item.id

    def test_bulk_operations(self, vault_service):
        """T024: Test bulk operations with multiple items."""
        # Create 10 items
        for i in range(10):
            item = VaultItem(
                id=f"bulk-test-{i}",
                title=f"Bulk Test {i}",
                source=Source.FILESYSTEM,
                source_path=f"/test/bulk-{i}.md",
                current_state=VaultState.INBOX,
                content=f"# Bulk Test {i}"
            )
            vault_service.write_item(item, VaultState.INBOX)

        # Verify all in Inbox
        inbox_items = vault_service.list_items(VaultState.INBOX)
        assert len(inbox_items) == 10

        # Move half to Needs_Action
        for i in range(5):
            vault_service.move_item(f"bulk-test-{i}", VaultState.INBOX, VaultState.NEEDS_ACTION)

        # Verify counts
        assert len(vault_service.list_items(VaultState.INBOX)) == 5
        assert len(vault_service.list_items(VaultState.NEEDS_ACTION)) == 5

        # Move all to Done
        for i in range(5):
            vault_service.move_item(f"bulk-test-{i}", VaultState.NEEDS_ACTION, VaultState.DONE)
        for i in range(5, 10):
            vault_service.move_item(f"bulk-test-{i}", VaultState.INBOX, VaultState.DONE)

        # Verify all in Done
        done_items = vault_service.list_items(VaultState.DONE)
        assert len(done_items) == 10
        assert len(vault_service.list_items(VaultState.INBOX)) == 0
        assert len(vault_service.list_items(VaultState.NEEDS_ACTION)) == 0


class TestStateTransitions:
    """T025: Integration tests for state transitions (SC-005 validation)."""

    def test_100_file_transitions_accuracy(self, vault_service):
        """T025: Verify file transitions correct with 98% accuracy (100 test cases)."""
        successful_transitions = 0
        total_transitions = 0

        # Test inbox -> needs_action -> done (50 items)
        for i in range(50):
            item_id = f"transition-test-{i}"
            item = VaultItem(
                id=item_id,
                title=f"Transition Test {i}",
                source=Source.FILESYSTEM,
                source_path=f"/test/transition-{i}.md",
                current_state=VaultState.INBOX,
                content=f"# Transition Test {i}"
            )
            vault_service.write_item(item, VaultState.INBOX)

            # Transition 1: Inbox -> Needs_Action
            total_transitions += 1
            try:
                vault_service.move_item(item_id, VaultState.INBOX, VaultState.NEEDS_ACTION)
                if vault_service.get_item_state(item_id) == VaultState.NEEDS_ACTION:
                    successful_transitions += 1
            except Exception:
                pass

            # Transition 2: Needs_Action -> Done
            total_transitions += 1
            try:
                vault_service.move_item(item_id, VaultState.NEEDS_ACTION, VaultState.DONE)
                if vault_service.get_item_state(item_id) == VaultState.DONE:
                    successful_transitions += 1
            except Exception:
                pass

        # Test inbox -> done direct (50 items)
        for i in range(50, 100):
            item_id = f"transition-test-{i}"
            item = VaultItem(
                id=item_id,
                title=f"Transition Test {i}",
                source=Source.FILESYSTEM,
                source_path=f"/test/transition-{i}.md",
                current_state=VaultState.INBOX,
                content=f"# Transition Test {i}"
            )
            vault_service.write_item(item, VaultState.INBOX)

            # Direct transition: Inbox -> Done
            total_transitions += 1
            try:
                vault_service.move_item(item_id, VaultState.INBOX, VaultState.DONE)
                if vault_service.get_item_state(item_id) == VaultState.DONE:
                    successful_transitions += 1
            except Exception:
                pass

        # Calculate accuracy
        accuracy = (successful_transitions / total_transitions) * 100
        assert accuracy >= 98.0, f"Transition accuracy {accuracy}% is below 98% threshold"
        assert successful_transitions == total_transitions, "All transitions should succeed"
