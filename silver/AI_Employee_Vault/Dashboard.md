# Dashboard

## Bronze Logs

<!-- Bronze Tier logs remain here - unchanged -->

---

## Silver Logs

### Watcher Triggers

| Timestamp | Watcher | Items Found | Status | Duration |
|-----------|---------|-------------|--------|----------|
| 2026-02-22T19:04:38Z | filesystem | 1 | Processed | <1s |

### Plan Creations

| Timestamp | Plan ID | Risk Level | Approval Required | Objective |
| 2026-02-23T12:53:15.099469+00:00 | Plan_20260223_002 | Low | No | Test plan generation in sandbox mode |
| 2026-02-23T06:26:15.088430+00:00 | Plan_20260223_001 | Low | No | Test plan generation in sandbox mode |
|-----------|---------|------------|-------------------|-----------|
| *No plans created yet* | | | | |

### Approval Decisions

| Timestamp | Action ID | Decision | Decision Time | Reviewer Notes |
|-----------|-----------|----------|---------------|----------------|
| *No approval decisions yet* | | | | |

### MCP Actions

| Timestamp | Action | Result | Duration | Status |
|-----------|--------|--------|----------|--------|
| 2026-02-22T19:05:00Z | health_check | healthy | <100ms | success |
| 2026-02-22T19:05:00Z | actions_list | 4 actions | <100ms | success |

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
