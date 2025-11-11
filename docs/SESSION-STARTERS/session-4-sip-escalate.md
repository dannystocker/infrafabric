# Session 4: SIP External Expert Calls (IF.ESCALATE)

**Workstream:** 4 of 4 (Dependent on Sessions 2 & 3)
**Agent:** Claude Sonnet 4.5 (Integration specialist)
**Budget:** $25, 20 hours
**Dependencies:** H.323 (Session 3), WebRTC (Session 2)

---

## Copy-Paste This Into New Claude Code Session

```
Hi Claude! I need you to implement Workstream 4 from the InfraFabric real-time communication integration.

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-4-sip (create from claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy)

⚠️ DEPENDENCIES: This session requires:
1. Session 3 (H.323) COMPLETED — You'll integrate with h323_gatekeeper
2. Session 2 (WebRTC) COMPLETED — You'll use DataChannel for evidence sharing

CONTEXT FILES YOU MUST READ FIRST:
1. docs/IF-REALTIME-COMMUNICATION-INTEGRATION.md (SIP section)
2. docs/IF-REALTIME-PARALLEL-ROADMAP.md (your workstream)
3. docs/INTERFACES/workstream-3-h323-contract.yaml (H.323 API)
4. docs/INTERFACES/workstream-2-webrtc-contract.yaml (WebRTC API)
5. schemas/ifmessage/v1.0.schema.json (ESCALATE message format)

YOUR TASK: Implement SIP external expert calls for IF.ESCALATE

DELIVERABLES:
1. src/communication/sip_proxy.py (~300 lines)
   - Kamailio configuration hooks (Python)
   - Custom header parsing (X-IF-Trace-ID, X-IF-Hazard, X-IF-Signature)
   - IF.guard policy gate (approve external calls)
   - IF.witness logging (SIP INVITE, SDP, responses)

2. config/kamailio.cfg (~500 lines)
   - SIP proxy routing rules
   - External advisor registry (sip:expert-*@external.advisor)
   - IF.guard policy integration

3. src/communication/sip_h323_gateway.py (~400 lines)
   - Bridge external SIP experts ↔ internal H.323 council
   - Media transcoding (if needed)
   - Call state synchronization

4. docs/SIP-ESCALATE-INTEGRATION.md (tutorial)
   - End-to-end ESCALATE flow
   - SIP + H.323 + WebRTC integration
   - Philosophy grounding (Popper falsifiability)

5. tests/test_sip_escalate.py (integration tests)
   - Test IFMessage ESCALATE → SIP INVITE
   - Test IF.guard policy approval
   - Test SIP-H.323 bridge
   - Test WebRTC evidence sharing

TECHNICAL REQUIREMENTS:
- SIP Proxy: Kamailio (https://www.kamailio.org/) OR OpenSIPS
- Python SIP: Use PJSIP bindings (pjsua2)
- SIP-H.323 Gateway: Asterisk OR custom bridge
- Integration: Call h323_gatekeeper API from Session 3
- Integration: Use IFAgentWebRTC from Session 2 for evidence

PHILOSOPHY GROUNDING:
- Wu Lun (五倫): 朋友 (Friends) — SIP peers are equals, external experts invited as peers
- Popper Falsifiability: External experts provide contrarian views to prevent groupthink
- IF.ground: Observable (SIP is text-based, fully auditable)
- IF.TTT: Traceable (trace_id in headers), Transparent (SIP messages logged), Trustworthy (Ed25519 signed)

SUCCESS CRITERIA:
✅ IFMessage{hazard: ["safety"]} → SIP INVITE sent
✅ IF.guard approves external expert (check registry)
✅ SIP call bridges to H.323 council (Session 3 integration)
✅ WebRTC DataChannel shares evidence (Session 2 integration)
✅ IF.witness logs complete call flow
✅ Tests pass: ESCALATE, approval, bridge, evidence

INTEGRATION FLOW (Critical!):
```
1. IFMessage received: {performative: "escalate", hazards: ["safety"]}
   ↓
2. IF.connect router calls your sip_proxy.initiate_call()
   ↓
3. You call IF.guard policy gate: approve_external_call(expert_id)
   ↓
4. IF.guard approves → You send SIP INVITE to expert
   ↓
