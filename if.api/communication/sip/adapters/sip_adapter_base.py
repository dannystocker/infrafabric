"""
Unified SIPAdapter Base Class - IF.connect Protocol Implementation

This module provides the abstract base class for all 7 SIP server adapters.

Philosophy: Confucian Wu Lun (五伦) relationship mapping ensures ethical call hierarchy.
Protocol: IF.TTT (Traceable/Transparent/Trustworthy) compliance for all operations.

Author: Agent 8 (IF.search discovery)
Version: 1.0.0
Date: 2025-11-11
"""

import abc
import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import (
    Any, Callable, Dict, List, Optional, Union, Tuple
)
from datetime import datetime
from collections import deque
import json


# ============================================================================
# Enums & Data Classes
# ============================================================================

class CallState(str, Enum):
    """Standard call state machine for all adapters."""
    CREATED = "created"
    DIALING = "dialing"
    RINGING = "ringing"
    INCOMING = "incoming"
    CONNECTED = "connected"
    ON_HOLD = "on_hold"
    TRANSFERRING = "transferring"
    HANGING_UP = "hanging_up"
    TERMINATED = "terminated"


class ConnectionState(str, Enum):
    """Adapter connection state."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class HealthStatus(str, Enum):
    """Overall health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CallStateEvent:
    """Event emitted when call state changes."""
    call_id: str
    state: CallState
    timestamp: float = field(default_factory=time.time)
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    duration: Optional[float] = None
    reason: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['state'] = self.state.value
        data['timestamp'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


@dataclass
class IncomingCallEvent:
    """Event emitted on incoming call."""
    call_id: str
    from_number: str
    to_number: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    accept_callback: Optional[Callable[[], bool]] = None
    reject_callback: Optional[Callable[[], bool]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding callbacks)."""
        data = {
            'call_id': self.call_id,
            'from_number': self.from_number,
            'to_number': self.to_number,
            'timestamp': datetime.fromtimestamp(self.timestamp).isoformat(),
            'details': self.details
        }
        return data


@dataclass
class ErrorEvent:
    """Event emitted on error."""
    error_code: int
    error_message: str
    severity: ErrorSeverity
    timestamp: float = field(default_factory=time.time)
    call_id: Optional[str] = None
    retryable: bool = True
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['timestamp'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


@dataclass
class ConnectionStateEvent:
    """Event emitted when connection state changes."""
    connected: bool
    reason: str
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


# ============================================================================
# Exception Classes
# ============================================================================

class SIPAdapterError(Exception):
    """Base exception for all adapter errors."""

    def __init__(
        self,
        code: int,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.severity = severity
        self.retryable = retryable
        self.details = details or {}
        super().__init__(message)


class ConnectionError(SIPAdapterError):
    """Connection-level errors (typically retryable)."""

    def __init__(self, message: str, code: int = 503, **kwargs):
        super().__init__(code=code, message=message, severity=ErrorSeverity.ERROR, **kwargs)


class CallError(SIPAdapterError):
    """Call-level errors."""

    def __init__(self, message: str, code: int = 500, **kwargs):
        super().__init__(code=code, message=message, **kwargs)


class ConfigurationError(SIPAdapterError):
    """Configuration validation errors (not retryable)."""

    def __init__(self, message: str, code: int = 400):
        super().__init__(
            code=code,
            message=message,
            severity=ErrorSeverity.ERROR,
            retryable=False
        )


class TimeoutError(SIPAdapterError):
    """Operation timeout (retryable)."""

    def __init__(self, message: str, code: int = 504, **kwargs):
        super().__init__(
            code=code,
            message=message,
            severity=ErrorSeverity.WARNING,
            retryable=True,
            **kwargs
        )


# ============================================================================
# Utility Classes
# ============================================================================

class EventEmitter:
    """
    Simple event emitter for async callbacks.

    Features:
    - Multiple handlers per event type
    - Error isolation (one handler failure doesn't affect others)
    - Thread-safe registration and emission
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    def on(self, event_type: str, callback: Callable) -> None:
        """Register callback for event type."""
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(callback)

    def off(self, event_type: str, callback: Callable) -> None:
        """Unregister callback."""
        with self._lock:
            if event_type in self._handlers:
                try:
                    self._handlers[event_type].remove(callback)
                except ValueError:
                    pass

    def emit(self, event_type: str, event_data: Union[Dict, object]) -> None:
        """Fire event to all registered callbacks."""
        with self._lock:
            handlers = self._handlers.get(event_type, []).copy()

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Schedule async handler
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(handler(event_data))
                        else:
                            loop.run_until_complete(handler(event_data))
                    except RuntimeError:
                        # No event loop, skip async handler
                        pass
                else:
                    # Call sync handler
                    handler(event_data)
            except Exception as e:
                self.logger.exception(f"Error in event handler for {event_type}: {e}")


class MetricsCollector:
    """
    Thread-safe metrics collection.

    Tracks: call counts, success rates, latencies, connection state.
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._lock = threading.Lock()

        # Call metrics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.call_durations: deque = deque(maxlen=window_size)

        # Connection metrics
        self.connection_failures = 0
        self.last_error: Optional[str] = None
        self.uptime_start = time.time()

        # Latency metrics
        self.latencies: deque = deque(maxlen=window_size)

    def record_call(self, success: bool, duration: Optional[float] = None) -> None:
        """Record call outcome."""
        with self._lock:
            self.total_calls += 1
            if success:
                self.successful_calls += 1
            else:
                self.failed_calls += 1
            if duration is not None:
                self.call_durations.append(duration)

    def record_latency(self, latency_ms: float) -> None:
        """Record latency measurement."""
        with self._lock:
            self.latencies.append(latency_ms)

    def record_connection_failure(self, error: str) -> None:
        """Record connection failure."""
        with self._lock:
            self.connection_failures += 1
            self.last_error = error

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        with self._lock:
            success_rate = (
                self.successful_calls / self.total_calls
                if self.total_calls > 0
                else 0
            )

            latencies = list(self.latencies) if self.latencies else [0]
            durations = list(self.call_durations) if self.call_durations else [0]

            return {
                "active_calls": 0,  # Updated by adapter
                "call_attempts": self.total_calls,
                "call_success_rate": success_rate,
                "failed_calls": self.failed_calls,
                "avg_call_duration": sum(durations) / len(durations) if durations else 0,
                "connection_failures": self.connection_failures,
                "last_error": self.last_error,
                "pool_utilization": 0,  # Updated by adapter
                "latency": {
                    "min_ms": min(latencies) if latencies else 0,
                    "max_ms": max(latencies) if latencies else 0,
                    "avg_ms": sum(latencies) / len(latencies) if latencies else 0
                },
                "uptime_seconds": time.time() - self.uptime_start,
            }


# ============================================================================
# Abstract Base Class
# ============================================================================

class SIPAdapterBase(abc.ABC):
    """
    Abstract base class for all SIP adapter implementations.

    All 7 adapters (Asterisk, FreeSWITCH, Kamailio, OpenSIPS, Yate, PJSUA, SIPp)
    must inherit from this class and implement all abstract methods.

    Thread Safety: All public methods are thread-safe. Internal state is protected
    by _lock.

    Philosophy: Wu Lun (五伦) mapping for call relationship hierarchy.
    """

    # Must be overridden by subclass
    adapter_type: str = "unknown"
    SUPPORTED_VERSIONS: Dict[str, List[str]] = {}

    def __init__(
        self,
        config: Dict[str, Any],
        logger: Optional[logging.Logger] = None,
        event_emitter: Optional[EventEmitter] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        """
        Initialize adapter with configuration.

        Args:
            config: Configuration dictionary (required fields: type, host, port, auth)
            logger: Optional logger instance
            event_emitter: Optional event emitter
            metrics_collector: Optional metrics collector
        """
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.event_emitter = event_emitter or EventEmitter(self.logger)
        self.metrics = metrics_collector or MetricsCollector()

        # State
        self._lock = threading.Lock()
        self.connection_state = ConnectionState.DISCONNECTED
        self.connected = False
        self.retry_count = 0

        # Call tracking
        self._active_calls: Dict[str, Dict[str, Any]] = {}
        self._call_history: deque = deque(maxlen=1000)

        # Validate configuration
        self._validate_config()

    # ========================================================================
    # Abstract Methods - MUST IMPLEMENT
    # ========================================================================

    @abc.abstractmethod
    def connect(self, host: str, port: int, auth_config: Dict[str, Any]) -> bool:
        """
        Establish connection to SIP server.

        Args:
            host: Server hostname or IP address
            port: Server port number
            auth_config: Authentication configuration (username, password, realm)

        Returns:
            True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abc.abstractmethod
    def disconnect(self) -> bool:
        """
        Gracefully terminate connection.

        Cleanup:
        - Close all open connections
        - Hangup any active calls
        - Release pooled resources
        - Unregister from registrar (if applicable)

        Returns:
            True if successful

        Raises:
            ConnectionError: If disconnect fails
        """
        pass

    @abc.abstractmethod
    def make_call(
        self,
        from_number: str,
        to_number: str,
        **options
    ) -> str:
        """
        Initiate outbound call.

        Args:
            from_number: Calling number (e.g., "+1234567890", "sip:user@domain")
            to_number: Called number
            options: Optional call parameters
                - timeout: Ring timeout in seconds
                - caller_id_name: Display name
                - headers: Custom SIP headers
                - early_media: Enable early media
                - record: Record call (True/False or format)

        Returns:
            call_id: Unique call identifier

        Raises:
            CallError: If call initiation fails
            ConfigurationError: If required fields missing
        """
        pass

    @abc.abstractmethod
    def hangup(self, call_id: str) -> bool:
        """
        Terminate active call.

        Args:
            call_id: Call identifier from make_call() or incoming call

        Returns:
            True if successful

        Raises:
            CallError: If hangup fails
        """
        pass

    @abc.abstractmethod
    def get_status(self, call_id: str) -> Dict[str, Any]:
        """
        Query current call state and metrics.

        Returns:
        {
            "call_id": "...",
            "state": "connected",  # CallState enum value
            "from_number": "...",
            "to_number": "...",
            "duration": 45.2,  # seconds
            "codec": "PCMA",
            "jitter": 12,  # ms
            "packet_loss": 0.5,  # %
            "rtp_quality": 85,  # 0-100 score
            "details": {...}  # Adapter-specific data
        }

        Raises:
            CallError: If call not found
        """
        pass

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Return comprehensive health metrics.

        Returns:
        {
            "adapter": "asterisk",
            "connected": True,
            "uptime_seconds": 3600,
            "metrics": {
                "active_calls": 5,
                "call_attempts": 142,
                "call_success_rate": 0.94,
                "avg_call_duration": 245,
                "connection_failures": 0,
                "last_error": None,
                "pool_utilization": 0.5,
            },
            "latency": {
                "min_ms": 12,
                "max_ms": 156,
                "avg_ms": 45
            },
            "last_check": "2025-11-11T10:30:45Z",
            "status": "healthy"  # "healthy" | "degraded" | "critical"
        }
        """
        pass

    @abc.abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration schema and values.

        Checks:
        - Required fields present (type, host, port, auth)
        - Value ranges valid (port 1024-65535, timeout > 0, etc.)
        - Enum values valid
        - Cross-field consistency (TLS enabled → cert required)

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        pass

    # ========================================================================
    # Optional Methods - OVERRIDE IF SUPPORTED
    # ========================================================================

    def transfer(
        self,
        call_id: str,
        destination: str,
        attended: bool = False,
        **options
    ) -> bool:
        """
        Blind or attended call transfer.

        Args:
            call_id: Call to transfer
            destination: Transfer destination number
            attended: If True, establish second call before transfer
            options: Adapter-specific options

        Returns:
            True if successful

        Raises:
            CallError: If transfer not supported or fails
        """
        raise NotImplementedError(f"{self.adapter_type} does not support transfer")

    def hold(self, call_id: str) -> bool:
        """
        Place call on hold (local).

        Returns:
            True if successful

        Raises:
            CallError: If hold not supported
        """
        raise NotImplementedError(f"{self.adapter_type} does not support hold")

    def resume(self, call_id: str) -> bool:
        """
        Resume held call.

        Returns:
            True if successful

        Raises:
            CallError: If resume fails
        """
        raise NotImplementedError(f"{self.adapter_type} does not support resume")

    def conference(self, call_ids: List[str], **options) -> str:
        """
        Merge multiple calls into conference.

        Args:
            call_ids: List of call IDs to conference
            options: Conference options (record, moderator, etc.)

        Returns:
            conference_id: Unique conference identifier

        Raises:
            CallError: If conference not supported
        """
        raise NotImplementedError(f"{self.adapter_type} does not support conference")

    def record(
        self,
        call_id: str,
        format: str = "wav",
        **options
    ) -> bool:
        """
        Record call audio.

        Args:
            call_id: Call to record
            format: Audio format (wav, mp3, gsm, ulaw, alaw)
            options: Record options (stereo, append, etc.)

        Returns:
            True if recording started

        Raises:
            CallError: If recording not supported
        """
        raise NotImplementedError(f"{self.adapter_type} does not support recording")

    def get_call_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve recent call history.

        Returns:
            List of call dictionaries with state history
        """
        with self._lock:
            return list(self._call_history)[-limit:]

    def get_cdr(self, call_id: str) -> Dict[str, Any]:
        """
        Retrieve Call Detail Record (CDR).

        Returns:
        {
            "call_id": "...",
            "from_number": "...",
            "to_number": "...",
            "start_time": "2025-11-11T10:30:45Z",
            "end_time": "2025-11-11T10:31:15Z",
            "duration": 30.0,
            "result": "completed",  # completed, no_answer, busy, failed
            "hangup_cause": "normal_clearing",
            "cost": 0.15,
            "details": {...}
        }

        Raises:
            CallError: If CDR not found
        """
        raise NotImplementedError(f"{self.adapter_type} does not support CDR")

    # ========================================================================
    # Shared Utilities
    # ========================================================================

    @staticmethod
    def retry_with_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff_base: float = 2.0,
        max_delay: float = 300.0,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
    ) -> Any:
        """
        Execute function with exponential backoff retry.

        Formula: delay = min(base_delay * (backoff_base ^ attempt), max_delay)

        Example with defaults:
            Attempt 1: 1s delay
            Attempt 2: 2s delay
            Attempt 3: 4s delay

        Args:
            func: Function to execute
            max_retries: Maximum retry attempts
            base_delay: Initial delay in seconds
            backoff_base: Exponential backoff multiplier
            max_delay: Maximum delay cap
            on_retry: Optional callback(attempt, exception) on each retry

        Returns:
            Function result on success

        Raises:
            Original exception if all retries exhausted
        """
        attempt = 0
        last_exception = None

        while attempt <= max_retries:
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = min(
                        base_delay * (backoff_base ** attempt),
                        max_delay
                    )
                    if on_retry:
                        on_retry(attempt + 1, e)
                    time.sleep(delay)
                    attempt += 1
                else:
                    break

        raise last_exception

    def _validate_config(self) -> None:
        """
        Validate configuration at initialization.

        Raises:
            ConfigurationError: If validation fails
        """
        required_fields = ["type", "host", "port", "auth"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required config field: {field}")

        if not self.validate_config(self.config):
            raise ConfigurationError("Configuration validation failed")

    def generate_call_id(self) -> str:
        """
        Generate unique call ID following IF.TTT protocol.

        Format: if://call/{uuid}
        """
        return f"if://call/{uuid.uuid4()}"

    def generate_request_id(self) -> str:
        """
        Generate unique request ID for traceability.

        Format: if://request/{uuid}
        """
        return f"if://request/{uuid.uuid4()}"

    # ========================================================================
    # Event Emission
    # ========================================================================

    def emit_call_state_changed(
        self,
        call_id: str,
        state: CallState,
        **kwargs
    ) -> None:
        """Emit call state change event."""
        event = CallStateEvent(call_id=call_id, state=state, **kwargs)
        self.event_emitter.emit("call_state_changed", event)
        self._update_call_history(event.to_dict())

    def emit_incoming_call(
        self,
        call_id: str,
        from_number: str,
        to_number: str,
        accept_callback: Optional[Callable] = None,
        reject_callback: Optional[Callable] = None,
        **kwargs
    ) -> None:
        """Emit incoming call event."""
        event = IncomingCallEvent(
            call_id=call_id,
            from_number=from_number,
            to_number=to_number,
            accept_callback=accept_callback,
            reject_callback=reject_callback,
            **kwargs
        )
        self.event_emitter.emit("incoming_call", event)

    def emit_error(
        self,
        code: int,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        call_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Emit error event."""
        event = ErrorEvent(
            error_code=code,
            error_message=message,
            severity=severity,
            call_id=call_id,
            **kwargs
        )
        self.event_emitter.emit("error", event)

    def emit_connection_state_changed(
        self,
        connected: bool,
        reason: str,
        retry_count: int = 0,
        **kwargs
    ) -> None:
        """Emit connection state change event."""
        event = ConnectionStateEvent(
            connected=connected,
            reason=reason,
            retry_count=retry_count,
            **kwargs
        )
        self.event_emitter.emit("connection_state_changed", event)

    # ========================================================================
    # State Management
    # ========================================================================

    def _update_connection_state(
        self,
        state: ConnectionState,
        reason: str = ""
    ) -> None:
        """Update connection state and emit event."""
        with self._lock:
            if self.connection_state != state:
                self.connection_state = state
                self.connected = (state == ConnectionState.CONNECTED)

        self.emit_connection_state_changed(
            connected=self.connected,
            reason=reason,
            retry_count=self.retry_count
        )

    def _add_active_call(self, call_id: str, call_data: Dict[str, Any]) -> None:
        """Track active call."""
        with self._lock:
            self._active_calls[call_id] = call_data

    def _remove_active_call(self, call_id: str) -> None:
        """Remove call from tracking."""
        with self._lock:
            self._active_calls.pop(call_id, None)

    def _get_active_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve active call data."""
        with self._lock:
            return self._active_calls.get(call_id)

    def _update_call_history(self, call_record: Dict[str, Any]) -> None:
        """Add record to call history."""
        with self._lock:
            self._call_history.append(call_record)

    def _get_active_calls_count(self) -> int:
        """Get count of active calls."""
        with self._lock:
            return len(self._active_calls)

    # ========================================================================
    # Wu Lun (五伦) Relationship Mapping
    # ========================================================================

    @staticmethod
    def get_wu_lun_weight(relationship: str) -> float:
        """
        Get priority weight for Wu Lun relationship.

        Based on Confucian Five Relationships (五伦):
        - 君臣 (Ruler-Subject): 0.95 - Call initiator authority
        - 父子 (Parent-Child): 0.85 - Master/transferred call
        - 夫婦 (Spouses): 0.80 - Conference participants
        - 兄弟 (Siblings): 0.75 - Peer adapters
        - 朋友 (Friends): 0.70 - Agent operators

        Args:
            relationship: One of above relationship types

        Returns:
            Priority weight (0.0-1.0)
        """
        weights = {
            "君臣": 0.95,
            "ruler_subject": 0.95,
            "parent_child": 0.85,
            "父子": 0.85,
            "spouse": 0.80,
            "夫婦": 0.80,
            "sibling": 0.75,
            "兄弟": 0.75,
            "friend": 0.70,
            "朋友": 0.70,
        }
        return weights.get(relationship, 0.5)

    # ========================================================================
    # Public Interface for Subclasses
    # ========================================================================

    def register_event_handler(
        self,
        event_type: str,
        callback: Callable
    ) -> None:
        """
        Register callback for event type.

        Supported events:
        - "call_state_changed": CallStateEvent
        - "incoming_call": IncomingCallEvent
        - "error": ErrorEvent
        - "connection_state_changed": ConnectionStateEvent
        """
        self.event_emitter.on(event_type, callback)

    def unregister_event_handler(
        self,
        event_type: str,
        callback: Callable
    ) -> None:
        """Unregister callback."""
        self.event_emitter.off(event_type, callback)

    def get_connection_state(self) -> ConnectionState:
        """Get current connection state."""
        with self._lock:
            return self.connection_state

    def is_connected(self) -> bool:
        """Check if adapter is connected."""
        with self._lock:
            return self.connected

    def get_adapter_info(self) -> Dict[str, Any]:
        """
        Get adapter information and capabilities.

        Returns:
        {
            "type": "asterisk",
            "version": "1.0.0",
            "supported_versions": {...},
            "connected": True,
            "supports": {
                "transfer": True,
                "hold": True,
                "conference": True,
                "recording": True
            },
            "config": {...}  # (sanitized, no credentials)
        }
        """
        supports = {
            "transfer": self._supports_method("transfer"),
            "hold": self._supports_method("hold"),
            "resume": self._supports_method("resume"),
            "conference": self._supports_method("conference"),
            "recording": self._supports_method("record"),
            "cdr": self._supports_method("get_cdr"),
        }

        return {
            "type": self.adapter_type,
            "version": "1.0.0",
            "supported_versions": self.SUPPORTED_VERSIONS,
            "connected": self.is_connected(),
            "supports": supports,
        }

    @staticmethod
    def _supports_method(method_name: str) -> bool:
        """Check if method is implemented (not abstract)."""
        # This is a simplification; in practice you'd check the method implementation
        return not getattr(SIPAdapterBase, method_name).__isabstractmethod__


# ============================================================================
# Factory Function
# ============================================================================

def create_adapter(
    config: Dict[str, Any],
    logger: Optional[logging.Logger] = None,
    event_emitter: Optional[EventEmitter] = None,
    metrics_collector: Optional[MetricsCollector] = None,
) -> SIPAdapterBase:
    """
    Factory function to create appropriate adapter based on config.

    This will be extended when concrete adapters are implemented.

    Args:
        config: Configuration dictionary with 'type' field
        logger: Optional logger
        event_emitter: Optional event emitter
        metrics_collector: Optional metrics collector

    Returns:
        Concrete adapter instance

    Raises:
        ConfigurationError: If type not recognized
    """
    adapter_type = config.get("type", "").lower()

    # Placeholder: will be populated when concrete adapters created
    adapters = {
        # "asterisk": AsteriskAdapter,
        # "freeswitch": FreeSwitchAdapter,
        # "kamailio": KamailioAdapter,
        # "opensips": OpenSIPSAdapter,
        # "yate": YateAdapter,
        # "pjsua": PJSUAAdapter,
        # "sipp": SIPpAdapter,
    }

    if adapter_type not in adapters:
        raise ConfigurationError(
            f"Unknown adapter type: {adapter_type}. "
            f"Supported: {list(adapters.keys())}"
        )

    return adapters[adapter_type](
        config,
        logger=logger,
        event_emitter=event_emitter,
        metrics_collector=metrics_collector,
    )


if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.DEBUG)

    # Create base configuration
    config = {
        "type": "asterisk",
        "host": "192.168.1.100",
        "port": 5038,
        "auth": {
            "username": "admin",
            "password": "secret",
            "realm": "asterisk.local"
        },
        "timeout": 30,
        "retry_count": 3,
        "pool_size": 10,
    }

    print("SIPAdapterBase Configuration Schema:")
    print(json.dumps(config, indent=2))
    print("\nAdapter types: asterisk, freeswitch, kamailio, opensips, yate, pjsua, sipp")
