# 7. SKILL: Completion Evaluator

## Purpose

Determine if a task in /Needs_Action is complete.

## Evaluation Criteria

- Contains confirmation text
- Contains "Done" marker
- Contains resolution message

## Behavior

If completed:

- Move file to /Done
- Update Status: Done
- Log event

If incomplete:

- Do nothing

---
