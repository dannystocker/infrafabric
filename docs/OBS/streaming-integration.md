# OBS Streaming Integration for InfraFabric

## Overview

This document describes the OBS Studio streaming integration for InfraFabric, enabling control of OBS streaming outputs, virtual camera, and recording functionality through the OBS WebSocket protocol.

## Features

- **Streaming Control**: Start/stop streaming to Twitch, YouTube, Facebook, or custom RTMP servers
- **Virtual Camera**: Enable OBS Virtual Camera for use in Zoom, Meet, Discord, etc.
- **Recording**: Local recording with pause/resume support
- **Statistics**: Real-time stream health monitoring (bitrate, dropped frames, CPU usage)
- **IF.witness Integration**: Provenance tracking with hash chain verification
- **Multi-format Support**: MP4, MKV, FLV recording formats

## Installation

### Prerequisites

1. **OBS Studio** (version 28.0+ recommended)
   - Download: https://obsproject.com/
   - Enable WebSocket server in OBS: Tools → WebSocket Server Settings

2. **Python Dependencies**

```bash
pip install obs-websocket-py
```

### OBS WebSocket Setup

1. Open OBS Studio
2. Go to **Tools → WebSocket Server Settings**
3. Enable **WebSocket Server**
4. Set **Server Port**: 4455 (default)
5. (Optional) Enable authentication and set password
6. Click **Apply** and **OK**

**Verify Connection:**
- Server should show: `WebSocket server is running on port 4455`
- Firewall: Allow connections on port 4455

## Quick Start

### Basic Streaming Example

```python
from src.integrations.obs_streaming import OBSStreamingController

# Create controller
controller = OBSStreamingController(
    obs_host="localhost",
    obs_port=4455,
    obs_password=None  # Set if you enabled authentication
)

# Connect to OBS
controller.connect()

# Start streaming to Twitch
controller.start_stream(
    service="Twitch",
    key="live_123456789_abcdefghijklmnop"
)

# Monitor stream health
import time
for i in range(10):
    status = controller.get_stream_status()
    print(f"Bitrate: {status['kbits_per_sec']} kbps, Dropped: {status['output_skipped_frames']}")
    time.sleep(5)

# Stop streaming
controller.stop_stream()

# Disconnect
controller.disconnect()
```

### Context Manager Usage

```python
from src.integrations.obs_streaming import OBSStreamingContext

controller = OBSStreamingController()

with OBSStreamingContext(controller) as obs:
    # Automatically connects
    obs.start_stream(service="YouTube", key="your-key")
    time.sleep(60)
    obs.stop_stream()
    # Automatically disconnects
```

## Streaming Services

### Twitch

```python
controller.start_stream(
    service="Twitch",
    key="live_123456789_abcdefg"
)
```

**Getting Your Twitch Stream Key:**
1. Go to https://dashboard.twitch.tv/settings/stream
2. Copy your **Primary Stream Key**
3. Never share your stream key publicly!

### YouTube Live

```python
controller.start_stream(
    service="YouTube Live",
    key="your-youtube-stream-key"
)
```

**Getting Your YouTube Stream Key:**
1. Go to https://studio.youtube.com/
2. Click **Go Live** → **Stream**
3. Copy your **Stream Key**

### Facebook Live

```python
controller.start_stream(
    service="Facebook Live",
    key="your-facebook-key"
)
```

### Custom RTMP Server

```python
controller.start_stream(
    service="Custom",
    server="rtmp://custom-server.example.com:1935/live",
    key="secret-stream-key"
)
```

**Common Custom RTMP Servers:**
- **Nginx RTMP**: `rtmp://server-ip:1935/live`
- **Wowza**: `rtmp://server:1935/live`
- **Restream.io**: `rtmp://live.restream.io/live`

## Virtual Camera

The OBS Virtual Camera creates a virtual webcam device that can be used in video conferencing applications.

### Platform Support

| Platform | Technology | Status |
|----------|-----------|--------|
| **Windows** | DirectShow | ✅ Supported |
| **macOS** | CoreMediaIO | ✅ Supported |
| **Linux** | v4l2loopback | ✅ Supported (requires setup) |

