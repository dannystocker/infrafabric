"""
Unit Tests for IF.proxy - Policy-Governed External API Proxy

Tests cover:
- HTTP proxy requests (GET, POST, PUT, DELETE)
- Target alias resolution
- Path validation (allow-list)
- Capability checking
- Timeout enforcement
- IF.witness logging
- Error handling
- Registry loading
- Security boundary enforcement
"""

import pytest
import asyncio
import json
import time
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pathlib import Path
from aiohttp import ClientSession, ClientResponse

from infrafabric.proxy import (
    IFProxy,
    ProxyResult,
    TargetConfig,
    SwarmPathPolicy,
    ProxyError,
    TargetNotFoundError,
    PathNotAllowedError,
    TimeoutError
)
from infrafabric.event_bus import EventBus, WatchEvent


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_event_bus():
    """Mock EventBus for testing"""
    bus = AsyncMock(spec=EventBus)
    bus.watch = AsyncMock(return_value='watch-123')
    bus.get = AsyncMock()
    bus.put = AsyncMock()
    return bus


@pytest.fixture
def mock_witness_logger():
    """Mock IF.witness logger"""
    logger = Mock()
    logger.events = []
    return logger


@pytest.fixture
def sample_registry(tmp_path):
    """Create sample registry file"""
    registry = {
        'meilisearch_api': {
            'alias': 'meilisearch_api',
            'base_url': 'http://127.0.0.1:7700',
            'allowed_swarms': {
                'navidocs-adapter': {
                    'swarm_id': 'navidocs-adapter',
                    'paths': ['/indexes/navidocs/.*', '/health']
                }
            },
            'default_timeout_ms': 10000,
            'max_timeout_ms': 60000
        },
        'home_assistant_api': {
            'alias': 'home_assistant_api',
            'base_url': 'http://homeassistant.local:8123',
            'allowed_swarms': {
                'ha-adapter': {
                    'swarm_id': 'ha-adapter',
                    'paths': ['/api/.*']
                }
            },
            'default_timeout_ms': 10000,
            'max_timeout_ms': 60000
        }
    }

    registry_file = tmp_path / 'proxy_registry.json'
    with open(registry_file, 'w') as f:
        json.dump(registry, f)

    return str(registry_file)


@pytest.fixture
async def proxy(mock_event_bus, mock_witness_logger, sample_registry):
    """IF.proxy instance with mocked dependencies"""
    proxy = IFProxy(
        event_bus=mock_event_bus,
        registry_path=sample_registry,
        witness_logger=mock_witness_logger
    )
    return proxy


# ============================================================================
# Service Lifecycle Tests
# ============================================================================

@pytest.mark.asyncio
async def test_proxy_start(proxy, mock_event_bus):
    """Test IF.proxy service start subscribes to command topic"""
    await proxy.start()

    mock_event_bus.watch.assert_called_once()
    call_args = mock_event_bus.watch.call_args

    assert call_args[0][0] == 'if.command.network.proxy'
    assert callable(call_args[1]['callback'])
    assert proxy._watch_id == 'watch-123'
    assert proxy._session is not None


@pytest.mark.asyncio
async def test_proxy_stop(proxy):
    """Test IF.proxy service stop"""
    # Create a mock session
    proxy._session = AsyncMock()
    proxy._watch_id = 'watch-123'

    await proxy.stop()

    proxy._session.close.assert_called_once()


# ============================================================================
# Registry Loading Tests
# ============================================================================

@pytest.mark.asyncio
async def test_load_registry_success(proxy):
    """Test loading valid registry file"""
    await proxy._load_registry()

    assert len(proxy._registry) == 2
    assert 'meilisearch_api' in proxy._registry
    assert 'home_assistant_api' in proxy._registry

    # Check meilisearch config
    meilisearch = proxy._registry['meilisearch_api']
    assert meilisearch.base_url == 'http://127.0.0.1:7700'
    assert 'navidocs-adapter' in meilisearch.allowed_swarms
    assert meilisearch.default_timeout_ms == 10000


