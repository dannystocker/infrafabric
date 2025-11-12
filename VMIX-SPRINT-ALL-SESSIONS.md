# VMIX INTEGRATION SPRINT - ALL SESSIONS (1-7)

**Mission:** Integrate vMix live video production software with InfraFabric

**Context:** vMix is professional live video production software with multiple APIs (REST, TCP, Function-based)

**Resources:**
- https://vmixapi.com/
- https://www.vmix.com/help25/index.htm?DeveloperAPI.html
- https://www.vmix.com/help25/index.htm?TCPAPI.html
- https://github.com/curtgrimes/vmix-rest-api

---

## IDENTIFY YOUR SESSION FIRST

Run: `git branch --show-current`

- claude/ndi-* → SESSION 1 (NDI) - See below
- claude/webrtc-* → SESSION 2 (WebRTC) - See below
- claude/h323-* → SESSION 3 (H.323) - See below
- claude/sip-* → SESSION 4 (SIP) - See below
- claude/cli-* → SESSION 5 (CLI) - See below
- claude/if-talent-* → SESSION 6 (Talent) - See below
- claude/if-bus-* → SESSION 7 (IF.bus) - See below

---

## Session 1 (NDI): vMix NDI Integration

**Your Expertise:** NDI streaming, video metadata, IF.witness

**Your Task:** Integrate vMix NDI inputs/outputs with IF.witness provenance

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): vMix NDI Input Research**
- How vMix discovers NDI sources
- vMix API calls: `AddInput`, `SetInputName`, input type "NDI"
- NDI source selection via vMix
- Metadata passthrough

**Agent 2 (Haiku): vMix NDI Output Research**
- vMix NDI output configuration
- Output naming conventions
- Multiple NDI outputs from one vMix instance
- Quality/bandwidth settings

**Agent 3 (Haiku): vMix API Discovery**
- REST API endpoints for NDI control
- TCP API commands for NDI inputs
- Function API: `AddInput Value=NDI|...`
- Status queries for NDI sources

**Agent 4 (Sonnet): Integration Implementation**
Build: `src/integrations/vmix_ndi_bridge.py`
```python
class VMixNDIBridge:
    """Bridge vMix NDI inputs/outputs with IF.witness"""

    def add_ndi_input(self, vmix_host, ndi_source_name):
        """Add NDI source to vMix, track with IF.witness"""
        # Call vMix API
        # Log to IF.witness with hash chain

    def create_ndi_output(self, vmix_host, output_name):
        """Configure vMix NDI output with provenance"""

    def get_ndi_sources(self, vmix_host):
        """List all NDI inputs in vMix"""
```

**Deliverables:**
- `src/integrations/vmix_ndi_bridge.py`
- `docs/VMIX/ndi-integration.md`
- `tests/test_vmix_ndi.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 2 (WebRTC): vMix Streaming Output Integration

**Your Expertise:** WebRTC, browser streaming, real-time communication

**Your Task:** Integrate vMix streaming outputs (RTMP, SRT, WebRTC) with IF.swarm

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): vMix RTMP Streaming**
- vMix streaming destinations API
- `StartStreaming`, `StopStreaming` commands
- RTMP URL configuration
- Stream health monitoring

**Agent 2 (Haiku): vMix SRT Output**
- SRT (Secure Reliable Transport) support in vMix
- SRT caller/listener modes
- Low-latency configuration
- Error recovery

**Agent 3 (Haiku): vMix Recording Control**
- `StartRecording`, `StopRecording`
- Recording formats (MP4, AVI, MOV)
- Multi-track recording
- Status queries

**Agent 4 (Sonnet): Streaming Controller**
Build: `src/integrations/vmix_streaming.py`
```python
class VMixStreamingController:
    """Control vMix streaming outputs"""

    def start_rtmp_stream(self, vmix_host, rtmp_url, key):
        """Start RTMP stream to destination"""

    def start_srt_stream(self, vmix_host, srt_address):
        """Start SRT stream (low latency)"""

    def start_recording(self, vmix_host, filename, format="MP4"):
        """Start local recording"""

    def get_stream_status(self, vmix_host):
        """Get streaming/recording status"""
