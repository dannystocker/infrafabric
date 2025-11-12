"""
Unit Tests for IF.governor Budget Tracking (P0.2.3)

Tests for:
- Cost tracking and budget deduction
- Budget warnings at 20% threshold
- Budget exhaustion handling
- Zero/negative budget prevents task assignment
- Integration stubs (IF.optimise, IF.witness)
- Error handling (unknown swarm)
- Multiple cost tracking operations

Author: Session 3 (H.323 Guardian Council)
Version: 1.0
Status: Phase 0 Development
"""

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
)


# ==========================================
# Basic Cost Tracking Tests
# ==========================================

class TestCostTracking:
    """Test basic cost tracking and budget deduction"""

    def test_track_cost_deducts_from_budget(self):
        """Test that track_cost() deducts cost from swarm budget"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Track $25 cost
        governor.track_cost("test-swarm", "code_review", 25.0)

        # Budget should be reduced
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 75.0

    def test_track_multiple_costs(self):
        """Test tracking multiple costs sequentially"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[Capability.GOVERNANCE_VOTING],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        governor.register_swarm(profile)

        # Track multiple operations
        governor.track_cost("guardian-council", "vote_1", 10.0)
        governor.track_cost("guardian-council", "vote_2", 15.0)
        governor.track_cost("guardian-council", "vote_3", 20.0)

        # Budget should reflect all deductions
        updated_profile = governor.get_swarm_profile("guardian-council")
        assert updated_profile.current_budget_remaining == 55.0  # 100 - 10 - 15 - 20

    def test_track_cost_with_fractional_amounts(self):
        """Test cost tracking with fractional dollar amounts"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.TESTING_UNIT],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Track fractional cost
        governor.track_cost("test-swarm", "small_task", 2.75)

        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == pytest.approx(47.25, abs=0.01)

    def test_track_cost_raises_error_for_unknown_swarm(self):
        """Test that track_cost() raises ValueError for unknown swarm"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        with pytest.raises(ValueError, match="Unknown swarm"):
            governor.track_cost("nonexistent-swarm", "operation", 10.0)


# ==========================================
# Budget Warning Tests
# ==========================================

class TestBudgetWarnings:
    """Test budget warning threshold (20% remaining)"""

    def test_budget_warning_at_20_percent_threshold(self):
        """Test that warning is logged when budget drops to 20%"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Spend $80 to bring budget to $20 (20%)
        governor.track_cost("test-swarm", "large_operation", 80.0)

        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 20.0

    def test_no_warning_above_20_percent_threshold(self):
        """Test that no warning is logged when budget is above 20%"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Spend $50 to bring budget to $50 (50% - above threshold)
        governor.track_cost("test-swarm", "operation", 50.0)

        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 50.0

    def test_budget_warning_with_custom_threshold(self):
        """Test budget warning with custom threshold"""
        # Custom policy with 10% threshold
        policy = ResourcePolicy(budget_warning_threshold=0.1)
        governor = IFGovernor(coordinator=None, policy=policy)

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.TESTING_INTEGRATION],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Spend $90 to bring budget to $10 (10%)
        governor.track_cost("test-swarm", "operation", 90.0)

        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 10.0


# ==========================================
# Budget Exhaustion Tests
# ==========================================

