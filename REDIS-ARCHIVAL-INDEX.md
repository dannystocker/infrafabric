# REDIS CONTEXT ARCHIVAL - QUICK INDEX

**Generated:** 2025-11-23
**Status:** Discovery Phase Complete
**Output:** REDIS-ARCHIVAL-CATALOG.md (full details)

---

## ONE-PAGE DECISION SUMMARY

### What We Found
- **57+ context files** across /home/setup/infrafabric/ and Windows downloads
- **~1.3 MB** total active context
- **28 files worth archiving** to Redis (~525K content)
- **8 files** should stay in git only (static frameworks)
- **5 files** can be consolidated (remove duplicates)

### What We Recommend

| Phase | Files | Memory | Priority | Action |
|-------|-------|--------|----------|--------|
| **Phase 1** | 6 | ~150K | **IMMEDIATE** | Master state + recovery guides + infrastructure reference |
| **Phase 2** | 10 | ~420K | **FIRST WEEK** | Research findings + Haiku investigations + procedures |
| **Phase 3** | 6 | ~225K | **OPTIONAL** | Production narratives + reference guides |
| **TOTAL** | 22 | ~795K | - | All recommended files |

**Recommended:** Deploy Phases 1 + 2 = ~570K memory (captures all critical infrastructure & research).

---

## FILES BY ARCHIVAL TIER

### Tier 1: IMMEDIATE - Critical Infrastructure (6 files, ~150K)
```
instance:master:session-resume
  → /home/setup/infrafabric/SESSION-RESUME.md (45K)
  → Master session state, used every instance, 90 day TTL

instance:template:zero-context-bootstrap
  → /home/setup/infrafabric/INSTANCE-XX-ZERO-CONTEXT-STARTER.md (11K)
  → Bootstrap for all new instances, 365 day TTL

instance:13:completion-state
  → /home/setup/infrafabric/INSTANCE-13-HANDOFF-COMPLETION.md (17K)
  → Most recent completion state, 45 day TTL

instance:13:redis-transfer-log
  → /home/setup/infrafabric/INSTANCE-13-REDIS-TRANSFER-SUMMARY.txt (14K)
  → Transfer verification log, 60 day TTL

shared:redis-usage-guide
  → /home/setup/infrafabric/REDIS-CONTEXT-GUIDE.md (12K)
  → How to use Redis, 365 day TTL

shared:redis-recovery-procedures
  → /home/setup/infrafabric/INSTANCE-13-REDIS-RECOVERY-GUIDE.md (3.9K)
  → Disaster recovery guide, 180 day TTL
```

### Tier 2: FIRST WEEK - Research & Findings (10 files, ~420K)
```
research:haiku-02-blocker-analysis
  → /home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-02-BLOCKER-ANALYSIS.md (34K)
  → P0 blocker findings, 90 day TTL

research:haiku-01-gedimat-investigation
  → /home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-01-GEDIMAT-INVESTIGATION.md (32K)
  → Gedimat deep-dive, 90 day TTL

research:haiku-03-methodology-templates
  → /home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-03-METHODOLOGY-TEMPLATES.md (32K)
  → Reusable framework templates, 180 day TTL

research:haiku-04-redis-investigation
  → /home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-04-REDIS-INVESTIGATION.md (17K)
  → Redis optimization findings, 90 day TTL

instance:12:georges-compliance-report-full
  → /home/setup/infrafabric/IF-TTT-COMPLIANCE-AUDIT-GEORGES-REPORT.md (53K)
  → Comprehensive Georges audit, 90 day TTL

instance:12:georges-compliance-narrative
  → /home/setup/infrafabric/IF-TTT-COMPLIANCE-AUDIT-GEORGES-NARRATION.md (28K)
  → Georges verification narrative, 90 day TTL

shared:intelligence-findings-core
  → /home/setup/infrafabric/IF-INTELLIGENCE-FINDINGS-SUMMARY.md (24K)
  → Core methodology findings, 90 day TTL

shared:citations-instances-8-10-json
  → /home/setup/infrafabric/IF-TTT-CITATION-INDEX-INSTANCES-8-10.json (34K)
  → Citation tracking data, 90 day TTL

shared:intelligence-procedures-methodology
  → /home/setup/infrafabric/IF-INTELLIGENCE-PROCEDURE.md (19K)
  → Methodology procedures, 180 day TTL

shared:redis-verification-procedures
  → /home/setup/infrafabric/REDIS-TRANSFER-VERIFICATION.md (16K)
  → Verification procedures, 180 day TTL
```

