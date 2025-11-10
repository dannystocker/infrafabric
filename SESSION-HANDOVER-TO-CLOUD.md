# Session Handover: Local → Cloud Transition

**Purpose:** Minimal context handoff for first Claude Code Web session (<2,000 tokens target)

**Created:** 2025-11-10
**Environment:** Claude Code Web (Anthropic $1000 credits)
**Repository:** https://github.com/dannystocker/infrafabric
**Citation:** if://session/handover-to-cloud-2025-11-10

---

## Current Mission

**Primary Task:** Fix yologuard benchmark reproducibility (CRITICAL BLOCKER for external publication)

**Context:** Gemini 2.5 Pro evaluation (2025-11-10) revealed false claims in project documentation. Most critical issue: yologuard benchmark not reproducible.

**⚠️ CRITICAL BLOCKER BEFORE EXTERNAL PUBLICATION:**
IF.yologuard benchmark UNVERIFIED - Cannot publish externally until fixed.
- **Claimed:** 98.96% recall (95/96 secrets), 100% precision
- **Gemini test:** 55.4% detection rate (97/175 secrets)
- **Issue:** Corpus size discrepancy, inconsistent metrics across papers

**Expected Outcome:**
1. Create canonical, reproducible benchmark script
2. Document exact "usable-only" filtering criteria
3. Explain corpus size discrepancy (96 vs 175 secrets)
4. Update all 6 papers with single, verified metric

---

## Repository State

**Location:** Clone from https://github.com/dannystocker/infrafabric
```bash
git clone https://github.com/dannystocker/infrafabric.git
cd infrafabric
```

**Size:** 71 MB (239 markdown files, 584 Python files)

**Latest Commits:**
```
9ac803a - Add cloud transition plan and update security policy (2025-11-10 04:15)
c409c74 - Configure GitHub secret scanning to ignore test fixtures (2025-11-10 03:45)
876c45f - Security: Add .env to .gitignore after removing from history (2025-11-10 03:41)
6393f6a - Fix false claims identified by Gemini 2.5 Pro evaluation (2025-11-10 02:37)
```

**Working Tree:** Clean (all commits pushed)

**Branch:** master (synced with origin/master)

---

## Critical Context

### What Was Recently Fixed (Local Environment)

✅ **COMPONENT-INDEX.md** - Rebuilt as functional catalog (87 components, not 91)
✅ **SESSION-RESUME.md** - Corrected false claims (component count, citations, yologuard status)
✅ **GUARDED-CLAIMS.md** - Yologuard status: VERIFIED → UNVERIFIED
✅ **InfraFabric.md** - Fixed citation numbering (all 47 citations now referenced)
✅ **Security Incident** - .env removed from git history, credentials revoked, gitignored

### What Gemini Verified (Can Use Externally)

✅ **Philosophy integration** genuine (8/10) - not marketing
✅ **Ethical foundation** authentic (9/10) - walks the talk
✅ **tools/ifctl.py** validator working (philosophy as lint rules)
✅ **100% Guardian consensus** (Dossier 07) - verified

### What Remains Broken (Cannot Publish)

⚠️ **IF.yologuard benchmark** UNVERIFIED (HIGHEST PRIORITY)
⚠️ **40+ undocumented IF.* components** (catalog or deprecate)
⚠️ **IF-momentum.md missing** (one of 6 core papers)
⚠️ **Naming inconsistencies** (IF.ceo vs IF.ceo_, IF.citation vs IF.citations)

---

## Token Budget ($1000 Anthropic Credits)

**Pricing:**
- **Sonnet 4.5:** Input $3/M, Output $15/M
- **Haiku 4.5:** Input $1/M, Output $5/M
- **Ratio:** Haiku = Sonnet / 3 (Anthropic-verified)

**Budget Allocation:**
```
Phase 1: Setup & Verification (5% - $50)
Phase 2: Yologuard Fix (30% - $300) ← START HERE
Phase 3: Documentation (25% - $250)
Phase 4: Paper Refinement (25% - $250)
Phase 5: Reserve (15% - $150)
```

**Estimated Runway:**
- Optimistic (80% Haiku): ~$34 for 4M tokens → 29x iterations
- Realistic (50% Haiku): ~$48 for 4M tokens → 20x iterations
- Conservative (20% Haiku): ~$78 for 5M tokens → 12x iterations

**Monitoring:** Track actual Haiku vs Sonnet ratio after first major task

---

## IF.optimise Strategy (Token Efficiency)

**Default Rule:**
```
Use Haiku for: file reads, git ops, data transforms, searches
Use Sonnet for: architecture, philosophy, complex reasoning
```

**Examples:**
```python
# ✅ Use Haiku
- Read papers/IF-armour.md and count "yologuard" mentions
- Git status, git log, git diff
- Grep search for IF.* component references
- JSON/YAML data transformations

# 🧠 Use Sonnet
- Design canonical benchmark methodology
- Guardian Council deliberations
- Philosophy → tech mapping validation
- Complex architectural decisions
```

