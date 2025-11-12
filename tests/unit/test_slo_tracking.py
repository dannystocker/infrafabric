"""Unit tests for SLO Tracking (P0.3.4)

Tests cover:
- ServiceLevelObjective creation and validation
- PerformanceMetric recording
- SLO compliance calculation
- p99 latency calculation
- Success rate calculation
- Violation tracking and logging
- Statistics generation

Task: P0.3.4 - SLO tracking
Session: 4 (SIP)
Model: Sonnet
"""

import pytest
import time
from infrafabric.chassis.slo import (
    ServiceLevelObjective,
    PerformanceMetric,
    SLOCompliance,
    SLOTracker,
)


class TestServiceLevelObjective:
    """Test ServiceLevelObjective dataclass"""

    def test_create_slo(self):
        """Create valid SLO"""
        slo = ServiceLevelObjective(
            p99_latency_ms=100,
            success_rate=0.99,
            availability=0.999
        )

        assert slo.p99_latency_ms == 100
        assert slo.success_rate == 0.99
        assert slo.availability == 0.999

    def test_slo_validation_negative_latency(self):
        """Negative latency raises ValueError"""
        with pytest.raises(ValueError, match="non-negative"):
            ServiceLevelObjective(
                p99_latency_ms=-1,
                success_rate=0.99,
                availability=0.999
            )

    def test_slo_validation_success_rate_bounds(self):
        """Success rate must be 0.0-1.0"""
        # Valid: 0.0
        ServiceLevelObjective(p99_latency_ms=100, success_rate=0.0, availability=0.9)

        # Valid: 1.0
        ServiceLevelObjective(p99_latency_ms=100, success_rate=1.0, availability=0.9)

        # Invalid: -0.1
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            ServiceLevelObjective(p99_latency_ms=100, success_rate=-0.1, availability=0.9)

        # Invalid: 1.1
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            ServiceLevelObjective(p99_latency_ms=100, success_rate=1.1, availability=0.9)

    def test_slo_validation_availability_bounds(self):
        """Availability must be 0.0-1.0"""
        # Valid: 0.0
        ServiceLevelObjective(p99_latency_ms=100, success_rate=0.9, availability=0.0)

        # Valid: 1.0
        ServiceLevelObjective(p99_latency_ms=100, success_rate=0.9, availability=1.0)

        # Invalid: -0.1
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            ServiceLevelObjective(p99_latency_ms=100, success_rate=0.9, availability=-0.1)

        # Invalid: 1.1
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            ServiceLevelObjective(p99_latency_ms=100, success_rate=0.9, availability=1.1)

    def test_slo_to_dict(self):
        """Convert SLO to dictionary"""
        slo = ServiceLevelObjective(
            p99_latency_ms=100,
            success_rate=0.99,
            availability=0.999
        )

        data = slo.to_dict()

        assert data["p99_latency_ms"] == 100
        assert data["success_rate"] == 0.99
        assert data["availability"] == 0.999


class TestPerformanceMetric:
    """Test PerformanceMetric dataclass"""

    def test_create_successful_metric(self):
        """Create successful operation metric"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            latency_ms=45.2,
            success=True
        )

        assert metric.latency_ms == 45.2
        assert metric.success is True

    def test_create_failed_metric(self):
        """Create failed operation metric"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            latency_ms=None,  # No latency for failed operation
            success=False
        )

        assert metric.latency_ms is None
        assert metric.success is False

    def test_metric_with_metadata(self):
        """Create metric with metadata"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            latency_ms=45.2,
            success=True,
            metadata={"task_type": "sip_integration"}
        )

        assert metric.metadata["task_type"] == "sip_integration"


class TestSLOTracker:
    """Test SLOTracker"""

    def test_set_slo(self):
        """Set SLO for swarm"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(
            p99_latency_ms=100,
            success_rate=0.99,
            availability=0.999
        )

        tracker.set_slo("session-4-sip", slo)

        assert "session-4-sip" in tracker.slos
        assert tracker.slos["session-4-sip"].p99_latency_ms == 100

    def test_record_metric(self):
        """Record performance metric"""
        tracker = SLOTracker()

        tracker.record_metric("session-4-sip", latency_ms=45.2, success=True)

        assert "session-4-sip" in tracker.metrics
        assert len(tracker.metrics["session-4-sip"]) == 1
        assert tracker.metrics["session-4-sip"][0].latency_ms == 45.2

    def test_record_multiple_metrics(self):
        """Record multiple metrics"""
        tracker = SLOTracker()

        for i in range(10):
            tracker.record_metric("session-4-sip", latency_ms=float(i * 10), success=True)

        assert len(tracker.metrics["session-4-sip"]) == 10

    def test_metrics_sliding_window(self):
        """Metrics limited by sliding window"""
        tracker = SLOTracker(max_metrics_per_swarm=100)

        # Record 150 metrics
        for i in range(150):
            tracker.record_metric("session-4-sip", latency_ms=float(i), success=True)

        # Should only keep last 100
        assert len(tracker.metrics["session-4-sip"]) == 100
        # Should keep most recent metrics
        assert tracker.metrics["session-4-sip"][-1].latency_ms == 149.0


