"""Reputation System for Swarm Prioritization (P0.3.5)

This module implements SLO-based reputation scoring for swarm agents.
Reputation scores are used by IF.governor to prioritize high-performing
swarms for task assignment.

Philosophy:
- Wu Lun (朋友): Fair, objective evaluation of peer swarms
- IF.ground Observable: All reputation changes are auditable
- IF.TTT Trustworthy: Deterministic scoring prevents favoritism

Task: P0.3.5 - Reputation system
Est: 2h (Sonnet)
Session: 4 (SIP)
Dependencies: P0.3.4 (SLO tracking)
Unblocks: P0.3.6 (Security audit tests)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import json
from infrafabric.chassis.slo import SLOTracker, SLOCompliance


@dataclass
class ReputationScore:
    """Reputation score with history

    Attributes:
        swarm_id: Swarm identifier
        score: Current reputation score (0.0-1.0)
        timestamp: When score was calculated
        slo_compliance: SLO compliance that generated this score
        penalties_applied: List of penalties applied
    """
    swarm_id: str
    score: float
    timestamp: float
    slo_compliance: Optional[SLOCompliance]
    penalties_applied: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary"""
        return {
            "swarm_id": self.swarm_id,
            "score": self.score,
            "timestamp": self.timestamp,
            "slo_compliance": self.slo_compliance.to_dict() if self.slo_compliance else None,
            "penalties_applied": self.penalties_applied,
        }


