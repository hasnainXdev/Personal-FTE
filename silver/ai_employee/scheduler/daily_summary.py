"""
Daily Summary Generator - Generate daily activity summaries

Creates daily summaries of watcher triggers, MCP actions,
and task processing for Dashboard.md
"""

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_daily_summary(
    date_range: str = "yesterday",
    include_watchers: bool = True,
    include_mcp_actions: bool = True,
    output_path: Path | None = None,
):
    """
    Generate a daily summary report.
    
    Args:
        date_range: "yesterday" or "today" or ISO date range
        include_watchers: Include watcher statistics
        include_mcp_actions: Include MCP action statistics
        output_path: Path to write summary (default: Dashboard.md)
    """
    project_root = Path(__file__).parent.parent.parent
    dashboard_path = output_path or (project_root / "AI_Employee_Vault" / "Dashboard.md")
    
    # Calculate date range
    now = datetime.now(timezone.utc)
    if date_range == "yesterday":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        end_date = start_date + timedelta(days=1)
    elif date_range == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:
        # Parse ISO format
        start_date = now - timedelta(days=1)
        end_date = now
    
    logger.info(f"Generating daily summary for {start_date} to {end_date}")
    
    # Collect statistics
    summary_sections = []
    
    # Header
    summary_sections.append(f"# Daily Summary: {start_date.date()}")
    summary_sections.append(f"\n**Generated**: {now.isoformat()}\n")
    
    # Watcher Statistics
    if include_watchers:
        watcher_stats = _collect_watcher_stats(start_date, end_date, project_root)
        summary_sections.append("\n## Watcher Activity\n")
        
        if watcher_stats:
            summary_sections.append("\n| Watcher | Items Found | Status |\n|---------|-------------|--------|")
            for watcher_name, stats in watcher_stats.items():
                summary_sections.append(f"| {watcher_name} | {stats['count']} | {stats['status']} |")
        else:
            summary_sections.append("\n*No watcher activity*\n")
    
    # MCP Actions Statistics
    if include_mcp_actions:
        mcp_stats = _collect_mcp_stats(start_date, end_date, project_root)
        summary_sections.append("\n## MCP Actions\n")
        
        if mcp_stats:
            summary_sections.append("\n| Action | Count | Success Rate |\n|--------|-------|-------------|")
            for action_name, stats in mcp_stats.items():
                success_rate = (stats['success'] / stats['count'] * 100) if stats['count'] > 0 else 0
                summary_sections.append(f"| {action_name} | {stats['count']} | {success_rate:.0f}% |")
        else:
            summary_sections.append("\n*No MCP actions*\n")
    
    # Write summary to Logs_Extended
    logs_dir = project_root / "AI_Employee_Vault" / "Logs_Extended"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    summary_file = logs_dir / f"daily_summary_{start_date.strftime('%Y%m%d')}.md"
    summary_content = "\n".join(summary_sections)
    summary_file.write_text(summary_content, encoding="utf-8")
    
    logger.info(f"Daily summary written to {summary_file}")
    
    return summary_content


def _collect_watcher_stats(start_date: datetime, end_date: datetime, project_root: Path) -> dict:
    """Collect watcher statistics from state files"""
    stats = {}
    
    logs_dir = project_root / "AI_Employee_Vault" / "Logs_Extended"
    
    for state_file in logs_dir.glob("watcher_*_state.md"):
        watcher_name = state_file.stem.replace("watcher_", "").replace("_state", "")
        
        try:
            content = state_file.read_text(encoding="utf-8")
            # Parse processed IDs count
            processed_file = logs_dir / f"watcher_{watcher_name}_processed.md"
            if processed_file.exists():
                processed_content = processed_file.read_text(encoding="utf-8")
                count = len([l for l in processed_content.split("\n") if l.strip().startswith("- ")])
            else:
                count = 0
            
            stats[watcher_name] = {
                "count": count,
                "status": "Active"
            }
        except Exception as e:
            logger.warning(f"Failed to read watcher stats for {watcher_name}: {e}")
    
    return stats


def _collect_mcp_stats(start_date: datetime, end_date: datetime, project_root: Path) -> dict:
    """Collect MCP action statistics from action log"""
    stats = {}
    
    mcp_log_path = project_root / "ai_employee" / "mcp_server" / "logs" / "mcp_actions.md"
    
    if not mcp_log_path.exists():
        return stats
    
    try:
        content = mcp_log_path.read_text(encoding="utf-8")
        
        # Parse log entries (simplified)
        for line in content.split("\n"):
            if "**Action**:" in line:
                action_name = line.split("**Action**:", 1)[1].strip()
                
                if action_name not in stats:
                    stats[action_name] = {"count": 0, "success": 0}
                
                stats[action_name]["count"] += 1
                
                # Check status
                if "**Status**: success" in content:
                    stats[action_name]["success"] += 1
    
    except Exception as e:
        logger.warning(f"Failed to read MCP stats: {e}")
    
    return stats


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Summary Generator")
    parser.add_argument("--date-range", default="yesterday", help="Date range")
    parser.add_argument("--no-watchers", action="store_true", help="Exclude watcher stats")
    parser.add_argument("--no-mcp", action="store_true", help="Exclude MCP stats")
    args = parser.parse_args()
    
    generate_daily_summary(
        date_range=args.date_range,
        include_watchers=not args.no_watchers,
        include_mcp_actions=not args.no_mcp
    )
