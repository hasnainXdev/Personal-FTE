# Silver Tier - Quick Commands Reference

## 🚀 Start Here

### Run Everything (Recommended)

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver

# Activate environment
source .venv/bin/activate

# Run all tests and start components
./run_all.sh run
```

---

## 📋 Command Cheat Sheet

### Testing (100% Safe - No External APIs)

```bash
# Full sandbox test suite
python test_sandbox.py

# Verbose output
python test_sandbox.py --verbose

# Test specific component
python test_sandbox.py --component mcp       # MCP Server only
python test_sandbox.py --component watcher   # Watchers only
python test_sandbox.py --component services  # Services only
python test_sandbox.py --component scheduler # Scheduler only
python test_sandbox.py --component vault     # Vault structure

# JSON output (for CI/CD)
python test_sandbox.py --json
```

### MCP Server

```bash
# Start MCP Server
python -m ai_employee.mcp_server.server

# Health check
curl http://localhost:8765/health

# List available actions
curl http://localhost:8765/actions

# Test an action (mock)
curl -X POST http://localhost:8765/execute \
  -H "Content-Type: application/json" \
  -d '{"action":"fetch_url","parameters":{"url":"http://localhost:9999/mock"}}'
```

### Filesystem Watcher

```bash
# Run single poll
python -m ai_employee.watchers.filesystem_watcher --test

# Run with custom interval
python -m ai_employee.watchers.filesystem_watcher --interval 30

# Test with new file
echo "Test content" > AI_Employee_Vault/Inbox_Drop/test_$(date +%s).txt
python -m ai_employee.watchers.filesystem_watcher --test
ls AI_Employee_Vault/Inbox/
```

### Plan Generator

```bash
# Test plan generation
python -m ai_employee.services.plan_generator

# Check generated plans
ls -la AI_Employee_Vault/Plans/
```

### Approval Request

```bash
# Test approval workflow
python -m ai_employee.services.approval_request

# Check pending actions
ls -la AI_Employee_Vault/Proposed_Actions/

# Approve an action (edit file and set)
# Approved: Yes
```

### LinkedIn Mock (Safe Testing)

```bash
# Run full mock workflow
python -m ai_employee.mcp_server.actions.linkedin_mock_test --test

# Execute pending approved actions
python -m ai_employee.mcp_server.actions.linkedin_mock_test --execute

# Create draft with custom content
python -m ai_employee.mcp_server.actions.linkedin_mock_test \
  --content "Your post content here" \
  --topic "Your Topic"
```

### Scheduler (Cron Runner)

```bash
# Check for missed executions
python -m ai_employee.scheduler.cron_runner --check

# Run due tasks
python -m ai_employee.scheduler.cron_runner --run-due

# Run specific task
python -m ai_employee.scheduler.cron_runner --task "Task_Name"
```

---

## 🎯 One-Liner Commands

```bash
# Quick health check
curl -s http://localhost:8765/health | grep -q "healthy" && echo "✓ MCP Healthy" || echo "✗ MCP Down"

# Count processed files
echo "Inbox: $(ls AI_Employee_Vault/Inbox/*.md 2>/dev/null | wc -l) files"

# Check MCP actions
curl -s http://localhost:8765/actions | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Actions: {len(d[\"actions\"])}')"

# Watch for new files (live)
watch -n 2 'ls -la AI_Employee_Vault/Inbox/'
```

---

## 🛡️ Safe Testing Commands

### Sandbox Mode (Always Safe)

```bash
# Run everything in sandbox mode
export SANDBOX_MODE=true
python test_sandbox.py
```

### Mock External APIs

```bash
# Start mock server (Terminal 1)
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
class M(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'mock':True,'id':'test123'}).encode())
    def log_message(self,*a): pass
print('Mock server: http://localhost:9999')
HTTPServer(('localhost',9999),M).serve_forever()
"

# Test against mock (Terminal 2)
curl -X POST http://localhost:9999 -H "Content-Type: application/json" -d '{"test":true}'
```

---

## 🧹 Cleanup Commands

```bash
# Clean test artifacts
./run_all.sh clean