@pytest.mark.asyncio
async def test_load_registry_file_not_found(mock_event_bus, mock_witness_logger):
    """Test loading registry when file doesn't exist"""
    proxy = IFProxy(
        event_bus=mock_event_bus,
        registry_path='/nonexistent/registry.json',
        witness_logger=mock_witness_logger
    )

    await proxy._load_registry()

    # Should handle gracefully
    assert len(proxy._registry) == 0


@pytest.mark.asyncio
async def test_add_target_programmatically(proxy):
    """Test adding target to registry programmatically"""
    proxy.add_target(
        alias='test_api',
        base_url='http://test.local:8080',
        swarm_policies={
            'test-swarm': ['/api/.*', '/health']
        },
        default_timeout_ms=5000,
        max_timeout_ms=30000
    )

    assert 'test_api' in proxy._registry
    target = proxy._registry['test_api']
    assert target.base_url == 'http://test.local:8080'
    assert 'test-swarm' in target.allowed_swarms


# ============================================================================
# Target Resolution Tests
# ============================================================================

def test_get_target_success(proxy):
    """Test resolving known target alias"""
    proxy._registry['test_api'] = TargetConfig(
        alias='test_api',
        base_url='http://test.local',
        allowed_swarms={}
    )

    target = proxy._get_target('test_api')

    assert target.alias == 'test_api'
    assert target.base_url == 'http://test.local'


def test_get_target_not_found(proxy):
    """Test resolving unknown target alias fails"""
    with pytest.raises(TargetNotFoundError, match='Unknown target alias'):
        proxy._get_target('nonexistent_api')


# ============================================================================
# Path Validation Tests
# ============================================================================

def test_validate_path_allowed_exact_match(proxy):
    """Test path validation allows exact match"""
    policy = SwarmPathPolicy(
        swarm_id='test-swarm',
        paths=['/health', '/status']
    )

    result = proxy._validate_path(policy, '/health')

    assert result is True


def test_validate_path_allowed_pattern_match(proxy):
    """Test path validation allows pattern match"""
    policy = SwarmPathPolicy(
        swarm_id='test-swarm',
        paths=['/api/.*', '/indexes/.*/documents']
    )

    result = proxy._validate_path(policy, '/api/users/123')

    assert result is True


def test_validate_path_denied(proxy):
    """Test path validation denies non-matching paths"""
    policy = SwarmPathPolicy(
        swarm_id='test-swarm',
        paths=['/api/.*']
    )

    result = proxy._validate_path(policy, '/admin/users')

    assert result is False


def test_validate_path_multiple_patterns(proxy):
    """Test path validation checks all patterns"""
    policy = SwarmPathPolicy(
        swarm_id='test-swarm',
        paths=['/health', '/api/.*', '/indexes/.*/documents']
    )

    # Should match second pattern
    result = proxy._validate_path(policy, '/api/search')

    assert result is True


# ============================================================================
# Capability Checking Tests
# ============================================================================

@pytest.mark.asyncio
async def test_check_capability_has_capability(proxy, mock_event_bus):
    """Test capability check succeeds when swarm has capability"""
    mock_event_bus.get.return_value = json.dumps([
        'network.http.proxy.external',
        'system.process.execute'
    ])

    result = await proxy._check_capability('test-swarm', 'network.http.proxy.external')

    assert result is True
    mock_event_bus.get.assert_called_once_with('/swarms/test-swarm/capabilities')


@pytest.mark.asyncio
async def test_check_capability_missing_capability(proxy, mock_event_bus):
    """Test capability check fails when swarm lacks capability"""
    mock_event_bus.get.return_value = json.dumps([
        'system.process.execute'  # Missing network.http.proxy.external
    ])

    result = await proxy._check_capability('test-swarm', 'network.http.proxy.external')

    assert result is False


@pytest.mark.asyncio
async def test_check_capability_swarm_not_registered(proxy, mock_event_bus):
    """Test capability check fails when swarm not registered"""
    mock_event_bus.get.return_value = None

    result = await proxy._check_capability('nonexistent-swarm', 'network.http.proxy.external')

    assert result is False


