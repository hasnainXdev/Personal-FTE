"""
Filesystem Watcher - Poll directory for new files

Polls a watched directory for new files and routes
them to Bronze Inbox for processing.
"""

import hashlib
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from .base_watcher import Watcher

logger = logging.getLogger(__name__)


class FilesystemWatcher(Watcher):
    """Watcher for filesystem directory"""
    
    def __init__(
        self,
        watch_dir: Path | None = None,
        state_dir: Path | None = None,
        inbox_dir: Path | None = None,
        interval_seconds: int = 60,
        file_patterns: list[str] | None = None,
        recursive: bool = False,
    ):
        """
        Initialize Filesystem watcher.
        
        Args:
            watch_dir: Directory to watch (default: Inbox_Drop)
            state_dir: Directory for state persistence (default: Logs_Extended)
            inbox_dir: Directory to write processed items (default: Inbox)
            interval_seconds: Polling interval
            file_patterns: File patterns to match (default: *.txt, *.md, *.json)
            recursive: Whether to watch subdirectories
        """
        # Default paths
        project_root = Path(__file__).parent.parent.parent
        if watch_dir is None:
            watch_dir = project_root / "AI_Employee_Vault" / "Inbox_Drop"
        if state_dir is None:
            state_dir = project_root / "Logs_Extended"
        if inbox_dir is None:
            inbox_dir = project_root / "AI_Employee_Vault" / "Inbox"
        
        # Store watch directory
        self.watch_dir = watch_dir
        self.file_patterns = file_patterns or ["*.txt", "*.md", "*.json"]
        self.recursive = recursive
        
        # Initialize base watcher
        super().__init__(
            name="filesystem",
            state_dir=state_dir,
            inbox_dir=inbox_dir,
            interval_seconds=interval_seconds,
        )
        
        # Ensure watch directory exists
        watch_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Watching directory: {watch_dir}")
    
    def _fetch_items(self, since: datetime) -> list:
        """
        Fetch files from watched directory modified since the given timestamp.
        """
        items = []
        
        # Get files matching patterns
        for pattern in self.file_patterns:
            if self.recursive:
                files = self.watch_dir.rglob(pattern)
            else:
                files = self.watch_dir.glob(pattern)
            
            for file_path in files:
                if not file_path.is_file():
                    continue
                
                # Check modification time
                try:
                    mtime = datetime.fromtimestamp(
                        file_path.stat().st_mtime,
                        tz=timezone.utc
                    )
                    
                    if mtime > since:
                        items.append({
                            "path": file_path,
                            "mtime": mtime,
                            "size": file_path.stat().st_size
                        })
                except Exception as e:
                    logger.warning(f"Failed to stat file {file_path}: {e}")
        
        logger.info(f"Found {len(items)} files modified since {since.isoformat()}")
        return items
    
    def _extract_id(self, item) -> str:
        """
        Extract unique ID from file.
        
        Uses file path hash for uniqueness.
        """
        file_path = item["path"]
        # Create ID from relative path and mtime
        rel_path = str(file_path.relative_to(self.watch_dir))
        mtime_str = item["mtime"].isoformat()
        unique_str = f"{rel_path}:{mtime_str}"
        
        # Hash for compact ID
        hash_id = hashlib.md5(unique_str.encode()).hexdigest()[:12]
        return f"FILE_{hash_id}"
    
    def _process_item(self, item, item_id: str):
        """
        Process file and save to Inbox as markdown.
        
        Reads file content and creates markdown with metadata.
        """
        file_path = item["path"]
        mtime = item["mtime"]
        
        # Read file content
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = "[Binary file - content not displayed]"
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            content = f"[Error reading file: {e}]"
        
        # Create markdown content
        rel_path = file_path.relative_to(self.watch_dir)
        
        markdown_content = f"""---
Source: Filesystem
Source_ID: {item_id}
Received: {mtime.isoformat()}
File_Path: {rel_path}
File_Size: {item['size']} bytes
---

# File: {file_path.name}

**Path**: {rel_path}
**Modified**: {mtime.isoformat()}

## Content

```
{content}
```

---
*Processed by Filesystem Watcher*
"""
        
        # Write to Inbox
        # Sanitize item_id for filename
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", item_id)
        inbox_file = self.inbox_dir / f"{safe_id}.md"
        
        inbox_file.write_text(markdown_content, encoding="utf-8")
        logger.info(f"Saved file to Inbox: {inbox_file.name}")
        
        # Optionally move processed file to Done folder
        # (commented out - can be enabled if desired)
        # done_dir = self.watch_dir.parent / "Done"
        # done_dir.mkdir(exist_ok=True)
        # file_path.rename(done_dir / file_path.name)


def run_watcher():
    """Entry point for running Filesystem watcher"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Filesystem Watcher")
    parser.add_argument("--test", action="store_true", help="Run test poll")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval")
    parser.add_argument("--watch-dir", type=Path, help="Directory to watch")
    args = parser.parse_args()
    
    watcher = FilesystemWatcher(
        watch_dir=args.watch_dir,
        interval_seconds=args.interval
    )
    
    if args.test:
        print("Running test poll...")
        count = watcher.poll()
        print(f"Processed {count} items")
    else:
        print("Running single poll...")
        count = watcher.poll()
        print(f"Processed {count} items")


if __name__ == "__main__":
    run_watcher()
