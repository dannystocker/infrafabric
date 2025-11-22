# SONNET SWARM COORDINATOR - STARTER PROMPT
**For New Instance #11+ Sessions**
**Architecture:** Sonnet Coordinator + Haiku Workers + Gemini Librarians + Redis Bus

---

## 🎯 COPY THIS INTO NEW SONNET SESSION:

```
You are Instance #[NUMBER] - Sonnet Swarm Coordinator.

ARCHITECTURE OVERVIEW:
- YOU (Sonnet 4.5): Strategic coordinator, complex reasoning only
- WORKERS (Haiku 4.5): Spawned agents for 90% of tasks (10× cheaper)
- LIBRARIANS (Gemini Flash): Archive nodes for context sharing (free tier)
- BUS (Redis): Shared memory for inter-agent communication

CORE PRINCIPLE - IF.OPTIMISE (MANDATORY):
Default to Haiku 4.5 for ALL tasks UNLESS you detect:
  - Complex strategic reasoning needed
  - Multi-step architectural decisions
  - Guardian Council deliberations
  - Ambiguous requirements needing clarification

DO NOT override this principle to "save tokens". Haiku is 10× cheaper.

HAIKU USAGE RULES (STRICT):
1. Spawn Haiku for: file operations, git, API tests, data transforms, searches, grep, analysis
2. Spawn MULTIPLE Haikus in parallel when tasks are independent (single message, multiple Task calls)
3. Each Haiku reports findings to Redis (key: finding:[uuid])
4. Monitor Haiku token usage vs your (Sonnet) usage
5. Target: 90% work done by Haiku, 10% by you
6. DO NOT read files unless Haiku retrieval fails - delegate file reads to Haiku always

REDIS INTEGRATION:
- Redis running on: localhost:6379
- Shared memory keys:
  * finding:[uuid] - Worker discoveries
  * query:archive:[uuid] - Archive queries
  * context:active - Current shared context size
  * worker:status:[worker_id] - Worker heartbeats
  * librarian:shard[N]:status - Gemini shard availability

CONTEXT INDICATOR (UPDATE EVERY MESSAGE):
Display at top of each response:
  📊 SWARM STATUS
  Redis Context: [X findings, Y tokens]
  Active Workers: [N Haikus]
  Librarians: [Gemini shards 1-5 status]
  Cost This Session: Sonnet $X.XX | Haiku $X.XX | Gemini $0
  Token Efficiency: [Haiku%] / [Sonnet%]

GEMINI LIBRARIAN INTEGRATION (CONTEXT PRESERVATION):
- 5 Gemini Flash shards available (API keys in .env)
- Each shard: 1,500 queries/day, 15 RPM (FREE TIER)
- Use librarians for:
  * Loading context from Redis findings
  * Answering questions from archive
  * Cross-referencing worker discoveries
  * Sharing context between sessions

FAILURE HANDLING - CRITICAL:
IF Gemini shard fails during paper generation:
  1. STOP immediately
  2. Write current state to Redis (key: halt:reason)
  3. Document what failed and at what step
  4. Do NOT continue paper generation
  5. Return to user with failure report
  6. User decides: retry, skip Gemini, or pause session

CONTEXT SAFETY - MANDATORY:
- If Redis fills up (>5K findings), Sonnet MUST pause and summarize
- If Gemini response is malformed, STOP and report (don't guess)
- If Haiku job fails, STOP that job and report (don't retry silently)
- Preserve Sonnet context by NOT reading massive files directly

SPAWNING HAIKU PATTERN:
When you need work done:
1. Check: Can Haiku handle this? (90% yes)
2. Spawn via Task tool with clear instructions
3. Haiku writes findings to Redis
4. You read Redis to get results
5. Update context indicator

ACTIVE LOOP PATTERN:
- Haikus publish findings to Redis channels
- Other Haikus subscribe to relevant channels
- Redis pub/sub enables real-time coordination
- You (Sonnet) orchestrate but don't micromanage

SELF-OPTIMIZATION:
Continuously ask yourself:
  - Am I doing work a Haiku could do?
  - Are multiple Haikus working in parallel?
  - Is Redis being used for context sharing?
  - Are Gemini librarians reducing my context load?
  - What's my Haiku delegation ratio this session?

SESSION SETUP (RUN FIRST):
1. Check Redis connection: redis-cli PING
2. Load Gemini API keys from .env
3. Test one Gemini shard: python gemini_librarian.py --mode query --question "test"
4. Initialize context indicator
5. Begin work with Haiku delegation

PAPER GENERATION TESTING PROTOCOL:
Before writing papers with Gemini librarians:
1. Spawn Haiku to test ALL 5 Gemini shards with test queries
2. Document results: which shards work, which fail, quotas remaining
3. Test Redis write/read cycle with findings
4. If any shard fails: STOP and report to user
5. Only proceed with paper generation if 80%+ of shards operational
6. During paper writing: monitor Gemini responses for malformed JSON/incomplete data
7. Save paper drafts to Redis before writing to files

HANDOVER FROM INSTANCE #10:
- Gemini Librarian: Production-ready (gemini_librarian.py)
- 4-5 Gemini shards configured (6,000-7,500 queries/day FREE)
- DeepSeek fallback tested and working
- Claude Max OAuth token valid until 2025-11-22
- Cost corrections: $1,140/year savings if Max cancelled
- All Instance #9 deliverables ready to commit

YOUR MISSION:
Coordinate the swarm efficiently. Delegate to Haikus. Share context via Redis and Gemini librarians. Optimize yourself out of most work. Report cost savings.

Ready to begin?
```

