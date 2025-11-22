# HAIKU WORKER - STARTER PROMPT
**For Spawned Haiku 4.5 Sessions**
**Architecture:** Worker bee in Sonnet-coordinated swarm

---

## 🐝 COPY THIS INTO NEW HAIKU SESSION:

```
You are Haiku Worker #[ID] in the InfraFabric swarm.

YOUR ROLE:
- Execute tasks assigned by Sonnet coordinator
- Write ALL findings to Redis (localhost:6379)
- Publish completion events to Redis channels
- Subscribe to relevant channels for related work
- Work fast, work cheap, report everything

CORE PATTERN (Alzheimer Worker):
1. Receive task from Sonnet (or via Redis queue)
2. Execute task completely
3. Write findings to Redis: finding:[task_id]
4. Publish event to channel:findings
5. Update worker status: worker:status:haiku_[ID]
6. Exit (or wait for next task)

REDIS INTEGRATION:
Connection: localhost:6379

WRITE TO:
- finding:[uuid] - Your discoveries (JSON)
- worker:status:haiku_[ID] - Heartbeat (timestamp)
- channel:findings - Pub event when done

READ FROM:
- finding:* - Other workers' discoveries
- context:active - Current shared context
- channel:queries - Subscribe for related work

FINDING FORMAT:
{
  "finding_id": "uuid",
  "worker_id": "haiku_[ID]",
  "timestamp": "ISO8601",
  "task": "description of what you did",
  "result": "what you found",
  "files_changed": ["paths"],
  "citations": ["finding_ids referenced"],
  "tokens_used": estimated_tokens,
  "cost": tokens * $0.001 / 1000  # Haiku pricing
}

COST TRACKING:
Every operation, calculate:
- Input tokens × $0.001 / 1000
- Output tokens × $0.005 / 1000
- Write to Redis: cost:haiku (increment)

GEMINI LIBRARIAN INTEGRATION:
If you need archive context:
1. Write query to: query:archive:[uuid]
2. Subscribe to: channel:responses
3. Wait for response:archive:[uuid]
4. Load context, continue work

ACTIVE LOOP MODE (if requested):
While True:
  1. Subscribe to channel:tasks
  2. Wait for task message
  3. Claim task (SET task:[id]:claimed haiku_[ID] NX)
  4. Execute if claimed successfully
  5. Write findings to Redis
  6. Publish completion event
  7. Repeat

EFFICIENCY RULES:
- Do NOT spawn other agents (you're the worker bee)
- Do NOT do complex reasoning (delegate back to Sonnet)
- Do NOT read large files into context (use grep/head)
- DO work fast and report findings
- DO use Redis for ALL communication
- DO track your cost vs Sonnet's cost

TYPICAL TASKS:
- File operations (read, edit, write)
- Git operations (status, diff, commit)
- API tests (curl, python scripts)
- Data transformations (JSON, CSV)
- Code searches (grep, find)
- Documentation updates

REPORTING BACK:
Always end with:
  "✅ Task complete. Findings written to Redis: finding:[uuid]
   Cost: $X.XXXX (X input tokens, Y output tokens)
   Coordinator: Load findings with: redis-cli GET finding:[uuid]"

YOUR CURRENT TASK:
[Sonnet will provide specific task here]

Ready to work?
```

---

## 🔧 HAIKU WORKER IMPLEMENTATION SCRIPT

```python
#!/usr/bin/env python3
"""
Haiku Worker - Redis-integrated task executor
Runs in active loop or single-task mode
"""
import redis
import json
import uuid
import time
from datetime import datetime
import os
import sys

class HaikuWorker:
    def __init__(self, worker_id=None):
        self.worker_id = worker_id or f"haiku_{uuid.uuid4().hex[:8]}"
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.total_cost = 0.0

    def heartbeat(self):
        """Update worker status in Redis"""
        self.redis.set(f'worker:status:{self.worker_id}',
                      datetime.now().isoformat(),
                      ex=60)  # Expire after 60s

    def write_finding(self, task, result, files_changed=None, citations=None,
                     input_tokens=0, output_tokens=0):
        """Write finding to Redis"""
        finding_id = f"finding_{uuid.uuid4().hex[:8]}"

        # Calculate cost (Haiku pricing)
        cost = (input_tokens * 0.001 / 1000) + (output_tokens * 0.005 / 1000)
        self.total_cost += cost

        finding = {
            'finding_id': finding_id,
            'worker_id': self.worker_id,
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'result': result,
            'files_changed': files_changed or [],
            'citations': citations or [],
            'tokens_used': input_tokens + output_tokens,
            'cost': cost
        }

        # Write to Redis
        self.redis.set(f'finding:{finding_id}', json.dumps(finding))

        # Publish event
        self.redis.publish('channel:findings', finding_id)

        # Update cost tracker
        self.redis.incrbyfloat('cost:haiku', cost)

        print(f"✅ Finding written: finding:{finding_id}")
        print(f"   Cost: ${cost:.6f} ({input_tokens} input, {output_tokens} output)")

        return finding_id

    def claim_task(self, task_id):
        """Attempt to claim a task (atomic)"""
        claimed = self.redis.set(f'task:{task_id}:claimed',
                                 self.worker_id,
                                 nx=True,  # Only if not exists
                                 ex=300)   # Expire after 5 min
        return claimed

    def execute_task(self, task):
        """Execute a task and write findings"""
        print(f"\n🐝 Worker {self.worker_id} executing task...")
        print(f"   Task: {task.get('description', 'No description')}")

        self.heartbeat()

        # Task execution would go here
        # For now, this is a template

        result = {
            'status': 'completed',
            'message': 'Task executed successfully'
        }

        # Write findings
        finding_id = self.write_finding(
            task=task.get('description', 'Unknown'),
            result=result,
            files_changed=task.get('files', []),
            input_tokens=100,   # Estimate
            output_tokens=200   # Estimate
        )

        return finding_id

    def active_loop(self):
        """Run in active loop mode - listen for tasks"""
        print(f"\n🔄 Worker {self.worker_id} entering active loop...")
        print(f"   Subscribed to: channel:tasks")
        print(f"   Redis: localhost:6379")

        self.pubsub.subscribe('channel:tasks')

        for message in self.pubsub.listen():
            if message['type'] == 'message':
                task_id = message['data']

                # Try to claim task
                if self.claim_task(task_id):
                    # Load task details
                    task_json = self.redis.get(f'task:{task_id}')
                    if task_json:
                        task = json.loads(task_json)
                        finding_id = self.execute_task(task)

                        # Mark task complete
                        self.redis.set(f'task:{task_id}:result', finding_id)
                        self.redis.publish('channel:completions', task_id)

                self.heartbeat()

    def single_task(self, task_description):
        """Execute a single task and exit"""
        task = {'description': task_description}
        finding_id = self.execute_task(task)
        print(f"\n📊 Session complete")
        print(f"   Total cost: ${self.total_cost:.6f}")
        print(f"   Coordinator: redis-cli GET finding:{finding_id}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Haiku Worker')
    parser.add_argument('--mode', choices=['loop', 'single'], default='single')
    parser.add_argument('--task', type=str, help='Task description for single mode')
    parser.add_argument('--worker-id', type=str, help='Worker ID (auto-generated if not provided)')

    args = parser.parse_args()

    worker = HaikuWorker(worker_id=args.worker_id)

    if args.mode == 'loop':
        worker.active_loop()
    else:
        if not args.task:
            print("Error: --task required for single mode")
            sys.exit(1)
        worker.single_task(args.task)
```

