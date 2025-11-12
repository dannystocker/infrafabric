"""Performance benchmarks for IF.governor

This module benchmarks the performance of IF.governor operations:
- P0.2.2: Capability matching (find_qualified_swarm)
- P0.2.3: Budget tracking (track_cost)
- P0.2.4: Circuit breaker overhead

Target metrics:
- Capability matching: <5ms per lookup
- Budget tracking: <1ms per operation
- Circuit breaker: <1ms overhead

Run with: python -m pytest tests/test_governor_benchmarks.py -v
"""

import pytest
import time
from typing import List
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
def governor_with_many_swarms():
    """Create governor with many swarms for realistic benchmarking"""
    policy = ResourcePolicy(min_capability_match=0.7)
    governor = IFGovernor(coordinator=None, policy=policy)

    # Register 50 swarms with various capabilities
    capabilities_pool = [
        [Capability.CODE_ANALYSIS_PYTHON, Capability.INFRA_DISTRIBUTED_SYSTEMS],
        [Capability.CODE_ANALYSIS_RUST, Capability.ARCHITECTURE_SECURITY],
        [Capability.INTEGRATION_SIP, Capability.TESTING_INTEGRATION],
        [Capability.INTEGRATION_NDI, Capability.DOCS_TECHNICAL_WRITING],
        [Capability.CODE_ANALYSIS_JAVASCRIPT, Capability.CLI_DESIGN],
        [Capability.INFRA_CLOUD, Capability.ARCHITECTURE_PERFORMANCE],
        [Capability.CODE_ANALYSIS_GO, Capability.TESTING_UNIT],
        [Capability.INTEGRATION_WEBRTC, Capability.ARCHITECTURE_PATTERNS],
    ]

    for i in range(50):
        profile = SwarmProfile(
            swarm_id=f'swarm-{i}',
            capabilities=capabilities_pool[i % len(capabilities_pool)],
            cost_per_hour=2.0 + (i % 20),
            reputation_score=0.80 + (i % 20) / 100.0,
            current_budget_remaining=100.0,
        )
        governor.register_swarm(profile)

    return governor


# ========== Capability Matching Benchmarks (P0.2.2) ==========

def test_benchmark_capability_matching_single_lookup(governor_with_many_swarms):
    """Benchmark single capability matching lookup

    Target: <5ms per lookup
    """
    governor = governor_with_many_swarms

    required_caps = [Capability.CODE_ANALYSIS_PYTHON]

    # Warm-up
    governor.find_qualified_swarm(required_caps, max_cost=50.0)

    # Benchmark
    start = time.perf_counter()
    result = governor.find_qualified_swarm(required_caps, max_cost=50.0)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert result is not None
    assert elapsed_ms < 5.0, f"Single lookup took {elapsed_ms:.2f}ms (target: <5ms)"

    print(f"\n✅ Single capability lookup: {elapsed_ms:.2f}ms")


def test_benchmark_capability_matching_100_lookups(governor_with_many_swarms):
    """Benchmark 100 capability matching lookups

    Target: <5ms average per lookup
    """
    governor = governor_with_many_swarms

    required_caps = [Capability.CODE_ANALYSIS_PYTHON, Capability.INFRA_DISTRIBUTED_SYSTEMS]

    # Benchmark
    start = time.perf_counter()
    for _ in range(100):
        governor.find_qualified_swarm(required_caps, max_cost=50.0)
    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 100

    assert avg_ms < 5.0, f"Average lookup took {avg_ms:.2f}ms (target: <5ms)"

    print(f"\n✅ 100 capability lookups: {elapsed_ms:.2f}ms total, {avg_ms:.2f}ms average")


def test_benchmark_capability_matching_with_filtering(governor_with_many_swarms):
    """Benchmark capability matching with budget/cost filtering

    Target: <5ms per lookup even with filtering
    """
    governor = governor_with_many_swarms

    # Exhaust budgets of some swarms
    for i in range(0, 25):
        governor.track_cost(f'swarm-{i}', 'test', 100.0)

    required_caps = [Capability.CODE_ANALYSIS_PYTHON]

    # Benchmark
    start = time.perf_counter()
    result = governor.find_qualified_swarm(required_caps, max_cost=50.0)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 5.0, f"Filtered lookup took {elapsed_ms:.2f}ms (target: <5ms)"

    print(f"\n✅ Filtered capability lookup: {elapsed_ms:.2f}ms")


