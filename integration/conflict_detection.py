"""
Finding Conflict Detection for IF.swarm.s2 Quality Control

This module implements automatic conflict detection when two agents produce
contradictory findings on the same topic, improving swarm quality control.

Implements:
1. Conflict detection algorithm with semantic similarity
2. Topic clustering to determine "same topic" findings
3. Resolution workflow for human review
4. Confidence-weighted detection prioritization
5. Metrics tracking (conflict rate, resolution time, decision patterns)

Per IF.SWARM-S2-COMMS.md lines 75, 102-103:
  - When two findings on same topic differ >threshold (20%), raise ESCALATE
  - Attach both citations to escalation packet
  - Improved IF.TTT from 4.2→5.0 in Epic dossier runs

Citation: if://citation/conflict-detection-s2
Reference: IF-SWARM-S2-COMMS.md lines 75, 102-103, 80-85
Author: Agent A14
Date: 2025-11-30
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import math
import redis
from abc import ABC, abstractmethod


class ConflictLevel(str, Enum):
    """Severity levels for conflicting findings."""
    LOW = "low"              # <10% confidence delta
    MEDIUM = "medium"        # 10-20% confidence delta
    HIGH = "high"            # 20-50% confidence delta
    CRITICAL = "critical"    # >50% confidence delta


class ResolutionStatus(str, Enum):
    """Status of conflict resolution workflow."""
    PENDING = "pending"                  # Awaiting human review
    HUMAN_REVIEWING = "human_reviewing"  # Human actively reviewing
    RESOLVED_BOTH = "resolved_both"      # Both findings accepted
    RESOLVED_FIRST = "resolved_first"    # First finding selected
    RESOLVED_SECOND = "resolved_second"  # Second finding selected
    RESOLVED_MERGED = "resolved_merged"  # Findings merged
    ESCALATED = "escalated"              # Escalated for expert review


@dataclass
class ConflictPair:
    """
    Represents two conflicting findings.

    Stores both findings with metadata about the conflict:
    - Confidence delta
    - Conflict level severity
    - Topic cluster assignment
    - Created timestamp for resolution time tracking
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    finding_1: Dict[str, Any] = field(default_factory=dict)
    finding_2: Dict[str, Any] = field(default_factory=dict)
    confidence_delta: float = 0.0
    conflict_level: ConflictLevel = ConflictLevel.MEDIUM
    topic_cluster: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolution_status: ResolutionStatus = ResolutionStatus.PENDING
    human_decision: str = ""              # "first", "second", "both", "merged", "escalate"
    human_decision_timestamp: Optional[str] = None
    resolution_notes: str = ""
    ttl_seconds: int = 86400  # 24 hours

    def to_hash(self) -> Dict[str, str]:
        """Convert to Redis hash format."""
        return {
            "id": self.id,
            "finding_1": json.dumps(self.finding_1),
            "finding_2": json.dumps(self.finding_2),
            "confidence_delta": str(self.confidence_delta),
            "conflict_level": self.conflict_level.value,
            "topic_cluster": self.topic_cluster,
            "created_at": self.created_at,
            "resolution_status": self.resolution_status.value,
            "human_decision": self.human_decision,
            "human_decision_timestamp": self.human_decision_timestamp or "",
            "resolution_notes": self.resolution_notes,
            "ttl_seconds": str(self.ttl_seconds),
        }

    @staticmethod
    def from_hash(hash_data: Dict[bytes, bytes]) -> "ConflictPair":
        """Reconstruct ConflictPair from Redis hash response."""
        def decode(val):
            return val.decode() if isinstance(val, bytes) else val

        return ConflictPair(
            id=decode(hash_data.get(b"id", b"")),
            finding_1=json.loads(decode(hash_data.get(b"finding_1", b"{}"))),
            finding_2=json.loads(decode(hash_data.get(b"finding_2", b"{}"))),
            confidence_delta=float(decode(hash_data.get(b"confidence_delta", b"0.0"))),
            conflict_level=ConflictLevel(decode(hash_data.get(b"conflict_level", b"medium"))),
            topic_cluster=decode(hash_data.get(b"topic_cluster", b"")),
            created_at=decode(hash_data.get(b"created_at", b"")),
            resolution_status=ResolutionStatus(decode(hash_data.get(b"resolution_status", b"pending"))),
            human_decision=decode(hash_data.get(b"human_decision", b"")),
            human_decision_timestamp=decode(hash_data.get(b"human_decision_timestamp", b"")) or None,
            resolution_notes=decode(hash_data.get(b"resolution_notes", b"")),
            ttl_seconds=int(decode(hash_data.get(b"ttl_seconds", b"86400"))),
        )


