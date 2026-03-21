#!/usr/bin/env python3
"""
Test Facebook Integration

Gold Tier - Personal AI Employee

Tests the Facebook Graph API integration.

Usage:
    python test_facebook.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.services.facebook_client import FacebookClient


def test_facebook_connection():
    """Test Facebook connection and configuration"""
    print('=' * 60)
    print('📘 Testing Facebook Connection')
    print('=' * 60)

    client = FacebookClient()

    # Check configuration
    print('\n📋 Checking configuration...')
    if not client.is_configured():
        print('   ✗ Facebook is not configured!')
        print('\n   To configure:')
        print('   1. Run: python auth_facebook.py')
        print('   2. Or set these environment variables:')
        print('      - FACEBOOK_ACCESS_TOKEN')
        print('      - FACEBOOK_PAGE_ID')
        return False

    print('   ✓ Facebook is configured')

    # Validate token
    print('\n📋 Validating access token...')
    token_info = client.validate_token()

    if token_info.get('valid'):
        print('   ✓ Token is valid')
        print(f'   • User ID: {token_info.get("user_id")}')
        print(f'   • Expires: {token_info.get("expires_at", "Never")}')
        print(f'   • Scopes: {", ".join(token_info.get("scopes", [])[:5])}')
    else:
        print('   ✗ Token is invalid or expired')
        print(f'   Error: {token_info.get("error", "Unknown")}')
        print('\n   To fix: Run python auth_facebook.py to refresh token')
        return False

    # Get page info
    print('\n📋 Getting page information...')
    page_info = client.get_page_info()

    if page_info.get('status') == 'success':
        page = page_info.get('page', {})
        print('   ✓ Page found:')
        print(f'      • Name: {page.get("name")}')
        print(f'      • ID: {page.get("id")}')
        print(f'      • Username: @{page.get("username", "N/A")}')
        print(f'      • Followers: {page.get("followers_count", "N/A")}')
        print(f'      • Likes: {page.get("likes", "N/A")}')
    else:
        print('   ✗ Failed to get page info')
        print(f'   Error: {page_info.get("error", "Unknown")}')
        return False

    return True


def test_facebook_post():
    """Test creating a Facebook post (draft mode by default)"""
    print('\n' + '=' * 60)
    print('📘 Testing Facebook Post (Draft Mode)')
    print('=' * 60)

    client = FacebookClient()

    if not client.is_configured():
        print('   ✗ Facebook not configured. Run: python auth_facebook.py')
        return False

    # Test draft creation (safe - doesn't actually post)
    from src.mcp.tools import post_facebook

    print('\n📋 Creating test post draft...')
    result = post_facebook(
        content='🧪 Test post from Gold Tier AI Employee\n\nThis is a test of the Facebook integration. If you see this, the system is working correctly!',
        reason='Testing Facebook integration',
        auto_post=False,  # Don't actually post
    )

    if result.get('status') == 'draft_created':
        print('   ✓ Draft created successfully')
        print(f'   • Path: {result.get("draft_path")}')
        print('\n   To actually post:')
        print('   1. Move the draft file to /Approved folder')
        print('   2. Or call post_facebook() with auto_post=True')
        return True
    else:
        print('   ✗ Failed to create draft')
        print(f'   Error: {result.get("error", "Unknown")}')
        return False


def test_facebook_live_post():
    """Test creating a live Facebook post"""
    print('\n' + '=' * 60)
    print('📘 Testing Facebook Live Post')
    print('=' * 60)

    print('\n⚠️  This will create an ACTUAL post on your Facebook Page!')
    confirm = input('   Continue? (yes/no): ').strip().lower()

    if confirm != 'yes':
        print('   Skipped.')
        return None

    client = FacebookClient()

    if not client.is_configured():
        print('   ✗ Facebook not configured. Run: python auth_facebook.py')
        return False

    print('\n📋 Creating live post...')
    result = client.post(
        message='🧪 LIVE TEST POST from Gold Tier AI Employee\n\nThis is a live test of the Facebook Graph API integration. Timestamp: {}'.format(
            __import__('datetime').datetime.now().isoformat()
        ),
    )

    if result.get('status') == 'success':
        print('   ✓ Post created successfully!')
        print(f'   • Post ID: {result.get("post_id")}')
        print(f'   • Post URL: {result.get("post_url")}')
        print('\n   Check your Facebook Page to verify the post!')
        return True
    else:
        print('   ✗ Failed to create post')
        print(f'   Error: {result.get("error", "Unknown")}')
        return False


def main():
    """Run all tests"""
    print('\n📘 Facebook Integration Tests - Gold Tier AI Employee\n')

    # Test 1: Connection
    connection_ok = test_facebook_connection()

    if not connection_ok:
        print('\n' + '=' * 60)
        print('⚠️  Connection test failed. Configure Facebook first.')
        print('=' * 60)
        print('\nSetup Instructions:')
        print('1. Go to https://developers.facebook.com')
        print('2. Create a Facebook App (Business type)')
        print('3. Add Facebook Login product')
        print('4. Get App ID and App Secret')
        print('5. Run: python auth_facebook.py')
        print('\nSee docs/FACEBOOK_SETUP.md for detailed instructions.')
        return 1

    # Test 2: Draft creation
    draft_ok = test_facebook_post()

    # Test 3: Live post (optional)
    live_ok = test_facebook_live_post()

    # Summary
    print('\n' + '=' * 60)
    print('📊 Test Summary')
    print('=' * 60)
    print(f'   Connection: {"✓ Pass" if connection_ok else "✗ Fail"}')
    print(f'   Draft Post: {"✓ Pass" if draft_ok else "✗ Fail"}')
    print(f'   Live Post: {"✓ Pass" if live_ok else "⊘ Skipped"}')

    if connection_ok and draft_ok:
        print('\n✅ Facebook integration is working correctly!')
        return 0
    else:
        print('\n❌ Some tests failed. Check configuration.')
        return 1


if __name__ == '__main__':
    exit(main())
