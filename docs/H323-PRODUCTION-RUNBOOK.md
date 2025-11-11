# H.323 Guardian Council - Production Runbook

**Component**: IF.guard Real-Time Conferencing
**Version**: 1.0
**Last Updated**: 2025-11-11
**Audience**: Operations, SRE, DevOps

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Summary](#architecture-summary)
3. [Deployment Procedures](#deployment-procedures)
4. [Monitoring & Observability](#monitoring--observability)
5. [Incident Response](#incident-response)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Rollback Procedures](#rollback-procedures)
8. [Maintenance Windows](#maintenance-windows)

---

## Overview

This runbook provides operational procedures for the H.323 Guardian Council conferencing system. The system enables secure, traceable real-time communication for InfraFabric's governance body.

### Key Components

- **H.323 Gatekeeper (Primary)**: Admission control (port 1719)
- **H.323 Gatekeeper (Secondary)**: Hot standby (port 1720)
- **MCU**: Multipoint Control Unit for audio/video mixing
- **SIP Gateway**: External expert bridge
- **Health Monitoring**: Prometheus + Grafana
- **IF.witness**: Audit logging

### SLA Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Uptime** | 99.9% | Monthly |
| **Failover Time** | <5 seconds | Per incident |
| **Latency** | <150ms | P95 |
| **Packet Loss** | <1% | Average |
| **Call Success Rate** | >99% | Per admission request |

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│  8-15 Guardian H.323 Terminals                              │
│  (Ed25519 signed admission requests)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ ARQ (Admission Request)
                        ↓
┌─────────────────────────────────────────────────────────────┐
│  H.323 Gatekeeper HA Cluster                                │
│  ┌──────────────┐              ┌──────────────┐             │
│  │  PRIMARY     │◄────────────►│  SECONDARY   │             │
│  │  Port 1719   │  Heartbeat   │  Port 1720   │             │
│  │  (Active)    │  (2 sec)     │  (Standby)   │             │
│  └──────┬───────┘              └──────┬───────┘             │
│         │                              │                     │
│         └──────────┬───────────────────┘                     │
│                    │                                         │
│              Health Monitor                                  │
│         (TCP + process checks)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ ACF/ARJ
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  MCU (Jitsi Videobridge / Kurento)                          │
│  - Audio mixing (centralized)                               │
│  - Video layout (4x4 grid)                                  │
│  - Max 25 guardians                                         │
└─────────────────────────────────────────────────────────────┘
                     │
                     │ Metrics
                     ↓
┌─────────────────────────────────────────────────────────────┐
│  Observability Stack                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Prometheus  │  │   Grafana    │  │  IF.witness  │      │
│  │  (Metrics)   │  │  (Dashboards)│  │  (Audit)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Procedures

### Prerequisites

**System Requirements**:
- Ubuntu 22.04+ or similar Linux distribution
- Python 3.9+
- 4+ CPU cores
- 8+ GB RAM
- 100+ GB disk space
- Network: Static IPs for gatekeeper cluster

**Dependencies**:
```bash
# System packages
sudo apt-get update
sudo apt-get install -y \
    python3.9 python3-pip \
    gstreamer1.0-tools gstreamer1.0-plugins-good \
    prometheus grafana \
    gnugk  # Optional: GNU Gatekeeper

# Python dependencies
pip3 install cryptography pyyaml asyncio
```

### Step 1: Clone Repository

```bash
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric
git checkout claude/h323-guardian-council-011CV2ntGfBNNQYpqiJxaS8B
```

### Step 2: Configure Guardian Registry

```bash
# Generate Ed25519 keypairs for guardians
python3 -c "
from src.communication.h323_gatekeeper import generate_test_keypair
for i in range(8):
    priv, pub = generate_test_keypair()
    print(f'Guardian {i+1} Public Key: {pub}')
"

# Edit registry
nano config/guardian-registry.yaml
# Add guardian public keys generated above
```

### Step 3: Deploy Gatekeeper Cluster

```bash
# Validate deployment
python3 scripts/deploy_gatekeeper_ha.py --validate

# Start primary gatekeeper
python3 src/communication/h323_gatekeeper.py &
GATEKEEPER_PRIMARY_PID=$!
echo $GATEKEEPER_PRIMARY_PID > /var/run/gatekeeper_primary.pid

# Start secondary gatekeeper (port 1720)
python3 src/communication/h323_gatekeeper.py --port 1720 &
GATEKEEPER_SECONDARY_PID=$!
echo $GATEKEEPER_SECONDARY_PID > /var/run/gatekeeper_secondary.pid

# Start HA manager
python3 -c "
import asyncio
from src.communication.h323_gatekeeper_ha import GatekeeperHAManager
ha_manager = GatekeeperHAManager()
asyncio.run(ha_manager.start())
" &
HA_MANAGER_PID=$!
echo $HA_MANAGER_PID > /var/run/ha_manager.pid
```

### Step 4: Deploy MCU

```bash
# Generate MCU config
python3 -c "
from src.communication.h323_mcu_config import MCUConfigManager
from pathlib import Path
mcu = MCUConfigManager(mcu_type='jitsi')
mcu.generate_jitsi_config(Path('config/jitsi-videobridge.json'))
"

# Start Jitsi Videobridge
jvb --config config/jitsi-videobridge.json &
MCU_PID=$!
echo $MCU_PID > /var/run/mcu.pid
```

### Step 5: Configure Monitoring

```bash
# Import Grafana dashboard
curl -X POST http://localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @config/grafana_gatekeeper_ha.json

# Verify Prometheus scraping
curl http://localhost:9090/api/v1/targets | jq .
```

### Step 6: Smoke Test

```bash
# Run production 8-guardian test
python3 tests/test_h323_production_8guardian.py

# Expected output: ✅ PASS - Production Ready
```

---

## Monitoring & Observability

### Prometheus Metrics

**Endpoint**: `http://localhost:9090/metrics`

**Key Metrics**:
- `h323_gatekeeper_up{instance, role}` - Gatekeeper health (1=healthy, 0=down)
- `h323_gatekeeper_active_sessions{instance}` - Active guardian sessions
- `h323_gatekeeper_total_admissions{instance}` - Total admission requests
- `h323_gatekeeper_failover_total` - Failover event count
- `h323_gatekeeper_failover_duration_seconds` - Last failover duration

**Alert Rules** (`/etc/prometheus/rules/h323_alerts.yml`):
```yaml
groups:
  - name: h323_gatekeeper
    rules:
      - alert: GatekeeperDown
        expr: h323_gatekeeper_up == 0
        for: 1m
        annotations:
          summary: "Gatekeeper {{ $labels.instance }} is down"

      - alert: FailoverTooSlow
        expr: h323_gatekeeper_failover_duration_seconds > 5
        annotations:
          summary: "Failover took {{ $value }}s (>5s SLA)"

      - alert: HighCPU
        expr: h323_mcu_cpu_percent > 80
        for: 5m
        annotations:
          summary: "MCU CPU at {{ $value }}%"
```

### Grafana Dashboards

**Dashboard**: `config/grafana_gatekeeper_ha.json`

**Panels**:
1. **Gatekeeper Health** - Real-time up/down status
2. **Active Sessions** - Guardian count over time
3. **Failover Events** - Timeline of failover incidents
4. **Latency P95** - 95th percentile latency

**Access**: `http://localhost:3000/dashboards`

### IF.witness Audit Logs

**Location**: `/home/user/infrafabric/logs/`

**Log Files**:
- `h323_witness/h323_ras_YYYYMMDD.jsonl` - Admission requests (ARQ/ACF/ARJ)
- `gateway/gateway_YYYYMMDD.jsonl` - SIP-H.323 bridge events
- `ha/failover_YYYYMMDD.jsonl` - Failover events

**Query Example**:
```bash
# Count admission requests today
grep '"msg_type": "ARQ"' logs/h323_witness/h323_ras_$(date +%Y%m%d).jsonl | wc -l

# Find admission rejections
grep '"msg_type": "ARJ"' logs/h323_witness/h323_ras_$(date +%Y%m%d).jsonl | jq .
```

---

## Incident Response

### Incident Classification

| Severity | Description | Response Time | Example |
|----------|-------------|---------------|---------|
| **P0 - Critical** | Complete outage | <15 minutes | Both gatekeepers down |
| **P1 - High** | Degraded service | <1 hour | Primary down, secondary active |
| **P2 - Medium** | Minor issues | <4 hours | High latency (>200ms) |
| **P3 - Low** | Non-urgent | <24 hours | Single guardian admission failure |

### P0 - Critical: Both Gatekeepers Down

**Symptoms**:
- `h323_gatekeeper_up` = 0 for both instances
- No guardian admissions succeeding
- Prometheus alert: `GatekeeperDown`

**Response**:
1. **Assess Impact** (1 minute)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_gatekeeper_up
   ```

2. **Check Process Status** (1 minute)
   ```bash
   ps aux | grep -E '(h323_gatekeeper|gnugk)'
   netstat -tulpn | grep -E '(1719|1720)'
   ```

3. **Restart Primary** (2 minutes)
   ```bash
   sudo systemctl restart h323-gatekeeper-primary
   # Or manual: python3 src/communication/h323_gatekeeper.py &
   ```

4. **Verify Recovery** (1 minute)
   ```bash
   python3 tests/test_h323_production_8guardian.py
   ```

5. **Notify Stakeholders** (5 minutes)
   - Slack: #if-guard-ops
   - Email: guardians@infrafabric.org

**Post-Incident**:
- Review IF.witness logs for root cause
- Update runbook if new failure mode discovered

### P1 - High: Primary Gatekeeper Failure

**Symptoms**:
- `h323_gatekeeper_up{role="primary"}` = 0
- Secondary promoted to primary
- Prometheus alert: `FailoverTriggered`

**Response**:
1. **Verify Failover** (1 minute)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_gatekeeper_failover_total
   # Should show recent failover
   ```

2. **Check Failover Duration** (1 minute)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_gatekeeper_failover_duration_seconds
   # Should be <5 seconds
   ```

3. **Diagnose Primary** (5 minutes)
   ```bash
   journalctl -u h323-gatekeeper-primary -n 100 --no-pager
   tail -n 50 logs/h323_witness/h323_ras_$(date +%Y%m%d).jsonl
   ```

4. **Restore Primary** (10 minutes)
   - Fix root cause
   - Restart primary
   - Wait for health checks to confirm healthy
   - HA manager will restore primary/secondary roles

**Success Criteria**:
- ✅ Failover completed <5 seconds
- ✅ Zero call drops during failover
- ✅ Primary restored and healthy

### P2 - Medium: High Latency

**Symptoms**:
- Average latency >150ms
- Guardian complaints about audio delay
- Prometheus alert: `HighLatency`

**Response**:
1. **Measure Latency** (2 minutes)
   ```bash
   python3 tests/load_test_h323_council.py --guardians 8
   # Check avg_latency_ms in output
   ```

2. **Check Network** (5 minutes)
   ```bash
   ping -c 10 <mcu-ip>
   traceroute <mcu-ip>
   ```

3. **Check MCU Load** (2 minutes)
   ```bash
   curl http://localhost:9090/api/v1/query?query=h323_mcu_cpu_percent
   # Should be <80%
   ```

4. **Mitigation**:
   - If MCU overloaded: Reduce guardian count or upgrade hardware
   - If network issue: Work with network team
   - If bandwidth saturation: Reduce video quality (2 Mbps → 1 Mbps)

---

## Troubleshooting Guide

### Common Issues

#### Issue: "Gatekeeper not responding on port 1719"

**Diagnosis**:
```bash
nc -zv localhost 1719
# Connection refused = not running
# Connection succeeded = running
```

**Solution**:
```bash
# Check if process running
ps aux | grep h323_gatekeeper

# If not running, start it
python3 src/communication/h323_gatekeeper.py &

# If port occupied, find and kill process
sudo lsof -i :1719
sudo kill -9 <PID>
```

#### Issue: "Guardian admission rejected (INVALID_SIGNATURE)"

**Diagnosis**:
```bash
# Check IF.witness logs for ARJ events
grep INVALID_SIGNATURE logs/h323_witness/*.jsonl | tail -n 10
```

**Solution**:
- Verify guardian public key in `config/guardian-registry.yaml`
- Ensure guardian terminal using correct private key
- Check Ed25519 signature generation code

#### Issue: "MCU at capacity (25 guardians)"

**Diagnosis**:
```bash
curl http://localhost:9090/api/v1/query?query=h323_mcu_active_participants
```

**Solution**:
- Wait for guardians to leave
- Deploy second MCU (cascading configuration)
- Reject new admissions with `CAPACITY_EXCEEDED`

#### Issue: "Failover taking >5 seconds"

**Diagnosis**:
```bash
grep GATEKEEPER_FAILOVER logs/ha/failover_*.jsonl | jq .failover_duration_sec
```

**Solution**:
- Check health check interval (should be 2 seconds)
- Verify network latency between primary/secondary
- Review failover logic in `h323_gatekeeper_ha.py`

---

## Rollback Procedures

### Scenario: Phase 3 Deployment Fails

**Rollback to Phase 2**:
```bash
# Stop all Phase 3 services
sudo systemctl stop h323-gatekeeper-primary
sudo systemctl stop h323-gatekeeper-secondary
sudo systemctl stop h323-mcu

# Checkout Phase 2 commit
git checkout b5e1f40  # Phase 1+2 commit

# Restart Phase 2 services
python3 src/communication/h323_gatekeeper.py &
python3 src/communication/h323_mcu_config.py &

# Verify
python3 tests/test_h323_admission.py
```

### Scenario: Configuration Error

**Rollback Config**:
```bash
# Restore previous guardian registry
cp config/guardian-registry.yaml.bak config/guardian-registry.yaml

# Restart gatekeeper to reload config
sudo systemctl restart h323-gatekeeper-primary
```

---

## Maintenance Windows

### Planned Maintenance Procedure

**Frequency**: Monthly
**Duration**: 2 hours
**Notification**: 1 week advance

**Steps**:
1. **Notify Guardians** (T-1 week)
   - Email: guardians@infrafabric.org
   - Slack: #if-guard-council
   - Subject: "Maintenance Window: H.323 System Upgrade"

2. **Prepare** (T-1 day)
   - Backup configs: `tar -czf configs_backup.tar.gz config/`
   - Backup logs: `tar -czf logs_backup.tar.gz logs/`
   - Test rollback procedure

3. **Execute Maintenance** (T-0)
   - Switch to secondary gatekeeper
   - Upgrade primary
   - Test primary
   - Switch back to primary
   - Upgrade secondary

4. **Validate** (T+15min)
   - Run production test: `python3 tests/test_h323_production_8guardian.py`
   - Check all metrics
   - Confirm zero issues

5. **Close** (T+2h)
   - Send completion email
   - Update maintenance log

---

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| **On-Call Engineer** | oncall@infrafabric.org | 24/7 |
| **Tech Lead** | danny.stocker@gmail.com | Business hours |
| **Guardian Council** | guardians@infrafabric.org | Business hours |

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-11 | 1.0 | Initial production runbook | InfraFabric S3 |

---

**Document Owner**: InfraFabric Operations Team
**Review Cycle**: Quarterly
**Next Review**: 2026-02-11
