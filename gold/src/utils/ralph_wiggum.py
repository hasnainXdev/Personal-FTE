"""
Ralph Wiggum Loop Implementation

The "Ralph Wiggum" pattern is a Stop hook that intercepts Claude's exit
and feeds the prompt back, allowing autonomous multi-step task completion.

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
"""

import subprocess
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)


class RalphWiggumLoop:
    """
    Ralph Wiggum loop for autonomous task completion
    
    This class implements the "Ralph Wiggum" pattern where:
    1. Claude works on a task
    2. When Claude tries to exit, the hook checks if task is complete
    3. If not complete, the hook blocks exit and re-injects the prompt
    4. Loop continues until task is complete or max iterations reached
    """
    
    def __init__(
        self,
        prompt: str,
        vault_path: str,
        completion_signal: str = 'TASK_COMPLETE',
        max_iterations: int = 10,
        claude_model: str = 'claude-sonnet-4-5-20250929',
    ):
        """
        Initialize Ralph Wiggum loop
        
        Args:
            prompt: Initial prompt/task for Claude
            vault_path: Path to Obsidian vault
            completion_signal: Signal that indicates task completion
            max_iterations: Maximum number of iterations
            claude_model: Claude model to use
        """
        self.prompt = prompt
        self.vault_path = Path(vault_path)
        self.completion_signal = completion_signal
        self.max_iterations = max_iterations
        self.claude_model = claude_model
        
        self.iteration = 0
        self.running = False
        self.state_file = self._create_state_file()
        
        logger.info(f'Ralph Wiggum Loop initialized')
        logger.info(f'Prompt: {prompt[:100]}...')
        logger.info(f'Max iterations: {max_iterations}')
    
    def _create_state_file(self) -> Path:
        """Create state file for tracking progress"""
        state_path = self.vault_path / 'In_Progress' / 'ralph_state.md'
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f'''---
created: {datetime.now().isoformat()}
status: in_progress
iteration: 0
max_iterations: {self.max_iterations}
---

# Ralph Wiggum Loop State

## Task
{self.prompt}

## Progress
- Iteration: 0/{self.max_iterations}
- Status: Starting

## Log
'''
        state_path.write_text(content)
        return state_path
    
    def _update_state(self, status: str, log_entry: str) -> None:
        """Update state file"""
        self.iteration += 1
        
        content = self.state_file.read_text()
        content = content.replace(
            '- Iteration: 0/',
            f'- Iteration: {self.iteration}/'
        )
        content = content.replace(
            '- Status: Starting',
            f'- Status: {status}'
        )
        content += f'\n- [{datetime.now().strftime("%H:%M:%S")}] {log_entry}'
        
        self.state_file.write_text(content)
    
    def is_task_complete(self) -> bool:
        """
        Check if task is complete
        
        Returns:
            True if task is complete
        """
        # Check if completion signal file exists
        completion_file = self.vault_path / 'Done' / f'{self.completion_signal}.md'
        if completion_file.exists():
            return True
        
        # Check if state file indicates completion
        if self.state_file.exists():
            content = self.state_file.read_text()
            if 'TASK_COMPLETE' in content or 'status: complete' in content:
                return True
        
        # Check if all items moved to Done
        needs_action = self.vault_path / 'Needs_Action'
        if needs_action.exists():
            items = list(needs_action.glob('*.md'))
            if len(items) == 0:
                return True
        
        return False
    
    def run(self) -> bool:
        """
        Run the Ralph Wiggum loop
        
        Returns:
            True if task completed successfully
        """
        self.running = True
        logger.info('Starting Ralph Wiggum Loop')
        
        while self.running and self.iteration < self.max_iterations:
            self._update_state('working', f'Iteration {self.iteration + 1} starting')
            
            # Check if task is complete
            if self.is_task_complete():
                self._update_state('complete', 'Task completed!')
                logger.info('Task completed successfully')
                return True
            
            # Run Claude with the prompt
            logger.info(f'Running Claude (iteration {self.iteration + 1})')
            
            try:
                result = self._run_claude()
                
                if result == 0:
                    # Claude exited successfully
                    # Check if we should continue
                    if not self.is_task_complete():
                        self._update_state('continuing', 'Task not complete, continuing...')
                        logger.info('Task not complete, continuing...')
                    else:
                        self._update_state('complete', 'Task completed!')
                        logger.info('Task completed successfully')
                        return True
                else:
                    # Claude exited with error
                    self._update_state('error', f'Claude exited with code {result}')
                    logger.warning(f'Claude exited with code {result}')
                    
            except Exception as e:
                self._update_state('error', str(e))
                logger.error(f'Error running Claude: {e}')
            
            # Small delay between iterations
            time.sleep(2)
        
        # Max iterations reached
        if self.iteration >= self.max_iterations:
            self._update_state('max_iterations', 'Max iterations reached')
            logger.warning('Max iterations reached, stopping')
            return False
        
        return self.is_task_complete()
    
    def _run_claude(self) -> int:
        """
        Run Claude Code with the prompt
        
        Returns:
            Exit code
        """
        # Build Claude command
        cmd = [
            'claude',
            '--model', self.claude_model,
            '--cwd', str(self.vault_path),
        ]
        
        # Build the prompt with context
        full_prompt = f'''{self.prompt}

IMPORTANT: 
- Work on this task until it is complete
- When finished, create a file named "TASK_COMPLETE.md" in the /Done folder
- Do not exit until the task is complete or you determine it cannot be completed

Current vault state:
- Needs_Action: {self._count_files(self.vault_path / 'Needs_Action')} files
- In_Progress: {self._count_files(self.vault_path / 'In_Progress')} files
- Done: {self._count_files(self.vault_path / 'Done')} files
- Pending_Approval: {self._count_files(self.vault_path / 'Pending_Approval')} files

Proceed with the task.
'''
        
        try:
            # Run Claude interactively
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.vault_path)
            )
            
            stdout, stderr = process.communicate(input=full_prompt, timeout=300)
            
            # Log output
            if stdout:
                logger.info(f'Claude output: {stdout[:500]}...')
            if stderr:
                logger.error(f'Claude error: {stderr[:500]}...')
            
            return process.returncode
            
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error('Claude timed out')
            return 1
        except Exception as e:
            logger.error(f'Error running Claude: {e}')
            return 1
    
    def _count_files(self, path: Path) -> int:
        """Count files in a directory"""
        if not path.exists():
            return 0
        return len(list(path.glob('*.md')))
    
    def stop(self) -> None:
        """Stop the loop"""
        self.running = False
        logger.info('Ralph Wiggum Loop stopped')


def ralph_loop(
    prompt: str,
    vault_path: str,
    completion_signal: str = 'TASK_COMPLETE',
    max_iterations: int = 10,
) -> bool:
    """
    Run a Ralph Wiggum loop
    
    Args:
        prompt: Task prompt
        vault_path: Path to vault
        completion_signal: Completion signal
        max_iterations: Maximum iterations
        
    Returns:
        True if task completed
    """
    loop = RalphWiggumLoop(
        prompt=prompt,
        vault_path=vault_path,
        completion_signal=completion_signal,
        max_iterations=max_iterations,
    )
    
    return loop.run()


def main() -> None:
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop')
    
    parser.add_argument('prompt', type=str, help='Task prompt')
    parser.add_argument(
        '--vault',
        type=str,
        default='./AI_Employee_Vault',
        help='Path to vault'
    )
    parser.add_argument(
        '--completion-signal',
        type=str,
        default='TASK_COMPLETE',
        help='Completion signal'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum iterations'
    )
    
    args = parser.parse_args()
    
    success = ralph_loop(
        prompt=args.prompt,
        vault_path=args.vault,
        completion_signal=args.completion_signal,
        max_iterations=args.max_iterations,
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
