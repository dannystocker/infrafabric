#!/usr/bin/env python3
"""
InfraFabric Structured Logging Library
Purpose: Provides standardized JSON logging with correlation ID tracking for all agents
Reference: if://code/logging-library/2025-11-30

Features:
  - Structured JSON output
  - Correlation ID propagation (request, task, or swarm scoped)
  - Multi-component logging
  - Performance metrics collection
  - Async non-blocking writes
  - Batch flushing to reduce I/O
  - IF.citation integration
  - Compatible with Fluent Bit, Loki, Elasticsearch aggregation

Usage:
    from logging_library import StructuredLogger, set_correlation_id

    logger = StructuredLogger(
        agent_id="A1-haiku-001",
        component="redis_bus",
        environment="production"
    )

    # Set request-scoped correlation ID
    set_correlation_id("req-abc123def456")

    logger.info(
        "Task claimed successfully",
        context={"task_id": "task:001", "duration_ms": 2.1},
        if_citation="if://log/redis-task-claim"
    )
"""

import asyncio
import contextvars
import json
import logging
import os
import socket
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading
from queue import Queue

# =============================================================================
# ENUMERATIONS & TYPES
# =============================================================================


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class CorrelationIDType(Enum):
    """Types of correlation IDs"""
    REQUEST = "req"     # User request
    TASK = "task"       # Background task
    SWARM = "swarm"     # Swarm operation


class Component(Enum):
    """Known components in InfraFabric"""
    REDIS_BUS = "redis_bus"
    CHROMADB = "chromadb"
    AUDIT_SYSTEM = "audit_system"
    OPENWEBUI = "openwebui"
    SECURITY = "security"
    RATE_LIMITER = "rate_limiter"
    CONTEXT_MANAGER = "context_manager"
    TASK_SCHEDULER = "task_scheduler"
    MESSAGE_HANDLER = "message_handler"
    API_GATEWAY = "api_gateway"
    MEMORY_SYSTEM = "memory_system"
    GUARDIAN_COUNCIL = "guardian_council"
    SYSTEM = "system"


# =============================================================================
# CONTEXT VARIABLES (for correlation ID tracking)
# =============================================================================

_correlation_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'correlation_id',
    default=None
)

_parent_agent_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'parent_agent_id',
    default=None
)

_trace_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'trace_id',
    default=None
)


def set_correlation_id(correlation_id: str, id_type: Optional[CorrelationIDType] = None) -> str:
    """
    Set correlation ID for this context (request/task/swarm).

    Args:
        correlation_id: ID to set (will generate if not provided)
        id_type: Type of correlation ID (request/task/swarm)

    Returns:
        The correlation ID set
    """
    if not correlation_id:
        id_prefix = id_type.value if id_type else "req"
        correlation_id = f"{id_prefix}-{uuid.uuid4().hex[:32]}"

    _correlation_id_context.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str:
    """Get current correlation ID or generate new one"""
    cid = _correlation_id_context.get()
    if not cid:
        cid = set_correlation_id(None, CorrelationIDType.REQUEST)
    return cid


def set_parent_agent_id(agent_id: str) -> None:
    """Set parent agent ID for hierarchical operations"""
    _parent_agent_context.set(agent_id)


