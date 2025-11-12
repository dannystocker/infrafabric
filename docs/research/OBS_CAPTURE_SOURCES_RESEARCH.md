# OBS Studio Capture Source Types: Master Integration Sprint Session 3

**Research Period**: November 12, 2025
**Research Agent**: Haiku 4.5 Research Agent
**Status**: Comprehensive Research Complete

---

## Table of Contents

1. [Window Capture Sources](#window-capture-sources)
2. [Display Capture Sources](#display-capture-sources)
3. [Game Capture Source](#game-capture-source)
4. [Audio Capture Sources](#audio-capture-sources)
5. [Source Properties & Configuration](#source-properties--configuration)
6. [WebSocket API Integration](#websocket-api-integration)
7. [Cross-Platform Differences](#cross-platform-differences)
8. [Implementation Guide](#implementation-guide)

---

## Window Capture Sources

### Overview
Window Capture allows you to capture a specific application window and its contents, keeping only that window visible even if other windows overlap it. This is ideal for recording tutorials, presentations, or specific application workflows.

### Source Types by Platform

#### Windows
- **Source Type**: `window_capture` (legacy) or Windows Graphics Capture (WGC)
- **Capture Methods**:
  - **BitBlt** (Legacy): Traditional Windows API method, works with most windows
  - **Windows Graphics Capture (WGC)**: Modern method (Windows 10+), captures windows that BitBlt cannot
  - **Automatic**: OBS selects the best method automatically

#### macOS
- **Source Type**: `window_capture` (deprecated on macOS 13.0+)
- **Status**: Not recommended due to poor performance
- **Recommendation**: Use Display Capture instead for better performance

#### Linux
- **Window Capture**: Standard Xcomposite-based capture
- **Window Capture (Xcomposite)**: X11-based window capture with advanced options
- **Window Capture (PipeWire)**: Modern Wayland-based capture

### Window Capture Properties

#### Windows Platform
```
{
  "window": "window_class_or_title",           // Target window identifier
  "capture_method": "auto|bitblt|wgc",        // Capture method selection
  "client_area": true|false,                   // Capture client area only (WGC)
  "cursor": true|false,                        // Show mouse cursor (default: true)
  "force_sdr": false|true,                     // Force SDR mode (WGC)
  "compatibility": true|false                  // BitBlt compatibility mode
}
```

#### macOS Platform
```
{
  "window": "window_id",                       // Target window ID
  "show_empty_names": false|true,              // Display unnamed windows
  "show_shadow": true|false                    // Show window shadow
}
```

#### Linux Platform (Xcomposite)
```
{
  "window": "window_id",                       // X11 window ID
  "capture_cursor": true|false,                // Show mouse cursor
  "use_randr": false|true,                     // Use RandR for multihead
  "crop_top": 0,                               // Crop top pixels
  "crop_left": 0,                              // Crop left pixels
  "crop_right": 0,                             // Crop right pixels
  "crop_bottom": 0,                            // Crop bottom pixels
  "swap_redblue": false|true,                  // Swap red/blue channels
  "lock_x": false|true                         // Lock X server during capture
}
```

### Window Capture API Creation

#### WebSocket API (obs-websocket 5.0+)

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Scene 1",
    "inputName": "Application Window",
    "inputKind": "window_capture",
    "inputSettings": {
      "window": "[explorer.exe]:Program Manager",
      "capture_method": "auto",
      "cursor": true
    }
  }
}
```

#### Property Retrieval

```json
{
  "requestType": "GetInputSettings",
  "requestData": {
    "inputName": "Application Window"
  }
}
```

#### Property Update

```json
{
  "requestType": "SetInputSettings",
  "requestData": {
    "inputName": "Application Window",
    "inputSettings": {
      "cursor": false,
      "capture_method": "wgc"
    }
  }
}
```

### Window Match Priority (Windows Only)

When the original window is unavailable, OBS uses Window Match Priority to find an alternative:
- **Window Title**: Match by exact window title
- **Class**: Match by window class name
- **Executable**: Match by process executable name

---

## Display Capture Sources

### Overview
Display/Screen Capture records your entire monitor output. Unlike Window Capture, it captures the full desktop including all windows, wallpaper, and overlays.

### Source Types by Platform

#### Windows & Linux
- **Source Type**: `monitor_capture` or `dxgi_output_duplication`
- **Method**: DXGI (Windows) - Direct X Graphics Infrastructure
- **Modern Method**: Windows 10 (1903+) with Windows.Graphics.Capture

#### macOS
- **Source Type**: `macos_screen_capture` (macOS 13.0+)
- **Legacy**: `display_capture` (deprecated)
- **Capture Methods**:
  - Display Capture: Full screen capture
  - Application Capture: Specific application window
  - Window Capture: Individual window (performant alternative)

#### Linux Wayland
- **Source Type**: `screen_capture_pipewire` or `screen_capture_xshm`
- **Screen Capture (XSHM)**: X11-based screen capturing
- **Screen Capture (PipeWire)**: Modern Wayland-based capture

### Display Capture Properties

#### Windows Platform
```
{
  "monitor_id": "\\\\?\\DISPLAY#Default_Monitor#xxxxxxx",  // Monitor identifier
  "method": "dxgi|wc",                                      // Capture method
  "cursor": true|false,                                     // Show cursor
  "force_sdr": false|true                                   // SDR mode
}
```

#### macOS Platform
```
{
  "display": 0,                                 // Display index (0=primary)
  "show_cursor": true|false,                   // Show mouse cursor
  "enable_hidden_windows": false|true          // Capture hidden windows
}
```

#### Linux Platform
```
{
  "screen": 0,                                  // Screen index
  "capture_cursor": true|false,                 // Show cursor
  "x": 0,                                       // X offset
  "y": 0,                                       // Y offset
  "width": 1920,                                // Capture width
  "height": 1080                                // Capture height
}
```

### Display Capture API Creation

#### WebSocket API (obs-websocket 5.0+)

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Desktop Scene",
    "inputName": "Primary Monitor",
    "inputKind": "monitor_capture",
    "inputSettings": {
      "monitor_id": "\\\\?\\DISPLAY#Default_Monitor#00000001",
      "method": "dxgi",
      "cursor": true
    }
  }
}
```

### Important Limitation

Only **one Display Capture source can be created per monitor**. If you need the same display in multiple scenes, create a reference to the existing Display Capture source rather than duplicating it.

---

## Game Capture Source

### Overview
Game Capture is the most efficient way to capture games in OBS Studio. It uses GPU-accelerated capture (D3D shared textures on Windows) and provides the best performance for gaming streams.

**Platform Support**: Windows only (no native macOS or Linux support)

### Game Capture Properties

#### Capture Mode Selection
1. **Automatic Fullscreen Mode**: Captures any fullscreen application automatically
2. **Capture Specific Window**: Specify exact game window
3. **Hotkey Method**: Use keyboard shortcut to start/stop capture

#### Configuration Properties

```json
{
  "capture_mode": "auto|window|hotkey",           // Capture mode
  "window": "[Game.exe]:Game Window",             // Target window (if mode=window)
  "capture_cursor": true|false,                   // Show mouse cursor (default: true)
  "antiCheatCompatibility": true|false,           // Anti-cheat hook support (default: true)
  "allowTransparency": false|true,                // Remove black backgrounds (default: false)
  "limitFramerate": false|true,                   // Limit to OBS FPS (default: false)
  "captureOverlays": false|true,                  // Capture game overlays (default: false)
  "useSLICrossfire": false|true,                  // SLI/Crossfire mode (default: false)
  "useMultiAdapter": false|true                   // Multi-GPU support
}
```

### Game Capture Technical Details

#### Capture Methods
- **D3D Shared Texture Capture**: Primary method for DirectX/OpenGL games
  - GPU-accelerated
  - Most efficient (minimal CPU overhead)
  - Works with fullscreen and windowed games
  - Requires DirectX 10+ or OpenGL 2.0+

#### Feature Details

| Property | Description | Default |
|----------|-------------|---------|
| **SLI/Crossfire Mode** | Switches from shared texture to memory capture for multi-GPU setups | Off |
| **Allow Transparency** | Removes opaque black backgrounds for games with transparency | Off |
| **Limit Framerate** | Prevents capture at higher FPS than OBS is configured for | Off |
| **Capture Cursor** | Shows mouse cursor during capture | On |
| **Anti-Cheat Hook** | Compatibility with anti-cheat detection systems | On |
| **Capture Overlays** | Captures game overlays if they don't conflict | Off |

### Game Capture API Creation

#### WebSocket API (obs-websocket 5.0+)

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Gaming Scene",
    "inputName": "Game Capture",
    "inputKind": "game_capture",
    "inputSettings": {
      "capture_mode": "auto",
      "antiCheatCompatibility": true,
      "allowTransparency": false,
      "limitFramerate": false,
      "captureOverlays": false,
      "capture_cursor": true
    }
  }
}
```

#### Game-Specific Configuration

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Gaming Scene",
    "inputName": "Valorant Capture",
    "inputKind": "game_capture",
    "inputSettings": {
      "capture_mode": "window",
      "window": "[VALORANT.exe]:VALORANT",
      "antiCheatCompatibility": true,
      "allowTransparency": false,
      "limitFramerate": true,
      "capture_cursor": false
    }
  }
}
```

### Game Capture Troubleshooting

**Black Screen Issues**:
- Enable "Allow Transparency" for games with transparent backgrounds
- Verify game is using DirectX/OpenGL compatible graphics API
- Check anti-cheat compatibility setting

**Performance Issues**:
- Reduce OBS encoding settings if GPU bottleneck
- Enable "Limit Framerate" to prevent excessive CPU usage
- Disable "Capture Overlays" if not needed

---

## Audio Capture Sources

### Overview
OBS provides multiple audio capture methods to record microphones, system audio, application audio, and output devices.

### Source Types by Platform

#### Windows & macOS
- **Audio Input Capture**: Microphones and line-in devices
- **Audio Output Capture**: System output and headphones
- **Application Audio Capture (BETA)**: Per-application audio (Windows 10 2004+, Windows 11)

#### Linux
- **Audio Capture (ALSA)**: ALSA audio system capture
- **Audio Capture (PulseAudio)**: PulseAudio system capture

### Audio Input/Output Capture Properties

#### Windows & macOS Configuration
```json
{
  "device_id": "device_uuid",              // Audio device identifier
  "use_device_timestamps": true|false      // Use device timestamps (Windows only)
}
```

#### Linux ALSA Configuration
```json
{
  "device": "hw:0,0",                      // ALSA device identifier
  "rate": 44100                            // Sample rate in Hz
}
```

#### Linux PulseAudio Configuration
```json
{
  "device": "device_name",                 // PulseAudio device name
  "rate": 48000                            // Sample rate in Hz
}
```

### Application Audio Capture (Windows)

**Platform Support**: Windows 10 (version 2004+) and Windows 11 only

```json
{
  "application": "Firefox.exe",            // Application executable name
  "device": "Stereo Mix|HDMI Output"       // Output device routing
}
```

### Audio Capture API Creation

#### WebSocket API - Microphone Input

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Stream Scene",
    "inputName": "Microphone",
    "inputKind": "wasapi_input_capture",
    "inputSettings": {
      "device_id": "{0.0.0.00000000}.{UUID-of-microphone}",
      "use_device_timestamps": true
    }
  }
}
```

#### WebSocket API - System Audio Output

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Stream Scene",
    "inputName": "System Audio",
    "inputKind": "wasapi_output_capture",
    "inputSettings": {
      "device_id": "{0.0.0.00000000}.{UUID-of-output-device}",
      "use_device_timestamps": true
    }
  }
}
```

#### WebSocket API - Application Audio (Windows 11)

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Stream Scene",
    "inputName": "Discord Audio",
    "inputKind": "win_wasapi_output_capture",
    "inputSettings": {
      "application": "Discord.exe"
    }
  }
}
```

### Audio Properties Management

#### Get Input Mute Status

```json
{
  "requestType": "GetInputMute",
  "requestData": {
    "inputName": "Microphone"
  }
}
```

#### Set Input Volume

```json
{
  "requestType": "SetInputVolume",
  "requestData": {
    "inputName": "Microphone",
    "inputVolume": {
      "mul": 1.0,                          // Multiplier (1.0 = 0dB)
      "db": 0.0                            // Decibels
    }
  }
}
```

#### Set Audio Monitoring Type

```json
{
  "requestType": "SetInputAudioMonitorType",
  "requestData": {
    "inputName": "Microphone",
    "monitorType": "none|monitorOnly|monitorAndOutput"
  }
}
```

**Monitor Types**:
- `none`: No monitoring (default)
- `monitorOnly`: Hear locally but don't send to stream
- `monitorAndOutput`: Hear locally and send to stream/recording

#### Audio Track Assignment

```json
{
  "requestType": "SetInputAudioTracks",
  "requestData": {
    "inputName": "Microphone",
    "audioTracks": 1                       // Bitmask: 1=Track 1, 2=Track 2, etc.
  }
}
```

### Audio Sync Offset

```json
{
  "requestType": "SetInputAudioSyncOffset",
  "requestData": {
    "inputName": "Microphone",
    "audioSyncOffset": 0                   // Milliseconds (positive = delay audio)
  }
}
```

### Audio Important Notes

**Echo Prevention**: Do not capture the same audio device in both global settings and as a scene source, as this will cause echo.

**Device Timestamp Usage**: On Windows, enabling "Use Device Timestamps" helps prevent audio desynchronization with video.

**Global vs Scene-Specific**: Audio sources can be configured globally in Settings > Audio or as scene-specific sources for better control.

---

## Source Properties & Configuration

### Getting Source Information

#### Retrieve Available Input Types

```json
{
  "requestType": "GetInputKindList"
}
```

**Response Example**:
```json
{
  "inputKinds": [
    "window_capture",
    "monitor_capture",
    "game_capture",
    "wasapi_input_capture",
    "wasapi_output_capture",
    "dshow_input",
    "ffmpeg_source",
    "text_gdiplus",
    "color_source",
    "image_source",
    "slideshow",
    "timer",
    "vlc_source"
  ]
}
```

#### Get Input Default Settings

```json
{
  "requestType": "GetInputDefaultSettings",
  "requestData": {
    "inputKind": "window_capture"
  }
}
```

#### Get Input Settings

```json
{
  "requestType": "GetInputSettings",
  "requestData": {
    "inputName": "Application Window"
  }
}
```

**Response**:
```json
{
  "inputSettings": {
    "window": "[explorer.exe]:Program Manager",
    "capture_method": "auto",
    "cursor": true
  }
}
```

### Setting Source Properties

#### Set Input Settings

```json
{
  "requestType": "SetInputSettings",
  "requestData": {
    "inputName": "Application Window",
    "inputSettings": {
      "cursor": false,
      "capture_method": "wgc"
    },
    "overlay": false                       // Update without adding to scene
  }
}
```

#### Rename Input

```json
{
  "requestType": "SetInputName",
  "requestData": {
    "inputName": "Application Window",
    "newInputName": "Visual Studio Window"
  }
}
```

### Input List and Enumeration

#### Get All Inputs

```json
{
  "requestType": "GetInputList",
  "requestData": {
    "inputKind": ""                        // Optional: filter by type
  }
}
```

**Response**:
```json
{
  "inputs": [
    {
      "inputName": "Primary Monitor",
      "inputKind": "monitor_capture",
      "inputIndex": 0
    },
    {
      "inputName": "Game Capture",
      "inputKind": "game_capture",
      "inputIndex": 1
    },
    {
      "inputName": "Microphone",
      "inputKind": "wasapi_input_capture",
      "inputIndex": 2
    }
  ]
}
```

### Input/Output Deinterlacing

#### Get Input Deinterlacing Settings

```json
{
  "requestType": "GetInputPropertiesListPropertyElements",
  "requestData": {
    "inputName": "Video Capture Device"
  }
}
```

#### Enable Deinterlacing

```json
{
  "requestType": "SetInputSettings",
  "requestData": {
    "inputName": "Video Capture Device",
    "inputSettings": {
      "deinterlace_mode": "adaptive|bob|linear"
    }
  }
}
```

---

## WebSocket API Integration

### Connection & Authentication

#### Connect to OBS WebSocket Server

```javascript
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:4455');

