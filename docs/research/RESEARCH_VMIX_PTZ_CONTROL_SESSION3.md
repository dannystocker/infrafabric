# vMix PTZ Camera Control - Research Report
## Session 3: Master Integration Sprint

**Date**: 2025-11-12
**Platform**: vMix (4K & PRO Editions)
**Research Focus**: Pan-Tilt-Zoom (PTZ) Camera Control via API and Shortcuts

---

## Table of Contents

1. [Overview](#overview)
2. [PTZ Commands Reference](#ptz-commands-reference)
3. [PTZ Preset Management](#ptz-preset-management)
4. [Supported Camera Types](#supported-camera-types)
5. [API Endpoints & Access Methods](#api-endpoints--access-methods)
6. [Real-time Control Methods](#real-time-control-methods)
7. [Speed Control](#speed-control)
8. [Setup & Configuration](#setup--configuration)
9. [Practical Examples](#practical-examples)
10. [Limitations & Constraints](#limitations--constraints)

---

## Overview

vMix PTZ Control is an advanced feature available in **4K and PRO editions** that enables direct control of Pan-Tilt-Zoom (PTZ) cameras from the main interface without requiring dedicated hardware or external software.

### Key Features:
- Real-time pan, tilt, and zoom control
- Preset position recall via Virtual Inputs
- Multiple control methods (shortcuts, joystick, mouse)
- Speed adjustable control
- Multiple camera management
- Network-based control (Ethernet/IP)

### Availability:
- **vMix 4K Edition**: Full PTZ support
- **vMix PRO Edition**: Full PTZ support
- **Earlier editions**: Limited or no PTZ support

---

## PTZ Commands Reference

### 1. Position Control Functions

#### SetPanX
**Purpose**: Change horizontal pan position
**Value Range**: `-2` to `2`
- `-2` = 100% to left
- `0` = centered
- `2` = 100% to right

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=SetPanX&Input=[InputNumber]&Value=[Value]
```

**Example - Pan 50% left**:
```
http://127.0.0.1:8088/API/?Function=SetPanX&Input=1&Value=-1
```

---

#### SetPanY
**Purpose**: Change vertical pan position
**Value Range**: `-2` to `2`
- `-2` = 100% to bottom
- `0` = centered
- `2` = 100% to top

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=SetPanY&Input=[InputNumber]&Value=[Value]
```

**Example - Pan 50% upward**:
```
http://127.0.0.1:8088/API/?Function=SetPanY&Input=1&Value=1
```

---

#### SetZoom
**Purpose**: Change zoom level of input
**Value Range**: `0` to `5`
- `1` = 100% (normal zoom)
- `0.5` = 50% zoom out
- `2` = 200% zoom in
- `5` = 500% maximum zoom

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=SetZoom&Input=[InputNumber]&Value=[Value]
```

**Example - Zoom to 150%**:
```
http://127.0.0.1:8088/API/?Function=SetZoom&Input=1&Value=1.5
```

---

### 2. Continuous Movement Commands

These commands initiate continuous movement until a stop command is issued.

#### PTZMoveUp
**Purpose**: Move camera upward continuously
**Speed Control**: Specify fractional value (0 to 1) for custom speed
**Default**: Uses speed slider from Input Settings PTZ tab

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=PTZMoveUp&Input=[InputNumber]&Value=[Speed]
```

**Example - Move up at default speed**:
```
http://127.0.0.1:8088/API/?Function=PTZMoveUp&Input=1
```

**Example - Move up at 50% speed**:
```
http://127.0.0.1:8088/API/?Function=PTZMoveUp&Input=1&Value=0.5
```

---

#### PTZMoveDown
**Purpose**: Move camera downward continuously
**Speed Control**: Fractional value (0 to 1)

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=PTZMoveDown&Input=[InputNumber]&Value=[Speed]
```

---

#### PTZMoveLeft
**Purpose**: Move camera left continuously
**Speed Control**: Fractional value (0 to 1)

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=PTZMoveLeft&Input=[InputNumber]&Value=[Speed]
```

---

#### PTZMoveRight
**Purpose**: Move camera right continuously
**Speed Control**: Fractional value (0 to 1)

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=PTZMoveRight&Input=[InputNumber]&Value=[Speed]
```

---

#### PTZMoveStop
**Purpose**: Stop all camera movement
**Speed Control**: N/A

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=PTZMoveStop&Input=[InputNumber]
```

---

#### PTZZoomIn
**Purpose**: Zoom in continuously
**Speed Control**: Fractional value (0 to 1)

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=PTZZoomIn&Input=[InputNumber]&Value=[Speed]
```

---

#### PTZZoomOut
**Purpose**: Zoom out continuously
**Speed Control**: Fractional value (0 to 1)

**API Syntax**:
```
http://127.0.0.1:8088/API/?Function=PTZZoomOut&Input=[InputNumber]&Value=[Speed]
```

---

### 3. Input Specification Methods

When calling any PTZ command, inputs can be specified in three ways:

1. **By Number**: `Input=1` (first input, starts at 1)
2. **Special References**:
   - `Input=0` - Preview input
   - `Input=-1` - Active/Program input
   - `Input=-3` - Currently hovered input
3. **By Name**: `Input=CameraNameHere` (case-sensitive, full name required)
4. **By GUID**: Using XML Key attribute identifier

---

## PTZ Preset Management

### Virtual Inputs Method (Primary Preset System)

vMix's native preset system uses **Virtual Inputs** to save and recall PTZ positions.

#### Creating a Preset:

1. **Position the Camera**: Move PTZ camera to desired position using controls
2. **Create Virtual Input**: Click "Create Input at this Position" button in PTZ Settings
3. **Name the Preset**: vMix generates a new input representing that position
4. **Automatic Thumbnail**: Each virtual input shows thumbnail of camera position

#### Recalling a Preset:

When you select a Virtual Input into vMix Preview:
- Camera automatically moves to saved position
- Movement speed controlled by "Position Speed" slider
- Transitions happen in real-time

**Example Workflow**:
```
Input: PTZ Camera (Main Input)
  └─ Virtual Input 1: "Wide Shot"
  └─ Virtual Input 2: "Close Up Presenter"
  └─ Virtual Input 3: "Podium View"
  └─ Virtual Input 4: "Audience Shot"

Bring "Close Up Presenter" to Preview → Camera moves automatically
```

#### Updating a Preset:

1. Move camera to new position
2. Click "Update" button for that virtual input preset
3. New position is saved and will be used for future recalls

#### Advantages of Virtual Input Presets:
- Visual thumbnails for easy identification
- Simple drag-and-drop to Preview
- Persistent storage in vMix project
- No camera firmware dependency
- Can manage multiple cameras as single production

#### Limitations:
- Presets are vMix project-specific (not stored on camera)
- Requires manual recreation if vMix project is lost
- All presets stored locally in vMix configuration

### Camera-Native Presets:

Some PTZ cameras support preset storage on device:
- **Sony VISCA over IP**: Full preset support with position speed control
- **Panasonic CGI PTZ**: Preset support (some models exclude AW-HE50, AW-HE120, AW-HE60)
- **PTZ Optics VISCA/UDP**: Preset support (pan speed only; zoom fixed)

**Note**: vMix does not expose native camera presets directly via API. Recall happens through Virtual Inputs and camera positioning.

---

## Supported Camera Types

### 1. PTZ Optics Cameras

**Protocol**: VISCA over UDP
**Models**: All current PTZ Optics models

**Features**:
- VISCA over UDP network control
- Pan, tilt, zoom control
- Preset recall via vMix Virtual Inputs
- Position speed control (pan only; zoom fixed)

**Connection**: Ethernet (same network as vMix)

---

### 2. Sony PTZ Cameras

**Protocol**: VISCA over IP (for SRG series)
**Supported Models**:
- SRG-300 series
- All Sony VISCA over IP models
- Telycam models (compatible with VISCA over IP)
- NewTek compatible models
- Lumens compatible models

**Features**:
- VISCA over IP network control
- Full pan, tilt, zoom control
- Position speed control supported
- CGI control over Ethernet
- Native preset storage on camera

**Connection**: Ethernet (static IP address required)

---

### 3. Panasonic PTZ Cameras

**Protocol**: CGI (Common Gateway Interface) control over Ethernet
**Supported Models**:
- AW-HE40 series
- AW-HE50 series (no position speed control)
- AW-HE60 series (no position speed control)
- AW-HE65 series
- AW-HE70 series
- AW-HE120 series (no position speed control)
- AW-HE130 series

**Features**:
- CGI-based network control
- Full pan, tilt, zoom functionality
- Position speed control (not available on HE50, HE60, HE120)
- High-quality imaging

**Connection**: Ethernet with static IP address

---

### 4. ValueHD Cameras

**Protocol**: VISCA over UDP
**Status**: Full compatibility

**Features**:
- Similar to PTZ Optics protocol
- Network-based PTZ control
- Virtual input preset system

---

### 5. USB Cameras (UVC Standard)

**Protocol**: USB Video Class (UVC) PTZ
**Supported Models**: USB cameras with UVC PTZ support
- HuddleCamHD Pro (4K USB)
- ObsBOT Tiny (USB camera)
- Other UVC-compliant webcams

**Connection**: Direct USB connection to vMix machine

**Control Methods**:
- UVC PTZ controls in vMix
- Virtual PTZ (digital pan/tilt/zoom)
- Standard shortcuts

**Advantages**:
- No network configuration needed
- Simple USB connection
- Ideal for studio setups

---

### 6. Virtual PTZ

**Type**: Digital pan, tilt, zoom on any input

**Features**:
- Convert any video input into PTZ camera
- Selectable zoom limits (prevent excessive digital zoom)
- Useful for fixed cameras or streams
- No hardware PTZ camera required

**Supported Inputs**:
- Cameras without PTZ capability
- RTSP streams
- NDI sources
- Any video source

---

### Unsupported Camera Types

**Serial-Based Cameras** (NOT supported):
- VISCA over RS-232/RS-422 (serial)
- Pelco D (serial)
- Pelco P (serial)
- Any camera requiring RS-485 serial connection

**Reason**: vMix only supports network-based PTZ control. Serial protocols require external converters and are not natively supported.

---

## API Endpoints & Access Methods

### 1. HTTP Web API (Primary Method)

**Purpose**: RESTful-style HTTP requests for PTZ control
**Protocol**: HTTP GET requests
**Default Port**: 8088
**Default Address**: `http://127.0.0.1:8088/API/`

#### Basic Syntax:
```
http://[vMix_IP]:8088/API/?Function=[FunctionName]&Input=[InputNumber]&Value=[Value]&Duration=[Duration]
```

#### Parameters:

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| Function | Yes | Shortcut function to execute | SetPanX |
| Input | Yes (usually) | Target input by number, name, or GUID | 1 or "PTZ Camera" |
| Value | Depends on function | Numeric value for function | -1 or 0.75 |
| Duration | No | Transition time in milliseconds | 1000 |
| SelectedIndex | No | For text/XAML elements | 0 |
| SelectedName | No | For text/XAML elements | "textField" |

#### Response Format:
- **Success**: HTTP 200 with XML state information
- **Error**: HTTP 500
- **No Parameters**: Returns full vMix XML state

#### Example Requests:

**Example 1: Pan left**
```
http://127.0.0.1:8088/API/?Function=PTZMoveLeft&Input=1&Value=0.8
```

**Example 2: Zoom in with duration**
```
http://127.0.0.1:8088/API/?Function=SetZoom&Input=1&Value=2&Duration=500
```

**Example 3: Position by name**
```
http://127.0.0.1:8088/API/?Function=SetPanY&Input=MainPTZCamera&Value=1
```

**Example 4: Stop movement**
```
http://127.0.0.1:8088/API/?Function=PTZMoveStop&Input=1
```

---

### 2. TCP API (Low-Level Protocol)

**Purpose**: Direct TCP socket connection for real-time control
**Protocol**: TCP text-based command/response
**Default Port**: 8099
**Use Case**: Custom applications, remote control systems

#### Connection Method:
```
telnet 127.0.0.1 8099
```

#### TCP Command Syntax:
```
FUNCTION [FunctionName] [QueryString]
```

The TCP API executes the same shortcut functions as HTTP API but through direct socket connection.

#### Example TCP Commands:

**Set pan position via TCP**:
```
FUNCTION SetPanX Input=1&Value=-1
```

**Zoom via TCP**:
```
FUNCTION SetZoom Input=1&Value=1.5
```

#### Other TCP Commands:

| Command | Purpose | Response |
|---------|---------|----------|
| TALLY | Get tally state | Tally status |
| XML | Get full state | Complete XML state |
| XMLTEXT [path] | Get XML value | Specific value |
| SUBSCRIBE [event] | Subscribe to events | Confirmation |
| QUIT | Close connection | Connection closed |

#### Advantages:
- Lower latency than HTTP
- Persistent connection
- Better for real-time applications
- Suitable for continuous movement scenarios

---

### 3. Function-Based API

**Method**: Direct function calls via Shortcuts system
**Access Point**: Settings → Shortcuts → Add
**Available in**: All control methods (keyboard, MIDI, game controller, API)

#### Function Availability:
Any function available in the Shortcuts dropdown can be called via:
- HTTP API
- TCP API
- Virtual Input selection
- Physical shortcuts (keyboard, MIDI, etc.)

#### Complete Function Reference:
Official documentation at: `https://www.vmix.com/help25/ShortcutFunctionReference.html`

Unofficial reference at: `https://vmixapi.com/`

---

## Real-time Control Methods

### 1. Continuous Movement Model

**Use Case**: Smooth, operator-controlled pan/tilt/zoom
**Method**: `PTZMoveUp`, `PTZMoveLeft`, etc. + `PTZMoveStop`
**Behavior**: Camera moves continuously until stop command

#### Implementation:

**Joystick/Controller**:
- Map analog sticks to directional functions
- Speed scaled by stick pressure (if pressure-sensitive)
- Release stick triggers `PTZMoveStop`

**HTTP API**:
```
// Start moving up at 75% speed
http://127.0.0.1:8088/API/?Function=PTZMoveUp&Input=1&Value=0.75

// Stop movement
http://127.0.0.1:8088/API/?Function=PTZMoveStop&Input=1
```

**Speed Control**:
- Default: Uses Input Settings PTZ tab speed sliders
- Custom: Pass fractional value (0 to 1) in Value parameter
- Pressure-sensitive: Enable "Pressure Enabled" in Xbox controller template

#### Advantages:
- Smooth, natural camera movement
- Operator control via joystick
- Real-time responsiveness
- Ideal for live production

#### Limitations:
- Requires continuous API calls or hardware integration
- Not suitable for automated scripts (unless looped)
- Harder to predict exact final position

---

### 2. Discrete Positioning Model

**Use Case**: Snap-to-position camera moves (preset recall)
**Method**: Virtual Inputs or `SetPanX`/`SetPanY`/`SetZoom`
**Behavior**: Camera moves to absolute position

#### Virtual Input Method:

**Workflow**:
1. Define preset positions as Virtual Inputs
2. Select Virtual Input to Preview
3. Camera automatically transitions to position
4. Duration controlled by "Position Speed" slider

**HTTP API Equivalent**:
```
// Recall preset by selecting input
http://127.0.0.1:8088/API/?Function=PreviewInput&Input=2
// Where Input=2 is a Virtual Input preset
```

#### SetPanX/SetPanY/SetZoom Method:

**Direct Positioning**:
```
// Move to absolute position immediately
http://127.0.0.1:8088/API/?Function=SetPanX&Input=1&Value=-0.5
http://127.0.0.1:8088/API/?Function=SetPanY&Input=1&Value=0.75
http://127.0.0.1:8088/API/?Function=SetZoom&Input=1&Value=1.5
```

**With Duration**:
```
// Move to position over 1 second (some functions support Duration)
http://127.0.0.1:8088/API/?Function=SetPanX&Input=1&Value=-0.5&Duration=1000
```

#### Advantages:
- Reproducible positions
- Easy automation
- Predictable camera placement
- Simple scripting/scheduling
- No operator interaction needed

#### Limitations:
- Less natural than smooth movement
- Not suitable for following moving subjects
- Requires predefined positions
- May look jerky if transition too fast

---

### 3. Speed Control Mechanisms

#### Movement Speed
Controls pan/tilt/zoom speed during manual operation

**Configuration**:
- Location: Input Settings → PTZ tab → Speed sliders
- Range: Adjustable per camera
- Application: Used when PTZMove* commands don't specify Value

**Camera Support**: All supported PTZ cameras

#### Position Speed
Controls camera transition speed when recalling presets

**Configuration**:
- Location: Input Settings → PTZ tab → Position Speed slider
- Range: Adjustable
- Application: Used when transitioning to Virtual Input presets

**Camera Support**:
- Sony VISCA over IP: Full support
- Panasonic CGI PTZ: All models except HE50, HE60, HE120
- PTZ Optics: Pan speed only (zoom speed fixed)

#### Xbox Controller Pressure Sensitivity

**Feature**: Variable speed based on stick pressure
**Configuration**: Settings → Shortcuts → [PTZ Function] → Pressure Enabled
**Controllers**: Xbox-compatible USB game controllers
**Advantage**: Natural analog control like broadcast PTZ systems

---

## Setup & Configuration

### Step 1: Enable PTZ on Input

1. **Open Input Settings**
   - Right-click input → Edit
   - Or click settings icon on input

2. **Select PTZ Tab**
   - Look for "PTZ" tab in input settings

3. **Choose Device Type**
   - **Network PTZ**: For IP-based cameras
   - **VISCA over IP**: For Sony SRG series
   - **VISCA over UDP**: For PTZ Optics, ValueHD
   - **Panasonic CGI**: For Panasonic models
   - **UVC PTZ**: For USB cameras
   - **Virtual PTZ**: For non-PTZ sources

### Step 2: Configure Connection

**For Network Cameras**:
1. Enter camera IP address or hostname
2. Enter port (usually default is fine)
3. Click "Connect"
4. Verify connection status

**For USB Cameras**:
1. Select camera from dropdown
2. Choose UVC PTZ
3. Click "Connect"

**For Virtual PTZ**:
1. Select "Virtual PTZ"
2. Configure Zoom Limit slider (prevents excessive digital zoom)
3. No network configuration needed

### Step 3: Configure Control Speeds

1. **Movement Speed**: Adjust "Pan Speed", "Tilt Speed", "Zoom Speed" sliders
   - Controls speed of PTZMove* commands
   - Applies to joystick and manual controls

2. **Position Speed**: Adjust "Position Speed" slider
   - Controls transition speed to presets
   - Applies when selecting Virtual Inputs

### Step 4: Create Presets (Virtual Inputs)

1. **Position Camera**: Use PTZ controls to position camera
2. **Click "Create Input at this Position"**
   - vMix creates new Virtual Input
   - Shows thumbnail of position
3. **Repeat** for each desired preset position
4. **Name Presets**: Rename for easy identification

### Step 5: Assign Shortcuts (Optional)

1. **Go to**: Settings → Shortcuts
2. **Click**: Add Shortcut
3. **Select Function**: Choose PTZ command
   - PTZMoveUp, PTZMoveLeft, etc.
4. **Select Input**: Choose PTZ camera input
5. **Assign Trigger**:
   - Keyboard key
   - MIDI controller
   - Game controller button
6. **Save Shortcut**

---

## Practical Examples

### Example 1: Multi-Camera Production Script

**Scenario**: Auto-switching between three virtual presets of one PTZ camera

**Setup**:
- Input 1: PTZ Camera (network camera)
- Input 2: "Wide Shot" (Virtual Input preset)
- Input 3: "Speaker Close-Up" (Virtual Input preset)
- Input 4: "Audience View" (Virtual Input preset)

**HTTP API Sequence** (executed by automation/script):
```
# Scene 1: Opening wide shot
http://127.0.0.1:8088/API/?Function=PreviewInput&Input=2

# Wait 10 seconds

# Scene 2: Switch to speaker close-up
http://127.0.0.1:8088/API/?Function=PreviewInput&Input=3

# Wait 5 seconds

# Scene 3: Switch to audience view
http://127.0.0.1:8088/API/?Function=PreviewInput&Input=4
```

**Advantages**:
- One camera appears as three inputs
- Smooth preset transitions
- Simple automation

---

### Example 2: Joystick-Controlled Pan/Tilt/Zoom

**Setup**:
- Xbox controller connected via USB
- PTZ camera configured in Input 1

**Shortcut Configuration**:
```
Shortcut 1: PTZMoveUp (Xbox Y button) → Input=1 → Pressure Enabled
Shortcut 2: PTZMoveDown (Xbox A button) → Input=1 → Pressure Enabled
Shortcut 3: PTZMoveLeft (Xbox X button) → Input=1 → Pressure Enabled
Shortcut 4: PTZMoveRight (Xbox B button) → Input=1 → Pressure Enabled
Shortcut 5: PTZZoomIn (Xbox Right Trigger) → Input=1
Shortcut 6: PTZZoomOut (Xbox Left Trigger) → Input=1
Shortcut 7: PTZMoveStop (Xbox Guide button) → Input=1
```

**Workflow**:
- Operator uses Xbox controller to pan/tilt/zoom
- Smooth movement with pressure sensitivity
- Professional control experience

---

### Example 3: API-Based PTZ Positioning

**Scenario**: Pan and zoom to specific coordinates via HTTP API

```bash
#!/bin/bash

# Function to set PTZ position
set_ptz_position() {
    local pan=$1
    local tilt=$2
    local zoom=$3

    echo "Setting PTZ position: Pan=$pan, Tilt=$tilt, Zoom=$zoom"

    # Set pan
    curl "http://127.0.0.1:8088/API/?Function=SetPanX&Input=1&Value=$pan"

    # Set tilt
    curl "http://127.0.0.1:8088/API/?Function=SetPanY&Input=1&Value=$tilt"

    # Set zoom
    curl "http://127.0.0.1:8088/API/?Function=SetZoom&Input=1&Value=$zoom"
}

# Usage examples
set_ptz_position -1 1 1        # Left-Up, 100% zoom (wide)
set_ptz_position 0 0 2         # Center, 200% zoom (close-up)
set_ptz_position 1 -1 1.5      # Right-Down, 150% zoom
```

**Use Cases**:
- Automated camera control
- Integration with scheduling systems
- Multi-camera coordination

---

### Example 4: TCP API Real-Time Control

**Scenario**: Custom application using TCP API for low-latency PTZ control

```python
#!/usr/bin/env python3
import socket
import time

class vMixPTZ:
    def __init__(self, host='127.0.0.1', port=8099):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send_command(self, function, input_num, value=None):
        if value is None:
            cmd = f"FUNCTION {function} Input={input_num}\n"
        else:
            cmd = f"FUNCTION {function} Input={input_num}&Value={value}\n"

        self.socket.send(cmd.encode())
        response = self.socket.recv(1024).decode()
        return response

    def pan_left(self, speed=0.8):
        return self.send_command('PTZMoveLeft', 1, speed)

    def pan_right(self, speed=0.8):
        return self.send_command('PTZMoveRight', 1, speed)

    def tilt_up(self, speed=0.8):
        return self.send_command('PTZMoveUp', 1, speed)

    def tilt_down(self, speed=0.8):
        return self.send_command('PTZMoveDown', 1, speed)

    def stop(self):
        return self.send_command('PTZMoveStop', 1)

    def zoom(self, level):
        return self.send_command('SetZoom', 1, level)

    def close(self):
        self.socket.close()

# Usage
if __name__ == '__main__':
    ptz = vMixPTZ()
    ptz.connect()

    # Move up and left
    ptz.tilt_up(0.5)
    time.sleep(2)
    ptz.pan_left(0.5)
    time.sleep(2)
    ptz.stop()

    # Zoom in
    ptz.zoom(2.0)

    ptz.close()
```

---

## Limitations & Constraints

### Hardware Limitations

1. **Network-Only PTZ Control**
   - Serial protocols (RS-232/RS-422 VISCA) not supported
   - Cameras without network control cannot be used
   - Requires stable Ethernet connection

2. **Camera Firmware Dependencies**
   - Some preset operations camera-dependent
   - Protocol variations between manufacturers
   - Firmware updates may affect compatibility

3. **Speed Control Variations**
   - Position speed not supported on all cameras:
     - Panasonic: No support on HE50, HE60, HE120 models
     - PTZ Optics: Zoom speed is fixed
   - May require camera-specific configuration

### API Limitations

1. **HTTP API Port Binding**
   - Default port 8088 may conflict with other services
   - Requires port configuration access
   - No native HTTPS support (use external proxy)

2. **TCP API**
   - Text-based protocol (lower throughput than binary)
   - Requires persistent connection management
   - May have latency on high-latency networks

3. **No Native REST API**
   - vMix uses HTTP GET (query string) not true REST
   - Third-party REST wrapper available at GitHub
   - Official API is function-based, not resource-oriented

### Operational Limitations

1. **Preset Management**
   - Virtual Input presets not stored on camera
   - Presets lost if vMix project backup not maintained
   - Manual recreation required after hardware failure
   - No native preset export/import functionality

2. **Multiple Camera Coordination**
   - Each PTZ camera requires separate API calls
   - No atomic multi-camera operations
   - Requires external orchestration layer

3. **Pan/Tilt/Zoom Coordination**
   - `SetPanX`, `SetPanY`, `SetZoom` are independent operations
   - No single "goto position" atomic command
   - Requires multiple HTTP requests for single position

### Network Limitations

1. **Latency Sensitivity**
   - Continuous movement depends on network latency
   - HTTP API call overhead may cause jitter
   - TCP API provides lower latency alternative

2. **Bandwidth Requirements**
   - Multiple continuous PTZMove* commands require bandwidth
   - Network congestion affects responsiveness
   - Shared network may cause control lag

3. **Firewall/NAT**
   - Port 8088 (HTTP) and 8099 (TCP) must be accessible
   - NAT traversal required for remote control
   - VPN or tunnel recommended for remote access

### Feature Limitations

1. **No Advanced Features**
   - No pattern recording/playback
   - No autonomous tracking via API
   - No position interpolation
   - Speed ramps not available

2. **Version Dependencies**
   - Features vary by vMix version (22-29)
   - Documentation may lag actual implementation
   - Backward compatibility not guaranteed

3. **Documentation Gaps**
   - Official documentation incomplete for some functions
   - `SetPTZCamera` parameters not fully documented
   - Unofficial vMixAPI.com provides community documentation

---

## Recommended Architecture for Production

### Multi-Camera PTZ System

```
Control Sources:
├── Joystick/Game Controller
├── Keyboard Shortcuts
├── Elgato StreamDeck
├── HTTP API (External Control)
└── TCP API (Real-time Applications)

↓

vMix PTZ Input Router:
├── Input 1: PTZ Camera 1 (Main)
├── Input 2: PTZ Camera 1 - Virtual Preset "Wide"
├── Input 3: PTZ Camera 1 - Virtual Preset "Close-Up"
├── Input 4: PTZ Camera 1 - Virtual Preset "Audience"
├── Input 5: PTZ Camera 2 (Backup)
├── Input 6: PTZ Camera 2 - Virtual Preset "Detail"
└── ...additional presets...

↓

vMix Preview/Program Output:
└── One or Multiple Outputs via Streaming/Mixing
```

### Speed Control Strategy

- **Live Operator Control**: Use joystick with pressure sensitivity
- **Automated Positioning**: Use Position Speed slider (0.5-1.0 seconds)
- **Real-time Streaming**: Use TCP API for low-latency control
- **Scheduled Events**: Use HTTP API with external orchestration

---

## Key Takeaways

1. **vMix PTZ is robust** for network-based cameras (IP, VISCA over UDP/IP)
2. **Virtual Inputs provide excellent preset management** for productions
3. **Three control methods** (shortcuts, joystick, API) accommodate different workflows
4. **HTTP API is accessible** from any networked device with basic HTTP client
5. **TCP API offers lower latency** for real-time applications
6. **Speed control is flexible** with both default and custom settings
7. **Multi-camera management is possible** but requires external orchestration
8. **Virtual PTZ** extends PTZ capabilities to non-PTZ camera inputs
9. **Documentation exists but is scattered** across official and third-party sources
10. **Proper network configuration critical** for reliable PTZ operation

---

## Resources

### Official Documentation
- **PTZ Main**: https://www.vmix.com/help25/PTZPanTiltZoom.html
- **PTZ Shortcuts**: https://www.vmix.com/help25/PTZControlShortcuts.html
- **Virtual Inputs**: https://www.vmix.com/help24/PTZControlVirtualInputs.html
- **HTTP Web API**: https://www.vmix.com/help25/DeveloperAPI.html
- **TCP API**: https://www.vmix.com/help25/TCPAPI.html
- **Shortcut Function Reference**: https://www.vmix.com/help25/ShortcutFunctionReference.html

### Third-Party Resources
- **Unofficial API Reference**: https://vmixapi.com/
- **vMix Knowledge Base**: https://www.vmix.com/knowledgebase/
- **vMix Forums**: https://forums.vmix.com/
- **PTZOptics Integration**: https://ptzoptics.com/vmix-integration/
- **StreamGeeks Guide**: https://streamgeeks.us/ptz-camera-controls-in-vmix/

### Related Technologies
- **Supported Cameras**: https://www.vmix.com/software/supported-hardware.aspx
- **vMix WebSocket API**: Available in newer versions
- **NDI Integration**: Enables remote camera control
- **MIDI Controller Integration**: For hardware PTZ control

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-12 | 1.0 | Initial comprehensive research report |

**Research Completed**: 20-30 minutes
**Last Updated**: 2025-11-12 17:00 UTC
**Status**: Complete & Ready for Integration

---

## Next Steps for Session 3

1. **API Integration Testing**: Implement HTTP API calls with PTZ commands
2. **Preset Workflow**: Create vMix project with multi-camera virtual inputs
3. **Real-time Control**: Develop TCP API client for low-latency control
4. **Hardware Integration**: Test with actual PTZ cameras (PTZOptics, Sony SRG series)
5. **Performance Optimization**: Benchmark API response times and throughput
6. **Documentation**: Create integration runbook based on findings

