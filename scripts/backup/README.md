# InfraFabric Automated Backup System

**Purpose:** Automated, idle-triggered backup system that runs when you're asleep or away from keyboard.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User Activity                                              │
│  ↓ (keyboard/mouse idle for 1 hour)                        │
├─────────────────────────────────────────────────────────────┤
│  idle-backup-system.sh                                      │
│  - Monitors idle time every 5 minutes                       │
│  - Triggers backup when threshold reached                   │
│  - Prevents duplicate backups                               │
├─────────────────────────────────────────────────────────────┤
│  run-chunked-backup.sh                                      │
│  - Creates 4 logical backup chunks                          │
│  - Generates SHA256 checksums                               │
│  - Creates detailed manifest                                │
│  - Auto-cleanup (keeps last 5 backups)                      │
├─────────────────────────────────────────────────────────────┤
│  Backup Storage: digital-lab.ca/infrafabric/backups/        │
│                                                              │
│  YYYY-MM-DD_HHMMSS_infrafabric/                            │
│  ├── 01_core_projects/       (~125M)                        │
│  ├── 02_config_history/      (~1.4G)                        │
│  ├── 03_mcp_bridge/          (~30M)                         │
│  ├── 04_work_projects/       (~4G)                          │
│  ├── MANIFEST.md                                            │
│  ├── SHA256SUMS.txt                                         │
│  └── backup.log                                             │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
cd /home/setup/infrafabric/scripts/backup
./install-backup-system.sh
```

This will:
1. Create backup directory structure
2. Make scripts executable
3. Add cron job for auto-start on boot
4. Optionally start the monitor now

## Usage

### Automatic (Recommended)
The system runs automatically:
- Starts on boot via crontab
- Monitors idle time continuously
- Triggers backup after 1 hour of inactivity
- Keeps last 5 backups (auto-cleanup)

### Manual Control

**Start monitor:**
```bash
/home/setup/infrafabric/scripts/backup/idle-backup-system.sh &
```

**Run backup immediately:**
```bash
/home/setup/infrafabric/scripts/backup/run-chunked-backup.sh
```

**View monitor log:**
```bash
tail -f /home/setup/.backup-idle.log
```

**Stop monitor:**
```bash
kill $(cat /home/setup/.backup-idle.pid)
```

**Check monitor status:**
```bash
ps -p $(cat /home/setup/.backup-idle.pid) && echo "Running" || echo "Stopped"
```

## Backup Structure

### Best Practice Folder Organization

```
/home/setup/public_html/digital-lab.ca/infrafabric/backups/
├── 2025-11-08_220000_infrafabric/
│   ├── 01_core_projects/
│   │   └── core_projects.tar.gz
│   ├── 02_config_history/
│   │   └── config_history.tar.gz
│   ├── 03_mcp_bridge/
│   │   └── mcp_bridge.tar.gz
│   ├── 04_work_projects/
│   │   └── work_projects.tar.gz
│   ├── MANIFEST.md
│   ├── SHA256SUMS.txt
│   └── backup.log
├── 2025-11-09_030000_infrafabric/
│   └── ...
└── 2025-11-10_010000_infrafabric/
    └── ...
```

### Chunk Priorities

| Chunk | Priority | Size | Contents |
|-------|----------|------|----------|
| 01_core_projects | CRITICAL | ~125M | infrafabric, papers, .security |
| 02_config_history | HIGH | ~1.4G | .claude, .config, credentials |
| 03_mcp_bridge | MEDIUM | ~30M | MCP coordination layer |
| 04_work_projects | LOW | ~4G | Development projects |

## Restore Procedures

### Quick Restore (Core Only)

```bash
cd /path/to/backup/YYYY-MM-DD_HHMMSS_infrafabric

# Verify checksums
sha256sum -c SHA256SUMS.txt

# Restore critical files
tar -xzf 01_core_projects/core_projects.tar.gz -C /home/setup
tar -xzf 02_config_history/config_history.tar.gz -C /home/setup

# Verify
ls -la /home/setup/.claude/CLAUDE.md
ls -la /home/setup/.security/
```

### Full Restore

```bash
cd /path/to/backup/YYYY-MM-DD_HHMMSS_infrafabric

# Verify checksums
sha256sum -c SHA256SUMS.txt

