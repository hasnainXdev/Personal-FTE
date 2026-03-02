"""
Email Action Handler - Send emails via SMTP or Gmail API

Handles all outbound email actions through MCP server.
Supports both SMTP and Gmail API (OAuth 2.0).
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64

from ai_employee.services.gmail_oauth import get_gmail_credentials

logger = logging.getLogger(__name__)


def _create_message(sender: str, to: str, subject: str, body: str, html: bool = False) -> dict:
    """Create a MIME message for Gmail API."""
    message = MIMEMultipart("alternative")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    
    content_type = "html" if html else "plain"
    message.attach(MIMEText(body, content_type))
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw_message}


async def _send_via_gmail_api(to: str, subject: str, body: str, from_email: str | None = None, html: bool = False) -> dict:
    """Send email using Gmail API."""
    credentials = get_gmail_credentials()
    if not credentials:
        raise ValueError("Gmail API credentials not available. Run setup first.")
    
    try:
        service = build("gmail", "v1", credentials=credentials)
        sender = from_email or credentials.id_token.get("email", "")
        
        if not sender:
            raise ValueError("Sender email not specified and cannot be retrieved from credentials")
        
        message = _create_message(sender, to, subject, body, html)
        
        # Send message
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        
        logger.info(f"Email sent via Gmail API to {to}, message ID: {sent_message['id']}")
        
        return {
            "message_id": sent_message["id"],
            "status": "sent",
            "recipient": to,
            "subject": subject,
            "method": "gmail_api",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HttpError as e:
        logger.error(f"Gmail API error: {e}")
        raise ValueError(f"Gmail API error ({e.resp.status}): {e.content.decode()}")


async def send_email(
    to: str,
    subject: str,
    body: str,
    from_email: str | None = None,
    html: bool = False,
    use_gmail_api: bool | None = None,
) -> dict:
    """
    Send an email via SMTP or Gmail API.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        from_email: Sender email (defaults to SMTP_USER or Gmail account)
        html: Whether body is HTML (default: False)
        use_gmail_api: Force Gmail API (True), SMTP (False), or auto-detect (None)

    Returns:
        dict with message_id and status
    """
    # Auto-detect method if not specified
    if use_gmail_api is None:
        use_gmail_api = get_gmail_credentials() is not None
    
    # Use Gmail API if available and preferred
    if use_gmail_api:
        try:
            return await _send_via_gmail_api(to, subject, body, from_email, html)
        except Exception as e:
            logger.warning(f"Gmail API failed, falling back to SMTP: {e}")
            if not os.getenv("SMTP_USER") or not os.getenv("SMTP_PASS"):
                raise
            # Fall through to SMTP
    
    # Use SMTP
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        raise ValueError("SMTP credentials not configured. Set SMTP_USER and SMTP_PASS in .env")

    if from_email is None:
        from_email = smtp_user

    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to

    # Attach body
    content_type = "html" if html else "plain"
    msg.attach(MIMEText(body, content_type))

    try:
        logger.info(f"Sending email to {to} with subject: {subject} (via SMTP)")

        # Connect and send
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        # Generate message ID
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        message_id = f"<{timestamp}.smtp.{os.getpid()}@{smtp_host}>"

        logger.info(f"Email sent successfully to {to} (via SMTP)")

        return {
            "message_id": message_id,
            "status": "sent",
            "recipient": to,
            "subject": subject,
            "method": "smtp",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        raise ValueError(f"SMTP authentication failed. Check credentials: {e}")

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise ValueError(f"Failed to send email: {e}")
