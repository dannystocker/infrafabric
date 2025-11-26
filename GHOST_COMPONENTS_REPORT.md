# InfraFabric Ghost Components Report
## Cross-reference Analysis: docs/ vs papers/ vs src/
**Generated: 2025-11-26**

---

## Executive Summary

This report identifies "ghost components" - IF.* components that exist in documentation or papers but lack implementations, or exist in code but lack documentation. Analysis of 38 unique IF. components across three zones reveals a critical documentation-code gap.

**Key Finding:** 94.7% (36/38) of IF. components lack full integration across all three layers (documentation, papers, and source code).

---

## Quick Stats

| Metric | Count |
|--------|-------|
| Total unique IF. components | 38 |
| Fully integrated (docs + papers + code) | 1 |
| Partially implemented (stub code exists) | 1 |
| Design-only (documented but not coded) | 20 |
| Vaporware (mentioned only) | 13 |
| Code-only (implemented but not documented) | 1 |
| **Implementation completion ratio** | **5.3%** |

---

## Component Status Breakdown

### Category 1: Fully Integrated (1)
Components with complete documentation, design, and implementation.

**IF.yologuard** - Production Ready
- Location: `/home/user/infrafabric/src/infrafabric/core/security/yologuard.py`
- Status: Version 3.0 (Confucian Relationship-Based Secret Detector)
- LOC: 672
- Features: Shannon entropy detection, Base64/hex decoding, JSON/XML parsing, Wu Lun relationship mapping
- Philosophy: Grounded in Confucianism (5 Wu Lun relationships)
- Documentation: Extensive (philosophy database, papers, design docs)
- Evaluation: 98.96% recall claimed

---

### Category 2: Code-Only (1)
Implemented but missing from conceptual documentation.

**IF.librarian** - Archive Node
- Location: `/home/user/infrafabric/src/infrafabric/core/services/librarian.py`
- Status: Fully implemented
- LOC: 366
- Features: Gemini API integration, Redis backing, 1M token context window
- Philosophy: NOT in IF.philosophy-database.yaml (documentation gap)
- Classes: `GeminiLibrarian`, `ArchiveQuery`, `ArchiveFinding`
- Issue: Working implementation discovered but not catalogued

---

### Category 3: Documented-Only (20)
Extensively designed but with zero implementation.

| Component | Documentation | Status | Blocker |
|-----------|---------------|--------|---------|
| **IF.ground** | IF-foundations.tex (525 lines) | 8 anti-hallucination principles; no guardrails code | Philosophy prose only |
| **IF.search** | IF-foundations.tex (336 lines) | Eight-pass investigative process; zero automation | No orchestration scripts |
| **IF.persona** | IF-foundations.tex (125 lines) | Bloom pattern personas; no runtime linkage | Character library only markdown |
| **IF.armour** | IF-armour.tex (paper) | Four-tier defense spec; no code | Detection heuristics described only |
| **IF.witness** | IF-witness.tex (113 lines) | Meta-validation methodology; MARL tooling missing | **IF.forge missing (blocker)** |
| **IF.optimise** | ANNEX-N Framework | Policy + pricing proofs; telemetry missing | Token accounting service undefined |
| **IF.guard** | Guardian Council debates | Governance logic in external archive | **EVALUATION CONTRADICTION: Claims 73% implemented but no src/ code** |
| **IF.citate** | docs/evidence | Citation validation framework | **EVALUATION CONTRADICTION: Claims 58% implemented but no src/ code** |
| **IF.sam** | EVALUATION_QUICKSTART.md | Design exists (referenced spec) | Requires OpenAI API; P1 priority; 1-2 weeks effort |

**6 More (documented-only):** IF.chase, IF.reflect, IF.garp, IF.quiet, IF.constitution, IF.federate (all mentioned in papers; no code)

---

### Category 4: Vaporware (13)
Mentioned in docs/papers but with no specification or code.

| Component | Source | Status |
|-----------|--------|--------|
| **IF.router** | README.md, IF-vision.tex | Fabric-aware routing (NVLink); no spec |
| **IF.memory** | README.md | Mentioned component index; no details |
| **IF.trace** | README.md, IF-vision.tex | Immutable audit logging; no schema |
| **IF.pulse** | README.md | Health monitoring; referenced only by name |
| **IF.ceo** | README.md | Annex reference; governance facets undefined |
| **IF.vesicle** | README.md, IF-vision.tex | Neurogenesis metaphor (89.1% approval); no design doc |
| **IF.kernel** | README.md | KERNEL integration promised; annex missing |
| **IF.swarm** | README.md | Flagged as vaporware (2/3 evaluators agree) |
| **IF.forge** | IF-witness.tex | **CRITICAL BLOCKER for IF.witness**; stage automation absent |
| **IF.marl** | IF-witness.tex | Multi-agent RL framework; no spec |
| **IF.mcp** | docs/evidence | MCP integration reference only |
| **IF.core** | docs/evidence | Vague core component reference |
| **IF.amplify** | docs/evidence | Amplification component mentioned |

