#!/usr/bin/env python3
"""Main entry point for AI Employee Bronze Tier watchers."""

import argparse
import logging
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from watchers import FileSystemWatcher


def setup_logging(debug: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_filesystem_watcher(vault_path: str, interval: int, debug: bool):
    """Run the file system watcher."""
    logger = logging.getLogger("main")
    
    # Validate vault path
    vault = Path(vault_path)
    if not vault.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Check for required files
    required_files = ['Dashboard.md', 'Company_Handbook.md']
    for file in required_files:
        if not (vault / file).exists():
            logger.warning(f"Missing recommended file: {file}")
    
    logger.info(f"Starting FileSystemWatcher")
    logger.info(f"Vault: {vault.absolute()}")
    logger.info(f"Check interval: {interval}s")
    
    watcher = FileSystemWatcher(
        vault_path=str(vault),
        check_interval=interval
    )
    
    try:
        watcher.run()
    except KeyboardInterrupt:
        logger.info("Watcher stopped by user")
    except Exception as e:
        logger.error(f"Watcher failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Employee Bronze Tier - File System Watcher"
    )
    
    parser.add_argument(
        '--vault', '-v',
        type=str,
        default='./AI_Employee_Vault',
        help='Path to Obsidian vault (default: ./AI_Employee_Vault)'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.debug)
    run_filesystem_watcher(args.vault, args.interval, args.debug)


if __name__ == '__main__':
    main()
