# Secrets & Yologuard Risk Mini Report

## Scan methodology
- Each of the 28 branches under `out/branches/` produces `secrets_candidates.txt` and `yologuard_refs.txt`. The counts quoted below are the number of branch directories that reference a given file path, which captures systemic reuse across timelines.

## Most-repeated secrets candidates
| Path | Branch hits | Risk level | Recommendation |
| --- | --- | --- | --- |
| `/home/setup/infrafabric/README.md` | 27 | LOW | Keep in place but hard-link or reference the canonical README instead of copying it; monitor for drift before reorg so future deletes do not break documentation bundles. |
| `/home/setup/infrafabric/annexes/infrafabric-IF-annexes.md` | 26 | MEDIUM | Centralize inside `docs/annexes/` (as per final tree) and sanitize any embedded credentials before copying into multiple branches. |
| `/home/setup/infrafabric/annexes/ANNEX-[N|O|P]-*.md` (N/O/P) | 26 | MEDIUM | Tag the annex folder as guarded, keep a single source of truth, and redact any guardian-protected notes before reusing in new branches. |
| `/home/setup/infrafabric/agents.md` | 23 | MEDIUM | Treat this as a coordinated meta document; gate edits through the reorg branch so the same content does not drop into high-risk branches without review. |
| `/home/setup/infrafabric/infrafabric/*.py` (manifests, guardians, coordination) | 22 | HIGH | These Python files appear in every branch’s secret sweep because they likely expose guardian APIs; ensure the future reorg explicitly documents their security controls, and avoid bundling them with downstream releases until they pass a secrets audit. |

## Top Yologuard hotspots
| Path | Branch hits | Risk level | Recommendation |
| --- | --- | --- | --- |
| `/home/setup/infrafabric/code/yologuard/GPT5_REQUIREMENTS.md` | 22 | HIGH | This is the most widely flagged Yologuard definition; treat it as a guarded artifact, ensure tokenized references are scrubbed, and rotate any secrets or keys referenced in the detector’s requirements before merging. |
| `/home/setup/infrafabric/IF_CONNECTIVITY_ARCHITECTURE.md` | 22 | MEDIUM | Contains Yologuard service hooks; tag it as an orchestration doc, keep a canonical copy, and review the GRPC endpoint descriptions for leaked secrets. |
| `/home/setup/infrafabric/EXTERNAL_REVIEW_*` family (prompt, arena bundle, superbundle) | 22+ | MEDIUM | These collateral prompts contain public/external metrics; mark them as evaluation-only and avoid shipping them intact into new outputs without re-running `scripts/update_links.py` so metadata stays consistent. |
| `/home/setup/infrafabric/SESSION-HANDOVER-TO-CLOUD.md` & `/home/setup/infrafabric/CLOUD-TRANSITION-PLAN.md` | 17 | MEDIUM | These ingestion briefs document Yologuard blockers and benchmarks; they should live under `infra/ingestion/operations/` and be audited for budget/credential mentions. |
| `/home/setup/infrafabric/SECURITY.md` | 17 | HIGH | Security posture docs appear in many Yologuard sweeps; before reorg, verify that no rotated credentials are embedded and add a note that the file is a high-risk asset requiring ops review. |

## Actions before the reorg commit
1. Normalize the repeated annex/guardian docs by deduplicating and sanitizing them in one directory so the scanner does not re-flag stale copies.
2. Quarantine or rotate secrets that may be embedded in the `infrafabric/*.py` runtime sources and the Yologuard requirement doc, since they show up across every branch scan.
3. Document the Yologuard blocker path (`SESSION-HANDOVER-TO-CLOUD` → `CLOUD-TRANSITION-PLAN`) in the final tree so future reorg work can verify the benchmark status before any merge.
4. Keep the aggregator outputs (aggregate report, relationship map, etc.) in `out/` but mark them in `infra/meta/` references so the new hierarchy preserves their provenance.
