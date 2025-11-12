# IF.obs CLI Interface

Dead-simple command-line interface for OBS Studio control via WebSocket.

## Overview

IF.obs provides comprehensive OBS Studio control through a clean CLI interface. All operations are logged to IF.witness for complete audit trails.

## Prerequisites

1. **OBS Studio** with obs-websocket plugin (v5.x)
   - Download: https://obsproject.com/
   - obs-websocket v5 is included in OBS Studio 28+ by default
   - Port: 4455 (default)

2. **Python Dependencies**
   ```bash
   pip install obs-websocket-py
   ```

3. **Enable WebSocket in OBS**
   - Tools → WebSocket Server Settings
   - Enable WebSocket server
   - Set password (recommended)
   - Note the port (default: 4455)

## Installation

```bash
# Install IF.obs
pip install -e .

# Verify installation
if-obs --help
```

## Quick Start

```bash
# Add OBS instance
if-obs add myobs --host localhost --port 4455 --password secret123

# Test connection
if-obs test myobs

# List scenes
if-obs scene list myobs

# Switch to a scene
if-obs scene switch myobs --scene "Gaming Scene"

# Start streaming
if-obs stream start myobs

# Get status
if-obs status myobs
```

## Command Reference

### 1. Connection Management

#### Add Instance
```bash
if-obs add <name> --host <host> --port <port> --password <password>
```

Examples:
```bash
# Local OBS with password
if-obs add local --host localhost --port 4455 --password secret123

# Remote OBS without password
if-obs add studio --host 192.168.1.100 --port 4455
```

#### List Instances
```bash
if-obs list [--format text|json]
```

Examples:
```bash
if-obs list
if-obs list --format json
```

#### Test Connection
```bash
if-obs test <instance>
```

Examples:
```bash
if-obs test myobs
```

#### Remove Instance
```bash
if-obs remove <instance>
```

Examples:
```bash
if-obs remove myobs
```

### 2. Scene Management

#### List Scenes
```bash
if-obs scene list <instance> [--format text|json]
```

Examples:
```bash
if-obs scene list myobs
if-obs scene list myobs --format json
```

#### Switch Scene
```bash
if-obs scene switch <instance> --scene <scene-name>
```

Examples:
```bash
if-obs scene switch myobs --scene "Gaming Scene"
if-obs scene switch myobs --scene "BRB Screen"
```

#### Create Scene
```bash
if-obs scene create <instance> --scene <scene-name>
```

Examples:
```bash
if-obs scene create myobs --scene "New Scene"
```

#### Remove Scene
```bash
if-obs scene remove <instance> --scene <scene-name>
```

Examples:
```bash
if-obs scene remove myobs --scene "Old Scene"
```

#### Get Current Scene
```bash
if-obs scene current <instance>
```

Examples:
```bash
if-obs scene current myobs
```

### 3. Source Management

#### List Sources
```bash
if-obs source list <instance> --scene <scene-name> [--format text|json]
```

Examples:
```bash
if-obs source list myobs --scene "Gaming Scene"
if-obs source list myobs --scene "Gaming Scene" --format json
```

#### Add Source
```bash
if-obs source add <instance> --scene <scene> --source <name> --type <type> [--ndi-name <ndi-source>]
```

Supported types:
- `camera` / `webcam` - V4L2 camera input (Linux)
- `ndi` - NDI source
- `media` / `video` - Media file
- `image` - Image file
- `browser` - Browser source
- `text` - Text source
- `color` - Color source

Examples:
```bash
# Add webcam
if-obs source add myobs --scene "Gaming" --source "Webcam" --type camera

# Add NDI source
if-obs source add myobs --scene "Gaming" --source "NDI Input" --type ndi --ndi-name "CAMERA1 (OBS)"

# Add media file
if-obs source add myobs --scene "Gaming" --source "Video" --type media
```

#### Show/Hide Source
```bash
if-obs source show <instance> --scene <scene> --source <source>
if-obs source hide <instance> --scene <scene> --source <source>
```

Examples:
```bash
if-obs source show myobs --scene "Gaming" --source "Webcam"
if-obs source hide myobs --scene "Gaming" --source "Webcam"
```

#### Remove Source
```bash
if-obs source remove <instance> --scene <scene> --source <source>
```

Examples:
```bash
if-obs source remove myobs --scene "Gaming" --source "Webcam"
```

### 4. Streaming Control

#### Start Streaming
```bash
if-obs stream start <instance>
```

Examples:
```bash
if-obs stream start myobs
```

**Note:** Stream destination must be configured in OBS Studio settings beforehand.

#### Stop Streaming
```bash
if-obs stream stop <instance>
```

Examples:
```bash
if-obs stream stop myobs
```

#### Stream Status
```bash
if-obs stream status <instance> [--format text|json]
```

