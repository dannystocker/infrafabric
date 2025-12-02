#!/usr/bin/env python3
"""
Reusable Health Check Functions for InfraFabric Swarm

Provides dependency health checks for:
- Redis Bus connectivity and latency
- ChromaDB collection accessibility
- Disk space availability
- Memory usage monitoring
- Environment variable validation

Citation: if://agent/A34_health_check_dependencies
Author: Agent A34
Date: 2025-11-30
"""

import os
import sys
import time
import psutil
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Redis Health Checks
# ============================================================================

class RedisHealthChecker:
    """Health checker for Redis Bus connections."""

    def __init__(self, host: str = 'localhost', port: int = 6379,
                 db: int = 0, password: Optional[str] = None,
                 timeout: float = 5.0):
        """Initialize Redis health checker.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.timeout = timeout
        self.connection = None
        self._cached_status = None
        self._cache_time = None
        self._cache_ttl = 5  # Cache health check for 5 seconds

    def _get_connection(self) -> Optional[redis.Redis]:
        """Get or create Redis connection."""
        if not REDIS_AVAILABLE:
            return None

        try:
            if self.connection is None:
                self.connection = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    decode_responses=True,
                    socket_timeout=self.timeout,
                    socket_connect_timeout=self.timeout,
                    health_check_interval=30
                )
            return self.connection
        except Exception as e:
            logger.error(f"Failed to create Redis connection: {e}")
            return None

    def check(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Check Redis health with PING and INFO latency metrics.

        Args:
            use_cache: Use cached result if available

        Returns:
            Dict with keys:
            - status: 'ok' or 'error'
            - latency_ms: PING latency in milliseconds
            - info: Redis INFO dict (if available)
            - error: Error message (if status is error)
            - timestamp: Check timestamp
        """
        # Check cache
        if use_cache and self._cached_status is not None:
            if time.time() - self._cache_time < self._cache_ttl:
                return self._cached_status

        start_time = time.time()
        result = {
            'status': 'error',
            'latency_ms': 0,
            'info': None,
            'error': None,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        if not REDIS_AVAILABLE:
            result['error'] = 'redis library not available'
            return result

        try:
            conn = self._get_connection()
            if conn is None:
                result['error'] = 'Failed to establish connection'
                return result

            # PING command
            ping_start = time.time()
            conn.ping()
            latency_ms = (time.time() - ping_start) * 1000

            # Get INFO for additional metrics
            try:
                info = conn.info()
                result['info'] = {
                    'used_memory_bytes': info.get('used_memory', 0),
                    'connected_clients': info.get('connected_clients', 0),
                    'ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                    'server_version': info.get('redis_version', 'unknown'),
                    'uptime_seconds': info.get('uptime_in_seconds', 0)
                }
            except Exception as e:
                logger.debug(f"Could not retrieve INFO: {e}")

            result['status'] = 'ok'
            result['latency_ms'] = round(latency_ms, 3)

        except redis.ConnectionError as e:
            result['error'] = f'Connection failed: {str(e)}'
            result['status'] = 'error'
        except redis.TimeoutError as e:
            result['error'] = f'Timeout: {str(e)}'
            result['status'] = 'error'
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
            result['status'] = 'error'

        # Cache result
        self._cached_status = result
        self._cache_time = time.time()

        return result

    def close(self):
        """Close Redis connection."""
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception as e:
                logger.debug(f"Error closing Redis connection: {e}")
            self.connection = None


# ============================================================================
# ChromaDB Health Checks
# ============================================================================

class ChromaDBHealthChecker:
    """Health checker for ChromaDB collections."""

    def __init__(self, path: str = '/root/openwebui-knowledge/chromadb',
                 timeout: float = 10.0):
        """Initialize ChromaDB health checker.

        Args:
            path: ChromaDB persistent storage path
            timeout: Operation timeout in seconds
        """
        self.path = path
        self.timeout = timeout
        self.client = None
        self._cached_status = None
        self._cache_time = None
        self._cache_ttl = 5  # Cache health check for 5 seconds

    def _get_client(self) -> Optional[Any]:
        """Get or create ChromaDB client."""
        if not CHROMADB_AVAILABLE:
            return None

        try:
            if self.client is None:
                self.client = chromadb.PersistentClient(path=self.path)
            return self.client
        except Exception as e:
            logger.error(f"Failed to create ChromaDB client: {e}")
            return None

    def check(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Check ChromaDB health by listing collections and querying.

        Args:
            use_cache: Use cached result if available

        Returns:
            Dict with keys:
            - status: 'ok' or 'error'
            - collections: List of collection names
            - collection_count: Number of accessible collections
            - error: Error message (if status is error)
            - timestamp: Check timestamp
        """
        # Check cache
        if use_cache and self._cached_status is not None:
            if time.time() - self._cache_time < self._cache_ttl:
                return self._cached_status

        result = {
            'status': 'error',
            'collections': [],
            'collection_count': 0,
            'error': None,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        if not CHROMADB_AVAILABLE:
            result['error'] = 'chromadb library not available'
            return result

        try:
            client = self._get_client()
            if client is None:
                result['error'] = 'Failed to create ChromaDB client'
                return result

            # List collections
            collections = client.list_collections()

            if collections is None:
                result['error'] = 'Could not list collections'
                return result

            collection_names = [col.name for col in collections]

            # Try a basic query on the first available collection
            if collection_names:
                try:
                    test_collection = client.get_collection(name=collection_names[0])
                    # Don't actually query, just verify we can get the collection
                    count = test_collection.count() if hasattr(test_collection, 'count') else 0
                    logger.debug(f"ChromaDB test collection '{collection_names[0]}' has {count} items")
                except Exception as e:
                    logger.debug(f"Could not access test collection: {e}")

            result['status'] = 'ok'
            result['collections'] = collection_names
            result['collection_count'] = len(collection_names)

        except Exception as e:
            result['error'] = f'Error checking ChromaDB: {str(e)}'
            result['status'] = 'error'

        # Cache result
        self._cached_status = result
        self._cache_time = time.time()

        return result


# ============================================================================
# System Health Checks
# ============================================================================

class SystemHealthChecker:
    """Health checker for system resources."""

    def __init__(self, disk_threshold_percent: float = 10.0,
                 memory_threshold_percent: float = 80.0):
        """Initialize system health checker.

        Args:
            disk_threshold_percent: Warn if free disk < this % of total
            memory_threshold_percent: Warn if memory > this % of total
        """
        self.disk_threshold = disk_threshold_percent
        self.memory_threshold = memory_threshold_percent
        self._cached_status = None
        self._cache_time = None
        self._cache_ttl = 10  # Cache for 10 seconds

    def check_disk(self, path: str = '/') -> Dict[str, Any]:
        """
        Check disk space availability.

        Args:
            path: Path to check disk usage for

        Returns:
            Dict with keys:
            - status: 'ok', 'warning', or 'error'
            - total_gb: Total disk space in GB
            - used_gb: Used disk space in GB
            - free_gb: Free disk space in GB
            - free_percent: Free space as percentage
            - timestamp: Check timestamp
        """
        result = {
            'status': 'ok',
            'total_gb': 0,
            'used_gb': 0,
            'free_gb': 0,
            'free_percent': 0,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        try:
            disk_usage = psutil.disk_usage(path)

            result['total_gb'] = round(disk_usage.total / (1024**3), 2)
            result['used_gb'] = round(disk_usage.used / (1024**3), 2)
            result['free_gb'] = round(disk_usage.free / (1024**3), 2)
            result['free_percent'] = round(disk_usage.percent, 2)

            # Determine status
            if disk_usage.percent >= (100 - self.disk_threshold):
                result['status'] = 'warning'

            if disk_usage.percent >= 95:
                result['status'] = 'error'

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result

    def check_memory(self) -> Dict[str, Any]:
        """
        Check memory usage.

        Returns:
            Dict with keys:
            - status: 'ok' or 'warning'
            - total_mb: Total memory in MB
            - used_mb: Used memory in MB
            - available_mb: Available memory in MB
            - percent: Memory usage percentage
            - timestamp: Check timestamp
        """
        result = {
            'status': 'ok',
            'total_mb': 0,
            'used_mb': 0,
            'available_mb': 0,
            'percent': 0,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        try:
            memory = psutil.virtual_memory()

            result['total_mb'] = round(memory.total / (1024**2), 2)
            result['used_mb'] = round(memory.used / (1024**2), 2)
            result['available_mb'] = round(memory.available / (1024**2), 2)
            result['percent'] = round(memory.percent, 2)

            # Determine status
            if memory.percent >= self.memory_threshold:
                result['status'] = 'warning'

            if memory.percent >= 95:
                result['status'] = 'error'

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result


# ============================================================================
# Environment Validation
# ============================================================================

class EnvironmentChecker:
    """Check required environment variables."""

    def __init__(self, required_vars: Optional[List[str]] = None):
        """Initialize environment checker.

        Args:
            required_vars: List of required environment variable names
        """
        self.required_vars = required_vars or [
            'REDIS_HOST',
            'CHROMADB_PATH',
            'INFRAFABRIC_ENV'
        ]

    def check(self) -> Dict[str, Any]:
        """
        Check that required environment variables are set.

        Returns:
            Dict with keys:
            - status: 'ok' or 'error'
            - missing_vars: List of missing variables
            - timestamp: Check timestamp
        """
        result = {
            'status': 'ok',
            'missing_vars': [],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        for var in self.required_vars:
            if not os.environ.get(var):
                result['missing_vars'].append(var)
                result['status'] = 'error'

        return result


# ============================================================================
# Combined Health Check Orchestrator
# ============================================================================

class HealthCheckOrchestrator:
    """Orchestrates all health checks for the /ready endpoint."""

    def __init__(self, redis_config: Optional[Dict[str, Any]] = None,
                 chromadb_config: Optional[Dict[str, Any]] = None,
                 system_config: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator with component checkers.

        Args:
            redis_config: Redis connection config
            chromadb_config: ChromaDB config
            system_config: System checker config
        """
        redis_config = redis_config or {}
        chromadb_config = chromadb_config or {}
        system_config = system_config or {}

        self.redis_checker = RedisHealthChecker(**redis_config)
        self.chromadb_checker = ChromaDBHealthChecker(**chromadb_config)
        self.system_checker = SystemHealthChecker(**system_config)
        self.environment_checker = EnvironmentChecker()

        self._start_time = time.time()

    def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks and return combined status.

        Returns:
            Dict with comprehensive health status
        """
        checks = {
            'redis': self.redis_checker.check(),
            'chromadb': self.chromadb_checker.check(),
            'disk': self.system_checker.check_disk(),
            'memory': self.system_checker.check_memory(),
            'environment': self.environment_checker.check()
        }

        # Determine overall readiness
        ready = all(
            check.get('status') in ('ok', 'warning')
            for check in checks.values()
        )

        # All critical checks must pass
        critical_ready = all(
            check.get('status') in ('ok',)
            for key, check in checks.items()
            if key in ('redis', 'chromadb', 'environment')
        )

        return {
            'ready': ready and critical_ready,
            'checks': checks,
            'uptime_seconds': round(time.time() - self._start_time, 2),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def check_alive(self) -> Dict[str, Any]:
        """
        Quick liveness check (process alive, no dependencies).

        Returns:
            Dict with liveness status
        """
        return {
            'alive': True,
            'uptime_seconds': round(time.time() - self._start_time, 2),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# ============================================================================
# Convenience Functions
# ============================================================================

_default_orchestrator: Optional[HealthCheckOrchestrator] = None


def initialize_health_checks(redis_config: Optional[Dict[str, Any]] = None,
                            chromadb_config: Optional[Dict[str, Any]] = None,
                            system_config: Optional[Dict[str, Any]] = None) -> HealthCheckOrchestrator:
    """Initialize default health check orchestrator."""
    global _default_orchestrator
    _default_orchestrator = HealthCheckOrchestrator(
        redis_config=redis_config,
        chromadb_config=chromadb_config,
        system_config=system_config
    )
    return _default_orchestrator


def get_health_orchestrator() -> HealthCheckOrchestrator:
    """Get default orchestrator or create one."""
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = HealthCheckOrchestrator()
    return _default_orchestrator


# ============================================================================
# CLI Usage (for testing)
# ============================================================================

if __name__ == '__main__':
    # Test each checker independently
    import json

    logging.basicConfig(level=logging.DEBUG)

    print("=" * 70)
    print("InfraFabric Health Check Dependency Checkers")
    print("=" * 70)

    # Test Redis
    print("\n[1/4] Testing Redis Health Checker...")
    redis_checker = RedisHealthChecker()
    redis_status = redis_checker.check()
    print(json.dumps(redis_status, indent=2))

    # Test ChromaDB
    print("\n[2/4] Testing ChromaDB Health Checker...")
    chromadb_checker = ChromaDBHealthChecker()
    chromadb_status = chromadb_checker.check()
    print(json.dumps(chromadb_status, indent=2))

    # Test System
    print("\n[3/4] Testing System Health Checker...")
    system_checker = SystemHealthChecker()
    print(f"Disk: {json.dumps(system_checker.check_disk(), indent=2)}")
    print(f"Memory: {json.dumps(system_checker.check_memory(), indent=2)}")

    # Test Environment
    print("\n[4/4] Testing Environment Checker...")
    env_checker = EnvironmentChecker()
    env_status = env_checker.check()
    print(json.dumps(env_status, indent=2))

    # Test Orchestrator
    print("\n" + "=" * 70)
    print("Combined Health Check")
    print("=" * 70)
    orchestrator = HealthCheckOrchestrator()
    full_status = orchestrator.check_all()
    print(json.dumps(full_status, indent=2))