---

### Category 5: Stub-Only (1)
Minimal implementations with NotImplementedError.

**OCRWorker** - Processing Pipeline Stub
- Location: `/home/user/infrafabric/src/infrafabric/core/workers/ocr_worker.py`
- Status: 50 lines, placeholder with NotImplementedError
- Specification: `/home/setup/navidocs/intelligence/session-2/document-versioning-spec.md`
- Queue: `bull:ocr-processing:*` (9 Redis keys active as of 2025-11-25)
- Issue: Stub awaiting implementation (Tesseract.js + pdfjs-dist)

---

## Critical Gaps & Contradictions

### Gap 1: Evaluation False Positives
**Severity: HIGH**

Two components are reported as "implemented" by evaluators despite having no source code:

- **IF.guard** - Evaluations claim "✅ Implemented (3/3 evaluators, 73% complete)"
  - Reality: No Python implementation found in `/home/user/infrafabric/src/`
  - Evidence: `docs/evidence/EVALUATION_QUICKSTART.md:48`
  - Impact: False confidence in implementation status

- **IF.citate** - Evaluations claim "✅ Implemented (3/3 evaluators, 58% complete)"
  - Reality: No Python implementation found in `/home/user/infrafabric/src/`
  - Evidence: `docs/evidence/EVALUATION_QUICKSTART.md:49`
  - Impact: False confidence in implementation status

**Recommendation:** Either create stub implementations or correct evaluation reports.

---

### Gap 2: Unsatisfiable Dependencies
**Severity: CRITICAL**

Components depend on other missing components:

- **IF.witness** depends on **IF.forge**
  - IF.forge (stage automation) does not exist
  - Impact: IF.witness cannot be implemented as designed
  - Blocker noted in: `docs/evidence/IF_COMPONENT_INVENTORY.yaml:38`

- **IF.optimise** depends on undefined token accounting service
  - No specification for "token accounting service"
  - No model routing hooks defined
  - Impact: Cannot create token-efficient routing

---

### Gap 3: Documentation-Code Divergence
**Severity: HIGH**

**IF.librarian** - Fully implemented but never documented:
- 366 lines of production-ready code
- Not in philosophy database
- Not in any paper
- Only docstring mentioning Gemini integration
- Impact: Component invisibility despite being functional

---

### Gap 4: External Repository Dependencies
**Severity: MEDIUM**

Core implementations reference external "mcp-multiagent-bridge" repository:
- `IF.yologuard_v1.py` (31.2% recall baseline)
- `IF.yologuard_v3.py` (98.96% recall with Wu Lun)
- Files at: https://github.com/dannystocker/infrafabric/blob/master/projects/yologuard/versions/

Impact: Cannot reproduce results from infrafabric repo alone.

---

### Gap 5: Prose Design Without Executable Specification
**Severity: MEDIUM**

Several components have philosophical grounding and narrative design but no machine-executable specification:

- **IF.search** - 8-pass methodology described in prose; no workflow orchestration
- **IF.persona** - Bloom patterns mapped to philosophers; no character library
- **IF.guard** - Guardian council governance as debate transcripts; no logic rules

Impact: Developers cannot programmatically instantiate designs.

---

## Philosophical Grounding Analysis

**Philosophers mapped to components (from IF.philosophy-database.yaml):**

- **Epictetus (Stoicism):** IF.quiet, IF.witness, IF.trace
- **John Locke (Empiricism):** IF.ground, IF.armour, IF.search
- **Charles Peirce (Pragmatism/Fallibilism):** IF.ground, IF.reflect, IF.search
- **Vienna Circle (Verificationism):** IF.ground, IF.search, IF.armour
- **Pierre Duhem (Philosophy of Science):** IF.ground, IF.search
- **Willard Quine (Coherentism):** IF.ground, IF.guardian, IF.search
- **William James (Pragmatism):** IF.ground, IF.optimise, IF.search
- **John Dewey (Pragmatism):** IF.ground, IF.search
- **Karl Popper (Critical Rationalism):** IF.ground, IF.guardian, IF.search, IF.armour
- **Buddha (Buddhism):** IF.guardian, IF.witness
- **Lao Tzu (Daoism):** IF.guardian, IF.witness

