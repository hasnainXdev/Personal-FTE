"""LinkedIn Service - Real posting using Playwright."""

import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class LinkedInService:
    """Service for posting to LinkedIn using Playwright browser automation.
    
    This service:
    1. Uses Playwright for browser automation
    2. Maintains persistent browser session
    3. Posts updates to LinkedIn
    4. Logs all activities
    
    Authentication:
    - First run: Browser opens for manual LinkedIn login
    - Subsequent runs: Uses saved session cookies
    """
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    FEED_URL = 'https://www.linkedin.com/feed/'
    
    def __init__(self, vault_path: str, session_path: Optional[str] = None):
        """Initialize the LinkedIn service.
        
        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session (optional)
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else self.vault_path / '.linkedin_session'
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Ensure session directory exists
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser = None
        self.context = None
        self.page = None
        
        # Track posts for rate limiting
        self.posts_today = 0
        self.last_post_time = None
        self.max_posts_per_day = 3
        
        # Load post count from logs
        self._load_post_count()
    
    def _load_post_count(self):
        """Load today's post count from logs."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'linkedin_{today}.md'
        
        if log_file.exists():
            content = log_file.read_text()
            # Count successful posts today
            self.posts_today = content.count('**Status**: Success')
    
    async def initialize(self):
        """Initialize the browser session."""
        try:
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            
            # Launch browser with persistent context and anti-detection
            self.context = await playwright.chromium.launch_persistent_context(
                self.session_path,  # user_data_dir as first positional argument
                headless=False,  # Show browser for manual login
                channel='chromium',  # Use chromium channel
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-extensions',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--no-first-run',
                ],
                ignore_default_args=['--enable-automation'],
            )
            
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            
            # Set realistic user agent and headers
            await self.page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            })
            
            # Bypass automation detection
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            self.logger.info("Browser initialized with anti-detection")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def is_logged_in(self) -> bool:
        """Check if logged into LinkedIn."""
        if not self.page:
            return False
        
        try:
            # Navigate to feed
            await self.page.goto(self.FEED_URL, wait_until='networkidle', timeout=30000)
            await self.page.wait_for_timeout(5000)
            
            # Check for feed element (only visible when logged in)
            feed_selector = '[data-testid="feed"]'
            try:
                await self.page.wait_for_selector(feed_selector, timeout=5000)
                self.logger.info("LinkedIn session valid - logged in")
                return True
            except:
                # Check if on login page
                current_url = self.page.url
                if 'login' in current_url or 'checkpoint' in current_url:
                    self.logger.info("LinkedIn session expired - need login")
                    return False
                
                # Try to find nav element as fallback
                try:
                    await self.page.wait_for_selector('nav', timeout=3000)
                    self.logger.info("LinkedIn appears logged in (nav found)")
                    return True
                except:
                    self.logger.info("LinkedIn not logged in")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            return False
    
    async def login(self, timeout_seconds: int = 300):
        """Navigate to LinkedIn login and wait for manual login.
        
        Args:
            timeout_seconds: How long to wait for manual login (default: 300s = 5 minutes)
        """
        if not self.page:
            await self.initialize()
        
        self.logger.info("Navigate to LinkedIn login page")
        self.logger.info(f"Manual login timeout: {timeout_seconds} seconds ({timeout_seconds//60} minutes)")
        self.logger.info("TIP: Use a real browser profile - LinkedIn may require OTP")
        self.logger.info("TIP: If page refreshes, try typing faster or use saved password")
        
        await self.page.goto(self.LINKEDIN_URL, wait_until='networkidle')
        
        # Wait for user to log in
        self.logger.info("Waiting for login...")
        
        # Check every 3 seconds until logged in or timeout
        checks = timeout_seconds // 3
        for i in range(checks):
            try:
                await self.page.wait_for_timeout(3000)
                
                # Check if we're on feed page (logged in)
                current_url = self.page.url
                if '/feed' in current_url or '/mynetwork' in current_url or '/messaging' in current_url:
                    self.logger.info("✓ Login successful! Detected LinkedIn homepage")
                    
                    # Verify by checking for feed element
                    try:
                        await self.page.wait_for_selector('[data-testid="feed"]', timeout=3000)
                        self.logger.info("✓ LinkedIn session valid")
                        return True
                    except:
                        # Might be on homepage but feed not loaded yet
                        self.logger.info("✓ On LinkedIn, waiting for feed to load...")
                        await self.page.wait_for_timeout(5000)
                        return True
                
                # Check if on checkpoint/challenge page (OTP)
                if '/checkpoint' in current_url or '/challenge' in current_url:
                    self.logger.info("⚠ Security checkpoint detected - complete the challenge")
                    self.logger.info("  This page may refresh - just complete the OTP/captcha")
                    continue
                
                # Check if still on login page
                if '/login' in current_url or '/uas/login' in current_url:
                    if i % 10 == 0:  # Show reminder every 30 seconds
                        remaining = (checks - i) * 3
                        self.logger.info(f"  Still waiting... {remaining}s remaining")
                    continue
                    
            except Exception as e:
                self.logger.debug(f"Check error (normal): {e}")
                continue
        
        self.logger.warning("Login timeout - please run again if not logged in")
        return False
    
    async def post_update(self, content: str) -> Dict[str, Any]:
        """Post an update to LinkedIn.
        
        Args:
            content: The post content
            
        Returns:
            dict with status and details
        """
        result = {
            'success': False,
            'error': None,
            'post_id': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check rate limits
        if self.posts_today >= self.max_posts_per_day:
            result['error'] = f'Daily post limit reached ({self.max_posts_per_day}/day)'
            return result
        
        try:
            if not self.page:
                await self.initialize()
            
            if not await self.is_logged_in():
                result['error'] = 'Not logged into LinkedIn. Run login first.'
                return result
            
            # Navigate to feed
            self.logger.info("Navigating to LinkedIn feed")
            await self.page.goto(self.FEED_URL, wait_until='networkidle')
            await self.page.wait_for_timeout(3000)
            
            # Find and click the post creation box
            self.logger.info("Looking for post creation box")
            
            # Try different selectors for post creation
            post_start_selectors = [
                '[data-testid="update-editor-start"]',
                '.share-box-feed-entry__trigger',
                'button:has-text("Start a post")',
                'button:has-text("Begin a post")'
            ]
            
            post_started = False
            for selector in post_start_selectors:
                try:
                    start_post = await self.page.query_selector(selector)
                    if start_post:
                        await start_post.click()
                        post_started = True
                        self.logger.info(f"Clicked post creation: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not post_started:
                result['error'] = 'Could not find post creation button'
                return result
            
            # Wait for editor to open
            await self.page.wait_for_timeout(2000)
            
            # Find the textarea and type content
            self.logger.info("Entering post content")
            
            editor_selectors = [
                '[data-testid="update-editor-textarea"]',
                '.ProseMirror',
                'div[contenteditable="true"]'
            ]
            
            for selector in editor_selectors:
                try:
                    textarea = await self.page.query_selector(selector)
                    if textarea:
                        # Clear existing content
                        await textarea.click()
                        await self.page.keyboard.press('Control+A')
                        await self.page.keyboard.press('Delete')
                        
                        # Type new content (slower for reliability)
                        await textarea.type(content, delay=50)
                        self.logger.info("Content entered successfully")
                        break
                except Exception as e:
                    continue
            
            # Wait for content to register
            await self.page.wait_for_timeout(2000)
            
            # Click the post button
            self.logger.info("Looking for Post button")
            
            post_button_selectors = [
                'button:has-text("Post")',
                'button:has-text("Share")'
            ]
            
            for selector in post_button_selectors:
                try:
                    post_button = await self.page.query_selector(selector)
                    if post_button:
                        await post_button.click()
                        self.logger.info(f"Clicked post button: {selector}")
                        
                        # Wait for confirmation
                        await self.page.wait_for_timeout(5000)
                        
                        result['success'] = True
                        result['post_id'] = datetime.now().strftime('%Y%m%d_%H%M%S')
                        self.posts_today += 1
                        self.last_post_time = datetime.now()
                        
                        self.logger.info(f"LinkedIn post successful: {result['post_id']}")
                        
                        # Log the post
                        self._log_post(content, result)
                        return result
                except Exception as e:
                    continue
            
            result['error'] = 'Could not find Post button'
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Failed to post to LinkedIn: {e}")
        
        return result
    
    def _log_post(self, content: str, result: dict):
        """Log the post to the logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'linkedin_{today}.md'
        
        entry = f"""
## Post - {result['timestamp']}

**Status**: {'Success' if result['success'] else 'Failed'}
**Post ID**: {result.get('post_id', 'N/A')}
**Error**: {result.get('error', 'None')}
**Posts Today**: {self.posts_today}/{self.max_posts_per_day}

**Content**:
{content[:300]}{'...' if len(content) > 300 else ''}

---
"""
        
        if log_file.exists():
            content_existing = log_file.read_text()
            log_file.write_text(content_existing + entry)
        else:
            log_file.write_text(f"""---
type: linkedin_log
date: {today}
---

# LinkedIn Posts - {today}
{entry}
""")
    
    async def close(self):
        """Close the browser session."""
        if self.context:
            await self.context.close()
            self.logger.info("Browser session closed")
    
    def create_draft_post(self, content: str, reason: str = "") -> Path:
        """Create a draft post file for approval.
        
        Args:
            content: The post content
            reason: Reason for the post
            
        Returns:
            Path to the draft file
        """
        file_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_path = self.vault_path / 'Pending_Approval' / f'LINKEDIN_POST_{file_id}.md'
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        
        content_md = f"""---
type: linkedin_post_draft
file_id: {file_id}
created: {datetime.now().isoformat()}
status: pending_approval
posts_today: {self.posts_today}
max_posts: {self.max_posts_per_day}
---

# LinkedIn Post Draft

## Post Content

{content}

## Reason
{reason}

## Posting Guidelines

- Maximum 3 posts per day
- Business content only
- Professional tone
- No controversial topics

## To Approve

1. Review the content above
2. Move this file to `/Approved/` folder
3. The LinkedIn service will post automatically

## To Reject

1. Add rejection reason below
2. Move this file to `/Rejected/` folder

---

*Created by LinkedInService*
*Silver Tier - Real Playwright Automation*
"""
        
        draft_path.write_text(content_md)
        self.logger.info(f"Created LinkedIn draft: {draft_path.name}")
        
        return draft_path
    
    def generate_business_post(self, topic: str) -> str:
        """Generate a business-focused LinkedIn post.
        
        Args:
            topic: The topic to post about
            
        Returns:
            Generated post content
        """
        templates = [
            f"""🚀 Exciting update!

{topic}

We're committed to delivering excellence and innovation to our clients.

#Business #Innovation #Growth""",
            
            f"""💡 Industry Insight

{topic}

This is transforming how we approach our work and serve our customers.

#Industry #Insights #Professional""",
            
            f"""📈 Business Update

{topic}

Proud of what we're building and the value we're creating.

#Business #Progress #Success""",
        ]
        
        import random
        return random.choice(templates)
