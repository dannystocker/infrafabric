# REDIS CONTEXT ARCHIVAL CATALOG
**Generated:** 2025-11-23
**Scan Scope:** /home/setup/infrafabric/ + /mnt/c/users/setup/downloads/
**Status:** DISCOVERY PHASE - Awaiting approval for implementation

---

## EXECUTIVE SUMMARY

**Files Discovered:** 57+ unique context files
**Total Data Volume:** ~1.3 MB
**Recommended for Redis:** 22-28 files (~525K content, ~800K with overhead)
**Files to Keep in Git Only:** 8-12 files
**Redundant Files to Consolidate:** 5-7 files

**Recommendation:** Deploy Phases 1 & 2 immediately (~570K memory) for critical infrastructure and research access without hitting typical Redis limits.

---

## DISCOVERY RESULTS BY TIER

### TIER 1: CRITICAL SESSION & INSTANCE HANDOFF FILES
**Location:** /home/setup/infrafabric/
**Total Size:** ~220K
**Files:** 11 active + 3 older instances = 14 files
**Redis Recommendation:** Archive 9 files immediately, 3-5 optionally

| File | Size | Modified | Worth Redis? | Reason |
|------|------|----------|--------------|--------|
| SESSION-RESUME.md | 45K | 2025-11-23 | ✅ HIGHEST | Master session state, used every instance |
| INSTANCE-XX-ZERO-CONTEXT-STARTER.md | 11K | 2025-11-23 | ✅ HIGH | Bootstrap template for all new instances |
| SESSION-INSTANCE-14-GEDIMAT-STATE.md | 18K | 2025-11-23 | ✅ HIGH | Current mission tracking (Gedimat + Quantum) |
| INSTANCE-13-HANDOFF-COMPLETION.md | 17K | 2025-11-23 | ✅ HIGH | Most recent completion state |
| INSTANCE-13-REDIS-TRANSFER-SUMMARY.txt | 14K | 2025-11-23 | ✅ HIGH | Transfer verification log |
| SESSION-INSTANCE-16-NARRATION.md | 9.4K | 2025-11-23 | ✅ YES | Current instance narration |
| SESSION-HANDOVER.md | 19K | 2025-11-22 | ✅ YES | Instances 9-13 recap |
| INSTANCE-13-REDIS-RECOVERY-GUIDE.md | 3.9K | 2025-11-23 | ✅ CRITICAL | Disaster recovery procedures |
| SESSION-HANDOFF-HAIKU-AUTOPOLL.md | 25K | 2025-11-20 | ⚠️ MAYBE | Haiku swarm coordination (if continuing) |
| SESSION-HANDOVER-INSTANCE9.md | 20K | 2025-11-21 | ⚠️ MAYBE | Instance 9 work (4 days old) |
| SESSION-HANDOVER-INSTANCE7.md | 17K | 2025-11-21 | ❌ NO | Already consolidated in SESSION-HANDOVER |
| SESSION-HANDOVER-INSTANCE6.md | 13K | 2025-11-20 | ❌ NO | >5 days old, archived |

### TIER 2: REDIS & TRANSFER MANAGEMENT GUIDES
**Location:** /home/setup/infrafabric/
**Total Size:** ~45K
**Files:** 5 files
**Redis Recommendation:** Archive ALL 5 (critical infrastructure)

| File | Size | Modified | Worth Redis? | TTL |
|------|------|----------|--------------|-----|
| REDIS-CONTEXT-GUIDE.md | 12K | 2025-11-23 | ✅ CRITICAL | 365 days |
| REDIS-TRANSFER-VERIFICATION.md | 16K | 2025-11-22 | ✅ CRITICAL | 180 days |
| HANDOFF-COMPLETE-CHECKLIST.md | 5.2K | 2025-11-20 | ✅ YES | 365 days |
| REDIS-QUICK-REFERENCE.md | 2.5K | 2025-11-22 | ✅ YES | 365 days |
| HANDOFF-INDEX.md | 10K | 2025-11-20 | ⚠️ MAYBE | 30 days |

### TIER 3: STRATEGIC FINDINGS & DISCOVERIES
**Location:** /home/setup/infrafabric/
**Total Size:** ~285K
**Files:** 9 files
**Redis Recommendation:** Archive 7 immediately, 2 optionally

