"""
Unit Tests for IF.governor - Capability Matching

Tests capability matching algorithm, circuit breaker, and resource policies.
"""

import pytest
from unittest.mock import Mock
from infrafabric.governor import IFGovernor, MatchResult, SwarmStats
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
)


# ==================== Fixtures ====================


@pytest.fixture
def mock_coordinator():
    """Mock IF.coordinator for testing."""
    return Mock()


@pytest.fixture
def default_policy():
    """Default resource policy for testing."""
    return ResourcePolicy(
        max_swarms_per_task=3,
        max_cost_per_task=25.0,
        min_capability_match=0.7,  # 70% threshold
        circuit_breaker_failure_threshold=3
    )


@pytest.fixture
def governor(mock_coordinator, default_policy):
    """IF.governor instance for testing."""
    return IFGovernor(mock_coordinator, default_policy)


@pytest.fixture
def webrtc_swarm():
    """WebRTC swarm profile."""
    return SwarmProfile(
        swarm_id="swarm-webrtc",
        capabilities=[
            Capability.INTEGRATION_WEBRTC,
            Capability.CODE_ANALYSIS_JAVASCRIPT,
            Capability.TESTING_INTEGRATION
        ],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
        model="sonnet"
    )


@pytest.fixture
def sip_swarm():
    """SIP swarm profile."""
    return SwarmProfile(
        swarm_id="swarm-sip",
        capabilities=[
            Capability.INTEGRATION_SIP,
            Capability.CODE_ANALYSIS_GO,
            Capability.TESTING_UNIT
        ],
        cost_per_hour=18.0,
        reputation_score=0.88,
        current_budget_remaining=50.0,
        model="sonnet"
    )


@pytest.fixture
def cli_swarm():
    """CLI swarm profile (cheap Haiku)."""
    return SwarmProfile(
        swarm_id="swarm-cli",
        capabilities=[
            Capability.CLI_DESIGN,
            Capability.CLI_TESTING,
            Capability.DOCS_TECHNICAL_WRITING
        ],
        cost_per_hour=2.0,
        reputation_score=0.90,
        current_budget_remaining=200.0,
        model="haiku"
    )


# ==================== Swarm Registration Tests ====================


def test_register_swarm(governor, webrtc_swarm):
    """Test registering a swarm."""
    governor.register_swarm(webrtc_swarm)
    assert "swarm-webrtc" in governor.swarm_registry
    assert governor.get_swarm_profile("swarm-webrtc") == webrtc_swarm


def test_register_swarm_creates_stats(governor, webrtc_swarm):
    """Test that registering a swarm creates stats."""
    governor.register_swarm(webrtc_swarm)
    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats is not None
    assert stats.swarm_id == "swarm-webrtc"
    assert stats.total_operations == 0


def test_register_swarm_invalid_no_id(governor):
    """Test that creating swarm without ID raises ValueError."""
    # SwarmProfile validation happens in __post_init__, not in register_swarm
    with pytest.raises(ValueError, match="Invalid swarm_id"):
        SwarmProfile(
            swarm_id="",
            capabilities=[Capability.CLI_DESIGN],
            cost_per_hour=1.0
        )


def test_register_swarm_invalid_no_capabilities(governor):
    """Test that creating swarm without capabilities raises ValueError."""
    # SwarmProfile validation happens in __post_init__, not in register_swarm
    with pytest.raises(ValueError, match="at least one capability"):
        SwarmProfile(
            swarm_id="swarm-test",
            capabilities=[],
            cost_per_hour=1.0
        )


def test_unregister_swarm(governor, webrtc_swarm):
    """Test unregistering a swarm."""
    governor.register_swarm(webrtc_swarm)
    governor.unregister_swarm("swarm-webrtc")
    assert "swarm-webrtc" not in governor.swarm_registry


