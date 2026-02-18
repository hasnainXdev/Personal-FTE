# 3. SKILL: Task State Mover

## Purpose
Safely move task files between state folders.

## Valid Transitions
Inbox → Needs_Action
Needs_Action → Done

## Invalid Transitions
Done → Needs_Action (Bronze restriction)

## Requirements
- Preserve file integrity.
- Update Status metadata.
- Log movement in Dashboard.md

---