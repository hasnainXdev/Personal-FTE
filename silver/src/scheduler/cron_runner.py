"""Cron Runner - Executes scheduled tasks based on cron expressions."""

import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, List, Optional, Any
from croniter import croniter


class CronRunner:
    """Runner for cron-based scheduled tasks.
    
    This scheduler:
    1. Manages scheduled tasks with cron expressions
    2. Executes tasks at specified intervals
    3. Logs all executions
    4. Supports task persistence
    """
    
    def __init__(self, vault_path: str):
        """Initialize the cron runner.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.scheduled_tasks = self.vault_path / 'Scheduled_Tasks'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        self.scheduled_tasks.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Registered tasks
        self.tasks: Dict[str, dict] = {}
        
        # Load persisted tasks
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks from scheduled tasks folder."""
        for task_file in self.scheduled_tasks.glob('*.md'):
            if task_file.name.startswith('Task_'):
                content = task_file.read_text()
                task_data = self._parse_task_file(content, task_file)
                if task_data:
                    self.tasks[task_data['name']] = task_data
        
        self.logger.info(f"Loaded {len(self.tasks)} scheduled tasks")
    
    def _parse_task_file(self, content: str, file_path: Path) -> Optional[dict]:
        """Parse a task file and extract task data."""
        try:
            lines = content.split('\n')
            task_data = {
                'name': file_path.stem,
                'file': file_path,
                'cron': None,
                'enabled': True,
                'last_run': None,
                'next_run': None,
                'action': None
            }
            
            for line in lines:
                if line.startswith('cron:'):
                    task_data['cron'] = line.split(':')[1].strip()
                elif line.startswith('enabled:'):
                    task_data['enabled'] = line.split(':')[1].strip().lower() == 'true'
                elif line.startswith('last_run:'):
                    task_data['last_run'] = line.split(':')[1].strip()
                elif line.startswith('action:'):
                    task_data['action'] = line.split(':')[1].strip()
            
            # Calculate next run
            if task_data['cron']:
                cron = croniter(task_data['cron'], datetime.now())
                task_data['next_run'] = cron.get_next(datetime).isoformat()
            
            return task_data
            
        except Exception as e:
            self.logger.error(f"Failed to parse task file {file_path}: {e}")
            return None
    
    def register_task(self, name: str, cron_expression: str, 
                      callback: Callable, description: str = "") -> Path:
        """Register a new scheduled task.
        
        Args:
            name: Task name
            cron_expression: Cron expression for scheduling
            callback: Function to call when task runs
            description: Task description
            
        Returns:
            Path to the task file
        """
        # Validate cron expression
        try:
            croniter(cron_expression)
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {e}")
        
        # Create task file
        task_file = self.scheduled_tasks / f'Task_{name.replace(" ", "_")}.md'
        
        content = f"""---
type: scheduled_task
name: {name}
cron: {cron_expression}
enabled: true
created: {datetime.now().isoformat()}
last_run: never
next_run: {croniter(cron_expression, datetime.now()).get_next(datetime).isoformat()}
---

# Scheduled Task: {name}

## Description

{description}

## Schedule

**Cron Expression**: `{cron_expression}`

## Action



## Execution History



---

*Created by CronRunner*
*Silver Tier*
"""
        
        task_file.write_text(content)
        
        # Register in memory
        self.tasks[name] = {
            'name': name,
            'file': task_file,
            'cron': cron_expression,
            'enabled': True,
            'callback': callback,
            'description': description,
            'last_run': None,
            'next_run': croniter(cron_expression, datetime.now()).get_next(datetime).isoformat()
        }
        
        self.logger.info(f"Registered task: {name} ({cron_expression})")
        
        return task_file
    
    async def run_due_tasks(self) -> List[dict]:
        """Run all tasks that are due.
        
        Returns:
            List of execution results
        """
        results = []
        now = datetime.now()
        
        for name, task in self.tasks.items():
            if not task['enabled']:
                continue
            
            # Check if task is due
            if task['next_run']:
                next_run = datetime.fromisoformat(task['next_run'])
                if now >= next_run:
                    result = await self._execute_task(task)
                    results.append(result)
        
        return results
    
    async def _execute_task(self, task: dict) -> dict:
        """Execute a single task.
        
        Args:
            task: Task dictionary
            
        Returns:
            Execution result
        """
        result = {
            'task': task['name'],
            'success': False,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            self.logger.info(f"Executing task: {task['name']}")
            
            # Execute callback
            if asyncio.iscoroutinefunction(task['callback']):
                await task['callback']()
            else:
                task['callback']()
            
            result['success'] = True
            
            # Update task file
            self._update_task_execution(task, result)
            
            # Calculate next run
            cron = croniter(task['cron'], datetime.now())
            task['next_run'] = cron.get_next(datetime).isoformat()
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Task execution failed: {task['name']} - {e}")
        
        return result
    
    def _update_task_execution(self, task: dict, result: dict):
        """Update task file with execution result."""
        try:
            content = task['file'].read_text()
            
            # Update last_run in frontmatter
            content = content.replace(
                f"last_run: {task.get('last_run', 'never')}",
                f"last_run: {result['timestamp']}"
            )
            
            # Add to execution history
            history_entry = f"- **{result['timestamp']}**: {'Success' if result['success'] else 'Failed'}\n"
            
            if '## Execution History' in content:
                content = content.replace(
                    '## Execution History\n',
                    f"## Execution History\n\n{history_entry}"
                )
            
            task['file'].write_text(content)
            task['last_run'] = result['timestamp']
            
        except Exception as e:
            self.logger.error(f"Failed to update task file: {e}")
    
    def get_task_status(self) -> List[dict]:
        """Get status of all tasks.
        
        Returns:
            List of task status dictionaries
        """
        status = []
        for name, task in self.tasks.items():
            status.append({
                'name': name,
                'cron': task['cron'],
                'enabled': task['enabled'],
                'last_run': task.get('last_run'),
                'next_run': task.get('next_run')
            })
        return status
    
    def enable_task(self, name: str):
        """Enable a task."""
        if name in self.tasks:
            self.tasks[name]['enabled'] = True
            self._update_task_enabled(name, True)
    
    def disable_task(self, name: str):
        """Disable a task."""
        if name in self.tasks:
            self.tasks[name]['enabled'] = False
            self._update_task_enabled(name, False)
    
    def _update_task_enabled(self, name: str, enabled: bool):
        """Update task enabled status in file."""
        task = self.tasks.get(name)
        if task:
            content = task['file'].read_text()
            content = content.replace(
                f"enabled: {'true' if not enabled else 'true'}",
                f"enabled: {'true' if enabled else 'false'}"
            )
            task['file'].write_text(content)
    
    async def run_continuously(self, check_interval: int = 60):
        """Run the scheduler continuously.
        
        Args:
            check_interval: Seconds between checks
        """
        self.logger.info(f"Starting continuous scheduler (check every {check_interval}s)")
        
        while True:
            try:
                await self.run_due_tasks()
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
            
            await asyncio.sleep(check_interval)
