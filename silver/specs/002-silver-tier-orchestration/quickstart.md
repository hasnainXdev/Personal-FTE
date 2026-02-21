# Quickstart Guide: Silver Tier Orchestration

**Feature**: Silver Tier Orchestration
**Created**: 2026-02-20
**Version**: 1.0.0

---

## Prerequisites

Before starting, ensure you have:

- ✅ Bronze Tier fully operational (Inbox processing, classification, state movement, logging)
- ✅ WSL Ubuntu installed (for Windows users)
- ✅ UV Python environment configured
- ✅ Git repository with Bronze Tier codebase
- ✅ Obsidian vault structure in place

---

## Step 1: Environment Setup

### 1.1 Activate UV Python Environment

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
uv python install 3.11
uv venv
source .venv/bin/activate
```

### 1.2 Install Dependencies

```bash
# Core dependencies (add to pyproject.toml)
uv add fastapi uvicorn httpx  # MCP server
uv add apscheduler  # Optional: if not using native cron
uv add google-auth google-auth-oauthlib  # Gmail watcher
uv add linkedin-api  # LinkedIn watcher (if available)
```

---

## Step 2: Configure Watchers

### 2.1 Gmail Watcher

**File**: `scripts/watchers/gmail_watcher.py`

**Configuration**:
```bash
# Set environment variables
export GMAIL_OAUTH_TOKEN="your-oauth-token"
export GMAIL_REFRESH_TOKEN="your-refresh-token"
```

**OAuth Setup**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project, enable Gmail API
3. Create OAuth 2.0 credentials
4. Download credentials.json
5. Run OAuth flow to get tokens

**Test**:
```bash
uv run python scripts/watchers/gmail_watcher.py --test
```

---

### 2.2 Filesystem Watcher

**File**: `scripts/watchers/filesystem_watcher.py`

**Configuration**:
```yaml
# scripts/watchers/config/filesystem.yaml
watch_directory: /mnt/d/it-course/hackathons/personal-FTE/silver/AI_Employee_Vault/Inbox_Drop
poll_interval: 60
file_patterns:
  - "*.txt"
  - "*.md"
  - "*.json"
recursive: false
```

**Test**:
```bash
# Create test file
echo "Test content" > /mnt/d/it-course/hackathons/personal-FTE/silver/AI_Employee_Vault/Inbox_Drop/test.txt

# Run watcher
uv run python scripts/watchers/filesystem_watcher.py --test
```

---

## Step 3: Set Up MCP Server

### 3.1 Create MCP Server Structure

```bash
mkdir -p mcp_server/actions mcp_server/logs
```

### 3.2 Configure MCP Server

**File**: `mcp_server/.env`
```bash
# MCP Server Configuration
MCP_PORT=8765
MCP_HOST=localhost

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your-linkedin-token
```

### 3.3 Start MCP Server

```bash
cd mcp_server
uv run python server.py
```

**Verify**:
```bash
curl http://localhost:8765/health
```

Expected response:
```json
{
  "status": "healthy",
  "uptime_seconds": 5,
  "version": "1.0.0"
}
```

---

## Step 4: Configure Scheduling

### 4.1 Create Cron Jobs

**Edit crontab**:
```bash
crontab -e
```

**Add entries**:
```bash
# Gmail watcher - every minute
* * * * * cd /mnt/d/it-course/hackathons/personal-FTE/silver && uv run python scripts/watchers/gmail_watcher.py >> Logs_Extended/watcher_gmail.md 2>&1

# Filesystem watcher - every minute
* * * * * cd /mnt/d/it-course/hackathons/personal-FTE/silver && uv run python scripts/watchers/filesystem_watcher.py >> Logs_Extended/watcher_filesystem.md 2>&1

# Daily summary - 9 AM daily
0 9 * * * cd /mnt/d/it-course/hackathons/personal-FTE/silver && uv run python scripts/scheduler/daily_summary.py >> Logs_Extended/scheduler.md 2>&1
```

### 4.2 Verify Cron

```bash
# List cron jobs
crontab -l

# Check cron service status
sudo service cron status
```

---

## Step 5: Create Vault Directories

```bash
cd AI_Employee_Vault

# Silver Tier directories
mkdir -p Plans Proposed_Actions Scheduled_Tasks Logs_Extended

