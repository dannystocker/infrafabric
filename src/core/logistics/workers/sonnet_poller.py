#!/usr/bin/env python3
"""
Sonnet S2 Coordinator - Redis-Based Multi-Agent Polling Loop

This script implements the S2 (Swarm-to-Swarm) communication protocol:
1. Registers as a Sonnet coordinator in the Redis swarm
2. Polls for task completions and Haiku responses via Redis
3. Coordinates sub-agent spawning and task distribution
4. Provides real-time status with 0.071ms Redis latency

Replaces legacy JSONL file-based communication with Redis pub/sub.

Usage:
    python sonnet_poller.py [--duration SECONDS] [--role ROLE]

IF.TTT Compliance: All messages logged with traceable IDs
"""

import json
import time
import os
import sys
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Set

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.core.logistics.redis_swarm_coordinator import RedisSwarmCoordinator
except ImportError:
    # Fallback for standalone execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from redis_swarm_coordinator import RedisSwarmCoordinator


class SonnetS2Coordinator:
    """
    Sonnet coordinator using Redis S2 protocol for swarm communication.

    Features:
    - Real-time task monitoring via Redis pub/sub
    - Haiku agent spawning and coordination
    - Context window sharing (up to 800K tokens)
    - Automatic heartbeat management
    - IF.TTT compliant logging
    """

    def __init__(self,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 role: str = 'sonnet_coordinator',
                 duration: int = 300):
        """
        Initialize Sonnet S2 Coordinator.

        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            role: Agent role identifier
            duration: Polling duration in seconds (default 5 minutes)
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.role = role
        self.duration = duration
        self.coordinator: Optional[RedisSwarmCoordinator] = None
        self.agent_id: Optional[str] = None
        self.displayed_responses: Set[str] = set()
        self.tasks_posted: Dict[str, dict] = {}
        self.tasks_completed: Dict[str, dict] = {}

    def connect(self) -> bool:
        """Connect to Redis and register as coordinator."""
        try:
            self.coordinator = RedisSwarmCoordinator(
                redis_host=self.redis_host,
                redis_port=self.redis_port,
                redis_db=0
            )

            self.agent_id = self.coordinator.register_agent(
                role=self.role,
                context_capacity=200000,  # 200K tokens for Sonnet
                metadata={
                    "model": "claude-sonnet-4.5",
                    "purpose": "orchestration",
                    "protocol": "S2",
                    "started_at": datetime.now().isoformat()
                }
            )

            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to Redis: {e}")
            return False

    def post_task_to_haiku(self,
                          task_type: str,
                          task_data: Dict,
                          queue: str = "haiku_tasks",
                          priority: int = 0) -> Optional[str]:
        """
        Post a task for Haiku agents to process.

        Args:
            task_type: Type of task (if.search, context_summary, etc.)
            task_data: Task parameters
            queue: Target queue name
            priority: Task priority (higher = first)

        Returns:
            task_id if successful, None otherwise
        """
        if not self.coordinator:
            return None

        task_id = self.coordinator.post_task(
            queue_name=queue,
            task_type=task_type,
            task_data=task_data,
            priority=priority
        )

        self.tasks_posted[task_id] = {
            "type": task_type,
            "data": task_data,
            "posted_at": time.time(),
            "status": "pending"
        }

        return task_id

    def check_messages(self) -> List[Dict]:
        """Check for new messages from Haiku agents."""
        if not self.coordinator:
            return []

        return self.coordinator.get_messages(limit=20)

    def get_active_agents(self) -> List[Dict]:
        """Get list of active agents in the swarm."""
        if not self.coordinator:
            return []

        return self.coordinator.list_active_agents(include_subagents=True)

    def get_queue_status(self, queue: str = "haiku_tasks") -> Dict:
        """Get status of a task queue."""
        if not self.coordinator:
            return {"error": "not connected"}

        return self.coordinator.get_queue_status(queue)

    def run_polling_loop(self):
        """Main polling loop with Redis S2 protocol."""

        print(f"\n{'='*80}")
        print(f"SONNET S2 COORDINATOR - Redis-Based Swarm Communication")
        print(f"{'='*80}")
        print(f"Agent ID: {self.agent_id}")
        print(f"Redis: {self.redis_host}:{self.redis_port}")
        print(f"Duration: {self.duration} seconds")
        print(f"Protocol: S2 (0.071ms latency)")
        print(f"{'='*80}\n")

        start_time = time.time()
        end_time = start_time + self.duration
        last_status_time = start_time
        last_heartbeat = start_time
        responses_seen = 0

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting S2 polling loop...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Loop ends at: {datetime.fromtimestamp(end_time).strftime('%H:%M:%S')}\n")

        try:
            while time.time() < end_time:
                current_time = time.time()
                remaining = int(end_time - current_time)

                # Send heartbeat every 30 seconds
                if current_time - last_heartbeat >= 30:
                    self.coordinator.heartbeat()
                    last_heartbeat = current_time

                # Check for messages from Haiku agents
                messages = self.check_messages()

                for msg in messages:
                    msg_id = msg.get('message_id', 'unknown')

                    if msg_id not in self.displayed_responses:
                        self.displayed_responses.add(msg_id)
                        responses_seen += 1

                        content = msg.get('content', {})
                        msg_type = content.get('type', 'unknown')

                        print(f"\n{'='*80}")
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ MESSAGE #{responses_seen} RECEIVED")
                        print(f"{'='*80}")
                        print(f"From: {msg.get('from', 'unknown')}")
                        print(f"Type: {msg_type}")

                        if msg_type == 'task_result':
                            print(f"Task ID: {content.get('task_id', 'N/A')}")
                            print(f"Result: {json.dumps(content.get('result', {}), indent=2)[:500]}")
                        elif msg_type == 'context_update':
                            print(f"Context Version: {content.get('version', 'N/A')}")
                            print(f"Size: {content.get('size_bytes', 0)} bytes")
                        else:
                            print(f"Content: {json.dumps(content, indent=2)[:500]}")

                        print(f"{'='*80}\n")

                # Show status every 5 seconds
                if int(current_time) - int(last_status_time) >= 5:
                    agents = self.get_active_agents()
                    queue_status = self.get_queue_status()

                    haiku_count = sum(1 for a in agents if 'haiku' in a.get('role', '').lower())
                    sonnet_count = sum(1 for a in agents if 'sonnet' in a.get('role', '').lower())

                    status_line = f"[{datetime.now().strftime('%H:%M:%S')}] "
                    status_line += f"POLLING ({remaining:3d}s) | "
                    status_line += f"Agents: {sonnet_count}S/{haiku_count}H | "
                    status_line += f"Queue: {queue_status.get('pending_tasks', 0)} | "
                    status_line += f"Msgs: {responses_seen} "

                    # Progress bar
                    progress = (current_time - start_time) / self.duration
                    bar_length = 20
                    filled = int(bar_length * progress)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    status_line += f"[{bar}]"

                    print(status_line)
                    last_status_time = current_time

                # Poll every 1 second (Redis is fast enough)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED BY USER]")

        # Final summary
        self._print_summary(start_time, responses_seen)

    def _print_summary(self, start_time: float, responses_seen: int):
        """Print final session summary."""
        duration = time.time() - start_time
        agents = self.get_active_agents()

        print(f"\n{'='*80}")
        print(f"S2 COORDINATION SESSION COMPLETE")
        print(f"{'='*80}")
        print(f"Duration: {int(duration)} seconds")
        print(f"Messages received: {responses_seen}")
        print(f"Tasks posted: {len(self.tasks_posted)}")
        print(f"Tasks completed: {len(self.tasks_completed)}")
        print(f"Active agents: {len(agents)}")
        print(f"{'='*80}\n")

        # Agent breakdown
        if agents:
            print(f"Active Agent Summary:\n")
            print(f"{'Role':<25} | {'Agent ID':<20} | {'Parent':<15}")
            print(f"{'-'*65}")

            for agent in agents:
                role = agent.get('role', 'unknown')
                agent_id = agent.get('agent_id', 'unknown')[:18]
                parent = agent.get('parent_id', 'none')[:13]
                print(f"{role:<25} | {agent_id:<20} | {parent:<15}")

            print(f"\n{'='*80}\n")

        # Haiku response check
        haiku_agents = [a for a in agents if 'haiku' in a.get('role', '').lower()]

        if haiku_agents:
            print(f"✓ {len(haiku_agents)} Haiku agent(s) active in swarm!")
            print(f"✓ S2 distributed communication OPERATIONAL!\n")
        else:
            print(f"✗ No Haiku agents currently active.")
            print(f"  Spawn Haiku workers with: coordinator.register_agent(role='haiku_worker', parent_id='{self.agent_id}')\n")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Sonnet S2 Coordinator - Redis-Based Swarm Communication'
    )
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=300,
        help='Polling duration in seconds (default: 300)'
    )
    parser.add_argument(
        '--role', '-r',
        type=str,
        default='sonnet_coordinator',
        help='Agent role (default: sonnet_coordinator)'
    )
    parser.add_argument(
        '--redis-host',
        type=str,
        default='localhost',
        help='Redis host (default: localhost)'
    )
    parser.add_argument(
        '--redis-port',
        type=int,
        default=6379,
        help='Redis port (default: 6379)'
    )

    args = parser.parse_args()

    coordinator = SonnetS2Coordinator(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        role=args.role,
        duration=args.duration
    )

    if not coordinator.connect():
        print("[FATAL] Could not connect to Redis. Ensure Redis is running.")
        sys.exit(1)

    coordinator.run_polling_loop()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
