"""Skill models for AI Employee Vault system."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class AgentSkill(BaseModel):
    """
    Represents a defined agent skill capability.

    Attributes:
        name: Unique skill identifier
        purpose: What this skill does
        input_format: Expected input structure (JSON Schema or markdown template)
        output_format: Produced output structure
        invocation_method: How to call this skill
        expected_behavior: Normal operation description
        failure_handling: Error recovery steps
        enabled: Whether skill is active
        execution_count: Number of times skill has been executed
        last_executed: Last execution timestamp
    """
    name: str
    purpose: str
    input_format: str
    output_format: str
    invocation_method: str
    expected_behavior: str
    failure_handling: str
    enabled: bool = True
    execution_count: int = 0
    last_executed: Optional[datetime] = None

    def mark_executed(self) -> None:
        """Mark the skill as executed."""
        self.execution_count += 1
        self.last_executed = datetime.utcnow()


class SkillResult(BaseModel):
    """
    Result of a skill execution.

    Attributes:
        skill_name: Name of the skill that was executed
        success: Whether execution was successful
        output: Skill output data
        error_message: Error details if failed
        duration_ms: Execution time in milliseconds
        files_created: List of files created/modified
        files_moved: State transitions performed
    """
    skill_name: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_ms: int = 0
    files_created: List[str] = Field(default_factory=list)
    files_moved: List[str] = Field(default_factory=list)

    @classmethod
    def from_success(
        cls,
        skill_name: str,
        output: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0,
        files_created: Optional[List[str]] = None,
        files_moved: Optional[List[str]] = None
    ) -> "SkillResult":
        """Create a successful skill result."""
        return cls(
            skill_name=skill_name,
            success=True,
            output=output,
            duration_ms=duration_ms,
            files_created=files_created or [],
            files_moved=files_moved or []
        )

    @classmethod
    def from_failure(
        cls,
        skill_name: str,
        error_message: str,
        duration_ms: int = 0
    ) -> "SkillResult":
        """Create a failed skill result."""
        return cls(
            skill_name=skill_name,
            success=False,
            error_message=error_message,
            duration_ms=duration_ms
        )
