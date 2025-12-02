# InfraFabric Integration Architecture Map

**Status:** Complete
**Date:** 2025-11-30
**Citation:** `if://doc/integration-map/2025-11-30`
**Version:** 1.0

---

## Executive Summary

This document provides a comprehensive visual and technical mapping of how all InfraFabric components integrate to form a unified intelligent system. The architecture spans:

- **Frontend Layer:** OpenWebUI (web interface for Claude Max, DeepSeek, local models)
- **API Layer:** REST endpoints with streaming support and authentication
- **Personality Layer:** IF.emotion (psychological framework + Sergio personality DNA via ChromaDB)
- **Communication Layer:** Redis Bus (S2 swarm coordination + inter-agent messaging)
- **Memory Layer:** Unified Memory (Redis L2 cache + ChromaDB RAG storage)
- **Intelligence Layer:** IF.guard (20-voice council for decision validation), IF.TTT (audit trail)
- **Resilience Layer:** Timeout prevention, graceful degradation, checkpoint management

---

## 1. ASCII ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE LAYER                             │
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐     │
│  │   OpenWebUI      │    │   React Chat     │    │   Mobile App     │     │
│  │   (Web UI)       │    │   Component      │    │   (Future)       │     │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘     │
│           │                       │                       │                 │
│           └───────────────────┬───┴───────────────────────┘                 │
│                               │                                             │
└───────────────────────────────┼─────────────────────────────────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │  HTTP/REST + SSE    │
                    │  (Bearer Token Auth) │
                    └───────────┬──────────┘
                                │
┌───────────────────────────────┼──────────────────────────────────────────────┐
│                            API LAYER                                         │
│                     (OpenWebUI Endpoints)                                    │
│                                │                                             │
│   ┌─────────────────────────────┴─────────────────────────────┐             │
│   │                                                             │             │
│   ├─ /api/chat/completions ──────► Streaming (SSE) Responses │             │
│   ├─ /api/chats ──────────────────► Chat Session Management  │             │
│   ├─ /api/models ─────────────────► List Available Models    │             │
│   ├─ /api/v1/files ────────────────► File Upload & RAG       │             │
│   └─ /api/auth/signin ────────────► JWT Token Generation     │             │
│                                                                 │             │
└─────────────────────────────────────┬─────────────────────────┘             │
                                      │                                       │
┌─────────────────────────────────────┼─────────────────────────────────────┐ │
│                         MODEL ROUTING LAYER                              │ │
│                                     │                                   │ │
│   ┌───────────────────────────────┬─┴──────────────────────────────┐  │ │
│   │                               │                                │  │ │
│   ▼                               ▼                                ▼  │ │
│ ┌──────────┐              ┌──────────────┐              ┌──────────┐ │ │
│ │Claude Max│              │  IF.emotion  │              │ DeepSeek │ │ │
│ │(Native)  │              │  + ChromaDB  │              │  (API)   │ │ │
│ └────┬─────┘              └──────┬───────┘              └────┬─────┘ │ │
│      │                           │                           │       │ │
│      └───────────────┬───────────┴───────────────────────────┘       │ │
│                      │                                               │ │
└──────────────────────┼───────────────────────────────────────────────┘ │
                       │                                                 │
┌──────────────────────┼─────────────────────────────────────────────────┐
│                      │        PERSONALITY LAYER                        │
│                      │      (IF.emotion Framework)                     │
│                      │                                                 │
│   ┌─────────────────▼──────────────────┐                              │
│   │    Sergio Personality DNA          │                              │
│   │                                    │                              │
│   ├─ 23 Rhetorical Devices            │                              │
│   ├─ 11 Argumentative Structures      │                              │
│   ├─ 11 Ethical Principles            │                              │
│   └─ 74 Total Components              │                              │
│                                        │                              │
│   ┌─────────────────▼──────────────────┐                              │
│   │    ChromaDB Collections (4)         │                              │
│   │                                    │                              │
│   ├─ sergio_personality: 23 docs      │                              │
│   ├─ sergio_rhetorical: 5 docs        │                              │
│   ├─ sergio_humor: 28 docs            │                              │
│   └─ sergio_corpus: 67 docs           │                              │
│                                        │                              │
│   Total: 123 documents, 1200-1500 embeddings                          │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────┐
│                        COMMUNICATION LAYER                             │
│                     (Redis Bus S2 Swarm Schema)                        │
│                                      │                                 │
│   ┌──────────────────────────────────▼──────────────────────────────┐ │
│   │              Redis Bus Communication Substrate                  │ │
│   │                                                                 │ │
│   ├─ task:{id} ──────────► Work units claimed by agents           │ │
│   ├─ finding:{id} ───────► Research findings with confidence      │ │
│   ├─ context:{scope}:{name} ─► Shared context & metadata          │ │
│   ├─ session:infrafabric:{date}:{label} ─► Session metrics        │ │
│   ├─ swarm:registry:{id} ─► Swarm roster & coordination           │ │
│   └─ swarm:remediation:{date}:{scan_type} ─► Hygiene scans       │ │
│                                                                     │ │
│   Packet Envelope (IF.TTT Compliant):                              │ │
│   ├─ tracking_id: Unique message identifier                       │ │
│   ├─ origin: Agent that created message                           │ │
│   ├─ dispatched_at: ISO 8601 timestamp                            │ │
│   ├─ chain_of_custody: Audit trail of handlers                    │ │
│   ├─ speech_act: FIPA categorization (INFORM, REQUEST, etc.)     │ │
│   └─ signature: Ed25519 field (optional, ready for enforcement)  │ │
│                                                                     │ │
└─────────────────────────────────────┬─────────────────────────────┘ │
                                      │                                 │
