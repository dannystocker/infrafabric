"""
Unified Production Adapter Base Class - IF.optimise Protocol Implementation

This module provides the abstract base class for all production infrastructure adapters
(vMix, OBS, Home Assistant, and other control systems).

Philosophy: Confucian Wu Lun (五伦) relationship mapping ensures ethical control hierarchy.
Protocol: IF.TTT (Traceable/Transparent/Trustworthy) compliance for all operations.
Logging: IF.witness integration for comprehensive audit trails.
Metrics: IF.optimise integration for performance optimization.

Author: Agent 8 (IF.bus architecture)
Version: 1.0.0
Date: 2025-11-12
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
    Any, Callable, Dict, List, Optional, Union, Tuple, Set
)
from datetime import datetime
from collections import deque
import json


# ============================================================================
# Enums & Data Classes
# ============================================================================

class InstanceState(str, Enum):
    """Standard instance state machine for all adapters."""
    CREATED = "created"
    DISCOVERING = "discovering"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"


class AdapterConnectionState(str, Enum):
    """Adapter-level connection state."""
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


class CommandType(str, Enum):
    """Types of commands that can be executed."""
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    CONFIGURE = "configure"
    QUERY = "query"
    CUSTOM = "custom"


@dataclass
class InstanceStateEvent:
    """Event emitted when instance state changes."""
    instance_name: str
    instance_id: str
    state: InstanceState
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['state'] = self.state.value
        data['timestamp'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


@dataclass
class CommandExecutionEvent:
    """Event emitted on command execution."""
    instance_name: str
    command: str
    command_type: CommandType
    success: bool
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['command_type'] = self.command_type.value
        data['timestamp'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


@dataclass
class DiscoveryEvent:
    """Event emitted on instance discovery."""
    instance_count: int
    new_instances: List[str]
    removed_instances: List[str]
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = datetime.fromtimestamp(self.timestamp).isoformat()
        return data


@dataclass
class ErrorEvent:
    """Event emitted on error."""
    error_code: int
    error_message: str
    severity: ErrorSeverity
    timestamp: float = field(default_factory=time.time)
    instance_name: Optional[str] = None
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
    """Event emitted when adapter connection state changes."""
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

class ProductionAdapterError(Exception):
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


class ConnectionError(ProductionAdapterError):
    """Connection-level errors (typically retryable)."""

    def __init__(self, message: str, code: int = 503, **kwargs):
        super().__init__(code=code, message=message, severity=ErrorSeverity.ERROR, **kwargs)


class InstanceError(ProductionAdapterError):
    """Instance-level errors."""

    def __init__(self, message: str, code: int = 500, **kwargs):
        super().__init__(code=code, message=message, **kwargs)


class CommandExecutionError(ProductionAdapterError):
    """Command execution errors."""

    def __init__(self, message: str, code: int = 502, **kwargs):
        super().__init__(code=code, message=message, **kwargs)


class ConfigurationError(ProductionAdapterError):
    """Configuration validation errors (not retryable)."""

    def __init__(self, message: str, code: int = 400):
        super().__init__(
            code=code,
            message=message,
            severity=ErrorSeverity.ERROR,
            retryable=False
        )


class TimeoutError(ProductionAdapterError):
    """Operation timeout (retryable)."""

    def __init__(self, message: str, code: int = 504, **kwargs):
        super().__init__(
            code=code,
            message=message,
            severity=ErrorSeverity.WARNING,
            retryable=True,
            **kwargs
        )


class DiscoveryError(ProductionAdapterError):
    """Instance discovery errors."""

    def __init__(self, message: str, code: int = 506, **kwargs):
        super().__init__(code=code, message=message, **kwargs)


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
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(handler(event_data))
                        else:
                            loop.run_until_complete(handler(event_data))
                    except RuntimeError:
                        pass
                else:
                    handler(event_data)
            except Exception as e:
                self.logger.exception(f"Error in event handler for {event_type}: {e}")


class MetricsCollector:
    """
    Thread-safe metrics collection for production infrastructure.

    Tracks: command counts, success rates, latencies, instance states.
    IF.optimise integration for performance optimization.
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self._lock = threading.Lock()

        # Command metrics
        self.total_commands = 0
        self.successful_commands = 0
        self.failed_commands = 0
        self.command_durations: deque = deque(maxlen=window_size)

        # Instance metrics
        self.total_instances = 0
        self.connected_instances = 0
        self.error_instances = 0

        # Connection metrics
        self.connection_failures = 0
        self.last_error: Optional[str] = None
        self.uptime_start = time.time()

        # Latency metrics
        self.latencies: deque = deque(maxlen=window_size)

    def record_command(self, success: bool, duration_ms: Optional[float] = None) -> None:
        """Record command outcome."""
        with self._lock:
            self.total_commands += 1
            if success:
                self.successful_commands += 1
            else:
                self.failed_commands += 1
            if duration_ms is not None:
                self.command_durations.append(duration_ms)

    def record_latency(self, latency_ms: float) -> None:
        """Record latency measurement."""
        with self._lock:
            self.latencies.append(latency_ms)

    def record_connection_failure(self, error: str) -> None:
        """Record connection failure."""
        with self._lock:
            self.connection_failures += 1
            self.last_error = error

    def update_instance_count(self, total: int, connected: int, errors: int) -> None:
        """Update instance counts."""
        with self._lock:
            self.total_instances = total
            self.connected_instances = connected
            self.error_instances = errors

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        with self._lock:
            success_rate = (
                self.successful_commands / self.total_commands
                if self.total_commands > 0
                else 0
            )

            latencies = list(self.latencies) if self.latencies else [0]
            durations = list(self.command_durations) if self.command_durations else [0]

            return {
                "total_instances": self.total_instances,
                "connected_instances": self.connected_instances,
                "error_instances": self.error_instances,
                "command_attempts": self.total_commands,
                "command_success_rate": success_rate,
                "failed_commands": self.failed_commands,
                "avg_command_duration_ms": sum(durations) / len(durations) if durations else 0,
                "connection_failures": self.connection_failures,
                "last_error": self.last_error,
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

class ProductionAdapterBase(abc.ABC):
    """
    Abstract base class for all production infrastructure adapters.

    All adapters (vMix, OBS, Home Assistant, etc.) must inherit from this class
    and implement all abstract methods.

    Thread Safety: All public methods are thread-safe. Internal state is protected
    by _lock.

    Philosophy: Wu Lun (五伦) mapping for instance relationship hierarchy.
    Logging: IF.witness integration for comprehensive audit trails.
    Metrics: IF.optimise integration for performance data.
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
        self.connection_state = AdapterConnectionState.DISCONNECTED
        self.connected = False
        self.retry_count = 0

        # Instance registry
        self._instances: Dict[str, Dict[str, Any]] = {}
        self._instance_states: Dict[str, InstanceState] = {}
        self._command_history: deque = deque(maxlen=1000)

        # Validate configuration
        self._validate_config()

    # ========================================================================
    # Abstract Methods - MUST IMPLEMENT
    # ========================================================================

    @abc.abstractmethod
    def discover_instances(self, network_config: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Auto-discover instances on network.

        Args:
            network_config: Optional network discovery configuration

        Returns:
            List of discovered instance names/IDs

        Raises:
            DiscoveryError: If discovery fails
        """
        pass

    @abc.abstractmethod
    def add_instance(self, name: str, config: Dict[str, Any]) -> str:
        """
        Add instance to registry.

        Args:
            name: Friendly instance name
            config: Instance configuration (host, port, credentials, etc.)

        Returns:
            instance_id: Unique instance identifier

        Raises:
            ConfigurationError: If config invalid
            InstanceError: If instance cannot be added
        """
        pass

    @abc.abstractmethod
    def remove_instance(self, name: str) -> bool:
        """
        Remove instance from registry.

        Args:
            name: Instance name to remove

        Returns:
            True if successful

        Raises:
            InstanceError: If instance not found or removal fails
        """
        pass

    @abc.abstractmethod
    def get_instance_status(self, name: str) -> Dict[str, Any]:
        """
        Get instance health/status.

        Returns:
        {
            "instance_id": "...",
            "name": "...",
            "state": "connected",  # InstanceState enum value
            "connected": True,
            "last_seen": "2025-11-12T10:30:45Z",
            "uptime_seconds": 3600,
            "command_count": 42,
            "error_count": 2,
            "details": {...}  # Adapter-specific data
        }

        Raises:
            InstanceError: If instance not found
        """
        pass

    @abc.abstractmethod
    def execute_command(
        self,
        name: str,
        command: str,
        command_type: CommandType = CommandType.CUSTOM,
        **params
    ) -> Dict[str, Any]:
        """
        Execute command on instance.

        Args:
            name: Instance name
            command: Command to execute
            command_type: Type of command
            params: Command-specific parameters

        Returns:
        {
            "success": True,
            "result": {...},  # Command-specific results
            "duration_ms": 125.5
        }

        Raises:
            CommandExecutionError: If command fails
            InstanceError: If instance not found
            TimeoutError: If command times out
        """
        pass

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Return comprehensive health metrics.

        Returns:
        {
            "adapter": "vmix",
            "connected": True,
            "uptime_seconds": 3600,
            "instances": {
                "total": 5,
                "connected": 4,
                "errors": 1
            },
            "metrics": {
                "command_attempts": 142,
                "command_success_rate": 0.94,
                "avg_command_duration_ms": 125.5,
                "connection_failures": 0,
                "last_error": None,
            },
            "latency": {
                "min_ms": 12,
                "max_ms": 156,
                "avg_ms": 45
            },
            "last_check": "2025-11-12T10:30:45Z",
            "status": "healthy"  # "healthy" | "degraded" | "critical"
        }
        """
        pass

    @abc.abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration schema and values.

        Checks:
        - Required fields present
        - Value ranges valid
        - Enum values valid
        - Cross-field consistency

        Returns:
            True if valid

        Raises:
            ConfigurationError: If validation fails
        """
        pass

    # ========================================================================
    # Optional Methods - OVERRIDE IF SUPPORTED
    # ========================================================================

    def connect(self, host: str, port: int, auth_config: Dict[str, Any]) -> bool:
        """
        Establish connection to production infrastructure.

        Args:
            host: Server hostname or IP address
            port: Server port number
            auth_config: Authentication configuration

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
        """
        raise NotImplementedError(f"{self.adapter_type} does not support explicit connect")

    def disconnect(self) -> bool:
        """
        Gracefully terminate connection.

        Returns:
            True if successful

        Raises:
            ConnectionError: If disconnect fails
        """
        raise NotImplementedError(f"{self.adapter_type} does not support explicit disconnect")

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
        required_fields = ["type"]
        for field in required_fields:
            if field not in self.config:
                raise ConfigurationError(f"Missing required config field: {field}")

        if not self.validate_config(self.config):
            raise ConfigurationError("Configuration validation failed")

    def generate_instance_id(self) -> str:
        """
        Generate unique instance ID following IF.TTT protocol.

        Format: if://instance/{uuid}
        """
        return f"if://instance/{uuid.uuid4()}"

    def generate_request_id(self) -> str:
        """
        Generate unique request ID for traceability.

        Format: if://request/{uuid}
        """
        return f"if://request/{uuid.uuid4()}"

    # ========================================================================
    # Event Emission
    # ========================================================================

    def emit_instance_state_changed(
        self,
        instance_name: str,
        instance_id: str,
        state: InstanceState,
        **kwargs
    ) -> None:
        """Emit instance state change event."""
        event = InstanceStateEvent(
            instance_name=instance_name,
            instance_id=instance_id,
            state=state,
            **kwargs
        )
        self.event_emitter.emit("instance_state_changed", event)
        self._update_command_history(event.to_dict())

    def emit_command_execution(
        self,
        instance_name: str,
        command: str,
        command_type: CommandType,
        success: bool,
        duration_ms: float = 0.0,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        **kwargs
    ) -> None:
        """Emit command execution event."""
        event = CommandExecutionEvent(
            instance_name=instance_name,
            command=command,
            command_type=command_type,
            success=success,
            duration_ms=duration_ms,
            result=result or {},
            error=error,
            **kwargs
        )
        self.event_emitter.emit("command_execution", event)
        self._update_command_history(event.to_dict())

    def emit_discovery(
        self,
        instance_count: int,
        new_instances: List[str],
        removed_instances: List[str],
        **kwargs
    ) -> None:
        """Emit discovery event."""
        event = DiscoveryEvent(
            instance_count=instance_count,
            new_instances=new_instances,
            removed_instances=removed_instances,
            **kwargs
        )
        self.event_emitter.emit("discovery", event)

    def emit_error(
        self,
        code: int,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        instance_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """Emit error event."""
        event = ErrorEvent(
            error_code=code,
            error_message=message,
            severity=severity,
            instance_name=instance_name,
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
        state: AdapterConnectionState,
        reason: str = ""
    ) -> None:
        """Update connection state and emit event."""
        with self._lock:
            if self.connection_state != state:
                self.connection_state = state
                self.connected = (state == AdapterConnectionState.CONNECTED)

        self.emit_connection_state_changed(
            connected=self.connected,
            reason=reason,
            retry_count=self.retry_count
        )

    def _add_instance(self, instance_id: str, instance_data: Dict[str, Any]) -> None:
        """Track instance."""
        with self._lock:
            self._instances[instance_id] = instance_data
            self._instance_states[instance_id] = InstanceState.CREATED

    def _remove_instance(self, instance_id: str) -> None:
        """Remove instance from tracking."""
        with self._lock:
            self._instances.pop(instance_id, None)
            self._instance_states.pop(instance_id, None)

    def _get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve instance data."""
        with self._lock:
            return self._instances.get(instance_id)

    def _update_instance_state(self, instance_id: str, state: InstanceState) -> None:
        """Update instance state."""
        with self._lock:
            self._instance_states[instance_id] = state

    def _get_instance_state(self, instance_id: str) -> Optional[InstanceState]:
        """Get instance state."""
        with self._lock:
            return self._instance_states.get(instance_id)

    def _update_command_history(self, command_record: Dict[str, Any]) -> None:
        """Add record to command history."""
        with self._lock:
            self._command_history.append(command_record)

    def _get_instances_count(self) -> int:
        """Get count of managed instances."""
        with self._lock:
            return len(self._instances)

    # ========================================================================
    # Wu Lun (五伦) Relationship Mapping
    # ========================================================================

    @staticmethod
    def get_wu_lun_weight(relationship: str) -> float:
        """
        Get priority weight for Wu Lun relationship.

        Based on Confucian Five Relationships (五伦):
        - 君臣 (Ruler-Subject): 0.95 - Primary/master instance
        - 父子 (Parent-Child): 0.85 - Dependent instances
        - 夫婦 (Spouses): 0.80 - Mirrored instances
        - 兄弟 (Siblings): 0.75 - Peer instances
        - 朋友 (Friends): 0.70 - Secondary instances

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
        - "instance_state_changed": InstanceStateEvent
        - "command_execution": CommandExecutionEvent
        - "discovery": DiscoveryEvent
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

    def get_connection_state(self) -> AdapterConnectionState:
        """Get current connection state."""
        with self._lock:
            return self.connection_state

    def is_connected(self) -> bool:
        """Check if adapter is connected."""
        with self._lock:
            return self.connected

    def get_command_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent command history."""
        with self._lock:
            return list(self._command_history)[-limit:]

    def get_adapter_info(self) -> Dict[str, Any]:
        """
        Get adapter information and capabilities.

        Returns:
        {
            "type": "vmix",
            "version": "1.0.0",
            "supported_versions": {...},
            "connected": True,
            "instance_count": 5,
            "supports": {
                "discovery": True,
                "instance_management": True,
                "command_execution": True
            },
            "config": {...}  # (sanitized, no credentials)
        }
        """
        supports = {
            "discovery": self._supports_method("discover_instances"),
            "instance_management": self._supports_method("add_instance"),
            "command_execution": self._supports_method("execute_command"),
        }

        return {
            "type": self.adapter_type,
            "version": "1.0.0",
            "supported_versions": self.SUPPORTED_VERSIONS,
            "connected": self.is_connected(),
            "instance_count": self._get_instances_count(),
            "supports": supports,
        }

    @staticmethod
    def _supports_method(method_name: str) -> bool:
        """Check if method is implemented (not abstract)."""
        return not getattr(ProductionAdapterBase, method_name).__isabstractmethod__


# ============================================================================
# Factory Function
# ============================================================================

def create_adapter(
    config: Dict[str, Any],
    logger: Optional[logging.Logger] = None,
    event_emitter: Optional[EventEmitter] = None,
    metrics_collector: Optional[MetricsCollector] = None,
) -> ProductionAdapterBase:
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
        # "vmix": VMixAdapter,
        # "obs": OBSAdapter,
        # "home_assistant": HomeAssistantAdapter,
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
        "type": "vmix",
        "host": "192.168.1.100",
        "port": 8088,
        "auth": {
            "username": "admin",
            "password": "secret"
        },
        "timeout": 30,
        "retry_count": 3,
        "discovery_timeout": 5,
    }

    print("ProductionAdapterBase Configuration Schema:")
    print(json.dumps(config, indent=2))
    print("\nAdapter types: vmix, obs, home_assistant")
