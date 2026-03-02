"""Gmail Watcher - Monitors Gmail for important unread emails."""

import logging
import base64
import os
from pathlib import Path
from datetime import datetime
from email.utils import parsedate_to_datetime

from .base_watcher import BaseWatcher


class GmailWatcher(BaseWatcher):
    """Watches Gmail for important unread emails and creates action files.
    
    This watcher:
    1. Connects to Gmail API using OAuth2
    2. Checks for unread, important emails
    3. Creates action files in /Needs_Action/
    4. Tracks processed message IDs to avoid duplicates
    
    Mock Mode:
    Set GMAIL_MOCK_MODE=true to use mock emails for testing
    """
    
    # Priority keywords
    PRIORITY_KEYWORDS = {
        'high': ['urgent', 'asap', 'emergency', 'important', 'priority', 'invoice', 'payment'],
        'medium': ['meeting', 'call', 'deadline', 'review', 'approval'],
        'low': ['newsletter', 'promo', 'offer', 'discount']
    }
    
    # Mock emails for testing
    MOCK_EMAILS = [
        {
            'id': 'mock_001',
            'from': 'client@example.com',
            'subject': 'Urgent: Invoice Request',
            'body': 'Hi, please send the invoice for January services. We need it ASAP for payment processing.',
            'date': datetime.now().isoformat()
        },
        {
            'id': 'mock_002',
            'from': 'partner@company.com',
            'subject': 'Meeting Tomorrow',
            'body': 'Just confirming our meeting scheduled for tomorrow at 2 PM.',
            'date': datetime.now().isoformat()
        },
        {
            'id': 'mock_003',
            'from': 'newsletter@tech.com',
            'subject': 'Weekly Tech Newsletter',
            'body': 'Check out this week top tech news and updates.',
            'date': datetime.now().isoformat()
        }
    ]
    
    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
        """Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to Gmail OAuth2 credentials JSON
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        self.credentials_path = Path(credentials_path)
        self.service = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Check for mock mode
        self.mock_mode = os.getenv('GMAIL_MOCK_MODE', 'false').lower() == 'true'
        if self.mock_mode:
            self.logger.info("Gmail watcher running in MOCK mode")
        
        # Track mock emails sent
        self.mock_sent = set()
        
        # Load state including processed message IDs
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Gmail API credentials."""
        if self.mock_mode:
            return
            
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            import json
            
            self.creds = None
            token_file = self.vault_path / 'token.json'  # Changed from token.pickle
            
            # Load existing credentials from JSON
            if token_file.exists():
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                    self.creds = Credentials.from_authorized_user_info(token_data)
            
            # Refresh or get new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                elif self.credentials_path.exists():
                    # Run local server flow for initial auth
                    # SCOPES: readonly + labels + send + compose for full email functionality
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        ['https://www.googleapis.com/auth/gmail.readonly',
                         'https://www.googleapis.com/auth/gmail.labels',
                         'https://www.googleapis.com/auth/gmail.send',
                         'https://www.googleapis.com/auth/gmail.compose']
                    )
                    # Use port 8085 (Google's default for desktop apps)
                    self.creds = flow.run_local_server(port=8085)
                else:
                    self.logger.error("Credentials file not found")
                    return
            
            # Save credentials to JSON (changed from pickle)
            if self.creds:
                token_data = {
                    'token': self.creds.token,
                    'refresh_token': self.creds.refresh_token,
                    'token_uri': self.creds.token_uri,
                    'client_id': self.creds.client_id,
                    'client_secret': self.creds.client_secret,
                    'scopes': self.creds.scopes
                }
                with open(token_file, 'w') as f:
                    json.dump(token_data, f, indent=2)
                self.logger.info(f"Credentials saved to {token_file}")
            
            # Build service
            self.service = build('gmail', 'v1', credentials=self.creds)
            self.logger.info("Gmail API connected successfully with send permissions")
            
        except Exception as e:
            self.logger.error(f"Failed to load Gmail credentials: {e}")
            self.service = None
    
    def check_for_updates(self) -> list:
        """Check Gmail for new important unread emails.
        
        Returns:
            List of new message IDs to process
        """
        # Return mock emails in mock mode
        if self.mock_mode:
            return self._get_mock_emails()
        
        if not self.service:
            self._load_credentials()
            if not self.service:
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
                msg_id = msg['id']
                if msg_id not in self.processed_ids:
                    new_messages.append(msg_id)
                    self.processed_ids.add(msg_id)
                    self.logger.info(f"New email detected: {msg_id}")
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []
    
    def _get_mock_emails(self) -> list:
        """Get mock emails for testing."""
        new_emails = []
        for email in self.MOCK_EMAILS:
            if email['id'] not in self.mock_sent:
                new_emails.append(email)
                self.mock_sent.add(email['id'])
        return new_emails
    
    def create_action_file(self, item) -> Path:
        """Create action file for the email.
        
        Args:
            item: Gmail message ID or mock email dict
            
        Returns:
            Path to the created action file
        """
        # Handle mock email
        if isinstance(item, dict):
            return self._create_mock_action_file(item)
        
        # Handle real Gmail message
        return self._create_gmail_action_file(item)
    
    def _create_mock_action_file(self, email: dict) -> Path:
        """Create action file for mock email."""
        message_id = email['id']
        from_email = email['from']
        subject = email['subject']
        body = email['body']
        date = email.get('date', datetime.now().isoformat())
        
        # Determine priority
        priority = self.get_priority(f"{subject} {body}", self.PRIORITY_KEYWORDS)
        
        # Generate unique ID
        file_id = self.generate_unique_id("EMAIL")
        
        # Create action file
        meta_path = self.needs_action / f"{file_id}.md"
        
        content = f"""---
type: email
file_id: {file_id}
gmail_id: {message_id}
from: {from_email}
subject: {subject}
date: {date}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
labels: unread
mock_mode: true
---

# Email: {subject}

## Sender
**From**: {from_email}
**Date**: {date}

## Email Content

{body}

## Instructions for Qwen

1. Read and understand the email content
2. Classify by type and priority
3. Draft appropriate response if needed
4. Create approval request for sending
5. Move to /Done/ when processed

## Suggested Actions

- [ ] Read email content
- [ ] Classify priority ({priority})
- [ ] Draft response (if needed)
- [ ] Create approval request for sending
- [ ] Mark as read in Gmail
- [ ] Move to /Done/

---

*Created by GmailWatcher (MOCK MODE)*
*Email ID: {message_id}*
"""
        
        meta_path.write_text(content)
        self.logger.info(f"Created mock action file: {meta_path.name}")
        
        return meta_path
    
    def _create_gmail_action_file(self, message_id: str) -> Path:
        """Create action file for real Gmail message."""
        try:
            # Get message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', datetime.now().isoformat())
            
            # Get body
            body = self._get_email_body(message)
            
            # Determine priority
            priority = self.get_priority(f"{subject} {body}", self.PRIORITY_KEYWORDS)
            
            # Generate unique ID
            file_id = self.generate_unique_id("EMAIL")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create action file
            meta_path = self.needs_action / f"{file_id}.md"
            
            content = f"""---
type: email
file_id: {file_id}
gmail_id: {message_id}
from: {from_email}
subject: {subject}
date: {date}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
labels: unread
---

# Email: {subject}

## Sender
**From**: {from_email}
**Date**: {date}

## Email Content

{body}

## Instructions for Qwen

1. Read and understand the email content
2. Classify by type and priority
3. Draft appropriate response if needed
4. Create approval request for sending
5. Move to /Done/ when processed

## Suggested Actions

- [ ] Read email content
- [ ] Classify priority ({priority})
- [ ] Draft response (if needed)
- [ ] Create approval request for sending
- [ ] Mark as read in Gmail
- [ ] Move to /Done/

---

*Created by GmailWatcher*
*Gmail ID: {message_id}*
"""
            
            meta_path.write_text(content)
            self.logger.info(f"Created action file: {meta_path.name}")
            
            return meta_path
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise
    
    def _get_email_body(self, message: dict) -> str:
        """Extract the email body from the message."""
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            
            # Fallback to body
            if 'body' in message['payload']:
                data = message['payload']['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return "[No text content]"
            
        except Exception as e:
            self.logger.error(f"Error extracting email body: {e}")
            return "[Error extracting content]"
    
    def mark_as_read(self, message_id: str):
        """Mark an email as read in Gmail."""
        if not self.service or self.mock_mode:
            return
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.info(f"Marked message {message_id} as read")
        except Exception as e:
            self.logger.error(f"Error marking message as read: {e}")
    
    def send_email(self, to: str, subject: str, body: str, 
                   in_reply_to: str = None) -> dict:
        """Send an email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            in_reply_to: Message ID to reply to (optional)
            
        Returns:
            dict with send result
        """
        result = {
            'success': False,
            'message_id': None,
            'error': None
        }
        
        if self.mock_mode:
            result['error'] = 'Mock mode - email not sent'
            return result
        
        if not self.service:
            result['error'] = 'Gmail service not initialized'
            return result
        
        try:
            from email.mime.text import MIMEText
            import base64
            
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['from'] = 'AI Employee'
            message['subject'] = subject
            
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            result['success'] = True
            result['message_id'] = sent_message['id']
            self.logger.info(f"Email sent to {to}: {sent_message['id']}")
            
            # Log the sent email
            self._log_sent_email(to, subject, body, sent_message['id'])
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Failed to send email: {e}")
        
        return result
    
    def _log_sent_email(self, to: str, subject: str, body: str, message_id: str):
        """Log sent email to logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'email_sent_{today}.md'
        
        entry = f"""
## Email Sent - {datetime.now().isoformat()}

**To**: {to}
**Subject**: {subject}
**Message ID**: {message_id}

**Body**:
{body[:300]}{'...' if len(body) > 300 else ''}

---
"""
        
        if log_file.exists():
            content = log_file.read_text()
            log_file.write_text(content + entry)
        else:
            log_file.write_text(f"""---
type: email_sent_log
date: {today}
---

# Emails Sent - {today}
{entry}
""")
