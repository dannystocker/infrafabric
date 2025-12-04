# InfraFabric API Documentation

This directory contains documentation for all API integrations.

## Quick Links

- [API Roadmap](API_ROADMAP.md) - Master integration plan
- [WebRTC](webrtc/) - Real-time communication
- [SIP](sip/) - Voice/video escalation
- [vMix](vmix/) - Live production
- [Integrations](integrations/) - Other APIs
- Recovered artifacts: see `recovered_api_work/` (vMix/OBS controllers/tests/examples from backup branch `claude/cloud-providers-011CV2nnsyHT4by1am1ZrkkA`)

## Currently Active

| API | Status | Implementation |
|-----|--------|----------------|
| Gemini | ACTIVE | `core/services/librarian.py` |
| Redis Cloud | ACTIVE | `core/logistics/packet.py` |
| DeepSeek | ACTIVE | Fallback in librarian |
| GitHub | ACTIVE | CI/CD workflows |
| vMix | RECOVERED | `recovered_api_work/vmix/` (pending reintegration) |
| OBS  | RECOVERED | `recovered_api_work/obs/` (pending reintegration) |

## Planned

| API | Target | Priority |
|-----|--------|----------|
| WebRTC | Q1 2026 | P1 |
| SIP | Q2 2026 | P2 |
| OCI | Q1 2026 | P2 |
| vMix | Future | P3 |
