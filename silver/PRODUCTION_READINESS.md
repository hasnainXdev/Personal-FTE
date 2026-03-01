# Production Readiness Checklist

## Current Status: 🟡 TESTING/SANDBOX MODE

**What's Working:**
- ✅ MCP Server (localhost:8765)
- ✅ Filesystem Watcher (local files)
- ✅ Plan Generator Service
- ✅ Approval Workflow
- ✅ LinkedIn **Mock** Poster (fake posts)
- ✅ Cron Runner (scheduler)
- ✅ Vault Structure (Obsidian)

**What's NOT Configured:**
- ❌ LinkedIn API (using mock)
- ❌ Gmail API (not connected)
- ❌ SMTP Email (not configured)
- ❌ Real webhooks (using localhost)
- ❌ Production monitoring
- ❌ Error alerting

---

## 🚀 Production Setup Requirements

### 1. LinkedIn Automation (Required for Posting)

**Status**: Currently using `linkedin_mock_test.py`

**To Enable Real Posting:**

#### Step 1: Get LinkedIn API Access

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create a new app
3. Enable these products:
   - **Sign In with LinkedIn**
   - **Share on LinkedIn**
   - **Organization API** (for company pages)

#### Step 2: Get Credentials

```bash
# You'll receive:
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token  # OAuth flow required
LINKEDIN_ORGANIZATION_ID=your_org_id     # Optional (for company posts)
```

#### Step 3: Configure `.env`

```bash
# Copy to .env and fill in real values
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

#### Step 4: Test Real Posting

```bash
# First test with mock (safe)
python -m ai_employee.mcp_server.actions.linkedin_mock_test --test

# Then test with real API (requires credentials)
# WARNING: This will create a REAL LinkedIn post
python -m ai_employee.mcp_server.actions.linkedin_test_real
```

**Alternative (No API Access):**
- Use **manual posting workflow** (draft → copy to LinkedIn → log URL)
- See `LINKEDIN_MANUAL_WORKFLOW.md`

---

### 2. Gmail Watcher (Required for Email Input)

**Status**: Not configured

**To Enable Gmail Watching:**

#### Step 1: Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable **Gmail API**
4. Create OAuth 2.0 credentials

#### Step 2: Get OAuth Tokens

```bash
# Run OAuth setup script
python -m ai_employee.utils.gmail_oauth_setup

# This will:
# 1. Open browser for Google login
# 2. Request Gmail permissions
# 3. Save tokens to .env
```

#### Step 3: Configure `.env`

```bash
GMAIL_OAUTH_TOKEN=your_oauth_token
GMAIL_REFRESH_TOKEN=your_refresh_token
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
```

#### Step 4: Test Gmail Watcher

```bash
# Test connection (read-only)
python -m ai_employee.watchers.gmail_watcher --test

# Should show:
# ✓ Connected to Gmail
# ✓ Found X unread emails
# ✓ Processed Y emails
```

**Alternative (No Gmail API):**
- Use **Filesystem Watcher** (already working)
- Forward emails to a monitored folder
- Use IMAP watcher (simpler, no OAuth)

---

### 3. SMTP Email (Required for Sending Emails)

**Status**: Not configured

**To Enable Email Sending:**

#### Step 1: Get SMTP Credentials

**For Gmail:**
1. Enable 2FA on your Google Account
2. Generate **App Password**: https://myaccount.google.com/apppasswords
3. Use app password (not your regular password)

**For Other Providers:**
- Outlook: smtp.office365.com:587
- SendGrid: smtp.sendgrid.net:587
- Custom: Your SMTP server details

#### Step 2: Configure `.env`

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password  # NOT your regular password!
```

#### Step 3: Test Email Sending

```bash
# Send test email
python -m ai_employee.mcp_server.actions.email_test \
  --to "test@example.com" \
  --subject "Test from AI Employee" \
  --body "This is a test email"

# Check inbox for test email
```

---

### 4. Production Environment Setup

#### Create `.env.production`