class TestSLOComplianceCalculation:
    """Test SLO compliance calculation"""

    def test_calculate_compliance_no_data(self):
        """No data returns None"""
        tracker = SLOTracker()

        compliance = tracker.calculate_slo_compliance("session-4-sip")

        assert compliance is None

    def test_calculate_compliance_no_slo(self):
        """No SLO configured returns None"""
        tracker = SLOTracker()

        tracker.record_metric("session-4-sip", latency_ms=45, success=True)
        compliance = tracker.calculate_slo_compliance("session-4-sip")

        assert compliance is None

    def test_calculate_compliance_all_passing(self):
        """All metrics passing SLO"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(
            p99_latency_ms=100,
            success_rate=0.99,
            availability=0.999
        )
        tracker.set_slo("session-4-sip", slo)

        # Record 100 successful operations with good latency
        for i in range(100):
            tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)

        compliance = tracker.calculate_slo_compliance("session-4-sip")

        assert compliance is not None
        assert compliance.swarm_id == "session-4-sip"
        assert compliance.total_operations == 100
        assert compliance.success_rate == 1.0  # 100% success
        assert compliance.success_rate_compliant is True
        assert compliance.p99_latency_ms == 50.0
        assert compliance.p99_latency_compliant is True
        assert compliance.overall_compliant is True

    def test_calculate_compliance_success_rate_violation(self):
        """Success rate below SLO"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(
            p99_latency_ms=100,
            success_rate=0.99,  # 99% required
            availability=0.999
        )
        tracker.set_slo("session-4-sip", slo)

        # Record 90 successful, 10 failed (90% success rate)
        for i in range(90):
            tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)
        for i in range(10):
            tracker.record_metric("session-4-sip", latency_ms=None, success=False)

        compliance = tracker.calculate_slo_compliance("session-4-sip")

        assert compliance.success_rate == 0.9  # 90%
        assert compliance.success_rate_compliant is False
        assert compliance.overall_compliant is False

    def test_calculate_compliance_latency_violation(self):
        """p99 latency exceeds SLO"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(
            p99_latency_ms=100,  # 100ms required
            success_rate=0.99,
            availability=0.999
        )
        tracker.set_slo("session-4-sip", slo)

        # Record 100 operations, 99 fast, 1 slow
        for i in range(99):
            tracker.record_metric("session-4-sip", latency_ms=50.0, success=True)
        tracker.record_metric("session-4-sip", latency_ms=150.0, success=True)  # Slow!

        compliance = tracker.calculate_slo_compliance("session-4-sip")

        assert compliance.success_rate == 1.0  # 100% success
        assert compliance.success_rate_compliant is True
        assert compliance.p99_latency_ms == 150.0  # p99 is the slow one
        assert compliance.p99_latency_compliant is False
        assert compliance.overall_compliant is False

    def test_p99_calculation_accuracy(self):
        """p99 latency calculation is accurate"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(p99_latency_ms=100, success_rate=0.99, availability=0.999)
        tracker.set_slo("test", slo)

        # Record 100 operations with known latencies
        for i in range(100):
            tracker.record_metric("test", latency_ms=float(i), success=True)

        compliance = tracker.calculate_slo_compliance("test")

        # p99 of 0-99 should be 99
        assert compliance.p99_latency_ms == 99.0

    def test_success_rate_calculation_accuracy(self):
        """Success rate calculation is accurate"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(p99_latency_ms=100, success_rate=0.95, availability=0.999)
        tracker.set_slo("test", slo)

        # Record 100 operations: 97 success, 3 failures
        for i in range(97):
            tracker.record_metric("test", latency_ms=50.0, success=True)
        for i in range(3):
            tracker.record_metric("test", latency_ms=None, success=False)

        compliance = tracker.calculate_slo_compliance("test")

        assert compliance.success_rate == 0.97  # 97%
        assert compliance.success_rate_compliant is True  # Meets 95% target


class TestViolationTracking:
    """Test SLO violation tracking"""

    def test_violation_logged(self):
        """SLO violation is logged"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(p99_latency_ms=100, success_rate=0.99, availability=0.999)
        tracker.set_slo("test", slo)

        # Create violation: low success rate
        for i in range(90):
            tracker.record_metric("test", latency_ms=50.0, success=True)
        for i in range(10):
            tracker.record_metric("test", latency_ms=None, success=False)

        compliance = tracker.calculate_slo_compliance("test")

        # Violation should be logged
        assert len(tracker.violations) == 1
        assert tracker.violations[0]["swarm_id"] == "test"
        assert not tracker.violations[0]["success_rate_compliant"]

    def test_get_violations_by_swarm(self):
        """Get violations for specific swarm"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(p99_latency_ms=100, success_rate=0.99, availability=0.999)
        tracker.set_slo("swarm-1", slo)
        tracker.set_slo("swarm-2", slo)

        # Create violations for swarm-1
        for i in range(90):
            tracker.record_metric("swarm-1", latency_ms=50.0, success=True)
        for i in range(10):
            tracker.record_metric("swarm-1", latency_ms=None, success=False)

        tracker.calculate_slo_compliance("swarm-1")

        # Create violations for swarm-2
        for i in range(100):
            tracker.record_metric("swarm-2", latency_ms=150.0, success=True)

        tracker.calculate_slo_compliance("swarm-2")

        swarm1_violations = tracker.get_violations("swarm-1")
        swarm2_violations = tracker.get_violations("swarm-2")

        assert len(swarm1_violations) == 1
        assert len(swarm2_violations) == 1
        assert swarm1_violations[0]["swarm_id"] == "swarm-1"
        assert swarm2_violations[0]["swarm_id"] == "swarm-2"


class TestStatistics:
    """Test statistics generation"""

    def test_get_stats(self):
        """Get statistics for swarm"""
        tracker = SLOTracker()

        # Record varied metrics
        tracker.record_metric("test", latency_ms=10.0, success=True)
        tracker.record_metric("test", latency_ms=50.0, success=True)
        tracker.record_metric("test", latency_ms=100.0, success=True)
        tracker.record_metric("test", latency_ms=None, success=False)

        stats = tracker.get_stats("test")

        assert stats["total_operations"] == 4
        assert stats["success_count"] == 3
        assert stats["failure_count"] == 1
        assert stats["success_rate"] == 0.75
        assert stats["latency_min"] == 10.0
        assert stats["latency_max"] == 100.0
        assert stats["latency_mean"] == pytest.approx(53.33, abs=0.01)

    def test_get_stats_no_data(self):
        """Get stats with no data returns empty dict"""
        tracker = SLOTracker()

        stats = tracker.get_stats("nonexistent")

        assert stats == {}


class TestMultipleSwarms:
    """Test tracking multiple swarms"""

    def test_track_multiple_swarms(self):
        """Track multiple swarms independently"""
        tracker = SLOTracker()

        slo1 = ServiceLevelObjective(p99_latency_ms=100, success_rate=0.99, availability=0.999)
        slo2 = ServiceLevelObjective(p99_latency_ms=50, success_rate=0.95, availability=0.99)

        tracker.set_slo("session-1", slo1)
        tracker.set_slo("session-4", slo2)

        # Record metrics for session-1
        for i in range(100):
            tracker.record_metric("session-1", latency_ms=80.0, success=True)

        # Record metrics for session-4
        for i in range(100):
            tracker.record_metric("session-4", latency_ms=40.0, success=True)

        compliance1 = tracker.calculate_slo_compliance("session-1")
        compliance4 = tracker.calculate_slo_compliance("session-4")

        assert compliance1.swarm_id == "session-1"
        assert compliance4.swarm_id == "session-4"
        assert compliance1.overall_compliant is True
        assert compliance4.overall_compliant is True

    def test_get_all_compliance(self):
        """Get compliance for all swarms"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(p99_latency_ms=100, success_rate=0.99, availability=0.999)
        tracker.set_slo("session-1", slo)
        tracker.set_slo("session-4", slo)

        for swarm in ["session-1", "session-4"]:
            for i in range(100):
                tracker.record_metric(swarm, latency_ms=50.0, success=True)

        all_compliance = tracker.get_all_compliance()

        assert len(all_compliance) == 2
        assert "session-1" in all_compliance
        assert "session-4" in all_compliance