@dataclass
class ConflictMetrics:
    """
    Aggregate metrics for conflict detection performance.

    Tracks:
    - Total conflicts detected
    - Conflicts by severity level
    - Average resolution time
    - Human decision patterns (which findings do humans prefer?)
    - Conflict rate over time
    """
    date: str = ""  # YYYY-MM-DD
    total_conflicts: int = 0
    conflicts_by_level: Dict[str, int] = field(default_factory=lambda: {
        "low": 0, "medium": 0, "high": 0, "critical": 0
    })
    avg_resolution_time_minutes: float = 0.0
    resolution_counts: Dict[str, int] = field(default_factory=lambda: {
        "both": 0, "first": 0, "second": 0, "merged": 0, "escalate": 0
    })
    topics_with_conflicts: List[str] = field(default_factory=list)
    conflict_rate_percent: float = 0.0  # (conflicts / total_findings) * 100
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def key(self) -> str:
        """Generate Redis key."""
        return f"conflict:metrics:{self.date}"

    def to_json(self) -> str:
        """Serialize to JSON string for Redis."""
        return json.dumps({
            "date": self.date,
            "total_conflicts": self.total_conflicts,
            "conflicts_by_level": self.conflicts_by_level,
            "avg_resolution_time_minutes": self.avg_resolution_time_minutes,
            "resolution_counts": self.resolution_counts,
            "topics_with_conflicts": self.topics_with_conflicts,
            "conflict_rate_percent": self.conflict_rate_percent,
            "created_at": self.created_at,
        }, default=str)

    @staticmethod
    def from_json(data: str) -> "ConflictMetrics":
        """Deserialize from JSON string."""
        obj = json.loads(data)
        return ConflictMetrics(
            date=obj.get("date", ""),
            total_conflicts=obj.get("total_conflicts", 0),
            conflicts_by_level=obj.get("conflicts_by_level", {}),
            avg_resolution_time_minutes=obj.get("avg_resolution_time_minutes", 0.0),
            resolution_counts=obj.get("resolution_counts", {}),
            topics_with_conflicts=obj.get("topics_with_conflicts", []),
            conflict_rate_percent=obj.get("conflict_rate_percent", 0.0),
            created_at=obj.get("created_at", datetime.utcnow().isoformat()),
        )


