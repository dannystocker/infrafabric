# InfraFabric Log Queries - Cookbook

**Reference:** if://doc/log-queries/2025-11-30

This document provides practical LogQL and Elasticsearch queries for common debugging and monitoring tasks.

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [Correlation ID Queries](#correlation-id-queries)
3. [Performance Analysis](#performance-analysis)
4. [Error Analysis](#error-analysis)
5. [Cross-Swarm Debugging](#cross-swarm-debugging)
6. [Operational Monitoring](#operational-monitoring)
7. [Elasticsearch Equivalents](#elasticsearch-equivalents)

---

## Basic Queries

### Query All Logs (Last Hour)

```logql
{component="redis_bus"} |= ""
```

### Query by Log Level

```logql
# All INFO logs
{level="INFO"}

# All errors and above
{level=~"ERROR|FATAL"}

# Exclude debug logs
{level!="DEBUG"}
```

### Query by Component

```logql
# All Redis logs
{component="redis_bus"}

# All audit system logs
{component="audit_system"}

# Multiple components
{component=~"redis_bus|chromadb"}
```

### Query by Agent

```logql
# Specific agent
{agent_id="A1-haiku-001"}

# Agent pattern (all haiku agents)
{agent_id=~".*haiku.*"}
```

### Recent Errors

```logql
{level="ERROR"} | json | __error__ !=""
```

---

## Correlation ID Queries

### Find All Logs for a Request

```logql
{correlation_id="req-abc123def456"}
```

This returns every log entry across all agents for a single user request.

**Output includes:**
- Timestamp sequence
- Agent execution path
- Any errors encountered
- Performance metrics

### Find All Logs for a Task

```logql
{correlation_id="task-xyz789uvw012"}
```

Useful for tracking async/background task execution.

### Find All Swarm Operations

```logql
{swarm_id="swarm-primary-001"}
```

Track all logs from a specific swarm, regardless of agent.

### Cross-Agent Communication Trace

```logql
{correlation_id="req-abc123def456"} | json
| pattern `<agent_id> to <parent_agent_id>`
```

### Correlation ID Distribution

Count how many unique correlation IDs logged in last hour:

```logql
{correlation_id!=""} | json | stats count by correlation_id
```

---

## Performance Analysis

### Slow Operation Detection

Find operations taking >100ms:

```logql
{component="redis_bus"} | json duration_ms > 100
```

### Average Response Time by Agent

```logql
{} | json | stats avg(duration_ms) by agent_id
```

### P95 Latency (95th Percentile)

```logql
{component="redis_bus"}
| json
| stats quantile_over_time(0.95, duration_ms[5m]) by agent_id
```

### Memory Usage Trends

```logql
{} | json | stats avg(memory_mb) by agent_id, timestamp
```

### Task Processing Rate

How many tasks/minute processed by each agent:

```logql
{tags="task-processing"}
| json
| stats rate(count[1m]) by agent_id
```

### Batch Size Analysis

Analyze batch processing efficiency:

```logql
{} | json batch_size > 0 | stats
  count,
  avg(batch_size),
  sum(batch_size) by agent_id
```

---

## Error Analysis

### All Errors in Last Hour

```logql
{level="ERROR"} | json
```

### Error Rate (errors/minute)

```logql
rate({level="ERROR"}[1m])
```

### Specific Error Type

Find all "ConnectionError" exceptions:

```logql
{level="ERROR"} | json error_type = "ConnectionError"
```

### Error by Component

Count errors per component:

```logql
{level="ERROR"} | json | stats count by component
```

### Error Spike Detection

Alert if error rate exceeds 10/minute:

```logql
rate({level="ERROR"}[5m]) > 10
```

### Stack Trace Search

Find errors containing "Redis connection":

```logql
{level="ERROR"} | json | pattern `*Redis connection*`
```

### Fatal Errors

Most critical failures:

```logql
{level="FATAL"} | json
```

---

## Cross-Swarm Debugging

### Find Cross-Swarm Messages

```logql
{} | json swarm_ids_length > 1
```

### Swarm Communication Latency

```logql
{swarm_id!="", tags="cross-swarm"}
| json
| stats avg(duration_ms) by swarm_id
```

### Inter-Agent Messaging Pattern

```logql
{} | json from_agent != "", to_agent != ""
| stats count by from_agent, to_agent
```

### Find Agent-to-Agent Escalations

```logql
{message_type="escalate"}
```

---

## Operational Monitoring

### System Health Check

```logql
{component="system"} | json | stats latest(value) by metric_name
```

### Redis Health

```logql
# Connection pool status
{component="redis_bus", tags="connection-pool"}
| json
| stats latest(status) by agent_id
```

### ChromaDB Status

```logql
{component="chromadb"} | json
| stats count by level
```

### Cache Hit Rate Monitoring

```logql
{component="redis_bus", context_cache_hit=true}
| json
| stats count by agent_id
```

### Rate Limit Warnings

```logql
{level="WARN", message=~".*rate.*limit.*"}
| json
```

### Memory Pressure

```logql
{} | json memory_mb > 500
| stats count by agent_id
```

---

## Advanced Queries

### Request Lifecycle Visualization

Show entire request flow with timing:

```logql
{correlation_id="req-abc123def456"}
| json
| table timestamp, agent_id, component, message, duration_ms
```

**In Grafana:** Select Table visualization to see request flow.

### Multi-Agent Task Coordination

Track when agents hand off work:

```logql
{message_type="request"} | json | stats count by from_agent, to_agent
```

### Network Partition Detection

Find cross-swarm messages that fail:

```logql
{swarm_id!="", level="ERROR"}
| json
| pattern `*swarm*failed*`
```

### Load Balancing Analysis

How evenly are tasks distributed?

```logql
{tags="task-claimed"}
| json
| stats sum(batch_size) by agent_id
```

### Context Access Patterns

Which agents access what context?

```logql
{component="context_manager", operation="read"}
| json
| stats count by agent_id, context_key
```

---

## Elasticsearch Equivalents

If using Elasticsearch instead of Loki:

### Find All Logs for Request

```json
{
  "query": {
    "match": {
      "correlation_id": "req-abc123def456"
    }
  }
}
```

### Error Rate in Kibana

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } },
        { "range": { "timestamp": { "gte": "now-1h" } } }
      ]
    }
  },
  "aggs": {
    "errors_per_minute": {
      "date_histogram": {
        "field": "timestamp",
        "interval": "1m"
      }
    }
  }
}
```

### Slow Operations (>100ms)

```json
{
  "query": {
    "range": {
      "performance.duration_ms": {
        "gte": 100
      }
    }
  },
  "sort": [
    { "performance.duration_ms": { "order": "desc" } }
  ]
}
```

### Error Heatmap

```json
{
  "aggs": {
    "errors_by_component": {
      "terms": { "field": "component" },
      "aggs": {
        "error_count": {
          "filter": { "term": { "level": "ERROR" } }
        }
      }
    }
  }
}
```

---

## CLI Query Examples

### Using curl with Loki API

```bash
# Query logs for last hour
curl -G http://loki:3100/loki/api/v1/query \
  --data-urlencode 'query={component="redis_bus"}' \
  --data-urlencode 'limit=100' | jq .

