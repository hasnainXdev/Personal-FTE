"""
Gold Tier AI Employee - MCP Server Module

MCP (Model Context Protocol) servers provide the "hands" for the AI Employee.
Gold Tier: Email, LinkedIn, Facebook, Odoo
"""

from .tools import (
    send_email,
    post_linkedin,
    post_facebook,
    create_approval_request,
    check_approvals,
    update_dashboard,
    create_odoo_invoice,
    record_odoo_payment,
)

__all__ = [
    'send_email',
    'post_linkedin',
    'post_facebook',
    'create_approval_request',
    'check_approvals',
    'update_dashboard',
    'create_odoo_invoice',
    'record_odoo_payment',
]
