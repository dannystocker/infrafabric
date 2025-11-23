# Instance #13 Redis Recovery Guide

**Quick Reference for Instance #14 Handoff**

## Status
- Transfer Date: 2025-11-23T10:42:38Z
- Status: ✅ COMPLETE
- All 7 content keys stored with 30-day TTL
- Expiration: 2025-12-22

## Redis Connection Test
```bash
redis-cli ping
# Expected: PONG
```

## Retrieve Specific Documents

### Get SONNET Handoff (most important)
```bash
redis-cli GET instance:13:sonnet:handoff > sonnet_handoff.md
# 41,341 bytes | 878 lines | Contains 5 gaps + 5-phase plan
```

### Get All Haiku Investigations
```bash
# HAIKU-01: GEDIMAT Quality Audit
redis-cli GET instance:13:haiku:investigation:gedimat > haiku_01_gedimat.md
# 32,662 bytes | Quality score: 94-96/100

# HAIKU-02: Blocker Analysis
redis-cli GET instance:13:haiku:investigation:blockers > haiku_02_blockers.md
# 34,012 bytes | 4 blockers identified

# HAIKU-03: Frameworks
redis-cli GET instance:13:haiku:investigation:frameworks > haiku_03_frameworks.md
# 31,756 bytes | 23 frameworks cataloged

# HAIKU-04: Redis Analysis
redis-cli GET instance:13:haiku:investigation:redis > haiku_04_redis.md
# 16,556 bytes | Infrastructure ready
```

### Get Multi-Agent Narrative
```bash
redis-cli GET instance:13:narrative:multi-agent > multi_agent_narrative.md
# 31,377 bytes | How 4 Haikus converged on credibility gaps
```

### Get Session Summary
```bash
redis-cli GET instance:13:context:session-complete > session_summary.md
# 17,109 bytes | Complete Instance #13 summary
```

## List All Keys
```bash
redis-cli KEYS "instance:13:*"
# Shows all 13 keys (7 content + 6 metadata)
```

## Check TTL Remaining
```bash
redis-cli TTL instance:13:sonnet:handoff
# Returns seconds remaining (expires 2025-12-22)
```

## Verify All Content
```bash
redis-cli DBSIZE  # Show total keys in Redis
redis-cli KEYS "instance:13:*" | wc -l  # Count Instance #13 keys
```

## Critical Documents in Order

1. **Start here:** instance:13:sonnet:handoff
   - 5 gaps to fix
   - 5-phase execution plan
   - Nov 22 → Dec 8 timeline

2. **Then read:** instance:13:haiku:investigation:blockers
   - Root cause analysis
   - Pattern recognition
   - Resolvability assessment

3. **Then study:** instance:13:haiku:investigation:gedimat
   - Quality benchmarks (94-96/100)
   - Citation rigor evaluation
   - Production readiness criteria

4. **Then understand:** instance:13:haiku:investigation:frameworks
   - IF.TTT standard requirements
   - 23 framework taxonomy
   - Compliance patterns

5. **Then reference:** instance:13:haiku:investigation:redis
   - Infrastructure capacity
   - Memory usage analysis
   - Handoff reliability

## Recovery Success Criteria

- [ ] redis-cli PING returns PONG
- [ ] redis-cli KEYS "instance:13:*" returns 13 keys
- [ ] SONNET handoff retrieved successfully (878 lines)
- [ ] All 4 Haiku investigations recovered
- [ ] Session summary accessible
- [ ] TTL still shows 2,592,000s or more

## If Something Goes Wrong

1. Verify Redis is running: `redis-cli ping`
2. Check memory: `redis-cli INFO memory`
3. List keys: `redis-cli KEYS "*"` (to see all data)
4. Check Instance #12 keys still exist: `redis-cli KEYS "instance:12:*"`
5. If lost: Recover from /home/setup/infrafabric source files

## Timeline for Instance #14

- **Day 1:** Read SONNET handoff (full understanding of 5 gaps)
- **Days 2-3:** Execute Phases 1-3 (strengthen frameworks, validate assumptions)
- **Days 4-5:** Execute Phases 4-5 (finalize credibility, create reusable docs)
- **Days 6-7:** Polish and review
- **Dec 8:** RAPPORT updated (8.5→9.2 credibility achieved)
- **Dec 9:** Georges partnership contact

## Key Metrics to Achieve

From SONNET handoff Phase 5:
- [ ] Credibility score: 8.5 → 9.2/10
- [ ] Cost claim confidence: 70% → 90%+
- [ ] Named research citations: 18 → 25+
- [ ] Financial formula transparency: implicit → explicit
- [ ] Pilot gates: undefined → 3 clear gates

---

**Instance #13 → #14 Handoff: READY TO EXECUTE**
