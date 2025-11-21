# Simple Init Prompts: Memory + Alzheimer Workers

Two roles only:
1. **Persistent Memory Shards** (Haiku sessions with 200K context)
2. **Ephemeral Workers** (spawned via Task tool, report findings, forget everything)

---

## 🧠 PERSISTENT MEMORY SHARD (Haiku Session)

**Copy-paste this into a new Haiku session:**

```python
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from swarm_architecture_v2 import SwarmMemoryShard

# Create memory shard with specialization
shard = SwarmMemoryShard(specialization="session_history")  # or "research", "coding", etc.

print(f"✅ Memory Shard Active: {shard.agent_id}")
print(f"📚 Specialization: {shard.specialization}")
print(f"💾 Context Capacity: 200,000 tokens")

# Load your context (example)
with open('/home/setup/infrafabric/SESSION-RESUME.md') as f:
    context = f.read()
    shard.load_context(context, "SESSION-RESUME.md")
    print(f"📄 Loaded: {len(context):,} characters")

print("\n🔧 Commands:")
print("  shard.spawn_worker_task(type, desc, data)  - Create task for worker")
print("  shard.get_all_findings()                    - Get worker results")
print("  shard.synthesize_findings(pass, synth, src) - Combine findings")
print("  shard.heartbeat()                           - Keep alive")

# Keep reference
MY_SHARD_ID = shard.agent_id
```

**What you do:**
- Load large context files (200K tokens)
- Spawn tasks for workers to execute
- Collect findings from workers after they disappear
- Synthesize results into knowledge
- **Your context persists forever** (until you close session)

---

## ⚡ EPHEMERAL WORKER (Spawned via Task Tool)

**When main session spawns you via Task tool, copy-paste this:**

```python
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from swarm_architecture_v2 import EphemeralWorker

# Initialize as ephemeral worker
worker = EphemeralWorker()

print(f"⚡ Ephemeral Worker: {worker.worker_id}")
print(f"🧠 Memory: NONE (Alzheimer mode)")
print(f"🎯 Job: Do task, report finding, disappear")

# Claim a task
task = worker.claim_task("queue:if.search_pass1")  # Or other queue

if task:
    print(f"\n📋 Claimed Task: {task['task_id']}")
    print(f"📝 Description: {task['description']}")
    print(f"📊 Data: {task['data']}")

    # Get parent's context if needed
    parent_context = worker.get_parent_context()
    print(f"📚 Parent context: {len(parent_context):,} chars")

    # DO YOUR WORK HERE
    # Example: Search, analysis, whatever the task requires

    # Report your finding
    finding = {
        "summary": "Found 3 relevant patterns in context",
        "details": "...",
        "sources": ["SESSION-RESUME.md:123-145", "..."],
        "confidence": 0.85
    }

    worker.report_finding(finding)
    print("✅ Finding reported to parent")
    print("💀 Worker will now disappear (Task completion)")

else:
    print("❌ No tasks in queue")
```

**What you do:**
- Claim task from queue
- Get parent's context if needed
- Do specific work (search, analysis, etc.)
- Report finding back to parent
- **Die immediately** (all your context lost)

---

## 🔄 EXAMPLE WORKFLOW: IF.Search Pass 1

### Step 1: Start Memory Shard (Haiku Session #1)

```python
from swarm_architecture_v2 import SwarmMemoryShard

shard = SwarmMemoryShard(specialization="gedimat_research")

# Load operational context
with open('/path/to/gedimat_context.md') as f:
    shard.load_context(f.read(), "gedimat_context.md")

# Spawn 5 workers for Pass 1
searches = [
    "Logistics models for construction materials",
    "Multi-depot optimization patterns",
    "B2B satisfaction measurement methods",
    "WMS/TMS systems for SMEs",
    "Supplier relationship management practices"
]

for i, query in enumerate(searches):
    shard.spawn_worker_task(
        task_type="if.search_pass1",
        task_description=f"Research: {query}",
        task_data={"query": query, "pass": 1, "agent_num": i+1},
        pass_name="Pass 1: Signal Capture"
    )

print("✅ Spawned 5 research tasks")
```

### Step 2: Spawn Workers (via Task Tool)