ws.on('open', () => {
  console.log('Connected to OBS WebSocket');
});

ws.on('message', (data) => {
  const message = JSON.parse(data);
  console.log('Received:', message);
});
```

**Default Port**: 4455 (configurable in OBS Settings > Tools > WebSocket Server Settings)

#### Authentication (if enabled)

```json
{
  "requestType": "Hello",
  "requestData": {
    "rpcVersion": 1,
    "authentication": "base64_encoded_auth_token"
  }
}
```

### Common Input Requests

#### Create Input (Generic Template)

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Scene Name",
    "inputName": "New Input",
    "inputKind": "source_type",
    "inputSettings": {
      "property1": "value1",
      "property2": "value2"
    },
    "sceneItemEnabled": true
  }
}
```

#### Remove Input

```json
{
  "requestType": "RemoveInput",
  "requestData": {
    "inputName": "Input to Remove"
  }
}
```

#### Get Input Properties

```json
{
  "requestType": "GetInputPropertiesListPropertyElements",
  "requestData": {
    "inputName": "Input Name"
  }
}
```

### Request/Response Pattern

```javascript
// Send request with ID for tracking
const requestId = `request_${Date.now()}`;

const request = {
  requestId: requestId,
  requestType: "CreateInput",
  requestData: {
    sceneName: "Scene 1",
    inputName: "New Window Capture",
    inputKind: "window_capture",
    inputSettings: {
      window: "[chrome.exe]:Google Chrome"
    }
  }
};

ws.send(JSON.stringify(request));

// Listen for response
ws.on('message', (data) => {
  const response = JSON.parse(data);

  if (response.requestId === requestId) {
    if (response.requestStatus.result) {
      console.log('Input created successfully');
    } else {
      console.error('Error:', response.requestStatus.comment);
    }
  }
});
```