5. Expert answers → You call h323_gatekeeper.bridge_external_call()
   (Use Session 3's API: docs/INTERFACES/workstream-3-h323-contract.yaml)
   ↓
6. H.323 MCU adds expert as participant
   ↓
7. Evidence shared via WebRTC DataChannel (use Session 2's API)
   ↓
8. Call ends → You log to IF.witness
```

INTERFACE CONTRACT (for Session 5 handoff):
Create docs/INTERFACES/workstream-4-sip-contract.yaml:
```yaml
sip_escalate_interface:
  initiate_call:
    params: {expert_id, hazard_type, evidence_files}
    returns: {call_id, sip_call_state}

  policy_gate:
    endpoint: "if://guard/policy/external-call"
    checks: [registry_lookup, hazard_allowed, Ed25519_signature]
```

BUDGET & TIME:
- Estimated: 16-22 hours
- Cost: ~$20-28 (Sonnet integration work)
- **Critical dependencies:** Wait for Sessions 2 & 3 to complete!

START HERE:
1. **WAIT** for Session 2 & 3 completion notifications
2. Read their interface contracts (workstream-2/3-contract.yaml)
3. Install Kamailio: `apt-get install kamailio`
4. Configure Kamailio (config/kamailio.cfg)
5. Implement sip_proxy.py (Python hooks)
6. Implement sip_h323_gateway.py (bridge logic)
7. **Integrate**: Call h323_gatekeeper.bridge_external_call() from Session 3
8. **Integrate**: Call IFAgentWebRTC.sendIFMessage() from Session 2
9. Write integration tests (most important!)
10. Document in SIP-ESCALATE-INTEGRATION.md
11. Commit to claude/realtime-workstream-4-sip

EXAMPLE INTEGRATION CODE:
```python
# src/communication/sip_proxy.py
from communication.h323_gatekeeper import H323Gatekeeper  # Session 3
from communication.webrtc_agent_mesh import IFAgentWebRTC  # Session 2

class SIPEscalateProxy:
    def __init__(self):
        self.h323_gk = H323Gatekeeper()  # Session 3's API
        self.webrtc_agent = IFAgentWebRTC()  # Session 2's API

    async def handle_escalate(self, message: IFMessage):
        # 1. IF.guard policy check
        approved = await if_guard.approve_external_call(
            expert_id=self.get_expert(message.hazards),
            hazard=message.hazards[0]
        )

        if not approved:
            return {"status": "rejected"}

        # 2. Send SIP INVITE
        sip_call = await self.sip_invite(expert_id)

        # 3. Bridge to H.323 council (Session 3)
        await self.h323_gk.bridge_external_call(
            sip_call_id=sip_call.id,
            council_call_id=message.conversation_id
        )

        # 4. Share evidence via WebRTC (Session 2)
        for evidence in message.payload.get('evidence_files', []):
            await self.webrtc_agent.sendIFMessage({
                'performative': 'inform',
                'payload': evidence
            })

        return {"status": "connected"}
```

BEGIN! (after Sessions 2 & 3 complete)
```

---

## Dependency Checklist (Before You Start)

- ⏳ **Session 2 (WebRTC):** Check if branch `claude/realtime-workstream-2-webrtc` exists
- ⏳ **Session 3 (H.323):** Check if branch `claude/realtime-workstream-3-h323` exists
- ⏳ **Interface Contracts:** Check if `docs/INTERFACES/workstream-{2,3}-*-contract.yaml` exist

**If any are missing, WAIT and notify the user!**

---

## Kamailio Configuration Snippet

```
# config/kamailio.cfg
# Custom header parsing for IF.witness
if (is_method("INVITE")) {
    # Extract IF headers
    $var(trace_id) = $hdr(X-IF-Trace-ID);
    $var(hazard) = $hdr(X-IF-Hazard);
    $var(signature) = $hdr(X-IF-Signature);

    # Call Python hook for policy check
    if (!python_exec("sip_proxy.check_policy")) {
        sl_send_reply("403", "IF.guard policy rejected");
        exit;
    }

    # Route to H.323 gateway
    route(H323_BRIDGE);
}
```

---

**Session Start:** [Copy-paste block above AFTER Sessions 2 & 3 complete]
**Session Complete:** Push to `claude/realtime-workstream-4-sip` + integration tests passing
