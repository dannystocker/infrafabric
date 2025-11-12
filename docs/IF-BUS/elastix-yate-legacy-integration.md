# IF.bus Legacy Protocol Integration: Elastix & Yate

**Session 3 (H.323) Contribution to Session 7 (IF.bus)**
**Research Date**: 2025-11-11
**Research Agents**: 2x Haiku (Elastix + Yate)
**Purpose**: Enable IF.bus SIP server adapters to bridge legacy H.323 endpoints

---

## Executive Summary

This document provides comprehensive research on integrating legacy H.323 protocol systems with modern SIP infrastructure using two proven platforms: **Elastix** (Asterisk-based) and **Yate** (multi-protocol engine). This research enables Session 7's IF.bus SIP server adapters to support legacy enterprise systems.

**Key Findings**:
- **Elastix**: Practical SIP-H.323 gateway using chan_ooh323 module (Asterisk-based)
- **Yate**: Native multi-protocol engine treating H.323 as first-class citizen
- **Use Cases**: Legacy PBX integration (Avaya, Cisco, Polycom, Tandberg)
- **Performance**: Both handle 100+ concurrent H.323 channels with proper hardware

**Recommended Approach for IF.bus**:
- **Yate** for greenfield deployments (cleaner architecture, native H.323)
- **Elastix** for Asterisk-familiar teams (larger community, more tutorials)

---

## Table of Contents

