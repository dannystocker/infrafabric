# OBS INTEGRATION SPRINT - ALL SESSIONS (1-7)

**Mission:** Integrate OBS Studio (Open Broadcaster Software) with InfraFabric

**Context:** OBS is open-source live streaming and recording software with WebSocket API (obs-websocket protocol)

**Resources:**
- https://docs.obsproject.com/
- https://github.com/obsproject/obs-websocket
- WebSocket Protocol: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
- Python Client: https://github.com/obsproject/obs-websocket-py

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

## Session 1 (NDI): OBS NDI Plugin Integration

**Your Expertise:** NDI streaming, video metadata, IF.witness

**Your Task:** Integrate OBS NDI plugin (obs-ndi) with IF.witness provenance

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): OBS NDI Plugin Research**
- obs-ndi plugin capabilities
- NDI source input in OBS
- NDI output from OBS
- Plugin installation/detection
- NDI discovery via OBS

**Agent 2 (Haiku): OBS Sources API**
- WebSocket: `GetInputList`, `CreateInput`
- Creating NDI source: `obs_ndi_source`
- NDI source settings (ndi_name, bandwidth, etc.)
- Source properties and filters

**Agent 3 (Haiku): OBS NDI Output**
- NDI output configuration
- WebSocket: `GetOutputList`, `StartOutput`
- NDI output settings
- Multiple NDI outputs

**Agent 4 (Sonnet): OBS NDI Bridge Implementation**
Build: `src/integrations/obs_ndi_bridge.py`
```python
class OBSNDIBridge:
    """Bridge OBS NDI plugin with IF.witness"""

    def __init__(self, obs_host="localhost", obs_port=4455, obs_password=None):
        """Connect to OBS WebSocket"""
        self.ws = obsws(obs_host, obs_port, obs_password)

    def add_ndi_source(self, scene_name, source_name, ndi_source):
        """Add NDI source to OBS scene, track with IF.witness"""
        # WebSocket: CreateInput
        # Log to IF.witness with hash chain

    def create_ndi_output(self, output_name, ndi_name):
        """Configure OBS NDI output with provenance"""

    def list_ndi_sources(self):
        """List available NDI sources visible to OBS"""

    def get_ndi_source_stats(self, source_name):
        """Get NDI source statistics (bandwidth, frames, etc.)"""
```

**Deliverables:**
- `src/integrations/obs_ndi_bridge.py`
- `docs/OBS/ndi-integration.md`
- `tests/test_obs_ndi.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 2 (WebRTC): OBS Streaming & Virtual Camera

**Your Expertise:** WebRTC, browser streaming, real-time communication

**Your Task:** Integrate OBS streaming outputs and Virtual Camera with IF.swarm

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): OBS Streaming API**
- WebSocket: `StartStream`, `StopStream`, `GetStreamStatus`
- Streaming service configuration (Twitch, YouTube, custom RTMP)
- Stream settings (bitrate, encoder, resolution)
- Stream health monitoring

**Agent 2 (Haiku): OBS Virtual Camera**
- Virtual Camera API (Start/Stop)
- Virtual Camera as WebRTC source
- Virtual Camera settings
- Cross-platform compatibility (Windows, macOS, Linux)

**Agent 3 (Haiku): OBS Recording API**
- WebSocket: `StartRecord`, `StopRecord`, `GetRecordStatus`
- Recording settings (format, quality, path)
- Multi-track recording
- Pause/Resume recording

**Agent 4 (Sonnet): OBS Streaming Controller**
Build: `src/integrations/obs_streaming.py`
```python
class OBSStreamingController:
    """Control OBS streaming and recording"""

    def __init__(self, obs_host="localhost", obs_port=4455, obs_password=None):
        self.ws = obsws(obs_host, obs_port, obs_password)

    def start_stream(self, service=None, server=None, key=None):
        """Start streaming to destination"""
        # Configure stream settings
        # WebSocket: StartStream
        # Monitor with IF.witness

    def start_virtual_camera(self):
        """Start OBS Virtual Camera"""

    def start_recording(self, filename=None, format="mp4"):
        """Start local recording"""

    def get_stream_status(self):
        """Get streaming statistics (bitrate, frames, duration)"""

    def stop_all(self):
        """Stop streaming, virtual camera, and recording"""
```

**Deliverables:**
- `src/integrations/obs_streaming.py`
- `docs/OBS/streaming-integration.md`
- `tests/test_obs_streaming.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 3 (H.323): OBS Media Sources & Browser Sources

