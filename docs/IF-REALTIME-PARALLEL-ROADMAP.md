# IF.connect Real-Time Communication — Parallel Implementation Roadmap

**Version:** 1.0
**Date:** 2025-11-11
**Purpose:** Divide real-time communication implementation across multiple Claude sessions using IF.optimise (cost efficiency) and IF.swarm (agent coordination)

---

## Strategic Division: 4 Independent Workstreams

### Workstream Philosophy

**IF.optimise Principle:** Maximize parallel execution, minimize dependencies
- Each workstream is **independently testable**
- Shared interface contracts defined upfront
- Integration happens at **Level 3 (IF.connect protocol)**, not within modules

**IF.swarm Principle:** Heterogeneous agent specialization
- **Early Bloomer (GPT):** Rapid prototyping (NDI, WebRTC)
- **Late Bloomer (Gemini):** Deep specification (H.323, SIP policy)
- **Steady Performer (Claude):** Integration & IF.witness logging

---

## Workstream 1: NDI Evidence Streaming (IF.witness)

**Agent Assignment:** Claude (Steady Performer)
- **Why:** Requires deep IF.witness integration, hash chain consistency, Ed25519 signatures
- **Complexity:** Medium (NDI SDK learning curve, metadata injection)
- **Dependencies:** None (standalone witness enhancement)

**Tasks:**
1. Install NDI SDK (Vizrt NDI SDK 5.6)
2. Create `IF.witness.ndi-publisher` (Python)
   - Wrap existing IF.yologuard scanner output as NDI stream
   - Inject witness hash chain into NDI metadata packets
   - Sign each frame with Ed25519
3. Create `IF.guard.ndi-viewer` (Python)
   - Subscribe to NDI streams
   - Verify metadata signatures in real-time
   - Display stream + overlay witness provenance
4. Test: Stream live secret scanning session to Guardian review

**Deliverables:**
- `src/communication/ndi_witness_publisher.py` (200 lines)
- `src/communication/ndi_guardian_viewer.py` (150 lines)
- `docs/NDI-WITNESS-INTEGRATION.md` (case study)
- `tests/test_ndi_witness.py` (unit tests)

**Effort:** 12-16 hours
**Cost:** ~$15-20 (Sonnet 4.5)
**Parallel Dependency:** None

---

## Workstream 2: WebRTC Agent Mesh (IF.swarm)

**Agent Assignment:** GPT-5 (Early Bloomer)
- **Why:** Fast iteration on JavaScript/TypeScript, excellent at WebRTC boilerplate
- **Complexity:** Medium (WebRTC signaling, ICE negotiation, STUN/TURN)
- **Dependencies:** None (standalone swarm enhancement)

**Tasks:**
1. Deploy WebRTC signaling server (Janus Gateway or mediasoup)
2. Implement `IFAgentWebRTC` class (TypeScript)
   - SDP offer/answer generation
   - ICE candidate exchange
   - DataChannel for IFMessage v2.1 transport
   - Ed25519 signature on every message
3. Integrate with IFMessage v2.1 schema
   - DataChannel = transport layer
   - SDP logging to IF.witness
4. Test: 5-agent swarm peer-to-peer mesh

**Deliverables:**
- `src/communication/webrtc-agent-mesh.ts` (400 lines)
- `src/communication/webrtc-signaling-server.ts` (200 lines)
- `tests/test_webrtc_mesh.spec.ts` (100 lines)
- `docs/WEBRTC-SWARM-MESH.md` (tutorial)

**Effort:** 10-14 hours
**Cost:** ~$8-12 (GPT-5 efficient on boilerplate)
**Parallel Dependency:** None

---

## Workstream 3: H.323 Guardian Council (IF.guard)

**Agent Assignment:** Gemini 2.5 Pro (Late Bloomer)
- **Why:** Requires deep policy design (Kantian duty gates), H.323 spec interpretation, Ubuntu consensus modeling
- **Complexity:** High (H.323 is complex, requires C++ interop)
- **Dependencies:** Partial (needs IFMessage v2.1 hazard routing, but can mock initially)

