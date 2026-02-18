# Agent Skills

This document defines all agent skills that the AI Employee can execute.
Each skill follows a standardized format with input/output specifications.

---

## Skill: ProcessFile

- **Purpose**: Process markdown files from filesystem input source
- **Input Format**:
  ```json
  {
    "file_path": "/absolute/path/to/file.md",
    "content": "markdown content string"
  }
  ```
- **Output Format**: Markdown file created in appropriate vault folder (Inbox/)
- **Invocation Method**: `python -m ai_employee.skills.process_file <file_path>`
- **Expected Behavior**:
  1. Read the input file
  2. Validate markdown content
  3. Generate unique ID (SHA256 hash of content)
  4. Check for duplicates (idempotency)
  5. Write to Inbox/ folder
  6. Log operation to Dashboard.md
- **Failure Handling Notes**:
  - If file not found: Log error, skip processing
  - If invalid markdown: Log error, move to Needs_Action for manual review
  - If duplicate detected: Log as skipped, no action taken
  - If write fails: Log error, retry with exponential backoff (3 attempts)

---

## Skill: ProcessEmail (Gmail Support)

- **Purpose**: Process emails from Gmail inbox
- **Input Format**:
  ```json
  {
    "from": "sender @example.com",
    "subject": "Email subject line",
    "body": "Email body content",
    "received_at": "2026-02-16T10:30:00Z",
    "message_id": "<unique-message-id @gmail.com>"
  }
  ```
- **Output Format**: Markdown file created in Inbox/ with email metadata
- **Invocation Method**: `python -m ai_employee.skills.process_email`
- **Expected Behavior**:
  1. Connect to Gmail via IMAP
  2. Fetch unread emails
  3. Parse email content and metadata
  4. Create markdown file with email content
  5. Write to Inbox/ folder
  6. Mark email as read
  7. Log operation to Dashboard.md
- **Failure Handling Notes**:
  - If IMAP connection fails: Retry with exponential backoff
  - If email parse fails: Log error, skip email
  - If write fails: Log error, retain email as unread for retry

---

## Skill: ExtractTasks

- **Purpose**: Extract actionable tasks from markdown content
- **Input Format**: Markdown file path containing potential tasks
- **Output Format**: Structured task list in markdown format
- **Invocation Method**: `python -m ai_employee.skills.extract_tasks <file_path>`
- **Expected Behavior**:
  1. Read input markdown file
  2. Identify task-like patterns (checkboxes, action items)
  3. Extract and format as structured task list
  4. Update original file with extracted tasks
  5. Move file to Needs_Action/ if tasks require action
  6. Log operation to Dashboard.md
- **Failure Handling Notes**:
  - If no tasks found: Log as informational, move to Done/
  - If parse fails: Log error, keep in Inbox for manual review

---

## Adding New Skills

To add a new agent skill:

1. Create a new section in this file with the skill definition
2. Implement the skill in `src/ai_employee/skills/` directory
3. Register the skill in the skill executor
4. Test the skill with sample inputs
5. Update documentation

### Skill Template

```markdown
## Skill: [Skill Name]

- **Purpose**: [What this skill does]
- **Input Format**: [Expected input structure with example]
- **Output Format**: [Produced output structure with example]
- **Invocation Method**: [How to call this skill]
- **Expected Behavior**: [Step-by-step normal operation]
- **Failure Handling Notes**: [Error recovery steps]
```
