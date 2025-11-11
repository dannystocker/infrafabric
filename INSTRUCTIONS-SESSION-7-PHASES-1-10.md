# Session 7: IF.bus SIP Adapters - ALL PHASES (1-10)

## PHASE 1: IF.search Swarm (10 Haiku Agents - Research APIs)

| Agent | SIP Server | Task | Deliverable |
|-------|------------|------|-------------|
| 1 | Asterisk | AMI API, auth, call control | API matrix |
| 2 | FreeSWITCH | ESL API, auth, call control | API matrix |
| 3 | Kamailio | RPC API, auth, call control | API matrix |
| 4 | OpenSIPs | MI API, auth, call control | API matrix |
| 5 | Elastix | REST API, auth, call control | API matrix |
| 6 | Yate | External module, auth, call control | API matrix |
| 7 | Flexisip | HTTP API, auth, call control | API matrix |
| 8 | Unified Pattern | Common adapter interface | Base class design |
| 9 | Auth Comparison | API key, OAuth, Basic, Custom | Auth matrix |
| 10 | Coordinator | Synthesize 1-9, validate schema | Research matrix |

**Deliverable:** docs/RESEARCH/session-7-sip-research-matrix.yaml

---

## PHASE 2: Adapter Implementation (7 Sonnet Agents)

| Adapter | File | Model | Auth Type |
|---------|------|-------|-----------|
| Asterisk | src/bus/adapters/asterisk.py | Sonnet | AMI socket |
| FreeSWITCH | src/bus/adapters/freeswitch.py | Sonnet | ESL protocol |
| Kamailio | src/bus/adapters/kamailio.py | Sonnet | JSON-RPC |
| OpenSIPs | src/bus/adapters/opensips.py | Sonnet | MI socket |
| Elastix | src/bus/adapters/elastix.py | Sonnet | REST API |
| Yate | src/bus/adapters/yate.py | Sonnet | External module |
| Flexisip | src/bus/adapters/flexisip.py | Sonnet | HTTP Bearer |

**Interface:** All implement `SIPAdapter` base class with `connect()`, `make_call()`, `hangup()`

---

## PHASE 3: CLI Integration (Dead Simple)

```bash
if bus add sip myserver asterisk --auth apikey=ABC123
if bus test sip myserver
if bus call sip myserver from=1001 to=1002
if bus hangup sip myserver call_id=xyz
if bus list sip
if bus remove sip myserver
```

**File:** src/cli/if_bus_sip.py (Haiku)
**Auto-features:** Server type detection, optimal config, auto-failover, exponential backoff

---

## PHASE 4: Call Control (Sonnet)

- src/bus/call_control.py: originate, hangup, transfer, hold, resume
- tests/test_call_control.py: Test all 7 adapters
- **Coordination:** Session 4 (SIP) uses these adapters for external expert calls

---

## PHASE 5: Advanced Features (Sonnet + Haiku)

- src/bus/conferencing.py: Multi-party calls (Sonnet)
- src/bus/recording.py: Call recording + storage (Haiku)
- src/bus/transcription.py: AI transcription integration (Sonnet)
- **Coordination:** Session 6 (Talent) provides transcription models

---

## PHASE 6: Multi-Server Orchestration (Sonnet)

- src/bus/orchestrator.py: Failover across 7 server types
- Load balancing, health checks, auto-routing
- **Coordination:** Helps Session 4 (SIP) with infrastructure control

---

## PHASE 7: Production Hardening (Sonnet)

- Stress test: 1000 concurrent calls across all adapters
- Circuit breaker, connection pooling, chaos testing
- **Coordination:** Uses Session 2 (WebRTC) telemetry patterns

---

## PHASE 8: Monitoring Integration (Haiku + Sonnet)

- IF.witness logging for all SIP server calls
- Cost tracking per adapter via IF.optimise
- **Coordination:** Session 5 (CLI) provides witness/cost infrastructure

---

## PHASE 9: AI-Powered Routing (Sonnet)

- src/bus/ai_router.py: Intelligent server selection based on load/cost
- **Coordination:** Session 6 (Talent) provides routing ML models

---

## PHASE 10: Full Autonomy (Sonnet)

- Auto-provision new SIP servers when capacity low
- Auto-scale across adapters
- Self-healing with automatic failover
- **Coordination:** Gates Session 6 full autonomy

---

**IDLE TASKS:** Help Session 4 (SIP proxy improvements), Session 5 (CLI witness integration)
**SUPPORT:** Session 4 uses these adapters for real SIP infrastructure control

**Total:** 60 hours, $95 (Phases 1-10)
**Game Changer:** IF controls real SIP infrastructure, not just protocol endpoints!