**Tasks:**
1. Deploy H.323 infrastructure
   - Gatekeeper: GNU Gatekeeper or OpenH323
   - MCU: Jitsi Videobridge or Kurento
2. Implement `IF.guard.h323-gatekeeper` (Python wrapper + C++ bindings)
   - Ed25519 admission control
   - Bandwidth quotas per guardian
   - IF.witness logging for all ARQ/ACF/ARJ messages
3. Implement `IF.guard.h323-mcu` (configuration + integration)
   - Centralized audio mixing
   - Continuous presence video (4x4 grid)
   - T.120 evidence whiteboard
4. Design policy gates (Kantian duty constraints)
   - PII detection → reject
   - Unregistered terminals → reject
   - Bandwidth quota exceeded → reject
5. Test: 15-guardian council call, ESCALATE trigger, decision recording

**Deliverables:**
- `src/communication/h323_gatekeeper.py` (500 lines)
- `src/communication/h323_mcu_config.py` (200 lines)
- `docs/H323-GUARD-COUNCIL.md` (architecture)
- `docs/H323-KANTIAN-POLICY.md` (policy specification)
- `tests/test_h323_admission.py` (policy tests)

**Effort:** 20-28 hours
**Cost:** ~$25-35 (Gemini late-bloomer depth required)
**Parallel Dependency:** IFMessage v2.1 hazard routing (can mock, integrate later)

---

## Workstream 4: SIP External Expert Calls (IF.ESCALATE)

**Agent Assignment:** Claude (Steady Performer)
- **Why:** Requires integration with existing IF.ESCALATE flow, IF.guard policy approval, IF.witness audit trail
- **Complexity:** Medium-High (SIP proxy configuration, policy integration)
- **Dependencies:** Strong (requires H.323 gateway, IFMessage v2.1)

**Tasks:**
1. Deploy SIP infrastructure
   - Proxy: Kamailio or OpenSIPS
   - Registrar: Built-in to proxy
2. Implement `IF.connect.sip-proxy` (Kamailio config + Python hooks)
   - Custom header parsing (X-IF-Trace-ID, X-IF-Hazard, X-IF-Signature)
   - IF.guard policy gate (approve external calls)
   - IF.witness logging (SIP INVITE, SDP, responses)
3. Implement SIP-H.323 gateway
   - Bridge external SIP experts ↔ internal H.323 council
   - Media transcoding if needed
4. Integrate with IF.ESCALATE
   - IFMessage with hazard → SIP INVITE flow
   - Evidence sharing via WebRTC DataChannel (hybrid SIP+WebRTC)
5. Test: ESCALATE → external expert call, evidence shared, decision logged

**Deliverables:**
- `src/communication/sip_proxy.py` (300 lines)
- `config/kamailio.cfg` (500 lines)
- `src/communication/sip_h323_gateway.py` (400 lines)
- `docs/SIP-ESCALATE-INTEGRATION.md` (tutorial)
- `tests/test_sip_escalate.py` (integration tests)

**Effort:** 16-22 hours
**Cost:** ~$20-28 (Sonnet 4.5)
**Parallel Dependency:** H.323 gateway (Workstream 3), WebRTC DataChannel (Workstream 2)

---

## Integration Phase (Week 9-10)

**Agent Assignment:** Claude (Integration Orchestrator)
- **Why:** Requires cross-workstream coordination, IF.witness audit trail consistency, IF.TTT validation

**Tasks:**
1. **Level 3 Integration:** Wire all 4 workstreams to IFMessage v2.1 protocol
   - NDI streams trigger on IF.witness events
   - WebRTC mesh receives IFMessage over DataChannel
   - H.323 calls triggered by IFMessage ESCALATE
   - SIP calls integrated with H.323 gateway
2. **IF.witness Consolidation:** Unified audit trail
   - Every stream/call/message logged
   - Consistent Ed25519 signature format
   - Trace IDs propagate across protocols
