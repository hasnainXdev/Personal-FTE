"""
Gold Tier AI Employee - Services Module

Services provide integration with external systems like Odoo.
"""

from .odoo_client import OdooClient

__all__ = ['OdooClient']
