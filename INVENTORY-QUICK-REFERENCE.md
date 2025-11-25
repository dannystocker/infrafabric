# InfraFabric File Inventory - Quick Reference

**Complete inventory:** `/home/setup/infrafabric/INFRAFABRIC_COMPLETE_INVENTORY.md` (35 KB)

---

## Critical Stats

| Metric | Value |
|--------|-------|
| Total Files | 11,705 |
| Total Size | 1.7 GB |
| Markdown Files | 251 |
| Python Scripts | 2,478 |
| JSON Config Files | 90 |
| Text Files | 324 |

---

## The 4 Master Files (Start Here)

1. **agents.md** (144 KB) - ALL projects documented (InfraFabric, NaviDocs, ICW, Digital-Lab, StackCP)
2. **SESSION-RESUME.md** (48 KB) - Current state, blockers, next actions
3. **IF-foundations.md** (76 KB) - Core principles and architecture
4. **README.md** (24 KB) - Project overview

---

## Directory Map

| Path | Size | Purpose |
|------|------|---------|
| /docs | 1.0 MB | Evidence, metrics, evaluation |
| /papers | 928 KB | Research papers (27 files) |
| /gedimat | 336 KB | Confidence framework |
| /out | 711 MB | Analysis output (large) |
| /swarm-architecture | 20 MB | Multi-agent patterns |
| /philosophy | 168 KB | Philosophy database |
| /annexes | 304 KB | Supplementary materials |
| /code/yologuard | 108 KB | Security implementation |
| /prompts | 112 KB | Agent prompts |
| /frameworks | 24 KB | Inquiry protocols |
| /tools | 12 KB | Utilities |
| /tests | 12 KB | Test suites |

---

## 16 IF-* Core Components

| File | Size | Category |
|------|------|----------|
| IF-foundations.md | 76 KB | Operating principles |
| IF-armour.md | 48 KB | Security/defensive |
| IF-vision.md | 36 KB | Strategic direction |
| IF-witness.md | 44 KB | Evidence methodology |
| IF-INTELLIGENCE-FINDINGS-SUMMARY.md | 24 KB | Intelligence results |
| IF-INTELLIGENCE-PROCEDURE.md | 20 KB | Intelligence gathering |
| IF-TTT-EVIDENCE-MAPPING.md | 20 KB | Compliance mapping |
| IF-TTT-CITATION-INDEX-SUMMARY.md | 24 KB | Citation index |
| IF-TTT-COMPLIANCE-AUDIT-GEORGES-REPORT.md | 56 KB | Full audit |
| IF-TTT-COMPLIANCE-AUDIT-GEORGES-NARRATION.md | 28 KB | Audit narrative |
| IF-TTT-INDEX-README.md | 8 KB | IF.TTT overview |
| IF-TTT-CITATION-INDEX-INSTANCES-8-10.json | 36 KB | Citation data |
| IF-TTT-INDEX-VERIFICATION.txt | 20 KB | Verification report |
| frameworks/IF-WWWWWW-INQUIRY-PROTOCOL.md | 4 KB | Six-W methodology |
| papers/IF-MEMORY-DISTRIBUTED.md | 48 KB | Memory architecture |
| papers/IF-SWARM-S2.md | 32 KB | Swarm patterns |

---

## Redis Caching Status

**41 keys already cached:**
- Core docs (6 keys)
- TTT compliance (8 keys)
- GEDIMAT (6 keys)
- Redis/caching (4 keys)
- Sessions (8 keys)
- CODEX (3 keys)
- Georges partnership (3 keys)

**Candidates for caching (next 43 keys):**
- Priority 1: Component files (220 KB)
- Priority 2-3: Session/instance context (668 KB)

---

## Session and Instance Files (52 total)

**Active Sessions:**
- SESSION-HANDOVER.md, SESSION-INSTANCE-18-FINAL-HANDOVER.md, SESSION-INSTANCE-19-PHASE-A-COMPLETE.md

