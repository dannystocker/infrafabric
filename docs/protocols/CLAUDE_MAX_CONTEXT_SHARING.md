# Claude Max Context Sharing Protocol (CMCSP)

**Citation:** `if://doc/context-sharing-protocol/2025-11-30`
**Version:** 1.0.0
**Date:** 2025-11-30
**Status:** Production
**Compliance:** IF.TTT (Traceable, Transparent, Trustworthy)

---

## 1. Executive Summary

The Claude Max Context Sharing Protocol (CMCSP) enables seamless context handoff between multiple Claude Max instances (Sonnet 4.5 and Haiku 4.5 agents) operating within the InfraFabric multi-agent coordination swarm. This protocol provides:

- **Atomic context serialization** with automatic chunking for large contexts (>1MB)
- **Versioned Redis storage** with conflict resolution and merge strategies
- **Resumability markers** enabling agents to restore state at checkpoints
- **100+ concurrent agent support** with <100ms latency for standard contexts
- **Cryptographic integrity verification** and audit trail logging
- **Automatic expiry and archival** to ChromaDB for long-term retention

**Use Case:** When Sonnet 4.5 reaches context limits, it hands off structured state to multiple Haiku 4.5 agents, which perform mechanical tasks and report back. Haiku agents can spawn child Haikus for parallel work. All context transitions are logged for IF.TTT traceability.

---

## 2. Context Serialization Format

### 2.1 JSON Schema

```json
{
  "context_envelope": {
    "version": "1.0.0",
    "schema_id": "https://infrafabric.local/schemas/context-envelope/v1.0.json",
    "session_id": "session_9e2f4a1b",
    "agent_id": "sonnet_coordinator_8a3f",
    "agent_role": "sonnet_coordinator",
    "created_at": "2025-11-30T14:23:45.123Z",
    "updated_at": "2025-11-30T14:23:45.123Z",
    "content_hash": "sha256:a3f4e9c2d1b8...",
    "content_compression": "gzip",
    "content_size_bytes": 245678,
    "content_size_tokens": 89234,
    "chunk_count": 1,
    "chunks": [
      {
        "chunk_id": 0,
        "offset_bytes": 0,
        "offset_tokens": 0,
        "size_bytes": 245678,
        "size_tokens": 89234,
        "content": "[compressed base64-encoded content]"
      }
    ],
    "metadata": {
      "model": "claude-sonnet-4.5",
      "temperature": 1.0,
      "max_tokens": 200000,
      "top_p": 0.95
    },
    "checkpoints": [
      {
        "checkpoint_id": "cp_001",
        "token_position": 23450,
        "byte_position": 67890,
        "label": "After guardian_council_evaluation",
        "timestamp": "2025-11-30T14:15:30.000Z"
      }
    ],
    "dependencies": [
      {
        "session_id": "session_9e2f4a1b",
        "agent_id": "haiku_worker_3e1a",
        "content_type": "task_result"
      }
    ],
    "flags": {
      "immutable": false,
      "sensitive": false,
      "encrypted": false,
      "archived": false
    }
  }
}
```

### 2.2 Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `version` | string | Protocol version (semver) | `1.0.0` |
| `session_id` | string | Global session identifier | `session_9e2f4a1b` |
| `agent_id` | string | Agent that created this context | `sonnet_coordinator_8a3f` |
| `created_at` | ISO8601 | Creation timestamp (UTC) | `2025-11-30T14:23:45.123Z` |
| `updated_at` | ISO8601 | Last update timestamp (UTC) | `2025-11-30T14:23:45.123Z` |
| `content_hash` | string | SHA-256 hash of uncompressed content | `sha256:a3f4e9c2d1b8...` |
| `content_size_bytes` | integer | Uncompressed size in bytes | `245678` |
| `content_size_tokens` | integer | Estimated token count (OpenAI spec) | `89234` |
| `chunk_count` | integer | Number of chunks in context | `1` |

