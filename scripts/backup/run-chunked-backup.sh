#!/bin/bash
# InfraFabric Chunked Backup Executor
# Creates organized backup with date/time/project structure

# Configuration
BACKUP_BASE="/home/setup/public_html/digital-lab.ca/infrafabric/backups"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
PROJECT_NAME="infrafabric"
BACKUP_ROOT="${BACKUP_BASE}/${TIMESTAMP}_${PROJECT_NAME}"

# Best practice structure:
# /backups/YYYY-MM-DD_HHMMSS_infrafabric/
#   ├── 01_core_projects/
#   ├── 02_config_history/
#   ├── 03_mcp_bridge/
#   ├── 04_work_projects/
#   ├── MANIFEST.md
#   ├── SHA256SUMS.txt
#   └── backup.log

mkdir -p "$BACKUP_ROOT"

# Redirect all output to log
exec > >(tee -a "$BACKUP_ROOT/backup.log")
exec 2>&1

echo "================================================================================"
echo "InfraFabric Automated Backup"
echo "================================================================================"
echo "Started: $(date)"
echo "Backup Location: $BACKUP_ROOT"
echo ""

# Chunk 1: CORE PROJECTS (critical - highest priority restore)
echo "📦 Chunk 1/4: CORE_PROJECTS"
mkdir -p "$BACKUP_ROOT/01_core_projects"
tar -czf "$BACKUP_ROOT/01_core_projects/core_projects.tar.gz" \
    -C /home/setup \
    infrafabric \
    infrafabric-core \
    public_html/digital-lab.ca/infrafabric \
    .security \
    council_ab_test_archive \
    2>/dev/null

SIZE1=$(du -sh "$BACKUP_ROOT/01_core_projects/core_projects.tar.gz" | cut -f1)
echo "   ✓ Created: $SIZE1"
echo ""

# Chunk 2: CONFIGURATION (Claude config, credentials, history)
echo "📦 Chunk 2/4: CONFIG_HISTORY"
mkdir -p "$BACKUP_ROOT/02_config_history"
tar -czf "$BACKUP_ROOT/02_config_history/config_history.tar.gz" \
    -C /home/setup \
    .claude \
    .config \
    .gitconfig \
    --exclude=.claude/.codex \
    2>/dev/null

SIZE2=$(du -sh "$BACKUP_ROOT/02_config_history/config_history.tar.gz" | cut -f1)
echo "   ✓ Created: $SIZE2"
echo ""

# Chunk 3: MCP BRIDGE (standalone utility - frequently updated)
echo "📦 Chunk 3/4: MCP_BRIDGE"
mkdir -p "$BACKUP_ROOT/03_mcp_bridge"
tar -czf "$BACKUP_ROOT/03_mcp_bridge/mcp_bridge.tar.gz" \
    -C /home/setup/work \
    mcp-multiagent-bridge \
    2>/dev/null

SIZE3=$(du -sh "$BACKUP_ROOT/03_mcp_bridge/mcp_bridge.tar.gz" | cut -f1)
echo "   ✓ Created: $SIZE3"
echo ""

# Chunk 4: WORK PROJECTS (development - optional, large)
echo "📦 Chunk 4/4: WORK_PROJECTS"
mkdir -p "$BACKUP_ROOT/04_work_projects"
tar -czf "$BACKUP_ROOT/04_work_projects/work_projects.tar.gz" \
    -C /home/setup \
    work \
    --exclude=work/mcp-multiagent-bridge \
    --exclude=node_modules \
    --exclude=.next \
    --exclude=dist \
    --exclude=build \
    --exclude=.git/objects \
    2>/dev/null

SIZE4=$(du -sh "$BACKUP_ROOT/04_work_projects/work_projects.tar.gz" | cut -f1)
echo "   ✓ Created: $SIZE4"
echo ""

# Create SHA256 checksums
echo "🔒 Generating checksums..."
cd "$BACKUP_ROOT"
find . -name "*.tar.gz" -type f -exec sha256sum {} \; > SHA256SUMS.txt
echo "   ✓ SHA256SUMS.txt created"
echo ""

# Create backup manifest
cat > "$BACKUP_ROOT/MANIFEST.md" << MANIFEST_EOF
# InfraFabric Backup Manifest

**Backup Date:** $(date)
**Timestamp:** $TIMESTAMP
**Host:** $(hostname)
**User:** $(whoami)
**Trigger:** Automated idle detection (1 hour idle)

## Backup Structure