### Error Handling

```json
{
  "requestId": "request_1234567890",
  "requestStatus": {
    "result": false,
    "code": 203,
    "comment": "Input kind does not exist"
  }
}
```

**Common Error Codes**:
- `200`: OK
- `203`: Input kind does not exist
- `204`: Resources not found
- `205`: Invalid request format
- `209`: Not implemented

---

## Cross-Platform Differences

### Summary Table

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| **Window Capture** | BitBlt/WGC | Deprecated | Xcomposite/PipeWire |
| **Display Capture** | DXGI | Screen Capture | XSHM/PipeWire |
| **Game Capture** | D3D Shared Texture | N/A | N/A (3rd-party plugin) |
| **Audio Input** | WASAPI | Coreaudio | ALSA/PulseAudio |
| **Audio Output** | WASAPI | Coreaudio | ALSA/PulseAudio |
| **App Audio** | Windows 10+ | Limited | N/A |

### Windows Specifics

#### Capture Methods
- **BitBlt**: Legacy, slower, more compatible
- **Windows Graphics Capture (WGC)**: Modern, faster, Windows 10+
- **DXGI**: Display capture, most efficient
- **D3D11**: Game capture using shared textures

#### Window Identification
Windows uses this format for window identifiers:
```
[executable.exe]:Window Title
[chrome.exe]:Google Chrome
[game.exe]:Main Window
```

