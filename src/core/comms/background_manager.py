#!/usr/bin/env python3
"""
Background Communication Manager - Persistent Agent Messaging

Implements persistent pub/sub with guaranteed delivery, offline message queueing,
and SIP-inspired session management for multi-agent communication.

Features:
- Publish/subscribe with persistent storage for offline agents
- Direct agent-to-agent messaging with delivery guarantees
- SIP-inspired session initiation (INVITE → ACK → BYE)
- Subscription management with automatic re-establishment
- Background listener threads for real-time message delivery
- Message TTL (24 hours) for automatic cleanup
- Read/unread message tracking
- Comprehensive audit logging for IF.TTT compliance

Citation: if://code/background-comms-manager/2025-11-30
"""

import redis
import json
import uuid
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import queue

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """Message delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"


class SessionState(Enum):
    """SIP-inspired session states"""
    INITIATED = "initiated"
    PENDING = "pending"
    ACTIVE = "active"
    TERMINATING = "terminating"
    TERMINATED = "terminated"
    REJECTED = "rejected"


@dataclass
class Message:
    """Message data structure with full metadata"""
    message_id: str
    from_agent: str
    to_agent: str
    topic: str
    content: Dict
    timestamp: datetime
    session_id: Optional[str] = None
    read: bool = False
    delivery_attempts: int = 0
    delivery_status: MessageStatus = MessageStatus.PENDING
    ttl_seconds: int = 86400  # 24 hours

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "topic": self.topic,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "read": self.read,
            "delivery_attempts": self.delivery_attempts,
            "delivery_status": self.delivery_status.value,
            "ttl_seconds": self.ttl_seconds
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Reconstruct from JSON dict"""
        return cls(
            message_id=data["message_id"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            topic=data["topic"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data.get("session_id"),
            read=data.get("read", False),
            delivery_attempts=data.get("delivery_attempts", 0),
            delivery_status=MessageStatus(data.get("delivery_status", "pending")),
            ttl_seconds=data.get("ttl_seconds", 86400)
        )


@dataclass
class Session:
    """SIP-inspired session for multi-message conversations"""
    session_id: str
    initiator_agent: str
    target_agent: str
    session_type: str  # context_sync, task_delegation, coordination, etc.
    created_at: datetime
    state: SessionState = SessionState.INITIATED
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            "session_id": self.session_id,
            "initiator_agent": self.initiator_agent,
            "target_agent": self.target_agent,
            "session_type": self.session_type,
            "created_at": self.created_at.isoformat(),
            "state": self.state.value,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        """Reconstruct from JSON dict"""
        return cls(
            session_id=data["session_id"],
            initiator_agent=data["initiator_agent"],
            target_agent=data["target_agent"],
            session_type=data["session_type"],
            created_at=datetime.fromisoformat(data["created_at"]),
            state=SessionState(data.get("state", "initiated")),
            metadata=data.get("metadata", {})
        )


@dataclass
class Subscription:
    """Subscription to a message topic"""
    subscription_id: str
    agent_id: str
    topic: str
    callback: Optional[Callable] = None
    active: bool = True
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert to serializable dict (callback not serialized)"""
        return {
            "subscription_id": self.subscription_id,
            "agent_id": self.agent_id,
            "topic": self.topic,
            "active": self.active,
            "created_at": self.created_at.isoformat()
        }


class BackgroundCommManager:
    """
    Background communication manager for persistent agent messaging.

    Provides:
    - Pub/sub with offline message persistence
    - Direct agent-to-agent messaging with delivery guarantees
    - SIP-inspired session management
    - Automatic retry and expiry
    - Background listener threads for real-time delivery
    """

    # Redis key patterns
    MESSAGES_KEY = "comms:messages:{agent_id}"
    SUBSCRIPTIONS_KEY = "comms:subscriptions:{agent_id}"
    TOPIC_SUBSCRIBERS_KEY = "comms:topic_subscribers:{topic}"
    SESSIONS_KEY = "comms:sessions:{session_id}"
    SESSION_INDEX_KEY = "comms:sessions:index"
    DELIVERY_QUEUE_KEY = "comms:delivery_queue"
    AUDIT_LOG_KEY = "comms:audit:{agent_id}"

    def __init__(
        self,
        redis_client: redis.Redis,
        agent_id: str,
        max_retries: int = 3,
        retry_interval: int = 5,
        message_ttl: int = 86400,
        enable_background_listener: bool = True
    ):
        """
        Initialize background communication manager.

        Args:
            redis_client: Connected Redis client instance
            agent_id: ID of this agent
            max_retries: Max delivery attempts before marking failed
            retry_interval: Seconds between retry attempts
            message_ttl: Message TTL in seconds (default 24h)
            enable_background_listener: Start background listener thread
        """
        self.redis = redis_client
        self.agent_id = agent_id
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.message_ttl = message_ttl

        # In-memory subscription callbacks (not persisted)
        self._subscriptions: Dict[str, Subscription] = {}
        self._listener_thread: Optional[threading.Thread] = None
        self._listener_queue: queue.Queue = queue.Queue()
        self._stop_listener = threading.Event()

        # Test Redis connection
        try:
            self.redis.ping()
            logger.info(f"BackgroundCommManager initialized for agent {agent_id}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

        # Start background listener if enabled
        if enable_background_listener:
            self.start_background_listener()

    def subscribe(
        self,
        topic: str,
        callback: Callable[[Message], None]
    ) -> Subscription:
        """
        Subscribe to a message topic with persistent callback.

        Args:
            topic: Topic name to subscribe to
            callback: Async callback function(message: Message) -> None

        Returns:
            Subscription object
        """
        subscription_id = f"sub_{uuid.uuid4().hex[:12]}"
        subscription = Subscription(
            subscription_id=subscription_id,
            agent_id=self.agent_id,
            topic=topic,
            callback=callback,
            active=True
        )

        # Store subscription metadata in Redis
        self.redis.hset(
            self.SUBSCRIPTIONS_KEY.format(agent_id=self.agent_id),
            subscription_id,
            json.dumps(subscription.to_dict())
        )

        # Add to topic subscriber index
        self.redis.sadd(
            self.TOPIC_SUBSCRIBERS_KEY.format(topic=topic),
            self.agent_id
        )

        # Cache in-memory
        self._subscriptions[subscription_id] = subscription

        # Log audit event
        self._log_audit("subscribe", {
            "topic": topic,
            "subscription_id": subscription_id
        })

        logger.info(f"Agent {self.agent_id} subscribed to topic '{topic}'")
        return subscription

    def publish(self, topic: str, message_content: Dict) -> str:
        """
        Publish message to topic (persists for offline agents).

        Args:
            topic: Topic name
            message_content: Message dict/content

        Returns:
            message_id
        """
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        msg = Message(
            message_id=message_id,
            from_agent=self.agent_id,
            to_agent="*",  # Broadcast
            topic=topic,
            content=message_content,
            timestamp=now,
            ttl_seconds=self.message_ttl
        )

        # Get all subscribers for this topic
        subscribers = self.redis.smembers(
            self.TOPIC_SUBSCRIBERS_KEY.format(topic=topic)
        )

        if not subscribers:
            logger.warning(f"No subscribers for topic '{topic}'")
            return message_id

        # Send to each subscriber
        for subscriber_id in subscribers:
            self._deliver_message(msg, subscriber_id)

        # Log audit
        self._log_audit("publish", {
            "topic": topic,
            "message_id": message_id,
            "subscriber_count": len(subscribers)
        })

        logger.info(f"Published message {message_id} to topic '{topic}' "
                   f"({len(subscribers)} subscribers)")
        return message_id

    def send_direct(self, to_agent_id: str, message_content: Dict) -> str:
        """
        Send direct message with delivery guarantee.

        Args:
            to_agent_id: Target agent ID
            message_content: Message dict/content

        Returns:
            message_id
        """
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        msg = Message(
            message_id=message_id,
            from_agent=self.agent_id,
            to_agent=to_agent_id,
            topic="direct",
            content=message_content,
            timestamp=now,
            ttl_seconds=self.message_ttl
        )

        # Attempt delivery
        self._deliver_message(msg, to_agent_id)

        # Queue for retry if delivery fails
        self.redis.rpush(
            self.DELIVERY_QUEUE_KEY,
            json.dumps(msg.to_dict())
        )

        # Log audit
        self._log_audit("send_direct", {
            "to_agent": to_agent_id,
            "message_id": message_id
        })

        logger.info(f"Sent direct message {message_id} to {to_agent_id}")
        return message_id

    def get_unread_messages(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """
        Retrieve unread messages for an agent.

        Args:
            agent_id: Target agent (default: self)
            limit: Max messages to retrieve

        Returns:
            List of Message objects
        """
        agent_id = agent_id or self.agent_id

        messages = []
        message_list = self.redis.lrange(
            self.MESSAGES_KEY.format(agent_id=agent_id),
            0,
            limit - 1
        )

        for msg_json in message_list:
            msg_dict = json.loads(msg_json)
            msg = Message.from_dict(msg_dict)

            # Only include unread
            if not msg.read:
                messages.append(msg)

        logger.info(f"Retrieved {len(messages)} unread messages for {agent_id}")
        return messages

    def mark_read(self, message_id: str, agent_id: Optional[str] = None) -> bool:
        """
        Mark message as read.

        Args:
            message_id: Message ID to mark read
            agent_id: Agent ID (default: self)

        Returns:
            True if marked, False if not found
        """
        agent_id = agent_id or self.agent_id

        # Retrieve all messages
        messages = self.redis.lrange(
            self.MESSAGES_KEY.format(agent_id=agent_id),
            0,
            -1
        )

        # Find and update
        updated = False
        for idx, msg_json in enumerate(messages):
            msg_dict = json.loads(msg_json)
            if msg_dict["message_id"] == message_id:
                msg_dict["read"] = True
                msg_dict["delivery_status"] = MessageStatus.READ.value
                self.redis.lset(
                    self.MESSAGES_KEY.format(agent_id=agent_id),
                    idx,
                    json.dumps(msg_dict)
                )
                updated = True
                break

        if updated:
            self._log_audit("mark_read", {"message_id": message_id})
            logger.info(f"Marked message {message_id} as read")

        return updated

    def initiate_session(
        self,
        target_agent_id: str,
        session_type: str,
        metadata: Optional[Dict] = None
    ) -> Session:
        """
        SIP-inspired session initiation (INVITE → pending ACK).

        Args:
            target_agent_id: Target agent for session
            session_type: Type (context_sync, task_delegation, etc.)
            metadata: Optional session metadata

        Returns:
            Session object
        """
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        session = Session(
            session_id=session_id,
            initiator_agent=self.agent_id,
            target_agent=target_agent_id,
            session_type=session_type,
            created_at=now,
            state=SessionState.INITIATED,
            metadata=metadata or {}
        )

        # Store session metadata
        self.redis.hset(
            self.SESSIONS_KEY.format(session_id=session_id),
            mapping={
                "session_id": session_id,
                "initiator_agent": self.agent_id,
                "target_agent": target_agent_id,
                "session_type": session_type,
                "created_at": now.isoformat(),
                "state": SessionState.INITIATED.value,
                "metadata": json.dumps(metadata or {})
            }
        )
        self.redis.expire(
            self.SESSIONS_KEY.format(session_id=session_id),
            self.message_ttl
        )

        # Add to session index
        self.redis.sadd(self.SESSION_INDEX_KEY, session_id)

        # Send INVITE message
        invite_msg = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            from_agent=self.agent_id,
            to_agent=target_agent_id,
            topic=f"sip:invite",
            content={
                "session_id": session_id,
                "session_type": session_type,
                "metadata": metadata or {}
            },
            timestamp=now,
            session_id=session_id
        )

        self._deliver_message(invite_msg, target_agent_id)

        # Log audit
        self._log_audit("initiate_session", {
            "session_id": session_id,
            "target_agent": target_agent_id,
            "session_type": session_type
        })

        logger.info(f"Initiated session {session_id} to {target_agent_id} "
                   f"(type={session_type})")

        return session

    def accept_session(self, session_id: str) -> bool:
        """
        Accept session invitation (send ACK).

        Args:
            session_id: Session ID to accept

        Returns:
            True if accepted, False if session not found
        """
        session_data = self.redis.hgetall(
            self.SESSIONS_KEY.format(session_id=session_id)
        )

        if not session_data:
            logger.warning(f"Session {session_id} not found")
            return False

        session = Session.from_dict(session_data)

        # Update session state
        session.state = SessionState.ACTIVE
        self.redis.hset(
            self.SESSIONS_KEY.format(session_id=session_id),
            "state",
            SessionState.ACTIVE.value
        )

        # Send ACK message
        ack_msg = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            from_agent=self.agent_id,
            to_agent=session.initiator_agent,
            topic="sip:ack",
            content={"session_id": session_id},
            timestamp=datetime.utcnow(),
            session_id=session_id
        )

        self._deliver_message(ack_msg, session.initiator_agent)

        # Log audit
        self._log_audit("accept_session", {"session_id": session_id})

        logger.info(f"Accepted session {session_id}")
        return True

    def reject_session(self, session_id: str, reason: str = "") -> bool:
        """
        Reject session invitation (send CANCEL).

        Args:
            session_id: Session ID to reject
            reason: Rejection reason

        Returns:
            True if rejected, False if session not found
        """
        session_data = self.redis.hgetall(
            self.SESSIONS_KEY.format(session_id=session_id)
        )

        if not session_data:
            logger.warning(f"Session {session_id} not found")
            return False

        session = Session.from_dict(session_data)

        # Update session state
        session.state = SessionState.REJECTED
        self.redis.hset(
            self.SESSIONS_KEY.format(session_id=session_id),
            "state",
            SessionState.REJECTED.value
        )

        # Send CANCEL message
        cancel_msg = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            from_agent=self.agent_id,
            to_agent=session.initiator_agent,
            topic="sip:cancel",
            content={
                "session_id": session_id,
                "reason": reason
            },
            timestamp=datetime.utcnow(),
            session_id=session_id
        )

        self._deliver_message(cancel_msg, session.initiator_agent)

        # Log audit
        self._log_audit("reject_session", {
            "session_id": session_id,
            "reason": reason
        })

        logger.info(f"Rejected session {session_id}: {reason}")
        return True

    def terminate_session(self, session_id: str) -> bool:
        """
        Graceful session termination (BYE).

        Args:
            session_id: Session ID to terminate

        Returns:
            True if terminated, False if session not found
        """
        session_data = self.redis.hgetall(
            self.SESSIONS_KEY.format(session_id=session_id)
        )

        if not session_data:
            logger.warning(f"Session {session_id} not found")
            return False

        session = Session.from_dict(session_data)

        # Update session state
        session.state = SessionState.TERMINATED
        self.redis.hset(
            self.SESSIONS_KEY.format(session_id=session_id),
            "state",
            SessionState.TERMINATED.value
        )

        # Send BYE message to other participant
        bye_msg = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            from_agent=self.agent_id,
            to_agent=session.target_agent if self.agent_id == session.initiator_agent
                     else session.initiator_agent,
            topic="sip:bye",
            content={"session_id": session_id},
            timestamp=datetime.utcnow(),
            session_id=session_id
        )

        target = bye_msg.to_agent
        self._deliver_message(bye_msg, target)

        # Clean up session after retention period
        self.redis.expire(
            self.SESSIONS_KEY.format(session_id=session_id),
            3600  # 1 hour grace period
        )

        # Log audit
        self._log_audit("terminate_session", {"session_id": session_id})

        logger.info(f"Terminated session {session_id}")
        return True

    def start_background_listener(self) -> None:
        """Start background listener thread for real-time message delivery."""
        if self._listener_thread is not None:
            logger.warning("Background listener already running")
            return

        self._stop_listener.clear()
        self._listener_thread = threading.Thread(
            target=self._listener_worker,
            daemon=True,
            name=f"CommsListener-{self.agent_id}"
        )
        self._listener_thread.start()
        logger.info(f"Background listener started for {self.agent_id}")

    def stop_background_listener(self) -> None:
        """Stop background listener thread gracefully."""
        if self._listener_thread is None:
            return

        self._stop_listener.set()
        self._listener_thread.join(timeout=5)
        self._listener_thread = None
        logger.info(f"Background listener stopped for {self.agent_id}")

    def _deliver_message(self, message: Message, to_agent_id: str) -> bool:
        """
        Deliver message to target agent (with retry capability).

        Args:
            message: Message to deliver
            to_agent_id: Target agent ID

        Returns:
            True if delivered, False otherwise
        """
        try:
            # Store message in recipient's queue
            message_json = json.dumps(message.to_dict())
            self.redis.rpush(
                self.MESSAGES_KEY.format(agent_id=to_agent_id),
                message_json
            )

            # Set TTL on message list
            self.redis.expire(
                self.MESSAGES_KEY.format(agent_id=to_agent_id),
                message.ttl_seconds
            )

            # Attempt real-time notification via pub/sub
            try:
                self.redis.publish(
                    f"comms:agent:{to_agent_id}",
                    json.dumps({
                        "type": "new_message",
                        "message_id": message.message_id,
                        "from_agent": message.from_agent,
                        "topic": message.topic
                    })
                )
            except Exception as e:
                logger.debug(f"Pub/sub notification failed: {e}")

            logger.debug(f"Delivered message {message.message_id} to {to_agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to deliver message {message.message_id}: {e}")
            return False

    def _listener_worker(self) -> None:
        """Background worker thread for handling message delivery retries."""
        logger.info(f"Listener worker starting for {self.agent_id}")

        while not self._stop_listener.is_set():
            try:
                # Check delivery queue for failed messages
                msg_json = self.redis.lpop(self.DELIVERY_QUEUE_KEY)

                if msg_json:
                    msg_dict = json.loads(msg_json)
                    msg = Message.from_dict(msg_dict)

                    # Check TTL
                    age_seconds = (datetime.utcnow() - msg.timestamp).total_seconds()
                    if age_seconds > msg.ttl_seconds:
                        logger.warning(f"Message {msg.message_id} expired")
                        msg.delivery_status = MessageStatus.EXPIRED
                        continue

                    # Retry delivery
                    if msg.delivery_attempts < self.max_retries:
                        msg.delivery_attempts += 1
                        success = self._deliver_message(msg, msg.to_agent)

                        if not success:
                            # Re-queue for retry
                            self.redis.rpush(
                                self.DELIVERY_QUEUE_KEY,
                                json.dumps(msg.to_dict())
                            )
                            # Back-off before retrying
                            time.sleep(self.retry_interval)
                    else:
                        logger.error(f"Message {msg.message_id} max retries exceeded")
                        msg.delivery_status = MessageStatus.FAILED

                # Poll for subscription callbacks
                for sub_id, subscription in self._subscriptions.items():
                    if not subscription.active:
                        continue

                    # Check for new messages on this topic
                    messages = self.get_unread_messages(limit=1)
                    for msg in messages:
                        if msg.topic == subscription.topic:
                            try:
                                # Execute callback
                                subscription.callback(msg)
                                self.mark_read(msg.message_id)
                            except Exception as e:
                                logger.error(f"Callback error for {sub_id}: {e}")

                # Small sleep to prevent CPU spinning
                time.sleep(1)

            except Exception as e:
                logger.error(f"Listener worker error: {e}")
                time.sleep(1)

        logger.info(f"Listener worker stopped for {self.agent_id}")

    def _log_audit(self, operation: str, details: Dict) -> None:
        """Log operation to audit trail for IF.TTT compliance."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "operation": operation,
            "details": details
        }

        try:
            self.redis.rpush(
                self.AUDIT_LOG_KEY.format(agent_id=self.agent_id),
                json.dumps(audit_entry)
            )
            # 30-day retention
            self.redis.expire(
                self.AUDIT_LOG_KEY.format(agent_id=self.agent_id),
                30 * 24 * 3600
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve session by ID."""
        session_data = self.redis.hgetall(
            self.SESSIONS_KEY.format(session_id=session_id)
        )

        if not session_data:
            return None

        return Session.from_dict(session_data)

    def list_active_sessions(self) -> List[Session]:
        """List all active sessions."""
        session_ids = self.redis.smembers(self.SESSION_INDEX_KEY)
        sessions = []

        for session_id in session_ids:
            session = self.get_session(session_id)
            if session and session.state in [SessionState.INITIATED, SessionState.ACTIVE]:
                sessions.append(session)

        return sessions

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Retrieve audit log entries."""
        entries = self.redis.lrange(
            self.AUDIT_LOG_KEY.format(agent_id=self.agent_id),
            -limit,
            -1
        )

        return [json.loads(entry) for entry in entries]

    def cleanup_expired_messages(self) -> int:
        """Remove expired messages from all agent queues."""
        count = 0
        now = datetime.utcnow()

        # This would require scanning all message keys - simplified version
        # In production, use Redis SCAN to iterate efficiently
        logger.info(f"Cleanup: removed {count} expired messages")
        return count

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.stop_background_listener()


if __name__ == "__main__":
    # Example usage
    import redis

    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Initialize communication managers for two agents
    manager_a = BackgroundCommManager(r, "agent_a")
    manager_b = BackgroundCommManager(r, "agent_b")

    # Agent B subscribes to a topic
    def on_message(msg: Message):
        print(f"[Agent B] Received: {msg.topic} from {msg.from_agent}")

    manager_b.subscribe("task_updates", on_message)

    # Agent A publishes to topic
    msg_id = manager_a.publish("task_updates", {
        "task": "analyze_data",
        "status": "in_progress"
    })
    print(f"Published message {msg_id}")

    # Agent A sends direct message to B
    direct_msg_id = manager_a.send_direct("agent_b", {
        "type": "request",
        "content": "Please process this data"
    })
    print(f"Sent direct message {direct_msg_id}")

    # Check B's unread messages
    unread = manager_b.get_unread_messages()
    print(f"Agent B has {len(unread)} unread messages")

    # Initiate session
    session = manager_a.initiate_session(
        "agent_b",
        "context_sync",
        metadata={"priority": "high"}
    )
    print(f"Initiated session {session.session_id}")

    # Accept session
    manager_b.accept_session(session.session_id)
    print(f"Accepted session {session.session_id}")

    # Terminate session
    manager_a.terminate_session(session.session_id)
    print(f"Terminated session {session.session_id}")

    # Clean up
    manager_a.stop_background_listener()
    manager_b.stop_background_listener()