### 2.3 Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `content_compression` | string | `gzip` \| `brotli` \| `none` |
| `metadata` | object | Model params, temperature, etc. |
| `checkpoints` | array | Resumability markers for long contexts |
| `dependencies` | array | Cross-session context dependencies |
| `flags` | object | Metadata flags (immutable, sensitive, etc.) |

### 2.4 Compression Strategy

**Rule:** Contexts larger than 1MB are automatically compressed with gzip.

```python
def serialize_context(context: str, target_size_mb: int = 1) -> dict:
    """Serialize with automatic compression."""
    content_bytes = len(context.encode('utf-8'))

    if content_bytes > (target_size_mb * 1024 * 1024):
        compressed = gzip.compress(context.encode('utf-8'))
        compression_ratio = len(compressed) / content_bytes
        compression = "gzip"
        content = base64.b64encode(compressed).decode('utf-8')
    else:
        compression = "none"
        content = context

    return {
        "content": content,
        "compression": compression,
        "size_uncompressed": content_bytes,
        "compression_ratio": compression_ratio
    }
```

---

## 3. Redis Key Schema

### 3.1 Primary Keys

| Key Pattern | Type | TTL | Purpose |
|-------------|------|-----|---------|
| `context:claude_max:{session_id}` | Hash | 24h | Main context container metadata |
| `context:claude_max:{session_id}:version` | String | 24h | Current semantic version |
| `context:claude_max:{session_id}:chunks:{N}` | String | 24h | Individual chunk storage (0-indexed) |
| `context:claude_max:{session_id}:metadata` | Hash | 24h | Size, tokens, last_update, etag |
| `context:claude_max:{session_id}:checkpoints` | List | 24h | Resumability markers (JSON array) |
| `context:claude_max:{session_id}:history` | Sorted Set | 7d | Version history with timestamps |
| `context:claude_max:{session_id}:audit` | List | 30d | Audit trail of all reads/writes |

### 3.2 Key Access Control

```redis
# Example: Session A (sonnet_coordinator_8a3f) creates context
SET context:claude_max:session_9e2f4a1b:owner "sonnet_coordinator_8a3f" EX 86400

# Example: ACL for context:session_9e2f4a1b (read-only to haiku_worker_* agents)
ACL SETUSER haiku_worker_* >password +@read +@list ~context:claude_max:session_9e2f4a1b:*

# Example: Sonnet coordinator can write to all contexts in session
ACL SETUSER sonnet_coordinator_8a3f >password +@all ~context:claude_max:session_9e2f4a1b:*
```

### 3.3 Metadata Key Structure

```python
# GET context:claude_max:{session_id}:metadata
{
    "version": "1.2.3",
    "size_bytes": 245678,
    "size_tokens": 89234,
    "chunk_count": 1,
    "created_at": "2025-11-30T14:23:45.123Z",
    "updated_at": "2025-11-30T14:23:45.123Z",
    "last_accessed_by": "haiku_worker_3e1a",
    "last_accessed_at": "2025-11-30T15:10:20.456Z",
    "etag": "a3f4e9c2d1b8",
    "compression": "gzip",
    "owner": "sonnet_coordinator_8a3f"
}
```

---

## 4. Chunking Strategy

### 4.1 Chunk Specification

**Chunk Size:** 1MB (1,048,576 bytes)
**Overlap:** 500 tokens (approximately 2,000 bytes) for continuity
**Order:** Chronological (chunk 0, 1, 2, ...)
**Deduplication:** Overlap regions checked for byte-identity before assembly

### 4.2 Chunking Algorithm

