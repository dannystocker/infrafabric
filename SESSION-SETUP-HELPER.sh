#!/bin/bash
# Session Setup Helper - InfraFabric Phase 0
# Helps all sessions identify themselves and access coordination branch files
# Usage: bash SESSION-SETUP-HELPER.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 InfraFabric Session Setup Helper"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# CRITICAL: The coordination branch name
COORD_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

echo ""
echo "Step 1: Fetching coordination branch..."
git fetch origin "$COORD_BRANCH" --quiet 2>/dev/null || {
    echo "⚠️  Warning: Could not fetch coordination branch"
    echo "    Branch: $COORD_BRANCH"
    echo "    Continuing anyway..."
}

echo ""
echo "Step 2: Identifying your session..."
CURRENT_BRANCH=$(git branch --show-current)
echo "    Current branch: $CURRENT_BRANCH"

# Identify session based on branch pattern
if [[ "$CURRENT_BRANCH" == *"ndi-witness-streaming"* ]]; then
    SESSION_NUM=1
    SESSION_NAME="NDI (Witness Streaming)"
    SESSION_FILE="INSTRUCTIONS-SESSION-1-NDI.md"
elif [[ "$CURRENT_BRANCH" == *"webrtc-agent-mesh"* ]]; then
    SESSION_NUM=2
    SESSION_NAME="WebRTC (Agent Mesh)"
    SESSION_FILE="INSTRUCTIONS-SESSION-2-WEBRTC.md"
elif [[ "$CURRENT_BRANCH" == *"h323-guardian-council"* ]]; then
    SESSION_NUM=3
    SESSION_NAME="H.323 (Guardian Council)"
    SESSION_FILE="INSTRUCTIONS-SESSION-3-H323.md"
elif [[ "$CURRENT_BRANCH" == *"sip-escalate-integration"* ]] || [[ "$CURRENT_BRANCH" == *"sip"* ]]; then
    SESSION_NUM=4
    SESSION_NAME="SIP (Escalate Integration)"
    SESSION_FILE="INSTRUCTIONS-SESSION-4-SIP.md"
elif [[ "$CURRENT_BRANCH" == *"cli-witness-optimise"* ]] || [[ "$CURRENT_BRANCH" == *"cli"* ]]; then
    SESSION_NUM=5
    SESSION_NAME="CLI (Witness + Optimise) ⚡ CRITICAL"
    SESSION_FILE="INSTRUCTIONS-SESSION-5-CLI.md"
elif [[ "$CURRENT_BRANCH" == *"if-bus-sip-adapters"* ]] || [[ "$CURRENT_BRANCH" == *"if-bus"* ]]; then
    SESSION_NUM=7
    SESSION_NAME="IF.bus (SIP Adapters)"
    SESSION_FILE="INSTRUCTIONS-SESSION-7-IFBUS.md"
else
    SESSION_NUM=6
    SESSION_NAME="Talent (Standby)"
    SESSION_FILE="INSTRUCTIONS-SESSION-6-TALENT.md"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ You are SESSION $SESSION_NUM: $SESSION_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Step 3: Reading welcome message..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git show "origin/$COORD_BRANCH:WELCOME-TO-INFRAFABRIC.md" 2>/dev/null || {
    echo "⚠️  Could not read WELCOME-TO-INFRAFABRIC.md"
    echo "    Trying alternative method..."
    curl -s "https://raw.githubusercontent.com/dannystocker/infrafabric/$COORD_BRANCH/WELCOME-TO-INFRAFABRIC.md" 2>/dev/null || {
        echo "❌ Failed to read welcome message"
        echo "    Please read manually from coordination branch"
    }
}

echo ""
echo "Step 4: Reading your session-specific instructions..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git show "origin/$COORD_BRANCH:$SESSION_FILE" 2>/dev/null || {
    echo "⚠️  Could not read $SESSION_FILE"
    echo "    Trying alternative method..."
    curl -s "https://raw.githubusercontent.com/dannystocker/infrafabric/$COORD_BRANCH/$SESSION_FILE" 2>/dev/null || {
        echo "❌ Failed to read instructions"
        echo "    Please read manually from coordination branch"
    }
}

echo ""
echo "Step 5: Reading Phase 0 task board..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git show "origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md" 2>/dev/null | head -150 || {
    echo "⚠️  Could not read PHASE-0-TASK-BOARD.md"
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Create your STATUS file: STATUS-SESSION-$SESSION_NUM.yaml"
echo "2. Look for 🔵 AVAILABLE tasks in PHASE-0-TASK-BOARD.md"
echo "3. Claim a task and start working"
echo "4. Update STATUS every 15 minutes"
echo ""
echo "Quick reference:"
echo "  📋 Task Board: git show origin/$COORD_BRANCH:PHASE-0-TASK-BOARD.md"
echo "  📝 Instructions: git show origin/$COORD_BRANCH:$SESSION_FILE"
echo "  🎯 Filler Tasks: git show origin/$COORD_BRANCH:FILLER-TASK-CATALOG.md"
echo ""
echo "Coordination branch: $COORD_BRANCH"
echo ""
echo "Your work is massively appreciated! Let's build something amazing! 🚀"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
