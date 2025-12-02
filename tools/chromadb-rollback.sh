#!/bin/bash

################################################################################
# ChromaDB Rollback Wrapper - Safe CLI for Emergency Recovery
################################################################################
#
# Mission: Provide easy command-line access to snapshot and rollback tools
# with safety checks and automated trigger support.
#
# Usage:
#   ./chromadb-rollback.sh snapshot create [--name "snapshot_name"]
#   ./chromadb-rollback.sh snapshot list
#   ./chromadb-rollback.sh snapshot verify <snapshot_id>
#   ./chromadb-rollback.sh rollback <snapshot_id> [--dry-run] [--partial]
#   ./chromadb-rollback.sh status
#   ./chromadb-rollback.sh validate
#
# Author: A28 (ChromaDB Migration Rollback Agent)
# Citation: if://design/chromadb-rollback-wrapper-v1.0-2025-11-30
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="${SCRIPT_DIR}"
SNAPSHOT_DIR="${SNAPSHOT_DIR:-/home/setup/infrafabric/chromadb_snapshots}"
CHROMADB_URL="${CHROMADB_URL:-http://localhost:8000}"
LOG_DIR="${SNAPSHOT_DIR}/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# UTILITY FUNCTIONS
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $*"
}

log_error() {
    echo -e "${RED}[✗]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $*"
}

