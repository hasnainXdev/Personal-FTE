# Quickstart: AI Employee Vault — Bronze Tier

**Branch**: `001-ai-employee-vault` | **Date**: 2026-02-16

## Overview

This quickstart guide helps you set up and run the AI Employee Vault system in under 10 minutes.

## Prerequisites

- [x] Python 3.11+ (managed via UV)
- [x] UV package manager (`uv --version` to verify)
- [x] Qwen CLI (`qwen --version` to verify)
- [x] Git (optional, for version control)

## Installation

### Step 1: Initialize UV Project

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/bronze

# Initialize UV project (if not already done)
uv init ai_employee
cd ai_employee

# Add required dependencies
uv add watchdog pydantic rich typer markdown
uv add --dev pytest pytest-asyncio
```

### Step 2: Create Vault Structure

```bash
# Create the required vault directories
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done}

# Create initial files
cat > AI_Employee_Vault/Dashboard.md << 'EOF'
# Operational Dashboard

## Activity Log

| Timestamp | Trigger Event | Skill Executed | File Moved | Outcome |
|-----------|---------------|----------------|------------|---------|
EOF

cat > AI_Employee_Vault/Company_Handbook.md << 'EOF'
# Company Handbook

## Mission
The AI Employee Vault automates routine information processing tasks.

## Business Rules
1. All processing occurs locally (no cloud transmission)
2. Privacy is paramount - encrypt sensitive data
3. Idempotency is required - no duplicate processing
4. All actions must be logged to Dashboard.md
EOF

cat > AI_Employee_Vault/Agent_Skills.md << 'EOF'
# Agent Skills

## Skill: ProcessEmail
- **Purpose**: Extract actionable items from Gmail messages
- **Input Format**: JSON with from, subject, body, received_at
- **Output Format**: Markdown file in Inbox/
- **Invocation Method**: python -m ai_employee.skills.process_email
- **Expected Behavior**: Creates vault item with extracted content
- **Failure Handling Notes**: Log error, move to Needs_Action for review

## Skill: ProcessFile
- **Purpose**: Process markdown files from filesystem input
- **Input Format**: File path to markdown file
- **Output Format**: Processed markdown in appropriate vault folder
- **Invocation Method**: python -m ai_employee.skills.process_file
- **Expected Behavior**: Reads file, categorizes, moves to correct folder
- **Failure Handling Notes**: Log error, keep in Inbox for manual review
EOF
```

### Step 3: Create Configuration

```bash
# Create config directory
mkdir -p AI_Employee_Vault/.ai_employee

# Create watcher configuration
cat > AI_Employee_Vault/.ai_employee/config.json << 'EOF'
{
  "watcher_type": "filesystem",
  "enabled": true,
  "poll_interval_seconds": 30,
  "source_config": {
    "watch_path": "/mnt/d/it-course/hackathons/personal-FTE/bronze/AI_Employee_Vault/Inbox",
    "file_pattern": "*.md",
    "recursive": false,
    "ignore_patterns": [".*", "*.tmp", "*.swp"]
  }
}
EOF
```

### Step 4: Create Project Structure

```bash
# Create source directories
mkdir -p src/ai_employee/{services,skills,models}
mkdir -p tests/{unit,integration,contract}

# Create __init__.py files
touch src/ai_employee/__init__.py
touch src/ai_employee/services/__init__.py
touch src/ai_employee/skills/__init__.py
touch src/ai_employee/models/__init__.py
```

### Step 5: Create Core Models

Create `src/ai_employee/models/vault.py`:

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib

class VaultState(str, Enum):
    INBOX = "inbox"
    NEEDS_ACTION = "needs_action"
    DONE = "done"

class Source(str, Enum):
    GMAIL = "gmail"
    FILESYSTEM = "filesystem"

class VaultItem(BaseModel):
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
    def from_content(cls, content: str, source: Source, source_path: str, 
                     title: str) -> "VaultItem":
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
```

### Step 6: Create Main Entry Point

Create `src/ai_employee/main.py`:

```python
import asyncio
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def start():
    """Start the AI Employee Vault system."""
    console.print("[green]Starting AI Employee Vault...[/green]")
    # TODO: Initialize watchers and start event loop
    console.print("[yellow]Implementation in progress[/yellow]")

@app.command()
def status():
    """Check system status."""
    console.print("[green]AI Employee Vault System[/green]")
    # TODO: Add health checks
    console.print("[yellow]Status check not yet implemented[/yellow]")

@app.command()
def process(input_path: str):
    """Manually process a single input file."""
    console.print(f"[green]Processing {input_path}...[/green]")
    # TODO: Add manual processing logic
    console.print("[yellow]Processing not yet implemented[/yellow]")

if __name__ == "__main__":
    app()
```

### Step 7: Update pyproject.toml

Ensure `pyproject.toml` has the entry point:

```toml
[project]
name = "ai-employee-vault"
version = "0.1.0"
description = "Autonomous AI Employee for Obsidian vault automation"
requires-python = ">=3.11"
dependencies = [
    "watchdog>=4.0.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",
    "typer>=0.9.0",
    "markdown>=3.5.0",
]

[project.scripts]
ai-employee = "ai_employee.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Running the System

### Start the Watcher

```bash
# Using UV
uv run ai-employee start

# Or directly with Python
uv run python -m ai_employee.main start
```

### Check Status

```bash
uv run ai-employee status
```

### Process a Test File

```bash
# Create a test input
cat > AI_Employee_Vault/Inbox/test-input.md << 'EOF'
# Test Input

This is a test file for the AI Employee Vault.

## Action Required
Please process this file and move it to Done.
EOF

# Process manually
uv run ai-employee process AI_Employee_Vault/Inbox/test-input.md
```

## Verification Checklist

- [ ] Vault structure exists (`Inbox/`, `Needs_Action/`, `Done/`)
- [ ] Dashboard.md has header and table
- [ ] Company_Handbook.md exists
- [ ] Agent_Skills.md has at least one skill defined
- [ ] Config file exists at `.ai_employee/config.json`
- [ ] `uv run ai-employee status` runs without errors
- [ ] Qwen CLI is available: `qwen --version`
- [ ] UV is available: `uv --version`

## Next Steps

1. **Implement Vault Service**: Create `src/ai_employee/services/vault.py`
2. **Implement Watcher Service**: Create `src/ai_employee/services/watcher.py`
3. **Implement Skill Executor**: Create `src/ai_employee/services/executor.py`
4. **Add Tests**: Create test files in `tests/` directory
5. **Configure Gmail** (optional): Update config for Gmail monitoring

## Troubleshooting

### "Command not found: ai-employee"

Ensure you're using `uv run`:
```bash
uv run ai-employee start
```

### "Vault structure not found"

Run the setup commands in Step 2 to create directories.

### "No module named 'ai_employee'"

Ensure you're in the project directory and dependencies are installed:
```bash
cd ai_employee
uv install
```

## Support

- **Spec**: `/specs/001-ai-employee-vault/spec.md`
- **Data Model**: `/specs/001-ai-employee-vault/data-model.md`
- **Contracts**: `/specs/001-ai-employee-vault/contracts/service-contracts.md`
