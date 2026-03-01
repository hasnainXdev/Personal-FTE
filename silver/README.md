# AI Employee - Silver Tier Orchestration

**Version**: 0.1.0
**Tier**: Silver (Functional Assistant with Orchestration)
**Foundation**: Bronze Tier (Reactive Task Processor)

---

## Overview

Silver Tier upgrades the AI Employee from a reactive task processor to an autonomous functional assistant with:

- **Multi-Channel Input**: Gmail and Filesystem watchers for automatic input capture
- **Structured Planning**: Plan.md generation for complex workflows
- **Human-in-the-Loop**: Approval workflow for high-risk and external actions
- **MCP Server**: Centralized external action boundary (email, LinkedIn, webhooks)
- **Scheduling**: Cron-based autonomous task execution
- **Skill Chaining**: Orchestrator for coordinated multi-skill workflows

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Silver Tier Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Watchers        │  Scheduler      │  Services              │
│  - Gmail         │  - Cron Runner  │  - Plan Generator      │
│  - Filesystem    │  - Daily Summary│  - Approval Request    │
│                  │                 │  - Orchestrator        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Bronze Tier Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Inbox Intake → Task Classifier → State Mover → Summarizer  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      MCP Server                              │
├─────────────────────────────────────────────────────────────┤
│  Email │ LinkedIn │ Webhook │ (All external actions)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- UV package manager
- WSL Ubuntu (for Windows users)
- Bronze Tier operational

### 2. Installation

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver

# Activate UV environment
uv python install 3.11
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required credentials:
- Gmail OAuth (for Gmail watcher)
- SMTP credentials (for email actions)
- LinkedIn access token (for LinkedIn automation)

### 4. Start MCP Server

```bash
cd ai_employee/mcp_server
uv run python -m ai_employee.mcp_server.server
```

Verify:
```bash
curl http://localhost:8765/health
```

### 5. Configure Watchers

```bash
# Test Gmail watcher
uv run python -m ai_employee.watchers.gmail_watcher --test

# Test Filesystem watcher
echo "Test content" > AI_Employee_Vault/Inbox_Drop/test.txt
uv run python -m ai_employee.watchers.filesystem_watcher --test
```

### 6. Configure Scheduling

```bash
# Edit crontab
crontab -e

# Add entries (see Scheduled_Tasks/ for examples)
```

---

## Project Structure

```
silver/
├── ai_employee/                 # Silver Tier code
│   ├── mcp_server/              # MCP server (external actions)
│   │   ├── actions/             # Action handlers
│   │   │   ├── email.py
│   │   │   ├── linkedin.py
│   │   │   └── webhook.py
│   │   ├── logs/                # MCP action logs
│   │   └── __init__.py          # Server definition
│   ├── watchers/                # Input channel watchers
│   │   ├── base_watcher.py      # Abstract base class
│   │   ├── gmail_watcher.py
│   │   └── filesystem_watcher.py
│   ├── scheduler/               # Scheduling layer
│   │   ├── cron_runner.py
│   │   └── daily_summary.py
│   └── services/                # Business logic services
│       ├── plan_generator.py
│       ├── approval_request.py
│       └── orchestrator.py
│
├── AI_Employee_Vault/           # Obsidian vault (immutable structure)
│   ├── Skills/
│   │   ├── Bronze/              # UNCHANGED - foundation
│   │   └── Silver/              # NEW - orchestration skills
│   ├── Inbox/                   # Bronze intake (unchanged)
│   ├── Needs_Action/            # Bronze (unchanged)
│   ├── Done/                    # Bronze (unchanged)
│   ├── Plans/                   # NEW - Plan.md storage
│   ├── Proposed_Actions/        # NEW - approval workflow
│   ├── Scheduled_Tasks/         # NEW - scheduled task configs
│   ├── Logs_Extended/           # NEW - detailed logs
│   └── Dashboard.md             # EXTENDED - new log sections
│
├── specs/002-silver-tier-orchestration/  # Feature documentation
│   ├── spec.md                   # Specification
│   ├── plan.md                   # Implementation plan
│   ├── tasks.md                  # Task breakdown
│   ├── data-model.md             # Entity definitions
│   ├── research.md               # Design decisions
│   ├── quickstart.md             # Setup guide
│   └── contracts/                # API contracts
│
├── .env.example                  # Environment template
├── pyproject.toml                # Python project config
└── README.md                     # This file
```

