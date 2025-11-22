# IF.OPTIMISE × IF.SEARCH × IF.SWARM
**Complete Workflow: Dispatch, Execute, Reassemble, Unblock**
**Date:** 2025-11-21
**Instance:** #10

---

## 🎯 THE THREE-WAY INTERSECTION

```
IF.optimise (Cost/Token Efficiency)
    ∩
IF.search (Distributed Research/Discovery)
    ∩
IF.swarm (Multi-agent Coordination)
    =
Intelligent Work Dispatch with Peer-Assisted Blocker Resolution
```

---

## 📊 COMPLETE WORKFLOW

### Phase 1: WORK DISPATCH (Sonnet → Workers via Redis)

**Trigger:** User asks complex research question

```
User: "Research Gedimat supplier network: logistics, pricing, market positioning"

Sonnet (Coordinator):
  1. IF.optimise analysis:
     - Can I (Sonnet) do this? No - too expensive
     - Can Haiku workers do this? Yes - 3× cheaper
     - Should I use Gemini librarian? Check if already researched

  2. Checks Redis for existing findings:
     redis-cli KEYS "finding:*gedimat*"
     Result: 3 old findings, but not recent supplier data

  3. IF.search decomposition:
     - Break into 8 sub-queries (IF.search passes)
     - Each pass targets different aspect
     - Assign complexity/priority scores

  4. IF.swarm dispatch:
     - Spawn 8 Haiku workers
     - Each gets one IF.search pass
     - Write tasks to Redis queues
```

**Redis Dispatch:**
```python
# Sonnet creates 8 tasks
import redis
import uuid
import json

r = redis.Redis(decode_responses=True)

tasks = [
    {"query": "Gedimat logistics network structure", "priority": "high"},
    {"query": "Gedimat pricing strategy 2024-2025", "priority": "high"},
    {"query": "Gedimat market positioning vs competitors", "priority": "medium"},
    {"query": "Gedimat supplier relationships", "priority": "medium"},
    {"query": "Gedimat regional coverage", "priority": "low"},
    {"query": "Gedimat digital transformation initiatives", "priority": "low"},
    {"query": "Gedimat financial performance Q3-Q4 2024", "priority": "medium"},
    {"query": "Gedimat customer segments and satisfaction", "priority": "low"},
]

for i, task_data in enumerate(tasks):
    task_id = f"task_{uuid.uuid4().hex[:8]}"

    task = {
        "task_id": task_id,
        "task_type": "if.search_pass1",
        "query": task_data["query"],
        "priority": task_data["priority"],
        "context": "gedimat_research",
        "timestamp": datetime.utcnow().isoformat(),
        "assigned_to": None  # Unclaimed
    }

    # Write task to Redis
    r.set(f"task:{task_id}", json.dumps(task), ex=3600)  # 1 hour TTL

    # Add to priority queue
    r.rpush(f"queue:tasks_{task_data['priority']}", task_id)

    # Publish notification
    r.publish("channel:tasks", task_id)

print(f"✅ Dispatched {len(tasks)} tasks to swarm")
print(f"   High priority: 2 tasks")
print(f"   Medium priority: 3 tasks")
print(f"   Low priority: 3 tasks")

# Sonnet updates cost tracker
sonnet_cost = 0.0025  # Cost to analyze and dispatch
r.incrbyfloat("cost:sonnet", sonnet_cost)
```

**Sonnet Output:**
```
📊 SWARM STATUS (Pre-dispatch)
Redis Context:    3 findings, ~300 tokens
Active Workers:   0 Haikus
Tasks Queued:     0

🚀 DISPATCHING WORK...
   Breaking question into 8 IF.search passes
   Spawning 8 Haiku workers
   Priority: 2 high, 3 medium, 3 low

📊 SWARM STATUS (Post-dispatch)
Redis Context:    3 findings, ~300 tokens
Active Workers:   0 Haikus (8 tasks queued)
Tasks Queued:     8
Cost: Sonnet $0.0025 (dispatch overhead)

Waiting for workers to claim tasks...
```

---

### Phase 2: WORK CLAIMING (Workers via Redis)

**8 Haiku terminals open (user spawns or automated):**

