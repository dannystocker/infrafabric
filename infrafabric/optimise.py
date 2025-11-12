"""IF.optimise - Cost tracking and optimization

This module provides cost tracking, budget management, and optimization
metrics for InfraFabric operations.

Philosophy: IF.TTT - Transparent cost tracking

Part of Phase 0: Stub implementation for integration
Full implementation in future phases.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class CostRecord:
    """Cost tracking record"""
    provider: str
    operation: str
    cost: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'provider': self.provider,
            'operation': self.operation,
            'cost': self.cost,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
        }


# In-memory cost tracking (stub implementation)
_cost_records: List[CostRecord] = []


def track_operation_cost(
    provider: str,
    operation: str,
    cost: float,
    timestamp: Optional[float] = None,
    **metadata
) -> None:
    """Track cost for an operation

    Args:
        provider: Provider/swarm identifier
        operation: Operation name
        cost: Cost in USD
        timestamp: Unix timestamp (defaults to now)
        **metadata: Additional metadata

    Example:
        >>> track_operation_cost(
        ...     provider='session-7-ifbus',
        ...     operation='budget_tracking',
        ...     cost=0.025
        ... )
    """
    if timestamp is None:
        timestamp = time.time()

    record = CostRecord(
        provider=provider,
        operation=operation,
        cost=cost,
        timestamp=timestamp,
        metadata=metadata,
    )

    _cost_records.append(record)


def get_total_cost(
    provider: Optional[str] = None,
    since: Optional[float] = None
) -> float:
    """Get total cost

    Args:
        provider: Filter by provider
        since: Only count costs after this timestamp

    Returns:
        Total cost in USD
    """
    records = _cost_records

    if provider:
        records = [r for r in records if r.provider == provider]

    if since:
        records = [r for r in records if r.timestamp >= since]

    return sum(r.cost for r in records)


def get_cost_report(
    provider: Optional[str] = None,
    since: Optional[float] = None
) -> Dict[str, Any]:
    """Get cost report

    Args:
        provider: Filter by provider
        since: Only include costs after this timestamp

    Returns:
        Cost report dictionary
    """
    records = _cost_records

    if provider:
        records = [r for r in records if r.provider == provider]

    if since:
        records = [r for r in records if r.timestamp >= since]

    total_cost = sum(r.cost for r in records)
    operation_counts = {}
    operation_costs = {}

    for record in records:
        operation_counts[record.operation] = operation_counts.get(record.operation, 0) + 1
        operation_costs[record.operation] = operation_costs.get(record.operation, 0.0) + record.cost

    return {
        'total_cost': total_cost,
        'total_operations': len(records),
        'operation_counts': operation_counts,
        'operation_costs': operation_costs,
        'providers': list(set(r.provider for r in records)),
    }


def clear_cost_records() -> None:
    """Clear cost records (for testing)"""
    global _cost_records
    _cost_records = []


def get_cost_records(
    provider: Optional[str] = None,
    operation: Optional[str] = None,
    since: Optional[float] = None
) -> List[CostRecord]:
    """Query cost records

    Args:
        provider: Filter by provider
        operation: Filter by operation
        since: Only return records after this timestamp

    Returns:
        List of matching cost records
    """
    records = _cost_records

    if provider:
        records = [r for r in records if r.provider == provider]

    if operation:
        records = [r for r in records if r.operation == operation]

    if since:
        records = [r for r in records if r.timestamp >= since]

    return records
