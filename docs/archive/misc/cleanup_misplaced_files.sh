#!/bin/bash

##############################################################################
# File Reconciliation Cleanup Script
# Purpose: Safely clean, archive, and reorganize misplaced files
# Date: 2025-11-15
# Scope: Operates across multiple locations
# Safety: All operations move files to archive/ - nothing is deleted
##############################################################################

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INFRAFABRIC_DIR="/home/setup/infrafabric"
ARCHIVE_DIR="${INFRAFABRIC_DIR}/archive"
SCRIPT_LOG="${INFRAFABRIC_DIR}/cleanup_log_$(date +%Y%m%d_%H%M%S).txt"
DRY_RUN=${1:-"false"}

##############################################################################
# Logging Functions
##############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$SCRIPT_LOG"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "$SCRIPT_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$SCRIPT_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$SCRIPT_LOG"
}

##############################################################################
# Utility Functions
##############################################################################

initialize_archive() {
    log_info "Initializing archive directory structure..."

    mkdir -p "${ARCHIVE_DIR}/"{benchmarks,evaluations,obsolete,temp-files,logs} 2>/dev/null || {
        log_warning "Some archive directories may already exist"
    }

    log_success "Archive structure ready: $ARCHIVE_DIR"
}

confirm_action() {
    if [ "$DRY_RUN" = "true" ]; then
        return 0
    fi

    read -p "Continue with this action? (yes/no): " -r
    [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]
}

##############################################################################
# PHASE 1: Immediate Cleanup (Safe - No Content Loss)
##############################################################################

cleanup_temporary_session_files() {
    log_info "PHASE 1: Cleaning temporary session files from /tmp"

    local tmp_files=$(find /tmp -maxdepth 1 -name "claude-*-cwd" 2>/dev/null | wc -l)

    if [ "$tmp_files" -eq 0 ]; then
        log_warning "No temporary session files found in /tmp"
        return 0
    fi

    log_info "Found $tmp_files temporary session files to remove"

    if [ "$DRY_RUN" = "true" ]; then
        log_info "[DRY RUN] Would remove the following files:"
        find /tmp -maxdepth 1 -name "claude-*-cwd" | head -10
        [ "$tmp_files" -gt 10 ] && log_info "... and $(($tmp_files - 10)) more files"
        return 0
    fi

    # Remove session files
    local removed=0
    while IFS= read -r file; do
        rm -f "$file" && ((removed++))
    done < <(find /tmp -maxdepth 1 -name "claude-*-cwd" 2>/dev/null)

    log_success "Removed $removed temporary session files"
    echo "Removed files from /tmp: $removed" >> "$SCRIPT_LOG"
}

cleanup_temporary_scripts() {
    log_info "Cleaning temporary utility scripts from /tmp"

    local scripts=(
        "/tmp/comprehensive_file_scan.sh"
        "/tmp/extended_scan_quick.sh"
        "/tmp/detailed_orphan_report.py"
    )

    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ "$DRY_RUN" = "true" ]; then
                log_info "[DRY RUN] Would remove: $script"
            else
                rm -f "$script"
                log_success "Removed: $script"
            fi
        fi
    done
}

##############################################################################
# PHASE 2: Archive Old Artifacts
##############################################################################

archive_benchmark_reports() {
    log_info "PHASE 2: Archiving old benchmark reports (2025-11-08)"

    local report_dir="${INFRAFABRIC_DIR}/code/yologuard/reports"

    if [ ! -d "$report_dir" ]; then
        log_warning "Benchmark reports directory not found: $report_dir"
        return 0
    fi

    local old_reports=$(find "$report_dir" -maxdepth 1 -name "20251108*" -type d 2>/dev/null | wc -l)

    if [ "$old_reports" -eq 0 ]; then
        log_info "No old benchmark reports found to archive"
        return 0
    fi

    log_info "Found $old_reports old benchmark report directories"

    if [ "$DRY_RUN" = "true" ]; then
        log_info "[DRY RUN] Would archive the following directories:"
        find "$report_dir" -maxdepth 1 -name "20251108*" -type d
        return 0
    fi

    local archive_benchmarks="${ARCHIVE_DIR}/benchmarks/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$archive_benchmarks"

    while IFS= read -r report_path; do
        local report_name=$(basename "$report_path")
        log_info "Archiving: $report_name"
        mv "$report_path" "$archive_benchmarks/"
    done < <(find "$report_dir" -maxdepth 1 -name "20251108*" -type d 2>/dev/null)

    log_success "Archived $old_reports benchmark report directories to: $archive_benchmarks"
}

