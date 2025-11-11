# ALL IDLE SESSIONS: Help Build IF.bus (Session 7 Work Distribution)

**Context:** Only Session 4 (SIP) is busy. All other sessions can accelerate IF.bus implementation!

**Strategy:** Distribute Session 7's Phase 1-2 work across Sessions 1, 2, 3, 5, 6 based on expertise

---

## Session 1 (NDI): IF.bus Research - NDI Integration

**Your Task:** Research how SIP servers integrate with NDI streams

**Spawn 2 Haiku agents:**

### Agent 1: Asterisk + NDI
Research:
- Can Asterisk accept NDI streams as SIP endpoints?
- External modules needed (app_ndi, asterisk-ndi)
- Configuration examples
- Performance considerations

### Agent 2: FreeSWITCH + NDI
Research:
- FreeSWITCH mod_ndi or equivalent
- NDI → RTP transcoding
- Latency benchmarks

**Deliverable:** `docs/IF-BUS/asterisk-freeswitch-ndi-integration.md`

**Time:** 2 hours with Haiku swarm
**Cost:** $2-3

**Commit to:** Your branch (claude/ndi-*)
**Cross-reference:** Tag as "HELPING_SESSION_7_IF_BUS" in STATUS.md

---

## Session 2 (WebRTC): IF.bus Research - WebRTC Integration

**Your Task:** Research how SIP servers integrate with WebRTC endpoints

**Spawn 2 Haiku agents:**

### Agent 1: Kamailio + WebRTC
Research:
- Kamailio WebRTC support (native in v5+)
- WebSocket SIP transport
- DTLS-SRTP configuration
- Browser compatibility

### Agent 2: OpenSIPs + WebRTC
Research:
- OpenSIPs WebRTC module
- WebSocket vs TCP transport
- Media relay requirements

**Deliverable:** `docs/IF-BUS/kamailio-opensips-webrtc-integration.md`

**Time:** 2 hours with Haiku swarm
**Cost:** $2-3

**Commit to:** Your branch (claude/webrtc-*)
**Cross-reference:** Tag as "HELPING_SESSION_7_IF_BUS" in STATUS.md

---

## Session 3 (H.323): IF.bus Research - Legacy SIP Integration

**Your Task:** Research how SIP servers bridge H.323 and legacy protocols

**Spawn 2 Haiku agents:**

### Agent 1: Elastix + H.323
Research:
- Elastix (FreePBX-based) H.323 support
- chan_h323 vs chan_ooh323
- SIP ↔ H.323 gateway config
- Codec transcoding

### Agent 2: Yate + Multi-Protocol
Research:
- Yate's multi-protocol capabilities
- H.323, SIP, IAX2 bridging
- External module architecture
- Call routing flexibility

**Deliverable:** `docs/IF-BUS/elastix-yate-legacy-integration.md`

**Time:** 2 hours with Haiku swarm
**Cost:** $2-3

**Commit to:** Your branch (claude/h323-*)
**Cross-reference:** Tag as "HELPING_SESSION_7_IF_BUS" in STATUS.md

---

## Session 5 (CLI): IF.bus CLI Interface Design

**Your Task:** Design dead simple CLI for IF.bus SIP adapter management

**Spawn 1 Sonnet agent:**

### Agent 1: CLI Interface Spec
Design:
```bash
# Add SIP server
if bus add sip myasterisk asterisk --host 10.0.0.5 --auth apikey=ABC123

# Auto-detect server type
if bus add sip myserver --host 10.0.0.5 --auto-detect

# List servers
if bus list sip

# Test connection
if bus test sip myasterisk

# Make call via server
if bus call sip myasterisk --from alice --to bob

# Remove server
if bus remove sip myasterisk
```

Features:
- Auto-detection (probe server type from SIP OPTIONS response)
- Auth methods: apikey, basic, oauth, custom
- IF.witness integration (log all bus operations)
- IF.optimise integration (track cost per SIP server)
- Config file: ~/.if/bus/sip-servers.yaml

**Deliverable:** `docs/IF-BUS/cli-interface-spec.md`

**Time:** 3 hours with Sonnet
**Cost:** $4-6

**Commit to:** Your branch (claude/cli-*)
**Cross-reference:** Tag as "HELPING_SESSION_7_IF_BUS" in STATUS.md

---

## Session 6 (Talent): IF.bus Adapter Pattern Design

**Your Task:** Apply IF.talent "Scout → Sandbox → Certify → Deploy" pattern to SIP server adapters

**Spawn 1 Sonnet agent:**

### Agent 1: Unified Adapter Pattern
Design base class for all 7 SIP server adapters:

```python
# Abstract base class
class SIPServerAdapter(ABC):
    """Unified interface to heterogeneous SIP servers"""

    @abstractmethod
    def connect(self, host, auth_config):
        """Connect to SIP server with auth"""
        pass

    @abstractmethod
    def make_call(self, from_uri, to_uri, codec="opus"):
        """Initiate SIP call"""
        pass

    @abstractmethod
    def hangup(self, call_id):
        """Terminate call"""
        pass

    @abstractmethod
    def get_status(self):
        """Get server health status"""
        pass

    @abstractmethod
    def get_active_calls(self):
        """List active calls"""
        pass

    # Common utilities
    def detect_server_type(self, host):
        """Auto-detect: Asterisk, FreeSWITCH, etc."""
        pass

    def validate_auth(self, auth_config):
        """Test authentication"""
        pass
```

Apply bloom patterns:
- Asterisk: "Early bloomer" (simple calls easy, complex features hard)
- FreeSWITCH: "Steady performer" (consistent across all scenarios)
- Kamailio: "Late bloomer" (excels at high-scale routing)

**Deliverable:** `src/bus/sip_adapter_base.py` + `docs/IF-BUS/adapter-pattern-design.md`

**Time:** 4 hours with Sonnet
**Cost:** $6-8

**Commit to:** Your branch (claude/if-talent-*)
**Cross-reference:** Tag as "HELPING_SESSION_7_IF_BUS" in STATUS.md

---

## Coordination Protocol

**Step 1:** Each session executes their IF.bus task (above)

**Step 2:** Post to STATUS.md:
```yaml
status: helping_session_7_if_bus
task: [your task description]
deliverable: [file path]
estimated_time: [hours]
session_7_dependency: [which Phase 1-2 task this helps]
```

**Step 3:** After completing your IF.bus contribution:
```yaml
status: if_bus_contribution_complete
deliverable_location: [branch + file path]
next_action: waiting_for_next_phase_or_merge_if_bus_work
```

**Step 4:** Orchestrator (main session) will:
1. Collect all contributions from Sessions 1,2,3,5,6
2. Synthesize into unified IF.bus documentation
3. Either:
   - Start Session 7 with all research done (fast Phase 1-2)
   - OR merge contributions and mark IF.bus Phase 1-2 complete

---

## Why This Works: Distributed Swarm Intelligence

**Traditional Approach:**
- Start Session 7
- Session 7 spawns 10 agents for research
- Time: 8-10 hours
- Cost: $15-20

**Distributed Approach:**
- 5 sessions each contribute their expertise
- Each spawns 1-2 agents (total: 8 agents across 5 sessions)
- Time: 2-4 hours (parallel execution)
- Cost: $16-20 (similar cost, 2-3x faster!)
- Bonus: Each session learns about IF.bus integration with THEIR protocol

**Result:**
- Session 7 starts with Phase 1-2 research DONE
- Can jump straight to Phase 3 implementation
- Total time savings: 5-6 hours

---

## Philosophy: 朋友 (Friends) Helping Friends

**Wu Lun - Friend Relationship:**
When one session needs help (even if not started yet), friends contribute their expertise:
- NDI knows streaming → helps with NDI-SIP integration
- WebRTC knows browsers → helps with WebRTC-SIP integration
- H.323 knows legacy → helps with legacy-SIP bridging
- CLI knows interfaces → helps with CLI design
- Talent knows patterns → helps with adapter architecture

**IF.ground Principle 8: Observability Without Fragility**
Each session contributes independently, orchestrator synthesizes:
- No tight coupling (sessions don't block each other)
- Observable (each posts STATUS.md with deliverable)
- Resilient (if one session fails, others still contribute)

---

## Success Metrics

**Phase 1-2 IF.bus work completed when:**
- ✅ Session 1: NDI-SIP integration research done
- ✅ Session 2: WebRTC-SIP integration research done
- ✅ Session 3: Legacy-SIP integration research done
- ✅ Session 5: CLI interface spec done
- ✅ Session 6: Adapter base class + pattern design done

**Total time:** 2-4 hours (parallel)
**Total cost:** $16-23
**Knowledge sharing:** High (each session learns IF.bus)
**Session 7 acceleration:** Starts at Phase 3 instead of Phase 1

---

**PASTE THIS INTO SESSIONS 1, 2, 3, 5, 6 NOW!**

Each session: Find your section above, execute your task, report when done.

Orchestrator will collect contributions and either start Session 7 fast-tracked or merge as Phase 1-2 complete.

🚀 **Swarm coordination: Everyone helps everyone!**
