# InfraFabric IF.* Component Status (Public Repo)

This file summarizes the status of key InfraFabric components **as they exist in the public `dannystocker/infrafabric` repo today**. It separates:

- What is implemented here,
- What is implemented only in external/local repos,
- What is currently specification or research only (“paperware” / “vaporware”).

## Legend

- **Implemented (local)** – Code exists in this repo.
- **Implemented (external)** – Code exists, but only in a different repo or local workspace.
- **Spec only** – Well-documented, no code in this repo.
- **Concept only** – Mentioned or sketched, no clear spec or code.

## Core Components

| Component        | Status                  | Location / Evidence                                                                 |
|-----------------|-------------------------|--------------------------------------------------------------------------------------|
| **IF.yologuard**| Implemented (local + external) | Detector code in `code/yologuard/src/IF.yologuard_v3.py` (branch `yologuard/v3-publish`); earlier versions and evaluation harnesses live in external/local repos. |
| **IF.search**   | Implemented (external)  | Implementation referenced as `mcp-multiagent-bridge/IF.search.py`; methodology documented in `IF-foundations.md`. No code in this repo. |
| **IF.philosophy** | Data only             | Philosopher database in `philosophy/IF.philosophy-database.yaml`. No query engine in this repo. |
| **IF.guard**    | Spec / simulation only  | Guardian council behavior described in papers and annexes, implemented as LLM roleplay transcripts, not as code. |
| **IF.witness**  | Spec only               | Observability / reflexion loop defined in `IF-witness.md`. No orchestration engine or services here. |
| **IF.router**   | Concept only            | Mentioned in docs as a reciprocity-based router; no implementation or concrete spec in this repo. |
| **IF.optimise** | Spec only               | Optimization methodology described in `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md`. No automation in this repo. |
| **IF.citate**   | Concept only            | Citation validation idea appears in tools/docs; no stable implementation here.      |

## Yologuard (IF.armour) vs Implementation

- **Design:** `IF-armour.md` describes Yologuard as a 4‑stage “immune system” with a **Multi‑Agent LLM Consensus** stage (5 models voting), a “Thymic Selection” stage, and a regulatory veto layer.
- **Code:** `code/yologuard/src/IF.yologuard_v3.py` is a **static scanner** with:
  - Entropy‑based token detection,
  - Recursive Base64/hex/JSON/XML decoding,
  - A large regex rule set,
  - A Confucian “relationship” heuristic (user–password, key–endpoint, token–session, cert–authority).
- **Gap:** The LLM consensus layer, Thymic selection mechanism, and orchestration described in `IF-armour.md` are **not implemented** in this repo. All claims about LLM‑based stages should be treated as design goals rather than current behavior.

## Philosophy & Evaluation Artifacts

- `philosophy/IF.philosophy-database.yaml` – stable data source; no runtime consumers in this repo.
- `docs/evidence/*.yaml` / `*.md` – evaluation reports and inventories produced by external agents (GPT‑5, Gemini, Codex). These are **meta‑artifacts**, not code; they describe status and metrics but do not implement functionality.

## Recommended Next Steps

1. **Keep this file updated** when any IF.* component gains real in‑repo code (e.g., when Yologuard is promoted into a proper package under `src/`).
2. **Add references here** to any new external repos that host implementations (with commit/tag IDs for reproducibility).
3. **Mark deprecated designs** when specs in the papers diverge from the behavior of real code, so evaluators (and future agents) know which documents are historical and which describe current behavior.