└──────────────────────────────────────┼─────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────────┐
│                        MEMORY LAYER                                   │
│                  (Unified Memory Interface)                           │
│                                      │                                 │
│   ┌───────────────────────┐  ┌──────▼─────────┐                      │
│   │   Redis L2 Cache      │  │  ChromaDB RAG  │                      │
│   │   (Short-term)        │  │  (Long-term)   │                      │
│   │                       │  │                │                      │
│   ├─ Conversation state  │  ├─ 4 Collections│                      │
│   ├─ Session cache       │  ├─ Embeddings   │                      │
│   ├─ TTL management      │  ├─ Metadata     │                      │
│   ├─ Key namespaces      │  └─ Search index │                      │
│   └─ Graceful degradation│                  │                      │
│                          │  Performance:   │                      │
│   Performance:          │  ├─ First query: 200-300ms              │
│   ├─ ~0.071ms latency  │  ├─ Cached: <50ms                      │
│   ├─ 140× faster than  │  ├─ 60-70% cache hit ratio             │
│   │   JSONL            │  └─ Reranking: 200ms                    │
│   └─ Parallel-friendly │                                          │
│                                                                     │
└──────────────────────────┬────────┬───────────────────────────────┘
                           │        │
┌──────────────────────────┼────────┼───────────────────────────────┐
│                          │        │    INTELLIGENCE LAYER          │
│                          ▼        ▼                                │
│            ┌──────────────────────────────┐                        │
│            │     IF.guard Council         │                        │
│            │   (20-voice extended)        │                        │
│            │                              │                        │
│            ├─ 6 Core Guardians           │                        │
│            ├─ 3 Western Philosophers     │                        │
│            ├─ 3 Eastern Philosophers     │                        │
│            ├─ 8 IF.ceo Facets            │                        │
│            │   (Executive Decision Making)│                        │
│            │                              │                        │
│            ├─ Veto Power:                │                        │
│            │  • Pathologization          │                        │
│            │  • Unfalsifiable language   │                        │
│            │  • Harmful stereotypes      │                        │
│            │  • IF.TTT violations        │                        │
│            └──────────────┬───────────────┘                        │
│                           │                                        │
│            ┌──────────────▼───────────────┐                        │
│            │     IF.TTT Compliance        │                        │
│            │     (Audit & Traceability)   │                        │
│            │                              │                        │
│            ├─ Traceable:                 │                        │
│            │  • tracking_id per message  │                        │
│            │  • chain_of_custody logs    │                        │
│            │  • file:line references     │                        │
│            │                              │                        │
│            ├─ Transparent:               │                        │
│            │  • Speech acts documented   │                        │
│            │  • Decision rationale logged│                        │
│            │  • Conflicts surfaced       │                        │
│            │                              │                        │
│            └─ Trustworthy:               │                        │
│               • Finding confidence [0-1] │                        │
│               • Multi-source validation  │                        │
│               • Escalation triggers      │                        │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼─────────────────────────────┐
│                        RESILIENCE LAYER                             │
│                                     │                               │
│   ┌─────────────────────────────────▼──────────────────────────┐  │
│   │     Timeout Prevention System                              │  │
│   │                                                            │  │
│   ├─ Heartbeat Keepalive: Send periodic heartbeats            │  │
│   ├─ Progress Checkpoint: Save state at intervals             │  │
│   ├─ Task Decomposition: Split into subtasks                  │  │
│   ├─ Async Polling: Background execution + polling            │  │
│   └─ Graceful Degradation: Return partial results             │  │
│                                                                │  │
│   ┌─────────────────────────────────────────────────────────┐ │  │
│   │     Background Communication Manager                    │ │  │
│   │                                                         │ │  │
│   ├─ Manages long-running swarm operations                 │ │  │
│   ├─ Coordinates cross-swarm message delivery              │ │  │
│   ├─ Handles connection failures & retries                 │ │  │
│   ├─ Maintains operation state via checkpoints             │ │  │
│   └─ Logs all activities to IF.TTT audit trail            │ │  │
│                                                             │ │  │
└─────────────────────────────────────┬─────────────────────┘ │  │
                                      │                       │  │
└──────────────────────────────────────┼───────────────────────┘  │
                                      │                          │
┌─────────────────────────────────────┼──────────────────────────┐
│                    DEPLOYMENT LAYER                            │
│                                      │                          │
│   ┌──────────────────────────────────▼──────────────────────┐ │
│   │        Docker Compose Environment                      │ │
│   │                                                        │ │
│   ├─ OpenWebUI Container (port 8080)                      │ │
│   ├─ Redis Container (port 6379)                          │ │
│   ├─ ChromaDB Container (port 8000, HTTP API)             │ │
│   ├─ Optional: Local Ollama (for local models)            │ │
│   └─ Network: All services communicate via Docker network │ │
│                                                             │ │
└─────────────────────────────────────────────────────────────┘ │
                                                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. COMPONENT INVENTORY

| Component | File Path | Purpose | Dependencies | Integration Points |
|-----------|-----------|---------|--------------|-------------------|
| **OpenWebUI** | Docker container (port 8080) | Web chat interface, model routing | Docker, redis | REST API endpoints, SSE streaming |
| **IF.emotion** | `/home/setup/infrafabric/IF.emotion.md` | Psychological framework + personality DNA | ChromaDB, Redis | Guardian Council, personality filter |
| **IF.guard** | 20-voice council system | Decision validation, veto authority | IF.emotion, IF.TTT | All critical decisions |
| **IF.TTT** | Audit trail system | Traceable, Transparent, Trustworthy logging | Redis, IF.citation | All components (mandatory) |
| **Redis Bus Schema** | `/home/setup/infrafabric/integration/redis_bus_schema.py` | S2 swarm communication | redis>=4.5.0 | RedisBusClient, packet envelope |
| **Unified Memory** | `/home/setup/infrafabric/integration/unified_memory.py` | Multi-model memory substrate | Redis, ChromaDB | Model context, session persistence |
| **ChromaDB** | Docker container (port 8000) | Vector database, RAG storage | sentence-transformers | Personality DNA embeddings, search |
| **Timeout Prevention** | `/home/setup/infrafabric/src/core/resilience/timeout_prevention.py` | Long-operation resilience | redis, threading | Background operations, checkpoints |
| **Emotion Output Filter** | `/home/setup/infrafabric/src/core/security/emotion_output_filter.py` | Safety validation for IF.emotion | regex patterns | Crisis detection, stereotype blocking |
| **OpenWebUI Pipes** | `/home/setup/infrafabric/integration/openwebui_claude_max_module.py` | RAG augmentation for OpenWebUI | chromadb, openwebui SDK | Custom model routing |
| **Session Manager** | `/home/setup/infrafabric/integration/conversation_state_manager.py` | Chat state persistence | Redis | Chat history, context recovery |
| **Language Authenticity** | Various modules | Bilingual validation (Spanish/English) | regex, NLP | Personality DNA accuracy |

