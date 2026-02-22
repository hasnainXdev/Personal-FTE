# Dashboard

## Bronze Logs

<!-- Bronze Tier logs remain here - unchanged -->

---

## Silver Logs

### Watcher Triggers

| Timestamp | Watcher | Items Found | Status | Duration |
|-----------|---------|-------------|--------|----------|
| *No watcher triggers yet* | | | | |

### Plan Creations

| Timestamp | Plan ID | Risk Level | Approval Required | Objective |
| 2026-02-22T06:43:05.589084+00:00 | Plan_20260222_001 | Medium | Yes | Test objective |
|-----------|---------|------------|-------------------|-----------|
| *No plans created yet* | | | | |

### Approval Decisions

| Timestamp | Action ID | Decision | Decision Time | Reviewer Notes |
|-----------|-----------|----------|---------------|----------------|
| *No approval decisions yet* | | | | |

### MCP Actions

| Timestamp | Action | Result | Duration | Status |
|-----------|--------|--------|----------|--------|
| *No MCP actions yet* | | | | |

### Scheduled Tasks

| Timestamp | Task | Next Run | Status | Notes |
|-----------|------|----------|--------|-------|
| *No scheduled tasks yet* | | | | |

---

## Log Format Reference

### Watcher Trigger Entry

```markdown
- **Timestamp**: ISO8601
- **Watcher**: gmail | filesystem | etc.
- **Items Found**: count
- **Status**: Processed | Error
- **Duration**: seconds
```

### Plan Creation Entry

```markdown
- **Timestamp**: ISO8601
- **Plan ID**: Plan_YYYYMMDD_NN
- **Risk Level**: Low | Medium | High
- **Approval Required**: Yes | No
- **Objective**: Brief description
```

### Approval Decision Entry

```markdown
- **Timestamp**: ISO8601
- **Action ID**: Action_YYYYMMDD_NN
- **Decision**: Approved | Rejected
- **Decision Time**: minutes from creation
- **Reviewer Notes**: Optional comments
```

### MCP Action Entry

```markdown
- **Timestamp**: ISO8601
- **Action**: send_email | post_linkedin | fetch_url | etc.
- **Result**: Success (URL) | Error message
- **Duration**: milliseconds
- **Status**: success | failure
```

### Scheduled Task Entry

```markdown
- **Timestamp**: ISO8601
- **Task**: Task name
- **Next Run**: ISO8601
- **Status**: Completed | Failed | Missed
- **Notes**: Additional context
```
