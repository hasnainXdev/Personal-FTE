#!/usr/bin/env python3
"""Fetch real Gmail emails and create action files."""

import sys
import json
import base64
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

VAULT_PATH = Path('./AI_Employee_Vault')
CREDENTIALS_PATH = Path('./credentials.json')
TOKEN_PATH = VAULT_PATH / 'token.json'
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'

# Priority keywords
PRIORITY_KEYWORDS = {
    'high': ['urgent', 'asap', 'emergency', 'important', 'priority', 'invoice', 'payment'],
    'medium': ['meeting', 'call', 'deadline', 'review', 'approval'],
    'low': ['newsletter', 'promo', 'offer', 'discount']
}


def get_priority(text: str, keywords: dict) -> str:
    """Determine priority based on keywords."""
    text_lower = text.lower()
    for priority, words in keywords.items():
        if any(word in text_lower for word in words):
            return priority
    return 'medium'


def fetch_emails():
    """Fetch unread emails from Gmail and create action files."""
    logger.info("=" * 60)
    logger.info("📧 GMAIL FETCHER - Starting")
    logger.info("=" * 60)
    
    # Load token
    if not TOKEN_PATH.exists():
        logger.error("❌ Token file not found. Authenticate first.")
        return
    
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)
    
    # Load credentials
    creds = Credentials.from_authorized_user_info(token_data)
    
    # Refresh if needed
    if not creds.valid:
        logger.info("⚠️  Token expired, refreshing...")
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
            # Save refreshed token
            new_token = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            with open(TOKEN_PATH, 'w') as f:
                json.dump(new_token, f, indent=2)
            logger.info("✅ Token refreshed and saved")
        else:
            logger.error("❌ Cannot refresh token")
            return
    
    # Build service
    service = build('gmail', 'v1', credentials=creds)
    logger.info("✅ Gmail API connected")
    
    # Get profile
    profile = service.users().getProfile(userId='me').execute()
    logger.info(f"📧 Logged in as: {profile['emailAddress']}")
    
    # Load processed IDs
    state_file = VAULT_PATH / 'Logs_Extended' / 'watcher_gmail_state.md'
    processed_ids = set()
    if state_file.exists():
        content = state_file.read_text()
        for line in content.split('\n'):
            if line.startswith('processed_id:'):
                processed_ids.add(line.split(':')[1].strip())
    
    # Fetch unread emails
    logger.info("📬 Fetching unread emails...")
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=10
    ).execute()
    
    messages = results.get('messages', [])
    logger.info(f"Found {len(messages)} unread emails")
    
    new_count = 0
    for msg in messages:
        msg_id = msg['id']
        
        if msg_id in processed_ids:
            continue
        
        # Get message details
        msg_detail = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = {h['name']: h['value'] for h in msg_detail['payload']['headers']}
        from_email = headers.get('From', 'Unknown')
        subject = headers.get('Subject', 'No Subject')
        date = headers.get('Date', datetime.now().isoformat())
        
        # Get body
        body = extract_body(msg_detail)
        
        # Determine priority
        priority = get_priority(f"{subject} {body}", PRIORITY_KEYWORDS)
        
        # Generate unique ID
        file_id = f"EMAIL_{msg_id[:12]}"
        
        # Create action file
        meta_path = NEEDS_ACTION / f"{file_id}.md"
        
        content = f"""---
type: email
file_id: {file_id}
gmail_id: {msg_id}
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

*Created by GmailFetcher*
*Gmail ID: {msg_id}*
"""
        
        meta_path.write_text(content, encoding='utf-8')
        logger.info(f"✅ Created: {meta_path.name}")
        
        # Mark as processed
        processed_ids.add(msg_id)
        new_count += 1
    
    # Save state
    state_content = f"""---
type: gmail_watcher_state
last_check: {datetime.now().isoformat()}
processed_count: {len(processed_ids)}
---

# Gmail Watcher State

## Processed Message IDs

"""
    for pid in processed_ids:
        state_content += f"processed_id: {pid}\n"
    
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(state_content, encoding='utf-8')
    
    logger.info("=" * 60)
    logger.info(f"✅ Fetch complete! Created {new_count} new action files")
    logger.info("=" * 60)


def extract_body(message: dict) -> str:
    """Extract email body from message."""
    try:
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        
        if 'body' in message['payload']:
            data = message['payload']['body'].get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return "[No text content]"
    except Exception as e:
        return f"[Error extracting content: {e}]"


if __name__ == '__main__':
    fetch_emails()
