# InfraFabric API Integrations Roadmap

**Generated:** 2025-11-26
**Status:** Phase 1 Planning
**Project:** InfraFabric Series 2

---

## Integration Categories

### 1. Real-Time Communication APIs

#### WebRTC
- **Status:** PLANNED (git branches exist)
- **Branches:** `claude/webrtc-final-push`, `claude/webrtc-agent-mesh`
- **Purpose:** Agent-to-agent real-time communication mesh
- **Priority:** P1 (Q1 2026)

#### SIP (Session Initiation Protocol)
- **Status:** PLANNED (git branches exist)
- **Branches:** `claude/sip-communication`, `claude/if-bus-sip-adapters`
- **Purpose:** Voice/video escalation from agent to human
- **Priority:** P2 (Q2 2026)

#### vMix
- **Status:** ROADMAP ONLY
- **Purpose:** Live video production integration for demos
- **Priority:** P3 (Future)

---

### 2. AI/ML APIs

| API | Status | Implementation |
|-----|--------|----------------|
| Gemini | ACTIVE | `core/services/librarian.py` |
| DeepSeek | ACTIVE | Fallback in librarian |
| Claude | ACTIVE | Primary coordination |

---

### 3. Infrastructure APIs

| API | Status | Purpose |
|-----|--------|---------|
| Redis Cloud | ACTIVE | State management |
| GitHub | ACTIVE | CI/CD |
| OCI | PLANNED | Compute/storage |

---

## Priority Matrix

| API | Priority | Quarter | Status |
|-----|----------|---------|--------|
| Gemini | P0 | DONE | ACTIVE |
| Redis | P0 | DONE | ACTIVE |
| WebRTC | P1 | Q1 2026 | PLANNED |
| SIP | P2 | Q2 2026 | PLANNED |
| vMix | P3 | Future | ROADMAP |

---

*This roadmap is maintained as part of InfraFabric Series 2.*
