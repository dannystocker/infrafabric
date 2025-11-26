# Bitfocus Companion v3.0+ Quick Reference

**Ultra-condensed API reference for production use**

---

## Connection Parameters

```python
# HTTP API
Host: localhost:8000
Method: POST (for actions)
Body: {} or JSON payload

# TCP Socket
Host: localhost:51234
Protocol: Raw TCP
Format: Command\n

# UDP Socket
Host: localhost:51235
Protocol: UDP Datagram
Format: Command\n

# Satellite API
Host: localhost:16622
Protocol: TCP Socket (bidirectional)
Format: Command ARG1=value ARG2=value\n
WebSocket: ws://localhost:16623 (v3.5+)
```

---

## HTTP API Quick Commands

### Button Press
```bash
# Press button at page 1, row 0, column 4
curl -X POST http://localhost:8000/api/location/1/0/4/press -d '{}'
```

### Update Style
```bash
# Change text and background color
curl -X POST http://localhost:8000/api/location/1/0/4/style \
  -H "Content-Type: application/json" \
  -d '{"text":"LIVE","bgcolor":"#ff0000","color":"#ffffff","size":28}'

# Change text only (query string)
curl -X POST "http://localhost:8000/api/location/1/0/4/style?text=LIVE"
```

### Press & Hold
```bash
# Press down
curl -X POST http://localhost:8000/api/location/1/0/4/down -d '{}'

# Release
curl -X POST http://localhost:8000/api/location/1/0/4/up -d '{}'
```

---

## TCP/UDP Socket Commands

### Button Control
```
LOCATION 1/0/4 PRESS
LOCATION 1/0/4 DOWN
LOCATION 1/0/4 UP
LOCATION 1/0/4 ROTATE AMOUNT=3
```

### Style Updates
```
LOCATION 1/0/4 STYLE TEXT="LIVE"
LOCATION 1/0/4 STYLE BGCOLOR=#ff0000
LOCATION 1/0/4 STYLE TEXT="ON AIR" BGCOLOR=#ff0000 COLOR=#ffffff
```

### Page Management
```
SURFACE emulator PAGE-SET 5
SURFACE emulator PAGE-GET
```

### Variables
```
CUSTOM-VARIABLE scene_number SET-VALUE 5
CUSTOM-VARIABLE status SET-VALUE "Recording"
```

### System
```
SURFACES RESCAN
SURFACES LIST
```

---

## Python Quick Start

### HTTP Client (Simple)
```python
import requests

def press_button(host, page, row, col):
    url = f"http://{host}:8000/api/location/{page}/{row}/{col}/press"
    requests.post(url, json={})

def set_style(host, page, row, col, text, bgcolor):
    url = f"http://{host}:8000/api/location/{page}/{row}/{col}/style"
    requests.post(url, json={"text": text, "bgcolor": bgcolor})

# Usage
press_button("192.168.1.100", 1, 0, 4)
set_style("192.168.1.100", 1, 0, 4, "LIVE", "#ff0000")
```

### TCP Client (Low Latency)
```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.1.100", 51234))

def send_command(command):
    sock.sendall(f"{command}\n".encode())

# Usage
send_command("LOCATION 1/0/4 PRESS")
send_command("LOCATION 1/0/4 STYLE TEXT=\"LIVE\" BGCOLOR=#ff0000")

sock.close()
```

### UDP Client (Ultra Fast)
```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_command(command):
    sock.sendto(f"{command}\n".encode(), ("192.168.1.100", 51235))

# Usage
send_command("LOCATION 1/0/4 PRESS")
send_command("LOCATION 1/0/4 STYLE BGCOLOR=#00ff00")

sock.close()
```

---

## Satellite API Quick Start

### Connection Handshake
```
Client: [Connect to port 16622]
Server: BEGIN CompanionVersion=3.0.0 ApiVersion=1.8.0
Client: ADD-DEVICE DEVICEID=deck001 PRODUCT_NAME="My StreamDeck" KEYS_TOTAL=15
Server: ADD-DEVICE OK
```

### Send Key Press
```
KEY-PRESS DEVICEID=deck001 KEY=0 PRESSED=1
KEY-PRESS DEVICEID=deck001 KEY=0 PRESSED=0
```

### Receive Key State
```
Server: KEY-STATE DEVICEID=deck001 KEY=0 COLOR=#ff0000 TEXT="LIVE"
```

### Keepalive
```
Client: PING test123
Server: PONG test123
```

