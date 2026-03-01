# QWEN.md - AI Employee Silver Tier Context

**Personal AI Employee Hackathon 2026 - Silver Tier**
*Powered by Qwen | Local-first | Agent-driven | Human-in-the-loop*

---

## 🎯 Project Overview

This is a **Personal AI Employee** system that uses **Qwen** as the reasoning engine to autonomously process files, emails, and business tasks. The Silver Tier builds on Bronze with Gmail integration, LinkedIn posting, MCP server, approval workflows, and scheduled tasks.

### Core Architecture

```
Perception (Watchers) → Reasoning (Qwen) → Action (MCP Server)
                          ↓
                    Planning → Approval → Execution
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| File Watcher | Monitors /Inbox folders | `src/watchers/filesystem_watcher.py` |
| Gmail Watcher | Monitors Gmail API | `src/watchers/gmail_watcher.py` |
| LinkedIn Service | Posts to LinkedIn | `src/services/linkedin_service.py` |
| Plan Service | Creates multi-step plans | `src/services/plan_service.py` |
| Approval Service | Manages HITL workflow | `src/services/approval_service.py` |
| Scheduler | Cron-based tasks | `src/scheduler/cron_runner.py` |
| MCP Server | External actions | `mcp_server/server.py` |
| Vault | Obsidian knowledge base | `AI_Employee_Vault/` |

---

## 🚀 Building and Running

### Prerequisites

- Python 3.13+
- pip or uv package manager
- Qwen CLI or API access
- Gmail credentials (optional)
- Playwright browsers

### Installation

```bash
cd silver

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install
```

### Running the System

```bash
# Terminal 1: Start watchers
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Start scheduler
python3 src/main.py --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: Start MCP server
python3 src/main.py --vault ./AI_Employee_Vault --mode mcp
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--vault`, `-v` | `./AI_Employee_Vault` | Path to Obsidian vault |
| `--interval`, `-i` | `30` | Watcher check interval (seconds) |
| `--mode`, `-m` | `watchers` | watchers/scheduler/mcp/all |
| `--debug`, `-d` | `false` | Enable debug logging |

### Testing

```bash
# Run test script
./test_silver.sh

# Run pytest
pytest tests/

# With coverage
pytest tests/ --cov=src
```

### Using Qwen to Process Tasks

```bash
# Navigate to vault
cd AI_Employee_Vault

# Process emails
qwen "Check /Needs_Action for email items and draft responses"

# Create a plan
qwen "Create a Plan.md for processing these invoice files"

# Generate LinkedIn post
qwen "Generate a business post about our Q1 achievements"

# Check approvals
qwen "Check /Pending_Approval and summarize what needs attention"

# Daily summary
qwen "Generate a daily summary briefing for yesterday"
```

---

## 📁 Project Structure

```
silver/
├── AI_Employee_Vault/       # Obsidian vault (knowledge base)
│   ├── Inbox/               # Drop files here
│   ├── Inbox_Drop/          # Additional drop folder
│   ├── Needs_Action/        # Items awaiting processing
│   ├── Done/                # Completed items archive
│   ├── Plans/               # Multi-step task plans
│   ├── Pending_Approval/    # Awaiting human approval
│   ├── Approved/            # Approved actions
│   ├── Rejected/            # Declined actions
│   ├── Scheduled_Tasks/     # Cron task definitions
│   ├── Skills/Silver/       # Silver-specific skills
│   ├── Logs/                # Activity and error logs
│   ├── Logs_Extended/       # Watcher state files
│   ├── Accounting/          # Financial transaction records
│   ├── Briefings/           # CEO briefings and reports
│   ├── Dashboard.md         # Real-time status overview
│   ├── Company_Handbook.md  # AI behavior rules and guidelines
│   ├── Agent_Skills.md      # Documented AI capabilities (14 skills)
│   └── Welcome.md           # Getting started guide
├── src/
│   ├── main.py              # CLI entry point
│   ├── watchers/
│   │   ├── base_watcher.py  # Abstract base watcher class
│   │   ├── filesystem_watcher.py  # File system monitor
│   │   └── gmail_watcher.py # Gmail API monitor
│   ├── services/
│   │   ├── linkedin_service.py  # LinkedIn automation
│   │   ├── approval_service.py  # HITL workflow
│   │   └── plan_service.py      # Plan generation
│   └── scheduler/
│       ├── cron_runner.py   # Cron-based scheduler
│       └── daily_summary.py # Daily briefing generator
├── mcp_server/
│   ├── server.py            # MCP server
│   └── actions/
│       ├── email.py         # Email actions
│       └── linkedin.py      # LinkedIn actions
├── tests/
│   └── test_silver.py       # Unit tests
├── pyproject.toml           # Python project configuration
├── README.md                # Full documentation
├── QWEN.md                  # This file - context for Qwen
├── SILVER_COMPLETE.md       # Completion summary
└── test_silver.sh           # Test script
```

---

## 🧠 Qwen Integration

### How Qwen Fits In

Qwen serves as the **reasoning engine** (the "Brain") in this architecture:

1. **Watchers detect** → Create action files
2. **Qwen reads** action file metadata
3. **Qwen processes** according to `Company_Handbook.md` rules
4. **Qwen acts**:
   - Creates plans for complex tasks
   - Requests approvals for sensitive actions
   - Uses MCP tools for external actions
   - Updates Dashboard.md
5. **Human reviews** pending approvals
6. **MCP executes** approved actions

### Processing Pattern

When Qwen is invoked, it should:

1. **Read** `Company_Handbook.md` first to understand rules
2. **Check** `/Needs_Action/` for pending items
3. **Process** each item:
   - Read the `.md` metadata file
   - Read any attached files
   - Determine required action
   - If 3+ steps: create Plan.md
   - If sensitive: create approval request
   - If simple: execute via MCP
   - Update `Dashboard.md`
   - Move to `/Done/` when complete
4. **Report** results to user

### MCP Tools Available

```python
# Available MCP tools for Qwen
- send_email: Send emails via Gmail
- post_linkedin: Post to LinkedIn  
- create_approval_request: Create approval files
- check_approvals: Check pending approvals
- update_dashboard: Update Dashboard.md
```

### Key Qwen Prompts

```bash
# Basic processing
qwen "Read Company_Handbook.md, then check /Needs_Action and process all items"

