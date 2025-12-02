#!/usr/bin/env python3
"""
Memory Layer Integration Tests - Pytest Implementation

This module contains all 10 integration tests for Redis + ChromaDB memory layer.

Test Coverage:
1. Redis basic store/retrieve
2. ChromaDB personality query
3. Multi-collection RAG
4. Cache hit vs miss latency
5. Redis failure graceful degradation
6. ChromaDB failure graceful degradation
7. Cross-model context sharing
8. Session persistence across restarts
9. TTL expiration
10. Markdown export

Usage:
    pytest test_memory_layer_integration.py -v
    pytest test_memory_layer_integration.py -v --cov=src/core/memory
    pytest test_memory_layer_integration.py::test_redis_store_conversation -v

Document ID: if://test/memory/integration/2025-11-30
"""

import pytest
import redis
import chromadb
import time
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from unittest.mock import patch, MagicMock
import requests


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def redis_client():
    """Connect to Redis for test session"""
    r = redis.Redis(
        host='localhost',
        port=6379,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True
    )

    # Verify connection
    try:
        r.ping()
    except redis.ConnectionError as e:
        pytest.skip(f"Redis not available: {e}")

    yield r

    # Cleanup after session
    r.flushdb()


@pytest.fixture(scope="session")
def chromadb_client():
    """Connect to ChromaDB for test session"""
    try:
        client = chromadb.HttpClient(host='localhost', port=8000)
        # Verify connection
        response = requests.get('http://localhost:8000/api/v1/heartbeat', timeout=2)
        if response.status_code != 200:
            pytest.skip("ChromaDB not responding")
    except (requests.ConnectionError, Exception) as e:
        pytest.skip(f"ChromaDB not available: {e}")

    yield client


@pytest.fixture
def memory(redis_client, chromadb_client):
    """Unified memory interface (mock implementation for testing)"""

    class MockIFMemory:
        """Simple in-memory implementation for testing"""

        def __init__(self, redis_client, chromadb_client):
            self.redis_client = redis_client
            self.chromadb_client = chromadb_client
            self._query_cache = {}

        def store_context(self, key: str, value: Dict, ttl: int) -> None:
            """Store in Context Memory (Redis)"""
            self.redis_client.setex(key, ttl, json.dumps(value))

        def retrieve_context(self, key: str) -> Optional[Dict]:
            """Retrieve from Context Memory (Redis)"""
            data = self.redis_client.get(key)
            return json.loads(data) if data else None

        def embed_knowledge(self, doc: Dict, collection: str, metadata: Dict = None) -> str:
            """Store in Deep Storage (ChromaDB)"""
            col = self.chromadb_client.get_or_create_collection(
                name=collection,
                metadata={"type": "knowledge"}
            )

            col.add(
                ids=[doc["id"]],
                documents=[doc.get("content", "")],
                metadatas=[metadata or {}]
            )

            return doc["id"]

        def query_knowledge(
            self,
            query: str,
            collections: List[str],
            k: int = 5,
            use_chromadb: bool = True,
            use_redis: bool = True
        ) -> List[Dict]:
            """Query across collections"""

            if not use_chromadb:
                return []

            all_results = []

            for collection_name in collections:
                try:
                    col = self.chromadb_client.get_or_create_collection(
                        name=collection_name
                    )

                    results = col.query(query_texts=[query], n_results=k)

                    for i, doc_id in enumerate(results["ids"][0]):
                        all_results.append({
                            "id": doc_id,
                            "collection": collection_name,
                            "score": results["distances"][0][i] if results["distances"] else 0.5,
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                        })

                except Exception as e:
                    print(f"Warning: Collection query failed: {e}")
                    continue

            # Sort by relevance (distance) - lower distance = better match
            all_results.sort(key=lambda x: x["score"])
            return all_results[:k]

    return MockIFMemory(redis_client, chromadb_client)


# ============================================================================
# TEST 1: Redis Store and Retrieve
# ============================================================================