#### Multi-Monitor Support
- Each monitor gets its own Display Capture source
- Window Capture works across monitors
- Game Capture can follow game across monitors

#### GPU Acceleration
- Game Capture uses DirectX shared textures (GPU-accelerated)
- Display Capture uses DXGI (GPU-accelerated)
- Window Capture uses BitBlt or WGC (CPU/GPU hybrid)

### macOS Specifics

#### Performance Characteristics
- **Window Capture**: Poor performance (not recommended)
- **Display Capture**: Excellent performance (recommended)
- **Game Capture**: Not available

#### Screen Recording Permission
Requires user approval in:
```
System Preferences > Security & Privacy > Screen Recording
```

#### Window Capture Issues
- Window IDs change when applications restart
- Window Match Priority feature unavailable on Apple Silicon
- Unnamed windows may not be captured properly

#### Recommended Configuration
```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Scene 1",
    "inputName": "macOS Screen",
    "inputKind": "macos_screen_capture",
    "inputSettings": {
      "display": 0,
      "show_cursor": true,
      "capture_method": "display"
    }
  }
}
```

### Linux Specifics

#### X11 vs Wayland
- **X11 (XSHM/Xcomposite)**: Traditional, stable, deprecated
- **Wayland (PipeWire)**: Modern, recommended, actively developed
- **PipeWire**: Growing support, future-proof

