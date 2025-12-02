# Redis Bus Schema - API Reference

Complete API documentation for the Redis Bus schema implementation.

Citation: if://citation/redis-bus-api-reference
Reference: IF-SWARM-S2-COMMS.md, redis_bus_schema.py

---

## Enumerations

### SpeechAct
FIPA-style speech acts for message semantics.

```python
class SpeechAct(str, Enum):
    INFORM = "inform"      # Standard finding/claim (lines 33)
    REQUEST = "request"    # Ask peer to verify/add source (line 34)
    ESCALATE = "escalate"  # Critical uncertainty to human (line 35)
    HOLD = "hold"          # Redundant or low-signal (line 36)
```

### TaskStatus
Task lifecycle states.

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    NEEDS_ASSIST = "needs_assist"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
```

---

## Packet Envelope

Implements IF.TTT audit trail with tracking ID and chain of custody.

### Packet (Dataclass)

**Fields:**
- `tracking_id: str` - Unique message identifier (UUID, auto-generated)
- `origin: str` - Agent/worker that created this message
- `dispatched_at: str` - ISO 8601 timestamp
- `speech_act: SpeechAct` - FIPA act category (default: INFORM)
- `contents: Dict[str, Any]` - Serialized payload
- `chain_of_custody: List[Tuple[str, str, str]]` - (agent_id, action, timestamp) tuples
- `signature: Optional[str]` - Ed25519 signature (optional, for future enforcement)

**Methods:**

#### `to_dict() -> Dict[str, Any]`
Serialize packet to dictionary.

```python
packet = Packet(origin="haiku-1", contents={"claim": "test"})
dict_repr = packet.to_dict()
# Returns all fields as dict
```

#### `to_json() -> str`
Serialize packet to JSON string.

```python
json_str = packet.to_json()
# Store in Redis: client.set(key, json_str)
```

#### `from_json(data: str) -> Packet`
Deserialize packet from JSON. *Static method.*

```python
restored = Packet.from_json(json_str)
```

#### `add_custody(agent_id: str, action: str) -> None`
Append entry to chain of custody for audit trail.

```python
packet.add_custody("haiku-2", "forward")
# chain_of_custody now includes ("haiku-2", "forward", <timestamp>)
```

---

## Task

Work unit claimed by agents.

### Task (Dataclass)

**Redis Pattern:** `task:{id}` (hash)

**Fields:**
- `id: str` - Unique task identifier (short UUID, auto-generated)
- `description: str` - Human-readable description
- `data: Dict[str, Any]` - Task-specific JSON data
- `type: str` - Task type (e.g., "research", "verify", "synthesize")
- `status: TaskStatus` - Current lifecycle state
- `assignee: str` - Agent ID currently working (empty if unassigned)
- `created_at: str` - ISO 8601 creation timestamp
- `updated_at: str` - ISO 8601 last update timestamp
- `ttl_seconds: int` - Time-to-live (default: 86400 = 24 hours)

**Methods:**

#### `to_hash() -> Dict[str, str]`
Convert to Redis hash format.

```python
task = Task(description="Research X")
hash_map = task.to_hash()
# Suitable for HSET: client.redis_conn.hset("task:123", mapping=hash_map)
```

#### `from_hash(hash_data: Dict[bytes, bytes]) -> Task`
Reconstruct from Redis HGETALL response. *Static method.*

```python
hash_data = client.redis_conn.hgetall("task:123")
task = Task.from_hash(hash_data)
```

---

## Finding

Research finding with confidence, citations, and custody tracking.

### Finding (Dataclass)

**Redis Pattern:** `finding:{id}` (hash)

**Fields:**
- `id: str` - Unique finding identifier (short UUID, auto-generated)
- `claim: str` - The assertion/finding text
- `confidence: float` - [0.0, 1.0] confidence score (validated)
- `citations: List[str]` - Evidence sources (if:// URIs preferred per IF.TTT)
- `timestamp: str` - ISO 8601 when finding was recorded
- `worker_id: str` - Agent that discovered this finding
- `task_id: str` - Parent task ID (can be empty if free-standing)
- `speech_act: SpeechAct` - FIPA act (default: INFORM)
- `ttl_seconds: int` - Time-to-live (default: 86400)

**Validation:**
- `confidence` must be in [0.0, 1.0]; ValueError raised otherwise

**Methods:**

#### `to_hash() -> Dict[str, str]`
Convert to Redis hash format.

```python
finding = Finding(claim="X is true", confidence=0.95)
hash_map = finding.to_hash()
```

#### `from_hash(hash_data: Dict[bytes, bytes]) -> Finding`
Reconstruct from Redis HGETALL response. *Static method.*

```python
hash_data = client.redis_conn.hgetall("finding:abc123")
finding = Finding.from_hash(hash_data)
```

---

## Context

Shared context, metadata, and working notes.

### Context (Dataclass)

**Redis Pattern:** `context:{scope}:{name}` (hash)

**Fields:**
- `scope: str` - Scope level (e.g., "task", "session", "swarm")
- `name: str` - Context name identifier
- `notes: str` - Shared notes and observations
- `timeline: List[Tuple[str, str]]` - Event timeline (timestamp, event)
- `topics: List[str]` - Topical tags
- `shared_data: Dict[str, Any]` - Arbitrary metadata (JSON)
- `updated_at: str` - ISO 8601 last update

**Methods:**

#### `key() -> str`
Generate Redis key.

```python
ctx = Context(scope="task", name="task-123")
key = ctx.key()
# Returns: "context:task:task-123"
```

#### `to_hash() -> Dict[str, str]`
Convert to Redis hash format.

```python
hash_map = ctx.to_hash()
```

#### `from_hash(hash_data: Dict[bytes, bytes]) -> Context`
Reconstruct from Redis HGETALL response. *Static method.*

```python
hash_data = client.redis_conn.hgetall("context:task:task-123")
ctx = Context.from_hash(hash_data)
```

---

## SessionSummary

Run summary for a swarm session.

### SessionSummary (Dataclass)

**Redis Pattern:** `session:infrafabric:{date}:{label}` (string)

**Fields:**
- `date: str` - YYYY-MM-DD format
- `label: str` - Session label (e.g., "protocol_scan", "haiku_swarm")
- `summary: str` - Human-readable summary
- `metrics: Dict[str, Any]` - Aggregated metrics
- `created_at: str` - ISO 8601 creation timestamp

**Methods:**

#### `key() -> str`
Generate Redis key.

```python
session = SessionSummary(date="2025-11-30", label="haiku_swarm")
key = session.key()
# Returns: "session:infrafabric:2025-11-30:haiku_swarm"
```

#### `to_json() -> str`
Serialize to JSON string.

```python
json_str = session.to_json()
# Store in Redis: client.set(key, json_str, ex=2592000)  # 30 days
```

#### `from_json(data: str) -> SessionSummary`
Deserialize from JSON string. *Static method.*

```python
restored = SessionSummary.from_json(json_str)
```

---

## SwarmRegistry

Swarm roster with active agents, roles, and artifacts.

### SwarmRegistry (Dataclass)

**Redis Pattern:** `swarm:registry:{id}` (string)

**Fields:**
- `id: str` - Swarm identifier (e.g., "infrafabric_2025-11-30")
- `agents: List[Dict[str, str]]` - Agent list with roles/status
- `roles: Dict[str, str]` - Role assignments (coordinator, leader, etc.)
- `artifacts: List[str]` - Output file paths
- `created_at: str` - ISO 8601 creation timestamp
- `updated_at: str` - ISO 8601 last update

**Methods:**

#### `key() -> str`
Generate Redis key.

```python
registry = SwarmRegistry(id="infrafabric_2025-11-30")
key = registry.key()
# Returns: "swarm:registry:infrafabric_2025-11-30"
```

#### `to_json() -> str`
Serialize to JSON string.

```python
json_str = registry.to_json()
# Store with 7-day TTL: client.set(key, json_str, ex=604800)
```

#### `from_json(data: str) -> SwarmRegistry`
Deserialize from JSON string. *Static method.*

```python
restored = SwarmRegistry.from_json(json_str)
```

---

## RemediationScan

Hygiene scan results for Redis Bus cleanup.

### RemediationScan (Dataclass)

**Redis Pattern:** `swarm:remediation:{date}:{scan_type}` (string)

**Fields:**
- `date: str` - YYYY-MM-DD or YYYY-MM-DD-HHmmss format
- `scan_type: str` - Scan type (e.g., "redis_cleanup", "schema_validation")
- `keys_scanned: int` - Number of keys examined
- `wrongtype_found: int` - WRONGTYPE keys detected
- `expired_found: int` - Expired entries detected
- `violations: List[str]` - Schema violation descriptions
- `actions_taken: List[str]` - Cleanup actions performed
- `created_at: str` - ISO 8601 timestamp

**Methods:**

#### `key() -> str`
Generate Redis key.

```python
scan = RemediationScan(date="2025-11-30", scan_type="redis_cleanup")
key = scan.key()
# Returns: "swarm:remediation:2025-11-30:redis_cleanup"
```

#### `to_json() -> str`
Serialize to JSON string.

```python
json_str = scan.to_json()
```

#### `from_json(data: str) -> RemediationScan`
Deserialize from JSON string. *Static method.*

```python
restored = RemediationScan.from_json(json_str)
```

---

## RedisBusClient

Main client for Redis Bus operations.

### Constructor

```python
client = RedisBusClient(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None
)
```

**Parameters:**
- `host`: Redis server hostname
- `port`: Redis port
- `db`: Redis database number
- `password`: Authentication password (if required)

### Methods

#### `health_check() -> bool`
Verify Redis connection is healthy.

```python
if client.health_check():
    print("Redis Bus is up")
