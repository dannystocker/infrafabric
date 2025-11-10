# IF.mission.arxiv - Research Curation & Endorser Discovery

## Purpose

Dual-purpose arXiv cs.AI analysis:
1. **Find potential endorsers** for InfraFabric paper submission (PRIMARY)
2. **Identify integration concepts** for IF framework expansion (SECONDARY)

## Quick Start

### One-Command Daily Execution
```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run Day 1 (conservative strategy)
./run_daily_research.sh conservative 1

# Run Day 1 (nuclear strategy - 10× more analysis)
./run_daily_research.sh nuclear 1
```

### Manual Execution (Step-by-Step)

```bash
# 1. Find endorsers
python3 find_arxiv_endorsers.py

# 2. Analyze papers for patterns
python3 if_gap_analysis.py

# 3. Check affiliations (Anthropic, Epic Games, FANG)
python3 check_fang_affiliations.py

# 4. Score endorser interest + employment potential
python3 analyze_endorser_interest.py

# 5. Generate personalized emails
python3 generate_endorser_emails.py
```

---

## Scripts Reference

### Core Pipeline

#### `find_arxiv_endorsers.py`
**Purpose:** Extract and rank potential endorsers from arXiv cs.AI papers

**How it works:**
- Fetches recent papers from arXiv RSS feed
- Scores by IF keyword relevance (multi-agent, coordination, safety, verification)
- Ranks authors by cumulative relevance across all papers

**Usage:**
```bash
python3 find_arxiv_endorsers.py
```

**Outputs:**
- `ARXIV_ENDORSERS.<timestamp>.md` - Human-readable report with top 20
- `arxiv_endorsers.<timestamp>.json` - Structured data for further analysis

---

#### `if_gap_analysis.py`
**Purpose:** Use Haiku to identify IF patterns + gaps in papers

**How it works:**
- Analyzes paper abstracts with Haiku agent
- Identifies patterns matching existing IF components
- Identifies gaps (missing IF capabilities)
- Generates integration proposals

**Usage:**
```bash
python3 if_gap_analysis.py  # Analyzes top 5 papers
```

**Outputs:**
- `IF_GAP_ANALYSIS.<timestamp>.md` - Patterns, gaps, integration ideas

---

#### `check_fang_affiliations.py`
**Purpose:** Web scrape arXiv pages for institutional affiliations

**How it works:**
- Takes endorser JSON as input
- Scrapes actual arXiv paper pages
- Detects affiliations: Anthropic, Epic Games, FANG, major AI labs

**Usage:**
```bash
python3 check_fang_affiliations.py  # Uses most recent arxiv_endorsers.*.json
```

**Outputs:**
- Console report with affiliation matches
- Highlights 🔥 ANTHROPIC and 🎮 EPIC_GAMES candidates

---

### Strategic Analysis

#### `analyze_endorser_interest.py`
**Purpose:** Score endorsers for interest probability + employment potential

**How it works:**
- **Interest probability** (0-100%): Alignment with IF focus areas
- **Employment potential** (0-100%): Signals for job opportunities
- **Priority flags**: 🔥 ANTHROPIC, 🎮 EPIC_GAMES, ⭐ MAJOR_LAB, ✨ HIGH_INTEREST_ACADEMIC

**Usage:**
```bash
python3 analyze_endorser_interest.py
```

**Outputs:**
- `IF_ENDORSER_STRATEGY.<timestamp>.md` - Strategic targeting report
- Sorted by composite score: relevance + interest + employment

---

#### `generate_endorser_emails.py`
**Purpose:** Automated personalized outreach email generation (Haiku)

**How it works:**
- Uses Haiku to draft personalized emails
- Includes: Paper praise, IF overview, endorsement request, collaboration invitation
- Framing: "invite collaboration" NOT "seek approval" (their work is published)

**Usage:**
```bash
python3 generate_endorser_emails.py  # Top 20 endorsers
```

