"""Approval Service - Manages human-in-the-loop approval workflow."""

import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


class ApprovalService:
    """Service for managing approval workflows.
    
    This service:
    1. Creates approval request files
    2. Monitors Approved/Rejected folders
    3. Executes approved actions
    4. Logs all approval activities
    """
    
    def __init__(self, vault_path: str):
        """Initialize the approval service.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.pending = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for directory in [self.pending, self.approved, self.rejected, self.logs]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_approval_request(self, request_type: str, details: dict, action_required: str) -> Path:
        """Create an approval request file.
        
        Args:
            request_type: Type of action (email, payment, linkedin_post, etc.)
            details: Dictionary of action details
            action_required: Description of what action will be taken
            
        Returns:
            Path to the created approval file
        """
        file_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        request_path = self.pending / f'APPROVAL_{request_type.upper()}_{file_id}.md'
        
        # Build details section
        details_md = "\n".join([f"- **{k.replace('_', ' ').title()}**: {v}" for k, v in details.items()])
        
        content = f"""---
type: approval_request
file_id: {file_id}
request_type: {request_type}
created: {datetime.now().isoformat()}
status: pending
expires: {self._get_expiry_date()}
---

# Approval Request: {request_type.replace('_', ' ').title()}

## Details

{details_md}

## Action Required

{action_required}

## To Approve

1. Review the details above
2. Move this file to `/Approved/` folder
3. The action will be executed automatically

## To Reject

1. Add your reason below
2. Move this file to `/Rejected/` folder

## Rejection Reason (if applicable)



---

*Created by ApprovalService*
*Silver Tier - Human-in-the-Loop*
"""
        
        request_path.write_text(content)
        self.logger.info(f"Created approval request: {request_path.name}")
        
        return request_path
    
    def _get_expiry_date(self) -> str:
        """Get expiry date (24 hours from now)."""
        from datetime import timedelta
        expiry = datetime.now() + timedelta(hours=24)
        return expiry.isoformat()
    
    def check_approved(self) -> list:
        """Check for approved actions ready to execute.
        
        Returns:
            List of approved file paths
        """
        approved_files = list(self.approved.glob('*.md'))
        return approved_files
    
    def check_rejected(self) -> list:
        """Check for rejected actions.
        
        Returns:
            List of rejected file paths
        """
        rejected_files = list(self.rejected.glob('*.md'))
        return rejected_files
    
    def execute_approved_action(self, file_path: Path) -> dict:
        """Execute an approved action.
        
        Args:
            file_path: Path to the approved file
            
        Returns:
            dict with execution result
        """
        result = {
            'success': False,
            'action_type': None,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            content = file_path.read_text()
            
            # Parse frontmatter to get action type
            if 'type: approval_request' not in content:
                result['error'] = 'Not a valid approval request'
                return result
            
            # Extract request type
            if 'request_type: ' in content:
                for line in content.split('\n'):
                    if line.startswith('request_type:'):
                        result['action_type'] = line.split(':')[1].strip()
                        break
            
            # Log the execution
            self._log_execution(file_path, result)
            
            # Move to Done
            done_folder = self.vault_path / 'Done' / 'Approvals'
            done_folder.mkdir(parents=True, exist_ok=True)
            dest_path = done_folder / file_path.name
            shutil.move(str(file_path), str(dest_path))
            
            result['success'] = True
            self.logger.info(f"Executed approved action: {file_path.name}")
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Failed to execute approved action: {e}")
        
        return result
    
    def _log_execution(self, file_path: Path, result: dict):
        """Log the execution of an approved action."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'approvals_{today}.md'
        
        entry = f"""
## Execution - {result['timestamp']}

**File**: {file_path.name}
**Type**: {result.get('action_type', 'Unknown')}
**Status**: {'Success' if result['success'] else 'Failed'}
**Error**: {result.get('error', 'None')}

---
"""
        
        if log_file.exists():
            content = log_file.read_text()
            log_file.write_text(content + entry)
        else:
            log_file.write_text(f"""---
type: approval_log
date: {today}
---

# Approval Executions - {today}
{entry}
""")
    
    def reject_request(self, file_path: Path, reason: str) -> Path:
        """Move a request to rejected with a reason.
        
        Args:
            file_path: Path to the pending request
            reason: Reason for rejection
            
        Returns:
            Path to the rejected file
        """
        try:
            # Add reason to file
            content = file_path.read_text()
            content = content.replace(
                '## Rejection Reason (if applicable)\n\n\n',
                f'## Rejection Reason\n\n{reason}\n\n'
            )
            content = content.replace(
                'status: pending',
                'status: rejected'
            )
            file_path.write_text(content)
            
            # Move to rejected
            dest_path = self.rejected / file_path.name
            shutil.move(str(file_path), str(dest_path))
            
            self.logger.info(f"Rejected request: {file_path.name}")
            return dest_path
            
        except Exception as e:
            self.logger.error(f"Failed to reject request: {e}")
            raise
    
    def get_pending_count(self) -> int:
        """Get count of pending approval requests."""
        return len(list(self.pending.glob('*.md')))
    
    def get_approved_count(self) -> int:
        """Get count of approved actions waiting execution."""
        return len(list(self.approved.glob('*.md')))
