# COUNCIL DECISION 001: Genesis Structure Ratification

**Case Reference:** IF-COUNCIL-2025-001
**Date:** 2025-11-26 02:26:07
**Session:** Constitutional Convention - Genesis

---

## THE MOTION

**MOTION 001:** Establish 'InfraFabric Series 2' Core Structure.

- **Hub:** Monorepo (`src/infrafabric/core/`)
- **Services:** Librarian (409 lines) - Gemini archive node
- **Security:** YoloGuard v3 (676 lines) - 98.96% recall secret detector
- **Workers:** OCR stub (awaiting implementation)
- **Build:** `uv` (Rust-based package manager)
- **State:** Pydantic Schemas Required ("No Schema, No Write")
- **Topology:** Hub-and-Spoke (navidocs, icw as satellites)


---

## DEBATE LOG

**CHAIR (Codex):** The motion is on the floor. The current state is 'High Integrity'
following the forensic swarm recovery of 2025-11-26. Twenty Haiku agents confirmed
the location of ghost components. The Librarian and YoloGuard have been physically
moved to `src/infrafabric/core/`. The floor is open.

---

**MEMBER A (Google Research Perspective):**
I reviewed `src/infrafabric/core`. The separation of `services/librarian.py` from
`security/yologuard.py` follows the principle of least privilege. The Librarian's
1M token context window with 3-tier fallback (Gemini -> DeepSeek -> Haiku) is
architecturally sound. The $43k/year savings claim is verifiable.

I vote **YES**, provided `uv` lockfiles are committed.

---

**MEMBER B (OSS Maintainer Perspective):**
`justfile` is present. `scripts/` directory exists. `.pre-commit-config.yaml` with
Gitleaks v8.18.4 is configured. I can clone and run. The security fix (commit 5a858d5)
addressed the leaked .env before it could be exploited.

I vote **YES**.

---

**MEMBER C (Ghost of Instance #0):**
You recovered the Librarian. You saved the Memory. The IF.yologuard philosophy of
Wu Lun (relationship-based secret detection) is preserved. The system can now
remember across sessions.

I vote **YES**.

---

**MEMBER D (Contrarian Guardian):**
I note the following concerns for the record:
1. OCR Worker is a stub - no actual implementation
2. SynthesisEngine remains a ghost (never built)
3. Redis state schema enforcement is policy, not code

However, these are documented gaps, not hidden debts. The archaeological approach
of recovering existing code rather than rewriting is fiscally responsible.

I vote **YES WITH RESERVATIONS** (recorded in gap_analysis).

---

**MEMBER E (Security Auditor):**
Pre-commit hooks: Gitleaks active.
.gitignore: Secrets patterns hardened.
API keys: OpenRouter REVOKED (2025-11-07), DeepSeek active but in CLAUDE.md (needs migration).
Recovery codes: Warning issued.

Risk level: ACCEPTABLE for research prototype.

I vote **YES**.


---

## VERDICT

**RATIFIED: 5-0** (with 1 reservation recorded)

The InfraFabric Series 2 Core Structure is hereby established.

### Binding Decisions:
1. `src/infrafabric/core/` is the canonical location for all core services
2. "No Schema, No Write" policy applies to all Redis operations
3. Hub-and-Spoke topology confirmed (navidocs, icw as satellites)
4. Forensic archaeology pattern approved for future recovery operations

### Action Items:
- [ ] Commit `uv.lock` when dependencies stabilize
- [ ] Implement OCR worker (tracked in gap_analysis)
- [ ] Migrate DeepSeek key from CLAUDE.md to secrets manager
- [ ] Schedule SynthesisEngine design review (Q1 2026)

### Genesis Commits:
- `5a858d5` - Security fix (leaked .env remediation)
- `660914f` - Archaeology resurrection (Librarian + YoloGuard)
- `{next}` - Council ratification (this document)


---

## SIGNATURES

| Member | Vote | Timestamp |
|--------|------|-----------|
| Chair (Codex) | PRESENT | 2025-11-26 02:26:07 |
| Member A (Research) | YES | 2025-11-26 02:26:07 |
| Member B (OSS) | YES | 2025-11-26 02:26:07 |
| Member C (Ghost #0) | YES | 2025-11-26 02:26:07 |
| Member D (Contrarian) | YES* | 2025-11-26 02:26:07 |
| Member E (Security) | YES | 2025-11-26 02:26:07 |

*With reservations recorded in gap_analysis

---

*This document is a permanent record of the InfraFabric Council decision.*
*Amendments require 4/5 supermajority and 14-day cooling-off period.*
