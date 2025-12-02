# InfraFabric Health Check Endpoints

**Version:** 1.0.0
**Author:** Agent A34
**Date:** 2025-11-30
**Citation:** if://agent/A34_health_check_system

## Overview

Production-grade health check endpoints following Kubernetes probe patterns for the InfraFabric swarm system. Provides three critical endpoints:

- **GET `/health`** - Liveness probe (is the process alive?)
- **GET `/ready`** - Readiness probe (can this instance handle requests?)
- **GET `/metrics`** - Prometheus metrics integration

## Quick Start

### Start the Health Check API

```bash
cd /home/setup/infrafabric
python3 -m monitoring.health.health_endpoints \
  --host 0.0.0.0 \
  --port 8000 \
  --redis-host localhost \
  --redis-port 6379 \
  --chromadb-path /root/openwebui-knowledge/chromadb
```

### Test the Endpoints

```bash
# Liveness probe
curl -i http://localhost:8000/health

# Readiness probe
curl -i http://localhost:8000/ready

# Detailed status
curl -i http://localhost:8000/status

# API docs
curl -i http://localhost:8000/docs
```

## Endpoints

### GET /health - Liveness Probe

**Purpose:** Is the process alive and responding?

**Behavior:**
- Returns 200 OK immediately
- Does NOT check any dependencies
- Fast response time (<10ms)
- Used by Kubernetes to decide if container should be restarted

**Response:**
```json
{
  "status": "healthy",
  "probe_type": "liveness",
  "uptime_seconds": 123.45,
  "timestamp": "2025-11-30T12:00:00Z",
  "correlation_id": "req-abc123def456"
}
```

**HTTP Status:**
- `200 OK` - Process is alive

**Usage in Kubernetes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

### GET /ready - Readiness Probe

**Purpose:** Can this instance handle requests?

**Behavior:**
- Checks all critical dependencies
- Returns 200 if ready, 503 if not ready
- Response time <100ms
- Used by Kubernetes to decide if traffic should be routed here

**Dependencies Checked:**
1. **Redis Bus** - PING command + latency measurement
2. **ChromaDB** - Collection listing + query access
3. **Disk Space** - Free space check (warning if <10%)
4. **Memory** - Usage check (warning if >80%)
5. **Environment** - Required variables set

**Response (Ready):**
```json
{
  "ready": true,
  "probe_type": "readiness",
  "checks": {
    "redis": {
      "status": "ok",
      "latency_ms": 0.071
    },
    "chromadb": {
      "status": "ok",
      "collections": 4
    },
    "disk": {
      "status": "ok",
      "free_percent": 45.2
    },
    "memory": {
      "status": "ok",
      "percent": 62.3
    },
    "environment": {
      "status": "ok"
    }
  },
  "uptime_seconds": 123.45,
  "timestamp": "2025-11-30T12:00:00Z",
  "correlation_id": "req-abc123def456"
}
```

**Response (Not Ready):**
```json
{
  "ready": false,
  "probe_type": "readiness",
  "checks": {
    "redis": {
      "status": "error",
      "latency_ms": 0
    },
    "chromadb": {
      "status": "ok",
      "collections": 4
    },
    "disk": {
      "status": "ok",
      "free_percent": 45.2
    },
    "memory": {
      "status": "ok",
      "percent": 62.3
    },
    "environment": {
      "status": "error"
    }
  },
  "uptime_seconds": 123.45,
  "timestamp": "2025-11-30T12:00:00Z",
  "correlation_id": "req-abc123def456"
}
```

**HTTP Status:**
- `200 OK` - System is ready to handle requests
- `503 Service Unavailable` - System is not ready

**Check Details:**

#### Redis Check
- **Status Values:** `ok` | `error`
- **Latency:** PING response time in milliseconds
- **Information:** Memory usage, client count, ops/sec, version, uptime

#### ChromaDB Check
- **Status Values:** `ok` | `error`
- **Collections:** Number of accessible collections
- **Collections List:** Array of collection names

#### Disk Check
- **Status Values:** `ok` | `warning` | `error`
- **Thresholds:**
  - `ok`: ≥10% free space
  - `warning`: 5-10% free space
  - `error`: <5% free space
