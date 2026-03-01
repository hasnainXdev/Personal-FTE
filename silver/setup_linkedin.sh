#!/bin/bash
# LinkedIn Setup Script for Silver Tier
# This script sets up Playwright for LinkedIn automation

set -e

echo "🔗 LinkedIn Setup for AI Employee Silver Tier"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}Step 1: Check Playwright Installation${NC}"
echo "-------------------------------------------"

if python3 -c "import playwright" 2>/dev/null; then
    echo -e "${GREEN}✓ Playwright is installed${NC}"
else
    echo -e "${YELLOW}⚠ Playwright not found - installing...${NC}"
    pip install playwright
fi

echo ""
echo -e "${BLUE}Step 2: Install Browsers${NC}"
echo "-------------------------------------------"

echo "Installing Chromium browser for Playwright..."
playwright install chromium

echo ""
echo -e "${GREEN}✓ Browsers installed${NC}"

echo ""
echo -e "${BLUE}Step 3: Test LinkedIn Service${NC}"
echo "-------------------------------------------"

cat > "$SCRIPT_DIR/test_linkedin.py" << 'EOF'
import asyncio
import sys
sys.path.insert(0, 'src')

from services.linkedin_service import LinkedInService

async def test():
    print("Initializing LinkedIn service...")
    service = LinkedInService('AI_Employee_Vault')
    
    print("Starting browser...")
    await service.initialize()
    
    print("Checking login status...")
    logged_in = await service.is_logged_in()
    
    if logged_in:
        print("\n✓ LinkedIn session valid!")
        print("You can now post updates.")
    else:
        print("\n⚠ Not logged in")
        print("\nOpening LinkedIn login page...")
        print("Please log in manually in the browser window.")
        print("After login, close the browser - session will be saved.")
        
        await service.login()
        
        # Wait for user to log in
        print("\nWaiting 60 seconds for login...")
        await asyncio.sleep(60)
        
        # Check again
        logged_in = await service.is_logged_in()
        if logged_in:
            print("\n✓ Login successful! Session saved.")
        else:
            print("\n⚠ Login not detected. Please run again.")
    
    await service.close()
    return logged_in

if __name__ == "__main__":
    result = asyncio.run(test())
    sys.exit(0 if result else 1)
EOF

echo "Running LinkedIn test..."
cd "$SCRIPT_DIR"
python3 test_linkedin.py

echo ""
echo -e "${GREEN}✓ LinkedIn setup complete!${NC}"

echo ""
echo "=================================================="
echo "Next steps:"
echo "1. Run: python3 src/main.py --vault ./AI_Employee_Vault --mode mcp"
echo "2. Use MCP tool 'post_linkedin' to create drafts"
echo "3. Approve drafts to post automatically"
echo ""
echo "For manual login test:"
echo "  python3 test_linkedin.py"
echo ""