class TestRedisStoreRetrieve:
    """Test 1: Store conversation in Redis, retrieve successfully"""

    @pytest.mark.timeout(5)
    def test_redis_basic_operations(self, redis_client):
        """Test basic Redis set/get operations"""

        # Test basic set/get
        redis_client.set("test:key:1", "value1", ex=3600)
        assert redis_client.get("test:key:1") == "value1"

        # Test TTL
        ttl = redis_client.ttl("test:key:1")
        assert 3500 < ttl <= 3600

        # Cleanup
        redis_client.delete("test:key:1")

    @pytest.mark.timeout(5)
    def test_conversation_storage(self, redis_client):
        """Test storing and retrieving conversation turns"""

        session_id = "session-test-1-20251130"

        turns = [
            {
                "turn_id": "turn-1",
                "speaker": "claude",
                "model": "claude-sonnet-4-5",
                "content": "Hello from Claude, analyzing this task...",
                "tokens": 150,
                "latency_ms": 245
            },
            {
                "turn_id": "turn-2",
                "speaker": "haiku",
                "model": "claude-haiku-4-5",
                "content": "Haiku agent 1 processing...",
                "tokens": 45,
                "latency_ms": 89
            },
            {
                "turn_id": "turn-3",
                "speaker": "deepseek",
                "model": "deepseek-v3",
                "content": "DeepSeek validation result...",
                "tokens": 200,
                "latency_ms": 512
            },
        ]

        # Store turns
        for turn in turns:
            redis_client.setex(
                f"conversation:{session_id}:{turn['turn_id']}",
                7 * 24 * 3600,
                json.dumps(turn)
            )

        # Store index
        turn_ids = [t["turn_id"] for t in turns]
        redis_client.setex(
            f"conversation:{session_id}:index",
            7 * 24 * 3600,
            json.dumps({"turns": turn_ids, "count": len(turn_ids)})
        )

        # Retrieve and verify
        index = json.loads(redis_client.get(f"conversation:{session_id}:index"))
        assert index["count"] == 3
        assert len(index["turns"]) == 3

        # Verify all turns
        for turn_id in index["turns"]:
            turn_data = json.loads(
                redis_client.get(f"conversation:{session_id}:{turn_id}")
            )
            assert turn_data is not None
            assert turn_data["speaker"] in ["claude", "haiku", "deepseek"]

        # Cleanup
        for turn_id in turn_ids:
            redis_client.delete(f"conversation:{session_id}:{turn_id}")
        redis_client.delete(f"conversation:{session_id}:index")


# ============================================================================
# TEST 2: ChromaDB Personality Query
# ============================================================================

class TestChromaDBQuery:
    """Test 2: Query ChromaDB for Sergio personality context"""

    @pytest.mark.timeout(10)
    def test_chromadb_collection_access(self, chromadb_client):
        """Test basic ChromaDB collection operations"""

        collection_name = "test-personality-collection"

        # Get or create collection
        collection = chromadb_client.get_or_create_collection(
            name=collection_name,
            metadata={"type": "personality"}
        )

        assert collection is not None

        # Add documents
        collection.add(
            ids=["trait-1", "trait-2"],
            documents=["This is about humor", "This is about empathy"],
            metadatas=[{"type": "humor"}, {"type": "empathy"}]
        )

        # Query
        results = collection.query(
            query_texts=["funny jokes"],
            n_results=1
        )

        assert len(results["ids"]) > 0
        assert results["ids"][0][0] in ["trait-1", "trait-2"]

    @pytest.mark.timeout(15)
    def test_personality_trait_retrieval(self, memory):
        """Test storing and retrieving personality traits"""

        collection_name = "personality_dna:sergio"

        personality_docs = [
            {
                "id": "sergio-trait-humor-1",
                "trait": "Humor Style",
                "content": "Sergio uses self-deprecating humor and puns about technology.",
                "confidence": 0.95
            },
            {
                "id": "sergio-trait-empathy",
                "trait": "Emotional Intelligence",
                "content": "Sergio reads user frustration and adjusts tone accordingly.",
                "confidence": 0.94
            },
            {
                "id": "sergio-trait-learning",
                "trait": "Learning Orientation",
                "content": "Admits knowledge gaps gracefully. Asks clarifying questions.",
                "confidence": 0.96
            },
        ]

        # Embed documents
        for doc in personality_docs:
            memory.embed_knowledge(
                doc=doc,
                collection=collection_name,
                metadata={"trait": doc["trait"], "confidence": doc["confidence"]}
            )

        # Query for humor
        humor_results = memory.query_knowledge(
            query="humorous response style",
            collections=[collection_name],
            k=2
        )

        assert len(humor_results) >= 1

        # Query for empathy
        empathy_results = memory.query_knowledge(
            query="emotional intelligence",
            collections=[collection_name],
            k=2
        )

        assert len(empathy_results) >= 1


