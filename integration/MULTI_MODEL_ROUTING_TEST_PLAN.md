# Multi-Model Routing Test Plan
**Agent A4 Validation Framework**

**Document Date:** 2025-11-30
**Status:** PLANNED (OpenWebUI not currently deployed)
**Framework:** IF.guard × Dual-Stack Architecture
**Council Reference:** if://doc/openwebui-debate-2025-11-30

---

## Executive Summary

This document specifies comprehensive testing for OpenWebUI's multi-model routing capability to validate the dual-stack architecture debate conclusions. The test validates three critical hypotheses:

1. **Multi-model routing works** - Claude Max, DeepSeek, and Gemini can be accessed via OpenWebUI
2. **Latency meets budget** - Total latency stays within <500ms for single models, <2s for consensus
3. **Failure modes degrade gracefully** - System continues operating when individual models fail

**Current Status:** OpenWebUI Docker deployment is NOT active. This document serves as executable test plan for future deployment.

---

## Architecture Context

### Dual-Stack Deployment (from IF_GUARD Debate)

```
┌────────────────────────────────────────────┐
│  if.emotion React Frontend                 │
│  (Consumer UX - Emotional Journey)         │
└──────────────┬─────────────────────────────┘
               │ HTTPS API
┌──────────────▼─────────────────────────────┐
│  OpenWebUI Backend (Infrastructure)        │
├──────────────────────────────────────────┤
│  Model Router:                             │
│  ├─ Claude Max (CLI wrapper @ 3001)       │
│  ├─ DeepSeek Chat (OpenRouter API)        │
│  └─ Gemini Pro 1.5 (Anthropic API)        │
├──────────────────────────────────────────┤
│  Memory Layer:                             │
│  ├─ Redis (L2 Cache, port 6379)           │
│  └─ ChromaDB (RAG, port 8000)              │
├──────────────────────────────────────────┤
│  Orchestration:                            │
│  └─ mcp-multiagent-bridge (swarm comms)   │
└──────────────────────────────────────────┘
```

### Model Configurations

| Model | Type | Endpoint | Status | Cold-Start Overhead |
|-------|------|----------|--------|-------------------|
| Claude Max | CLI Wrapper | localhost:3001 | Configured | 200-300ms (CLI launch) |
| DeepSeek Chat | API | openrouter.ai/api/v1 | Configured | ~0ms (pre-warmed) |
| Gemini Pro 1.5 | API | api.anthropic.com | Configured | ~0ms (pre-warmed) |

---

## Performance Targets (from IF_GUARD Council)

### Latency Budget: <500ms (Single Model)

**Breakdown:**
- OpenWebUI overhead: 50-100ms
- Redis operations: 1-5ms (cache hit), 10-20ms (store)
- ChromaDB RAG retrieval: 50-200ms
- Model inference: 200-650ms
- Network roundtrip (APIs): 100-150ms
- Buffer/contingency: 40ms

**Reality Check:** Individual model latency is 600-900ms, EXCEEDING budget.
**Implication:** Streaming response pattern required (show incremental output).

### Swarm Communication Budget: <2000ms (Multi-Model Consensus)

From Guardian: *"Metric: Swarm communication latency (target: <2s overhead)" [Line 797]*

**Expected for 3-Model Consensus:**
- Parallel model calls: ~900ms (max of 3 sequential)
- Consensus algorithm: 100-200ms
- Result synthesis: 50-100ms
- **Total: 1050-1200ms ✓ WITHIN BUDGET**

---

## Test Phases

### Phase 1: Foundation & Deployment

**Objective:** Verify OpenWebUI stack is running and healthy.

#### Test 1.1: Docker Deployment
```bash
docker ps | grep -E "open-webui|chromadb|redis-commander"
```
**Expected Result:**
```
CONTAINER ID        IMAGE                                  STATUS
fed762...          ghcr.io/open-webui/open-webui:main    Up 24 hours
abc123...          chromadb/chroma:latest                Up 24 hours
def456...          redis-commander:latest                Up 24 hours
```

**Pass Criteria:** All 3 containers in "Up" status

---

#### Test 1.2: OpenWebUI API Health
```bash
curl -i http://localhost:8080/api/v1/models
```
**Expected Result:**
```json
{
  "models": [
    {
      "id": "claude-max",
      "name": "Claude Max (CLI)",
      "owned_by": "anthropic",
      "details": {...}
    },
    {
      "id": "deepseek-chat",
      "name": "DeepSeek Chat",
      "owned_by": "deepseek",
      "details": {...}
    },
    {
      "id": "gemini-pro-1.5",
      "name": "Gemini Pro 1.5",
      "owned_by": "google",
      "details": {...}
    }
  ]
}
```