class TestSession4Integration:
    """Test Session 4 (SIP) specific scenarios"""

    def test_sip_integration_slo(self):
        """Session 4 SIP integration with realistic SLO"""
        tracker = SLOTracker()

        # SIP integration SLO: <100ms p99, 99% success rate
        slo = ServiceLevelObjective(
            p99_latency_ms=100,
            success_rate=0.99,
            availability=0.999
        )
        tracker.set_slo("session-4-sip", slo)

        # Record realistic SIP metrics
        # 98 successful operations, 2 failures
        for i in range(98):
            tracker.record_metric("session-4-sip", latency_ms=45.0 + i % 10, success=True)
        for i in range(2):
            tracker.record_metric("session-4-sip", latency_ms=None, success=False)

        compliance = tracker.calculate_slo_compliance("session-4-sip")

        assert compliance.success_rate == 0.98  # 98% < 99% target
        assert compliance.success_rate_compliant is False
        assert compliance.overall_compliant is False

    def test_multiple_session_4_tasks(self):
        """Multiple Session 4 tasks tracked independently"""
        tracker = SLOTracker()

        slo = ServiceLevelObjective(p99_latency_ms=100, success_rate=0.99, availability=0.999)

        # Track different task types
        tracker.set_slo("session-4-sip-escalate", slo)
        tracker.set_slo("session-4-sip-proxy", slo)

        for task in ["session-4-sip-escalate", "session-4-sip-proxy"]:
            for i in range(100):
                tracker.record_metric(task, latency_ms=50.0, success=True)

        escalate_compliance = tracker.calculate_slo_compliance("session-4-sip-escalate")
        proxy_compliance = tracker.calculate_slo_compliance("session-4-sip-proxy")

        assert escalate_compliance.overall_compliant is True
        assert proxy_compliance.overall_compliant is True


# Run tests with: pytest tests/unit/test_slo_tracking.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
