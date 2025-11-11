# WebRTC Agent Mesh - Operations Documentation Index

**Status:** Production Ready
**Last Updated:** November 11, 2025
**Target Audience:** On-call engineers, SRE team, incident responders

---

## Documentation Overview

This directory contains comprehensive operations documentation for the WebRTC Agent Mesh system deployed in InfraFabric Session 2.

### Core Documents

1. **[WEBRTC-PROD-RUNBOOK.md](./WEBRTC-PROD-RUNBOOK.md)** ⭐ START HERE
   - **Length:** ~2,500 lines
   - **Purpose:** Complete operational guide for production deployment and management
   - **Key Sections:**
     - System architecture overview
     - Pre-deployment checklist and verification
     - Step-by-step deployment procedures
     - Monitoring setup with Prometheus/Grafana
     - Common issues & troubleshooting guide
     - Incident response procedures
     - Failover procedures
     - Rollback strategies
     - Maintenance operations
   - **Target Users:** Deployment engineers, on-call responders
   - **When to Use:** Daily operations, deployment planning, incident response

2. **[WEBRTC-FAILOVER-SCENARIOS.md](./WEBRTC-FAILOVER-SCENARIOS.md)** ⭐ FOR INCIDENT RESPONSE
   - **Length:** ~1,200 lines
   - **Purpose:** Decision trees and procedures for 5 critical failover scenarios
   - **Failover Scenarios Covered:**
     - **Scenario A:** TURN server failure → automatic retry logic
     - **Scenario B:** Signaling server failure → reconnection strategy
     - **Scenario C:** Network partition → mesh healing
     - **Scenario D:** Certificate expiration → rotation procedure
     - **Scenario E:** SRTP key compromise → emergency rotation
   - **Special Features:**
     - ASCII decision trees for quick diagnosis
     - TypeScript code examples for implementation
     - Bash scripts for manual recovery
     - Post-recovery validation procedures
   - **Target Users:** On-call engineers, incident commanders
   - **When to Use:** Incident response, failover testing

3. **[WEBRTC-MONITORING-CHECKLIST.md](./WEBRTC-MONITORING-CHECKLIST.md)** ⭐ FOR SETUP & VALIDATION
   - **Length:** ~1,000 lines
   - **Purpose:** Complete monitoring setup and dashboard configuration
   - **Key Sections:**
     - Pre-deployment monitoring checklist (10 items)
     - Metric definitions and thresholds
     - 4 Grafana dashboard templates (JSON-ready)
     - Prometheus alert rules (production-tested)
     - AlertManager routing configuration
     - IF.witness query reference (7 common queries)
     - Troubleshooting query examples
   - **Monitoring Metrics (25+):**
     - Connection success rate, P2P usage, TURN fallback rate
     - Latency distribution (P50/P95/P99)
     - Packet loss, jitter, message throughput
     - DTLS validation, signature verification
     - SRTP key rotation events
     - CPU, memory, file descriptors
     - Certificate expiration countdown
   - **Target Users:** SRE team, monitoring engineers
   - **When to Use:** Initial setup, dashboard creation, alert configuration

---

## Quick Start Guide

### For New Operations Engineers

```bash
# Day 1: Read the runbook (2-3 hours)
1. Read: WEBRTC-PROD-RUNBOOK.md → "System Architecture Overview"
2. Review: Pre-deployment checklist
3. Understand: Communication flow diagrams

# Day 2-3: Set up monitoring (4-6 hours)
1. Follow: WEBRTC-MONITORING-CHECKLIST.md → "Monitoring Setup Checklist"
2. Create: Prometheus scrape configuration
3. Deploy: Grafana dashboards
4. Configure: Alert rules and notifications

# Day 4-5: Deployment practice (4-6 hours)
1. Read: WEBRTC-PROD-RUNBOOK.md → "Deployment Procedure"
2. Review: Pre-flight checks
3. Stage: Test deployment in non-prod
4. Execute: Canary deployment strategy

# Day 6-7: Incident readiness (6-8 hours)
1. Study: WEBRTC-FAILOVER-SCENARIOS.md → All 5 scenarios
2. Understand: Decision trees
3. Practice: Failover simulations
4. Review: IF.witness queries for troubleshooting
```

### For On-Call Responders

```bash
# Incident declared → 5 minutes
1. Open: WEBRTC-FAILOVER-SCENARIOS.md
2. Assess: Which scenario matches symptoms?
3. Execute: Corresponding decision tree
4. Action: Follow immediate recovery steps

# P1 Incident → 15 minutes
1. Page on-call engineer (PagerDuty)
2. Refer: WEBRTC-PROD-RUNBOOK.md → "Incident Response Procedures"
3. Execute: Step-by-step P1 procedure
4. Log: Incident ID to IF.witness
5. Communicate: Team notification via Slack

# Post-incident → 30 minutes
1. Validate: Recovery using checklists in WEBRTC-FAILOVER-SCENARIOS.md
2. Verify: Metrics recovered to normal (see WEBRTC-MONITORING-CHECKLIST.md)
3. Log: Incident summary to IF.witness
4. Escalate: If recovery incomplete, escalate to engineering lead
```

