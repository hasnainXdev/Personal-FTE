"""
LinkedIn Action Handler - Post to LinkedIn

Handles LinkedIn content publishing through MCP server.
Note: Requires LinkedIn API access token.
"""

import logging
import os
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

# LinkedIn API endpoints
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"


async def post_linkedin(
    content: str,
    visibility: str = "PUBLIC",
    draft_url: str | None = None,
) -> dict:
    """
    Post content to LinkedIn.
    
    Args:
        content: The post text content
        visibility: Post visibility (PUBLIC, CONNECTIONS, etc.)
        draft_url: Reference to draft in vault (optional)
    
    Returns:
        dict with post_url and status
    """
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    organization_id = os.getenv("LINKEDIN_ORGANIZATION_ID")
    
    if not access_token:
        raise ValueError("LinkedIn access token not configured. Set LINKEDIN_ACCESS_TOKEN in .env")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # Determine author (personal or organization)
    if organization_id:
        author = f"urn:li:organization:{organization_id}"
    else:
        author = "urn:li:person:me"
    
    # Prepare post payload
    payload = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility
        }
    }
    
    try:
        logger.info(f"Posting to LinkedIn (visibility: {visibility})")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract post ID from response
            post_id = result.get("id", "")
            post_url = f"https://www.linkedin.com/feed/update/{post_id}"
            
            logger.info(f"LinkedIn post created: {post_url}")
            
            return {
                "post_url": post_url,
                "post_id": post_id,
                "status": "published",
                "visibility": visibility,
                "draft_reference": draft_url,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"LinkedIn API error: {e.response.status_code} - {e.response.text}")
        raise ValueError(f"LinkedIn API error ({e.response.status_code}): {e.response.text}")
    
    except httpx.RequestError as e:
        logger.error(f"Request to LinkedIn failed: {e}")
        raise ValueError(f"Failed to connect to LinkedIn: {e}")
