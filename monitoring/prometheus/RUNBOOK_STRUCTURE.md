# InfraFabric Alert Runbooks - Structure & Guide

## Overview

Each alert in the InfraFabric monitoring system links to a runbook that provides step-by-step remediation procedures. This document outlines the standard runbook structure and locations.

## Runbook Directory Structure

```
/docs/runbooks/
├── RUNBOOK_INDEX.md              # Master index of all runbooks
├── TEMPLATE.md                   # Runbook template
├── agent_restart.md              # [P0] Agent death recovery
├── redis_recovery.md             # [P0] Redis down recovery
├── chromadb_recovery.md          # [P0] ChromaDB down recovery
├── api_recovery.md               # [P0] API unavailable recovery
├── consensus_recovery.md         # [P0] Consensus failure recovery
├── memory_recovery.md            # [P0] Memory exhaustion recovery
├── latency_investigation.md      # [P1] Latency spike investigation
├── error_rate_investigation.md   # [P1] Error rate investigation
├── queue_management.md           # [P1] Task queue backlog management
├── conflict_resolution.md        # [P1] State conflict resolution
├── cache_optimization.md         # [P1] Cache hit ratio improvement
├── disk_expansion.md             # [P1] Disk usage management
├── load_balancing.md             # [P2] High load handling
├── query_optimization.md         # [P2] Query performance optimization
├── agent_diagnostics.md          # [P2] Agent churn investigation
├── consensus_tuning.md           # [P2] Consensus tuning
└── redis_tuning.md               # [P2] Redis optimization
```

## Runbook Template

Each runbook MUST follow this structure:

```markdown
# [ALERT_NAME] - Runbook

**Severity:** [P0/P1/P2]
**Component:** [Component Name]
**Impact:** [Brief impact statement]
**SLO:** [Response time target]

## Quick Diagnosis

[2-3 quick commands to assess the issue]

## Step-by-Step Resolution

### Step 1: [Action]
[Details and commands]

### Step 2: [Action]
[Details and commands]

### Step 3: [Action]
[Details and commands]

## Verification

[How to verify the fix worked]

## Escalation

[When/how to escalate to other teams]

## Prevention

[How to prevent this issue in the future]

## Related Alerts

- [Link to related alert]
- [Link to related alert]

## References

- [Citation to relevant docs/code]
- [Link to monitoring dashboard]
```

## Alert-to-Runbook Mapping

### P0 Critical Alerts (6 total)

| Alert Name | Runbook | Response Time | Team |
|---|---|---|---|
| AgentDeathDetected | `/docs/runbooks/agent_restart.md` | <1 min | DevOps, SRE |
| RedisDown | `/docs/runbooks/redis_recovery.md` | <30s | DevOps, Database |
| ChromaDBDown | `/docs/runbooks/chromadb_recovery.md` | <30s | DevOps, ML Ops |
| APIUnavailable | `/docs/runbooks/api_recovery.md` | <2 min | DevOps, Platform |
| ConsensusFailure | `/docs/runbooks/consensus_recovery.md` | <5 min | DevOps, SRE |
| MemoryExhaustion | `/docs/runbooks/memory_recovery.md` | <2 min | DevOps, SRE |

### P1 High Alerts (6 total)

| Alert Name | Runbook | Response Time | Team |
|---|---|---|---|
| LatencySpike | `/docs/runbooks/latency_investigation.md` | <5 min | Platform, SRE |
| HighErrorRate | `/docs/runbooks/error_rate_investigation.md` | <3 min | Platform, DevOps |
| TaskQueueBacklog | `/docs/runbooks/queue_management.md` | <10 min | Platform, SRE |
| HighConflictRate | `/docs/runbooks/conflict_resolution.md` | <10 min | Platform, Arch |
| CacheDegradation | `/docs/runbooks/cache_optimization.md` | <15 min | Platform, DB |
| DiskUsageCritical | `/docs/runbooks/disk_expansion.md` | <30 min | DevOps, Storage |

### P2 Medium Alerts (5 total)

| Alert Name | Runbook | Response Time | Team |
|---|---|---|---|
| HighLoadCondition | `/docs/runbooks/load_balancing.md` | <30 min | Platform, SRE |
| SlowQueryDetected | `/docs/runbooks/query_optimization.md` | <10 min | Platform, ML Ops |
| AgentChurnHigh | `/docs/runbooks/agent_diagnostics.md` | <10 min | DevOps, Platform |
| EscalateSpikeSpeechAct | `/docs/runbooks/consensus_tuning.md` | <15 min | Platform, Arch |
| RedisKeyExpirationRate | `/docs/runbooks/redis_tuning.md` | <20 min | Platform, DB |

## Runbook Creation Checklist

When creating a new runbook:

- [ ] Copy TEMPLATE.md as base
- [ ] Add alert name and severity
- [ ] Include quick diagnosis commands
- [ ] Write 3-5 clear remediation steps
- [ ] Add verification procedures
- [ ] Define escalation criteria
- [ ] Include prevention recommendations
- [ ] Add links to related dashboards
- [ ] Include citations to code/docs
- [ ] Test all commands in staging
- [ ] Get peer review from team leads
- [ ] Update RUNBOOK_INDEX.md with new entry

## Quick Command Reference