\`\`\`
${TIMESTAMP}_${PROJECT_NAME}/
├── 01_core_projects/
│   └── core_projects.tar.gz ($SIZE1)
├── 02_config_history/
│   └── config_history.tar.gz ($SIZE2)
├── 03_mcp_bridge/
│   └── mcp_bridge.tar.gz ($SIZE3)
├── 04_work_projects/
│   └── work_projects.tar.gz ($SIZE4)
├── MANIFEST.md (this file)
├── SHA256SUMS.txt
└── backup.log
\`\`\`

## Chunk Details

### Chunk 1: CORE_PROJECTS ($SIZE1)
**Priority:** CRITICAL - Restore first
**Contents:**
- infrafabric/ (main research codebase)
- infrafabric-core/ (core papers: IF.vision, IF.armour, IF.foundations, IF.witness)
- public_html/digital-lab.ca/infrafabric/ (deployed microsite)
- .security/ (security evidence, revoked keys whitelist, incident reports)
- council_ab_test_archive/ (A/B test microsite with git history)

**Restore command:**
\`\`\`bash
tar -xzf 01_core_projects/core_projects.tar.gz -C /home/setup
\`\`\`

### Chunk 2: CONFIG_HISTORY ($SIZE2)
**Priority:** HIGH - Conversation context and credentials
**Contents:**
- .claude/ (conversation history, agents, CLAUDE.md config)
- .config/ (system configuration)
- .gitconfig (git user config)

**Restore command:**
\`\`\`bash
tar -xzf 02_config_history/config_history.tar.gz -C /home/setup
\`\`\`

### Chunk 3: MCP_BRIDGE ($SIZE3)
**Priority:** MEDIUM - Standalone utility
**Contents:**
- work/mcp-multiagent-bridge/ (MCP coordination layer)

**Restore command:**
\`\`\`bash
mkdir -p /home/setup/work
tar -xzf 03_mcp_bridge/mcp_bridge.tar.gz -C /home/setup/work
\`\`\`

### Chunk 4: WORK_PROJECTS ($SIZE4)
**Priority:** LOW - Development projects (can rebuild)
**Contents:**
- work/* (icw-nextspread, job-hunt, stayscape, etc.)
- Excludes: node_modules, .next, dist, build, .git/objects

**Restore command:**
\`\`\`bash
tar -xzf 04_work_projects/work_projects.tar.gz -C /home/setup
\`\`\`

## Full Restore Procedure

1. Verify checksums: \`sha256sum -c SHA256SUMS.txt\`
2. Restore Chunk 1 (CORE_PROJECTS)
3. Restore Chunk 2 (CONFIG_HISTORY)
4. Verify critical files:
   - .claude/CLAUDE.md
   - .security/revoked-keys-whitelist.md
   - infrafabric/papers/IF-vision.md
5. (Optional) Restore Chunk 3 (MCP_BRIDGE)
6. (Optional) Restore Chunk 4 (WORK_PROJECTS)

## Disaster Recovery Checklist

- [ ] Verify all 4 chunks present
- [ ] Verify SHA256SUMS.txt checksums pass
- [ ] Restore Chunk 1 + 2 (minimum viable system)
- [ ] Check API keys in .claude/CLAUDE.md
- [ ] Verify security evidence in .security/
- [ ] Test git repositories have remotes configured
- [ ] Reinstall Node.js dependencies if needed

## Critical Files Quick Reference

**API Keys:** .claude/CLAUDE.md (lines 15-16)
**Security Whitelist:** .security/revoked-keys-whitelist.md
**Security Incident:** .security/openrouter-key-exposure-2025-11-07.md
**Email Evidence:** .security/openrouter-security-alert-2025-11-07.eml

**Git Remotes:**
- infrafabric → https://github.com/dannystocker/infrafabric
- infrafabric-core → https://github.com/dannystocker/infrafabric-core
- icw-nextspread → http://localhost:4000/ggq-admin/icw-nextspread

## IF.citation

\`\`\`
if://citation/${TIMESTAMP}/automated-backup-manifest
Type: backup_manifest
Source: Automated idle-triggered backup
Claim: Complete system backup in 4 logical chunks for efficient restore
Evidence: Backup timestamps, file sizes, SHA256 checksums
Verification: sha256sum -c SHA256SUMS.txt
Trigger: System idle detection (1 hour threshold)
\`\`\`

---

**Generated:** $(date)
**Backup Script:** /home/setup/infrafabric/scripts/backup/run-chunked-backup.sh
**Monitor Script:** /home/setup/infrafabric/scripts/backup/idle-backup-system.sh

🤖 Generated with InfraFabric automated backup system
MANIFEST_EOF

echo "================================================================================"
echo "Backup Complete!"
echo "================================================================================"
echo ""
echo "Backup Location: $BACKUP_ROOT"
echo ""
echo "Chunks created:"
echo "  01_core_projects/     $SIZE1"
echo "  02_config_history/    $SIZE2"
echo "  03_mcp_bridge/        $SIZE3"
echo "  04_work_projects/     $SIZE4"
echo ""
TOTAL_SIZE=$(du -sh "$BACKUP_ROOT" | cut -f1)
echo "Total backup size: $TOTAL_SIZE"
echo ""
echo "Manifest: $BACKUP_ROOT/MANIFEST.md"
echo "Checksums: $BACKUP_ROOT/SHA256SUMS.txt"
echo "Log: $BACKUP_ROOT/backup.log"
echo ""
echo "Completed: $(date)"
echo ""

# Cleanup: Keep only last 5 backups
echo "🗑️  Cleanup: Keeping last 5 backups..."
cd "$BACKUP_BASE"
ls -t | grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}_" | tail -n +6 | while read old_backup; do
    echo "   Removing old backup: $old_backup"
    rm -rf "$old_backup"
done
echo ""
echo "Backup system complete."
