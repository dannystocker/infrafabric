# WebRTC Agent Mesh - Monitoring Checklist & Dashboards

**Version:** 1.0
**Last Updated:** November 11, 2025
**Status:** Production Ready

---

## Table of Contents

1. [Quick Reference - Key Metrics](#quick-reference---key-metrics)
2. [Monitoring Setup Checklist](#monitoring-setup-checklist)
3. [Grafana Dashboard Templates](#grafana-dashboard-templates)
4. [Alert Configuration](#alert-configuration)
5. [IF.witness Query Reference](#ifwitness-query-reference)
6. [Troubleshooting Queries](#troubleshooting-queries)

---

## Quick Reference - Key Metrics

### Critical Metrics (RED Method)

| Metric | Threshold | Alert When | Priority |
|--------|-----------|-----------|----------|
| **Connection Success Rate** | >95% | <95% | P1 |
| **Error Rate** | <1% | >1% | P1 |
| **Latency P95** | <150ms (P2P), <500ms (TURN) | Exceeded | P2 |

### Performance Metrics (USE Method)

| Aspect | Metric | Healthy | Alert When |
|--------|--------|---------|-----------|
| **Utilization** | CPU usage | <70% | >80% |
| **Saturation** | Queue depth | <100 msgs | >500 msgs |
| **Errors** | Failed connections | <5% | >5% |

### Operational Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **TURN Fallback Rate** | <20% | >20% | >50% |
| **Message Loss** | <0.1% | >0.5% | >1% |
| **Certificate Days Until Expiry** | >7 | <7 | <1 |
| **SRTP Key Age** | <24h | 23h+ | >24h |

---

## Monitoring Setup Checklist

### Pre-Deployment Monitoring Setup

- [ ] **Prometheus Installed**
  ```bash
  docker run -d \
    --name prometheus \
    -p 9090:9090 \
    -v /etc/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
    prom/prometheus:latest
  ```

- [ ] **Prometheus Scrape Configuration Created**
  - Location: `/etc/prometheus/prometheus.yml`
  - Contains: WebRTC mesh targets, signaling server, IF.witness

- [ ] **Grafana Installed**
  ```bash
  docker run -d \
    --name grafana \
    -p 3000:3000 \
    grafana/grafana:latest
  ```

- [ ] **Grafana Data Source Added**
  - Name: Prometheus
  - URL: `http://prometheus:9090`
  - Type: Prometheus
  - Test connection: ✓ Pass

- [ ] **Grafana Dashboards Imported**
  - [ ] WebRTC Overview Dashboard (main)
  - [ ] Connection Metrics Dashboard
  - [ ] Latency Distribution Dashboard
  - [ ] Security Events Dashboard
  - [ ] Resource Utilization Dashboard

- [ ] **Alert Manager Configured**
  - Email notifications: Configured
  - PagerDuty integration: Configured
  - Slack webhooks: Configured

- [ ] **IF.witness Logging**
  - API endpoint accessible: ✓
  - Authentication key configured: ✓
  - Event ingestion tested: ✓

- [ ] **Log Aggregation (Optional but Recommended)**
  - [ ] ELK Stack (Elasticsearch, Logstash, Kibana) OR
  - [ ] Splunk OR
  - [ ] CloudWatch / DataDog

### Continuous Monitoring Setup

```bash
#!/bin/bash
# setup-monitoring.sh

set -e

echo "Setting up WebRTC Monitoring Stack"

# 1. Create monitoring directory structure
mkdir -p /opt/monitoring/{prometheus,grafana,alertmanager}

# 2. Deploy Prometheus
echo "Deploying Prometheus..."
cat > /opt/monitoring/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    service: 'webrtc-mesh'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - 'webrtc-alerts.yml'

scrape_configs:
  - job_name: 'webrtc-mesh'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 10s

  - job_name: 'signaling-server'
    static_configs:
      - targets: ['localhost:8443']
    scrape_interval: 10s

  - job_name: 'if-witness'
    static_configs:
      - targets: ['witness.infrafabric.local:9090']
    scrape_interval: 30s
EOF

docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /opt/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v /opt/monitoring/prometheus/webrtc-alerts.yml:/etc/prometheus/webrtc-alerts.yml \
  prom/prometheus:v2.35.0

# 3. Deploy Grafana
echo "Deploying Grafana..."
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana:9.0.0

# 4. Add Prometheus data source
sleep 5
curl -X POST http://localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }'

# 5. Import dashboards
echo "Importing Grafana dashboards..."
# (Dashboards defined in next section)

echo "✅ Monitoring setup complete"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3000 (admin:admin)"
```

---

## Grafana Dashboard Templates

### Dashboard 1: WebRTC Overview (Main)

```json
{
  "dashboard": {
    "title": "WebRTC Agent Mesh - Overview",
    "tags": ["webrtc", "production"],
    "panels": [
      {
        "title": "Connection Status",
        "targets": [
          {
            "expr": "webrtc_connections_total{state=\"connected\"}",
            "legendFormat": "Connected"
          },
          {
            "expr": "webrtc_connections_total{state=\"failed\"}",
            "legendFormat": "Failed"
          },
          {
            "expr": "webrtc_connections_total{state=\"pending\"}",
            "legendFormat": "Pending"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Success Rate (5m)",
        "targets": [
          {
            "expr": "rate(webrtc_connections_established[5m]) / rate(webrtc_connections_attempted[5m])",
            "legendFormat": "Success Rate"
          }
        ],
        "type": "gauge",
        "thresholds": "0.95,1"
      },
      {
        "title": "Active Agents",
        "targets": [
          {
            "expr": "count(webrtc_agent_connected)",
            "legendFormat": "Agents"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Messages/sec",
        "targets": [
          {
            "expr": "rate(webrtc_messages_sent_total[1m])",
            "legendFormat": "Sent"
          },
          {
            "expr": "rate(webrtc_messages_received_total[1m])",
            "legendFormat": "Received"
          }
        ],
        "type": "graph"
      },
      {
        "title": "TURN Fallback Rate",
        "targets": [
          {
            "expr": "rate(webrtc_turn_fallback_total[5m]) * 100",
            "legendFormat": "TURN %"
          }
        ],
        "type": "gauge",
        "thresholds": "20,50"
      },
      {
        "title": "Latest Errors",
        "targets": [
          {
            "expr": "topk(5, increase(webrtc_errors_total[5m]))",
            "legendFormat": "{{ error_type }}"
          }
        ],
        "type": "table"
      }
    ]
  }
}
```

### Dashboard 2: Latency Analysis

```json
{
  "dashboard": {
    "title": "WebRTC - Latency & Performance",
    "tags": ["webrtc", "performance"],
    "panels": [
      {
        "title": "RTT Distribution (P2P)",
        "targets": [
          {
            "expr": "histogram_quantile(0.5, rate(webrtc_rtt_milliseconds_bucket{connection_type=\"p2p\"}[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(webrtc_rtt_milliseconds_bucket{connection_type=\"p2p\"}[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(webrtc_rtt_milliseconds_bucket{connection_type=\"p2p\"}[5m]))",
            "legendFormat": "P99"
          }
        ],
        "type": "graph"
      },
      {
        "title": "RTT Distribution (TURN)",
        "targets": [
          {
            "expr": "histogram_quantile(0.5, rate(webrtc_rtt_milliseconds_bucket{connection_type=\"relay\"}[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(webrtc_rtt_milliseconds_bucket{connection_type=\"relay\"}[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(webrtc_rtt_milliseconds_bucket{connection_type=\"relay\"}[5m]))",
            "legendFormat": "P99"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Jitter (Latency Variance)",
        "targets": [
          {
            "expr": "rate(webrtc_jitter_milliseconds[5m])",
            "legendFormat": "Jitter"
          }
        ],
        "type": "graph",
        "alert": {
          "conditions": [
            {"evaluator": {"params": [100]}, "operator": {"type": "gt"}}
          ]
        }
      },
      {
        "title": "Connection Establishment Time (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(webrtc_connection_establishment_seconds_bucket[5m]))",
            "legendFormat": "Establishment Time"
          }
        ],
        "type": "gauge"
      }
    ]
  }
}
```

### Dashboard 3: Security & Encryption

```json
{
  "dashboard": {
    "title": "WebRTC - Security & Encryption",
    "tags": ["webrtc", "security"],
    "panels": [
      {
        "title": "DTLS Validation Status",
        "targets": [
          {
            "expr": "rate(webrtc_dtls_validation_success[5m])",
            "legendFormat": "Successful"
          },
          {
            "expr": "rate(webrtc_dtls_validation_failures[5m])",
            "legendFormat": "Failed"
          }
        ],
        "type": "stat",
        "color": {
          "mode": "thresholds",
          "thresholds": {"steps": [{"value": null, "color": "red"}, {"value": 1, "color": "green"}]}
        }
      },
      {
        "title": "Signature Verification",
        "targets": [
          {
            "expr": "rate(webrtc_signature_verification_success[5m])",
            "legendFormat": "Valid"
          },
          {
            "expr": "rate(webrtc_signature_verification_failures[5m])",
            "legendFormat": "Invalid"
          }
        ],
        "type": "graph"
      },
      {
        "title": "SRTP Key Rotation Events",
        "targets": [
          {
            "expr": "increase(webrtc_srtp_key_rotations_total[1h])",
            "legendFormat": "Rotations/Hour"
          }
        ],
        "type": "stat"
      },
      {
        "title": "Certificate Expiration Status",
        "targets": [
          {
            "expr": "(node_time_seconds - ssl_cert_not_after_seconds) / 86400",
            "legendFormat": "Days Until Expiry"
          }
        ],
        "type": "gauge",
        "thresholds": "7,1"
      },
      {
        "title": "Security Events (24h)",
        "targets": [
          {
            "expr": "topk(10, increase(webrtc_security_events_total[24h]))",
            "legendFormat": "{{ event_type }}"
          }
        ],
        "type": "table"
      }
    ]
  }
}
```

### Dashboard 4: Resource Utilization

```json
{
  "dashboard": {
    "title": "WebRTC - Resource Utilization",
    "tags": ["webrtc", "resources"],
    "panels": [
      {
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "rate(webrtc_cpu_seconds[5m]) * 100",
            "legendFormat": "{{ pod }}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Memory Usage",
        "targets": [
          {
            "expr": "webrtc_memory_bytes / 1024 / 1024 / 1024",
            "legendFormat": "{{ pod }} (GB)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Network I/O (bytes/sec)",
        "targets": [
          {
            "expr": "rate(webrtc_network_bytes_sent[5m])",
            "legendFormat": "Sent"
          },
          {
            "expr": "rate(webrtc_network_bytes_received[5m])",
            "legendFormat": "Received"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Goroutine Count (Node.js processes)",
        "targets": [
          {
            "expr": "process_resident_memory_bytes",
            "legendFormat": "Memory"
          }
        ],
        "type": "graph"
      },
      {
        "title": "File Descriptors Usage",
        "targets": [
          {
            "expr": "process_open_fds / process_max_fds * 100",
            "legendFormat": "Usage %"
          }
        ],
        "type": "gauge"
      }
    ]
  }
}
```

---

## Alert Configuration

### Alert Rules (Prometheus)

```yaml
# /etc/prometheus/webrtc-alerts.yml

groups:
  - name: webrtc_critical
    interval: 1m
    rules:
      # === CONNECTION ALERTS ===
      - alert: WebRTCConnectionFailureRate
        expr: |
          (increase(webrtc_connections_failed_total[5m]) /
           increase(webrtc_connections_attempted_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
          team: webrtc
        annotations:
          summary: "WebRTC connection failure rate exceeds 5%"
          description: "{{ $value | humanizePercentage }} of connection attempts are failing"
          runbook_url: "https://wiki.infrafabric.local/webrtc/incident-connection-failures"

      - alert: WebRTCNoConnectedAgents
        expr: count(webrtc_agent_connected) == 0
        for: 2m
        labels:
          severity: critical
          team: webrtc
        annotations:
          summary: "No agents connected to WebRTC mesh"
          description: "All agents have disconnected"
          impact: "Complete service outage"

      # === LATENCY ALERTS ===
      - alert: WebRTCHighLatencyP2P
        expr: |
          histogram_quantile(0.95, rate(webrtc_rtt_milliseconds_bucket{connection_type="p2p"}[5m])) > 100
        for: 10m
        labels:
          severity: warning
          team: webrtc
        annotations:
          summary: "P2P latency P95 exceeds 100ms"
          description: "Current P95: {{ $value }}ms"
          runbook_url: "https://wiki.infrafabric.local/webrtc/incident-high-latency"

      - alert: WebRTCHighLatencyTURN
        expr: |
          histogram_quantile(0.95, rate(webrtc_rtt_milliseconds_bucket{connection_type="relay"}[5m])) > 500
        for: 10m
        labels:
          severity: warning
          team: webrtc
        annotations:
          summary: "TURN latency P95 exceeds 500ms"
          description: "Current P95: {{ $value }}ms"

      # === PACKET LOSS ALERTS ===
      - alert: WebRTCHighPacketLoss
        expr: |
          (increase(webrtc_packets_lost_total[5m]) /
           increase(webrtc_packets_sent_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
          team: webrtc
        annotations:
          summary: "Packet loss exceeds 5%"
          description: "Loss rate: {{ $value | humanizePercentage }}"
          runbook_url: "https://wiki.infrafabric.local/webrtc/incident-packet-loss"

      # === TURN USAGE ALERTS ===
      - alert: WebRTCHighTURNUsage
        expr: |
          (increase(webrtc_turn_fallback_total[5m]) /
           increase(webrtc_total_connections[5m])) > 0.2
        for: 10m
        labels:
          severity: warning
          team: webrtc
        annotations:
          summary: "TURN fallback usage exceeds 20%"
          description: "{{ $value | humanizePercentage }} of connections using TURN"
          impact: "Higher latency, increased bandwidth costs"

      # === SECURITY ALERTS ===
      - alert: WebRTCDTLSValidationFailure
        expr: increase(webrtc_dtls_validation_failures_total[5m]) > 0
        for: 1m
        labels:
          severity: critical
          team: security
        annotations:
          summary: "DTLS certificate validation failures detected"
          description: "{{ $value }} validation failures in last 5 minutes"
          impact: "Potential security breach"
          runbook_url: "https://wiki.infrafabric.local/webrtc/incident-security"

      - alert: WebRTCSignatureVerificationFailure
        expr: increase(webrtc_signature_verification_failures_total[5m]) > 0
        for: 1m
        labels:
          severity: critical
          team: security
        annotations:
          summary: "Message signature verification failures detected"
          description: "{{ $value }} signature failures in last 5 minutes"
          impact: "Possible message tampering"
          runbook_url: "https://wiki.infrafabric.local/webrtc/incident-security"

      - alert: WebRTCCertificateExpiringSoon
        expr: |
          (ssl_cert_not_after_seconds - time()) / 86400 < 7
        for: 1h
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "TLS certificate expiring within 7 days"
          description: "Days until expiry: {{ $value | humanize }}"
          runbook_url: "https://wiki.infrafabric.local/webrtc/incident-cert-expiry"

      # === RESOURCE ALERTS ===
      - alert: WebRTCHighMemoryUsage
        expr: webrtc_memory_bytes / 1024 / 1024 / 1024 > 0.7
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "WebRTC memory usage exceeds 700MB"
          description: "Current memory: {{ $value | humanize }}GB"
          impact: "Potential OOM crash"

      - alert: WebRTCHighCPUUsage
        expr: rate(webrtc_cpu_seconds[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "WebRTC CPU usage exceeds 80%"
          description: "Current CPU usage: {{ $value | humanizePercentage }}"
          impact: "Performance degradation"

      # === AVAILABILITY ALERTS ===
      - alert: WebRTCSignalingServerDown
        expr: up{job="signaling-server"} == 0
        for: 2m
        labels:
          severity: critical
          team: webrtc
        annotations:
          summary: "Signaling server is down"
          description: "Signaling server at {{ $labels.instance }} is unreachable"
          impact: "New connections cannot be established"
          runbook_url: "https://wiki.infrafabric.local/webrtc/incident-signaling-down"

      - alert: WebRTCPrometheusScrapeFailing
        expr: up{job="webrtc-mesh"} == 0
        for: 5m
        labels:
          severity: warning
          team: infrastructure
        annotations:
          summary: "Cannot scrape metrics from WebRTC mesh"
          description: "Prometheus cannot reach WebRTC metrics endpoint"
          impact: "Loss of observability"

  - name: webrtc_sla
    interval: 5m
    rules:
      - alert: WebRTCSLAViolation
        expr: |
          (count(webrtc_connections_total{state="connected"}) /
           count(webrtc_agent_connected)) < 0.95
        for: 10m
        labels:
          severity: critical
          sla: "99.5%"
        annotations:
          summary: "WebRTC SLA violated - connectivity below 95%"
          description: "Mesh connectivity: {{ $value | humanizePercentage }}"
```

### Alerting Routing (Alert Manager)

```yaml
# /etc/alertmanager/config.yml

global:
  resolve_timeout: 5m

route:
  receiver: default
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

  routes:
    # Critical security alerts
    - match:
        severity: critical
        team: security
      receiver: security-team
      continue: true
      repeat_interval: 5m

    # Critical WebRTC alerts
    - match:
        severity: critical
        team: webrtc
      receiver: webrtc-oncall
      continue: true
      repeat_interval: 5m

    # Warning alerts
    - match:
        severity: warning
      receiver: webrtc-team
      group_wait: 30s

receivers:
  - name: default
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#monitoring'
        title: 'Prometheus Alert'

  - name: webrtc-oncall
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        description: '{{ .CommonAnnotations.summary }}'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#incident-response'
    email_configs:
      - to: 'oncall@infrafabric.local'
        from: 'alertmanager@infrafabric.local'
        smarthost: 'smtp.example.com:587'

  - name: security-team
    email_configs:
      - to: 'security@infrafabric.local'
        from: 'alertmanager@infrafabric.local'
        smarthost: 'smtp.example.com:587'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL_SECURITY}'
        channel: '#security-incidents'
```

---

## IF.witness Query Reference

### Common Queries for Troubleshooting

#### Query 1: Find all connection failures for an agent

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "event": "connection_state_changed",
      "agent_id": "agent-1",
      "metadata.state": "failed"
    },
    "time_range": {"from": "-1h", "to": "now"}
  }' | jq '.results[] | {timestamp, event, metadata}'
```

#### Query 2: Track TURN fallback events

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "event": "turn_fallback_initiated"
    },
    "time_range": {"from": "-24h", "to": "now"}
  }' | jq '.results | group_by(.metadata.peer_id) | map({
    peer: .[0].metadata.peer_id,
    fallback_count: length,
    first_time: .[0].timestamp,
    last_time: .[-1].timestamp
  })'
```

#### Query 3: Find all signature verification failures

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "event": "signature_verification_failed"
    },
    "time_range": {"from": "-1h", "to": "now"}
  }' | jq '.results'
```

#### Query 4: Trace complete connection lifecycle

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "agent_id": "agent-1",
      "peer_id": "agent-2",
      "event": {"regex": "^(webrtc_|connection_|turn_).*"}
    },
    "time_range": {"from": "-1h", "to": "now"},
    "sort": {"timestamp": 1}
  }' | jq '.results[] | {
    timestamp,
    event,
    state: .metadata.state,
    rtt: .metadata.roundTripTime
  }'
```

#### Query 5: SRTP key rotation audit trail

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "event": "srtp_key_rotated"
    },
    "time_range": {"from": "-7d", "to": "now"}
  }' | jq '.results | group_by(.agent_id) | map({
    agent: .[0].agent_id,
    total_rotations: length,
    last_rotation: .[0].timestamp
  })'
