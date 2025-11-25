# Proposed Tree Reorganization

The next InfraFabric layout collapses scattered manifestos, evidentiary notes, and automation helpers into a guardrail-focused hierarchy:

- `infra/guardians/` holds the ritualistic playbooks (`IF-armour.md`, `IF-foundations.md`) and becomes home for future guardian-specific manifests.
- `infra/cycles/` captures the temporal vision layers (`IF-vision.md`) so cycles and dreams stay together.
- `infra/ingestion/evaluations/` centralizes audit/evaluation assets from `docs/evidence/`, giving the ingestion stream a predictable namespace for OCR, metadata, and audit logs.
- `infra/orchestrations/` collects witness intelligence and search/optimise notes that orchestrate the swarm.
- `docs/` retains the annexes/evidence subfolders, while `tools/automation/` documents the scripts that keep the saga intact.

The YAML tree (`proposed_tree.yaml`) mirrors this plan so the reorganization is both descriptive and prescriptive.