# ============================================================================
# HTTP Request Tests
# ============================================================================

@pytest.mark.asyncio
async def test_make_request_get_success(proxy):
    """Test successful GET request"""
    # Mock aiohttp session
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.text = AsyncMock(return_value='{"result": "success"}')

    proxy._session = AsyncMock()
    proxy._session.request = AsyncMock(return_value=mock_response)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock()

    result = await proxy._make_request(
        'GET',
        'http://test.local/api/data',
        {},
        None
    )

    assert result.success is True
    assert result.status_code == 200
    assert 'Content-Type' in result.headers
    assert result.body == '{"result": "success"}'
    assert result.request_time_ms > 0


@pytest.mark.asyncio
async def test_make_request_post_with_body(proxy):
    """Test POST request with body"""
    mock_response = AsyncMock()
    mock_response.status = 201
    mock_response.headers = {}
    mock_response.text = AsyncMock(return_value='')

    proxy._session = AsyncMock()
    proxy._session.request = AsyncMock(return_value=mock_response)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock()

    result = await proxy._make_request(
        'POST',
        'http://test.local/api/data',
        {'Content-Type': 'application/json'},
        '{"key": "value"}'
    )

    assert result.success is True
    assert result.status_code == 201


@pytest.mark.asyncio
async def test_make_request_error_response(proxy):
    """Test request with error status code"""
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_response.headers = {}
    mock_response.text = AsyncMock(return_value='Not Found')

    proxy._session = AsyncMock()
    proxy._session.request = AsyncMock(return_value=mock_response)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock()

    result = await proxy._make_request(
        'GET',
        'http://test.local/api/notfound',
        {},
        None
    )

    assert result.success is False  # 404 is not success
    assert result.status_code == 404


