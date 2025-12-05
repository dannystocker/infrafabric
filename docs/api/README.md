# InfraFabric API Documentation

This directory contains documentation for all API integrations.

## Quick Links

- [API Roadmap](API_ROADMAP.md) - Master integration plan
- [WebRTC](webrtc/) - Real-time communication
- [SIP](sip/) - Voice/video escalation
- [vMix](vmix/) - Live production
- [LLM](llm/) - LLM providers and debug tools
- [Fintech](fintech/) - Fintech adapters and debug tools
- [Integrations](integrations/) - Other APIs
- Broadcast controllers and IF.bus adapters live under `if.api/broadcast/` (vMix/OBS controllers, tests, and bus adapters).

## Currently Active

| API | Status | Implementation |
|-----|--------|----------------|
| Gemini | ACTIVE | `core/services/librarian.py` |
| Redis Cloud | ACTIVE | `core/logistics/packet.py` |
| DeepSeek | ACTIVE | Fallback in librarian |
| GitHub | ACTIVE | CI/CD workflows |
| vMix | ACTIVE | `if.api/broadcast/vmix/` |
| OBS  | ACTIVE | `if.api/broadcast/obs/` |

## Planned

| API | Target | Priority |
|-----|--------|----------|
| WebRTC | Q1 2026 | P1 |
| SIP | Q2 2026 | P2 |
| OCI | Q1 2026 | P2 |