```

#### Query 6: Security event summary

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "event": {"regex": ".*validation.*|.*security.*|.*failed.*"}
    },
    "time_range": {"from": "-24h", "to": "now"}
  }' | jq '.results | group_by(.event) | map({
    event: .[0].event,
    count: length,
    latest: .[0].timestamp
  })'
```

#### Query 7: Correlation analysis - latency spikes

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "event": "connection_quality_update",
      "metadata.roundTripTime": {"\$gt": 500}
    },
    "time_range": {"from": "-1h", "to": "now"}
  }' | jq '.results | map({
    timestamp,
    agent: .agent_id,
    peer: .peer_id,
    rtt: .metadata.roundTripTime,
    candidate_type: .metadata.candidateType
  }) | sort_by(.rtt) | reverse | .[0:5]'
```

---

## Troubleshooting Queries

### Issue: High latency - which region is affected?

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -d '{
    "query": {
      "event": "connection_quality_update",
      "metadata.roundTripTime": {"\$gt": 200}
    },
    "time_range": {"from": "-30m", "to": "now"}
  }' | jq '.results | map({
    agent: .agent_id,
    region: .metadata.agent_region,
    rtt: .metadata.roundTripTime
  }) | group_by(.region) | map({
    region: .[0].region,
    high_latency_count: length,
    avg_rtt: (map(.rtt) | add / length)
  })'
```

