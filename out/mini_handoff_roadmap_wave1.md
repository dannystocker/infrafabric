# GPT‑5‑mini Handoff – Encode IF.council Decisions into Plan & Roadmap

You are GPT‑5‑mini running in the same WSL environment as another agent.
Repo root: `/home/setup/infrafabric`
All outputs you create MUST go under: `/home/setup/infrafabric/out/`.

You have NO prior chat history; all context is in files. Do not ask me questions. Work autonomously.

## Context files to read first

- `/home/setup/infrafabric/docs/meta/IF_COMPONENT_STATUS.md`
- `/home/setup/infrafabric/docs/meta/INFRA_REORG_PLAN.md`
- `/home/setup/infrafabric/out/final_tree.yaml`
- `/home/setup/infrafabric/out/moves_expanded.csv`
- `/home/setup/infrafabric/out/moves_external_candidates.csv`
- `/home/setup/infrafabric/out/moves_validation_report.md`
- `/home/setup/infrafabric/out/dossier_diff_report.md`
- `/home/setup/infrafabric/out/dossier_canonical_outline.md`

Assume (from recent IF.council runs) that:
- For the **reorg wave case**, the council verdict across multiple models is consistently **B (Staged reorg with focused publication)**, with conditions like:
  - Wave 1 should apply the new tree and import only canonical/carefully vetted artefacts.
  - Yologuard v3 code must be merged with tests/CI passing before/with the reorg.
  - STATUS / DEFERRED lists should explicitly record what is not yet imported.
- For the **Yologuard hard-gate case**, the council verdict is consistently **B (Staged hard gate)** with strong emphasis on advisory data, FP management, and guardrails.

You do not need the raw council transcripts; treat the above summary as given.

## Task 1 – Draft a Wave 1 contents plan

Goal: produce a **concrete, human-readable list** of what should be included in the first reorg/publication wave.

Using:
- `final_tree.yaml`
- `moves_expanded.csv`
- `moves_external_candidates.csv`
- `dossier_canonical_outline.md`

Write:
- `out/wave1_contents_plan.md`

Contents:
- A short narrative summary of Wave 1 goals (one or two paragraphs).
- Bullet lists of **included categories** for Wave 1, such as:
  - Core IF papers (which files, where they will live),
  - Canonical dossier(s) and where they land under `docs/dossiers/`,
  - Yologuard v3 code, tests, and any immediate CI jobs,
  - Key evaluation prompts / evidence needed for reviewers.
- A short list of **deferred categories** (legacy dossiers, full evidence bundles, extra variants) that should *not* ship in Wave 1 but should be explicitly listed later in a DEFERRED section.

Keep it specific enough that a human maintainer could turn it into a checklist for the `infra/reorg-…` branch.

## Task 2 – ROADMAP draft

Goal: produce a clear, reader-friendly roadmap that reflects what the repo actually is and what we plan next.

Write:
- `out/ROADMAP_draft.md`

Contents:
- A top-level overview section (2–3 paragraphs) summarising:
  - What InfraFabric is trying to be,
  - What is implemented now (especially Yologuard v3),
  - What is still research/speculative.
- A **phased roadmap** with at least three waves:
  - Wave 1 – Reorg + publication (based on wave1_contents_plan).
  - Wave 2 – Additional imports (legacy dossiers, more evidence) and Yologuard refactor/package.
  - Wave 3 – Broader IF.* implementation or integrations (guard/council, search/optimise, etc.).
- For each wave, list 3–7 bullets combining:
  - Structural changes,
  - Implementation work,
  - Evaluation/replication work,
  - Governance / documentation work (e.g., making IF.council binding on certain decisions later).

Align your wording with IF_COMPONENT_STATUS.md so we don’t over-claim.

## Task 3 – Reorg plan delta (Wave 1 constraints)

Goal: express how INFRA_REORG_PLAN.md should be adjusted to encode the council’s Wave 1 constraints.

Write:
- `out/INFRA_REORG_PLAN_wave1_patch.md`

Contents:
- A short intro explaining that this patch incorporates:
  - Council verdict B (staged reorg),
  - Conditions (canonical imports only, CI/tests, STATUS/DEFERRED docs, history-preserving moves).
- A bullet list of **additions/changes** that should be made to INFRA_REORG_PLAN.md, for example:
  - “Add a section ‘Wave 1 Scope’ specifying that only [these categories] are included.”
  - “Add a requirement that Yologuard v3 is merged with passing tests/CI before the reorg PR merges.”
  - “Add a requirement for a DEFERRED_ARTEFACTS section listing omitted dossiers.”
- You do **not** need to rewrite the whole plan – just describe the patch in enough detail that a human can apply it.

## Rules

- Do NOT modify or move any files outside `out/`.
- Be explicit when something is inferred from the summary vs directly read.
- Work autonomously; assume no follow-up questions.

When you are done, summarise what you wrote to:
- wave1_contents_plan.md
- ROADMAP_draft.md
- INFRA_REORG_PLAN_wave1_patch.md
