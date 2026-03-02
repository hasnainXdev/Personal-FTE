"""MCP Server for AI Employee Silver Tier.

This MCP (Model Context Protocol) server provides tools for:
- Sending emails via Gmail API
- Posting to LinkedIn via Playwright
- Managing approvals
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP library not installed. Install with: pip install mcp")
    sys.exit(1)

from src.services.linkedin_service import LinkedInService
from src.services.approval_service import ApprovalService
from src.watchers.gmail_watcher import GmailWatcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp-server")

# Create MCP server
server = Server("ai-employee-silver")

# Global services
vault_path: Optional[Path] = None
linkedin_service: Optional[LinkedInService] = None
approval_service: Optional[ApprovalService] = None
gmail_watcher: Optional[GmailWatcher] = None


def init_services(vault: str):
    """Initialize services with vault path."""
    global vault_path, linkedin_service, approval_service, gmail_watcher
    
    vault_path = Path(vault)
    
    # Initialize services
    linkedin_service = LinkedInService(str(vault_path))
    approval_service = ApprovalService(str(vault_path))
    
    # Initialize Gmail watcher (for sending)
    credentials_path = vault_path.parent / 'credentials.json'
    if credentials_path.exists():
        gmail_watcher = GmailWatcher(
            str(vault_path),
            str(credentials_path),
            check_interval=120
        )
    else:
        logger.warning("Gmail credentials not found - email sending disabled")
        gmail_watcher = None
    
    logger.info(f"Initialized MCP services for vault: {vault_path}")


@server.list_tools()
async def list_tools() -> list:
    """List available MCP tools."""
    return [
        Tool(
            name="send_email",
            description="Send an email via Gmail API (requires approval for first-time recipients)",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                    "in_reply_to": {"type": "string", "description": "Message ID to reply to"},
                    "skip_approval": {"type": "boolean", "description": "Skip approval if true (use with caution)"}
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="post_linkedin",
            description="Post an update to LinkedIn via Playwright (requires approval)",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Post content"},
                    "reason": {"type": "string", "description": "Reason for the post"},
                    "skip_approval": {"type": "boolean", "description": "Skip approval if true"}
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="create_approval_request",
            description="Create an approval request file for human review",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_type": {"type": "string", "description": "Type of request (email, payment, linkedin_post)"},
                    "details": {"type": "object", "description": "Request details as key-value pairs"},
                    "action_required": {"type": "string", "description": "Description of action to be taken"}
                },
                "required": ["request_type", "details", "action_required"]
            }
        ),
        Tool(
            name="check_approvals",
            description="Check for approved actions ready to execute",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="update_dashboard",
            description="Update the Dashboard.md with activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Action description"},
                    "status": {"type": "string", "description": "Status (success, pending, failed)", "enum": ["success", "pending", "failed"]}
                },
                "required": ["action", "status"]
            }
        ),
        Tool(
            name="linkedin_login",
            description="Initialize LinkedIn login (opens browser for manual login)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list:
    """Execute a tool."""
    try:
        if name == "send_email":
            return await handle_send_email(arguments)
        elif name == "post_linkedin":
            return await handle_post_linkedin(arguments)
        elif name == "create_approval_request":
            return handle_create_approval(arguments)
        elif name == "check_approvals":
            return handle_check_approvals()
        elif name == "update_dashboard":
            return handle_update_dashboard(arguments)
        elif name == "linkedin_login":
            return await handle_linkedin_login()
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_send_email(args: Dict[str, Any]) -> list:
    """Handle send_email tool."""
    to = args.get("to")
    subject = args.get("subject")
    body = args.get("body")
    in_reply_to = args.get("in_reply_to")
    skip_approval = args.get("skip_approval", False)
    
    if not gmail_watcher or not gmail_watcher.service:
        return [TextContent(type="text", text="Gmail service not initialized. Check credentials.")]
    
    # For first-time recipients or if approval not skipped, create approval request
    if not skip_approval:
        if approval_service:
            details = {
                "to": to,
                "subject": subject,
                "body_preview": body[:100] + "..." if len(body) > 100 else body
            }
            request_path = approval_service.create_approval_request(
                "email_send",
                details,
                f"Send email to {to} with subject: {subject}"
            )
            
            return [TextContent(
                type="text",
                text=f"Email approval request created: {request_path.name}. Move to /Approved/ to send."
            )]
    
    # Send email directly
    result = gmail_watcher.send_email(to, subject, body, in_reply_to)
    
    if result['success']:
        return [TextContent(
            type="text",
            text=f"Email sent successfully to {to}. Message ID: {result['message_id']}"
        )]
    else:
        return [TextContent(
            type="text",
            text=f"Failed to send email: {result['error']}"
        )]


async def handle_post_linkedin(args: Dict[str, Any]) -> list:
    """Handle post_linkedin tool."""
    content = args.get("content")
    reason = args.get("reason", "Business update")
    skip_approval = args.get("skip_approval", False)
    
    if not linkedin_service:
        return [TextContent(type="text", text="LinkedIn service not initialized")]
    
    # Check if logged in
    if not await linkedin_service.is_logged_in():
        return [TextContent(
            type="text",
            text="Not logged into LinkedIn. Run linkedin_login tool first or open browser manually."
        )]
    
    # For most posts, create approval request
    if not skip_approval:
        draft_path = linkedin_service.create_draft_post(content, reason)
        return [TextContent(
            type="text",
            text=f"LinkedIn post draft created: {draft_path.name}. Move to /Approved/ to post."
        )]
    
    # Post directly
    result = await linkedin_service.post_update(content)
    
    if result['success']:
        return [TextContent(
            type="text",
            text=f"LinkedIn post successful! Post ID: {result['post_id']}"
        )]
    else:
        return [TextContent(
            type="text",
            text=f"Failed to post: {result['error']}"
        )]


def handle_create_approval(args: Dict[str, Any]) -> list:
    """Handle create_approval_request tool."""
    request_type = args.get("request_type")
    details = args.get("details", {})
    action_required = args.get("action_required")
    
    if approval_service:
        request_path = approval_service.create_approval_request(
            request_type,
            details,
            action_required
        )
        
        return [TextContent(
            type="text",
            text=f"Approval request created: {request_path.name}"
        )]
    
    return [TextContent(type="text", text="Approval service not initialized")]


def handle_check_approvals() -> list:
    """Handle check_approvals tool."""
    if approval_service:
        approved = approval_service.check_approved()
        pending_count = approval_service.get_pending_count()
        
        result = f"Pending approvals: {pending_count}\n"
        result += f"Approved ready to execute: {len(approved)}\n"
        
        for f in approved[:5]:  # Show first 5
            result += f"  - {f.name}\n"
        
        return [TextContent(type="text", text=result)]
    
    return [TextContent(type="text", text="Approval service not initialized")]


def handle_update_dashboard(args: Dict[str, Any]) -> list:
    """Handle update_dashboard tool."""
    action = args.get("action")
    status = args.get("status")
    
    if vault_path:
        dashboard = vault_path / "Dashboard.md"
        if dashboard.exists():
            content = dashboard.read_text()
            
            # Add activity entry
            timestamp = datetime.now().strftime("%H:%M")
            entry = f"| {timestamp} | {action} | {status} |\n"
            
            # Find Today's Activity section and add entry
            if "## 📊 Today's Activity" in content:
                lines = content.split("\n")
                new_lines = []
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    if line.startswith("| Time |"):
                        new_lines.append(entry)
                
                content = "\n".join(new_lines)
                dashboard.write_text(content)
                
                return [TextContent(type="text", text="Dashboard updated")]
    
    return [TextContent(type="text", text="Failed to update dashboard")]


async def handle_linkedin_login() -> list:
    """Handle linkedin_login tool."""
    if not linkedin_service:
        return [TextContent(type="text", text="LinkedIn service not initialized")]
    
    try:
        # Initialize browser
        await linkedin_service.initialize()
        
        # Navigate to login
        await linkedin_service.login()
        
        return [TextContent(
            type="text",
            text="LinkedIn login browser opened. Please log in manually. Session will be saved for future use."
        )]
        
    except Exception as e:
        return [TextContent(type="text", text=f"LinkedIn login error: {str(e)}")]


async def main():
    """Run the MCP server."""
    # Get vault path from environment or argument
    vault = sys.argv[1] if len(sys.argv) > 1 else "./AI_Employee_Vault"
    init_services(vault)
    
    logger.info("Starting AI Employee Silver MCP Server")
    logger.info("Tools available: send_email, post_linkedin, create_approval_request, check_approvals, update_dashboard, linkedin_login")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
