---
Skill: LinkedIn Generator
Type: Content Generator
Requires_Plan: Yes
Requires_Approval: Yes
Side_Effects: Creates drafts in Proposed_Actions/, publishes to LinkedIn
Dependencies:
  - Task Classifier
  - Plan Generator
  - Approval Request
---

# Skill: LinkedIn Generator

**Purpose**: Generate LinkedIn post drafts and execute posting through approval workflow

**Source**: `ai_employee/services/linkedin_generator.py` (optional enhancement)

## Configuration

```yaml
draft_storage: Proposed_Actions/
url_storage: Logs_Extended/linkedin_posts.md
approval_required: true
```

## Environment Variables

```bash
LINKEDIN_ACCESS_TOKEN=your-access-token
LINKEDIN_ORGANIZATION_ID=your-org-id (optional)
```

## Behavior

1. **Content Generation**: Creates draft LinkedIn posts from task content
2. **Draft Storage**: Saves drafts to Proposed_Actions/ for approval
3. **Approval Integration**: Triggers Approval Request skill after draft creation
4. **MCP Execution**: Calls MCP server post_linkedin action after approval
5. **URL Storage**: Captures and stores LinkedIn post URL after publishing

## Input Format

Task from Bronze Inbox with LinkedIn-related content

## Output Format

Draft markdown in `Proposed_Actions/`:

```markdown
---
Title: LinkedIn Post Draft
Plan_Reference: Plans/Plan_YYYYMMDD_NN.md
Risk_Level: Medium
Approved: PENDING
---

## Draft Content

[LinkedIn post text]
```

## Logging

- Draft creation logged to Dashboard.md Plan Creations
- Approval decision logged to Dashboard.md Approval Decisions
- Post execution logged to Dashboard.md MCP Actions
- Post URL stored in Logs_Extended/linkedin_posts.md

## Related Skills

- Plan Generator (creates execution plan)
- Approval Request (manages approval workflow)
- MCP Execution (publishes to LinkedIn)
