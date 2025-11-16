# InfraFabric Agent & Project Documentation

**Version:** 1.0
**Last Updated:** 2025-11-15
**Purpose:** Central reference for all InfraFabric components, evaluations, and project state

---

## Project Overview

InfraFabric is a research project on AI agent coordination and civilizational resilience, featuring:
- **Philosophical Foundation:** 12-philosopher database grounding IF.* components
- **Epistemological Framework:** IF.ground (8 anti-hallucination principles)
- **Research Methodology:** IF.search (8-pass investigative approach)
- **Token Efficiency:** IF.optimise (87-90% cost reduction via Haiku swarms)
- **Production Component:** IF.yologuard (100× false-positive reduction)

**Repository:** https://github.com/dannystocker/infrafabric
**Status:** Well-documented research with limited in-repo implementation

---

## File Consolidation (2025-11-15)

### Duplicate Detection & Integration System

**Analysis Scope:**
- 366 total files scanned across entire repository
- 59 duplicate groups identified (175 total duplicate files)
- 8.31 MB total recoverable space (7.93 MB after consolidation)
- Categories: documentation, data (JSON), misc, code

**Top Duplicates by File Count:**
1. `infrafabric-complete-v7.01` variants: 15 copies (0.09 MB per group)
2. `infrafabric-annexes-v7.01` variants: 13 copies (0.11 MB per group)
3. IF.yologuard documentation: 6 variants (0.22 MB)
4. Chat-IFpersonality variants: 4 copies (0.18 MB)
5. JSON data files (overview, prospect outreach): 2-6 copies per file

**Smart Integration System:**

Location: `smart_integrate.sh` (Bash script, 150+ lines)

Features:
- SHA256 content-based deduplication (not filename-based)
- mtime-based conflict resolution (keeps newest, archives older)
- Dry-run mode (safe preview before execution)
- Color-coded logging with statistics
- Timestamp-based archive organization

**Integration Report:**

Location: `integration_duplicates_report.json` (comprehensive analysis)

Contains:
- Duplicate group hashes and timestamps
- File categories and sizes per group
- mtime-based resolution decisions
- Recovery statistics and recovery bytes
- Ready for immediate execution

**Next Step:** Run `./smart_integrate.sh execute` to consolidate (recovers 8.31 MB)

---

## Multi-Evaluator Assessment (2025-11-15)

### Three Independent Evaluations Completed

**Evaluator 1: GPT-5.1 Desktop**
- Overall Score: 6.2/10
- Strength: Comprehensive metrics and URL audit
- File: `docs/evidence/INFRAFABRIC_SINGLE_EVAL.yaml`

**Evaluator 2: Codex (GPT-5.1 CLI)**
- Overall Score: 4.5/10 (most critical)
- Strength: Detailed IF.* component inventory
- File: `docs/evidence/INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml`

**Evaluator 3: Gemini AI Agent**
- Qualitative assessment (no numeric scores)
- Strength: Alternative perspective, different schema
- File: `docs/evidence/infrafabric_eval_Gemini_20251115_103000.yaml`

### Consensus Findings (3 Evaluators)

**Scores (Average):**
- Overall: 5.35/10
- Substance: 7.0/10 (strong conceptual foundation)
- Novelty: 7.5/10 (genuinely new ideas)
- Code Quality: Low (implementation gaps)

**100% Agreement:**
- ✅ Strong philosophical foundation (IF.philosophy database)
- ✅ Well-documented IF.* components
- ❌ Minimal executable code in main repo
- ❌ Implementation exists in external repos only

**Report:** `docs/evidence/INFRAFABRIC_CONSENSUS_REPORT.md`

---

## IF.* Component Status

**Source:** `docs/evidence/IF_COMPONENT_INVENTORY.yaml` (from Codex evaluation)

### ✅ Implemented (with working code)

1. **IF.yologuard** - AI-generated code detector
   - Location: `mcp-multiagent-bridge` repo
   - Status: Production-ready, 100× false-positive reduction
   - Evidence: Evaluation artifacts in `code/yologuard/`

