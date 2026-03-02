"""Plan Service - Creates and manages multi-step task plans."""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List


class PlanService:
    """Service for creating and managing multi-step task plans.
    
    This service:
    1. Creates Plan.md files for complex tasks
    2. Tracks plan progress
    3. Updates plan status as steps complete
    4. Archives completed plans
    """
    
    def __init__(self, vault_path: str):
        """Initialize the plan service.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done' / 'Plans'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for directory in [self.plans, self.done, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.plan_counter = self._load_plan_counter()
    
    def _load_plan_counter(self) -> int:
        """Load the plan counter from state."""
        counter_file = self.logs / 'plan_counter.txt'
        if counter_file.exists():
            return int(counter_file.read_text().strip())
        return 0
    
    def _save_plan_counter(self):
        """Save the plan counter."""
        counter_file = self.logs / 'plan_counter.txt'
        counter_file.write_text(str(self.plan_counter))
    
    def create_plan(self, title: str, objective: str, steps: List[str], 
                    source_file: Optional[str] = None) -> Path:
        """Create a new plan for a multi-step task.
        
        Args:
            title: Plan title
            objective: What the plan aims to achieve
            steps: List of steps to complete
            source_file: Optional source file that triggered this plan
            
        Returns:
            Path to the created plan file
        """
        self.plan_counter += 1
        self._save_plan_counter()
        
        date_str = datetime.now().strftime('%Y%m%d')
        file_id = f'Plan_{date_str}_{self.plan_counter:03d}'
        plan_path = self.plans / f'{file_id}.md'
        
        # Create steps checklist
        steps_md = "\n".join([f"- [ ] {step}" for step in steps])
        
        content = f"""---
type: plan
file_id: {file_id}
title: {title}
created: {datetime.now().isoformat()}
status: pending
total_steps: {len(steps)}
completed_steps: 0
source_file: {source_file or 'N/A'}
---

# Plan: {title}

## Objective

{objective}

## Steps

{steps_md}

## Progress

- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Steps**: {len(steps)}
- **Completed**: 0
- **Status**: Pending

## Notes



## Completion

When all steps are complete:
1. Update status to 'completed'
2. Add completion timestamp
3. Move to /Done/Plans/

---

*Created by PlanService*
*Silver Tier*
"""
        
        plan_path.write_text(content)
        self.logger.info(f"Created plan: {plan_path.name}")
        
        return plan_path
    
    def update_step(self, plan_path: Path, step_number: int, completed: bool = True) -> dict:
        """Update a step's completion status.
        
        Args:
            plan_path: Path to the plan file
            step_number: Step number to update (1-indexed)
            completed: Whether the step is completed
            
        Returns:
            dict with update result
        """
        result = {
            'success': False,
            'error': None,
            'completed_steps': 0,
            'total_steps': 0
        }
        
        try:
            content = plan_path.read_text()
            lines = content.split('\n')
            
            # Find and update the step
            step_count = 0
            completed_count = 0
            new_lines = []
            
            for line in lines:
                if line.strip().startswith('- [ ]') or line.strip().startswith('- [x]'):
                    step_count += 1
                    if step_count == step_number:
                        if completed:
                            new_lines.append(line.replace('- [ ]', '- [x]'))
                            completed_count += 1
                        else:
                            new_lines.append(line.replace('- [x]', '- [ ]'))
                    else:
                        if '- [x]' in line:
                            completed_count += 1
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # Update progress section
            new_content = '\n'.join(new_lines)
            new_content = self._update_progress(new_content, completed_count, step_count)
            
            # Check if all steps complete
            if completed_count == step_count and step_count > 0:
                new_content = new_content.replace('status: pending', 'status: completed')
                new_content = new_content.replace(
                    '## Completion',
                    f'**Completed**: {datetime.now().isoformat()}\n\n## Completion'
                )
            
            plan_path.write_text(new_content)
            
            result['success'] = True
            result['completed_steps'] = completed_count
            result['total_steps'] = step_count
            
            self.logger.info(f"Updated plan step {step_number}: {plan_path.name}")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Failed to update plan step: {e}")
        
        return result
    
    def _update_progress(self, content: str, completed: int, total: int) -> str:
        """Update the progress section in the plan."""
        lines = content.split('\n')
        new_lines = []
        in_progress = False
        
        for line in lines:
            if line.startswith('## Progress'):
                in_progress = True
                new_lines.append(line)
                new_lines.append('')
                # Skip old progress lines until we hit next section
                continue
            elif in_progress and line.startswith('##'):
                in_progress = False
                # Add new progress
                new_lines.append(f"- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                new_lines.append(f"- **Total Steps**: {total}")
                new_lines.append(f"- **Completed**: {completed}")
                status = 'completed' if completed == total else 'in_progress'
                new_lines.append(f"- **Status**: {status}")
                new_lines.append('')
                new_lines.append(line)
            elif not in_progress:
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def get_active_plans(self) -> List[Path]:
        """Get all active (non-completed) plans.
        
        Returns:
            List of active plan file paths
        """
        active = []
        for plan_file in self.plans.glob('*.md'):
            content = plan_file.read_text()
            if 'status: completed' not in content:
                active.append(plan_file)
        return active
    
    def archive_completed_plan(self, plan_path: Path) -> Path:
        """Move a completed plan to the Done folder.
        
        Args:
            plan_path: Path to the completed plan
            
        Returns:
            Path to the archived plan
        """
        dest_path = self.done / plan_path.name
        plan_path.rename(dest_path)
        self.logger.info(f"Archived completed plan: {plan_path.name}")
        return dest_path
    
    def get_plan_status(self, plan_path: Path) -> dict:
        """Get the status of a plan.
        
        Args:
            plan_path: Path to the plan file
            
        Returns:
            dict with plan status
        """
        content = plan_path.read_text()
        
        status = {
            'file': plan_path.name,
            'status': 'unknown',
            'completed_steps': 0,
            'total_steps': 0
        }
        
        # Parse status
        for line in content.split('\n'):
            if line.startswith('status:'):
                status['status'] = line.split(':')[1].strip()
            elif line.startswith('completed_steps:'):
                status['completed_steps'] = int(line.split(':')[1].strip())
            elif line.startswith('total_steps:'):
                status['total_steps'] = int(line.split(':')[1].strip())
        
        return status
