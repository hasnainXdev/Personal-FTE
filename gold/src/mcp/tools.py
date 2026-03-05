"""
Gold Tier AI Employee - MCP Tools

MCP tools for external actions.
Includes: Silver features (Email, LinkedIn) + Gold features (Odoo, Facebook)
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def send_email(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None,
    cc: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send an email via Gmail API
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        attachments: List of file paths to attach
        cc: CC recipient
        
    Returns:
        Result dictionary
    """
    logger.info(f'Sending email to {to}: {subject}')
    
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        import base64
        
        # Load credentials
        token_path = Path('./credentials/gmail_token.json')
        if not token_path.exists():
            return {
                'status': 'error',
                'error': 'Gmail credentials not found. Please authenticate first.',
            }
        
        creds = Credentials.from_authorized_user_file(
            token_path,
            ['https://www.googleapis.com/auth/gmail.send']
        )
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = 'AI Employee'
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        
        message.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{Path(filepath).name}"'
                        )
                        message.attach(part)
                except Exception as e:
                    logger.error(f'Error attaching {filepath}: {e}')
        
        # Encode and send
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        logger.info(f'Email sent: {result["id"]}')
        
        return {
            'status': 'success',
            'message_id': result['id'],
        }
        
    except Exception as e:
        logger.error(f'Error sending email: {e}')
        return {
            'status': 'error',
            'error': str(e),
        }


def post_linkedin(
    content: str,
    reason: str = 'Business update',
) -> Dict[str, Any]:
    """
    Post to LinkedIn using Playwright
    
    Args:
        content: Post content
        reason: Reason for post
        
    Returns:
        Result dictionary
    """
    logger.info('Posting to LinkedIn')
    
    try:
        # For now, create draft for approval (Silver tier pattern)
        draft_path = Path('./AI_Employee_Vault/Pending_Approval')
        draft_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_file = draft_path / f'LINKEDIN_{timestamp}.md'
        
        content_md = f'''---
type: linkedin_post_draft
created: {datetime.now().isoformat()}
status: pending_approval
---

# LinkedIn Post Draft

## Content
{content}

## Reason
{reason}

## To Approve
Move this file to /Approved folder

## To Reject
Move this file to /Rejected folder with reason

---
*Created by MCP LinkedIn Tool*
'''
        draft_file.write_text(content_md)
        
        return {
            'status': 'draft_created',
            'draft_path': str(draft_file),
            'message': 'LinkedIn post created as draft. Move to /Approved to post.',
        }
        
    except Exception as e:
        logger.error(f'Error creating LinkedIn post: {e}')
        return {
            'status': 'error',
            'error': str(e),
        }


def post_facebook(
    content: str,
    image_url: Optional[str] = None,
    link_url: Optional[str] = None,
    reason: str = 'Business update',
) -> Dict[str, Any]:
    """
    Post to Facebook
    
    Args:
        content: Post content
        image_url: Optional image URL
        link_url: Optional link to share
        reason: Reason for post
        
    Returns:
        Result dictionary
    """
    logger.info('Posting to Facebook')
    
    try:
        # Create draft for approval (Gold tier feature)
        draft_path = Path('./AI_Employee_Vault/Pending_Approval')
        draft_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_file = draft_path / f'FACEBOOK_{timestamp}.md'
        
        content_md = f'''---
type: facebook_post_draft
created: {datetime.now().isoformat()}
status: pending_approval
---

# Facebook Post Draft

## Content
{content}

{f"**Image**: {image_url}" if image_url else ""}
{f"**Link**: {link_url}" if link_url else ""}

## Reason
{reason}

## To Approve
Move this file to /Approved folder

## To Reject
Move this file to /Rejected folder with reason

---
*Created by MCP Facebook Tool (Gold Tier)*
'''
        draft_file.write_text(content_md)
        
        return {
            'status': 'draft_created',
            'draft_path': str(draft_file),
            'message': 'Facebook post created as draft. Move to /Approved to post.',
        }
        
    except Exception as e:
        logger.error(f'Error creating Facebook post: {e}')
        return {
            'status': 'error',
            'error': str(e),
        }


def create_approval_request(
    action_type: str,
    details: Dict[str, Any],
    reason: str,
) -> Dict[str, Any]:
    """
    Create an approval request file
    
    Args:
        action_type: Type of action
        details: Action details
        reason: Reason for request
        
    Returns:
        Result dictionary
    """
    logger.info(f'Creating approval request: {action_type}')
    
    try:
        approval_path = Path('./AI_Employee_Vault/Pending_Approval')
        approval_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = approval_path / f'APPROVAL_{action_type.upper()}_{timestamp}.md'
        
        details_json = json.dumps(details, indent=2, default=str)
        
        content = f'''---
type: approval_request
action_type: {action_type}
created: {datetime.now().isoformat()}
status: pending
---

# Approval Request: {action_type}

## Reason
{reason}

## Details
```json
{details_json}
```

## Instructions
- Move to /Approved to approve
- Move to /Rejected to reject

---
*Created by MCP Approval Tool*
'''
        approval_file.write_text(content)
        
        return {
            'status': 'created',
            'approval_path': str(approval_file),
        }
        
    except Exception as e:
        logger.error(f'Error creating approval request: {e}')
        return {
            'status': 'error',
            'error': str(e),
        }


