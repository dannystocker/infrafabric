"""
InfraFabric Health Check Endpoints Module

Production-grade health check endpoints for Kubernetes deployments.

Exports:
- create_app() - FastAPI application factory
- HealthCheckOrchestrator - Dependency check orchestrator
- RedisHealthChecker - Redis health checks
- ChromaDBHealthChecker - ChromaDB health checks
- SystemHealthChecker - System resource checks
- EnvironmentChecker - Environment variable validation

Citation: if://agent/A34_health_check_system
"""

try:
    from .dependency_checks import (
        HealthCheckOrchestrator,
        RedisHealthChecker,
        ChromaDBHealthChecker,
        SystemHealthChecker,
        EnvironmentChecker,
        initialize_health_checks,
        get_health_orchestrator
    )
except ImportError:
    pass

try:
    from .health_endpoints import create_app
except ImportError:
    # uvicorn may not be installed, that's OK
    create_app = None

__version__ = "1.0.0"
__author__ = "Agent A34"
__all__ = [
    'create_app',
    'HealthCheckOrchestrator',
    'RedisHealthChecker',
    'ChromaDBHealthChecker',
    'SystemHealthChecker',
    'EnvironmentChecker',
    'initialize_health_checks',
    'get_health_orchestrator'
]
