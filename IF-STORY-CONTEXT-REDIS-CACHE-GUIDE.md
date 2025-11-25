# IF.* Story Context - Redis Cache Guide

**Purpose:** Pre-cache component contexts to avoid reading duplicate files across 12 story agents
**Estimated Savings:** 40-50% token reduction through deduplication
**Setup Time:** ~30 minutes (one-time, before agents start)
**Retrieval Speed:** <100ms per key (vs 500-2000ms for file reads)

---

## Architecture: Why Redis?

### Problem
12 Haiku agents × 12 stories = 144 potential file reads

If each story needs:
- agents.md section (50-100 lines) = 1 read
- IF-foundations.md excerpt (200 lines) = 1 read
- IF-armour.md excerpt (300 lines) = 1 read
- Local philosophy database excerpt = 1 read

That's 4 reads × 12 agents = **48 redundant file reads** of identical content

### Solution
Pre-cache every component's essential context in Redis:
- Agent 1 reads "context:file:agents.md:IF.yologuard-section" → stored in Redis
- Agent 2 needs same content → retrieves from Redis (100× faster)
- Net result: 48 file reads → 12 unique reads + 36 cache hits

### Token Savings
- Average file excerpt: 200-500 tokens
- 36 cache hits × 400 tokens average = **14,400 tokens saved**
- That's enough budget for 1 entire additional story

---

## Redis Keys Schema

All keys follow this pattern:

```
context:{type}:{source}:{component}[-:{detail}]

Types:
  - file: Specific file excerpt (with line range)
  - doc: Complete documentation/conceptual guide
  - incident: Real-world case study reference
  - methodology: Framework/methodology explainer

Examples:
  context:file:agents.md:IF.yologuard-section
  context:file:IF-armour.md:defense-tiers
  context:doc:yologuard-complete-v3
  context:incident:knight-capital-440m-loss
  context:methodology:8-pass-search
```

---

## Pre-Cache Initialization

### Step 1: Redis Connection
```bash
redis-cli ping
# Should return: PONG

# If not running:
# redis-server --daemonize yes
# redis-cli ping
```

### Step 2: Load Core Component Contexts

For **each story**, extract key sections and pre-cache:

#### Story 1: IF.yologuard
```bash
# Agents.md IF.yologuard overview (lines 67-75)
redis-cli SET "context:file:agents.md:IF.yologuard-section" \
  "$(sed -n '67,75p' /home/setup/infrafabric/agents.md)" \
  EX 86400  # 24-hour expiration

# IF-armour.md false-positive reduction mechanics (lines 78-383)
redis-cli SET "context:file:IF-armour.md:fp-reduction" \
  "$(sed -n '78,383p' /home/setup/infrafabric/IF-armour.md)" \
  EX 86400

# IF.yologuard_v3.py entropy detection code (lines 1-200)
redis-cli SET "context:file:IF.yologuard_v3.py:entropy-detection" \
  "$(sed -n '1,200p' /home/setup/infrafabric/code/yologuard/src/IF.yologuard_v3.py)" \
  EX 86400
```

#### Story 2: IF.guard
```bash
# IF-foundations.md Guardian Council section (lines 1-200)
redis-cli SET "context:file:IF-foundations.md:guardian-council" \
  "$(sed -n '1,200p' /home/setup/infrafabric/IF-foundations.md)" \
  EX 86400

# demo-guardian-council.html implementation (lines 1-100)
redis-cli SET "context:file:demo-guardian-council.html:council-viz" \
  "$(sed -n '1,100p' /home/setup/infrafabric/demo-guardian-council.html)" \
  EX 86400
```

#### Story 3: IF.ceo
```bash
# agents.md IF.ceo definition
redis-cli SET "context:file:agents.md:IF.ceo-facets" \
  "$(sed -n '95,105p' /home/setup/infrafabric/agents.md)" \
  EX 86400

# IF-vision.md 8 light + 8 dark facets
redis-cli SET "context:file:IF-vision.md:ceo-integration" \
  "$(sed -n '200,400p' /home/setup/infrafabric/IF-vision.md)" \
  EX 86400
```

#### Story 4: IF.memory
```bash
# IF-MEMORY-DISTRIBUTED.md persistence architecture
redis-cli SET "context:file:IF-MEMORY-DISTRIBUTED.md:architecture" \
  "$(sed -n '1,300p' /home/setup/infrafabric/papers/IF-MEMORY-DISTRIBUTED.md)" \
  EX 86400

# agents.md session handover system
redis-cli SET "context:file:agents.md:IF.memory-handover" \
  "$(sed -n '145,165p' /home/setup/infrafabric/agents.md)" \
  EX 86400
```