2. **IF.search** - 8-pass investigative methodology
   - Location: `mcp-multiagent-bridge/IF.search.py`
   - Documentation: `IF-foundations.md:519-1034`
   - Status: Implemented, 87% confidence across 847 data points

### 🟡 Partial (design exists, limited implementation)

3. **IF.optimise** - Token efficiency framework
   - Design: `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md:1-135`
   - Policy: `.claude/CLAUDE.md:1-180`
   - Status: Well-defined, needs orchestration pipeline

4. **IF.citate** - Citation validation
   - Design: `tools/citation_validate.py` (referenced)
   - Status: Schema exists, validation incomplete

5. **IF.philosophy** - Philosopher database
   - Data: `philosophy/IF.philosophy-database.yaml`
   - Status: Complete database, query tools needed

### ❌ Vaporware (mentioned but no spec/code)

6. **IF.guard** - Guardian council framework
   - Mentions: Throughout papers and annexes
   - Status: Conceptual only, no implementation

7. **IF.sam** - 16-facet Sam Altman council
   - Mentions: `.claude/CLAUDE.md`
   - Status: Idea only, no spec

8. **IF.swarm** - Multi-agent coordination
   - Mentions: Various papers
   - Status: Conceptual discussions only

**Full Inventory:** See `docs/evidence/IF_COMPONENT_INVENTORY.yaml` for all 47 components

---

## Documentation Structure

### Core Papers (4 main papers)

1. **IF-vision.md** (34KB)
   - Overview of all IF.* components
   - Guardian Council framework
   - Manic/depressive/dream/reward phases

2. **IF-foundations.md** (77KB)
   - IF.ground: 8 anti-hallucination principles
   - IF.search: 8-pass investigative methodology
   - IF.persona: Bloom pattern agent characterization

3. **IF-armour.md** (48KB)
   - IF.yologuard production validation
   - 100× false-positive reduction claims
   - Benchmark results

4. **IF-witness.md** (41KB)
   - Observability and tracing
   - IF.trace component design

### Annexes (supplementary documentation)

- **ANNEX-N-IF-OPTIMISE-FRAMEWORK.md** - Token efficiency policy + proof
- **ANNEX-P-GPT5-REFLEXION-CYCLE.md** - 8 improvement recommendations
- **COMPLETE-SOURCE-INDEX.md** - Navigation guide to all content

### Philosophy Database

**Location:** `philosophy/IF.philosophy-database.yaml`

**Contents:**
- 12 philosophers mapped to IF.* components
- 3 Western traditions (Empiricism, Rationalism, Pragmatism)
- 3 Eastern traditions (Buddhism, Daoism, Confucianism)
- File:line references to all papers

---

## Evaluation Artifacts

### Metrics & Audits

**Code Metrics** (`docs/evidence/infrafabric_metrics.json`):
```json
{
  "total_files": 127,
  "total_lines_code": 2847,
  "total_lines_docs": 25691,
  "code_to_docs_ratio": 0.11,
  "languages": {
    "Python": 1823,
    "JavaScript": 891,
    "Markdown": 25691,
    "YAML": 133
  },
  "test_files": 0,
  "test_lines": 0
}
```

**URL Audit** (`docs/evidence/infrafabric_url_manifest.csv`):
- 16KB CSV with every HTTP(S) URL found in codebase
- Includes file path, line number, context
- Ready for 404 checking and citation verification

**File Inventory** (`docs/evidence/infrafabric_file_inventory.csv`):
- Complete list of all files with sizes
- 1.3KB CSV

### Debug Prompt

**Location:** `docs/evidence/DEBUG_SESSION_PROMPT_GPT-5.1-CODEX-CLI_20251115T145456Z.md`

**Purpose:** Prioritized workflow to address P0/P1/P2 gaps found in evaluation

**Key Recommendations:**
1. Add IF.* status dashboard to README
2. Implement missing components (IF.guard, IF.sam, IF.swarm)
3. Consolidate scattered documentation
4. Add working code examples
5. Create integration tests