### Linux Setup (v4l2loopback)

```bash
# Install v4l2loopback
sudo apt-get install v4l2loopback-dkms

# Load module
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="OBS Virtual Camera" exclusive_caps=1

# Make persistent (add to /etc/modules)
echo "v4l2loopback" | sudo tee -a /etc/modules
```

### Using Virtual Camera

```python
# Start virtual camera
controller.start_virtual_camera()

# Now available in:
# - Zoom: Camera → OBS Virtual Camera
# - Google Meet: Settings → Video → OBS Virtual Camera
# - Discord: Voice & Video → Camera → OBS Virtual Camera
# - Microsoft Teams: Settings → Devices → Camera → OBS Virtual Camera

# Check status
status = controller.get_virtual_camera_status()
print(f"Virtual Camera Active: {status['active']}")

# Stop virtual camera
controller.stop_virtual_camera()
```

### Virtual Camera vs Physical Camera

**When to use Virtual Camera:**
- Broadcasting with OBS scenes (overlays, lower thirds, multiple sources)
- Screen sharing with webcam overlay
- Advanced video effects (chroma key, filters, color correction)
- Multi-source composition (webcam + screen + images)

**When to use Physical Camera:**
- Simple webcam calls with no effects needed
- Lower latency requirements
- Reduced CPU usage

## Recording

### Start Recording

```python
# Start recording (OBS uses default filename pattern)
controller.start_recording(format="mp4")

# Or specify custom filename
controller.start_recording(
    filename="meeting_2024-01-15.mp4",
    format="mp4"
)
```

### Recording Formats

| Format | Pros | Cons | Use Case |
|--------|------|------|----------|
| **MP4** | Universal compatibility, small file size | Can corrupt if OBS crashes | Final recordings for sharing |
| **MKV** | Crash-resistant, remuxable to MP4 | Less compatible | Long recordings, safety first |
| **FLV** | Streaming-optimized | Limited compatibility | Archive streaming sessions |
| **MOV** | High quality, Apple ecosystem | Large file size | Professional editing |

**Recommendation:** Use **MKV** for recording, then remux to MP4 after:
```bash
# Remux MKV to MP4 in OBS
# File → Remux Recordings → Select MKV → Remux
```

### Pause and Resume

```python
# Start recording
controller.start_recording(format="mkv")

# Pause recording (useful for breaks)
controller.pause_recording()

# Resume recording
controller.resume_recording()

# Stop and finalize
result = controller.stop_recording()
print(f"Recording saved to: {result['output_path']}")
```

### Multi-Track Audio Recording

Configure in OBS before starting:

1. **Settings → Output → Recording**
2. Enable **Advanced** mode
3. Set **Audio Tracks** (up to 6 tracks)
4. Format must be **MKV** (MP4 only supports 1 track)

**Track Configuration Example:**
- Track 1: Desktop Audio (game/system sounds)
- Track 2: Microphone
- Track 3: Discord/Zoom audio
- Track 4: Music

### Recording Status and Statistics

```python
# Get recording status
status = controller.get_record_status()

print(f"""
Recording: {status['recording']}
Paused: {status['paused']}
Duration: {status['timecode']}
File Size: {status['bytes'] / 1024 / 1024:.2f} MB
""")
```

## Stream Health Monitoring

### Real-Time Statistics

```python
# Get stream status
status = controller.get_stream_status()

print(f"""
Streaming: {status['streaming']}
Bitrate: {status['kbits_per_sec']} kbps
Duration: {status['duration_ms'] / 1000:.0f} seconds
Bytes Sent: {status['bytes_sent'] / 1024 / 1024:.2f} MB
Dropped Frames: {status['output_skipped_frames']} / {status['output_total_frames']}
Congestion: {status['congestion']:.2%}
""")
```

### OBS Performance Stats

```python
# Get OBS performance statistics
stats = controller.get_stats()

print(f"""
CPU Usage: {stats['cpu_usage']:.1f}%
Memory: {stats['memory_usage_mb']:.0f} MB
Render FPS: {stats['render_fps']:.1f}
Output FPS: {stats['output_fps']:.1f}
Free Disk Space: {stats['free_disk_space_mb']} MB
""")
```

