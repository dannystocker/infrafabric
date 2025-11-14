# 🛡️ How to Prevent Future Session Stalls

**Purpose:** Design patterns and checklist to prevent coordination breakdowns
**Target Audience:** Orchestrator sessions creating multi-agent prompts
**Last Updated:** 2025-11-14 09:00 UTC

---

## 🎯 The Core Problem

When you create a "universal prompt" for multiple sessions, you're building a **distributed coordination system**. If the infrastructure doesn't exist, sessions will silently fail.

**What happened this time:**
- Created UNIVERSAL-SESSION-PROMPT.md (coordination logic)
- But didn't create SESSION-STATUS.md (the data it reads)
- Sessions read prompt → looked for status → found nothing → waited forever

**The fix:**
- Create the STATUS file BEFORE sending the prompt
- Use actual data structures, not prose descriptions
- Test with one session before deploying to all

---

## ✅ PREVENTION CHECKLIST

Use this BEFORE sending any multi-session coordination prompt:

### 1. Infrastructure First, Prompts Second

```bash
# DO THIS ORDER:
1. Create SESSION-STATUS.md (or equivalent status file)
2. Populate with UNCLAIMED sessions
3. Commit and push status file
4. THEN create UNIVERSAL-SESSION-PROMPT.md
5. Test prompt with ONE session first
6. Only after verified working → send to all sessions
```

**Anti-pattern:** Writing a prompt that references files that don't exist yet.

**Correct pattern:** Creating all infrastructure files first, then writing prompts that use them.

---

### 2. Status File Design Pattern

Every multi-session coordination needs a **central status file** with this structure:

```markdown
# SESSION-STATUS.md

## Session [ID]: [Name]
- Status: [UNCLAIMED | CLAIMED | IN_PROGRESS | COMPLETE | BLOCKED | ERROR]
- Claimed By: [UNCLAIMED | CLAIMED-timestamp-pid]
- Repository: [dannystocker/repo-name]
- Branch: [branch-name or pattern]
- Output File: [where to write results]
- Mission File: [detailed instructions file] (if applicable)
- Expected Completion: [timestamp]
```

**Critical fields:**
1. **Status** - Must use consistent keywords (not prose)
2. **Claimed By** - Atomic claim mechanism
3. **Repository** - Prevents wrong-repo commits
4. **Output File** - Explicit deliverable location

**Why this works:**
- Grepable (scripts can parse it)
- Atomic updates (one field at a time)
- Self-documenting (humans can read it)
- Version controlled (git tracks all changes)

---

### 3. Atomic Claim Mechanism

Sessions must be able to claim work WITHOUT human intervention:

```bash
# GOOD: Atomic claim with immediate commit
git pull
sed -i "s/Session X.*UNCLAIMED/Session X: CLAIMED-$(date +%s)/" SESSION-STATUS.md
git add SESSION-STATUS.md
git commit -m "claim: Session X"
git push

# Check for conflicts
if [ $? -ne 0 ]; then
  # Another session won the race
  git pull --rebase
  # Try next UNCLAIMED session
fi
```

**BAD: Non-atomic claims**
```bash
# This creates race conditions:
echo "I want Session 2" > /tmp/claim.txt
# Wait for orchestrator to assign...
# Multiple sessions claim same work
```

**Why atomic matters:**
- Multiple sessions can safely run in parallel
- First to push wins
- Losers automatically retry with next available
- No deadlocks or duplicate work

---

### 4. Repository Confusion Prevention

**Always include repository verification in prompts:**

```bash
# START OF EVERY PROMPT:
echo "=== REPOSITORY CHECK ==="
git remote -v
CURRENT_REPO=$(git remote get-url origin | grep -o '[^/]*$' | sed 's/.git//')
echo "Current repository: $CURRENT_REPO"

# THEN: Read assignment from SESSION-STATUS.md
TARGET_REPO=$(grep -A 5 "^### Session $MY_SESSION" SESSION-STATUS.md | grep "Repository:" | cut -d'/' -f2)

if [ "$CURRENT_REPO" != "$TARGET_REPO" ]; then
  echo "ERROR: Wrong repository!"
  echo "  Current: $CURRENT_REPO"
  echo "  Expected: $TARGET_REPO"
  echo "  Switching..."
  # [switching logic here]
fi
```

