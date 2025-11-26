# InfraFabric Debug Session Prompt (GPT-5.1 Codex CLI @ 2025-11-15T14:54:56Z)

## Component Status Overview
- **Documented only:** IF.ground, IF.search, IF.persona (see IF-foundations.md:14-1034)
- **Security concepts without code:** IF.armour, IF.yologuard (IF-armour.md:81-383; annexes/infrafabric-IF-annexes.md:2621-2650)
- **Meta-validation prose:** IF.witness, IF.forge, IF.swarm (IF-witness.md:1-1363)
- **Policy-only:** IF.optimise (annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md:1-135)
- **Unimplemented placeholders:** IF.router, IF.memory, IF.trace, IF.pulse, IF.ceo, IF.vesicle, IF.kernel (README.md:149-175)

## Foundational Gaps Inventory
1. **No committed source code for touted production systems** — `code/yologuard/` is empty; all deliverables are narrative (docs/evidence/infrafabric_metrics.json:1-10).
2. **Traceability holes** — `/papers/*.tex` cite dozens of sources without DOIs or working URLs (e.g., papers/IF-witness.tex:1285-1323).
3. **Unverifiable metrics** — README claims 6-month production validation with 96.43% recall (README.md:125-145) but no logs or data are checked in.
4. **Annex references to missing repos** — COMPLETE-SOURCE-INDEX points to `/home/setup/...` paths that are not part of this Git tree (annexes/COMPLETE-SOURCE-INDEX.md:1-76).

## Prioritized Issues
### P0 (Blockers)
- **P0-1 Missing runnable implementation** — Ship the actual IF.yologuard/IF.optimise code or reduce claims (docs/evidence/infrafabric_metrics.json:1-10).
- **P0-2 Broken citation targets** — Replace or archive dead references like https://superagi.com/swarms (papers/IF-witness.tex:1285).

### P1 (High Priority)
- **P1-1 Annotate README with current repo scope** — Clarify that this is a document bundle, not the production stack (README.md:125-185).
- **P1-2 Formalize IF.optimise scheduler spec** — Attach concrete pipelines, budgets, and token tracking tables (annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md:22-134).
- **P1-3 Provide audit logs for IF.yologuard metrics** — Attach anonymized detection runs supporting the 96.43% claim (annexes/infrafabric-IF-annexes.md:2621-2650).

### P2 (Medium Priority)
- **P2-1 Consolidate philosophical references with DOIs** — Add modern sources (<3 years) and proper citations (papers/IF-foundations.tex:2403-2531).
- **P2-2 Document dependency footprint** — List Anthropic/OpenAI/Gemini requirements and billing implications (README.md:125-159).
- **P2-3 Publish guardian council mechanics** — Provide weights/config schemas instead of prose (README.md:129-176).

## Step-by-Step Debug Workflow
1. **Inventory reality** — Run `git ls-files` and `docs/evidence/infrafabric_metrics.json` to confirm that no executable subsystems exist; scope work to documentation fixes or ingest external code.
2. **Citations triage** — Extract all `http` references from `papers/*.tex`, test them with `curl --head`, and either update, archive, or annotate unreachable URLs.
3. **README alignment** — Update `README.md` to clearly state repo contents, remove or qualify production-proof claims, and link to missing repos if they exist.
4. **Attach evidence** — Collect IF.yologuard benchmark outputs (tables, logs, confusion matrices) and commit sanitized artifacts inside `code/yologuard/`.
5. **Spec to code translation** — For IF.optimise and IF.guard council weights, derive minimum viable schema/configuration files and commit them with placeholder implementations to unblock future engineering work.
6. **Regression checklist** — Add automated validation (YAML schema checks, citation lints) so future documentation edits don't silently degrade the traceability guarantees relied on throughout the papers.
