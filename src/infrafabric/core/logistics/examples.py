#!/usr/bin/env python3
"""
IF.LOGISTICS Usage Examples

Demonstrates how to use Parcel, LogisticsDispatcher, and DispatchQueue
for Redis operations using the civic logistics metaphor.
"""

from infrafabric.core.logistics import DispatchQueue, LogisticsDispatcher, Parcel


def example_basic_string_storage() -> None:
    """Basic dispatch/collect with chain-of-custody semantics."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    parcel = Parcel(
        origin="council-secretariat",
        contents={"query": "find architecture patterns", "results_count": 42},
    )

    print("\n=== Example: Basic String Storage ===")
    print(f"Dispatching Parcel {parcel.tracking_id} from {parcel.origin}...")
    dispatcher.dispatch_to_redis(key="logistics:latest", parcel=parcel, operation="set")

    fetched = dispatcher.collect_from_redis(key="logistics:latest", operation="get")
    if fetched:
        print("Recovered Parcel with contents:")
        print(f"  origin: {fetched.origin}")
        print(f"  contents: {fetched.contents}")
        print(f"  dispatched_at: {fetched.dispatched_at}")


def example_list_queue() -> None:
    """Queue-style list operations for sequential processing."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    parcels = [
        Parcel(origin=f"worker-{i}", contents={"task_id": f"task-{i:03d}"})
        for i in range(3)
    ]

    print("\n=== Example: Queue Operations (LIST) ===")
    for parcel in parcels:
        dispatcher.dispatch_to_redis(key="logistics:queue", parcel=parcel, operation="rpush")
        print(f"  queued {parcel.contents['task_id']} with tracking {parcel.tracking_id}")

    recovered = dispatcher.collect_from_redis(key="logistics:queue", operation="lrange")
    print(f"Recovered {len(recovered or [])} Parcels in FIFO order")
    for item in recovered or []:
        print(f"  {item.tracking_id}: {item.contents}")


def example_hash_registry() -> None:
    """Hash-based storage keyed by tracking IDs."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    parcels = [
        Parcel(origin="dispatch-a", contents={"role": "coordinator", "status": "active"}),
        Parcel(origin="dispatch-b", contents={"role": "worker", "status": "idle"}),
        Parcel(origin="dispatch-c", contents={"role": "archive", "status": "indexing"}),
    ]

    print("\n=== Example: Hash Registry ===")
    for parcel in parcels:
        dispatcher.dispatch_to_redis(key="logistics:registry", parcel=parcel, operation="hset")
        print(f"  stored {parcel.origin} as {parcel.tracking_id}")

    registry = dispatcher.collect_from_redis(key="logistics:registry", operation="hgetall")
    print(f"Registry contains {len(registry or {})} Parcels")
    for tracking_id, parcel in (registry or {}).items():
        print(f"  {tracking_id} → {parcel.origin}: {parcel.contents}")


def example_batch_dispatch() -> None:
    """Batch dispatch via DispatchQueue to reduce round-trips."""

    dispatcher = LogisticsDispatcher(redis_db=15)
    queue = DispatchQueue(dispatcher)

    for i in range(5):
        parcel = Parcel(origin="batch-office", contents={"line_item": i})
        queue.add_parcel("logistics:batch", parcel, operation="lpush")

    print("\n=== Example: Batch Dispatch ===")
    count = queue.flush()
    print(f"Queued {count} Parcels in a single flush")


if __name__ == "__main__":
    example_basic_string_storage()
    example_list_queue()
    example_hash_registry()
    example_batch_dispatch()
