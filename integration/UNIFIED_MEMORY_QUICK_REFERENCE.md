# UnifiedMemory Quick Reference

**Fast lookup guide for developers integrating UnifiedMemory with their models.**

---

## Import and Initialize

```python
from unified_memory import UnifiedMemory

memory = UnifiedMemory(
    redis_host="localhost",
    redis_port=6379,
    chromadb_host="localhost",
    chromadb_port=8000,
    enable_memory_fallback=True  # Recommended: always use fallback
)
```

---

## Method Quick Reference

### 1. Store Conversation (Redis)
```python
op = memory.store_conversation(
    model_id="claude-max",      # Unique model identifier
    session_id="session-001",   # User session
    messages=[                  # List of message dicts
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
    ]
)
# Returns: MemoryOperation
# Status: SUCCESS/PARTIAL/DEGRADED/FAILED
# TTL: 1 hour (configurable)
```

**When to use:** Every time you receive or generate a message

---

### 2. Retrieve Conversation (Redis)
```python
messages = memory.retrieve_conversation(
    model_id="claude-max",
    session_id="session-001"
)
# Returns: List[Dict] or None
# If found: [{"role": "user", "content": "..."}, ...]
# If not found: None
```

**When to use:** At start of session to load conversation history

---

### 3. Retrieve Context (ChromaDB RAG)
```python
context = memory.retrieve_context(
    query="What does the user prefer?",
    collections=["personality", "knowledge", "findings"],
    n_results=3
)
# Returns: List[Dict]
# Format: [
#   {
#     "collection": "personality",
#     "document": "Sergio is witty and direct",
#     "metadata": {...},
#     "distance": 0.15
#   },
#   ...
# ]
```

**When to use:** Before generating a response, to inject context

**Collections to use:**
- `personality` - Character/persona traits
- `rhetorical` - Communication patterns
- `knowledge` - Domain knowledge
- `findings` - Stored insights
- `consensus` - Multi-model agreements

---

### 4. Store Finding (Redis + ChromaDB)
```python
op = memory.store_finding({
    "finding_id": f"find_{int(time.time())}",
    "content": "Users prefer shorter responses",
    "source_model": "claude-max",
    "session_id": "session-001",
    "confidence": 0.92,  # 0.0 to 1.0
    "tags": ["ux-insight", "user-preference"]
})
# Returns: MemoryOperation
# TTL: 24 hours (stored in both Redis and ChromaDB)
```

**When to use:** When generating an important insight to preserve

**Confidence scores:**
- 0.0-0.33: Low confidence, exploratory
- 0.33-0.66: Medium confidence, likely
- 0.66-1.0: High confidence, validated

---

### 5. Store Session State (Redis)
```python
op = memory.store_session_state(
    session_id="session-001",
    state_data={
        "user_id": "user-123",
        "communication_style": "casual",
        "context_level": "advanced",
        "language": "en",
        "timezone": "America/New_York"
    },
    ttl_seconds=3600  # Optional, defaults to conversation_ttl
)
# Returns: MemoryOperation
```

**When to use:** After analyzing user preferences

**Common state fields:**
- `user_id` - User identifier
- `communication_style` - "casual", "formal", "technical"
- `context_level` - "beginner", "intermediate", "advanced"
- `language` - "en", "es", "fr", etc.
- `tone` - "serious", "humorous", "empathetic"
- `session_start` - ISO timestamp

---

### 6. Get Session State (Redis)
```python
state = memory.get_session_state("session-001")
# Returns: Dict or None
# Format: {
#   "user_id": "user-123",
#   "communication_style": "casual",
#   "updated_at": "2025-11-30T19:30:45.123456"
# }
```

**When to use:** Before responding, to check user preferences

---

## Error Handling Pattern

```python
try:
    op = memory.store_conversation("model", session_id, messages)

    if op.status == MemoryOperationStatus.SUCCESS:
        logger.info(f"Stored to {[b.value for b in op.backends_used]}")
    elif op.status == MemoryOperationStatus.PARTIAL:
        logger.warning(f"Partial storage: {op.warning}")
    elif op.status == MemoryOperationStatus.DEGRADED:
        logger.warning(f"Degraded mode (falling back): {op.warning}")
    elif op.status == MemoryOperationStatus.FAILED:
        logger.error(f"Storage failed: {op.error}")

except Exception as e:
    # This should rarely happen with graceful degradation enabled
    logger.error(f"Unexpected error: {e}")
```

---

## Health Checking

```python
health = memory.get_health_status()

if health["redis"]["connected"]:
    print("Redis is available")
if health["chromadb"]["connected"]:
    print("ChromaDB is available")

print(f"Fallback in-memory conversations: {health['memory_fallback']['conversations']}")
```

---

## Common Integration Patterns

