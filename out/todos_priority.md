# Prioritized TODOs

## Blocking
- **Finalize branch artifacts** (owner: infra-lead, size: M): ensure `out/branches` has no missing summaries, rerun `run_branch_scans.sh` if new branches appear or if new scanner logic is committed.
- **Secure secrets review** (owner: opsec, size: S): triage the `out/branches/*/secrets_candidates.txt` results and feed any high-confidence leaks into the SOC pipeline before publishing.

## High-value
- **Canonical branch consolidation** (owner: infra-arch, size: L): align downstream merges and `IF.*` definitions to `claude/sip-escalate-integration…` and mark it as the canonical basis for the next release.
- **Reorg execution** (owner: infra-engineering, size: M): apply the `moves.csv` plan, run `scripts/update_links.py`, and verify the proposed tree in `proposed_tree.yaml`/`.md` before committing.
- **Aggregate visibility** (owner: data-ops, size: M): publish `if_relationship_map.json/.dot` to the analytics dashboard and refresh the `aggregate_report.md` when new branches arrive.

## Optional
- **Swarm automation cleanup** (owner: automation, size: S): expand `scripts/bulk_move_and_update.sh` to cover Markdown link-checkers or unit tests that future proof link stability.
- **Narrative translation** (owner: comms, size: M): translate the `clean_spec.md` tone rules into multilingual briefs for each guardian channel to reduce misinterpretation.
