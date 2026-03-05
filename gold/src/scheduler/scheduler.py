"""
Task Scheduler

Handles cron-based scheduled tasks using croniter.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional
from croniter import croniter

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Represents a scheduled task"""
    
    def __init__(
        self,
        name: str,
        cron_expression: str,
        callback: Callable,
        enabled: bool = True,
    ):
        """
        Initialize scheduled task
        
        Args:
            name: Task name
            cron_expression: Cron expression (e.g., '0 8 * * *')
            callback: Function to call
            enabled: Whether task is enabled
        """
        self.name = name
        self.cron_expression = cron_expression
        self.callback = callback
        self.enabled = enabled
        self.cron = croniter(cron_expression, datetime.now())
        self.next_run = self.cron.get_next(datetime)
        self.last_run = None
        self.run_count = 0
        
    def should_run(self) -> bool:
        """Check if task should run now"""
        if not self.enabled:
            return False
        return datetime.now() >= self.next_run
    
    def mark_completed(self) -> None:
        """Mark task as completed and schedule next run"""
        self.last_run = datetime.now()
        self.run_count += 1
        self.next_run = self.cron.get_next(datetime)
        logger.info(f'Task {self.name} completed. Next run: {self.next_run}')
    
    def __repr__(self) -> str:
        return f'ScheduledTask({self.name}, next={self.next_run})'


class TaskScheduler:
    """Task scheduler with cron support"""
    
    def __init__(self, vault_path: str):
        """
        Initialize scheduler
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure schedules folder exists
        schedules_path = self.vault_path / 'Scheduled_Tasks'
        schedules_path.mkdir(parents=True, exist_ok=True)
    
    def add_task(
        self,
        name: str,
        cron_expression: str,
        callback: Callable,
        enabled: bool = True,
    ) -> None:
        """
        Add a scheduled task
        
        Args:
            name: Task name
            cron_expression: Cron expression
            callback: Function to call
            enabled: Whether task is enabled
        """
        task = ScheduledTask(name, cron_expression, callback, enabled)
        self.tasks[name] = task
        self.logger.info(f'Added task: {name} ({cron_expression})')
    
    def remove_task(self, name: str) -> None:
        """Remove a task"""
        if name in self.tasks:
            del self.tasks[name]
            self.logger.info(f'Removed task: {name}')
    
    def enable_task(self, name: str) -> None:
        """Enable a task"""
        if name in self.tasks:
            self.tasks[name].enabled = True
            self.logger.info(f'Enabled task: {name}')
    
    def disable_task(self, name: str) -> None:
        """Disable a task"""
        if name in self.tasks:
            self.tasks[name].enabled = False
            self.logger.info(f'Disabled task: {name}')
    
    def get_next_runs(self) -> List[Dict[str, datetime]]:
        """Get next run times for all tasks"""
        return [
            {'name': task.name, 'next_run': task.next_run}
            for task in self.tasks.values()
            if task.enabled
        ]
    
    def run(self, check_interval: int = 60) -> None:
        """
        Run the scheduler loop
        
        Args:
            check_interval: Seconds between checks
        """
        self.running = True
        self.logger.info('Starting scheduler')
        
        while self.running:
            try:
                for task in self.tasks.values():
                    if task.should_run():
                        self.logger.info(f'Running task: {task.name}')
                        try:
                            task.callback()
                            task.mark_completed()
                        except Exception as e:
                            self.logger.error(f'Task {task.name} failed: {e}', exc_info=True)
                
            except Exception as e:
                self.logger.error(f'Scheduler error: {e}', exc_info=True)
            
            time.sleep(check_interval)
    
    def stop(self) -> None:
        """Stop the scheduler"""
        self.running = False
        self.logger.info('Scheduler stopped')
    
    def save_schedule(self, filepath: Optional[str] = None) -> Path:
        """
        Save current schedule to file
        
        Args:
            filepath: Optional file path
            
        Returns:
            Path to saved file
        """
        if filepath is None:
            filepath = self.vault_path / 'Scheduled_Tasks' / 'schedule.md'
        
        path = Path(filepath)
        
        content = '''---
generated: {generated}
---

# Scheduled Tasks

| Task | Cron Expression | Next Run | Enabled |
|------|-----------------|----------|---------|
'''.format(generated=datetime.now().isoformat())
        
        for task in self.tasks.values():
            status = '✅' if task.enabled else '❌'
            content += f'| {task.name} | `{task.cron_expression}` | {task.next_run} | {status} |\n'
        
        path.write_text(content)
        return path
