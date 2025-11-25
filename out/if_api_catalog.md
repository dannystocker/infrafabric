# IF.* API Catalog

## Implemented here
- **IF.yologuard (Tech Guardian)**
  - Description: Confucian relationship-based static secret detector with entropy scoring, greedy decoding helpers, regex patterns, and a redactor class.
  - Spec sources: `papers/IF-armour.md`, `INFRAFABRIC-COMPLETE-DOSSIER-v11.md` (Sections 4–8, ANNEX N–P), `INFRAFABRIC-COMPLETE-DOSSIER-v7.01.md` (Part II, Section 2.1–2.5).
  - Implementation: `code/yologuard/src/IF.yologuard_v3.py`, `code/yologuard/versions/IF.yologuard_v3.py`, `code/yologuard/README.md`, and the Yologuard test vectors (`out/yologuard_test_vectors.md`, `out/tests_test_yologuard.py`).
  - External siblings: additional variants under `/home/setup/work/mcp-multiagent-bridge/IF.yologuard_v3.py`, `/home/setup/digital-lab.ca/infrafabric/yologuard/REPRODUCIBILITY_COMPLETE/IF.yologuard_v3.py`, and `/mnt/c/users/setup/Downloads/yologuard-codex-review/code/v3/IF.yologuard_v3.py` (see `out/yologuard_variants_comparison.md`).

## Implemented externally
- **IF.search**
  - Description: Eight-pass investigation engine that indexes guardians, telemetry, and mention graphs; described in `clean_spec.md` and the dossiers’ validation stacks.
  - Spec sources: `papers/IF-foundations.md` (search methodology sections), `INFRAFABRIC-COMPLETE-DOSSIER-v11.md` Section 7 (“Validation Stack – IF.search”), and Annex C (“IF.search Methodology”).
  - Implementation references: `work/mcp-multiagent-bridge/IF.search.py` (external repo) and `docs/evidence/infrafabric_file_inventory.csv` entries that record search runs.

## Spec-only
- **IF.guard**
  - Description: Guardian decision-making, veto/dissent, and sensitivity rules described in `clean_spec.md` and `INFRAFABRIC-COMPLETE-DOSSIER-v11.md` Sections 4–6.
  - Spec sources: `IF-armour.md`, `INFRAFABRIC-COMPLETE-DOSSIER-v7.01.md` Part I, `philosophy/IF.philosophy-*.md`.
  - Implementation status: no runnable code; future reorg should point reviewers to `papers/IF-armour` for guard rules and to `INFRAFABRIC` annexes for vote history.

- **IF.optimise**
  - Description: Token-efficient orchestration framework and economics (Section 10 of the v11 dossier, Annex N, and the eight-step Ethical Guardian heuristics in v7.01 Part III).
  - Spec sources: `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md`, `papers/IF-foundations.md`, `INFRAFABRIC-COMPLETE-DOSSIER-v11.md` Section 10.
  - Implementation status: design only; call out the lack of code in `docs/meta/IF_COMPONENT_STATUS.md`.

- **IF.witness**
  - Description: Observability/reflexion stack, test-case generation, and multi-agent witness logging (Sections 5–7 of dossier v11 and `papers/IF-witness.md`).
  - Spec sources: `papers/IF-witness.md`, `INFRAFABRIC-COMPLETE-DOSSIER-v11.md` Sections 5–7, `out/todos_priority.md` (“Veto, Dissent, Sensitivity Rules”).
  - Implementation status: no service exists in repo; only described in spec (see `IF_COMPONENT_STATUS`).

- **IF.philosophy**
  - Description: Indexed philosopher database and query prompts underpinning cycle guidance.
  - Spec sources: `philosophy/IF.philosophy-database.yaml`, `philosophy/IF.philosophy-queries.md`, `INFRAFABRIC-COMPLETE-DOSSIER-v7.01.md` Part I.
  - Implementation status: data-only; no runtime consumer yet.

## Concept-only
- **IF.router**
  - Description: Reciprocity-based router mentioned in doctrine (per `IF_COMPONENT_STATUS.md`); no spec detail beyond the note and occasional references in dossiers (e.g., v7.01 Section 3.3 “IF.router”).
  - Implementation status: concept placeholder; no code, no files.

- **IF.citate**
  - Description: Mentioned as a citation-validation guardrail in `IF_COMPONENT_STATUS.md` and `INFRAFABRIC-COMPLETE-DOSSIER-v7.01.md` (strategic report sections), but remains unnamed beyond the concept.
  - Implementation status: no implementation.
