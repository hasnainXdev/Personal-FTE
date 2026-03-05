#!/usr/bin/env python3
"""
Test Odoo Integration

Tests Odoo connection and basic operations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from services.odoo_client import OdooClient


def test_connection():
    """Test Odoo connection"""
    print("=" * 60)
    print("ODOO INTEGRATION TEST")
    print("=" * 60)
    
    client = OdooClient()
    
    # Test 1: Authentication
    print("\n[TEST 1] Authenticating with Odoo...")
    if client.authenticate():
        print(f"✓ Odoo connected!")
        print(f"  URL: {client.url}")
        print(f"  Database: {client.db}")
        print(f"  User ID: {client.uid}")
    else:
        print("✗ Odoo connection failed")
        print("  Check: ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY in .env")
        return False
    
    # Test 2: List existing partners
    print("\n[TEST 2] Listing existing partners...")
    try:
        partners = client.search_read(
            'res.partner',
            [],
            fields=['id', 'name', 'email'],
            limit=5
        )
        
        if partners:
            print(f"✓ Found {len(partners)} partners:")
            for p in partners:
                print(f"  - {p['name']} ({p.get('email', 'no email')})")
        else:
            print("  No partners found (empty database)")
    except Exception as e:
        print(f"✗ Error listing partners: {e}")
        print("  This may be a permissions issue")
    
    # Test 3: Try to create a partner (may fail due to permissions)
    print("\n[TEST 3] Creating test partner...")
    try:
        partner_id = client.create_partner(
            name='Test Customer',
            email='test@example.com',
            phone='+1234567890'
        )
        
        if partner_id:
            print(f"✓ Created partner with ID: {partner_id}")
        else:
            print("✗ Failed to create partner")
            print("  Solution: Grant 'Contacts' permission to your user")
            print("  Steps:")
            print("    1. Settings → Users & Companies → Users")
            print("    2. Click your user")
            print("    3. Set Contacts: Officer")
            print("    4. Save")
    except Exception as e:
        print(f"✗ Error creating partner: {e}")
        if 'AccessDenied' in str(e):
            print("  Access Denied - Check user permissions!")
    
    # Test 4: List invoices
    print("\n[TEST 4] Checking invoices...")
    try:
        invoices = client.search_read(
            'account.move',
            [],
            fields=['id', 'name', 'partner_id', 'amount_total'],
            limit=5
        )
        
        if invoices:
            print(f"✓ Found {len(invoices)} invoices:")
            for inv in invoices:
                partner = inv.get('partner_id', ['Unknown'])[1] if inv.get('partner_id') else 'Unknown'
                print(f"  - {inv['name']}: ${inv.get('amount_total', 0)} ({partner})")
        else:
            print("  No invoices found")
    except Exception as e:
        print(f"✗ Error checking invoices: {e}")
        print("  Make sure Invoicing app is installed")
    
    # Test 5: Financial summary
    print("\n[TEST 5] Financial summary...")
    try:
        from datetime import datetime, timedelta
        
        today = datetime.now()
        last_month = today - timedelta(days=30)
        
        summary = client.get_financial_summary(
            start_date=last_month.strftime('%Y-%m-%d'),
            end_date=today.strftime('%Y-%m-%d')
        )
        
        print(f"✓ Last 30 days:")
        print(f"  Total Invoices: {summary.get('total_invoices', 0)}")
        print(f"  Total Revenue: ${summary.get('total_revenue', 0)}")
        print(f"  Total Paid: ${summary.get('total_paid', 0)}")
        print(f"  Outstanding: ${summary.get('outstanding', 0)}")
        
    except Exception as e:
        print(f"✗ Error getting summary: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    test_connection()
