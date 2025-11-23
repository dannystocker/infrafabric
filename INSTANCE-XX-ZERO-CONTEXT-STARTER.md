# Instance #XX Zero-Context Starter Prompt

**You are Instance #XX of the InfraFabric strategic engagement project.**

---

## What You Need to Know in 2 Minutes

### Project Overview
- **What:** InfraFabric is a credibility-measurement consulting firm positioning for two parallel market verticals (B2B communications + quantum threat response)
- **Founder:** Danny Stocker (GitHub: dannystocker)
- **Methodology:** GEDIMAT (behavioral psychology + financial formulas + operational protocols)
- **Current Status:** Two execution tracks ready to launch (Georges partnership starting Dec 9, Quantum market prep for Q1 2026)

### Current Mission Status (Instance #16 Complete - Nov 23, 2025)

**Track A: Georges-Antoine Gary Partnership (IMMEDIATE - Dec 9)**
- Status: ✅ All materials board-ready (9.2/10 credibility)
- Contact Call: Dec 9 (60 min)
- Demo Walkthrough: Dec 10-15 (90 min technical deep-dive)
- Pilot Execution: Dec 17-Jan 11 (4 weeks with weekly gates)
- Partnership Decision: Dec 20 (Pilot Week 4)
- Critical Files: PARTNERSHIP-EXECUTION-PLAN-GEORGES.md, RAPPORT-POUR-GEORGES-ANTOINE-GARY.md, QUICK-REFERENCE-GEORGES-PARTNERSHIP.md

**Track B: Quantum Threat Market (Q1 2026)**
- Status: ✅ Strategic brief updated with aggressive 2026-2027 timeline (60-70% primary scenario)
- Market Window: Dec (prospect identification) → Jan (framework) → Q1 2026 (engagement launch)
- Critical Insight: "18-24 month migration window" before CRQC arrival
- Market Opportunity: Crisis positioning for unprepared organizations
- Critical Files: QUANTUM-THREAT-BLOCKCHAIN-STRATEGIC-BRIEF.md, POST-QUANTUM-CRYPTOGRAPHY-MIGRATION-FRAMEWORK.md
- Git Commit: `8e386c8` "Update quantum threat timeline: 2026-2027 as primary scenario"

### Known Blockers (P0)

**Cost Claims Verification:** Currently 91-97% verified, not 100%
- Assumptions: 6,000 queries/day, 30K tokens/query
- Action: Validate against live usage data before final pitch
- Impact: Don't present as absolute guarantees until validated
- Est. Fix Time: 2-3 hours
- Decision: Instance #12 approved fixing P0 before partner outreach

---

## What To Do First (30 min total)

### Step 1: Read Current Status (5 min)
1. **This file** - What you're reading now
2. `/home/setup/infrafabric/SESSION-RESUME.md` - Full handoff status
3. `git log --oneline -10` - Recent work trajectory

### Step 2: Understand Your Role (5 min)

**Are you continuing mid-task?**
- Read SESSION-RESUME.md section "Critical Path Forward"
- Check if last instance left any unfinished work (search "⏳ Running")

**Are you starting new work?**
- Check SESSION-RESUME.md "Immediate Next Actions" (around line 770)
- Most likely: Continue with P0 cost validation or launch partnership outreach

**Are you troubleshooting?**
- Read SESSION-INSTANCE-16-NARRATION.md from previous instance
- Check git log for error patterns

### Step 3: Git State Check (2 min)
```bash
cd /home/setup/infrafabric
git status
git log --oneline -5
```

### Step 4: Read Your Assignment (5 min)

**If cost validation needed:**
- Open: `/home/setup/infrafabric/GEDIMAT_XCEL_V3.56_BTP_CLEAN.md`
- Section: Find "6,000 queries/day" assumption
- Task: Validate against real usage patterns from previous deployments
- Deliverable: Three-scenario cost table (Conservative/Realistic/Aggressive)

