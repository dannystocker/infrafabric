# HyperDeck Protocol - Quick Reference Card

## Connection

```
TCP port: 9993
Telnet: telnet 192.168.x.x 9993
```

---

## Basic Command Format

```
{Command}: {Param}: {Value} {Param}: {Value}
play: speed: 200 loop: true
```

---

## Essential Commands

### Transport Control

| Command | Example | Response |
|---------|---------|----------|
| Play | `play` | `200 ok` |
| Play w/ speed | `play: speed: 200` | `200 ok` |
| Record | `record` | `200 ok` |
| Record named | `record: name: Clip001` | `200 ok` |
| Stop | `stop` | `200 ok` |

### Navigation

| Command | Example | Response |
|---------|---------|----------|
| Go to clip | `goto: clip id: 5` | `200 ok` |
| Go to timecode | `goto: timecode: 00:10:00:00` | `200 ok` |
| Next clip | `next` | `200 ok` |
| Previous | `previous` | `200 ok` |

### Information Queries

| Command | Example | Response Code |
|---------|---------|---|
| Device info | `device info` | 205 |
| Transport info | `transport info` | 208 |
| Slot info | `slot info: slot id: 1` | 207 |
| Clip count | `clips count` | 208 |
| Get all clips | `clips get: version: 2` | 206 |

### Configuration

| Command | Example | Response |
|---------|---------|----------|
| Video input | `configuration: video input: SDI` | `200 ok` |
| Audio input | `configuration: audio input: XLR` | `200 ok` |
| File format | `configuration: file format: ProRes HQ` | `200 ok` |
| Timecode source | `configuration: timecode input: external` | `200 ok` |
| Set timecode | `configuration: timecode preset: 01:00:00:00` | `200 ok` |

### Remote Control

| Command | Example | Response |
|---------|---------|----------|
| Enable remote | `remote: enable: true` | `200 ok` |
| Watchdog | `watchdog: period: 30` | `200 ok` |
| Subscribe transport | `notify: transport: true` | `200 ok` |
| Subscribe slots | `notify: slot: true` | `200 ok` |

---

## Response Codes Cheat Sheet

### Success (200-299)
- **200** ok
- **205** device info:
- **206** clips:
- **207** slot info:
- **208** transport info: or clips count:
- **209** display timecode:

### Errors (100-199)
- **100** syntax error
- **101** unsupported parameter
- **102** invalid value
- **104** disk full
- **105** no disk
- **110** no input signal
- **111** remote control disabled

### Notifications (500-599)
- **500** connection info (on connect)
- **506** clips changed
- **507** slot changed
- **508** transport changed
- **509** configuration changed

---

## Transport Status Values

```
play          - Playing forward
record        - Recording
stopped       - Stopped
forward       - Jog/shuttle forward
backward      - Jog/shuttle backward
paused        - Paused (some models)
```

---

## Video Input Options

```
SDI
HDMI
component
```

---

## Audio Input Options

```
embedded      - From video signal
XLR
RCA
```

---

## File Format Options

```
H.264
H.265
ProRes HQ
ProRes Standard
ProRes LT
ProRes Proxy
DNxHD         (4K models only)
DNxHR         (4K models only)
```

---

## Timecode Input Sources

```
external      - From SDI/HDMI input
embedded      - From video stream
preset        - Manual configuration
clip          - From timeline
```

---

## Slot Status Values

```
empty         - No media
mounting      - Media mounting
mounted       - Ready to use
ejecting      - Media ejecting
error         - Hardware error
```

---

## Python Quick Start

```python
import socket

sock = socket.socket()
sock.connect(('192.168.1.100', 9993))

# Receive connection info
print(sock.recv(1024).decode())

# Send command
sock.sendall(b'device info\n')
print(sock.recv(1024).decode())

# Send another command
sock.sendall(b'transport info\n')
print(sock.recv(1024).decode())

sock.close()
```

---

## Response Parsing Template

```python
def parse_response(response_text):
    lines = response_text.strip().split('\n')
    code = int(lines[0].split()[0])

    if 200 <= code <= 299:
        return {'status': 'success', 'code': code}
    elif 100 <= code <= 199:
        return {'status': 'error', 'code': code}
    elif 500 <= code <= 599:
        return {'status': 'notification', 'code': code}
```

---

## Common Workflows

### Play a Specific Clip

```
goto: clip id: 5
play: speed: 100
transport info
```

### Record with Slot Management

```
slot info: slot id: 1
record: name: MyClip spill: true slot id: 2
notify: transport: true
(wait...)
stop
```

### Multitrack Sync Setup

**Deck 1 (Primary):**
```
configuration: timecode input: external
```

**Deck 2 (Secondary):**
```
configuration: timecode input: external
```
*(Connect TC OUT from Deck 1 to TC IN on Deck 2)*

### Error Recovery

```
transport info                    # Check current state
clips count                       # Verify timeline
slot info: slot id: 1            # Check disk
remote: enable: true             # Re-enable remote
watchdog: period: 30             # Reset keepalive
```

---

## Keepalive Interval

**Recommended:** 30 seconds

Must send at least one command every N seconds to maintain connection:

```
watchdog: period: 30
```

Client sends any command within 30s, or connection closes.

---

## Multi-line Response Example

```
208 transport info:
status: play
speed: 100
slot id: 1
clip id: 0
timecode: 00:01:23:15
cache filling: false

```

(Note: blank line at end indicates end of response)

---

## Timecode Format

```
HH:MM:SS:FF

HH = Hours (00-23)
MM = Minutes (00-59)
SS = Seconds (00-59)
FF = Frames (00-29 NTSC, 00-24 PAL)

Example: 01:23:45:15
```

---

## Speed Values

```
-5000 = 5x reverse
-1000 = 1x reverse (backward)
0     = Stopped (jog)
100   = 1x forward (normal speed)
200   = 2x forward
5000  = 5x forward
```

---

## Telnet Tips

1. Connect: `telnet 192.168.1.100 9993`
2. Type commands followed by Enter
3. Exit: `Ctrl+]` then type `quit`
4. Note: Responses include blank line terminator

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Check IP, port, network |
| Connection rejected (120) | Another client connected; disconnect it |
| Syntax error (100) | Check command format exactly |
| Invalid value (102) | Check parameter ranges |
| Disk full (104) | Eject and replace media |
| No input (110) | Check video/audio source |
| Command timeout | Send keepalive command |

---

## JSON Redis Mapping Template

```json
{
  "hyperdeck:deck-01:device_info": {
    "model": "HyperDeck Extreme",
    "protocol_version": "2.11"
  },
  "hyperdeck:deck-01:transport": {
    "status": "play",
    "timecode": "00:01:23:15",
    "speed": 100
  }
}
```

---

## Resources

- **Official PDF:** https://documents.blackmagicdesign.com/DeveloperManuals/HyperDeckEthernetProtocol.pdf
- **Developer Portal:** https://www.blackmagicdesign.com/developer/products/hyperdeck/sdk-and-software

---

**Version 1.0 | 2024-11-26 | Blackmagic HyperDeck Protocol 2.11+**