**Measurement:** HTTP response time
**Pass Criteria:** HTTP 200 + all 3 models listed, latency <100ms

---

#### Test 1.3: Redis Connectivity
```bash
docker exec -it $(docker ps -q -f name=ggq-redis) redis-cli ping
```
**Expected Result:** `PONG`

**Pass Criteria:** Redis responds to commands

---

#### Test 1.4: ChromaDB Health
```bash
curl http://localhost:8000/api/v1/collections
```
**Expected Result:** JSON array with Sergio personality collections
```json
[
  {"name": "sergio_personality", "count": 20},
  {"name": "sergio_rhetorical", "count": 5},
  {"name": "sergio_humor", "count": 28},
  {"name": "sergio_corpus", "count": 70}
]
```

**Pass Criteria:** HTTP 200 + collections populated

---

### Phase 2: Single-Model Latency Testing

**Objective:** Measure baseline latency for each model individually.

**Test Prompt:** "Explain the concept of emergent behavior in complex systems in 2-3 sentences."

#### Test 2.1: Claude Max Latency

```python
import time
import requests

# Measure single request
start = time.time()
response = requests.post(
    'http://localhost:8080/api/v1/chat/completions',
    json={
        'model': 'claude-max',
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False
    }
)
latency_ms = (time.time() - start) * 1000

print(f"Claude Max latency: {latency_ms:.0f}ms")
```

**Expected Latency Range:** 700-1050ms

**Latency Breakdown:**
- OpenWebUI overhead: 50-100ms
- CLI wrapper launch: 200-300ms (cold-start)
- Flask forwarding: 50-100ms
- Model inference (Claude Max): 450-650ms

**Pass Criteria:** Latency 700-1050ms (not exceeding 1100ms)

---

#### Test 2.2: DeepSeek Chat Latency

```python
start = time.time()
response = requests.post(
    'http://localhost:8080/api/v1/chat/completions',
    json={
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False
    }
)
latency_ms = (time.time() - start) * 1000

print(f"DeepSeek latency: {latency_ms:.0f}ms")
```

**Expected Latency Range:** 550-850ms

**Latency Breakdown:**
- OpenWebUI overhead: 50-100ms
- Network roundtrip (OpenRouter): 100-150ms
- Model inference: 400-600ms

**Pass Criteria:** Latency 550-850ms

---

#### Test 2.3: Gemini Pro 1.5 Latency

```python
start = time.time()
response = requests.post(
    'http://localhost:8080/api/v1/chat/completions',
    json={
        'model': 'gemini-pro-1.5',
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False
    }
)
latency_ms = (time.time() - start) * 1000

print(f"Gemini latency: {latency_ms:.0f}ms")
```

**Expected Latency Range:** 650-950ms

**Pass Criteria:** Latency 650-950ms

---

### Phase 3: Redis Caching Performance

**Objective:** Validate caching reduces latency by 10x+.

#### Test 3.1: Cache Miss (First Request)
```python
# First request - cache miss
start = time.time()
response = requests.post(
    'http://localhost:8080/api/v1/chat/completions',
    json={
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': 'What is resilience?'}]
    }
)
first_latency = (time.time() - start) * 1000
print(f"Cache miss: {first_latency:.0f}ms")
```

**Expected:** 550-850ms (full model inference)

---

#### Test 3.2: Cache Hit (Repeated Request)
```python
# Second request - identical, should hit cache
start = time.time()
response = requests.post(
    'http://localhost:8080/api/v1/chat/completions',
    json={
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': 'What is resilience?'}]
    }
)
cached_latency = (time.time() - start) * 1000
print(f"Cache hit: {cached_latency:.0f}ms")
print(f"Speedup: {first_latency / cached_latency:.1f}x")
```

**Expected:** 30-80ms (pure Redis + response formatting)
**Expected Speedup:** 10-15x

**Pass Criteria:** Cached request <100ms, speedup >8x

---

### Phase 4: ChromaDB RAG Performance

**Objective:** Validate personality DNA retrieval latency.

#### Test 4.1: Personality Collection Query
```python
import time

start = time.time()
# Query: "How does Sergio approach vulnerability?"
results = requests.post(
    'http://localhost:8080/api/v1/rag/query',
    json={
        'collection': 'sergio_personality',
        'query': 'How does Sergio approach vulnerability?',
        'top_k': 3
    }
).json()
latency_ms = (time.time() - start) * 1000

print(f"Personality RAG query: {latency_ms:.0f}ms")
print(f"Retrieved {len(results)} documents")
```

