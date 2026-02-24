# Gmail API + Playwright LinkedIn Setup Guide

Complete setup guide for AI Employee email and LinkedIn automation.

---

## Quick Start

```bash
# 1. Install dependencies
uv sync
uv run playwright install chromium

# 2. Setup Gmail (choose one method)
#    Option A: Gmail API (recommended)
#    Option B: SMTP (simpler)

# 3. Setup LinkedIn
#    Add credentials to .env

# 4. Test everything
python test_integrations.py
```

---

## Part 1: Gmail API Setup (OAuth 2.0)

### Step 1: Google Cloud Console (10 minutes)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Gmail account

2. **Create New Project**
   - Click project dropdown at top
   - Click "NEW PROJECT"
   - Name: `AI Employee`
   - Click "CREATE"

3. **Enable Gmail API**
   - In dashboard, go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and press "ENABLE"

4. **Create OAuth Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "OAuth client ID"
   - If prompted, configure "OAuth consent screen":
     - User Type: "External"
     - App name: "AI Employee"
     - User support email: your email
     - Developer contact: your email
     - Click "SAVE AND CONTINUE"
     - Scopes: Skip (click "SAVE AND CONTINUE")
     - Test users: Add your Gmail address
     - Click "SAVE AND CONTINUE"

5. **Create OAuth Client ID**
   - Application type: **Web application**
   - Name: `AI Employee Client`
   - Authorized redirect URIs:
     - Click "+ ADD URI"
     - Enter: `http://localhost:8085/callback`
   - Click "CREATE"

6. **Download Credentials**
   - A popup shows "OAuth client created"
   - Click "DOWNLOAD JSON"
   - Save the file

### Step 2: Save Credentials to Vault

```bash
# Create Skills directory if it doesn't exist
mkdir -p AI_Employee_Vault/Skills

# Move downloaded JSON to vault
# Replace PATH with actual download location
mv ~/Downloads/client_secret_*.json AI_Employee_Vault/Skills/gmail_credentials.json

# Rename for consistency
cd AI_Employee_Vault/Skills
mv client_secret_*.json gmail_credentials.json

# Secure permissions (Linux/Mac)
chmod 600 gmail_credentials.json
```

### Step 3: Run OAuth Authorization Flow

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Run OAuth setup
python -m ai_employee.services.gmail_oauth
```

**What happens:**
1. Browser opens automatically
2. Sign in to your Gmail account
3. Grant permissions to "AI Employee"
4. Redirected back to localhost:8085
5. Token saved automatically

**Expected output:**
```
============================================================
GMAIL API OAUTH SETUP
============================================================

✓ Found client config: AI_Employee_Vault/Skills/gmail_credentials.json

Starting Gmail OAuth 2.0 flow
Opening browser to: https://accounts.google.com/...

Waiting for authorization...

✓ Gmail OAuth setup completed successfully!
✓ Token saved to: AI_Employee_Vault/Skills/gmail_token.json
```

### Step 4: Verify Gmail Setup

```bash
# Test Gmail API connection
python -c "
from ai_employee.services.gmail_oauth import get_gmail_credentials
creds = get_gmail_credentials()
if creds:
    print(f'✓ Gmail API authorized for: {creds.id_token.get(\"email\")}')
    print(f'✓ Token valid until: {creds.expiry}')
else:
    print('✗ Gmail API not authorized')
"
```

---

## Part 2: LinkedIn Setup (Playwright)

### Step 1: Install Playwright Browsers

```bash
# Install Chromium browser for Playwright
uv run playwright install chromium

# Install system dependencies (Linux only)
uv run playwright install-deps chromium
```

### Step 2: Add LinkedIn Credentials to .env

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add:
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_linkedin_password

# Security settings (recommended)
LINKEDIN_REQUIRE_CONFIRMATION=true  # Manual confirmation before posting
LINKEDIN_HEADLESS=false  # Show browser window
```

### Step 3: Test LinkedIn Connection

```bash
# Test LinkedIn login (creates session cookies)
python -m ai_employee.services.linkedin_playwright
```

**Expected output:**
```
Starting LinkedIn automation session...
Browser session started
Navigating to LinkedIn login...
Login submitted
Login successful
Session saved: AI_Employee_Vault/Skills/linkedin_cookies.json
```

**First login will:**
1. Open browser window
2. Navigate to LinkedIn login
3. Enter credentials automatically
4. Save session cookies to vault
5. Close browser

**Subsequent runs will:**
- Use saved cookies (no re-login needed)
- Auto-refresh expired sessions

---

## Part 3: Configuration Options

### Gmail: API vs SMTP

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Gmail API** | OAuth 2.0, modern, full Gmail features | More setup steps | Production use |
| **SMTP** | Simple, 15-min setup | Legacy protocol | Quick testing |

**To use SMTP instead:**

1. Enable 2FA on Gmail: https://myaccount.google.com/security
2. Create App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```
   SMTP_USER=your.email@gmail.com
   SMTP_PASS=16-char-app-password
   ```

