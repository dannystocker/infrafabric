# IF.vmix CLI Interface

**Dead-simple command-line control for vMix professional video production**

IF.vmix provides a complete CLI interface for controlling vMix live video production software, with built-in IF.witness logging for audit trails.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Command Reference](#command-reference)
5. [IF.witness Integration](#ifwitness-integration)
6. [Shell Completion](#shell-completion)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)

---

## Quick Start

**Get up and running in 5 minutes:**

```bash
# 1. Add your vMix instance
if vmix add myvmix --host 192.168.1.100 --port 8088

# 2. Test connection
if vmix test myvmix

# 3. Control production
if vmix cut myvmix --input 1           # Instant cut to input 1
if vmix fade myvmix --input 2          # Fade to input 2
if vmix preview myvmix --input 3       # Set preview to input 3

# 4. Check status
if vmix status myvmix
if vmix inputs myvmix
```

**That's it!** Every operation is logged to IF.witness for audit trails.

---

## Installation

### Prerequisites

- Python 3.10 or higher
- vMix 25.0 or higher (with API enabled)
- Network access to vMix host

### Install IF.vmix

```bash
# Clone repository
git clone https://github.com/yourorg/infrafabric
cd infrafabric

# Install dependencies
pip install -r requirements.txt

# Install CLI
pip install -e .

# Verify installation
if vmix --help
```

### Enable vMix API

1. Open vMix
2. Go to **Settings** → **Web Controller**
3. Enable **Web Controller**
4. Note the port (default: 8088)
5. Ensure firewall allows access to port 8088

---

## Configuration

### Instance Management

IF.vmix stores instance configurations in `~/.if/vmix/instances.yaml`.

**Add instance:**
```bash
if vmix add myvmix --host 192.168.1.100 --port 8088
```

**List instances:**
```bash
if vmix list

# Output:
Configured vMix Instances (2)

Name                 Host                 Port       Added
---------------------------------------------------------------------------
myvmix               192.168.1.100        8088       2025-11-11T23:00:00
studio2              192.168.1.101        8088       2025-11-11T22:00:00
```

**Test connection:**
```bash
if vmix test myvmix

# Output:
Testing connection to 192.168.1.100:8088...
✓ Connection successful
  Version: 25.0.0.65
  Edition: 4K
  Inputs: 8
  Active: Input 1
  Preview: Input 2
```

**Remove instance:**
```bash
if vmix remove myvmix
```

---

## Command Reference

### Connection Management

#### `add` - Add vMix instance
```bash
if vmix add <name> --host <ip> [--port <port>]
```

**Parameters:**
- `name` - Unique instance name
- `--host` - vMix host IP or hostname (required)
- `--port` - API port (default: 8088)

**Example:**
```bash
if vmix add studio1 --host 192.168.1.100 --port 8088
```

#### `list` - List instances
```bash
if vmix list [--format text|json]
```

**Example:**
```bash
if vmix list --format json
```

#### `test` - Test connection
```bash
if vmix test <instance>
```

**Example:**
```bash
if vmix test studio1
```

#### `remove` - Remove instance
```bash
if vmix remove <instance>
```

**Example:**
```bash
if vmix remove studio1
```

---

### Production Control

#### `cut` - Instant cut to input
```bash
if vmix cut <instance> --input <number>
```

**Example:**
```bash
if vmix cut myvmix --input 1
```

#### `fade` - Fade to input
```bash
if vmix fade <instance> --input <number> [--duration <ms>]
```

**Parameters:**
- `--duration` - Fade duration in milliseconds (default: 1000)

**Example:**
```bash
if vmix fade myvmix --input 2 --duration 2000
```

#### `preview` - Set preview input
```bash
if vmix preview <instance> --input <number>
```

**Example:**
```bash
if vmix preview myvmix --input 3
```

#### `transition` - Custom transition
```bash
if vmix transition <instance> --type <type> [--duration <ms>] [--input <number>]
```

**Parameters:**
- `--type` - Transition type: Fade, Merge, Wipe, Zoom, Stinger
- `--duration` - Duration in milliseconds (default: 1000)
- `--input` - Input number (optional, uses preview if not specified)

**Example:**
```bash
if vmix transition myvmix --type Merge --duration 1000
if vmix transition myvmix --type Wipe --duration 500 --input 4
```

#### `overlay` - Set overlay input
```bash
if vmix overlay <instance> --num <1-4> --input <number> [--action <action>]
```

**Parameters:**
- `--num` - Overlay number (1-4)
- `--input` - Input number
- `--action` - Overlay action: OverlayInput, OverlayInputIn, OverlayInputOut

**Example:**
```bash
if vmix overlay myvmix --num 1 --input 4
if vmix overlay myvmix --num 2 --input 5 --action OverlayInputIn
```

---

### NDI Control

#### `ndi add` - Add NDI input source
```bash
if vmix ndi add <instance> --source "<source-name>"
```

**Example:**
```bash
if vmix ndi add myvmix --source "Camera 1 (192.168.1.50)"
```

#### `ndi list` - List NDI inputs
```bash
if vmix ndi list <instance> [--format text|json]
```

**Example:**
```bash
if vmix ndi list myvmix
```

#### `ndi remove` - Remove NDI input
```bash
if vmix ndi remove <instance> --input <number>
```

**Example:**
```bash
if vmix ndi remove myvmix --input 5
```

---

### Streaming Control

#### `stream start` - Start streaming
```bash
if vmix stream start <instance> [--rtmp <url>] [--key <key>] [--channel <0-2>]
```

**Parameters:**
- `--rtmp` - RTMP URL (e.g., rtmp://server/live)
- `--key` - Stream key
- `--channel` - Stream channel (0-2, default: 0)

**Example:**
```bash
# Start with pre-configured stream
if vmix stream start myvmix

# Start with custom RTMP URL
if vmix stream start myvmix --rtmp rtmp://live.example.com/live --key abc123
```

#### `stream stop` - Stop streaming
```bash
if vmix stream stop <instance> [--channel <0-2>]
```

**Example:**
```bash
if vmix stream stop myvmix
```

#### `stream status` - Get streaming status
```bash
if vmix stream status <instance> [--format text|json]
```

**Example:**
```bash
if vmix stream status myvmix
```

---

### Recording Control

#### `record start` - Start recording
```bash
if vmix record start <instance> [--file <filename>] [--format <format>]
```

**Parameters:**
- `--file` - Output filename (optional, vMix uses default if not specified)
- `--format` - File format: MP4, AVI, MOV (for documentation)

**Example:**
```bash
if vmix record start myvmix
if vmix record start myvmix --file "Event_2025-11-11.mp4"
```

#### `record stop` - Stop recording
```bash
if vmix record stop <instance>
```

**Example:**
```bash
if vmix record stop myvmix
```

#### `record status` - Get recording status
```bash
if vmix record status <instance> [--format text|json]
```

**Example:**
```bash
if vmix record status myvmix
```

---

### Status & Queries

#### `status` - Get vMix status
```bash
if vmix status <instance> [--format text|json]
```

**Example:**
```bash
if vmix status myvmix

# Output:
vMix Status: myvmix
--------------------------------------------------
Version:    25.0.0.65
Edition:    4K
Inputs:     8
Active:     Input 1
Preview:    Input 2
Recording:  False
Streaming:  True
Audio:      True
```

#### `inputs` - List all inputs
```bash
if vmix inputs <instance> [--format text|json]
```

**Example:**
```bash
if vmix inputs myvmix

# Output:
Inputs (8)

Input      Type            Title                          State
----------------------------------------------------------------------
1          Video           Camera 1                       Running
2          NDI             NDI Source                     Running
3          Video           Video Clip                     Paused
```

#### `state` - Get production state
```bash
if vmix state <instance> [--format text|json]
```

**Example:**
```bash
if vmix state myvmix

# Output:
Production State
--------------------------------------------------
Active:  Input 1 - Camera 1 (Video)
Preview: Input 2 - NDI Source (NDI)
```

---

### PTZ Camera Control

#### `ptz move` - Move PTZ camera
```bash
if vmix ptz move <instance> --input <number> [--pan <-100..100>] [--tilt <-100..100>] [--zoom <0..100>]
```

**Parameters:**
- `--pan` - Pan value (-100 to 100)
- `--tilt` - Tilt value (-100 to 100)
- `--zoom` - Zoom value (0 to 100)

**Example:**
```bash
if vmix ptz move myvmix --input 1 --pan 50 --tilt 30 --zoom 80
if vmix ptz move myvmix --input 1 --pan 0 --tilt 0  # Center camera
```

#### `ptz preset` - Recall PTZ preset
```bash
if vmix ptz preset <instance> --input <number> --preset <number>
```

**Example:**
```bash
if vmix ptz preset myvmix --input 1 --preset 3
```

#### `ptz home` - Move PTZ to home position
```bash
if vmix ptz home <instance> --input <number>
```

**Example:**
```bash
if vmix ptz home myvmix --input 1
```

---

### Audio Control

#### `audio volume` - Set input volume
```bash
if vmix audio volume <instance> --input <number> --volume <0-100>
```

**Example:**
```bash
if vmix audio volume myvmix --input 1 --volume 75
```

#### `audio mute` - Mute input audio
```bash
if vmix audio mute <instance> --input <number>
```

**Example:**
```bash
if vmix audio mute myvmix --input 1
```

#### `audio unmute` - Unmute input audio
```bash
if vmix audio unmute <instance> --input <number>
```

**Example:**
```bash
if vmix audio unmute myvmix --input 1
```

---

## IF.witness Integration

**Every vMix operation is automatically logged to IF.witness** for complete audit trails.

### What Gets Logged

- All production control operations (cut, fade, transition)
- Instance management (add, remove)
- Streaming and recording events
- PTZ camera movements
- Audio changes

### View Witness Logs

```bash
# View all vMix operations
if witness query --component IF.vmix

# View operations for specific instance
if witness query --component IF.vmix --filter "instance:myvmix"

# View specific operation types
if witness query --component IF.vmix --filter "event:vmix_cut"
```

### Log Entry Format

```json
{
  "id": "uuid",
  "timestamp": "2025-11-11T23:15:30Z",
  "event": "vmix_cut",
  "component": "IF.vmix",
  "trace_id": "vmix-myvmix-uuid",
  "payload": {
    "instance": "myvmix",
    "operation": "cut",
    "params": {"input": 1},
    "result": {"success": true}
  }
}
```

### Compliance & Audit

IF.witness provides:
- **Tamper-proof logs** - Hash-chained entries with Ed25519 signatures
- **Complete history** - Every operation recorded
- **Trace chains** - Link related operations
- **Export capabilities** - CSV, JSON, PDF reports

---

## Shell Completion

Enable tab completion for faster command entry.

### Bash

```bash
# Install completion
source /path/to/completions/vmix-completion.bash

# Or add to ~/.bashrc
echo "source /path/to/completions/vmix-completion.bash" >> ~/.bashrc
```

### Zsh

```bash
# Copy to your fpath
cp /path/to/completions/vmix-completion.zsh ~/.zsh/completions/_if

# Add to ~/.zshrc if needed
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```

### Usage

```bash
if vmix <TAB>                    # Show all commands
if vmix cut my<TAB>             # Complete instance name
if vmix cut myvmix --inp<TAB>  # Complete --input option
```

---

## Examples

### Complete Production Workflow

```bash
# Setup
if vmix add studio1 --host 192.168.1.100
if vmix test studio1

# Pre-show setup
if vmix ndi add studio1 --source "Camera 1 (192.168.1.50)"
if vmix ndi add studio1 --source "Camera 2 (192.168.1.51)"

# Configure streaming
if vmix stream start studio1 --rtmp rtmp://live.example.com/live --key abc123

# Start recording
if vmix record start studio1 --file "Event_2025-11-11.mp4"

# Production control
if vmix preview studio1 --input 2
if vmix fade studio1 --input 2 --duration 2000
if vmix cut studio1 --input 1
if vmix overlay studio1 --num 1 --input 5

# PTZ control
if vmix ptz preset studio1 --input 1 --preset 3
if vmix ptz move studio1 --input 2 --pan 50 --tilt 30

# Audio control
if vmix audio volume studio1 --input 1 --volume 75
if vmix audio mute studio1 --input 3

# End show
if vmix record stop studio1
if vmix stream stop studio1
```

### Automated Show Script

```bash
#!/bin/bash
# automated_show.sh - Run automated production sequence

INSTANCE="studio1"

# Scene 1: Opening
if vmix cut $INSTANCE --input 1
if vmix audio unmute $INSTANCE --input 1
sleep 5

# Scene 2: Camera 2
if vmix preview $INSTANCE --input 2
if vmix fade $INSTANCE --input 2 --duration 2000
sleep 10

# Scene 3: Graphics overlay
if vmix overlay $INSTANCE --num 1 --input 5
sleep 3

# Scene 4: Close
if vmix fade $INSTANCE --input 1 --duration 3000
if vmix audio volume $INSTANCE --input 1 --volume 50
```

### Multi-Instance Control

```bash
# Control multiple vMix instances
if vmix add main --host 192.168.1.100
if vmix add backup --host 192.168.1.101

# Synchronized cuts
if vmix cut main --input 1 &
if vmix cut backup --input 1 &
wait

# Failover scenario
if vmix test main || {
    echo "Main failed, switching to backup"
    if vmix stream start backup
}
```

### Status Monitoring

```bash
#!/bin/bash
# monitor.sh - Monitor vMix status

while true; do
    clear
    echo "=== vMix Status Monitor ==="
    date
    echo
    if vmix status studio1
    echo
    if vmix state studio1
    sleep 5
done
```

---

## Troubleshooting

### Connection Issues

**Problem:** `Cannot connect to vMix`

**Solutions:**
1. Check vMix is running and Web Controller is enabled
2. Verify host IP and port: `if vmix test <instance>`
3. Check firewall: `telnet <host> 8088`
4. Ensure vMix API is accessible: `curl http://<host>:8088/api/`

### Configuration Issues

**Problem:** `Instance not found`

**Solutions:**
1. List instances: `if vmix list`
2. Check config file: `cat ~/.if/vmix/instances.yaml`
3. Re-add instance: `if vmix add <name> --host <ip>`

### API Errors

**Problem:** `vMix API error`

**Solutions:**
1. Check vMix logs
2. Verify input numbers exist: `if vmix inputs <instance>`
3. Test with browser: `http://<host>:8088/api/?Function=Cut&Input=1`

### Permission Issues

**Problem:** `Failed to write config file`

**Solutions:**
1. Check directory permissions: `ls -la ~/.if/vmix/`
2. Create directory: `mkdir -p ~/.if/vmix`
3. Fix permissions: `chmod 755 ~/.if/vmix`

---

## API Reference

### vMix Function API

IF.vmix uses the vMix Function API via HTTP GET requests.

**Base URL:** `http://<host>:<port>/api/`

**Format:** `http://<host>:<port>/api/?Function=<name>&Param=Value`

### Supported Functions

| Function | Parameters | Description |
|----------|------------|-------------|
| Cut | Input | Instant cut to input |
| Fade | Input, Duration | Fade to input |
| PreviewInput | Input | Set preview input |
| Transition | Mix, Duration, Input | Custom transition |
| OverlayInput1-4 | Input | Set overlay input |
| AddInput | Value | Add input (e.g., NDI) |
| RemoveInput | Input | Remove input |
| StartStreaming | Value | Start streaming (channel) |
| StopStreaming | Value | Stop streaming |
| StartRecording | Filename | Start recording |
| StopRecording | - | Stop recording |
| PTZ | Input, Pan, Tilt, Zoom | PTZ camera control |
| PTZPreset | Input, Value | Recall PTZ preset |
| PTZHome | Input | PTZ home position |
| SetVolume | Input, Value | Set input volume |
| AudioOn | Input | Unmute audio |
| AudioOff | Input | Mute audio |

### XML Status API

**Endpoint:** `http://<host>:<port>/api/`

**Method:** GET (no parameters)

**Response:** XML document with system status

**Example:**
```xml
<vmix>
  <version>25.0.0.65</version>
  <edition>4K</edition>
  <inputs>
    <input key="1" number="1" type="Video" state="Running">Camera 1</input>
  </inputs>
  <active>1</active>
  <preview>2</preview>
  <recording>False</recording>
  <streaming>True</streaming>
</vmix>
```

### Official Documentation

For complete vMix API documentation:
- https://www.vmix.com/help25/index.htm?DeveloperAPI.html

---

## Support

### Community

- GitHub Issues: https://github.com/yourorg/infrafabric/issues
- Discord: https://discord.gg/infrafabric
- Documentation: https://docs.infrafabric.dev

### Contributing

Contributions welcome! See [CONTRIBUTING.md](../../CONTRIBUTING.md)

### License

MIT License - See [LICENSE](../../LICENSE)

---

**Built with InfraFabric Philosophy**
- **IF.ground Principle 8**: Observability without fragility
- **Dead-simple CLI**: Production engineers first
- **IF.witness logging**: Complete audit trails
- **No magic**: Transparent operations

---

*Last updated: 2025-11-12*
