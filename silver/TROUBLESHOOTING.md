# Troubleshooting Guide: Silver Tier Orchestration

**Created**: 2026-02-21
**Version**: 1.0.0

---

## Common Issues

### 1. Watcher Not Triggering

**Symptoms**: No entries in Dashboard.md Watcher Triggers section

**Diagnostic Commands**:
```bash
# Check if cron is running
sudo service cron status

# Check cron logs
grep CRON /var/log/syslog

# Check watcher state files
cat AI_Employee_Vault/Logs_Extended/watcher_*_state.md

# Test watcher manually
uv run python -m ai_employee.watchers.gmail_watcher --test
uv run python -m ai_employee.watchers.filesystem_watcher --test
```

**Possible Causes**:
- Cron service not running
- OAuth token expired (Gmail)
- Watch directory doesn't exist (Filesystem)
- Python environment not activated

**Solutions**:
```bash
# Start cron service
sudo service cron start

# Refresh Gmail OAuth token
# (Re-run OAuth flow)

# Create watch directory
mkdir -p AI_Employee_Vault/Inbox_Drop

# Activate UV environment
source .venv/bin/activate
```

---

### 2. MCP Server Unreachable

**Symptoms**: `curl: (7) Failed to connect to localhost:8765`

**Diagnostic Commands**:
```bash
# Is server running?
ps aux | grep mcp_server

# Check port binding
netstat -tlnp | grep 8765

# Check server logs
tail -f ai_employee/mcp_server/logs/mcp_server.log

# Test health endpoint
curl http://localhost:8765/health
```

**Possible Causes**:
- Server not started
- Port already in use
- Firewall blocking localhost
- Python import errors

**Solutions**:
```bash
# Start MCP server
cd ai_employee/mcp_server
uv run python -m ai_employee.mcp_server.server &

# Check for port conflicts
lsof -i :8765

# Kill conflicting process
kill -9 <PID>

# Check Python dependencies
uv run python -c "import fastapi, uvicorn, httpx"
```

---

### 3. Approval Not Detected

**Symptoms**: Execution doesn't proceed after setting "Approved: Yes"

**Diagnostic Commands**:
```bash
# Verify file format
cat Proposed_Actions/Action_*.md

# Check for exact "Approved: Yes" string
grep "Approved: Yes" Proposed_Actions/Action_*.md

# Check file modification time
stat Proposed_Actions/Action_*.md

# Check polling script logs
tail -f AI_Employee_Vault/Logs_Extended/approval_polling.md
```

**Possible Causes**:
- File format incorrect (not markdown)
- Approved field not in frontmatter
- Polling script not running
- File permissions issue

**Solutions**:
```bash
# Verify frontmatter format
# Ensure file starts and ends with ---

# Check file permissions
chmod 644 Proposed_Actions/Action_*.md

# Manually trigger approval check
uv run python -m ai_employee.services.approval_request
```

---

### 4. LinkedIn Post Not Publishing

**Symptoms**: Approval granted but post not published

**Diagnostic Commands**:
```bash
# Check MCP action logs
cat ai_employee/mcp_server/logs/mcp_actions.md

# Verify LinkedIn token
echo $LINKEDIN_ACCESS_TOKEN

# Test LinkedIn API manually
curl -X POST https://api.linkedin.com/v2/ugcPosts \
  -H "Authorization: Bearer $LINKEDIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"author":"urn:li:person:me","lifecycleState":"PUBLISHED",...}'
```

**Possible Causes**:
- Invalid access token
- API rate limit exceeded
- Network connectivity issue
- LinkedIn API changes

**Solutions**:
```bash
# Refresh LinkedIn token
# (Re-authorize LinkedIn app)

# Check API rate limits
# (LinkedIn developer dashboard)

# Test network connectivity
curl -I https://api.linkedin.com
```

---

### 5. Scheduled Task Not Executing

**Symptoms**: Task not running at scheduled time

**Diagnostic Commands**:
```bash
# Check crontab
crontab -l

# Check cron logs
grep CRON /var/log/syslog | grep <task_name>

# Check task configuration
cat Scheduled_Tasks/<task_name>.md

# Check last run timestamp
grep "Last_Run" Scheduled_Tasks/<task_name>.md
```

**Possible Causes**:
- Cron expression incorrect
- Task disabled
- System was off at scheduled time
- Python path not set correctly in cron

**Solutions**:
```bash
# Fix cron expression
# (Use cron expression generator)

# Enable task
# Edit Scheduled_Tasks/<task_name>.md, set Enabled: true

# Handle missed schedule
# System should auto-execute on restart with missed_schedule: true

# Fix cron PATH
# Add PATH=/usr/local/bin:/usr/bin:/bin to crontab
```