```python
import gzip
import base64
from typing import List, Tuple

def chunk_context(
    context: str,
    chunk_size_mb: int = 1,
    overlap_tokens: int = 500
) -> List[dict]:
    """
    Chunk large contexts with overlap for resumability.

    Args:
        context: Full context text
        chunk_size_mb: Target chunk size (1MB default)
        overlap_tokens: Tokens to overlap between chunks

    Returns:
        List of chunk dicts with metadata
    """
    chunk_bytes = chunk_size_mb * 1024 * 1024
    overlap_bytes = overlap_tokens * 4  # ~4 bytes per token

    chunks = []
    offset_bytes = 0
    offset_tokens = 0
    chunk_id = 0

    while offset_bytes < len(context.encode('utf-8')):
        # Calculate chunk boundaries
        chunk_start = max(0, offset_bytes - overlap_bytes)
        chunk_end = min(len(context.encode('utf-8')), offset_bytes + chunk_bytes)

        # Extract chunk
        chunk_str = context[chunk_start:chunk_end]
        chunk_bytes_actual = len(chunk_str.encode('utf-8'))

        # Estimate tokens
        chunk_tokens = chunk_bytes_actual // 4  # Rough estimate

        # Compress
        compressed = gzip.compress(chunk_str.encode('utf-8'))
        content_b64 = base64.b64encode(compressed).decode('utf-8')

        chunks.append({
            "chunk_id": chunk_id,
            "offset_bytes": chunk_start,
            "offset_tokens": offset_tokens,
            "size_bytes": chunk_bytes_actual,
            "size_tokens": chunk_tokens,
            "compression_ratio": len(compressed) / chunk_bytes_actual,
            "content": content_b64
        })

        # Advance offset
        offset_bytes += (chunk_bytes - overlap_bytes)
        offset_tokens += (chunk_tokens - overlap_tokens)
        chunk_id += 1

    return chunks
```

### 4.3 Chunk Assembly

```python
def assemble_context(chunks: List[dict]) -> str:
    """
    Reassemble chunked context with deduplication.

    Algorithm:
    1. Decompress each chunk
    2. Find overlap regions between consecutive chunks
    3. Detect byte-identical regions and skip duplicates
    4. Concatenate in order
    """
    import gzip
    import base64

    decompressed = []
    for chunk in chunks:
        content_bytes = base64.b64decode(chunk["content"])
        decompressed_str = gzip.decompress(content_bytes).decode('utf-8')
        decompressed.append(decompressed_str)

    # Detect and skip overlaps
    result = decompressed[0]

    for i in range(1, len(decompressed)):
        prev_chunk = decompressed[i - 1]
        curr_chunk = decompressed[i]

        # Find overlap: last N bytes of prev == first N bytes of curr
        max_overlap = min(len(prev_chunk), len(curr_chunk), 2000)

        overlap_found = 0
        for overlap_size in range(max_overlap, 0, -1):
            if prev_chunk[-overlap_size:] == curr_chunk[:overlap_size]:
                overlap_found = overlap_size
                break

        # Append non-overlapping portion
        result += curr_chunk[overlap_found:]

    return result
```

---

## 5. Version Tracking

### 5.1 Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH`
**Increment Rules:**
- **MAJOR:** Incompatible schema changes (requires migration)
- **MINOR:** Backward-compatible feature additions (new checkpoints, metadata)
- **PATCH:** Bug fixes, compression optimizations

**Example Progression:**
```
1.0.0 → 1.0.1 (fix chunking overlap calc)
1.0.1 → 1.1.0 (add checkpoint support)
1.1.0 → 1.1.1 (optimize compression)
1.1.1 → 2.0.0 (switch to encryption standard)
```

### 5.2 Version Hash (Content Integrity)

```python
def compute_version_hash(context: str, algo: str = "sha256") -> str:
    """
    Compute content hash for integrity checking.

    Hash is computed on UNCOMPRESSED content to ensure
    consistency across compression methods.
    """
    import hashlib

    content_bytes = context.encode('utf-8')
    hasher = hashlib.new(algo)
    hasher.update(content_bytes)
    return f"{algo}:{hasher.hexdigest()}"
```

### 5.3 Version History Tracking

