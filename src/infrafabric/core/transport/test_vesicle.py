#!/usr/bin/env python3
"""
Unit tests for IF.VESICLE transport layer

Run with: python -m pytest test_vesicle.py -v
"""

import pytest
import json
import redis
from datetime import datetime
from vesicle import (
    VesiclePayload,
    VesicleTransport,
    VesiclePool,
    RedisKeyType,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def redis_client():
    """Get a Redis client for testing"""
    try:
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=15,  # Use database 15 for testing
            decode_responses=True
        )
        client.ping()
        yield client
        client.flushdb()  # Cleanup after tests
    except redis.ConnectionError:
        pytest.skip("Redis not available")


@pytest.fixture
def transport(redis_client):
    """Get a VesicleTransport instance"""
    return VesicleTransport(
        redis_host='localhost',
        redis_port=6379,
        redis_db=15,
        decode_responses=True
    )


@pytest.fixture
def simple_payload():
    """Create a simple test payload"""
    return VesiclePayload(
        source_agent='test-agent',
        content={'test': 'data', 'value': 42},
        schema_version='1.0',
        ttl_seconds=3600
    )


# =============================================================================
# PAYLOAD TESTS
# =============================================================================

class TestVesiclePayload:
    """Tests for VesiclePayload dataclass"""

    def test_payload_creation(self):
        """Test basic payload creation"""
        payload = VesiclePayload(
            source_agent='test-agent',
            content={'key': 'value'}
        )
        assert payload.source_agent == 'test-agent'
        assert payload.content == {'key': 'value'}
        assert payload.schema_version == '1.0'
        assert payload.ttl_seconds == 3600

    def test_payload_id_generation(self):
        """Test unique payload ID generation"""
        payload1 = VesiclePayload(
            source_agent='agent1',
            content={}
        )
        payload2 = VesiclePayload(
            source_agent='agent2',
            content={}
        )
        assert payload1.payload_id != payload2.payload_id
        assert len(payload1.payload_id) == 36  # UUID4 format

    def test_payload_timestamp_generation(self):
        """Test timestamp is generated"""
        payload = VesiclePayload(
            source_agent='test',
            content={}
        )
        # Should be valid ISO format
        datetime.fromisoformat(payload.timestamp)

    def test_invalid_ttl_too_high(self):
        """Test TTL validation (max 86400)"""
        with pytest.raises(ValueError, match="ttl_seconds must be 1-86400"):
            VesiclePayload(
                source_agent='test',
                content={},
                ttl_seconds=999999
            )

    def test_invalid_ttl_too_low(self):
        """Test TTL validation (min 1)"""
        with pytest.raises(ValueError, match="ttl_seconds must be 1-86400"):
            VesiclePayload(
                source_agent='test',
                content={},
                ttl_seconds=0
            )

    def test_invalid_schema_version(self):
        """Test schema version validation"""
        with pytest.raises(ValueError, match="Unknown schema_version"):
            VesiclePayload(
                source_agent='test',
                content={},
                schema_version='9.9'
            )

    def test_invalid_content_type(self):
        """Test content must be dict"""
        with pytest.raises(TypeError, match="content must be a dictionary"):
            VesiclePayload(
                source_agent='test',
                content="not a dict"
            )

    def test_payload_to_dict(self):
        """Test conversion to dictionary"""
        payload = VesiclePayload(
            source_agent='test',
            content={'key': 'value'},
            schema_version='1.0'
        )
        payload_dict = payload.to_dict()
        assert isinstance(payload_dict, dict)
        assert payload_dict['source_agent'] == 'test'
        assert payload_dict['content'] == {'key': 'value'}

    def test_payload_to_json(self):
        """Test conversion to JSON"""
        payload = VesiclePayload(
            source_agent='test',
            content={'key': 'value'}
        )
        json_str = payload.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed['source_agent'] == 'test'

    def test_payload_to_msgpack(self):
        """Test conversion to msgpack"""
        payload = VesiclePayload(
            source_agent='test',
            content={'key': 'value'}
        )
        msgpack_bytes = payload.to_msgpack()
        assert isinstance(msgpack_bytes, bytes)

    def test_payload_from_json(self):
        """Test creation from JSON"""
        original = VesiclePayload(
            source_agent='test',
            content={'key': 'value'}
        )
        json_str = original.to_json()
        restored = VesiclePayload.from_json(json_str)
        assert restored.source_agent == original.source_agent
        assert restored.content == original.content

    def test_payload_from_msgpack(self):
        """Test creation from msgpack"""
        original = VesiclePayload(
            source_agent='test',
            content={'key': 'value'}
        )
        msgpack_bytes = original.to_msgpack()
        restored = VesiclePayload.from_msgpack(msgpack_bytes)
        assert restored.source_agent == original.source_agent
        assert restored.content == original.content


# =============================================================================
# TRANSPORT TESTS
# =============================================================================

