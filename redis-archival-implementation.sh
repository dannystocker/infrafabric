#!/bin/bash
###############################################################################
# REDIS CONTEXT ARCHIVAL IMPLEMENTATION SCRIPT
# Generated: 2025-11-23
# Status: READY TO EXECUTE (awaiting approval)
#
# This script loads discovered context files to Redis with appropriate TTLs
# Run only after user approval of REDIS-ARCHIVAL-CATALOG.md
###############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
PHASE="${1:-phase1}"  # phase1, phase2, phase3, or all
DRY_RUN="${DRY_RUN:-false}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  REDIS CONTEXT ARCHIVAL IMPLEMENTATION                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

###############################################################################
# PHASE 1: CRITICAL INFRASTRUCTURE (6 files, ~150K memory)
###############################################################################

load_phase1() {
    echo -e "${YELLOW}[PHASE 1] Loading critical infrastructure files...${NC}"
    echo ""

    # 1. SESSION-RESUME.md (Master session state)
    echo "Loading: instance:master:session-resume"
    CONTENT=$(cat /home/setup/infrafabric/SESSION-RESUME.md)
    SIZE=${#CONTENT}
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [DRY RUN] Would store $SIZE bytes, TTL: 90 days"
    else
        echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            -x SET instance:master:session-resume > /dev/null
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            EXPIRE instance:master:session-resume $((90 * 24 * 3600)) > /dev/null
        echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: 90 days${NC}"
    fi

    # 2. INSTANCE-XX-ZERO-CONTEXT-STARTER.md (Bootstrap template)
    echo "Loading: instance:template:zero-context-bootstrap"
    CONTENT=$(cat /home/setup/infrafabric/INSTANCE-XX-ZERO-CONTEXT-STARTER.md)
    SIZE=${#CONTENT}
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [DRY RUN] Would store $SIZE bytes, TTL: 365 days"
    else
        echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            -x SET instance:template:zero-context-bootstrap > /dev/null
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            EXPIRE instance:template:zero-context-bootstrap $((365 * 24 * 3600)) > /dev/null
        echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: 365 days${NC}"
    fi

    # 3. INSTANCE-13-HANDOFF-COMPLETION.md (Most recent completion)
    echo "Loading: instance:13:completion-state"
    CONTENT=$(cat /home/setup/infrafabric/INSTANCE-13-HANDOFF-COMPLETION.md)
    SIZE=${#CONTENT}
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [DRY RUN] Would store $SIZE bytes, TTL: 45 days"
    else
        echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            -x SET instance:13:completion-state > /dev/null
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            EXPIRE instance:13:completion-state $((45 * 24 * 3600)) > /dev/null
        echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: 45 days${NC}"
    fi

    # 4. INSTANCE-13-REDIS-TRANSFER-SUMMARY.txt (Transfer verification log)
    echo "Loading: instance:13:redis-transfer-log"
    CONTENT=$(cat /home/setup/infrafabric/INSTANCE-13-REDIS-TRANSFER-SUMMARY.txt)
    SIZE=${#CONTENT}
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [DRY RUN] Would store $SIZE bytes, TTL: 60 days"
    else
        echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            -x SET instance:13:redis-transfer-log > /dev/null
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            EXPIRE instance:13:redis-transfer-log $((60 * 24 * 3600)) > /dev/null
        echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: 60 days${NC}"
    fi

    # 5. REDIS-CONTEXT-GUIDE.md (How to use Redis)
    echo "Loading: shared:redis-usage-guide"
    CONTENT=$(cat /home/setup/infrafabric/REDIS-CONTEXT-GUIDE.md)
    SIZE=${#CONTENT}
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [DRY RUN] Would store $SIZE bytes, TTL: 365 days"
    else
        echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            -x SET shared:redis-usage-guide > /dev/null
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            EXPIRE shared:redis-usage-guide $((365 * 24 * 3600)) > /dev/null
        echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: 365 days${NC}"
    fi

    # 6. INSTANCE-13-REDIS-RECOVERY-GUIDE.md (Disaster recovery)
    echo "Loading: shared:redis-recovery-procedures"
    CONTENT=$(cat /home/setup/infrafabric/INSTANCE-13-REDIS-RECOVERY-GUIDE.md)
    SIZE=${#CONTENT}
    if [ "$DRY_RUN" = "true" ]; then
        echo "  [DRY RUN] Would store $SIZE bytes, TTL: 180 days"
    else
        echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            -x SET shared:redis-recovery-procedures > /dev/null
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
            EXPIRE shared:redis-recovery-procedures $((180 * 24 * 3600)) > /dev/null
        echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: 180 days${NC}"
    fi

    echo ""
    echo -e "${GREEN}[PHASE 1] Complete! 6 critical infrastructure files loaded.${NC}"
    echo ""
}

###############################################################################
# PHASE 2: RESEARCH & FINDINGS (10 files, ~420K memory)
###############################################################################

load_phase2() {
    echo -e "${YELLOW}[PHASE 2] Loading research & findings files...${NC}"
    echo ""

    # Array of files to load: (redis_key, file_path, ttl_days)
    declare -a FILES=(
        "research:haiku-02-blocker-analysis|/home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-02-BLOCKER-ANALYSIS.md|90"
        "research:haiku-01-gedimat-investigation|/home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-01-GEDIMAT-INVESTIGATION.md|90"
        "research:haiku-03-methodology-templates|/home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-03-METHODOLOGY-TEMPLATES.md|180"
        "research:haiku-04-redis-investigation|/home/setup/infrafabric/HAIKU-SESSION-NARRATIVES/HAIKU-04-REDIS-INVESTIGATION.md|90"
        "instance:12:georges-compliance-report-full|/home/setup/infrafabric/IF-TTT-COMPLIANCE-AUDIT-GEORGES-REPORT.md|90"
        "instance:12:georges-compliance-narrative|/home/setup/infrafabric/IF-TTT-COMPLIANCE-AUDIT-GEORGES-NARRATION.md|90"
        "shared:intelligence-findings-core|/home/setup/infrafabric/IF-INTELLIGENCE-FINDINGS-SUMMARY.md|90"
        "shared:citations-instances-8-10-json|/home/setup/infrafabric/IF-TTT-CITATION-INDEX-INSTANCES-8-10.json|90"
        "shared:intelligence-procedures-methodology|/home/setup/infrafabric/IF-INTELLIGENCE-PROCEDURE.md|180"
        "shared:redis-verification-procedures|/home/setup/infrafabric/REDIS-TRANSFER-VERIFICATION.md|180"
    )

    for file_spec in "${FILES[@]}"; do
        IFS='|' read -r redis_key file_path ttl_days <<< "$file_spec"

        echo "Loading: $redis_key"
        if [ ! -f "$file_path" ]; then
            echo -e "  ${RED}✗ File not found: $file_path${NC}"
            continue
        fi

        CONTENT=$(cat "$file_path")
        SIZE=${#CONTENT}
        TTL_SECONDS=$((ttl_days * 24 * 3600))

        if [ "$DRY_RUN" = "true" ]; then
            echo "  [DRY RUN] Would store $SIZE bytes, TTL: $ttl_days days"
        else
            echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
                -x SET "$redis_key" > /dev/null
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
                EXPIRE "$redis_key" "$TTL_SECONDS" > /dev/null
            echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: ${ttl_days} days${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}[PHASE 2] Complete! 10 research & findings files loaded.${NC}"
    echo ""
}

###############################################################################
# PHASE 3: OPTIONAL NARRATIVES (6 files, ~225K memory)
###############################################################################

load_phase3() {
    echo -e "${YELLOW}[PHASE 3] Loading optional narratives & references...${NC}"
    echo ""

    declare -a FILES=(
        "narrative:ep-13-partnership-infrastructure|/home/setup/infrafabric/papers/narrations/if.instance.ep.13_the-partnership-infrastructure-built.md|90"
        "narrative:ep-14-research-architect|/home/setup/infrafabric/papers/narrations/if.instance.ep.14_the-research-architect-reflection.md|90"
        "narrative:ep-15-methodology-enhancement|/home/setup/infrafabric/papers/narrations/if.instance.ep.15_methodology-enhancement-swarm.md|90"
        "shared:handoff-completion-checklist|/home/setup/infrafabric/HANDOFF-COMPLETE-CHECKLIST.md|365"
        "shared:redis-quick-reference|/home/setup/infrafabric/REDIS-QUICK-REFERENCE.md|365"
        "instance:14:gedimat-quantum-state|/home/setup/infrafabric/SESSION-INSTANCE-14-GEDIMAT-STATE.md|60"
    )

    for file_spec in "${FILES[@]}"; do
        IFS='|' read -r redis_key file_path ttl_days <<< "$file_spec"

        echo "Loading: $redis_key"
        if [ ! -f "$file_path" ]; then
            echo -e "  ${RED}✗ File not found: $file_path${NC}"
            continue
        fi

        CONTENT=$(cat "$file_path")
        SIZE=${#CONTENT}
        TTL_SECONDS=$((ttl_days * 24 * 3600))

        if [ "$DRY_RUN" = "true" ]; then
            echo "  [DRY RUN] Would store $SIZE bytes, TTL: $ttl_days days"
        else
            echo "$CONTENT" | redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
                -x SET "$redis_key" > /dev/null
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" \
                EXPIRE "$redis_key" "$TTL_SECONDS" > /dev/null
            echo -e "  ${GREEN}✓ Stored ${SIZE} bytes, TTL: ${ttl_days} days${NC}"
        fi
    done

    echo ""
    echo -e "${GREEN}[PHASE 3] Complete! 6 optional narrative files loaded.${NC}"
    echo ""
}

###############################################################################
# VERIFICATION
###############################################################################

verify_archival() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}VERIFICATION REPORT${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    CRITICAL_KEYS=(
        "instance:master:session-resume"
        "instance:template:zero-context-bootstrap"
        "instance:13:completion-state"
        "instance:13:redis-transfer-log"
        "shared:redis-usage-guide"
        "shared:redis-recovery-procedures"
    )

    echo "Checking critical keys:"
    FOUND=0
    for key in "${CRITICAL_KEYS[@]}"; do
        TTL=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" TTL "$key" 2>/dev/null || echo "-2")
        if [ "$TTL" -gt 0 ]; then
            SIZE=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" STRLEN "$key" 2>/dev/null || echo "0")
            echo -e "  ${GREEN}✓ $key${NC} (${SIZE} bytes, TTL: ${TTL}s)"
            ((FOUND++))
        else
            echo -e "  ${RED}✗ $key - NOT FOUND OR EXPIRED${NC}"
        fi
    done

    echo ""
    echo "Summary:"
    TOTAL_KEYS=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" KEYS "*" 2>/dev/null | wc -l)
    echo "  Total Redis keys: $TOTAL_KEYS"
    echo "  Critical keys found: $FOUND / 6"

    MEMORY=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO memory 2>/dev/null | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
    echo "  Redis memory usage: $MEMORY"
    echo ""

    if [ "$FOUND" -eq 6 ]; then
        echo -e "${GREEN}✓ VERIFICATION PASSED - All critical keys present${NC}"
    else
        echo -e "${RED}✗ VERIFICATION FAILED - Some critical keys missing${NC}"
    fi
    echo ""
}

###############################################################################
# MAIN
###############################################################################

# Check Redis connectivity
if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Cannot connect to Redis at $REDIS_HOST:$REDIS_PORT${NC}"
    echo "Please ensure Redis is running and accessible."
    exit 1
fi

echo "Redis Connection: ${GREEN}✓${NC} ($REDIS_HOST:$REDIS_PORT)"
echo ""

# Execute requested phases
case "$PHASE" in
    phase1)
        load_phase1
        verify_archival
        ;;
    phase2)
        load_phase2
        verify_archival
        ;;
    phase3)
        load_phase3
        verify_archival
        ;;
    all)
        load_phase1
        load_phase2
        load_phase3
        verify_archival
        ;;
    *)
        echo "Usage: $0 [phase1|phase2|phase3|all]"
        echo ""
        echo "Examples:"
        echo "  $0 phase1              # Load critical infrastructure (6 files)"
        echo "  $0 phase2              # Load research & findings (10 files)"
        echo "  $0 phase3              # Load optional narratives (6 files)"
        echo "  $0 all                 # Load all files"
        echo ""
        echo "Environment Variables:"
        echo "  REDIS_HOST             Default: localhost"
        echo "  REDIS_PORT             Default: 6379"
        echo "  DRY_RUN=true           Preview without storing"
        exit 1
        ;;
esac

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Archival process complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