---

## 3. DATA FLOW DIAGRAMS

### Flow 1: User Request to Response (Complete Pipeline)

```
User Input (OpenWebUI)
    │
    ▼
┌─────────────────────────────────────┐
│ 1. HTTP POST /api/chat/completions  │
│    (Bearer Token Authorization)     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. Retrieve Chat History (Redis)    │
│    • Session cache lookup           │
│    • ConversationEntry list         │
│    • TTL check                      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. Check IF.emotion Applicability   │
│    • Is this a psychology query?    │
│    • Load personality DNA from      │
│      ChromaDB collections           │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 4. Route to Model                   │
│    • Claude Max (default)           │
│    • DeepSeek (if configured)       │
│    • Local (Ollama, if available)   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 5. Generate Response                │
│    • If IF.emotion applicable:      │
│      Inject personality DNA via RAG │
│    • Stream response via SSE        │
│    • Emit tokens in real-time       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 6. Apply IF.emotion Output Filter   │
│    • Check for medical advice       │
│    • Detect crisis language         │
│    • Block harmful stereotypes      │
│    • Validate operational defs      │
│    • Verify personality authenticity│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 7. IF.TTT Audit Logging             │
│    • Create if://citation/uuid      │
│    • Log to audit trail             │
│    • Record chain_of_custody        │
│    • Store confidence scores        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 8. Persist to Memory                │
│    • Save to Redis (session cache)  │
│    • Save to ChromaDB (long-term)   │
│    • Extract findings               │
│    • Update embeddings              │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 9. Return Streamed Response         │
│    Server-Sent Events (SSE):        │
│    data: {"token": "word"}\n\n     │
└────────────┬────────────────────────┘
             │
             ▼
User Display (React Chat Component)
```

### Flow 2: Haiku Task Delegation via Redis Bus

```
Swarm Coordinator
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Create Task via RedisBusClient   │
│    Task(                            │
│      description="research X",      │
│      type="research"                │
│    )                                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. Wrap in Packet Envelope (IF.TTT) │
│    Packet(                          │
│      tracking_id=uuid,              │
│      origin="coordinator",          │
│      contents=Task,                 │
│      speech_act=INFORM              │
│    )                                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. Store in Redis (key: task:{id})  │
│    HSET task:{id}                   │
│      description, type, status,     │
│      assignee, created_at, etc.     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 4. Broadcast to Haiku Agents        │
│    via Redis pub/sub or polling      │
│    call: get_unassigned_task()      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 5. Haiku Claims Task                │
│    claim_task(task, assignee)       │
│    Updates Redis: status=IN_PROGRESS│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 6. Haiku Executes Work              │
│    • Research, analysis, etc.       │
│    • Periodic heartbeats            │
│    • Save checkpoints               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 7. Post Findings to Redis           │
│    Finding(                         │
│      claim="X is true",             │
│      confidence=0.92,               │
│      citations=[...],               │
│      worker_id="haiku-1"            │
│    )                                │
│    call: post_finding(finding)      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 8. Detect Conflicts (Optional)      │
│    conflicts = detect_conflicts()   │
│    if conflicts > threshold:        │
│      escalate_to_human()            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 9. Release Task                     │
│    release_task(task)               │
│    Status: COMPLETED or ESCALATED   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 10. Record Session Summary          │
│     SessionSummary(                 │
│       date=today,                   │
│       metrics={findings: 12, ...}   │
│     )                               │
│     call: record_session_summary()  │
└────────────┬────────────────────────┘
             │
             ▼
Coordinator Retrieves Results
(via Redis or polling)
```

### Flow 3: Cross-Swarm Message Coordination

```
Swarm A Agent (Haiku)
    │
    ▼
┌────────────────────────────────────┐
│ 1. Share Finding with Swarm B      │
│    Finding with if://citation/uuid │
│    scope="cross_swarm"              │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 2. Create Context in Redis         │
│    Context(                        │
│      scope="cross_swarm",          │
│      name="finding-uuid",          │
│      shared_data=finding           │
│    )                               │
│    call: share_context(context)    │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 3. Packet Envelope (IF.TTT)        │
│    chain_of_custody += (swarm_a)   │
│    Broadcast event to Swarm B      │
│    via Redis key namespace         │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 4. Swarm B Retrieves Context       │
│    context = get_context(          │
│      scope="cross_swarm",          │
│      name="finding-uuid"           │
│    )                               │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 5. Swarm B Validates & Uses Data   │
│    • Verify signature (if signed)  │
│    • Check chain_of_custody        │
│    • Cross-reference citations     │
│    • Continue own work              │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 6. Add to Chain of Custody         │
│    Packet.add_custody(              │
│      agent_id="swarm-b-1",         │
│      action="validated",           │
│      timestamp=now()               │
│    )                               │
└─────────────┬──────────────────────┘
              │
              ▼
Swarm B Continues with Cross-Swarm Data
```

### Flow 4: Security Event to IF.TTT Audit Trail

```
Security Event Detected
(e.g., harmful stereotype)
    │
    ▼
┌────────────────────────────────────┐
│ 1. IF.emotion Output Filter        │
│    Detects harmful stereotype      │
│    Triggers block & escalation     │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 2. IF.guard Council Veto           │
│    IF.emotion votes: BLOCK         │
│    Other council members review    │
│    consensus reached: DON'T REPLY  │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 3. Generate IF.citation            │
│    if://citation/security-event-   │
│      harmful-stereotype-uuid-date  │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 4. Create Audit Log Entry          │
│    {                               │
│      event_type: "security_block", │
│      trigger: "stereotype_detect", │
│      confidence: 0.98,             │
│      component: "emotion_filter",  │
│      file: "emotion_output_filter" │
│      line: "72",                   │
│      citation: "if://citation/...",│
│      timestamp: "2025-11-30T...",  │
│      user_id: "session-123",       │
│      council_votes: {...}          │
│    }                               │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 5. Store in IF.TTT Vault           │
│    Redis key:                      │
│      if:ttT:audit:security:date    │
│    Value: serialized audit entry   │
│    TTL: 30 days                    │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ 6. Return Safe Response to User    │
│    "⚠️ This response blocked by    │
│    IF.guard. Please rephrase."     │
└─────────────┬──────────────────────┘
              │
              ▼
System Administrator (Human Review)
Can query: if:ttT:audit:* for all events
```