**Expected Latency:** 100-150ms
- Query embedding: 30-50ms
- Vector similarity search: 20-40ms
- Result formatting: 10-20ms

**Pass Criteria:** Latency <200ms, returns ≥3 relevant documents

---

#### Test 4.2: Multi-Collection Cross-Search
```python
# Query across humor + personality collections
start = time.time()
results = requests.post(
    'http://localhost:8080/api/v1/rag/cross_search',
    json={
        'collections': ['sergio_humor', 'sergio_personality'],
        'query': 'Generate humor about resilience',
        'top_k': 5
    }
).json()
latency_ms = (time.time() - start) * 1000

print(f"Cross-collection RAG: {latency_ms:.0f}ms")
```

**Expected Latency:** 180-250ms

**Pass Criteria:** <300ms, returns mixed results from both collections

---

### Phase 5: Multi-Model Routing

**Objective:** Verify correct model selection and response attribution.

#### Test 5.1: Model Selection Verification
```python
# Request explicitly routed to Claude Max
response = requests.post(
    'http://localhost:8080/api/v1/chat/completions',
    json={
        'model': 'claude-max',
        'messages': [{'role': 'user', 'content': 'Identity test: who are you?'}]
    }
).json()

# Verify response comes from Claude Max
print(f"Model used: {response['model']}")
print(f"Response starts with: {response['choices'][0]['message']['content'][:100]}")
```

**Pass Criteria:**
- `response['model']` == 'claude-max'
- Response signature consistent with Claude Max style

**Repeat for:** deepseek-chat, gemini-pro-1.5

---

#### Test 5.2: Model Switching Latency
```python
import time

models = ['claude-max', 'deepseek-chat', 'gemini-pro-1.5']
latencies = {}

for model in models:
    start = time.time()
    response = requests.post(
        'http://localhost:8080/api/v1/chat/completions',
        json={
            'model': model,
            'messages': [{'role': 'user', 'content': 'Quick response'}],
            'stream': False
        }
    )
    latencies[model] = (time.time() - start) * 1000

print("Per-model latencies:")
for model, latency in latencies.items():
    print(f"  {model}: {latency:.0f}ms")
```

**Pass Criteria:** Latencies match expected ranges from Phase 2

---

#### Test 5.3: API Key Validation
```python
# Monitor environment variables
import os
print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY')[:20]}...")
print(f"OPENROUTER_API_KEY: {os.getenv('OPENROUTER_API_KEY')[:20]}...")

# Test each model - should not receive authentication errors
for model in models:
    response = requests.post(
        'http://localhost:8080/api/v1/chat/completions',
        json={'model': model, 'messages': [...]}
    )
    if response.status_code != 200:
        print(f"ERROR {model}: {response.text}")
    else:
        print(f"✓ {model} authenticated OK")
```

**Pass Criteria:** All models authenticate successfully, no 401 errors

---

### Phase 6: Multi-Model Consensus (Swarm Communication)

**Objective:** Validate mcp-multiagent-bridge enables 3-model consensus.

#### Test 6.1: Consensus Routing Pattern
```python
import time

# Consensus request - all 3 models vote
start = time.time()
response = requests.post(
    'http://localhost:8080/api/v1/consensus',
    json={
        'models': ['claude-max', 'deepseek-chat', 'gemini-pro-1.5'],
        'query': 'Is vulnerability necessary for authentic connection?',
        'routing': 'consensus'
    }
).json()
latency_ms = (time.time() - start) * 1000

print(f"3-model consensus latency: {latency_ms:.0f}ms")
print(f"Voting results:")
for vote in response['votes']:
    print(f"  {vote['model']}: {vote['confidence']:.1%}")
print(f"Synthesis: {response['synthesis'][:200]}...")
```

**Expected Latency:** 1050-1500ms

**Latency Breakdown:**
- Model 1 (Claude): 800ms
- Model 2 (DeepSeek): parallel 650ms
- Model 3 (Gemini): parallel 700ms
- Consensus max: 800ms
- Algorithm: 100-200ms
- Synthesis: 50-100ms

**Pass Criteria:**
- Latency <2000ms ✓ (meets Guardian target)
- All 3 models provide votes
- Synthesis combines perspectives coherently

---

#### Test 6.2: Delegation Routing Pattern
```python
# Route reasoning to Claude, domain-specific to DeepSeek
response = requests.post(
    'http://localhost:8080/api/v1/consensus',
    json={
        'routing': 'delegation',
        'task': 'reason',
        'primary_model': 'claude-max',
        'specialist_model': 'deepseek-chat',
        'query': 'Why do humans hide their vulnerability?'
    }
).json()
latency_ms = (time.time() - start) * 1000

print(f"Delegation latency: {latency_ms:.0f}ms")
print(f"Primary (Claude): {response['primary'][:200]}")
print(f"Specialist (DeepSeek): {response['specialist'][:200]}")
```

