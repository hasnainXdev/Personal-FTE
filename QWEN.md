# QWEN.md - AI Employee Project Context

**Personal AI Employee Hackathon 2026**
*Powered by Qwen | Local-first | Agent-driven | Human-in-the-loop*

---

## 🎯 Project Overview

This is a **Personal AI Employee** system that uses **Qwen** as the reasoning engine to autonomously process files, emails, and business tasks. The project has two tiers:

| Tier | Status | Description |
|------|--------|-------------|
| **Bronze** | ✅ Complete | Foundation with file system monitoring |
| **Silver** | ✅ Complete | Gmail, LinkedIn, MCP, approvals, scheduling |

### Core Architecture

```
Perception (Watchers) → Reasoning (Qwen) → Action (MCP Server)
                          ↓
                    Planning → Approval → Execution
```

### Tier Comparison

| Feature | Bronze | Silver |
|---------|--------|--------|
| Watchers | 1 (File) | 2 (File + Gmail) |
| Actions | Manual | MCP Server |
| Planning | Manual | Auto-generated |
| Approvals | Basic | Full workflow |
| Scheduling | None | Cron-based |
| Briefings | Manual | Auto daily |
| Skills | 7 | 14 |
| Location | `bronze/` | `silver/` |

---

## 📁 Project Structure

```
Personal-FTE/
├── QWEN.md                  # This file - project context
├── PROMPT.md                # Hackathon brief
├── bronze/                  # Bronze Tier (Foundation)
│   ├── AI_Employee_Vault/   # Obsidian vault
│   ├── src/
│   │   ├── main.py
│   │   └── watchers/
│   ├── tests/
│   ├── README.md
│   ├── QWEN_PROMPT_TEMPLATE.md
│   └── BRONZE_COMPLETE.md
└── silver/                  # Silver Tier (Functional)
    ├── AI_Employee_Vault/   # Obsidian vault
    ├── src/
    │   ├── main.py
    │   ├── watchers/
    │   ├── services/
    │   └── scheduler/
    ├── mcp_server/
    ├── tests/
    ├── README.md
    └── SILVER_COMPLETE.md
```

---

## 🚀 Building and Running

### Bronze Tier (Foundation)

```bash
cd bronze

# Install dependencies
pip install watchdog

# Start the file system watcher
python3 src/main.py --vault ./AI_Employee_Vault --interval 30

# Test
./test_simple.sh
```

### Silver Tier (Functional)

```bash
cd silver

# Install dependencies
pip install -e .
playwright install

# Terminal 1: Start watchers
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Start scheduler
python3 src/main.py --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: Start MCP server
python3 src/main.py --vault ./AI_Employee_Vault --mode mcp

# Test
./test_silver.sh
```

---

## 🧠 Qwen Integration

### How Qwen Fits In

Qwen serves as the **reasoning engine** (the "Brain"):

1. **Watchers detect** → Create action files
2. **Qwen reads** action file metadata
3. **Qwen processes** according to `Company_Handbook.md`
4. **Qwen acts**:
   - Creates plans for complex tasks
   - Requests approvals for sensitive actions
   - Uses MCP tools for external actions
   - Updates Dashboard.md
5. **Human reviews** pending approvals
6. **MCP executes** approved actions

### Processing Pattern

When Qwen is invoked:

1. **Read** `Company_Handbook.md` first
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

### Key Qwen Prompts

