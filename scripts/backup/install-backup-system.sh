#!/bin/bash
# InfraFabric Backup System Installer
# Sets up automated idle-triggered backups

echo "================================================================================"
echo "InfraFabric Backup System Installer"
echo "================================================================================"
echo ""

SCRIPTS_DIR="/home/setup/infrafabric/scripts/backup"
CRON_JOB="@reboot $SCRIPTS_DIR/idle-backup-system.sh &"

# Create backup destination
BACKUP_BASE="/home/setup/public_html/digital-lab.ca/infrafabric/backups"
mkdir -p "$BACKUP_BASE"
echo "✓ Created backup directory: $BACKUP_BASE"

# Make scripts executable
chmod +x "$SCRIPTS_DIR/idle-backup-system.sh"
chmod +x "$SCRIPTS_DIR/run-chunked-backup.sh"
echo "✓ Made scripts executable"

# Check if xprintidle is available (for better idle detection)
if ! command -v xprintidle > /dev/null 2>&1; then
    echo ""
    echo "⚠️  xprintidle not found (optional but recommended)"
    echo "   Install with: sudo apt-get install xprintidle"
    echo "   (Will use fallback idle detection method)"
    echo ""
fi

# Add to crontab
echo ""
echo "Setting up auto-start on boot..."
(crontab -l 2>/dev/null | grep -v "idle-backup-system.sh"; echo "$CRON_JOB") | crontab -
echo "✓ Added to crontab: $CRON_JOB"

echo ""
echo "================================================================================"
echo "Installation Complete!"
echo "================================================================================"
echo ""
echo "Backup system will:"
echo "  - Start automatically on boot"
echo "  - Monitor system idle time (1 hour threshold)"
echo "  - Trigger backup when idle"
echo "  - Save to: $BACKUP_BASE"
echo "  - Keep last 5 backups automatically"
echo ""
echo "Manual commands:"
echo "  Start monitor:  $SCRIPTS_DIR/idle-backup-system.sh &"
echo "  Run backup now: $SCRIPTS_DIR/run-chunked-backup.sh"
echo "  View log:       tail -f /home/setup/.backup-idle.log"
echo "  Stop monitor:   kill \$(cat /home/setup/.backup-idle.pid)"
echo ""
echo "Start the monitor now? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    nohup "$SCRIPTS_DIR/idle-backup-system.sh" > /dev/null 2>&1 &
    echo "✓ Backup monitor started (PID $!)"
    echo "  Monitor log: /home/setup/.backup-idle.log"
else
    echo "Run manually when ready: $SCRIPTS_DIR/idle-backup-system.sh &"
fi
echo ""
