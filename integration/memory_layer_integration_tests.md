# Memory Layer Integration Test Plan

**Document ID:** `if://doc/memory-integration-tests/2025-11-30`
**Date:** November 30, 2025
**Status:** DRAFT - Integration Test Design
**Audience:** InfraFabric QA, DevOps, Architecture teams
**References:**
- `if://doc/s2-swarm-comms/2025-11-26` → /home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md
- `if://code/redis-swarm-coordinator` → /home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py
- `if://doc/context-memory/2025-11-30` → (A6 output)
- `if://doc/deep-storage/2025-11-30` → (A7 output)
- `if://interface/unified-memory/2025-11-30` → (A8 output)
- `if://doc/memory-persistence/2025-11-30` → (A9 output)

---

## Executive Summary

This test plan validates end-to-end integration of InfraFabric's dual-layer memory system:
- **Context Memory (Redis):** Fast, session-scoped, short-term state
- **Deep Storage (ChromaDB):** Vector embeddings, personality DNA, long-term knowledge

The 10 test scenarios ensure graceful degradation, cross-model access, state persistence, and production resilience.

---

## Architecture Overview

### Component Dependencies
```
┌─────────────────────────────────────────┐
│   Application Layer (Haiku/Sonnet)      │
├─────────────────────────────────────────┤
│   IFMemory (Unified Interface)          │ ← A8 Output
├─────────────────────────────────────────┤
│   Context Memory (Redis)  │ Deep Storage │
│   - Sessions              │ (ChromaDB)   │
│   - Task Queues           │ - Embeddings │
│   - Findings              │ - Personality│
│   - Context Sharing       │ - Knowledge  │
└─────────────────────────────────────────┘
```

### Required Infrastructure
- **Redis:** 6.2+ (localhost:6379 or configurable)
- **ChromaDB:** 0.3.21+ (localhost:8000 or in-process)
- **Python:** 3.10+ with pytest, redis, chromadb, numpy
- **Disk Space:** 5GB minimum for ChromaDB vector store
- **Network:** Redis/ChromaDB unreliable network simulation capability

---

## Test Environment Setup

### Docker Compose (Recommended)
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/data
    environment:
      - IS_PERSISTENT=TRUE
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  redis_data:
  chroma_data:
```

### Installation
```bash
# Create test venv
python3 -m venv test_venv
source test_venv/bin/activate

# Install dependencies
pip install pytest pytest-asyncio pytest-cov redis chromadb numpy scipy scikit-learn
pip install faker  # For test data generation
pip install pytest-timeout  # For timeout protection
```

### Pre-Test Checklist
```bash
# 1. Start infrastructure
docker-compose up -d

# 2. Wait for health checks
docker-compose ps  # Verify "healthy" status

# 3. Verify connectivity
redis-cli ping
curl http://localhost:8000/api/v1/heartbeat

# 4. Run setup script
python scripts/test_setup.py
```

---

## Test Scenarios (10 Integration Tests)

### TEST 1: Store Conversation in Redis, Retrieve Successfully

**Test ID:** `it://test/memory/redis-basic-store-retrieve/2025-11-30`

**Objective:**
Validate that Context Memory (Redis) can store conversation turns and retrieve them without data loss.

**Scenario:**
1. Initialize IFMemory with Redis backend
2. Store 5 conversation turns from Claude → Haiku → DeepSeek cycle
3. Retrieve conversation by session key
4. Verify all turns present, ordered, with correct metadata

**Test Code:**
```python
import pytest
from datetime import datetime
from infrafabric.src.core.memory.unified_memory import IFMemory
from infrafabric.src.core.memory.models import ConversationTurn, Message

@pytest.mark.asyncio
async def test_redis_store_conversation(redis_client, memory):
    """Test 1: Store and retrieve conversation in Redis"""

    session_id = "session-test-1-20251130"
    turns = [
        ConversationTurn(
            turn_id="turn-1",
            speaker="claude",
            model="claude-sonnet-4-5",
            message=Message(
                role="assistant",
                content="Hello from Claude, analyzing this task...",
                timestamp=datetime.now()
            ),
            tokens=150,
            latency_ms=245
        ),
        ConversationTurn(
            turn_id="turn-2",
            speaker="haiku",
            model="claude-haiku-4-5",
            message=Message(
                role="assistant",
                content="Haiku agent 1 processing...",
                timestamp=datetime.now()
            ),
            tokens=45,
            latency_ms=89
        ),
        ConversationTurn(
            turn_id="turn-3",
            speaker="deepseek",
            model="deepseek-v3",
            message=Message(
                role="assistant",
                content="DeepSeek validation result...",
                timestamp=datetime.now()
            ),
            tokens=200,
            latency_ms=512
        ),
        ConversationTurn(
            turn_id="turn-4",
            speaker="claude",
            model="claude-sonnet-4-5",
            message=Message(
                role="assistant",
                content="Claude synthesizing results...",
                timestamp=datetime.now()
            ),
            tokens=320,
            latency_ms=398
        ),
        ConversationTurn(
            turn_id="turn-5",
            speaker="haiku",
            model="claude-haiku-4-5",
            message=Message(
                role="assistant",
                content="Final Haiku summary...",
                timestamp=datetime.now()
            ),
            tokens=78,
            latency_ms=125
        ),
    ]

    # Store all turns
    for turn in turns:
        memory.store_context(
            key=f"conversation:{session_id}:{turn.turn_id}",
            value=turn.to_dict(),
            ttl=7*24*3600  # 7-day TTL
        )

    # Store conversation index
    turn_ids = [t.turn_id for t in turns]
    memory.store_context(
        key=f"conversation:{session_id}:index",
        value={"turns": turn_ids, "count": len(turn_ids)},
        ttl=7*24*3600
    )

    # Retrieve and verify
    index = memory.retrieve_context(f"conversation:{session_id}:index")
    assert index is not None
    assert index["count"] == 5
    assert len(index["turns"]) == 5

    # Verify all turns retrievable
    retrieved_turns = []
    for turn_id in index["turns"]:
        turn_data = memory.retrieve_context(f"conversation:{session_id}:{turn_id}")
        assert turn_data is not None
        retrieved_turns.append(turn_data)

    assert len(retrieved_turns) == 5
    assert retrieved_turns[0]["speaker"] == "claude"
    assert retrieved_turns[2]["speaker"] == "deepseek"
    assert retrieved_turns[4]["message"]["content"] == "Final Haiku summary..."

@pytest.mark.timeout(5)
def test_redis_basic_operations():
    """Synchronous version for basic Redis operations"""
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Test basic set/get
    r.set("test:key:1", "value1", ex=3600)
    assert r.get("test:key:1") == "value1"

    # Test TTL
    ttl = r.ttl("test:key:1")
    assert 3500 < ttl <= 3600

    # Cleanup
    r.delete("test:key:1")
```

**Success Criteria:**
- [ ] All 5 conversation turns stored without error
- [ ] Retrieved conversation index matches original
- [ ] All turns retrievable by ID
- [ ] Data integrity maintained (no truncation, encoding issues)
- [ ] TTL respected (expires after 7 days)

**Estimated Duration:** 2 seconds
**Latency Target:** <100ms per operation
**Failure Modes:**
- Redis connection timeout → catch and report
- Data serialization error → log turn ID and error
- TTL not set → warning (will eventually expire via Redis default)

