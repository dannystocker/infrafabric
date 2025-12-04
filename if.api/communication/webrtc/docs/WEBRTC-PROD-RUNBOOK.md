# WebRTC Agent Mesh - Production Runbook

**Last Updated:** November 11, 2025
**Runbook Version:** 1.0
**Status:** Production Ready
**Owner:** Infrastructure & Operations Team
**On-Call Contact:** See [Contact Information](#contact-information)

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Procedure](#deployment-procedure)
4. [Monitoring Setup](#monitoring-setup)
5. [Common Issues & Troubleshooting](#common-issues--troubleshooting)
6. [Incident Response Procedures](#incident-response-procedures)
7. [Failover Scenarios](#failover-scenarios)
8. [Rollback Procedures](#rollback-procedures)
9. [Maintenance Operations](#maintenance-operations)
10. [Contact Information](#contact-information)

---

## System Architecture Overview

### Core Components

The WebRTC Agent Mesh is composed of three interconnected systems:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Production Deployment                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Agent 1    │  │   Agent 2    │  │   Agent N    │         │
│  │ (WebRTC)     │  │ (WebRTC)     │  │ (WebRTC)     │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                  │
│                           │ IFMessage + Ed25519 Signatures     │
│                    ┌──────▼───────┐                            │
│                    │  Signaling   │ WebSocket                  │
│                    │  Server      │ (Port 8443)               │
│                    │  (SDP/ICE)   │                            │
│                    └──────┬───────┘                            │
│                           │                                    │
│         ┌─────────────────┼──────────────────┐               │
│         │                 │                  │                │
│    ┌────▼────┐    ┌──────▼────┐    ┌───────▼──┐            │
│    │  STUN   │    │  TURN 1   │    │ TURN 2   │            │
│    │ Server  │    │ Server    │    │ Server   │            │
│    │ (ICE)   │    │ (Fallback)│    │(Fallback)│            │
│    └─────────┘    └───────────┘    └──────────┘            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              IF.witness Event Logger                    │ │
│  │  (Audit Trail: All connections, key rotations, errors) │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Communication Flow

```
1. Agent Registration (Signaling Server)
   Agent → SignalingServer: register message (agent_id)

2. Peer Discovery
   SignalingServer → Other Agents: agent-joined notification

3. Connection Establishment
   Agent1 → SignalingServer: offer (SDP)
   SignalingServer → Agent2: relayed offer
   Agent2 → SignalingServer: answer (SDP)
   SignalingServer → Agent1: relayed answer
   Agent1, Agent2: ICE candidates exchanged (one-by-one)

4. Data Channel Open
   Agent1 ↔ Agent2: RTCDataChannel established (DTLS secured)

5. IFMessage Exchange
   Agent1 → Agent2: IFMessage (Ed25519 signed)
   Agent2 → Agent1: IFMessage response

6. Monitoring
   Agent1 ↔ Agent2: Connection quality stats (every 2 seconds)
   All Events → IF.witness: Audit trail
```

### Key Features

- **Peer-to-Peer Communication:** Direct WebRTC DataChannels between agents
- **Automatic TURN Fallback:** Switches to relay after 5s of no direct connection
- **End-to-End Encryption:** DTLS per RFC 5763, SRTP key rotation every 24h
- **Message Signatures:** Ed25519 cryptographic signatures on all IFMessages
- **Connection Monitoring:** Real-time metrics (latency, packet loss, TURN usage)
- **Security Hardening:** DTLS certificate validation, self-signed cert detection
- **Bandwidth Adaptation:** Automatic quality mode adjustment for constrained networks
- **Complete Audit Trail:** IF.witness logging for all signaling and security events

---

## Pre-Deployment Checklist

### Prerequisites

- [ ] Node.js 18+ installed on all systems
- [ ] `ws` and `@noble/ed25519` npm packages installed
- [ ] TURN server credentials obtained (2+ redundant servers recommended)
- [ ] STUN servers verified (Google public STUN: stun.l.google.com:19302)
- [ ] Firewall rules configured for WebSocket port (default: 8443/TCP)
- [ ] TLS certificates provisioned for signaling server
- [ ] IF.witness logging service accessible and tested
- [ ] Monitoring infrastructure ready (see Monitoring Setup)

### Infrastructure Verification

```bash
# Test STUN server connectivity
node -e "
const dns = require('dns').promises;
dns.resolve4('stun.l.google.com').then(ips => {
  console.log('STUN server IPs:', ips);
}).catch(e => console.error('STUN lookup failed:', e.message));
"

# Test TURN server credentials (if applicable)
# Contact your TURN provider for credential validation

# Verify WebSocket port availability
netstat -tuln | grep 8443 || echo "Port 8443 available"

# Check IF.witness service
curl -s http://witness.infrafabric.local/health || echo "IF.witness service check"
```

### Configuration File Template

Create `config/webrtc-production.env`:

```bash
# Signaling Server
SIGNALING_HOST=0.0.0.0
SIGNALING_PORT=8443
SIGNALING_TLS_CERT=/path/to/cert.pem
SIGNALING_TLS_KEY=/path/to/key.pem

# STUN Servers (primary; fallback to public servers if unavailable)
STUN_SERVERS=stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302

# TURN Servers (critical for production)
# Format: turn:server:port?transport=udp,turn:server:port?transport=tcp
TURN_SERVERS=turn:turn1.example.com:3478?transport=udp,turn:turn2.example.com:3478?transport=udp
TURN_USERNAME=username_here
TURN_PASSWORD=password_here
TURN_FALLBACK_TIMEOUT_MS=5000

# Security Settings
PRODUCTION_MODE=true
ICE_TRANSPORT_POLICY=relay        # "all" for dev, "relay" for high-security
ALLOW_SELF_SIGNED_CERTS=false     # Always false in production
ENABLE_CERT_VALIDATION=true

# SRTP Key Rotation
ENABLE_SRTP_KEY_ROTATION=true
SRTP_KEY_ROTATION_INTERVAL_MS=86400000  # 24 hours

# IF.witness Logging
IF_WITNESS_ENDPOINT=https://witness.infrafabric.local/api/log
IF_WITNESS_API_KEY=your_api_key_here

# Monitoring & Alerting
GRAFANA_DATASOURCE_URL=http://prometheus:9090
ALERT_EMAIL=ops-team@example.com
PAGERDUTY_INTEGRATION_KEY=your_integration_key
```

### Pre-Flight Tests

```bash
#!/bin/bash
# pre-flight-check.sh - Run before every deployment

set -e

echo "=== WebRTC Production Pre-Flight Check ==="

# 1. Dependency check
echo "✓ Checking dependencies..."
npm ls ws @noble/ed25519 > /dev/null || {
  echo "✗ Missing required dependencies"
  exit 1
}

# 2. Configuration check
echo "✓ Verifying configuration..."
test -f config/webrtc-production.env || {
  echo "✗ Configuration file missing"
  exit 1
}
source config/webrtc-production.env

# 3. Port availability
echo "✓ Checking port availability..."
! netstat -tuln 2>/dev/null | grep -q ":$SIGNALING_PORT " || {
  echo "✗ Port $SIGNALING_PORT already in use"
  exit 1
}

# 4. TLS certificates
echo "✓ Verifying TLS certificates..."
test -f "$SIGNALING_TLS_CERT" || {
  echo "✗ TLS certificate not found: $SIGNALING_TLS_CERT"
  exit 1
}
test -f "$SIGNALING_TLS_KEY" || {
  echo "✗ TLS key not found: $SIGNALING_TLS_KEY"
  exit 1
}

# 5. IF.witness connectivity
echo "✓ Testing IF.witness endpoint..."
curl -sf "$IF_WITNESS_ENDPOINT/health" > /dev/null || {
  echo "✗ IF.witness endpoint unreachable: $IF_WITNESS_ENDPOINT"
  exit 1
}

# 6. Build verification
echo "✓ Running build..."
npm run build > /dev/null 2>&1 || {
  echo "✗ Build failed"
  exit 1
}

# 7. Basic sanity test
echo "✓ Running sanity tests..."
npm run test:sanity || {
  echo "✗ Sanity tests failed"
  exit 1
}

echo ""
echo "✅ All pre-flight checks passed!"
```

---

## Deployment Procedure

### Initial Deployment

#### Step 1: Prepare Environment

```bash
# 1. Set environment variables
export NODE_ENV=production
export DEPLOYMENT_ID=$(date +%s)

# 2. Create deployment directory
mkdir -p /opt/infrafabric/webrtc-mesh
cd /opt/infrafabric/webrtc-mesh

# 3. Clone/pull code
git clone --branch production <repo-url> .
git checkout <release-tag>

# 4. Install dependencies
npm ci --production  # Use npm ci instead of npm install

# 5. Run pre-flight checks
bash scripts/pre-flight-check.sh
```

#### Step 2: Deploy Signaling Server

```bash
#!/bin/bash
# deploy-signaling-server.sh

set -e

DEPLOYMENT_ID=$1
INSTANCE_COUNT=${2:-2}  # Deploy 2 instances by default

echo "Deploying WebRTC Signaling Server (Deployment ID: $DEPLOYMENT_ID)"

# Start signaling server instances (behind load balancer)
for i in $(seq 1 $INSTANCE_COUNT); do
  PORT=$((8443 + $i - 1))
  echo "Starting signaling server instance $i on port $PORT..."

  node dist/communication/webrtc-signaling-server.js \
    --host 127.0.0.1 \
    --port $PORT \
    --env production \
    --log-level info \
    > logs/signaling-$i.log 2>&1 &

  PID=$!
  echo $PID > logs/signaling-$i.pid

  # Wait for startup
  sleep 2

  # Verify health
  if ! curl -sf http://127.0.0.1:$PORT/health > /dev/null; then
    echo "✗ Signaling server instance $i failed health check"
    kill $PID || true
    exit 1
  fi

  echo "✓ Instance $i healthy (PID: $PID)"
done

# Configure load balancer
echo "Configuring load balancer..."
# Example: update nginx upstream block
cat > /etc/nginx/conf.d/webrtc-upstream.conf <<EOF
upstream webrtc_signaling {
  least_conn;
  server 127.0.0.1:8443;
  server 127.0.0.1:8444;
}
EOF

nginx -s reload

echo "✓ Signaling server deployment complete"
```

#### Step 3: Deploy Agent Mesh Runtime

```bash
#!/bin/bash
# deploy-agent-mesh.sh

set -e

DEPLOYMENT_ID=$1
AGENT_CONFIG_DIR=${2:-config/agents}

echo "Deploying Agent Mesh Runtime..."

# 1. Validate agent configurations
echo "✓ Validating agent configurations..."
for config_file in $AGENT_CONFIG_DIR/*.json; do
  node -e "require('$config_file')" || {
    echo "✗ Invalid configuration: $config_file"
    exit 1
  }
done

# 2. Initialize IF.witness audit
echo "✓ Initializing audit trail..."
curl -X POST \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"webrtc_deployment_started\",
    \"deployment_id\": \"$DEPLOYMENT_ID\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
  }" \
  "$IF_WITNESS_ENDPOINT/api/events" \
  || echo "⚠ IF.witness logging failed (non-critical)"

# 3. Start monitoring agents
echo "✓ Starting monitoring agents..."
npm run agents:start -- \
  --config-dir "$AGENT_CONFIG_DIR" \
  --deployment-id "$DEPLOYMENT_ID" \
  --log-level info

echo "✓ Agent mesh deployment complete (Deployment ID: $DEPLOYMENT_ID)"
```

#### Step 4: Health Verification

```bash
#!/bin/bash
# verify-deployment.sh

DEPLOYMENT_ID=$1
MAX_RETRIES=30
RETRY_INTERVAL=5

echo "Verifying WebRTC deployment (ID: $DEPLOYMENT_ID)..."

# 1. Check signaling server health
echo "1. Checking signaling server health..."
RETRIES=0
while [ $RETRIES -lt $MAX_RETRIES ]; do
  if curl -sf http://webrtc.infrafabric.local:8443/health | \
     grep -q '"status":"ok"'; then
    echo "   ✓ Signaling server healthy"
    break
  fi
  RETRIES=$((RETRIES + 1))
  sleep $RETRY_INTERVAL
done

if [ $RETRIES -eq $MAX_RETRIES ]; then
  echo "   ✗ Signaling server health check failed"
  exit 1
fi

# 2. Check agent connections
echo "2. Checking agent mesh formation..."
CONNECTED_AGENTS=$(curl -sf http://webrtc.infrafabric.local:8443/agents | \
  jq '.agents | length')
if [ "$CONNECTED_AGENTS" -ge 2 ]; then
  echo "   ✓ Agent mesh formed ($CONNECTED_AGENTS agents)"
else
  echo "   ✗ Insufficient agents connected: $CONNECTED_AGENTS"
  exit 1
fi

# 3. Check connection establishment
echo "3. Verifying peer connections..."
ESTABLISHED_CONNECTIONS=$(curl -sf http://webrtc.infrafabric.local:8443/connections | \
  jq '.connections | map(select(.state=="connected")) | length')
EXPECTED_CONNECTIONS=$(($CONNECTED_AGENTS * ($CONNECTED_AGENTS - 1) / 2))
if [ "$ESTABLISHED_CONNECTIONS" -ge $((EXPECTED_CONNECTIONS / 2)) ]; then
  echo "   ✓ Peer connections established ($ESTABLISHED_CONNECTIONS/$EXPECTED_CONNECTIONS)"
else
  echo "   ⚠ Partial connectivity: $ESTABLISHED_CONNECTIONS/$EXPECTED_CONNECTIONS"
fi

# 4. Test message exchange
echo "4. Testing IFMessage exchange..."
if node scripts/test-message-exchange.js --deployment-id "$DEPLOYMENT_ID"; then
  echo "   ✓ IFMessage exchange working"
else
  echo "   ✗ IFMessage exchange failed"
  exit 1
fi

echo ""
echo "✅ Deployment verification complete (ID: $DEPLOYMENT_ID)"
```

### Canary Deployment Strategy

For high-confidence deployments, use canary deployment:

```bash
#!/bin/bash
# canary-deployment.sh

set -e

STAGE=${1:-staging}
CANARY_AGENTS=${2:-1}  # Start with 1 agent

echo "Starting canary deployment to $STAGE (Agents: $CANARY_AGENTS)..."

# Phase 1: Deploy to canary agents
echo "Phase 1: Deploying to $CANARY_AGENTS canary agent(s)..."
bash scripts/deploy-agent-mesh.sh \
  --deployment-id "canary-$(date +%s)" \
  --agent-count $CANARY_AGENTS \
  --stage $STAGE

sleep 30

# Phase 2: Monitor canary for 5 minutes
echo "Phase 2: Monitoring canary agents (5 minutes)..."
for i in $(seq 1 5); do
  echo "   Monitoring: $(($i * 60))s / 300s"

  # Check for errors in logs
  if grep -q "ERROR\|CRITICAL" logs/agent-canary*.log; then
    echo "   ✗ Errors detected in canary logs"
    bash scripts/rollback.sh canary
    exit 1
  fi

  # Check connection health
  if ! curl -sf http://webrtc-canary:8443/health > /dev/null; then
    echo "   ✗ Canary health check failed"
    bash scripts/rollback.sh canary
    exit 1
  fi

  sleep 60
done

# Phase 3: Expand to 25% of agents
echo "Phase 3: Expanding to 25% of production agents..."
TOTAL_AGENTS=$(curl -sf http://webrtc.infrafabric.local:8443/agents | jq '.agents | length')
EXPAND_COUNT=$((TOTAL_AGENTS / 4))
bash scripts/deploy-agent-mesh.sh \
  --deployment-id "canary-expand-$(date +%s)" \
  --agent-count $EXPAND_COUNT \
  --stage production

sleep 60

# Phase 4: Final expansion
echo "Phase 4: Expanding to 100% of agents..."
bash scripts/deploy-agent-mesh.sh \
  --deployment-id "prod-$(date +%s)" \
  --agent-count $TOTAL_AGENTS \
  --stage production

echo "✅ Canary deployment complete"
```

---

## Monitoring Setup

### Key Metrics to Track

#### Connection Metrics

| Metric | Threshold | Alert When | Check Interval |
|--------|-----------|-----------|----------------|
| **Connection Success Rate** | >95% | <95% | Every 1 min |
| **P2P Connection Rate** | >80% | <80% | Every 1 min |
| **TURN Fallback Rate** | <20% | >20% | Every 5 min |
| **Connection Establishment Time** | <5s (p95) | >5s | Every 5 min |
| **Connection Failures** | <5% | >5% | Every 1 min |

#### Latency Metrics

| Metric | Threshold | Alert When | Check Interval |
|--------|-----------|-----------|----------------|
| **RTT (P2P)** | <50ms (p50) | >100ms | Every 10s |
| **RTT (TURN)** | <200ms (p50) | >300ms | Every 10s |
| **RTT (p95)** | <150ms (p2p), <500ms (TURN) | Exceeded | Every 10s |
| **Jitter** | <50ms | >100ms | Every 30s |

#### Message Metrics

| Metric | Threshold | Alert When | Check Interval |
|--------|-----------|-----------|----------------|
| **Messages/sec** | >1000 | Baseline tracking | Every 1 min |
| **Message Loss Rate** | <0.1% | >0.5% | Every 1 min |
| **Message Signature Verification** | 100% valid | Any invalid | Real-time |
| **Message Delivery Latency** | <100ms (p95) | >200ms | Every 1 min |

#### Security Metrics

| Metric | Threshold | Alert When | Check Interval |
|--------|-----------|-----------|----------------|
| **DTLS Validation Failures** | 0 | Any failure | Real-time |
| **Certificate Expiration** | >7 days | <7 days | Every 6 hours |
| **SRTP Key Rotation Success** | 100% | Any failure | Per rotation (24h) |
| **Unauthorized Connection Attempts** | 0 | Any attempt | Real-time |

#### Resource Metrics

| Metric | Threshold | Alert When | Check Interval |
|--------|-----------|-----------|----------------|
| **CPU Usage** | <70% | >80% | Every 30s |
| **Memory Usage** | <500MB per agent | >700MB | Every 30s |
| **Bandwidth Usage** | Monitor baseline | >2x baseline | Every 1 min |
| **Goroutine Count** | Monitor baseline | >1.5x baseline (Go) | Every 30s |

### Prometheus Scrape Configuration

```yaml
# prometheus/webrtc-scrape-config.yml
scrape_configs:
  - job_name: 'webrtc-mesh'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 15s
    scrape_timeout: 10s
    metrics_path: '/metrics'

  - job_name: 'signaling-server'
    static_configs:
      - targets: ['localhost:8443']
    scrape_interval: 10s
    scrape_timeout: 5s
    metrics_path: '/metrics'

  - job_name: 'if-witness'
    static_configs:
      - targets: ['witness.infrafabric.local:9090']
    scrape_interval: 30s
```

### Grafana Dashboard Configuration

Create dashboard with the following panels:

#### Panel 1: Connection Overview

```json
{
  "title": "WebRTC Connection Status",
  "targets": [
    {
      "expr": "increase(webrtc_connections_established_total[5m])",
      "legendFormat": "Established"
    },
    {
      "expr": "increase(webrtc_connections_failed_total[5m])",
      "legendFormat": "Failed"
    },
    {
      "expr": "increase(webrtc_connections_dropped_total[5m])",
      "legendFormat": "Dropped"
    }
  ],
  "type": "graph"
}
```

#### Panel 2: Latency Distribution

```json
{
  "title": "RTT Distribution (P2P vs TURN)",
  "targets": [
    {
      "expr": "histogram_quantile(0.5, webrtc_rtt_milliseconds{connection_type='p2p'})",
      "legendFormat": "P2P - P50"
    },
    {
      "expr": "histogram_quantile(0.95, webrtc_rtt_milliseconds{connection_type='p2p'})",
      "legendFormat": "P2P - P95"
    },
    {
      "expr": "histogram_quantile(0.5, webrtc_rtt_milliseconds{connection_type='relay'})",
      "legendFormat": "TURN - P50"
    },
    {
      "expr": "histogram_quantile(0.95, webrtc_rtt_milliseconds{connection_type='relay'})",
      "legendFormat": "TURN - P95"
    }
  ],
  "type": "graph"
}
```

#### Panel 3: Message Throughput

```json
{
  "title": "IFMessage Throughput",
  "targets": [
    {
      "expr": "rate(webrtc_messages_sent_total[1m])",
      "legendFormat": "Sent/sec"
    },
    {
      "expr": "rate(webrtc_messages_received_total[1m])",
      "legendFormat": "Received/sec"
    },
    {
      "expr": "rate(webrtc_message_errors_total[1m])",
      "legendFormat": "Errors/sec"
    }
  ],
  "type": "graph"
}
```

#### Panel 4: TURN Fallback Usage

```json
{
  "title": "TURN Fallback Rate",
  "targets": [
    {
      "expr": "rate(webrtc_turn_fallback_attempts_total[5m])",
      "legendFormat": "TURN Fallbacks/sec"
    },
    {
      "expr": "increase(webrtc_turn_fallback_attempts_total[1h])",
      "legendFormat": "Total in Last Hour"
    }
  ],
  "type": "gauge"
}
```

#### Panel 5: Security Events

```json
{
  "title": "Security Events",
  "targets": [
    {
      "expr": "increase(webrtc_dtls_validation_failures_total[5m])",
      "legendFormat": "DTLS Failures"
    },
    {
      "expr": "increase(webrtc_signature_verification_failures_total[5m])",
      "legendFormat": "Signature Failures"
    },
    {
      "expr": "increase(webrtc_srtp_key_rotations_total[1h])",
      "legendFormat": "Key Rotations/Hour"
    }
  ],
  "type": "table"
}
```

### Alert Rules (Prometheus)

```yaml
# prometheus/webrtc-alerts.yml
groups:
  - name: webrtc_alerts
    rules:
      # Connection alerts
      - alert: WebRTCConnectionFailureRate
        expr: |
          (increase(webrtc_connections_failed_total[5m]) /
           increase(webrtc_connections_attempted_total[5m])) > 0.05
        for: 5m
        annotations:
          summary: "WebRTC connection failure rate exceeds 5%"
          runbook_url: "https://wiki.infrafabric.local/webrtc/connection-failures"

      - alert: WebRTCHighTURNUsage
        expr: |
          (increase(webrtc_turn_fallback_total[5m]) /
           increase(webrtc_total_connections[5m])) > 0.2
        for: 5m
        annotations:
          summary: "TURN fallback usage exceeds 20%"
          impact: "Increased latency and bandwidth costs"

      # Latency alerts
      - alert: WebRTCHighLatency
        expr: |
          histogram_quantile(0.95, webrtc_rtt_milliseconds{connection_type='p2p'}) > 100
        for: 10m
        annotations:
          summary: "P2P latency P95 exceeds 100ms"
          runbook_url: "https://wiki.infrafabric.local/webrtc/high-latency"

      # Security alerts
      - alert: WebRTCDTLSValidationFailure
        expr: increase(webrtc_dtls_validation_failures_total[5m]) > 0
        for: 1m
        annotations:
          summary: "DTLS certificate validation failures detected"
          severity: "critical"
          runbook_url: "https://wiki.infrafabric.local/webrtc/security-incident"

      - alert: WebRTCSignatureVerificationFailure
        expr: increase(webrtc_signature_verification_failures_total[5m]) > 0
        for: 1m
        annotations:
          summary: "Message signature verification failures"
          severity: "critical"
          runbook_url: "https://wiki.infrafabric.local/webrtc/security-incident"

      # Resource alerts
      - alert: WebRTCHighMemoryUsage
        expr: webrtc_memory_bytes / 1024 / 1024 / 1024 > 0.7
        for: 5m
        annotations:
          summary: "WebRTC memory usage exceeds 700MB"
          impact: "Potential OOM risk"

      - alert: WebRTCHighCPUUsage
        expr: rate(webrtc_cpu_time_seconds[5m]) > 0.8
        for: 5m
        annotations:
          summary: "WebRTC CPU usage exceeds 80%"
          impact: "Performance degradation"

      # Availability alerts
      - alert: WebRTCSignalingServerDown
        expr: up{job="signaling-server"} == 0
        for: 2m
        annotations:
          summary: "Signaling server is down"
          severity: "critical"
          impact: "New connections cannot be established"
```

### IF.witness Queries for Troubleshooting

```bash
# Query: Find all connection failures for a specific agent
curl -X POST http://witness.infrafabric.local/api/query -d '{
  "query": {
    "event": "connection_state_changed",
    "agent_id": "agent-1",
    "metadata.state": "failed"
  },
  "time_range": {"from": "-1h", "to": "now"}
}'

# Query: Find all TURN fallback events
curl -X POST http://witness.infrafabric.local/api/query -d '{
  "query": {
    "event": "turn_fallback_initiated"
  },
  "time_range": {"from": "-24h", "to": "now"}
}'

# Query: Find all signature verification failures
curl -X POST http://witness.infrafabric.local/api/query -d '{
  "query": {
    "event": "signature_verification_failed"
  },
  "time_range": {"from": "-1h", "to": "now"}
}'

# Query: Find all SRTP key rotations
curl -X POST http://witness.infrafabric.local/api/query -d '{
  "query": {
    "event": "srtp_key_rotated"
  },
  "time_range": {"from": "-7d", "to": "now"}
}'

# Query: Find connection chain for a specific trace
curl -X POST http://witness.infrafabric.local/api/query -d '{
  "query": {
    "trace_id": "abc123def456"
  },
  "time_range": {"from": "-1h", "to": "now"}
}'
```

---

## Common Issues & Troubleshooting

### Issue 1: Connection Establishment Timeout (>5 seconds)

**Symptoms:**
- Agents appear in registry but don't exchange messages
- High TURN fallback rate
- IF.witness shows "turn_fallback_initiated" events

**Root Causes:**
1. Network path blocked (firewall rules)
2. STUN server unreachable
3. ISP blocking peer connections (severe NAT)
4. Inadequate TURN server capacity

**Diagnosis Steps:**

```bash
#!/bin/bash
# troubleshoot-connection-timeout.sh

AGENT_ID=$1
PEER_ID=$2

echo "Troubleshooting connection timeout: $AGENT_ID → $PEER_ID"

# Step 1: Check signaling connectivity
echo "1. Verifying signaling server connectivity..."
if curl -sf http://webrtc.infrafabric.local:8443/agents | \
   jq -e ".agents[] | select(.agent_id==\"$AGENT_ID\")" > /dev/null; then
  echo "   ✓ Agent registered with signaling server"
else
  echo "   ✗ Agent not registered"
  exit 1
fi

# Step 2: Check ICE candidates
echo "2. Examining ICE candidates in IF.witness..."
curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {
    \"event\": \"ice_candidate_sent\",
    \"agent_id\": \"$AGENT_ID\",
    \"peer_id\": \"$PEER_ID\"
  },
  \"time_range\": {\"from\": \"-5m\", \"to\": \"now\"}
}" | jq '.results | length'

# If no ICE candidates, connection timeout expected
if [ $(curl -s -X POST http://witness.infrafabric.local/api/query -d "{...}" | \
       jq '.results | length') -eq 0 ]; then
  echo "   ✗ No ICE candidates exchanged"
  echo "   ACTION: Check if peer connection was created"
fi

# Step 3: Check STUN server accessibility
echo "3. Testing STUN server connectivity..."
for stun_server in stun.l.google.com stun1.l.google.com; do
  if nc -zv -w 2 $stun_server 19302; then
    echo "   ✓ STUN server reachable: $stun_server"
  else
    echo "   ✗ STUN server unreachable: $stun_server"
  fi
done

# Step 4: Check TURN fallback trigger
echo "4. Checking TURN fallback configuration..."
TURN_TIMEOUT=$(curl -s http://webrtc.infrafabric.local:8443/config | \
  jq '.turnFallbackTimeout')
echo "   TURN fallback timeout: ${TURN_TIMEOUT}ms"

# Step 5: Network path analysis
echo "5. Analyzing network path..."
PEER_HOST=$(curl -s http://webrtc.infrafabric.local:8443/peers/$PEER_ID | \
  jq -r '.host')
if ping -c 1 -W 2 $PEER_HOST > /dev/null 2>&1; then
  echo "   ✓ Network path to peer is reachable"
else
  echo "   ✗ Network path to peer blocked"
  echo "   ACTION: Check firewall rules for UDP 5000-65535"
fi

echo ""
echo "Recommendation: Check firewall UDP rules for peer-to-peer communication"
```

**Solution by Root Cause:**

```bash
# If STUN server issue:
# 1. Check firewall rules allow UDP:19302 outbound
sudo ufw allow out 19302/udp

# 2. Add redundant STUN servers to config
STUN_SERVERS="stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302,stun:stun2.l.google.com:19302"

# If TURN server issue:
# 1. Verify TURN credentials
curl -X POST \
  -H "Authorization: Bearer $TURN_API_KEY" \
  https://turn-provider.example.com/api/credentials/validate

# 2. Check TURN server capacity
# Contact TURN provider for current load metrics

# If firewall blocking P2P:
# 1. Ensure UDP port range open (5000-65535)
sudo ufw allow 5000:65535/udp

# 2. Enable TURN relay mode as fallback
ICE_TRANSPORT_POLICY=relay
```

### Issue 2: High Packet Loss (>5%)

**Symptoms:**
- Messages not received
- IF.witness shows high "packetsLost" in stats
- Users report delayed or missing information

**Root Causes:**
1. Congested network path
2. TURN server overloaded
3. Bandwidth exhaustion
4. Codec mismatch

**Diagnosis:**

```bash
#!/bin/bash
# troubleshoot-packet-loss.sh

AGENT_ID=$1

echo "Diagnosing packet loss for $AGENT_ID"

# Get current packet loss rate
LOSS_RATE=$(curl -s http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"connection_quality_update\", \"agent_id\": \"$AGENT_ID\"},
  \"time_range\": {\"from\": \"-5m\", \"to\": \"now\"}
}" | jq '.results[-1].metadata.packetsLost // 0')

echo "Current packet loss: $LOSS_RATE packets"

# Check bandwidth usage
BANDWIDTH_USAGE=$(curl -s http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"bandwidth_update\", \"agent_id\": \"$AGENT_ID\"},
  \"time_range\": {\"from\": \"-1m\", \"to\": \"now\"}
}" | jq '.results | last.metadata.bytesPerSecond // 0')

echo "Bandwidth usage: $BANDWIDTH_USAGE bytes/sec"

# Check if TURN is being used
USING_TURN=$(curl -s http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"turn_connection_detected\", \"agent_id\": \"$AGENT_ID\"},
  \"time_range\": {\"from\": \"-1m\", \"to\": \"now\"}
}" | jq '.results | length')

if [ "$USING_TURN" -gt 0 ]; then
  echo "⚠ Agent is using TURN (relay) - higher packet loss expected"
fi
```

**Solution by Root Cause:**

```bash
# If network congestion:
# 1. Enable bandwidth adaptation
BANDWIDTH_ADAPTATION=true
QUALITY_MODE=automatic

# 2. Reduce message frequency or batch messages
# In application code:
# const adapter = new BandwidthAdapter(agentId);
# await adapter.queueMessage(peerId, message, sendFn);

# If TURN overloaded:
# 1. Add more TURN servers
TURN_SERVERS="turn:turn1.example.com:3478,turn:turn2.example.com:3478,turn:turn3.example.com:3478"

# 2. Balance load across TURN servers
# (Usually handled by round-robin in client SDK)

# If bandwidth exhausted:
# 1. Monitor bandwidth usage
curl http://webrtc.infrafabric.local:8443/metrics | grep webrtc_bandwidth

# 2. Implement rate limiting
# In application code:
// Limit to 1Mbps per peer
const MAX_BITRATE_KBPS = 1000;
const rtcRtpSender = pc.getSenders()[0];
rtcRtpSender.setParameters({
  encodings: [{maxBitrate: MAX_BITRATE_KBPS * 1000}]
});
```

### Issue 3: DTLS Certificate Validation Failures

**Symptoms:**
- IF.witness shows "webrtc_cert_validated: {valid: false}" events
- Connections fail in production mode
- Security logs show DTLS fingerprint mismatches

**Root Causes:**
1. Self-signed certificates in production
2. Certificate expiration
3. Certificate chain validation failure
4. Clock skew between hosts

**Diagnosis:**

```bash
#!/bin/bash
# troubleshoot-dtls-validation.sh

AGENT_ID=$1
PEER_ID=$2

echo "Diagnosing DTLS validation failure: $AGENT_ID → $PEER_ID"

# Get validation failure details from IF.witness
curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {
    \"event\": \"webrtc_cert_validated\",
    \"agent_id\": \"$AGENT_ID\",
    \"peer_id\": \"$PEER_ID\",
    \"metadata.valid\": false
  },
  \"time_range\": {\"from\": \"-1h\", \"to\": \"now\"}
}" | jq '.results | last.metadata'

# Check for self-signed certificate flags
echo "Checking for self-signed certificates..."
curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {
    \"event\": \"webrtc_cert_validated\",
    \"metadata.self_signed\": true
  },
  \"time_range\": {\"from\": \"-1h\", \"to\": \"now\"}
}" | jq '.results | length'

# Check certificate timestamps
echo "Verifying certificate timestamps..."
date -u  # Compare with IF.witness event timestamps
```

**Solution by Root Cause:**

```bash
# If self-signed in production:
# 1. Ensure ALLOW_SELF_SIGNED_CERTS=false in production
ALLOW_SELF_SIGNED_CERTS=false
PRODUCTION_MODE=true

# 2. Provision proper certificates via CA
# Generate CSR
openssl req -new -newkey rsa:2048 -nodes -out server.csr -keyout server.key

# 3. Deploy certificates and restart
cp /path/to/server.crt /etc/webrtc/
systemctl restart webrtc-signaling-server

# If certificate expired:
# 1. Check certificate expiration
openssl x509 -in /etc/webrtc/server.crt -noout -dates

# 2. Renew certificate before expiration
# Use cert renewal automation (Let's Encrypt via certbot)
sudo certbot renew --force-renewal

# 3. Restart signaling server
systemctl restart webrtc-signaling-server

# If clock skew:
# 1. Sync system time on all hosts
sudo ntpdate -s time.nist.gov

# 2. Verify clock synchronization
timedatectl
```

### Issue 4: High Memory Usage (>700MB)

**Symptoms:**
- Memory usage increasing over time
- Potential OOM crashes
- Prometheus metric `webrtc_memory_bytes` > 700MB

**Root Causes:**
1. Connection leak (connections not properly closed)
2. Large message buffering
3. Memory leak in bandwidth adapter
4. Excessive logging

**Diagnosis:**

```bash
#!/bin/bash
# troubleshoot-memory.sh

echo "Analyzing memory usage..."

# Get memory usage trend
curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"memory_usage_update\"},
  \"time_range\": {\"from\": \"-1h\", \"to\": \"now\"}
}" | jq '.results | map(.metadata.memory_bytes / 1024 / 1024) | .[-10:]' \
  | jq 'map(. | "\(. | floor)MB")'

# Check for connection leaks
echo "Checking for unclosed connections..."
OPEN_CONNECTIONS=$(curl -s http://webrtc.infrafabric.local:8443/stats | \
  jq '.connections | map(select(.state=="connected")) | length')
echo "Open connections: $OPEN_CONNECTIONS"

# Compare with expected
EXPECTED=$(curl -s http://webrtc.infrafabric.local:8443/agents | \
  jq '.agents | length * (.agents | length - 1) / 2')
echo "Expected connections: $EXPECTED"

if [ "$OPEN_CONNECTIONS" -gt "$((EXPECTED * 2))" ]; then
  echo "⚠ Possible connection leak detected"
fi
```

**Solution by Root Cause:**

```bash
# If connection leak:
# 1. Ensure all connections are properly closed on disconnect
# In code:
// Verify disconnectPeer method calls pc.close()
await agent.disconnectPeer(peerId);

# 2. Restart service to reclaim memory
systemctl restart webrtc-mesh

# If large message buffering:
# 1. Reduce message queue size
BANDWIDTH_BUFFER_SIZE=1048576  # 1MB instead of default

# 2. Implement message batching
// Batch 10 messages before sending
const BATCH_SIZE = 10;

# If excessive logging:
# 1. Reduce log level in production
LOG_LEVEL=warn  # Instead of debug

# 2. Configure log rotation
cat > /etc/logrotate.d/webrtc <<EOF
/var/log/webrtc/*.log {
  daily
  rotate 7
  compress
  delaycompress
  notifempty
  create 0640 webrtc webrtc
}
EOF
```

---

## Incident Response Procedures

### Incident Classification

| Level | Description | Response Time | Escalation |
|-------|-------------|---|---|
| **P1 - Critical** | Total service down, >1000 agents affected | Immediate (< 5 min) | VP Engineering + On-Call |
| **P2 - High** | Severe degradation, >100 agents affected | 15 minutes | Engineering Lead + On-Call |
| **P3 - Medium** | Partial degradation, <100 agents affected | 1 hour | Team Lead |
| **P4 - Low** | Minor issues, no user impact | 24 hours | Ticket |

### P1 Incident Response

**Incident: Total Service Outage**

```bash
#!/bin/bash
# incident-response-p1-total-outage.sh

set -e

INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"
RESPONSE_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "🚨 P1 INCIDENT: Total Service Outage"
echo "Incident ID: $INCIDENT_ID"
echo "Response Start: $RESPONSE_START"

# Step 1: Acknowledge and declare incident
echo ""
echo "STEP 1: Declare Incident"
echo "- Incident ID: $INCIDENT_ID"
echo "- Severity: P1"
echo "- Action: Immediately page on-call engineer"

# Create incident in your incident management system
curl -X POST https://pagerduty.example.com/api/incidents \
  -H "Authorization: Token token=$PAGERDUTY_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"incidents\": [{
      \"incident_key\": \"$INCIDENT_ID\",
      \"title\": \"WebRTC Agent Mesh - Total Service Outage\",
      \"urgency\": \"high\",
      \"body\": {
        \"type\": \"incident_body\",
        \"description\": \"WebRTC mesh signaling server is completely unavailable\"
      }
    }]
  }"

# Step 2: Halt deployments
echo ""
echo "STEP 2: Halt All Deployments"
echo "- Disable CI/CD pipeline"
echo "- Cancel any in-flight deployments"

# Log to IF.witness
curl -X POST http://witness.infrafabric.local/api/log \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"incident_declared\",
    \"incident_id\": \"$INCIDENT_ID\",
    \"severity\": \"p1\",
    \"timestamp\": \"$RESPONSE_START\",
    \"action\": \"deployments_halted\"
  }"

# Step 3: Assess impact
echo ""
echo "STEP 3: Assess Impact"

CONNECTED_AGENTS=$(curl -sf http://webrtc.infrafabric.local:8443/agents 2>/dev/null | \
  jq '.agents | length' || echo "0")

FAILED_CONNECTIONS=$(curl -sf http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"connection_state_changed\", \"metadata.state\": \"failed\"},
  \"time_range\": {\"from\": \"-5m\", \"to\": \"now\"}
}" | jq '.results | length' || echo "unknown")

echo "- Connected agents: $CONNECTED_AGENTS"
echo "- Failed connections (last 5m): $FAILED_CONNECTIONS"

# Step 4: Initial diagnosis
echo ""
echo "STEP 4: Initial Diagnosis"

if ! curl -sf http://webrtc.infrafabric.local:8443/health > /dev/null 2>&1; then
  echo "✗ Signaling server is DOWN"
  echo "ACTION: Check signaling server logs"
  echo "$ tail -f /var/log/webrtc/signaling-server.log"

  # Check if process is running
  if ! pgrep -f "webrtc-signaling-server" > /dev/null; then
    echo ""
    echo "IMMEDIATE ACTION: Restart signaling server"
    systemctl start webrtc-signaling-server
    sleep 5

    if curl -sf http://webrtc.infrafabric.local:8443/health > /dev/null 2>&1; then
      echo "✓ Signaling server recovered"

      # Log recovery
      curl -X POST http://witness.infrafabric.local/api/log \
        -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
          \"event\": \"incident_auto_recovery\",
          \"incident_id\": \"$INCIDENT_ID\",
          \"action\": \"signaling_server_restarted\",
          \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }"

      exit 0
    fi
  fi
else
  echo "✓ Signaling server is UP"
  echo "⚠ Issue may be network connectivity or load balancer"
fi

# Step 5: Engage team
echo ""
echo "STEP 5: Engage Response Team"
echo "Notify:"
echo "- On-call engineer (via PagerDuty)"
echo "- Engineering team (Slack #incident-response)"
echo "- Product team (status page update)"

curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"🚨 P1 INCIDENT: WebRTC Agent Mesh Total Outage\",
    \"attachments\": [{
      \"color\": \"danger\",
      \"fields\": [
        {\"title\": \"Incident ID\", \"value\": \"$INCIDENT_ID\"},
        {\"title\": \"Start Time\", \"value\": \"$RESPONSE_START\"},
        {\"title\": \"Severity\", \"value\": \"P1\"},
        {\"title\": \"Impact\", \"value\": \"Connected agents: $CONNECTED_AGENTS\"}
      ]
    }]
  }"

# Step 6: Continue investigation
echo ""
echo "STEP 6: Investigation (Continue below)"
```

**Investigation Continuation:**

```bash
#!/bin/bash
# investigate-p1-outage.sh

INCIDENT_ID=$1

echo "Investigating incident: $INCIDENT_ID"

# Check system resources
echo ""
echo "System Resources:"
ps aux | grep -E "webrtc|node" | grep -v grep
free -h
df -h

# Check network connectivity
echo ""
echo "Network Status:"
ss -tulnp | grep -E "8443|3478"  # Check signaling and TURN ports

# Check IF.witness logs
echo ""
echo "Recent Events from IF.witness:"
curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": {\"regex\": \".*error.*\"}},
  \"time_range\": {\"from\": \"-30m\", \"to\": \"now\"}
}" | jq '.results[-10:] | .[] | {timestamp, event, metadata}'

# Check DNS resolution
echo ""
echo "DNS Status:"
nslookup webrtc.infrafabric.local
nslookup turn1.example.com
nslookup witness.infrafabric.local

# Check database/backend connectivity
echo ""
echo "Backend Services:"
curl -sf http://witness.infrafabric.local/health | jq '.'
```

### P2 Incident Response: High Latency

**Incident: RTT >500ms for >30% of connections**

```bash
#!/bin/bash
# incident-response-p2-high-latency.sh

set -e

INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"

echo "⚠️ P2 INCIDENT: High Latency"
echo "Incident ID: $INCIDENT_ID"

# Step 1: Measure impact
echo ""
echo "STEP 1: Quantify Impact"

HIGH_LATENCY_CONNS=$(curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"connection_quality_update\", \"metadata.roundTripTime\": {\"\$gt\": 500}},
  \"time_range\": {\"from\": \"-5m\", \"to\": \"now\"}
}" | jq '.results | length')

TOTAL_CONNS=$(curl -s http://webrtc.infrafabric.local:8443/stats | \
  jq '.connections | length')

PCT=$((HIGH_LATENCY_CONNS * 100 / TOTAL_CONNS))
echo "High latency connections: $HIGH_LATENCY_CONNS / $TOTAL_CONNS ($PCT%)"

# Step 2: Check if TURN-related
echo ""
echo "STEP 2: Check TURN Usage"

TURN_CONNS=$(curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"connection_quality_update\", \"metadata.candidateType\": \"relay\"},
  \"time_range\": {\"from\": \"-5m\", \"to\": \"now\"}
}" | jq '.results | length')

echo "Connections using TURN: $TURN_CONNS"

if [ "$TURN_CONNS" -gt "$((TOTAL_CONNS / 2))" ]; then
  echo "⚠ More than 50% of connections on TURN"
  echo "ACTION: Check TURN server health"

  for turn_server in ${TURN_SERVERS//,/ }; do
    echo "  Testing: $turn_server"
    timeout 2 nc -zv ${turn_server%:*} ${turn_server##*:} || echo "  ✗ Unreachable"
  done
fi

# Step 3: Check network path
echo ""
echo "STEP 3: Network Path Analysis"
# Use MTR or similar to check path latency
# mtr -r -c 10 <peer_host>

# Step 4: Check if geo-distribution issue
echo ""
echo "STEP 4: Geo-Distribution Check"
curl -X POST http://witness.infrafabric.local/api/query -d "{
  \"query\": {\"event\": \"connection_quality_update\"},
  \"time_range\": {\"from\": \"-5m\", \"to\": \"now\"}
}" | jq '.results | group_by(.metadata.agent_location) | map({
  location: .[0].metadata.agent_location,
  avg_rtt: (map(.metadata.roundTripTime) | add / length)
})'

# Step 5: Mitigation
echo ""
echo "STEP 5: Mitigation Options"
echo "1. Enable bandwidth adaptation (reduces payload size)"
echo "2. Add more TURN servers closer to high-latency regions"
echo "3. Check for network congestion on internet"

# Check bandwidth usage
BANDWIDTH_USAGE=$(curl -s http://webrtc.infrafabric.local:8443/metrics | \
  grep webrtc_bandwidth_bytes_per_second | tail -1)
echo "Current bandwidth usage: $BANDWIDTH_USAGE"

# If high, enable bandwidth limiting
echo ""
echo "Enabling bandwidth adaptation..."
curl -X POST http://webrtc.infrafabric.local:8443/config/bandwidth \
  -H "Content-Type: application/json" \
  -d '{
    "enableBandwidthAdaptation": true,
    "maxBitrateMbps": 1
  }'
```

### Incident Runbook Index

| Incident Type | Response Time | Runbook Location |
|---|---|---|
| **Total Service Outage** | < 5 min | `scripts/incident-response-p1-total-outage.sh` |
| **High Latency** | < 15 min | `scripts/incident-response-p2-high-latency.sh` |
| **High Packet Loss** | < 15 min | `scripts/troubleshoot-packet-loss.sh` |
| **Security Breach** | < 5 min | `scripts/incident-response-p1-security.sh` |
| **Certificate Expiration** | < 1 hour | `scripts/incident-response-p3-cert-expiry.sh` |
| **TURN Server Failure** | < 30 min | `scripts/incident-response-p2-turn-failure.sh` |

---

## Failover Scenarios

### Scenario 1: TURN Server Failure

**Trigger:** TURN server becomes unreachable
**Detection:** Automatic (connection stats monitoring)
**Recovery:** Automatic retry with exponential backoff

```typescript
// src/communication/webrtc-agent-mesh.ts - TURN Failover Logic

/**
 * TURN Server Failover Strategy
 *
 * 1. Primary TURN server fails
 * 2. Client automatically retries with secondary TURN
 * 3. If secondary also fails, use tertiary
 * 4. Log all failures to IF.witness
 * 5. Alert operations after 3 consecutive failures
 */

private turnServers: TURNServerConfig[] = [];
private turnFailureCount: Map<string, number> = new Map();
private MAX_TURN_FAILURES = 3;

async attemptTurnFallback(peerId: string): Promise<void> {
  // Existing TURN fallback code
  // Tracks which TURN servers succeeded/failed

  for (const turnServer of this.turnServers) {
    try {
      // Attempt connection with this TURN server
      const success = await this.testTurnServer(turnServer);
      if (success) {
        // Connection successful, reset failure count
        this.turnFailureCount.delete(turnServer.urls);
        return;
      }
    } catch (error) {
      // Track failure
      const failCount = (this.turnFailureCount.get(turnServer.urls) || 0) + 1;
      this.turnFailureCount.set(turnServer.urls, failCount);

      // Alert after 3 failures
      if (failCount >= this.MAX_TURN_FAILURES) {
        await this.logToWitness({
          event: 'turn_server_failure_alert',
          metadata: {
            turn_server: turnServer.urls,
            failure_count: failCount,
            severity: 'warning'
          }
        });
      }

      // Continue to next TURN server
      continue;
    }
  }

  // All TURN servers failed
  throw new Error('All TURN servers unavailable');
}

private async testTurnServer(server: TURNServerConfig): Promise<boolean> {
  // Parse server URL to get host:port
  // Send STUN Binding Request to TURN server
  // Return true if response received within timeout
  return true;  // Simplified
}
```

**Manual Recovery:**

```bash
#!/bin/bash
# recover-turn-server-failure.sh

FAILED_SERVER=$1
REPLACEMENT_SERVER=$2

echo "Recovering from TURN server failure"
echo "Failed: $FAILED_SERVER"
echo "Replacement: $REPLACEMENT_SERVER"

# Step 1: Remove failed server from rotation
TURN_SERVERS="${TURN_SERVERS//$FAILED_SERVER,/}"
TURN_SERVERS="${TURN_SERVERS%,}"

# Step 2: Add replacement server
TURN_SERVERS="${TURN_SERVERS},$REPLACEMENT_SERVER"

# Step 3: Update configuration
cat > config/webrtc-production.env <<EOF
TURN_SERVERS=$TURN_SERVERS
EOF

# Step 4: Restart signaling server to apply changes
systemctl restart webrtc-signaling-server

# Step 5: Verify new server
sleep 5
if curl -sf http://webrtc.infrafabric.local:8443/health > /dev/null; then
  echo "✓ Failover complete, using $REPLACEMENT_SERVER"
else
  echo "✗ Failover failed, manual intervention required"
  exit 1
fi

# Step 6: Log to IF.witness
curl -X POST http://witness.infrafabric.local/api/log \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"turn_server_failover\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"metadata\": {
      \"failed_server\": \"$FAILED_SERVER\",
      \"replacement_server\": \"$REPLACEMENT_SERVER\",
      \"action\": \"automatic\"
    }
  }"
```

### Scenario 2: Signaling Server Failure

**Trigger:** Signaling server (port 8443) unreachable
**Detection:** Agents cannot register or exchange SDP
**Recovery:** Switch to standby instance or restart

```typescript
// Signaling Server Redundancy Configuration

export interface SignalingServerConfig {
  // Primary signaling server
  primaryUrl: string;  // "wss://signaling1.infrafabric.local:8443"

  // Failover servers (in priority order)
  failoverUrls: string[];  // ["wss://signaling2:8443", "wss://signaling3:8443"]

  // Failover timeout
  failoverTimeoutMs: number;  // 5000ms
}

class IFAgentWebRTC {
  private signalingUrls: string[];
  private currentUrlIndex: number = 0;

  async connectToSignaling(): Promise<void> {
    let lastError: Error | undefined;

    for (let i = 0; i < this.signalingUrls.length; i++) {
      try {
        this.currentUrlIndex = i;
        const url = this.signalingUrls[i];

        this.signalingWs = new WebSocket(url);

        // Wait for connection with timeout
        await Promise.race([
          this.waitForConnection(),
          this.timeout(this.failoverTimeoutMs)
        ]);

        // Success - log which server
        await this.logToWitness({
          event: 'signaling_connected',
          metadata: {
            server: url,
            attempt: i + 1
          }
        });

        return;
      } catch (error) {
        lastError = error as Error;

        await this.logToWitness({
          event: 'signaling_connection_failed',
          metadata: {
            server: this.signalingUrls[i],
            attempt: i + 1,
            error: lastError.message
          }
        });

        // Try next server
      }
    }

    throw new Error(
      `All signaling servers failed: ${lastError?.message}`
    );
  }
}
```

**Automatic Recovery with Load Balancer:**

```yaml
# nginx load balancer config for signaling servers
upstream webrtc_signaling {
  least_conn;
  server signaling1.infrafabric.local:8443 weight=10 max_fails=3 fail_timeout=30s;
  server signaling2.infrafabric.local:8443 weight=10 max_fails=3 fail_timeout=30s;
  server signaling3.infrafabric.local:8443 weight=10 backup;
}

server {
  listen 8443 ssl;
  server_name signaling.infrafabric.local;

  ssl_certificate /etc/nginx/certs/signaling.crt;
  ssl_certificate_key /etc/nginx/certs/signaling.key;

  location / {
    proxy_pass wss://webrtc_signaling;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;

    # Health check
    proxy_connect_timeout 5s;
  }
}
```

### Scenario 3: Network Partition (Mesh Healing)

**Trigger:** Agent loses connectivity to mesh
**Detection:** No messages received for >30 seconds
**Recovery:** Automatic reconnection with exponential backoff

```typescript
/**
 * Mesh Healing Strategy
 *
 * When an agent becomes isolated:
 * 1. Detect lack of heartbeat (no data for 30s)
 * 2. Initiate reconnection to all peers
 * 3. Use exponential backoff: 1s, 2s, 4s, 8s...
 * 4. Max attempts: 10 (2^10 = 1024s ≈ 17 minutes)
 * 5. Log all reconnection events to IF.witness
 */

private heartbeatIntervals: Map<string, NodeJS.Timeout> = new Map();
private reconnectionAttempts: Map<string, number> = new Map();
private readonly HEARTBEAT_TIMEOUT = 30000;  // 30 seconds
private readonly MAX_RECONNECT_ATTEMPTS = 10;

startHeartbeat(peerId: string): void {
  // Clear existing heartbeat
  const existing = this.heartbeatIntervals.get(peerId);
  if (existing) clearTimeout(existing);

  // Start heartbeat timeout
  const timeout = setTimeout(() => {
    this.handleHeartbeatTimeout(peerId);
  }, this.HEARTBEAT_TIMEOUT);

  this.heartbeatIntervals.set(peerId, timeout);
}

receiveMessage(peerId: string, message: IFMessage): void {
  // Reset heartbeat on message receipt
  this.startHeartbeat(peerId);
}

private async handleHeartbeatTimeout(peerId: string): Promise<void> {
  await this.logToWitness({
    event: 'mesh_partition_detected',
    peer_id: peerId,
    timestamp: new Date().toISOString()
  });

  // Initiate reconnection
  await this.reconnectWithBackoff(peerId);
}

private async reconnectWithBackoff(peerId: string): Promise<void> {
  const attempts = this.reconnectionAttempts.get(peerId) || 0;

  if (attempts >= this.MAX_RECONNECT_ATTEMPTS) {
    await this.logToWitness({
      event: 'mesh_healing_failed',
      peer_id: peerId,
      timestamp: new Date().toISOString(),
      metadata: {
        attempts,
        severity: 'critical'
      }
    });
    return;
  }

  // Exponential backoff: 2^attempt seconds
  const delayMs = Math.pow(2, attempts) * 1000;

  await this.logToWitness({
    event: 'mesh_reconnection_scheduled',
    peer_id: peerId,
    metadata: {
      attempt: attempts + 1,
      delay_ms: delayMs
    }
  });

  setTimeout(async () => {
    try {
      // Attempt to reconnect
      const oldPc = this.peerConnections.get(peerId);
      if (oldPc) {
        oldPc.close();
      }

      // Create new connection
      const offer = await this.createOffer(peerId);

      // Reset attempt counter on success
      this.reconnectionAttempts.delete(peerId);

      await this.logToWitness({
        event: 'mesh_reconnection_successful',
        peer_id: peerId,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      // Increment attempts and retry
      this.reconnectionAttempts.set(peerId, attempts + 1);
      await this.reconnectWithBackoff(peerId);
    }
  }, delayMs);
}
```

### Scenario 4: Certificate Expiration

**Trigger:** DTLS certificate approaching or past expiration
**Detection:** Daily check at 00:00 UTC
**Recovery:** Automatic rotation if possible, manual renewal

```bash
#!/bin/bash
# certificate-rotation-procedure.sh

set -e

echo "WebRTC Certificate Rotation Procedure"

CERT_PATH="/etc/webrtc/server.crt"
KEY_PATH="/etc/webrtc/server.key"

# Step 1: Check certificate expiration
echo "Checking certificate expiration..."
EXPIRY_DATE=$(openssl x509 -in "$CERT_PATH" -noout -enddate | cut -d= -f2)
EXPIRY_SECONDS=$(date -d "$EXPIRY_DATE" +%s)
NOW_SECONDS=$(date +%s)
DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_SECONDS - $NOW_SECONDS) / 86400 ))

echo "Certificate expires: $EXPIRY_DATE"
echo "Days until expiration: $DAYS_UNTIL_EXPIRY"

# Step 2: Generate new certificate if within 7 days of expiration
if [ "$DAYS_UNTIL_EXPIRY" -lt 7 ]; then
  echo "⚠ Certificate expiration within 7 days, renewing..."

  # Create backup of old certificate
  cp "$CERT_PATH" "$CERT_PATH.backup.$(date +%s)"
  cp "$KEY_PATH" "$KEY_PATH.backup.$(date +%s)"

  # Option 1: Use Let's Encrypt (if applicable)
  if command -v certbot > /dev/null; then
    echo "Renewing with Let's Encrypt..."
    certbot renew --force-renewal

    # Copy new cert to WebRTC directory
    cp /etc/letsencrypt/live/webrtc.infrafabric.local/fullchain.pem "$CERT_PATH"
    cp /etc/letsencrypt/live/webrtc.infrafabric.local/privkey.pem "$KEY_PATH"
  else
    # Option 2: Manual renewal process
    echo "Generate new certificate and key, then run:"
    echo "  cp /path/to/new/cert $CERT_PATH"
    echo "  cp /path/to/new/key $KEY_PATH"
    echo "  systemctl restart webrtc-signaling-server"
  fi

  # Step 3: Restart signaling server with new certificate
  echo "Restarting signaling server..."
  systemctl restart webrtc-signaling-server

  # Step 4: Verify new certificate
  sleep 5
  NEW_EXPIRY=$(openssl x509 -in "$CERT_PATH" -noout -enddate | cut -d= -f2)
  echo "✓ New certificate loaded: expires $NEW_EXPIRY"

  # Step 5: Log to IF.witness
  curl -X POST http://witness.infrafabric.local/api/log \
    -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"event\": \"tls_certificate_rotated\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
      \"metadata\": {
        \"old_expiry\": \"$EXPIRY_DATE\",
        \"new_expiry\": \"$NEW_EXPIRY\",
        \"action\": \"automatic_renewal\"
      }
    }"

  # Step 6: Notify team
  echo "✓ Certificate rotation complete"
else
  echo "✓ Certificate is valid for $DAYS_UNTIL_EXPIRY more days"
fi
```

### Scenario 5: SRTP Key Compromise (Emergency Rotation)

**Trigger:** Security incident, suspected key compromise
**Detection:** Manual alert or security system
**Recovery:** Force immediate key rotation for all peers

```bash
#!/bin/bash
# emergency-srtp-key-rotation.sh

set -e

INCIDENT_ID="SEC-$(date +%Y%m%d-%H%M%S)"
echo "🔐 EMERGENCY SRTP KEY ROTATION"
echo "Incident ID: $INCIDENT_ID"

# Step 1: Notify about incident
echo ""
echo "STEP 1: Declare Security Incident"
curl -X POST http://witness.infrafabric.local/api/log \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"srtp_key_compromise_detected\",
    \"incident_id\": \"$INCIDENT_ID\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"severity\": \"critical\",
    \"action\": \"emergency_key_rotation_initiated\"
  }"

# Step 2: Trigger key rotation for all active peers
echo ""
echo "STEP 2: Rotating SRTP Keys"
curl -X POST http://webrtc.infrafabric.local:8443/admin/rotate-keys \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"rotation_reason\": \"security_incident\",
    \"incident_id\": \"$INCIDENT_ID\",
    \"force_immediate\": true
  }" | jq '.status'

# Step 3: Monitor rotation progress
echo ""
echo "STEP 3: Monitoring Rotation Progress"
for i in {1..30}; do
  COMPLETED=$(curl -s http://webrtc.infrafabric.local:8443/admin/key-rotation-status | \
    jq '.completed')
  TOTAL=$(curl -s http://webrtc.infrafabric.local:8443/admin/key-rotation-status | \
    jq '.total')

  PCT=$(( COMPLETED * 100 / TOTAL ))
  echo "  [$i/30] Progress: $COMPLETED/$TOTAL ($PCT%)"

  if [ "$COMPLETED" -eq "$TOTAL" ]; then
    echo "✓ Key rotation complete"
    break
  fi

  sleep 2
done

# Step 4: Verify all connections stable
echo ""
echo "STEP 4: Verifying Stability"
sleep 10

FAILED_CONNS=$(curl -s http://webrtc.infrafabric.local:8443/stats | \
  jq '.connections | map(select(.state=="failed")) | length')

if [ "$FAILED_CONNS" -eq 0 ]; then
  echo "✓ All connections stable"
else
  echo "⚠ $FAILED_CONNS connections failed after rotation"
  echo "  ACTION: Monitor and investigate reconnections"
fi

# Step 5: Final audit log
echo ""
echo "STEP 5: Audit Trail Complete"
echo "Incident ID: $INCIDENT_ID"
echo "All rotation events logged to IF.witness"
```

---

## Rollback Procedures

### Rollback Trigger Conditions

| Condition | Severity | Action |
|-----------|----------|--------|
| Error rate > 5% | P2 | Automatic rollback |
| Connection success rate < 95% | P1 | Automatic rollback |
| Memory leak detected | P2 | Automatic rollback |
| DTLS/signature validation failures | P1 | Automatic rollback |
| Manual request from on-call | Manual | On-call triggered |

### Automated Rollback

```bash
#!/bin/bash
# automated-rollback-monitor.sh

DEPLOYMENT_ID=$1
MONITORING_DURATION=$((5 * 60))  # 5 minutes
CHECK_INTERVAL=10

START_TIME=$(date +%s)
CURRENT_TIME=$START_TIME

echo "Monitoring deployment for automatic rollback (ID: $DEPLOYMENT_ID)"

while [ $((CURRENT_TIME - START_TIME)) -lt $MONITORING_DURATION ]; do
  CURRENT_TIME=$(date +%s)
  ELAPSED=$(($CURRENT_TIME - $START_TIME))

  echo "[$ELAPSED/$MONITORING_DURATION seconds] Checking health..."

  # Check error rate
  ERROR_RATE=$(curl -s http://witness.infrafabric.local/api/query -d "{
    \"query\": {\"deployment_id\": \"$DEPLOYMENT_ID\", \"event\": {\"regex\": \".*error.*\"}},
    \"time_range\": {\"from\": \"-1m\", \"to\": \"now\"}
  }" | jq '.results | length')

  TOTAL_EVENTS=$(curl -s http://witness.infrafabric.local/api/query -d "{
    \"query\": {\"deployment_id\": \"$DEPLOYMENT_ID\"},
    \"time_range\": {\"from\": \"-1m\", \"to\": \"now\"}
  }" | jq '.results | length')

  if [ $TOTAL_EVENTS -gt 0 ]; then
    ERROR_PCT=$(( ERROR_RATE * 100 / TOTAL_EVENTS ))
  else
    ERROR_PCT=0
  fi

  echo "  Error rate: $ERROR_PCT%"

  # Trigger automatic rollback if error rate > 5%
  if [ "$ERROR_PCT" -gt 5 ]; then
    echo "✗ Error rate exceeds 5%, triggering automatic rollback"
    bash scripts/rollback.sh "$DEPLOYMENT_ID"
    exit 1
  fi

  # Check connection success rate
  SUCCESSFUL=$(curl -s http://witness.infrafabric.local/api/query -d "{
    \"query\": {
      \"event\": \"connection_state_changed\",
      \"metadata.state\": \"connected\",
      \"deployment_id\": \"$DEPLOYMENT_ID\"
    },
    \"time_range\": {\"from\": \"-1m\", \"to\": \"now\"}
  }" | jq '.results | length')

  ATTEMPTED=$(curl -s http://witness.infrafabric.local/api/query -d "{
    \"query\": {
      \"event\": \"connection_state_changed\",
      \"deployment_id\": \"$DEPLOYMENT_ID\"
    },
    \"time_range\": {\"from\": \"-1m\", \"to\": \"now\"}
  }" | jq '.results | length')

  if [ $ATTEMPTED -gt 0 ]; then
    SUCCESS_RATE=$(( SUCCESSFUL * 100 / ATTEMPTED ))
  else
    SUCCESS_RATE=0
  fi

  echo "  Connection success rate: $SUCCESS_RATE%"

  if [ "$SUCCESS_RATE" -lt 95 ]; then
    echo "✗ Connection success rate < 95%, triggering automatic rollback"
    bash scripts/rollback.sh "$DEPLOYMENT_ID"
    exit 1
  fi

  sleep $CHECK_INTERVAL
done

echo "✓ Deployment monitoring complete, no automatic rollback triggered"
```

### Manual Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

set -e

DEPLOYMENT_ID=${1:-latest}
ROLLBACK_REASON=${2:-"Manual rollback request"}

echo "🔄 WebRTC Deployment Rollback"
echo "Deployment ID: $DEPLOYMENT_ID"
echo "Reason: $ROLLBACK_REASON"

# Step 1: Get previous deployment
echo ""
echo "STEP 1: Finding previous deployment..."
PREVIOUS_DEPLOYMENT=$(git log --oneline --grep="deployment" | head -2 | tail -1 | cut -d' ' -f1)
PREVIOUS_VERSION=$(git describe --tags $PREVIOUS_DEPLOYMENT 2>/dev/null || echo "unknown")

echo "Rolling back to: $PREVIOUS_VERSION"

# Step 2: Verify previous version works
echo ""
echo "STEP 2: Verifying previous version..."
git checkout "$PREVIOUS_VERSION" 2>/dev/null || {
  echo "✗ Failed to checkout previous version"
  exit 1
}

# Step 3: Stop current deployment
echo ""
echo "STEP 3: Stopping current deployment..."
systemctl stop webrtc-signaling-server
systemctl stop webrtc-mesh || true

# Step 4: Reinstall and rebuild
echo ""
echo "STEP 4: Reinstalling packages..."
npm ci --production

npm run build

# Step 5: Start previous version
echo ""
echo "STEP 5: Starting previous version..."
systemctl start webrtc-signaling-server
systemctl start webrtc-mesh

# Step 6: Health check
echo ""
echo "STEP 6: Health verification..."
sleep 5

if curl -sf http://webrtc.infrafabric.local:8443/health > /dev/null; then
  echo "✓ Health check passed"
else
  echo "✗ Health check failed"
  exit 1
fi

# Step 7: Log rollback
echo ""
echo "STEP 7: Logging rollback event..."
curl -X POST http://witness.infrafabric.local/api/log \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"deployment_rollback\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"metadata\": {
      \"deployment_id\": \"$DEPLOYMENT_ID\",
      \"rollback_version\": \"$PREVIOUS_VERSION\",
      \"reason\": \"$ROLLBACK_REASON\",
      \"operator\": \"$(whoami)\"
    }
  }"

echo ""
echo "✅ Rollback complete"
echo "Previous version: $PREVIOUS_VERSION"
```

---

## Maintenance Operations

### Daily Maintenance (00:00 UTC)

```bash
#!/bin/bash
# daily-maintenance.sh

set -e

MAINTENANCE_ID="MAINT-$(date +%Y%m%d)"
echo "🔧 Daily WebRTC Maintenance (ID: $MAINTENANCE_ID)"

# 1. Certificate expiration check
echo "1. Checking certificate expiration..."
DAYS_LEFT=$(openssl x509 -in /etc/webrtc/server.crt -noout -enddate | \
  xargs -I {} date -d {} +%s | \
  xargs -I {} echo $(( ($@ - $(date +%s)) / 86400 )) )
echo "   Days until expiration: $DAYS_LEFT"

if [ "$DAYS_LEFT" -lt 7 ]; then
  echo "   ⚠ Certificate renewal required (see certificate-rotation-procedure.sh)"
fi

# 2. Check log file sizes
echo "2. Checking log file sizes..."
du -sh logs/*

# 3. Rotate old logs
echo "3. Rotating logs..."
logrotate -f /etc/logrotate.d/webrtc || echo "   (no action needed)"

# 4. Database maintenance
echo "4. Running database cleanup..."
# Example: clean up old IF.witness events
curl -X POST http://witness.infrafabric.local/api/admin/cleanup \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"retain_days": 30}'

# 5. Generate health report
echo "5. Generating health report..."
cat > reports/daily-health-$(date +%Y%m%d).json <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "certificate_days_left": $DAYS_LEFT,
  "total_agents": $(curl -s http://webrtc.infrafabric.local:8443/agents | jq '.agents | length'),
  "active_connections": $(curl -s http://webrtc.infrafabric.local:8443/stats | jq '.connections | length'),
  "error_count_24h": $(curl -s http://witness.infrafabric.local/api/query -d '{...}' | jq '.results | length')
}
EOF

echo "✅ Daily maintenance complete (ID: $MAINTENANCE_ID)"
```

### Weekly Maintenance (Sunday 00:00 UTC)

```bash
#!/bin/bash
# weekly-maintenance.sh

echo "🔧 Weekly WebRTC Maintenance"

# 1. Full system test
echo "1. Running full system test..."
npm run test:integration

# 2. Performance baseline check
echo "2. Checking performance metrics..."
curl -s http://prometheus:9090/api/v1/query?query=webrtc_rtt_milliseconds | \
  jq '.data.result | map(.value[1] | tonumber) | {min, max, avg: (add/length)}'

# 3. Security audit
echo "3. Checking for security events..."
curl -X POST http://witness.infrafabric.local/api/query -d '{
  "query": {"event": {"regex": "security|failure|error"}},
  "time_range": {"from": "-7d", "to": "now"}
}' | jq '.results | length'

# 4. Capacity planning
echo "4. Capacity analysis..."
# Check if approaching limits and plan scaling

echo "✅ Weekly maintenance complete"
```

---

## Contact Information

### On-Call Escalation

**Level 1 (First Response): On-Call Engineer**
- Page via PagerDuty
- Response time: < 15 minutes
- Contact: `pagerduty.infrafabric.local`

**Level 2 (Engineering Lead)**
- Page if Level 1 unavailable
- Response time: < 30 minutes
- Slack: `@webrtc-oncall`

**Level 3 (VP Engineering)**
- Page for P1 incidents lasting > 1 hour
- Response time: < 1 hour
- Email: `engineering-vp@infrafabric.local`

### Support Channels

| Channel | Purpose | Response Time |
|---------|---------|---|
| **PagerDuty** | P1/P2 Incidents | < 5 min |
| **Slack #incident-response** | Real-time coordination | < 5 min |
| **Email ops@infrafabric.local** | Documentation, non-urgent | < 4 hours |
| **IF.witness** | Audit trail access | Immediate (self-service) |

### External Support

| Service | Contact | Escalation |
|---------|---------|---|
| **STUN Server** | Google | N/A (public service) |
| **TURN Provider** | `support@turn-provider.example.com` | Account manager |
| **Certificate Authority** | Let's Encrypt automation | N/A (automatic renewal) |
| **ISP (network issues)** | `noc@isp.example.com` | Technical support |

### Additional Resources

- **Runbook Repository:** https://github.com/infrafabric/runbooks
- **Monitoring Dashboard:** https://grafana.infrafabric.local/d/webrtc-overview
- **IF.witness Query Tool:** https://witness.infrafabric.local/query
- **Architecture Documentation:** `/docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md`
- **API Documentation:** `https://api-docs.infrafabric.local/webrtc`

---

**Runbook Effective Date:** November 11, 2025
**Last Reviewed:** November 11, 2025
**Next Review:** November 25, 2025

For updates or questions, please contact: ops-team@infrafabric.local
