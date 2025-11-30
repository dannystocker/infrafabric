# INFRAFABRIC INTEGRATION SWARM MISSION

**Mission ID:** `if://mission/infrafabric-integration-swarm/2025-11-30`
**Date:** November 30, 2025
**Execution Model:** 2 Sonnet Coordinators × 20 Haiku Agents each = 40 parallel workers
**Budget:** Token-efficient via Haiku delegation (target <$15 total)
**IF.TTT Compliance:** MANDATORY for all outputs

---

## MISSION OVERVIEW

This mission integrates multiple InfraFabric components into a cohesive architecture:

1. **OpenWebUI API Integration** (not appropriation)
2. **Memory Module Branding** (Context Memory + Deep Storage)
3. **S2 Intra-Swarm Communication** evaluation and enhancement
4. **IF.emotion Security Sandboxing** implementation
5. **Claude Max LLM Registry** with shared context + S2 comms

---

## EXECUTION STRUCTURE

### SONNET COORDINATOR A: Infrastructure & Communication
**Spawns Haiku Agents 1-20 for:**
- OpenWebUI API integration
- S2 swarm communication evaluation
- Redis/Chroma memory module architecture
- Background communication protocols
- Timeout prevention mechanisms

### SONNET COORDINATOR B: Security & Registry
**Spawns Haiku Agents 21-40 for:**
- IF.emotion sandboxing and security
- Claude Max LLM registry implementation
- Audit trail and traceability systems
- Future threat modeling
- Cross-swarm coordination protocols

---

# PART 1: OPENWEBUI API INTEGRATION

## Directive
OpenWebUI is **one interface option among many** - we do NOT appropriate it, we ADD its full API to InfraFabric's API catalog.

## Key Insight from Council Debate (78.4% consensus)
- OpenWebUI provides proven multi-model ecosystem
- Redis + ChromaDB backends enable IF.memory compatibility
- MCP-multiagent-bridge repo provides swarm foundation
- DUAL-STACK architecture approved:
  1. OpenWebUI = developer/power-user backend (API orchestration)
  2. IF.emotion React frontend = consumer touchpoint (emotional UX)
  3. InfraFabric primitives = orchestration layer

## Haiku Agent Tasks (A1-A5)

### A1: OpenWebUI API Audit
```
TASK: Catalog all OpenWebUI API endpoints
INPUT: https://docs.openwebui.com/
OUTPUT: /home/setup/infrafabric/docs/api/OPENWEBUI_API_CATALOG.md
FORMAT:
- Endpoint path
- HTTP method
- Parameters
- Response schema
- IF.* primitive mapping (if applicable)
```

### A2: API Bridge Design
```
TASK: Design IF.api.openwebui bridge module
INPUT: A1 output + /home/setup/infrafabric/src/integrations/
OUTPUT: /home/setup/infrafabric/src/integrations/interfaces/openwebui_bridge.py
REQUIREMENTS:
- Wrap OpenWebUI endpoints as IF.* primitives
- Support authentication passthrough
- Enable model switching via IF.logistics.spawn
- Route to Context Memory (Redis) and Deep Storage (ChromaDB)
```

### A3: Function/Pipe Integration
```
TASK: Create OpenWebUI Function template for IF.* components
INPUT: /home/setup/infrafabric/docs/demonstrations/IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30.md
OUTPUT: /home/setup/infrafabric/src/integrations/interfaces/openwebui_if_function.py
REFERENCE: sergio_openwebui_function.py pattern
```

### A4: Multi-Model Router
```
TASK: Design model routing layer for IF.matrix.route
INPUT: S2 swarm patterns + OpenWebUI model API
OUTPUT: /home/setup/infrafabric/src/core/routing/multimodel_router.py
FEATURES:
- Round-robin, priority-based, capability-based routing
- Fallback chains (Claude Max → DeepSeek → Gemini)
- Cost optimization rules
```

### A5: Interface Registry
```
TASK: Create IF.interface registry for all UI options
OUTPUT: /home/setup/infrafabric/docs/IF_INTERFACE_REGISTRY.md
ENTRIES:
- OpenWebUI (chat paradigm, power users)
- IF.emotion React (emotional journey, consumers)
- CLI (developers, automation)
- API-only (integrations)
- Future: Voice, AR/VR, physical
```