---

## Related Projects

### 1. NaviDocs
**Path:** `/home/setup/navidocs`
**Repo:** https://github.com/dannystocker/navidocs
**Status:** 65% complete MVP (boat documentation management platform)

**Recent Work:**
- Feature catalogue created: https://digital-lab.ca/navidocs/builder/NAVIDOCS_FEATURE_CATALOGUE.md
- 8 critical security/UX fixes documented
- E2E tests passing (100% success rate)

### 2. InfraFabric Core
**Path:** `/home/setup/infrafabric-core`
**Repo:** https://github.com/dannystocker/infrafabric-core
**Purpose:** Research papers repository

### 3. MCP Multiagent Bridge
**External Repo** (not on local machine)
**Contains:** IF.yologuard + IF.search implementations

### 4. GGQ CRM
**Path:** `/home/setup/ggq-crm`
**Repo:** http://localhost:4000/dannystocker/ggq-crm (Gitea)
**Status:** Dolibarr 22.0 production deployment complete (2025-11-15)

**Migration History:**
- Phase 1: SuiteCRM 8 installation (23,581 records imported from calendar + business DB)
- Phase 2: Dolibarr migration (better UX for novice user Marc Gauvran)

**Current Production System: Dolibarr**
- URL: https://digital-lab.ca/ggq/doli/htdocs/
- Version: 22.0.0 (upgraded from 21.0.2)
- Language: French (fr_FR)
- Users: Marc (marc/marc123), Admin (admin/admin123)
- Data: 1,404 companies (404 prospects + 1,000 customers)

**Databases:**
- Dolibarr: `dolibarr-353037376a57` @ `sdb-78.hosting.stackcp.net`
- SuiteCRM (legacy): `suitecrm-3130373ec5` @ `shareddb-n.hosting.stackcp.net`

**Key Files:**
- Session handover: `/home/setup/ggq-crm/SESSION-HANDOVER.md`
- Import script: `/home/setup/ggq-crm/import_to_dolibarr.py`
- Source data: `/home/setup/ggq-crm/data/calendars/` (9,094 calendar entries)

**Pending Work:**
- P0: Marc UI testing and feedback
- P1: Import remaining 5,157 customers + 11,091 contacts + timeline data
- P2: Reset passwords to secure values after testing
- P3: Build Google Calendar ↔ Dolibarr bidirectional sync (40-60 hours)

---

## Key Contacts & Credentials

### Git Repositories

**GitHub:**
- User: dannystocker
- Repos: infrafabric, infrafabric-core, navidocs

**Local Gitea:**
- URL: http://localhost:4000/
- Admin: ggq-admin / Admin_GGQ-2025!
- User: dannystocker / @@Gitea305$$

### External Services

**OpenRouter API:**
- Key: `sk-or-v1-...` (REVOKED 2025-11-07, exposed in GitHub)
- Status: Disabled, see `/home/setup/.security/revoked-keys-whitelist.md`

**DeepSeek API:**
- Key: `sk-c2b06f3ae3c442de82f4e529bcce71ed`

### StackCP (Hosting)

**SSH Alias:** `stackcp`
- Host: ssh.gb.stackcp.com
- User: digital-lab.ca
- Key: `~/.ssh/icw_stackcp_ed25519`

**Web Roots:**
- icantwait.ca: `~/public_html/icantwait.ca/`
- digital-lab.ca: `~/public_html/digital-lab.ca/`

---

## IF.TTT Traceability Framework

**Status:** MANDATORY for all agent operations

**Principles:**
- Every claim must link to observable source (file:line, git commit, citation)
- Generate `if://citation/uuid` for findings
- Citation schema: `/home/setup/infrafabric/schemas/citation/v1.0.schema.json`
- Validation: `python tools/citation_validate.py citations/session-<date>.json`

**Citation States:**
- `unverified` → `verified` → `disputed` → `revoked`

---

