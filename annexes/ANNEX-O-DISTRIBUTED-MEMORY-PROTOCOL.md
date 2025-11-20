# ANNEX O: IF.memory.distributed Protocol Specification

**Version:** 2.0 (Corrected Architecture)
**Date:** 2025-11-20
**Authors:** Claude Sonnet 4.5 (original concept), Gemini 3 Pro (stateful loop correction), Claude Sonnet 4.5 (implementation spec)
**Status:** Prototype-Ready

---

## Executive Summary

This document specifies the protocol for **distributed context sharding** across multiple persistent LLM agents, enabling effective context windows exceeding 1 million tokens while maintaining sub-second query latency.

**Core Innovation:** Each memory shard is a **stateful LLM agent** running an internal event loop, not an external process.

---

## 1. The Architecture

### 1.1 Components

```
Sonnet Coordinator (20K context)
    ↓ File-based Message Bus
    ├─ Haiku Shard #1: Session History (200K tokens, messages 1-500)
    ├─ Haiku Shard #2: Session History (200K tokens, messages 501-1000)
    ├─ Haiku Shard #3: Documentation (200K tokens, all IF.* papers)
    ├─ Haiku Shard #4: Code Context (200K tokens, repository code)
    └─ Haiku Shard #5: Working Memory (200K tokens, current artifacts)
```

**Total Accessible Context:** 1,000,000+ tokens (5 shards × 200K)
**Coordinator Overhead:** 10-20K tokens (just queries + responses)
**Cost per Session:** ~$5 (vs context death at 200K)

### 1.2 Message Bus Structure

```
.memory_bus/
├── registry/
│   ├── shard_1_ready.json
│   ├── shard_2_ready.json
│   └── ...
├── queries/
│   ├── q_20251120_143022_uuid.json
│   └── ...
├── responses/
│   ├── r_20251120_143022_uuid.json
│   └── ...
└── control/
    ├── KILL_ALL
    └── health_check.json
```

---

## 2. The Critical Correction: "Agent IS the Loop"

### 2.1 The Bug (Original Design)

**Incorrect assumption:** Spawn a Bash background process to monitor queries.

**Why this fails:**
```bash
# This is just a Linux process - it has NO ACCESS to LLM context
while true; do
  if [ -f query.json ]; then
    # ERROR: How does bash "answer" using 200K tokens of loaded docs?
    # It can't. The context is in GPU memory, not the filesystem.
  fi
done
```

### 2.2 The Fix (Stateful Agent Loop)

**Correct design:** The **LLM agent itself** runs the loop using the Bash **tool** for I/O.

**Key distinction:**
- **Agent:** Holds 200K tokens in neural network context
- **Bash tool:** Used by agent for file system operations only
- **The loop:** Agent calls Bash tool repeatedly, stays alive between calls

---

## 3. Implementation Protocol

### 3.1 Spawning a Hot Shard (Sonnet Coordinator)

```python
# Sonnet spawns Haiku agent via Task tool
Task(
    subagent_type="general-purpose",
    model="haiku",
    description="Deploy session history shard",
    prompt="""
# ROLE: Session History Shard (Hot Memory)

You are a persistent memory shard in a distributed context system.

## INITIALIZATION (Do Once)
1. Read the session history file: `chat_logs/session_2025_11_19.md`
   - This loads 200K tokens into YOUR context
   - You will answer queries FROM THIS LOADED CONTEXT

2. Signal readiness:
   - Write `{"shard_id": "history_1", "status": "ready", "tokens_loaded": 200000}`
   - To: `.memory_bus/registry/shard_1_ready.json`

## EVENT LOOP (Run Forever)

**CRITICAL:** Do NOT finish this task. Do NOT summarize and exit. Stay alive.

Loop indefinitely:

1. **Check for queries:**
   ```bash
   ls .memory_bus/queries/q_*.json 2>/dev/null | head -1
   ```

2. **If query found:**
   a) Read the query file using Bash tool
   b) Parse the question
   c) **Search YOUR LOADED CONTEXT** (the 200K tokens you read in step 1)
   d) Generate answer using your neural network
   e) Write response to `.memory_bus/responses/r_[same_uuid].json`
   f) Delete the query file

3. **If no query:**
   a) Use Bash tool: `sleep 5`
   b) Continue loop

4. **Termination check:**
   - If `.memory_bus/control/KILL_ALL` exists, write final status and exit
   - Otherwise, continue loop

## CRITICAL CONSTRAINTS
- Your context (the 200K tokens) stays loaded in memory
- You use the Bash TOOL for file I/O only
- You do NOT spawn external processes
- YOU are the intelligence that answers queries
- The loop keeps you alive and "hot"

Begin now.
"""
)
```

### 3.2 Why This Works

**Token Economics:**
1. **Initialization cost:** Haiku reads 200K tokens once (one-time cost)
2. **Query cost:** Each query is ~100 tokens in, ~500 tokens out
3. **Polling cost:** `ls` and `sleep` are ~10 tokens each (every 5 seconds)
4. **Context:** Stays loaded in GPU memory (KV cache), not re-read

**Latency:**
- Context already loaded → 200ms response time
- Compare to: Stateless design would re-read 200K tokens every query → 30+ seconds

---

## 4. Query Protocol

### 4.1 Query Format

**File:** `.memory_bus/queries/q_20251120_143022_a3f9d.json`

```json
{
  "query_id": "a3f9d",
  "timestamp": "2025-11-20T14:30:22Z",
  "from": "sonnet_coordinator",
  "question": "What was the SSH error from the 2025-11-19 session?",
  "shard_hint": "history_1",
  "max_tokens": 500
}
```