archive_old_evaluations() {
    log_info "Archiving old evaluation artifacts"

    local evidence_dir="${INFRAFABRIC_DIR}/docs/evidence"

    if [ ! -d "$evidence_dir" ]; then
        log_warning "Evidence directory not found: $evidence_dir"
        return 0
    fi

    local old_evals=$(find "$evidence_dir" -maxdepth 1 -name "*_[0-9]*.yaml" -type f 2>/dev/null | wc -l)

    if [ "$old_evals" -eq 0 ]; then
        log_info "No old evaluation files found to archive"
        return 0
    fi

    log_info "Found $old_evals old evaluation YAML files"

    if [ "$DRY_RUN" = "true" ]; then
        log_info "[DRY RUN] Would archive the following files:"
        find "$evidence_dir" -maxdepth 1 -name "*_[0-9]*.yaml" -type f
        return 0
    fi

    local archive_evals="${ARCHIVE_DIR}/evaluations/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$archive_evals"

    while IFS= read -r eval_file; do
        log_info "Archiving: $(basename "$eval_file")"
        mv "$eval_file" "$archive_evals/"
    done < <(find "$evidence_dir" -maxdepth 1 -name "*_[0-9]*.yaml" -type f 2>/dev/null)

    log_success "Archived $old_evals evaluation files to: $archive_evals"
}

archive_obsolete_files() {
    log_info "Archiving obsolete system files"

    local obsolete_files=(
        "/home/setup/full_inventory.txt"
    )

    for file in "${obsolete_files[@]}"; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            log_info "Found obsolete file: $filename"

            if [ "$DRY_RUN" = "true" ]; then
                log_info "[DRY RUN] Would archive: $file"
            else
                mv "$file" "${ARCHIVE_DIR}/obsolete/"
                log_success "Archived: $filename"
            fi
        fi
    done
}

##############################################################################
# PHASE 3: Verification and Reporting
##############################################################################

verify_cleanup() {
    log_info "PHASE 3: Verifying cleanup results"

    # Check that session files are gone
    local remaining_sessions=$(find /tmp -maxdepth 1 -name "claude-*-cwd" 2>/dev/null | wc -l)
    if [ "$remaining_sessions" -eq 0 ]; then
        log_success "Verification: All session files removed from /tmp"
    else
        log_warning "Verification: $remaining_sessions session files still remain in /tmp"
    fi

    # Check archive directory size
    if [ -d "$ARCHIVE_DIR" ]; then
        local archive_size=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | awk '{print $1}')
        log_info "Archive directory size: $archive_size"
    fi
}

generate_report() {
    log_info "Generating cleanup summary report"

    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local report_file="${ARCHIVE_DIR}/CLEANUP_REPORT_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# File Reconciliation Cleanup Report

**Date:** $timestamp
**Dry Run:** $DRY_RUN
**Archive Location:** $ARCHIVE_DIR

## Summary

- Temporary session files cleaned: Completed
- Old benchmark reports archived: Completed
- Old evaluation files archived: Completed
- Obsolete files archived: Completed

## Archive Contents

\`\`\`
$(find "$ARCHIVE_DIR" -type d | head -20)
\`\`\`

## Log File

Complete details in: $SCRIPT_LOG

EOF

    log_success "Cleanup report saved to: $report_file"
}

##############################################################################
# Dry Run Information
##############################################################################

show_dry_run_summary() {
    log_info "====== DRY RUN MODE ======"
    log_info "No files will be modified"
    log_info "This is a simulation showing what would be done"
    log_info ""
    log_info "To execute the actual cleanup, run:"
    log_info "  $0 false"
    log_info ""
}

##############################################################################
# Main Execution
##############################################################################

main() {
    echo "=========================================="
    echo "File Reconciliation Cleanup Script"
    echo "=========================================="
    echo ""

    if [ ! -w "$INFRAFABRIC_DIR" ]; then
        log_error "Cannot write to $INFRAFABRIC_DIR"
        log_error "Please check permissions"
        exit 1
    fi

    # Create log file
    touch "$SCRIPT_LOG" || {
        log_error "Cannot create log file at $SCRIPT_LOG"
        exit 1
    }

    log_info "Cleanup script started"
    log_info "Mode: $([ "$DRY_RUN" = "true" ] && echo "DRY RUN" || echo "EXECUTE")"
    log_info "Archive directory: $ARCHIVE_DIR"
    log_info "Log file: $SCRIPT_LOG"
    echo ""

    if [ "$DRY_RUN" = "true" ]; then
        show_dry_run_summary
    fi

    # Execute phases
    initialize_archive
    echo ""

    log_info "========== PHASE 1: Immediate Cleanup =========="
    cleanup_temporary_session_files
    cleanup_temporary_scripts
    echo ""

    log_info "========== PHASE 2: Archive Old Artifacts =========="
    archive_benchmark_reports
    archive_old_evaluations
    archive_obsolete_files
    echo ""

    log_info "========== PHASE 3: Verification =========="
    verify_cleanup
    echo ""

    # Generate report only if not dry run
    if [ "$DRY_RUN" = "false" ]; then
        generate_report
    fi

    log_success "Cleanup script completed"
    log_info "Log saved to: $SCRIPT_LOG"
}

##############################################################################
# Error Handling
##############################################################################

trap 'log_error "Script interrupted"; exit 1' INT TERM

##############################################################################
# Entry Point
##############################################################################

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
