# Security & Compliance Guide

## Overview

This guide covers secure testing practices for the AI Employee Silver Tier, ensuring you can test all functionality **without risking account bans, API restrictions, or compliance violations**.

---

## 🛡️ Risk-Free Testing Architecture

### Testing Pyramid

```
                    ┌─────────────┐
                    │  PRODUCTION │ ← Never test here first
                    │   (Real)    │
                   ─┴─────────────┴─
                  ╱                 ╲
                 ╱   STAGING/UAT     ╲
                ╱    (Test Accounts)  ╲
               ─────────────────────────
              ╱                         ╲
             ╱     SANDBOX (Mock APIs)   ╲  ← Start here!
            ╱      (100% Safe, Local)     ╲
           ─────────────────────────────────
```

---

## ✅ Safe Testing Methods (No Account Risk)

### Method 1: Sandbox Test Suite (RECOMMENDED)

**Zero external API calls - completely isolated**

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
source .venv/bin/activate

# Run full test suite
python test_sandbox.py

# Expected output:
# ✓ All 8 tests passed - 100% success rate
# ✓ No external API calls made
# ✓ Safe for CI/CD pipelines
```

**Coverage:**
- MCP Server health & endpoints
- Filesystem Watcher processing
- Plan Generator service
- Approval Request workflow
- LinkedIn Mock poster
- Cron Runner scheduling
- Vault structure integrity

---

### Method 2: Mock LinkedIn Poster

**Simulates LinkedIn workflow without API**

```bash
# Generate test post
python -m ai_employee.mcp_server.actions.linkedin_mock_test --test

# Output:
# === LinkedIn Mock Posting Workflow ===
# [1/4] Generating LinkedIn post draft...
#       ✓ Draft created: Plans/LinkedIn_Draft_*.md
# [2/4] Creating approval request...
#       ✓ Approval request: Action_*.md
# [3/4] Checking approval status...
#       Status: PENDING
# [4/4] Executing mock LinkedIn post...
#       ✓ Mock URL: https://www.linkedin.com/feed/update/mock_*
```

**What happens:**
1. Draft saved to vault (not LinkedIn)
2. Approval workflow tested locally
3. "Published" post saved to Done/ folder
4. Mock URL generated (not real)

**Safety:**
- ✅ No LinkedIn API calls
- ✅ No credentials needed
- ✅ No account risk
- ✅ Full workflow simulation

---

### Method 3: Local Mock Server

**Simulate external APIs on localhost**

```bash
# Terminal 1: Start mock LinkedIn server
python3 << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MockLinkedIn(BaseHTTPRequestHandler):
    def do_POST(self):
        # Log request for verification
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Received: {post_data.decode()}")
        
        # Send mock success response
        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            "id": "urn:li:share:mock_test_123",
            "status": "PUBLISHED",
            "mock": True
        }
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress default logs

print("🔒 Mock LinkedIn: http://localhost:9999")
print("Press Ctrl+C to stop")
HTTPServer(('localhost', 9999), MockLinkedIn).serve_forever()
EOF

# Terminal 2: Test against mock
curl -X POST http://localhost:9999 \
  -H "Content-Type: application/json" \
  -d '{"content": "Test post from Silver Tier"}'

# Response:
# {"id": "urn:li:share:mock_test_123", "status": "PUBLISHED", "mock": true}
```

---

### Method 4: Network Isolation

**Block external calls during tests**

#### Linux (iptables)

```bash
# Create test chain
sudo iptables -N TEST_BLOCK

# Block social media APIs
sudo iptables -A TEST_BLOCK -p tcp --dport 443 -d linkedin.com -j DROP
sudo iptables -A TEST_BLOCK -p tcp --dport 443 -d api.linkedin.com -j DROP
sudo iptables -A TEST_BLOCK -p tcp --dport 443 -d gmail.com -j DROP
sudo iptables -A TEST_BLOCK -p tcp --dport 443 -d smtp.gmail.com -j DROP

# Enable blocking
sudo iptables -I OUTPUT -j TEST_BLOCK

# Run tests (will use mocks)
python test_sandbox.py

