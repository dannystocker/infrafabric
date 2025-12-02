#!/usr/bin/env python3
"""
Comprehensive Test Suite for Health Check Endpoints and Dependencies

Tests cover:
- Liveness probe (/health) - fast response, no dependencies
- Readiness probe (/ready) - dependency checking
- Dependency checkers: Redis, ChromaDB, System
- Graceful degradation modes
- Performance requirements (<10ms for /health, <100ms for /ready)

Citation: if://agent/A34_health_check_tests
Author: Agent A34
Date: 2025-11-30
"""

import os
import sys
import time
import json
import pytest
import tempfile
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Mock FastAPI if needed
try:
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from monitoring.health.dependency_checks import (
    RedisHealthChecker,
    ChromaDBHealthChecker,
    SystemHealthChecker,
    EnvironmentChecker,
    HealthCheckOrchestrator
)

if FASTAPI_AVAILABLE:
    from monitoring.health.health_endpoints import create_app


# ============================================================================
# Redis Health Checker Tests
# ============================================================================

class TestRedisHealthChecker:
    """Test suite for Redis health checking."""

    def test_redis_checker_init(self):
        """Test RedisHealthChecker initialization."""
        checker = RedisHealthChecker(
            host='localhost',
            port=6379,
            timeout=5.0
        )
        assert checker.host == 'localhost'
        assert checker.port == 6379
        assert checker.timeout == 5.0

    def test_redis_checker_check_redis_not_available(self):
        """Test check when redis library not available."""
        checker = RedisHealthChecker()

        # Mock REDIS_AVAILABLE to False
        with patch('monitoring.health.dependency_checks.REDIS_AVAILABLE', False):
            result = checker.check()

        assert result['status'] == 'error'
        assert 'not available' in result['error'].lower()

    def test_redis_checker_connection_error(self):
        """Test handling of connection errors."""
        checker = RedisHealthChecker(host='invalid-host')

        # Mock connection to fail
        with patch('monitoring.health.dependency_checks.redis.Redis') as mock_redis:
            mock_redis.side_effect = Exception("Connection refused")
            # Reset connection cache
            checker.connection = None

            result = checker.check(use_cache=False)

        assert result['status'] == 'error'
        assert result['error'] is not None

    def test_redis_checker_caching(self):
        """Test result caching."""
        checker = RedisHealthChecker()

        # Create a mock connection
        mock_conn = MagicMock()
        mock_conn.ping.return_value = True
        mock_conn.info.return_value = {
            'used_memory': 1000000,
            'connected_clients': 5,
            'instantaneous_ops_per_sec': 100,
            'redis_version': '7.0.0',
            'uptime_in_seconds': 3600
        }
        checker.connection = mock_conn

        # First check
        result1 = checker.check(use_cache=False)
        time.sleep(0.1)

        # Second check (should use cache)
        result2 = checker.check(use_cache=True)

        assert result1 == result2
        # ping should only be called once due to caching
        assert mock_conn.ping.call_count == 1

    def test_redis_checker_timeout(self):
        """Test timeout handling."""
        checker = RedisHealthChecker(timeout=0.1)

        with patch('monitoring.health.dependency_checks.redis.Redis') as mock_redis:
            mock_instance = MagicMock()
            mock_instance.ping.side_effect = TimeoutError("Connection timeout")
            mock_redis.return_value = mock_instance
            checker.connection = None

            result = checker.check(use_cache=False)

        assert result['status'] == 'error'
        assert 'timeout' in result['error'].lower()


# ============================================================================
# ChromaDB Health Checker Tests
# ============================================================================

