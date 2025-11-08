# InfraFabric — 10‑Agent Haiku Swarm Plan (with Git Tree Tracking)

Date: 2025‑11‑08
Coordinator: Claude (run as low‑cost Haiku swarm)
Goal (Week 1): Ship novice foundations + reproducibility + governance enforcement + schema

## Operating Rules
- Branch per agent: `swarm/<id>-<slug>` (e.g., `swarm/a1-quickstart`)
- Path ownership: each agent edits only assigned subpaths (below)
- Commits: small, frequent; conventional messages; include `[SWARM:<id>]`
- Evidence‑Binding: all claims in docs cite `path:line`
- PRs: target `master`; request reviewers from neighboring agents; pass CI
- Git Tree Tracking: run `scripts/git-tree-tracker.sh` to summarize changes per branch/path

## Agents, Tasks, Branches, Paths, Acceptance Criteria

1) A1 — Quick Start + Hello World
- Branch: `swarm/a1-quickstart`
- Paths: `docs/QUICK_START.md`, `docs/HELLO_W0RLD.md`, `docs/EXAMPLES/01_scan_single_file.sh`
- Done when: new user can scan in <5 min; script runs; outputs shown; troubleshooting included

2) A2 — Examples 02–05
- Branch: `swarm/a2-examples`
- Paths: `docs/EXAMPLES/02_scan_directory.sh`, `docs/EXAMPLES/03_ci_integration.sh`, `docs/EXAMPLES/04_custom_profiles.sh`, `docs/EXAMPLES/05_governance_simple.sh`
- Done when: each script is single‑concept, commented, expected outputs included

3) A3 — Simple Output Mode (CLI)
- Branch: `swarm/a3-simple-output`
- Paths: `code/yologuard/src/IF.yologuard_v3.py` (flags `--simple-output`, `--format json-simple`), `docs/GLOSSARY.md`
- Done when: CLI prints friendly messages; JSON‑simple schema documented; benchmarks unchanged

4) A4 — Reproducibility & Ablations
- Branch: `swarm/a4-repro-ablations`
- Paths: `code/yologuard/repro/REPRODUCE.md`, `code/yologuard/repro/run_config.json`, `docs/ABLATIONS.md`, `code/yologuard/harness/*` (reports only)
- Done when: commit hash + hyperparams captured; expected vs actual output; ablation table stubbed; FP precision summary generated

5) A5 — IFMessage Schema + Samples
- Branch: `swarm/a5-ifmessage-schema`
- Paths: `schemas/ifmessage/v1.0.schema.json`, `messages/examples/*.json`, `scripts/validate_message.py`
- Done when: sample messages validate with `jsonschema`; doc block in schema header explains fields

6) A6 — CI Governance + Schema Validation
- Branch: `swarm/a6-ci-governance`
- Paths: `.github/workflows/review.yml`, `.github/PULL_REQUEST_TEMPLATE.md`
- Done when: CI validates decision JSONs (REVIEW_SCHEMA.json) and IFMessage samples; labeled ‘release’ PRs fail if missing/invalid

7) A7 — Governance Runbook + Example
- Branch: `swarm/a7-governance-runbook`
- Paths: `governance/DECISION_DISSENT_RUNBOOK.md`, `governance/examples/decision_example.json`
- Done when: dissent escalation steps clear; example JSON passes schema; cross‑linked from Quick Start advanced section

8) A8 — Performance Targets
- Branch: `swarm/a8-perf-targets`
- Paths: `docs/PERFORMANCE_TARGETS.md`
- Done when: p50/p95/p99 targets documented; “what to expect” table added; async fallback semantics written

9) A9 — Visuals (Mermaid placeholders)
- Branch: `swarm/a9-visuals`
- Paths: `docs/VISUALS/architecture_simple.md`, `docs/VISUALS/how_detection_works.md`, `docs/VISUALS/profiles_explained.md`
- Done when: mermaid diagrams render; linked from Quick Start and README; PNGs can be added later

10) A10 — Coordinator & QA
- Branch: `swarm/a10-coordination`
- Paths: `SWARM_STATUS.md`, `SWARM_BRANCHES.txt`, `scripts/git-tree-tracker.sh`
- Done when: status board updated daily; tracker lists changes per branch; release notes draft compiled

## Commit Message Template
```
feat(docs): quick start v1 with single-file example [SWARM:A1]
fix(cli): add --simple-output, json-simple format [SWARM:A3]
ci(governance): validate decision JSON + IFMessage [SWARM:A6]
```

## Review & Merge Protocol
- Pre‑merge checklist: links render, examples run locally, CI green, citations present
- Governance PRs (A6, A7): require 2 approvals (one from A10)
- CLI PR (A3): must re‑run benchmark (107/96; 42/42) and attach results

## Git Tree Tracking
- Branch list file: `SWARM_BRANCHES.txt` (one per line)
- Tracker script: `scripts/git-tree-tracker.sh` prints `git diff --name-status origin/master...<branch>`

## Owner Matrix
- A1: docs/QUICK_START.md, docs/EXAMPLES/01_*
- A2: docs/EXAMPLES/02_* to 05_*
- A3: code/yologuard/src/IF.yologuard_v3.py; docs/GLOSSARY.md
- A4: code/yologuard/repro/*; docs/ABLATIONS.md
- A5: schemas/ifmessage/*; scripts/validate_message.py; messages/examples/*
- A6: .github/workflows/*; .github/PULL_REQUEST_TEMPLATE.md
- A7: governance/*
- A8: docs/PERFORMANCE_TARGETS.md
- A9: docs/VISUALS/* (mermaid)
- A10: SWARM_STATUS.md; scripts/git-tree-tracker.sh; EXTERNAL_REVIEW_LINKS.txt

## Success Criteria (Week 1)
- Time‑to‑first‑scan < 5 minutes
- At least 5 examples runnable
- IFMessage v1.0 schema + validator shipped
- CI enforces decision JSON + message samples
- Performance targets documented
- Evidence‑binding present in new docs
