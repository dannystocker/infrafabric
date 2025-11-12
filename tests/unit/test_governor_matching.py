"""Unit tests for P0.2.2 - Capability Matching Algorithm

This test suite validates the 70% capability matching algorithm used by
IF.governor for intelligent task assignment.

Philosophy:
- IF.TTT Trustworthy: Objective capability scoring prevents favoritism
- IF.ground Observable: All assignment decisions are auditable
- Wu Lun (朋友): Fair evaluation of peer swarms based on capabilities

Test Coverage:
- Capability matching (Jaccard similarity)
- 70% threshold enforcement
- Combined scoring (capability × reputation / cost)
- Budget enforcement
- Edge cases (no swarms, no match, tie-breaking)
"""

import pytest
from infrafabric.governor import IFGovernor, MatchScore
from infrafabric.schemas.capability import Capability, SwarmProfile, ResourcePolicy


class TestMatchScore:
    """Test MatchScore dataclass"""

    def test_match_score_creation(self):
        """Test creating a match score"""
        score = MatchScore(
            swarm_id="session-4-sip",
            capability_match=0.95,
            reputation=0.90,
            cost_per_hour=2.0,
            combined_score=0.4275,
            qualified=True
        )
        assert score.swarm_id == "session-4-sip"
        assert score.capability_match == 0.95
        assert score.qualified is True

    def test_match_score_to_dict(self):
        """Test converting match score to dictionary"""
        score = MatchScore(
            swarm_id="test-swarm",
            capability_match=0.85,
            reputation=0.95,
            cost_per_hour=1.5,
            combined_score=0.54,
            qualified=True
        )
        data = score.to_dict()

        assert data["swarm_id"] == "test-swarm"
        assert data["capability_match"] == 0.85
        assert data["combined_score"] == 0.54


class TestIFGovernorInitialization:
    """Test IFGovernor initialization"""

    def test_create_governor_with_default_policy(self):
        """Test creating governor with default policy"""
        governor = IFGovernor()
        assert governor.policy.min_capability_match == 0.7
        assert governor.swarm_registry == {}

    def test_create_governor_with_custom_policy(self):
        """Test creating governor with custom policy"""
        policy = ResourcePolicy(min_capability_match=0.8)
        governor = IFGovernor(policy=policy)
        assert governor.policy.min_capability_match == 0.8

    def test_create_governor_with_coordinator(self):
        """Test creating governor with coordinator"""
        mock_coordinator = {"status": "running"}
        governor = IFGovernor(coordinator=mock_coordinator)
        assert governor.coordinator == mock_coordinator


