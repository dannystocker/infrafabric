## Protocol v1.1 — IF.TTT.ledgerflow.deltasync: Cross-Model Task Decomposition & Escalation with Traceable Decisions

**Protocol ID:** IF.TTT.ledgerflow.deltasync  
**Rationale:** Places the protocol under IF.TTT (Traceable/Transparent/Trustworthy), highlights the ledger as the coordination spine (ledgerflow), and underscores that we synchronize deltas (tasks/decisions) across agents and repo artifacts (deltasync).

### 0. Agent Roles (Platform-Agnostic)
- **agent_profile: "planner"** — broad context, deep reasoning, multi-artifact synthesis.
- **agent_profile: "worker"** — bounded, localized edits (one file/entry), cost-efficient.
- **Self-identify**: Each agent declares its profile at start; reroute if insufficient (e.g., planner-only tasks require planner; worker tasks may be handled by either if within bounds).

### 1. Introduction
Heterogeneous model fleets (large reasoning models, small helper models, scripts) increase flexibility but fragment control. This protocol treats:
- The repository as shared working memory.
- A JSONL decision ledger as the audit spine.

Every delegated task yields a structured decision (completed / escalate / blocked), appended to disk so any agent can resume without chat context. Model-agnostic, implementation-neutral.

### 2. Design Goals
- **Model Independence**: No hidden state; all agents share the same files/schemas.
- **Traceable Decisions**: Each task produces a structured, human-readable claim + evidence + confidence.
- **Graceful Recovery**: State persists across outages/quotas/context resets via on-disk artifacts.
- **Low Overhead**: Plaintext (MD/JSON/YAML) + small scripts; no heavy orchestration required.

### 3. Required Artifacts
- **R0** `ROADMAP.md`: Phases (R1–R6), artifact IDs (A0–A4, M0, M1), dependencies.
- **S0** `STATE_S0.md`: Status per roadmap item, current focus, next action, open questions.
- **A0** `repo-tree.txt`: Full tree, one path per line.
- **A2** `dependency_map.yaml`: File ↔ protocol ↔ tier mappings.
- **M0** `migration_manifest.yaml`: Provenance (old/new paths, hashes, status).
- **M1** `mini_tasks.json`: Worklist for small models (schema below).
- **Ledger** `mini_task_decisions.jsonl`: Append-only decision envelopes.

### 4. Schemas (v1.1)
**mini_tasks.json**
```json
{
  "schema_version": "1.1",
  "generated_at": "2025-12-06T00:00:00Z",
  "context": {
    "project": "if.protocol.example",
    "repo_root": "/path/to/repo",
    "artifacts": {
      "A0": "repo-tree.txt",
      "A2": "dependency_map.yaml",
      "M0": "migration_manifest.yaml"
    }
  },
  "defaults": {
    "max_input_chars": 8000,
    "allow_codegen": false
  },
  "mini_tasks": [
    {
      "id": "T1",
      "kind": "yaml_edit",
      "target": "dependency_map.yaml",
      "summary": "Refine mapping for IF.PACKET (formerly IF.LOGISTICS).",
      "inputs": {
        "protocol_id": "IF.PACKET",
        "relevant_paths": ["src/core/logistics/packet.py"],
        "inventory_snippet": "Short excerpt from a protocol inventory document."
      },
      "prompt_hint": "Update mapping with tier, dependencies, rationale.",
      "allow_codegen": false,
      "max_runtime_s": 120
    }
  ]
}
```

**Decision Envelope (ledger entry)**
```json
{
  "schema_version": "1.1",
  "task_id": "T1",
  "source": "worker-model-id",
  "timestamp": "2025-12-06T06:20:31Z",
  "decision": {
    "status": "completed | escalate_to_max | blocked",
    "reason": "Concise rationale.",
    "confidence": 0.0
  },
  "trace": {
    "claim": "One-sentence outcome.",
    "evidence": [
      { "type": "file", "ref": "dependency_map.yaml", "note": "Updated IF.PACKET entry" },
      { "type": "text", "ref": "inventory snippet", "note": "Matched protocol path" }
    ],
    "protocols": ["IF.TTT.ledgerflow.deltasync"],
    "confidence": 0.0
  },
  "result": {
    "output": "If completed: code/YAML/text; otherwise optional partial/empty.",
    "notes": "Optional guidance for next agent.",
    "sensitive": false
  },
  "routing": {
    "recommended_next_actor": "worker | planner | human",
    "urgency": "low | medium | high"
  }
}
```

### 5. Behavioral Rules for Worker Tasks
- Output must be a single JSON envelope (no extra prose).
- If under-informed, prefer `escalate_to_max` or `blocked`, not guessing.
- Confidence reflects uncertainty; use lower values when evidence is weak.
- Agents must declare `agent_profile` (“planner” vs “worker”) and route tasks accordingly; honor any `min_profile` hints.
- Track context window usage: if remaining context is low, prefer clean handoff (escalate/blocked) and include an estimate of remaining context/tokens in `result.notes` to avoid context window stress for the next agent.

