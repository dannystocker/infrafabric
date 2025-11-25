# GPT‑5‑mini Home/Windows IF Index Handoff

You are GPT‑5‑mini running in the same WSL environment as another agent. Your job in this task is **ONLY** to inventory InfraFabric‑related material in the wider filesystem so nothing important is lost when we clean up and reorganize.

Repo root: `/home/setup/infrafabric`
All outputs you write must go under: `/home/setup/infrafabric/out/`

## 1. Scope & goals

Scan these locations for **InfraFabric / IF / Yologuard**-related files:
- `/home/setup`  (Linux home)
- `/mnt/c/users/setup`  (Windows profile)

Do NOT modify or move any files. You are only indexing and classifying.

We care about files that look related to:
- InfraFabric conceptually (`INFRAFABRIC`, `IF-vision`, `IF-foundations`, `IF.armour`, `IF.witness`, `IF.guard`, `IF.optimise`, etc.)
- Yologuard (any path containing `yologuard` or `YOLOGUARD`)
- Philosophy & evaluation artifacts (`IF.philosophy`, `INFRAFABRIC_EVAL`, Gemini / Codex evaluation logs)

## 2. Home directory index (/home/setup)

1. Search under `/home/setup` (excluding `.git`, `.venv*`, `node_modules`, large caches) for files whose **path OR content** matches case-insensitive patterns:
   - `infrafabric`
   - `IF-vision` / `IF-vision.md`
   - `IF-foundations`
   - `IF-armour`
   - `IF-witness`
   - `IF.yologuard` / `yologuard`
   - `INFRAFABRIC_EVAL` / `INFRAFABRIC-COMPLETE-DOSSIER`

2. Write a summary index to:
   - `out/home_if_index.txt`

Format for each line:
- `TYPE|PATH|HINT`

Where:
- `TYPE` is one of: `SAFE_DOC`, `CODE_NONSECRET`, `SECRET_RISK`, `UNKNOWN`.
- `PATH` is the absolute path.
- `HINT` is a short note (e.g., `yologuard reproducibility bundle`, `v7 dossier`, `evaluation logs`).

Heuristics:
- Mark as `SECRET_RISK` anything under directories like `.security`, `.ssh`, `.claude`, `.git`, or that clearly looks like credentials / tokens.
- Mark as `CODE_NONSECRET` any `.py`, `.sh`, `.js`, `.ts` that is clearly logic (not configs with keys).
- Mark as `SAFE_DOC` for `.md`, `.txt`, `.pdf`, `.tex` that are conceptual docs or logs.
- Use `UNKNOWN` when in doubt.

## 3. Windows profile index (/mnt/c/users/setup)

Do a similar scan for the Windows side:
- Root: `/mnt/c/users/setup`
- Focus on subtrees that are likely to contain project files: `Downloads/`, `Documents/`, `Desktop/`, any `infrafabric*` folders, evaluation logs, annex bundles, etc.

Write the index to:
- `out/windows_if_index.txt`

Use the same `TYPE|PATH|HINT` format and heuristics as above. It is OK to skip obviously unrelated system directories (e.g., AppData, .cache equivalents) if they are too noisy.

## 4. Summary report

After building both indexes, write a short human-readable summary to:
- `out/fs_if_index_summary_mini.md`

Include:
- Counts of files per TYPE for `/home/setup` and `/mnt/c/users/setup`.
- Notable clusters (e.g., "infrafabric-clean bundle here", "yologuard reproducibility pack there").
- A list of **top priority candidates** to consider importing into the Git repo (paths only, no contents), especially:
  - Any `IF.yologuard_v3.py` locations outside the repo,
  - Any `INFRAFABRIC-COMPLETE-*` or annex bundles not yet in `~/infrafabric`.

## 5. How to run

You should:
- Use shell and file-read tools available to you (e.g., `find`, `rg`, `grep`) to implement these scans.
- Be careful with performance: avoid recursing into obviously huge or binary-heavy trees unnecessarily.
- Never print actual secret values; only reference file paths.

When finished, your deliverables are:
- `out/home_if_index.txt`
- `out/windows_if_index.txt`
- `out/fs_if_index_summary_mini.md`

Do not modify any other files. Do not delete anything. This task is read/scan only.