Examples:
```bash
if-obs stream status myobs
if-obs stream status myobs --format json
```

### 5. Recording Control

#### Start Recording
```bash
if-obs record start <instance> [--file <filename>]
```

Examples:
```bash
if-obs record start myobs
if-obs record start myobs --file output.mp4
```

**Note:** Output path must be configured in OBS Studio settings.

#### Stop Recording
```bash
if-obs record stop <instance>
```

Examples:
```bash
if-obs record stop myobs
```

#### Record Status
```bash
if-obs record status <instance> [--format text|json]
```

Examples:
```bash
if-obs record status myobs
if-obs record status myobs --format json
```

### 6. Virtual Camera

#### Start Virtual Camera
```bash
if-obs virtualcam start <instance>
```

Examples:
```bash
if-obs virtualcam start myobs
```

#### Stop Virtual Camera
```bash
if-obs virtualcam stop <instance>
```

Examples:
```bash
if-obs virtualcam stop myobs
```

### 7. Filter Management

#### List Filters
```bash
if-obs filter list <instance> --source <source> [--format text|json]
```

Examples:
```bash
if-obs filter list myobs --source "Webcam"
if-obs filter list myobs --source "Webcam" --format json
```

#### Add Filter
```bash
if-obs filter add <instance> --source <source> --filter <name> --type <type>
```

Supported types:
- `chroma_key` - Chroma key (green screen)
- `color_correction` - Color correction
- `sharpness` - Sharpness filter
- `lut` - LUT filter
- `noise_reduction` - Noise reduction
- `gain` - Audio gain

Examples:
```bash
if-obs filter add myobs --source "Webcam" --filter "Chroma Key" --type chroma_key
if-obs filter add myobs --source "Webcam" --filter "Color Fix" --type color_correction
```

#### Remove Filter
```bash
if-obs filter remove <instance> --source <source> --filter <filter>
```

Examples:
```bash
if-obs filter remove myobs --source "Webcam" --filter "Chroma Key"
```

### 8. Media Control

#### Add Media Source
```bash
if-obs media add <instance> --scene <scene> --source <name> --file <path> [--loop]
```

Examples:
```bash
if-obs media add myobs --scene "Gaming" --source "Video" --file /path/to/video.mp4
if-obs media add myobs --scene "Gaming" --source "Video" --file /path/to/video.mp4 --loop
```

#### Play/Pause/Stop Media
```bash
if-obs media play <instance> --source <source>
if-obs media pause <instance> --source <source>
if-obs media stop <instance> --source <source>
```

Examples:
```bash
if-obs media play myobs --source "Video"
if-obs media pause myobs --source "Video"
if-obs media stop myobs --source "Video"
```

### 9. Browser Sources

#### Add Browser Source
```bash
if-obs browser add <instance> --scene <scene> --source <name> --url <url> [--width <w>] [--height <h>]
```

Examples:
```bash
if-obs browser add myobs --scene "Gaming" --source "Overlay" \
    --url "https://example.com/overlay.html" \
    --width 1920 --height 1080

if-obs browser add myobs --scene "Chat" --source "Twitch Chat" \
    --url "https://twitch.tv/popout/channel/chat" \
    --width 400 --height 800
```

### 10. Status & Statistics

#### Get Status
```bash
if-obs status <instance> [--format text|json]
```

Examples:
```bash
if-obs status myobs
if-obs status myobs --format json
```

#### Get Performance Stats
```bash
if-obs stats <instance> [--format text|json]
```

Examples:
```bash
if-obs stats myobs
if-obs stats myobs --format json
```

Output includes:
- CPU usage
- Memory usage
- FPS
- Frame render time
- Dropped frames (rendering)
- Dropped frames (encoding)

#### Get Version
```bash
if-obs version <instance> [--format text|json]
```

Examples:
```bash
if-obs version myobs
if-obs version myobs --format json
```

## Configuration

### Config File Location
```
~/.if/obs/instances.yaml
```

### Config Format
```yaml
instances:
  myobs:
    host: localhost
    port: 4455
    password: <base64-encoded>
    added_at: 2025-11-12T00:00:00Z
  studio:
    host: 192.168.1.100
    port: 4455
    added_at: 2025-11-12T01:00:00Z
```

**Note:** Passwords are base64-encoded for basic obfuscation. For production use, consider using environment variables or a secrets manager.

## IF.witness Integration

All operations are automatically logged to IF.witness:

```bash
# View recent OBS operations
if-witness export --format json | grep obs_

# Trace specific operation
if-witness trace --trace-id obs-myobs-<uuid>
```

