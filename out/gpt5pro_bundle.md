# GPT5Pro Evaluation Bundle

## Objectives
- Capture the full InfraFabric reconstruction, indexing, branch scanning, and metadata extraction work in a single place so GPT5Pro can evaluate everything without extra context or file access.
- Surface the most actionable data (per-branch summaries, aggregated maps, canonical spec, reorg plan, tooling) and describe what still needs attention.
- Request targeted assistance from GPT5Pro to review those artifacts, spot missing linkages, and help debug the plan so the repo can be reorganized cleanly.

## Delivered Artifacts
- `out/branches/` – per-branch directories containing `if_index.json`, `if_mentions.json`, manifest files, `yologuard_refs.txt`, `secrets_candidates.txt`, and `summary.txt`. Use these to understand branch-specific IF function coverage and risks.
- `out/aggregate_report.md` – totals, contradictions resolved, canonical branch recommendation (`claude/sip-escalate-integration…`), and next actions.
- `out/if_relationship_map.json` & `.dot` – unified call graph and mention cooccurrence data across every branch scanned.
- `out/clean_spec.md` – canonical specification covering Guardians, Cycles, ingestion flow, orchestration families, veto/dissent/sensitivity rules, multilingual tone, and message pipelines.
- `out/proposed_tree.{md,yaml}` – proposed tree restructure plus rationale for reorganizing guardian and ingestion assets.
- `out/moves.csv` + `out/migration_instructions.md` – precise move list and commands for running `scripts/update_links.py` safely in dry-run and apply modes.
- `scripts/scan_if_functions.py`, `scan_if_mentions.py`, `update_links.py`, `bulk_move_and_update.sh` – surgical tooling for re-scanning, mention discovery, and safe link updating. There’s also `~/infrafabric-tools/run_branch_scans.sh` for repeating branch-wide scans and the scheduler for `scripts/` resides under `scripts/`.
- `out/todos_priority.md` – blocking/high-value/optional next steps with owners and size estimates.
- `out/lost_files_index.txt`, `out/claude_session_addendum.md`, `out/addendum_plan.md` – results of the lost-files sweep and Claude session metadata you asked to include.
- `out/summary.txt` – executive-level recap plus checklist referencing the path to everything.

## Request for GPT5Pro Assistance
1. **Audit the per-branch scans**: Validate that all first-class `if_*` definitions and mention graphs are captured; call out branches missing data and advise whether additional tooling (e.g., deeper AST parsing) is required.
2. **Review `if_relationship_map.json/.dot`**: Confirm that the canonical branch assigned in the aggregate report is logical and suggest alternative merges if contradictions remain.
3. **Confirm the reorg plan**: Given `proposed_tree.*` and `moves.csv`, highlight any missing references or metadata (especially Claude session indexes and `out/claude_session_addendum.md`) that must move or be cross-referenced before the tree is reorganized.
4. **Help debug the migration scripts**: Describe how you would verify `scripts/update_links.py` and `scripts/bulk_move_and_update.sh` interact with `moves.csv` and what additional assertions should run (Markdown link check, rerun scanners) to ensure no broken references.
5. **Advise on sequencing**: Should we re-run branch scans after reorganizing (via `~/infrafabric-tools/run_branch_scans.sh`), re-index Yologuard references, or audit secrets before merging into the canonical branch?

## Best Path Forward
1. Review `out/addendum_plan.md` to ensure the metadata indexes (Claude sessions, lost-file scan) are embedded or referenced in the new tree.
2. Follow `out/migration_instructions.md` step-by-step to move files, run `scripts/update_links.py` with `--dry-run`, then commit once clean.
3. After rerunning `scripts/scan_if_functions.py`/`scan_if_mentions.py` on the reorganized tree, regenerate `out/aggregate_report.md`, `if_relationship_map.*`, and update `out/clean_spec.md` if guardian/cycle definitions change.
4. Document the new state in `out/summary.txt` as a final delivery bundle so GPT5Pro can re-evaluate the entire project with the same single-source approach.

## Debug Guidance & Surgical Scripts
- Use `scripts/scan_if_functions.py --root=. --out-dir=out/branches/<branch>` to refresh per-branch IF call graphs whenever files move.
- Use `scripts/scan_if_mentions.py --root=. --out-dir=out/branches/<branch>` to regenerate mention graphs after refactors.
- Run `python3 scripts/update_links.py --mapping out/moves.csv --dry-run` before any moves to preview changes; rerun without `--dry-run` after `git mv` commands.
- Execute `scripts/bulk_move_and_update.sh out/moves.csv` from repo root if you want a scripted application of all planned moves plus link update and markdown checks.
- Rerun `~/infrafabric-tools/run_branch_scans.sh` (or the branch-scanning workflow you already used) after reorganizing to verify branch coverage and to regenerate `out/branches` snapshots.

## Next Deliverable
Please unzip `out_bundle.zip` (located both in `/home/setup/infrafabric/` and `/mnt/c/users/setup/downloads/`) so you can walk every artifact with no additional inputs. Review the bundle, note outstanding questions or missing data in `out/todos_priority.md`, and help craft the debug plan (including any additional scripts or checks) so the reorganization can be executed reliably. Once we align on the final instructions, update this bundle with the new state and rerun the automated scans to keep GPT5Pro’s single-document evaluation accurate.
