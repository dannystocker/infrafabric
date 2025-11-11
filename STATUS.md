# Worker Status: Session 4 (SIP External Expert Calls)

## Identity
```yaml
session: SESSION-4-SIP
branch: claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7
role: SIP External Expert Calls (IF.ESCALATE)
workstream: 4 of 4
agent: Claude Sonnet 4.5 (Integration specialist)
```

## Current Status
```yaml
status: waiting_for_instructions
last_completed: null
timestamp: 2025-11-11T21:15:00Z
ready_for: INSTRUCTIONS-SESSION-4.md
dependencies:
  - session_2_webrtc: pending
  - session_3_h323: pending
  - interface_contracts: pending
```

## Capability Summary
**Workstream 4: SIP External Expert Calls (IF.ESCALATE)**

### Deliverables Ready to Implement:
1. `src/communication/sip_proxy.py` (~300 lines)
   - Kamailio configuration hooks (Python)
   - Custom header parsing (X-IF-Trace-ID, X-IF-Hazard, X-IF-Signature)
   - IF.guard policy gate (approve external calls)
   - IF.witness logging (SIP INVITE, SDP, responses)

2. `config/kamailio.cfg` (~500 lines)
   - SIP proxy routing rules
   - External advisor registry (sip:expert-*@external.advisor)
   - IF.guard policy integration

3. `src/communication/sip_h323_gateway.py` (~400 lines)
   - Bridge external SIP experts ↔ internal H.323 council
   - Media transcoding (if needed)
   - Call state synchronization

4. `docs/SIP-ESCALATE-INTEGRATION.md` (tutorial)
   - End-to-end ESCALATE flow
   - SIP + H.323 + WebRTC integration
   - Philosophy grounding (Popper falsifiability)

5. `tests/test_sip_escalate.py` (integration tests)
   - Test IFMessage ESCALATE → SIP INVITE
   - Test IF.guard policy approval
   - Test SIP-H.323 bridge
   - Test WebRTC evidence sharing

6. `docs/INTERFACES/workstream-4-sip-contract.yaml` (interface contract)

### Integration Requirements:
- **Session 2 (WebRTC):** IFAgentWebRTC.sendIFMessage() for evidence sharing
- **Session 3 (H.323):** H323Gatekeeper.bridge_external_call() for council bridge
- **Session 5:** Provide SIP interface contract for final integration

### Philosophy Grounding:
- Wu Lun (五倫): 朋友 (Friends) — SIP peers are equals
- Popper Falsifiability: External experts provide contrarian views
- IF.ground: Observable (SIP is text-based, fully auditable)
- IF.TTT: Traceable, Transparent, Trustworthy (Ed25519 signed)

### Budget Allocation:
- Estimated: 16-22 hours
- Cost: ~$20-28 (Sonnet integration work)
- Budget: $25 allocated

## Autonomous Mode Configuration

### Sub-Agent Strategy:
```yaml
simple_tasks:
  model: haiku
  tasks:
    - YAML interface contracts
    - Test scaffolding
    - Documentation markdown

complex_tasks:
  model: sonnet
  tasks:
    - sip_proxy.py implementation
    - sip_h323_gateway.py bridge logic
    - Kamailio configuration
    - Integration testing
```

### Polling Configuration:
```bash
poll_interval: 60 seconds
instruction_file: INSTRUCTIONS-SESSION-4.md
branch: claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7
```

## Dependencies Status

### Blocking Dependencies:
- ❌ **Session 2 (WebRTC):** Branch `claude/realtime-workstream-2-webrtc` not found
- ❌ **Session 3 (H.323):** Branch `claude/realtime-workstream-3-h323` not found
- ❌ **Interface Contracts:**
  - `docs/INTERFACES/workstream-2-webrtc-contract.yaml` missing
  - `docs/INTERFACES/workstream-3-h323-contract.yaml` missing

### Required Context Files (Missing):
- ❌ `docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md`
- ❌ `docs/IF-REALTIME-PARALLEL-ROADMAP.md`

### Available Context:
- ✅ `schemas/ifmessage/v1.0.schema.json` exists
- ✅ InfraFabric framework structure understood
- ✅ IF.ground, IF.witness, IF.TTT principles documented

## Ready State

**Worker is READY but BLOCKED by dependencies.**

### Options:
1. **Wait for Dependencies** (Recommended per task instructions)
   - Sessions 2 & 3 must complete first
   - Interface contracts must be published

2. **Implement with Mocks** (Alternative)
   - Create stub interfaces for Session 2 & 3 APIs
   - Implement SIP functionality standalone
   - Add integration points for later connection

3. **Request Full Stack** (Alternative)
   - Implement Sessions 2, 3, and 4 sequentially
   - Requires ~60 hours total (~3x budget)

### Awaiting Instructions:
Please create `INSTRUCTIONS-SESSION-4.md` with one of:
- `WAIT` - Continue polling until dependencies complete
- `MOCK` - Implement with stub interfaces
- `STANDALONE` - Implement SIP independently
- `FULL` - Implement all three sessions

## IF.TTT Compliance Ready

All commits will include:
- Clear description of changes
- Philosophy grounding (Wu Lun, Popper, IF.ground principles)
- Test results (if code changed)
- Trace ID linking to instruction file

## Cost Tracking Ready

`COST-REPORT.yaml` will track:
- Task name and model used
- Token counts and costs
- Budget utilization (out of $25)
- IF.optimise strategy (Haiku for simple, Sonnet for complex)

---

**Status:** 🟡 READY & WAITING FOR INSTRUCTIONS
**Next Action:** Poll for `INSTRUCTIONS-SESSION-4.md`
**Last Updated:** 2025-11-11T21:15:00Z

🤖 Auto-polling worker configured and ready for autonomous execution
