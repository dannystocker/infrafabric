# OBS Studio Media Integration Module
## Production-Ready Integration Guide

**Module**: `src/integrations/obs_media.py`
**Protocol**: obs-websocket 5.0+
**Author**: InfraFabric Project
**License**: CC BY 4.0
**Last Updated**: 2025-11-12

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Media Source Control](#media-source-control)
6. [Browser Source Control](#browser-source-control)
7. [Capture Source Control](#capture-source-control)
8. [WebSocket API](#websocket-api)
9. [IF.witness Audit Logging](#ifwitness-audit-logging)
10. [Platform-Specific Notes](#platform-specific-notes)
11. [Error Handling](#error-handling)
12. [Complete Examples](#complete-examples)
13. [API Reference](#api-reference)

---

## Overview

The OBS Media Integration Module provides production-ready control of OBS Studio via the obs-websocket 5.0+ protocol. It enables programmatic management of:

- **Media Sources**: Video/audio file playback, image display, slideshows
- **Browser Sources**: Web-based overlays with CEF (Chromium Embedded Framework)
- **Capture Sources**: Window, display, game, and audio capture (platform-aware)
- **Playback Control**: Play, pause, stop, restart, seek, next/previous
- **Real-Time Events**: Subscribe to OBS state changes
- **Audit Logging**: Complete IF.witness trail for compliance

### Key Features

✓ **SHA-256 Authentication** - Secure WebSocket connection
✓ **Event-Driven Architecture** - Real-time OBS state updates
✓ **Platform-Aware** - Windows, macOS, Linux support
✓ **IF.witness Integration** - Full audit trail
✓ **Type Hints** - Complete type safety
✓ **Comprehensive Error Handling** - Production-ready reliability
✓ **Context Manager Support** - Automatic connection management

### Supported Formats

**Video**: H.264, H.265, VP9, AV1 (OBS 29+), MP4, MKV, MOV, WebM
**Audio**: MP3, AAC, OGG, WAV, FLAC, OPUS
**Images**: PNG, JPEG, BMP, TGA, GIF (animated)
**Streams**: RTMP, RTSP, HTTP/HLS

---

## Installation

### Prerequisites

1. **OBS Studio 28+** with obs-websocket 5.0+ enabled
2. **Python 3.8+**
3. **websocket-client** library

### Install Dependencies

```bash
pip install websocket-client>=1.0.0
```

### OBS Configuration

1. Open OBS Studio
2. Navigate to **Tools** → **WebSocket Server Settings**
3. Enable "Enable WebSocket server"
4. Set port to **4455** (default)
5. (Optional) Set authentication password
6. Click "Apply"

### Import Module

```python
from src.integrations.obs_media import (
    OBSMediaManager,
    MediaSourceConfig,
    BrowserSourceConfig,
    CaptureSourceConfig,
    MediaAction,
    Platform
)
```

---

## Quick Start

### Basic Usage

```python
from src.integrations.obs_media import OBSMediaManager, MediaSourceConfig, MediaAction

# Connect to OBS
manager = OBSMediaManager(host="localhost", port=4455, password="your_password")
manager.connect()

# Create video source
config = MediaSourceConfig(
    local_file="/videos/intro.mp4",
    looping=True,
    restart_on_activate=True
)
manager.media.create_media_source("MainScene", "IntroVideo", config)

# Control playback
manager.media.trigger_media_action("IntroVideo", MediaAction.PLAY)

# Get status
status = manager.media.get_media_status("IntroVideo")
print(f"Duration: {status['mediaDuration']}ms")
print(f"Position: {status['mediaCursor']}ms")

# Disconnect
manager.disconnect()
```

### Context Manager Usage (Recommended)

```python
from src.integrations.obs_media import OBSMediaManager, MediaSourceConfig

with OBSMediaManager(host="localhost", port=4455) as manager:
    config = MediaSourceConfig(local_file="/videos/intro.mp4", looping=True)
    manager.media.create_media_source("MainScene", "IntroVideo", config)
    manager.media.trigger_media_action("IntroVideo", MediaAction.PLAY)
# Auto-disconnect on exit
```

---

## Architecture

### Component Hierarchy

```
OBSMediaManager (High-level interface)
├── OBSWebSocketClient (WebSocket communication)
│   ├── SHA-256 Authentication
│   ├── Request/Response Pattern
│   ├── Event Subscription
│   └── IF.witness Logging
├── MediaSourceController (Media sources)
│   ├── ffmpeg_source (video/audio)
│   ├── image_source (static images)
│   ├── slideshow (image sequences)
│   └── vlc_source (playlists)
├── BrowserSourceController (Browser sources)
│   ├── CEF (Chromium Embedded Framework)
│   ├── URL loading
│   └── Custom CSS/JavaScript
└── CaptureSourceController (Capture sources)
    ├── Window Capture
    ├── Display Capture
    ├── Game Capture (Windows only)
    └── Audio Capture
```

### Data Flow

```
Application Code
    ↓
OBSMediaManager
    ↓
Controller (Media/Browser/Capture)
    ↓
OBSWebSocketClient
    ↓ (Request OpCode 6)
OBS Studio (obs-websocket)
    ↓ (Response OpCode 7)
OBSWebSocketClient
    ↓
IF.witness Log
    ↓
Application Code
```

---

## Media Source Control

### Video/Audio Playback (ffmpeg_source)

#### Create Media Source

```python
from src.integrations.obs_media import MediaSourceConfig

config = MediaSourceConfig(
    local_file="/path/to/video.mp4",
    looping=True,                    # Auto-restart on end
    restart_on_activate=True,        # Restart when scene becomes active
    clear_on_media_end=False,        # Don't hide on end
    speed_percent=100,               # Normal speed (1%-200%)
    is_local_file=True,              # Local file (False for streams)
    buffering_mb=2,                  # Buffer size
    reconnect_delay_sec=10           # Reconnect delay for streams
)

result = manager.media.create_media_source("MainScene", "IntroVideo", config)
print(f"Created input UUID: {result['inputUuid']}")
```

#### Remote Stream Source

```python
config = MediaSourceConfig(
    local_file="rtmp://stream.example.com/live/stream1",
    is_local_file=False,             # Remote stream
    reconnect_delay_sec=5,           # Auto-reconnect on disconnect
    buffering_mb=4                   # Larger buffer for streaming
)

manager.media.create_media_source("StreamScene", "LiveFeed", config)
```

#### Playback Control

```python
from src.integrations.obs_media import MediaAction

# Play
manager.media.trigger_media_action("IntroVideo", MediaAction.PLAY)

# Pause
manager.media.trigger_media_action("IntroVideo", MediaAction.PAUSE)

# Stop (reset to beginning)
manager.media.trigger_media_action("IntroVideo", MediaAction.STOP)

# Restart from beginning
manager.media.trigger_media_action("IntroVideo", MediaAction.RESTART)

# Next (for playlists/slideshows)
manager.media.trigger_media_action("IntroVideo", MediaAction.NEXT)

# Previous (for playlists/slideshows)
manager.media.trigger_media_action("IntroVideo", MediaAction.PREVIOUS)
```

#### Media Position Control

```python
# Jump to 30 seconds
manager.media.set_media_cursor("IntroVideo", 30000)  # milliseconds

# Get current status
status = manager.media.get_media_status("IntroVideo")
print(f"Duration: {status['mediaDuration']}ms")
print(f"Current Position: {status['mediaCursor']}ms")
print(f"State: {status['mediaState']}")
# States: OBS_MEDIA_STATE_PLAYING, OBS_MEDIA_STATE_PAUSED, etc.
```

### Image Sources

#### Static Image Display

```python
manager.media.create_image_source(
    scene_name="OverlayScene",
    input_name="Logo",
    file_path="/images/logo.png",
    unload=False  # Keep loaded when hidden
)
```

### Slideshow Sources

#### Image Sequence

```python
files = [
    "/images/slide1.png",
    "/images/slide2.png",
    "/images/slide3.png",
    "/images/slide4.png"
]

manager.media.create_slideshow(
    scene_name="GalleryScene",
    input_name="PhotoSlideshow",
    files=files,
    slide_time=5000,         # 5 seconds per slide
    transition="fade",       # Transition effect
    transition_speed=700,    # 700ms transition
    loop=True,              # Loop slideshow
    randomize=False         # Sequential order
)

# Manual control
manager.media.trigger_media_action("PhotoSlideshow", MediaAction.NEXT)
manager.media.trigger_media_action("PhotoSlideshow", MediaAction.PREVIOUS)
```

---

## Browser Source Control

### Web-Based Overlays (CEF)

#### External URL

```python
from src.integrations.obs_media import BrowserSourceConfig

config = BrowserSourceConfig(
    url="https://example.com/overlay.html",
    width=1920,
    height=1080,
    fps=30,                          # Frame rate
    css="body { background: transparent; }",  # Custom CSS
    is_local_file=False,
    shutdown=False,                  # Keep running when hidden
    refresh_on_scene_show=False      # Don't refresh on scene change
)

manager.browser.create_browser_source("MainScene", "WebOverlay", config)
```

#### Local HTML File

```python
config = BrowserSourceConfig(
    url="file:///C:/overlays/timer.html",  # Windows
    # url="file:///home/user/overlays/timer.html",  # Linux
    # url="file:///Users/user/overlays/timer.html",  # macOS
    width=800,
    height=600,
    is_local_file=True
)

manager.browser.create_browser_source("TimerScene", "CountdownTimer", config)
```

#### Inline HTML (Data URI)

```python
html_content = """
<html>
<head>
    <style>
        body {
            background: transparent;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        h1 {
            font-size: 72px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }
    </style>
</head>
<body>
    <h1>LIVE</h1>
</body>
</html>
"""

config = BrowserSourceConfig(
    url=f"data:text/html,{html_content}",
    width=800,
    height=200
)

manager.browser.create_browser_source("AlertScene", "LiveIndicator", config)
```

#### Custom CSS Injection

```python
config = BrowserSourceConfig(
    url="https://www.twitch.tv/embed/channelname/chat",
    width=400,
    height=720,
    css="""
        /* Hide specific elements */
        .chat-header { display: none; }

        /* Custom styling */
        .chat-line {
            background: rgba(0,0,0,0.7) !important;
            color: #00ff00 !important;
        }

        /* Add shadow */
        * { text-shadow: 1px 1px 2px rgba(0,0,0,0.8); }
    """
)

manager.browser.create_browser_source("ChatScene", "TwitchChat", config)
```

#### Refresh Browser Source

```python
# Force refresh (cache-busting)
manager.browser.refresh_browser_source("WebOverlay")
```

### JavaScript API Access

Browser sources have access to `window.obsstudio` JavaScript API with methods like:

- `getStatus()` - Get OBS streaming/recording status
- `getCurrentScene()` - Get active scene name
- `setCurrentScene(name)` - Switch scenes
- `startStreaming()` / `stopStreaming()`
- `startRecording()` / `stopRecording()`
- Event listeners: `obsSceneChanged`, `obsStreamingStarted`, etc.

**Example HTML with OBS API**:

```html
<!DOCTYPE html>
<html>
<body>
    <h1 id="status">Offline</h1>
    <script>
        if (typeof window.obsstudio !== 'undefined') {
            window.addEventListener('obsStreamingStarted', function() {
                document.getElementById('status').textContent = 'LIVE';
            });

            window.addEventListener('obsStreamingStopped', function() {
                document.getElementById('status').textContent = 'Offline';
            });
        }
    </script>
</body>
</html>
```

---

## Capture Source Control

### Window Capture

#### Windows Platform

```python
from src.integrations.obs_media import CaptureSourceConfig, Platform

# Initialize with platform
manager = OBSMediaManager(platform=Platform.WINDOWS)
manager.connect()

config = CaptureSourceConfig(
    window="[chrome.exe]:Google Chrome",  # [executable]:Window Title
    capture_method="auto",                # auto|bitblt|wgc
    client_area=False,                    # Capture entire window
    cursor=True                           # Show mouse cursor
)

manager.capture.create_window_capture("MainScene", "BrowserWindow", config)
```

#### Linux Platform

```python
manager = OBSMediaManager(platform=Platform.LINUX)
manager.connect()

config = CaptureSourceConfig(
    window="window_id",  # X11 window ID
    cursor=True
)

manager.capture.create_window_capture("MainScene", "AppWindow", config)
```

### Display Capture

#### Full Monitor Capture

```python
config = CaptureSourceConfig(
    monitor_id="\\\\?\\DISPLAY#Default_Monitor#00000001",  # Windows
    cursor=True
)

manager.capture.create_display_capture("DesktopScene", "PrimaryMonitor", config)
```

#### macOS Display Capture

```python
manager = OBSMediaManager(platform=Platform.MACOS)
manager.connect()

config = CaptureSourceConfig(
    display=0,        # Display index (0 = primary)
    cursor=True
)

manager.capture.create_display_capture("DesktopScene", "MainDisplay", config)
```

### Game Capture (Windows Only)

#### Automatic Fullscreen Detection

```python
config = CaptureSourceConfig(
    capture_mode="auto",              # Capture any fullscreen game
    antiCheatCompatibility=True,      # Anti-cheat support
    allowTransparency=False,          # Opaque background
    limitFramerate=False,             # Don't limit FPS
    captureOverlays=False,            # Don't capture overlays
    cursor=True
)

manager.capture.create_game_capture("GamingScene", "GameCapture", config)
```

#### Specific Window Capture

```python
config = CaptureSourceConfig(
    capture_mode="window",
    window="[Game.exe]:Game Window Title",
    antiCheatCompatibility=True,
    limitFramerate=True,              # Match OBS FPS
    cursor=False
)

manager.capture.create_game_capture("GamingScene", "SpecificGame", config)
```

### Audio Capture

#### Microphone Input

```python
# Get device ID from OBS or system
device_id = "{0.0.0.00000000}.{UUID-of-microphone}"

manager.capture.create_audio_input(
    scene_name="StreamScene",
    input_name="Microphone",
    device_id=device_id
)
```

#### System Audio Output

```python
device_id = "{0.0.0.00000000}.{UUID-of-output-device}"

manager.capture.create_audio_output(
    scene_name="StreamScene",
    input_name="SystemAudio",
    device_id=device_id
)
```

---

## WebSocket API

### Connection Management

#### Manual Connection

```python
from src.integrations.obs_media import OBSWebSocketClient

client = OBSWebSocketClient(
    host="localhost",
    port=4455,
    password="your_password",
    enable_witness=True
)

# Connect
if client.connect():
    print("Connected to OBS")
else:
    print("Connection failed")

# Use client...

# Disconnect
client.disconnect()
```

#### Authentication Flow

The module automatically handles SHA-256 challenge/response authentication:

1. Client sends connection request
2. OBS sends Hello message with challenge/salt
3. Client computes: `auth_response = base64(SHA256(base64(SHA256(password + salt)) + challenge))`
4. Client sends Identify message with auth_response
5. OBS sends Identified message on success

### Event Subscription

#### Register Event Handlers

```python
def on_media_ended(event_data):
    print(f"Media ended: {event_data['inputName']}")
    # Restart or switch to next source

client.on_event("MediaInputPlaybackEnded", on_media_ended)

def on_scene_changed(event_data):
    print(f"Scene changed to: {event_data['sceneName']}")

client.on_event("CurrentProgramSceneChanged", on_scene_changed)
```

#### Available Events

- `MediaInputPlaybackStarted` - Media playback started
- `MediaInputPlaybackEnded` - Media playback ended
- `MediaInputActionTriggered` - Media action triggered
- `CurrentProgramSceneChanged` - Active scene changed
- `SceneItemEnableStateChanged` - Source visibility changed
- `StreamStateChanged` - Streaming state changed
- `RecordStateChanged` - Recording state changed

### Low-Level Request API

```python
# Send custom request
response = client.request("GetSceneList")
scenes = response["scenes"]

for scene in scenes:
    print(f"Scene: {scene['sceneName']}")
```

---

## IF.witness Audit Logging

### Automatic Logging

All operations are automatically logged to IF.witness when `enable_witness=True` (default):

```python
manager = OBSMediaManager(enable_witness=True)
manager.connect()

# All operations logged automatically
manager.media.create_media_source("Scene", "Video", config)
manager.media.trigger_media_action("Video", MediaAction.PLAY)
```

### Retrieve Audit Logs

```python
# Get all logs
logs = manager.client.get_witness_logs()

for log in logs:
    print(f"[{log['timestamp']}] {log['operation']}: {log['input_name']} - Success: {log['success']}")
    if log['error_message']:
        print(f"  Error: {log['error_message']}")
```

### Export Audit Logs

```python
# Export to JSON file
manager.client.export_witness_logs("/logs/obs_audit_2025-11-12.json")
```

### Log Entry Structure

```python
{
    "event_id": "uuid-here",
    "timestamp": "2025-11-12T10:30:45.123456+00:00",
    "operation": "CREATE_MEDIA_SOURCE",
    "input_name": "IntroVideo",
    "input_type": "ffmpeg_source",
    "details": {
        "scene": "MainScene",
        "file": "/videos/intro.mp4"
    },
    "success": true,
    "error_message": null
}
```

### Philosophy Grounding

IF.witness logging embodies:

- **IF.TTT** (Traceable, Transparent, Trustworthy): Full audit trail
- **Ubuntu**: Collective accountability in collaborative streaming
- **Kantian Duty**: Respect for user agency through transparency

---

## Platform-Specific Notes

### Windows

**Capture Methods**:
- **BitBlt**: Legacy, compatible with most apps
- **Windows Graphics Capture (WGC)**: Modern, Windows 10+, captures UWP apps
- **DXGI**: Display capture, GPU-accelerated

**Window Format**: `[executable.exe]:Window Title`

**Game Capture**: D3D11 shared texture capture (most efficient)

### macOS

**Screen Recording Permission**: Required in System Preferences → Security & Privacy → Screen Recording

**Recommended**: Use Display Capture instead of Window Capture for better performance

**Window Capture**: Deprecated on macOS 13.0+, poor performance

### Linux

**Display Servers**:
- **X11**: Xcomposite window capture, XSHM display capture
- **Wayland**: PipeWire capture (modern, recommended)

**Audio**: ALSA or PulseAudio

**Game Capture**: Not natively supported (use obs-vkcapture plugin for Vulkan/OpenGL games)

---

## Error Handling

### Connection Errors

```python
try:
    manager = OBSMediaManager(host="localhost", port=4455, password="wrong_password")
    if not manager.connect():
        print("Failed to connect to OBS")
        # Handle connection failure
except Exception as e:
    print(f"Connection error: {e}")
```

### Request Errors

```python
try:
    config = MediaSourceConfig(local_file="/nonexistent/file.mp4")
    manager.media.create_media_source("Scene", "Video", config)
except Exception as e:
    print(f"Failed to create source: {e}")
    # Check IF.witness logs for details
    logs = manager.client.get_witness_logs()
    failed_log = [log for log in logs if not log['success']][-1]
    print(f"Error details: {failed_log['error_message']}")
```

### Platform Validation

```python
from src.integrations.obs_media import Platform

try:
    # This will raise exception on non-Windows platforms
    manager = OBSMediaManager(platform=Platform.LINUX)
    manager.connect()

    config = CaptureSourceConfig(capture_mode="auto")
    manager.capture.create_game_capture("Scene", "Game", config)
except Exception as e:
    print(f"Game capture error: {e}")
    # "Game capture is only available on Windows"
```

---

## Complete Examples

### Example 1: Streaming Setup with Multiple Sources

```python
from src.integrations.obs_media import (
    OBSMediaManager, MediaSourceConfig, BrowserSourceConfig,
    CaptureSourceConfig, Platform, MediaAction
)

with OBSMediaManager(host="localhost", port=4455, platform=Platform.WINDOWS) as manager:
    # Create video intro
    intro_config = MediaSourceConfig(
        local_file="C:/videos/stream_intro.mp4",
        looping=False,
        restart_on_activate=True
    )
    manager.media.create_media_source("IntroScene", "IntroVideo", intro_config)

    # Create background music
    music_config = MediaSourceConfig(
        local_file="C:/music/background.mp3",
        looping=True
    )
    manager.media.create_media_source("MainScene", "BackgroundMusic", music_config)

    # Create browser overlay
    overlay_config = BrowserSourceConfig(
        url="https://streamelements.com/overlay/OVERLAY_ID",
        width=1920,
        height=1080
    )
    manager.browser.create_browser_source("MainScene", "Alerts", overlay_config)

    # Create game capture
    game_config = CaptureSourceConfig(
        capture_mode="auto",
        antiCheatCompatibility=True,
        cursor=False
    )
    manager.capture.create_game_capture("GameScene", "GameCapture", game_config)

    # Create microphone
    manager.capture.create_audio_input(
        "MainScene",
        "Microphone",
        "{0.0.0.00000000}.{mic-uuid}"
    )

    # Play intro
    manager.media.trigger_media_action("IntroVideo", MediaAction.PLAY)

    # Export audit log
    manager.client.export_witness_logs("/logs/stream_setup.json")
```

### Example 2: Slideshow with Event Handling

```python
import time
from src.integrations.obs_media import OBSMediaManager, MediaAction

def on_slideshow_ended(event_data):
    print("Slideshow completed, restarting...")
    manager.media.trigger_media_action("PhotoShow", MediaAction.RESTART)

manager = OBSMediaManager()
manager.connect()

# Register event handler
manager.client.on_event("MediaInputPlaybackEnded", on_slideshow_ended)

# Create slideshow
files = [f"/images/photo{i}.jpg" for i in range(1, 11)]
manager.media.create_slideshow(
    "GalleryScene",
    "PhotoShow",
    files,
    slide_time=3000,
    loop=False  # Will trigger ended event
)

# Start slideshow
manager.media.trigger_media_action("PhotoShow", MediaAction.PLAY)

# Keep running to receive events
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    manager.disconnect()
```

### Example 3: Dynamic Overlay Update

```python
from src.integrations.obs_media import OBSMediaManager, BrowserSourceConfig

manager = OBSMediaManager()
manager.connect()

# Create initial overlay
config = BrowserSourceConfig(
    url="http://localhost:8000/overlay.html",
    width=1920,
    height=1080
)
manager.browser.create_browser_source("MainScene", "DynamicOverlay", config)

# Update overlay content (server-side)
# Your web server updates overlay.html

# Force refresh browser source
manager.browser.refresh_browser_source("DynamicOverlay")

manager.disconnect()
```

---

## API Reference

### Classes

#### OBSMediaManager

High-level interface for OBS integration.

**Constructor**:
```python
OBSMediaManager(
    host: str = "localhost",
    port: int = 4455,
    password: Optional[str] = None,
    platform: Platform = Platform.WINDOWS,
    enable_witness: bool = True
)
```

**Attributes**:
- `client: OBSWebSocketClient` - WebSocket client
- `media: MediaSourceController` - Media source controller
- `browser: BrowserSourceController` - Browser source controller
- `capture: CaptureSourceController` - Capture source controller

**Methods**:
- `connect() -> bool` - Connect to OBS
- `disconnect() -> None` - Disconnect from OBS

---

#### OBSWebSocketClient

Low-level WebSocket client.

**Constructor**:
```python
OBSWebSocketClient(
    host: str = "localhost",
    port: int = 4455,
    password: Optional[str] = None,
    enable_witness: bool = True
)
```

**Methods**:
- `connect() -> bool` - Connect and authenticate
- `disconnect() -> None` - Close connection
- `request(request_type: str, request_data: Dict) -> Dict` - Send request
- `on_event(event_type: str, handler: Callable) -> None` - Register event handler
- `get_witness_logs() -> List[Dict]` - Get audit logs
- `export_witness_logs(file_path: str) -> None` - Export logs to JSON

---

#### MediaSourceController

Controller for media sources.

**Methods**:
- `create_media_source(scene_name, input_name, config: MediaSourceConfig) -> Dict`
- `create_image_source(scene_name, input_name, file_path, unload) -> Dict`
- `create_slideshow(scene_name, input_name, files, ...) -> Dict`
- `trigger_media_action(input_name, action: MediaAction) -> Dict`
- `get_media_status(input_name) -> Dict`
- `set_media_cursor(input_name, position_ms) -> Dict`

---

#### BrowserSourceController

Controller for browser sources.

**Methods**:
- `create_browser_source(scene_name, input_name, config: BrowserSourceConfig) -> Dict`
- `refresh_browser_source(input_name) -> None`

---

#### CaptureSourceController

Controller for capture sources.

**Constructor**:
```python
CaptureSourceController(
    client: OBSWebSocketClient,
    platform: Platform = Platform.WINDOWS
)
```

**Methods**:
- `create_window_capture(scene_name, input_name, config: CaptureSourceConfig) -> Dict`
- `create_display_capture(scene_name, input_name, config: CaptureSourceConfig) -> Dict`
- `create_game_capture(scene_name, input_name, config: CaptureSourceConfig) -> Dict` (Windows only)
- `create_audio_input(scene_name, input_name, device_id) -> Dict`
- `create_audio_output(scene_name, input_name, device_id) -> Dict`

---

### Data Classes

#### MediaSourceConfig

Configuration for media sources.

**Attributes**:
- `local_file: str` - File path or stream URL
- `looping: bool = False` - Loop playback
- `restart_on_activate: bool = True` - Restart when scene becomes active
- `clear_on_media_end: bool = False` - Hide when playback ends
- `speed_percent: int = 100` - Playback speed (1-200%)
- `is_local_file: bool = True` - Local file vs remote stream
- `buffering_mb: int = 2` - Buffer size in MB
- `reconnect_delay_sec: int = 10` - Reconnect delay for streams

---

#### BrowserSourceConfig

Configuration for browser sources.

**Attributes**:
- `url: str` - URL or data URI
- `width: int = 1920` - Source width
- `height: int = 1080` - Source height
- `fps: int = 30` - Frame rate
- `css: str = ""` - Custom CSS
- `is_local_file: bool = False` - Local HTML file
- `shutdown: bool = False` - Shutdown when hidden
- `refresh_on_scene_show: bool = False` - Refresh on scene activation

---

#### CaptureSourceConfig

Configuration for capture sources.

**Attributes**:
- `cursor: bool = True` - Show mouse cursor
- `window: Optional[str] = None` - Window identifier
- `capture_method: str = "auto"` - Capture method (auto|bitblt|wgc)
- `client_area: bool = False` - Capture client area only
- `monitor_id: Optional[str] = None` - Monitor identifier
- `display: int = 0` - Display index
- `capture_mode: str = "auto"` - Game capture mode
- `antiCheatCompatibility: bool = True` - Anti-cheat support
- `allowTransparency: bool = False` - Allow transparency
- `limitFramerate: bool = False` - Limit to OBS FPS
- `captureOverlays: bool = False` - Capture game overlays
- `device_id: Optional[str] = None` - Audio device ID
- `use_device_timestamps: bool = True` - Use device timestamps

---

### Enums

#### MediaAction

Playback actions for media sources.

Values: `PLAY`, `PAUSE`, `STOP`, `RESTART`, `NEXT`, `PREVIOUS`

#### Platform

Operating system platforms.

Values: `WINDOWS`, `MACOS`, `LINUX`

#### MediaInputType

OBS input types.

Values: `FFMPEG_SOURCE`, `IMAGE_SOURCE`, `SLIDESHOW`, `VLC_SOURCE`, `BROWSER_SOURCE`, `WINDOW_CAPTURE`, `MONITOR_CAPTURE`, `GAME_CAPTURE`, `WASAPI_INPUT`, `WASAPI_OUTPUT`

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to OBS
**Solution**: Verify OBS WebSocket server is enabled in Tools → WebSocket Server Settings

**Problem**: Authentication failed
**Solution**: Ensure password matches OBS WebSocket settings

### Black Screen Captures

**Problem**: Window capture shows black screen
**Solution**: Try different capture method (BitBlt vs WGC on Windows)

**Problem**: Game capture shows black screen
**Solution**: Ensure game uses DirectX/OpenGL, disable anti-cheat compatibility if needed

### Audio Echo

**Problem**: Audio feedback/echo
**Solution**: Don't capture the same audio device in both global settings and scene sources

### Performance Issues

**Problem**: High CPU usage with browser sources
**Solution**: Lower FPS, enable "shutdown when hidden", reduce browser source resolution

---

## References

- **OBS WebSocket Protocol**: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
- **OBS Studio Docs**: https://docs.obsproject.com/
- **websocket-client**: https://pypi.org/project/websocket-client/
- **InfraFabric Project**: https://github.com/infrafabric

---

## License

CC BY 4.0 - Creative Commons Attribution 4.0 International

---

**End of Documentation**
