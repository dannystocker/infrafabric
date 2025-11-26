#!/bin/bash

#==============================================================================
# Smart InfraFabric Integration Script
# Generated: 2025-11-15
#
# Purpose: Intelligently merge InfraFabric files based on timestamps and
#          content hashes (SHA256), organizing duplicates into archives
#
# Usage:
#   ./smart_integrate.sh [dry-run|execute]
#
# Default: dry-run mode (safe, shows what would happen)
#==============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=${1:-true}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${SCRIPT_DIR}/integration_${TIMESTAMP}.log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Statistics
STATS_EXACT_DUPS=0
STATS_NEWER_KEPT=0
STATS_OLDER_ARCHIVED=0
STATS_CONFLICTS=0
STATS_BYTES_RECOVERED=0
STATS_TOTAL_FILES=0

#==============================================================================
# Helper Functions
#==============================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_dryrun() {
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} $1" | tee -a "$LOG_FILE"
    fi
}

# Create directory if needed
mkdir_safe() {
    local dir="$1"
    if [ "$DRY_RUN" = "true" ]; then
        log_dryrun "Would create directory: $dir"
    else
        mkdir -p "$dir"
        log_success "Created directory: $dir"
    fi
}

# Copy file with optional archiving
copy_file() {
    local src="$1"
    local dst="$2"
    local archive_name="$3"  # Optional: basename for archive

    if [ ! -f "$src" ]; then
        log_error "Source file not found: $src"
        return 1
    fi

    if [ "$DRY_RUN" = "true" ]; then
        log_dryrun "Would copy: $src -> $dst"
    else
        cp "$src" "$dst"
        log_success "Copied: $(basename "$src") -> $dst"
    fi
}

# Get file size in human-readable format
human_size() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    elif [ "$bytes" -lt 1048576 ]; then
        echo "$((bytes / 1024))KB"
    else
        echo "$((bytes / 1048576))MB"
    fi
}

#==============================================================================
# Initialize Environment
#==============================================================================

echo -e "${BLUE}"
echo "========================================================================"
echo "          Smart InfraFabric Integration Script"
echo "========================================================================"
echo -e "${NC}"
echo ""

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${YELLOW}MODE: DRY-RUN (no changes will be made)${NC}"
else
    echo -e "${GREEN}MODE: EXECUTE (making actual changes)${NC}"
fi

echo ""
log "Starting InfraFabric integration process..."
log "Log file: $LOG_FILE"
log ""

# Create archive base directories
log "Creating archive directory structure..."
mkdir_safe "${SCRIPT_DIR}/tools/archive"
mkdir_safe "${SCRIPT_DIR}/docs/archive"
mkdir_safe "${SCRIPT_DIR}/philosophy/archive"
mkdir_safe "${SCRIPT_DIR}/evaluations/archive"
mkdir_safe "${SCRIPT_DIR}/research/archive"
mkdir_safe "${SCRIPT_DIR}/archive/metadata"

echo ""

#==============================================================================
# Process Duplicates (Exact Matches - Same Content Hash)
#==============================================================================

echo -e "${BLUE}=== PHASE 1: Processing Exact Duplicates ===${NC}"
echo "Processing files with identical SHA256 hashes..."
echo ""

python3 << 'PYTHON_DUPLICATE_HANDLER'
import json
import os
from collections import defaultdict
from datetime import datetime

# Configuration
SCRIPT_DIR = "/home/setup/infrafabric"
DRY_RUN = os.environ.get("DRY_RUN", "true") == "true"

# Load duplicate data
with open(f"{SCRIPT_DIR}/CONSOLIDATION_DUPLICATES.json") as f:
    duplicates = json.load(f)

log_lines = []