---

## Performance Targets

| Protocol | Latency (LAN) | Throughput | Use Case |
|----------|---------------|------------|----------|
| HTTP API | 5-15ms | 100-200 req/s | Web integration, simple control |
| TCP Socket | 2-8ms | 500-2000 cmd/s | Production automation, low latency |
| UDP Socket | 1-3ms | 1000-5000 cmd/s | High-frequency updates, indicators |
| Satellite API | 3-10ms | 50-100 upd/s | Custom surfaces, full state sync |

---

## Security Checklist

- [ ] APIs enabled only on trusted networks
- [ ] Firewall rules configured (whitelist IPs)
- [ ] VPN/tunnel for remote access
- [ ] No public internet exposure
- [ ] Surface PIN codes enabled (if applicable)
- [ ] Connection monitoring active
- [ ] Logs reviewed regularly

---

## Common Issues & Solutions

### HTTP 405 Method Not Allowed
**Cause:** Using GET instead of POST
**Solution:** Use POST method with empty JSON body: `curl -X POST url -d '{}'`

### TCP Connection Refused
**Cause:** TCP server not enabled or wrong port
**Solution:** Settings → HTTP → Enable "TCP Server", verify port 51234

### No Response from UDP
**Cause:** UDP is fire-and-forget, no confirmation
**Solution:** Expected behavior. Use TCP if acknowledgment needed.

### Button Not Responding
**Cause:** Wrong location format or button doesn't exist
**Solution:** Verify page/row/column indexing (0-based), check button exists in Companion

### Style Not Updating
**Cause:** Invalid color format or missing quotes for text with spaces
**Solution:** Use hex format `#ff0000`, quote text: `TEXT="ON AIR"`

---

## Location Format

**Format:** `page/row/column` (all 0-indexed)

**Example:**
- Page 1, Row 0 (top), Column 4 (5th button): `1/0/4`
- Page 2, Row 1, Column 0 (first button, second row): `2/1/0`

**Stream Deck 15-key Layout (5x3):**
```
Page 1, Row 0: 1/0/0  1/0/1  1/0/2  1/0/3  1/0/4
Page 1, Row 1: 1/1/0  1/1/1  1/1/2  1/1/3  1/1/4
Page 1, Row 2: 1/2/0  1/2/1  1/2/2  1/2/3  1/2/4
```

---

## Color Format

**Supported Formats:**
- Hex: `#ff0000` or `ff0000`
- RGB: `rgb(255,0,0)`
- Named: Not supported (use hex/rgb)

**Common Colors:**
- Red: `#ff0000`
- Green: `#00ff00`
- Blue: `#0000ff`
- Yellow: `#ffff00`
- White: `#ffffff`
- Black: `#000000`

---

## Troubleshooting Commands

### Test HTTP API
```bash
# Test button press (should return 200 OK)
curl -v -X POST http://localhost:8000/api/location/1/0/0/press -d '{}'
```

### Test TCP Connection
```bash
# Send command via netcat
echo "LOCATION 1/0/0 PRESS" | nc localhost 51234
```

### Test UDP Connection
```bash
# Send command via netcat (UDP mode)
echo "LOCATION 1/0/0 PRESS" | nc -u localhost 51235
```

### Check Port Availability
```bash
# Linux/Mac
netstat -an | grep LISTEN | grep -E '(8000|51234|51235|16622)'

# Windows
netstat -an | findstr /C:"8000" /C:"51234" /C:"51235" /C:"16622"
```

---

## One-Liners

### Press button every second (bash)
```bash
while true; do
  curl -X POST http://localhost:8000/api/location/1/0/0/press -d '{}'
  sleep 1
done
```

### Animate colors (Python)
```python
import requests, time
colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
url = "http://localhost:8000/api/location/1/0/0/style"
while True:
    for color in colors:
        requests.post(url, json={"bgcolor": color})
        time.sleep(0.5)
```

### TCP stress test (Python)
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 51234))
for i in range(1000):
    sock.sendall(f"LOCATION 1/0/{i%10} PRESS\n".encode())
sock.close()
```

---

## Documentation Links

- **Full API Guide:** [README.md](README.md)
- **GitHub Repo:** https://github.com/bitfocus/companion
- **Satellite API:** https://github.com/bitfocus/companion/wiki/Satellite-API
- **Official Site:** https://bitfocus.io/companion

---

**Last Updated:** 2025-11-26
**Version:** v3.0+
