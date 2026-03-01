#!/usr/bin/env python3
"""Test script for LinkedIn service with improved authentication."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from services.linkedin_service import LinkedInService


async def test_linkedin():
    """Test LinkedIn service."""
    print("🔗 LinkedIn Service Test")
    print("=" * 60)
    print()
    
    # Get vault path
    vault_path = os.getenv('VAULT_PATH', 'AI_Employee_Vault')
    
    print(f"Vault: {vault_path}")
    print(f"Session: {vault_path}/.linkedin_session/")
    print()
    
    # Create service
    service = LinkedInService(vault_path)
    
    print("Step 1: Initialize browser...")
    try:
        await service.initialize()
        print("  ✓ Browser initialized with anti-detection")
    except Exception as e:
        print(f"  ✗ Browser init failed: {e}")
        print("  Try: playwright install chromium")
        return False
    
    print()
    print("Step 2: Check existing session...")
    logged_in = await service.is_logged_in()
    
    if logged_in:
        print("  ✓ Already logged in!")
        print()
        print("Step 3: Test post (draft mode)...")
        
        # Create a test draft
        draft_path = service.create_draft_post(
            "Test post from AI Employee Silver Tier",
            "Testing LinkedIn integration"
        )
        print(f"  ✓ Draft created: {draft_path.name}")
        print()
        print("To post: Move draft to /Approved/ folder")
        
    else:
        print("  ⚠ Not logged in")
        print()
        print("Step 3: Opening LinkedIn login...")
        print("=" * 60)
        print()
        print("📝 MANUAL LOGIN REQUIRED")
        print()
        print("A browser window will open. Please:")
        print("  1. Log in to LinkedIn manually")
        print("  2. Complete any OTP/security challenges")
        print("  3. Wait until you see your feed")
        print()
        print("⏱️  Timeout: 5 minutes (300 seconds)")
        print()
        print("💡 TIPS:")
        print("  - Use saved password for faster login")
        print("  - If page refreshes, keep typing - don't stop")
        print("  - OTP codes expire fast - be ready!")
        print("  - Session saves after successful login")
        print()
        print("=" * 60)
        print()
        
        # Open login with extended timeout
        await service.login(timeout_seconds=300)
        
        # Verify final state
        logged_in = await service.is_logged_in()
        if logged_in:
            print()
            print("  ✓ Login successful! Session saved.")
            print()
            print("  Next time you run, you'll be auto-logged in.")
        else:
            print()
            print("  ⚠ Login not completed")
            print("  Run this script again to retry")
    
    print()
    print("Step 4: Close browser...")
    await service.close()
    print("  ✓ Browser closed")
    
    print()
    print("=" * 60)
    print("Test complete!")
    print()
    print("Next steps:")
    if logged_in:
        print("  ✓ You're logged in!")
        print("  1. Start MCP server: python3 mcp_server/server.py ./AI_Employee_Vault")
        print("  2. Use post_linkedin tool to create drafts")
        print("  3. Approve drafts to post automatically")
    else:
        print("  ⚠ Please run again and complete login")
        print("  Command: python3 test_linkedin.py")
    print()
    
    return logged_in


if __name__ == "__main__":
    result = asyncio.run(test_linkedin())
    sys.exit(0 if result else 1)