class TestSwarmRegistration:
    """Test swarm registration"""

    def test_register_swarm(self):
        """Test registering a swarm"""
        governor = IFGovernor()
        profile = SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="sonnet"
        )
        governor.register_swarm(profile)

        assert "session-4-sip" in governor.swarm_registry
        assert governor.swarm_registry["session-4-sip"] == profile

    def test_register_multiple_swarms(self):
        """Test registering multiple swarms"""
        governor = IFGovernor()

        profiles = [
            SwarmProfile("session-1", [Capability.INTEGRATION_NDI], 1.5, 0.90, 15.0, "haiku"),
            SwarmProfile("session-2", [Capability.INTEGRATION_WEBRTC], 2.0, 0.92, 12.0, "sonnet"),
            SwarmProfile("session-3", [Capability.INTEGRATION_H323], 1.8, 0.88, 18.0, "haiku"),
        ]

        for profile in profiles:
            governor.register_swarm(profile)

        assert len(governor.swarm_registry) == 3

    def test_unregister_swarm(self):
        """Test unregistering a swarm"""
        governor = IFGovernor()
        profile = SwarmProfile("session-4", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet")
        governor.register_swarm(profile)

        result = governor.unregister_swarm("session-4")
        assert result is True
        assert "session-4" not in governor.swarm_registry

    def test_unregister_unknown_swarm(self):
        """Test unregistering unknown swarm returns False"""
        governor = IFGovernor()
        result = governor.unregister_swarm("unknown-swarm")
        assert result is False


class TestCapabilityMatching:
    """Test capability matching algorithm"""

    @pytest.fixture
    def governor(self):
        """Create governor with standard policy"""
        return IFGovernor(policy=ResourcePolicy(min_capability_match=0.7))

    def test_perfect_capability_match(self, governor):
        """Test 100% capability match returns swarm"""
        governor.register_swarm(SwarmProfile(
            swarm_id="perfect-match",
            capabilities=[Capability.INTEGRATION_SIP, Capability.INTEGRATION_H323],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="sonnet"
        ))

        result = governor.find_qualified_swarm(
            required_capabilities=[Capability.INTEGRATION_SIP, Capability.INTEGRATION_H323],
            max_cost=5.0
        )

        assert result == "perfect-match"

    def test_exact_70_percent_match(self, governor):
        """Test exactly 70% capability match is accepted"""
        governor.register_swarm(SwarmProfile(
            swarm_id="70-percent",
            capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.INTEGRATION_H323,
                Capability.INTEGRATION_WEBRTC,
                Capability.INTEGRATION_NDI,
                Capability.CODE_ANALYSIS_PYTHON,
                Capability.ARCHITECTURE_SECURITY,
                Capability.DOCS_TECHNICAL_WRITING,
            ],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="sonnet"
        ))

        # Require 10 capabilities, swarm has 7 = 70%
        required_caps = [
            Capability.INTEGRATION_SIP,
            Capability.INTEGRATION_H323,
            Capability.INTEGRATION_WEBRTC,
            Capability.INTEGRATION_NDI,
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.ARCHITECTURE_SECURITY,
            Capability.DOCS_TECHNICAL_WRITING,
            Capability.INTEGRATION_RTSP,
            Capability.INTEGRATION_MQTT,
            Capability.INTEGRATION_GRPC,
        ]

        result = governor.find_qualified_swarm(required_caps, max_cost=5.0)
        assert result == "70-percent"

    def test_below_70_percent_rejected(self, governor):
        """Test below 70% capability match is rejected"""
        governor.register_swarm(SwarmProfile(
            swarm_id="low-match",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="sonnet"
        ))

        # Require 3 capabilities, swarm has 1 = 33%
        result = governor.find_qualified_swarm(
            required_capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.INTEGRATION_WEBRTC,
                Capability.INTEGRATION_NDI,
            ],
            max_cost=5.0
        )

        assert result is None

    def test_no_capability_overlap_rejected(self, governor):
        """Test zero capability overlap returns None"""
        governor.register_swarm(SwarmProfile(
            swarm_id="wrong-caps",
            capabilities=[Capability.INTEGRATION_NDI],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="haiku"
        ))

        result = governor.find_qualified_swarm(
            required_capabilities=[Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        assert result is None


class TestCombinedScoring:
    """Test combined scoring (capability × reputation / cost)"""

    @pytest.fixture
    def governor(self):
        """Create governor"""
        return IFGovernor()

    def test_higher_reputation_preferred(self, governor):
        """Test higher reputation swarm wins when capabilities equal"""
        governor.register_swarm(SwarmProfile(
            swarm_id="low-reputation",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.70,
            current_budget_remaining=10.0,
            model="sonnet"
        ))
        governor.register_swarm(SwarmProfile(
            swarm_id="high-reputation",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="sonnet"
        ))

        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        assert result == "high-reputation"

    def test_cheaper_swarm_preferred(self, governor):
        """Test cheaper swarm wins when capabilities and reputation equal"""
        governor.register_swarm(SwarmProfile(
            swarm_id="expensive",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=20.0,
            reputation_score=0.95,
            current_budget_remaining=5.0,
            model="opus"
        ))
        governor.register_swarm(SwarmProfile(
            swarm_id="cheap",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=1.5,
            reputation_score=0.95,
            current_budget_remaining=10.0,
            model="haiku"
        ))

        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=25.0
        )

        assert result == "cheap"

    def test_combined_score_calculation(self, governor):
        """Test combined score is calculated correctly"""
        governor.register_swarm(SwarmProfile(
            swarm_id="test-swarm",
            capabilities=[Capability.INTEGRATION_SIP, Capability.INTEGRATION_H323],
            cost_per_hour=2.0,
            reputation_score=0.90,
            current_budget_remaining=10.0,
            model="sonnet"
        ))

        scores = governor.calculate_match_scores(
            [Capability.INTEGRATION_SIP, Capability.INTEGRATION_H323],
            max_cost=5.0
        )

        assert len(scores) == 1
        score = scores[0]

        # capability_match = 2/2 = 1.0
        # reputation = 0.90
        # cost = 2.0
        # combined = (1.0 * 0.90) / 2.0 = 0.45
        assert score.capability_match == 1.0
        assert score.combined_score == pytest.approx(0.45, rel=0.01)


class TestBudgetEnforcement:
    """Test budget enforcement"""

    @pytest.fixture
    def governor(self):
        """Create governor"""
        return IFGovernor()

    def test_zero_budget_swarm_excluded(self, governor):
        """Test swarm with zero budget is excluded"""
        governor.register_swarm(SwarmProfile(
            swarm_id="broke-swarm",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=0.0,
            model="sonnet"
        ))

        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        assert result is None

    def test_negative_budget_swarm_excluded(self, governor):
        """Test swarm with negative budget is excluded"""
        governor.register_swarm(SwarmProfile(
            swarm_id="over-budget",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=-5.0,
            model="sonnet"
        ))

        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        assert result is None

    def test_cost_limit_enforced(self, governor):
        """Test max_cost limit is enforced"""
        governor.register_swarm(SwarmProfile(
            swarm_id="too-expensive",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=10.0,
            reputation_score=0.95,
            current_budget_remaining=20.0,
            model="opus"
        ))

        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0  # Below swarm cost
        )

        assert result is None