# Disable blocking after tests
sudo iptables -D OUTPUT -j TEST_BLOCK
sudo iptables -F TEST_BLOCK
sudo iptables -X TEST_BLOCK
```

#### macOS (pfctl)

```bash
# Create block list
cat > /tmp/block_test.conf << 'EOF'
block drop quick out proto tcp from any to any port 443
EOF

# Enable (requires sudo)
sudo pfctl -f /tmp/block_test.conf -e

# Run tests
python test_sandbox.py

# Disable
sudo pfctl -d
```

---

## 🔒 Environment-Based Safety

### Sandbox Mode Configuration

Create `.env.sandbox`:

```bash
# SANDBOX MODE - All external calls disabled
SANDBOX_MODE=true
MOCK_EXTERNAL_ACTIONS=true
TEST_MODE=true

# Fake credentials (never used)
LINKEDIN_ACCESS_TOKEN=mock_token_do_not_use
LINKEDIN_ORGANIZATION_ID=mock_org_123
GMAIL_OAUTH_TOKEN=mock_oauth_token
SMTP_USER=noreply@example.com
SMTP_PASS=fake_password_123

# Local-only configuration
MCP_HOST=localhost
MCP_PORT=8765
ALLOW_LOCALHOST_ONLY=true

# Logging (verbose for tests)
LOG_LEVEL=DEBUG
LOG_TO_FILE=true
```

Usage:

```bash
# Load sandbox environment
set -a && source .env.sandbox && set +a

# Run tests
python test_sandbox.py --verbose
```

---

## ⚠️ Dangerous Tests (AVOID Without Authorization)

### Never Test These Without Approval

| Test Type | Risk | Consequence | Safe Alternative |
|-----------|------|-------------|------------------|
| Real LinkedIn API | 🔴 CRITICAL | Account ban, API revoke | Mock poster |
| Real email sending | 🔴 CRITICAL | Spam flags, domain blacklist | Log to file |
| Production webhooks | 🔴 CRITICAL | Unintended actions | Mock server |
| Rate limit testing | 🔴 CRITICAL | Immediate API ban | Simulated delays |
| User data processing | 🔴 CRITICAL | GDPR/privacy violations | Synthetic data |
| Credential testing | 🔴 CRITICAL | Account compromise | Mock auth |
| Payment APIs | 🔴 CRITICAL | Financial loss | Sandbox APIs |

### Authorization Required

Before testing with real APIs, obtain:

1. ✅ **Written approval** from platform owner
2. ✅ **Test account** (not production)
3. ✅ **Rate limit documentation**
4. ✅ **Terms of Service** review
5. ✅ **Security team** sign-off
6. ✅ **Compliance review** (if handling user data)

---

## ✅ Compliance Checklist

### Pre-Testing Checklist

```markdown
## Security Compliance Checklist

### Account Safety
- [ ] Using test/sandbox account (not production)
- [ ] API credentials scoped to test environment
- [ ] Rate limits documented and respected
- [ ] Monitoring enabled for unusual activity

### Data Protection
- [ ] No PII (Personally Identifiable Information) in tests
- [ ] No real user data in test vault
- [ ] Synthetic/test data only
- [ ] Data encryption enabled for sensitive tests

### API Compliance
- [ ] Terms of Service reviewed
- [ ] API usage within allowed limits
- [ ] No prohibited test types (scraping, brute force, etc.)
- [ ] Proper error handling implemented

### Logging & Monitoring
- [ ] Logs configured (no secrets logged)
- [ ] Alert thresholds set
- [ ] Rollback procedure documented
- [ ] Emergency stop mechanism tested

### Environment Isolation
- [ ] Test environment isolated from production
- [ ] Network rules prevent production access
- [ ] Database/storage separate from production
- [ ] Credentials different from production
```

---

## 🧪 Test Scenarios (Safe)

### Scenario 1: Full Workflow Test

```bash
#!/bin/bash
# test_full_workflow.sh

echo "=== Safe Full Workflow Test ==="

# 1. Start MCP Server
python -m ai_employee.mcp_server.server &
MCP_PID=$!
sleep 3

# 2. Verify MCP
curl -s http://localhost:8765/health | grep -q "healthy"
if [ $? -ne 0 ]; then
    echo "MCP Server failed to start"
    exit 1
