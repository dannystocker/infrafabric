#!/usr/bin/env python3
"""
Redis Swarm V2: Epic Games Model + Gedimat Intelligence Pattern

Architecture:
- Persistent memory shards (Haiku sessions, 200K context)
- Ephemeral workers (spawned via Task tool, report back, disappear)
- Redis preserves worker findings even after Task completion
- IF.optimise x IF.guard x IF.search x IF.swarm integration

Key Difference from V1:
V1: Spawned workers stay alive and communicate
V2: Spawned workers are ephemeral, findings stored in Redis for parent to retrieve

Based on:
- Gedimat logistics analysis (40 Haiku agents, 8 passes IF.search)
- Epic Games V4 model (3 levels + plateau + debug)
"""

import redis
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SwarmMemoryShard:
    """
    Persistent Haiku memory shard with 200K context window
    Spawns ephemeral workers, collects their findings, preserves knowledge
    """

    def __init__(self, redis_host='localhost', redis_port=6379, specialization='general'):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.redis.ping()

        self.agent_id = f"memory_{specialization}_{uuid.uuid4().hex[:8]}"
        self.specialization = specialization
        self.context = ""
        self.worker_findings = []  # Accumulates findings from ephemeral workers

        # Register in swarm
        self.redis.hset(f"shard:{self.agent_id}", mapping={
            "type": "persistent_memory",
            "specialization": specialization,
            "context_capacity": 200000,
            "registered_at": datetime.now().isoformat()
        })

        self.redis.sadd("swarm:memory_shards", self.agent_id)
        logger.info(f"Memory shard initialized: {self.agent_id} ({specialization})")

    def load_context(self, context_text: str, context_source: str):
        """
        Load initial context into shard (e.g., SESSION-RESUME.md)
        This persists for lifetime of shard
        """
        self.context = context_text

        # Store in Redis for sharing
        self.redis.hset(f"shard:{self.agent_id}:context", mapping={
            "content": context_text[:1024*1024],  # First 1MB
            "source": context_source,
            "size_bytes": len(context_text.encode()),
            "loaded_at": datetime.now().isoformat()
        })

        # Store full context in chunks if large
        if len(context_text) > 1024*1024:
            chunks = [context_text[i:i+1024*1024]
                     for i in range(0, len(context_text), 1024*1024)]
            self.redis.set(f"shard:{self.agent_id}:context:chunks", len(chunks))
            for idx, chunk in enumerate(chunks):
                self.redis.set(f"shard:{self.agent_id}:context:chunk:{idx}",
                              chunk, ex=86400)  # 24h TTL

        logger.info(f"Loaded context: {len(context_text)} chars from {context_source}")

    def spawn_worker_task(self,
                         task_type: str,
                         task_description: str,
                         task_data: Dict,
                         pass_name: Optional[str] = None) -> str:
        """
        Post task for ephemeral worker to claim
        Worker will be spawned via Task tool, complete work, then disappear

        Args:
            task_type: e.g., "if.search_pass1", "analysis", "validation"
            task_description: Human-readable description
            task_data: Parameters for worker (query, context ref, etc.)
            pass_name: IF.search pass name (Pass 1, Pass 2, etc.)

        Returns:
            task_id for tracking
        """
        task_id = f"task_{self.specialization}_{uuid.uuid4().hex[:8]}"

        task_record = {
            "task_id": task_id,
            "parent_shard": self.agent_id,
            "type": task_type,
            "description": task_description,
            "data": json.dumps(task_data),
            "pass_name": pass_name or "unknown",
            "posted_at": datetime.now().isoformat(),
            "status": "pending"
        }

        # Store task
        self.redis.hset(f"task:{task_id}", mapping=task_record)

        # Add to work queue
        queue_name = f"queue:{task_type}"
        self.redis.rpush(queue_name, task_id)

        # Track under parent
        self.redis.rpush(f"shard:{self.agent_id}:tasks", task_id)

        logger.info(f"Spawned task {task_id}: {task_description}")
        return task_id

    def collect_worker_finding(self,
                               task_id: str,
                               finding: Dict,
                               worker_id: Optional[str] = None):
        """
        Called when ephemeral worker completes task
        Worker disappears after this, but finding persists in parent shard
        """
        finding_record = {
            "task_id": task_id,
            "worker_id": worker_id or "unknown",
            "timestamp": datetime.now().isoformat(),
            "content": json.dumps(finding)
        }

        # Store finding
        finding_id = f"finding_{uuid.uuid4().hex[:8]}"
        self.redis.hset(f"finding:{finding_id}", mapping=finding_record)

        # Link to parent shard
        self.redis.rpush(f"shard:{self.agent_id}:findings", finding_id)

        # Update task status
        self.redis.hset(f"task:{task_id}", mapping={
            "status": "completed",
            "finding_id": finding_id,
            "completed_at": datetime.now().isoformat()
        })

        # Add to memory
        self.worker_findings.append(finding)

        logger.info(f"Collected finding from task {task_id}: {finding.get('summary', 'No summary')}")

    def get_all_findings(self, task_type: Optional[str] = None) -> List[Dict]:
        """
        Retrieve all findings collected from ephemeral workers
        Findings persist even after workers disappear
        """
        finding_ids = self.redis.lrange(f"shard:{self.agent_id}:findings", 0, -1)

        findings = []
        for fid in finding_ids:
            finding_data = self.redis.hgetall(f"finding:{fid}")
            if finding_data:
                content = json.loads(finding_data.get("content", "{}"))

                # Filter by task type if specified
                task_id = finding_data.get("task_id")
                task_data = self.redis.hgetall(f"task:{task_id}")
                if task_type and task_data.get("type") != task_type:
                    continue

                findings.append({
                    "finding_id": fid,
                    "task_id": task_id,
                    "worker_id": finding_data.get("worker_id"),
                    "timestamp": finding_data.get("timestamp"),
                    "content": content
                })

        return findings

    def synthesize_findings(self,
                           pass_name: str,
                           synthesis: str,
                           sources: List[str]):
        """
        After collecting findings from multiple ephemeral workers,
        synthesize into coherent knowledge (done by persistent Sonnet or this shard)
        """
        synthesis_id = f"synthesis_{pass_name}_{uuid.uuid4().hex[:8]}"

        synthesis_record = {
            "synthesis_id": synthesis_id,
            "parent_shard": self.agent_id,
            "pass_name": pass_name,
            "content": synthesis,
            "sources": json.dumps(sources),
            "created_at": datetime.now().isoformat()
        }

        self.redis.hset(f"synthesis:{synthesis_id}", mapping=synthesis_record)
        self.redis.rpush(f"shard:{self.agent_id}:syntheses", synthesis_id)

        logger.info(f"Synthesized {pass_name}: {len(synthesis)} chars, {len(sources)} sources")
        return synthesis_id

    def get_context_for_worker(self) -> Dict:
        """
        Prepare context package for ephemeral worker
        Worker gets enough info to do task, then returns findings
        """
        return {
            "parent_shard_id": self.agent_id,
            "specialization": self.specialization,
            "context_preview": self.context[:5000],  # First 5K chars
            "context_full_location": f"shard:{self.agent_id}:context",
            "findings_count": len(self.worker_findings)
        }

    def heartbeat(self):
        """Maintain presence in swarm"""
        self.redis.set(f"shard:{self.agent_id}:heartbeat", time.time(), ex=300)


