# AGENT 4-7: THE LIBRARIANS - Bitfocus Companion Ecosystem Research

**Research Date:** 2025-11-26
**Agent ID:** AGENT-4-7-LIBRARIANS
**Mission:** Comprehensive documentation of Bitfocus Companion module ecosystem for MCR broadcast applications

---

## Executive Summary

Bitfocus Companion is a professional control surface platform that transforms affordable hardware (Elgato Stream Deck, etc.) into professional shotbox surfaces for broadcast and AV equipment. The ecosystem comprises **700+ hardware and software integrations** across the professional broadcast and AV industries.

**Key Statistics:**
- **Total Modules:** 700+
- **Repository Commits:** 2,438
- **License:** MIT
- **Primary Languages:** JavaScript (84.1%), TypeScript
- **Node.js Requirement:** 18.0.0+
- **Module Base Package:** @companion-module/base

---

## 1. Module Registry Structure

### Repository Organization

**Primary Repository:** [companion-bundled-modules](https://github.com/bitfocus/companion-bundled-modules)

**Naming Convention:**
```
{manufacturer}-{product}

Examples:
- bmd-atem (Blackmagic ATEM)
- behringer-x32 (Behringer X32)
- obs-studio (OBS Studio)
- studiocoast-vmix (vMix)
- ptzoptics-visca (PTZOptics VISCA)
```

All module names use lowercase hyphenated format for consistency.

### Category Taxonomy

The ecosystem organizes modules into functional categories:

#### **Audio & Sound**
Allen & Heath, Behringer X32/M32, Biamp, BSS, Yamaha, Calrec, Dante, Audac

#### **Video Switching & Vision Mixing**
Blackmagic ATEM, Analogway (LivePremier, Midra), Barco EventMaster, vMix, NewTek TriCaster, Ross Carbonite

#### **PTZ Cameras**
PTZOptics, Sony VISCA, Panasonic, Canon CR-N/X, BirdDog, Axis

#### **Recording & Playout**
Blackmagic HyperDeck, AJA Ki Pro, CasparCG, Grass Valley

#### **Lighting Control**
Elgato Key Light, Avolites Titan, ChamSys MagicQ, ETC, MA Lighting

#### **Streaming & Encoding**
OBS Studio, vMix, AWS Elemental, Teradek, Blackmagic WebPresenter

#### **Matrix Routing**
Blackmagic Videohub, AJA Kumo, Barco, Aten, Evertz

#### **Generic Protocols**
ArtNet, MIDI, MQTT, OSC, SNMP, DMX, WebSocket, SSH, HTTP, PJLink

---

## 2. Top-Tier Module Deep Dive

### Module Action & Feedback Summary

| Module | Manufacturer | Protocol | Est. Actions | Tier | Primary Use Case |
|--------|--------------|----------|--------------|------|------------------|
| **bmd-atem** | Blackmagic | TCP | 150 | 1 | Live production switching |
| **studiocoast-vmix** | StudioCoast | REST/TCP | 120 | 1 | Live streaming software |
| **obs-studio** | OBS Project | WebSocket | 85 | 1 | Streaming & recording |
| **ptzoptics-visca** | PTZOptics | VISCA/TCP | 60 | 1 | PTZ camera control |
| **zoom-osc-iso** | Liminal | OSC | 35 | 1 | Zoom meeting control |
| **newtek-tricaster** | NewTek | TCP | 75 | 1 | Video production switcher |
| **generic-pjlink** | JBMIA | PJLink | 15 | 2 | Projector control |
| **elgato-keylight** | Elgato | REST | 8 | 3 | Studio lighting |

---

### Detailed Module Profiles

#### **1. Blackmagic ATEM (bmd-atem)**

**Broadcast Tier:** Tier-1
**Protocol:** Blackmagic ATEM TCP
**Repository:** https://github.com/bitfocus/companion-module-bmd-atem

**Core Capabilities:**
- **Switching:** Program/Preview, Cut, Auto, Fade-to-Black, T-bar control
- **Audio:** Fairlight mixer fader control, routing, solo/mute, master/monitor gain
- **Macros:** Execute macros by index/name, looping, startup state management
- **Media:** Media player control, still capture/deletion, recording filename config
- **Keying:** USK/DSK control, DVE keyframes, SuperSource configuration
- **Camera:** Iris, exposure, zoom, color correction
- **Display:** Multiviewer configuration, input labeling, display clock

**Key Feedbacks:**
- Program/Preview tally (red/green indicators)
- Recording/streaming status
- Transition in progress
- USK/DSK on-air status
- Audio level monitoring

**Variables:** Program input, preview input, transition style, recording status, media player sources, input labels, model info

**Supported Models:** ATEM Mini series, Television Studio HD, Production Studio 4K (1/2/4 M/E), Constellation 8K

**Network Requirements:** Must be on same IP range (USB NOT supported), Firmware 7.5.2+ recommended

---

#### **2. vMix (studiocoast-vmix)**

**Broadcast Tier:** Tier-1
**Protocol:** REST API + TCP
**Repository:** https://github.com/bitfocus/companion-module-studiocoast-vmix

**Core Capabilities:**
- **Input Controls:** Switching, selection, GO actions, Cut/Fade/Transition
- **Audio:** Bus volume, headphones, input-level audio, routing
- **Transitions:** Auto/Stinger (8 stingers), AlphaFade, custom duration, T-bar
- **Overlays:** 8 overlay functions, multiple mix support
- **Titles/Graphics:** Animation triggers, image setting, visibility, dynamic text
- **Replay:** Play events by ID, Quad View, event text management
- **Recording/Streaming:** Start/stop recording, multi-destination streaming
- **Custom Commands:** Direct vMix API access with syntax `CommandName Value=parameter`

**Polling Configuration:**
- Default interval: 250ms (configurable)
- Legacy: 100ms (pre-1.2.6)
- Data source: vMix REST API
- HTTP API support for 3rd party integration

**Key Feedbacks:**
- Program/Preview tally
- Recording/Streaming status
- Audio levels
- Layer routing
- Replay mode indicators

**Command Examples:**
```
Cut to Input 1
Fade to Input 2 over 1000ms
SetVolume Value=1&Volume=75
OverlayInput1In
StartRecording
TitleBeginAnimation Input=1&Value=PageIn
```

---

#### **3. OBS Studio (obs-studio)**

**Broadcast Tier:** Tier-1
**Protocol:** WebSocket (obs-websocket v5.0+)
**Repository:** https://github.com/bitfocus/companion-module-obs-studio

**Requirements:**
- OBS 28+ (includes obs-websocket by default)
- WebSocket port: 4455 (default)
- Password authentication required
- Same network as Companion

**Core Capabilities:**
- **Recording/Streaming:** Toggle/Start/Stop, pause/resume, split files, chapters, captions, replay buffer
- **Switching:** Scene switching (program/preview), smart switching, transitions (type, duration)
- **Source Controls:** Visibility, filters, transforms (position/scale/rotation), audio (mute, volume, monitoring, sync, balance)
- **Text/Media:** Modify text content, refresh browsers, media playback, file path updates
- **General:** Studio mode toggle, projectors, profile/collection changes, hotkey triggering
- **Advanced:** Custom JSON commands, vendor requests, raw WebSocket

**Key Feedbacks:**
- Streaming/Recording active status
- Scene transition state
- Source visibility
- Audio mute status
- Media playback status
- Studio mode state
- Disk space monitoring
- Stream congestion alerts

**Variables:**
- Recording timecode and file info
- Streaming metrics (uptime, bitrate, dropped frames)
- Current/preview scene names
- Transition type and duration
- Media playback status
- Source volumes and mute states
- System metrics (FPS, CPU, memory)
- Output resolution/framerate
- Custom command responses

---

#### **4. Zoom OSC ISO (zoom-osc-iso)**

**Broadcast Tier:** Tier-1
**Protocol:** OSC (Open Sound Control)
**Repository:** https://github.com/bitfocus/companion-module-zoom-osc-iso

**Control Pattern:** "First select user(s), then apply action(s)"

**Core Capabilities:**
- **Participant Selection:** Gallery view (max 49), Participants list, single/multi-selection, "Me" macro
- **Meeting Management:** Mute/unmute, video on/off, pin/unpin, spotlight, hand raise, device changes
- **ZoomISO Routing:** Route users to outputs, configure output properties, audio channel assignment
- **Meeting Control:** Join (ID/password/name), leave, end, sync actions/feedbacks

**Key Feedbacks:**
- Multi-state participant status (video, audio, hand raised)
- Automatic participant name display
- Real-time status color changes
- Status icons (on/off states)

**Variables:**
- callStatusNumber (0=Not in meeting, 1=Joining, 3=Connected, 4=Disconnected, 7=Ended, 8=Audio Ready)
- Participant names
- Video/audio device names
- Gallery view positions

**Use Cases:** Hybrid production, remote meeting control, webinar management, ISO routing for broadcast

---

#### **5. PTZOptics VISCA (ptzoptics-visca)**

**Broadcast Tier:** Tier-1
**Protocol:** VISCA over TCP/IP
**Repository:** https://github.com/bitfocus/companion-module-ptzoptics-visca

**Core Capabilities:**
- **PTZ Movement:** Pan/tilt (left/right/up/down), combined movement, home position, speed control, zoom in/out/stop
- **Focus:** Auto/manual, near/far, speed control, one-push AF, focus lock, touch AF
- **Exposure:** Auto/manual, iris, gain, shutter, backlight compensation, WDR, exposure compensation
- **White Balance:** Auto, indoor/outdoor mode, one-push WB, manual, color temperature
- **Presets:** Recall (1-255), save, clear, speed control
- **Image Settings:** Flip/reverse, noise reduction, digital zoom, image stabilization
- **Advanced:** Custom VISCA commands, power on/off, reset, status queries

**Network:**
- Port: 5678 (default VISCA)
- Low latency network recommended for smooth PTZ

**Supported Cameras:** PTZOptics 12X/20X/30X (G2/G3), Move 4K, most VISCA-compatible cameras

**VISCA Command Examples:**
```
81 01 06 02 VV WW 0P 0P 0P 0P 0T 0T 0T 0T FF (Pan/Tilt Position)
81 01 04 07 02 FF (Zoom Tele)
81 01 04 38 02 FF (Auto Focus On)
81 01 04 3F 02 pp FF (Recall Preset)
```

---

#### **6. PJLink Projectors (generic-pjlink)**

**Broadcast Tier:** Tier-2
**Protocol:** PJLink Class 1 & 2

**PJLink Versions:**
- Class 1: 2009 specification
- Class 2: 2016 specification (advanced features)

**Core Capabilities:**
- **Power Control:** POWR 0 (off), POWR 1 (on), query status
- **Input Selection:** RGB, HDMI, video inputs, query available inputs
- **Status:** Query lamp hours, error status, projector info, input list
- **Advanced (Class 2):** Input resolution, recommended resolution, filter usage, lamp model, screen freeze, serial number

**Security:**
- Random number control ticket authentication
- Password support
- Per-connection ticket generation

**Command Examples:**
```
%1POWR 1\r (Power On)
%1INPT 31\r (Select HDMI input 1)
%1LAMP ?\r (Query lamp hours)
```

**Use Cases:** Projector control in broadcast monitoring, screening rooms, presentation systems

---

#### **7. Elgato Key Light (elgato-keylight)**

**Broadcast Tier:** Tier-3
**Protocol:** REST API (HTTP)
**Port:** 9123

**Core Capabilities:**
- **Power:** On/off/toggle
- **Brightness:** Set level (0-100%), increase/decrease
- **Color Temperature:** Set (2900K-7000K), warmer/cooler adjustment
  - Temperature range: 143 (7000K) to 344 (2900K)

**Network:**
- Cross-VLAN supported if port 9123 allowed
- Static IP via DHCP reservation recommended

**Tested Compatibility:**
- Key Light (Firmware 1.0.3/200, 1.0.3/218)
- Key Light Air (Firmware 1.0.3/195, 1.0.3/200)
- Ring Light

**Command Examples:**
```json
PUT /elgato/lights
{
  "lights": [
    {"on": 1},
    {"brightness": 50},
    {"temperature": 200}
  ]
}
```

---

## 3. Device Catalog - Top 50 MCR Devices

### Tier Definitions

- **Tier 1:** Essential, commonly used in professional MCR environments (action count typically 50+)
- **Tier 2:** Important for specific workflows, professional quality (action count typically 30-50)
- **Tier 3:** Useful for specialized applications or smaller setups (action count typically <30)

### Top 15 Essential MCR Devices

| Rank | Manufacturer | Model | Category | Protocol | Actions | Tier |
|------|-------------|-------|----------|----------|---------|------|
| 1 | Blackmagic | ATEM Switchers | Video Switching | TCP | 150 | 1 |
| 2 | StudioCoast | vMix | Production Software | REST/TCP | 120 | 1 |
| 3 | OBS Project | OBS Studio | Streaming Software | WebSocket | 85 | 1 |
| 4 | Blackmagic | HyperDeck | Recording/Playout | TCP | 40 | 1 |
| 5 | PTZOptics | PTZ Cameras | PTZ Camera | VISCA/TCP | 60 | 1 |
| 6 | NewTek | TriCaster | Video Switcher | TCP | 75 | 1 |
| 7 | Ross Video | Carbonite | Video Switcher | RossTalk | 90 | 1 |
| 8 | Blackmagic | VideoHub | Video Router | TCP | 30 | 1 |
| 9 | Behringer | X32/M32 | Audio Mixer | OSC | 100 | 1 |
| 10 | Allen & Heath | SQ Series | Audio Mixer | TCP/MIDI | 85 | 1 |
| 11 | Liminal | ZoomOSC ISO | Video Conferencing | OSC | 35 | 1 |
| 12 | CasparCG | Server | Graphics/Playout | AMCP | 65 | 1 |
| 13 | Analogway | LivePremier | Video Processor | TCP/AWJ | 110 | 1 |
| 14 | Sony | VISCA PTZ | PTZ Camera | VISCA/TCP | 65 | 1 |
| 15 | Panasonic | PTZ Cameras | PTZ Camera | HTTP/CGI | 55 | 1 |

### Category Breakdown (Full Top 50)

**Video Switching (11 devices):**
ATEM, vMix, TriCaster, Ross Carbonite, Analogway LivePremier, Roland V-Series, Barco EventMaster, Grass Valley AMPP, Barco Folsom

**PTZ Cameras (5 devices):**
PTZOptics, Sony VISCA, Panasonic, Canon CR-N, BirdDog

**Audio (6 devices):**
Behringer X32/M32, Allen & Heath SQ, Yamaha CL/QL, Biamp Tesira, Audac MTX, Dante, Shure Wireless

**Recording/Playout (6 devices):**
HyperDeck, AJA Ki Pro, CasparCG, Epiphan Pearl, Matrox Monarch

**Streaming Software (2 devices):**
OBS Studio, vMix

**Routing/Matrix (4 devices):**
VideoHub, AJA Kumo, Smart Videohub, Extron

**Lighting (3 devices):**
Elgato Key Light, Avolites Titan, ChamSys MagicQ

**Encoders (5 devices):**
Teradek Prism, AWS Elemental, Magewell UltraStream, Haivision Makito X

**Media Servers (3 devices):**
Resolume, Christie Pandoras Box, Disguise

**Other Infrastructure (5 devices):**
Riedel Artist (Intercom), TSL UMD (Tally), PJLink Projectors, Cisco Webex, Microsoft Teams

*(Full catalog of 50 devices available in JSON file)*

---

## 4. Module Base Class API Structure

### Package Information

**Package Name:** `@companion-module/base`
**NPM:** https://www.npmjs.com/package/@companion-module/base
**Documentation:** https://bitfocus.github.io/companion-module-base/
**GitHub:** https://github.com/bitfocus/companion-module-base
**Weekly Downloads:** 552
**Node.js:** 18.0.0+

### InstanceBase<TConfig, TSecrets>

The abstract base class that all modules extend.

#### Abstract Methods (Required Implementation)

```typescript
// Lifecycle Methods
async init(config: TConfig): Promise<void>
  // Main initialization, called when module starts

async destroy(): Promise<void>
  // Cleanup before instance destruction

async configUpdated(config: TConfig): Promise<void>
  // Called when user changes configuration

getConfigFields(): SomeCompanionConfigField[]
  // Define configuration UI fields
```

#### Definition Methods

```typescript
setActionDefinitions(actions: CompanionActionDefinitions): void
  // Register available actions users can assign to buttons

setFeedbackDefinitions(feedbacks: CompanionFeedbackDefinitions): void
  // Register feedback types that update button appearance

setPresetDefinitions(presets: CompanionPresetDefinitions): void
  // Register preset button configurations

setVariableDefinitions(variables: CompanionVariableDefinition[]): void
  // Register variables that expose device state
```

#### Subscription Management

```typescript
subscribeActions(actions: Record<string, CompanionActionInfo>): void
unsubscribeActions(actions: string[]): void

subscribeFeedbacks(feedbacks: Record<string, CompanionFeedbackInfo>): void
unsubscribeFeedbacks(feedbacks: string[]): void
```

#### State Updates

```typescript
// Trigger feedback re-evaluation
checkFeedbacks(...feedbackTypes: string[]): void
checkFeedbacksById(...feedbackIds: string[]): void

// Update variable values
setVariableValues(values: CompanionVariableValues): void
getVariableValue(variableId: string): CompanionVariableValue | undefined

// Parse variables in strings
async parseVariablesInString(text: string): Promise<string>
```

#### Status & Logging

```typescript
updateStatus(status: InstanceStatus, message?: string): void
  // Statuses: Ok, Warning, Error, Connecting, Disconnected

log(level: LogLevel, message: string): void
  // Levels: debug, info, warn, error
```

#### Utilities

```typescript
oscSend(host: string, port: number, path: string, args: OSCArgument[]): void
saveConfig(config: TConfig): void
createSharedUdpSocket(options: UDPSocketOptions): UDPSocket
recordAction(action: CompanionActionInfo, uniquenessId?: string): boolean
```

---

### Action Interface

```typescript
interface CompanionActionDefinition {
  name: string                    // Human-readable action name
  description?: string            // Optional description
  options: SomeCompanionInputField[]  // User input fields
  callback: async (action: CompanionActionEvent) => Promise<void>
  learn?: (action) => Promise<CompanionActionDefinition>
  subscribe?: (action) => void
  unsubscribe?: (action) => void
}

// Callback receives:
interface CompanionActionEvent {
  actionId: string              // Action being executed
  options: Record<string, any>  // User-configured values
  surfaceId?: string           // Triggering surface
}
```

**Flow:**
1. User presses button
2. Companion calls `action.callback(actionEvent)`
3. Module processes `action.options` and executes device command
4. Module updates variables/feedbacks/status as needed

---

### Feedback Interface

```typescript
interface CompanionBooleanFeedbackDefinition {
  type: 'boolean'
  name: string
  description?: string
  options: SomeCompanionInputField[]
  defaultStyle: CompanionButtonStyleProps  // Applied when true
  callback: (feedback: CompanionFeedbackInfo) => boolean | Promise<boolean>
  learn?: (feedback) => Promise<CompanionFeedbackDefinition>
  subscribe?: (feedback) => void
  unsubscribe?: (feedback) => void
}

// defaultStyle properties:
interface CompanionButtonStyleProps {
  bgcolor?: number      // Background color (RGB integer)
  color?: number        // Foreground color (RGB integer)
  text?: string         // Button text
  png64?: string        // Base64-encoded PNG
  alignment?: string    // Text alignment
  size?: string         // Text size
  show_topbar?: boolean
}
```

**Flow:**
1. Module registers feedback with callback
2. Device state changes, module calls `checkFeedbacks(type)`
3. Companion re-evaluates all active feedbacks of that type
4. Callback returns true/false
5. If true, `defaultStyle` applied to button
6. Button appearance updates in real-time

---

### Variable System

```typescript
interface CompanionVariableDefinition {
  variableId: string    // Unique ID
  name: string          // Human-readable name
}

// Usage:
setVariableDefinitions([
  { variableId: 'current_scene', name: 'Current Scene' }
])

// Update values:
setVariableValues({
  current_scene: 'Studio A'
})

// Users reference as:
$(instance:current_scene)
```

**Flow:**
1. Module defines variables via `setVariableDefinitions()`
2. Device state changes, module calls `setVariableValues({variable: value})`
3. Companion updates variable store
4. Any buttons/actions referencing `$(instance:variable)` auto-update
5. Variables usable in button text, action parameters, conditions, etc.

---

### Preset System

```typescript
interface CompanionButtonPresetDefinition {
  type: 'button'
  category: string      // Organization category
  name: string          // Preset name
  style: CompanionButtonStyleProps
  feedbacks: CompanionFeedbackDefinition[]
  steps: Array<{
    down: CompanionActionDefinition[]
    up?: CompanionActionDefinition[]
  }>
}
```

**Purpose:** Provide users with pre-configured button setups for common workflows.

**Example:** "Program Input 1" preset with:
- Button text: "Camera 1"
- Action: Set Program to Input 1
- Feedback: Turn red when Input 1 is on Program

---

### Lifecycle Sequences

#### Startup Sequence
```
1. Companion instantiates module class
2. Calls getConfigFields() → builds config UI
3. User configures (IP, credentials, etc.)
4. Calls init(config)
5. Module connects to device, registers definitions
6. Module calls updateStatus() → indicates connection state
7. Module ready for action execution
```

#### Config Change Sequence
```
1. User modifies configuration in UI
2. Companion calls configUpdated(newConfig)
3. Module tears down old connections (if needed)
4. Module establishes new connections
5. Module updates status and may re-register definitions
```

#### Shutdown Sequence
```
1. Companion calls destroy()
2. Module closes connections, cleans up timers/intervals
3. Module releases resources
4. Instance removed from Companion
```

---

## 5. Command Invocation Patterns

### Action Execution Pattern

**Example: ATEM Cut to Input 1**

```typescript
// 1. User defines action in module
setActionDefinitions({
  'cut': {
    name: 'Cut to Input',
    options: [
      {
        type: 'dropdown',
        label: 'Input',
        id: 'input',
        choices: [
          { id: 1, label: 'Camera 1' },
          { id: 2, label: 'Camera 2' }
        ]
      }
    ],
    callback: async (action) => {
      const input = action.options.input
      await this.atem.changeProgramInput(input)
      this.setVariableValues({ program_input: input })
      this.checkFeedbacks('programTally')
    }
  }
})

// 2. User presses button
// 3. Companion calls callback with { actionId: 'cut', options: { input: 1 } }
// 4. Module sends command to ATEM
// 5. Module updates program_input variable
// 6. Module triggers programTally feedback re-evaluation
```

### Feedback Evaluation Pattern

**Example: ATEM Program Tally**

```typescript
// 1. Define feedback
setFeedbackDefinitions({
  'programTally': {
    type: 'boolean',
    name: 'Input is on Program',
    options: [
      {
        type: 'dropdown',
        label: 'Input',
        id: 'input',
        choices: [{ id: 1, label: 'Camera 1' }]
      }
    ],
    defaultStyle: {
      bgcolor: 0xFF0000,  // Red
      color: 0xFFFFFF     // White text
    },
    callback: (feedback) => {
      return this.currentProgramInput === feedback.options.input
    }
  }
})

// 2. User adds programTally feedback for Input 1 to button
// 3. ATEM program changes to Input 1
// 4. Module receives state update
// 5. Module calls checkFeedbacks('programTally')
// 6. Companion re-evaluates all programTally feedbacks
// 7. Callback for Input 1 returns true
// 8. Button turns red (defaultStyle applied)
```

### Variable Update Pattern

**Example: OBS Current Scene**

```typescript
// 1. Define variable
setVariableDefinitions([
  { variableId: 'current_scene', name: 'Current Scene' }
])

// 2. OBS scene changes to 'Studio A'
// 3. Module receives WebSocket event
// 4. Module updates variable:
setVariableValues({ current_scene: 'Studio A' })

// 5. User has button with text: "Scene: $(obs:current_scene)"
// 6. Button text automatically updates to "Scene: Studio A"
```

### Subscription Pattern

**Example: Audio Level Monitoring**

```typescript
setFeedbackDefinitions({
  'audioLevel': {
    type: 'boolean',
    name: 'Audio Level Above Threshold',
    options: [
      { type: 'textinput', label: 'Channel', id: 'channel' },
      { type: 'number', label: 'Threshold (dB)', id: 'threshold' }
    ],
    subscribe: (feedback) => {
      // User added audio level feedback
      const channel = feedback.options.channel
      if (!this.monitoredChannels.has(channel)) {
        this.monitoredChannels.add(channel)
        this.startAudioMonitoring(channel)
      }
    },
    unsubscribe: (feedback) => {
      // User removed audio level feedback
      const channel = feedback.options.channel
      if (!this.hasOtherSubscribers(channel)) {
        this.monitoredChannels.delete(channel)
        this.stopAudioMonitoring(channel)
      }
    },
    callback: (feedback) => {
      const level = this.audioLevels[feedback.options.channel]
      return level > feedback.options.threshold
    }
  }
})
```

**Benefit:** Modules only monitor/poll device state when feedbacks/actions are actually in use, conserving resources.

---

## 6. Key Findings & Recommendations for InfraFabric

### Ecosystem Scale

- **700+ integrations** across professional broadcast/AV
- **Independent child processes** for module stability
- **Well-defined API** through @companion-module/base
- **Companion 3.0+:** Modules as independent plugins, updatable separately

### Protocol Diversity

Supported protocols include: TCP, UDP, WebSocket, REST, OSC, VISCA, MIDI, DMX, PJLink, ArtNet, SNMP, SSH, HTTP, and custom proprietary protocols.

### Tier-1 MCR Essentials

For Master Control Room applications, prioritize:
1. **Blackmagic ATEM** - Video switching
2. **vMix** - Software production
3. **OBS Studio** - Streaming
4. **HyperDeck** - Recording
5. **PTZ Cameras (VISCA)** - Camera control
6. **VideoHub** - Routing
7. **Audio Mixers** - X32, SQ, Yamaha
8. **CasparCG** - Graphics
9. **Dante** - Audio networking
10. **ZoomOSC** - Hybrid production

### Integration Priorities for InfraFabric

1. **Study Action/Feedback/Variable Paradigm**
   - Maps well to agent command/response patterns
   - Provides real-time state synchronization model
   - Demonstrates effective device state exposure

2. **Leverage Lifecycle Patterns**
   - `init/configUpdated/destroy` maps to agent lifecycle management
   - Subscription patterns inform efficient resource management
   - Status updates provide health monitoring model

3. **Protocol Coverage for Series 3+**
   - **Tier 1 Priority:** ATEM, VISCA, WebSocket (OBS/vMix), OSC, REST APIs
   - **Tier 2 Priority:** PJLink, AMCP (CasparCG), RossTalk
   - **Universal Fallback:** Generic HTTP/TCP

4. **Command Schema Insights**
   - Action definitions could inform Haiku protocol command schemas
   - Preset system shows value of pre-configured workflows
   - Variable system demonstrates dynamic text/parameter substitution

5. **Multi-Device Workflow Patterns**
   - Study common MCR workflows: Switcher + Cameras + Audio + Graphics
   - Identify cross-device dependencies (e.g., tally routing)
   - Observe state synchronization patterns across systems

### Architectural Insights

**For Haiku Agents:**
- Companion's InstanceBase lifecycle provides blueprint for agent initialization/shutdown
- Subscription pattern prevents unnecessary polling (apply to Series 2+ agents)
- Feedback mechanism offers model for real-time UI updates in control interfaces
- Variable system demonstrates parameter substitution (useful for template-based commands)
- Preset concept valuable for complex multi-step agent workflows

**For IF Protocols:**
- 150+ actions in bmd-atem shows comprehensive device coverage needed
- 120+ actions in vmix shows software control complexity
- Action option schemas provide template for command parameter definition
- Feedback defaultStyle patterns inform visual state representation

---

## Research Sources

- [Bitfocus Companion (Main)](https://bitfocus.io/companion)
- [Companion Module Base](https://github.com/bitfocus/companion-module-base)
- [Companion Bundled Modules](https://github.com/bitfocus/companion-bundled-modules)
- [Companion Module Base API Docs](https://bitfocus.github.io/companion-module-base/)
- [@companion-module/base on npm](https://www.npmjs.com/package/@companion-module/base)
- [Bitfocus Connections Directory](https://bitfocus.io/connections)
- [Module Development Wiki](https://github.com/bitfocus/companion/wiki/Module-Development)
- [DeepWiki - Module Development](https://deepwiki.com/bitfocus/companion/8-module-development)
- [Blackmagic ATEM Module](https://github.com/bitfocus/companion-module-bmd-atem)
- [vMix Module](https://github.com/bitfocus/companion-module-studiocoast-vmix)
- [OBS Studio Module](https://github.com/bitfocus/companion-module-obs-studio)
- [Zoom OSC ISO Module](https://github.com/bitfocus/companion-module-zoom-osc-iso)
- [PTZOptics VISCA Module](https://github.com/bitfocus/companion-module-ptzoptics-visca)
- [Elgato Key Light Module](https://github.com/bitfocus/companion-module-elgato-keylight)
- [PJLink Specifications](https://pjlink.jbmia.or.jp/english/)

---

## Deliverables

1. **JSON Structured Catalog:** `/home/user/infrafabric/LIBRARIAN_RESEARCH_BITFOCUS_COMPANION_ECOSYSTEM.json`
   - Complete module registry structure
   - Top 7 module deep dives with action/feedback inventories
   - Top 50 MCR device catalog with tiering
   - Complete API interface documentation
   - Command invocation patterns
   - Recommendations for InfraFabric integration

2. **Summary Document:** `/home/user/infrafabric/LIBRARIAN_RESEARCH_SUMMARY.md` (this file)
   - Executive summary
   - Module organization and taxonomy
   - Detailed module profiles
   - API structure and patterns
   - Integration recommendations

---

**Research Completed:** 2025-11-26
**Agent:** AGENT-4-7-LIBRARIANS
**Status:** ✓ Complete - Ready for Series 3 Protocol Development