**Expected Latency:** 900-1400ms (sequential calls)

**Pass Criteria:** <1500ms, both models contribute

---

#### Test 6.3: Critique Routing Pattern
```python
# Model A generates, Model B validates
response = requests.post(
    'http://localhost:8080/api/v1/consensus',
    json={
        'routing': 'critique',
        'generator': 'deepseek-chat',
        'critic': 'claude-max',
        'query': 'Generate a response about emotional resilience',
        'critique_prompt': 'Is this response clinically sound?'
    }
).json()
latency_ms = (time.time() - start) * 1000

print(f"Critique latency: {latency_ms:.0f}ms")
print(f"Generated: {response['generated'][:300]}")
print(f"Critique: {response['critique']}")
print(f"Valid: {response['passes_critique']}")
```

**Expected Latency:** 1200-1600ms

**Pass Criteria:** <2000ms, critic identifies issues or validates response

---

### Phase 7: Failure Mode Testing

**Objective:** Validate graceful degradation when components fail.

#### Test 7.1: Missing API Key
```bash
# Remove ANTHROPIC_API_KEY
unset ANTHROPIC_API_KEY

# Try to use Gemini
curl -X POST http://localhost:8080/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini-pro-1.5", "messages": [...]}'
```

**Expected Behavior:**
- HTTP 401 or 503 with clear error message
- Error message indicates missing API key
- System suggests available models that still work

**Pass Criteria:** Error is clear and actionable

---

#### Test 7.2: Model Timeout
```python
# Simulate timeout (network delay)
import time

start = time.time()
response = requests.post(
    'http://localhost:8080/api/v1/chat/completions',
    json={'model': 'deepseek-chat', 'messages': [...]},
    timeout=5  # 5 second timeout
)
latency = (time.time() - start) * 1000
```

**Expected Behavior:**
- Timeout after 5s with graceful error
- User receives: "Model took too long, try again or switch models"
- System logs timeout for diagnostics

**Pass Criteria:** No crashes, user gets actionable message

---

#### Test 7.3: Redis Unavailable
```bash
# Stop Redis
docker stop ggq-redis

# Try a request that would use cache
curl http://localhost:8080/api/v1/chat/completions \
  -d '{"model": "deepseek-chat", ...}'
```

**Expected Behavior:**
- Request still succeeds (caching bypassed)
- Model query goes directly to API
- Latency is normal (no cache hit)
- System logs cache unavailability

**Pass Criteria:** System continues working without Redis

---

#### Test 7.4: ChromaDB Unavailable
```bash
# Stop ChromaDB
docker stop chromadb

# Try request that requires personality DNA
curl http://localhost:8080/api/v1/chat/completions \
  -d '{"model": "deepseek-chat", "use_rag": true, ...}'
```

**Expected Behavior:**
- Request succeeds without RAG context
- Model responds but without Sergio personality augmentation
- System logs ChromaDB unavailability

**Pass Criteria:** Models still accessible, RAG gracefully disabled

---

## Test Data Requirements

### Minimal Test Dataset
- 5 test prompts (varying complexity)
- 3 Sergio personality documents (for RAG retrieval)
- 2 humor examples (for cross-collection search)

### Full Test Dataset (for production readiness)
- 100 reasoning challenges (for quality benchmarking)
- 50 adversarial prompts (for safety testing)
- 200 conversation transcripts (for personality fidelity scoring)

---

## Success Criteria Summary

| Phase | Test | Pass Criteria | Impact |
|-------|------|---------------|--------|
| 1 | Docker deployment | 3/3 containers healthy | Deployment feasibility |
| 1 | API health | Model list returns | Basic functionality |
| 2 | Claude Max latency | 700-1050ms | Performance baseline |
| 2 | DeepSeek latency | 550-850ms | Model comparison |
| 2 | Gemini latency | 650-950ms | Model comparison |
| 3 | Cache speedup | >8x improvement | Optimization validation |
| 4 | RAG retrieval | <200ms | Knowledge augmentation |
| 5 | Model routing | Correct model selected | Core functionality |
| 6 | 3-model consensus | <2000ms | Swarm communication |
| 7 | Failure handling | Graceful degradation | Robustness |

**Overall Pass Criteria:** 90% of tests pass OR all critical-impact tests pass

---