```

#### `claim_task(task: Task, assignee: str, agent_id: str = "") -> bool`
Claim a task by setting assignee and status=in_progress. *Lines 45-54.*

**Parameters:**
- `task`: Task object to claim
- `assignee`: Agent ID claiming the task
- `agent_id`: Agent performing the claim (for custody chain)

**Returns:** True if claim succeeded, False if already assigned

**Wrapping:** Wrap in Packet envelope with custody tracking

```python
task = Task(description="Research X")
success = client.claim_task(task, assignee="haiku-1", agent_id="haiku-1")
```

#### `release_task(task_id: str, agent_id: str = "") -> bool`
Release a task back to pending. Used when blocked or handing off.

**Parameters:**
- `task_id`: Task ID to release
- `agent_id`: Agent releasing the task

**Returns:** True if release succeeded

```python
client.release_task(task_id="abc123", agent_id="haiku-1")
```

#### `get_unassigned_task() -> Optional[Task]`
Get oldest unassigned task (for idle agents looking for work).

**Returns:** Task object or None

```python
unassigned = client.get_unassigned_task()
if unassigned:
    client.claim_task(unassigned, assignee="haiku-2")
```

#### `post_finding(finding: Finding, agent_id: str = "") -> bool`
Post a finding with IF.TTT audit trail.

**Parameters:**
- `finding`: Finding object to post
- `agent_id`: Agent posting the finding

**Returns:** True if post succeeded

```python
finding = Finding(
    claim="X is true",
    confidence=0.95,
    citations=["if://citation/uuid1"],
    worker_id="haiku-1"
)
client.post_finding(finding, agent_id="haiku-1")
```

#### `get_finding(finding_id: str) -> Optional[Finding]`
Retrieve a finding by ID.

**Parameters:**
- `finding_id`: Finding ID

**Returns:** Finding object or None

```python
finding = client.get_finding("abc123")
```

#### `get_findings_for_task(task_id: str) -> List[Finding]`
Get all findings associated with a task.

**Parameters:**
- `task_id`: Task ID

**Returns:** List of Finding objects

```python
findings = client.get_findings_for_task("task-123")
for f in findings:
    print(f"{f.claim} (confidence={f.confidence})")
