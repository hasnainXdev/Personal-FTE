"""
Audit Logger

Comprehensive audit logging for all AI Employee actions.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logger for tracking all AI Employee actions"""
    
    def __init__(self, vault_path: str):
        """
        Initialize audit logger
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / 'Logs'
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.log_file = self.logs_path / f'audit_{self.today}.json'
        
        # Initialize today's log file if needed
        if not self.log_file.exists():
            self.log_file.write_text('[]')
    
    def log(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        approval_status: str = 'auto',
        approved_by: Optional[str] = None,
        result: str = 'success',
        error: Optional[str] = None,
    ) -> None:
        """
        Log an action
        
        Args:
            action_type: Type of action (email_send, payment, etc.)
            actor: Who performed the action (claude_code, watcher, etc.)
            target: Target of the action (email address, file path, etc.)
            parameters: Action parameters
            approval_status: Approval status (auto, approved, rejected)
            approved_by: Who approved (human username or None)
            result: Result (success, failure, skipped)
            error: Error message if failed
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'parameters': parameters or {},
            'approval_status': approval_status,
            'approved_by': approved_by,
            'result': result,
            'error': error,
        }
        
        try:
            # Read existing logs
            logs = json.loads(self.log_file.read_text() or '[]')
            
            # Add new entry
            logs.append(entry)
            
            # Write back
            self.log_file.write_text(json.dumps(logs, indent=2))
            
        except Exception as e:
            logger.error(f'Failed to write audit log: {e}')
    
    def get_logs(
        self,
        date: Optional[str] = None,
        action_type: Optional[str] = None,
        actor: Optional[str] = None,
    ) -> list:
        """
        Get logs with optional filtering
        
        Args:
            date: Date to filter (YYYY-MM-DD)
            action_type: Action type to filter
            actor: Actor to filter
            
        Returns:
            List of log entries
        """
        if date is None:
            date = self.today
        
        log_file = self.logs_path / f'audit_{date}.json'
        
        if not log_file.exists():
            return []
        
        try:
            logs = json.loads(log_file.read_text() or '[]')
            
            # Filter
            if action_type:
                logs = [l for l in logs if l.get('action_type') == action_type]
            if actor:
                logs = [l for l in logs if l.get('actor') == actor]
            
            return logs
            
        except Exception as e:
            logger.error(f'Failed to read audit log: {e}')
            return []
    
    def get_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary of logs for a date
        
        Args:
            date: Date to summarize
            
        Returns:
            Summary dictionary
        """
        logs = self.get_logs(date)
        
        summary = {
            'date': date or self.today,
            'total_actions': len(logs),
            'by_type': {},
            'by_result': {'success': 0, 'failure': 0, 'skipped': 0},
            'by_approval': {'auto': 0, 'approved': 0, 'rejected': 0},
        }
        
        for log in logs:
            # Count by type
            action_type = log.get('action_type', 'unknown')
            summary['by_type'][action_type] = summary['by_type'].get(action_type, 0) + 1
            
            # Count by result
            result = log.get('result', 'unknown')
            if result in summary['by_result']:
                summary['by_result'][result] += 1
            
            # Count by approval
            approval = log.get('approval_status', 'unknown')
            if approval in summary['by_approval']:
                summary['by_approval'][approval] += 1
        
        return summary
    
    def export_logs(
        self,
        start_date: str,
        end_date: str,
        output_path: str,
    ) -> Path:
        """
        Export logs for a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        all_logs = []
        
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            logs = self.get_logs(date_str)
            all_logs.extend(logs)
            current += timedelta(days=1)
        
        output = Path(output_path)
        output.write_text(json.dumps(all_logs, indent=2))
        
        logger.info(f'Exported {len(all_logs)} logs to {output}')
        
        return output
