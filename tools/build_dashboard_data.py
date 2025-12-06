#!/usr/bin/env python3
"""
Build dashboard data for GitHub Pages.

Reads:
  - mini_task_decisions.jsonl (ledger of mini task outcomes)
  - mini_tasks.json (worklist)
  - STATE_S0.md (optional; summarised if present)

Outputs (under docs/dashboard/data):
  - decisions.json      : sanitized list of decision records
  - summary.json        : status counts, rates, timestamps
  - tasks_open.json     : open mini tasks (not completed)
  - state.json          : minimal snapshot from STATE_S0.md (if available)

All outputs are JSON and safe to publish (sensitive outputs are redacted).
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = REPO_ROOT / "mini_task_decisions.jsonl"
TASKS_PATH = REPO_ROOT / "mini_tasks.json"
STATE_PATH = REPO_ROOT / "STATE_S0.md"

DASHBOARD_DIR = REPO_ROOT / "docs" / "dashboard"
DATA_DIR = DASHBOARD_DIR / "data"

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


def load_ndjson(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines; they should be handled upstream
                continue
    return records


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None


def safe_timestamp(ts: Optional[str]) -> Optional[str]:
    if not ts:
        return None
    try:
        # Normalize to Zulu if parseable
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime(DATE_FMT)
    except ValueError:
        return None


def sanitize_decision(dec: Dict[str, Any]) -> Dict[str, Any]:
    # Extract minimal safe fields
    decision = dec.get("decision", {})
    trace = dec.get("trace", {}) or dec.get("if_ttt_decision_record", {})
    result = dec.get("result", {})

    return {
        "task_id": dec.get("task_id"),
        "source": dec.get("source"),
        "timestamp": safe_timestamp(dec.get("timestamp")),
        "status": decision.get("status"),
        "reason": decision.get("reason"),
        "confidence": decision.get("confidence"),
        "trace": {
            "claim": trace.get("claim"),
            "evidence": trace.get("evidence", []),
            "protocols": trace.get("protocols", []),
            "confidence": trace.get("confidence"),
        },
        "result": {
            "notes": result.get("notes"),
            "sensitive": bool(result.get("sensitive", False)),
            # Do not publish output if sensitive
            "output": None if result.get("sensitive") else result.get("output"),
        },
        "routing": dec.get("routing", {}),
    }


def summarize_state_md(path: Path) -> Dict[str, Any]:
    """
    Very light extraction from STATE_S0.md:
    - status lines that look like "R1: completed" etc.
    """
    if not path.exists():
        return {}

    status_map: Dict[str, str] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"\s*(R\d+)\s*[:\-]\s*(completed|in[_ ]progress|pending)", line, re.IGNORECASE)
            if match:
                rid = match.group(1).upper()
                status_map[rid] = match.group(2).replace(" ", "_").lower()
    return {"roadmap_status": status_map, "last_scanned": datetime.utcnow().strftime(DATE_FMT)}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    decisions_raw = load_ndjson(LEDGER_PATH)
    tasks_raw = load_json(TASKS_PATH) or {}

    decisions = [sanitize_decision(d) for d in decisions_raw]

    # Summary stats
    status_counts = Counter(d.get("status") for d in decisions if d.get("status"))
    total = sum(status_counts.values())
    escalation_rate = (status_counts.get("escalate_to_max", 0) / total) if total else 0.0
    block_rate = (status_counts.get("blocked", 0) / total) if total else 0.0

    # Timeline by date
    timeline = defaultdict(lambda: Counter())
    for d in decisions:
        ts = d.get("timestamp")
        if not ts:
            continue
        day = ts.split("T")[0]
        timeline[day][d.get("status")] += 1
    timeline_list = [
        {"date": day, "counts": dict(counts)}
        for day, counts in sorted(timeline.items())
    ]

    # Open tasks: those in mini_tasks.json not marked completed
    completed_ids = {d.get("task_id") for d in decisions if d.get("status") == "completed"}
    open_tasks = []
    for t in tasks_raw.get("mini_tasks", []):
        if t.get("id") not in completed_ids:
            open_tasks.append({
                "id": t.get("id"),
                "kind": t.get("kind"),
                "target": t.get("target"),
                "summary": t.get("summary"),
                "allow_codegen": t.get("allow_codegen", tasks_raw.get("defaults", {}).get("allow_codegen", False)),
            })

    summary = {
        "generated_at": datetime.utcnow().strftime(DATE_FMT),
        "total_decisions": total,
        "status_counts": dict(status_counts),
        "escalation_rate": escalation_rate,
        "block_rate": block_rate,
        "timeline": timeline_list,
    }

    # State snapshot (optional)
    state_snapshot = summarize_state_md(STATE_PATH)

    # Write outputs
    (DATA_DIR / "decisions.json").write_text(json.dumps(decisions, indent=2), encoding="utf-8")
    (DATA_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (DATA_DIR / "tasks_open.json").write_text(json.dumps(open_tasks, indent=2), encoding="utf-8")
    (DATA_DIR / "state.json").write_text(json.dumps(state_snapshot, indent=2), encoding="utf-8")

    print("Dashboard data written to", DATA_DIR)


if __name__ == "__main__":
    main()