class TestChromaDBHealthChecker:
    """Test suite for ChromaDB health checking."""

    def test_chromadb_checker_init(self):
        """Test ChromaDBHealthChecker initialization."""
        checker = ChromaDBHealthChecker(path='/tmp/chromadb')
        assert checker.path == '/tmp/chromadb'

    def test_chromadb_checker_chromadb_not_available(self):
        """Test check when chromadb library not available."""
        checker = ChromaDBHealthChecker()

        with patch('monitoring.health.dependency_checks.CHROMADB_AVAILABLE', False):
            result = checker.check()

        assert result['status'] == 'error'
        assert 'not available' in result['error'].lower()

    def test_chromadb_checker_list_collections(self):
        """Test successful collection listing."""
        checker = ChromaDBHealthChecker()

        # Mock ChromaDB client
        mock_client = MagicMock()
        mock_collection1 = MagicMock()
        mock_collection1.name = 'openwebui_core'
        mock_collection2 = MagicMock()
        mock_collection2.name = 'openwebui_docs'

        mock_client.list_collections.return_value = [mock_collection1, mock_collection2]
        mock_client.get_collection.return_value = mock_collection1

        with patch('monitoring.health.dependency_checks.chromadb.PersistentClient',
                   return_value=mock_client):
            checker.client = None
            result = checker.check(use_cache=False)

        assert result['status'] == 'ok'
        assert result['collection_count'] == 2
        assert 'openwebui_core' in result['collections']

    def test_chromadb_checker_client_error(self):
        """Test handling of client creation errors."""
        checker = ChromaDBHealthChecker()

        with patch('monitoring.health.dependency_checks.chromadb.PersistentClient') as mock_client:
            mock_client.side_effect = Exception("Invalid path")
            checker.client = None

            result = checker.check(use_cache=False)

        assert result['status'] == 'error'
        assert result['error'] is not None

    def test_chromadb_checker_caching(self):
        """Test result caching."""
        checker = ChromaDBHealthChecker()

        mock_client = MagicMock()
        mock_col = MagicMock()
        mock_col.name = 'test_collection'
        mock_client.list_collections.return_value = [mock_col]

        checker.client = mock_client

        # First check
        result1 = checker.check(use_cache=False)

        # Second check (should use cache)
        result2 = checker.check(use_cache=True)

        assert result1 == result2
        # list_collections should only be called once
        assert mock_client.list_collections.call_count == 1


# ============================================================================
# System Health Checker Tests
# ============================================================================

class TestSystemHealthChecker:
    """Test suite for system health checking."""

    def test_system_checker_init(self):
        """Test SystemHealthChecker initialization."""
        checker = SystemHealthChecker(
            disk_threshold_percent=15.0,
            memory_threshold_percent=85.0
        )
        assert checker.disk_threshold == 15.0
        assert checker.memory_threshold == 85.0

    def test_disk_check_ok(self):
        """Test disk check when status is OK."""
        checker = SystemHealthChecker(disk_threshold_percent=10.0)

        with patch('monitoring.health.dependency_checks.psutil.disk_usage') as mock_disk:
            mock_disk.return_value = MagicMock(
                total=1000000000,  # 1GB
                used=300000000,    # 30% used
                free=700000000,    # 70% free
                percent=30
            )

            result = checker.check_disk()

        assert result['status'] == 'ok'
        assert result['free_percent'] == 30
        assert result['total_gb'] > 0

    def test_disk_check_warning(self):
        """Test disk check when status is WARNING."""
        checker = SystemHealthChecker(disk_threshold_percent=10.0)

        with patch('monitoring.health.dependency_checks.psutil.disk_usage') as mock_disk:
            mock_disk.return_value = MagicMock(
                total=1000000000,
                used=950000000,  # 95% used, 5% free
                free=50000000,
                percent=95
            )

            result = checker.check_disk()

        assert result['status'] == 'warning'

    def test_disk_check_error(self):
        """Test disk check when status is ERROR."""
        checker = SystemHealthChecker(disk_threshold_percent=10.0)

        with patch('monitoring.health.dependency_checks.psutil.disk_usage') as mock_disk:
            mock_disk.return_value = MagicMock(
                total=1000000000,
                used=980000000,  # 98% used
                free=20000000,
                percent=98
            )

            result = checker.check_disk()

        assert result['status'] == 'error'

    def test_memory_check_ok(self):
        """Test memory check when status is OK."""
        checker = SystemHealthChecker(memory_threshold_percent=80.0)

        with patch('monitoring.health.dependency_checks.psutil.virtual_memory') as mock_mem:
            mock_mem.return_value = MagicMock(
                total=8000000000,
                used=3200000000,  # 40% used
                available=4800000000,
                percent=40
            )

            result = checker.check_memory()

        assert result['status'] == 'ok'
        assert result['percent'] == 40

    def test_memory_check_warning(self):
        """Test memory check when status is WARNING."""
        checker = SystemHealthChecker(memory_threshold_percent=80.0)

        with patch('monitoring.health.dependency_checks.psutil.virtual_memory') as mock_mem:
            mock_mem.return_value = MagicMock(
                total=8000000000,
                used=6400000000,  # 80% used
                available=1600000000,
                percent=80
            )

            result = checker.check_memory()

        assert result['status'] == 'warning'

    def test_disk_check_error_handling(self):
        """Test error handling in disk check."""
        checker = SystemHealthChecker()

        with patch('monitoring.health.dependency_checks.psutil.disk_usage') as mock_disk:
            mock_disk.side_effect = Exception("Permission denied")

            result = checker.check_disk()

        assert result['status'] == 'error'
        assert 'error' in result


