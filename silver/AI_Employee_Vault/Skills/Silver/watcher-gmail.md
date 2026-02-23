---
Skill: Gmail Watcher
Type: Input Channel
Requires_Plan: No
Requires_Approval: No
Side_Effects: Creates files in Inbox/
Dependencies: []
---

# Skill: Gmail Watcher

**Purpose**: Monitor Gmail inbox for new messages and route to Bronze Inbox

**Source**: `ai_employee/watchers/gmail_watcher.py`

## Configuration

```yaml
interval_seconds: 60
oauth_required: true
state_persistence: Logs_Extended/watcher_gmail_state.md
processed_ids_storage: Logs_Extended/watcher_gmail_processed.md
```

## Environment Variables

```bash
GMAIL_OAUTH_TOKEN=your-oauth-token
GMAIL_REFRESH_TOKEN=your-refresh-token
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret
```

## Behavior

1. **Polling**: Checks Gmail every 60 seconds for new messages
2. **Duplicate Detection**: Skips already-processed message IDs
3. **State Persistence**: Saves last_check timestamp and processed_ids
4. **Restart Safety**: Resumes from last check on restart
5. **Routing**: Creates markdown files in Inbox/ with metadata

## Input Format

N/A (polls Gmail API directly)

## Output Format

Creates markdown files in `Inbox/`:

```markdown
---
Source: Gmail
Source_ID: MSG_{message_id}
Received: {ISO8601}
From: {sender}
Subject: {subject}
---

# Email: {subject}

**From**: {sender}
**Date**: {timestamp}

## Content

[Email content]
```

## Logging

Logs to Dashboard.md Watcher Triggers section:
- Timestamp
- Items found
- Status (Processed/Error)
- Duration

## Error Handling

- OAuth failures: Log warning, skip poll
- API errors: Log error, retry on next poll
- State corruption: Reset to 30 days ago

## Testing

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
uv run python -m ai_employee.watchers.gmail_watcher --test
```

## Related Skills

- Filesystem Watcher (parallel input channel)
- Bronze Inbox Intake (downstream processor)