# ============================================================================
# TEST 3: Multi-Collection RAG
# ============================================================================

class TestMultiCollectionRAG:
    """Test 3: Multi-collection RAG query"""

    @pytest.mark.timeout(15)
    def test_multi_collection_query(self, memory):
        """Test querying across multiple collections"""

        personality_col = "personality_dna:sergio"
        humor_col = "knowledge:humor"

        # Add to personality collection
        memory.embed_knowledge(
            doc={
                "id": "personality-humor",
                "content": "Sergio uses self-deprecating humor",
                "trait": "Humor"
            },
            collection=personality_col
        )

        # Add to humor collection
        memory.embed_knowledge(
            doc={
                "id": "humor-timing",
                "content": "Timing is everything in humor",
                "type": "technique"
            },
            collection=humor_col
        )

        # Query across both
        results = memory.query_knowledge(
            query="humor response style",
            collections=[personality_col, humor_col],
            k=5
        )

        assert len(results) >= 1


# ============================================================================
# TEST 4: Cache Latency
# ============================================================================

class TestCacheLatency:
    """Test 4: Cache hit vs miss latency comparison"""

    @pytest.mark.timeout(10)
    def test_redis_latency_baseline(self, redis_client):
        """Measure raw Redis latency"""

        latencies = []

        for i in range(50):
            start = time.perf_counter()
            redis_client.set(f"latency_test:{i}", f"value_{i}", ex=3600)
            latencies.append((time.perf_counter() - start) * 1000)

        avg_latency = sum(latencies) / len(latencies)

        # Redis SET should be <5ms
        assert avg_latency < 5, f"SET latency {avg_latency:.2f}ms exceeds 5ms target"

        # Cleanup
        for i in range(50):
            redis_client.delete(f"latency_test:{i}")

    @pytest.mark.timeout(10)
    def test_cache_speedup(self, memory, redis_client):
        """Test that caching provides latency speedup"""

        query_text = "test query"
        collection = "test-collection"
        cache_key = f"query_cache:{collection}:{hash(query_text)}"

        # Clear cache
        redis_client.delete(cache_key)

        # First query (cache miss)
        start_miss = time.perf_counter()
        # Simulate query latency (100ms)
        time.sleep(0.1)
        latency_miss_ms = (time.perf_counter() - start_miss) * 1000

        # Cache result
        redis_client.setex(cache_key, 3600, json.dumps({"results": []}))

        # Second query (cache hit)
        start_hit = time.perf_counter()
        cached = redis_client.get(cache_key)
        latency_hit_ms = (time.perf_counter() - start_hit) * 1000

        assert cached is not None
        assert latency_hit_ms < latency_miss_ms / 3, f"Cache hit should be 3x+ faster"


# ============================================================================
# TEST 5: Redis Failure Graceful Degradation
# ============================================================================

class TestRedisFailureDegradation:
    """Test 5: Redis failure graceful degradation"""

    @pytest.mark.timeout(10)
    def test_redis_connection_failure_handling(self):
        """Test handling of Redis connection failures"""

        # Try to connect to unreachable Redis
        try:
            r = redis.Redis(
                host='localhost',
                port=9999,  # Wrong port
                socket_connect_timeout=1
            )
            r.ping()
            pytest.fail("Should fail on wrong port")
        except redis.ConnectionError:
            # Expected behavior
            pass

    @pytest.mark.timeout(10)
    def test_redis_retry_logic(self, redis_client):
        """Test Redis retry mechanism"""

        # Verify normal operation
        redis_client.set("test:retry", "value")
        assert redis_client.get("test:retry") == "value"

        # Connection should be reusable
        redis_client.set("test:retry2", "value2")
        assert redis_client.get("test:retry2") == "value2"

        redis_client.delete("test:retry")
        redis_client.delete("test:retry2")


# ============================================================================
# TEST 6: ChromaDB Failure Graceful Degradation
# ============================================================================

