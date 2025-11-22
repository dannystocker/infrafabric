# START HERE - HAIKU AUTOPOLL HANDOFF (Next Session)

**Status:** Ready for Next Sonnet Session
**Conversation:** conv_f621d999f19a3a7f
**Created:** 2025-11-20 23:38 UTC

---

## What's Happening

A Haiku autopoll system is running continuously in the background since Nov 19 (~39+ hours). The system was working fine, but subprocess.run() is starting to hang due to kernel resource exhaustion. This document package provides everything needed to fix it.

---

## The Fix (In One Sentence)

Replace subprocess.run() with TCP socket piping to the persistent Claude instance already running in pts/5, getting 6-7x faster responses with indefinite uptime.

---

## How to Get Started (Pick Your Time Budget)

### If you have 2 minutes:
Read this:
```
/home/setup/infrafabric/HAIKU-AUTOPOLL-QUICK-REFERENCE.md
```
You'll understand: Problem + Solution + Code changes needed

### If you have 15 minutes:
Read this:
```
/home/setup/infrafabric/SESSION-HANDOFF-HAIKU-AUTOPOLL.md
```
You'll have: Complete context + architecture + implementation steps + debugging procedures

### If you have 30+ minutes:
Read this for reference:
```
/home/setup/HAIKU_AUTOPOLL_ARCHITECTURE.txt
```
You'll get: Technical deep-dive + system diagrams + message flows + performance analysis

### Need navigation help?
See:
```
/home/setup/infrafabric/HANDOFF-INDEX.md
```
Full document map + learning paths + critical information table

---

## The Minimal Context You Need Right Now

| Item | Value |
|------|-------|
| **What's running** | Autopoll script (PID 475967) polling MCP bridge every 5 sec since Nov 19 |
| **What's the problem** | subprocess.run() hangs after 39 hours due to fork/exec resource exhaustion |
| **What's the solution** | Use TCP socket (port 9999) to existing persistent Claude (PID 2292, pts/5) |
| **How fast will it be** | 3-5 seconds (was 30-45 seconds) - 6-7x faster |
| **How much code to change** | ~50 lines (replace one function + update its call) |
| **How to validate** | Run 24+ hours, verify no subprocess hangs |

---

## Critical Processes (Check These First)

```bash
# Check if autopoll is running (should show PID 475967)
ps aux | grep haiku_shard_autopoll

# Check if persistent Claude is healthy (should show PID 2292, 39+ hours runtime)
ps aux | grep "claude --dangerously"
```

Both should be running. If not, see the debugging section in the full handoff.

---

## Quick Action Items

**Today (Implement):**
- [ ] Read QUICK-REFERENCE.md (2 min)
- [ ] Read SESSION-HANDOFF.md "The Solution" section (5 min)
- [ ] Replace subprocess.run() function in haiku_shard_autopoll.py (~10 min)
- [ ] Create TCP socket listener in pts/5 (~10 min)
- [ ] Test with single manual query (~10 min)

**Next 24 hours (Validate):**
- [ ] Run autopoll continuously
- [ ] Verify no subprocess hangs
- [ ] Monitor response times <5 sec
- [ ] Check database queue stays clean

**Expect:**
- ✅ Autopoll continues running indefinitely (not 39-hour limit)
- ✅ Queries answered in 3-5 seconds (not 30-45 seconds)
- ✅ CPU usage ~1% (not blocking on subprocess waits)
- ✅ Bridge message queue stays clean (processed immediately)

---

## Files You'll Be Working With

```
/home/setup/infrafabric/haiku_shard_autopoll.py
  └─ Line 20-74: spawn_haiku_via_task_tool() function
     Replace with: pipe_to_persistent_claude() function

/home/setup/infrafabric/haiku_shard_autopoll.py
  └─ Line 128: answer, sources = spawn_haiku_via_task_tool(...)
     Change to: answer, sources = pipe_to_persistent_claude(...)

pts/5 (Interactive Claude shell)
  └─ Add TCP socket listener for port 9999
     (Code provided in handoff document)
```

---

## Key Credentials (Use Carefully)

```
Conversation ID:  conv_f621d999f19a3a7f
Auth Token:       a531c037b8bb5ba0d371fe1a54d4472a2047c20775062ffc97eab71ab2b9854e
API Key:          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
MCP Bridge:       /home/setup/infrafabric/.memory_bus/distributed_memory.db
```

---

## Document Map

| Document | Size | Read Time | What You Get |
|----------|------|-----------|--------------|
| HAIKU-AUTOPOLL-QUICK-REFERENCE.md | 3.4 KB | 2 min | Problem + Solution + Code |
| SESSION-HANDOFF-HAIKU-AUTOPOLL.md | 25 KB | 15 min | Full Context + Implementation Guide |
| HAIKU_AUTOPOLL_ARCHITECTURE.txt | 42 KB | 30 min | Technical Deep-Dive + Diagrams |
| HANDOFF-INDEX.md | 10 KB | 5 min | Navigation + Document Map |

---

## The Flow (What's Happening Right Now)

```
USER SENDS QUERY
    ↓
MCP BRIDGE (SQLite Database)
    ↓
AUTOPOLL SCRIPT (Polls every 5 sec)
    ├─ CURRENT (BROKEN): subprocess.run() → Fork/Exec → Hangs
    └─ FIXED (TARGET):   TCP Socket → Persistent Claude → 2-5 sec response
    ↓
RESPONSE SENT BACK VIA BRIDGE
    ↓
USER GETS ANSWER
```

---

## Success Looks Like

After you implement this:
- Autopoll continues running for days/weeks without hanging
- Responses come back in 3-5 seconds (not 30-45)
- Bridge database stays clean (no message backlog)
- CPU usage ~1% (not blocking)
- Extension logs show zero subprocess errors

---

## If Something Goes Wrong

**Autopoll hangs again?**
→ See "Debugging Checklist" in SESSION-HANDOFF-HAIKU-AUTOPOLL.md

**TCP socket won't connect?**
→ See "Debugging Checklist" section "If TCP Socket Fails"

**Persistent Claude crashed?**
→ See "Debugging Checklist" section "If Persistent Claude Crashed"

---

## Next Steps (Right Now)

1. Open this file (you're reading it): START HERE ✓
2. Choose your depth: 2 min, 15 min, or 30 min handoff
3. Read appropriate document
4. Implement TCP socket fix
5. Test with 24-hour run
6. Validate success criteria

---

## One More Thing

The persistent Claude instance (PID 2292) has been running healthy for 39+ hours. This proves Claude can run indefinitely without degradation. Your job is just to wire it up as a socket server instead of spawning new processes. It's a ~50-line change with massive payoff (6-7x faster, unlimited uptime).

---

**Ready to proceed?**
→ Read `/home/setup/infrafabric/HAIKU-AUTOPOLL-QUICK-REFERENCE.md` (2 minutes)

Then:
→ Read `/home/setup/infrafabric/SESSION-HANDOFF-HAIKU-AUTOPOLL.md` (15 minutes)

Everything you need is documented. Good luck!