# ========== Budget Tracking Benchmarks (P0.2.3) ==========

def test_benchmark_budget_tracking_single_operation():
    """Benchmark single budget tracking operation

    Target: <1ms per operation
    """
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    profile = SwarmProfile(
        swarm_id='test-swarm',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=1000.0,
    )
    governor.register_swarm(profile)

    # Warm-up
    governor.track_cost('test-swarm', 'test', 1.0)

    # Benchmark
    start = time.perf_counter()
    governor.track_cost('test-swarm', 'operation', 0.5)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 1.0, f"Budget tracking took {elapsed_ms:.2f}ms (target: <1ms)"

    print(f"\n✅ Single budget tracking: {elapsed_ms:.3f}ms")


def test_benchmark_budget_tracking_1000_operations():
    """Benchmark 1000 budget tracking operations

    Target: <1ms average per operation
    """
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    profile = SwarmProfile(
        swarm_id='test-swarm',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=10000.0,
    )
    governor.register_swarm(profile)

    # Benchmark
    start = time.perf_counter()
    for i in range(1000):
        governor.track_cost('test-swarm', f'operation-{i}', 0.1)
    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 1000

    assert avg_ms < 1.0, f"Average budget tracking took {avg_ms:.3f}ms (target: <1ms)"

    print(f"\n✅ 1000 budget tracking operations: {elapsed_ms:.2f}ms total, {avg_ms:.3f}ms average")


def test_benchmark_budget_report_generation(governor_with_many_swarms):
    """Benchmark budget report generation

    Target: <10ms for 50 swarms
    """
    governor = governor_with_many_swarms

    # Track some costs
    for i in range(25):
        governor.track_cost(f'swarm-{i}', 'test', 5.0)

    # Benchmark
    start = time.perf_counter()
    report = governor.get_budget_report()
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert len(report) == 50
    assert elapsed_ms < 10.0, f"Budget report took {elapsed_ms:.2f}ms (target: <10ms)"

    print(f"\n✅ Budget report (50 swarms): {elapsed_ms:.2f}ms")


# ========== Circuit Breaker Benchmarks (P0.2.4) ==========

