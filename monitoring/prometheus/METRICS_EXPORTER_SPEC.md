# InfraFabric Prometheus Metrics Exporter Specification

**Version**: 1.0
**Date**: 2025-11-30
**Author**: Agent A31
**Target Implementation**: Python (prometheus_client), Go (prometheus/client_golang), or custom exporter
**Deployment Port**: 9091 (swarm metrics), 9092 (API metrics)

---

## Overview

This specification defines all Prometheus metrics that power the 5 Grafana dashboards. Each metric must be exported with proper labels, type (counter/gauge/histogram), and cardinality controls to prevent Prometheus memory explosion.

## Metric Naming Convention

All metrics follow Prometheus best practices:
- Prefix: `swarm_`, `redis_`, `chromadb_`, `http_`
- Snake case: `swarm_active_agents_total`
- Suffixes:
  - `_total` → Counter (monotonically increasing)
  - `_seconds`, `_bytes` → Gauge (unit-specific)
  - `_bucket`, `_count`, `_sum` → Histogram (latency buckets)

## Swarm Metrics (swarm_* namespace)

These metrics track overall swarm health and coordination.

### swarm_active_agents_total
- **Type**: Gauge
- **Unit**: Count
- **Description**: Number of currently active agents
- **Labels**: None (global metric)
- **Example Scrape**:
  ```
  # HELP swarm_active_agents_total Number of active agents
  # TYPE swarm_active_agents_total gauge
  swarm_active_agents_total 42
  ```
- **Implementation**:
  ```python
  from prometheus_client import Gauge
  active_agents = Gauge('swarm_active_agents_total', 'Number of active agents')
  active_agents.set(len(active_agents_list))
  ```

### swarm_requests_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Total requests processed by swarm
- **Labels**: None
- **Example Scrape**:
  ```
  swarm_requests_total 125432
  ```
- **Implementation**:
  ```python
  from prometheus_client import Counter
  requests = Counter('swarm_requests_total', 'Total requests')
  requests.inc()
  ```

### swarm_errors_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Total errors encountered
- **Labels**: None
- **Example Scrape**:
  ```
  swarm_errors_total 324
  ```
- **Calculation**: Used to compute error rate = swarm_errors_total / swarm_requests_total

### swarm_latency_seconds_bucket
- **Type**: Histogram
- **Unit**: Seconds
- **Description**: Request latency distribution
- **Buckets**: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
- **Labels**: None
- **Example Scrape**:
  ```
  swarm_latency_seconds_bucket{le="0.001"} 5234
  swarm_latency_seconds_bucket{le="0.01"} 42123
  swarm_latency_seconds_bucket{le="0.1"} 125432
  swarm_latency_seconds_bucket{le="+Inf"} 125432
  swarm_latency_seconds_count 125432
  swarm_latency_seconds_sum 15423.45
  ```
- **Implementation**:
  ```python
  from prometheus_client import Histogram
  latency = Histogram('swarm_latency_seconds', 'Request latency',
                      buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0])
  latency.observe(elapsed_seconds)
  ```

### swarm_task_queue_depth
- **Type**: Gauge
- **Unit**: Count
- **Description**: Tasks waiting in the queue
- **Labels**: None
- **Example Scrape**:
  ```
  swarm_task_queue_depth 127
  ```
- **Implementation**: Increment on task submit, decrement on completion

### swarm_speech_acts_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Speech acts issued by agents
- **Labels**: `action` (SHARE, HOLD, ESCALATE)
- **Example Scrape**:
  ```
  swarm_speech_acts_total{action="SHARE"} 98234
  swarm_speech_acts_total{action="HOLD"} 12443
  swarm_speech_acts_total{action="ESCALATE"} 1234
  ```
- **Implementation**:
  ```python
  speech_acts = Counter('swarm_speech_acts_total', 'Speech acts', ['action'])
  speech_acts.labels(action='SHARE').inc()
  ```
- **IF.search Mapping**: Directly tied to 8-pass investigation phases

### swarm_agents_active
- **Type**: Gauge
- **Unit**: Count
- **Description**: Active agent count by model
- **Labels**: `model` (haiku, sonnet, opus)
- **Example Scrape**:
  ```
  swarm_agents_active{model="haiku"} 40
  swarm_agents_active{model="sonnet"} 2
  swarm_agents_active{model="opus"} 0
  ```

### swarm_task_started_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Tasks started
- **Labels**: None

