#!/usr/bin/env python3
"""
Sanitize dashboard/public data by removing or masking denylisted tokens.

Reads (if present):
  - denylist.json (not committed; add to .gitignore)
    Format: { "denylist": ["sensitive1", "sensitive2"], "mask": "[REDACTED]" }

Sanitizes:
  - docs/dashboard/data/decisions.json
  - docs/dashboard/data/tasks_open.json
  - docs/dashboard/data/summary.json
  - docs/dashboard/data/state.json

Default mask: "[REDACTED]"

Intended usage:
  - Run after generating dashboard data (build_dashboard_data.py) and before publishing.
  - Keep denylist.json local; do not commit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
DASH_DATA = REPO_ROOT / "docs" / "dashboard" / "data"
DENYLIST_PATH = REPO_ROOT / "denylist.json"

TARGET_FILES = [
  "decisions.json",
  "tasks_open.json",
  "summary.json",
  "state.json",
]


def load_denylist(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"denylist": [], "mask": "[REDACTED]"}
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        "denylist": data.get("denylist", []),
        "mask": data.get("mask", "[REDACTED]"),
    }


def mask_value(val: Any, tokens: List[str], mask: str) -> Any:
    if isinstance(val, str):
        out = val
        for t in tokens:
            if t:
                out = out.replace(t, mask)
        return out
    if isinstance(val, list):
        return [mask_value(v, tokens, mask) for v in val]
    if isinstance(val, dict):
        return {k: mask_value(v, tokens, mask) for k, v in val.items()}
    return val


def sanitize_file(path: Path, tokens: List[str], mask: str) -> None:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    sanitized = mask_value(data, tokens, mask)
    with path.open("w", encoding="utf-8") as f:
        json.dump(sanitized, f, indent=2)
    print(f"Sanitized {path.name}")


def main() -> None:
    cfg = load_denylist(DENYLIST_PATH)
    tokens = cfg.get("denylist", [])
    mask = cfg.get("mask", "[REDACTED]")
    if not tokens:
        print("No denylist.json or empty denylist; nothing to sanitize.")
        return
    for fname in TARGET_FILES:
        sanitize_file(DASH_DATA / fname, tokens, mask)


if __name__ == "__main__":
    main()