```bash
# NEVER commit this file to git!
cat > .env.production << 'EOF'
# ===== PRODUCTION CONFIGURATION =====

# MCP Server
MCP_HOST=0.0.0.0  # Listen on all interfaces
MCP_PORT=8765

# LinkedIn (Real API)
LINKEDIN_CLIENT_ID=prod_client_id_12345
LINKEDIN_CLIENT_SECRET=prod_secret_67890
LINKEDIN_ACCESS_TOKEN=prod_access_token_abcde
LINKEDIN_ORGANIZATION_ID=prod_org_12345

# Gmail (Real API)
GMAIL_OAUTH_TOKEN=prod_oauth_token
GMAIL_REFRESH_TOKEN=prod_refresh_token
GMAIL_CLIENT_ID=prod_gmail_client
GMAIL_CLIENT_SECRET=prod_gmail_secret

# SMTP (Real Email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ai-employee@yourcompany.com
SMTP_PASS=prod_app_password

# Security
SANDBOX_MODE=false  # DISABLE sandbox mode
ALLOW_EXTERNAL_ACTIONS=true
LOG_LEVEL=INFO  # Less verbose than DEBUG

# Monitoring
ENABLE_ALERTING=true
ALERT_EMAIL=admin@yourcompany.com
EOF

# Set restrictive permissions
chmod 600 .env.production
```

---

### 5. Production Deployment

#### Option A: Run as System Service (Linux)

```bash
# Create systemd service
sudo nano /etc/systemd/system/ai-employee.service
```

```ini
[Unit]
Description=AI Employee Silver Tier
After=network.target

[Service]
Type=simple
User=ai-employee
WorkingDirectory=/opt/ai-employee/silver
Environment="PATH=/opt/ai-employee/silver/.venv/bin"
ExecStart=/opt/ai-employee/silver/.venv/bin/python -m ai_employee.mcp_server.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
sudo systemctl status ai-employee
```

#### Option B: Run with Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8765

CMD ["python", "-m", "ai_employee.mcp_server.server"]
```

```bash
# Build and run
docker build -t ai-employee:silver .
docker run -d \
  --name ai-employee \
  -p 8765:8765 \
  -v $(pwd)/AI_Employee_Vault:/app/AI_Employee_Vault \
  --env-file .env.production \
  ai-employee:silver
```

#### Option C: Run with PM2 (Cross-platform)

```bash
# Install PM2
npm install -g pm2

# Create ecosystem config
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'ai-employee-mcp',
    script: 'python',
    args: '-m ai_employee.mcp_server.server',
    cwd: '/path/to/silver',
    env: {
      PYTHONPATH: '.',
    },
    restart_delay: 10000,
    max_restarts: 10,
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

### 6. Production Monitoring

#### Health Check Endpoint

```bash
# Check MCP Server health
curl http://localhost:8765/health

# Expected response:
# {"status":"healthy","uptime_seconds":12345,"version":"1.0.0"}
```

#### Log Monitoring

```bash
# Watch MCP logs in real-time
tail -f ai_employee/mcp_server/logs/mcp_actions.md

# Watch for errors
grep -i "error" ai_employee/mcp_server/logs/*.md | tail -20
```

#### Alerting Setup

```bash
# Create monitoring script
cat > scripts/health_check.sh << 'EOF'
#!/bin/bash

HEALTH_URL="http://localhost:8765/health"
ALERT_EMAIL="admin@example.com"

response=$(curl -s $HEALTH_URL)
status=$(echo $response | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))")

if [ "$status" != "healthy" ]; then
    echo "AI Employee MCP Server is UNHEALTHY" | \
    mail -s "🚨 AI Employee Alert" $ALERT_EMAIL
fi
EOF

chmod +x scripts/health_check.sh

# Add to crontab (check every 5 minutes)
crontab -e
# Add: */5 * * * * /path/to/scripts/health_check.sh
```

---

### 7. Security Hardening

#### Firewall Rules

```bash
# Linux: Allow only localhost access (recommended)
sudo ufw allow from 127.0.0.1 to any port 8765

# Or allow specific IPs
sudo ufw allow from 192.168.1.100 to any port 8765

# Deny all other access
sudo ufw deny 8765
```

#### API Authentication

```bash
# Add API key to .env
MCP_API_KEY=your_secret_api_key_12345

# Modify MCP server to require authentication
# (See ai_employee/mcp_server/auth.py for implementation)
```

#### Secrets Management

```bash
# NEVER commit .env to git
echo ".env" >> .gitignore

# Use secrets manager in production
# AWS: AWS Secrets Manager
# Azure: Azure Key Vault
# GCP: Secret Manager
```

---

## ✅ Production Validation Checklist