class TestVesicleTransport:
    """Tests for VesicleTransport class"""

    def test_transport_initialization(self, transport):
        """Test transport initializes correctly"""
        assert transport is not None
        assert transport.transport_id.startswith('vesicle_')
        assert transport.default_ttl == 3600

    def test_transport_redis_connection(self, transport):
        """Test Redis connection verification"""
        # If we got here, connection succeeded
        assert transport.redis_client.ping()

    # =========================================================================
    # SET OPERATIONS (STRING)
    # =========================================================================

    def test_send_and_fetch_string(self, transport, simple_payload):
        """Test basic string send and fetch"""
        transport.send_to_redis(
            key='test:string',
            payload=simple_payload,
            operation='set'
        )

        fetched = transport.fetch_from_redis(
            key='test:string',
            operation='get'
        )

        assert fetched is not None
        assert fetched.source_agent == simple_payload.source_agent
        assert fetched.content == simple_payload.content

    def test_string_type_check(self, transport, simple_payload):
        """Test type checking prevents mixing operations"""
        # Store as STRING
        transport.send_to_redis(
            key='test:type_check',
            payload=simple_payload,
            operation='set'
        )

        # Try to use LIST operation (should fail)
        with pytest.raises(TypeError, match="cannot use 'lpush'"):
            transport.send_to_redis(
                key='test:type_check',
                payload=simple_payload,
                operation='lpush'
            )

    def test_fetch_nonexistent_key(self, transport):
        """Test fetching nonexistent key returns None"""
        result = transport.fetch_from_redis(
            key='test:nonexistent',
            operation='get'
        )
        assert result is None

    # =========================================================================
    # LIST OPERATIONS
    # =========================================================================

    def test_rpush_and_lrange(self, transport, simple_payload):
        """Test list push and range operations"""
        # Push items
        for i in range(3):
            payload = VesiclePayload(
                source_agent=f'agent-{i}',
                content={'index': i},
                ttl_seconds=1800
            )
            transport.send_to_redis(
                key='test:list',
                payload=payload,
                operation='rpush'
            )

        # Fetch range
        results = transport.fetch_from_redis(
            key='test:list',
            operation='lrange'
        )

        assert results is not None
        assert len(results) == 3
        assert results[0].content['index'] == 0

    def test_lpush_operations(self, transport):
        """Test left push operations"""
        for i in range(3):
            payload = VesiclePayload(
                source_agent=f'agent-{i}',
                content={'index': i},
                ttl_seconds=1800
            )
            transport.send_to_redis(
                key='test:lpush',
                payload=payload,
                operation='lpush'
            )

        results = transport.fetch_from_redis(
            key='test:lpush',
            operation='lrange'
        )

        assert len(results) == 3
        # LPUSH adds to front, so order is reversed
        assert results[0].content['index'] == 2

    def test_lindex_operation(self, transport, simple_payload):
        """Test list index fetch"""
        transport.send_to_redis(
            key='test:lindex',
            payload=simple_payload,
            operation='rpush'
        )

        result = transport.fetch_from_redis(
            key='test:lindex',
            operation='lindex',
            list_index=0
        )

        assert result is not None
        assert result.source_agent == simple_payload.source_agent

    def test_list_type_check(self, transport, simple_payload):
        """Test type checking for list operations"""
        # Create as STRING first
        transport.send_to_redis(
            key='test:list_type',
            payload=simple_payload,
            operation='set'
        )

        # Try LIST operation (should fail)
        with pytest.raises(TypeError, match="cannot use 'rpush'"):
            transport.send_to_redis(
                key='test:list_type',
                payload=simple_payload,
                operation='rpush'
            )

    # =========================================================================
    # HASH OPERATIONS
    # =========================================================================

    def test_hset_and_hgetall(self, transport):
        """Test hash set and getall operations"""
        for i in range(3):
            payload = VesiclePayload(
                source_agent=f'agent-{i}',
                content={'index': i},
                ttl_seconds=1800
            )
            transport.send_to_redis(
                key='test:hash',
                payload=payload,
                operation='hset'
            )

        results = transport.fetch_from_redis(
            key='test:hash',
            operation='hgetall'
        )

        assert isinstance(results, dict)
        assert len(results) == 3

    def test_hget_specific_field(self, transport, simple_payload):
        """Test fetching specific hash field"""
        transport.send_to_redis(
            key='test:hget',
            payload=simple_payload,
            operation='hset'
        )

        result = transport.fetch_from_redis(
            key='test:hget',
            operation='hget',
            hash_field=simple_payload.payload_id
        )

        assert result is not None
        assert result.payload_id == simple_payload.payload_id

    def test_hash_type_check(self, transport, simple_payload):
        """Test type checking for hash operations"""
        transport.send_to_redis(
            key='test:hash_type',
            payload=simple_payload,
            operation='set'
        )

        with pytest.raises(TypeError, match="cannot use 'hset'"):
            transport.send_to_redis(
                key='test:hash_type',
                payload=simple_payload,
                operation='hset'
            )

    # =========================================================================
    # SET OPERATIONS (SET TYPE)
    # =========================================================================

    def test_sadd_and_smembers(self, transport):
        """Test set add and members operations"""
        for i in range(3):
            payload = VesiclePayload(
                source_agent=f'agent-{i}',
                content={'index': i},
                ttl_seconds=1800
            )
            transport.send_to_redis(
                key='test:set',
                payload=payload,
                operation='sadd'
            )

        results = transport.fetch_from_redis(
            key='test:set',
            operation='smembers'
        )

        assert isinstance(results, list)
        assert len(results) == 3

    def test_set_type_check(self, transport, simple_payload):
        """Test type checking for set operations"""
        transport.send_to_redis(
            key='test:set_type',
            payload=simple_payload,
            operation='set'
        )

        with pytest.raises(TypeError, match="cannot use 'sadd'"):
            transport.send_to_redis(
                key='test:set_type',
                payload=simple_payload,
                operation='sadd'
            )

    # =========================================================================
    # UTILITY OPERATIONS
    # =========================================================================

    def test_key_exists(self, transport, simple_payload):
        """Test key existence check"""
        transport.send_to_redis(
            key='test:exists',
            payload=simple_payload,
            operation='set'
        )

        assert transport.key_exists('test:exists')
        assert not transport.key_exists('test:nonexistent')

    def test_get_key_type(self, transport, simple_payload):
        """Test getting key type"""
        transport.send_to_redis(
            key='test:keytype',
            payload=simple_payload,
            operation='set'
        )

        key_type = transport.get_key_type('test:keytype')
        assert key_type == RedisKeyType.STRING

    def test_get_key_type_nonexistent(self, transport):
        """Test getting type of nonexistent key"""
        key_type = transport.get_key_type('test:nonexistent')
        assert key_type == RedisKeyType.NONE

    def test_delete_key(self, transport, simple_payload):
        """Test key deletion"""
        transport.send_to_redis(
            key='test:delete',
            payload=simple_payload,
            operation='set'
        )

        assert transport.key_exists('test:delete')
        deleted = transport.delete_key('test:delete')
        assert deleted
        assert not transport.key_exists('test:delete')

    def test_get_stats(self, transport):
        """Test getting transport statistics"""
        stats = transport.get_stats()
        assert 'transport_id' in stats
        assert 'redis_version' in stats
        assert stats['transport_id'] == transport.transport_id

    # =========================================================================
    # MSGPACK SERIALIZATION
    # =========================================================================

    def test_msgpack_serialization(self, transport, simple_payload):
        """Test msgpack send and fetch"""
        transport.send_to_redis(
            key='test:msgpack',
            payload=simple_payload,
            operation='set',
            use_msgpack=True
        )

        fetched = transport.fetch_from_redis(
            key='test:msgpack',
            operation='get',
            use_msgpack=True
        )

        assert fetched is not None
        assert fetched.source_agent == simple_payload.source_agent
        assert fetched.content == simple_payload.content