```

**Deliverables:**
- `src/integrations/vmix_streaming.py`
- `docs/VMIX/streaming-integration.md`
- `tests/test_vmix_streaming.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 3 (H.323): vMix SIP/PTZ Camera Integration

**Your Expertise:** Legacy protocols, H.323, video conferencing

**Your Task:** Integrate vMix PTZ camera control and SIP call capabilities

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): vMix PTZ Control**
- PTZ (Pan-Tilt-Zoom) commands via vMix API
- `SetPanX`, `SetPanY`, `SetZoom` functions
- PTZ preset recall
- PTZ camera types supported

**Agent 2 (Haiku): vMix SIP/Skype Integration**
- vMix "Call" input type
- SIP call management via API
- Skype TX/NDI integration
- Audio routing for calls

**Agent 3 (Haiku): vMix Input Control**
- Camera input switching
- Input effects (color correction, zoom)
- Input layers and mixing
- Virtual camera sets

**Agent 4 (Sonnet): PTZ & Call Controller**
Build: `src/integrations/vmix_ptz_call.py`
```python
class VMixPTZCallController:
    """Control PTZ cameras and calls via vMix"""

    def ptz_move(self, vmix_host, input_name, pan, tilt, zoom):
        """Move PTZ camera"""

    def ptz_preset(self, vmix_host, input_name, preset_number):
        """Recall PTZ preset"""

    def start_sip_call(self, vmix_host, sip_address):
        """Start SIP call input"""

    def end_call(self, vmix_host, input_name):
        """End call input"""
```

**Deliverables:**
- `src/integrations/vmix_ptz_call.py`
- `docs/VMIX/ptz-call-integration.md`
- `tests/test_vmix_ptz_call.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 4 (SIP): vMix Production Control & Switching

**Your Expertise:** SIP, call routing, integration coordination

**Your Task:** Core vMix production control (preview/program switching, transitions)

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): vMix Switching API**
- `PreviewInput`, `ActiveInput` functions
- Transition commands: `Cut`, `Fade`, `Merge`, `Wipe`, `Zoom`
- Transition duration control
- Overlay management (1-4)

**Agent 2 (Haiku): vMix Mix & Audio**
- Audio mixer control via API
- `SetVolume`, `AudioBus`, `AudioMute`
- Audio routing matrix
- Master audio levels

**Agent 3 (Haiku): vMix Status & State**
- XML status endpoint (port 8088)
- Real-time state queries
- Active input detection
- Preview/program state

**Agent 4 (Sonnet): Production Controller**
Build: `src/integrations/vmix_production.py`
```python
class VMixProductionController:
    """Core vMix production control"""

    def cut_to_input(self, vmix_host, input_number):
        """Cut to input (instant)"""

    def fade_to_input(self, vmix_host, input_number, duration_ms=1000):
        """Fade to input with duration"""

    def set_preview(self, vmix_host, input_number):
        """Set preview input"""

    def set_overlay(self, vmix_host, overlay_num, input_number):
        """Set overlay 1-4"""

    def get_state(self, vmix_host):
        """Get current production state (XML parse)"""
```

**Deliverables:**
- `src/integrations/vmix_production.py`
- `docs/VMIX/production-control-integration.md`
- `tests/test_vmix_production.py`

**Time:** 5-6 hours
**Cost:** $6-10

---

## Session 5 (CLI): vMix CLI Interface

**Your Expertise:** CLI design, IF.witness, user experience

**Your Task:** Design dead simple CLI for vMix control

### Workstreams (Spawn 1 Sonnet):

**Agent 1 (Sonnet): CLI Interface Design & Implementation**

Design & Build:
```bash
# vMix connection management
if vmix add myvmix --host 192.168.1.100 --port 8088
if vmix list
if vmix test myvmix

# Production control
if vmix cut myvmix --input 1
if vmix fade myvmix --input 2 --duration 2000
if vmix preview myvmix --input 3

# NDI control
if vmix ndi add myvmix --source "NDI Source Name"
if vmix ndi list myvmix

# Streaming
if vmix stream start myvmix --rtmp rtmp://server/live --key abc123
if vmix stream stop myvmix
if vmix record start myvmix --file output.mp4