#### Display Server Detection
Linux automatically detects the display server:
```bash
echo $XDG_SESSION_TYPE  # wayland or x11
```

#### Window Capture Cropping
Linux offers advanced cropping for performance:
```json
{
  "crop_top": 0,
  "crop_left": 0,
  "crop_right": 0,
  "crop_bottom": 0
}
```

#### Audio Capture Differences
```json
// ALSA (older systems)
{
  "device": "hw:0,0",
  "rate": 44100
}

// PulseAudio (modern systems)
{
  "device": "alsa_output.pci-0000_00_1f.3.analog-stereo",
  "rate": 48000
}
```

#### Game Capture on Linux
Native game capture is unavailable. Third-party option:
- **obs-vkcapture**: Vulkan/OpenGL game capture plugin
  - Installation: Manual plugin installation required
  - Usage: Environment variable injection (`LD_PRELOAD`)
  - Repository: https://github.com/nowrep/obs-vkcapture

### Platform-Specific Property Availability

#### Windows-Only Properties
- `capture_method` (BitBlt vs WGC)
- `client_area` (for WGC)
- `force_sdr` (for WGC)
- `use_device_timestamps` (for audio)
- `antiCheatCompatibility` (Game Capture)
- `useSLICrossfire` (Game Capture)

#### macOS-Only Properties
- `show_empty_names` (Window Capture)
- `show_shadow` (Window Capture)
- `capture_method` (Display, Application, Window)

