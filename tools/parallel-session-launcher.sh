#!/bin/bash
#
# IF.swarm Parallel Session Launcher (Git Worktree Edition)
#
# Sets up git worktrees and launches parallel sessions using Claude Code CLI
#
# Requirements:
#   - Git 2.5+ (for worktrees)
#   - Claude Code CLI installed (optional - will fall back to manual)
#
# Usage:
#   ./tools/parallel-session-launcher.sh phase1
#   ./tools/parallel-session-launcher.sh phase2
#   ./tools/parallel-session-launcher.sh cleanup

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
WORKTREE_DIR="$REPO_ROOT/.worktrees"
BASE_BRANCH="claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[⚠]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; }

# Session configurations
declare -A PHASE1_SESSIONS=(
    ["session-1-ndi"]="docs/SESSION-STARTERS/session-1-ndi-witness.md:claude/realtime-workstream-1-ndi"
    ["session-2-webrtc"]="docs/SESSION-STARTERS/session-2-webrtc-swarm.md:claude/realtime-workstream-2-webrtc"
    ["session-3-h323"]="docs/SESSION-STARTERS/session-3-h323-guard.md:claude/realtime-workstream-3-h323"
    ["session-cli"]="docs/SESSION-STARTERS/session-parallel-cli-witness.md:claude/cli-witness-optimise"
)

declare -A PHASE2_SESSIONS=(
    ["session-4-sip"]="docs/SESSION-STARTERS/session-4-sip-escalate.md:claude/realtime-workstream-4-sip"
)

create_worktree() {
    local session_name="$1"
    local branch_name="$2"
    local worktree_path="$WORKTREE_DIR/$session_name"

    if [ -d "$worktree_path" ]; then
        warn "Worktree already exists: $worktree_path"
        return 0
    fi

    log "Creating worktree: $worktree_path"
    mkdir -p "$WORKTREE_DIR"

    git worktree add -b "$branch_name" "$worktree_path" "$BASE_BRANCH" 2>/dev/null || {
        # Branch might already exist
        git worktree add "$worktree_path" "$branch_name" 2>/dev/null || {
            error "Failed to create worktree for $session_name"
            return 1
        }
    }

    success "Created worktree: $worktree_path"
}

extract_prompt() {
    local session_file="$1"

    # Extract the "Copy-Paste This" block
    awk '
        /^```$/ && !in_block { in_block=1; next }
        /^```$/ && in_block { in_block=0; exit }
        in_block { print }
    ' "$REPO_ROOT/$session_file"
}

launch_session_manual() {
    local session_name="$1"
    local session_file="$2"
    local worktree_path="$3"

    log "Generating prompt for $session_name"

    local prompt_file="$worktree_path/SESSION_PROMPT.txt"
    {
        echo "# Auto-generated prompt for $session_name"
        echo "# Worktree: $worktree_path"
        echo "# Copy-paste this into a Claude Code session"
        echo ""
        echo "WORKTREE: $worktree_path"
        echo ""
        extract_prompt "$session_file"
    } > "$prompt_file"

    success "Prompt saved: $prompt_file"
    warn "MANUAL ACTION REQUIRED:"
    echo "  1. Open a new Claude Code session"
    echo "  2. Paste the contents of: $prompt_file"
    echo "  3. Session will run in worktree: $worktree_path"
}

launch_session_cli() {
    local session_name="$1"
    local session_file="$2"
    local worktree_path="$3"

    # Check if Claude Code CLI is available
    if ! command -v claude-code &> /dev/null; then
        launch_session_manual "$session_name" "$session_file" "$worktree_path"
        return
    fi

    log "Launching $session_name via Claude Code CLI"

    local prompt=$(extract_prompt "$session_file")

    # Launch in background
    (
        cd "$worktree_path"
        claude-code --prompt "$prompt" > "$worktree_path/session.log" 2>&1 &
        echo $! > "$worktree_path/session.pid"
    )

    success "Session launched (PID: $(cat "$worktree_path/session.pid"))"
}