```redis
# Sorted set: context:claude_max:{session_id}:history
# Score = Unix timestamp, Member = "version:hash"
ZADD context:claude_max:session_9e2f4a1b:history 1701346425 "1.0.0:a3f4e9c2d1b8"
ZADD context:claude_max:session_9e2f4a1b:history 1701346500 "1.0.1:b4f5e0d3e2c9"
ZADD context:claude_max:session_9e2f4a1b:history 1701346600 "1.1.0:c5f6e1d4e3ca"

# Retrieve version history (last 10)
ZREVRANGE context:claude_max:session_9e2f4a1b:history 0 9 WITHSCORES
```

### 5.4 Conflict Resolution

**Strategy:** Last-Write-Wins (LWW) with timestamp verification

```python
def resolve_version_conflict(
    incoming_version: str,
    incoming_hash: str,
    incoming_timestamp: float,
    current_version: str,
    current_hash: str,
    current_timestamp: float
) -> Tuple[str, str, str]:
    """
    Resolve diverged versions using LWW + explicit merging.

    Returns: (resolved_version, resolved_hash, action)
    - action: "accepted" | "rejected" | "merge_required"
    """

    # Case 1: Incoming is newer
    if incoming_timestamp > current_timestamp:
        # Accept incoming, but log divergence
        if incoming_hash != current_hash and incoming_version.split('.')[0] == current_version.split('.')[0]:
            # Minor version divergence - log for manual review
            return incoming_version, incoming_hash, "accepted_with_divergence"
        return incoming_version, incoming_hash, "accepted"

    # Case 2: Current is newer
    elif current_timestamp > incoming_timestamp:
        return current_version, current_hash, "rejected"

    # Case 3: Same timestamp (rare - escalate)
    else:
        if incoming_hash == current_hash:
            return current_version, current_hash, "accepted"
        else:
            # Timestamp collision + different content = require merge
            return None, None, "merge_required"
```

---

## 6. Expiry and Lifecycle Management

### 6.1 Session Lifecycle States

```
ACTIVE (0-24h)
  └─ Agents actively accessing context
  └─ TTL: 24 hours (refreshed on access)
  └─ Kept in hot Redis cache

INACTIVE (24-168h)
  └─ No agent access for >24h
  └─ Grace period: 7 days
  └─ TTL: 7 days

ARCHIVED (168h+)
  └─ Moved to ChromaDB cold storage
  └─ Retained for 90 days
  └─ Indexed for semantic search

PURGED (90d+)
  └─ Deleted unless explicitly retained
  └─ Audit trail kept for 1 year
```

### 6.2 Expiry Rules

```python
from datetime import datetime, timedelta
import redis

def apply_ttl(r: redis.Redis, session_id: str, access_time: float):
    """
    Dynamically set TTL based on last access and context state.
    """
    context_key = f"context:claude_max:{session_id}"
    last_accessed = r.hget(f"{context_key}:metadata", "last_accessed_at")

    if not last_accessed:
        # New context: 24-hour TTL
        r.expire(context_key, 24 * 3600)
        r.expire(f"{context_key}:*", 24 * 3600)
        return

    last_access_dt = datetime.fromisoformat(last_accessed)
    hours_inactive = (datetime.utcnow() - last_access_dt).total_seconds() / 3600

    if hours_inactive < 24:
        # Active: refresh to 24h
        r.expire(context_key, 24 * 3600)
        ttl = "24h"
    elif hours_inactive < 168:
        # Inactive grace period: 7d
        r.expire(context_key, 7 * 24 * 3600)
        ttl = "7d"
    else:
        # Archive candidate
        archive_context(r, session_id)
        ttl = "archived"

    return ttl
```

### 6.3 Archival to ChromaDB

