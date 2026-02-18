"""Error taxonomy for AI Employee Vault system.

Each error class includes an error code for logging and tracking.
"""

from typing import Optional


class AIEmployeeError(Exception):
    """Base exception for all AI Employee Vault errors."""
    error_code: str = "UNKNOWN"
    
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert error to dictionary for logging."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


# Vault Service Errors (VLT-xxx)

class VaultCreationError(AIEmployeeError):
    """Raised when vault directories cannot be created."""
    error_code = "VLT-001"


class FileLockTimeout(AIEmployeeError):
    """Raised when file lock cannot be acquired after retries."""
    error_code = "VLT-002"


class InvalidMarkdown(AIEmployeeError):
    """Raised when content fails markdown validation."""
    error_code = "VLT-003"


class ItemNotFound(AIEmployeeError):
    """Raised when item ID not found in specified state."""
    error_code = "VLT-004"


class InvalidTransition(AIEmployeeError):
    """Raised when state transition is not allowed."""
    error_code = "VLT-005"


# Watcher Service Errors (WTC-xxx)

class WatcherConfigError(AIEmployeeError):
    """Raised when watcher configuration is invalid."""
    error_code = "WTC-001"


class WatcherConnectionError(AIEmployeeError):
    """Raised when watcher cannot connect to source."""
    error_code = "WTC-002"


class WatcherTimeout(AIEmployeeError):
    """Raised when watcher fails to respond."""
    error_code = "WTC-003"


# Skill Executor Errors (SKL-xxx)

class SkillNotFound(AIEmployeeError):
    """Raised when skill name not found."""
    error_code = "SKL-001"


class SkillParseError(AIEmployeeError):
    """Raised when skills file cannot be parsed."""
    error_code = "SKL-002"


class SkillValidationError(AIEmployeeError):
    """Raised when input/output validation fails."""
    error_code = "SKL-003"


class SkillExecutionError(AIEmployeeError):
    """Raised when skill execution fails."""
    error_code = "SKL-004"


# Logger Errors (LOG-xxx)

class LogWriteError(AIEmployeeError):
    """Raised when cannot write to Dashboard.md."""
    error_code = "LOG-001"


class LogArchiveError(AIEmployeeError):
    """Raised when archiving logs fails."""
    error_code = "LOG-002"


# Registry Errors (REG-xxx)

class RegistryWriteError(AIEmployeeError):
    """Raised when cannot update registry."""
    error_code = "REG-001"


class RegistryCorruption(AIEmployeeError):
    """Raised when registry file is corrupted."""
    error_code = "REG-002"


# Configuration Errors (CFG-xxx)

class ConfigNotFound(AIEmployeeError):
    """Raised when configuration file not found."""
    error_code = "CFG-001"


class ConfigValidationError(AIEmployeeError):
    """Raised when configuration validation fails."""
    error_code = "CFG-002"


# Resource Errors (RSC-xxx)

class StorageCapacityExceeded(AIEmployeeError):
    """Raised when vault storage limit is exceeded."""
    error_code = "RSC-001"


class MaxFileSizeExceeded(AIEmployeeError):
    """Raised when file exceeds maximum size limit."""
    error_code = "RSC-002"
