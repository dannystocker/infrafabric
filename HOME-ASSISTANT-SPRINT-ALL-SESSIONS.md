# HOME ASSISTANT INTEGRATION SPRINT - ALL SESSIONS (1-7)

**Mission:** Integrate Home Assistant (home automation platform) with InfraFabric for physical infrastructure control

**Context:** Home Assistant is open-source home automation that controls IoT devices, cameras, lighting, sensors, and more via REST API

**Resources:**
- https://developers.home-assistant.io/docs/api/rest/
- https://www.home-assistant.io/integrations/
- WebSocket API: https://developers.home-assistant.io/docs/api/websocket
- Python Client: https://github.com/home-assistant/home-assistant

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

## Session 1 (NDI): Home Assistant Camera Integration

**Your Expertise:** NDI streaming, video metadata, IF.witness

**Your Task:** Integrate Home Assistant cameras (ONVIF, RTSP, USB) with NDI and IF.witness

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): Home Assistant Camera Entities**
- REST API: `GET /api/states/camera.*`
- Camera attributes (stream URL, RTSP, MJPEG)
- Camera services: `turn_on`, `turn_off`, `snapshot`
- Camera stream proxy endpoint

**Agent 2 (Haiku): RTSP → NDI Transcoding**
- Extract RTSP URLs from Home Assistant cameras
- RTSP to NDI conversion (ffmpeg or similar)
- NDI output naming (HA camera entity_id → NDI source name)
- Latency optimization

**Agent 3 (Haiku): Home Assistant Camera Events**
- WebSocket API: Subscribe to camera state changes
- Motion detection events
- Camera availability monitoring
- Snapshot capture triggers

**Agent 4 (Sonnet): HA Camera NDI Bridge**
Build: `src/integrations/ha_camera_ndi_bridge.py`
```python
class HACameraNDIBridge:
    """Bridge Home Assistant cameras to NDI with IF.witness"""

    def __init__(self, ha_url, ha_token):
        """Connect to Home Assistant API"""
        self.ha_url = ha_url
        self.ha_token = ha_token

    def discover_cameras(self):
        """List all camera entities in Home Assistant"""
        # GET /api/states/camera.*
        # Return list of camera entity_ids

    def stream_camera_to_ndi(self, camera_entity_id, ndi_name=None):
        """Stream HA camera to NDI output"""
        # Get RTSP/MJPEG URL from HA
        # Transcode to NDI
        # Track with IF.witness

    def capture_snapshot(self, camera_entity_id, filename):
        """Capture camera snapshot"""
        # POST /api/services/camera/snapshot

    def monitor_motion(self, camera_entity_id, callback):
        """Monitor motion detection events"""
        # WebSocket: Subscribe to state changes
        # Trigger callback on motion
```

**Deliverables:**
- `src/integrations/ha_camera_ndi_bridge.py`
- `docs/HOME-ASSISTANT/camera-ndi-integration.md`
- `tests/test_ha_camera_ndi.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 2 (WebRTC): Home Assistant Notifications & Webhooks

**Your Expertise:** WebRTC, real-time communication, browser integration

**Your Task:** Integrate Home Assistant notifications and webhooks with IF.swarm

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): Home Assistant Notifications**
- REST API: `POST /api/services/notify/notify`
- Notification services (mobile_app, email, telegram, etc.)
- Rich notifications (actions, images, URLs)
- Priority levels

**Agent 2 (Haiku): Home Assistant Webhooks**
- Webhook trigger integration
- POST to Home Assistant webhook
- Webhook automation triggers
- Webhook → automation → action flow

**Agent 3 (Haiku): Home Assistant Events**
- REST API: `POST /api/events/[event_type]`
- Custom event firing
- Event listeners
- State change events

**Agent 4 (Sonnet): HA Notification Controller**
Build: `src/integrations/ha_notifications.py`
```python
class HANotificationController:
    """Control Home Assistant notifications and webhooks"""

    def __init__(self, ha_url, ha_token):
        self.ha_url = ha_url
        self.ha_token = ha_token

    def send_notification(self, message, title=None, target=None, data=None):
        """Send notification via Home Assistant"""
        # POST /api/services/notify/notify
        # Support mobile_app, persistent_notification, etc.

    def trigger_webhook(self, webhook_id, payload):
        """Trigger Home Assistant webhook"""
        # POST /api/webhook/[webhook_id]
        # Return automation response

    def fire_event(self, event_type, event_data):
        """Fire custom event in Home Assistant"""
        # POST /api/events/[event_type]

    def subscribe_to_events(self, event_type, callback):
        """Subscribe to Home Assistant events (WebSocket)"""
        # WebSocket: subscribe to events
        # Trigger callback on event
