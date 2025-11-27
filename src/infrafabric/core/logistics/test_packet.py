#!/usr/bin/env python3
"""
Unit tests for IF.LOGISTICS dispatch layer.

Run with: python -m pytest src/infrafabric/core/logistics/test_packet.py -v
"""

from datetime import datetime
from typing import Dict

import pytest
import redis

from infrafabric.core.logistics import DispatchQueue, LogisticsDispatcher, Packet, RedisKeyType


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def redis_client():
    """Get a Redis client for testing."""
    try:
        client = redis.Redis(host="localhost", port=6379, db=15, decode_responses=True)
        client.ping()
        yield client
        client.flushdb()
    except redis.ConnectionError:
        pytest.skip("Redis not available")


@pytest.fixture
def dispatcher(redis_client):
    """Instantiate a LogisticsDispatcher against the test DB."""
    return LogisticsDispatcher(redis_host="localhost", redis_port=6379, redis_db=15, decode_responses=True)


@pytest.fixture
def simple_packet() -> Packet:
    """Create a simple test packet."""
    return Packet(origin="test-agent", contents={"test": "data", "value": 42}, schema_version="1.0", ttl_seconds=3600)


# =============================================================================
# PACKET TESTS
# =============================================================================


class TestPacket:
    """Tests for Packet dataclass."""

    def test_packet_creation(self):
        packet = Packet(origin="test-agent", contents={"key": "value"})
        assert packet.origin == "test-agent"
        assert packet.contents == {"key": "value"}
        assert packet.schema_version == "1.0"
        assert packet.ttl_seconds == 3600

    def test_tracking_id_generation(self):
        one = Packet(origin="agent1", contents={})
        two = Packet(origin="agent2", contents={})
        assert one.tracking_id != two.tracking_id
        assert len(one.tracking_id) == 36

    def test_dispatched_timestamp_generation(self):
        packet = Packet(origin="test", contents={})
        datetime.fromisoformat(packet.dispatched_at)

    def test_invalid_ttl_bounds(self):
        with pytest.raises(ValueError, match="ttl_seconds must be 1-86400"):
            Packet(origin="test", contents={}, ttl_seconds=0)

    def test_invalid_schema_version(self):
        with pytest.raises(ValueError, match="Unknown schema_version"):
            Packet(origin="test", contents={}, schema_version="9.9")

    def test_contents_type_validation(self):
        with pytest.raises(TypeError, match="contents must be a dictionary"):
            Packet(origin="test", contents="not a dict")

    def test_serialization_roundtrip(self):
        packet = Packet(origin="test", contents={"key": "value"})
        restored = Packet.from_json(packet.to_json())
        assert restored.origin == packet.origin
        assert restored.contents == packet.contents

    def test_legacy_field_mapping(self):
        legacy_data: Dict[str, object] = {
            "payload_id": "123",
            "timestamp": datetime.utcnow().isoformat(),
            "source_agent": "legacy",
            "content": {"note": "legacy"},
            "schema_version": "1.0",
        }
        restored = Packet.from_dict(legacy_data)
        assert restored.origin == "legacy"
        assert restored.tracking_id == "123"
        assert restored.contents == {"note": "legacy"}


# =============================================================================
# DISPATCHER TESTS
# =============================================================================


class TestLogisticsDispatcher:
    """Tests for LogisticsDispatcher class."""

    def test_initialization(self, dispatcher):
        assert dispatcher is not None
        assert dispatcher.transport_id.startswith("logistics_")
        assert dispatcher.default_ttl == 3600

    def test_redis_connection(self, dispatcher):
        assert dispatcher.redis_client.ping()

    def test_dispatch_and_collect_string(self, dispatcher, simple_parcel):
        dispatcher.dispatch_to_redis(key="test:string", packet=simple_parcel, operation="set")
        fetched = dispatcher.collect_from_redis(key="test:string", operation="get")
        assert fetched is not None
        assert fetched.origin == simple_parcel.origin
        assert fetched.contents == simple_parcel.contents

    def test_list_operations(self, dispatcher):
        for i in range(3):
            packet = Packet(origin=f"agent-{i}", contents={"index": i}, ttl_seconds=1800)
            dispatcher.dispatch_to_redis(key="test:list", packet=packet, operation="rpush")

        results = dispatcher.collect_from_redis(key="test:list", operation="lrange")
        assert results is not None
        assert len(results) == 3
        assert results[0].contents["index"] == 0

    def test_hash_operations(self, dispatcher, simple_parcel):
        dispatcher.dispatch_to_redis(key="test:hash", packet=simple_parcel, operation="hset")
        result = dispatcher.collect_from_redis(
            key="test:hash", operation="hget", hash_field=simple_parcel.tracking_id
        )
        assert result is not None
        assert result.tracking_id == simple_parcel.tracking_id

    def test_set_operations(self, dispatcher):
        packet = Packet(origin="worker", contents={"role": "worker"})
        dispatcher.dispatch_to_redis(key="test:set", packet=packet, operation="sadd")
        results = dispatcher.collect_from_redis(key="test:set", operation="smembers")
        assert results is not None
        assert any(item.contents.get("role") == "worker" for item in results)

    def test_type_queries(self, dispatcher, simple_parcel):
        dispatcher.dispatch_to_redis(key="test:type", packet=simple_parcel, operation="set")
        assert dispatcher.key_exists("test:type")
        assert dispatcher.get_key_type("test:type") == RedisKeyType.STRING


# =============================================================================
# DISPATCH QUEUE TESTS
# =============================================================================


class TestDispatchQueue:
    """Tests for DispatchQueue batch operations."""

    def test_queue_flush(self, dispatcher):
        queue = DispatchQueue(dispatcher)
        for i in range(2):
            queue.add_parcel("test:batch", Packet(origin="queue", contents={"idx": i}), operation="lpush")
        assert len(queue) == 2
        count = queue.flush()
        assert count == 2