#### Linux-Only Properties
- `crop_top`, `crop_left`, `crop_right`, `crop_bottom` (Xcomposite)
- `swap_redblue` (color channel swap)
- `lock_x` (X server locking)

---

## Implementation Guide

### Quick Start: Create a Multi-Source Stream Setup

#### Step 1: Connect to OBS WebSocket

```javascript
const WebSocket = require('ws');

const obs = new WebSocket('ws://localhost:4455');

obs.on('open', () => {
  console.log('OBS connected');
  setupSources();
});

function setupSources() {
  createWindowCapture();
  createDisplayCapture();
  createAudioInput();
  createAudioOutput();
}
```

#### Step 2: Create Window Capture

```javascript
function createWindowCapture() {
  const request = {
    requestType: "CreateInput",
    requestData: {
      sceneName: "Stream Scene",
      inputName: "Application Window",
      inputKind: "window_capture",
      inputSettings: {
        window: "[code.exe]:Visual Studio Code",
        capture_method: "auto",
        cursor: true
      }
    }
  };

  obs.send(JSON.stringify(request));
}
```

#### Step 3: Create Display Capture

```javascript
function createDisplayCapture() {
  const request = {
    requestType: "CreateInput",
    requestData: {
      sceneName: "Stream Scene",
      inputName: "Primary Monitor",
      inputKind: "monitor_capture",
      inputSettings: {
        monitor_id: "\\\\?\\DISPLAY#Default_Monitor#00000001",
        method: "dxgi",
        cursor: true
      }
    }
  };

  obs.send(JSON.stringify(request));
}
```

#### Step 4: Create Audio Sources

```javascript
function createAudioInput() {
  const request = {
    requestType: "CreateInput",
    requestData: {
      sceneName: "Stream Scene",
      inputName: "Microphone",
      inputKind: "wasapi_input_capture",
      inputSettings: {
        device_id: "{microphone_uuid}",
        use_device_timestamps: true
      }
    }
  };

  obs.send(JSON.stringify(request));
}

function createAudioOutput() {
  const request = {
    requestType: "CreateInput",
    requestData: {
      sceneName: "Stream Scene",
      inputName: "System Audio",
      inputKind: "wasapi_output_capture",
      inputSettings: {
        device_id: "{output_device_uuid}",
        use_device_timestamps: true
      }
    }
  };

  obs.send(JSON.stringify(request));
}
```

#### Step 5: Configure Audio Monitoring

```javascript
function configureAudioMonitoring() {
  // Set microphone monitoring
  obs.send(JSON.stringify({
    requestType: "SetInputAudioMonitorType",
    requestData: {
      inputName: "Microphone",
      monitorType: "monitorAndOutput"
    }
  }));

  // Set system audio to track 2
  obs.send(JSON.stringify({
    requestType: "SetInputAudioTracks",
    requestData: {
      inputName: "System Audio",
      audioTracks": 2  // Track 2 (bitmask)
    }
  }));
}
```

### Device ID Retrieval Guide

#### Windows - Find Device IDs

```json
{
  "requestType": "GetInputSettings",
  "requestData": {
    "inputName": "Existing Audio Source"
  }
}
```

Response contains the actual device UUID:
```json
{
  "inputSettings": {
    "device_id": "{0.0.0.00000000}.{UUID-HERE}"
  }
}
```

#### Windows - Find Monitor ID

1. Create a Display Capture source manually in OBS
2. Check OBS logs for monitor identifier
3. Query via API:

```json
{
  "requestType": "GetInputSettings",
  "requestData": {
    "inputName": "Primary Monitor"
  }
}
```

#### macOS - Find Audio Devices

```bash
# List audio devices
system_profiler SPAudioDataType

# Get device ID for OBS
# Format: device_uuid
```

#### Linux - Find ALSA Devices

