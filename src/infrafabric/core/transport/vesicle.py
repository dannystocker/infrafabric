#!/usr/bin/env python3
"""
IF.VESICLE v1.0 - Transport Container for Redis Operations
===========================================================

Role: Standardized wrapper for all Redis operations with schema validation,
type checking, and IF.TTT traceability headers.

Biological Metaphor:
  Just as extracellular vesicles (EVs) are cellular "message packets" carrying
  proteins, lipids, and genetic material across the blood-brain barrier,
  IF.VESICLE is the standardized container for all data flowing through Redis.

Core Philosophy: "No Schema, No Write"
  Every payload must be validated against a schema before storage.
  Every Redis operation must be type-checked to prevent WRONGTYPE errors.
  Every packet carries IF.TTT headers for traceability.

Responsibilities:
  1. VesiclePayload - Dataclass representing a single transport packet
  2. VesicleTransport - Core class handling all Redis operations
  3. Type checking before operations (prevent WRONGTYPE errors)
  4. Schema validation (enforce structure before writes)
  5. msgpack serialization for complex objects
  6. IF.TTT traceability headers (payload_id, source_agent, timestamp)

Usage:
  from infrafabric.core.transport.vesicle import VesicleTransport, VesiclePayload

  # Create transport instance
  transport = VesicleTransport(redis_host='localhost', redis_port=6379)

  # Create payload
  payload = VesiclePayload(
      source_agent='gemini-librarian',
      content={'query': 'find architecture patterns'},
      schema_version='1.0',
      ttl_seconds=3600
  )

  # Send to Redis with automatic type checking and schema validation
  transport.send_to_redis('queue:context', payload)

  # Fetch with automatic unpacking
  fetched = transport.fetch_from_redis('queue:context')
  print(fetched.content)  # Automatically deserialized
"""

import uuid
import json
import redis
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional, Union, List
from enum import Enum

# Optional msgpack support (for efficient binary serialization)
try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
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


class VesicleSchemaVersion(Enum):
    """Supported schema versions for payload validation"""
    V1_0 = "1.0"
    V1_1 = "1.1"


# =============================================================================
# SCHEMA DEFINITIONS (No Schema, No Write)
# =============================================================================

VESICLE_SCHEMA_V1_0 = {
    "type": "object",
    "required": ["payload_id", "timestamp", "source_agent", "content", "schema_version"],
    "properties": {
        "payload_id": {"type": "string", "pattern": "^[a-f0-9-]{36}$"},
        "timestamp": {"type": "string", "format": "iso8601"},
        "source_agent": {"type": "string", "minLength": 1, "maxLength": 255},
        "content": {"type": "object"},
        "schema_version": {"type": "string", "enum": ["1.0", "1.1"]},
        "ttl_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
    }
}

VESICLE_SCHEMA_V1_1 = {
    "type": "object",
    "required": [
        "payload_id", "timestamp", "source_agent", "content",
        "schema_version", "ttl_seconds"
    ],
    "properties": {
        "payload_id": {"type": "string", "pattern": "^[a-f0-9-]{36}$"},
        "timestamp": {"type": "string", "format": "iso8601"},
        "source_agent": {"type": "string", "minLength": 1, "maxLength": 255},
        "content": {"type": "object"},
        "schema_version": {"type": "string", "enum": ["1.0", "1.1"]},
        "ttl_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
        "ttt_headers": {
            "type": "object",
            "properties": {
                "traceable_id": {"type": "string"},
                "transparent_lineage": {"type": "array", "items": {"type": "string"}},
                "trustworthy_signature": {"type": "string"}
            }
        }
    }
}

SCHEMA_MAP = {
    "1.0": VESICLE_SCHEMA_V1_0,
    "1.1": VESICLE_SCHEMA_V1_1,
}


# =============================================================================
# VESICLE PAYLOAD
# =============================================================================