```

**Deliverables:**
- `src/integrations/ha_notifications.py`
- `docs/HOME-ASSISTANT/notifications-webhooks-integration.md`
- `tests/test_ha_notifications.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 3 (H.323): Home Assistant Media Players & TTS

**Your Expertise:** Legacy protocols, media, audio/video

**Your Task:** Integrate Home Assistant media players and text-to-speech

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): Home Assistant Media Players**
- REST API: `GET /api/states/media_player.*`
- Media player services: `play_media`, `pause`, `stop`, `volume_set`
- Media player attributes (state, volume, source, media info)
- Supported media types (music, video, podcast, URL)

**Agent 2 (Haiku): Home Assistant Text-to-Speech**
- TTS services: `google_translate_say`, `tts.speak`, etc.
- TTS to media players
- Multi-language support
- TTS caching

**Agent 3 (Haiku): Home Assistant Audio/Video Sources**
- Media source browser
- Local media files
- URL streaming
- Radio/podcast integration

**Agent 4 (Sonnet): HA Media Controller**
Build: `src/integrations/ha_media.py`
```python
class HAMediaController:
    """Control Home Assistant media players and TTS"""

    def __init__(self, ha_url, ha_token):
        self.ha_url = ha_url
        self.ha_token = ha_token

    def discover_media_players(self):
        """List all media player entities"""
        # GET /api/states/media_player.*

    def play_media(self, media_player_entity, media_url, media_type="music"):
        """Play media on media player"""
        # POST /api/services/media_player/play_media

    def text_to_speech(self, media_player_entity, message, language="en"):
        """Speak text on media player"""
        # POST /api/services/tts/google_translate_say

    def control_playback(self, media_player_entity, action="play"):
        """Control playback (play/pause/stop/next/previous)"""

    def set_volume(self, media_player_entity, volume_level):
        """Set media player volume (0.0-1.0)"""

    def announce(self, message, targets=None):
        """Announce message to all/selected media players"""
        # Broadcast TTS to multiple media players
```

**Deliverables:**
- `src/integrations/ha_media.py`
- `docs/HOME-ASSISTANT/media-tts-integration.md`
- `tests/test_ha_media.py`

**Time:** 4-5 hours
**Cost:** $5-8

---

## Session 4 (SIP): Home Assistant Automation & Scripts

**Your Expertise:** SIP, call routing, integration coordination

**Your Task:** Core Home Assistant automation and script execution

### Workstreams (Spawn 3 Haiku + 1 Sonnet):

**Agent 1 (Haiku): Home Assistant Automations**
- REST API: `GET /api/config/automation/config/[automation_id]`
- Trigger automations: `POST /api/services/automation/trigger`
- Enable/disable automations
- Automation traces and debugging

**Agent 2 (Haiku): Home Assistant Scripts**
- REST API: `POST /api/services/script/[script_name]`
- Script execution with parameters
- Script sequences
- Script results

**Agent 3 (Haiku): Home Assistant Scenes**
- REST API: `GET /api/states/scene.*`
- Activate scenes: `POST /api/services/scene/turn_on`
- Scene creation
- Scene restore

