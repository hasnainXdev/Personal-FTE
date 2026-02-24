#!/bin/bash
# Silver Tier - Complete Test & Run Script
# 
# Usage:
#   ./run_all.sh              # Run full test suite
#   ./run_all.sh test         # Run sandbox tests only
#   ./run_all.sh run          # Start all components
#   ./run_all.sh demo         # Run demo workflow
#   ./run_all.sh clean        # Clean test artifacts
#   ./run_all.sh help         # Show help

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$PROJECT_ROOT/AI_Employee_Vault"
VENVActivate="$PROJECT_ROOT/.venv/bin/activate"

# Functions
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}${1:^60}${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_venv() {
    if [ ! -f "$VENVActivate" ]; then
        print_error "Virtual environment not found!"
        print_info "Run: uv venv && source .venv/bin/activate"
        exit 1
    fi
    source "$VENVActivate"
}

run_tests() {
    print_header "🛡️ Running Sandbox Tests"
    
    check_venv
    
    cd "$PROJECT_ROOT"
    python test_sandbox.py --verbose
    
    if [ $? -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed!"
        exit 1
    fi
}

run_mcp_server() {
    print_header "🚀 Starting MCP Server"
    
    check_venv
    
    cd "$PROJECT_ROOT"
    
    # Check if already running
    if curl -s http://localhost:8765/health > /dev/null 2>&1; then
        print_warning "MCP Server already running"
        curl -s http://localhost:8765/health | python3 -m json.tool
        return 0
    fi
    
    print_info "Starting MCP Server on http://localhost:8765"
    python -m ai_employee.mcp_server.server &
    MCP_PID=$!
    
    # Wait for server
    print_info "Waiting for server to start..."
    for i in {1..10}; do
        if curl -s http://localhost:8765/health > /dev/null 2>&1; then
            print_success "MCP Server started (PID: $MCP_PID)"
            curl -s http://localhost:8765/health | python3 -m json.tool
            return 0
        fi
        sleep 1
    done
    
    print_error "Failed to start MCP Server"
    exit 1
}

run_demo() {
    print_header "🎬 Running Demo Workflow"
    
    check_venv
    cd "$PROJECT_ROOT"
    
    # Ensure MCP is running
    if ! curl -s http://localhost:8765/health > /dev/null 2>&1; then
        run_mcp_server
    fi
    
    echo ""
    echo "Step 1: Create test input file"
    echo "--------------------------------"
    TEST_FILE="$VAULT_DIR/Inbox_Drop/demo_test_$(date +%s).txt"
    echo "Demo workflow test - $(date)" > "$TEST_FILE"
    print_success "Created: $TEST_FILE"
    
    echo ""
    echo "Step 2: Run Filesystem Watcher"
    echo "-------------------------------"
    python -m ai_employee.watchers.filesystem_watcher --test
    print_success "Watcher completed"
    
    echo ""
    echo "Step 3: Generate Plan"
    echo "---------------------"
    python -m ai_employee.services.plan_generator
    print_success "Plan generated"
    
    echo ""
    echo "Step 4: Create Approval Request"
    echo "--------------------------------"
    python -m ai_employee.services.approval_request
    print_success "Approval request created"
    
    echo ""
    echo "Step 5: Mock LinkedIn Post"
    echo "--------------------------"
    python -m ai_employee.mcp_server.actions.linkedin_mock_test --test
    print_success "Mock post created"
    
    echo ""
    echo "Step 6: Check Scheduler"
    echo "-----------------------"
    python -m ai_employee.scheduler.cron_runner --check
    print_success "Scheduler checked"
    
    echo ""
    print_header "✅ Demo Workflow Complete"
    
    print_info "Check these directories for results:"
    echo "  - Inbox:          $VAULT_DIR/Inbox/"
    echo "  - Plans:          $VAULT_DIR/Plans/"
    echo "  - Proposed:       $VAULT_DIR/Proposed_Actions/"
    echo "  - Done:           $VAULT_DIR/Done/"
    echo "  - Logs:           $VAULT_DIR/Logs_Extended/"
    echo ""
}

run_all() {
    print_header "🚀 Starting All Silver Tier Components"
    
    check_venv
    cd "$PROJECT_ROOT"
    
    # Test first
    run_tests
    
    # Start MCP
    run_mcp_server
    
    # Run demo
    run_demo
    
    print_header "📊 Summary"
    
    print_info "MCP Server Status:"
    curl -s http://localhost:8765/health | python3 -m json.tool
    
    print_info "MCP Available Actions:"
    curl -s http://localhost:8765/actions | python3 -m json.tool
    
    print_info "Vault Structure:"
    for dir in Inbox_Drop Inbox Plans Proposed_Actions Done Logs_Extended Scheduled_Tasks; do
        COUNT=$(find "$VAULT_DIR/$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        echo "  $dir: $COUNT files"
    done
    
    print_header "✅ All Components Ready"
    
    print_warning "MCP Server is running in background"
    print_info "To stop: kill %1  or  pkill -f mcp_server"
}

clean_artifacts() {
    print_header "🧹 Cleaning Test Artifacts"
    
    cd "$PROJECT_ROOT"
    
    # Clean test files
    rm -f "$VAULT_DIR/Inbox_Drop/test_"*.txt 2>/dev/null || true
    rm -f "$VAULT_DIR/Inbox_Drop/demo_test_"*.txt 2>/dev/null || true
    rm -f "$VAULT_DIR/Inbox_Drop/load_test_"*.txt 2>/dev/null || true
    rm -f "$VAULT_DIR/Inbox_Drop/sandbox_test_"*.txt 2>/dev/null || true
    
    # Clean generated files (keep structure)
    rm -f "$VAULT_DIR/Inbox/FILE_"*.md 2>/dev/null || true
    rm -f "$VAULT_DIR/Plans/Plan_"*.md 2>/dev/null || true
    rm -f "$VAULT_DIR/Plans/LinkedIn_Draft_"*.md 2>/dev/null || true
    rm -f "$VAULT_DIR/Proposed_Actions/Action_"*.md 2>/dev/null || true
    rm -f "$VAULT_DIR/Done/LinkedIn_Post_"*.md 2>/dev/null || true
    
    # Clean logs
    rm -f "$VAULT_DIR/Logs_Extended/watcher_"*.md 2>/dev/null || true
    
    # Clean MCP logs
    rm -f "$PROJECT_ROOT/ai_employee/mcp_server/logs/mcp_actions.md" 2>/dev/null || true
    
    print_success "Cleaned test artifacts"
    print_info "Vault structure preserved"
}

show_help() {
    cat << 'EOF'
Silver Tier - Complete Run & Test Script

USAGE:
    ./run_all.sh [COMMAND]

COMMANDS:
    test        Run sandbox test suite (100% safe, no external APIs)
    run         Start all components (MCP + run demo)
    mcp         Start MCP Server only
    demo        Run demo workflow (requires MCP running)
    clean       Clean test artifacts
    help        Show this help message

EXAMPLES:
    # Run all tests
    ./run_all.sh test
    
    # Start everything
    ./run_all.sh run
    
    # Just start MCP Server
    ./run_all.sh mcp
    
    # Run demo workflow
    ./run_all.sh demo
    
    # Clean up test files
    ./run_all.sh clean

SAFETY:
    All tests run in sandbox mode - NO external API calls.
    See SECURITY_COMPLIANCE.md for details.

DOCUMENTATION:
    - RUN_GUIDE.md           - Complete run guide
    - SECURITY_COMPLIANCE.md - Security & testing guidelines
    - README.md              - Project overview

EOF
}

# Main
case "${1:-run}" in
    test)
        run_tests
        ;;
    run)
        run_all
        ;;
    mcp)
        run_mcp_server
        ;;
    demo)
        run_demo
        ;;
    clean)
        clean_artifacts
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