3. **IF.TTT Validation:** End-to-end compliance check
   - Traceable: Every operation has trace_id + provenance
   - Transparent: SDP, SIP headers, NDI metadata all logged
   - Trustworthy: Ed25519 signatures verified at every layer
4. **Integration Tests:** Cross-protocol flows
   - Test: IF.yologuard detects secret → NDI stream → Guardian views → H.323 council → Decision logged
   - Test: IFMessage ESCALATE → SIP call → External expert → WebRTC evidence → H.323 council → Decision
5. **Performance Benchmarking:** Meet success metrics
   - IF.ESCALATE latency < 30s
   - IF.witness coverage 100%
   - IF.guard quorum 15+ concurrent
   - IF.swarm mesh latency < 50ms

**Deliverables:**
- `src/communication/if_connect_integration.py` (600 lines)
- `tests/test_integration_realtime.py` (200 lines)
- `docs/IF-REALTIME-INTEGRATION-COMPLETE.md` (case study)
- Performance report: IF-REALTIME-BENCHMARKS.md

**Effort:** 16-24 hours
**Cost:** ~$20-30 (Sonnet 4.5)
**Parallel Dependency:** All 4 workstreams complete

---

## Dependency Graph

```
Workstream 1 (NDI)     ─┐
                        ├──> Integration Phase (Week 9-10)
Workstream 2 (WebRTC)  ─┤
                        │
Workstream 3 (H.323)   ─┤
                        │
Workstream 4 (SIP)     ─┘
   └─(depends on)─> Workstream 3
   └─(depends on)─> Workstream 2
```

**Critical Path:** Workstream 3 (H.323) → Workstream 4 (SIP) → Integration
**Parallel Capacity:** 3 workstreams can run simultaneously (1, 2, 3)

---

## IF.swarm Session Allocation

### Session 1: NDI Evidence Streaming
- **Agent:** Claude Sonnet 4.5
- **Prompt:** "Implement IF.witness.ndi-publisher using NDI SDK 5.6, inject hash chain metadata with Ed25519 signatures"
- **Budget:** $20, 14 hours
- **Deliverable:** `src/communication/ndi_witness_publisher.py`

### Session 2: WebRTC Agent Mesh
- **Agent:** GPT-5
- **Prompt:** "Implement IFAgentWebRTC class with signaling server (Janus), DataChannel for IFMessage v2.1, Ed25519 signing"
- **Budget:** $12, 12 hours
- **Deliverable:** `src/communication/webrtc-agent-mesh.ts`

### Session 3: H.323 Guardian Council
- **Agent:** Gemini 2.5 Pro
- **Prompt:** "Deploy H.323 Gatekeeper + MCU, implement Kantian admission control, Ed25519 policy gates, IF.witness logging"
- **Budget:** $30, 24 hours
- **Deliverable:** `src/communication/h323_gatekeeper.py`

### Session 4: SIP External Expert Calls
- **Agent:** Claude Sonnet 4.5
- **Prompt:** "Configure Kamailio SIP proxy, implement IF.guard policy gate, SIP-H.323 gateway, IF.ESCALATE integration"
- **Budget:** $25, 20 hours
- **Deliverable:** `src/communication/sip_proxy.py`

### Session 5: Integration & Validation
- **Agent:** Claude Sonnet 4.5 (orchestrator)
- **Prompt:** "Integrate all 4 workstreams via IFMessage v2.1, validate IF.TTT compliance, benchmark performance"
- **Budget:** $25, 20 hours
- **Deliverable:** `src/communication/if_connect_integration.py`

**Total Budget:** $112
**Total Time:** ~90 hours (but parallelized to ~3-4 weeks calendar time)

---

## IF.optimise Cost Breakdown

| Workstream | Agent | Est. Cost | Est. Hours | $/Hour |
|------------|-------|-----------|------------|--------|
| NDI | Claude Sonnet 4.5 | $20 | 14 | $1.43 |
| WebRTC | GPT-5 | $12 | 12 | $1.00 |
| H.323 | Gemini 2.5 Pro | $30 | 24 | $1.25 |
| SIP | Claude Sonnet 4.5 | $25 | 20 | $1.25 |
| Integration | Claude Sonnet 4.5 | $25 | 20 | $1.25 |
| **TOTAL** | **Mixed** | **$112** | **90** | **$1.24** |

