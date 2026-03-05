# Qwen Commands Quick Reference

## Setup

Add Qwen to your PATH (if not already):

```bash
# Add to ~/.bashrc or ~/.zshsc
export PATH="$PATH:/path/to/qwen"
```

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
qwen "Read /Needs_Action/SOCIAL_*.md and create Facebook post drafts in /Pending_Approval"

# Generate LinkedIn business post
qwen "Create a LinkedIn post about our Q1 business achievements and save to /Pending_Approval"

# Generate multiple social posts
qwen "Generate 3 Facebook posts and 2 LinkedIn posts for this week's business updates and save to /Needs_Action"
```

---

### 4. Create Odoo Invoices

```bash
# Process invoice request
qwen "Read /Needs_Action/INVOICE_*.md, create invoices in Odoo, and prepare approval requests"

# Create invoice for specific client
qwen "Create an Odoo invoice for ABC Corp, $2500, due Net 15, and draft email to send"

# Process all pending invoices
qwen "Check /Needs_Action for invoice requests and create them in Odoo"
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
# Terminal 1: Start watchers
python -m src.main --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Start scheduler
python -m src.main --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: Manual Qwen processing (run as needed)
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

## Common Qwen Prompt Templates

### Email Processing

```bash
qwen "Read Company_Handbook.md email rules, then process emails in /Needs_Action and draft responses"
```

### Invoice Creation

```bash
qwen "Read invoice requests in /Needs_Action, create Odoo invoices, create approval requests for sending"
```

### Social Media

```bash
qwen "Generate business social media posts for [TOPIC], save drafts to /Pending_Approval"
```

### Daily Operations

```bash
qwen "Check /Needs_Action, /Pending_Approval, update Dashboard.md with status"
```

### Weekly Review

```bash
qwen "Generate weekly audit from /Done, /Accounting, and /Briefings folders"
```

---

_Quick Reference for Gold Tier - Personal AI Employee_
_Powered by Qwen_