#### Story 5: IF.optimise
```bash
# CLAUDE.md IF.optimise framework
redis-cli SET "context:file:CLAUDE.md:IF.optimise-framework" \
  "$(grep -A 20 'Token Efficiency Strategy' /home/setup/infrafabric/.claude/CLAUDE.md)" \
  EX 86400

# ANNEX-N-IF-OPTIMISE-FRAMEWORK.md (if file exists)
redis-cli SET "context:file:annexes:IF.optimise-costs" \
  "$(sed -n '1,135p' /home/setup/infrafabric/annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md 2>/dev/null || echo 'File not found')" \
  EX 86400
```

#### Story 6: IF.search
```bash
# IF-foundations.md 8-pass methodology
redis-cli SET "context:file:IF-foundations.md:search-8pass" \
  "$(sed -n '519,855p' /home/setup/infrafabric/IF-foundations.md)" \
  EX 86400
```

#### Story 7: IF.witness
```bash
# IF-witness.md meta-validation architecture
redis-cli SET "context:file:IF-witness.md:meta-validation" \
  "$(sed -n '1,300p' /home/setup/infrafabric/IF-witness.md)" \
  EX 86400
```

#### Story 8: IF.ground
```bash
# IF-foundations.md 8 anti-hallucination principles
redis-cli SET "context:file:IF-foundations.md:ground-principles" \
  "$(sed -n '14,96p' /home/setup/infrafabric/IF-foundations.md)" \
  EX 86400
```

#### Story 9: IF.joe × IF.rory
```bash
# agents.md GEDIMAT framework integration
redis-cli SET "context:file:agents.md:IF.joe-rory-gedimat" \
  "$(sed -n '108,205p' /home/setup/infrafabric/agents.md)" \
  EX 86400

# IF.philosophy-database.yaml Joe Coulombe section
redis-cli SET "context:file:IF.philosophy-database.yaml:joe-coulombe" \
  "$(sed -n '168,254p' /home/setup/infrafabric/philosophy/IF.philosophy-database.yaml)" \
  EX 86400
```

#### Story 10: IF.TTT
```bash
# IF-TTT-INDEX-README.md compliance framework
redis-cli SET "context:file:IF-TTT-INDEX-README.md:ttt-framework" \
  "$(sed -n '1,150p' /home/setup/infrafabric/IF-TTT-INDEX-README.md)" \
  EX 86400
```

#### Story 11: IF.philosophy
```bash
# IF.philosophy-database.yaml 12-philosopher definitions
redis-cli SET "context:file:IF.philosophy-database.yaml:12-philosophers" \
  "$(sed -n '1,300p' /home/setup/infrafabric/philosophy/IF.philosophy-database.yaml)" \
  EX 86400
```

#### Story 12: IF.swarm
```bash
# IF-SWARM-S2.md multi-agent coordination
redis-cli SET "context:file:IF-SWARM-S2.md:architecture" \
  "$(sed -n '1,300p' /home/setup/infrafabric/papers/IF-SWARM-S2.md)" \
  EX 86400
```

---

## Real Incident Contexts

Pre-cache key real incidents referenced in stories:

```bash
# Knight Capital $440M loss reference
redis-cli SET "context:incident:knight-capital-2012" \
  "Real incident: Knight Capital Group's algorithmic trading error on August 2, 2012. \
  A new trading code was released that the firm failed to fully test. The code executed \
  trades wildly for 45 minutes before being shut down, causing a loss of $440 million. \
  The company was on the brink of bankruptcy." \
  EX 86400

# Flash Crash 2010 reference
redis-cli SET "context:incident:flash-crash-2010" \
  "Real incident: May 6, 2010 - US stock market underwent a sudden, severe crash. \
  Within minutes, $1 trillion in market value evaporated. Automated trading algorithms, \
  faced with a sudden wave of selling, algorithm amplified the crash through feedback loops. \
  Within 14 minutes, the market recovered." \
  EX 86400

# Cambridge Analytica data scandal
redis-cli SET "context:incident:cambridge-analytica-2018" \
  "Real incident: 2018 - Political consulting firm Cambridge Analytica harvested personal \
  data of millions of Facebook users without consent. Used psychological profiling for \
  political advertising. Scandal destroyed company, resulted in massive regulatory fines, \
  and changed social media privacy laws worldwide." \
  EX 86400

# ProPublica COMPAS investigation
redis-cli SET "context:incident:compas-propublica-2016" \
  "Real incident: ProPublica's 2016 investigation revealed COMPAS (Correctional Offender \
  Management Profiling for Alternative Sanctions), a criminal risk assessment tool used \
  by US courts, had significant racial bias. African American defendants were 45% more \
  likely to be labeled as higher risk than white defendants." \
  EX 86400
```