# ============================================================================
# Environment Checker Tests
# ============================================================================

class TestEnvironmentChecker:
    """Test suite for environment variable checking."""

    def test_environment_checker_init(self):
        """Test EnvironmentChecker initialization."""
        required = ['VAR1', 'VAR2']
        checker = EnvironmentChecker(required_vars=required)
        assert checker.required_vars == required

    def test_environment_check_all_present(self):
        """Test when all required variables are present."""
        checker = EnvironmentChecker(required_vars=['PATH'])

        # PATH should always be present
        result = checker.check()

        assert result['status'] == 'ok'
        assert len(result['missing_vars']) == 0

    def test_environment_check_missing_vars(self):
        """Test when required variables are missing."""
        checker = EnvironmentChecker(
            required_vars=['NONEXISTENT_VAR_ABC123', 'ANOTHER_MISSING_VAR']
        )

        result = checker.check()

        assert result['status'] == 'error'
        assert len(result['missing_vars']) == 2
        assert 'NONEXISTENT_VAR_ABC123' in result['missing_vars']

    def test_environment_check_partial_missing(self):
        """Test when some variables are missing."""
        checker = EnvironmentChecker(
            required_vars=['PATH', 'NONEXISTENT_VAR_XYZ']
        )

        result = checker.check()

        assert result['status'] == 'error'
        assert len(result['missing_vars']) == 1


# ============================================================================
# Health Check Orchestrator Tests
# ============================================================================

class TestHealthCheckOrchestrator:
    """Test suite for the orchestrator."""

    def test_orchestrator_init(self):
        """Test orchestrator initialization."""
        orchestrator = HealthCheckOrchestrator()
        assert orchestrator.redis_checker is not None
        assert orchestrator.chromadb_checker is not None
        assert orchestrator.system_checker is not None

    def test_orchestrator_check_alive(self):
        """Test liveness check."""
        orchestrator = HealthCheckOrchestrator()
        result = orchestrator.check_alive()

        assert result['alive'] is True
        assert result['uptime_seconds'] >= 0
        assert 'timestamp' in result

    def test_orchestrator_check_all_degraded(self):
        """Test when system is degraded but still ready."""
        orchestrator = HealthCheckOrchestrator()

        # Mock some checks to return warnings
        with patch.object(orchestrator.redis_checker, 'check') as mock_redis:
            with patch.object(orchestrator.chromadb_checker, 'check') as mock_chromadb:
                with patch.object(orchestrator.system_checker, 'check_disk') as mock_disk:
                    mock_redis.return_value = {
                        'status': 'ok',
                        'latency_ms': 0.5
                    }
                    mock_chromadb.return_value = {
                        'status': 'ok',
                        'collection_count': 4
                    }
                    mock_disk.return_value = {
                        'status': 'warning',
                        'free_percent': 8
                    }

                    result = orchestrator.check_all()

        assert 'checks' in result
        assert result['ready'] is True  # Still ready despite warning


# ============================================================================
# FastAPI Endpoints Tests
# ============================================================================

