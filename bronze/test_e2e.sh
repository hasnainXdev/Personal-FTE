#!/bin/bash
# Final End-to-End Test for Bronze Tier

set -e

echo "🎯 BRONZE TIER - END-TO-END TEST"
echo "================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_PATH="$SCRIPT_DIR/AI_Employee_Vault"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        fail_count=$((fail_count + 1))
    fi
}

# Test 1: Vault Structure
echo "📁 Test 1: Vault Structure"
echo "--------------------------"
for folder in Inbox Needs_Action Done Plans Pending_Approval Approved Rejected Logs Accounting Briefings; do
    if [ -d "$VAULT_PATH/$folder" ]; then
        test_result 0 "/$folder folder exists"
    else
        test_result 1 "/$folder folder missing"
    fi
done
echo ""

# Test 2: Core Files
echo "📄 Test 2: Core Files"
echo "---------------------"
for file in Dashboard.md Company_Handbook.md Agent_Skills.md Welcome.md; do
    if [ -f "$VAULT_PATH/$file" ]; then
        test_result 0 "$file exists"
    else
        test_result 1 "$file missing"
    fi
done
echo ""

# Test 3: Watcher Code
echo "⚙️  Test 3: Watcher Code"
echo "------------------------"
if [ -f "$SCRIPT_DIR/src/watchers/base_watcher.py" ]; then
    test_result 0 "base_watcher.py exists"
else
    test_result 1 "base_watcher.py missing"
fi

if [ -f "$SCRIPT_DIR/src/watchers/filesystem_watcher.py" ]; then
    test_result 0 "filesystem_watcher.py exists"
else
    test_result 1 "filesystem_watcher.py missing"
fi

if [ -f "$SCRIPT_DIR/src/main.py" ]; then
    test_result 0 "main.py entry point exists"
else
    test_result 1 "main.py missing"
fi
echo ""

# Test 4: Functional Test
echo "🔄 Test 4: Functional Test"
echo "--------------------------"

# Clean up
rm -f "$VAULT_PATH/Inbox"/*.txt 2>/dev/null || true
rm -f "$VAULT_PATH/Needs_Action"/FILE_* 2>/dev/null || true

# Create test file
TEST_FILE="$VAULT_PATH/Inbox/e2e_test_$(date +%Y%m%d_%H%M%S).txt"
echo "End-to-end test file" > "$TEST_FILE"
test_result 0 "Created test file in /Inbox"

# Run watcher
cd "$SCRIPT_DIR"
timeout 3 python3 src/main.py --vault "$VAULT_PATH" --interval 1 2>&1 > /dev/null

# Check results
ACTION_FILES=$(ls -1 "$VAULT_PATH/Needs_Action"/FILE_*.md 2>/dev/null | wc -l)
if [ "$ACTION_FILES" -gt 0 ]; then
    test_result 0 "Action file created ($ACTION_FILES files)"
else
    test_result 1 "No action file created"
fi

COPIED_FILES=$(ls -1 "$VAULT_PATH/Needs_Action"/FILE_*.txt 2>/dev/null | wc -l)
if [ "$COPIED_FILES" -gt 0 ]; then
    test_result 0 "File copied to Needs_Action ($COPIED_FILES files)"
else
    test_result 1 "File not copied"
fi
echo ""

# Test 5: Action File Format
echo "📋 Test 5: Action File Format"
echo "------------------------------"
FIRST_MD=$(ls -1 "$VAULT_PATH/Needs_Action"/FILE_*.md 2>/dev/null | head -1)
if [ -n "$FIRST_MD" ]; then
    content=$(cat "$FIRST_MD")
    
    if echo "$content" | grep -q "type: file_drop"; then
        test_result 0 "Has type frontmatter"
    else
        test_result 1 "Missing type frontmatter"
    fi
    
    if echo "$content" | grep -q "priority:"; then
        test_result 0 "Has priority field"
    else
        test_result 1 "Missing priority field"
    fi
    
    if echo "$content" | grep -q "status: pending"; then
        test_result 0 "Has status field"
    else
        test_result 1 "Missing status field"
    fi
    
    if echo "$content" | grep -q "Instructions for Qwen"; then
        test_result 0 "Has Qwen instructions"
    else
        test_result 1 "Missing Qwen instructions"
    fi
else
    test_result 1 "No action file to check"
fi
echo ""

# Test 6: Documentation
echo "📚 Test 6: Documentation"
echo "------------------------"
if [ -f "$SCRIPT_DIR/README.md" ]; then
    test_result 0 "README.md exists"
else
    test_result 1 "README.md missing"
fi

if [ -f "$SCRIPT_DIR/QWEN_PROMPT_TEMPLATE.md" ]; then
    test_result 0 "Qwen prompt template exists"
else
    test_result 1 "Qwen prompt template missing"
fi

if [ -f "$SCRIPT_DIR/VALIDATION.md" ]; then
    test_result 0 "Validation checklist exists"
else
    test_result 1 "Validation checklist missing"
fi
echo ""

# Summary
echo "================================="
echo "📊 TEST SUMMARY"
echo "================================="
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "Bronze Tier is COMPLETE and ready for use!"
    echo ""
    echo "Next steps:"
    echo "1. Review QWEN_PROMPT_TEMPLATE.md for Qwen integration"
    echo "2. Run ./run_watcher.sh to start the watcher"
    echo "3. Drop files in AI_Employee_Vault/Inbox to test"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please fix the failing tests above."
    exit 1
fi
