# Migration Instructions

Before running the reorg, refresh the tree and work from a new branch:
```
git checkout -b infra/reorg-$(date +%Y%m%d)
```

Move the primary assets listed in `out/moves.csv`:
```
git mv "IF-foundations.md" "infra/guardians/IF-foundations.md"
git mv "IF-vision.md" "infra/cycles/IF-vision.md"
git mv "IF-armour.md" "infra/guardians/IF-armour.md"
git mv "docs/evidence/INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml" "infra/ingestion/evaluations/INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml"
git mv "docs/evidence/INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md" "infra/ingestion/evaluations/INFRAFABRIC_COMPREHENSIVE_EVALUATION_PROMPT.md"
```

Run the link updater in dry-run mode to verify referenced paths:
```
python3 scripts/update_links.py --mapping out/moves.csv --dry-run
```
Once the dry-run passes, execute the real rewrite and rerun the script to refresh backups:
```
python3 scripts/update_links.py --mapping out/moves.csv
```

Finally stage everything and finalize the branch:
```
git add -A
git commit -m "infra: structural reorg"
```