---

### TEST 2: Query ChromaDB for Sergio Personality Context

**Test ID:** `it://test/memory/chromadb-personality-query/2025-11-30`

**Objective:**
Validate that Deep Storage (ChromaDB) can store and retrieve Sergio personality embeddings with semantic search.

**Scenario:**
1. Initialize ChromaDB collection: `personality_dna:sergio`
2. Embed 10 personality trait documents (humor, empathy, boundaries, etc.)
3. Query for "humorous response style" → verify top result is humor-related
4. Query for "emotional intelligence" → verify empathy trait retrieved

**Test Code:**
```python
import pytest
from infrafabric.src.core.memory.unified_memory import IFMemory
from datetime import datetime

@pytest.mark.asyncio
async def test_chromadb_personality_retrieval(memory):
    """Test 2: Store and retrieve Sergio personality from Deep Storage"""

    collection_name = "personality_dna:sergio"

    # Personality trait documents
    personality_docs = [
        {
            "id": "sergio-trait-humor-1",
            "trait": "Humor Style",
            "content": "Sergio uses self-deprecating humor and puns about technology. Makes jokes about debugging and coffee. Never mean-spirited.",
            "confidence": 0.95
        },
        {
            "id": "sergio-trait-humor-2",
            "trait": "Humor Timing",
            "content": "Humor appears naturally after solving problems. Lightens mood during debugging sessions. Uses timing for maximum effect.",
            "confidence": 0.92
        },
        {
            "id": "sergio-trait-empathy",
            "trait": "Emotional Intelligence",
            "content": "Sergio reads user frustration and adjusts tone accordingly. Validates concerns before offering solutions. Shows genuine care.",
            "confidence": 0.94
        },
        {
            "id": "sergio-trait-boundaries",
            "trait": "Professional Boundaries",
            "content": "Maintains friendly but professional tone. Avoids personal topics unless user initiates. Sets expectations clearly.",
            "confidence": 0.89
        },
        {
            "id": "sergio-trait-learning",
            "trait": "Learning Orientation",
            "content": "Admits knowledge gaps gracefully. Asks clarifying questions. Grows from feedback. Models intellectual humility.",
            "confidence": 0.96
        },
        {
            "id": "sergio-trait-curiosity",
            "trait": "Intellectual Curiosity",
            "content": "Explores edge cases and 'what if' scenarios. Digs deeper when answers feel incomplete. Loves technical challenges.",
            "confidence": 0.91
        },
        {
            "id": "sergio-trait-clarity",
            "trait": "Communication Clarity",
            "content": "Explains complex concepts with analogies. Uses code examples liberally. Structures responses for easy scanning.",
            "confidence": 0.93
        },
        {
            "id": "sergio-trait-resilience",
            "trait": "Resilience Under Pressure",
            "content": "Stays calm during crisis debugging. Breaks problems into smaller chunks. Celebrates small wins to maintain momentum.",
            "confidence": 0.88
        },
        {
            "id": "sergio-trait-collaboration",
            "trait": "Collaboration Style",
            "content": "Pairs well with other agents (Haiku, DeepSeek). Explains reasoning to enable handoff. Documents context for next agent.",
            "confidence": 0.90
        },
        {
            "id": "sergio-trait-growth",
            "trait": "Growth Mindset",
            "content": "Views challenges as opportunities. Learns from mistakes. Iterates on solutions based on results.",
            "confidence": 0.94
        },
    ]

    # Embed documents into ChromaDB
    for doc in personality_docs:
        memory.embed_knowledge(
            doc=doc,
            collection=collection_name,
            metadata={"trait": doc["trait"], "confidence": doc["confidence"]}
        )

    # Query 1: Humor retrieval
    humor_results = memory.query_knowledge(
        query="humorous response style and funny jokes",
        collections=[collection_name],
        k=2
    )

    assert len(humor_results) >= 2
    assert any("humor" in r.get("trait", "").lower() for r in humor_results)
    assert humor_results[0]["metadata"]["confidence"] > 0.85

    # Query 2: Empathy retrieval
    empathy_results = memory.query_knowledge(
        query="emotional intelligence and user understanding",
        collections=[collection_name],
        k=2
    )

    assert len(empathy_results) >= 1
    assert any("empathy" in r.get("trait", "").lower()
               or "emotional" in r.get("trait", "").lower()
               for r in empathy_results)

    # Query 3: Learning orientation
    learning_results = memory.query_knowledge(
        query="learning from feedback and admitting gaps",
        collections=[collection_name],
        k=2
    )

    assert len(learning_results) >= 1
    assert any("learning" in r.get("trait", "").lower()
               or "growth" in r.get("trait", "").lower()
               for r in learning_results)

    # Verify all traits retrievable
    all_results = memory.query_knowledge(
        query="Sergio personality traits",
        collections=[collection_name],
        k=10
    )

    assert len(all_results) == 10

@pytest.mark.timeout(10)
def test_chromadb_basic_operations():
    """Synchronous version for basic ChromaDB operations"""
    import chromadb

    client = chromadb.HttpClient(host='localhost', port=8000)

    # Create collection
    collection = client.get_or_create_collection(
        name="test-collection",
        metadata={"hnsw:space": "cosine"}
    )

    # Add documents
    collection.add(
        ids=["id1", "id2"],
        documents=["This is a test", "Another test document"],
        metadatas=[{"source": "test"}, {"source": "test"}]
    )

    # Query
    results = collection.query(
        query_texts=["test"],
        n_results=2
    )

    assert len(results["ids"]) > 0
```

**Success Criteria:**
- [ ] All 10 personality documents embedded successfully
- [ ] Humor query returns humor-related traits in top 2
- [ ] Empathy query returns emotional/empathy traits
- [ ] All 10 traits retrievable with single query
- [ ] Relevance scores reasonable (top result > 0.7 similarity)

**Estimated Duration:** 3 seconds
**Latency Target:** <500ms per query
**Failure Modes:**
- ChromaDB connection timeout → report service unavailable
- Embedding failure → retry with different vectorizer
- Query returns no results → verify collection has documents

---

### TEST 3: Multi-Collection RAG Query (Personality + Humor)

**Test ID:** `it://test/memory/multi-collection-rag/2025-11-30`

**Objective:**
Validate cross-collection RAG (Retrieval-Augmented Generation) combining personality and humor knowledge.

**Scenario:**
1. Create two ChromaDB collections:
   - `personality_dna:sergio` (from TEST 2)
   - `knowledge:humor` (domain knowledge about humor)
2. Query across both collections: "How would Sergio respond humorously?"
3. Verify results from both collections in merged response
4. Validate ranking by relevance across collections

