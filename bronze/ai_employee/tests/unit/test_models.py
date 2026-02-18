"""Unit tests for models."""

import pytest
from datetime import datetime

from src.ai_employee.models.vault import VaultItem, VaultState, Source
from src.ai_employee.models.skill import AgentSkill, SkillResult


class TestVaultItem:
    """Tests for VaultItem model."""

    def test_create_vault_item(self):
        """Verify VaultItem can be created with all fields."""
        item = VaultItem(
            id="test-hash",
            title="Test Item",
            source=Source.FILESYSTEM,
            source_path="/test/path.md",
            current_state=VaultState.INBOX,
            content="# Test Content"
        )
        assert item.id == "test-hash"
        assert item.title == "Test Item"
        assert item.source == Source.FILESYSTEM
        assert item.current_state == VaultState.INBOX

    def test_from_content(self):
        """Verify from_content() creates item with automatic ID."""
        item = VaultItem.from_content(
            content="# Test",
            source=Source.FILESYSTEM,
            source_path="/test.md",
            title="Test"
        )
        assert item.id is not None
        assert len(item.id) == 64  # SHA256 hex length
        assert item.current_state == VaultState.INBOX

    def test_mark_processed(self):
        """Verify mark_processed() updates timestamps."""
        item = VaultItem(
            id="test",
            title="Test",
            source=Source.FILESYSTEM,
            source_path="/test.md",
            current_state=VaultState.INBOX,
            content="# Test"
        )
        assert item.processed_at is None
        
        item.mark_processed()
        assert item.processed_at is not None

    def test_update_content(self):
        """Verify update_content() changes hash."""
        item = VaultItem(
            id="original-hash",
            title="Test",
            source=Source.FILESYSTEM,
            source_path="/test.md",
            current_state=VaultState.INBOX,
            content="# Original"
        )
        original_id = item.id
        
        item.update_content("# Updated content")
        assert item.content == "# Updated content"
        assert item.id != original_id  # Hash changed


class TestVaultState:
    """Tests for VaultState enum."""

    def test_state_values(self):
        """Verify state values."""
        assert VaultState.INBOX.value == "inbox"
        assert VaultState.NEEDS_ACTION.value == "needs_action"
        assert VaultState.DONE.value == "done"


class TestSource:
    """Tests for Source enum."""

    def test_source_values(self):
        """Verify source values."""
        assert Source.GMAIL.value == "gmail"
        assert Source.FILESYSTEM.value == "filesystem"


class TestAgentSkillModel:
    """Tests for AgentSkill model."""

    def test_create_skill(self):
        """Verify AgentSkill creation."""
        skill = AgentSkill(
            name="TestSkill",
            purpose="Test purpose",
            input_format="JSON",
            output_format="Markdown",
            invocation_method="test",
            expected_behavior="Test",
            failure_handling="Test"
        )
        assert skill.name == "TestSkill"
        assert skill.enabled is True
        assert skill.execution_count == 0


class TestSkillResultModel:
    """Tests for SkillResult model."""

    def test_success_result(self):
        """Verify successful result."""
        result = SkillResult.from_success(
            skill_name="Test",
            output={"key": "value"},
            duration_ms=100
        )
        assert result.success is True
        assert result.output == {"key": "value"}

    def test_failure_result(self):
        """Verify failed result."""
        result = SkillResult.from_failure(
            skill_name="Test",
            error_message="Error",
            duration_ms=50
        )
        assert result.success is False
        assert result.error_message == "Error"
