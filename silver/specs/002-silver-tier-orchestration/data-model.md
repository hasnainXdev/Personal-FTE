# Data Model: Silver Tier Orchestration

**Feature**: Silver Tier Orchestration
**Created**: 2026-02-20
**Version**: 1.0.0

---

## Core Entities

### 1. Watcher

**Purpose**: Independent input channel monitor that detects and logs triggers from external sources

**Storage**: `Skills/Silver/watcher-{name}.md` (skill definition) + `Logs_Extended/watcher-{name}.md` (state)

**Fields**:
```yaml
name: string                    # Unique identifier (e.g., "gmail", "filesystem")
source_type: string             # gmail | filesystem | whatsapp | linkedin
enabled: boolean                # Watcher active flag
interval_seconds: number        # Polling interval (default: 60)
last_check_timestamp: ISO8601   # Last poll time
processed_ids: string[]         # Already-processed item IDs (for duplicate detection)
status: string                  # idle | polling | error
error_context: string | null    # Last error message (if status=error)
```

**Relationships**:
- Outputs → Bronze Inbox/ (via standard intake format)
- Logs → Dashboard.md (Watcher Triggers section)
- State → Logs_Extended/watcher-{name}.md (persistent state)

**Validation Rules**:
- `interval_seconds` MUST be >= 30 (prevent API rate limit violations)
- `processed_ids` MUST be pruned to last 1000 IDs (prevent unbounded growth)
- `last_check_timestamp` MUST persist across restarts

---

### 2. Plan

**Purpose**: Structured execution document containing objective, steps, risk assessment, and approval requirements

**Storage**: `Plans/Plan_{YYYYMMDD}_{NN}.md`

**Fields**:
```yaml
title: string                   # Short descriptive name
objective: string               # What this plan achieves
risk_level: enum                # Low | Medium | High
approval_required: boolean      # Whether human approval needed
created_timestamp: ISO8601      # Plan creation time
status: enum                    # Draft | Active | Completed | Rolled_Back
steps:                          # Numbered execution steps
  - step_number: integer
    skill_name: string
    description: string
    dependencies: integer[]     # Step numbers this depends on
expected_outcome: string        # Success criteria
rollback_strategy: string       # How to undo if failed
executed_timestamp: ISO8601 | null
result_summary: string | null   # Execution outcome
```

**Relationships**:
- Referenced by → Proposed_Action.md
- Executed by → Orchestrator skill
- Logs → Dashboard.md (Plan Creations section)

**Validation Rules**:
- `risk_level` MUST be Low/Medium/High
- `steps` MUST have at least 1 step
- `steps[].step_number` MUST be sequential (1, 2, 3...)
- `steps[].dependencies` MUST reference earlier step numbers only
- Plan MUST be saved before execution begins

**Example**:
```markdown
---
Title: Post LinkedIn business update
Objective: Generate and publish LinkedIn post about quarterly achievements
Risk_Level: Medium
Approval_Required: Yes
Created: 2026-02-20T10:30:00Z
Status: Draft
---

## Steps

1. **Generate Content** (Skill: LinkedIn Generator)
   - Draft LinkedIn post based on quarterly metrics
   - Dependencies: []

2. **Save Draft** (Skill: File Writer)
   - Store draft in Proposed_Actions/
   - Dependencies: [1]

3. **Request Approval** (Skill: Approval Request)
   - Notify user, wait for approval
   - Dependencies: [2]

4. **Execute Post** (Skill: MCP Execution)
   - Send to MCP server for posting
   - Dependencies: [3]

## Expected Outcome

LinkedIn post published, URL stored in vault, Dashboard logged

## Rollback Strategy

If post fails: delete draft, log error, notify user
```

---

### 3. Proposed_Action

**Purpose**: Approval request document containing action summary, plan reference, risk level, and approval status

**Storage**: `Proposed_Actions/Action_{YYYYMMDD}_{NN}.md`

