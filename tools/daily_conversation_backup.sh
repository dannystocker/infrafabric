#!/bin/bash
###############################################################################
# Daily Conversation Backup Script
#
# This script runs daily to:
# 1. Backup all Open WebUI conversations to Redis L2
# 2. Export conversations as JSON and Markdown
# 3. Create timestamped archives
# 4. Clean up old backups (keep last 30 days)
#
# Installation:
#   chmod +x /home/setup/infrafabric/tools/daily_conversation_backup.sh
#   crontab -e
#   Add: 0 2 * * * /home/setup/infrafabric/tools/daily_conversation_backup.sh
#
###############################################################################

# Configuration
SCRIPT_DIR="/home/setup/infrafabric/tools"
BACKUP_DIR="/home/setup/conversation-archives/daily-backups"
LOG_DIR="/home/setup/infrafabric/logs"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log file for this run
LOGFILE="$LOG_DIR/backup_$DATE.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

log "=========================================="
log "DAILY CONVERSATION BACKUP STARTED"
log "=========================================="

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"/{json,markdown,archives}

# Check if Open WebUI is running
if ! docker ps | grep -q open-webui; then
    log "⚠️  Warning: Open WebUI container not running"
    log "   Skipping backup (no new conversations)"
    exit 0
fi

# Run backup script
log "📥 Running backup to Redis L2 and files..."

cd "$SCRIPT_DIR" || exit 1

# Activate virtual environment if exists
if [ -d "/home/setup/infrafabric/venv" ]; then
    source /home/setup/infrafabric/venv/bin/activate
fi

# Run Python backup script
python3 "$SCRIPT_DIR/openwebui_redis_sync.py" \
    --export-dir "$BACKUP_DIR" \
    >> "$LOGFILE" 2>&1

BACKUP_STATUS=$?

if [ $BACKUP_STATUS -eq 0 ]; then
    log "✅ Backup completed successfully"
else
    log "❌ Backup failed with status $BACKUP_STATUS"
    log "   Check log: $LOGFILE"
    exit 1
fi

# Create timestamped archive
log "📦 Creating timestamped archive..."

ARCHIVE_NAME="conversations_$TIMESTAMP.tar.gz"
ARCHIVE_PATH="$BACKUP_DIR/archives/$ARCHIVE_NAME"

tar -czf "$ARCHIVE_PATH" \
    -C "$BACKUP_DIR" \
    json markdown \
    >> "$LOGFILE" 2>&1

if [ $? -eq 0 ]; then
    ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
    log "✅ Archive created: $ARCHIVE_NAME ($ARCHIVE_SIZE)"
else
    log "❌ Archive creation failed"
fi

# Clean up old backups (keep last 30 days)
log "🧹 Cleaning up old backups (keeping last 30 days)..."

find "$BACKUP_DIR/archives" -name "conversations_*.tar.gz" -mtime +30 -delete >> "$LOGFILE" 2>&1
DELETED_COUNT=$(find "$BACKUP_DIR/archives" -name "conversations_*.tar.gz" -mtime +30 | wc -l)

if [ $DELETED_COUNT -gt 0 ]; then
    log "   Deleted $DELETED_COUNT old archives"
else
    log "   No old archives to delete"
fi

# Generate backup summary
log "📊 Backup Summary:"
log "   JSON files: $(find "$BACKUP_DIR/json" -type f | wc -l)"
log "   Markdown files: $(find "$BACKUP_DIR/markdown" -type f | wc -l)"
log "   Archives: $(find "$BACKUP_DIR/archives" -type f | wc -l)"
log "   Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"

# Update Redis with backup metadata
log "💾 Updating Redis L2 with backup metadata..."

redis-cli -h 85.239.243.227 -p 6379 \
    -a '@@Redis_InfraFabric_L2_2025$$' \
    SET "backup:daily:last_run" "$TIMESTAMP" \
    >> "$LOGFILE" 2>&1

redis-cli -h 85.239.243.227 -p 6379 \
    -a '@@Redis_InfraFabric_L2_2025$$' \
    SET "backup:daily:last_status" "success" \
    >> "$LOGFILE" 2>&1

log "=========================================="
log "DAILY BACKUP COMPLETED SUCCESSFULLY"
log "=========================================="
log ""

# Keep only last 7 days of logs
find "$LOG_DIR" -name "backup_*.log" -mtime +7 -delete

exit 0
