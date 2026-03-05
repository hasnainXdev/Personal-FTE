"""
Gold Tier AI Employee - Main Module

Main entry point and orchestrator.
Matches Silver tier structure + Gold features (Odoo, Facebook)
"""

import argparse
import logging
import sys
from pathlib import Path

from .watchers import FileSystemWatcher, GmailWatcher
from .scheduler import TaskScheduler
from .scheduler.tasks import (
    generate_daily_briefing,
    generate_weekly_audit,
    update_dashboard,
)
from .utils import setup_logging


logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False):
    """Configure logging."""
    level = logging.DEBUG if debug else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level, format=format_str)


def run_watchers(vault_path: str, interval: int = 30):
    """Run all watchers."""
    vault = Path(vault_path)
    
    if not vault.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    logger.info("Starting Gold Tier Watchers")
    logger.info(f"Vault: {vault.absolute()}")
    
    # File system watcher (always enabled) - uses 1 second interval internally
    fs_watcher = FileSystemWatcher(str(vault))
    logger.info("File system watcher initialized")
    
    # Gmail watcher (requires credentials)
    credentials_path = vault.parent / "credentials.json"
    gmail_watcher = None
    if credentials_path.exists():
        gmail_watcher = GmailWatcher(
            str(vault), str(credentials_path), check_interval=120
        )
        logger.info("Gmail watcher initialized")
    else:
        logger.warning("Gmail credentials not found. Gmail watcher disabled.")
    
    # Run watchers
    try:
        logger.info("Starting file system watcher...")
        fs_watcher.run()
    except KeyboardInterrupt:
        logger.info("Watchers stopped by user")
    except Exception as e:
        logger.error(f"Watcher failed: {e}")
        sys.exit(1)


def run_scheduler(vault_path: str):
    """Run the task scheduler."""
    import asyncio
    
    vault = Path(vault_path)
    scheduler = TaskScheduler(str(vault))
    
    # Register daily briefing (8:00 AM daily)
    scheduler.add_task(
        name='daily_briefing',
        cron_expression='0 8 * * *',
        callback=lambda: generate_daily_briefing(str(vault)),
        enabled=True,
    )
    
    # Register weekly audit (Sunday 6:00 PM)
    scheduler.add_task(
        name='weekly_audit',
        cron_expression='0 18 * * 0',
        callback=lambda: generate_weekly_audit(str(vault)),
        enabled=True,
    )
    
    # Register dashboard update (every hour)
    scheduler.add_task(
        name='dashboard_update',
        cron_expression='0 * * * *',
        callback=lambda: update_dashboard(str(vault)),
        enabled=True,
    )
    
    try:
        logger.info("Starting scheduler...")
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        sys.exit(1)


def run_mcp_server(vault_path: str):
    """Run the MCP server."""
    import subprocess
    
    logger.info(f"Starting MCP server for vault: {vault_path}")
    
    mcp_server_path = Path(__file__).parent / "mcp_server.py"
    
    try:
        subprocess.run([sys.executable, str(mcp_server_path), vault_path], check=True)
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP server failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Employee Gold Tier - Orchestrator"
    )
    
    parser.add_argument(
        "--vault", "-v",
        type=str,
        default="./AI_Employee_Vault",
        help="Path to Obsidian vault"
    )
    
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Watcher check interval in seconds"
    )
    
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["watchers", "scheduler", "mcp", "all"],
        default="watchers",
        help="Run mode"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.debug)
    
    if args.mode == "watchers":
        run_watchers(args.vault, args.interval)
    elif args.mode == "scheduler":
        run_scheduler(args.vault)
    elif args.mode == "mcp":
        run_mcp_server(args.vault)
    elif args.mode == "all":
        logger.warning("'all' mode not implemented. Run components separately.")
        logger.info("Start watchers: python main.py --mode watchers")
        logger.info("Start scheduler: python main.py --mode scheduler")
        logger.info("Start MCP: python main.py --mode mcp")


if __name__ == "__main__":
    main()
