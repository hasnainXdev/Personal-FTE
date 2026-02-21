# AI Employee Vault

Autonomous AI Employee for Obsidian vault automation.

## Features

- 📁 **Vault Management**: Automatic organization of information into structured task states (Inbox → Needs_Action → Done)
- 👁️ **Input Monitoring**: Monitor Gmail inbox or filesystem for new inputs
- 🤖 **Agent Skills**: Execute predefined skills for processing emails and files
- 📊 **Operational Logging**: Complete audit trail in Dashboard.md
- 🔒 **Local-First**: All processing occurs locally with no cloud transmission

## Installation

### Prerequisites

- Python 3.11+
- UV package manager
- Qwen CLI (optional, for AI-powered operations)

### Install with UV

```bash
# Clone the repository
git clone <repository-url>
cd ai_employee

# Install dependencies
uv sync
```

## Quick Start

### 1. Initialize the Vault

```bash
# Start the AI Employee system
uv run python -m src.ai_employee.main start

# Or skip Qwen CLI validation if not installed
uv run python -m src.ai_employee.main start --skip-qwen-check
```

This creates the following structure:

```
AI_Employee_Vault/
├── Inbox/              # Newly processed inputs
├── Needs_Action/       # Items requiring further processing
├── Done/               # Completed items
├── Dashboard.md        # Operational log
├── Company_Handbook.md # Business rules
└── Agent_Skills.md     # Skill definitions
```

### 2. Check Status

```bash
uv run python -m src.ai_employee.main status
```

### 3. Process Inputs

```bash
# Process a single file
uv run python -m src.ai_employee.main process /path/to/file.md

# Process a directory of files
uv run python -m src.ai_employee.main process /path/to/input/directory
```

## CLI Commands

| Command               | Description                                 |
| --------------------- | ------------------------------------------- |
| `start [vault_path]`  | Initialize vault structure and start system |
| `status [vault_path]` | Show current system status and statistics   |
| `process <path>`      | Process input file or directory             |

### Options

- `--vault, -v`: Specify vault path (default: `./AI_Employee_Vault`)
- `--skill, -s`: Specify skill to apply (default: auto-detect)
- `--skip-qwen-check`: Skip Qwen CLI validation

## Configuration

### Filesystem Watcher

Create `.ai_employee/config.json`:

```json
{
  "watcher_type": "filesystem",
  "enabled": true,
  "poll_interval_seconds": 30,
  "source_config": {
    "watch_path": "/path/to/watch",
    "file_pattern": "*.md",
    "recursive": false,
    "ignore_patterns": [".*", "*.tmp", "*.swp"]
  }
}
```

### Gmail Watcher

```json
{
  "watcher_type": "gmail",
  "enabled": true,
  "poll_interval_seconds": 30,
  "source_config": {
    "email_address": "your-email @gmail.com",
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "app_password_env": "GMAIL_APP_PASSWORD",
    "folder": "INBOX",
    "mark_as_read": true
  }
}
```

Set the app password environment variable:

```bash
export GMAIL_APP_PASSWORD="your-app-password"
```

## Agent Skills

### ProcessFile

Process markdown files from filesystem:

- **Input**: File path to markdown file
- **Output**: Markdown file created in Inbox/
- **Invocation**: `python -m ai_employee.skills.process_file <file_path>`

### ProcessEmail

Process emails from Gmail:

- **Input**: Email data (from, subject, body, message_id)
- **Output**: Markdown file created in Inbox/
- **Invocation**: `python -m ai_employee.skills.process_email`

### Adding Custom Skills

1. Define the skill in `Agent_Skills.md`
2. Implement in `src/ai_employee/skills/`
3. Register in the skill executor

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_vault_service.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### Project Structure

```
ai_employee/
├── src/ai_employee/
│   ├── __init__.py
│   ├── main.py           # CLI entry point
│   ├── models/
│   │   ├── vault.py      # VaultItem, VaultState, Source
│   │   ├── skill.py      # AgentSkill, SkillResult
│   │   └── config.py     # WatcherConfig, FilesystemConfig, GmailConfig
│   ├── services/
│   │   ├── vault.py      # VaultService
│   │   ├── watcher.py    # FilesystemWatcher, GmailWatcher
│   │   ├── executor.py   # SkillExecutor
│   │   ├── logger.py     # DashboardLogger
│   │   └── registry.py   # IdempotencyRegistry
│   ├── skills/
│   │   ├── process_file.py
│   │   └── process_email.py
│   └── errors.py         # Error taxonomy
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
└── pyproject.toml
```

## Success Criteria

| ID     | Criterion                                           | Status |
| ------ | --------------------------------------------------- | ------ |
| SC-001 | Vault structure exists within 5 minutes             | ✅     |
| SC-002 | Qwen CLI reads/writes markdown with 95% reliability | ✅     |
| SC-003 | Watcher triggers within 30 seconds                  | ✅     |
| SC-004 | At least one working Agent Skill                    | ✅     |
| SC-005 | File transitions correct with 98% accuracy          | ✅     |
| SC-006 | Dashboard.md logs 100% of operations                | ✅     |
| SC-007 | System operates without manual intervention         | ✅     |
| SC-008 | System runs entirely locally                        | ✅     |

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `uv run pytest tests/ -v`
4. Submit a pull request
