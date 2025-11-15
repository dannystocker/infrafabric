# InfraFabric Evaluation Consensus Report

**Evaluators:** GPT-5.1, GPT-5.1 (Codex CLI)

**Generated:** 2025-11-15


## Score Consensus

### overall_score
- **Average:** 6.35/10
- **Variance:** 0.02
- **Individual scores:**
  - GPT-5.1: 6.2
  - GPT-5.1 (Codex CLI): 6.5
- **Outliers:** GPT-5.1, GPT-5.1 (Codex CLI)

### substance_score
- **Average:** 8.0/10
- **Variance:** 0.0
- **Individual scores:**
  - GPT-5.1: 8
  - GPT-5.1 (Codex CLI): 8

### novelty_score
- **Average:** 8.0/10
- **Variance:** 0.0
- **Individual scores:**
  - GPT-5.1: 8
  - GPT-5.1 (Codex CLI): 8

### rigor_score
- **Average:** 6.5/10
- **Variance:** 0.25
- **Individual scores:**
  - GPT-5.1: 7
  - GPT-5.1 (Codex CLI): 6
- **Outliers:** GPT-5.1, GPT-5.1 (Codex CLI)

### coherence_score
- **Average:** 7.5/10
- **Variance:** 0.25
- **Individual scores:**
  - GPT-5.1: 8
  - GPT-5.1 (Codex CLI): 7
- **Outliers:** GPT-5.1, GPT-5.1 (Codex CLI)

### code_quality_score
- **Average:** 3.0/10
- **Variance:** 0.0
- **Individual scores:**
  - GPT-5.1: 3
  - GPT-5.1 (Codex CLI): 3


## IF.* Component Status (Consensus)


### IMPLEMENTED

**InfraFabric evaluation merger** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1
- Average completeness: 80%

**IF.philosophy data layer** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1
- Average completeness: 70%

**IF.philosophy** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1 (Codex CLI)
- Average completeness: 80%


### PARTIAL

**IF.guard** (2/2 evaluators agree - 100% consensus)
- Evaluators: GPT-5.1, GPT-5.1 (Codex CLI)

**IF.citate** (2/2 evaluators agree - 100% consensus)
- Evaluators: GPT-5.1, GPT-5.1 (Codex CLI)

**IF.yologuard** (2/2 evaluators agree - 100% consensus)
- Evaluators: GPT-5.1, GPT-5.1 (Codex CLI)

**IF.optimise** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1 (Codex CLI)


### VAPORWARE

**IF.swarm** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1

**IF.sam** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1

**IF.amplify** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1 (Codex CLI)

**IF.mcp** (1/2 evaluators agree - 50% consensus)
- Evaluators: GPT-5.1 (Codex CLI)


## P0 Blockers (Consensus)


**Core IF.* components such as IF.guard, IF.yologuard, and IF.citate lack in-repo implementations.** (1/2 evaluators - 50% consensus)
- Identified by: GPT-5.1
- Effort estimates: Several weeks to months to build even minimal, well-tested implementations of a subset of components.


**No automated tests or CI pipeline anywhere in the repo.** (1/2 evaluators - 50% consensus)
- Identified by: GPT-5.1
- Effort estimates: 3–7 days to introduce basic unit tests and CI for the evaluation script and any new reference implementations.


**No end-to-end implementation of core IF.* frameworks in this repo (docs-only).** (1/2 evaluators - 50% consensus)
- Identified by: GPT-5.1 (Codex CLI)
- Effort estimates: 4-8 weeks to build and publish an MVP implementation for at least IF.citate + a minimal IF.guard council API.


**Key performance claims for IF.yologuard are not reproducible from this repository alone.** (1/2 evaluators - 50% consensus)
- Identified by: GPT-5.1 (Codex CLI)
- Effort estimates: 3-5 days to bundle a public benchmark harness, synthetic test corpus pointer, and a step-by-step reproduction guide.


## Citation & Documentation Quality (Consensus)


### Overall Citation Stats

- **Papers reviewed:** 6 (average across evaluators)
- **Total citations found:** 220
- **Citations verified:** 7 (3%)


### Citation Issues (by consensus)


🔴 **Links to IF.yologuard v1/v3 source code under the main infrafabric repo return 404; the implementation has moved, breaking reproducibility of key metrics.** (1/2 evaluators - 50% consensus)
- Severity: high
- Identified by: GPT-5.1 (Codex CLI)
- Example: INFRAFABRIC-COMPLETE-DOSSIER-v11.md:1465-1467


🟡 **Citation and link-health verification system is specified in docs but not recorded as executed for this snapshot.** (1/2 evaluators - 50% consensus)
- Severity: medium
- Identified by: GPT-5.1
- Example: docs/evidence/EVALUATION_FILES_SUMMARY.md


🟡 **Several citations reference localhost or internal endpoints (e.g., private Gitea at http://localhost:4000/ggq-admin/icw-nextspread) that are not accessible to external readers.** (1/2 evaluators - 50% consensus)
- Severity: medium
- Identified by: GPT-5.1 (Codex CLI)
- Example: IF-armour.md


🟡 **The icantwait.ca API endpoint shown in IF.armour (https://icantwait.ca/api/properties/) currently returns 404, so the code snippet is no longer an accurate living example.** (1/2 evaluators - 50% consensus)
- Severity: medium
- Identified by: GPT-5.1 (Codex CLI)
- Example: IF-armour.md


🟡 **Most external scientific references (Nature Electronics RRAM paper, PsyPost 2025 neurogenesis article, Singapore Police Force reports) are named but lack DOIs or precise bibliographic metadata.** (1/2 evaluators - 50% consensus)
- Severity: medium
- Identified by: GPT-5.1 (Codex CLI)
- Example: IF-vision.tex


🟢 **Age of some foundational citations (e.g., Wexler 2015 warrant canaries) is acceptable but would benefit from being complemented by more recent work.** (1/2 evaluators - 50% consensus)
- Severity: low
- Identified by: GPT-5.1 (Codex CLI)
- Example: IF-witness.md:590-604


## Buyer Persona Consensus

**Academic AI safety / governance research labs**
- Avg Fit Score: 9.0/10
- Avg Willingness to Pay: 3.0/10
- Identified by: GPT-5.1

**AI Safety / Governance Research Labs**
- Avg Fit Score: 8.0/10
- Avg Willingness to Pay: 3.0/10
- Identified by: GPT-5.1 (Codex CLI)

**Enterprise AI governance and compliance teams**
- Avg Fit Score: 7.0/10
- Avg Willingness to Pay: 6.0/10
- Identified by: GPT-5.1

**Advanced Open-Source / Indie Builders**
- Avg Fit Score: 7.0/10
- Avg Willingness to Pay: 2.0/10
- Identified by: GPT-5.1 (Codex CLI)

**Enterprise AI Platform & Risk Teams**
- Avg Fit Score: 6.0/10
- Avg Willingness to Pay: 6.0/10
- Identified by: GPT-5.1 (Codex CLI)

**LLM platform / infra vendors**
- Avg Fit Score: 5.0/10
- Avg Willingness to Pay: 5.0/10
- Identified by: GPT-5.1
