"""IF.coordinator Performance Benchmarks (F7.10)

Comprehensive benchmark suite for measuring IF.coordinator performance:
- Task claiming throughput (ops/second)
- Task broadcast latency (p50, p95, p99)
- Multi-swarm coordination stress test
- Performance regression detection
- Results visualization with charts

Part of Phase 0 Filler Tasks - Session 7
"""

import asyncio
import time
import statistics
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

from infrafabric.coordinator import IFCoordinator
from infrafabric.event_bus import EventBus
from infrafabric.schemas.capability import Capability


@dataclass
class BenchmarkResult:
    """Result from a single benchmark run"""
    name: str
    duration_seconds: float
    operations: int
    throughput_ops_per_sec: float
    latencies_ms: List[float]
    p50_ms: float
    p95_ms: float
    p99_ms: float
    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding full latency list)"""
        d = asdict(self)
        d['latencies_ms'] = f"{len(self.latencies_ms)} samples"
        return d


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results"""
    timestamp: float
    results: List[BenchmarkResult]
    baseline: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'results': [r.to_dict() for r in self.results],
            'baseline': self.baseline
        }


def calculate_percentiles(latencies: List[float]) -> Dict[str, float]:
    """Calculate percentiles from latency list"""
    if not latencies:
        return {'p50': 0, 'p95': 0, 'p99': 0, 'min': 0, 'max': 0, 'mean': 0, 'median': 0}

    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)

    return {
        'p50': sorted_latencies[int(n * 0.50)],
        'p95': sorted_latencies[int(n * 0.95)],
        'p99': sorted_latencies[int(n * 0.99)],
        'min': sorted_latencies[0],
        'max': sorted_latencies[-1],
        'mean': statistics.mean(sorted_latencies),
        'median': statistics.median(sorted_latencies),
    }


async def benchmark_task_claiming_throughput(
    num_tasks: int = 1000,
    num_swarms: int = 10
) -> BenchmarkResult:
    """Benchmark task claiming throughput

    Measures how many task claims can be processed per second
    when multiple swarms are competing for tasks.

    Args:
        num_tasks: Number of tasks to create
        num_swarms: Number of swarms competing for tasks

    Returns:
        BenchmarkResult with throughput metrics
    """
    print(f"\n📊 Benchmark: Task Claiming Throughput ({num_tasks} tasks, {num_swarms} swarms)")

    # Setup
    event_bus = EventBus()
    coordinator = IFCoordinator(event_bus=event_bus)
    await coordinator.connect()

    # Create tasks
    print(f"   Creating {num_tasks} tasks...")
    for i in range(num_tasks):
        await coordinator.create_task(
            f'task-{i}',
            [Capability.CODE_ANALYSIS_PYTHON],
            priority=i % 10
        )

    # Claim tasks from multiple swarms
    print(f"   Claiming tasks from {num_swarms} swarms...")
    latencies = []

    start_time = time.perf_counter()

    task_index = 0
    for swarm_id in range(num_swarms):
        swarm_name = f'swarm-{swarm_id}'

        # Each swarm claims tasks until no more available
        while task_index < num_tasks:
            task_id = f'task-{task_index}'
            task_index += 1

            claim_start = time.perf_counter()
            success = await coordinator.claim_task(swarm_name, task_id)
            claim_duration = (time.perf_counter() - claim_start) * 1000  # ms

            if success:
                latencies.append(claim_duration)
                break  # Move to next swarm
            # If claim failed, task already claimed, move to next task

    end_time = time.perf_counter()
    duration = end_time - start_time

    # Calculate metrics
    successful_claims = len(latencies)
    throughput = successful_claims / duration if duration > 0 else 0
    percentiles = calculate_percentiles(latencies)

    await coordinator.disconnect()

    print(f"   ✅ Claimed {successful_claims} tasks in {duration:.3f}s")
    print(f"   ⚡ Throughput: {throughput:.0f} claims/second")
    print(f"   📈 Latency: p50={percentiles['p50']:.3f}ms, p95={percentiles['p95']:.3f}ms, p99={percentiles['p99']:.3f}ms")

    return BenchmarkResult(
        name='task_claiming_throughput',
        duration_seconds=duration,
        operations=successful_claims,
        throughput_ops_per_sec=throughput,
        latencies_ms=latencies,
        p50_ms=percentiles['p50'],
        p95_ms=percentiles['p95'],
        p99_ms=percentiles['p99'],
        min_ms=percentiles['min'],
        max_ms=percentiles['max'],
        mean_ms=percentiles['mean'],
        median_ms=percentiles['median'],
    )


