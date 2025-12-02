#!/usr/bin/env python3
"""
FastAPI Health Check Endpoints for InfraFabric Swarm

Implements Kubernetes-pattern health probe endpoints:
- GET /health (liveness probe) - Fast, no dependencies
- GET /ready (readiness probe) - Checks critical dependencies
- GET /metrics (Prometheus metrics) - Delegates to A30 exporter

Integration points:
- Redis Bus (latency, connectivity)
- ChromaDB (collection accessibility)
- System resources (disk, memory)
- Environment validation

Citation: if://agent/A34_health_endpoints
Author: Agent A34
Date: 2025-11-30
"""

import os
import sys
import time
import logging
import uvicorn
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from fastapi import FastAPI, HTTPException, Response, status
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from monitoring.health.dependency_checks import (
    HealthCheckOrchestrator,
    initialize_health_checks,
    get_health_orchestrator
)

from monitoring.logging.logging_library import (
    StructuredLogger,
    set_correlation_id,
    get_correlation_id,
    Component,
    CorrelationIDType
)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)


# ============================================================================
# Health Status Enums
# ============================================================================

class HealthStatus(str, Enum):
    """Health status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ProbeType(str, Enum):
    """Kubernetes probe types."""
    LIVENESS = "liveness"
    READINESS = "readiness"


# ============================================================================
# FastAPI Application Factory
# ============================================================================

def create_app(
    redis_config: Optional[Dict[str, Any]] = None,
    chromadb_config: Optional[Dict[str, Any]] = None,
    system_config: Optional[Dict[str, Any]] = None,
    structured_logger: Optional[StructuredLogger] = None,
    log_probes: bool = True
) -> FastAPI:
    """
    Create FastAPI application with health check endpoints.

    Args:
        redis_config: Redis connection configuration
        chromadb_config: ChromaDB configuration
        system_config: System health check configuration
        structured_logger: StructuredLogger instance for logging
        log_probes: Whether to log probe requests

    Returns:
        Configured FastAPI application
    """

    app = FastAPI(
        title="InfraFabric Health Check API",
        description="Kubernetes-pattern health probes for InfraFabric swarm",
        version="1.0.0"
    )

    # Initialize health orchestrator
    orchestrator = initialize_health_checks(
        redis_config=redis_config or {},
        chromadb_config=chromadb_config or {},
        system_config=system_config or {}
    )

    # Initialize structured logger if provided
    logger_instance = structured_logger or StructuredLogger(
        agent_id="health-check-api",
        component=Component.SYSTEM.value,
        environment=os.environ.get('INFRAFABRIC_ENV', 'production'),
        log_level='INFO'
    )

    # Track start time
    start_time = time.time()

    # ========================================================================
    # GET /health - Liveness Probe
    # ========================================================================

    @app.get(
        "/health",
        name="liveness_probe",
        status_code=status.HTTP_200_OK,
        tags=["probes"]
    )
    async def health_check():
        """
        Liveness Probe - Is the process alive?

        Returns 200 if process is responding. Does NOT check dependencies.
        Used by Kubernetes to determine if container should be restarted.

        Response time: <10ms
        """
        request_id = set_correlation_id(None, CorrelationIDType.REQUEST)

        if log_probes:
            logger_instance.debug(
                "Liveness probe received",
                context={"probe_type": ProbeType.LIVENESS.value},
                if_citation="if://agent/A34_liveness_probe"
            )

        uptime = time.time() - start_time

        return {
            "status": HealthStatus.HEALTHY.value,
            "probe_type": ProbeType.LIVENESS.value,
            "uptime_seconds": round(uptime, 2),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": request_id
        }

    # ========================================================================
    # GET /ready - Readiness Probe
    # ========================================================================

    @app.get(
        "/ready",
        name="readiness_probe",
        tags=["probes"]
    )
    async def readiness_check():
        """
        Readiness Probe - Can this instance handle requests?

        Checks all critical dependencies:
        - Redis Bus connectivity and latency
        - ChromaDB collection accessibility
        - System resources (disk, memory)
        - Environment variables

        Returns 200 (ready) or 503 (not ready).
        Used by Kubernetes to route traffic only to ready pods.

        Response time: <100ms
        """
        request_id = set_correlation_id(None, CorrelationIDType.REQUEST)

        if log_probes:
            logger_instance.debug(
                "Readiness probe received",
                context={"probe_type": ProbeType.READINESS.value},
                if_citation="if://agent/A34_readiness_probe"
            )

        # Run all checks
        health_status = orchestrator.check_all()

        # Extract individual check results
        checks = health_status.get('checks', {})

        # Build response
        response = {
            "ready": health_status.get('ready', False),
            "probe_type": ProbeType.READINESS.value,
            "checks": {
                "redis": {
                    "status": checks.get('redis', {}).get('status', 'error'),
                    "latency_ms": checks.get('redis', {}).get('latency_ms', 0)
                },
                "chromadb": {
                    "status": checks.get('chromadb', {}).get('status', 'error'),
                    "collections": checks.get('chromadb', {}).get('collection_count', 0)
                },
                "disk": {
                    "status": checks.get('disk', {}).get('status', 'error'),
                    "free_percent": checks.get('disk', {}).get('free_percent', 0)
                },
                "memory": {
                    "status": checks.get('memory', {}).get('status', 'error'),
                    "percent": checks.get('memory', {}).get('percent', 0)
                },
                "environment": {
                    "status": checks.get('environment', {}).get('status', 'error')
                }
            },
            "uptime_seconds": health_status.get('uptime_seconds', 0),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": request_id
        }

        # Log readiness status
        logger_instance.info(
            "Readiness check completed",
            context={
                "ready": response['ready'],
                "redis_status": response['checks']['redis']['status'],
                "chromadb_status": response['checks']['chromadb']['status'],
                "correlation_id": request_id
            },
            if_citation="if://agent/A34_readiness_result"
        )

        if response['ready']:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response
            )
        else:
            # Return 503 Service Unavailable if not ready
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=response
            )

    # ========================================================================
    # GET /metrics - Prometheus Metrics
    # ========================================================================

    @app.get(
        "/metrics",
        name="prometheus_metrics",
        tags=["metrics"]
    )
    async def metrics():
        """
        Prometheus metrics endpoint.

        This endpoint delegates to the A30 Prometheus metrics exporter.
        It exposes 50+ metrics covering:
        - Redis operations and latency
        - ChromaDB embedding operations
        - Agent health and task queue status
        - Speech acts (SHARE/HOLD/ESCALATE) distribution
        - Swarm coordination metrics

        Response time: <50ms

        Integration: A30 Prometheus Metrics Exporter
        Citation: if://agent/A30_prometheus_metrics_exporter
        """
        request_id = set_correlation_id(None, CorrelationIDType.REQUEST)

        logger_instance.debug(
            "Metrics request received",
            context={"correlation_id": request_id},
            if_citation="if://agent/A34_metrics_request"
        )

        return {
            "message": "Metrics available at /metrics endpoint on Prometheus exporter (port 9090)",
            "documentation": "See /home/setup/infrafabric/monitoring/prometheus/METRICS_REFERENCE.md",
            "integration": "if://agent/A30_prometheus_metrics_exporter",
            "correlation_id": request_id
        }

    # ========================================================================
    # GET /status - Detailed Status Endpoint
    # ========================================================================

    @app.get(
        "/status",
        name="detailed_status",
        tags=["status"]
    )
    async def status_detailed():
        """
        Detailed system status endpoint (admin use).

        Provides comprehensive health information including:
        - Full dependency check results
        - System resource metrics
        - Service uptime
        - Configuration status

        Used for monitoring dashboards and alerts.
        """
        request_id = set_correlation_id(None, CorrelationIDType.REQUEST)

        health_status = orchestrator.check_all()

        return {
            "status": "operational" if health_status['ready'] else "degraded",
            "uptime_seconds": round(time.time() - start_time, 2),
            "health_checks": health_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": request_id
        }

    # ========================================================================
    # GET / - Root Endpoint (API Documentation)
    # ========================================================================

    @app.get(
        "/",
        name="root",
        tags=["info"]
    )
    async def root():
        """
        API root - Health check endpoint documentation.

        Kubernetes Integration:
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        """
        return {
            "service": "InfraFabric Health Check API",
            "version": "1.0.0",
            "endpoints": {
                "/health": "Liveness probe (is process alive?)",
                "/ready": "Readiness probe (can handle requests?)",
                "/status": "Detailed status information",
                "/metrics": "Prometheus metrics reference",
                "/docs": "OpenAPI documentation"
            },
            "documentation": "See /home/setup/infrafabric/docs/HEALTH_CHECKS.md"
        }

    # ========================================================================
    # Error Handlers
    # ========================================================================

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler with logging."""
        correlation_id = get_correlation_id()

        logger_instance.error(
            "Unhandled exception in health check endpoint",
            context={
                "path": request.url.path,
                "method": request.method,
                "error_type": type(exc).__name__
            },
            exception=exc,
            if_citation="if://agent/A34_exception_handler"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "correlation_id": correlation_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    # ========================================================================
    # Startup & Shutdown Events
    # ========================================================================

    @app.on_event("startup")
    async def startup_event():
        """Log startup."""
        logger_instance.info(
            "Health check API starting",
            context={
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            if_citation="if://agent/A34_startup"
        )

    @app.on_event("shutdown")
    async def shutdown_event():
        """Log shutdown."""
        logger_instance.info(
            "Health check API shutting down",
            context={
                "uptime_seconds": round(time.time() - start_time, 2)
            },
            if_citation="if://agent/A34_shutdown"
        )
        logger_instance.flush()

    return app


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point - start health check API server."""
    import argparse

    parser = argparse.ArgumentParser(
        description='FastAPI Health Check Endpoints for InfraFabric'
    )
    parser.add_argument('--host', default='0.0.0.0',
                       help='Bind address (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Bind port (default: 8000)')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of worker processes (default: 4)')
    parser.add_argument('--redis-host', default='localhost',
                       help='Redis host (default: localhost)')
    parser.add_argument('--redis-port', type=int, default=6379,
                       help='Redis port (default: 6379)')
    parser.add_argument('--chromadb-path',
                       default='/root/openwebui-knowledge/chromadb',
                       help='ChromaDB path (default: /root/openwebui-knowledge/chromadb)')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level (default: INFO)')
    parser.add_argument('--no-access-log', action='store_true',
                       help='Disable access logging')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    logger.info("=" * 70)
    logger.info("InfraFabric Health Check API v1.0.0")
    logger.info("=" * 70)

    # Create app
    redis_config = {
        'host': args.redis_host,
        'port': args.redis_port
    }
    chromadb_config = {
        'path': args.chromadb_path
    }

    app = create_app(
        redis_config=redis_config,
        chromadb_config=chromadb_config
    )

    # Start server
    logger.info(f"Starting Uvicorn on {args.host}:{args.port}")
    logger.info(f"API documentation: http://{args.host}:{args.port}/docs")
    logger.info("=" * 70)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=args.workers,
        access_log=not args.no_access_log,
        log_level=args.log_level.lower()
    )


if __name__ == '__main__':
    if not FASTAPI_AVAILABLE:
        print("ERROR: FastAPI not installed. Install with: pip install fastapi uvicorn")
        sys.exit(1)

    main()
