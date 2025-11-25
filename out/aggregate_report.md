# Aggregate InfraFabric Report

## Branches Processed
- 28 branches scanned, covering the `claude`, `swarm`, `gedimat`, `evaluation-system`, and `test-ci-validation` silos.
- Table below captures the IF coverage diagnostics pulled from each branch's summary snapshot.

| Branch | IF functions | Definitions | Mention tokens | Yologuard refs | Secrets candidates |
| --- | --- | --- | --- | --- | --- |
| `claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7` | 11 | 2 | 209 | 62 | 395 |
| `master` | 0 | 0 | 62 | 7 | 141 |
| `test-ci-validation` | 0 | 0 | 75 | 29 | 230 |
| `gedimat-v3-deploy` | 0 | 0 | 12 | 0 | 23 |
| `swarm/w2-a6-checklist` | 0 | 0 | 75 | 29 | 227 |

## Differences Between Branches
- Most branches only manifest IF mentions (tokens) and do not define any `if_*` functions; in contrast `claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7` is the only branch where the AST scanner detected actual `if_*` definitions and a small call graph (two definitions leading to six edges).
- Mention volume ranges from 12 tokens (`gedimat-v3-deploy`) to 209 tokens (`claude/sip-escalate-integration...`), while secrets sweeps flag 23–395 candidates per branch, signaling inconsistent hygiene across branches.

## IF Function Presence Map
- The aggregated graph reveals only a handful of functions covered anywhere in the codebase: `if_guard_policy`, `if_witness_logger`, `if_headers.get`, and their associated tests/callers. Each is localized to `claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7`.
- The mention graph includes hundreds of tokens but only a few defined call edges, underscoring the gap between conceptual references (`IF.optimise`, `IF.swarm`) and actual callable code.

## Recommended Canonical Branch
`claude/sip-escalate-integration-011CV2nwLukS7EtnB5iZUUe7` should serve as the canonical branch because it hosts the full suite of `if_*` definitions, the richest call edges, and the largest aggregated metadata footprint (mentions, Yologuard references, secrets candidate coverage). Downstream work can merge other branches back into this lineage once the reorganized tree is in place.

## Contradictions Resolved
- The disparity between mention-heavy branches and the function-rich `claude` branch creates duplicate vocabularies with no shared implementation. Resolving this requires consolidating the mention base into a single canonical repository of functions.
- Secrets and Yologuard reference counts vary wildly; the plan is to normalize these scans so every branch writes into the same logging pattern and to treat the canonical branch as the source of truth for guardian-aware calls.

## Next Steps
1. Use `if_relationship_map.json` / `.dot` to guide refactors and to surface potential dependency blind spots.
2. Rebuild the tree so that guardian, cycle, and orchestration documents live under predictable directories (see `proposed_tree.*`).
3. Run `scripts/update_links.py` after any move to avoid stale references and to keep the aggregated experience consistent.
