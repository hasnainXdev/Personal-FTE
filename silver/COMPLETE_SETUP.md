# Silver Tier - Complete Setup Guide

## 🎯 Complete Silver Tier Implementation

This guide walks you through setting up the **complete** Silver Tier with:

- ✅ Gmail API (fetch + send emails)
- ✅ LinkedIn posting with Playwright
- ✅ File System watcher (already working)
- ✅ MCP Server for external actions
- ✅ Approval workflows
- ✅ Scheduled tasks

---

## 📋 Prerequisites

- Python 3.13+
- Google Cloud Console account
- LinkedIn account
- Playwright browsers

---

## 🔧 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
cd silver

# Install all dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Step 2: Setup Gmail API

#### 2.1 Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g., "AI Employee")
3. Enable **Gmail API**

#### 2.2 Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** user type
3. Fill in:
   - App name: AI Employee
   - User support email: your email
   - Developer contact email: your email
4. Add scopes:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.labels
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/gmail.compose
   ```
5. Add test users (your Gmail address)
6. Save and continue

#### 2.3 Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8085/callback
   ```
5. Click **Create**
6. Download the JSON file
7. Save as `credentials.json` in `silver/` folder

#### 2.4 Authenticate Gmail

```bash
# Run setup script
./setup_gmail.sh

# Or test directly
python3 -c "from src.watchers.gmail_watcher import GmailWatcher; g = GmailWatcher('AI_Employee_Vault', 'credentials.json'); print('Success!' if g.service else 'Failed')"
```

A browser window will open. Log in and grant permissions. Token will be saved automatically.

### Step 3: Setup LinkedIn

#### 3.1 Install Playwright

```bash
# Already done in Step 1, but verify:
playwright install chromium
```

#### 3.2 Authenticate LinkedIn

```bash
# Run setup script
./setup_linkedin.sh

# Or test manually
python3 test_linkedin.py
```

A browser window will open. Log in to LinkedIn manually. The session will be saved for future use.

### Step 4: Verify Installation

```bash
# Run complete test
./test_all_features.sh
```

---

## 🚀 Running the System

### Start All Components (3 Terminals)

**Terminal 1 - Watchers:**

```bash
cd silver
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers
```

**Terminal 2 - Scheduler:**

```bash
python3 src/main.py --vault ./AI_Employee_Vault --mode scheduler
```

**Terminal 3 - MCP Server:**

```bash
python3 mcp_server/server.py ./AI_Employee_Vault
```

---

## 📋 Using the System

### Gmail - Fetch and Send Emails

**Fetch emails automatically:**

- Gmail watcher runs every 2 minutes
- Creates action files in `/Needs_Action/`

**Send email via Qwen:**

```bash
cd AI_Employee_Vault
qwen "Draft a reply to the latest email in /Needs_Action and create approval request"
```

**Send email via MCP:**

```python
# Use MCP tool
send_email(
    to="client@example.com",
    subject="Re: Invoice Request",
    body="Dear Client, Please find attached...",
    skip_approval=False  # Creates approval request
)
```

### LinkedIn - Post Updates

**Create post draft:**

```bash
cd AI_Employee_Vault
qwen "Generate a LinkedIn post about completing Silver Tier"
```

**Approve and post:**

```bash
# Move draft to approved
mv AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md AI_Employee_Vault/Approved/

# MCP will post automatically
```

**Post via MCP:**

```python
post_linkedin(
    content="🚀 Exciting update about our project...",
    reason="Business update",
    skip_approval=False
)
```

### File System - Already Working

Drop files in `AI_Employee_Vault/Inbox_Drop/` and watcher will process them.

---

## 🧪 Testing

### Test Gmail Send

```bash
cd silver
python3 << 'EOF'
from src.watchers.gmail_watcher import GmailWatcher

g = GmailWatcher('AI_Employee_Vault', 'credentials.json')

if g.service:
    result = g.send_email(
        to="your-test-email@gmail.com",
        subject="Test from AI Employee",
        body="This is a test email from Silver Tier"
    )
    print(f"Send result: {result}")
else:
    print("Gmail service not initialized")
EOF
```

### Test LinkedIn Post

```bash
cd silver
python3 test_linkedin.py
```

### Test Complete Flow

```bash
./test_all_features.sh
```

---

## 📁 File Structure

```
silver/
├── credentials.json          # Gmail OAuth (you create)
├── AI_Employee_Vault/
│   ├── token.json          # Gmail token (auto-created)
│   ├── .linkedin_session/    # LinkedIn session (auto-created)
│   ├── Needs_Action/         # Items to process
│   ├── Pending_Approval/     # Awaiting approval
│   ├── Approved/             # Approved actions
│   ├── Done/                 # Completed
│   ├── Logs/                 # Activity logs
│   └── Dashboard.md          # Status overview
├── src/
│   ├── watchers/
│   │   ├── gmail_watcher.py  # Gmail fetch + send
│   │   └── filesystem_watcher.py
│   ├── services/
│   │   └── linkedin_service.py  # LinkedIn posting
│   └── scheduler/
│       └── cron_runner.py
├── mcp_server/
│   └── server.py             # MCP server
├── setup_gmail.sh            # Gmail setup script
├── setup_linkedin.sh         # LinkedIn setup script
└── test_*.sh                 # Test scripts
```

---

## 🔐 Security

- **credentials.json**: Never commit to git
- **token.json**: Auto-generated, never commit
- **.linkedin_session/**: Auto-generated, never commit
- All credentials stored locally, not in vault

---

## 🐛 Troubleshooting

### Gmail: redirect_uri_mismatch

- Add `http://localhost:8085/callback` to Google Cloud Console
- Wait 5-10 minutes for propagation

### Gmail: Scope insufficient

- Add `gmail.send` and `gmail.compose` scopes
- Delete `token.json` and re-authenticate

### LinkedIn: Not logged in

- Run `python3 test_linkedin.py`
- Log in manually in browser
- Session saves automatically

### Playwright: Browser errors

- Run `playwright install chromium`
- Ensure you have disk space

---

## ✅ Silver Tier Complete When:

- [x] Gmail fetches emails automatically
- [x] Gmail sends emails via API
- [x] LinkedIn posts via Playwright
- [x] File system watcher working
- [x] MCP server running
- [x] Approval workflows functional
- [x] Scheduler running tasks
- [x] All tests passing

---

_Silver Tier - Complete Implementation_
_Powered by Qwen_
