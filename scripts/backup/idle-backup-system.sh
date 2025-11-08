#!/bin/bash
# InfraFabric Idle Backup System
# Triggers backup when system is idle for 1 hour
# Best practice: runs during sleep/inactivity

BACKUP_BASE="/home/setup/public_html/digital-lab.ca/infrafabric/backups"
IDLE_THRESHOLD=3600  # 1 hour in seconds
LOG_FILE="/home/setup/.backup-idle.log"
PID_FILE="/home/setup/.backup-idle.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "$(date): Backup monitor already running (PID $OLD_PID)" >> "$LOG_FILE"
        exit 0
    fi
fi

# Write our PID
echo $$ > "$PID_FILE"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

get_idle_time() {
    # Get idle time from X server (if available)
    if command -v xprintidle > /dev/null 2>&1; then
        echo $(($(xprintidle) / 1000))  # Convert ms to seconds
        return
    fi

    # Fallback: check last input from w command
    idle_str=$(w -h | awk '{print $4}' | head -1)

    # Parse idle string (could be "2:30" or "5.0s" or "1:20m")
    if [[ $idle_str == *"s" ]]; then
        echo 0  # Less than a minute
    elif [[ $idle_str == *"m" ]]; then
        mins=$(echo "$idle_str" | tr -d 'm')
        echo $((mins * 60))
    elif [[ $idle_str == *":"* ]]; then
        IFS=: read h m <<< "$idle_str"
        echo $((h * 3600 + m * 60))
    else
        echo 0
    fi
}

log "Idle backup monitor started (PID $$)"
log "Monitoring for ${IDLE_THRESHOLD}s (1 hour) idle time"
log "Backup destination: $BACKUP_BASE"

BACKUP_TRIGGERED=false

while true; do
    IDLE=$(get_idle_time)

    if [ "$IDLE" -ge "$IDLE_THRESHOLD" ] && [ "$BACKUP_TRIGGERED" = false ]; then
        log "System idle for ${IDLE}s (threshold: ${IDLE_THRESHOLD}s)"
        log "Triggering automated backup..."

        # Run the backup script
        /home/setup/infrafabric/scripts/backup/run-chunked-backup.sh >> "$LOG_FILE" 2>&1

        BACKUP_TRIGGERED=true
        log "Backup completed. Monitor will continue..."
    fi

    # Reset trigger if user becomes active again
    if [ "$IDLE" -lt 300 ] && [ "$BACKUP_TRIGGERED" = true ]; then
        log "User activity detected. Resetting backup trigger."
        BACKUP_TRIGGERED=false
    fi

    # Check every 5 minutes
    sleep 300
done