**Claimed Savings:** 87-90% cost reduction via Haiku delegation
**Status:** ⚠️ UNVERIFIED - use cautiously, measure actual savings

---

## First Actions (Choose Path A, B, or C)

### Path A: Verify Cloud Environment (RECOMMENDED FIRST STEP - 10 min)

1. **Clone Repository**
   ```bash
   git clone https://github.com/dannystocker/infrafabric.git
   cd infrafabric
   git log --oneline -5  # Should show: 9ac803a, c409c74, 876c45f, 6393f6a
   ```

2. **Verify .env is NOT Present**
   ```bash
   ls .env  # Should NOT exist (gitignored)
   cat .gitignore | grep "\.env"  # Should show .env is ignored
   ```

3. **Test Haiku Agent Spawn**
   ```
   Prompt: "Spawn a Haiku agent to read COMPONENT-INDEX.md and count how many
   components have status '✅ Documented'. Report back the count."

   Expected: Haiku agent completes task, returns count (should be ~25)
   Cost: ~500-1000 tokens Haiku ($0.003-0.006)
   ```

4. **Verify Python Tools Work**
   ```bash
   python --version  # Should be 3.12+
   python tools/ifctl.py validate --test  # Should show IF.ground principles
   ```

**Success Criteria:**
- ✅ Repository cloned
- ✅ .env not present (as expected)
- ✅ Haiku agent spawns and completes task
- ✅ tools/ifctl.py runs successfully

**Then → Proceed to Path B (Yologuard Fix)**

---

### Path B: Fix Yologuard Benchmark (CRITICAL BLOCKER - 15-25K tokens)

**Estimated Time:** 2-3 hours
**Estimated Cost:** $10-30 (depending on Haiku delegation)

**Step 1: Understand Current State (Use Haiku)**
```
Spawn 3 Haiku agents in parallel to read:
1. papers/IF-armour.md (yologuard section)
2. docs/GUARDED-CLAIMS.md (Claim 1: yologuard)
3. code/yologuard/benchmarks/run_leaky_repo_test.py (current benchmark)

Ask each: "What does this document claim about yologuard's recall rate?"
```

**Step 2: Identify Corpus Discrepancy (Use Sonnet)**
```
Analyze Haiku summaries:
- Why does benchmark script find 175 secrets when docs claim 96?
- What is "usable-only" filtering?
- Are there multiple versions of Leaky Repo?
```

**Step 3: Create Canonical Benchmark (Use Haiku for implementation)**
```
Create code/yologuard/benchmarks/canonical_benchmark.py:
1. Document exact Leaky Repo commit hash
2. Implement "usable-only" filter with explicit criteria
3. Add corpus size verification (fail if != expected size)
4. Generate reproducible output (JSON with all metrics)
```

**Step 4: Run and Verify (Use Haiku)**
```bash
python code/yologuard/benchmarks/canonical_benchmark.py > results.json
cat results.json  # Verify metrics match documentation
```

**Step 5: Update All Papers (Use Haiku for mechanical edits)**
```
Search all papers for inconsistent metrics:
- grep -r "98.96" papers/
- grep -r "96.43" papers/
- grep -r "100%" papers/ (precision claims)

Update each file with single, verified metric from canonical benchmark
```

**Success Criteria:**
- ✅ Canonical benchmark script exists and runs
- ✅ Corpus size explained (96 vs 175 resolved)
- ✅ Single, consistent metric across all papers
- ✅ Independent reproduction possible (documented steps)

---

### Path C: Document Undocumented Components (10-15K tokens)

**Only choose this if yologuard is fixed or being handled separately**

1. Read COMPONENT-INDEX.md (87 components listed)
2. Identify all components with status "⏸️ Prototype" (~40+ components)
3. For each prototype:
   - Grep codebase for usage
   - Either: Document properly OR mark as deprecated
4. Update COMPONENT-INDEX.md with decisions

**Success Criteria:**
- ✅ All 87 components have clear status (✅ Documented or 📚 Deprecated)
- ✅ No ⏸️ Prototype components remaining

---

## Key Documents to Read (On-Demand)

**DO NOT load all into context at once. Read only as needed:**

### Critical for Yologuard Fix:
- papers/IF-armour.md (yologuard section)
- docs/GUARDED-CLAIMS.md (Claim 1)
- code/yologuard/benchmarks/run_leaky_repo_test.py

### Understanding Project Architecture:
- SESSION-ONBOARDING.md - WHY/HOW/WHEN protocol
- COMPONENT-INDEX.md - 87 IF.* components catalog
- agents.md - IF.TTT traceability protocol

### Context from Previous Work:
- SESSION-RESUME.md - Full session history (2025-11-10)
- CLOUD-TRANSITION-PLAN.md - This transition plan
- GEMINI-EVALUATION-PROMPT.md - What Gemini evaluated