# Status
if vmix status myvmix
if vmix inputs myvmix

# PTZ control
if vmix ptz myvmix --input 1 --pan 50 --tilt 30 --zoom 80
if vmix ptz preset myvmix --input 1 --preset 3
```

**Features:**
- Auto-discovery (mDNS for local vMix instances)
- IF.witness integration (log all vMix operations)
- IF.optimise integration (track usage)
- Config: `~/.if/vmix/instances.yaml`
- Tab completion for inputs/overlays

**Deliverables:**
- `src/cli/vmix_commands.py`
- `docs/VMIX/cli-interface.md`
- Shell completion scripts

**Time:** 5-6 hours
**Cost:** $8-12

---

## Session 6 (Talent): vMix Adapter Pattern & Bloom Classification

**Your Expertise:** Architecture patterns, IF.talent, capability modeling

**Your Task:** Design unified vMix adapter pattern with bloom classification

### Workstreams (Spawn 1 Sonnet):

**Agent 1 (Sonnet): Unified vMix Adapter Architecture**

Design base class:
```python
class VMixAdapter(ABC):
    """Unified interface to vMix instances"""

    # Connection
    @abstractmethod
    def connect(self, host, port=8088):
        """Connect to vMix instance"""

    # Production control
    @abstractmethod
    def switch_input(self, input_id, transition="Cut", duration_ms=0):
        """Switch to input with transition"""

    # Inputs
    @abstractmethod
    def add_input(self, input_type, **kwargs):
        """Add input (NDI, Video, Image, etc.)"""

    @abstractmethod
    def remove_input(self, input_id):
        """Remove input"""

    # Streaming
    @abstractmethod
    def start_stream(self, destination, **kwargs):
        """Start streaming"""

    # Status
    @abstractmethod
    def get_state(self):
        """Get current production state"""

    # IF.witness integration
    def log_operation(self, operation, params, result):
        """Log all operations with IF.witness"""
```

**Bloom Pattern Classification:**

**vMix as "Steady Performer":**
- Consistent API across all features
- Reliable state management
- Good error handling
- Production-proven stability

**Feature Maturity:**
- Early bloomer: Basic switching, NDI I/O (simple, works great)
- Steady performer: Streaming, recording, audio mixing (consistent)
- Late bloomer: Advanced scripting, automation (powerful at scale)

**Scout → Sandbox → Certify → Deploy:**
- Scout: Test vMix API endpoints, discover capabilities
- Sandbox: Test in non-production vMix instance
- Certify: Validate against vMix production patterns
- Deploy: Use in live production with confidence

**Deliverables:**
- `src/integrations/vmix_adapter_base.py`
- `docs/VMIX/adapter-architecture.md`
- `docs/VMIX/bloom-patterns.md` (vMix capability classification)

**Time:** 5-6 hours
**Cost:** $8-12

---

## Session 7 (IF.bus): vMix as Infrastructure Control Target

**Your Expertise:** Infrastructure control, multi-instance orchestration

**Your Task:** Add vMix to IF.bus as controllable infrastructure

### Workstreams (Spawn 2 Haiku + 1 Sonnet):

**Agent 1 (Haiku): vMix Instance Discovery**
- mDNS discovery of local vMix instances
- API probing for version detection
- Health check endpoints
- Multi-instance coordination

**Agent 2 (Haiku): vMix REST API Wrapper**
- Review: https://github.com/curtgrimes/vmix-rest-api
- Evaluate as IF.bus foundation
- REST vs TCP API tradeoffs
- Authentication (if any)

**Agent 3 (Sonnet): IF.bus vMix Adapter**
Build: `src/bus/vmix_bus_adapter.py`
```python
class VMixBusAdapter(InfrastructureAdapter):
    """IF.bus adapter for vMix production infrastructure"""

    def discover_instances(self):
        """Auto-discover vMix instances on network"""

    def add_instance(self, name, host, port=8088):
        """Add vMix instance to IF.bus"""

    def get_instance_status(self, name):
        """Get health/status of vMix instance"""

    def execute_command(self, name, command, **params):
        """Execute any vMix command on instance"""

    def load_balance_inputs(self, input_sources):
        """Distribute inputs across multiple vMix instances"""
