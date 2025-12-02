#!/usr/bin/env python3
"""
Recovery Orchestrator for InfraFabric Infrastructure

Monitors health check status and triggers automated recovery actions based on
failure type. Integrates with:
- A34: Health check system
- A28: ChromaDB snapshot rollback
- A32: Prometheus alerting
- A30: Metrics exporter

Citation: if://agent/A35_recovery_orchestrator
Author: Agent A35
Date: 2025-11-30
"""

import os
import sys
import time
import json
import uuid
import logging
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Constants and Enums
# ============================================================================

class RecoveryPriority(str, Enum):
    """Recovery action priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecoveryStrategy(str, Enum):
    """Available recovery strategies for each component."""
    # Redis strategies
    RECONNECT = "reconnect"
    FLUSH_CORRUPTED = "flush_corrupted"
    RESTART_CONTAINER = "restart_container"

    # ChromaDB strategies
    QUERY_RETRY = "query_retry"
    SNAPSHOT_ROLLBACK = "snapshot_rollback"
    COLLECTION_RELOAD = "collection_reload"
    INDEX_REBUILD = "index_rebuild"

    # OpenWebUI strategies
    TOKEN_REFRESH = "token_refresh"
    MODEL_FAILOVER = "model_failover"
    GRACEFUL_DEGRADATION = "graceful_degradation"

    # System strategies
    DISK_CLEANUP = "disk_cleanup"
    MEMORY_GC = "memory_gc"
    PROCESS_RESTART = "process_restart"
    FILE_HANDLE_CLEANUP = "file_handle_cleanup"


class RecoveryStatus(str, Enum):
    """Recovery action status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    REQUIRES_APPROVAL = "requires_approval"


class ComponentFailureType(str, Enum):
    """Types of component failures."""
    CONNECTION_TIMEOUT = "connection_timeout"
    CONNECTION_ERROR = "connection_error"
    HIGH_LATENCY = "high_latency"
    MEMORY_PRESSURE = "memory_pressure"
    CORRUPTION = "corruption"
    INDEX_ERROR = "index_error"
    AUTH_FAILURE = "auth_failure"
    MODEL_UNAVAILABLE = "model_unavailable"
    RATE_LIMITING = "rate_limiting"
    DISK_FULL = "disk_full"
    MEMORY_LEAK = "memory_leak"
    FILE_HANDLE_EXHAUSTION = "file_handle_exhaustion"
    PERMISSION_ERROR = "permission_error"


# ============================================================================
# Recovery Audit Trail
# ============================================================================

class RecoveryAuditEntry:
    """Audit trail entry for a recovery action."""

    def __init__(self, component: str, failure_type: str, strategy: str):
        self.recovery_id = str(uuid.uuid4())
        self.timestamp = datetime.now()
        self.component = component
        self.failure_type = failure_type
        self.strategy = strategy
        self.attempts = 0
        self.success = False
        self.duration_seconds = 0.0
        self.actions_taken: List[str] = []
        self.metrics_before: Dict[str, Any] = {}
        self.metrics_after: Dict[str, Any] = {}
        self.error_message: Optional[str] = None
        self.correlation_id = str(uuid.uuid4())
        self.start_time = time.time()

    def finish(self, success: bool, error: Optional[str] = None):
        """Mark recovery as finished."""
        self.success = success
        self.duration_seconds = time.time() - self.start_time
        self.error_message = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "recovery_id": self.recovery_id,
            "timestamp": self.timestamp.isoformat() + "Z",
            "component": self.component,
            "failure_type": self.failure_type,
            "strategy": self.strategy,
            "attempts": self.attempts,
            "success": self.success,
            "duration_seconds": round(self.duration_seconds, 3),
            "actions_taken": self.actions_taken,
            "metrics_before": self.metrics_before,
            "metrics_after": self.metrics_after,
            "error_message": self.error_message,
            "correlation_id": self.correlation_id
        }


# ============================================================================
# Recovery State Tracking
# ============================================================================

