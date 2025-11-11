"""
Load Test: H.323 Guardian Council (8-12 Concurrent Video Streams)

Simulates IF.guard council meeting with multiple concurrent guardians.

Test Scenarios:
1. 8 guardians (baseline)
2. 12 guardians (target capacity)
3. 15 guardians (maximum capacity)
4. 20 guardians (stress test)

Measurements:
- Bandwidth usage per guardian
- End-to-end latency (RTP)
- Packet loss rate
- Jitter (variance in latency)
- MCU CPU/memory usage

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import asyncio
import json
import subprocess
import time
import statistics
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
import random


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class GuardianEndpoint:
    """Simulated H.323 Guardian terminal"""
    terminal_id: str
    codec: str              # G.729, G.711
    bitrate_kbps: int       # 8 kbps (G.729) or 64 kbps (G.711)
    video_enabled: bool
    video_bitrate_kbps: int  # 0 (audio only) or 2000 (720p video)
    rtp_port: int


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single guardian"""
    terminal_id: str
    bandwidth_kbps: float
    latency_ms: float
    packet_loss_percent: float
    jitter_ms: float
    cpu_percent: float


@dataclass
class LoadTestResults:
    """Complete load test results"""
    test_id: str
    timestamp: str
    num_guardians: int
    test_duration_sec: float

    # Aggregate metrics
    total_bandwidth_mbps: float
    avg_latency_ms: float
    max_latency_ms: float
    avg_packet_loss_percent: float
    avg_jitter_ms: float
    mcu_cpu_percent: float
    mcu_memory_mb: float

    # Per-guardian metrics
    guardian_metrics: List[PerformanceMetrics]

    # Success criteria
    meets_requirements: bool
    issues: List[str]


# ============================================================================
# H.323 Endpoint Simulator
# ============================================================================

class H323EndpointSimulator:
    """
    Simulates H.323 Guardian terminal sending RTP streams.

    In production, this would use:
    - OpenH323 library (libh323plus)
    - GStreamer RTP pipelines
    - Real codec encoding

    For testing, we simulate network behavior.
    """

    def __init__(self, endpoint: GuardianEndpoint):
        self.endpoint = endpoint
        self.running = False
        self.packets_sent = 0
        self.packets_received = 0
        self.latencies_ms: List[float] = []

    async def start_streaming(self, duration_sec: int = 30):
        """Simulate RTP streaming for duration"""
        self.running = True
        start_time = time.time()

        print(f"[{self.endpoint.terminal_id}] Starting stream...")
        print(f"  Audio: {self.endpoint.codec} ({self.endpoint.bitrate_kbps} kbps)")
        print(f"  Video: {'Enabled' if self.endpoint.video_enabled else 'Disabled'} "
              f"({self.endpoint.video_bitrate_kbps} kbps)")

        while self.running and (time.time() - start_time) < duration_sec:
            # Simulate sending RTP packets
            await self._send_rtp_packet()
            await asyncio.sleep(0.02)  # 50 packets/sec

        self.running = False
        print(f"[{self.endpoint.terminal_id}] Stream stopped")

    async def _send_rtp_packet(self):
        """Simulate sending one RTP packet"""
        # Simulate network latency (2-50ms range)
        latency = random.uniform(2.0, 50.0)
        self.latencies_ms.append(latency)
        self.packets_sent += 1

        # Simulate packet loss (0-2% range)
        if random.random() > 0.02:  # 98% success rate
            self.packets_received += 1

    def get_metrics(self) -> PerformanceMetrics:
        """Get performance metrics for this endpoint"""
        # Calculate bandwidth
        total_bitrate_kbps = self.endpoint.bitrate_kbps
        if self.endpoint.video_enabled:
            total_bitrate_kbps += self.endpoint.video_bitrate_kbps

        # Calculate latency stats
        avg_latency = statistics.mean(self.latencies_ms) if self.latencies_ms else 0

        # Calculate jitter (variance in latency)
        jitter = statistics.stdev(self.latencies_ms) if len(self.latencies_ms) > 1 else 0

        # Calculate packet loss
        packet_loss = 0.0
        if self.packets_sent > 0:
            packet_loss = (1 - self.packets_received / self.packets_sent) * 100

        return PerformanceMetrics(
            terminal_id=self.endpoint.terminal_id,
            bandwidth_kbps=total_bitrate_kbps,
            latency_ms=avg_latency,
            packet_loss_percent=packet_loss,
            jitter_ms=jitter,
            cpu_percent=random.uniform(2.0, 8.0)  # Mock CPU usage
        )