def test_get_all_swarms(governor, webrtc_swarm, sip_swarm):
    """Test getting all registered swarms."""
    governor.register_swarm(webrtc_swarm)
    governor.register_swarm(sip_swarm)
    swarms = governor.get_all_swarms()
    assert len(swarms) == 2
    assert webrtc_swarm in swarms
    assert sip_swarm in swarms


# ==================== Capability Matching Tests ====================


def test_find_qualified_swarm_perfect_match(governor, webrtc_swarm):
    """Test finding swarm with 100% capability match."""
    governor.register_swarm(webrtc_swarm)

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_WEBRTC],
        max_cost=20.0
    )

    assert swarm_id == "swarm-webrtc"


def test_find_qualified_swarm_multiple_capabilities(governor, webrtc_swarm):
    """Test finding swarm with multiple required capabilities."""
    governor.register_swarm(webrtc_swarm)

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[
            Capability.INTEGRATION_WEBRTC,
            Capability.TESTING_INTEGRATION
        ],
        max_cost=20.0
    )

    assert swarm_id == "swarm-webrtc"


def test_find_qualified_swarm_below_threshold(governor, webrtc_swarm):
    """Test that swarm below 70% threshold is rejected."""
    governor.register_swarm(webrtc_swarm)

    # WebRTC swarm has: WEBRTC, JS, TESTING_INTEGRATION (3 capabilities)
    # Required: WEBRTC, SIP, GO (3 capabilities)
    # Match: 1/3 = 33% (below 70% threshold)
    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[
            Capability.INTEGRATION_WEBRTC,
            Capability.INTEGRATION_SIP,  # Not in swarm
            Capability.CODE_ANALYSIS_GO  # Not in swarm
        ],
        max_cost=20.0
    )

    assert swarm_id is None


def test_find_qualified_swarm_no_match(governor, webrtc_swarm):
    """Test that swarm with 0% match is rejected."""
    governor.register_swarm(webrtc_swarm)

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[
            Capability.INTEGRATION_SIP,  # Not in swarm
            Capability.CODE_ANALYSIS_GO  # Not in swarm
        ],
        max_cost=20.0
    )

    assert swarm_id is None


def test_find_qualified_swarm_too_expensive(governor, webrtc_swarm):
    """Test that swarm exceeding max_cost is rejected."""
    governor.register_swarm(webrtc_swarm)

    # WebRTC swarm costs $15/hour
    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_WEBRTC],
        max_cost=10.0  # Below swarm cost
    )

    assert swarm_id is None


def test_find_qualified_swarm_budget_exhausted(governor, webrtc_swarm):
    """Test that swarm with zero budget is rejected."""
    webrtc_swarm.current_budget_remaining = 0.0
    governor.register_swarm(webrtc_swarm)

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_WEBRTC],
        max_cost=20.0
    )

    assert swarm_id is None


def test_find_qualified_swarm_prefers_cheaper(governor, webrtc_swarm, cli_swarm):
    """Test that cheaper swarm is preferred when capabilities and reputation equal."""
    # Make both swarms have same capability and similar reputation
    webrtc_swarm.capabilities = [Capability.CLI_DESIGN]
    webrtc_swarm.reputation_score = 0.90
    webrtc_swarm.cost_per_hour = 15.0

    cli_swarm.reputation_score = 0.90
    cli_swarm.cost_per_hour = 2.0

    governor.register_swarm(webrtc_swarm)
    governor.register_swarm(cli_swarm)

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.CLI_DESIGN],
        max_cost=20.0
    )

    # CLI swarm is cheaper, so should be preferred
    # Combined score: (1.0 × 0.90) / 2.0 = 0.45 (cli)
    # Combined score: (1.0 × 0.90) / 15.0 = 0.06 (webrtc)
    assert swarm_id == "swarm-cli"