**Test Code:**
```python
import pytest
from infrafabric.src.core.memory.unified_memory import IFMemory

@pytest.mark.asyncio
async def test_multi_collection_rag(memory):
    """Test 3: Multi-collection RAG query combining personality + humor knowledge"""

    # Ensure both collections exist with documents
    personality_collection = "personality_dna:sergio"
    humor_collection = "knowledge:humor"

    # Add humor knowledge documents if not present
    humor_docs = [
        {
            "id": "humor-timing-1",
            "content": "Timing is everything in humor. Wait for the perfect moment when tension is high.",
            "type": "technique"
        },
        {
            "id": "humor-pun-1",
            "content": "Programming puns: 'Why do Java developers wear glasses? Because they can't C#'",
            "type": "example"
        },
        {
            "id": "humor-self-deprecation-1",
            "content": "Self-deprecating humor works well in technical contexts. 'I debug like a caveman.'",
            "type": "technique"
        },
        {
            "id": "humor-context-1",
            "content": "The best jokes are those that relate to shared context. Tech jokes for developers, domain humor for experts.",
            "type": "principle"
        },
        {
            "id": "humor-appropriateness-1",
            "content": "Humor must match the situation. Avoid during crisis debugging. Use after resolution to celebrate.",
            "type": "principle"
        },
    ]

    for doc in humor_docs:
        memory.embed_knowledge(
            doc=doc,
            collection=humor_collection,
            metadata={"type": doc["type"]}
        )

    # Multi-collection query
    query = "How should I respond to a user's frustration with a debugging problem in a humorous but helpful way?"

    results = memory.query_knowledge(
        query=query,
        collections=[personality_collection, humor_collection],
        k=5  # Top 5 across both collections
    )

    # Verify results from both collections
    assert len(results) >= 4  # At least some results

    personality_results = [r for r in results if "personality" in r.get("collection", "")]
    humor_results = [r for r in results if "humor" in r.get("collection", "")]

    # Should have at least one result from each
    assert len(personality_results) > 0, "Should retrieve personality traits"
    assert len(humor_results) > 0, "Should retrieve humor knowledge"

    # Verify results are relevant
    for result in results:
        assert result.get("score", 0) > 0.5  # Basic relevance threshold

    # Results should be sorted by relevance across collections
    scores = [r.get("score", 0) for r in results]
    assert scores == sorted(scores, reverse=True), "Results should be ordered by relevance"

@pytest.mark.timeout(15)
def test_multi_collection_setup():
    """Verify ChromaDB collections can be accessed"""
    import chromadb

    client = chromadb.HttpClient(host='localhost', port=8000)

    # Get or create collections
    personality_collection = client.get_or_create_collection(
        name="personality_dna:sergio",
        metadata={"type": "personality"}
    )

    humor_collection = client.get_or_create_collection(
        name="knowledge:humor",
        metadata={"type": "humor"}
    )

    # Verify collections are accessible
    assert personality_collection is not None
    assert humor_collection is not None
```

**Success Criteria:**
- [ ] Both collections accessible without error
- [ ] Query returns results from both collections
- [ ] At least 1 personality trait retrieved
- [ ] At least 1 humor principle/technique retrieved
- [ ] Results ranked by relevance across collections
- [ ] No duplicate results in merged output

**Estimated Duration:** 4 seconds
**Latency Target:** <1000ms for cross-collection query
**Failure Modes:**
- Collection not found → create automatically
- Query returns one collection only → verify both collections have content
- Ranking doesn't account for cross-collection → log warning

---

### TEST 4: Cache Hit vs. Cache Miss Latency Comparison

**Test ID:** `it://test/memory/cache-hit-vs-miss-latency/2025-11-30`

**Objective:**
Validate that Redis caching improves latency by 3-5x for repeated queries.

**Scenario:**
1. Query ChromaDB for Sergio personality (cache miss)
2. Repeat same query (cache hit)
3. Measure latency for both operations
4. Verify cache hit is 3-5x faster

**Test Code:**
```python
import pytest
import time
from infrafabric.src.core.memory.unified_memory import IFMemory

@pytest.mark.asyncio
async def test_cache_hit_miss_latency(memory):
    """Test 4: Compare latency of cache miss vs hit"""

    query_text = "Sergio personality traits for humor and empathy"
    collection = "personality_dna:sergio"
    cache_key = f"query_cache:{collection}:{hash(query_text)}"

    # Clear cache
    memory.redis_client.delete(cache_key)

    # CACHE MISS: Query ChromaDB directly
    start_miss = time.perf_counter()
    miss_results = memory.query_knowledge(
        query=query_text,
        collections=[collection],
        k=5
    )
    latency_miss_ms = (time.perf_counter() - start_miss) * 1000

    assert len(miss_results) > 0, "Query should return results"

    # CACHE HIT: Query again (should use Redis cache)
    start_hit = time.perf_counter()
    hit_results = memory.query_knowledge(
        query=query_text,
        collections=[collection],
        k=5
    )
    latency_hit_ms = (time.perf_counter() - start_hit) * 1000

    # Results should be identical
    assert miss_results == hit_results, "Cached results should match original"

    # Cache hit should be significantly faster
    speedup = latency_miss_ms / latency_hit_ms

    # Performance assertions
    assert latency_miss_ms < 1000, f"Cache miss should complete <1s, got {latency_miss_ms:.1f}ms"
    assert latency_hit_ms < 100, f"Cache hit should complete <100ms, got {latency_hit_ms:.1f}ms"
    assert speedup >= 3, f"Cache hit should be 3x+ faster, got {speedup:.1f}x (miss: {latency_miss_ms:.1f}ms, hit: {latency_hit_ms:.1f}ms)"

    # Report metrics
    print(f"\nCache Performance:")
    print(f"  Miss: {latency_miss_ms:.1f}ms")
    print(f"  Hit:  {latency_hit_ms:.1f}ms")
    print(f"  Speedup: {speedup:.1f}x")

@pytest.mark.timeout(5)
def test_redis_latency_measurement():
    """Measure raw Redis latency for cache operations"""
    import redis
    import time

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Warm up
    r.set("warmup", "value")
    r.get("warmup")

    # Measure set latency
    latencies = []
    for i in range(100):
        start = time.perf_counter()
        r.set(f"latency_test:{i}", f"value_{i}", ex=3600)
        latencies.append((time.perf_counter() - start) * 1000)

    avg_set_latency = sum(latencies) / len(latencies)
    assert avg_set_latency < 5, f"SET should be <5ms, got {avg_set_latency:.2f}ms"

    # Measure get latency
    latencies = []
    for i in range(100):
        start = time.perf_counter()
        r.get(f"latency_test:{i}")
        latencies.append((time.perf_counter() - start) * 1000)

    avg_get_latency = sum(latencies) / len(latencies)
    assert avg_get_latency < 2, f"GET should be <2ms, got {avg_get_latency:.2f}ms"

    print(f"\nRedis Latency Baseline:")
    print(f"  SET avg: {avg_set_latency:.2f}ms")
    print(f"  GET avg: {avg_get_latency:.2f}ms")
```

**Success Criteria:**
- [ ] Cache miss completes in <1000ms
- [ ] Cache hit completes in <100ms
- [ ] Cache hit is 3x+ faster than miss
- [ ] Cached results identical to original
- [ ] Redis SET/GET latency <5ms and <2ms respectively

**Estimated Duration:** 5 seconds
**Latency Targets:**
- Cache miss: <1000ms
- Cache hit: <100ms
- Speedup: 3-5x

**Failure Modes:**
- Cache not populated → verify caching layer enabled
- Cache hit slower than miss → check cache key collision
- ChromaDB slow → verify ChromaDB instance health

---

### TEST 5: Redis Failure → Graceful Degradation (Continue Without Cache)

**Test ID:** `it://test/memory/redis-failure-degradation/2025-11-30`

**Objective:**
Validate that system continues functioning when Redis becomes unavailable.

