# Security Notes (Draft)

## Main risk surfaces
1. **Over-referenced narrative docs** – `README.md`, the annexes under `annexes/`, and the guardian-focused `papers/IF-*` files appear in 22–27 branch scans (`out/secrets_yologuard_risk_mini.md`). Treat them as high-value references, sanitize any embedded credentials, and keep the committed copies under `docs/annexes/` or `docs/legacy/` so copies do not proliferate when the tree is reorganized.
2. **Operational manifests** – artifacts such as `agents.md`, `SESSION-*` handoff notes, and the many `INFRAFABRIC-COMPLETE-*` dossiers show up repeatedly in both secrets and Yologuard sweeps. Before moving them into `infra/` or `docs/`, scrub and confirm that budgets/endpoints/public keys are redacted or referenced via a vault.
3. **Yologuard-facing documentation** – `code/yologuard/GPT5_REQUIREMENTS.md`, `IF_CONNECTIVITY_ARCHITECTURE.md`, `CLOUD-*` transition plans, and the External Review prompts are listed in `out/secrets_yologuard_risk_mini.md` as hotspots. During the reorg, host these files in `infra/tools/yologuard/` or `infra/meta/` with the appropriate classification so the high-visibility surface isn’t mistaken for code.
4. **Implementation gap risk** – `docs/meta/IF_COMPONENT_STATUS.md` notes that only IF.yologuard has an in-repo implementation; the other components remain spec-only or external. That means the repository cannot enforce the multi-agent consensus or witness promises yet, so treat LLM/guardian claims as design artifacts until code arrives.

## Recommended handling
- **Sanitize before you commit:** Keep secrets in an external vault and inject only placeholders/links into committed docs. Run `python code/yologuard/src/IF.yologuard_v3.py` (or the packaged CLI) against each tagged document before moving it to `infra/`/`docs/`.
- **Document-level gating:** Keep high-risk documents in `docs/legacy/` or `infra/meta/` while referencing them from sanitized summaries. Use `.gitignore` to exclude `out/branches`, the Claude workspace, and `Downloads/` directories flagged by the indexes.
- **Yologuard gating for new files:** Configure future workflows to run `yologuard` on any directory that contains new instrumentation or ingestion notes (docs/evidence, infra/ingestion, etc.) so the scanner becomes the first line of defense.

## PR reviewer checklist (auth / secrets / evidence)
1. Was the change scanned with `tests/test_yologuard.py` or `python code/yologuard/src/IF.yologuard_v3.py`? (The new test vectors in `out/yologuard_test_vectors.md` should guide coverage.)
2. Does the PR introduce updates to dossiers, annexes, or prompts listed in `out/secrets_yologuard_risk_mini.md`? If so, confirm those files no longer expose credentials or budget figures.
3. Are there new references to sensitive directories (e.g., `out/branches`, `.claude`, or Claude session dumps)? Keep the final tree free of direct pointers to the scanned workspace.
4. If the PR touches code/yologuard, ensure new patterns have narrative justification in `papers/IF-armour.md` and the feature is recorded in `docs/meta/IF_COMPONENT_STATUS.md`.
5. Confirm that `infra/meta/security/` (or the future `infra/meta/` area) captures every security-relevant change: mention new policy docs, redaction instructions, or gating controls.

**Note:** Until the multi-agent consensus and witness layers described in `IF-armour.md` and `papers/IF-witness.md` ship as runtime code, treat them as design goals. The security posture described in `infra/meta/security/SECURITY.md` should reflect what is actually enforced today (primarily the static Yologuard detector).