**INSTANCE Files (19 total):**
- INSTANCE-11 through INSTANCE-19 (various formats)
- Plus 4 HAIKU-SESSION-NARRATIVES (Redis investigation, GEDIMAT, methodology, blocker analysis)

**Handover/Handoff Protocols:**
- 52 files documenting context transfers between sessions

---

## Python Automation (2,478 scripts)

**Agent Shards:**
- haiku_shard_autopoll.py (auto-polling)
- haiku_shard_DIRECT.py (direct control)
- haiku_shard_TASKTOOL.py (Task tool integration)
- launch_haiku_shard_*.py (6 launcher variants)

**Sonnet Controllers:**
- sonnet_polling_loop_5min.py (5-min polling)
- sonnet_debug_bus_loop.py (debug mode)
- sonnet_direct_query_loop.py (direct queries)
- queen_sonnet_simple.py (primary controller)

**Testing Suite:**
- test_real_haiku_llm.py
- test_distributed_memory.py
- tests/test_yologuard.py
- migrate_memory.py

---

## Architecture Documents

| File | Size | Purpose |
|------|------|---------|
| REDIS-EXOSKELETON-ARCHITECTURE.md | 20 KB | Redis system design |
| REDIS-AGENT-COMMUNICATION.md | 24 KB | Agent-to-agent messaging |
| DISTRIBUTED_MEMORY_VALIDATION_REPORT.md | 32 KB | Memory system validation |
| MULTI-AGENT-SESSION-NARRATIVE.md | 32 KB | Multi-agent execution patterns |
| papers/IF-MEMORY-DISTRIBUTED.md | 48 KB | Distributed memory specification |
| papers/IF-SWARM-S2.md | 32 KB | Swarm coordination v2 |

---

## Integration Points

### CODEX System
- CODEX-STARTER-PROMPT.md (4 KB)
- CODEX-USAGE-GUIDE.md (16 KB)
- CODEX-CLI-INTEGRATION.md (16 KB)
- CODEX-5.1-MAX-SUPERPROMPT.md (20 KB)

### GEMINI Integration
- GEMINI-WEB-INTEGRATION.md (20 KB)
- GEMINI-APP-INTELLIGENCE-INTEGRATION.md (32 KB)
- GEMINI-3-RESEARCH-PROMPT.txt (12 KB)

### StackCP Integration
- STACKCP-AGENT-MANUAL.md (8 KB)
- STACKCP-REDIS-PROXY-SETUP.md (16 KB)
- docs/STACKCP_REDIS_*.md (3 files)

### ICW Project
- ICW_SESSION_HANDOVER_NOV21.md (12 KB)

---

## Partnership and Research

### Georges Partnership (7 files)
- PARTNERSHIP-EXECUTION-PLAN-GEORGES.md (16 KB)
- GEORGES-ANTOINE-GARY-COMPREHENSIVE-PROFILE.md (20 KB)
- GEORGES-MATERIALS-INDEX.md (16 KB)
- QUICK-REFERENCE-GEORGES-PARTNERSHIP.md (12 KB)
- RAPPORT-POUR-GEORGES-ANTOINE-GARY.md (32 KB)

### Research Libraries
- philosophy/ (168 KB) - Philosophy database with 3 files
- papers/ (928 KB) - 27 research papers + 6 narrations
- gedimat/ (336 KB) - Confidence framework + 20+ analysis files
- intelligence-tests/ (652 KB) - French logistics testing suite

---

## Key Files by Use Case

**First Day Onboarding:**
1. agents.md (master docs)
2. SESSION-RESUME.md (current state)
3. IF-foundations.md (how system works)
4. README.md (overview)

**Compliance/Verification:**
1. IF-TTT-COMPLIANCE-AUDIT-GEORGES-REPORT.md (56 KB)
2. IF-TTT-EVIDENCE-MAPPING.md (20 KB)
3. IF-TTT-CITATION-INDEX-SUMMARY.md (24 KB)

