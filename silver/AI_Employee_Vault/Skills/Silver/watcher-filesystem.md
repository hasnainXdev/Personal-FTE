---
Skill: Filesystem Watcher
Type: Input Channel
Requires_Plan: No
Requires_Approval: No
Side_Effects: Creates files in Inbox/
Dependencies: []
---

# Skill: Filesystem Watcher

**Purpose**: Monitor directory for new files and route to Bronze Inbox

**Source**: `ai_employee/watchers/filesystem_watcher.py`

## Configuration

```yaml
interval_seconds: 60
watch_directory: AI_Employee_Vault/Inbox_Drop
file_patterns:
  - "*.txt"
  - "*.md"
  - "*.json"
recursive: false
state_persistence: Logs_Extended/watcher_filesystem_state.md
processed_ids_storage: Logs_Extended/watcher_filesystem_processed.md
```

## Environment Variables

None required (uses filesystem permissions)

## Behavior

1. **Polling**: Checks watch directory every 60 seconds
2. **Pattern Matching**: Only processes files matching configured patterns
3. **Duplicate Detection**: Uses file path + mtime hash for uniqueness
4. **State Persistence**: Saves last_check timestamp and processed file IDs
5. **Restart Safety**: Resumes from last check on restart
6. **Routing**: Creates markdown files in Inbox/ with file content

## Input Format

Files dropped in `AI_Employee_Vault/Inbox_Drop/`

## Output Format

Creates markdown files in `Inbox/`:

```markdown
---
Source: Filesystem
Source_ID: FILE_{hash}
Received: {ISO8601}
File_Path: {relative_path}
File_Size: {bytes}
---

# File: {filename}

**Path**: {relative_path}
**Modified**: {timestamp}

## Content

```
[file content]
```
```

## Logging

Logs to Dashboard.md Watcher Triggers section:
- Timestamp
- Items found
- Status (Processed/Error)
- Duration

## Error Handling

- Permission errors: Log warning, skip file
- Encoding errors: Mark as binary, skip content
- State corruption: Reset to 30 days ago

## Testing

```bash
cd /mnt/d/it-course/hackathons/personal-FTE/silver
echo "Test content" > AI_Employee_Vault/Inbox_Drop/test.txt
uv run python -m ai_employee.watchers.filesystem_watcher --test
```

## Related Skills

- Gmail Watcher (parallel input channel)
- Bronze Inbox Intake (downstream processor)