**Outputs:**
- `IF_ENDORSER_EMAILS.<timestamp>.md` - Review document with all drafts
- `IF_ENDORSER_EMAILS.<timestamp>.json` - Structured data for automation

**Email structure:**
1. Subject line (mentions their work)
2. Praise specific paper
3. IF overview (Guardian Council, 111% GitHub-parity validation)
4. Relevance connection (their concepts → IF components)
5. Dual request: arXiv endorsement + collaboration invitation
6. Closing with contact info

---

### Optimization

#### `optimize_anthropic_credit.py`
**Purpose:** Calculate optimal $974 budget usage over 7 days

**How it works:**
- Haiku pricing: $0.25/$1.25 per million tokens (input/output)
- Estimates cost per analysis type
- Generates 7-day schedule with daily targets

**Usage:**
```bash
python3 optimize_anthropic_credit.py
```

**Outputs:**
- Console report with cost breakdown
- `ANTHROPIC_CREDIT_SCHEDULE.<timestamp>.json` - Schedule for automation

**Key insights:**
- Theoretical capacity: 649k analyses
- Practical capacity: ~3.5k analyses (data constrained)
- Conservative strategy: $15 (1.6% budget)
- Nuclear strategy: $110 (11% budget)

---

#### `run_daily_research.sh`
**Purpose:** Master orchestration script for 7-day execution

**Usage:**
```bash
# Syntax: ./run_daily_research.sh [strategy] [day]

# Conservative strategy (minimal spend, high quality)
./run_daily_research.sh conservative 1

# Nuclear strategy (10× coverage, still only $110)
./run_daily_research.sh nuclear 1
```

**What it does:**
- Checks for ANTHROPIC_API_KEY
- Installs dependencies if needed
- Runs appropriate scripts for each day
- Tracks outputs and provides next steps

**7-Day Schedule:**
- **Day 1:** Discovery (find endorsers + gap analysis)
- **Day 2:** Deep profiling (interest scoring)
- **Day 3:** Email generation (top 20)
- **Day 4-5:** Continuous discovery (fresh papers)
- **Day 6:** Integration proposals (deep-dive)
- **Day 7:** Batch outreach (50 emails)

---

### Legacy

#### `if_swarm_research.py`
**Purpose:** Full 4-agent analysis pipeline (from GPT-5 spec)

**Features:**
- 4-agent analysis (Safety, Systems, Methods, Ethics)
- IF.trace/IF.citation compliant (jsonl outputs)
- Token cost tracking (IF.optimise)
- STUB mode + OpenAI/Anthropic adapters

**Usage:**
```bash
# STUB mode (no API key needed)
python3 if_swarm_research.py

# With real LLM
PROVIDER=openai OPENAI_API_KEY=sk-... python3 if_swarm_research.py
```

**Status:** Superseded by modular pipeline (find_arxiv_endorsers.py + if_gap_analysis.py)

## Integration with InfraFabric

**Components Used:**
- `IF.mission` - Scheduled task execution
- `IF.swarm` - Multi-agent parallel analysis
- `IF.trace` - Execution logging (jsonl)
- `IF.citation` - Paper provenance tracking
- `IF.optimise` - Token cost monitoring

**Scheduling:**
- GitHub Actions: `.github/workflows/arxiv_research.yml` (recommended)
- Cron: `0 */12 * * *` for 12-hour cadence
- Manual: Run scripts on-demand

## Top Endorser Candidates (2025-11-10)

1. **Dongsu Lee, Amy Zhang** - Multi-agent coordination via flow matching
2. **Ishan Kavathekar et al** - TAMAS: Multi-agent LLM safety
3. **L. J. Janse van Rensburg** - Citation auditing protocols

See `ARXIV_ENDORSERS.*.md` for full list with contact strategies.

## Integration Opportunities

Papers with concepts worth integrating:
- **Citation Auditing** → Enhance IF.citation with zero-assumption protocols
- **Flow Matching Coordination** → Add to IF.swarm coordination mechanisms
- **Adversarial Multi-Agent Testing** → IF.guard stress testing framework

