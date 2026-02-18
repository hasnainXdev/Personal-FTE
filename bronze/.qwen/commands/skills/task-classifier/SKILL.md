# 2. SKILL: Task Classifier

## Purpose
Determine whether a task requires action.

## Input
Markdown task file from /Inbox

## Evaluation Criteria
- Does it contain a request?
- Is a response expected?
- Is there a deadline?
- Is there a verb requiring action?

## Decision Outcomes

IF action required:
→ Move to /Needs_Action
→ Update Status: Needs_Action

IF informational only:
→ Move to /Done
→ Update Status: Done

## Constraints
- Must not change file content except Status field.
- Must log decision in Dashboard.

---