# Email processing
qwen "Check /Needs_Action for email items and draft responses"

# Plan creation
qwen "Create a Plan.md for processing these invoice files"

# LinkedIn post
qwen "Generate a business post about our latest project completion"

# Approval check
qwen "Check /Pending_Approval and summarize what needs my attention"

# Daily summary
qwen "Generate a daily summary briefing for yesterday"

# Dashboard update
qwen "Update Dashboard.md with current vault status"
```

---

## 📋 Development Conventions

### Code Style

- **Python**: Type hints where applicable, docstrings for all functions
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Logging**: Use Python logging module, structured format
- **Error Handling**: Try/except with logging, graceful degradation

### Testing Practices

- **Unit Tests**: pytest framework in `tests/` directory
- **Test Files**: Prefix with `test_`
- **Fixtures**: Use pytest fixtures for common setup
- **Coverage**: Aim for 80%+ coverage on core modules

### File Naming

- **Action Files**: `TYPE_<unique_id>.md` with frontmatter
- **Plans**: `Plan_YYYYMMDD_NN.md` in `/Plans/`
- **Approvals**: `APPROVAL_TYPE_YYYYMMDD_HHMMSS.md`
- **Logs**: `type_YYYY-MM-DD.md` in `/Logs/`
- **Briefings**: `Daily_YYYY-MM-DD.md` in `/Briefings/`

### Git Workflow

- **Branch**: Main development on current branch
- **Commits**: Descriptive messages, reference issues
- **Tags**: Version tags for milestones (e.g., `v0.2.0-silver`)

---

## 🔒 Security & Privacy

### Credential Management

- **Never store in vault**: Credentials in root only
- **OAuth2 tokens**: Stored in `token.json`
- **Session files**: Browser sessions in hidden folders
- **.gitignore**: All sensitive files ignored

### Current Security Model (Silver Tier)

- **Local-first**: Minimal external API calls
- **Human approval**: Required for all sensitive actions
- **Audit trail**: Complete logging in `/Logs/`
- **Rate limiting**: Max 3 LinkedIn posts/day

### Rules from Company_Handbook.md

```markdown
- Always be polite and professional
- Flag any payment over $500 for human approval
- Never auto-approve payments to new recipients
- Email sends require approval (first time)
- LinkedIn posts always require approval
- Check /Needs_Action folder every activation
- Create Plan.md for multi-step tasks (3+ steps)
- Move completed items to /Done/ with timestamp
- Log all actions in Dashboard.md
- Never delete files - move to /Done/ or /Archive/
- Add frontmatter to all created files
```

### Approval Requirements

| Action | Threshold | Approval |
|--------|-----------|----------|
| Email send | Any | Yes (first time) |
| LinkedIn post | Any | Yes (always) |
| Payment | > $50 | Yes (always) |
| New payment recipient | Any | Yes (always) |
| File delete | Any | Yes (always) |

---

## 🐛 Troubleshooting

### Watcher Issues

**Problem**: Watcher not detecting files
- Ensure file is not `.md` extension (reserved for metadata)
- Check watcher logs in `/Logs_Extended/`
- Verify vault path is correct
- Ensure file permissions allow reading

**Problem**: Gmail watcher not working
- Check `credentials.json` exists
- Run initial OAuth flow manually
- Check Gmail API is enabled in Google Cloud
- Review `/Logs/error_*.md`

### LinkedIn Issues

**Problem**: Posting fails
- Ensure browser session is authenticated
- Run `playwright install` if not done
- Check LinkedIn session in browser
- Review `/Logs/linkedin_*.md`

### Qwen Processing Issues

**Problem**: Qwen not processing correctly
- Verify `Company_Handbook.md` exists and is readable
- Check action files have proper frontmatter
- Review `/Logs/` for error details
- Use prompts from this file

**Problem**: Dashboard not updating
- Ensure Qwen has write permissions to vault
- Check Dashboard.md structure matches expected format
- Verify frontmatter is valid YAML

### Scheduler Issues

**Problem**: Tasks not running
- Check task is enabled in `/Scheduled_Tasks/`
- Verify cron expression is valid
- Check scheduler logs
- Ensure Python can import `croniter`

---

## 📈 Scheduled Tasks

| Task | Cron Expression | Description |
|------|-----------------|-------------|
| Daily Briefing | `0 8 * * *` | Generate at 8:00 AM daily |
| Email Check | `*/2 9-17 * * 1-5` | Every 2 min, 9AM-5PM, Mon-Fri |
| Weekly Review | `0 18 * * 0` | Sunday 6:00 PM |

---

## 🎓 Key Files Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` | Complete documentation | First time setup |
| `QWEN.md` | This file - Qwen context | Qwen processing |
| `Company_Handbook.md` | AI behavior rules | Qwen processing |
| `Agent_Skills.md` | Capability documentation | Understanding features |
| `SILVER_COMPLETE.md` | Success summary | Review |
| `test_silver.sh` | Test script | Testing |
| `src/watchers/gmail_watcher.py` | Gmail monitor | Development |
| `src/services/linkedin_service.py` | LinkedIn automation | Development |
| `src/services/plan_service.py` | Plan generation | Development |
| `src/services/approval_service.py` | HITL workflow | Development |
| `src/scheduler/cron_runner.py` | Scheduler | Development |
| `mcp_server/server.py` | MCP server | Integration |