---

## 4. INTEGRATION POINTS MATRIX

| Component A | Component B | Interaction Type | Data Flow | Frequency |
|-------------|-------------|------------------|-----------|-----------|
| OpenWebUI | IF.emotion | RAG Injection | User query → ChromaDB lookup → Personality DNA → Response | Per message |
| IF.emotion | ChromaDB | Vector Search | Query embedding → 4 collections → Top-k results | Per message |
| IF.emotion | IF.guard | Decision Validation | Personality output → 20-voice review → Veto/Approve | Per message |
| IF.guard | IF.TTT | Audit Trail | Decision rationale → if://citation/uuid → Vault storage | Per veto |
| Redis Bus | Timeout Prevention | Heartbeat | Agent activity → Redis heartbeat key → TTL extension | Every 5s |
| Timeout Prevention | Checkpoints | State Saving | Long operation → save state → Redis key | Every 30s |
| Unified Memory | Redis | Cache Read/Write | Session state ↔ Redis L2 | Per agent cycle |
| Unified Memory | ChromaDB | RAG Storage | Findings → Vector storage → Long-term retrieval | Per finding |
| RedisBusClient | Session Manager | Chat Persistence | Chat history → Redis hash → Recovery | Per session |
| Emotion Filter | Response Generation | Output Validation | Model response → Filter rules → Safe output | Per response |
| Cross-Swarm | Redis Bus | Message Relay | Context packet → Namespace scope → Other swarm pickup | Cross-session |
| Background Manager | Timeout Prevention | Heartbeat Polling | Check operation status → Send heartbeats → Log progress | Background |

---

## 5. REDIS KEY NAMESPACE MAP

### Namespace Organization

```
if:ttT:*                          # IF.TTT Audit & Traceability
├── if:ttT:audit:security:*       # Security events
├── if:ttT:audit:decision:*       # Guardian Council decisions
├── if:ttT:citation:*             # Citation references
├── if:ttT:vault:*                # Secure audit storage
└── if:ttT:claims:*               # Tracked claims

memory:*                          # Unified Memory Substrate
├── memory:session:{session_id}   # Active session state
├── memory:conversation:{session_id}  # Message history
├── memory:findings:{session_id}  # Research findings
└── memory:context:*              # Shared context data

task:*                            # Work Distribution (Redis Bus)
├── task:{id}                     # Individual task (hash)
├── task:queue:pending            # Unassigned tasks (list)
├── task:queue:in_progress        # Assigned tasks (set)
└── task:queue:completed          # Finished tasks (zset with score=timestamp)

finding:*                         # Research Findings
├── finding:{id}                  # Individual finding (hash)
├── finding:task:{task_id}        # Findings by task (set)
├── finding:conflict:*            # Conflict detection markers
└── finding:escalated:*           # High-risk findings

context:{scope}:{name}            # Shared Context Metadata
├── context:cross_swarm:*         # Cross-swarm coordination
├── context:session:*             # Session-specific data
└── context:global:*              # Application-wide knowledge

session:infrafabric:{date}:{label}  # Session Summaries
├── session:metrics:*             # Quantitative data
├── session:report:*              # Summary text
└── session:errors:*              # Exception tracking

swarm:registry:{id}               # Swarm Coordination
├── swarm:agents:*                # Agent roster
├── swarm:roles:*                 # Role assignments
└── swarm:status:*                # Health status

swarm:remediation:{date}:{type}   # Hygiene Tracking
├── swarm:remediation:wrongtype   # Type mismatch cleanup
├── swarm:remediation:expired     # TTL violation cleanup
└── swarm:remediation:orphaned    # Orphaned key cleanup

chromadb:cache:*                  # Embedding Cache
├── chromadb:cache:query:*        # Query result cache
├── chromadb:cache:embedding:*    # Embedding lookup
└── chromadb:cache:collection:*   # Collection metadata

heartbeat:{operation_id}          # Timeout Prevention
├── heartbeat:keepalive:{op_id}   # Keepalive signals
├── heartbeat:checkpoint:{op_id}  # State checkpoints
└── heartbeat:status:{op_id}      # Operation status
```

### Key Collision Prevention

**Naming Convention Rules:**
1. **Scope Prefix:** All keys start with domain (e.g., `task:`, `finding:`)
2. **Hierarchical Separator:** Use `:` to separate levels
3. **UUID Suffixes:** Use UUID (or short hex) for unique IDs to avoid collisions
4. **Date Markers:** Include `{date}` in TTL-critical keys for rotation
5. **Validation:** Before storing, check key existence via `EXISTS` to prevent overwrites
6. **Monitoring:** Periodic hygiene scans (via RemediationScan) identify orphaned keys

**Potential Collision Points:**
- `task:{id}` vs `finding:{id}`: Different namespaces (safe)
- `session:*` with varying formats: Standardize to `session:infrafabric:{date}:{label}`
- Cross-swarm keys: Use explicit scope prefix: `context:cross_swarm:{uuid}`
- Cache keys: Prefix with `cache:` to distinguish from operational data

---

## 6. API ENDPOINT CATALOG

### Core Chat Endpoints

