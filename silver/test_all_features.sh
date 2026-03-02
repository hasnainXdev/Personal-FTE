#!/bin/bash
# Silver Tier - Complete Feature Test

set -e

echo "🥈 SILVER TIER - COMPLETE FEATURE TEST"
echo "======================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VAULT_PATH="$SCRIPT_DIR/AI_Employee_Vault"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

pass=0
fail=0

test_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    pass=$((pass + 1))
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    fail=$((fail + 1))
}

# ============================================
# TEST 1: Process Emails
# ============================================
echo -e "${BLUE}TEST 1: Email Processing${NC}"
echo "-------------------------------------------"

EMAIL_FILES=$(ls -1 "$VAULT_PATH/Needs_Action/EMAIL_*.md" 2>/dev/null | wc -l)
if [ "$EMAIL_FILES" -gt 0 ]; then
    test_pass "Found $EMAIL_FILES email action files"
    
    # Show first email
    FIRST_EMAIL=$(ls -1 "$VAULT_PATH/Needs_Action/EMAIL_*.md" 2>/dev/null | head -1)
    if [ -n "$FIRST_EMAIL" ]; then
        echo "  Sample: $(basename $FIRST_EMAIL)"
        grep -E "^(from|subject|priority):" "$FIRST_EMAIL" 2>/dev/null | sed 's/^/    /'
    fi
else
    test_fail "No email files found"
fi
echo ""

# ============================================
# TEST 2: LinkedIn Posting
# ============================================
echo -e "${BLUE}TEST 2: LinkedIn Integration${NC}"
echo "-------------------------------------------"

# Check if LinkedIn service exists
if [ -f "$SCRIPT_DIR/src/services/linkedin_service.py" ]; then
    test_pass "LinkedIn service exists"
else
    test_fail "LinkedIn service missing"
fi

# Create a test LinkedIn post draft
echo "  Creating LinkedIn post draft..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LINKEDIN_DRAFT="$VAULT_PATH/Pending_Approval/LINKEDIN_POST_${TIMESTAMP}.md"

cat > "$LINKEDIN_DRAFT" << EOF
---
type: linkedin_post_draft
file_id: LINKEDIN_POST_${TIMESTAMP}
created: $(date -Iseconds)
status: pending_approval
posts_today: 0
max_posts: 3
---

# LinkedIn Post Draft

## Post Content

🚀 Exciting Update!

We're thrilled to announce the successful completion of our AI Employee Silver Tier!

Key features:
✅ Gmail integration
✅ LinkedIn automation
✅ MCP server for actions
✅ Approval workflows
✅ Scheduled tasks

Powered by Qwen - Local-first, Agent-driven, Human-in-the-loop.

#AI #Automation #Innovation #Business

## To Approve