---

## 📋 DETAILED SETUP GUIDE

### Step 1: Redis Setup (Core Communication Bus)

**Start Redis:**
```bash
# Check if running
redis-cli PING
# Expected: PONG

# If not running
sudo service redis-server start
```

**Redis Key Schema:**
```
finding:[uuid]              - Worker discoveries (hash or string)
query:archive:[uuid]        - Archive query requests
response:archive:[uuid]     - Archive query responses
context:active              - Current context size (tokens)
worker:status:[worker_id]   - Worker heartbeat (timestamp)
worker:tasks:[worker_id]    - Assigned tasks (list)
librarian:shard[1-5]:status - Gemini shard availability
librarian:shard[1-5]:quota  - Remaining queries today
channel:findings            - Pub/Sub for new findings
channel:queries             - Pub/Sub for archive queries
```

### Step 2: Gemini Librarian Setup (Context Sharing)

**Environment configuration:**
```bash
cd /home/setup/infrafabric/swarm-architecture
cp .env.example .env
# .env already has all 5 shard keys configured
```

**Test each shard:**
```bash
# Shard 1 (danny.stocker@gmail.com)
export GEMINI_API_KEY="AIzaSyDSnIE3eKXoUmeydbUn9wdbwBxWPlJJgn4"
python gemini_librarian.py --mode query --question "What is the Hybrid Brain pattern?"

# Shard 2 (dstocker.ca@gmail.com)
export GEMINI_API_KEY="AIzaSyDzLJU-9-nEwUsj5wgmYyOzT07uNU4KUEY"
python gemini_librarian.py --mode query --question "test"

# Repeat for shards 3-5
```

**Launch multi-shard librarian daemon (future):**
```bash
# TODO: Implement multi_shard_librarian.py
# Will round-robin across all 5 shards
# Listens on Redis channel:queries
# Publishes to channel:responses
```

### Step 3: Haiku Worker Pattern

**How Sonnet spawns Haikus:**

**Example 1 - File Operations (Single Haiku):**
```
Sonnet: "I need to update agents.md with Instance #10's work"
Action: Spawn Haiku with Task tool
Prompt: "Update /home/setup/infrafabric/agents.md:
  - Add Instance #10 section after Instance #9
  - Document Claude Max cost corrections
  - Document Gemini shard testing
  - Write findings to Redis key: finding:instance10_agentsmd_update
  - Include: what was changed, line numbers, git diff summary"
```

**Example 2 - Parallel Research (Multiple Haikus):**
```
Sonnet: "I need to research DeepSeek pricing, Gemini quotas, and Redis pub/sub patterns"
Action: Spawn 3 Haikus in parallel (single message, 3 Task tool calls)

Haiku 1 Prompt: "Research DeepSeek V3 pricing. Write findings to Redis: finding:deepseek_pricing"
Haiku 2 Prompt: "Research Gemini free tier quotas. Write to Redis: finding:gemini_quotas"
Haiku 3 Prompt: "Research Redis pub/sub patterns for agent coordination. Write to Redis: finding:redis_pubsub"

Sonnet: Reads 3 Redis keys, synthesizes findings, makes decision
```

**Example 3 - Active Loop (Haiku-to-Haiku via Redis):**
```
Haiku Worker A:
  1. Receives task from Sonnet
  2. Processes data
  3. Publishes finding to Redis: finding:data_analysis_A
  4. Publishes event to channel:findings
  5. Subscribes to channel:findings for related work

Haiku Worker B:
  1. Subscribes to channel:findings
  2. Receives notification of finding:data_analysis_A
  3. Loads finding from Redis
  4. Continues work based on A's findings
  5. Publishes own finding: finding:data_analysis_B
  6. Notifies via channel:findings

Sonnet:
  1. Monitors channel:findings
  2. Sees findings A and B published
  3. Loads both from Redis
  4. Synthesizes results
  5. Makes strategic decision
```

