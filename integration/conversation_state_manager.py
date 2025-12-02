#!/usr/bin/env python3
"""
IF.emotion Conversation State Persistence Manager
==================================================

Manages IF.emotion conversation state across browser refreshes, model switches,
and session handovers using Redis L2 (Context Memory) with ChromaDB archival.

Features:
- Session initialization and resumption
- Atomic emotional state updates
- Incremental message appending (ring buffer)
- Milestone and breakthrough recording
- Markdown export for therapist collaboration
- IF.TTT traceability for all state changes

Reference: /home/setup/infrafabric/integration/conversation_state_persistence.md
"""

import redis
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# EMOTIONAL STATE ENUMERATION
# ============================================================================

class EmotionalState(Enum):
    """Valid emotional states for IF.emotion conversations."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    FRUSTRATED = "frustrated"
    ANXIOUS = "anxious"
    BREAKTHROUGH = "breakthrough"
    INTEGRATED = "integrated"
    EXPLORING = "exploring"
    RESISTANT = "resistant"


class TherapeuticCategory(Enum):
    """Therapeutic categories for breakthrough moments."""
    REFRAME = "reframe"
    INTEGRATION = "integration"
    INSIGHT = "insight"
    ACCEPTANCE = "acceptance"
    PATTERN_RECOGNITION = "pattern_recognition"
    RESOLUTION = "resolution"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Message:
    """Conversation message object."""
    role: str  # "user" or "assistant"
    content: str
    model_id: str
    tokens: int
    emotion_context: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    parent_message_id: Optional[str] = None
    is_milestone: bool = False
    is_breakthrough_trigger: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class Milestone:
    """Significant milestone in conversation journey."""
    description: str
    emotion_state: str
    model_id: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    message_count: int = 0
    tracking_id: str = field(default_factory=lambda: f"if://citation/{uuid.uuid4()}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class Breakthrough:
    """Breakthrough moment (insight, realization, pattern recognition)."""
    insight: str
    trigger_message_id: str
    therapeutic_category: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 0.8
    tracking_id: str = field(default_factory=lambda: f"if://citation/{uuid.uuid4()}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class SessionMetadata:
    """Session metadata for resumption and recovery."""
    user_id: str
    session_id: str
    conversation_id: str
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_model: str = "claude-haiku-4-5-20250929"
    last_resumed: Optional[str] = None
    milestone_count: int = 0
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# CONVERSATION STATE MANAGER
# ============================================================================

class ConversationStateManager:
    """
    Manages IF.emotion conversation state persistence.

    Redis Key Schema:
    - session:{user_id}:{session_id}:metadata              (HASH)
    - session:{user_id}:{session_id}:emotion               (HASH)
    - session:{user_id}:{session_id}:messages              (LIST, ring buffer)
    - session:{user_id}:{session_id}:milestones            (ZSET, timestamp score)
    - session:{user_id}:{session_id}:breakthroughs         (ZSET, confidence score)
    - session:{user_id}:{session_id}:context_snapshot      (HASH)
    - sessions:user:{user_id}:index                        (SET)
    - sessions:global:active                               (SET)
    """

    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 redis_db: int = 0, ttl_days: int = 7):
        """
        Initialize conversation state manager.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            ttl_days: Time-to-live for session state (days)
        """
        try:
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            self.redis.ping()
            logger.info(f"Connected to Redis: {redis_host}:{redis_port}/{redis_db}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

        self.ttl = ttl_days * 86400  # Convert days to seconds
        self.max_message_window = 100
        logger.info(f"ConversationStateManager initialized (TTL: {ttl_days} days)")

    # ========================================================================
    # SESSION LIFECYCLE
    # ========================================================================

    def initialize_session(self, user_id: str) -> Tuple[str, str]:
        """
        Create new conversation session.

        Args:
            user_id: Unique user identifier

        Returns:
            Tuple of (session_id, conversation_id)
        """
        session_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        pipe = self.redis.pipeline()

        # Create session metadata
        metadata = SessionMetadata(
            user_id=user_id,
            session_id=session_id,
            conversation_id=conversation_id,
            started_at=now,
            last_updated=now
        )
        pipe.hset(f"session:{user_id}:{session_id}:metadata",
                  mapping=asdict(metadata))
        pipe.expire(f"session:{user_id}:{session_id}:metadata", self.ttl)

        # Initialize emotional state
        pipe.hset(f"session:{user_id}:{session_id}:emotion", mapping={
            'current_emotion': EmotionalState.NEUTRAL.value,
            'emotion_intensity': '0.0',
            'emotion_confidence': '0.5',
            'last_emotion_change': now,
            'emotion_tracking_id': f'if://citation/{uuid.uuid4()}'
        })
        pipe.expire(f"session:{user_id}:{session_id}:emotion", self.ttl)

        # Initialize context snapshot
        pipe.hset(f"session:{user_id}:{session_id}:context_snapshot", mapping={
            'current_theme': 'session_initialization',
            'therapeutic_focus': 'unknown',
            'client_state_summary': 'beginning session',
            'session_notes': 'session started',
            'last_summarized': now
        })
        pipe.expire(f"session:{user_id}:{session_id}:context_snapshot", self.ttl)

        # Register in indices
        pipe.sadd(f"sessions:user:{user_id}:index", session_id)
        pipe.sadd("sessions:global:active", f"{user_id}:{session_id}")

        pipe.execute()
        logger.info(f"Session initialized: {session_id}")
        return session_id, conversation_id

    def resume_session(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Resume conversation from persistent state.

        Args:
            user_id: Unique user identifier
            session_id: Session to resume

        Returns:
            Dictionary with full session state for UI rehydration

        Raises:
            ValueError: Session not found or expired
        """
        metadata_key = f"session:{user_id}:{session_id}:metadata"
        metadata = self.redis.hgetall(metadata_key)

        if not metadata:
            raise ValueError(f"Session {session_id} not found or expired")

        # Update resumption metadata
        now = datetime.utcnow().isoformat()
        pipe = self.redis.pipeline()
        pipe.hset(metadata_key, mapping={
            'last_resumed': now,
            'last_updated': now
        })

        # Refresh TTLs (keep session alive)
        for key in [f"session:{user_id}:{session_id}:metadata",
                    f"session:{user_id}:{session_id}:messages",
                    f"session:{user_id}:{session_id}:emotion",
                    f"session:{user_id}:{session_id}:milestones",
                    f"session:{user_id}:{session_id}:breakthroughs",
                    f"session:{user_id}:{session_id}:context_snapshot"]:
            pipe.expire(key, self.ttl)

        pipe.execute()

        # Fetch current state
        recent_messages = self.redis.lrange(
            f"session:{user_id}:{session_id}:messages", -20, -1)
        milestones = self.redis.zrange(
            f"session:{user_id}:{session_id}:milestones", -5, -1)
        last_breakthrough = self.redis.zrange(
            f"session:{user_id}:{session_id}:breakthroughs", -1, -1)

        logger.info(f"Session resumed: {session_id}")
        return {
            'session_metadata': metadata,
            'emotional_state': self.redis.hgetall(
                f"session:{user_id}:{session_id}:emotion"),
            'recent_messages': [Message.from_json(m) for m in recent_messages if m],
            'recent_milestones': [json.loads(m) for m in milestones if m],
            'last_breakthrough': [json.loads(b) for b in last_breakthrough if b]
        }

    def close_session(self, user_id: str, session_id: str) -> bool:
        """
        Close a session (optional archival before deletion).

        Args:
            user_id: Unique user identifier
            session_id: Session to close

        Returns:
            True if successfully closed
        """
        pipe = self.redis.pipeline()
        pipe.srem(f"sessions:user:{user_id}:index", session_id)
        pipe.srem("sessions:global:active", f"{user_id}:{session_id}")
        pipe.execute()

        logger.info(f"Session closed: {session_id}")
        return True

    # ========================================================================
    # MESSAGE HANDLING
    # ========================================================================

    def append_message(self, user_id: str, session_id: str,
                      message: Message,
                      update_emotion: Optional[Dict[str, Any]] = None,
                      is_breakthrough: bool = False) -> str:
        """
        Append message to conversation history (ring buffer pattern).

        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            message: Message object to append
            update_emotion: Optional emotion state update
            is_breakthrough: Whether this is a breakthrough trigger

        Returns:
            Message ID
        """
        now = datetime.utcnow()
        message.message_id = str(uuid.uuid4())
        message.timestamp = now.isoformat()

        pipe = self.redis.pipeline()

        # Append to message history (ring buffer)
        msg_key = f"session:{user_id}:{session_id}:messages"
        pipe.rpush(msg_key, message.to_json())
        pipe.ltrim(msg_key, -self.max_message_window, -1)  # Keep last N
        pipe.expire(msg_key, self.ttl)

        # Update metadata timestamp
        pipe.hset(f"session:{user_id}:{session_id}:metadata",
                  mapping={'last_updated': now.isoformat()})

        # Update emotion if provided
        if update_emotion:
            pipe.hset(f"session:{user_id}:{session_id}:emotion", mapping={
                'current_emotion': update_emotion['emotion'],
                'emotion_intensity': str(update_emotion['intensity']),
                'emotion_confidence': str(update_emotion['confidence']),
                'last_emotion_change': now.isoformat(),
                'emotion_tracking_id': f'if://citation/{uuid.uuid4()}'
            })

        # Record breakthrough if applicable
        if is_breakthrough and 'breakthrough_insight' in update_emotion or {}:
            breakthrough = Breakthrough(
                insight=update_emotion.get('breakthrough_insight', message.content[:200]),
                trigger_message_id=message.message_id,
                therapeutic_category=update_emotion.get('category', 'insight'),
                confidence=update_emotion.get('confidence', 0.85)
            )
            score = breakthrough.confidence * now.timestamp()
            pipe.zadd(f"session:{user_id}:{session_id}:breakthroughs",
                      {breakthrough.to_json(): score})

        pipe.execute()
        logger.info(f"Message appended: {message.message_id}")
        return message.message_id

    def get_message_history(self, user_id: str, session_id: str,
                           limit: int = 50) -> List[Message]:
        """
        Retrieve message history (most recent N messages).

        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            limit: Number of recent messages to retrieve

        Returns:
            List of Message objects
        """
        messages_json = self.redis.lrange(
            f"session:{user_id}:{session_id}:messages", -limit, -1)
        return [Message.from_json(m) for m in messages_json if m]

    # ========================================================================
    # EMOTIONAL STATE MANAGEMENT
    # ========================================================================

    def update_emotion(self, user_id: str, session_id: str,
                      emotion: EmotionalState, intensity: float = 0.5,
                      confidence: float = 0.7) -> str:
        """
        Atomically update emotional state.

        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            emotion: EmotionalState enum value
            intensity: Intensity of emotion (0.0-1.0)
            confidence: Confidence in emotion assessment (0.0-1.0)

        Returns:
            Tracking ID for IF.TTT citation
        """
        now = datetime.utcnow().isoformat()
        tracking_id = f'if://citation/{uuid.uuid4()}'

        if not 0.0 <= intensity <= 1.0:
            raise ValueError(f"Intensity must be 0.0-1.0, got {intensity}")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")

        pipe = self.redis.pipeline()
        pipe.hset(f"session:{user_id}:{session_id}:emotion", mapping={
            'current_emotion': emotion.value,
            'emotion_intensity': str(intensity),
            'emotion_confidence': str(confidence),
            'last_emotion_change': now,
            'emotion_tracking_id': tracking_id
        })
        pipe.expire(f"session:{user_id}:{session_id}:emotion", self.ttl)
        pipe.execute()

        logger.info(f"Emotion updated: {emotion.value} ({intensity}, {confidence})")
        return tracking_id

    def get_emotion_state(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Retrieve current emotional state.

        Args:
            user_id: Unique user identifier
            session_id: Session identifier

        Returns:
            Dictionary with emotional state
        """
        return self.redis.hgetall(f"session:{user_id}:{session_id}:emotion")

    # ========================================================================
    # JOURNEY TRACKING (MILESTONES & BREAKTHROUGHS)
    # ========================================================================

    def record_milestone(self, user_id: str, session_id: str,
                        description: str, emotion_state: str,
                        model_id: str) -> str:
        """
        Record significant milestone in conversation.

        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            description: Description of milestone
            emotion_state: Emotional state at milestone
            model_id: Which model was active

        Returns:
            Milestone tracking ID
        """
        msg_count = self.redis.llen(f"session:{user_id}:{session_id}:messages") or 0
        milestone = Milestone(
            description=description,
            emotion_state=emotion_state,
            model_id=model_id,
            message_count=msg_count
        )

        pipe = self.redis.pipeline()
        score = datetime.utcnow().timestamp()
        pipe.zadd(f"session:{user_id}:{session_id}:milestones",
                  {milestone.to_json(): score})
        pipe.hincrby(f"session:{user_id}:{session_id}:metadata",
                     "milestone_count", 1)
        pipe.expire(f"session:{user_id}:{session_id}:milestones", self.ttl)
        pipe.execute()

        logger.info(f"Milestone recorded: {description}")
        return milestone.tracking_id

    def record_breakthrough(self, user_id: str, session_id: str,
                           insight: str, trigger_message_id: str,
                           category: str = "insight",
                           confidence: float = 0.85) -> str:
        """
        Record breakthrough moment (insight, pattern recognition, etc.).

        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            insight: Description of the insight
            trigger_message_id: Message that triggered breakthrough
            category: TherapeuticCategory value
            confidence: Confidence in breakthrough significance (0.0-1.0)

        Returns:
            Breakthrough tracking ID
        """
        breakthrough = Breakthrough(
            insight=insight,
            trigger_message_id=trigger_message_id,
            therapeutic_category=category,
            confidence=confidence
        )

        pipe = self.redis.pipeline()
        # Score by confidence * timestamp for relevance sorting
        score = confidence * datetime.utcnow().timestamp()
        pipe.zadd(f"session:{user_id}:{session_id}:breakthroughs",
                  {breakthrough.to_json(): score})
        pipe.expire(f"session:{user_id}:{session_id}:breakthroughs", self.ttl)
        pipe.execute()

        logger.info(f"Breakthrough recorded: {insight[:50]}...")
        return breakthrough.tracking_id

    def get_journey_summary(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get summary of conversation journey.

        Args:
            user_id: Unique user identifier
            session_id: Session identifier

        Returns:
            Dictionary with journey summary
        """
        metadata = self.redis.hgetall(f"session:{user_id}:{session_id}:metadata")
        milestones = self.redis.zrange(f"session:{user_id}:{session_id}:milestones", 0, -1)
        breakthroughs = self.redis.zrange(f"session:{user_id}:{session_id}:breakthroughs", 0, -1)

        return {
            'total_duration_minutes': self._calculate_duration(metadata),
            'milestone_count': len(milestones),
            'breakthrough_count': len(breakthroughs),
            'milestones': [json.loads(m) for m in milestones if m],
            'breakthroughs': [json.loads(b) for b in breakthroughs if b]
        }

    # ========================================================================
    # CONTEXT & SNAPSHOTS
    # ========================================================================

    def update_context_snapshot(self, user_id: str, session_id: str,
                               current_theme: str = None,
                               therapeutic_focus: str = None,
                               client_state_summary: str = None,
                               session_notes: str = None) -> bool:
        """
        Update context snapshot (working notes and understanding).

        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            current_theme: What we're currently exploring
            therapeutic_focus: Type of therapeutic work (existential, somatic, etc.)
            client_state_summary: Current understanding of client
            session_notes: Working notes and hypotheses

        Returns:
            True if successful
        """
        now = datetime.utcnow().isoformat()
        updates = {'last_summarized': now}

        if current_theme:
            updates['current_theme'] = current_theme
        if therapeutic_focus:
            updates['therapeutic_focus'] = therapeutic_focus
        if client_state_summary:
            updates['client_state_summary'] = client_state_summary
        if session_notes:
            updates['session_notes'] = session_notes

        pipe = self.redis.pipeline()
        pipe.hset(f"session:{user_id}:{session_id}:context_snapshot",
                  mapping=updates)
        pipe.expire(f"session:{user_id}:{session_id}:context_snapshot", self.ttl)
        pipe.execute()

        return True

    def get_context_snapshot(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Retrieve context snapshot.

        Args:
            user_id: Unique user identifier
            session_id: Session identifier

        Returns:
            Dictionary with context information
        """
        return self.redis.hgetall(f"session:{user_id}:{session_id}:context_snapshot")

    # ========================================================================
    # EXPORT FUNCTIONALITY
    # ========================================================================

    def export_markdown(self, user_id: str, session_id: str,
                       include_transcript: bool = True) -> Tuple[str, str]:
        """
        Generate Markdown export for therapist collaboration.

        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            include_transcript: Whether to include full message transcript

        Returns:
            Tuple of (markdown_content, export_id)
        """
        # Fetch all session data
        metadata = self.redis.hgetall(f"session:{user_id}:{session_id}:metadata")
        emotion = self.redis.hgetall(f"session:{user_id}:{session_id}:emotion")
        messages = self.redis.lrange(f"session:{user_id}:{session_id}:messages", 0, -1)
        milestones = self.redis.zrange(f"session:{user_id}:{session_id}:milestones", 0, -1)
        breakthroughs = self.redis.zrange(f"session:{user_id}:{session_id}:breakthroughs", 0, -1)
        context = self.redis.hgetall(f"session:{user_id}:{session_id}:context_snapshot")

        # Parse data
        parsed_messages = [Message.from_json(m) for m in messages if m]
        parsed_milestones = [json.loads(m) for m in milestones if m]
        parsed_breakthroughs = [json.loads(b) for b in breakthroughs if b]

        # Build metadata
        export_id = str(uuid.uuid4())
        export_timestamp = datetime.utcnow().isoformat()
        started_at = datetime.fromisoformat(metadata.get('started_at', ''))
        last_updated = datetime.fromisoformat(metadata.get('last_updated', ''))
        duration_minutes = (last_updated - started_at).total_seconds() / 60

        # Build markdown
        markdown = f"""# IF.emotion Conversation Export

**Session ID:** {session_id}
**Export Date:** {export_timestamp}
**Citation:** if://export/{session_id}/{export_id}

---

## Session Overview

| Metric | Value |
|--------|-------|
| Duration | {duration_minutes:.1f} minutes |
| Started | {metadata.get('started_at')} |
| Last Updated | {metadata.get('last_updated')} |
| Total Messages | {len(parsed_messages)} |
| Milestones | {len(parsed_milestones)} |
| Breakthroughs | {len(parsed_breakthroughs)} |

---

## Current Emotional State

**Emotion:** {emotion.get('current_emotion')}
**Intensity:** {emotion.get('emotion_intensity')}/10
**Confidence:** {emotion.get('emotion_confidence')}
**Last Change:** {emotion.get('last_emotion_change')}

---

## Key Milestones

"""

        for milestone in parsed_milestones:
            markdown += f"- **{milestone['timestamp']}** {milestone['description']}\n"
            markdown += f"  - Emotion: {milestone['emotion_state']}\n"
            markdown += f"  - Citation: {milestone['tracking_id']}\n\n"

        markdown += "\n## Breakthroughs\n\n"

        for breakthrough in parsed_breakthroughs:
            markdown += f"- **{breakthrough['timestamp']}** {breakthrough['insight']}\n"
            markdown += f"  - Category: {breakthrough['therapeutic_category']}\n"
            markdown += f"  - Confidence: {breakthrough['confidence']}\n"
            markdown += f"  - Citation: {breakthrough['tracking_id']}\n\n"

        if include_transcript:
            markdown += "\n## Conversation Transcript (Last 50 Messages)\n\n"
            for msg in parsed_messages[-50:]:
                role = "User" if msg.role == 'user' else "IF.emotion"
                markdown += f"**[{msg.timestamp}] {role}:**\n{msg.content}\n\n"

        markdown += f"\n## Therapeutic Context\n\n"
        markdown += f"- **Current Theme:** {context.get('current_theme')}\n"
        markdown += f"- **Focus:** {context.get('therapeutic_focus')}\n"
        markdown += f"- **Client State:** {context.get('client_state_summary')}\n"
        markdown += f"- **Notes:** {context.get('session_notes')}\n"

        markdown += f"\n---\n\nExported from IF.emotion by InfraFabric\n"

        return markdown, export_id

    def export_json(self, user_id: str, session_id: str) -> Tuple[Dict[str, Any], str]:
        """
        Export full session state as JSON.

        Args:
            user_id: Unique user identifier
            session_id: Session identifier

        Returns:
            Tuple of (json_data, export_id)
        """
        export_id = str(uuid.uuid4())
        export_timestamp = datetime.utcnow().isoformat()

        # Fetch all data
        metadata = self.redis.hgetall(f"session:{user_id}:{session_id}:metadata")
        emotion = self.redis.hgetall(f"session:{user_id}:{session_id}:emotion")
        messages = self.redis.lrange(f"session:{user_id}:{session_id}:messages", 0, -1)
        milestones = self.redis.zrange(f"session:{user_id}:{session_id}:milestones", 0, -1)
        breakthroughs = self.redis.zrange(f"session:{user_id}:{session_id}:breakthroughs", 0, -1)
        context = self.redis.hgetall(f"session:{user_id}:{session_id}:context_snapshot")

        return {
            'export_id': export_id,
            'export_timestamp': export_timestamp,
            'session_metadata': metadata,
            'emotional_state': emotion,
            'messages': [Message.from_json(m).to_dict() for m in messages if m],
            'milestones': [json.loads(m) for m in milestones if m],
            'breakthroughs': [json.loads(b) for b in breakthroughs if b],
            'context_snapshot': context
        }, export_id

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all active sessions for a user."""
        return list(self.redis.smembers(f"sessions:user:{user_id}:index"))

    def get_session_stats(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session."""
        metadata = self.redis.hgetall(f"session:{user_id}:{session_id}:metadata")
        msg_count = self.redis.llen(f"session:{user_id}:{session_id}:messages") or 0
        milestone_count = self.redis.zcard(f"session:{user_id}:{session_id}:milestones") or 0
        breakthrough_count = self.redis.zcard(f"session:{user_id}:{session_id}:breakthroughs") or 0

        return {
            'session_id': session_id,
            'started_at': metadata.get('started_at'),
            'message_count': msg_count,
            'milestone_count': milestone_count,
            'breakthrough_count': breakthrough_count,
            'ttl_seconds': self.redis.ttl(f"session:{user_id}:{session_id}:metadata")
        }

    def _calculate_duration(self, metadata: Dict[str, Any]) -> float:
        """Calculate session duration in minutes."""
        try:
            started = datetime.fromisoformat(metadata.get('started_at', ''))
            updated = datetime.fromisoformat(metadata.get('last_updated', ''))
            return (updated - started).total_seconds() / 60
        except (ValueError, TypeError):
            return 0.0

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from indices.

        Returns:
            Number of sessions cleaned
        """
        active_sessions = self.redis.smembers("sessions:global:active")
        cleaned = 0

        for session_str in active_sessions:
            user_id, session_id = session_str.split(':')
            metadata_key = f"session:{user_id}:{session_id}:metadata"

            if not self.redis.exists(metadata_key):
                self.redis.srem("sessions:global:active", session_str)
                self.redis.srem(f"sessions:user:{user_id}:index", session_id)
                cleaned += 1

        logger.info(f"Cleaned up {cleaned} expired sessions")
        return cleaned


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Initialize manager
    manager = ConversationStateManager()

    # Create session
    user_id = str(uuid.uuid4())
    session_id, conv_id = manager.initialize_session(user_id)
    print(f"Created session: {session_id}")

    # Add message from user
    user_msg = Message(
        role='user',
        content='I have been struggling with my sense of identity lately',
        model_id='claude-haiku-4-5-20250929',
        tokens=15,
        emotion_context='anxious'
    )
    msg_id = manager.append_message(user_id, session_id, user_msg)
    print(f"Appended user message: {msg_id}")

    # Add assistant response and update emotion
    assistant_msg = Message(
        role='assistant',
        content='Identity questions are deeply important. Let us explore what aspects feel uncertain to you.',
        model_id='claude-haiku-4-5-20250929',
        tokens=20,
        emotion_context='exploring'
    )
    emotion_update = {
        'emotion': EmotionalState.EXPLORING.value,
        'intensity': 0.6,
        'confidence': 0.8
    }
    manager.append_message(user_id, session_id, assistant_msg, update_emotion=emotion_update)
    print(f"Appended assistant response")

    # Record milestone
    milestone_id = manager.record_milestone(
        user_id, session_id,
        "Client identified core identity question",
        EmotionalState.EXPLORING.value,
        "claude-haiku-4-5-20250929"
    )
    print(f"Milestone recorded: {milestone_id}")

    # Record breakthrough
    breakthrough_id = manager.record_breakthrough(
        user_id, session_id,
        "Realized identity shifts contextually based on relationships",
        msg_id,
        category=TherapeuticCategory.INSIGHT.value,
        confidence=0.9
    )
    print(f"Breakthrough recorded: {breakthrough_id}")

    # Update emotion to breakthrough
    manager.update_emotion(user_id, session_id, EmotionalState.BREAKTHROUGH, 0.8, 0.95)
    print(f"Emotion updated to breakthrough")

    # Get journey summary
    summary = manager.get_journey_summary(user_id, session_id)
    print(f"Journey summary: {summary['milestone_count']} milestones, "
          f"{summary['breakthrough_count']} breakthroughs")

    # Get session stats
    stats = manager.get_session_stats(user_id, session_id)
    print(f"Session stats: {stats}")

    # Export markdown
    markdown, export_id = manager.export_markdown(user_id, session_id)
    print(f"Export generated: {export_id}")
    print(f"Markdown length: {len(markdown)} characters")

    # Resume session
    state = manager.resume_session(user_id, session_id)
    print(f"Session resumed successfully")

    print("\nAll operations completed successfully!")