### Redis Commands
```bash
# Check Redis health
redis-cli PING

# Monitor real-time activity
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory

# Get all keys matching pattern
redis-cli KEYS 'pattern*'

# Check eviction policy
redis-cli CONFIG GET maxmemory-policy
```

### ChromaDB Commands
```bash
# Check ChromaDB status
curl http://localhost:8000/api/v1/heartbeat

# List collections
python3 -c "import chromadb; c=chromadb.PersistentClient(); print([col.name for col in c.list_collections()])"

# Check disk usage
du -sh /path/to/chromadb

# Monitor logs
tail -f /var/log/chromadb/chroma.log
```

### Agent Commands
```bash
# Check running agents
ps aux | grep agent

# Check agent logs
tail -f /var/log/infrafabric/agents.log

# Get agent status
curl http://localhost:8001/api/agents/status

# Restart agent supervisor
systemctl restart infrafabric-agents
```

### Prometheus Commands
```bash
# Query metric
curl 'http://localhost:9090/api/v1/query?query=metric_name'

# Check alerts
curl 'http://localhost:9090/api/v1/alerts'

# Reload config
curl -X POST http://localhost:9090/-/reload
```

## Notification Channels

### P0 Critical
- **PagerDuty:** Immediate page to on-call engineer
- **Slack:** #incidents channel with @here mention
- **Email:** Critical alerts distribution list
- **Escalation:** Automatic page after 5 min if not acknowledged

### P1 High
- **Slack:** #alerts channel
- **Email:** Alerts distribution list (within 5 min)
- **Manual Escalation:** Team lead decides if page needed

### P2 Medium
- **Slack:** #monitoring channel (batched every 30 min)
- **Email:** Daily digest of medium alerts
- **Manual Escalation:** If multiple related P2s fire

## On-Call Responsibilities

### During P0 Alert
1. Acknowledge page within 1 minute
2. Pull up relevant runbook
3. Execute diagnostic steps
4. Document actions taken in #incidents channel
5. Keep SRE lead updated every 5 minutes
6. Continue until service restored

### During P1 Alert
1. Check #alerts channel within 5 minutes
2. Review runbook
3. Begin investigation
4. Document findings
5. Escalate to platform team if needed

### During P2 Alert
1. Review #monitoring channel
2. Assess priority vs. other work
3. Schedule investigation
4. Document findings for improvement

## Metrics Used in Alerts

The following metrics are expected to be exported by the InfraFabric swarm:

### Agent Metrics
- `agent_active_count` - Number of currently active agents
- `agent_restart_total` - Cumulative agent restart count

### API Metrics
- `http_requests_total` - Total HTTP requests (labeled by status)
- `http_request_duration_seconds_bucket` - Request latency histogram

### Consensus Metrics
- `consensus_vote_total` - Total votes cast
- `consensus_vote_failure_total` - Failed votes
- `state_conflict_total` - State conflicts detected
- `speech_act_escalate_total` - ESCALATE speech acts

### Redis Metrics
- `redis_up` - Redis server health (1=up, 0=down)
- `redis_cache_hits_total` - Cache hit count
- `redis_cache_misses_total` - Cache miss count
- `redis_expired_keys_total` - Keys expired by TTL
- `redis_set_total` - Total SET operations

### ChromaDB Metrics
- `chromadb_up` - ChromaDB server health
- `chromadb_query_duration_seconds_bucket` - Query latency histogram
- `chromadb_disk_usage_bytes` - Current disk usage
- `chromadb_disk_total_bytes` - Total disk available

### System Metrics
- `node_memory_MemAvailable_bytes` - Available memory
- `node_memory_MemTotal_bytes` - Total memory

## Configuration

### Prometheus Configuration

Add to `/etc/prometheus/prometheus.yml`:

```yaml
rule_files:
  - '/etc/prometheus/rules/p0_critical.yml'
  - '/etc/prometheus/rules/p1_high.yml'
  - '/etc/prometheus/rules/p2_medium.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - 'localhost:9093'
```

### AlertManager Configuration

Update `/etc/alertmanager/alertmanager.yml` with Slack webhooks and PagerDuty integration keys.

### Environment Variables Required

```bash
export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'
export PAGERDUTY_SERVICE_KEY='...'
export ALERTS_EMAIL='alerts@infrafabric.local'
export ALERTMANAGER_FROM_EMAIL='prometheus@infrafabric.local'
export SMTP_HOST='mail.infrafabric.local'
export SMTP_PORT='587'
export SMTP_USER='alertmanager'
export SMTP_PASSWORD='...'
```

## Testing Alerts

### Test PagerDuty Integration
```bash
amtool alert add TestAlert severity=critical
```

### Test Slack Integration
```bash
# Send test message to #incidents
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test alert from Prometheus"}'
```

### Generate Synthetic Metrics
```bash
# In test environment, generate metrics
prometheus-sd-discovery simulate --config prometheus.yml
```

## Support & Escalation

- **Prometheus Issues:** #ops-monitoring (Slack)
- **AlertManager Issues:** #ops-alerting (Slack)
- **Runbook Questions:** #ops-runbooks (Slack)
- **On-Call Escalation:** Page on-call SRE lead

## Last Updated

- **Date:** 2025-11-30
- **Author:** Agent A32
- **Status:** Active
- **Review Schedule:** Quarterly (January, April, July, October)