**Haiku Worker 1:**
```python
import redis

class HaikuWorker:
    def claim_task(self):
        """Claim highest priority task available"""
        # Try high → medium → low
        for priority in ["high", "medium", "low"]:
            queue = f"queue:tasks_{priority}"
            task_id = self.redis.lpop(queue)  # Atomic claim

            if task_id:
                # Lock task
                if self.redis.set(f"task:{task_id}:claimed",
                                 self.worker_id,
                                 nx=True,  # Only if not exists
                                 ex=300):   # 5 min expiry
                    # Load task details
                    task_json = self.redis.get(f"task:{task_id}")
                    if task_json:
                        task = json.loads(task_json)
                        print(f"✅ Claimed task {task_id} (priority: {priority})")
                        return task

        return None  # No tasks available

worker = HaikuWorker(worker_id="haiku_001")
task = worker.claim_task()

# Output:
# ✅ Claimed task task_a1b2c3d4 (priority: high)
# Query: "Gedimat logistics network structure"
```

**All 8 workers claim simultaneously:**
```
Haiku 1: Claims task_a1b2c3d4 (high)   - Gedimat logistics
Haiku 2: Claims task_e5f6g7h8 (high)   - Gedimat pricing
Haiku 3: Claims task_i9j0k1l2 (medium) - Market positioning
Haiku 4: Claims task_m3n4o5p6 (medium) - Supplier relationships
Haiku 5: Claims task_q7r8s9t0 (medium) - Financial performance
Haiku 6: Claims task_u1v2w3x4 (low)    - Regional coverage
Haiku 7: Claims task_y5z6a7b8 (low)    - Digital transformation
Haiku 8: Claims task_c9d0e1f2 (low)    - Customer segments
```

---

### Phase 3: WORK EXECUTION (Workers with Peer Assist)

**Haiku 1 executes IF.search pass:**

```python
class HaikuWorker:
    def execute_with_assistance(self, task):
        """Execute task with peer assist fallback"""
        try:
            # Execute IF.search pass
            print(f"🔍 Researching: {task['query']}")

            # Search web, databases, documents
            results = self.conduct_research(task['query'])

            # Extract findings
            finding = self.extract_finding(results)

            # Write to Redis
            finding_id = self.write_finding(task, finding)

            return finding_id

        except BlockerEncountered as e:
            # BLOCKER HIT - Use Peer Assist Pattern
            print(f"⚠️  Blocker encountered: {e}")
            return self.request_peer_assistance(task, e)
```

**Example execution (Haiku 1):**
```
🔍 Researching: Gedimat logistics network structure
   Searching web sources...
   Found 12 articles
   Extracting key facts...
   ✅ Finding extracted
   Writing to Redis: finding:gedimat_logistics_a1b2c3d4

📝 Finding Summary:
   - 14 distribution centers across France
   - Hub-and-spoke network model
   - Just-in-time delivery to 500+ stores
   - Partnership with LogisTrans for last-mile

💰 Cost: $0.0018 (450 input tokens, 600 output tokens)
   Updating Redis: cost:haiku += $0.0018
```

---

### Phase 4: BLOCKER ENCOUNTERED (Peer Assist Pattern)

**Haiku 4 hits blocker:**

```python
# Haiku 4 researching "Gedimat supplier relationships"
try:
    results = self.search_supplier_database("gedimat")
except APIRateLimitError as e:
    # API rate limit hit (429 Too Many Requests)
    print(f"❌ BLOCKER: {e}")
    print(f"   Broadcasting help request...")

    # Request peer assistance
    assist_id = self.request_peer_assistance(
        blocked_task=task,
        blocker_type="APIRateLimit",
        blocker_details="supplier API 429 error",
        urgency="high"
    )

    # Wait for peer solution
    solution = self.wait_for_peer_solution(assist_id, timeout=60)
```

**Redis broadcast:**
```python
# Haiku 4 publishes help request
help_request = {
    "assist_id": "assist_x9y8z7",
    "requester": "haiku_004",
    "blocked_task_id": "task_m3n4o5p6",
    "blocker_type": "APIRateLimit",
    "blocker_details": "suppliers.api.com returning 429",
    "query": "Gedimat supplier relationships",
    "urgency": "high",
    "timestamp": "2025-11-21T14:32:15Z"
}

# Write to Redis
r.set("assist_request:assist_x9y8z7", json.dumps(help_request), ex=300)

# Publish to channel
r.publish("help_requests:high", json.dumps(help_request))

# Add to claimable queue
r.rpush("queue:assist_high", "assist_x9y8z7")
```

**3 idle workers see the help request:**

```
Haiku 6 (idle after completing its task): "I can help!"
Haiku 7 (idle after completing its task): "I can help!"
Haiku 8 (idle after completing its task): "I can help!"
```

**Parallel assistance attempts:**

**Haiku 6:**
```python
# Claims assist request
assist = worker.claim_assist_request()
print(f"🆘 Assisting haiku_004 with API rate limit")

# Try backup API endpoint
try:
    results = self.search_backup_api("gedimat suppliers")
    solution = {"source": "backup_api", "data": results}
    worker.publish_solution("assist_x9y8z7", solution)
    print("✅ Solution published: backup API data")
except:
    print("❌ Backup API also failed")
```