async def benchmark_broadcast_latency(
    num_broadcasts: int = 1000,
    num_swarms: int = 20
) -> BenchmarkResult:
    """Benchmark task broadcast latency

    Measures latency of direct task push notifications to swarms.

    Args:
        num_broadcasts: Number of push operations to measure
        num_swarms: Number of swarms to register

    Returns:
        BenchmarkResult with latency percentiles
    """
    print(f"\n📊 Benchmark: Broadcast Latency ({num_broadcasts} broadcasts, {num_swarms} swarms)")

    # Setup
    event_bus = EventBus()
    coordinator = IFCoordinator(event_bus=event_bus)
    await coordinator.connect()

    # Register swarms
    print(f"   Registering {num_swarms} swarms...")
    for i in range(num_swarms):
        await coordinator.register_swarm(
            f'swarm-{i}',
            [Capability.CODE_ANALYSIS_PYTHON]
        )

    # Create tasks
    print(f"   Creating {num_broadcasts} tasks...")
    for i in range(num_broadcasts):
        await coordinator.create_task(
            f'task-{i}',
            [Capability.CODE_ANALYSIS_PYTHON]
        )

    # Measure push latency
    print(f"   Measuring push latency...")
    latencies = []

    start_time = time.perf_counter()

    for i in range(num_broadcasts):
        swarm_id = f'swarm-{i % num_swarms}'
        task_id = f'task-{i}'

        push_start = time.perf_counter()
        await coordinator.push_task_to_swarm(swarm_id, task_id)
        push_duration = (time.perf_counter() - push_start) * 1000  # ms

        latencies.append(push_duration)

    end_time = time.perf_counter()
    duration = end_time - start_time

    # Calculate metrics
    throughput = num_broadcasts / duration if duration > 0 else 0
    percentiles = calculate_percentiles(latencies)

    await coordinator.disconnect()

    print(f"   ✅ Pushed {num_broadcasts} tasks in {duration:.3f}s")
    print(f"   ⚡ Throughput: {throughput:.0f} pushes/second")
    print(f"   📈 Latency: p50={percentiles['p50']:.3f}ms, p95={percentiles['p95']:.3f}ms, p99={percentiles['p99']:.3f}ms")

    return BenchmarkResult(
        name='broadcast_latency',
        duration_seconds=duration,
        operations=num_broadcasts,
        throughput_ops_per_sec=throughput,
        latencies_ms=latencies,
        p50_ms=percentiles['p50'],
        p95_ms=percentiles['p95'],
        p99_ms=percentiles['p99'],
        min_ms=percentiles['min'],
        max_ms=percentiles['max'],
        mean_ms=percentiles['mean'],
        median_ms=percentiles['median'],
    )


