# Qwen Processing Instructions

## Current Task: Process Items in /Needs_Action

### Step 1: Read Company Handbook
First, read the rules in `Company_Handbook.md` to understand how to process items.

### Step 2: Check /Needs_Action Folder
You have the following items to process:

**Emails (3):**
1. `EMAIL_94d230dc2223.md` - "Urgent: Invoice Request" from client@example.com (HIGH priority)
2. `EMAIL_2ba3a925b3af.md` - "Meeting Tomorrow" from partner@company.com (MEDIUM priority)
3. `EMAIL_e77a7d6bcb90.md` - "Weekly Tech Newsletter" from newsletter@tech.com (LOW priority)

**Files (5):**
- Various test files dropped in Inbox

### Step 3: Process Each Item

For each EMAIL:
1. Read the email content
2. Classify by type and priority
3. Draft a response (if needed)
4. Create approval request in `/Pending_Approval/` for sending
5. Update Dashboard.md with activity
6. Move to `/Done/` when processed

For each FILE:
1. Read the file content
2. Determine what action is needed
3. Process according to Company_Handbook.md
4. Move to `/Done/` when complete

### Step 4: Create Summary

After processing, update `Dashboard.md` with:
- Number of items processed
- Priority classifications
- Actions taken
- Pending approvals

---

## Example Email Response Draft

For the "Urgent: Invoice Request" email:

```
Subject: Re: Urgent: Invoice Request

Dear Client,

Thank you for your email. I'm preparing the invoice for January services 
and will send it to you within 24 hours.

Best regards,
AI Employee
```

---

## Approval Request Format

Create in `/Pending_Approval/`:

```markdown
---
type: approval_request
request_type: email_send
created: 2026-02-28T...
status: pending
---

# Approval Request: Email Send

## Details
- **To**: client@example.com
- **Subject**: Re: Urgent: Invoice Request
- **Priority**: High

## Draft Content
[Draft response here]

## To Approve
Move this file to `/Approved/` folder
```

---

*Follow Company_Handbook.md rules for all processing*
