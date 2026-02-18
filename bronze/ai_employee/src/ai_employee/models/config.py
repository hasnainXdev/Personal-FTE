"""Configuration models for AI Employee Vault system."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class WatcherType(str, Enum):
    """Type of input source watcher."""
    GMAIL = "gmail"
    FILESYSTEM = "filesystem"


class FilesystemConfig(BaseModel):
    """
    Configuration for filesystem watcher.

    Attributes:
        watch_path: Absolute path to directory to monitor
        file_pattern: Glob pattern for files to watch (default: *.md)
        recursive: Whether to watch subdirectories (default: False)
        ignore_patterns: List of patterns to ignore
        poll_interval_seconds: How often to check for changes (default: 30)
    """
    watch_path: str
    file_pattern: str = "*.md"
    recursive: bool = False
    ignore_patterns: List[str] = Field(default_factory=lambda: [".*", "*.tmp", "*.swp"])
    poll_interval_seconds: int = Field(default=30, ge=1, le=300)

    @field_validator("watch_path")
    @classmethod
    def validate_watch_path(cls, v: str) -> str:
        """Validate watch path is absolute."""
        if not v.startswith("/"):
            raise ValueError("watch_path must be an absolute path")
        return v


class GmailConfig(BaseModel):
    """
    Configuration for Gmail watcher.

    Attributes:
        imap_server: IMAP server address (default: imap.gmail.com)
        imap_port: IMAP port (default: 993)
        email_address: Gmail address to monitor
        app_password_env: Environment variable name for app password
        folder: IMAP folder to monitor (default: INBOX)
        mark_as_read: Whether to mark processed emails as read (default: True)
        poll_interval_seconds: How often to check for new mail (default: 30)
    """
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    email_address: str
    app_password_env: str = "GMAIL_APP_PASSWORD"
    folder: str = "INBOX"
    mark_as_read: bool = True
    poll_interval_seconds: int = Field(default=30, ge=1, le=300)

    @field_validator("email_address")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email address")
        return v


class WatcherConfig(BaseModel):
    """
    Main configuration for input source monitoring.

    Attributes:
        watcher_type: Type of watcher (gmail or filesystem)
        enabled: Whether watcher is active
        poll_interval_seconds: Default poll interval
        source_config: Type-specific configuration
    """
    watcher_type: WatcherType
    enabled: bool = True
    poll_interval_seconds: int = Field(default=30, ge=1, le=300)
    source_config: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_filesystem(cls, config: FilesystemConfig) -> "WatcherConfig":
        """Create watcher config from filesystem config."""
        return cls(
            watcher_type=WatcherType.FILESYSTEM,
            enabled=True,
            poll_interval_seconds=config.poll_interval_seconds,
            source_config=config.model_dump()
        )

    @classmethod
    def from_gmail(cls, config: GmailConfig) -> "WatcherConfig":
        """Create watcher config from Gmail config."""
        return cls(
            watcher_type=WatcherType.GMAIL,
            enabled=True,
            poll_interval_seconds=config.poll_interval_seconds,
            source_config=config.model_dump()
        )

    def to_filesystem_config(self) -> FilesystemConfig:
        """Convert to filesystem config."""
        if self.watcher_type != WatcherType.FILESYSTEM:
            raise ValueError("Watcher type is not filesystem")
        return FilesystemConfig(**self.source_config)

    def to_gmail_config(self) -> GmailConfig:
        """Convert to Gmail config."""
        if self.watcher_type != WatcherType.GMAIL:
            raise ValueError("Watcher type is not gmail")
        return GmailConfig(**self.source_config)
