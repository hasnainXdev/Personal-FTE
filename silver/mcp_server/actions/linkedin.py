"""LinkedIn actions for MCP Server."""

import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LinkedInAction:
    """Handle LinkedIn posting actions."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self.posts_today = 0
        self.max_posts_per_day = 3
        self.last_post_date = datetime.now().date()
    
    async def post_update(self, content: str, approval_file: Optional[str] = None) -> Dict[str, Any]:
        """Post an update to LinkedIn.
        
        Args:
            content: Post content
            approval_file: Path to approval file
            
        Returns:
            dict with post result
        """
        result = {
            'success': False,
            'message': '',
            'post_id': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check rate limit
        if not self._check_rate_limit():
            result['message'] = 'Daily post limit reached'
            return result
        
        try:
            # For Silver Tier, we log the intended action
            # In production, use Playwright to actually post
            self._log_post(content, approval_file)
            
            result['success'] = True
            result['message'] = 'LinkedIn post logged (mock mode)'
            result['post_id'] = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.posts_today += 1
            
            logger.info(f"LinkedIn post action: {content[:50]}...")
            
        except Exception as e:
            result['message'] = str(e)
            logger.error(f"Failed to post to LinkedIn: {e}")
        
        return result
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        today = datetime.now().date()
        
        if today != self.last_post_date:
            self.posts_today = 0
            self.last_post_date = today
        
        return self.posts_today < self.max_posts_per_day
    
    def _log_post(self, content: str, approval_file: Optional[str]):
        """Log the LinkedIn post action."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'linkedin_{today}.md'
        
        entry = f"""
## Post - {datetime.now().isoformat()}

**Status**: Logged (Mock)
**Approval File**: {approval_file or 'None'}
**Posts Today**: {self.posts_today + 1}/{self.max_posts_per_day}

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
    
    def create_post_draft(self, content: str, reason: str = "") -> Path:
        """Create a LinkedIn post draft for approval.
        
        Args:
            content: Post content
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
3. The MCP server will post automatically

## To Reject

1. Add rejection reason below
2. Move this file to `/Rejected/` folder

---

*Created by LinkedInAction*
*Silver Tier*
"""
        
        draft_path.write_text(content_md)
        logger.info(f"Created LinkedIn draft: {draft_path.name}")
        
        return draft_path
    
    def generate_business_post(self, topic: str) -> str:
        """Generate a business-focused LinkedIn post.
        
        Args:
            topic: Topic to post about
            
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
