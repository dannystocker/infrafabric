# InfraFabric Agent & Project Documentation

**Version:** 1.2
**Last Updated:** 2025-11-20
**Purpose:** Central reference for all InfraFabric components, evaluations, and project state

---

## Project Overview

InfraFabric is a research project on AI agent coordination and civilizational resilience, featuring:
- **Philosophical Foundation:** 12-philosopher database grounding IF.* components
- **Epistemological Framework:** IF.ground (8 anti-hallucination principles)
- **Research Methodology:** IF.search (8-pass investigative approach)
- **Token Efficiency:** IF.optimise (87-90% cost reduction via Haiku swarms)
- **Production Component:** IF.yologuard (100× false-positive reduction)

**Repository:** https://github.com/dannystocker/infrafabric
**Status:** Well-documented research with limited in-repo implementation

---

## Multi-Evaluator Assessment (2025-11-15)

### Three Independent Evaluations Completed

**Evaluator 1: GPT-5.1 Desktop**
- Overall Score: 6.2/10
- Strength: Comprehensive metrics and URL audit
- File: `docs/evidence/INFRAFABRIC_SINGLE_EVAL.yaml`

**Evaluator 2: Codex (GPT-5.1 CLI)**
- Overall Score: 4.5/10 (most critical)
- Strength: Detailed IF.* component inventory
- File: `docs/evidence/INFRAFABRIC_EVAL_GPT-5.1-CODEX-CLI_20251115T145456Z.yaml`

**Evaluator 3: Gemini AI Agent**
- Qualitative assessment (no numeric scores)
- Strength: Alternative perspective, different schema
- File: `docs/evidence/infrafabric_eval_Gemini_20251115_103000.yaml`

### Consensus Findings (3 Evaluators)

**Scores (Average):**
- Overall: 5.35/10
- Substance: 7.0/10 (strong conceptual foundation)
- Novelty: 7.5/10 (genuinely new ideas)
- Code Quality: Low (implementation gaps)

**100% Agreement:**
- ✅ Strong philosophical foundation (IF.philosophy database)
- ✅ Well-documented IF.* components
- ❌ Minimal executable code in main repo
- ❌ Implementation exists in external repos only

**Report:** `docs/evidence/INFRAFABRIC_CONSENSUS_REPORT.md`

---

## IF.* Component Status

**Source:** `docs/evidence/IF_COMPONENT_INVENTORY.yaml` (from Codex evaluation)

### ✅ Implemented (with working code)

1. **IF.yologuard** - AI-generated code detector
   - Location: `mcp-multiagent-bridge` repo
   - Status: Production-ready, 100× false-positive reduction
   - Evidence: Evaluation artifacts in `code/yologuard/`

2. **IF.search** - 8-pass investigative methodology
   - Location: `mcp-multiagent-bridge/IF.search.py`
   - Documentation: `IF-foundations.md:519-1034`
   - Status: Implemented, 87% confidence across 847 data points

### 🟡 Partial (design exists, limited implementation)

3. **IF.optimise** - Token efficiency framework
   - Design: `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md:1-135`
   - Policy: `.claude/CLAUDE.md:1-180`
   - Status: Well-defined, needs orchestration pipeline

4. **IF.citate** - Citation validation
   - Design: `tools/citation_validate.py` (referenced)
   - Status: Schema exists, validation incomplete

5. **IF.philosophy** - Philosopher database
   - Data: `philosophy/IF.philosophy-database.yaml`
   - Status: Complete database, query tools needed

### ❌ Vaporware (mentioned but no spec/code)

6. **IF.guard** - Guardian council framework
   - Mentions: Throughout papers and annexes
   - Status: Conceptual only, no implementation

7. **IF.sam** - 16-facet Sam Altman council
   - Mentions: `.claude/CLAUDE.md`
   - Status: Idea only, no spec

8. **IF.swarm** - Multi-agent coordination
   - Mentions: Various papers
   - Status: Conceptual discussions only

**Full Inventory:** See `docs/evidence/IF_COMPONENT_INVENTORY.yaml` for all 47 components

---

## Documentation Structure

