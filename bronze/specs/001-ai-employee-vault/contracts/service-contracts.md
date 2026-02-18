# API Contracts: AI Employee Vault

**Branch**: `001-ai-employee-vault` | **Date**: 2026-02-16

## Internal Service Contracts

This document defines the internal Python module contracts for the AI Employee Vault system. These are not external HTTP APIs but internal service interfaces that must be implemented consistently.

---

## 1. Vault Service Contract

**Module**: `ai_employee.services.vault`

### Interface

```python
class VaultService:
    """
    Manages all vault file operations with atomic transitions.
    """
    
    async def create_vault_structure(self) -> bool:
        """
        Create required vault directories and files.
        
        Returns:
            True if structure created successfully or already exists
        
        Raises:
            VaultCreationError: If directories cannot be created
        """
        pass
    
    async def read_item(self, item_id: str) -> VaultItem | None:
        """
        Read a vault item by ID.
        
        Args:
            item_id: SHA256 hash of item content
            
        Returns:
            VaultItem if found, None otherwise
        """
        pass
    
    async def write_item(self, item: VaultItem, state: VaultState) -> str:
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
        pass
    
    async def move_item(self, item_id: str, from_state: VaultState, 
                        to_state: VaultState) -> bool:
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
        """
        pass
    
    async def list_items(self, state: VaultState) -> list[VaultItem]:
        """
        List all items in a given state.
        
        Args:
            state: State folder to list
            
        Returns:
            List of VaultItem objects
        """
        pass
```

### Error Codes

| Error | Code | Description |
|-------|------|-------------|
| `VaultCreationError` | VLT-001 | Cannot create vault directories |
| `FileLockTimeout` | VLT-002 | File lock not available after retries |
| `InvalidMarkdown` | VLT-003 | Content fails markdown validation |
| `ItemNotFound` | VLT-004 | Item ID not found in specified state |
| `InvalidTransition` | VLT-005 | State transition not allowed |

---

## 2. Watcher Service Contract

**Module**: `ai_employee.services.watcher`

### Interface

```python
from abc import ABC, abstractmethod
from typing import Callable, AsyncIterator

class WatcherService(ABC):
    """
    Abstract base for input source watchers.
    """
    
    @abstractmethod
    async def start(self, callback: Callable[[InputEvent], None]) -> None:
        """
        Start watching for new inputs.
        
        Args:
            callback: Function to call when new input detected
            
        Raises:
            WatcherConfigError: If configuration is invalid
            WatcherConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """
        Stop watching and cleanup resources.
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if watcher is connected and healthy.
        
        Returns:
            True if healthy
        """
        pass


class InputEvent:
    """Represents a detected input event."""
    
    def __init__(self, source: str, content: str, metadata: dict):
        self.source = source          # 'gmail' or 'filesystem'
        self.content = content        # Raw content
        self.metadata = metadata      # Source-specific metadata
        self.timestamp = datetime.utcnow()
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique event ID from content hash."""
        pass
```

### Gmail Watcher Implementation

```python
class GmailWatcher(WatcherService):
    """IMAP-based Gmail watcher."""
    
    def __init__(self, config: GmailConfig):
        self.config = config
        self.mail: imaplib.IMAP4_SSL | None = None
    
    async def start(self, callback: Callable[[InputEvent], None]) -> None:
        """
        Connect to Gmail and poll for new messages.
        
        Config requirements:
        - IMAP server and port
        - Email address and app password
        - Folder to monitor (default: INBOX)
        - Poll interval (default: 30s)
        """
        pass
```

### Filesystem Watcher Implementation

```python
class FilesystemWatcher(WatcherService):
    """Watchdog-based filesystem watcher."""
    
    def __init__(self, config: FilesystemConfig):
        self.config = config
        self.observer: Observer | None = None
    
    async def start(self, callback: Callable[[InputEvent], None]) -> None:
        """
        Start filesystem monitoring.
        
        Config requirements:
        - Watch path (must exist)
        - File pattern (glob)
        - Recursive flag
        - Ignore patterns
        """
        pass
```

### Error Codes

| Error | Code | Description |
|-------|------|-------------|
| `WatcherConfigError` | WTC-001 | Invalid watcher configuration |
| `WatcherConnectionError` | WTC-002 | Cannot connect to source |
| `WatcherTimeout` | WTC-003 | Watcher failed to respond |

---

## 3. Agent Skill Executor Contract

**Module**: `ai_employee.services.executor`

### Interface

```python
class SkillExecutor:
    """
    Executes agent skills with validation and error handling.
    """
    
    async def load_skills(self) -> list[AgentSkill]:
        """
        Load all skills from Agent_Skills.md.
        
        Returns:
            List of AgentSkill objects
            
        Raises:
            SkillParseError: If skills file is malformed
        """
        pass
    
    async def execute_skill(self, skill_name: str, 
                           input_data: dict) -> SkillResult:
        """
        Execute a skill with validated input.
        
        Args:
            skill_name: Name of skill to execute
            input_data: Validated input data
            
        Returns:
            SkillResult with output and metadata
            
        Raises:
            SkillNotFound: If skill doesn't exist
            SkillValidationError: If input doesn't match schema
            SkillExecutionError: If skill execution fails
        """
        pass
    
    async def validate_input(self, skill: AgentSkill, 
                            input_data: dict) -> bool:
        """
        Validate input against skill's input format.
        
        Args:
            skill: Skill definition
            input_data: Data to validate
            
        Returns:
            True if valid
            
        Raises:
            SkillValidationError: Detailed validation error
        """
        pass
    
    async def validate_output(self, skill: AgentSkill, 
                             output_data: any) -> bool:
        """
        Validate output against skill's output format.
        
        Returns:
            True if valid
            
        Raises:
            SkillValidationError: Detailed validation error
        """
        pass
```