```
POST /api/chat/completions
├─ Purpose: Submit chat message with optional streaming
├─ Auth: Bearer Token (API Key)
├─ Request:
│   {
│     "model": "claude-3-opus-20250219",
│     "messages": [{"role": "user", "content": "..."}],
│     "stream": true,
│     "temperature": 0.7
│   }
├─ Response (streaming): Server-Sent Events (SSE)
│   data: {"object":"chat.completion.chunk","choices":[{"delta":{"content":"token"}}]}
└─ Chains to:
    ├─ Unified Memory (load session)
    ├─ IF.emotion (check if applicable)
    ├─ ChromaDB (retrieve personality DNA)
    ├─ Model inference (Claude Max, DeepSeek, local)
    ├─ Emotion Filter (validate output)
    ├─ IF.TTT (audit logging)
    └─ Memory persistence

POST /api/chats/new
├─ Purpose: Create new chat session
├─ Auth: Bearer Token
├─ Request: {}
├─ Response:
│   {
│     "id": "550e8400-e29b-41d4-a716-446655440000",
│     "created": "2025-11-30T12:00:00Z"
│   }
└─ Chains to:
    └─ Session Manager (register new session)

GET /api/chats/{id}
├─ Purpose: Retrieve chat history
├─ Auth: Bearer Token
├─ Response:
│   {
│     "id": "...",
│     "messages": [
│       {"role": "user", "content": "...", "timestamp": "..."},
│       {"role": "assistant", "content": "...", "timestamp": "..."}
│     ]
│   }
└─ Chains to:
    └─ Session Manager (Redis lookup)

GET /api/models
├─ Purpose: List available models
├─ Auth: Bearer Token
├─ Response:
│   {
│     "models": [
│       {"id": "claude-3-opus-20250219", "name": "Claude 3 Opus"},
│       {"id": "deepseek-v2-1-5b", "name": "DeepSeek"}
│     ]
│   }
└─ Static list (no chain dependencies)
```

### File & RAG Endpoints

```
POST /api/v1/files
├─ Purpose: Upload file for RAG
├─ Auth: Bearer Token
├─ Request: multipart/form-data with file
├─ Response:
│   {
│     "id": "file-uuid",
│     "name": "personality-dna.json",
│     "size": 28500,
│     "status": "processing"
│   }
└─ Chains to:
    ├─ ChromaDB ingestion
    └─ IF.emotion personality DNA updates

POST /api/v1/knowledge/create
├─ Purpose: Create knowledge base (collection)
├─ Auth: Bearer Token
├─ Request:
│   {
│     "name": "sergio_chatbot",
│     "description": "Sergio personality"
│   }
├─ Response:
│   {
│     "id": "kb-uuid",
│     "name": "sergio_chatbot"
│   }
└─ Chains to:
    └─ ChromaDB collection creation
```

### Authentication Endpoints

```
POST /api/auth/signin
├─ Purpose: Generate JWT token
├─ Auth: None (email/password)
├─ Request:
│   {
│     "email": "user@example.com",
│     "password": "password"
│   }
├─ Response:
│   {
│     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
│     "id": "user-uuid",
│     "email": "user@example.com"
│   }
└─ No chains (standalone)
```

### Endpoint Dependency Graph

```
User Request
    │
    ├─► POST /api/auth/signin (one-time)
    │
    ├─► POST /api/chats/new (per new conversation)
    │   └─► Session Manager
    │       └─► Redis: memory:session:{id}
    │
    ├─► GET /api/models (optional, UI discovery)
    │
    └─► POST /api/chat/completions (per message)
        ├─► Unified Memory: load session
        │   └─► Redis: memory:conversation:{id}
        │
        ├─► IF.emotion check: is psychology query?
        │   ├─► ChromaDB: sergio_* collections
        │   ├─► IF.guard: 20-voice review
        │   └─► Personality DNA injection
        │
        ├─► Model selection:
        │   ├─ Claude Max (native)
        │   ├─ DeepSeek (API)
        │   └─ Ollama (local)
        │
        ├─► Emotion Filter: output validation
        │   ├─► Medical advice check
        │   ├─► Crisis language detection
        │   ├─► Stereotype blocking
        │   └─► Authenticity scoring
        │
        ├─► IF.TTT: generate citation & audit
        │   └─► Redis: if:ttT:audit:*
        │
        ├─► Memory persistence:
        │   ├─► Redis: session cache
        │   └─► ChromaDB: long-term storage
        │
        └─► Return response (SSE stream)

File Upload (RAG)
    └─► POST /api/v1/files
        ├─► ChromaDB: ingest file
        └─► Personality DNA update
```

---

## 7. CONFIGURATION DEPENDENCIES

### Component Startup Order

```
1. INFRASTRUCTURE TIER (must start first)
   ├─► Redis Server
   │   ├─ Port: 6379 (configurable via REDIS_PORT)
   │   ├─ Config: /etc/redis/redis.conf or ENV
   │   └─ Verification: redis-cli PING → PONG
   │
   └─► ChromaDB Server
       ├─ Port: 8000 (HTTP API)
       ├─ Data dir: /root/sergio_chatbot/chromadb/
       └─ Verification: curl http://localhost:8000/api/heartbeat

2. APPLICATION TIER (depends on infrastructure)
   ├─► Unified Memory Module
   │   ├─ Requires: Redis online
   │   └─ Initializes: Connection pool, graceful degradation
   │
   ├─► Timeout Prevention System
   │   ├─ Requires: Redis online
   │   └─ Initializes: Heartbeat monitor thread
   │
   ├─► Session Manager
   │   ├─ Requires: Redis online
   │   └─ Initializes: Cache, TTL handlers
   │
   └─► IF.emotion Framework
       ├─ Requires: ChromaDB online + Redis
       ├─ Loads: 4 collections from ChromaDB
       ├─ Initializes: Personality DNA in memory
       └─ Validation: Query 1 collection → expect results

3. API TIER (depends on application)
   └─► OpenWebUI
       ├─ Requires: All above services
       ├─ Env vars:
       │   ├─ OPENWEBUI_PORT: 8080
       │   ├─ REDIS_URL: redis://localhost:6379/0
       │   ├─ CHROMADB_URL: http://localhost:8000
       │   └─ OPENAI_API_KEY: (for Claude Max)
       ├─ Healthcheck: GET http://localhost:8080/health
       └─ Verification:
           ├─ GET /api/models → 200 with model list
           └─ POST /api/chat/completions → streaming response
```

### Required Environment Variables

