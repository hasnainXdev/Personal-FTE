"""Dashboard logger for operational logging."""

from pathlib import Path
from datetime import datetime
from typing import Optional, List
from enum import Enum

from ..errors import LogWriteError, LogArchiveError


class LogOutcome(str, Enum):
    """Possible outcomes for a log entry."""
    SUCCESS = "Success"
    FAILURE = "Failure"
    SKIPPED = "Skipped"


class LogEntry:
    """
    Single log entry for Dashboard.md.
    
    Attributes:
        timestamp: When the action occurred
        trigger_event: What initiated the action
        skill_executed: Name of skill (if applicable)
        file_moved: Transition (e.g., "Inbox→Needs_Action")
        outcome: Success, failure, or skipped
        error_message: Error details (if failed)
        duration_ms: Execution time in milliseconds
    """
    
    def __init__(
        self,
        timestamp: datetime,
        trigger_event: str,
        skill_executed: Optional[str] = None,
        file_moved: Optional[str] = None,
        outcome: LogOutcome = LogOutcome.SUCCESS,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ):
        self.timestamp = timestamp
        self.trigger_event = trigger_event
        self.skill_executed = skill_executed or "-"
        self.file_moved = file_moved or "-"
        self.outcome = outcome
        self.error_message = error_message or "-"
        self.duration_ms = duration_ms or 0
    
    def to_markdown_row(self) -> str:
        """Convert to markdown table row."""
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"| {timestamp_str} | {self.trigger_event} | {self.skill_executed} | "
            f"{self.file_moved} | {self.outcome.value} |\n"
        )
    
    @classmethod
    def from_success(
        cls,
        trigger_event: str,
        skill_executed: Optional[str] = None,
        file_moved: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> "LogEntry":
        """Create a successful log entry."""
        return cls(
            timestamp=datetime.utcnow(),
            trigger_event=trigger_event,
            skill_executed=skill_executed,
            file_moved=file_moved,
            outcome=LogOutcome.SUCCESS,
            duration_ms=duration_ms
        )
    
    @classmethod
    def from_failure(
        cls,
        trigger_event: str,
        error_message: str,
        skill_executed: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> "LogEntry":
        """Create a failed log entry."""
        return cls(
            timestamp=datetime.utcnow(),
            trigger_event=trigger_event,
            skill_executed=skill_executed,
            outcome=LogOutcome.FAILURE,
            error_message=error_message,
            duration_ms=duration_ms
        )
    
    @classmethod
    def from_skipped(
        cls,
        trigger_event: str,
        reason: str,
        skill_executed: Optional[str] = None
    ) -> "LogEntry":
        """Create a skipped log entry."""
        return cls(
            timestamp=datetime.utcnow(),
            trigger_event=f"{trigger_event} ({reason})",
            skill_executed=skill_executed,
            outcome=LogOutcome.SKIPPED,
            error_message=reason
        )


class DashboardLogger:
    """
    Manages operational logging to Dashboard.md.
    
    Features:
    - Append-only logging to Dashboard.md
    - Log rotation when entries exceed threshold
    - Monthly archiving of old logs
    """
    
    MAX_ENTRIES = 1000  # Archive when exceeding this count
    
    def __init__(self, dashboard_path: str, archive_dir: Optional[str] = None):
        """
        Initialize the dashboard logger.
        
        Args:
            dashboard_path: Path to Dashboard.md
            archive_dir: Directory for archived logs (default: parent of dashboard)
        """
        self.dashboard_path = Path(dashboard_path)
        self.archive_dir = Path(archive_dir) if archive_dir else self.dashboard_path.parent / "Archive"
        self._ensure_dashboard_exists()
    
    def _ensure_dashboard_exists(self) -> None:
        """Create Dashboard.md with header if it doesn't exist."""
        self.dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.dashboard_path.exists():
            self.dashboard_path.write_text(
                "# Operational Dashboard\n\n"
                "## Activity Log\n\n"
                "| Timestamp | Trigger Event | Skill Executed | File Moved | Outcome |\n"
                "|-----------|---------------|----------------|------------|---------|\n"
            )
    
    def _count_entries(self) -> int:
        """Count the number of log entries in Dashboard.md."""
        if not self.dashboard_path.exists():
            return 0
        
        content = self.dashboard_path.read_text()
        # Count lines that look like table rows (start with |)
        lines = content.split('\n')
        entry_count = sum(1 for line in lines if line.startswith('|') and '---' not in line)
        # Subtract 1 for header row
        return max(0, entry_count - 1)
    
    def log_entry(self, entry: LogEntry) -> None:
        """
        Append a log entry to Dashboard.md.
        
        Args:
            entry: LogEntry to append
            
        Raises:
            LogWriteError: If cannot write to dashboard
        """
        try:
            row = entry.to_markdown_row()
            
            # Append to file
            with open(self.dashboard_path, 'a') as f:
                f.write(row)
            
            # Check if rotation needed
            if self._count_entries() > self.MAX_ENTRIES:
                self._rotate_logs()
                
        except (IOError, OSError) as e:
            raise LogWriteError(
                f"Failed to write log entry: {e}",
                {"dashboard": str(self.dashboard_path)}
            )
    
    def _rotate_logs(self) -> None:
        """Archive old logs when threshold exceeded."""
        try:
            # Create archive directory
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Read current content
            content = self.dashboard_path.read_text()
            lines = content.split('\n')
            
            # Find header end (after the separator line)
            header_end = 0
            for i, line in enumerate(lines):
                if '|---' in line:
                    header_end = i + 1
                    break
            
            # Keep header + last MAX_ENTRIES/2 entries
            keep_count = self.MAX_ENTRIES // 2
            entries_to_archive = lines[header_end:-keep_count] if len(lines) > header_end + keep_count else []
            entries_to_keep = lines[:header_end] + lines[-keep_count:] if entries_to_archive else lines
            
            # Write archived entries to monthly file
            if entries_to_archive:
                archive_month = datetime.utcnow().strftime("%Y-%m")
                archive_path = self.archive_dir / f"{archive_month}.md"
                
                archive_content = (
                    "# Archived Logs\n\n"
                    f"**Month**: {archive_month}\n\n"
                    "| Timestamp | Trigger Event | Skill Executed | File Moved | Outcome |\n"
                    "|-----------|---------------|----------------|------------|---------|\n"
                )
                archive_content += ''.join(entries_to_archive)
                archive_path.write_text(archive_content)
            
            # Rewrite dashboard with remaining entries
            self.dashboard_path.write_text('\n'.join(entries_to_keep))
            
        except (IOError, OSError) as e:
            raise LogArchiveError(
                f"Failed to archive logs: {e}",
                {"archive_dir": str(self.archive_dir)}
            )
    
    def get_recent_logs(self, limit: int = 100) -> List[LogEntry]:
        """
        Get recent log entries.
        
        Args:
            limit: Maximum entries to return
            
        Returns:
            List of LogEntry objects (newest first)
        """
        if not self.dashboard_path.exists():
            return []
        
        content = self.dashboard_path.read_text()
        lines = content.split('\n')
        
        entries = []
        for line in reversed(lines):
            if not line.startswith('|') or '---' in line or 'Timestamp' in line:
                continue
            
            # Parse table row
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                try:
                    timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
                    entry = LogEntry(
                        timestamp=timestamp,
                        trigger_event=parts[1],
                        skill_executed=parts[2] if parts[2] != '-' else None,
                        file_moved=parts[3] if parts[3] != '-' else None,
                        outcome=LogOutcome(parts[4]) if parts[4] in [e.value for e in LogOutcome] else LogOutcome.SUCCESS
                    )
                    entries.append(entry)
                    
                    if len(entries) >= limit:
                        break
                except (ValueError, IndexError):
                    continue
        
        return entries
    
    def archive_old_logs(self, cutoff_date: datetime) -> str:
        """
        Archive logs older than cutoff date.
        
        Args:
            cutoff_date: Entries before this date will be archived
            
        Returns:
            Archive file path
            
        Raises:
            LogArchiveError: If archiving fails
        """
        try:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            
            content = self.dashboard_path.read_text()
            lines = content.split('\n')
            
            header_lines = []
            entries_to_keep = []
            entries_to_archive = []
            
            in_header = True
            for line in lines:
                if in_header:
                    header_lines.append(line)
                    if '|---' in line:
                        in_header = False
                    continue
                
                if not line.startswith('|'):
                    continue
                
                # Parse timestamp from row
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 1:
                    try:
                        timestamp = datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
                        if timestamp < cutoff_date:
                            entries_to_archive.append(line)
                        else:
                            entries_to_keep.append(line)
                    except ValueError:
                        entries_to_keep.append(line)
            
            # Write archive file
            if entries_to_archive:
                archive_date = cutoff_date.strftime("%Y-%m-%d")
                archive_path = self.archive_dir / f"before-{archive_date}.md"
                
                archive_content = (
                    "# Archived Logs\n\n"
                    f"**Archived entries before**: {archive_date}\n\n"
                    "| Timestamp | Trigger Event | Skill Executed | File Moved | Outcome |\n"
                    "|-----------|---------------|----------------|------------|---------|\n"
                )
                archive_content += '\n'.join(entries_to_archive)
                archive_path.write_text(archive_content)
                
                # Rewrite dashboard
                new_content = '\n'.join(header_lines + entries_to_keep)
                self.dashboard_path.write_text(new_content)
                
                return str(archive_path)
            
            return str(self.archive_dir)
            
        except (IOError, OSError) as e:
            raise LogArchiveError(
                f"Failed to archive logs: {e}",
                {"cutoff": cutoff_date.isoformat()}
            )
