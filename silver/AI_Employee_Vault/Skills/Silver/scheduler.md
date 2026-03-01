---
Skill: Scheduler
Type: Time-Based Trigger
Requires_Plan: No
Requires_Approval: No
Side_Effects: Executes scheduled tasks, logs to Dashboard.md
Dependencies: []
---

# Skill: Scheduler

**Purpose**: Execute routine tasks on schedule without user initiation

**Source**: `ai_employee/scheduler/cron_runner.py`

## Configuration

```yaml
scheduled_tasks_dir: Scheduled_Tasks/
dashboard_path: Dashboard.md
missed_schedule_threshold: 3600  # seconds
```

## Supported Schedules

- **Native cron** (Linux/WSL): Standard 5-field cron format
- **Windows Task Scheduler**: Via scheduled tasks configuration

## Cron Format

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sunday=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

## Examples

```bash
# Daily at 9 AM
0 9 * * *

# Every hour
0 * * * *

# Every 15 minutes
*/15 * * * *

# Weekdays at 8 AM
0 8 * * 1-5
```

## Task Configuration

Creates Scheduled_Tasks/{task_name}.md:

```markdown
---
Name: Daily Summary Generation
Cron: 0 9 * * *
Enabled: true
Last_Run: ISO8601
Next_Run: ISO8601
Missed_Schedule: false
Execution_Count: 15
---

## Task Configuration

```yaml
action: generate_daily_summary
parameters:
  date_range: yesterday
  include_watchers: true
```
```

## Restart Safety

- Checks last_run timestamp on start
- If missed execution detected (>1 hour overdue), executes with "missed_schedule: true" flag
- Persists state to Scheduled_Tasks/ directory

## Logging

Logs to Dashboard.md Scheduled Tasks section:
- Timestamp
- Task name
- Next run time
- Status (Completed/Failed/Missed)
- Notes

## Related Skills

- Daily Summary Generator (scheduled task example)
- Watchers (can be triggered on schedule)