```

#### `detect_finding_conflicts(task_id: str, conflict_threshold: float = 0.2) -> List[Tuple[Finding, Finding]]`
Detect conflicting findings on the same task. *Lines 102, 103.*

When two findings differ in confidence > threshold, they are considered in conflict.

**Parameters:**
- `task_id`: Task ID to check
- `conflict_threshold`: Confidence delta threshold (default 0.2 = 20%)

**Returns:** List of (finding1, finding2) conflict tuples

```python
conflicts = client.detect_finding_conflicts("task-123", threshold=0.2)
for f1, f2 in conflicts:
    print(f"Conflict: {f1.confidence} vs {f2.confidence}")
```

#### `share_context(context: Context, agent_id: str = "") -> bool`
Share context notes and metadata on the bus.

**Parameters:**
- `context`: Context object to share
- `agent_id`: Agent sharing the context

**Returns:** True if share succeeded

```python
ctx = Context(scope="task", name="task-123")
ctx.notes = "Important observation"
client.share_context(ctx, agent_id="haiku-1")
```

#### `get_context(scope: str, name: str) -> Optional[Context]`
Retrieve context by scope and name.

**Parameters:**
- `scope`: Context scope (e.g., "task", "session")
- `name`: Context name

**Returns:** Context object or None

```python
ctx = client.get_context("task", "task-123")
```

#### `record_session_summary(summary: SessionSummary, agent_id: str = "") -> bool`
Record a session summary with aggregated metrics.

**Parameters:**
- `summary`: SessionSummary object
- `agent_id`: Agent recording the summary

**Returns:** True if record succeeded

```python
session = SessionSummary(date="2025-11-30", label="haiku_swarm")
session.metrics = {"tasks": 1, "findings": 12}
client.record_session_summary(session)
```

#### `register_swarm(registry: SwarmRegistry, agent_id: str = "") -> bool`
Register swarm with roster of agents and roles.

**Parameters:**
- `registry`: SwarmRegistry object
- `agent_id`: Agent registering the swarm

**Returns:** True if registration succeeded

```python
registry = SwarmRegistry(id="infrafabric_2025-11-30")
registry.agents = [{"id": "haiku-1", "role": "worker"}]
client.register_swarm(registry)
```

#### `escalate_to_human(task_id: str, reason: str, findings: Optional[List[Finding]] = None, agent_id: str = "") -> bool`
Escalate a task with critical uncertainty to human review. *Lines 102, 35.*

Creates escalation Packet with supporting findings.

**Parameters:**
- `task_id`: Task ID requiring human attention
- `reason`: Reason for escalation
- `findings`: Supporting findings (optional)
- `agent_id`: Agent initiating escalation

**Returns:** True if escalation posted successfully

```python
client.escalate_to_human(
    task_id="task-123",
    reason="Conflicting evidence - requires human judgment",
    findings=[finding1, finding2]
)
```

---

## Key Patterns Summary

| Pattern | Redis Key | Type | TTL |
|---------|-----------|------|-----|
| Task | `task:{id}` | hash | 24 hours |
| Finding | `finding:{id}` | hash | 24 hours |
| Context | `context:{scope}:{name}` | hash | 24 hours |
| Session | `session:infrafabric:{date}:{label}` | string | 30 days |
| Swarm Roster | `swarm:registry:{id}` | string | 7 days |
| Remediation | `swarm:remediation:{date}:{scan_type}` | string | 7 days |
| Packet | `packet:{type}:{id}:{action}` | string | Same as parent |

---

## Performance Characteristics

- Redis Bus latency: ~0.071 ms per operation
- 140× faster than JSONL dump/parse
- Suitable for parallel Haiku swarms
- Key scans use cursor (O(N) but memory efficient)
- All writes include Packet envelopes (minimal overhead)

---

## References

- IF-SWARM-S2-COMMS.md (lines 45-54, 29-42)
- redis_bus_schema.py (implementation)
- REDIS_BUS_USAGE_EXAMPLES.md (practical examples)