**Observation:** Heavy philosophy concentration on IF.ground, IF.search (core-level components) with less depth on mid-level orchestration components (IF.trace, IF.router, IF.optimise).

---

## Recommendations by Priority

### P0: Critical (Immediate - Week 1)
1. **Resolve IF.guard/IF.citate evaluation contradiction**
   - Either: Implement Python stubs and commit to src/
   - Or: Correct evaluation reports to reflect "documented only" status
   - Impact: Restores credibility of evaluation process

2. **Document IF.librarian in philosophy database**
   - Add to `philosophy/IF.philosophy-database.yaml`
   - Assign grounding philosophers (e.g., Plato: Memory/Archive)
   - Impact: Closes documentation gap for working code

3. **Create IF.forge stub OR decouple IF.witness**
   - Option A: Create minimal IF.forge (stage automation framework)
   - Option B: Refactor IF.witness to not depend on IF.forge
   - Impact: Unblocks IF.witness implementation

### P1: High (Short-term - Weeks 2-4)
1. **Implement IF.sam (1-2 weeks)**
   - Design file exists (referenced as `IF-sam-specification.md`)
   - Requires: OpenAI API integration
   - Priority per 3/3 evaluators

2. **Convert IF.search prose to executable workflow**
   - 8-pass methodology exists (IF-foundations.tex)
   - Create orchestration script in `/src/infrafabric/core/search/`
   - Integrate tool versioning

3. **Create schema definitions for IF.trace**
   - Immutable audit logging specification
   - Redis or database-agnostic design

### P2: Medium (Medium-term - Months 1-2)
1. **Refactor documentation to separate meta-components from runtime components**
   - Papers (IF.vision, IF.foundations, IF.armour, IF.witness) are not components
   - Create separate "Framework" vs "Component" taxonomy

2. **Build interdependency map**
   - Which components depend on which
   - Identify circular dependencies
   - Map blocking chains

3. **Implement minimal versions of top 5 vaporware**
   - IF.router (fabric routing stub)
   - IF.memory (key-value cache wrapper)
   - IF.trace (logging schema)
   - IF.pulse (health check framework)
   - IF.swarm (agent coordination stub)

### P3: Strategic (Months 2-3)
1. **Unify philosophy and code layers**
   - Ensure every IF.* component has philosopher grounding
   - Create bidirectional links (component → philosophers, philosopher → components)

2. **Port IF.yologuard implementations from external repo**
   - v1.0 (31.2% baseline)
   - v2.0 (intermediate)
   - v3.0 (98.96% with Wu Lun)

---

## Files for Reference

**Source Files:**
- `/home/user/infrafabric/src/infrafabric/core/security/yologuard.py` - IF.yologuard
- `/home/user/infrafabric/src/infrafabric/core/services/librarian.py` - IF.librarian
- `/home/user/infrafabric/src/infrafabric/core/workers/ocr_worker.py` - OCRWorker stub

**Documentation Files:**
- `/home/user/infrafabric/philosophy/IF.philosophy-database.yaml` - Philosopher mapping
- `/home/user/infrafabric/docs/evidence/IF_COMPONENT_INVENTORY.yaml` - Component status (inventory source)
- `/home/user/infrafabric/docs/evidence/EVALUATION_QUICKSTART.md` - Evaluation contradictions
- `/home/user/infrafabric/docs/evidence/INFRAFABRIC_EVAL_PASTE_PROMPT.txt` - Evaluation prompt

**Papers:**
- `/home/user/infrafabric/papers/IF-vision.tex` - Component philosophy (vision paper)
- `/home/user/infrafabric/papers/IF-foundations.tex` - Core component specs
- `/home/user/infrafabric/papers/IF-armour.tex` - Security component spec
- `/home/user/infrafabric/papers/IF-witness.tex` - Validation methodology

---

## Appendix: Complete Component List with Status

```
✅ FULLY INTEGRATED (1)
- IF.yologuard

🟡 CODE-ONLY (1)
- IF.librarian

📝 DOCUMENTED-ONLY (20)
- IF.ground, IF.search, IF.persona, IF.armour, IF.witness
- IF.optimise, IF.sam, IF.guard, IF.citate
- IF.chase, IF.reflect, IF.garp, IF.quiet, IF.constitution
- IF.federate, IF.arbitrate, IF.resource, IF.simplify, IF.collapse

❌ VAPORWARE (13)
- IF.router, IF.memory, IF.trace, IF.pulse, IF.ceo, IF.vesicle
- IF.kernel, IF.swarm, IF.forge, IF.marl, IF.mcp, IF.core
- IF.amplify, IF.council, IF.methodology, IF.pursuit

🔧 STUB-ONLY (1)
- OCRWorker
```

---

**End of Report**
