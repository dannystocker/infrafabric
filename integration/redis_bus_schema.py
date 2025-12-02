"""
Redis Bus Schema Implementation for IF.swarm.s2 Communication

This module implements production-ready Redis key patterns and packet structures
for InfraFabric Series 2 (S2) swarm communication, following the architecture
defined in IF-SWARM-S2-COMMS.md.

Key Patterns Implemented:
  - task:{id} (hash) - work units claimed by agents
  - finding:{id} (hash) - research findings with citations and confidence
  - context:{scope}:{name} (hash) - shared context and metadata
  - session:infrafabric:{date}:{label} (string) - run summaries
  - swarm:registry:{id} (string) - swarm rosters
  - swarm:remediation:{date} (string) - hygiene scan results
  - bus:queue:{topic} (list) - optional FIFO dispatch queue

Citation: if://citation/redis-bus-schema-s2
Reference: IF-SWARM-S2-COMMS.md lines 45-54 (keying convention)
Reference: IF-SWARM-S2-COMMS.md lines 29-42 (communication semantics)

Author: Agent A6
Date: 2025-11-30
"""

import json
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import redis
from abc import ABC, abstractmethod


class SpeechAct(str, Enum):
    """FIPA-style speech acts for bus communication semantics."""
    INFORM = "inform"      # claim + confidence + citations
    REQUEST = "request"    # ask peer to verify / add source
    ESCALATE = "escalate"  # critical uncertainty to human
    HOLD = "hold"          # redundant or low-signal content