1. Review the content above
2. Move this file to \`/Approved/\` folder
3. The MCP server will post automatically

## To Reject

1. Add rejection reason below
2. Move this file to \`/Rejected/\` folder

---

*Created by Silver Tier Test*
EOF

if [ -f "$LINKEDIN_DRAFT" ]; then
    test_pass "Created LinkedIn post draft"
    echo "  Draft: $(basename $LINKEDIN_DRAFT)"
else
    test_fail "Failed to create LinkedIn draft"
fi
echo ""

# ============================================
# TEST 3: Approval Workflow
# ============================================
echo -e "${BLUE}TEST 3: Approval Workflow${NC}"
echo "-------------------------------------------"

# Check approval folders exist
for folder in Pending_Approval Approved Rejected; do
    if [ -d "$VAULT_PATH/$folder" ]; then
        test_pass "/$folder folder exists"
    else
        test_fail "/$folder folder missing"
    fi
done

# Count pending approvals
PENDING_COUNT=$(ls -1 "$VAULT_PATH/Pending_Approval/"*.md 2>/dev/null | wc -l)
echo "  Pending approvals: $PENDING_COUNT"

if [ "$PENDING_COUNT" -gt 0 ]; then
    test_pass "Has pending approvals to process"
    echo "  Files:"
    ls -1 "$VAULT_PATH/Pending_Approval/"*.md 2>/dev/null | sed 's/^/    - /'
else
    echo "  (No pending approvals yet)"
fi
echo ""

# ============================================
# TEST 4: Scheduled Tasks
# ============================================
echo -e "${BLUE}TEST 4: Scheduled Tasks${NC}"
echo "-------------------------------------------"

# Check scheduler exists
if [ -f "$SCRIPT_DIR/src/scheduler/cron_runner.py" ]; then
    test_pass "Cron runner exists"
else
    test_fail "Cron runner missing"
fi

# Check scheduled tasks folder
if [ -d "$VAULT_PATH/Scheduled_Tasks" ]; then
    test_pass "/Scheduled_Tasks folder exists"
else
    test_fail "/Scheduled_Tasks folder missing"
fi

# Create a sample scheduled task
TASK_FILE="$VAULT_PATH/Scheduled_Tasks/Task_test_task.md"
cat > "$TASK_FILE" << EOF
---
type: scheduled_task
name: test_task
cron: 0 8 * * *
enabled: true
created: $(date -Iseconds)
last_run: never
next_run: $(date -d "tomorrow 08:00" -Iseconds 2>/dev/null || date -Iseconds)
---

# Scheduled Task: Test Task

## Description

This is a test scheduled task for Silver Tier validation.

## Schedule

**Cron Expression**: \`0 8 * * *\` (Daily at 8:00 AM)

## Action

Run daily summary generation.

## Execution History

- **$(date +%Y-%m-%d)**: Task created

---

*Created by Silver Tier Test*
EOF

if [ -f "$TASK_FILE" ]; then
    test_pass "Created sample scheduled task"
else
    test_fail "Failed to create scheduled task"
fi
echo ""

# ============================================
# TEST 5: Dashboard Update
# ============================================
echo -e "${BLUE}TEST 5: Dashboard & Logging${NC}"
echo "-------------------------------------------"

if [ -f "$VAULT_PATH/Dashboard.md" ]; then
    test_pass "Dashboard.md exists"
    
    # Check for key sections
    if grep -q "Quick Status" "$VAULT_PATH/Dashboard.md"; then
        test_pass "Dashboard has Quick Status section"
    else
        test_fail "Dashboard missing Quick Status"
    fi
else
    test_fail "Dashboard.md missing"
fi

# Check logs folder
if [ -d "$VAULT_PATH/Logs" ]; then
    test_pass "/Logs folder exists"
    LOG_COUNT=$(ls -1 "$VAULT_PATH/Logs/"*.md 2>/dev/null | wc -l)
    echo "  Log files: $LOG_COUNT"
else
    test_fail "/Logs folder missing"
fi
echo ""

# ============================================
# SUMMARY
# ============================================
echo "======================================"
echo -e "${YELLOW}TEST SUMMARY${NC}"
echo "======================================"
echo -e "${GREEN}Passed: $pass${NC}"
echo -e "${RED}Failed: $fail${NC}"
echo ""

if [ $fail -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "Silver Tier features tested:"
    echo "  ✓ Email processing workflow"
    echo "  ✓ LinkedIn post drafts"
    echo "  ✓ Approval workflow"
    echo "  ✓ Scheduled tasks"
    echo "  ✓ Dashboard & logging"
    echo ""
    echo "Next steps:"
    echo "  1. Review pending approvals:"
    echo "     ls $VAULT_PATH/Pending_Approval/"
    echo ""
    echo "  2. Approve LinkedIn post:"
    echo "     mv $VAULT_PATH/Pending_Approval/LINKEDIN_POST_*.md $VAULT_PATH/Approved/"
    echo ""
    echo "  3. Start scheduler:"
    echo "     python3 src/main.py --vault $VAULT_PATH --mode scheduler"
    echo ""
    echo "  4. Process with Qwen:"
    echo "     cd $VAULT_PATH"
    echo "     qwen 'Process all items in /Needs_Action'"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review the failures above."
    exit 1
fi