**Why this matters:**
- Most common source of "where did my commits go?" confusion
- Prevents wasted work in wrong repo
- Catches errors before they happen

---

### 5. Error Handling with Recovery

**Every step in a multi-session prompt should have error handling:**

```bash
# PATTERN:
command_that_might_fail
if [ $? -ne 0 ]; then
  echo "ERROR: [what failed]" >> BLOCKERS.md
  echo "Attempted: [what you tried]" >> BLOCKERS.md
  echo "Expected: [what should have happened]" >> BLOCKERS.md
  git add BLOCKERS.md
  git commit -m "blocker: [short description]"
  git push

  # THEN: Either recover or fail gracefully
  echo "Attempting recovery: [recovery strategy]"
  # [recovery logic]
fi
```

**Anti-pattern:**
```bash
# This silently fails:
cd /some/directory
git clone repo  # Might fail if already exists
cd repo         # Now you're in wrong directory!
```

**Correct pattern:**
```bash
cd /some/directory
if [ ! -d "repo" ]; then
  git clone repo
  if [ $? -ne 0 ]; then
    echo "BLOCKER: Clone failed" >> BLOCKERS.md
    exit 1
  fi
fi
cd repo
pwd  # Verify you're in right place
```

---

### 6. Single Source of Truth

**Problem:** Multiple status files with conflicting information

This happened with:
- SESSION-HANDOVER-PROTOCOL.md (Nov 14, talks about Session 1)
- TASK-ASSIGNMENTS-ALL-SESSIONS.md (Nov 12, talks about Phase 0 Sessions 1-7)
- NAVIDOCS-STATUS.md (Nov 14, talks about NaviDocs swarms)
- UNIVERSAL-SESSION-PROMPT.md (Nov 14, expects different format)

**Solution:** One status file, updated in real-time

```bash
# RULE: Only ONE file tracks session status
SESSION-STATUS.md  # This is the source of truth

# All other files can REFERENCE it:
PHASE-0-WORK.md → "See SESSION-STATUS.md for Session 1-7 status"
NAVIDOCS-WORK.md → "See SESSION-STATUS.md for NaviDocs swarm status"
```

**Why this matters:**
- No conflicting information
- Easy to find current status (check one file)
- Updates are atomic (one file, one commit)

---

### 7. Test with One Session First

**Before sending prompt to 7 sessions:**

```bash
# 1. Paste prompt to ONE test session
# 2. Watch what it does:
#    - Does it claim work correctly?
#    - Does it find all files it needs?
#    - Does it commit to right repository?
#    - Does it update status when done?
# 3. If test succeeds → send to remaining sessions
# 4. If test fails → fix prompt and retry
```

**Why this matters:**
- Catch bugs before they multiply by 7x
- Faster iteration (fix → test → fix vs fix → deploy 7 → wait → realize broken)
- Lower cost (1 Haiku test vs 7 Haiku sessions)

---

### 8. Explicit Fallback Behavior

**Every prompt needs to answer: "What if no work is available?"**

```markdown
# GOOD:
If no UNCLAIMED sessions found:
1. Check if any CLAIMED sessions are stale (>2 hours, no commits)
2. If yes, reset them to UNCLAIMED and retry
3. If no, check NaviDocs swarms
4. If none available, wait 30 minutes and check again
5. After 3 retries, create BLOCKER and wait for human

# BAD:
If no sessions found: Wait.  # Wait forever? Wait how long? Silent or report?
```

**Why explicit matters:**
- Sessions know what to do when blocked
- No silent infinite waits
- Clear escalation path to human

---

## 📋 PRE-DEPLOYMENT CHECKLIST

Use this before sending ANY multi-session coordination prompt:

```markdown
## Infrastructure
- [ ] Status file exists (SESSION-STATUS.md or equivalent)
- [ ] Status file has consistent format (Status: UNCLAIMED/CLAIMED/COMPLETE)
- [ ] Status file includes repository field for each session
- [ ] Status file includes output file field for each session
- [ ] Status file committed and pushed to remote

## Claiming Mechanism
- [ ] Prompt includes atomic claim logic (pull → edit → commit → push)
- [ ] Prompt handles claim conflicts (another session won race)
- [ ] Prompt verifies claim succeeded before starting work
- [ ] Claimed sessions update status to IN_PROGRESS

## Repository Handling
- [ ] Prompt checks current repository before work
- [ ] Prompt reads target repository from status file
- [ ] Prompt switches repositories if needed
- [ ] Prompt verifies switch succeeded

## Error Handling
- [ ] Every command has error check (if [ $? -ne 0 ])
- [ ] Errors are logged to BLOCKERS.md
- [ ] Errors trigger recovery attempts
- [ ] Fatal errors stop execution (don't continue after failure)

## Validation
- [ ] Tested prompt with ONE session first
- [ ] Test session successfully claimed work
- [ ] Test session successfully completed work
- [ ] Test session successfully updated status to COMPLETE
- [ ] No blockers created during test

## Fallback Behavior
- [ ] Prompt defines what to do if no work available
- [ ] Prompt defines timeout for waiting (not infinite)
- [ ] Prompt defines escalation path (when to create blocker)
- [ ] Prompt includes "All complete" success message

## Documentation
- [ ] Status file location documented in prompt
- [ ] Expected timeline documented (T+5min agents deploy, T+4h complete)
- [ ] Monitoring commands provided (how to check progress)
- [ ] Troubleshooting guide included (what if X fails)
```

**Only after ALL checkboxes are ✅ should you deploy to all sessions.**

---

## 🔍 MONITORING PATTERN

After deploying a multi-session prompt, monitor with:

```bash
# 1. Check claims (should see within 2 minutes)
watch -n 60 'git pull -q && grep "Claimed By:" SESSION-STATUS.md'

# 2. Check commits (should see within 10 minutes)
watch -n 60 'git fetch --all -q && git log --all --oneline --since="10 minutes ago"'

# 3. Check blockers (should stay empty)
watch -n 60 'git pull -q && cat BLOCKERS.md 2>/dev/null | tail -20'

# 4. Check progress (status should advance)
watch -n 300 'git pull -q && grep "Status:" SESSION-STATUS.md'
```

**Red flags:**
- 🚩 No claims after 5 minutes → Prompt not reaching sessions or auto-detect broken
- 🚩 Claims but no commits after 15 minutes → Sessions stalled after claiming
- 🚩 BLOCKERS.md filling up → Systematic error (bad prompt or missing dependency)
- 🚩 Status not changing after 1 hour → Sessions claiming but not executing

**Green flags:**
- ✅ Claims within 2 minutes
- ✅ Commits from multiple branches within 10 minutes
- ✅ BLOCKERS.md stays empty or has resolved entries
- ✅ Status progresses UNCLAIMED → CLAIMED → IN_PROGRESS → COMPLETE

---

## 🎓 LESSONS FROM THIS INCIDENT

### What Went Wrong
1. Created prompt referencing status format that didn't exist
2. Multiple conflicting status files (3 projects in one repo)
3. No atomic claim mechanism (prose instructions, not bash code)
4. No fallback behavior (sessions just "wait" indefinitely)
5. No pre-deployment test (sent to 7 sessions without validating)

### What Went Right
1. Comprehensive documentation (easy to diagnose)
2. Git-based coordination (all history visible)
3. IF.TTT compliance (traceable, transparent, trustworthy)
4. Clear separation of concerns (different branches for different work)

### Key Takeaway
**Infrastructure before instructions.**

Build the status system, THEN build the coordination prompt.
Test with one session, THEN deploy to all.

---

## 📚 REFERENCE: GOOD vs BAD PROMPTS

### ❌ BAD Multi-Session Prompt

```markdown
You are Session X. Read the coordination doc and figure out what to do.

ASSIGNMENT LOGIC:
- If you're Session 2, do cloud APIs
- If you're Session 3, do SIP APIs
- If no work, wait

Check SESSION-HANDOVER-PROTOCOL.md for details.
```

**Problems:**
- No actual status check (just prose)
- No claiming mechanism
- No repository verification
- No error handling
- No fallback timeout
- No validation

### ✅ GOOD Multi-Session Prompt

