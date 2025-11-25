# Moves Validation Report

## Summary
- Verified `out/moves_expanded.csv` and `out/moves_external_candidates.csv` against the live filesystem.
- Found no conflicting `new_path` targets, but several `old_path` references currently point to files that do not exist inside `/home/setup/infrafabric`.
- Added a supplemental “wave 2” plan (`out/moves_expanded_v2.csv`) to relocate the philosophy dataset and meta docs into `docs/philosophy/` and `infra/meta/`.

## Missing sources in `moves_expanded.csv`
| old_path | expected location | note |
| --- | --- | --- |
| `IF-momentum.md` | `/home/setup/infrafabric/IF-momentum.md` | File not present; consider generating it or linking to the momentum chapter inside `INFRAFABRIC-COMPLETE-DOSSIER-v11`. |
| `docs/evidence/GEMINI-TO-SYNTHESIS-SAGA.md` | `/home/setup/infrafabric/docs/evidence/GEMINI-TO-SYNTHESIS-SAGA.md` | Document not found; may live in an external bundle or be pending export from the Gemini workspace. |
| `docs/evidence/gemini-logs/.../Evaluate Project_ Yologuard Documentation And Code` | ... | No matching path in the repo yet; the evaluation log may still live under `out/branches` or Windows downloads. |
| `docs/evidence/gemini-logs/.../Extraordinary Body Of Work_` | ... | Same as above. |
| `docs/evidence/gemini-logs/TTT-COMPLIANCE.md` | ... | Same as above. |
| `CLOUD-COMMS-TASK-PROMPT.md` | `/home/setup/infrafabric/CLOUD-COMMS-TASK-PROMPT.md` | File is missing; a local copy should be imported to keep the ingestion directions together with the repo. |
| `CLOUD-TRANSITION-PLAN.md` | ... | Missing; previously referenced in external scans but not present here. |
| `SESSION-HANDOVER-TO-CLOUD.md` | ... | Missing plan sheet (likely lives in the Windows/home root). |
| `SESSION_HANDOFF_2025-11-08_IF-ARMOUR.md` | ... | Missing handoff note. |
| `IF_CONNECTIVITY_ARCHITECTURE.md` | ... | Connectivity spec absent from the repo root but noted by Yologuard scans. |
| `EXTERNAL_REVIEW_PROMPT_IF_FULL.md` | ... | Missing prompt currently stored outside the repo. |
| `EXTERNAL_REVIEW_ARENA_*` | ... | All three referenced arena docs are absent; expected to arrive from downloads or archives. |
| `CALL_FOR_EXTERNAL_REVIEW.md` | ... | Handoff prompt missing. |
| `CONTRIBUTING.md` | ... | Not currently part of repo; may need to be added from the external workspace. |
| `SECURITY.md` | ... | The security posture note has not been committed yet. |
| `code/yologuard/GPT5_REQUIREMENTS.md` | ... | Requirements doc missing; it may belong under `code/yologuard/benchmarks/` or a new `infra/tools/yologuard` directory. |

*(All missing entries appear to live outside `/home/setup/infrafabric` today; add them from their originating branches before running the reorg.)*

## Moves tree consistency
- No `new_path` collisions were detected across either CSV.
- The `new_path` values use `infra/`, `docs/`, and `infra/tools/` roots in line with `out/final_tree.yaml`, though the `docs/dossiers/` and `docs/legacy/` subtrees from `moves_external_candidates.csv` are new namespaces that should be documented in the final tree narrative before the CLI agent commits them.
- The external plan also introduces `infra/tools/yologuard/external` and `infra/tools/yologuard/reproducibility`, both of which slot under `infra/tools/` and mirror the `code/yologuard` purpose noted in `docs/meta/IF_COMPONENT_STATUS.md`.

## Next action (wave 2)
- `out/moves_expanded_v2.csv` proposes relocating the philosophy dataset (`philosophy/IF.philosophy-*`) into `docs/philosophy/` and moving the meta docs from `docs/meta/` into `infra/meta/`. These moves keep the philosophy data accessible while aligning metadata with the new clearinghouse described in `INFRA_REORG_PLAN.md`.
- Updated `/home/setup/infrafabric/out/moves_external_candidates.csv` so the COMPLETE-v7.03 source now points to the existing `Downloads/infrafabric/infrafabric-complete-v7.03.md` file rather than a missing `drive-download` path.