```

**CLI Integration:**
```bash
# Add vMix to IF.bus
if bus add vmix myvmix --host 192.168.1.100 --port 8088 --auto-detect

# List vMix instances
if bus list vmix

# Execute command
if bus exec vmix myvmix --command "Cut" --input 1

# Multi-instance orchestration
if bus orchestrate vmix --profile "3-camera-production"
```

**Deliverables:**
- `src/bus/vmix_bus_adapter.py`
- `docs/VMIX/if-bus-integration.md`
- `docs/VMIX/multi-instance-orchestration.md`

**Time:** 5-6 hours
**Cost:** $8-12

---

## Cross-Session Coordination

### Integration Points:

**Session 1 (NDI) → Session 7 (IF.bus):**
- Session 1's NDI bridge used by Session 7 for discovery

**Session 2 (Streaming) → Session 4 (Production):**
- Production controller triggers streaming start/stop

**Session 3 (PTZ) → Session 4 (Production):**
- PTZ presets recalled during production switching

**Session 5 (CLI) → All Sessions:**
- CLI uses all integration modules

**Session 6 (Adapter) → All Sessions:**
- All sessions inherit from unified adapter pattern

### Coordination Protocol:

**Step 1:** Each session spawns agents, starts work

**Step 2:** Post to STATUS.md:
```yaml
status: vmix_sprint_in_progress
task: [your task from above]
deliverables: [file paths]
estimated_time: [hours]
dependencies: [other sessions you need]
```

**Step 3:** Commit work to your branch:
```bash
git add .
git commit -m "feat(vmix): [Session X] - [description]"
git push origin $(git branch --show-current)
```

**Step 4:** Signal completion:
```yaml
status: vmix_sprint_complete
deliverables_complete: [list files]
next_action: waiting_for_integration
```

---

## Timeline & Cost Estimates

| Session | Task | Time | Cost |
|---------|------|------|------|
| Session 1 | NDI Integration | 4-5h | $5-8 |
| Session 2 | Streaming | 4-5h | $5-8 |
| Session 3 | PTZ/Calls | 4-5h | $5-8 |
| Session 4 | Production Control | 5-6h | $6-10 |
| Session 5 | CLI Interface | 5-6h | $8-12 |
| Session 6 | Adapter Pattern | 5-6h | $8-12 |
| Session 7 | IF.bus Integration | 5-6h | $8-12 |
| **TOTAL** | **All Sessions** | **33-39h sequential** | **$45-70** |

**With parallel execution:** 5-6 hours wall-clock time (all sessions work simultaneously!)

**Velocity gain:** 6-7x faster than sequential

---

## Philosophy: vMix as "Friend" in Production

**Wu Lun (五倫) - 朋友 (Friends):**
vMix joins InfraFabric as a "friend" - reliable production infrastructure we orchestrate alongside SIP servers, NDI sources, and streaming destinations.

**IF.ground Principle 2: Validate with toolchain**
Every vMix integration tested against real vMix instance before deployment.

**IF.TTT:**
- **Traceable:** All vMix commands logged via IF.witness
- **Transparent:** Full state visibility via XML status API
- **Trustworthy:** Production-proven vMix stability + IF tests

---

## Success Metrics

**Sprint complete when:**
- ✅ All 7 sessions deliver their modules
- ✅ CLI can control vMix (Session 5 complete)
- ✅ IF.bus can orchestrate vMix (Session 7 complete)
- ✅ Integration tests pass
- ✅ Documentation complete

**Result:**
InfraFabric gains full vMix production control:
- NDI input/output management
- RTMP/SRT streaming control
- PTZ camera control
- Production switching automation
- Multi-instance orchestration via IF.bus

---

## START NOW!

1. **Identify:** Run `git branch --show-current`
2. **Find:** Your session section above
3. **Execute:** Spawn agents, start work
4. **Coordinate:** Post STATUS.md updates
5. **Deliver:** Commit modules, tests, docs

**Timeline:** 5-6 hours wall-clock (all sessions parallel)

🎬 **vMix Sprint: Professional production control for InfraFabric!**