def test_benchmark_circuit_breaker_check_overhead():
    """Benchmark circuit breaker check overhead

    Target: <0.1ms overhead per check
    """
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    profile = SwarmProfile(
        swarm_id='test-swarm',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Benchmark
    start = time.perf_counter()
    for _ in range(1000):
        governor.is_swarm_available('test-swarm')
    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 1000

    assert avg_ms < 0.1, f"Average availability check took {avg_ms:.3f}ms (target: <0.1ms)"

    print(f"\n✅ 1000 availability checks: {elapsed_ms:.2f}ms total, {avg_ms:.3f}ms average")


def test_benchmark_failure_tracking():
    """Benchmark failure tracking performance

    Target: <1ms per failure record
    """
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy(circuit_breaker_failure_threshold=1000))

    profile = SwarmProfile(
        swarm_id='test-swarm',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Benchmark
    start = time.perf_counter()
    for i in range(100):
        governor.record_task_failure('test-swarm', f'task-{i}', 'error')
    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 100

    assert avg_ms < 1.0, f"Average failure tracking took {avg_ms:.3f}ms (target: <1ms)"

    print(f"\n✅ 100 failure records: {elapsed_ms:.2f}ms total, {avg_ms:.3f}ms average")


def test_benchmark_success_tracking():
    """Benchmark success tracking performance

    Target: <1ms per success record
    """
    governor = IFGovernor(coordinator=None, policy=ResourcePolicy())

    profile = SwarmProfile(
        swarm_id='test-swarm',
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=15.0,
        current_budget_remaining=100.0,
    )
    governor.register_swarm(profile)

    # Benchmark
    start = time.perf_counter()
    for i in range(100):
        governor.record_task_success('test-swarm', f'task-{i}', 60.0)
    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 100

    assert avg_ms < 1.0, f"Average success tracking took {avg_ms:.3f}ms (target: <1ms)"

    print(f"\n✅ 100 success records: {elapsed_ms:.2f}ms total, {avg_ms:.3f}ms average")


# ========== Combined Operations Benchmarks ==========

def test_benchmark_realistic_workflow(governor_with_many_swarms):
    """Benchmark realistic governor workflow

    Workflow:
    1. Find qualified swarm
    2. Track cost
    3. Record success/failure
    4. Check availability

    Target: <10ms for complete workflow
    """
    governor = governor_with_many_swarms

    required_caps = [Capability.CODE_ANALYSIS_PYTHON]

    # Benchmark
    start = time.perf_counter()

    # Find swarm
    swarm_id = governor.find_qualified_swarm(required_caps, max_cost=50.0)
    assert swarm_id is not None

    # Track cost
    governor.track_cost(swarm_id, 'code-review', 2.5)

    # Record success
    governor.record_task_success(swarm_id, 'task-123', 45.0)

    # Check availability
    available = governor.is_swarm_available(swarm_id)
    assert available == True

    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 10.0, f"Realistic workflow took {elapsed_ms:.2f}ms (target: <10ms)"

    print(f"\n✅ Complete workflow (find + track + record + check): {elapsed_ms:.2f}ms")


def test_benchmark_concurrent_swarm_operations(governor_with_many_swarms):
    """Benchmark operations across multiple swarms

    Target: Linear scaling (no lock contention)
    """
    governor = governor_with_many_swarms

    # Benchmark: Operate on 20 swarms
    start = time.perf_counter()

    for i in range(20):
        swarm_id = f'swarm-{i}'
        governor.track_cost(swarm_id, 'operation', 1.0)
        governor.record_task_success(swarm_id, f'task-{i}', 30.0)

    elapsed_ms = (time.perf_counter() - start) * 1000

    avg_ms = elapsed_ms / 20

    assert avg_ms < 2.0, f"Average per-swarm operation took {avg_ms:.3f}ms (target: <2ms)"

    print(f"\n✅ 20 concurrent swarm operations: {elapsed_ms:.2f}ms total, {avg_ms:.3f}ms average")


# ========== Performance Summary ==========

def test_performance_summary(governor_with_many_swarms):
    """Generate performance summary report"""
    print("\n" + "="*60)
    print("IF.GOVERNOR PERFORMANCE SUMMARY")
    print("="*60)

    governor = governor_with_many_swarms

    # Capability matching
    start = time.perf_counter()
    for _ in range(100):
        governor.find_qualified_swarm([Capability.CODE_ANALYSIS_PYTHON], max_cost=50.0)
    matching_avg = ((time.perf_counter() - start) * 1000) / 100

    # Budget tracking
    governor.track_cost('swarm-0', 'test', 10.0)
    start = time.perf_counter()
    for i in range(100):
        governor.track_cost('swarm-0', f'op-{i}', 0.1)
    budget_avg = ((time.perf_counter() - start) * 1000) / 100

    # Availability check
    start = time.perf_counter()
    for _ in range(100):
        governor.is_swarm_available('swarm-0')
    availability_avg = ((time.perf_counter() - start) * 1000) / 100

    print(f"\n📊 Average Performance (100 operations each):")
    print(f"  • Capability matching:  {matching_avg:.3f}ms  (target: <5ms)")
    print(f"  • Budget tracking:      {budget_avg:.3f}ms  (target: <1ms)")
    print(f"  • Availability check:   {availability_avg:.3f}ms  (target: <0.1ms)")

    print(f"\n🎯 Performance Targets:")
    print(f"  • Capability matching:  {'✅ PASS' if matching_avg < 5.0 else '❌ FAIL'}")
    print(f"  • Budget tracking:      {'✅ PASS' if budget_avg < 1.0 else '❌ FAIL'}")
    print(f"  • Availability check:   {'✅ PASS' if availability_avg < 0.1 else '❌ FAIL'}")

    print(f"\n💡 Throughput Estimates (ops/sec):")
    print(f"  • Capability matching:  {1000/matching_avg:.0f} ops/sec")
    print(f"  • Budget tracking:      {1000/budget_avg:.0f} ops/sec")
    print(f"  • Availability check:   {1000/availability_avg:.0f} ops/sec")

    print("="*60)

    # All should pass targets
    assert matching_avg < 5.0
    assert budget_avg < 1.0
    assert availability_avg < 0.1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
