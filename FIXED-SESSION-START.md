# FIXED Session Start - Paste This Into All Sessions

**Copy this ENTIRE block into each Claude Code session:**

```bash
# Step 1: Fetch the coordination branch (has all instructions)
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Step 2: Read the welcome message
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:WELCOME-TO-INFRAFABRIC.md

# Step 3: Identify which session you are
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Identifying your session..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" == *"ndi-witness-streaming"* ]]; then
    SESSION_NUM=1
    SESSION_NAME="NDI - Documentation & Witness"
elif [[ "$CURRENT_BRANCH" == *"webrtc-agent-mesh"* ]]; then
    SESSION_NUM=2
    SESSION_NAME="WebRTC - Documentation & Test Support"
elif [[ "$CURRENT_BRANCH" == *"h323-guardian-council"* ]]; then
    SESSION_NUM=3
    SESSION_NAME="H.323 - Documentation & MCU Support"
elif [[ "$CURRENT_BRANCH" == *"sip-escalate-integration"* ]]; then
    SESSION_NUM=4
    SESSION_NAME="SIP - Integration Testing & Security"
elif [[ "$CURRENT_BRANCH" == *"cli-witness-optimise"* ]]; then
    SESSION_NUM=5
    SESSION_NAME="CLI - Foundation & Infrastructure ⚡ CRITICAL"
elif [[ "$CURRENT_BRANCH" == *"if-bus-sip-adapters"* ]]; then
    SESSION_NUM=7
    SESSION_NAME="IF.bus - Core Component Implementation"
else
    SESSION_NUM=6
    SESSION_NAME="Talent - Reserved for Phase 1"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ You are SESSION $SESSION_NUM ($SESSION_NAME)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 4: Read your session-specific instructions
echo "Reading your instructions..."
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-$SESSION_NUM-*.md 2>/dev/null || \
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-${SESSION_NUM}*.md 2>/dev/null

# Step 5: Show the task board
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checking Phase 0 Task Board..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:PHASE-0-TASK-BOARD.md | grep "Session $SESSION_NUM" -A 5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete! You are SESSION $SESSION_NUM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Create your STATUS file: STATUS-SESSION-$SESSION_NUM.yaml"
echo "2. Claim your first available task from the task board"
echo "3. Execute following the acceptance criteria"
echo "4. Update progress every 15 minutes"
echo ""
echo "Coordination branch: claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"
echo "Your work is massively appreciated! 🚀"
```

---

## Why This Works

✅ **Works from ANY branch** - uses `git show origin/...` to read files
✅ **Auto-identifies session** - checks branch name pattern
✅ **No GitHub links needed** - reads directly from git
✅ **Shows relevant info only** - filters task board for your session
✅ **Clear next steps** - tells you exactly what to do

---

## Manual Alternative (If Script Fails)

If the bash script doesn't work, paste this into the Claude session:

```
Please help me get started with InfraFabric Phase 0.

Step 1: Run this command and tell me the output:
git branch --show-current

Step 2: Based on my branch name, fetch and read my instructions:
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

Step 3: Read the welcome message:
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:WELCOME-TO-INFRAFABRIC.md

Step 4: Help me identify which session I am and what tasks I should work on.
```

---

## For Session 4 (SIP) Specifically

The SIP session is looking for a "coordination" branch that doesn't exist.

**Correct branch name:** `claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy`

Tell Session 4 to run:
```bash
git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-4-SIP.md
```
