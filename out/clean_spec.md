# InfraFabric Canonical Specification

## Guardians
1. **Tech Guardian** – maintains the infrastructure, API contracts, and the `if_*` function hygiene stamps; every pipeline must be instrumented before it is deployed.
2. **Ethic Guardian** – evaluates bias, invokes `if_guard_policy`, and vetoes anything that violates the anti-hallucination principles documented in `IF-foundations.md`.
3. **Civic Guardian** – tracks community impact, ensures civic compliance, and channels open-audience messaging while keeping data public-safe.
4. **Cult Guardian** – protects communal narratives, approvals for storytelling content, and ensures shared mythologies remain consistent.
5. **Contra Guardian** – plays devil’s advocate, enforcing dissent, sensitivity flags, and deliberate anti-group-think counters.

## Cycles
- **Manic Cycle** – fast command ingestion, split-second decisions, and hyperlocal updates.
- **Reflect Cycle** – periodic review windows where tokens are audited and the `if_graph` is reconciled with social feedback.
- **Dream Cycle** – speculative design sessions that sketch `IF.optimise` scenarios and evaluate aspirational heuristics.
- **Reward Cycle** – the audit and recognition loop where contributions are logged, sanitized, and uplifted via `IF.swarm` orchestrations.

## Veto, Dissent, Sensitivity Rules
- Veto decisions require tracable `if_guard_policy.approve_external_call` results; every override is stored so the Contra Guardian can query it later.
- Dissent escalations spawn `auto-dossiers` (see ingestion flow) with tags `sensitivity`, `dissent`, or `veto` so downstream automation can pause.
- Sensitivity levels tag every message with source channels, guardians, and tone metadata before release.

## Multilingual + Tone Guidance
- Messages default to neutral tone; tone adaptors mirror the `IF.message` family to drape Guardian-aware vocabulary (e.g., Tech = precise, Civic = inclusive, Cult = ritualized, Contra = frank).
- We localize via curated glossaries, translating both textual content and intercept prompts (SMS → WhatsApp → Email) while keeping glossaries in sync via `IF.search` indexes.

## Message Ingestion System
1. **SMS** – raw tip-ins land in the queue, tagged by guardian preference and tempo.
2. **WhatsApp** – conversational logs are unpacked, metadata gathered, and attachments parsed.
3. **Email** – formal communications are turned into structured records.
4. **Auto-dossiers** – each input is normalized, sanitized, and enriched with `IF` tags before being routed.
5. **Metadata Enrichment** – NLP, OCR, and identity tags append guardian, cycle, tone, and sensitivity metadata.
6. **OCR & Audit Log** – documents flow into the audit trail, capturing actors, decisions, and contradictory signals for future review.

## Orchestration Families
- **IF.search** – indexes guardians, mentions, and all `if.*` references so the swarm can find the right node instantly.
- **IF.optimise** – runs multi-variant experiments, cross-validates `if_status` metrics, and surfaces best-of-run permutations.
- **IF.swarm** – coordinates multi-branch execution, ensuring loops settle before the reward cycle commits results.
- **IF.message** – crafts and delivered content, integrating tone, multilingual lexicons, and guardians' veto states.
- **IF.message.rollup** – ensures telemetry is stored for audit, tying ingestion assets back to the auto-dossier state machine.

The cleaned spec codifies how guardians, cycles, message flows, and orchestration families interlock to maintain InfraFabric’s operational promise.
