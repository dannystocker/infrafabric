# GPT‑5‑mini Reorg & Cleanup Task Handoff

You are GPT‑5‑mini running in the same WSL environment as another agent.
Repo root: `/home/setup/infrafabric`
All outputs you create MUST go under: `/home/setup/infrafabric/out/`.

You have NO prior chat history; all context is in files. Do not ask me questions. Work autonomously.

You should treat this document as your task list.

Core context to read first
--------------------------

Read these files to understand the plan and current state:

- `/home/setup/infrafabric/docs/meta/IF_COMPONENT_STATUS.md`
- `/home/setup/infrafabric/docs/meta/INFRA_REORG_PLAN.md`
- `/home/setup/infrafabric/out/final_tree.yaml`
- `/home/setup/infrafabric/out/moves_expanded.csv`
- `/home/setup/infrafabric/out/moves_external_candidates.csv`
- `/home/setup/infrafabric/out/fs_if_index_summary_mini.md`
- `/home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py`
- `/home/setup/infrafabric/code/yologuard/README.md`
- `/home/setup/infrafabric/out/yologuard_test_vectors.md` (if present)

Use additional repo files (docs, annexes, evidence) as needed.

Task A – Dossier & docs consolidation
------------------------------------

Goal: clarify how all the INFRAFABRIC-* dossiers and related docs relate to each other and to the main papers.

1. Using the filesystem indexes (`home_if_index.txt`, `windows_if_index.txt`) and the existing INFRAFABRIC dossiers already in the repo (e.g., `INFRAFABRIC-COMPLETE-DOSSIER-v11.md`), produce:

   a) `out/dossier_diff_report.md`
      - For each major dossier variant (v7, v8, v11, COMPLETE_PACKAGE, etc.):
        - Briefly describe scope, size, and apparent generation date.
        - Summarize what is unique to each vs the others (sections present/absent, notable structural differences).

   b) `out/dossier_canonical_outline.md`
      - A single merged outline of “canonical” InfraFabric content, showing:
        - Suggested section headings (e.g., Vision, Foundations, Armour, Witness, Evaluations, Roadmap).
        - For each heading, list source file(s) and section anchors where that content currently lives.
      - This is a map for a future editor; do NOT rewrite the dossiers themselves.

Task B – Move planning validation
---------------------------------

Goal: sanity‑check the current move CSVs and propose a second wave if needed.

1. Validate `out/moves_expanded.csv` and `out/moves_external_candidates.csv`:
   - Check that all `old_path` entries exist on disk.
   - Check that no two rows map to the same `new_path` unless that is clearly intentional.
   - Check that `new_path` locations are consistent with `final_tree.yaml` and `INFRA_REORG_PLAN.md`.

2. Write your findings to:
   - `out/moves_validation_report.md`

   Include:
   - Missing old_path entries (if any),
   - Conflicting new_path entries,
   - Any obvious tree mismatches.

3. If you see obvious additional moves that align with `final_tree.yaml` (e.g., philosophy data, remaining IF.* specs, evaluation scripts), propose a “wave 2” mapping as:
   - `out/moves_expanded_v2.csv`
   Format identical to the others: `old_path,new_path` (repo‑relative).

Task C – IF.* API surface catalogue
-----------------------------------

Goal: build a human‑readable index of IF.* components as they appear across the docs.

1. Scan the repo for references to IF.* / IF_* / if.guard / if.search / if.optimise / if.swarm / etc. (use `rg` or `grep`).

2. Build:
   - `out/if_api_catalog.md`

   Contents:
   - Group components into:
     - Implemented here (as per IF_COMPONENT_STATUS.md),
     - Implemented externally,
     - Spec‑only,
     - Concept‑only.
   - For each component, list:
     - Short description,
     - Primary spec docs (file paths),
     - Any implementation paths (local or external mentioned in docs).

Task D – Yologuard variants comparison
--------------------------------------

Goal: understand how all IF.yologuard_v3.py copies differ.

1. For the paths listed in `fs_if_index_summary_mini.md` and `moves_external_candidates.csv` that point to IF.yologuard_v3.py, compare them to the repo copy in `code/yologuard/src/IF.yologuard_v3.py`.

2. Produce:
   - `out/yologuard_variants_comparison.md`

   Include for each variant:
   - Path,
   - Whether it is identical, a superset, or an older revision vs the repo version,
   - Any notable differences (e.g., extra patterns, different test harness, different philosophy comments).

Task E – Yologuard refactor proposal
------------------------------------

Goal: propose how to split the monolithic IF.yologuard_v3.py into a package.

1. Based on the current code and README, write:
   - `out/yologuard_refactor_plan.md`

   Include:
   - Suggested module layout (e.g., detector.py, patterns.py, relationships.py, cli.py) under a future `src/infrafabric/yologuard/` package.
   - Proposed public API (functions/classes external callers should use).
   - How tests in `tests/test_yologuard.py` should be structured in that package.

Task F – CI workflow drafts
---------------------------

Goal: draft GitHub Actions workflows for docs and Yologuard.

1. Draft a docs‑focused CI workflow as text:
   - `out/github_workflow_docs-ci.yaml.txt`

   It should include jobs for:
   - Markdown link checking across docs/, annexes/, and infra/meta.
   - YAML validation for philosophy and docs/evidence inventories.

2. Draft a Yologuard‑focused CI workflow as text:
   - `out/github_workflow_yologuard-ci.yaml.txt`

   It should include jobs for:
   - Running `pytest tests/test_yologuard.py`.
   - (Optional) Running the Yologuard detector in dry‑run mode against the repo (with sensible exclusions, e.g., tests and any directories that intentionally contain synthetic secrets).

Task G – Security notes draft
-----------------------------

Goal: assemble a first pass security/hardening note for this repo.

1. Using `out/secrets_yologuard_risk_mini.md`, `IF_COMPONENT_STATUS.md`, and any relevant SECURITY‑related docs in the repo, draft:
   - `out/SECURITY-NOTES_draft.md`

   Contents:
   - Main risk surfaces (secrets, simulated evidence, missing implementations).
   - Recommended secret handling approach (local vaults, `.gitignore` patterns, use of Yologuard).
   - A short checklist for PR reviewers touching auth/secrets/evidence.

General rules
-------------

- Do NOT modify or move files outside `out/`.
- Do NOT delete anything.
- Be explicit when something is inferred (vs directly read from files).
- Work autonomously; assume there will be no follow‑up questions.

When you’re done, summarise which of Tasks A–G you completed and which outputs you wrote under `out/`.