Logged events include:
- `obs_add_instance` - Instance added
- `obs_remove_instance` - Instance removed
- `obs_test_connection` - Connection tested
- `obs_scene_switch` - Scene switched
- `obs_scene_create` - Scene created
- `obs_scene_remove` - Scene removed
- `obs_source_add` - Source added
- `obs_source_show` - Source shown
- `obs_source_hide` - Source hidden
- `obs_source_remove` - Source removed
- `obs_stream_start` - Streaming started
- `obs_stream_stop` - Streaming stopped
- `obs_record_start` - Recording started
- `obs_record_stop` - Recording stopped
- `obs_virtualcam_start` - Virtual camera started
- `obs_virtualcam_stop` - Virtual camera stopped
- `obs_filter_add` - Filter added
- `obs_filter_remove` - Filter removed
- `obs_media_add` - Media source added
- `obs_media_play` - Media playback started
- `obs_media_pause` - Media paused
- `obs_media_stop` - Media stopped
- `obs_browser_add` - Browser source added

## Automation Examples

### Streaming Workflow
```bash
#!/bin/bash
# Start streaming workflow

# Switch to starting scene
if-obs scene switch myobs --scene "Starting Soon"

# Start streaming
if-obs stream start myobs

# Wait 30 seconds
sleep 30

# Switch to main scene
if-obs scene switch myobs --scene "Gaming Scene"

# Show webcam
if-obs source show myobs --scene "Gaming Scene" --source "Webcam"
```

### Recording Automation
```bash
#!/bin/bash
# Automated recording

# Start recording
if-obs record start myobs --file session_$(date +%Y%m%d_%H%M%S).mp4

# Record for 1 hour
sleep 3600

# Stop recording
if-obs record stop myobs
```

### Scene Rotation
```bash
#!/bin/bash
# Rotate through scenes

scenes=("Scene 1" "Scene 2" "Scene 3")

for scene in "${scenes[@]}"; do
    if-obs scene switch myobs --scene "$scene"
    sleep 10
done
```

## Troubleshooting

### Connection Issues

1. **Check OBS WebSocket is enabled**
   ```
   Tools → WebSocket Server Settings → Enable
   ```

2. **Verify port is correct**
   ```bash
   if-obs test myobs
   ```

3. **Check firewall**
   ```bash
   # Allow port 4455
   sudo ufw allow 4455/tcp
   ```

### Common Errors

**"Cannot connect to OBS"**
- OBS Studio is not running
- WebSocket server is disabled
- Incorrect host/port
- Firewall blocking connection

**"obs-websocket-py is not installed"**
```bash
pip install obs-websocket-py
```

**"Instance not found"**
```bash
# List configured instances
if-obs list

# Add instance
if-obs add myobs --host localhost --port 4455
```

**"Scene not found"**
```bash
# List available scenes
if-obs scene list myobs
```

## Performance Monitoring

Use the stats command to monitor OBS performance:

```bash
# Check for dropped frames
if-obs stats myobs

# Watch stats in real-time (requires watch)
watch -n 1 'if-obs stats myobs'

# Log stats to file
if-obs stats myobs --format json >> obs-stats.log
```

Key metrics to watch:
- **CPU Usage**: Should stay below 80% for stable streaming
- **FPS**: Should match your target framerate
- **Render Skip Rate**: Should be < 0.1%
- **Output Skip Rate**: Should be < 0.1%

## Best Practices

1. **Test connections before going live**
   ```bash
   if-obs test myobs
   if-obs status myobs
   ```

2. **Use named scenes for clarity**
   ```bash
   if-obs scene create myobs --scene "Starting Soon"
   if-obs scene create myobs --scene "Main Show"
   if-obs scene create myobs --scene "BRB"
   if-obs scene create myobs --scene "Ending"
   ```

3. **Monitor performance during streams**
   ```bash
   if-obs stats myobs
   ```

4. **Use JSON output for scripting**
   ```bash
   if-obs status myobs --format json | jq '.streaming.active'
   ```

5. **Automate repetitive tasks**
   - Create shell scripts for common workflows
   - Use cron jobs for scheduled recordings
   - Integrate with stream deck software

## Integration with Other Tools

### Stream Deck Integration
```bash
# Configure Stream Deck buttons to run if-obs commands
# Button 1: Start stream
if-obs stream start myobs

# Button 2: Switch to gaming scene
if-obs scene switch myobs --scene "Gaming"
```

### Monitoring Integration
```bash
# Export IF.witness logs to monitoring system
if-witness export --format json | \
    grep obs_stream_start | \
    your-monitoring-tool
```

### CI/CD Integration
```bash
# Automated testing in CI
if-obs test myobs
if-obs scene list myobs
if-obs status myobs --format json
```

## Support

- **OBS WebSocket Protocol**: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
- **OBS Forums**: https://obsproject.com/forum/
- **InfraFabric Docs**: https://github.com/dannystocker/infrafabric

## License

MIT License - see LICENSE file for details
