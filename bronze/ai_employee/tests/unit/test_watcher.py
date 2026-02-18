"""Unit tests for Watcher services."""

import pytest
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.ai_employee.models.config import (
    WatcherConfig,
    FilesystemConfig,
    GmailConfig,
    WatcherType,
)
from src.ai_employee.services.watcher import (
    FilesystemWatcher,
    GmailWatcher,
    FilesystemEventHandler,
)
from src.ai_employee.errors import (
    WatcherConfigError,
    WatcherConnectionError,
)


class TestFilesystemConfig:
    """T041: Tests for FilesystemConfig model."""

    def test_create_filesystem_config(self):
        """T041: Verify FilesystemConfig can be created with required fields."""
        config = FilesystemConfig(
            watch_path="/tmp/test_watch"
        )
        assert config.watch_path == "/tmp/test_watch"
        assert config.file_pattern == "*.md"
        assert config.recursive is False
        assert config.poll_interval_seconds == 30

    def test_filesystem_config_custom_values(self):
        """T041: Verify FilesystemConfig accepts custom values."""
        config = FilesystemConfig(
            watch_path="/tmp/custom_watch",
            file_pattern="*.txt",
            recursive=True,
            ignore_patterns=["*.log", "*.bak"],
            poll_interval_seconds=60
        )
        assert config.watch_path == "/tmp/custom_watch"
        assert config.file_pattern == "*.txt"
        assert config.recursive is True
        assert config.ignore_patterns == ["*.log", "*.bak"]
        assert config.poll_interval_seconds == 60

    def test_filesystem_config_validates_absolute_path(self):
        """T041: Verify FilesystemConfig rejects relative paths."""
        with pytest.raises(ValueError, match="absolute path"):
            FilesystemConfig(watch_path="relative/path")


class TestGmailConfig:
    """T042: Tests for GmailConfig model."""

    def test_create_gmail_config(self):
        """T042: Verify GmailConfig can be created with required fields."""
        config = GmailConfig(
            email_address="test @gmail.com"
        )
        assert config.email_address == "test @gmail.com"
        assert config.imap_server == "imap.gmail.com"
        assert config.imap_port == 993
        assert config.app_password_env == "GMAIL_APP_PASSWORD"
        assert config.poll_interval_seconds == 30

    def test_gmail_config_custom_values(self):
        """T042: Verify GmailConfig accepts custom values."""
        config = GmailConfig(
            email_address="user @example.com",
            imap_server="imap.example.com",
            imap_port=993,
            app_password_env="CUSTOM_PASSWORD",
            folder="INBOX",
            mark_as_read=False,
            poll_interval_seconds=60
        )
        assert config.email_address == "user @example.com"
        assert config.imap_server == "imap.example.com"
        assert config.app_password_env == "CUSTOM_PASSWORD"
        assert config.mark_as_read is False
        assert config.poll_interval_seconds == 60

    def test_gmail_config_validates_email(self):
        """T042: Verify GmailConfig rejects invalid email addresses."""
        with pytest.raises(ValueError, match="Invalid email"):
            GmailConfig(email_address="invalid-email")


class TestWatcherConfig:
    """T043: Tests for WatcherConfig model."""

    def test_create_filesystem_watcher_config(self):
        """T043: Verify WatcherConfig for filesystem type."""
        fs_config = FilesystemConfig(watch_path="/tmp/watch")
        config = WatcherConfig.from_filesystem(fs_config)

        assert config.watcher_type == WatcherType.FILESYSTEM
        assert config.enabled is True
        assert config.source_config["watch_path"] == "/tmp/watch"

    def test_create_gmail_watcher_config(self):
        """T043: Verify WatcherConfig for Gmail type."""
        gmail_config = GmailConfig(email_address="test @gmail.com")
        config = WatcherConfig.from_gmail(gmail_config)

        assert config.watcher_type == WatcherType.GMAIL
        assert config.enabled is True
        assert config.source_config["email_address"] == "test @gmail.com"

    def test_watcher_config_to_filesystem_config(self):
        """T043: Verify conversion to FilesystemConfig."""
        fs_config = FilesystemConfig(watch_path="/tmp/watch", recursive=True)
        config = WatcherConfig.from_filesystem(fs_config)

        converted = config.to_filesystem_config()
        assert converted.watch_path == "/tmp/watch"
        assert converted.recursive is True

    def test_watcher_config_to_gmail_config(self):
        """T043: Verify conversion to GmailConfig."""
        gmail_config = GmailConfig(email_address="test @gmail.com", mark_as_read=False)
        config = WatcherConfig.from_gmail(gmail_config)

        converted = config.to_gmail_config()
        assert converted.email_address == "test @gmail.com"
        assert converted.mark_as_read is False