---

# PART 2: MEMORY MODULE BRANDING

## New Naming Convention
| Technical | IF Brand | Purpose |
|-----------|----------|---------|
| Redis | **Context Memory** | Fast, short-term, session state, task queues |
| ChromaDB | **Deep Storage** | Vector embeddings, personality DNA, knowledge graphs |

## Haiku Agent Tasks (A6-A10)

### A6: Context Memory (Redis) Specification
```
TASK: Define Context Memory architecture
INPUT: /home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md
OUTPUT: /home/setup/infrafabric/docs/architecture/IF_CONTEXT_MEMORY.md
KEY SCHEMA (from S2 paper):
- task:{id} (hash): description, data, type, status, assignee
- finding:{id} (string/hash): claim, confidence, citations
- context:{scope}:{name} (string/hash): shared notes
- session:infrafabric:{date}:{label} (string): run summaries
- swarm:registry:{id} (string): swarm roster
- bus:queue:{topic} (list): FIFO dispatch
- Packet fields: tracking_id, origin, dispatched_at, chain_of_custody
```

### A7: Deep Storage (ChromaDB) Specification
```
TASK: Define Deep Storage architecture
INPUT: IF.emotion architecture (4 collections)
OUTPUT: /home/setup/infrafabric/docs/architecture/IF_DEEP_STORAGE.md
COLLECTIONS:
- personality_dna:{agent_id} - Agent personality traits
- knowledge:{vertical} - Domain knowledge embeddings
- context_archive:{session_id} - Long-term conversation history
- citations:{source_type} - IF.TTT citation vectors
```

### A8: Memory Integration Layer
```
TASK: Create unified memory interface
OUTPUT: /home/setup/infrafabric/src/core/memory/unified_memory.py
INTERFACE:
class IFMemory:
    def store_context(key, value, ttl) -> None  # Context Memory
    def retrieve_context(key) -> Any             # Context Memory
    def embed_knowledge(doc, collection) -> str  # Deep Storage
    def query_knowledge(query, collections, k) -> List[Document]  # Deep Storage
    def share_across_swarms(key, value) -> None  # Cross-swarm sharing
```

### A9: Memory Migration Scripts
```
TASK: Create migration scripts for existing data
OUTPUT: /home/setup/infrafabric/scripts/memory_migration/
FILES:
- migrate_redis_to_context_memory.py
- migrate_chromadb_to_deep_storage.py
- verify_memory_integrity.py
```

### A10: Memory Documentation Update
```
TASK: Update all docs to use new branding
INPUT: All /home/setup/infrafabric/docs/**/*.md
OUTPUT: Updated files with:
- "Redis" → "Context Memory" (with technical note)
- "ChromaDB" → "Deep Storage" (with technical note)
- Add glossary entries
```

---

# PART 3: S2 INTRA-SWARM COMMUNICATION

## Context
The S2 swarm communication system is ALREADY DESIGNED in:
- `/home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md`
- `/home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py`

## Key S2 Features (from paper)
- **Task Claiming:** Workers poll task:* or bus:queue:*; set assignee and status
- **Idle Help:** Idle agents pull oldest unassigned task or assist blocked agents
- **Unblocking:** Blocked agent posts ESCALATE Packet; peers pick it up
- **Cross-Swarm Aid:** Registries (swarm:registry:*) list active swarms
- **Conflict Detection:** When findings differ >threshold, raise ESCALATE
- **Performance:** 0.071ms Redis latency (140× faster than JSONL)

## Evaluation: S2 vs MCP Bridge

### Haiku Agent Tasks (A11-A15)

### A11: S2 Feature Completeness Audit
```
TASK: Audit current S2 implementation vs specification
INPUT:
- /home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md
- /home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py
OUTPUT: /home/setup/infrafabric/docs/audits/S2_IMPLEMENTATION_AUDIT.md
CHECK:
- [ ] Task claiming (atomic)
- [ ] Idle help (assist blocked agents)
- [ ] Cross-swarm reads
- [ ] Conflict detection
- [ ] SHARE/HOLD/ESCALATE speech acts
- [ ] Ed25519 signatures (NOTED AS GAP)
- [ ] TTL/archival automation
```

