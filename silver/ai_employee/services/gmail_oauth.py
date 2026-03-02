"""
Gmail OAuth 2.0 Setup and Token Management

Handles OAuth 2.0 flow for Gmail API access.
Stores tokens securely in the vault.
"""

import json
import logging
import os
import webbrowser
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

# Gmail API scopes
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
]

# Vault paths for token storage
VAULT_ROOT = Path(os.getenv("VAULT_ROOT", "AI_Employee_Vault"))
CREDENTIALS_PATH = VAULT_ROOT / "Skills" / "gmail_credentials.json"
TOKEN_PATH = VAULT_ROOT / "Skills" / "gmail_token.json"


def ensure_vault_structure():
    """Ensure vault directories exist for storing credentials."""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_client_config() -> dict | None:
    """Load Gmail OAuth client configuration."""
    if not CREDENTIALS_PATH.exists():
        return None
    
    with open(CREDENTIALS_PATH, "r") as f:
        return json.load(f)


def save_client_config(config: dict):
    """Save Gmail OAuth client configuration securely."""
    ensure_vault_structure()
    with open(CREDENTIALS_PATH, "w") as f:
        json.dump(config, f, indent=2)
    # Restrict file permissions (Unix only)
    try:
        os.chmod(CREDENTIALS_PATH, 0o600)
        logger.info(f"Client config saved with restricted permissions: {CREDENTIALS_PATH}")
    except Exception as e:
        logger.warning(f"Could not restrict file permissions: {e}")


def load_token() -> Credentials | None:
    """Load stored OAuth token."""
    if not TOKEN_PATH.exists():
        return None
    
    with open(TOKEN_PATH, "r") as f:
        token_data = json.load(f)
    
    return Credentials.from_authorized_user_info(token_data, GMAIL_SCOPES)


def save_token(credentials: Credentials):
    """Save OAuth token securely."""
    ensure_vault_structure()
    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    }
    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f, indent=2)
    # Restrict file permissions
    try:
        os.chmod(TOKEN_PATH, 0o600)
        logger.info(f"Token saved with restricted permissions: {TOKEN_PATH}")
    except Exception as e:
        logger.warning(f"Could not restrict file permissions: {e}")


def refresh_token_if_needed(credentials: Credentials) -> Credentials:
    """Refresh token if expired."""
    if credentials.expired and credentials.refresh_token:
        logger.info("Refreshing expired Gmail OAuth token")
        credentials.refresh(Request())
        save_token(credentials)
        logger.info("Token refreshed successfully")
    return credentials