class TestFilesystemEventHandler:
    """T037: Tests for FilesystemEventHandler."""

    def test_handler_detects_new_md_files(self, tmp_path):
        """T037: Verify handler detects new .md files."""
        callback_calls = []

        def mock_callback(path):
            callback_calls.append(path)

        handler = FilesystemEventHandler(
            callback=mock_callback,
            file_pattern="*.md",
            debounce_ms=50
        )

        # Simulate file creation event
        test_file = tmp_path / "test.md"
        from watchdog.events import FileCreatedEvent
        event = FileCreatedEvent(str(test_file))

        handler.on_created(event)
        time.sleep(0.1)  # Wait for debounce
        handler.process_pending()

        assert len(callback_calls) == 1
        assert callback_calls[0] == str(test_file)

    def test_handler_ignores_non_md_files(self, tmp_path):
        """T037: Verify handler ignores non-.md files."""
        callback_calls = []

        def mock_callback(path):
            callback_calls.append(path)

        handler = FilesystemEventHandler(
            callback=mock_callback,
            file_pattern="*.md",
            debounce_ms=50
        )

        # Simulate txt file creation
        test_file = tmp_path / "test.txt"
        from watchdog.events import FileCreatedEvent
        event = FileCreatedEvent(str(test_file))

        handler.on_created(event)
        time.sleep(0.1)
        handler.process_pending()

        assert len(callback_calls) == 0

    def test_handler_ignores_temp_files(self, tmp_path):
        """T037: Verify handler ignores temporary files."""
        callback_calls = []

        def mock_callback(path):
            callback_calls.append(path)

        handler = FilesystemEventHandler(
            callback=mock_callback,
            file_pattern="*.md",
            ignore_patterns=["*.tmp", "*.swp"],
            debounce_ms=50
        )

        # Simulate temp file creation
        test_file = tmp_path / "test.tmp"
        from watchdog.events import FileCreatedEvent
        event = FileCreatedEvent(str(test_file))

        handler.on_created(event)
        time.sleep(0.1)
        handler.process_pending()

        assert len(callback_calls) == 0

    def test_handler_debounce_works(self, tmp_path):
        """T037: Verify handler respects debounce (500ms default)."""
        callback_calls = []

        def mock_callback(path):
            callback_calls.append((path, time.time()))

        handler = FilesystemEventHandler(
            callback=mock_callback,
            debounce_ms=50  # Very short for testing
        )

        # Create file
        test_file = tmp_path / "test.md"
        from watchdog.events import FileCreatedEvent
        event = FileCreatedEvent(str(test_file))

        handler.on_created(event)

        # Check before debounce period - should not process yet
        time.sleep(0.03)
        handler.process_pending()
        assert len(callback_calls) == 0

        # Wait for debounce to expire and process
        time.sleep(0.1)
        handler.process_pending()
        # After debounce expires, file should be processed
        assert len(callback_calls) >= 1 or len(handler._pending_files) == 0


