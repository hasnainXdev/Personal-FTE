#!/usr/bin/env python3
"""
Gold Tier Validation Script

Validates that all Gold Tier requirements are met.
Run: python3 validate_gold_tier.py
"""

import sys
from pathlib import Path


def check_file(filepath: str, description: str) -> bool:
    """Check if a file exists"""
    path = Path(filepath)
    if path.exists():
        print(f"  ✓ {description}: {filepath}")
        return True
    else:
        print(f"  ✗ {description} MISSING: {filepath}")
        return False


def check_folder(folderpath: str, description: str) -> bool:
    """Check if a folder exists"""
    path = Path(folderpath)
    if path.exists() and path.is_dir():
        print(f"  ✓ {description}: {folderpath}")
        return True
    else:
        print(f"  ✗ {description} MISSING: {folderpath}")
        return False


def check_import(module: str, name: str) -> bool:
    """Check if a module can be imported"""
    try:
        __import__(module)
        print(f"  ✓ {name}: {module}")
        return True
    except ImportError as e:
        print(f"  ✗ {name} IMPORT ERROR: {module} - {e}")
        return False


def main():
    print("=" * 60)
    print("GOLD TIER VALIDATION")
    print("=" * 60)
    
    base = Path(__file__).parent
    vault = base / 'AI_Employee_Vault'
    src = base / 'src'
    
    all_passed = True
    
    # 1. Silver Requirements
    print("\n1. SILVER REQUIREMENTS")
    print("-" * 40)
    
    # Core files
    all_passed &= check_file(str(vault / 'Dashboard.md'), 'Dashboard')
    all_passed &= check_file(str(vault / 'Company_Handbook.md'), 'Company Handbook')
    all_passed &= check_file(str(vault / 'Business_Goals' / 'Company_Goals.md'), 'Business Goals')
    
    # Watchers
    all_passed &= check_import('watchers.filesystem_watcher', 'File System Watcher')
    all_passed &= check_import('watchers.gmail_watcher', 'Gmail Watcher')
    
    # Scheduler
    all_passed &= check_import('scheduler.scheduler', 'Scheduler')
    all_passed &= check_import('scheduler.tasks', 'Scheduled Tasks')
    
    # MCP
    all_passed &= check_import('mcp.tools', 'MCP Tools')
    
    # 2. Gold Additions
    print("\n2. GOLD ADDITIONS (Odoo + Facebook)")
    print("-" * 40)
    
    all_passed &= check_import('services.odoo_client', 'Odoo Client')
    all_passed &= check_file(str(src / 'services' / 'odoo_client.py'), 'Odoo Service File')
    
    # Check Facebook tool exists
    from mcp import tools
    if hasattr(tools, 'post_facebook'):
        print(f"  ✓ Facebook Integration: post_facebook() available")
    else:
        print(f"  ✗ Facebook Integration MISSING: post_facebook() not found")
        all_passed = False
    
    # Check Odoo tools exist
    if hasattr(tools, 'create_odoo_invoice') and hasattr(tools, 'record_odoo_payment'):
        print(f"  ✓ Odoo Integration: create_odoo_invoice(), record_odoo_payment() available")
    else:
        print(f"  ✗ Odoo Integration MISSING: Tools not found")
        all_passed = False
    
    # 3. Vault Structure
    print("\n3. VAULT STRUCTURE")
    print("-" * 40)
    
    required_folders = [
        ('Inbox', 'Inbox'),
        ('Needs_Action', 'Needs Action'),
        ('In_Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Pending_Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Plans', 'Plans'),
        ('Briefings', 'Briefings'),
        ('Logs', 'Logs'),
        ('Accounting', 'Accounting'),
        ('Invoices', 'Invoices'),
        ('Business_Goals', 'Business Goals'),
        ('Social_Media/LinkedIn', 'LinkedIn'),
        ('Social_Media/Facebook', 'Facebook'),
        ('Gmail', 'Gmail'),
        ('Odoo', 'Odoo'),
        ('Archive', 'Archive'),
    ]
    
    for folder, desc in required_folders:
        all_passed &= check_folder(str(vault / folder), desc)
    
    # 4. Skipped Features (should NOT exist)
    print("\n4. SKIPPED FEATURES (Should be absent)")
    print("-" * 40)
    
    skipped = [
        ('Social_Media/Instagram', 'Instagram'),
        ('Social_Media/Twitter', 'Twitter'),
        ('WhatsApp', 'WhatsApp'),
    ]
    
    for folder, desc in skipped:
        path = vault / folder
        if not path.exists():
            print(f"  ✓ {desc} correctly skipped")
        else:
            print(f"  ✗ {desc} should be removed")
            all_passed = False
    
    # 5. MCP Tools Count
    print("\n5. MCP TOOLS")
    print("-" * 40)
    
    expected_tools = [
        'send_email',
        'post_linkedin',
        'post_facebook',
        'create_approval_request',
        'check_approvals',
        'update_dashboard',
        'create_odoo_invoice',
        'record_odoo_payment',
    ]
    
    for tool in expected_tools:
        if hasattr(tools, tool):
            print(f"  ✓ {tool}()")
        else:
            print(f"  ✗ {tool}() MISSING")
            all_passed = False
    
    # 6. Configuration Files
    print("\n6. CONFIGURATION FILES")
    print("-" * 40)
    
    all_passed &= check_file(str(base / 'requirements.txt'), 'requirements.txt')
    all_passed &= check_file(str(base / 'pyproject.toml'), 'pyproject.toml')
    all_passed &= check_file(str(base / '.env.example'), '.env.example')
    all_passed &= check_file(str(base / '.gitignore'), '.gitignore')
    all_passed &= check_file(str(base / 'README.md'), 'README.md')
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ GOLD TIER VALIDATION PASSED")
        print("\nAll requirements met:")
        print("- Silver tier features (FileSystem, Gmail, LinkedIn, Scheduler)")
        print("- Gold additions (Odoo, Facebook)")
        print("- Vault structure complete")
        print("- Skipped features removed (Instagram, Twitter, WhatsApp)")
    else:
        print("✗ GOLD TIER VALIDATION FAILED")
        print("\nSome requirements not met. See errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    sys.exit(main())
