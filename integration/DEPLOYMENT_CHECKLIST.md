# Redis Bus Schema - Deployment Checklist

Production-readiness checklist and deployment guide for Redis Bus Schema (S2 swarms).

Citation: if://citation/redis-bus-deployment-checklist
Reference: IF-SWARM-S2-COMMS.md

**Last Updated:** 2025-11-30
**Status:** Ready for Production
**Test Results:** All 7 unit tests passing

---

## Implementation Status

### ✓ Completed Components

#### 1. Core Data Structures
- [x] **Packet Envelope** (lines 76-132)
  - tracking_id (UUID)
  - origin, dispatched_at, chain_of_custody
  - speech_act (FIPA) with proper enum
  - Serialization: to_dict(), to_json()
  - Deserialization: from_json()
  - Custody tracking: add_custody() method

- [x] **Task** (lines 135-180)
  - Redis hash: `task:{id}`
  - Fields: description, data, type, status, assignee
  - created_at, updated_at, ttl_seconds
  - Methods: to_hash(), from_hash()
  - Status enum: PENDING, IN_PROGRESS, NEEDS_ASSIST, COMPLETED, FAILED, BLOCKED
  - TTL: 24 hours (configurable)

- [x] **Finding** (lines 183-233)
  - Redis hash: `finding:{id}`
  - Confidence validation: [0.0, 1.0]
  - Citations: List[str] (supports if:// URIs per IF.TTT)
  - Speech acts: INFORM, REQUEST, ESCALATE, HOLD
  - worker_id, task_id, timestamp tracking
  - Methods: to_hash(), from_hash()
  - TTL: 24 hours (configurable)

- [x] **Context** (lines 236-278)
  - Redis hash: `context:{scope}:{name}`
  - Shared notes, timeline, topics
  - shared_data for arbitrary metadata
  - Methods: key(), to_hash(), from_hash()
  - TTL: 24 hours on storage

- [x] **SessionSummary** (lines 281-311)
  - Redis string: `session:infrafabric:{date}:{label}`
  - Aggregated metrics per session
  - IF.search 8-pass metadata support
  - Methods: key(), to_json(), from_json()
  - TTL: 30 days

- [x] **SwarmRegistry** (lines 314-352)
  - Redis string: `swarm:registry:{id}`
  - Agent roster with roles and status
  - Artifact tracking
  - Cross-swarm coordination support
  - Methods: key(), to_json(), from_json()
  - TTL: 7 days

- [x] **RemediationScan** (lines 355-398)
  - Redis string: `swarm:remediation:{date}:{scan_type}`
  - WRONGTYPE/expired key tracking
  - Schema violation logging
  - Cleanup action audit trail
  - Methods: key(), to_json(), from_json()
  - TTL: 7 days

#### 2. Client Operations

- [x] **Task Operations**
  - claim_task(task, assignee, agent_id) - acquire work
  - release_task(task_id, agent_id) - hand off blocked task
  - get_unassigned_task() - find idle work

- [x] **Finding Operations**
  - post_finding(finding, agent_id) - record evidence
  - get_finding(finding_id) - retrieve by ID
  - get_findings_for_task(task_id) - get task findings
  - detect_finding_conflicts(task_id, threshold) - surface contradictions

- [x] **Context Operations**
  - share_context(context, agent_id) - post notes
  - get_context(scope, name) - retrieve by scope/name

- [x] **Session & Swarm Operations**
  - record_session_summary(summary, agent_id)
  - register_swarm(registry, agent_id)
  - escalate_to_human(task_id, reason, findings, agent_id)

- [x] **Utility**
  - health_check() - Redis connectivity verify

#### 3. IF.TTT Compliance
- [x] **Traceable:** All operations wrapped in Packet envelope with tracking_id
- [x] **Transparent:** Chain of custody tracked in every Packet
- [x] **Trustworthy:** Finding confidence validation, conflict detection
- [x] **Citations:** citations field in Finding (supports if:// URIs)
- [x] **Audit Trail:** add_custody() creates immutable transaction log

#### 4. Communication Semantics (FIPA-style)
- [x] INFORM - standard claims with confidence
- [x] REQUEST - ask peer to verify/add source
- [x] ESCALATE - critical uncertainty to human (triggered at confidence < 0.2)
- [x] HOLD - redundant/low-signal content

#### 5. Unit Tests (7/7 passing)
```
✓ test_packet_envelope         - Serialization, custody tracking
✓ test_task_lifecycle          - Create, claim, release
✓ test_finding_validation      - Confidence bounds [0.0, 1.0]
✓ test_context_operations      - Key generation, metadata
✓ test_session_summary         - Session tracking, metrics
✓ test_swarm_registry          - Swarm registration, roster
✓ test_remediation_scan        - Hygiene tracking, violations
```

---

## Pre-Deployment Requirements

### Redis Infrastructure
- [ ] Redis 6.0+ installed and running
- [ ] Redis Port 6379 (or custom port configured)
- [ ] Redis persistence enabled (RDB or AOF)
- [ ] Redis memory policy: `maxmemory-policy allkeys-lru` (or similar)
- [ ] Redis authentication configured (if required)
- [ ] Redis monitoring/alerting in place

### Python Dependencies
- [ ] Python 3.9+
- [ ] redis >= 4.5.0 (`pip install redis`)
- [ ] dataclasses (stdlib in 3.7+)
- [ ] json (stdlib)
- [ ] uuid (stdlib)
- [ ] hashlib (stdlib)
- [ ] hmac (stdlib)
- [ ] datetime (stdlib)
- [ ] typing (stdlib)
- [ ] abc (stdlib)
- [ ] enum (stdlib)

### Installation
```bash
pip install redis>=4.5.0
```

### Network Requirements
- [ ] Redis is reachable from swarm agents
- [ ] Firewall allows Redis port (6379)
- [ ] No SSL/TLS interceptors blocking Redis protocol (unless using redis-py SSL)
- [ ] Low-latency connection (target: < 1ms RTT)

---

## Deployment Steps

### Step 1: Copy Implementation File
```bash
cp redis_bus_schema.py /path/to/your/swarm/integration/
```

### Step 2: Verify Redis Connection
```python
from integration.redis_bus_schema import RedisBusClient

client = RedisBusClient(host="localhost", port=6379)
assert client.health_check(), "Redis connection failed!"
print("✓ Redis Bus connection verified")
```

### Step 3: Run Unit Tests
```bash
python -m integration.redis_bus_schema
# Output: All tests passed! ✓
```

### Step 4: Configure Agent IDs
```python
# In each swarm agent's startup:
client = RedisBusClient(...)
client.agent_id = "haiku-1"  # Set agent identifier for custody tracking
```

### Step 5: Initialize Swarm Registry
```python
from integration.redis_bus_schema import SwarmRegistry

registry = SwarmRegistry(
    id="swarm_" + datetime.now().strftime("%Y-%m-%d-%H%M%S"),
    agents=[
        {"id": "haiku-1", "role": "worker", "status": "starting"},
        {"id": "haiku-2", "role": "worker", "status": "starting"},
    ],
    roles={"coordinator": "sonnet-1"}
)

client.register_swarm(registry, agent_id="sonnet-1")
print(f"✓ Swarm {registry.id} registered")
```

### Step 6: Configure TTLs
```python
# Default TTLs are production-ready:
# - Tasks: 24 hours
# - Findings: 24 hours
# - Sessions: 30 days
# - Registries: 7 days
# - Remediations: 7 days

# Override if needed:
task = Task(..., ttl_seconds=3600)  # 1 hour instead of 24
```

### Step 7: Enable Metrics Collection
```python
# At end of session:
session = SessionSummary(
    date=datetime.now().strftime("%Y-%m-%d"),
    label="haiku_swarm",
    metrics={
        "tasks_processed": N,
        "findings_posted": M,
        "conflicts_detected": C,
        "escalations": E,
    }
)
client.record_session_summary(session)
```

---

## Production Configuration

### Redis Configuration (redis.conf)
```redis
# Memory
maxmemory 8gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Network
bind 127.0.0.1 ::1
port 6379
timeout 0
tcp-keepalive 300

# Logging
loglevel notice
logfile "/var/log/redis.log"

# Security (if authentication required)
requirepass <strong-password>
```

### Python Configuration
```python
import os
from integration.redis_bus_schema import RedisBusClient

# Environment-based configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

client = RedisBusClient(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD
)

assert client.health_check(), "Redis Bus startup failed!"
```

---

## Monitoring & Operations

### Health Checks
```python
# Periodic health checks (e.g., every 30 seconds)
if not client.health_check():
    logger.error("Redis Bus connection lost")
    # Implement retry logic
```

### Metrics Collection
```bash
# Monitor Redis key count
redis-cli DBSIZE

# Monitor memory usage
redis-cli INFO memory

# Scan for WRONGTYPE keys (hygiene check)
redis-cli --scan --pattern "task:*" | while read key; do
  redis-cli TYPE "$key"
done
```

### Cleaning Up Expired Data
```python
# Run periodic remediation scans
from integration.redis_bus_schema import RemediationScan

scan = RemediationScan(
    date=datetime.now().strftime("%Y-%m-%d-%H%M%S"),
    scan_type="redis_cleanup",
    keys_scanned=0,
    wrongtype_found=0
)

# Use Redis SCAN to find and clean WRONGTYPE keys
# Record results in scan object
client.redis_conn.set(scan.key(), scan.to_json())
```

### Logging
```python
import logging

logger = logging.getLogger("redis_bus")

# Log task claims
logger.info(f"Task {task.id} claimed by {assignee}")

# Log findings
logger.info(f"Finding {finding.id} posted with confidence {finding.confidence}")

# Log escalations
logger.warning(f"Task {task_id} escalated: {reason}")
```

---

## API Usage Patterns

### Pattern 1: Task Workflow
```python
# 1. Get unassigned work
task = client.get_unassigned_task()

# 2. Claim it
client.claim_task(task, assignee="haiku-1", agent_id="haiku-1")

# 3. Do work, post findings
for claim, confidence in findings:
    finding = Finding(
        claim=claim,
        confidence=confidence,
        worker_id="haiku-1",
        task_id=task.id
    )
    client.post_finding(finding)

# 4. Release if blocked
if blocked:
    client.release_task(task.id, agent_id="haiku-1")
```

### Pattern 2: Conflict Detection
```python
conflicts = client.detect_finding_conflicts(task.id, threshold=0.2)

if conflicts:
    for f1, f2 in conflicts:
        client.escalate_to_human(
            task_id=task.id,
            reason=f"Confidence conflict: {f1.confidence} vs {f2.confidence}",
            findings=[f1, f2]
        )
```

### Pattern 3: Session Management
```python
# Start session
start = datetime.now()

# ... do swarm work ...

# End session, record metrics
duration = (datetime.now() - start).total_seconds()
session = SessionSummary(
    date=datetime.now().strftime("%Y-%m-%d"),
    label="analysis_run",
    metrics={"duration_seconds": duration, ...}
)
client.record_session_summary(session)
```

---

## Troubleshooting

### Issue: "Redis connection refused"
**Solution:**
- Check Redis is running: `redis-cli PING`
- Verify host/port configuration
- Check firewall allows port 6379
- Verify authentication credentials

### Issue: "WRONGTYPE Operation against a key holding the wrong kind of value"
**Solution:**
- Run remediation scan to identify wrongtype keys
- Delete corrupted key: `redis-cli DEL <key>`
- Restart affected agents

### Issue: "Confidence must be in [0.0, 1.0]"
**Solution:**
- Validate confidence scores before creating Finding objects
- Use try/except to catch ValueError

### Issue: "Task already claimed"
**Solution:**
- check_task_status() before claiming
- Implement backoff and retry for unassigned tasks

---

## Rollback Procedures

### Partial Rollback (keep data)
```bash
# Remove just the library
rm /path/to/redis_bus_schema.py

# Keep Redis data intact for recovery
```

### Full Rollback (reset Redis)
```bash
# WARNING: This deletes all bus data
redis-cli FLUSHDB

# Or selective deletion by pattern
redis-cli --scan --pattern "task:*" | xargs redis-cli DEL
redis-cli --scan --pattern "finding:*" | xargs redis-cli DEL
```

---

## Success Criteria (All Met ✓)

- [x] Production-ready code (not pseudocode)
- [x] All 6 key patterns implemented (Task, Finding, Context, SessionSummary, SwarmRegistry, RemediationScan)
- [x] Packet envelope structure included with custody tracking
- [x] Unit tests pass (7/7)
- [x] IF.TTT compliance verified
- [x] FIPA speech acts implemented
- [x] Helper methods complete (claim, release, post, detect_conflicts, escalate)
- [x] Docstrings with IF.citation references
- [x] Example usage in docstrings

---

## Next Steps

1. **Deploy to Redis Bus infrastructure**
   - Copy redis_bus_schema.py to integration directory
   - Run unit tests in production environment
   - Verify Redis connectivity

2. **Integrate with Swarm Agents**
   - Update haiku agent startup to initialize RedisBusClient
   - Set agent_id for custody tracking
   - Register swarm with SwarmRegistry

3. **Monitor Operations**
   - Set up Redis health checks
   - Enable metrics collection
   - Schedule periodic remediation scans

4. **Implement Access Control** (Recommendation from IF-SWARM-S2-COMMS.md)
   - Add allowlist per swarm registry
   - Gate cross-swarm reads
   - Document permission model

5. **Add Signature Enforcement** (Recommendation from IF-SWARM-S2-COMMS.md)
   - Implement Ed25519 sign/verify
   - Reject unsigned messages
   - Add to Packet envelope

---

## References

- **IF-SWARM-S2-COMMS.md** - Complete specification
- **redis_bus_schema.py** - Implementation source
- **REDIS_BUS_USAGE_EXAMPLES.md** - Practical examples
- **REDIS_BUS_API_REFERENCE.md** - Complete API documentation
- **IF-foundations.md** - IF.search 8-pass methodology

---

## Document Metadata

- **Created:** 2025-11-30
- **Implementation Status:** Production-Ready
- **Test Coverage:** 7/7 unit tests passing
- **Code Size:** ~1,100 lines (production code + tests)
- **Documentation:** 3 supporting docs (usage, API reference, deployment)
- **Citations:** All code linked to IF-SWARM-S2-COMMS.md with line references
