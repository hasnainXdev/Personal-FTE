# Gmail Integration Setup Guide

## Quick Start Options

### Option 1: Use Mock Mode (Recommended for Testing)

For immediate testing without Google Cloud setup:

```bash
# Set mock mode environment variable
export GMAIL_MOCK_MODE=true

# Run watchers - will generate test emails
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers
```

In mock mode, the watcher generates 3 test emails:
1. Urgent invoice request (high priority)
2. Meeting confirmation (medium priority)
3. Newsletter (low priority)

### Option 2: Connect Real Gmail (Production)

To connect your real Gmail account, follow the setup below.

---

## Error 400: redirect_uri_mismatch

This error occurs when the OAuth2 redirect URI doesn't match what's registered in Google Cloud Console.

### Quick Fix

**The default redirect URI is:** `http://localhost:8085/callback`

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project

2. **Navigate to Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Find your OAuth 2.0 Client ID (Desktop app)
   - Click to edit

3. **Add Authorized Redirect URI**
   - Under "Authorized redirect URIs", add:
     ```
     http://localhost:8085/callback
     ```
   - Click "Save"

4. **Wait for Propagation**
   - Changes can take 5-10 minutes to propagate

5. **Run the Watcher Again**
   ```bash
   python3 src/main.py --vault ./AI_Employee_Vault --mode watchers
   ```

---

## Complete Setup Guide

### 1. Create Google Cloud Project

1. Visit https://console.cloud.google.com/
2. Create a new project (e.g., "AI Employee")

### 2. Enable Gmail API

1. Go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "Enable"

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in required fields:
   - App name: AI Employee
   - User support email: your email
   - Developer contact email: your email
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.labels`
5. Add test users (your Gmail address)
6. Click "Save and Continue"

### 4. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Desktop app**
4. Under "Authorized redirect URIs", add:
   ```
   http://localhost:8085/callback
   ```
5. Click "Create"
6. Download the JSON file
7. Save as `credentials.json` in `silver/` folder

### 5. Run the Watcher

```bash
cd silver
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers
```

The first run will:
1. Open browser to Google login
2. You authorize the app
3. Token is saved to `AI_Employee_Vault/token.json`
4. Subsequent runs use the saved token

---

## Troubleshooting

### Still Getting redirect_uri_mismatch

1. **Check redirect URI format**
   - Must exactly match: `http://localhost:8085/callback`
   - Not `http://localhost:8085/` or `http://localhost:8085`

2. **Wait for propagation**
   - Google Cloud changes can take 5-10 minutes

3. **Use incognito mode**
   - Clear browser cache and try again

4. **Check OAuth client type**
   - Must be "Desktop app" not "Web application"

### Mock Mode Not Working

```bash
# Verify mock mode is enabled
echo $GMAIL_MOCK_MODE  # Should output: true

# Export if not set
export GMAIL_MOCK_MODE=true
```

### Credentials File Not Found

```bash
# Check if credentials.json exists
ls -la credentials.json

# Should be in silver/ folder (same level as src/)
```

### Token File Issues

```bash
# Remove old token and re-authenticate
rm AI_Employee_Vault/token.json

# Run watcher again
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers
```

---

## Testing Without Gmail

You can fully test the Silver Tier without Gmail integration:

```bash
# 1. Use mock mode
export GMAIL_MOCK_MODE=true
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers

# 2. Drop a test file
echo "Test content" > AI_Employee_Vault/Inbox_Drop/test.txt

# 3. Process with Qwen
cd AI_Employee_Vault
qwen "Process items in /Needs_Action"
```

---

## Security Notes

- **Never commit** `credentials.json` to git
- **Never commit** `token.json` to git
- Store credentials securely
- Rotate credentials regularly
- Use test users during development

---

## Next Steps

1. **For Development**: Use mock mode (recommended)
2. **For Testing**: Set up Google Cloud Console
3. **For Production**: Implement service account

---

*Silver Tier - Gmail Integration*
*Powered by Qwen*