def set_trace_id(trace_id: str) -> None:
    """Set distributed trace ID"""
    _trace_id_context.set(trace_id)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class LogEntry:
    """Single structured log entry"""
    timestamp: str
    level: str
    correlation_id: str
    agent_id: str
    component: str
    message: str
    severity: Optional[str] = None
    service: str = "infrafabric"
    environment: str = "development"
    context: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    if_citation: Optional[str] = None
    trace_id: Optional[str] = None
    parent_agent_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    hostname: str = field(default_factory=socket.gethostname)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Convert to JSON string for logging"""
        data = asdict(self)
        # Remove None values to keep JSON clean
        data = {k: v for k, v in data.items() if v is not None}
        return json.dumps(data, default=str)


# =============================================================================
# STRUCTURED LOGGER CLASS
# =============================================================================

class StructuredLogger:
    """
    Structured JSON logger for InfraFabric agents.

    Features:
      - Automatic JSON formatting
      - Correlation ID propagation
      - Batch writing for efficiency
      - Async non-blocking operations
      - Compatible with Fluent Bit/Loki/Elasticsearch
    """

    def __init__(
        self,
        agent_id: str,
        component: str,
        environment: str = "development",
        service: str = "infrafabric",
        log_level: LogLevel = LogLevel.INFO,
        log_path: Optional[str] = None,
        batch_size: int = 50,
        flush_interval_seconds: float = 5.0,
        async_mode: bool = True
    ):
        """
        Initialize structured logger.

        Args:
            agent_id: Unique agent identifier (e.g., A1-haiku-001)
            component: Component name
            environment: Deployment environment (development/staging/production)
            service: Service name
            log_level: Minimum log level to output
            log_path: Path to write logs (None = stdout)
            batch_size: Number of entries to batch before flushing
            flush_interval_seconds: Time between batch flushes
            async_mode: Use async/threaded writing
        """
        self.agent_id = agent_id
        self.component = component
        self.environment = environment
        self.service = service
        self.log_level = log_level
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds

        # Setup logging backend
        self.log_path = log_path or f"/var/log/infrafabric/{agent_id}.log"
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # Batch queue for async writes
        self.batch_queue: List[LogEntry] = []
        self.batch_lock = threading.Lock()

        # Async flush thread
        self.async_mode = async_mode
        if async_mode:
            self._start_flush_thread()

    def _start_flush_thread(self) -> None:
        """Start background thread for periodic batch flushing"""
        def flush_loop():
            while True:
                try:
                    asyncio.sleep(self.flush_interval_seconds)
                    self._flush_batch()
                except Exception as e:
                    print(f"Flush error: {e}", file=sys.stderr)

        thread = threading.Thread(target=flush_loop, daemon=True)
        thread.start()

    def _should_log(self, level: LogLevel) -> bool:
        """Check if level should be logged"""
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.FATAL]
        min_idx = level_order.index(self.log_level)
        current_idx = level_order.index(level)
        return current_idx >= min_idx

    def _write_entry(self, entry: LogEntry) -> None:
        """Write single log entry (batched)"""
        if not self._should_log(LogLevel[entry.level]):
            return

        with self.batch_lock:
            self.batch_queue.append(entry)
            if len(self.batch_queue) >= self.batch_size:
                self._flush_batch()

    def _flush_batch(self) -> None:
        """Flush batch queue to storage"""
        with self.batch_lock:
            if not self.batch_queue:
                return

            entries = self.batch_queue.copy()
            self.batch_queue.clear()

        # Write to file and stdout
        try:
            with open(self.log_path, "a") as f:
                for entry in entries:
                    f.write(entry.to_json() + "\n")

            # Also write to stdout for container logging
            for entry in entries:
                print(entry.to_json(), file=sys.stdout)

        except Exception as e:
            print(f"Failed to write logs: {e}", file=sys.stderr)

    # =========================================================================
    # LOGGING METHODS
    # =========================================================================

    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        if_citation: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Log DEBUG message (verbose details)"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=LogLevel.DEBUG.value,
            correlation_id=get_correlation_id(),
            agent_id=self.agent_id,
            component=self.component,
            message=message,
            environment=self.environment,
            service=self.service,
            context=context or {},
            if_citation=if_citation,
            trace_id=_trace_id_context.get(),
            parent_agent_id=_parent_agent_context.get(),
            tags=tags or []
        )
        self._write_entry(entry)

    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        if_citation: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Log INFO message (normal operations)"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=LogLevel.INFO.value,
            correlation_id=get_correlation_id(),
            agent_id=self.agent_id,
            component=self.component,
            message=message,
            environment=self.environment,
            service=self.service,
            context=context or {},
            if_citation=if_citation,
            trace_id=_trace_id_context.get(),
            parent_agent_id=_parent_agent_context.get(),
            tags=tags or []
        )
        self._write_entry(entry)

    def warn(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        if_citation: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Log WARN message (recoverable issues)"""
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=LogLevel.WARN.value,
            correlation_id=get_correlation_id(),
            agent_id=self.agent_id,
            component=self.component,
            message=message,
            severity="medium",
            environment=self.environment,
            service=self.service,
            context=context or {},
            if_citation=if_citation,
            trace_id=_trace_id_context.get(),
            parent_agent_id=_parent_agent_context.get(),
            tags=tags or []
        )
        self._write_entry(entry)

    def error(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
        if_citation: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Log ERROR message (failures requiring attention)"""
        error_dict = None
        if exception:
            import traceback
            error_dict = {
                "type": exception.__class__.__name__,
                "message": str(exception),
                "stack_trace": traceback.format_exc()
            }
            if error_code:
                error_dict["code"] = error_code

        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=LogLevel.ERROR.value,
            correlation_id=get_correlation_id(),
            agent_id=self.agent_id,
            component=self.component,
            message=message,
            severity="high",
            environment=self.environment,
            service=self.service,
            context=context or {},
            error=error_dict,
            if_citation=if_citation,
            trace_id=_trace_id_context.get(),
            parent_agent_id=_parent_agent_context.get(),
            tags=tags or []
        )
        self._write_entry(entry)

    def fatal(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
        if_citation: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Log FATAL message (system-wide failures)"""
        error_dict = None
        if exception:
            import traceback
            error_dict = {
                "type": exception.__class__.__name__,
                "message": str(exception),
                "stack_trace": traceback.format_exc()
            }
            if error_code:
                error_dict["code"] = error_code

        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=LogLevel.FATAL.value,
            correlation_id=get_correlation_id(),
            agent_id=self.agent_id,
            component=self.component,
            message=message,
            severity="critical",
            environment=self.environment,
            service=self.service,
            context=context or {},
            error=error_dict,
            if_citation=if_citation,
            trace_id=_trace_id_context.get(),
            parent_agent_id=_parent_agent_context.get(),
            tags=tags or []
        )
        self._write_entry(entry)

    def log_performance(
        self,
        message: str,
        duration_ms: float,
        memory_mb: Optional[float] = None,
        cpu_percent: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        if_citation: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> None:
        """Log performance metrics"""
        perf = {"duration_ms": duration_ms}
        if memory_mb is not None:
            perf["memory_mb"] = memory_mb
        if cpu_percent is not None:
            perf["cpu_percent"] = cpu_percent

        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=LogLevel.INFO.value,
            correlation_id=get_correlation_id(),
            agent_id=self.agent_id,
            component=self.component,
            message=message,
            environment=self.environment,
            service=self.service,
            context=context or {},
            performance=perf,
            if_citation=if_citation,
            trace_id=_trace_id_context.get(),
            parent_agent_id=_parent_agent_context.get(),
            tags=tags or []
        )
        self._write_entry(entry)

    def flush(self) -> None:
        """Force flush pending batch"""
        self._flush_batch()


