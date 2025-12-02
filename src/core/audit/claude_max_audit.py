#!/usr/bin/env python3
"""
Claude Max Audit System - Comprehensive Agent Communication & Context Tracking

if://code/claude-max-audit/2025-11-30

Role: Implements complete audit trail for all Claude Max communications, context access,
security events, and decision logging with IF.TTT (Traceable, Transparent, Trustworthy)
compliance.

Architecture:
  - Hot Storage (Redis): 30-day rolling window for fast queries, real-time analytics
  - Cold Storage (ChromaDB): 30+ days archived, semantic search capability, 7-year retention
  - Async Logging: Non-blocking event capture for high-throughput messaging
  - Batch Inserts: Group 10+ entries before Redis write to optimize performance
  - IF.Citation Integration: Every audit entry gets unique if://citation URI

Queryable Dimensions:
  - By agent_id (all messages from/to specific agent)
  - By swarm_id (all activity in swarm or cross-swarm)
  - By time range (ISO8601 start/end)
  - By message type (inform, request, escalate, hold)
  - By security severity (low, medium, high, critical)
  - By content hash (find duplicates or specific messages)
  - Semantic search (natural language queries on archived logs)

Security Events Logged:
  - Rate limit violations
  - Authentication failures
  - Unauthorized access attempts
  - Anomalous message patterns
  - Confidence score manipulation
  - Context poisoning attempts
  - Cross-swarm anomalies

Retention Policy:
  - Redis (hot): 30 days rolling window
  - ChromaDB (cold): 7 years minimum
  - Daily archival: Compress + embed + transfer
  - Auto-purge: After 7 years unless flagged for permanent retention
"""

import asyncio
import hashlib
import json
import logging
import os
import redis
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import sys

# Setup path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Optional ChromaDB integration
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except (ModuleNotFoundError, ImportError):
    CHROMADB_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class AuditEntryType(Enum):
    """Types of audit entries"""
    MESSAGE = "message"
    CONTEXT_ACCESS = "context_access"
    DECISION = "decision"
    SECURITY_EVENT = "security_event"
    PERFORMANCE_METRIC = "performance_metric"


class MessageType(Enum):
    """Types of agent-to-agent messages"""
    INFORM = "inform"          # Information sharing
    REQUEST = "request"        # Task/context request
    ESCALATE = "escalate"      # Security/governance escalation
    HOLD = "hold"              # Pause/context freeze
    RESPONSE = "response"      # Response to request
    ERROR = "error"            # Error notification


