"""
Cross-Session Test Fixtures - IFMessage Mocks

Reusable test fixtures for IF.bus message patterns used across all InfraFabric
components. Enables consistent testing of message-based communication.

Components Covered:
- IF.coordinator: Task coordination messages
- IF.executor: Command execution messages
- IF.proxy: API proxy messages
- IF.governor: Resource allocation messages
- IF.witness: Audit log messages

Usage:
    from tests.fixtures.if_messages import (
        coordinator_task_claim_msg,
        executor_command_msg,
        proxy_request_msg
    )

    def test_my_component():
        msg = coordinator_task_claim_msg()
        # Test with realistic message
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


# ============================================================================
# IF.coordinator Message Fixtures
# ============================================================================

def coordinator_task_claim_msg(
    task_id: str = 'task-123',
    swarm_id: str = 'swarm-finance',
    task_type: str = 'code-review',
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Task claim message for IF.coordinator

    Example:
        msg = coordinator_task_claim_msg()
        success = await coordinator.claim_task(msg['swarm_id'], msg['task_id'])
    """
    return {
        'task_id': task_id,
        'swarm_id': swarm_id,
        'task_type': task_type,
        'metadata': metadata or {'pr_url': 'https://github.com/org/repo/pull/123'},
        'timestamp': time.time()
    }


