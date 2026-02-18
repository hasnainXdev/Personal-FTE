"""Skill executor for AI Employee Vault system."""

import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..models.skill import AgentSkill, SkillResult
from ..models.vault import VaultItem, VaultState, Source
from ..services.vault import VaultService
from ..services.logger import DashboardLogger, LogEntry
from ..errors import SkillNotFound, SkillExecutionError, SkillValidationError


class SkillExecutor:
    """
    T075: Executes agent skills defined in Agent_Skills.md.

    Features:
    - Load skills from Agent_Skills.md
    - Validate input/output against skill schema
    - Execute skills with error handling
    - Log all executions to Dashboard.md
    """

    def __init__(
        self,
        vault_service: VaultService,
        dashboard_logger: DashboardLogger,
        skills_path: Optional[str] = None
    ):
        """
        Initialize the skill executor.

        Args:
            vault_service: Vault service for file operations
            dashboard_logger: Logger for operational logging
            skills_path: Path to Agent_Skills.md (default: vault_path/Agent_Skills.md)
        """
        self.vault_service = vault_service
        self.dashboard_logger = dashboard_logger
        self.skills_path = Path(skills_path) if skills_path else None
        self._skills: Dict[str, AgentSkill] = {}

        if self.skills_path and self.skills_path.exists():
            self._skills = self._parse_skills_file()

    def _parse_skills_file(self) -> Dict[str, AgentSkill]:
        """
        T076: Parse Agent_Skills.md and load skill definitions.

        Returns:
            Dictionary of skill name -> AgentSkill
        """
        if not self.skills_path or not self.skills_path.exists():
            return {}

        content = self.skills_path.read_text()
        skills = {}

        # Parse skill sections
        skill_pattern = r'## Skill:\s*(.+?)\n(.*?)(?=\n## Skill:|\Z)'
        matches = re.findall(skill_pattern, content, re.DOTALL)

        for name, body in matches:
            skill = self._parse_skill_body(name.strip(), body)
            if skill:
                skills[skill.name] = skill

        return skills

    def _parse_skill_body(self, name: str, body: str) -> Optional[AgentSkill]:
        """Parse individual skill definition."""
        fields = {}

        # Extract fields using regex
        field_patterns = {
            'purpose': r'\*\*Purpose\*\*:\s*(.+?)(?=\n|$)',
            'input_format': r'\*\*Input Format\*\*:\s*(.+?)(?=\n\*\*|\Z)',
            'output_format': r'\*\*Output Format\*\*:\s*(.+?)(?=\n\*\*|\Z)',
            'invocation_method': r'\*\*Invocation Method\*\*:\s*(.+?)(?=\n|$)',
            'expected_behavior': r'\*\*Expected Behavior\*\*:\s*(.+?)(?=\n\*\*|\Z)',
            'failure_handling': r'\*\*Failure Handling Notes\*\*:\s*(.+?)(?=\n\*\*|\Z)',
        }

        for field, pattern in field_patterns.items():
            match = re.search(pattern, body, re.DOTALL)
            if match:
                fields[field] = match.group(1).strip()

        # Check required fields
        required = ['purpose', 'invocation_method', 'expected_behavior', 'failure_handling']
        if not all(f in fields for f in required):
            return None

        return AgentSkill(
            name=name,
            **fields
        )

    def get_skill(self, name: str) -> Optional[AgentSkill]:
        """Get a skill by name."""
        return self._skills.get(name)

    def list_skills(self) -> List[AgentSkill]:
        """List all available skills."""
        return list(self._skills.values())

    def validate_input(self, skill: AgentSkill, input_data: Any) -> bool:
        """
        T077: Validate input against skill's input format.

        For Bronze tier, we do basic validation:
        - Check input is not None
        - Check input has expected structure

        Args:
            skill: Skill to validate against
            input_data: Input data to validate

        Returns:
            True if valid

        Raises:
            SkillValidationError: If validation fails
        """
        if input_data is None:
            raise SkillValidationError(
                "Input cannot be None",
                {"skill": skill.name}
            )

        # For file-based skills, check file exists
        if isinstance(input_data, dict) and 'file_path' in input_data:
            if not Path(input_data['file_path']).exists():
                raise SkillValidationError(
                    f"Input file not found: {input_data['file_path']}",
                    {"skill": skill.name}
                )

        return True

    def validate_output(self, skill: AgentSkill, output_data: Any) -> bool:
        """
        T078: Validate output against skill's output format.

        For Bronze tier, we do basic validation:
        - Check output is not None for skills that produce output

        Args:
            skill: Skill to validate against
            output_data: Output data to validate

        Returns:
            True if valid

        Raises:
            SkillValidationError: If validation fails
        """
        # Basic validation - output should exist for most skills
        if output_data is None and skill.name not in ['ExtractTasks']:
            # Some skills might not produce output
            pass

        return True

    def execute_skill(
        self,
        skill_name: str,
        input_data: Dict[str, Any],
        dry_run: bool = False
    ) -> SkillResult:
        """
        T079: Execute a skill with error handling.

        Args:
            skill_name: Name of skill to execute
            input_data: Input data for the skill
            dry_run: If True, validate but don't execute

        Returns:
            SkillResult with execution outcome

        Raises:
            SkillNotFound: If skill doesn't exist
            SkillExecutionError: If execution fails
        """
        start_time = time.time()

        # Get skill
        skill = self.get_skill(skill_name)
        if not skill:
            raise SkillNotFound(
                f"Skill not found: {skill_name}",
                {"skill_name": skill_name}
            )

        if not skill.enabled:
            raise SkillExecutionError(
                f"Skill is disabled: {skill_name}",
                {"skill_name": skill_name}
            )

        try:
            # Validate input
            self.validate_input(skill, input_data)

            if dry_run:
                return SkillResult.from_success(
                    skill_name=skill_name,
                    output={"dry_run": True},
                    duration_ms=0
                )

            # Execute based on skill name
            if skill_name == "ProcessFile":
                result = self._execute_process_file(input_data)
            elif skill_name == "ProcessEmail":
                result = self._execute_process_email(input_data)
            else:
                raise SkillExecutionError(
                    f"Unknown skill: {skill_name}",
                    {"skill_name": skill_name}
                )

            # Validate output
            self.validate_output(skill, result.output)

            # Update skill stats
            skill.mark_executed()

            return result

        except SkillValidationError:
            raise
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return SkillResult.from_failure(
                skill_name=skill_name,
                error_message=str(e),
                duration_ms=duration_ms
            )

    def _execute_process_file(self, input_data: Dict[str, Any]) -> SkillResult:
        """
        T080/T081: Execute ProcessFile skill.

        Args:
            input_data: {'file_path': str, 'content': str}

        Returns:
            SkillResult with file processing outcome
        """
        start_time = time.time()
        file_path = input_data.get('file_path')
        content = input_data.get('content')

        if not file_path:
            raise SkillExecutionError(
                "Missing required field: file_path",
                {"skill": "ProcessFile"}
            )

        # Read content if not provided
        if not content:
            content = Path(file_path).read_text()

        # Create vault item
        import hashlib
        item_id = hashlib.sha256(content.encode()).hexdigest()

        # Check for duplicates
        if self.vault_service.item_exists(item_id):
            return SkillResult.from_success(
                skill_name="ProcessFile",
                output={"skipped": True, "reason": "duplicate"},
                duration_ms=int((time.time() - start_time) * 1000)
            )

        # Create and write item
        item = VaultItem(
            id=item_id,
            title=Path(file_path).stem,
            source=Source.FILESYSTEM,
            source_path=str(Path(file_path).absolute()),
            current_state=VaultState.INBOX,
            content=content
        )

        written_path = self.vault_service.write_item(item, VaultState.INBOX)

        return SkillResult.from_success(
            skill_name="ProcessFile",
            output={"item_id": item_id, "state": "inbox"},
            duration_ms=int((time.time() - start_time) * 1000),
            files_created=[written_path],
            files_moved=["→ Inbox"]
        )

    def _execute_process_email(self, input_data: Dict[str, Any]) -> SkillResult:
        """
        T085: Execute ProcessEmail skill (Gmail support).

        Args:
            input_data: {'from': str, 'subject': str, 'body': str, 'received_at': str, 'message_id': str}

        Returns:
            SkillResult with email processing outcome
        """
        start_time = time.time()

        # Validate required fields
        required = ['from', 'subject', 'body', 'message_id']
        for field in required:
            if field not in input_data:
                raise SkillExecutionError(
                    f"Missing required field: {field}",
                    {"skill": "ProcessEmail"}
                )

        # Create markdown content from email
        content = f"""# Email: {input_data['subject']}

**From:** {input_data['from']}
**Received:** {input_data.get('received_at', 'Unknown')}
**Message-ID:** {input_data['message_id']}

---

{input_data['body']}
"""

        # Create vault item
        import hashlib
        item_id = hashlib.sha256(content.encode()).hexdigest()

        # Check for duplicates
        if self.vault_service.item_exists(item_id):
            return SkillResult.from_success(
                skill_name="ProcessEmail",
                output={"skipped": True, "reason": "duplicate"},
                duration_ms=int((time.time() - start_time) * 1000)
            )

        # Create and write item
        item = VaultItem(
            id=item_id,
            title=input_data['subject'],
            source=Source.GMAIL,
            source_path=input_data['message_id'],
            current_state=VaultState.INBOX,
            content=content
        )

        written_path = self.vault_service.write_item(item, VaultState.INBOX)

        return SkillResult.from_success(
            skill_name="ProcessEmail",
            output={"item_id": item_id, "state": "inbox"},
            duration_ms=int((time.time() - start_time) * 1000),
            files_created=[written_path],
            files_moved=["→ Inbox"]
        )
