---
version: 1.0
tier: Bronze
ai_engine: Qwen
---

# 🤖 Agent Skills

This document defines all AI capabilities available in Bronze Tier, powered by **Qwen**.

## Skill 1: Inbox Intake Processor

**Purpose**: Process files dropped in /Inbox and move to appropriate folders

**Trigger**: File appears in /Inbox

**Actions**:
1. Read file content
2. Classify type (task, note, reference)
3. Add metadata frontmatter
4. Move to /Needs_Action/ or /Done/

---

## Skill 2: Task Classifier

**Purpose**: Categorize items in /Needs_Action by priority and type

**Trigger**: New item in /Needs_Action

**Classification Types**:
- `email` - Email communications
- `file_drop` - Dropped files for processing
- `task` - Action items
- `reference` - Information only

**Priority Levels**:
- `high` - Urgent/ASAP keywords
- `medium` - Normal tasks
- `low` - Reference/archive

---

## Skill 3: Task Summarizer

**Purpose**: Create summaries of task content for Dashboard

**Input**: Any .md file in vault

**Output**: 2-3 line summary for Dashboard activity log

---

## Skill 4: Dashboard Updater

**Purpose**: Keep Dashboard.md current with latest activity

**Trigger**: After any task completion

**Updates**:
- Increment completed count
- Add activity row
- Update timestamp

---

## Skill 5: Task State Mover

**Purpose**: Move tasks between folders based on state

**State Flow**:
```
/Needs_Action/ → /Done/ (complete)
/Pending_Approval/ → /Approved/ (human approved)
/Pending_Approval/ → /Rejected/ (human declined)
```

---

## Skill 6: Duplicate Detector

**Purpose**: Prevent processing same item twice

**Check**: Compare against processed IDs in logs

**Action**: Skip if already processed, alert if uncertain

---

## Skill 7: Completion Evaluator

**Purpose**: Verify task is actually complete before moving to /Done/

**Checklist**:
- [ ] All subtasks done?
- [ ] Results documented?
- [ ] Dashboard updated?
- [ ] Log entry created?

---

*To add new skills, create a SKILL.md file with the same structure*
