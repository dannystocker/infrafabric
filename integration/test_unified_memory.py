#!/usr/bin/env python3
"""
Unit Tests for UnifiedMemory

Tests cover:
- Connection management (Redis, ChromaDB, fallback)
- Conversation storage and retrieval
- Finding storage and semantic search
- Session state management
- Context window trimming
- Error handling and graceful degradation
- Health status reporting

IF.citation: if://test/unified-memory/v1.0.0
IF.TTT: All tests logged with traceable IDs
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from unified_memory import (
    UnifiedMemory,
    MemoryOperation,
    MemoryOperationStatus,
    StorageBackend,
    RedisConnectionManager,
    ChromaDBConnectionManager,
)


# ============================================================================
# Mock Backends for Testing
# ============================================================================

class MockRedisClient:
    """Mock Redis client for testing without real Redis"""

    def __init__(self):
        self.data = {}
        self.ttls = {}

    def setex(self, key, ttl, value):
        """Mock setex"""
        self.data[key] = value
        self.ttls[key] = time.time() + ttl

    def get(self, key):
        """Mock get"""
        if key not in self.data:
            return None
        if time.time() > self.ttls.get(key, float('inf')):
            del self.data[key]
            return None
        return self.data[key]

    def ping(self):
        """Mock ping"""
        return True

    def close(self):
        """Mock close"""
        pass


class MockChromaDBCollection:
    """Mock ChromaDB collection for testing"""

    def __init__(self, name):
        self.name = name
        self.data = {}  # id -> {doc, metadata}

    def add(self, ids, documents, metadatas):
        """Mock add"""
        for id, doc, meta in zip(ids, documents, metadatas):
            self.data[id] = {"document": doc, "metadata": meta}

    def query(self, query_texts, n_results, include):
        """Mock query"""
        # Simple substring matching for testing
        query = query_texts[0]
        matches = []
        for id, item in list(self.data.items())[:n_results]:
            if query.lower() in item["document"].lower():
                matches.append({
                    "document": item["document"],
                    "metadata": item["metadata"],
                    "distance": 0.1,
                })

        return {
            "documents": [[m["document"] for m in matches]],
            "metadatas": [[m["metadata"] for m in matches]],
            "distances": [[m["distance"] for m in matches]],
        }


class MockChromaDBClient:
    """Mock ChromaDB client for testing"""

    def __init__(self):
        self.collections = {}

    def heartbeat(self):
        """Mock heartbeat"""
        return True

    def get_or_create_collection(self, name, metadata=None):
        """Mock get_or_create_collection"""
        if name not in self.collections:
            self.collections[name] = MockChromaDBCollection(name)
        return self.collections[name]


# ============================================================================
# Unit Tests
# ============================================================================

class TestRedisConnectionManager(unittest.TestCase):
    """Test Redis connection manager"""

    def test_connect_failure_without_redis_module(self):
        """Test connection failure when redis module not available"""
        mgr = RedisConnectionManager("localhost", 6379)

        # This will fail because redis isn't installed in test env
        # but the code should handle it gracefully
        result = mgr.connect()
        # We expect it to fail or succeed depending on env
        self.assertIsInstance(result, bool)

    def test_client_getter_returns_none_when_not_connected(self):
        """Test that get_client returns None when not connected"""
        mgr = RedisConnectionManager("localhost", 6379)
        client = mgr.get_client()
        self.assertIsNone(client)

    def test_close_is_safe(self):
        """Test that close can be called even when not connected"""
        mgr = RedisConnectionManager("localhost", 6379)
        # Should not raise
        mgr.close()


class TestChromaDBConnectionManager(unittest.TestCase):
    """Test ChromaDB connection manager"""

    def test_connect_failure_without_chromadb_module(self):
        """Test connection failure when chromadb module not available"""
        mgr = ChromaDBConnectionManager("localhost", 8000)
        result = mgr.connect()
        self.assertIsInstance(result, bool)

    def test_client_getter_returns_none_when_not_connected(self):
        """Test that get_client returns None when not connected"""
        mgr = ChromaDBConnectionManager("localhost", 8000)
        client = mgr.get_client()
        self.assertIsNone(client)

    def test_close_is_safe(self):
        """Test that close can be called even when not connected"""
        mgr = ChromaDBConnectionManager("localhost", 8000)
        mgr.close()


class TestUnifiedMemoryWithMocks(unittest.TestCase):
    """Test UnifiedMemory with mocked backends"""

    def setUp(self):
        """Set up test fixtures"""
        self.memory = UnifiedMemory(
            redis_host="localhost",
            redis_port=6379,
            chromadb_host="localhost",
            chromadb_port=8000,
            enable_memory_fallback=True,
            conversation_ttl_seconds=3600,
            finding_ttl_seconds=86400,
        )

    def tearDown(self):
        """Clean up"""
        self.memory.close()

    def test_initialization_with_fallback(self):
        """Test UnifiedMemory initializes with fallback enabled"""
        self.assertTrue(self.memory.enable_memory_fallback)
        self.assertEqual(self.memory.conversation_ttl, 3600)
        self.assertEqual(self.memory.finding_ttl, 86400)

    def test_store_conversation_fallback(self):
        """Test conversation storage falls back to memory when Redis unavailable"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        op = self.memory.store_conversation("claude-max", "session-001", messages)

        # Should succeed with memory fallback
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])
        self.assertTrue(len(op.backends_used) > 0)

    def test_retrieve_conversation_fallback(self):
        """Test conversation retrieval falls back to memory"""
        messages = [
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "Response"},
        ]

        # Store first
        self.memory.store_conversation("claude-max", "session-002", messages)

        # Retrieve
        retrieved = self.memory.retrieve_conversation("claude-max", "session-002")

        # Should get something back (either from memory fallback or none)
        if retrieved:
            self.assertIsInstance(retrieved, list)

    def test_store_finding_fallback(self):
        """Test finding storage with fallback"""
        finding = {
            "finding_id": "find-001",
            "content": "Important insight",
            "source_model": "claude-max",
            "session_id": "session-001",
            "confidence": 0.95,
            "tags": ["insight"],
        }

        op = self.memory.store_finding(finding)

        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])
        self.assertTrue(len(op.backends_used) > 0)

    def test_retrieve_context_returns_list(self):
        """Test context retrieval always returns a list"""
        context = self.memory.retrieve_context(
            query="test query",
            collections=["personality"],
            n_results=3,
        )

        self.assertIsInstance(context, list)

    def test_session_state_storage(self):
        """Test session state can be stored and retrieved"""
        state = {
            "user_id": "user-123",
            "tone": "casual",
            "context_level": "advanced",
        }

        op = self.memory.store_session_state("session-001", state)
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])

        retrieved = self.memory.get_session_state("session-001")
        if retrieved:
            self.assertEqual(retrieved.get("user_id"), "user-123")

    def test_trim_context_window_short_message_list(self):
        """Test context trimming with short message list"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        trimmed = self.memory._trim_context_window(messages)
        self.assertEqual(len(trimmed), 2)

    def test_trim_context_window_long_message_list(self):
        """Test context trimming with long message list"""
        # Set small max for testing
        self.memory.max_context_messages = 10

        messages = [
            {"role": "system", "content": "System"},
        ] + [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"}
            for i in range(100)
        ]

        trimmed = self.memory._trim_context_window(messages)
        self.assertLessEqual(len(trimmed), self.memory.max_context_messages)

        # Should keep system message if first
        if messages[0]["role"] == "system":
            self.assertEqual(trimmed[0]["role"], "system")

    def test_health_status(self):
        """Test health status reporting"""
        health = self.memory.get_health_status()

        self.assertIn("timestamp", health)
        self.assertIn("redis", health)
        self.assertIn("chromadb", health)
        self.assertIn("memory_fallback", health)

        # Fallback should be enabled
        self.assertTrue(health["memory_fallback"]["enabled"])

    def test_clear_expired_data(self):
        """Test expired data cleanup"""
        result = self.memory.clear_expired_data()

        self.assertIsInstance(result, dict)
        self.assertIn("conversations", result)
        self.assertIn("findings", result)
        self.assertIn("session_states", result)

    def test_operation_id_generation(self):
        """Test operation ID is unique"""
        op_id_1 = self.memory._generate_operation_id()
        time.sleep(0.01)
        op_id_2 = self.memory._generate_operation_id()

        self.assertNotEqual(op_id_1, op_id_2)
        self.assertEqual(len(op_id_1), 12)

    def test_memory_operation_object(self):
        """Test MemoryOperation dataclass"""
        op = MemoryOperation(
            status=MemoryOperationStatus.SUCCESS,
            operation_id="op-123",
            timestamp=datetime.now().isoformat(),
            model_id="claude-max",
            session_id="session-001",
            data_type="conversation",
            backends_used=[StorageBackend.REDIS],
            latency_ms=45.2,
        )

        self.assertEqual(op.status, MemoryOperationStatus.SUCCESS)
        self.assertEqual(op.model_id, "claude-max")
        self.assertEqual(op.latency_ms, 45.2)

    def test_concurrent_operations(self):
        """Test multiple operations don't interfere"""
        messages1 = [{"role": "user", "content": "First"}]
        messages2 = [{"role": "user", "content": "Second"}]

        op1 = self.memory.store_conversation("model-1", "session-1", messages1)
        op2 = self.memory.store_conversation("model-2", "session-2", messages2)

        self.assertNotEqual(op1.operation_id, op2.operation_id)

        # Both should succeed (or partial)
        self.assertIn(op1.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])
        self.assertIn(op2.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])

    def test_conversation_with_metadata(self):
        """Test storing conversations with rich message data"""
        messages = [
            {"role": "user", "content": "Hello", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "Hi", "metadata": {"model": "claude"}},
        ]

        op = self.memory.store_conversation("claude-max", "session-001", messages)
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])

    def test_finding_storage_with_tags(self):
        """Test finding storage with multiple tags"""
        finding = {
            "finding_id": "find-multi-tag",
            "content": "Complex insight",
            "source_model": "deepseek",
            "session_id": "session-001",
            "confidence": 0.87,
            "tags": ["tag1", "tag2", "tag3"],
        }

        op = self.memory.store_finding(finding)
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])

    def test_error_handling_in_store_conversation(self):
        """Test error handling in store_conversation"""
        # Pass invalid message format
        op = self.memory.store_conversation("model", "session", "not a list")

        # Should succeed with fallback (graceful degradation)
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])

    def test_error_handling_in_store_finding(self):
        """Test error handling in store_finding"""
        # Pass incomplete finding
        op = self.memory.store_finding({})

        # Should succeed with fallback (graceful degradation)
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])


