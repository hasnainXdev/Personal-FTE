---
Name: Scheduled Task Template
Cron: 0 9 * * *
Enabled: true
Last_Run: null
Next_Run: null
Missed_Schedule: false
Execution_Count: 0
---

# Scheduled Task: [Task Name]

**Cron Expression**: [5-field cron format]

**Enabled**: true

**Next Run**: [Auto-calculated]

## Task Configuration

```yaml
action: [action_name]
parameters:
  key: value
```

## Execution History

| Date | Status | Duration | Notes |
|------|--------|----------|-------|
| *No executions yet* | | | |

## Missed Schedule Handling

If this task misses a scheduled execution (system was off), it will execute on next system start with `missed_schedule: true`.

---

*Template: Edit and save to Scheduled_Tasks/[task_name].md*