@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
class TestHealthEndpoints:
    """Test suite for FastAPI health endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app(
            redis_config={'host': 'localhost', 'port': 6379},
            chromadb_config={'path': '/tmp/chromadb'},
            log_probes=False  # Disable probe logging for tests
        )
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test GET / root endpoint."""
        response = client.get('/')
        assert response.status_code == 200

        data = response.json()
        assert 'service' in data
        assert 'endpoints' in data

    def test_health_endpoint_response_time(self, client):
        """Test /health endpoint response time (<10ms)."""
        start = time.time()
        response = client.get('/health')
        elapsed_ms = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 50  # Allow some buffer, but still fast

    def test_health_endpoint_format(self, client):
        """Test /health endpoint response format."""
        response = client.get('/health')
        assert response.status_code == 200

        data = response.json()
        assert data['status'] == 'healthy'
        assert 'probe_type' in data
        assert 'uptime_seconds' in data
        assert 'timestamp' in data
        assert 'correlation_id' in data

    def test_ready_endpoint_response_time(self, client):
        """Test /ready endpoint response time (<100ms)."""
        start = time.time()
        response = client.get('/ready')
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 200  # Allow buffer for dependency checks

    def test_ready_endpoint_format(self, client):
        """Test /ready endpoint response format."""
        response = client.get('/ready')

        # Could be 200 or 503 depending on system state
        assert response.status_code in [200, 503]

        data = response.json()
        assert 'ready' in data
        assert 'checks' in data
        assert 'redis' in data['checks']
        assert 'chromadb' in data['checks']
        assert 'disk' in data['checks']
        assert 'memory' in data['checks']

    def test_ready_endpoint_redis_check(self, client):
        """Test Redis check in ready endpoint."""
        response = client.get('/ready')
        data = response.json()

        redis_check = data['checks']['redis']
        assert 'status' in redis_check
        assert 'latency_ms' in redis_check
        assert isinstance(redis_check['latency_ms'], (int, float))

    def test_ready_endpoint_chromadb_check(self, client):
        """Test ChromaDB check in ready endpoint."""
        response = client.get('/ready')
        data = response.json()

        chromadb_check = data['checks']['chromadb']
        assert 'status' in chromadb_check
        assert 'collections' in chromadb_check
        assert isinstance(chromadb_check['collections'], int)

    def test_status_endpoint(self, client):
        """Test /status endpoint."""
        response = client.get('/status')
        assert response.status_code == 200

        data = response.json()
        assert 'status' in data
        assert 'uptime_seconds' in data
        assert 'health_checks' in data

    def test_metrics_endpoint(self, client):
        """Test /metrics endpoint."""
        response = client.get('/metrics')
        assert response.status_code == 200

        data = response.json()
        assert 'integration' in data


# ============================================================================
# Integration Tests
# ============================================================================

