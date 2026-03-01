#!/usr/bin/env python3
"""
AI Employee - Production Setup Wizard

This interactive wizard helps you configure credentials for production use.

Usage:
    python setup_wizard.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
ENV_FILE = PROJECT_ROOT / ".env"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.RESET}")


def get_input(prompt, default=None, required=False, secret=False):
    """Get user input with validation"""
    while True:
        if default:
            value = input(f"{prompt} [{default}]: ").strip()
        else:
            value = input(f"{prompt}: ").strip()
        
        if not value and default:
            return default
        elif not value and required:
            print_error("This field is required")
            continue
        else:
            return value


def load_env_example():
    """Load .env.example as template"""
    if not ENV_EXAMPLE.exists():
        return {}
    
    config = {}
    content = ENV_EXAMPLE.read_text()
    
    for line in content.split('\n'):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    
    return config


def save_env(config):
    """Save configuration to .env"""
    header = f"""# AI Employee Silver Tier - Environment Configuration
# Generated: {datetime.now().isoformat()}
# 
# SECURITY: Keep this file private! Never commit to git.
# Run 'chmod 600 .env' to restrict access.

"""
    
    content = header
    
    for key, value in config.items():
        if value:
            content += f"{key}={value}\n"
        else:
            content += f"# {key}=\n"
    
    ENV_FILE.write_text(content)
    
    # Set restrictive permissions (Unix only)
    if os.name != 'nt':
        os.chmod(ENV_FILE, 0o600)
        print_success(f"Set restrictive permissions (600) on {ENV_FILE}")


def configure_linkedin():
    """Configure LinkedIn API credentials"""
    print_header("🔗 LinkedIn API Configuration")
    
    print_info("LinkedIn is required for automated posting.")
    print_info("Don't have API access? Use manual workflow (skip this step).")
    print()
    
    config = {}
    
    use_linkedin = get_input(
        "Do you want to configure LinkedIn API? (y/n)",
        default="n"
    ).lower()
    
    if use_linkedin != 'y':
        print_warning("Skipping LinkedIn configuration")
        print_info("You can use the manual workflow:")
        print_info("  python -m ai_employee.mcp_server.actions.linkedin_mock_test --test")
        return config
    
    print()
    print_info("Get your credentials from: https://www.linkedin.com/developers/")
    print()
    
    config['LINKEDIN_CLIENT_ID'] = get_input(
        "LinkedIn Client ID",
        required=False
    )
    
    config['LINKEDIN_CLIENT_SECRET'] = get_input(
        "LinkedIn Client Secret",
        required=False,
        secret=True
    )
    
    config['LINKEDIN_ACCESS_TOKEN'] = get_input(
        "LinkedIn Access Token",
        required=False,
        secret=True
    )
    
    config['LINKEDIN_ORGANIZATION_ID'] = get_input(
        "LinkedIn Organization ID (optional, for company pages)",
        default=""
    )
    
    print_success("LinkedIn configuration saved")
    return config


def configure_gmail():
    """Configure Gmail API credentials"""
    print_header("📧 Gmail API Configuration")
    
    print_info("Gmail API is required for reading emails automatically.")
    print_info("Alternative: Use Filesystem Watcher (already configured).")
    print()
    
    config = {}
    
    use_gmail = get_input(
        "Do you want to configure Gmail API? (y/n)",
        default="n"
    ).lower()
    
    if use_gmail != 'y':
        print_warning("Skipping Gmail configuration")
        print_info("Filesystem Watcher will be used for input")
        return config
    
    print()
    print_info("Get your credentials from: https://console.cloud.google.com/")
    print()
    
    config['GMAIL_CLIENT_ID'] = get_input(
        "Gmail Client ID",
        required=False
    )
    
    config['GMAIL_CLIENT_SECRET'] = get_input(
        "Gmail Client Secret",
        required=False,
        secret=True
    )
    
    config['GMAIL_OAUTH_TOKEN'] = get_input(
        "Gmail OAuth Token (run OAuth setup flow)",
        required=False,
        secret=True
    )
    
    config['GMAIL_REFRESH_TOKEN'] = get_input(
        "Gmail Refresh Token",
        required=False,
        secret=True
    )
    
    print_success("Gmail configuration saved")
    return config


def configure_smtp():
    """Configure SMTP credentials for sending emails"""
    print_header("📤 SMTP Configuration")
    
    print_info("SMTP is required for sending emails.")
    print_info("For Gmail: Use App Password, NOT your regular password!")
    print()
    
    config = {}
    
    use_smtp = get_input(
        "Do you want to configure SMTP? (y/n)",
        default="y"
    ).lower()
    
    if use_smtp != 'y':
        print_warning("Skipping SMTP configuration")
        return config
    
    print()
    print_info("Gmail App Password: https://myaccount.google.com/apppasswords")
    print("Other providers:")
    print("  - Outlook: smtp.office365.com:587")
    print("  - SendGrid: smtp.sendgrid.net:587")
    print()
    
    config['SMTP_HOST'] = get_input(
        "SMTP Host",
        default="smtp.gmail.com"
    )
    
    config['SMTP_PORT'] = get_input(
        "SMTP Port",
        default="587"
    )
    
    config['SMTP_USER'] = get_input(
        "SMTP Username (email)",
        required=True
    )
    
    config['SMTP_PASS'] = get_input(
        "SMTP Password (App Password for Gmail)",
        required=True,
        secret=True
    )
    
    print_success("SMTP configuration saved")
    return config


def configure_security():
    """Configure security settings"""
    print_header("🔒 Security Configuration")
    
    config = {}
    
    sandbox_mode = get_input(
        "Enable SANDBOX_MODE? (y/n) - Recommended for testing",
        default="y"
    ).lower()
    
    config['SANDBOX_MODE'] = 'true' if sandbox_mode == 'y' else 'false'
    
    if config['SANDBOX_MODE'] == 'false':
        print_warning("Sandbox mode disabled - real API calls will be made!")
    
    config['MCP_HOST'] = get_input(
        "MCP Server Host",
        default="localhost"
    )
    
    config['MCP_PORT'] = get_input(
        "MCP Server Port",
        default="8765"
    )
    
    config['LOG_LEVEL'] = get_input(
        "Log Level",
        default="INFO"
    )
    
    print_success("Security configuration saved")
    return config


def test_configuration(config):
    """Test the configuration"""
    print_header("🧪 Testing Configuration")
    
    if not config:
        print_warning("No configuration to test")
        return
    
    # Check if MCP Server is running
    import httpx
    
    try:
        response = httpx.get(f"http://{config.get('MCP_HOST', 'localhost')}:{config.get('MCP_PORT', '8765')}/health", timeout=3.0)
        if response.status_code == 200:
            print_success("MCP Server is running")
            print_info(f"Response: {response.json()}")
        else:
            print_error("MCP Server returned unexpected status")
    except Exception as e:
        print_error(f"MCP Server not reachable: {e}")
        print_info("Start it with: python -m ai_employee.mcp_server.server")
    
    print()
    print_info("Next steps:")
    if config.get('SANDBOX_MODE') == 'true':
        print_success("✓ Sandbox mode enabled - safe for testing")
        print("  Run: python test_sandbox.py")
    else:
        print_warning("⚠ Sandbox mode disabled - real API calls will be made")
        print("  Test with mock first: python -m ai_employee.mcp_server.actions.linkedin_mock_test --test")
    
    print()
    print_info("Configuration file saved to:")
    print(f"  {ENV_FILE}")
    print()
    print_info("To apply changes, restart MCP Server:")
    print("  pkill -f mcp_server")
    print("  python -m ai_employee.mcp_server.server")


def main():
    print_header("🤖 AI Employee Production Setup Wizard")
    
    print_info("This wizard will help you configure credentials for production use.")
    print_info("All values are optional - you can configure services later.")
    print()
    
    # Load existing config
    config = {}
    
    if ENV_FILE.exists():
        print_warning(f"Found existing .env file: {ENV_FILE}")
        overwrite = get_input("Overwrite existing configuration? (y/n)", default="n")
        
        if overwrite.lower() == 'y':
            print_info("Loading existing configuration...")
            config = load_env_example()
        else:
            print_info("Keeping existing configuration")
            return
    
    # Configure services
    config.update(configure_linkedin())
    config.update(configure_gmail())
    config.update(configure_smtp())
    config.update(configure_security())
    
    # Save configuration
    print_header("💾 Saving Configuration")
    
    save_env(config)
    print_success(f"Configuration saved to: {ENV_FILE}")
    
    # Test configuration
    test_configuration(config)
    
    print_header("✅ Setup Complete!")
    
    print()
    print("Quick Start:")
    print("  1. Test sandbox:     python test_sandbox.py")
    print("  2. Start MCP Server: python -m ai_employee.mcp_server.server")
    print("  3. Run demo:         ./run_all.sh demo")
    print()
    print("Documentation:")
    print("  - RUN_GUIDE.md             - How to run components")
    print("  - PRODUCTION_READINESS.md  - Production setup guide")
    print("  - SECURITY_COMPLIANCE.md   - Security best practices")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
