#!/usr/bin/env python3
"""Main entry point for AI Employee Silver Tier."""

import argparse
import logging
import sys
import asyncio
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from watchers import FileSystemWatcher, GmailWatcher
from services import LinkedInService, ApprovalService, PlanService
from scheduler import CronRunner, DailySummary


def setup_logging(debug: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level, format=format_str, handlers=[logging.StreamHandler(sys.stdout)]
    )


def run_watchers(vault_path: str, interval: int):
    """Run all watchers."""
    logger = logging.getLogger("main")

    vault = Path(vault_path)
    if not vault.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)

    logger.info(f"Starting Silver Tier Watchers")
    logger.info(f"Vault: {vault.absolute()}")

    # Create watchers
    fs_watcher = FileSystemWatcher(str(vault), check_interval=interval)

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

    # Run watchers (simplified - in production, run in separate threads)
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
    logger = logging.getLogger("main")

    vault = Path(vault_path)
    cron_runner = CronRunner(str(vault))
    daily_summary = DailySummary(str(vault))

    # Register daily summary task (8:00 AM daily)
    cron_runner.register_task(
        name="daily_briefing",
        cron_expression="0 8 * * *",
        callback=daily_summary.generate_summary,
        description="Generate daily business briefing at 8:00 AM",
    )

    # Run scheduler
    try:
        logger.info("Starting scheduler...")
        asyncio.run(cron_runner.run_continuously(check_interval=60))
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        sys.exit(1)


def run_mcp_server(vault_path: str):
    """Run the MCP server."""
    import subprocess

    logger = logging.getLogger("main")
    logger.info(f"Starting MCP server for vault: {vault_path}")

    mcp_server_path = Path(__file__).parent.parent / "mcp_server" / "server.py"

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
        description="AI Employee Silver Tier - Orchestrator"
    )

    parser.add_argument(
        "--vault",
        "-v",
        type=str,
        default="./AI_Employee_Vault",
        help="Path to Obsidian vault (default: ./AI_Employee_Vault)",
    )

    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=30,
        help="Watcher check interval in seconds (default: 30)",
    )

    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        choices=["watchers", "scheduler", "mcp", "all"],
        default="watchers",
        help="Run mode (default: watchers)",
    )

    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug logging"
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
        logger = logging.getLogger("main")
        logger.warning("'all' mode not implemented. Run components separately.")
        logger.info("Start watchers: python main.py --mode watchers")
        logger.info("Start scheduler: python main.py --mode scheduler")
        logger.info("Start MCP: python main.py --mode mcp")


if __name__ == "__main__":
    main()