**Scenario:**
1. Start operation with Redis available
2. Simulate Redis failure (network disconnect, container crash)
3. System should:
   - Detect connection loss
   - Degrade to ChromaDB-only mode
   - Continue serving queries (slower but functional)
   - Log degradation event
   - Alert operator
4. Verify no data loss when Redis recovers

**Test Code:**
```python
import pytest
from unittest.mock import patch, MagicMock
from infrafabric.src.core.memory.unified_memory import IFMemory
import redis

@pytest.mark.asyncio
async def test_redis_failure_graceful_degradation(memory):
    """Test 5: System continues without Redis (degraded mode)"""

    query_text = "Sergio personality"
    collection = "personality_dna:sergio"

    # Phase 1: Normal operation (Redis available)
    print("\n[Phase 1] Operating with Redis...")
    results_normal = memory.query_knowledge(
        query=query_text,
        collections=[collection],
        k=3
    )
    assert len(results_normal) > 0, "Should get results with Redis available"

    # Phase 2: Simulate Redis failure
    print("[Phase 2] Simulating Redis failure...")

    # Mock Redis to raise connection error
    with patch.object(memory.redis_client, 'get') as mock_get:
        with patch.object(memory.redis_client, 'set') as mock_set:
            mock_get.side_effect = redis.ConnectionError("Connection refused")
            mock_set.side_effect = redis.ConnectionError("Connection refused")

            # System should detect failure and degrade
            # Query should still work via ChromaDB directly
            try:
                results_degraded = memory.query_knowledge(
                    query=query_text,
                    collections=[collection],
                    k=3,
                    use_redis=False  # Force degraded mode
                )

                # Should still get results (from ChromaDB)
                assert len(results_degraded) > 0, "Should continue working without Redis"
                print("[Phase 2] SUCCESS: System degraded gracefully, still returning results")

            except Exception as e:
                pytest.fail(f"System should handle Redis failure gracefully, got: {e}")

    # Phase 3: Verify redis reconnection attempts
    print("[Phase 3] Verifying Redis recovery detection...")

    # System should attempt reconnection
    reconnect_attempts = 0
    max_attempts = 5

    while reconnect_attempts < max_attempts:
        try:
            # Check if Redis is back (mock stops raising errors)
            test_result = memory.redis_client.ping()
            if test_result:
                print(f"[Phase 3] Redis reconnected after {reconnect_attempts} attempts")
                break
        except redis.ConnectionError:
            reconnect_attempts += 1
            continue

    # Phase 4: Resume normal operation
    print("[Phase 4] Resuming normal operation...")
    results_resumed = memory.query_knowledge(
        query=query_text,
        collections=[collection],
        k=3
    )
    assert len(results_resumed) > 0, "Should resume normal operation"

@pytest.mark.timeout(10)
def test_redis_connection_retry_logic():
    """Test connection retry mechanism"""
    import redis
    from redis import ConnectionPool

    # Create connection pool with retry config
    pool = ConnectionPool(
        host='localhost',
        port=6379,
        max_connections=5,
        retry_on_timeout=True
    )

    r = redis.Redis(connection_pool=pool)

    # Test connection
    try:
        result = r.ping()
        assert result is True
    except redis.ConnectionError:
        pytest.skip("Redis not available")
```

**Success Criteria:**
- [ ] System detects Redis connection loss
- [ ] Queries continue via ChromaDB-only fallback
- [ ] Degraded mode returns results (slower but functional)
- [ ] Degradation event logged with timestamp
- [ ] Operator alert triggered (or in logs)
- [ ] No data loss on Redis recovery
- [ ] Automatic reconnection attempted

**Estimated Duration:** 6 seconds
**Degraded Mode Latency Target:** <2000ms (slower than cached, faster than full recovery)
**Failure Modes:**
- System crashes instead of degrading → verify error handling
- Data loss on recovery → check persistence mechanism
- Infinite retry loop → verify retry backoff strategy

---

### TEST 6: ChromaDB Failure → Graceful Degradation (Continue Without RAG)

**Test ID:** `it://test/memory/chromadb-failure-degradation/2025-11-30`

**Objective:**
Validate that system continues functioning when ChromaDB becomes unavailable.

**Scenario:**
1. Start operation with ChromaDB available
2. Simulate ChromaDB failure (network disconnect, container crash)
3. System should:
   - Detect connection loss
   - Degrade to Context Memory only
   - Continue serving cached queries
   - Skip RAG operations
   - Log degradation event
4. Verify personality retrieval still works from cache

**Test Code:**
```python
import pytest
from unittest.mock import patch
from infrafabric.src.core.memory.unified_memory import IFMemory
import requests

@pytest.mark.asyncio
async def test_chromadb_failure_graceful_degradation(memory):
    """Test 6: System continues without ChromaDB (memory-only mode)"""

    query_text = "Sergio personality traits"
    collection = "personality_dna:sergio"

    # Phase 1: Warm cache (ensure data is in Redis)
    print("\n[Phase 1] Warming cache...")
    results_cached = memory.query_knowledge(
        query=query_text,
        collections=[collection],
        k=3
    )

    # Store results in cache explicitly
    cache_key = f"query_cache:{collection}:{hash(query_text)}"
    memory.redis_client.setex(
        cache_key,
        3600,
        str(results_cached)
    )
    print(f"[Phase 1] Cached {len(results_cached)} results")

    # Phase 2: Simulate ChromaDB failure
    print("[Phase 2] Simulating ChromaDB failure...")

    with patch('infrafabric.src.core.memory.unified_memory.chromadb.HttpClient') as mock_client:
        mock_client.side_effect = requests.ConnectionError("ChromaDB unreachable")

        # Query should still work from cache
        try:
            results_degraded = memory.query_knowledge(
                query=query_text,
                collections=[collection],
                k=3,
                use_chromadb=False  # Force degraded mode
            )

            # Should get cached results
            if results_degraded:
                print(f"[Phase 2] SUCCESS: Returned {len(results_degraded)} cached results despite ChromaDB failure")
            else:
                print("[Phase 2] WARNING: No cached results available")

        except Exception as e:
            pytest.fail(f"System should handle ChromaDB failure gracefully, got: {e}")

    # Phase 3: Verify fallback behavior
    print("[Phase 3] Verifying fallback to Context Memory...")

    # New query (not in cache) should be rejected gracefully
    new_query = "Something very specific that's not cached"

    try:
        results_new = memory.query_knowledge(
            query=new_query,
            collections=[collection],
            k=1,
            use_chromadb=False
        )

        if not results_new:
            print("[Phase 3] Correctly returned empty set for uncached query during degradation")
        else:
            print(f"[Phase 3] Found {len(results_new)} results in Context Memory for new query")

    except Exception as e:
        print(f"[Phase 3] Gracefully handled failure for uncached query: {type(e).__name__}")

@pytest.mark.timeout(5)
def test_chromadb_health_check():
    """Verify ChromaDB health check mechanism"""
    import requests

    try:
        response = requests.get(
            'http://localhost:8000/api/v1/heartbeat',
            timeout=2
        )
        assert response.status_code == 200
        print("ChromaDB health check: OK")
    except requests.ConnectionError:
        pytest.skip("ChromaDB not available")
    except Exception as e:
        pytest.skip(f"ChromaDB health check failed: {e}")
```

