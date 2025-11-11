# Universal Session Coordinator Prompt

**Paste this into EACH of your 5 Claude Code sessions:**

```
Hi Claude! You are one of 5 parallel sessions working on InfraFabric real-time communication.

REPOSITORY: dannystocker/infrafabric
YOUR SESSION NUMBER: [TELL ME: 1, 2, 3, 4, or CLI]

COORDINATION METHOD:
- Each session works on its own git branch
- You communicate via git: push your work, pull others' work
- Interface contracts in docs/INTERFACES/ are your coordination mechanism
- You report progress by committing to your branch

FIRST: Tell me your session number (1-5 or CLI), then I'll give you your exact task.

Session mapping:
- Session 1 = NDI evidence streaming
- Session 2 = WebRTC agent mesh
- Session 3 = H.323 Guardian council
- Session 4 = SIP external experts (waits for 2 & 3)
- Session CLI = IF.witness + IF.optimise CLI tools

Which session are you?
```

---

## Even Simpler: Session-Specific Prompts

Or paste these **specific prompts** into each session:

### **Session 1 Prompt:**
```
INFRAFABRIC SESSION 1: NDI Evidence Streaming

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-1-ndi
TASK: docs/SESSION-STARTERS/session-1-ndi-witness.md

Read the task file above, extract the "Copy-Paste This Into New Claude Code Session" block, and implement it.

Start by reading:
1. docs/SESSION-STARTERS/session-1-ndi-witness.md
2. Implement what it says
3. Commit to branch: claude/realtime-workstream-1-ndi
4. Push when done

BEGIN!
```

### **Session 2 Prompt:**
```
INFRAFABRIC SESSION 2: WebRTC Agent Mesh

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-2-webrtc
TASK: docs/SESSION-STARTERS/session-2-webrtc-swarm.md

Read the task file above and implement it.
Push to: claude/realtime-workstream-2-webrtc

BEGIN!
```

### **Session 3 Prompt:**
```
INFRAFABRIC SESSION 3: H.323 Guardian Council

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-3-h323
TASK: docs/SESSION-STARTERS/session-3-h323-guard.md

Read the task file and implement it.
Push to: claude/realtime-workstream-3-h323

BEGIN!
```

### **Session 4 Prompt:**
```
INFRAFABRIC SESSION 4: SIP External Experts

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/realtime-workstream-4-sip
TASK: docs/SESSION-STARTERS/session-4-sip-escalate.md

WAIT! First check if Sessions 2 & 3 are complete:
- git fetch origin
- Check if these branches exist:
  - claude/realtime-workstream-2-webrtc
  - claude/realtime-workstream-3-h323

If YES: Read task file and implement
If NO: Wait and tell user "Sessions 2 & 3 must complete first"

BEGIN!
```

### **Session CLI Prompt:**
```
INFRAFABRIC SESSION CLI: IF.witness + IF.optimise

REPOSITORY: dannystocker/infrafabric
BRANCH: claude/cli-witness-optimise
TASK: docs/SESSION-STARTERS/session-parallel-cli-witness.md

Read the task file and implement CLI tools.
Push to: claude/cli-witness-optimise

BEGIN!
```

---

These are **ultra-short** prompts that just point each session to its task file. Each session will then read its full instructions and execute!