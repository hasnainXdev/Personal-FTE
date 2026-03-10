"""
MCP Server for Gold Tier AI Employee

This module provides the MCP (Model Context Protocol) server
that exposes tools for the AI Employee to use.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def run_mcp_server(vault_path: str) -> None:
    """
    Run the MCP server
    
    Args:
        vault_path: Path to Obsidian vault
    """
    logger.info(f'Starting MCP server with vault: {vault_path}')
    
    # For now, we'll use a simple HTTP-based MCP server
    # In production, you would use the official MCP SDK
    
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        import uvicorn
        
        app = FastAPI(title='AI Employee MCP Server')
        
        # Store vault path in app state
        app.state.vault_path = Path(vault_path)
        
        # Define request/response models
        class ToolRequest(BaseModel):
            tool: str
            params: Dict[str, Any] = {}
        
        class ToolResponse(BaseModel):
            status: str
            result: Any = None
            error: str = None
        
        @app.get('/health')
        async def health_check():
            return {'status': 'healthy', 'vault': str(app.state.vault_path)}
        
        @app.post('/tool/{tool_name}')
        async def call_tool(tool_name: str, request: ToolRequest) -> ToolResponse:
            """Call an MCP tool"""
            try:
                result = await execute_tool(
                    tool_name,
                    request.params,
                    app.state.vault_path
                )
                return ToolResponse(status='success', result=result)
            except Exception as e:
                logger.error(f'Tool error: {e}')
                return ToolResponse(status='error', error=str(e))
        
        @app.get('/tools')
        async def list_tools():
            """List available tools"""
            return {
                'tools': [
                    {'name': 'send_email', 'description': 'Send an email'},
                    {'name': 'post_linkedin', 'description': 'Post to LinkedIn'},
                    {'name': 'post_facebook', 'description': 'Post to Facebook'},
                    {'name': 'create_approval_request', 'description': 'Create approval request'},
                    {'name': 'check_approvals', 'description': 'Check pending approvals'},
                    {'name': 'update_dashboard', 'description': 'Update dashboard'},
                    {'name': 'create_odoo_invoice', 'description': 'Create Odoo invoice'},
                    {'name': 'record_odoo_payment', 'description': 'Record Odoo payment'},
                ]
            }
        
        # Run server
        uvicorn.run(app, host='0.0.0.0', port=8765)
        
    except ImportError:
        logger.error('FastAPI not installed. Install with: pip install fastapi uvicorn')
        logger.info('MCP server not available. Using direct tool calls instead.')


async def execute_tool(tool_name: str, params: Dict[str, Any], vault_path: Path) -> Any:
    """
    Execute a tool

    Args:
        tool_name: Name of tool to execute
        params: Tool parameters
        vault_path: Path to vault

    Returns:
        Tool result
    """
    from .mcp.tools import (
        send_email,
        post_linkedin,
        post_facebook,
        create_approval_request,
        check_approvals,
        update_dashboard,
        create_odoo_invoice,
        record_odoo_payment,
    )

    tools = {
        'send_email': send_email,
        'post_linkedin': post_linkedin,
        'post_facebook': post_facebook,
        'create_approval_request': create_approval_request,
        'check_approvals': check_approvals,
        'update_dashboard': update_dashboard,
        'create_odoo_invoice': create_odoo_invoice,
        'record_odoo_payment': record_odoo_payment,
    }

    if tool_name not in tools:
        raise ValueError(f'Unknown tool: {tool_name}')

    return tools[tool_name](**params)
