# InfraFabric Mini State Summary

## Branch usage and IF coverage
- 28 branch scans live under `out/branches/` (Claude, Swarm, Gedimat, master, evaluation-system, test-ci, etc.), and the work bifurcates into doc-heavy knowledge snapshots versus a single logic-rich donor lineage.
- Every Claude/Swarm branch piles up hundreds of mention tokens and yologuard/secrets candidates without defining new `if_*` functions, so the branch scans are mostly narrative context with no executable call graph.
- The aggregate report (`out/aggregate_report.md`) already calls out `claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7` as the lone source of real `if_*` definitions (two definitions, six edges, 11 named symbols) while all other branches report zero definitions.

## Definitions vs mention-only references
- Mention-only branches sprinkle tokens like `IF.optimise`, `IF.swarm`, `if-armour`, `if-trace`, and dozens of metric strings, but none actually introduce a callable `if_*` body; the canonical branch holds `if_guard_policy`, `if_witness_logger`, and the associated tests.
- The mention graphs highlight unresolved nodes such as `if-`, `if.`/`if...`, `if.log.meta`, and `if-show` that appear widely across branches and therefore need manual mapping or better parser coverage before future merges.

## Secrets & Yologuard hotspots
- Secrets scans repeatedly flag `README.md` (27 branches), every annex under `annexes/` (26 branches for the key ANNEX files), and core spec docs in `papers/` plus the `infrafabric/` package sources (22 branches each). These documents are the most widely duplicated files and merit central hygiene controls before any reorg.
- Yologuard references cluster around `code/yologuard/GPT5_REQUIREMENTS.md`, `IF_CONNECTIVITY_ARCHITECTURE.md`, and the External Review prompts/arena bundles (22 branches each), while additional logistics briefs (`SESSION-HANDOVER-TO-CLOUD.md`, `CLOUD-TRANSITION-PLAN.md`, `SECURITY.md`) appear in almost every branch’s Yologuard list. Each of those is a high-visibility surface for reminders or validation metadata.

## Clean spec & proposed tree intent
- `out/clean_spec.md` is the canonical specification that names the five guardians, the four cycles, the ingestion vector, veto/dissent rules, tone guidance, and the orchestration families (search, optimise, swarm, message) that the new tree must respect.
- `out/proposed_tree.{md,yaml}` already sketches the planned `infra/guardians`, `infra/cycles`, `infra/ingestion/evaluations`, and `infra/orchestrations` layout so those core documents are co-located with the tooling that keeps references accurate.
- While the `out/` folder stays the landing zone for generated diagnostics, the reorganized tree should place the canonical manifestos, ingestion prompts, orchestration notes, and meta indexes under `infra/` so downstream agents can find them quickly.

## Summary
InfraFabric currently looks like a metadata-heavy snapshot of many mention-rich branches plus a single logic branch. The next step is to clarify where purpose-built documents live, protect the high-risk files in the annex/agents/Yologuard space, and execute the reorganized `infra/*` layout described in `proposed_tree.*` before handing the baton back to a higher-tier agent.
