"""
Error handling for Companion MCR Bridge

Defines error types and classification for retry logic.
"""

from enum import Enum
from typing import Any, Dict


class CompanionErrorType(Enum):
    """
    Error type classification.

    Used to determine retry behavior.
    """

    # Network errors (retryable)
    CONNECTION_REFUSED = "connection_refused"
    CONNECTION_TIMEOUT = "connection_timeout"
    DNS_RESOLUTION = "dns_resolution"

    # Protocol errors (non-retryable)
    INVALID_RESPONSE = "invalid_response"
    PROTOCOL_ERROR = "protocol_error"

    # Logical errors (non-retryable)
    INTENT_NOT_FOUND = "intent_not_found"
    DEVICE_NOT_FOUND = "device_not_found"
    INVALID_MAPPING = "invalid_mapping"

    # Rate limiting (retryable with backoff)
    RATE_LIMITED = "rate_limited"

    # State errors (non-retryable)
    STATE_CORRUPTION = "state_corruption"
    VALIDATION_ERROR = "validation_error"


class CompanionError(Exception):
    """
    Base exception for Companion bridge errors.

    Attributes:
        error_type: Classification of error
        message: Human-readable error message
        details: Additional context
    """

    def __init__(
        self,
        error_type: CompanionErrorType,
        message: str,
        details: Dict[str, Any] = None,
    ):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(message)

    @property
    def is_retryable(self) -> bool:
        """Check if error is retryable"""
        return self.error_type in {
            CompanionErrorType.CONNECTION_REFUSED,
            CompanionErrorType.CONNECTION_TIMEOUT,
            CompanionErrorType.DNS_RESOLUTION,
            CompanionErrorType.RATE_LIMITED,
        }

    def __repr__(self) -> str:
        return f"CompanionError({self.error_type.value}: {self.message})"


class MacroAbortError(CompanionError):
    """Raised when a macro is aborted due to step failure"""

    def __init__(self, message: str, step_number: int = None):
        super().__init__(
            CompanionErrorType.PROTOCOL_ERROR,
            message,
            {"step_number": step_number},
        )