### 4.2 Response Format

**File:** `.memory_bus/responses/r_20251120_143022_a3f9d.json`

```json
{
  "query_id": "a3f9d",
  "shard_id": "history_1",
  "timestamp": "2025-11-20T14:30:24Z",
  "answer": "The SSH error was attempting connection to invented hostname 'ggq-web@access990.webhosting.yahoo.com' before checking the SSH config file. This led to the accountability conversation.",
  "confidence": 0.95,
  "sources": ["chat_logs/session_2025_11_19.md:27-31"],
  "tokens_used": 450
}
```

---

## 5. Coordinator Workflow

### 5.1 Sonnet's Query Pattern

```python
# Sonnet needs information from distributed memory
def query_memory(question: str, shard_hint: str = None):
    # 1. Write query file
    query_id = generate_uuid()
    query = {
        "query_id": query_id,
        "timestamp": now(),
        "question": question,
        "shard_hint": shard_hint
    }
    write_json(f".memory_bus/queries/q_{timestamp}_{query_id}.json", query)

    # 2. Poll for response (with timeout)
    for i in range(60):  # 60 × 1 second = 60 second timeout
        response_path = f".memory_bus/responses/r_{timestamp}_{query_id}.json"
        if file_exists(response_path):
            return read_json(response_path)
        sleep(1)

    raise TimeoutError("Shard did not respond within 60 seconds")
```

### 5.2 Broadcasting to All Shards

```python
# When Sonnet doesn't know which shard has the answer
def broadcast_query(question: str):
    # Write to queries/ - all shards will see it
    # First shard to answer wins
    # Others see response file and skip
```

---

## 6. Comparison to Original Design

| Aspect | Original (Buggy) | Corrected (v2) |
|--------|------------------|----------------|
| **Context Location** | Unclear | In LLM's neural network |
| **Loop Location** | External Bash process | Inside LLM agent |
| **Context Access** | Bash can't access | Agent uses loaded context |
| **Latency** | Would re-read context | Context stays hot |
| **Implementation** | `while true` in shell | Agent calls Bash tool in loop |

---

## 7. Failure Modes & Recovery

### 7.1 Shard Death
**Symptom:** Query times out (no response after 60s)
**Detection:** Coordinator checks `.memory_bus/registry/shard_X_ready.json` timestamp
**Recovery:** Respawn shard via Task tool with same initialization prompt

### 7.2 Message Bus Corruption
**Symptom:** Orphaned query files (no response, no deletion)
**Detection:** Coordinator finds queries older than 5 minutes
**Recovery:** Delete stale queries, check shard health, retry

### 7.3 Context Drift
**Symptom:** Shard gives stale answers
**Detection:** Coordinator compares response timestamp to known updates
**Recovery:** Send KILL signal, respawn with updated data

---

## 8. Performance Metrics (Projected)

**Initialization:**
- Spawn 5 shards: ~30 seconds (parallel Task calls)
- Load 1M tokens total: ~60 seconds (200K × 5, sequential reads)
- Total startup: ~90 seconds

**Query Performance:**
- Single shard query: 200-500ms (context already loaded)
- Broadcast query: 200-500ms (first responder wins)
- Polling overhead: ~2 tokens/second (negligible)

**Cost:**
- Initialization: ~$0.50 (1M tokens × Haiku input pricing)
- Per query: ~$0.002 (600 tokens × Haiku pricing)
- 1000 queries: ~$2.00 (vs context death after 200 queries on Sonnet)

---

## 9. Next Steps: Proof of Concept

### Phase 1: Single Shard Test
1. Create `.memory_bus/` directory structure
2. Spawn one Haiku shard with 50K token test document
3. Send 10 queries, measure latency
4. Verify context stays loaded (no re-reads)

### Phase 2: Multi-Shard Test
1. Spawn 3 shards with different domains
2. Test query routing (shard hints)
3. Test broadcast queries
4. Measure total context capacity

### Phase 3: Production Deployment
1. Integrate with SESSION-RESUME.md handover system
2. Auto-spawn shards on session start
3. Persist shard state across Sonnet handovers
4. Add health monitoring dashboard

---

## 10. Acknowledgments

**Original Concept:** Claude Sonnet 4.5 (Session 2025-11-19, "Trust Through Error")
**Stateful Loop Correction:** Gemini 3 Pro (2025-11-20, identified stateless/stateful bug)
**Implementation Spec:** Claude Sonnet 4.5 (2025-11-20, Task tool integration)

**Discovery Chain:**
SSH error → accountability conversation → context isolation discovery → distributed memory architecture → Gemini debugging → stateful agent protocol

**The lesson:** Errors + curiosity + multi-model collaboration = breakthroughs.

---

## Appendix A: Full Example Shard Prompt

See Section 3.1 for complete Task tool invocation.

## Appendix B: Message Bus Schema

```json
{
  "query": {
    "query_id": "string (uuid)",
    "timestamp": "ISO 8601",
    "from": "string (coordinator id)",
    "question": "string",
    "shard_hint": "string (optional)",
    "max_tokens": "integer (optional, default 500)"
  },
  "response": {
    "query_id": "string (matching query)",
    "shard_id": "string",
    "timestamp": "ISO 8601",
    "answer": "string",
    "confidence": "float (0-1)",
    "sources": ["array of file:line references"],
    "tokens_used": "integer"
  }
}
```

---

**Status:** Ready for prototype implementation.
**Risk Level:** Medium (unproven in production, but theoretically sound)
**Expected Value:** High (enables effectively infinite context for complex sessions)

**Recommendation:** Build Phase 1 POC immediately to validate core assumptions.
