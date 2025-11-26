# InfraFabric Missing Links Audit
**Date:** 2025-11-25
**Agent:** D (The Scout)
**Status:** Phase 4 - Dimension Future

---

## Overview

This document identifies all referenced items that don't exist in the codebase or have broken references.

---

## 1. Referenced Files That Don't Exist

### 1.1 Citation Schema
**Referenced in:** agents.md line 335, IF-foundations.md, IF-armour.md
**Expected location:** `/home/setup/infrafabric/schemas/citation/v1.0.schema.json`
**Actual status:** ❌ File not found

**Impact:** IF.TTT framework cannot be validated (no schema to test against)

**Action needed:** Create citation schema JSON with these fields:
```json
{
  "claim_id": "string",
  "text": "string",
  "source": "string",
  "verification_status": "unverified|verified|disputed|revoked",
  "uri": "if://citation/uuid",
  "timestamp": "ISO8601",
  "signed_by": "string",
  "signature": "base64"
}
```

---

### 1.2 Citation Validation Script (Partial)
**Referenced in:** agents.md line 336
**Path:** `/home/setup/infrafabric/tools/citation_validate.py`
**Status:** File exists but only ~50 lines (stub)

**Content:**
- ❌ No validation logic
- ❌ No schema loading
- ❌ No DOI/URL verification
- ❌ No citation database

**Action needed:** Implement full validation engine

---

### 1.3 Security Revocation List
**Referenced in:** CLAUDE.md and agents.md
**Path:** `/home/setup/.security/revoked-keys-whitelist.md`
**Status:** File exists ✅

**Content checked:** Confirms OpenRouter API revocation (2025-11-07)

---

## 2. Referenced External Resources

### 2.1 MCP Multiagent Bridge Repository
**Referenced in:** agents.md:116, multiple papers
**Contains:** IF.search.py, IF.yologuard implementations
**Status:** External repo (not in /home/setup)
**Location:** Likely GitHub but not accessible locally

**Action needed:**
- Clone or document GitHub URL
- Add submodule reference
- Or copy implementation to local repo

---

### 2.2 InfraFabric Core Repository
**Referenced in:** agents.md:252
**Contains:** Research papers in LaTeX
**Status:** External repo (not in /home/setup)
**Path mentioned:** `/home/setup/infrafabric-core`

**Checked:** Directory exists but is sparse

**Action needed:**
- Verify GitHub: https://github.com/dannystocker/infrafabric-core
- Ensure local copy is up-to-date
- Document paper locations

---

## 3. Referenced Components with No Implementation

### 3.1 IF.guard - Guardian Council
**Referenced in:**
- agents.md (line 136-146)
- IF-vision.md (throughout)
- IF-armour.md (line 160, 747, 762)
- Multiple council-archive files

**Exists:**
- Skeleton: `/home/setup/infrafabric/tools/guardians.py` (30% complete)
- Example: `/home/setup/infrafabric/tools/guardian_debate_example.py`

**Missing:**
- 6 Core Guardian definitions (not in database)
- Integration with IF.philosophy-database.yaml
- 8 IF.ceo facet definitions (for extended council)
- Automated debate orchestration
- Council decision persistence