**Agent 4 (Sonnet): HA Automation Controller**
Build: `src/integrations/ha_automation.py`
```python
class HAAutomationController:
    """Control Home Assistant automations and scripts"""

    def __init__(self, ha_url, ha_token):
        self.ha_url = ha_url
        self.ha_token = ha_token

    def trigger_automation(self, automation_id, skip_condition=False):
        """Trigger automation manually"""
        # POST /api/services/automation/trigger

    def enable_automation(self, automation_id):
        """Enable automation"""

    def disable_automation(self, automation_id):
        """Disable automation"""

    def run_script(self, script_name, **params):
        """Execute script with parameters"""
        # POST /api/services/script/[script_name]

    def activate_scene(self, scene_entity_id):
        """Activate scene"""
        # POST /api/services/scene/turn_on

    def get_automation_traces(self, automation_id):
        """Get automation execution traces"""
        # Debug automation runs
```

**Deliverables:**
- `src/integrations/ha_automation.py`
- `docs/HOME-ASSISTANT/automation-integration.md`
- `tests/test_ha_automation.py`

**Time:** 5-6 hours
**Cost:** $6-10

---

## Session 5 (CLI): Home Assistant CLI Interface

**Your Expertise:** CLI design, IF.witness, user experience

**Your Task:** Design dead simple CLI for Home Assistant control

### Workstreams (Spawn 1 Sonnet):

**Agent 1 (Sonnet): CLI Interface Design & Implementation**

Design & Build:
```bash
# Home Assistant connection management
if ha add myhome --url http://homeassistant.local:8123 --token eyJ0...
if ha list
if ha test myhome

# Entity control
if ha entities myhome --domain light
if ha entities myhome --domain switch
if ha state myhome light.living_room
if ha set myhome light.living_room --state on --brightness 80

# Services
if ha service myhome light.turn_on --entity light.living_room --brightness 80
if ha service myhome switch.toggle --entity switch.coffee_maker

# Cameras
if ha camera list myhome
if ha camera stream myhome camera.front_door --ndi "Front Door NDI"
if ha camera snapshot myhome camera.front_door --file snapshot.jpg

# Automations
if ha automation list myhome
if ha automation trigger myhome automation.motion_detected
if ha automation enable myhome automation.night_mode
if ha automation disable myhome automation.vacation_mode

# Scripts
if ha script list myhome
if ha script run myhome script.movie_mode

# Scenes
if ha scene list myhome
if ha scene activate myhome scene.evening

# Notifications
if ha notify myhome --message "Doorbell pressed" --title "Alert"

# Media players
if ha media list myhome
if ha media play myhome media_player.living_room --url http://stream.com/radio.mp3
if ha tts myhome media_player.kitchen --message "Dinner is ready"

# Events
if ha event fire myhome custom_event --data '{"key": "value"}'

# Status
if ha status myhome
if ha info myhome  # HA version, uptime, etc.
```

**Features:**
- Auto-discovery (mDNS for local Home Assistant)
- IF.witness integration (log all HA operations)
- IF.optimise integration (track IoT device control)
- Config: `~/.if/home-assistant/instances.yaml`
- Tab completion for entities, domains, services
- JSON output mode for scripting
- Entity filtering (by domain, area, device_class)

**Deliverables:**
- `src/cli/ha_commands.py`
- `docs/HOME-ASSISTANT/cli-interface.md`
- Shell completion scripts

**Time:** 5-6 hours
**Cost:** $8-12

---

## Session 6 (Talent): Home Assistant Adapter Pattern & Bloom Classification

**Your Expertise:** Architecture patterns, IF.talent, capability modeling

**Your Task:** Design unified Home Assistant adapter pattern with bloom classification

### Workstreams (Spawn 1 Sonnet):

**Agent 1 (Sonnet): Unified Home Assistant Adapter Architecture**

