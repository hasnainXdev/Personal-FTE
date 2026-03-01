# AI Employee - Bronze Tier

**Personal AI Employee powered by Qwen** - Local-first, agent-driven, human-in-the-loop.

## 🎯 Bronze Tier Goals

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] One working Watcher script (File System monitoring)
- [x] Qwen integration for reading/writing to vault
- [x] Agent Skills documentation

## 📁 Project Structure

```
bronze/
├── AI_Employee_Vault/       # Obsidian vault
│   ├── Inbox/               # Drop files here
│   ├── Needs_Action/        # Items to process
│   ├── Done/                # Completed items
│   ├── Plans/               # Multi-step plans
│   ├── Pending_Approval/    # Awaiting human approval
│   ├── Approved/            # Approved actions
│   ├── Rejected/            # Declined actions
│   ├── Logs/                # Activity logs
│   ├── Accounting/          # Financial records
│   ├── Briefings/           # CEO briefings
│   ├── Dashboard.md         # Main status view
│   ├── Company_Handbook.md  # AI behavior rules
│   ├── Agent_Skills.md      # Available capabilities
│   └── Welcome.md           # Getting started
├── src/
│   ├── main.py              # Entry point
│   └── watchers/
│       ├── __init__.py
│       ├── base_watcher.py  # Base watcher class
│       └── filesystem_watcher.py  # File monitor
├── tests/
├── pyproject.toml
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd bronze

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Start the File System Watcher

```bash
# From the bronze directory
python src/main.py --vault ./AI_Employee_Vault --interval 30

# Or with debug logging
python src/main.py --vault ./AI_Employee_Vault --interval 30 --debug
```

### 3. Test the System

```bash
# In one terminal, start the watcher
python src/main.py --vault ./AI_Employee_Vault

# In another terminal, drop a test file
echo "Test content" > ./AI_Employee_Vault/Inbox/test_file.txt
```

The watcher will:
1. Detect the new file in `/Inbox`
2. Copy it to `/Needs_Action/` with a unique ID
3. Create a `.md` metadata file with processing instructions

### 4. Process with Qwen

```bash
# Navigate to vault
cd AI_Employee_Vault

# Ask Qwen to process (using your Qwen CLI/API)
qwen "Check /Needs_Action folder and process all pending items according to Company_Handbook.md"
```

## 🧠 Using Qwen as the AI Brain

### Basic Commands

```bash
# Process pending items
qwen "Read all files in /Needs_Action and process them according to Company_Handbook.md rules"

# Update dashboard
qwen "Update Dashboard.md with current status of all folders"

# Create a plan for complex tasks
qwen "Create a Plan.md for processing the file drop items"

# Summarize activity
qwen "Summarize what's in the /Done folder from today"
```

### Qwen Integration Pattern

1. **Watcher detects** → Creates action file in `/Needs_Action/`
2. **Qwen reads** → Processes the action file content
3. **Qwen acts** → Updates Dashboard, moves files, creates logs
4. **Human approves** → For sensitive actions in `/Pending_Approval/`

## 📋 Agent Skills (Bronze Tier)

| Skill | Description |
|-------|-------------|
| Inbox Intake | Process files dropped in /Inbox |
| Task Classifier | Categorize items by type and priority |
| Task Summarizer | Create summaries for Dashboard |
| Dashboard Updater | Keep Dashboard.md current |
| Task State Mover | Move tasks between folders |
| Duplicate Detector | Prevent reprocessing |
| Completion Evaluator | Verify task completion |

See `AI_Employee_Vault/Agent_Skills.md` for details.

## 🔄 Workflow Example

```
1. User drops file: /Inbox/report.pdf
2. Watcher detects → Creates:
   - /Needs_Action/FILE_abc123_report.pdf (copy)
   - /Needs_Action/FILE_abc123.md (metadata)
3. Qwen processes:
   - Reads metadata file
   - Classifies as "file_drop"
   - Takes appropriate action
   - Moves to /Done/report.pdf
   - Updates Dashboard.md
4. Human reviews Dashboard for summary
```

## ⚙️ Configuration

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--vault` | `./AI_Employee_Vault` | Path to vault |
| `--interval` | `30` | Check interval (seconds) |
| `--debug` | `false` | Enable debug logs |

### Environment Variables

```bash
# Optional: Set log level
export LOG_LEVEL=DEBUG

# Optional: Custom vault path
export AI_EMPLOYEE_VAULT=/path/to/vault
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src
```

## 📝 Key Files Explained

### Dashboard.md
Real-time overview of system status, pending tasks, and recent activity.

### Company_Handbook.md
Rules and guidelines for Qwen's decision-making process.

### Agent_Skills.md
Documentation of all available AI capabilities.

## 🔒 Security Notes (Bronze Tier)

- **No external API calls** - Everything runs locally
- **No credentials stored** - Pure file system operations
- **Human approval required** - All actions are reviewable
- **Audit trail** - All movements logged in Dashboard

## 🐛 Troubleshooting

### Watcher not detecting files
- Ensure file is not a `.md` file (those are metadata files)
- Check watcher logs for errors
- Verify vault path is correct

### Qwen not processing correctly
- Check Company_Handbook.md for rules
- Ensure action files have proper frontmatter
- Review Logs folder for error details

## 📈 Next Steps (Silver Tier)

After mastering Bronze Tier, consider adding:
- Gmail Watcher for email monitoring
- WhatsApp Watcher for message monitoring
- MCP Servers for external actions
- Human-in-the-loop approval workflow
- Scheduled tasks via cron

## 📄 License

MIT License - See LICENSE file for details.

---

*Built for the Personal AI Employee Hackathon 2026*
*Powered by Qwen*
