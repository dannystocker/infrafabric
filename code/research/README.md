# IF.mission.arxiv - Research Curation & Endorser Discovery

## Purpose

Dual-purpose arXiv cs.AI analysis:
1. **Find potential endorsers** for InfraFabric paper submission
2. **Identify integration concepts** for IF framework expansion

## Scripts

### `find_arxiv_endorsers.py` (Current)
- Extracts authors from recent cs.AI papers
- Ranks by relevance to InfraFabric topics
- Outputs endorser candidates with contact strategy

**Usage:**
```bash
python3 find_arxiv_endorsers.py
```

**Outputs:**
- `ARXIV_ENDORSERS.<timestamp>.md` - Human-readable report
- `arxiv_endorsers.<timestamp>.json` - Structured data

### `if_swarm_research.py` (Full Pipeline)
- 4-agent analysis (Safety, Systems, Methods, Ethics)
- IF.trace/IF.citation compliant
- Token cost tracking (IF.optimise)

**Usage:**
```bash
# STUB mode (no API key needed)
python3 if_swarm_research.py

# With real LLM (set PROVIDER env var)
PROVIDER=openai OPENAI_API_KEY=sk-... python3 if_swarm_research.py
```

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

