# InfraFabric Structured Logging & Aggregation System

**Reference:** if://config/logging-system/2025-11-30

## Quick Start

### 1. Deploy Logging Stack

```bash
# Navigate to logging directory
cd /home/setup/infrafabric/monitoring/logging

# Deploy with Docker Compose
docker-compose -f docker-compose-logging.yml up -d

# Verify services are running
docker-compose ps
```

**Services deployed:**
- **Loki** (http://localhost:3100) - Log aggregation
- **Fluent Bit** - Log collector on each node
- **Grafana** (http://localhost:3000) - Visualization (admin/admin)
- **Prometheus** (http://localhost:9090) - Metrics collection

### 2. Update Agent Code

Modify your agents to use structured logging:

```python
from monitoring.logging.logging_library import StructuredLogger, set_correlation_id

# Initialize logger
logger = StructuredLogger(
    agent_id="A1-haiku-001",
    component="redis_bus",
    environment="production"
)

# Set request context
set_correlation_id("req-" + user_request_id)

# Log structured messages
logger.info(
    "Task processed",
    context={"task_id": "task:001", "duration_ms": 42.5},
    if_citation="if://log/task-processed"
)
```

### 3. Query Logs in Grafana

1. Open http://localhost:3000 (admin/admin)
2. Go to Explore > select Loki
3. Try a query:
   ```logql
   {correlation_id="req-abc123"}
   ```
4. See all logs for that request in sequence

## File Structure

```
monitoring/logging/
├── log-schema.json                 # JSON Schema for structured logs
├── fluent-bit.conf                 # Fluent Bit collector config
├── parsers.conf                    # Log format parsers
├── loki-config.yml                 # Loki aggregation config
├── logging-library.py              # Python logging SDK
├── docker-compose-logging.yml      # Docker stack definition
├── grafana-datasource.yml          # Grafana datasource config
├── prometheus.yml                  # Prometheus scrape config
├── LOGGING_ARCHITECTURE.md         # Full system design
├── LOG_QUERIES.md                  # Query cookbook (50+ examples)
└── README.md                       # This file
```

## Core Components

### 1. Structured Logger (logging-library.py)

Python library for agents to emit structured JSON logs:

```python
from logging_library import StructuredLogger, LogLevel, set_correlation_id

logger = StructuredLogger(
    agent_id="A1-haiku-001",
    component="redis_bus",
    environment="production",
    log_level=LogLevel.INFO
)

# Automatic JSON formatting + correlation tracking
logger.info("Task started", context={"task_id": "task:123"})
logger.error("Failed", exception=e, error_code="ERR_TIMEOUT")
logger.log_performance("Process", duration_ms=1234.5)
```

**Features:**
- Automatic JSON serialization
- Correlation ID propagation via context variables
- Batch flushing for efficiency (<1ms write latency)
- Thread-safe operations
- IF.citation integration

### 2. Fluent Bit (fluent-bit.conf)

Lightweight log collector deployed on each node:

**Inputs:**
- Agent JSON logs → `/var/log/infrafabric/agents/*.log`
- Redis logs → `/var/log/redis/redis.log`
- ChromaDB logs → `/var/log/chromadb/*.log`
- API access logs → `/var/log/openwebui/access.log`
- System logs → journald

**Processing:**
- Parse multiple formats (JSON, Redis, syslog, etc.)
- Add metadata (hostname, service, version)
- Extract labels for efficient indexing
- Rate limiting (1000 entries/sec)

**Outputs:**
- Primary: **Loki** (fast aggregation)
- Secondary: **S3** (long-term retention)
- Tertiary: **Elasticsearch** (optional - rich analytics)

### 3. Loki (loki-config.yml)

Centralized log aggregation optimized for distributed systems:

**Architecture:**
```
Fluent Bit agents
    ↓ (2,000+ logs/sec)
Loki Distributor
    ↓
Loki Ingester (batches, compresses)
    ↓
BoltDB + Filesystem
    ↓ (after 30 days)
S3 Cold Storage (7-year retention)
```

**Query Language:** LogQL
```logql
# Find all logs for correlation ID
{correlation_id="req-abc123"}

# Filter by level
{level="ERROR"}

# Aggregate metrics
{component="redis_bus"} | json | stats avg(duration_ms) by agent_id
```

**Performance:**
- Ingest: 2,000-5,000 logs/sec
- Query latency: <5-10s (hot), <30s (cold)
- Storage: 50GB for 30 days (compressed)
- Cardinality limit: 100K unique label combinations

### 4. Grafana (UI + Dashboards)

Visualization dashboard with Loki integration:

**Default dashboards (after provisioning):**
- Request tracing (by correlation_id)
- Error rate monitoring
- Agent load distribution
- Latency percentiles

**Create custom dashboards:**
1. Click "+" → Dashboard
2. Add panel with LogQL query
3. Choose visualization (logs, table, graph)
4. Save and share

## Correlation ID System

### How It Works

Every log automatically includes a `correlation_id` that tracks:

1. **User requests** (req-*): From API → coordinator → agents
2. **Async tasks** (task-*): Background processing flow
3. **Swarm operations** (swarm-*): Multi-agent coordination

**Usage:**

```python
# In request handler
@app.route("/api/process")
def process():
    # Generate and set correlation ID for this request
    set_correlation_id("req-" + uuid.uuid4().hex[:32])

    # All subsequent logs automatically include it
    logger.info("Processing started")     # req-abc123 auto-included

    # Send to other agents - include correlation_id
    await send_to_agent("A2-haiku-002", {
        "task": data,
        "correlation_id": get_correlation_id()  # req-abc123
    })

    # Child agent receives
    set_correlation_id(packet["correlation_id"])  # req-abc123
    logger.info("Task received")  # req-abc123 auto-included
```

**Query all logs for a request:**
```logql
{correlation_id="req-abc123def456"}
```

Returns: All logs from all agents in execution order, enabling:
- End-to-end request tracing
- Latency bottleneck identification
- Error root cause analysis

## Log Format

All logs follow standardized JSON schema (log-schema.json):

```json
{
  "timestamp": "2025-11-30T12:34:56.789Z",
  "level": "INFO",
  "correlation_id": "req-abc123def456",
  "agent_id": "A1-haiku-001",
  "component": "redis_bus",
  "message": "Task claimed successfully",
  "context": {
    "task_id": "task:001",
    "duration_ms": 2.1,
    "batch_size": 100
  },
  "if_citation": "if://log/redis-task-claim",
  "tags": ["redis", "task-processing"],
  "hostname": "agent-node-01",
  "service": "infrafabric"
}
```

**Key fields:**
- **correlation_id**: Links all logs for a request/task/swarm
- **agent_id**: Source agent (A1-haiku-001, etc.)
- **component**: Subsystem (redis_bus, chromadb, etc.)
- **level**: Severity (DEBUG, INFO, WARN, ERROR, FATAL)
- **context**: Operation-specific data
- **if_citation**: Compliance tracking URI
- **performance**: Optional latency/memory metrics
- **error**: Exception details for ERROR/FATAL logs

## Common Tasks

### 1. View Logs for a Request

```bash
# In Grafana Explore:
{correlation_id="req-abc123def456"}

# Or via CLI:
curl -G http://loki:3100/loki/api/v1/query \
  --data-urlencode 'query={correlation_id="req-abc123def456"}' | jq
```

### 2. Find Slow Operations

```logql
{component="redis_bus"} | json duration_ms > 100
```

### 3. Analyze Error Rate

```logql
rate({level="ERROR"}[5m])
```

### 4. Track Task Processing

```logql
{tags="task-processing"} | json | stats count by agent_id
```

### 5. Debug Cross-Swarm Communication

```logql
{swarm_id!="", level="ERROR"} | json | pattern `*swarm*`
```

**More queries:** See `LOG_QUERIES.md` for 50+ examples

### 6. Monitor Agent Health

In Grafana:
1. Create dashboard
2. Add panels:
   - **Active agents:** `count(count_over_time({agent_id!=""}[1h]) by (agent_id))`
   - **Error rate:** `rate({level="ERROR"}[5m])`
   - **Task throughput:** `rate({tags="task-processed"}[1m])`

## Performance Optimization

### For Logging Library

```python
# Use appropriate log levels
logger.debug("Verbose details")      # Only in development
logger.info("Normal operations")     # Production default
logger.warn("Recoverable issues")    # Needs attention
logger.error("Failures")             # Alert-worthy
logger.fatal("System failures")      # Critical alert

# Batch size tuning
logger = StructuredLogger(
    batch_size=100,           # Larger = fewer I/O, higher latency
    flush_interval_seconds=2  # Smaller = lower latency, more I/O
)

# Use context only when needed
logger.info("Started", context={"task_id": "123"})  # Good
logger.debug("x=" + str(x))                         # Avoid string concat
```

### For Fluent Bit

```conf
[FILTER]
    Name          throttle
    Match         agent.*
    Rate          1000       # Don't exceed 1000 logs/sec per stream
    Window        5          # Over 5-second window
```

### For Loki

```yaml
limits_config:
  max_query_lookback: 720h   # 30 days - older queries are slow
  split_queries_by_interval: 24h  # Queries automatically split
```

## Troubleshooting

### Logs not appearing in Loki

```bash
# 1. Check Fluent Bit is running
docker-compose ps fluent-bit

# 2. Verify logs are being written locally
tail -f /var/log/infrafabric/agents/*.log

# 3. Check Fluent Bit logs
docker logs infrafabric-fluent-bit | grep -i error

# 4. Test connection to Loki
curl http://loki:3100/ready
```

### High query latency

```bash
# Query metrics
curl http://loki:3100/metrics | grep loki_logql

# Look for high numbers in:
# - loki_logql_query_duration_seconds
# - loki_ingester_memory_bytes

# Solutions:
# - Use narrower time range
# - Add more label filters
# - Consider Elasticsearch for full-text search
```

### Disk space filling up

```bash
# Check storage
docker exec infrafabric-loki du -sh /loki

# Review retention policy in loki-config.yml:
# - Increase retention_delete_delay
# - Move logs to S3 more frequently
# - Consider distributed Loki deployment
```

## Integration with Existing Systems

### With Redis Bus

```python
# In message handler
async def handle_message(packet):
    # Extract correlation_id from packet
    if "correlation_id" in packet:
        set_correlation_id(packet["correlation_id"])

    logger.info("Message received", context={"from": packet["from_agent"]})
```

### With Audit System

Logs complement the audit system:
- **Logs:** Real-time operational details
- **Audit:** Formal record of decisions, security events, context access

Both use correlation IDs for linking.

### With Guardian Council

Log errors automatically alert guardians:
```python
logger.error("Rate limit exceeded",
    severity="high",
    if_citation="if://audit/security-event/123")

# Guardian council queries:
# {level="ERROR", severity="high"} for escalations
```

## Next Steps

1. **Update all agents** to use StructuredLogger
2. **Set correlation IDs** in request handlers
3. **Create dashboards** for your key metrics
4. **Configure alerts** in Loki ruler or Alertmanager
5. **Test log queries** in LOG_QUERIES.md
6. **Scale to production:** Use distributed Loki + S3 backend

## References

- **Loki Docs:** https://grafana.com/docs/loki/latest/
- **LogQL Reference:** https://grafana.com/docs/loki/latest/logql/
- **Fluent Bit:** https://docs.fluentbit.io/
- **Query Examples:** `LOG_QUERIES.md`
- **Architecture Details:** `LOGGING_ARCHITECTURE.md`
- **Schema Validation:** `log-schema.json`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review `LOG_QUERIES.md` for usage examples
3. Consult `LOGGING_ARCHITECTURE.md` for design details
4. Check Loki/Grafana documentation links above
