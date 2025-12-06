#!/usr/bin/env python3
"""
Mini Task Decision Logger

Purpose
-------
Provide a simple, model-agnostic way to log and validate the outcomes
of "mini" tasks into a JSONL ledger.

Each mini task is expected to return a JSON decision with this shape:

{
  "decision": {
    "status": "<completed|escalate_to_max|blocked>",
    "reason": "Short explanation",
    "confidence": 0.0
  },
  "if_ttt_decision_record": {
    "claim": "One-sentence claim",
    "evidence": ["..."],
    "protocols": ["IF.TTT.AUTOSYNC"],
    "confidence": 0.0
  },
  "result": {
    "output": "Code / YAML / text, or empty",
    "notes": "Optional notes for the higher-capacity agent or human operator."
  }
}

This logger:
  - Reads that JSON (from stdin or a file),
  - Validates structure and basic invariants,
  - Appends a normalized record to mini_task_decisions.jsonl:
      {
        "task_id": "...",
        "source": "codex-mini" | "claude-mini" | "...",
        "timestamp": "<ISO8601>",
        "decision": { ... },
        "if_ttt_decision_record": { ... },
        "result": { ... }
      }

By keeping this ledger on disk, any higher-capacity agent (or human)
can later resume work, see which tasks were completed vs escalated,
and why, without depending on chat history.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = REPO_ROOT / "mini_task_decisions.jsonl"

VALID_STATUSES = {"completed", "escalate_to_max", "blocked"}


@dataclass
class DecisionEnvelope:
    task_id: str
    source: str
    timestamp: str
    decision: Dict[str, Any]
    if_ttt_decision_record: Dict[str, Any]
    result: Dict[str, Any]


def _read_json_from_stdin() -> Dict[str, Any]:
    data = sys.stdin.read()
    if not data.strip():
        raise ValueError("No input received on stdin.")
    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON from stdin: {exc}") from exc


def _read_json_from_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON input file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in file {path}: {exc}") from exc


def _ensure_float(value: Any, field_name: str) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number, got {value!r}") from exc
    if not (0.0 <= f <= 1.0):
        raise ValueError(f"{field_name} must be between 0.0 and 1.0, got {f}")
    return f


def validate_decision_payload(payload: Dict[str, Any], task_id: str) -> DecisionEnvelope:
    """
    Validate and normalize a mini task decision payload.
    Raises ValueError on any structural or semantic issues.
    """
    if not isinstance(payload, dict):
        raise ValueError("Top-level decision payload must be a JSON object.")

    decision = payload.get("decision")
    if_ttt = payload.get("if_ttt_decision_record")
    result = payload.get("result")

    if not isinstance(decision, dict):
        raise ValueError("Missing or invalid 'decision' object.")
    if not isinstance(if_ttt, dict):
        raise ValueError("Missing or invalid 'if_ttt_decision_record' object.")
    if not isinstance(result, dict):
        raise ValueError("Missing or invalid 'result' object.")

    status = decision.get("status")
    if status not in VALID_STATUSES:
        raise ValueError(
            f"decision.status must be one of {sorted(VALID_STATUSES)}, got {status!r}"
        )

    reason = decision.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("decision.reason must be a non-empty string.")

    decision_conf = _ensure_float(decision.get("confidence", 0.0), "decision.confidence")
    decision["confidence"] = decision_conf

    # if_ttt_decision_record basic checks
    claim = if_ttt.get("claim")
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("if_ttt_decision_record.claim must be a non-empty string.")

    evidence = if_ttt.get("evidence", [])
    if not isinstance(evidence, list):
        raise ValueError("if_ttt_decision_record.evidence must be a list of strings.")
    for e in evidence:
        if not isinstance(e, str):
            raise ValueError("All if_ttt_decision_record.evidence entries must be strings.")

    if_ttt_conf = _ensure_float(if_ttt.get("confidence", 0.0), "if_ttt_decision_record.confidence")
    if_ttt["confidence"] = if_ttt_conf

    # result checks
    output = result.get("output", "")
    if status == "completed":
        if not isinstance(output, str) or not output.strip():
            raise ValueError(
                "For status 'completed', result.output must be a non-empty string."
            )
    else:
        if not isinstance(output, str):
            raise ValueError("result.output must be a string.")

    # Fill in defaults for optional fields
    result.setdefault("notes", "")

    envelope = DecisionEnvelope(
        task_id=task_id,
        source="",  # filled later
        timestamp=datetime.utcnow().isoformat() + "Z",
        decision=decision,
        if_ttt_decision_record=if_ttt,
        result=result,
    )
    return envelope


def append_decision(
    envelope: DecisionEnvelope,
    source: str,
    log_path: Path = DEFAULT_LOG_PATH,
) -> None:
    """
    Append a validated decision envelope to the JSONL log.
    """
    envelope.source = source
    record = asdict(envelope)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=False) + "\n")


def run_demo() -> None:
    """
    Demo mode: validate and print a sample decision envelope
    without writing to the real log.
    """
    sample_payload = {
        "decision": {
            "status": "completed",
            "reason": "Task was small and fully covered by the provided function body.",
            "confidence": 0.9,
        },
        "if_ttt_decision_record": {
            "claim": "Mini agent successfully refactored the square(x) function locally.",
            "evidence": [
                "Function body was fully provided.",
                "No cross-file dependencies required.",
                "Requirements were simple: docstring + type hints + same behavior.",
            ],
            "protocols": ["IF.TTT.AUTOSYNC"],
            "confidence": 0.9,
        },
        "result": {
            "output": "def square(x: float) -> float:\n    \"\"\"Return the square of x.\"\"\"\n    return x * x\n",
            "notes": "Behavior preserved; added docstring and type hints.",
        },
    }
    task_id = "T_demo_1"
    envelope = validate_decision_payload(sample_payload, task_id=task_id)
    envelope.source = "demo-mini"
    print(json.dumps(asdict(envelope), indent=2, sort_keys=False))


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Mini Task Decision Logger - validate and append mini task decisions to a JSONL log."
    )
    parser.add_argument(
        "--task-id",
        type=str,
        help="ID of the mini task this decision corresponds to (required unless --demo).",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="codex-mini",
        help="Identifier for the source agent/model (default: codex-mini).",
    )
    parser.add_argument(
        "--json-file",
        type=str,
        help="Path to a JSON file containing the decision payload. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=str(DEFAULT_LOG_PATH),
        help=f"Path to JSONL log file (default: {DEFAULT_LOG_PATH}).",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo mode: validate and print a sample envelope without writing to the log.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)

    if args.demo:
        run_demo()
        return

    if not args.task_id:
        raise SystemExit("Error: --task-id is required unless --demo is used.")

    # Load payload
    if args.json_file:
        payload = _read_json_from_file(Path(args.json_file))
    else:
        payload = _read_json_from_stdin()

    # Validate and append
    envelope = validate_decision_payload(payload, task_id=args.task_id)
    append_decision(envelope, source=args.source, log_path=Path(args.log_file))

    print(
        f"Appended decision for task_id={args.task_id!r} from source={args.source!r} to {args.log_file}"
    )


if __name__ == "__main__":
    main()

