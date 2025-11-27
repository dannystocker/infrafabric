# IF.LOGISTICS - Implementation Summary

**Status**: ✓ Complete and ready for integration

## Overview

IF.LOGISTICS standardizes how InfraFabric moves data through Redis: every Packet gets a tracking ID, is validated against a schema, and carries IF.TTT chain-of-custody headers. The transport metaphor is replaced with a civic dispatch office that enforces rules before anything leaves the dock.

## Core Components

### Packet (dataclass)
- **Purpose**: Sealed container for data with automatic tracking ID and timestamp.
- **Fields**:
  - `tracking_id`: UUID4 (unique, traceable)
  - `dispatched_at`: ISO8601 timestamp
  - `origin`: Preparing agent/department
  - `contents`: Arbitrary dict payload
  - `schema_version`: "1.0" or "1.1"
  - `ttl_seconds`: Time-to-live (1-86400 seconds)
  - `chain_of_custody`: Optional IF.TTT headers (v1.1+)
- **Features**:
  - Automatic validation on creation
  - JSON or msgpack serialization
  - Legacy field mapping for backward compatibility

### LogisticsDispatcher (class)
- **Purpose**: Central dispatch layer for Redis operations.
- **Responsibilities**:
  1. Schema validation before writes ("No Schema, No Dispatch")
  2. Type checking to prevent WRONGTYPE errors
  3. Automatic serialization/deserialization
  4. TTL management and stats reporting
  5. Chain-of-custody preservation
- **Operations Supported**:
  - STRING: `set`/`get`
  - LIST: `lpush`/`rpush`/`lindex`/`lrange`
  - HASH: `hset`/`hget`/`hgetall`
  - SET: `sadd`/`smembers`
- **Utilities**: `key_exists`, `get_key_type`, `delete_key`, `clear_all`, `get_stats`

### DispatchQueue (class)
- **Purpose**: Batch dispatch to reduce Redis round-trips.
- **Feature**: Queue many Parcels and send in a single flush.

### RedisKeyType (enum)
- **Purpose**: Type-safe guards for Redis key types.
- **Values**: STRING, LIST, HASH, SET, ZSET, STREAM, NONE

## Schema Validation ("No Schema, No Dispatch")

### Schema v1.0
```json
{
  "tracking_id": "uuid4",
  "dispatched_at": "iso8601",
  "origin": "string(1-255)",
  "contents": "object",
  "schema_version": "1.0",
  "ttl_seconds": "integer(1-86400)"
}
```

### Schema v1.1 (with Chain of Custody)
```json
{
  "tracking_id": "uuid4",
  "dispatched_at": "iso8601",
  "origin": "string(1-255)",
  "contents": "object",
  "schema_version": "1.1",
  "ttl_seconds": "integer(1-86400)",
  "chain_of_custody": {
    "traceable_id": "string",
    "transparent_lineage": "array[string]",
    "trustworthy_signature": "string"
  }
}
```

Validation enforcement:
- Required fields must be present
- Field types must match schema
- TTL must be 1-86400 seconds
- Unknown schema versions raise `ValueError`

## Type Safety

Redis type mismatches are blocked before execution. Example:
```python
dispatcher.dispatch_to_redis(key='docs', packet=packet, operation='set')

with pytest.raises(TypeError):
    dispatcher.dispatch_to_redis(key='docs', packet=packet, operation='rpush')
```

## Serialization Options

- **JSON (default):** human-readable, built-in.
- **msgpack (optional):** smaller/faster; install `msgpack` to enable.

## Error Handling

- `ValueError` for schema violations
- `TypeError` for Redis type mismatches
- `RuntimeError` for Redis connectivity or msgpack availability issues

## Batch Dispatch Pattern

```python
from infrafabric.core.logistics import DispatchQueue, LogisticsDispatcher, Packet

dispatcher = LogisticsDispatcher()
queue = DispatchQueue(dispatcher)
for i in range(50):
    queue.add_parcel('logistics:batch', Packet(origin='worker', contents={'i': i}), operation='lpush')
queue.flush()
```

## Chain-of-Custody Guidance

Use schema v1.1 when you need IF.TTT alignment:
- `traceable_id` keeps a consistent audit handle.
- `transparent_lineage` records each hop.
- `trustworthy_signature` captures author verification.