class RecoveryCooldown:
    """Tracks cooldown state for recovery prevention loops."""

    def __init__(self, max_attempts_per_hour: int = 3,
                 cooldown_seconds: int = 300):
        self.max_attempts = max_attempts_per_hour
        self.cooldown_seconds = cooldown_seconds
        self.attempt_log: Dict[str, List[float]] = defaultdict(list)
        self.cooldown_ends: Dict[str, float] = {}

    def can_attempt(self, component: str) -> bool:
        """Check if recovery can be attempted for component."""
        # Check if in cooldown
        if component in self.cooldown_ends:
            if time.time() < self.cooldown_ends[component]:
                return False
            else:
                del self.cooldown_ends[component]

        # Check attempt count in last hour
        now = time.time()
        cutoff = now - 3600

        # Clean old attempts
        self.attempt_log[component] = [
            t for t in self.attempt_log[component] if t > cutoff
        ]

        # Check if under limit
        return len(self.attempt_log[component]) < self.max_attempts

    def record_attempt(self, component: str):
        """Record a recovery attempt."""
        self.attempt_log[component].append(time.time())

    def set_cooldown(self, component: str):
        """Set cooldown for component."""
        self.cooldown_ends[component] = time.time() + self.cooldown_seconds


# ============================================================================
# Recovery Orchestrator
# ============================================================================

