# vMix Streaming Integration with InfraFabric

**Session 2 (WebRTC) - vMix Streaming Integration**
**Author:** IF.Session2 Agent
**Date:** 2025-11-12
**Status:** ✅ Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Quick Start](#quick-start)
5. [API Reference](#api-reference)
6. [Streaming Destinations](#streaming-destinations)
7. [SRT Streaming](#srt-streaming)
8. [Recording Control](#recording-control)
9. [Monitoring & Health](#monitoring--health)
10. [IF.witness Integration](#ifwitness-integration)
11. [Troubleshooting](#troubleshooting)
12. [Examples](#examples)

---

## Overview

The vMix Streaming Integration provides comprehensive control over vMix streaming outputs within the InfraFabric ecosystem. This integration enables:

- **RTMP Streaming**: Multi-platform streaming (Twitch, YouTube, Facebook, custom servers)
- **SRT Streaming**: Low-latency, secure reliable transport for professional workflows
- **Recording Control**: Local recording with multiple format support
- **Health Monitoring**: Real-time stream quality metrics
- **Provenance Tracking**: IF.witness integration for audit trails

### Key Features

✅ **Multi-Channel Support**: Stream to 3 destinations simultaneously (vMix channels 0-2)
✅ **Platform Presets**: Pre-configured settings for Twitch, YouTube, Facebook
✅ **Low Latency**: SRT support with sub-second latency (120ms default)
✅ **Error Handling**: Comprehensive validation and graceful failure handling
✅ **Audit Trail**: IF.witness hash chain for provenance tracking
✅ **Health Monitoring**: Real-time FPS, bitrate, and dropped frame tracking

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 InfraFabric Application                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │     VMixStreamingController                         │    │
│  │                                                     │    │
│  │  • RTMP Stream Control                             │    │
│  │  • SRT Stream Control                              │    │
│  │  • Recording Control                               │    │
│  │  • Status & Health Monitoring                      │    │
│  │  • IF.witness Integration                          │    │
│  └───────────────────┬────────────────────────────────┘    │
│                      │                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │
                       │ HTTP API (Port 8088)
                       │
         ┌─────────────┴──────────────┐
         │                            │
         │      vMix Instance         │
         │                            │
         │  • Function API            │
         │  • XML Status API          │
         │  • Web Controller          │
         │                            │
         └─────────────┬──────────────┘
                       │
         ┌─────────────┴──────────────────────────────┐
         │                                             │
    ┌────▼────┐   ┌────────────┐   ┌─────────────┐  │
    │  RTMP   │   │    SRT     │   │  Recording  │  │
    │ Channel │   │  Stream    │   │    Output   │  │
    └─────────┘   └────────────┘   └─────────────┘  │
         │                │                 │         │
         │                │                 │         │
    ┌────▼─────┐    ┌────▼─────┐     ┌─────▼──────┐ │
    │ Twitch   │    │  Live     │     │  Local     │ │
    │ YouTube  │    │  Production│     │  Storage   │ │
    │ Facebook │    │  (120ms)   │     │  (MP4/AVI) │ │
    └──────────┘    └───────────┘     └────────────┘ │
                                                       │
                    Streaming Outputs                  │
                                                       │
└───────────────────────────────────────────────────────┘
```

### Component Interactions

1. **Application Layer**: Your InfraFabric application instantiates `VMixStreamingController`
2. **Controller Layer**: Manages vMix API communication and IF.witness logging
3. **vMix Instance**: Handles encoding, streaming, and recording operations
4. **Output Destinations**: RTMP servers, SRT endpoints, local storage

---

## Installation & Setup

### Prerequisites

1. **vMix Software** (version 24+)
   - Download: https://www.vmix.com/
   - Supported editions: Basic, HD, 4K, Pro
   - Web Controller must be enabled

2. **Python Requirements**
   ```bash
   pip install requests
   ```

3. **vMix Configuration**
   - Enable Web Controller: Settings → Web Controller → Enable
   - Default port: 8088 (configurable in vMix settings)
   - Note: Web Controller may require vMix HD edition or higher

### Installation Steps

1. **Copy Integration File**
   ```bash
   cp src/integrations/vmix_streaming.py your_project/integrations/
   ```

2. **Verify vMix Connection**
   ```python
   from integrations.vmix_streaming import VMixStreamingController

   controller = VMixStreamingController(vmix_host='localhost', vmix_port=8088)

   try:
       controller._check_connection()
       print("✅ vMix connection successful!")
   except Exception as e:
       print(f"❌ Connection failed: {e}")
   ```

3. **Test Configuration**
   ```bash
   # Run example usage
   python src/integrations/vmix_streaming.py
   ```

---

## Quick Start

### Basic RTMP Streaming

```python
from integrations.vmix_streaming import VMixStreamingController, StreamingDestinations

# Initialize controller
controller = VMixStreamingController(vmix_host='localhost', vmix_port=8088)

# Start Twitch stream
twitch_config = StreamingDestinations.twitch("your_stream_key_here")
result = controller.start_rtmp_stream(**twitch_config, channel=0)

if result['success']:
    print(f"✅ Stream started on channel {result['channel']}")
else:
    print(f"❌ Failed: {result['message']}")

# Monitor stream status
status = controller.get_stream_status()
print(f"Streaming: {status['streaming']}, Uptime: {status['stream_time']}")

# Stop stream
controller.stop_stream(channel=0)
```

### SRT Low-Latency Streaming

```python
# Start SRT stream (caller mode, 120ms latency)
result = controller.start_srt_stream(
    srt_address="srt://192.168.1.100:9000",
    mode="caller",
    latency_ms=120,
    channel=0
)

print(f"SRT stream: {result['message']}")
```

### Recording Control

```python
# Start recording
result = controller.start_recording(
    filename="production_2025-11-12.mp4",
    format="MP4",
    quality="high"
)

print(f"Recording started: {result['filename']}")

# Stop recording after 1 hour
import time
time.sleep(3600)  # 1 hour

stop_result = controller.stop_recording()
print(f"Recording stopped. Duration: {stop_result['duration']}")
```

---

## API Reference

### `VMixStreamingController`

#### `__init__(vmix_host='localhost', vmix_port=8088)`

Initialize vMix controller.

**Parameters:**
- `vmix_host` (str): vMix instance hostname/IP (default: 'localhost')
- `vmix_port` (int): vMix HTTP API port (default: 8088)

**Example:**
```python
# Local vMix instance
controller = VMixStreamingController()

# Remote vMix instance
controller = VMixStreamingController(vmix_host='192.168.1.50', vmix_port=8088)
```

---

#### `start_rtmp_stream(rtmp_url, stream_key, channel=0, configure_first=True)`

Start RTMP stream to destination.

**Parameters:**
- `rtmp_url` (str): RTMP server URL (e.g., `rtmp://live.twitch.tv/app/`)
- `stream_key` (str): Stream key/password
- `channel` (int): Stream channel 0-2 (default: 0)
- `configure_first` (bool): Configure destination before starting (default: True)

**Returns:**
```python
{
    'success': True,
    'message': 'RTMP stream started on channel 0',
    'channel': 0,
    'destination': 'rtmp://live.twitch.tv/app/'
}
```

**Example:**
```python
result = controller.start_rtmp_stream(
    rtmp_url='rtmp://live.twitch.tv/app/',
    stream_key='live_123456789_abc',
    channel=0
)
```

---

#### `start_srt_stream(srt_address, mode='caller', latency_ms=120, channel=0)`

Start SRT stream (Secure Reliable Transport).

**Parameters:**
- `srt_address` (str): SRT address (e.g., `srt://192.168.1.100:9000`)
- `mode` (str): 'caller' or 'listener' (default: 'caller')
- `latency_ms` (int): SRT latency in milliseconds 20-8000 (default: 120)
- `channel` (int): Stream channel 0-2 (default: 0)

**Returns:**
```python
{
    'success': True,
    'message': 'SRT stream started (caller mode, 120ms latency)',
    'protocol': 'SRT',
    'mode': 'caller',
    'latency_ms': 120,
    'channel': 0
}
```

**Example:**
```python
# Caller mode (vMix initiates connection)
result = controller.start_srt_stream(
    srt_address='srt://192.168.1.100:9000',
    mode='caller',
    latency_ms=120
)

# Listener mode (vMix waits for connection)
result = controller.start_srt_stream(
    srt_address='srt://0.0.0.0:9000',
    mode='listener',
    latency_ms=200
)
```

---

#### `start_recording(filename=None, format='MP4', quality='high')`

Start local recording.

**Parameters:**
- `filename` (str, optional): Output filename (vMix auto-generates if None)
- `format` (str): Recording format: 'MP4', 'AVI', 'MOV', 'MKV' (default: 'MP4')
- `quality` (str): Quality preset: 'low', 'medium', 'high', 'custom' (default: 'high')

**Returns:**
```python
{
    'success': True,
    'message': 'Recording started',
    'filename': 'production_2025-11-12.mp4',
    'format': 'MP4',
    'quality': 'high'
}
```

**Example:**
```python
# Custom filename
result = controller.start_recording(
    filename='live_show_2025-11-12.mp4',
    format='MP4',
    quality='high'
)

# Auto-generated filename
result = controller.start_recording(format='MP4', quality='high')
```

---

#### `stop_stream(channel=0)`

Stop streaming on specified channel.

**Parameters:**
- `channel` (int): Stream channel to stop 0-2 (default: 0)

**Returns:**
```python
{
    'success': True,
    'message': 'Stream stopped on channel 0',
    'channel': 0
}
```

---

#### `stop_recording()`

Stop active recording.

**Returns:**
```python
{
    'success': True,
    'message': 'Recording stopped',
    'duration': '00:45:32'
}
```

---

#### `get_stream_status()`

Get streaming/recording status from vMix.

**Returns:**
```python
{
    'streaming': True,
    'recording': False,
    'stream_time': '00:15:30',
    'record_time': '00:00:00',
    'stream_channels': [0, 1],
    'version': '25.0.0.0',
    'edition': 'Pro',
    'timestamp': '2025-11-12T10:30:00.000Z'
}
```

**Example:**
```python
status = controller.get_stream_status()

if status['streaming']:
    print(f"Streaming on channels: {status['stream_channels']}")
    print(f"Uptime: {status['stream_time']}")

if status['recording']:
    print(f"Recording duration: {status['record_time']}")
```

---

#### `get_stream_health()`

Get stream health metrics.

**Returns:**
```python
{
    'bitrate_kbps': 5000.0,
    'dropped_frames': 50,
    'fps': 30.0,
    'uptime_seconds': 1800,
    'health_status': 'healthy',  # 'healthy', 'warning', 'critical'
    'timestamp': '2025-11-12T10:30:00.000Z'
}
```

**Health Status Criteria:**
- `healthy`: fps ≥ 29, dropped_frames < 100
- `warning`: fps ≥ 25, dropped_frames < 500
- `critical`: fps < 25 or dropped_frames ≥ 500

**Example:**
```python
health = controller.get_stream_health()

if health['health_status'] == 'critical':
    print("⚠️ Stream quality degraded!")
    print(f"FPS: {health['fps']}, Dropped: {health['dropped_frames']}")
    # Trigger alert or reduce bitrate
```

---

## Streaming Destinations

### Pre-configured Platforms

The `StreamingDestinations` class provides pre-configured settings for popular platforms:

#### Twitch

```python
from integrations.vmix_streaming import StreamingDestinations

config = StreamingDestinations.twitch("your_stream_key")
# Returns: {
#     'rtmp_url': 'rtmp://live.twitch.tv/app/',
#     'stream_key': 'your_stream_key'
# }

controller.start_rtmp_stream(**config, channel=0)
```

**Getting Your Twitch Stream Key:**
1. Go to: https://dashboard.twitch.tv/settings/stream
2. Copy "Primary Stream Key"
3. Format: `live_123456789_abcdefghijklmnopqrstuvwx`

---

#### YouTube Live

```python
config = StreamingDestinations.youtube("your_stream_key")
# Returns: {
#     'rtmp_url': 'rtmp://a.rtmp.youtube.com/live2/',
#     'stream_key': 'your_stream_key'
# }

controller.start_rtmp_stream(**config, channel=0)
```

**Getting Your YouTube Stream Key:**
1. Go to: https://studio.youtube.com/
2. Click "Go Live" → "Stream" tab
3. Copy "Stream key"
4. Format: `xxxx-xxxx-xxxx-xxxx-xxxx`

---

#### Facebook Live

```python
config = StreamingDestinations.facebook("your_stream_key")
# Returns: {
#     'rtmp_url': 'rtmps://live-api-s.facebook.com:443/rtmp/',
#     'stream_key': 'your_stream_key'
# }

controller.start_rtmp_stream(**config, channel=0)
```

**Getting Your Facebook Stream Key:**
1. Go to: https://www.facebook.com/live/producer
2. Click "Go Live" → "Streaming Software"
3. Copy "Stream Key"

---

#### Custom RTMP Server

```python
config = StreamingDestinations.custom_rtmp(
    server_url='rtmp://your-server.com/live',
    stream_key='custom_stream_key'
)

controller.start_rtmp_stream(**config, channel=0)
```

**Common Custom RTMP Servers:**
- **Restream.io**: `rtmp://live.restream.io/live/`
- **OBS Ninja**: Custom server URL
- **Wowza Streaming Engine**: `rtmp://your-server.com/live/`
- **Nginx RTMP Module**: `rtmp://your-server.com/live/`

---

## SRT Streaming

### What is SRT?

**SRT (Secure Reliable Transport)** is a UDP-based streaming protocol offering:

- **Low Latency**: Sub-second latency (default 120ms)
- **Reliability**: Packet retransmission for error recovery
- **Security**: AES encryption support
- **Firewall Traversal**: Works across NAT and firewalls

### SRT Modes

#### Caller Mode (Client)

vMix initiates connection to remote SRT server.

```python
result = controller.start_srt_stream(
    srt_address='srt://192.168.1.100:9000',
    mode='caller',
    latency_ms=120,
    channel=0
)
```

**Use Cases:**
- Streaming to remote production facility
- Sending feed to cloud transcoding service
- Point-to-point contribution

---

#### Listener Mode (Server)

vMix waits for incoming SRT connections.

```python
result = controller.start_srt_stream(
    srt_address='srt://0.0.0.0:9000',  # Listen on all interfaces
    mode='listener',
    latency_ms=200,
    channel=0
)
```

**Use Cases:**
- Receiving feeds from remote cameras
- Studio-to-studio backhaul
- Multi-camera live production

---

### SRT Latency Configuration

| Latency | Use Case | Network Requirements |
|---------|----------|---------------------|
| 20-60ms | LAN streaming | Stable, low-latency network |
| 120ms (default) | Internet streaming | Standard broadband |
| 200-500ms | Long-haul / satellite | High-latency or unreliable networks |
| 1000-8000ms | Extremely challenging networks | Packet loss > 10% |

**Example:**
```python
# Low latency for LAN
result = controller.start_srt_stream(
    srt_address='srt://192.168.1.100:9000',
    mode='caller',
    latency_ms=50  # 50ms for LAN
)

# Higher latency for unreliable network
result = controller.start_srt_stream(
    srt_address='srt://remote-server.com:9000',
    mode='caller',
    latency_ms=500  # 500ms for reliability
)
```

---

## Recording Control

### Recording Formats

| Format | Use Case | File Size | Quality |
|--------|----------|-----------|---------|
| **MP4** | Broadcast, web | Small | High |
| **AVI** | Legacy compatibility | Large | High |
| **MOV** | Video editing (ProRes) | Very large | Highest |
| **MKV** | Archival, multi-track | Medium | High |

### Recording Workflow

```python
# 1. Start recording with custom filename
result = controller.start_recording(
    filename='production_2025-11-12_show-01.mp4',
    format='MP4',
    quality='high'
)

print(f"Recording: {result['filename']}")

# 2. Monitor recording status
import time
while True:
    status = controller.get_stream_status()
    print(f"Recording time: {status['record_time']}")
    time.sleep(60)  # Check every minute

    # Stop after 1 hour
    if status['record_time'] >= '01:00:00':
        break

# 3. Stop recording
stop_result = controller.stop_recording()
print(f"Recording saved. Duration: {stop_result['duration']}")
```

### Auto-Generated Filenames

If `filename=None`, vMix generates filename automatically:

```python
result = controller.start_recording(format='MP4', quality='high')
# vMix generates: vMix - 2025-11-12 10-30-00.mp4
```

**Format:** `vMix - YYYY-MM-DD HH-MM-SS.ext`

---

## Monitoring & Health

### Real-Time Health Monitoring

```python
import time

def monitor_stream_health(controller, interval=30):
    """Monitor stream health and alert on issues"""

    while True:
        health = controller.get_stream_health()
        status = controller.get_stream_status()

        print(f"\n=== Stream Health Report ===")
        print(f"Status: {health['health_status'].upper()}")
        print(f"FPS: {health['fps']:.1f}")
        print(f"Bitrate: {health['bitrate_kbps']:.0f} kbps")
        print(f"Dropped Frames: {health['dropped_frames']}")
        print(f"Uptime: {status['stream_time']}")

        # Alert on critical issues
        if health['health_status'] == 'critical':
            print("⚠️ CRITICAL: Stream quality degraded!")
            # Send alert (email, Slack, etc.)
            send_alert(f"Stream critical: FPS={health['fps']}, Dropped={health['dropped_frames']}")

        elif health['health_status'] == 'warning':
            print("⚠️ WARNING: Stream quality declining")

        time.sleep(interval)

# Start monitoring
monitor_stream_health(controller, interval=30)
```

### Health Metrics Dashboard

```python
def create_health_dashboard(controller):
    """Create real-time health dashboard"""

    health = controller.get_stream_health()
    status = controller.get_stream_status()

    # Calculate health score (0-100)
    fps_score = min(100, (health['fps'] / 30) * 100)
    drop_score = max(0, 100 - (health['dropped_frames'] / 10))
    overall_score = (fps_score + drop_score) / 2

    dashboard = f"""
    ╔═══════════════════════════════════════════════╗
    ║          vMix Stream Health Dashboard          ║
    ╠═══════════════════════════════════════════════╣
    ║ Overall Health:  {overall_score:.0f}%  [{health['health_status'].upper()}]      ║
    ║                                               ║
    ║ Frame Rate:      {health['fps']:.1f} FPS                      ║
    ║ Bitrate:         {health['bitrate_kbps']:.0f} kbps                   ║
    ║ Dropped Frames:  {health['dropped_frames']}                           ║
    ║ Uptime:          {status['stream_time']}                      ║
    ║                                               ║
    ║ Active Channels: {len(status['stream_channels'])} ({', '.join(map(str, status['stream_channels']))})                   ║
    ║ Recording:       {'Yes' if status['recording'] else 'No'}                          ║
    ╚═══════════════════════════════════════════════╝
    """

    print(dashboard)
    return overall_score

# Display dashboard
create_health_dashboard(controller)
```

---

## IF.witness Integration

### Provenance Tracking

The vMix integration includes IF.witness hash chain for provenance tracking, creating tamper-evident audit trails of all streaming operations.

### How It Works

1. **Genesis Hash**: Controller initialized with genesis hash
2. **Event Logging**: Each operation logged to witness chain
3. **Hash Chain**: Each event hashed with previous hash
4. **Verification**: Chain integrity can be verified

### Event Types

| Event Type | Description |
|------------|-------------|
| `stream_started` | RTMP/SRT stream started |
| `stream_stopped` | Stream stopped |
| `srt_stream_started` | SRT stream started (with latency params) |
| `recording_started` | Recording started |
| `recording_stopped` | Recording stopped (with duration) |

### Retrieving Witness Log

```python
# Get all witness events
log = controller.get_witness_log()

for entry in log:
    event = entry['event']
    print(f"{event['timestamp']}: {event['event_type']}")
    print(f"  Hash: {entry['current_hash'][:16]}...")
    print(f"  Params: {event['params']}")

# Filter by event type
stream_events = controller.get_witness_log(event_type='stream_started')
print(f"Total stream starts: {len(stream_events)}")
```

### Verifying Chain Integrity

```python
verification = controller.verify_witness_chain()

if verification['valid']:
    print("✅ Witness chain is intact")
    print(f"   Total events: {verification['total_events']}")
    print(f"   First hash: {verification['first_hash'][:16]}...")
    print(f"   Last hash: {verification['last_hash'][:16]}...")
else:
    print("❌ Witness chain is broken!")
    print(f"   Broken at index: {verification['broken_at']}")
```

### Example Witness Entry

```python
{
    'event': {
        'event_type': 'stream_started',
        'timestamp': '2025-11-12T10:30:00.000Z',
        'params': {
            'protocol': 'RTMP',
            'destination': 'rtmp://live.twitch.tv/app/',
            'channel': 0
        },
        'result': {'success': True}
    },
    'previous_hash': 'a7f3c91b...',
    'current_hash': 'b2e4d87a...',
    'witness_timestamp': '2025-11-12T10:30:00.123Z'
}
```

---

## Troubleshooting

### Common Issues

#### 1. Cannot Connect to vMix

**Error:**
```
VMixConnectionError: Cannot connect to vMix at localhost:8088
```

**Solutions:**
- ✅ Verify vMix is running
- ✅ Check Web Controller is enabled: Settings → Web Controller → Enable
- ✅ Verify port 8088 is not blocked by firewall
- ✅ Try accessing http://localhost:8088/api in browser (should show XML)
- ✅ If using remote vMix, ensure correct IP address

**Test Connection:**
```python
import requests
response = requests.get('http://localhost:8088/api')
print(response.status_code)  # Should be 200
print(response.text[:100])   # Should show XML
```

---

#### 2. Stream Starts But No Output

**Symptoms:**
- `start_rtmp_stream()` returns success
- vMix shows "Streaming" but no data on platform

**Solutions:**
- ✅ Verify stream key is correct (check Twitch/YouTube dashboard)
- ✅ Check RTMP URL format includes trailing slash: `rtmp://server.com/app/`
- ✅ Ensure vMix has active inputs (camera, video file, etc.)
- ✅ Check vMix firewall rules allow outbound RTMP (port 1935)

**Debug:**
```python
status = controller.get_stream_status()
print(f"Streaming: {status['streaming']}")
print(f"Active channels: {status['stream_channels']}")

health = controller.get_stream_health()
print(f"Bitrate: {health['bitrate_kbps']} kbps")  # Should be > 0
```

---

#### 3. High Dropped Frames

**Symptoms:**
```python
health = controller.get_stream_health()
print(health['dropped_frames'])  # > 500
print(health['health_status'])   # 'critical'
```

**Solutions:**
- ✅ Reduce stream bitrate in vMix: Settings → Stream → Quality
- ✅ Check CPU usage (vMix encoding is CPU-intensive)
- ✅ Verify network bandwidth (4K streaming requires 15-25 Mbps upload)
- ✅ Switch to hardware encoding (NVIDIA NVENC, Intel QuickSync)
- ✅ Close other applications consuming bandwidth

---

#### 4. SRT Connection Fails

**Error:**
```python
result = controller.start_srt_stream(...)
print(result['success'])  # False
```

**Solutions:**
- ✅ Verify SRT address format: `srt://ip:port` (no trailing slash)
- ✅ Check firewall allows UDP traffic on SRT port (default: 9000)
- ✅ Ensure SRT latency matches network conditions (increase for long-haul)
- ✅ Verify remote SRT server is in matching mode (caller ↔ listener)
- ✅ Test SRT connection with srt-live-transmit tool first

**Test SRT Connectivity:**
```bash
# Install SRT tools
sudo apt-get install srt-tools

# Test SRT connection
srt-live-transmit srt://192.168.1.100:9000 output.ts
```

---

#### 5. Recording Fails to Start

**Error:**
```python
result = controller.start_recording(...)
print(result['success'])  # False
```

**Solutions:**
- ✅ Check vMix recording path has sufficient disk space
- ✅ Verify write permissions on recording directory
- ✅ Ensure filename doesn't contain invalid characters (`< > : " / \ | ? *`)
- ✅ Check vMix edition supports recording (Basic edition has limitations)
- ✅ Verify codec settings are valid (some require specific vMix editions)

---

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('vmix_streaming')

# Add debug output to controller
controller._send_function('StartStreaming', Value='0')
# Logs: GET http://localhost:8088/api/?Function=StartStreaming&Value=0
```

---

## Examples

### Example 1: Multi-Platform Streaming

Stream to Twitch, YouTube, and Facebook simultaneously.

```python
from integrations.vmix_streaming import VMixStreamingController, StreamingDestinations

controller = VMixStreamingController()

# Configure all platforms
platforms = [
    ('Twitch', StreamingDestinations.twitch('twitch_key_here'), 0),
    ('YouTube', StreamingDestinations.youtube('youtube_key_here'), 1),
    ('Facebook', StreamingDestinations.facebook('facebook_key_here'), 2)
]

# Start all streams
for name, config, channel in platforms:
    result = controller.start_rtmp_stream(**config, channel=channel)
    if result['success']:
        print(f"✅ {name} streaming on channel {channel}")
    else:
        print(f"❌ {name} failed: {result['message']}")

# Monitor all streams
import time
while True:
    status = controller.get_stream_status()
    health = controller.get_stream_health()

    print(f"\nActive channels: {status['stream_channels']}")
    print(f"Health: {health['health_status']}, FPS: {health['fps']}")

    time.sleep(30)
```

---

### Example 2: Automated Recording with Schedule

Record shows automatically based on schedule.

```python
import schedule
import time
from datetime import datetime

def start_show_recording():
    """Start recording for scheduled show"""
    show_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"daily_show_{show_date}.mp4"

    result = controller.start_recording(
        filename=filename,
        format='MP4',
        quality='high'
    )

    if result['success']:
        print(f"✅ Recording started: {filename}")

        # Also start Twitch stream
        twitch_config = StreamingDestinations.twitch('your_key')
        controller.start_rtmp_stream(**twitch_config, channel=0)

def stop_show_recording():
    """Stop recording after show ends"""
    stop_result = controller.stop_recording()
    controller.stop_stream(channel=0)

    print(f"✅ Show ended. Duration: {stop_result['duration']}")

# Schedule daily show (Monday-Friday, 7 PM - 9 PM)
schedule.every().monday.at("19:00").do(start_show_recording)
schedule.every().monday.at("21:00").do(stop_show_recording)

schedule.every().tuesday.at("19:00").do(start_show_recording)
schedule.every().tuesday.at("21:00").do(stop_show_recording)

# ... repeat for other days

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

### Example 3: SRT Contribution Feed

Receive SRT feed from remote camera and record.

```python
# vMix as SRT listener (waiting for remote camera)
result = controller.start_srt_stream(
    srt_address='srt://0.0.0.0:9000',
    mode='listener',
    latency_ms=200,
    channel=0
)

print(f"SRT listener active on port 9000")
print("Waiting for remote camera connection...")

# Start recording when connected
import time
time.sleep(5)  # Wait for connection

status = controller.get_stream_status()
if status['streaming']:
    print("✅ Remote camera connected!")

    # Start recording
    result = controller.start_recording(
        filename='remote_feed_backup.mp4',
        format='MP4',
        quality='high'
    )

    print(f"Recording remote feed: {result['filename']}")
else:
    print("❌ No connection received")
```

---

### Example 4: Health Monitoring with Alerts

Monitor stream health and send alerts on issues.

```python
import time
import smtplib
from email.mime.text import MIMEText

def send_alert_email(subject, body):
    """Send email alert"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'alerts@yourstream.com'
    msg['To'] = 'admin@yourstream.com'

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login('your_email@gmail.com', 'your_password')
    smtp.send_message(msg)
    smtp.quit()

def monitor_with_alerts(controller, interval=30):
    """Monitor stream health and send alerts"""

    alert_threshold = {
        'critical': False,
        'warning': False
    }

    while True:
        health = controller.get_stream_health()
        status = controller.get_stream_status()

        # Check for critical issues
        if health['health_status'] == 'critical':
            if not alert_threshold['critical']:
                send_alert_email(
                    subject='🚨 CRITICAL: Stream Quality Degraded',
                    body=f"Stream health is critical!\n"
                         f"FPS: {health['fps']}\n"
                         f"Dropped Frames: {health['dropped_frames']}\n"
                         f"Bitrate: {health['bitrate_kbps']} kbps"
                )
                alert_threshold['critical'] = True
        else:
            alert_threshold['critical'] = False

        # Check for warnings
        if health['health_status'] == 'warning':
            if not alert_threshold['warning']:
                print("⚠️ WARNING: Stream quality declining")
                alert_threshold['warning'] = True
        else:
            alert_threshold['warning'] = False

        time.sleep(interval)

# Start monitoring
monitor_with_alerts(controller, interval=30)
```

---

### Example 5: IF.witness Audit Trail Export

Export provenance log for compliance auditing.

```python
import json
from datetime import datetime

def export_witness_log(controller, output_file='witness_log.json'):
    """Export IF.witness log to JSON file"""

    log = controller.get_witness_log()
    verification = controller.verify_witness_chain()

    export_data = {
        'export_date': datetime.utcnow().isoformat(),
        'total_events': verification['total_events'],
        'chain_valid': verification['valid'],
        'first_hash': verification['first_hash'],
        'last_hash': verification['last_hash'],
        'events': log
    }

    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"✅ Witness log exported to {output_file}")
    print(f"   Total events: {verification['total_events']}")
    print(f"   Chain valid: {verification['valid']}")

# Export log
export_witness_log(controller, 'vmix_audit_trail_2025-11-12.json')
```

---

## Advanced Topics

### Custom vMix Functions

Send custom vMix Function API commands:

```python
# Custom function example: Set audio volume
result = controller._send_function(
    'SetVolume',
    Input='1',
    Value='50'
)

# Custom function: Transition to input
result = controller._send_function(
    'Transition',
    Input='2',
    Duration='1000'  # 1 second
)
```

### Extending the Controller

Subclass `VMixStreamingController` for custom behavior:

```python
class CustomVMixController(VMixStreamingController):
    def start_twitch_with_recording(self, stream_key):
        """Start Twitch stream and recording together"""

        # Start Twitch stream
        twitch_config = StreamingDestinations.twitch(stream_key)
        stream_result = self.start_rtmp_stream(**twitch_config, channel=0)

        # Start recording backup
        record_result = self.start_recording(
            filename=f"twitch_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
            format='MP4',
            quality='high'
        )

        return {
            'stream': stream_result,
            'recording': record_result
        }

# Use custom controller
custom_controller = CustomVMixController()
result = custom_controller.start_twitch_with_recording('your_key')
```

---

## Additional Resources

### Official vMix Documentation
- vMix API Reference: https://www.vmix.com/help25/index.htm?DeveloperAPI.html
- vMix Function List: https://www.vmix.com/help25/ShortcutFunctionReference.html
- vMix XML API: https://www.vmix.com/help25/XMLAPI.html

### Community Resources
- vMix API Explorer: https://vmixapi.com/
- vMix Forums: https://forums.vmix.com/
- vMix REST API (GitHub): https://github.com/curtgrimes/vmix-rest-api

### InfraFabric Resources
- IF.witness Paper: `/home/user/infrafabric/papers/IF-witness.md`
- WebRTC Integration: `/home/user/infrafabric/docs/WEBRTC-README.md`
- Component Index: `/home/user/infrafabric/COMPONENT-INDEX.md`

---

## Support & Contributing

### Report Issues

Found a bug? Please report:
1. vMix version and edition
2. Python version
3. Error message and traceback
4. Steps to reproduce

### Feature Requests

Suggest enhancements:
- Multi-destination recording (record + stream simultaneously to different servers)
- NDI integration (vMix → NDI → InfraFabric)
- Advanced SRT features (encryption, bonding)
- Replay and instant replay control

### Contributing

Contributions welcome! Areas for improvement:
- Additional streaming platform presets
- Enhanced health monitoring algorithms
- Integration with InfraFabric messaging bus
- WebRTC bridge for browser-based control

---

## Changelog

### Version 1.0.0 (2025-11-12)

✅ **Initial Release**
- RTMP streaming (Twitch, YouTube, Facebook, custom)
- SRT streaming (caller/listener modes, configurable latency)
- Recording control (MP4, AVI, MOV, MKV)
- Status queries and health monitoring
- IF.witness integration with hash chain
- Comprehensive error handling
- Full test suite
- Complete documentation

---

## License

This integration is part of the InfraFabric project.

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Code & Data:** Available at https://github.com/dannystocker/infrafabric-core
**Contact:** Danny Stocker (danny.stocker@gmail.com)

---

**Document Metadata:**
- Generated: 2025-11-12
- Session: IF.Session2 (WebRTC) - vMix Streaming Integration
- IF.witness: Hash chain enabled
- Status: ✅ Complete

🤖 Generated with InfraFabric coordination infrastructure