# ============================================================================
# MCU Load Simulator
# ============================================================================

class MCULoadSimulator:
    """
    Simulates MCU (Multipoint Control Unit) mixing load.

    MCU tasks:
    - Audio mixing (N inputs → N outputs)
    - Video layout (continuous presence grid)
    - T.120 whiteboard
    """

    def __init__(self, max_participants: int = 25):
        self.max_participants = max_participants
        self.current_participants = 0
        self.cpu_usage_percent = 0.0
        self.memory_usage_mb = 100.0  # Base usage

    def add_participant(self):
        """Add guardian to MCU"""
        if self.current_participants >= self.max_participants:
            raise ValueError("MCU at capacity")

        self.current_participants += 1

        # CPU scales roughly O(N log N) for audio mixing
        self.cpu_usage_percent = 10 + (self.current_participants * 3) + \
                                 (self.current_participants * 0.5 * (self.current_participants - 1))

        # Memory scales linearly with participants
        self.memory_usage_mb = 100 + (self.current_participants * 50)

    def remove_participant(self):
        """Remove guardian from MCU"""
        if self.current_participants > 0:
            self.current_participants -= 1

    def get_metrics(self) -> Dict[str, float]:
        """Get MCU performance metrics"""
        return {
            "participants": self.current_participants,
            "cpu_percent": min(self.cpu_usage_percent, 100.0),
            "memory_mb": self.memory_usage_mb
        }


# ============================================================================
# Load Test Orchestrator
# ============================================================================

class GuardianCouncilLoadTest:
    """
    Orchestrates load testing for Guardian Council meetings.
    """

    def __init__(self, results_dir: Path = Path("/home/user/infrafabric/logs/load_tests")):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.mcu = MCULoadSimulator(max_participants=25)

    async def run_test(
        self,
        num_guardians: int,
        test_duration_sec: int = 30,
        video_enabled: bool = True
    ) -> LoadTestResults:
        """
        Run load test with specified number of guardians.

        Args:
            num_guardians: Number of concurrent guardians (8-20)
            test_duration_sec: Test duration in seconds
            video_enabled: Enable video streams (vs audio-only)

        Returns:
            LoadTestResults with performance metrics
        """
        test_id = f"load-test-{num_guardians}-guardians-{int(time.time())}"

        print("\n" + "="*70)
        print(f"Load Test: {num_guardians} Guardians")
        print("="*70)
        print(f"Test ID: {test_id}")
        print(f"Duration: {test_duration_sec}s")
        print(f"Video: {'Enabled' if video_enabled else 'Disabled'}")
        print()

        # Create guardian endpoints
        endpoints = []
        simulators = []

        for i in range(num_guardians):
            endpoint = GuardianEndpoint(
                terminal_id=f"if://guardian/test-{i+1}",
                codec="G.729",
                bitrate_kbps=8,  # G.729 = 8 kbps
                video_enabled=video_enabled,
                video_bitrate_kbps=2000 if video_enabled else 0,  # 720p ≈ 2 Mbps
                rtp_port=10000 + i
            )
            endpoints.append(endpoint)

            simulator = H323EndpointSimulator(endpoint)
            simulators.append(simulator)

            # Add to MCU
            self.mcu.add_participant()

        # Start all streams concurrently
        start_time = time.time()
        tasks = [sim.start_streaming(test_duration_sec) for sim in simulators]
        await asyncio.gather(*tasks)
        end_time = time.time()

        # Collect metrics
        guardian_metrics = [sim.get_metrics() for sim in simulators]
        mcu_metrics = self.mcu.get_metrics()

        # Calculate aggregate metrics
        total_bandwidth_kbps = sum(m.bandwidth_kbps for m in guardian_metrics)
        avg_latency = statistics.mean(m.latency_ms for m in guardian_metrics)
        max_latency = max(m.latency_ms for m in guardian_metrics)
        avg_packet_loss = statistics.mean(m.packet_loss_percent for m in guardian_metrics)
        avg_jitter = statistics.mean(m.jitter_ms for m in guardian_metrics)

        # Evaluate success criteria
        issues = []
        if total_bandwidth_kbps / 1000 > 100:  # 100 Mbps total budget
            issues.append(f"Bandwidth exceeded: {total_bandwidth_kbps/1000:.1f} Mbps > 100 Mbps")

        if avg_latency > 150:  # 150ms acceptable for real-time
            issues.append(f"Latency too high: {avg_latency:.1f}ms > 150ms")

        if avg_packet_loss > 1.0:  # <1% packet loss required
            issues.append(f"Packet loss too high: {avg_packet_loss:.2f}% > 1%")

        if mcu_metrics["cpu_percent"] > 80:  # 80% CPU threshold
            issues.append(f"MCU CPU overloaded: {mcu_metrics['cpu_percent']:.1f}% > 80%")

        meets_requirements = len(issues) == 0

        # Create results
        results = LoadTestResults(
            test_id=test_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            num_guardians=num_guardians,
            test_duration_sec=end_time - start_time,
            total_bandwidth_mbps=total_bandwidth_kbps / 1000,
            avg_latency_ms=avg_latency,
            max_latency_ms=max_latency,
            avg_packet_loss_percent=avg_packet_loss,
            avg_jitter_ms=avg_jitter,
            mcu_cpu_percent=mcu_metrics["cpu_percent"],
            mcu_memory_mb=mcu_metrics["memory_mb"],
            guardian_metrics=guardian_metrics,
            meets_requirements=meets_requirements,
            issues=issues
        )

        # Save results
        self._save_results(results)

        # Print summary
        self._print_results(results)

        return results

    def _save_results(self, results: LoadTestResults):
        """Save results to JSON file"""
        results_file = self.results_dir / f"{results.test_id}.json"

        # Convert to dict
        results_dict = asdict(results)

        with open(results_file, 'w') as f:
            json.dump(results_dict, f, indent=2)

        print(f"\n📊 Results saved: {results_file}")

    def _print_results(self, results: LoadTestResults):
        """Print results summary"""
        print("\n" + "="*70)
        print("Test Results")
        print("="*70)
        print(f"Guardians: {results.num_guardians}")
        print(f"Duration: {results.test_duration_sec:.1f}s")
        print()
        print("Bandwidth:")
        print(f"  Total: {results.total_bandwidth_mbps:.2f} Mbps")
        print(f"  Per Guardian: {results.total_bandwidth_mbps / results.num_guardians:.2f} Mbps")
        print()
        print("Latency:")
        print(f"  Average: {results.avg_latency_ms:.1f} ms")
        print(f"  Maximum: {results.max_latency_ms:.1f} ms")
        print()
        print("Quality:")
        print(f"  Packet Loss: {results.avg_packet_loss_percent:.2f}%")
        print(f"  Jitter: {results.avg_jitter_ms:.1f} ms")
        print()
        print("MCU Load:")
        print(f"  CPU: {results.mcu_cpu_percent:.1f}%")
        print(f"  Memory: {results.mcu_memory_mb:.1f} MB")
        print()
        print(f"Status: {'✅ PASS' if results.meets_requirements else '❌ FAIL'}")

        if results.issues:
            print("\nIssues:")
            for issue in results.issues:
                print(f"  - {issue}")

        print("="*70)