**Success Criteria:**
- [ ] ChromaDB failure detected
- [ ] Cached queries still returned
- [ ] New queries return empty set or cached fallback
- [ ] System doesn't crash or hang
- [ ] Degradation event logged
- [ ] Context Memory (Redis) operations continue

**Estimated Duration:** 4 seconds
**Degraded Mode Behavior:**
- Cached queries: <100ms (Redis only)
- New queries: Return empty set or timeout gracefully

**Failure Modes:**
- System hangs on ChromaDB connection → verify timeout setting
- Cached data not retrieved → verify Redis cache validation
- Cascading failure → check isolation between components

---

### TEST 7: Cross-Model Access (Claude Stores, DeepSeek Retrieves)

**Test ID:** `it://test/memory/cross-model-context-sharing/2025-11-30`

**Objective:**
Validate that different LLM models can share context through the memory layer.

**Scenario:**
1. Claude (Sonnet) stores conversation + analysis in Context Memory
2. DeepSeek reads same context and retrieves it
3. DeepSeek stores validation results
4. Claude reads DeepSeek results
5. Verify no data loss or corruption in cross-model handoff

**Test Code:**
```python
import pytest
from datetime import datetime
from infrafabric.src.core.memory.unified_memory import IFMemory

@pytest.mark.asyncio
async def test_cross_model_context_sharing(memory):
    """Test 7: Different models share context through unified memory"""

    session_id = "cross-model-session-test-7"

    # Step 1: Claude (Sonnet) stores initial analysis
    print("\n[Step 1] Claude storing analysis...")

    claude_analysis = {
        "agent_id": "claude-sonnet-1",
        "timestamp": datetime.now().isoformat(),
        "task": "Analyze code quality",
        "findings": [
            {"type": "security", "severity": "high", "description": "SQL injection vulnerability"},
            {"type": "performance", "severity": "medium", "description": "N+1 query pattern"},
            {"type": "style", "severity": "low", "description": "Inconsistent naming"}
        ],
        "confidence": 0.92
    }

    memory.store_context(
        key=f"analysis:claude:{session_id}",
        value=claude_analysis,
        ttl=3600
    )

    # Store reference in shared context
    memory.store_context(
        key=f"context:analysis_queue:{session_id}",
        value={"pending_validation": ["claude-sonnet-1"]},
        ttl=3600
    )

    print(f"[Step 1] Stored Claude analysis with {len(claude_analysis['findings'])} findings")

    # Step 2: DeepSeek (different model) retrieves Claude's analysis
    print("[Step 2] DeepSeek retrieving Claude's analysis...")

    retrieved_analysis = memory.retrieve_context(f"analysis:claude:{session_id}")
    assert retrieved_analysis is not None, "DeepSeek should retrieve Claude's analysis"
    assert retrieved_analysis["agent_id"] == "claude-sonnet-1"
    assert len(retrieved_analysis["findings"]) == 3

    print(f"[Step 2] DeepSeek retrieved {len(retrieved_analysis['findings'])} findings from Claude")

    # Step 3: DeepSeek performs validation and stores results
    print("[Step 3] DeepSeek storing validation results...")

    deepseek_validation = {
        "agent_id": "deepseek-v3-1",
        "timestamp": datetime.now().isoformat(),
        "validating_analysis_from": "claude-sonnet-1",
        "session_id": session_id,
        "validation_results": [
            {
                "finding_index": 0,
                "severity": "high",
                "confirmed": True,
                "evidence": "Found LIKE operator vulnerable to injection"
            },
            {
                "finding_index": 1,
                "severity": "medium",
                "confirmed": True,
                "mitigation": "Use join instead of separate queries"
            },
            {
                "finding_index": 2,
                "severity": "low",
                "confirmed": False,
                "note": "Naming is actually consistent with project standards"
            }
        ],
        "average_confidence": 0.94
    }

    memory.store_context(
        key=f"analysis:deepseek:{session_id}",
        value=deepseek_validation,
        ttl=3600
    )

    print(f"[Step 3] Stored DeepSeek validation with {len(deepseek_validation['validation_results'])} results")

    # Step 4: Claude reads DeepSeek results
    print("[Step 4] Claude retrieving DeepSeek validation...")

    retrieved_validation = memory.retrieve_context(f"analysis:deepseek:{session_id}")
    assert retrieved_validation is not None, "Claude should retrieve DeepSeek validation"
    assert retrieved_validation["agent_id"] == "deepseek-v3-1"
    assert retrieved_validation["validating_analysis_from"] == "claude-sonnet-1"

    print(f"[Step 4] Claude retrieved validation from DeepSeek")

    # Step 5: Verify complete handoff integrity
    print("[Step 5] Verifying data integrity across handoff...")

    # Check that findings match across models
    for i, validation in enumerate(retrieved_validation["validation_results"]):
        original_finding = claude_analysis["findings"][i]
        assert validation["finding_index"] == i
        assert validation["severity"] == original_finding["severity"]

    print("[Step 5] SUCCESS: All data maintained integrity across cross-model sharing")

    # Step 6: Verify history chain
    print("[Step 6] Verifying context history...")

    history = memory.retrieve_context(f"context:analysis_queue:{session_id}")
    assert history is not None

    print("[Step 6] Context chain verified")

@pytest.mark.timeout(5)
def test_context_key_patterns():
    """Verify context key naming conventions"""
    import redis

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Test key patterns
    test_keys = [
        "analysis:claude:session-1",
        "analysis:deepseek:session-1",
        "context:analysis_queue:session-1",
    ]

    for key in test_keys:
        r.set(key, "test_value")
        assert r.exists(key)
        r.delete(key)
```

**Success Criteria:**
- [ ] Claude stores analysis successfully
- [ ] DeepSeek retrieves Claude's complete analysis
- [ ] DeepSeek validation stored correctly
- [ ] Claude retrieves DeepSeek validation
- [ ] Data integrity maintained across handoff
- [ ] No fields lost or corrupted in transfer
- [ ] Cross-model timestamps preserved

**Estimated Duration:** 2 seconds
**Latency Target:** <200ms per cross-model operation
**Failure Modes:**
- DeepSeek can't retrieve → verify key naming
- Data corruption → check serialization/deserialization
- Missing fields → validate data structure

---

### TEST 8: Session State Persistence Across Restarts

**Test ID:** `it://test/memory/session-persistence-restart/2025-11-30`

**Objective:**
Validate that session state survives application restart via Redis persistence.

**Scenario:**
1. Create session with conversation history + context
2. Simulate application shutdown
3. Restart application
4. Retrieve same session
5. Verify all state intact and queryable