```markdown
You are an autonomous session. Run these commands to find and claim your work:

# 1. Get latest status
cd /home/user/infrafabric
git checkout claude/coordination-branch
git pull origin claude/coordination-branch

# 2. Find available work
AVAILABLE=$(grep -n "Status: UNCLAIMED" SESSION-STATUS.md | head -1 | cut -d: -f1)
if [ -z "$AVAILABLE" ]; then
  echo "No work available"
  # [explicit fallback here]
  exit 0
fi

# 3. Claim work atomically
SESSION_NAME=$(sed -n "${AVAILABLE}p" SESSION-STATUS.md)
CLAIM_ID="CLAIMED-$(date +%s)"
sed -i "${AVAILABLE}s/UNCLAIMED/$CLAIM_ID/" SESSION-STATUS.md
git add SESSION-STATUS.md && git commit -m "claim: $SESSION_NAME" && git push

# 4. Verify claim (check for conflicts)
if [ $? -ne 0 ]; then
  echo "Claim conflict, retrying..."
  git pull --rebase
  # [retry logic here]
fi

# 5. Read assignment details
TARGET_REPO=$(sed -n "${AVAILABLE},/^###/p" SESSION-STATUS.md | grep "Repository:" | cut -d: -f2)
OUTPUT_FILE=$(sed -n "${AVAILABLE},/^###/p" SESSION-STATUS.md | grep "Output File:" | cut -d: -f2)

# 6. Verify repository
CURRENT_REPO=$(git remote get-url origin)
if [[ ! "$CURRENT_REPO" =~ "$TARGET_REPO" ]]; then
  echo "Wrong repo, switching..."
  # [repo switch logic with error handling]
fi

# 7. Execute work
# [actual work here]

# 8. Update status on completion
sed -i "${AVAILABLE}s/Status: CLAIMED/Status: COMPLETE/" SESSION-STATUS.md
git add SESSION-STATUS.md && git commit -m "complete: $SESSION_NAME" && git push
```

**Why this is better:**
- Actual bash commands (not prose)
- Atomic claiming with conflict detection
- Repository verification before work
- Error handling at each step
- Explicit completion tracking
- Testable (can run manually to verify)

---

## 🚀 FUTURE IMPROVEMENTS

### 1. Real-Time Coordination (IF.notify)
Instead of git polling, use pub/sub:
```bash
# When session claims work:
curl -X POST http://if-notify/claim \
  -d '{"session": "Session 2", "status": "CLAIMED"}'

# Orchestrator subscribes:
curl http://if-notify/subscribe/claims
# Receives real-time updates
```

### 2. Health Checks
Sessions should heartbeat:
```bash
# Every 5 minutes while working:
sed -i "s/Last Heartbeat:.*/Last Heartbeat: $(date -u +%s)/" SESSION-STATUS.md
git add SESSION-STATUS.md && git commit -m "heartbeat" && git push

# Orchestrator detects stalls:
STALE=$(grep "Last Heartbeat:" SESSION-STATUS.md | \
  awk -v now=$(date +%s) '{if (now - $3 > 600) print $0}')
# Reset stale sessions to UNCLAIMED
```

### 3. Dependency Graphs
For complex workflows:
```yaml
# DEPENDENCIES.yaml
Session3_Integration:
  depends_on:
    - Session1_Backend: "checkpoint_1_complete"
    - Session2_Frontend: "checkpoint_1_complete"
  blocks_until: ["Session1_Backend", "Session2_Frontend"]
```

### 4. Cost Tracking
Track agent costs in status:
```bash
AGENTS_USED=$(grep "Task tool" session.log | wc -l)
ESTIMATED_COST=$(echo "$AGENTS_USED * 0.25" | bc)
sed -i "s/Cost:.*/Cost: \$$ESTIMATED_COST/" SESSION-STATUS.md
```

---

## ✅ SUCCESS CRITERIA

You'll know you've prevented future stalls when:

1. **Status file exists before prompts sent** ✅
2. **One session claims and completes successfully** ✅
3. **All 7 sessions deployed, all claim work within 5 minutes** ✅
4. **No BLOCKERS.md entries for coordination issues** ✅
5. **Monitoring shows steady progress every hour** ✅
6. **All sessions complete within expected timeline** ✅
7. **No "where did my commits go?" questions** ✅

---

**Remember:** Multi-agent coordination is distributed systems engineering. Apply the same rigor you'd apply to a production microservices architecture.

- Design for failure
- Make operations atomic
- Monitor everything
- Test before deploying
- Document explicitly
- Fail gracefully

**Your future self (and your sessions) will thank you.** 🙏