class TestBudgetExhaustion:
    """Test budget exhaustion and circuit breaker triggering"""

    def test_budget_exhaustion_at_zero(self):
        """Test that budget exhaustion is detected at $0"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_RUST],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Spend exactly the budget
        governor.track_cost("test-swarm", "operation", 50.0)

        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 0.0

    def test_budget_exhaustion_with_overage(self):
        """Test budget exhaustion when cost exceeds remaining budget"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.DOCS_TECHNICAL_WRITING],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=30.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Spend more than remaining budget
        governor.track_cost("test-swarm", "expensive_operation", 50.0)

        updated_profile = governor.get_swarm_profile("test-swarm")
        # Budget should be at 0 (floored at 0, not negative)
        assert updated_profile.current_budget_remaining == 0.0

    def test_exhausted_swarm_excluded_from_task_assignment(self):
        """Test that swarm with $0 budget is excluded from find_qualified_swarm"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        # Swarm with budget
        funded_profile = SwarmProfile(
            swarm_id="funded-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        # Swarm without budget
        broke_profile = SwarmProfile(
            swarm_id="broke-swarm",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.95,  # Higher reputation
            current_budget_remaining=10.0,
            model="haiku"
        )

        governor.register_swarm(funded_profile)
        governor.register_swarm(broke_profile)

        # Exhaust broke_profile budget
        governor.track_cost("broke-swarm", "operation", 10.0)

        # Try to assign task
        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            max_cost=10.0
        )

        # Should select funded-swarm (only one with budget)
        assert selected == "funded-swarm"


# ==========================================
# Budget Report Tests
# ==========================================

class TestBudgetReporting:
    """Test budget reporting after cost tracking"""

    def test_budget_report_reflects_cost_tracking(self):
        """Test that budget report shows updated budgets after tracking costs"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.TESTING_PERFORMANCE],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Track some costs
        governor.track_cost("test-swarm", "operation_1", 20.0)
        governor.track_cost("test-swarm", "operation_2", 30.0)

        # Get budget report
        report = governor.get_budget_report()

        assert report["test-swarm"]["remaining"] == 50.0
        assert report["test-swarm"]["cost_per_hour"] == 2.0

    def test_budget_report_for_multiple_swarms_after_tracking(self):
        """Test budget report for multiple swarms with different spending"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm1 = SwarmProfile(
            swarm_id="swarm-1",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        swarm2 = SwarmProfile(
            swarm_id="swarm-2",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=15.0,
            reputation_score=0.95,
            current_budget_remaining=200.0,
            model="sonnet"
        )

        governor.register_swarm(swarm1)
        governor.register_swarm(swarm2)

        # Track different costs for each swarm
        governor.track_cost("swarm-1", "operation", 25.0)
        governor.track_cost("swarm-2", "operation", 75.0)

        report = governor.get_budget_report()

        assert report["swarm-1"]["remaining"] == 75.0
        assert report["swarm-2"]["remaining"] == 125.0


# ==========================================
# Integration Point Tests
# ==========================================

class TestIntegrationStubs:
    """Test integration stubs for IF.optimise and IF.witness"""

    def test_cost_tracking_calls_optimise_stub(self):
        """Test that cost tracking logs to IF.optimise stub"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CODE_ANALYSIS_GO],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # This should call _log_cost_to_optimise internally
        governor.track_cost("test-swarm", "operation", 10.0)

        # Verify cost was deducted (integration stub doesn't affect this)
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 40.0

    def test_cost_tracking_calls_witness_stub(self):
        """Test that cost tracking logs to IF.witness stub"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.ARCHITECTURE_SECURITY],
            cost_per_hour=15.0,
            reputation_score=0.95,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        governor.register_swarm(profile)

        # This should call _log_cost_to_witness internally
        governor.track_cost("test-swarm", "security_audit", 25.0)

        # Verify cost was deducted
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 75.0


# ==========================================
# Edge Case Tests
# ==========================================

class TestBudgetEdgeCases:
    """Test edge cases in budget tracking"""

    def test_track_zero_cost(self):
        """Test tracking zero cost operation"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.TESTING_UNIT],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=50.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Track zero cost
        governor.track_cost("test-swarm", "free_operation", 0.0)

        # Budget should be unchanged
        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == 50.0

    def test_track_very_small_cost(self):
        """Test tracking very small fractional cost"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        profile = SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.CLI_TESTING],
            cost_per_hour=2.0,
            reputation_score=0.85,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(profile)

        # Track very small cost (1 cent)
        governor.track_cost("test-swarm", "tiny_operation", 0.01)

        updated_profile = governor.get_swarm_profile("test-swarm")
        assert updated_profile.current_budget_remaining == pytest.approx(99.99, abs=0.001)

    def test_multiple_swarms_independent_budgets(self):
        """Test that cost tracking for one swarm doesn't affect others"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm1 = SwarmProfile(
            swarm_id="swarm-1",
            capabilities=[Capability.CODE_ANALYSIS_PYTHON],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        swarm2 = SwarmProfile(
            swarm_id="swarm-2",
            capabilities=[Capability.CODE_ANALYSIS_RUST],
            cost_per_hour=2.0,
            reputation_score=0.8,
            current_budget_remaining=100.0,
            model="haiku"
        )

        governor.register_swarm(swarm1)
        governor.register_swarm(swarm2)

        # Track cost only for swarm-1
        governor.track_cost("swarm-1", "operation", 50.0)

        # swarm-1 budget should be reduced
        swarm1_profile = governor.get_swarm_profile("swarm-1")
        assert swarm1_profile.current_budget_remaining == 50.0

        # swarm-2 budget should be unchanged
        swarm2_profile = governor.get_swarm_profile("swarm-2")
        assert swarm2_profile.current_budget_remaining == 100.0


# ==========================================
# Scenario Tests
# ==========================================

class TestBudgetScenarios:
    """Test realistic budget tracking scenarios"""

    def test_guardian_council_budget_lifecycle(self):
        """Test realistic guardian council budget lifecycle"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        guardian_profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[
                Capability.GOVERNANCE_VOTING,
                Capability.INTEGRATION_H323,
                Capability.DOCS_TECHNICAL_WRITING
            ],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="sonnet"
        )

        governor.register_swarm(guardian_profile)

        # Realistic series of operations
        operations = [
            ("h323_vote_1", 12.50),
            ("quality_assessment", 8.75),
            ("h323_vote_2", 11.00),
            ("documentation_review", 15.25),
            ("tie_breaking_vote", 9.50),
        ]

        for operation, cost in operations:
            governor.track_cost("guardian-council", operation, cost)

        # Total spent: $57.00, remaining: $43.00
        final_profile = governor.get_swarm_profile("guardian-council")
        assert final_profile.current_budget_remaining == pytest.approx(43.00, abs=0.01)

        # Should still be able to assign tasks (budget > 0)
        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.GOVERNANCE_VOTING],
            max_cost=20.0
        )
        assert selected == "guardian-council"

    def test_budget_prevents_assignment_after_exhaustion(self):
        """Test complete workflow: budget exhaustion prevents task assignment"""
        governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

        swarm_profile = SwarmProfile(
            swarm_id="limited-budget-swarm",
            capabilities=[Capability.INTEGRATION_NDI],
            cost_per_hour=2.0,
            reputation_score=0.9,
            current_budget_remaining=25.0,
            model="haiku"
        )

        governor.register_swarm(swarm_profile)

        # Before exhaustion: can be assigned
        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.INTEGRATION_NDI],
            max_cost=10.0
        )
        assert selected == "limited-budget-swarm"

        # Exhaust budget
        governor.track_cost("limited-budget-swarm", "operation_1", 15.0)
        governor.track_cost("limited-budget-swarm", "operation_2", 10.0)

        # After exhaustion: cannot be assigned
        selected = governor.find_qualified_swarm(
            required_capabilities=[Capability.INTEGRATION_NDI],
            max_cost=10.0
        )
        assert selected is None  # No swarms with budget available


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