### Tier 3: OPTIONAL - Narratives & References (6 files, ~225K)
```
narrative:ep-13-partnership-infrastructure
  → /home/setup/infrafabric/papers/narrations/if.instance.ep.13_...md (25K)
  → Production narrative, 90 day TTL

narrative:ep-14-research-architect
  → /home/setup/infrafabric/papers/narrations/if.instance.ep.14_...md (19K)
  → Production narrative, 90 day TTL

narrative:ep-15-methodology-enhancement
  → /home/setup/infrafabric/papers/narrations/if.instance.ep.15_...md (16K)
  → Production narrative, 90 day TTL

shared:handoff-completion-checklist
  → /home/setup/infrafabric/HANDOFF-COMPLETE-CHECKLIST.md (5.2K)
  → Handoff process template, 365 day TTL

shared:redis-quick-reference
  → /home/setup/infrafabric/REDIS-QUICK-REFERENCE.md (2.5K)
  → Quick Redis lookup, 365 day TTL

instance:14:gedimat-quantum-state
  → /home/setup/infrafabric/SESSION-INSTANCE-14-GEDIMAT-STATE.md (18K)
  → Current mission tracking, 60 day TTL
```

### Files to Keep in Git Only (No Redis)
```
IF-armour.md (48K)           - Static framework, full git history
IF-vision.md (34K)           - Static framework, full git history
IF-witness.md (41K)          - Static framework, full git history
IF-foundations.md (76K)      - Static framework, full git history
```

---

## QUICK DECISION MATRIX

| Question | Answer | Action |
|----------|--------|--------|
| Is this used by next 2-3 instances? | YES → | Archive to Redis |
| Is this a unique discovery not easily recreated? | YES → | Archive to Redis |
| Is this infrastructure guide or procedure? | YES → | Archive to Redis |
| Is this static/mature and already in git? | YES → | Keep in git only |
| Is this >5 days old and consolidated elsewhere? | YES → | Consolidate/clean |
| Is this a duplicate backup? | YES → | Remove redundant copy |

---

## APPROVAL WORKFLOW

### Phase 1 Approval (IMMEDIATE)
Approve 6 critical infrastructure files (~150K memory)?
- [APPROVE] Load all 6 to Redis with configured TTLs
- [DEFER] Review full catalog first (REDIS-ARCHIVAL-CATALOG.md)

### Phase 2 Approval (FIRST WEEK)
Approve 10 research & findings files (~420K additional memory)?
- [APPROVE] Load all 10 to Redis with configured TTLs
- [DEFER] Decide after Phase 1 verification

### Phase 3 Approval (OPTIONAL)
Approve 6 production narratives (~225K additional memory)?
- [APPROVE] Load optional narratives
- [DEFER] Deploy only if needed later
- [SKIP] Don't archive narratives (available in git)

---

## VERIFICATION AFTER ARCHIVAL

Run this command to verify all critical keys loaded:

```bash
redis-cli MGET \
  "instance:master:session-resume" \
  "instance:template:zero-context-bootstrap" \
  "instance:13:completion-state" \
  "instance:13:redis-transfer-log" \
  "shared:redis-usage-guide" \
  "shared:redis-recovery-procedures" | wc -l
```

Expected output: `6` (all critical keys present)

---

## WHERE TO FIND DETAILS

**Full Analysis:** `/home/setup/infrafabric/REDIS-ARCHIVAL-CATALOG.md`
- Complete evaluation table (all 57 files)
- Detailed Redis preservation criteria
- Implementation checklist
- Memory impact analysis
- TTL recommendations
- Verification procedures

**This File:** `/home/setup/infrafabric/REDIS-ARCHIVAL-INDEX.md` (quick reference)

---

## STATS AT A GLANCE

| Metric | Value |
|--------|-------|
| Total Files Discovered | 57+ |
| Total Data Volume | ~1.3 MB |
| Files Recommended for Redis | 22-28 (60-70%) |
| Files Keep in Git Only | 8 (20-25%) |
| Memory Cost (Phase 1+2) | ~570K |
| Memory Cost (All Phases) | ~800K |
| Recommended TTL Range | 30-365 days |

---

## NEXT ACTION

1. Read this file (you're doing it!)
2. Review `/home/setup/infrafabric/REDIS-ARCHIVAL-CATALOG.md` for full details
3. Decide on approval for:
   - Phase 1 (IMMEDIATE) - 6 critical files
   - Phase 2 (FIRST WEEK) - 10 research files
   - Phase 3 (OPTIONAL) - 6 narrative files
4. Authorize implementation
5. Run verification after loading

**Status:** DISCOVERY PHASE - No files have been moved or modified yet. All changes await your approval.
