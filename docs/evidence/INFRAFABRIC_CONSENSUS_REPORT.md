# InfraFabric Evaluation Consensus Report

**Evaluators:** Codex, GPT-5.1, Gemini AI Agent

**Generated:** 2025-11-15


## Score Consensus

### overall_score
- **Average:** 5.35/10
- **Variance:** 0.72
- **Individual scores:**
  - Codex: 4.5
  - GPT-5.1: 6.2

### substance_score
- **Average:** 7.0/10
- **Variance:** 1.0
- **Individual scores:**
  - Codex: 6
  - GPT-5.1: 8

### novelty_score
- **Average:** 7.5/10
- **Variance:** 0.25
- **Individual scores:**
  - Codex: 7
  - GPT-5.1: 8
- **Outliers:** Codex, GPT-5.1

### rigor_score
- **Average:** 5.5/10
- **Variance:** 2.25
- **Individual scores:**
  - Codex: 4
  - GPT-5.1: 7

### coherence_score
- **Average:** 7.0/10
- **Variance:** 1.0
- **Individual scores:**
  - Codex: 6
  - GPT-5.1: 8

### code_quality_score
- **Average:** 2.5/10
- **Variance:** 0.25
- **Individual scores:**
  - Codex: 2
  - GPT-5.1: 3
- **Outliers:** Codex, GPT-5.1


## IF.* Component Status (Consensus)


### IMPLEMENTED

**InfraFabric evaluation merger** (1/3 evaluators agree - 33% consensus)
- Evaluators: GPT-5.1
- Average completeness: 80%

**IF.philosophy data layer** (1/3 evaluators agree - 33% consensus)
- Evaluators: GPT-5.1
- Average completeness: 70%


### PARTIAL

**IF.ground** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.search** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.persona** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.armour** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.witness** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.yologuard** (2/3 evaluators agree - 67% consensus)
- Evaluators: Codex, GPT-5.1

**IF.optimise** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.guard** (1/3 evaluators agree - 33% consensus)
- Evaluators: GPT-5.1

**IF.citate** (1/3 evaluators agree - 33% consensus)
- Evaluators: GPT-5.1


### VAPORWARE

**IF.router** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.memory** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.trace** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.pulse** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.ceo** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.vesicle** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.kernel** (1/3 evaluators agree - 33% consensus)
- Evaluators: Codex

**IF.swarm** (1/3 evaluators agree - 33% consensus)
- Evaluators: GPT-5.1

**IF.ceo** (1/3 evaluators agree - 33% consensus)
- Evaluators: GPT-5.1


## P0 Blockers (Consensus)


**No runnable IF.* implementations committed** (1/3 evaluators - 33% consensus)
- Identified by: Codex
- Effort estimates: 2-4 weeks


**Broken / gated citations in core papers** (1/3 evaluators - 33% consensus)
- Identified by: Codex
- Effort estimates: 1-2 days


**Core IF.* components such as IF.guard, IF.yologuard, and IF.citate lack in-repo implementations.** (1/3 evaluators - 33% consensus)
- Identified by: GPT-5.1
- Effort estimates: Several weeks to months to build even minimal, well-tested implementations of a subset of components.


**No automated tests or CI pipeline anywhere in the repo.** (1/3 evaluators - 33% consensus)
- Identified by: GPT-5.1
- Effort estimates: 3–7 days to introduce basic unit tests and CI for the evaluation script and any new reference implementations.


## Citation & Documentation Quality (Consensus)


### Overall Citation Stats

- **Papers reviewed:** 4 (average across evaluators)
- **Total citations found:** 118
- **Citations verified:** 10 (8%)


### Citation Issues (by consensus)


🟡 **SuperAGI swarm reference 404s (https://superagi.com/swarms checked 2025-11-15).** (1/3 evaluators - 33% consensus)
- Severity: medium
- Identified by: Codex
- Example: papers/IF-witness.tex:1285-1288


🟡 **Citation and link-health verification system is specified in docs but not recorded as executed for this snapshot.** (1/3 evaluators - 33% consensus)
- Severity: medium
- Identified by: GPT-5.1
- Example: docs/evidence/EVALUATION_FILES_SUMMARY.md


🟢 **Warrant canary SSRN citation requires authentication (HTTP 403).** (1/3 evaluators - 33% consensus)
- Severity: low
- Identified by: Codex
- Example: papers/IF-witness.tex:1316-1319


🟢 **Most IF.ground references are >65 years old with no modern corroboration.** (1/3 evaluators - 33% consensus)
- Severity: low
- Identified by: Codex
- Example: papers/IF-foundations.tex:2403-2434


## Buyer Persona Consensus

**Academic AI safety / governance research labs**
- Avg Fit Score: 9.0/10
- Avg Willingness to Pay: 3.0/10
- Identified by: GPT-5.1

**AI safety / governance research labs**
- Avg Fit Score: 7.0/10
- Avg Willingness to Pay: 3.0/10
- Identified by: Codex

**Enterprise AI governance and compliance teams**
- Avg Fit Score: 7.0/10
- Avg Willingness to Pay: 6.0/10
- Identified by: GPT-5.1

**LLM platform / infra vendors**
- Avg Fit Score: 5.0/10
- Avg Willingness to Pay: 5.0/10
- Identified by: GPT-5.1

**Enterprise security leaders evaluating AI workflows**
- Avg Fit Score: 4.0/10
- Avg Willingness to Pay: 4.0/10
- Identified by: Codex

**Public-sector innovation units**
- Avg Fit Score: 3.0/10
- Avg Willingness to Pay: 2.0/10
- Identified by: Codex
