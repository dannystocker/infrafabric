"""
CLI Test Fixtures

Reusable test data and fixtures for all CLI command testing.
Provides mock data for witness, coordinator, governor, chassis, and optimise.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pytest


# ====================
# Witness Test Fixtures
# ====================

WITNESS_SAMPLE_ENTRIES = [
    {
        "id": 1,
        "timestamp": "2025-11-12T10:00:00Z",
        "event": "task_claimed",
        "component": "IF.coordinator",
        "trace_id": "trace-001",
        "payload": json.dumps({"swarm_id": "session-2-webrtc", "task_id": "build-ui"}),
        "hash": "abc123def456...",
        "prev_hash": "000000000000...",
        "signature": "ed25519:sig1..."
    },
    {
        "id": 2,
        "timestamp": "2025-11-12T10:01:30Z",
        "event": "capability_match",
        "component": "IF.governor",
        "trace_id": "trace-002",
        "payload": json.dumps({"swarm_id": "session-4-sip", "match_score": 0.85, "cost": 0.05}),
        "hash": "def456ghi789...",
        "prev_hash": "abc123def456...",
        "signature": "ed25519:sig2..."
    },
    {
        "id": 3,
        "timestamp": "2025-11-12T10:05:00Z",
        "event": "sandbox_created",
        "component": "IF.chassis",
        "trace_id": "trace-003",
        "payload": json.dumps({"sandbox_id": "sb-001", "memory_mb": 512, "cpu_percent": 50}),
        "hash": "ghi789jkl012...",
        "prev_hash": "def456ghi789...",
        "signature": "ed25519:sig3..."
    },
    {
        "id": 4,
        "timestamp": "2025-11-12T10:10:00Z",
        "event": "cost_tracked",
        "component": "IF.optimise",
        "trace_id": "trace-004",
        "payload": json.dumps({"model": "sonnet", "tokens_input": 5000, "tokens_output": 2000, "cost_usd": 0.45}),
        "hash": "jkl012mno345...",
        "prev_hash": "ghi789jkl012...",
        "signature": "ed25519:sig4..."
    },
    {
        "id": 5,
        "timestamp": "2025-11-12T10:15:00Z",
        "event": "task_completed",
        "component": "IF.coordinator",
        "trace_id": "trace-001",
        "payload": json.dumps({"swarm_id": "session-2-webrtc", "task_id": "build-ui", "duration_ms": 45000}),
        "hash": "mno345pqr678...",
        "prev_hash": "jkl012mno345...",
        "signature": "ed25519:sig5..."
    }
]


WITNESS_QUERY_FILTERS = {
    "by_component": {
        "component": "IF.coordinator",
        "expected_count": 2,
        "expected_ids": [1, 5]
    },
    "by_trace_id": {
        "trace_id": "trace-001",
        "expected_count": 2,
        "expected_ids": [1, 5]
    },
    "by_event": {
        "event": "capability_match",
        "expected_count": 1,
        "expected_ids": [2]
    },
    "by_date_range": {
        "start_date": "2025-11-12T10:05:00Z",
        "end_date": "2025-11-12T10:15:00Z",
        "expected_count": 3,
        "expected_ids": [3, 4, 5]
    }
}


WITNESS_SAMPLE_PAYLOADS = {
    "simple": {
        "description": "Simple key-value payload",
        "json": '{"key": "value", "count": 42}',
        "dict": {"key": "value", "count": 42}
    },
    "nested": {
        "description": "Nested object payload",
        "json": '{"user": {"id": 123, "name": "test"}, "metadata": {"tags": ["a", "b"]}}',
        "dict": {"user": {"id": 123, "name": "test"}, "metadata": {"tags": ["a", "b"]}}
    },
    "with_arrays": {
        "description": "Payload with arrays",
        "json": '{"items": [1, 2, 3], "names": ["alice", "bob"]}',
        "dict": {"items": [1, 2, 3], "names": ["alice", "bob"]}
    },
    "task_claim": {
        "description": "Task claim event payload",
        "json": '{"swarm_id": "session-7", "task_id": "P0.1.2", "latency_ms": 4.2}',
        "dict": {"swarm_id": "session-7", "task_id": "P0.1.2", "latency_ms": 4.2}
    },
    "cost_tracking": {
        "description": "Cost tracking payload",
        "json": '{"model": "haiku", "tokens_input": 1000, "tokens_output": 500, "cost_usd": 0.012, "cached": false}',
        "dict": {"model": "haiku", "tokens_input": 1000, "tokens_output": 500, "cost_usd": 0.012, "cached": False}
    }
}


WITNESS_INVALID_PAYLOADS = [
    {
        "description": "Missing closing brace",
        "json": '{"key": "value"',
        "error_type": "JSONDecodeError"
    },
    {
        "description": "Single quotes instead of double",
        "json": "{'key': 'value'}",
        "error_type": "JSONDecodeError"
    },
    {
        "description": "Trailing comma",
        "json": '{"key": "value",}',
        "error_type": "JSONDecodeError"
    },
    {
        "description": "Unquoted key",
        "json": '{key: "value"}',
        "error_type": "JSONDecodeError"
    }
]


# ====================
# Coordinator Test Fixtures
# ====================

COORDINATOR_SAMPLE_TASKS = [
    {
        "task_id": "P0.1.2",
        "description": "Implement atomic CAS operations",
        "required_capabilities": ["coordination:etcd", "python:async"],
        "estimated_time_hours": 2,
        "max_cost": 5.0,
        "status": "unclaimed"
    },
    {
        "task_id": "P0.2.3",
        "description": "Implement budget tracking",
        "required_capabilities": ["governance:budget", "python:dataclass"],
        "estimated_time_hours": 1.5,
        "max_cost": 3.0,
        "status": "claimed",
        "owner": "session-4-sip"
    },
    {
        "task_id": "P0.3.1",
        "description": "Implement WASM runtime",
        "required_capabilities": ["wasm:wasmtime", "rust:integration"],
        "estimated_time_hours": 3,
        "max_cost": 10.0,
        "status": "completed",
        "owner": "session-3-h323"
    }
]


COORDINATOR_CAS_SCENARIOS = [
    {
        "name": "successful_claim",
        "initial_state": "unclaimed",
        "claim_swarm": "session-1",
        "expected_result": True,
        "expected_final_state": "session-1"
    },
    {
        "name": "race_condition",
        "initial_state": "unclaimed",
        "claim_swarms": ["session-1", "session-2"],
        "expected_winners": 1,
        "expected_losers": 1
    },
    {
        "name": "already_claimed",
        "initial_state": "session-2",
        "claim_swarm": "session-1",
        "expected_result": False,
        "expected_final_state": "session-2"
    }
]


# ====================
# Governor Test Fixtures
# ====================

GOVERNOR_SAMPLE_SWARMS = [
    {
        "swarm_id": "session-1-ndi",
        "capabilities": ["streaming:ndi", "video:production", "cli:design"],
        "cost_per_hour": 2.0,
        "reputation_score": 0.95,
        "budget_remaining": 80.0,
        "model": "haiku"
    },
    {
        "swarm_id": "session-2-webrtc",
        "capabilities": ["streaming:webrtc", "integration:testing", "python:async"],
        "cost_per_hour": 18.0,
        "reputation_score": 0.88,
        "budget_remaining": 120.0,
        "model": "sonnet"
    },
    {
        "swarm_id": "session-4-sip",
        "capabilities": ["governance:budget", "governance:circuit-breaker", "python:dataclass"],
        "cost_per_hour": 15.0,
        "reputation_score": 0.92,
        "budget_remaining": 50.0,
        "model": "sonnet"
    },
    {
        "swarm_id": "session-7-if-bus",
        "capabilities": ["coordination:etcd", "python:async", "architecture:patterns"],
        "cost_per_hour": 20.0,
        "reputation_score": 0.85,
        "budget_remaining": 10.0,
        "model": "sonnet"
    }
]


GOVERNOR_CAPABILITY_MATCH_SCENARIOS = [
    {
        "name": "perfect_match",
        "required": ["streaming:ndi", "video:production"],
        "swarm": "session-1-ndi",
        "expected_match_score": 1.0
    },
    {
        "name": "partial_match",
        "required": ["streaming:ndi", "integration:testing", "cli:design"],
        "swarm": "session-1-ndi",
        "expected_match_score": 0.667  # 2 out of 3
    },
    {
        "name": "no_match",
        "required": ["rust:integration", "wasm:wasmtime"],
        "swarm": "session-1-ndi",
        "expected_match_score": 0.0
    },
    {
        "name": "below_threshold",
        "required": ["coordination:etcd", "rust:integration", "wasm:wasmtime"],
        "swarm": "session-7-if-bus",
        "expected_match_score": 0.333,  # 1 out of 3
        "below_threshold": True  # < 0.7
    }
]


GOVERNOR_BUDGET_SCENARIOS = [
    {
        "name": "sufficient_budget",
        "swarm_id": "session-2-webrtc",
        "operation_cost": 5.0,
        "expected_allowed": True,
        "expected_remaining": 115.0
    },
    {
        "name": "exhausted_budget",
        "swarm_id": "session-7-if-bus",
        "operation_cost": 15.0,
        "expected_allowed": False,
        "expected_circuit_breaker": True
    },
    {
        "name": "budget_alert",
        "swarm_id": "session-7-if-bus",
        "operation_cost": 5.0,
        "expected_allowed": True,
        "expected_remaining": 5.0,
        "expected_alert": True  # Below 10% threshold
    }
]


# ====================
# Chassis Test Fixtures
# ====================

CHASSIS_SAMPLE_SANDBOXES = [
    {
        "sandbox_id": "sb-001",
        "wasm_module": "yologuard.wasm",
        "memory_mb": 256,
        "cpu_percent": 25,
        "max_execution_time_ms": 60000,
        "status": "running"
    },
    {
        "sandbox_id": "sb-002",
        "wasm_module": "transformer.wasm",
        "memory_mb": 512,
        "cpu_percent": 50,
        "max_execution_time_ms": 120000,
        "status": "completed"
    },
    {
        "sandbox_id": "sb-003",
        "wasm_module": "validator.wasm",
        "memory_mb": 128,
        "cpu_percent": 10,
        "max_execution_time_ms": 30000,
        "status": "failed",
        "error": "Timeout exceeded"
    }
]


CHASSIS_RESOURCE_LIMIT_SCENARIOS = [
    {
        "name": "within_limits",
        "memory_mb": 256,
        "cpu_percent": 25,
        "execution_time_ms": 5000,
        "expected_allowed": True
    },
    {
        "name": "memory_exceeded",
        "memory_mb": 1024,
        "cpu_percent": 25,
        "execution_time_ms": 5000,
        "expected_allowed": False,
        "expected_error": "Memory limit exceeded"
    },
    {
        "name": "cpu_exceeded",
        "memory_mb": 256,
        "cpu_percent": 80,
        "execution_time_ms": 5000,
        "expected_allowed": False,
        "expected_error": "CPU limit exceeded"
    },
    {
        "name": "timeout",
        "memory_mb": 256,
        "cpu_percent": 25,
        "execution_time_ms": 400000,  # > 5 minutes
        "expected_allowed": False,
        "expected_error": "Execution timeout"
    }
]


CHASSIS_SAMPLE_CREDENTIALS = [
    {
        "credential_id": "cred-001",
        "service": "github",
        "scope": "read:repo",
        "expiry": (datetime.utcnow() + timedelta(days=90)).isoformat()
    },
    {
        "credential_id": "cred-002",
        "service": "aws-s3",
        "scope": "read:bucket/yologuard-*",
        "expiry": (datetime.utcnow() + timedelta(days=30)).isoformat()
    },
    {
        "credential_id": "cred-003",
        "service": "anthropic-api",
        "scope": "api:messages",
        "expiry": (datetime.utcnow() + timedelta(days=365)).isoformat()
    }
]


# ====================
# Optimise Test Fixtures
# ====================

OPTIMISE_SAMPLE_OPERATIONS = [
    {
        "operation_id": "op-001",
        "model": "haiku",
        "tokens_input": 1000,
        "tokens_output": 500,
        "cache_hit": False,
        "cost_usd": 0.012,
        "latency_ms": 450
    },
    {
        "operation_id": "op-002",
        "model": "sonnet",
        "tokens_input": 5000,
        "tokens_output": 2000,
        "cache_hit": True,
        "cost_usd": 0.045,  # 90% discount from cache
        "latency_ms": 120
    },
    {
        "operation_id": "op-003",
        "model": "opus",
        "tokens_input": 10000,
        "tokens_output": 5000,
        "cache_hit": False,
        "cost_usd": 5.25,
        "latency_ms": 2500
    }
]


OPTIMISE_COST_SCENARIOS = [
    {
        "name": "under_budget",
        "total_budget": 100.0,
        "operations_cost": 45.0,
        "expected_alert": False,
        "expected_remaining": 55.0
    },
    {
        "name": "budget_warning",
        "total_budget": 100.0,
        "operations_cost": 85.0,
        "expected_alert": True,  # > 80% threshold
        "expected_remaining": 15.0
    },
    {
        "name": "budget_exceeded",
        "total_budget": 100.0,
        "operations_cost": 110.0,
        "expected_alert": True,
        "expected_remaining": -10.0,
        "expected_circuit_breaker": True
    }
]


# ====================
# Config Test Fixtures
# ====================

SAMPLE_CONFIG_YAML = """
config_version: "1.0"
log_level: debug
enable_telemetry: true

