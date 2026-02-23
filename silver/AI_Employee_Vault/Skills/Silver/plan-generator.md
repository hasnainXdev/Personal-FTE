---
Skill: Plan Generator
Type: Planner
Requires_Plan: No
Requires_Approval: No
Side_Effects: Creates Plan.md in Plans/
Dependencies:
  - Inbox Intake
  - Task Classifier
---

# Skill: Plan Generator

**Purpose**: Generate structured execution plans for complex tasks

**Source**: `ai_employee/services/plan_generator.py`

## Configuration

```yaml
plans_dir: Plans/
risk_assessment: automatic
approval_trigger: automatic
```

## Trigger Conditions

Plan generation is triggered when:
- Task requires 3+ skill invocations
- External action required (MCP server call)
- High-risk task detected
- Business posting (LinkedIn, external communication)

## Risk Assessment Heuristics

| Condition | Risk Level | Approval Required |
|-----------|------------|-------------------|
| Internal state change only | Low | No |
| Single external read (fetch) | Low | No |
| Single external write (post/email) | Medium | Yes |
| Multi-step external workflow | High | Yes |
| Irreversible action (delete) | High | Yes |

## Output Format

Creates Plan.md in `Plans/`:

```markdown
---
Title: Plan title
Objective: What this plan achieves
Risk_Level: Low|Medium|High
Approval_Required: Yes|No
Created: ISO8601
Status: Draft
---

## Steps

1. **Skill Name**
   - Step description

## Expected Outcome

Success criteria

## Rollback Strategy

How to undo if failed
```

## Logging

Logs to Dashboard.md Plan Creations section:
- Timestamp
- Plan ID
- Risk Level
- Approval Required flag
- Objective

## Related Skills

- Task Classifier (upstream trigger)
- Approval Request (downstream for high-risk plans)
- Orchestrator (executes plan steps)
