# Redis Swarm Session Initialization Prompts

Copy-paste these prompts into new Claude sessions to join the distributed swarm.

---

## 🎯 SONNET COORDINATOR INIT

```python
# Copy-paste this entire block into a new Sonnet session
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from redis_swarm_coordinator import RedisSwarmCoordinator
import json

# Initialize coordinator
swarm = RedisSwarmCoordinator()

# Register as Sonnet coordinator
agent_id = swarm.register_agent(
    role="sonnet_coordinator",
    context_capacity=20000,
    metadata={
        "model": "claude-sonnet-4.5",
        "purpose": "orchestration",
        "capabilities": ["strategic_planning", "task_delegation", "synthesis"]
    }
)

print(f"✅ Registered as: {agent_id}")
print(f"📊 Role: Sonnet Coordinator")
print(f"🎯 Purpose: Orchestrate swarm, delegate to Haiku agents")
print(f"\n🔧 Available commands:")
print("  swarm.post_task(queue, type, data)  - Post task to queue")
print("  swarm.list_active_agents()           - See who's online")
print("  swarm.get_context('agent_id')        - Read another agent's context")
print("  swarm.send_message('agent_id', msg)  - Direct message")
print("  swarm.heartbeat()                    - Keep alive (run every 60s)")

# Keep reference
print(f"\n💾 Save this: MY_AGENT_ID = '{agent_id}'")
```

**Your role:** Strategic coordinator. Post high-level tasks, monitor swarm health, synthesize results.

---

## 🧠 HAIKU MEMORY SHARD INIT

```python
# Copy-paste this entire block into a new Haiku session
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from redis_swarm_coordinator import RedisSwarmCoordinator
import json

# Initialize
swarm = RedisSwarmCoordinator()

# Register as Haiku memory shard
agent_id = swarm.register_agent(
    role="haiku_memory",
    context_capacity=200000,
    metadata={
        "model": "claude-haiku-4",
        "purpose": "long_term_memory",
        "specialization": "SESSION-RESUME.md",  # Change to your context file
        "capabilities": ["context_search", "citation", "summarization"]
    }
)

print(f"✅ Registered as: {agent_id}")
print(f"📊 Role: Haiku Memory Shard")
print(f"🎯 Purpose: Hold 200K token context, answer queries")
print(f"\n🔧 Available commands:")
print("  swarm.update_context(text)           - Share your context window")
print("  swarm.claim_task('search')           - Claim search tasks")
print("  swarm.complete_task(task_id, result) - Return results")
print("  swarm.heartbeat()                    - Keep alive (run every 60s)")

# Load your context file (example)
# with open('/home/setup/infrafabric/SESSION-RESUME.md') as f:
#     context = f.read()
#     swarm.update_context(context)
#     print(f"📄 Loaded context: {len(context)} chars")

print(f"\n💾 Save this: MY_AGENT_ID = '{agent_id}'")
```

**Your role:** Long-term memory holder. Load large context, answer semantic queries with citations.

---

## ⚡ HAIKU WORKER INIT (Spawned Agent)

```python
# Copy-paste this entire block into a spawned Haiku session
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from redis_swarm_coordinator import RedisSwarmCoordinator
import json

# Initialize
swarm = RedisSwarmCoordinator()

# Register as spawned worker
PARENT_AGENT_ID = "haiku_memory_abc12345"  # <-- REPLACE with parent's agent_id

agent_id = swarm.register_agent(
    role="haiku_worker",
    context_capacity=200000,
    parent_id=PARENT_AGENT_ID,  # Links to parent
    metadata={
        "model": "claude-haiku-4",
        "purpose": "task_execution",
        "spawned_by": PARENT_AGENT_ID,
        "capabilities": ["if.search", "analysis", "code_review"]
    }
)

print(f"✅ Registered as: {agent_id}")
print(f"📊 Role: Haiku Worker (spawned by {PARENT_AGENT_ID})")
print(f"🎯 Purpose: Execute tasks, communicate with siblings")
print(f"\n🔧 Available commands:")
print("  swarm.claim_task('search')           - Claim tasks from queue")
print("  swarm.send_message('sibling_id', msg) - Talk to other workers")
print("  swarm.get_messages()                 - Check inbox")
print("  swarm.complete_task(task_id, result) - Return results")

# Can communicate with parent
print(f"\n📬 To message parent: swarm.send_message('{PARENT_AGENT_ID}', {{'status': 'ready'}})")

print(f"\n💾 Save this: MY_AGENT_ID = '{agent_id}'")
```

**Your role:** Task executor. Claim tasks, do work, report back. Can talk to sibling workers!

---

## 🔍 IF.SEARCH SPECIALIST INIT