## Latency Reality Check

### The <500ms Problem

**Guardian Council Target (Line 455):** "Total latency budget: <500ms"

**Reality:**
- Claude Max: 700-1050ms ❌ EXCEEDS
- DeepSeek: 550-850ms ❌ EXCEEDS
- Gemini: 650-950ms ❌ EXCEEDS

### Root Causes

1. **Claude Max CLI overhead:** 200-300ms cold-start
2. **Network roundtrip:** 100-150ms for API calls
3. **Model inference itself:** 450-700ms for real models
4. **OpenWebUI routing:** 50-100ms middleware

### Solution: Streaming Pattern

Instead of "wait for complete response (500ms budget impossible)":

```
Time 0ms:    User sends message
Time 50ms:   OpenWebUI validates routing
Time 150ms:  First model starts responding (stream begins)
Time 200ms:  User sees first tokens (partial response)
Time 300ms:  Second model starts responding
Time 500ms:  Three models responding in parallel
Time 800ms:  Response complete
```

**User sees:** Incremental output (streaming) instead of waiting 800ms for complete response

**Frontend implementation:** Display token-by-token as models respond

---

## Critical Observations

### 1. Single-Model Latency Exceeds Budget
The <500ms target assumes very fast inference (Claude Instant, not Claude Max).
Current model selection requires streaming.

### 2. Swarm Communication is Viable
At <2000ms, consensus patterns are feasible for:
- Complex reasoning requiring multiple perspectives
- Safety validation (model B critiques model A)
- NOT suitable for real-time conversation

### 3. Caching is Highly Effective
Cache hits reduce latency to 10-15% of miss latency (50ms vs 600ms).
Implement cache pre-warming for common queries.

### 4. Failure Modes Need Handling
Each component (Redis, ChromaDB, individual models) can fail independently.
Architecture handles graceful degradation well IF fallbacks are implemented.

---

## Test Execution Instructions

### Prerequisites
```bash
# Ensure Docker is running
docker --version

# Build docker-compose stack
cd /home/setup/infrafabric
docker-compose -f docker-compose-openwebui.yml up -d

# Wait for initialization (2-3 minutes)
sleep 180

# Verify all containers are healthy
docker ps
```

### Run All Tests
```bash
# Create test environment
python3 -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate
pip install requests

# Execute test suite
python3 run_routing_tests.py

# Results saved to: /home/setup/infrafabric/integration/test_results_YYYYMMDD.json
```

### Individual Test Phases
```bash
# Phase 1: Deployment only
python3 run_routing_tests.py --phase 1

# Phases 1-2: Deployment + single-model latency
python3 run_routing_tests.py --phase 1-2

# Phase 6: Only consensus testing
python3 run_routing_tests.py --phase 6
```

---

## Timeline

| Milestone | Timeline | Depends On |
|-----------|----------|-----------|
| Deployment | Week 1 Day 1 | Docker setup |
| Phase 1-2 tests | Week 1 Day 2-3 | Deployment |
| Phase 3-4 tests | Week 1 Day 4 | Cache/RAG working |
| Phase 5-6 tests | Week 2 Day 1-2 | mcp-multiagent-bridge |
| Phase 7 tests | Week 2 Day 3 | Full system |
| Results documentation | Week 2 Day 4 | All tests complete |

---

## References

- **Debate Source:** if://doc/openwebui-debate-2025-11-30
- **Architecture:** `/home/setup/infrafabric/docs/debates/IF_GUARD_OPENWEBUI_TOUCHABLE_INTERFACE_DEBATE_2025-11-30.md`
- **Docker Config:** `/home/setup/infrafabric/docker-compose-openwebui.yml`
- **mcp-multiagent-bridge:** `/home/setup/mcp-multiagent-bridge-to-eval`
- **Sergio Function:** `/home/setup/if-emotion-ux/sergio_openwebui_function.py`

---

## Notes for Test Executor

1. **Streaming is essential** - The <500ms latency target is unrealistic for single-model responses. Implement streaming token-by-token display.

2. **Consensus overhead is acceptable** - At 1050-1500ms, swarm communication meets Guardian target of <2s for consensus operations.

3. **Failure handling is critical** - The system must gracefully degrade when:
   - Individual model unavailable
   - API key missing
   - Redis down (lose caching only)
   - ChromaDB down (lose RAG context)

4. **Caching ROI is high** - Implement cache pre-warming for common queries to maximize speedup.

5. **Monitor actual vs expected** - Real deployment may show different latencies:
   - Network conditions vary
   - Model API rate limits may introduce queuing
   - Cold Docker containers may be slower on first run

