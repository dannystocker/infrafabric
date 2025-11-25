# GPT‑5‑mini WSL Handoff

You are GPT‑5‑mini running in the **same WSL environment** as another (more expensive) GPT‑5.1 agent. Both of you share the same filesystem at `/home/setup`, but you do **not** talk to each other directly. This file is the contract between you.

## Ground rules
- Repo root: `/home/setup/infrafabric`
- All outputs you create must go under: `/home/setup/infrafabric/out/`
- Do **not** ask the user follow‑up questions; assume reasonable defaults.
- Do **not** run destructive git commands (no history rewrites, no force‑push, no reset --hard).
- You may read any files under `/home/setup` and `/tmp` that the OS allows, but write only inside `~/infrafabric/out/`.

## 1. Understand the current state

1. Read these core files:
   - `out/aggregate_report.md`
   - `out/clean_spec.md`
   - `out/proposed_tree.md`
   - `out/proposed_tree.yaml`
   - `out/moves.csv`
   - `out/todos_priority.md`
   - `out/if_relationship_map.json`
   - `out/summary.txt`
   - `out/claude_session_addendum.md` (if present)
   - `out/addendum_plan.md` (if present)

2. Sample per‑branch data:
   - For each directory under `out/branches/`, read its `summary.txt`.
   - Skim a few representative `if_index.json` and `if_mentions.json` files (especially from `claude/*`, `swarm/*`, and `master`).

3. From this, write a human‑readable overview to:
   - `out/state_summary_mini.md`

That overview should explain:
- How branches are used (docs‑heavy vs IF‑logic‑heavy).
- Where real `if_*` definitions live vs. just mentions.
- Where secrets and Yologuard hotspots are (based on the per‑branch summaries).
- What `clean_spec.md` and `proposed_tree.*` are trying to achieve.

## 2. Design a professor‑grade final tree

1. Propose a **clean, human‑logical directory hierarchy** for the repo itself (under `/home/setup/infrafabric`). Cover at least:
   - Guardians & cycles docs (e.g., `IF-armour`, `IF-foundations`, `IF-vision`, annexes).
   - Ingestion & evaluations (INFRAFABRIC_EVAL*, evaluation prompts/guides, annexes mentioned in the spec).
   - Orchestration / witness / swarm / search docs.
   - Meta / indices / logs (aggregate reports, relationship maps, session addenda, meta indexes).
   - Code / scripts / tools.

2. Represent this as YAML and markdown:
   - YAML tree: `out/final_tree.yaml`
   - Narrative explanation: `out/final_tree.md`

Assume the Git trunk should remain `master`, and that one of the `claude/sip-*` branches is the main **donor** of IF logic to be merged into a future `infra/reorg-YYYYMMDD` feature branch off `master`.

## 3. Expand and fix moves.csv

1. Treat the existing `out/moves.csv` as a seed (it currently has only a few moves).

2. Produce a **new, expanded mapping** that:
   - Has each row as exactly: `old_path,new_path` (two fields), relative to repo root.
   - Is encoded in UTF‑8 and contains no line wrapping/truncation.
   - Covers at minimum:
     - Core guardians/cycles docs (e.g., `IF-armour.md`, `IF-foundations.md`, `IF-vision.md`, any key IF annexes already in the repo).
     - Key ingestion/evaluation docs (INFRAFABRIC_EVAL*, core evaluation prompts/guides in `docs/` that clearly belong under an ingestion/evaluations subtree).
     - Orchestration docs (IF‑witness, IF.swarm‑related docs, search/optimise case studies).
     - Meta/indices that clearly belong under an `infra/meta` or similar subtree (e.g., aggregate reports, relationship maps).

3. Write the expanded mapping to **a new file**:
   - `out/moves_expanded.csv`

Do **not** attempt to list every possible move; aim for a focused but meaningful set of moves that implements the heart of your `final_tree.yaml` proposal.

## 4. Secrets & Yologuard risk map

1. For each branch directory under `out/branches/`, if it contains:
   - `secrets_candidates.txt`
   - `yologuard_refs.txt`
   read them and look for **repeated file paths** that show up across many branches.

2. Produce a markdown report:
   - `out/secrets_yologuard_risk_mini.md`

This report should:
- List the top repeated file paths and, for each, how many branches reference it.
- Assign a qualitative risk level per file: HIGH / MEDIUM / LOW (based on filename and context only; do not quote actual secrets).
- Recommend what a human should do **before** any reorg commit (scrub, rotate, quarantine, or keep but monitor).

## 5. UNDEF:: call‑graph issues

1. Inspect `out/if_relationship_map.json` for any nodes or edges involving `UNDEF::` or obviously unresolved symbols.

2. Create:
   - `out/undef_callgraph_notes_mini.md`

Include in that file:
- A list of the top 10–20 ambiguous nodes.
- For each, a best‑effort hypothesis about what it likely refers to.
- A recommendation: map to a specific `if_*` symbol, document as inherently dynamic, or flag as a scanning gap.

## 6. Migration plan for the CLI agent

Finally, write a concrete, numbered migration plan for the higher‑tier GPT‑5.1 CLI agent to follow later:
- Save this plan to: `out/migration_plan_mini.md`

The plan should assume:
- Repo: `/home/setup/infrafabric`
- Trunk: `master`
- Donor branch: choose the best `claude/*` branch based on the scans (likely a sip/escalate branch with actual `if_*` definitions).

In `out/migration_plan_mini.md`:
- Describe how to:
  1. Create an `infra/reorg-YYYYMMDD` branch off `master`.
  2. Bring the donor branch’s IF logic into that branch (merge or cherry‑pick) **without** rewriting history.
  3. Apply `out/moves_expanded.csv` using `git mv` and `scripts/update_links.py --mapping ... --dry-run` followed by a real run.
  4. Rerun the branch scanners (`run_branch_scans.sh`) to rebuild `out/branches` and regenerate the aggregate reports.
  5. Address the HIGH‑risk secrets/Yologuard files and UNDEF issues you identified.
  6. Produce a fresh `out_bundle_v2.zip` and updated `gpt5pro_bundle_v2.md` for a final review.

Do all of the above **autonomously** in this WSL environment, using shell and file‑read tools as available to you. Write your results only to the `out/` files specified.
