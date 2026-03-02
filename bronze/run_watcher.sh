#!/bin/bash
# Quick start script for Bronze Tier AI Employee

set -e

echo "🤖 AI Employee - Bronze Tier"
echo "============================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_PATH="$SCRIPT_DIR/AI_Employee_Vault"

echo "Vault: $VAULT_PATH"
echo ""

# Check if vault exists
if [ ! -d "$VAULT_PATH" ]; then
    echo "❌ Vault not found! Creating..."
    mkdir -p "$VAULT_PATH"/{Inbox,Needs_Action,Done,Plans,Pending_Approval,Approved,Rejected,Logs,Accounting,Briefings}
fi

# Check for required files
echo "📋 Checking vault structure..."
for file in Dashboard.md Company_Handbook.md Agent_Skills.md Welcome.md; do
    if [ -f "$VAULT_PATH/$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ⚠️  $file (missing)"
    fi
done

echo ""
echo "🚀 Starting File System Watcher..."
echo "   - Monitoring: $VAULT_PATH/Inbox"
echo "   - Check interval: 30 seconds"
echo "   - Press Ctrl+C to stop"
echo ""

# Run the watcher
cd "$SCRIPT_DIR"
python src/main.py --vault "$VAULT_PATH" --interval 30