### swarm_task_completed_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Tasks successfully completed
- **Labels**: None
- **Note**: Used to calculate completion rate = completed / started

### swarm_conflict_detected_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Conflicting findings detected (>threshold difference)
- **Labels**: None
- **Threshold**: Difference > 20% between findings triggers escalation

### swarm_consensus_votes_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Council consensus votes
- **Labels**: `outcome` (approved, rejected, mixed)
- **Example Scrape**:
  ```
  swarm_consensus_votes_total{outcome="approved"} 45
  swarm_consensus_votes_total{outcome="rejected"} 8
  swarm_consensus_votes_total{outcome="mixed"} 12
  ```

### swarm_delegation_success_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Successful task delegations
- **Labels**: None

### swarm_delegation_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Total delegation attempts
- **Labels**: None
- **Calculation**: Success rate = success / total

### swarm_agent_failures_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Agent failures or restarts
- **Labels**: `model` (haiku, sonnet, opus)
- **Example Scrape**:
  ```
  swarm_agent_failures_total{model="haiku"} 3
  swarm_agent_failures_total{model="sonnet"} 0
  swarm_agent_failures_total{model="opus"} 0
  ```

---

## Redis Context Memory Metrics (redis_* namespace)

These metrics monitor L1 and L2 cache tiers (Context Memory).

### redis_ops_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Redis operations by command type
- **Labels**: `operation` (GET, SET, HGET, HSET, LPUSH, LPOP, DEL, INCR, etc.)
- **Example Scrape**:
  ```
  redis_ops_total{operation="GET"} 523421
  redis_ops_total{operation="SET"} 321234
  redis_ops_total{operation="HGET"} 98234
  ```
- **Implementation**:
  ```python
  redis_ops = Counter('redis_ops_total', 'Redis operations', ['operation'])
  redis_ops.labels(operation='GET').inc()
  ```

