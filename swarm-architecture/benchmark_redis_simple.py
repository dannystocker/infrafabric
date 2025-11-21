#!/usr/bin/env python3
"""
Simple Redis Benchmark for Swarm Architecture
Tests basic operations and measures latency
"""

import redis
import time
import json
import sys

def benchmark_redis():
    """Run Redis benchmarks and print results"""

    print("=" * 60)
    print("REDIS SWARM ARCHITECTURE BENCHMARK")
    print("=" * 60)
    print()

    # Connect to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Connected to Redis (localhost:6379)")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        sys.exit(1)

    print()

    # Test 1: PING (round-trip latency)
    print("Test 1: PING Latency (1000 iterations)")
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        r.ping()
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms

    avg_ping = sum(times) / len(times)
    min_ping = min(times)
    max_ping = max(times)
    print(f"  Average: {avg_ping:.3f} ms")
    print(f"  Min:     {min_ping:.3f} ms")
    print(f"  Max:     {max_ping:.3f} ms")
    print()

    # Test 2: SET operations (write latency)
    print("Test 2: SET Latency (1000 iterations)")
    times = []
    for i in range(1000):
        start = time.perf_counter()
        r.set(f"benchmark:test:{i}", "test_value")
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    avg_set = sum(times) / len(times)
    min_set = min(times)
    max_set = max(times)
    print(f"  Average: {avg_set:.3f} ms")
    print(f"  Min:     {min_set:.3f} ms")
    print(f"  Max:     {max_set:.3f} ms")
    print()

    # Test 3: GET operations (read latency)
    print("Test 3: GET Latency (1000 iterations)")
    times = []
    for i in range(1000):
        start = time.perf_counter()
        r.get(f"benchmark:test:{i}")
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    avg_get = sum(times) / len(times)
    min_get = min(times)
    max_get = max(times)
    print(f"  Average: {avg_get:.3f} ms")
    print(f"  Min:     {min_get:.3f} ms")
    print(f"  Max:     {max_get:.3f} ms")
    print()

    # Test 4: Large context transfer (800K tokens ≈ 3.2MB)
    print("Test 4: Large Context Transfer (3.2MB, simulating 800K tokens)")
    large_context = "x" * (3_200_000)  # 3.2MB string

    # Write
    start = time.perf_counter()
    r.set("benchmark:large_context", large_context)
    write_time = (time.perf_counter() - start) * 1000
    print(f"  Write: {write_time:.2f} ms")

    # Read
    start = time.perf_counter()
    retrieved = r.get("benchmark:large_context")
    read_time = (time.perf_counter() - start) * 1000
    print(f"  Read:  {read_time:.2f} ms")
    print(f"  Total: {write_time + read_time:.2f} ms")
    print()

    # Test 5: Task queue operations (lpush/lpop)
    print("Test 5: Task Queue Operations (1000 iterations)")
    times = []
    for i in range(1000):
        # Simulate task posting
        task_data = json.dumps({
            "task_id": f"task_{i}",
            "type": "research",
            "data": {"query": "test query"}
        })

        start = time.perf_counter()
        r.rpush("benchmark:queue", task_data)
        r.lpop("benchmark:queue")
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)

    avg_queue = sum(times) / len(times)
    min_queue = min(times)
    max_queue = max(times)
    print(f"  Average: {avg_queue:.3f} ms")
    print(f"  Min:     {min_queue:.3f} ms")
    print(f"  Max:     {max_queue:.3f} ms")
    print()

    # Cleanup
    print("Cleaning up benchmark keys...")
    for i in range(1000):
        r.delete(f"benchmark:test:{i}")
    r.delete("benchmark:large_context")
    r.delete("benchmark:queue")
    print("✅ Cleanup complete")
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"PING latency:          {avg_ping:.3f} ms")
    print(f"SET latency:           {avg_set:.3f} ms")
    print(f"GET latency:           {avg_get:.3f} ms")
    print(f"Queue ops latency:     {avg_queue:.3f} ms")
    print(f"Large context (800K):  {write_time + read_time:.2f} ms")
    print()
    print("COMPARISON TO JSONL (2-3 seconds):")
    jsonl_baseline = 2500  # 2.5 seconds in ms
    speedup_ping = jsonl_baseline / avg_ping
    speedup_context = jsonl_baseline / (write_time + read_time)
    print(f"  PING speedup:     {speedup_ping:.0f}×")
    print(f"  Context speedup:  {speedup_context:.0f}×")
    print()
    print("✅ BENCHMARK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    benchmark_redis()