### Issue: Connection loop - agent keeps reconnecting

```bash
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -d '{
    "query": {
      "agent_id": "agent-name",
      "event": {"regex": "connection_.*|reconnect.*"}
    },
    "time_range": {"from": "-30m", "to": "now"}
  }' | jq '.results | group_by(.peer_id) | map({
    peer: .[0].peer_id,
    state_changes: length,
    events: map(.event) | unique,
    duration_minutes: ((.[0].timestamp | fromdateiso8601) - (.[−1].timestamp | fromdateiso8601)) / 60
  })'
```

### Issue: Message loss spike

```bash
# Check for retransmission or dropped messages
curl -X POST http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -d '{
    "query": {
      "event": {"regex": "ifmessage_(sent|received|failed)"}
    },
    "time_range": {"from": "-30m", "to": "now"}
  }' | jq '
    .results as $events |
    {
      sent: ($events | map(select(.event == "ifmessage_sent")) | length),
      received: ($events | map(select(.event == "ifmessage_received")) | length),
      failed: ($events | map(select(.event == "ifmessage_failed")) | length)
    } |
    {
      sent,
      received,
      failed,
      loss_rate: ((sent - received) / sent * 100)
    }
  '
```

---

## Dashboard Import Instructions

### Step 1: Create Dashboards in Grafana