### Health Check Example

```python
def check_stream_health(controller):
    """Check if stream is healthy"""
    status = controller.get_stream_status()
    stats = controller.get_stats()

    issues = []

    # Check dropped frames
    if status['output_total_frames'] > 0:
        drop_rate = status['output_skipped_frames'] / status['output_total_frames']
        if drop_rate > 0.01:  # More than 1% dropped
            issues.append(f"High frame drop rate: {drop_rate:.2%}")

    # Check CPU usage
    if stats['cpu_usage'] > 80:
        issues.append(f"High CPU usage: {stats['cpu_usage']:.1f}%")

    # Check congestion
    if status['congestion'] > 0.5:
        issues.append(f"Network congestion: {status['congestion']:.2%}")

    # Check bitrate
    if status['kbits_per_sec'] < 1000:
        issues.append(f"Low bitrate: {status['kbits_per_sec']} kbps")

    return {
        'healthy': len(issues) == 0,
        'issues': issues,
        'status': status,
        'stats': stats
    }
```

## IF.witness Provenance Tracking

All OBS operations are logged to the IF.witness hash chain for provenance tracking.

### Logged Events

- `obs_connected`: OBS WebSocket connection established
- `stream_started`: Streaming started with destination
- `stream_stopped`: Streaming stopped with final statistics
- `virtualcam_started`: Virtual camera activated
- `virtualcam_stopped`: Virtual camera deactivated
- `recording_started`: Recording started
- `recording_paused`: Recording paused
- `recording_resumed`: Recording resumed
- `recording_stopped`: Recording stopped with file path
- `emergency_stop_all`: Emergency stop triggered

### Accessing Witness Chain

```python
# Get complete event chain
chain = controller.get_witness_chain()

for event in chain:
    print(f"{event['timestamp']}: {event['event_type']}")
    print(f"  Hash: {event['hash'][:16]}...")
    print(f"  Params: {event['params']}")
    print(f"  Result: {event['result']}")
```

### Verify Hash Chain Integrity

```python
# Verify chain has not been tampered with
is_valid = controller.verify_witness_chain()
print(f"Chain integrity: {'✅ VALID' if is_valid else '❌ INVALID'}")
```

### Export Witness Report

```python
# Export complete provenance report
controller.export_witness_report('/path/to/report.json')
```

**Report Structure:**
```json
{
  "chain": [
    {
      "timestamp": "2024-01-15T10:30:00.000000",
      "event_type": "stream_started",
      "params": {"service": "Twitch", "key": "[REDACTED]"},
      "result": {"status": "started", "streaming": true},
      "prev_hash": "0000...",
      "hash": "a3f4..."
    }
  ],
  "verified": true,
  "timestamp": "2024-01-15T11:00:00.000000"
}
```

## Error Handling

### Connection Errors

```python
from src.integrations.obs_streaming import OBSConnectionError

try:
    controller.connect()
except OBSConnectionError as e:
    print(f"Failed to connect: {e}")
    # Check:
    # 1. Is OBS running?
    # 2. Is WebSocket server enabled?
    # 3. Correct port (4455)?
    # 4. Correct password?
```

### Streaming Errors

```python
from src.integrations.obs_streaming import OBSStreamingError

try:
    controller.start_stream(service="Twitch", key="invalid-key")
except OBSStreamingError as e:
    print(f"Stream failed: {e}")
    # Check:
    # 1. Valid stream key?
    # 2. Stream settings configured in OBS?
    # 3. Network connection stable?
```

### Graceful Error Handling

```python
# Emergency stop all outputs
try:
    results = controller.stop_all()
    print(f"Stopped: {results}")
except Exception as e:
    print(f"Failed to stop: {e}")
finally:
    controller.disconnect()
```

## Advanced Usage

### Event Callbacks

```python
def on_stream_started(result):
    print(f"Stream started at {result['timestamp']}")
    # Send notification, update database, etc.

def on_stream_stopped(result):
    print(f"Stream stopped. Stats: {result['final_stats']}")
    # Log analytics, send summary email, etc.

controller.on_stream_started(on_stream_started)
controller.on_stream_stopped(on_stream_stopped)
```