**Haiku 7:**
```python
# Claims same assist (parallel attempt)
assist = worker.claim_assist_request()
print(f"🆘 Assisting haiku_004 with API rate limit")

# Check Redis cache
cached_data = self.redis.get("cache:gedimat_suppliers")
if cached_data:
    solution = {"source": "redis_cache", "data": json.loads(cached_data), "age_hours": 6}
    worker.publish_solution("assist_x9y8z7", solution)
    print("✅ Solution published: cached data (6 hours old)")
```

**Haiku 8:**
```python
# Also attempts to help
assist = worker.claim_assist_request()
print(f"🆘 Assisting haiku_004 with API rate limit")

# Search local database mirror
local_data = self.search_local_db("gedimat suppliers")
if local_data:
    solution = {"source": "local_db", "data": local_data}
    worker.publish_solution("assist_x9y8z7", solution)
    print("✅ Solution published: local database")
```

**Haiku 4 receives first solution (Haiku 7's cache):**
```python
# Waiting for solution...
solution = worker.wait_for_peer_solution("assist_x9y8z7", timeout=60)

# Received after 3 seconds!
print(f"✅ Solution received from haiku_007")
print(f"   Source: Redis cache (6 hours old)")
print(f"   Applying solution...")

# Use cached data to complete task
finding = worker.complete_task_with_solution(task, solution)
worker.write_finding(task, finding, note="Used cached data due to API limit")

print("✅ Task unblocked and completed")
print("   Blocker resolution time: 3 seconds (vs 5 min escalation to Sonnet)")
```

**Key: Sonnet was NEVER notified of the blocker!**

---

### Phase 5: FINDINGS ACCUMULATION (Redis)

**As workers complete, findings accumulate:**

```bash
redis-cli KEYS "finding:*"

# Output:
1) "finding:gedimat_logistics_a1b2c3d4"
2) "finding:gedimat_pricing_e5f6g7h8"
3) "finding:gedimat_market_positioning_i9j0k1l2"
4) "finding:gedimat_suppliers_m3n4o5p6"
5) "finding:gedimat_financial_q7r8s9t0"
6) "finding:gedimat_regional_u1v2w3x4"
7) "finding:gedimat_digital_y5z6a7b8"
8) "finding:gedimat_customers_c9d0e1f2"
```

**Context indicator updates in real-time:**
```bash
watch -n 2 'python3 context_indicator.py'

# Every 2 seconds shows:
📊 SWARM STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Redis Context:    11 findings (+8), ~4,200 tokens
Active Workers:   0 Haikus (8 completed tasks)
Librarians:       S1:1498✅ | S2:1500✅ | S3:1500✅ | S4:1500✅ | S5:1500✅
Tasks Queued:     0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cost This Session:
  Sonnet:  $0.0025 (dispatch only)
  Haiku:   $0.0187 (8 workers executed)
  Gemini:  $0.0000
  Total:   $0.0212
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Token Efficiency: ✅
  Haiku:   88.2% (target: 90%+)  ← Almost there!
  Sonnet:  11.8%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Peer Assists: 1 blocker resolved in 3 seconds (0 Sonnet escalations)
```

---

### Phase 6: WORK REASSEMBLY (Sonnet Synthesis)

**Sonnet loads findings from Redis and synthesizes:**

```python
import redis
import json

class SonnetCoordinator:
    def reassemble_findings(self, task_ids):
        """Load and synthesize findings from completed tasks"""
        findings = []

        for task_id in task_ids:
            # Load finding from Redis
            finding_key = self.redis.get(f"task:{task_id}:result")
            if finding_key:
                finding_json = self.redis.get(finding_key)
                if finding_json:
                    findings.append(json.loads(finding_json))

        # Synthesize all findings
        synthesis = self.synthesize(findings)
        return synthesis

sonnet = SonnetCoordinator()
synthesis = sonnet.reassemble_findings(task_ids)
```

**Sonnet synthesis (strategic, high-level):**
```
📋 GEDIMAT RESEARCH SYNTHESIS

I've coordinated 8 Haiku workers to research Gedimat comprehensively. Here's the synthesis:

🏭 LOGISTICS & OPERATIONS
From finding:gedimat_logistics:
  - 14 distribution centers (hub-and-spoke model)
  - 500+ retail stores served
  - Partnership with LogisTrans for last-mile delivery
  - Just-in-time inventory system

💰 PRICING & FINANCIAL
From findings: gedimat_pricing, gedimat_financial:
  - Premium pricing strategy (15% above market average)
  - Q3-Q4 2024: €450M revenue (+8% YoY)
  - Margin pressure from digital competitors
  - Focus on professional/B2B segments (higher margins)

🏆 MARKET POSITIONING
From findings: gedimat_market_positioning, gedimat_suppliers:
  - #3 player in French building materials
  - Differentiation: Expert advice + local service
  - Strong supplier relationships (30-year partnerships)
  - Competing against Leroy Merlin (digital) and Saint-Gobain (scale)

💻 DIGITAL TRANSFORMATION
From finding: gedimat_digital:
  - €12M investment in e-commerce platform (2024)
  - Mobile app for pro customers (quote management)
  - Still 70% in-store sales (vs 40% industry avg)
  - Digital gap = strategic vulnerability

👥 CUSTOMER SEGMENTS
From finding: gedimat_customers:
  - 60% professional contractors
  - 40% DIY/residential
  - NPS score: 72 (professional), 58 (DIY)
  - Customer retention: 89% (professional)

🎯 STRATEGIC INSIGHTS
  1. Gedimat excels at B2B/professional market (pricing power, loyalty)
  2. Digital transformation lagging (risk from pure-play e-commerce)
  3. Logistics network is strength (just-in-time, local coverage)
  4. Supplier relationships = moat (hard to replicate)

📊 SWARM PERFORMANCE
  Cost: $0.0212 total ($0.0025 Sonnet, $0.0187 Haiku)
  If I (Sonnet) did all 8 research passes: $0.0845 (4× more expensive)
  Savings: $0.0633 (75% cost reduction via IF.optimise + IF.swarm)

  Blocker resolution: 1 API rate limit resolved by peer assist (3 sec, 0 Sonnet context)

  Token efficiency: 88.2% Haiku / 11.8% Sonnet (target: 90% achieved ✅)
```

---

## 🔄 COMPLETE FLOW DIAGRAM

```
USER REQUEST
    ↓
┌─────────────────────────────────────────────────────────┐
│ SONNET COORDINATOR (IF.optimise decision)               │
│ - Analyze: Can Haiku do this? YES → Dispatch           │
│ - Cost: $0.0025 (analysis + dispatch)                  │
└─────────────────────────────────────────────────────────┘
    ↓
    IF.search decomposition (8 sub-queries)
    ↓
┌─────────────────────────────────────────────────────────┐
│ REDIS BUS (Work dispatch)                               │
│ - queue:tasks_high    [task_1, task_2]                 │
│ - queue:tasks_medium  [task_3, task_4, task_5]         │
│ - queue:tasks_low     [task_6, task_7, task_8]         │
│ - channel:tasks       (notify workers)                  │
└─────────────────────────────────────────────────────────┘
    ↓
    8 workers claim tasks (atomic, parallel)
    ↓
┌────────────┬────────────┬────────────┬────────────┐
│ HAIKU 1    │ HAIKU 2    │ HAIKU 3    │ HAIKU 4    │ ...
│ Task 1     │ Task 2     │ Task 3     │ Task 4     │
│ (Execute)  │ (Execute)  │ (Execute)  │ ❌BLOCKED  │
└────────────┴────────────┴────────────┴──────┬─────┘
                                              ↓
                                       BLOCKER HIT
                                              ↓
┌─────────────────────────────────────────────────────────┐
│ REDIS PEER ASSIST (IF.swarm self-healing)               │
│ - assist_request:x9y8z7 (blocker details)              │
│ - channel:help_requests:high (broadcast)                │
│ - queue:assist_high (claimable)                         │
└─────────────────────────────────────────────────────────┘
    ↓
┌────────────┬────────────┬────────────┐
│ HAIKU 6    │ HAIKU 7    │ HAIKU 8    │ (idle workers)
│ Try backup │ Find cache │ Search DB  │
│ API        │ (6h old)   │ mirror     │
│    ↓       │    ✅      │     ↓      │
│  Fails     │ SOLUTION!  │   Slower   │
└────────────┴──────┬─────┴────────────┘
                    ↓
              assist_solution:x9y8z7
                    ↓
              HAIKU 4 UNBLOCKED (3 sec)
                    ↓
              Task completes
    ↓
All 8 tasks complete
    ↓
┌─────────────────────────────────────────────────────────┐
│ REDIS BUS (Findings accumulation)                       │
│ - finding:gedimat_logistics                             │
│ - finding:gedimat_pricing                               │
│ - finding:gedimat_market_positioning                    │
│ - ... (8 total findings)                                │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│ SONNET COORDINATOR (Reassembly + Synthesis)             │
│ - Load 8 findings from Redis                            │
│ - Synthesize strategic insights                         │
│ - Cost: Incremental (synthesis only)                    │
└─────────────────────────────────────────────────────────┘
    ↓
USER RECEIVES COMPREHENSIVE ANSWER
```

---

## 💰 COST BREAKDOWN

### If Sonnet Did Everything (No IF.optimise):
```
Sonnet researches 8 topics:
  - 8 × 2,000 input tokens × $0.003/1K = $0.048
  - 8 × 1,500 output tokens × $0.015/1K = $0.180
  TOTAL: $0.228
```

### With IF.optimise × IF.search × IF.swarm:
```
Sonnet (Dispatch + Synthesis):
  - Dispatch: 500 input × $0.003/1K = $0.0015
  - Synthesis: 1,000 input + 800 output = $0.0150
  Subtotal: $0.0165

Haiku Workers (8 parallel executions):
  - 8 × 450 input tokens × $0.001/1K = $0.0036
  - 8 × 600 output tokens × $0.005/1K = $0.0240
  Subtotal: $0.0276

Gemini Librarian (Optional context loading):
  - 1 shard query: $0 (free tier)
  Subtotal: $0

Peer Assists (3 helpers for 1 blocker):
  - 3 × 100 input tokens × $0.001/1K = $0.0003
  - 3 × 150 output tokens × $0.005/1K = $0.0023
  Subtotal: $0.0026

TOTAL: $0.0467
SAVINGS: $0.1813 (79.5% cheaper!)
```

**BONUS:** Blocker resolved in 3 seconds by peers (vs 5 min Sonnet escalation)

---

## 🎯 KEY INNOVATIONS

### 1. IF.optimise: Cost-Aware Delegation
- Sonnet analyzes every task: "Can Haiku do this?"
- Default YES (90% of work)
- Only uses itself for strategic synthesis
- Real-time cost tracking enforces efficiency

### 2. IF.search: Parallel Decomposition
- Break complex question into N sub-queries
- Each sub-query = independent task
- Workers execute in parallel
- Reassemble at end (Sonnet synthesis)

### 3. IF.swarm: Distributed Coordination
- Workers claim tasks atomically (no conflicts)
- Redis pub/sub for real-time coordination
- Persistent workers stay alive to help peers
- Self-healing via peer assist pattern

### 4. Peer Assist: Zero-Escalation Blocker Resolution
- Blocked worker broadcasts help request
- Idle workers attempt parallel solutions
- First to solve publishes solution
- Blocked worker unblocks and continues
- **Sonnet never notified** (context preserved)

---

## 📈 PERFORMANCE METRICS

| Metric | Without Swarm | With Swarm | Improvement |
|--------|--------------|------------|-------------|
| **Cost** | $0.228 (all Sonnet) | $0.0467 | 79.5% cheaper |
| **Time** | 12 min (sequential) | 3 min (parallel) | 4× faster |
| **Blocker resolution** | 5 min (Sonnet escalation) | 3 sec (peer assist) | 100× faster |
| **Sonnet context** | 16K tokens | 2.5K tokens | 84% reduction |
| **Scalability** | Limited (Sonnet bottleneck) | Unlimited (add workers) | ∞ |

---

## ✅ READY TO USE

**Files created:**
1. ✅ `SONNET_SWARM_COORDINATOR_PROMPT.md` - Coordinator starter
2. ✅ `HAIKU_WORKER_STARTER_PROMPT.md` - Worker starter
3. ✅ `context_indicator.py` - Real-time monitoring
4. ✅ `PEER_ASSIST_PATTERN.md` - Blocker resolution (Instance #8)
5. ✅ `IF_OPTIMISE_SEARCH_SWARM_WORKFLOW.md` - This document

**Start your next session:**
```bash
# Terminal 1: Sonnet coordinator
claude --model sonnet-4.5
# Paste: SONNET_SWARM_COORDINATOR_PROMPT.md

# Ask complex question
"Research Gedimat supplier network"

# Sonnet dispatches 8 tasks to Redis

# Terminals 2-9: Haiku workers (spawn as needed)
claude --model haiku-4.5
# Paste: HAIKU_WORKER_STARTER_PROMPT.md

# Workers claim tasks, execute, write findings to Redis
# If blocked, request peer assistance
# Peers resolve blockers in parallel
# No Sonnet escalation needed

# Sonnet loads findings from Redis
# Synthesizes comprehensive answer
# Reports cost savings and efficiency
```

**You now have the complete IF.optimise × IF.search × IF.swarm architecture!** 🚀
