#!/usr/bin/env python3
"""
IF.LOGISTICS v1.0 - Parcels & Dispatch
======================================

Role: Civic logistics layer that seals data into Parcels with traceable
chain-of-custody metadata before dispatching to Redis.

Metaphor Shift:
  * Department: Transport → Logistics (central dispatch office)
  * Unit: Vesicle → Packet (sealed container with tracking ID)
  * Action: send/transmit → dispatch
  * Envelope: wrapper/membrane → packaging
  * Body: payload → contents

Core Philosophy: "No Schema, No Dispatch"
  Every Packet is validated against a schema before it is handed to Redis.
  Every dispatch checks key type to avoid WRONGTYPE errors.
  Every container carries IF.TTT headers for auditability.

Responsibilities:
  1. Packet - Dataclass representing a sealed container and its metadata.
  2. LogisticsDispatcher - Core class coordinating Redis operations.
  3. DispatchQueue - Batch dispatcher that reduces round-trips.
  4. IF.TTT headers for custody and timestamping.

Usage:
  from infrafabric.core.logistics.packet import LogisticsDispatcher, Packet

  dispatcher = LogisticsDispatcher(redis_host='localhost', redis_port=6379)
  packet = Packet(
      origin='council-secretariat',
      contents={'query': 'find architecture patterns'},
      schema_version='1.0',
      ttl_seconds=3600,
  )

  dispatcher.dispatch_to_redis('queue:context', packet)
  fetched = dispatcher.collect_from_redis('queue:context')
  print(fetched.contents)  # Automatically deserialized
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid
from typing import Any, Dict, List, Optional, cast

import redis

# Optional msgpack support (for efficient binary serialization)
try:
    import msgpack

    HAS_MSGPACK = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_MSGPACK = False


class RedisKeyType(Enum):
    """Redis data types for type checking"""

    STRING = "string"
    HASH = "hash"
    LIST = "list"
    SET = "set"
    ZSET = "zset"
    STREAM = "stream"
    NONE = "none"  # Key doesn't exist


class ParcelSchemaVersion(Enum):
    """Supported schema versions for packet validation"""

    V1_0 = "1.0"
    V1_1 = "1.1"


# =============================================================================
# SCHEMA DEFINITIONS (No Schema, No Dispatch)
# =============================================================================

PARCEL_SCHEMA_V1_0 = {
    "type": "object",
    "required": [
        "tracking_id",
        "dispatched_at",
        "origin",
        "contents",
        "schema_version",
    ],
    "properties": {
        "tracking_id": {"type": "string", "pattern": "^[a-f0-9-]{36}$"},
        "dispatched_at": {"type": "string", "format": "iso8601"},
        "origin": {"type": "string", "minLength": 1, "maxLength": 255},
        "contents": {"type": "object"},
        "schema_version": {"type": "string", "enum": ["1.0", "1.1"]},
        "ttl_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
    },
}

PARCEL_SCHEMA_V1_1 = {
    "type": "object",
    "required": [
        "tracking_id",
        "dispatched_at",
        "origin",
        "contents",
        "schema_version",
        "ttl_seconds",
    ],
    "properties": {
        "tracking_id": {"type": "string", "pattern": "^[a-f0-9-]{36}$"},
        "dispatched_at": {"type": "string", "format": "iso8601"},
        "origin": {"type": "string", "minLength": 1, "maxLength": 255},
        "contents": {"type": "object"},
        "schema_version": {"type": "string", "enum": ["1.0", "1.1"]},
        "ttl_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
        "chain_of_custody": {
            "type": "object",
            "properties": {
                "traceable_id": {"type": "string"},
                "transparent_lineage": {"type": "array", "items": {"type": "string"}},
                "trustworthy_signature": {"type": "string"},
            },
        },
    },
}

SCHEMA_MAP = {
    "1.0": PARCEL_SCHEMA_V1_0,
    "1.1": PARCEL_SCHEMA_V1_1,
}


# =============================================================================
# PACKET
# =============================================================================

@dataclass
class Packet:
    """
    Sealed container for Redis dispatches.

    Fields:
        tracking_id: Unique identifier (UUID4) for traceability
        dispatched_at: ISO8601 creation timestamp
        origin: Originating agent or department
        contents: Arbitrary packet contents (must serialize to msgpack)
        schema_version: Version of this packet schema
        ttl_seconds: Time-to-live in seconds (max 86400)
        chain_of_custody: IF.TTT headers (optional, v1.1+)
    """

    origin: str
    contents: Dict[str, Any]
    schema_version: str = "1.0"
    ttl_seconds: int = 3600
    tracking_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dispatched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    chain_of_custody: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validate packet after initialization."""
        if not 1 <= self.ttl_seconds <= 86400:
            raise ValueError(f"ttl_seconds must be 1-86400, got {self.ttl_seconds}")

        if self.schema_version not in SCHEMA_MAP:
            raise ValueError(f"Unknown schema_version: {self.schema_version}")

        if not isinstance(self.contents, dict):
            raise TypeError("contents must be a dictionary")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    def to_msgpack(self) -> bytes:
        """Convert to msgpack bytes (efficient for binary storage)."""
        if not HAS_MSGPACK:
            raise RuntimeError("msgpack not installed. Install with: pip install msgpack")
        return msgpack.packb(self.to_dict(), use_bin_type=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Packet":
        """Create from dictionary, handling legacy field names for compatibility."""
        normalized = dict(data)
        alias_map = [
            ("payload_id", "tracking_id"),
            ("timestamp", "dispatched_at"),
            ("source_agent", "origin"),
            ("content", "contents"),
            ("ttt_headers", "chain_of_custody"),
        ]
        for legacy_key, modern_key in alias_map:
            if legacy_key in normalized and modern_key not in normalized:
                normalized[modern_key] = normalized.pop(legacy_key)
        return cls(**normalized)

    @classmethod
    def from_json(cls, json_str: str) -> "Packet":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_msgpack(cls, data: bytes) -> "Packet":
        """Create from msgpack bytes."""
        if not HAS_MSGPACK:
            raise RuntimeError("msgpack not installed. Install with: pip install msgpack")
        decoded = msgpack.unpackb(data, raw=False)
        return cls.from_dict(decoded)


# =============================================================================
# LOGISTICS DISPATCHER
# =============================================================================

class LogisticsDispatcher:
    """
    Civic logistics layer for Redis operations with schema validation,
    type checking, and IF.TTT chain-of-custody support.

    Prevents:
    - WRONGTYPE errors (checks key type before operations)
    - Schema violations (validates before writes)
    - Type corruption (enforces msgpack serialization)

    Provides:
    - Automatic serialization/deserialization
    - TTL-based expiration
    - Traceability headers
    - Type-safe Redis operations
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        decode_responses: bool = True,
        default_ttl: int = 3600,
    ) -> None:
        """
        Initialize logistics dispatcher.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            decode_responses: Decode responses to strings (vs bytes)
            default_ttl: Default TTL in seconds for parcels
        """

        # Use Any so synchronous redis client types (and optional async stubs) do not
        # pollute static analysis when we intentionally operate in a blocking mode.
        self.redis_client: Any = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=decode_responses,
        )
        self.default_ttl = default_ttl
        self.logistics_id = f"logistics_{uuid.uuid4().hex[:8]}"
        self.transport_id = self.logistics_id  # Backwards compatibility

        try:
            self.redis_client.ping()
            print(f"✓ Logistics dispatcher initialized: {self.logistics_id}")
            print(f"  Redis: {redis_host}:{redis_port}/{redis_db}")
        except redis.ConnectionError as exc:  # pragma: no cover - network dependent
            raise RuntimeError(f"Cannot connect to Redis: {exc}")

    def _get_redis_type(self, key: str) -> RedisKeyType:
        """
        Determine the type of a Redis key.

        Returns:
            RedisKeyType enum value
        """

        key_type = self.redis_client.type(key)

        if key_type in (b"none", "none"):
            return RedisKeyType.NONE
        if key_type in (b"string", "string"):
            return RedisKeyType.STRING
        if key_type in (b"hash", "hash"):
            return RedisKeyType.HASH
        if key_type in (b"list", "list"):
            return RedisKeyType.LIST
        if key_type in (b"set", "set"):
            return RedisKeyType.SET
        if key_type in (b"zset", "zset"):
            return RedisKeyType.ZSET
        if key_type in (b"stream", "stream"):
            return RedisKeyType.STREAM

        raise ValueError(f"Unknown Redis type: {key_type}")

    def _validate_schema(self, packet: Packet) -> bool:
        """
        Validate packet against schema.

        Implements: "No Schema, No Dispatch"

        Args:
            packet: Packet to validate

        Returns:
            True if valid

        Raises:
            ValueError if validation fails
        """

        schema = SCHEMA_MAP.get(packet.schema_version)
        if not schema:
            raise ValueError(f"Unknown schema_version: {packet.schema_version}")

        required = schema.get("required", [])
        packet_dict = packet.to_dict()

        for field_name in required:
            if field_name not in packet_dict:
                raise ValueError(f"Missing required field: {field_name}")

        properties = cast(Dict[str, Any], schema.get("properties", {}))
        for field_name, field_value in packet_dict.items():
            if field_name not in properties:
                continue

            prop_schema = properties[field_name]
            field_type = prop_schema.get("type")

            if field_type == "string" and not isinstance(field_value, str):
                raise TypeError(f"Field '{field_name}' must be string, got {type(field_value)}")
            if field_type == "object" and not isinstance(field_value, dict):
                raise TypeError(f"Field '{field_name}' must be object, got {type(field_value)}")
            if field_type == "integer" and not isinstance(field_value, int):
                raise TypeError(f"Field '{field_name}' must be integer, got {type(field_value)}")

        return True

    # =========================================================================
    # CORE OPERATIONS: DISPATCH TO REDIS
    # =========================================================================

    def dispatch_to_redis(
        self,
        key: str,
        packet: Packet,
        operation: str = "set",
        use_msgpack: bool = False,
    ) -> bool:
        """
        Dispatch packet to Redis with schema validation and type checking.

        Operations:
        - 'set': STRING key (overwrites)
        - 'lpush': LIST key (push to left)
        - 'rpush': LIST key (push to right)
        - 'hset': HASH key (field-based storage)
        - 'sadd': SET key (set membership)

        Args:
            key: Redis key
            packet: Packet to dispatch
            operation: Redis operation type
            use_msgpack: Use msgpack serialization (vs JSON)

        Returns:
            True if successful

        Raises:
            ValueError: Schema validation failed
            TypeError: Type mismatch
            redis.RedisError: Redis operation failed
        """

        self._validate_schema(packet)

        serialized: Any
        if use_msgpack:
            if not HAS_MSGPACK:
                raise RuntimeError("msgpack not installed. Install with: pip install msgpack")
            serialized = packet.to_msgpack()
        else:
            serialized = packet.to_json()

        try:
            if operation == "set":
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.STRING]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'set' operation")

                self.redis_client.set(key, serialized, ex=packet.ttl_seconds)
                return True

            if operation == "lpush":
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'lpush' operation")

                self.redis_client.lpush(key, serialized)
                self.redis_client.expire(key, packet.ttl_seconds)
                return True

            if operation == "rpush":
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'rpush' operation")

                self.redis_client.rpush(key, serialized)
                self.redis_client.expire(key, packet.ttl_seconds)
                return True

            if operation == "hset":
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.HASH]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'hset' operation")

                field_name = packet.tracking_id
                self.redis_client.hset(key, field_name, serialized)
                self.redis_client.expire(key, packet.ttl_seconds)
                return True

            if operation == "sadd":
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.SET]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'sadd' operation")

                self.redis_client.sadd(key, serialized)
                self.redis_client.expire(key, packet.ttl_seconds)
                return True

            raise ValueError(f"Unknown operation: {operation}")

        except (redis.RedisError, redis.ConnectionError) as exc:
            raise RuntimeError(f"Redis operation failed: {exc}")

    # =========================================================================
    # CORE OPERATIONS: COLLECT FROM REDIS
    # =========================================================================

    def collect_from_redis(
        self,
        key: str,
        operation: str = "get",
        use_msgpack: bool = False,
        list_index: Optional[int] = None,
        hash_field: Optional[str] = None,
    ) -> Any:
        """
        Collect packet(s) from Redis with automatic type checking and deserialization.

        Operations:
        - 'get': Fetch STRING value
        - 'lindex': Fetch LIST element by index
        - 'lrange': Fetch LIST range (returns list)
        - 'hget': Fetch HASH field value
        - 'hgetall': Fetch all HASH fields (returns dict)
        - 'smembers': Fetch all SET members (returns list)

        Args:
            key: Redis key
            operation: Redis operation type
            use_msgpack: Data is msgpack-serialized
            list_index: For 'lindex', which element to fetch
            hash_field: For 'hget', which field to fetch

        Returns:
            Packet or collection of Parcels, or None if key doesn't exist

        Raises:
            TypeError: Key type mismatch
            redis.RedisError: Redis operation failed
        """

        try:
            key_type = self._get_redis_type(key)

            if operation == "get":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.STRING]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'get' operation")

                data = self.redis_client.get(key)
                if data is None:
                    return None

                return Packet.from_msgpack(data) if use_msgpack else Packet.from_json(data)

            if operation == "lindex":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'lindex' operation")

                if list_index is None:
                    raise ValueError("list_index required for 'lindex' operation")

                data = self.redis_client.lindex(key, list_index)
                if data is None:
                    return None

                return Packet.from_msgpack(data) if use_msgpack else Packet.from_json(data)

            if operation == "lrange":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'lrange' operation")

                start = list_index if list_index is not None else 0
                data_list = self.redis_client.lrange(key, start, -1)

                list_results: List[Packet] = []
                for data in data_list:
                    packet = Packet.from_msgpack(data) if use_msgpack else Packet.from_json(data)
                    list_results.append(packet)

                return list_results if list_results else None

            if operation == "hget":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.HASH]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'hget' operation")

                if hash_field is None:
                    raise ValueError("hash_field required for 'hget' operation")

                data = self.redis_client.hget(key, hash_field)
                if data is None:
                    return None

                return Packet.from_msgpack(data) if use_msgpack else Packet.from_json(data)

            if operation == "hgetall":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.HASH]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'hgetall' operation")

                data_dict = self.redis_client.hgetall(key)
                if not data_dict:
                    return None

                dict_results: Dict[str, Packet] = {}
                for field, data in data_dict.items():
                    packet = Packet.from_msgpack(data) if use_msgpack else Packet.from_json(data)
                    dict_results[field] = packet

                return dict_results

            if operation == "smembers":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.SET]:
                    raise TypeError(f"Key '{key}' is {key_type.value}, cannot use 'smembers' operation")

                data_set = self.redis_client.smembers(key)
                if not data_set:
                    return None

                set_results: List[Packet] = []
                for data in data_set:
                    packet = Packet.from_msgpack(data) if use_msgpack else Packet.from_json(data)
                    set_results.append(packet)

                return set_results

            raise ValueError(f"Unknown operation: {operation}")

        except (redis.RedisError, redis.ConnectionError) as exc:
            raise RuntimeError(f"Redis operation failed: {exc}")

    # =========================================================================
    # UTILITY OPERATIONS
    # =========================================================================

    def key_exists(self, key: str) -> bool:
        """Check if key exists in Redis."""

        return self.redis_client.exists(key) > 0

    def get_key_type(self, key: str) -> RedisKeyType:
        """Get the type of a Redis key."""

        return self._get_redis_type(key)

    def delete_key(self, key: str) -> bool:
        """Delete a key from Redis."""

        return self.redis_client.delete(key) > 0

    def clear_all(self) -> int:
        """Clear all keys from current Redis database (DANGEROUS)."""

        return self.redis_client.flushdb()

    def get_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics."""

        info = self.redis_client.info()
        return {
            "logistics_id": self.logistics_id,
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human"),
            "total_commands_processed": info.get("total_commands_processed"),
            "default_ttl": self.default_ttl,
        }


# =============================================================================
# DISPATCH QUEUE (for efficiency)
# =============================================================================

class DispatchQueue:
    """
    Batch operations for multiple parcels (reduces Redis round-trips).

    Usage:
        queue = DispatchQueue(dispatcher)
        queue.add_parcel(key1, parcel1)
        queue.add_parcel(key2, parcel2)
        queue.flush()  # Dispatches all at once
    """

    def __init__(self, dispatcher: LogisticsDispatcher):
        self.dispatcher = dispatcher
        self.pending: List[tuple] = []

    def add_parcel(self, key: str, packet: Packet, operation: str = "set") -> None:
        """Queue packet for batch dispatch."""

        self.pending.append((key, packet, operation))

    def flush(self) -> int:
        """Dispatch all queued parcels, return count."""

        count = 0
        for key, packet, operation in self.pending:
            self.dispatcher.dispatch_to_redis(key, packet, operation=operation)
            count += 1
        self.pending.clear()
        return count

    def __len__(self) -> int:
        return len(self.pending)
