# IF.VESICLE Quick Reference

## Installation

```python
from infrafabric.core.transport.vesicle import VesiclePayload, VesicleTransport
```

## Basic Usage

### Create Transport
```python
transport = VesicleTransport(redis_host='localhost', redis_port=6379)
```

### Create Payload
```python
payload = VesiclePayload(
    source_agent='my-agent',
    content={'key': 'value'},
    ttl_seconds=3600
)
```

### Send to Redis
```python
transport.send_to_redis('mykey', payload, operation='set')
```

### Fetch from Redis
```python
fetched = transport.fetch_from_redis('mykey', operation='get')
print(fetched.content)
```

## Common Operations

### String Storage
```python
# Send
transport.send_to_redis(key='key:name', payload=payload, operation='set')

# Fetch
result = transport.fetch_from_redis(key='key:name', operation='get')
```

### Queue (FIFO)
```python
# Push
transport.send_to_redis(key='queue:name', payload=payload, operation='rpush')

# Get all
items = transport.fetch_from_redis(key='queue:name', operation='lrange')
```

### Hash Registry
```python
# Store
transport.send_to_redis(key='registry:name', payload=payload, operation='hset')

# Fetch all
items = transport.fetch_from_redis(key='registry:name', operation='hgetall')
```

### Set Members
```python
# Add
transport.send_to_redis(key='set:name', payload=payload, operation='sadd')

# Get all
items = transport.fetch_from_redis(key='set:name', operation='smembers')
```

## Batch Operations

```python
pool = VesiclePool(transport)

# Queue multiple
for i in range(100):
    payload = VesiclePayload(source_agent=f'agent-{i}', content={})
    pool.add_payload('queue', payload, operation='rpush')

# Send all at once (1 Redis call)
pool.flush()
```

## TTT Traceability (v1.1)

```python
payload = VesiclePayload(
    source_agent='agent-name',
    content={...},
    schema_version='1.1',
    ttt_headers={
        'traceable_id': 'trace-001',
        'transparent_lineage': ['step-1', 'step-2'],
        'trustworthy_signature': 'sig-hash'
    }
)
```

## Error Handling

### Schema Validation
```python
try:
    payload = VesiclePayload(source_agent='test', content={}, ttl_seconds=999999)
except ValueError as e:
    print(f"Invalid schema: {e}")
```

### Type Safety
```python
try:
    transport.send_to_redis(key='str_key', payload=payload, operation='rpush')
except TypeError as e:
    print(f"Type mismatch: {e}")
```

### Connection Error
```python
try:
    transport = VesicleTransport(redis_host='invalid_host')
except RuntimeError as e:
    print(f"Connection failed: {e}")
```

## Utilities

```python
# Check if key exists
if transport.key_exists('mykey'):
    print("Key found")

# Get key type
key_type = transport.get_key_type('mykey')

# Delete key
transport.delete_key('mykey')

# Get stats
stats = transport.get_stats()
```

## Schema Versions

### v1.0 (Default)
- Basic payload validation
- Required: payload_id, timestamp, source_agent, content, schema_version, ttl_seconds

### v1.1 (With Traceability)
- All v1.0 fields plus ttt_headers
- Use for decision lineage tracking

## Performance Tips

1. **Large Payloads**: Use msgpack
   ```python
   transport.send_to_redis(key, payload, operation='set', use_msgpack=True)
   ```

2. **Batch Operations**: Use VesiclePool
   ```python
   pool = VesiclePool(transport)
   # ... add many payloads ...
   pool.flush()  # 1 Redis call instead of 100
   ```

3. **Short-lived Data**: Use short TTL
   ```python
   payload = VesiclePayload(..., ttl_seconds=300)  # 5 minutes
   ```

4. **Pick Right Data Type**:
   - STRING for single values
   - LIST for queues
   - HASH for multi-field objects
   - SET for membership tests

## Testing

```bash
# Run all tests
pytest test_vesicle.py -v

# Run specific test
pytest test_vesicle.py::TestVesiclePayload -v

# With coverage
pytest test_vesicle.py --cov=vesicle
```

## Common Patterns

### Coordinator ↔ Workers Communication
```python
# Coordinator sends task
transport.send_to_redis('tasks:queue', task_payload, operation='rpush')

# Worker fetches task
task = transport.fetch_from_redis('tasks:queue', operation='lindex', list_index=0)
```

### Agent Registry
```python
# Register agent
transport.send_to_redis('agents:registry', agent_payload, operation='hset')

# List all agents
agents = transport.fetch_from_redis('agents:registry', operation='hgetall')
```

### Result Collection
```python
pool = VesiclePool(transport)
for result in results:
    payload = VesiclePayload(source_agent='worker', content=result)
    pool.add_payload('results:batch', payload, operation='rpush')
pool.flush()
```

## Troubleshooting

**Q: "Cannot connect to Redis"**
- Check: `redis-cli ping`
- Fix: Start Redis or verify host/port

**Q: "Key 'x' is string, cannot use 'rpush'"**
- Fix: Delete key and recreate, or use different key name

**Q: "msgpack not installed"**
- Fix: `pip install msgpack` OR use JSON (default)

**Q: "ttl_seconds must be 1-86400"**
- Fix: Use TTL between 1 second and 24 hours

**Q: Payload doesn't serialize**
- Fix: Ensure `content` is dict with JSON-serializable values

## Documentation

- **README.md** - Complete reference
- **examples.py** - 8 runnable examples
- **test_vesicle.py** - 60+ test cases
- **IMPLEMENTATION_SUMMARY.md** - Technical details

## Support

For issues:
1. Check error message (specific and helpful)
2. Review README.md or examples.py
3. Check test_vesicle.py for similar test case
4. Verify Redis is running and accessible