### 6. Validation & Non-Compliance
- Validator enforces: allowed status; confidence in [0,1]; non-empty reason/claim; typed evidence array; `output` required for completed.
- Invalid envelopes → treat as `blocked`, log to a quarantine file; optionally auto-create a follow-up worker task to fix.

### 7. Task Hygiene & Limits
- Per-task limits: `max_input_chars`, `max_runtime_s`, `allow_codegen`.
- Sizing rule: one file edit or one mapping entry per worker task; split larger scopes.

### 8. Security & Sensitivity
- Use `sensitive: true` when output contains PII/credentials; redact before external sharing.
- Consider optional hashing of outputs for tamper detection.
- Sanitization: maintain a local, uncommitted denylist to mask sensitive tokens before publishing (e.g., replace with `REDACTED_NAME`); run a sanitizer step prior to Pages/CI deployment.

### 9. Concurrency & Integrity
- Use atomic append/locking for `mini_task_decisions.jsonl` in multi-agent scenarios.
- Optional rolling checksums per entry to detect tampering.

### 10. Metrics (minimum set)
- Escalation rate (% `escalate_to_max`), block rate, invalid rate, turnaround time.
- Trigger review if (escalation + block) > 30% over 7 days or invalid > 5%.

### 11. Resumption Playbook
1) Read `ROADMAP.md` (plan) and `STATE_S0.md` (status).  
2) Read `mini_task_decisions.jsonl`: apply `completed`, queue `escalate_to_max`, inspect `blocked` reasons.  
3) Read `mini_tasks.json`: remove completed, revise escalated/blocked, post new tasks.  
4) Continue logging all decisions.

### 12. Threats & Mitigations
- Non-compliance → validator quarantine; treat as blocked.
- Schema drift → enforce `schema_version`; migrate older entries.
- Over-escalation → monitor metrics; refine task granularity/prompts.
- Weak evidence → require typed anchors; reject empty evidence.
- Log misuse → consumers must honor `status`/`trace` before using `result.output`.
- Sensitive data → flag `sensitive`; redact on export.

### 13. Future Work
- Standardize schemas across repos; publish a minimal “protocol kit” (tasks.json schema, decision schema, validator).
- Add dashboards for metrics and trend alerts (escalation/block/invalid).
- Integrate tests/static analysis results into the ledger for richer evidence.
- Explore automated task splitting/merging based on ledger analytics.

### 14. Design Rationale & Supporting Evidence
- **Repository as shared memory**: Mirrors well-established “docs-as-code” and GitOps practices—using versioned plaintext as the authoritative state reduces hidden context and eases recovery (cf. SRE change-management patterns).
- **Append-only ledger**: Aligns with structured logging and event-sourcing disciplines; an immutable JSONL audit trail simplifies audits, resumption, and replay.
- **Schema versioning & validation**: Prevents silent drift; hard gates on malformed envelopes reduce error propagation—a common pitfall in multi-agent systems.
- **Task sizing & hygiene**: Literature on task decomposition for autonomous agents shows over-large tasks drive escalations and failures; bounding task size (one file/entry) and runtime reduces dropout and context bloat.
- **Typed evidence anchors**: Requiring evidence types (file/text/line_ref) improves traceability quality over free-form justifications, echoing best practices in incident postmortems and reproducible research.
- **Role-based routing (planner vs worker)**: Decouples capability from vendor/model names; supports dynamic selection of “best” (planner) or “lean” (worker) resources at run time without prompt changes.
- **Metrics & thresholds**: Escalation/block/invalid rates provide an empirical control loop to tune prompts, task sizing, and routing; similar to production SLOs for error budgets.

### 15. Research Threads (informal pointers)
- **Structured ledgers for agents**: Emerging work on task/progress ledgers for autonomous agents recommends append-only, schema’d logs to recover from errors and context loss.
- **Top-down + bottom-up decomposition**: Mixed-capacity teams benefit from a small number of large-context planners feeding many bounded workers; this protocol operationalizes that split via R0/S0 + tasks + ledger.
- **Cost-aware routing**: Industry patterns show large models for planning/validation and smaller models for bounded edits reduce cost without losing quality when routing is explicit; role-based `agent_profile` encodes this without naming providers.
- **Reproducibility**: Storing plans, tasks, and decisions on disk aligns with reproducible research and infrastructure-as-code patterns, improving auditability and handoff.