**Optimization:** Using GPT-5 for boilerplate (WebRTC) saves ~$8 vs Claude for same task

---

## Handoff Protocol (Between Sessions)

### Session N → Session N+1 Handoff

**Required Artifacts:**
1. **Code Repository:**
   - Branch: `claude/realtime-workstream-{N}`
   - Commit: Final working state + tests passing
2. **Interface Contract:**
   - File: `docs/INTERFACES/workstream-{N}-contract.yaml`
   - Contains: Function signatures, message schemas, test fixtures
3. **IF.witness Log:**
   - File: `logs/workstream-{N}-witness.jsonl`
   - Contains: All development events, decisions, failures
4. **Known Issues:**
   - File: `docs/WORKSTREAM-{N}-ISSUES.md`
   - Contains: Blockers, assumptions, TODOs

**Example Handoff (WebRTC → SIP):**

```yaml
# docs/INTERFACES/workstream-2-webrtc-contract.yaml
webrtc_datachannel_interface:
  class: IFAgentWebRTC
  methods:
    - name: sendIFMessage
      params:
        - message: IFMessage (v2.1 schema)
      returns: Promise<void>
      errors:
        - SignatureVerificationFailed
        - DataChannelClosed

    - name: onIFMessage
      type: EventHandler
      params:
        - message: IFMessage (verified)
      description: "Triggered when peer sends IFMessage"

  test_fixtures:
    - valid_ifmessage_escalate.json
    - valid_sdp_offer.json
    - valid_ice_candidates.json

  integration_notes:
    - "SIP gateway can use this DataChannel for evidence sharing"
    - "SDP must be logged to IF.witness before connection"
```

**Handoff Checklist:**
- ✅ All tests passing
- ✅ Interface contract documented
- ✅ IF.witness logs complete
- ✅ Known issues documented
- ✅ Code committed + pushed
- ✅ Next session can import as library

---

## Success Criteria (Post-Integration)

### Functional Requirements
- ✅ **IF.ESCALATE Flow:** Hazard detection → H.323 call < 30s
- ✅ **IF.witness Coverage:** 100% of NDI frames have hash chain
- ✅ **IF.guard Quorum:** 15+ guardians concurrent H.323
- ✅ **IF.swarm Mesh:** 8+ agents WebRTC < 50ms latency

### IF.TTT Compliance
- ✅ **Traceable:** Every call/stream has trace_id + provenance
- ✅ **Transparent:** SDP, SIP headers, NDI metadata logged
- ✅ **Trustworthy:** Ed25519 signatures verified at every layer

### Philosophy Grounding
- ✅ **Vienna Circle:** 2+ sources for every critical claim (NDI mDNS + Discovery Server)
- ✅ **Ubuntu:** Council consensus via H.323 MCU mixed audio
- ✅ **Popper:** External experts via SIP provide falsifiability
- ✅ **Indra's Net:** WebRTC mesh reflects all peer states

---

## Next Steps

1. **User Approval:** Review this roadmap, confirm workstream division
2. **Session Kickoff:** Launch Sessions 1-3 in parallel (NDI + WebRTC + H.323)
3. **Session 4 Queue:** Wait for H.323 complete, then launch SIP
4. **Session 5 Final:** Integration orchestrator ties all workstreams together

**Estimated Calendar Time:** 4-6 weeks (with 3 parallel sessions)
**Estimated Cost:** $112 total
**Estimated Human Oversight:** 10-15 hours (reviewing handoffs, approving integrations)

---

**Citation:** `if://doc/realtime-parallel-roadmap-2025-11-11`
**Status:** Ready for multi-session execution
**Dependencies:** IFMessage v2.1 schema (already exists), IF.witness logging (already exists)