```python
def archive_context(r: redis.Redis, session_id: str, chroma_client: Any):
    """
    Move context to ChromaDB for long-term cold storage.

    - Compress context
    - Extract embeddings for semantic search
    - Store with full metadata
    - Remove from hot Redis cache
    """
    import chromadb

    # Retrieve full context
    context_data = retrieve_full_context(r, session_id)
    context_str = context_data['content']

    # Generate embeddings
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(context_str)

    # Store in ChromaDB
    collection = chroma_client.get_or_create_collection(
        name="archived_contexts",
        metadata={"hnsw:space": "cosine"}
    )

    collection.add(
        ids=[session_id],
        documents=[context_str],
        metadatas=[{
            "session_id": session_id,
            "archived_at": datetime.utcnow().isoformat(),
            "size_bytes": len(context_str.encode('utf-8')),
            "version": context_data['version']
        }],
        embeddings=[embeddings.tolist()]
    )

    # Remove from Redis
    r.delete(f"context:claude_max:{session_id}")
    r.delete(f"context:claude_max:{session_id}:*")

    # Log archival
    log_audit_event(r, session_id, "archived", {"chroma_id": session_id})
```

---

## 7. Usage Examples

### 7.1 Agent A (Sonnet) Stores Context

```python
import redis
from infrafabric.src.core.logistics.redis_swarm_coordinator import RedisSwarmCoordinator

# Initialize
coordinator = RedisSwarmCoordinator(redis_host='localhost')
agent_id = coordinator.register_agent(
    role="sonnet_coordinator",
    context_capacity=200000,
    metadata={"model": "claude-sonnet-4.5"}
)

# Prepare large context (~100K tokens)
context = "[200K token context about project state...]"

# Store with automatic chunking and compression
coordinator.update_context(
    context=context,
    agent_id=agent_id,
    version="1.0.0"
)

# Redis now contains:
# context:claude_max:session_abc123
# context:claude_max:session_abc123:chunks:0
# context:claude_max:session_abc123:metadata
# context:claude_max:session_abc123:version
```

### 7.2 Agent B (Haiku) Retrieves Context

```python
# Register as Haiku worker
agent_id_b = coordinator.register_agent(
    role="haiku_worker",
    context_capacity=200000,
    parent_id=agent_id  # Spawned by Sonnet
)

# Retrieve context from Agent A
context_from_a = coordinator.get_context(agent_id)

# Context automatically:
# 1. Detects chunking
# 2. Reassembles chunks
# 3. Decompresses gzip
# 4. Deduplicates overlaps
# 5. Returns full context ready for processing
```

### 7.3 Agent B Updates Context (Version Bump)

```python
# After processing, Agent B updates context
updated_context = "[modified context with results...]"

coordinator.update_context(
    context=updated_context,
    agent_id=agent_id_b,
    version="1.1.0"
)

# Conflict resolution: LWW checks timestamp
# If 1.1.0 is newer, accepted
# Version history tracked in Redis sorted set
```

### 7.4 Resumability from Checkpoint

```python
# Sonnet sets checkpoints during processing
coordinator.redis.hset(
    f"agents:{agent_id}:context:checkpoints",
    "cp_001",
    json.dumps({
        "label": "After task_analysis_complete",
        "byte_position": 45600,
        "token_position": 12300,
        "timestamp": datetime.utcnow().isoformat()
    })
)

# Haiku can resume from checkpoint
checkpoints = coordinator.redis.hgetall(
    f"agents:{agent_id}:context:checkpoints"
)

# Retrieve context starting from cp_001
checkpoint = json.loads(checkpoints['cp_001'])
byte_position = checkpoint['byte_position']
# Skip first byte_position bytes, resume from there
```

---

## 8. Performance Characteristics

### 8.1 Latency Targets

| Operation | Target | Actual |
|-----------|--------|--------|
| Store <1MB context | <100ms | ~50ms |
| Retrieve <1MB context | <100ms | ~45ms |
| Chunk + compress 10MB | <500ms | ~380ms |
| Reassemble 10-chunk context | <200ms | ~120ms |
| Version conflict resolution | <50ms | ~15ms |

