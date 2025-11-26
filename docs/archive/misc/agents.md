# InfraFabric Agent & Project Documentation

**Version:** 1.0
**Last Updated:** 2025-11-15
**Purpose:** Central reference for InfraFabric components, evaluations, and project state

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
- Strong philosophical foundation (IF.philosophy database)
- Well-documented IF.* components
- Minimal executable code in main repo
- Implementation exists in external repos only

**Report:** `docs/evidence/INFRAFABRIC_CONSENSUS_REPORT.md`

---

## IF.* Component Status

**Source:** `docs/evidence/IF_COMPONENT_INVENTORY.yaml` (from Codex evaluation)

### Implemented (with working code)

1. **IF.yologuard** - AI-generated code detector
   - Location: `src/infrafabric/core/security/yologuard.py`
   - Status: Production-ready, 100× false-positive reduction
   - Evidence: Evaluation artifacts in `code/yologuard/`

2. **IF.search** - 8-pass investigative methodology
   - Documentation: `IF-foundations.md:519-1034`
   - Status: Implemented, 87% confidence across 847 data points

### Partial (design exists, limited implementation)

3. **IF.optimise** - Token efficiency framework
   - Design: `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md:1-135`
   - Status: Well-defined, needs orchestration pipeline

4. **IF.citate** - Citation validation
   - Design: `tools/citation_validate.py` (referenced)
   - Status: Schema exists, validation incomplete

5. **IF.philosophy** - Philosopher database
   - Data: `philosophy/IF.philosophy-database.yaml`
   - Status: Complete database, query tools needed

### Vaporware (mentioned but no spec/code)

6. **IF.guard** - Guardian council framework
   - Mentions: Throughout papers and annexes
   - Status: Conceptual only, no implementation

7. **IF.sam** - 16-facet council
   - Mentions: Documentation
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

## IF.TTT Traceability Framework

**Status:** MANDATORY for all agent operations

**Principles:**
- Every claim must link to observable source (file:line, git commit, citation)
- Generate `if://citation/uuid` for findings
- Citation schema: `schemas/citation/v1.0.schema.json`
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
| IF.search | `IF-foundations.md:519-1034` | External | Implemented |
| IF.optimise | `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md` | Policy only | Partial |
| IF.yologuard | `IF-armour.md` | `core/security/yologuard.py` | Production |
| IF.philosophy | Papers | `philosophy/IF.philosophy-database.yaml` | Data only |
| IF.guard | Papers | None | Vaporware |
| IF.sam | Documentation | None | Vaporware |
| IF.citate | Mentions | `tools/citation_validate.py` | Partial |

---

## Session 2025-11-25: Operation Universe 4D Restructuring

### Achievements:
1. **Council Archive Complete**: 15+ debates archived in European Court style with full deliberation transcripts
2. **4D Universe Created**: Restructured entire InfraFabric repo into SPACE/TIME/FEATURE/FUTURE dimensions with cross-referenced navigation
3. **Jack Clark Origin Story**: Extracted "Page Zero" foundational narrative from "Seeking Confirmation" transcript
4. **SQLite Export**: Single-file database (900KB) comprehensively indexed for Gemini review
5. **IF.sam → IF.ceo Rename**: Global update across all documentation and component references
6. **Redis Deduplicated**: 716 unique keys, 18.3MB footprint (optimized from 723 keys)

### Key Files Created:
- `universe/` - Complete 4D dimensional structure
- `universe/time/long_term/origin_story/00_The_Jack_Clark_Inquiry.md` - Page Zero foundational document
- `universe/feature/ethics/seat_01_kant.md` - Kant Guardian council seat
- `universe/feature/ethics/seat_12_confucius.md` - Confucius Guardian council seat
- `universe/feature/governance/constitution/budget.md` - Budget Veto Protocol framework

### Gap Analysis Results:
- **5 IMPLEMENTED (29%)**: IF.yologuard, IF.search, IF.philosophy, IF.ground, IF.persona
- **4 PARTIAL (24%)**: IF.optimise, IF.citate, IF.trace, IF.forge
- **5 PLANNED (29%)**: IF.guard, IF.ceo, IF.swarm, IF.arbitrate, IF.vesicle
- **3 VAPORWARE (18%)**: IF.quantum, IF.core, IF.witness

---

**Last Session:** Multi-evaluator assessment complete (3 evaluators, consensus generated) + File consolidation analysis (366 files, 59 duplicate groups, 8.31 MB identified)
**Next Session Options:** Execute file consolidation / Debug P0 gaps / Add Claude evaluation / Citation cleanup
**Git Status:** Clean, all evaluation artifacts and consolidation tools committed to master
**Smart Integration:** Ready for execution (`./smart_integrate.sh execute` to recover 8.31 MB)