# Manual cleanup
rm -f AI_Employee_Vault/Inbox_Drop/test_*.txt
rm -f AI_Employee_Vault/Inbox/FILE_*.md
rm -f AI_Employee_Vault/Plans/Plan_*.md
rm -f AI_Employee_Vault/Proposed_Actions/Action_*.md
```

---

## 📊 Monitoring Commands

```bash
# Check MCP logs
tail -f ai_employee/mcp_server/logs/mcp_actions.md

# Check watcher state
cat Logs_Extended/watcher_filesystem_state.md

# Check Dashboard
tail -20 AI_Employee_Vault/Dashboard.md

# Monitor processes
ps aux | grep -E "(mcp|watcher|scheduler)"
```

---

## 🔧 Troubleshooting Commands

```bash
# Check if MCP port is in use
netstat -tlnp | grep 8765

# Kill MCP if stuck
pkill -f mcp_server

# Check Python version
python --version

# Verify virtual environment
which python

# Check dependencies
uv pip list

# Reinstall dependencies
uv sync
```

---

## 📁 Important Paths

```bash
# Project root
PROJECT=/mnt/d/it-course/hackathons/personal-FTE/silver

# Vault directories
VAULT=$PROJECT/AI_Employee_Vault
INBOX=$VAULT/Inbox
INBOX_DROP=$VAULT/Inbox_Drop
PLANS=$VAULT/Plans
PROPOSED=$VAULT/Proposed_Actions
DONE=$VAULT/Done
LOGS=$VAULT/Logs_Extended
SCHEDULED=$VAULT/Scheduled_Tasks

# Code directories
MCP_SERVER=$PROJECT/ai_employee/mcp_server
WATCHERS=$PROJECT/ai_employee/watchers
SERVICES=$PROJECT/ai_employee/services
SCHEDULER=$PROJECT/ai_employee/scheduler

# Logs
MCP_LOGS=$PROJECT/ai_employee/mcp_server/logs
```

---

## 🎬 Demo Scenarios

### Scenario 1: First Time Setup

```bash
# 1. Clone and setup
cd /mnt/d/it-course/hackathons/personal-FTE/silver
uv venv
source .venv/bin/activate
uv sync

# 2. Run tests
python test_sandbox.py

# 3. Start MCP
python -m ai_employee.mcp_server.server &

# 4. Test watcher
echo "Hello World" > AI_Employee_Vault/Inbox_Drop/hello.txt
python -m ai_employee.watchers.filesystem_watcher --test

# 5. Check result
cat AI_Employee_Vault/Inbox/*.md
```

### Scenario 2: Full Workflow Demo

```bash
# Run complete demo
./run_all.sh demo

# Or manually:
# 1. Start MCP
python -m ai_employee.mcp_server.server &

# 2. Create test input
echo "Demo test" > AI_Employee_Vault/Inbox_Drop/demo.txt

# 3. Process input
python -m ai_employee.watchers.filesystem_watcher --test

# 4. Generate plan
python -m ai_employee.services.plan_generator

# 5. Create approval
python -m ai_employee.services.approval_request

# 6. Mock LinkedIn post
python -m ai_employee.mcp_server.actions.linkedin_mock_test --test
```

### Scenario 3: CI/CD Pipeline

```bash
#!/bin/bash
# .github/workflows/test.yml

- name: Run Tests
  run: |
    uv venv
    source .venv/bin/activate
    uv sync
    python test_sandbox.py --json > results.json

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: results.json
```

---

## 📚 Documentation Links

- **Run Guide**: `RUN_GUIDE.md` - Complete setup and usage
- **Security**: `SECURITY_COMPLIANCE.md` - Safe testing practices
- **README**: `README.md` - Project overview
- **Validation**: `VALIDATION_CHECKLIST.md` - Feature validation

---

## 🆘 Quick Help

```bash
# Show help
./run_all.sh help

# Check if MCP is running
curl -s http://localhost:8765/health

# Restart everything
pkill -f mcp_server
./run_all.sh run
```

---

**Last Updated**: 2026-02-23
**Version**: Silver Tier v0.1.0