**Architecture/Design:**
1. REDIS-EXOSKELETON-ARCHITECTURE.md (20 KB)
2. REDIS-AGENT-COMMUNICATION.md (24 KB)
3. papers/IF-MEMORY-DISTRIBUTED.md (48 KB)
4. papers/IF-SWARM-S2.md (32 KB)

**Handoff/Session Management:**
1. SESSION-HANDOVER.md (primary template)
2. SESSION-INSTANCE-18-FINAL-HANDOVER.md (latest)
3. INSTANCE-XX-ZERO-CONTEXT-STARTER.md (bootstrap)
4. README-HANDOFF-START-HERE.md (instructions)

**Deployment/Operations:**
1. STACKCP-REDIS-PROXY-SETUP.md (16 KB)
2. REDIS-CLOUD-MIGRATION-COMPLETION-2025-11-23.md (8 KB)
3. CODEX-USAGE-GUIDE.md (16 KB)
4. GEDIMAT-CONFIDENCE-FRAMEWORK.md (16 KB)

---

## Files NOT Yet in Redis Cache

### Priority 1 (High Priority - 220 KB)
- IF-TTT-CITATION-INDEX-SUMMARY.md (24 KB)
- IF-INTELLIGENCE-FINDINGS-SUMMARY.md (24 KB)
- IF-INTELLIGENCE-PROCEDURE.md (20 KB)
- papers/IF-MEMORY-DISTRIBUTED.md (48 KB)
- papers/IF-SWARM-S2.md (32 KB)
- frameworks/IF-WWWWWW-INQUIRY-PROTOCOL.md (4 KB)

### Priority 2 (Medium Priority - 296 KB)
- All SESSION-INSTANCE-* files (128 KB)
- All HAIKU-SESSION-NARRATIVES (124 KB)
- papers/narrations/* (48 KB)

### Priority 3 (Lower Priority - 372 KB)
- Evidence evaluation files
- Analysis reports
- Testing documentation

---

## Maintenance Status

| Task | Status | Date |
|------|--------|------|
| Inventory Created | COMPLETE | 2025-11-23 |
| Redis Migration | COMPLETE | 2025-11-23 |
| TTT Compliance Audit | COMPLETE | 2025-11-23 |
| GEDIMAT Integration | COMPLETE | 2025-11-23 |
| Session Handover System | COMPLETE | 2025-11-10 |
| Haiku Autopoll Setup | COMPLETE | 2025-11-23 |

---

## Quick Command Reference

```bash
# View complete inventory
cat /home/setup/infrafabric/INFRAFABRIC_COMPLETE_INVENTORY.md

# Count files by type
find /home/setup/infrafabric -name "*.md" | wc -l
find /home/setup/infrafabric -name "*.py" | wc -l

# Find specific IF-* components
find /home/setup/infrafabric -name "IF-*.md" | sort

# List largest files
du -sh /home/setup/infrafabric/* | sort -h | tail -20

# Find session/instance files
find /home/setup/infrafabric -name "SESSION*" -o -name "INSTANCE*" | sort

# Check Redis cache status
redis-cli KEYS "if:*" | wc -l
```

---

## Organization Recommendations

**Current Issues:**
1. 251 MD files in root directory (cluttered)
2. 711 MB /out directory (should archive)
3. Duplicate files across locations
4. Inconsistent naming conventions

**Recommended Structure:**
```
/home/setup/infrafabric/
├── 01-CORE/ (4 master files)
├── 02-COMPONENTS/ (14 IF-* files)
├── 03-SESSIONS/ (52 SESSION/INSTANCE files)
├── 04-RESEARCH/ (papers, gedimat, philosophy)
├── 05-IMPLEMENTATION/ (code, prompts, frameworks, tools)
├── 06-ANALYSIS/ (docs, evidence, annexes, swarm-architecture)
├── 07-ARCHIVES/ (out directory, old files)
└── INVENTORY.md (this file)
```

---

Last Updated: 2025-11-23
Maintained by: Haiku Agent (File Inventory System)
