# Final Tree Proposal

The final InfraFabric tree is organized around the guardians, cycles, ingestion funnel, orchestration families, and meta index layers described in `clean_spec.md`. The layout below keeps the canonical `claude/sip-escalate-integration...` donor content (the only place that surfaces runnable `if_*` definitions) aligned with the new directories so future merges find the right artifacts immediately.

## Guardians and annexes
`infra/guardians/` becomes the home of the ritual playbooks (`IF-armour`, `IF-foundations`) plus the agents manifest (`agents.md`) that constantly surfaces for every branch. Its `annexes/` subtree stores the reference annexes (N/O/P, `infrafabric-IF-annexes`, the engineering backlog, and the complete source index), so the documents flagged by the repeated secret scans live under a guarded namespace that can be sanity-checked before publishing.

## Cycles and reflections
`infra/cycles/` keeps the temporal artifacts tidy: `papers/IF-vision` and `papers/IF-momentum` sit inside the `vision` node while `papers/IF-foundations` closes the loop under `foundations`. This gives audit and dream cycle contributors a predictable place to find canonical vision docs.

## Ingestion and evaluations
`infra/ingestion/` branches into three pillars:
- `evaluations/` stores the YAML and Gemini dossiers (`INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml`, the Gemini-to-Synthesis saga, and the gemini-logs ties) so the evaluation data that the Yologuard sweeps flagged is co-located with the instrumentation that produces it.
- `prompts/` keeps high-level prompts (`INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md`, `CLOUD-COMMS-TASK-PROMPT.md`, the External Review suites, and the call-for-external-review brief) together so ingestion nodes can look up what to feed the scanners.
- `operations/` hosts the grey-box transition docs (`CLOUD-TRANSITION-PLAN.md`, `SESSION-HANDOVER-TO-CLOUD.md`, `SESSION-RESUME.md`, `SESSION_HANDOFF_2025-11-08_IF-ARMOUR.md`) for the message ingestion cycle and the guard-reviewed path B for Yologuard.

## Orchestration / witness / search
`infra/orchestrations/` contains the witness narratives and search/swarm notes:
- `witness/` holds `papers/IF-witness.md`, `IF_CONNECTIVITY_ARCHITECTURE.md`, and the session handoff/resume logs that the witness agents use.
- `swarm/` groups the gemini logs and compliance writeups so the swarm can replay the evaluation loops.
- `search/` contains the Gemini-to-Synthesis and `CLOUD-COMMS-TASK-PROMPT.md` references that power the `IF.search` discovery layer.

## Meta / indices / tooling
`infra/meta/` preserves all the diagnostic outputs under predictable subfolders:
- `reports/` for `out/aggregate_report.md`, `clean_spec.md`, `if_relationship_map.*`, `migration_instructions.md`, and the existing `proposed_tree.*` references so the analytics dashboards have a consistent path.
- `indices/` for `out/summary.txt`, `todos_priority.md`, and `lost_files_index.txt` keeps the narrative state handy.
- `addenda/` for the Claude session log and addendum plan keeps the auxiliary context aligned with the tree.
`infra/meta/security/` tracks the `SECURITY.md` posture doc, and `infra/tools/` houses the automation scripts plus the `code/yologuard` README so tooling and detectors stay in sync.

## Docs shell
`docs/annexes/` and `docs/evidence/` function as the living memex of annexes and evaluation evidence that feed the `infra/` nodes: they mirror the same files as the new `infra` layout but remain available for downstream readers or translators.

This layout makes guardians, ingestion, and orchestration artifacts discoverable, removes the duplicates that the secret scans worry about, and keeps the aggregator metadata (branches, relationship maps) under a meta umbrella that can itself be relocated or archived after the reorg completes.
