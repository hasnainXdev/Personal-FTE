"""
Email Action Handler - Send emails via SMTP

Handles all outbound email actions through MCP server.
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)


async def send_email(
    to: str,
    subject: str,
    body: str,
    from_email: str | None = None,
    html: bool = False,
) -> dict:
    """
    Send an email via SMTP.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        from_email: Sender email (defaults to SMTP_USER env)
        html: Whether body is HTML (default: False)
    
    Returns:
        dict with message_id and status
    """
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
        logger.info(f"Sending email to {to} with subject: {subject}")
        
        # Connect and send
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        # Generate message ID
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        message_id = f"<{timestamp}.smtp.{os.getpid()}@{smtp_host}>"
        
        logger.info(f"Email sent successfully to {to}")
        
        return {
            "message_id": message_id,
            "status": "sent",
            "recipient": to,
            "subject": subject,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        raise ValueError(f"SMTP authentication failed. Check credentials: {e}")
    
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise ValueError(f"Failed to send email: {e}")
