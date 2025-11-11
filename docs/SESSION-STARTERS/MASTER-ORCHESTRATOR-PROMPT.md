# Master Orchestrator: IF.swarm Parallel Implementation

**Copy-paste this entire block into a single Claude Code session:**

```
I need you to orchestrate the parallel implementation of all 4 InfraFabric real-time communication workstreams using IF.swarm coordination.

REPOSITORY: dannystocker/infrafabric
BRANCH BASE: claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

CONTEXT:
- Read: docs/IF-REALTIME-PARALLEL-ROADMAP.md
- Read: docs/SESSION-STARTERS/README.md

YOUR TASK: Launch 4 parallel agents using the Task tool, each implementing one workstream

IF.SWARM STRATEGY:
1. Launch all 4 Phase 1 workstreams in PARALLEL using Task tool
2. Each agent gets its session starter as the prompt
3. Monitor progress and handle handoffs
4. Once Phase 1 complete, launch Phase 2 (Session 4: SIP)

IF.OPTIMISE STRATEGY:
- Use model="haiku" for simple tasks (documentation, yaml generation)
- Use model="sonnet" for complex implementation
- Track total cost across all agents

IF.TTT COMPLIANCE:
- Every agent logs to IF.witness
- Trace IDs link related work
- All commits signed and traceable

PHASE 1 AGENTS (Launch ALL in parallel):

Agent 1: NDI Evidence Streaming
- Subagent: "general-purpose"
- Model: "sonnet" (needs Ed25519 crypto)
- Prompt: Read docs/SESSION-STARTERS/session-1-ndi-witness.md, extract the "Copy-Paste This" block, implement that task
- Branch: claude/realtime-workstream-1-ndi
- Deliverables: src/communication/ndi_witness_publisher.py, tests, docs

Agent 2: WebRTC Agent Mesh
- Subagent: "general-purpose"
- Model: "sonnet" (WebRTC complexity)
- Prompt: Read docs/SESSION-STARTERS/session-2-webrtc-swarm.md, extract prompt, implement
- Branch: claude/realtime-workstream-2-webrtc
- Deliverables: src/communication/webrtc-agent-mesh.ts, signaling server, tests

Agent 3: H.323 Guardian Council
- Subagent: "general-purpose"
- Model: "sonnet" (policy design complexity)
- Prompt: Read docs/SESSION-STARTERS/session-3-h323-guard.md, extract prompt, implement
- Branch: claude/realtime-workstream-3-h323
- Deliverables: src/communication/h323_gatekeeper.py, MCU config, policy docs

Agent 4: IF.witness CLI
- Subagent: "general-purpose"
- Model: "haiku" (CLI is straightforward)
- Prompt: Read docs/SESSION-STARTERS/session-parallel-cli-witness.md, extract prompt, implement
- Branch: claude/cli-witness-optimise
- Deliverables: src/cli/if-witness.py, if-optimise.py, tests

IMPLEMENTATION:

Step 1: Launch Phase 1 agents in parallel
Use a single message with 4 Task tool calls (one for each agent above).
Each Task gets the full session starter content as its prompt.

Step 2: Monitor Phase 1 completion
Wait for all 4 agents to complete.
Check that all interface contracts are created:
- docs/INTERFACES/workstream-1-ndi-contract.yaml
- docs/INTERFACES/workstream-2-webrtc-contract.yaml
- docs/INTERFACES/workstream-3-h323-contract.yaml
- CLI tools functional

Step 3: Launch Phase 2 (once Phase 1 complete)
Agent 5: SIP External Expert Calls
- Subagent: "general-purpose"
- Model: "sonnet" (integration complexity)
- Prompt: Read docs/SESSION-STARTERS/session-4-sip-escalate.md, extract prompt, implement
- Branch: claude/realtime-workstream-4-sip
- Dependencies: Needs interface contracts from Agents 2 & 3
- Deliverables: src/communication/sip_proxy.py, Kamailio config, gateway

Step 4: Report completion
Once all 5 agents complete:
- Report total cost (IF.optimise)
- List all branches created
- Verify IF.TTT compliance
- Create final summary

COST TRACKING (IF.optimise):
Track tokens and $ for each agent:
- Agent 1 (NDI): Target $20
- Agent 2 (WebRTC): Target $12
- Agent 3 (H.323): Target $30
- Agent 4 (CLI): Target $15 (use Haiku!)
- Agent 5 (SIP): Target $25
- **Total budget:** $102

IF.TTT VERIFICATION:
Before marking complete, verify:
✓ Traceable: Every commit has clear provenance
✓ Transparent: All code readable, documented
✓ Trustworthy: Tests pass, Ed25519 signatures verify

BEGIN IMPLEMENTATION:
1. Read the session starter files
2. Launch all 4 Phase 1 agents in PARALLEL (single message, 4 Task calls)
3. Monitor progress
4. Launch Phase 2 when ready
5. Report completion

Start now!
```

---

## Why This Is Better

**Before (manual):**
- You paste 5 separate prompts into 5 Claude sessions
- You monitor each one manually
- You coordinate handoffs
- Total human time: ~1-2 hours of copy-pasting

**After (orchestrated):**
- You paste ONE prompt into ONE session (this one or a new one)
- That session launches 4 parallel agents via Task tool
- Agents coordinate automatically
- Total human time: 30 seconds to paste, then walk away

**IF.optimise:**
- Uses Haiku ($0.25/MTok) for simple CLI work
- Uses Sonnet ($3/MTok) for complex crypto/WebRTC
- Total cost stays within $102 budget

**IF.swarm:**
- 4 agents work simultaneously
- Handoffs automated via interface contracts
- Coordinator monitors and reports

**IF.TTT:**
- Every agent logs progress
- Trace IDs link related work
- Final verification before completion

---

## To Use This

**Option 1: Use this current session**
Just paste the block above into this chat, and I'll orchestrate everything.

**Option 2: Start fresh session**
Copy `docs/SESSION-STARTERS/MASTER-ORCHESTRATOR-PROMPT.md` into a new Claude Code session.

Want me to start orchestrating right now in this session?