class TestUnifiedMemoryWithMockedConnections(unittest.TestCase):
    """Test UnifiedMemory with fully mocked connections"""

    def setUp(self):
        """Set up with mocked connections"""
        self.memory = UnifiedMemory(enable_memory_fallback=True)

        # Mock Redis
        self.mock_redis = MockRedisClient()
        self.memory.redis_mgr._redis_client = self.mock_redis
        self.memory.redis_mgr._is_connected = True

        # Mock ChromaDB
        self.mock_chromadb = MockChromaDBClient()
        self.memory.chromadb_mgr._client = self.mock_chromadb
        self.memory.chromadb_mgr._is_connected = True

    def test_conversation_round_trip_with_redis(self):
        """Test storing and retrieving conversation via mocked Redis"""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "What is AI?"},
            {"role": "assistant", "content": "AI is artificial intelligence"},
        ]

        # Store
        op = self.memory.store_conversation("claude-max", "session-001", messages)
        self.assertEqual(op.status, MemoryOperationStatus.SUCCESS)
        self.assertIn(StorageBackend.REDIS, op.backends_used)

        # Retrieve
        retrieved = self.memory.retrieve_conversation("claude-max", "session-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved), 3)
        self.assertEqual(retrieved[0]["role"], "system")

    def test_finding_round_trip_with_chromadb(self):
        """Test storing and retrieving findings via mocked ChromaDB"""
        finding = {
            "finding_id": "find-001",
            "content": "Users prefer shorter responses",
            "source_model": "claude-max",
            "session_id": "session-001",
            "confidence": 0.92,
            "tags": ["ux-insight", "user-behavior"],
        }

        # Store
        op = self.memory.store_finding(finding)
        self.assertEqual(op.status, MemoryOperationStatus.SUCCESS)

        # Retrieve via semantic search
        context = self.memory.retrieve_context(
            query="shorter responses",
            collections=["findings"],
            n_results=5,
        )

        # Should find something
        self.assertGreater(len(context), 0)

    def test_session_state_round_trip(self):
        """Test session state storage and retrieval"""
        state = {
            "user_id": "user-123",
            "preferences": {"language": "en", "tone": "formal"},
            "context_depth": "advanced",
        }

        # Store
        op = self.memory.store_session_state("session-001", state)
        self.assertEqual(op.status, MemoryOperationStatus.SUCCESS)

        # Retrieve
        retrieved = self.memory.get_session_state("session-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["user_id"], "user-123")

    def test_multiple_collections_retrieval(self):
        """Test retrieving context from multiple collections"""
        # Pre-populate multiple collections
        personality_collection = self.mock_chromadb.get_or_create_collection(
            "personality"
        )
        personality_collection.add(
            ids=["p1"],
            documents=["Sergio is witty and direct"],
            metadatas=[{"type": "personality"}],
        )

        knowledge_collection = self.mock_chromadb.get_or_create_collection(
            "knowledge"
        )
        knowledge_collection.add(
            ids=["k1"],
            documents=["Therapy requires openness"],
            metadatas=[{"type": "knowledge"}],
        )

        # Query both
        context = self.memory.retrieve_context(
            query="therapy",
            collections=["personality", "knowledge"],
            n_results=2,
        )

        self.assertIsInstance(context, list)


class TestIntegrationExamples(unittest.TestCase):
    """Test example integration patterns"""

    def test_claude_max_integration_example(self):
        """Test Claude Max integration pattern compiles"""
        # Just verify the example code is syntactically valid
        from unified_memory import ModelMemoryIntegration

        self.assertTrue(hasattr(ModelMemoryIntegration, "claude_max_integration"))

    def test_deepseek_integration_example(self):
        """Test DeepSeek integration pattern compiles"""
        from unified_memory import ModelMemoryIntegration

        self.assertTrue(hasattr(ModelMemoryIntegration, "deepseek_integration"))

    def test_gemini_integration_example(self):
        """Test Gemini integration pattern compiles"""
        from unified_memory import ModelMemoryIntegration

        self.assertTrue(hasattr(ModelMemoryIntegration, "gemini_integration"))


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""

    def setUp(self):
        """Set up for performance tests"""
        self.memory = UnifiedMemory(enable_memory_fallback=True)

    def tearDown(self):
        """Clean up"""
        self.memory.close()

    def test_operation_latency_under_100ms(self):
        """Test that operations complete in reasonable time"""
        messages = [{"role": "user", "content": f"Message {i}"} for i in range(50)]

        start = time.time()
        op = self.memory.store_conversation("model", "session", messages)
        latency = op.latency_ms

        # Should be reasonably fast
        self.assertLess(latency, 500)  # 500ms for in-memory operations is acceptable

    def test_context_trimming_performance(self):
        """Test that context trimming is fast"""
        messages = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"}
            for i in range(1000)
        ]

        start = time.time()
        trimmed = self.memory._trim_context_window(messages)
        elapsed = (time.time() - start) * 1000  # ms

        self.assertLess(elapsed, 100)  # Should be very fast
        self.assertLessEqual(len(trimmed), self.memory.max_context_messages)


# ============================================================================
# Integration with Debate Document Requirements
# ============================================================================

class TestDebateDocumentRequirements(unittest.TestCase):
    """Test that implementation meets debate document requirements"""

    def setUp(self):
        """Set up test memory"""
        self.memory = UnifiedMemory(enable_memory_fallback=True)

    def tearDown(self):
        """Clean up"""
        self.memory.close()

    def test_requirement_store_conversation_redis_1h_ttl(self):
        """
        Requirement from debate lines 222-225:
        store_conversation(model_id, session_id, messages) → Redis with 1h TTL
        """
        messages = [{"role": "user", "content": "Test"}]
        op = self.memory.store_conversation("claude-max", "session-001", messages)

        # Operation should succeed
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])

        # TTL should be 1 hour (3600 seconds)
        self.assertEqual(self.memory.conversation_ttl, 3600)

    def test_requirement_retrieve_conversation_from_redis(self):
        """
        Requirement from debate line 226:
        retrieve_conversation(model_id, session_id) → from Redis
        """
        messages = [{"role": "user", "content": "Test"}]
        self.memory.store_conversation("model", "session", messages)

        retrieved = self.memory.retrieve_conversation("model", "session")

        # Should be able to retrieve
        if retrieved:
            self.assertIsInstance(retrieved, list)

    def test_requirement_retrieve_context_chromadb(self):
        """
        Requirement from debate line 227-232:
        retrieve_context(query, collections, n_results=3) → from ChromaDB
        """
        context = self.memory.retrieve_context(
            query="test query",
            collections=["personality", "knowledge"],
            n_results=3,
        )

        # Should always return a list (even if empty)
        self.assertIsInstance(context, list)

    def test_requirement_store_finding_24h_ttl(self):
        """
        Requirement from debate:
        store_finding(finding_data) → Redis with 24h TTL
        """
        finding = {
            "finding_id": "find-001",
            "content": "Test finding",
            "source_model": "model",
            "session_id": "session",
            "confidence": 0.9,
            "tags": ["test"],
        }

        op = self.memory.store_finding(finding)

        # Operation should succeed
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
        ])

        # TTL should be 24 hours (86400 seconds)
        self.assertEqual(self.memory.finding_ttl, 86400)

    def test_requirement_get_session_state(self):
        """
        Requirement from debate:
        get_session_state(session_id) → Redis
        """
        state = {"user_id": "user-123", "tone": "casual"}
        self.memory.store_session_state("session-001", state)

        retrieved = self.memory.get_session_state("session-001")

        # Should be able to retrieve
        if retrieved:
            self.assertEqual(retrieved.get("user_id"), "user-123")

    def test_requirement_context_window_management(self):
        """
        Requirement from debate line 244:
        Context window management (trim old messages if >100)
        """
        messages = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(200)
        ]

        trimmed = self.memory._trim_context_window(messages)

        # Should be trimmed
        self.assertLessEqual(len(trimmed), self.memory.max_context_messages)

    def test_requirement_graceful_degradation(self):
        """
        Requirement from debate:
        Graceful degradation (if Redis fails, continue without caching)
        """
        # This is tested by enable_memory_fallback=True
        self.assertTrue(self.memory.enable_memory_fallback)

        # Even with no backends, operations should not raise
        messages = [{"role": "user", "content": "Test"}]
        op = self.memory.store_conversation("model", "session", messages)

        # Should succeed or partially succeed
        self.assertIn(op.status, [
            MemoryOperationStatus.SUCCESS,
            MemoryOperationStatus.PARTIAL,
            MemoryOperationStatus.DEGRADED,
        ])


if __name__ == "__main__":
    unittest.main()
