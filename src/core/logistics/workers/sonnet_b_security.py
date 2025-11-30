#!/usr/bin/env python3
"""
Sonnet B - Security & Registry Coordinator

Part of the 40-Agent Swarm Mission (2 Sonnet × 20 Haiku each)
Coordinates security tasks: IF.emotion Sandboxing, Claude Max Registry

Mission Reference: /home/setup/infrafabric/INFRAFABRIC_INTEGRATION_SWARM_MISSION_2025-11-30.md

Tasks B1-B20:
- B1-B8: IF.emotion Security Sandboxing (8-layer defense)
- B9-B15: Claude Max Registry
- B16-B20: Integration Testing & Documentation

IF.TTT Compliance: All task dispatches logged with traceable IDs
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.logistics.redis_swarm_coordinator import RedisSwarmCoordinator


class SonnetBCoordinator:
    """
    Sonnet B: Security & Registry Coordinator

    Manages 20 Haiku agents (B1-B20) for:
    - IF.emotion security sandboxing (8-layer defense)
    - Claude Max registry with timeout prevention
    - Integration testing and documentation
    """

    # Task definitions for security workstream
    TASKS = {
        # IF.emotion Security Sandboxing - 8 Layers (B1-B8)
        "B1": {
            "name": "emotion_input_sanitizer",
            "type": "code_generation",
            "description": "Layer 1: Input sanitization for IF.emotion",
            "data": {
                "layer": 1,
                "output": "emotion_input_sanitizer.py",
                "features": ["injection_prevention", "encoding_validation", "length_limits"]
            },
            "priority": 10
        },
        "B2": {
            "name": "emotion_output_filter",
            "type": "code_generation",
            "description": "Layer 2: Output filtering for psychological safety",
            "data": {
                "layer": 2,
                "output": "emotion_output_filter.py",
                "features": ["content_classification", "harm_detection", "redaction"]
            },
            "priority": 10
        },
        "B3": {
            "name": "emotion_rate_limiter",
            "type": "code_generation",
            "description": "Layer 3: Rate limiting and abuse prevention",
            "data": {
                "layer": 3,
                "output": "emotion_rate_limiter.py",
                "features": ["token_bucket", "user_quotas", "burst_control"]
            },
            "priority": 9
        },
        "B4": {
            "name": "emotion_session_isolation",
            "type": "code_generation",
            "description": "Layer 4: Session isolation (no cross-contamination)",
            "data": {
                "layer": 4,
                "output": "emotion_session_isolation.py",
                "features": ["namespace_separation", "memory_isolation", "context_boundaries"]
            },
            "priority": 9
        },
        "B5": {
            "name": "emotion_audit_logger",
            "type": "code_generation",
            "description": "Layer 5: IF.TTT compliant audit logging",
            "data": {
                "layer": 5,
                "output": "emotion_audit_logger.py",
                "features": ["structured_logging", "immutable_records", "citation_generation"]
            },
            "priority": 8
        },
        "B6": {
            "name": "emotion_guardian_integration",
            "type": "code_generation",
            "description": "Layer 6: Guardian Council integration",
            "data": {
                "layer": 6,
                "output": "emotion_guardian_integration.py",
                "features": ["vote_routing", "escalation_triggers", "consensus_tracking"]
            },
            "priority": 8
        },
        "B7": {
            "name": "emotion_encryption_layer",
            "type": "code_generation",
            "description": "Layer 7: Data encryption at rest and transit",
            "data": {
                "layer": 7,
                "output": "emotion_encryption_layer.py",
                "features": ["aes256_encryption", "key_rotation", "secure_storage"]
            },
            "priority": 7
        },
        "B8": {
            "name": "emotion_sandbox_orchestrator",
            "type": "code_generation",
            "description": "Layer 8: Sandbox orchestration (all layers)",
            "data": {
                "layer": 8,
                "output": "emotion_sandbox_orchestrator.py",
                "features": ["layer_composition", "health_checks", "failsafe_triggers"]
            },
            "priority": 7
        },

        # Claude Max Registry (B9-B15)
        "B9": {
            "name": "registry_schema_design",
            "type": "schema_design",
            "description": "Claude Max registry schema",
            "data": {
                "output": "claude_max_registry_schema.yaml",
                "features": ["model_capabilities", "rate_limits", "cost_tracking"]
            },
            "priority": 10
        },
        "B10": {
            "name": "registry_timeout_prevention",
            "type": "code_generation",
            "description": "Timeout prevention with checkpointing",
            "data": {
                "output": "timeout_prevention.py",
                "features": ["checkpoint_manager", "progress_tracking", "auto_resume"]
            },
            "priority": 10
        },
        "B11": {
            "name": "registry_capability_router",
            "type": "code_generation",
            "description": "Capability-based model routing",
            "data": {
                "output": "capability_router.py",
                "features": ["task_matching", "fallback_chains", "cost_optimization"]
            },
            "priority": 9
        },
        "B12": {
            "name": "registry_cost_governor",
            "type": "code_generation",
            "description": "Cost governance and budgeting",
            "data": {
                "output": "cost_governor.py",
                "features": ["budget_enforcement", "alerts", "usage_reports"]
            },
            "priority": 9
        },
        "B13": {
            "name": "registry_health_monitor",
            "type": "code_generation",
            "description": "Model health and availability monitor",
            "data": {
                "output": "health_monitor.py",
                "features": ["latency_tracking", "error_rates", "circuit_breaker"]
            },
            "priority": 8
        },
        "B14": {
            "name": "registry_graceful_degradation",
            "type": "code_generation",
            "description": "Graceful degradation strategies",
            "data": {
                "output": "graceful_degradation.py",
                "features": ["fallback_selection", "partial_results", "user_notification"]
            },
            "priority": 8
        },
        "B15": {
            "name": "registry_api_gateway",
            "type": "code_generation",
            "description": "Unified registry API gateway",
            "data": {
                "output": "registry_api_gateway.py",
                "features": ["request_routing", "response_caching", "rate_limiting"]
            },
            "priority": 7
        },

        # Integration Testing & Documentation (B16-B20)
        "B16": {
            "name": "emotion_security_tests",
            "type": "test_generation",
            "description": "IF.emotion security test suite",
            "data": {
                "targets": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"],
                "output": "test_emotion_security.py"
            },
            "priority": 6
        },
        "B17": {
            "name": "registry_integration_tests",
            "type": "test_generation",
            "description": "Claude Max registry test suite",
            "data": {
                "targets": ["B9", "B10", "B11", "B12", "B13", "B14", "B15"],
                "output": "test_claude_registry.py"
            },
            "priority": 6
        },
        "B18": {
            "name": "end_to_end_security_tests",
            "type": "test_generation",
            "description": "End-to-end security integration tests",
            "data": {
                "scope": "full_stack",
                "output": "test_e2e_security.py"
            },
            "priority": 5
        },
        "B19": {
            "name": "security_documentation",
            "type": "documentation",
            "description": "Security architecture documentation",
            "data": {
                "format": "markdown",
                "outputs": [
                    "EMOTION_SECURITY_ARCHITECTURE.md",
                    "CLAUDE_MAX_REGISTRY_GUIDE.md"
                ]
            },
            "priority": 5
        },
        "B20": {
            "name": "threat_model_report",
            "type": "security_analysis",
            "description": "Comprehensive threat model",
            "data": {
                "methodology": "STRIDE",
                "output": "THREAT_MODEL_REPORT.md"
            },
            "priority": 4
        }
    }

    def __init__(self,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 max_haiku_agents: int = 20):
        """Initialize Sonnet B coordinator."""
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.max_haiku_agents = max_haiku_agents
        self.coordinator: Optional[RedisSwarmCoordinator] = None
        self.agent_id: Optional[str] = None
        self.spawned_haikus: Dict[str, str] = {}
        self.task_status: Dict[str, str] = {}

    def connect(self) -> bool:
        """Connect to Redis and register as Sonnet B coordinator."""
        try:
            self.coordinator = RedisSwarmCoordinator(
                redis_host=self.redis_host,
                redis_port=self.redis_port,
                redis_db=0
            )

            self.agent_id = self.coordinator.register_agent(
                role="sonnet_b_security",
                context_capacity=200000,
                metadata={
                    "model": "claude-sonnet-4.5",
                    "purpose": "security_coordination",
                    "workstream": "B",
                    "tasks": list(self.TASKS.keys()),
                    "max_haiku_agents": self.max_haiku_agents,
                    "started_at": datetime.now().isoformat()
                }
            )

            print(f"[SONNET-B] Registered as: {self.agent_id}")
            return True
        except Exception as e:
            print(f"[SONNET-B] Connection failed: {e}")
            return False

    def dispatch_all_tasks(self) -> Dict[str, str]:
        """Dispatch all security tasks to Haiku queue."""
        if not self.coordinator:
            raise RuntimeError("Not connected")

        dispatched = {}

        for task_key, task_def in self.TASKS.items():
            task_id = self.coordinator.post_task(
                queue_name="haiku_security",
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

            print(f"[SONNET-B] Dispatched {task_key}: {task_def['name']} -> {task_id}")

        return dispatched

    def dispatch_security_layer(self, layer: int) -> Dict[str, str]:
        """Dispatch only specific security layer tasks."""
        layer_tasks = {k: v for k, v in self.TASKS.items()
                      if v.get("data", {}).get("layer") == layer}

        dispatched = {}
        for task_key, task_def in layer_tasks.items():
            task_id = self.coordinator.post_task(
                queue_name="haiku_security",
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

        return dispatched

    def monitor_progress(self, duration: int = 300) -> Dict:
        """Monitor task completion for specified duration."""
        if not self.coordinator:
            raise RuntimeError("Not connected")

        start_time = time.time()
        end_time = start_time + duration
        completed_count = 0

        print(f"\n[SONNET-B] Monitoring {len(self.TASKS)} tasks for {duration}s...")

        while time.time() < end_time:
            messages = self.coordinator.get_messages(limit=20)

            for msg in messages:
                content = msg.get('content', {})
                if content.get('type') == 'task_result':
                    task_id = content.get('task_id')
                    if task_id in self.task_status:
                        self.task_status[task_id] = "completed"
                        completed_count += 1
                        print(f"[SONNET-B] Task completed: {task_id}")

            if int(time.time()) % 10 == 0:
                pending = sum(1 for s in self.task_status.values() if s == "dispatched")
                print(f"[SONNET-B] Progress: {completed_count}/{len(self.TASKS)} complete, {pending} pending")

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
            "coordinator": "Sonnet B - Security",
            "agent_id": self.agent_id,
            "workstream": "B (B1-B20)",
            "focus_areas": [
                "IF.emotion Security Sandboxing (8 layers)",
                "Claude Max Registry",
                "Integration Testing & Documentation"
            ],
            "tasks_defined": len(self.TASKS),
            "task_status": dict(self.task_status),
            "spawned_haikus": len(self.spawned_haikus)
        }


def main():
    """Main entry point for Sonnet B coordinator."""
    import argparse

    parser = argparse.ArgumentParser(description='Sonnet B - Security Coordinator')
    parser.add_argument('--dispatch', action='store_true', help='Dispatch all tasks')
    parser.add_argument('--layer', type=int, help='Dispatch specific security layer (1-8)')
    parser.add_argument('--monitor', type=int, default=300, help='Monitor duration (seconds)')
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')

    args = parser.parse_args()

    coordinator = SonnetBCoordinator(
        redis_host=args.redis_host,
        redis_port=args.redis_port
    )

    if not coordinator.connect():
        print("[FATAL] Could not connect to Redis")
        sys.exit(1)

    if args.dispatch:
        print("\n[SONNET-B] Dispatching security tasks...")
        dispatched = coordinator.dispatch_all_tasks()
        print(f"\n[SONNET-B] Dispatched {len(dispatched)} tasks")

        print("\n[SONNET-B] Starting monitoring phase...")
        result = coordinator.monitor_progress(args.monitor)

        print(f"\n[SONNET-B] Final Results:")
        print(json.dumps(result, indent=2))
    elif args.layer:
        print(f"\n[SONNET-B] Dispatching Layer {args.layer} tasks...")
        dispatched = coordinator.dispatch_security_layer(args.layer)
        print(f"\n[SONNET-B] Dispatched {len(dispatched)} layer {args.layer} tasks")
    else:
        print("\n[SONNET-B] Task Definitions:")
        print("\n8-Layer IF.emotion Security:")
        for i in range(1, 9):
            task = [t for k, t in coordinator.TASKS.items() if t.get("data", {}).get("layer") == i]
            if task:
                t = task[0]
                print(f"  Layer {i}: {t['name']} - {t['description']}")

        print("\nClaude Max Registry:")
        for key in ["B9", "B10", "B11", "B12", "B13", "B14", "B15"]:
            t = coordinator.TASKS[key]
            print(f"  {key}: {t['name']} - {t['description']}")

        print("\nIntegration & Docs:")
        for key in ["B16", "B17", "B18", "B19", "B20"]:
            t = coordinator.TASKS[key]
            print(f"  {key}: {t['name']} - {t['description']}")

        print("\nRun with --dispatch to start task distribution")
        print("Run with --layer N to dispatch specific security layer")


if __name__ == '__main__':
    main()
