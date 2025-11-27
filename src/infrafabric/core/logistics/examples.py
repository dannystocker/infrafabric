#!/usr/bin/env python3
"""
IF.LOGISTICS Usage Examples

Demonstrates how to use Packet, LogisticsDispatcher, and DispatchQueue
for Redis operations using the civic logistics metaphor.
"""

from infrafabric.core.logistics import DispatchQueue, LogisticsDispatcher, Packet


def example_basic_string_storage() -> None:
    """Basic dispatch/collect with chain-of-custody semantics."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    packet = Packet(
        origin="council-secretariat",
        contents={"query": "find architecture patterns", "results_count": 42},
    )

    print("\n=== Example: Basic String Storage ===")
    print(f"Dispatching Packet {packet.tracking_id} from {packet.origin}...")
    dispatcher.dispatch_to_redis(key="logistics:latest", packet=packet, operation="set")

    fetched = dispatcher.collect_from_redis(key="logistics:latest", operation="get")
    if fetched:
        print("Recovered Packet with contents:")
        print(f"  origin: {fetched.origin}")
        print(f"  contents: {fetched.contents}")
        print(f"  dispatched_at: {fetched.dispatched_at}")


def example_list_queue() -> None:
    """Queue-style list operations for sequential processing."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    parcels = [
        Packet(origin=f"worker-{i}", contents={"task_id": f"task-{i:03d}"})
        for i in range(3)
    ]

    print("\n=== Example: Queue Operations (LIST) ===")
    for packet in parcels:
        dispatcher.dispatch_to_redis(key="logistics:queue", packet=packet, operation="rpush")
        print(f"  queued {packet.contents['task_id']} with tracking {packet.tracking_id}")

    recovered = dispatcher.collect_from_redis(key="logistics:queue", operation="lrange")
    print(f"Recovered {len(recovered or [])} Parcels in FIFO order")
    for item in recovered or []:
        print(f"  {item.tracking_id}: {item.contents}")


def example_hash_registry() -> None:
    """Hash-based storage keyed by tracking IDs."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    parcels = [
        Packet(origin="dispatch-a", contents={"role": "coordinator", "status": "active"}),
        Packet(origin="dispatch-b", contents={"role": "worker", "status": "idle"}),
        Packet(origin="dispatch-c", contents={"role": "archive", "status": "indexing"}),
    ]

    print("\n=== Example: Hash Registry ===")
    for packet in parcels:
        dispatcher.dispatch_to_redis(key="logistics:registry", packet=packet, operation="hset")
        print(f"  stored {packet.origin} as {packet.tracking_id}")

    registry = dispatcher.collect_from_redis(key="logistics:registry", operation="hgetall")
    print(f"Registry contains {len(registry or {})} Parcels")
    for tracking_id, packet in (registry or {}).items():
        print(f"  {tracking_id} → {packet.origin}: {packet.contents}")


def example_batch_dispatch() -> None:
    """Batch dispatch via DispatchQueue to reduce round-trips."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    queue = DispatchQueue(dispatcher)

    for i in range(5):
        packet = Packet(origin="batch-office", contents={"line_item": i})
        queue.add_parcel("logistics:batch", packet, operation="lpush")

    print("\n=== Example: Batch Dispatch ===")
    count = queue.flush()
    print(f"Queued {count} Parcels in a single flush")


if __name__ == "__main__":
    example_basic_string_storage()
    example_list_queue()
    example_hash_registry()
    example_batch_dispatch()