**Your Expertise:** Legacy protocols, video conferencing, media integration

**Your Task:** Integrate OBS media sources (video files, images, browser sources)

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): OBS Media Source**
- Media source types (video file, image, slideshow)
- WebSocket: CreateInput with `ffmpeg_source`, `image_source`
- Media playback control (play, pause, restart)
- Looping and playlist support

**Agent 2 (Haiku): OBS Browser Source**
- Browser source capabilities (HTML, CSS, JS)
- WebSocket: CreateInput with `browser_source`
- URL-based content
- Custom HTML/CSS overlays
- JavaScript interaction

**Agent 3 (Haiku): OBS Capture Sources**
- Window capture, display capture, game capture
- Audio input/output capture
- Source properties and settings
- Cross-platform capture differences

**Agent 4 (Sonnet): OBS Media Controller**
Build: `src/integrations/obs_media.py`
```python
class OBSMediaController:
    """Control OBS media and browser sources"""

    def add_media_source(self, scene_name, source_name, file_path, loop=False):
        """Add video/image media source"""

    def add_browser_source(self, scene_name, source_name, url, width=1920, height=1080):
        """Add browser source with URL"""

    def add_html_overlay(self, scene_name, source_name, html_content):
        """Add custom HTML overlay"""

    def control_media_playback(self, source_name, action="play"):
        """Control media playback (play/pause/restart)"""

    def refresh_browser_source(self, source_name):
        """Refresh browser source content"""

    def add_window_capture(self, scene_name, source_name, window_title):
        """Add window capture source"""
```

**Deliverables:**
- `src/integrations/obs_media.py`
- `docs/OBS/media-sources-integration.md`
- `tests/test_obs_media.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 4 (SIP): OBS Scene & Source Management

**Your Expertise:** SIP, call routing, integration coordination

**Your Task:** Core OBS scene management, source switching, and transitions

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): OBS Scene Management**
- WebSocket: `GetSceneList`, `CreateScene`, `SetCurrentProgramScene`
- Scene switching and transitions
- Scene collections
- Scene item management (sources within scenes)

**Agent 2 (Haiku): OBS Transitions**
- Transition types (Cut, Fade, Swipe, Slide, Stinger)
- WebSocket: `GetTransitionKindList`, `SetCurrentSceneTransition`
- Transition duration and settings
- Custom transitions

**Agent 3 (Haiku): OBS Source Management**
- WebSocket: `GetInputList`, `SetInputSettings`
- Source visibility and transform
- Source filters (color correction, chroma key, etc.)
- Source audio mixing

**Agent 4 (Sonnet): OBS Scene Controller**
Build: `src/integrations/obs_scenes.py`
```python
class OBSSceneController:
    """Core OBS scene and source management"""

    def create_scene(self, scene_name):
        """Create new scene"""

    def switch_scene(self, scene_name, transition="Fade", duration_ms=300):
        """Switch to scene with transition"""

    def get_current_scene(self):
        """Get current program scene"""

    def add_source_to_scene(self, scene_name, source_name, source_type, settings):
        """Add source to scene"""

    def set_source_visibility(self, scene_name, source_name, visible=True):
        """Show/hide source in scene"""

    def set_source_transform(self, scene_name, source_name, x=0, y=0, scale_x=1.0, scale_y=1.0):
        """Transform source position and scale"""

    def apply_filter(self, source_name, filter_name, filter_type, settings):
        """Apply filter to source (chroma key, color correction, etc.)"""

    def get_scene_items(self, scene_name):
        """List all sources in scene"""
```

**Deliverables:**
- `src/integrations/obs_scenes.py`
- `docs/OBS/scene-management-integration.md`
- `tests/test_obs_scenes.py`

**Time:** 5-6 hours
**Cost:** $6-10

---

## Session 5 (CLI): OBS CLI Interface

**Your Expertise:** CLI design, IF.witness, user experience

**Your Task:** Design dead simple CLI for OBS control

### Workstreams (Spawn 1 Sonnet):

**Agent 1 (Sonnet): CLI Interface Design & Implementation**

Design & Build:
```bash
# OBS connection management
if obs add myobs --host localhost --port 4455 --password secret123
if obs list
if obs test myobs

# Scene management
if obs scene list myobs
if obs scene switch myobs --scene "Gaming Scene"
if obs scene create myobs --scene "New Scene"