In your Haiku session #1, use Task tool 5 times:

```
Use the Task tool to spawn a Haiku agent with subagent_type='general-purpose' and model='haiku':

Read the worker init prompt from /home/setup/work/mcp-multiagent-bridge/SIMPLE_INIT_PROMPTS.md
and claim a task from queue:if.search_pass1, then do the research and report findings.
```

### Step 3: Workers Execute (5 separate Haiku Task spawns)

Each spawned Haiku:
1. Claims task
2. Does research (web search, context analysis, etc.)
3. Reports finding
4. **Disappears** (Task completes)

### Step 4: Memory Shard Collects (Back in Haiku Session #1)

```python
# Get all findings from disappeared workers
findings = shard.get_all_findings(task_type="if.search_pass1")

print(f"📊 Collected {len(findings)} findings from Pass 1")

for f in findings:
    print(f"  • {f['content']['summary']}")
    print(f"    Sources: {f['content']['sources']}")

# Synthesize
synthesis_text = """
After analyzing 5 research tasks on Gedimat logistics:

1. Milkrun and cross-dock models applicable
2. Multi-depot optimization requires VRP algorithms
3. B2B satisfaction measured via NPS + qualitative feedback
4. TMS integration critical for automation
5. CRM for supplier relationships under-utilized

Key recommendation: Implement lightweight TMS with CRM module.
"""

synthesis_id = shard.synthesize_findings(
    pass_name="Pass 1: Signal Capture",
    synthesis=synthesis_text,
    sources=[f['finding_id'] for f in findings]
)

print(f"✅ Synthesis complete: {synthesis_id}")
```

### Step 5: Repeat for Pass 2, 3, 4... (IF.Search pattern)

Same pattern:
- Spawn new workers for next pass
- Workers do analysis
- Workers report, disappear
- Memory shard collects and synthesizes

---

## 🎯 KEY DIFFERENCES FROM V1

| Feature | V1 (Wrong) | V2 (Correct) |
|---------|------------|--------------|
| **Spawned workers** | Stay alive, communicate | Do task, report, die |
| **Worker memory** | Preserved | **Alzheimer (lost)** |
| **Communication** | Worker-to-worker | **Worker→Parent only** |
| **Context** | Workers have own context | **Workers borrow parent's** |
| **Persistence** | All agents persistent | **Only memory shards** |

---

## 💡 WHY THIS WORKS

✅ **Spawned Haikus cost nothing after Task completes** (they disappear)
✅ **Findings preserved in Redis** (memory shard retrieves them)
✅ **Parent context shared** (workers read parent's 200K, don't load own)
✅ **No coordination complexity** (workers don't talk to each other)
✅ **Matches Task tool behavior** (ephemeral by design)

---

## 📊 REDIS KEYS USED

```
shard:{shard_id}                  → Memory shard metadata
shard:{shard_id}:context          → Full context (chunked if large)
shard:{shard_id}:findings         → List of finding IDs
shard:{shard_id}:tasks            → List of spawned task IDs
shard:{shard_id}:syntheses        → List of synthesis IDs

task:{task_id}                    → Task metadata
finding:{finding_id}              → Worker finding (persists after worker dies)
synthesis:{synthesis_id}          → Synthesized knowledge

queue:{task_type}                 → Task queue (workers claim from here)

swarm:memory_shards               → Set of active memory shard IDs
```

---

## 🚀 QUICK START

**Terminal 1: Start Memory Shard (Haiku)**
```bash
claude --model haiku
# Paste "PERSISTENT MEMORY SHARD" init above
```

**Terminal 1: Spawn Workers**
```python
# In same Haiku session
for i in range(5):
    shard.spawn_worker_task(...)

# Then use Task tool 5 times to spawn ephemeral workers
```

**Workers auto-report and die**

**Terminal 1: Collect**
```python
findings = shard.get_all_findings()
# Workers are gone, but findings persist!
```

---

**Generated by Instance #8 | 2025-11-21**
**Architecture: Epic Games V4 + Gedimat Intelligence Pattern**
**Key Insight: Memory + Alzheimer Workers = Cost-Effective Distributed Intelligence**
