"""
Cron Runner - Execute scheduled tasks

Handles cron-based scheduling with restart safety
and missed execution detection.
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    name: str
    cron_expression: str
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None
    task_config: dict = field(default_factory=dict)
    missed_schedule: bool = False
    execution_count: int = 0
    
    def to_markdown(self) -> str:
        """Convert to markdown format for storage"""
        return f"""---
Name: {self.name}
Cron: {self.cron_expression}
Enabled: {self.enabled}
Last_Run: {self.last_run.isoformat() if self.last_run else 'null'}
Next_Run: {self.next_run.isoformat() if self.next_run else 'null'}
Missed_Schedule: {self.missed_schedule}
Execution_Count: {self.execution_count}
---

## Task Configuration

```yaml
{self.task_config}
```

## Execution History

| Date | Status | Duration | Notes |
|------|--------|----------|-------|
| *No executions yet* | | | |
"""
    
    @classmethod
    def from_markdown(cls, content: str) -> "ScheduledTask":
        """Parse from markdown format"""
        import re
        
        # Extract frontmatter
        match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            raise ValueError("Invalid task markdown format")
        
        frontmatter = match.group(1)
        fields = {}
        
        for line in frontmatter.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                elif value == "null":
                    value = None
                elif key in ["Execution_Count"]:
                    value = int(value)
                
                fields[key] = value
        
        return cls(
            name=fields.get("Name", "Unknown"),
            cron_expression=fields.get("Cron", "* * * * *"),
            enabled=fields.get("Enabled", True),
            last_run=datetime.fromisoformat(fields["Last_Run"].replace("Z", "+00:00")) if fields.get("Last_Run") and fields["Last_Run"] != "null" else None,
            next_run=datetime.fromisoformat(fields["Next_Run"].replace("Z", "+00:00")) if fields.get("Next_Run") and fields["Next_Run"] != "null" else None,
            task_config=fields.get("task_config", {}),
            missed_schedule=fields.get("Missed_Schedule", False),
            execution_count=fields.get("Execution_Count", 0)
        )


class CronRunner:
    """
    Execute scheduled tasks based on cron expressions.
    
    Supports:
    - Standard 5-field cron format (minute hour day month weekday)
    - Missed execution detection
    - Restart safety
    """
    
    def __init__(self, scheduled_tasks_dir: Path | None = None, dashboard_path: Path | None = None):
        """
        Initialize cron runner.
        
        Args:
            scheduled_tasks_dir: Directory for task configs (default: Scheduled_Tasks)
            dashboard_path: Path to Dashboard.md for logging (default: Dashboard.md)
        """
        project_root = Path(__file__).parent.parent.parent
        self.scheduled_tasks_dir = scheduled_tasks_dir or (project_root / "AI_Employee_Vault" / "Scheduled_Tasks")
        self.dashboard_path = dashboard_path or (project_root / "AI_Employee_Vault" / "Dashboard.md")
        
        self.scheduled_tasks_dir.mkdir(parents=True, exist_ok=True)
        
        self.tasks: dict[str, ScheduledTask] = {}
        self._load_tasks()
        
        logger.info(f"CronRunner initialized with {len(self.tasks)} tasks")
    
    def _load_tasks(self):
        """Load scheduled tasks from disk"""
        if not self.scheduled_tasks_dir.exists():
            return
        
        for task_file in self.scheduled_tasks_dir.glob("*.md"):
            try:
                content = task_file.read_text(encoding="utf-8")
                task = ScheduledTask.from_markdown(content)
                self.tasks[task.name] = task
                logger.info(f"Loaded scheduled task: {task.name}")
            except Exception as e:
                logger.error(f"Failed to load task {task_file.name}: {e}")
    
    def _save_task(self, task: ScheduledTask):
        """Save task to disk"""
        task_file = self.scheduled_tasks_dir / f"{task.name.replace(' ', '_')}.md"
        task_file.write_text(task.to_markdown(), encoding="utf-8")
    
    def _log_to_dashboard(self, task_name: str, status: str, next_run: datetime, notes: str = ""):
        """Log scheduled task execution to Dashboard.md"""
        timestamp = datetime.now(timezone.utc).isoformat()
        next_run_str = next_run.isoformat() if next_run else "N/A"
        
        log_entry = f"| {timestamp} | {task_name} | {next_run_str} | {status} | {notes} |\n"
        
        try:
            if self.dashboard_path.exists():
                content = self.dashboard_path.read_text(encoding="utf-8")
                
                # Find Scheduled Tasks table and insert entry
                if "### Scheduled Tasks" in content:
                    lines = content.split("\n")
                    new_lines = []
                    inserted = False
                    
                    for line in lines:
                        new_lines.append(line)
                        if line.startswith("| Timestamp |") and not inserted:
                            new_lines.append(log_entry.rstrip())
                            inserted = True
                    
                    content = "\n".join(new_lines)
                else:
                    # Append to end
                    content += f"\n### Scheduled Tasks\n\n| Timestamp | Task | Next Run | Status | Notes |\n|-----------|------|----------|--------|-------|\n{log_entry}"
                
                self.dashboard_path.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to log to dashboard: {e}")
    
    def _parse_cron(self, cron_expr: str) -> list[datetime]:
        """
        Parse cron expression and return next run times.
        
        Simplified cron parser for common patterns.
        Format: minute hour day month weekday
        """
        # For now, return a simple implementation
        # A full cron parser would be more complex
        from croniter import croniter
        
        base = datetime.now(timezone.utc)
        cron = croniter(cron_expr, base)
        return [cron.get_next(datetime)]
    
    def check_missed_executions(self):
        """Check for and handle missed executions"""
        now = datetime.now(timezone.utc)
        
        for task in self.tasks.values():
            if not task.enabled:
                continue
            
            if task.next_run and task.next_run < now:
                time_diff = (now - task.next_run).total_seconds()
                
                # If more than 1 hour overdue, mark as missed
                if time_diff > 3600:
                    logger.warning(f"Task '{task.name}' missed execution ({time_diff:.0f}s ago)")
                    task.missed_schedule = True
                    self._save_task(task)
    
    def run_task(self, task_name: str):
        """
        Execute a scheduled task.
        
        Args:
            task_name: Name of task to execute
        """
        if task_name not in self.tasks:
            logger.error(f"Task '{task_name}' not found")
            return
        
        task = self.tasks[task_name]
        
        if not task.enabled:
            logger.info(f"Task '{task_name}' is disabled, skipping")
            return
        
        logger.info(f"Executing scheduled task: {task.name}")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Execute based on task config
            action = task.task_config.get("action", "")
            parameters = task.task_config.get("parameters", {})
            
            if action == "generate_daily_summary":
                from .daily_summary import generate_daily_summary
                generate_daily_summary(**parameters)
            else:
                logger.warning(f"Unknown action: {action}")
            
            # Update task state
            task.last_run = datetime.now(timezone.utc)
            task.execution_count += 1
            task.missed_schedule = False
            
            # Calculate next run (simplified)
            from croniter import croniter
            cron = croniter(task.cron_expression, task.last_run)
            task.next_run = cron.get_next(datetime)
            
            self._save_task(task)
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._log_to_dashboard(
                task.name,
                f"Completed ({duration:.1f}s)",
                task.next_run,
                "Normal execution" if not task.missed_schedule else "Missed schedule recovered"
            )
            
            logger.info(f"Task '{task.name}' completed in {duration:.1f}s")
        
        except ImportError as e:
            logger.error(f"Task '{task.name}' failed - module not found: {e}")
            self._log_to_dashboard(task.name, "Failed (import error)", task.next_run, str(e))
        
        except Exception as e:
            logger.error(f"Task '{task.name}' failed: {e}", exc_info=True)
            self._log_to_dashboard(task.name, "Failed", task.next_run, str(e))
    
    def run_all_due_tasks(self):
        """Run all tasks that are due"""
        now = datetime.now(timezone.utc)
        
        for task in self.tasks.values():
            if not task.enabled:
                continue
            
            if task.next_run and task.next_run <= now:
                self.run_task(task.name)
    
    def create_task(
        self,
        name: str,
        cron_expression: str,
        action: str,
        parameters: dict | None = None,
        enabled: bool = True,
    ) -> ScheduledTask:
        """
        Create a new scheduled task.
        
        Args:
            name: Task name
            cron_expression: Cron schedule
            action: Action to execute
            parameters: Action parameters
            enabled: Whether task is active
        
        Returns:
            Created task
        """
        # Calculate initial next_run
        from croniter import croniter
        base = datetime.now(timezone.utc)
        cron = croniter(cron_expression, base)
        next_run = cron.get_next(datetime)
        
        task = ScheduledTask(
            name=name,
            cron_expression=cron_expression,
            enabled=enabled,
            next_run=next_run,
            task_config={
                "action": action,
                "parameters": parameters or {}
            }
        )
        
        self.tasks[name] = task
        self._save_task(task)
        
        logger.info(f"Created scheduled task: {name} (next run: {next_run})")
        return task


def run_scheduler():
    """Entry point for running scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cron Runner")
    parser.add_argument("--check", action="store_true", help="Check for missed executions")
    parser.add_argument("--run-due", action="store_true", help="Run all due tasks")
    parser.add_argument("--task", type=str, help="Run specific task by name")
    args = parser.parse_args()
    
    runner = CronRunner()
    
    if args.check:
        runner.check_missed_executions()
    elif args.run_due:
        runner.run_all_due_tasks()
    elif args.task:
        runner.run_task(args.task)
    else:
        print("Use --check, --run-due, or --task <name>")


if __name__ == "__main__":
    run_scheduler()
