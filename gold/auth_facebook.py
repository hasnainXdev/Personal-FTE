#!/usr/bin/env python3
"""
Facebook Authentication Script

Gold Tier - Personal AI Employee

This script helps you authenticate with Facebook and obtain the necessary
access tokens for posting to your Facebook Page.

Usage:
    python auth_facebook.py

Follow the prompts to:
1. Enter your Facebook App ID and App Secret
2. Get a User Access Token
3. Exchange it for a Page Access Token
4. Save credentials for future use
"""

import webbrowser
import json
import hashlib
import base64
import secrets
from pathlib import Path
from urllib.parse import urlencode
import http.server
import socketserver
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

CREDENTIALS_DIR = Path("./credentials")
CREDENTIALS_FILE = CREDENTIALS_DIR / "facebook_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "facebook_token.json"

# Facebook OAuth URLs
FACEBOOK_AUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
FACEBOOK_REDIRECT_URI = "http://localhost:8080/"

# Required permissions for posting to pages
PERMISSIONS = [
    "pages_manage_posts",  # Create posts on pages
    "pages_read_engagement",  # Read page engagement
    "publish_to_groups",  # Post to groups (optional)
]


def generate_code_verifier():
    """Generate a code verifier for PKCE"""
    return secrets.token_urlsafe(32)