| File | Size | Modified | Worth Redis? | Reason |
|------|------|----------|--------------|--------|
| IF-TTT-COMPLIANCE-AUDIT-GEORGES-REPORT.md | 53K | 2025-11-22 | ✅ YES | Comprehensive audit (largest single file) |
| IF-TTT-COMPLIANCE-AUDIT-GEORGES-NARRATION.md | 28K | 2025-11-22 | ✅ YES | Georges verification narrative |
| IF-INTELLIGENCE-FINDINGS-SUMMARY.md | 24K | 2025-11-22 | ✅ YES | Core methodology findings |
| IF-TTT-CITATION-INDEX-INSTANCES-8-10.json | 34K | 2025-11-22 | ✅ YES | Citation tracking (JSON) |
| IF-INTELLIGENCE-PROCEDURE.md | 19K | 2025-11-22 | ✅ YES | Methodology procedures |
| SECURITY_FINDINGS_IF_TTT_EVIDENCE.md | 16K | 2025-11-20 | ⚠️ MAYBE | Security analysis |
| IF-TTT-EVIDENCE-MAPPING.md | 17K | 2025-11-22 | ⚠️ MAYBE | Evidence traceability |
| IF-TTT-CITATION-INDEX-SUMMARY.md | 24K | 2025-11-22 | ⚠️ MAYBE | Consolidate with JSON version |

### TIER 4: HAIKU INVESTIGATION NARRATIVES
**Location:** /home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/
**Total Size:** 124K
**Files:** 4 files
**Redis Recommendation:** Archive ALL 4 (foundational research)

| File | Size | Modified | Worth Redis? | Reason |
|------|------|----------|--------------|--------|
| HAIKU-02-BLOCKER-ANALYSIS.md | 34K | 2025-11-22 | ✅ YES | P0 blocker findings |
| HAIKU-01-GEDIMAT-INVESTIGATION.md | 32K | 2025-11-22 | ✅ YES | Gedimat deep-dive |
| HAIKU-03-METHODOLOGY-TEMPLATES.md | 32K | 2025-11-22 | ✅ YES | Reusable framework templates |
| HAIKU-04-REDIS-INVESTIGATION.md | 17K | 2025-11-22 | ✅ YES | Redis optimization findings |

### TIER 5: IF-FRAMEWORK PAPERS
**Location:** /home/setup/infrafabric/
**Total Size:** ~200K (IF-armour, IF-vision, IF-witness, IF-foundations)
**Files:** 4 files
**Redis Recommendation:** Keep in Git Only (static documents)

**Reason:** These are mature strategic papers already in git with full history. Static content, not instance-dependent, not critical for instance-to-instance transfer.

### TIER 6: NARRATION ARCHIVE
**Location:** /home/setup/infrafabric/papers/narrations/
**Total Size:** 344K
**Files:** 6+ production episodes
**Redis Recommendation:** Archive 3 production episodes (Tier 3)

| File | Size | Worth Redis? | Reason |
|------|------|--------------|--------|
| if.instance.ep.13_the-partnership-infrastructure-built.md | 25K | ✅ YES | Production narrative for external use |
| if.instance.ep.14_the-research-architect-reflection.md | 19K | ✅ YES | Production narrative for external use |
| if.instance.ep.15_methodology-enhancement-swarm.md | 16K | ✅ YES | Production narrative for external use |
| INSTANCE_12_CLAUDE_NARRATION_GEDIMAT_FRAMEWORK.md | 20K | ⚠️ MAYBE | Historical; content in SESSION-RESUME |

### TIER 7: WINDOWS DOWNLOADS BACKUP
**Location:** /mnt/c/users/setup/downloads/
**Total Size:** ~115K
**Files:** 9 files
**Redis Recommendation:** Archive original in /home/setup/infrafabric only (avoid duplication)

**Note:** Contains duplicates and old handoffs (20+ days). Clean up downloads folder after verification.

---

## PROPOSED REDIS KEY STRUCTURE

### Priority Tier 1 (IMMEDIATE - Deploy in next 24 hours)
```redis
# 6 files, ~95K content, ~150K with overhead
instance:master:session-resume
instance:template:zero-context-bootstrap
instance:13:completion-state
instance:13:redis-transfer-log
shared:redis-usage-guide
shared:redis-recovery-procedures
```

### Priority Tier 2 (FIRST WEEK - Deploy with Tier 1)
```redis
# 10 files, ~280K content, ~420K with overhead
instance:14:gedimat-quantum-state
instance:16:session-narration
research:haiku-01-gedimat-investigation
research:haiku-02-blocker-analysis
research:haiku-03-methodology-templates
research:haiku-04-redis-investigation
shared:intelligence-findings-core
instance:12:georges-compliance-report-full
shared:intelligence-procedures-methodology
shared:citations-instances-8-10-json
```

### Priority Tier 3 (OPTIONAL - Deploy Week 2+)
```redis
# 6 files, ~150K content, ~225K with overhead
narrative:ep-13-partnership-infrastructure
narrative:ep-14-research-architect
narrative:ep-15-methodology-enhancement
shared:handoff-completion-checklist
shared:redis-quick-reference
shared:redis-verification-procedures
```

---

## MEMORY IMPACT ANALYSIS

