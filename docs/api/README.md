# InfraFabric API Documentation

This directory contains documentation for all API integrations.

## Quick Links

- [API Roadmap](API_ROADMAP.md) - Master integration plan
- [WebRTC](webrtc/) - Real-time communication
- [SIP](sip/) - Voice/video escalation
- [vMix](vmix/) - Live production
- [Integrations](integrations/) - Other APIs

## Currently Active

| API | Status | Implementation |
|-----|--------|----------------|
| Gemini | ACTIVE | `core/services/librarian.py` |
| Redis Cloud | ACTIVE | `core/logistics/packet.py` |
| DeepSeek | ACTIVE | Fallback in librarian |
| GitHub | ACTIVE | CI/CD workflows |

## Planned

| API | Target | Priority |
|-----|--------|----------|
| WebRTC | Q1 2026 | P1 |
| SIP | Q2 2026 | P2 |
| OCI | Q1 2026 | P2 |
| vMix | Future | P3 |