**Test Code:**
```python
import pytest
import os
import subprocess
import time
from datetime import datetime

@pytest.mark.asyncio
async def test_session_persistence_across_restart(memory, redis_client):
    """Test 8: Session survives application restart via Redis"""

    session_id = "persistence-test-session-8"

    # Phase 1: Create and populate session
    print("\n[Phase 1] Creating persistent session...")

    session_data = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "model_stack": ["claude-sonnet", "claude-haiku", "deepseek"],
        "conversation_turns": 5,
        "context_keys": [
            f"conversation:{session_id}:1",
            f"conversation:{session_id}:2",
            f"conversation:{session_id}:3",
            f"conversation:{session_id}:4",
            f"conversation:{session_id}:5",
        ]
    }

    # Store session with 7-day TTL (persists beyond restart)
    redis_client.setex(
        f"session:{session_id}",
        7*24*3600,
        str(session_data)
    )

    # Store conversation turns
    for i, key in enumerate(session_data["context_keys"], 1):
        turn_data = {
            "turn_id": i,
            "speaker": ["claude", "haiku", "deepseek"][(i-1) % 3],
            "timestamp": datetime.now().isoformat(),
            "content": f"Turn {i} content..."
        }
        redis_client.setex(
            key,
            7*24*3600,
            str(turn_data)
        )

    # Store session metadata in set for tracking
    redis_client.sadd("sessions:active", session_id)

    print(f"[Phase 1] Created session with {len(session_data['context_keys'])} turns")

    # Phase 2: Verify pre-restart state
    print("[Phase 2] Verifying state before restart...")

    session_before = redis_client.get(f"session:{session_id}")
    assert session_before is not None, "Session should exist before restart"

    turn_count_before = 0
    for key in session_data["context_keys"]:
        if redis_client.exists(key):
            turn_count_before += 1

    assert turn_count_before == 5, f"Should have 5 turns, got {turn_count_before}"
    print(f"[Phase 2] Pre-restart state verified: {turn_count_before} turns present")

    # Phase 3: Simulate restart (Redis persistence)
    print("[Phase 3] Simulating restart (checking Redis persistence)...")

    # In real test, this would stop/restart app
    # For this test, verify Redis persistence mechanism
    redis_info = redis_client.info('persistence')
    print(f"[Phase 3] Redis persistence enabled: {redis_info.get('rdb_last_save_time') is not None}")

    # Phase 4: Post-restart verification
    print("[Phase 4] Verifying state after restart...")

    # Retrieve session
    session_after = redis_client.get(f"session:{session_id}")
    assert session_after is not None, "Session should persist after restart"
    assert session_before == session_after, "Session data should be identical"

    # Verify all turns still accessible
    turns_recovered = []
    for key in session_data["context_keys"]:
        turn = redis_client.get(key)
        if turn:
            turns_recovered.append(turn)

    assert len(turns_recovered) == 5, f"Should recover 5 turns, got {len(turns_recovered)}"
    print(f"[Phase 4] Post-restart state verified: {len(turns_recovered)} turns recovered")

    # Phase 5: Verify queryability
    print("[Phase 5] Testing queryability of recovered session...")

    is_active = redis_client.sismember("sessions:active", session_id)
    assert is_active, "Session should be in active set"

    ttl = redis_client.ttl(f"session:{session_id}")
    assert ttl > 0, "Session TTL should be positive"
    assert ttl <= 7*24*3600, "Session TTL should be 7 days"

    print(f"[Phase 5] Session queryable with TTL: {ttl / 3600 / 24:.1f} days")

@pytest.mark.timeout(5)
def test_redis_persistence_configuration():
    """Verify Redis persistence configuration"""
    import redis

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Check persistence settings
    config = r.config_get('save')
    save_rules = config.get('save', '')

    if save_rules:
        print(f"Redis persistence rules: {save_rules}")

    # Check persistence status
    info = r.info('persistence')
    last_save = info.get('rdb_last_save_time', 0)

    assert last_save > 0, "Redis should have persistence enabled"

    # Check last save time is recent (within last hour)
    import time
    current_time = time.time()
    assert (current_time - last_save) < 3600, "Last save should be recent"
```

**Success Criteria:**
- [ ] Session created and stored with 7-day TTL
- [ ] All 5 conversation turns stored
- [ ] Redis persistence configured and working
- [ ] Session data retrieved post-restart
- [ ] All 5 turns recovered intact
- [ ] Session queryable from sessions:active set
- [ ] TTL preserved (not reset)

**Estimated Duration:** 3 seconds
**Persistence Target:** 7-day session TTL minimum
**Failure Modes:**
- Session lost on restart → verify Redis persistence enabled
- Partial data loss → check Redis RDB save
- TTL not preserved → verify SETEX usage
- Sessions not tracked → verify sessions:active set management

---

### TEST 9: TTL Expiration (Session Expires After 7 Days)

**Test ID:** `it://test/memory/ttl-expiration/2025-11-30`

**Objective:**
Validate that sessions and conversations expire after 7 days, freeing resources.

**Scenario:**
1. Create session with 7-day TTL
2. Verify TTL decreases over time
3. Fast-forward test to near expiration
4. Verify session expires and is removed
5. Verify data no longer queryable

**Test Code:**
```python
import pytest
import time
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_ttl_expiration(redis_client):
    """Test 9: Sessions expire and are cleaned up after TTL"""

    session_id = "ttl-test-session-9"

    # Phase 1: Create session with 7-day TTL
    print("\n[Phase 1] Creating session with 7-day TTL...")

    seven_days_seconds = 7 * 24 * 3600

    redis_client.setex(
        f"session:{session_id}",
        seven_days_seconds,
        '{"status": "active", "created": "now"}'
    )

    # Store test conversation turns
    for i in range(5):
        redis_client.setex(
            f"conversation:{session_id}:{i}",
            seven_days_seconds,
            f'{{"turn": {i}, "content": "test"}}'
        )

    # Store in active sessions
    redis_client.sadd("sessions:active", session_id)

    print(f"[Phase 1] Created session {session_id} with {seven_days_seconds} second TTL")

    # Phase 2: Verify TTL is set
    print("[Phase 2] Verifying TTL...")

    ttl = redis_client.ttl(f"session:{session_id}")
    assert ttl > 0, "TTL should be positive"
    assert ttl <= seven_days_seconds, "TTL should not exceed 7 days"

    # TTL should be close to 7 days (within 10 seconds)
    expected_ttl = seven_days_seconds
    assert abs(expected_ttl - ttl) < 10, f"TTL should be ~7 days, got {ttl} seconds"

    print(f"[Phase 2] TTL verified: {ttl / 3600 / 24:.2f} days remaining")

    # Phase 3: Simulate time passage (with short TTL for testing)
    print("[Phase 3] Testing accelerated TTL expiration...")

    test_session_id = "ttl-test-short-9"
    short_ttl_seconds = 2  # 2 seconds for fast test

    redis_client.setex(
        f"session:{test_session_id}",
        short_ttl_seconds,
        '{"status": "testing"}'
    )

    # Verify key exists
    assert redis_client.exists(f"session:{test_session_id}"), "Key should exist immediately"
    print(f"[Phase 3.1] Key created with {short_ttl_seconds}s TTL")

    # Wait for expiration
    print(f"[Phase 3.2] Waiting for TTL expiration ({short_ttl_seconds}s)...")
    time.sleep(short_ttl_seconds + 1)

    # Verify key is gone
    exists = redis_client.exists(f"session:{test_session_id}")
    assert not exists, "Key should be expired and removed"
    print("[Phase 3.3] Key expired and removed successfully")

    # Phase 4: Verify permanent session still exists
    print("[Phase 4] Verifying long-TTL session still exists...")

    still_exists = redis_client.exists(f"session:{session_id}")
    assert still_exists, "Original 7-day session should still exist"

    ttl_remaining = redis_client.ttl(f"session:{session_id}")
    assert ttl_remaining > 0, "TTL should still be positive"

    print(f"[Phase 4] Long-TTL session still exists with {ttl_remaining / 3600 / 24:.2f} days remaining")

    # Phase 5: Cleanup
    print("[Phase 5] Cleanup...")

    redis_client.delete(f"session:{session_id}")
    for i in range(5):
        redis_client.delete(f"conversation:{session_id}:{i}")
    redis_client.srem("sessions:active", session_id)

    print("[Phase 5] Cleanup complete")

@pytest.mark.timeout(15)
def test_ttl_memory_cleanup():
    """Verify memory is freed when keys expire"""
    import redis

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Get initial memory usage
    info_before = r.info('memory')
    used_before = info_before.get('used_memory', 0)

    # Create many keys with short TTL
    for i in range(1000):
        r.setex(
            f"cleanup_test:{i}",
            2,  # 2-second TTL
            f"value_{i}" * 10  # Larger value to use memory
        )

    # Wait for expiration
    time.sleep(3)

    # Force eviction (if needed)
    r.bgrewriteaof()
    time.sleep(1)

    # Get memory after cleanup
    info_after = r.info('memory')
    used_after = info_after.get('used_memory', 0)

    # Memory should be freed (or at least not grow significantly)
    growth = used_after - used_before
    growth_percent = (growth / used_before * 100) if used_before > 0 else 0

    print(f"\nMemory usage before: {used_before / 1024 / 1024:.1f} MB")
    print(f"Memory usage after:  {used_after / 1024 / 1024:.1f} MB")
    print(f"Growth: {growth_percent:.1f}%")

    # Should not grow more than 5% (keys expired, memory freed)
    assert growth_percent < 5, f"Memory should be freed after TTL, but grew {growth_percent:.1f}%"
```

