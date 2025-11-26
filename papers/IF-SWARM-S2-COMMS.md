# IF.swarm.s2 – Redis Bus Communication for Production Swarms

**Date:** 2025-11-26  
**Audience:** InfraFabric architects, reliability leads, multi-agent researchers  
**Sources:** INTRA-AGENT-COMMUNICATION-VALUE-ANALYSIS.md (2025-11-11), IF-foundations.md (IF.search 8-pass), swarm-architecture docs (Instance #8–#11), Redis remediation logs (2025-11-26)

---

## Abstract
InfraFabric’s Series 2 swarms run like a fleet of motorbikes cutting through traffic: many small, agile agents moving in parallel, instead of one luxury car stuck in congestion. The Redis Bus is the shared road. This paper describes how S2 swarms communicate, claim work, unblock peers, and escalate uncertainty, with explicit Traceable / Transparent / Trustworthy (IF.TTT) controls. It is fact-based and admits gaps: recent Redis scans still found WRONGTYPE residue and missing automation for signatures.

---

## Executive Summary
- **Problem:** Independent agents duplicate work, miss conflicts, and hide uncertainties.  
- **Pattern:** Redis Bus + Parcel envelopes + IF.search (8-pass) + SHARE/HOLD/ESCALATE.  
- **Outcome:** Intra-agent comms improved IF.TTT from 4.2 → 5.0 (v1→v3) in Epic dossier runs; conflicts surfaced and human escalation worked.  
- **Cost/Speed:** Instance #8 measured ~0.071 ms Redis latency (140× faster than JSONL dumps) enabling parallel Haiku swarms.  
- **Risk:** Hygiene debt remains (WRONGTYPE keys seen on 2025-11-26 scan); cryptographic signatures are specified but not enforced in code.  

---

## Architecture (Luxury Car vs Motorbikes)
- **Monolith / Luxury Car:** One large agent processes sequentially; stuck behind slow steps; single point of hallucination.  
- **Swarm / Motorbikes:** N Haiku agents plus a coordinator; each claims tasks opportunistically; results merged; stuck agents can hand off.  
- **Road:** Redis Bus (shared memory). Messages travel as Parcels (sealed containers with custody headers).  

---

## Communication Semantics
1) **Envelope:** Parcel (tracking_id, origin, dispatched_at, contents, chain_of_custody).  
2) **Speech Acts (FIPA-style):**  
   - `inform` (claim + confidence + citations)  
   - `request` (ask peer to verify / add source)  
   - `escalate` (critical uncertainty to human)  
   - `hold` (redundant or low-signal content)  
3) **Custody:** Ed25519 signatures specified per message; audit trail via tracking_id + citations. (Implementation gap: signatures not yet enforced in code.)  
4) **IF.TTT:**  
   - Traceable: citations and sender IDs logged.  
   - Transparent: SHARE/HOLD/ESCALATE decisions recorded.  
   - Trustworthy: multi-source rule enforced; conflicts surfaced; human loop for <0.2 confidence.  

---

## Redis Bus Keying (S2 convention)
- `task:{id}` (hash): `description`, `data`, `type`, `status`, `assignee`, `created_at`.  
- `finding:{id}` (string/hash): claim, confidence, citations, timestamp, worker_id, task_id.  
- `context:{scope}:{name}` (string/hash): shared notes, timelines, topics.  
- `session:infrafabric:{date}:{label}` (string): run summaries (e.g., protocol_scan, haiku_swarm).  
- `swarm:registry:{id}` (string): swarm roster (agents, roles, artifacts).  
- `swarm:remediation:{date}` (string): hygiene scans (keys scanned, wrongtype found, actions).  
- `bus:queue:{topic}` (list) [optional]: FIFO dispatch for workers in waiting mode.  
- **Parcel fields in values:** embed `tracking_id`, `origin`, `dispatched_at`, `chain_of_custody` in serialized JSON/msgpack.

---

