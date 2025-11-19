# Yologuard v3 – Secret Detector (Static Confucian Analysis)

This directory contains the **IF.yologuard v3** secret detector implementation referred to throughout the InfraFabric papers and annexes.

## Files

- `src/IF.yologuard_v3.py` – main detector implementation (published on branch `yologuard/v3-publish`).
- `versions/IF.yologuard_v3.py` – alias copy, matching historical references in documentation.
- `benchmarks/` – summary metrics and results JSON from past evaluations.
- `reports/` – human‑readable benchmark reports and SARIF logs.

## What This Code Actually Does

`IF.yologuard_v3.py` is a single‑file **static secret scanner** with:

- **Entropy‑based token detection** (Shannon entropy) to find high‑entropy strings.
- **Recursive decoding** of Base64/hex/JSON/XML payloads to expose hidden secrets.
- A large library of **regex patterns** for common secret formats (API keys, OAuth tokens, JWTs, passwords, salts, etc.).
- A “Confucian relationship” heuristic that:
  - Looks for **user–password** pairs,
  - **Key–endpoint** pairs (API key near an endpoint URL),
  - **Token–session** patterns,
  - **Cert–authority** chains.

This **relationship mapping** is used to down‑rank isolated high‑entropy strings and up‑rank tokens that are clearly credentials, reducing false positives.

## What It Does *Not* Do (Yet)

The `IF-armour.md` paper describes Yologuard as a **4‑stage immune system** with:

- A multi‑LLM “Multi‑Agent Consensus” stage,
- Thymic selection and regulatory veto agents,
- Live deployment gating.

Those stages are **not implemented** in this repository. This code is:

- A deterministic Python script,
- No LLM calls or orchestration,
- No long‑running service wrapper.

Treat the paper as a **design document**, and this directory as the current, static implementation.

## Running Locally

From the repo root:

```bash
python code/yologuard/src/IF.yologuard_v3.py path/to/file_or_directory
```

You can also import and use it as a library once it is refactored into a package (future work).

## Future Work

- Refactor into a package under `src/infrafabric/yologuard/`.
- Split regex rules and relationship logic into separate modules.
- Add unit tests for:
  - Entropy detection and decoding,
  - Relationship mapping,
  - Each major pattern group (AWS, JWT, OAuth, etc.).
- Wire into CI to self‑scan this repo (with appropriate exclusions for test fixtures).