fi
echo "✓ MCP Server running"

# 3. Create test input
echo "Test workflow $(date)" > AI_Employee_Vault/Inbox_Drop/workflow_test.txt

# 4. Run watcher
python -m ai_employee.watchers.filesystem_watcher --test
echo "✓ Filesystem Watcher processed"

# 5. Generate plan
python -m ai_employee.services.plan_generator
echo "✓ Plan Generator tested"

# 6. Create approval request
python -m ai_employee.services.approval_request
echo "✓ Approval Request tested"

# 7. Mock LinkedIn post
python -m ai_employee.mcp_server.actions.linkedin_mock_test --test
echo "✓ LinkedIn Mock tested"

# 8. Check scheduler
python -m ai_employee.scheduler.cron_runner --check
echo "✓ Cron Runner checked"

# Cleanup
kill $MCP_PID

echo ""
echo "=== All Tests Passed (100% Safe) ==="
```

---

### Scenario 2: CI/CD Pipeline Test

```yaml
# .github/workflows/test-silver-tier.yml
name: Silver Tier Tests

on: [push, pull_request]

jobs:
  sandbox-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv venv
          source .venv/bin/activate
          uv sync
      
      - name: Run Sandbox Tests
        run: |
          source .venv/bin/activate
          python test_sandbox.py --json > test-results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results.json
```

---

### Scenario 3: Load Testing (Safe)

```bash
#!/bin/bash
# test_load.sh - Simulate high volume without external APIs

echo "=== Load Test (Mock Only) ==="

# Create 100 test files
for i in {1..100}; do
    echo "Load test file $i" > AI_Employee_Vault/Inbox_Drop/load_test_$i.txt
done

echo "Created 100 test files"

# Process all files
for i in {1..100}; do
    python -m ai_employee.watchers.filesystem_watcher --test
done

echo "Processed all files"

# Check results
INBOX_COUNT=$(ls AI_Employee_Vault/Inbox/*.md 2>/dev/null | wc -l)
echo "Files in Inbox: $INBOX_COUNT"

# Cleanup
rm AI_Employee_Vault/Inbox_Drop/load_test_*.txt
```

---

## 📊 Test Results Verification

### Verify No External Calls

```bash
# Monitor network during tests
sudo tcpdump -i any -n port 443 2>&1 | tee /tmp/network.log

# In another terminal, run tests
python test_sandbox.py

# After tests, check for external calls
grep -v "localhost" /tmp/network.log
grep -v "127.0.0.1" /tmp/network.log

# Should show NO external connections
```

### Verify Mock Usage

```bash
# Check logs for mock indicators
grep -i "mock" ai_employee/mcp_server/logs/mcp_actions.md
grep -i "mock" AI_Employee_Vault/Done/*.md

# Should show mock URLs, not real ones
```

---

## 🚨 Incident Response

### If Account Gets Flagged

1. **Stop all testing immediately**
2. **Document what was tested**
3. **Review API logs**
4. **Contact platform support**
5. **File incident report**

### Prevention

- Always use sandbox mode first
- Never test rate limits without approval
- Monitor API usage dashboards
- Set up alerts for unusual activity
- Use separate test accounts

---

## 📚 Additional Resources

- **Sandbox Tester**: `test_sandbox.py`
- **Mock LinkedIn**: `ai_employee/mcp_server/actions/linkedin_mock_test.py`
- **Run Guide**: `RUN_GUIDE.md`
- **API Documentation**: Platform-specific docs

---

## Summary

| Testing Method | Safety Level | External Calls | Credentials Needed |
|---------------|--------------|----------------|-------------------|
| Sandbox Suite | ✅ 100% Safe | None | None |
| Mock Poster | ✅ 100% Safe | None | None |
| Local Mock Server | ✅ 100% Safe | Localhost only | None |
| Network Blocked | ✅ 100% Safe | Blocked | None |
| Test Account | ⚠️ Use Caution | Yes (test) | Test credentials |
| Production API | 🔴 Dangerous | Yes (real) | Real credentials |

**Golden Rule:** Always start with sandbox testing. Only escalate to real APIs after thorough review and approval.