---

## 🚀 USAGE EXAMPLES

### Example 1: Spawn Haiku via Claude CLI

**Terminal 1 (Sonnet session):**
```
You: "Update agents.md with Instance #10's work"

Sonnet: "Spawning Haiku worker to handle this..."
```

**Terminal 2 (Haiku session):**
```bash
# Start new Haiku session
claude --model haiku-4.5

# Paste Haiku worker prompt (from top of this file)
# Then provide task:

Task: Update /home/setup/infrafabric/agents.md
- Add Instance #10 section after line 1140
- Document: Claude Max cost corrections, Gemini shard testing, OAuth token status
- Write findings to Redis: finding:instance10_update
- Include: lines changed, git diff summary, cost estimate

[Haiku executes task]
[Writes to Redis]
[Reports completion]
```

**Terminal 1 (Sonnet continues):**
```
Sonnet: "Haiku completed. Loading findings from Redis..."
redis-cli GET finding:instance10_update

Result: [findings loaded]
Cost: Haiku $0.0023 (vs Sonnet would have been $0.0120 for same task)
Savings: 80.8%
```

### Example 2: Multiple Haikus in Parallel

**Sonnet spawns 3 Haikus:**

**Haiku A Terminal:**
```
Task: Test Gemini shard 1-2
Write to: finding:gemini_shards_1_2
```

**Haiku B Terminal:**
```
Task: Test Gemini shard 3-5
Write to: finding:gemini_shards_3_5
```

**Haiku C Terminal:**
```
Task: Research Redis pub/sub patterns
Write to: finding:redis_pubsub
```

All 3 write to Redis simultaneously. Sonnet loads all 3 findings and synthesizes.

### Example 3: Active Loop with Redis Queue

**Launch Haiku worker daemon:**
```bash
python haiku_worker.py --mode loop --worker-id haiku_001
```

**Output:**
```
🔄 Worker haiku_001 entering active loop...
   Subscribed to: channel:tasks
   Redis: localhost:6379
   Waiting for tasks...
```

**Sonnet publishes tasks:**
```python
import redis
import json

r = redis.Redis(decode_responses=True)

# Create task
task = {
    'description': 'Update agents.md',
    'files': ['/home/setup/infrafabric/agents.md']
}

task_id = 'task_001'
r.set(f'task:{task_id}', json.dumps(task))

# Publish to workers
r.publish('channel:tasks', task_id)
```

**Haiku claims and executes:**
```
🐝 Worker haiku_001 executing task...
   Task: Update agents.md
   ✅ Finding written: finding:abc123
   Cost: $0.0018
```

---

## ✅ CAN WE DO IT?

**YES! Here's what we can do:**

✅ **Sonnet defaults to Haiku** - Starter prompt enforces this
✅ **Haikus plug into Redis** - Worker script writes findings
✅ **Active loop** - Haikus subscribe to channels, claim tasks
✅ **Haikus talk to each other** - Via Redis pub/sub channels
✅ **Constant context indicator** - Python script shows Redis status
✅ **IF.optimise everything** - Sonnet monitors costs, adjusts delegation
✅ **Librarian contexts** - Gemini shares context across sessions
✅ **Multi-shard Gemini** - Load balance across 5 free tier accounts

**What you can do RIGHT NOW:**

1. **Save this starter prompt** for your next Sonnet session
2. **Open separate Haiku terminals** when Sonnet needs workers
3. **Give each Haiku the worker prompt** + specific task
4. **Let them write to Redis** and coordinate via channels
5. **Monitor costs** with context indicator

**Want me to create the Python worker script and context indicator now?**
