"""
Odoo Community Edition Client

Client for interacting with Odoo via JSON-RPC API.
Supports Odoo 19+ Community Edition.
"""

import json
import logging
import requests
from typing import Any, Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)


class OdooClient:
    """Client for Odoo JSON-RPC API"""
    
    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Odoo client
        
        Args:
            url: Odoo server URL
            db: Database name
            username: Username
            api_key: API key
        """
        # Load from environment if not provided
        load_dotenv()
        
        self.url = url or os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = db or os.getenv('ODOO_DB')
        self.username = username or os.getenv('ODOO_USERNAME')
        self.api_key = api_key or os.getenv('ODOO_API_KEY')
        
        self.uid = None
        self.session = requests.Session()
        self._authenticated = False
        
        logger.info(f'Odoo client initialized for {self.url}')
    
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo
        
        Returns:
            True if authentication successful
        """
        if self._authenticated:
            return True
        
        try:
            # Odoo JSON-RPC authentication
            payload = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'common',
                    'method': 'authenticate',
                    'args': [
                        self.db,
                        self.username,
                        self.api_key,
                        {}
                    ]
                },
                'id': 1
            }
            
            response = self.session.post(
                f'{self.url}/jsonrpc',
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if 'result' in result:
                self.uid = result['result']
                self._authenticated = True
                logger.info(f'Odoo authentication successful, UID: {self.uid}')
                return True
            else:
                logger.error(f'Odoo authentication failed: {result}')
                return False
                
        except Exception as e:
            logger.error(f'Odoo authentication error: {e}')
            return False
    
    def execute(
        self,
        model: str,
        method: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute a method on an Odoo model
        
        Args:
            model: Model name (e.g., 'res.partner')
            method: Method name (e.g., 'create', 'write', 'search')
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Method result
        """
        if not self._authenticated:
            if not self.authenticate():
                return None
        
        try:
            payload = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.db,
                        self.uid,
                        self.api_key,
                        model,
                        method,
                        args or [],
                        kwargs or {}
                    ]
                },
                'id': 2
            }
            
            response = self.session.post(
                f'{self.url}/jsonrpc',
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            result = response.json()
            
            if 'result' in result:
                return result['result']
            else:
                logger.error(f'Odoo execute error: {result}')
                return None
                
        except Exception as e:
            logger.error(f'Odoo execute error: {e}')
            return None
    
    def search(
        self,
        model: str,
        domain: List[Any],
        limit: int = 80,
        offset: int = 0,
    ) -> List[int]:
        """
        Search for records
        
        Args:
            model: Model name
            domain: Search domain
            limit: Maximum results
            offset: Offset for pagination
            
        Returns:
            List of record IDs
        """
        return self.execute(
            model,
            'search',
            [domain],
            {'limit': limit, 'offset': offset}
        ) or []
    
    def search_read(
        self,
        model: str,
        domain: List[Any],
        fields: Optional[List[str]] = None,
        limit: int = 80,
    ) -> List[Dict[str, Any]]:
        """
        Search and read records
        
        Args:
            model: Model name
            domain: Search domain
            fields: Fields to return
            limit: Maximum results
            
        Returns:
            List of record dictionaries
        """
        return self.execute(
            model,
            'search_read',
            [domain],
            {'fields': fields or [], 'limit': limit}
        ) or []
    
    def create(self, model: str, values: Dict[str, Any]) -> Optional[int]:
        """
        Create a new record
        
        Args:
            model: Model name
            values: Field values
            
        Returns:
            New record ID
        """
        result = self.execute(model, 'create', [values])
        return result
    
    def write(
        self,
        model: str,
        ids: List[int],
        values: Dict[str, Any],
    ) -> bool:
        """
        Update records
        
        Args:
            model: Model name
            ids: Record IDs
            values: Field values to update
            
        Returns:
            True if successful
        """
        result = self.execute(model, 'write', [ids, values])
        return bool(result)
    
    def unlink(self, model: str, ids: List[int]) -> bool:
        """
        Delete records
        
        Args:
            model: Model name
            ids: Record IDs
            
        Returns:
            True if successful
        """
        result = self.execute(model, 'unlink', [ids])
        return bool(result)
    
    def read(self, model: str, ids: List[int], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Read records
        
        Args:
            model: Model name
            ids: Record IDs
            fields: Fields to return
            
        Returns:
            List of record dictionaries
        """
        return self.execute(
            model,
            'read',
            [ids],
            {'fields': fields or []}
        ) or []
    
    def create_invoice(
        self,
        partner_id: int,
        lines: List[Dict[str, Any]],
        invoice_type: str = 'out_invoice',
    ) -> Optional[int]:
        """
        Create a customer invoice
        
        Args:
            partner_id: Customer/partner ID
            lines: Invoice line items
            invoice_type: Type of invoice
            
        Returns:
            Invoice ID
        """
        invoice_data = {
            'partner_id': partner_id,
            'move_type': invoice_type,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': line.get('product_id'),
                    'name': line.get('name', 'Product'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                })
                for line in lines
            ],
        }
        
        return self.create('account.move', invoice_data)
    
    def register_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Register a payment for an invoice
        
        Args:
            invoice_id: Invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD)
            
        Returns:
            Payment result
        """
        try:
            # Create payment record
            payment_data = {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': self.read('account.move', [invoice_id], ['partner_id'])[0].get('partner_id'),
                'amount': amount,
                'payment_date': payment_date or self._today(),
                'journal_id': self._get_cash_journal_id(),
            }
            
            payment_id = self.create('account.payment', payment_data)
            
            if payment_id:
                # Post payment
                self.execute('account.payment', 'action_post', [[payment_id]])
                
                # Reconcile with invoice
                self.execute(
                    'account.payment',
                    'action_invoice_payment',
                    [[payment_id], invoice_id]
                )
                
                return {'id': payment_id, 'amount': amount}
            
            return None
            
        except Exception as e:
            logger.error(f'Error registering payment: {e}')
            return None
    
    def _get_cash_journal_id(self) -> Optional[int]:
        """Get the default cash journal ID"""
        journals = self.search_read(
            'account.journal',
            [('type', '=', 'cash')],
            fields=['id'],
            limit=1
        )
        return journals[0]['id'] if journals else None
    
    def _today(self) -> str:
        """Get today's date in YYYY-MM-DD format"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
    
    def get_partner_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find partner by email
        
        Args:
            email: Email address
            
        Returns:
            Partner record or None
        """
        partners = self.search_read(
            'res.partner',
            [('email', '=', email)],
            fields=['id', 'name', 'email', 'phone'],
            limit=1
        )
        return partners[0] if partners else None
    
    def create_partner(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Optional[int]:
        """
        Create a new partner
        
        Args:
            name: Partner name
            email: Email address
            phone: Phone number
            
        Returns:
            Partner ID
        """
        return self.create('res.partner', {
            'name': name,
            'email': email,
            'phone': phone,
        })
    
    def get_invoice_status(self, invoice_id: int) -> Optional[str]:
        """
        Get invoice payment status
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Status string (draft, posted, paid, cancelled)
        """
        result = self.read('account.move', [invoice_id], ['payment_state'])
        return result[0].get('payment_state') if result else None
    
    def get_financial_summary(
        self,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """
        Get financial summary for period
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Summary dictionary
        """
        # Get total invoices
        invoices = self.search_read(
            'account.move',
            [
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
            ],
            fields=['amount_total', 'amount_residual', 'payment_state']
        )
        
        total_revenue = sum(inv.get('amount_total', 0) for inv in invoices)
        outstanding = sum(inv.get('amount_residual', 0) for inv in invoices)
        paid = total_revenue - outstanding
        
        return {
            'period': f'{start_date} to {end_date}',
            'total_invoices': len(invoices),
            'total_revenue': total_revenue,
            'total_paid': paid,
            'outstanding': outstanding,
            'invoices': invoices,
        }