---

### 6. Plan Not Generated

**Symptoms**: Complex task executed without Plan.md creation

**Diagnostic Commands**:
```bash
# Check Plans directory
ls -la AI_Employee_Vault/Plans/

# Check Dashboard.md Plan Creations section
grep -A 5 "### Plan Creations" AI_Employee_Vault/Dashboard.md

# Check plan generator logs
tail -f AI_Employee_Vault/Logs_Extended/plan_generator.md
```

**Possible Causes**:
- Task classifier not marking as complex
- Risk assessment too low
- Plan generator service not imported
- Trigger conditions not met

**Solutions**:
```bash
# Manually trigger plan generation
uv run python -m ai_employee.services.plan_generator

# Check task classifier output
cat AI_Employee_Vault/Inbox/*.md

# Review risk assessment heuristics
# (ai_employee/services/plan_generator.py)
```

---

### 7. Duplicate Processing After Restart

**Symptoms**: Same items processed multiple times after system restart

**Diagnostic Commands**:
```bash
# Check processed IDs files
cat AI_Employee_Vault/Logs_Extended/watcher_*_processed.md

# Check state files
cat AI_Employee_Vault/Logs_Extended/watcher_*_state.md

# Check last_check timestamp
grep "last_check" AI_Employee_Vault/Logs_Extended/watcher_*_state.md
```

**Possible Causes**:
- State files not persisted
- Processed IDs file corrupted
- Timestamp format incorrect
- Watcher not loading state on restart

**Solutions**:
```bash
# Verify state file permissions
chmod 644 AI_Employee_Vault/Logs_Extended/watcher_*_state.md

# Manually prune processed IDs
# (Edit processed IDs file, keep last 1000)

# Restart watcher
uv run python -m ai_employee.watchers.gmail_watcher --restart
```

---

### 8. Bronze Regression

**Symptoms**: Inbox processing broken after Silver changes

**⚠️ CRITICAL**: Constitution violation detected. STOP immediately.

**Diagnostic Commands**:
```bash
# Check Bronze skill files
ls -la AI_Employee_Vault/Skills/Bronze/

# Test Bronze intake manually
# (Drop file in Inbox, verify processing)

# Check git status
git status

# Review recent changes
git log --oneline -10
```

**Recovery Steps**:

```bash
# 1. Revert Silver changes
git stash

# 2. Verify Bronze functionality
# - Drop test file in Inbox
# - Verify classification
# - Verify state movement
# - Verify logging

# 3. Re-apply Silver changes incrementally
git stash pop

# 4. Test each Silver feature individually
# - Watchers
# - MCP server
# - Approval workflow
# - Scheduling

# 5. Validate Constitution principles
# (specs/002-silver-tier-orchestration/plan.md)
```

---

## Diagnostic Script

Run full diagnostic:

```bash
#!/bin/bash
# diagnostic.sh

echo "=== Silver Tier Diagnostic ==="
echo

echo "1. Python Environment"
uv run python --version
echo

echo "2. MCP Server Status"
curl -s http://localhost:8765/health || echo "MCP server not running"
echo

echo "3. Watcher State Files"
ls -la AI_Employee_Vault/Logs_Extended/watcher_*_state.md 2>/dev/null || echo "No watcher state files"
echo

echo "4. Scheduled Tasks"
ls -la AI_Employee_Vault/Scheduled_Tasks/ 2>/dev/null || echo "No scheduled tasks"
echo

echo "5. Recent Dashboard Entries"
tail -20 AI_Employee_Vault/Dashboard.md
echo

echo "6. Git Status"
git status --short
echo

echo "=== Diagnostic Complete ==="
```

---

## Getting Help

If issues persist:

1. **Check Documentation**:
   - `specs/002-silver-tier-orchestration/quickstart.md`
   - `README.md`
   - Skill definitions in `AI_Employee_Vault/Skills/Silver/`

2. **Review Logs**:
   - `AI_Employee_Vault/Logs_Extended/`
   - `ai_employee/mcp_server/logs/`
   - `Dashboard.md`

3. **Check Constitution**:
   - Verify no Bronze modifications
   - Verify MCP server is only external access point
   - Verify approval workflow for external actions

4. **Rollback**:
   - Use git to revert to last known good state
   - Re-apply changes incrementally
   - Test each feature independently

---

## Contact

For escalation, refer to project maintainers or create issue with:
- Diagnostic output
- Error logs
- Steps to reproduce
- Expected vs actual behavior