# =============================================================================
# CONVENIENCE FUNCTIONS & GLOBAL LOGGER
# =============================================================================

_global_logger: Optional[StructuredLogger] = None


def initialize_global_logger(
    agent_id: str,
    component: str,
    environment: str = "development",
    **kwargs
) -> StructuredLogger:
    """Initialize global logger instance"""
    global _global_logger
    _global_logger = StructuredLogger(
        agent_id=agent_id,
        component=component,
        environment=environment,
        **kwargs
    )
    return _global_logger


def get_logger() -> Optional[StructuredLogger]:
    """Get global logger instance"""
    if _global_logger is None:
        raise RuntimeError("Global logger not initialized. Call initialize_global_logger() first.")
    return _global_logger


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Initialize logger for this agent
    logger = StructuredLogger(
        agent_id="A1-haiku-001",
        component="redis_bus",
        environment="development",
        log_level=LogLevel.DEBUG,
        log_path="/tmp/infrafabric-test.log"
    )

    # Set correlation ID for request
    set_correlation_id("req-user123request456", CorrelationIDType.REQUEST)

    # Log some examples
    logger.info(
        "Agent initialized",
        context={"version": "1.0.0", "workers": 4},
        tags=["startup", "initialization"]
    )

    logger.debug(
        "Starting task processing",
        context={"queue_size": 100},
        if_citation="if://log/task-processing-start"
    )

    logger.info(
        "Task claimed successfully",
        context={"task_id": "task:001", "duration_ms": 2.1, "batch_size": 100},
        if_citation="if://log/redis-task-claim"
    )

    logger.log_performance(
        "Task processing completed",
        duration_ms=125.5,
        memory_mb=250.3,
        context={"tasks_processed": 100}
    )

    logger.warn(
        "Cache hit rate below threshold",
        context={"hit_rate": 0.65, "threshold": 0.80},
        tags=["performance", "cache"]
    )

    try:
        # Simulate error
        raise ValueError("Example error for logging")
    except Exception as e:
        logger.error(
            "Failed to process task",
            context={"task_id": "task:002"},
            exception=e,
            error_code="ERR_TASK_PROCESSING",
            if_citation="if://log/task-processing-error"
        )

    # Force flush before exit
    logger.flush()

    print("\nTest logs written to /tmp/infrafabric-test.log")