class SecuritySeverity(Enum):
    """Security event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OperationType(Enum):
    """Context operations"""
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class AuditEntry:
    """
    Complete audit entry with all metadata.

    Attributes:
        entry_id: Unique UUID for this entry
        timestamp: ISO8601 creation timestamp
        agent_id: Source agent identifier
        swarm_id: Source swarm identifier
        entry_type: Type of audit entry (message, context_access, decision, security)
        from_agent: Source agent (for messages)
        to_agent: Destination agent (for messages)
        message_type: Message type (inform, request, escalate, hold)
        content_hash: SHA-256 hash of payload for deduplication
        size_bytes: Size of logged content
        metadata: Entry-specific metadata dict
        citation: IF.citation URI for this entry
        severity: Security severity level (for security events)
        context_window_size: Size of context accessed/modified
        swarm_ids: Set of all swarms involved (for cross-swarm messages)
    """
    entry_id: str
    timestamp: datetime
    agent_id: str
    swarm_id: str
    entry_type: AuditEntryType
    from_agent: Optional[str] = None
    to_agent: Optional[str] = None
    message_type: Optional[MessageType] = None
    content_hash: str = ""
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    citation: Optional[str] = None
    severity: Optional[SecuritySeverity] = None
    context_window_size: int = 0
    swarm_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['entry_type'] = self.entry_type.value
        data['message_type'] = self.message_type.value if self.message_type else None
        data['severity'] = self.severity.value if self.severity else None
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class AuditQueryResult:
    """Results from an audit query"""
    entries: List[AuditEntry]
    total_count: int
    query_time_ms: float
    source: str  # "redis" or "chromadb"


@dataclass
class PerformanceMetrics:
    """Performance metrics for audit operations"""
    messages_per_second: float = 0.0
    avg_log_latency_ms: float = 0.0
    active_agents: int = 0
    total_entries_hot: int = 0
    total_entries_cold: int = 0
    cross_swarm_messages: int = 0


# =============================================================================
# CITATION GENERATOR
# =============================================================================

class CitationGenerator:
    """Generate IF.citation URIs for audit entries"""

    @staticmethod
    def generate(entry_type: AuditEntryType, entry_id: str) -> str:
        """
        Generate IF.citation URI for audit entry.

        Format: if://audit/{entry_type}/{entry_id}
        Example: if://audit/decision/a1b2c3d4-5678-90ef-ghij-klmnopqrstuv

        Args:
            entry_type: Type of audit entry
            entry_id: Unique entry identifier

        Returns:
            IF.citation URI string
        """
        return f"if://audit/{entry_type.value}/{entry_id}"

    @staticmethod
    def parse(citation: str) -> Tuple[str, str, str]:
        """
        Parse IF.citation URI.

        Args:
            citation: IF.citation URI to parse

        Returns:
            Tuple of (scheme, entry_type, entry_id)
        """
        if not citation.startswith("if://audit/"):
            raise ValueError(f"Invalid audit citation format: {citation}")

        parts = citation.replace("if://audit/", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Malformed audit citation: {citation}")

        return "audit", parts[0], parts[1]


# =============================================================================
# CLAUDE MAX AUDITOR
# =============================================================================

class ClaudeMaxAuditor:
    """
    Central audit system for all Claude Max communications and context access.

    Implements dual-tier storage with Redis (hot) and ChromaDB (cold), async logging,
    IF.TTT compliance, and comprehensive query capabilities.
    """

    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        storage_backend: str = "redis+chromadb",
        chromadb_path: Optional[str] = None,
        batch_size: int = 10,
        hot_storage_days: int = 30,
        cold_storage_years: int = 7
    ):
        """
        Initialize Claude Max Auditor.

        Args:
            redis_client: Existing Redis client (optional)
            redis_host: Redis host (default: localhost)
            redis_port: Redis port (default: 6379)
            redis_db: Redis database number (default: 0)
            storage_backend: "redis", "chromadb", or "redis+chromadb"
            chromadb_path: Path for ChromaDB storage
            batch_size: Number of entries to batch before writing
            hot_storage_days: Days to keep in hot storage (default: 30)
            cold_storage_years: Years to keep in cold storage (default: 7)
        """
        # Redis setup
        if redis_client:
            self.redis = redis_client
        else:
            try:
                self.redis = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
                self.redis.ping()
                logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
            except redis.ConnectionError as e:
                logger.warning(f"Redis connection failed: {e}. Audit logging degraded.")
                self.redis = None

        # ChromaDB setup
        self.chromadb = None
        self.chromadb_collection = None
        if storage_backend in {"chromadb", "redis+chromadb"} and CHROMADB_AVAILABLE:
            try:
                chroma_path = chromadb_path or os.path.join(PROJECT_ROOT, "audit_store")
                os.makedirs(chroma_path, exist_ok=True)

                settings = ChromaSettings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=chroma_path,
                    anonymized_telemetry=False
                )
                self.chromadb = chromadb.Client(settings)

                # Get or create collection for audit entries
                self.chromadb_collection = self.chromadb.get_or_create_collection(
                    name="claude_max_audit",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Connected to ChromaDB at {chroma_path}")
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}")
                self.chromadb = None

        # Configuration
        self.storage_backend = storage_backend
        self.batch_size = batch_size
        self.hot_storage_days = hot_storage_days
        self.cold_storage_years = cold_storage_years

        # Batch queue for async operations
        self.batch_queue: List[AuditEntry] = []
        self.batch_lock = asyncio.Lock()

        # Citation generator
        self.citation_gen = CitationGenerator()

    # =========================================================================
    # MESSAGE LOGGING
    # =========================================================================

    async def log_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        content: str,
        swarm_id: Optional[str] = None,
        from_swarm: Optional[str] = None,
        to_swarm: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log agent-to-agent message.

        Args:
            from_agent: Source agent ID
            to_agent: Destination agent ID
            message_type: Type of message (inform, request, escalate, hold)
            content: Message content
            swarm_id: Swarm identifier (defaults to from_swarm or to_swarm)
            from_swarm: Source swarm ID
            to_swarm: Destination swarm ID
            metadata: Additional metadata (priority, latency, etc.)

        Returns:
            Entry ID (UUID)
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Determine swarm context
        swarm_id = swarm_id or from_swarm or to_swarm or "unknown"
        swarm_ids = [from_swarm, to_swarm] if from_swarm and to_swarm and from_swarm != to_swarm else [swarm_id]
        swarm_ids = [s for s in swarm_ids if s]  # Remove None/empty

        citation = self.citation_gen.generate(AuditEntryType.MESSAGE, entry_id)

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            agent_id=from_agent,
            swarm_id=swarm_id,
            entry_type=AuditEntryType.MESSAGE,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content_hash=content_hash,
            size_bytes=len(content.encode('utf-8')),
            metadata=metadata or {"cross_swarm": len(swarm_ids) > 1},
            citation=citation,
            swarm_ids=swarm_ids
        )

        await self._queue_entry(entry)
        logger.debug(f"Logged message {entry_id}: {from_agent} -> {to_agent}")

        return entry_id

    # =========================================================================
    # CONTEXT ACCESS LOGGING
    # =========================================================================

    async def log_context_access(
        self,
        agent_id: str,
        session_id: str,
        operation: OperationType,
        size_bytes: int,
        swarm_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log context read/write operations.

        Args:
            agent_id: Agent accessing context
            session_id: Session identifier
            operation: Type of operation (read, write, update, delete)
            size_bytes: Size of context accessed/modified
            swarm_id: Swarm identifier
            metadata: Additional metadata (context_version, chunk_count, etc.)

        Returns:
            Entry ID (UUID)
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        swarm_id = swarm_id or "unknown"

        citation = self.citation_gen.generate(AuditEntryType.CONTEXT_ACCESS, entry_id)

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            agent_id=agent_id,
            swarm_id=swarm_id,
            entry_type=AuditEntryType.CONTEXT_ACCESS,
            context_window_size=size_bytes,
            metadata={
                "session_id": session_id,
                "operation": operation.value,
                **(metadata or {})
            },
            citation=citation
        )

        await self._queue_entry(entry)
        logger.debug(f"Logged context access {entry_id}: {agent_id} {operation.value}")

        return entry_id

    # =========================================================================
    # DECISION LOGGING
    # =========================================================================

    async def log_decision(
        self,
        agent_id: str,
        decision_type: str,
        rationale: str,
        citation: str,
        swarm_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log significant decisions with IF.citation.

        Args:
            agent_id: Agent making decision
            decision_type: Type of decision (governance, escalation, routing, etc.)
            rationale: Explanation of decision
            citation: IF.citation URI for the decision source
            swarm_id: Swarm identifier
            metadata: Additional metadata (confidence_score, alternatives, etc.)

        Returns:
            Entry ID (UUID)
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        swarm_id = swarm_id or "unknown"

        decision_citation = self.citation_gen.generate(AuditEntryType.DECISION, entry_id)

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            agent_id=agent_id,
            swarm_id=swarm_id,
            entry_type=AuditEntryType.DECISION,
            metadata={
                "decision_type": decision_type,
                "rationale": rationale,
                "source_citation": citation,
                **(metadata or {})
            },
            citation=decision_citation
        )

        await self._queue_entry(entry)
        logger.debug(f"Logged decision {entry_id}: {decision_type}")

        return entry_id

    # =========================================================================
    # SECURITY EVENT LOGGING
    # =========================================================================

    async def log_security_event(
        self,
        agent_id: str,
        event_type: str,
        severity: SecuritySeverity,
        details: Dict[str, Any],
        swarm_id: Optional[str] = None
    ) -> str:
        """
        Log security violations and anomalies.

        Security events include:
          - Rate limit violations
          - Authentication failures
          - Unauthorized access attempts
          - Anomalous message patterns
          - Confidence score manipulation
          - Context poisoning attempts
          - Cross-swarm anomalies

        Args:
            agent_id: Agent involved in security event
            event_type: Type of security event
            severity: Severity level (low, medium, high, critical)
            details: Event details and context
            swarm_id: Swarm identifier

        Returns:
            Entry ID (UUID)
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        swarm_id = swarm_id or "unknown"

        citation = self.citation_gen.generate(AuditEntryType.SECURITY_EVENT, entry_id)

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            agent_id=agent_id,
            swarm_id=swarm_id,
            entry_type=AuditEntryType.SECURITY_EVENT,
            severity=severity,
            metadata={
                "event_type": event_type,
                **details
            },
            citation=citation
        )

        await self._queue_entry(entry)

        # Log at appropriate level
        log_level = {
            SecuritySeverity.LOW: logging.INFO,
            SecuritySeverity.MEDIUM: logging.WARNING,
            SecuritySeverity.HIGH: logging.ERROR,
            SecuritySeverity.CRITICAL: logging.CRITICAL
        }.get(severity, logging.WARNING)

        logger.log(
            log_level,
            f"Security event {entry_id} [{severity.value}]: {event_type} (agent={agent_id})"
        )

        return entry_id

    # =========================================================================
    # PERFORMANCE METRICS
    # =========================================================================

    async def log_performance_metric(
        self,
        agent_id: str,
        metric_type: str,
        value: float,
        unit: str,
        swarm_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log performance metrics for monitoring.

        Args:
            agent_id: Agent associated with metric
            metric_type: Type of metric (latency, throughput, memory, etc.)
            value: Metric value
            unit: Unit of measurement
            swarm_id: Swarm identifier
            metadata: Additional metadata

        Returns:
            Entry ID (UUID)
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        swarm_id = swarm_id or "unknown"

        citation = self.citation_gen.generate(AuditEntryType.PERFORMANCE_METRIC, entry_id)

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            agent_id=agent_id,
            swarm_id=swarm_id,
            entry_type=AuditEntryType.PERFORMANCE_METRIC,
            metadata={
                "metric_type": metric_type,
                "value": value,
                "unit": unit,
                **(metadata or {})
            },
            citation=citation
        )

        await self._queue_entry(entry)
        return entry_id

    # =========================================================================
    # QUEUING & STORAGE
    # =========================================================================

    async def _queue_entry(self, entry: AuditEntry) -> None:
        """Queue entry for batch insert"""
        async with self.batch_lock:
            self.batch_queue.append(entry)

            if len(self.batch_queue) >= self.batch_size:
                await self._flush_batch()

    async def _flush_batch(self) -> None:
        """Flush queued entries to storage"""
        if not self.batch_queue:
            return

        entries = self.batch_queue.copy()
        self.batch_queue.clear()

        # Write to Redis (hot storage)
        if self.redis:
            try:
                for entry in entries:
                    date_key = entry.timestamp.strftime("%Y-%m-%d")

                    # Add to date-based sorted set
                    self.redis.zadd(
                        f"audit:entries:{date_key}",
                        {entry.entry_id: entry.timestamp.timestamp()}
                    )

                    # Add to agent index
                    self.redis.sadd(f"audit:agent:{entry.agent_id}", entry.entry_id)

                    # Add to swarm index
                    for swarm_id in entry.swarm_ids or [entry.swarm_id]:
                        self.redis.sadd(f"audit:swarm:{swarm_id}", entry.entry_id)

                    # Store full entry
                    self.redis.hset(f"audit:entry:{entry.entry_id}", mapping=entry.to_dict())

                    # Set expiration (30 days)
                    self.redis.expire(f"audit:entry:{entry.entry_id}", 30 * 24 * 3600)

                logger.debug(f"Flushed {len(entries)} entries to Redis")
            except Exception as e:
                logger.error(f"Failed to write to Redis: {e}")

        # Write to ChromaDB (cold storage with embeddings)
        if self.chromadb_collection:
            try:
                ids = [entry.entry_id for entry in entries]
                documents = [entry.to_json() for entry in entries]
                metadatas = [
                    {
                        "agent_id": entry.agent_id,
                        "swarm_id": entry.swarm_id,
                        "entry_type": entry.entry_type.value,
                        "timestamp": entry.timestamp.isoformat(),
                        "severity": entry.severity.value if entry.severity else "none"
                    }
                    for entry in entries
                ]

                self.chromadb_collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.debug(f"Archived {len(entries)} entries to ChromaDB")
            except Exception as e:
                logger.error(f"Failed to write to ChromaDB: {e}")

    async def flush_all(self) -> None:
        """Force flush all pending entries"""
        async with self.batch_lock:
            await self._flush_batch()

    # =========================================================================
    # QUERYING
    # =========================================================================

    async def search_logs(
        self,
        query: Dict[str, Any],
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> AuditQueryResult:
        """
        Search audit logs with multiple dimensions.

        Supported query keys:
          - agent_id: Search by agent
          - swarm_id: Search by swarm
          - entry_type: Search by entry type
          - message_type: Search by message type
          - severity: Search by security severity
          - content_hash: Find specific message

        Args:
            query: Query criteria dict
            time_range: Optional (start_datetime, end_datetime) tuple
            limit: Max results to return
            offset: Result offset

        Returns:
            AuditQueryResult with matching entries
        """
        start_time = datetime.utcnow()

        # Try Redis first (hot storage)
        if self.redis and time_range:
            start_dt, end_dt = time_range
            result = await self._search_redis(query, start_dt, end_dt, limit, offset)
            if result:
                query_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                return AuditQueryResult(
                    entries=result,
                    total_count=len(result),
                    query_time_ms=query_time,
                    source="redis"
                )

        # Fall back to ChromaDB for semantic/archived searches
        if self.chromadb_collection:
            result = await self._search_chromadb(query, limit, offset)
            if result:
                query_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                return AuditQueryResult(
                    entries=result,
                    total_count=len(result),
                    query_time_ms=query_time,
                    source="chromadb"
                )

        query_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        return AuditQueryResult(entries=[], total_count=0, query_time_ms=query_time, source="none")

    async def _search_redis(
        self,
        query: Dict[str, Any],
        start_dt: datetime,
        end_dt: datetime,
        limit: int,
        offset: int
    ) -> List[AuditEntry]:
        """Search Redis hot storage"""
        if not self.redis:
            return []

        results = []

        try:
            # Build key pattern based on query
            if "agent_id" in query:
                agent_id = query["agent_id"]
                entry_ids = self.redis.smembers(f"audit:agent:{agent_id}")
            elif "swarm_id" in query:
                swarm_id = query["swarm_id"]
                entry_ids = self.redis.smembers(f"audit:swarm:{swarm_id}")
            else:
                # Scan date range
                entry_ids = set()
                current = start_dt
                while current <= end_dt:
                    date_key = current.strftime("%Y-%m-%d")
                    daily_ids = self.redis.zrange(f"audit:entries:{date_key}", 0, -1)
                    entry_ids.update(daily_ids)
                    current += timedelta(days=1)

            # Fetch entries and filter
            for entry_id in sorted(entry_ids)[offset:offset+limit]:
                entry_data = self.redis.hgetall(f"audit:entry:{entry_id}")
                if entry_data:
                    entry = self._dict_to_entry(entry_data)

                    # Apply additional filters
                    if self._matches_query(entry, query):
                        results.append(entry)

            return results[:limit]
        except Exception as e:
            logger.error(f"Redis search failed: {e}")
            return []

    async def _search_chromadb(
        self,
        query: Dict[str, Any],
        limit: int,
        offset: int
    ) -> List[AuditEntry]:
        """Search ChromaDB for semantic/archived queries"""
        if not self.chromadb_collection:
            return []

        try:
            # Handle semantic search if query string provided
            if "text_query" in query:
                results = self.chromadb_collection.query(
                    query_texts=[query["text_query"]],
                    n_results=limit,
                    where=self._build_chromadb_where(query) if query else None
                )

                entries = []
                if results["ids"] and len(results["ids"]) > 0:
                    for entry_json in results["documents"][0][offset:offset+limit]:
                        entry_dict = json.loads(entry_json)
                        entries.append(self._dict_to_entry(entry_dict))
                return entries

            # Regular metadata query
            results = self.chromadb_collection.get(
                where=self._build_chromadb_where(query),
                limit=limit,
                offset=offset
            )

            entries = []
            if results["ids"]:
                for entry_json in results["documents"]:
                    entry_dict = json.loads(entry_json)
                    entries.append(self._dict_to_entry(entry_dict))
            return entries
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []

    def _build_chromadb_where(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB where clause from query"""
        where_clauses = []

        if "agent_id" in query:
            where_clauses.append({"agent_id": {"$eq": query["agent_id"]}})
        if "severity" in query:
            where_clauses.append({"severity": {"$eq": query["severity"]}})
        if "entry_type" in query:
            where_clauses.append({"entry_type": {"$eq": query["entry_type"]}})

        if len(where_clauses) == 1:
            return where_clauses[0]
        elif len(where_clauses) > 1:
            return {"$and": where_clauses}
        return {}

    def _matches_query(self, entry: AuditEntry, query: Dict[str, Any]) -> bool:
        """Check if entry matches query criteria"""
        if "entry_type" in query and entry.entry_type.value != query["entry_type"]:
            return False
        if "message_type" in query and entry.message_type and entry.message_type.value != query["message_type"]:
            return False
        if "severity" in query and entry.severity and entry.severity.value != query["severity"]:
            return False
        if "content_hash" in query and entry.content_hash != query["content_hash"]:
            return False
        return True

    def _dict_to_entry(self, data: Dict[str, Any]) -> AuditEntry:
        """Convert dict from storage to AuditEntry"""
        return AuditEntry(
            entry_id=data.get("entry_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"],
            agent_id=data.get("agent_id", ""),
            swarm_id=data.get("swarm_id", ""),
            entry_type=AuditEntryType(data.get("entry_type", "message")),
            from_agent=data.get("from_agent"),
            to_agent=data.get("to_agent"),
            message_type=MessageType(data["message_type"]) if data.get("message_type") else None,
            content_hash=data.get("content_hash", ""),
            size_bytes=int(data.get("size_bytes", 0)),
            metadata=json.loads(data.get("metadata", "{}")) if isinstance(data.get("metadata"), str) else data.get("metadata", {}),
            citation=data.get("citation"),
            severity=SecuritySeverity(data["severity"]) if data.get("severity") and data["severity"] != "none" else None,
            context_window_size=int(data.get("context_window_size", 0)),
            swarm_ids=json.loads(data.get("swarm_ids", "[]")) if isinstance(data.get("swarm_ids"), str) else data.get("swarm_ids", [])
        )

    # =========================================================================
    # CITATION & EXPORT
    # =========================================================================

    async def generate_citation(self, entry_id: str) -> str:
        """
        Generate or retrieve IF.citation for audit entry.

        Args:
            entry_id: Audit entry ID

        Returns:
            IF.citation URI
        """
        if self.redis:
            entry_data = self.redis.hgetall(f"audit:entry:{entry_id}")
            if entry_data and "citation" in entry_data:
                return entry_data["citation"]

        # Generate new citation
        return self.citation_gen.generate(AuditEntryType.MESSAGE, entry_id)

    async def export_audit_trail(
        self,
        swarm_id: str,
        format: str = "jsonl",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Export complete audit trail for a swarm.

        Formats: jsonl, json, csv

        Args:
            swarm_id: Swarm to export
            format: Export format (jsonl, json, csv)
            start_date: Start of date range
            end_date: End of date range
            output_path: File path for export (defaults to temp)

        Returns:
            Path to exported file
        """
        results = await self.search_logs(
            {"swarm_id": swarm_id},
            (start_date, end_date) if start_date and end_date else None,
            limit=100000
        )

        if not output_path:
            output_path = f"/tmp/audit_export_{swarm_id}_{datetime.utcnow().timestamp()}.{format}"

        # Write export
        with open(output_path, "w") as f:
            if format == "jsonl":
                for entry in results.entries:
                    f.write(entry.to_json() + "\n")
            elif format == "json":
                f.write(json.dumps([entry.to_dict() for entry in results.entries], default=str, indent=2))
            elif format == "csv":
                import csv
                if results.entries:
                    writer = csv.DictWriter(f, fieldnames=results.entries[0].to_dict().keys())
                    writer.writeheader()
                    for entry in results.entries:
                        writer.writerow(entry.to_dict())

        logger.info(f"Exported {len(results.entries)} entries to {output_path}")
        return output_path

    # =========================================================================
    # METRICS & MONITORING
    # =========================================================================

    async def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        if not self.redis:
            return PerformanceMetrics()

        try:
            # Count active agents and messages
            all_agents = set()
            hot_count = 0
            cross_swarm = 0

            for key in self.redis.scan_iter("audit:agent:*"):
                agent_id = key.replace("audit:agent:", "")
                all_agents.add(agent_id)
                count = self.redis.scard(key)
                hot_count += count

            # Count cross-swarm messages
            for key in self.redis.scan_iter("audit:entry:*"):
                entry_data = self.redis.hgetall(key)
                swarm_ids = entry_data.get("swarm_ids", "[]")
                swarm_list = json.loads(swarm_ids) if isinstance(swarm_ids, str) else swarm_ids
                if len(swarm_list) > 1:
                    cross_swarm += 1

            return PerformanceMetrics(
                active_agents=len(all_agents),
                total_entries_hot=hot_count,
                cross_swarm_messages=cross_swarm
            )
        except Exception as e:
            logger.error(f"Failed to compute metrics: {e}")
            return PerformanceMetrics()

    # =========================================================================
    # CLEANUP & MAINTENANCE
    # =========================================================================

    async def archive_old_entries(self, days_old: int = 30) -> int:
        """
        Move entries older than days_old from Redis to ChromaDB.

        Args:
            days_old: Age threshold in days

        Returns:
            Number of entries archived
        """
        if not self.redis or not self.chromadb_collection:
            return 0

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        archived_count = 0

        try:
            # Find old date keys
            current = datetime.utcnow() - timedelta(days=90)  # Scan last 90 days
            while current < cutoff_date:
                date_key = current.strftime("%Y-%m-%d")
                entry_ids = self.redis.zrange(f"audit:entries:{date_key}", 0, -1)

                for entry_id in entry_ids:
                    entry_data = self.redis.hgetall(f"audit:entry:{entry_id}")
                    if entry_data:
                        # Ensure in ChromaDB
                        if self.chromadb_collection:
                            self.chromadb_collection.upsert(
                                ids=[entry_id],
                                documents=[json.dumps(entry_data, default=str)],
                                metadatas=[{"archived_at": datetime.utcnow().isoformat()}]
                            )

                        # Remove from Redis
                        self.redis.delete(f"audit:entry:{entry_id}")
                        archived_count += 1

                current += timedelta(days=1)

            logger.info(f"Archived {archived_count} entries")
            return archived_count
        except Exception as e:
            logger.error(f"Archival failed: {e}")
            return 0

    async def cleanup_expired_entries(self, older_than_days: int = 2555) -> int:
        """
        Purge entries older than 7 years (unless flagged for permanent retention).

        Args:
            older_than_days: Age threshold in days (default: 7 years = 2555 days)

        Returns:
            Number of entries purged
        """
        if not self.chromadb_collection:
            return 0

        cutoff_date = (datetime.utcnow() - timedelta(days=older_than_days)).isoformat()
        purged_count = 0

        try:
            # Note: This is a simplified version. In production, implement proper
            # filtering in ChromaDB or use separate "retention" metadata field
            logger.info(f"Cleanup scan for entries before {cutoff_date}")
            return purged_count
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Global auditor instance
_auditor: Optional[ClaudeMaxAuditor] = None


def get_auditor(
    redis_client: Optional[redis.Redis] = None,
    redis_host: str = "localhost",
    redis_port: int = 6379
) -> ClaudeMaxAuditor:
    """Get or create global auditor instance"""
    global _auditor
    if _auditor is None:
        _auditor = ClaudeMaxAuditor(
            redis_client=redis_client,
            redis_host=redis_host,
            redis_port=redis_port
        )
    return _auditor


if __name__ == "__main__":
    # Example usage
    import asyncio

    async def example():
        auditor = ClaudeMaxAuditor()

        # Log a message
        msg_id = await auditor.log_message(
            from_agent="sonnet_coordinator_abc123",
            to_agent="haiku_worker_def456",
            message_type=MessageType.REQUEST,
            content="Please analyze the provided context",
            from_swarm="swarm_primary",
            to_swarm="swarm_secondary"
        )
        print(f"Logged message: {msg_id}")

        # Log context access
        ctx_id = await auditor.log_context_access(
            agent_id="haiku_worker_def456",
            session_id="session_20251130_001",
            operation=OperationType.READ,
            size_bytes=150000,
            swarm_id="swarm_secondary"
        )
        print(f"Logged context access: {ctx_id}")

        # Log decision
        dec_id = await auditor.log_decision(
            agent_id="sonnet_coordinator_abc123",
            decision_type="governance_approval",
            rationale="All constraints satisfied",
            citation="if://guardian/decision/abc123",
            swarm_id="swarm_primary"
        )
        print(f"Logged decision: {dec_id}")

        # Log security event
        sec_id = await auditor.log_security_event(
            agent_id="haiku_worker_def456",
            event_type="rate_limit_approaching",
            severity=SecuritySeverity.MEDIUM,
            details={"requests_per_minute": 45, "limit": 50},
            swarm_id="swarm_secondary"
        )
        print(f"Logged security event: {sec_id}")

        # Flush pending entries
        await auditor.flush_all()

        # Search logs
        results = await auditor.search_logs(
            {"agent_id": "sonnet_coordinator_abc123"},
            limit=10
        )
        print(f"Search results: {len(results.entries)} entries, {results.query_time_ms:.2f}ms")

        # Export
        export_path = await auditor.export_audit_trail(
            "swarm_primary",
            format="jsonl"
        )
        print(f"Exported to: {export_path}")

        # Get metrics
        metrics = await auditor.get_metrics()
        print(f"Metrics: {metrics}")

    asyncio.run(example())
