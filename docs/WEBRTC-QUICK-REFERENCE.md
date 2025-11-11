# WebRTC Agent Mesh - Quick Reference Card

**Print This & Keep at Your Desk**
**For On-Call Engineers**

---

## 🚨 P1 Incident: Total Outage

```
Symptom: Zero agents connected, all connections failing

1. ASSESS (30 seconds)
   □ Check: curl -sf https://signaling.infrafabric.local/health
   □ Page: PagerDuty incident (urgent)
   □ Notify: Slack #incident-response

2. IMMEDIATE ACTIONS (2-5 minutes)
   □ IF signaling server down → systemctl restart webrtc-signaling-server
   □ IF database down → Check IF.witness status
   □ IF both up → Check firewall rules (UDP 5000-65535)

3. ESCALATE IF NOT RECOVERED (5 minutes)
   □ Contact: Engineering lead (@webrtc-oncall)
   □ Run: bash scripts/incident-response-p1-total-outage.sh

Full Runbook: WEBRTC-PROD-RUNBOOK.md § "P1 Incident Response"
```

---

## ⚠️ P2 Incident: High Latency (>500ms)

```
Symptom: Latency exceeds threshold, 20%+ connections affected

1. DIAGNOSE (5 minutes)
   □ Check dashboard: https://grafana.infrafabric.local/d/webrtc-latency
   □ Query: curl http://prometheus:9090/metrics | grep webrtc_rtt
   □ Determine: P2P or TURN issue?
      → P2P: Network path issue
      → TURN: Relay server overloaded

2. MITIGATION (10 minutes)
   IF TURN overloaded:
   □ Enable bandwidth adaptation: BANDWIDTH_ADAPTATION=true
   □ Failover to secondary TURN: bash scripts/recover-turn-server-failure.sh

   IF P2P congestion:
   □ Reduce message rate in application
   □ Monitor for 5 minutes

3. ESCALATE IF UNRESOLVED (15 minutes)
   □ Notify: WebRTC team

Full Runbook: WEBRTC-FAILOVER-SCENARIOS.md § "Tree 2: High Latency Detection"
```

---

## 🔒 P1 Security: Certificate Validation Failure

```
Symptom: Multiple DTLS validation failures in IF.witness

IMMEDIATE ACTIONS (1 minute):
□ Severity: CRITICAL - stop further actions
□ Page: Security team + on-call engineer
□ Isolate: Check affected peers in logs
□ Query: curl http://witness.infrafabric.local/api/query \
    -d '{"query":{"event":"dtls_validation_failures"}}'

INVESTIGATION (5 minutes):
□ Is it cert expired? → Check: openssl x509 -in /etc/webrtc/server.crt -noout -dates
□ Is it self-signed in prod? → Check config: ALLOW_SELF_SIGNED_CERTS
□ Is it MITM attack? → Check: Peer IP addresses, network path

REMEDIATION:
□ If expired cert: bash scripts/certificate-rotation-procedure.sh
□ If self-signed in prod: Deploy proper CA certificate, restart
□ If possible MITM: Isolate network, escalate to security team

Full Runbook: WEBRTC-FAILOVER-SCENARIOS.md § "Scenario D: Certificate Expiration"
```

---

## 📊 Monitoring Dashboard Health Checks

```
BEFORE STARTING SHIFT:

□ Dashboard: https://grafana.infrafabric.local/d/webrtc-overview
   ✓ Green? → Proceed with normal ops
   ✗ Red?   → Investigate alerts section

□ Connection Success Rate: Should be >95%
   ✓ >95%  → Healthy
   ✗ <95%  → Check WEBRTC-PROD-RUNBOOK.md § "Issue 1"

□ P50 Latency (P2P): Should be <50ms
   ✓ <50ms  → Healthy
   ⚠️ 50-100ms → Monitor
   ✗ >100ms → See "P2 Incident" section above

□ TURN Fallback Rate: Should be <20%
   ✓ <20%  → Normal
   ⚠️ 20-50% → Investigate network
   ✗ >50%   → TURN server issue

□ Recent Errors: Section on main dashboard
   ✓ None   → Good
   ✗ Any    → Click for details
```

---

## 🔄 Common Failover Scenarios

| Scenario | Detection | Quick Fix | Full Runbook |
|----------|-----------|-----------|---|
| **TURN Down** | Latency >500ms, high TURN usage | Next TURN server auto-tried | Scenario A |
| **Signaling Down** | Cannot register agents | Auto-failover to backup | Scenario B |
| **Network Partition** | Heartbeat missing 30s | Exponential backoff reconnect | Scenario C |
| **Cert Expiring** | Daily check, <7 days warning | Auto-renewal or manual rotation | Scenario D |
| **SRTP Compromised** | Manual security alert | Emergency key rotation | Scenario E |

