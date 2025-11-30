#!/usr/bin/env python3
"""
Sonnet A - Infrastructure & Communication Coordinator

Part of the 40-Agent Swarm Mission (2 Sonnet × 20 Haiku each)
Coordinates infrastructure tasks: OpenWebUI API, Memory Modules, S2 Comms

Mission Reference: /home/setup/infrafabric/INFRAFABRIC_INTEGRATION_SWARM_MISSION_2025-11-30.md

Tasks A1-A15:
- A1-A5: OpenWebUI API Integration
- A6-A10: Memory Module Architecture
- A11-A15: S2 Intra-Swarm Communication

IF.TTT Compliance: All task dispatches logged with traceable IDs
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.logistics.redis_swarm_coordinator import RedisSwarmCoordinator


class SonnetACoordinator:
    """
    Sonnet A: Infrastructure & Communication Coordinator

    Manages 15 Haiku agents (A1-A15) for:
    - OpenWebUI API integration
    - Memory module architecture (Context Memory + Deep Storage)
    - S2 intra-swarm communication enhancements
    """

    # Task definitions for infrastructure workstream
    TASKS = {
        # OpenWebUI API Integration (A1-A5)
        "A1": {
            "name": "openwebui_api_audit",
            "type": "if.search",
            "description": "Audit OpenWebUI Functions API endpoints",
            "data": {
                "target": "openwebui_functions",
                "query": "Pipe Function API interface manifest.json",
                "output": "api_audit_report.json"
            },
            "priority": 10
        },
        "A2": {
            "name": "claude_cli_pipe",
            "type": "code_generation",
            "description": "Create Claude CLI Pipe function",
            "data": {
                "template": "openwebui_pipe",
                "output": "claude_cli_pipe.py",
                "features": ["streaming", "context_injection", "model_selection"]
            },
            "priority": 9
        },
        "A3": {
            "name": "model_visibility_filter",
            "type": "code_generation",
            "description": "Create model visibility Filter function",
            "data": {
                "template": "openwebui_filter",
                "output": "model_visibility_filter.py",
                "features": ["tag_filtering", "user_roles", "dynamic_visibility"]
            },
            "priority": 8
        },
        "A4": {
            "name": "multi_collection_rag",
            "type": "code_generation",
            "description": "Multi-collection RAG Pipe",
            "data": {
                "template": "openwebui_pipe",
                "output": "multi_rag_pipe.py",
                "features": ["collection_routing", "query_rewriting", "context_fusion"]
            },
            "priority": 7
        },
        "A5": {
            "name": "openwebui_test_suite",
            "type": "test_generation",
            "description": "Test suite for OpenWebUI functions",
            "data": {
                "targets": ["A2", "A3", "A4"],
                "output": "test_openwebui_functions.py"
            },
            "priority": 6
        },

        # Memory Module Architecture (A6-A10)
        "A6": {
            "name": "context_memory_schema",
            "type": "schema_design",
            "description": "Design Context Memory (Redis L1/L2) schema",
            "data": {
                "backend": "redis",
                "features": ["ttl_management", "hot_cold_tiering", "compression"],
                "output": "context_memory_schema.yaml"
            },
            "priority": 10
        },
        "A7": {
            "name": "deep_storage_schema",
            "type": "schema_design",
            "description": "Design Deep Storage (ChromaDB) schema",
            "data": {
                "backend": "chromadb",
                "features": ["semantic_search", "metadata_filtering", "collections"],
                "output": "deep_storage_schema.yaml"
            },
            "priority": 9
        },
        "A8": {
            "name": "memory_sync_service",
            "type": "code_generation",
            "description": "Context Memory ↔ Deep Storage sync service",
            "data": {
                "output": "memory_sync_service.py",
                "features": ["bidirectional_sync", "conflict_resolution", "batch_processing"]
            },
            "priority": 8
        },
        "A9": {
            "name": "memory_api_gateway",
            "type": "code_generation",
            "description": "Unified memory API gateway",
            "data": {
                "output": "memory_api_gateway.py",
                "features": ["read_through_cache", "write_behind", "circuit_breaker"]
            },
            "priority": 7
        },
        "A10": {
            "name": "memory_test_suite",
            "type": "test_generation",
            "description": "Test suite for memory modules",
            "data": {
                "targets": ["A6", "A7", "A8", "A9"],
                "output": "test_memory_modules.py"
            },
            "priority": 6
        },

        # S2 Intra-Swarm Communication (A11-A15)
        "A11": {
            "name": "s2_protocol_enhancement",
            "type": "code_review",
            "description": "Review and enhance S2 protocol",
            "data": {
                "source": "redis_swarm_coordinator.py",
                "focus": ["latency_optimization", "message_batching", "compression"],
                "output": "s2_enhancement_report.md"
            },
            "priority": 10
        },
        "A12": {
            "name": "haiku_spawn_manager",
            "type": "code_generation",
            "description": "Haiku agent spawn manager",
            "data": {
                "output": "haiku_spawn_manager.py",
                "features": ["pool_management", "load_balancing", "auto_scaling"]
            },
            "priority": 9
        },
        "A13": {
            "name": "context_sharing_v2",
            "type": "code_generation",
            "description": "Enhanced context sharing (800K+ tokens)",
            "data": {
                "output": "context_sharing_v2.py",
                "features": ["chunked_transfer", "delta_sync", "compression"]
            },
            "priority": 8
        },
        "A14": {
            "name": "cross_swarm_bridge",
            "type": "code_generation",
            "description": "Cross-swarm communication bridge",
            "data": {
                "output": "cross_swarm_bridge.py",
                "features": ["federation", "routing", "security"]
            },
            "priority": 7
        },
        "A15": {
            "name": "s2_test_suite",
            "type": "test_generation",
            "description": "S2 communication test suite",
            "data": {
                "targets": ["A11", "A12", "A13", "A14"],
                "output": "test_s2_communication.py"
            },
            "priority": 6
        }
    }

    def __init__(self,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 max_haiku_agents: int = 15):
        """Initialize Sonnet A coordinator."""
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.max_haiku_agents = max_haiku_agents
        self.coordinator: Optional[RedisSwarmCoordinator] = None
        self.agent_id: Optional[str] = None
        self.spawned_haikus: Dict[str, str] = {}  # task_id -> haiku_agent_id
        self.task_status: Dict[str, str] = {}  # task_id -> status

    def connect(self) -> bool:
        """Connect to Redis and register as Sonnet A coordinator."""
        try:
            self.coordinator = RedisSwarmCoordinator(
                redis_host=self.redis_host,
                redis_port=self.redis_port,
                redis_db=0
            )

            self.agent_id = self.coordinator.register_agent(
                role="sonnet_a_infrastructure",
                context_capacity=200000,
                metadata={
                    "model": "claude-sonnet-4.5",
                    "purpose": "infrastructure_coordination",
                    "workstream": "A",
                    "tasks": list(self.TASKS.keys()),
                    "max_haiku_agents": self.max_haiku_agents,
                    "started_at": datetime.now().isoformat()
                }
            )

            print(f"[SONNET-A] Registered as: {self.agent_id}")
            return True
        except Exception as e:
            print(f"[SONNET-A] Connection failed: {e}")
            return False

    def dispatch_all_tasks(self) -> Dict[str, str]:
        """Dispatch all infrastructure tasks to Haiku queue."""
        if not self.coordinator:
            raise RuntimeError("Not connected")

        dispatched = {}

        for task_key, task_def in self.TASKS.items():
            task_id = self.coordinator.post_task(
                queue_name="haiku_infrastructure",
                task_type=task_def["type"],
                task_data={
                    "task_key": task_key,
                    "name": task_def["name"],
                    "description": task_def["description"],
                    **task_def["data"]
                },
                priority=task_def["priority"]
            )

            dispatched[task_key] = task_id
            self.task_status[task_id] = "dispatched"

            print(f"[SONNET-A] Dispatched {task_key}: {task_def['name']} -> {task_id}")

        return dispatched

    def monitor_progress(self, duration: int = 300) -> Dict:
        """Monitor task completion for specified duration."""
        if not self.coordinator:
            raise RuntimeError("Not connected")

        start_time = time.time()
        end_time = start_time + duration
        completed_count = 0

        print(f"\n[SONNET-A] Monitoring {len(self.TASKS)} tasks for {duration}s...")

        while time.time() < end_time:
            # Check for completion messages
            messages = self.coordinator.get_messages(limit=20)

            for msg in messages:
                content = msg.get('content', {})
                if content.get('type') == 'task_result':
                    task_id = content.get('task_id')
                    if task_id in self.task_status:
                        self.task_status[task_id] = "completed"
                        completed_count += 1
                        print(f"[SONNET-A] Task completed: {task_id}")

            # Status update every 10 seconds
            if int(time.time()) % 10 == 0:
                pending = sum(1 for s in self.task_status.values() if s == "dispatched")
                print(f"[SONNET-A] Progress: {completed_count}/{len(self.TASKS)} complete, {pending} pending")

            # Send heartbeat
            self.coordinator.heartbeat()
            time.sleep(2)

        return {
            "total_tasks": len(self.TASKS),
            "completed": completed_count,
            "pending": len(self.TASKS) - completed_count,
            "duration": time.time() - start_time
        }

    def get_summary(self) -> Dict:
        """Get current coordination summary."""
        return {
            "coordinator": "Sonnet A - Infrastructure",
            "agent_id": self.agent_id,
            "workstream": "A (A1-A15)",
            "focus_areas": [
                "OpenWebUI API Integration",
                "Memory Module Architecture",
                "S2 Intra-Swarm Communication"
            ],
            "tasks_defined": len(self.TASKS),
            "task_status": dict(self.task_status),
            "spawned_haikus": len(self.spawned_haikus)
        }


def main():
    """Main entry point for Sonnet A coordinator."""
    import argparse

    parser = argparse.ArgumentParser(description='Sonnet A - Infrastructure Coordinator')
    parser.add_argument('--dispatch', action='store_true', help='Dispatch all tasks')
    parser.add_argument('--monitor', type=int, default=300, help='Monitor duration (seconds)')
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')

    args = parser.parse_args()

    coordinator = SonnetACoordinator(
        redis_host=args.redis_host,
        redis_port=args.redis_port
    )

    if not coordinator.connect():
        print("[FATAL] Could not connect to Redis")
        sys.exit(1)

    if args.dispatch:
        print("\n[SONNET-A] Dispatching infrastructure tasks...")
        dispatched = coordinator.dispatch_all_tasks()
        print(f"\n[SONNET-A] Dispatched {len(dispatched)} tasks")

        print("\n[SONNET-A] Starting monitoring phase...")
        result = coordinator.monitor_progress(args.monitor)

        print(f"\n[SONNET-A] Final Results:")
        print(json.dumps(result, indent=2))
    else:
        print("\n[SONNET-A] Task Definitions:")
        for key, task in coordinator.TASKS.items():
            print(f"  {key}: {task['name']} ({task['type']}) - Priority {task['priority']}")

        print("\nRun with --dispatch to start task distribution")


if __name__ == '__main__':
    main()