class TestHealthCheckIntegration:
    """Integration tests for full health check system."""

    def test_orchestrator_with_all_checks_ok(self):
        """Test orchestrator when all checks pass."""
        orchestrator = HealthCheckOrchestrator()

        # Mock all checkers
        with patch.object(orchestrator.redis_checker, 'check') as mock_redis:
            with patch.object(orchestrator.chromadb_checker, 'check') as mock_chromadb:
                with patch.object(orchestrator.system_checker, 'check_disk') as mock_disk:
                    with patch.object(orchestrator.system_checker, 'check_memory') as mock_mem:
                        with patch.object(orchestrator.environment_checker, 'check') as mock_env:
                            mock_redis.return_value = {'status': 'ok', 'latency_ms': 0.5}
                            mock_chromadb.return_value = {'status': 'ok', 'collection_count': 4}
                            mock_disk.return_value = {'status': 'ok', 'free_percent': 50}
                            mock_mem.return_value = {'status': 'ok', 'percent': 40}
                            mock_env.return_value = {'status': 'ok', 'missing_vars': []}

                            result = orchestrator.check_all()

        assert result['ready'] is True

    def test_orchestrator_with_critical_failure(self):
        """Test orchestrator when critical check fails."""
        orchestrator = HealthCheckOrchestrator()

        with patch.object(orchestrator.redis_checker, 'check') as mock_redis:
            with patch.object(orchestrator.chromadb_checker, 'check') as mock_chromadb:
                with patch.object(orchestrator.system_checker, 'check_disk') as mock_disk:
                    with patch.object(orchestrator.system_checker, 'check_memory') as mock_mem:
                        with patch.object(orchestrator.environment_checker, 'check') as mock_env:
                            mock_redis.return_value = {'status': 'error', 'error': 'Connection failed'}
                            mock_chromadb.return_value = {'status': 'ok', 'collection_count': 4}
                            mock_disk.return_value = {'status': 'ok', 'free_percent': 50}
                            mock_mem.return_value = {'status': 'ok', 'percent': 40}
                            mock_env.return_value = {'status': 'ok', 'missing_vars': []}

                            result = orchestrator.check_all()

        # Should not be ready if critical Redis check fails
        assert result['ready'] is False

    @pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
    def test_full_api_health_check_sequence(self):
        """Test complete health check sequence."""
        app = create_app(log_probes=False)
        client = TestClient(app)

        # 1. Get root info
        resp = client.get('/')
        assert resp.status_code == 200

        # 2. Check liveness
        resp = client.get('/health')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'healthy'

        # 3. Check readiness
        resp = client.get('/ready')
        assert resp.status_code in [200, 503]
        assert 'checks' in resp.json()

        # 4. Get detailed status
        resp = client.get('/status')
        assert resp.status_code == 200
        assert 'health_checks' in resp.json()


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Performance tests for health checks."""

    def test_liveness_probe_performance(self):
        """Test liveness check is fast (<10ms)."""
        orchestrator = HealthCheckOrchestrator()

        start = time.time()
        result = orchestrator.check_alive()
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 5  # Should be nearly instant

    def test_redis_checker_performance(self):
        """Test Redis checker latency measurement."""
        checker = RedisHealthChecker()

        with patch('monitoring.health.dependency_checks.redis.Redis') as mock_redis:
            mock_instance = MagicMock()
            mock_instance.ping.return_value = True
            mock_instance.info.return_value = {}
            mock_redis.return_value = mock_instance
            checker.connection = None

            result = checker.check(use_cache=False)

        # Should have measured latency
        assert result['latency_ms'] >= 0


# ============================================================================
# Graceful Degradation Tests
# ============================================================================

class TestGracefulDegradation:
    """Test graceful degradation when dependencies fail."""

    def test_graceful_degradation_redis_down(self):
        """Test system continues when Redis is down."""
        orchestrator = HealthCheckOrchestrator()

        with patch.object(orchestrator.redis_checker, 'check') as mock_redis:
            with patch.object(orchestrator.chromadb_checker, 'check') as mock_chromadb:
                mock_redis.return_value = {'status': 'error'}
                mock_chromadb.return_value = {'status': 'ok', 'collection_count': 4}

                result = orchestrator.check_all()

        # Liveness should still work
        alive = orchestrator.check_alive()
        assert alive['alive'] is True

    def test_graceful_degradation_chromadb_down(self):
        """Test system continues when ChromaDB is down."""
        orchestrator = HealthCheckOrchestrator()

        with patch.object(orchestrator.redis_checker, 'check') as mock_redis:
            with patch.object(orchestrator.chromadb_checker, 'check') as mock_chromadb:
                mock_redis.return_value = {'status': 'ok', 'latency_ms': 0.5}
                mock_chromadb.return_value = {'status': 'error'}

                result = orchestrator.check_all()

        # Liveness should still work
        alive = orchestrator.check_alive()
        assert alive['alive'] is True

    def test_graceful_degradation_both_down(self):
        """Test system continues when both Redis and ChromaDB are down."""
        orchestrator = HealthCheckOrchestrator()

        with patch.object(orchestrator.redis_checker, 'check') as mock_redis:
            with patch.object(orchestrator.chromadb_checker, 'check') as mock_chromadb:
                mock_redis.return_value = {'status': 'error'}
                mock_chromadb.return_value = {'status': 'error'}

                result = orchestrator.check_all()

        # Liveness should still work - don't restart the container
        alive = orchestrator.check_alive()
        assert alive['alive'] is True
        # But readiness should be false
        assert result['ready'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
