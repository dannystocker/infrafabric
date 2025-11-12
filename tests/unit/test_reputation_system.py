"""Unit tests for P0.3.5 - Reputation System

This test suite validates SLO-based reputation scoring for swarm agents.
Reputation scores are used by IF.governor to prioritize high-performing swarms.

Philosophy:
- Wu Lun (朋友): Fair, objective evaluation of peer swarms
- IF.ground Observable: All reputation changes are auditable
- IF.TTT Trustworthy: Deterministic scoring prevents favoritism

Test Coverage:
- Reputation calculation based on SLO compliance
- Success rate penalties
- Latency penalties
- Reputation history tracking
- Top performers ranking
- Reputation decay (optional)
"""

import pytest
import time
from infrafabric.chassis.slo import SLOTracker, ServiceLevelObjective
from infrafabric.chassis.reputation import ReputationScore, ReputationSystem


class TestReputationScore:
    """Test ReputationScore dataclass"""

    def test_reputation_score_creation(self):
        """Test creating a reputation score"""
        score = ReputationScore(
            swarm_id="session-4-sip",
            score=0.95,
            timestamp=time.time(),
            slo_compliance=None,
            penalties_applied=[]
        )
        assert score.swarm_id == "session-4-sip"
        assert score.score == 0.95
        assert score.penalties_applied == []

    def test_reputation_score_to_dict(self):
        """Test converting reputation score to dictionary"""
        score = ReputationScore(
            swarm_id="session-4-sip",
            score=0.95,
            timestamp=1234567890.0,
            slo_compliance=None,
            penalties_applied=["success_rate_shortfall_0.05"]
        )
        data = score.to_dict()

        assert data["swarm_id"] == "session-4-sip"
        assert data["score"] == 0.95
        assert data["timestamp"] == 1234567890.0
        assert data["penalties_applied"] == ["success_rate_shortfall_0.05"]
        assert data["slo_compliance"] is None