---

## Verification: Check Cache Load

```bash
# List all cache keys
redis-cli KEYS "context:*"

# Count cached entries
redis-cli KEYS "context:*" | wc -l
# Should be 25-35 keys depending on what was cached

# Check size of specific key
redis-cli STRLEN "context:file:IF-armour.md:fp-reduction"

# Check memory usage
redis-cli INFO memory

# Verify specific key exists
redis-cli EXISTS "context:file:agents.md:IF.yologuard-section"
# Should return: (integer) 1
```

---

## Haiku Agent Retrieval

When a Haiku agent needs context, they execute:

```bash
# Example: Story 1 needs IF.yologuard overview
redis-cli GET "context:file:agents.md:IF.yologuard-section"

# Output will be the cached file excerpt (fast, no disk I/O)
```

**Time Comparison:**
- Direct file read: `sed -n '67,75p' /path/to/agents.md` = 200-500ms
- Redis retrieval: `redis-cli GET "context:..."` = 10-50ms
- **Speedup: 10-50× faster**

---

## Cache Invalidation Strategy

Set expiration time based on file update frequency:

```
Short-lived (6 hours - EX 21600):
  - CLAUDE.md sections (user updates frequently)
  - agents.md sections (may change during session)

Medium-lived (24 hours - EX 86400):
  - IF-armour.md, IF-witness.md (stable research docs)
  - Philosophy database (rarely changes)

Long-lived (7 days - EX 604800):
  - Real incident references (immutable historical data)
  - Completed case studies (GEDIMAT, etc.)
```

### Refresh Cache After Update

If a source file is updated:

```bash
# Clear old cache
redis-cli DEL "context:file:agents.md:IF.yologuard-section"

# Re-populate with new content
redis-cli SET "context:file:agents.md:IF.yologuard-section" \
  "$(sed -n '67,75p' /home/setup/infrafabric/agents.md)" \
  EX 86400
```

---

## Monitoring Cache Performance

Track cache hit/miss rates:

```bash
# Before agents start
redis-cli INFO stats | grep -E "hits|misses|keyspace"

# After agents finish
redis-cli INFO stats | grep -E "hits|misses|keyspace"

# Calculate hit rate
# (hits / (hits + misses)) × 100 = percentage
# Target: >85% hit rate for optimal performance
```

**Expected result:**
- 48 potential reads
- 12 cache misses (initial reads)
- 36 cache hits (agents sharing contexts)
- **Hit rate: 75% minimum, 85%+ target**

---

## Memory Management

Estimate Redis memory usage:

```
Per cached file excerpt: 200-1500 tokens ≈ 600-5000 bytes
Total contexts: 25-35 keys
Expected memory: 15-150 KB (very small)

Actual check:
redis-cli INFO memory | grep used_memory
```

**No memory concerns.** Redis overhead < 1 MB even with full cache.

---

## Troubleshooting

### Redis Connection Fails
```bash
# Check if Redis is running
ps aux | grep redis-server

# Start Redis if needed
redis-server --daemonize yes

# Test connection
redis-cli ping
```

### Cache Key Not Found
```bash
# Check for typos in key name
redis-cli KEYS "*yologuard*"

# Should return matching keys like:
# "context:file:agents.md:IF.yologuard-section"

# If no results, key wasn't cached. Add it:
redis-cli SET "context:file:agents.md:IF.yologuard-section" \
  "$(sed -n '67,75p' /home/setup/infrafabric/agents.md)" \
  EX 86400
```

### Memory Too High
```bash
# Check what's using memory
redis-cli --bigkeys

# Clear less-used keys
redis-cli EVAL "return redis.call('del', unpack(redis.call('keys', 'context:incident:*')))" 0
```

---

## Full Bootstrap Script

Save as `/home/setup/infrafabric/scripts/cache-init.sh`:

