---
created: 2026-02-28
type: welcome
tier: silver
---

# 👋 Welcome to Your AI Employee Vault - Silver Tier

This is your **Personal AI Employee** knowledge base and control center, powered by **Qwen** as the reasoning engine.

## 🆕 What's New in Silver Tier

Silver Tier adds these capabilities to the Bronze foundation:

| Feature | Description |
|---------|-------------|
| 📧 Gmail Integration | Auto-monitor Gmail for important emails |
| 🔗 LinkedIn Posting | Schedule and post business updates |
| 📋 Multi-Step Plans | Automatic plan generation for complex tasks |
| ✅ Approval Workflow | Human-in-the-loop for sensitive actions |
| ⏰ Scheduled Tasks | Cron-based task scheduling |
| 📊 Daily Briefings | Automated business summaries |
| 🔌 MCP Server | External action capabilities |

## 📁 Folder Structure

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming files |
| `/Inbox_Drop` | Additional drop folder |
| `/Needs_Action` | Items requiring processing |
| `/Done` | Completed tasks archive |
| `/Plans` | Multi-step task plans |
| `/Pending_Approval` | Awaiting human approval |
| `/Approved` | Approved actions ready |
| `/Rejected` | Declined actions |
| `/Scheduled_Tasks` | Cron task definitions |
| `/Skills/Silver` | Silver-specific skills |
| `/Logs` | Activity logs |
| `/Logs_Extended` | Extended watcher state |
| `/Accounting` | Financial records |
| `/Briefings` | CEO briefings |

## 🚀 Quick Start

### 1. Start the System

```bash
# Terminal 1: Start watchers
python3 src/main.py --vault ./AI_Employee_Vault --mode watchers

# Terminal 2: Start scheduler
python3 src/main.py --vault ./AI_Employee_Vault --mode scheduler

# Terminal 3: Start MCP server
python3 src/main.py --vault ./AI_Employee_Vault --mode mcp
```

### 2. Configure Gmail (Optional)

```bash
# Place credentials.json in silver/ folder
cp /path/to/credentials.json ./credentials.json

# First run will open browser for OAuth
```

### 3. Test the System

```bash
# Drop a test file
echo "Test content" > AI_Employee_Vault/Inbox_Drop/test.txt

# Watcher will create action file in Needs_Action/
```

### 4. Process with Qwen

```bash
cd AI_Employee_Vault

# Process pending items
qwen "Check /Needs_Action and process all items according to Company_Handbook.md"

# Generate LinkedIn post
qwen "Generate a business post about our latest achievement"

# Check approvals
qwen "Check /Pending_Approval and summarize what needs my attention"
```

## 🧠 AI Brain: Qwen

This system uses **Qwen** as the primary reasoning engine:
- High-level reasoning and planning
- File system understanding
- Multi-step task completion
- Natural language processing
- MCP tool integration

## 📋 Key Files

- **Dashboard.md** - Real-time status overview
- **Company_Handbook.md** - AI behavior rules
- **Agent_Skills.md** - Available capabilities (14 skills)
- **Welcome.md** - This guide

## 🎯 Silver Tier Goals

- [x] All Bronze tier features
- [x] Gmail Watcher working
- [x] LinkedIn Poster working
- [x] MCP Server running
- [x] Plan Generator active
- [x] Approval workflow functional
- [x] Scheduler running
- [x] Daily briefings generating

## 🔄 Typical Workflow

```
1. Gmail Watcher detects important email
   ↓
2. Creates action file in /Needs_Action/
   ↓
3. Qwen reads and drafts response
   ↓
4. MCP creates approval request
   ↓
5. You approve (move to /Approved/)
   ↓
6. MCP sends email
   ↓
7. Dashboard updated automatically
```

## 📞 Support

- **Documentation**: See README.md
- **Skills**: See Agent_Skills.md
- **Rules**: See Company_Handbook.md
- **Qwen Prompts**: See QWEN_PROMPT_TEMPLATE.md

---

*Ready to start? Drop a file in /Inbox_Drop to begin!*

*Silver Tier - Powered by Qwen*
