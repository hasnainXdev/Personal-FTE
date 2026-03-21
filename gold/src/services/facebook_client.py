"""
Facebook Graph API Client

Gold Tier - Personal AI Employee
Handles Facebook posting via Facebook Graph API
"""

import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class FacebookClient:
    """
    Facebook Graph API client for posting to Facebook pages
    """

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        page_id: Optional[str] = None,
    ):
        """
        Initialize Facebook client

        Args:
            app_id: Facebook App ID
            app_secret: Facebook App Secret
            access_token: Facebook Access Token (Page Access Token recommended)
            page_id: Facebook Page ID to post to
        """
        import os
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()

        self.app_id = app_id or os.getenv('FACEBOOK_APP_ID')
        self.app_secret = app_secret or os.getenv('FACEBOOK_APP_SECRET')
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = page_id or os.getenv('FACEBOOK_PAGE_ID')

        self.base_url = 'https://graph.facebook.com/v18.0'

        # Token storage paths
        self.credentials_path = Path('./credentials/facebook_credentials.json')
        self.token_path = Path('./credentials/facebook_token.json')

    def is_configured(self) -> bool:
        """Check if Facebook is properly configured"""
        if not self.access_token:
            logger.warning('Facebook access token not configured')
            return False
        if not self.page_id:
            logger.warning('Facebook page ID not configured')
            return False
        return True

    def get_page_access_token(self, user_access_token: str) -> Optional[str]:
        """
        Exchange user access token for page access token

        Args:
            user_access_token: User's OAuth token

        Returns:
            Page access token or None
        """
        try:
            # Get list of pages the user manages
            url = f'{self.base_url}/me/accounts'
            params = {
                'access_token': user_access_token,
            }

            response = requests.get(url, params=params, timeout=10)
            result = response.json()

            if 'error' in result:
                logger.error(f'Error getting pages: {result["error"]}')
                return None

            # Find the page by ID or return first page
            for page in result.get('data', []):
                if self.page_id and page.get('id') == self.page_id:
                    logger.info(f'Got page access token for: {page.get("name")}')
                    return page.get('access_token')

            # If no specific page ID, return first page token
            if result.get('data'):
                page = result['data'][0]
                self.page_id = page.get('id')
                logger.info(f'Using page: {page.get("name")} ({page.get("id")})')
                return page.get('access_token')

            logger.error('No pages found for this user')
            return None

        except Exception as e:
            logger.error(f'Error getting page access token: {e}')
            return None

    def post(
        self,
        message: str,
        image_url: Optional[str] = None,
        link_url: Optional[str] = None,
        scheduled_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a post on Facebook

        Args:
            message: Post message content
            image_url: Optional URL of image to attach
            link_url: Optional link to share
            scheduled_time: Optional ISO 8601 datetime for scheduled posting

        Returns:
            Result dictionary with post ID or error
        """
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Facebook not configured. Please set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID',
            }

        try:
            url = f'{self.base_url}/{self.page_id}/feed'

            params = {
                'access_token': self.access_token,
                'message': message,
            }

            # Add link if provided
            if link_url:
                params['link'] = link_url

            # Add scheduled publish time
            if scheduled_time:
                params['published'] = False
                params['scheduled_publish_time'] = scheduled_time

            # Handle image upload
            if image_url:
                # For image URL, we'll create a photo post
                url = f'{self.base_url}/{self.page_id}/photos'
                params['url'] = image_url

            logger.info(f'Posting to Facebook page {self.page_id}')

            response = requests.post(url, params=params, timeout=30)
            result = response.json()

            if 'error' in result:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                logger.error(f'Facebook API error: {error_msg}')
                return {
                    'status': 'error',
                    'error': error_msg,
                    'error_code': result.get('error', {}).get('code'),
                }

            post_id = result.get('id')
            logger.info(f'Facebook post created: {post_id}')

            return {
                'status': 'success',
                'post_id': post_id,
                'post_url': f'https://www.facebook.com/{post_id}',
                'message': 'Post successfully created on Facebook',
            }

        except requests.exceptions.Timeout:
            logger.error('Facebook API request timed out')
            return {
                'status': 'error',
                'error': 'Request timed out',
            }
        except requests.exceptions.RequestException as e:
            logger.error(f'Facebook API request failed: {e}')
            return {
                'status': 'error',
                'error': str(e),
            }
        except Exception as e:
            logger.error(f'Unexpected error posting to Facebook: {e}')
            return {
                'status': 'error',
                'error': str(e),
            }

    def post_with_image(
        self,
        message: str,
        image_path: str,
        link_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a post with an uploaded image

        Args:
            message: Post message
            image_path: Local path to image file
            link_url: Optional link to share

        Returns:
            Result dictionary
        """
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Facebook not configured',
            }

        try:
            url = f'{self.base_url}/{self.page_id}/photos'

            params = {
                'access_token': self.access_token,
                'published': True,
            }

            if message:
                params['message'] = message

            # Upload image file
            with open(image_path, 'rb') as f:
                files = {'source': f}
                response = requests.post(url, params=params, files=files, timeout=30)

            result = response.json()

            if 'error' in result:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                return {
                    'status': 'error',
                    'error': error_msg,
                }

            post_id = result.get('id')
            logger.info(f'Facebook photo post created: {post_id}')

            return {
                'status': 'success',
                'post_id': post_id,
                'post_url': f'https://www.facebook.com/{post_id}',
            }

        except FileNotFoundError:
            logger.error(f'Image file not found: {image_path}')
            return {
                'status': 'error',
                'error': f'Image file not found: {image_path}',
            }
        except Exception as e:
            logger.error(f'Error posting image to Facebook: {e}')
            return {
                'status': 'error',
                'error': str(e),
            }

    def get_page_info(self) -> Dict[str, Any]:
        """
        Get information about the configured Facebook page

        Returns:
            Page information dictionary
        """
        if not self.is_configured():
            return {
                'status': 'error',
                'error': 'Facebook not configured',
            }

        try:
            url = f'{self.base_url}/{self.page_id}'
            params = {
                'access_token': self.access_token,
                'fields': 'id,name,username,about,followers_count,likes',
            }

            response = requests.get(url, params=params, timeout=10)
            result = response.json()

            if 'error' in result:
                return {
                    'status': 'error',
                    'error': result.get('error', {}).get('message', 'Unknown error'),
                }

            return {
                'status': 'success',
                'page': result,
            }

        except Exception as e:
            logger.error(f'Error getting page info: {e}')
            return {
                'status': 'error',
                'error': str(e),
            }

    def validate_token(self) -> Dict[str, Any]:
        """
        Validate the current access token

        Returns:
            Token validation result
        """
        if not self.access_token:
            return {
                'status': 'error',
                'error': 'No access token configured',
                'valid': False,
            }

        try:
            url = f'{self.base_url}/debug_token'
            params = {
                'input_token': self.access_token,
                'access_token': f'{self.app_id}|{self.app_secret}',
            }

            response = requests.get(url, params=params, timeout=10)
            result = response.json()

            if 'error' in result:
                return {
                    'status': 'error',
                    'error': result.get('error', {}).get('message', 'Unknown error'),
                    'valid': False,
                }

            data = result.get('data', {})
            is_valid = data.get('is_valid', False)

            return {
                'status': 'success',
                'valid': is_valid,
                'expires_at': data.get('expires_at'),
                'scopes': data.get('scopes', []),
                'user_id': data.get('user_id'),
            }

        except Exception as e:
            logger.error(f'Error validating token: {e}')
            return {
                'status': 'error',
                'error': str(e),
                'valid': False,
            }


# Convenience function for quick posting
def post_to_facebook(
    message: str,
    image_url: Optional[str] = None,
    link_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Quick function to post to Facebook

    Args:
        message: Post message
        image_url: Optional image URL
        link_url: Optional link URL

    Returns:
        Result dictionary
    """
    client = FacebookClient()
    return client.post(message, image_url, link_url)
