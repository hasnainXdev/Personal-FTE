# 📁 Silver Tier - File Naming Patterns

**Date**: 2026-03-03  
**Purpose**: Document actual file naming conventions used

---

## Email Action Files

**Pattern**: `EMAIL_<gmail_id>.md`

**Location**: `/Needs_Action/`

**Example**:
```
EMAIL_19caedfdd48e.md
EMAIL_19cae85dc95d.md
EMAIL_19caa2d5af8b.md
```

**Frontmatter**:
```yaml
---
type: email
file_id: EMAIL_19caedfdd48e
gmail_id: 19caedfdd48e68e8
from: Pinterest <recommendations@discover.pinterest.com>
subject: Hasnainop, you have a good eye
date: Mon, 02 Mar 2026 14:07:12 +0000
received: 2026-03-03T01:49:22.324438
priority: medium
status: pending
labels: unread
---
```

**Workflow**:
1. Created by: `fetch_gmail_emails.py` or GmailWatcher
2. Processed from: `/Needs_Action/`
3. Archived to: `/Done/`

---

## File Drop Action Files

**Pattern**: `FILE_<unique_id>.md` + original file

**Location**: `/Needs_Action/`

**Example**:
```
FILE_cac449c4e077.md
FILE_cac449c4e077_silver_test.txt
```

**Frontmatter**:
```yaml
---
type: file_drop
file_id: FILE_cac449c4e077
original_name: silver_test.txt
size: 21
received: 2026-03-02T02:23:45
priority: medium
status: pending
source: inbox
---
```

**Workflow**:
1. Created by: FileSystemWatcher
2. Processed from: `/Needs_Action/`
3. Archived to: `/Done/`

---

## LinkedIn Post Drafts

**Pattern**: `LINKEDIN_POST_YYYYMMDD_HHMMSS.md`

**Location**: `/Pending_Approval/` → `/Approved/` → `/Done/LinkedIn/`

**Example**:
```
LINKEDIN_POST_20260302_230233.md
```

**Frontmatter**:
```yaml
---
type: linkedin_post_draft
file_id: 20260302_230233
created: 2026-03-02T23:02:33.531036
status: pending_approval
posts_today: 0
max_posts: 3
---
```

**Workflow**:
1. Created by: `linkedin_service.py` or MCP tool
2. Approval from: `/Pending_Approval/`
3. Moved to: `/Approved/` (for posting)
4. Archived to: `/Done/LinkedIn/`

---

## Approval Requests

**Pattern**: `APPROVAL_<TYPE>_YYYYMMDD_HHMMSS.md`

**Location**: `/Pending_Approval/` → `/Approved/` or `/Rejected/`

**Example**:
```
APPROVAL_EMAIL_SEND_20260302_120000.md
APPROVAL_PAYMENT_20260302_120500.md
APPROVAL_LINKEDIN_POST_20260302_121000.md
```

**Frontmatter**:
```yaml
---
type: approval_request
file_id: 20260302_120000
request_type: email_send
created: 2026-03-02T12:00:00
status: pending
expires: 2026-03-03T12:00:00
---
```

**Workflow**:
1. Created by: `approval_service.py` or MCP tool
2. Approval from: `/Pending_Approval/`
3. Moved to: `/Approved/` or `/Rejected/`
4. Archived to: `/Done/Approvals/`

---

## State Tracking Files

**Pattern**: `watcher_<type>_state.md`

**Location**: `/Logs_Extended/`

**Example**:
```
watcher_filesystem_state.md
watcher_gmail_state.md
```

**Frontmatter**:
```yaml
---
type: gmail_watcher_state
last_check: 2026-03-03T01:49:25
processed_count: 10
---
```

**Content**:
```markdown
# Gmail Watcher State

## Processed Message IDs

processed_id: 19caedfdd48e
processed_id: 19cae85dc95d
processed_id: 19caa2d5af8b
```

**Purpose**: Track processed items to avoid duplicates

---

## Log Files

**Pattern**: `<type>_YYYY-MM-DD.md`

**Location**: `/Logs/`

**Example**:
```
gmail_2026-03-03.md
linkedin_2026-03-03.md
approvals_2026-03-03.md
email_sent_2026-03-03.md
```

**Frontmatter**:
```yaml
---
type: gmail_log
date: 2026-03-03
---
```

**Purpose**: Daily activity logs

---

## Plan Files

**Pattern**: `Plan_YYYYMMDD_NN.md`

**Location**: `/Plans/` → `/Done/Plans/`

**Example**:
```
Plan_20260303_01.md
```

**Frontmatter**:
```yaml
---
type: plan
file_id: Plan_20260303_01
created: 2026-03-03T08:00:00
status: in_progress
steps_total: 5
steps_completed: 0
---
```

**Purpose**: Multi-step task tracking (3+ steps)

---

## Daily Briefings

**Pattern**: `Daily_YYYY-MM-DD.md`

**Location**: `/Briefings/`

**Example**:
```
Daily_2026-03-03.md
```

**Frontmatter**:
```yaml
---
type: daily_briefing
date: 2026-03-03
generated: 2026-03-03T08:00:00
---
```

**Purpose**: Daily summary reports

---

## Quick Reference Table

| File Type | Pattern | Location | Created By |
|-----------|---------|----------|------------|
| Email Action | `EMAIL_<gmail_id>.md` | `/Needs_Action/` | GmailWatcher |
| File Drop | `FILE_<id>.md` | `/Needs_Action/` | FileSystemWatcher |
| LinkedIn Draft | `LINKEDIN_POST_YYYYMMDD_HHMMSS.md` | `/Pending_Approval/` | LinkedInService |
| Approval Request | `APPROVAL_TYPE_YYYYMMDD_HHMMSS.md` | `/Pending_Approval/` | ApprovalService |
| State Track | `watcher_<type>_state.md` | `/Logs_Extended/` | Watchers |
| Activity Log | `<type>_YYYY-MM-DD.md` | `/Logs/` | Services |
| Plan | `Plan_YYYYMMDD_NN.md` | `/Plans/` | PlanService |
| Briefing | `Daily_YYYY-MM-DD.md` | `/Briefings/` | DailySummary |

---

## Common Commands

### List Files by Type
```bash
# Email action files
ls AI_Employee_Vault/Needs_Action/EMAIL_*.md

# File drop files
ls AI_Employee_Vault/Needs_Action/FILE_*.md

# LinkedIn drafts
ls AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md

# Approval requests
ls AI_Employee_Vault/Pending_Approval/APPROVAL_*.md

# Logs
ls AI_Employee_Vault/Logs/*.md
```

### Move Files (Workflow)
```bash
# Archive processed emails
mv AI_Employee_Vault/Needs_Action/EMAIL_*.md AI_Employee_Vault/Done/

# Archive processed files
mv AI_Employee_Vault/Needs_Action/FILE_*.md AI_Employee_Vault/Done/

# Approve LinkedIn post
mv AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md AI_Employee_Vault/Approved/

# Archive posted LinkedIn
mv AI_Employee_Vault/Approved/LINKEDIN_POST_*.md AI_Employee_Vault/Done/LinkedIn/

# Archive approvals
mv AI_Employee_Vault/Approved/*.md AI_Employee_Vault/Done/Approvals/
```

---

*File Naming Patterns Documentation - 2026-03-03*
