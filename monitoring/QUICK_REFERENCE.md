# InfraFabric Grafana Dashboards - Quick Reference Card

**For**: SRE & DevOps teams
**Generated**: 2025-11-30 (Agent A31)
**Status**: Production Ready

---

## One-Line Summary

5 production-grade Grafana dashboards (Swarm Overview, Redis Performance, ChromaDB Performance, Agent Health, API & UX) with 40+ Prometheus metrics for real-time visibility into swarm health, latency, and coordination.

---

## 30-Second Setup

```bash
# 1. Get Grafana API key (Settings → API Keys → New)
# 2. Run import script
cd /home/setup/infrafabric/monitoring/grafana
./import_dashboards.sh http://grafana:3000 glsa_your_api_key

# 3. Verify dashboards appear at http://grafana:3000/dashboards
# 4. Implement metrics exporter (Python or Go)
# 5. Update Prometheus scrape config (ports 9091, 9092)
```

---

## Dashboard URLs

Once imported, access via:

| Dashboard | URL | Use Case |
|-----------|-----|----------|
| Swarm Overview | `/d/swarm_overview` | Executive view, SLA checks |
| Redis Performance | `/d/redis_performance` | Cache tuning, memory pressure |
| ChromaDB Performance | `/d/chromadb_performance` | Vector search bottlenecks |
| Agent Health | `/d/agent_health` | Agent failures, coordination |
| API & UX | `/d/api_ux` | User experience, endpoint latency |

Full URL: `http://grafana:3000/d/{uid}`

---

## Key Metrics at a Glance

### Swarm Health (Swarm Overview)
- Active agents: 0-100+ (scales with load)
- Request rate: Target <500 req/sec (GREEN), <1000 (YELLOW), >1000 (RED)
- Error rate: Target <5% (GREEN), <10% (YELLOW), >10% (RED)
- P95 latency: Target <100ms (GREEN), <500ms (YELLOW), >500ms (RED)
- Task queue: Monitor for >500 tasks (backlog indicator)
- Speech acts: SHARE > HOLD > ESCALATE (expected ratio)

### Redis Cache (Redis Performance)
- Latency p95: Target <10ms (baseline 0.071ms per S2 paper)
- Hit ratio: Target >80% (GREEN), >60% (YELLOW), <30% (RED)
- Memory: Target <70% (GREEN), <90% (YELLOW), >90% (RED)
- Evictions: Spike = memory pressure, check hit/miss ratio

### Vector DB (ChromaDB Performance)
- Query latency: <100ms (GREEN), <500ms (YELLOW), >500ms (RED)
- Collections: 9,832 docs indexed across 6 collections
- Disk usage: <50% (GREEN), 50-80% (YELLOW), >80% (RED)
- Cache effectiveness: >60% (GREEN), 30-60% (YELLOW), <30% (RED)

### Agents (Agent Health)
- By model: Haiku (40), Sonnet (2), Opus (0 in current deployment)
- Task completion: >95% (GREEN), >90% (YELLOW), <80% (RED)
- Conflicts/min: <5 (GREEN), 5-10 (YELLOW), >10 (RED)
- Delegation success: >95% (GREEN), >90% (YELLOW), <90% (RED)

### User Experience (API & UX)
- TTFT (streaming): <500ms (GREEN), <1s (YELLOW), >1s (RED)
- P95 latency: <200ms (GREEN), <500ms (YELLOW), >500ms (RED)
- Error rate: <1% (GREEN), <5% (YELLOW), >5% (RED)

---

## Alert Thresholds

All dashboards use color coding:

| Color | Meaning | Action |
|-------|---------|--------|
| GREEN | Healthy | Monitored, no action |
| YELLOW | Warning | Trending toward limit, prepare |
| RED | Critical | SLA violation, page on-call |