@dataclass
class VesiclePayload:
    """
    Transport container for Redis operations.

    Fields:
        payload_id: Unique identifier (UUID4) for traceability
        timestamp: ISO8601 creation timestamp
        source_agent: Originating agent identifier
        content: Arbitrary payload (must serialize to msgpack)
        schema_version: Version of this payload schema
        ttl_seconds: Time-to-live in seconds (max 86400)
        ttt_headers: IF.TTT traceability headers (optional, v1.1+)
    """
    source_agent: str
    content: Dict[str, Any]
    schema_version: str = "1.0"
    ttl_seconds: int = 3600
    payload_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    ttt_headers: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate payload after initialization"""
        if not 1 <= self.ttl_seconds <= 86400:
            raise ValueError(f"ttl_seconds must be 1-86400, got {self.ttl_seconds}")

        if self.schema_version not in SCHEMA_MAP:
            raise ValueError(f"Unknown schema_version: {self.schema_version}")

        if not isinstance(self.content, dict):
            raise TypeError("content must be a dictionary")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    def to_msgpack(self) -> bytes:
        """Convert to msgpack bytes (efficient for binary storage)"""
        if not HAS_MSGPACK:
            raise RuntimeError(
                "msgpack not installed. Install with: pip install msgpack"
            )
        return msgpack.packb(self.to_dict(), use_bin_type=True)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VesiclePayload':
        """Create from dictionary"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'VesiclePayload':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_msgpack(cls, data: bytes) -> 'VesiclePayload':
        """Create from msgpack bytes"""
        if not HAS_MSGPACK:
            raise RuntimeError(
                "msgpack not installed. Install with: pip install msgpack"
            )
        decoded = msgpack.unpackb(data, raw=False)
        return cls.from_dict(decoded)


# =============================================================================
# VESICLE TRANSPORT
# =============================================================================