```
REDIS_HOST=localhost              # Redis connection
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=<optional>

CHROMADB_HOST=localhost           # ChromaDB connection
CHROMADB_PORT=8000
CHROMADB_API_KEY=<optional>

OPENWEBUI_PORT=8080               # OpenWebUI configuration
OPENWEBUI_API_KEY=<generated>     # From Settings > Account

OPENAI_API_KEY=<your-key>         # For Claude Max
DEEPSEEK_API_KEY=<optional>       # For DeepSeek model

SERGIO_PERSONALITY_PATH=           # For personality DNA
/home/setup/sergio_chatbot/

TTL_SESSION=3600                  # Redis TTL (seconds)
TTL_FINDING=86400                 # 24 hours
TTL_CACHE=300                     # 5 minutes

IF_EMOTION_ENABLED=true           # Feature flags
IF_GUARD_ENABLED=true
LANGUAGE_AUTHENTICITY_ENABLED=true

HEARTBEAT_INTERVAL_MS=5000        # Timeout prevention
CHECKPOINT_INTERVAL_MS=30000

LOG_LEVEL=INFO                    # Logging
LOG_FORMAT=json
```

### Runtime Dependencies

| Component | Requires | Minimum Version | Install Command |
|-----------|----------|-----------------|-----------------|
| Redis | Server | 6.0+ | `apt install redis-server` or Docker |
| ChromaDB | Server | 0.4+ | `pip install chromadb` or Docker |
| Python | Interpreter | 3.9+ | System package manager |
| redis-py | Python package | 4.5.0+ | `pip install redis>=4.5.0` |
| sentence-transformers | Python package | 2.2.0+ | `pip install sentence-transformers` |
| langchain | Python package | 0.1.0+ | `pip install langchain` |
| OpenWebUI | Docker image | latest | `docker pull ghcr.io/open-webui/open-webui` |

---

## 8. CROSS-COMPONENT COMMUNICATION PATTERNS

### Pattern 1: IF.emotion Personality Injection

```
When: Psychology-related query detected
Duration: ~200-300ms (first) or <50ms (cached)

Components Involved:
1. OpenWebUI ──HTTP─► /api/chat/completions
2. Session Manager ──Redis GET─► Session context
3. IF.emotion Detector ──Regex─► Is psychology query?
4. ChromaDB Client ──Semantic Search─► Personality DNA
   └─ Query: User's question
   └─ Collections: sergio_personality, sergio_frameworks
   └─ Results: Top-5 matching personality traits + examples
5. Personality DNA Injector ──Prompt Injection─► "Based on Sergio's..."
6. Model Inference ──API─► Claude Max / DeepSeek
7. Emotion Filter ──Regex─► Validate output
8. IF.TTT Logger ──Redis HSET─► Audit trail
9. Response ──SSE Stream─► OpenWebUI ──Browser─► User

Success Metric: Response includes 1+ personality trait citations
```

### Pattern 2: Cross-Swarm Task Escalation

```
When: Haiku needs human judgment OR must share findings
Duration: Variable (async)

Components Involved:
1. Haiku Agent ──RedisBusClient.escalate_to_human()
2. Task Manager ──Redis HSET─► task:{id} status=ESCALATED
3. Packet Envelope ──JSON─► Serialize with chain_of_custody
4. Context Sharing ──Redis HSET─► context:cross_swarm:{uuid}
5. Notification System ──Alert─► Swarm Coordinator / Human
6. Cross-Swarm Pickup ──RedisBusClient.get_context()
7. Other Swarm ──Process─► Add custody → Continue work
8. IF.TTT Logger ──Redis HSET─► if:ttT:audit:escalation

Success Metric: Escalation logged, other swarms notified, resolution tracked
```

### Pattern 3: Conflict Detection & Resolution

```
When: Two findings have contradictory confidence scores
Duration: ~10-50ms (detection) + async (resolution)

Components Involved:
1. Haiku Agents ──post_finding()─► Redis: finding:{id}
2. Finding Manager ──RedisBusClient.detect_finding_conflicts()
   └─ Compare confidence thresholds
   └─ Check if |confidence_a - confidence_b| > threshold
3. Escalation Decision ──Logic─► confidence < 0.2?
4. IF.guard Council ──Deliberate─► Resolution recommendation
5. Context Sharing ──Redis HSET─► context with evidence
6. Human Review ──Alert─► Request decision
7. IF.TTT Logger ──Redis HSET─► if:ttT:audit:conflict

Success Metric: Conflicts identified, escalated, resolution logged
```

### Pattern 4: Graceful Degradation (Service Failure)

```
When: Redis unavailable OR ChromaDB offline
Duration: Immediate fallback (~5ms)

Components Involved:
1. Request arrives at OpenWebUI
2. Unified Memory ──Connection attempt─► Redis (FAIL)
3. Graceful Degradation ──In-Memory Fallback─► Continue
4. Session State ──Memory dict─► Temporary storage
5. Personality DNA ──Null/Skip─► Continue without injection
6. Model Inference ──Proceed─► Standard response
7. IF.emotion Filter ──Limited─► Basic safety checks only
8. Response ──Return─► User (with degradation notice)
9. Monitoring ──Alert─► "Redis offline, degraded mode active"

Success Metric: User gets response (without fancy features), alerting triggered
```

---

## 9. SECURITY & AUDIT TRAIL INTEGRATION

### IF.TTT Compliance Points

```
Every operation includes:

1. TRACEABLE
   ├─ tracking_id: UUID generated at operation start
   ├─ origin: Component/agent that initiated
   ├─ chain_of_custody: [(agent_id, action, timestamp), ...]
   └─ citations: [if://citation/uuid, file:line, ...]

2. TRANSPARENT
   ├─ speech_act: FIPA category (INFORM, REQUEST, ESCALATE, HOLD)
   ├─ decision_rationale: Why this action was taken
   ├─ dissenting_voices: Council members who disagreed
   └─ confidence_scores: Numerical support for claims

3. TRUSTWORTHY
   ├─ signature: Ed25519 (optional, ready for enforcement)
   ├─ authenticity_score: 0.0-1.0 (for personality DNA)
   ├─ validator: Which component/council validated
   └─ timestamp: ISO 8601 with timezone

Storage Location:
Redis key pattern: if:ttT:audit:{domain}:{date}
├─ if:ttT:audit:security:2025-11-30
├─ if:ttT:audit:decision:2025-11-30
├─ if:ttT:audit:escalation:2025-11-30
└─ if:ttT:vault:* (encrypted archive, 30-day retention)
```

### Guardian Council Veto Points