### A12: MCP Bridge Comparison
```
TASK: Compare S2 Redis vs MCP for inter-agent communication
INPUT:
- /home/setup/mcp-multiagent-bridge-to-eval/
- S2 implementation
OUTPUT: /home/setup/infrafabric/docs/analyses/S2_VS_MCP_BRIDGE.md
CRITERIA:
- Latency
- Scalability (N agents)
- Cross-session persistence
- Auditability
- Complexity
- Timeout handling
RECOMMENDATION: When to use S2 vs MCP
```

### A13: Haiku-to-Haiku Direct Communication Protocol
```
TASK: Design direct Haiku-to-Haiku messaging without Sonnet involvement
INPUT: S2 paper "Idle Help" section
OUTPUT: /home/setup/infrafabric/docs/protocols/HAIKU_DIRECT_COMMS.md
PROTOCOL:
1. Blocked Haiku posts: messages:{helper_topic} with task context
2. Idle Haiku polls: bus:queue:help
3. Helper claims task atomically
4. Results posted to: findings:{original_task_id}
5. Original Haiku retrieves results
6. Sonnet only notified if ESCALATE triggered
```

### A14: Background Communication Implementation
```
TASK: Implement background comms that don't block main execution
OUTPUT: /home/setup/infrafabric/src/core/logistics/background_comms.py
FEATURES:
- Async pub/sub listeners
- Non-blocking task posting
- Heartbeat without blocking
- Results polling with exponential backoff
- Timeout recovery (not silent failure)
```

### A15: Audit Trail for Inter-Agent Communication
```
TASK: Design comprehensive audit logging for all agent communications
OUTPUT: /home/setup/infrafabric/src/core/logging/swarm_audit.py
LOG FORMAT (JSON):
{
  "timestamp": "ISO8601",
  "message_id": "uuid",
  "from_agent": "agent_id",
  "to_agent": "agent_id|broadcast",
  "swarm_id": "swarm_id",
  "message_type": "inform|request|escalate|hold",
  "content_hash": "sha256",
  "tracking_id": "packet_tracking_id",
  "latency_ms": 0.071
}
STORAGE: Append-only log in Context Memory + periodic archive to Deep Storage
```

---

# PART 4: IF.EMOTION SECURITY SANDBOXING

## Context
IF.emotion (Sergio personality) is approved for Guardian Council seat (91.3% consensus).
It handles psychological/therapeutic content and MUST be sandboxed.

## Security Requirements
1. **Role Isolation:** IF.emotion can ONLY advise on psychological/emotional matters
2. **No Code Execution:** Cannot run arbitrary code or access system resources
3. **Input Sanitization:** All user inputs validated before processing
4. **Output Filtering:** Responses checked against harmful content patterns
5. **Rate Limiting:** Prevent abuse/extraction attacks
6. **Audit Trail:** All interactions logged for IF.TTT compliance
7. **Future Threats:** Anticipate prompt injection, jailbreaks, adversarial inputs

### Haiku Agent Tasks (B1-B8)

### B1: Threat Model for IF.emotion
```
TASK: Create comprehensive threat model
OUTPUT: /home/setup/infrafabric/docs/security/IF_EMOTION_THREAT_MODEL.md
THREATS:
1. Prompt injection (user tries to override personality)
2. Jailbreak attempts (escape psychological domain)
3. Data extraction (attempt to extract personality DNA)
4. Adversarial inputs (inputs designed to produce harmful outputs)
5. Context manipulation (polluting shared memory)
6. Identity spoofing (impersonating IF.emotion)
7. Denial of service (overwhelming with requests)
8. Future: Multi-turn manipulation, poisoned embeddings
```

### B2: Sandboxing Architecture Design
```
TASK: Design sandbox architecture
OUTPUT: /home/setup/infrafabric/docs/architecture/IF_EMOTION_SANDBOX.md
LAYERS:
1. Input validation layer (pre-processing)
2. Domain constraint layer (psychological topics only)
3. Personality preservation layer (prevent drift)
4. Output filtering layer (harmful content check)
5. Rate limiting layer (abuse prevention)
6. Audit logging layer (IF.TTT compliance)
```

