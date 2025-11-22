#!/bin/bash
##############################################################################
# FILE: spawn_copilot_shard.sh
# PURPOSE: Message Bus Integration for Copilot Thinking Shard
# ARCHITECTURE: Part of IF.memory.distributed - Distributed Memory System
#
# WORKFLOW:
# 1. Monitor .memory_bus/queries/ for queries tagged {"target": "copilot"}
# 2. When found, execute copilot_shard.py with the prompt
# 3. Write JSON response to .memory_bus/responses/
# 4. Loop forever (until KILL signal)
#
# USAGE:
#   ./spawn_copilot_shard.sh
#
# DEPENDENCIES:
#   - Python 3 with re-edge-gpt installed (.venv-copilot/)
#   - cookies.json in same directory
#   - .memory_bus/ directory structure
##############################################################################

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_BUS="$SCRIPT_DIR/.memory_bus"
QUERIES_DIR="$MEMORY_BUS/queries"
RESPONSES_DIR="$MEMORY_BUS/responses"
HEARTBEAT_DIR="$MEMORY_BUS/heartbeat"
CONTROL_DIR="$MEMORY_BUS/control"
PYTHON_VENV="$SCRIPT_DIR/.venv-copilot/bin/python3"
COPILOT_SCRIPT="$SCRIPT_DIR/copilot_shard.py"
SHARD_ID="copilot_shard"

# Ensure directories exist
mkdir -p "$QUERIES_DIR" "$RESPONSES_DIR" "$HEARTBEAT_DIR" "$CONTROL_DIR"

# Heartbeat function
heartbeat() {
    echo "$(date -Iseconds)" > "$HEARTBEAT_DIR/$SHARD_ID.txt"
}

# Log function
log() {
    echo "[$(date -Iseconds)] [$SHARD_ID] $1"
}

# Main monitoring loop
log "Starting Copilot Thinking Shard..."
log "Monitoring: $QUERIES_DIR"
log "Python: $PYTHON_VENV"

CYCLE_COUNT=0

while true; do
    # Check for KILL signal
    if [ -f "$CONTROL_DIR/KILL" ]; then
        log "KILL signal received. Shutting down."
        exit 0
    fi

    # Update heartbeat every 5 cycles
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    if [ $((CYCLE_COUNT % 5)) -eq 0 ]; then
        heartbeat
    fi

    # Scan for queries tagged for Copilot
    for query_file in "$QUERIES_DIR"/*.json; do
        # Skip if no files found
        [ -e "$query_file" ] || continue

        # Read query
        QUERY_CONTENT=$(cat "$query_file")

        # Check if this query is for Copilot
        TARGET=$(echo "$QUERY_CONTENT" | grep -o '"target"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"/\1/')

        if [ "$TARGET" = "copilot" ]; then
            # Extract query details
            QUERY_ID=$(echo "$QUERY_CONTENT" | grep -o '"query_id"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"/\1/')
            QUESTION=$(echo "$QUERY_CONTENT" | grep -o '"question"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"/\1/')

            log "Processing query: $QUERY_ID"
            log "Question: $QUESTION"

            # Execute Copilot query
            RESPONSE=$("$PYTHON_VENV" "$COPILOT_SCRIPT" "$QUESTION")
            EXIT_CODE=$?

            # Prepare response
            RESPONSE_FILE="$RESPONSES_DIR/r_${QUERY_ID}.json"

            if [ $EXIT_CODE -eq 0 ]; then
                # Success - wrap in response envelope
                echo "{\"query_id\": \"$QUERY_ID\", \"status\": \"success\", \"shard\": \"$SHARD_ID\", \"result\": $RESPONSE}" > "$RESPONSE_FILE"
                log "Response written: $RESPONSE_FILE"
            else
                # Error - include error details
                echo "{\"query_id\": \"$QUERY_ID\", \"status\": \"error\", \"shard\": \"$SHARD_ID\", \"error\": $RESPONSE}" > "$RESPONSE_FILE"
                log "Error response written: $RESPONSE_FILE"
            fi

            # Delete processed query
            rm "$query_file"
            log "Query file deleted: $query_file"
        fi
    done

    # Sleep before next cycle
    sleep 5
done
