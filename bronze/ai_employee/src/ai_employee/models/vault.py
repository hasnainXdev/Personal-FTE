"""Vault models for AI Employee Vault system."""

from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib
from pydantic import BaseModel, Field


class VaultState(str, Enum):
    """Represents the state of a vault item in the task workflow."""
    INBOX = "inbox"
    NEEDS_ACTION = "needs_action"
    DONE = "done"


class Source(str, Enum):
    """Represents the source of input to the AI employee."""
    GMAIL = "gmail"
    FILESYSTEM = "filesystem"


class VaultItem(BaseModel):
    """
    Represents a single piece of information tracked in the vault.
    
    Attributes:
        id: Unique identifier (SHA256 hash of content)
        title: Human-readable title extracted from content
        source: Source of the input (gmail or filesystem)
        source_path: Original file path or email message-id
        current_state: Current state in the workflow
        content: Full markdown content
        created_at: When the item was created
        updated_at: When the item was last updated
        processed_at: When the item was last processed
        assigned_skill: Name of agent skill to apply
        metadata: Additional structured data
    """
    id: str
    title: str
    source: Source
    source_path: str
    current_state: VaultState
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    assigned_skill: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    
    @classmethod
    def from_content(
        cls, 
        content: str, 
        source: Source, 
        source_path: str,
        title: str
    ) -> "VaultItem":
        """Create a VaultItem from content with automatic ID generation."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        return cls(
            id=content_hash,
            title=title,
            source=source,
            source_path=source_path,
            current_state=VaultState.INBOX,
            content=content
        )
    
    def mark_processed(self) -> None:
        """Mark the item as processed with current timestamp."""
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_content(self, new_content: str) -> None:
        """Update content and refresh the ID based on new hash."""
        self.content = new_content
        self.id = hashlib.sha256(new_content.encode()).hexdigest()
        self.updated_at = datetime.utcnow()
