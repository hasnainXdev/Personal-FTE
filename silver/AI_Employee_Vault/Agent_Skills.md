---
version: 2.0
tier: Silver
ai_engine: Qwen
---

# 🤖 Agent Skills - Silver Tier

This document defines all AI capabilities available in Silver Tier, powered by **Qwen**.

## Bronze Tier Skills (Included)

| Skill | Description |
|-------|-------------|
| Inbox Intake Processor | Process files dropped in /Inbox |
| Task Classifier | Categorize items by type and priority |
| Task Summarizer | Create summaries for Dashboard |
| Dashboard Updater | Keep Dashboard.md current |
| Task State Mover | Move tasks between folders |
| Duplicate Detector | Prevent reprocessing |
| Completion Evaluator | Verify task completion |

---

## Silver Tier Skills (New)

### Skill 8: Gmail Watcher

**Purpose**: Monitor Gmail for important unread emails

**Trigger**: Every 2 minutes

**Actions**:
1. Connect to Gmail API using OAuth2
2. Search for unread messages
3. Extract email content and headers
4. Classify by priority using keywords
5. Create action file in /Needs_Action/
6. Track processed message IDs

**Priority Keywords**:
- High: urgent, asap, emergency, invoice, payment
- Medium: meeting, call, deadline, review
- Low: newsletter, promo, offer

---

### Skill 9: LinkedIn Poster

**Purpose**: Create and post business updates to LinkedIn

**Trigger**: Manual or scheduled

**Actions**:
1. Generate business-focused post content
2. Create draft in /Pending_Approval/
3. Wait for human approval
4. Post via Playwright browser automation
5. Log post in /Logs/
6. Track daily post count (max 3/day)

**Posting Guidelines**:
- Maximum 3 posts per day
- Business content only
- Professional tone
- Requires approval before posting

---

### Skill 10: Plan Generator

**Purpose**: Create structured plans for multi-step tasks

**Trigger**: Task with 3+ steps detected

**Actions**:
1. Analyze task requirements
2. Break down into sequential steps
3. Create Plan.md in /Plans/
4. Track step completion
5. Update progress as steps complete
6. Archive to /Done/Plans/ when complete

**Plan Structure**:
```markdown
---
type: plan
status: pending
total_steps: N
completed_steps: 0
---

# Plan: Title

## Objective
Description

## Steps
- [ ] Step 1
- [ ] Step 2
...
```

---

### Skill 11: Approval Workflow

**Purpose**: Manage human-in-the-loop approvals

**Trigger**: Sensitive action detected

**Actions**:
1. Create approval request in /Pending_Approval/
2. Include full action details
3. Wait for human decision
4. If approved: execute action
5. If rejected: log reason and archive
6. Track approval history

**Actions Requiring Approval**:
- Email sends (always)
- LinkedIn posts (always)
- Payments > $50 (always)
- Payments to new recipients (always)
- File deletions (always)

---

### Skill 12: Scheduler

**Purpose**: Execute tasks on cron-based schedules

**Trigger**: Cron expression matches current time

**Actions**:
1. Register scheduled tasks
2. Check due tasks every 60 seconds
3. Execute task callbacks
4. Log execution results
5. Calculate next run time
6. Persist task state

**Default Scheduled Tasks**:
- Daily Briefing: 8:00 AM daily
- Email Check: Every 2 minutes (business hours)
- Weekly Review: Sunday 6:00 PM

---

### Skill 13: Daily Summary Generator

**Purpose**: Generate daily business briefings

**Trigger**: Daily at 8:00 AM

**Actions**:
1. Gather metrics from previous day
2. Count emails, files, tasks processed
3. Summarize completed work
4. List pending items
5. Create briefing in /Briefings/
6. Update Dashboard.md

**Briefing Contents**:
- Key metrics table
- Email activity summary
- File processing summary
- Completed tasks list
- Pending items list

---

### Skill 14: MCP Server Integration

**Purpose**: Expose actions via Model Context Protocol

**Tools Available**:
- `send_email` - Send emails via Gmail
- `post_linkedin` - Post to LinkedIn
- `create_approval_request` - Create approval files
- `check_approvals` - Check pending approvals
- `update_dashboard` - Update Dashboard.md

**Usage**:
```bash
# Start MCP server
python mcp_server/server.py ./AI_Employee_Vault
```

---

## Skill Implementation Files

| Skill | File |
|-------|------|
| Gmail Watcher | `src/watchers/gmail_watcher.py` |
| LinkedIn Poster | `src/services/linkedin_service.py` |
| Plan Generator | `src/services/plan_service.py` |
| Approval Workflow | `src/services/approval_service.py` |
| Scheduler | `src/scheduler/cron_runner.py` |
| Daily Summary | `src/scheduler/daily_summary.py` |
| MCP Server | `mcp_server/server.py` |

---

## Using Agent Skills with Qwen

### Example Prompts

```bash
# Process emails
qwen "Check /Needs_Action for email items and draft responses"

# Create a plan
qwen "Create a Plan.md for processing the invoice files"

# Generate LinkedIn post
qwen "Generate a business post about our latest project completion"

# Check approvals
qwen "Check /Pending_Approval and summarize what needs my attention"

# Daily summary
qwen "Generate a daily summary briefing for yesterday"
```

---

## Skill Orchestration

Skills work together in the Silver Tier architecture:

```
Watcher detects → Plan Generator creates plan → 
Approval Workflow requests approval → Human approves → 
MCP Server executes → Daily Summary logs results
```

---

*Silver Tier - 14 Total Skills (7 Bronze + 7 Silver)*
*Powered by Qwen*
