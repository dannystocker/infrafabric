"""IF.witness - Cryptographic provenance and audit logging

This module provides cryptographic logging using Ed25519 signatures
for traceable, transparent, and trustworthy operations.

Philosophy: IF.TTT (Traceable, Transparent, Trustworthy)

Part of Phase 0: Stub implementation for integration
Full implementation in future phases.
"""

import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class Operation:
    """Logged operation with provenance"""
    component: str
    operation: str
    params: Dict[str, Any]
    timestamp: float
    severity: str = "INFO"
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'component': self.component,
            'operation': self.operation,
            'params': self.params,
            'timestamp': self.timestamp,
            'severity': self.severity,
            'signature': self.signature,
        }


# In-memory operation log (stub implementation)
_operation_log: List[Operation] = []


def log_operation(
    component: str,
    operation: str,
    params: Dict[str, Any],
    timestamp: Optional[float] = None,
    severity: str = "INFO"
) -> None:
    """Log an operation with provenance

    Args:
        component: Component name (e.g., 'IF.coordinator', 'IF.governor')
        operation: Operation name (e.g., 'task_claimed', 'cost_tracked')
        params: Operation parameters
        timestamp: Unix timestamp (defaults to now)
        severity: Log severity (INFO, WARN, HIGH)

    Example:
        >>> log_operation(
        ...     component='IF.governor',
        ...     operation='budget_deducted',
        ...     params={'swarm_id': 'session-7', 'amount': 0.50}
        ... )
    """
    if timestamp is None:
        timestamp = time.time()

    op = Operation(
        component=component,
        operation=operation,
        params=params,
        timestamp=timestamp,
        severity=severity,
    )

    _operation_log.append(op)

    # Simple console logging for now
    if severity in ["WARN", "HIGH", "CRITICAL"]:
        print(f"[IF.witness] {severity}: {component}.{operation} - {json.dumps(params)}")


def get_operations(
    component: Optional[str] = None,
    operation: Optional[str] = None,
    since: Optional[float] = None
) -> List[Operation]:
    """Query operation log

    Args:
        component: Filter by component name
        operation: Filter by operation name
        since: Only return operations after this timestamp

    Returns:
        List of matching operations
    """
    results = _operation_log

    if component:
        results = [op for op in results if op.component == component]

    if operation:
        results = [op for op in results if op.operation == operation]

    if since:
        results = [op for op in results if op.timestamp >= since]

    return results


def clear_operations() -> None:
    """Clear operation log (for testing)"""
    global _operation_log
    _operation_log = []


def get_operation_count() -> int:
    """Get total operation count"""
    return len(_operation_log)