### Deep Archives (Use Haiku agents, NEVER read directly):
- papers/*.md - 6 papers (6,078 lines total)
- docs/evidence/ - 102 validation documents
- annexes/ - Complete council debates

---

## Verification Commands

**Before starting work:**
```bash
git status                               # Should be clean
git log --oneline -5                     # Verify latest commits
ls .env                                  # Should NOT exist
grep -r "98.96" papers/                  # Find yologuard claims
python tools/ifctl.py validate --test   # Verify validator works
```

**After yologuard fix:**
```bash
python code/yologuard/benchmarks/canonical_benchmark.py
grep -r "98.96\|96.43" papers/          # Should find consistent metric
git diff                                 # Review changes
```

---

## Security Reminders

⚠️ **NEVER create .env in cloud environment**
⚠️ **NEVER commit credentials to git**
⚠️ **All secrets stay in local environment**
✅ **Cloud reads code/docs from GitHub only**

**Files Gitignored (Safe):**
- .env (contains Google Cloud API key - local only)
- .venv_tools/ (Python virtual environment)
- __pycache__/ (Python bytecode)

**Test Fixtures (Safe - Public Benchmark Data):**
- code/yologuard/benchmarks/leaky-repo/** (Plazmaz/leaky-repo public corpus)
- Allowlisted in .github/secret_scanning.yml

---

## Gemini Evaluation Summary (2025-11-10)

**Scores:**
- Technical Rigor: 3/10 ⚠️ (yologuard unverified, inconsistent metrics)
- Documentation Quality: 2/10 ⚠️ (component index was prose, IF-momentum missing)
- Philosophy Integration: 8/10 ✅ (genuine, not marketing)
- Ethical Foundation: 9/10 ✅ (walks the talk)
- Code Quality (ifctl.py): ✅ VERIFIED

**Critical Findings:**
1. IF.yologuard benchmark UNVERIFIED (55.4% vs claimed 98.96%)
2. COMPONENT-INDEX.md was prose, not functional (now fixed)
3. IF-momentum.md missing (one of 6 core papers)
4. Citation numbering error in InfraFabric.md (now fixed)

**Blocker for External Publication:**
IF.yologuard benchmark must be reproducible before any external claims.

---

## Next Session Should Start By...

**Immediate Next Action:**
Read SESSION-HANDOVER-TO-CLOUD.md (this file), then:

**Path A (RECOMMENDED):** Verify cloud environment works (10 min)
**Then Path B:** Start yologuard benchmark fix (2-3 hours)
**Then Path C:** Document remaining components (as time permits)

**After Each Major Task:**
1. Commit changes to git
2. Push to GitHub
3. Update SESSION-RESUME.md (create if needed)
4. Track token costs (Haiku vs Sonnet ratio)

---

## Philosophy Grounding

**Empiricism (Locke):**
- "Nothing in intellect except what came through senses" → Verify benchmark reproduces

**Verificationism (Vienna Circle):**
- "Meaning = verification method" → Canonical benchmark = verification of claims

**Fallibilism (Peirce):**
- "Make unknowns explicit" → Document corpus discrepancy (96 vs 175)

**Falsifiability (Popper):**
- "Bold claims require severe tests" → Independent reproduction required

**Pragmatism (James-Dewey):**
- "Truth is what works" → Benchmark must run on any machine

---

## Quick Recovery Checklist

If starting fresh in cloud session, verify:

- [ ] Read SESSION-HANDOVER-TO-CLOUD.md (you are here)
- [ ] Checked git log (verify 9ac803a latest)
- [ ] Verified .env NOT present (gitignored)
- [ ] Know current blocker: Yologuard benchmark UNVERIFIED
- [ ] Know token budget: $1000 USD, target 50-80% Haiku
- [ ] Ready to spawn Haiku agents for file reads
- [ ] Know first task: Path A (verify environment) → Path B (yologuard fix)

**If all checked:** Proceed with Path A verification, then Path B yologuard fix.

---

## Meta: Handover Metadata

**Session Start:** First cloud session (TBD)
**Previous Environment:** Local WSL2 (/home/setup/infrafabric)
**Cloud Environment:** Claude Code Web (Anthropic)
**Credits Available:** $1000 USD
**Primary User:** Danny Stocker (dannystocker)

**Quality Metrics (Target):**
- Haiku delegation ratio: 50-80%
- Token efficiency: Measure actual vs claimed 87-90% savings
- Tasks completed per $100: Minimum 10 major tasks

---

## Validation

**Before starting cloud work:**

- [x] Repository pushed to GitHub (9ac803a latest)
- [x] .env confirmed gitignored
- [x] SESSION-HANDOVER-TO-CLOUD.md committed
- [x] Security checklist complete
- [x] Yologuard blocker clearly identified
- [x] Three paths forward specified

**Validation Command (First Cloud Action):**
```bash
git status                               # Should be clean
git log --oneline -3                     # Should show: 9ac803a, c409c74, 876c45f
ls .env 2>&1 | grep "No such file"       # Should confirm .env absent
```

---

**Last Updated:** 2025-11-10T04:30:00Z
**Next Update Due:** After first cloud session starts
**Citation:** if://session/handover-to-cloud-2025-11-10

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
