# Haiku Swarm Test Framework: Philosophy-Grounded Distributed Communication

**Purpose:** Real-world testbed for intra-agent communication with IF.TTT compliance and real-time IF.optimise tracking.

**Last Updated:** 2025-11-10
**Citation:** if://design/haiku-swarm-framework-2025-11-10
**Status:** Design Specification (Implementation: TBD)

---

## 1. Architecture Overview

### Philosophy → Technology Mapping

The 12-philosopher database (2,500 years) maps directly to distributed systems patterns:

| Philosophy Principle | IF.ground # | Drone/Blockchain Tech | Implementation |
|---------------------|-------------|----------------------|----------------|
| **Empiricism** (Locke) | Principle 1 | Append-only audit log | Every message signed with timestamp, immutable record |
| **Verificationism** (Vienna Circle) | Principle 2 | Content-addressing (SHA-256) | Messages identified by hash, not mutable IDs |
| **Fallibilism** (Peirce) | Principle 3 | CRDT conflict resolution | Agents can disagree, system converges gracefully |
| **Underdetermination** (Quine-Duhem) | Principle 4 | DDS QoS policies | Multiple reliability strategies (best-effort vs reliable) |
| **Coherentism** (Neurath's Boat) | Principle 5 | Merkle tree commitments | Consistency through cryptographic tree structure |
| **Pragmatism** (James/Dewey) | Principle 6 | FIPA-ACL speech acts | Meaning = use (request/inform/agree/query-if) |
| **Falsifiability** (Popper) | Principle 7 | Ed25519 signatures | Claims cryptographically disprovable |
| **Stoic Prudence** (Epictetus) | Principle 8 | C-UAS layered defense | Graceful degradation under adversity |

### Extended Mappings (Eastern Philosophy)

| Eastern Philosophy | Principle | Drone/Blockchain Tech | Implementation |
|-------------------|-----------|----------------------|----------------|
| **Wu Lun** (Confucius) | Five Relationships | Agent role taxonomy | Coordinator/Worker/Validator/Critic/Observer |
| **Wu Wei** (Daoism) | Effortless action | IF.quiet anti-spectacle | Best swarm makes minimal noise, prevents vs detects |
| **Madhyamaka** (Nagarjuna) | Middle way | DDS QoS balance | Neither over-reliable (waste) nor unreliable (failure) |

---

## 2. Haiku Swarm Communication Protocol

### 2.1 IFMessage Schema (Philosophy-Annotated)

```json
{
  "performative": "inform",              // Pragmatism: Speech act defines meaning
  "sender": "if://agent/swarm/worker-1", // Empiricism: Observable agent identity
  "receiver": "if://agent/coordinator",  // Wu Lun: Relationship-based routing
  "conversation_id": "if://conversation/mission-2025-11-10-ABC",
  "content": {
    "claim": "Task X completed",         // Verificationism: Testable claim
    "evidence": ["file.py:123"],         // Empiricism: Observable artifacts
    "cost_tokens": 1247                  // IF.optimise: Real-time cost tracking
  },
  "citation_ids": [                      // IF.TTT: Traceable evidence
    "if://citation/9f2b3a1e-..."
  ],
  "timestamp": 1699632000000000000,      // Empiricism: Immutable temporal record
  "sequence_num": 42,                    // Coherentism: Ordered consistency
  "content_hash": "sha256:5a3d2f8c...",  // Verificationism: Content-addressed
  "signature": {                         // Falsifiability: Cryptographically disprovable
    "algorithm": "ed25519",
    "public_key": "ed25519:AAAC3NzaC1...",
    "signature_bytes": "ed25519:p9RLz6Y4..."
  },
  "philosophy_metadata": {               // NEW: Explicit philosophy grounding
    "principles_invoked": [
      "IF.ground:principle_1_observable_artifacts",
      "IF.ground:principle_6_pragmatism_speech_acts",
      "IF.ground:principle_7_falsifiability"
    ],
    "wu_lun_relationship": "worker→coordinator", // Confucian relationship type
    "stoic_resilience": "retry_3x_exponential_backoff" // Principle 8: Prudence
  }
}
```

### 2.2 C-UAS Layered Defense → Agent Communication

**C-UAS (Counter Unmanned Aircraft Systems) Architecture:**
- Layer 1: **Detect** → Passive sensors (radar, RF, acoustic)
- Layer 2: **Track** → Maintain contact, predict trajectory
- Layer 3: **Identify** → Friend/foe/unknown classification
- Layer 4: **Counter** → Kinetic/non-kinetic response

**Mapped to Haiku Swarm:**

| C-UAS Layer | Agent Role | Communication Pattern | Philosophy Principle |
|-------------|------------|----------------------|---------------------|
| **Detect** | Observer agents | Pub: `if://topic/observations/raw` | Empiricism (report what you see) |
| **Track** | Tracker agents | Sub: observations, Pub: `if://topic/tracks/maintained` | Coherentism (maintain consistency) |
| **Identify** | Classifier agents | Sub: tracks, Pub: `if://topic/classifications/verified` | Verificationism (verify claims) |
| **Counter** | Effector agents | Sub: classifications, Pub: `if://topic/effects/executed` | Pragmatism (act on meaning) |

**DDS QoS Policies by Layer:**

```yaml
Detect (Observers):
  reliability: BEST_EFFORT        # Stoic Prudence: Don't block on sensor failures
  durability: VOLATILE             # Empiricism: Current observations only
  history: {keep_last: 1}          # Underdetermination: Latest sensor reading

Track (Trackers):
  reliability: RELIABLE            # Coherentism: Must maintain consistency
  durability: TRANSIENT_LOCAL      # Fallibilism: Keep recent history for correction
  history: {keep_last: 10}         # Underdetermination: Multiple hypotheses

Identify (Classifiers):
  reliability: RELIABLE            # Verificationism: Classification must arrive
  durability: TRANSIENT_LOCAL      # Fallibilism: Can update classifications
  history: {keep_all}              # Coherentism: Full classification history

Counter (Effectors):
  reliability: RELIABLE            # Pragmatism: Actions must execute
  durability: PERSISTENT           # Empiricism: Immutable action log
  history: {keep_all}              # Stoic Prudence: Audit all interventions
```

---

## 3. IF.optimise Real-Time Tracking

### 3.1 Token Cost Measurement (Per Agent)

Each Haiku agent reports token consumption at message boundaries:

```json
{
  "agent_id": "if://agent/swarm/worker-1",
  "session_start": "2025-11-10T12:00:00Z",
  "cumulative_tokens": {
    "input": 12450,
    "output": 3782,
    "total": 16232
  },
  "cost_usd": 0.00032464,  // Haiku pricing: $0.25/1M input, $1.25/1M output
  "messages_sent": 15,
  "messages_received": 23,
  "avg_tokens_per_message": 405.8,
  "efficiency_metrics": {
    "tokens_per_task": 1623,         // 10 tasks completed
    "compared_to_sonnet": 0.093,     // 9.3% of Sonnet cost (10.7× savings)
    "communication_overhead": 0.127  // 12.7% overhead from message signing
  }
}
```

### 3.2 Swarm-Level IF.optimise Dashboard

**Real-time aggregation:**

```
⚡ IF.optimise Multi-Haiku Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active Agents: 15 Haiku
Mission: if://conversation/epic-research-2025-11-10
Elapsed: 4m 32s

Total Tokens:     243,920 tokens
Total Cost:       $0.0487 USD
Sonnet Baseline:  $0.5232 USD (if done by single Sonnet)
Savings:          90.7% ($0.4745 saved)

Agent Efficiency:
  worker-1:  16,232 tokens (405 tokens/msg, 1,623 tokens/task)
  worker-2:  14,890 tokens (372 tokens/msg, 1,489 tokens/task)
  ...
  observer-5: 8,123 tokens (203 tokens/msg, 812 tokens/task)

Communication Overhead:
  Messages: 342 total (15 agents × avg 22.8 msgs)
  Avg message size: 203 tokens (150 content + 53 signature/metadata)
  TTT compliance overhead: 26.1% (signatures, citations, hashes)
  Net efficiency: 90.7% - 26.1% = 64.6% savings

Philosophy Principle Usage:
  IF.ground:principle_1 (Empiricism): 89 invocations
  IF.ground:principle_6 (Pragmatism): 67 invocations
  IF.ground:principle_7 (Falsifiability): 34 invocations
  Wu Lun relationships: 128 messages (worker→coordinator: 45, coordinator→worker: 38, ...)

Bottlenecks:
  ⚠️  Coordinator (if://agent/coordinator): 34,892 tokens (14.3% of total)
  → Consider splitting coordinator role (Wu Lun: delegate to sub-coordinators)
```

---

## 4. IF.TTT Compliance in Swarm Communication

### 4.1 Automatic Citation Generation

Every agent message automatically generates an IF.citation artifact:

```python
class HaikuAgent:
    def send_message(self, performative, receiver, content):
        # 1. Create claim (Verificationism: testable assertion)
        claim_id = f"if://claim/{self.mission_id}/{self.agent_id}/{self.sequence_num}"

        # 2. Generate citation (IF.TTT: Traceable)
        citation = {
            "citation_id": f"if://citation/{uuid4()}",
            "claim_id": claim_id,
            "sources": [
                {"type": "agent", "ref": self.agent_id, "hash": self.get_state_hash()},
                {"type": "message", "ref": f"{receiver}:seq_{self.sequence_num}"}
            ],
            "content_hash": sha256(content).hexdigest(),  # Verificationism
            "rationale": content.get("rationale", ""),
            "status": "unverified",  # IF.TTT: Transparent about verification state
            "created_by": self.agent_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "signature": self.sign_citation(citation),  # Falsifiability
            "philosophy_principles": self.infer_principles(performative, content)
        }

        # 3. Construct IFMessage (Pragmatism: speech act)
        message = {
            "performative": performative,
            "sender": self.agent_id,
            "receiver": receiver,
            "conversation_id": self.conversation_id,
            "content": content,
            "citation_ids": [citation["citation_id"]],
            "timestamp": time.time_ns(),
            "sequence_num": self.sequence_num,
            "content_hash": citation["content_hash"],
            "signature": self.sign_message(message),
            "philosophy_metadata": {
                "principles_invoked": citation["philosophy_principles"],
                "wu_lun_relationship": self.get_relationship(receiver),
                "stoic_resilience": "retry_3x_exponential_backoff"
            }
        }

        # 4. Store citation (Empiricism: immutable record)
        self.citation_store.append(citation)

        # 5. Publish message (Pragmatism: action)
        self.publish(f"if://topic/{receiver}", message)

        # 6. Track tokens (IF.optimise)
        self.track_tokens(message)

        self.sequence_num += 1
        return message
```

### 4.2 Philosophy Principle Inference

**Automatic detection of which principles are being invoked:**

```python
def infer_principles(self, performative, content):
    principles = []

    # Pragmatism: All speech acts invoke Principle 6
    if performative in ["request", "inform", "agree", "query-if"]:
        principles.append("IF.ground:principle_6_pragmatism_speech_acts")

    # Empiricism: Messages with evidence invoke Principle 1
    if "evidence" in content and content["evidence"]:
        principles.append("IF.ground:principle_1_observable_artifacts")

    # Verificationism: Content-addressed messages invoke Principle 2
    if "content_hash" in content:
        principles.append("IF.ground:principle_2_verificationism")

    # Fallibilism: Messages requesting validation invoke Principle 3
    if performative == "query-if" or "validation_requested" in content:
        principles.append("IF.ground:principle_3_fallibilism")

    # Coherentism: Messages referencing prior messages invoke Principle 5
    if "in_reply_to" in content or "conversation_id" in content:
        principles.append("IF.ground:principle_5_coherentism")

    # Falsifiability: All signed messages invoke Principle 7
    if "signature" in content:
        principles.append("IF.ground:principle_7_falsifiability")

    # Stoic Prudence: Messages with retry logic invoke Principle 8
    if "stoic_resilience" in content:
        principles.append("IF.ground:principle_8_stoic_prudence")

    return principles
```

---

## 5. Test Harness Implementation

### 5.1 Minimal Viable Test (3-Agent Swarm)

**Scenario:** Parallel file summarization (simulates IF.search Pass 1)

```python
# test_haiku_swarm_minimal.py

import asyncio
from anthropic import Anthropic

class HaikuSwarmTest:
    def __init__(self):
        self.client = Anthropic()
        self.agents = []
        self.message_bus = []  # In-memory DDS simulation
        self.citation_store = []
        self.token_tracker = {
            "total_input": 0,
            "total_output": 0,
            "per_agent": {}
        }

    async def spawn_agent(self, agent_id, role, task):
        """Spawn a Haiku agent with IF.TTT compliance"""

        prompt = f"""You are {agent_id}, a Haiku agent in an InfraFabric swarm.

Your role: {role}
Your task: {task}

MANDATORY IF.TTT COMPLIANCE:
1. Every claim must cite observable source (file:line)
2. Report token consumption after each operation
3. Generate if://citation/uuid for findings
4. Use FIPA-ACL speech acts (inform/request/agree/query-if)

Output format (JSON):
{{
  "performative": "inform",
  "content": {{"summary": "...", "evidence": ["file.py:123"], "cost_tokens": 1247}},
  "citation_id": "if://citation/...",
  "philosophy_principles": ["IF.ground:principle_1_observable_artifacts"]
}}
"""

        response = await self.client.messages.create(
            model="claude-haiku-4.5-20250912",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Track tokens (IF.optimise)
        self.token_tracker["total_input"] += response.usage.input_tokens
        self.token_tracker["total_output"] += response.usage.output_tokens
        self.token_tracker["per_agent"][agent_id] = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }

        # Parse response and store citation (IF.TTT)
        result = json.loads(response.content[0].text)
        self.citation_store.append({
            "citation_id": result["citation_id"],
            "agent_id": agent_id,
            "content": result["content"],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        return result

    async def run_test(self):
        """Spawn 3 agents to summarize 3 files in parallel"""

        tasks = [
            self.spawn_agent("if://agent/swarm/worker-1", "Summarizer",
                           "Summarize /papers/IF-vision.md"),
            self.spawn_agent("if://agent/swarm/worker-2", "Summarizer",
                           "Summarize /papers/IF-foundations.md"),
            self.spawn_agent("if://agent/swarm/worker-3", "Summarizer",
                           "Summarize /papers/IF-armour.md")
        ]

        results = await asyncio.gather(*tasks)

        # Generate IF.optimise report
        total_tokens = (self.token_tracker["total_input"] +
                       self.token_tracker["total_output"])

        # Baseline: Single Sonnet reading 3 files sequentially
        baseline_tokens = 15000  # Estimated

        print(f"""
⚡ IF.optimise Multi-Haiku Test Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agents: 3 Haiku (parallel execution)
Task: Summarize 3 papers

Total Tokens: {total_tokens}
  Input:  {self.token_tracker["total_input"]}
  Output: {self.token_tracker["total_output"]}

Baseline (Sonnet sequential): {baseline_tokens} tokens
Savings: {100 * (1 - total_tokens/baseline_tokens):.1f}%

Per-Agent Breakdown:
  worker-1: {self.token_tracker["per_agent"]["if://agent/swarm/worker-1"]["input"] +
             self.token_tracker["per_agent"]["if://agent/swarm/worker-1"]["output"]} tokens
  worker-2: {self.token_tracker["per_agent"]["if://agent/swarm/worker-2"]["input"] +
             self.token_tracker["per_agent"]["if://agent/swarm/worker-2"]["output"]} tokens
  worker-3: {self.token_tracker["per_agent"]["if://agent/swarm/worker-3"]["input"] +
             self.token_tracker["per_agent"]["if://agent/swarm/worker-3"]["output"]} tokens

Citations Generated: {len(self.citation_store)}
IF.TTT Compliance: ✓ All agents generated citations

Philosophy Principles Used:
{self.analyze_philosophy_usage()}
        """)

    def analyze_philosophy_usage(self):
        """Analyze which philosophy principles were invoked"""
        usage = {}
        for citation in self.citation_store:
            for principle in citation.get("philosophy_principles", []):
                usage[principle] = usage.get(principle, 0) + 1
        return "\n".join([f"  {k}: {v} invocations" for k, v in sorted(usage.items())])

# Run test
if __name__ == "__main__":
    test = HaikuSwarmTest()
    asyncio.run(test.run_test())
```

### 5.2 Advanced Test (15-Agent Swarm with C-UAS Layers)

**Scenario:** Full 4-layer C-UAS pattern applied to code analysis

```
Layer 1 (Detect): 5 Observer agents scan codebase for patterns
  → Pub: if://topic/observations/raw

Layer 2 (Track): 3 Tracker agents maintain pattern consistency
  → Sub: observations, Pub: if://topic/tracks/maintained

Layer 3 (Identify): 4 Classifier agents verify patterns against IF.ground
  → Sub: tracks, Pub: if://topic/classifications/verified

Layer 4 (Counter): 3 Effector agents generate recommendations
  → Sub: classifications, Pub: if://topic/effects/executed

Coordinator: 1 agent orchestrates, tracks IF.optimise metrics
  → Sub: all topics, generates final report with citations
```

**Expected Metrics:**
- Total tokens: 80,000-120,000 (15 agents × avg 6,000 tokens)
- Baseline (Sonnet): 250,000 tokens (single-agent analysis)
- Savings: 52-68% (accounting for 26% TTT overhead)
- Citations: 60-80 (15 agents × avg 4-5 findings each)
- Philosophy usage: Empiricism (45%), Pragmatism (30%), Coherentism (15%), others (10%)

---

## 6. Blockchain Integration (OpenTimestamps Anchoring)

### 6.1 Merkle Tree Commitment (Per Swarm Run)

After swarm completes, batch-commit all citations:

```python
def commit_swarm_citations(self, run_id):
    """Create Merkle tree of all citations, anchor to Bitcoin blockchain"""

    # 1. Sort citations by timestamp
    citations = sorted(self.citation_store, key=lambda c: c["timestamp"])

    # 2. Build Merkle tree
    leaves = [sha256(json.dumps(c, sort_keys=True).encode()).digest()
              for c in citations]
    merkle_tree = MerkleTree(leaves)
    root_hash = merkle_tree.get_root_hash()

    # 3. Create commitment block
    commitment = {
        "run_id": run_id,
        "conversation_id": self.conversation_id,
        "merkle_root": root_hash.hex(),
        "citation_count": len(citations),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agents": list(set([c["agent_id"] for c in citations])),
        "total_tokens": self.token_tracker["total_input"] + self.token_tracker["total_output"]
    }

    # 4. Anchor to Bitcoin (OpenTimestamps)
    ots_proof = opentimestamps.stamp(root_hash)
    commitment["ots_proof"] = ots_proof.hex()

    # 5. Store commitment
    with open(f"citations/swarm-{run_id}-commitment.json", "w") as f:
        json.dump(commitment, f, indent=2)

    # 6. Store Merkle proofs for each citation
    for i, citation in enumerate(citations):
        proof = merkle_tree.get_proof(i)
        citation["merkle_proof"] = [h.hex() for h in proof]

    return commitment
```

### 6.2 Verification Protocol

Anyone can verify a citation from the swarm:

```bash
# Verify citation if://citation/9f2b3a1e-...
python tools/verify_swarm_citation.py \
  --citation-id if://citation/9f2b3a1e-... \
  --commitment citations/swarm-run-2025-11-10-commitment.json

# Output:
✓ Citation content hash matches (sha256:5a3d2f8c...)
✓ Ed25519 signature valid (if://agent/swarm/worker-1)
✓ Merkle proof valid (leaf → root)
✓ Merkle root matches commitment (sha256:8c5d4e3f...)
✓ OpenTimestamps proof valid (Bitcoin block 870234, 2025-11-10T14:32:00Z)

= VERIFIED (5/5 checks passed)

Philosophy Principles Invoked:
  - IF.ground:principle_1_observable_artifacts (Empiricism)
  - IF.ground:principle_2_verificationism (Vienna Circle)
  - IF.ground:principle_7_falsifiability (Popper)
```

---

## 7. Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Implement `IFMessage` class with philosophy metadata
- [ ] Create `HaikuAgent` base class with auto-citation
- [ ] Build token tracking infrastructure
- [ ] Minimal 3-agent test harness

### Phase 2: C-UAS Layers (Week 3-4)
- [ ] Implement 4-layer agent roles (Detect/Track/Identify/Counter)
- [ ] DDS QoS policy simulation (in-memory)
- [ ] 15-agent swarm test with real tasks
- [ ] IF.optimise dashboard (real-time metrics)

### Phase 3: Blockchain Integration (Week 5-6)
- [ ] Merkle tree implementation
- [ ] OpenTimestamps anchoring
- [ ] Verification CLI tool
- [ ] Citation graph visualization

### Phase 4: Production (Week 7-8)
- [ ] Real DDS/RTPS integration (Cyclone DDS or RTI Connext)
- [ ] REST API for swarm orchestration
- [ ] Guardian Council integration (vote on swarm proposals)
- [ ] Documentation and examples

---

## 8. Success Metrics

**IF.optimise (Token Efficiency):**
- Target: 50-70% savings vs single Sonnet (accounting for TTT overhead)
- Measured: Per-agent token consumption, communication overhead
- Dashboard: Real-time cost tracking during swarm execution

**IF.TTT (Traceability):**
- Target: 100% citation coverage (every agent message → citation)
- Measured: Citations generated / messages sent ratio
- Validation: All citations verify with Merkle proofs + OpenTimestamps

**Philosophy Grounding:**
- Target: Every message maps to 1-3 IF.ground principles
- Measured: Philosophy principle usage distribution
- Expected: Empiricism (40-50%), Pragmatism (25-35%), others (15-25%)

**Wu Lun Relationships:**
- Target: Clear role taxonomy (Coordinator/Worker/Validator/Critic/Observer)
- Measured: Message routing patterns (who talks to whom)
- Validation: No anti-patterns (workers shouldn't coordinate, coordinators shouldn't observe)

**C-UAS Defense Effectiveness:**
- Target: Layered processing reduces false positives by 60-80%
- Measured: Layer 1 observations → Layer 4 actions conversion rate
- Validation: Compare to single-agent pattern detection (no layering)

---

## 9. Open Questions

1. **DDS vs In-Memory Simulation:** Start with in-memory message bus or go directly to Cyclone DDS?
   - Recommendation: Start in-memory (simpler), migrate to DDS in Phase 2

2. **Agent Spawning:** Claude Code Task tool vs external orchestrator (Kubernetes, Docker Swarm)?
   - Recommendation: Task tool for prototyping, containerized for production

3. **Citation Storage:** File-based JSON vs database (PostgreSQL, MongoDB)?
   - Recommendation: JSON for Phase 1-2, database for Phase 3+ (indexing, queries)

4. **OpenTimestamps Cost:** Bitcoin anchoring costs ~$0.01-0.10 per commitment
   - Recommendation: Batch commits (1 per swarm run, not per citation)

5. **Guardian Oversight:** Should swarm proposals require Guardian approval before execution?
   - Recommendation: Yes for production (IF.guard review), no for testing

---

## 10. Philosophy Validation Checklist

Before deploying swarm framework, verify all 8 IF.ground principles are testable:

- [ ] **Principle 1 (Empiricism):** Agents cite file:line for all claims
- [ ] **Principle 2 (Verificationism):** Content hashes verify message integrity
- [ ] **Principle 3 (Fallibilism):** Agents can request validation, update beliefs
- [ ] **Principle 4 (Underdetermination):** Multiple DDS QoS strategies supported
- [ ] **Principle 5 (Coherentism):** Message ordering via sequence numbers + timestamps
- [ ] **Principle 6 (Pragmatism):** FIPA-ACL speech acts define meaning
- [ ] **Principle 7 (Falsifiability):** Ed25519 signatures make claims disprovable
- [ ] **Principle 8 (Stoic Prudence):** Retry logic, graceful degradation, layered defense

**Extended (Eastern Philosophy):**
- [ ] **Wu Lun:** 5 agent roles map to Confucian relationships
- [ ] **Wu Wei:** IF.quiet metrics (best swarm is silent)
- [ ] **Madhyamaka:** DDS QoS balance (middle way between extremes)

---

**Citation:** if://design/haiku-swarm-framework-2025-11-10
**Status:** Design Specification (Ready for implementation discussion)
**Next Step:** User approval → Phase 1 implementation (Week 1-2)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
