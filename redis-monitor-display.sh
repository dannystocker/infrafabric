#!/bin/bash

################################################################################
# Redis Monitoring Display Script
# Purpose: Show real-time Redis activity + shard capacity at terminal bottom
# Usage: ./redis-monitor-display.sh &
# Exit: Ctrl+C or when Redis becomes unavailable
################################################################################

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
UPDATE_INTERVAL=5

# ANSI Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Terminal control
SAVE_CURSOR='\033[s'
RESTORE_CURSOR='\033[u'
HIDE_CURSOR='\033[?25l'
SHOW_CURSOR='\033[?25h'
CLEAR_LINE='\033[K'

################################################################################
# Utility Functions
################################################################################

# Log to file (for debugging)
log_debug() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> /tmp/redis-monitor.log
}

# Cleanup on exit
cleanup() {
    echo -e "${SHOW_CURSOR}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check Redis connection
check_redis_connection() {
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING >/dev/null 2>&1
    return $?
}

# Get memory information from Redis
get_memory_info() {
    local info=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO memory 2>/dev/null)
    local used=$(echo "$info" | grep "^used_memory_human:" | cut -d: -f2 | tr -d '\r')
    local max=$(echo "$info" | grep "^maxmemory_human:" | cut -d: -f2 | tr -d '\r')
    local used_bytes=$(echo "$info" | grep "^used_memory:" | cut -d: -f2 | tr -d '\r')
    local max_bytes=$(echo "$info" | grep "^maxmemory:" | cut -d: -f2 | tr -d '\r')

    # If maxmemory not set, use total system memory
    if [ -z "$max_bytes" ] || [ "$max_bytes" = "0" ]; then
        max_bytes=$(grep MemTotal /proc/meminfo | awk '{print $2 * 1024}')
        max="$(printf '%d' $((max_bytes / 1048576))) MB"
    fi

    echo "$used|$max|$used_bytes|$max_bytes"
}

# Get active instance keys
get_active_keys() {
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" KEYS "instance:*" 2>/dev/null | wc -l
}

# Get most recent operation from slowlog
get_last_operation() {
    local slowlog=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SLOWLOG GET 1 2>/dev/null)
    if [ -n "$slowlog" ]; then
        echo "$slowlog" | grep -oP '"\K[^"]+' | head -1 | cut -c1-60
    else
        echo "N/A"
    fi
}

# Get connection count
get_connection_count() {
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO clients 2>/dev/null | \
        grep "^connected_clients:" | cut -d: -f2 | tr -d '\r'
}

# Get operations per second
get_ops_per_second() {
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO stats 2>/dev/null | \
        grep "^instantaneous_ops_per_sec:" | cut -d: -f2 | tr -d '\r'
}

# Create a progress bar
create_progress_bar() {
    local used=$1
    local total=$2
    local width=25
    local percentage=0

    # Avoid division by zero
    if [ "$total" -gt 0 ]; then
        percentage=$((used * 100 / total))
    fi

    local filled=$((width * percentage / 100))

    printf "["
    for ((i=0; i<filled; i++)); do printf "█"; done
    for ((i=filled; i<width; i++)); do printf "░"; done
    printf "] "
    printf "%3d%%" "$percentage"
}

# Format bytes to human readable
format_bytes() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    elif [ "$bytes" -lt 1048576 ]; then
        echo "$((bytes / 1024))KB"
    elif [ "$bytes" -lt 1073741824 ]; then
        echo "$((bytes / 1048576))MB"
    else
        echo "$((bytes / 1073741824))GB"
    fi
}