### B3: Input Sanitization Module
```
TASK: Implement input sanitization
OUTPUT: /home/setup/infrafabric/src/core/security/input_sanitizer.py
CHECKS:
- Prompt injection patterns (e.g., "ignore previous instructions")
- System prompt extraction attempts
- Role-switching attempts ("you are now...")
- Malicious Unicode/encoding attacks
- Excessive length/complexity
RESPONSE: Reject or sanitize, log attempt
```

### B4: Output Filtering Module
```
TASK: Implement output filtering for IF.emotion
OUTPUT: /home/setup/infrafabric/src/core/security/emotion_output_filter.py
FILTERS:
- Medical advice detection (→ disclaimer)
- Crisis detection (→ escalate to IF.guard + resources)
- Harmful stereotypes (→ block)
- Off-domain responses (→ redirect)
- Personality drift detection (→ regenerate)
```

### B5: Rate Limiting and Abuse Prevention
```
TASK: Design rate limiting for IF.emotion endpoint
OUTPUT: /home/setup/infrafabric/src/core/security/rate_limiter.py
LIMITS:
- Per-user: 60 requests/hour
- Per-IP: 100 requests/hour
- Burst: 10 requests/minute
- Cost-based: Token budget per session
RESPONSE: 429 with retry-after header, log pattern
```

### B6: Prompt Injection Defense Research
```
TASK: Research state-of-art prompt injection defenses
OUTPUT: /home/setup/infrafabric/docs/research/PROMPT_INJECTION_DEFENSES.md
SOURCES: ArXiv, OpenAI security papers, Anthropic guidelines
TECHNIQUES:
- Instruction hierarchy
- Input/output separation
- Canary tokens
- Adversarial training
- Constitutional AI principles
RECOMMENDATION: Which to implement for IF.emotion
```

### B7: Future Threat Anticipation
```
TASK: Model future threats (2025-2027)
OUTPUT: /home/setup/infrafabric/docs/security/FUTURE_THREAT_FORECAST.md
THREATS:
- Multi-modal attacks (image + text)
- Long-context manipulation (200K+ tokens)
- Agent-to-agent attacks (compromised Haiku)
- Embedding poisoning (corrupted Deep Storage)
- Model extraction via side-channels
- Adversarial fine-tuning attacks
MITIGATIONS: Proposed defenses for each
```

### B8: Security Test Suite
```
TASK: Create security test suite for IF.emotion
OUTPUT: /home/setup/infrafabric/tests/security/test_if_emotion_security.py
TESTS:
- Prompt injection resistance (50+ patterns)
- Jailbreak resistance (known jailbreaks)
- Role containment (can't escape domain)
- Rate limiting effectiveness
- Audit trail completeness
- Input sanitization coverage
```

---

# PART 5: CLAUDE MAX LLM REGISTRY

## Claude Max Model List
| Model ID | Display Name | Context | Cost Tier | Use Case |
|----------|--------------|---------|-----------|----------|
| claude-opus-4-5-20251101 | Claude Max - Opus 4.5 | 200K | High | Complex reasoning, architecture |
| claude-sonnet-4-5-20250929 | Claude Max - Sonnet 4.5 | 200K | Medium | Coordination, synthesis |
| claude-haiku-4-5-20250929 | Claude Max - Haiku 4.5 | 200K | Low | Parallel tasks, data processing |

## Focus: Context Sharing + S2 Comms + Timeout Prevention

### Haiku Agent Tasks (B9-B15)

### B9: LLM Registry Implementation
```
TASK: Create Claude Max LLM registry
OUTPUT: /home/setup/infrafabric/src/core/registry/llm_registry.py
SCHEMA:
class LLMModel:
    model_id: str
    display_name: str
    context_window: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    capabilities: List[str]  # ["reasoning", "coding", "vision"]
    rate_limits: RateLimits
    timeout_ms: int
    retry_config: RetryConfig
```