**Fields**:
```yaml
title: string                   # Short action description
plan_reference: string          # Path to Plan.md being requested
risk_level: enum                # Low | Medium | High
summary: string                 # Human-readable action summary
approved: enum                  # PENDING | Yes | No
created_timestamp: ISO8601      # Request creation time
reviewed_timestamp: ISO8601 | null  # When human reviewed
reviewer_notes: string | null   # Optional human comments
executed_timestamp: ISO8601 | null
result: string | null           # Execution outcome or rejection reason
```

**Relationships**:
- References → Plan.md
- Triggers → MCP action (if approved)
- Logs → Dashboard.md (Approval Decisions section)

**Validation Rules**:
- `approved` MUST start as PENDING
- `approved` can only transition: PENDING → Yes OR PENDING → No
- Execution MUST NOT proceed unless `approved` = Yes
- All approval decisions MUST be logged

**Example**:
```markdown
---
Title: Post LinkedIn business update
Plan_Reference: Plans/Plan_20260220_001.md
Risk_Level: Medium
Summary: Publish quarterly achievements post to LinkedIn (draft attached)
Approved: PENDING
Created: 2026-02-20T10:35:00Z
Reviewed: null
Reviewer_Notes: null
Executed: null
Result: null
---

## Draft Content

[LinkedIn post text here]

## Approval Instructions

1. Review draft content above
2. Check Plan reference for full execution steps
3. Edit this file: set "Approved: Yes" or "Approved: No"
4. Save file - system will detect change and act accordingly

## Decision

Approved: [PENDING]  ← Edit this line

Reviewer_Notes: [Optional - add your comments here]
```

---

### 4. Scheduled_Task

**Purpose**: Time-based trigger that executes predefined workflows without user initiation

**Storage**: `Scheduled_Tasks/{task_name}.md`

**Fields**:
```yaml
name: string                    # Unique task identifier
cron_expression: string         # Cron schedule (e.g., "0 9 * * *")
enabled: boolean                # Task active flag
last_run: ISO8601 | null        # Last execution time
next_run: ISO8601 | null        # Next scheduled time
task_config: object             # Task-specific configuration
missed_schedule: boolean        # True if executing missed run
execution_count: integer        # Total times executed
```

**Relationships**:
- Triggers → Orchestrator (with scheduled task context)
- Logs → Dashboard.md (Scheduled Tasks section)

**Validation Rules**:
- `cron_expression` MUST be valid 5-field cron format
- `next_run` MUST be calculated from `cron_expression` + `last_run`
- Task MUST be restart-safe (handle missed executions)

**Example**:
```markdown
---
Name: Daily Summary Generation
Cron: 0 9 * * *  (Daily at 9 AM)
Enabled: true
Last_Run: 2026-02-20T09:00:00Z
Next_Run: 2026-02-21T09:00:00Z
Missed_Schedule: false
Execution_Count: 15
---

## Task Configuration

```yaml
action: generate_daily_summary
parameters:
  date_range: yesterday
  include_watchers: true
  include_mcp_actions: true
output: Dashboard.md
```

## Execution History

| Date | Status | Duration | Notes |
|------|--------|----------|-------|
| 2026-02-20 | Success | 1.2s | Normal execution |
| 2026-02-19 | Success | 1.1s | Normal execution |
```

---

### 5. MCP_Action_Log

**Purpose**: Comprehensive audit trail of all external actions routed through MCP server

**Storage**: `mcp_server/logs/mcp_actions.md` (append-only)

**Fields**:
```yaml
timestamp: ISO8601              # When action executed
action_type: string             # send_email | post_linkedin | fetch_url | etc.
request_payload: object         # Full request sent to MCP
response_payload: object        # Full response from MCP
status: enum                    # success | failure | timeout
error_context: string | null    # Error details (if failure)
duration_ms: number             # Execution duration
plan_reference: string | null   # Associated Plan.md (if applicable)
approval_reference: string | null  # Associated Proposed_Action.md
```

**Relationships**:
- Summarized in → Dashboard.md (MCP Actions section)
- Referenced by → Plan execution results

