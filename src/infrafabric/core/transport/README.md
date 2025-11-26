# IF.VESICLE v1.0 - Transport Container for Redis Operations

**Transport Container** - A standardized wrapper for all Redis operations that enforces schema validation, prevents type corruption, and adds IF.TTT traceability.

## Table of Contents
- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Schema Validation](#schema-validation)
- [Type Safety](#type-safety)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)

## Overview

IF.VESICLE is inspired by **extracellular vesicles (EVs)** from neuroscience—cellular "message packets" that carry proteins and genetic material across the blood-brain barrier. Similarly, IF.VESICLE is the standardized container for all data flowing through Redis:

```
[Payload] → [VESICLE Container] → [Redis] → [VESICLE Container] → [Payload]
```

### Core Philosophy: "No Schema, No Write"

Every payload must be validated against a schema before being written to Redis. This prevents:
- **Type corruption** (WRONGTYPE errors)
- **Schema violations** (invalid structures)
- **Data integrity issues** (malformed data in Redis)

### Key Features

| Feature | Benefit |
|---------|---------|
| **Schema Validation** | No invalid data reaches Redis |
| **Type Checking** | Prevents WRONGTYPE errors before they occur |
| **Automatic Serialization** | JSON or msgpack with zero boilerplate |
| **TTL Management** | Automatic expiration with customizable per-key TTL |
| **IF.TTT Traceability** | Every payload carries full traceability headers |
| **Batch Operations** | VesiclePool reduces Redis round-trips |
| **Type Safety** | Compile-time type hints with runtime validation |

## Core Concepts

### VesiclePayload

A standardized data container with automatic ID generation and timestamp:

```python
@dataclass
class VesiclePayload:
    source_agent: str              # Which agent created this
    content: Dict[str, Any]        # The actual data
    schema_version: str = "1.0"    # Validation rules to apply
    ttl_seconds: int = 3600        # Expiration time
    payload_id: str = (auto-uuid)  # Unique identifier
    timestamp: str = (auto-iso)    # Creation time
    ttt_headers: Optional[Dict]    # Traceability info (v1.1+)
```

### VesicleTransport

Handles all Redis operations with automatic validation and type checking:

```python
transport = VesicleTransport(
    redis_host='localhost',
    redis_port=6379,
    default_ttl=3600
)

# Send payload
transport.send_to_redis(key, payload, operation='set')

# Fetch payload
fetched = transport.fetch_from_redis(key, operation='get')
```

### RedisKeyType

Enum for Redis data types with automatic type checking:

```
STRING   # Single value
LIST     # Ordered queue
HASH     # Field-value pairs
SET      # Unique members
ZSET     # Sorted set
STREAM   # Event stream
NONE     # Key doesn't exist
```

## Installation

### 1. Prerequisites

```bash
pip install redis>=5.0 pydantic>=2.5 msgpack>=1.0
```

### 2. Import

```python
from infrafabric.core.transport.vesicle import (
    VesiclePayload,
    VesicleTransport,
    VesiclePool,
    RedisKeyType,
)
```

### 3. Verify Redis Connection

```python
transport = VesicleTransport(redis_host='localhost', redis_port=6379)
print(transport.get_stats())
```

## Quick Start

### Example 1: Basic String Storage

```python
from infrafabric.core.transport.vesicle import VesiclePayload, VesicleTransport

# Initialize
transport = VesicleTransport()

# Create payload
payload = VesiclePayload(
    source_agent='gemini-librarian',
    content={'query': 'find architecture patterns', 'results': 42},
    ttl_seconds=3600
)

# Send to Redis (schema automatically validated)
transport.send_to_redis(key='query:latest', payload=payload, operation='set')

# Fetch from Redis (automatically deserialized)
fetched = transport.fetch_from_redis(key='query:latest', operation='get')
print(f"Source: {fetched.source_agent}")
print(f"Content: {fetched.content}")
```

### Example 2: Queue-Style List Operations

```python
# Push multiple items to a queue
for i in range(5):
    payload = VesiclePayload(
        source_agent=f'worker-{i}',
        content={'task': f'task-{i}'},
        ttl_seconds=1800
    )
    transport.send_to_redis(
        key='task:queue',
        payload=payload,
        operation='rpush'  # Right push
    )

# Fetch entire queue
queue_items = transport.fetch_from_redis(
    key='task:queue',
    operation='lrange'  # Get all items
)

for item in queue_items:
    print(f"{item.source_agent}: {item.content}")
```

### Example 3: Hash-Based Agent Registry

```python
# Store agent information as hash
for agent_name in ['sonnet', 'haiku', 'gemini']:
    payload = VesiclePayload(
        source_agent=agent_name,
        content={'role': 'worker', 'status': 'active'},
        ttl_seconds=7200
    )
    transport.send_to_redis(
        key='agents:registry',
        payload=payload,
        operation='hset'
    )

# Fetch all agents
agents = transport.fetch_from_redis(
    key='agents:registry',
    operation='hgetall'
)

for field_id, payload in agents.items():
    print(f"{payload.source_agent}: {payload.content['status']}")
```

### Example 4: Type-Safe Operations

```python
# Create as STRING
payload = VesiclePayload(source_agent='test', content={'type': 'string'})
transport.send_to_redis(key='mykey', payload=payload, operation='set')

# Try to use LIST operation (raises TypeError automatically)
try:
    transport.send_to_redis(key='mykey', payload=payload, operation='rpush')
except TypeError as e:
    print(f"✓ Type error caught: {e}")
    # Output: "Key 'mykey' is string, cannot use 'rpush' operation"
```

## API Reference

### VesiclePayload

#### Creating Payloads

```python
# Basic creation
payload = VesiclePayload(
    source_agent='my-agent',
    content={'key': 'value'},
)

# With custom TTL
payload = VesiclePayload(
    source_agent='my-agent',
    content={'key': 'value'},
    ttl_seconds=7200  # 2 hours
)

# With v1.1 schema and TTT headers
payload = VesiclePayload(
    source_agent='my-agent',
    content={'key': 'value'},
    schema_version='1.1',
    ttt_headers={
        'traceable_id': 'trace-0001',
        'transparent_lineage': ['step1', 'step2'],
        'trustworthy_signature': 'sig_hash'
    }
)
```

#### Serialization Methods

```python
# JSON serialization
json_str = payload.to_json()
restored = VesiclePayload.from_json(json_str)

# msgpack serialization (binary, more efficient)
msgpack_bytes = payload.to_msgpack()
restored = VesiclePayload.from_msgpack(msgpack_bytes)

# Dictionary conversion
payload_dict = payload.to_dict()
restored = VesiclePayload.from_dict(payload_dict)
```

#### Properties

```python
payload.payload_id        # UUID4 unique identifier
payload.timestamp         # ISO8601 creation time
payload.source_agent      # Agent identifier
payload.content          # Payload data (dict)
payload.schema_version   # "1.0" or "1.1"
payload.ttl_seconds      # Time-to-live in seconds
payload.ttt_headers      # Traceability headers (optional)
```

### VesicleTransport

#### Initialization

```python
transport = VesicleTransport(
    redis_host='localhost',      # Redis hostname
    redis_port=6379,             # Redis port
    redis_db=0,                  # Database number
    decode_responses=True,       # Return strings (vs bytes)
    default_ttl=3600             # Default TTL in seconds
)
```

#### Send Operations

```python
# STRING: Set a single value (overwrites)
transport.send_to_redis(
    key='key:name',
    payload=payload,
    operation='set',
    use_msgpack=False  # Use JSON (default)
)

# LIST: Push to right (queue-style FIFO)
transport.send_to_redis(
    key='queue:name',
    payload=payload,
    operation='rpush'
)

# LIST: Push to left (stack-style LIFO)
transport.send_to_redis(
    key='stack:name',
    payload=payload,
    operation='lpush'
)

# HASH: Store with field key (batch storage)
transport.send_to_redis(
    key='hash:name',
    payload=payload,
    operation='hset'  # Uses payload.payload_id as field
)

# SET: Add unique member
transport.send_to_redis(
    key='set:name',
    payload=payload,
    operation='sadd'
)
```

#### Fetch Operations

```python
# STRING: Get single value
payload = transport.fetch_from_redis(
    key='key:name',
    operation='get'
)

# LIST: Get specific index
payload = transport.fetch_from_redis(
    key='queue:name',
    operation='lindex',
    list_index=0
)

# LIST: Get range (all)
payloads = transport.fetch_from_redis(
    key='queue:name',
    operation='lrange'
)

# HASH: Get specific field
payload = transport.fetch_from_redis(
    key='hash:name',
    operation='hget',
    hash_field='field_name'
)

# HASH: Get all fields
payloads_dict = transport.fetch_from_redis(
    key='hash:name',
    operation='hgetall'
)

# SET: Get all members
payloads = transport.fetch_from_redis(
    key='set:name',
    operation='smembers'
)
```

#### Utility Operations

```python
# Check if key exists
if transport.key_exists('mykey'):
    print("Key found")

# Get key type
key_type = transport.get_key_type('mykey')
if key_type == RedisKeyType.STRING:
    print("This is a STRING key")

# Delete key
transport.delete_key('mykey')

# Get statistics
stats = transport.get_stats()
print(f"Redis version: {stats['redis_version']}")
print(f"Used memory: {stats['used_memory']}")

# Clear all keys in database (DANGEROUS)
count = transport.clear_all()
```

### VesiclePool

Batch operations for efficiency:

```python
pool = VesiclePool(transport)

# Queue multiple payloads
for i in range(100):
    payload = VesiclePayload(
        source_agent=f'agent-{i}',
        content={'index': i}
    )
    pool.add_payload('results:batch', payload, operation='rpush')

# Send all at once (1 round-trip instead of 100)
count = pool.flush()
print(f"Sent {count} payloads")
```

## Schema Validation

### "No Schema, No Write" Principle

Every payload is validated before being sent to Redis:

```python
# Valid: All required fields present
payload = VesiclePayload(
    source_agent='test',
    content={'data': 'test'}
)
# ✓ Schema validation passes

# Invalid: TTL out of range
try:
    payload = VesiclePayload(
        source_agent='test',
        content={},
        ttl_seconds=999999  # Max is 86400
    )
except ValueError as e:
    print(f"✗ Validation error: {e}")

# Invalid: Unknown schema version
try:
    payload = VesiclePayload(
        source_agent='test',
        content={},
        schema_version='9.9'
    )
except ValueError as e:
    print(f"✗ Validation error: {e}")
```

### Schema Versions

#### v1.0 (Current)

```json
{
  "payload_id": "uuid4",
  "timestamp": "iso8601",
  "source_agent": "string",
  "content": "object",
  "schema_version": "1.0",
  "ttl_seconds": "integer(1-86400)"
}
```

#### v1.1 (With TTT Headers)

```json
{
  "payload_id": "uuid4",
  "timestamp": "iso8601",
  "source_agent": "string",
  "content": "object",
  "schema_version": "1.1",
  "ttl_seconds": "integer(1-86400)",
  "ttt_headers": {
    "traceable_id": "string",
    "transparent_lineage": ["string"],
    "trustworthy_signature": "string"
  }
}
```

## Type Safety

### Preventing WRONGTYPE Errors

Redis has strict type rules. IF.VESICLE prevents violations:

```python
# Create STRING key
payload = VesiclePayload(source_agent='test', content={})
transport.send_to_redis('mykey', payload, operation='set')
# ✓ Key 'mykey' is now type: STRING

# Try to use LIST operation (PREVENTED)
try:
    transport.send_to_redis('mykey', payload, operation='rpush')
except TypeError as e:
    print(f"✓ Type error caught before Redis: {e}")
    # Output: "Key 'mykey' is string, cannot use 'rpush' operation"

# Correct way: Use STRING operation
transport.send_to_redis('mykey', payload, operation='set')
# ✓ Overwrites successfully (both STRING operations)
```

### Type Checking Enforces Consistency

```python
# Each key type has allowed operations

STRING:  set, get
LIST:    lpush, rpush, lindex, lrange
HASH:    hset, hget, hgetall
SET:     sadd, smembers
NONE:    any (creates new key with correct type)
```

## Examples

See `examples.py` for comprehensive examples:

1. **Basic String Storage** - Simple send/fetch
2. **Queue Operations** - FIFO queue patterns
3. **Hash Storage** - Multi-field objects
4. **Type Safety** - WRONGTYPE prevention
5. **Batch Operations** - VesiclePool efficiency
6. **Schema Validation** - Error handling
7. **TTT Headers** - Traceability
8. **msgpack Serialization** - Binary efficiency

Run examples:
```bash
python examples.py
```

## Error Handling

### Type Errors

```python
try:
    # Try LIST operation on STRING key
    transport.send_to_redis(key, payload, operation='rpush')
except TypeError as e:
    print(f"Type mismatch: {e}")
    # Handle gracefully
```

### Schema Validation Errors

```python
try:
    payload = VesiclePayload(
        source_agent='test',
        content={},
        ttl_seconds=999999  # Invalid
    )
except ValueError as e:
    print(f"Schema validation failed: {e}")
    # Handle gracefully
```

### Redis Connection Errors

```python
try:
    transport = VesicleTransport(redis_host='invalid_host')
except RuntimeError as e:
    print(f"Redis connection failed: {e}")
    # Handle gracefully
```

### Operation Errors

```python
try:
    result = transport.fetch_from_redis('mykey', operation='invalid')
except ValueError as e:
    print(f"Invalid operation: {e}")
```

## Performance Considerations

### 1. Use VesiclePool for Batch Operations

```python
# SLOW: 100 round-trips
for payload in payloads:
    transport.send_to_redis(key, payload, operation='rpush')

# FAST: 1 round-trip
pool = VesiclePool(transport)
for payload in payloads:
    pool.add_payload(key, payload, operation='rpush')
pool.flush()
```

### 2. Use msgpack for Large Payloads

```python
# JSON: Larger, slower
transport.send_to_redis(key, payload, operation='set', use_msgpack=False)

# msgpack: Compact, faster (for large objects)
transport.send_to_redis(key, payload, operation='set', use_msgpack=True)
```

### 3. Tune TTL Based on Usage

```python
# Short TTL: Quick cleanup, more memory efficient
payload = VesiclePayload(source_agent='test', content={}, ttl_seconds=300)

# Long TTL: Persistent storage
payload = VesiclePayload(source_agent='test', content={}, ttl_seconds=86400)
```

### 4. Use Appropriate Data Structure

```python
# Single value: STRING (fastest)
transport.send_to_redis(key, payload, operation='set')

# Queue: LIST (fast append/read)
transport.send_to_redis(key, payload, operation='rpush')

# Key-value pairs: HASH (good for many fields)
transport.send_to_redis(key, payload, operation='hset')

# Unique members: SET (good for membership tests)
transport.send_to_redis(key, payload, operation='sadd')
```

## Testing

Run unit tests:

```bash
pytest test_vesicle.py -v
```

Test coverage includes:
- Payload creation and validation
- All Redis operations (STRING, LIST, HASH, SET)
- Type safety and WRONGTYPE prevention
- Serialization (JSON and msgpack)
- Batch operations
- Error handling
- Schema validation

## Architecture

### Data Flow

```
Agent Code
    ↓
VesiclePayload (create)
    ↓
Schema Validation (No Schema, No Write)
    ↓
Type Checking (prevent WRONGTYPE)
    ↓
Serialization (JSON or msgpack)
    ↓
Redis Storage
    ↓
Deserialization
    ↓
Type Checking
    ↓
VesiclePayload (restored)
    ↓
Agent Code
```

### Directory Structure

```
core/transport/
├── __init__.py           # Package initialization
├── vesicle.py            # Main implementation
├── test_vesicle.py       # Unit tests
├── examples.py           # Usage examples
└── README.md             # This file
```

## Future Enhancements

- [ ] Support for Redis Streams (event-based operations)
- [ ] Compression (gzip for very large payloads)
- [ ] Connection pooling for multi-threaded applications
- [ ] Metrics/telemetry (operation counters, timing)
- [ ] Distributed transactions (atomic multi-key operations)
- [ ] Cache invalidation patterns (LRU, TTL-based)

## References

- **IF.TTT Framework** - Traceable, Transparent, Trustworthy principles
- **Redis Documentation** - https://redis.io/docs/
- **Extracellular Vesicles** - https://en.wikipedia.org/wiki/Extracellular_vesicle
- **Biological Metaphor** - Exercise-triggered brain growth through vesicle transport

## License

Part of InfraFabric v2.0 - Autonomous Infrastructure System

## Support

For issues or questions:
1. Check examples.py for usage patterns
2. Review test_vesicle.py for test cases
3. Check error messages (they include helpful context)
4. Verify Redis is running and accessible
