"""
Gmail Watcher

Monitors Gmail for new unread/important messages and creates
action files in the Needs_Action folder.
"""

import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from email import message_from_bytes

from .base_watcher import BaseWatcher


class GmailWatcher(BaseWatcher):
    """Watcher for Gmail messages"""
    
    def __init__(
        self,
        vault_path: str,
        credentials_path: str,
        token_path: str,
        check_interval: int = 120,
    ):
        """
        Initialize Gmail watcher
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail credentials JSON
            token_path: Path to store OAuth token
            check_interval: Seconds between checks
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        self.urgent_keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'important']
        self.vip_senders = []  # Populate from config
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API
        
        Returns:
            True if authentication successful
        """
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            creds = None
            
            # Load existing token
            if self.token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    self.token_path,
                    ['https://www.googleapis.com/auth/gmail.readonly']
                )
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        ['https://www.googleapis.com/auth/gmail.readonly']
                    )
                    creds = flow.run_local_server(port=8080)
                
                # Save token
                self.token_path.write_text(creds.to_json())
            
            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail authentication successful')
            return True
            
        except Exception as e:
            self.logger.error(f'Gmail authentication failed: {e}')
            return False
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new unread/important emails
        
        Returns:
            List of new messages
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            new_messages = []
            
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
                    self.processed_ids.add(msg['id'])
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f'Error checking for updates: {e}')
            return []
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create action file for email message
        
        Args:
            message: Gmail message dict
            
        Returns:
            Path to created action file
        """
        try:
            # Get full message
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
            
            # Determine priority
            subject = headers.get('Subject', '').lower()
            sender = headers.get('From', '')
            priority = self._determine_priority(subject, sender)
            
            # Get body
            body = self._extract_body(msg)
            
            # Get attachments info
            attachments = self._get_attachments_info(msg)
            
            # Create action file content
            action_id = self.generate_unique_id('EMAIL')
            content = f'''---
type: email
action_id: {action_id}
from: {headers.get('From', 'Unknown')}
to: {headers.get('To', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
message_id: {message['id']}
has_attachments: {str(len(attachments) > 0).lower()}
---

# Email Received

## Header Information
- **From**: {headers.get('From', 'Unknown')}
- **To**: {headers.get('To', 'Unknown')}
- **Subject**: {headers.get('Subject', 'No Subject')}
- **Date**: {headers.get('Date', 'Unknown')}
- **Priority**: {priority.upper()}

## Email Content
{body}

## Attachments
{self._format_attachments(attachments)}

## Suggested Actions
- [ ] Read and understand email content
- [ ] Draft appropriate response
- [ ] Request approval if sending reply (first time)
- [ ] Mark as read after processing
- [ ] Move to /Done when complete

## Response Draft
[Draft your response here]

---
*Created by GmailWatcher*
'''
            
            action_path = self.needs_action / f'{action_id}.md'
            action_path.write_text(content)
            
            self.logger.info(f'Created action file for email from {sender}')
            return action_path
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None
    
    def _extract_body(self, msg: Dict[str, Any]) -> str:
        """Extract email body from message"""
        try:
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'body' in msg['payload']:
                data = msg['payload']['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            self.logger.error(f'Error extracting body: {e}')
        
        return msg.get('snippet', '[No content available]')
    
    def _get_attachments_info(self, msg: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get information about email attachments"""
        attachments = []
        
        try:
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['filename']:
                        attachments.append({
                            'filename': part['filename'],
                            'mimeType': part['mimeType'],
                            'size': part['body'].get('size', 0),
                            'attachmentId': part['body'].get('attachmentId', '')
                        })
        except Exception as e:
            self.logger.error(f'Error getting attachments: {e}')
        
        return attachments
    
    def _determine_priority(self, subject: str, sender: str) -> str:
        """Determine email priority based on content"""
        # Check for urgent keywords
        for keyword in self.urgent_keywords:
            if keyword in subject.lower():
                return 'high'
        
        # Check for VIP senders
        for vip in self.vip_senders:
            if vip.lower() in sender.lower():
                return 'high'
        
        return 'normal'
    
    def _format_attachments(self, attachments: List[Dict[str, Any]]) -> str:
        """Format attachments list for display"""
        if not attachments:
            return '_No attachments_'
        
        lines = ['| Filename | Type | Size |', '|----------|------|------|']
        for att in attachments:
            size = self._format_size(att.get('size', 0))
            lines.append(f"| {att['filename']} | {att['mimeType']} | {size} |")
        
        return '\n'.join(lines)
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} GB'