| Tier | Files | Content Size | Redis Overhead | Total | TTL | Priority |
|------|-------|----------------|----------------|-------|-----|----------|
| Tier 1 | 6 | ~95K | ~55K | ~150K | 30-365d | IMMEDIATE |
| Tier 2 | 10 | ~280K | ~140K | ~420K | 60-180d | FIRST WEEK |
| Tier 3 | 6 | ~150K | ~75K | ~225K | 90-365d | OPTIONAL |
| **Total** | **22** | **~525K** | **~270K** | **~795K** | Varied | Phase 1+2 |

**Recommendation:** Deploy Tier 1 + Tier 2 = ~570K memory (reasonable for most Redis instances).
**Maximum Safe Deployment:** All 22 files = ~800K (assumes >1GB Redis instance).

---

## FILES TO EXCLUDE FROM REDIS

### Keep in Git Only (Static, Already Versioned)
- IF-armour.md (48K)
- IF-vision.md (34K)
- IF-witness.md (41K)
- IF-foundations.md (76K)

**Reason:** Mature strategic papers with full git history. Static content not requiring instance-to-instance transfer. Full commit history provides better value than Redis.

### Consolidate/Archive Later (Redundant Versions)
- IF-TTT-CITATION-INDEX-SUMMARY.md (consolidate with JSON)
- SESSION-INSTANCE-13-SUMMARY.md (consolidate with SESSION-RESUME)
- INSTANCE-12-REDIS-TRANSFER.md (consolidate with _SUMMARY version)
- Old Windows downloads (consolidate in single location)

### Purge After Archival
- SESSION-HANDOVER-INSTANCE6.md, SESSION-HANDOVER-INSTANCE7.md (7+ days old, already consolidated)
- Old /mnt/c/users/setup/downloads backups (20+ days old)

---

## ARCHIVAL CRITERIA REFERENCE

### ✅ YES - Archive to Redis
1. **Used by next 2-3 instances** (session state, recovery guides)
2. **Unique discoveries not easily recreated** (research findings, audit reports)
3. **Must be accessible to every instance** (infrastructure guides, procedures)
4. **External-facing deliverables** (production narratives)
5. **Recently created** (<5 days old for instance-specific work)

### ⚠️ MAYBE - Consider Archival
1. **Moderately useful but alternatives exist** (old narratives with summaries elsewhere)
2. **Static references that change rarely** (evidence mapping, citation summaries)
3. **Conditional use** (Haiku swarm files if continuing swarm pattern)

### ❌ NO - Keep in Git Only or Purge
1. **Mature, static papers** (IF-framework documents already fully versioned)
2. **Older than 5 days and consolidated elsewhere** (Instance 6, 7 handovers)
3. **Duplicate backups** (Windows downloads copies)
4. **Multiple versions of same content** (keep best version only)

---

## IMPLEMENTATION CHECKLIST

- [ ] **Phase 1 Approval** - User approves 6 Tier 1 files for archival
- [ ] **Phase 1 Load** - Load all 6 Tier 1 files to Redis with correct TTLs
- [ ] **Phase 1 Verification** - Run verification command, confirm all keys readable
- [ ] **Phase 2 Approval** - User approves 10 Tier 2 files for archival
- [ ] **Phase 2 Load** - Load all 10 Tier 2 files to Redis with correct TTLs
- [ ] **Phase 2 Verification** - Run verification command, confirm cumulative 16 keys
- [ ] **Consolidation** - Remove redundant files (duplicate _SUMMARY versions)
- [ ] **Git Cleanup** - Verify /mnt/c/users/setup/downloads backups can be purged
- [ ] **Phase 3 Decision** - User decides on optional Tier 3 narratives

---

## VERIFICATION COMMAND

Save and run this after archival implementation:

```bash
#!/bin/bash
CRITICAL_KEYS=(
    "instance:master:session-resume"
    "instance:template:zero-context-bootstrap"
    "instance:13:completion-state"
    "instance:13:redis-transfer-log"
    "shared:redis-usage-guide"
    "shared:redis-recovery-procedures"
)

echo "=== REDIS CONTEXT ARCHIVAL VERIFICATION ==="
for key in "${CRITICAL_KEYS[@]}"; do
    TTL=$(redis-cli TTL "$key" 2>/dev/null)
    SIZE=$(redis-cli STRLEN "$key" 2>/dev/null)
    if [ "$TTL" -gt 0 ]; then
        echo "✅ $key (${SIZE} bytes, TTL: ${TTL}s)"
    else
        echo "❌ $key - NOT FOUND"
    fi
done
echo "Total Redis memory: $(redis-cli INFO memory | grep used_memory_human)"
```

---

## NEXT STEPS

1. **Review this catalog** - Confirm recommendations align with your archival strategy
2. **Approve Phase 1** - Authorize loading 6 critical infrastructure files to Redis
3. **Approve Phase 2** - Authorize loading 10 research and findings files to Redis
4. **Implement & Verify** - Run load sequence and verification command
5. **Optional Phase 3** - Decide on 6 production narratives later as needed

**Note:** This is DISCOVERY phase only. No files have been moved or modified. All recommendations await your approval before any Redis operations execute.