# Source management
if obs source add myobs --scene "Gaming Scene" --source "Webcam" --type camera
if obs source add myobs --scene "Gaming Scene" --source "NDI Input" --type ndi --ndi-name "Source1"
if obs source show myobs --scene "Gaming Scene" --source "Webcam"
if obs source hide myobs --scene "Gaming Scene" --source "Webcam"

# Streaming & Recording
if obs stream start myobs --service twitch --key abc123
if obs stream stop myobs
if obs stream status myobs
if obs record start myobs --file output.mp4
if obs record stop myobs
if obs virtualcam start myobs

# Filters
if obs filter add myobs --source "Webcam" --filter "Chroma Key" --type chroma_key --color green

# Media control
if obs media add myobs --scene "Gaming Scene" --source "Video" --file video.mp4 --loop
if obs media play myobs --source "Video"
if obs media pause myobs --source "Video"

# Browser sources
if obs browser add myobs --scene "Gaming Scene" --source "Overlay" --url "https://example.com/overlay.html"

# Status
if obs status myobs
if obs stats myobs  # Streaming stats, CPU usage, FPS
```

**Features:**
- Auto-discovery (local OBS instances on port 4455)
- IF.witness integration (log all OBS operations)
- IF.optimise integration (track streaming bandwidth/costs)
- Config: `~/.if/obs/instances.yaml`
- Tab completion for scenes/sources
- JSON output mode for scripting

**Deliverables:**
- `src/cli/obs_commands.py`
- `docs/OBS/cli-interface.md`
- Shell completion scripts

**Time:** 5-6 hours
**Cost:** $8-12

---

## Session 6 (Talent): OBS Adapter Pattern & Bloom Classification

**Your Expertise:** Architecture patterns, IF.talent, capability modeling

**Your Task:** Design unified OBS adapter pattern with bloom classification

### Workstreams (Spawn 1 Sonnet):

**Agent 1 (Sonnet): Unified OBS Adapter Architecture**

Design base class:
```python
from abc import ABC, abstractmethod
import asyncio
from obswebsocket import obsws, requests