async def benchmark_multi_swarm_coordination(
    num_swarms: int = 50,
    num_tasks: int = 500,
    concurrent_operations: int = 10
) -> BenchmarkResult:
    """Benchmark multi-swarm coordination stress test

    Simulates realistic scenario with many swarms concurrently:
    - Registering
    - Receiving task broadcasts
    - Claiming tasks
    - Completing tasks

    Args:
        num_swarms: Number of swarms to coordinate
        num_tasks: Number of tasks to distribute
        concurrent_operations: Concurrent operations per phase

    Returns:
        BenchmarkResult with overall coordination metrics
    """
    print(f"\n📊 Benchmark: Multi-Swarm Coordination ({num_swarms} swarms, {num_tasks} tasks)")

    # Setup
    event_bus = EventBus()
    coordinator = IFCoordinator(event_bus=event_bus)
    await coordinator.connect()

    latencies = []
    total_operations = 0

    # Phase 1: Concurrent swarm registration
    print(f"   Phase 1: Registering {num_swarms} swarms (batches of {concurrent_operations})...")
    phase_start = time.perf_counter()

    for batch_start in range(0, num_swarms, concurrent_operations):
        batch_end = min(batch_start + concurrent_operations, num_swarms)
        register_tasks = [
            coordinator.register_swarm(
                f'swarm-{i}',
                [Capability.CODE_ANALYSIS_PYTHON, Capability.TESTING_UNIT]
            )
            for i in range(batch_start, batch_end)
        ]

        batch_time_start = time.perf_counter()
        await asyncio.gather(*register_tasks)
        batch_duration = (time.perf_counter() - batch_time_start) * 1000
        latencies.append(batch_duration)
        total_operations += len(register_tasks)

    print(f"      ✓ Registered {num_swarms} swarms in {time.perf_counter() - phase_start:.3f}s")

    # Phase 2: Create tasks
    print(f"   Phase 2: Creating {num_tasks} tasks...")
    phase_start = time.perf_counter()

    for i in range(num_tasks):
        create_start = time.perf_counter()
        await coordinator.create_task(
            f'task-{i}',
            [Capability.CODE_ANALYSIS_PYTHON],
            priority=i % 10
        )
        create_duration = (time.perf_counter() - create_start) * 1000
        latencies.append(create_duration)
        total_operations += 1

    print(f"      ✓ Created {num_tasks} tasks in {time.perf_counter() - phase_start:.3f}s")

    # Phase 3: Concurrent task claiming
    print(f"   Phase 3: Claiming tasks (batches of {concurrent_operations})...")
    phase_start = time.perf_counter()

    task_index = 0
    while task_index < num_tasks:
        batch_size = min(concurrent_operations, num_tasks - task_index)
        claim_tasks = []

        for i in range(batch_size):
            swarm_id = f'swarm-{(task_index + i) % num_swarms}'
            task_id = f'task-{task_index + i}'
            claim_tasks.append(coordinator.claim_task(swarm_id, task_id))

        batch_time_start = time.perf_counter()
        results = await asyncio.gather(*claim_tasks)
        batch_duration = (time.perf_counter() - batch_time_start) * 1000
        latencies.append(batch_duration)

        total_operations += len(claim_tasks)
        task_index += batch_size

    print(f"      ✓ Claimed {num_tasks} tasks in {time.perf_counter() - phase_start:.3f}s")

    # Phase 4: Concurrent task completion
    print(f"   Phase 4: Completing tasks (batches of {concurrent_operations})...")
    phase_start = time.perf_counter()

    task_index = 0
    while task_index < num_tasks:
        batch_size = min(concurrent_operations, num_tasks - task_index)
        complete_tasks = []

        for i in range(batch_size):
            swarm_id = f'swarm-{(task_index + i) % num_swarms}'
            task_id = f'task-{task_index + i}'
            complete_tasks.append(
                coordinator.complete_task(swarm_id, task_id, result={'status': 'success'})
            )

        batch_time_start = time.perf_counter()
        await asyncio.gather(*complete_tasks)
        batch_duration = (time.perf_counter() - batch_time_start) * 1000
        latencies.append(batch_duration)

        total_operations += len(complete_tasks)
        task_index += batch_size

    print(f"      ✓ Completed {num_tasks} tasks in {time.perf_counter() - phase_start:.3f}s")

    # Calculate overall metrics
    duration = sum(latencies) / 1000  # Convert to seconds
    throughput = total_operations / duration if duration > 0 else 0
    percentiles = calculate_percentiles(latencies)

    await coordinator.disconnect()

    print(f"   ✅ Coordinated {num_swarms} swarms across {total_operations} operations")
    print(f"   ⚡ Throughput: {throughput:.0f} ops/second")
    print(f"   📈 Batch Latency: p50={percentiles['p50']:.3f}ms, p95={percentiles['p95']:.3f}ms, p99={percentiles['p99']:.3f}ms")

    return BenchmarkResult(
        name='multi_swarm_coordination',
        duration_seconds=duration,
        operations=total_operations,
        throughput_ops_per_sec=throughput,
        latencies_ms=latencies,
        p50_ms=percentiles['p50'],
        p95_ms=percentiles['p95'],
        p99_ms=percentiles['p99'],
        min_ms=percentiles['min'],
        max_ms=percentiles['max'],
        mean_ms=percentiles['mean'],
        median_ms=percentiles['median'],
    )