class VesicleTransport:
    """
    Core transport layer for Redis operations with schema validation,
    type checking, and IF.TTT traceability.

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

    def __init__(self,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 decode_responses: bool = True,
                 default_ttl: int = 3600):
        """
        Initialize transport layer.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            decode_responses: Decode responses to strings (vs bytes)
            default_ttl: Default TTL in seconds for payloads
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=decode_responses
        )
        self.default_ttl = default_ttl
        self.transport_id = f"vesicle_{uuid.uuid4().hex[:8]}"

        # Verify connection
        try:
            self.redis_client.ping()
            print(f"✓ VesicleTransport initialized: {self.transport_id}")
            print(f"  Redis: {redis_host}:{redis_port}/{redis_db}")
        except redis.ConnectionError as e:
            raise RuntimeError(f"Cannot connect to Redis: {e}")

    def _get_redis_type(self, key: str) -> RedisKeyType:
        """
        Determine the type of a Redis key.

        Returns:
            RedisKeyType enum value
        """
        key_type = self.redis_client.type(key)

        if key_type == b'none' or key_type == 'none':
            return RedisKeyType.NONE
        elif key_type == b'string' or key_type == 'string':
            return RedisKeyType.STRING
        elif key_type == b'hash' or key_type == 'hash':
            return RedisKeyType.HASH
        elif key_type == b'list' or key_type == 'list':
            return RedisKeyType.LIST
        elif key_type == b'set' or key_type == 'set':
            return RedisKeyType.SET
        elif key_type == b'zset' or key_type == 'zset':
            return RedisKeyType.ZSET
        elif key_type == b'stream' or key_type == 'stream':
            return RedisKeyType.STREAM
        else:
            raise ValueError(f"Unknown Redis type: {key_type}")

    def _validate_schema(self, payload: VesiclePayload) -> bool:
        """
        Validate payload against schema.

        Implements: "No Schema, No Write"

        Args:
            payload: Payload to validate

        Returns:
            True if valid

        Raises:
            ValueError if validation fails
        """
        schema = SCHEMA_MAP.get(payload.schema_version)
        if not schema:
            raise ValueError(f"Unknown schema_version: {payload.schema_version}")

        # Check required fields
        required = schema.get("required", [])
        payload_dict = payload.to_dict()

        for field_name in required:
            if field_name not in payload_dict:
                raise ValueError(f"Missing required field: {field_name}")

        # Validate field types
        properties = schema.get("properties", {})
        for field_name, field_value in payload_dict.items():
            if field_name not in properties:
                continue

            prop_schema = properties[field_name]
            field_type = prop_schema.get("type")

            if field_type == "string" and not isinstance(field_value, str):
                raise TypeError(
                    f"Field '{field_name}' must be string, got {type(field_value)}"
                )
            elif field_type == "object" and not isinstance(field_value, dict):
                raise TypeError(
                    f"Field '{field_name}' must be object, got {type(field_value)}"
                )
            elif field_type == "integer" and not isinstance(field_value, int):
                raise TypeError(
                    f"Field '{field_name}' must be integer, got {type(field_value)}"
                )

        return True

    # =========================================================================
    # CORE OPERATIONS: SEND TO REDIS
    # =========================================================================

    def send_to_redis(self,
                      key: str,
                      payload: VesiclePayload,
                      operation: str = "set",
                      use_msgpack: bool = False) -> bool:
        """
        Send payload to Redis with schema validation and type checking.

        Operations:
        - 'set': STRING key (overwrites)
        - 'lpush': LIST key (push to left)
        - 'rpush': LIST key (push to right)
        - 'hset': HASH key (field-based storage)
        - 'sadd': SET key (set membership)

        Args:
            key: Redis key
            payload: VesiclePayload to send
            operation: Redis operation type
            use_msgpack: Use msgpack serialization (vs JSON)

        Returns:
            True if successful

        Raises:
            ValueError: Schema validation failed
            TypeError: Type mismatch
            redis.RedisError: Redis operation failed
        """
        # Validate schema (No Schema, No Write)
        self._validate_schema(payload)

        # Serialize payload
        if use_msgpack:
            if not HAS_MSGPACK:
                raise RuntimeError(
                    "msgpack not installed. Install with: pip install msgpack"
                )
            serialized = payload.to_msgpack()
        else:
            serialized = payload.to_json()

        try:
            if operation == "set":
                # STRING operation: check if key exists and is correct type
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.STRING]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'set' operation"
                    )

                self.redis_client.set(key, serialized, ex=payload.ttl_seconds)
                return True

            elif operation == "lpush":
                # LIST operation: check if key is list or none
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'lpush' operation"
                    )

                self.redis_client.lpush(key, serialized)
                self.redis_client.expire(key, payload.ttl_seconds)
                return True

            elif operation == "rpush":
                # LIST operation: check if key is list or none
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'rpush' operation"
                    )

                self.redis_client.rpush(key, serialized)
                self.redis_client.expire(key, payload.ttl_seconds)
                return True

            elif operation == "hset":
                # HASH operation: check if key is hash or none
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.HASH]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'hset' operation"
                    )

                # Use payload_id as field name for hash
                field_name = payload.payload_id
                self.redis_client.hset(key, field_name, serialized)
                self.redis_client.expire(key, payload.ttl_seconds)
                return True

            elif operation == "sadd":
                # SET operation: check if key is set or none
                key_type = self._get_redis_type(key)
                if key_type not in [RedisKeyType.NONE, RedisKeyType.SET]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'sadd' operation"
                    )

                self.redis_client.sadd(key, serialized)
                self.redis_client.expire(key, payload.ttl_seconds)
                return True

            else:
                raise ValueError(f"Unknown operation: {operation}")

        except (redis.RedisError, redis.ConnectionError) as e:
            raise RuntimeError(f"Redis operation failed: {e}")

    # =========================================================================
    # CORE OPERATIONS: FETCH FROM REDIS
    # =========================================================================

    def fetch_from_redis(self,
                        key: str,
                        operation: str = "get",
                        use_msgpack: bool = False,
                        list_index: Optional[int] = None,
                        hash_field: Optional[str] = None) -> Optional[VesiclePayload]:
        """
        Fetch payload from Redis with automatic type checking and deserialization.

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
            VesiclePayload or None if key doesn't exist

        Raises:
            TypeError: Key type mismatch
            redis.RedisError: Redis operation failed
        """
        try:
            key_type = self._get_redis_type(key)

            if operation == "get":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.STRING]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'get' operation"
                    )

                data = self.redis_client.get(key)
                if data is None:
                    return None

                if use_msgpack:
                    return VesiclePayload.from_msgpack(data)
                else:
                    return VesiclePayload.from_json(data)

            elif operation == "lindex":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'lindex' operation"
                    )

                if list_index is None:
                    raise ValueError("list_index required for 'lindex' operation")

                data = self.redis_client.lindex(key, list_index)
                if data is None:
                    return None

                if use_msgpack:
                    return VesiclePayload.from_msgpack(data)
                else:
                    return VesiclePayload.from_json(data)

            elif operation == "lrange":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.LIST]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'lrange' operation"
                    )

                start = list_index if list_index is not None else 0
                data_list = self.redis_client.lrange(key, start, -1)

                results = []
                for data in data_list:
                    if use_msgpack:
                        payload = VesiclePayload.from_msgpack(data)
                    else:
                        payload = VesiclePayload.from_json(data)
                    results.append(payload)

                return results if results else None

            elif operation == "hget":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.HASH]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'hget' operation"
                    )

                if hash_field is None:
                    raise ValueError("hash_field required for 'hget' operation")

                data = self.redis_client.hget(key, hash_field)
                if data is None:
                    return None

                if use_msgpack:
                    return VesiclePayload.from_msgpack(data)
                else:
                    return VesiclePayload.from_json(data)

            elif operation == "hgetall":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.HASH]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'hgetall' operation"
                    )

                data_dict = self.redis_client.hgetall(key)
                if not data_dict:
                    return None

                results = {}
                for field, data in data_dict.items():
                    if use_msgpack:
                        payload = VesiclePayload.from_msgpack(data)
                    else:
                        payload = VesiclePayload.from_json(data)
                    results[field] = payload

                return results

            elif operation == "smembers":
                if key_type not in [RedisKeyType.NONE, RedisKeyType.SET]:
                    raise TypeError(
                        f"Key '{key}' is {key_type.value}, cannot use 'smembers' operation"
                    )

                data_set = self.redis_client.smembers(key)
                if not data_set:
                    return None

                results = []
                for data in data_set:
                    if use_msgpack:
                        payload = VesiclePayload.from_msgpack(data)
                    else:
                        payload = VesiclePayload.from_json(data)
                    results.append(payload)

                return results

            else:
                raise ValueError(f"Unknown operation: {operation}")

        except (redis.RedisError, redis.ConnectionError) as e:
            raise RuntimeError(f"Redis operation failed: {e}")

    # =========================================================================
    # UTILITY OPERATIONS
    # =========================================================================

    def key_exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        return self.redis_client.exists(key) > 0

    def get_key_type(self, key: str) -> RedisKeyType:
        """Get the type of a Redis key"""
        return self._get_redis_type(key)

    def delete_key(self, key: str) -> bool:
        """Delete a key from Redis"""
        return self.redis_client.delete(key) > 0

    def clear_all(self) -> int:
        """Clear all keys from current Redis database (DANGEROUS)"""
        return self.redis_client.flushdb()

    def get_stats(self) -> Dict[str, Any]:
        """Get transport statistics"""
        info = self.redis_client.info()
        return {
            "transport_id": self.transport_id,
            "redis_version": info.get("redis_version"),
            "connected_clients": info.get("connected_clients"),
            "used_memory": info.get("used_memory_human"),
            "total_commands_processed": info.get("total_commands_processed"),
            "default_ttl": self.default_ttl,
        }


# =============================================================================
# VESICLE BATCH OPERATIONS (for efficiency)
# =============================================================================

class VesiclePool:
    """
    Batch operations for multiple payloads (reduces Redis round-trips).

    Usage:
        pool = VesiclePool(transport)
        pool.add_payload(key1, payload1)
        pool.add_payload(key2, payload2)
        pool.flush()  # Sends all at once
    """

    def __init__(self, transport: VesicleTransport):
        self.transport = transport
        self.pending: List[tuple] = []

    def add_payload(self,
                    key: str,
                    payload: VesiclePayload,
                    operation: str = "set") -> None:
        """Queue payload for batch send"""
        self.pending.append((key, payload, operation))

    def flush(self) -> int:
        """Send all queued payloads, return count"""
        count = 0
        for key, payload, operation in self.pending:
            self.transport.send_to_redis(key, payload, operation=operation)
            count += 1
        self.pending.clear()
        return count

    def __len__(self) -> int:
        return len(self.pending)
