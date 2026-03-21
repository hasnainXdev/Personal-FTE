# Qwen Commands Quick Reference

## Gold Tier Overview

**Gold Tier = Silver Features + Odoo + Facebook**

| Category         | Tools Available                                                  |
| ---------------- | ---------------------------------------------------------------- |
| **Email**        | `send_email` (Gmail API)                                         |
| **Social Media** | `post_linkedin`, `post_facebook`                                 |
| **Accounting**   | `create_odoo_invoice`, `record_odoo_payment`                     |
| **Workflow**     | `create_approval_request`, `check_approvals`, `update_dashboard` |

**Skipped:** WhatsApp, Instagram, Twitter/X (per requirements)

---

## Setup

### 1. Configure Environment

```bash
cd gold
cp .env.example .env
# Edit .env with your credentials
```

### 2. Required .env Configuration

```env
# Odoo (Accounting)
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key

# Gmail (Email)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REDIRECT_URI=http://localhost:8080

# System
VAULT_PATH=./AI_Employee_Vault
LOG_LEVEL=INFO
```

### 3. Install Dependencies

```bash
uv sync
playwright install  # For LinkedIn automation
```

### 4. Start Components

```bash
# Terminal 1: Watchers (File System + Gmail)
python -m src.main --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Scheduler (Daily Briefing, Weekly Audit)
python -m src.main --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: MCP Server (API for tools)
python -m src.main --vault ./AI_Employee_Vault --mode mcp

# Terminal 4: Qwen Orchestrator (Auto-invokes Qwen every 30s)
python -m src.services.qwen_orchestrator --vault ./AI_Employee_Vault --interval 30
```

---

## File System Watcher Usage

The Gold tier uses a **File System Watcher** pattern. Drop files into `Inbox/` and they're automatically processed.

### How It Works

```
1. Drop file → AI_Employee_Vault/Inbox/
2. FileSystemWatcher detects (real-time via Watchdog)
3. Creates action file → AI_Employee_Vault/Needs_Action/FILE_*.md
4. Qwen orchestrator processes the action file
5. Creates approval requests in /Pending_Approval/
6. Human approves (move to /Approved/)
7. Action executed, moved to /Done/
```

### Usage Examples

```bash
# Drop a file
cp invoice.pdf AI_Employee_Vault/Inbox/

# Watcher auto-creates: Needs_Action/FILE_invoice_abc123.md

# Process with Qwen (manual)
qwen "Read Company_Handbook.md, then process /Needs_Action"

# Or wait for orchestrator (auto-checks every 30 seconds)
```

### Create Request Files Manually

```bash
# Facebook post request
cat > AI_Employee_Vault/Needs_Action/SOCIAL_facebook_post.md << 'EOF'
---
type: social_media_request
platform: facebook
priority: normal
---

Create a post about our Q1 achievements
EOF

# Invoice request
cat > AI_Employee_Vault/Needs_Action/INVOICE_client_xyz.md << 'EOF'
---
type: invoice_request
client: XYZ Corporation
client_email: billing@xyzcorp.com
amount: 2500
description: Consulting services - January 2026
due_date: 2026-02-15
---

Please create and send invoice
EOF

# Email processing request
cat > AI_Employee_Vault/Needs_Action/EMAIL_followup.md << 'EOF'
---
type: email_request
to: client@example.com
priority: high
---

Send a follow-up email about the pending invoice
EOF
```

---

## MCP Tools Reference

| Tool | Description | Approval Required |
|------|-------------|-------------------|
| `send_email` | Send emails via Gmail API | First time |
| `post_linkedin` | Post to LinkedIn | Always |
| `post_facebook` | Post to Facebook | Always |
| `create_approval_request` | Create approval file | No |
| `check_approvals` | Check pending approvals | No |
| `update_dashboard` | Update Dashboard.md | No |
| `create_odoo_invoice` | Create Odoo invoice | Yes |
| `record_odoo_payment` | Record Odoo payment | Yes |

---

## Basic Qwen Commands for Vault Operations

### 1. Process All Pending Items

```bash
qwen "Read Company_Handbook.md, then check /Needs_Action and process all pending items"
```

---

### 2. Draft Email Responses

```bash
# Process specific email
qwen "Read /Needs_Action/EMAIL_*.md and draft response emails"

# Process urgent emails only
qwen "Check /Needs_Action for high priority emails and draft responses"

# Reply to specific sender
qwen "Find emails from client@example.com in /Needs_Action and draft replies"
```

---

### 3. Create Facebook/LinkedIn Posts

```bash
# Create Facebook post from request
qwen "Read /Needs_Action/SOCIAL_facebook_*.md and create Facebook post drafts in /Pending_Approval"

# Generate LinkedIn business post
qwen "Create a LinkedIn post about our Q1 business achievements, save draft to /Pending_Approval"

# Generate multiple social posts
qwen "Generate 3 Facebook posts and 2 LinkedIn posts for this week's business updates"

# Create post from scratch
qwen "Create a Facebook post about our new product launch, save to /Pending_Approval"
```