class TestEdgeCases:
    """Test edge cases"""

    @pytest.fixture
    def governor(self):
        """Create governor"""
        return IFGovernor()

    def test_no_swarms_registered(self, governor):
        """Test returns None when no swarms registered"""
        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )
        assert result is None

    def test_empty_required_capabilities(self, governor):
        """Test returns None for empty required capabilities"""
        governor.register_swarm(SwarmProfile(
            "test", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"
        ))

        result = governor.find_qualified_swarm([], max_cost=5.0)
        assert result is None

    def test_multiple_qualified_swarms(self, governor):
        """Test returns highest-scoring when multiple qualify"""
        # Register 3 qualified swarms
        governor.register_swarm(SwarmProfile(
            "swarm-1", [Capability.INTEGRATION_SIP], 2.0, 0.85, 10.0, "sonnet"
        ))
        governor.register_swarm(SwarmProfile(
            "swarm-2", [Capability.INTEGRATION_SIP], 1.5, 0.95, 15.0, "haiku"
        ))
        governor.register_swarm(SwarmProfile(
            "swarm-3", [Capability.INTEGRATION_SIP], 3.0, 0.90, 8.0, "sonnet"
        ))

        result = governor.find_qualified_swarm(
            [Capability.INTEGRATION_SIP],
            max_cost=5.0
        )

        # swarm-2 should win: (1.0 * 0.95) / 1.5 = 0.633
        assert result == "swarm-2"


class TestAssignmentHistory:
    """Test assignment history tracking"""

    def test_assignment_recorded(self):
        """Test assignment is recorded in history"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "session-4", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"
        ))

        governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)

        history = governor.get_assignment_history()
        assert len(history) == 1
        assert history[0]['swarm_id'] == "session-4"

    def test_get_assignment_history_by_swarm(self):
        """Test filtering assignment history by swarm"""
        governor = IFGovernor()
        governor.register_swarm(SwarmProfile(
            "swarm-a", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"
        ))
        governor.register_swarm(SwarmProfile(
            "swarm-b", [Capability.INTEGRATION_NDI], 1.5, 0.90, 15.0, "haiku"
        ))

        governor.find_qualified_swarm([Capability.INTEGRATION_SIP], max_cost=5.0)
        governor.find_qualified_swarm([Capability.INTEGRATION_NDI], max_cost=5.0)

        swarm_a_history = governor.get_assignment_history(swarm_id="swarm-a")
        assert len(swarm_a_history) == 1
        assert swarm_a_history[0]['swarm_id'] == "swarm-a"


class TestGetters:
    """Test getter methods"""

    def test_get_swarm_profile(self):
        """Test getting swarm profile"""
        governor = IFGovernor()
        profile = SwarmProfile(
            "session-4", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"
        )
        governor.register_swarm(profile)

        result = governor.get_swarm_profile("session-4")
        assert result == profile

    def test_get_swarm_profile_not_found(self):
        """Test getting unknown swarm returns None"""
        governor = IFGovernor()
        result = governor.get_swarm_profile("unknown")
        assert result is None

    def test_get_all_swarms(self):
        """Test getting all registered swarms"""
        governor = IFGovernor()
        profiles = [
            SwarmProfile("s1", [Capability.INTEGRATION_SIP], 2.0, 0.95, 10.0, "sonnet"),
            SwarmProfile("s2", [Capability.INTEGRATION_NDI], 1.5, 0.90, 15.0, "haiku"),
        ]

        for profile in profiles:
            governor.register_swarm(profile)

        all_swarms = governor.get_all_swarms()
        assert len(all_swarms) == 2


class TestSession4Integration:
    """Test Session 4 (SIP) integration scenarios"""

    def test_session_4_sip_capability_matching(self):
        """Test Session 4 SIP escalation matches correctly"""
        governor = IFGovernor()

        # Register Session 4 swarm
        governor.register_swarm(SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.INTEGRATION_H323,
                Capability.INTEGRATION_WEBRTC,
                Capability.ARCHITECTURE_SECURITY,
                Capability.CODE_ANALYSIS_PYTHON,
            ],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.44,
            model="sonnet"
        ))

        # SIP escalation task
        result = governor.find_qualified_swarm(
            required_capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.ARCHITECTURE_SECURITY,
            ],
            max_cost=5.0
        )

        assert result == "session-4-sip"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
