# Session Resume - [DATE]

**Purpose:** Minimal context handoff for new Claude sessions (<2,000 tokens target)

**Last Updated:** [ISO 8601 timestamp]
**Updated By:** [if://agent/name]
**Session ID:** [uuid or identifier]

---

## Current Mission

**Primary Task:** [One sentence: What are we working on RIGHT NOW?]

**Context:** [2-3 sentences: Why this matters, what problem it solves]

**Expected Outcome:** [What success looks like]

---

## Status

**Overall Progress:** [In Progress | Blocked | Awaiting Decision | Completed]

**Progress Indicators:**
- [ ] [Major milestone 1]
- [ ] [Major milestone 2]
- [ ] [Major milestone 3]

**Current Step:** [What specific action is next?]

---

## Git Repository State

**Branch:** `[branch-name]`

**Status:**
```
[Output of: git status --short]
```

**Recent Commits:**
```
[Output of: git log --oneline -5]
```

**Uncommitted Changes:**
- [File path] - [Brief description of changes]
- [File path] - [Brief description of changes]

**Untracked Files (Need Decision):**
- [File path] - [Should commit? Y/N] - [Reason]
- [File path] - [Should commit? Y/N] - [Reason]

---

## Blockers & Dependencies

**Critical Blockers:**
1. [Blocker description] - [Who/what can unblock]
2. [Blocker description] - [Who/what can unblock]

**External Dependencies:**
- [Waiting on user decision about X]
- [Waiting on external validation from Y]
- [Blocked by rate limit / API availability]

**Technical Debt:**
- [Known issue that doesn't block current work but should be addressed]

---

## Decisions Pending User Input

**Decision 1: [Decision name]**
- Question: [What needs to be decided?]
- Options: [A) ... B) ... C) ...]
- Impact: [Why this matters]
- Citation: [if://decision/id if exists]

**Decision 2: [Decision name]**
- Question: [What needs to be decided?]
- Options: [A) ... B) ... C) ...]
- Impact: [Why this matters]
- Citation: [if://decision/id if exists]

---

## Recent Citations Generated

**Session Citations:** `citations/session-[DATE].json`

**Key Citations:**
1. [if://citation/uuid] - [Brief description] - Status: [unverified|verified]
2. [if://citation/uuid] - [Brief description] - Status: [unverified|verified]
3. [if://citation/uuid] - [Brief description] - Status: [unverified|verified]

**Guardian Decisions:**
- [Dossier/Annex reference] - [Topic] - [Approval %] - [if://decision/id]

---

## Token Efficiency Report

**IF.optimise Status:** [⚡ Active | 🧠 Sonnet mode | 🚀 Multi-Haiku | 💤 Disabled]

**This Session:**
- Total tokens consumed: [number]
- Haiku delegation: [number] tokens ([X]% savings)
- Sonnet direct: [number] tokens
- Average cost per task: [number] tokens

**Recommendations for Next Session:**
- [Specific optimization suggestion based on current work]

---

## Context Links (Read Only If Needed)

**DO NOT load these into context unless specifically required:**

**Core Documentation:**
- SESSION-ONBOARDING.md - How to onboard efficiently
- COMPONENT-INDEX.md - Component catalog (read sections on-demand)
- agents.md - Agent traceability protocol

**Domain-Specific:**
- [Link to specific paper section if critical to current task]
- [Link to specific evidence file if critical to current task]
- [Link to specific code file if critical to current task]

**Deep Archives (Access via Haiku agents):**
- papers/*.md - 6 papers (6,078 lines total) - NEVER read directly
- docs/evidence/ - 102 validation documents - Use Task agents
- annexes/ - Complete council debates - Summarize via Haiku

---

## Quick Recovery Checklist

If starting fresh in a new session, verify:

- [ ] Read this SESSION-RESUME.md file (you are here)
- [ ] Checked git status (understand repo state)
- [ ] IF.optimise indicator visible (⚡/🧠/🚀/💤)
- [ ] Did NOT load full papers into context
- [ ] Ready to spawn Haiku agents for research needs
- [ ] TodoWrite tool active (if multi-step task)
- [ ] Know what the current blocker is (if any)
- [ ] Know what user decision is pending (if any)

**If all checked:** Resume work on Current Mission above.

**If blockers exist:** Address blockers before continuing with main task.

---

## Handoff Notes (Session-Specific Context)

**What Worked Well This Session:**
- [Specific success or efficiency gain]
- [Specific success or efficiency gain]

**What To Avoid Next Session:**
- [Specific anti-pattern or mistake]
- [Specific anti-pattern or mistake]

**Discoveries / Insights:**
- [New understanding about the codebase / architecture / problem]
- [New understanding about the codebase / architecture / problem]

**Technical Debt Created:**
- [Shortcuts taken that need cleanup]
- [TODOs left in code that need addressing]

---

## Next Session Should Start By...

**Immediate Next Action:**
[One sentence: Exactly what the next Claude should do first]

**Example:**
"Spawn Haiku agent to read /docs/evidence/philosophy_database_evaluation_2025-11-09.md and summarize the decision rationale."

**Then:**
[Next 2-3 steps in sequence]

---

## Evidence Artifacts Created This Session

**Files Created:**
- [path/to/file.md] - [Purpose] - [Hash: sha256:...]
- [path/to/file.json] - [Purpose] - [Hash: sha256:...]

**Files Modified:**
- [path/to/file.py] - [What changed] - [Hash before] → [Hash after]
- [path/to/file.md] - [What changed] - [Hash before] → [Hash after]

**Git Commits:**
- [commit-sha] - [commit message] - [citation reference if any]
- [commit-sha] - [commit message] - [citation reference if any]

**Test Results:**
- [Test suite name] - [Pass/Fail] - [X/Y passing] - [Report path]

---

## Guardian Council Activity

**Deliberations This Session:**
- [Dossier/Topic] - [Status: proposed | in-review | decided]
- [Vote tally if decided: X/20 approved, dissent recorded]
- [Citation: if://decision/id]

**Pending Guardian Review:**
- [Topic awaiting council review]
- [Expected timeline for review]

---

## Meta: Session Metadata

**Session Start:** [ISO 8601 timestamp]
**Session End:** [ISO 8601 timestamp]
**Duration:** [X hours Y minutes]
**Claude Model:** [claude-sonnet-4.5 | claude-haiku-4.5 | mixed]
**Haiku Agents Spawned:** [Number]
**Primary User:** [username]

**Quality Metrics:**
- Citations generated: [number]
- Citations verified: [number]
- Token efficiency: [X]% better than baseline
- User interventions required: [number]

---

## Template Usage Instructions

**When to create SESSION-RESUME.md:**
1. End of major work session (before long break)
2. Context approaching 150K tokens (preemptive handoff)
3. Major milestone completed (release, architecture decision)
4. User types `/resume` command
5. About to switch from Sonnet to Haiku (context handoff)

**How to update SESSION-RESUME.md:**
1. Copy this template to `SESSION-RESUME.md`
2. Replace all `[PLACEHOLDERS]` with actual values
3. Delete sections that don't apply (mark as "N/A" if unsure)
4. Keep file under 2,000 tokens (aggressive editing)
5. Link to deep evidence rather than embedding it
6. Commit with citation reference in message

**How to use SESSION-RESUME.md (next session):**
1. Read ONLY this file (not full papers)
2. Follow "Quick Recovery Checklist" above
3. Execute "Immediate Next Action"
4. Refer to COMPONENT-INDEX.md for on-demand context
5. Spawn Haiku agents for deep research
6. Update this file as work progresses

---

## Validation

**Before committing this SESSION-RESUME.md:**

- [ ] File is under 2,000 tokens (use `wc -w` and divide by 0.75)
- [ ] All git commands output included (status, log, diff)
- [ ] All blockers clearly identified
- [ ] All pending decisions listed with options
- [ ] Citations list is complete and validated
- [ ] Token costs measured and reported
- [ ] Immediate next action is specific and actionable
- [ ] Evidence artifacts have hashes for verification

**Validation Command:**
```bash
# Check token count (approximate)
wc -w SESSION-RESUME.md
# Should be < 1500 words (≈ 2000 tokens)

# Validate citations
python tools/citation_validate.py citations/session-[DATE].json

# Verify git state matches documentation
git status
git log --oneline -5
```

---

**Last Updated:** [UPDATE THIS TIMESTAMP]
**Next Update Due:** [When next major milestone expected]