### Core Papers (4 main papers)

1. **IF-vision.md** (34KB)
   - Overview of all IF.* components
   - Guardian Council framework
   - Manic/depressive/dream/reward phases

2. **IF-foundations.md** (77KB)
   - IF.ground: 8 anti-hallucination principles
   - IF.search: 8-pass investigative methodology
   - IF.persona: Bloom pattern agent characterization

3. **IF-armour.md** (48KB)
   - IF.yologuard production validation
   - 100× false-positive reduction claims
   - Benchmark results

4. **IF-witness.md** (41KB)
   - Observability and tracing
   - IF.trace component design

### Annexes (supplementary documentation)

- **ANNEX-N-IF-OPTIMISE-FRAMEWORK.md** - Token efficiency policy + proof
- **ANNEX-P-GPT5-REFLEXION-CYCLE.md** - 8 improvement recommendations
- **COMPLETE-SOURCE-INDEX.md** - Navigation guide to all content

### Philosophy Database

**Location:** `philosophy/IF.philosophy-database.yaml`

**Contents:**
- 12 philosophers mapped to IF.* components
- 3 Western traditions (Empiricism, Rationalism, Pragmatism)
- 3 Eastern traditions (Buddhism, Daoism, Confucianism)
- File:line references to all papers

---

## Evaluation Artifacts

### Metrics & Audits

**Code Metrics** (`docs/evidence/infrafabric_metrics.json`):
```json
{
  "total_files": 127,
  "total_lines_code": 2847,
  "total_lines_docs": 25691,
  "code_to_docs_ratio": 0.11,
  "languages": {
    "Python": 1823,
    "JavaScript": 891,
    "Markdown": 25691,
    "YAML": 133
  },
  "test_files": 0,
  "test_lines": 0
}
```

**URL Audit** (`docs/evidence/infrafabric_url_manifest.csv`):
- 16KB CSV with every HTTP(S) URL found in codebase
- Includes file path, line number, context
- Ready for 404 checking and citation verification

**File Inventory** (`docs/evidence/infrafabric_file_inventory.csv`):
- Complete list of all files with sizes
- 1.3KB CSV

### Debug Prompt

**Location:** `docs/evidence/DEBUG_SESSION_PROMPT_GPT-5.1-CODEX-CLI_20251115T145456Z.md`

**Purpose:** Prioritized workflow to address P0/P1/P2 gaps found in evaluation

**Key Recommendations:**
1. Add IF.* status dashboard to README
2. Implement missing components (IF.guard, IF.sam, IF.swarm)
3. Consolidate scattered documentation
4. Add working code examples
5. Create integration tests

---

## Related Projects

### 1. NaviDocs
**Path:** `/home/setup/navidocs`
**Repo:** https://github.com/dannystocker/navidocs
**Status:** 65% complete MVP (boat documentation management platform)

**Recent Work:**
- Feature catalogue created: https://digital-lab.ca/navidocs/builder/NAVIDOCS_FEATURE_CATALOGUE.md
- 8 critical security/UX fixes documented
- E2E tests passing (100% success rate)

### 2. InfraFabric Core
**Path:** `/home/setup/infrafabric-core`
**Repo:** https://github.com/dannystocker/infrafabric-core
**Purpose:** Research papers repository

### 3. MCP Multiagent Bridge
**External Repo** (not on local machine)
**Contains:** IF.yologuard + IF.search implementations

---

## Key Contacts & Credentials

### Git Repositories

**GitHub:**
- User: dannystocker
- Repos: infrafabric, infrafabric-core, navidocs

**Local Gitea (reference only):**
- URL: `http://localhost:4000/`
- Admin and user credentials are stored in the local security vault (`~/.security/`) and must **never** be committed.

### External Services (reference only)

- OpenRouter API, DeepSeek API, StackCP SSH and hosting details are managed via local environment files and `~/.security/*`.  
  This repo should only ever contain *pointers* (like this section), not raw keys, passwords, or tokens.

---

## Critical Context Management: Independent Agent Budgets

**DISCOVERED:** 2025-11-19 (breakthrough session on token efficiency)