---

## Key Operational Concepts

### Architecture Principles

The WebRTC mesh is built on three InfraFabric principles:

1. **IF.TTT (Transparent, Traceable, Trustworthy)**
   - All signaling logged to IF.witness
   - Ed25519 signatures on every message
   - Complete audit trail for compliance

2. **IF.ground (Observable & Verifiable)**
   - Metrics are source of truth
   - Connection quality stats every 2 seconds
   - DTLS fingerprints validated

3. **IF.witness (Security & Compliance)**
   - All events logged with timestamps
   - Query reference: See WEBRTC-MONITORING-CHECKLIST.md
   - Incident investigation uses witness logs

### Critical Failover Mechanisms

| Scenario | Detection | Automatic | Recovery Time | Manual Action |
|----------|-----------|-----------|---|---|
| **TURN server down** | Health check fails | Yes - try next TURN | <30s | Rarely needed |
| **Signaling server down** | Connection timeout | Yes - failover to backup | <2m | May need load balancer update |
| **Network partition** | No heartbeat 30s | Yes - exponential backoff | 30s-17m | Possible restart |
| **Cert expiration** | Daily check | Yes - auto-renewal | <1 hour | Monitor renewal |
| **SRTP compromise** | Manual alert | Yes - emergency rotation | <1m | Investigate incident |

---

## Document Cross-References

### Common Questions & Answers

**Q: "Connection establishment is timing out"**
- Read: WEBRTC-PROD-RUNBOOK.md → "Common Issues & Troubleshooting" → Issue 1
- Decision Tree: WEBRTC-FAILOVER-SCENARIOS.md → "Tree 1: Connection Establishment Failure"

**Q: "Latency suddenly increased"**
- Read: WEBRTC-FAILOVER-SCENARIOS.md → "Tree 2: High Latency Detection"
- Metrics: WEBRTC-MONITORING-CHECKLIST.md → "Dashboard 2: Latency Analysis"

**Q: "How do I know what to monitor?"**
- Read: WEBRTC-MONITORING-CHECKLIST.md → "Quick Reference - Key Metrics"
- Setup: WEBRTC-MONITORING-CHECKLIST.md → "Monitoring Setup Checklist"

**Q: "Service is completely down"**
- Read: WEBRTC-PROD-RUNBOOK.md → "Incident Response Procedures" → "P1 Incident Response"
- Runbook: scripts/incident-response-p1-total-outage.sh

**Q: "Should I rollback my deployment?"**
- Read: WEBRTC-PROD-RUNBOOK.md → "Rollback Procedures"
- Automation: scripts/automated-rollback-monitor.sh

**Q: "How do I diagnose a problem?"**
- Read: WEBRTC-MONITORING-CHECKLIST.md → "IF.witness Query Reference"
- Examples: Multiple curl commands with IF.witness API

---

## Operational Runbooks (By Scenario)

### Connection Problems

| Issue | Runbook Location | Response Time |
|-------|---|---|
| Connection timeout | WEBRTC-PROD-RUNBOOK.md Issue 1 + FAILOVER Scenario A/B | 5-15 min |
| P2P connection blocked | WEBRTC-PROD-RUNBOOK.md Issue 1 | 15-30 min |
| TURN server unavailable | WEBRTC-FAILOVER-SCENARIOS.md Scenario A | 5 min |
| Signaling server down | WEBRTC-FAILOVER-SCENARIOS.md Scenario B | 2-5 min |

### Performance Issues

| Issue | Runbook Location | Response Time |
|-------|---|---|
| High latency | WEBRTC-FAILOVER-SCENARIOS.md Tree 2 | 15 min |
| Packet loss | WEBRTC-PROD-RUNBOOK.md Issue 2 | 15 min |
| High TURN usage | WEBRTC-MONITORING-CHECKLIST.md Metric: TURN Fallback Rate | 30 min |

### Security Issues

| Issue | Runbook Location | Response Time |
|-------|---|---|
| DTLS validation failure | WEBRTC-PROD-RUNBOOK.md Issue 3 | 15 min |
| Certificate expired | WEBRTC-FAILOVER-SCENARIOS.md Scenario D | <1 hour |
| Signature verification failure | WEBRTC-FAILOVER-SCENARIOS.md Tree 4 | 5 min |
| SRTP key compromise | WEBRTC-FAILOVER-SCENARIOS.md Scenario E | <1 min |

### Resource Issues

| Issue | Runbook Location | Response Time |
|-------|---|---|
| High memory | WEBRTC-PROD-RUNBOOK.md Issue 4 | 15 min |
| High CPU | WEBRTC-MONITORING-CHECKLIST.md Alert: CPU > 80% | 15 min |
| File descriptor exhaustion | WEBRTC-MONITORING-CHECKLIST.md Resource monitoring | 30 min |

---

## Metrics Dashboard Quick Reference

**Grafana URL:** https://grafana.infrafabric.local/d/webrtc-overview

### Key Dashboards