run_phase() {
    local phase="$1"

    case $phase in
        phase1)
            log "Launching Phase 1: 4 independent sessions"
            for session_name in "${!PHASE1_SESSIONS[@]}"; do
                IFS=':' read -r session_file branch_name <<< "${PHASE1_SESSIONS[$session_name]}"
                create_worktree "$session_name" "$branch_name"
                launch_session_manual "$session_name" "$session_file" "$WORKTREE_DIR/$session_name"
                echo ""
            done
            ;;
        phase2)
            log "Launching Phase 2: SIP session (depends on Phase 1)"

            # Check dependencies
            warn "Checking Phase 1 completion..."
            for dep in session-2-webrtc session-3-h323; do
                if ! git show-ref --verify --quiet "refs/heads/claude/realtime-workstream-*"; then
                    error "Dependency not met: $dep must complete first"
                    return 1
                fi
            done

            for session_name in "${!PHASE2_SESSIONS[@]}"; do
                IFS=':' read -r session_file branch_name <<< "${PHASE2_SESSIONS[$session_name]}"
                create_worktree "$session_name" "$branch_name"
                launch_session_manual "$session_name" "$session_file" "$WORKTREE_DIR/$session_name"
            done
            ;;
        *)
            error "Unknown phase: $phase"
            return 1
            ;;
    esac

    success "All sessions prepared!"
    echo ""
    echo "Next steps:"
    echo "  1. Open the SESSION_PROMPT.txt files in each worktree"
    echo "  2. Paste into separate Claude Code sessions"
    echo "  3. Monitor progress: ls -l $WORKTREE_DIR/*/SESSION_PROMPT.txt"
}

cleanup() {
    log "Cleaning up worktrees..."

    if [ ! -d "$WORKTREE_DIR" ]; then
        warn "No worktrees to clean up"
        return
    fi

    # Kill any running sessions
    for pid_file in "$WORKTREE_DIR"/*/session.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                log "Killing session PID $pid"
                kill "$pid" || true
            fi
            rm "$pid_file"
        fi
    done

    # Remove worktrees
    git worktree list | grep "\.worktrees" | awk '{print $1}' | while read -r wt; do
        log "Removing worktree: $wt"
        git worktree remove "$wt" --force || true
    done

    git worktree prune

    rm -rf "$WORKTREE_DIR"
    success "Cleanup complete"
}

status() {
    log "Session Status:"
    echo ""

    if [ ! -d "$WORKTREE_DIR" ]; then
        warn "No active sessions"
        return
    fi

    for wt in "$WORKTREE_DIR"/*; do
        if [ ! -d "$wt" ]; then continue; fi

        session_name=$(basename "$wt")
        echo "Session: $session_name"

        if [ -f "$wt/session.pid" ]; then
            pid=$(cat "$wt/session.pid")
            if kill -0 "$pid" 2>/dev/null; then
                echo "  Status: Running (PID $pid)"
            else
                echo "  Status: Stopped"
            fi
        else
            echo "  Status: Manual (check Claude Code session)"
        fi

        # Check for commits
        cd "$wt"
        commit_count=$(git log --oneline origin/$(git branch --show-current) 2>/dev/null | wc -l || echo 0)
        echo "  Commits: $commit_count"

        cd - > /dev/null
        echo ""
    done
}

main() {
    local command="${1:-help}"

    case $command in
        phase1)
            run_phase "phase1"
            ;;
        phase2)
            run_phase "phase2"
            ;;
        cleanup)
            cleanup
            ;;
        status)
            status
            ;;
        help|*)
            echo "IF.swarm Parallel Session Launcher"
            echo ""
            echo "Usage:"
            echo "  $0 phase1    - Launch Phase 1 (4 independent sessions)"
            echo "  $0 phase2    - Launch Phase 2 (SIP session, depends on Phase 1)"
            echo "  $0 status    - Show session status"
            echo "  $0 cleanup   - Remove all worktrees"
            echo ""
            echo "Worktrees will be created in: $WORKTREE_DIR"
            ;;
    esac
}

main "$@"