## Session Handover System

**3-Tier Architecture:**

**Tier 1:** `SESSION-RESUME.md` (<2K tokens)
- Current mission, git state, blockers, next action

**Tier 2:** `agents.md` (this file) (<10K tokens)
- IF.* component catalog, evaluations, project overview

**Tier 3:** Deep Archives (Haiku agents only)
- Papers (77KB each), Evidence (102+ docs), never read directly

**Update Triggers:**
- `/resume` command
- Context window approaching 150K tokens
- Major decisions (Guardian Council votes)
- Session boundaries (end of day, machine change)
- Git commits to main documentation

---

## Evaluation Framework (For Future Assessments)

**Prompt Location:** `docs/evidence/INFRAFABRIC_EVAL_PASTE_PROMPT.txt`

**Features:**
- Standardized YAML schema for all evaluators
- Mandatory citation verification (DOI/URL checks)
- README accuracy audit
- IF.* component inventory
- P0/P1/P2 gap analysis
- Market fit assessment

**Merger Tool:** `docs/evidence/merge_evaluations.py`
- Merges multiple YAML evaluations
- Calculates consensus scores
- Identifies outliers
- Ranks issues by agreement %

**Usage:**
```bash
python3 merge_evaluations.py eval1.yaml eval2.yaml eval3.yaml
# Generates: INFRAFABRIC_CONSENSUS_REPORT.md
```

---

## Quick Reference: Component Locations

| Component | Documentation | Implementation | Status |
|-----------|---------------|----------------|--------|
| IF.search | `IF-foundations.md:519-1034` | `mcp-multiagent-bridge/` | ✅ Implemented |
| IF.optimise | `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md` | Policy only | 🟡 Partial |
| IF.yologuard | `IF-armour.md` | `mcp-multiagent-bridge/` | ✅ Production |
| IF.philosophy | Papers | `philosophy/IF.philosophy-database.yaml` | 🟡 Data only |
| IF.guard | Papers | None | ❌ Vaporware |
| IF.sam | `.claude/CLAUDE.md` | None | ❌ Vaporware |
| IF.citate | Mentions | `tools/citation_validate.py` | 🟡 Partial |

---

**Last Session:** Multi-evaluator assessment complete (3 evaluators, consensus generated) + File consolidation analysis (366 files, 59 duplicate groups, 8.31 MB identified)
**Next Session Options:** Execute file consolidation / Debug P0 gaps / Add Claude evaluation / Citation cleanup
**Git Status:** Clean, all evaluation artifacts and consolidation tools committed to master
**Smart Integration:** Ready for execution (`./smart_integrate.sh execute` to recover 8.31 MB)

---

## Gedimat Logistics Intelligence Test (ACTIVE)

**Status:** V3 Final Sprint Ready (90/100 → 95%+ target)
**Date Started:** 2025-11-16
**Location:** `/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/`
**Branch:** `gedimat-v3-final`

### Project Overview

**Purpose:** Real-world test of IF.search 8-pass methodology + IF.TTT compliance on French B2B logistics optimization.

**Client Context:**
- Gedimat: Building materials distributor (3 depots: Lieu, Méru, Breuilpont)
- Problem: High external freight costs (>10t shipments via Médiafret), manual coordination
- Coordinator: Angélique (4 years experience)
- Deliverable: C-suite Board presentation with ROI recommendations

### Score Evolution

**V1 (Initial):** 86/100 methodology, 40/100 financials
- Problem: 8 unsourced "credibility bombs" (50K€ gains, 10× ROI, 30K€ baseline)
- Audit: 23 total unsourced claims identified

**V2 (Factual Grounded):** 78/100 (Codex GPT-4o) / 90/100 (GPT 5.1 high)
- Fix: Eliminated all unsourced Gedimat projections
- Replaced with: Data collection forms, external benchmarks, calculation formulas
- Created: 10 audit files, vendor pricing research

