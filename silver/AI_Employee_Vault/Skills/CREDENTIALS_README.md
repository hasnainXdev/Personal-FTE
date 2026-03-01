# AI Employee Credentials Vault

## 🔐 Security Notice

This directory contains **SENSITIVE CREDENTIALS** for external services.

**File Permissions:** All files should have `600` permissions (owner read/write only).

---

## Stored Credentials

### Gmail API
- `gmail_credentials.json` - OAuth client configuration (from Google Cloud Console)
- `gmail_token.json` - OAuth access/refresh tokens (auto-generated)

### LinkedIn (Playwright)
- `linkedin_cookies.json` - Session cookies for LinkedIn (auto-generated after login)

---

## Setup Commands

### Gmail API Setup
```bash
# 1. Download OAuth credentials from Google Cloud Console
# 2. Save as: AI_Employee_Vault/Skills/gmail_credentials.json
# 3. Run OAuth flow:
python -m ai_employee.services.gmail_oauth
```

### LinkedIn Setup
```bash
# 1. Add credentials to .env:
#    LINKEDIN_EMAIL=your@email.com
#    LINKEDIN_PASSWORD=your_password
# 2. First run will auto-save session cookies
```

---

## Security Best Practices

1. **Never commit** these files to Git (already in .gitignore)
2. **Backup securely** - encrypt before cloud backup
3. **Rotate regularly** - regenerate tokens periodically
4. **Monitor access** - check Google/Lincoln security dashboards
5. **Use 2FA** - enable on all accounts

---

## File Permissions (Linux/Mac)

```bash
# Restrict access to credentials only
chmod 600 AI_Employee_Vault/Skills/gmail_*.json
chmod 600 AI_Employee_Vault/Skills/linkedin_*.json
```

---

## Troubleshooting

### Gmail API Token Expired
```bash
# Delete old token and re-run OAuth
rm AI_Employee_Vault/Skills/gmail_token.json
python -m ai_employee.services.gmail_oauth
```

### LinkedIn Session Expired
```bash
# Delete cookies and re-login
rm AI_Employee_Vault/Skills/linkedin_cookies.json
# Next run will re-authenticate
```

### Permission Denied Errors
```bash
# Fix file permissions
chmod 600 AI_Employee_Vault/Skills/*.json
```