Common P0 alerts:
- P95 latency > 500ms (may be Redis or ChromaDB)
- Error rate > 10% (check agent health panel)
- Agent failures > 1/min (check logs for timeout/OOM)
- Task queue depth > 500 (agents stuck, check completion rate)
- Cache hit ratio < 30% (memory pressure, eviction spike)

---

## Troubleshooting Checklist

### "No Data" in Panels
- [ ] Metrics exporter running? `curl http://localhost:9091/metrics`
- [ ] Prometheus scraping? Check `/targets` in Prometheus UI
- [ ] Datasource URL correct? Settings → Datasources → Prometheus

### High Latency Alert (P95 > 500ms)
- [ ] Check Swarm Overview task queue depth
- [ ] If high: agents stuck, check Agent Health completion rate
- [ ] Check Redis Performance latency heatmap
- [ ] If p95 > 50ms: Redis bottleneck, check memory/evictions
- [ ] Check ChromaDB Performance query latency
- [ ] If high: semantic search slow, check disk I/O

### Memory Pressure
- [ ] Redis Performance: memory > 90%?
- [ ] Check eviction events (should be 0 at baseline)
- [ ] Hit ratio dropping? = evictions occurring
- [ ] Scale Redis pool or reduce TTL

### Agent Failures
- [ ] Agent Health: restart spike?
- [ ] Check by model (Haiku likely due to load)
- [ ] Check logs: timeout, OOM, network partition?
- [ ] May need more agents or larger resources

### User Complaints (Slow API)
- [ ] API & UX: TTFT high?
- [ ] Check latency by endpoint
- [ ] Check message throughput
- [ ] Check session durations
- [ ] Correlate with Agent Health failures

---

## File Locations

### Grafana Dashboard JSON Files (5 total)
```
/home/setup/infrafabric/monitoring/grafana/dashboards/
  ├── swarm_overview.json           (11 KB - 6 panels)
  ├── redis_performance.json        (13 KB - 7 panels)
  ├── chromadb_performance.json     (13 KB - 7 panels)
  ├── agent_health.json             (13 KB - 8 panels)
  └── api_ux.json                   (14 KB - 6 panels)
```

### Documentation
```
/home/setup/infrafabric/monitoring/
  ├── DEPLOYMENT_SUMMARY.md         (Main docs)
  ├── QUICK_REFERENCE.md            (This file)
  ├── grafana/README.md             (Import & config guide)
  └── prometheus/METRICS_EXPORTER_SPEC.md  (Implementation guide)
```

### Import Tool
```
/home/setup/infrafabric/monitoring/grafana/
  └── import_dashboards.sh          (Automated import script)
```

---

## Grafana Configuration

### Required Datasource
- Name: `Prometheus`
- URL: `http://prometheus:9090`
- Access: `Server`
- Basic Auth: Optional

### Prometheus Scrape Jobs
Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'infrafabric-swarm'
    static_configs:
      - targets: ['localhost:9091']
    scrape_interval: 15s

  - job_name: 'infrafabric-api'
    static_configs:
      - targets: ['localhost:9092']
    scrape_interval: 15s
```

### Dashboard Variables (Auto-populated)
- **Swarm Overview**: `job` (Prometheus scrape job)
- **Redis Performance**: None (global)
- **ChromaDB Performance**: `collection` (vector DB collections)
- **Agent Health**: `agent_model` (haiku, sonnet, opus)
- **API & UX**: `endpoint` (API routes)

All dashboards support time range picker (1h, 6h, 24h, 7d).

---

## Metrics Summary

Total: 40+ individual metrics across 4 namespaces

| Namespace | Count | Coverage |
|-----------|-------|----------|
| `swarm_*` | 12 | Agents, requests, coordination |
| `redis_*` | 7 | Cache operations, latency, evictions |
| `chromadb_*` | 7 | Vector queries, embeddings, disk |
| `http_*` | 6 | API endpoints, latency, errors |

All metrics are defined in: `/home/setup/infrafabric/monitoring/prometheus/METRICS_EXPORTER_SPEC.md`

---

## Sample PromQL Queries

Common queries used in dashboards:

```promql
# Request rate (req/sec)
rate(swarm_requests_total[1m])