Before going live, verify:

### Infrastructure
- [ ] MCP Server running as service/daemon
- [ ] Auto-restart on failure configured
- [ ] Logs rotating (logrotate configured)
- [ ] Backup strategy for vault data

### API Credentials
- [ ] LinkedIn API credentials configured
- [ ] Gmail API credentials configured
- [ ] SMTP credentials configured
- [ ] All credentials tested and working

### Security
- [ ] `.env` file has restrictive permissions (600)
- [ ] Firewall rules configured
- [ ] API authentication enabled (if exposed)
- [ ] No secrets in logs

### Monitoring
- [ ] Health check endpoint responding
- [ ] Alert emails configured
- [ ] Log monitoring active
- [ ] Error tracking enabled

### Testing
- [ ] All sandbox tests passing
- [ ] Real API tests successful
- [ ] End-to-end workflow tested
- [ ] Rollback procedure documented

### Documentation
- [ ] Runbook created
- [ ] Emergency contacts listed
- [ ] Incident response plan documented
- [ ] Team trained on operations

---

## 🎯 Minimum Viable Production (MVP)

If you want to start small, here's the **minimum** to go live:

### Week 1: Filesystem + Manual LinkedIn

```bash
# 1. Filesystem Watcher (already working)
python -m ai_employee.watchers.filesystem_watcher --test

# 2. Manual LinkedIn posting workflow
python -m ai_employee.mcp_server.actions.linkedin_mock_test --test
# → Copy draft to LinkedIn manually
# → Log URL in vault
```

**Status**: ✅ Ready now (no API keys needed)

### Week 2: Add Email (SMTP)

```bash
# 1. Configure SMTP
# Edit .env with Gmail app password

# 2. Test email sending
python -m ai_employee.mcp_server.actions.email_test \
  --to "your@email.com" \
  --subject "Test" \
  --body "Hello"
```

**Status**: ⚠️ Requires SMTP credentials

### Week 3: Add LinkedIn API

```bash
# 1. Get LinkedIn API access
# 2. Configure credentials
# 3. Test real posting
python -m ai_employee.mcp_server.actions.linkedin_test_real
```

**Status**: ⚠️ Requires LinkedIn API approval

### Week 4: Add Gmail API

```bash
# 1. Enable Gmail API
# 2. Run OAuth setup
# 3. Test Gmail watcher
python -m ai_employee.watchers.gmail_watcher --test
```

**Status**: ⚠️ Requires Google Cloud setup

---

## 📊 Current vs Production Comparison

| Feature | Current (Sandbox) | Production |
|---------|------------------|------------|
| **LinkedIn** | Mock posts in vault | Real LinkedIn API posts |
| **Gmail** | Not configured | Real Gmail API watcher |
| **Email Send** | Not configured | Real SMTP emails |
| **Filesystem** | ✅ Working | ✅ Working |
| **Planning** | ✅ Working | ✅ Working |
| **Approval** | ✅ Working | ✅ Working |
| **Scheduler** | ✅ Working | ✅ Working |
| **MCP Server** | localhost only | Network accessible |
| **Monitoring** | Basic logs | Health checks + alerts |
| **Security** | None | Auth + firewall |

---

## 🚨 Important Warnings

### Before Production:

1. **NEVER** commit `.env` to git
2. **ALWAYS** use app passwords (not regular passwords)
3. **TEST** with sandbox mode first
4. **MONITOR** API usage to avoid rate limits
5. **BACKUP** vault data regularly

### API Rate Limits:

| Platform | Limit | Consequence |
|----------|-------|-------------|
| LinkedIn | 50 posts/day | API suspension |
| Gmail | 500 emails/day | Account temporary lock |
| Gmail API | 1B units/day | Quota exceeded errors |

---

## 📚 Next Steps

1. **Read**: `SECURITY_COMPLIANCE.md` - Security best practices
2. **Configure**: `.env` with your credentials
3. **Test**: Sandbox mode first (`python test_sandbox.py`)
4. **Deploy**: Start with MVP (filesystem + manual LinkedIn)
5. **Monitor**: Set up health checks and alerts

---

**Questions?** See documentation:
- `RUN_GUIDE.md` - How to run components
- `QUICK_COMMANDS.md` - Command reference
- `SECURITY_COMPLIANCE.md` - Security guidelines
