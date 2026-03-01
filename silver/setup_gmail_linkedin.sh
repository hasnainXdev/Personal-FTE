#!/bin/bash
# Quick Setup Script for Gmail API + LinkedIn Playwright
# Run this to get started quickly

set -e

echo "============================================================"
echo "AI Employee - Gmail + LinkedIn Setup"
echo "============================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    uv sync
fi

# Activate virtual environment
source .venv/bin/activate

# Install Playwright browsers
echo -e "${BLUE}Installing Playwright browsers...${NC}"
uv run playwright install chromium

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
    echo -e "${YELLOW}⚠ Edit .env and add your credentials${NC}"
fi

# Create vault structure
echo -e "${BLUE}Setting up vault structure...${NC}"
mkdir -p AI_Employee_Vault/Skills
echo -e "${GREEN}✓ Vault structure ready${NC}"

echo ""
echo "============================================================"
echo "SETUP COMPLETE - Next Steps"
echo "============================================================"
echo ""
echo -e "${BLUE}1. GMAIL API SETUP:${NC}"
echo "   a) Go to https://console.cloud.google.com/"
echo "   b) Create project and enable Gmail API"
echo "   c) Create OAuth credentials (Web application)"
echo "   d) Add redirect URI: http://localhost:8085/callback"
echo "   e) Download JSON and save to: AI_Employee_Vault/Skills/gmail_credentials.json"
echo "   f) Run: python -m ai_employee.services.gmail_oauth"
echo ""
echo -e "${BLUE}2. LINKEDIN SETUP:${NC}"
echo "   a) Edit .env and add:"
echo "      LINKEDIN_EMAIL=your@email.com"
echo "      LINKEDIN_PASSWORD=your_password"
echo "   b) First run will auto-save session cookies"
echo ""
echo -e "${BLUE}3. TEST EVERYTHING:${NC}"
echo "   python test_integrations.py"
echo ""
echo -e "${YELLOW}For detailed instructions, see: GMAIL_LINKEDIN_SETUP.md${NC}"
echo ""
echo "============================================================"