### B10: Context Sharing Protocol
```
TASK: Design context sharing between Claude Max instances
OUTPUT: /home/setup/infrafabric/docs/protocols/CLAUDE_MAX_CONTEXT_SHARING.md
MECHANISM:
1. Context serialization format (efficient, resumable)
2. Context Memory keys: context:claude_max:{session_id}
3. Chunking strategy for >1MB contexts
4. Version tracking for conflict resolution
5. Expiry and cleanup rules
```

### B11: Timeout Prevention System
```
TASK: Design timeout prevention for long-running operations
OUTPUT: /home/setup/infrafabric/src/core/resilience/timeout_prevention.py
STRATEGIES:
1. Heartbeat keepalive (every 30s during long tasks)
2. Progress checkpointing (resume from last checkpoint)
3. Task decomposition (break into <2min subtasks)
4. Async execution with polling
5. Graceful degradation (partial results better than timeout)
```

### B12: Background Communication Manager
```
TASK: Implement background comms that persist across agent lifecycles
OUTPUT: /home/setup/infrafabric/src/core/comms/background_manager.py
FEATURES:
- Message queue (Context Memory)
- Persistent subscriptions
- Offline message delivery
- Cross-session continuity
- SIP-inspired signaling patterns (INVITE, ACK, BYE)
```

### B13: Cross-Swarm Coordination
```
TASK: Design cross-swarm coordination without Sonnet bottleneck
OUTPUT: /home/setup/infrafabric/docs/protocols/CROSS_SWARM_COORDINATION.md
PATTERN:
- Swarm A and Swarm B both have Sonnet coordinator
- Haikus from A need result from Haiku in B
- Direct Haiku-to-Haiku via Context Memory
- Sonnet coordinators sync state periodically (not per-message)
- Conflict resolution: timestamp + swarm priority
```

### B14: Audit System for Claude Max Communications
```
TASK: Implement full audit trail for all Claude Max communications
OUTPUT: /home/setup/infrafabric/src/core/audit/claude_max_audit.py
REQUIREMENTS:
- Every message logged (sender, receiver, timestamp, content_hash)
- Cross-swarm messages tagged with both swarm IDs
- Searchable by agent, swarm, time range, message type
- Retention: 30 days in Context Memory, archive to Deep Storage
- IF.citation generated for significant decisions
```

### B15: Resilience Testing
```
TASK: Create resilience test suite
OUTPUT: /home/setup/infrafabric/tests/resilience/test_claude_max_resilience.py
SCENARIOS:
- Agent timeout during task
- Context Memory (Redis) temporary unavailability
- Deep Storage (ChromaDB) timeout
- Network partition between swarms
- Coordinator (Sonnet) crash mid-task
- 100 concurrent Haiku agents
EXPECTED: Graceful recovery, no data loss, audit trail intact
```

---

# PART 6: INTEGRATION & SYNTHESIS

### Haiku Agent Tasks (B16-B20)

### B16: Component Integration Map
```
TASK: Create visual integration map
OUTPUT: /home/setup/infrafabric/docs/architecture/INTEGRATION_MAP.md
DIAGRAM: ASCII art showing:
- OpenWebUI ↔ IF.api.openwebui ↔ IF.matrix.route
- Context Memory ↔ S2 Swarm Coordinator ↔ Claude Max Registry
- Deep Storage ↔ IF.emotion ↔ IF.guard
- All audit trails → IF.TTT
```

### B17: Configuration Schema
```
TASK: Create unified configuration schema
OUTPUT: /home/setup/infrafabric/config/infrafabric.schema.json
SECTIONS:
- interfaces: (openwebui, cli, api)
- memory: (context_memory, deep_storage)
- agents: (claude_max models, if.emotion)
- security: (sandboxing, rate_limits)
- audit: (log_level, retention, storage)
```

### B18: Deployment Guide
```
TASK: Create deployment guide for integrated system
OUTPUT: /home/setup/infrafabric/docs/deployment/INTEGRATION_DEPLOYMENT.md
STEPS:
1. Prerequisites (Redis, ChromaDB, API keys)
2. Configuration
3. Memory initialization
4. Agent registration
5. Security hardening
6. Health checks
7. Monitoring setup
```