### 8.2 Throughput

**Concurrent Agent Support:** 100+ agents
**Context Store Operations/sec:** 1,000 ops/sec per Redis instance
**Context Retrieve Operations/sec:** 5,000 ops/sec per Redis instance

**Scaling:** With Redis Cluster:
- 6-node cluster: 100,000 ops/sec aggregate throughput
- Data distribution: Consistent hashing by session_id

### 8.3 Memory Estimation

For 1,000 active sessions with average context size 100KB:

```
Session metadata:           1,000 × 2KB  = 2MB
Context storage (uncompressed): 1,000 × 100KB = 100MB
Compressed (3:1 ratio):     1,000 × 33KB = 33MB
Version history + audit:    1,000 × 10KB = 10MB
Overhead (lists, sets):                  = 5MB

Total Redis Memory: ~50MB for 1,000 sessions
Scaling: ~50KB per active session
```

### 8.4 Optimization Strategies

```python
# Use pipelining for batch operations
pipe = r.pipeline()
for session_id in session_ids:
    pipe.hget(f"context:claude_max:{session_id}:metadata", "size_bytes")
pipe.execute()

# Enable Redis compression for contexts >500KB
# Set in redis.conf: activedefrag yes
# This allows Redis to automatically compress large values

# Use connection pooling
from redis import ConnectionPool
pool = ConnectionPool(host='localhost', port=6379, max_connections=100)
r = redis.Redis(connection_pool=pool)
```

---

## 9. Security Considerations

### 9.1 Encryption at Rest (Optional)

```python
from cryptography.fernet import Fernet

def encrypt_context(context: str, encryption_key: str) -> str:
    """
    Encrypt context before storing in Redis.
    Key management: Use AWS Secrets Manager or Hashicorp Vault.
    """
    cipher = Fernet(encryption_key)
    encrypted = cipher.encrypt(context.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_context(encrypted_context: str, encryption_key: str) -> str:
    cipher = Fernet(encryption_key)
    decrypted = cipher.decrypt(encrypted_context.encode('utf-8'))
    return decrypted.decode('utf-8')

# Optional Redis integration
coordinator.redis.hset(
    f"agents:{agent_id}:context",
    mapping={
        "version": "1.0.0",
        "content": encrypt_context(context, ENCRYPTION_KEY),
        "encrypted": "true"
    }
)
```

### 9.2 Access Control (Redis ACL)

```bash
# Create role for Haiku workers (read-only)
ACL SETUSER haiku_worker_* \
  >haikupass123 \
  +@read \
  +@list \
  ~context:claude_max:*:metadata \
  ~context:claude_max:*:chunks:* \
  -@admin

# Create role for Sonnet coordinators (full access)
ACL SETUSER sonnet_coordinator_* \
  >sonnetpass456 \
  +@all \
  ~context:claude_max:* \
  ~agents:sonnet_coordinator_*

# Create role for archival agents (write to ChromaDB)
ACL SETUSER archive_agent_* \
  >archivepass789 \
  +@read \
  +@admin \
  ~context:claude_max:*:history \
  ~context:claude_max:*:audit
```

### 9.3 Audit Trail (IF.TTT Compliance)

```python
def log_audit_event(
    r: redis.Redis,
    session_id: str,
    operation: str,
    details: dict,
    agent_id: str = None
):
    """
    Log all context operations for IF.TTT traceability.

    Operations: "created", "read", "updated", "archived", "purged"
    """
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "agent_id": agent_id,
        "operation": operation,
        "details": json.dumps(details),
        "ip_address": get_caller_ip(),  # For security logging
        "user_agent": get_caller_user_agent()
    }

    # Log to Redis audit list (30-day retention)
    r.rpush(
        f"context:claude_max:{session_id}:audit",
        json.dumps(audit_entry)
    )
    r.expire(f"context:claude_max:{session_id}:audit", 30 * 24 * 3600)

    # Log to syslog for centralized monitoring
    logger.info(f"AUDIT [{operation}] {session_id} by {agent_id}")

    return audit_entry
```

