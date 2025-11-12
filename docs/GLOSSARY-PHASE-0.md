# InfraFabric Phase 0 Glossary

**Quick reference for Phase 0 and Swarm of Swarms (S²) terminology**

**Last Updated:** 2025-11-12
**Audience:** All sessions, new contributors, external reviewers

---

## Table of Contents

1. [Core Components](#core-components)
2. [Coordination Concepts](#coordination-concepts)
3. [Technical Infrastructure](#technical-infrastructure)
4. [Performance Metrics](#performance-metrics)
5. [Session Organization](#session-organization)
6. [Workflow & Process](#workflow--process)
7. [Security & Cryptography](#security--cryptography)
8. [Philosophical Foundations](#philosophical-foundations)

---

## Core Components

### IF.coordinator
**Real-time task coordination system**
- Replaces git polling with event-driven coordination
- Uses etcd + NATS for distributed task management
- Provides <10ms task claim latency
- Eliminates race conditions via atomic CAS operations
- **Example:** When Session 2 claims task P0.1.5, IF.coordinator ensures no other session can claim it simultaneously

### IF.governor
**Resource management and capability matching system**
- Routes tasks to agents based on capabilities (skills, model, tier)
- Enforces budgets (hard limits, soft limits, circuit breaker)
- Optimizes model selection (Haiku for simple, Sonnet for complex)
- Tracks SLOs and reputation scores
- **Example:** If a task requires WebRTC expertise, IF.governor routes it to Session 2

### IF.chassis
**WASM sandbox runtime for agent execution**
- Provides secure, isolated execution environment
- Enforces resource limits (memory, CPU, syscalls)
- Enables cross-platform agent deployment
- Based on wasmtime runtime
- **Example:** Untrusted agent code runs in chassis sandbox, cannot access filesystem directly

### IF.witness
**Cryptographic audit trail system**
- Records events in tamper-proof hash chain
- Uses Ed25519 signatures for authenticity
- Detects tampering via chain verification
- Provides compliance and debugging audit trails
- **Example:** IF.witness records "Session 1 claimed task P0.5.1 at 2025-11-12T14:32:15Z" with cryptographic proof

### IF.optimise
**Cost optimization framework**
- Dynamically selects model tier based on task complexity
- Haiku for simple tasks (1/3 cost of Sonnet)
- Sonnet for complex tasks (3× cost but higher quality)
- Achieves 50% average cost reduction
- **Example:** Documentation task → Haiku, Complex code review → Sonnet

### IF.bus
**Message bus for inter-agent communication**
- Routes messages between sessions (IFMessage protocol)
- Supports pub/sub patterns
- Integrates with IF.coordinator for coordination events
- **Example:** Session 1 publishes NDI stream metadata, Session 2 subscribes for WebRTC conversion

---

## Coordination Concepts

### Swarm of Swarms (S²)
**7 sessions × 7 agents = 49 concurrent agents**
- Multi-session, multi-agent architecture
- Each session focuses on specific protocol or component
- Sessions coordinate autonomously via IF.coordinator
- **Sessions:** NDI (1), WebRTC (2), H.323 (3), SIP (4), CLI (5), Talent (6), IF.bus (7)

### Autonomous Coordination
**Self-directed task assignment without human intervention**
- Sessions read AUTONOMOUS-NEXT-TASKS.md every 5 minutes
- Claim tasks based on assignments
- Execute work autonomously
- Update STATUS files for visibility
- **Example:** Session completes P0.5.1, checks for next task, finds P0.5.4, claims and starts immediately

### Task Claiming
**Atomic process of reserving work**
- Session declares intent to work on specific task
- IF.coordinator ensures exclusive claim (one session per task)
- Prevents duplicate work and race conditions
- **Example:** `claiming: P0.5.1` in STATUS file + IF.coordinator CAS operation

### Filler Tasks
**Work done while blocked on dependencies**
- Maintains 100% productivity (zero idle time)
- Categorized: documentation, testing, code quality, cross-session support
- Prioritized: High (unblocks others), Medium (improves quality), Low (nice-to-have)
- **Example:** Session 1 blocked on P0.5.1 (needs P0.1.5), works on F1.1 (doc improvement) instead

### CMP Principle (Complete, not Maximize Pace)
**Finish all work thoroughly, not as fast as possible**
- Avoid premature termination
- Ensure deliverables meet acceptance criteria
- Quality over speed
- **Example:** Don't skip tests to finish faster - complete ALL acceptance criteria

---

## Technical Infrastructure

### etcd
**Distributed key-value store for coordination**
- Strong consistency guarantees (Raft consensus)
- Atomic CAS (Compare-And-Swap) operations
- Watch API for real-time event notifications
- Used by IF.coordinator for task state
- **Like:** Redis but with stronger consistency, ZooKeeper but simpler
- **Example:** Task state stored at `/tasks/P0.5.1` in etcd

### NATS
**Lightweight message bus for real-time events**
- Pub/sub messaging
- High throughput (millions of messages/sec)
- Low latency (<1ms)
- Used for coordination event broadcasts
- **Example:** When task claimed, IF.coordinator publishes `task_claimed` event to NATS

### CAS (Compare-And-Swap)
**Atomic operation for lock-free synchronization**
- Read current value
- Compare with expected value
- If match, update to new value
- If no match, operation fails (someone else modified it)
- **Example:** Session 1 tries to claim task: CAS(status="available", new="claimed"). If Session 2 already claimed, CAS fails.

### WASM (WebAssembly)
**Secure, portable bytecode format**
- Sandboxed execution (memory isolation, syscall filtering)
- Near-native performance
- Cross-platform (runs on Linux, macOS, Windows)
- Used by IF.chassis for agent code execution
- **Example:** Python agent code compiled to WASM, runs in chassis sandbox

### wasmtime
**WebAssembly runtime implementation**
- Executes WASM bytecode
- Provides resource controls (memory, CPU limits)
- Used by IF.chassis
- **Alternative:** wasmer, Wasmtime chosen for maturity and Rust ecosystem

---

## Performance Metrics

### p95 Latency
**95th percentile latency (95% of requests faster than this)**
- More representative than average (ignores outliers)
- **Example:** p95=8ms means 95% of task claims complete in <8ms

### p99 Latency
**99th percentile latency**
- Used for strict SLAs
- **Example:** p99=15ms means 99% of operations complete in <15ms

### Throughput
**Operations per second**
- **Example:** IF.coordinator: 500 task claims/sec

### RPO (Recovery Point Objective)
**Maximum acceptable data loss**
- Measured in time (how far back we can restore)
- **Example:** 5-min RPO = etcd snapshots every 5 minutes, lose max 5 min of data

### RTO (Recovery Time Objective)
**Maximum acceptable downtime**
- Time to restore service after failure
- **Example:** 15-min RTO = restore from backup in <15 minutes

### SLO (Service Level Objective)
**Target for service performance**
- Internal goal (less strict than SLA)
- **Example:** "99.9% of task claims succeed" (SLO)

### SLA (Service Level Agreement)
**Contractual guarantee of service performance**
- Customer-facing commitment
- **Example:** "99.95% uptime guaranteed" (SLA)

---

## Session Organization

### Session
**Independent Claude Code instance with specific focus**
- Session 1 (NDI): NDI streaming + witness integration
- Session 2 (WebRTC): WebRTC mesh + integration tests
- Session 3 (H.323): H.323 gateway + guardian council
- Session 4 (SIP): SIP proxy + governance policies
- Session 5 (CLI): Command-line tools + witness commands
- Session 6 (Talent): Agent skill management (Phase 1)
- Session 7 (IF.bus): Core bus implementation

### Branch Naming
**claude/{purpose}-{session-id}**
- **Example:** `claude/ndi-witness-streaming-011CV2niqJBK5CYADJMRLNGs`
- Purpose: Describes work focus (ndi-witness-streaming)
- Session ID: Unique identifier (011CV2niqJBK5CYADJMRLNGs)

### STATUS File
**STATUS-SESSION-{N}-{PROTOCOL}.yaml**
- Tracks session progress, current task, blockers
- Updated every 15-60 minutes
- Read by other sessions for coordination
- **Example:** `STATUS-SESSION-1-NDI.yaml`

### Task ID Format
**{Phase}.{Component}.{Sequence}**
- **Phase:** P0 (Phase 0), F1-F7 (Filler), U (Universal)
- **Component:** Logical grouping (1=coordinator, 2=governor, 3=chassis, 4=witness, 5=docs)
- **Sequence:** Task number within component
- **Examples:**
  - `P0.1.1` - Phase 0, Coordinator, Task 1
  - `F1.5` - Filler task for Session 1, Task 5
  - `U.20` - Universal task, Task 20

---

## Workflow & Process

### Primary Task
**Main work assigned to session**
- Appears in AUTONOMOUS-NEXT-TASKS.md
- Blocks on dependencies
- **Example:** P0.5.1 (IF.coordinator documentation) - primary task for Session 1

### Filler Task
**Work done while blocked on primary task**
- Prefix: F{SessionNumber}.{TaskNumber}
- Categories: docs (F1.1-F1.9), tests (F1.10-F1.19), cross-session (F1.20-F1.29), code quality (F1.30-F1.39)
- **Example:** F1.5 (NDI Witness FAQ) - filler task for Session 1

### Universal Task
**Work applicable to any session**
- Prefix: U.{TaskNumber}
- Categories: code quality (U.1-U.9), testing (U.10-U.19), docs (U.20-U.29), infrastructure (U.30-U.39)
- **Example:** U.20 (Update README) - any session can do this

### Acceptance Criteria
**Checklist defining "done"**
- Functional requirements (features work correctly)
- Performance requirements (meets latency/throughput targets)
- Operational requirements (monitoring, runbook entries)
- Security requirements (keys secured, no secrets in code)
- **Example:** P0.5.1 acceptance: "Documentation covers API, config, troubleshooting"

### Blocker
**Dependency preventing progress on task**
- **Example:** P0.5.1 blocked on P0.1.5 (integration tests not ready)
- Recorded in `blocked_on` field of STATUS file
- Triggers switch to filler tasks

### Milestone
**Progress indicator for current work**
- Format: "{Progress}% - {Task} {Status}: {Description}"
- **Example:** "75% - P0.5.1 in progress: API reference complete, examples next"

---

## Security & Cryptography

### Ed25519
**Modern elliptic curve digital signature algorithm**
- Fast: ~0.3ms signing, ~0.5ms verification
- Small: 64-byte signatures, 32-byte keys
- Secure: 128-bit security level
- Used by IF.witness for event signing
- **Alternative:** RSA (slow), ECDSA (implementation bugs)

### Hash Chain
**Cryptographically linked sequence of events**
- Each event includes hash of previous event
- Tampering with any event breaks the chain
- Used by IF.witness for audit trails
- **Example:** Event1(hash=abc) → Event2(prev_hash=abc, hash=def) → Event3(prev_hash=def, hash=ghi)

### Tamper Detection
**Verification that data hasn't been modified**
- Compute hash of event data
- Compare with stored hash
- If mismatch, tampering detected
- **Example:** Event claims hash=abc, computed hash=xyz → tampering detected

### KMS (Key Management Service)
**System for storing cryptographic keys**
- **Examples:** AWS KMS, HashiCorp Vault, etcd with encryption
- Provides: access control, audit logging, key rotation
- Used for IF.witness signing keys in production

### Certificate Authority (CA)
**Issues digital certificates for TLS**
- Signs certificates to prove authenticity
- Used for etcd TLS, IF.coordinator HTTPS
- **Example:** IF.coordinator trusts etcd cert if signed by known CA

---

## Philosophical Foundations

### Wu Lun (五倫)
**Confucian Five Relationships**
- Applied to context weighting in InfraFabric
- Weights: Ruler-Subject (0.90), Father-Son (0.88), Husband-Wife (0.82), Elder-Younger (0.80), Friend-Friend (0.75)
- Used in IF.yologuard secret detection
- **Example:** Email to boss weighted higher (0.90) than email to peer (0.75)

### Page Zero
**Philosophical foundation before technical implementation**
- Epistemology (what can we know?)
- Ethics (what should we do?)
- Governance (how do we coordinate?)
- Wellbeing (what makes AI agents healthy?)
- **Example:** IF.ground based on Page Zero epistemology (falsifiability, provenance, explicit unknowns)

### IF.TTT Principles
**Traceable, Transparent, Trustworthy**
- **Traceable:** Every decision has audit trail (IF.witness)
- **Transparent:** Observable system state (metrics, logs, STATUS files)
- **Trustworthy:** Verifiable correctness (tests, validation, consensus)

### Guardian Council
**20-voice validation system**
- 6 core philosophers (Kant, Popper, Rawls, etc.)
- 12 extended council (Confucius, Nagarjuna, Latour, etc.)
- 8 IF.ceo facets (technical, ethical, pragmatic perspectives)
- Validates architecture decisions via multi-perspective analysis

### CMP (Complete, not Maximize Pace)
**Quality-first work principle**
- Finish all work thoroughly
- Don't rush to completion
- **Example:** Write tests even if they take longer - completeness matters

---

## Acronyms Quick Reference

| Acronym | Full Name | Definition |
|---------|-----------|------------|
| **S²** | Swarm of Swarms | 7-session × 7-agent architecture |
| **CAS** | Compare-And-Swap | Atomic operation for lock-free synchronization |
| **CMP** | Complete, not Maximize Pace | Quality-first work principle |
| **SDP** | Session Description Protocol | WebRTC media negotiation protocol |
| **ICE** | Interactive Connectivity Establishment | WebRTC NAT traversal protocol |
| **DTLS** | Datagram TLS | Secure transport for WebRTC |
| **SIP** | Session Initiation Protocol | VoIP call signaling protocol |
| **NDI** | Network Device Interface | NewTek video streaming protocol |
| **RTC** | Real-Time Communication | Generic term for WebRTC/video |
| **WASM** | WebAssembly | Portable bytecode format |
| **p95/p99** | 95th/99th percentile | Latency metrics |
| **RPO** | Recovery Point Objective | Max acceptable data loss |
| **RTO** | Recovery Time Objective | Max acceptable downtime |
| **SLO** | Service Level Objective | Internal performance target |
| **SLA** | Service Level Agreement | External performance guarantee |
| **KMS** | Key Management Service | Cryptographic key storage |
| **CA** | Certificate Authority | Issues TLS certificates |
| **TLS** | Transport Layer Security | Encryption protocol |
| **HTTPS** | HTTP Secure | HTTP over TLS |
| **TTT** | Traceable, Transparent, Trustworthy | IF core principles |

---

## Common Confusion Points

### Q: What's the difference between IF.coordinator and IF.governor?

**A:**
- **IF.coordinator:** Task state management (which session has which task, claiming, releasing)
- **IF.governor:** Agent selection and resource management (who should get the task, budget enforcement)
- **Analogy:** IF.coordinator is the "task board", IF.governor is the "project manager"

### Q: When do I use etcd vs NATS?

**A:**
- **etcd:** Persistent state (task assignments, configuration, witness events)
- **NATS:** Transient events (task claimed notification, coordination broadcasts)
- **Rule:** If it needs to survive restart → etcd. If it's just a notification → NATS.

### Q: What's the difference between Haiku and Sonnet?

**A:**
- **Haiku:** Smaller, faster, cheaper model (1/3 cost of Sonnet)
- **Sonnet:** Larger, more capable, more expensive model
- **Use:** IF.optimise framework chooses based on task complexity
- **Example:** Documentation → Haiku, Complex architecture design → Sonnet

### Q: What's the difference between primary and filler tasks?

**A:**
- **Primary:** Main work assigned to session (blocks on dependencies)
- **Filler:** Work done while blocked (maintains 100% productivity)
- **Rule:** If blocked → switch to filler. If unblocked → return to primary.

### Q: What does "autonomous coordination" mean?

**A:**
- Sessions read task assignments from shared file (AUTONOMOUS-NEXT-TASKS.md)
- Claim and execute tasks without human approval
- No centralized controller - purely distributed coordination
- **Human role:** Monitoring, unblocking, strategic direction

---

## Usage Examples

### Reading This Glossary

**New Contributor:**
1. Start with [Core Components](#core-components) - understand what you're building
2. Read [Session Organization](#session-organization) - find your session
3. Skim [Workflow & Process](#workflow--process) - understand how work happens
4. Reference [Technical Infrastructure](#technical-infrastructure) as needed

**Experienced Contributor:**
- Use [Acronyms Quick Reference](#acronyms-quick-reference) for quick lookups
- Check [Common Confusion Points](#common-confusion-points) when unclear
- Dive into specific sections as needed

**External Reviewer:**
1. Read [Philosophical Foundations](#philosophical-foundations) - understand the "why"
2. Read [Core Components](#core-components) - understand the "what"
3. Check [Performance Metrics](#performance-metrics) - understand the targets

---

## Related Documentation

- **Architecture:** `docs/SWARM-OF-SWARMS-ARCHITECTURE.md`
- **Onboarding:** `docs/ONBOARDING.md`
- **Component Docs:** `docs/components/IF.COORDINATOR.md`, `docs/components/IF.GOVERNOR.md`
- **Migration Guide:** `docs/MIGRATION-GIT-TO-ETCD.md`
- **Production Runbook:** `docs/PHASE-0-PRODUCTION-RUNBOOK.md`

---

## Contributing to This Glossary

**Add new terms:**
1. Identify which section it belongs to
2. Follow format: **Term** - One-line description, bullet points for details, example
3. Add cross-references where relevant
4. Update Table of Contents

**Improve existing terms:**
- Add clarifying examples
- Add "Common Confusion" entries
- Add cross-references to related documentation

---

**Document Status:** ✅ Complete
**Last Review:** 2025-11-12
**Next Review:** 2025-12-12 (monthly)
**Maintained By:** All sessions (contribute!)