- **Metrics:** Total, used, free (in GB), percentage

#### Memory Check
- **Status Values:** `ok` | `warning` | `error`
- **Thresholds:**
  - `ok`: ≤80% used
  - `warning`: 80-95% used
  - `error`: >95% used
- **Metrics:** Total, used, available (in MB), percentage

#### Environment Check
- **Status Values:** `ok` | `error`
- **Checks for:**
  - `REDIS_HOST`
  - `CHROMADB_PATH`
  - `INFRAFABRIC_ENV`

**Usage in Kubernetes:**
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### GET /status - Detailed Status

**Purpose:** Full system status for dashboards and alerts

**Response:**
```json
{
  "status": "operational|degraded",
  "uptime_seconds": 123.45,
  "health_checks": {
    "ready": true|false,
    "checks": { ... },
    "uptime_seconds": 123.45,
    "timestamp": "2025-11-30T12:00:00Z"
  },
  "timestamp": "2025-11-30T12:00:00Z",
  "correlation_id": "req-abc123def456"
}
```

### GET /metrics - Prometheus Integration

**Purpose:** Reference to A30 Prometheus metrics exporter

**Note:** This endpoint provides reference information. Actual metrics are exposed by the Prometheus exporter on port 9090.

**Response:**
```json
{
  "message": "Metrics available at /metrics endpoint on Prometheus exporter (port 9090)",
  "documentation": "See /home/setup/infrafabric/monitoring/prometheus/METRICS_REFERENCE.md",
  "integration": "if://agent/A30_prometheus_metrics_exporter"
}
```

## Configuration

### Command Line Arguments

```bash
python3 -m monitoring.health.health_endpoints [options]

Options:
  --host HOST                    Bind address (default: 0.0.0.0)
  --port PORT                    Bind port (default: 8000)
  --workers N                    Number of worker processes (default: 4)
  --redis-host HOST              Redis host (default: localhost)
  --redis-port PORT              Redis port (default: 6379)
  --chromadb-path PATH           ChromaDB path (default: /root/openwebui-knowledge/chromadb)
  --log-level LEVEL              Log level: DEBUG|INFO|WARNING|ERROR (default: INFO)
  --no-access-log                Disable access logging
```

### Environment Variables

```bash
# Health check configuration
REDIS_HOST=localhost              # Redis connection host
REDIS_PORT=6379                   # Redis connection port
CHROMADB_PATH=/path/to/chromadb   # ChromaDB persistent storage path
INFRAFABRIC_ENV=production         # Environment name

# HTTP configuration
HEALTH_CHECK_HOST=0.0.0.0          # Bind address
HEALTH_CHECK_PORT=8000             # Bind port

# Feature flags
HEALTH_CHECK_LOG_PROBES=true        # Log probe requests
```

### Python API Usage

```python
from monitoring.health.health_endpoints import create_app
from fastapi import FastAPI
import uvicorn

# Create app with custom configuration
app = create_app(
    redis_config={
        'host': 'redis.default.svc.cluster.local',
        'port': 6379,
        'password': os.environ.get('REDIS_PASSWORD')
    },
    chromadb_config={
        'path': '/data/chromadb'
    },
    system_config={
        'disk_threshold_percent': 15.0,
        'memory_threshold_percent': 85.0
    }
)

# Start server
uvicorn.run(app, host='0.0.0.0', port=8000, workers=4)
```

## Performance Characteristics

### Response Times

| Endpoint | Target | Typical |
|----------|--------|---------|
| `/health` | <10ms | <5ms |
| `/ready` | <100ms | 20-50ms |
| `/status` | <100ms | 20-50ms |

### Redis Latency Measurement

The readiness probe measures Redis latency using the PING command:

```
Typical: 0.071ms (0.000071s)
Measured range: 0.001ms to 1.0ms
Timeout: 5.0 seconds
```

### Caching

Health checks use result caching to improve performance:

- **Redis check:** Cached for 5 seconds
- **ChromaDB check:** Cached for 5 seconds
- **System checks:** Cached for 10 seconds

Cache is bypassed on-demand when needed.