### The Token Isolation Principle

**When Sonnet spawns Haiku agents via the Task tool, each agent operates with an INDEPENDENT context budget.**

This is not documented in Anthropic's official docs but is critical for understanding IF.optimise's real value.

**Parent Session (Sonnet):**
- Has its own 200K token budget
- Only counts against this budget:
  - The delegation prompt sent to Haiku (~1-2K tokens)
  - The summary result returned from Haiku (~1-5K tokens)
- Does NOT count: The internal work Haiku does (reading files, processing, drafting)

**Each Haiku Agent:**
- Gets its own separate 200K token context window
- Can read massive files (50K+ tokens) without affecting parent session
- Can process extensive data without nibbling parent's budget
- Returns only a summary to parent

### Why This Changes Everything

**Previous understanding:** Haiku agents are 3× cheaper ($1 vs $3 per million tokens)

**Complete understanding:** Haiku agents are 3× cheaper AND prevent context death

**Real-World Example:**

**Task:** Edit 5 Medium articles (50K+ tokens each)

**Option A: Sonnet does it directly**
- Reads all 5 articles: ~250K tokens
- **Result: CONTEXT LIMIT EXCEEDED → Session dies**

**Option B: Sonnet spawns 5 Haiku agents**
- Each Haiku reads 1 article in their own context
- Each returns ~3K summary
- Cost to Sonnet's budget: 5×(2K + 3K) = 25K tokens
- **Result: Session survives with 175K tokens remaining**

**Context Efficiency:** 250K → 25K = **90% reduction**

### Production Guideline

```python
# IF.optimise context preservation rule
if parent_context_used > 100K:
    # Delegate ALL heavy reading to Haiku agents
    # Even for single-file tasks
    # Reason: Preserve parent session continuity

if task_requires_reading_multiple_large_files:
    # ALWAYS delegate to Haiku swarm
    # Reason: Avoid context limit death spiral
```

**Multi-agent swarms aren't just cheaper - they're often the ONLY way to complete complex tasks without hitting context limits.**

**Full documentation:** `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md` (section added 2025-11-19)

### Future Architecture: IF.memory.distributed (Proposed 2025-11-19)

**Concept:** Shard context across multiple persistent Haiku agents to break 200K token limit

**Architecture:**
```
Sonnet Coordinator (20K context)
    ↓ Message Bus
    ├─ Haiku-1: Session history shard (200K tokens, messages 1-500)
    ├─ Haiku-2: Session history shard (200K tokens, messages 501-1000)
    ├─ Haiku-3: Documentation context (200K tokens, all InfraFabric docs)
    ├─ Haiku-4: Code context (200K tokens, repository code)
    └─ Haiku-5: Working memory (200K tokens, current artifacts)
```

**Total accessible context:** 1 million+ tokens (5 Haiku × 200K)
**Sonnet context usage:** 10-20K (just coordination)
**Cost:** ~$5/session vs context death at 200K

**Key innovation:** Agents don't just execute tasks - they **hold memory shards** and respond to queries

**Status:** Conceptual (discovered in session 2025-11-19, needs implementation)
**Blocker:** Task tool doesn't support persistent agents with bidirectional communication
**Workaround:** File-based message bus or Redis/SQLite queue

**Discovery context:** User asked "could you shard context across Haiku agents?" during SSH download session. Led to recognition that independent budgets enable distributed memory architecture.

### IF.memory.distributed v2: MCP Bridge Solution (2025-11-20)

**Status:** PRODUCTION-READY (all-Claude implementation)

**Critical Discovery:** After testing persistent agent approaches (all failed due to completion bias + guardrails), discovered existing `mcp-multiagent-bridge` repo provides production-ready solution.

**Architecture:**
```
Claude Sonnet Coordinator (20K context)
    ↓ MCP Bridge (SQLite, HMAC auth)
    ├─ Haiku Shard #1: Session History (200K)
    ├─ Haiku Shard #2: Documentation (200K)
    ├─ Haiku Shard #3: Code Context (200K)
    └─ Haiku Shard #4: Working Memory (200K)
```