**Validation Rules**:
- Log entry MUST be created before action execution
- Log MUST be append-only (no edits after creation)
- Failed actions MUST include error_context
- Sensitive data (passwords, tokens) MUST be redacted

**Example**:
```markdown
## MCP Action Log Entry

**Timestamp**: 2026-02-20T10:11:23Z
**Action**: post_linkedin
**Request**:
```json
{
  "content": "Excited to share our Q1 achievements...",
  "draft_url": "Proposed_Actions/Action_20260220_001.md"
}
```
**Response**:
```json
{
  "success": true,
  "result": {
    "post_url": "https://www.linkedin.com/posts/user_123456"
  }
}
```
**Status**: success
**Duration**: 2340ms
**Plan Reference**: Plans/Plan_20260220_001.md
**Approval Reference**: Proposed_Actions/Action_20260220_001.md
```

---

## State Transitions

### Plan State Machine

```
┌─────────┐
│  Draft  │ ← Plan created, not yet executing
└────┬────┘
     │ Start Execution
     ▼
┌─────────┐
│ Active  │ ← Currently executing steps
└────┬────┘
     ├──────────────┐
     │ Success      │ Failure/Rollback
     ▼              ▼
┌───────────┐  ┌─────────────┐
│ Completed │  │ Rolled_Back │
└───────────┘  └─────────────┘
```

### Proposed_Action State Machine

```
┌──────────┐
│ PENDING  │ ← Awaiting human review
└────┬─────┘
     ├──────────────┐
     │ Approved:Yes │ Approved:No
     ▼              ▼
┌───────────┐  ┌──────────┐
│ Executing │  │ Rejected │
└─────┬─────┘  └──────────┘
      │
      │ Complete
      ▼
┌───────────┐
│ Completed │
└───────────┘
```

### Scheduled_Task State Machine

```
┌─────────┐
│ Enabled │ ──────────────┐
└────┬────┘               │
     │ Trigger            │
     ▼                    │
┌───────────┐             │
│ Executing │ ── Failure ─┤ (retry/continue)
└─────┬─────┘             │
      │                   │
      │ Success           │
      ▼                   │
┌───────────┐ ────────────┘
│ Completed │
│ (calculate next_run)    │
└───────────┘
```

---

## Entity Relationships Diagram

```
┌─────────────┐
│   Watcher   │
└──────┬──────┘
       │ triggers
       ▼
┌─────────────┐     references     ┌─────────────┐
│     Plan    │◄───────────────────│Proposed_Action│
└──────┬──────┘                    └──────┬────────┘
       │                                  │
       │ executes                         │ triggers
       ▼                                  ▼
┌─────────────┐                    ┌─────────────┐
│Orchestrator │                    │  MCP Server │
└──────┬──────┘                    └──────┬────────┘
       │                                  │
       │ logs                             │ logs
       ▼                                  ▼
┌─────────────┐                    ┌─────────────┐
│  Dashboard  │                    │MCP_Action_Log│
└─────────────┘                    └─────────────┘

┌──────────────┐
│Scheduled_Task│
└──────┬───────┘
       │ triggers
       ▼
┌─────────────┐
│Orchestrator │
└─────────────┘
```

---

## Validation Summary

| Entity | Storage | Validation Rules | State Transitions |
|--------|---------|------------------|-------------------|
| Watcher | Logs_Extended/ | interval >= 30s, prune IDs | idle ↔ polling ↔ error |
| Plan | Plans/ | sequential steps, valid risk | Draft → Active → Completed/Rolled_Back |
| Proposed_Action | Proposed_Actions/ | PENDING→Yes/No, log decisions | PENDING → Executing/Rejected |
| Scheduled_Task | Scheduled_Tasks/ | valid cron, calculate next_run | Enabled → Executing → Completed |
| MCP_Action_Log | mcp_server/logs/ | append-only, redact secrets | N/A (log only) |

---

## Next Steps

1. ✅ Data model complete
2. Generate API contracts (contracts/mcp-interface.md, contracts/watcher-contract.md)
3. Create quickstart.md (setup guide)
4. Run update-agent-context.sh
