# IF.LOGISTICS Quick Reference

Minimal reminders for dispatching Parcels through Redis with the LogisticsDispatcher.

## Imports

```python
from infrafabric.core.logistics import DispatchQueue, LogisticsDispatcher, Parcel, RedisKeyType
```

## Basic Dispatch

```python
dispatcher = LogisticsDispatcher(redis_host="localhost", redis_port=6379)
parcel = Parcel(origin="librarian", contents={"note": "hello"})

dispatcher.dispatch_to_redis("logistics:hello", parcel, operation="set")
restored = dispatcher.collect_from_redis("logistics:hello", operation="get")
print(restored.contents)
```

## Common Operations

```python
# STRING
dispatcher.dispatch_to_redis("key:name", parcel, operation="set")
dispatcher.collect_from_redis("key:name", operation="get")

# LIST (queue)
dispatcher.dispatch_to_redis("queue:name", parcel, operation="rpush")
dispatcher.collect_from_redis("queue:name", operation="lrange")

# HASH (registry)
dispatcher.dispatch_to_redis("registry:name", parcel, operation="hset")
dispatcher.collect_from_redis("registry:name", operation="hgetall")

# SET (membership)
dispatcher.dispatch_to_redis("set:name", parcel, operation="sadd")
dispatcher.collect_from_redis("set:name", operation="smembers")
```

## Batch Dispatch

```python
queue = DispatchQueue(dispatcher)
for i in range(10):
    queue.add_parcel("batch", Parcel(origin="worker", contents={"i": i}), operation="lpush")
queue.flush()
```

## Chain of Custody (v1.1)

```python
parcel = Parcel(
    origin="guardian",
    contents={"decision": "approve"},
    schema_version="1.1",
    chain_of_custody={
        "traceable_id": "trace-001",
        "transparent_lineage": ["draft", "review"],
        "trustworthy_signature": "sig-hash",
    },
)
```

## Validation & Safety

- "No Schema, No Dispatch" → schema validation runs on every write.
- Type guardrails → attempts to `lpush` into a HASH raise `TypeError`.
- Utilities: `key_exists`, `get_key_type`, `delete_key`, `clear_all`, `get_stats`.