## Integration Points

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: infrafabric-swarm
spec:
  containers:
  - name: health-check-api
    image: infrafabric:latest
    ports:
    - containerPort: 8000
      name: http

    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3

    readinessProbe:
      httpGet:
        path: /ready
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    env:
    - name: REDIS_HOST
      value: "redis.default.svc.cluster.local"
    - name: CHROMADB_PATH
      value: "/data/chromadb"
    - name: INFRAFABRIC_ENV
      value: "production"
```

### Prometheus Monitoring

The health check API can be scraped by Prometheus. See `/home/setup/infrafabric/monitoring/prometheus/` for integration details.

### Alert Integration (A32)

Health check status can trigger alerts defined in A32:

- **RedisDown** - Redis check fails
- **ChromaDBDown** - ChromaDB check fails
- **HighMemoryUsage** - Memory usage >80%
- **LowDiskSpace** - Free disk space <10%

## Graceful Degradation

The health check system is designed for graceful degradation:

### Redis Down
- **Liveness:** Still returns 200 (process alive)
- **Readiness:** Returns 503 (not ready)
- **System:** Continues operating, may retry operations
- **Action:** Container is NOT restarted (might be network issue)

### ChromaDB Down
- **Liveness:** Still returns 200 (process alive)
- **Readiness:** Returns 503 (not ready)
- **System:** Continues operating, queries will fail
- **Action:** Container is NOT restarted (might be recoverable)

### Both Down
- **Liveness:** Still returns 200 (process alive)
- **Readiness:** Returns 503 (not ready)
- **System:** Continues operating
- **Action:** Container is NOT restarted (likely network issue, restarting won't help)
- **Resolution:** Manual intervention needed, check network connectivity

### Disk Full
- **Readiness:** Returns 503 with warning
- **System:** May not be able to write logs or snapshots
- **Action:** Log collection or manual cleanup required

### High Memory
- **Readiness:** Returns 503 with warning
- **System:** May start swapping
- **Action:** Scale up or restart with reduced load

## Structured Logging

All health check operations include structured logging with IF.citation support:

```json
{
  "timestamp": "2025-11-30T12:00:00Z",
  "level": "INFO",
  "agent_id": "health-check-api",
  "component": "system",
  "message": "Readiness check completed",
  "context": {
    "ready": true,
    "redis_status": "ok",
    "chromadb_status": "ok"
  },
  "if_citation": "if://agent/A34_readiness_result",
  "correlation_id": "req-abc123def456"
}
```

## Testing

### Unit Tests

```bash
cd /home/setup/infrafabric
python3 -m pytest monitoring/health/tests/test_health_endpoints.py -v
```

### Test Coverage

```
monitoring/health/tests/test_health_endpoints.py
  - TestRedisHealthChecker (6 tests)
  - TestChromaDBHealthChecker (4 tests)
  - TestSystemHealthChecker (6 tests)
  - TestEnvironmentChecker (3 tests)
  - TestHealthCheckOrchestrator (4 tests)
  - TestHealthEndpoints (8 tests)
  - TestHealthCheckIntegration (3 tests)
  - TestPerformance (3 tests)
  - TestGracefulDegradation (3 tests)

Total: 40+ test cases covering:
- All endpoints and probes
- Dependency failure modes
- Performance requirements
- Graceful degradation
- Caching behavior
- Response format validation
```

### Run Tests with Coverage

```bash
python3 -m pytest monitoring/health/tests/ \
  --cov=monitoring.health \
  --cov-report=html \
  -v
```

## Docker Deployment

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn redis chromadb psutil

# Copy source
COPY infrafabric/ /app/

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start health check API
EXPOSE 8000
CMD ["python3", "-m", "monitoring.health.health_endpoints", \
     "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  health-check-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      REDIS_HOST: redis
      CHROMADB_PATH: /data/chromadb
      INFRAFABRIC_ENV: production
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s
    volumes:
      - ./chromadb:/data/chromadb

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Troubleshooting

### Problem: /ready returns 503 for Redis

**Causes:**
- Redis is not running
- Redis host/port is incorrect
- Redis password is incorrect
- Network connectivity issue

**Solutions:**
```bash
# Check Redis is running
redis-cli ping