---

## 🏆 Silver Tier Status

**✅ COMPLETE** - All requirements met:

- [x] All Bronze tier requirements
- [x] Gmail Watcher with OAuth2
- [x] LinkedIn Poster (Playwright)
- [x] MCP Server for external actions
- [x] Plan Generator for multi-step tasks
- [x] Human-in-the-loop approval workflow
- [x] Scheduler for cron-based tasks
- [x] Daily Summary Generator
- [x] Agent Skills documentation (14 skills)
- [x] End-to-end flow tested and working

**Test Results**: All 26 tests passing
- ✓ Vault structure (13 folders)
- ✓ Core files (4 markdown files)
- ✓ Watcher code (7 Python modules)
- ✓ Functional test (file drop)
- ✓ Dependencies installed

---

## 🔄 Workflow Examples

### Email Processing Flow

```
1. Gmail Watcher detects new email
   ↓
2. Creates action file in /Needs_Action/
   ↓
3. Qwen reads and drafts response
   ↓
4. MCP creates approval request
   ↓
5. Human moves to /Approved/
   ↓
6. MCP sends email via Gmail API
   ↓
7. Logs result and moves to /Done/
```

### LinkedIn Post Flow

```
1. Qwen generates business post
   ↓
2. Creates draft in /Pending_Approval/
   ↓
3. Human reviews and approves
   ↓
4. MCP posts via Playwright
   ↓
5. Logs post in /Logs/
   ↓
6. Updates Dashboard
```

### Multi-Step Task Flow

```
1. Complex task detected (3+ steps)
   ↓
2. Plan Generator creates Plan.md
   ↓
3. Qwen executes steps sequentially
   ↓
4. Updates plan progress
   ↓
5. Archives to /Done/Plans/ when complete
```

---

*Built for the Personal AI Employee Hackathon 2026*
*Powered by Qwen - Local-first, Agent-driven, Human-in-the-loop*
