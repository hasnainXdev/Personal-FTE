#!/usr/bin/env python3
"""
Integration Tests for Gmail API + LinkedIn Playwright

Tests external API integrations with real credentials.
SAFE TO RUN - uses confirmation mode by default.

Usage:
    python test_integrations.py

Requirements:
    - Gmail OAuth setup OR SMTP credentials
    - LinkedIn credentials in .env
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


# Test colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text: str):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text: str):
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text: str):
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text: str):
    print(f"  {text}")


# ===========================================
# Test 1: Gmail OAuth Configuration
# ===========================================
def test_gmail_oauth_config():
    """Test Gmail OAuth configuration files exist."""
    print_header("TEST 1: Gmail OAuth Configuration")
    
    vault_path = Path("AI_Employee_Vault/Skills")
    credentials_file = vault_path / "gmail_credentials.json"
    token_file = vault_path / "gmail_token.json"
    
    # Check credentials file
    if credentials_file.exists():
        print_success(f"Credentials file exists: {credentials_file}")
        
        # Validate structure
        with open(credentials_file) as f:
            config = json.load(f)
        
        if "web" in config or "installed" in config:
            print_success("Credentials file has valid structure")
        else:
            print_error("Credentials file missing 'web' or 'installed' key")
            return False
    else:
        print_warning(f"Credentials file not found: {credentials_file}")
        print_info("Run: python -m ai_employee.services.gmail_oauth")
    
    # Check token file
    if token_file.exists():
        print_success(f"Token file exists: {token_file}")
        
        with open(token_file) as f:
            token = json.load(f)
        
        if "refresh_token" in token:
            print_success("Token has refresh_token (can be refreshed)")
        else:
            print_warning("Token missing refresh_token (may expire)")
    else:
        print_warning(f"Token file not found: {token_file}")
        print_info("OAuth flow will create this automatically")
    
    return True


# ===========================================
# Test 2: Gmail API Credentials Valid
# ===========================================
def test_gmail_api_credentials():
    """Test Gmail API credentials are valid and can be refreshed."""
    print_header("TEST 2: Gmail API Credentials")
    
    try:
        from ai_employee.services.gmail_oauth import get_gmail_credentials
        
        credentials = get_gmail_credentials()
        
        if credentials:
            print_success("Gmail API credentials loaded successfully")
            
            email = credentials.id_token.get("email", "Unknown") if credentials.id_token else "Unknown"
            print_info(f"Authorized for: {email}")
            
            if credentials.valid:
                print_success("Credentials are valid")
            elif credentials.refresh_token:
                print_warning("Credentials expired but can be refreshed")
                
                # Try to refresh
                from google.auth.transport.requests import Request
                try:
                    credentials.refresh(Request())
                    print_success("Credentials refreshed successfully")
                except Exception as e:
                    print_error(f"Failed to refresh: {e}")
                    return False
            else:
                print_error("Credentials invalid and cannot be refreshed")
                return False
            
            return True
        else:
            print_warning("Gmail API credentials not found")
            print_info("Run OAuth flow: python -m ai_employee.services.gmail_oauth")
            return False
            
    except ImportError as e:
        print_error(f"Import error: {e}")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


# ===========================================
# Test 3: SMTP Configuration
# ===========================================
def test_smtp_config():
    """Test SMTP configuration."""
    print_header("TEST 3: SMTP Configuration")
    
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if smtp_user and smtp_pass:
        print_success("SMTP credentials configured")
        print_info(f"SMTP User: {smtp_user}")
        print_info(f"SMTP Host: {os.getenv('SMTP_HOST', 'smtp.gmail.com')}")
        print_info(f"SMTP Port: {os.getenv('SMTP_PORT', '587')}")
        return True
    else:
        print_warning("SMTP credentials not configured")
        print_info("Add to .env:")
        print_info("  SMTP_USER=your.email@gmail.com")
        print_info("  SMTP_PASS=your-app-password")
        return False


# ===========================================
# Test 4: Email Sending Test
# ===========================================
async def test_email_sending():
    """Test sending email (with confirmation)."""
    print_header("TEST 4: Email Sending")
    
    # Check if either method is available
    has_gmail = False
    has_smtp = False
    
    try:
        from ai_employee.services.gmail_oauth import get_gmail_credentials
        has_gmail = get_gmail_credentials() is not None
    except:
        pass
    
    has_smtp = bool(os.getenv("SMTP_USER") and os.getenv("SMTP_PASS"))
    
    if not has_gmail and not has_smtp:
        print_warning("No email method configured (Gmail API or SMTP)")
        print_info("Configure at least one method to send emails")
        return False
    
    # Send test email
    test_email = os.getenv("TEST_EMAIL_ADDRESS", smtp_user if has_smtp else "test@example.com")
    
    print_info(f"Test will send to: {test_email}")
    print_warning("This is a REAL email - check your inbox")
    
    try:
        from ai_employee.mcp_server.actions.email import send_email
        
        result = await send_email(
            to=test_email,
            subject="AI Employee Test Email",
            body="This is a test email from the AI Employee integration test.\n\nIf you received this, the email system is working correctly!",
            html=False,
        )
        
        print_success(f"Email sent successfully!")
        print_info(f"Message ID: {result.get('message_id', 'N/A')}")
        print_info(f"Method: {result.get('method', 'N/A')}")
        print_info(f"Status: {result.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to send email: {e}")
        return False


# ===========================================
# Test 5: LinkedIn Configuration
# ===========================================
def test_linkedin_config():
    """Test LinkedIn configuration."""
    print_header("TEST 5: LinkedIn Configuration")
    
    vault_path = Path("AI_Employee_Vault/Skills")
    cookies_file = vault_path / "linkedin_cookies.json"
    
    # Check credentials
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_pass = os.getenv("LINKEDIN_PASSWORD")
    
    if linkedin_email and linkedin_pass:
        print_success("LinkedIn credentials configured")
        print_info(f"Email: {linkedin_email}")
    else:
        print_warning("LinkedIn credentials not configured")
        print_info("Add to .env:")
        print_info("  LINKEDIN_EMAIL=your@email.com")
        print_info("  LINKEDIN_PASSWORD=your-password")
        return False
    
    # Check saved session
    if cookies_file.exists():
        print_success(f"Saved session found: {cookies_file}")
        
        with open(cookies_file) as f:
            session = json.load(f)
        
        if "cookies" in session and len(session["cookies"]) > 0:
            print_success(f"Session has {len(session['cookies'])} cookies")
            
            # Check expiry
            saved_at = session.get("saved_at", "Unknown")
            print_info(f"Saved at: {saved_at}")
        else:
            print_warning("Session file exists but has no cookies")
    else:
        print_warning("No saved LinkedIn session")
        print_info("First run will create session cookies")
    
    # Check security settings
    require_confirmation = os.getenv("LINKEDIN_REQUIRE_CONFIRMATION", "true")
    if require_confirmation.lower() == "true":
        print_success("Confirmation mode enabled (SAFE)")
    else:
        print_warning("Confirmation mode DISABLED - posts will be automatic")
    
    return True


# ===========================================
# Test 6: Playwright Installation
# ===========================================
def test_playwright_installation():
    """Test Playwright is installed with browsers."""
    print_header("TEST 6: Playwright Installation")
    
    try:
        from playwright.async_api import async_playwright
        print_success("Playwright package installed")
        
        # Check if browsers are installed
        import subprocess
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True
        )
        
        if "is already installed" in result.stdout or result.returncode == 0:
            print_success("Chromium browser available")
        else:
            print_warning("Chromium browser may need installation")
            print_info("Run: uv run playwright install chromium")
        
        return True
        
    except ImportError:
        print_error("Playwright not installed")
        print_info("Run: uv add playwright")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


# ===========================================
# Test 7: LinkedIn Login Test
# ===========================================
async def test_linkedin_login():
    """Test LinkedIn login (saves session)."""
    print_header("TEST 7: LinkedIn Login")
    
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email or not password:
        print_warning("LinkedIn credentials not configured")
        return False
    
    try:
        from ai_employee.services.linkedin_playwright import LinkedInAutomation
        
        automation = LinkedInAutomation()
        
        print_info("Starting browser...")
        await automation.start(headless=False)
        
        try:
            print_info("Attempting login...")
            success = await automation.ensure_logged_in(email, password)
            
            if success:
                print_success("LinkedIn login successful!")
                
                # Check if session was saved
                cookies_file = Path("AI_Employee_Vault/Skills/linkedin_cookies.json")
                if cookies_file.exists():
                    print_success("Session cookies saved")
                else:
                    print_warning("Session cookies not saved")
                
                return True
            else:
                print_error("LinkedIn login failed")
                print_info("Check credentials and try again")
                return False
                
        finally:
            await automation.stop()
            
    except Exception as e:
        print_error(f"Login failed: {e}")
        print_info("Make sure Playwright browsers are installed")
        return False


# ===========================================
# Test 8: LinkedIn Post Draft
# ===========================================
async def test_linkedin_post_draft():
    """Test LinkedIn post creation (draft mode, no actual post)."""
    print_header("TEST 8: LinkedIn Post (Draft Mode)")
    
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email or not password:
        print_warning("LinkedIn credentials not configured")
        return False
    
    try:
        from ai_employee.services.linkedin_playwright import LinkedInAutomation
        
        automation = LinkedInAutomation()
        
        await automation.start(headless=False)
        
        try:
            # Login first
            logged_in = await automation.ensure_logged_in(email, password)
            if not logged_in:
                print_error("Not logged in")
                return False
            
            print_info("Testing post creation (draft mode)...")
            
            # This will create draft but not submit (confirmation mode)
            from ai_employee.services.linkedin_playwright import create_post
            
            result = await create_post(
                automation.page,
                content="Test post from AI Employee integration test",
                visibility="PUBLIC"
            )
            
            if result.get("status") == "draft_ready":
                print_success("Post draft created successfully")
                print_info(f"Status: {result.get('status')}")
                print_info(f"Requires confirmation: {result.get('requires_confirmation')}")
                return True
            elif result.get("status") == "posted":
                print_warning("Post was actually submitted (confirmation mode disabled)")
                return True
            else:
                print_error(f"Unexpected result: {result}")
                return False
                
        finally:
            await automation.stop()
            
    except Exception as e:
        print_error(f"Test failed: {e}")
        return False


# ===========================================
# Main Test Runner
# ===========================================
async def run_async_tests():
    """Run all async tests."""
    results = []
    
    # Test 4: Email sending (optional)
    print("\n" + "="*60)
    response = input("Run email sending test? (y/n): ").strip().lower()
    if response == 'y':
        results.append(("Email Sending", await test_email_sending()))
    else:
        print_info("Skipping email sending test")
    
    # Test 7: LinkedIn login (optional)
    print("\n" + "="*60)
    response = input("Run LinkedIn login test? (y/n): ").strip().lower()
    if response == 'y':
        results.append(("LinkedIn Login", await test_linkedin_login()))
    else:
        print_info("Skipping LinkedIn login test")
    
    # Test 8: LinkedIn post draft (optional)
    print("\n" + "="*60)
    response = input("Run LinkedIn post draft test? (y/n): ").strip().lower()
    if response == 'y':
        results.append(("LinkedIn Post Draft", await test_linkedin_post_draft()))
    else:
        print_info("Skipping LinkedIn post draft test")
    
    return results


def main():
    """Run all integration tests."""
    print_header("AI EMPLOYEE INTEGRATION TESTS")
    print_info("Testing Gmail API + LinkedIn Playwright integrations")
    print_info("Note: External API tests require real credentials")
    print_info("="*60)
    
    results = []
    
    # Configuration tests (always run)
    results.append(("Gmail OAuth Config", test_gmail_oauth_config()))
    results.append(("Gmail API Credentials", test_gmail_api_credentials()))
    results.append(("SMTP Config", test_smtp_config()))
    results.append(("LinkedIn Config", test_linkedin_config()))
    results.append(("Playwright Installation", test_playwright_installation()))
    
    # Interactive tests (user chooses)
    print("\n" + "="*60)
    print_info("The following tests make external API calls")
    print_info("They are optional but recommended for verification")
    
    async_results = asyncio.run(run_async_tests())
    results.extend(async_results)
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for name, result in results:
        if result is True:
            print_success(f"{name}")
        elif result is False:
            print_error(f"{name}")
        else:
            print_warning(f"{name} (skipped)")
    
    print("\n" + "="*60)
    print_info(f"Passed: {passed}/{len(results)}")
    print_info(f"Failed: {failed}/{len(results)}")
    print_info(f"Skipped: {skipped}/{len(results)}")
    
    if failed == 0:
        print_success("\nAll tests passed! System ready for use.")
        return 0
    else:
        print_error(f"\n{failed} test(s) failed. Review configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