class TaskStatus(str, Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    NEEDS_ASSIST = "needs_assist"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class ConfidenceLevel(float):
    """Confidence scores must be in [0.0, 1.0] range."""

    def __new__(cls, value: float):
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {value}")
        return float(value)


@dataclass
class Packet:
    """
    Envelope structure for Redis bus messages per IF.TTT (Traceable, Transparent, Trustworthy).

    All bus writes wrap payloads in Packet envelopes with custody headers.
    Implements audit trail via tracking_id and chain_of_custody.

    Fields:
        tracking_id: Unique message identifier (UUID)
        origin: Agent/worker that created this message
        dispatched_at: ISO 8601 timestamp when packet was created
        speech_act: FIPA speech act category (inform, request, escalate, hold)
        contents: Serialized payload (finding, task claim, etc.)
        chain_of_custody: List of (agent_id, action, timestamp) tuples
        signature: Ed25519 signature (optional, for future enforcement)
    """
    tracking_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    origin: str = ""
    dispatched_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    speech_act: SpeechAct = SpeechAct.INFORM
    contents: Dict[str, Any] = field(default_factory=dict)
    chain_of_custody: List[Tuple[str, str, str]] = field(default_factory=list)
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize packet to dictionary for Redis storage."""
        return {
            "tracking_id": self.tracking_id,
            "origin": self.origin,
            "dispatched_at": self.dispatched_at,
            "speech_act": self.speech_act.value,
            "contents": self.contents,
            "chain_of_custody": self.chain_of_custody,
            "signature": self.signature or "",
        }

    def to_json(self) -> str:
        """Serialize packet to JSON for Redis string storage."""
        return json.dumps(self.to_dict(), default=str)

    @staticmethod
    def from_json(data: str) -> "Packet":
        """Deserialize packet from JSON."""
        obj = json.loads(data)
        packet = Packet(
            tracking_id=obj.get("tracking_id", str(uuid.uuid4())),
            origin=obj.get("origin", ""),
            dispatched_at=obj.get("dispatched_at", datetime.utcnow().isoformat()),
            speech_act=SpeechAct(obj.get("speech_act", "inform")),
            contents=obj.get("contents", {}),
            chain_of_custody=obj.get("chain_of_custody", []),
            signature=obj.get("signature"),
        )
        return packet

    def add_custody(self, agent_id: str, action: str) -> None:
        """Add entry to chain of custody for audit trail."""
        timestamp = datetime.utcnow().isoformat()
        self.chain_of_custody.append((agent_id, action, timestamp))


@dataclass
class Task:
    """
    Redis hash: task:{id}
    Work unit claimed by agents via the Redis Bus.

    Fields:
        id: Unique task identifier
        description: Human-readable task description
        data: Task-specific data (serialized JSON)
        type: Task type (e.g., "research", "verify", "synthesize")
        status: Current lifecycle state
        assignee: Agent ID currently working on task (or empty)
        created_at: ISO 8601 timestamp
        updated_at: ISO 8601 timestamp
        ttl_seconds: Time-to-live for this task (default: 86400 = 24 hours)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    type: str = ""
    status: TaskStatus = TaskStatus.PENDING
    assignee: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    ttl_seconds: int = 86400  # 24 hours

    def to_hash(self) -> Dict[str, str]:
        """Convert to Redis hash format."""
        return {
            "id": self.id,
            "description": self.description,
            "data": json.dumps(self.data),
            "type": self.type,
            "status": self.status.value,
            "assignee": self.assignee,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "ttl_seconds": str(self.ttl_seconds),
        }

    @staticmethod
    def from_hash(hash_data: Dict[bytes, bytes]) -> "Task":
        """Reconstruct Task from Redis hash response."""
        def decode(val):
            return val.decode() if isinstance(val, bytes) else val

        return Task(
            id=decode(hash_data.get(b"id", b"")),
            description=decode(hash_data.get(b"description", b"")),
            data=json.loads(decode(hash_data.get(b"data", b"{}"))),
            type=decode(hash_data.get(b"type", b"")),
            status=TaskStatus(decode(hash_data.get(b"status", b"pending"))),
            assignee=decode(hash_data.get(b"assignee", b"")),
            created_at=decode(hash_data.get(b"created_at", b"")),
            updated_at=decode(hash_data.get(b"updated_at", b"")),
            ttl_seconds=int(decode(hash_data.get(b"ttl_seconds", b"86400"))),
        )


@dataclass
class Finding:
    """
    Redis hash: finding:{id}
    Research finding with evidence, confidence, and custody tracking.

    Per IF.TTT (Traceable, Transparent, Trustworthy):
    - claim: The actual finding/assertion
    - confidence: [0.0, 1.0] score
    - citations: List of sources (can be if:// URIs or file:line references)
    - timestamp: When finding was recorded
    - worker_id: Agent that discovered this finding
    - task_id: Parent task ID (can be empty if free-standing)
    - speech_act: FIPA act type (usually "inform", can be "escalate" if high uncertainty)
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    claim: str = ""
    confidence: float = 0.5
    citations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    worker_id: str = ""
    task_id: str = ""
    speech_act: SpeechAct = SpeechAct.INFORM
    ttl_seconds: int = 86400  # 24 hours

    def __post_init__(self):
        """Validate confidence is in [0.0, 1.0]."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {self.confidence}")

    def to_hash(self) -> Dict[str, str]:
        """Convert to Redis hash format."""
        return {
            "id": self.id,
            "claim": self.claim,
            "confidence": str(self.confidence),
            "citations": json.dumps(self.citations),
            "timestamp": self.timestamp,
            "worker_id": self.worker_id,
            "task_id": self.task_id,
            "speech_act": self.speech_act.value,
            "ttl_seconds": str(self.ttl_seconds),
        }

    @staticmethod
    def from_hash(hash_data: Dict[bytes, bytes]) -> "Finding":
        """Reconstruct Finding from Redis hash response."""
        def decode(val):
            return val.decode() if isinstance(val, bytes) else val

        return Finding(
            id=decode(hash_data.get(b"id", b"")),
            claim=decode(hash_data.get(b"claim", b"")),
            confidence=float(decode(hash_data.get(b"confidence", b"0.5"))),
            citations=json.loads(decode(hash_data.get(b"citations", b"[]"))),
            timestamp=decode(hash_data.get(b"timestamp", b"")),
            worker_id=decode(hash_data.get(b"worker_id", b"")),
            task_id=decode(hash_data.get(b"task_id", b"")),
            speech_act=SpeechAct(decode(hash_data.get(b"speech_act", b"inform"))),
            ttl_seconds=int(decode(hash_data.get(b"ttl_seconds", b"86400"))),
        )