```bash
# Navigate to vault
cd bronze/AI_Employee_Vault  # or silver/AI_Employee_Vault

# Basic processing
qwen "Read Company_Handbook.md, then check /Needs_Action and process all items"

# Email processing (Silver)
qwen "Check /Needs_Action for email items and draft responses"

# Create a plan
qwen "Create a Plan.md for processing these invoice files"

# Generate LinkedIn post (Silver)
qwen "Generate a business post about our Q1 achievements"

# Check approvals (Silver)
qwen "Check /Pending_Approval and summarize what needs attention"

# Daily summary (Silver)
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
- **OAuth2 tokens**: Stored in `token.pickle`
- **Session files**: Browser sessions in hidden folders
- **.gitignore**: All sensitive files ignored

### Approval Requirements

| Action | Threshold | Approval |
|--------|-----------|----------|
| Email send | Any | Yes (first time) |
| LinkedIn post | Any | Yes (always) |
| Payment | > $50 | Yes (always) |
| New payment recipient | Any | Yes (always) |
| File delete | Any | Yes (always) |

### Rules from Company_Handbook.md

```markdown
- Always be polite and professional
- Flag any payment over $500 for human approval
- Never auto-approve payments to new recipients
- Check /Needs_Action folder every activation
- Create Plan.md for multi-step tasks (3+ steps)
- Move completed items to /Done/ with timestamp
- Log all actions in Dashboard.md
- Never delete files - move to /Done/ or /Archive/
- Add frontmatter to all created files
```

---

## 🐛 Troubleshooting

### Watcher Issues

**Problem**: Watcher not detecting files
- Ensure file is not `.md` extension (reserved for metadata)
- Check watcher logs in `/Logs/` or `/Logs_Extended/`
- Verify vault path is correct
- Ensure file permissions allow reading

**Problem**: Gmail watcher not working (Silver)
- Check `credentials.json` exists
- Run initial OAuth flow manually
- Check Gmail API is enabled in Google Cloud
- Review `/Logs/error_*.md`

### LinkedIn Issues (Silver)

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

### Scheduler Issues (Silver)

**Problem**: Tasks not running
- Check task is enabled in `/Scheduled_Tasks/`
- Verify cron expression is valid
- Check scheduler logs
- Ensure Python can import `croniter`

---

## 📈 Scheduled Tasks (Silver)

| Task | Cron Expression | Description |
|------|-----------------|-------------|
| Daily Briefing | `0 8 * * *` | Generate at 8:00 AM daily |
| Email Check | `*/2 9-17 * * 1-5` | Every 2 min, 9AM-5PM, Mon-Fri |
| Weekly Review | `0 18 * * 0` | Sunday 6:00 PM |

---

## 🎓 Key Files Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` (tier) | Complete documentation | First time setup |
| `QWEN.md` | This file - project context | Always |
| `Company_Handbook.md` | AI behavior rules | Qwen processing |
| `Agent_Skills.md` | Capability documentation | Understanding features |
| `BRONZE_COMPLETE.md` | Bronze success summary | Review |
| `SILVER_COMPLETE.md` | Silver success summary | Review |
| `test_simple.sh` | Bronze test script | Testing |
| `test_silver.sh` | Silver test script | Testing |

---

## 🏆 Tier Status

### Bronze Tier ✅ COMPLETE

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] One working Watcher script (File System)
- [x] Qwen integration for reading/writing to vault
- [x] Agent Skills documentation (7 skills)
- [x] End-to-end flow tested and working

### Silver Tier ✅ COMPLETE

- [x] All Bronze requirements
- [x] Gmail Watcher with OAuth2
- [x] LinkedIn Poster (Playwright)
- [x] MCP Server for external actions
- [x] Plan Generator for multi-step tasks
- [x] Human-in-the-loop approval workflow
- [x] Scheduler for cron-based tasks
- [x] Daily Summary Generator
- [x] Agent Skills documentation (14 skills)
- [x] End-to-end flow tested and working

---

## 📊 Test Results

### Bronze Tier
- ✓ Vault structure (10 folders)
- ✓ Core files (4 markdown files)
- ✓ Watcher code (3 Python files)
- ✓ Functional test (file detection)
- ✓ Action file creation
- ✓ Documentation complete

### Silver Tier
- ✓ Vault structure (13 folders)
- ✓ Core files (4 markdown files)
- ✓ Source code (7 Python modules)
- ✓ Functional test (file drop)
- ✓ Dependencies installed
- ✓ All 26 tests passing

---

## 🔌 MCP Server Tools (Silver)

| Tool | Description |
|------|-------------|
| `send_email` | Send emails via Gmail |
| `post_linkedin` | Post to LinkedIn |
| `create_approval_request` | Create approval files |
| `check_approvals` | Check pending approvals |
| `update_dashboard` | Update Dashboard.md |

---

## 📚 Documentation by Tier

### Bronze Tier
- `bronze/README.md` - Full documentation
- `bronze/QWEN_PROMPT_TEMPLATE.md` - Qwen prompts
- `bronze/VALIDATION.md` - Requirements checklist
- `bronze/BRONZE_COMPLETE.md` - Completion summary

### Silver Tier
- `silver/README.md` - Full documentation
- `silver/QWEN.md` - Silver-specific context
- `silver/SILVER_COMPLETE.md` - Completion summary

---

*Built for the Personal AI Employee Hackathon 2026*
*Powered by Qwen - Local-first, Agent-driven, Human-in-the-loop*

**Tagline:** Your life and business on autopilot.
