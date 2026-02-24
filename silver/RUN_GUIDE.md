# Silver Tier - Complete Run Guide

## Overview

This guide covers running the entire Silver Tier locally, including:
- MCP Server (external actions boundary)
- Filesystem Watcher (input channel)
- Gmail Watcher (input channel - requires OAuth)
- Scheduler (cron-based task execution)
- Plan Generator (structured planning)
- Approval Workflow (human-in-the-loop)

---

## Security & Compliance - Safe Testing

### 🛡️ Sandbox Mode (RECOMMENDED - 100% Safe)

**Zero risk testing** without any external API calls:

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
source .venv/bin/activate

# Run complete test suite (safe, local only)
python test_sandbox.py

# Test specific component
python test_sandbox.py --component mcp
python test_sandbox.py --component watcher
python test_sandbox.py --component services

# Verbose output
python test_sandbox.py --verbose
```

**What it tests:**
- ✅ MCP Server health & actions
- ✅ Filesystem Watcher processing
- ✅ Plan Generator service
- ✅ Approval Request workflow
- ✅ LinkedIn Mock poster (no real LinkedIn)
- ✅ Cron Runner scheduling
- ✅ Vault structure integrity

**Why use sandbox:**
- No account flags or bans
- No credentials required
- Works offline
- Fast execution
- CI/CD friendly
- Compliance safe

---

### 🔒 Anonymous Testing Strategies

#### Strategy 1: Mock Objects (Safest)

Use mock implementations instead of real APIs:

```bash
# LinkedIn Mock Poster (creates fake posts in vault)
python -m ai_employee.mcp_server.actions.linkedin_mock_test --test