**V3 (Target):** 95%+ 
- Fix: 4 remaining GPT 5.1 concerns (temper claims, Board summary, move V1 tables, French corrections)
- Agent research: 6 Haiku agents (<$1), verified benchmarks + vendor pricing
- Deployment: Claude Cloud sprint with 40 Haiku agents

### External Evaluations

**Codex (GPT-4o) - 2025-11-16:**
- Score: 78/100
- Conformité IF.TTT: 78/100 (formulas present but costs declarative)
- Qualité preuves: 70/100 (citations textual, no URLs)
- Méthodologie: 86/100 (IF.search architecture coherent)
- Français: 72/100 (anglicisms persist)
- Critical: Benchmarks unverifiable, costs unsourced

**GPT 5.1 High - 2025-11-16:**
- Score: 90/100
- Conformité IF.TTT: 88/100
- Qualité preuves: 87/100
- Méthodologie: 95/100 (highest score)
- Actionnabilité: 92/100
- Français: 92/100
- Gap: 4 issues (impact claims, Board summary, V1 tables, anglicisms)

**Gemini (2.0-flash-exp):**
- Validation: Successfully generated 60-85 page structured dossier
- Result: Proves V2 prompt is executable and produces coherent output

### V3 Agent Deployment (6 Haiku, 30 minutes, <$1)

**Agent 1: Point P Benchmark Verification**
- Status: ❌ NOT FOUND (LSA Conso Mars 2023 p.34 unverifiable)
- Solution: Saint-Gobain Transport Control Tower (13% CO2, $10M savings)
- File: `benchmarks/POINT_P_ALTERNATIVE_VERIFIED.md`

**Agent 2: Leroy Merlin Benchmark Verification**
- Status: ⚠️ PARTIAL (ROI 8.5× not found in ADEO reports)
- Verified: 55% e-commerce growth, 11-15% cost reduction, €40M investment
- URLs: ADEO Overview 2023 + Supply Chain Magazine Oct 2022
- File: `benchmarks/LEROY_MERLIN_2021_VERIFIED.md`

**Agent 3: Castorama Benchmark Verification**
- Status: ❌ NOT FOUND (Internal Analytics unverifiable)
- Alternative: Kingfisher Group NPS 50 (parent company)
- Recommendation: REMOVE (B2C vs B2B mismatch)
- File: `benchmarks/KINGFISHER_GROUP_NPS_VERIFIED.md`

**Agent 4: Vendor Cost Sourcing**
- Excel VBA: €420-€700 (Codeur.com €140/day × 3-5 days)
- Custom Dev: €3,830-€5,745 (Free-Work €383/day × 10-15 days)
- WMS License: €30,000/year (Generix Group public pricing)
- WMS Implementation: €25K-€250K (Sitaci market guide)
- TMS: Quote required via RFP (no public pricing)

**Agent 5: French Language Corrections**
- Found: 40 anglicisms
- Priority: Quick Win → Gain Rapide, dashboard → tableau de bord, KPI → Indicateurs Clés
- Deliverable: Complete sed script for batch replacement

**Agent 6: GitHub Deployment Package**
- Structure: 19-file specification
- READMEs: Comprehensive (7,500 words) + one-page checklist
- Files: V3_GITHUB_DEPLOYMENT_PACKAGE.md, README_CLAUDE_CODE_CLOUD.md, QUICK_START_GITHUB.md

### V3 Remaining Work (4 Issues, 2-3 hours)

**Issue 1: Impact Claims Need Tempering (HIGH)**
- Problem: "-50% retards", "-12-15% affrètement" stated as facts
- Fix: Add "potentiel / à confirmer après pilote" qualifiers
- File: `GPT5_VS_V3_FIXES_ANALYSIS.md` section A1

**Issue 2: Board Executive Summary (HIGH)**
- Problem: Too much IF.* jargon (40 agents, 26 voices)
- Fix: Create 1-page C-suite summary (business metrics, no methodology)
- File: New `EXECUTIVE_SUMMARY_BOARD.md`