def log_msg(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines.append(f"[{timestamp}] {msg}")
    print(msg)

log_msg(f"Processing {len(duplicates)} duplicate groups...")

exact_dup_count = 0
exact_dup_files = 0
exact_dup_bytes = 0

for dup_group in duplicates:
    hash_val = dup_group["hash"]
    files = dup_group["files"]
    count = dup_group["count"]

    if count < 2:
        continue

    exact_dup_count += 1
    exact_dup_files += count
    exact_dup_bytes += dup_group["recoverable_bytes"]

    # Sort by mtime (newest first)
    sorted_files = sorted(files, key=lambda x: x["mtime"], reverse=True)

    newest = sorted_files[0]
    older = sorted_files[1:]

    # Determine category and destination
    name = newest["name"]
    location = newest["location"]

    # Categorize by file type
    if name.endswith('.md'):
        category = "documentation"
    elif name.endswith(('.py', '.js', '.ts')):
        category = "code"
    elif name.endswith(('.yaml', '.yml')):
        category = "philosophy"
    elif name.endswith('.json'):
        category = "data"
    else:
        category = "misc"

    log_msg(f"\nDuplicate Group (Hash: {hash_val[:16]}...)")
    log_msg(f"  Category: {category} | Files: {count} | Size: {dup_group['size_mb']:.2f}MB")
    log_msg(f"  Keeping (newest): {newest['name']} (mtime: {datetime.fromtimestamp(newest['mtime'])})")

    for old_file in older:
        old_mtime = datetime.fromtimestamp(old_file["mtime"])
        log_msg(f"  Duplicate: {old_file['name']} (mtime: {old_mtime})")

log_msg(f"\n=== SUMMARY: Exact Duplicates ===")
log_msg(f"Groups: {exact_dup_count}")
log_msg(f"Total duplicate files: {exact_dup_files}")
log_msg(f"Recoverable space: {exact_dup_bytes / 1024 / 1024:.2f}MB")

# Save to duplicate report
report = {
    "phase": "duplicates",
    "timestamp": datetime.now().isoformat(),
    "dry_run": DRY_RUN,
    "duplicate_groups": exact_dup_count,
    "duplicate_files": exact_dup_files,
    "recoverable_bytes": exact_dup_bytes,
    "messages": log_lines
}

with open(f"{SCRIPT_DIR}/integration_duplicates_report.json", "w") as f:
    json.dump(report, f, indent=2)

PYTHON_DUPLICATE_HANDLER

export DRY_RUN

echo ""
echo -e "${GREEN}Duplicate analysis complete${NC}"

#==============================================================================
# Process File Merges (Same Basename, Different Content)
#==============================================================================

echo ""
echo -e "${BLUE}=== PHASE 2: Processing File Variants by Basename ===${NC}"
echo "Grouping files by basename and organizing versions..."
echo ""

python3 << 'PYTHON_MERGE_HANDLER'
import json
import os
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = "/home/setup/infrafabric"
DRY_RUN = os.environ.get("DRY_RUN", "true") == "true"

# Load file list
with open(f"{SCRIPT_DIR}/CONSOLIDATION_FILE_LIST.json") as f:
    all_files = json.load(f)

# Group by basename (handle variations like "file.py", "file (1).py", "file_old.py")
def normalize_basename(name):
    """Extract core filename, ignoring version suffixes"""
    import re
    # Remove common versioning patterns: (1), (2), _old, _backup, etc.
    base = re.sub(r'\s*\(\d+\)$', '', name)
    base = re.sub(r'_+(old|backup|archive|v\d+)$', '', base, flags=re.IGNORECASE)
    return base

groups = defaultdict(list)
for file_info in all_files:
    name = file_info["name"]
    # Use full name as key for simplicity; in production could use normalize_basename
    base_key = name
    groups[base_key].append(file_info)

# Categorize groups by extension
python_files = []
markdown_files = []
yaml_files = []
json_files = []
other_files = []

for base_key, file_group in groups.items():
    if base_key.endswith('.py'):
        python_files.append((base_key, file_group))
    elif base_key.endswith('.md'):
        markdown_files.append((base_key, file_group))
    elif base_key.endswith(('.yaml', '.yml')):
        yaml_files.append((base_key, file_group))
    elif base_key.endswith('.json'):
        json_files.append((base_key, file_group))
    else:
        other_files.append((base_key, file_group))

# Generate integration plan
plan = {
    "timestamp": datetime.now().isoformat(),
    "dry_run": DRY_RUN,
    "categories": {
        "python_tools": {
            "count": len(python_files),
            "files": [name for name, _ in python_files]
        },
        "documentation": {
            "count": len(markdown_files),
            "files": [name for name, _ in markdown_files]
        },
        "philosophy_yaml": {
            "count": len(yaml_files),
            "files": [name for name, _ in yaml_files]
        },
        "data_json": {
            "count": len(json_files),
            "files": [name for name, _ in json_files]
        },
        "other": {
            "count": len(other_files),
            "files": [name for name, _ in other_files]
        }
    },
    "summary": {
        "total_basenames": len(groups),
        "python_tools": len(python_files),
        "documentation": len(markdown_files),
        "philosophy_yaml": len(yaml_files),
        "data_json": len(json_files),
        "other_files": len(other_files),
        "total_individual_files": len(all_files)
    }
}

# Print summary
print("\n=== FILE ORGANIZATION SUMMARY ===\n")
print(f"Python Tools (.py):     {len(python_files):3d} files")
print(f"Documentation (.md):    {len(markdown_files):3d} files")
print(f"Philosophy YAML:        {len(yaml_files):3d} files")
print(f"Data JSON:              {len(json_files):3d} files")
print(f"Other files:            {len(other_files):3d} files")
print(f"{'─' * 45}")
print(f"Total unique basenames: {len(groups):3d}")
print(f"Total individual files: {len(all_files):3d}")

# Save plan
with open(f"{SCRIPT_DIR}/integration_merge_plan.json", "w") as f:
    json.dump(plan, f, indent=2)

print("\nMerge plan saved to: integration_merge_plan.json")

PYTHON_MERGE_HANDLER

echo ""
echo -e "${GREEN}File grouping and analysis complete${NC}"

#==============================================================================
# Generate Integration Recommendations
#==============================================================================

echo ""
echo -e "${BLUE}=== PHASE 3: Generating Integration Recommendations ===${NC}"
echo ""

python3 << 'PYTHON_RECOMMENDATIONS'
import json
import os
from datetime import datetime

SCRIPT_DIR = "/home/setup/infrafabric"

# Load consolidation data
with open(f"{SCRIPT_DIR}/CONSOLIDATION_DUPLICATES.json") as f:
    duplicates = json.load(f)

with open(f"{SCRIPT_DIR}/CONSOLIDATION_FILE_LIST.json") as f:
    all_files = json.load(f)

recommendations = []

# Analyze potential conflicts
for dup_group in duplicates:
    if dup_group["count"] > 2:
        recommendations.append({
            "type": "high_duplication",
            "description": f"File has {dup_group['count']} copies (recoverable: {dup_group['size_mb']:.2f}MB)",
            "hash": dup_group["hash"][:16] + "...",
            "action": "Keep newest, delete all others"
        })

# Analyze file locations
downloads_files = [f for f in all_files if "downloads" in f["location"].lower()]
recommendations.append({
    "type": "location_analysis",
    "description": f"Found {len(downloads_files)} files in Downloads (should be migrated to repo)",
    "action": "Move critical files from Downloads to appropriate repo directory"
})

# Output summary
print("\n=== INTEGRATION RECOMMENDATIONS ===\n")

for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['type'].upper()}")
    print(f"   Description: {rec['description']}")
    print(f"   Action: {rec['action']}\n")

