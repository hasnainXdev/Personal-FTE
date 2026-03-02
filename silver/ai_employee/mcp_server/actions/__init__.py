"""
MCP Action Handlers Registration

All external action handlers are registered here.
"""

import logging
from . import email, linkedin, webhook

logger = logging.getLogger(__name__)


def register_all_handlers(register_func):
    """Register all action handlers with the MCP server"""
    # Register email actions
    if hasattr(email, "send_email"):
        register_func("send_email", email.send_email)
        logger.info("Registered action: send_email")

    # Register LinkedIn actions
    if hasattr(linkedin, "post_linkedin"):
        register_func("post_linkedin", linkedin.post_linkedin)
        logger.info("Registered action: post_linkedin")

    # Register webhook actions
    if hasattr(webhook, "fetch_url"):
        register_func("fetch_url", webhook.fetch_url)
        logger.info("Registered action: fetch_url")

    if hasattr(webhook, "trigger_webhook"):
        register_func("trigger_webhook", webhook.trigger_webhook)
        logger.info("Registered action: trigger_webhook")

    logger.info("All action handlers registered")