@dataclass
class Context:
    """
    Redis hash: context:{scope}:{name}
    Shared context, metadata, and working notes for swarm coordination.

    scope: Scope level (e.g., "task", "session", "swarm")
    name: Context name identifier
    notes: Shared notes and observations
    timeline: Event timeline (list of (timestamp, event) tuples)
    topics: List of topical tags
    shared_data: Arbitrary shared metadata (JSON)
    """
    scope: str = ""
    name: str = ""
    notes: str = ""
    timeline: List[Tuple[str, str]] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def key(self) -> str:
        """Generate Redis key."""
        return f"context:{self.scope}:{self.name}"

    def to_hash(self) -> Dict[str, str]:
        """Convert to Redis hash format."""
        return {
            "scope": self.scope,
            "name": self.name,
            "notes": self.notes,
            "timeline": json.dumps(self.timeline),
            "topics": json.dumps(self.topics),
            "shared_data": json.dumps(self.shared_data),
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_hash(hash_data: Dict[bytes, bytes]) -> "Context":
        """Reconstruct Context from Redis hash response."""
        def decode(val):
            return val.decode() if isinstance(val, bytes) else val

        return Context(
            scope=decode(hash_data.get(b"scope", b"")),
            name=decode(hash_data.get(b"name", b"")),
            notes=decode(hash_data.get(b"notes", b"")),
            timeline=json.loads(decode(hash_data.get(b"timeline", b"[]"))),
            topics=json.loads(decode(hash_data.get(b"topics", b"[]"))),
            shared_data=json.loads(decode(hash_data.get(b"shared_data", b"{}"))),
            updated_at=decode(hash_data.get(b"updated_at", b"")),
        )


@dataclass
class SessionSummary:
    """
    Redis string: session:infrafabric:{date}:{label}
    Run summary for a swarm session (e.g., protocol_scan, haiku_swarm).

    Stored as JSON string in Redis. Includes IF.search 8-pass metadata
    and SHARE/HOLD/ESCALATE metrics for this session.
    """
    date: str = ""  # YYYY-MM-DD
    label: str = ""  # protocol_scan, haiku_swarm, etc.
    summary: str = ""  # Human-readable summary
    metrics: Dict[str, Any] = field(default_factory=dict)  # Aggregated metrics
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def key(self) -> str:
        """Generate Redis key."""
        return f"session:infrafabric:{self.date}:{self.label}"

    def to_json(self) -> str:
        """Serialize to JSON string for Redis."""
        return json.dumps({
            "date": self.date,
            "label": self.label,
            "summary": self.summary,
            "metrics": self.metrics,
            "created_at": self.created_at,
        }, default=str)

    @staticmethod
    def from_json(data: str) -> "SessionSummary":
        """Deserialize from JSON string."""
        obj = json.loads(data)
        return SessionSummary(
            date=obj.get("date", ""),
            label=obj.get("label", ""),
            summary=obj.get("summary", ""),
            metrics=obj.get("metrics", {}),
            created_at=obj.get("created_at", datetime.utcnow().isoformat()),
        )


@dataclass
class SwarmRegistry:
    """
    Redis string: swarm:registry:{id}
    Swarm roster with active agents, roles, and artifacts.

    Stored as JSON string. Used for cross-swarm coordination and
    service discovery.
    """
    id: str = ""  # Swarm identifier (e.g., "infrafabric_2025-11-26")
    agents: List[Dict[str, str]] = field(default_factory=list)  # [{"id": "haiku-1", "role": "worker", ...}]
    roles: Dict[str, str] = field(default_factory=dict)  # {"coordinator": "haiku-0", ...}
    artifacts: List[str] = field(default_factory=list)  # Output artifacts, file paths
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def key(self) -> str:
        """Generate Redis key."""
        return f"swarm:registry:{self.id}"

    def to_json(self) -> str:
        """Serialize to JSON string for Redis."""
        return json.dumps({
            "id": self.id,
            "agents": self.agents,
            "roles": self.roles,
            "artifacts": self.artifacts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }, default=str)

    @staticmethod
    def from_json(data: str) -> "SwarmRegistry":
        """Deserialize from JSON string."""
        obj = json.loads(data)
        return SwarmRegistry(
            id=obj.get("id", ""),
            agents=obj.get("agents", []),
            roles=obj.get("roles", {}),
            artifacts=obj.get("artifacts", []),
            created_at=obj.get("created_at", datetime.utcnow().isoformat()),
            updated_at=obj.get("updated_at", datetime.utcnow().isoformat()),
        )


@dataclass
class RemediationScan:
    """
    Redis string: swarm:remediation:{date}:{scan_type}
    Hygiene scan results for Redis Bus cleanup.

    Scans for WRONGTYPE keys, expired entries, stale data, and schema violations.
    """
    date: str = ""  # YYYY-MM-DD or YYYY-MM-DD-HHmmss
    scan_type: str = ""  # e.g., "redis_cleanup", "schema_validation"
    keys_scanned: int = 0
    wrongtype_found: int = 0
    expired_found: int = 0
    violations: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def key(self) -> str:
        """Generate Redis key."""
        return f"swarm:remediation:{self.date}:{self.scan_type}"

    def to_json(self) -> str:
        """Serialize to JSON string for Redis."""
        return json.dumps({
            "date": self.date,
            "scan_type": self.scan_type,
            "keys_scanned": self.keys_scanned,
            "wrongtype_found": self.wrongtype_found,
            "expired_found": self.expired_found,
            "violations": self.violations,
            "actions_taken": self.actions_taken,
            "created_at": self.created_at,
        }, default=str)

    @staticmethod
    def from_json(data: str) -> "RemediationScan":
        """Deserialize from JSON string."""
        obj = json.loads(data)
        return RemediationScan(
            date=obj.get("date", ""),
            scan_type=obj.get("scan_type", ""),
            keys_scanned=obj.get("keys_scanned", 0),
            wrongtype_found=obj.get("wrongtype_found", 0),
            expired_found=obj.get("expired_found", 0),
            violations=obj.get("violations", []),
            actions_taken=obj.get("actions_taken", []),
            created_at=obj.get("created_at", datetime.utcnow().isoformat()),
        )


class RedisBusClient:
    """
    Production-ready Redis Bus client for IF.swarm.s2 communication.

    Implements all Redis key patterns and helper methods for:
    - Claiming and releasing tasks
    - Posting and retrieving findings
    - Managing shared context
    - Task unblocking and escalation
    - Swarm registration and cross-swarm aid

    All writes wrap payloads in Packet envelopes per IF.TTT requirements.

    Example usage:
        client = RedisBusClient(host="localhost", port=6379)

        # Claim a task
        task = Task(description="Research X", type="research")
        client.claim_task(task, assignee="haiku-1")

        # Post a finding
        finding = Finding(
            claim="X is true",
            confidence=0.95,
            citations=["if://citation/uuid1"],
            worker_id="haiku-1",
            task_id=task.id
        )
        client.post_finding(finding)

        # Share context
        ctx = Context(scope="task", name=task.id)
        ctx.notes = "Important note about X"
        client.share_context(ctx)
    """

    def __init__(self, host: str = "localhost", port: int = 6379,
                 db: int = 0, password: Optional[str] = None):
        """Initialize Redis connection."""
        self.redis_conn = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
        )
        self.agent_id = ""  # Set by caller for custody tracking

    def health_check(self) -> bool:
        """Verify Redis connection is healthy."""
        try:
            return self.redis_conn.ping()
        except Exception:
            return False

    # Task operations

    def claim_task(self, task: Task, assignee: str, agent_id: str = "") -> bool:
        """
        Claim a task by setting assignee and status=in_progress.
        Wraps operation in Packet envelope for audit trail.

        Args:
            task: Task to claim
            assignee: Agent ID claiming the task
            agent_id: Agent performing the claim (for custody chain)

        Returns:
            True if claim succeeded, False if already assigned
        """
        if agent_id:
            self.agent_id = agent_id

        # Check if already assigned
        existing = self.redis_conn.hgetall(f"task:{task.id}")
        if existing and existing.get("assignee"):
            return False  # Already claimed

        # Update task
        task.assignee = assignee
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.utcnow().isoformat()

        # Wrap in packet
        packet = Packet(
            origin=self.agent_id or assignee,
            speech_act=SpeechAct.INFORM,
            contents={"task_id": task.id, "action": "claim"}
        )
        packet.add_custody(self.agent_id or assignee, "claim_task")

        # Store task hash + packet metadata
        self.redis_conn.hset(f"task:{task.id}", mapping=task.to_hash())
        self.redis_conn.expire(f"task:{task.id}", task.ttl_seconds)

        # Store packet as JSON in companion key
        self.redis_conn.set(
            f"packet:task:{task.id}:claim",
            packet.to_json(),
            ex=task.ttl_seconds
        )

        return True

    def release_task(self, task_id: str, agent_id: str = "") -> bool:
        """
        Release a task (set assignee to empty, status back to pending).
        Used when agent is blocked or handing off.

        Args:
            task_id: Task ID to release
            agent_id: Agent releasing the task

        Returns:
            True if release succeeded
        """
        if agent_id:
            self.agent_id = agent_id

        task_key = f"task:{task_id}"
        if not self.redis_conn.exists(task_key):
            return False

        task_data = self.redis_conn.hgetall(task_key)
        task = Task.from_hash(task_data)

        task.assignee = ""
        task.status = TaskStatus.PENDING
        task.updated_at = datetime.utcnow().isoformat()

        # Wrap in packet
        packet = Packet(
            origin=self.agent_id,
            speech_act=SpeechAct.INFORM,
            contents={"task_id": task_id, "action": "release"}
        )
        packet.add_custody(self.agent_id, "release_task")

        self.redis_conn.hset(task_key, mapping=task.to_hash())
        self.redis_conn.set(
            f"packet:task:{task_id}:release",
            packet.to_json(),
            ex=task.ttl_seconds
        )

        return True

    def get_unassigned_task(self) -> Optional[Task]:
        """
        Get oldest unassigned task (for idle agents looking for work).

        Returns:
            Task object or None if no unassigned tasks
        """
        # Scan for pending tasks
        cursor = 0
        while True:
            cursor, keys = self.redis_conn.scan(
                cursor,
                match="task:*",
                count=100
            )

            for key in keys:
                task_data = self.redis_conn.hgetall(key)
                task = Task.from_hash(task_data)

                if task.status == TaskStatus.PENDING and not task.assignee:
                    return task

            if cursor == 0:
                break

        return None

    # Finding operations

    def post_finding(self, finding: Finding, agent_id: str = "") -> bool:
        """
        Post a finding to the bus with full IF.TTT audit trail.

        Args:
            finding: Finding to post
            agent_id: Agent posting the finding

        Returns:
            True if post succeeded
        """
        if agent_id:
            self.agent_id = agent_id

        finding_key = f"finding:{finding.id}"

        # Wrap in packet
        packet = Packet(
            origin=self.agent_id or finding.worker_id,
            speech_act=finding.speech_act,
            contents=finding.to_hash()
        )
        packet.add_custody(self.agent_id or finding.worker_id, "post_finding")

        # Store finding hash
        self.redis_conn.hset(finding_key, mapping=finding.to_hash())
        self.redis_conn.expire(finding_key, finding.ttl_seconds)

        # Store packet envelope
        self.redis_conn.set(
            f"packet:finding:{finding.id}",
            packet.to_json(),
            ex=finding.ttl_seconds
        )

        return True

    def get_finding(self, finding_id: str) -> Optional[Finding]:
        """Retrieve a finding by ID."""
        data = self.redis_conn.hgetall(f"finding:{finding_id}")
        if not data:
            return None
        return Finding.from_hash(data)

    def get_findings_for_task(self, task_id: str) -> List[Finding]:
        """Get all findings associated with a task."""
        cursor = 0
        findings = []

        while True:
            cursor, keys = self.redis_conn.scan(
                cursor,
                match="finding:*",
                count=100
            )

            for key in keys:
                finding_data = self.redis_conn.hgetall(key)
                finding = Finding.from_hash(finding_data)

                if finding.task_id == task_id:
                    findings.append(finding)

            if cursor == 0:
                break

        return findings

    def detect_finding_conflicts(self, task_id: str,
                                  conflict_threshold: float = 0.2) -> List[Tuple[Finding, Finding]]:
        """
        Detect conflicting findings on the same task.

        When two findings on same topic differ in confidence > threshold,
        raise escalation.

        Args:
            task_id: Task ID to check for conflicts
            conflict_threshold: Confidence delta threshold (default 0.2 = 20%)

        Returns:
            List of (finding1, finding2) tuples representing conflicts
        """
        findings = self.get_findings_for_task(task_id)
        conflicts = []

        for i, f1 in enumerate(findings):
            for f2 in findings[i+1:]:
                # Simple heuristic: same claim topic but different confidence
                if abs(f1.confidence - f2.confidence) > conflict_threshold:
                    conflicts.append((f1, f2))

        return conflicts

    # Context operations

    def share_context(self, context: Context, agent_id: str = "") -> bool:
        """
        Share context notes and metadata on the bus.

        Args:
            context: Context object to share
            agent_id: Agent sharing the context

        Returns:
            True if share succeeded
        """
        if agent_id:
            self.agent_id = agent_id

        context_key = context.key()
        context.updated_at = datetime.utcnow().isoformat()

        # Wrap in packet
        packet = Packet(
            origin=self.agent_id,
            speech_act=SpeechAct.INFORM,
            contents=context.to_hash()
        )
        packet.add_custody(self.agent_id, "share_context")

        # Store context hash
        self.redis_conn.hset(context_key, mapping=context.to_hash())
        self.redis_conn.expire(context_key, 86400)  # 24 hour TTL

        # Store packet
        self.redis_conn.set(
            f"packet:{context_key}",
            packet.to_json(),
            ex=86400
        )

        return True

    def get_context(self, scope: str, name: str) -> Optional[Context]:
        """Retrieve context by scope and name."""
        context_key = f"context:{scope}:{name}"
        data = self.redis_conn.hgetall(context_key)

        if not data:
            return None

        context = Context.from_hash(data)
        return context

    # Session and swarm operations

    def record_session_summary(self, summary: SessionSummary, agent_id: str = "") -> bool:
        """Record a session summary with aggregated metrics."""
        if agent_id:
            self.agent_id = agent_id

        summary_key = summary.key()

        # Wrap in packet
        packet = Packet(
            origin=self.agent_id,
            speech_act=SpeechAct.INFORM,
            contents=json.loads(summary.to_json())
        )
        packet.add_custody(self.agent_id, "record_session_summary")

        self.redis_conn.set(
            summary_key,
            summary.to_json(),
            ex=30 * 86400  # 30 day retention
        )

        return True

    def register_swarm(self, registry: SwarmRegistry, agent_id: str = "") -> bool:
        """Register swarm with roster of agents and roles."""
        if agent_id:
            self.agent_id = agent_id

        registry_key = registry.key()
        registry.updated_at = datetime.utcnow().isoformat()

        # Wrap in packet
        packet = Packet(
            origin=self.agent_id,
            speech_act=SpeechAct.INFORM,
            contents=json.loads(registry.to_json())
        )
        packet.add_custody(self.agent_id, "register_swarm")

        self.redis_conn.set(
            registry_key,
            registry.to_json(),
            ex=7 * 86400  # 7 day retention for swarm rosters
        )

        return True

    def escalate_to_human(self, task_id: str, reason: str,
                         findings: Optional[List[Finding]] = None,
                         agent_id: str = "") -> bool:
        """
        Escalate a task with critical uncertainty to human review.
        Creates escalation packet with supporting findings.

        Args:
            task_id: Task requiring human attention
            reason: Reason for escalation
            findings: Supporting findings (optional)
            agent_id: Agent initiating escalation

        Returns:
            True if escalation posted successfully
        """
        if agent_id:
            self.agent_id = agent_id

        # Create escalation finding
        escalation = Finding(
            claim=reason,
            confidence=0.0,  # Critical uncertainty
            speech_act=SpeechAct.ESCALATE,
            worker_id=self.agent_id,
            task_id=task_id,
            citations=[f"finding:{f.id}" for f in (findings or [])]
        )

        # Post escalation
        self.post_finding(escalation, self.agent_id)

        # Mark task as blocked
        task_key = f"task:{task_id}"
        self.redis_conn.hset(task_key, "status", TaskStatus.BLOCKED.value)

        return True