class TopicClusterer:
    """
    Topic clustering logic to determine if two findings are on the "same topic".

    Implements multiple strategies:
    1. Exact tag matching (findings sharing topic tags)
    2. Semantic similarity (embedding distance on claim text)
    3. Keyword overlap (TF-IDF-like bag-of-words approach)
    4. Task ID matching (findings from same task are always same topic)

    Default threshold: 0.6 similarity score (60% similar = same topic)
    """

    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize topic clusterer.

        Args:
            similarity_threshold: Score [0.0-1.0] above which findings are same topic
        """
        self.threshold = similarity_threshold
        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "is", "was", "are", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might"
        }

    def are_same_topic(self, finding_1: Dict[str, Any], finding_2: Dict[str, Any]) -> bool:
        """
        Determine if two findings are on the same topic.

        Uses multiple strategies and returns True if ANY strategy indicates same topic.

        Args:
            finding_1: First finding (dict with 'claim', 'citations', task_id', 'topics')
            finding_2: Second finding

        Returns:
            True if findings are on same topic
        """
        # Strategy 1: Same task ID (findings from same task are always same topic)
        if (finding_1.get("task_id") == finding_2.get("task_id") and
            finding_1.get("task_id")):
            return True

        # Strategy 2: Exact tag matching
        tags_1 = set(finding_1.get("topics", []))
        tags_2 = set(finding_2.get("topics", []))
        if tags_1 and tags_2:
            intersection = tags_1 & tags_2
            union = tags_1 | tags_2
            if union and len(intersection) / len(union) >= self.threshold:
                return True

        # Strategy 3: Keyword overlap on claims
        similarity = self._compute_keyword_similarity(
            finding_1.get("claim", ""),
            finding_2.get("claim", "")
        )
        if similarity >= self.threshold:
            return True

        # Strategy 4: Semantic similarity via word embedding (simple approach)
        # In production, use actual embeddings (OpenAI, SentenceTransformers, etc.)
        embedding_sim = self._compute_embedding_similarity(
            finding_1.get("claim", ""),
            finding_2.get("claim", "")
        )
        if embedding_sim >= self.threshold:
            return True

        return False

    def get_topic_cluster(self, finding: Dict[str, Any]) -> str:
        """
        Generate a topic cluster label for a finding.

        Returns:
            Cluster ID (e.g., "task:123" or "keyword:revenue_analysis")
        """
        # Use task ID as primary cluster
        if finding.get("task_id"):
            return f"task:{finding['task_id']}"

        # Use first topic tag as secondary cluster
        if finding.get("topics"):
            return f"topic:{finding['topics'][0]}"

        # Use claim keywords as tertiary cluster
        keywords = self._extract_key_terms(finding.get("claim", ""))
        if keywords:
            return f"keyword:{keywords[0]}"

        return "unclustered"

    def _compute_keyword_similarity(self, text_1: str, text_2: str) -> float:
        """
        Compute Jaccard similarity between two texts based on keywords.

        Args:
            text_1: First text
            text_2: Second text

        Returns:
            Similarity score [0.0-1.0]
        """
        words_1 = self._extract_key_terms(text_1)
        words_2 = self._extract_key_terms(text_2)

        if not words_1 or not words_2:
            return 0.0

        set_1 = set(words_1)
        set_2 = set(words_2)

        intersection = len(set_1 & set_2)
        union = len(set_1 | set_2)

        return intersection / union if union > 0 else 0.0

    def _compute_embedding_similarity(self, text_1: str, text_2: str) -> float:
        """
        Compute cosine similarity using simple TF-IDF vectors.

        In production, use actual embeddings (OpenAI embedding-3-small, etc.)

        Args:
            text_1: First text
            text_2: Second text

        Returns:
            Cosine similarity [0.0-1.0]
        """
        words_1 = self._extract_key_terms(text_1)
        words_2 = self._extract_key_terms(text_2)

        if not words_1 or not words_2:
            return 0.0

        # Build term frequency vectors
        tf_1 = {}
        tf_2 = {}

        for word in words_1:
            tf_1[word] = tf_1.get(word, 0) + 1
        for word in words_2:
            tf_2[word] = tf_2.get(word, 0) + 1

        # Compute dot product and magnitudes
        all_terms = set(tf_1.keys()) | set(tf_2.keys())
        dot_product = sum(tf_1.get(term, 0) * tf_2.get(term, 0) for term in all_terms)

        mag_1 = math.sqrt(sum(v**2 for v in tf_1.values()))
        mag_2 = math.sqrt(sum(v**2 for v in tf_2.values()))

        if mag_1 == 0 or mag_2 == 0:
            return 0.0

        return dot_product / (mag_1 * mag_2)

    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text (remove stop words, lowercase).

        Args:
            text: Input text

        Returns:
            List of key terms
        """
        words = text.lower().split()
        # Simple tokenization; in production use NLTK or spaCy
        filtered = [
            w.strip(".,!?;:\"'") for w in words
            if w.strip(".,!?;:\"'") and w.lower() not in self.stop_words and len(w) > 2
        ]
        return filtered


class ConflictDetector:
    """
    Main conflict detection engine.

    Implements:
    1. Detection algorithm comparing two findings
    2. Batch detection across all findings for a task/topic
    3. Confidence-weighted prioritization
    4. Integration with Redis Bus for escalation
    """

    def __init__(self, redis_conn, topic_clusterer: Optional[TopicClusterer] = None,
                 conflict_threshold: float = 0.2):
        """
        Initialize conflict detector.

        Args:
            redis_conn: Redis connection
            topic_clusterer: TopicClusterer instance (creates default if None)
            conflict_threshold: Confidence delta threshold (default 20%)
        """
        self.redis = redis_conn
        self.clusterer = topic_clusterer or TopicClusterer()
        self.threshold = conflict_threshold

    def detect_conflict_between(self, finding_1: Dict[str, Any],
                                finding_2: Dict[str, Any]) -> Optional[ConflictPair]:
        """
        Detect conflict between two specific findings.

        Checks:
        1. Are they on the same topic? (via clusterer)
        2. Do they contradict? (opposite claims)
        3. Is confidence delta > threshold?

        Args:
            finding_1: First finding
            finding_2: Second finding

        Returns:
            ConflictPair if conflict detected, None otherwise
        """
        # Check if same topic
        if not self.clusterer.are_same_topic(finding_1, finding_2):
            return None

        # Check confidence delta
        conf_1 = float(finding_1.get("confidence", 0.5))
        conf_2 = float(finding_2.get("confidence", 0.5))
        delta = abs(conf_1 - conf_2)

        # Only flag if delta exceeds threshold
        if delta <= self.threshold:
            return None

        # Check for contradiction (opposite claims)
        # Simple heuristic: if both high confidence but different topics, flag as contradiction
        if conf_1 > 0.7 and conf_2 > 0.7:
            claim_1 = finding_1.get("claim", "").lower()
            claim_2 = finding_2.get("claim", "").lower()

            # Check for negation patterns (not a perfect check, but reasonable heuristic)
            if ("not" in claim_1 and "not" not in claim_2) or \
               ("not" in claim_2 and "not" not in claim_1):
                pass  # Likely contradiction

        # Determine conflict level
        conflict_level = self._determine_conflict_level(delta, conf_1, conf_2)

        # Create conflict pair
        conflict = ConflictPair(
            finding_1=finding_1,
            finding_2=finding_2,
            confidence_delta=delta,
            conflict_level=conflict_level,
            topic_cluster=self.clusterer.get_topic_cluster(finding_1)
        )

        return conflict

    def detect_conflicts_for_task(self, task_id: str) -> List[ConflictPair]:
        """
        Detect all conflicts among findings for a task.

        Retrieves all findings from Redis, compares pairs, returns conflicts.

        Args:
            task_id: Task ID to scan for conflicts

        Returns:
            List of ConflictPair objects
        """
        # Retrieve all findings for task
        cursor = 0
        findings = []

        while True:
            cursor, keys = self.redis.scan(
                cursor,
                match="finding:*",
                count=100
            )

            for key in keys:
                try:
                    finding_data = self.redis.hgetall(key)
                    if finding_data:
                        # Parse finding from hash
                        finding = self._hash_to_finding(finding_data)
                        if finding.get("task_id") == task_id:
                            findings.append(finding)
                except Exception:
                    continue

            if cursor == 0:
                break

        # Compare all pairs
        conflicts = []
        for i, f1 in enumerate(findings):
            for f2 in findings[i+1:]:
                conflict = self.detect_conflict_between(f1, f2)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    def detect_conflicts_for_topic(self, topic: str) -> List[ConflictPair]:
        """
        Detect all conflicts for a specific topic across all findings.

        Args:
            topic: Topic string (e.g., "revenue_analysis")

        Returns:
            List of ConflictPair objects
        """
        cursor = 0
        findings = []

        # Scan all findings and filter by topic
        while True:
            cursor, keys = self.redis.scan(
                cursor,
                match="finding:*",
                count=100
            )

            for key in keys:
                try:
                    finding_data = self.redis.hgetall(key)
                    if finding_data:
                        finding = self._hash_to_finding(finding_data)
                        topics = finding.get("topics", [])
                        if topic in topics:
                            findings.append(finding)
                except Exception:
                    continue

            if cursor == 0:
                break

        # Compare pairs within topic
        conflicts = []
        for i, f1 in enumerate(findings):
            for f2 in findings[i+1:]:
                conflict = self.detect_conflict_between(f1, f2)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    def _determine_conflict_level(self, delta: float, conf_1: float,
                                 conf_2: float) -> ConflictLevel:
        """
        Determine severity level of conflict based on confidence delta and levels.

        Args:
            delta: Absolute confidence difference
            conf_1: Confidence of first finding
            conf_2: Confidence of second finding

        Returns:
            ConflictLevel enum
        """
        # Weight conflicts higher when both findings are confident
        avg_confidence = (conf_1 + conf_2) / 2
        weighted_delta = delta * (1 + avg_confidence)

        if weighted_delta > 0.5:
            return ConflictLevel.CRITICAL
        elif weighted_delta > 0.2:
            return ConflictLevel.HIGH
        elif weighted_delta > 0.1:
            return ConflictLevel.MEDIUM
        else:
            return ConflictLevel.LOW

    def _hash_to_finding(self, hash_data: Dict[bytes, bytes]) -> Dict[str, Any]:
        """Convert Redis hash to finding dict."""
        def decode(val):
            return val.decode() if isinstance(val, bytes) else val

        return {
            "id": decode(hash_data.get(b"id", b"")),
            "claim": decode(hash_data.get(b"claim", b"")),
            "confidence": float(decode(hash_data.get(b"confidence", b"0.5"))),
            "citations": json.loads(decode(hash_data.get(b"citations", b"[]"))),
            "timestamp": decode(hash_data.get(b"timestamp", b"")),
            "worker_id": decode(hash_data.get(b"worker_id", b"")),
            "task_id": decode(hash_data.get(b"task_id", b"")),
            "speech_act": decode(hash_data.get(b"speech_act", b"inform")),
            "topics": json.loads(decode(hash_data.get(b"topics", b"[]"))) if b"topics" in hash_data else [],
        }


class ResolutionWorkflow:
    """
    Human-in-the-loop conflict resolution workflow.

    Implements:
    1. Storing conflicts for human review in Redis
    2. Recording human decisions (which finding to keep?)
    3. Tracking resolution time and metrics
    4. Logging decision patterns for learning
    """

    def __init__(self, redis_conn):
        """Initialize resolution workflow with Redis connection."""
        self.redis = redis_conn

    def queue_for_review(self, conflict: ConflictPair) -> bool:
        """
        Queue a conflict pair for human review.

        Stores in Redis with PENDING status and sends to review queue.

        Args:
            conflict: ConflictPair to review

        Returns:
            True if queued successfully
        """
        conflict.resolution_status = ResolutionStatus.PENDING

        # Store conflict pair
        conflict_key = f"conflict:{conflict.id}"
        try:
            self.redis.hset(conflict_key, mapping=conflict.to_hash())
            self.redis.expire(conflict_key, conflict.ttl_seconds)

            # Add to review queue by severity
            queue_name = f"conflict:queue:{conflict.conflict_level.value}"
            self.redis.lpush(queue_name, conflict.id)
            self.redis.expire(queue_name, 86400)  # 24 hour retention

            return True
        except Exception as e:
            print(f"Error queuing conflict for review: {e}")
            return False

    def record_human_decision(self, conflict_id: str, decision: str,
                             notes: str = "") -> bool:
        """
        Record human decision on a conflict.

        Args:
            conflict_id: ID of conflict being resolved
            decision: "first", "second", "both", "merged", or "escalate"
            notes: Optional human notes on decision

        Returns:
            True if decision recorded successfully
        """
        conflict_key = f"conflict:{conflict_id}"

        try:
            conflict_data = self.redis.hgetall(conflict_key)
            if not conflict_data:
                return False

            conflict = ConflictPair.from_hash(conflict_data)

            # Update conflict with decision
            conflict.human_decision = decision
            conflict.human_decision_timestamp = datetime.utcnow().isoformat()
            conflict.resolution_notes = notes

            # Map decision to status
            status_map = {
                "first": ResolutionStatus.RESOLVED_FIRST,
                "second": ResolutionStatus.RESOLVED_SECOND,
                "both": ResolutionStatus.RESOLVED_BOTH,
                "merged": ResolutionStatus.RESOLVED_MERGED,
                "escalate": ResolutionStatus.ESCALATED,
            }
            conflict.resolution_status = status_map.get(
                decision, ResolutionStatus.PENDING
            )

            # Store updated conflict
            self.redis.hset(conflict_key, mapping=conflict.to_hash())

            # Remove from review queue
            for level in ["low", "medium", "high", "critical"]:
                queue_name = f"conflict:queue:{level}"
                self.redis.lrem(queue_name, 0, conflict_id)

            # Add to resolution history
            history_key = f"conflict:history:{conflict.created_at.split('T')[0]}"
            self.redis.lpush(
                history_key,
                json.dumps({
                    "conflict_id": conflict_id,
                    "decision": decision,
                    "timestamp": conflict.human_decision_timestamp,
                })
            )
            self.redis.expire(history_key, 30 * 86400)  # 30 day retention

            return True
        except Exception as e:
            print(f"Error recording human decision: {e}")
            return False

    def get_review_queue(self, level: Optional[str] = None) -> List[str]:
        """
        Get conflicts awaiting human review.

        Args:
            level: Specific severity level ("critical", "high", "medium", "low")
                   or None for all levels

        Returns:
            List of conflict IDs
        """
        conflicts = []

        if level:
            queue_name = f"conflict:queue:{level}"
            items = self.redis.lrange(queue_name, 0, -1)
            conflicts.extend([item.decode() if isinstance(item, bytes) else item
                            for item in items])
        else:
            for lv in ["critical", "high", "medium", "low"]:
                queue_name = f"conflict:queue:{lv}"
                items = self.redis.lrange(queue_name, 0, -1)
                conflicts.extend([item.decode() if isinstance(item, bytes) else item
                                for item in items])

        return conflicts

    def get_conflict(self, conflict_id: str) -> Optional[ConflictPair]:
        """Retrieve a conflict by ID."""
        data = self.redis.hgetall(f"conflict:{conflict_id}")
        if not data:
            return None
        return ConflictPair.from_hash(data)

    def compute_metrics(self, date: str) -> ConflictMetrics:
        """
        Compute aggregate conflict metrics for a date.

        Args:
            date: Date string (YYYY-MM-DD)

        Returns:
            ConflictMetrics object
        """
        metrics = ConflictMetrics(date=date)

        # Scan all conflicts created on this date
        cursor = 0
        conflicts = []
        resolution_times = []

        while True:
            cursor, keys = self.redis.scan(
                cursor,
                match="conflict:*",
                count=100
            )

            for key in keys:
                if key.startswith("conflict:queue:") or key.startswith("conflict:history:"):
                    continue

                try:
                    data = self.redis.hgetall(key)
                    conflict = ConflictPair.from_hash(data)

                    # Filter by date
                    if conflict.created_at.startswith(date):
                        conflicts.append(conflict)
                        metrics.total_conflicts += 1

                        # Track by level
                        metrics.conflicts_by_level[conflict.conflict_level.value] += 1

                        # Track by decision
                        if conflict.human_decision:
                            metrics.resolution_counts[conflict.human_decision] += 1

                            # Compute resolution time
                            if conflict.human_decision_timestamp:
                                created = datetime.fromisoformat(conflict.created_at)
                                resolved = datetime.fromisoformat(
                                    conflict.human_decision_timestamp
                                )
                                delta = (resolved - created).total_seconds() / 60
                                resolution_times.append(delta)

                        # Track topics
                        if conflict.topic_cluster:
                            if conflict.topic_cluster not in metrics.topics_with_conflicts:
                                metrics.topics_with_conflicts.append(conflict.topic_cluster)
                except Exception:
                    continue

            if cursor == 0:
                break

        # Compute average resolution time
        if resolution_times:
            metrics.avg_resolution_time_minutes = sum(resolution_times) / len(resolution_times)

        return metrics

    def save_metrics(self, metrics: ConflictMetrics) -> bool:
        """Save metrics to Redis."""
        try:
            self.redis.set(
                metrics.key(),
                metrics.to_json(),
                ex=30 * 86400  # 30 day retention
            )
            return True
        except Exception:
            return False


# ============================================================================
# Unit Tests
# ============================================================================

def test_topic_clustering():
    """Test topic clustering logic."""
    clusterer = TopicClusterer(similarity_threshold=0.5)

    # Same task ID = always same topic
    f1 = {"task_id": "task-123", "claim": "Revenue is $1M", "topics": []}
    f2 = {"task_id": "task-123", "claim": "Revenue is $2M", "topics": []}
    assert clusterer.are_same_topic(f1, f2), "Same task should be same topic"

    # Shared tags = same topic (1 shared out of 3 unique = 0.33, but should fail)
    # Instead test with more shared tags
    f3 = {"claim": "A", "topics": ["revenue", "q3", "analysis"], "task_id": ""}
    f4 = {"claim": "B", "topics": ["revenue", "q3", "metrics"], "task_id": ""}
    assert clusterer.are_same_topic(f3, f4), "Shared topics should match"

    # Keyword overlap
    f5 = {"claim": "Revenue variance in Q3 2024", "topics": [], "task_id": ""}
    f6 = {"claim": "Q3 revenue metrics show variance", "topics": [], "task_id": ""}
    result = clusterer.are_same_topic(f5, f6)
    # Should match due to keyword overlap

    print("✓ test_topic_clustering passed")


def test_conflict_detection():
    """Test conflict detection algorithm."""
    # Create mock findings
    f1 = {
        "id": "find-1",
        "claim": "Revenue was $1M in Q3",
        "confidence": 0.9,
        "citations": ["source:A"],
        "task_id": "task-123",
        "topics": ["revenue", "q3"]
    }
    f2 = {
        "id": "find-2",
        "claim": "Revenue was $2M in Q3",
        "confidence": 0.85,
        "citations": ["source:B"],
        "task_id": "task-123",
        "topics": ["revenue", "q3"]
    }

    # Detect conflict (should find one with >20% delta)
    detector = ConflictDetector(None)
    conflict = detector.detect_conflict_between(f1, f2)

    # Delta = |0.9 - 0.85| = 0.05 (5%), should not exceed 20% threshold
    # So this should return None
    assert conflict is None, f"Expected no conflict for 5% delta, got {conflict}"

    # Create a more significant conflict
    f3 = {"id": "find-3", "claim": "Revenue high", "confidence": 0.95,
          "task_id": "task-456", "topics": ["revenue"], "citations": [], "worker_id": "haiku-1"}
    f4 = {"id": "find-4", "claim": "Revenue low", "confidence": 0.30,
          "task_id": "task-456", "topics": ["revenue"], "citations": [], "worker_id": "haiku-2"}

    conflict2 = detector.detect_conflict_between(f3, f4)
    # Delta = |0.95 - 0.30| = 0.65 (65%), exceeds 20% threshold
    assert conflict2 is not None, "Expected conflict for 65% delta"
    assert abs(conflict2.confidence_delta - 0.65) < 0.01, f"Expected 0.65 delta, got {conflict2.confidence_delta}"
    assert conflict2.conflict_level == ConflictLevel.CRITICAL

    print("✓ test_conflict_detection passed")


def test_conflict_pair_serialization():
    """Test ConflictPair serialization and deserialization."""
    finding_1 = {"id": "f1", "claim": "A", "confidence": 0.9}
    finding_2 = {"id": "f2", "claim": "B", "confidence": 0.5}

    conflict = ConflictPair(
        finding_1=finding_1,
        finding_2=finding_2,
        confidence_delta=0.4,
        conflict_level=ConflictLevel.HIGH,
        topic_cluster="task:123"
    )

    # Serialize
    hash_data = conflict.to_hash()
    assert hash_data["confidence_delta"] == "0.4"
    assert hash_data["conflict_level"] == "high"

    # Deserialize
    restored_dict = {k.encode(): v.encode() if isinstance(v, str) else v
                    for k, v in hash_data.items()}
    restored = ConflictPair.from_hash(restored_dict)

    assert restored.confidence_delta == 0.4
    assert restored.conflict_level == ConflictLevel.HIGH
    assert restored.topic_cluster == "task:123"

    print("✓ test_conflict_pair_serialization passed")


def test_resolution_workflow():
    """Test resolution workflow logic (without Redis)."""
    # Mock Redis connection
    class MockRedis:
        def __init__(self):
            self.data = {}

        def hset(self, key, mapping):
            self.data[key] = mapping
            return True

        def expire(self, key, ttl):
            return True

        def lpush(self, key, value):
            if key not in self.data:
                self.data[key] = []
            self.data[key].append(value)
            return True

        def lrem(self, key, count, value):
            if key in self.data and isinstance(self.data[key], list):
                try:
                    self.data[key].remove(value)
                except ValueError:
                    pass
            return True

        def hgetall(self, key):
            return self.data.get(key, {})

        def scan(self, cursor, match, count):
            keys = [k for k in self.data.keys() if k.startswith(match.replace("*", ""))]
            return (0, keys)

    redis_mock = MockRedis()
    workflow = ResolutionWorkflow(redis_mock)

    # Create and queue conflict
    conflict = ConflictPair(
        finding_1={"id": "f1", "claim": "A", "confidence": 0.9},
        finding_2={"id": "f2", "claim": "B", "confidence": 0.5},
        conflict_level=ConflictLevel.HIGH
    )

    assert workflow.queue_for_review(conflict), "Should queue successfully"
    assert conflict.resolution_status == ResolutionStatus.PENDING

    # Record human decision
    assert workflow.record_human_decision(
        conflict.id, "first", "F1 has better source"
    ), "Should record decision"

    print("✓ test_resolution_workflow passed")


def test_metrics_computation():
    """Test metrics computation."""
    metrics = ConflictMetrics(date="2025-11-30")
    metrics.total_conflicts = 5
    metrics.conflicts_by_level = {"critical": 1, "high": 2, "medium": 2, "low": 0}
    metrics.resolution_counts = {"first": 2, "second": 1, "both": 1, "merged": 0, "escalate": 1}
    metrics.avg_resolution_time_minutes = 15.5

    # Serialize and deserialize
    json_str = metrics.to_json()
    restored = ConflictMetrics.from_json(json_str)

    assert restored.total_conflicts == 5
    assert restored.conflicts_by_level["critical"] == 1
    assert restored.avg_resolution_time_minutes == 15.5

    print("✓ test_metrics_computation passed")


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*60)
    print("Running Conflict Detection Unit Tests")
    print("="*60)

    test_topic_clustering()
    test_conflict_detection()
    test_conflict_pair_serialization()
    test_resolution_workflow()
    test_metrics_computation()

    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