---

### 4. Create Odoo Invoices

```bash
# Process invoice request
qwen "Read /Needs_Action/INVOICE_*.md, create invoices in Odoo, prepare approval requests"

# Create invoice for specific client
qwen "Create an Odoo invoice for ABC Corp, $2500, due Net 15, draft email to send"

# Process all pending invoices
qwen "Check /Needs_Action for invoice requests and create them in Odoo"

# Record payment
qwen "Record $2500 payment for invoice #INV-2026-001 in Odoo"

# Get invoice status
qwen "Check payment status of invoice #INV-2026-001 in Odoo"
```

---

### 5. Generate Briefings

```bash
# Daily briefing
qwen "Generate a daily briefing for today and save to /Briefings/Daily_YYYY-MM-DD.md"

# Weekly CEO briefing
qwen "Generate weekly business audit and CEO briefing, save to /Briefings/"

# Monthly summary
qwen "Create a monthly business summary from /Accounting and /Done folders"
```

---

### 6. Process File Drops

```bash
# Process dropped files
qwen "Check /Needs_Action for FILE_*.md and determine required actions"

# Process invoice PDF
qwen "Read the invoice PDF in /Needs_Action, extract details, and create Odoo entry"

# Process document
qwen "Review the document dropped in /Needs_Action and suggest actions"
```

---

### 7. Check Approvals

```bash
# List pending approvals
qwen "Check /Pending_Approval and summarize what needs my attention"

# Process approved items
qwen "Check /Approved folder and execute all approved actions"

# Review rejected items
qwen "Check /Rejected folder and summarize why items were rejected"
```

---

### 8. Update Dashboard

```bash
# Update dashboard status
qwen "Update Dashboard.md with current vault status and recent activities"

# Generate metrics
qwen "Calculate business metrics from /Done and /Accounting, update Dashboard.md"

# Weekly status
qwen "Update Dashboard.md with weekly summary and pending items count"
```

---

### 9. Plan Complex Tasks

```bash
# Create action plan
qwen "Create a Plan.md for processing these 5 invoice files in /Needs_Action"

# Multi-step task
qwen "Plan the steps to send invoices to all clients with overdue payments"

# Project planning
qwen "Create a plan for Q2 business goals based on /Business_Goals/Company_Goals.md"
```

---

### 10. Cleanup & Archive

```bash
# Archive old items
qwen "Move completed items older than 30 days from /Done to /Archive"

# Cleanup pending
qwen "Review /Pending_Approval and flag expired requests"

# Organize vault
qwen "Organize /Needs_Action folder by type and priority"
```

---

## Complete Workflow Examples

### Example 1: Email → Invoice → Send

```bash
# Step 1: Process email requesting invoice
qwen "Read /Needs_Action/EMAIL_invoice_request.md, extract client details, create Odoo invoice"

# Step 2: After approval, send invoice
qwen "Check /Approved folder, send invoice email to client, move to /Done"

# Step 3: Update records
qwen "Update Dashboard.md with invoice sent and payment tracking"
```

---

### Example 2: Social Media Campaign

```bash
# Step 1: Create posts
qwen "Generate 3 Facebook posts about our new product launch, save to /Pending_Approval"

# Step 2: After approval, post
qwen "Check /Approved for social media posts and execute posting"

# Step 3: Log results
qwen "Log social media activity to /Logs/social_YYYY-MM-DD.md"
```

---

### Example 3: Weekly Business Review

```bash
# Step 1: Generate briefing
qwen "Generate weekly CEO briefing with revenue, tasks completed, and bottlenecks"

# Step 2: Review approvals
qwen "Check /Pending_Approval and summarize items needing attention before weekend"

# Step 3: Update dashboard
qwen "Update Dashboard.md with weekly metrics and next week priorities"
```

---

## One-Liner Commands

```bash
# Quick process all
qwen "Process /Needs_Action"

# Quick draft emails
qwen "Draft responses for emails in /Needs_Action"

# Quick create invoice
qwen "Create Odoo invoice from /Needs_Action/INVOICE_*.md"

# Quick Facebook post
qwen "Draft Facebook post in /Pending_Approval"

# Quick check status
qwen "Summarize /Needs_Action, /Pending_Approval, and /Done"

# Quick daily briefing
qwen "Generate daily briefing for today"

# Quick dashboard update
qwen "Update Dashboard.md with current status"
```

---

## Qwen + Watchers Workflow