async def benchmark_blocker_escalation_throughput(
    num_blockers: int = 1000
) -> BenchmarkResult:
    """Benchmark blocker escalation throughput

    Measures how quickly blockers can be escalated to orchestrator.

    Args:
        num_blockers: Number of blocker escalations to measure

    Returns:
        BenchmarkResult with escalation metrics
    """
    print(f"\n📊 Benchmark: Blocker Escalation Throughput ({num_blockers} blockers)")

    # Setup
    event_bus = EventBus()
    coordinator = IFCoordinator(event_bus=event_bus)
    await coordinator.connect()

    # Register swarm
    await coordinator.register_swarm('test-swarm', [Capability.CODE_ANALYSIS_PYTHON])

    # Measure escalation latency
    print(f"   Escalating {num_blockers} blockers...")
    latencies = []

    start_time = time.perf_counter()

    for i in range(num_blockers):
        blocker_info = {
            'type': 'circuit_breaker_tripped',
            'reason': 'budget_exhausted',
            'task_id': f'task-{i}'
        }

        escalate_start = time.perf_counter()
        await coordinator.detect_blocker('test-swarm', blocker_info)
        escalate_duration = (time.perf_counter() - escalate_start) * 1000  # ms

        latencies.append(escalate_duration)

    end_time = time.perf_counter()
    duration = end_time - start_time

    # Calculate metrics
    throughput = num_blockers / duration if duration > 0 else 0
    percentiles = calculate_percentiles(latencies)

    await coordinator.disconnect()

    print(f"   ✅ Escalated {num_blockers} blockers in {duration:.3f}s")
    print(f"   ⚡ Throughput: {throughput:.0f} escalations/second")
    print(f"   📈 Latency: p50={percentiles['p50']:.3f}ms, p95={percentiles['p95']:.3f}ms, p99={percentiles['p99']:.3f}ms")

    return BenchmarkResult(
        name='blocker_escalation_throughput',
        duration_seconds=duration,
        operations=num_blockers,
        throughput_ops_per_sec=throughput,
        latencies_ms=latencies,
        p50_ms=percentiles['p50'],
        p95_ms=percentiles['p95'],
        p99_ms=percentiles['p99'],
        min_ms=percentiles['min'],
        max_ms=percentiles['max'],
        mean_ms=percentiles['mean'],
        median_ms=percentiles['median'],
    )