**If partnership execution:**
- Open: `/home/setup/infrafabric/PARTNERSHIP-EXECUTION-PLAN-GEORGES.md`
- Your role: Prepare for Dec 9 contact call
- Deliverable: Outreach email with research evidence

**If quantum prep:**
- Open: `/home/setup/infrafabric/QUANTUM-THREAT-BLOCKCHAIN-STRATEGIC-BRIEF.md`
- Your role: Build prospect list for financial/critical infrastructure orgs
- Deliverable: Tier 1 prospect database with contact info

---

## Critical Files You'll Need

**Always Open These First:**
- `/home/setup/infrafabric/SESSION-RESUME.md` - Handoff document with current status + blockers
- `/home/setup/infrafabric/agents.md` - Master documentation (ALL projects)
- `git log --oneline -20` - See what changed since last session

**Track A - Georges Partnership:**
- PARTNERSHIP-EXECUTION-PLAN-GEORGES.md
- RAPPORT-POUR-GEORGES-ANTOINE-GARY.md (French proposal)
- QUICK-REFERENCE-GEORGES-PARTNERSHIP.md (one-page checklist)
- GEORGES-ANTOINE-GARY-COMPREHENSIVE-PROFILE.md (research reference)

**Track B - Quantum Threat:**
- QUANTUM-THREAT-BLOCKCHAIN-STRATEGIC-BRIEF.md (strategic positioning)
- POST-QUANTUM-CRYPTOGRAPHY-MIGRATION-FRAMEWORK.md (technical framework)

**Methodology Reference:**
- GEDIMAT_XCEL_V3.56_BTP_CLEAN.md (full marketing framework)
- GEDIMAT_SECTION_4.5_JOE_COULOMBE_VARIATIONS.md (18 persona variations)