coordinator:
  backend: etcd
  etcd_host: localhost
  etcd_port: 2379
  target_cas_latency_ms: 5
  witness_enabled: true

governor:
  min_capability_match: 0.7
  default_budget_per_swarm: 100.0
  failure_threshold: 3

chassis:
  wasm_runtime: wasmtime
  max_memory_mb: 512
  max_cpu_percent: 50

witness:
  db_path: ~/.if-witness/witness.db
  hash_algorithm: SHA-256
  retention_days: 365

optimise:
  track_token_costs: true
  enable_caching: true
"""


INVALID_CONFIG_SAMPLES = [
    {
        "name": "invalid_backend",
        "yaml": "coordinator:\n  backend: invalid",
        "expected_error": "Invalid backend"
    },
    {
        "name": "invalid_port",
        "yaml": "coordinator:\n  etcd_port: 99999",
        "expected_error": "Invalid etcd_port"
    },
    {
        "name": "invalid_capability_match",
        "yaml": "governor:\n  min_capability_match: 1.5",
        "expected_error": "must be between 0 and 1"
    }
]


# ====================
# Pytest Fixtures
# ====================

@pytest.fixture
def witness_entries():
    """Provide sample witness entries"""
    return WITNESS_SAMPLE_ENTRIES.copy()


@pytest.fixture
def witness_payloads():
    """Provide sample payloads"""
    return WITNESS_SAMPLE_PAYLOADS.copy()


@pytest.fixture
def coordinator_tasks():
    """Provide sample coordinator tasks"""
    return COORDINATOR_SAMPLE_TASKS.copy()


@pytest.fixture
def governor_swarms():
    """Provide sample swarm profiles"""
    return GOVERNOR_SAMPLE_SWARMS.copy()


@pytest.fixture
def chassis_sandboxes():
    """Provide sample sandboxes"""
    return CHASSIS_SAMPLE_SANDBOXES.copy()


@pytest.fixture
def optimise_operations():
    """Provide sample operations"""
    return OPTIMISE_SAMPLE_OPERATIONS.copy()


@pytest.fixture
def temp_config_file():
    """Create temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(SAMPLE_CONFIG_YAML)
        config_path = Path(f.name)

    yield config_path

    # Cleanup
    config_path.unlink()


