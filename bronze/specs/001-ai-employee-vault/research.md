# Research: AI Employee Vault — Bronze Tier

**Branch**: `001-ai-employee-vault` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)

## Technical Context Resolution

### Language/Version: Python 3.11+

**Decision**: Python 3.11+ managed via UV

**Rationale**:
- UV provides fast, reliable Python project management
- Python has excellent libraries for file system monitoring, email processing, and markdown handling
- Qwen CLI integration works seamlessly with Python scripts
- Strong ecosystem for local AI automation tasks

**Alternatives Considered**:
- Node.js: Good for file operations but less mature for email processing
- Rust: Excellent performance but higher complexity for rapid prototyping
- Go: Good choice but Python has better AI/ML library support

---

### Primary Dependencies

**Decision**:
- `watchdog` - Filesystem monitoring for input source
- `imaplib` / `email` (stdlib) - Gmail monitoring via IMAP
- `markdown` / `mistune` - Markdown parsing and generation
- `pydantic` - Data validation and settings management
- `rich` - CLI output formatting
- `click` / `typer` - CLI interface (optional, may use Qwen CLI directly)

**Rationale**:
- Minimal dependencies to maintain simplicity
- Standard library usage where possible (imaplib, email, json)
- Watchdog is the de facto standard for cross-platform file monitoring
- Pydantic provides robust validation for agent skill definitions

**Alternatives Considered**:
- `inotify` (Linux-only) vs `watchdog` (cross-platform) → watchdog chosen for portability
- Custom markdown parsing vs `markdown` library → library chosen for reliability

---

### Storage: Filesystem-based (Obsidian Vault)

**Decision**: Local filesystem storage with markdown files

**Rationale**:
- Obsidian vault is filesystem-based by design
- No database required for Bronze tier (max 1GB vault, 50 daily inputs)
- Markdown files are human-readable and version-control friendly
- Simple file operations (read/write/move) suffice for task state management

**Storage Structure**:
```
AI_Employee_Vault/
├── Inbox/           # Newly processed inputs
├── Needs_Action/    # Items requiring further processing
├── Done/            # Completed items
├── Dashboard.md     # Operational log
├── Company_Handbook.md  # Business rules
└── Agent_Skills.md  # Skill definitions
```

---

### Testing: pytest

**Decision**: pytest with standard test structure

**Rationale**:
- Industry standard for Python testing
- Excellent fixture support for vault state setup
- Integration with UV: `uv run pytest`
- Supports contract, integration, and unit tests

**Test Structure**:
```
tests/
├── contract/        # Agent skill contract tests
├── integration/     # Vault operations, watcher integration
└── unit/           # Individual function tests
```

---

### Target Platform: Linux (WSL2 compatible)

**Decision**: Linux-first development (WSL2 on Windows)

**Rationale**:
- User environment is WSL2 (evidenced by `/mnt/d/` path)
- Filesystem monitoring works reliably on Linux
- Qwen CLI and UV both work natively on Linux
- No Docker/containerization required (per spec FR-008)

**Compatibility Notes**:
- File paths use POSIX style
- File locking via `fcntl` (Linux) or `flock`
- Watchdog supports Linux inotify backend

---

### Performance Goals

**Decision**:
- Input detection latency: <30 seconds (per SC-003)
- File operations: <1 second per operation
- Concurrent operations: Support up to 5 (per spec)
- Memory usage: <200MB during normal operation

**Rationale**:
- Derived from success criteria and scale assumptions
- 50 daily inputs = ~0.0006 inputs/second average
- 30-second detection window provides ample processing time
- Local-only processing eliminates network latency concerns

---

### Constraints

**Decision**:
- All processing must occur locally (no cloud APIs except Gmail IMAP)
- No external data transmission (privacy requirement)
- Must work within Qwen CLI execution model
- UV-managed Python environment for reproducibility

**Rationale**:
- Security & privacy requirements from spec
- FR-010: System MUST operate entirely locally
- FR-011: System MUST run via Qwen CLI and UV

---

### Scale/Scope

**Decision**:
- Max vault size: 1GB (per spec)
- Daily input volume: 50 inputs
- Concurrent operations: 5
- File count: Up to 10,000 markdown files

**Rationale**:
- Directly from spec's "Data Scale Assumptions"
- Bronze tier is foundation - designed for single-user personal automation
- Scalability to higher tiers (Silver, Gold) addressed in future phases

---

## Integration Patterns

### Filesystem Watcher Pattern

**Pattern**: Observer pattern with debounce

**Implementation**:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InputWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.md'):
            trigger_processing(event.src_path)