def validate_credentials(client_config: dict) -> bool:
    """Validate client configuration structure."""
    required_keys = ["web", "installed"]
    
    if "web" in client_config:
        # Web application credentials
        web_config = client_config["web"]
        required = ["client_id", "client_secret", "redirect_uris", "auth_uri", "token_uri"]
        return all(key in web_config for key in required)
    elif "installed" in client_config:
        # Desktop/Installed app credentials
        installed_config = client_config["installed"]
        required = ["client_id", "client_secret", "redirect_uris", "auth_uri", "token_uri"]
        return all(key in installed_config for key in required)
    else:
        logger.error("Invalid client config format. Must contain 'web' or 'installed' key")
        return False


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle OAuth 2.0 callback."""
    
    def __init__(self, *args, flow=None, **kwargs):
        self.flow = flow
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle OAuth callback."""
        query_params = parse_qs(urlparse(self.path).query)
        
        if "error" in query_params:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            error_msg = f"OAuth Error: {query_params['error'][0]}"
            self.wfile.write(f"<html><body><h1>{error_msg}</h1><p>You can close this window.</p></body></html>".encode())
            logger.error(error_msg)
            return
        
        if "code" not in query_params:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>No authorization code received</h1></body></html>")
            return
        
        # Exchange code for token
        code = query_params["code"][0]
        try:
            self.flow.fetch_token(code=code)
            credentials = self.flow.credentials
            
            # Save token
            save_token(credentials)
            
            # Success page
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            success_html = f"""
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✓ Gmail API Authorized!</h1>
                <p>Email: {credentials.id_token.get('email', 'Unknown')}</p>
                <p>Token expires: {credentials.expiry}</p>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
            logger.info(f"Gmail OAuth successful for: {credentials.id_token.get('email', 'Unknown')}")
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Token Exchange Failed</h1><p>{e}</p></body></html>".encode())
            logger.error(f"Token exchange failed: {e}")


def run_oauth_flow(client_config: dict, port: int = 8085) -> Credentials:
    """
    Run OAuth 2.0 flow to get Gmail API credentials.
    
    Args:
        client_config: OAuth client configuration
        port: Port for OAuth callback server
        
    Returns:
        OAuth credentials
    """
    logger.info("Starting Gmail OAuth 2.0 flow")
    
    # Create flow
    flow = Flow.from_client_config(
        client_config,
        scopes=GMAIL_SCOPES,
        redirect_uri=f"http://localhost:{port}/callback"
    )
    
    # Generate authorization URL
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    
    logger.info(f"Opening browser to: {auth_url}")
    print(f"\n{'='*60}")
    print("GMAIL API AUTHORIZATION")
    print(f"{'='*60}")
    print(f"\n1. Opening browser to Gmail authorization page...")
    print(f"2. If browser doesn't open, visit:")
    print(f"   {auth_url}")
    print(f"\n3. Sign in with your Gmail account")
    print(f"4. Grant permissions to the AI Employee")
    print(f"5. You'll be redirected back automatically")
    print(f"\nWaiting for authorization...")
    print(f"{'='*60}\n")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Start callback server
    def handler(*args, **kwargs):
        return OAuthCallbackHandler(*args, flow=flow, **kwargs)
    
    server = HTTPServer(("localhost", port), handler)
    server.timeout = 300  # 5 minute timeout
    
    try:
        server.handle_request()
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise
    
    # Get credentials
    credentials = flow.credentials
    
    if not credentials.valid:
        if credentials.refresh_token:
            credentials.refresh(Request())
    
    return credentials


def setup_gmail_oauth(port: int = 8085) -> bool:
    """
    Interactive setup for Gmail OAuth.
    
    Returns:
        True if setup successful
    """
    print("\n" + "="*60)
    print("GMAIL API OAUTH SETUP")
    print("="*60)
    
    # Check for existing credentials
    if CREDENTIALS_PATH.exists():
        print(f"\n✓ Found client config: {CREDENTIALS_PATH}")
        client_config = load_client_config()
        if not validate_credentials(client_config):
            print("✗ Invalid client config format")
            return False
    else:
        print("\n✗ Client config not found!")
        print(f"\nExpected location: {CREDENTIALS_PATH}")
        print("\nTo get your credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Go to Credentials > Create Credentials > OAuth client ID")
        print("5. Application type: Web application")
        print(f"6. Authorized redirect URIs: http://localhost:{port}/callback")
        print("7. Download the JSON file")
        print(f"8. Save it as: {CREDENTIALS_PATH}")
        print("\nAfter saving the file, run this script again.")
        return False
    
    # Check for existing token
    if TOKEN_PATH.exists():
        print(f"\n✓ Found existing token: {TOKEN_PATH}")
        token = load_token()
        if token and token.valid:
            print("✓ Existing token is valid")
            try:
                token = refresh_token_if_needed(token)
                print(f"✓ Token valid until: {token.expiry}")
                return True
            except Exception as e:
                print(f"✗ Token refresh failed: {e}")
        else:
            print("✗ Existing token is invalid or expired")
    
    # Run OAuth flow
    try:
        credentials = run_oauth_flow(client_config, port)
        print("\n✓ Gmail OAuth setup completed successfully!")
        print(f"✓ Token saved to: {TOKEN_PATH}")
        return True
    except Exception as e:
        print(f"\n✗ OAuth setup failed: {e}")
        return False


def get_gmail_credentials() -> Credentials | None:
    """
    Get valid Gmail OAuth credentials.
    
    Returns:
        Valid credentials or None if not available
    """
    if not TOKEN_PATH.exists():
        logger.info("No Gmail token found")
        return None
    
    credentials = load_token()
    if not credentials:
        return None
    
    if not credentials.valid:
        if credentials.refresh_token:
            try:
                credentials = refresh_token_if_needed(credentials)
                return credentials
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                return None
        else:
            logger.warning("Token expired and no refresh token")
            return None
    
    return credentials


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    success = setup_gmail_oauth()
    exit(0 if success else 1)