### LinkedIn: Security Settings

```bash
# .env configuration

# Require manual confirmation before posting (RECOMMENDED)
LINKEDIN_REQUIRE_CONFIRMATION=true

# Show browser window (helps with debugging)
LINKEDIN_HEADLESS=false

# Rate limiting (built-in, don't change unless necessary)
# Max 20 actions/hour with 30-120s random delays
```

---

## Part 4: Testing

### Run Integration Tests

```bash
# Full integration test suite
python test_integrations.py
```

### Test Email Sending

```bash
# Test Gmail API
python -c "
import asyncio
from ai_employee.mcp_server.actions.email import send_email

async def test():
    result = await send_email(
        to='your.email@gmail.com',
        subject='Test from AI Employee',
        body='This is a test email from the AI Employee system.',
        use_gmail_api=True  # Force Gmail API
    )
    print(f'Email sent: {result}')

asyncio.run(test())
"
```

### Test LinkedIn Posting

```bash
# Test LinkedIn (draft mode - no actual post)
python -c "
import asyncio
from ai_employee.services.linkedin_playwright import post_to_linkedin

async def test():
    result = await post_to_linkedin(
        content='Test post from AI Employee',
        visibility='PUBLIC',
        require_confirmation=True  # Don't actually post
    )
    print(f'LinkedIn result: {result}')

asyncio.run(test())
"
```

---

## Part 5: Usage in MCP Server

### Send Email via MCP

```python
# The MCP server automatically uses Gmail API if available
# Falls back to SMTP if Gmail API not configured

# Example: Send email through MCP
{
    "action": "send_email",
    "params": {
        "to": "recipient@example.com",
        "subject": "Hello from AI Employee",
        "body": "This email was sent automatically!",
        "html": false
    }
}
```

### Post to LinkedIn via MCP

```python
# LinkedIn posts go through approval workflow
# 1. Create draft in vault
# 2. Request approval
# 3. Post after approval

# Example: Post to LinkedIn through MCP
{
    "action": "post_linkedin",
    "params": {
        "content": "Excited to share our latest update!",
        "visibility": "PUBLIC",
        "draft_url": "Plans/LinkedIn_Post_20240224.md"
    }
}
```

---

## Troubleshooting

### Gmail API Issues

**Error: "Token expired"**
```bash
# Refresh token
python -m ai_employee.services.gmail_oauth

# Or delete and re-authorize
rm AI_Employee_Vault/Skills/gmail_token.json
python -m ai_employee.services.gmail_oauth
```

**Error: "Redirect URI mismatch"**
- Check redirect URI in Google Cloud Console
- Must be exactly: `http://localhost:8085/callback`
- No trailing slash

**Error: "App not verified"**
- Your app is in "Testing" mode
- Add your email as a test user in OAuth consent screen
- For production, submit for verification (takes days)

### LinkedIn Issues

**Error: "Login failed"**
- Check credentials in .env
- LinkedIn may require 2FA code
- Try manual login first to save cookies

**Error: "Post button not found"**
- LinkedIn UI changed
- Update selectors in `linkedin_playwright.py`
- Run with `LINKEDIN_HEADLESS=false` to debug

**Error: "Suspicious activity detected"**
- LinkedIn detected automation
- Stop immediately
- Wait 24-48 hours before retrying
- Increase delays in rate limit config

### Playwright Issues

**Error: "Browser not found"**
```bash
# Reinstall browsers
uv run playwright install chromium
```

**Error: "Missing system dependencies" (Linux)**
```bash
# Install system deps
uv run playwright install-deps chromium
```

---

## Security Best Practices

### 1. Protect Credentials

```bash
# Restrict file permissions
chmod 600 AI_Employee_Vault/Skills/*.json
chmod 600 .env

# Never commit credentials
# (already in .gitignore)
```

### 2. Monitor Account Activity

- **Gmail**: https://myaccount.google.com/security
- **LinkedIn**: https://www.linkedin.com/psettings/account-access

### 3. Use Rate Limiting

Built-in safeguards:
- Max 20 LinkedIn actions/hour
- Random delays 30-120 seconds
- Manual confirmation mode

### 4. Rotate Credentials

- Regenerate Gmail tokens monthly
- Change LinkedIn password quarterly
- Review connected apps regularly

### 5. Enable 2FA

- **Gmail**: https://myaccount.google.com/security
- **LinkedIn**: Settings > Account > Sign in & security

---

## Next Steps

1. ✅ Test email sending
2. ✅ Test LinkedIn posting (draft mode)
3. ✅ Configure MCP server
4. ✅ Set up watchers
5. ✅ Create first automation workflow

---

## Support

**Documentation:**
- Gmail API: https://developers.google.com/gmail/api
- Playwright: https://playwright.dev/python
- LinkedIn: https://docs.microsoft.com/linkedin

**Issues:**
- Check logs: `ai_employee/mcp_server/logs/`
- Enable debug: Add `LOG_LEVEL=DEBUG` to .env
