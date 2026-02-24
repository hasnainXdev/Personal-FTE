"""
LinkedIn Automation via Playwright

Secure browser automation for LinkedIn actions with anti-detection measures.
IMPORTANT: Use responsibly to avoid account restrictions.

Security Features:
- Rate limiting with random delays
- Session persistence (avoid repeated logins)
- Human-like behavior simulation
- Manual confirmation mode
- Detection awareness
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

# Vault paths
VAULT_ROOT = Path(os.getenv("VAULT_ROOT", "AI_Employee_Vault"))
SESSION_PATH = VAULT_ROOT / "Skills" / "linkedin_session.json"
COOKIES_PATH = VAULT_ROOT / "Skills" / "linkedin_cookies.json"

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "min_delay_between_actions": 30,  # seconds
    "max_delay_between_actions": 120,  # seconds
    "max_actions_per_hour": 20,
    "min_delay_after_login": 5,  # seconds
    "max_delay_after_login": 15,  # seconds
}

# LinkedIn URLs
LINKEDIN_URL = "https://www.linkedin.com"
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed"


class LinkedInSecurityError(Exception):
    """Raised when LinkedIn security measures are detected."""
    pass


class LinkedInRateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


def ensure_vault_structure():
    """Ensure vault directories exist."""
    COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)


def save_session_state(email: str, cookies: list):
    """Save session cookies securely."""
    ensure_vault_structure()
    session_data = {
        "email": email,
        "cookies": cookies,
        "saved_at": datetime.utcnow().isoformat(),
    }
    with open(COOKIES_PATH, "w") as f:
        json.dump(session_data, f, indent=2)
    try:
        os.chmod(COOKIES_PATH, 0o600)
        logger.info(f"Session saved: {COOKIES_PATH}")
    except Exception as e:
        logger.warning(f"Could not restrict permissions: {e}")


def load_session_state() -> dict | None:
    """Load saved session cookies."""
    if not COOKIES_PATH.exists():
        return None
    
    try:
        with open(COOKIES_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load session: {e}")
        return None


def random_delay(min_seconds: float, max_seconds: float):
    """Add random delay to simulate human behavior."""
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Waiting {delay:.1f}s (human-like delay)")
    time.sleep(delay)


async def random_delay_async(min_seconds: float, max_seconds: float):
    """Add random async delay to simulate human behavior."""
    delay = random.uniform(min_seconds, max_seconds)
    logger.debug(f"Waiting {delay:.1f}s (human-like delay)")
    await asyncio.sleep(delay)


async def simulate_human_behavior(page: Page):
    """Simulate human-like mouse movements and scrolling."""
    try:
        # Random small mouse movements
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Random scroll
        scroll_amount = random.randint(100, 500)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        logger.debug("Human behavior simulated")
    except Exception as e:
        logger.debug(f"Behavior simulation skipped: {e}")


async def check_for_detection(page: Page) -> bool:
    """
    Check if LinkedIn has detected automation.
    
    Returns:
        True if detection suspected
    """
    try:
        # Check for common detection indicators
        page_text = await page.content()
        
        detection_indicators = [
            "suspicious activity",
            "unusual traffic",
            "verify you are human",
            "captcha",
            "security check",
        ]
        
        for indicator in detection_indicators:
            if indicator.lower() in page_text.lower():
                logger.warning(f"Detection indicator found: {indicator}")
                return True
        
        # Check for CAPTCHA elements
        captcha_selectors = [
            'iframe[src*="captcha"]',
            '[data-testid="challenge"]',
            '.captcha',
        ]
        
        for selector in captcha_selectors:
            if await page.query_selector(selector):
                logger.warning(f"CAPTCHA detected: {selector}")
                return True
        
        return False
    except Exception as e:
        logger.debug(f"Detection check error: {e}")
        return False


async def login_linkedin(
    page: Page,
    email: str,
    password: str,
) -> bool:
    """
    Login to LinkedIn with human-like behavior.
    
    Returns:
        True if login successful
    """
    logger.info("Navigating to LinkedIn login...")
    
    await page.goto(LINKEDIN_LOGIN_URL, wait_until="networkidle")
    await simulate_human_behavior(page)
    
    # Check if already logged in
    if LINKEDIN_FEED_URL in page.url:
        logger.info("Already logged in to LinkedIn")
        return True
    
    try:
        # Find and fill login form
        await page.fill('input[id="username"]', email)
        await simulate_human_behavior(page)
        await random_delay_async(1, 3)
        
        await page.fill('input[id="password"]', password)
        await simulate_human_behavior(page)
        await random_delay_async(1, 2)
        
        # Click sign in
        await page.click('button[type="submit"]')
        logger.info("Login submitted")
        
        # Wait for navigation
        await page.wait_for_load_state("networkidle")
        await random_delay_async(RATE_LIMIT_CONFIG["min_delay_after_login"], 
                                  RATE_LIMIT_CONFIG["max_delay_after_login"])
        
        # Check if login successful
        if LINKEDIN_FEED_URL in page.url or "feed" in page.url:
            logger.info("Login successful")
            return True
        else:
            # Check for error messages
            error_selectors = ['.alert', '[data-test-error]', '.error']
            for selector in error_selectors:
                if await page.query_selector(selector):
                    error_text = await page.text_content(selector)
                    logger.error(f"Login error: {error_text}")
                    return False
            
            logger.warning("Login may have failed - unexpected URL")
            return False
            
    except PlaywrightTimeout:
        logger.error("Login timeout - page may have changed")
        return False
    except Exception as e:
        logger.error(f"Login error: {e}")
        return False


async def create_post(
    page: Page,
    content: str,
    visibility: Literal["PUBLIC", "CONNECTIONS", "GROUP"] = "PUBLIC",
) -> dict:
    """
    Create a LinkedIn post.
    
    Args:
        page: Playwright page
        content: Post content
        visibility: Post visibility
        
    Returns:
        dict with post info
    """
    logger.info("Creating LinkedIn post...")
    
    # Navigate to feed
    await page.goto(LINKEDIN_FEED_URL, wait_until="networkidle")
    await simulate_human_behavior(page)
    await random_delay_async(2, 4)
    
    try:
        # Find the post creation textarea
        post_box = await page.wait_for_selector(
            'div[role="textbox"][aria-label="Share what you think"]',
            timeout=10000
        )
        
        if not post_box:
            # Try alternative selector
            post_box = await page.query_selector('textarea[aria-label="Share what you think"]')
        
        if not post_box:
            raise LinkedInSecurityError("Post creation box not found - may be blocked")
        
        # Click to focus
        await post_box.click()
        await random_delay_async(1, 2)
        
        # Type content (simulate typing)
        await post_box.fill(content)
        await random_delay_async(2, 4)
        await simulate_human_behavior(page)
        
        # Set visibility if needed
        if visibility != "PUBLIC":
            visibility_button = await page.query_selector('button[aria-label*="visibility"]')
            if visibility_button:
                await visibility_button.click()
                await random_delay_async(1, 2)
                # Select appropriate visibility option
                # (implementation depends on LinkedIn's current UI)
        
        # Check for "Post" button and click
        post_button = await page.query_selector('button:has-text("Post")')
        if not post_button:
            post_button = await page.query_selector('button:has-text("Share")')
        
        if not post_button:
            raise LinkedInSecurityError("Post button not found")
        
        # Confirm before posting (safety feature)
        if os.getenv("LINKEDIN_REQUIRE_CONFIRMATION", "true").lower() == "true":
            logger.warning("CONFIRMATION MODE: Post ready but not submitted")
            logger.warning(f"Content preview: {content[:100]}...")
            logger.warning("To auto-post, set LINKEDIN_REQUIRE_CONFIRMATION=false in .env")
            return {
                "status": "draft_ready",
                "content": content,
                "visibility": visibility,
                "requires_confirmation": True,
                "message": "Post drafted. Manual confirmation required."
            }
        
        await post_button.click()
        await random_delay_async(2, 4)
        
        logger.info("Post submitted successfully")
        
        return {
            "status": "posted",
            "content": content,
            "visibility": visibility,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_confirmation": False,
        }
        
    except PlaywrightTimeout:
        logger.error("Timeout creating post")
        raise LinkedInSecurityError("Post creation timed out - may be blocked")
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise


async def connect_with_profile(
    page: Page,
    profile_url: str,
    message: str | None = None,
) -> dict:
    """
    Send connection request to a LinkedIn profile.
    
    Args:
        page: Playwright page
        profile_url: URL of the profile
        message: Optional connection message
        
    Returns:
        dict with result
    """
    logger.info(f"Connecting with profile: {profile_url}")
    
    await page.goto(profile_url, wait_until="networkidle")
    await simulate_human_behavior(page)
    await random_delay_async(2, 4)
    
    try:
        # Find "Connect" button
        connect_button = await page.query_selector('button:has-text("Connect")')
        
        if not connect_button:
            # Already connected?
            if await page.query_selector('button:has-text("Message")'):
                logger.info("Already connected to this profile")
                return {"status": "already_connected", "profile_url": profile_url}
            
            raise LinkedInSecurityError("Connect button not found")
        
        await connect_button.click()
        await random_delay_async(1, 2)
        
        # If message option available
        if message:
            add_note = await page.query_selector('button:has-text("Add a note")')
            if add_note:
                await add_note.click()
                await random_delay_async(1, 2)
                
                # Fill message
                message_box = await page.query_selector('textarea[aria-label*="message"]')
                if message_box:
                    await message_box.fill(message)
                    await random_delay_async(1, 2)
        
        # Send request
        send_button = await page.query_selector('button:has-text("Send")')
        if send_button:
            if os.getenv("LINKEDIN_REQUIRE_CONFIRMATION", "true").lower() == "true":
                logger.warning("CONFIRMATION MODE: Connection request ready but not sent")
                return {
                    "status": "ready",
                    "profile_url": profile_url,
                    "requires_confirmation": True,
                }
            
            await send_button.click()
            await random_delay_async(1, 2)
            
            logger.info("Connection request sent")
            return {
                "status": "sent",
                "profile_url": profile_url,
                "timestamp": datetime.utcnow().isoformat(),
            }
        
        return {"status": "unknown", "profile_url": profile_url}
        
    except Exception as e:
        logger.error(f"Error connecting: {e}")
        raise


class LinkedInAutomation:
    """Main LinkedIn automation manager."""
    
    def __init__(self):
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self._action_count = 0
        self._hour_start = time.time()
    
    async def start(self, headless: bool = False):
        """Start browser session."""
        logger.info("Starting LinkedIn automation session...")
        
        playwright = await async_playwright().start()
        
        # Browser args for stealth
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=args
        )
        
        # Context with anti-detection
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        # Add init script to hide automation
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        self.page = await self.context.new_page()
        logger.info("Browser session started")
    
    async def stop(self):
        """Stop browser session and save state."""
        if self.context:
            # Save cookies
            cookies = await self.context.cookies()
            if self.page:
                try:
                    # Try to get logged-in user
                    await self.page.goto(LINKEDIN_URL, wait_until="networkidle", timeout=5000)
                    # Email would be extracted from profile
                except:
                    pass
            
            save_session_state("unknown", cookies)
            logger.info("Session cookies saved")
        
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
    
    async def ensure_logged_in(self, email: str, password: str) -> bool:
        """Ensure logged in, using saved session if available."""
        if not self.page:
            raise RuntimeError("Browser not started")
        
        # Try to load saved session
        session = load_session_state()
        if session and session.get("cookies"):
            logger.info("Loading saved session...")
            await self.context.add_cookies(session["cookies"])
            await self.page.goto(LINKEDIN_URL, wait_until="networkidle")
            
            # Check if still logged in
            if "feed" in self.page.url:
                logger.info("Session restored successfully")
                return True
            
            logger.info("Saved session expired, re-logging in")
        
        # Login
        success = await login_linkedin(self.page, email, password)
        
        if success:
            # Save new session
            cookies = await self.context.cookies()
            save_session_state(email, cookies)
        
        return success
    
    def _check_rate_limit(self):
        """Check and enforce rate limits."""
        current_time = time.time()
        
        # Reset hourly counter
        if current_time - self._hour_start > 3600:
            self._action_count = 0
            self._hour_start = current_time
            logger.info("Hourly rate limit reset")
        
        # Check hourly limit
        if self._action_count >= RATE_LIMIT_CONFIG["max_actions_per_hour"]:
            raise LinkedInRateLimitError(
                f"Hourly rate limit reached ({RATE_LIMIT_CONFIG['max_actions_per_hour']} actions/hour)"
            )
        
        # Random delay between actions
        if self._action_count > 0:
            delay = random.uniform(
                RATE_LIMIT_CONFIG["min_delay_between_actions"],
                RATE_LIMIT_CONFIG["max_delay_between_actions"]
            )
            logger.info(f"Rate limit delay: {delay:.1f}s")
            time.sleep(delay)
        
        self._action_count += 1
    
    async def post_content(
        self,
        content: str,
        email: str,
        password: str,
        visibility: str = "PUBLIC",
        headless: bool = False,
    ) -> dict:
        """
        Post content to LinkedIn (full workflow).
        
        Args:
            content: Post content
            email: LinkedIn email
            password: LinkedIn password
            visibility: Post visibility
            headless: Run browser headless
            
        Returns:
            dict with post result
        """
        self._check_rate_limit()
        
        await self.start(headless=headless)
        
        try:
            # Ensure logged in
            logged_in = await self.ensure_logged_in(email, password)
            if not logged_in:
                raise LinkedInSecurityError("Login failed")
            
            # Check for detection
            if await check_for_detection(self.page):
                raise LinkedInSecurityError(
                    "LinkedIn automation detected! Stop immediately and review account."
                )
            
            # Create post
            result = await create_post(self.page, content, visibility)
            
            return result
            
        finally:
            await self.stop()


async def post_to_linkedin(
    content: str,
    visibility: str = "PUBLIC",
    require_confirmation: bool = True,
) -> dict:
    """
    Convenience function to post to LinkedIn.
    
    Args:
        content: Post content
        visibility: Post visibility
        require_confirmation: Require manual confirmation
        
    Returns:
        dict with post result
    """
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email or not password:
        raise ValueError("LinkedIn credentials not configured. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
    
    automation = LinkedInAutomation()
    
    try:
        result = await automation.post_content(
            content=content,
            email=email,
            password=password,
            visibility=visibility,
            headless=not require_confirmation,  # Show browser if confirmation needed
        )
        return result
    except Exception as e:
        logger.error(f"LinkedIn posting failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test connection
    async def test():
        automation = LinkedInAutomation()
        await automation.start(headless=False)
        
        try:
            email = os.getenv("LINKEDIN_EMAIL")
            password = os.getenv("LINKEDIN_PASSWORD")
            
            if not email or not password:
                print("Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")
                return
            
            success = await automation.ensure_logged_in(email, password)
            print(f"Login: {'Success' if success else 'Failed'}")
            
        finally:
            await automation.stop()
    
    asyncio.run(test())