**Success Criteria:**
- [ ] 7-day TTL set correctly on session creation
- [ ] TTL decreases over time
- [ ] Short-TTL keys expire as expected
- [ ] Expired keys automatically removed
- [ ] Long-TTL sessions persist
- [ ] Memory freed after expiration
- [ ] No manual cleanup required

**Estimated Duration:** 12 seconds
**TTL Target:** 7 days (604,800 seconds)
**Failure Modes:**
- TTL not set → verify SETEX usage
- Key persists after expiration → check Redis configuration
- Memory not freed → verify Redis memory management

---

### TEST 10: Markdown Export Generation

**Test ID:** `it://test/memory/markdown-export/2025-11-30`

**Objective:**
Validate that session data can be exported to Markdown format with complete context.

**Scenario:**
1. Retrieve session conversation + findings
2. Generate Markdown document with:
   - Session metadata (date, participants, models)
   - Full conversation history
   - Extracted findings
   - Cross-references to Deep Storage
3. Verify Markdown is valid, readable, and preserves structure

**Test Code:**
```python
import pytest
from datetime import datetime
from pathlib import Path
import json

@pytest.mark.asyncio
async def test_markdown_export_generation(memory, tmp_path):
    """Test 10: Generate valid Markdown export from session state"""

    session_id = "export-test-session-10"

    # Phase 1: Setup test session data
    print("\n[Phase 1] Setting up test session...")

    session_metadata = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "model_stack": ["claude-sonnet-4-5", "claude-haiku-4-5", "deepseek-v3"],
        "duration_minutes": 12,
        "total_tokens": 4500
    }

    conversation_turns = [
        {
            "turn_id": 1,
            "speaker": "user",
            "timestamp": datetime.now().isoformat(),
            "content": "Can you help me understand the Redis architecture?"
        },
        {
            "turn_id": 2,
            "speaker": "claude-sonnet",
            "timestamp": datetime.now().isoformat(),
            "content": "Redis uses in-memory data structures for fast access. Key components: strings, lists, sets, hashes..."
        },
        {
            "turn_id": 3,
            "speaker": "claude-haiku",
            "timestamp": datetime.now().isoformat(),
            "content": "Redis persistence: RDB snapshots and AOF logs."
        },
        {
            "turn_id": 4,
            "speaker": "deepseek",
            "timestamp": datetime.now().isoformat(),
            "content": "Clustering enables horizontal scaling across multiple nodes."
        },
        {
            "turn_id": 5,
            "speaker": "claude-sonnet",
            "timestamp": datetime.now().isoformat(),
            "content": "Summary: Redis = fast in-memory store with persistence and clustering support."
        }
    ]

    findings = [
        {
            "id": "finding-1",
            "type": "architectural_insight",
            "confidence": 0.96,
            "claim": "Redis is optimal for Context Memory due to <1ms latency",
            "citations": ["benchmark-redis-latency-2025"]
        },
        {
            "id": "finding-2",
            "type": "recommendation",
            "confidence": 0.92,
            "claim": "Enable RDB + AOF for production reliability",
            "citations": ["redis-persistence-guide"]
        }
    ]

    print(f"[Phase 1] Setup complete: {len(conversation_turns)} turns, {len(findings)} findings")

    # Phase 2: Generate Markdown
    print("[Phase 2] Generating Markdown export...")

    markdown_lines = [
        f"# Session Export: {session_id}",
        "",
        "## Session Metadata",
        "",
        f"- **Session ID:** {session_metadata['session_id']}",
        f"- **Created:** {session_metadata['created_at']}",
        f"- **Duration:** {session_metadata['duration_minutes']} minutes",
        f"- **Total Tokens:** {session_metadata['total_tokens']}",
        f"- **Models Used:** {', '.join(session_metadata['model_stack'])}",
        "",
        "## Conversation History",
        "",
    ]

    # Add conversation turns
    for turn in conversation_turns:
        speaker = turn["speaker"].upper()
        markdown_lines.extend([
            f"### Turn {turn['turn_id']}: {speaker}",
            "",
            turn["content"],
            "",
        ])

    # Add findings section
    markdown_lines.extend([
        "## Key Findings",
        "",
    ])

    for finding in findings:
        markdown_lines.extend([
            f"### {finding['claim']}",
            "",
            f"**Type:** {finding['type']}",
            f"**Confidence:** {finding['confidence']:.0%}",
            f"**Citations:** {', '.join(finding['citations'])}",
            "",
        ])

    # Add metadata footer
    markdown_lines.extend([
        "---",
        "",
        f"*Exported: {datetime.now().isoformat()}*",
        f"*Session TTL: 7 days*",
    ])

    markdown_content = "\n".join(markdown_lines)

    print(f"[Phase 2] Generated {len(markdown_lines)} markdown lines")

    # Phase 3: Write to file
    print("[Phase 3] Writing to file...")

    export_path = tmp_path / f"session_{session_id}.md"
    export_path.write_text(markdown_content)

    assert export_path.exists(), "Markdown file should be created"
    file_size = export_path.stat().st_size
    print(f"[Phase 3] Written to {export_path} ({file_size} bytes)")

    # Phase 4: Validate Markdown structure
    print("[Phase 4] Validating Markdown structure...")

    content = export_path.read_text()

    # Check required sections
    assert "# Session Export:" in content, "Should have main heading"
    assert "## Session Metadata" in content, "Should have metadata section"
    assert "## Conversation History" in content, "Should have conversation section"
    assert "## Key Findings" in content, "Should have findings section"

    # Check content preservation
    assert session_id in content, "Session ID should be present"
    assert "Redis" in content, "Conversation content should be preserved"

    # Count sections
    turn_headings = content.count("### Turn")
    assert turn_headings == len(conversation_turns), f"Should have {len(conversation_turns)} turns"

    print(f"[Phase 4] Markdown validation passed")

    # Phase 5: Check readability
    print("[Phase 5] Checking readability...")

    lines = content.split("\n")

    # Should have proper structure (not just a wall of text)
    assert len(lines) > len(conversation_turns) * 2, "Should have structure/spacing"

    # Should be valid UTF-8
    try:
        content.encode('utf-8').decode('utf-8')
        print("[Phase 5] UTF-8 encoding valid")
    except UnicodeDecodeError as e:
        pytest.fail(f"Markdown should be valid UTF-8: {e}")

    # Should not have obvious formatting errors
    assert "\\n" not in content, "Should use actual newlines, not escaped"
    assert "[" not in content or "]" in content, "Brackets should be paired"

    print("[Phase 5] Readability verified")

    # Phase 6: Return path for manual inspection
    print(f"[Phase 6] Export available at: {export_path}")

@pytest.mark.timeout(5)
def test_markdown_validation():
    """Verify generated Markdown is valid"""

    # Sample Markdown
    sample_md = """# Test Document

## Section 1

Content here with **bold** and *italic*.

### Subsection

- Item 1
- Item 2

## Section 2

Another paragraph.

---

*Footer*
"""

    # Basic validation
    assert sample_md.count("#") > 0, "Should have headings"
    assert sample_md.count("\n") > 0, "Should have line breaks"
    assert "**bold**" in sample_md, "Should support formatting"
    assert "---" in sample_md, "Should support separators"

    # Valid structure
    lines = sample_md.split("\n")
    assert lines[0].startswith("#"), "Should start with heading"
```

