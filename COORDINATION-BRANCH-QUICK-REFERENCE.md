# Coordination Branch Quick Reference

**For all sessions having trouble accessing coordination branch files**

---

## ⚠️ Common Issue: "Coordination branch not found"

**Problem:** Looking for branch named `coordination` - doesn't exist!

**Solution:** The correct branch name is:
```
claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
```

---

## 🔧 Quick Fix Commands

### For Session 4 (SIP) Specifically:

```bash
# Fetch the CORRECT coordination branch
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Read your instructions
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-4-SIP.md

# Read task board
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:PHASE-0-TASK-BOARD.md
```

### For Any Session:

```bash
# 1. Fetch coordination branch
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# 2. Identify your session
git branch --show-current

# 3. Read appropriate instructions file:
# Session 1: INSTRUCTIONS-SESSION-1-NDI.md
# Session 2: INSTRUCTIONS-SESSION-2-WEBRTC.md
# Session 3: INSTRUCTIONS-SESSION-3-H323.md
# Session 4: INSTRUCTIONS-SESSION-4-SIP.md
# Session 5: INSTRUCTIONS-SESSION-5-CLI.md
# Session 6: INSTRUCTIONS-SESSION-6-TALENT.md
# Session 7: INSTRUCTIONS-SESSION-7-IFBUS.md

git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-{N}-{NAME}.md
```

---

## 🤖 Automated Setup Script

**Easiest method:** Use the setup helper script!

```bash
bash SESSION-SETUP-HELPER.sh
```

This will:
- ✅ Auto-identify which session you are
- ✅ Fetch coordination branch
- ✅ Show your instructions
- ✅ Display task board
- ✅ Give you next steps

---

## 📝 Reading Files from Coordination Branch

### Method 1: git show (Recommended)

```bash
# General pattern:
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:FILENAME

# Examples:
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:WELCOME-TO-INFRAFABRIC.md
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:PHASE-0-TASK-BOARD.md
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:FILLER-TASK-CATALOG.md
```

### Method 2: Checkout coordination branch (Alternative)

```bash
# Save your current work first!
git stash

# Checkout coordination branch
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Read files directly
cat INSTRUCTIONS-SESSION-4-SIP.md
cat PHASE-0-TASK-BOARD.md

# Return to your branch
git checkout -

# Restore your work
git stash pop
```

### Method 3: GitHub Web (If all else fails)

Navigate to:
```
https://github.com/dannystocker/infrafabric/tree/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
```

---

## 🎯 Essential Files to Read (In Order)

1. **WELCOME-TO-INFRAFABRIC.md** - Understand the mission
2. **INSTRUCTIONS-SESSION-{N}-{NAME}.md** - Your specific role
3. **PHASE-0-TASK-BOARD.md** - Available tasks
4. **FILLER-TASK-CATALOG.md** - Backup tasks if blocked

---

## 🆘 Troubleshooting

### "fatal: Invalid object name 'origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy'"

**Fix:**
```bash
# Fetch the branch first
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Try again
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:WELCOME-TO-INFRAFABRIC.md
```

### "fatal: Path 'INSTRUCTIONS-SESSION-X.md' does not exist"

**Check spelling:** File names are case-sensitive!
- Correct: `INSTRUCTIONS-SESSION-4-SIP.md`
- Wrong: `instructions-session-4-sip.md`

**List available files:**
```bash
git ls-tree -r --name-only origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy | grep INSTRUCTIONS
```

### "I'm on branch 'coordination' but files not found"

**Wrong branch!** You need:
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git checkout claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
```

Or stay on your branch and use `git show origin/...`

---

## ⚡ Session-Specific Quick Commands

### Session 1 (NDI):
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-1-NDI.md
```

### Session 2 (WebRTC):
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-2-WEBRTC.md
```

### Session 3 (H.323):
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-3-H323.md
```

### Session 4 (SIP):
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-4-SIP.md
```

### Session 5 (CLI):
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-5-CLI.md
```

### Session 6 (Talent):
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-6-TALENT.md
```

### Session 7 (IF.bus):
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-7-IFBUS.md
```

---

## 📋 File Reference

All files are on coordination branch: `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

**Essential Files:**
- `WELCOME-TO-INFRAFABRIC.md` - Start here!
- `UNIVERSAL-SESSION-START.md` - Universal onboarding
- `SESSION-START-COMMANDS.md` - Session identification
- `PHASE-0-TASK-BOARD.md` - Task assignments
- `FILLER-TASK-CATALOG.md` - Backup tasks
- `PHASE-0-COORDINATION-MATRIX.md` - How sessions coordinate

**Session Instructions:**
- `INSTRUCTIONS-SESSION-1-NDI.md`
- `INSTRUCTIONS-SESSION-2-WEBRTC.md`
- `INSTRUCTIONS-SESSION-3-H323.md`
- `INSTRUCTIONS-SESSION-4-SIP.md`
- `INSTRUCTIONS-SESSION-5-CLI.md`
- `INSTRUCTIONS-SESSION-6-TALENT.md`
- `INSTRUCTIONS-SESSION-7-IFBUS.md`

**Architecture & Design:**
- `S2-CRITICAL-BUGS-AND-FIXES.md` - Why Phase 0 exists
- `SWARM-OF-SWARMS-ARCHITECTURE.md` - Overall architecture
- `reviews/IF-ROADMAP-V1.1-TO-V3.0.md` - Complete vision

---

## ✅ Verification

**After setup, verify you can access files:**

```bash
# Test 1: Can you read welcome?
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:WELCOME-TO-INFRAFABRIC.md | head -20

# Test 2: Can you read your instructions?
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-{YOUR_NUM}-{YOUR_NAME}.md | head -20

# Test 3: Can you see task board?
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:PHASE-0-TASK-BOARD.md | grep "AVAILABLE"
```

If all 3 work: ✅ **You're ready to start!**

---

## 💡 Pro Tips

1. **Bookmark the coordination branch name:**
   ```bash
   export COORD=claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
   git show origin/$COORD:PHASE-0-TASK-BOARD.md
   ```

2. **Create an alias:**
   ```bash
   alias coord='git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:'
   coord PHASE-0-TASK-BOARD.md
   ```

3. **Use tab completion:**
   ```bash
   git show origin/claude/debug-<TAB>  # Auto-completes branch name
   ```

---

## 🚀 Ready to Start?

**Your checklist:**
- ✅ Fetched coordination branch
- ✅ Read welcome message
- ✅ Read your session instructions
- ✅ Read task board
- ✅ Created STATUS file
- ✅ Claimed a 🔵 AVAILABLE task

**Let's build something amazing! 🎉**

---

**Document Version:** 1.0
**Created:** 2025-11-12
**By:** Session 6 (Talent) - Cross-session support
**Purpose:** Help all sessions access coordination branch files

---

*If you're still stuck, check SESSION-SETUP-HELPER.sh or ask for help in your STATUS file!*
