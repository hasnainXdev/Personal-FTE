"""
Gmail Watcher - Poll Gmail for new messages

Polls Gmail inbox using OAuth2 authentication and routes
new messages to Bronze Inbox for processing.
"""

import logging
import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from .base_watcher import Watcher

logger = logging.getLogger(__name__)


class GmailWatcher(Watcher):
    """Watcher for Gmail inbox"""
    
    def __init__(
        self,
        state_dir: Path | None = None,
        inbox_dir: Path | None = None,
        interval_seconds: int = 60,
    ):
        """
        Initialize Gmail watcher.
        
        Args:
            state_dir: Directory for state persistence (default: Logs_Extended)
            inbox_dir: Directory to write processed items (default: Inbox)
            interval_seconds: Polling interval
        """
        # Default paths relative to project root
        if state_dir is None:
            state_dir = Path(__file__).parent.parent.parent / "Logs_Extended"
        if inbox_dir is None:
            inbox_dir = Path(__file__).parent.parent.parent / "AI_Employee_Vault" / "Inbox"
        
        super().__init__(
            name="gmail",
            state_dir=state_dir,
            inbox_dir=inbox_dir,
            interval_seconds=interval_seconds,
        )
        
        self.oauth_token = os.getenv("GMAIL_OAUTH_TOKEN")
        self.refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")
        
        if not self.oauth_token and not self.refresh_token:
            logger.warning("Gmail OAuth credentials not configured")
    
    def _fetch_items(self, since: datetime) -> list:
        """
        Fetch emails from Gmail since the given timestamp.
        
        Uses Gmail API with OAuth2 authentication.
        """
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            if not self.oauth_token:
                logger.warning("Gmail OAuth token not configured, skipping poll")
                return []
            
            # Build credentials
            credentials = Credentials(
                token=self.oauth_token,
                refresh_token=self.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GMAIL_CLIENT_ID"),
                client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
            )
            
            # Build Gmail service
            service = build("gmail", "v1", credentials=credentials)
            
            # Calculate timestamp for query (Gmail uses Unix timestamp in seconds)
            since_timestamp = int(since.timestamp())
            
            # Query for messages after the timestamp
            query = f"after:{since_timestamp}"
            
            # Fetch message IDs
            results = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get("messages", [])
            logger.info(f"Found {len(messages)} messages matching query: {query}")
            
            # Fetch full message details
            items = []
            for msg in messages:
                full_msg = service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format="metadata",
                    metadataHeaders=["From", "To", "Subject", "Date"]
                ).execute()
                items.append(full_msg)
            
            return items
        
        except ImportError:
            logger.warning("Google API libraries not installed, skipping Gmail poll")
            return []
        
        except Exception as e:
            logger.error(f"Failed to fetch Gmail messages: {e}")
            return []
    
    def _extract_id(self, item) -> str:
        """Extract unique message ID from email"""
        msg_id = item.get("id", "unknown")
        return f"MSG_{msg_id}"
    
    def _process_item(self, item, item_id: str):
        """
        Process email and save to Inbox as markdown.
        
        Creates a markdown file with email metadata and content.
        """
        # Extract email metadata
        headers = item.get("payload", {}).get("headers", [])
        metadata = {}
        for header in headers:
            name = header.get("name", "")
            value = header.get("value", "")
            if name.lower() in ["from", "to", "subject", "date"]:
                metadata[name.lower()] = value
        
        # Parse date
        date_str = metadata.get("date", "")
        try:
            date_obj = parsedate_to_datetime(date_str)
            iso_date = date_obj.isoformat()
        except Exception:
            iso_date = datetime.now(timezone.utc).isoformat()
        
        # Create markdown content
        subject = metadata.get("subject", "No Subject")
        from_addr = metadata.get("from", "Unknown")
        
        content = f"""---
Source: Gmail
Source_ID: {item_id}
Received: {iso_date}
From: {from_addr}
Subject: {subject}
---

# Email: {subject}

**From**: {from_addr}
**Date**: {iso_date}

## Content

[Email content would be fetched with full message retrieval]

---
*Processed by Gmail Watcher*
"""
        
        # Write to Inbox
        # Sanitize item_id for filename
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", item_id)
        inbox_file = self.inbox_dir / f"{safe_id}.md"
        
        inbox_file.write_text(content, encoding="utf-8")
        logger.info(f"Saved email to Inbox: {inbox_file.name}")


def run_watcher():
    """Entry point for running Gmail watcher"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gmail Watcher")
    parser.add_argument("--test", action="store_true", help="Run test poll")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval")
    args = parser.parse_args()
    
    watcher = GmailWatcher(interval_seconds=args.interval)
    
    if args.test:
        print("Running test poll...")
        count = watcher.poll()
        print(f"Processed {count} items")
    else:
        print("Running single poll...")
        count = watcher.poll()
        print(f"Processed {count} items")


if __name__ == "__main__":
    run_watcher()