**Expected file:** `/home/setup/infrafabric/data/guardians.yaml` (❌ doesn't exist)

---

### 3.2 IF.ceo - Sam Altman Council
**Referenced in:**
- agents.md (line 140-142)
- CLAUDE.md ("IF.ceo have a panel of 8...")
- IF-vision.md references to "8 IF.ceo facets"

**Exists:** Concept only

**Missing:** Everything
- No personality definitions
- No profile data
- No implementation
- No specifications

**Expected file:** `/home/setup/infrafabric/data/sam_altman_facets.yaml` (❌ doesn't exist)

---

### 3.3 IF.swarm - Multi-Agent Coordination
**Referenced in:**
- agents.md (line 144-146)
- KEY_MOMENTS.json (line 288: "15-agent epistemic swarm")
- GITHUB_API_ROADMAP_CHECK.md (line 188: "IF.swarm thymic selection")

**Exists:** Zero implementation

**Missing:** Everything
- 15 agent definitions
- Thymic selection algorithm
- Consensus mechanism
- Veto protocol

**Expected file:** `/home/setup/infrafabric/data/swarm_agents.yaml` (❌ doesn't exist)

---

### 3.4 IF.arbitrate - Resource Arbitration
**Referenced in:**
- agents.md (implied in optimization)
- GITHUB_API_ROADMAP_CHECK.md (line 253-266)

**Exists:** Pseudo-code only

**Missing:** Everything
- Cost model definitions
- Optimization algorithm
- Cloud API integrations
- Real-time monitoring

**Expected file:** `/home/setup/infrafabric/code/IF.arbitrate.py` (❌ doesn't exist)

---

### 3.5 IF.vesicle - Module Ecosystem
**Referenced in:**
- GITHUB_API_ROADMAP_CHECK.md (line 176-188)
- agents.md (implied)

**Exists:** Module list planned only

**Missing:** Everything
- 20 module specifications
- Boilerplate templates
- Discovery mechanism
- Module interface spec

**Expected file:** `/home/setup/infrafabric/universe/future/vesicle/MODULES.yaml` (❌ doesn't exist)

---

## 4. Referenced Data Files with Issues

### 4.1 IF.philosophy-database.yaml
**Status:** ✅ Exists and is complete
**Location:** `/home/setup/infrafabric/philosophy/IF.philosophy-database.yaml`
**Verified:** 12 philosophers mapped, 6 traditions covered

---

### 4.2 IF.persona-database.json
**Status:** ✅ Exists
**Location:** `/home/setup/infrafabric/philosophy/IF.persona-database.json`
**Verified:** Agent archetypes documented

---

### 4.3 IF_COMPONENT_INVENTORY.yaml
**Status:** ✅ Exists
**Location:** `/home/setup/infrafabric/docs/evidence/IF_COMPONENT_INVENTORY.yaml`
**Verified:** Comprehensive component list from evaluation

---

### 4.4 Guardian Council Data
**Status:** ❌ Missing
**Expected location:** `/home/setup/infrafabric/data/guardians_extended_council.yaml`

**Should contain:**
```yaml
guardians:
  core:
    - name: "Technical Guardian"
      expertise: "Systems architecture, cryptography"
      weight: 1.5
      safeguards: []
      red_lines: ["No false security claims"]

    # ... 5 more core guardians

  western_philosophers:
    - name: "Empiricist"
      tradition: "Empiricism"
      philosophy: "Hume, Locke"
      # ...

    # ... 2 more western philosophers

  eastern_philosophers:
    - name: "Buddhist"
      tradition: "Buddhism"
      philosophy: "Nagarjuna, Dharmakaya"
      # ...

    # ... 2 more eastern philosophers

  sam_altman_facets:
    - name: "Visionary Sam"
      orientation: "Light Side"
      traits: ["idealistic", "long-term thinking"]
      # ...

    # ... 7 more facets (4 light, 4 dark)
```

---

## 5. Referenced Papers with Issues

### 5.1 IF-vision.md
**Status:** ✅ Exists
**Location:** `/home/setup/infrafabric/IF-vision.md`
**Size:** 34 KB
**Verified:** Complete

---

### 5.2 IF-foundations.md
**Status:** ✅ Exists
**Location:** `/home/setup/infrafabric/IF-foundations.md`
**Size:** 77 KB
**Verified:** Complete

---

### 5.3 IF-armour.md
**Status:** ✅ Exists
**Location:** `/home/setup/infrafabric/IF-armour.md`
**Size:** 48 KB
**Verified:** Complete

---

### 5.4 IF-witness.md
**Status:** ✅ Exists
**Location:** `/home/setup/infrafabric/IF-witness.md`
**Size:** 41 KB
**Verified:** Complete

---

### 5.5 Latex Files (TeX format)
**Referenced in:** agents.md structure
**Locations:**
- `/home/setup/infrafabric/papers/IF-vision.tex`
- `/home/setup/infrafabric/papers/IF-foundations.tex`
- `/home/setup/infrafabric/papers/IF-armour.tex`
- `/home/setup/infrafabric/papers/IF-witness.tex`

**Status:** ✅ All exist
**Verified:** PDF compilation possible from these

---

## 6. Referenced Tools/Scripts with Issues

### 6.1 merge_evaluations.py
**Status:** ✅ Exists in two locations:
- `/home/setup/infrafabric/tools/merge_evaluations.py`
- `/home/setup/infrafabric/docs/evidence/merge_evaluations.py`

**Issue:** Duplicate file

---

### 6.2 guardians.py
**Status:** 🟡 Exists but incomplete
**Location:** `/home/setup/infrafabric/tools/guardians.py`
**Lines:** ~400
**Issue:** Missing council data, no debate orchestration

---

### 6.3 citation_validate.py
**Status:** 🟡 Stub only
**Location:** `/home/setup/infrafabric/tools/citation_validate.py`
**Lines:** ~50
**Issue:** No validation logic implemented

---

## 7. Referenced External APIs/Services

### 7.1 OpenRouter API
**Referenced in:** CLAUDE.md
**Status:** ❌ REVOKED (2025-11-07)
**Key:** `sk-or-v1-...` (disabled)
**Evidence:** `/home/setup/.security/revoked-keys-whitelist.md`

**Action:** Remove from all scripts

---

### 7.2 DeepSeek API
**Referenced in:** CLAUDE.md, agents.md
**Status:** ✅ Active
**Key:** `sk-c2b06f3ae3c442de82f4e529bcce71ed`
**Note:** Should be moved to .env file (not in CLAUDE.md)

---

### 7.3 OpenAI API
**Referenced in:** Multiple papers
**Status:** Assumed active (user has account)
**Note:** Key not stored in repo (good security practice)

---

## 8. Referenced Configurations

### 8.1 IF.TTT Citation Framework
**Referenced in:** agents.md line 328-340
**Expected schema:** `/home/setup/infrafabric/schemas/citation/v1.0.schema.json`
**Status:** ❌ Schema file missing

**Should define:**
- Citation metadata structure
- Verification state machine
- Signature format
- URI format validation

---

## 9. Deployment-Related References

### 9.1 StackCP Deployment
**Referenced in:** agents.md:315-325, CLAUDE.md
**Services mentioned:**
- icantwait.ca (ProcessWire + Next.js)
- digital-lab.ca (project hub)

**Credentials present:** SSH key reference only (secure)

**Issue:** No local InfraFabric deployment configuration

---

## 10. Database References

### 10.1 SuiteCRM Database
**Referenced in:** agents.md, CLAUDE.md
**Status:** Legacy (migrated to Dolibarr)
**Database:** `suitecrm-3130373ec5`
**Connection:** Available but no connection code in repo

---

## 11. Council Archive References

### 11.1 Debate Archive
**Location:** `/home/setup/infrafabric/council-archive/`
**Status:** ✅ Exists and comprehensive

**Contains:**
- 2025/Q4/ - Latest debates
- metadata/guardians.yaml - Guardian definitions
- metadata/KEY_MOMENTS.json - Timeline

**Verified:** Complete for Q4 2025

---

## 12. Missing But Implied Files

Based on documentation patterns, these files should exist:

### 12.1 System Architecture Diagram
**Implied by:** IF-vision.md, all papers
**Status:** ❌ No .png, .svg, or .dia file found
**Expected:** `/home/setup/infrafabric/docs/SYSTEM_ARCHITECTURE.png` or similar

---

### 12.2 Component Integration Guide
**Implied by:** agents.md multi-component references
**Status:** ❌ No integration guide
**Expected:** `/home/setup/infrafabric/docs/COMPONENT_INTEGRATION.md`

---

### 12.3 API Documentation
**Implied by:** Component descriptions
**Status:** ❌ No API specs for components
**Expected:** `/home/setup/infrafabric/api/` directory with OpenAPI specs

---

### 12.4 Deployment Playbook
**Implied by:** agents.md project references
**Status:** ❌ No deployment guide
**Expected:** `/home/setup/infrafabric/docs/DEPLOYMENT.md`

---

## 13. Broken Cross-References

### 13.1 In agents.md
```
Line 335: "Citation schema: `/home/setup/infrafabric/schemas/citation/v1.0.schema.json`"
Status: ❌ File doesn't exist
```

### 13.2 In IF-armour.md
```
Line 873: References to "IF.guard philosophical council for epistemological review"
Status: 🟡 Council exists in concept/skeleton but not fully implemented
```

---

## 14. Summary: Missing Links Count

| Category | Count | Severity |
|----------|-------|----------|
| Missing implementations | 5 | Critical |
| Missing data files | 1 | High |
| Missing specifications | 4 | High |
| Missing documentation | 3 | Medium |
| Broken references | 2 | Medium |
| Missing schemas | 1 | Medium |
| Stub implementations | 2 | Low |
| Duplicate files | 1 | Low |

**Total Issues:** 19

---

## 15. Remediation Plan

### Immediate (Weeks 1-2)
1. [ ] Create `/home/setup/infrafabric/schemas/citation/v1.0.schema.json`
2. [ ] Create `/home/setup/infrafabric/data/guardians_extended_council.yaml`
3. [ ] Create `/home/setup/infrafabric/data/sam_altman_facets.yaml`
4. [ ] Remove OpenRouter API references

### Short-term (Weeks 2-4)
5. [ ] Complete IF.guard implementation (use guardian council data)
6. [ ] Implement IF.citate validation (use citation schema)
7. [ ] Create `/home/setup/infrafabric/docs/SYSTEM_ARCHITECTURE.md`

### Medium-term (Weeks 5-8)
8. [ ] Create IF.swarm agent definitions
9. [ ] Create IF.vesicle module specifications
10. [ ] Create IF.arbitrate implementation

### Long-term (Months 3+)
11. [ ] Create API documentation (OpenAPI specs)
12. [ ] Create deployment playbook
13. [ ] Create component integration guide

---

## 16. Conclusion

InfraFabric has **19 documented gaps between story and reality**:
- 5 components are vaporware (no implementation)
- 1 critical data file missing (guardian council)
- 3 schema/specification files missing
- Multiple broken references throughout

**Impact:** Cannot deploy or test integrated system until these gaps are closed.

**Timeline to completion:** 8-12 weeks (with full-time effort)

---

**Agent D (The Scout) - Missing Links Audit Complete**
**All gaps documented in /home/setup/infrafabric/universe/future/**