1. **WebRTC Overview (Main Dashboard)**
   - Status: Healthy/Degraded/Down
   - Active agents: Real-time count
   - Connection success rate: SLA indicator
   - Messages/sec: Throughput
   - Recent errors: Alert summary

2. **Latency & Performance**
   - P50/P95/P99 RTT (P2P vs TURN)
   - Jitter and variance
   - Connection establishment time

3. **Security & Encryption**
   - DTLS validation status
   - Signature verification rate
   - SRTP key rotation events
   - Certificate expiration countdown

4. **Resource Utilization**
   - CPU, memory, network I/O
   - File descriptors usage
   - Process metrics

---

## Contact & Escalation

### On-Call Escalation Chain

1. **Level 1 (First Response):** On-call engineer
   - Page via PagerDuty: `ops.pagerduty.com`
   - Response time: < 15 minutes

2. **Level 2 (Engineering Lead):** WebRTC team lead
   - If Level 1 unavailable: `@webrtc-oncall` in Slack
   - Response time: < 30 minutes

3. **Level 3 (VP Engineering):** VP Infrastructure
   - For P1 incidents lasting > 1 hour
   - Email: `engineering-vp@infrafabric.local`

### Support Channels

| Channel | Use For | Response Time |
|---------|---------|---|
| **PagerDuty** | P1/P2 incidents | < 5 min |
| **#incident-response** Slack | Real-time coordination | < 5 min |
| **ops@infrafabric.local** | Documentation requests | < 4 hours |

### External Contacts

- **TURN Provider:** support@turn-provider.example.com
- **Certificate Authority:** Let's Encrypt (automated)
- **ISP (if network issue):** noc@isp.example.com

---

## Learning Resources

### Understanding WebRTC

- [MDN WebRTC API Reference](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [RFC 3550 - RTP](https://tools.ietf.org/html/rfc3550) (Real-time Transport Protocol)
- [RFC 5763 - DTLS](https://tools.ietf.org/html/rfc5763) (DTLS protocol)
- [RFC 3711 - SRTP](https://tools.ietf.org/html/rfc3711) (SRTP encryption)

### InfraFabric Architecture

- [IF-REALTIME-COMMUNICATION-INTEGRATION.md](./IF-REALTIME-COMMUNICATION-INTEGRATION.md)
- [IF-REALTIME-PARALLEL-ROADMAP.md](./IF-REALTIME-PARALLEL-ROADMAP.md)
- [PHILOSOPHY-TO-TECH-MAPPING.md](./PHILOSOPHY-TO-TECH-MAPPING.md)

### Operational Practices

- [Incident Command System (ICS)](https://en.wikipedia.org/wiki/Incident_Command_System)
- [SRE Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Observability Engineering](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)

---

## Document Maintenance

### Update Schedule

- **Monthly:** Update metric thresholds based on baseline data
- **Quarterly:** Review and update decision trees based on lessons learned
- **Semi-annually:** Full audit and refresh of all procedures
- **On-demand:** Add new incident responses, update contact info

### Contributing Updates

To propose updates:

1. Create issue in GitHub with `ops-documentation` label
2. Reference relevant section in existing docs
3. Propose change with rationale
4. Submit PR with reviewed changes

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-11 | Operations Team | Initial production-ready documentation |

---

## Appendix A: Command Reference

### Quick Health Check Commands

```bash
# Check signaling server health
curl -sf https://signaling.infrafabric.local/health | jq '.'

# Check agent connectivity
curl -sf https://signaling.infrafabric.local/stats | jq '.total_agents'

# Check connection count
curl -sf https://webrtc.infrafabric.local:8443/stats | jq '.connections | length'

# Get recent errors from IF.witness
curl -X POST https://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -d '{"query":{"event":{"regex":".*error.*"}}}' | jq '.results[-5:]'

# View metrics
curl -s https://webrtc.infrafabric.local:8443/metrics
```

### Useful Scripts

All scripts referenced in this documentation are located in:

- **Deployment:** `scripts/deploy-*.sh`
- **Incident Response:** `scripts/incident-response-*.sh`
- **Monitoring:** `scripts/setup-monitoring.sh`
- **Maintenance:** `scripts/daily-maintenance.sh`
- **Testing:** `scripts/test-*.js`

---

## Appendix B: Metric Definitions

### Connection Metrics

- **Connection Success Rate:** (Established connections) / (Attempted connections) in last 5 minutes
- **P2P Connection Rate:** (Direct connections) / (Total connections)
- **TURN Fallback Rate:** (TURN relay used) / (Total connections)

### Latency Metrics

- **RTT (Round Trip Time):** Time for message to reach peer and response to return
- **P50/P95/P99:** Latency percentiles (50th, 95th, 99th)
- **Jitter:** Variance in latency measurements

### Message Metrics

- **Message Throughput:** Messages sent + received per second
- **Message Loss Rate:** (Messages sent - Messages received) / Messages sent
- **Delivery Latency:** Time from send to receipt

---

**Last Updated:** November 11, 2025
**Maintained By:** InfraFabric Operations Team
**Status:** Production Ready ✅