def check_approvals() -> Dict[str, Any]:
    """
    Check for pending approval requests
    
    Returns:
        List of pending approvals
    """
    logger.info('Checking pending approvals')
    
    try:
        approval_path = Path('./AI_Employee_Vault/Pending_Approval')
        
        if not approval_path.exists():
            return {'status': 'success', 'pending_approvals': [], 'count': 0}
        
        approvals = []
        for f in approval_path.glob('*.md'):
            content = f.read_text()
            if 'status: pending' in content:
                approvals.append({
                    'file': f.name,
                    'path': str(f),
                })
        
        return {
            'status': 'success',
            'pending_approvals': approvals,
            'count': len(approvals),
        }
        
    except Exception as e:
        logger.error(f'Error checking approvals: {e}')
        return {
            'status': 'error',
            'error': str(e),
            'pending_approvals': [],
            'count': 0,
        }


def update_dashboard(
    section: str,
    content: str,
) -> Dict[str, Any]:
    """
    Update the Dashboard.md file
    
    Args:
        section: Section to update
        content: New content
        
    Returns:
        Result dictionary
    """
    logger.info(f'Updating dashboard: {section}')
    
    try:
        dashboard_path = Path('./AI_Employee_Vault/Dashboard.md')
        
        if not dashboard_path.exists():
            return {'status': 'error', 'error': 'Dashboard.md not found'}
        
        # Append to Recent Activity section
        content_md = dashboard_path.read_text()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_line = f'- [{timestamp}] {content}\n'
        
        if '| Timestamp | Action | Status |' in content_md:
            lines = content_md.split('\n')
            for i, line in enumerate(lines):
                if '|---|---|---|' in line:
                    lines.insert(i + 1, new_line.strip())
                    break
            content_md = '\n'.join(lines)
        
        dashboard_path.write_text(content_md)
        
        return {'status': 'success', 'message': f'Dashboard updated: {section}'}
        
    except Exception as e:
        logger.error(f'Error updating dashboard: {e}')
        return {'status': 'error', 'error': str(e)}


def create_odoo_invoice(
    partner_id: int,
    lines: List[Dict[str, Any]],
    invoice_type: str = 'out_invoice',
) -> Dict[str, Any]:
    """
    Create an invoice in Odoo via JSON-RPC
    
    Args:
        partner_id: Odoo partner ID
        lines: Invoice line items
        invoice_type: Type of invoice
        
    Returns:
        Result dictionary
    """
    logger.info(f'Creating Odoo invoice for partner {partner_id}')
    
    try:
        from src.services.odoo_client import OdooClient
        
        client = OdooClient()
        
        if not client.authenticate():
            return {
                'status': 'error',
                'error': 'Failed to authenticate with Odoo',
            }
        
        invoice_data = {
            'partner_id': partner_id,
            'move_type': invoice_type,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': line.get('product_id'),
                    'name': line.get('name', 'Product'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                })
                for line in lines
            ],
        }
        
        invoice_id = client.create('account.move', invoice_data)
        
        if invoice_id:
            return {
                'status': 'success',
                'invoice_id': invoice_id,
            }
        else:
            return {'status': 'error', 'error': 'Failed to create invoice'}
        
    except Exception as e:
        logger.error(f'Error creating Odoo invoice: {e}')
        return {'status': 'error', 'error': str(e)}


def record_odoo_payment(
    invoice_id: int,
    amount: float,
) -> Dict[str, Any]:
    """
    Record a payment in Odoo
    
    Args:
        invoice_id: Invoice ID
        amount: Payment amount
        
    Returns:
        Result dictionary
    """
    logger.info(f'Recording payment for invoice {invoice_id}')
    
    try:
        from src.services.odoo_client import OdooClient
        
        client = OdooClient()
        
        if not client.authenticate():
            return {'status': 'error', 'error': 'Failed to authenticate with Odoo'}
        
        # Simple payment recording
        result = client.register_payment(invoice_id, amount)
        
        if result:
            return {
                'status': 'success',
                'payment_id': result.get('id'),
            }
        else:
            return {'status': 'error', 'error': 'Failed to record payment'}
        
    except Exception as e:
        logger.error(f'Error recording payment: {e}')
        return {'status': 'error', 'error': str(e)}