# ============================================================================
# Test Suite
# ============================================================================

async def run_load_test_suite():
    """Run complete load test suite"""
    tester = GuardianCouncilLoadTest()

    test_cases = [
        ("8 Guardians (Baseline)", 8, 30, True),
        ("12 Guardians (Target)", 12, 30, True),
        ("15 Guardians (Maximum)", 15, 30, True),
        ("20 Guardians (Stress Test)", 20, 30, True),
    ]

    all_results = []

    print("\n" + "="*70)
    print("Guardian Council Load Test Suite")
    print("="*70)

    for test_name, num_guardians, duration, video in test_cases:
        print(f"\nRunning: {test_name}")
        results = await tester.run_test(num_guardians, duration, video)
        all_results.append(results)

        # Wait between tests
        await asyncio.sleep(2)

    # Print summary
    print("\n" + "="*70)
    print("Load Test Suite Summary")
    print("="*70)

    for i, (test_name, _, _, _) in enumerate(test_cases):
        results = all_results[i]
        status = "✅ PASS" if results.meets_requirements else "❌ FAIL"
        print(f"{test_name}: {status}")
        print(f"  Bandwidth: {results.total_bandwidth_mbps:.2f} Mbps")
        print(f"  Latency: {results.avg_latency_ms:.1f} ms")
        print(f"  MCU CPU: {results.mcu_cpu_percent:.1f}%")

    print("="*70)

    # Overall assessment
    max_supported = 0
    for i, results in enumerate(all_results):
        if results.meets_requirements:
            max_supported = test_cases[i][1]

    print(f"\n🎯 Maximum Supported Guardians: {max_supported}")
    print(f"   Target: 15 concurrent guardians")
    print(f"   Status: {'✅ ACHIEVED' if max_supported >= 15 else '❌ NOT ACHIEVED'}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    asyncio.run(run_load_test_suite())
