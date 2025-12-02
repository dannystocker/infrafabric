# Claude Max Audit System

if://code/claude-max-audit/2025-11-30

Comprehensive audit trail system for all Claude Max multi-agent communications, context access logging, security event tracking, and decision recording with full IF.TTT (Traceable, Transparent, Trustworthy) compliance.

## Overview

The Claude Max Audit System provides complete visibility into all agent-to-agent communications within swarms, context window operations, significant decisions, and security events. It implements a dual-tier storage architecture:

- **Hot Storage (Redis)**: 30-day rolling window for fast queries and real-time analytics
- **Cold Storage (ChromaDB)**: 30+ days archived with semantic search and 7-year retention

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│         ClaudeMaxAuditor (Main Audit Class)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Message Logging                                      │  │
│  │  - Agent-to-agent messages                           │  │
│  │  - Cross-swarm communications                        │  │
│  │  - Message types: inform, request, escalate, hold    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Context Access Logging                               │  │
│  │  - Read/write/update/delete operations               │  │
│  │  - Context window size tracking                      │  │
│  │  - Session correlation                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Decision Logging                                     │  │
│  │  - Significant agent decisions                       │  │
│  │  - Governance approvals/rejections                   │  │
│  │  - IF.citation cross-references                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Security Event Logging                               │  │
│  │  - Rate limit violations                             │  │
│  │  - Authentication failures                           │  │
│  │  - Unauthorized access attempts                      │  │
│  │  - Anomalous patterns                                │  │
│  │  - Severity levels: low, medium, high, critical      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Query Engine (Multiple Dimensions)                   │  │
│  │  - By agent_id, swarm_id, entry_type                 │  │
│  │  - Time range queries                                │  │
│  │  - Semantic search (ChromaDB)                        │  │
│  │  - Content hash lookup (deduplication)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │                           │
         ↓                           ↓
    ┌─────────────┐         ┌────────────────┐
    │    Redis    │         │   ChromaDB     │
    │ (Hot: 30d)  │         │  (Cold: 7yr)   │
    └─────────────┘         └────────────────┘
```

### Storage Strategy

#### Hot Storage (Redis)

Keys organized by query dimension:

```
audit:entries:{YYYY-MM-DD}     → Sorted set of entry IDs (by timestamp)
audit:agent:{agent_id}          → Set of entry IDs from this agent
audit:swarm:{swarm_id}          → Set of entry IDs in this swarm
audit:entry:{entry_id}          → Hash with full entry data
```

**Characteristics:**
- Fast queries (O(log n) or O(1) operations)
- Real-time analytics and dashboards
- 30-day automatic expiration via TTL
- Automatic index management

#### Cold Storage (ChromaDB)

**Characteristics:**
- Semantic search via embeddings
- Metadata filtering on agent_id, swarm_id, severity, type
- Compressed storage format
- Full 7-year retention
- Daily archival job transfers entries from Redis to ChromaDB

### Batch & Async Operations

All logging operations are non-blocking:

- **Async Methods**: All log_* methods are `async` and return immediately
- **Batch Queueing**: Entries queued in-memory until batch_size threshold
- **Automatic Flush**: Batch flushed to Redis+ChromaDB when queue reaches batch_size
- **Manual Flush**: `await auditor.flush_all()` for immediate write

Benefits:
- Doesn't block message delivery or context transfers
- Reduces Redis write operations by 10× (batch 10 entries per write)
- Automatic retry on failure

## API Reference

### Initialization

```python
from infrafabric.src.core.audit import ClaudeMaxAuditor, MessageType, SecuritySeverity

# Create auditor instance
auditor = ClaudeMaxAuditor(
    redis_host="localhost",
    redis_port=6379,
    storage_backend="redis+chromadb",  # or "redis", "chromadb"
    batch_size=10,
    hot_storage_days=30,
    cold_storage_years=7
)

