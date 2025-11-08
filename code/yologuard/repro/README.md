## IF.yologuard Reproducibility Bundle (v1)

This folder provides minimal, pinned commands to reproduce headline claims and generate forensics artifacts.

Prereqs
- Python 3.10+
- Optional: `regex` library for regex timeouts; `pipx` to install Gitleaks/TruffleHog for head‑to‑head

Quick Start
```bash
cd infrafabric
bash code/yologuard/repro/run_benchmark.sh     # 107/96; 42/42
bash code/yologuard/repro/run_forensics.sh     # JSON + SARIF + graph + manifest + PQ
# Optional (requires pipx gitleaks and trufflehog):
bash code/yologuard/repro/run_head2head.sh
```

Install optional tools
```bash
python3 -m pip install --user regex
python3 -m pip install --user pipx || true
pipx install gitleaks
pipx install trufflehog
```

Notes
- No live validation, no exfiltration (Kantian duty).
- Artifacts are written to `code/yologuard/reports/<timestamp>/` and `repro/out/<timestamp>/`.

