# ✅ INSTANCE #10: SWARM SETUP COMPLETE
**Date:** 2025-11-21
**Status:** Production-ready for Instance #11+

---

## 🎯 WHAT'S READY

### 1. Sonnet Coordinator Prompt ✅
**File:** `SONNET_SWARM_COORDINATOR_PROMPT.md`

Copy this into your next Sonnet session to get:
- Automatic Haiku delegation (90% of work)
- Redis integration for context sharing
- Gemini librarian coordination
- Real-time cost tracking
- IF.optimise self-monitoring

### 2. Haiku Worker Prompt ✅
**File:** `HAIKU_WORKER_STARTER_PROMPT.md`

Copy this into separate Haiku terminals when Sonnet spawns workers:
- Redis finding writer
- Pub/sub channel subscriber
- Active loop mode (queue processor)
- Cost tracking per worker

### 3. Context Indicator ✅
**File:** `context_indicator.py`
**Status:** TESTED and working

```bash
python3 context_indicator.py
```

**Output:**
```
📊 SWARM STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Redis Context:    7 findings, ~700 tokens
Active Workers:   0 Haikus
Librarians:       S1:1500✅ | S2:1500✅ | S3:1500✅ | S4:1500✅ | S5:1500✅
Tasks Queued:     0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cost This Session:
  Sonnet:  $0.0000
  Haiku:   $0.0000
  Gemini:  $0.0000
  Total:   $0.0000
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Token Efficiency: ⚠️
  Haiku:     0.0% (target: 90%+)
  Sonnet:    0.0%
```