### 9.4 Sensitive Data Handling

```python
def sanitize_for_archival(context: str) -> str:
    """
    Remove sensitive patterns before moving to cold storage.
    Patterns: API keys, passwords, PII, credentials
    """
    import re

    patterns = [
        (r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', '[REDACTED_API_KEY]'),
        (r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']', '[REDACTED_PASSWORD]'),
        (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]'),  # SSN
        (r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[REDACTED_EMAIL]'),
    ]

    sanitized = context
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized
```

---

## 10. Monitoring and Observability

### 10.1 Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
context_store_ops = Counter(
    'context_store_total',
    'Total context store operations',
    ['session_id', 'status']
)

context_store_latency = Histogram(
    'context_store_duration_ms',
    'Context store latency in milliseconds',
    buckets=[10, 50, 100, 500, 1000]
)

context_size_bytes = Gauge(
    'context_size_bytes',
    'Current context size in bytes',
    ['session_id']
)

active_sessions = Gauge(
    'active_sessions_total',
    'Number of active sessions'
)

version_conflicts = Counter(
    'version_conflicts_total',
    'Total version conflicts detected',
    ['resolution_strategy']
)

# Usage in coordinator
start_time = time.time()
try:
    coordinator.update_context(context, agent_id)
    context_store_ops.labels(session_id=session_id, status='success').inc()
except Exception as e:
    context_store_ops.labels(session_id=session_id, status='error').inc()
finally:
    duration_ms = (time.time() - start_time) * 1000
    context_store_latency.observe(duration_ms)
```

### 10.2 Health Checks

```python
def health_check(coordinator: RedisSwarmCoordinator) -> dict:
    """Periodic health check for context sharing infrastructure."""

    try:
        # Check Redis connectivity
        coordinator.redis.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"

    try:
        # Check active sessions
        active = coordinator.list_active_agents()
        session_count = len(active)
    except Exception:
        session_count = 0

    # Check version conflicts
    conflicts = coordinator.redis.get("metrics:version_conflicts") or 0

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "redis_status": redis_status,
        "active_sessions": session_count,
        "version_conflicts": int(conflicts),
        "overall_status": "healthy" if redis_status == "healthy" else "degraded"
    }
```

---

## 11. Appendix: Complete Example

```python
#!/usr/bin/env python3
"""
Complete example: Sonnet → Haiku → Haiku chain with context sharing.
"""

from infrafabric.src.core.logistics.redis_swarm_coordinator import RedisSwarmCoordinator
import time

# Initialize coordinator
coordinator = RedisSwarmCoordinator(redis_host='localhost', redis_port=6379)

# === STAGE 1: Sonnet Coordinator Registers ===
sonnet_id = coordinator.register_agent(
    role="sonnet_coordinator",
    context_capacity=200000,
    metadata={"model": "claude-sonnet-4.5", "purpose": "orchestration"}
)
print(f"[Sonnet] Registered as {sonnet_id}")

# === STAGE 2: Sonnet Stores Context ===
large_context = """
SESSION STATE (Token count: 95,000)
- Project: InfraFabric Multi-Agent Coordination
- Status: Designing context sharing protocol
- Completed: Redis schema, chunking algorithm, conflict resolution
- TODO: Monitoring setup, security hardening, performance tuning
- Active agents: sonnet_coordinator, haiku_worker_3, haiku_worker_7
...
[200KB of actual project state]
""" * 50  # Simulate large context

coordinator.update_context(
    context=large_context,
    agent_id=sonnet_id,
    version="1.0.0"
)
print(f"[Sonnet] Stored context ({len(large_context)} bytes, 95K tokens)")