Design base class:
```python
from abc import ABC, abstractmethod
import aiohttp
import asyncio

class HomeAssistantAdapter(ABC):
    """Unified interface to Home Assistant instances"""

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.session = None

    # Connection
    @abstractmethod
    async def connect(self):
        """Connect to Home Assistant API"""

    @abstractmethod
    async def disconnect(self):
        """Disconnect"""

    # Entity management
    @abstractmethod
    async def get_states(self, entity_id=None):
        """Get entity states"""

    @abstractmethod
    async def set_state(self, entity_id, state, attributes=None):
        """Set entity state"""

    # Service calls
    @abstractmethod
    async def call_service(self, domain, service, **service_data):
        """Call Home Assistant service"""

    # Events
    @abstractmethod
    async def fire_event(self, event_type, event_data):
        """Fire event"""

    @abstractmethod
    async def subscribe_events(self, event_type, callback):
        """Subscribe to events (WebSocket)"""

    # Config
    @abstractmethod
    async def get_config(self):
        """Get Home Assistant configuration"""

    # Status
    @abstractmethod
    async def check_health(self):
        """Check Home Assistant health"""

    # IF.witness integration
    def log_operation(self, operation, params, result):
        """Log all operations with IF.witness"""
        pass

    # IF.optimise integration
    def track_device_control(self, device_id, action, energy_impact=0):
        """Track IoT device control costs"""
        pass
```

**Bloom Pattern Classification:**

**Home Assistant as "Steady Performer + Integration Champion":**
- Early bloomer: Basic light/switch control (simple, works immediately)
- Steady performer: Automations, scripts, scenes (consistent, reliable)
- Late bloomer: Complex integrations, custom components (powerful ecosystem)

**Feature Maturity:**
- **Early bloomer:** Basic entity control (lights, switches) - works out of box
- **Steady performer:** Automations, notifications, media - reliable core
- **Late bloomer:** 2000+ integrations, custom components, advanced automations

**Home Assistant Philosophy:**
- **Local control:** No cloud required (aligns with IF.ground)
- **Open source:** Community-driven (aligns with IF principles)
- **Privacy-first:** Data stays local
- **Integration hub:** Connects 2000+ devices/services

**Scout → Sandbox → Certify → Deploy:**
- **Scout:** Discover HA integrations, test API endpoints
- **Sandbox:** Test automations in non-production HA instance
- **Certify:** Validate against real IoT devices
- **Deploy:** Control production home automation

**Deliverables:**
- `src/integrations/ha_adapter_base.py`
- `docs/HOME-ASSISTANT/adapter-architecture.md`
- `docs/HOME-ASSISTANT/bloom-patterns.md`
- `docs/HOME-ASSISTANT/ha-philosophy-alignment.md` (HA ↔ IF.ground)

**Time:** 5-6 hours
**Cost:** $8-12

---

## Session 7 (IF.bus): Home Assistant as Infrastructure Control Target

**Your Expertise:** Infrastructure control, multi-instance orchestration

**Your Task:** Add Home Assistant to IF.bus as controllable physical infrastructure

### Workstreams (Spawn 2 Haiku + 1 Sonnet):

**Agent 1 (Haiku): Home Assistant Instance Discovery**
- mDNS discovery (homeassistant.local)
- API health check: `GET /api/`
- Version detection: `GET /api/config`
- Multi-instance coordination (multiple HA instances)
- Integration detection (which integrations enabled)

**Agent 2 (Haiku): Home Assistant WebSocket API**
- WebSocket connection setup
- Authentication via token
- Event subscriptions (state_changed, call_service, etc.)
- Real-time state monitoring
- Command execution via WebSocket

**Agent 3 (Sonnet): IF.bus Home Assistant Adapter**
Build: `src/bus/ha_bus_adapter.py`
```python
class HABusAdapter(InfrastructureAdapter):
    """IF.bus adapter for Home Assistant physical infrastructure"""

    def discover_instances(self, network_range="192.168.1.0/24"):
        """Auto-discover Home Assistant instances on network"""
        # mDNS discovery
        # Port 8123 scanning
        # Return list of (host, version)

    def add_instance(self, name, url, token):
        """Add Home Assistant instance to IF.bus"""
        # Store in IF.bus registry
        # Test connection
        # Discover entities
        # Log with IF.witness

    def get_instance_status(self, name):
        """Get health/status of HA instance"""
        # Connection status
        # Entity count
        # Automation count
        # System health

    def execute_command(self, name, domain, service, **params):
        """Execute any Home Assistant service"""
        # Generic service call
        # Log with IF.witness
        # Track device control costs

    def orchestrate_devices(self, profile):
        """Orchestrate devices across HA instances"""
        # Multi-home coordination
        # Device failover
        # Load balancing

    def sync_automations(self, source_instance, target_instances):
        """Sync automations across HA instances"""
        # Copy automation configs
        # Redundancy setup
        # Backup/restore

    def control_physical_infrastructure(self, action):
        """Control physical infrastructure via HA"""
        # Lights, switches, locks, cameras
        # HVAC, sensors, alarms
        # Production studio control (lights, audio, cameras via HA)
```