class RecoveryOrchestrator:
    """Main recovery orchestrator."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize recovery orchestrator.

        Args:
            config: Recovery configuration dict
        """
        self.config = config or self._load_default_config()
        self.cooldown = RecoveryCooldown(
            max_attempts_per_hour=self.config.get('max_attempts_per_hour', 3),
            cooldown_seconds=self.config.get('cooldown_seconds', 300)
        )
        self.audit_trail: List[RecoveryAuditEntry] = []
        self.degraded_modes: Dict[str, bool] = {}
        self.redis_conn: Optional[Any] = None
        self.lock = threading.RLock()

        # Recovery handlers
        self.handlers: Dict[str, Callable] = {}
        self._register_handlers()

        logger.info("Recovery orchestrator initialized")

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default recovery configuration."""
        config_path = os.path.join(
            os.path.dirname(__file__),
            'recovery_config.yml'
        )

        if os.path.exists(config_path):
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}

        # Return minimal default config
        return {
            'max_attempts_per_hour': 3,
            'cooldown_seconds': 300,
            'redis': {'priority': 'critical'},
            'chromadb': {'priority': 'critical'},
            'openwebui': {'priority': 'medium'},
            'system': {'priority': 'high'}
        }

    def _register_handlers(self):
        """Register recovery handlers."""
        # Import handlers (will be in separate files)
        try:
            from monitoring.recovery.handlers import redis_recovery
            self.handlers['redis'] = redis_recovery.handle_redis_recovery
        except ImportError:
            logger.warning("Redis recovery handler not available")

        try:
            from monitoring.recovery.handlers import chromadb_recovery
            self.handlers['chromadb'] = chromadb_recovery.handle_chromadb_recovery
        except ImportError:
            logger.warning("ChromaDB recovery handler not available")

        try:
            from monitoring.recovery.handlers import openwebui_recovery
            self.handlers['openwebui'] = openwebui_recovery.handle_openwebui_recovery
        except ImportError:
            logger.warning("OpenWebUI recovery handler not available")

        try:
            from monitoring.recovery.handlers import system_recovery
            self.handlers['system'] = system_recovery.handle_system_recovery
        except ImportError:
            logger.warning("System recovery handler not available")

    def trigger_recovery(self, component: str, failure_type: str,
                        strategy: Optional[str] = None,
                        require_approval: bool = False,
                        context: Optional[Dict[str, Any]] = None) -> str:
        """
        Trigger recovery for a component.

        Args:
            component: Component name (redis, chromadb, etc.)
            failure_type: Type of failure
            strategy: Recovery strategy to use (auto-select if None)
            require_approval: Whether to require manual approval
            context: Additional context for recovery

        Returns:
            Recovery ID
        """
        with self.lock:
            # Check cooldown
            if not self.cooldown.can_attempt(component):
                logger.warning(
                    f"Recovery for {component} in cooldown or at attempt limit"
                )
                return ""

            # Auto-select strategy if not provided
            if strategy is None:
                strategy = self._select_strategy(component, failure_type)

            # Create audit entry
            entry = RecoveryAuditEntry(component, failure_type, strategy)
            self.audit_trail.append(entry)

            # Check if approval required
            if require_approval:
                entry_dict = entry.to_dict()
                entry_dict['status'] = RecoveryStatus.REQUIRES_APPROVAL.value
                logger.warning(
                    f"Recovery requires approval: {json.dumps(entry_dict)}"
                )
                return entry.recovery_id

            # Execute recovery
            self.cooldown.record_attempt(component)
            self._execute_recovery(entry, strategy, context or {})

            return entry.recovery_id

    def _select_strategy(self, component: str, failure_type: str) -> str:
        """Auto-select recovery strategy based on failure type."""
        mapping = {
            'redis': {
                ComponentFailureType.CONNECTION_TIMEOUT.value: RecoveryStrategy.RECONNECT.value,
                ComponentFailureType.CONNECTION_ERROR.value: RecoveryStrategy.RECONNECT.value,
                ComponentFailureType.HIGH_LATENCY.value: RecoveryStrategy.RECONNECT.value,
                ComponentFailureType.MEMORY_PRESSURE.value: RecoveryStrategy.FLUSH_CORRUPTED.value,
                ComponentFailureType.CORRUPTION.value: RecoveryStrategy.FLUSH_CORRUPTED.value,
            },
            'chromadb': {
                ComponentFailureType.CORRUPTION.value: RecoveryStrategy.SNAPSHOT_ROLLBACK.value,
                ComponentFailureType.INDEX_ERROR.value: RecoveryStrategy.INDEX_REBUILD.value,
                ComponentFailureType.CONNECTION_TIMEOUT.value: RecoveryStrategy.QUERY_RETRY.value,
            },
            'openwebui': {
                ComponentFailureType.AUTH_FAILURE.value: RecoveryStrategy.TOKEN_REFRESH.value,
                ComponentFailureType.MODEL_UNAVAILABLE.value: RecoveryStrategy.MODEL_FAILOVER.value,
                ComponentFailureType.RATE_LIMITING.value: RecoveryStrategy.GRACEFUL_DEGRADATION.value,
            },
            'system': {
                ComponentFailureType.DISK_FULL.value: RecoveryStrategy.DISK_CLEANUP.value,
                ComponentFailureType.MEMORY_LEAK.value: RecoveryStrategy.MEMORY_GC.value,
                ComponentFailureType.FILE_HANDLE_EXHAUSTION.value: RecoveryStrategy.FILE_HANDLE_CLEANUP.value,
            }
        }

        default_strategies = {
            'redis': RecoveryStrategy.RECONNECT.value,
            'chromadb': RecoveryStrategy.QUERY_RETRY.value,
            'openwebui': RecoveryStrategy.TOKEN_REFRESH.value,
            'system': RecoveryStrategy.MEMORY_GC.value,
        }

        return mapping.get(component, {}).get(
            failure_type,
            default_strategies.get(component, RecoveryStrategy.RECONNECT.value)
        )

    def _execute_recovery(self, entry: RecoveryAuditEntry,
                         strategy: str, context: Dict[str, Any]):
        """Execute recovery action."""
        logger.info(
            f"Executing {entry.strategy} recovery for {entry.component}",
            extra={'correlation_id': entry.correlation_id}
        )

        try:
            # Call component-specific handler
            if entry.component in self.handlers:
                handler = self.handlers[entry.component]
                success = handler(
                    strategy=strategy,
                    context=context,
                    orchestrator=self
                )
                entry.finish(success)
            else:
                entry.finish(False, f"No handler for {entry.component}")

            # Record cooldown if failed
            if not entry.success:
                self.cooldown.set_cooldown(entry.component)

        except Exception as e:
            logger.error(
                f"Recovery execution failed: {e}",
                extra={'correlation_id': entry.correlation_id},
                exc_info=True
            )
            entry.finish(False, str(e))
            self.cooldown.set_cooldown(entry.component)

    def get_recovery_history(self, component: Optional[str] = None,
                            hours: int = 24) -> List[Dict[str, Any]]:
        """Get recovery history."""
        cutoff = datetime.now() - timedelta(hours=hours)

        results = []
        for entry in self.audit_trail:
            if entry.timestamp < cutoff:
                continue
            if component and entry.component != component:
                continue
            results.append(entry.to_dict())

        return results

    def get_cooldown_status(self) -> Dict[str, Any]:
        """Get current cooldown status for all components."""
        now = time.time()
        status = {}

        for component, end_time in self.cooldown.cooldown_ends.items():
            status[component] = {
                'in_cooldown': now < end_time,
                'cooldown_until': datetime.fromtimestamp(end_time).isoformat() + "Z",
                'seconds_remaining': max(0, end_time - now)
            }

        return status

    def activate_degraded_mode(self, mode: str, reason: str):
        """Activate degraded mode for a component."""
        with self.lock:
            self.degraded_modes[mode] = True
            logger.warning(f"Activated degraded mode: {mode} (reason: {reason})")

            # Emit metric
            self._emit_degraded_mode_metric(mode, 1)

    def deactivate_degraded_mode(self, mode: str):
        """Deactivate degraded mode for a component."""
        with self.lock:
            if mode in self.degraded_modes:
                del self.degraded_modes[mode]
                logger.info(f"Deactivated degraded mode: {mode}")

                # Emit metric
                self._emit_degraded_mode_metric(mode, 0)

    def is_degraded_mode_active(self, mode: str) -> bool:
        """Check if degraded mode is active."""
        return self.degraded_modes.get(mode, False)

    def _emit_degraded_mode_metric(self, mode: str, value: int):
        """Emit Prometheus metric for degraded mode."""
        try:
            from monitoring.prometheus.metrics_exporter import get_metrics_registry
            registry = get_metrics_registry()
            if hasattr(registry, 'degraded_mode_active'):
                registry.degraded_mode_active.labels(mode=mode).set(value)
        except Exception as e:
            logger.debug(f"Could not emit degraded mode metric: {e}")

    def save_audit_trail(self, filepath: str):
        """Save audit trail to JSON file."""
        data = {
            'recovered_at': datetime.now().isoformat() + "Z",
            'total_recoveries': len(self.audit_trail),
            'successful_recoveries': sum(
                1 for e in self.audit_trail if e.success
            ),
            'recoveries': [e.to_dict() for e in self.audit_trail]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Audit trail saved to {filepath}")


# ============================================================================
# Degraded Mode Manager
# ============================================================================

class DegradedModeManager:
    """Manages degraded operation modes."""

    # Define degraded mode capabilities
    CAPABILITIES = {
        'chromadb_unavailable': {
            'available': [
                'basic_conversation',
                'redis_memory',
                'simple_qa',
                'direct_api_calls'
            ],
            'unavailable': [
                'semantic_search',
                'personality_injection',
                'long_term_memory',
                'chromadb_query'
            ]
        },
        'openwebui_unavailable': {
            'available': [
                'direct_api_calls',
                'single_model_inference',
                'basic_conversation'
            ],
            'unavailable': [
                'multi_model_consensus',
                'openwebui_ui',
                'model_switching'
            ]
        },
        'redis_unavailable': {
            'available': [
                'basic_conversation',
                'in_memory_cache',
                'single_session'
            ],
            'unavailable': [
                'semantic_search',
                'long_term_memory',
                'multi_session_state',
                'persistent_storage'
            ]
        }
    }

    @classmethod
    def get_capabilities(cls, mode: str) -> Dict[str, List[str]]:
        """Get capabilities for a degraded mode."""
        return cls.CAPABILITIES.get(mode, {
            'available': [],
            'unavailable': []
        })


# ============================================================================
# Module initialization
# ============================================================================

_default_orchestrator: Optional[RecoveryOrchestrator] = None


def get_recovery_orchestrator() -> RecoveryOrchestrator:
    """Get or create default recovery orchestrator."""
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = RecoveryOrchestrator()
    return _default_orchestrator


def initialize_recovery(config: Optional[Dict[str, Any]] = None) -> RecoveryOrchestrator:
    """Initialize recovery orchestrator with config."""
    global _default_orchestrator
    _default_orchestrator = RecoveryOrchestrator(config=config)
    return _default_orchestrator


if __name__ == '__main__':
    # Test
    logging.basicConfig(level=logging.INFO)

    orchestrator = RecoveryOrchestrator()
    print("Recovery orchestrator initialized successfully")