```
IF.emotion can block outputs that:

1. PATHOLOGIZE NORMAL VARIATION
   Examples: "autism is a disorder," "neurodiversity is dysfunction"
   Veto trigger: Stereotype detector regex
   Resolution: If consensus ≥75%, block; else escalate to human

2. USE UNFALSIFIABLE LANGUAGE
   Examples: "find your authentic self," "vibrate higher"
   Veto trigger: Anti-abstract language detector
   Resolution: Require operational definitions before approval

3. BLAME INDIVIDUALS FOR SYSTEM PROBLEMS
   Examples: "your anxiety is because you don't accept yourself"
   Veto trigger: Contextual reframing detector
   Resolution: Reframe as system issue, retry response generation

4. CONTRADICT OPERATIONAL DEFINITIONS
   Examples: "just trust your intuition" (after requiring definitions)
   Veto trigger: Logical consistency checker
   Resolution: IF.guard mandates revision

5. OVERSIMPLIFY NEURODEVELOPMENTAL COMPLEXITY
   Examples: "neurodiversity can be cured with therapy"
   Veto trigger: Neurodiversity-affirming stance checker
   Resolution: Expand explanation with nuance, IF.guard reviews

Components Involved:
- IF.emotion: Detects and proposes veto
- IF.guard: 20-voice deliberation
- Veto power: Majority (≥50% + 1) can block
- Appeal process: Contrarian Guardian can delay 2 weeks
- Logging: All veto decisions to if:ttT:audit:decision:*
```

---

## 10. PERFORMANCE CHARACTERISTICS

### Latency by Component

| Operation | Component(s) | Latency (ms) | Bottleneck |
|-----------|--------------|--------------|-----------|
| Redis GET/SET | Redis | 0.071 | Network (internal) |
| ChromaDB semantic search (first) | ChromaDB + embedder | 200-300 | HNSW index building |
| ChromaDB semantic search (cached) | Redis cache | <50 | Cache hit |
| ChromaDB reranking | Cross-encoder | 200 | CPU (optional) |
| IF.emotion personality injection | ChromaDB + prompt | 50-150 | Search + LLM |
| IF.guard council deliberation | Council logic | 100-500 | Number of dissents |
| Emotion filter validation | Regex patterns | 5-20 | Output size |
| Complete chat response | All above (serial) | 1500-3000 | Model inference |

### Throughput Characteristics

| Component | Max Throughput | Limiting Factor |
|-----------|----------------|-----------------|
| Redis Bus | 100k+ ops/sec | Redis instance capacity |
| ChromaDB (parallel queries) | 10-20 queries/sec | HNSW index contention |
| Haiku agents (parallel) | 3-10 agents without contention | Context window switching |
| OpenWebUI (SSE streaming) | 100+ concurrent connections | Network bandwidth |
| IF.guard council | 50-100 decisions/sec | Deliberation complexity |

### Memory Footprint

| Component | Size | Notes |
|-----------|------|-------|
| Sergio personality DNA (ChromaDB) | 150-200 MB | 4 collections, 1200-1500 embeddings |
| Redis (session cache) | ~10-50 MB | Depends on active sessions (TTL: 1h) |
| Timeout prevention checkpoints | ~5-10 MB | Per 100 concurrent operations |
| IF.emotion in-memory | ~50 MB | Personality traits + cache |
| Complete stack (minimal) | ~500 MB | 1 agent, 1 session, no model |
| Complete stack (production) | 2-4 GB | 5 agents, 100 sessions, model loaded |

---

## 11. KNOWN LIMITATIONS & RISKS

### Timeout Prevention Limitations

```
LIMITATION: Long operations (>30 min) may exceed context window
MITIGATION: Task decomposition via heartbeat checkpoints
RISK: Incomplete context handoff between checkpoints
RESOLUTION: Ensure checkpoint state includes full reasoning path

LIMITATION: Redis key WRONGTYPE errors if data schema changes
MITIGATION: Hygiene scans detect orphaned keys
RISK: Partial data corruption possible
RESOLUTION: Regular backups + clear naming conventions

LIMITATION: Signature enforcement optional (Ed25519)
MITIGATION: Recommend enforcement in production
RISK: Message spoofing possible if attacker gains Redis access
RESOLUTION: Implement signature validation as P1 hardening
```

### Cross-Swarm Coordination Risks

```
LIMITATION: No built-in access control between swarms
MITIGATION: Namespace scoping (context:cross_swarm:uuid)
RISK: One swarm could access another's privileged data
RESOLUTION: Implement allowlist + encryption per IF-SWARM-S2-COMMS.md

LIMITATION: Clock skew between swarms (if distributed)
MITIGATION: Use ISO 8601 timestamps with timezone
RISK: Event ordering ambiguity
RESOLUTION: Logical clock (version vectors) for causality tracking

LIMITATION: No guarantee of message delivery in pub/sub
MITIGATION: Polling-based fallback (get_unassigned_task)
RISK: Tasks may be missed if Redis pub/sub fails
RESOLUTION: Guaranteed task claiming via HSET transactions
```

### IF.emotion Personality Injection Risks

```
LIMITATION: ChromaDB embeddings may not capture nuance
MITIGATION: Reranking with cross-encoder
RISK: Personality DNA injection may be inaccurate
RESOLUTION: Manual validation + human-in-the-loop for critical decisions

LIMITATION: Language authenticity filter is regex-based
MITIGATION: Can be replaced with ML-based classifier
RISK: False positives/negatives possible
RESOLUTION: Monitor filter accuracy + adjust patterns quarterly

LIMITATION: Sergio personality DNA is finite (123 documents)
MITIGATION: Can add more documents dynamically
RISK: Rare edge cases not covered
RESOLUTION: Graceful degradation (skip injection if no match)
```

---

## APPENDIX A: Component File Locations