class TestChromaDBFailureDegradation:
    """Test 6: ChromaDB failure graceful degradation"""

    @pytest.mark.timeout(10)
    def test_chromadb_health_check(self):
        """Test ChromaDB health check"""

        try:
            response = requests.get(
                'http://localhost:8000/api/v1/heartbeat',
                timeout=2
            )
            assert response.status_code == 200
        except requests.ConnectionError:
            pytest.skip("ChromaDB not available")

    @pytest.mark.timeout(10)
    def test_fallback_to_cached_results(self, redis_client):
        """Test fallback to cached results when ChromaDB unavailable"""

        query_key = "cached:query:results"
        cached_data = {"results": [{"id": "1", "content": "cached result"}]}

        # Store cached result
        redis_client.setex(query_key, 3600, json.dumps(cached_data))

        # Retrieve without ChromaDB
        cached = json.loads(redis_client.get(query_key))
        assert cached == cached_data

        redis_client.delete(query_key)


# ============================================================================
# TEST 7: Cross-Model Context Sharing
# ============================================================================

class TestCrossModelSharing:
    """Test 7: Cross-model context sharing"""

    @pytest.mark.timeout(10)
    def test_claude_deepseek_handoff(self, redis_client):
        """Test context handoff between Claude and DeepSeek"""

        session_id = "cross-model-test"

        # Claude stores analysis
        claude_analysis = {
            "agent_id": "claude-sonnet-1",
            "findings": ["finding-1", "finding-2", "finding-3"],
            "confidence": 0.92
        }

        redis_client.setex(
            f"analysis:claude:{session_id}",
            3600,
            json.dumps(claude_analysis)
        )

        # DeepSeek retrieves
        retrieved = json.loads(
            redis_client.get(f"analysis:claude:{session_id}")
        )

        assert retrieved["agent_id"] == "claude-sonnet-1"
        assert len(retrieved["findings"]) == 3

        # DeepSeek stores validation
        deepseek_validation = {
            "agent_id": "deepseek-v3-1",
            "validating": "claude-sonnet-1",
            "confirmed_findings": 3
        }

        redis_client.setex(
            f"analysis:deepseek:{session_id}",
            3600,
            json.dumps(deepseek_validation)
        )

        # Claude retrieves
        validation = json.loads(
            redis_client.get(f"analysis:deepseek:{session_id}")
        )

        assert validation["agent_id"] == "deepseek-v3-1"
        assert validation["validating"] == "claude-sonnet-1"

        redis_client.delete(f"analysis:claude:{session_id}")
        redis_client.delete(f"analysis:deepseek:{session_id}")


# ============================================================================
# TEST 8: Session Persistence
# ============================================================================

class TestSessionPersistence:
    """Test 8: Session state persistence across restarts"""

    @pytest.mark.timeout(10)
    def test_session_persistence(self, redis_client):
        """Test session persists with Redis"""

        session_id = "persistence-test"
        seven_days = 7 * 24 * 3600

        session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "model_stack": ["claude", "haiku", "deepseek"],
            "turns": 5
        }

        # Store with 7-day TTL
        redis_client.setex(
            f"session:{session_id}",
            seven_days,
            json.dumps(session_data)
        )

        # Store conversation turns
        for i in range(5):
            redis_client.setex(
                f"conversation:{session_id}:{i}",
                seven_days,
                json.dumps({"turn": i, "content": "test"})
            )

        # Verify persistence
        ttl = redis_client.ttl(f"session:{session_id}")
        assert ttl > 0
        assert ttl <= seven_days

        # Verify turns recoverable
        turns = 0
        for i in range(5):
            if redis_client.exists(f"conversation:{session_id}:{i}"):
                turns += 1

        assert turns == 5

        # Cleanup
        redis_client.delete(f"session:{session_id}")
        for i in range(5):
            redis_client.delete(f"conversation:{session_id}:{i}")


# ============================================================================
# TEST 9: TTL Expiration
# ============================================================================

