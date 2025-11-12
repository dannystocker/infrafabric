"""Unit tests for IF.governor budget tracking (P0.2.3)

Tests budget tracking and enforcement functionality:
- Budget deduction
- Zero/negative budget prevention
- IF.optimise integration
- Budget reports
- Witness logging
- Circuit breaker on budget exhaustion
"""

import pytest
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import (
    SwarmProfile,
    ResourcePolicy,
    Capability,
)
from infrafabric import witness, optimise


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test"""
    witness.clear_operations()
    optimise.clear_cost_records()
    yield
    witness.clear_operations()
    optimise.clear_cost_records()


@pytest.fixture
def governor():
    """Create IF.governor instance"""
    policy = ResourcePolicy(
        max_cost_per_task=10.0,
        min_capability_match=0.7,
        enable_cost_tracking=True,
        enable_witness_logging=True,
    )
    return IFGovernor(coordinator=None, policy=policy)


@pytest.fixture
def sample_profile():
    """Create sample swarm profile"""
    return SwarmProfile(
        swarm_id='session-7-test',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON, Capability.INFRA_DISTRIBUTED_SYSTEMS],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
        model='sonnet',
    )


def test_register_swarm(governor, sample_profile):
    """Test swarm registration"""
    governor.register_swarm(sample_profile)

    assert 'session-7-test' in governor.swarm_registry
    assert governor.swarm_registry['session-7-test'].swarm_id == 'session-7-test'
    assert governor.swarm_registry['session-7-test'].current_budget_remaining == 100.0

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='swarm_registered')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7-test'


def test_track_cost_basic(governor, sample_profile):
    """Test basic cost tracking"""
    governor.register_swarm(sample_profile)

    # Track cost
    governor.track_cost('session-7-test', 'code-review', 5.0)

    # Check budget deduction
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == 95.0

    # Check IF.optimise integration
    total_cost = optimise.get_total_cost(provider='session-7-test')
    assert total_cost == 5.0

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='cost_tracked')
    assert len(ops) == 1
    assert ops[0].params['cost'] == 5.0
    assert ops[0].params['remaining_budget'] == 95.0


def test_track_cost_multiple_operations(governor, sample_profile):
    """Test tracking multiple costs"""
    governor.register_swarm(sample_profile)

    # Track multiple costs
    governor.track_cost('session-7-test', 'code-review', 10.0)
    governor.track_cost('session-7-test', 'testing', 15.0)
    governor.track_cost('session-7-test', 'deployment', 20.0)

    # Check total deduction
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == 55.0  # 100 - 10 - 15 - 20

    # Check IF.optimise total
    total_cost = optimise.get_total_cost(provider='session-7-test')
    assert total_cost == 45.0


def test_budget_exhaustion_trips_circuit_breaker(governor, sample_profile):
    """Test that budget exhaustion trips circuit breaker"""
    governor.register_swarm(sample_profile)

    # Exhaust budget
    governor.track_cost('session-7-test', 'expensive-operation', 100.0)

    # Check budget is 0
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == 0.0

    # Check circuit breaker tripped
    assert governor._circuit_breakers['session-7-test'] == True

    # Check witness logging
    ops = witness.get_operations(component='IF.governor', operation='circuit_breaker_tripped')
    assert len(ops) == 1
    assert ops[0].params['reason'] == 'budget_exhausted'


def test_budget_over_exhaustion(governor, sample_profile):
    """Test tracking cost that exceeds remaining budget"""
    governor.register_swarm(sample_profile)

    # Spend more than budget
    governor.track_cost('session-7-test', 'over-budget-operation', 150.0)

    # Check budget is negative
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == -50.0

    # Circuit breaker should be tripped
    assert governor._circuit_breakers['session-7-test'] == True


def test_is_swarm_available_with_budget(governor, sample_profile):
    """Test swarm availability check with budget"""
    governor.register_swarm(sample_profile)

    # Initially available
    assert governor.is_swarm_available('session-7-test') == True

    # Exhaust budget
    governor.track_cost('session-7-test', 'operation', 100.0)

    # No longer available
    assert governor.is_swarm_available('session-7-test') == False


def test_get_budget_report_single_swarm(governor, sample_profile):
    """Test budget report for single swarm"""
    governor.register_swarm(sample_profile)

    # Track some costs
    governor.track_cost('session-7-test', 'operation-1', 10.0)
    governor.track_cost('session-7-test', 'operation-2', 5.0)

    # Get report
    report = governor.get_budget_report('session-7-test')

    assert 'session-7-test' in report
    assert report['session-7-test']['remaining'] == 85.0
    assert report['session-7-test']['spent'] == 15.0
    assert report['session-7-test']['cost_per_hour'] == 15.0
    assert report['session-7-test']['circuit_breaker'] == False


def test_get_budget_report_all_swarms(governor):
    """Test budget report for all swarms"""
    # Register multiple swarms
    profile1 = SwarmProfile(
        swarm_id='session-1',
        capabilities=[Capability.INTEGRATION_NDI],
        cost_per_hour=2.0,
        current_budget_remaining=50.0,
        model='haiku',
    )
    profile2 = SwarmProfile(
        swarm_id='session-7',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=100.0,
        model='sonnet',
    )

    governor.register_swarm(profile1)
    governor.register_swarm(profile2)

    # Track costs
    governor.track_cost('session-1', 'doc-update', 2.0)
    governor.track_cost('session-7', 'code-review', 10.0)

    # Get report for all swarms
    report = governor.get_budget_report()

    assert len(report) == 2
    assert 'session-1' in report
    assert 'session-7' in report
    assert report['session-1']['remaining'] == 48.0
    assert report['session-7']['remaining'] == 90.0


def test_track_cost_with_metadata(governor, sample_profile):
    """Test cost tracking with metadata"""
    governor.register_swarm(sample_profile)

    metadata = {
        'task_id': 'P0.2.3',
        'duration_seconds': 120,
        'lines_of_code': 500,
    }

    governor.track_cost('session-7-test', 'code-review', 5.0, metadata=metadata)

    # Check metadata in witness log
    ops = witness.get_operations(component='IF.governor', operation='cost_tracked')
    assert len(ops) == 1
    assert ops[0].params['metadata'] == metadata


def test_track_cost_unknown_swarm(governor):
    """Test tracking cost for unknown swarm raises error"""
    with pytest.raises(ValueError, match="Unknown swarm"):
        governor.track_cost('unknown-swarm', 'operation', 10.0)


def test_reset_circuit_breaker(governor, sample_profile):
    """Test manual circuit breaker reset"""
    governor.register_swarm(sample_profile)

    # Trip circuit breaker
    governor.track_cost('session-7-test', 'operation', 100.0)
    assert governor._circuit_breakers['session-7-test'] == True

    # Reset with new budget
    governor.reset_circuit_breaker('session-7-test', new_budget=50.0)

    # Check circuit breaker cleared
    assert governor._circuit_breakers['session-7-test'] == False

    # Check new budget
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == 50.0

    # Check swarm is available again
    assert governor.is_swarm_available('session-7-test') == True


def test_cost_tracking_integration_with_optimise(governor, sample_profile):
    """Test IF.optimise integration"""
    governor.register_swarm(sample_profile)

    # Track various costs
    governor.track_cost('session-7-test', 'code-review', 5.0)
    governor.track_cost('session-7-test', 'code-review', 3.0)
    governor.track_cost('session-7-test', 'testing', 7.0)

    # Get cost report from IF.optimise
    report = optimise.get_cost_report(provider='session-7-test')

    assert report['total_cost'] == 15.0
    assert report['total_operations'] == 3
    assert report['operation_counts']['code-review'] == 2
    assert report['operation_counts']['testing'] == 1
    assert report['operation_costs']['code-review'] == 8.0
    assert report['operation_costs']['testing'] == 7.0


def test_witness_logging_disabled(sample_profile):
    """Test with witness logging disabled"""
    policy = ResourcePolicy(enable_witness_logging=False)
    governor = IFGovernor(coordinator=None, policy=policy)

    governor.register_swarm(sample_profile)
    governor.track_cost('session-7-test', 'operation', 5.0)

    # No witness operations should be logged
    ops = witness.get_operations(component='IF.governor', operation='cost_tracked')
    assert len(ops) == 0


def test_cost_tracking_disabled(sample_profile):
    """Test with cost tracking disabled"""
    policy = ResourcePolicy(enable_cost_tracking=False, enable_witness_logging=False)
    governor = IFGovernor(coordinator=None, policy=policy)

    governor.register_swarm(sample_profile)
    governor.track_cost('session-7-test', 'operation', 5.0)

    # Budget should still be deducted
    profile = governor.swarm_registry['session-7-test']
    assert profile.current_budget_remaining == 95.0

    # But no cost records in IF.optimise
    total_cost = optimise.get_total_cost(provider='session-7-test')
    assert total_cost == 0.0


def test_get_swarm_stats(governor, sample_profile):
    """Test getting swarm statistics"""
    governor.register_swarm(sample_profile)
    governor.track_cost('session-7-test', 'operation', 10.0)

    stats = governor.get_swarm_stats('session-7-test')

    assert stats['swarm_id'] == 'session-7-test'
    assert stats['budget_remaining'] == 90.0
    assert stats['budget_spent'] == 10.0
    assert stats['cost_per_hour'] == 15.0
    assert stats['reputation'] == 0.95
    assert stats['circuit_breaker'] == False
    assert stats['available'] == True
    assert stats['model'] == 'sonnet'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