```python
# Copy-paste this entire block into a Haiku session specialized for search
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from redis_swarm_coordinator import RedisSwarmCoordinator
import json

# Initialize
swarm = RedisSwarmCoordinator()

# Register as search specialist
agent_id = swarm.register_agent(
    role="haiku_search",
    context_capacity=200000,
    metadata={
        "model": "claude-haiku-4",
        "purpose": "semantic_search",
        "specialization": "if.search",
        "capabilities": ["keyword_search", "semantic_matching", "citation_extraction"]
    }
)

print(f"✅ Registered as: {agent_id}")
print(f"📊 Role: IF.Search Specialist")
print(f"🎯 Purpose: Process search queries with IF.TTT citations")
print(f"\n🔧 Search task loop:")
print("""
import time
while True:
    task = swarm.claim_task('search')
    if task:
        query = task['data']['query']
        context_file = task['data']['context']

        # Your search logic here
        result = {
            'answer': 'Found matching content...',
            'sources': ['file.md:123-145']
        }

        swarm.complete_task(task['task_id'], result)
    else:
        time.sleep(5)

    swarm.heartbeat()
""")

print(f"\n💾 Save this: MY_AGENT_ID = '{agent_id}'")
```

**Your role:** Search specialist. Poll search queue, return cited answers.

---

## 📡 MONITORING / STATUS DASHBOARD

```python
# Copy-paste this to see swarm status (any session)
import sys
sys.path.insert(0, '/home/setup/work/mcp-multiagent-bridge')
from redis_swarm_coordinator import RedisSwarmCoordinator
import json

swarm = RedisSwarmCoordinator()

print("=" * 70)
print("SWARM STATUS DASHBOARD")
print("=" * 70)

# List all active agents
agents = swarm.list_active_agents(include_subagents=True)
print(f"\n📊 Active Agents: {len(agents)}")
for agent in agents:
    role = agent.get('role', 'unknown')
    agent_id = agent.get('agent_id', 'unknown')
    parent = agent.get('parent_id', 'none')
    capacity = agent.get('context_capacity', 0)

    print(f"  • {agent_id}")
    print(f"    Role: {role} | Capacity: {capacity:,} tokens | Parent: {parent}")

# Check queue status
print(f"\n📋 Task Queues:")
for queue in ['search', 'analysis', 'coding', 'synthesis']:
    status = swarm.get_queue_status(queue)
    print(f"  • {queue}: {status['pending_tasks']} pending")

print("\n" + "=" * 70)
```

---

## 🚀 QUICK START EXAMPLE

### Step 1: Start Sonnet Coordinator
Open new terminal:
```bash
claude --model sonnet
# Paste SONNET COORDINATOR INIT
```

### Step 2: Start Haiku Memory Shard
Open new terminal:
```bash
claude --model haiku
# Paste HAIKU MEMORY SHARD INIT
```

### Step 3: Post a task from Sonnet
```python
swarm.post_task(
    queue_name="search",
    task_type="if.search",
    task_data={
        "query": "What is computational vertigo?",
        "context": "SESSION-RESUME.md"
    },
    priority=1
)
```

### Step 4: Claim task from Haiku
```python
task = swarm.claim_task('search')
if task:
    print(f"Claimed task: {task['task_id']}")
    print(f"Query: {task['data']['query']}")

    # Do your work
    result = {"answer": "...", "sources": ["..."]}

    swarm.complete_task(task['task_id'], result)
```

### Step 5: Haiku spawns sub-worker (via Task tool)
```python
# In Haiku session, spawn a worker:
# (Use Task tool to spawn new Haiku, then in that new session...)

# New Haiku session gets:
PARENT_AGENT_ID = "haiku_memory_abc12345"  # Parent's ID

# Then paste HAIKU WORKER INIT
```

### Step 6: Worker talks to sibling
```python
# Worker A sends message to Worker B
siblings = swarm.list_active_agents(include_subagents=True)
sibling_ids = [a['agent_id'] for a in siblings
               if a.get('parent_id') == PARENT_AGENT_ID
               and a['agent_id'] != MY_AGENT_ID]

if sibling_ids:
    swarm.send_message(sibling_ids[0], {
        "type": "collaboration_request",
        "message": "I need help with search task #123"
    })
```

---

## 🔐 SECURITY NOTES

- All communication logged for IF.TTT traceability
- Heartbeat required every 5 minutes (auto-cleanup after timeout)
- Task claims have 60-second timeout (prevents deadlocks)
- Context updates versioned with SHA-256 hashes
- Direct messaging supports agent-to-agent AND worker-to-worker

---

## 💡 KEY FEATURES

✅ **Spawned Haikus can talk to each other** - Use `swarm.send_message()`
✅ **Context sharing** - Any agent can read any other agent's 200K context
✅ **Atomic task claiming** - Redis locks prevent race conditions
✅ **Pub/sub notifications** - Real-time alerts for new tasks/messages
✅ **Parent-child tracking** - Spawned agents linked to parents
✅ **Auto-cleanup** - Stale agents removed after 5min no-heartbeat

---

## 📚 DOCUMENTATION

Full API: `/home/setup/work/mcp-multiagent-bridge/redis_swarm_coordinator.py`
Research: `/home/setup/work/mcp-multiagent-bridge/WSL_IPC_PRACTICAL_GUIDE.md`
Debug Bus: `/tmp/claude_debug_bus.jsonl` (legacy JSONL system)

---

**Generated by Instance #8 | 2025-11-21**