# Error rate percentage
100 * (rate(swarm_errors_total[5m]) / rate(swarm_requests_total[5m]))

# P95 latency (ms)
histogram_quantile(0.95, swarm_latency_seconds_bucket) * 1000

# Redis cache hit ratio
rate(redis_hits_total[5m]) / (rate(redis_hits_total[5m]) + rate(redis_misses_total[5m]))

# Task completion rate
100 * (rate(swarm_task_completed_total[5m]) / rate(swarm_task_started_total[5m]))

# Active agents by model
swarm_agents_active{model=~"haiku|sonnet|opus"}
```

---

## Performance Baselines (from S2 Paper)

| Metric | Baseline | Target | P95 | P99 |
|--------|----------|--------|-----|-----|
| Redis latency | 0.071ms | <0.1ms | <10ms | <50ms |
| Swarm latency | ~100ms | - | <500ms | <1s |
| Request rate | 100K+ ops/sec | - | - | - |
| Cache hit ratio | ~80% | - | >60% | >30% |
| Concurrent agents | 40 Haiku + 2 Sonnet | - | - | - |

Source: `/home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md`

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Grafana dashboards | ✓ Complete | 5 dashboards, production-ready JSON |
| Metrics spec | ✓ Complete | 40+ metrics documented |
| Import script | ✓ Complete | Automated with validation |
| Documentation | ✓ Complete | README + METRICS_EXPORTER_SPEC |
| Metrics exporter | ⏳ TODO | Your team implements (Python/Go) |
| Prometheus config | ⏳ TODO | Update with scrape jobs (ports 9091, 9092) |
| Alert rules | ⏳ TODO | Create in Grafana UI or config |

---

## Next Actions

### Immediate (Next hour)
1. [ ] Read this quick reference
2. [ ] Get Grafana API key
3. [ ] Run `import_dashboards.sh`
4. [ ] Verify dashboards appear in Grafana

### Today
1. [ ] Read `/home/setup/infrafabric/monitoring/grafana/README.md` (comprehensive guide)
2. [ ] Read `/home/setup/infrafabric/monitoring/prometheus/METRICS_EXPORTER_SPEC.md` (implementation)
3. [ ] Start metrics exporter implementation (Python or Go)

### This Week
1. [ ] Deploy metrics exporter (9091, 9092)
2. [ ] Update Prometheus scrape config
3. [ ] Verify metrics populate dashboards
4. [ ] Create Grafana alert rules
5. [ ] Test alerts with synthetic metrics

### Long-term
1. [ ] Monitor dashboard performance
2. [ ] Optimize cardinality (prevent Prometheus memory bloat)
3. [ ] Establish runbook for common alerts
4. [ ] Plan v1.1 enhancements (agent-level metrics)

---

## Contact & Support

**Questions about dashboards?** → Read: `/home/setup/infrafabric/monitoring/grafana/README.md`

**Questions about metrics?** → Read: `/home/setup/infrafabric/monitoring/prometheus/METRICS_EXPORTER_SPEC.md`

**Questions about architecture?** → Read: `/home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md`

**Import issues?** → Run: `./import_dashboards.sh` with verbose output

---

## Quick Command Reference

```bash
# Check metrics exporter
curl http://localhost:9091/metrics | head -20

# Test Prometheus
curl 'http://localhost:9090/api/v1/query?query=up'

# View Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets'

# Make script executable
chmod +x /home/setup/infrafabric/monitoring/grafana/import_dashboards.sh

# Run import
./import_dashboards.sh http://grafana:3000 glsa_your_key

# Open Grafana
open http://localhost:3000
```

---

**Version**: 1.0
**Updated**: 2025-11-30
**Author**: Agent A31 (Grafana Dashboard Templates)
**Citation**: `if://dashboard/grafana/quick-ref/v1.0/2025-11-30`