print_usage() {
    cat << EOF
ChromaDB Rollback Wrapper - Safe CLI for Emergency Recovery

USAGE:
    ${0##*/} <command> [options]

SNAPSHOT COMMANDS:
    snapshot create             Create pre-migration snapshot
    snapshot list               List all available snapshots
    snapshot verify <id>        Verify snapshot integrity
    snapshot info <id>          Get snapshot details
    snapshot cleanup            Remove expired snapshots

ROLLBACK COMMANDS:
    rollback <id>               Perform full rollback from snapshot
    rollback <id> --dry-run     Test rollback without actual restore
    rollback <id> --partial     Partial rollback (failed collections only)
    status                      Show recent rollback operations
    audit-log                   View complete audit log

MANAGEMENT COMMANDS:
    validate                    Validate rollback system configuration
    health-check                Check ChromaDB connectivity
    cleanup                     Remove old snapshots and logs

ENVIRONMENT VARIABLES:
    CHROMADB_URL               ChromaDB server URL (default: http://localhost:8000)
    SNAPSHOT_DIR               Snapshot storage directory (default: /home/setup/infrafabric/chromadb_snapshots)

EXAMPLES:
    # Create snapshot before migration
    ${0##*/} snapshot create --name "pre_migration_2025-11-30"

    # List snapshots
    ${0##*/} snapshot list

    # Verify snapshot
    ${0##*/} snapshot verify snapshot_20251130_143022

    # Perform full rollback
    ${0##*/} rollback snapshot_20251130_143022

    # Dry-run rollback
    ${0##*/} rollback snapshot_20251130_143022 --dry-run

    # Partial rollback
    ${0##*/} rollback snapshot_20251130_143022 --partial

    # Check rollback status
    ${0##*/} status

    # View audit log
    ${0##*/} audit-log

SAFETY FEATURES:
    - Pre-rollback snapshot verification
    - Dry-run mode for testing
    - Audit logging of all operations
    - Automatic integrity checks
    - Checksum validation (SHA-256)

EOF
    exit 1
}

create_directories() {
    mkdir -p "${SNAPSHOT_DIR}"
    mkdir -p "${SNAPSHOT_DIR}/manifests"
    mkdir -p "${LOG_DIR}"
    mkdir -p "${SNAPSHOT_DIR}/.tmp"
    mkdir -p "${SNAPSHOT_DIR}/.restore"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
}

check_chromadb_connection() {
    log_info "Checking ChromaDB connection..."

    if [[ "${CHROMADB_URL}" == http* ]]; then
        local host=$(echo "${CHROMADB_URL}" | sed 's|http.*://||' | cut -d: -f1)
        local port=$(echo "${CHROMADB_URL}" | sed 's|.*:||')

        if timeout 5 bash -c "echo > /dev/tcp/${host}/${port}" 2>/dev/null; then
            log_success "Connected to ${CHROMADB_URL}"
            return 0
        else
            log_error "Cannot connect to ChromaDB at ${CHROMADB_URL}"
            return 1
        fi
    else
        if [[ -d "${CHROMADB_URL}" ]]; then
            log_success "Local ChromaDB storage found: ${CHROMADB_URL}"
            return 0
        else
            log_error "ChromaDB directory not found: ${CHROMADB_URL}"
            return 1
        fi
    fi
}

################################################################################
# SNAPSHOT COMMANDS
################################################################################

cmd_snapshot_create() {
    local snapshot_name=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name)
                snapshot_name="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    log_info "Creating snapshot..."

    local cmd="python3 '${TOOLS_DIR}/chromadb_snapshot.py' \
        --chromadb-url '${CHROMADB_URL}' \
        --action create \
        --snapshot-dir '${SNAPSHOT_DIR}'"

    if [[ -n "${snapshot_name}" ]]; then
        cmd="${cmd} --snapshot-name '${snapshot_name}'"
    fi

    if eval "${cmd}"; then
        log_success "Snapshot created successfully"
        return 0
    else
        log_error "Snapshot creation failed"
        return 1
    fi
}

cmd_snapshot_list() {
    log_info "Listing available snapshots..."

    python3 "${TOOLS_DIR}/chromadb_snapshot.py" \
        --chromadb-url "${CHROMADB_URL}" \
        --action list \
        --snapshot-dir "${SNAPSHOT_DIR}"
}

cmd_snapshot_verify() {
    local snapshot_id="$1"

    if [[ -z "${snapshot_id}" ]]; then
        log_error "Snapshot ID required"
        exit 1
    fi

    log_info "Verifying snapshot: ${snapshot_id}..."

    if python3 "${TOOLS_DIR}/chromadb_snapshot.py" \
        --chromadb-url "${CHROMADB_URL}" \
        --action verify \
        --snapshot-id "${snapshot_id}" \
        --snapshot-dir "${SNAPSHOT_DIR}"; then
        log_success "Snapshot verified"
        return 0
    else
        log_error "Snapshot verification failed"
        return 1
    fi
}

cmd_snapshot_info() {
    local snapshot_id="$1"

    if [[ -z "${snapshot_id}" ]]; then
        log_error "Snapshot ID required"
        exit 1
    fi

    log_info "Getting snapshot info: ${snapshot_id}..."

    python3 "${TOOLS_DIR}/chromadb_snapshot.py" \
        --chromadb-url "${CHROMADB_URL}" \
        --action info \
        --snapshot-id "${snapshot_id}" \
        --snapshot-dir "${SNAPSHOT_DIR}"
}

cmd_snapshot_cleanup() {
    log_warning "This will delete expired snapshots (older than 7 days)"
    read -p "Continue? (y/N): " -r

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleanup cancelled"
        return 0
    fi

    log_info "Cleaning up expired snapshots..."

    python3 "${TOOLS_DIR}/chromadb_snapshot.py" \
        --action cleanup \
        --snapshot-dir "${SNAPSHOT_DIR}"
}

################################################################################
# ROLLBACK COMMANDS
################################################################################

cmd_rollback() {
    local snapshot_id="$1"
    shift

    if [[ -z "${snapshot_id}" ]]; then
        log_error "Snapshot ID required"
        exit 1
    fi

    local dry_run=false
    local partial=false
    local failed_collections=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                dry_run=true
                shift
                ;;
            --partial)
                partial=true
                shift
                ;;
            --failed-collections)
                failed_collections="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    if [[ "${dry_run}" == true ]]; then
        log_warning "DRY-RUN MODE: No actual rollback will be performed"
    else
        log_warning "CRITICAL: This will RESTORE ChromaDB from snapshot: ${snapshot_id}"
        log_warning "All data written since snapshot will be LOST"
        read -p "Are you sure? Type 'yes' to confirm: " -r

        if [[ ! $REPLY == "yes" ]]; then
            log_info "Rollback cancelled"
            return 0
        fi
    fi

    log_info "Starting rollback from snapshot: ${snapshot_id}..."

    local cmd="python3 '${TOOLS_DIR}/chromadb_rollback.py' \
        --chromadb-url '${CHROMADB_URL}' \
        --action rollback \
        --snapshot-id '${snapshot_id}' \
        --snapshot-dir '${SNAPSHOT_DIR}'"

    if [[ "${dry_run}" == true ]]; then
        cmd="${cmd} --dry-run"
    fi

    if [[ "${partial}" == true ]]; then
        cmd="${cmd} --partial"
        if [[ -n "${failed_collections}" ]]; then
            cmd="${cmd} --failed-collections '${failed_collections}'"
        fi
    fi

    if eval "${cmd}"; then
        log_success "Rollback completed successfully"
        return 0
    else
        log_error "Rollback failed"
        return 1
    fi
}

cmd_status() {
    log_info "Showing rollback status..."

    python3 "${TOOLS_DIR}/chromadb_rollback.py" \
        --action status \
        --snapshot-dir "${SNAPSHOT_DIR}"
}

cmd_audit_log() {
    log_info "Showing audit log..."

    python3 "${TOOLS_DIR}/chromadb_rollback.py" \
        --action audit-log \
        --snapshot-dir "${SNAPSHOT_DIR}"
}

################################################################################
# MANAGEMENT COMMANDS
################################################################################

cmd_validate() {
    log_info "Validating rollback system..."

    local errors=0

    # Check Python
    log_info "Checking Python 3..."
    if command -v python3 &> /dev/null; then
        log_success "Python 3 found: $(python3 --version)"
    else
        log_error "Python 3 not found"
        ((errors++))
    fi

    # Check required scripts
    log_info "Checking required scripts..."
    for script in chromadb_snapshot.py chromadb_rollback.py; do
        if [[ -f "${TOOLS_DIR}/${script}" ]]; then
            log_success "Found: ${script}"
        else
            log_error "Missing: ${script}"
            ((errors++))
        fi
    done

    # Check ChromaDB connection
    log_info "Checking ChromaDB connection..."
    if check_chromadb_connection; then
        log_success "ChromaDB is accessible"
    else
        log_error "ChromaDB is not accessible"
        ((errors++))
    fi

    # Check snapshot directory
    log_info "Checking snapshot directory..."
    if [[ -d "${SNAPSHOT_DIR}" ]]; then
        log_success "Snapshot directory exists: ${SNAPSHOT_DIR}"
        local snapshot_count=$(find "${SNAPSHOT_DIR}/manifests" -name "*.json" 2>/dev/null | wc -l)
        log_info "Available snapshots: ${snapshot_count}"
    else
        log_error "Snapshot directory not found: ${SNAPSHOT_DIR}"
        ((errors++))
    fi

    # Check disk space
    log_info "Checking disk space..."
    local available_space=$(df -BM "${SNAPSHOT_DIR}" | awk 'NR==2 {print $4}' | sed 's/M//')
    if [[ ${available_space} -gt 1000 ]]; then
        log_success "Sufficient disk space: ${available_space}M available"
    else
        log_warning "Low disk space: ${available_space}M available"
    fi

    if [[ ${errors} -eq 0 ]]; then
        log_success "All validation checks passed"
        return 0
    else
        log_error "Validation found ${errors} issue(s)"
        return 1
    fi
}

cmd_health_check() {
    log_info "Running health check..."

    if check_chromadb_connection; then
        log_success "ChromaDB health check passed"
        return 0
    else
        log_error "ChromaDB health check failed"
        return 1
    fi
}

################################################################################
# MAIN
################################################################################

main() {
    if [[ $# -eq 0 ]]; then
        print_usage
    fi

    # Create necessary directories
    create_directories

    # Check Python
    check_python

    local command="$1"
    shift || true

    case "${command}" in
        snapshot)
            if [[ $# -eq 0 ]]; then
                log_error "Snapshot subcommand required"
                exit 1
            fi

            local subcommand="$1"
            shift || true

            case "${subcommand}" in
                create)
                    cmd_snapshot_create "$@"
                    ;;
                list)
                    cmd_snapshot_list "$@"
                    ;;
                verify)
                    cmd_snapshot_verify "$@"
                    ;;
                info)
                    cmd_snapshot_info "$@"
                    ;;
                cleanup)
                    cmd_snapshot_cleanup "$@"
                    ;;
                *)
                    log_error "Unknown snapshot subcommand: ${subcommand}"
                    exit 1
                    ;;
            esac
            ;;

        rollback)
            cmd_rollback "$@"
            ;;

        status)
            cmd_status "$@"
            ;;

        audit-log)
            cmd_audit_log "$@"
            ;;

        validate)
            cmd_validate "$@"
            ;;

        health-check)
            cmd_health_check "$@"
            ;;

        cleanup)
            cmd_snapshot_cleanup "$@"
            ;;

        help)
            print_usage
            ;;

        *)
            log_error "Unknown command: ${command}"
            print_usage
            ;;
    esac
}

main "$@"