```bash
# List ALSA devices
arecord -l
aplay -l

# Common format: hw:CARD,DEV
# Example: hw:0,0 or hw:Intel,0
```

#### Linux - Find PulseAudio Devices

```bash
# List PulseAudio devices
pactl list short sinks
pactl list short sources

# Get device names for OBS
# Format: device_name_or_uuid
```

### Troubleshooting Common Issues

#### Black Screen on Display/Window Capture

**Windows**:
```json
{
  "requestType": "SetInputSettings",
  "requestData": {
    "inputName": "Display Capture",
    "inputSettings": {
      "method": "wc"  // Try Windows Graphics Capture
    }
  }
}
```

**macOS**:
```json
{
  "requestType": "SetInputSettings",
  "requestData": {
    "inputName": "Screen Capture",
    "inputSettings": {
      "capture_method": "display"  // Use Display, not Application
    }
  }
}
```

#### Audio Echo (Same Device in Multiple Sources)

**Solution**: Use only one source per device, or disable monitoring:
```json
{
  "requestType": "SetInputAudioMonitorType",
  "requestData": {
    "inputName": "Microphone",
    "monitorType": "none"  // Disable monitoring
  }
}
```

#### Game Capture Not Working (Windows)

```json
{
  "requestType": "SetInputSettings",
  "requestData": {
    "inputName": "Game Capture",
    "inputSettings": {
      "antiCheatCompatibility": false,  // Disable if hanging
      "useSLICrossfire": true           // Enable for multi-GPU
    }
  }
}
```

---

## API Reference Summary

### Input Request Categories

| Category | Purpose |
|----------|---------|
| **CreateInput** | Create new capture source |
| **RemoveInput** | Delete input source |
| **GetInputList** | List all inputs |
| **GetInputKindList** | List available source types |
| **GetInputDefaultSettings** | Get default properties for source type |
| **GetInputSettings** | Retrieve current input properties |
| **SetInputSettings** | Modify input properties |
| **SetInputName** | Rename input |
| **GetInputMute** / **SetInputMute** | Control audio mute |
| **GetInputVolume** / **SetInputVolume** | Control audio level |
| **GetInputAudioBalance** / **SetInputAudioBalance** | Control stereo balance |
| **GetInputAudioSyncOffset** / **SetInputAudioSyncOffset** | Adjust audio timing |
| **GetInputAudioMonitorType** / **SetInputAudioMonitorType** | Configure monitoring |
| **GetInputAudioTracks** / **SetInputAudioTracks** | Assign audio tracks |

### Common Input Kinds (Source Types)

**Video Capture**:
- `window_capture` - Window capture (Windows/Linux)
- `monitor_capture` - Display capture (Windows/Linux)
- `dxgi_output_duplication` - Display capture (Windows, internal)
- `macos_screen_capture` - Display capture (macOS)
- `game_capture` - Game capture (Windows only)
- `dshow_input` - Video capture device (Windows)

**Audio Capture**:
- `wasapi_input_capture` - Microphone/Line-in (Windows)
- `wasapi_output_capture` - System audio/Headphones (Windows)
- `coreaudio_input_capture` - Audio input (macOS)
- `coreaudio_output_capture` - Audio output (macOS)
- `pulse_input_capture` - PulseAudio input (Linux)
- `pulse_output_capture` - PulseAudio output (Linux)
- `alsa_input_capture` - ALSA input (Linux)
- `alsa_output_capture` - ALSA output (Linux)

**Media**:
- `ffmpeg_source` - Video file playback
- `image_source` - Static image display
- `slideshow` - Image sequence

**Graphics**:
- `color_source` - Solid color background
- `browser_source` - Web browser content
- `text_gdiplus` - Text overlay (Windows)
- `text_ft2_source` - Text overlay (Linux/macOS)

---

## Conclusion

This research provides comprehensive documentation for OBS Studio capture sources, enabling programmatic control through the WebSocket API with platform-specific implementation details. The information covers:

- **5 primary capture source types**: Window, Display, Game, Audio Input, Audio Output
- **3 major platforms**: Windows, macOS, Linux
- **Complete API integration examples**: WebSocket requests, property management, error handling
- **Platform-specific differences**: Capture methods, device identification, performance characteristics

This documentation supports the Master Integration Sprint Session 3 objectives for advanced OBS integration capabilities.

---

**Document Version**: 1.0
**Last Updated**: November 12, 2025
**Research Completeness**: 100% (All requested topics covered)