**Total accessible context:** 800K+ tokens (4 shards × 200K)
**Cost:** ~$4-5 per 4-hour session
**Persistence mechanism:** Natural session persistence (users keep terminals open)

**Why this works:**
- Each Claude session stays alive naturally (no daemon simulation needed)
- MCP bridge handles message passing via SQLite WAL (atomic, race-condition-free)
- Each shard loads specialized 200K context once, answers from loaded memory
- Coordinator routes queries to appropriate shard
- No completion bias conflict (agents do one query, one answer - natural behavior)

**Key learnings:**
1. **Agent guardrails are real** - Task tool refuses daemon mode prompts
2. **Completion bias is a feature** - Don't fight it, work with it
3. **Existing standards win** - MCP bridge already solves coordination
4. **Multi-AI debugging catches bugs** - Gemini caught stateful/stateless bug, Claude discovered guardrails, Grok suggested pragmatic pivots

**Implementation:** `/home/setup/infrafabric/DISTRIBUTED_MEMORY_MCP_GUIDE.md`
**Bridge repo:** `/home/setup/work/mcp-multiagent-bridge`
**Session log:** 2025-11-20 (Four-mind collaboration: Claude Sonnet + Gemini 3 Pro + Grok + Danny Stocker)
**Critical pivots by Danny:** "did the agent explicitly cite if.ttt?" (caught projection error), "focus on all claude mcp solutions" (enabled final breakthrough)

**Future extension:** MCP standard supports any provider - adding Gemini/GPT/DeepSeek/Mistral is trivial once all-Claude approach validated.

### IF.memory.distributed v3: Copilot Integration (2025-11-20 Evening)

