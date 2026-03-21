# Facebook Integration Setup Guide

**Gold Tier - Personal AI Employee**

This guide walks you through setting up Facebook API access for your AI Employee.

---

## Overview

The Facebook integration allows your AI Employee to:
- ✅ Post text updates to your Facebook Page
- ✅ Share links with previews
- ✅ Post images (via URL)
- ✅ Schedule posts for later
- ✅ Create draft posts for approval (HITL workflow)

---

## Prerequisites

Before you begin, ensure you have:

1. ✅ A **Facebook Business Account** (free at [business.facebook.com](https://business.facebook.com))
2. ✅ A **Facebook Page** that you admin (for your business/brand)
3. ✅ A **Facebook Developer Account** (free at [developers.facebook.com](https://developers.facebook.com))

---

## Step 1: Create a Facebook App

### 1.1 Go to Facebook Developers

1. Visit [https://developers.facebook.com](https://developers.facebook.com)
2. Click **"Get Started"** or **"My Apps"** in the top right
3. Log in with your Facebook account

### 1.2 Create New App

1. Click **"Create App"** button
2. Select use case: **"Business"** (recommended) or **"Other"**
3. Click **"Next"**

### 1.3 Configure App

Fill in the details:

| Field | Value |
|-------|-------|
| **App Name** | `AI Employee` (or your business name) |
| **App Contact Email** | Your email address |
| **Business Account** | Select your business (or create one) |

4. Click **"Create App"**
5. Complete security verification if prompted

### 1.4 Get App Credentials

1. Go to **Settings → Basic** in the left sidebar
2. You'll see:
   - **App ID** (copy this)
   - **App Secret** (click "Show" and copy)

Save these for the next step!

---

## Step 2: Add Facebook Login Product

### 2.1 Add Product

1. In your App Dashboard, scroll down to **"Add Products to Your App"**
2. Find **"Facebook Login"** and click **"Set Up"**

### 2.2 Configure Settings

1. Click **"Facebook Login"** in the left sidebar
2. Under **"Settings"**:
   - **Valid OAuth Redirect URIs**: Add `http://localhost:8080/`
   - **Client OAuth Settings**: Enable **"Embedded Browser OAuth"**
   - **Web OAuth Login**: Enable
3. Click **"Save Changes"**

### 2.3 Configure App Domains (Optional for Production)

For local development, this is not required. For production:

1. Go to **Settings → Basic**
2. Add your domain to **"App Domains"**
3. Add your website URL to **"Privacy Policy URL"** and **"User Data Deletion URL"**

---

## Step 3: Authenticate and Get Access Token

### Option A: Automated Script (Recommended)

We provide an authentication script that handles the OAuth flow:

```bash
# Navigate to gold directory
cd gold

# Run authentication script
python auth_facebook.py
```

The script will:
1. Open your browser to Facebook OAuth
2. Prompt you to log in and grant permissions
3. Select your Facebook Page
4. Save credentials automatically
5. Update your `.env` file

**Follow the on-screen prompts!**

### Option B: Manual Token Generation

If you prefer manual setup:

#### 3.1 Get User Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **"Get Token" → "Get User Access Token"**
4. Select permissions:
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_engagement`
   - ✅ `publish_to_groups` (optional)
5. Click **"Generate Access Token"**
6. Complete any security checks
7. Copy the generated token

#### 3.2 Get Page Access Token

1. In Graph API Explorer, with your token selected:
2. In the query box, enter: `me/accounts`
3. Click **"Submit"**
4. Find your page in the results
5. Copy the `access_token` value (this is your **Page Access Token**)
6. Also copy the page `id` (this is your **Page ID**)

#### 3.3 Save Credentials

Add to your `.env` file:

```env
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

---

## Step 4: Test the Integration

### 4.1 Run Test Script

```bash
python test_facebook.py
```

This will:
- ✓ Verify your configuration
- ✓ Validate your access token
- ✓ Get your page information
- ✓ Create a test draft post

### 4.2 Expected Output

```
============================================================
📘 Testing Facebook Connection
============================================================

📋 Checking configuration...
   ✓ Facebook is configured

📋 Validating access token...
   ✓ Token is valid
   • User ID: 123456789
   • Expires: Never
   • Scopes: pages_manage_posts, pages_read_engagement

📋 Getting page information...
   ✓ Page found:
      • Name: Your Business Page
      • ID: 987654321
      • Username: @yourpage
      • Followers: 1234
      • Likes: 1200

============================================================
📘 Testing Facebook Post (Draft Mode)
============================================================
   ✓ Draft created successfully
   • Path: AI_Employee_Vault/Pending_Approval/FACEBOOK_20260314_120000.md

✅ Facebook integration is working correctly!
```

---

## Step 5: Using Facebook in Your AI Employee

### Via Qwen Commands

```bash
# Create a Facebook post draft
qwen "Create a Facebook post about our new product launch"

# Post directly (if auto_post enabled)
qwen "Post to Facebook: We just hit 1000 followers! Thank you all! 🎉"

# With image
qwen "Post to Facebook with image https://example.com/image.jpg about our team event"
```

### Via MCP Tool

```python
from src.mcp.tools import post_facebook

# Create draft (default - requires approval)
result = post_facebook(
    content='Exciting news! Our Q1 results are in... 📈',
    reason='Business update',
    auto_post=False,  # Creates draft for approval
)

# Post directly (no approval)
result = post_facebook(
    content='Flash sale! 50% off everything today only! 🛍️',
    link_url='https://yourstore.com/sale',
    auto_post=True,
)
```

### Via Action Files

Create a request file:

```bash
cat > AI_Employee_Vault/Needs_Action/SOCIAL_facebook_q1.md << 'EOF'
---
type: social_media_request
platform: facebook
priority: normal
---

# Facebook Post Request

Create a business post about our Q1 achievements:
- Revenue grew 25%
- New clients: 15
- Team expanded to 10 people

Include relevant emojis and keep it professional.
EOF
```

Then invoke Qwen:

```bash
qwen "Process /Needs_Action for Facebook posts"
```

Qwen will create a draft in `/Pending_Approval/`. Move it to `/Approved/` to post.

---

## Troubleshooting

### Error: "Facebook not configured"

**Cause:** Missing credentials in `.env`

**Fix:**
```bash
python auth_facebook.py
```

Or manually add to `.env`:
```env
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
```

### Error: "Invalid access token"

**Cause:** Token expired or revoked

**Fix:** Re-run authentication:
```bash
python auth_facebook.py
```

### Error: "(#200) Requires pages_manage_posts permission"

**Cause:** Missing permission in OAuth scope

**Fix:**
1. Re-run `python auth_facebook.py`
2. Ensure you grant all requested permissions
3. Or manually generate token with `pages_manage_posts` permission

### Error: "Page not found"

**Cause:** Wrong Page ID or you're not an admin

**Fix:**
1. Verify you're admin of the page
2. Get correct Page ID from [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
3. Query: `me/accounts`
4. Use the `id` from your page

### Error: "App is in development mode"

**Cause:** App not published

**Fix:**
1. Go to **App Dashboard → Settings → Basic**
2. Toggle **"App Mode"** to **"Live"**
3. Save changes

---

## Security Best Practices

### Token Storage

- ✅ Tokens stored in `credentials/` folder (gitignored)
- ✅ Never commit `.env` or credential files
- ✅ Use Page Access Tokens (don't expire) instead of User Tokens

### Permissions

Only request necessary permissions:
- `pages_manage_posts` - Required for posting
- `pages_read_engagement` - Required for reading page info
- `publish_to_groups` - Optional, for group posting

### App Review

For production use with real users, your app needs Facebook review:

1. Go to **App Dashboard → App Review**
2. Submit each permission for review
3. Provide screencast demonstrating usage
4. Wait for approval (typically 1-7 days)

**For personal use (posting to your own pages), app review is NOT required.**

---

## API Limits

Facebook Graph API has rate limits:

| Endpoint | Limit |
|----------|-------|
| Page Posts | 200 posts per hour |
| Token Validation | 200 calls per hour |

For typical AI Employee usage, you won't hit these limits.

---

## Advanced Usage

### Posting Images

```python
from src.services.facebook_client import FacebookClient

client = FacebookClient()

# Post with image URL
result = client.post(
    message='Check out our new office! 🏢',
    image_url='https://example.com/office.jpg',
)

# Post with local image file
result = client.post_with_image(
    message='Team photo 2026! 📸',
    image_path='./photos/team_2026.jpg',
)
```

### Scheduling Posts

```python
from datetime import datetime, timedelta

# Schedule for tomorrow at 9 AM
tomorrow = datetime.now() + timedelta(days=1)
scheduled_time = tomorrow.replace(hour=9, minute=0).isoformat()

result = client.post(
    message='Good morning! Here\'s your daily tip... ☀️',
    scheduled_time=scheduled_time,
)
```

### Sharing Links

```python
result = client.post(
    message='New blog post alert! 📝',
    link_url='https://yourblog.com/latest-post',
)
```

---

## Reference

- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [Facebook Login Docs](https://developers.facebook.com/docs/facebook-login)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Page Access Tokens](https://developers.facebook.com/docs/pages/access-tokens)

---

## Support

For issues:
1. Check this guide first
2. Run `python test_facebook.py` to diagnose
3. Check logs in `AI_Employee_Vault/Logs/`
4. Re-run `python auth_facebook.py` to refresh credentials

---

*Gold Tier - Personal AI Employee*
*Facebook Integration v1.0*
