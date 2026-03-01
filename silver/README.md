# 🥈 Silver Tier - COMPLETE

**Personal AI Employee Hackathon 2026**
*Powered by Qwen | Real Gmail API | Real LinkedIn Posting | Playwright Automation*

---

## ✅ Complete Implementation

This is the **fully functional** Silver Tier with:

| Feature | Status | Implementation |
|---------|--------|----------------|
| Gmail Fetch | ✅ Working | OAuth2 + Gmail API |
| Gmail Send | ✅ Working | Gmail API with scopes |
| LinkedIn Post | ✅ Working | Playwright browser automation |
| File System | ✅ Working | Watchdog-based monitoring |
| MCP Server | ✅ Working | Full tool integration |
| Approval Workflow | ✅ Working | Human-in-the-loop |
| Scheduler | ✅ Working | Cron-based tasks |
| Daily Briefings | ✅ Working | Auto-generated summaries |

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd silver
pip install -e .
playwright install chromium
```

### 2. Setup Gmail (5 minutes)

```bash
# Follow COMPLETE_SETUP.md or run:
./setup_gmail.sh

# This will:
# 1. Check credentials.json
# 2. Open browser for OAuth
# 3. Save token automatically
```

### 3. Setup LinkedIn (2 minutes)

```bash
# Run setup script
./setup_linkedin.sh

# This will:
# 1. Install Playwright browsers
# 2. Open LinkedIn login
# 3. Save session automatically
```

### 4. Start the System

```bash
# Terminal 1: Watchers (Gmail + File)
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Scheduler
python3 src/main.py --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: MCP Server
python3 mcp_server/server.py ./AI_Employee_Vault
```

---

## 📋 Features

### 📧 Gmail Integration

**Fetch Emails:**
- Monitors Gmail every 2 minutes
- Creates action files for unread emails
- Classifies by priority (high/medium/low)

**Send Emails:**
```python
# Via MCP tool
send_email(
    to="client@example.com",
    subject="Re: Invoice Request",
    body="Dear Client, Thank you for your email...",
    skip_approval=False  # Creates approval request
)
```

**OAuth Scopes:**
- `gmail.readonly` - Read emails
- `gmail.labels` - Manage labels
- `gmail.send` - Send emails
- `gmail.compose` - Draft emails

### 🔗 LinkedIn Integration

**Post Updates:**
```python
# Via MCP tool
post_linkedin(
    content="🚀 Exciting business update!",
    reason="Q1 achievements",
    skip_approval=False
)
```

**Features:**
- Real browser automation via Playwright
- Persistent session (login once)
- Rate limiting (max 3 posts/day)
- Draft approval workflow

### 📁 File System

**Monitor Folders:**
- `/Inbox` - Primary drop folder
- `/Inbox_Drop` - Secondary drop folder

**Processing:**
- Detects new files every 30 seconds
- Creates action files with metadata
- Classifies by content priority

### 🔌 MCP Server Tools

| Tool | Description |
|------|-------------|
| `send_email` | Send via Gmail API |
| `post_linkedin` | Post via Playwright |
| `create_approval_request` | Create approval file |
| `check_approvals` | Check pending approvals |
| `update_dashboard` | Update Dashboard.md |
| `linkedin_login` | Initialize LinkedIn session |

---

## 📁 Complete Structure

```
silver/
├── credentials.json          # Gmail OAuth (you create)
├── .env                      # Optional environment vars
├── pyproject.toml            # Python dependencies
├── README.md                 # This file
├── COMPLETE_SETUP.md         # Detailed setup guide
├── setup_gmail.sh            # Gmail setup script
├── setup_linkedin.sh         # LinkedIn setup script
├── test_linkedin.py          # LinkedIn test script
├── test_all_features.sh      # Complete test suite
│
├── AI_Employee_Vault/        # Obsidian vault
│   ├── token.json          # Gmail OAuth token
│   ├── .linkedin_session/    # LinkedIn browser session
│   ├── Inbox/                # Primary drop folder
│   ├── Inbox_Drop/           # Secondary drop folder
│   ├── Needs_Action/         # Items to process
│   ├── Pending_Approval/     # Awaiting approval
│   ├── Approved/             # Approved actions
│   ├── Rejected/             # Declined actions
│   ├── Done/                 # Completed items
│   ├── Plans/                # Multi-step plans
│   ├── Scheduled_Tasks/      # Cron task definitions
│   ├── Logs/                 # Activity logs
│   ├── Briefings/            # Daily summaries
│   ├── Dashboard.md          # Real-time status
│   ├── Company_Handbook.md   # AI behavior rules
│   └── Agent_Skills.md       # 14 capabilities
│
├── src/
│   ├── main.py               # Main entry point
│   ├── watchers/
│   │   ├── base_watcher.py   # Base class
│   │   ├── gmail_watcher.py  # Gmail API (fetch + send)
│   │   └── filesystem_watcher.py  # File monitoring
│   ├── services/
│   │   ├── linkedin_service.py  # LinkedIn Playwright
│   │   ├── approval_service.py  # HITL workflow
│   │   └── plan_service.py      # Plan generation
│   └── scheduler/
│       ├── cron_runner.py    # Cron scheduler
│       └── daily_summary.py  # Daily briefings
│
└── mcp_server/
    ├── server.py             # MCP server
    └── actions/
        ├── email.py          # Email actions
        └── linkedin.py       # LinkedIn actions