def coordinator_task_push_msg(
    task_id: str = 'task-456',
    swarm_id: str = 'swarm-infrastructure',
    task_type: str = 'integration-test',
    priority: str = 'high',
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Task push message for IF.coordinator (pub/sub)

    Example:
        msg = coordinator_task_push_msg()
        await coordinator.push_task_to_swarm(msg['swarm_id'], msg)
    """
    return {
        'task_id': task_id,
        'task_type': task_type,
        'priority': priority,
        'metadata': metadata or {'test_suite': 'integration', 'timeout': 300},
        'assigned_at': time.time()
    }


def coordinator_blocker_msg(
    blocked_swarm_id: str = 'swarm-session-4',
    task_id: str = 'task-blocked-789',
    blocker_type: str = 'capability_gap',
    required_capabilities: Optional[List[str]] = None,
    description: str = 'Complex Rust concurrency issue in SIP adapter'
) -> Dict[str, Any]:
    """
    Blocker detection message for IF.coordinator

    Example:
        msg = coordinator_blocker_msg()
        await coordinator.detect_blocker(msg['swarm_id'], msg)
    """
    return {
        'swarm_id': blocked_swarm_id,
        'task_id': task_id,
        'blocker_type': blocker_type,
        'required_capabilities': required_capabilities or [
            'code-analysis:rust',
            'infra:distributed-systems'
        ],
        'description': description,
        'urgency': 'high',
        'detected_at': time.time()
    }


def coordinator_swarm_registration_msg(
    swarm_id: str = 'swarm-session-2',
    capabilities: Optional[List[str]] = None,
    model: str = 'sonnet',
    cost_per_hour: float = 15.0,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Swarm registration message for IF.coordinator

    Example:
        msg = coordinator_swarm_registration_msg()
        await coordinator.register_swarm(msg['swarm_id'], msg['capabilities'], msg['metadata'])
    """
    return {
        'swarm_id': swarm_id,
        'capabilities': capabilities or [
            'integration:webrtc',
            'code-analysis:python',
            'infra:distributed-systems'
        ],
        'model': model,
        'cost_per_hour': cost_per_hour,
        'metadata': metadata or {
            'session': 'session-2-webrtc',
            'branch': 'claude/webrtc-final-push-011CV2nnsyHT4by1am1ZrkkA'
        },
        'registered_at': time.time()
    }


# ============================================================================
# IF.executor Message Fixtures
# ============================================================================

def executor_command_msg(
    trace_id: str = 'trace-exec-123',
    swarm_id: str = 'navidocs-adapter',
    executable: str = '/usr/bin/systemctl',
    args: Optional[List[str]] = None,
    timeout_ms: int = 5000
) -> Dict[str, Any]:
    """
    Command execution request for IF.executor

    Example:
        msg = executor_command_msg()
        await executor._handle_execute_request(event_with_msg(msg))
    """
    return {
        'trace_id': trace_id,
        'swarm_id': swarm_id,
        'executable': executable,
        'args': args or ['status', 'meilisearch'],
        'timeout_ms': timeout_ms
    }


def executor_command_result_msg(
    trace_id: str = 'trace-exec-123',
    success: bool = True,
    exit_code: int = 0,
    stdout: Optional[str] = '● meilisearch.service - Meilisearch\n   Active: active (running)',
    stderr: Optional[str] = None,
    execution_time_ms: float = 45.2
) -> Dict[str, Any]:
    """
    Command execution result from IF.executor

    Example:
        msg = executor_command_result_msg()
        # Verify result format
    """
    return {
        'trace_id': trace_id,
        'success': success,
        'exit_code': exit_code,
        'stdout': stdout,
        'stderr': stderr,
        'execution_time_ms': execution_time_ms
    }


def executor_pgrep_msg(
    trace_id: str = 'trace-pgrep-456',
    swarm_id: str = 'navidocs-adapter',
    process_name: str = 'meilisearch'
) -> Dict[str, Any]:
    """
    Process check command for IF.executor

    Example:
        msg = executor_pgrep_msg()
        # Check if Meilisearch is running
    """
    return {
        'trace_id': trace_id,
        'swarm_id': swarm_id,
        'executable': '/usr/bin/pgrep',
        'args': ['-f', process_name],
        'timeout_ms': 3000
    }


def executor_service_control_msg(
    trace_id: str = 'trace-service-789',
    swarm_id: str = 'navidocs-adapter',
    action: str = 'start',
    service: str = 'meilisearch'
) -> Dict[str, Any]:
    """
    Service control command for IF.executor

    Example:
        msg = executor_service_control_msg(action='restart')
        # Restart Meilisearch service
    """
    return {
        'trace_id': trace_id,
        'swarm_id': swarm_id,
        'executable': '/usr/bin/systemctl',
        'args': [action, service],
        'timeout_ms': 30000  # Service operations can be slow
    }


# ============================================================================
# IF.proxy Message Fixtures
# ============================================================================

def proxy_request_msg(
    trace_id: str = 'trace-proxy-123',
    swarm_id: str = 'navidocs-adapter',
    target_alias: str = 'meilisearch_api',
    method: str = 'POST',
    path: str = '/indexes/navidocs/documents',
    headers: Optional[Dict[str, str]] = None,
    body: Optional[str] = None,
    timeout_ms: int = 10000
) -> Dict[str, Any]:
    """
    API proxy request for IF.proxy

    Example:
        msg = proxy_request_msg()
        await proxy._handle_proxy_request(event_with_msg(msg))
    """
    return {
        'trace_id': trace_id,
        'swarm_id': swarm_id,
        'target_alias': target_alias,
        'method': method,
        'path': path,
        'headers': headers or {'Content-Type': 'application/json'},
        'body': body or '{"id": 1, "title": "Test Document", "content": "Lorem ipsum"}',
        'timeout_ms': timeout_ms
    }


def proxy_result_msg(
    trace_id: str = 'trace-proxy-123',
    success: bool = True,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    body: Optional[str] = None,
    request_time_ms: float = 123.4
) -> Dict[str, Any]:
    """
    API proxy result from IF.proxy

    Example:
        msg = proxy_result_msg()
        # Verify response format
    """
    return {
        'trace_id': trace_id,
        'success': success,
        'status_code': status_code,
        'headers': headers or {'Content-Type': 'application/json'},
        'body': body or '{"uid": 1, "status": "processed"}',
        'request_time_ms': request_time_ms
    }


def proxy_meilisearch_index_msg(
    trace_id: str = 'trace-meilisearch-456',
    swarm_id: str = 'navidocs-adapter',
    index_name: str = 'navidocs',
    documents: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Meilisearch indexing request via IF.proxy

    Example:
        msg = proxy_meilisearch_index_msg()
        # Index documents in Meilisearch
    """
    return {
        'trace_id': trace_id,
        'swarm_id': swarm_id,
        'target_alias': 'meilisearch_api',
        'method': 'POST',
        'path': f'/indexes/{index_name}/documents',
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(documents or [
            {'id': 1, 'title': 'Document 1', 'content': 'First document'},
            {'id': 2, 'title': 'Document 2', 'content': 'Second document'}
        ]),
        'timeout_ms': 15000
    }


def proxy_home_assistant_msg(
    trace_id: str = 'trace-ha-789',
    swarm_id: str = 'ha-adapter',
    entity_id: str = 'light.living_room',
    action: str = 'turn_on'
) -> Dict[str, Any]:
    """
    Home Assistant control request via IF.proxy

    Example:
        msg = proxy_home_assistant_msg(action='turn_off')
        # Control Home Assistant device
    """
    return {
        'trace_id': trace_id,
        'swarm_id': swarm_id,
        'target_alias': 'home_assistant_api',
        'method': 'POST',
        'path': f'/api/services/light/{action}',
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'entity_id': entity_id}),
        'timeout_ms': 5000
    }


# ============================================================================
# IF.governor Message Fixtures
# ============================================================================

def governor_capability_match_msg(
    required_capabilities: Optional[List[str]] = None,
    max_cost: float = 20.0,
    task_description: str = 'Code review for SIP integration'
) -> Dict[str, Any]:
    """
    Capability matching request for IF.governor

    Example:
        msg = governor_capability_match_msg()
        swarm_id = governor.find_qualified_swarm(msg['required_capabilities'], msg['max_cost'])
    """
    return {
        'required_capabilities': required_capabilities or [
            'integration:sip',
            'code-analysis:python'
        ],
        'max_cost': max_cost,
        'task_description': task_description
    }


def governor_budget_tracking_msg(
    swarm_id: str = 'swarm-session-4',
    operation: str = 'code_review',
    cost: float = 7.50,
    duration_minutes: int = 30
) -> Dict[str, Any]:
    """
    Cost tracking message for IF.governor

    Example:
        msg = governor_budget_tracking_msg()
        governor.track_cost(msg['swarm_id'], msg['operation'], msg['cost'])
    """
    return {
        'swarm_id': swarm_id,
        'operation': operation,
        'cost': cost,
        'duration_minutes': duration_minutes,
        'model': 'sonnet',
        'timestamp': time.time()
    }


def governor_help_request_msg(
    blocked_swarm_id: str = 'swarm-session-4',
    task_id: str = 'task-blocked-123',
    required_capabilities: Optional[List[str]] = None,
    description: str = 'Need Rust expert for concurrency issue',
    urgency: str = 'high'
) -> Dict[str, Any]:
    """
    Help request message for IF.governor (Gang Up on Blocker)

    Example:
        msg = governor_help_request_msg()
        helpers = await governor.request_help_for_blocker(msg['blocked_swarm_id'], msg)
    """
    return {
        'blocked_swarm_id': blocked_swarm_id,
        'task_id': task_id,
        'required_capabilities': required_capabilities or [
            'code-analysis:rust',
            'infra:distributed-systems'
        ],
        'description': description,
        'urgency': urgency,
        'max_helpers': 3,
        'max_cost_per_helper': 10.0
    }


def governor_swarm_profile_msg(
    swarm_id: str = 'swarm-session-2',
    capabilities: Optional[List[str]] = None,
    cost_per_hour: float = 15.0,
    reputation_score: float = 0.95,
    current_budget_remaining: float = 50.0,
    model: str = 'sonnet'
) -> Dict[str, Any]:
    """
    Swarm profile for IF.governor registration

    Example:
        msg = governor_swarm_profile_msg()
        governor.register_swarm(SwarmProfile(**msg))
    """
    return {
        'swarm_id': swarm_id,
        'capabilities': capabilities or [
            'integration:webrtc',
            'code-analysis:python',
            'infra:distributed-systems'
        ],
        'cost_per_hour': cost_per_hour,
        'reputation_score': reputation_score,
        'current_budget_remaining': current_budget_remaining,
        'model': model
    }


# ============================================================================
# IF.witness Message Fixtures
# ============================================================================

def witness_log_entry_msg(
    component: str = 'IF.coordinator',
    operation: str = 'task_claimed',
    swarm_id: str = 'swarm-finance',
    task_id: str = 'task-123',
    extra: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Witness log entry for IF.witness audit trail

    Example:
        msg = witness_log_entry_msg()
        witness_logger.log(msg)
    """
    return {
        'component': component,
        'operation': operation,
        'timestamp': time.time(),
        'swarm_id': swarm_id,
        'task_id': task_id,
        **(extra or {})
    }


def witness_executor_log_msg(
    swarm_id: str = 'navidocs-adapter',
    executable: str = '/usr/bin/systemctl',
    args: Optional[List[str]] = None,
    exit_code: int = 0,
    execution_time_ms: float = 45.2
) -> Dict[str, Any]:
    """
    Executor operation log for IF.witness

    Example:
        msg = witness_executor_log_msg()
        witness_logger.log(msg)
    """
    return {
        'component': 'IF.executor',
        'operation': 'command_executed',
        'timestamp': time.time(),
        'swarm_id': swarm_id,
        'executable': executable,
        'args': args or ['status', 'meilisearch'],
        'exit_code': exit_code,
        'execution_time_ms': execution_time_ms
    }


def witness_proxy_log_msg(
    swarm_id: str = 'navidocs-adapter',
    target_alias: str = 'meilisearch_api',
    method: str = 'POST',
    path: str = '/indexes/navidocs/documents',
    status_code: int = 200,
    request_time_ms: float = 123.4
) -> Dict[str, Any]:
    """
    Proxy operation log for IF.witness

    Example:
        msg = witness_proxy_log_msg()
        witness_logger.log(msg)
    """
    return {
        'component': 'IF.proxy',
        'operation': 'request_completed',
        'timestamp': time.time(),
        'swarm_id': swarm_id,
        'target_alias': target_alias,
        'method': method,
        'path': path,
        'status_code': status_code,
        'request_time_ms': request_time_ms
    }


# ============================================================================
# Common Test Utilities
# ============================================================================

def event_with_msg(msg: Dict[str, Any], event_type: str = 'put') -> Any:
    """
    Wrap message in EventBus WatchEvent format

    Example:
        event = event_with_msg(executor_command_msg())
        await executor._handle_execute_request(event)
    """
    from dataclasses import dataclass

    @dataclass
    class WatchEvent:
        key: str
        value: str
        event_type: str
        mod_revision: int

    return WatchEvent(
        key='test-key',
        value=json.dumps(msg),
        event_type=event_type,
        mod_revision=1
    )


def mock_etcd_response(value: Optional[str] = None) -> str:
    """
    Mock etcd get() response

    Example:
        mock_event_bus.get.return_value = mock_etcd_response('{"task_id": "task-123"}')
    """
    return value if value is not None else json.dumps({'status': 'ok'})


def mock_witness_logger():
    """
    Mock IF.witness logger for testing

    Example:
        witness = mock_witness_logger()
        coordinator = IFCoordinator(event_bus, witness_logger=witness)
        # Check logs: witness.events
    """
    class MockWitnessLogger:
        def __init__(self):
            self.events = []

        def log(self, entry):
            self.events.append(entry)

    return MockWitnessLogger()


# ============================================================================
# Batch Fixtures for Integration Tests
# ============================================================================

def coordinator_full_workflow_msgs():
    """
    Complete task workflow messages for integration testing

    Returns: (registration_msg, task_msg, claim_msg, complete_msg)

    Example:
        reg, task, claim, complete = coordinator_full_workflow_msgs()
        await coordinator.register_swarm(**reg)
        task_id = await coordinator.create_task(task)
        success = await coordinator.claim_task(claim['swarm_id'], task_id)
        await coordinator.complete_task(complete['swarm_id'], task_id, complete['result'])
    """
    swarm_id = 'swarm-integration-test'
    task_id = 'task-integration-123'

    return (
        coordinator_swarm_registration_msg(swarm_id=swarm_id),
        coordinator_task_claim_msg(task_id=task_id, swarm_id=swarm_id),
        {'swarm_id': swarm_id, 'task_id': task_id},
        {'swarm_id': swarm_id, 'task_id': task_id, 'result': {'status': 'success'}}
    )


def executor_policy_test_msgs():
    """
    Executor policy validation test messages

    Returns: (allowed_msg, denied_msg, pattern_match_msg, pattern_fail_msg)

    Example:
        allowed, denied, match, fail = executor_policy_test_msgs()
        # Test policy enforcement with various scenarios
    """
    return (
        executor_command_msg(executable='/usr/bin/systemctl', args=['status', 'meilisearch']),
        executor_command_msg(executable='/bin/rm', args=['-rf', '/']),
        executor_command_msg(executable='/usr/bin/pgrep', args=['-f', 'meilisearch']),
        executor_command_msg(executable='/usr/bin/pgrep', args=['--invalid-pattern'])
    )


def proxy_target_test_msgs():
    """
    Proxy target validation test messages

    Returns: (allowed_msg, wrong_target_msg, wrong_path_msg, wrong_swarm_msg)

    Example:
        allowed, wrong_target, wrong_path, wrong_swarm = proxy_target_test_msgs()
        # Test target/path validation
    """
    return (
        proxy_request_msg(
            swarm_id='navidocs-adapter',
            target_alias='meilisearch_api',
            path='/indexes/navidocs/documents'
        ),
        proxy_request_msg(
            swarm_id='navidocs-adapter',
            target_alias='nonexistent_api',
            path='/any/path'
        ),
        proxy_request_msg(
            swarm_id='navidocs-adapter',
            target_alias='meilisearch_api',
            path='/admin/delete-all'  # Not in allow-list
        ),
        proxy_request_msg(
            swarm_id='unauthorized-swarm',
            target_alias='meilisearch_api',
            path='/indexes/navidocs/documents'
        )
    )


# ============================================================================
# Export All Fixtures
# ============================================================================

__all__ = [
    # IF.coordinator
    'coordinator_task_claim_msg',
    'coordinator_task_push_msg',
    'coordinator_blocker_msg',
    'coordinator_swarm_registration_msg',
    'coordinator_full_workflow_msgs',

    # IF.executor
    'executor_command_msg',
    'executor_command_result_msg',
    'executor_pgrep_msg',
    'executor_service_control_msg',
    'executor_policy_test_msgs',

    # IF.proxy
    'proxy_request_msg',
    'proxy_result_msg',
    'proxy_meilisearch_index_msg',
    'proxy_home_assistant_msg',
    'proxy_target_test_msgs',

    # IF.governor
    'governor_capability_match_msg',
    'governor_budget_tracking_msg',
    'governor_help_request_msg',
    'governor_swarm_profile_msg',

    # IF.witness
    'witness_log_entry_msg',
    'witness_executor_log_msg',
    'witness_proxy_log_msg',

    # Utilities
    'event_with_msg',
    'mock_etcd_response',
    'mock_witness_logger'
]