def load_baseline(baseline_file: str = 'benchmarks/baseline.json') -> Dict[str, Any]:
    """Load baseline performance metrics from file

    Args:
        baseline_file: Path to baseline JSON file

    Returns:
        Dictionary with baseline metrics, or empty dict if not found
    """
    try:
        with open(baseline_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_baseline(suite: BenchmarkSuite, baseline_file: str = 'benchmarks/baseline.json'):
    """Save current results as baseline

    Args:
        suite: BenchmarkSuite to save as baseline
        baseline_file: Path to save baseline JSON
    """
    with open(baseline_file, 'w') as f:
        json.dump(suite.to_dict(), f, indent=2)
    print(f"\n💾 Saved baseline to {baseline_file}")


def detect_regressions(
    current: BenchmarkResult,
    baseline: Dict[str, Any],
    threshold_percent: float = 10.0
) -> List[str]:
    """Detect performance regressions compared to baseline

    Args:
        current: Current benchmark result
        baseline: Baseline benchmark results dictionary
        threshold_percent: Regression threshold (% slower)

    Returns:
        List of regression messages (empty if no regressions)
    """
    regressions = []

    if not baseline:
        return regressions

    # Find matching baseline result
    baseline_result = None
    for result in baseline.get('results', []):
        if result['name'] == current.name:
            baseline_result = result
            break

    if not baseline_result:
        return regressions

    # Check throughput regression
    baseline_throughput = baseline_result['throughput_ops_per_sec']
    current_throughput = current.throughput_ops_per_sec

    if current_throughput < baseline_throughput * (1 - threshold_percent / 100):
        percent_slower = ((baseline_throughput - current_throughput) / baseline_throughput) * 100
        regressions.append(
            f"⚠️  Throughput regression: {current_throughput:.0f} ops/s vs baseline {baseline_throughput:.0f} ops/s ({percent_slower:.1f}% slower)"
        )

    # Check p95 latency regression
    baseline_p95 = baseline_result['p95_ms']
    current_p95 = current.p95_ms

    if current_p95 > baseline_p95 * (1 + threshold_percent / 100):
        percent_slower = ((current_p95 - baseline_p95) / baseline_p95) * 100
        regressions.append(
            f"⚠️  P95 latency regression: {current_p95:.3f}ms vs baseline {baseline_p95:.3f}ms ({percent_slower:.1f}% slower)"
        )

    # Check p99 latency regression
    baseline_p99 = baseline_result['p99_ms']
    current_p99 = current.p99_ms

    if current_p99 > baseline_p99 * (1 + threshold_percent / 100):
        percent_slower = ((current_p99 - baseline_p99) / baseline_p99) * 100
        regressions.append(
            f"⚠️  P99 latency regression: {current_p99:.3f}ms vs baseline {baseline_p99:.3f}ms ({percent_slower:.1f}% slower)"
        )

    return regressions


def generate_ascii_chart(result: BenchmarkResult, width: int = 60) -> str:
    """Generate ASCII bar chart for latency distribution

    Args:
        result: BenchmarkResult to visualize
        width: Chart width in characters

    Returns:
        ASCII art chart as string
    """
    chart_lines = []
    chart_lines.append(f"\n📊 {result.name.replace('_', ' ').title()} - Latency Distribution")
    chart_lines.append("=" * width)

    # Latency metrics
    metrics = [
        ('Min', result.min_ms),
        ('P50 (median)', result.p50_ms),
        ('P95', result.p95_ms),
        ('P99', result.p99_ms),
        ('Max', result.max_ms),
    ]

    max_value = result.max_ms if result.max_ms > 0 else 1

    for label, value in metrics:
        bar_length = int((value / max_value) * (width - 25))
        bar = '█' * bar_length
        chart_lines.append(f"{label:15} {value:8.3f}ms |{bar}")

    chart_lines.append("=" * width)
    chart_lines.append(f"Mean: {result.mean_ms:.3f}ms | Throughput: {result.throughput_ops_per_sec:.0f} ops/s")
    chart_lines.append(f"Operations: {result.operations} | Duration: {result.duration_seconds:.3f}s")

    return '\n'.join(chart_lines)


def generate_summary_report(suite: BenchmarkSuite, baseline: Dict[str, Any]) -> str:
    """Generate comprehensive summary report

    Args:
        suite: BenchmarkSuite with all results
        baseline: Baseline metrics for comparison

    Returns:
        Formatted summary report
    """
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("IF.COORDINATOR PERFORMANCE BENCHMARK REPORT")
    lines.append("=" * 80)
    lines.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(suite.timestamp))}")
    lines.append("")

    # Overall summary
    total_operations = sum(r.operations for r in suite.results)
    total_duration = sum(r.duration_seconds for r in suite.results)

    lines.append("📈 OVERALL SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Benchmarks: {len(suite.results)}")
    lines.append(f"Total Operations: {total_operations:,}")
    lines.append(f"Total Duration: {total_duration:.2f}s")
    lines.append("")

    # Individual benchmark results
    lines.append("📊 BENCHMARK RESULTS")
    lines.append("-" * 80)

    for result in suite.results:
        lines.append(f"\n{result.name.replace('_', ' ').title()}:")
        lines.append(f"  Operations: {result.operations:,} in {result.duration_seconds:.3f}s")
        lines.append(f"  Throughput: {result.throughput_ops_per_sec:,.0f} ops/second")
        lines.append(f"  Latency (ms):")
        lines.append(f"    Min: {result.min_ms:.3f}  |  P50: {result.p50_ms:.3f}  |  P95: {result.p95_ms:.3f}  |  P99: {result.p99_ms:.3f}  |  Max: {result.max_ms:.3f}")

        # Check for regressions
        regressions = detect_regressions(result, baseline)
        if regressions:
            lines.append("  ⚠️  PERFORMANCE REGRESSIONS DETECTED:")
            for regression in regressions:
                lines.append(f"    {regression}")
        else:
            if baseline:
                lines.append("  ✅ No regressions detected")

    lines.append("")
    lines.append("=" * 80)

    return '\n'.join(lines)


