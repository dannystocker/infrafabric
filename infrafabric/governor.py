"""IF.governor - Capability-aware resource and budget management

This module implements intelligent task assignment based on:
- Capability matching (70%+ threshold)
- Cost optimization (prevent 57% waste)
- Budget enforcement (hard limits)
- Circuit breakers (prevent spirals)

Philosophy: IF.ground (Wu Lun - 五倫)
- 夫婦 (Complementarity): Match task needs to swarm capabilities
- 君臣 (Authority): Enforce budget and policy constraints
- 朋友 (Trust): Build reputation through performance

Part of Phase 0: Bug #2 (Cost Waste) fix
Target: Reduce 57% cost waste → <10%
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    calculate_capability_overlap,
)
from infrafabric.witness import log_operation
from infrafabric.optimise import track_operation_cost


class IFGovernor:
    """Capability-aware resource and budget management

    This class implements the IF.governor component for Phase 0.
    It provides:
    - Swarm registration and capability management
    - Intelligent task assignment (70%+ capability match)
    - Budget tracking and enforcement
    - Circuit breaker for cost/failure protection
    - Policy enforcement

    Example:
        >>> from infrafabric.schemas.capability import ResourcePolicy, SwarmProfile, Capability
        >>> policy = ResourcePolicy(max_cost_per_task=10.0)
        >>> governor = IFGovernor(coordinator=None, policy=policy)
        >>> profile = SwarmProfile(
        ...     swarm_id='session-7',
        ...     capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        ...     cost_per_hour=15.0,
        ...     current_budget_remaining=100.0
        ... )
        >>> governor.register_swarm(profile)
        >>> governor.track_cost('session-7', 'code-review', 0.50)
    """

    def __init__(
        self,
        coordinator: Optional[Any] = None,
        policy: Optional[ResourcePolicy] = None
    ):
        """Initialize IF.governor

        Args:
            coordinator: IF.coordinator instance (for notifications)
            policy: Resource policy (defaults to standard policy)
        """
        self.coordinator = coordinator
        self.policy = policy or ResourcePolicy()
        self.swarm_registry: Dict[str, SwarmProfile] = {}
        self._circuit_breakers: Dict[str, bool] = {}  # swarm_id -> is_tripped
        self._failure_counts: Dict[str, int] = {}  # swarm_id -> failure_count

        if self.policy.enable_witness_logging:
            log_operation(
                component='IF.governor',
                operation='initialized',
                params={
                    'policy': self.policy.to_dict(),
                }
            )

    def register_swarm(self, profile: SwarmProfile) -> None:
        """Register swarm with capabilities

        Args:
            profile: Swarm profile containing capabilities and cost info

        Example:
            >>> profile = SwarmProfile(
            ...     swarm_id='session-7-ifbus',
            ...     capabilities=[Capability.INFRA_DISTRIBUTED_SYSTEMS],
            ...     cost_per_hour=15.0,
            ...     current_budget_remaining=100.0
            ... )
            >>> governor.register_swarm(profile)
        """
        self.swarm_registry[profile.swarm_id] = profile
        self._circuit_breakers[profile.swarm_id] = False
        self._failure_counts[profile.swarm_id] = 0

        if self.policy.enable_witness_logging:
            log_operation(
                component='IF.governor',
                operation='swarm_registered',
                params={
                    'swarm_id': profile.swarm_id,
                    'capabilities': [c.value for c in profile.capabilities],
                    'cost_per_hour': profile.cost_per_hour,
                    'budget': profile.current_budget_remaining,
                }
            )

    def track_cost(
        self,
        swarm_id: str,
        operation: str,
        cost: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track costs and enforce budget limits

        This is the core method for P0.2.3 (Budget Tracking and Enforcement).

        Features:
        - Deducts cost from swarm budget
        - Integrates with IF.optimise for cost tracking
        - Logs to IF.witness for audit trail
        - Trips circuit breaker if budget exhausted
        - Prevents new task assignment when budget = 0

        Args:
            swarm_id: Swarm identifier
            operation: Operation name (e.g., 'code-review', 'task-execution')
            cost: Cost in USD
            metadata: Optional metadata about the operation

        Raises:
            ValueError: If swarm_id is unknown

        Example:
            >>> governor.track_cost('session-7', 'code-review', 0.50)
            >>> governor.track_cost('session-7', 'task-execution', 1.25, {
            ...     'task_id': 'P0.2.3',
            ...     'duration_seconds': 120
            ... })
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        profile = self.swarm_registry[swarm_id]

        # Deduct from budget
        profile.current_budget_remaining -= cost

        # Log cost to IF.optimise
        if self.policy.enable_cost_tracking:
            track_operation_cost(
                provider=swarm_id,
                operation=operation,
                cost=cost,
                **(metadata or {})
            )

        # Log to IF.witness
        if self.policy.enable_witness_logging:
            log_operation(
                component='IF.governor',
                operation='cost_tracked',
                params={
                    'swarm_id': swarm_id,
                    'operation': operation,
                    'cost': cost,
                    'remaining_budget': profile.current_budget_remaining,
                    'metadata': metadata or {},
                }
            )

        # Check if budget exhausted
        if profile.current_budget_remaining <= 0:
            self._trip_circuit_breaker(
                swarm_id,
                reason='budget_exhausted',
                details={
                    'final_operation': operation,
                    'final_cost': cost,
                    'total_spent': -profile.current_budget_remaining,
                }
            )

    def get_budget_report(
        self,
        swarm_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get budget status for swarms

        Args:
            swarm_id: Optional swarm ID to filter (returns all if None)

        Returns:
            Dictionary mapping swarm_id to budget info

        Example:
            >>> report = governor.get_budget_report()
            >>> print(report)
            {
                'session-7': {
                    'remaining': 95.50,
                    'spent': 4.50,
                    'cost_per_hour': 15.0,
                    'circuit_breaker': False
                }
            }
        """
        if swarm_id:
            if swarm_id not in self.swarm_registry:
                raise ValueError(f"Unknown swarm: {swarm_id}")
            swarms = {swarm_id: self.swarm_registry[swarm_id]}
        else:
            swarms = self.swarm_registry

        report = {}
        for sid, profile in swarms.items():
            # Calculate spent from IF.optimise
            from infrafabric.optimise import get_total_cost
            spent = get_total_cost(provider=sid)

            report[sid] = {
                'remaining': profile.current_budget_remaining,
                'spent': spent,
                'cost_per_hour': profile.cost_per_hour,
                'circuit_breaker': self._circuit_breakers.get(sid, False),
                'reputation': profile.reputation_score,
                'model': profile.model,
            }

        return report

    def is_swarm_available(self, swarm_id: str) -> bool:
        """Check if swarm is available for task assignment

        A swarm is unavailable if:
        - Circuit breaker is tripped
        - Budget is exhausted (≤ 0)
        - Swarm is not registered

        Args:
            swarm_id: Swarm identifier

        Returns:
            True if swarm can accept tasks, False otherwise
        """
        if swarm_id not in self.swarm_registry:
            return False

        if self._circuit_breakers.get(swarm_id, False):
            return False

        profile = self.swarm_registry[swarm_id]
        if profile.current_budget_remaining <= 0:
            return False

        return True

    def find_qualified_swarm(
        self,
        required_capabilities: List[Capability],
        max_cost: float
    ) -> Optional[str]:
        """Find best swarm based on capability match and cost

        This implements the 70%+ capability matching algorithm for P0.2.2.
        Note: This method is a placeholder for P0.2.2 implementation.

        Algorithm:
        1. Calculate capability overlap (Jaccard similarity)
        2. Filter by policy.min_capability_match (default 70%)
        3. Filter by max_cost
        4. Filter by budget availability
        5. Score: (capability_match × reputation) / cost
        6. Return highest-scoring swarm

        Args:
            required_capabilities: List of required capabilities
            max_cost: Maximum cost per hour

        Returns:
            Swarm ID of best match, or None if no qualified swarm

        Example:
            >>> swarm = governor.find_qualified_swarm(
            ...     required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            ...     max_cost=20.0
            ... )
        """
        candidates = []

        for swarm_id, profile in self.swarm_registry.items():
            # Skip unavailable swarms
            if not self.is_swarm_available(swarm_id):
                continue

            # Calculate capability overlap
            capability_overlap = calculate_capability_overlap(
                required=required_capabilities,
                available=profile.capabilities
            )

            # Filter by policy
            if capability_overlap < self.policy.min_capability_match:
                continue  # Not qualified (below 70%)

            if profile.cost_per_hour > max_cost:
                continue  # Too expensive

            # Combined score: (capability × reputation) / cost
            # Higher is better
            score = (capability_overlap * profile.reputation_score) / profile.cost_per_hour

            candidates.append((swarm_id, score, capability_overlap))

        if not candidates:
            return None

        # Return highest-scoring swarm
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_swarm_id = candidates[0][0]

        if self.policy.enable_witness_logging:
            log_operation(
                component='IF.governor',
                operation='swarm_matched',
                params={
                    'required_capabilities': [c.value for c in required_capabilities],
                    'matched_swarm': best_swarm_id,
                    'score': candidates[0][1],
                    'capability_overlap': candidates[0][2],
                }
            )

        return best_swarm_id

    def _trip_circuit_breaker(
        self,
        swarm_id: str,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Halt swarm to prevent cost spirals or repeated failures

        This implements circuit breaker logic for P0.2.4.

        Actions:
        - Mark swarm as unavailable
        - Notify coordinator to stop sending tasks
        - Log incident with HIGH severity
        - Escalate to human for intervention

        Args:
            swarm_id: Swarm to halt
            reason: Reason for circuit breaker trip
            details: Additional details
        """
        # Mark swarm as unavailable
        self._circuit_breakers[swarm_id] = True

        # Notify coordinator (if available)
        if self.coordinator:
            asyncio.create_task(
                self.coordinator.event_bus.put(
                    f'/swarms/{swarm_id}/status',
                    'circuit_breaker_tripped'
                )
            )

        # Log incident with HIGH severity
        log_operation(
            component='IF.governor',
            operation='circuit_breaker_tripped',
            params={
                'swarm_id': swarm_id,
                'reason': reason,
                'details': details or {},
            },
            severity='HIGH'
        )

        # Escalate to human
        self._escalate_to_human(swarm_id, {
            'type': 'circuit_breaker',
            'reason': reason,
            'details': details or {},
        })

    def _escalate_to_human(
        self,
        swarm_id: str,
        issue: Dict[str, Any]
    ) -> None:
        """ESCALATE pattern: Notify human for intervention

        This prints a notification for human review.
        In production, this would send notifications via multiple channels.

        Args:
            swarm_id: Swarm requiring intervention
            issue: Issue details
        """
        notification = f"""
╔════════════════════════════════════════════════════════════════╗
║  🚨 S² System Escalation Required                              ║
╠════════════════════════════════════════════════════════════════╣
║  Swarm: {swarm_id:<54} ║
║  Issue Type: {issue.get('type', 'unknown'):<48} ║
║  Reason: {issue.get('reason', 'unknown'):<51} ║
╠════════════════════════════════════════════════════════════════╣
║  Action Required: Manual review and intervention               ║
║                                                                  ║
║  To reset circuit breaker:                                     ║
║    if governor reset-circuit-breaker {swarm_id:<30} ║
║                                                                  ║
║  To check budget:                                              ║
║    if governor budget-report {swarm_id:<35} ║
╚════════════════════════════════════════════════════════════════╝
        """

        print(notification)

        # Log escalation
        log_operation(
            component='IF.governor',
            operation='escalated_to_human',
            params={
                'swarm_id': swarm_id,
                'issue': issue,
            },
            severity='HIGH'
        )

    def reset_circuit_breaker(
        self,
        swarm_id: str,
        new_budget: Optional[float] = None
    ) -> None:
        """Manually reset circuit breaker (requires human approval)

        Args:
            swarm_id: Swarm to reset
            new_budget: Optional new budget to allocate

        Raises:
            ValueError: If swarm_id is unknown

        Example:
            >>> governor.reset_circuit_breaker('session-7', new_budget=50.0)
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        # Reset circuit breaker
        self._circuit_breakers[swarm_id] = False
        self._failure_counts[swarm_id] = 0

        # Update budget if provided
        if new_budget is not None:
            profile = self.swarm_registry[swarm_id]
            profile.current_budget_remaining = new_budget

        # Update status in coordinator
        if self.coordinator:
            asyncio.create_task(
                self.coordinator.event_bus.put(
                    f'/swarms/{swarm_id}/status',
                    'active'
                )
            )

        # Log reset
        log_operation(
            component='IF.governor',
            operation='circuit_breaker_reset',
            params={
                'swarm_id': swarm_id,
                'new_budget': new_budget,
            },
            severity='INFO'
        )

        print(f"✅ Circuit breaker reset for {swarm_id}")
        if new_budget:
            print(f"   New budget: ${new_budget:.2f}")

    def record_task_failure(
        self,
        swarm_id: str,
        task_id: str,
        reason: str
    ) -> None:
        """Record task failure and check circuit breaker threshold

        Args:
            swarm_id: Swarm that failed
            task_id: Task identifier
            reason: Failure reason
        """
        if swarm_id not in self.swarm_registry:
            return

        # Increment failure count
        self._failure_counts[swarm_id] = self._failure_counts.get(swarm_id, 0) + 1

        # Log failure
        log_operation(
            component='IF.governor',
            operation='task_failed',
            params={
                'swarm_id': swarm_id,
                'task_id': task_id,
                'reason': reason,
                'failure_count': self._failure_counts[swarm_id],
            },
            severity='WARN'
        )

        # Check threshold
        if self._failure_counts[swarm_id] >= self.policy.circuit_breaker_failure_threshold:
            self._trip_circuit_breaker(
                swarm_id,
                reason='repeated_failures',
                details={
                    'failure_count': self._failure_counts[swarm_id],
                    'last_task': task_id,
                    'last_reason': reason,
                }
            )

    def record_task_success(
        self,
        swarm_id: str,
        task_id: str,
        duration_seconds: float
    ) -> None:
        """Record successful task completion

        Args:
            swarm_id: Swarm that succeeded
            task_id: Task identifier
            duration_seconds: Task duration
        """
        if swarm_id not in self.swarm_registry:
            return

        # Reset failure count on success
        self._failure_counts[swarm_id] = 0

        # Log success
        if self.policy.enable_witness_logging:
            log_operation(
                component='IF.governor',
                operation='task_succeeded',
                params={
                    'swarm_id': swarm_id,
                    'task_id': task_id,
                    'duration_seconds': duration_seconds,
                }
            )

    def get_swarm_stats(self, swarm_id: str) -> Dict[str, Any]:
        """Get statistics for a swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            Dictionary with swarm statistics

        Raises:
            ValueError: If swarm_id is unknown
        """
        if swarm_id not in self.swarm_registry:
            raise ValueError(f"Unknown swarm: {swarm_id}")

        profile = self.swarm_registry[swarm_id]

        from infrafabric.optimise import get_total_cost, get_cost_report

        return {
            'swarm_id': swarm_id,
            'capabilities': [c.value for c in profile.capabilities],
            'cost_per_hour': profile.cost_per_hour,
            'reputation': profile.reputation_score,
            'budget_remaining': profile.current_budget_remaining,
            'budget_spent': get_total_cost(provider=swarm_id),
            'circuit_breaker': self._circuit_breakers.get(swarm_id, False),
            'failure_count': self._failure_counts.get(swarm_id, 0),
            'available': self.is_swarm_available(swarm_id),
            'model': profile.model,
        }