### redis_command_duration_seconds_bucket
- **Type**: Histogram
- **Unit**: Seconds
- **Description**: Redis command latency
- **Buckets**: [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
- **Example Scrape**:
  ```
  redis_command_duration_seconds_bucket{le="0.001"} 423912
  redis_command_duration_seconds_bucket{le="0.01"} 521234
  redis_command_duration_seconds_bucket{le="+Inf"} 523421
  ```
- **Baseline**: ~0.071ms (p50) per IF-SWARM-S2-COMMS.md

### redis_connection_pool_usage_percent
- **Type**: Gauge
- **Unit**: Percent (0-100)
- **Description**: Connection pool utilization
- **Labels**: None
- **Example Scrape**:
  ```
  redis_connection_pool_usage_percent 42.5
  ```
- **Implementation**:
  ```python
  pool_usage = Gauge('redis_connection_pool_usage_percent', 'Pool usage %')
  pool_usage.set((active_connections / max_connections) * 100)
  ```

### redis_hits_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Cache hits
- **Labels**: None

### redis_misses_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Cache misses
- **Labels**: None
- **Calculation**: Hit ratio = hits / (hits + misses)

### redis_memory_usage_percent
- **Type**: Gauge
- **Unit**: Percent (0-100)
- **Description**: Memory utilization
- **Labels**: None
- **Example Scrape**:
  ```
  redis_memory_usage_percent 68.3
  ```

### redis_eviction_events_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Key eviction events
- **Labels**: None
- **Note**: Spikes indicate memory pressure; correlates with hits/misses

---

## ChromaDB Deep Storage Metrics (chromadb_* namespace)

These metrics monitor semantic search and vector storage (Deep Storage / L2).

### chromadb_query_duration_seconds_bucket
- **Type**: Histogram
- **Unit**: Seconds
- **Description**: Vector query latency by collection
- **Buckets**: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
- **Labels**: `collection` (personality_dna, knowledge, context_archive, openwebui_core, etc.)
- **Example Scrape**:
  ```
  chromadb_query_duration_seconds_bucket{collection="personality_dna",le="0.1"} 4232
  chromadb_query_duration_seconds_bucket{collection="knowledge",le="0.5"} 12342
  ```

### chromadb_embeddings_operations_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Embedding generation operations
- **Labels**: None
- **Example Scrape**:
  ```
  chromadb_embeddings_operations_total 123421
  ```

### chromadb_collection_size_documents
- **Type**: Gauge
- **Unit**: Count
- **Description**: Document count per collection
- **Labels**: `collection`
- **Example Scrape**:
  ```
  chromadb_collection_size_documents{collection="personality_dna"} 1234
  chromadb_collection_size_documents{collection="knowledge"} 9832
  ```

### chromadb_disk_usage_bytes
- **Type**: Gauge
- **Unit**: Bytes
- **Description**: Total disk usage
- **Labels**: None
- **Example Scrape**:
  ```
  chromadb_disk_usage_bytes 34572932123
  ```

### chromadb_query_types_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Query types (semantic, metadata, hybrid)
- **Labels**: `type` (semantic_search, metadata_filter, hybrid, vector_search)
- **Example Scrape**:
  ```
  chromadb_query_types_total{type="semantic_search"} 8234
  chromadb_query_types_total{type="metadata_filter"} 1232
  ```

### chromadb_cache_hits_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Vector cache hits
- **Labels**: None

### chromadb_cache_misses_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Vector cache misses
- **Labels**: None
- **Calculation**: Effectiveness = hits / (hits + misses)

---

## HTTP API Metrics (http_* namespace)

These metrics track user-facing API performance.

### http_requests_total
- **Type**: Counter
- **Unit**: Count
- **Description**: HTTP requests by endpoint
- **Labels**: `endpoint` (/chat, /models, /functions, /pipelines, /admin, etc.)
- **Example Scrape**:
  ```
  http_requests_total{endpoint="/chat"} 234123
  http_requests_total{endpoint="/models"} 12341
  ```

### http_request_duration_seconds_bucket
- **Type**: Histogram
- **Unit**: Seconds
- **Description**: HTTP request latency by endpoint
- **Buckets**: [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
- **Labels**: `endpoint`
- **Example Scrape**:
  ```
  http_request_duration_seconds_bucket{endpoint="/chat",le="0.5"} 198234
  http_request_duration_seconds_bucket{endpoint="/chat",le="1.0"} 234123
  ```

### http_errors_total
- **Type**: Counter
- **Unit**: Count
- **Description**: HTTP errors by status code
- **Labels**: `status` (4xx, 5xx)
- **Example Scrape**:
  ```
  http_errors_total{status="400"} 234
  http_errors_total{status="404"} 123
  http_errors_total{status="500"} 12
  http_errors_total{status="503"} 5
  ```

### http_time_to_first_byte_seconds_bucket
- **Type**: Histogram
- **Unit**: Seconds
- **Description**: Time to first byte for streaming responses
- **Buckets**: [0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
- **Example Scrape**:
  ```
  http_time_to_first_byte_seconds_bucket{le="0.5"} 234123
  http_time_to_first_byte_seconds_bucket{le="1.0"} 238234
  ```
- **SLA Target**: p95 < 0.5s (500ms)

### http_messages_total
- **Type**: Counter
- **Unit**: Count
- **Description**: Chat messages processed
- **Labels**: None

### http_session_duration_seconds_bucket
- **Type**: Histogram
- **Unit**: Seconds
- **Description**: User session duration
- **Buckets**: [30, 60, 300, 600, 1800, 3600, 7200]
- **Example Scrape**:
  ```
  http_session_duration_seconds_bucket{le="300"} 1234
  http_session_duration_seconds_bucket{le="3600"} 2342
  ```

---

## Implementation Patterns

### Python (prometheus_client)

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time

# Swarm metrics
swarm_requests = Counter('swarm_requests_total', 'Total requests')
swarm_errors = Counter('swarm_errors_total', 'Total errors')
swarm_latency = Histogram('swarm_latency_seconds', 'Request latency',
                          buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0])
swarm_agents = Gauge('swarm_active_agents_total', 'Active agents')

# Redis metrics
redis_ops = Counter('redis_ops_total', 'Redis ops', ['operation'])
redis_latency = Histogram('redis_command_duration_seconds', 'Redis latency',
                          buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1])

# Start exporter on port 9091
start_http_server(9091)

# In request handler:
with swarm_latency.time():
    handle_request()
    swarm_requests.inc()
```

### Go (prometheus/client_golang)

```go
package main

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "net/http"
)

var (
    swarmRequests = prometheus.NewCounter(
        prometheus.CounterOpts{
            Name: "swarm_requests_total",
            Help: "Total requests",
        })
    swarmLatency = prometheus.NewHistogram(
        prometheus.HistogramOpts{
            Name: "swarm_latency_seconds",
            Help: "Request latency",
            Buckets: []float64{0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0},
        })
)