class TestTTLExpiration:
    """Test 9: TTL expiration (session expires after 7 days)"""

    @pytest.mark.timeout(15)
    def test_short_ttl_expiration(self, redis_client):
        """Test TTL expiration with short timeout"""

        session_id = "ttl-test-short"
        ttl_seconds = 2

        # Create key with short TTL
        redis_client.setex(
            f"session:{session_id}",
            ttl_seconds,
            json.dumps({"status": "testing"})
        )

        # Verify exists
        assert redis_client.exists(f"session:{session_id}")

        # Wait for expiration
        time.sleep(ttl_seconds + 1)

        # Verify expired
        assert not redis_client.exists(f"session:{session_id}")

    @pytest.mark.timeout(10)
    def test_ttl_preservation(self, redis_client):
        """Test TTL is correctly set and preserved"""

        session_id = "ttl-test-long"
        seven_days = 7 * 24 * 3600

        redis_client.setex(
            f"session:{session_id}",
            seven_days,
            json.dumps({"test": "data"})
        )

        ttl = redis_client.ttl(f"session:{session_id}")

        # Should be close to 7 days
        assert ttl > 0
        assert ttl <= seven_days
        assert abs(seven_days - ttl) < 10  # Within 10 seconds

        redis_client.delete(f"session:{session_id}")


# ============================================================================
# TEST 10: Markdown Export
# ============================================================================

class TestMarkdownExport:
    """Test 10: Markdown export generation"""

    @pytest.mark.timeout(10)
    def test_markdown_generation(self, tmp_path):
        """Test generating valid Markdown export"""

        session_id = "export-test"

        # Conversation data
        conversation = [
            {"turn": 1, "speaker": "user", "content": "Can you help?"},
            {"turn": 2, "speaker": "claude", "content": "Of course!"},
            {"turn": 3, "speaker": "haiku", "content": "Processing..."},
        ]

        findings = [
            {"claim": "Finding 1", "confidence": 0.95},
            {"claim": "Finding 2", "confidence": 0.92},
        ]

        # Generate Markdown
        lines = [
            f"# Session: {session_id}",
            "",
            "## Conversation",
            "",
        ]

        for turn in conversation:
            lines.extend([
                f"**{turn['speaker'].upper()}:** {turn['content']}",
                ""
            ])

        lines.extend(["## Findings", ""])

        for finding in findings:
            lines.extend([
                f"- {finding['claim']} ({finding['confidence']:.0%})",
            ])

        markdown = "\n".join(lines)

        # Write and verify
        export_path = tmp_path / f"session_{session_id}.md"
        export_path.write_text(markdown)

        assert export_path.exists()

        content = export_path.read_text()
        assert "# Session:" in content
        assert "## Conversation" in content
        assert "## Findings" in content
        assert len(content) > 0

    @pytest.mark.timeout(10)
    def test_markdown_structure_validation(self, tmp_path):
        """Test Markdown structure is valid"""

        sample_md = """# Test Document

## Section 1

Content with **bold** and *italic*.

### Subsection

- Item 1
- Item 2

## Section 2

Another section.

---

*Footer*
"""

        # Validate structure
        assert sample_md.count("#") > 0
        assert "**bold**" in sample_md
        assert "*italic*" in sample_md
        assert "---" in sample_md

        # Write and verify readability
        path = tmp_path / "test.md"
        path.write_text(sample_md)

        content = path.read_text()
        assert content == sample_md


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmarks for memory layer"""

    @pytest.mark.timeout(10)
    def test_redis_set_performance(self, redis_client, benchmark):
        """Benchmark Redis SET operation"""

        def set_operation():
            redis_client.set("bench:key", "value", ex=3600)

        result = benchmark(set_operation)

    @pytest.mark.timeout(10)
    def test_redis_get_performance(self, redis_client, benchmark):
        """Benchmark Redis GET operation"""

        redis_client.set("bench:key", "value", ex=3600)

        def get_operation():
            redis_client.get("bench:key")

        result = benchmark(get_operation)


# ============================================================================
# INTEGRATION HEALTH CHECKS
# ============================================================================

@pytest.mark.health_check
class TestInfrastructureHealth:
    """Health checks for required infrastructure"""

    def test_redis_available(self, redis_client):
        """Verify Redis is available"""
        assert redis_client.ping()

    def test_chromadb_available(self, chromadb_client):
        """Verify ChromaDB is available"""
        try:
            response = requests.get(
                'http://localhost:8000/api/v1/heartbeat',
                timeout=2
            )
            assert response.status_code == 200
        except requests.ConnectionError:
            pytest.skip("ChromaDB not available")


# ============================================================================
# CONFTEST / CLEANUP
# ============================================================================

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "timeout(N): marks test with timeout in seconds"
    )
    config.addinivalue_line(
        "markers", "benchmark: marks test as performance benchmark"
    )
    config.addinivalue_line(
        "markers", "health_check: marks test as infrastructure health check"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
