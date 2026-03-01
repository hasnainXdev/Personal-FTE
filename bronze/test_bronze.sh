#!/bin/bash
# Test script for Bronze Tier

set -e

echo "🧪 Testing AI Employee Bronze Tier"
echo "==================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_PATH="$SCRIPT_DIR/AI_Employee_Vault"

# Clean up any previous test files
echo "🧹 Cleaning up previous test files..."
rm -f "$VAULT_PATH/Inbox"/*.txt 2>/dev/null || true
rm -f "$VAULT_PATH/Needs_Action"/FILE_*.md 2>/dev/null || true
rm -f "$VAULT_PATH/Needs_Action"/FILE_*.txt 2>/dev/null || true

echo ""
echo "📁 Vault structure:"
ls -la "$VAULT_PATH"
echo ""

# Test 1: Check required files exist
echo "✅ Test 1: Checking required files..."
for file in Dashboard.md Company_Handbook.md Agent_Skills.md Welcome.md; do
    if [ -f "$VAULT_PATH/$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file MISSING"
        exit 1
    fi
done
echo ""

# Test 2: Check folders exist
echo "📁 Test 2: Checking folders..."
for folder in Inbox Needs_Action Done Plans Pending_Approval Approved Rejected Logs Accounting Briefings; do
    if [ -d "$VAULT_PATH/$folder" ]; then
        echo "  ✓ /$folder exists"
    else
        echo "  ✗ /$folder MISSING"
        exit 1
    fi
done
echo ""

# Test 3: Drop a test file
echo "📝 Test 3: Dropping test file..."
TEST_CONTENT="This is a test file for the AI Employee Bronze Tier.
Created at: $(date)
Purpose: Test the FileSystemWatcher functionality."

echo "$TEST_CONTENT" > "$VAULT_PATH/Inbox/test_file_$(date +%Y%m%d_%H%M%S).txt"
echo "  ✓ Test file created in /Inbox"
echo ""

# Test 4: Run watcher for one cycle
echo "⏱️  Test 4: Running watcher for one cycle..."
cd "$SCRIPT_DIR"
timeout 5 python3 src/main.py --vault "$VAULT_PATH" --interval 1 2>&1 || true
echo ""

# Test 5: Check if action files were created
echo "📋 Test 5: Checking for action files..."
ACTION_FILES=$(ls -1 "$VAULT_PATH/Needs_Action"/*.md 2>/dev/null | wc -l)
COPIED_FILES=$(ls -1 "$VAULT_PATH/Needs_Action"/*.txt 2>/dev/null | wc -l)

if [ "$ACTION_FILES" -gt 0 ]; then
    echo "  ✓ Action files created: $ACTION_FILES"
    echo "  Files:"
    ls -1 "$VAULT_PATH/Needs_Action"/*.md 2>/dev/null | while read f; do echo "    - $(basename $f)"; done
else
    echo "  ✗ No action files created"
fi

if [ "$COPIED_FILES" -gt 0 ]; then
    echo "  ✓ Files copied: $COPIED_FILES"
else
    echo "  ✗ No files copied"
fi
echo ""

# Test 6: Show action file content
echo "📄 Test 6: Action file content sample..."
FIRST_MD=$(ls -1 "$VAULT_PATH/Needs_Action"/*.md 2>/dev/null | head -1)
if [ -n "$FIRST_MD" ]; then
    echo "  Content of $(basename $FIRST_MD):"
    echo "  ---"
    head -20 "$FIRST_MD" | sed 's/^/  /'
    echo "  ..."
else
    echo "  No .md files found"
fi
echo ""

echo "==================================="
echo "🎉 Test Complete!"
echo ""
echo "Next steps:"
echo "1. Review the action files in: $VAULT_PATH/Needs_Action/"
echo "2. Use Qwen to process: qwen 'Check /Needs_Action and process all items'"
echo "3. Check Dashboard.md for updates"
