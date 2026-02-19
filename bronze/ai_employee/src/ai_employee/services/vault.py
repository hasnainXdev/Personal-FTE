"""Vault service for managing all vault file operations."""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import markdown

# Cross-platform file locking
if sys.platform == 'win32':
    import msvcrt
else:
    import fcntl

from ..models.vault import VaultItem, VaultState, Source
from ..errors import (
    VaultCreationError,
    FileLockTimeout,
    InvalidMarkdown,
    ItemNotFound,
    InvalidTransition,
)


class VaultService:
    """
    Manages all vault file operations with atomic transitions.
    
    This service handles:
    - Creating vault directory structure
    - Reading/writing vault items with file locking
    - Atomic state transitions (moving files between folders)
    - Listing items by state
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        VaultState.INBOX: [VaultState.NEEDS_ACTION, VaultState.DONE],
        VaultState.NEEDS_ACTION: [VaultState.DONE],
        VaultState.DONE: [],  # Terminal state
    }
    
    def __init__(self, vault_path: str):
        """
        Initialize the vault service.
        
        Args:
            vault_path: Absolute path to the AI_Employee_Vault directory
        """
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
    
    def create_vault_structure(self) -> bool:
        """
        Create required vault directories and files.
        
        Returns:
            True if structure created successfully or already exists
            
        Raises:
            VaultCreationError: If directories cannot be created
        """
        try:
            # Create state directories
            for dir_path in [self.inbox_path, self.needs_action_path, self.done_path]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create Dashboard.md if not exists
            dashboard_path = self.vault_path / "Dashboard.md"
            if not dashboard_path.exists():
                dashboard_path.write_text(
                    "# Operational Dashboard\n\n"
                    "## Activity Log\n\n"
                    "| Timestamp | Trigger Event | Skill Executed | File Moved | Outcome |\n"
                    "|-----------|---------------|----------------|------------|---------|\n"
                )
            
            # Create Company_Handbook.md if not exists (T032)
            handbook_path = self.vault_path / "Company_Handbook.md"
            if not handbook_path.exists():
                handbook_path.write_text(
                    "# Company Handbook\n\n"
                    "## Mission\n\n"
                    "The AI Employee Vault is an autonomous AI system that automates routine information "
                    "processing tasks within an Obsidian vault. It monitors input sources, organizes "
                    "information into structured task states, and executes predefined agent skills.\n\n"
                    "## Business Rules\n\n"
                    "1. **Local Processing**: All processing occurs locally (no cloud transmission)\n"
                    "2. **Privacy**: Privacy is paramount - encrypt sensitive data at rest\n"
                    "3. **Idempotency**: Idempotency is required - no duplicate processing\n"
                    "4. **Logging**: All actions must be logged to Dashboard.md\n"
                    "5. **State Management**: All items follow the state workflow: Inbox → Needs_Action → Done\n"
                    "6. **Error Handling**: Errors are logged and items are moved to Needs_Action for manual review\n\n"
                    "## Operating Hours\n\n"
                    "- **Uptime Target**: 99% during business hours (Monday-Friday, 9AM-6PM)\n"
                    "- **Recovery Time**: Maximum 4-hour recovery time after system failure\n"
                    "- **Backup**: Automatic daily backups of vault data recommended\n\n"
                    "## Scale Constraints\n\n"
                    "- **Max Vault Size**: 1GB total\n"
                    "- **Daily Input Volume**: Up to 50 new inputs per day\n"
                    "- **Concurrent Operations**: Support for up to 5 concurrent operations\n"
                    "- **Max File Size**: 10MB per file\n\n"
                    "## Contact\n\n"
                    "For issues or questions, refer to Dashboard.md for operational logs.\n"
                )

            # Create Agent_Skills.md if not exists (T033)
            skills_path = self.vault_path / "Agent_Skills.md"
            if not skills_path.exists():
                skills_path.write_text(
                    "# Agent Skills\n\n"
                    "This document defines all agent skills that the AI Employee can execute.\n"
                    "Each skill follows a standardized format with input/output specifications.\n\n"
                    "---\n\n"
                    "## Skill: ProcessFile\n\n"
                    "- **Purpose**: Process markdown files from filesystem input source\n"
                    "- **Input Format**:\n"
                    "  ```json\n"
                    "  {\n"
                    '    "file_path": "/absolute/path/to/file.md",\n'
                    '    "content": "markdown content string"\n'
                    "  }\n"
                    "  ```\n"
                    "- **Output Format**: Markdown file created in appropriate vault folder (Inbox/)\n"
                    "- **Invocation Method**: `python -m ai_employee.skills.process_file <file_path>`\n"
                    "- **Expected Behavior**:\n"
                    "  1. Read the input file\n"
                    "  2. Validate markdown content\n"
                    "  3. Generate unique ID (SHA256 hash of content)\n"
                    "  4. Check for duplicates (idempotency)\n"
                    "  5. Write to Inbox/ folder\n"
                    "  6. Log operation to Dashboard.md\n"
                    "- **Failure Handling Notes**:\n"
                    "  - If file not found: Log error, skip processing\n"
                    "  - If invalid markdown: Log error, move to Needs_Action for manual review\n"
                    "  - If duplicate detected: Log as skipped, no action taken\n"
                    "  - If write fails: Log error, retry with exponential backoff (3 attempts)\n\n"
                    "---\n\n"
                    "## Skill: ProcessEmail (Gmail Support)\n\n"
                    "- **Purpose**: Process emails from Gmail inbox\n"
                    "- **Input Format**:\n"
                    "  ```json\n"
                    "  {\n"
                    '    "from": "sender @example.com",\n'
                    '    "subject": "Email subject line",\n'
                    '    "body": "Email body content",\n'
                    '    "received_at": "2026-02-16T10:30:00Z",\n'
                    '    "message_id": "<unique-message-id @gmail.com>"\n'
                    "  }\n"
                    "  ```\n"
                    "- **Output Format**: Markdown file created in Inbox/ with email metadata\n"
                    "- **Invocation Method**: `python -m ai_employee.skills.process_email`\n"
                    "- **Expected Behavior**:\n"
                    "  1. Connect to Gmail via IMAP\n"
                    "  2. Fetch unread emails\n"
                    "  3. Parse email content and metadata\n"
                    "  4. Create markdown file with email content\n"
                    "  5. Write to Inbox/ folder\n"
                    "  6. Mark email as read\n"
                    "  7. Log operation to Dashboard.md\n"
                    "- **Failure Handling Notes**:\n"
                    "  - If IMAP connection fails: Retry with exponential backoff\n"
                    "  - If email parse fails: Log error, skip email\n"
                    "  - If write fails: Log error, retain email as unread for retry\n\n"
                    "---\n\n"
                    "## Skill: ExtractTasks\n\n"
                    "- **Purpose**: Extract actionable tasks from markdown content\n"
                    "- **Input Format**: Markdown file path containing potential tasks\n"
                    "- **Output Format**: Structured task list in markdown format\n"
                    "- **Invocation Method**: `python -m ai_employee.skills.extract_tasks <file_path>`\n"
                    "- **Expected Behavior**:\n"
                    "  1. Read input markdown file\n"
                    "  2. Identify task-like patterns (checkboxes, action items)\n"
                    "  3. Extract and format as structured task list\n"
                    "  4. Update original file with extracted tasks\n"
                    "  5. Move file to Needs_Action/ if tasks require action\n"
                    "  6. Log operation to Dashboard.md\n"
                    "- **Failure Handling Notes**:\n"
                    "  - If no tasks found: Log as informational, move to Done/\n"
                    "  - If parse fails: Log error, keep in Inbox for manual review\n\n"
                    "---\n\n"
                    "## Adding New Skills\n\n"
                    "To add a new agent skill:\n\n"
                    "1. Create a new section in this file with the skill definition\n"
                    "2. Implement the skill in `src/ai_employee/skills/` directory\n"
                    "3. Register the skill in the skill executor\n"
                    "4. Test the skill with sample inputs\n"
                    "5. Update documentation\n\n"
                    "### Skill Template\n\n"
                    "```markdown\n"
                    "## Skill: [Skill Name]\n\n"
                    "- **Purpose**: [What this skill does]\n"
                    "- **Input Format**: [Expected input structure with example]\n"
                    "- **Output Format**: [Produced output structure with example]\n"
                    "- **Invocation Method**: [How to call this skill]\n"
                    "- **Expected Behavior**: [Step-by-step normal operation]\n"
                    "- **Failure Handling Notes**: [Error recovery steps]\n"
                    "```\n"
                )
            
            return True
            
        except (OSError, PermissionError) as e:
            raise VaultCreationError(
                f"Failed to create vault structure: {e}",
                {"path": str(self.vault_path)}
            )
    
    def _get_state_path(self, state: VaultState) -> Path:
        """Get the directory path for a given state."""
        state_paths = {
            VaultState.INBOX: self.inbox_path,
            VaultState.NEEDS_ACTION: self.needs_action_path,
            VaultState.DONE: self.done_path,
        }
        return state_paths[state]
    
    def _validate_markdown(self, content: str) -> bool:
        """Validate that content is valid markdown."""
        try:
            markdown.markdown(content)
            return True
        except Exception:
            return False
    
    def _acquire_lock(self, file_handle, exclusive: bool = False, timeout: float = 5.0) -> bool:
        """
        Acquire file lock with timeout (cross-platform).

        Args:
            file_handle: Open file handle
            exclusive: If True, acquire exclusive lock; otherwise shared
            timeout: Maximum time to wait for lock in seconds

        Returns:
            True if lock acquired

        Raises:
            FileLockTimeout: If lock cannot be acquired within timeout
        """
        start_time = datetime.now()

        while True:
            try:
                if sys.platform == 'win32':
                    # Windows: use msvcrt for locking
                    mode = msvcrt.LK_LOCK if exclusive else msvcrt.LK_NBLCK
                    file_size = file_handle.seek(0, 2)  # Get file size
                    file_handle.seek(0)
                    msvcrt.locking(file_handle.fileno(), mode, file_size)
                    return True
                else:
                    # Unix/Linux: use fcntl
                    lock_type = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
                    fcntl.flock(file_handle.fileno(), lock_type | fcntl.LOCK_NB)
                    return True
            except (IOError, OSError, OSError):
                if (datetime.now() - start_time).total_seconds() > timeout:
                    return False
    
    def read_item(self, item_id: str) -> Optional[VaultItem]:
        """
        Read a vault item by ID.
        
        Args:
            item_id: SHA256 hash of item content
            
        Returns:
            VaultItem if found, None otherwise
        """
        # Search in all state folders
        for state in VaultState:
            state_path = self._get_state_path(state)
            file_path = state_path / f"{item_id}.md"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        if not self._acquire_lock(f, exclusive=False):
                            raise FileLockTimeout(
                                f"Cannot acquire lock for reading: {file_path}"
                            )
                        content = f.read()
                    
                    # Parse frontmatter if present, otherwise use content as-is
                    title = file_path.stem  # Use filename as title
                    return VaultItem(
                        id=item_id,
                        title=title,
                        source=Source.FILESYSTEM,
                        source_path=str(file_path),
                        current_state=state,
                        content=content
                    )
                except (IOError, OSError) as e:
                    raise FileLockTimeout(f"Failed to read item: {e}")
        
        return None
    
    def write_item(self, item: VaultItem, state: VaultState) -> str:
        """
        Write a vault item to appropriate state folder.
        
        Args:
            item: VaultItem to write
            state: Target state (inbox, needs_action, done)
            
        Returns:
            File path where item was written
            
        Raises:
            FileLockTimeout: If file cannot be locked
            InvalidMarkdown: If content is not valid markdown
        """
        # Validate markdown
        if not self._validate_markdown(item.content):
            raise InvalidMarkdown(
                "Content is not valid markdown",
                {"item_id": item.id}
            )
        
        state_path = self._get_state_path(state)
        file_path = state_path / f"{item.id}.md"
        
        try:
            # Write atomically using temp file
            temp_path = file_path.with_suffix('.md.tmp')
            
            with open(temp_path, 'w') as f:
                if not self._acquire_lock(f, exclusive=True):
                    raise FileLockTimeout(
                        f"Cannot acquire lock for writing: {file_path}"
                    )
                f.write(item.content)
            
            # Atomic rename
            temp_path.rename(file_path)
            return str(file_path)
            
        except (IOError, OSError) as e:
            # Cleanup temp file if exists
            if temp_path.exists():
                temp_path.unlink()
            raise FileLockTimeout(f"Failed to write item: {e}")
    
    def move_item(self, item_id: str, from_state: VaultState, to_state: VaultState) -> bool:
        """
        Atomically move item between state folders.
        
        Args:
            item_id: ID of item to move
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if move successful
            
        Raises:
            ItemNotFound: If item doesn't exist in from_state
            InvalidTransition: If transition is not allowed
            FileLockTimeout: If file cannot be locked during move
        """
        # Validate transition
        if to_state not in self.VALID_TRANSITIONS.get(from_state, []):
            raise InvalidTransition(
                f"Invalid transition from {from_state.value} to {to_state.value}",
                {"item_id": item_id, "from": from_state.value, "to": to_state.value}
            )
        
        from_path = self._get_state_path(from_state) / f"{item_id}.md"
        to_path = self._get_state_path(to_state) / f"{item_id}.md"
        
        if not from_path.exists():
            raise ItemNotFound(
                f"Item not found in {from_state.value}",
                {"item_id": item_id, "state": from_state.value}
            )
        
        try:
            # Atomic move
            shutil.move(str(from_path), str(to_path))
            return True
        except (IOError, OSError) as e:
            raise FileLockTimeout(f"Failed to move item: {e}")
    
    def list_items(self, state: VaultState) -> List[VaultItem]:
        """
        List all items in a given state.
        
        Args:
            state: State folder to list
            
        Returns:
            List of VaultItem objects
        """
        state_path = self._get_state_path(state)
        items = []
        
        if not state_path.exists():
            return items
        
        for file_path in state_path.glob("*.md"):
            if file_path.suffix == '.tmp':
                continue  # Skip temp files
            
            try:
                content = file_path.read_text()
                item = VaultItem(
                    id=file_path.stem,
                    title=file_path.stem,
                    source=Source.FILESYSTEM,
                    source_path=str(file_path),
                    current_state=state,
                    content=content
                )
                items.append(item)
            except (IOError, OSError):
                # Skip files that can't be read
                continue
        
        return items
    
    def item_exists(self, item_id: str) -> bool:
        """Check if an item exists in any state folder."""
        for state in VaultState:
            state_path = self._get_state_path(state)
            if (state_path / f"{item_id}.md").exists():
                return True
        return False
    
    def get_item_state(self, item_id: str) -> Optional[VaultState]:
        """Get the current state of an item."""
        for state in VaultState:
            state_path = self._get_state_path(state)
            if (state_path / f"{item_id}.md").exists():
                return state
        return None
