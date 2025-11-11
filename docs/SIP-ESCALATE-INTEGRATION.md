# SIP ESCALATE Integration - Comprehensive Tutorial

**Status:** Session 4 Implementation Complete (SIP Worker Ready and Waiting)

## Table of Contents

1. [Introduction](#introduction)
2. [Philosophy Grounding](#philosophy-grounding)
3. [Architecture Overview](#architecture-overview)
4. [End-to-End ESCALATE Flow](#end-to-end-escalate-flow)
5. [Component Details](#component-details)
6. [Custom SIP Headers](#custom-sip-headers)
7. [Integration Points](#integration-points)
8. [Example Usage](#example-usage)
9. [Testing](#testing)
10. [Production Deployment](#production-deployment)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is IF.ESCALATE?

**IF.ESCALATE** is InfraFabric's external expert escalation system—a sophisticated SIP-based mechanism for bringing trusted external experts into Guardian council deliberations during critical decision-making moments.

**Key Scenarios:**
- **Safety Review**: When a hazardous decision emerges, automatically escalate to safety experts
- **Ethics Challenge**: When bias is detected, bring in ethics experts for external validation
- **Security Audit**: When privacy concerns arise, engage security specialists for real-time review
- **Alignment Verification**: When alignment drift is suspected, consult external alignment experts

### Why External Expert Calls?

Traditional AI safety approaches rely exclusively on internal checks. **IF.ESCALATE inverts this assumption:**

> **"Wisdom requires dialogue with others, not introspection alone."**

**Benefits of external expert escalation:**
1. **Prevents Groupthink**: Internal systems can develop blind spots. External experts provide fresh perspectives.
2. **Validates Critical Decisions**: High-stakes decisions benefit from independent expert review.
3. **Observable Audit Trail**: Every escalation, approval, and decision is logged and auditable.
4. **Distributed Trust**: Rather than concentrating decision-making authority, distribute expertise across trusted partners.

---

## Philosophy Grounding

### 1. Wu Lun (五倫) - 朋友 (Friends)

The ancient Chinese concept of **Wu Lun** (Five Relationships) includes **朋友 (Friends)**, which emphasizes:
- **Equality**: Friends are peers, not hierarchical relationships
- **Mutual Respect**: Peers listen to each other's perspectives
- **Voluntary Association**: Friends choose to collaborate

**In IF.ESCALATE Context:**
- External experts are invited as **peer advisors**, not subordinates
- Guardian council explicitly seeks their counsel
- Both parties bring equal intellectual authority to the discussion

*Implementation*: `SIPEscalateProxy.get_expert_for_hazard()` matches hazard types to appropriate expert specializations—not random assignment, but careful peer selection.

### 2. Popper Falsifiability

Karl Popper's philosophy emphasizes that valid scientific knowledge requires:
- **Testable Hypotheses**: Theories must be falsifiable
- **Contrarian Views**: Alternative explanations prevent dogmatism
- **Systematic Refutation Attempts**: Science progresses by proving ideas wrong

**In IF.ESCALATE Context:**
- External experts provide **contrarian views** that could falsify internal assumptions
- If internal logic is sound, external experts will validate it
- If internal logic is flawed, external experts will expose it
- The presence of external experts makes internal reasoning more rigorous

*Implementation*: `IFGuardPolicy.approve_external_call()` verifies expert specialization matches hazard type—ensuring the expert can actually falsify (or validate) the internal claim.

### 3. IF.ground - Observable

**Principle**: All decisions affecting IF.ground must be **observable and auditable**.

For IF.ESCALATE, this means:
- **SIP Text-Based Signaling**: Unlike binary media protocols, SIP messages are human-readable
- **Complete Trace**: Every INVITE, ACK, BYE is logged
- **Header Visibility**: Custom IF headers expose reasoning (trace IDs, hazard types, signatures)

*Implementation*:
- `IFWitnessLogger` captures all SIP events to audit trail
- Custom headers `X-IF-Trace-ID`, `X-IF-Hazard`, `X-IF-Signature` encode decision context
- Kamailio logs all routing decisions with `xlog()` directives

### 4. IF.TTT - Traceable, Transparent, Trustworthy

**Three Pillars of IF.ESCALATE Trustworthiness:**

| Pillar | Implementation |
|--------|-----------------|
| **Traceable** | X-IF-Trace-ID correlates SIP, H.323, and WebRTC legs across all three sessions |
| **Transparent** | All state transitions and decisions logged; no hidden communication |
| **Trustworthy** | Ed25519 signatures validate expert identity; SRTP/H.235 encryption protects media |

---

## Architecture Overview

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        External Expert Domain                        │
│  ┌──────────────┐                                                   │
│  │ Expert Alice │  (SIP URI: expert-safety@external.advisor)        │
│  │ (Safety)     │                                                   │
│  └──────┬───────┘                                                   │
└─────────┼──────────────────────────────────────────────────────────┘
          │
          │ SIP INVITE (with X-IF-* headers)
          │ ● X-IF-Trace-ID: Correlation ID
          │ ● X-IF-Hazard: "safety"
          │ ● X-IF-Signature: Ed25519(sha256(msg))
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      InfraFabric Swarm                              │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Kamailio SIP Proxy (Port 5060)                              │   │
│  │ ├─ Route[IF_ESCALATE_INVITE]: Policy routing               │   │
│  │ ├─ Python Hook: sip_proxy.py (IF.guard + IF.witness)      │   │
│  │ └─ Custom Headers: Parse X-IF-* headers                    │   │
│  └──────────┬────────────────────────────────────────────────┘   │
│             │                                                      │
│  ┌──────────▼────────────────────────────────────────────────┐   │
│  │ SIPEscalateProxy (src/communication/sip_proxy.py)        │   │
│  │ ├─ parse_if_headers(): Extract custom headers             │   │
│  │ ├─ handle_escalate(): Main orchestration flow             │   │
│  │ ├─ send_sip_invite(): Route to expert                     │   │
│  │ ├─ get_expert_for_hazard(): Select appropriate expert     │   │
│  │ └─ terminate_call(): Cleanup SIP leg                      │   │
│  └──────────┬────────────────────────────────────────────────┘   │
│             │                                                      │
│  ┌──────────▼────────────────────────────────────────────────┐   │
│  │ IF.guard Policy Gate                                      │   │
│  │ ├─ approved_experts: Registry of trusted experts          │   │
│  │ ├─ approve_external_call(): Policy decision               │   │
│  │ └─ Signature verification (Ed25519)                       │   │
│  └──────────┬────────────────────────────────────────────────┘   │
│             │ APPROVED                                             │
│             ▼                                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ SIP-H.323 Gateway Bridge (Session 4 + Session 3)         │   │
│  │ ├─ SIPtoH323Bridge: Orchestrate bridge creation          │   │
│  │ ├─ MediaTranscoder: RTP ↔ H.323 audio                    │   │
│  │ ├─ BridgedCall: State tracking (both legs)               │   │
│  │ └─ Media encryption: SRTP ↔ H.235                        │   │
│  └──────────┬────────────────────────────────────────────────┘   │
│             │                                                      │
│  ┌──────────▼────────────────────────────────────────────────┐   │
│  │ Session 3 (H.323) - Guardian Council MCU                  │   │
│  │ └─ H323Gatekeeper.bridge_external_call()                  │   │
│  └──────────┬────────────────────────────────────────────────┘   │
│             │                                                      │
│  ┌──────────▼────────────────────────────────────────────────┐   │
│  │ Guardian Council (Multiple H.323 Endpoints)               │   │
│  │ ├─ guardian-alice@h323.infrafabric.internal               │   │
│  │ ├─ guardian-bob@h323.infrafabric.internal                 │   │
│  │ └─ guardian-carol@h323.infrafabric.internal               │   │
│  └──────────┬────────────────────────────────────────────────┘   │
│             │                                                      │
│  ┌──────────▼────────────────────────────────────────────────┐   │
│  │ WebRTC Agent Mesh (Session 2)                             │   │
│  │ ├─ Evidence DataChannel to expert                         │   │
│  │ ├─ Real-time document sharing                             │   │
│  │ └─ Trace correlation (trace_id in all packets)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│             │                                                      │
│  ┌──────────▼────────────────────────────────────────────────┐   │
│  │ IF.witness Audit Trail                                    │   │
│  │ ├─ sip_witness.log: Complete SIP event history            │   │
│  │ ├─ Bridge events: Creation, state changes, termination    │   │
│  │ ├─ Media stats: Packets, bytes, codec info                │   │
│  │ └─ Policy decisions: Approved/rejected + reason            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Integration Points

| Component | Role | File |
|-----------|------|------|
| **Kamailio** | SIP signaling server | `config/kamailio.cfg` |
| **SIPEscalateProxy** | Main orchestration logic | `src/communication/sip_proxy.py` |
| **SIPtoH323Bridge** | Protocol bridge (SIP ↔ H.323) | `src/communication/sip_h323_gateway.py` |
| **H323Gatekeeper** | Guardian council integration | `src/communication/h323_gatekeeper.py` |
| **IFAgentWebRTC** | Evidence sharing mesh | `src/communication/webrtc_agent_mesh.py` |
| **IFGuardPolicy** | Policy approval gate | `src/communication/sip_proxy.py` lines 62-143 |
| **IFWitnessLogger** | Audit trail logging | `src/communication/sip_proxy.py` lines 146-185 |

---

## End-to-End ESCALATE Flow

### Complete Call Lifecycle

```
Timeline: A hazardous decision is detected, requiring expert escalation

T=0.00s    IF.connect detects hazard
           └─→ Creates IFMessage(performative='escalate', hazards=['safety'])

T=0.01s    SIPEscalateProxy.handle_escalate() called
           └─→ Parse hazard: 'safety'
           └─→ Select expert: expert-safety@external.advisor
           └─→ Trace ID: sha256(message_id)[:16]

T=0.02s    IF.guard policy check: approve_external_call()
           ├─ Verify expert in registry ✓
           ├─ Verify specialization matches hazard ✓
           ├─ Verify Ed25519 signature ✓
           └─→ APPROVED

T=0.03s    Send SIP INVITE to expert
           ├─ Custom headers:
           │  ├─ X-IF-Trace-ID: abc123def456
           │  ├─ X-IF-Hazard: safety
           │  └─ X-IF-Signature: ed25519_signature
           └─→ SIP call_id: sip-call-7a8b9c0d1e2f3g4h

T=0.10s    External expert's SIP phone rings (100 Trying)
           └─→ [IF.witness] Log: RINGING event

T=0.50s    Expert answers (180 Ringing)
           └─→ [IF.witness] Log: ALERTING event

T=1.00s    Expert accepts (200 OK - SIP leg connected)
           └─→ SIP media (RTP) begins: expert → Kamailio
           └─→ [IF.witness] Log: CONNECTED event

T=1.01s    ACK from Kamailio to expert
           └─→ SIP dialog established

T=1.02s    SIPtoH323Bridge.create_bridge() called
           ├─ Setup SIP leg: RTP port 10000, codec G.711-ulaw, SRTP
           ├─ Setup H.323 leg: H.323 audio channel, codec G.711, H.235
           ├─ Initialize MediaTranscoder: bidirectional RTP ↔ H.323
           └─→ bridge_id: bridge-7a8b9c0d1e2f3g4h

T=1.03s    H323Gatekeeper.bridge_external_call()
           ├─ Register external expert as MCU participant
           ├─ mcu_participant_id: mcu-participant-0
           └─→ Guardian council H.323 session now includes expert

T=1.05s    Media transcoding begins
           ├─ Expert's RTP packets → Decode G.711
           ├─ Transcode to H.323 audio channel
           ├─ Guardian council's H.323 audio → Decode
           ├─ Transcode to RTP → Send to expert
           └─→ Expert's voice now audible in Guardian council

T=1.10s    WebRTC evidence sharing
           ├─ IFAgentWebRTC.shareEvidence()
           ├─ Send evidence files to expert via DataChannel
           ├─ All evidence tagged with trace_id
           └─→ Expert receives context documents for real-time review

T=1.11s    IF.witness logs bridge establishment
           ├─ source: SIPtoH323Bridge
           ├─ event_type: BRIDGE_ESTABLISHED
           ├─ details:
           │  ├─ sip_call_id: sip-call-7a8b9c0d1e2f3g4h
           │  ├─ h323_call_id: council-abc123def456
           │  ├─ expert_id: expert-safety@external.advisor
           │  ├─ h323_participant_id: mcu-participant-0
           │  └─ trace_id: abc123def456
           └─→ [IF.witness] Log: BRIDGE_ESTABLISHED event

T=1.12s to   Guardian Council Deliberation + Expert Input
T=5.00s      ├─ Expert can hear all council discussion (H.323 audio)
             ├─ Expert can speak (RTP → H.323 transcoding)
             ├─ Expert reviews evidence (WebRTC DataChannel)
             ├─ Media statistics updated (packets/bytes)
             └─→ Multiple IF.witness STATE_CHANGE events logged

T=5.01s    Decision reaches consensus
           ├─ Expert provides recommendation: "Safety concern addressed"
           ├─ Guardian council deliberates final decision
           └─→ Decision made with external expert input

T=5.02s    Expert ends call (BYE from expert)
           ├─ SIP leg: sip-call-7a8b9c0d1e2f3g4h receives BYE
           ├─ H.323 leg: mcu-participant-0 removed from council
           ├─ MediaTranscoder: Teardown bidirectional audio
           ├─ Duration: 4.01 seconds
           └─→ [IF.witness] Log: TERMINATED event

T=5.03s    IF.witness logs call termination
           ├─ event_type: BRIDGE_TERMINATED
           ├─ details:
           │  ├─ duration_seconds: 4.01
           │  ├─ media_stats: {sip: {...}, h323: {...}}
           │  ├─ expert_id: expert-safety@external.advisor
           │  └─ trace_id: abc123def456
           └─→ Complete audit trail created
```

---

## Component Details

### 1. SIPEscalateProxy

**File**: `src/communication/sip_proxy.py` (lines 188-420)

**Responsibilities**:
- Parse custom IF headers from SIP messages
- Orchestrate end-to-end ESCALATE flow
- Coordinate with IF.guard, H.323 gateway, and WebRTC mesh

**Key Methods**:

#### `handle_escalate(message: IFMessage) → Dict[str, Any]`

Main entry point for escalation requests.

```python
# Example call
proxy = SIPEscalateProxy()
result = await proxy.handle_escalate(
    message=IFMessage(
        id="msg-001",
        timestamp="2025-11-11T10:30:00Z",
        level=8,  # High severity
        source="guardian-alice",
        destination="external-expert",
        trace_id="abc123def456",
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": ["safety"],
            "signature": "ed25519_signature...",
            "evidence_files": [
                "/var/evidence/decision-001.json",
                "/var/evidence/log-001.txt"
            ],
            "conversation_id": "council-001"
        }
    )
)

# Returns:
# {
#     "status": "connected",
#     "call_id": "sip-call-7a8b9c0d1e2f3g4h",
#     "expert_id": "expert-safety@external.advisor",
#     "h323_participant": "mcu-participant-0"
# }
```

**Flow Inside `handle_escalate()`**:

1. **Parse hazards** from `message.payload["hazards"]`
2. **Select expert** via `get_expert_for_hazard(hazard)`
3. **Policy check** via `if_guard.approve_external_call()`
4. **Send SIP INVITE** via `send_sip_invite()`
5. **Bridge to H.323** via `h323_gk.bridge_external_call()`
6. **Share evidence** via `webrtc_agent.shareEvidence()`
7. **Log all events** via `if_witness.log_sip_event()`

#### `parse_if_headers(sip_message: Dict) → Dict`

Extracts custom headers from SIP INVITE.

```python
if_headers = proxy.parse_if_headers({
    "headers": {
        "X-IF-Trace-ID": "abc123def456",
        "X-IF-Hazard": "safety",
        "X-IF-Signature": "ed25519_sig_..."
    }
})

# Returns:
# {
#     "trace_id": "abc123def456",
#     "hazard": "safety",
#     "signature": "ed25519_sig_..."
# }
```

#### `get_expert_for_hazard(hazard: str) → str`

Maps hazard types to expert SIP URIs.

```python
expert_id = proxy.get_expert_for_hazard("safety")
# Returns: "expert-safety@external.advisor"

expert_id = proxy.get_expert_for_hazard("ethics")
# Returns: "expert-ethics@external.advisor"

expert_id = proxy.get_expert_for_hazard("security")
# Returns: "expert-security@external.advisor"
```

**Hazard → Expert Mapping**:

| Hazard | Expert | Specialization |
|--------|--------|-----------------|
| safety | expert-safety@external.advisor | ["safety", "alignment"] |
| alignment | expert-safety@external.advisor | ["safety", "alignment"] |
| ethics | expert-ethics@external.advisor | ["ethics", "bias"] |
| bias | expert-ethics@external.advisor | ["ethics", "bias"] |
| security | expert-security@external.advisor | ["security", "privacy"] |
| privacy | expert-security@external.advisor | ["security", "privacy"] |

### 2. IF.guard Policy Gate

**File**: `src/communication/sip_proxy.py` (lines 62-143)

**Responsibilities**:
- Maintain registry of approved external experts
- Verify expert qualifications match hazard type
- Validate Ed25519 signatures (optional)
- Make final approval/rejection decision

**Key Methods**:

#### `approve_external_call(expert_id: str, hazard: str, signature: Optional[str]) → Dict`

Decision gate for external calls.

```python
policy = IFGuardPolicy()

# Approved expert, matching specialization
result = await policy.approve_external_call(
    expert_id="expert-safety@external.advisor",
    hazard="safety",
    signature="ed25519_signature..."
)
# Returns:
# {
#     "approved": True,
#     "reason": "Expert approved and specialization matches hazard",
#     "expert_info": {
#         "name": "Safety Expert",
#         "specialization": ["safety", "alignment"],
#         "verified": True
#     }
# }

# Rejected: Expert not in registry
result = await policy.approve_external_call(
    expert_id="malicious@attacker.com",
    hazard="safety"
)
# Returns:
# {
#     "approved": False,
#     "reason": "Expert not in approved registry",
#     "expert_id": "malicious@attacker.com"
# }

# Rejected: Specialization mismatch
result = await policy.approve_external_call(
    expert_id="expert-safety@external.advisor",
    hazard="ethics"  # Safety expert not qualified for ethics
)
# Returns:
# {
#     "approved": False,
#     "reason": "Expert specialization ['safety', 'alignment'] does not match hazard ethics",
#     "expert_id": "expert-safety@external.advisor"
# }
```

**Adding New Experts**:

Modify `approved_experts` registry in `IFGuardPolicy.__init__()`:

```python
self.approved_experts = {
    "expert-safety@external.advisor": {
        "name": "Safety Expert",
        "specialization": ["safety", "alignment"],
        "verified": True
    },
    "expert-new@external.advisor": {  # New expert
        "name": "New Expert Name",
        "specialization": ["new_hazard_type"],
        "verified": True
    }
}
```

### 3. IF.witness Audit Logger

**File**: `src/communication/sip_proxy.py` (lines 146-185)

**Responsibilities**:
- Log all SIP events to persistent audit trail
- Track call lifecycle (INVITE → CONNECTED → TERMINATED)
- Store event details in IF.witness format

**Key Methods**:

#### `log_sip_event(event_type: str, sip_method: str, trace_id: str, details: Dict) → None`

Records SIP event to audit trail.

```python
witness = IFWitnessLogger()

# Log incoming INVITE
await witness.log_sip_event(
    event_type="INVITE",
    sip_method="INVITE",
    trace_id="abc123def456",
    details={
        "from_uri": "expert-safety@external.advisor",
        "to_uri": "guardian-council@infrafabric.internal",
        "call_id": "sip-call-7a8b9c0d1e2f3g4h",
        "headers": {
            "X-IF-Trace-ID": "abc123def456",
            "X-IF-Hazard": "safety"
        }
    }
)

# Log call connected
await witness.log_sip_event(
    event_type="CONNECTED",
    sip_method="200-OK",
    trace_id="abc123def456",
    details={
        "call_id": "sip-call-7a8b9c0d1e2f3g4h",
        "expert_id": "expert-safety@external.advisor",
        "h323_participant_id": "mcu-participant-0",
        "evidence_count": 2
    }
)
```

**Logged Events**:

| Event Type | Trigger | Use Case |
|------------|---------|----------|
| INVITE | SIP INVITE received | Track call initiation |
| RINGING | 180 Ringing response | Track expert alerting |
| CONNECTED | 200 OK response | Track successful connection |
| STATE_CHANGE | Bridge state transition | Track media flow |
| BRIDGE_ESTABLISHED | SIP-H.323 bridge created | Track bridge lifecycle |
| BRIDGE_TERMINATED | Bridge torn down | Track call cleanup |
| REJECTED | IF.guard rejects call | Track policy decisions |
| TERMINATED | BYE received/sent | Track call completion |
| ERROR | Exception during call | Track failures |

**Audit Trail Format**:

```json
{
    "timestamp": "2025-11-11T10:30:05.123Z",
    "event_type": "BRIDGE_ESTABLISHED",
    "sip_method": "INVITE",
    "trace_id": "abc123def456",
    "details": {
        "call_id": "sip-call-7a8b9c0d1e2f3g4h",
        "expert_id": "expert-safety@external.advisor",
        "h323_participant_id": "mcu-participant-0",
        "sip_endpoint": "sip:expert-safety@external.advisor",
        "h323_endpoint": "h323://guardian-council-mcu/external",
        "evidence_count": 2
    },
    "source": "IF.sip_proxy"
}
```

### 4. SIP-H.323 Gateway Bridge

**File**: `src/communication/sip_h323_gateway.py`

**Responsibilities**:
- Create bidirectional bridge between SIP expert and H.323 council
- Manage both call legs (SIP + H.323)
- Transcode audio between protocols
- Synchronize call state across protocol boundaries

**Key Classes**:

#### `SIPtoH323Bridge`

Main gateway bridge orchestrator.

```python
bridge = SIPtoH323Bridge(h323_gatekeeper=gk)

# Create new bridge for external expert
result = await bridge.create_bridge(
    sip_call_id="sip-call-7a8b9c0d1e2f3g4h",
    sip_from="expert-safety@external.advisor",
    council_call_id="council-abc123def456",
    trace_id="abc123def456",
    expert_id="expert-safety@external.advisor",
    hazard_type="safety"
)

# Returns:
# {
#     "status": "success",
#     "bridge_id": "bridge-7a8b9c0d1e2f3g4h",
#     "h323_participant_id": "mcu-participant-0",
#     "sip_endpoint": "sip:expert-safety@external.advisor",
#     "h323_endpoint": "h323://guardian-council-mcu/external"
# }
```

**Bridge State Tracking**:

```python
# Get status of specific bridge
status = bridge.get_bridge_status("bridge-7a8b9c0d1e2f3g4h")
# Returns:
# {
#     "bridge_id": "bridge-7a8b9c0d1e2f3g4h",
#     "trace_id": "abc123def456",
#     "expert_id": "expert-safety@external.advisor",
#     "hazard_type": "safety",
#     "sip_state": "connected",
#     "h323_state": "connected",
#     "bridge_state": "connected",
#     "duration_seconds": 4.01,
#     "h323_participant_id": "mcu-participant-0"
# }

# Get all active bridges
all_bridges = bridge.get_all_bridges()
# Returns: List[Dict] of all active bridge statuses
```

#### `BridgedCall` Data Structure

Complete call state for both SIP and H.323 legs:

```python
@dataclass
class BridgedCall:
    bridge_id: str
    trace_id: str

    # SIP leg (external expert)
    sip_call_id: str
    sip_from: str  # e.g., "expert-safety@external.advisor"
    sip_to: str    # e.g., "guardian-council@infrafabric.internal"
    sip_state: CallState  # idle, setup, ringing, connected, disconnecting, disconnected
    sip_media: Optional[MediaStream]  # RTP stream descriptor

    # H.323 leg (Guardian council)
    h323_call_id: str
    h323_endpoint: str
    h323_mcu_participant_id: Optional[str]  # e.g., "mcu-participant-0"
    h323_state: CallState
    h323_media: Optional[MediaStream]  # H.323 audio channel descriptor

    # Bridge state
    bridge_state: CallState
    start_time: datetime
    connect_time: Optional[datetime]
    end_time: Optional[datetime]

    # Metadata
    expert_id: str
    hazard_type: str
    evidence_files: List[str]
```

#### `MediaTranscoder`

Handles audio transcoding between SIP RTP and H.323 channels.

```python
transcoder = MediaTranscoder()

# Setup bidirectional audio
success = await transcoder.setup_bidirectional_audio(
    bridge_id="bridge-7a8b9c0d1e2f3g4h",
    sip_stream=MediaStream(
        stream_id="sip-expert-001",
        codec=MediaCodec.G711_ULAW,
        sample_rate=8000,
        rtp_port=10000,
        encryption="SRTP"
    ),
    h323_stream=MediaStream(
        stream_id="h323-council-001",
        codec=MediaCodec.G711_ULAW,
        sample_rate=8000,
        h323_channel="h323-audio-channel-0",
        encryption="H.235"
    )
)

# Transcode SIP → H.323
h323_frame = await transcoder.transcode_sip_to_h323(
    bridge_id="bridge-7a8b9c0d1e2f3g4h",
    rtp_packet=b"..."  # Raw RTP packet from expert
)

# Transcode H.323 → SIP
rtp_packet = await transcoder.transcode_h323_to_sip(
    bridge_id="bridge-7a8b9c0d1e2f3g4h",
    h323_frame=b"..."  # Raw H.323 audio frame
)

# Teardown bridge
await transcoder.teardown_audio("bridge-7a8b9c0d1e2f3g4h")
```

### 5. Kamailio SIP Configuration

**File**: `config/kamailio.cfg`

**Key Routing Blocks**:

#### `route[IF_ESCALATE_INVITE]` (lines 104-139)

Handles incoming INVITE for external expert escalation.

```
# Extract custom IF headers
$var(trace_id) = $hdr(X-IF-Trace-ID)
$var(hazard) = $hdr(X-IF-Hazard)
$var(signature) = $hdr(X-IF-Signature)

# Validate required headers
if (!$var(trace_id) || !$var(hazard)) {
    sl_send_reply("400", "Bad Request - Missing IF headers")
    exit
}

# Call Python hook for policy check
if (!python_exec("check_policy")) {
    sl_send_reply("403", "Forbidden - IF.guard policy rejected")
    exit
}

# Route to H.323 gateway bridge
route(H323_BRIDGE)
```

#### `route[EXTERNAL_EXPERT]` (lines 141-154)

Routes INVITE to external expert (when destination is expert SIP URI).

```
record_route_preset("0.0.0.0:5060", "trace=$var(trace_id)")
xlog("L_INFO", "[IF.witness] INVITE to external expert $ru\n")
t_relay()  # Forward to external SIP infrastructure
```

#### `route[H323_BRIDGE]` (lines 156-173)

Routes INVITE to H.323 gateway for Guardian council bridging.

```
# Rewrite URI to H.323 gateway endpoint
$ru = "sip:h323-gateway@127.0.0.1:5062"

# Add custom headers for H.323 gateway
append_hf("X-IF-Source: SIP-External-Expert\r\n")
append_hf("X-IF-Bridge-Mode: SIP-to-H323\r\n")

# IF.witness logging
xlog("L_INFO", "[IF.witness] Bridging to H.323: trace=$var(trace_id)\n")

# Forward to H.323 gateway
t_relay()
```

#### `onreply_route` (lines 215-227)

Handles all SIP responses (status codes).

```
# Log all responses
xlog("L_INFO", "[IF.witness] SIP response $rs $rr (Call-ID: $ci)\n")

# Handle 1xx/2xx (success)
if (status =~ "^[12][0-9][0-9]$") {
    xlog("L_INFO", "[IF.ESCALATE] Success response: $rs $rr\n")
}

# Handle 4xx/5xx/6xx (errors)
else if (status =~ "^[4-6][0-9][0-9]$") {
    xlog("L_WARN", "[IF.ESCALATE] Error response: $rs $rr\n")
}
```

---

## Custom SIP Headers

### Header: X-IF-Trace-ID

**Purpose**: Correlation ID linking SIP, H.323, and WebRTC legs

**Format**: SHA256 hash (first 16 chars hex)

**Example**: `X-IF-Trace-ID: abc123def456789f`

**Usage**:
```
# In SIPEscalateProxy
trace_id = message.trace_id or message.id
# Used in all downstream operations to correlate logs
```

**In Kamailio**:
```kamailio
$var(trace_id) = $hdr(X-IF-Trace-ID)
xlog("L_INFO", "[IF.witness] Trace: $var(trace_id)\n")
record_route_preset("0.0.0.0:5060", "trace=$var(trace_id)")
```

### Header: X-IF-Hazard

**Purpose**: Identifies hazard type requiring escalation

**Format**: Text string (safety, ethics, security, etc.)

**Example**: `X-IF-Hazard: safety`

**Valid Values**:
| Value | Maps to Expert | Specialization |
|-------|----------------|-----------------|
| safety | expert-safety@external.advisor | Safety & Alignment |
| alignment | expert-safety@external.advisor | Safety & Alignment |
| ethics | expert-ethics@external.advisor | Ethics & Bias |
| bias | expert-ethics@external.advisor | Ethics & Bias |
| security | expert-security@external.advisor | Security & Privacy |
| privacy | expert-security@external.advisor | Security & Privacy |

**Usage**:
```python
# In SIPEscalateProxy.handle_escalate()
hazard = message.payload.get("hazards", [])[0]
expert_id = self.get_expert_for_hazard(hazard)
```

**In Kamailio**:
```kamailio
$var(hazard) = $hdr(X-IF-Hazard)
if (!$var(hazard)) {
    sl_send_reply("400", "Bad Request - Missing X-IF-Hazard")
    exit
}
```

### Header: X-IF-Signature

**Purpose**: Ed25519 digital signature for authenticity verification

**Format**: Base64-encoded Ed25519 signature

**Example**: `X-IF-Signature: sig_base64_encoded_...`

**Signature Creation**:
```python
import hashlib
from nacl import signing

# Message to sign: JSON serialization of IFMessage
message_json = json.dumps(message.to_dict(), sort_keys=True)

# Sign with Ed25519 private key
signing_key = signing.SigningKey(private_key_bytes)
signature = signing_key.sign(message_json.encode()).signature
signature_b64 = base64.b64encode(signature).decode()

# Add to SIP INVITE headers
```

**Signature Verification** (in IF.guard):
```python
import nacl.signing

# Extract signature from header
signature_b64 = message.payload.get("signature")
if not signature_b64:
    return {"approved": False, "reason": "No signature provided"}

# Verify with expert's public key
try:
    public_key = nacl.signing.VerifyKey(expert_public_key_bytes)
    public_key.verify(message_json.encode(), signature_bytes)
    # Signature valid
except nacl.exceptions.BadSignatureError:
    return {"approved": False, "reason": "Invalid signature"}
```

### Header: X-IF-Source (Kamailio-added)

**Purpose**: Identifies message source for bridging

**Format**: Text string

**Example**: `X-IF-Source: SIP-External-Expert`

**Added by Kamailio** in `route[H323_BRIDGE]`:
```kamailio
append_hf("X-IF-Source: SIP-External-Expert\r\n")
```

### Header: X-IF-Bridge-Mode (Kamailio-added)

**Purpose**: Indicates bridging direction

**Format**: Text string

**Example**: `X-IF-Bridge-Mode: SIP-to-H323`

**Added by Kamailio** in `route[H323_BRIDGE]`:
```kamailio
append_hf("X-IF-Bridge-Mode: SIP-to-H323\r\n")
```

---

## Integration Points

### 1. Session 2 (WebRTC Agent Mesh) Integration

**File**: `src/communication/webrtc_agent_mesh.py`

**Integration Point**: Evidence sharing during expert call

```python
# In SIPEscalateProxy.handle_escalate() (line 295-300)
evidence_files = message.payload.get("evidence_files", [])
if evidence_files:
    await self.webrtc_agent.shareEvidence(
        evidence_files=evidence_files,
        peer_ids=[expert_id, council_call_id]
    )
```

**Flow**:
1. After SIP call connected to expert
2. After H.323 bridge established to council
3. Share evidence files via WebRTC DataChannel to both expert and council
4. Expert reviews evidence in real-time during conversation

**Contract**:
```python
class IFAgentWebRTC:
    async def shareEvidence(
        self,
        evidence_files: list,
        peer_ids: list
    ) -> Dict[str, Any]:
        """
        Args:
            evidence_files: List of file paths/URLs
            peer_ids: Peer agent IDs to receive evidence

        Returns:
            {"shared": count, "peers": [...], "status": "completed"}
        """
```

### 2. Session 3 (H.323 Guardian Council) Integration

**File**: `src/communication/h323_gatekeeper.py`

**Integration Point**: Adding expert as council participant

```python
# In SIPtoH323Bridge.create_bridge() (line 346-350)
h323_result = await self.h323_gk.bridge_external_call(
    sip_call_id=sip_call_id,
    council_call_id=council_call_id,
    external_expert_id=expert_id
)
```

**Contract**:
```python
class H323Gatekeeper:
    async def bridge_external_call(
        self,
        sip_call_id: str,
        council_call_id: str,
        external_expert_id: str = None
    ) -> Dict[str, Any]:
        """
        Bridge external SIP call to H.323 Guardian council MCU

        Returns:
            {
                "status": "bridged",
                "h323_endpoint": "h323://...",
                "mcu_participant_id": "mcu-participant-0"
            }
        """
```

**Flow**:
1. Register external expert as MCU participant
2. Add expert to ongoing Guardian council conference
3. Expert's audio routed through H.323 MCU
4. Expert listed as active participant in council recording

### 3. IF.guard Policy Integration

**Used by**: `SIPEscalateProxy.handle_escalate()`

```python
# Before routing to expert, check policy
approval = await self.if_guard.approve_external_call(
    expert_id=expert_id,
    hazard=hazard,
    signature=message.payload.get("signature")
)

if not approval["approved"]:
    # Reject call
    return {"status": "rejected", "reason": approval["reason"]}
```

**Policy Decision Points**:
1. Is expert in approved registry?
2. Does expert specialization match hazard?
3. Is Ed25519 signature valid (if provided)?

### 4. IF.witness Audit Integration

**Used by**: All components

```python
# SIPEscalateProxy
await self.if_witness.log_sip_event(
    event_type="CONNECTED",
    sip_method="INVITE",
    trace_id=trace_id,
    details={...}
)

# SIPtoH323Bridge
await self._log_witness_event(
    bridge_id=bridge_id,
    event_type="BRIDGE_ESTABLISHED",
    details={...}
)
```

**Logged Events Include**:
- All SIP method invocations (INVITE, ACK, BYE, etc.)
- Bridge lifecycle (creation, state changes, termination)
- Media statistics (packets, bytes, codecs)
- Policy decisions (approved/rejected with reason)

---

## Example Usage

### Example 1: Trigger ESCALATE for Safety Hazard

```python
import asyncio
from communication.sip_proxy import SIPEscalateProxy, IFMessage

async def escalate_safety_concern():
    """Trigger expert escalation for safety hazard"""

    proxy = SIPEscalateProxy()

    # Create escalation message
    message = IFMessage(
        id="msg-001",
        timestamp="2025-11-11T10:30:00Z",
        level=8,  # High severity
        source="guardian-alice",
        destination="external-expert",
        trace_id="abc123def456",
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": ["safety"],
            "signature": "ed25519_signature_...",
            "evidence_files": [
                "/var/evidence/decision-001.json",
                "/var/evidence/reasoning-001.txt"
            ],
            "conversation_id": "council-001"
        }
    )

    # Trigger escalation
    result = await proxy.handle_escalate(message)

    # Result:
    # {
    #     "status": "connected",
    #     "call_id": "sip-call-7a8b9c0d1e2f3g4h",
    #     "expert_id": "expert-safety@external.advisor",
    #     "h323_participant": "mcu-participant-0"
    # }

    if result["status"] == "connected":
        print(f"Expert call connected: {result['expert_id']}")
        print(f"H.323 participant: {result['h323_participant']}")
    else:
        print(f"Escalation rejected: {result.get('reason')}")

    return result

# Run escalation
result = asyncio.run(escalate_safety_concern())
```

### Example 2: Terminate Expert Call

```python
async def end_expert_call(call_id: str):
    """Terminate expert call after deliberation"""

    proxy = SIPEscalateProxy()

    # Terminate call
    result = await proxy.terminate_call(call_id)

    # Result:
    # {
    #     "status": "terminated",
    #     "call_id": "sip-call-7a8b9c0d1e2f3g4h"
    # }

    print(f"Call {call_id} terminated")
    return result

result = asyncio.run(end_expert_call("sip-call-7a8b9c0d1e2f3g4h"))
```

### Example 3: Check Bridge Status

```python
async def monitor_bridge(bridge_id: str):
    """Monitor active bridge status"""

    from communication.sip_h323_gateway import SIPtoH323Bridge

    bridge = SIPtoH323Bridge()

    # Get bridge status
    status = bridge.get_bridge_status(bridge_id)

    # Result:
    # {
    #     "bridge_id": "bridge-7a8b9c0d1e2f3g4h",
    #     "trace_id": "abc123def456",
    #     "expert_id": "expert-safety@external.advisor",
    #     "hazard_type": "safety",
    #     "sip_state": "connected",
    #     "h323_state": "connected",
    #     "bridge_state": "connected",
    #     "duration_seconds": 45.23,
    #     "h323_participant_id": "mcu-participant-0"
    # }

    print(f"Bridge {bridge_id} status:")
    print(f"  Expert: {status['expert_id']}")
    print(f"  Duration: {status['duration_seconds']} seconds")
    print(f"  Bridge state: {status['bridge_state']}")

    return status

status = asyncio.run(monitor_bridge("bridge-7a8b9c0d1e2f3g4h"))
```

### Example 4: Register New External Expert

```python
def register_new_expert(
    expert_id: str,
    name: str,
    specialization: list,
    verified: bool = True
):
    """Add new expert to IF.guard approval registry"""

    from communication.sip_proxy import IFGuardPolicy

    policy = IFGuardPolicy()

    # Add expert to registry
    policy.approved_experts[expert_id] = {
        "name": name,
        "specialization": specialization,
        "verified": verified
    }

    print(f"Registered expert: {expert_id}")
    print(f"  Name: {name}")
    print(f"  Specialization: {specialization}")

    # Verify registration
    approval = asyncio.run(policy.approve_external_call(
        expert_id=expert_id,
        hazard=specialization[0]
    ))

    if approval["approved"]:
        print(f"Expert {expert_id} approved for hazard {specialization[0]}")
    else:
        print(f"Expert registration failed: {approval['reason']}")

# Register new security expert
register_new_expert(
    expert_id="expert-crypto@external.advisor",
    name="Cryptography Specialist",
    specialization=["security"],
    verified=True
)
```

---

## Testing

### Unit Tests

Run tests for SIP proxy components:

```bash
# Test IF.guard policy decisions
pytest tests/test_sip_proxy.py::TestIFGuardPolicy -v

# Test SIPEscalateProxy escalation flow
pytest tests/test_sip_proxy.py::TestSIPEscalateProxy -v

# Test SIP-H.323 bridge creation
pytest tests/test_sip_h323_gateway.py::TestSIPtoH323Bridge -v

# Run all SIP tests
pytest tests/ -k "sip" -v
```

### Integration Tests

Test full end-to-end flow:

```bash
# Test complete escalation flow (SIP → H.323 → WebRTC)
pytest tests/test_escalate_integration.py -v

# Test with actual Kamailio routing
pytest tests/test_kamailio_integration.py -v

# Test error scenarios (rejected calls, timeout, etc.)
pytest tests/test_escalate_error_cases.py -v
```

### Manual Testing

1. **Start Kamailio**:
```bash
kamailio -f config/kamailio.cfg -D
```

2. **Simulate external expert SIP phone**:
```bash
# Use PJSUA or SIPp to create SIP endpoint
pjsua --id=sip:expert-safety@external.advisor --registrar=sip:127.0.0.1:5060
```

3. **Trigger escalation from Python**:
```python
import asyncio
from communication.sip_proxy import SIPEscalateProxy, IFMessage

async def test():
    proxy = SIPEscalateProxy()
    message = IFMessage(
        id="test-001",
        timestamp="2025-11-11T10:30:00Z",
        level=8,
        source="test-source",
        destination="test-dest",
        trace_id="test-trace-001",
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": ["safety"],
            "evidence_files": ["/tmp/evidence.txt"],
            "conversation_id": "test-council-001"
        }
    )
    result = await proxy.handle_escalate(message)
    print(result)

asyncio.run(test())
```

4. **Check Kamailio logs**:
```bash
# Tail Kamailio logs
tail -f /var/log/kamailio/kamailio.log

# Look for IF.witness events
grep "IF.witness" /var/log/kamailio/kamailio.log
grep "IF.guard" /var/log/kamailio/kamailio.log
grep "IF.ESCALATE" /var/log/kamailio/kamailio.log
```

5. **Verify audit trail**:
```bash
# Check IF.witness SIP audit log
tail -f /var/log/infrafabric/sip_witness.log

# Parse witness events
cat /var/log/infrafabric/sip_witness.log | jq '.event_type'
```

---

## Production Deployment

### Phase 1: Basic Deployment (Current)

**Current Status**: Kamailio proxy + Python policy hooks

**Components**:
- Kamailio SIP proxy (UDP 5060 + TCP 5060)
- Python integration (app_python3 module)
- IF.guard policy evaluation
- IF.witness logging to file
- H.323 bridge stub (ready for Session 3 integration)

**Deployment Steps**:

1. **Install Kamailio**:
```bash
apt-get install kamailio kamailio-modules kamailio-python3-modules
```

2. **Copy configuration**:
```bash
cp config/kamailio.cfg /etc/kamailio/kamailio.cfg
```

3. **Create log directory**:
```bash
mkdir -p /var/log/infrafabric
chown kamailio:kamailio /var/log/infrafabric
chmod 750 /var/log/infrafabric
```

4. **Start Kamailio**:
```bash
systemctl start kamailio
systemctl enable kamailio  # Enable on boot
```

5. **Verify status**:
```bash
systemctl status kamailio
kamailio -v  # Check version
```

### Phase 2: TLS Security (TODO)

**Changes Required**:

1. **Enable TLS in Kamailio**:
```kamailio
# Uncomment in config/kamailio.cfg:
listen=tls:0.0.0.0:5061
loadmodule "tls.so"

# Configure certificate paths
modparam("tls", "certificate", "/etc/kamailio/certs/cert.pem")
modparam("tls", "private_key", "/etc/kamailio/certs/key.pem")
```

2. **Add digest authentication**:
```kamailio
loadmodule "auth.so"
loadmodule "auth_db.so"

modparam("auth_db", "load", "uri:password")
```

3. **Add rate limiting**:
```kamailio
loadmodule "htable.so"
modparam("htable", "htable", "sip_calls=>size=10;expire=3600;")
```

### Phase 3: Monitoring & Metrics (TODO)

**Export Prometheus metrics**:

```bash
# Kamailio Prometheus exporter
# Enable in Kamailio config:
modparam("usrloc", "db_mode", 0)  # Enable in-memory stats
modparam("statistics", "stat_groups", "all")
```

**Metrics to track**:
- `sip_calls_total`: Total escalated calls
- `sip_call_duration_seconds`: Call duration histogram
- `sip_errors_total`: Failed calls by error code
- `sip_policy_decisions_total{result="approved|rejected"}`: Policy decisions
- `sip_bridge_duration_seconds`: Bridge lifetime
- `h323_participants_active`: Active H.323 connections
- `webrtc_evidence_shared_total`: Evidence files shared

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 External Expert Network                 │
│         expert-safety@external.advisor                  │
│         expert-ethics@external.advisor                  │
│         expert-security@external.advisor                │
└──────────────────────┬──────────────────────────────────┘
                       │ SIP (UDP/TCP 5060 or TLS 5061)
                       ▼
        ┌──────────────────────────────┐
        │   Kamailio SIP Proxy          │
        │   ├─ Protocol: UDP/TCP/TLS    │
        │   ├─ Port: 5060 (5061 TLS)    │
        │   ├─ Python hooks: IF.guard   │
        │   └─ Logging: IF.witness      │
        └──────────┬─────────────────────┘
                   │
      ┌────────────┴─────────────┐
      │                          │
      ▼                          ▼
┌──────────────────┐    ┌──────────────────┐
│  H.323 Gateway   │    │  WebRTC Agent    │
│  (Session 3)     │    │  Mesh (Session 2)│
│  ├─ MCU          │    │  ├─ Evidence     │
│  └─ Participants │    │  └─ DataChannel  │
└────────┬─────────┘    └──────┬───────────┘
         │                      │
         ▼                      ▼
     ┌────────────────────────────┐
     │  Guardian Council MCU       │
     │  ├─ guardian-alice          │
     │  ├─ guardian-bob            │
     │  ├─ guardian-carol          │
     │  └─ [external-expert]       │
     └────────────────────────────┘
```

### Health Checks

```bash
# Check Kamailio SIP processing
kamctl fifo get_statistics sip_requests

# Check active calls
kamctl fifo get_statistics dialog

# Monitor Python integration
grep "kamailio_init" /var/log/kamailio/kamailio.log
grep "Python error" /var/log/kamailio/kamailio.log

# Test SIP connectivity
sip-options sip:127.0.0.1:5060

# Monitor resource usage
top -p $(pgrep -f kamailio)
```

---

## Troubleshooting

### Issue 1: "Missing required IF headers" Error

**Error**: Kamailio rejects INVITE with 400 Bad Request

**Cause**: Custom headers X-IF-Trace-ID or X-IF-Hazard not provided

**Solution**:

1. **Verify headers in INVITE**:
```bash
# Use tcpdump to capture SIP packets
tcpdump -i eth0 -A "port 5060" | grep -A 20 "INVITE"

# Look for:
# X-IF-Trace-ID: abc123def456
# X-IF-Hazard: safety
```

2. **Check SIP client configuration**:
```python
# Ensure IFMessage.payload includes trace_id
message = IFMessage(
    ...
    trace_id="abc123def456",  # Required!
    payload={
        "hazards": ["safety"],  # Required!
        ...
    }
)
```

3. **Verify Kamailio routing**:
```kamailio
# In config/kamailio.cfg, check IF_ESCALATE_INVITE route
route[IF_ESCALATE_INVITE] {
    $var(trace_id) = $hdr(X-IF-Trace-ID);
    $var(hazard) = $hdr(X-IF-Hazard);

    if (!$var(trace_id) || !$var(hazard)) {
        xlog("L_WARN", "Missing headers: trace=$var(trace_id) hazard=$var(hazard)\n");
        ...
    }
}
```

### Issue 2: "IF.guard policy rejected" Error

**Error**: Kamailio rejects INVITE with 403 Forbidden

**Cause**: Expert not in approved registry or specialization mismatch

**Solution**:

1. **Check expert registry**:
```python
from communication.sip_proxy import IFGuardPolicy

policy = IFGuardPolicy()
print(policy.approved_experts)
# Look for your expert_id in the registry
```

2. **Verify specialization match**:
```python
# If trying to use expert-safety@external.advisor for "ethics" hazard:
expert = policy.approved_experts["expert-safety@external.advisor"]
print(expert["specialization"])  # ["safety", "alignment"]
# "ethics" not in specialization → REJECTED

# Solution: Use expert-ethics@external.advisor instead
```

3. **Add expert to registry**:
```python
policy.approved_experts["expert-new@external.advisor"] = {
    "name": "New Expert",
    "specialization": ["hazard_type"],
    "verified": True
}
```

### Issue 3: "No bridge to H.323 council" Error

**Error**: SIPtoH323Bridge fails to connect to guardian council

**Cause**: H323Gatekeeper endpoint unreachable or misconfigured

**Solution**:

1. **Check H.323 gateway endpoint**:
```kamailio
# In route[H323_BRIDGE]:
$ru = "sip:h323-gateway@127.0.0.1:5062"  # Is this correct?

# Verify endpoint is reachable:
# sip h323-gateway@127.0.0.1:5062
```

2. **Check H323Gatekeeper stub**:
```python
from communication.h323_gatekeeper import H323Gatekeeper

gk = H323Gatekeeper()
result = asyncio.run(gk.bridge_external_call(
    sip_call_id="test-001",
    council_call_id="test-council-001",
    external_expert_id="expert-safety@external.advisor"
))
print(result)  # Should show "status": "bridged"
```

3. **Check logs for bridge errors**:
```bash
grep "BRIDGE_ERROR" /var/log/infrafabric/sip_witness.log
grep "bridge" /var/log/kamailio/kamailio.log
```

### Issue 4: "Call timeout" Error

**Error**: SIP INVITE timeout or expert doesn't answer

**Cause**: Expert SIP endpoint not responding or network issue

**Solution**:

1. **Check expert availability**:
```bash
# Ping expert endpoint
sip-options sip:expert-safety@external.advisor

# Check if expert is registered
kamctl fifo ul_show_contact expert-safety external.advisor
```

2. **Check Kamailio transaction timers**:
```kamailio
# In config/kamailio.cfg:
modparam("tm", "fr_timer", 2000)      # Final response: 2 seconds
modparam("tm", "fr_inv_timer", 40000) # INVITE: 40 seconds

# Increase timeouts for slow networks:
modparam("tm", "fr_inv_timer", 60000) # INVITE: 60 seconds
```

3. **Check network connectivity**:
```bash
# Test SIP routing
sip-options sip:127.0.0.1:5060

# Check DNS resolution
nslookup external.advisor

# Check firewall
sudo iptables -L -n | grep 5060
```

### Issue 5: "Media transcoding failed" Error

**Error**: Audio not flowing between SIP expert and H.323 council

**Cause**: MediaTranscoder codec mismatch or port allocation issue

**Solution**:

1. **Check codec compatibility**:
```python
# Verify SIP and H.323 use same codec
bridge_status = bridge.get_bridge_status("bridge-...")
print(bridge_status)

# sip_media and h323_media should use compatible codecs
# Typically: G.711-ulaw (8000 Hz) on both sides
```

2. **Check RTP port allocation**:
```python
# Ensure RTP ports don't conflict
bridge = SIPtoH323Bridge()
all_bridges = bridge.get_all_bridges()

# Each bridge should have unique RTP port
# Default allocation: 10000 + bridge_index
```

3. **Check media encryption**:
```python
# Verify SRTP and H.235 configured
sip_media = bridge.sip_media
h323_media = bridge.h323_media

print(f"SIP encryption: {sip_media.encryption}")    # Should be "SRTP"
print(f"H.323 encryption: {h323_media.encryption}") # Should be "H.235"
```

### Issue 6: "IF.witness log file not found" Error

**Error**: Audit trail events not logged

**Cause**: Log directory not created or permissions issue

**Solution**:

1. **Create log directory**:
```bash
sudo mkdir -p /var/log/infrafabric
sudo chown kamailio:kamailio /var/log/infrafabric
sudo chmod 750 /var/log/infrafabric
```

2. **Check log file permissions**:
```bash
ls -la /var/log/infrafabric/
# Should see sip_witness.log with kamailio:kamailio ownership
```

3. **Enable witness logging**:
```python
# In IFWitnessLogger.__init__():
witness = IFWitnessLogger(
    log_file="/var/log/infrafabric/sip_witness.log"
)
```

### Issue 7: "Python module not loading" Error

**Error**: Kamailio fails to load app_python3 module

**Cause**: Python module not installed or path incorrect

**Solution**:

1. **Install Python module**:
```bash
# Install Kamailio with Python3 support
apt-get install kamailio-python3-modules

# Verify installation
ls -la /usr/lib/kamailio/modules/app_python3.so
```

2. **Check Kamailio config**:
```kamailio
# In config/kamailio.cfg:
loadmodule "app_python3.so"

modparam("app_python3", "load", "/home/user/infrafabric/src/communication/sip_proxy.py")
modparam("app_python3", "script_name", "sip_proxy")

# Verify path exists and is readable
# ls -la /home/user/infrafabric/src/communication/sip_proxy.py
```

3. **Check Kamailio logs for module errors**:
```bash
kamailio -f config/kamailio.cfg -D  # Run in debug mode
grep "python" /var/log/kamailio/kamailio.log
grep "error" /var/log/kamailio/kamailio.log
```

### Issue 8: "Evidence sharing failed" Error

**Error**: WebRTC DataChannel doesn't send evidence to expert

**Cause**: WebRTC agent mesh not yet implemented (stub)

**Solution**:

This is expected in Phase 1 (current). The WebRTC integration will be implemented in Session 2.

**Workaround**:

```python
# For now, evidence is logged but not actually transmitted
# Implement actual WebRTC when Session 2 is complete

# Track evidence in IFMessage payload
message = IFMessage(
    ...
    payload={
        ...
        "evidence_files": ["/var/evidence/file1.json"],
        # These are stored in bridge.evidence_files
    }
)

# Query bridge for evidence list
bridge_status = bridge.get_bridge_status(bridge_id)
# When Session 2 complete, will send these via WebRTC
```

---

## FAQ

**Q: How do I add a new external expert?**

A: Modify `IFGuardPolicy.approved_experts` dictionary in `src/communication/sip_proxy.py`:

```python
self.approved_experts["expert-new@external.advisor"] = {
    "name": "New Expert Name",
    "specialization": ["hazard_type"],
    "verified": True
}
```

**Q: What if the expert's SIP phone is outside our network?**

A: Kamailio routes INVITE to the expert's SIP URI. The external expert's SIP provider handles their registration and routing.

**Q: How long can an escalation call last?**

A: Limited only by system resources. No hard timeout is enforced. Call can be terminated manually via `terminate_call()`.

**Q: What encryption is used for SIP?**

A: Phase 1 uses UDP/TCP (plaintext). Phase 2 will add TLS (port 5061) for encrypted SIP signaling.

**Q: Can multiple experts join the same call?**

A: Current implementation bridges one expert per call. Multiple simultaneous calls to different experts are supported.

**Q: What's the latency for establishing an expert call?**

A: Typically 1-3 seconds (SIP setup + H.323 bridge). Depends on network conditions.

**Q: How are expert credentials managed?**

A: Registry-based (in-memory). Phase 2 will add database persistence.

---

## References

- **SIP Protocol**: RFC 3261 (https://tools.ietf.org/html/rfc3261)
- **Kamailio Docs**: https://kamailio.org/docs/
- **H.323 Protocol**: ITU-T H.323
- **WebRTC**: https://www.w3.org/TR/webrtc/
- **Ed25519**: RFC 8037 (https://tools.ietf.org/html/rfc8037)
- **SRTP**: RFC 3711 (https://tools.ietf.org/html/rfc3711)

---

## Document Version

- **Version**: 1.0
- **Status**: Session 4 Implementation Complete
- **Last Updated**: 2025-11-11
- **Author**: InfraFabric Team
- **License**: SPDX-License-Identifier: MIT