```

---

## 🧪 Testing

### Run All Tests

```bash
./test_all_features.sh
```

### Test Gmail Send

```bash
python3 << 'EOF'
from src.watchers.gmail_watcher import GmailWatcher
g = GmailWatcher('AI_Employee_Vault', 'credentials.json')
result = g.send_email(
    to="your-email@gmail.com",
    subject="Test",
    body="Test from Silver Tier"
)
print(result)
EOF
```

### Test LinkedIn Post

```bash
python3 test_linkedin.py
```

---

## 📊 Agent Skills (14 Total)

### Bronze (7)
1. Inbox Intake Processor
2. Task Classifier
3. Task Summarizer
4. Dashboard Updater
5. Task State Mover
6. Duplicate Detector
7. Completion Evaluator

### Silver (7 New)
8. **Gmail Watcher** - Fetch emails via API
9. **Gmail Sender** - Send emails via API
10. **LinkedIn Poster** - Post via Playwright
11. **Plan Generator** - Multi-step planning
12. **Approval Workflow** - Human-in-the-loop
13. **Scheduler** - Cron-based tasks
14. **Daily Summary** - Auto briefings

---

## 🔐 Security

### Credentials

| File | Purpose | Commit? |
|------|---------|---------|
| `credentials.json` | Gmail OAuth | ❌ Never |
| `token.json` | Gmail token | ❌ Never |
| `.linkedin_session/` | LinkedIn session | ❌ Never |
| `.env` | Environment vars | ❌ Never |

### Approval Requirements

| Action | Approval |
|--------|----------|
| Email send (new recipient) | Required |
| Email send (known recipient) | Optional |
| LinkedIn post | Always required |
| Payment > $50 | Always required |
| File delete | Always required |

---

## 🐛 Troubleshooting

### Gmail: redirect_uri_mismatch

**Error:** `Error 400: redirect_uri_mismatch`

**Fix:**
1. Go to Google Cloud Console
2. APIs & Services → Credentials
3. Edit your OAuth client
4. Add redirect URI: `http://localhost:8085/callback`
5. Save and wait 5-10 minutes

### Gmail: Insufficient scopes

**Error:** `Insufficient scopes for operation`

**Fix:**
1. Delete `AI_Employee_Vault/token.json`
2. Add scopes to OAuth consent screen:
   - `gmail.send`
   - `gmail.compose`
3. Re-run: `./setup_gmail.sh`

### LinkedIn: Not logged in

**Error:** `Not logged into LinkedIn`

**Fix:**
```bash
python3 test_linkedin.py
# Log in manually in browser
# Session saves automatically
```

### Playwright: Browser errors

**Error:** `Browser executable not found`

**Fix:**
```bash
playwright install chromium
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `COMPLETE_SETUP.md` | Complete setup guide |
| `TESTING_GUIDE.md` | Hands-on testing |
| `QUICK_REFERENCE.md` | Quick commands |
| `GMAIL_SETUP.md` | Gmail integration |
| `Agent_Skills.md` | 14 capabilities |
| `Company_Handbook.md` | AI behavior rules |

---

## 🎯 What's Working

### ✅ Gmail API
- [x] Fetch unread emails
- [x] Classify by priority
- [x] Create action files
- [x] Send emails via API
- [x] Log sent emails
- [x] Mark as read

### ✅ LinkedIn
- [x] Browser automation
- [x] Persistent session
- [x] Post updates
- [x] Rate limiting
- [x] Draft approval
- [x] Activity logging

### ✅ File System
- [x] Monitor folders
- [x] Detect new files
- [x] Create action files
- [x] Priority classification
- [x] Duplicate prevention

### ✅ MCP Server
- [x] send_email tool
- [x] post_linkedin tool
- [x] create_approval_request
- [x] check_approvals
- [x] update_dashboard
- [x] linkedin_login

### ✅ Approval Workflow
- [x] Create approval files
- [x] Human review
- [x] Execute approved
- [x] Archive rejected
- [x] Activity logging

### ✅ Scheduler
- [x] Cron-based tasks
- [x] Daily briefings
- [x] Task persistence
- [x] Execution logging

---

## 🏆 Silver Tier Complete!

**All requirements met:**
- ✅ Gmail Watcher with OAuth2
- ✅ Gmail Send with API
- ✅ LinkedIn Poster with Playwright
- ✅ MCP Server for actions
- ✅ Plan Generator
- ✅ Approval Workflow
- ✅ Scheduler
- ✅ Daily Summary
- ✅ 14 Agent Skills
- ✅ Complete documentation

---

*Built for the Personal AI Employee Hackathon 2026*
*Powered by Qwen - Local-first, Agent-driven, Human-in-the-loop*

**Tagline:** Your life and business on autopilot.