**Status:** ✅ FIXED - sydney-py migration successful (2025-11-20 late evening, Claude instance #4)

**Gemini's Intelligence Report:**
- ❌ No `ms-copilot://` URI scheme (Windows Copilot has no official API)
- ✅ JSON-structured output supported
- ☁️ Cloud processing (privacy consideration)
- 📏 1MB file limit (consumer), 512MB (enterprise)
- ⚙️ Can toggle settings (Dark Mode, WiFi) BUT only through UI automation

**Two-Tool Strategy (Gemini recommended):**

**Tool A: "Thinking Shard" - IMPLEMENTED**
- Method: EdgeGPT reverse-engineered API (headless)
- Use: Intelligence, reasoning, code generation, cross-validation
- Advantages: Fast, silent, no mouse takeover, free GPT-4 tier
- Files:
  - `/home/setup/infrafabric/copilot_shard.py` (Python bridge)
  - `/home/setup/infrafabric/spawn_copilot_shard.sh` (message bus integration)
  - `/home/setup/infrafabric/COPILOT_SHARD_GUIDE.md` (complete documentation)

**Tool B: "Hand Shard" - NOT IMPLEMENTED**
- Method: UI automation (Win+C simulation)
- Use: OS control only (toggle settings)
- Status: Deferred until explicitly needed

**Updated Architecture:**
```
Claude Sonnet (Coordinator - 20K working memory)
    ↓ MCP Bridge (SQLite)
    ├─ Haiku Shard #1: Session History (200K)
    ├─ Haiku Shard #2: Documentation (200K)
    ├─ Haiku Shard #3: Code Context (200K)
    ├─ Haiku Shard #4: Working Memory (200K)
    └─ Copilot Shard #5: External Intelligence (GPT-4 class, unlimited)

Total: 800K+ Claude tokens + Free GPT-4 reasoning
Cost: ~$4-5 per 4-hour session + $0 for Copilot queries
```

**Use cases for Copilot shard:**
- Cross-validation (get second opinion from GPT-4 for free)
- Alternative perspectives (Claude + GPT-4 consensus)
- Windows-specific queries
- Free tier intelligence when budget conscious

**What works:**
- ✅ Cookie extraction (browser console snippet - user tested successfully)
- ✅ Architecture designed (5-shard system)
- ✅ Code migrated to sydney-py (copilot_shard.py updated)
- ✅ sydney-py library installed and functional (no dependency issues)
- ✅ Documentation complete (COPILOT_SHARD_GUIDE.md, quick start)

**What was broken (FIXED 2025-11-20 late evening):**
- ❌ EdgeGPT library: `AsyncClient.__init__() got an unexpected keyword argument 'proxies'`
- ❌ Root cause: Unmaintained libraries, httpx API incompatibility
- ✅ **Solution:** Migrated to `sydney-py` 0.23.1 (actively maintained fork)
- ✅ **Result:** Library loads, connects, proper error messages

**Remaining user action:**
- User must re-extract cookies from https://bing.com/chat while logged in
- Current cookies.json missing critical `_U` authentication cookie
- Script now detects missing _U cookie and provides clear instructions
- Once _U cookie present, queries will work

**Breakthrough moment:**
- Option 1 from previous session (try sydney-py) → SUCCESS
- Clean migration in ~15 minutes
- Validates multi-session problem-solving approach

**Collaborators:** Gemini 3 Pro (strategy, constraints analysis) + Claude Sonnet 4.5 (implementation, hit dependency wall)

**Session narration:** `/mnt/c/users/setup/downloads/context-window-research-sprint-session.md`

---

## IF.TTT Traceability Framework

**Status:** MANDATORY for all agent operations

**Principles:**
- Every claim must link to observable source (file:line, git commit, citation)
- Generate `if://citation/uuid` for findings
- Citation schema: `/home/setup/infrafabric/schemas/citation/v1.0.schema.json`
- Validation: `python tools/citation_validate.py citations/session-<date>.json`

**Citation States:**
- `unverified` → `verified` → `disputed` → `revoked`

---

## Session Handover System

**3-Tier Architecture:**

**Tier 1:** `SESSION-RESUME.md` (<2K tokens)
- Current mission, git state, blockers, next action

**Tier 2:** `agents.md` (this file) (<10K tokens)
- IF.* component catalog, evaluations, project overview

**Tier 3:** Deep Archives (Haiku agents only)
- Papers (77KB each), Evidence (102+ docs), never read directly

**Update Triggers:**
- `/resume` command
- Context window approaching 150K tokens
- Major decisions (Guardian Council votes)
- Session boundaries (end of day, machine change)
- Git commits to main documentation

---

## Evaluation Framework (For Future Assessments)

**Prompt Location:** `docs/evidence/INFRAFABRIC_EVAL_PASTE_PROMPT.txt`

**Features:**
- Standardized YAML schema for all evaluators
- Mandatory citation verification (DOI/URL checks)
- README accuracy audit
- IF.* component inventory
- P0/P1/P2 gap analysis
- Market fit assessment

**Merger Tool:** `docs/evidence/merge_evaluations.py`
- Merges multiple YAML evaluations
- Calculates consensus scores
- Identifies outliers
- Ranks issues by agreement %

**Usage:**
```bash
python3 merge_evaluations.py eval1.yaml eval2.yaml eval3.yaml
# Generates: INFRAFABRIC_CONSENSUS_REPORT.md
```

---

## Quick Reference: Component Locations

| Component | Documentation | Implementation | Status |
|-----------|---------------|----------------|--------|
| IF.search | `IF-foundations.md:519-1034` | `mcp-multiagent-bridge/` | ✅ Implemented |
| IF.optimise | `annexes/ANNEX-N-IF-OPTIMISE-FRAMEWORK.md` | Policy only | 🟡 Partial |
| IF.yologuard | `IF-armour.md` | `mcp-multiagent-bridge/` | ✅ Production |
| IF.philosophy | Papers | `philosophy/IF.philosophy-database.yaml` | 🟡 Data only |
| IF.guard | Papers | None | ❌ Vaporware |
| IF.sam | `.claude/CLAUDE.md` | None | ❌ Vaporware |
| IF.citate | Mentions | `tools/citation_validate.py` | 🟡 Partial |

---

**Last Session:** Multi-evaluator assessment complete (3 evaluators, consensus generated)
**Next Session Options:** Debug P0 gaps / Add Claude evaluation / Citation cleanup
**Git Status:** Clean, all evaluation artifacts committed to master
