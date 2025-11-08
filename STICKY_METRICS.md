# InfraFabric — Sticky Metrics (TTT‑aligned)

Purpose: One non‑negotiable guiding metric per component. Each metric is objective, reproducible, and mapped to a simple verification step to orient developers new to the IF universe.

- IF.yologuard
  - Sticky Metric: “Benchmark invariants hold”: 107/96 detections (component‑inclusive) AND 42/42 file coverage on leaky‑repo.
  - Verify: `python3 code/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py` → expect 107/96, 42/42.

- IF.guard
  - Sticky Metric: “Deliberation captured”: 100% of releases have a guardian handoff JSON with decision + dissent notes.
  - Verify: Presence of `code/yologuard/integration/guardian_handoff_result.json` (or module‑specific equivalent) updated in the release commit.

- IF.connect
  - Sticky Metric: “Message schema consistency”: 100% of messages validate against IFMessage schema; p95 round‑trip latency budget declared per level (0–4).
  - Verify: Lint/validate messages in integration tests; CI prints p95 latency budget per level.

- IF.armour.honeypot (planned)
  - Sticky Metric: “No‑exfil challenge”: ≥1 honey challenge verified in CI without network calls (sandboxed), evidence recorded in manifest.
  - Verify: CI artifact includes redacted challenge + manifest.

- IF.armour.learner (planned)
  - Sticky Metric: “Closed‑loop synthesis”: ≥5 patterns synthesized from public CVEs with 0 regressions on falsifiers.
  - Verify: Learner run produces a diff; falsifiers remain 0 FP.

- IF.witness
  - Sticky Metric: “Recursive validation present”: Every major analysis includes a MARL loop entry and at least one falsifiable prediction.
  - Verify: Papers/docs cite MARL stage and prediction artifact path.

- IF.foundations / IF.vision
  - Sticky Metric: “Philosophy → code link exists”: All philosophical claims referenced in docs have at least one code citation (path:line) and one test/demo.
  - Verify: Cross‑reference table in docs (or auto‑generated) with working links.