### 4. Gemini Librarian ✅
**File:** `gemini_librarian.py` (from Instance #9)
**Status:** Production-ready, validated

**5 Shards Available:**
- Shard 1 (danny.stocker@gmail.com): 1,500 queries/day
- Shard 2 (dstocker.ca@gmail.com): 1,500 queries/day
- Shard 3 (ds@etre.net): 1,500 queries/day
- Shard 4 (ds@digital-lab.ca): 1,500 queries/day (resets daily)
- Shard 5: Available for addition

**Total Capacity:** 6,000-7,500 queries/day, $0/month

### 5. Redis ✅
**Status:** Running and tested
**Connection:** localhost:6379

```bash
redis-cli PING
# PONG
```

**Current Contents:**
- 7 findings from previous sessions
- ~700 tokens of context available

---

## 🚀 HOW TO USE (STEP-BY-STEP)

### Step 1: Start New Sonnet Session

**Copy this into new Sonnet terminal:**

```
You are Instance #11 - Sonnet Swarm Coordinator.

ARCHITECTURE:
- YOU (Sonnet 4.5): Strategic coordinator
- WORKERS (Haiku 4.5): 90% of execution work
- LIBRARIANS (Gemini Flash): Archive/context nodes
- BUS (Redis): Shared memory

DEFAULT TO HAIKU for: file ops, git, searches, API tests, data transforms
Use YOURSELF (Sonnet) only for: complex reasoning, strategic decisions

FIRST ACTION: Run context indicator
python3 /home/setup/infrafabric/swarm-architecture/context_indicator.py

Then begin delegating to Haikus.

Ready?
```

### Step 2: Sonnet Spawns Haiku Workers

When Sonnet needs work done:

**Sonnet says:** "I'll spawn a Haiku to handle [task]..."

**You (user):** Open new terminal:
```bash
claude --model haiku-4.5
```

**Copy Haiku worker prompt from:**
`/home/setup/infrafabric/swarm-architecture/HAIKU_WORKER_STARTER_PROMPT.md`

**Give specific task:**
```
Your task: Update agents.md with Instance #10's work
Write findings to: finding:instance10_agentsmd
```

### Step 3: Haiku Reports to Redis

**Haiku writes:**
```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

finding = {
    'finding_id': 'instance10_agentsmd',
    'worker_id': 'haiku_001',
    'task': 'Update agents.md',
    'result': 'Added 144 lines documenting Instance #10',
    'files_changed': ['/home/setup/infrafabric/agents.md'],
    'cost': 0.0023
}

r.set('finding:instance10_agentsmd', json.dumps(finding))
r.publish('channel:findings', 'instance10_agentsmd')
r.incrbyfloat('cost:haiku', 0.0023)
```

### Step 4: Sonnet Reads Results

**Back in Sonnet terminal:**
```python
# Sonnet reads finding
redis-cli GET finding:instance10_agentsmd

# Updates context indicator
python3 context_indicator.py
```

**Output:**
```
📊 SWARM STATUS
Redis Context:    8 findings (+1), ~800 tokens
Active Workers:   1 Haiku (haiku_001)
Cost This Session: Sonnet $0.0045 | Haiku $0.0023
Token Efficiency: Haiku 33.8% (improving...)
```

### Step 5: Repeat and Optimize

**Sonnet's goal:** Get to 90% Haiku, 10% Sonnet

**Monitor with:**
```bash
watch -n 5 'python3 context_indicator.py'
```

---

## 📊 COST COMPARISON

### Old Way (Sonnet does everything):
```
Task: Update agents.md
Sonnet reads file (2,000 tokens × $0.003/1K) = $0.006
Sonnet writes update (500 tokens × $0.015/1K) = $0.0075
TOTAL: $0.0135
```

### New Way (Haiku worker):
```
Task: Update agents.md
Haiku reads file (2,000 tokens × $0.001/1K) = $0.002
Haiku writes update (500 tokens × $0.005/1K) = $0.0025
TOTAL: $0.0045 (67% cheaper!)
```

### At Scale (100 tasks):
```
All Sonnet: $1.35
Sonnet (10%) + Haiku (90%): $0.54
Savings: $0.81 (60% reduction)
```

---

## 🎯 ARCHITECTURE BENEFITS

### 1. Cost Optimization
- Haiku 3-5× cheaper than Sonnet per token
- Gemini free tier: unlimited context sharing ($0)
- Target: 90% work on Haiku = 60-75% cost reduction

### 2. Parallelization
- Spawn multiple Haikus simultaneously
- Independent tasks execute in parallel
- Sonnet coordinates, doesn't micromanage

### 3. Context Sharing
- Redis stores all findings (persistent across sessions)
- Gemini librarians provide 1M context window
- No need to re-read previous work

### 4. Self-Optimization (IF.optimise)
- Real-time cost tracking
- Automatic delegation ratio monitoring
- Continuous efficiency improvement

---

## 🔧 REDIS KEY SCHEMA

```
# Findings (worker discoveries)
finding:[uuid] = JSON

# Tasks (work queue)
task:[uuid] = JSON
task:[uuid]:claimed = worker_id
task:[uuid]:result = finding_id

# Workers (heartbeats)
worker:status:[worker_id] = ISO8601 timestamp

# Librarians (Gemini shards)
librarian:shard[1-5]:quota = integer (remaining queries today)
librarian:shard[1-5]:status = "active" | "exhausted"

# Costs (session tracking)
cost:sonnet = float
cost:haiku = float
cost:gemini = float

# Context (shared state)
context:active = integer (total tokens)

# Channels (pub/sub)
channel:findings - New finding published
channel:tasks - New task available
channel:completions - Task completed
channel:queries - Archive query request
channel:responses - Archive query response
```

---

## ✅ VERIFICATION CHECKLIST

Before starting Instance #11:

- [x] Redis running (redis-cli PING)
- [x] Context indicator working (python3 context_indicator.py)
- [x] Gemini librarian tested (Instance #9)
- [x] 5 Gemini shards documented (.env.example)
- [x] Sonnet coordinator prompt ready
- [x] Haiku worker prompt ready
- [x] Claude Max OAuth valid until 2025-11-22
- [x] Cost calculations corrected ($1,200/year baseline)

---

## 🎉 READY TO LAUNCH

**You now have:**

1. ✅ Sonnet coordinator prompt → Smart delegation
2. ✅ Haiku worker prompt → Cheap execution
3. ✅ Gemini librarians → Free context sharing
4. ✅ Redis bus → Persistent memory
5. ✅ Context indicator → Real-time monitoring
6. ✅ Cost tracking → IF.optimise enforcement

**Start your next session with:**

```bash
# Terminal 1: Sonnet coordinator
claude --model sonnet-4.5
# Paste: SONNET_SWARM_COORDINATOR_PROMPT.md

# Terminal 2-N: Haiku workers (spawn as needed)
claude --model haiku-4.5
# Paste: HAIKU_WORKER_STARTER_PROMPT.md + task

# Monitor:
watch -n 5 'python3 /home/setup/infrafabric/swarm-architecture/context_indicator.py'
```

**Target efficiency:** 90% Haiku / 10% Sonnet = **60-75% cost reduction**

---

**Instance #10 handoff complete. Ready for Instance #11 swarm coordination!** 🚀