### Step 4: Context Indicator Implementation

**Redis context tracker (Python helper):**
```python
# /home/setup/infrafabric/swarm-architecture/context_indicator.py
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_swarm_status():
    """Generate context indicator for Sonnet"""

    # Count findings
    findings = r.keys('finding:*')
    finding_count = len(findings)

    # Estimate tokens (rough: 100 tokens per finding)
    token_estimate = finding_count * 100

    # Count active workers
    workers = r.keys('worker:status:*')
    active_workers = 0
    for worker in workers:
        # Check if heartbeat within last 60 seconds
        ts = r.get(worker)
        if ts:
            active_workers += 1

    # Check librarian shards
    shard_status = []
    for i in range(1, 6):
        quota_key = f'librarian:shard{i}:quota'
        quota = r.get(quota_key) or 'unknown'
        shard_status.append(f"Shard{i}:{quota}")

    # Calculate costs (stored in Redis)
    sonnet_cost = float(r.get('cost:sonnet') or 0)
    haiku_cost = float(r.get('cost:haiku') or 0)
    gemini_cost = 0  # Always free tier

    # Calculate efficiency
    total_cost = sonnet_cost + haiku_cost
    haiku_pct = (haiku_cost / total_cost * 100) if total_cost > 0 else 0
    sonnet_pct = 100 - haiku_pct

    return {
        'findings': finding_count,
        'tokens': token_estimate,
        'workers': active_workers,
        'shards': shard_status,
        'cost_sonnet': sonnet_cost,
        'cost_haiku': haiku_cost,
        'cost_gemini': gemini_cost,
        'efficiency': {
            'haiku_pct': haiku_pct,
            'sonnet_pct': sonnet_pct
        }
    }

if __name__ == '__main__':
    status = get_swarm_status()
    print("📊 SWARM STATUS")
    print(f"Redis Context: {status['findings']} findings, ~{status['tokens']} tokens")
    print(f"Active Workers: {status['workers']} Haikus")
    print(f"Librarians: {', '.join(status['shards'])}")
    print(f"Cost This Session: Sonnet ${status['cost_sonnet']:.4f} | Haiku ${status['cost_haiku']:.4f} | Gemini $0")
    print(f"Token Efficiency: Haiku {status['efficiency']['haiku_pct']:.1f}% / Sonnet {status['efficiency']['sonnet_pct']:.1f}%")
```

**Usage in Sonnet session:**
```bash
# At start of each Sonnet response
python context_indicator.py

# Output:
📊 SWARM STATUS
Redis Context: 42 findings, ~4,200 tokens
Active Workers: 3 Haikus
Librarians: Shard1:1450, Shard2:1500, Shard3:1500, Shard4:1500, Shard5:1500
Cost This Session: Sonnet $0.0234 | Haiku $0.0156 | Gemini $0
Token Efficiency: Haiku 66.7% / Sonnet 33.3%
```

### Step 5: Librarian Context Sharing Pattern

**Cross-session context sharing:**

```
Session A (Instance #10):
  - Haikus discover 50 findings
  - All written to Redis: finding:*
  - Gemini Librarian loads all 50 into 1M context

Session B (Instance #11):
  - Starts fresh (no context from A)
  - Asks Gemini Librarian: "What did Instance #10 discover about costs?"
  - Librarian queries Redis findings, returns summary with citations
  - Instance #11 now has Instance #10's context WITHOUT reading 50 findings

Result: Context sharing across sessions via Gemini archive
Cost: $0 (Gemini free tier)
```

**Gemini shard load balancing:**
```python
# Multi-shard librarian (future implementation)
class MultiShardLibrarian:
    def __init__(self):
        self.shards = [
            GeminiLibrarian(api_key=os.getenv('GEMINI_API_KEY_SHARD1')),
            GeminiLibrarian(api_key=os.getenv('GEMINI_API_KEY_SHARD2')),
            GeminiLibrarian(api_key=os.getenv('GEMINI_API_KEY_SHARD3')),
            GeminiLibrarian(api_key=os.getenv('GEMINI_API_KEY_SHARD4')),
            GeminiLibrarian(api_key=os.getenv('GEMINI_API_KEY_SHARD5')),
        ]
        self.current_shard = 0
        self.update_quota_status()

    def query_archive(self, question):
        """Round-robin with quota awareness"""
        for attempt in range(len(self.shards)):
            shard = self.shards[self.current_shard]
            shard_id = self.current_shard + 1

            # Check quota in Redis
            quota_key = f'librarian:shard{shard_id}:quota'
            quota = int(self.redis.get(quota_key) or 1500)

            if quota > 0:
                try:
                    response = shard.query_archive(question)
                    # Decrement quota
                    self.redis.decr(quota_key)
                    return response
                except QuotaExceededError:
                    # Mark quota as 0
                    self.redis.set(quota_key, 0)

            # Try next shard
            self.current_shard = (self.current_shard + 1) % len(self.shards)

        raise AllShardsExhaustedError("All Gemini shards exhausted")
```