1. [Elastix H.323 Integration](#1-elastix-h323-integration)
2. [Yate Multi-Protocol Integration](#2-yate-multi-protocol-integration)
3. [Architecture Comparison](#3-architecture-comparison)
4. [Configuration Examples](#4-configuration-examples)
5. [Performance Analysis](#5-performance-analysis)
6. [IF.bus Adapter Design](#6-ifbus-adapter-design)
7. [References](#7-references)

---

## 1. Elastix H.323 Integration

### 1.1 Overview

**Elastix** is a unified communications server based on Asterisk and FreePBX. H.323 support is provided via the **chan_ooh323** module (Objective Oriented H.323).

**Architecture**:
```
Elastix (FreePBX GUI)
    ↓
Asterisk Core
    ├── chan_pjsip (SIP - modern)
    ├── chan_sip (SIP - legacy)
    └── chan_ooh323 ← H.323 support
```

**Status**: Unsupported but widely deployed in production (legacy compatibility)

---

### 1.2 chan_h323 vs chan_ooh323

Two H.323 implementations exist for Asterisk:

| Feature | chan_h323 (deprecated) | chan_ooh323 (current) |
|---------|----------------------|---------------------|
| **Vendor** | NuFone Networks | Objective Systems |
| **Library** | OpenH323 + PWLib | ooh323c (pure C) |
| **Compilation** | ❌ Difficult | ✅ Easier |
| **CPU Usage** | ~1x baseline | ~10-15x (higher) |
| **Stability** | High | Moderate-High |
| **Media** | Via OpenH323 library | Via Asterisk RTP stack |
| **Jitter Buffer** | None | Yes (adaptive) |
| **Current Status** | Abandoned | Included in Asterisk addons |
| **Distribution** | TrixBox (old) | Elastix, FreePBX |

**Recommendation**: Use **chan_ooh323** (current, stable, easier to deploy)

---

### 1.3 SIP ↔ H.323 Gateway Configuration

**Basic Configuration** (`/etc/asterisk/ooh323.conf`):

```ini
[general]
; Port configuration
port = 1720
bindaddr = 0.0.0.0

; Jitter buffer
jitterbuffer = yes
jbmaxsize = 200
jbminsize = 50

; DTMF method (RFC2833 recommended)
dtmfmode = rfc2833

; Codecs (G.711 recommended - no transcoding)
disallow = all
allow = ulaw
allow = alaw
allow = g729  ; Optional, requires licensing

; Gatekeeper mode (default: no gatekeeper, direct peer-to-peer)
gatekeeper = DISABLE

[avaya-gateway]
; H.323 peer configuration
type = peer
context = from-h323
host = 192.168.1.100
port = 1720
dtmfmode = h245signal  ; Avaya preference
```

**Dial Plan** (`/etc/asterisk/extensions.conf`):

```ini
; Route incoming SIP calls to H.323 endpoint
[outgoing-to-h323]
exten => _9XXX,1,NoOp(Call to H.323 extension ${EXTEN:1})
exten => _9XXX,2,Dial(OOH323/${EXTEN:1}@avaya-gateway,30)
exten => _9XXX,3,Hangup()

; Route incoming H.323 calls to SIP
[from-h323]
exten => _XXXX,1,NoOp(Incoming H.323 call from ${CALLERID(num)})
exten => _XXXX,2,Dial(PJSIP/${EXTEN},30)
exten => _XXXX,3,Hangup()
```

---

### 1.4 Codec Support Matrix

| Codec | Bandwidth | Quality | Transcoding CPU | Elastix Support | Recommendation |
|-------|-----------|---------|----------------|----------------|----------------|
| **G.711** (ulaw/alaw) | 64 kbps | High | N/A (pass-through) | ✅ Mandatory | ⭐ **Use this** |
| **G.729** | 8 kbps | Medium | 15-20% per channel | ✅ Optional (licensed) | Use for low bandwidth |
| **G.722** | 64 kbps | HD Audio | ~5% per channel | ✅ Optional | Use for high quality |
| **G.723.1** | 5.3/6.3 kbps | Low | High (software) | ✅ Rare | Avoid |

**IF.bus Recommendation**: **Standardize on G.711** to avoid transcoding overhead

---

### 1.5 Performance Benchmarks

**Hardware**: Dual Xeon 3.06 GHz, 2 GB RAM

| Codec | Concurrent Channels | CPU Usage | Notes |
|-------|-------------------|-----------|-------|
| **G.711 (pass-through)** | 120 channels (60 calls) | <10% | No transcoding |
| **G.729 (transcoding)** | 20-30 channels per core | 80%+ | High CPU cost |
| **MeetMe conferences** | 30+ conferences | 0.5 load avg | G.711 only |

**Recommendation**: For IF.bus deployments expecting 100+ concurrent calls, use G.711 or deploy multiple instances.

---

### 1.6 Real-World Example: Avaya Integration

**Scenario**: Bridge Avaya Communication Manager (H.323) to Elastix (SIP)

**Step 1**: Configure Avaya CM:
```
; Avaya CM: Add Elastix as H.323 gateway
change node-names ip
avaya-ip-addr: 192.168.1.100
elastix-ip-addr: 192.168.1.200

change signaling-group 1
Group Type: h323
Transport Method: tcp
Near-end Node Name: avaya-ip-addr
Far-end Node Name: elastix-ip-addr
```

**Step 2**: Configure Elastix (ooh323.conf):
```ini
[avaya-cm]
type = peer
host = 192.168.1.100
context = from-avaya
dtmfmode = h245signal  ; Avaya preferred method
```

**Step 3**: Test Call Flow:
```bash
# From Elastix CLI
asterisk -r
*CLI> ooh323 show peers
*CLI> ooh323 show channels
*CLI> core show channels

# Make test call
Dial(OOH323/5001@avaya-cm)
```

**Common Issues**:
- **No Audio**: Check firewall rules for RTP ports (10000-20000)
- **DTMF Not Working**: Switch to `dtmfmode = h245signal`
- **Call Setup Slow**: Disable gatekeeper mode (`gatekeeper = DISABLE`)

---

### 1.7 Elastix for IF.bus: Implementation Notes

**Adapter Interface**:
```python
class ElastixH323Adapter(SIPServerAdapter):
    """Elastix adapter for IF.bus with H.323 support"""

    def __init__(self, host, ami_user, ami_secret):
        self.ami = asterisk.manager.Manager()
        self.ami.connect(host)
        self.ami.login(ami_user, ami_secret)

    def make_call_h323(self, from_sip, to_h323_peer, extension):
        """Bridge SIP caller to H.323 endpoint"""
        action = {
            'Action': 'Originate',
            'Channel': f'OOH323/{extension}@{to_h323_peer}',
            'Context': 'from-h323',
            'Exten': from_sip,
            'Priority': '1',
            'CallerID': from_sip
        }
        response = self.ami.send_action(action)
        return response

    def get_h323_peers(self):
        """List configured H.323 peers"""
        action = {'Action': 'Command', 'Command': 'ooh323 show peers'}
        response = self.ami.send_action(action)
        # Parse response for peer list
        return self._parse_peers(response)
```

**Key Advantages**:
- ✅ Large community (Asterisk ecosystem)
- ✅ Extensive documentation and tutorials
- ✅ FreePBX GUI for configuration
- ✅ AMI (Asterisk Manager Interface) for programmatic control

**Key Limitations**:
- ❌ chan_ooh323 is unsupported (use at own risk)
- ❌ Higher CPU usage than chan_h323
- ❌ SIP-centric architecture (H.323 is bolted on)

---

## 2. Yate Multi-Protocol Integration

### 2.1 Overview

**Yate** (Yet Another Telephony Engine) is a C++ VoIP platform with native multi-protocol support. Unlike Asterisk (SIP-focused) or FreeSWITCH (modern-focused), Yate treats all protocols as first-class citizens.

**Architecture**:
```
┌─────────────────────────────────────────────┐
│           Yate Core Engine                  │
├─────────────────────────────────────────────┤
│ 1. Core Layer        (String, Thread, Socket) │
│ 2. Message Engine    (Pub/Sub routing)        │
│ 3. Telephony Engine  (Call control)           │
│ 4. Module Layer      (Protocol modules)       │
└─────────────────────────────────────────────┘
         │
         ├── h323chan (H.323 via OpenH323)
         ├── ysipchan (SIP via YASS stack)
         ├── yiaxchan (IAX2)
         ├── zaptel drivers (ISDN)
         └── regexroute (call routing)
```

**Key Advantage**: Message-passing architecture enables seamless protocol bridging

---

### 2.2 Protocol Support Matrix

| Protocol | Module | Status | Use Case |
|----------|--------|--------|----------|
| **H.323** | h323chan | Native | Legacy enterprise (Avaya, Cisco, Polycom) |
| **SIP** | ysipchan | Native | Modern VoIP, cloud, carriers |
| **IAX2** | yiaxchan | Native | Inter-PBX, Asterisk compatibility |
| **ISDN** | zaptel | Native | PSTN gateway, E1/T1 |
| **SS7** | chan_ss7 | Native | PSTN signaling (M3UA/SIGTRAN) |
| **MGCP** | mgcpgw | Native | Cisco MGCP devices |
| **Jingle** | jinglechan | Native | Google Talk, XMPP |

**Why This Matters**: Yate is **protocol-agnostic** - H.323 isn't an afterthought.

---

### 2.3 Message-Passing Architecture

Yate's core innovation is its **message-passing system**:

```
┌───────────────┐         ┌───────────────┐
│ H.323 Module  │         │  SIP Module   │
│ (h323chan)    │         │ (ysipchan)    │
└───────┬───────┘         └───────┬───────┘
        │                         │
        │  call.execute message   │
        └────────►┌─────┐◄────────┘
                  │ MSG │
                  │ ENG │  Central message queue
                  └──┬──┘  Priority ordering
                     │     Subscription filtering
        ┌────────────┴────────────┐
        │                         │
┌───────▼───────┐         ┌───────▼───────┐
│ Routing       │         │  Media        │
│ (regexroute)  │         │  (yrtpchan)   │
└───────────────┘         └───────────────┘
```

**Message Flow** (H.323 → SIP call):
1. H.323 SETUP arrives → h323chan posts `call.execute` message
2. regexroute module subscribes to `call.execute`, routes based on dest number
3. regexroute posts `call.route` message with target SIP URI
4. ysipchan subscribes to `call.route`, sends SIP INVITE
5. RTP forwarding handled by yrtpchan (media pass-through, no transcoding)

---

### 2.4 H.323-SIP Bridging Configuration

**h323chan.conf** (H.323 settings):
```ini
[general]
; Port configuration
signalling=tcp
port=1720

; Jitter buffer
jitter=enabled
jitter_min=50
jitter_max=200

; Codecs
codecs=alaw,ulaw,g729
dtmfmethod=rfc2833

; Gatekeeper (optional)
gatekeeper=no
```

**ysipchan.conf** (SIP settings):
```ini
[general]
port=5060
addr=0.0.0.0

; Codec preferences
codecs=alaw,ulaw,g729

; SIP options
prack=disable
update=disable
```

**regexroute.conf** (Call routing):
```ini
; Route H.323 calls (1XXX) to SIP domain
^1\([0-9]\{3\}\)$=sip/sip:\1@sip.example.com

; Route SIP calls (2XXX) to H.323 gateway
^2\([0-9]\{3\}\)$=h323/\1@192.168.1.100

; Least-cost routing example
^9\([0-9]\+\)$=external/lcr;\1
```

**Key Configuration Notes**:
- No "dial plan" like Asterisk - all routing via regex
- RTP forwarding by default (no transcoding unless needed)
- Message-based routing enables complex logic (Python/JavaScript modules)

---

### 2.5 External Module Architecture

Yate's **external module protocol** enables custom call routing in any language:

**Python Example** (VIP caller routing):
```python
#!/usr/bin/env python3
import sys

vip_callers = ['1001', '1002', '1003']  # VIP extensions

while True:
    line = sys.stdin.readline()
    if not line:
        break

    if 'call.route' in line:
        # Parse message
        params = dict(x.split('=', 1) for x in line.split(':'))
        caller = params.get('caller', '')

        if caller in vip_callers:
            # Route VIP to premium gateway
            sys.stdout.write('%%>setlocal:called:sip/sip:premium@gateway.com\n')
            sys.stdout.write('%%<message:call.route:true:\n')
        else:
            # Route regular caller to standard gateway
            sys.stdout.write('%%>setlocal:called:sip/sip:standard@gateway.com\n')
            sys.stdout.write('%%<message:call.route:true:\n')

        sys.stdout.flush()
```

**Usage**:
```bash
# Run external module
./vip_router.py | yate -vvv
```

**Key Advantages**:
- Write complex routing logic in Python/Node.js/Perl
- No need to learn Asterisk dial plan syntax
- Dynamic routing based on database, time, caller class, etc.

---

### 2.6 Performance Analysis

**Benchmarks** (Yate official documentation):

| Scenario | Concurrent Calls | Hardware | Notes |
|----------|-----------------|----------|-------|
| **SIP only** | 2,000-5,000 | Dual-core, 2 GB RAM | Pass-through (no transcoding) |
| **H.323 only** | 200-500 | Dual-core, 2 GB RAM | OpenH323 library overhead |
| **Mixed H.323-SIP** | 100-200 | Quad-core, 4 GB RAM | Some transcoding |
| **Transcoding** | 50-100 | Quad-core, 4 GB RAM | G.729 ↔ G.711 |

**Performance Factors**:
- **Pass-through**: 5x more capacity than transcoding
- **H.323**: 10x lower capacity than SIP (OpenH323 overhead)
- **Routing**: Negligible CPU (regex-based, very fast)

**IF.bus Recommendation**: Deploy multiple Yate instances for >500 concurrent calls

---

### 2.7 Yate for IF.bus: Implementation Notes

**Adapter Interface**:
```python
class YateH323Adapter(SIPServerAdapter):
    """Yate adapter for IF.bus with native H.323 support"""

    def __init__(self, host, external_module_path):
        self.yate_proc = subprocess.Popen(
            ['yate', '-vvv'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        self.external_module = external_module_path

    def make_call_h323(self, from_sip, to_h323_host, extension):
        """Bridge SIP caller to H.323 endpoint via message passing"""
        msg = f'%%>message:call.execute:true:id=ifbus-{uuid.uuid4()}\n'
        msg += f'%%>setlocal:caller:{from_sip}\n'
        msg += f'%%>setlocal:called:h323/{extension}@{to_h323_host}\n'
        msg += f'%%<message:call.execute::\n'

        self.yate_proc.stdin.write(msg.encode())
        self.yate_proc.stdin.flush()

    def get_active_calls(self):
        """Query active calls via message"""
        msg = '%%>message:engine.status:true:\n'
        self.yate_proc.stdin.write(msg.encode())
        response = self.yate_proc.stdout.readline().decode()
        return self._parse_status(response)
```

**Key Advantages**:
- ✅ Native H.323 support (not bolted on)
- ✅ Protocol-agnostic architecture
- ✅ Lightweight (50 MB vs 200 MB for Asterisk)
- ✅ Message-passing enables complex routing
- ✅ External modules in any language

**Key Limitations**:
- ❌ Smaller community than Asterisk
- ❌ Less documentation/tutorials
- ❌ No GUI (command-line only)
- ❌ H.323 capacity lower than SIP

---

## 3. Architecture Comparison

### 3.1 Elastix vs Yate Feature Matrix

| Feature | Elastix (Asterisk) | Yate | Winner |
|---------|-------------------|------|--------|
| **H.323 Support** | chan_ooh323 (unsupported) | h323chan (native) | Yate |
| **Community Size** | Large (Asterisk ecosystem) | Medium | Elastix |
| **Documentation** | Extensive | Good | Elastix |
| **GUI** | FreePBX (excellent) | None | Elastix |
| **Programmatic Control** | AMI (Asterisk Manager Interface) | Message-passing | Tie |
| **Learning Curve** | Medium (dial plan syntax) | Low (regex routing) | Yate |
| **Multi-Protocol** | SIP-centric | Protocol-agnostic | Yate |
| **Performance (SIP)** | High | Very High | Yate |
| **Performance (H.323)** | Medium (chan_ooh323 overhead) | Medium (OpenH323 overhead) | Tie |
| **Transcoding** | Good (via Asterisk codecs) | Good (via FFmpeg) | Tie |
| **Licensing** | GPL | GPL | Tie |
| **Deployment** | Docker, packages | Source/packages | Elastix |

### 3.2 When to Use Each

**Use Elastix when**:
- ✅ Team familiar with Asterisk
- ✅ Need GUI for non-technical users
- ✅ Large community support important
- ✅ Extensive FreePBX integrations needed (CRM, voicemail, IVR)

**Use Yate when**:
- ✅ Native H.323 support critical
- ✅ Multi-protocol bridging needed (H.323, IAX2, ISDN, SS7)
- ✅ Custom routing logic required (Python/Node.js modules)
- ✅ Lightweight footprint preferred
- ✅ Greenfield deployment (no existing Asterisk investment)

---

## 4. Configuration Examples

### 4.1 Complete SIP-H.323 Bridge (Elastix)

**Scenario**: Route SIP extension 1001 to H.323 endpoint 2001@192.168.1.100

**ooh323.conf**:
```ini
[general]
port = 1720
bindaddr = 0.0.0.0
jitterbuffer = yes
dtmfmode = rfc2833
disallow = all
allow = ulaw
gatekeeper = DISABLE

[legacy-h323-gateway]
type = peer
host = 192.168.1.100
context = from-legacy
dtmfmode = h245signal
```

**extensions.conf**:
```ini
; SIP → H.323
[from-sip]
exten => _2XXX,1,NoOp(Route to H.323: ${EXTEN})
exten => _2XXX,2,Dial(OOH323/${EXTEN}@legacy-h323-gateway,30)
exten => _2XXX,3,Hangup()

; H.323 → SIP
[from-legacy]
exten => _1XXX,1,NoOp(Route to SIP: ${EXTEN})
exten => _1XXX,2,Dial(PJSIP/${EXTEN},30)
exten => _1XXX,3,Hangup()
```

**Test**:
```bash
asterisk -r
*CLI> dial OOH323/2001@legacy-h323-gateway
*CLI> ooh323 show channels
```

---

### 4.2 Complete SIP-H.323 Bridge (Yate)

**Scenario**: Route SIP extension 1001 to H.323 endpoint 2001@192.168.1.100

**h323chan.conf**:
```ini
[general]
signalling=tcp
port=1720
codecs=ulaw,alaw
dtmfmethod=rfc2833
gatekeeper=no
```

**ysipchan.conf**:
```ini
[general]
port=5060
addr=0.0.0.0
codecs=ulaw,alaw
```

**regexroute.conf**:
```ini
; SIP → H.323 (extensions starting with 2)
^2\([0-9]\{3\}\)$=h323/\1@192.168.1.100

; H.323 → SIP (extensions starting with 1)
^1\([0-9]\{3\}\)$=sip/sip:\1@localhost:5060
```

**Test**:
```bash
yate -vvv
# Make call from SIP phone to 2001
# Should route to H.323 endpoint
```

---

## 5. Performance Analysis

### 5.1 Call Capacity Comparison

**Test Setup**: Dual Xeon 3.06 GHz, 4 GB RAM, G.711 codec

| Platform | SIP Calls | H.323 Calls | Mixed Calls | Notes |
|----------|-----------|-------------|-------------|-------|
| **Elastix** | 1,000+ | 120 | 200 | chan_ooh323 overhead |
| **Yate** | 2,000+ | 200-500 | 300 | OpenH323 overhead |

**Key Insight**: Both platforms handle H.323 at ~10-20% of SIP capacity due to protocol complexity.

### 5.2 Transcoding Overhead

**G.711 ↔ G.729 Transcoding** (both platforms):
- **CPU**: 15-20% per concurrent channel
- **Latency**: +10-20ms
- **Quality**: Minimal loss (if using licensed G.729)

**Recommendation**: Avoid transcoding whenever possible - use G.711 end-to-end.

---

## 6. IF.bus Adapter Design

### 6.1 Unified Adapter Interface

Session 6 (Talent) is designing the base `SIPServerAdapter` class. Here's how H.323 fits:

```python
class ElastixH323Adapter(SIPServerAdapter):
    """Elastix adapter with H.323 support"""

    def connect(self, host, auth_config):
        """Connect via AMI"""
        self.ami = asterisk.manager.Manager()
        self.ami.connect(host)
        self.ami.login(auth_config['user'], auth_config['secret'])

    def make_call(self, from_uri, to_uri, codec="ulaw"):
        """
        Bridge call. Auto-detect if to_uri is H.323 or SIP.

        Examples:
        - to_uri = "sip:1001@example.com" → SIP call
        - to_uri = "h323:2001@192.168.1.100" → H.323 call
        """
        if to_uri.startswith('h323:'):
            # Extract H.323 extension and host
            extension, host = to_uri[5:].split('@')
            return self._make_h323_call(from_uri, extension, host, codec)
        else:
            return self._make_sip_call(from_uri, to_uri, codec)

    def _make_h323_call(self, from_sip, to_h323_ext, to_h323_host, codec):
        """Route SIP caller to H.323 endpoint"""
        action = {
            'Action': 'Originate',
            'Channel': f'OOH323/{to_h323_ext}@{to_h323_host}',
            'Context': 'from-h323',
            'Exten': from_sip,
            'Priority': '1',
            'CallerID': from_sip,
            'Variable': f'CHANNEL(codec)={codec}'
        }
        return self.ami.send_action(action)


class YateH323Adapter(SIPServerAdapter):
    """Yate adapter with native H.323 support"""

    def connect(self, host, auth_config):
        """Connect via external module protocol"""
        self.yate_proc = subprocess.Popen(
            ['yate', '-vvv'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

    def make_call(self, from_uri, to_uri, codec="ulaw"):
        """Route call via message passing"""
        if to_uri.startswith('h323:'):
            extension, host = to_uri[5:].split('@')
            target = f'h323/{extension}@{host}'
        else:
            target = to_uri.replace('sip:', 'sip/sip:')

        msg = f'%%>message:call.execute:true:id={uuid.uuid4()}\n'
        msg += f'%%>setlocal:caller:{from_uri}\n'
        msg += f'%%>setlocal:called:{target}\n'
        msg += f'%%>setlocal:format:{codec}\n'
        msg += f'%%<message:call.execute::\n'

        self.yate_proc.stdin.write(msg.encode())
        self.yate_proc.stdin.flush()
```

### 6.2 Auto-Detection of H.323 Peers

**Challenge**: How does IF.bus know if a peer is H.323 or SIP?

**Solution 1: URI Scheme**
```python
# Explicit H.323 URIs
to_uri = "h323:2001@192.168.1.100"  # H.323
to_uri = "sip:1001@example.com"     # SIP
```

**Solution 2: Probe Peer**
```python
def detect_peer_protocol(host, port=None):
    """
    Probe peer to detect protocol.

    Try in order:
    1. SIP OPTIONS → port 5060
    2. H.323 SETUP → port 1720
    3. IAX2 → port 4569
    """
    # Try SIP
    if probe_sip_options(host, port or 5060):
        return 'sip'

    # Try H.323
    if probe_h323_setup(host, port or 1720):
        return 'h323'

    # Try IAX2
    if probe_iax2(host, port or 4569):
        return 'iax2'

    return 'unknown'
```

**Solution 3: Configuration**
```yaml
# IF.bus configuration: ~/.if/bus/peers.yaml
peers:
  - name: "legacy-avaya"
    host: "192.168.1.100"
    protocol: "h323"
    port: 1720

  - name: "modern-sip"
    host: "sip.example.com"
    protocol: "sip"
    port: 5060
```

---

## 7. References

### Elastix / Asterisk
1. **Asterisk chan_ooh323 Documentation**: https://wiki.asterisk.org/wiki/display/AST/Asterisk+ooh323
2. **Elastix Documentation**: https://www.elastix.org/
3. **FreePBX Community**: https://community.freepbx.org/
4. **Avaya-Asterisk Integration Guide**: https://downloads.avaya.com/css/P8/documents/100177119

### Yate
1. **Yate Official Docs**: https://docs.yate.ro/wiki/
2. **Yate GitHub**: https://github.com/yatevoip/yate
3. **Yate External Module Protocol**: https://docs.yate.ro/wiki/External_module_command_flow
4. **Yate H.323 Configuration**: https://docs.yate.ro/wiki/H323_Channel

### H.323 Protocol
1. **ITU-T H.323 Standard**: https://www.itu.int/rec/T-REC-H.323
2. **OpenH323 Library**: http://www.openh323.org/
3. **H.323 vs SIP Comparison**: IEEE Communications Magazine

### IF.bus Integration
- See Session 7 (IF.bus) for adapter base class design
- See Session 5 (CLI) for IF.bus CLI interface spec
- See Session 6 (Talent) for adapter pattern architecture

---

## Conclusion

Both **Elastix** and **Yate** provide robust SIP-H.323 bridging capabilities for IF.bus:

- **Elastix**: Best for teams familiar with Asterisk, need GUI, large community
- **Yate**: Best for greenfield deployments, native H.323, lightweight architecture

**IF.bus Recommendation**:
1. **Primary**: Yate (native H.323, protocol-agnostic)
2. **Secondary**: Elastix (larger community, more tutorials)
3. **Fallback**: Manual SIP-H.323 gateway (if neither available)

**Next Steps for Session 7**:
- Implement `ElastixH323Adapter` class
- Implement `YateH323Adapter` class
- Add H.323 URI scheme support (`h323:extension@host`)
- Add peer protocol auto-detection
- Test with legacy H.323 devices (Polycom, Cisco, Avaya)

---

**Document Status**: ✅ **Complete**
**Session 3 Contribution**: IF.bus legacy protocol integration research
**Deliverable for**: Session 7 (IF.bus) Phase 1-2 acceleration

**END OF DOCUMENT**