# Restore all chunks
tar -xzf 01_core_projects/core_projects.tar.gz -C /home/setup
tar -xzf 02_config_history/config_history.tar.gz -C /home/setup
mkdir -p /home/setup/work
tar -xzf 03_mcp_bridge/mcp_bridge.tar.gz -C /home/setup/work
tar -xzf 04_work_projects/work_projects.tar.gz -C /home/setup
```

### Disaster Recovery Checklist

- [ ] Boot from live USB / fresh WSL install
- [ ] Mount backup drive / download from cloud
- [ ] Verify SHA256 checksums
- [ ] Restore Chunk 1 (core projects)
- [ ] Restore Chunk 2 (config + credentials)
- [ ] Check API keys: `cat /home/setup/.claude/CLAUDE.md | grep "api key"`
- [ ] Verify security evidence: `ls -la /home/setup/.security/`
- [ ] (Optional) Restore Chunk 3 + 4
- [ ] Reinstall Node.js: `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash`
- [ ] Install dependencies: `npm install` in project directories
- [ ] Verify git remotes: `git remote -v` in each repository

## Configuration

### Adjust Idle Threshold

Edit `/home/setup/infrafabric/scripts/backup/idle-backup-system.sh`:

```bash
IDLE_THRESHOLD=3600  # Default: 1 hour (3600 seconds)
```

Common values:
- 30 minutes: `1800`
- 1 hour: `3600` (default)
- 2 hours: `7200`

### Change Backup Retention

Edit `/home/setup/infrafabric/scripts/backup/run-chunked-backup.sh`:

```bash
# Keep only last 5 backups
ls -t | tail -n +6 | while read old_backup; do
```

Change `6` to keep different number:
- Keep last 3: `tail -n +4`
- Keep last 10: `tail -n +11`

## Monitoring

### View Recent Backups

```bash
ls -lht /home/setup/public_html/digital-lab.ca/infrafabric/backups/ | head -10
```

### Check Backup Sizes

```bash
du -sh /home/setup/public_html/digital-lab.ca/infrafabric/backups/*
```

### Monitor Real-Time

```bash
tail -f /home/setup/.backup-idle.log
```

### Verify Latest Backup

```bash
LATEST=$(ls -t /home/setup/public_html/digital-lab.ca/infrafabric/backups/ | head -1)
cd "/home/setup/public_html/digital-lab.ca/infrafabric/backups/$LATEST"
sha256sum -c SHA256SUMS.txt
```

## Troubleshooting

### Monitor won't start

```bash
# Check if already running
ps aux | grep idle-backup-system

# Check logs
cat /home/setup/.backup-idle.log

# Remove stale PID file
rm /home/setup/.backup-idle.pid

# Restart
/home/setup/infrafabric/scripts/backup/idle-backup-system.sh &
```

### Backup fails

```bash
# Check disk space
df -h /home/setup/public_html

# Check permissions
ls -la /home/setup/public_html/digital-lab.ca/infrafabric/

# Run manually to see errors
/home/setup/infrafabric/scripts/backup/run-chunked-backup.sh
```

### Idle detection not working

```bash
# Install xprintidle for better detection
sudo apt-get update
sudo apt-get install xprintidle

# Test idle detection
w -h  # Shows current idle time
```

## Cloud Sync (Optional)

To sync backups to cloud storage:

```bash
# Example: rclone to Google Drive
rclone sync /home/setup/public_html/digital-lab.ca/infrafabric/backups/ \
  gdrive:InfraFabric-Backups/ \
  --progress

# Example: AWS S3
aws s3 sync /home/setup/public_html/digital-lab.ca/infrafabric/backups/ \
  s3://infrafabric-backups/ \
  --storage-class GLACIER
```

## IF.philosophy Integration

**Principle 3: Make Unknowns Explicit (Fallibilism)**
- Manifest documents what's backed up (no mystery data)
- SHA256 checksums verify integrity (know if corruption occurred)
- Backup log shows exact execution timeline

**Principle 8: Observability Without Fragility (Stoic Prudence)**
- Automated system removes human error (no "forgot to backup")
- Idle detection prevents interruption (runs when sleeping)
- Auto-cleanup prevents disk fill (resilient by design)

**IF.witness (Meta-Validation)**
- Backup system validates itself through checksums
- Manifest includes IF.citation for provenance
- Restore procedures are documented and testable

---

**Last Updated:** 2025-11-08
**Maintained By:** InfraFabric Backup Team
**License:** MIT (internal tooling)

🤖 Generated with InfraFabric automation
Co-Authored-By: Claude Sonnet 4.5 (Anthropic)