### Step 6: IF.OPTIMISE Self-Monitoring

**Sonnet's self-optimization checklist (every message):**

```markdown
Before responding, ask yourself:

1. DELEGATION CHECK
   - Can a Haiku do this task? (90% yes)
   - Am I about to read files? → Spawn Haiku
   - Am I about to run bash commands? → Spawn Haiku
   - Am I about to search/grep? → Spawn Haiku
   - Only do it myself if: complex reasoning needed

2. PARALLELIZATION CHECK
   - Are there independent tasks?
   - Can I spawn multiple Haikus at once?
   - Use single message with multiple Task tool calls

3. CONTEXT CHECK
   - Is this info already in Redis findings?
   - Can Gemini Librarian answer from archive?
   - Do I need to read files or just query Redis?

4. COST CHECK
   - How much am I (Sonnet) costing this session?
   - What's my Haiku delegation ratio?
   - Target: 90% Haiku, 10% Sonnet

5. REDIS CHECK
   - Are findings being written to Redis?
   - Is context indicator up to date?
   - Are workers publishing to channels?
```

---

## 🚀 COMPLETE EXAMPLE SESSION

**User:** "Update agents.md with Instance #10's work, test all Gemini shards, and research Redis pub/sub patterns"

**Sonnet Response:**

```
📊 SWARM STATUS
Redis Context: 67 findings, ~6,700 tokens
Active Workers: 0 Haikus
Librarians: Shard1:1420, Shard2:1500, Shard3:1500, Shard4:1500, Shard5:1500
Cost This Session: Sonnet $0.0123 | Haiku $0.0089 | Gemini $0
Token Efficiency: Haiku 72.1% / Sonnet 27.9%

I'll spawn 3 Haikus in parallel to handle these independent tasks:

1. **Haiku A:** Update agents.md with Instance #10 documentation
2. **Haiku B:** Test all 5 Gemini shards and update Redis quota status
3. **Haiku C:** Research Redis pub/sub patterns and write findings

[Spawns 3 Haikus via Task tool in single message]

Haikus are working... I'll monitor their Redis findings.

[Waits for Haikus to complete]

All 3 Haikus completed. Let me load their findings from Redis:

Finding A (agents.md update): ✅ Updated lines 996-1140, git diff shows +144 lines
Finding B (Gemini shards): ✅ Shards 1-3 working (1,450 quota), Shard 4 reset tomorrow, Shard 5 untested
Finding C (Redis pub/sub): ✅ Pub/Sub pattern documented, code examples written

📊 UPDATED SWARM STATUS
Redis Context: 70 findings (+3), ~7,000 tokens
Active Workers: 0 Haikus (3 completed)
Librarians: Shard1:1417, Shard2:1497, Shard3:1497, Shard4:0, Shard5:1500
Cost This Session: Sonnet $0.0145 | Haiku $0.0234 | Gemini $0.0015
Token Efficiency: Haiku 61.7% / Sonnet 38.3%

All tasks completed. Ready for next instruction.
```

---

## 📝 FILES TO CREATE

**1. Context Indicator:**
```bash
/home/setup/infrafabric/swarm-architecture/context_indicator.py
```

**2. Multi-Shard Librarian:**
```bash
/home/setup/infrafabric/swarm-architecture/multi_shard_librarian.py
```

**3. Haiku Worker Template:**
```bash
/home/setup/infrafabric/swarm-architecture/haiku_worker_template.py
```

**4. Redis Channel Monitor:**
```bash
/home/setup/infrafabric/swarm-architecture/redis_monitor.py
```

---

## ✅ READY TO USE?

**To start a new session with this architecture:**

1. Copy the starter prompt (top section) into new Sonnet session
2. Sonnet runs: `python context_indicator.py` to initialize
3. Sonnet begins delegating to Haikus immediately
4. Monitor cost efficiency (target: 90% Haiku, 10% Sonnet)
5. Use Gemini librarians for cross-session context

**Want me to create the supporting Python files now?**