def test_find_qualified_swarm_prefers_higher_reputation(governor, webrtc_swarm, sip_swarm):
    """Test that higher reputation swarm is preferred when cost equal."""
    # Make both swarms same cost and capabilities
    webrtc_swarm.capabilities = [Capability.CLI_DESIGN]
    webrtc_swarm.cost_per_hour = 15.0
    webrtc_swarm.reputation_score = 0.95  # Higher reputation

    sip_swarm.capabilities = [Capability.CLI_DESIGN]
    sip_swarm.cost_per_hour = 15.0
    sip_swarm.reputation_score = 0.70  # Lower reputation

    governor.register_swarm(webrtc_swarm)
    governor.register_swarm(sip_swarm)

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.CLI_DESIGN],
        max_cost=20.0
    )

    # WebRTC has higher reputation, so should be preferred
    # Combined score: (1.0 × 0.95) / 15.0 = 0.063 (webrtc)
    # Combined score: (1.0 × 0.70) / 15.0 = 0.047 (sip)
    assert swarm_id == "swarm-webrtc"


def test_find_qualified_swarm_prefers_better_match(governor, webrtc_swarm, cli_swarm):
    """Test that better capability match is preferred."""
    # WebRTC has 3 capabilities, CLI has 3 capabilities
    # Both cost $15/hour, both 0.90 reputation
    webrtc_swarm.cost_per_hour = 15.0
    webrtc_swarm.reputation_score = 0.90

    cli_swarm.cost_per_hour = 15.0
    cli_swarm.reputation_score = 0.90

    governor.register_swarm(webrtc_swarm)
    governor.register_swarm(cli_swarm)

    # Require 2 capabilities: WEBRTC + TESTING_INTEGRATION
    # WebRTC matches both (2/2 = 1.0 match)
    # CLI matches neither (0/2 = 0.0 match, rejected)
    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[
            Capability.INTEGRATION_WEBRTC,
            Capability.TESTING_INTEGRATION
        ],
        max_cost=20.0
    )

    assert swarm_id == "swarm-webrtc"


def test_find_qualified_swarm_no_swarms_registered(governor):
    """Test that None is returned when no swarms registered."""
    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.CLI_DESIGN],
        max_cost=20.0
    )

    assert swarm_id is None


def test_find_qualified_swarm_empty_requirements_raises(governor):
    """Test that empty requirements raises ValueError."""
    with pytest.raises(ValueError, match="required_capabilities cannot be empty"):
        governor.find_qualified_swarm(
            required_capabilities=[],
            max_cost=20.0
        )


def test_find_qualified_swarm_uses_policy_max_cost(governor, webrtc_swarm, default_policy):
    """Test that policy max_cost is used when not specified."""
    governor.register_swarm(webrtc_swarm)

    # Policy max_cost is 25.0, swarm costs 15.0 (should match)
    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_WEBRTC]
        # No max_cost specified, should use policy default (25.0)
    )

    assert swarm_id == "swarm-webrtc"


def test_find_qualified_swarm_circuit_breaker_excludes(governor, webrtc_swarm):
    """Test that swarm with open circuit is excluded."""
    governor.register_swarm(webrtc_swarm)

    # Open circuit breaker
    stats = governor.get_swarm_stats("swarm-webrtc")
    stats.circuit_open = True

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_WEBRTC],
        max_cost=20.0
    )

    assert swarm_id is None


# ==================== find_all_qualified_swarms Tests ====================


def test_find_all_qualified_swarms(governor, webrtc_swarm, sip_swarm, cli_swarm):
    """Test finding all qualified swarms."""
    # Make all swarms have CLI capability
    webrtc_swarm.capabilities = [Capability.CLI_DESIGN]
    webrtc_swarm.cost_per_hour = 15.0

    sip_swarm.capabilities = [Capability.CLI_DESIGN]
    sip_swarm.cost_per_hour = 18.0

    cli_swarm.capabilities = [Capability.CLI_DESIGN]
    cli_swarm.cost_per_hour = 2.0

    governor.register_swarm(webrtc_swarm)
    governor.register_swarm(sip_swarm)
    governor.register_swarm(cli_swarm)

    results = governor.find_all_qualified_swarms(
        required_capabilities=[Capability.CLI_DESIGN],
        max_cost=20.0
    )

    # Should return all 3 swarms, sorted by combined score
    assert len(results) == 3

    # CLI should be first (cheapest, so highest combined score)
    assert results[0].swarm_id == "swarm-cli"