# =============================================================================
# BATCH OPERATIONS TESTS
# =============================================================================

class TestVesiclePool:
    """Tests for VesiclePool batch operations"""

    def test_pool_creation(self, transport):
        """Test pool initialization"""
        pool = VesiclePool(transport)
        assert len(pool) == 0

    def test_pool_add_payload(self, transport, simple_payload):
        """Test adding payloads to pool"""
        pool = VesiclePool(transport)
        pool.add_payload('test:pool', simple_payload)
        assert len(pool) == 1

    def test_pool_flush(self, transport):
        """Test flushing pool to Redis"""
        pool = VesiclePool(transport)

        for i in range(5):
            payload = VesiclePayload(
                source_agent=f'agent-{i}',
                content={'index': i}
            )
            pool.add_payload('test:batch', payload, operation='rpush')

        count = pool.flush()
        assert count == 5
        assert len(pool) == 0

        # Verify in Redis
        results = transport.fetch_from_redis(
            key='test:batch',
            operation='lrange'
        )
        assert len(results) == 5


# =============================================================================
# SCHEMA VALIDATION TESTS
# =============================================================================

class TestSchemaValidation:
    """Tests for schema validation"""

    def test_valid_schema_v1_0(self, transport):
        """Test valid v1.0 payload"""
        payload = VesiclePayload(
            source_agent='test',
            content={'data': 'test'},
            schema_version='1.0'
        )
        # Should not raise
        transport.send_to_redis(
            key='test:schema_v1',
            payload=payload,
            operation='set'
        )

    def test_valid_schema_v1_1(self, transport):
        """Test valid v1.1 payload with TTT headers"""
        payload = VesiclePayload(
            source_agent='test',
            content={'data': 'test'},
            schema_version='1.1',
            ttl_seconds=1800,
            ttt_headers={
                'traceable_id': 'trace-001',
                'transparent_lineage': ['step1', 'step2'],
                'trustworthy_signature': 'sig-001'
            }
        )
        # Should not raise
        transport.send_to_redis(
            key='test:schema_v1_1',
            payload=payload,
            operation='set'
        )

    def test_invalid_schema_version_in_payload(self):
        """Test invalid schema version"""
        with pytest.raises(ValueError):
            VesiclePayload(
                source_agent='test',
                content={},
                schema_version='invalid'
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
