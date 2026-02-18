"""Unit tests for Skill Executor."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.ai_employee.models.skill import AgentSkill, SkillResult
from src.ai_employee.models.vault import VaultState
from src.ai_employee.services.vault import VaultService
from src.ai_employee.services.logger import DashboardLogger
from src.ai_employee.services.executor import SkillExecutor
from src.ai_employee.errors import (
    SkillNotFound,
    SkillExecutionError,
    SkillValidationError,
)


@pytest.fixture
def temp_vault():
    """Create temporary vault directory."""
    temp_dir = tempfile.mkdtemp()
    vault_path = Path(temp_dir) / "AI_Employee_Vault"
    yield vault_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def vault_service(temp_vault):
    """Create VaultService for testing."""
    service = VaultService(str(temp_vault))
    service.create_vault_structure()
    return service


@pytest.fixture
def dashboard_logger(temp_vault):
    """Create DashboardLogger for testing."""
    return DashboardLogger(str(temp_vault / "Dashboard.md"))


@pytest.fixture
def skills_path(temp_vault):
    """Create Agent_Skills.md for testing."""
    skills_file = temp_vault / "Agent_Skills.md"
    skills_file.write_text(
        "# Agent Skills\n\n"
        "## Skill: ProcessFile\n\n"
        "- **Purpose**: Process markdown files from filesystem\n"
        "- **Input Format**: File path to markdown file\n"
        "- **Output Format**: Markdown file in Inbox/\n"
        "- **Invocation Method**: python -m ai_employee.skills.process_file\n"
        "- **Expected Behavior**: Reads file, creates vault item\n"
        "- **Failure Handling Notes**: Log error, skip processing\n\n"
        "## Skill: ProcessEmail\n\n"
        "- **Purpose**: Process emails from Gmail\n"
        "- **Input Format**: Email data JSON\n"
        "- **Output Format**: Markdown file in Inbox/\n"
        "- **Invocation Method**: python -m ai_employee.skills.process_email\n"
        "- **Expected Behavior**: Creates vault item from email\n"
        "- **Failure Handling Notes**: Log error, retry\n"
    )
    return skills_file


@pytest.fixture
def executor(vault_service, dashboard_logger, skills_path):
    """Create SkillExecutor for testing."""
    return SkillExecutor(
        vault_service=vault_service,
        dashboard_logger=dashboard_logger,
        skills_path=str(skills_path)
    )


class TestAgentSkill:
    """T073: Tests for AgentSkill model."""

    def test_create_agent_skill(self):
        """T073: Verify AgentSkill can be created with required fields."""
        skill = AgentSkill(
            name="TestSkill",
            purpose="Test purpose",
            input_format="JSON schema",
            output_format="Markdown",
            invocation_method="python -m test",
            expected_behavior="Does something",
            failure_handling="Log error"
        )
        assert skill.name == "TestSkill"
        assert skill.enabled is True
        assert skill.execution_count == 0

    def test_skill_mark_executed(self):
        """T073: Verify mark_executed() updates stats."""
        skill = AgentSkill(
            name="TestSkill",
            purpose="Test",
            input_format="JSON",
            output_format="Markdown",
            invocation_method="test",
            expected_behavior="Test",
            failure_handling="Test"
        )

        assert skill.execution_count == 0
        assert skill.last_executed is None

        skill.mark_executed()

        assert skill.execution_count == 1
        assert skill.last_executed is not None


class TestSkillResult:
    """T074: Tests for SkillResult model."""

    def test_create_success_result(self):
        """T074: Verify successful SkillResult creation."""
        result = SkillResult.from_success(
            skill_name="TestSkill",
            output={"key": "value"},
            duration_ms=100,
            files_created=["/path/to/file.md"],
            files_moved=["→ Inbox"]
        )

        assert result.success is True
        assert result.skill_name == "TestSkill"
        assert result.output == {"key": "value"}
        assert result.duration_ms == 100
        assert result.files_created == ["/path/to/file.md"]
        assert result.files_moved == ["→ Inbox"]

    def test_create_failure_result(self):
        """T074: Verify failed SkillResult creation."""
        result = SkillResult.from_failure(
            skill_name="TestSkill",
            error_message="Something went wrong",
            duration_ms=50
        )

        assert result.success is False
        assert result.skill_name == "TestSkill"
        assert result.error_message == "Something went wrong"
        assert result.duration_ms == 50
        assert result.output is None


class TestSkillExecutor:
    """T066-T072: Tests for SkillExecutor service."""

    def test_load_skills_from_file(self, executor):
        """T067: Verify skills are loaded from Agent_Skills.md."""
        skills = executor.list_skills()
        assert len(skills) == 2

        skill_names = [s.name for s in skills]
        assert "ProcessFile" in skill_names
        assert "ProcessEmail" in skill_names

    def test_get_skill(self, executor):
        """T067: Verify get_skill() returns correct skill."""
        skill = executor.get_skill("ProcessFile")
        assert skill is not None
        assert skill.name == "ProcessFile"
        assert "Process markdown files" in skill.purpose

    def test_get_unknown_skill(self, executor):
        """T066: Verify get_skill() returns None for unknown skill."""
        skill = executor.get_skill("UnknownSkill")
        assert skill is None

    def test_validate_input_success(self, executor, tmp_path):
        """T068: Verify input validation passes for valid input."""
        # Create a test file that exists
        test_file = tmp_path / "valid.md"
        test_file.write_text("# Test")
        
        skill = executor.get_skill("ProcessFile")
        result = executor.validate_input(skill, {"file_path": str(test_file)})
        assert result is True

    def test_validate_input_none(self, executor):
        """T068: Verify input validation fails for None input."""
        skill = executor.get_skill("ProcessFile")
        with pytest.raises(SkillValidationError):
            executor.validate_input(skill, None)

    def test_validate_input_missing_file(self, executor, tmp_path):
        """T068: Verify input validation fails for non-existent file."""
        skill = executor.get_skill("ProcessFile")
        with pytest.raises(SkillValidationError):
            executor.validate_input(skill, {"file_path": "/nonexistent/file.md"})

    def test_validate_output_success(self, executor):
        """T069: Verify output validation passes."""
        skill = executor.get_skill("ProcessFile")
        result = executor.validate_output(skill, {"item_id": "abc123"})
        assert result is True

    def test_execute_process_file_success(self, executor, tmp_path):
        """T070: Verify ProcessFile skill executes successfully."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Content\n\nThis is test content.")

        result = executor.execute_skill(
            skill_name="ProcessFile",
            input_data={"file_path": str(test_file)}
        )

        assert result.success is True
        assert result.skill_name == "ProcessFile"
        assert "item_id" in result.output
        assert len(result.files_created) == 1
        assert "Inbox" in result.files_moved[0]

    def test_execute_process_file_duplicate(self, executor, tmp_path):
        """T070: Verify ProcessFile skill handles duplicates."""
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test Content\n\nThis is test content.")

        # Process first time
        result1 = executor.execute_skill(
            skill_name="ProcessFile",
            input_data={"file_path": str(test_file)}
        )
        assert result1.success is True

        # Process second time (duplicate)
        result2 = executor.execute_skill(
            skill_name="ProcessFile",
            input_data={"file_path": str(test_file)}
        )
        assert result2.success is True
        assert result2.output.get("skipped") is True
        assert result2.output.get("reason") == "duplicate"

    def test_execute_process_file_missing_path(self, executor):
        """T071: Verify ProcessFile skill fails with missing file_path."""
        result = executor.execute_skill(
            skill_name="ProcessFile",
            input_data={"content": "test"}
        )

        assert result.success is False
        assert "file_path" in result.error_message

    def test_execute_skill_not_found(self, executor):
        """T071: Verify execute_skill() raises SkillNotFound."""
        with pytest.raises(SkillNotFound):
            executor.execute_skill(
                skill_name="NonExistentSkill",
                input_data={}
            )

    def test_execute_process_email_success(self, executor):
        """T070/T072: Verify ProcessEmail skill executes successfully."""
        email_data = {
            "from": "sender @example.com",
            "subject": "Test Email",
            "body": "This is the email body.",
            "received_at": "2026-02-16T10:30:00Z",
            "message_id": "<test-123 @gmail.com>"
        }

        result = executor.execute_skill(
            skill_name="ProcessEmail",
            input_data=email_data
        )

        assert result.success is True
        assert result.skill_name == "ProcessEmail"
        assert "item_id" in result.output
        assert len(result.files_created) == 1

    def test_execute_process_email_missing_field(self, executor):
        """T071: Verify ProcessEmail skill fails with missing fields."""
        email_data = {
            "from": "sender @example.com",
            # Missing subject, body, message_id
        }

        result = executor.execute_skill(
            skill_name="ProcessEmail",
            input_data=email_data
        )

        assert result.success is False
        assert "Missing required field" in result.error_message

    def test_skill_execution_updates_stats(self, executor, tmp_path):
        """T084: Verify execution count is tracked."""
        test_file = tmp_path / "test.md"
        test_file.write_text("# Test")

        skill = executor.get_skill("ProcessFile")
        assert skill.execution_count == 0

        executor.execute_skill(
            skill_name="ProcessFile",
            input_data={"file_path": str(test_file)}
        )

        # Refresh skill from executor
        skill = executor.get_skill("ProcessFile")
        assert skill.execution_count == 1
        assert skill.last_executed is not None