### Automated Stream Health Monitoring

```python
import threading
import time

def monitor_stream(controller, interval=5):
    """Monitor stream health in background"""
    while controller.get_stream_status()['streaming']:
        health = check_stream_health(controller)

        if not health['healthy']:
            print("⚠️ STREAM ISSUES DETECTED:")
            for issue in health['issues']:
                print(f"  - {issue}")

        time.sleep(interval)

# Start monitoring in background thread
controller.start_stream(service="Twitch", key="...")
monitor_thread = threading.Thread(target=monitor_stream, args=(controller,))
monitor_thread.start()
```

### Multi-Destination Streaming

OBS natively supports only one stream destination. For multi-streaming:

**Option 1: Use Restream.io**
```python
controller.start_stream(
    service="Custom",
    server="rtmp://live.restream.io/live",
    key="your-restream-key"
)
# Configure destinations in Restream.io dashboard
```

**Option 2: Multiple OBS Instances**
```python
# Instance 1: Twitch
controller1 = OBSStreamingController(port=4455)
controller1.connect()
controller1.start_stream(service="Twitch", key="...")

# Instance 2: YouTube
controller2 = OBSStreamingController(port=4456)
controller2.connect()
controller2.start_stream(service="YouTube", key="...")
```

## Troubleshooting

### OBS Connection Fails

**Problem:** `OBSConnectionError: Connection refused`

**Solutions:**
1. Verify OBS is running
2. Check WebSocket server is enabled: Tools → WebSocket Server Settings
3. Verify port: Default is 4455
4. Check firewall: Allow port 4455
5. Test connection:
   ```bash
   # Linux/Mac
   nc -zv localhost 4455

   # Windows PowerShell
   Test-NetConnection -ComputerName localhost -Port 4455
   ```

### Authentication Fails

**Problem:** `OBSConnectionError: Authentication failed`

**Solutions:**
1. Check password is correct
2. Try with `obs_password=None` if auth is disabled
3. Disable authentication in OBS to test
4. Re-enable and set new password

### Stream Won't Start

**Problem:** `OBSStreamingError: Failed to start stream`

**Solutions:**
1. Verify stream key is correct
2. Check OBS streaming settings: Settings → Stream
3. Test stream manually in OBS first
4. Check network connection
5. Verify service is correct ("Twitch" vs "Twitch.tv")

### Virtual Camera Not Available

**Problem:** Virtual camera not showing in Zoom/Meet

**Solutions:**

**Windows:**
1. Restart OBS as Administrator
2. Tools → VirtualCam → Start
3. Restart video conferencing app

**macOS:**
1. Install OBS Virtual Camera plugin (included in OBS 26.1+)
2. System Preferences → Security & Privacy → Camera → Allow access
3. Restart video app

**Linux:**
1. Install v4l2loopback: `sudo apt install v4l2loopback-dkms`
2. Load module: `sudo modprobe v4l2loopback`
3. Start virtual camera in OBS
4. Check device: `ls /dev/video*`

### High CPU Usage

**Problem:** OBS using 80%+ CPU, stream lagging

**Solutions:**
1. Lower resolution: Settings → Video → Output Resolution
2. Change encoder: Settings → Output → Encoder
   - Try **Hardware** encoders: NVENC (NVIDIA), QuickSync (Intel), AMF (AMD)
   - Software (x264) is CPU-intensive but high quality
3. Lower bitrate: Settings → Output → Bitrate
4. Reduce FPS: Settings → Video → FPS → 30 instead of 60
5. Disable preview: Right-click preview → Disable Preview

### Dropped Frames

**Problem:** `output_skipped_frames` increasing rapidly

**Solutions:**
1. **Network Issues:**
   - Check upload speed: https://speedtest.net
   - Required: 1.5x your bitrate (e.g., 6 Mbps for 4000 kbps stream)
   - Close bandwidth-heavy apps (downloads, uploads)