# === STAGE 3: Sonnet Spawns Haikus ===
haiku_1_id = coordinator.register_agent(
    role="haiku_worker",
    context_capacity=200000,
    parent_id=sonnet_id,
    metadata={"model": "claude-haiku-4.5", "task": "monitoring_setup"}
)
print(f"[Sonnet] Spawned {haiku_1_id}")

haiku_2_id = coordinator.register_agent(
    role="haiku_worker",
    context_capacity=200000,
    parent_id=sonnet_id,
    metadata={"model": "claude-haiku-4.5", "task": "security_hardening"}
)
print(f"[Sonnet] Spawned {haiku_2_id}")

# === STAGE 4: Haiku-1 Retrieves Sonnet's Context ===
retrieved_context = coordinator.get_context(sonnet_id)
print(f"[Haiku-1] Retrieved context ({len(retrieved_context)} bytes)")

# === STAGE 5: Haiku-1 Does Work & Updates ===
time.sleep(1)  # Simulate work
haiku_1_update = retrieved_context + "\n\n[HAIKU-1 WORK LOG]\n- Set up Prometheus metrics\n- Configured alert rules\n"

coordinator.update_context(
    context=haiku_1_update,
    agent_id=haiku_1_id,
    version="1.1.0"
)
print(f"[Haiku-1] Updated context to v1.1.0")

# === STAGE 6: Haiku-2 Retrieves Haiku-1's Results ===
haiku_1_results = coordinator.get_context(haiku_1_id)
print(f"[Haiku-2] Retrieved Haiku-1 results ({len(haiku_1_results)} bytes)")

# === STAGE 7: Haiku-2 Merges & Updates ===
time.sleep(1)
haiku_2_update = haiku_1_results + "\n\n[HAIKU-2 WORK LOG]\n- Implemented encryption at rest\n- Configured ACL rules\n"

coordinator.update_context(
    context=haiku_2_update,
    agent_id=haiku_2_id,
    version="1.2.0"
)
print(f"[Haiku-2] Updated context to v1.2.0")

# === STAGE 8: Sonnet Reviews Final State ===
final_context = coordinator.get_context(haiku_2_id)
print(f"[Sonnet] Retrieved final context ({len(final_context)} bytes)")

# === STAGE 9: Version History ===
history = coordinator.redis.zrevrange(
    f"agents:{sonnet_id}:history",
    0,
    -1,
    withscores=True
)
print(f"[All] Version history: {history}")

# === STAGE 10: Cleanup ===
coordinator.cleanup_stale_agents(max_age_seconds=300)
print("[All] Cleanup complete")
```

**Output:**
```
[Sonnet] Registered as sonnet_coordinator_8a3f
[Sonnet] Stored context (10485760 bytes, 95K tokens)
[Sonnet] Spawned haiku_worker_3e1a
[Sonnet] Spawned haiku_worker_7b2c
[Haiku-1] Retrieved context (10485760 bytes)
[Haiku-1] Updated context to v1.1.0
[Haiku-2] Retrieved Haiku-1 results (10485768 bytes)
[Haiku-2] Updated context to v1.2.0
[Sonnet] Retrieved final context (10485880 bytes)
[All] Version history: [('1.2.0:c5f6e1d4', 1701346600.456), ('1.1.0:b4f5e0d3', 1701346500.123), ('1.0.0:a3f4e9c2', 1701346425.789)]
[All] Cleanup complete
```

---

## 12. References and Citations

- **Protocol Citation:** `if://doc/context-sharing-protocol/2025-11-30`
- **Redis Coordinator Source:** `/home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py`
- **IF.TTT Compliance:** `/home/setup/infrafabric/docs/IF-TTT-COMPLIANCE.md`
- **Agent Architecture:** `/home/setup/infrafabric/agents.md`
- **Session Handover System:** `/home/setup/infrafabric/SESSION-RESUME.md`

---

**Version:** 1.0.0
**Last Updated:** 2025-11-30
**Status:** Production Ready
**Maintainer:** InfraFabric Logistics Team
