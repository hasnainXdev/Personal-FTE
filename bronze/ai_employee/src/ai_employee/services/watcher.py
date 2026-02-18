"""Watcher service for monitoring input sources."""

import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from ..models.config import WatcherConfig, FilesystemConfig, GmailConfig, WatcherType
from ..errors import WatcherConfigError, WatcherConnectionError, WatcherTimeout


class WatcherService(ABC):
    """Abstract base class for input source watchers."""

    def __init__(self, config: WatcherConfig):
        """
        Initialize the watcher service.

        Args:
            config: Watcher configuration
        """
        self.config = config
        self._running = False
        self._callback: Optional[Callable[[str], None]] = None

    @abstractmethod
    def start(self) -> None:
        """Start the watcher."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the watcher."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if watcher is healthy and connected."""
        pass

    def set_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set callback function for when new input is detected.

        Args:
            callback: Function to call with input path/data
        """
        self._callback = callback

    def _notify(self, input_data: str) -> None:
        """Notify callback of new input."""
        if self._callback:
            self._callback(input_data)

    @property
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running


class FilesystemEventHandler(FileSystemEventHandler):
    """Handler for filesystem events with debounce support."""

    def __init__(
        self,
        callback: Callable[[str], None],
        file_pattern: str = "*.md",
        ignore_patterns: Optional[List[str]] = None,
        debounce_ms: int = 500
    ):
        """
        Initialize the event handler.

        Args:
            callback: Function to call when file is created
            file_pattern: Glob pattern for files to watch
            ignore_patterns: Patterns to ignore
            debounce_ms: Debounce time in milliseconds
        """
        super().__init__()
        self._callback = callback
        self._file_pattern = file_pattern
        self._ignore_patterns = ignore_patterns or [".*", "*.tmp", "*.swp"]
        self._debounce_ms = debounce_ms
        self._pending_files: dict[str, float] = {}

    def _should_ignore(self, path: str) -> bool:
        """Check if file should be ignored."""
        filename = os.path.basename(path)
        for pattern in self._ignore_patterns:
            if pattern.startswith("*"):
                if filename.endswith(pattern[1:]):
                    return True
            elif pattern.startswith("."):
                if filename.startswith(pattern):
                    return True
        return False

    def _matches_pattern(self, path: str) -> bool:
        """Check if file matches the watch pattern."""
        filename = os.path.basename(path)
        if self._file_pattern == "*.md":
            return filename.endswith(".md")
        return True

    def on_created(self, event):
        """Handle file creation events with debounce."""
        if isinstance(event, FileCreatedEvent):
            path = event.src_path

            # Skip directories
            if os.path.isdir(path):
                return

            # Check ignore patterns
            if self._should_ignore(path):
                return

            # Check file pattern
            if not self._matches_pattern(path):
                return

            # Add to pending files for debounce
            self._pending_files[path] = time.time()

    def process_pending(self) -> None:
        """Process pending files after debounce period."""
        current_time = time.time()
        processed = []

        for path, created_time in self._pending_files.items():
            if (current_time - created_time) * 1000 >= self._debounce_ms:
                self._callback(path)
                processed.append(path)

        for path in processed:
            del self._pending_files[path]


class FilesystemWatcher(WatcherService):
    """
    T045/T046/T047: Filesystem watcher using watchdog.

    Monitors a directory for new markdown files and triggers processing.
    """

    def __init__(self, config: WatcherConfig):
        """
        Initialize the filesystem watcher.

        Args:
            config: Watcher configuration with filesystem source_config
        """
        super().__init__(config)

        if config.watcher_type != WatcherType.FILESYSTEM:
            raise WatcherConfigError(
                "Invalid watcher type: expected filesystem",
                {"type": config.watcher_type}
            )

        fs_config = config.to_filesystem_config()
        self._fs_config = fs_config
        self._watch_path = Path(fs_config.watch_path)
        self._observer: Optional[Observer] = None
        self._event_handler: Optional[FilesystemEventHandler] = None

    def start(self) -> None:
        """
        T047: Start the filesystem watcher.

        Raises:
            WatcherConnectionError: If watch path doesn't exist
        """
        if self._running:
            return

        # Validate watch path
        if not self._watch_path.exists():
            raise WatcherConnectionError(
                f"Watch path does not exist: {self._watch_path}",
                {"path": str(self._watch_path)}
            )

        if not self._watch_path.is_dir():
            raise WatcherConnectionError(
                f"Watch path is not a directory: {self._watch_path}",
                {"path": str(self._watch_path)}
            )

        # Create event handler with callback
        self._event_handler = FilesystemEventHandler(
            callback=self._notify,
            file_pattern=self._fs_config.file_pattern,
            ignore_patterns=self._fs_config.ignore_patterns,
            debounce_ms=500  # T046: 500ms debounce
        )

        # Create and configure observer
        self._observer = Observer()
        self._observer.schedule(
            self._event_handler,
            str(self._watch_path),
            recursive=self._fs_config.recursive
        )

        # Start observer
        self._observer.start()
        self._running = True

    def stop(self) -> None:
        """T047: Stop the filesystem watcher."""
        if not self._running:
            return

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

        self._running = False

    def health_check(self) -> bool:
        """
        T049: Check if watcher is healthy.

        Returns:
            True if watcher is running and path is accessible
        """
        if not self._running:
            return False

        # Check if watch path is still accessible
        try:
            if not self._watch_path.exists():
                return False
            if not os.access(self._watch_path, os.R_OK):
                return False
        except Exception:
            return False

        # Check if observer thread is alive
        if self._observer and not self._observer.is_alive():
            return False

        return True

    def process_pending(self) -> None:
        """Process any pending debounced files."""
        if self._event_handler:
            self._event_handler.process_pending()


class GmailWatcher(WatcherService):
    """
    Gmail watcher using IMAP.

    Monitors Gmail inbox for new emails and triggers processing.
    """

    def __init__(self, config: WatcherConfig):
        """
        Initialize the Gmail watcher.

        Args:
            config: Watcher configuration with Gmail source_config
        """
        super().__init__(config)

        if config.watcher_type != WatcherType.GMAIL:
            raise WatcherConfigError(
                "Invalid watcher type: expected gmail",
                {"type": config.watcher_type}
            )

        self._gmail_config = config.to_gmail_config()
        self._last_check: Optional[datetime] = None
        self._connected: bool = False

    def _connect(self) -> None:
        """Establish IMAP connection."""
        import imaplib

        try:
            # Get app password from environment
            app_password = os.getenv(self._gmail_config.app_password_env)
            if not app_password:
                raise WatcherConnectionError(
                    f"App password not found. Set {self._gmail_config.app_password_env} environment variable.",
                    {"env_var": self._gmail_config.app_password_env}
                )

            # Connect to IMAP server
            self._mail = imaplib.IMAP4_SSL(
                self._gmail_config.imap_server,
                self._gmail_config.imap_port
            )

            # Login
            self._mail.login(
                self._gmail_config.email_address,
                app_password
            )

            # Select folder
            self._mail.select(self._gmail_config.folder)

            self._connected = True
            self._last_check = datetime.utcnow()

        except Exception as e:
            raise WatcherConnectionError(
                f"Failed to connect to Gmail: {e}",
                {"email": self._gmail_config.email_address}
            )

    def start(self) -> None:
        """Start the Gmail watcher."""
        if self._running:
            return

        self._connect()
        self._running = True

    def stop(self) -> None:
        """Stop the Gmail watcher."""
        if not self._running:
            return

        if hasattr(self, "_mail"):
            try:
                self._mail.close()
                self._mail.logout()
            except Exception:
                pass

        self._running = False
        self._connected = False

    def health_check(self) -> bool:
        """Check if Gmail connection is healthy."""
        if not self._running or not self._connected:
            return False

        try:
            # Try to select folder to verify connection
            if hasattr(self, "_mail"):
                self._mail.select(self._gmail_config.folder)
            return True
        except Exception:
            self._connected = False
            return False

    def check_new_mail(self) -> List[dict]:
        """
        Check for new unread emails.

        Returns:
            List of email data dictionaries
        """
        import email
        from email.header import decode_header

        if not self._connected:
            self._connect()

        new_emails = []

        try:
            # Search for unread emails
            status, messages = self._mail.search(None, 'UNSEEN')

            if status != 'OK':
                return []

            # Process each email
            for msg_id in messages[0].split():
                status, msg_data = self._mail.fetch(msg_id, '(RFC822)')

                if status != 'OK':
                    continue

                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Extract data
                subject, encoding = decode_header(email_message['Subject'])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8', errors='replace')

                from_address = email_message.get('From', '')
                date_str = email_message.get('Date', '')

                # Get body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition', ''))
                        if content_type == 'text/plain' and 'attachment' not in content_disposition:
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                                break
                            except Exception:
                                pass
                else:
                    try:
                        body = email_message.get_payload(decode=True).decode('utf-8', errors='replace')
                    except Exception:
                        pass

                new_emails.append({
                    'message_id': email_message.get('Message-ID', ''),
                    'from': from_address,
                    'subject': subject,
                    'body': body,
                    'date': date_str,
                    'msg_id': msg_id.decode()
                })

            self._last_check = datetime.utcnow()

        except Exception:
            # Connection error - will retry on next check
            pass

        return new_emails

    def mark_as_read(self, msg_id: str) -> None:
        """Mark an email as read."""
        if self._connected and hasattr(self, "_mail"):
            try:
                self._mail.store(msg_id, '+FLAGS', '\\Seen')
            except Exception:
                pass
