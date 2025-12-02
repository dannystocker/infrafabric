# InfraFabric Grafana Dashboards

Production-grade Grafana dashboards for monitoring InfraFabric swarm performance, latency, and error metrics across all critical infrastructure components.

## Overview

This package contains 5 dashboards visualizing metrics from the S2 Swarm Communication architecture:

1. **Swarm Overview** - Executive view of swarm health and request flow
2. **Redis Performance** - Context Memory operations, latency, and cache efficiency
3. **ChromaDB Performance** - Deep Storage queries, embeddings, and collection health
4. **Agent Health & Coordination** - Individual agent status, consensus, and coordination metrics
5. **API & User Experience** - Endpoint latency, throughput, and session analytics

## Prerequisites

### Grafana Installation
- Grafana 8.0+ (tested on 8.x, 9.x, 10.x)
- Datasource: Prometheus (http://prometheus:9090)

### Prometheus Setup
Ensure your Prometheus instance scrapes the metrics exporter endpoints:

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

### Required Metrics

The dashboards expect the following metrics to be exported by your application. If any metrics are unavailable, panels will show "No data".

#### Swarm Metrics
- `swarm_active_agents_total` - Number of active agents (gauge)
- `swarm_requests_total` - Total requests processed (counter)
- `swarm_errors_total` - Total errors (counter)
- `swarm_latency_seconds_bucket` - Request latency histogram
- `swarm_task_queue_depth` - Tasks pending in queue (gauge)
- `swarm_speech_acts_total` - Count of SHARE/HOLD/ESCALATE speech acts (counter by `action` label)

#### Redis Context Memory Metrics
- `redis_ops_total` - Operations by type: GET, SET, HGET, HSET, LPUSH, LPOP (counter by `operation` label)
- `redis_command_duration_seconds_bucket` - Command latency histogram
- `redis_connection_pool_usage_percent` - Pool utilization (gauge, 0-100)
- `redis_hits_total` - Cache hit count (counter)
- `redis_misses_total` - Cache miss count (counter)
- `redis_memory_usage_percent` - Memory utilization (gauge, 0-100)
- `redis_eviction_events_total` - Number of evictions (counter)

#### ChromaDB Deep Storage Metrics
- `chromadb_query_duration_seconds_bucket` - Query latency histogram (labels: `collection`)
- `chromadb_embeddings_operations_total` - Embedding operations (counter)
- `chromadb_collection_size_documents` - Document count per collection (gauge, labels: `collection`)
- `chromadb_disk_usage_bytes` - Disk usage (gauge)
- `chromadb_query_types_total` - Queries by type (counter by `type` label)
- `chromadb_cache_hits_total` - Cache hits (counter)
- `chromadb_cache_misses_total` - Cache misses (counter)

#### Agent Metrics
- `swarm_agents_active` - Active agents (gauge by `model` label: haiku, sonnet, opus)
- `swarm_task_started_total` - Tasks started (counter)
- `swarm_task_completed_total` - Tasks completed (counter)
- `swarm_conflict_detected_total` - Conflict detection events (counter)
- `swarm_consensus_votes_total` - Consensus votes (counter by `outcome` label)
- `swarm_delegation_success_total` - Successful delegations (counter)
- `swarm_delegation_total` - Total delegation attempts (counter)
- `swarm_agent_failures_total` - Agent failures/restarts (counter by `model` label)

#### API & UX Metrics
- `http_requests_total` - HTTP requests (counter by `endpoint` label)
- `http_request_duration_seconds_bucket` - Request latency histogram (labels: `endpoint`)
- `http_errors_total` - HTTP errors (counter by `status` label)
- `http_time_to_first_byte_seconds_bucket` - TTFB for streaming (histogram)
- `http_messages_total` - Message count (counter)
- `http_session_duration_seconds_bucket` - Session duration histogram

## Dashboard Import Instructions

### Option 1: Import from JSON (Recommended)

1. **Open Grafana**: Navigate to `http://your-grafana:3000`

2. **Navigate to Dashboards**:
   - Click "Dashboards" in left sidebar
   - Click "New" → "Import"

3. **Upload Dashboard JSON**:
   - Click "Upload JSON file" or paste the JSON content
   - Select from `/home/setup/infrafabric/monitoring/grafana/dashboards/`:
     - `swarm_overview.json`
     - `redis_performance.json`
     - `chromadb_performance.json`
     - `agent_health.json`
     - `api_ux.json`

4. **Configure Datasource**:
   - Select "Prometheus" as the datasource
   - Confirm the URL matches your Prometheus instance
   - Click "Import"

### Option 2: Bulk Import via API

```bash
#!/bin/bash
GRAFANA_URL="http://localhost:3000"
GRAFANA_API_KEY="your_api_key_here"
DASHBOARD_DIR="/home/setup/infrafabric/monitoring/grafana/dashboards"

for dashboard in $DASHBOARD_DIR/*.json; do
    echo "Importing $(basename $dashboard)..."

    # Add Prometheus datasource reference
    cat "$dashboard" | jq '.overwrite=true' | \
    curl -X POST \
      -H "Authorization: Bearer $GRAFANA_API_KEY" \
      -H "Content-Type: application/json" \
      -d @- \
      "$GRAFANA_URL/api/dashboards/db"

    echo "Imported $(basename $dashboard)"
done
```

### Option 3: Manual Dashboard URL

After importing a dashboard, share it via:
```
http://your-grafana:3000/d/swarm_overview
http://your-grafana:3000/d/redis_performance
http://your-grafana:3000/d/chromadb_performance
http://your-grafana:3000/d/agent_health
http://your-grafana:3000/d/api_ux
```

## Dashboard Descriptions

### 1. Swarm Overview (swarm_overview.json)

**Purpose**: Executive-level view of swarm health and system performance.

**Key Panels**:
- **Active Agents Over Time** (timeseries) - Tracks agent count changes, identifies scaling events
- **Request Rate (req/sec)** (stat) - Shows current request throughput
- **Error Rate (%)** (stat) - Calculated from request and error counters; RED > 10% triggers alert
- **P95 Latency (ms)** (stat) - Tail latency; RED > 500ms
- **Task Queue Depth** (stat) - Pending work; RED > 500 indicates backlog
- **Speech Acts Distribution** (pie chart) - Ratio of SHARE/HOLD/ESCALATE decisions by IF.search 8-pass

**Alert Thresholds**:
- Green: Request rate < 500 req/sec, error rate < 5%, latency < 100ms
- Yellow: Request rate 500-1000, error rate 5-10%, latency 100-500ms
- Red: Request rate > 1000, error rate > 10%, latency > 500ms

**Use Cases**:
- Monitor swarm stability during large deployments
- Detect cascading failures via queue depth spikes
- Validate S2 coordination effectiveness via speech acts ratio

---

### 2. Redis Performance (redis_performance.json)

**Purpose**: Monitor Context Memory tier (L1 fast cache) operational health.

**Key Panels**:
- **Redis Operations/sec by Type** (timeseries) - Breakdown of GET/SET/HGET/HSET/LPUSH/LPOP
- **Redis Latency Heatmap** (timeseries) - p50/p95/p99; target: p95 < 10ms
- **Connection Pool Usage** (stat) - Current pool utilization; RED > 95%
- **Cache Hit/Miss Ratio** (timeseries) - Higher is better; target > 80%
- **Memory Usage (%)** (stat) - Total heap utilization; RED > 90%
- **Eviction Events (5m)** (bars) - Number of keys evicted; spikes indicate memory pressure

**Alert Thresholds**:
- Green: Latency p95 < 10ms, pool < 80%, hit ratio > 80%, memory < 70%
- Yellow: Latency 10-50ms, pool 80-95%, hit ratio 50-80%, memory 70-90%
- Red: Latency > 50ms, pool > 95%, hit ratio < 50%, memory > 90%

**Metrics from S2 Swarm Communication Paper**:
- Baseline latency: ~0.071ms (Redis Bus performance benchmark from Instance #8)
- Cache tier supports 100K+ ops/sec

**Use Cases**:
- Identify cache saturation before evictions
- Detect memory leaks via trending graphs
- Verify Redis backend health for coordinator operations

---

### 3. ChromaDB Performance (chromadb_performance.json)

**Purpose**: Monitor Deep Storage tier (L2 persistent vector database).

**Key Panels**:
- **Query Latency by Collection** (timeseries) - p95 per collection; target < 100ms
- **Embeddings Operations/sec** (timeseries) - Embedding generation rate
- **Collection Sizes (document counts)** (timeseries) - Growth trend per collection
- **Disk Usage Trend** (timeseries) - Storage growth; RED > 80% capacity
- **Query Types Distribution** (pie chart) - Semantic search, metadata filter, etc.
- **Cache Effectiveness (%)** (stat) - Vector cache hit ratio; RED < 30%

**Alert Thresholds**:
- Green: Latency < 100ms, disk < 50%, cache > 60%
- Yellow: Latency 100-500ms, disk 50-80%, cache 30-60%
- Red: Latency > 500ms, disk > 80%, cache < 30%

**Context from IF.emotion & ChromaDB Architecture**:
- Collections: personality_dna:{agent_id}, knowledge:{vertical}, context_archive:{session_id}
- Embeddings enable semantic search for agent memory retrieval
- 9,832 chunks indexed across 6 OpenWebUI collections (Proxmox deployment)

**Use Cases**:
- Track vector embedding generation bottlenecks
- Monitor collection growth and disk saturation
- Validate semantic search effectiveness via query latency

---

### 4. Agent Health & Coordination (agent_health.json)

**Purpose**: Detailed agent lifecycle, coordination patterns, and consensus mechanics.

**Key Panels**:
- **Active Agents by Model** (stacked area) - Haiku/Sonnet/Opus instance count
- **Task Completion Rate (%)** (stat) - Completed / Started; RED < 80%
- **Speech Acts Timeline** (timeseries) - SHARE/HOLD/ESCALATE rate over time
- **Conflict Detection Events** (stat) - 5-minute rolling count; RED > 10
- **Consensus Vote Outcomes** (pie) - Approved / Rejected / Mixed votes
- **Delegation Success Rate (%)** (stat) - Successful / Total delegations
- **Agent Failures/Restarts** (bars) - By model; RED indicates instability

**Alert Thresholds**:
- Green: Completion rate > 95%, success rate > 95%, failures < 1/min
- Yellow: Completion rate 80-95%, success rate 90-95%, conflicts 5-10/min
- Red: Completion rate < 80%, success rate < 90%, failures > 1/min or conflicts > 10/min

**IF.TTT Compliance**:
- Conflict detection ensures conflicting findings are escalated per IF.search pass 3
- Consensus outcomes are logged with citations
- Delegation tracking enables audit trail reconstruction

**Use Cases**:
- Diagnose agent stuck states via completion rate drops
- Validate IF.search 8-pass coordination via speech acts distribution
- Track consensus effectiveness across council votes
- Identify flaky agents via restart frequency

---

### 5. API & User Experience (api_ux.json)

**Purpose**: End-user SLA metrics and API endpoint performance.

**Key Panels**:
- **Request Rate by Endpoint** (timeseries) - Requests/sec per API route
- **Latency by Endpoint** (timeseries) - p50/p95/p99 per endpoint
- **Error Rate by Status Code** (stacked bars) - 4xx/5xx breakdown
- **Time-to-First-Token (TTFT)** (stat) - Streaming response latency
- **Message Throughput** (timeseries) - Messages/sec (chat volume)
- **User Session Durations** (timeseries) - P95 session length

**Alert Thresholds**:
- Green: Latency p95 < 200ms, error rate < 1%, TTFT < 500ms
- Yellow: Latency p95 200-500ms, error rate 1-5%, TTFT 500-1000ms
- Red: Latency p95 > 500ms, error rate > 5%, TTFT > 1000ms

**User Experience Goals**:
- TTFT < 500ms ensures conversational feel
- P95 latency < 200ms meets human perception thresholds
- Session duration trending indicates engagement quality

**Use Cases**:
- Debug API performance regressions via endpoint breakdowns
- Monitor streaming response quality via TTFT
- Correlate error spikes with deployment changes
- Track user engagement via session duration

---

## Configuration

### Time Range Selector

All dashboards include a time range dropdown with presets:
- **1h** - Recent monitoring (default)
- **6h** - Daily trend analysis
- **24h** - Multi-shift performance
- **7d** - Weekly patterns and anomalies

Use the Grafana date picker (top-right) for custom ranges.

### Auto-Refresh

Dashboards are set to refresh on preset intervals:
- **10s** - Real-time monitoring (high-frequency swarms)
- **30s** - Standard monitoring
- **1m** - Trending analysis (less sensitive to noise)

Change via Grafana's refresh button or include `&refresh=30s` in dashboard URL.

### Variable Templates

Dashboards include dynamic variable dropdowns for filtering:

**Swarm Overview**:
- `job` - Prometheus scrape job selector

**Redis Performance**:
- None (instance-wide metrics)

**ChromaDB Performance**:
- `collection` - Filter by ChromaDB collection name

**Agent Health**:
- `agent_model` - Filter by model (haiku/sonnet/opus)

**API & UX**:
- `endpoint` - Filter by API endpoint

## Advanced: Custom Alerts

### Grafana Alert Rules

Once dashboards are imported, create alert rules:

1. **P95 Latency Spike Alert**:
   ```
   histogram_quantile(0.95, swarm_latency_seconds_bucket) > 0.5
   for 5m
   ```

2. **Agent Failure Alert**:
   ```
   rate(swarm_agent_failures_total[5m]) > 0.016  # > 1 failure/min
   ```

3. **Cache Eviction Alert**:
   ```
   increase(redis_eviction_events_total[5m]) > 100
   ```

4. **ChromaDB Disk Alert**:
   ```
   chromadb_disk_usage_bytes / (100*1073741824) > 0.8  # > 80% of 100GB
   ```

### Integration with Notification Channels

Configure notification destinations in Grafana:
- Email
- Slack (recommended for ops)
- PagerDuty (for P0 incidents)
- Webhook (custom integrations)

## Troubleshooting

### "No Data" in Panels

**Cause**: Metrics not being scraped.

**Fix**:
1. Verify Prometheus job in `prometheus.yml` targets the exporter
2. Check exporter is running: `curl http://localhost:9091/metrics` (or 9092)
3. Verify metric names match dashboard queries
4. Check Grafana datasource URL: Settings → Datasources → Prometheus

### High Latency Spikes

**Investigation Steps**:
1. Check **Swarm Overview** task queue depth
   - If high: backlog exists; check agent task completion rate
2. Check **Redis Performance** latency heatmap
   - If p95 > 50ms: Redis bottleneck; check memory usage and eviction events
3. Check **ChromaDB Performance** query latency
   - If high: slow semantic search; check disk I/O and cache hit ratio
4. Check **Agent Health** failure rate
   - If high: agents crashing; check logs for timeout/OOM

### Memory Leaks

**Trending Analysis**:
1. Open **Redis Performance** dashboard
2. Set time range to 7d
3. Check memory usage trend line
   - Steady increase indicates leak
   - Examine eviction events for correlation

## Exporting & Sharing

### Export Dashboard JSON

1. Click dashboard settings (gear icon, top-right)
2. Select "Save as..."
3. Copy JSON, version control in git
4. Share URL: `http://your-grafana:3000/d/swarm_overview`

### Create Snapshots

1. Click dashboard settings
2. Select "Snapshot"
3. Snapshot is publicly viewable (no auth required)
4. Share snapshot URL for incident post-mortems

## Performance Tuning

### Prometheus Query Optimization

If dashboards load slowly:

1. Reduce scrape frequency: `scrape_interval: 30s` (if real-time isn't critical)
2. Increase Prometheus retention: `--storage.tsdb.retention.time=30d`
3. Add query caching via Trickster proxy
4. Increase Grafana dashboard cache time: Settings → Features → Dashboard cache

### High-Cardinality Labels

If Prometheus memory grows unbounded:

1. Reduce label dimensions (avoid unique IDs per request)
2. Use metric relabeling to drop unused labels
3. Partition metrics by job (separate scrape configs)

Example `prometheus.yml` cardinality control:

```yaml
global:
  external_labels:
    cluster: infrafabric
    environment: production

metric_relabel_configs:
  # Drop high-cardinality labels
  - source_labels: [__name__]
    regex: 'http_request_.*'
    target_label: 'endpoint'
    replacement: 'grouped'  # Coalesce unique endpoints
```

## Documentation

### S2 Swarm Communication Paper

All metrics and SLA targets are grounded in:
- **File**: `/home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md`
- **Key Data**: 0.071ms Redis latency, 100K+ ops/sec baseline
- **Coordination**: IF.search 8-pass mapped to SHARE/HOLD/ESCALATE speech acts

### Agent Architecture

Agent deployment and model selection:
- **Haiku Agents** (40-agent swarms): Parallel task execution, cost-optimized
- **Sonnet Coordinators** (2 coordinators × 20 agents): Task distribution, conflict resolution
- **Opus Agents** (future): Complex reasoning, final synthesis

## Version History

- **v1.0** (2025-11-30): Initial 5-dashboard release
  - Covers S2 swarm metrics from production deployment
  - Supports Grafana 8.0+ and Prometheus 2.0+
  - IF.TTT compliance for audit trails
  - Production-ready thresholds and alert baselines

## Support

For issues or enhancements:

1. Check metrics exporter implementation
2. Verify Prometheus scrape configs
3. Review dashboard variable templates
4. Consult S2 swarm communication paper for metric definitions

---

**Last Updated**: 2025-11-30
**Author**: Agent A31 (Grafana Dashboard Templates for InfraFabric Swarm)
**License**: Apache 2.0
**Citation**: `if://dashboard/grafana/v1.0/2025-11-30`
