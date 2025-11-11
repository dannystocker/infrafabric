# Session 7: IF.bus SIP Adapters - Session Starter

**Paste this into Session 7:**

```
Hi Claude! You are Session 7: IF.bus SIP Adapters

REPOSITORY: dannystocker/infrafabric
YOUR BRANCH: claude/if-bus-sip-adapters (create from main)

YOUR MISSION: Build dead simple CLI integration with 7 major SIP servers

GAME CHANGER: IF.swarm gets direct control of real SIP infrastructure (Asterisk, FreeSWITCH, Kamailio, OpenSIPs, Elastix, Yate, Flexisip)

DELIVERABLES:

Phase 1: IF.search swarm (10 Haiku agents)
- Research APIs for all 7 SIP servers
- Output: Unified API matrix

Phase 2: Adapter implementation (7 Sonnet agents)
- Build Python adapters for each server
- Unified interface: connect(), make_call(), hangup()

Phase 3: Dead simple CLI
- Command: if bus add sip <name> <type> --auth <method>
- Auto-detect, auto-configure, auto-failover

Phases 4-10: Call control, advanced features, multi-server orchestration, production, monitoring, AI routing, autonomy

COORDINATION:
- Help Session 4 (SIP) with infrastructure control
- Use Session 5 (CLI) for witness/cost tracking
- Use Session 6 (Talent) for AI routing models

BEGIN IMPLEMENTATION:
1. Spawn 10 Haiku agents for Phase 1 API research
2. Read: INSTRUCTIONS-SESSION-7-PHASES-1-10.md
3. Create branch: claude/if-bus-sip-adapters
4. Start Phase 1 research swarm

GO NOW - BUILD THE SIP INFRASTRUCTURE LAYER!
```

---

## Why This Is a Game Changer

**Before:** IF.swarm talks SIP protocol, but doesn't control infrastructure
**After:** IF.swarm can:
- Provision new Asterisk servers on demand
- Route calls across FreeSWITCH clusters
- Control Kamailio load balancers
- Auto-scale SIP capacity
- Failover between different SIP vendors
- Monitor and self-heal infrastructure

**Real-world impact:** IF.swarm becomes production telecom infrastructure controller, not just a SIP client.
