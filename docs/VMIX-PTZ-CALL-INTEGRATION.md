# vMix PTZ and Call Control Integration

**Module**: `src/integrations/vmix_ptz_call.py`
**Version**: 1.0.0
**Author**: InfraFabric Project - Agent 4 (vMix Integration Sprint)
**License**: CC BY 4.0
**Last Updated**: 2025-11-12

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [PTZ Camera Control](#ptz-camera-control)
6. [vMix Call Control](#vmix-call-control)
7. [Input Switching](#input-switching)
8. [IF.witness Audit Logging](#ifwitness-audit-logging)
9. [Error Handling](#error-handling)
10. [API Reference](#api-reference)
11. [Production Examples](#production-examples)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The vMix PTZ and Call Control Integration module provides a production-ready Python interface for controlling vMix streaming software via its HTTP API. This module enables automated control of PTZ cameras, vMix Call (WebRTC) audio/video routing, and input switching with comprehensive audit logging.

### Architecture

```
┌─────────────────────────────────────────────────┐
│          VMixController (Main API)              │
├─────────────────────────────────────────────────┤
│  • PTZ Control (position, continuous movement)  │
│  • Call Control (audio/video routing)           │
│  • Input Switching (transitions, preview)       │
└──────────────┬──────────────────────────────────┘
               │
               ├─► VMixHTTPClient (HTTP + Retry)
               ├─► VMixWitnessLogger (Audit Trail)
               └─► vMix HTTP API (Port 8088)
```

### Philosophy Grounding

- **IF.TTT**: Traceable, Transparent, Trustworthy operations
- **Ubuntu**: Communal production workflows for collaborative content creation
- **Kantian Duty**: Integrity in command execution with audit trails

---

## Features

### ✅ PTZ Camera Control
- **Absolute Positioning**: SetPanX, SetPanY, SetZoom (-2 to 2 range for pan, 0 to 5 for zoom)
- **Continuous Movement**: PTZMoveUp/Down/Left/Right with speed control (0-1)
- **Zoom Control**: PTZZoomIn/Out with speed control
- **Movement Stop**: PTZMoveStop for all movements
- **Preset Support**: Position storage via Virtual Inputs

### ✅ vMix Call Control (WebRTC)
- **Audio Routing**: Master, Headphones, Bus A-G (9 options)
- **Video Routing**: Output 1-4, None
- **Auto Mix-Minus**: Automatic echo prevention
- **Call State Management**: Connection state tracking

### ✅ Input Control & Switching
- **Transitions**: Cut, CutDirect, Fade, Slide, Push, Zoom
- **Duration Control**: Configurable transition duration (milliseconds)
- **Preview Mode**: PreviewInput for safe switching
- **Multi-Mix Support**: Main mix + secondary mixes (4K/Pro editions)

### ✅ Production-Ready Features
- **IF.witness Logging**: SHA-256 hashed audit trail
- **Retry Logic**: Exponential backoff for network failures
- **Error Handling**: Comprehensive exception handling
- **Type Safety**: Full type hints throughout
- **Context Manager**: Automatic resource cleanup

---

## Installation

### Requirements

```bash
pip install requests  # HTTP client library
```

### Module Import

```python
from src.integrations.vmix_ptz_call import (
    VMixController,
    PTZPosition,
    TransitionType,
    AudioSource,
    VideoSource,
    create_vmix_controller
)
```

---

## Quick Start

### Basic Usage

```python
from pathlib import Path
from src.integrations.vmix_ptz_call import VMixController, PTZPosition

# Create controller with audit logging
controller = VMixController(
    base_url="http://127.0.0.1:8088/API/",
    witness_log_dir=Path("./witness_logs")
)

# Set PTZ camera position
position = PTZPosition(pan_x=1.0, pan_y=-0.5, zoom=2.0)
response = controller.set_ptz_position(input_ref=1, position=position)

if response.success:
    print("PTZ position set successfully!")

# Clean up
controller.close()
```

### Context Manager (Recommended)

```python
from src.integrations.vmix_ptz_call import create_vmix_controller
from pathlib import Path

# Automatic resource cleanup
with create_vmix_controller(witness_log_dir=Path("./witness")) as vmix:
    # Set camera position
    position = PTZPosition(pan_x=0, pan_y=0, zoom=1.5)
    vmix.set_ptz_position(input_ref=1, position=position)

    # Switch input with fade
    from integrations.vmix_ptz_call import TransitionType
    vmix.switch_input(
        input_ref=2,
        transition=TransitionType.FADE,
        duration=1000
    )
```

---

## PTZ Camera Control

### Absolute Positioning

```python
from src.integrations.vmix_ptz_call import PTZPosition

# Define camera position
position = PTZPosition(
    pan_x=1.5,   # Range: -2 (left) to 2 (right)
    pan_y=-1.0,  # Range: -2 (bottom) to 2 (top)
    zoom=2.5     # Range: 0 to 5 (zoom level)
)

# Move camera to position
response = controller.set_ptz_position(
    input_ref=1,        # Camera input number
    position=position,
    duration=500        # Optional: transition duration in ms
)
```

### Continuous Movement

```python
# Start moving camera up at 80% speed
controller.ptz_move_continuous(
    input_ref=1,
    direction="up",   # "up", "down", "left", "right", "zoom_in", "zoom_out"
    speed=0.8         # Range: 0.0 to 1.0
)

# Move for desired duration (controlled externally)
import time
time.sleep(2)

# Stop movement
controller.ptz_stop(input_ref=1)
```

### PTZ Preset Workflow

```python
# Preset 1: Wide Shot
wide_shot = PTZPosition(pan_x=0, pan_y=0, zoom=1.0)
controller.set_ptz_position(input_ref=1, position=wide_shot)

# Preset 2: Close-Up
close_up = PTZPosition(pan_x=1.5, pan_y=0.5, zoom=3.0)
controller.set_ptz_position(input_ref=1, position=close_up)

# Preset 3: Over-The-Shoulder
ots = PTZPosition(pan_x=-1.2, pan_y=0.8, zoom=2.0)
controller.set_ptz_position(input_ref=1, position=ots, duration=1000)
```

### Supported PTZ Protocols

The module works with all vMix-supported PTZ cameras:

- **VISCA over IP**: Sony SRG series
- **VISCA over UDP**: PTZ Optics, ValueHD
- **Panasonic CGI**: AW-HE series
- **UVC PTZ**: USB cameras with PTZ support
- **Virtual PTZ**: Digital pan/tilt/zoom on any input

---

## vMix Call Control

### Audio Routing

```python
from src.integrations.vmix_ptz_call import AudioSource

# Send Master mix to guest (default)
controller.set_call_audio_source(
    input_ref=2,  # vMix Call input number
    audio_source=AudioSource.MASTER
)

# Send Bus A to guest (virtual green room)
controller.set_call_audio_source(
    input_ref=2,
    audio_source=AudioSource.BUS_A
)

# Available audio sources:
# - AudioSource.MASTER
# - AudioSource.HEADPHONES
# - AudioSource.BUS_A through AudioSource.BUS_G
```

### Video Routing

```python
from src.integrations.vmix_ptz_call import VideoSource

# Send Output 1 to guest
controller.set_call_video_source(
    input_ref=2,
    video_source=VideoSource.OUTPUT1
)

# Send no video (audio only)
controller.set_call_video_source(
    input_ref=2,
    video_source=VideoSource.NONE
)

# Available video sources:
# - VideoSource.OUTPUT1 through VideoSource.OUTPUT4
# - VideoSource.NONE
```

### Production Call Workflow

```python
from src.integrations.vmix_ptz_call import AudioSource, VideoSource

# Guest waiting in virtual green room
controller.set_call_audio_source(input_ref=2, audio_source=AudioSource.BUS_A)
controller.set_call_video_source(input_ref=2, video_source=VideoSource.NONE)

# Bring guest live
controller.set_call_audio_source(input_ref=2, audio_source=AudioSource.MASTER)
controller.set_call_video_source(input_ref=2, video_source=VideoSource.OUTPUT1)

# Return to green room after segment
controller.set_call_audio_source(input_ref=2, audio_source=AudioSource.BUS_A)
```

---

## Input Switching

### Transition Types

```python
from src.integrations.vmix_ptz_call import TransitionType

# Hard cut to input 3
controller.switch_input(
    input_ref=3,
    transition=TransitionType.CUT
)

# Fade to input 4 over 1 second
controller.switch_input(
    input_ref=4,
    transition=TransitionType.FADE,
    duration=1000
)

# Available transitions:
# - TransitionType.CUT
# - TransitionType.CUT_DIRECT
# - TransitionType.FADE
# - TransitionType.SLIDE
# - TransitionType.PUSH
# - TransitionType.ZOOM
```

### Preview and Program

```python
# Set input to preview (not live)
controller.preview_input(input_ref=5)

# Transition preview to program
controller.switch_input(
    input_ref=5,
    transition=TransitionType.FADE,
    duration=500
)
```

### Multi-Mix Support

```python
# Switch on main mix (default)
controller.switch_input(
    input_ref=2,
    transition=TransitionType.CUT,
    mix=0  # Main mix
)

# Switch on secondary mix 1 (4K/Pro editions)
controller.switch_input(
    input_ref=3,
    transition=TransitionType.FADE,
    duration=1000,
    mix=1  # Secondary mix 1
)
```

---

## IF.witness Audit Logging

### Automatic Logging

All commands and responses are automatically logged when a witness directory is provided:

```python
from pathlib import Path

controller = VMixController(
    witness_log_dir=Path("./witness_logs")
)

# All operations are automatically logged
controller.set_ptz_position(input_ref=1, position=PTZPosition(0, 0, 1.5))
```

### Log Format

Logs are stored in JSON Lines format with SHA-256 hashing:

```json
{
  "msg_type": "VMIX_CMD",
  "timestamp": "2025-11-12T15:30:45.123456Z",
  "data": {
    "function": "SetPanX",
    "input_ref": 1,
    "value": 1.5,
    "duration": null,
    "mix": null,
    "timestamp": "2025-11-12T15:30:45.123456Z"
  },
  "hash": "a7f3d2c1e5b4..."
}
```

### Log Files

Logs are organized by date:

```
witness_logs/
  ├── vmix_api_20251112.jsonl
  ├── vmix_api_20251113.jsonl
  └── vmix_api_20251114.jsonl
```

### Audit Trail Types

- **VMIX_CMD**: Command sent to vMix
- **VMIX_RESP**: Response from vMix
- **PTZ_MOVE**: PTZ camera movement
- **CALL_CTRL**: vMix Call control action

---

## Error Handling

### Retry Logic

The HTTP client automatically retries failed requests with exponential backoff:

```python
controller = VMixController(
    base_url="http://127.0.0.1:8088/API/",
    timeout=5,         # Request timeout in seconds
    max_retries=3      # Maximum retry attempts
)
```

### Response Checking

```python
response = controller.switch_input(input_ref=2, transition=TransitionType.FADE)

if response.success:
    print("Success!")
else:
    print(f"Error: {response.error_message}")
    print(f"Status code: {response.status_code}")
```

### Exception Handling

```python
from src.integrations.vmix_ptz_call import PTZPosition

try:
    # Invalid position (pan_x out of range)
    position = PTZPosition(pan_x=10, pan_y=0, zoom=1.0)
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # Invalid direction
    controller.ptz_move_continuous(input_ref=1, direction="invalid", speed=0.8)
except ValueError as e:
    print(f"Invalid direction: {e}")
```

---

## API Reference

### VMixController

Main controller class for vMix integration.

#### Methods

##### `set_ptz_position(input_ref, position, duration=None)`
Set PTZ camera to absolute position.

**Parameters:**
- `input_ref` (int|str): Input number, name, or GUID
- `position` (PTZPosition): Target position
- `duration` (int, optional): Transition duration in milliseconds

**Returns:** `VMixResponse`

##### `ptz_move_continuous(input_ref, direction, speed=0.8)`
Start continuous PTZ movement.

**Parameters:**
- `input_ref` (int|str): Input number, name, or GUID
- `direction` (str): "up", "down", "left", "right", "zoom_in", "zoom_out"
- `speed` (float): Movement speed (0.0 to 1.0)

**Returns:** `VMixResponse`

##### `ptz_stop(input_ref)`
Stop all PTZ camera movement.

**Parameters:**
- `input_ref` (int|str): Input number, name, or GUID

**Returns:** `VMixResponse`

##### `set_call_audio_source(input_ref, audio_source)`
Set audio return feed for vMix Call guest.

**Parameters:**
- `input_ref` (int|str): vMix Call input
- `audio_source` (AudioSource): Audio routing destination

**Returns:** `VMixResponse`

##### `set_call_video_source(input_ref, video_source)`
Set video return feed for vMix Call guest.

**Parameters:**
- `input_ref` (int|str): vMix Call input
- `video_source` (VideoSource): Video output

**Returns:** `VMixResponse`

##### `switch_input(input_ref, transition=TransitionType.CUT, duration=None, mix=0)`
Switch to specified input with transition.

**Parameters:**
- `input_ref` (int|str): Input number, name, or GUID
- `transition` (TransitionType): Transition type
- `duration` (int, optional): Transition duration in milliseconds
- `mix` (int): Mix number (0=main, 1-2=secondary)

**Returns:** `VMixResponse`

##### `preview_input(input_ref)`
Set input to preview without going live.

**Parameters:**
- `input_ref` (int|str): Input number, name, or GUID

**Returns:** `VMixResponse`

##### `get_state()`
Get current vMix state as XML.

**Returns:** `VMixResponse` with XML state data

---

## Production Examples

### Multi-Camera Production

```python
from pathlib import Path
from src.integrations.vmix_ptz_call import (
    create_vmix_controller,
    PTZPosition,
    TransitionType
)

with create_vmix_controller(witness_log_dir=Path("./witness")) as vmix:
    # Scene 1: Opening wide shot
    wide = PTZPosition(pan_x=0, pan_y=0, zoom=1.0)
    vmix.set_ptz_position(input_ref=1, position=wide, duration=1000)
    vmix.switch_input(input_ref=1, transition=TransitionType.FADE, duration=500)

    # Wait for scene duration
    import time
    time.sleep(5)

    # Scene 2: Close-up on speaker
    close_up = PTZPosition(pan_x=1.5, pan_y=0.5, zoom=3.0)
    vmix.set_ptz_position(input_ref=1, position=close_up, duration=1500)

    # Scene 3: Switch to second camera
    vmix.preview_input(input_ref=2)
    vmix.switch_input(input_ref=2, transition=TransitionType.CUT)
```

### Live Interview with Remote Guest

```python
from src.integrations.vmix_ptz_call import (
    VMixController,
    AudioSource,
    VideoSource,
    TransitionType
)

controller = VMixController()

# Guest joins in virtual green room (Bus A)
controller.set_call_audio_source(input_ref=3, audio_source=AudioSource.BUS_A)
controller.set_call_video_source(input_ref=3, video_source=VideoSource.NONE)

# Prepare guest camera for preview
controller.preview_input(input_ref=3)

# Bring guest live
controller.set_call_audio_source(input_ref=3, audio_source=AudioSource.MASTER)
controller.set_call_video_source(input_ref=3, video_source=VideoSource.OUTPUT1)
controller.switch_input(input_ref=3, transition=TransitionType.FADE, duration=1000)

# Interview segment...

# Return guest to green room
controller.set_call_audio_source(input_ref=3, audio_source=AudioSource.BUS_A)
controller.switch_input(input_ref=1, transition=TransitionType.CUT)

controller.close()
```

### Automated Camera Tracking

```python
from src.integrations.vmix_ptz_call import VMixController, PTZPosition
import time

controller = VMixController()

# Define tracking positions
positions = [
    PTZPosition(pan_x=-1.5, pan_y=0, zoom=2.0),   # Position 1
    PTZPosition(pan_x=0, pan_y=0, zoom=2.0),       # Position 2
    PTZPosition(pan_x=1.5, pan_y=0, zoom=2.0),     # Position 3
]

# Cycle through positions
for position in positions:
    controller.set_ptz_position(input_ref=1, position=position, duration=2000)
    time.sleep(5)  # Hold position for 5 seconds

controller.close()
```

---

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to vMix API

**Solutions**:
1. Verify vMix is running
2. Check API is enabled in Settings → Web
3. Confirm port 8088 is accessible
4. Test with browser: `http://127.0.0.1:8088/API/`

```python
# Test connection
controller = VMixController()
response = controller.get_state()
if response.success:
    print("Connected successfully!")
else:
    print(f"Connection failed: {response.error_message}")
```

### PTZ Camera Not Responding

**Problem**: PTZ commands sent but camera doesn't move

**Checklist**:
1. Verify camera is configured in vMix (Input Settings → PTZ tab)
2. Confirm camera protocol matches (VISCA, CGI, UVC)
3. Check camera IP address and network connectivity
4. Test manual PTZ control in vMix interface

```python
# Verify command is being sent
import logging
logging.basicConfig(level=logging.DEBUG)

controller = VMixController()
response = controller.ptz_move_continuous(input_ref=1, direction="up", speed=0.5)
print(f"Response: {response.success}, Status: {response.status_code}")
```

### Input Switching Delays

**Problem**: Transitions are too slow or instant

**Solution**: Adjust duration parameter

```python
# Fast cut (no duration)
controller.switch_input(input_ref=2, transition=TransitionType.CUT)

# Slow fade (2 seconds)
controller.switch_input(
    input_ref=3,
    transition=TransitionType.FADE,
    duration=2000
)
```

### Witness Logs Not Created

**Problem**: No log files in witness directory

**Solutions**:
1. Verify witness_log_dir is provided
2. Check directory permissions
3. Ensure Path object is used

```python
from pathlib import Path

# Correct
controller = VMixController(witness_log_dir=Path("./witness"))

# Incorrect - must use Path object
# controller = VMixController(witness_log_dir="./witness")
```

---

## Advanced Topics

### Custom HTTP Client Configuration

```python
from src.integrations.vmix_ptz_call import VMixHTTPClient, VMixController

# Create custom HTTP client
client = VMixHTTPClient(
    base_url="http://192.168.1.100:8088/API/",
    timeout=10,
    max_retries=5,
    backoff_factor=1.0
)

# Use custom client (advanced)
# Note: VMixController creates its own client by default
```

### Manual Command Construction

```python
from src.integrations.vmix_ptz_call import VMixCommand

# Construct command manually
cmd = VMixCommand(
    function="SetPanX",
    input_ref=1,
    value=1.5,
    duration=1000
)

# Get URL parameters
params = cmd.to_url_params()
print(params)  # {'Function': 'SetPanX', 'Input': '1', 'Value': '1.5', 'Duration': '1000'}

# Get canonical representation for hashing
canonical = cmd.to_canonical()
```

### Direct Witness Logging

```python
from pathlib import Path
from src.integrations.vmix_ptz_call import (
    VMixWitnessLogger,
    VMixCommand,
    VMixResponse,
    PTZPosition
)

# Create standalone witness logger
witness = VMixWitnessLogger(Path("./custom_witness"))

# Log custom events
cmd = VMixCommand(function="CustomFunction", input_ref=1)
witness.log_command(cmd)

response = VMixResponse(success=True, status_code=200)
witness.log_response(response)

position = PTZPosition(pan_x=1.0, pan_y=0, zoom=2.0)
witness.log_ptz_move(input_ref=1, position=position)
```

---

## References

### Official vMix Documentation
- **HTTP Web API**: https://www.vmix.com/help25/DeveloperAPI.html
- **PTZ Control**: https://www.vmix.com/help25/PTZPanTiltZoom.html
- **vMix Call**: https://www.vmix.com/help24/VideoCall.html
- **Shortcut Functions**: https://www.vmix.com/help25/ShortcutFunctionReference.html

### InfraFabric Resources
- **Research Reports**:
  - PTZ Control: `/home/user/infrafabric/RESEARCH_VMIX_PTZ_CONTROL_SESSION3.md`
  - SIP/Skype Integration: `/home/user/infrafabric/docs/research/vMix-SIP-Skype-Integration-Research.md`
  - Input Control: `/home/user/infrafabric/VMIX_INPUT_CONTROL_RESEARCH.md`

### Module Files
- **Source**: `/home/user/infrafabric/src/integrations/vmix_ptz_call.py`
- **Tests**: `/home/user/infrafabric/tests/test_vmix_ptz_call.py`

---

## Support

For issues, questions, or contributions:

1. Review research reports in `/home/user/infrafabric/docs/research/`
2. Check test suite for usage examples
3. Examine IF.witness logs for debugging

---

**End of Documentation**

*Generated: 2025-11-12*
*Version: 1.0.0*
*Module: vMix PTZ and Call Control Integration*