def test_find_all_qualified_swarms_limit(governor, webrtc_swarm, sip_swarm, cli_swarm):
    """Test limiting number of qualified swarms returned."""
    # Make all swarms have CLI capability
    webrtc_swarm.capabilities = [Capability.CLI_DESIGN]
    sip_swarm.capabilities = [Capability.CLI_DESIGN]
    cli_swarm.capabilities = [Capability.CLI_DESIGN]

    governor.register_swarm(webrtc_swarm)
    governor.register_swarm(sip_swarm)
    governor.register_swarm(cli_swarm)

    results = governor.find_all_qualified_swarms(
        required_capabilities=[Capability.CLI_DESIGN],
        max_cost=20.0,
        limit=2  # Only return top 2
    )

    assert len(results) == 2


def test_find_all_qualified_swarms_match_result_fields(governor, webrtc_swarm):
    """Test that MatchResult contains correct fields."""
    governor.register_swarm(webrtc_swarm)

    results = governor.find_all_qualified_swarms(
        required_capabilities=[Capability.INTEGRATION_WEBRTC],
        max_cost=20.0
    )

    assert len(results) == 1
    match = results[0]

    assert match.swarm_id == "swarm-webrtc"
    assert match.match_score == 1.0  # Perfect match
    assert match.reputation_score == 0.95
    assert match.cost_per_hour == 15.0
    assert match.capabilities_matched == 1
    assert match.capabilities_required == 1
    assert match.combined_score > 0


# ==================== Capability Match Calculation Tests ====================


def test_calculate_capability_match_perfect(governor):
    """Test 100% capability match."""
    swarm_caps = [Capability.CLI_DESIGN, Capability.CLI_TESTING]
    required_caps = [Capability.CLI_DESIGN, Capability.CLI_TESTING]

    match = governor._calculate_capability_match(swarm_caps, required_caps)
    assert match == 1.0


def test_calculate_capability_match_partial(governor):
    """Test partial capability match."""
    swarm_caps = [Capability.CLI_DESIGN, Capability.CLI_TESTING, Capability.DOCS_TECHNICAL_WRITING]
    required_caps = [Capability.CLI_DESIGN, Capability.CLI_TESTING]

    # Swarm has all 2 required capabilities (plus 1 extra)
    # Match = 2/2 = 1.0
    match = governor._calculate_capability_match(swarm_caps, required_caps)
    assert match == 1.0


def test_calculate_capability_match_missing_some(governor):
    """Test match when swarm is missing some capabilities."""
    swarm_caps = [Capability.CLI_DESIGN]
    required_caps = [Capability.CLI_DESIGN, Capability.CLI_TESTING, Capability.DOCS_TECHNICAL_WRITING]

    # Swarm has 1 out of 3 required capabilities
    # Match = 1/3 = 0.333...
    match = governor._calculate_capability_match(swarm_caps, required_caps)
    assert abs(match - 0.333) < 0.01


def test_calculate_capability_match_none(governor):
    """Test 0% capability match."""
    swarm_caps = [Capability.CLI_DESIGN]
    required_caps = [Capability.INTEGRATION_SIP, Capability.CODE_ANALYSIS_GO]

    match = governor._calculate_capability_match(swarm_caps, required_caps)
    assert match == 0.0


def test_calculate_capability_match_empty_required(governor):
    """Test that empty requirements gives 1.0 match."""
    swarm_caps = [Capability.CLI_DESIGN]
    required_caps = []

    match = governor._calculate_capability_match(swarm_caps, required_caps)
    assert match == 1.0


# ==================== Circuit Breaker Tests ====================