```bash
#!/bin/bash
# Initialize Redis cache for IF.* story contexts
# Usage: bash cache-init.sh

echo "Initializing Redis cache for 12 story contexts..."

# Story 1: IF.yologuard
redis-cli SET "context:file:agents.md:IF.yologuard-section" "$(sed -n '67,75p' /home/setup/infrafabric/agents.md)" EX 86400
redis-cli SET "context:file:IF-armour.md:fp-reduction" "$(sed -n '78,383p' /home/setup/infrafabric/IF-armour.md)" EX 86400

# Story 2: IF.guard
redis-cli SET "context:file:IF-foundations.md:guardian-council" "$(sed -n '1,200p' /home/setup/infrafabric/IF-foundations.md)" EX 86400

# Story 3: IF.ceo
redis-cli SET "context:file:agents.md:IF.ceo-facets" "$(sed -n '95,105p' /home/setup/infrafabric/agents.md)" EX 86400

# Story 4: IF.memory
redis-cli SET "context:file:agents.md:IF.memory-handover" "$(sed -n '145,165p' /home/setup/infrafabric/agents.md)" EX 86400

# Story 5: IF.optimise
redis-cli SET "context:file:agents.md:IF.optimise-section" "$(sed -n '165-183p' /home/setup/infrafabric/agents.md)" EX 86400

# Story 6: IF.search
redis-cli SET "context:file:IF-foundations.md:search-8pass" "$(sed -n '519,855p' /home/setup/infrafabric/IF-foundations.md)" EX 86400

# Story 7: IF.witness
redis-cli SET "context:file:IF-witness.md:meta-validation" "$(sed -n '1,300p' /home/setup/infrafabric/IF-witness.md)" EX 86400

# Story 8: IF.ground
redis-cli SET "context:file:IF-foundations.md:ground-principles" "$(sed -n '14,96p' /home/setup/infrafabric/IF-foundations.md)" EX 86400

# Story 9: IF.joe × IF.rory
redis-cli SET "context:file:agents.md:IF.joe-rory-gedimat" "$(sed -n '108,205p' /home/setup/infrafabric/agents.md)" EX 86400

# Story 10: IF.TTT
redis-cli SET "context:file:IF-TTT-INDEX-README.md:ttt-framework" "$(sed -n '1,150p' /home/setup/infrafabric/IF-TTT-INDEX-README.md)" EX 86400

# Story 11: IF.philosophy
redis-cli SET "context:file:IF.philosophy-database.yaml:12-philosophers" "$(sed -n '1,300p' /home/setup/infrafabric/philosophy/IF.philosophy-database.yaml)" EX 86400

# Story 12: IF.swarm
redis-cli SET "context:file:IF-SWARM-S2.md:architecture" "$(sed -n '1,300p' /home/setup/infrafabric/papers/IF-SWARM-S2.md)" EX 86400

# Real incidents
redis-cli SET "context:incident:knight-capital-2012" "Knight Capital Group - $440M loss, August 2, 2012. Algorithmic trading code failure." EX 604800
redis-cli SET "context:incident:flash-crash-2010" "Flash Crash 2010 - $1 trillion market evaporation in 14 minutes due to automated trading feedback loops." EX 604800
redis-cli SET "context:incident:cambridge-analytica-2018" "Cambridge Analytica - 2018 political consulting firm scandal, unauthorized data harvesting, psychological profiling." EX 604800
redis-cli SET "context:incident:compas-propublica-2016" "COMPAS investigation - 2016 ProPublica study revealed 45% racial bias in criminal risk assessment." EX 604800

echo "Cache initialization complete."
echo "Total keys cached: $(redis-cli KEYS 'context:*' | wc -l)"
echo "Memory used: $(redis-cli INFO memory | grep used_memory_human)"
```

Run it:
```bash
chmod +x /home/setup/infrafabric/scripts/cache-init.sh
bash /home/setup/infrafabric/scripts/cache-init.sh
```

---

## Performance Metrics

Expected improvements with full cache:

| Metric | Without Cache | With Cache | Improvement |
|--------|---------------|-----------|------------|
| Context retrieval per agent | 4-6 seconds | 0.5-1 second | **6-10× faster** |
| Total time 12 agents reading context | 48-72 seconds | 6-12 seconds | **6-10× faster** |
| Token cost (file reads) | 20-25K tokens | 10-15K tokens | **40-50% reduction** |
| Parallel story writing speed | 60-90 minutes | 50-70 minutes | **20% faster** |

---

## Summary

Pre-caching in Redis:
1. **Eliminates 36 redundant file reads** (out of 48)
2. **Saves 14,400 tokens** of context budget
3. **Speeds up retrieval by 6-10×**
4. **Enables parallel execution** of 12 agents without bottlenecks
5. **Costs ~30 minutes setup**, saves 1+ hour execution

**Next step:** Run `cache-init.sh` before agents start writing.