# Or get global instance
from infrafabric.src.core.audit import get_auditor
auditor = get_auditor()
```

### Logging Messages

```python
# Log agent-to-agent message
message_id = await auditor.log_message(
    from_agent="sonnet_coordinator_abc123",
    to_agent="haiku_worker_def456",
    message_type=MessageType.REQUEST,
    content="Please analyze the provided context",
    from_swarm="swarm_primary",
    to_swarm="swarm_secondary",
    metadata={
        "priority": "high",
        "timeout_seconds": 300
    }
)
```

**Message Types:**
- `MessageType.INFORM`: Information sharing
- `MessageType.REQUEST`: Task/context request
- `MessageType.ESCALATE`: Security/governance escalation
- `MessageType.HOLD`: Pause/context freeze
- `MessageType.RESPONSE`: Response to request
- `MessageType.ERROR`: Error notification

### Logging Context Access

```python
# Log context read/write
access_id = await auditor.log_context_access(
    agent_id="haiku_worker_def456",
    session_id="session_20251130_001",
    operation=OperationType.READ,
    size_bytes=150000,
    swarm_id="swarm_secondary",
    metadata={
        "context_version": "v1.2",
        "chunk_count": 3
    }
)
```

**Operations:**
- `OperationType.READ`: Context read (doesn't modify)
- `OperationType.WRITE`: New context creation
- `OperationType.UPDATE`: Context modification
- `OperationType.DELETE`: Context removal

### Logging Decisions

```python
# Log significant decision
decision_id = await auditor.log_decision(
    agent_id="sonnet_coordinator_abc123",
    decision_type="governance_approval",
    rationale="All constraints satisfied, entropy < 0.5",
    citation="if://guardian/decision/abc123",
    swarm_id="swarm_primary",
    metadata={
        "confidence_score": 0.95,
        "alternatives_considered": 3
    }
)
```

### Logging Security Events

```python
# Log security violation
security_id = await auditor.log_security_event(
    agent_id="haiku_worker_def456",
    event_type="rate_limit_approaching",
    severity=SecuritySeverity.MEDIUM,
    details={
        "requests_per_minute": 45,
        "limit": 50,
        "breach_in_seconds": 60
    },
    swarm_id="swarm_secondary"
)
```

**Security Event Types:**
- `"rate_limit_violation"` - Exceeded request rate
- `"auth_failure"` - Authentication failure
- `"unauthorized_access"` - Access control violation
- `"anomalous_pattern"` - Unusual message patterns detected
- `"confidence_manipulation"` - Confidence score anomaly
- `"context_poisoning"` - Suspicious context modification
- `"cross_swarm_anomaly"` - Unusual cross-swarm activity

**Severity Levels:**
- `SecuritySeverity.LOW` - Minor issue, informational
- `SecuritySeverity.MEDIUM` - Concerning, needs investigation
- `SecuritySeverity.HIGH` - Serious, immediate attention
- `SecuritySeverity.CRITICAL` - System-critical, emergency response

### Searching Logs

```python
# Search by agent
results = await auditor.search_logs(
    query={"agent_id": "sonnet_coordinator_abc123"},
    time_range=(start_datetime, end_datetime),
    limit=100
)

# Search by swarm
results = await auditor.search_logs(
    query={"swarm_id": "swarm_primary"}
)

# Search by entry type
results = await auditor.search_logs(
    query={"entry_type": "security_event"}
)

# Search by security severity
results = await auditor.search_logs(
    query={"severity": "critical"}
)

# Semantic search (ChromaDB)
results = await auditor.search_logs(
    query={"text_query": "Find all authorization failures"}
)
```

**Query Result Structure:**

```python
results: AuditQueryResult
├── entries: List[AuditEntry]              # Matching entries
├── total_count: int                       # Total matches
├── query_time_ms: float                  # Query latency
└── source: str                            # "redis" or "chromadb"
```

### Exporting Audit Trails

```python
# Export full swarm audit trail
export_path = await auditor.export_audit_trail(
    swarm_id="swarm_primary",
    format="jsonl",  # or "json", "csv"
    start_date=datetime(2025, 11, 1),
    end_date=datetime(2025, 11, 30),
    output_path="/tmp/audit_export.jsonl"
)
```

### Getting Performance Metrics

```python
metrics = await auditor.get_metrics()
print(f"Active agents: {metrics.active_agents}")
print(f"Hot storage entries: {metrics.total_entries_hot}")
print(f"Cross-swarm messages: {metrics.cross_swarm_messages}")
```

## IF.Citation Integration

Every audit entry generates a unique IF.citation URI:

```python
# Automatic citation generation
message_id = await auditor.log_message(...)
# Returns citation: if://audit/message/[uuid]

# Access citation from entry
entry: AuditEntry = ...
citation = entry.citation  # if://audit/message/abc-def-ghi

# Generate citation for existing entry
citation = await auditor.generate_citation(entry_id="abc123")
```

**Citation Format:** `if://audit/{entry_type}/{entry_id}`

**Examples:**
- `if://audit/message/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv`
- `if://audit/decision/x9y8z7w6-5432-10ef-jihg-tsrqponmlkji`
- `if://audit/security_event/m5n4o3p2-1098-76ef-dcba-ihgfedcbakji`

## Retention & Archival

### Default Policy

- **Hot (Redis)**: 30 days, automatic expiration
- **Cold (ChromaDB)**: 7 years minimum, semantic indexing
- **Permanent Flag**: Fields marked with `retention="permanent"` skip auto-purge

### Manual Archival

```python
# Archive entries older than 30 days
archived_count = await auditor.archive_old_entries(days_old=30)

# Cleanup entries older than 7 years
purged_count = await auditor.cleanup_expired_entries(older_than_days=2555)
```

### Daily Archival Job (Recommended)

```python
# Run in background task
import asyncio

async def daily_archival():
    auditor = get_auditor()
    while True:
        # Every 24 hours
        await asyncio.sleep(86400)
        archived = await auditor.archive_old_entries(days_old=30)
        logger.info(f"Daily archival: {archived} entries")

# Start in background
asyncio.create_task(daily_archival())
```