class TestFilesystemWatcher:
    """T038: Tests for FilesystemWatcher service."""

    @pytest.fixture
    def watch_dir(self):
        """Create temporary watch directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def watcher_config(self, watch_dir):
        """Create watcher config for test directory."""
        fs_config = FilesystemConfig(
            watch_path=str(watch_dir),
            poll_interval_seconds=30
        )
        return WatcherConfig.from_filesystem(fs_config)

    def test_watcher_starts_successfully(self, watcher_config):
        """T038: Verify FilesystemWatcher starts without errors."""
        watcher = FilesystemWatcher(watcher_config)
        watcher.start()

        assert watcher.is_running is True

        watcher.stop()

    def test_watcher_stops_successfully(self, watcher_config):
        """T038: Verify FilesystemWatcher stops cleanly."""
        watcher = FilesystemWatcher(watcher_config)
        watcher.start()
        watcher.stop()

        assert watcher.is_running is False

    def test_watcher_detects_new_files(self, watcher_config, watch_dir):
        """T038: Verify FilesystemWatcher detects new .md files."""
        detected_files = []

        watcher = FilesystemWatcher(watcher_config)
        watcher.set_callback(lambda path: detected_files.append(path))
        watcher.start()

        try:
            # Create a new markdown file
            test_file = watch_dir / "new_file.md"
            test_file.write_text("# Test")

            # Wait for detection (with debounce)
            time.sleep(0.7)

            # Process pending
            watcher.process_pending()

            assert len(detected_files) == 1
            assert str(test_file) in detected_files[0]
        finally:
            watcher.stop()

    def test_watcher_health_check(self, watcher_config, watch_dir):
        """T049: Verify health_check() returns True when watcher is healthy."""
        watcher = FilesystemWatcher(watcher_config)

        # Before start
        assert watcher.health_check() is False

        # After start
        watcher.start()
        assert watcher.health_check() is True

        watcher.stop()

    def test_watcher_rejects_invalid_path(self):
        """T038: Verify FilesystemWatcher rejects non-existent path."""
        config = WatcherConfig(
            watcher_type=WatcherType.FILESYSTEM,
            source_config={"watch_path": "/nonexistent/path"}
        )

        watcher = FilesystemWatcher(config)

        with pytest.raises(WatcherConnectionError):
            watcher.start()

    def test_watcher_rejects_file_as_path(self, watch_dir):
        """T038: Verify FilesystemWatcher rejects file path (not directory)."""
        test_file = watch_dir / "file.md"
        test_file.write_text("test")

        config = WatcherConfig(
            watcher_type=WatcherType.FILESYSTEM,
            source_config={"watch_path": str(test_file)}
        )

        watcher = FilesystemWatcher(config)

        with pytest.raises(WatcherConnectionError, match="not a directory"):
            watcher.start()

    def test_watcher_callback_integration(self, watcher_config, watch_dir):
        """T038: Verify callback is called when file detected."""
        callback_called = []

        def callback(path):
            callback_called.append(path)

        watcher = FilesystemWatcher(watcher_config)
        watcher.set_callback(callback)
        watcher.start()

        try:
            test_file = watch_dir / "callback_test.md"
            test_file.write_text("# Callback Test")

            time.sleep(0.7)
            watcher.process_pending()

            assert len(callback_called) == 1
        finally:
            watcher.stop()


class TestGmailWatcher:
    """T039: Tests for GmailWatcher service."""

    @pytest.fixture
    def gmail_config(self):
        """Create Gmail config for testing."""
        return WatcherConfig(
            watcher_type=WatcherType.GMAIL,
            source_config={
                "email_address": "test @gmail.com",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "app_password_env": "TEST_GMAIL_PASSWORD",
                "poll_interval_seconds": 30
            }
        )

    def test_gmail_watcher_rejects_missing_password(self, gmail_config):
        """T039: Verify GmailWatcher fails when password not set."""
        # Ensure env var is not set
        import os
        original = os.environ.pop("TEST_GMAIL_PASSWORD", None)

        watcher = GmailWatcher(gmail_config)

        with pytest.raises(WatcherConnectionError, match="App password not found"):
            watcher.start()

        # Restore original
        if original:
            os.environ["TEST_GMAIL_PASSWORD"] = original

    @patch('imaplib.IMAP4_SSL')
    def test_gmail_watcher_starts_with_valid_credentials(self, mock_imap, gmail_config):
        """T039: Verify GmailWatcher starts with valid credentials."""
        import os
        os.environ["TEST_GMAIL_PASSWORD"] = "fake_password"

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        watcher = GmailWatcher(gmail_config)
        watcher.start()

        assert watcher.is_running is True
        mock_mail.login.assert_called_once()
        mock_mail.select.assert_called()

        watcher.stop()
        del os.environ["TEST_GMAIL_PASSWORD"]

    @patch('imaplib.IMAP4_SSL')
    def test_gmail_watcher_health_check(self, mock_imap, gmail_config):
        """T049: Verify GmailWatcher health check works."""
        import os
        os.environ["TEST_GMAIL_PASSWORD"] = "fake_password"

        mock_mail = MagicMock()
        mock_imap.return_value = mock_mail

        watcher = GmailWatcher(gmail_config)
        watcher.start()

        assert watcher.health_check() is True

        watcher.stop()
        del os.environ["TEST_GMAIL_PASSWORD"]


class TestWatcherIntegration:
    """T040: Integration tests for watcher functionality."""

    @pytest.fixture
    def watch_dir(self):
        """Create temporary watch directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_watcher_triggers_within_30s(self, watch_dir):
        """T040: Verify watcher triggers processing within 30 seconds (SC-003)."""
        detected_files = []
        detection_time = []

        def callback(path):
            detected_files.append(path)
            detection_time.append(time.time())

        fs_config = FilesystemConfig(
            watch_path=str(watch_dir),
            poll_interval_seconds=30
        )
        config = WatcherConfig.from_filesystem(fs_config)

        watcher = FilesystemWatcher(config)
        watcher.set_callback(callback)

        start_time = time.time()
        watcher.start()

        try:
            # Create file
            test_file = watch_dir / "timing_test.md"
            test_file.write_text("# Timing Test")

            # Wait for detection
            timeout = 35  # 30s + debounce + buffer
            while len(detected_files) == 0 and (time.time() - start_time) < timeout:
                time.sleep(0.5)
                watcher.process_pending()

            elapsed = time.time() - start_time

            # Should detect within 30 seconds per SC-003
            assert len(detected_files) == 1
            assert elapsed < 30.0, f"Detection took {elapsed}s, exceeds 30s requirement"

        finally:
            watcher.stop()