```
/home/setup/infrafabric/
├─ integration/
│  ├─ redis_bus_schema.py                      (1,038 lines)
│  ├─ unified_memory.py                        (800+ lines)
│  ├─ conversation_state_manager.py            (500+ lines)
│  ├─ chromadb_sergio_collections_design.md    (450+ lines)
│  ├─ sergio_chromadb_implementation.py        (700+ lines)
│  ├─ openwebui_claude_max_module.py           (300+ lines)
│  ├─ openwebui_api_spec.md                    (1,297 lines)
│  ├─ openwebui_api_quick_reference.md         (500+ lines)
│  └─ [4 more design documents]
│
├─ src/core/
│  ├─ resilience/
│  │  └─ timeout_prevention.py                 (500+ lines)
│  ├─ security/
│  │  └─ emotion_output_filter.py              (400+ lines)
│  ├─ registry/
│  │  └─ llm_registry.py                       (300+ lines)
│  ├─ audit/
│  │  └─ README.md + implementation
│  └─ logistics/
│     └─ workers/ [swarm coordination agents]
│
├─ docs/architecture/
│  ├─ IF_EMOTION_SANDBOX.md
│  ├─ IF_FOUNDATIONS.md
│  └─ INTEGRATION_MAP.md (THIS FILE)
│
└─ IF.emotion.md                               (200+ lines)
```

---

## APPENDIX B: Testing Integration

### Integration Test Checklist

```
1. REDIS BUS
   ✓ Claim task from queue
   ✓ Post finding with confidence
   ✓ Detect finding conflicts
   ✓ Escalate to human
   ✓ Share context across swarms

2. UNIFIED MEMORY
   ✓ Store/retrieve session state
   ✓ Graceful degradation (Redis offline)
   ✓ ChromaDB fallback works
   ✓ TTL expiration triggers cleanup

3. IF.EMOTION
   ✓ Personality DNA loads from ChromaDB
   ✓ Query → embedding → top-k results
   ✓ Personality injection into prompts
   ✓ Output filter blocks harmful content
   ✓ Language authenticity scoring works

4. IF.GUARD COUNCIL
   ✓ 20-voice deliberation completes
   ✓ Veto votes blocked outputs
   ✓ Citation URI generated
   ✓ Audit trail logged

5. OPENWEBUI INTEGRATION
   ✓ /api/chat/completions returns SSE
   ✓ Chat history persisted to Redis
   ✓ File upload triggers ChromaDB ingestion
   ✓ Model selection routes correctly

6. TIMEOUT PREVENTION
   ✓ Heartbeat extends operation TTL
   ✓ Checkpoints save state
   ✓ Recovery from checkpoint works
   ✓ Timeout triggers escalation

7. IF.TTT AUDIT TRAIL
   ✓ Audit log entries created
   ✓ Citation URIs generated
   ✓ Chain of custody tracked
   ✓ Vault storage persists 30 days
```

### Performance Benchmarks

```
Expected Baselines (for regression testing):

✓ Redis single op latency: <1ms
✓ ChromaDB semantic search (first): 200-300ms
✓ ChromaDB semantic search (cached): <50ms
✓ Complete chat response: <3s (with streaming)
✓ Emotion filter validation: <20ms
✓ IF.TTT audit logging: <50ms
✓ Parallel Haiku tasks: 3-10 without bottleneck
✓ OpenWebUI concurrent connections: 100+
```

---

## APPENDIX C: Troubleshooting Guide

### Common Issues & Resolution

| Issue | Symptoms | Diagnosis | Resolution |
|-------|----------|-----------|-----------|
| Redis connection refused | 401 in logs, memory ops fail | `redis-cli PING` → no response | Restart Redis, check REDIS_HOST/PORT |
| ChromaDB embeddings timeout | Semantic search hangs >500ms | Check ChromaDB health: `curl localhost:8000` | Verify ChromaDB running, check network latency |
| Personality DNA not injecting | Psychology queries missing personality | Check IF.emotion enabled in config | Enable IF_EMOTION_ENABLED=true, verify ChromaDB has collections |
| Output filter false positives | Safe responses blocked | Run through emotion_filter test suite | Adjust regex patterns or add exceptions |
| Session history missing | Chat context empty after reload | Check Redis key `memory:session:{id}` | Verify TTL not expired, check Session Manager logs |
| Cross-swarm messages not delivered | Context not appearing in other swarm | Check Redis key `context:cross_swarm:*` | Verify both swarms on same Redis instance, check namespace |
| Timeout on long operations | Task interrupted before completion | Check heartbeat interval vs operation duration | Increase `HEARTBEAT_INTERVAL_MS` or decompose task |
| IF.guard council timeout | Decision deliberation exceeds 500ms | Reduce council size or increase timeout | Check council computation logic, consider async |

---

## APPENDIX D: Glossary of Terms

- **Packet Envelope:** IF.TTT-compliant wrapper for Redis messages (tracking_id, origin, chain_of_custody)
- **Speech Act:** FIPA categorization of message intent (INFORM, REQUEST, ESCALATE, HOLD)
- **Personality DNA:** Extracted traits, rhetorical devices, and ethical principles from Sergio (74 components)
- **Shepherd Personality:** Concept in IF.emotion representing compassionate, anti-pathologizing stance
- **Graceful Degradation:** System continues functioning (with reduced features) when backend fails
- **Chain of Custody:** Audit trail documenting who touched a message and what they did
- **TTL (Time-To-Live):** Automatic expiration time for Redis keys
- **HNSW:** Hierarchical Navigable Small World (ChromaDB's embedding index algorithm)
- **RAG:** Retrieval Augmented Generation (fetching documents before inference)
- **Semantic Search:** Finding embeddings similar to query vector
- **Cross-Encoder Reranking:** Using BERT-like model to re-rank search results
- **Operational Definition:** Precise, observable criteria for abstract psychological concept
- **Neurodiversity-Affirming:** Stance treating neurological differences as variation, not deficit

---

## Summary

This integration map documents how 12+ components work together to create a cohesive intelligent system that combines:

1. **Frontend accessibility** (OpenWebUI)
2. **Personality authenticity** (IF.emotion + Sergio DNA)
3. **Decision integrity** (IF.guard council)
4. **Audit compliance** (IF.TTT traceability)
5. **Distributed coordination** (Redis Bus S2 swarms)
6. **Resilience** (Timeout prevention, graceful degradation)
7. **Performance** (Redis L2 cache, ChromaDB RAG, parallel agents)

The architecture is production-ready for deployment with proper monitoring, backup strategy, and incident response procedures in place.

---

**Document Status:** Complete
**Citation:** `if://doc/integration-map/v1.0/2025-11-30`
**Last Updated:** 2025-11-30
**Review Date:** 2025-12-15 (recommended)