2. **CPU Overload:**
   - Lower encoder preset: Settings → Output → Encoder Preset → "veryfast"
   - Use hardware encoder (NVENC, QuickSync)
3. **Disk Issues (Recording):**
   - Record to SSD, not HDD
   - Check disk space
   - Use MKV format (more resilient)

### Recording File Corrupted

**Problem:** MP4 recording won't play after OBS crash

**Solutions:**
1. **Prevention:** Always use MKV format for long recordings
2. **Recovery:** Use VLC to recover
   ```
   vlc corrupted.mp4 --sout='#standard{access=file,mux=mp4,dst=recovered.mp4}'
   ```
3. **Future:** Settings → Output → Recording Format → MKV
4. **Remux after:** File → Remux Recordings → Convert MKV to MP4

## Performance Optimization

### Recommended Stream Settings

| Resolution | FPS | Bitrate | Encoder | Use Case |
|------------|-----|---------|---------|----------|
| 1920x1080 | 60 | 6000 kbps | NVENC/QuickSync | Gaming, high motion |
| 1920x1080 | 30 | 4500 kbps | x264/NVENC | Talk shows, low motion |
| 1280x720 | 60 | 4500 kbps | NVENC | Gaming, lower quality |
| 1280x720 | 30 | 3000 kbps | x264 | Standard streaming |
| 854x480 | 30 | 1500 kbps | x264 | Low bandwidth |

### Encoder Comparison

| Encoder | Quality | CPU Usage | GPU Usage | Latency | Notes |
|---------|---------|-----------|-----------|---------|-------|
| **x264** | ⭐⭐⭐⭐⭐ | 🔥🔥🔥🔥 | - | Medium | Best quality, high CPU |
| **NVENC** (NVIDIA) | ⭐⭐⭐⭐ | 🔥 | 🔥🔥 | Low | Excellent, requires NVIDIA GPU |
| **QuickSync** (Intel) | ⭐⭐⭐ | 🔥 | 🔥🔥 | Low | Good, built into Intel CPUs |
| **AMF** (AMD) | ⭐⭐⭐ | 🔥 | 🔥🔥 | Low | Good, requires AMD GPU |

**Recommendation:** Use hardware encoder (NVENC/QuickSync/AMF) for streaming, x264 for local recording.

## API Reference

### OBSStreamingController

#### Constructor

```python
controller = OBSStreamingController(
    obs_host: str = "localhost",
    obs_port: int = 4455,
    obs_password: Optional[str] = None,
    witness_logger: Optional[IFWitnessLogger] = None
)
```

#### Connection Methods

- `connect() -> Dict`: Connect to OBS WebSocket
- `disconnect() -> Dict`: Disconnect from OBS
- `stop_all() -> Dict`: Emergency stop all outputs

#### Streaming Methods

- `start_stream(service, server, key) -> Dict`: Start streaming
- `stop_stream() -> Dict`: Stop streaming
- `get_stream_status() -> Dict`: Get stream statistics

#### Virtual Camera Methods

- `start_virtual_camera() -> Dict`: Start virtual camera
- `stop_virtual_camera() -> Dict`: Stop virtual camera
- `get_virtual_camera_status() -> Dict`: Get virtual camera status

#### Recording Methods

- `start_recording(filename, format) -> Dict`: Start recording
- `stop_recording() -> Dict`: Stop recording
- `pause_recording() -> Dict`: Pause recording
- `resume_recording() -> Dict`: Resume recording
- `get_record_status() -> Dict`: Get recording status

#### Statistics Methods

- `get_stats() -> Dict`: Get OBS performance stats

#### IF.witness Methods

- `log_to_witness(event_type, params, result) -> str`: Log event
- `get_witness_chain() -> list`: Get event chain
- `verify_witness_chain() -> bool`: Verify chain integrity
- `export_witness_report(filepath)`: Export report

#### Callbacks

- `on_stream_started(callback)`: Register stream started callback
- `on_stream_stopped(callback)`: Register stream stopped callback
- `on_recording_started(callback)`: Register recording started callback

## Examples

### Complete Streaming Session