## IF.search (8-Pass) Alignment
Passes (IF-foundations.md) map to bus actions:  
1. **Scan:** seed tasks to `task:*`; shallow sources.  
2. **Deepen:** `request` to specialists; push sub-tasks.  
3. **Cross-Reference:** compare `finding:*`; detect conflicts.  
4. **Skeptical Review:** adversarial agent issues `request`/`hold`.  
5. **Synthesize:** coordinator merges `finding:*` into context.  
6. **Challenge:** contrarian agent probes gaps; may `escalate`.  
7. **Integrate:** merge into report; update `context:*`.  
8. **Reflect:** meta-analysis on SHARE/HOLD/ESCALATE rates; write back lessons.  

---

## S2 Swarm Behavior (expected)
- **Task Claiming:** Workers poll `task:*` or `bus:queue:*`; set `assignee` and `status=in_progress`; release if blocked.  
- **Idle Help:** Idle agents pull oldest unassigned task or assist on a task with `status=needs_assist`.  
- **Unblocking:** Blocked agent posts `escalate` Parcel; peers or coordinator pick it up.  
- **Cross-Swarm Aid:** Registries (`swarm:registry:*`) list active swarms; helpers can read findings from another swarm if allowed.  
- **Conflict Detection:** When two findings on same topic differ > threshold, raise `escalate` + attach both citations.  
- **Hygiene:** Periodic scans (e.g., `swarm:remediation:redis_cleanup:*`) to clear WRONGTYPE/expired debris.  

---

## Observed Evidence (from logs and runs)
- **Speed:** Instance #8 Redis Bus latency ~0.071 ms; 140× faster vs JSONL dump/parse.  
- **Quality delta:** In Epic dossier runs, comms v3 lifted IF.TTT from 4.2→5.0; ESCALATE worked; conflicts surfaced (revenue variance example).  
- **Hygiene debt:** 2025-11-26 remediation log found ~100 WRONGTYPE/corrupted keys out of 720 scanned.  
- **Ops readiness:** Registries and remediation keys exist; signatures and bus schemas are not enforced programmatically.  

---

## Risks and Gaps (honest view)
- Signatures optional → spoof risk.  
- WRONGTYPE residue shows schema drift/hygiene gaps.  
- No automated TTL/archival on findings/tasks; risk of stale state.  
- No load/soak tests for high agent counts.  
- Cross-swarm reads need access control; not specified.  

---

## Recommendations (to productionize)
1. **Enforce Parcels:** wrap all bus writes in Parcel with custody headers.  
2. **Signatures:** implement Ed25519 sign/verify on every message; reject unsigned.  
3. **Schema guard:** add ruff/mypy + runtime validators for bus payloads; auto-HOLD malformed writes.  
4. **Queues + leases:** use `bus:queue:*` with leases to avoid double-claim; requeue on timeout.  
5. **Conflict hooks:** library helper to compare findings on same topic and auto-ESCALATE conflicts >20%.  
6. **Hygiene cron:** scheduled Redis scan to clear WRONGTYPE/stale; log to `swarm:remediation:*`.  
7. **Metrics:** ship Prometheus/Grafana dashboards (latency, queue depth, conflict rate, escalate rate).  
8. **Access control:** gate cross-swarm reads; add allowlist per swarm registry.  

---

## Citations
- **INTRA-AGENT-COMMUNICATION-VALUE-ANALYSIS.md** – Epic revenue conflict example; SHARE/HOLD/ESCALATE metrics v1→v3.  
- **IF-foundations.md** – IF.search 8-pass investigation methodology.  
- **swarm-architecture/INSTANCE9_GEMINI_PIVOT.md** – Redis Bus latency (0.071 ms) and 140× JSONL comparison.  
- **swarm:remediation:redis_cleanup:2025-11-26** – WRONGTYPE/corruption scan results.  
- **swarm:registry:infrafabric_2025-11-26** – Example swarm roster for Haiku multi-agent run.  

---

## Closing
S2 swarms only outperform the “luxury car” when the Redis Bus is disciplined: signed Parcels, clear key schema, hygiene, and conflict-aware workflows. The evidence shows communication quality directly lifted IF.TTT to 5.0/5 in real runs. The remaining work is engineering discipline: enforce the protocol, add guardrails, and measure it.