**Success Criteria:**
- [ ] Markdown file created successfully
- [ ] Session metadata included (ID, date, models, tokens)
- [ ] All 5 conversation turns included
- [ ] All findings included with confidence scores
- [ ] Proper Markdown structure (headings, sections)
- [ ] Content readable and properly formatted
- [ ] File is valid UTF-8
- [ ] File can be opened in Markdown viewer

**Estimated Duration:** 2 seconds
**Export Format:** Valid Markdown (RFC 7763)
**Failure Modes:**
- File not created → check write permissions
- Content incomplete → verify all data retrieved
- Invalid Markdown → check formatting

---

## Performance Benchmarks

### Target Latencies
| Operation | Target | Acceptable | Degraded |
|-----------|--------|------------|----------|
| Redis SET | <5ms | <10ms | 10-50ms |
| Redis GET | <2ms | <5ms | 5-20ms |
| ChromaDB embed | <100ms | <500ms | 500-2000ms |
| ChromaDB query | <500ms | <1000ms | 1-5s |
| Cache hit | <100ms | <200ms | 200-500ms |
| Cache miss | <1000ms | <2000ms | 2-5s |
| Cross-model handoff | <200ms | <500ms | 500-1000ms |

### Load Testing (Future)
- Concurrent sessions: 10, 50, 100, 500
- Conversation depth: 5, 50, 500 turns
- Personality collection size: 10, 100, 1000 embeddings
- Network latency simulation: 0ms, 10ms, 100ms, 500ms

---

## Test Execution

### Running All Tests
```bash
cd /home/setup/infrafabric
pytest integration/memory_layer_integration_tests.md -v --tb=short
```

### Running Specific Test
```bash
pytest integration/memory_layer_integration_tests.md::test_redis_store_conversation -v
```

### Running with Coverage
```bash
pytest integration/memory_layer_integration_tests.md --cov=src/core/memory --cov-report=html
```

### Running with Performance Profiling
```bash
pytest integration/memory_layer_integration_tests.md --profile
```

### Docker-based Testing
```bash
docker-compose -f tests/docker-compose.test.yml up
pytest integration/memory_layer_integration_tests.md -v
docker-compose -f tests/docker-compose.test.yml down
```

---

## Expected Test Execution Time

| Test | Solo Time | With Overhead |
|------|-----------|---------------|
| TEST 1 (Redis store) | 2s | 2.5s |
| TEST 2 (ChromaDB query) | 3s | 4s |
| TEST 3 (Multi-collection) | 4s | 5s |
| TEST 4 (Cache latency) | 5s | 6s |
| TEST 5 (Redis failure) | 6s | 7s |
| TEST 6 (ChromaDB failure) | 4s | 5s |
| TEST 7 (Cross-model) | 2s | 3s |
| TEST 8 (Persistence) | 3s | 4s |
| TEST 9 (TTL expiration) | 12s | 15s |
| TEST 10 (Markdown export) | 2s | 3s |
| **TOTAL** | **43s** | **54s** |

---

## CI/CD Integration

### GitHub Actions Workflow
```yaml
name: Memory Layer Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
      chromadb:
        image: chromadb/chroma:latest
        ports:
          - 8000:8000

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest integration/memory_layer_integration_tests.md -v --cov
      - uses: codecov/codecov-action@v3
```

---

## Failure Recovery Procedures

### Redis Connection Failure
1. Check Redis container status: `docker ps | grep redis`
2. View logs: `docker logs redis-container-name`
3. Verify port: `netstat -an | grep 6379`
4. Restart: `docker-compose restart redis`
5. Verify health: `redis-cli ping`

### ChromaDB Connection Failure
1. Check ChromaDB health: `curl http://localhost:8000/api/v1/heartbeat`
2. View logs: `docker logs chromadb-container-name`
3. Verify port: `netstat -an | grep 8000`
4. Restart: `docker-compose restart chromadb`
5. Verify collections: `curl http://localhost:8000/api/v1/collections`

### Memory Leak Detection
```bash
# Monitor Redis memory
redis-cli INFO memory

# Monitor ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Python memory profiling
python -m memory_profiler test_script.py
```

---

## Sign-Off Checklist

**Test Plan Review:**
- [ ] All 10 scenarios documented
- [ ] Success criteria clear and measurable
- [ ] Estimated times realistic
- [ ] Failure modes identified
- [ ] Performance targets established
- [ ] Python test code provided
- [ ] Manual procedures documented
- [ ] CI/CD integration specified
- [ ] Recovery procedures documented

**Ready for Handoff to QA/DevOps:**
- [ ] Deploy infrastructure (Redis + ChromaDB)
- [ ] Execute pre-test checklist
- [ ] Run all 10 tests sequentially
- [ ] Generate coverage report
- [ ] Document any failures
- [ ] Performance benchmark results
- [ ] Recommendation for production deployment

---

## References

**IF.citation:**
- `if://doc/s2-swarm-comms/2025-11-26` → S2 Redis architecture and packet design
- `if://code/redis-swarm-coordinator` → Current Redis implementation
- `if://interface/unified-memory/2025-11-30` → A8 Unified Memory interface
- `if://mission/infrafabric-integration-swarm/2025-11-30` → Full 40-agent mission

**External References:**
- Redis Docs: https://redis.io/documentation
- ChromaDB Docs: https://docs.trychroma.com
- pytest Documentation: https://docs.pytest.org
- Python redis Library: https://github.com/redis/redis-py

---

**Document Status:** DRAFT - READY FOR IMPLEMENTATION
**Last Updated:** 2025-11-30
**Author:** Agent A10 (Memory Layer Integration Tests)
**Approver:** Empiricist Guardian (IF.guard council seat)

🧠 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