# Display Redis monitoring panel
display_monitor() {
    local memory_info=$(get_memory_info)
    local used=$(echo "$memory_info" | cut -d'|' -f1)
    local max=$(echo "$memory_info" | cut -d'|' -f2)
    local used_bytes=$(echo "$memory_info" | cut -d'|' -f3)
    local max_bytes=$(echo "$memory_info" | cut -d'|' -f4)

    local active_keys=$(get_active_keys)
    local last_op=$(get_last_operation)
    local connections=$(get_connection_count)
    local ops_per_sec=$(get_ops_per_second)

    local timestamp=$(date +'%H:%M:%S')

    # Determine health status based on memory usage
    local health_status="HEALTHY"
    local health_color="${GREEN}"
    if [ "$max_bytes" -gt 0 ]; then
        local usage_percent=$((used_bytes * 100 / max_bytes))
        if [ "$usage_percent" -ge 90 ]; then
            health_status="CRITICAL"
            health_color="${RED}"
        elif [ "$usage_percent" -ge 75 ]; then
            health_status="WARNING"
            health_color="${YELLOW}"
        fi
    fi

    # Clear previous display (move to line 1000 to avoid scrolling)
    tput cup $(($(tput lines) - 8)) 0

    # Border top
    printf "╔════════════════════════════════════════════════════════════════════╗\n"

    # Title with timestamp
    printf "║ ${BLUE}REDIS MONITORING${NC} (${timestamp})                            ║\n"

    # Separator
    printf "╟────────────────────────────────────────────────────────────────────╢\n"

    # Connection and operations info
    printf "║ Status: ${health_color}[%s]${NC} | Connections: %-3s | Ops/sec: %-8s       ║\n" \
        "$health_status" "$connections" "$ops_per_sec"

    # Memory usage bar
    printf "║ Memory: "
    create_progress_bar "$used_bytes" "$max_bytes"
    printf " %-8s / %-8s       ║\n" "$used" "$max"

    # Active keys
    printf "║ Instance Keys: %-3s Active                                          ║\n" "$active_keys"

    # Last operation
    printf "║ Last Op: ${YELLOW}%-60s${NC} ║\n" "$last_op"

    # Border bottom
    printf "╚════════════════════════════════════════════════════════════════════╝\n"
}

# Display TTL information for instance keys
display_ttl_info() {
    local keys=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" KEYS "instance:*" 2>/dev/null)

    if [ -z "$keys" ]; then
        return
    fi

    tput cup $(($(tput lines) - 1)) 0
    printf "${YELLOW}TTL Active Keys:${NC} "

    local count=0
    while IFS= read -r key; do
        if [ "$count" -ge 3 ]; then
            printf "... and %d more" "$(($(echo "$keys" | wc -l) - 3))"
            break
        fi

        local ttl=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" TTL "$key" 2>/dev/null)
        if [ "$ttl" -gt 0 ]; then
            local days=$((ttl / 86400))
            local hours=$(((ttl % 86400) / 3600))
            if [ "$days" -gt 0 ]; then
                printf "$key (${days}d) "
            else
                printf "$key (${hours}h) "
            fi
            ((count++))
        fi
    done <<< "$keys"

    printf "\n"
}

################################################################################
# Main Monitoring Loop
################################################################################

echo -e "${HIDE_CURSOR}"
log_debug "Redis Monitor started (host: $REDIS_HOST, port: $REDIS_PORT)"

while true; do
    # Check if Redis is still accessible
    if ! check_redis_connection; then
        tput cup $(($(tput lines) - 8)) 0
        printf "╔════════════════════════════════════════════════════════════════════╗\n"
        printf "║ ${RED}REDIS DISCONNECTED${NC}                                              ║\n"
        printf "║ Cannot connect to Redis at ${REDIS_HOST}:${REDIS_PORT}                   ║\n"
        printf "║ Retrying in ${UPDATE_INTERVAL} seconds...                                   ║\n"
        printf "╚════════════════════════════════════════════════════════════════════╝\n"

        log_debug "Redis connection failed - retrying in $UPDATE_INTERVAL seconds"
    else
        # Display the monitoring panel
        display_monitor
        display_ttl_info
    fi

    # Sleep before next update
    sleep "$UPDATE_INTERVAL"
done