### Skill Result

```python
class SkillResult:
    """Result of skill execution."""
    
    def __init__(self, 
                 success: bool,
                 output: any,
                 duration_ms: int,
                 error: str | None = None):
        self.success = success
        self.output = output
        self.duration_ms = duration_ms
        self.error = error
        self.timestamp = datetime.utcnow()
```

### Error Codes

| Error | Code | Description |
|-------|------|-------------|
| `SkillNotFound` | SKL-001 | Skill name not found |
| `SkillParseError` | SKL-002 | Cannot parse skills file |
| `SkillValidationError` | SKL-003 | Input/output validation failed |
| `SkillExecutionError` | SKL-004 | Skill execution failed |

---

## 4. Dashboard Logger Contract

**Module**: `ai_employee.services.logger`

### Interface

```python
class DashboardLogger:
    """
    Manages operational logging to Dashboard.md.
    """
    
    async def log_entry(self, entry: LogEntry) -> None:
        """
        Append a log entry to Dashboard.md.
        
        Args:
            entry: LogEntry to append
            
        Raises:
            LogWriteError: If cannot write to dashboard
        """
        pass
    
    async def get_recent_logs(self, 
                             limit: int = 100) -> list[LogEntry]:
        """
        Get recent log entries.
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            List of LogEntry objects (newest first)
        """
        pass
    
    async def archive_old_logs(self, 
                              cutoff_date: datetime) -> str:
        """
        Archive logs older than cutoff date.
        
        Args:
            cutoff_date: Entries before this date will be archived
            
        Returns:
            Archive file path
            
        Raises:
            LogArchiveError: If archiving fails
        """
        pass
```

### Log Entry

```python
class LogEntry:
    """Single log entry for Dashboard.md."""
    
    def __init__(self,
                 timestamp: datetime,
                 trigger_event: str,
                 skill_executed: str | None,
                 file_moved: str | None,
                 outcome: LogOutcome,
                 error_message: str | None = None,
                 duration_ms: int | None = None):
        self.timestamp = timestamp
        self.trigger_event = trigger_event
        self.skill_executed = skill_executed
        self.file_moved = file_moved
        self.outcome = outcome
        self.error_message = error_message
        self.duration_ms = duration_ms
    
    def to_markdown_row(self) -> str:
        """Convert to markdown table row."""
        pass
```

### Log Outcome Enum

```python
class LogOutcome(str, Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"
    SKIPPED = "Skipped"
```

### Error Codes

| Error | Code | Description |
|-------|------|-------------|
| `LogWriteError` | LOG-001 | Cannot write to Dashboard.md |
| `LogArchiveError` | LOG-002 | Cannot archive logs |

---

## 5. Idempotency Registry Contract

**Module**: `ai_employee.services.registry`

### Interface

```python
class IdempotencyRegistry:
    """
    Tracks processed items to prevent duplicate processing.
    """
    
    async def is_processed(self, content_hash: str) -> bool:
        """
        Check if content has already been processed.
        
        Args:
            content_hash: SHA256 hash of content
            
        Returns:
            True if already processed
        """
        pass
    
    async def mark_processed(self, 
                            content_hash: str, 
                            item_id: str,
                            source: str) -> None:
        """
        Mark content as processed.
        
        Args:
            content_hash: SHA256 hash
            item_id: VaultItem ID
            source: 'gmail' or 'filesystem'
            
        Raises:
            RegistryWriteError: If cannot update registry
        """
        pass
    
    async def get_stats(self) -> RegistryStats:
        """
        Get registry statistics.
        
        Returns:
            RegistryStats object
        """
        pass
```

### Registry Stats

```python
class RegistryStats:
    def __init__(self,
                 total_processed: int,
                 today_count: int,
                 oldest_entry: datetime,
                 storage_size_bytes: int):
        self.total_processed = total_processed
        self.today_count = today_count
        self.oldest_entry = oldest_entry
        self.storage_size_bytes = storage_size_bytes
```

### Error Codes

| Error | Code | Description |
|-------|------|-------------|
| `RegistryWriteError` | REG-001 | Cannot update registry |
| `RegistryCorruption` | REG-002 | Registry file is corrupted |

---

## Data Flow Contracts

### Input Processing Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Watcher   │────▶│  Idempotency │────▶│   Skill     │
│  (detects)  │     │   Registry   │     │  Executor   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   (skip if   │     │   Vault     │
                    │  duplicate)  │     │  Service    │
                    └──────────────┘     └─────────────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  Dashboard  │
                                         │   Logger    │
                                         └─────────────┘
```

### Contract Invariants

1. **All services MUST log to Dashboard** after completing operations
2. **Idempotency check MUST precede skill execution**
3. **Vault operations MUST be atomic** (no partial writes)
4. **All errors MUST be logged** with appropriate error codes
5. **State transitions MUST be validated** before execution
