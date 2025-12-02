# Health Check System Quick Start Guide

**Fast reference for using the InfraFabric Health Check System**

## Installation

### Prerequisites
```bash
pip install fastapi uvicorn redis chromadb psutil pyyaml
```

### Verify Installation
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/setup/infrafabric')
from monitoring.health.dependency_checks import HealthCheckOrchestrator
print("✓ Health Check system ready!")
EOF
```

## Starting the Health Check API

```bash
cd /home/setup/infrafabric

# Basic startup
python3 -m monitoring.health.health_endpoints

# Custom configuration
python3 -m monitoring.health.health_endpoints \
  --host 0.0.0.0 \
  --port 8000 \
  --redis-host localhost \
  --redis-port 6379 \
  --chromadb-path /root/openwebui-knowledge/chromadb \
  --log-level INFO
```

API documentation available at: http://localhost:8000/docs

## Testing Endpoints

### Liveness Probe (Is process alive?)
```bash
curl -i http://localhost:8000/health
# Expected: 200 OK in <10ms
```

### Readiness Probe (Can handle requests?)
```bash
curl -i http://localhost:8000/ready
# Expected: 200 OK if ready, 503 Service Unavailable if not ready
```

### Detailed Status
```bash
curl -i http://localhost:8000/status
# Returns comprehensive health information
```

### JSON Response Example
```json
{
  "ready": true,
  "checks": {
    "redis": {
      "status": "ok",
      "latency_ms": 0.5
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

## CLI Tool Usage

### Check All Components
```bash
python3 monitoring/health/health_cli.py check
```

Output example:
```
=====================================================================
InfraFabric Health Check
=====================================================================

REDIS
  Status: ✓ OK
  Latency: 0.5ms

CHROMADB
  Status: ✓ OK
  Collections: 4

DISK
  Status: ✓ OK
  Free: 45.2% (250.5GB / 554.0GB)

MEMORY
  Status: ✓ OK
  Used: 62.3% (4992MB / 8000MB)

ENVIRONMENT
  Status: ✓ OK

=====================================================================
Overall Status: Ready
Uptime: 123.45s
Timestamp: 2025-11-30T12:00:00Z
=====================================================================
```

### Check Specific Component
```bash
python3 monitoring/health/health_cli.py check --component redis --detailed
```

### Watch Mode (Continuous Monitoring)
```bash
python3 monitoring/health/health_cli.py watch --interval 5
```

Auto-updates every 5 seconds. Press Ctrl+C to exit.

### Export Status

**JSON (machine-readable):**
```bash
python3 monitoring/health/health_cli.py status --format json
```

**YAML (human-readable):**
```bash
python3 monitoring/health/health_cli.py status --format yaml
```

**Prometheus metrics:**
```bash
python3 monitoring/health/health_cli.py status --format prometheus
```

**CSV (spreadsheet):**
```bash
python3 monitoring/health/health_cli.py status --format csv
```

### Configuration Management
```bash
# Display current configuration
python3 monitoring/health/health_cli.py config show

# Validate configuration
python3 monitoring/health/health_cli.py config validate
```

## Configuration

### Configuration File
Location: `/home/setup/infrafabric/monitoring/health/health_config.yml`

### Key Settings
```yaml
global:
  check_interval_seconds: 5        # How often to check (def: 5s)
  check_timeout_seconds: 30        # Overall timeout (def: 30s)
  enable_caching: true             # Cache results for performance
  cache_ttl_seconds: 5             # Cache lifetime (def: 5s)

redis:
  critical: true                   # Blocks readiness if fails
  thresholds:
    latency_p99_ms: 10             # Warning if >10ms
    memory_usage_percent_critical: 95

chromadb:
  critical: true
  total_expected_docs: 9832
  thresholds:
    query_latency_p99_ms: 100
    doc_count_missing_percent_critical: 25

system:
  disk:
    free_percent_critical: 5       # Error if <5% free
  memory:
    used_percent_critical: 95      # Error if >95% used
```

## Environment Variables

```bash
# Set these before starting the API
export REDIS_HOST=localhost
export REDIS_PORT=6379
export CHROMADB_PATH=/root/openwebui-knowledge/chromadb
export INFRAFABRIC_ENV=production
export INFRAFABRIC_LOG_LEVEL=INFO
```

## Docker Deployment

### Docker Compose
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

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Run with Docker Compose
```bash
docker-compose -f monitoring/health/docker-compose-health.yml up
```

## Kubernetes Deployment

### Health Probe Configuration
```yaml
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
```

## Troubleshooting

### Problem: /ready returns 503 for Redis

**Check Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**Check connectivity:**
```bash
telnet localhost 6379
# Should connect successfully
```

**Check logs:**
```bash
tail -f /var/log/redis/redis-server.log
```

### Problem: /ready returns 503 for ChromaDB

**Verify path exists:**
```bash
ls -la /root/openwebui-knowledge/chromadb/
```

**Test ChromaDB connection:**
```bash
python3 << 'EOF'
import chromadb
client = chromadb.PersistentClient(path='/root/openwebui-knowledge/chromadb')
print(client.list_collections())
EOF
```

### Problem: High latency on /ready (>100ms)

**Check Redis latency:**
```bash
redis-cli --latency
```

**Check system load:**
```bash
top
```

**Check network:**
```bash
iftop  # if installed
```

### Problem: Memory or Disk warnings

**Check memory usage:**
```bash
free -h
```

**Check disk usage:**
```bash
df -h
```

**Free up space:**
```bash
# Clean logs
find /var/log -name "*.log" -mtime +7 -delete

# Clean temp files
rm -rf /tmp/*
```

## Performance Expectations

| Endpoint | Response Time | Latency SLA |
|----------|---------------|------------|
| `/health` | 2-5ms | <10ms ✓ |
| `/ready` | 20-50ms | <100ms ✓ |
| `/status` | 30-60ms | <150ms ✓ |
| `/metrics` | 5-10ms | <50ms ✓ |

## Health Check Thresholds

### Redis
- ✓ **OK:** Latency <5ms, Memory <80%
- ⚠ **Warning:** Latency 5-10ms, Memory 80-95%
- ✗ **Error:** Latency >50ms, Memory >95%

### ChromaDB
- ✓ **OK:** Query latency <50ms, Collections accessible
- ⚠ **Warning:** Query latency 50-100ms
- ✗ **Error:** Query latency >500ms, Collections inaccessible

### System Disk
- ✓ **OK:** Free space >20%
- ⚠ **Warning:** Free space 10-20%
- ✗ **Error:** Free space <5%

### System Memory
- ✓ **OK:** Usage <75%
- ⚠ **Warning:** Usage 75-80%
- ✗ **Error:** Usage >95%

## Running Tests

### All Tests
```bash
python3 -m pytest monitoring/health/tests/ -v
```

### Specific Test
```bash
python3 -m pytest monitoring/health/tests/test_health_cli.py::TestHealthCheckCLI -v
```

### With Coverage
```bash
python3 -m pytest monitoring/health/tests/ \
  --cov=monitoring.health \
  --cov-report=html \
  -v
```

## Integration with Monitoring Stack

### Prometheus Scraping
Add to `/home/setup/infrafabric/monitoring/prometheus/prometheus.yml`:

```yaml
- job_name: 'health-check'
  scrape_interval: 10s
  static_configs:
    - targets: ['localhost:8000']
  metrics_path: '/metrics'
```

### Grafana Dashboard
Import dashboard for health metrics visualization.

### Alert Rules
Configure alerts in Alert Manager for:
- RedisDown (P0)
- ChromaDBDown (P0)
- HighMemory (P1)
- LowDiskSpace (P1)

## Quick Diagnostics

```bash
# All in one health check
curl -s http://localhost:8000/ready | python3 -m json.tool

# Export for analysis
python3 monitoring/health/health_cli.py status --format json > health_status.json

# Monitor continuously
python3 monitoring/health/health_cli.py watch --interval 2

# Check specific component with details
python3 monitoring/health/health_cli.py check --component redis --detailed
```

## Next Steps

1. **Start API:** `python3 -m monitoring.health.health_endpoints`
2. **Test endpoints:** Use curl or Postman
3. **Configure CLI:** Adjust `health_config.yml` as needed
4. **Set up Kubernetes:** Configure liveness & readiness probes
5. **Enable monitoring:** Integrate with Prometheus (A30) & Alerts (A32)
6. **Create dashboards:** Grafana visualization of health metrics
7. **Set up alerting:** Configure Alert Manager rules

## Files Reference

| File | Purpose |
|------|---------|
| `health_endpoints.py` | FastAPI application factory |
| `dependency_checks.py` | Component health checkers |
| `health_cli.py` | CLI tool |
| `health_config.yml` | Configuration file |
| `HEALTH_CHECKS.md` | Complete API reference |
| `HEALTH_CHECK_ARCHITECTURE.md` | System architecture guide |

## Support

For detailed information, see:
- `/home/setup/infrafabric/docs/HEALTH_CHECKS.md` - Complete reference
- `/home/setup/infrafabric/docs/HEALTH_CHECK_ARCHITECTURE.md` - Architecture guide
- `/home/setup/infrafabric/monitoring/health/IMPLEMENTATION_SUMMARY.md` - Implementation details

## FAQ

**Q: How often should health checks run?**
A: Default is every 5 seconds. Configure `check_interval_seconds` in `health_config.yml`.

**Q: What if a dependency is temporarily down?**
A: Circuit breaker waits 30 seconds then retries. Meanwhile, readiness returns 503.

**Q: Can I add custom health checks?**
A: Yes! Create a new checker class in `dependency_checks.py` and add to orchestrator.

**Q: Why are results cached?**
A: Improves performance and reduces load on dependencies (especially for disk/system checks).

**Q: What's the correlation ID?**
A: Unique ID for tracing requests through the monitoring system for debugging.

---

**Last Updated:** 2025-11-30
**Version:** 1.0.0
**Agent:** A34
