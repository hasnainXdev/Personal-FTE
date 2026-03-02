#!/usr/bin/env python3
"""Simple LinkedIn login using your default browser."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from playwright.async_api import async_playwright


async def login_linkedin_simple():
    """Login to LinkedIn using your default browser."""
    print("🔗 LinkedIn Simple Login")
    print("=" * 60)
    print()
    print("This will open LinkedIn in your DEFAULT BROWSER.")
    print()
    print("Steps:")
    print("  1. A browser window will open")
    print("  2. Log in to LinkedIn manually")
    print("  3. Complete any OTP/security checks")
    print("  4. Wait until you see your feed")
    print("  5. Press ENTER in this terminal when logged in")
    print()
    print("⏱️  Timeout: 5 minutes")
    print()
    
    vault_path = os.getenv('VAULT_PATH', 'AI_Employee_Vault')
    session_path = os.path.join(vault_path, '.linkedin_session')
    
    async with async_playwright() as p:
        # Launch browser - will use system browser if available
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        # Create context
        context = await browser.new_context(
            user_data_dir=session_path,
            viewport={'width': 1920, 'height': 1080},
        )
        
        page = await context.new_page()
        
        # Add anti-detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("Opening LinkedIn...")
        await page.goto('https://www.linkedin.com/login')
        
        print()
        print("✓ Browser opened")
        print("  → Log in now...")
        print()
        
        # Wait for user to press enter
        input("Press ENTER when you're logged in and see your feed...")
        
        # Check if logged in
        current_url = page.url
        if '/feed' in current_url or '/mynetwork' in current_url:
            print()
            print("✓ Login successful!")
            print(f"  Session saved to: {session_path}")
            print()
            print("Next time you run, the session will be reused.")
        else:
            print()
            print("⚠ May not be logged in yet")
            print(f"  Current URL: {current_url}")
            print("  Run again to retry")
        
        await context.close()
        await browser.close()
    
    print()
    print("=" * 60)
    print("Done!")
    print()
    print("Next steps:")
    print("  1. Run: python3 test_linkedin.py")
    print("  2. Or start MCP server: python3 mcp_server/server.py ./AI_Employee_Vault")
    print()


if __name__ == "__main__":
    asyncio.run(login_linkedin_simple())