## Cross-Swarm Message Tracking

Messages between different swarms are automatically tagged:

```python
# Log cross-swarm message
await auditor.log_message(
    from_agent="agent_in_swarm_a",
    to_agent="agent_in_swarm_b",
    from_swarm="swarm_a",
    to_swarm="swarm_b",
    content="..."
)

# Entry automatically has:
# - entry.swarm_ids = ["swarm_a", "swarm_b"]
# - metadata["cross_swarm"] = True

# Query cross-swarm activity
results = await auditor.search_logs(
    query={"text_query": "cross_swarm"}
)
```

## Performance Optimization

### Configuration Best Practices

```python
auditor = ClaudeMaxAuditor(
    batch_size=10,              # Larger = fewer Redis writes, more latency
    hot_storage_days=30,        # Balance between retention and storage
    storage_backend="redis+chromadb"  # Use both for best performance
)
```

### Query Optimization

1. **Use time_range for large datasets:**
   ```python
   # Fast (specific date range)
   results = await auditor.search_logs(
       query={...},
       time_range=(start, end),
       limit=100
   )

   # Slow (all entries)
   results = await auditor.search_logs(query={...})
   ```

2. **Index cache for common queries:**
   ```python
   # First query loads agent index
   results1 = await auditor.search_logs({"agent_id": "agent_abc"})
   # Second query uses cached index
   results2 = await auditor.search_logs({"agent_id": "agent_abc"})
   ```

3. **Semantic search on cold storage only:**
   - Text queries automatically use ChromaDB
   - Fast indexing via embeddings
   - No full-text scan required

## Integration Examples

### With Redis Swarm Coordinator

```python
from infrafabric.src.core.logistics.redis_swarm_coordinator import RedisSwarmCoordinator
from infrafabric.src.core.audit import get_auditor

coordinator = RedisSwarmCoordinator()
auditor = get_auditor()

# Log every message sent through coordinator
async def log_coordinator_message(from_agent, to_agent, message):
    await auditor.log_message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.INFORM,
        content=json.dumps(message),
        metadata={"coordinator": True}
    )
```

### With Guardian Council

```python
from infrafabric.src.core.governance.guardian import GuardianCouncil
from infrafabric.src.core.audit import get_auditor

council = GuardianCouncil()
auditor = get_auditor()

# Log governance decisions
async def log_governance_decision(action, decision):
    if not decision.approved:
        await auditor.log_security_event(
            agent_id="guardian_council",
            event_type="governance_rejection",
            severity=SecuritySeverity.HIGH,
            details={
                "action": action,
                "reason": decision.reason,
                "actor": action.actor
            }
        )
```

### With Context Management

```python
async def manage_context_with_audit(agent_id, session_id, operation, context):
    auditor = get_auditor()

    # Perform operation
    result = await perform_operation(agent_id, operation, context)

    # Log access
    await auditor.log_context_access(
        agent_id=agent_id,
        session_id=session_id,
        operation=operation,
        size_bytes=len(context.encode()),
        metadata={"result": result}
    )

    return result
```

## Dashboard Integration

The audit system provides hooks for real-time dashboards:

```python
# Real-time metrics endpoint
async def get_dashboard_metrics():
    auditor = get_auditor()
    return {
        "metrics": await auditor.get_metrics(),
        "recent_entries": await auditor.search_logs(
            query={},
            limit=50
        )
    }

# Security alerts
async def get_critical_alerts():
    auditor = get_auditor()
    return await auditor.search_logs(
        query={"severity": "critical"},
        time_range=(datetime.utcnow() - timedelta(hours=1), datetime.utcnow())
    )
```

## Troubleshooting

### Redis Connection Issues

```python
# Check Redis connectivity
try:
    auditor = ClaudeMaxAuditor(redis_host="localhost", redis_port=6379)
    print("Redis connected")
except redis.ConnectionError as e:
    print(f"Redis unavailable: {e}")
    # Falls back to ChromaDB-only mode
```

### ChromaDB Initialization

```python
# Specify custom path
auditor = ClaudeMaxAuditor(
    chromadb_path="/custom/audit/path"
)

# Or disable ChromaDB
auditor = ClaudeMaxAuditor(
    storage_backend="redis"  # Redis-only
)
```

### Batch Queue Overflow

```python
# Manual flush if queue builds up
if len(auditor.batch_queue) > 100:
    await auditor.flush_all()
```

## Contributing

All audit code follows IF.TTT compliance:
- **Traceable**: Every entry has unique UUID + citation
- **Transparent**: Query any dimension, export full trails
- **Trustworthy**: Immutable log format, retention policies

## License & Citation

**if://code/claude-max-audit/2025-11-30**

Part of InfraFabric integration framework.
See `/home/setup/infrafabric/agents.md` for full context.