---

## User Stories

### US1: Multi-Channel Input Processing 🎯 MVP

**Goal**: Implement 2+ independent watchers that route to Bronze Inbox without interference

**Test**: Configure both watchers, trigger inputs on both channels within same minute, verify both logged in Dashboard.md and processed through Bronze intake without data loss or duplication

### US2: Structured Plan Generation

**Goal**: Automatic Plan.md generation for multi-step tasks, external actions, and high-risk workflows

**Test**: Trigger a task requiring multiple steps, verify Plan.md is created with objective, steps, expected outcome, and risk level before any execution begins

### US3: Human Approval Workflow

**Goal**: Prevent unsafe auto-execution by requiring human approval for external actions

**Test**: Trigger an action requiring approval (e.g., LinkedIn post), verify Proposed_Action.md is created, wait for manual approval marking, then verify execution only proceeds after "Approved: Yes" is set

### US4: LinkedIn Content Automation

**Goal**: Generate LinkedIn post drafts, route through approval, execute via MCP, store post URL

**Test**: Request LinkedIn post generation, verify draft is saved, approve it, verify post is published via MCP, verify LinkedIn URL is stored in vault

### US5: Scheduled Autonomous Workflows

**Goal**: Execute routine tasks on schedule (daily summaries, periodic scanning) without user initiation

**Test**: Configure a scheduled task (e.g., daily inbox scan at 9 AM), verify it triggers automatically at the scheduled time and logs execution in Dashboard.md

### US6: External Action Execution via MCP

**Goal**: Centralize all external actions through MCP server for logging, audit, and safety

**Test**: Trigger an external action (e.g., send email), verify it routes through MCP server, verify action is logged with full context, verify no direct API calls bypass MCP

### US7: Skill Chaining and Orchestration

**Goal**: Chain multiple skills together in defined sequence for complex workflows

**Test**: Trigger a workflow requiring skill chaining, verify each skill executes in declared order, verify dependencies are respected, verify no implicit chaining occurs

---

## Environment Variables

```bash
# MCP Server
MCP_PORT=8765
MCP_HOST=localhost

# Gmail OAuth
GMAIL_OAUTH_TOKEN=
GMAIL_REFRESH_TOKEN=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# LinkedIn
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORGANIZATION_ID=
```

---

## Troubleshooting

### Watcher Not Triggering

**Check**:
```bash
# Check cron logs
grep CRON /var/log/syslog

# Check watcher logs
tail -f AI_Employee_Vault/Logs_Extended/watcher_*.md

# Test manually
uv run python -m ai_employee.watchers.gmail_watcher --verbose
```

### MCP Server Unreachable

**Check**:
```bash
# Is server running?
ps aux | grep mcp_server

# Check port
netstat -tlnp | grep 8765

# Test health endpoint
curl http://localhost:8765/health
```

### Approval Not Detected

**Check**:
```bash
# Verify file format
cat Proposed_Actions/Action_*.md

# Check for "Approved: Yes" exactly
grep "Approved: Yes" Proposed_Actions/Action_*.md
```

### Bronze Regression

**Action**: STOP immediately. Constitution violation detected.

**Recovery**:
```bash
# Revert Silver changes
git stash

# Verify Bronze functionality

# Re-apply Silver changes incrementally
git stash pop
```

---

## Testing

### Run All Tests

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
uv run pytest
```

### Manual Scenario Testing

See `specs/002-silver-tier-orchestration/quickstart.md` for validation checklists per user story.

---

## Contributing

1. Create feature branch
2. Implement changes
3. Run tests
4. Update documentation
5. Submit PR

---

## License

Internal use only - AI Employee Project

---

## Support

- **Spec**: `specs/002-silver-tier-orchestration/spec.md`
- **Plan**: `specs/002-silver-tier-orchestration/plan.md`
- **Quickstart**: `specs/002-silver-tier-orchestration/quickstart.md`
- **Data Model**: `specs/002-silver-tier-orchestration/data-model.md`
