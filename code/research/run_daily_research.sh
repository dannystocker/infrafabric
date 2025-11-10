#!/bin/bash
# IF.mission.arxiv - Daily Research Automation
# Master orchestration script for 7-day execution plan

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STRATEGY="${1:-conservative}"  # conservative | nuclear | custom
DAY="${2:-1}"  # 1-7

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}IF.mission.arxiv - Day ${DAY} Research${NC}"
echo -e "${BLUE}Strategy: ${STRATEGY}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}ERROR: ANTHROPIC_API_KEY not set${NC}"
    echo "Export your API key:"
    echo "  export ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
fi

# Check dependencies
if ! python3 -c "import anthropic" 2>/dev/null; then
    echo -e "${YELLOW}Installing anthropic SDK...${NC}"
    pip install --user anthropic
fi

if ! python3 -c "import feedparser" 2>/dev/null; then
    echo -e "${YELLOW}Installing feedparser...${NC}"
    pip install --user feedparser
fi

# Timestamp for outputs
TIMESTAMP=$(date -u +"%Y%m%d-%H%M%S")

# Execute based on day and strategy
case $DAY in
    1)
        echo -e "${GREEN}Day 1: Discovery Phase${NC}"
        echo "→ Fetching recent papers + finding endorsers..."
        python3 find_arxiv_endorsers.py

        echo ""
        echo "→ Running gap analysis..."
        python3 if_gap_analysis.py

        if [ "$STRATEGY" == "nuclear" ]; then
            echo ""
            echo "→ Checking FANG/Anthropic/Epic affiliations..."
            python3 check_fang_affiliations.py
        fi
        ;;

    2)
        echo -e "${GREEN}Day 2: Deep Profiling${NC}"
        echo "→ Analyzing endorser interest + employment potential..."
        python3 analyze_endorser_interest.py

        if [ "$STRATEGY" == "nuclear" ]; then
            echo ""
            echo "→ Running extended gap analysis (100 papers)..."
            python3 if_gap_analysis.py
        fi
        ;;

    3)
        echo -e "${GREEN}Day 3: Email Generation${NC}"
        echo "→ Generating personalized outreach emails (top 20)..."
        python3 generate_endorser_emails.py

        if [ "$STRATEGY" == "nuclear" ]; then
            echo ""
            echo "→ Checking affiliations for email batch..."
            python3 check_fang_affiliations.py
        fi
        ;;

    4)
        echo -e "${GREEN}Day 4: Continuous Discovery${NC}"
        echo "→ Fetching fresh papers..."
        python3 find_arxiv_endorsers.py

        echo ""
        echo "→ Running gap analysis..."
        python3 if_gap_analysis.py

        if [ "$STRATEGY" == "nuclear" ]; then
            echo ""
            echo "→ Checking affiliations..."
            python3 check_fang_affiliations.py
        fi
        ;;

    5)
        echo -e "${GREEN}Day 5: Continuous Discovery${NC}"
        echo "→ Fetching fresh papers..."
        python3 find_arxiv_endorsers.py

        echo ""
        echo "→ Running gap analysis..."
        python3 if_gap_analysis.py

        echo ""
        echo "→ Updating endorser interest scores..."
        python3 analyze_endorser_interest.py
        ;;

    6)
        echo -e "${GREEN}Day 6: Integration Proposals${NC}"
        echo "→ Running deep-dive gap analysis..."
        python3 if_gap_analysis.py

        if [ "$STRATEGY" == "nuclear" ]; then
            echo ""
            echo "→ Generating integration proposals for IF.guard..."
            # Note: Would need separate integration proposal generator
            echo "   (Manual review recommended for integration proposals)"
        fi
        ;;

    7)
        echo -e "${GREEN}Day 7: Batch Outreach${NC}"
        echo "→ Generating emails for top 50 endorsers..."
        python3 generate_endorser_emails.py

        echo ""
        echo "→ Final endorser interest analysis..."
        python3 analyze_endorser_interest.py

        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${BLUE}7-Day Research Campaign Complete!${NC}"
        echo -e "${BLUE}========================================${NC}"
        ;;

    *)
        echo -e "${RED}Invalid day: $DAY (must be 1-7)${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Day ${DAY} complete${NC}"
echo ""
echo "📊 Generated outputs (gitignored):"
ls -lh ARXIV_ENDORSERS.* 2>/dev/null || true
ls -lh IF_GAP_ANALYSIS.* 2>/dev/null || true
ls -lh IF_ENDORSER_STRATEGY.* 2>/dev/null || true
ls -lh IF_ENDORSER_EMAILS.* 2>/dev/null || true

echo ""
echo "💡 Next steps:"
if [ $DAY -lt 7 ]; then
    NEXT_DAY=$((DAY + 1))
    echo "   ./run_daily_research.sh $STRATEGY $NEXT_DAY"
else
    echo "   1. Review IF_ENDORSER_EMAILS.*.md for outreach"
    echo "   2. Send personalized emails to top candidates"
    echo "   3. Review IF_GAP_ANALYSIS.*.md for integration opportunities"
    echo "   4. Queue top integrations for IF.guard deliberation"
fi
echo ""
