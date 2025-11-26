# HyperDeck Ethernet Protocol - Implementation Guide

**Document Version:** 1.0
**Last Updated:** 2024-11-26
**Protocol Version:** 2.11+
**Source:** Blackmagic Design HyperDeck Documentation

---

## Table of Contents

1. [Connection & Initialization](#connection--initialization)
2. [Protocol Basics](#protocol-basics)
3. [Command Categories](#command-categories)
4. [Response Codes Reference](#response-codes-reference)
5. [Practical Examples](#practical-examples)
6. [Error Handling](#error-handling)
7. [Timecode Synchronization](#timecode-synchronization)
8. [Implementation Patterns](#implementation-patterns)

---

## Connection & Initialization

### TCP Connection Details

| Parameter | Value |
|-----------|-------|
| **Protocol** | TCP/IP |
| **Port** | 9993 |
| **Default IP** | Device IP (DHCP/Static) |
| **Connection Limit** | 1 simultaneous client |
| **Line Terminator (Server)** | ASCII CR LF (`\r\n`) |
| **Line Terminator (Client)** | LF (`\n`) or CR LF (`\r\n`) |

### Telnet Connection Example

```bash
telnet 192.168.1.100 9993
```

### Expected Connection Response

Upon successful connection, the server sends:

```
500 connection info:
protocol version: 2.11
model: HyperDeck Extreme
unique id: ABC123DEF456GHI789
```

### Watchdog/Keepalive Setup

```
watchdog: period: 30
200 ok
```

Client must send at least one command every 30 seconds, or connection will be terminated.

---

## Protocol Basics

### Command Format - Single Line

```
{Command}: {Parameter}: {Value} {Parameter}: {Value}...↵
```

**Example:**
```
play: speed: 200 loop: true
```

### Command Format - Multi-line

```
{Command}:↵
{Parameter}: {Value}↵
{Parameter}: {Value}↵
↵
```

**Example:**
```
record:
name: MyRecording
spill: true
slot id: 2

```

### Response Format - Simple

```
{Code} {Text}
```

**Example:**
```
200 ok
```

### Response Format - With Parameters

```
{Code} {Text}:
{Parameter}: {Value}
{Parameter}: {Value}
↵
```

**Example:**
```
208 transport info:
status: play
speed: 100
slot id: 1
clip id: 0
timecode: 00:01:23:15
cache filling: false

```

---

## Command Categories

### 1. Transport Control

#### Play Command

```
play
200 ok

play: speed: 200
200 ok

play: speed: 200 loop: true single clip: true
200 ok
```

**Parameters:**
- `speed` (int): -5000 to 5000 (percentage, negative = reverse)
- `loop` (bool): Loop playback
- `single clip` (bool): Play current clip only

#### Record Command

```
record
200 ok

record: name: MyClip
200 ok

record: spill: true slot id: 2
200 ok
```

**Parameters:**
- `name` (string): Clip name
- `spill` (bool): Spill to alternate slot
- `slot id` (int): Target slot for spill

#### Stop Command

```
stop
200 ok
```

### 2. Navigation

#### Go To Clip

```
goto: clip id: 5
200 ok
```

#### Go To Timecode

```
goto: timecode: 00:05:30:15
200 ok
```

#### Next/Previous

```
next
200 ok

previous
200 ok
```

### 3. Clip Management

#### Get Clip Count

```
clips count
208 clips count:
count: 12

```

#### Get All Clips (Version 2 - Recommended)

```
clips get: version: 2
206 clips:
0 00:00:00:00 00:10:00:00 00:00:00:00 Opening Scene
1 00:10:00:00 00:05:30:15 00:00:00:00 Scene Transition
2 00:15:30:15 00:12:45:00 00:00:00:00 Main Content
3 00:28:15:15 00:03:20:00 00:00:00:00 Closing

```

**Response Fields:**
- Clip ID
- Start timecode on timeline
- Duration
- In timecode (within clip)
- Clip name

#### Get Clips Version 3 (Recursive Paths)

```
clips get: version: 3
206 clips:
0 00:00:00:00 00:10:00:00 00:00:00:00 Production/OpeningScene
1 00:10:00:00 00:05:30:15 00:00:00:00 Production/Transitions/SceneTransition

```

#### Add Clip

```
clips add: name: NewClip
200 ok
```

#### Remove Clip

```
clips remove: clip id: 5
200 ok
```

#### Set Playback Range

```
playrange set: clip id: 5 count: 7
200 ok
```

Plays clips 5 through 11 (7 clips total).

### 4. Status Queries

#### Device Info

```
device info
205 device info:
protocol version: 2.11
model: HyperDeck Extreme
unique id: ABC123DEF456GHI789
slot count: 2
software version: 8.5.2

```

#### Transport Info

```
transport info
208 transport info:
status: play
speed: 100
slot id: 1
clip id: 0
timecode: 00:01:23:15
cache filling: false

```

**Status Values:**
- `play` - Playing forward
- `record` - Recording
- `stopped` - Stopped
- `forward` - Forward in jog/shuttle
- `backward` - Backward in jog/shuttle
- `jog` - Jogging
- `shuttle` - Shuttle playback

#### Slot Info

```
slot info: slot id: 1
207 slot info:
slot id: 1
status: mounted
volume name: SSD_001
recording time: 02:30:45:00
video format: 1080i59.94
blocked: false

```

**Status Values:**
- `empty` - Slot is empty
- `mounting` - Media is mounting
- `mounted` - Media ready
- `ejecting` - Media being ejected
- `error` - Hardware error

### 5. Configuration

#### Video Input

```
configuration: video input: SDI
200 ok
```

**Values:** `SDI`, `HDMI`, `component`

#### Audio Input

```
configuration: audio input: XLR
200 ok
```

**Values:** `embedded`, `XLR`, `RCA`

#### File Format

```
configuration: file format: ProRes HQ
200 ok
```

**Values:** `H.264`, `H.265`, `ProRes HQ`, `ProRes Standard`, `ProRes LT`, `ProRes Proxy`, `DNxHD`, `DNxHR`

#### Timecode Input

```
configuration: timecode input: external
200 ok
```

**Values:** `external`, `embedded`, `preset`, `clip`

#### Timecode Preset

```
configuration: timecode preset: 01:00:00:00
200 ok
```

### 6. Remote Control Management

#### Enable/Disable Remote

```
remote: enable: true
200 ok

remote: override: true
200 ok
```

#### Watchdog (Keepalive)

```
watchdog: period: 30
200 ok
```

If period is 0 or negative, watchdog is disabled.

### 7. Notifications

#### Subscribe to Transport Changes

```
notify: transport: true
200 ok
```

Server will now send `508 transport info:` messages when status changes.

#### Subscribe to Slot Changes

```
notify: slot: true
200 ok
```

Server will send `507 slot info:` messages.

#### Subscribe to Clips Changes

```
notify: clips: true
200 ok
```

Server will send `506 clips:` messages.

#### Subscribe to Configuration Changes

```
notify: configuration: true
200 ok
```

Server will send `509 configuration:` messages.

---

## Response Codes Reference

### Success Codes (200-299)

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Simple acknowledgment | `200 ok` |
| 201 | Asynchronous message ack | `201 ok` |
| 205 | Device info response | `205 device info:` |
| 206 | Clip list response | `206 clips:` |
| 207 | Slot info response | `207 slot info:` |
| 208 | Transport/clips count | `208 transport info:` |
| 209 | Display timecode | `209 display timecode:` |

### Asynchronous Messages (500-599)

| Code | Message | Meaning |
|------|---------|---------|
| 500 | Connection info | Device sends on client connect |
| 501 | Device info | Device properties changed |
| 502 | Remote | Remote control state changed |
| 503 | Recording time | Available recording time changed |
| 504 | Cache filling | Buffer status changed |
| 505 | OK | Graceful disconnect |
| 506 | Clips | Timeline modified |
| 507 | Slot info | Slot status changed |
| 508 | Transport info | Playback/record state changed |
| 509 | Configuration | Settings changed |

### Error Codes (100-199)

| Code | Name | Description |
|------|------|-------------|
| 100 | Syntax error | Invalid command format |
| 101 | Unsupported parameter | Parameter not available |
| 102 | Invalid value | Parameter value out of range |
| 103 | Unsupported | Feature not supported on this model |
| 104 | Disk full | Storage media is full |
| 105 | No disk | No media inserted |
| 106 | Disk error | Hardware failure |
| 107 | Timeline empty | No clips to play |
| 108 | Internal error | Device firmware error |
| 109 | Out of range | ID/value exceeds limits |
| 110 | No input | No video/audio signal |
| 111 | Remote disabled | Remote control disabled |
| 120 | Connection rejected | Another client connected |

---

## Practical Examples

### Example 1: Simple Playback Control

```python
import socket
import time

def send_command(sock, cmd):
    sock.sendall((cmd + '\n').encode('utf-8'))
    response = sock.recv(4096).decode('utf-8')
    return response

# Connect
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.100', 9993))

# Read connection info
response = sock.recv(4096).decode('utf-8')
print("Connection:", response)

# Set watchdog
print(send_command(sock, 'watchdog: period: 30'))

# Get device info
print(send_command(sock, 'device info'))

# Start playback at 200% speed
print(send_command(sock, 'play: speed: 200'))

# Wait 5 seconds
time.sleep(5)

# Stop playback
print(send_command(sock, 'stop'))

sock.close()
```

### Example 2: Recording with Slot Management

```python
def record_clip(sock, clip_name, slot_id=1):
    # Get slot info first
    response = send_command(sock, f'slot info: slot id: {slot_id}')
    print(f"Slot status: {response}")

    # Start recording
    cmd = f'record: name: {clip_name}'
    if slot_id > 1:
        cmd += f' spill: true slot id: {slot_id}'

    return send_command(sock, cmd)

# Record to primary slot
print(record_clip(sock, 'MyClip_001', slot_id=1))

# Record for 30 seconds
time.sleep(30)

# Stop recording
print(send_command(sock, 'stop'))
```

### Example 3: Timeline Navigation

```python
def navigate_timeline(sock, clip_id):
    # Get clip count
    response = send_command(sock, 'clips count')
    print(f"Clips on timeline: {response}")

    # Get all clips
    response = send_command(sock, 'clips get: version: 2')
    print(f"Clip list:\n{response}")

    # Jump to specific clip
    response = send_command(sock, f'goto: clip id: {clip_id}')
    print(f"Goto clip {clip_id}: {response}")

    # Check transport state
    response = send_command(sock, 'transport info')
    print(f"Current state:\n{response}")

navigate_timeline(sock, 5)
```

### Example 4: Timecode Synchronization

```python
def setup_timecode_sync(sock, preset_tc='01:00:00:00'):
    # Set external timecode input
    print(send_command(sock, 'configuration: timecode input: external'))

    # Alternative: use preset
    print(send_command(sock, f'configuration: timecode preset: {preset_tc}'))

    # Enable frame resync
    print(send_command(sock, 'configuration: timecode input: preset'))

    # Verify
    print(send_command(sock, 'transport info'))

setup_timecode_sync(sock)
```

### Example 5: Notification Subscription

```python
import threading

def listen_for_notifications(sock):
    """Listen for asynchronous messages from device"""
    while True:
        try:
            data = sock.recv(4096).decode('utf-8')
            if data:
                print(f"Notification: {data}")
        except:
            break

# Subscribe to all notifications
send_command(sock, 'notify: transport: true')
send_command(sock, 'notify: slot: true')
send_command(sock, 'notify: clips: true')
send_command(sock, 'notify: configuration: true')

# Start listener thread
listener = threading.Thread(target=listen_for_notifications, args=(sock,), daemon=True)
listener.start()

# Your main program continues...
```

---

## Error Handling

### Error Response Parsing

```python
def parse_response(response):
    lines = response.strip().split('\n')
    code = int(lines[0].split()[0])

    if 200 <= code <= 299:
        return {'status': 'success', 'code': code, 'data': lines[1:]}
    elif 100 <= code <= 199:
        error_msg = ' '.join(lines[0].split()[1:])
        return {'status': 'error', 'code': code, 'error': error_msg}
    elif 500 <= code <= 599:
        return {'status': 'notification', 'code': code, 'data': lines[1:]}
    else:
        return {'status': 'unknown', 'code': code}

# Usage
response = send_command(sock, 'play: speed: invalid')
result = parse_response(response)

if result['status'] == 'error':
    print(f"Error {result['code']}: {result['error']}")
```

### Retry Logic with Exponential Backoff

```python
import time

def send_with_retry(sock, cmd, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = send_command(sock, cmd)
            result = parse_response(response)

            if result['status'] == 'success':
                return result
            elif result['status'] == 'error':
                # Check if retryable
                if result['code'] in [108, 110]:  # Internal/no input
                    wait_time = (2 ** attempt)
                    print(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Error {result['code']}: {result['error']}")
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    return None
```

---

## Timecode Synchronization

### Multi-Deck Synchronization

**Setup:**

1. Primary deck with timecode output (TC OUT)
2. Secondary decks with timecode input (TC IN)
3. Loop TC output from primary → TC in on secondary

**Configuration:**

```
# Primary deck
configuration: timecode input: external

# Secondary deck
configuration: timecode input: external

# Both decks connected:
# Primary TC OUT → Secondary TC IN
```

### Frame Resync

When input video is slightly out of sync, enable frame resync:

```
configuration: timecode input: external
# Frame resync happens automatically when drift detected
```

### Preset Timecode

For standalone operation:

```
configuration: timecode input: preset
configuration: timecode preset: 01:00:00:00
```

---

## Implementation Patterns

### Connection Pool Pattern

```python
class HyperDeckPool:
    def __init__(self, devices):
        self.devices = {dev['id']: dev for dev in devices}
        self.connections = {}

    def connect_all(self):
        for dev_id, dev in self.devices.items():
            sock = socket.socket()
            sock.connect((dev['ip'], 9993))
            self.connections[dev_id] = sock

            # Set watchdog
            sock.sendall(b'watchdog: period: 30\n')
            sock.recv(1024)

    def send_to_all(self, command):
        results = {}
        for dev_id, sock in self.connections.items():
            sock.sendall((command + '\n').encode())
            results[dev_id] = sock.recv(4096).decode()
        return results

    def disconnect_all(self):
        for sock in self.connections.values():
            sock.close()
```

### Command Queue Pattern

```python
class CommandQueue:
    def __init__(self, sock):
        self.sock = sock
        self.queue = []

    def enqueue(self, command):
        self.queue.append(command)

    def execute_all(self):
        for cmd in self.queue:
            response = send_command(self.sock, cmd)
            print(f"Executed: {cmd} -> {response}")
        self.queue.clear()

# Usage
q = CommandQueue(sock)
q.enqueue('record: name: Clip001')
q.enqueue('notify: transport: true')
q.enqueue('watchdog: period: 30')
q.execute_all()
```

### State Caching Pattern

```python
import json
from datetime import datetime, timedelta

class HyperDeckStateCache:
    def __init__(self, device_id, cache_ttl=5):
        self.device_id = device_id
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.timestamps = {}

    def get(self, key):
        if key in self.cache:
            age = datetime.now() - self.timestamps[key]
            if age < timedelta(seconds=self.cache_ttl):
                return self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = value
        self.timestamps[key] = datetime.now()

    def invalidate(self, key):
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
```

---

## References

- **Official Protocol Documentation:** https://documents.blackmagicdesign.com/DeveloperManuals/HyperDeckEthernetProtocol.pdf
- **REST API Alternative:** https://documents.blackmagicdesign.com/DeveloperManuals/RESTAPIForHyperDeck.pdf
- **Developer Portal:** https://www.blackmagicdesign.com/developer/products/hyperdeck/sdk-and-software

---

**End of Implementation Guide**
