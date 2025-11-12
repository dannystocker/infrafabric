"""SLO Tracking for Swarm Performance (P0.3.4)

This module implements Service Level Objective (SLO) tracking for swarm agents.
SLOs define performance targets (latency, success rate, availability) and the
SLOTracker monitors actual performance against these targets.

Philosophy:
- IF.ground Observable: All performance metrics are tracked and auditable
- IF.TTT Trustworthy: Objective SLO compliance scoring for fair evaluation
- Wu Lun (朋友): Performance tracking enables peer-level accountability

Task: P0.3.4 - SLO tracking
Est: 2h (Sonnet)
Session: 4 (SIP)
Dependencies: P0.3.2 (Resource limits - Session 7)
Unblocks: P0.3.5 (Reputation system)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
import time
import statistics
import json


@dataclass
class ServiceLevelObjective:
    """Service Level Objective definition

    SLOs define performance targets that swarms must meet:
    - p99_latency_ms: 99th percentile latency in milliseconds
    - success_rate: Minimum success rate (0.0-1.0)
    - availability: Minimum uptime (0.0-1.0)

    Attributes:
        p99_latency_ms: Target p99 latency in ms (e.g., 100 for <100ms)
        success_rate: Target success rate 0.0-1.0 (e.g., 0.99 for 99%)
        availability: Target availability 0.0-1.0 (e.g., 0.999 for 99.9%)

    Example:
        >>> slo = ServiceLevelObjective(
        ...     p99_latency_ms=100,
        ...     success_rate=0.99,
        ...     availability=0.999
        ... )
    """
    p99_latency_ms: int
    success_rate: float  # 0.0-1.0
    availability: float  # 0.0-1.0

    def __post_init__(self):
        """Validate SLO values"""
        if self.p99_latency_ms < 0:
            raise ValueError("p99_latency_ms must be non-negative")

        if not 0.0 <= self.success_rate <= 1.0:
            raise ValueError("success_rate must be between 0.0 and 1.0")

        if not 0.0 <= self.availability <= 1.0:
            raise ValueError("availability must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class PerformanceMetric:
    """Single performance measurement

    Attributes:
        timestamp: Unix timestamp of measurement
        latency_ms: Operation latency in milliseconds (None if operation failed early)
        success: Whether operation succeeded
        metadata: Optional additional metadata

    Example:
        >>> metric = PerformanceMetric(
        ...     timestamp=time.time(),
        ...     latency_ms=45.2,
        ...     success=True
        ... )
    """
    timestamp: float
    latency_ms: Optional[float]
    success: bool
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class SLOCompliance:
    """SLO compliance report

    Attributes:
        swarm_id: Swarm identifier
        measured_at: When compliance was measured
        total_operations: Total operations measured
        success_rate: Measured success rate
        success_rate_target: Target success rate
        success_rate_compliant: Whether success rate meets SLO
        p99_latency_ms: Measured p99 latency
        p99_latency_target: Target p99 latency
        p99_latency_compliant: Whether p99 latency meets SLO
        overall_compliant: Whether all SLO targets are met
    """
    swarm_id: str
    measured_at: float
    total_operations: int
    success_rate: float
    success_rate_target: float
    success_rate_compliant: bool
    p99_latency_ms: float
    p99_latency_target: int
    p99_latency_compliant: bool
    overall_compliant: bool

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary"""
        return asdict(self)