class EphemeralWorker:
    """
    Temporary worker spawned via Task tool
    Claims task, does work, reports finding, then disappears
    Context NOT preserved after completion
    """

    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.redis.ping()

        self.worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        self.task_id = None
        self.parent_shard_id = None

        logger.info(f"Ephemeral worker spawned: {self.worker_id}")

    def claim_task(self, queue_name: str) -> Optional[Dict]:
        """Claim next task from queue"""
        task_id = self.redis.lpop(queue_name)

        if not task_id:
            return None

        task_data = self.redis.hgetall(f"task:{task_id}")
        if not task_data:
            return None

        self.task_id = task_id
        self.parent_shard_id = task_data.get("parent_shard")

        # Mark claimed
        self.redis.hset(f"task:{task_id}", mapping={
            "status": "in_progress",
            "worker_id": self.worker_id,
            "claimed_at": datetime.now().isoformat()
        })

        logger.info(f"Worker {self.worker_id} claimed task {task_id}")

        task_data["data"] = json.loads(task_data.get("data", "{}"))
        return task_data

    def report_finding(self, finding: Dict):
        """
        Report finding back to parent shard
        This is the ONLY output that persists after worker disappears
        """
        if not self.task_id or not self.parent_shard_id:
            raise ValueError("No task claimed yet")

        # Store finding in parent shard
        finding_record = {
            "task_id": self.task_id,
            "worker_id": self.worker_id,
            "timestamp": datetime.now().isoformat(),
            "content": json.dumps(finding)
        }

        finding_id = f"finding_{uuid.uuid4().hex[:8]}"
        self.redis.hset(f"finding:{finding_id}", mapping=finding_record)

        # Link to parent shard
        self.redis.rpush(f"shard:{self.parent_shard_id}:findings", finding_id)

        # Update task
        self.redis.hset(f"task:{self.task_id}", mapping={
            "status": "completed",
            "finding_id": finding_id,
            "completed_at": datetime.now().isoformat()
        })

        logger.info(f"Worker {self.worker_id} reported finding for task {self.task_id}")

    def get_parent_context(self) -> str:
        """Retrieve parent shard's full context for processing"""
        if not self.parent_shard_id:
            raise ValueError("No parent shard assigned")

        context_data = self.redis.hgetall(f"shard:{self.parent_shard_id}:context")

        # Check if chunked
        num_chunks = self.redis.get(f"shard:{self.parent_shard_id}:context:chunks")
        if num_chunks:
            chunks = []
            for idx in range(int(num_chunks)):
                chunk = self.redis.get(f"shard:{self.parent_shard_id}:context:chunk:{idx}")
                if chunk:
                    chunks.append(chunk)
            return "".join(chunks)
        else:
            return context_data.get("content", "")