func init() {
    prometheus.MustRegister(swarmRequests, swarmLatency)
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":9091", nil)
}
```

### Exporter Registration

Register metrics in Prometheus config:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'infrafabric-swarm'
    static_configs:
      - targets: ['localhost:9091']
    scrape_interval: 15s
    scrape_timeout: 10s

  - job_name: 'infrafabric-api'
    static_configs:
      - targets: ['localhost:9092']
    scrape_interval: 15s
```

---

## Cardinality Management

To prevent Prometheus memory explosion:

### Label Dimension Limits

- **Endpoint labels**: Cap at ~20 unique values (group under /api/*, /chat/*, etc.)
- **Agent model labels**: Only 3 values (haiku, sonnet, opus) - fixed
- **Collection labels**: Expected ~6-10 unique ChromaDB collections
- **Status labels**: Only 4xx, 5xx (avoid per-status-code)

### High-Cardinality Patterns to AVOID

```
# BAD: Creates unique label per request
request_id = request.id  # Millions of unique values!

# GOOD: Use grouped dimensions
endpoint = request.path  # ~20 unique values

# BAD: Track every user
user_id = request.user_id  # Thousands of unique values!

# GOOD: Use aggregated metrics
http_requests_total{endpoint="/chat"}  # One metric with high cardinality
```

### Metric Relabeling

In `prometheus.yml`:

```yaml
metric_relabel_configs:
  # Drop internal labels
  - source_labels: [__name__]
    regex: 'go_.*'
    action: drop

  # Group high-cardinality endpoints
  - source_labels: [endpoint]
    regex: '/api/v[0-9]/.*'
    target_label: 'endpoint'
    replacement: '/api/grouped'
```

---

## Testing Metrics

### Manual Exporter Test

```bash
# Check metrics are exported
curl http://localhost:9091/metrics | grep swarm_

# Verify Prometheus scrapes endpoint
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="infrafabric-swarm")'

# Query metric in Prometheus
curl 'http://localhost:9090/api/v1/query?query=swarm_requests_total'
```

### Load Test

```python
import requests
import time
from prometheus_client import Counter, start_http_server

test_requests = Counter('test_requests_total', 'Test requests')
start_http_server(9091)

for i in range(10000):
    test_requests.inc()
    time.sleep(0.01)

# Check Prometheus: rate(test_requests_total[1m]) should ~= 100 req/sec
```

---

## Dashboard Query Reference

Common PromQL queries used by dashboards:

```promql
# Request rate
rate(swarm_requests_total[1m])

# Error rate percentage
100 * (rate(swarm_errors_total[5m]) / rate(swarm_requests_total[5m]))

# P95 latency
histogram_quantile(0.95, swarm_latency_seconds_bucket) * 1000  # Convert to ms

# Cache hit ratio
rate(redis_hits_total[5m]) / (rate(redis_hits_total[5m]) + rate(redis_misses_total[5m]))

# Task completion rate
100 * (rate(swarm_task_completed_total[5m]) / rate(swarm_task_started_total[5m]))

# Speech acts distribution
sum(swarm_speech_acts_total) by (action)

# Active agents by model
swarm_agents_active{model=~"haiku|sonnet|opus"}
```

---

## Performance Targets

Based on S2 Swarm Communication paper (IF-SWARM-S2-COMMS.md):

| Metric | Target | P95 | P99 |
|--------|--------|-----|-----|
| **Redis latency** | <0.1ms | <10ms | <50ms |
| **Swarm latency** | <100ms | <500ms | <1s |
| **ChromaDB latency** | <100ms | <500ms | <1s |
| **TTFT (streaming)** | <500ms | <1s | <2.5s |
| **Cache hit ratio** | >80% | >60% | >30% |
| **Task completion** | >95% | >90% | >80% |
| **Delegation success** | >95% | >90% | >80% |

---

## Maintenance

### Metric Versioning

- Version 1.0: Initial swarm metrics (2025-11-30)
- Plan for v1.1: Add agent-level latency breakdown, cost per task
- Plan for v2.0: Multi-region swarm metrics (2026 Q1)

### Backward Compatibility

- Never remove metrics (mark as deprecated instead)
- New metrics: add with `_v2` suffix if changing meaning
- Label additions: always add `optional` in documentation

### Cleanup

Disable stale metrics after 6 months:
```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'deprecated_.*'
    action: drop
```

---

**Citation**: `if://doc/prometheus-metrics/v1.0/2025-11-30`
**References**:
- IF-SWARM-S2-COMMS.md (latency baselines)
- Prometheus best practices (naming, cardinality)
- Grafana dashboard specifications (query patterns)