@pytest.fixture
def temp_witness_db():
    """Create temporary witness database"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)

    yield db_path

    # Cleanup
    if db_path.exists():
        db_path.unlink()


# ====================
# Test Helpers
# ====================

def create_sample_witness_entry(
    event: str,
    component: str,
    trace_id: str,
    payload: Dict[str, Any],
    entry_id: int = 1
) -> Dict[str, Any]:
    """Create a sample witness entry with provided values"""
    return {
        "id": entry_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        "component": component,
        "trace_id": trace_id,
        "payload": json.dumps(payload),
        "hash": f"hash{entry_id:03d}...",
        "prev_hash": f"hash{entry_id-1:03d}..." if entry_id > 1 else "000000...",
        "signature": f"ed25519:sig{entry_id}..."
    }


def create_sample_swarm_profile(
    swarm_id: str,
    capabilities: List[str],
    cost_per_hour: float = 15.0,
    reputation: float = 0.9,
    budget: float = 100.0
) -> Dict[str, Any]:
    """Create a sample swarm profile"""
    return {
        "swarm_id": swarm_id,
        "capabilities": capabilities,
        "cost_per_hour": cost_per_hour,
        "reputation_score": reputation,
        "budget_remaining": budget,
        "model": "sonnet" if cost_per_hour > 10 else "haiku"
    }


def create_sample_task(
    task_id: str,
    required_capabilities: List[str],
    status: str = "unclaimed",
    owner: str = None
) -> Dict[str, Any]:
    """Create a sample task"""
    task = {
        "task_id": task_id,
        "description": f"Task {task_id}",
        "required_capabilities": required_capabilities,
        "estimated_time_hours": 2,
        "max_cost": 10.0,
        "status": status
    }
    if owner:
        task["owner"] = owner
    return task
