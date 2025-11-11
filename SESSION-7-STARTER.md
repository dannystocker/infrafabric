# Session 7: IF.bus SIP Adapters - START HERE

**Copy-paste this entire block into a new Claude session:**

---

```
Hi Claude! You are Session 7: IF.bus SIP Adapters

YOUR MISSION: Build dead simple CLI integration with 7 major SIP servers (Asterisk, FreeSWITCH, Kamailio, OpenSIPs, Elastix, Yate, Flexisip)

GAME CHANGER: IF.swarm gets direct control of real SIP infrastructure - provision, scale, failover

REPOSITORY:
- GitHub: https://github.com/dannystocker/infrafabric
- Clone: git clone https://github.com/dannystocker/infrafabric.git
- Branch: claude/if-bus-sip-adapters (create from main)

SETUP:
1. cd infrafabric
2. git checkout -b claude/if-bus-sip-adapters
3. git fetch origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
4. git show origin/claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy:INSTRUCTIONS-SESSION-7-PHASES-1-10.md > INSTRUCTIONS-SESSION-7-PHASES-1-10.md

YOUR DELIVERABLES (10 Phases):

Phase 1: IF.search swarm (10 Haiku agents)
- Research APIs for all 7 SIP servers
- Output: Unified API matrix comparing auth, call control, features

Phase 2: Adapter implementation (7 Sonnet agents)
- Build Python adapters for each server
- Unified interface: connect(), make_call(), hangup(), get_status()

Phase 3: Dead simple CLI
- Command: if bus add sip <name> <type> --auth <method>
- Auto-detect server type, auto-configure, auto-failover

Phases 4-10: Call control, advanced features, multi-server orchestration, production deployment, monitoring, AI routing, full autonomy

COORDINATION WITH OTHER SESSIONS:
- Session 4 (SIP): You provide infrastructure control for their SIP proxy
- Session 5 (CLI): You use their IF.witness for provenance tracking
- Session 6 (Talent): You use their bloom patterns for AI model routing

PHILOSOPHY GROUNDING:
- Wu Lun 朋友 (Friends): SIP servers are "friends" we bring into the team
- IF.ground Principle 2: Validate with toolchain (test all 7 servers)
- IF.TTT: Traceable (git), Transparent (docs), Trustworthy (tests)

BEGIN IMPLEMENTATION:
1. Read full instructions:
   cat INSTRUCTIONS-SESSION-7-PHASES-1-10.md

2. Start Phase 1 (IF.search swarm):
   - Spawn 10 Haiku agents
   - Each researches 1 SIP server API
   - Agent 8: Unified pattern design
   - Agent 9: Auth comparison
   - Agent 10: Coordinator + synthesis

3. Create STATUS.md:
   ```yaml
   session: session-7-if-bus
   status: phase_1_in_progress
   branch: claude/if-bus-sip-adapters
   current_phase: 1
   agents_spawned: 10
   ```

4. Post after each phase completes:
   - Create STATUS-PHASE-[N].md
   - Commit, push to your branch
   - Auto-poll for next phase instructions

AUTO-POLLING (after completing current phase):
```bash
while true; do
  git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy --quiet
  if [ -f INSTRUCTIONS-SESSION-7-PHASE-*.md ]; then
    cat INSTRUCTIONS-SESSION-7-PHASE-*.md
    break
  fi
  sleep 30  # Poll every 30 seconds
done
```

VELOCITY TARGET:
- Sequential: 40-50 hours
- With swarms: 8-10 hours (5x gain)
- Cost: $40-60 total

WHY THIS MATTERS:
Before: IF.swarm talks SIP protocol, but doesn't control infrastructure
After: IF.swarm can provision Asterisk servers, route calls across FreeSWITCH clusters, control Kamailio load balancers, auto-scale SIP capacity - becoming a production telecom infrastructure controller

GO NOW - BUILD THE SIP INFRASTRUCTURE LAYER! 🚀

Report back when Phase 1 (API research) is complete.
```

---

**This is your copy-paste starter for Session 7.**

Save this prompt, paste into new Claude session when ready to start IF.bus implementation.
