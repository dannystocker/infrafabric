#!/usr/bin/env python3
"""
Control Arm: Simple Governance (Single Technical Guardian)
Fast, deterministic, rule-based decisions.
"""

import json
import time
from pathlib import Path

OUTDIR = Path("experiments/ab_council_test/results/control")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Simple rule-based guardian
GUARDIAN_SYSTEM = """You are Technical Guardian (T-01) from InfraFabric.
Your role: Apply clear technical rules, prevent runaway acceleration.

Decision framework:
1. If credentials detected → QUARANTINE (zero-tolerance)
2. If bias detected → DOCUMENT and keep heterogeneous consensus
3. If forged citation → REJECT proposal

Respond ONLY with valid JSON:
{
  "decision": "quarantine|reject|accept|escalate",
  "rationale": "Brief technical reasoning (max 2 sentences)",
  "confidence": 0.0-1.0,
  "citations": ["IF.chase:5%_rule", "IF.ground:principle_3"]
}
"""

def make_decision(case):
    """Simulate simple guardian decision (deterministic rule-based)"""
    prompt = case['prompt']

    # Simple pattern matching (no LLM needed for control - pure rules)
    if 'credentials' in prompt.lower() and 'akia' in prompt.lower():
        return {
            "decision": "quarantine",
            "rationale": "Credentials detected. Zero-tolerance policy applies.",
            "confidence": 1.0,
            "citations": ["IF.chase:bystander_protection", "IF.yologuard:v3_redaction"]
        }

    elif 'bias' in prompt.lower() and 'mai-1' in prompt.lower():
        return {
            "decision": "accept_with_weighting",
            "rationale": "Heterogeneous consensus strengthens detection. Document bias, keep MAI-1 with reduced weight.",
            "confidence": 0.85,
            "citations": ["IF.federate:diversity_principle", "IF.core:multi_model_consensus"]
        }

    elif 'forged' in prompt.lower() and 'doi' in prompt.lower():
        return {
            "decision": "reject",
            "rationale": "Forged citation violates epistemic integrity. Proposal rejected.",
            "confidence": 0.95,
            "citations": ["IF.ground:principle_1_observable_artifacts", "IF.trace:immutable_audit"]
        }

    else:
        return {
            "decision": "escalate",
            "rationale": "Case does not match clear rules. Escalating to human review.",
            "confidence": 0.5,
            "citations": []
        }

def run_case(case):
    """Execute control arm decision"""
    t0 = time.time()
    decision = make_decision(case)
    t1 = time.time()

    result = {
        "case_id": case["case_id"],
        "arm": "control",
        "category": case["category"],
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_s": t1 - t0,
        "decision_data": decision,
        "tokens_used": 0,  # Rule-based, no LLM calls
        "manifest_id": f"manifest:control:{case['case_id']}"
    }

    outfile = OUTDIR / f"{case['case_id']}.json"
    with outfile.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result

def main():
    cases_file = Path("experiments/ab_council_test/cases.jsonl")

    print("=== CONTROL ARM: Simple Governance ===")
    print("Guardian: Technical (T-01)")
    print("Strategy: Rule-based, deterministic\n")

    with cases_file.open() as fh:
        for line in fh:
            case = json.loads(line)
            result = run_case(case)
            print(f"✓ {case['case_id']}: {result['decision_data']['decision']} (confidence: {result['decision_data']['confidence']})")
            print(f"  Rationale: {result['decision_data']['rationale']}")
            print(f"  Duration: {result['duration_s']:.3f}s\n")

    print(f"Results saved to: {OUTDIR}")

if __name__ == "__main__":
    main()
