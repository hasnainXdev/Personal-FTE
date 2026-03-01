---
Skill: Approval Request
Type: Approval Manager
Requires_Plan: Yes (for high-risk actions)
Requires_Approval: No
Side_Effects: Creates Proposed_Action.md, moves to Done/Rejected on rejection
Dependencies:
  - Plan Generator
---

# Skill: Approval Request

**Purpose**: Manage human-in-the-loop approval workflow for high-risk actions

**Source**: `ai_employee/services/approval_request.py`

## Configuration

```yaml
actions_dir: Proposed_Actions/
polling_interval: 60  # seconds
timeout_minutes: 60
done_dir: Done/Rejected
```

## Behavior

1. **Action Creation**: Creates Proposed_Action.md with action summary and plan reference
2. **Approval Polling**: Checks for approval decisions every 60 seconds
3. **Decision Handling**:
   - Approved: Triggers MCP execution
   - Rejected: Moves to Done/Rejected, logs rejection
4. **Timeout Handling**: Times out after 60 minutes (configurable)

## Input Format

Plan reference and action summary

## Output Format

Creates Proposed_Action.md in `Proposed_Actions/`:

```markdown
---
Title: Action title
Plan_Reference: Plans/Plan_YYYYMMDD_NN.md
Risk_Level: Medium
Summary: Human-readable summary
Approved: PENDING
Created: ISO8601
---

## Approval Instructions

Edit Approved field to Yes or No
```

## Approval Workflow

```
1. AI creates Proposed_Action.md with Approved: PENDING
2. Human reviews in Obsidian, edits: Approved: Yes or Approved: No
3. Polling detects mtime change, reads Approved field
4. If Yes → execute via MCP
   If No → log rejection, move to Done/Rejected
```

## Logging

Logs to Dashboard.md Approval Decisions section:
- Timestamp
- Action ID
- Decision (Approved/Rejected)
- Decision Time (minutes from creation)
- Reviewer Notes

## Related Skills

- Plan Generator (upstream, provides plan reference)
- MCP Execution (downstream, executes approved actions)
- Orchestrator (coordinates workflow)
