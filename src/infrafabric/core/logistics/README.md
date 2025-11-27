# IF.LOGISTICS - Packet Dispatch for Redis

A civic logistics layer that seals data into Parcels, validates every manifest, and dispatches to Redis with chain-of-custody metadata.

## Overview

InfraFabric treats Redis like a city-wide dispatch yard. The Logistics Department issues a tracking ID, wraps data in protective packaging, and enforces schema and type checks before anything leaves the dock. No schema? No dispatch.

## Core Concepts

### Packet
A sealed container with a tracking ID and custody headers.
```python
from infrafabric.core.logistics import Packet

packet = Packet(
    origin="council-secretariat",
    contents={"query": "find architecture patterns"},
    schema_version="1.0",
    ttl_seconds=3600,
)
```
Fields:
- `tracking_id`: UUID4 for traceability
- `dispatched_at`: ISO8601 timestamp
- `origin`: Who prepared the Packet
- `contents`: The document or data being moved
- `chain_of_custody`: IF.TTT metadata (v1.1+)

### LogisticsDispatcher
The central dispatch office that validates schemas, checks Redis key types, and handles serialization.
```python
from infrafabric.core.logistics import LogisticsDispatcher

dispatcher = LogisticsDispatcher(redis_host="localhost", redis_port=6379)
dispatcher.dispatch_to_redis("logistics:queue", packet)
fetched = dispatcher.collect_from_redis("logistics:queue")
```

### DispatchQueue
Batch dispatcher that reduces round-trips when you have many Parcels to move.
```python
from infrafabric.core.logistics import DispatchQueue

queue = DispatchQueue(dispatcher)
queue.add_parcel("logistics:batch", packet, operation="lpush")
queue.flush()
```

### RedisKeyType
Enum for type-aware safety rails (`STRING`, `LIST`, `HASH`, `SET`, `ZSET`, `STREAM`, `NONE`).

## Quick Start

```python
from infrafabric.core.logistics import LogisticsDispatcher, Packet

dispatcher = LogisticsDispatcher()
packet = Packet(origin="librarian", contents={"question": "What is Series 2?"})

# Dispatch with schema + type checks
dispatcher.dispatch_to_redis(key="requests:latest", packet=packet, operation="set")

# Collect and deserialize
restored = dispatcher.collect_from_redis(key="requests:latest", operation="get")
print(restored.contents)
```

## Schema Validation (No Schema, No Dispatch)

Supported schema versions:
- **1.0**: tracking_id, dispatched_at, origin, contents, schema_version, ttl_seconds
- **1.1**: Adds `chain_of_custody` (traceable_id, transparent_lineage, trustworthy_signature)

Every dispatch calls `_validate_schema` before writing to Redis and rejects mismatched types (e.g., trying to `lpush` into a HASH key).

## Operations

- `dispatch_to_redis(key, packet, operation="set", use_msgpack=False)`
- `collect_from_redis(key, operation="get", list_index=None, hash_field=None, use_msgpack=False)`
- `key_exists`, `get_key_type`, `delete_key`, `clear_all`, `get_stats`

### Supported Redis operations
- `set` → STRING
- `lpush` / `rpush` → LIST
- `hset` → HASH (field uses `tracking_id`)
- `sadd` → SET

## Examples

See `examples.py` for runnable snippets covering single dispatches, queues, hash registries, and batch flushes.

## Error Handling

- Type mismatches raise `TypeError` with a human-readable explanation.
- Schema violations raise `ValueError`.
- Redis connectivity issues surface as `RuntimeError`.

## Chain of Custody

IF.TTT headers live in `chain_of_custody` to record traceable IDs, lineage, and signatures. Parcels can be validated against schema v1.1 to enforce custody before dispatch.