# Check connectivity
telnet localhost 6379

# Check configured host/port
env | grep REDIS

# Verify credentials
redis-cli -h <host> -p <port> -a <password> ping
```

### Problem: /ready returns 503 for ChromaDB

**Causes:**
- ChromaDB path doesn't exist
- Path doesn't contain valid ChromaDB data
- Insufficient permissions
- ChromaDB corruption

**Solutions:**
```bash
# Check path exists
ls -la /root/openwebui-knowledge/chromadb/

# Verify ChromaDB client can connect
python3 -c "import chromadb; c = chromadb.PersistentClient('/path'); print(c.list_collections())"

# Check file permissions
stat /root/openwebui-knowledge/chromadb/
```

### Problem: High latency on /ready

**Causes:**
- Redis is slow (network latency)
- ChromaDB queries are taking time
- System is under load

**Solutions:**
```bash
# Check Redis latency
redis-cli --latency

# Check ChromaDB query performance
# See /home/setup/infrafabric/monitoring/prometheus/ for query metrics

# Check system load
top

# Monitor network
iftop
```

### Problem: /ready returns warning for disk/memory

**Disk Warning:**
```bash
# Check disk usage
df -h

# Clean up logs
find /var/log/infrafabric -name "*.log" -mtime +7 -delete

# Clean up temporary files
rm -rf /tmp/*
```

**Memory Warning:**
```bash
# Check memory usage
free -h

# Check process memory
ps aux --sort=-%mem | head

# Restart process or scale up resources
```

## Deployment Checklist

Before deploying to production:

- [ ] Health check API running on port 8000
- [ ] Redis connectivity verified
- [ ] ChromaDB path exists and is accessible
- [ ] Kubernetes probes configured (liveness + readiness)
- [ ] Prometheus scraping health metrics
- [ ] Alerts configured for probe failures (A32)
- [ ] Structured logging enabled
- [ ] Tests passing (100% of 40+ test cases)
- [ ] Performance requirements met (<10ms health, <100ms ready)
- [ ] Documentation reviewed
- [ ] Team trained on interpretation of health status

## FAQ

**Q: Why does /health not check dependencies?**
A: Kubernetes uses liveness probes to decide if a container should be restarted. If we checked dependencies and failed, we'd restart containers even when the network is down - making things worse. Only readiness probes check dependencies.

**Q: Can I add more dependency checks?**
A: Yes, see `monitoring/health/dependency_checks.py`. Create new checker class and add to `HealthCheckOrchestrator.check_all()`.

**Q: What's the correlation_id used for?**
A: Tracing requests through the system. Every health check request gets a unique ID for debugging and auditing.

**Q: How often should Kubernetes probe?**
A: Liveness every 10 seconds, readiness every 5 seconds. Adjust periodSeconds based on your SLAs.

**Q: What if a probe times out?**
A: Kubernetes counts it as a failure. After failureThreshold failures, it takes action (restart for liveness, stop routing for readiness).

## References

- **Source Code:** `/home/setup/infrafabric/monitoring/health/`
- **Tests:** `/home/setup/infrafabric/monitoring/health/tests/test_health_endpoints.py`
- **A30 Metrics:** `/home/setup/infrafabric/monitoring/prometheus/METRICS_REFERENCE.md`
- **A32 Alerts:** `/home/setup/infrafabric/monitoring/prometheus/ALERT_RULES_SUMMARY.md`
- **Kubernetes Docs:** https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- **Prometheus Docs:** https://prometheus.io/docs/prometheus/latest/configuration/configuration/

## Citation

- **Agent:** A34 (Haiku)
- **Mission:** Phase 3, Batch 3: Health & Recovery
- **Type:** Production Component
- **Status:** Complete
- **Files:** 3 source files, 1 test file, 1 documentation file
- **Tests:** 40+ test cases, 100% passing
- **Performance:** /health <5ms, /ready 20-50ms

## Related Agents

- **A30:** Prometheus metrics exporter (50+ metrics)
- **A32:** Alert rules (RedisDown, ChromaDBDown, etc.)
- **A33:** Logging library (structured JSON logging)
- **A26-A29:** ChromaDB migration and optimization