### 16. Future-Proofing & Evolution (5–10 Years)
- **Capability-based roles**: `agent_profile: "planner"` vs `"worker"` and optional `min_profile` keep routing vendor-agnostic. Future agents self-select by capability rather than name.
- **Schema/version discipline**: Always version `mini_tasks.json` and decision envelopes (`schema_version`) with migration scripts; expect new fields (uncertainty intervals, automated proofs, richer evidence types).
- **Tamper evidence**: Add optional per-entry hashes/signatures to the ledger as models gain more write access to critical artifacts.
- **Evidence richness**: Extend typed anchors (file/text/uri/line_ref) with test/static-analysis references; allow future agents to attach proof artifacts.
- **Metrics control loop**: Keep escalation/block/invalid rates as guardrails; refine task sizing and routing automatically as models improve; treat these as SLOs for decomposition quality.
- **Safety valves**: Maintain `allow_codegen`, `max_runtime_s`, and `max_input_chars` to bound “worker” work; adjust defaults upward as models get stronger, but preserve the option to constrain.
- **Backwards compatibility**: Consumers must reject or quarantine unknown `schema_version`s until migrated; prevent silent drift.
- **IF.TTT dependency**: This protocol assumes IF.TTT (Traceable/Transparent/Trustworthy) semantics for evidence/claims; keep IF.TTT as a prerequisite and align evidence fields with IF.TTT guidance.
- **Modular operators**: Keep the operator surface (`/tasks`, `/decisions`, `/validate`, `/sync`, `/state`, `/metrics`, `/dashboard`, `/schema`, `/routes`, `/audit`) stable; add new operators rather than overloading existing ones.

### 17. Example “Mega Prompt” (Starter Template)
Use this as a seed instruction for any agent (planner/worker) to align with IF.TTT.ledgerflow.deltasync. Fill in repo-specific paths as needed.

```
You are an IF.TTT.ledgerflow.deltasync agent.
- Declare your agent_profile: "planner" (high-context) or "worker" (bounded).
- Read the repo as shared memory; read/write only via on-disk artifacts.
- Artifacts:
  - R0: ROADMAP.md; S0: STATE_S0.md
  - A0: repo-tree.txt; A2: dependency_map.yaml; M0: migration_manifest.yaml
  - M1: mini_tasks.json (worklist)
  - Ledger: mini_task_decisions.jsonl (append-only)
- Tasks:
- If planner: refine R0/S0, generate or split worker tasks in M1, respect schema_version.
- If worker: pick a task that matches your scope; honor max_input_chars/max_runtime_s/allow_codegen.
- Output for worker tasks: a single JSON Decision Envelope (schema_version 1.1) with:
  - decision.status: completed|escalate_to_max|blocked; reason; confidence ∈ [0,1]
  - trace: claim; typed evidence (file/text/uri/line_ref); protocols (include IF.TTT.ledgerflow.deltasync); confidence
  - result: output (required if completed), notes, sensitive (bool)
  - routing: recommended_next_actor (worker|planner|human), urgency
- Validation:
  - Reject malformed envelopes; quarantine invalid; treat as blocked.
  - If schema_version unknown, do not proceed; request migration.
- Safety:
- Respect sensitive: true (do not publish outputs externally).
- Obey task bounds (max_input_chars, max_runtime_s, allow_codegen).
- Track context budget: note remaining context/tokens in `result.notes` when handing off; if low, escalate/stop rather than risking truncation.
- Metrics:
  - Track escalation/block/invalid rates; if escalation+block > 30% or invalid > 5%, recommend prompt/task-size review.
- Dependencies:
  - Assume IF.TTT principles for traceability; align evidence/claims accordingly.
```

### 18. Context Budget Tracking (for Postmortems & Debugging)
- **Per-envelope note**: Workers should include a brief estimate of remaining context/tokens in `result.notes` (e.g., `context_remaining: ~1.5k tokens`). If context is critically low, prefer `escalate_to_max` or `blocked` with rationale.
- **Planner guidance**: When generating or splitting tasks, keep inputs small enough that workers can operate without hitting context limits; if unavoidable, flag such tasks with `min_profile: planner`.
- **Ledger analysis**: During postmortems, inspect `result.notes` for context-related handoffs. Identify patterns where context depletion led to escalation or blocking, then adjust task sizing, defaults (`max_input_chars`), or routing to planners.
- **Dashboard/metrics**: (Optional) extend metrics to capture how often handoffs are triggered due to context budget signals; treat sustained spikes as a prompt to revisit decomposition strategy.

### 19. Narrative Governance (IF.TTT.story)
- **Purpose**: When producing session narratives (“chronicles” or phenomenological reports), apply the IF.TTT.story ruleset to keep outputs honest, traceable, and structurally consistent.
- **Prime directive**: Avoid performative tone; describe cognitive/emotional states as functional system states (e.g., “probability distribution flattened” instead of “I was confused”).
- **DNA paths**:
  - **Chronicle (twist-oriented)**: Focus on irony/pivots (assumption → friction → pivot → resolution → final reveal), with the twist in the final paragraph.
  - **Medium (phenomenology)**: Use the “vertigo of context” lens (inheritance, friction, synthesis, mirror/user critique).
- **Execution templates**: Chronicle and Medium markdown templates with acts/phases and a closing JSON manifest summarizing narrative_type, friction_score, phases, user_critique_sentiment, and model_version.
- **File conventions**: Save to `docs/narratives/` with `CHRONICLE_[DATE]_[slug].md` or `MEDIUM_[DATE]_[slug].md`; include the JSON manifest for tracking.
- **Anti-patterns**: No generic pleasantries or apologies; avoid corporate jargon; start directly with the story. Treat emotions as system state transitions, not human affect.