**Issue 3: V1 Tables Still Visible (MEDIUM)**
- Problem: Historical unsourced numbers confuse readers
- Fix: Move to `audit/V1_V2_EVOLUTION.md`

**Issue 4: Anglicisms Remain (MEDIUM)**
- Problem: "Quick Win", "dashboard", "KPI" in French document
- Fix: Apply Agent 5 sed script (40 replacements)

### Files Created (15 key files)

**Evaluation Results:**
1. `session-output/gedimat_eval_codex-gpt-5_v1_20251116T195639Z.md` (Codex 78/100)
2. `session-output/gedimat_eval_gpt-5.1_v2_20251116T202446Z.md` (GPT 5.1 90/100)
3. `EVALUATION_FINDINGS_SUMMARY.md` (comprehensive analysis)
4. `GPT5_VS_V3_FIXES_ANALYSIS.md` (issue-by-issue breakdown)

**Verified Benchmarks:**
5. `benchmarks/POINT_P_ALTERNATIVE_VERIFIED.md`
6. `benchmarks/LEROY_MERLIN_2021_VERIFIED.md`
7. `benchmarks/KINGFISHER_GROUP_NPS_VERIFIED.md`
8. `benchmarks/README_BENCHMARKS.md`

**V3 Deployment:**
9. `CLAUDE_CLOUD_V3_SPRINT.md` (detailed technical sprint)
10. `CLAUDE_CLOUD_V3_SIMPLE.md` ← **Main deployment prompt** (self-contained, no IF.* context)

**V2 Base:**
11. `PROMPT_V2_FACTUAL_GROUNDED.md` (48KB, 1,060 lines)
12. `audit/` directory (10 files: AUDIT_UNSOURCED_NUMBERS.md, QUICK_REFERENCE, etc.)

**Orientation:**
13. `README_CLAUDE_CODE_CLOUD.md` (569 lines, comprehensive)
14. `QUICK_START_GITHUB.md` (200 lines, one-page)
15. `V3_GITHUB_DEPLOYMENT_PACKAGE.md` (1,278 lines, complete spec)

### Lessons Learned

1. **External validation catches blind spots** - Codex found issues internal review missed
2. **Benchmarks must be verifiable** - "LSA Conso p.34" unverifiable → credibility destroyed
3. **Vendor costs need sources** - CFO will question unsourced "5K€"
4. **French quality matters** - Anglicisms → immediate C-suite credibility loss
5. **IF.TTT is mandatory** - Single unverifiable claim → entire dossier questioned
6. **Haiku agents cost-effective** - $0.15 for 6 agents × 5-10 min each
7. **IF.optimise works** - <$1 total for complete external validation + fixes
8. **GPT 5.1 high > Codex GPT-4o** - 90/100 vs 78/100, caught nuanced presentation issues

### Next Steps

1. **Push branch `gedimat-v3-final` to GitHub** (clean, no Slack token)
2. **Provide user:**
   - GitHub raw URL: `https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v3-final/intelligence-tests/gedimat-logistics-fr/CLAUDE_CLOUD_V3_SIMPLE.md`
   - One-line instruction for Claude Cloud
3. **Claude Cloud executes:** 40 Haiku agents, 2-3 hours, 4 focused fixes
4. **Re-evaluate:** GPT 5.1 to confirm ≥95/100
5. **Deploy:** Merge to main if successful

### Budget Summary

**Total Spent:** <$1 USD
- Codex evaluation (GPT-4o): ~$0.50
- Gemini evaluation (2.0-flash-exp): ~$0.30
- 6 Haiku agents (benchmarks, costs, French): ~$0.15

**Remaining Budget:** ~$2 USD (40 Haiku agents for V3 final sprint)

**ROI Demonstration:**
- Methodology validation: IF.search scored 86-95/100 (proves framework works)
- Cost efficiency: External validation + 6 agents + full V3 spec = <$1
- Quality improvement: 78 → 90 → 95%+ achievable with systematic fixes
- Proves IF.optimise: Haiku for labor, Sonnet for architecture, external evaluators for validation