class OBSAdapter(ABC):
    """Unified interface to OBS instances"""

    def __init__(self, host="localhost", port=4455, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.ws = None

    # Connection
    @abstractmethod
    async def connect(self):
        """Connect to OBS WebSocket"""

    @abstractmethod
    async def disconnect(self):
        """Disconnect from OBS"""

    # Scene management
    @abstractmethod
    async def switch_scene(self, scene_name, transition=None, duration_ms=None):
        """Switch to scene"""

    @abstractmethod
    async def get_scene_list(self):
        """Get all scenes"""

    # Source management
    @abstractmethod
    async def create_source(self, scene_name, source_name, source_type, settings):
        """Create source in scene"""

    @abstractmethod
    async def set_source_settings(self, source_name, settings):
        """Update source settings"""

    # Streaming
    @abstractmethod
    async def start_stream(self):
        """Start streaming"""

    @abstractmethod
    async def stop_stream(self):
        """Stop streaming"""

    @abstractmethod
    async def get_stream_status(self):
        """Get streaming status"""

    # Recording
    @abstractmethod
    async def start_record(self):
        """Start recording"""

    @abstractmethod
    async def stop_record(self):
        """Stop recording"""

    # Status
    @abstractmethod
    async def get_stats(self):
        """Get OBS stats (CPU, FPS, etc.)"""

    @abstractmethod
    async def get_version(self):
        """Get OBS version info"""

    # IF.witness integration
    def log_operation(self, operation, params, result):
        """Log all operations with IF.witness"""
        # IF.witness hash chain
        pass

    # IF.optimise integration
    def track_cost(self, operation, bandwidth_mb=0, duration_sec=0):
        """Track streaming costs with IF.optimise"""
        pass
```

**Bloom Pattern Classification:**

**OBS as "Early Bloomer + Open Source Champion":**
- Early bloomer: Basic streaming/recording (simple, free, works great)
- Steady performer: Scene management, sources (consistent API)
- Late bloomer: Advanced plugins, scripting (powerful ecosystem)

**Feature Maturity:**
- **Early bloomer:** Basic streaming to Twitch/YouTube (works immediately)
- **Steady performer:** Scene switching, sources, filters (reliable)
- **Late bloomer:** Custom plugins, Lua/Python scripting, complex automations

**OBS vs vMix Comparison:**
- OBS: Free, open-source, extensible, large community
- vMix: Commercial, integrated, professional, unified API
- Both: Production-quality, reliable, industry-standard

**Scout → Sandbox → Certify → Deploy:**
- **Scout:** Test OBS WebSocket API, discover plugins (NDI, etc.)
- **Sandbox:** Test in non-production OBS instance, experiment with scenes
- **Certify:** Validate against streaming platforms (Twitch, YouTube)
- **Deploy:** Use in live production with confidence

**Deliverables:**
- `src/integrations/obs_adapter_base.py`
- `docs/OBS/adapter-architecture.md`
- `docs/OBS/bloom-patterns.md` (OBS capability classification)
- `docs/OBS/obs-vs-vmix-comparison.md`

**Time:** 5-6 hours
**Cost:** $8-12

---

## Session 7 (IF.bus): OBS as Infrastructure Control Target

**Your Expertise:** Infrastructure control, multi-instance orchestration

**Your Task:** Add OBS to IF.bus as controllable infrastructure

### Workstreams (Spawn 2 Haiku + 1 Sonnet):

**Agent 1 (Haiku): OBS Instance Discovery**
- WebSocket discovery (scan port 4455)
- OBS version detection via `GetVersion`
- Health check endpoints
- Multi-instance coordination (multiple OBS on same network)
- OBS plugin detection (NDI, Browser, etc.)

**Agent 2 (Haiku): OBS WebSocket Protocol**
- obs-websocket protocol v5.x
- Authentication mechanism
- Event subscriptions (scene changes, stream start/stop)
- Batch requests for performance
- Error handling patterns

**Agent 3 (Sonnet): IF.bus OBS Adapter**
Build: `src/bus/obs_bus_adapter.py`
```python
class OBSBusAdapter(InfrastructureAdapter):
    """IF.bus adapter for OBS infrastructure"""

    def discover_instances(self, network_range="192.168.1.0/24"):
        """Auto-discover OBS instances on network"""
        # Scan port 4455
        # Return list of (host, port, version)

    def add_instance(self, name, host, port=4455, password=None):
        """Add OBS instance to IF.bus"""
        # Store in IF.bus registry
        # Test connection
        # Log with IF.witness

    def get_instance_status(self, name):
        """Get health/status of OBS instance"""
        # Connection status
        # Stream/record status
        # CPU usage, FPS

    def execute_command(self, name, command, **params):
        """Execute any OBS WebSocket command"""
        # Generic command execution
        # Log with IF.witness
        # Track cost with IF.optimise

    def load_balance_sources(self, sources, instances):
        """Distribute sources across multiple OBS instances"""
        # Scene distribution
        # Load balancing algorithm
        # Health-based routing

    def sync_scenes(self, source_instance, target_instances):
        """Sync scene configuration across OBS instances"""
        # Copy scenes/sources
        # Redundancy setup
```

**CLI Integration:**
```bash
# Add OBS to IF.bus
if bus add obs myobs --host 192.168.1.100 --port 4455 --password secret --auto-detect

# List OBS instances
if bus list obs

# Execute command
if bus exec obs myobs --command "SetCurrentProgramScene" --scene "Gaming Scene"

# Multi-instance orchestration
if bus orchestrate obs --profile "redundant-streaming"
# Profile: 2 OBS instances, same scenes, failover on stream drop

# Discover OBS on network
if bus discover obs --network 192.168.1.0/24
```

**Deliverables:**
- `src/bus/obs_bus_adapter.py`
- `docs/OBS/if-bus-integration.md`
- `docs/OBS/multi-instance-orchestration.md`
- `docs/OBS/obs-redundancy-patterns.md`

**Time:** 5-6 hours
**Cost:** $8-12

---

## Cross-Session Coordination

### Integration Points:

**Session 1 (NDI) ↔ Session 7 (IF.bus):**
- Session 1's NDI bridge discovers NDI sources for OBS
- Session 7 orchestrates NDI distribution across OBS instances

**Session 2 (Streaming) ↔ Session 4 (Scenes):**
- Scene controller triggers stream start/stop
- Streaming stats used for scene automation

**Session 3 (Media) ↔ Session 4 (Scenes):**
- Media sources added to scenes
- Scene switching controls media playback

**Session 5 (CLI) → All Sessions:**
- CLI uses all integration modules
- Unified interface to all OBS features

**Session 6 (Adapter) → All Sessions:**
- All sessions inherit from unified adapter pattern
- Consistent error handling and logging

**OBS ↔ vMix Integration:**
- NDI bridge connects OBS output to vMix input
- Unified IF.bus control of both platforms
- Failover: OBS → vMix or vMix → OBS

### Coordination Protocol:

**Step 1:** Each session spawns agents, starts work

**Step 2:** Post to STATUS.md:
```yaml
status: obs_sprint_in_progress
task: [your task from above]
deliverables: [file paths]
estimated_time: [hours]
dependencies: [other sessions you need]
vmix_integration: [how this relates to vMix sprint]
```

**Step 3:** Commit work to your branch:
```bash
git add .
git commit -m "feat(obs): [Session X] - [description]"
git push origin $(git branch --show-current)
```

**Step 4:** Signal completion:
```yaml
status: obs_sprint_complete
deliverables_complete: [list files]
next_action: waiting_for_integration
```

---

## Timeline & Cost Estimates

| Session | Task | Time | Cost |
|---------|------|------|------|
| Session 1 | NDI Integration | 4-5h | $5-8 |
| Session 2 | Streaming & Virtual Camera | 4-5h | $5-8 |
| Session 3 | Media & Browser Sources | 4-5h | $5-8 |
| Session 4 | Scene Management | 5-6h | $6-10 |
| Session 5 | CLI Interface | 5-6h | $8-12 |
| Session 6 | Adapter Pattern | 5-6h | $8-12 |
| Session 7 | IF.bus Integration | 5-6h | $8-12 |
| **TOTAL** | **All Sessions** | **33-39h sequential** | **$45-70** |

**With parallel execution:** 5-6 hours wall-clock time (all sessions work simultaneously!)

**Velocity gain:** 6-7x faster than sequential

---

## Philosophy: OBS as "Open Friend" in Production

**Wu Lun (五倫) - 朋友 (Friends):**
OBS joins InfraFabric as an "open friend" - free, extensible production infrastructure we orchestrate alongside vMix, SIP servers, and NDI sources.

**IF.ground Principle 1: Open Source First**
OBS embodies open-source excellence - free, community-driven, extensible.

**IF.ground Principle 2: Validate with toolchain**
Every OBS integration tested against real OBS instance before deployment.

**IF.TTT:**
- **Traceable:** All OBS commands logged via IF.witness
- **Transparent:** Full state visibility via WebSocket API
- **Trustworthy:** Production-proven OBS stability + IF tests

---

## Success Metrics

**Sprint complete when:**
- ✅ All 7 sessions deliver their modules
- ✅ CLI can control OBS (Session 5 complete)
- ✅ IF.bus can orchestrate OBS (Session 7 complete)
- ✅ OBS ↔ vMix integration working (NDI bridge)
- ✅ Integration tests pass
- ✅ Documentation complete

**Result:**
InfraFabric gains full OBS production control:
- NDI input/output management
- RTMP/SRT streaming control
- Virtual Camera for WebRTC
- Scene/source automation
- Multi-instance orchestration via IF.bus
- OBS ↔ vMix interoperability

---

## OBS + vMix = Complete Production Stack

**Unified Control:**
```bash
# Stream to both OBS and vMix simultaneously
if bus orchestrate --profile "dual-production"
# - OBS: Free, main stream to Twitch
# - vMix: Professional backup, NDI outputs
# - Failover: If OBS crashes, vMix takes over

# NDI bridge
if obs ndi output myobs --name "OBS Output 1"
if vmix ndi add myvmix --source "OBS Output 1"
# Result: vMix gets OBS output via NDI
```

**Best of Both Worlds:**
- OBS: Free, open-source, large plugin ecosystem
- vMix: Professional, integrated, powerful features
- InfraFabric: Orchestrates both, provides IF.TTT guarantees

---

## START NOW!

1. **Identify:** Run `git branch --show-current`
2. **Find:** Your session section above
3. **Execute:** Spawn agents, start work
4. **Coordinate:** Post STATUS.md updates
5. **Deliver:** Commit modules, tests, docs

**Timeline:** 5-6 hours wall-clock (all sessions parallel)

🎬 **OBS Sprint: Open-source production control for InfraFabric!**

---

## Combined Sprint Summary (OBS + vMix)

**Total Deliverables:**
- 14 integration modules (7 for vMix, 7 for OBS)
- Unified CLI for both platforms
- IF.bus orchestration for both
- NDI bridge between OBS ↔ vMix
- Comprehensive documentation

**Total Timeline:** 10-12 hours wall-clock (both sprints parallel!)
**Total Cost:** $90-140 (both sprints)
**Velocity:** 12-14x faster than sequential

🚀 **Professional production control: OBS + vMix under unified InfraFabric orchestration!**