class ReputationSystem:
    """SLO-based reputation scoring for swarm prioritization

    The ReputationSystem calculates reputation scores based on SLO compliance:
    - High performers (meeting SLOs) get high scores (0.9-1.0)
    - Medium performers get medium scores (0.7-0.9)
    - Low performers (missing SLOs) get low scores (<0.7)

    Reputation scores are used by IF.governor to:
    - Prioritize high-reputation swarms for task assignment
    - Identify underperforming swarms for investigation
    - Fair resource allocation based on performance

    Example:
        >>> tracker = SLOTracker()
        >>> reputation = ReputationSystem(tracker)
        >>>
        >>> # After swarm completes tasks...
        >>> score = reputation.calculate_reputation("session-4-sip")
        >>> assert 0.0 <= score <= 1.0
    """

    def __init__(self, slo_tracker: SLOTracker, decay_enabled: bool = False):
        """Initialize reputation system

        Args:
            slo_tracker: SLO tracker to get compliance data
            decay_enabled: Enable reputation decay over time (optional)
        """
        self.slo_tracker = slo_tracker
        self.reputation_scores: Dict[str, float] = {}
        self.reputation_history: Dict[str, List[ReputationScore]] = {}
        self.decay_enabled = decay_enabled

    def calculate_reputation(self, swarm_id: str) -> float:
        """Calculate reputation score based on SLO compliance

        Args:
            swarm_id: Swarm identifier

        Returns:
            Reputation score 0.0-1.0
            - 1.0 = Perfect (new swarms, or meeting all SLOs)
            - 0.9-1.0 = Excellent (meeting SLOs)
            - 0.7-0.9 = Good (minor SLO violations)
            - 0.5-0.7 = Fair (significant SLO violations)
            - <0.5 = Poor (major SLO violations)

        Example:
            >>> reputation = ReputationSystem(slo_tracker)
            >>> score = reputation.calculate_reputation("session-4")
            >>> assert 0.0 <= score <= 1.0
        """
        compliance = self.slo_tracker.calculate_slo_compliance(swarm_id)

        if not compliance:
            # New swarm - benefit of the doubt
            return 1.0

        # Start with perfect reputation
        reputation = 1.0
        penalties = []

        # Success rate penalty
        if not compliance.success_rate_compliant:
            # Calculate penalty based on how far below target
            shortfall = compliance.success_rate_target - compliance.success_rate
            penalty = min(shortfall * 2, 0.3)  # Max 30% penalty
            reputation -= penalty
            penalties.append(f"success_rate_shortfall_{shortfall:.2f}")

        # Latency penalty
        if not compliance.p99_latency_compliant:
            # Calculate penalty based on how far above target
            overage_ratio = compliance.p99_latency_ms / compliance.p99_latency_target
            penalty = min((overage_ratio - 1.0) * 0.2, 0.2)  # Max 20% penalty
            reputation -= penalty
            penalties.append(f"latency_overage_{overage_ratio:.2f}x")

        # Weight by actual success rate (heavily impacts low success rates)
        reputation *= compliance.success_rate

        # Ensure reputation stays in valid range
        reputation = max(0.0, min(1.0, reputation))

        # Store reputation
        self.reputation_scores[swarm_id] = reputation

        # Store in history
        reputation_record = ReputationScore(
            swarm_id=swarm_id,
            score=reputation,
            timestamp=time.time(),
            slo_compliance=compliance,
            penalties_applied=penalties
        )

        if swarm_id not in self.reputation_history:
            self.reputation_history[swarm_id] = []
        self.reputation_history[swarm_id].append(reputation_record)

        # Keep last 100 reputation records
        self.reputation_history[swarm_id] = self.reputation_history[swarm_id][-100:]

        # Log reputation update
        self._log_operation(
            operation='reputation_calculated',
            params={
                'swarm_id': swarm_id,
                'reputation': reputation,
                'penalties': penalties,
                'success_rate': compliance.success_rate,
                'p99_latency_ms': compliance.p99_latency_ms
            }
        )

        # Update IF.governor (if available)
        try:
            from infrafabric.governor import update_reputation
            update_reputation(swarm_id, reputation)
        except ImportError:
            # IF.governor not available yet - that's OK
            pass

        return reputation

    def get_reputation(self, swarm_id: str) -> float:
        """Get current reputation score

        Args:
            swarm_id: Swarm identifier

        Returns:
            Current reputation score (default 1.0 for new swarms)
        """
        return self.reputation_scores.get(swarm_id, 1.0)

    def get_reputation_history(
        self,
        swarm_id: str,
        limit: Optional[int] = None
    ) -> List[ReputationScore]:
        """Get reputation history for swarm

        Args:
            swarm_id: Swarm identifier
            limit: Optional limit on records (most recent first)

        Returns:
            List of reputation scores (newest first)
        """
        if swarm_id not in self.reputation_history:
            return []

        history = list(reversed(self.reputation_history[swarm_id]))
        if limit:
            return history[:limit]
        return history

    def get_all_reputations(self) -> Dict[str, float]:
        """Get all current reputation scores

        Returns:
            Dictionary mapping swarm_id to reputation score
        """
        # Calculate fresh reputation for all swarms with SLOs
        for swarm_id in self.slo_tracker.slos.keys():
            self.calculate_reputation(swarm_id)

        return dict(self.reputation_scores)

    def get_top_performers(self, limit: int = 10) -> List[tuple[str, float]]:
        """Get top-performing swarms by reputation

        Args:
            limit: Number of top performers to return

        Returns:
            List of (swarm_id, reputation) tuples, sorted by reputation descending
        """
        # Refresh all reputations
        self.get_all_reputations()

        # Sort by reputation descending
        sorted_reputations = sorted(
            self.reputation_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_reputations[:limit]

    def get_reputation_summary(self, swarm_id: str) -> Dict[str, any]:
        """Get comprehensive reputation summary

        Args:
            swarm_id: Swarm identifier

        Returns:
            Dictionary with reputation stats
        """
        if swarm_id not in self.reputation_history:
            return {
                "swarm_id": swarm_id,
                "current_reputation": 1.0,
                "history_count": 0
            }

        history = self.reputation_history[swarm_id]
        scores = [r.score for r in history]

        return {
            "swarm_id": swarm_id,
            "current_reputation": self.reputation_scores.get(swarm_id, 1.0),
            "history_count": len(history),
            "min_reputation": min(scores) if scores else 1.0,
            "max_reputation": max(scores) if scores else 1.0,
            "avg_reputation": sum(scores) / len(scores) if scores else 1.0,
            "latest_penalties": history[-1].penalties_applied if history else [],
        }

    def apply_decay(self, decay_rate: float = 0.01) -> None:
        """Apply reputation decay to inactive swarms

        Optionally decay reputation over time for swarms that haven't
        completed tasks recently. This encourages continued activity.

        Args:
            decay_rate: Rate of decay per day (default 1% per day)

        Note:
            Only applied if decay_enabled=True in constructor
        """
        if not self.decay_enabled:
            return

        current_time = time.time()
        one_day_seconds = 86400

        for swarm_id, history in self.reputation_history.items():
            if not history:
                continue

            last_update = history[-1].timestamp
            days_inactive = (current_time - last_update) / one_day_seconds

            if days_inactive > 1.0:
                current_reputation = self.reputation_scores.get(swarm_id, 1.0)
                decay_factor = (1.0 - decay_rate) ** days_inactive
                new_reputation = current_reputation * decay_factor

                self.reputation_scores[swarm_id] = new_reputation

                self._log_operation(
                    operation='reputation_decayed',
                    params={
                        'swarm_id': swarm_id,
                        'days_inactive': days_inactive,
                        'old_reputation': current_reputation,
                        'new_reputation': new_reputation
                    }
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
                component='IF.chassis.reputation',
                operation=operation,
                params=params,
                severity=severity
            )
        except ImportError:
            # IF.witness not available - log to stderr
            import sys
            print(
                f"[IF.chassis.reputation] {severity}: {operation} - {json.dumps(params)}",
                file=sys.stderr
            )


__all__ = [
    "ReputationScore",
    "ReputationSystem",
]