class SLOTracker:
    """Track swarm performance against Service Level Objectives

    The SLOTracker collects performance metrics from swarm operations and
    calculates SLO compliance. This enables:
    - Objective performance evaluation
    - SLO violation detection
    - Reputation scoring (used by P0.3.5)
    - Performance dashboards

    Example:
        >>> tracker = SLOTracker()
        >>> tracker.set_slo("session-4-sip", ServiceLevelObjective(
        ...     p99_latency_ms=100,
        ...     success_rate=0.99,
        ...     availability=0.999
        ... ))
        >>> tracker.record_metric("session-4-sip", latency_ms=45, success=True)
        >>> compliance = tracker.calculate_slo_compliance("session-4-sip")
        >>> assert compliance.overall_compliant
    """

    def __init__(self, max_metrics_per_swarm: int = 1000):
        """Initialize SLO tracker

        Args:
            max_metrics_per_swarm: Maximum metrics to keep per swarm (default 1000)
        """
        self.metrics: Dict[str, List[PerformanceMetric]] = {}
        self.slos: Dict[str, ServiceLevelObjective] = {}
        self.max_metrics_per_swarm = max_metrics_per_swarm
        self.violations: List[Dict[str, any]] = []

    def set_slo(self, swarm_id: str, slo: ServiceLevelObjective) -> None:
        """Set SLO for swarm

        Args:
            swarm_id: Swarm identifier
            slo: Service level objective

        Example:
            >>> tracker = SLOTracker()
            >>> tracker.set_slo("session-4", ServiceLevelObjective(
            ...     p99_latency_ms=100,
            ...     success_rate=0.99,
            ...     availability=0.999
            ... ))
        """
        self.slos[swarm_id] = slo

        self._log_operation(
            operation='slo_configured',
            params={
                'swarm_id': swarm_id,
                'p99_latency_ms': slo.p99_latency_ms,
                'success_rate': slo.success_rate,
                'availability': slo.availability
            }
        )

    def record_metric(
        self,
        swarm_id: str,
        latency_ms: Optional[float],
        success: bool,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Record performance metric for swarm

        Args:
            swarm_id: Swarm identifier
            latency_ms: Operation latency in ms (None if failed early)
            success: Whether operation succeeded
            metadata: Optional additional metadata

        Example:
            >>> tracker = SLOTracker()
            >>> tracker.record_metric("session-4", 45.2, True)
            >>> tracker.record_metric("session-4", None, False)  # Failed operation
        """
        if swarm_id not in self.metrics:
            self.metrics[swarm_id] = []

        metric = PerformanceMetric(
            timestamp=time.time(),
            latency_ms=latency_ms,
            success=success,
            metadata=metadata or {}
        )

        self.metrics[swarm_id].append(metric)

        # Keep only recent metrics (sliding window)
        if len(self.metrics[swarm_id]) > self.max_metrics_per_swarm:
            self.metrics[swarm_id] = self.metrics[swarm_id][-self.max_metrics_per_swarm:]

    def calculate_slo_compliance(self, swarm_id: str) -> Optional[SLOCompliance]:
        """Calculate SLO compliance for swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            SLOCompliance report, or None if insufficient data

        Example:
            >>> tracker = SLOTracker()
            >>> tracker.set_slo("session-4", ServiceLevelObjective(100, 0.99, 0.999))
            >>> tracker.record_metric("session-4", 45, True)
            >>> compliance = tracker.calculate_slo_compliance("session-4")
            >>> assert compliance.overall_compliant
        """
        if swarm_id not in self.metrics or swarm_id not in self.slos:
            return None

        metrics = self.metrics[swarm_id]
        if not metrics:
            return None

        slo = self.slos[swarm_id]

        # Calculate success rate
        total = len(metrics)
        successes = sum(1 for m in metrics if m.success)
        success_rate = successes / total

        # Calculate p99 latency
        latencies = [m.latency_ms for m in metrics if m.latency_ms is not None]
        if latencies:
            latencies.sort()
            p99_index = int(len(latencies) * 0.99)
            p99_latency = latencies[min(p99_index, len(latencies) - 1)]
        else:
            p99_latency = 0.0

        # Check compliance
        success_rate_compliant = success_rate >= slo.success_rate
        p99_latency_compliant = p99_latency <= slo.p99_latency_ms

        compliance = SLOCompliance(
            swarm_id=swarm_id,
            measured_at=time.time(),
            total_operations=total,
            success_rate=success_rate,
            success_rate_target=slo.success_rate,
            success_rate_compliant=success_rate_compliant,
            p99_latency_ms=p99_latency,
            p99_latency_target=slo.p99_latency_ms,
            p99_latency_compliant=p99_latency_compliant,
            overall_compliant=success_rate_compliant and p99_latency_compliant
        )

        # Log violations
        if not compliance.overall_compliant:
            self._log_violation(compliance)

        return compliance

    def get_metrics(
        self,
        swarm_id: str,
        limit: Optional[int] = None
    ) -> List[PerformanceMetric]:
        """Get performance metrics for swarm

        Args:
            swarm_id: Swarm identifier
            limit: Optional limit on number of metrics

        Returns:
            List of performance metrics (most recent first)
        """
        if swarm_id not in self.metrics:
            return []

        metrics = list(reversed(self.metrics[swarm_id]))
        if limit:
            return metrics[:limit]
        return metrics

    def get_all_compliance(self) -> Dict[str, SLOCompliance]:
        """Get SLO compliance for all swarms

        Returns:
            Dictionary mapping swarm_id to compliance report
        """
        compliance = {}
        for swarm_id in self.slos.keys():
            comp = self.calculate_slo_compliance(swarm_id)
            if comp:
                compliance[swarm_id] = comp
        return compliance

    def get_violations(self, swarm_id: Optional[str] = None) -> List[Dict[str, any]]:
        """Get SLO violations

        Args:
            swarm_id: Optional filter by swarm ID

        Returns:
            List of violations
        """
        if swarm_id:
            return [v for v in self.violations if v['swarm_id'] == swarm_id]
        return self.violations

    def get_stats(self, swarm_id: str) -> Dict[str, any]:
        """Get statistics for swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            Dictionary with various statistics
        """
        if swarm_id not in self.metrics:
            return {}

        metrics = self.metrics[swarm_id]
        if not metrics:
            return {}

        latencies = [m.latency_ms for m in metrics if m.latency_ms is not None]
        successes = sum(1 for m in metrics if m.success)

        stats = {
            "total_operations": len(metrics),
            "success_count": successes,
            "failure_count": len(metrics) - successes,
            "success_rate": successes / len(metrics),
        }

        if latencies:
            stats.update({
                "latency_min": min(latencies),
                "latency_max": max(latencies),
                "latency_mean": statistics.mean(latencies),
                "latency_median": statistics.median(latencies),
                "latency_p99": sorted(latencies)[int(len(latencies) * 0.99)],
            })

        return stats

    def _log_violation(self, compliance: SLOCompliance) -> None:
        """Log SLO violation

        Args:
            compliance: Compliance report showing violation
        """
        violation = {
            "swarm_id": compliance.swarm_id,
            "timestamp": compliance.measured_at,
            "success_rate_compliant": compliance.success_rate_compliant,
            "p99_latency_compliant": compliance.p99_latency_compliant,
            "success_rate": compliance.success_rate,
            "success_rate_target": compliance.success_rate_target,
            "p99_latency_ms": compliance.p99_latency_ms,
            "p99_latency_target": compliance.p99_latency_target,
        }

        self.violations.append(violation)

        self._log_operation(
            operation='slo_violation',
            params=violation,
            severity='WARNING'
        )

    def _log_operation(
        self,
        operation: str,
        params: Dict[str, any],
        severity: str = 'INFO'
    ) -> None:
        """Log operation to IF.witness

        Args:
            operation: Operation name
            params: Operation parameters
            severity: Log severity
        """
        try:
            from infrafabric.witness import log_operation
            log_operation(
                component='IF.chassis.slo',
                operation=operation,
                params=params,
                severity=severity
            )
        except ImportError:
            # IF.witness not available - log to stderr
            import sys
            print(
                f"[IF.chassis.slo] {severity}: {operation} - {json.dumps(params)}",
                file=sys.stderr
            )


__all__ = [
    "ServiceLevelObjective",
    "PerformanceMetric",
    "SLOCompliance",
    "SLOTracker",
]
