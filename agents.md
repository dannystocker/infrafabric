# InfraFabric Agent & Protocol Documentation

**Generated:** 2025-11-26
**Version:** Series 2 Genesis
**Compliance:** 95%+ (up from 78%)

---

## Overview

InfraFabric is a consent-based AI governance framework with 132 documented IF protocols. This document serves as the master reference for all agents, protocols, and project components.

---

## IF Protocol Registry (Top 50)

| Protocol | Mentions | Status | Implementation |
|----------|----------|--------|----------------|
| IF.guard | 9,176 | ACTIVE | Strategic communications council |
| IF.infrafabric | 6,163 | FRAMEWORK | Core namespace |
| IF.yologuard | 3,433 | ACTIVE | `core/security/yologuard.py` (680 lines) |
| IF.optimise | 3,370 | ACTIVE | Token efficiency engine |
| IF.sam | 2,176 | ACTIVE | 16 facets (8 light + 8 dark) |
| IF.TTT | 2,071 | ACTIVE | Traceable, Transparent, Trustworthy |
| IF.council | 1,933 | ACTIVE | Guardian Council governance |
| IF.vesicle | 1,811 | ACTIVE | `core/transport/vesicle.py` (672 lines) |
| IF.memory | 1,200 | ACTIVE | Distributed memory system |
| IF.search | 1,196 | ACTIVE | 8-pass investigative methodology |
| IF.synthesis | 1,083 | GHOST | Never fully implemented |
| IF.garp | 1,002 | REFERENCE | Government AI Readiness Program |
| IF.bus | 999 | ACTIVE | Message bus infrastructure |
| IF.trace | 960 | ACTIVE | Accountability tracking |
| IF.reflect | 854 | ACTIVE | Self-improvement loops |
| IF.veil | 773 | CONCEPTUAL | Privacy guarantees |
| IF.guardian | 760 | ACTIVE | Guardian role definitions |
| IF.arbitrate | 633 | ACTIVE | `core/governance/arbitrate.py` (945 lines) |
| IF.armour | 611 | REFERENCE | Production validation |
| IF.witness | 375 | REFERENCE | IF-witness.tex paper |
| IF.persona | 306 | ACTIVE | Agent characterization |
| IF.swarm | 258 | ACTIVE | Multi-agent coordination |
| IF.philosophy | 244 | ACTIVE | 12 philosophers, 20 quotes |
| IF.intelligence | 154 | ACTIVE | Research intelligence |
| IF.WWWWWW | 124 | ACTIVE | 6W structured inquiry |
| IF.librarian | 49 | ACTIVE | `core/services/librarian.py` (410 lines) |
| IF.citate | 35 | ACTIVE | Citation generation |

**Full registry:** See `docs/IF_PROTOCOL_REGISTRY.md`

---

## Code Implementation Map

### Production Code

| Component | File | Lines | Status |
|-----------|------|-------|--------|
| IF.arbitrate | `src/infrafabric/core/governance/arbitrate.py` | 945 | ACTIVE |
| IF.yologuard | `src/infrafabric/core/security/yologuard.py` | 680 | ACTIVE |
| IF.vesicle | `src/infrafabric/core/transport/vesicle.py` | 672 | ACTIVE |
| IF.librarian | `src/infrafabric/core/services/librarian.py` | 410 | ACTIVE |
| IF.ocr | `src/infrafabric/core/workers/ocr_worker.py` | 63 | STUB |

**Total Production Code:** 2,770 lines

### Supporting Files

| File | Lines | Purpose |
|------|-------|---------|
| `core/transport/test_vesicle.py` | 610 | Unit tests |
| `core/transport/examples.py` | 409 | Usage examples |
| `core/transport/README.md` | 715 | Documentation |
| `core/governance/README.md` | 430 | Documentation |

---

## Project Locations

| Project | Local Path | Remote |
|---------|------------|--------|
| InfraFabric | `/home/setup/infrafabric` | github.com/dannystocker/infrafabric |
| InfraFabric-Core | `/home/setup/infrafabric-core` | github.com/dannystocker/infrafabric-core |
| NaviDocs | `/home/setup/navidocs` | github.com/dannystocker/navidocs |
| ICW | `/home/setup/icw-nextspread` | Gitea: localhost:4000 |
| Job Hunt | `/home/setup/job-hunt` | Gitea: localhost:4000 |

---

## Guardian Council

### 20-Voice Extended Council

**6 Core Guardians:**
1. Research (Google perspective)
2. OSS Maintainer
3. Ghost of Instance #0
4. Contrarian Guardian (veto power)
5. Security Auditor
6. Chair (Codex)

**6 Philosophers:**
- 3 Western: Aristotle, Kant, Mill
- 3 Eastern: Confucius, Laozi, Buddha

**8 IF.sam Facets:**
- 4 Light Side: Visionary, Ethical, Communicator, Builder
- 4 Dark Side: Pragmatist, Negotiator, Strategist, Survivor

### Constitutional Rules

- 80% supermajority for approval
- Contrarian veto at >95% approval
- 14-day cooling-off period for amendments

---

## Redis State Management

**Host:** `redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com:19956`
**Keys:** 621 (as of 2025-11-26)
**Corruption:** 0% (cleaned from 43%)

### Key Prefixes

| Prefix | Count | Purpose |
|--------|-------|---------|
| `session:infrafabric:*` | 150+ | Session handover |
| `context:archive:*` | 200+ | Archived documents |
| `context:council:*` | 20+ | Council chronicles |
| `research:*` | 10+ | Research findings |

---

## API Integrations

### Active

| API | Status | Implementation |
|-----|--------|----------------|
| Gemini | ACTIVE | IF.librarian |
| Redis Cloud | ACTIVE | IF.vesicle |
| DeepSeek | ACTIVE | Fallback |
| GitHub | ACTIVE | CI/CD |

### Planned

| API | Target | Priority |
|-----|--------|----------|
| WebRTC | Q1 2026 | P1 |
| SIP | Q2 2026 | P2 |
| OCI | Q1 2026 | P2 |

**Full roadmap:** See `docs/api/API_ROADMAP.md`

---

## Documentation Index

| Document | Location | Purpose |
|----------|----------|---------|
| IF Protocol Registry | `docs/IF_PROTOCOL_REGISTRY.md` | Complete protocol list |
| API Roadmap | `docs/api/API_ROADMAP.md` | Integration plans |
| Gap Report | `docs/INFRAFABRIC-SERIES2-GAP-REPORT.md` | Compliance tracking |
| Chronicles | `docs/narratives/` | Historical record |
| Council Debates | `docs/debates/` | Governance decisions |

---

## Session Handover Protocol

When starting a new session:

1. Read this file (`agents.md`)
2. Check `SESSION-RESUME.md` for current mission
3. Run `just check` to verify build
4. Run `just audit-db` to verify Redis

---

*Last updated: 2025-11-26 by Comprehensive IF Protocol Scan*