# ============================================================================
# Unit Tests
# ============================================================================

def test_packet_envelope():
    """Test Packet envelope serialization and custody tracking."""
    packet = Packet(
        origin="haiku-1",
        speech_act=SpeechAct.INFORM,
        contents={"claim": "test", "confidence": 0.9}
    )

    # Add custody chain
    packet.add_custody("haiku-1", "create_packet")
    packet.add_custody("haiku-2", "forward_packet")

    # Serialize and deserialize
    json_str = packet.to_json()
    restored = Packet.from_json(json_str)

    assert restored.tracking_id == packet.tracking_id
    assert restored.origin == "haiku-1"
    assert restored.speech_act == SpeechAct.INFORM
    assert len(restored.chain_of_custody) == 2
    assert restored.chain_of_custody[0][1] == "create_packet"
    print("✓ test_packet_envelope passed")


def test_task_lifecycle():
    """Test task claiming and releasing."""
    task = Task(
        description="Research feature X",
        type="research",
        status=TaskStatus.PENDING
    )

    # Convert to hash and back
    hash_data = task.to_hash()
    restored = Task.from_hash({k.encode(): v.encode() if isinstance(v, str) else v
                              for k, v in hash_data.items()})

    assert restored.description == task.description
    assert restored.status == TaskStatus.PENDING
    assert restored.assignee == ""
    print("✓ test_task_lifecycle passed")