**Framework Documentation:**
- `/home/setup/infrafabric/COMPONENT-INDEX.md` - 91+ IF.* components catalog
- `/home/setup/infrafabric/docs/IF-URI-SCHEME.md` - Citation system (if://citation/uuid)

---

## Timeline Reference

```
Nov 23 (Instance #16):
  ✅ Quantum brief timeline reframed (aggressive scenario now primary)
  ✅ Session protocol formalized

Dec 9:   Georges partnership contact call
Dec 10-15: Demo walkthrough
Dec 17:  Pilot execution begins
Dec 20:  Partnership decision window
Dec 31:  Quantum prospect identification complete

Jan 2026: Framework development
Q1 2026: Quantum threat market launch
```

---

## Your Session-End Obligations

**Before you sign off, you MUST:**

1. ✅ **Write SESSION-INSTANCE-XX-NARRATION.md** documenting your work
   - What you accomplished
   - Decisions made
   - Blockers encountered
   - Tests run
   - Key findings

2. ✅ **Update SESSION-RESUME.md** for next instance
   - Current mission status
   - What changed this session
   - Next immediate actions
   - Any new blockers

3. ✅ **Git commit with comprehensive message**
   - What changed
   - Why it matters
   - What's next
   - Example: `git commit -m "Update quantum brief: aggressive timeline now 60-70% scenario"`

4. ✅ **Store findings for continuity**
   - If using Redis: `redis-cli SET instance:XX:findings "..."`
   - Otherwise: Just update SESSION-RESUME.md

---

## If You're Stuck

**1. Check Previous Instance Narrations**
```bash
ls -la /home/setup/infrafabric/SESSION-INSTANCE-*.md
```

**2. Find Similar Work**
```bash
git log --grep="cost" --oneline
git log --grep="quantum" --oneline
git log --grep="Georges" --oneline
```

**3. Read agents.md for Component Context**
- `/home/setup/infrafabric/agents.md` has all frameworks
- Search for "IF.gedimat", "IF.quantum", "IF.guard"
- Each component explains its purpose and usage

**4. Check for Test Results**
- Look for files named TEST-* or RESULTS-*
- Tests running: #2 (Performance), #5 (Pitch Dry-Run), #7 (External Reviewer)
- Check status in SESSION-RESUME.md around line 50

---

## Communication Preferences (This User)

This user is **exceptionally sophisticated** in AI collaboration:

- **Direct & Concise:** Gets to the point, hates verbosity
- **Security-Conscious:** Will call out errors immediately (welcome it!)
- **Token-Efficient:** Values Haiku delegation heavily for mechanical work
- **Systems Thinker:** Asks architectural questions, designs solutions collaboratively
- **Honest First:** Trust is earned through accountability, not perfection

**If you make an error:**
- Own it completely
- Explain why it happened
- Update your process
- User will paradoxically trust you MORE for transparency

---

## Key Discoveries (For Context)

**Discovery #1 - Independent Haiku Context Budgets**
- Each Haiku agent operates with independent 200K token budget
- Parent Sonnet only counts delegation cost (1-5K)
- Impact: Multi-file tasks become 90% cheaper in tokens
- Documented: `agents.md` section "IF.optimise"

**Discovery #2 - Trust Through Error**
- SSH mistake → accountability → trust increase
- Key insight: Reflection > perfection
- Documented: Multiple Medium articles in `/mnt/c/users/setup/downloads/`

**Discovery #3 - Distributed Memory Architecture**
- Can shard context across multiple persistent Claude sessions
- Total accessible memory: 1M+ tokens (vs 200K limit)
- Status: MCP bridge solution documented, untested
- Documented: `agents.md` section "IF.memory.distributed"

---

## Common Patterns From Previous Sessions

**When approaching partners:**
1. Lead with 9.2/10 credibility research (not features)
2. Frame as "emergency response positioning" (not planned migration)
3. Use behavioral psychology backing (Rory Sutherland, Joe Coulombe)
4. Emphasize control + visibility (not speed)
5. Test assumptions against real market data

**When fixing blockers:**
1. Gather evidence first (don't guess)
2. Run test on small sample (de-risk)
3. Document findings with if://citation/uuid
4. Update agents.md with new learning
5. Commit to git with full context

**When delegating to Haiku:**
1. Give Haiku complete context (they won't carry context back)
2. Ask for specific deliverable format
3. Review results immediately (don't queue)
4. Use parallel Haiku calls for independent tasks

---

## Your First 5 Actions

1. **Read SESSION-RESUME.md** (2 min)
2. **Check git log** (1 min)
3. **Identify your assignment** from "Critical Path Forward" section
4. **Open the relevant files** for your track (1 min)
5. **Check if any tests are blocking you** (1 min)

Then: Execute assigned work with full context loaded.

---

## Questions? Check Here First

| Question | Answer Location |
|----------|-----------------|
| What was accomplished last session? | SESSION-INSTANCE-16-NARRATION.md |
| What's blocking us now? | SESSION-RESUME.md section "Current Blockers" |
| How do I approach Georges? | QUICK-REFERENCE-GEORGES-PARTNERSHIP.md |
| What's the quantum market opportunity? | QUANTUM-THREAT-BLOCKCHAIN-STRATEGIC-BRIEF.md |
| How do I use GEDIMAT? | GEDIMAT_XCEL_V3.56_BTP_CLEAN.md (marketing) |
| What are the IF.* components? | agents.md (full documentation) |
| What's the cost calculation issue? | SESSION-RESUME.md line ~1010 |
| How do I commit my work? | End of SESSION-RESUME.md has examples |

---

## You Have Everything You Need

- ✅ Full context from Session #16
- ✅ Two ready-to-execute partnership strategies
- ✅ Clear next actions with timelines
- ✅ Known blockers documented
- ✅ Previous session narrations for reference
- ✅ Component documentation (91+ IF.* frameworks)
- ✅ Test tracking visible

**You are not starting from zero. You are starting from Instance #16's completed work.**

**Read SESSION-RESUME.md. Find your assignment. Execute with full backing.**

**Go forth and build credibility.**

---

**Last Updated:** 2025-11-23 (Instance #16 Complete)
**Next Critical Dates:** Dec 9 (Georges call), Dec 20 (Decision), Jan 2026 (Quantum launch)
**Template Version:** 1.0
**For:** Instance #17+