def generate_code_challenge(verifier):
    """Generate a code challenge from verifier"""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().replace("=", "")


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handle OAuth callback from Facebook"""

    def do_GET(self):
        """Handle GET request (OAuth callback)"""
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            # Success - got authorization code
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"""
                <html>
                <head><title>Facebook Auth Success</title></head>
                <body>
                    <h1>Facebook Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <script>setTimeout(() => window.close(), 5000);</script>
                </body>
                </html>
            """.encode(
                    "utf-8"
                )
            )
        elif "error" in params:
            # Error occurred
            self.server.auth_error = params.get("error_reason", ["Unknown"])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                f"""
                <html>
                <head><title>Auth Error</title></head>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>Error: {params.get("error", ["Unknown"])[0]}</p>
                    <p>Reason: {params.get("error_reason", ["Unknown"])[0]}</p>
                    <p>You can close this window.</p>
                </body>
                </html>
            """.encode(
                    "utf-8"
                )
            )
        else:
            self.send_response(400)
            self.end_headers()

        self.server.shutdown()

    def log_message(self, format, *args):
        """Suppress logging"""
        pass


def get_user_access_token(app_id: str, app_secret: str) -> str:
    """
    Get user access token via OAuth flow

    Args:
        app_id: Facebook App ID
        app_secret: Facebook App Secret

    Returns:
        User access token
    """
    import requests

    print("\n📱 Step 1: Opening Facebook authorization page...")

    # Generate PKCE parameters
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Build authorization URL
    auth_params = {
        "client_id": app_id,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "scope": ",".join(PERMISSIONS),
        "response_type": "code",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": secrets.token_urlsafe(16),
    }

    auth_url = f"{FACEBOOK_AUTH_URL}?{urlencode(auth_params)}"

    print(f"   Opening: {auth_url[:80]}...")
    print("   If browser does not open, copy the URL above and paste it in your browser.")

    # Start local server to catch callback
    with socketserver.TCPServer(("localhost", 8080), OAuthCallbackHandler) as httpd:
        httpd.auth_code = None
        httpd.auth_error = None

        # Open browser
        webbrowser.open(auth_url)

        print("\n📋 Step 2: Complete authorization in your browser...")
        print("   1. Log in to Facebook (if not already logged in)")
        print("   2. Select the Page you want to post to")
        print('   3. Click "Continue" to grant permissions')
        print("   4. You'll be redirected back (auto-close in 5 seconds)")
        print("\n   Waiting for callback...")

        # Handle single request
        httpd.handle_request()
        httpd.server_close()

        if httpd.auth_error:
            raise Exception(f"Authorization failed: {httpd.auth_error}")

        if not httpd.auth_code:
            raise Exception("No authorization code received")

        auth_code = httpd.auth_code
        print(f"   ✓ Got authorization code: {auth_code[:20]}...")

    print("\n📱 Step 3: Exchanging code for access token...")

    # Exchange code for token
    token_params = {
        "client_id": app_id,
        "client_secret": app_secret,
        "code": auth_code,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "code_verifier": code_verifier,
    }

    response = requests.post(FACEBOOK_TOKEN_URL, data=token_params, timeout=30)
    result = response.json()

    if "error" in result:
        raise Exception(f'Token exchange failed: {result["error"].get("message", "Unknown error")}')

    user_token = result.get("access_token")
    expires_in = result.get("expires_in", "Never")

    print(f"   ✓ Got user access token")
    print(f"   ⏰ Expires in: {expires_in} seconds")

    return user_token


def get_page_access_token(user_token: str, app_id: str, app_secret: str) -> tuple:
    """
    Get page access token from user token

    Args:
        user_token: User access token
        app_id: Facebook App ID
        app_secret: Facebook App Secret

    Returns:
        Tuple of (page_access_token, page_id, page_name)
    """
    import requests

    print("\n📱 Step 4: Getting your Facebook Pages...")

    url = "https://graph.facebook.com/v18.0/me/accounts"
    params = {
        "access_token": user_token,
    }

    response = requests.get(url, params=params, timeout=30)
    result = response.json()

    if "error" in result:
        raise Exception(f'Failed to get pages: {result["error"].get("message", "Unknown error")}')

    pages = result.get("data", [])

    if not pages:
        raise Exception("No Facebook Pages found. You need to be an admin of at least one Page.")

    print(f"   ✓ Found {len(pages)} page(s):")
    for i, page in enumerate(pages, 1):
        print(f'      {i}. {page.get("name")} (ID: {page.get("id")})')

    # Select page
    if len(pages) == 1:
        selected = pages[0]
    else:
        while True:
            try:
                choice = input("\n   Select page number (1): ") or "1"
                idx = int(choice) - 1
                if 0 <= idx < len(pages):
                    selected = pages[idx]
                    break
                else:
                    print(f"   Please enter a number between 1 and {len(pages)}")
            except ValueError:
                print("   Please enter a valid number")

    page_id = selected.get("id")
    page_name = selected.get("name")
    page_token = selected.get("access_token")

    print(f"\n   ✓ Selected: {page_name}")
    print(f"   ✓ Page ID: {page_id}")

    return page_token, page_id, page_name


def save_credentials(
    app_id: str,
    app_secret: str,
    page_access_token: str,
    page_id: str,
    page_name: str,
):
    """Save credentials to files"""

    # Create credentials directory
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

    # Save app credentials
    credentials = {
        "app_id": app_id,
        "app_secret": app_secret,
        "page_id": page_id,
        "page_name": page_name,
        "created": datetime.now().isoformat(),
    }

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=2)

    # Save token
    token_data = {
        "access_token": page_access_token,
        "page_id": page_id,
        "page_name": page_name,
        "created": datetime.now().isoformat(),
    }

    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"\n💾 Credentials saved:")
    print(f"   • {CREDENTIALS_FILE}")
    print(f"   • {TOKEN_FILE}")


def main():
    """Main authentication flow"""
    import os
    from dotenv import load_dotenv

    print("=" * 60)
    print("📘 Facebook Authentication - Gold Tier AI Employee")
    print("=" * 60)

    # Check if already authenticated
    if TOKEN_FILE.exists():
        print("\n⚠️  Facebook credentials already exist!")
        with open(TOKEN_FILE) as f:
            existing = json.load(f)
        print(f'   Page: {existing.get("page_name", "Unknown")}')
        print(f'   Created: {existing.get("created", "Unknown")}')

        overwrite = input("\n   Overwrite existing credentials? (y/N): ")
        if overwrite.lower() != "y":
            print("   Using existing credentials.")
            return

    print("\n📋 Before you start, you need:")
    print("   1. A Facebook Developer Account")
    print("   2. A Facebook App (created at developers.facebook.com)")
    print("   3. Admin access to a Facebook Page")
    print("\n   See README.md or docs/ for detailed setup instructions.")

    input("\n   Press Enter to continue...")

    # Get App ID and Secret
    print("\n📱 Enter your Facebook App credentials:")
    print("   (Find these at developers.facebook.com → Your App → Settings → Basic)")

    app_id = input("   App ID: ").strip()
    app_secret = input("   App Secret: ").strip()

    if not app_id or not app_secret:
        print("   ✗ App ID and App Secret are required!")
        return

    print(f"\n   ✓ App ID: {app_id}")
    print(f'   ✓ App Secret: {"*" * len(app_secret)}')

    try:
        # Get user access token
        user_token = get_user_access_token(app_id, app_secret)

        # Get page access token
        page_token, page_id, page_name = get_page_access_token(user_token, app_id, app_secret)

        # Save credentials
        save_credentials(app_id, app_secret, page_token, page_id, page_name)

        # Update .env file
        env_file = Path("./.env")
        if env_file.exists():
            print("\n💾 Updating .env file...")
            env_content = env_file.read_text()

            # Update or add Facebook credentials
            updates = {
                "FACEBOOK_ACCESS_TOKEN": page_token,
                "FACEBOOK_PAGE_ID": page_id,
            }

            for key, value in updates.items():
                if key in env_content:
                    # Update existing
                    lines = env_content.split("\n")
                    for i, line in enumerate(lines):
                        if line.startswith(f"{key}="):
                            lines[i] = f"{key}={value}"
                            break
                    env_content = "\n".join(lines)
                else:
                    # Add new
                    env_content += f"\n{key}={value}"

            env_file.write_text(env_content)
            print("   ✓ .env file updated")

        print("\n" + "=" * 60)
        print("✅ Facebook Authentication Complete!")
        print("=" * 60)
        print(f"\n📊 Configuration:")
        print(f"   • Page: {page_name}")
        print(f"   • Page ID: {page_id}")
        print(f"   • Token saved to: {TOKEN_FILE}")
        print(f"   • Credentials saved to: {CREDENTIALS_FILE}")

        print("\n🚀 Next steps:")
        print("   1. Add FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID to your .env file")
        print("   2. Test posting: python test_facebook.py")
        print('   3. Use in your AI Employee: qwen "Post to Facebook about..."')

        print("\n⚠️  Important:")
        print("   • Page Access Tokens from this flow do not expire")
        print("   • Keep your credentials secure - never commit them to git!")
        print("   • If posting fails, re-run this script to refresh tokens")

    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")
        print("\n   Troubleshooting:")
        print("   1. Ensure your Facebook App is properly configured")
        print("   2. Check that you have admin access to the Page")
        print("   3. Verify the App ID and Secret are correct")
        print("   4. See docs/FACEBOOK_SETUP.md for detailed instructions")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