# Set permissions
chmod 755 Plans Proposed_Actions Scheduled_Tasks Logs_Extended
```

---

## Step 6: Phase 1 Validation (Multi-Watcher)

### Test Plan

1. **Start both watchers**:
   ```bash
   # Terminal 1
   uv run python scripts/watchers/gmail_watcher.py --continuous

   # Terminal 2
   uv run python scripts/watchers/filesystem_watcher.py --continuous
   ```

2. **Trigger Gmail input**: Send yourself a test email

3. **Trigger Filesystem input**: Drop a file in watched directory

4. **Verify Dashboard.md**:
   ```markdown
   ### Watcher Triggers

   | Timestamp | Watcher | Items Found | Status |
   |-----------|---------|-------------|--------|
   | 2026-02-20T10:00:00Z | Gmail | 1 | Processed |
   | 2026-02-20T10:00:00Z | Filesystem | 1 | Processed |
   ```

5. **Verify Bronze Inbox**: Both inputs should appear in `Inbox/` folder

6. **Verify no interference**: Check logs show independent operation

### Validation Checklist

- [ ] Gmail watcher triggers and logs
- [ ] Filesystem watcher triggers and logs
- [ ] Both watchers operate simultaneously
- [ ] No duplicate processing after restart
- [ ] Bronze Inbox receives both inputs
- [ ] Dashboard.md shows both watchers
- [ ] No cross-watcher interference

**Phase 1 Complete**: ✅ All checks pass

---

## Step 7: Phase 2 Validation (Planning Layer)

### Test Plan

1. **Create complex task**: Drop multi-step request in Inbox

2. **Verify Plan.md generation**:
   ```bash
   ls -la Plans/
   # Should show: Plan_20260220_001.md
   ```

3. **Check Plan content**:
   ```markdown
   ---
   Title: Process multi-step request
   Objective: Execute 3-step workflow
   Risk_Level: Medium
   Approval_Required: Yes
   ---
   ```

### Validation Checklist

- [ ] Plan.md created for complex tasks
- [ ] Plan includes all required fields
- [ ] Plan saved before execution
- [ ] Simple tasks skip planning (Bronze behavior)

**Phase 2 Complete**: ✅ All checks pass

---

## Step 8: Phase 3-7 Validation Summary

| Phase | Feature | Validation Command | Expected Result |
|-------|---------|-------------------|-----------------|
| 3 | Approval Workflow | Create Proposed_Action.md, set "Approved: Yes" | Execution proceeds |
| 4 | MCP Integration | `curl http://localhost:8765/health` | `{"status": "healthy"}` |
| 5 | LinkedIn Automation | Request post, approve, verify URL stored | LinkedIn URL in vault |
| 6 | Scheduling | Wait for scheduled time, check logs | Task triggered automatically |
| 7 | Orchestration | Trigger full chain, verify sequence | Skills execute in order |

---

## Troubleshooting

### Watcher Not Triggering

**Symptoms**: No entries in Dashboard.md

**Check**:
```bash
# Check cron logs
grep CRON /var/log/syslog

# Check watcher logs
tail -f Logs_Extended/watcher_*.md

# Test manually
uv run python scripts/watchers/gmail_watcher.py --verbose
```

### MCP Server Unreachable

**Symptoms**: `curl: (7) Failed to connect`

**Check**:
```bash
# Is server running?
ps aux | grep mcp_server

# Check port
netstat -tlnp | grep 8765

# Check firewall
sudo ufw status
```

### Approval Not Detected

**Symptoms**: Execution doesn't proceed after approval

**Check**:
```bash
# Verify file format
cat Proposed_Actions/Action_*.md

# Check for "Approved: Yes" exactly
grep "Approved: Yes" Proposed_Actions/Action_*.md

# Check polling script logs
tail -f Logs_Extended/approval_polling.md
```

### Bronze Regression

**Symptoms**: Inbox processing broken after Silver changes

**Action**: STOP immediately. Constitution violation detected.

**Recovery**:
```bash
# Revert Silver changes
git stash

# Verify Bronze functionality
# Run Bronze test scenarios

# Re-apply Silver changes incrementally
git stash pop
```

---

## Next Steps

After completing all phases:

1. ✅ Silver Tier operational
2. Run `/sp.tasks` to generate implementation task list
3. Begin Phase 1 implementation
4. Validate each phase before proceeding

---

## Support

- **Spec**: `specs/002-silver-tier-orchestration/spec.md`
- **Plan**: `specs/002-silver-tier-orchestration/plan.md`
- **Research**: `specs/002-silver-tier-orchestration/research.md`
- **Data Model**: `specs/002-silver-tier-orchestration/data-model.md`
- **Contracts**: `specs/002-silver-tier-orchestration/contracts/`