# ============================================================================
# End-to-End Request Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_proxy_request_success(proxy, mock_event_bus, mock_witness_logger):
    """Test successful proxy request end-to-end"""
    await proxy._load_registry()

    # Mock capability check
    mock_event_bus.get.return_value = json.dumps(['network.http.proxy.external'])

    # Mock HTTP request
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {'Content-Type': 'application/json'}
    mock_response.text = AsyncMock(return_value='{"id": 1}')

    proxy._session = AsyncMock()
    proxy._session.request = AsyncMock(return_value=mock_response)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock()

    # Create request event
    request = {
        'trace_id': 'trace-123',
        'swarm_id': 'navidocs-adapter',
        'target_alias': 'meilisearch_api',
        'method': 'GET',
        'path': '/health',
        'headers': {},
        'timeout_ms': 10000
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Verify result published
    mock_event_bus.put.assert_called_once()
    call_args = mock_event_bus.put.call_args
    assert call_args[0][0] == 'if.event.network.proxy.result/trace-123'

    result = json.loads(call_args[0][1])
    assert result['trace_id'] == 'trace-123'
    assert result['success'] is True
    assert result['status_code'] == 200

    # Verify IF.witness logging
    assert len(mock_witness_logger.events) == 1
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'request_completed'
    assert log['swarm_id'] == 'navidocs-adapter'
    assert log['target_alias'] == 'meilisearch_api'


@pytest.mark.asyncio
async def test_handle_proxy_request_missing_capability(proxy, mock_event_bus, mock_witness_logger):
    """Test request denied when swarm lacks capability"""
    await proxy._load_registry()

    # Mock capability check fails
    mock_event_bus.get.return_value = json.dumps([])

    request = {
        'trace_id': 'trace-456',
        'swarm_id': 'test-swarm',
        'target_alias': 'meilisearch_api',
        'method': 'GET',
        'path': '/health',
        'timeout_ms': 10000
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'capability' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'request_denied_capability'


@pytest.mark.asyncio
async def test_handle_proxy_request_target_not_found(proxy, mock_event_bus, mock_witness_logger):
    """Test request denied when target alias doesn't exist"""
    await proxy._load_registry()

    # Mock capability check succeeds
    mock_event_bus.get.return_value = json.dumps(['network.http.proxy.external'])

    request = {
        'trace_id': 'trace-789',
        'swarm_id': 'navidocs-adapter',
        'target_alias': 'nonexistent_api',  # Not in registry
        'method': 'GET',
        'path': '/health',
        'timeout_ms': 10000
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'unknown target alias' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'request_denied_target_not_found'


@pytest.mark.asyncio
async def test_handle_proxy_request_swarm_not_allowed(proxy, mock_event_bus, mock_witness_logger):
    """Test request denied when swarm not allowed to access target"""
    await proxy._load_registry()

    # Mock capability check succeeds
    mock_event_bus.get.return_value = json.dumps(['network.http.proxy.external'])

    # Request from swarm not in allowed_swarms for this target
    request = {
        'trace_id': 'trace-abc',
        'swarm_id': 'unauthorized-swarm',  # Not in meilisearch allowed_swarms
        'target_alias': 'meilisearch_api',
        'method': 'GET',
        'path': '/health',
        'timeout_ms': 10000
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'not allowed to access target' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'request_denied_swarm_not_allowed'


@pytest.mark.asyncio
async def test_handle_proxy_request_path_not_allowed(proxy, mock_event_bus, mock_witness_logger):
    """Test request denied when path violates allow-list"""
    await proxy._load_registry()

    # Mock capability check succeeds
    mock_event_bus.get.return_value = json.dumps(['network.http.proxy.external'])

    # Request path not in allowed patterns
    request = {
        'trace_id': 'trace-def',
        'swarm_id': 'navidocs-adapter',
        'target_alias': 'meilisearch_api',
        'method': 'DELETE',
        'path': '/admin/delete-all',  # Not in allowed paths!
        'timeout_ms': 10000
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'path not allowed' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'request_denied_path'


@pytest.mark.asyncio
async def test_handle_proxy_request_timeout(proxy, mock_event_bus, mock_witness_logger):
    """Test request times out if takes too long"""
    await proxy._load_registry()

    # Mock capability check
    mock_event_bus.get.return_value = json.dumps(['network.http.proxy.external'])

    # Mock slow HTTP request
    async def slow_request(*args, **kwargs):
        await asyncio.sleep(10)  # Sleep 10 seconds
        mock_response = AsyncMock()
        mock_response.status = 200
        return mock_response

    proxy._session = AsyncMock()
    proxy._session.request = slow_request

    # Request with very short timeout
    request = {
        'trace_id': 'trace-timeout',
        'swarm_id': 'navidocs-adapter',
        'target_alias': 'meilisearch_api',
        'method': 'GET',
        'path': '/health',
        'timeout_ms': 100  # 100ms timeout
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Verify timeout error
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'timeout' in result['error'].lower()

    # Verify IF.witness logging
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'request_timeout'


@pytest.mark.asyncio
async def test_handle_proxy_request_missing_fields(proxy, mock_event_bus):
    """Test request rejected when missing required fields"""
    request = {
        'trace_id': 'trace-bad',
        # Missing swarm_id and target_alias
        'method': 'GET',
        'path': '/health'
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Verify error result
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is False
    assert 'missing required fields' in result['error'].lower()


@pytest.mark.asyncio
async def test_handle_proxy_request_respects_max_timeout(proxy, mock_event_bus):
    """Test request timeout capped at target max_timeout_ms"""
    await proxy._load_registry()

    # Mock capability check
    mock_event_bus.get.return_value = json.dumps(['network.http.proxy.external'])

    # Mock HTTP request
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.headers = {}
    mock_response.text = AsyncMock(return_value='')

    proxy._session = AsyncMock()
    proxy._session.request = AsyncMock(return_value=mock_response)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock()

    # Request with timeout exceeding target max
    request = {
        'trace_id': 'trace-max',
        'swarm_id': 'navidocs-adapter',
        'target_alias': 'meilisearch_api',
        'method': 'GET',
        'path': '/health',
        'timeout_ms': 999999  # Way over target max of 60000ms
    }

    event = WatchEvent(
        key='if.command.network.proxy',
        value=json.dumps(request),
        event_type='put',
        mod_revision=1
    )

    await proxy._handle_proxy_request(event)

    # Execution should succeed (capped at 60000ms)
    call_args = mock_event_bus.put.call_args
    result = json.loads(call_args[0][1])
    assert result['success'] is True


# ============================================================================
# IF.witness Logging Tests
# ============================================================================

def test_log_witness_with_callable(proxy):
    """Test IF.witness logging with callable logger"""
    logged_entries = []
    proxy.witness_logger = lambda entry: logged_entries.append(entry)

    proxy._log_witness(
        'test_operation',
        'test-swarm',
        'test_api',
        'GET',
        '/health',
        {'extra': 'data'}
    )

    assert len(logged_entries) == 1
    log = logged_entries[0]
    assert log['component'] == 'IF.proxy'
    assert log['operation'] == 'test_operation'
    assert log['swarm_id'] == 'test-swarm'
    assert log['target_alias'] == 'test_api'
    assert log['method'] == 'GET'
    assert log['path'] == '/health'
    assert log['extra'] == 'data'
    assert 'timestamp' in log


def test_log_witness_with_events_list(proxy, mock_witness_logger):
    """Test IF.witness logging with events list"""
    proxy._log_witness(
        'test_operation',
        'test-swarm',
        'test_api',
        'POST',
        '/api/data'
    )

    assert len(mock_witness_logger.events) == 1
    log = mock_witness_logger.events[0]
    assert log['operation'] == 'test_operation'


def test_log_witness_no_logger(proxy):
    """Test IF.witness logging gracefully handles no logger"""
    proxy.witness_logger = None

    # Should not raise exception
    proxy._log_witness(
        'test_operation',
        'test-swarm',
        'test_api',
        'GET',
        '/health'
    )


# ============================================================================
# Result Publishing Tests
# ============================================================================

@pytest.mark.asyncio
async def test_send_result_publishes_to_correct_topic(proxy, mock_event_bus):
    """Test result publishing uses correct IF.bus topic"""
    await proxy._send_result(
        'trace-123',
        success=True,
        status_code=200,
        body='{"result": "ok"}'
    )

    mock_event_bus.put.assert_called_once()
    call_args = mock_event_bus.put.call_args

    assert call_args[0][0] == 'if.event.network.proxy.result/trace-123'

    result = json.loads(call_args[0][1])
    assert result['trace_id'] == 'trace-123'
    assert result['success'] is True
    assert result['status_code'] == 200
    assert result['body'] == '{"result": "ok"}'


# ============================================================================
# Security Tests
# ============================================================================

def test_path_validation_prevents_unauthorized_access(proxy):
    """Test path validation prevents access to unauthorized endpoints"""
    policy = SwarmPathPolicy(
        swarm_id='test-swarm',
        paths=['/api/public/.*']  # Only public API allowed
    )

    # Try to access admin endpoint
    result = proxy._validate_path(policy, '/api/admin/users')

    assert result is False


def test_path_validation_enforces_strict_patterns(proxy):
    """Test path validation enforces strict regex patterns"""
    policy = SwarmPathPolicy(
        swarm_id='test-swarm',
        paths=['/indexes/[a-z]+/documents']  # Only lowercase index names
    )

    # Try uppercase (should fail)
    result = proxy._validate_path(policy, '/indexes/ADMIN/documents')

    assert result is False

    # Try valid lowercase (should pass)
    result = proxy._validate_path(policy, '/indexes/navidocs/documents')

    assert result is True


@pytest.mark.asyncio
async def test_target_isolation_between_swarms(proxy):
    """Test different swarms have isolated path policies"""
    await proxy._load_registry()

    # navidocs-adapter can access meilisearch
    target = proxy._get_target('meilisearch_api')
    navidocs_policy = target.allowed_swarms['navidocs-adapter']
    assert proxy._validate_path(navidocs_policy, '/indexes/navidocs/documents')

    # ha-adapter can only access home_assistant_api, not meilisearch
    assert 'ha-adapter' not in target.allowed_swarms