---

## 🛠️ Most Common Fixes

### Issue: Connection Timeout (Stuck >5 seconds)

```
QUICK DIAGNOSIS (2 min):
1. Is STUN server reachable?
   $ nc -zv stun.l.google.com 19302

2. Is TURN server reachable?
   $ nc -zv turn1.example.com 3478

3. Is it a firewall issue?
   $ sudo ufw allow out 5000:65535/udp

QUICK FIX:
→ If STUN fails: Add redundant STUN (automatic)
→ If TURN fails: Failover to secondary TURN
→ If firewall fails: Open UDP port range
```

### Issue: High Memory (>700MB)

```
QUICK DIAGNOSIS (2 min):
1. Check trend:
   $ curl http://prometheus:9090/metrics | grep memory

2. Check for connection leaks:
   $ curl http://webrtc.infrafabric.local:8443/stats | jq '.connections | length'

QUICK FIX:
→ If leaking: Restart service → systemctl restart webrtc-mesh
→ If stable: Monitor, escalate if approaching limit
```

### Issue: Signature Verification Failure

```
QUICK ACTIONS (30 seconds):
1. DON'T ignore this - it's a security event
2. ISOLATE affected peer if possible
3. PAGE security team immediately
4. Query witness for scope:
   curl http://witness.infrafabric.local/api/query \
     -d '{"query":{"event":"signature_verification_failed"}}'

NEXT:
→ Investigate peer identity and network path
→ Check for MITM attack indicators
→ Follow WEBRTC-FAILOVER-SCENARIOS.md § "Tree 4: Security Event Response"
```

---

## 📋 Essential Commands

```bash
# Health Check (1 minute)
curl -sf https://signaling.infrafabric.local/health && echo "✓ Signaling OK"
curl -sf https://webrtc.infrafabric.local:8443/health && echo "✓ WebRTC OK"

# View Dashboard
open https://grafana.infrafabric.local/d/webrtc-overview

# Check recent errors
curl http://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -d '{"query":{"event":{"regex":".*error.*"}},"time_range":{"from":"-30m","to":"now"}}' \
  | jq '.results'

# View all agents
curl https://signaling.infrafabric.local/stats | jq '.agents'

# Get metrics
curl https://webrtc.infrafabric.local:8443/metrics | head -20

# Check certificate expiry
openssl x509 -in /etc/webrtc/server.crt -noout -enddate

# View service logs
tail -f /var/log/webrtc/mesh.log
tail -f /var/log/webrtc/signaling-server.log

# Restart services
systemctl restart webrtc-mesh
systemctl restart webrtc-signaling-server
```

---

## 📞 Who to Page

| Situation | Page | Response Time |
|-----------|------|---|
| **P1 Incident** | On-call engineer (PagerDuty) | <15 min |
| **P1 > 30 min** | Engineering lead (@webrtc-oncall) | <30 min |
| **P1 > 1 hour** | VP Engineering | <1 hour |
| **Security Issue** | Security team + on-call | <5 min |
| **Non-emergency** | ops@infrafabric.local | <4 hours |

---

## 🔗 Key Links

| Resource | URL |
|----------|-----|
| **Main Dashboard** | https://grafana.infrafabric.local/d/webrtc-overview |
| **Prometheus** | http://prometheus:9090 |
| **IF.witness Query** | https://witness.infrafabric.local/query |
| **Runbook Repo** | https://github.com/infrafabric/runbooks |
| **API Docs** | https://api-docs.infrafabric.local/webrtc |

---

## 📖 Full Documentation

For detailed procedures, consult:

1. **WEBRTC-PROD-RUNBOOK.md** - Complete operations guide
2. **WEBRTC-FAILOVER-SCENARIOS.md** - Incident decision trees
3. **WEBRTC-MONITORING-CHECKLIST.md** - Monitoring setup & queries
4. **WEBRTC-OPS-README.md** - Documentation index

---

## ✅ Pre-Shift Checklist (2 minutes)

```
□ Coffee ☕
□ Check Grafana dashboard for red/yellow
□ Verify PagerDuty is working
□ Check if you can SSH to production
□ Open WEBRTC-QUICK-REFERENCE.md (this file) in new tab
□ Skim latest incident reports (if any)

You're ready to go!
```

---

**Incident Support:** Page on-call engineer
**Questions:** ops@infrafabric.local
**Last Updated:** November 11, 2025

Keep this card visible on your desk. In an incident, refer to the appropriate section above, then consult full runbooks for details.