# Time-range query
curl -G http://loki:3100/loki/api/v1/query_range \
  --data-urlencode 'query={level="ERROR"}' \
  --data-urlencode 'start=2025-11-30T12:00:00Z' \
  --data-urlencode 'end=2025-11-30T13:00:00Z' \
  --data-urlencode 'step=1m' | jq .

# Pretty print JSON logs
curl -s -G http://loki:3100/loki/api/v1/query \
  --data-urlencode 'query={correlation_id="req-abc123"}' | \
  jq '.data.result[].values[] | .[1] | fromjson'
```

### Using grep for local logs

```bash
# Find request in local logs
grep "req-abc123def456" /var/log/infrafabric/agents/*.log | jq .

# Find errors in last hour
find /var/log/infrafabric -mmin -60 -exec grep '"level":"ERROR"' {} +

# Count logs by level
grep -h '"level":' /var/log/infrafabric/agents/*.log | \
  jq -r '.level' | sort | uniq -c
```

---

## Grafana Dashboards

### Creating a Custom Dashboard

1. Open Grafana: http://localhost:3000
2. Click "+" → Dashboard
3. Add panels with queries:

**Panel 1: Request Trace**
```logql
{correlation_id="$correlation_id"}
```

**Panel 2: Error Rate**
```logql
rate({level="ERROR"}[5m])
```

**Panel 3: Agent Load**
```logql
{tags="task-processing"} | json | stats count by agent_id
```

**Panel 4: Latency Distribution**
```logql
{} | json | stats quantile_over_time(0.95, duration_ms[5m]) by agent_id
```

---

## Performance Tips

1. **Use time range:** Queries over large time ranges are slower
   ```logql
   {component="redis_bus"} # Searches last 1h (Loki default)
   ```

2. **Filter early:** Apply label filters before JSON parsing
   ```logql
   {level="ERROR"} | json  # Good
   {} | json | level = "ERROR"  # Slower
   ```

3. **Limit results:** Don't fetch millions of entries
   ```logql
   {component="redis_bus"} | limit 1000
   ```

4. **Use dashboards for monitoring:** Pre-built queries are faster than ad-hoc

5. **Archive old logs:** Move logs >30 days old to S3 for better performance

---

## References

- Loki LogQL Reference: https://grafana.com/docs/loki/latest/logql/
- Grafana Dashboard Docs: https://grafana.com/docs/grafana/latest/dashboards/
- Elasticsearch Query DSL: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html
