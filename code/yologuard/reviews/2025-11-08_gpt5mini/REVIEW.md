# External Review — Static (Plain-Language)

Reviewer: GPT-5 Thinking mini (independent static review)
Repo: https://github.com/dannystocker/infrafabric (master)
Date: 2025-11-08

## Executive Summary
InfraFabric is a coherent, well-documented attempt to make philosophy executable: governance, ethics, and epistemology are translated into auditable artifacts and code. Strengths include rigorous traceability (TTT), a practical governance model (IF.guard), and concrete implementations (IF.yologuard with IEF + TTT). The primary gaps are runnable reproducibility bundles for headline claims and an adversarial test suite. Address those and the project is ready for broader external scrutiny and applied research settings.

## Strengths
- Exceptional traceability and reviewer guidance (TTT manifests, external review prompt, sticky metrics)
- Operationalized philosophy (IF.ground mapped to engineering patterns; multi-voice council)
- Concrete components and tools (yologuard detector, harness, governance artifacts)

## Risks & Deficiencies
- Missing reproducible, pinned runbooks for key numeric claims (recall/FP, cost proofs)
- Latency/cost tradeoffs not summarized for production SLAs
- Adversarial surfaces (forgery/mode-attestation) need test definitions and cases
- Enforcement path from guardian decision to runtime controls needs an operations playbook

## Recommended Actions (Prioritized)
1) Add a reproducibility bundle per headline claim (scripts, pinned deps, seed data, outputs)
2) Publish a one-page cost/latency matrix for IF.search/IF.optimise scenarios
3) Ship a 10-case adversarial test suite (spoofed metadata, doc-like examples, mode-claims)
4) Write a 2-page enforcement runbook tying guardian decisions to runtime hooks and keys
5) Separate poetic narrative from core specs to reduce mixed-audience confusion

## Sticky Metrics (suggested)
- IF.yologuard: Detection Recall @ 1% FPR (clean corpus) in addition to benchmark invariants
- IF.guard: Median time-to-resolution for strategic events (<48h)
- IF.search: Average end-to-end latency (8-pass vs hybrid)
- IF.optimise: Cost per standard task and percent saved
- IF.federate: Mode-attestation failure rate

## Limitations
Static, forensic review only (no code execution). Benchmarks and harnesses were not run in this review. The repo contains what is needed to run them; this review focused on documentation, architecture, and governance substance.