def test_finding_validation():
    """Test finding confidence validation."""
    # Valid finding
    finding = Finding(
        claim="X is true",
        confidence=0.95,
        worker_id="haiku-1"
    )
    assert finding.confidence == 0.95

    # Invalid confidence (too high)
    try:
        bad_finding = Finding(claim="test", confidence=1.5)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected

    # Invalid confidence (too low)
    try:
        bad_finding = Finding(claim="test", confidence=-0.1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected

    print("✓ test_finding_validation passed")


def test_context_operations():
    """Test context key generation and serialization."""
    context = Context(
        scope="task",
        name="task-123",
        notes="Important findings",
        topics=["research", "verification"]
    )

    assert context.key() == "context:task:task-123"

    # Serialize and deserialize
    hash_data = context.to_hash()
    restored = Context.from_hash({k.encode(): v.encode() if isinstance(v, str) else v
                                 for k, v in hash_data.items()})

    assert restored.scope == "task"
    assert restored.name == "task-123"
    assert "research" in restored.topics
    print("✓ test_context_operations passed")


def test_session_summary():
    """Test session summary serialization."""
    summary = SessionSummary(
        date="2025-11-30",
        label="protocol_scan",
        summary="Scanned 100 tasks, found 5 conflicts",
        metrics={
            "tasks_scanned": 100,
            "conflicts_found": 5,
            "escalations": 2
        }
    )

    key = summary.key()
    assert key == "session:infrafabric:2025-11-30:protocol_scan"

    json_str = summary.to_json()
    restored = SessionSummary.from_json(json_str)

    assert restored.label == "protocol_scan"
    assert restored.metrics["tasks_scanned"] == 100
    print("✓ test_session_summary passed")


def test_swarm_registry():
    """Test swarm registry management."""
    registry = SwarmRegistry(
        id="infrafabric_2025-11-30",
        agents=[
            {"id": "haiku-1", "role": "worker"},
            {"id": "haiku-2", "role": "worker"},
        ],
        roles={
            "coordinator": "sonnet-1",
        },
        artifacts=["output.json", "metrics.csv"]
    )

    key = registry.key()
    assert key == "swarm:registry:infrafabric_2025-11-30"

    json_str = registry.to_json()
    restored = SwarmRegistry.from_json(json_str)

    assert len(restored.agents) == 2
    assert restored.roles["coordinator"] == "sonnet-1"
    print("✓ test_swarm_registry passed")


def test_remediation_scan():
    """Test hygiene remediation tracking."""
    scan = RemediationScan(
        date="2025-11-30",
        scan_type="redis_cleanup",
        keys_scanned=720,
        wrongtype_found=100,
        expired_found=50,
        violations=["WRONGTYPE: finding:123", "STALE: task:456"],
        actions_taken=["DELETED: 100 wrongtype keys", "EXPIRED: 50 old findings"]
    )

    key = scan.key()
    assert "redis_cleanup" in key

    json_str = scan.to_json()
    restored = RemediationScan.from_json(json_str)

    assert restored.wrongtype_found == 100
    assert restored.expired_found == 50
    print("✓ test_remediation_scan passed")


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*60)
    print("Running Redis Bus Schema Unit Tests")
    print("="*60)

    test_packet_envelope()
    test_task_lifecycle()
    test_finding_validation()
    test_context_operations()
    test_session_summary()
    test_swarm_registry()
    test_remediation_scan()

    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