```bash
# Terminal 1: Start watchers (File System + Gmail)
python -m src.main --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Start scheduler (Daily Briefing, Weekly Audit)
python -m src.main --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: Start MCP server (Tool API)
python -m src.main --vault ./AI_Employee_Vault --mode mcp

# Terminal 4: Qwen orchestrator (auto-invokes Qwen every 30s)
python -m src.services.qwen_orchestrator --vault ./AI_Employee_Vault --interval 30

# Or manual Qwen processing (run as needed)
qwen "Process /Needs_Action"
```

---

## Qwen + MCP Server Workflow

```bash
# Terminal 1: Start MCP server
python -m src.main --vault ./AI_Employee_Vault --mode mcp

# Terminal 2: Use Qwen with MCP tools
qwen "Use MCP tools to send email, create Odoo invoice, and post to Facebook"
```

---

## Testing

```bash
# Run all tests
pytest tests/test_gold_tier.py -v

# Validate Gold Tier
python3 validate_gold_tier.py

# Test Odoo connection
uv run test_odoo.py

# Check vault structure
ls -la AI_Employee_Vault/
```

---

## Tips for Better Qwen Results

1. **Be specific about folders:**

   ```bash
   # Good
   qwen "Process files in /Needs_Action"

   # Better
   qwen "Read all .md files in /Needs_Action, prioritize by frontmatter priority field"
   ```

2. **Reference Company Handbook:**

   ```bash
   qwen "Read Company_Handbook.md first, then process invoice requests following the payment rules"
   ```

3. **Specify output location:**

   ```bash
   qwen "Create Facebook post drafts in /Pending_Approval folder"
   ```

4. **Chain operations:**
   ```bash
   qwen "Process /Needs_Action, move completed to /Done, update Dashboard.md"
   ```

---

## Quick Reference Card

```bash
# ===== START COMPONENTS =====

# Start watchers (File System + Gmail)
python -m src.main --vault ./AI_Employee_Vault --mode watchers

# Start scheduler (Daily Briefing, Weekly Audit)
python -m src.main --vault ./AI_Employee_Vault --mode scheduler

# Start MCP server (Tool API)
python -m src.main --vault ./AI_Employee_Vault --mode mcp

# Start Qwen orchestrator (auto-invokes every 30s)
python -m src.services.qwen_orchestrator --vault ./AI_Employee_Vault --interval 30

# ===== QWEN COMMANDS =====

# Process all pending items
qwen "Read Company_Handbook.md, then process /Needs_Action"

# Draft email responses
qwen "Draft responses for emails in /Needs_Action"

# Create Facebook post
qwen "Create Facebook post draft for [TOPIC]"

# Create LinkedIn post
qwen "Create LinkedIn post about [TOPIC]"

# Create Odoo invoice
qwen "Create Odoo invoice from /Needs_Action/INVOICE_*.md"

# Record Odoo payment
qwen "Record payment for invoice #INV-2026-001"

# Generate daily briefing
qwen "Generate daily briefing for today"

# Generate weekly CEO briefing
qwen "Generate weekly business audit and CEO briefing"

# Check pending approvals
qwen "Check /Pending_Approval and summarize what needs attention"

# Update dashboard
qwen "Update Dashboard.md with current vault status"

# ===== CREATE REQUEST FILES =====

# Create Facebook post request
cat > AI_Employee_Vault/Needs_Action/SOCIAL_facebook.md << 'EOF'
---
type: social_media_request
platform: facebook
priority: normal
---

Create a post about our new product launch
EOF

# Create invoice request
cat > AI_Employee_Vault/Needs_Action/INVOICE_client.md << 'EOF'
---
type: invoice_request
client: Client Name
amount: 1000
description: Consulting services
---

Please create and send invoice
EOF

# ===== TEST COMMANDS =====

# Run tests
pytest tests/ -v

# Validate Gold Tier
python3 validate_gold_tier.py

# Test Odoo
uv run test_odoo.py
```

---

## Troubleshooting

### Qwen API Error
```
Error: QWEN_API_KEY not set
```
**Fix:** Add to `.env`:
```env
QWEN_API_KEY=sk-your-key-here
```

### Odoo Access Denied
```
Error: AccessDenied: Access Denied
```
**Fix:** Grant permissions in Odoo:
1. Settings → Users → Your User
2. Set Contacts: Officer
3. Set Invoicing: Officer
4. Save

### Gmail Watcher Not Working
```
Warning: Gmail credentials not found
```
**Fix:**
1. Get credentials from Google Cloud Console
2. Save as `credentials/gmail_credentials.json`
3. Run OAuth flow once

### File Not Processed
**Check:**
- File is in `Inbox/` or `Needs_Action/`
- File has `.md` extension for metadata files
- Qwen orchestrator is running
- Company_Handbook.md exists

---

_Quick Reference for Gold Tier - Personal AI Employee_
_Powered by Qwen | Local-first, Agent-driven, Human-in-the-loop_
_Gold Tier = Silver + Odoo + Facebook_