```

**Debounce Strategy**:
- Wait 500ms after file creation before processing
- Prevents processing incomplete writes
- Use file lock to ensure exclusive access during read

---

### Gmail IMAP Monitoring Pattern

**Pattern**: Polling with IDLE extension

**Implementation**:
```python
import imaplib
import email

class GmailWatcher:
    def __init__(self, email, app_password):
        self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
        self.mail.login(email, app_password)
    
    def check_new_mail(self):
        self.mail.select('inbox')
        status, messages = self.mail.search(None, 'UNSEEN')
        return messages
```

**Security Notes**:
- Requires Gmail App Password (not main password)
- Credentials stored in environment variables or encrypted config
- IMAP connection uses SSL/TLS

---

### Task State Machine Pattern

**Pattern**: Finite State Machine for file transitions

**States**: `Inbox` → `Needs_Action` → `Done`

**Transitions**:
```
Inbox --(requires_action)--> Needs_Action
Needs_Action --(processing_complete)--> Done
Inbox --(no_action_needed)--> Done (direct)
```

**Implementation**:
- File move operations are atomic on POSIX filesystems
- Use temporary files during write to prevent partial reads
- Log all transitions to Dashboard.md

---

### Agent Skill Execution Pattern

**Pattern**: Command pattern with validation

**Skill Definition Structure** (from FR-013):
```markdown
## Skill: [Name]
- **Purpose**: [What this skill does]
- **Input Format**: [Expected input structure]
- **Output Format**: [Produced output structure]
- **Invocation Method**: [How to call this skill]
- **Expected Behavior**: [Normal operation description]
- **Failure Handling Notes**: [Error recovery steps]
```

**Execution Flow**:
1. Parse input from source (file/email)
2. Validate input against skill's Input Format
3. Execute skill logic
4. Validate output against Output Format
5. Write output to vault
6. Log to Dashboard.md
7. Move file to next state

---

## Best Practices

### File Locking

**Pattern**: Advisory locking with `fcntl`

```python
import fcntl

def read_file_locked(path):
    with open(path, 'r') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock
        content = f.read()
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return content

def write_file_locked(path, content):
    with open(path, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        f.write(content)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

---

### Idempotency Pattern

**Strategy**: Content-addressable operations

**Implementation**:
- Hash input content to detect duplicates
- Maintain processed-items registry (simple JSON file)
- Before processing, check if hash already exists
- Skip if already processed; log as "duplicate skipped"

```python
import hashlib

def get_content_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()
```

---

### Error Handling Pattern

**Strategy**: Retry with exponential backoff + circuit breaker

```python
import time
from functools import wraps

def retry_with_backoff(max_attempts=3, base_delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TransientError as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
        return wrapper
    return decorator
```

**Circuit Breaker**:
- Track failure count per operation type
- After 5 consecutive failures, open circuit for 60 seconds
- Log circuit state changes to Dashboard.md

---

### Logging Pattern

**Strategy**: Append-only markdown log

**Dashboard.md Format**:
```markdown
# Operational Dashboard

## Activity Log

| Timestamp | Trigger Event | Skill Executed | File Moved | Outcome |
|-----------|---------------|----------------|------------|---------|
| 2026-02-16 10:30:00 | Gmail: "Meeting Notes" | ProcessEmail | Inbox→Needs_Action | Success |
| 2026-02-16 10:31:00 | File: task-001.md | ExtractTasks | Needs_Action→Done | Success |
```

**Log Rotation**:
- Archive logs monthly to `Archive/YYYY-MM.md`
- Keep current month in Dashboard.md
- Archive triggered when log exceeds 1000 entries

---

## Technology Choices Summary

| Component | Choice | Justification |
|-----------|--------|---------------|
| Language | Python 3.11+ | UV support, rich ecosystem, Qwen CLI integration |
| File Watcher | watchdog | Cross-platform, mature, low overhead |
| Email Access | imaplib (stdlib) | No extra dependencies, SSL support |
| Markdown | markdown | Simple, reliable, well-maintained |
| Validation | pydantic | Type safety, clear error messages |
| CLI | typer | Modern, type-annotated, Qwen-friendly |
| Testing | pytest | Industry standard, great fixtures |
| File Locking | fcntl | POSIX standard, reliable |
| State Management | Filesystem moves | Simple, atomic, observable |

---

## Unresolved Questions

None. All technical clarifications resolved for Bronze tier implementation.

---

## References

- **Spec**: `/specs/001-ai-employee-vault/spec.md`
- **Constitution**: `/.specify/memory/constitution.md`
- **Qwen CLI**: Version 0.10.3 (verified)
- **UV**: Version 0.9.13 (verified)