# Output shows mock URL like:
# https://www.linkedin.com/feed/update/mock_20260223120000
# (This is NOT a real LinkedIn URL - safe for testing)
```

#### Strategy 2: Local HTTP Mock Server

Simulate external APIs locally:

```bash
# Start mock server (Terminal 1)
python3 << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MockAPI(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        # Mock LinkedIn response
        response = {"id": "urn:li:share:mock123", "status": "created"}
        self.wfile.write(json.dumps(response).encode())
    def log_message(self, *args): pass

print("Mock API running on http://localhost:9999")
HTTPServer(('localhost', 9999), MockAPI).serve_forever()
EOF

# Test against mock (Terminal 2)
curl -X POST http://localhost:9999 \
  -H "Content-Type: application/json" \
  -d '{"content": "test post"}'
```

#### Strategy 3: Environment Isolation

Use `.env.test` for isolated testing:

```bash
# Create test environment
cat > .env.test << 'EOF'
# SANDBOX MODE - All external calls mocked
SANDBOX_MODE=true
MOCK_EXTERNAL_ACTIONS=true

# Fake credentials (never used in sandbox)
LINKEDIN_ACCESS_TOKEN=mock_token_12345
SMTP_USER=test@example.com
SMTP_PASS=fake_password

# Local-only settings
MCP_HOST=localhost
MCP_PORT=8765
EOF

# Run with test environment
source .env.test && python test_sandbox.py
```

#### Strategy 4: Network Blocking (Paranoid Mode)

Block all outbound traffic during tests:

```bash
# Linux: Block outbound to social media during tests
sudo iptables -A OUTPUT -p tcp --dport 443 -d linkedin.com -j DROP
sudo iptables -A OUTPUT -p tcp --dport 443 -d api.linkedin.com -j DROP

# Run tests (they will use mocks)
python test_sandbox.py

# Restore after tests
sudo iptables -F OUTPUT
```

---

### ⚠️ What NOT to Test Without Approval

**Never test these without explicit authorization:**

| Action | Risk Level | Why |
|--------|-----------|-----|
| Real LinkedIn API calls | 🔴 HIGH | Account suspension, API ban |
| Real email sending | 🔴 HIGH | Spam flags, domain reputation |
| Production webhooks | 🔴 HIGH | Unintended side effects |
| Real user data | 🔴 HIGH | Privacy violations, GDPR |
| Rate limit testing | 🔴 HIGH | Immediate API ban |

**Safe alternatives:**
- Use mock implementations
- Test with localhost endpoints
- Use sandbox/test accounts
- Test with synthetic data only

---

### ✅ Compliance Checklist

Before testing with real APIs:

- [ ] **Terms of Service** reviewed and understood
- [ ] **API Rate Limits** documented and respected
- [ ] **Test Account** created (not production)
- [ ] **Data Privacy** impact assessed
- [ ] **Logging** configured (no PII in logs)
- [ ] **Rollback Plan** documented
- [ ] **Monitoring** enabled for anomalies
- [ ] **Approval** from security/compliance team

---

## Quick Start Commands

### 1. Start All Components (Recommended for Testing)

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver

# Activate virtual environment
source .venv/bin/activate

# Terminal 1: Start MCP Server (required for external actions)
python -m ai_employee.mcp_server.server

# Terminal 2: Run Filesystem Watcher (single poll)
python -m ai_employee.watchers.filesystem_watcher --test

# Terminal 3: Check scheduled tasks
python -m ai_employee.scheduler.cron_runner --check
```

### 2. Start All Components (Background Mode)

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
source .venv/bin/activate

# Start MCP Server in background
python -m ai_employee.mcp_server.server &
MCP_PID=$!

# Wait for server to start
sleep 3

# Verify MCP Server is running
curl http://localhost:8765/health

# Run Filesystem Watcher
python -m ai_employee.watchers.filesystem_watcher --test

# To stop MCP Server later:
kill $MCP_PID
```

### 3. Complete Silver Tier Test Suite

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
source .venv/bin/activate

echo "=== Silver Tier Test Suite ==="

# Test 1: MCP Server Health
echo "[1/6] Testing MCP Server health..."
curl -s http://localhost:8765/health | python3 -m json.tool

# Test 2: List Available Actions
echo "[2/6] Listing available actions..."
curl -s http://localhost:8765/actions | python3 -m json.tool

# Test 3: Filesystem Watcher
echo "[3/6] Running Filesystem Watcher..."
python -m ai_employee.watchers.filesystem_watcher --test

# Test 4: Plan Generator
echo "[4/6] Testing Plan Generator..."
python -m ai_employee.services.plan_generator

# Test 5: Approval Request Service
echo "[5/6] Testing Approval Request..."
python -m ai_employee.services.approval_request

# Test 6: Cron Runner
echo "[6/6] Checking scheduled tasks..."
python -m ai_employee.scheduler.cron_runner --check

echo "=== Test Suite Complete ==="
```

---

## Component Details

### MCP Server (Port 8765)

**Purpose**: Centralized external action boundary for email, LinkedIn, and webhooks.

**Start Command**:
```bash
source .venv/bin/activate
python -m ai_employee.mcp_server.server
```

**Health Check**:
```bash
curl http://localhost:8765/health
```

**List Actions**:
```bash
curl http://localhost:8765/actions
```

**Test Action (fetch_url)**:
```bash
curl -X POST http://localhost:8765/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "fetch_url",
    "parameters": {"url": "https://httpbin.org/get"},
    "timeout_ms": 10000
  }'
```

**Logs**: `ai_employee/mcp_server/logs/mcp_actions.md`

---

### Filesystem Watcher

**Purpose**: Monitor `AI_Employee_Vault/Inbox_Drop/` for new files and route to Inbox.

**Run Once**:
```bash
source .venv/bin/activate
python -m ai_employee.watchers.filesystem_watcher --test
```

**Run with Custom Interval**:
```bash
python -m ai_employee.watchers.filesystem_watcher --interval 30
```

**Test It**:
```bash
# Create test file
echo "Test content" > AI_Employee_Vault/Inbox_Drop/test_$(date +%s).txt

# Run watcher
python -m ai_employee.watchers.filesystem_watcher --test

# Check Inbox for processed file
ls -la AI_Employee_Vault/Inbox/
```

**Logs**: 
- State: `Logs_Extended/watcher_filesystem_state.md`
- Processed IDs: `Logs_Extended/watcher_filesystem_processed.md`

---

### Gmail Watcher (Requires OAuth)

**Purpose**: Monitor Gmail for new emails and route to Inbox.

**Setup Required**:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Set environment variables in `.env`:
   ```
   GMAIL_OAUTH_TOKEN=your_token
   GMAIL_REFRESH_TOKEN=your_refresh_token
   GMAIL_CLIENT_ID=your_client_id
   GMAIL_CLIENT_SECRET=your_client_secret
   ```

**Run Once**:
```bash
source .venv/bin/activate
python -m ai_employee.watchers.gmail_watcher --test
```

---

### Plan Generator Service

**Purpose**: Generate structured execution plans for complex tasks.

**Test Command**:
```bash
source .venv/bin/activate
python -m ai_employee.services.plan_generator
```

**Output**: Creates plan in `AI_Employee_Vault/Plans/Plan_YYYYMMDD_NNN.md`

**Dashboard Log**: Updates "Plan Creations" table in `Dashboard.md`

---

### Approval Request Service

**Purpose**: Human-in-the-loop approval workflow for high-risk actions.

**Test Command**:
```bash
source .venv/bin/activate
python -m ai_employee.services.approval_request
```

**Output**: Creates approval request in `AI_Employee_Vault/Proposed_Actions/Action_YYYYMMDD_NNN.md`

**Approve an Action**:
```bash
# Edit the action file and set:
Approved: Yes

# Or reject:
Approved: No
```

**Poll for Decisions**:
```bash
# Custom script to poll pending actions
python -c "
from ai_employee.services.approval_request import ApprovalRequest
service = ApprovalRequest()
service.poll_pending_actions()
"
```

---

### Cron Runner (Scheduler)

**Purpose**: Execute scheduled tasks based on cron expressions.

**Check Missed Executions**:
```bash
source .venv/bin/activate
python -m ai_employee.scheduler.cron_runner --check
```

**Run Due Tasks**:
```bash
python -m ai_employee.scheduler.cron_runner --run-due
```

**Run Specific Task**:
```bash
python -m ai_employee.scheduler.cron_runner --task "Daily_Summary"
```

**Create Scheduled Task**:
```bash
# Create file: AI_Employee_Vault/Scheduled_Tasks/Daily_Summary.md
cat > AI_Employee_Vault/Scheduled_Tasks/Daily_Summary.md << 'EOF'
---
Name: Daily_Summary
Cron: 0 9 * * *
Enabled: true
Last_Run: null
Next_Run: 2026-02-23T09:00:00Z
Missed_Schedule: false
Execution_Count: 0
---

## Task Configuration

```yaml
action: generate_daily_summary
parameters:
  output_dir: Logs_Extended
```

## Execution History

| Date | Status | Duration | Notes |
|------|--------|----------|-------|
| *No executions yet* | | | |
```
EOF
```

---

## LinkedIn Testing (Without API Access)

Since LinkedIn API access is restricted, use the **Mock LinkedIn Tester**:

### Option 1: Mock LinkedIn Post Tester

```bash
source .venv/bin/activate
python -m ai_employee.mcp_server.actions.linkedin_mock_test
```

This creates a mock post in the vault instead of posting to LinkedIn.

### Option 2: Manual LinkedIn Testing Workflow

1. **Generate Post Draft** (via Plan Generator):
   ```bash
   python -m ai_employee.services.plan_generator
   ```

2. **Create Approval Request**:
   ```bash
   python -m ai_employee.services.approval_request
   ```

3. **Approve the Action**:
   Edit `AI_Employee_Vault/Proposed_Actions/Action_*.md`:
   ```markdown
   Approved: Yes
   ```

4. **Execute Mock Post** (simulates LinkedIn post):
   ```bash
   python -m ai_employee.mcp_server.actions.linkedin_mock_test --execute
   ```

5. **Verify Output**:
   Check `AI_Employee_Vault/Done/LinkedIn_Post_*.md` for the "published" post.

### Option 3: Use LinkedIn Manual Posting

For real LinkedIn posts without API:

1. Generate post content using AI
2. Save to `AI_Employee_Vault/Plans/LinkedIn_Draft_*.md`
3. Copy content manually to LinkedIn.com
4. Log the post URL in the vault

---

## Environment Configuration

### Required Variables (.env)

```bash
# MCP Server
MCP_PORT=8765
MCP_HOST=localhost

# Gmail OAuth (optional - for Gmail watcher)
GMAIL_OAUTH_TOKEN=
GMAIL_REFRESH_TOKEN=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=

# SMTP (optional - for email actions)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# LinkedIn (optional - for LinkedIn actions)
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORGANIZATION_ID=

# Watcher Configuration
WATCHER_POLL_INTERVAL=60
WATCHER_GMAIL_ENABLED=true
WATCHER_FILESYSTEM_ENABLED=true

# Scheduler Configuration
SCHEDULER_ENABLED=true
DAILY_SUMMARY_TIME=09:00
```

### Setup .env

```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

---

## Troubleshooting

### MCP Server Won't Start

```bash
# Check if port is in use
netstat -tlnp | grep 8765

# Kill existing process
kill $(lsof -t -i:8765)

# Check logs
tail -f ai_employee/mcp_server/logs/mcp_server.log
```

### Watcher Not Processing Files

```bash
# Check file modification time
stat AI_Employee_Vault/Inbox_Drop/test.txt

# Check watcher state
cat Logs_Extended/watcher_filesystem_state.md

# Clear state and retry
rm Logs_Extended/watcher_filesystem_*.md
python -m ai_employee.watchers.filesystem_watcher --test
```

### Approval Not Detected

```bash
# Verify file format
cat Proposed_Actions/Action_*.md

# Check for exact "Approved: Yes"
grep "Approved: Yes" Proposed_Actions/Action_*.md

# Poll manually
python -c "
from ai_employee.services.approval_request import ApprovalRequest
service = ApprovalRequest()
service.poll_pending_actions(lambda x: print(f'Approved: {x}'))
"
```

---

## Validation Checklist

Run this to verify all components:

```bash
#!/bin/bash
# validation_check.sh

echo "=== Silver Tier Validation ==="

# 1. MCP Server
echo -n "[1/5] MCP Server health... "
if curl -s http://localhost:8765/health | grep -q "healthy"; then
    echo "✓ PASS"
else
    echo "✗ FAIL (start with: python -m ai_employee.mcp_server.server)"
fi

# 2. MCP Actions
echo -n "[2/5] MCP actions registered... "
ACTIONS=$(curl -s http://localhost:8765/actions | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('actions',[])))")
if [ "$ACTIONS" -ge 4 ]; then
    echo "✓ PASS ($ACTIONS actions)"
else
    echo "✗ FAIL (expected 4+, got $ACTIONS)"
fi

# 3. Filesystem Watcher
echo -n "[3/5] Filesystem watcher... "
if python -m ai_employee.watchers.filesystem_watcher --test 2>&1 | grep -q "Processed"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

# 4. Plan Generator
echo -n "[4/5] Plan generator... "
if python -m ai_employee.services.plan_generator 2>&1 | grep -q "Created plan"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

# 5. Approval Request
echo -n "[5/5] Approval request... "
if python -m ai_employee.services.approval_request 2>&1 | grep -q "Created approval request"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
fi

echo "=== Validation Complete ==="
```

---

## Architecture Reference

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

## Next Steps

1. **Start MCP Server** (always first)
2. **Run watchers** to process inputs
3. **Generate plans** for complex tasks
4. **Create approval requests** for high-risk actions
5. **Execute scheduled tasks** via cron runner
6. **Monitor Dashboard.md** for activity logs

For production use:
- Configure Gmail OAuth for email watching
- Set up cron jobs for scheduled tasks
- Configure SMTP for email actions
- Obtain LinkedIn API access for posting
