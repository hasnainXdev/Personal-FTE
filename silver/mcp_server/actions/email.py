"""Email actions for MCP Server."""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class EmailAction:
    """Handle email sending actions."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)
    
    def send_email(self, to: str, subject: str, body: str,
                   approval_file: Optional[str] = None) -> Dict[str, Any]:
        """Send an email (mock implementation for Silver Tier).
        
        In production, this would integrate with Gmail API.
        For Silver Tier, we log the intended action.
        """
        result = {
            'success': False,
            'message': '',
            'email_id': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Log the email that would be sent
            self._log_email(to, subject, body, approval_file)
            
            # For Silver Tier, we just create a log entry
            # In production, integrate with Gmail API
            result['success'] = True
            result['message'] = f"Email logged for sending to {to}"
            result['email_id'] = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            logger.info(f"Email action: To={to}, Subject={subject}")
            
        except Exception as e:
            result['message'] = str(e)
            logger.error(f"Failed to send email: {e}")
        
        return result
    
    def _log_email(self, to: str, subject: str, body: str, 
                   approval_file: Optional[str]):
        """Log the email action."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'email_{today}.md'
        
        entry = f"""
## Email - {datetime.now().isoformat()}

**To**: {to}
**Subject**: {subject}
**Approval File**: {approval_file or 'None'}

**Body**:
{body[:300]}{'...' if len(body) > 300 else ''}

---
"""
        
        if log_file.exists():
            content = log_file.read_text()
            log_file.write_text(content + entry)
        else:
            log_file.write_text(f"""---
type: email_log
date: {today}
---

# Email Log - {today}
{entry}
""")
    
    def draft_email(self, to: str, subject: str, body: str) -> Path:
        """Create an email draft for approval."""
        file_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_path = self.vault_path / 'Pending_Approval' / f'EMAIL_DRAFT_{file_id}.md'
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""---
type: email_draft
file_id: {file_id}
created: {datetime.now().isoformat()}
status: pending_approval
to: {to}
subject: {subject}
---

# Email Draft

## To
{to}

## Subject
{subject}

## Body

{body}

## To Approve

1. Review the email content
2. Move this file to `/Approved/` folder
3. The MCP server will send the email

## To Reject

1. Add rejection reason below
2. Move this file to `/Rejected/` folder

---

*Created by EmailAction*
*Silver Tier*
"""
        
        draft_path.write_text(content)
        logger.info(f"Created email draft: {draft_path.name}")
        
        return draft_path