async def run_full_benchmark_suite() -> BenchmarkSuite:
    """Run complete benchmark suite

    Returns:
        BenchmarkSuite with all results
    """
    print("\n" + "=" * 80)
    print("🚀 IF.COORDINATOR PERFORMANCE BENCHMARK SUITE")
    print("=" * 80)
    print("Session 7 - Filler Task F7.10")
    print("Measuring performance of P0.1.2 (Atomic CAS) + P0.1.3 (Real-Time Broadcast)")
    print("=" * 80)

    results = []

    # Benchmark 1: Task claiming throughput
    result = await benchmark_task_claiming_throughput(num_tasks=1000, num_swarms=10)
    results.append(result)
    print(generate_ascii_chart(result))

    # Benchmark 2: Broadcast latency
    result = await benchmark_broadcast_latency(num_broadcasts=1000, num_swarms=20)
    results.append(result)
    print(generate_ascii_chart(result))

    # Benchmark 3: Multi-swarm coordination
    result = await benchmark_multi_swarm_coordination(num_swarms=50, num_tasks=500, concurrent_operations=10)
    results.append(result)
    print(generate_ascii_chart(result))

    # Benchmark 4: Blocker escalation throughput
    result = await benchmark_blocker_escalation_throughput(num_blockers=1000)
    results.append(result)
    print(generate_ascii_chart(result))

    # Create suite
    suite = BenchmarkSuite(
        timestamp=time.time(),
        results=results
    )

    # Load baseline and detect regressions
    baseline = load_baseline()
    suite.baseline = baseline

    # Generate summary report
    report = generate_summary_report(suite, baseline)
    print(report)

    # Save results
    results_file = 'benchmarks/results_latest.json'
    with open(results_file, 'w') as f:
        json.dump(suite.to_dict(), f, indent=2)
    print(f"\n💾 Saved results to {results_file}")

    # Ask if should save as baseline
    print("\n💡 Tip: To save these results as baseline for future regression detection:")
    print("    python -c \"from benchmarks.coordinator_performance import *; import asyncio; asyncio.run(save_baseline_interactive())\"")

    return suite


async def save_baseline_interactive():
    """Interactive baseline saving"""
    suite = await run_full_benchmark_suite()
    save_baseline(suite)


if __name__ == '__main__':
    asyncio.run(run_full_benchmark_suite())