### Pattern 1: OpenWebUI Pipe Function
```python
class MyFunction:
    def __init__(self):
        self.memory = UnifiedMemory()

    def pipe(self, body: dict) -> Generator[str, None, None]:
        session_id = body.get("session_id", "default")
        messages = body.get("messages", [])

        # 1. Store conversation
        self.memory.store_conversation("my-model", session_id, messages)

        # 2. Get session preferences
        state = self.memory.get_session_state(session_id)

        # 3. Retrieve context
        query = messages[-1]["content"] if messages else ""
        context = self.memory.retrieve_context(
            query=query,
            collections=["personality", "knowledge"],
            n_results=3
        )

        # 4. Generate response
        response = self.generate_response(messages, context, state)

        # 5. Store important findings
        if self.should_save_as_finding(response):
            self.memory.store_finding({
                "finding_id": f"find_{int(time.time())}",
                "content": response,
                "source_model": "my-model",
                "session_id": session_id,
                "confidence": 0.85,
                "tags": ["generated-insight"]
            })

        yield response
```

### Pattern 2: Multi-Model Consensus
```python
def get_consensus(query, session_id):
    memory = UnifiedMemory()

    # Get insights from all models
    findings = memory.retrieve_context(
        query=query,
        collections=["claude-findings", "deepseek-findings", "gemini-findings"],
        n_results=3
    )

    # Aggregate by confidence
    high_confidence = [f for f in findings if f["metadata"]["confidence"] > 0.8]

    # Store consensus
    if high_confidence:
        memory.store_finding({
            "finding_id": f"consensus_{int(time.time())}",
            "content": f"Consensus from {len(high_confidence)} models",
            "source_model": "system",
            "session_id": session_id,
            "confidence": 0.95,
            "tags": ["consensus", "multi-model"]
        })

    return high_confidence
```

### Pattern 3: Personality DNA Injection
```python
def inject_personality(query, session_id):
    memory = UnifiedMemory()

    # Get personality DNA
    personality = memory.retrieve_context(
        query=query,
        collections=["personality", "rhetorical", "humor"],
        n_results=5
    )

    # Build personality prompt
    prompt = "You are Sergio. Characteristics:\n"
    for item in personality:
        prompt += f"- {item['document']}\n"

    return prompt
```

---

## Performance Tips

1. **Batch operations when possible**
   ```python
   # ✅ Good: Store once
   memory.store_conversation("model", session_id, all_messages)

   # ❌ Avoid: Multiple stores per message
   for msg in messages:
       memory.store_conversation("model", session_id, [msg])
   ```

2. **Cache session state**
   ```python
   # ✅ Good: Get once, use multiple times
   state = memory.get_session_state(session_id)
   for _ in range(5):
       # Use cached state

   # ❌ Avoid: Getting repeatedly
   for _ in range(5):
       state = memory.get_session_state(session_id)
   ```

3. **Use specific collections in retrieve_context**
   ```python
   # ✅ Good: Query relevant collections only
   context = memory.retrieve_context(query, ["personality"], n_results=3)

   # ❌ Avoid: Querying all collections
   context = memory.retrieve_context(query, ["all-collections"], n_results=10)
   ```

4. **Set appropriate confidence scores**
   ```python
   # ✅ Good: Realistic confidence
   memory.store_finding({...confidence: 0.75...})

   # ❌ Avoid: Always max confidence
   memory.store_finding({...confidence: 1.0...})
   ```

---

## Monitoring and Debugging

### Check Backend Status
```python
health = memory.get_health_status()
print(json.dumps(health, indent=2))
```

### Verify Stored Data
```python
# Retrieve immediately after storing
op = memory.store_conversation("model", session, messages)
retrieved = memory.retrieve_conversation("model", session)
assert retrieved == messages  # Verify round-trip
```

### Monitor Operation Performance
```python
op = memory.store_conversation("model", session, messages)
print(f"Latency: {op.latency_ms:.2f}ms")
print(f"Backends: {[b.value for b in op.backends_used]}")
print(f"Status: {op.status.value}")
```

---

## Troubleshooting

### "Redis not found"
```
Solution: Make sure Redis is running
docker run -d -p 6379:6379 redis:7-alpine
```

### "ChromaDB connection failed"
```
Solution: Make sure ChromaDB is running
docker run -d -p 8000:8000 chromadb/chroma:latest
```

### All data lost (no fallback active)
```
Prevention: Always enable enable_memory_fallback=True
memory = UnifiedMemory(enable_memory_fallback=True)
```

### Context window too large
```
Solution: Reduce max_context_messages
memory = UnifiedMemory(max_context_messages=50)
```

### Stale session data
```
Solution: Reduce TTL
memory = UnifiedMemory(conversation_ttl_seconds=1800)  # 30 minutes
```

---

## Cleanup

```python
# Always close connections
memory.close()

# Or use context manager pattern (if implemented)
with UnifiedMemory() as memory:
    # Use memory
    pass
# Automatically cleaned up
```

---

## Integration Checklist

- [ ] Import UnifiedMemory
- [ ] Initialize in __init__ with fallback enabled
- [ ] Store conversations after each exchange
- [ ] Retrieve context before generating responses
- [ ] Store important findings with confidence scores
- [ ] Check session state for user preferences
- [ ] Call memory.close() on shutdown
- [ ] Monitor health status in logs
- [ ] Test both backend-available and degraded modes
- [ ] Handle MemoryOperationStatus appropriately

---

**For detailed documentation, see:** `/home/setup/infrafabric/integration/UNIFIED_MEMORY_IMPLEMENTATION.md`