class SonnetCoordinator:
    """
    Strategic coordinator (20K context)
    Orchestrates memory shards and interprets synthesized findings
    Does NOT spawn workers directly - shards do that
    """

    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.redis.ping()

        self.agent_id = f"coordinator_{uuid.uuid4().hex[:8]}"

        self.redis.hset(f"coordinator:{self.agent_id}", mapping={
            "type": "sonnet_coordinator",
            "registered_at": datetime.now().isoformat()
        })

        logger.info(f"Sonnet coordinator initialized: {self.agent_id}")

    def get_swarm_status(self) -> Dict:
        """Get overview of all memory shards and their findings"""
        shard_ids = self.redis.smembers("swarm:memory_shards")

        shards = []
        for shard_id in shard_ids:
            shard_data = self.redis.hgetall(f"shard:{shard_id}")
            if not shard_data:
                continue

            # Count findings
            findings_count = self.redis.llen(f"shard:{shard_id}:findings")

            # Count pending tasks
            task_ids = self.redis.lrange(f"shard:{shard_id}:tasks", 0, -1)
            pending_count = sum(1 for tid in task_ids
                               if self.redis.hget(f"task:{tid}", "status") == "pending")

            shards.append({
                "shard_id": shard_id,
                "specialization": shard_data.get("specialization"),
                "findings_count": findings_count,
                "pending_tasks": pending_count
            })

        return {
            "total_shards": len(shards),
            "shards": shards,
            "coordinator_id": self.agent_id
        }

    def request_synthesis(self, shard_id: str, pass_name: str, instructions: str) -> str:
        """
        Ask memory shard to synthesize its collected findings
        Returns synthesis_id for retrieval
        """
        synthesis_task_id = f"synthesis_request_{uuid.uuid4().hex[:8]}"

        self.redis.hset(f"synthesis_request:{synthesis_task_id}", mapping={
            "shard_id": shard_id,
            "pass_name": pass_name,
            "instructions": instructions,
            "requested_by": self.agent_id,
            "requested_at": datetime.now().isoformat()
        })

        self.redis.rpush(f"shard:{shard_id}:synthesis_requests", synthesis_task_id)

        logger.info(f"Requested synthesis from {shard_id}: {pass_name}")
        return synthesis_task_id


if __name__ == "__main__":
    # Example: Gedimat-style intelligence gathering

    # 1. Create persistent memory shard
    shard = SwarmMemoryShard(specialization="gedimat_logistics")

    # 2. Load context (e.g., Gedimat operational docs)
    shard.load_context(
        context_text="Gedimat has 3 depots... [200K tokens of context]",
        context_source="gedimat_operational_context.md"
    )

    # 3. Spawn 5 ephemeral workers for IF.search Pass 1
    for i in range(5):
        task_id = shard.spawn_worker_task(
            task_type="if.search_pass1",
            task_description=f"Research logistics optimization patterns #{i+1}",
            task_data={"query": f"logistics pattern {i+1}", "context_ref": shard.agent_id},
            pass_name="Pass 1: Signal Capture"
        )

    print("Spawned 5 tasks for Pass 1")

    # 4. Ephemeral worker lifecycle (simulated)
    worker = EphemeralWorker()
    task = worker.claim_task("queue:if.search_pass1")

    if task:
        # Worker does research...
        finding = {
            "summary": "Found 3 logistics patterns applicable to Gedimat",
            "patterns": ["milkrun", "cross-dock", "consolidation"],
            "sources": ["source1.pdf", "source2.pdf"]
        }

        worker.report_finding(finding)
        print("Worker reported finding and will now disappear")

    # 5. Parent shard collects all findings
    findings = shard.get_all_findings(task_type="if.search_pass1")
    print(f"Collected {len(findings)} findings from Pass 1")

    # 6. Synthesize (done by shard or coordinator)
    synthesis_id = shard.synthesize_findings(
        pass_name="Pass 1",
        synthesis="After reviewing 5 research tasks, 3 key patterns emerged...",
        sources=["finding_12345", "finding_67890"]
    )

    print(f"Synthesis complete: {synthesis_id}")