1. Log into Grafana: `http://grafana.infrafabric.local:3000`
2. Click "+" → "Dashboard"
3. Click "Panel" → "Add Query"
4. Select Prometheus as datasource
5. Add metric queries from dashboard templates above

### Step 2: Set Up Alerts

1. In each panel, click "Alert" tab
2. Configure alert condition
3. Add notification channel (Slack, email, PagerDuty)

### Step 3: Import Pre-Built Dashboards

```bash
#!/bin/bash
# import-dashboards.sh

GRAFANA_URL="http://grafana.infrafabric.local:3000"
GRAFANA_API_KEY="your_api_key"

# Import WebRTC Overview dashboard
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @dashboards/webrtc-overview.json

# Import other dashboards
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -d @dashboards/webrtc-latency.json

curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -d @dashboards/webrtc-security.json

curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -d @dashboards/webrtc-resources.json

echo "✓ Dashboards imported"
```

---

## Monitoring Validation Checklist

After deploying monitoring, verify:

- [ ] Prometheus scraping WebRTC metrics
  ```
  http://prometheus:9090/targets
  ```

- [ ] All dashboards populated with data
  - [ ] WebRTC Overview
  - [ ] Latency Dashboard
  - [ ] Security Dashboard
  - [ ] Resource Dashboard

- [ ] Alerts firing on test conditions
  ```
  # Generate test alert
  curl -X POST http://webrtc.infrafabric.local:8443/test/trigger-alert
  ```

- [ ] IF.witness logging events
  ```
  curl http://witness.infrafabric.local/api/stats | jq '.total_events'
  ```

- [ ] Notification channels working
  - [ ] Slack messages received
  - [ ] Email notifications sent
  - [ ] PagerDuty incidents created

---

**Document Version:** 1.0
**Last Updated:** November 11, 2025
**Next Review:** December 11, 2025

For dashboard updates or metric additions, contact: ops-team@infrafabric.local