class TestSkillContract:
    """T070/T072: Contract tests for skill input/output."""

    def test_process_file_input_contract(self, executor, tmp_path):
        """T070: Verify ProcessFile input meets contract (SC-004)."""
        test_file = tmp_path / "contract_test.md"
        test_file.write_text("# Contract Test")

        # Valid input should work
        result = executor.execute_skill(
            skill_name="ProcessFile",
            input_data={"file_path": str(test_file)}
        )
        assert result.success is True

    def test_process_file_output_contract(self, executor, tmp_path):
        """T070: Verify ProcessFile output meets contract (SC-004)."""
        test_file = tmp_path / "output_contract.md"
        test_file.write_text("# Output Contract")

        result = executor.execute_skill(
            skill_name="ProcessFile",
            input_data={"file_path": str(test_file)}
        )

        # Output should have required fields
        assert result.output is not None
        assert "item_id" in result.output
        assert "state" in result.output or "skipped" in result.output

    def test_process_email_input_contract(self, executor):
        """T070: Verify ProcessEmail input meets contract (SC-004)."""
        email_data = {
            "from": "sender @example.com",
            "subject": "Contract Test",
            "body": "Testing input contract.",
            "message_id": "<contract-test @gmail.com>"
        }

        result = executor.execute_skill(
            skill_name="ProcessEmail",
            input_data=email_data
        )
        assert result.success is True

    def test_process_email_output_contract(self, executor):
        """T070: Verify ProcessEmail output meets contract (SC-004)."""
        email_data = {
            "from": "sender @example.com",
            "subject": "Output Contract",
            "body": "Testing output contract.",
            "message_id": "<output-contract @gmail.com>"
        }

        result = executor.execute_skill(
            skill_name="ProcessEmail",
            input_data=email_data
        )

        # Output should have required fields
        assert result.output is not None
        assert "item_id" in result.output
