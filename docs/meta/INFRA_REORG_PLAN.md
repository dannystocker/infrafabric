# InfraFabric Repository Reorganisation Plan

This document summarises the planned cleanup and reorganisation of `dannystocker/infrafabric`, based on:

- `out/final_tree.yaml` and `out/moves_expanded.csv` (local planning artefacts),
- `out/migration_plan_mini.md` (mini’s migration steps),
- External reviews from GPT‑5 and Gemini 3.

It is the “playbook” the CLI agent will follow on a feature branch off `master`.

## Goals

- Move from a “crime‑scene” dump to a **professor‑grade, research‑friendly tree**.
- Give core docs (`IF-*` papers, annexes, evidence) clear homes under `docs/` and `infra/`.
- Make concrete implementations (Yologuard v3 and future code) **discoverable** under a conventional `code/` or `src/` layout.
- Preserve all historical dossiers and evaluation logs, but quarantine them under narrative/legacy folders so they don’t obscure current specs.

## High‑Level Tree (see also `out/final_tree.yaml`)

- `infra/guardians/` – canonical IF armour/foundations docs.
- `infra/cycles/` – cycle/vision docs.
- `infra/ingestion/` – evaluation YAMLs, prompts, operations (handover, session resume).
- `infra/orchestrations/` – witness/swap/search orchestration notes.
- `infra/meta/` – this plan, IF component status, security/meta docs.
- `infra/tools/` – Yologuard requirements and automation scripts.
- `docs/annexes/` – annexes moved out of the root `annexes/` dump.
- `docs/evidence/` – evaluation reports and metrics (kept as historical evidence).

## Phases

1. **Branching**
   - Create `infra/reorg-YYYYMMDD` off `master`.
   - Do not rewrite history; keep `master` and all evaluation branches intact.

2. **Core Moves (driven by `out/moves_expanded.csv`)**
   - Move `IF-armour.md`, `IF-foundations.md`, `IF-vision.md`, `IF-witness.md` into `infra/guardians` / `infra/cycles` / `infra/orchestrations`.
   - Move annexes from `annexes/` into `docs/annexes/`.
   - Move key evaluation YAMLs and prompts under `infra/ingestion/{evaluations,prompts,operations}`.
   - Move `agents.md`, `SECURITY.md`, and Yologuard requirements into `infra/meta/` and `infra/tools/`.

3. **Refine Yologuard Surface**
   - Keep `code/yologuard/src/IF.yologuard_v3.py` and `code/yologuard/versions/IF.yologuard_v3.py` as the implementation anchor.
   - Add a minimal `code/yologuard/README.md` (see below) to explain how the detector relates to `IF-armour.md` and how to run it.
   - Future work: promote into a package under `src/infrafabric/yologuard/` with tests and a CLI entry point.

4. **Meta & Status**
   - Keep `docs/meta/IF_COMPONENT_STATUS.md` as the canonical truth table for which components are implemented vs spec‑only.
   - Update it whenever new code is added or external implementations are published.

5. **CI & Hygiene**
   - Add GitHub Actions for:
     - Markdown link checks (so internal references survive the move),
     - YAML validation for `philosophy/` and inventories,
     - Secret scanning (GitHub’s native + optional self‑dogfooding via Yologuard),
     - Minimal tests once Yologuard is packaged.

## Execution Notes

- All heavy `out/` artefacts (branch scans, relationship maps, planning YAMLs) remain **local** by default and are used as decision support, not as part of the public API.
- The reorg should be done in small commits grouped by logical move sets (e.g., “move core papers”, “move annexes”, “move ingestion assets”) to keep diffs reviewable.
- After the reorg, regenerate a fresh `out_bundle_v2` and update the external evaluation bundle so GPT/Gemini runs against the new tree.