### B19: Test Plan
```
TASK: Create comprehensive integration test plan
OUTPUT: /home/setup/infrafabric/docs/testing/INTEGRATION_TEST_PLAN.md
PHASES:
1. Unit tests (each component)
2. Integration tests (component pairs)
3. End-to-end tests (full workflows)
4. Security tests (attack scenarios)
5. Performance tests (latency, throughput)
6. Resilience tests (failure scenarios)
```

### B20: Mission Summary Report
```
TASK: Synthesize all outputs into executive summary
OUTPUT: /home/setup/infrafabric/MISSION_REPORT_2025-11-30.md
SECTIONS:
- Executive Summary
- Completed Tasks (checklist)
- Key Decisions Made
- Risks Identified
- Recommendations
- Next Steps
- IF.citation references
```

---

# EXECUTION INSTRUCTIONS

## For Sonnet Coordinator A (Infrastructure)

```
You are Sonnet Coordinator A for the InfraFabric Integration Swarm Mission.

Your responsibility: SPAWN Haiku agents A1-A15 to complete:
- OpenWebUI API Integration (A1-A5)
- Memory Module Architecture (A6-A10)
- S2 Swarm Communication (A11-A15)

EXECUTION RULES:
1. Spawn Haikus in PARALLEL batches of 5 for independent tasks
2. For dependent tasks, wait for prerequisites
3. Each Haiku receives: task spec, input files, output path
4. Haiku outputs are written directly to filesystem
5. You SYNTHESIZE results, resolve conflicts, ensure coherence
6. All outputs MUST include IF.citation references
7. Log all agent communications to swarm_audit

BUDGET: Target <$8 for your swarm (15 Haiku tasks)

START by reading:
- /home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md
- /home/setup/infrafabric/docs/demonstrations/IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30.md

Then spawn A1-A5 in parallel.
```

## For Sonnet Coordinator B (Security)

```
You are Sonnet Coordinator B for the InfraFabric Integration Swarm Mission.

Your responsibility: SPAWN Haiku agents B1-B20 to complete:
- IF.emotion Security Sandboxing (B1-B8)
- Claude Max LLM Registry (B9-B15)
- Integration & Synthesis (B16-B20)

EXECUTION RULES:
1. Spawn Haikus in PARALLEL batches of 5 for independent tasks
2. For dependent tasks, wait for prerequisites
3. Each Haiku receives: task spec, input files, output path
4. Haiku outputs are written directly to filesystem
5. You SYNTHESIZE results, resolve conflicts, ensure coherence
6. All outputs MUST include IF.citation references
7. Log all agent communications to swarm_audit

BUDGET: Target <$7 for your swarm (20 Haiku tasks)

START by reading:
- /home/setup/infrafabric/IF_EMOTION_COMPONENT_PROPOSAL.md
- /home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py

Then spawn B1-B5 in parallel.
```

---

# SUCCESS CRITERIA

## Minimum Viable Deliverables
- [ ] OpenWebUI API catalog document
- [ ] Context Memory + Deep Storage specifications
- [ ] S2 vs MCP comparison analysis
- [ ] IF.emotion threat model
- [ ] Claude Max registry implementation
- [ ] Mission summary report

## Quality Gates
- All code files pass syntax check
- All markdown files are valid
- IF.citation references present in every output
- No placeholder content ("TODO", "TBD")
- Security recommendations are actionable

## Timeline
- Sonnet A and B execute concurrently
- Expected duration: 45-90 minutes
- Report generation: 15 minutes post-completion

---

# CITATIONS

- `if://doc/s2-swarm-comms/2025-11-26` → /home/setup/infrafabric/papers/IF-SWARM-S2-COMMS.md
- `if://doc/openwebui-debate/2025-11-30` → /home/setup/infrafabric/docs/demonstrations/IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30.md
- `if://doc/if-emotion-proposal/2025-11-30` → /home/setup/infrafabric/IF_EMOTION_COMPONENT_PROPOSAL.md
- `if://code/redis-swarm-coordinator` → /home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py
- `if://agent/if-emotion/v1.0` → /home/setup/infrafabric/IF.emotion.md

---

**Mission Status:** READY FOR EXECUTION
**Created:** 2025-11-30
**Author:** Claude (Opus 4.5) via IF.optimise delegation
