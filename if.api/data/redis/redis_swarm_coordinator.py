#!/usr/bin/env python3
"""
Redis Swarm Coordinator - Multi-Agent AI Coordination System
Enables persistent Claude Sonnet/Haiku sessions to coordinate via Redis

Features:
- Session registration and heartbeat management
- Task queue with atomic claiming (Redis locks)
- Context window sharing (800K+ tokens)
- Direct agent-to-agent messaging
- Haiku-spawned-Haiku communication
- Pub/sub for real-time notifications
- Automatic session cleanup

Architecture:
- Main sessions (Sonnet/Haiku) register as agents with role + context capacity
- Sub-agents (spawned Haikus) register under parent session
- Tasks posted to queues, claimed atomically
- Context shared via versioned Redis keys
- All communication logged for IF.TTT traceability
"""

import redis
import json
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class RedisSwarmCoordinator:
    """
    Central coordinator for multi-agent swarm coordination

    Redis Key Schema:
    - agents:{agent_id}                    → Agent metadata (role, capacity, parent)
    - agents:{agent_id}:heartbeat          → Last heartbeat timestamp
    - agents:{agent_id}:context            → Full context window (chunked if >1MB)
    - tasks:queue:{queue_name}             → Task queue (list)
    - tasks:claimed:{task_id}              → Claimed by agent_id + timestamp
    - tasks:completed:{task_id}            → Result + completion time
    - messages:{to_agent_id}               → Direct messages (list)
    - swarm:sessions                       → Set of active main session IDs
    - swarm:subagents:{parent_id}          → Set of spawned sub-agents
    - channel:broadcast                    → Pub/sub broadcast channel
    - channel:agent:{agent_id}             → Per-agent pub/sub channel
    """

    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db,
                                  decode_responses=True)
        self.agent_id = None
        self.role = None
        self.parent_id = None

        # Test connection
        try:
            self.redis.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def register_agent(self,
                      role: str,
                      context_capacity: int = 200000,
                      parent_id: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> str:
        """
        Register a new agent in the swarm

        Args:
            role: Agent role (sonnet_coordinator, haiku_memory, haiku_worker, etc.)
            context_capacity: Token capacity (default 200K for Haiku)
            parent_id: If spawned by another agent, specify parent agent_id
            metadata: Additional metadata (model, specialization, etc.)

        Returns:
            agent_id: Unique identifier for this agent
        """
        agent_id = f"{role}_{uuid.uuid4().hex[:8]}"

        agent_data = {
            "agent_id": agent_id,
            "role": role,
            "context_capacity": context_capacity,
            "parent_id": parent_id or "none",
            "registered_at": datetime.now().isoformat(),
            "metadata": json.dumps(metadata or {})
        }

        # Store agent metadata
        self.redis.hset(f"agents:{agent_id}", mapping=agent_data)

        # Update heartbeat
        self.redis.set(f"agents:{agent_id}:heartbeat", time.time(), ex=300)  # 5min TTL

        # Track in global session list
        if parent_id:
            # Sub-agent: track under parent
            self.redis.sadd(f"swarm:subagents:{parent_id}", agent_id)
        else:
            # Main session: track in global sessions
            self.redis.sadd("swarm:sessions", agent_id)

        # Create pub/sub channel
        self.redis.publish("channel:broadcast", json.dumps({
            "type": "agent_registered",
            "agent_id": agent_id,
            "role": role,
            "parent_id": parent_id,
            "timestamp": time.time()
        }))

        self.agent_id = agent_id
        self.role = role
        self.parent_id = parent_id

        logger.info(f"Registered agent: {agent_id} (role={role}, parent={parent_id})")
        return agent_id

    def heartbeat(self, agent_id: Optional[str] = None):
        """Send heartbeat to indicate agent is alive"""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            raise ValueError("No agent_id specified and no agent registered")

        self.redis.set(f"agents:{agent_id}:heartbeat", time.time(), ex=300)

    def update_context(self,
                      context: str,
                      agent_id: Optional[str] = None,
                      version: Optional[str] = None):
        """
        Update agent's context window (shared with other agents)

        Args:
            context: Full context text (will be chunked if >1MB)
            agent_id: Target agent (defaults to self)
            version: Optional version tag (defaults to hash)
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            raise ValueError("No agent_id specified")

        # Generate version hash
        if not version:
            version = hashlib.sha256(context.encode()).hexdigest()[:12]

        # Store context (chunked if large)
        context_bytes = len(context.encode('utf-8'))
        chunk_size = 1024 * 1024  # 1MB chunks

        if context_bytes > chunk_size:
            # Chunked storage
            chunks = [context[i:i+chunk_size] for i in range(0, len(context), chunk_size)]
            self.redis.hset(f"agents:{agent_id}:context", mapping={
                "version": version,
                "chunks": len(chunks),
                "size_bytes": context_bytes,
                "updated_at": datetime.now().isoformat()
            })

            for idx, chunk in enumerate(chunks):
                self.redis.set(f"agents:{agent_id}:context:chunk:{idx}", chunk, ex=3600)

            logger.info(f"Updated context for {agent_id}: {len(chunks)} chunks, {context_bytes} bytes")
        else:
            # Single storage
            self.redis.hset(f"agents:{agent_id}:context", mapping={
                "version": version,
                "content": context,
                "size_bytes": context_bytes,
                "updated_at": datetime.now().isoformat()
            })
            logger.info(f"Updated context for {agent_id}: {context_bytes} bytes")

        # Notify subscribers
        self.redis.publish(f"channel:agent:{agent_id}", json.dumps({
            "type": "context_updated",
            "agent_id": agent_id,
            "version": version,
            "size_bytes": context_bytes
        }))

    def get_context(self, agent_id: str) -> Optional[str]:
        """Retrieve another agent's context window"""
        context_meta = self.redis.hgetall(f"agents:{agent_id}:context")

        if not context_meta:
            return None

        # Check if chunked
        if "chunks" in context_meta:
            chunks = []
            num_chunks = int(context_meta["chunks"])
            for idx in range(num_chunks):
                chunk = self.redis.get(f"agents:{agent_id}:context:chunk:{idx}")
                if chunk:
                    chunks.append(chunk)
                else:
                    logger.warning(f"Missing chunk {idx} for {agent_id}")

            return "".join(chunks)
        else:
            return context_meta.get("content")

    def post_task(self,
                 queue_name: str,
                 task_type: str,
                 task_data: Dict,
                 priority: int = 0) -> str:
        """
        Post a task to a queue for agents to claim

        Args:
            queue_name: Target queue (e.g., "search", "analysis", "coding")
            task_type: Type of task (e.g., "if.search", "context_summary")
            task_data: Task parameters and input data
            priority: Higher priority = processed first (default 0)

        Returns:
            task_id: Unique task identifier
        """
        task_id = f"task_{uuid.uuid4().hex[:12]}"

        task = {
            "task_id": task_id,
            "queue": queue_name,
            "type": task_type,
            "data": json.dumps(task_data),
            "posted_by": self.agent_id or "unknown",
            "posted_at": datetime.now().isoformat(),
            "priority": priority
        }

        # Store task metadata
        self.redis.hset(f"tasks:meta:{task_id}", mapping=task)

        # Add to queue with priority score
        self.redis.zadd(f"tasks:queue:{queue_name}", {task_id: -priority})

        # Notify queue subscribers
        self.redis.publish(f"channel:queue:{queue_name}", json.dumps({
            "type": "task_posted",
            "task_id": task_id,
            "task_type": task_type,
            "priority": priority
        }))

        logger.info(f"Posted task {task_id} to queue '{queue_name}' (type={task_type})")
        return task_id

    def claim_task(self, queue_name: str, timeout: int = 60) -> Optional[Dict]:
        """
        Atomically claim the next task from a queue

        Args:
            queue_name: Queue to claim from
            timeout: How long to hold the claim lock (seconds)

        Returns:
            Task dict if claimed, None if queue empty
        """
        if not self.agent_id:
            raise ValueError("Must register agent before claiming tasks")

        # Get highest priority task
        tasks = self.redis.zrange(f"tasks:queue:{queue_name}", 0, 0)

        if not tasks:
            return None

        task_id = tasks[0]

        # Try to acquire lock
        lock_key = f"tasks:claimed:{task_id}"
        claimed = self.redis.set(lock_key, json.dumps({
            "agent_id": self.agent_id,
            "claimed_at": datetime.now().isoformat()
        }), nx=True, ex=timeout)

        if not claimed:
            # Already claimed by another agent
            return None

        # Remove from queue
        self.redis.zrem(f"tasks:queue:{queue_name}", task_id)

        # Retrieve task metadata
        task_meta = self.redis.hgetall(f"tasks:meta:{task_id}")
        task_meta["data"] = json.loads(task_meta.get("data", "{}"))

        logger.info(f"Claimed task {task_id} from queue '{queue_name}'")
        return task_meta

    def complete_task(self, task_id: str, result: Any):
        """Mark task as completed with result"""
        completion_data = {
            "task_id": task_id,
            "completed_by": self.agent_id or "unknown",
            "completed_at": datetime.now().isoformat(),
            "result": json.dumps(result)
        }

        self.redis.hset(f"tasks:completed:{task_id}", mapping=completion_data)

        # Release claim lock
        self.redis.delete(f"tasks:claimed:{task_id}")

        # Notify
        task_meta = self.redis.hgetall(f"tasks:meta:{task_id}")
        posted_by = task_meta.get("posted_by", "unknown")

        self.redis.publish(f"channel:agent:{posted_by}", json.dumps({
            "type": "task_completed",
            "task_id": task_id,
            "completed_by": self.agent_id
        }))

        logger.info(f"Completed task {task_id}")

    def send_message(self, to_agent_id: str, message: Dict):
        """
        Send direct message to another agent (including spawned Haikus)

        Args:
            to_agent_id: Target agent identifier
            message: Message dict (type, content, etc.)
        """
        message_id = f"msg_{uuid.uuid4().hex[:8]}"

        message_data = {
            "message_id": message_id,
            "from": self.agent_id or "unknown",
            "to": to_agent_id,
            "timestamp": datetime.now().isoformat(),
            "content": json.dumps(message)
        }

        # Add to recipient's message queue
        self.redis.rpush(f"messages:{to_agent_id}", json.dumps(message_data))

        # Notify via pub/sub
        self.redis.publish(f"channel:agent:{to_agent_id}", json.dumps({
            "type": "new_message",
            "message_id": message_id,
            "from": self.agent_id
        }))

        logger.info(f"Sent message {message_id} to {to_agent_id}")

    def get_messages(self, agent_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Retrieve messages for an agent"""
        agent_id = agent_id or self.agent_id
        if not agent_id:
            raise ValueError("No agent_id specified")

        # Pop messages from queue
        messages = []
        for _ in range(limit):
            msg_json = self.redis.lpop(f"messages:{agent_id}")
            if not msg_json:
                break

            msg = json.loads(msg_json)
            msg["content"] = json.loads(msg["content"])
            messages.append(msg)

        return messages

    def list_active_agents(self, include_subagents: bool = False) -> List[Dict]:
        """List all active agents in the swarm"""
        agents = []

        # Get main sessions
        session_ids = self.redis.smembers("swarm:sessions")

        for agent_id in session_ids:
            # Check heartbeat
            heartbeat = self.redis.get(f"agents:{agent_id}:heartbeat")
            if heartbeat and (time.time() - float(heartbeat)) < 300:
                agent_data = self.redis.hgetall(f"agents:{agent_id}")
                agents.append(agent_data)

                if include_subagents:
                    # Include spawned sub-agents
                    subagent_ids = self.redis.smembers(f"swarm:subagents:{agent_id}")
                    for sub_id in subagent_ids:
                        sub_data = self.redis.hgetall(f"agents:{sub_id}")
                        if sub_data:
                            agents.append(sub_data)

        return agents

    def get_queue_status(self, queue_name: str) -> Dict:
        """Get status of a task queue"""
        pending_count = self.redis.zcard(f"tasks:queue:{queue_name}")

        return {
            "queue": queue_name,
            "pending_tasks": pending_count,
            "tasks": [task.decode() if isinstance(task, bytes) else task
                     for task in self.redis.zrange(f"tasks:queue:{queue_name}", 0, 9)]
        }

    def cleanup_stale_agents(self, max_age_seconds: int = 300):
        """Remove agents that haven't sent heartbeat recently"""
        session_ids = self.redis.smembers("swarm:sessions")

        for agent_id in session_ids:
            heartbeat = self.redis.get(f"agents:{agent_id}:heartbeat")
            if not heartbeat or (time.time() - float(heartbeat)) > max_age_seconds:
                logger.info(f"Removing stale agent: {agent_id}")
                self.redis.srem("swarm:sessions", agent_id)
                self.redis.delete(f"agents:{agent_id}")
                self.redis.delete(f"agents:{agent_id}:heartbeat")


if __name__ == "__main__":
    # Example usage
    coordinator = RedisSwarmCoordinator()

    # Register as main Sonnet coordinator
    agent_id = coordinator.register_agent(
        role="sonnet_coordinator",
        context_capacity=20000,
        metadata={"model": "claude-sonnet-4.5", "purpose": "orchestration"}
    )

    print(f"Registered as: {agent_id}")

    # Post a test task
    task_id = coordinator.post_task(
        queue_name="search",
        task_type="if.search",
        task_data={"query": "computational vertigo", "context": "SESSION-RESUME.md"}
    )

    print(f"Posted task: {task_id}")

    # List active agents
    agents = coordinator.list_active_agents()
    print(f"Active agents: {len(agents)}")