class TestReputationSystem:
    """Test ReputationSystem for swarm prioritization"""

    @pytest.fixture
    def slo_tracker(self):
        """Create SLO tracker with standard SLO"""
        tracker = SLOTracker()
        tracker.set_slo("session-4-sip", ServiceLevelObjective(
            p99_latency_ms=100,
            success_rate=0.99,
            availability=0.999
        ))
        return tracker

    @pytest.fixture
    def reputation_system(self, slo_tracker):
        """Create reputation system"""
        return ReputationSystem(slo_tracker)

    def test_reputation_system_initialization(self, slo_tracker):
        """Test initializing reputation system"""
        system = ReputationSystem(slo_tracker)
        assert system.slo_tracker == slo_tracker
        assert system.reputation_scores == {}
        assert system.reputation_history == {}
        assert system.decay_enabled is False

    def test_reputation_system_with_decay_enabled(self, slo_tracker):
        """Test initializing reputation system with decay enabled"""
        system = ReputationSystem(slo_tracker, decay_enabled=True)
        assert system.decay_enabled is True

    def test_new_swarm_gets_perfect_reputation(self, reputation_system):
        """Test that new swarms get 1.0 reputation (benefit of the doubt)"""
        reputation = reputation_system.calculate_reputation("new-swarm")
        assert reputation == 1.0

    def test_compliant_swarm_gets_high_reputation(self, slo_tracker, reputation_system):
        """Test that SLO-compliant swarms get high reputation"""
        # Record 100 successful operations with good latency
        for _ in range(100):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        reputation = reputation_system.calculate_reputation("session-4-sip")

        # Should be close to 1.0 (perfect)
        assert reputation >= 0.95
        assert reputation <= 1.0

    def test_success_rate_penalty(self, slo_tracker, reputation_system):
        """Test that low success rate reduces reputation"""
        # Record 80% success rate (target is 99%)
        for _ in range(80):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)
        for _ in range(20):
            slo_tracker.record_metric("session-4-sip", latency_ms=None, success=False)

        reputation = reputation_system.calculate_reputation("session-4-sip")

        # Should be significantly lower than 1.0
        # Success rate: 0.80
        # Target: 0.99
        # Shortfall: 0.19
        # Penalty: min(0.19 * 2, 0.3) = 0.30
        # Reputation: (1.0 - 0.30) * 0.80 = 0.56
        assert reputation < 0.80
        assert reputation > 0.40

    def test_latency_penalty(self, slo_tracker, reputation_system):
        """Test that high latency reduces reputation"""
        # Record high latency (200ms when target is 100ms)
        for _ in range(100):
            slo_tracker.record_metric("session-4-sip", latency_ms=200.0, success=True)

        reputation = reputation_system.calculate_reputation("session-4-sip")

        # Should be lower than 1.0 due to latency penalty
        # Overage ratio: 200 / 100 = 2.0
        # Penalty: min((2.0 - 1.0) * 0.2, 0.2) = 0.2
        # Reputation: (1.0 - 0.2) * 1.0 = 0.80
        assert reputation < 0.85
        assert reputation > 0.75

    def test_combined_penalties(self, slo_tracker, reputation_system):
        """Test that multiple SLO violations result in lower reputation"""
        # Record 85% success rate with high latency
        for _ in range(85):
            slo_tracker.record_metric("session-4-sip", latency_ms=150.0, success=True)
        for _ in range(15):
            slo_tracker.record_metric("session-4-sip", latency_ms=None, success=False)

        reputation = reputation_system.calculate_reputation("session-4-sip")

        # Should have both success rate and latency penalties
        assert reputation < 0.85
        assert reputation > 0.40

    def test_reputation_history_tracking(self, slo_tracker, reputation_system):
        """Test that reputation history is tracked"""
        # Calculate reputation twice
        for _ in range(50):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        reputation_system.calculate_reputation("session-4-sip")
        reputation_system.calculate_reputation("session-4-sip")

        history = reputation_system.get_reputation_history("session-4-sip")
        assert len(history) == 2
        assert all(isinstance(r, ReputationScore) for r in history)
        # History should be newest first
        assert history[0].timestamp >= history[1].timestamp

    def test_reputation_history_limit(self, slo_tracker, reputation_system):
        """Test that reputation history is limited to 100 records"""
        for _ in range(10):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        # Calculate reputation 150 times
        for _ in range(150):
            reputation_system.calculate_reputation("session-4-sip")

        history = reputation_system.get_reputation_history("session-4-sip")
        assert len(history) == 100

    def test_get_reputation(self, slo_tracker, reputation_system):
        """Test getting current reputation score"""
        # New swarm should default to 1.0
        assert reputation_system.get_reputation("new-swarm") == 1.0

        # Calculate reputation
        for _ in range(50):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        reputation = reputation_system.calculate_reputation("session-4-sip")
        assert reputation_system.get_reputation("session-4-sip") == reputation

    def test_get_reputation_history_with_limit(self, slo_tracker, reputation_system):
        """Test getting limited reputation history"""
        for _ in range(10):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        # Calculate reputation 10 times
        for _ in range(10):
            reputation_system.calculate_reputation("session-4-sip")

        # Get only last 5
        history = reputation_system.get_reputation_history("session-4-sip", limit=5)
        assert len(history) == 5

    def test_get_reputation_history_empty(self, reputation_system):
        """Test getting reputation history for unknown swarm"""
        history = reputation_system.get_reputation_history("unknown-swarm")
        assert history == []

    def test_get_all_reputations(self, slo_tracker, reputation_system):
        """Test getting all reputation scores"""
        # Set up multiple swarms
        slo_tracker.set_slo("swarm-1", ServiceLevelObjective(100, 0.99, 0.999))
        slo_tracker.set_slo("swarm-2", ServiceLevelObjective(100, 0.99, 0.999))

        for swarm_id in ["swarm-1", "swarm-2"]:
            for _ in range(50):
                slo_tracker.record_metric(swarm_id, latency_ms=50.0, success=True)

        all_reputations = reputation_system.get_all_reputations()

        assert "swarm-1" in all_reputations
        assert "swarm-2" in all_reputations
        assert all(0.0 <= score <= 1.0 for score in all_reputations.values())

    def test_get_top_performers(self, slo_tracker, reputation_system):
        """Test getting top-performing swarms by reputation"""
        # Create swarms with different performance levels
        swarms = {
            "excellent-swarm": (100, 0),    # 100% success, good latency
            "good-swarm": (95, 5),          # 95% success
            "fair-swarm": (80, 20),         # 80% success
            "poor-swarm": (60, 40),         # 60% success
        }

        for swarm_id in swarms.keys():
            slo_tracker.set_slo(swarm_id, ServiceLevelObjective(100, 0.99, 0.999))

        for swarm_id, (successes, failures) in swarms.items():
            for _ in range(successes):
                slo_tracker.record_metric(swarm_id, latency_ms=50.0, success=True)
            for _ in range(failures):
                slo_tracker.record_metric(swarm_id, latency_ms=None, success=False)

        top_performers = reputation_system.get_top_performers(limit=3)

        assert len(top_performers) == 3
        # Check ordering (highest first)
        assert top_performers[0][1] >= top_performers[1][1]
        assert top_performers[1][1] >= top_performers[2][1]
        # Excellent swarm should be first
        assert top_performers[0][0] == "excellent-swarm"

    def test_get_reputation_summary(self, slo_tracker, reputation_system):
        """Test getting comprehensive reputation summary"""
        # Record varying performance
        for i in range(100):
            success = i % 10 != 0  # 90% success rate
            latency = 50.0 if success else None
            slo_tracker.record_metric("session-4-sip", latency_ms=latency, success=success)
            reputation_system.calculate_reputation("session-4-sip")

        summary = reputation_system.get_reputation_summary("session-4-sip")

        assert summary["swarm_id"] == "session-4-sip"
        assert "current_reputation" in summary
        assert summary["history_count"] == 100
        assert "min_reputation" in summary
        assert "max_reputation" in summary
        assert "avg_reputation" in summary
        assert summary["min_reputation"] <= summary["avg_reputation"] <= summary["max_reputation"]

    def test_get_reputation_summary_for_new_swarm(self, reputation_system):
        """Test reputation summary for swarm with no history"""
        summary = reputation_system.get_reputation_summary("new-swarm")

        assert summary["swarm_id"] == "new-swarm"
        assert summary["current_reputation"] == 1.0
        assert summary["history_count"] == 0

    def test_reputation_decay_disabled_by_default(self, slo_tracker, reputation_system):
        """Test that reputation decay is disabled by default"""
        for _ in range(50):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        reputation_before = reputation_system.calculate_reputation("session-4-sip")

        # Apply decay (should have no effect)
        reputation_system.apply_decay(decay_rate=0.1)

        reputation_after = reputation_system.get_reputation("session-4-sip")
        assert reputation_after == reputation_before

    def test_reputation_decay_when_enabled(self, slo_tracker):
        """Test that reputation decays over time when enabled"""
        reputation_system = ReputationSystem(slo_tracker, decay_enabled=True)

        for _ in range(50):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        # Calculate initial reputation
        reputation_before = reputation_system.calculate_reputation("session-4-sip")

        # Manually set timestamp to 2 days ago
        reputation_system.reputation_history["session-4-sip"][-1].timestamp = time.time() - (2 * 86400)

        # Apply decay
        reputation_system.apply_decay(decay_rate=0.01)

        reputation_after = reputation_system.get_reputation("session-4-sip")
        # Should be lower due to 2 days of decay at 1% per day
        # decay_factor = (1 - 0.01) ^ 2 = 0.9801
        assert reputation_after < reputation_before
        assert reputation_after >= reputation_before * 0.96  # Allow some tolerance

    def test_penalties_applied_tracking(self, slo_tracker, reputation_system):
        """Test that penalties are tracked in reputation history"""
        # Record poor performance
        for _ in range(70):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)
        for _ in range(30):
            slo_tracker.record_metric("session-4-sip", latency_ms=None, success=False)

        reputation_system.calculate_reputation("session-4-sip")

        history = reputation_system.get_reputation_history("session-4-sip")
        assert len(history) == 1
        # Should have success rate penalty
        assert any("success_rate" in p for p in history[0].penalties_applied)

    def test_reputation_score_bounds(self, slo_tracker, reputation_system):
        """Test that reputation scores are always between 0.0 and 1.0"""
        # Test perfect performance
        for _ in range(100):
            slo_tracker.record_metric("perfect-swarm", latency_ms=10.0, success=True)

        slo_tracker.set_slo("perfect-swarm", ServiceLevelObjective(100, 0.99, 0.999))
        perfect_reputation = reputation_system.calculate_reputation("perfect-swarm")
        assert 0.0 <= perfect_reputation <= 1.0

        # Test terrible performance
        for _ in range(100):
            slo_tracker.record_metric("poor-swarm", latency_ms=None, success=False)

        slo_tracker.set_slo("poor-swarm", ServiceLevelObjective(100, 0.99, 0.999))
        poor_reputation = reputation_system.calculate_reputation("poor-swarm")
        assert 0.0 <= poor_reputation <= 1.0

    def test_reputation_updates_on_new_metrics(self, slo_tracker, reputation_system):
        """Test that reputation updates when new metrics are recorded"""
        # Start with good performance
        for _ in range(100):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        good_reputation = reputation_system.calculate_reputation("session-4-sip")

        # Add poor performance
        for _ in range(50):
            slo_tracker.record_metric("session-4-sip", latency_ms=None, success=False)

        updated_reputation = reputation_system.calculate_reputation("session-4-sip")

        # Reputation should decrease
        assert updated_reputation < good_reputation

    def test_reputation_with_slo_compliance_data(self, slo_tracker, reputation_system):
        """Test that reputation includes SLO compliance data in history"""
        for _ in range(50):
            slo_tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        reputation_system.calculate_reputation("session-4-sip")

        history = reputation_system.get_reputation_history("session-4-sip")
        assert len(history) == 1
        assert history[0].slo_compliance is not None
        assert history[0].slo_compliance.swarm_id == "session-4-sip"

    def test_multiple_swarms_independent_reputations(self, slo_tracker, reputation_system):
        """Test that multiple swarms maintain independent reputations"""
        # Set up two swarms with different SLOs
        slo_tracker.set_slo("swarm-a", ServiceLevelObjective(100, 0.99, 0.999))
        slo_tracker.set_slo("swarm-b", ServiceLevelObjective(50, 0.95, 0.99))

        # Swarm A: perfect performance
        for _ in range(100):
            slo_tracker.record_metric("swarm-a", latency_ms=50.0, success=True)

        # Swarm B: poor performance
        for _ in range(50):
            slo_tracker.record_metric("swarm-b", latency_ms=100.0, success=True)
        for _ in range(50):
            slo_tracker.record_metric("swarm-b", latency_ms=None, success=False)

        reputation_a = reputation_system.calculate_reputation("swarm-a")
        reputation_b = reputation_system.calculate_reputation("swarm-b")

        # Swarm A should have higher reputation
        assert reputation_a > reputation_b
        assert reputation_a >= 0.95
        assert reputation_b < 0.70


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