```python
from src.integrations.obs_streaming import OBSStreamingController
import time

# Initialize
controller = OBSStreamingController(
    obs_host="localhost",
    obs_port=4455,
    obs_password=None
)

# Connect
print("Connecting to OBS...")
conn_result = controller.connect()
print(f"Connected: OBS {conn_result['obs_version']}")

# Start streaming
print("Starting stream to Twitch...")
controller.start_stream(
    service="Twitch",
    key="live_123456789_abcdefghijklmnop"
)

# Monitor for 5 minutes
print("Monitoring stream...")
for i in range(60):  # 5 minutes
    status = controller.get_stream_status()
    stats = controller.get_stats()

    print(f"[{i*5}s] Bitrate: {status['kbits_per_sec']} kbps | "
          f"Dropped: {status['output_skipped_frames']} | "
          f"CPU: {stats['cpu_usage']:.1f}%")

    time.sleep(5)

# Stop streaming
print("Stopping stream...")
result = controller.stop_stream()
print(f"Stream stopped. Total frames: {result['final_stats']['output_total_frames']}")

# Export provenance report
controller.export_witness_report('stream_report.json')
print("Provenance report saved to stream_report.json")

# Disconnect
controller.disconnect()
print("Disconnected from OBS")
```

### Automated Recording with Health Checks

```python
from src.integrations.obs_streaming import OBSStreamingController
import time
import threading

def health_monitor(controller, stop_event):
    """Monitor and log health issues"""
    while not stop_event.is_set():
        stats = controller.get_stats()

        if stats['cpu_usage'] > 80:
            print(f"⚠️ HIGH CPU: {stats['cpu_usage']:.1f}%")

        if stats['free_disk_space_mb'] < 1000:
            print(f"⚠️ LOW DISK SPACE: {stats['free_disk_space_mb']} MB")
            controller.pause_recording()
            print("Recording paused due to low disk space!")
            break

        time.sleep(10)

# Setup
controller = OBSStreamingController()
controller.connect()

# Start recording
controller.start_recording(
    filename=f"recording_{int(time.time())}.mkv",
    format="mkv"
)

# Start health monitoring
stop_monitoring = threading.Event()
monitor_thread = threading.Thread(target=health_monitor, args=(controller, stop_monitoring))
monitor_thread.start()

# Record for 1 hour or until interrupted
try:
    time.sleep(3600)
except KeyboardInterrupt:
    print("Recording interrupted by user")

# Stop monitoring and recording
stop_monitoring.set()
monitor_thread.join()

result = controller.stop_recording()
print(f"Recording saved: {result.get('output_path', 'Unknown')}")

controller.disconnect()
```

## Integration with InfraFabric

### WebRTC Integration

The OBS Virtual Camera can be used as a WebRTC source:

```python
# Start OBS virtual camera
obs_controller.start_virtual_camera()

# Use in WebRTC connection
# The virtual camera appears as "OBS Virtual Camera" device
# Compatible with browser WebRTC APIs (getUserMedia)
```

### IF.bus Integration

Stream events can be published to IF.bus:

```python
from src.integrations.obs_streaming import OBSStreamingController
# from src.bus.if_bus import IFBus  # When available

obs = OBSStreamingController()

def on_stream_started(result):
    # Publish to IF.bus
    # bus.publish('obs.stream.started', result)
    print(f"Stream started event: {result}")

obs.on_stream_started(on_stream_started)
```

## References

- **OBS WebSocket Protocol**: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
- **obs-websocket-py Client**: https://github.com/obsproject/obs-websocket-py
- **OBS Studio**: https://obsproject.com/
- **OBS Forums**: https://obsproject.com/forum/
- **Streaming Services**:
  - Twitch: https://stream.twitch.tv/
  - YouTube: https://support.google.com/youtube/answer/2907883
  - Facebook: https://www.facebook.com/formedia/tools/facebook-live

## License

This integration is part of InfraFabric and follows the project's license.

## Support

For issues with:
- **OBS Integration Code**: Open issue in InfraFabric repository
- **OBS Studio**: https://obsproject.com/forum/
- **obs-websocket**: https://github.com/obsproject/obs-websocket/issues