**CLI Integration:**
```bash
# Add Home Assistant to IF.bus
if bus add ha myhome --url http://homeassistant.local:8123 --token eyJ0... --auto-detect

# List HA instances
if bus list ha

# Execute service
if bus exec ha myhome --domain light --service turn_on --entity light.studio_key

# Multi-instance orchestration
if bus orchestrate ha --profile "production-studio"
# Profile: Control all studio lights, cameras, audio via HA
#          - Key light, fill light, back light
#          - Camera pan/tilt
#          - Audio monitoring
#          - Emergency shutdown

# Discover HA on network
if bus discover ha --network 192.168.1.0/24
```

**Production Studio Control via Home Assistant:**
```yaml
# Example: Studio lighting via Home Assistant + IF.bus
studio_lighting_automation:
  - id: studio_recording_mode
    trigger:
      - platform: event
        event_type: if_swarm_recording_started
    action:
      - service: light.turn_on
        target:
          entity_id:
            - light.studio_key_light
            - light.studio_fill_light
            - light.studio_back_light
        data:
          brightness: 255
          color_temp: 5600  # Daylight
```

**Deliverables:**
- `src/bus/ha_bus_adapter.py`
- `docs/HOME-ASSISTANT/if-bus-integration.md`
- `docs/HOME-ASSISTANT/production-studio-control.md`
- `docs/HOME-ASSISTANT/multi-instance-orchestration.md`

**Time:** 5-6 hours
**Cost:** $8-12

---

## Cross-Session Coordination

### Integration Points:

**Session 1 (Cameras) ↔ vMix/OBS:**
- HA cameras → RTSP → NDI → vMix/OBS input
- Motion detection triggers scene switch

**Session 2 (Notifications) ↔ IF.swarm:**
- IF.swarm events → HA notifications
- Recording started → notify mobile app
- Stream dropped → alert via HA

**Session 3 (Media) ↔ Session 4 (Automation):**
- Automations trigger TTS announcements
- Production start → announce via speakers

**Session 5 (CLI) → All Sessions:**
- Unified CLI for all HA features
- Studio control from command line

**Session 7 (IF.bus) → Production Infrastructure:**
- Control studio lights via HA
- Control studio cameras (pan/tilt) via HA
- Emergency shutdown via HA
- HVAC control for equipment cooling

### Home Assistant as Production Infrastructure Layer:

```
┌─────────────────────────────────────────┐
│         InfraFabric (IF.bus)            │
│  ┌─────────────────────────────────┐   │
│  │  Production Software Layer      │   │
│  │  - vMix (video mixing)          │   │
│  │  - OBS (streaming)              │   │
│  │  - SIP (communications)         │   │
│  │  - NDI (video transport)        │   │
│  └──────────────┬──────────────────┘   │
│                 │                        │
│  ┌──────────────▼──────────────────┐   │
│  │  Home Assistant (Physical)      │   │
│  │  - Studio lights (key/fill/back)│   │
│  │  - PTZ cameras                  │   │
│  │  - Audio monitoring             │   │
│  │  - HVAC (equipment cooling)     │   │
│  │  - Security (door locks)        │   │
│  │  - Sensors (temp, humidity)     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Coordination Protocol:

**Step 1:** Each session spawns agents, starts work

**Step 2:** Post to STATUS.md:
```yaml
status: ha_sprint_in_progress
task: [your task from above]
deliverables: [file paths]
estimated_time: [hours]
dependencies: [other sessions you need]
vmix_obs_integration: [how this relates to vMix/OBS]
```

**Step 3:** Commit work to your branch:
```bash
git add .
git commit -m "feat(ha): [Session X] - [description]"
git push origin $(git branch --show-current)
```

**Step 4:** Signal completion:
```yaml
status: ha_sprint_complete
deliverables_complete: [list files]
next_action: waiting_for_integration
```

---

## Timeline & Cost Estimates

| Session | Task | Time | Cost |
|---------|------|------|------|
| Session 1 | Camera → NDI | 4-5h | $5-8 |
| Session 2 | Notifications & Webhooks | 4-5h | $5-8 |
| Session 3 | Media Players & TTS | 4-5h | $5-8 |
| Session 4 | Automations & Scripts | 5-6h | $6-10 |
| Session 5 | CLI Interface | 5-6h | $8-12 |
| Session 6 | Adapter Pattern | 5-6h | $8-12 |
| Session 7 | IF.bus Integration | 5-6h | $8-12 |
| **TOTAL** | **All Sessions** | **33-39h sequential** | **$45-70** |

**With parallel execution:** 5-6 hours wall-clock time (all sessions work simultaneously!)

**Velocity gain:** 6-7x faster than sequential

---

## Philosophy: Home Assistant as "Physical Friend"

**Wu Lun (五倫) - 朋友 (Friends):**
Home Assistant joins InfraFabric as a "physical friend" - controlling real-world infrastructure (lights, cameras, sensors) that supports production.

**IF.ground Principle 1: Open Source First**
Home Assistant is open-source, local-first, privacy-focused - perfect alignment.

**IF.ground Principle 8: Observability Without Fragility**
HA provides full observability of physical infrastructure without fragility.

**IF.TTT:**
- **Traceable:** All HA commands logged via IF.witness
- **Transparent:** Full state visibility via REST/WebSocket API
- **Trustworthy:** Local control, no cloud dependency

---

## Success Metrics

**Sprint complete when:**
- ✅ All 7 sessions deliver their modules
- ✅ CLI can control Home Assistant (Session 5 complete)
- ✅ IF.bus can orchestrate HA (Session 7 complete)
- ✅ HA cameras → NDI → vMix/OBS working
- ✅ Production automations working (lights, cameras)
- ✅ Integration tests pass
- ✅ Documentation complete

**Result:**
InfraFabric gains physical infrastructure control:
- Camera control (pan/tilt, zoom)
- Lighting control (key/fill/back lights)
- Audio monitoring
- HVAC (equipment cooling)
- Security (door locks, sensors)
- Emergency shutdown
- Production automation triggers

---

## Combined Sprint Summary (vMix + OBS + Home Assistant)

**Total Deliverables:**
- 21 integration modules (7×3 platforms)
- Unified CLI for all platforms
- IF.bus orchestration for all
- Full production stack control (software + physical)
- Comprehensive documentation

**Integration Flow:**
```
Home Assistant (Physical)
  └─> Cameras (RTSP) ──┐
  └─> Lights (Z-Wave)  │
  └─> Sensors (Zigbee) │
                        │
                        ├─> NDI ─┐
                        │        │
                        │        ├─> vMix (Production)
                        │        │
                        │        └─> OBS (Streaming)
                        │
                        └─> IF.bus (Orchestration)
                             └─> IF.witness (Provenance)
                             └─> IF.optimise (Cost tracking)
```

**Total Timeline:** 15-18 hours wall-clock (all 3 sprints parallel!)
**Total Cost:** $135-210 (all 3 sprints)
**Velocity:** 18-21x faster than sequential

🚀 **Complete production infrastructure: Software (vMix/OBS) + Physical (Home Assistant) under unified InfraFabric orchestration!**

---

## START NOW!

1. **Identify:** Run `git branch --show-current`
2. **Find:** Your session section above
3. **Execute:** Spawn agents, start work
4. **Coordinate:** Post STATUS.md updates
5. **Deliver:** Commit modules, tests, docs

**Timeline:** 5-6 hours wall-clock (all sessions parallel)

🏠 **Home Assistant Sprint: Physical infrastructure control for InfraFabric!**