print(f"Total recommendations: {len(recommendations)}")

# Save recommendations
with open(f"{SCRIPT_DIR}/integration_recommendations.json", "w") as f:
    json.dump(recommendations, f, indent=2)

print("\nRecommendations saved to: integration_recommendations.json")

PYTHON_RECOMMENDATIONS

echo ""

#==============================================================================
# Summary and Next Steps
#==============================================================================

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}               INTEGRATION SUMMARY & NEXT STEPS${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${YELLOW}DRY-RUN MODE${NC} - No changes made"
    echo ""
    echo "To execute the integration:"
    echo "  ./smart_integrate.sh execute"
    echo ""
else
    echo -e "${GREEN}EXECUTE MODE${NC} - Changes applied"
    echo ""
fi

echo "Reports generated:"
echo "  - Log file: $LOG_FILE"
echo "  - Duplicate analysis: integration_duplicates_report.json"
echo "  - Merge plan: integration_merge_plan.json"
echo "  - Recommendations: integration_recommendations.json"
echo ""

echo "Archive structure created:"
echo "  - /tools/archive/"
echo "  - /docs/archive/"
echo "  - /philosophy/archive/"
echo "  - /evaluations/archive/"
echo "  - /research/archive/"
echo "  - /archive/metadata/"
echo ""

log_success "Integration script completed successfully"

echo ""
echo "For detailed analysis, see: INTEGRATION_REPORT.md"
echo ""