def test_record_operation_success(governor, webrtc_swarm):
    """Test recording successful operation."""
    governor.register_swarm(webrtc_swarm)
    governor.record_operation_success("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.total_operations == 1
    assert stats.failed_operations == 0
    assert stats.consecutive_failures == 0
    assert stats.circuit_open is False


def test_record_operation_failure(governor, webrtc_swarm):
    """Test recording failed operation."""
    governor.register_swarm(webrtc_swarm)
    governor.record_operation_failure("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.total_operations == 1
    assert stats.failed_operations == 1
    assert stats.consecutive_failures == 1
    assert stats.circuit_open is False  # Below threshold (3)


def test_circuit_breaker_opens_after_threshold(governor, webrtc_swarm, default_policy):
    """Test that circuit opens after consecutive failures exceed threshold."""
    governor.register_swarm(webrtc_swarm)

    # Policy threshold is 3 consecutive failures
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_failure("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.circuit_open is True
    assert stats.circuit_opened_at is not None


def test_circuit_breaker_resets_on_success(governor, webrtc_swarm):
    """Test that circuit breaker resets consecutive failures on success."""
    governor.register_swarm(webrtc_swarm)

    # 2 failures, then success
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_success("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.consecutive_failures == 0
    assert stats.circuit_open is False


def test_circuit_breaker_closes_on_success(governor, webrtc_swarm):
    """Test that circuit closes when successful operation after being open."""
    governor.register_swarm(webrtc_swarm)

    # Open circuit
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_failure("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.circuit_open is True

    # Success closes circuit
    governor.record_operation_success("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.circuit_open is False
    assert stats.circuit_opened_at is None


def test_reset_circuit_breaker_manually(governor, webrtc_swarm):
    """Test manually resetting circuit breaker."""
    governor.register_swarm(webrtc_swarm)

    # Open circuit
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_failure("swarm-webrtc")
    governor.record_operation_failure("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.circuit_open is True

    # Manual reset
    governor.reset_circuit_breaker("swarm-webrtc")

    stats = governor.get_swarm_stats("swarm-webrtc")
    assert stats.circuit_open is False
    assert stats.consecutive_failures == 0
    assert stats.circuit_opened_at is None


# ==================== Edge Cases ====================


def test_multiple_swarms_same_score(governor):
    """Test behavior when multiple swarms have same combined score."""
    swarm1 = SwarmProfile(
        swarm_id="swarm-1",
        capabilities=[Capability.CLI_DESIGN],
        cost_per_hour=10.0,
        reputation_score=0.90,
        current_budget_remaining=100.0
    )

    swarm2 = SwarmProfile(
        swarm_id="swarm-2",
        capabilities=[Capability.CLI_DESIGN],
        cost_per_hour=10.0,
        reputation_score=0.90,
        current_budget_remaining=100.0
    )

    governor.register_swarm(swarm1)
    governor.register_swarm(swarm2)

    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.CLI_DESIGN],
        max_cost=20.0
    )

    # Should return one of them (deterministic based on dict order)
    assert swarm_id in ["swarm-1", "swarm-2"]


def test_swarm_with_extra_capabilities_not_penalized(governor):
    """Test that swarm with extra capabilities is not penalized in matching."""
    swarm = SwarmProfile(
        swarm_id="swarm-multi",
        capabilities=[
            Capability.CLI_DESIGN,
            Capability.CLI_TESTING,
            Capability.CLI_UX,
            Capability.DOCS_TECHNICAL_WRITING,
            Capability.DOCS_API_DESIGN
        ],
        cost_per_hour=10.0,
        reputation_score=0.90,
        current_budget_remaining=100.0
    )

    governor.register_swarm(swarm)

    # Only require 1 capability
    swarm_id = governor.find_qualified_swarm(
        required_capabilities=[Capability.CLI_DESIGN],
        max_cost=20.0
    )

    # Should match perfectly (1/1 = 1.0) despite having 4 extra capabilities
    assert swarm_id == "swarm-multi"
