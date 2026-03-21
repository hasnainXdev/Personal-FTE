# Gold Tier - Personal AI Employee

**Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

![Gold Tier](https://img.shields.io/badge/Tier-Gold-yellow)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

Gold Tier includes **all Silver tier features** plus:
- ✅ **Odoo Community accounting** integration via JSON-RPC (Odoo 19+)
- ✅ **Facebook integration** for business posts via Graph API

### What's Included

| Category | Features |
|----------|----------|
| **Silver Features** | File System Watcher, Gmail Watcher, LinkedIn posting, MCP server, Approval workflow, Scheduler |
| **Gold Additions** | Odoo integration, Facebook integration (Graph API) |
| **Skipped** | WhatsApp, Instagram, Twitter (per requirements) |

### Facebook Integration Features

- ✅ Post text updates to Facebook Pages
- ✅ Share links with previews
- ✅ Post images (via URL or file upload)
- ✅ Schedule posts for later publishing
- ✅ Human-in-the-loop approval workflow
- ✅ Draft mode for review before posting
- ✅ Automatic logging and audit trail

## Quick Start

### Prerequisites

- Python 3.12+
- Obsidian v1.10.6+
- Claude Code subscription
- Gmail API credentials (for Gmail watcher)
- (Optional) Odoo Community Edition for accounting
- (Optional) Facebook Page for social media posting

### Installation

```bash
# Navigate to gold directory
cd gold

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
playwright install  # For LinkedIn automation

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

### Running

```bash
# Terminal 1: Start watchers
python -m src.main --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Start scheduler
python -m src.main --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: Start MCP server
python -m src.main --vault ./AI_Employee_Vault --mode mcp
```

## Project Structure

```
gold/
├── AI_Employee_Vault/       # Obsidian vault
│   ├── Inbox/              # Raw incoming items
│   ├── Needs_Action/       # Items requiring action
│   ├── In_Progress/        # Currently being worked
│   ├── Done/               # Completed items
│   ├── Pending_Approval/   # Awaiting human decision
│   ├── Approved/           # Approved actions
│   ├── Rejected/           # Rejected items
│   ├── Plans/              # Multi-step plans
│   ├── Briefings/          # Daily/Weekly briefings
│   ├── Logs/               # System logs
│   ├── Accounting/         # Financial records
│   ├── Invoices/           # Invoice files
│   ├── Business_Goals/     # Goals and objectives
│   ├── Signals/            # System signals
│   ├── Updates/            # Update notifications
│   ├── Social_Media/       # Social media drafts
│   │   ├── LinkedIn/       # LinkedIn drafts
│   │   └── Facebook/       # Facebook drafts
│   ├── Gmail/              # Gmail-related files
│   ├── Odoo/               # Odoo integration files
│   └── Archive/            # Archived items
├── src/
│   ├── main.py             # Main orchestrator
│   ├── watchers/           # Watcher implementations
│   │   ├── base_watcher.py
│   │   ├── filesystem_watcher.py
│   │   └── gmail_watcher.py
│   ├── mcp/                # MCP tools
│   │   └── tools.py
│   ├── services/           # External services
│   │   └── odoo_client.py
│   ├── scheduler/          # Task scheduler
│   │   ├── scheduler.py
│   │   └── tasks.py
│   └── utils/              # Utilities
│       ├── logging_config.py
│       ├── retry_handler.py
│       ├── audit_logger.py
│       └── ralph_wiggum.py
├── mcp_server/             # MCP server
├── tests/                  # Test suite
├── credentials/            # Credentials (gitignored)
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Core Components

### 1. Watchers (Perception)

| Watcher | Description | Interval |
|---------|-------------|----------|
| FileSystemWatcher | Monitors drop folder for new files | Real-time |
| GmailWatcher | Monitors Gmail for unread emails | 2 minutes |

### 2. MCP Tools (Actions)

| Tool | Description | Approval |
|------|-------------|----------|
| `send_email` | Send emails via Gmail | First time |
| `post_linkedin` | Post to LinkedIn | Always |
| `post_facebook` | Post to Facebook | Always |
| `create_approval_request` | Create approval file | No |
| `check_approvals` | Check pending approvals | No |
| `update_dashboard` | Update Dashboard.md | No |
| `create_odoo_invoice` | Create Odoo invoice | Yes |
| `record_odoo_payment` | Record payment | Yes |

### 3. Scheduler

| Task | Cron Expression | Description |
|------|-----------------|-------------|
| Daily Briefing | `0 8 * * *` | 8:00 AM daily |
| Weekly Audit | `0 18 * * 0` | Sunday 6:00 PM |
| Dashboard Update | `0 * * * *` | Every hour |

## Odoo Integration

### Setup

1. Install Odoo Community Edition (v19+)
2. Create database and user
3. Generate API key in Odoo settings
4. Configure in `.env`:

```env
ODOO_URL=http://localhost:8069
ODOO_DB=your_database
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key
```

### Usage

```python
from src.services.odoo_client import OdooClient

client = OdooClient()
client.authenticate()

# Create invoice
invoice_id = client.create('account.move', {
    'partner_id': 1,
    'move_type': 'out_invoice',
    'invoice_line_ids': [(0, 0, {
        'product_id': 1,
        'quantity': 1,
        'price_unit': 100,
    })],
})

# Record payment
client.register_payment(invoice_id, 100)
```

## Facebook Integration

### Quick Setup

**Option 1: Automated Script (Recommended)**

```bash
# Run the authentication script
python auth_facebook.py
```

This will:
1. Open browser to Facebook OAuth
2. Prompt you to select your Page
3. Save credentials automatically
4. Update your `.env` file

**Option 2: Manual Setup**

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create a new App (Business type)
3. Add Facebook Login product
4. Get App ID and App Secret from Settings
5. Generate Page Access Token via Graph API Explorer
6. Add to `.env`:

```env
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id
```

**See `docs/FACEBOOK_SETUP.md` for detailed instructions.**

### Usage

```python
from src.mcp.tools import post_facebook

# Create draft (requires approval - default)
result = post_facebook(
    content='Exciting news about our product launch! 🚀',
    reason='Business update',
    auto_post=False,
)

# Post directly (no approval)
result = post_facebook(
    content='Flash sale today only! 50% off! 🛍️',
    link_url='https://yourstore.com/sale',
    auto_post=True,
)

# With image
result = post_facebook(
    content='Check out our new office! 🏢',
    image_url='https://example.com/office.jpg',
    auto_post=True,
)
```

### Via Qwen Commands

```bash
# Create Facebook post draft
qwen "Create a Facebook post about our Q1 achievements"

# Post directly
qwen "Post to Facebook: We just hit 1000 followers! Thank you! 🎉"

# Process social media requests
qwen "Process /Needs_Action for Facebook posts"
```

### Testing

```bash
# Test Facebook connection
python test_facebook.py

# Test with live post (optional)
python test_facebook.py  # Select "yes" for live post test
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Facebook not configured" | Run `python auth_facebook.py` |
| "Invalid access token" | Re-run `python auth_facebook.py` |
| "Missing permissions" | Ensure `pages_manage_posts` permission granted |
| "Page not found" | Verify Page ID and admin access |

---

## Human-in-the-Loop (HITL)

For sensitive actions, the AI creates approval request files:

```markdown
---
type: approval_request
action_type: payment
created: 2026-03-04T10:30:00Z
status: pending
---

# Approval Request: payment

## Details
- Amount: $500.00
- To: Client A

## Instructions
- Move to /Approved to approve
- Move to /Rejected to reject
```

## Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src
```

## Troubleshooting

### Gmail Watcher not working
1. Ensure `credentials.json` exists in project root
2. Run initial OAuth flow manually
3. Check Gmail API is enabled in Google Cloud Console

### Odoo connection fails
1. Verify Odoo is running: `http://localhost:8069`
2. Check credentials in `.env`
3. Verify database exists

### Facebook posting fails
1. Run `python auth_facebook.py` to refresh credentials
2. Check token validity: `python test_facebook.py`
3. Verify Page admin access
4. See `docs/FACEBOOK_SETUP.md` for detailed setup

## License

MIT License

## Acknowledgments

- Built for the Personal AI Employee Hackathon 2026
- Powered by Claude Code
- Silver tier features as foundation

---

*Built with ❤️ for the AI Employee revolution*
