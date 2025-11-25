# External Import Plan Notes

- Imported the cleanest INFRAFABRIC dossiers (v11) into docs/dossiers for reviewers to find the latest narrative, while sending older variants (v8, v7.01, v7.03) into docs/legacy/dossiers to preserve the history without cluttering the canonical tree.
- Captured the INFRAFABRIC COMPLETE SOURCE INDEX from the Windows Downloads package so the repo keeps the master inventory alongside the new dossier copies.
- Brought in external Yologuard v3 implementations (mcp-multiagent-bridge, digital-lab reproducibility bundle, Codex review edition) into infra/tools/yologuard/[external|reproducibility] so we can compare scanner variations before refactoring into src/.
- Paths follow INFRA_REORG_PLAN.md quality goal (docs/dossiers, docs/legacy, infra/tools/yologuard) and align with final_tree.yaml policy on annex/evidence placement.
