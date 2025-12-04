# InfraFabric API Integrations Roadmap

**Updated:** 2025-12-04
**Status:** Production Ready (25+ Integrations)
**Project:** InfraFabric Series 2
**Primary Location:** `/if.api/`

---

## Consolidated Structure

All API integrations have been consolidated into the `/if.api/` directory:

```
if.api/
├── broadcast/          # Video/Audio Streaming (P3)
│   ├── vmix/          # vMix HTTP API (COMPLETE)
│   ├── obs/           # OBS WebSocket API (COMPLETE)
│   ├── bus-adapters/  # IF.bus adapters (COMPLETE)
│   └── ndi/           # NDI (PLANNED)
│
├── communication/      # Real-time Communication (P1-P2)
│   ├── webrtc/        # WebRTC P2P mesh (COMPLETE)
│   ├── sip/adapters/  # 7 SIP servers (COMPLETE)
│   └── h323/          # H.323 (PLANNED)
│
├── llm/               # AI/LLM Providers (P1)
│   ├── claude/        # Anthropic (COMPLETE)
│   ├── gemini/        # Google (COMPLETE)
│   └── deepseek/      # DeepSeek (COMPLETE)
│
├── data/              # Data Infrastructure (P1)
│   ├── redis/         # Redis Cloud L1/L2 (COMPLETE)
│   └── file-cache/    # File-based fallback (COMPLETE)
│
├── security/          # Security (P1)
│   └── yologuard/     # Secret detection v3.0 (COMPLETE)
│
├── cloud/             # Cloud Platforms (P2-P3)
│   ├── stackcp/       # StackCP (COMPLETE)
│   └── oci/           # Oracle Cloud (PLANNED)
│
├── defense/           # Defense/C-UAS (ROADMAP)
│   └── cuas/          # Counter-UAS 4-layer architecture
│
└── messaging/         # Notifications (RESEARCH)
    ├── sms-voice/     # Twilio, Plivo, Bandwidth
    ├── email/         # SendGrid, Postmark
    └── team/          # Slack, Discord
```

---

## Integration Status Matrix

### Production Ready (18)

| Category | Integration | Files | Tests | Location |
|----------|-------------|-------|-------|----------|
| Broadcast | vMix | 3 | Yes | `if.api/broadcast/vmix/` |
| Broadcast | OBS | 4 | Yes | `if.api/broadcast/obs/` |
| Broadcast | Bus Adapters | 4 | Yes | `if.api/broadcast/bus-adapters/` |
| Communication | WebRTC | 5+ | Yes | `if.api/communication/webrtc/` |
| Communication | Asterisk | 1 | Yes | `if.api/communication/sip/adapters/` |
| Communication | OpenSIPs | 1 | Yes | `if.api/communication/sip/adapters/` |
| Communication | Kamailio | 1 | Yes | `if.api/communication/sip/adapters/` |
| Communication | FreeSWITCH | 1 | Yes | `if.api/communication/sip/adapters/` |
| Communication | Flexisip | 1 | Yes | `if.api/communication/sip/adapters/` |
| Communication | Yate | 1 | Yes | `if.api/communication/sip/adapters/` |
| LLM | Claude | 3 | Yes | `if.api/llm/claude/` |
| LLM | Gemini | 1 | Yes | `if.api/llm/gemini/` |
| LLM | DeepSeek | 1 | Yes | `if.api/llm/deepseek/` |
| Data | Redis Cloud | 3 | Yes | `if.api/data/redis/` |
| Data | File Cache | 1 | Yes | `if.api/data/file-cache/` |
| Security | Yologuard v3 | 1 | Yes | `if.api/security/yologuard/` |
| Cloud | StackCP | 1 | Yes | `if.api/cloud/stackcp/` |

### Planned/Roadmap (7+)

| Category | Integration | Status | Target |
|----------|-------------|--------|--------|
| Broadcast | NDI | Stub | Q1 2026 |
| Communication | H.323 | Docs | Q2 2026 |
| Cloud | Oracle OCI | Planned | Q1 2026 |
| Defense | C-UAS Detect | Spec | Q2 2026 |
| Defense | C-UAS Track | Spec | Q2 2026 |
| Defense | C-UAS Identify | Spec | Q3 2026 |
| Defense | C-UAS Counter | Spec | Q3 2026 |

---

## Defense/C-UAS Roadmap (Civil & Military)

4-layer philosophy-grounded architecture for drone defense:

| Layer | Function | Philosophy | Civil Use | Military Use |
|-------|----------|------------|-----------|--------------|
| Detect | Passive observation | Empiricism (Locke) | Airport, Prison | Full spectrum |
| Track | Maintain contact | Coherentism (Neurath) | Event security | Multi-target |
| Identify | Friend/Foe | Verificationism | Remote ID | IFF modes |
| Counter | Response | Pragmatism (James) | RF jamming | Full capability |

**See:** `if.api/defense/cuas/README.md`

---

## Priority Matrix (Updated)

| Priority | Category | Integration | Status |
|----------|----------|-------------|--------|
| P0 | Core | Gemini, Redis, Claude | ACTIVE |
| P1 | Communication | WebRTC | COMPLETE |
| P1 | Security | Yologuard v3 | COMPLETE |
| P2 | Communication | SIP (7 servers) | COMPLETE |
| P2 | Cloud | StackCP | COMPLETE |
| P3 | Broadcast | vMix, OBS | COMPLETE |
| P3 | Cloud | OCI | PLANNED |
| P4 | Defense | C-UAS | ROADMAP |

---

## Related Documentation

- **Full Inventory:** `/IF-API-INTEGRATIONS-INVENTORY.md`
- **API Reference:** `/docs/api/API_REFERENCE.md`
- **OpenAPI Spec:** `/docs/api/openapi.yaml`
- **Examples:** `/docs/api/EXAMPLES.md`

---

*Updated by IF.optimise - Consolidated from 38+ branches*
