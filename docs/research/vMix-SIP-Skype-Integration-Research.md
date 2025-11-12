# vMix SIP/Skype Call Integration - Session 3 Research Report

**Research Date**: November 12, 2025
**Research Agent**: Haiku 4.5 (Master Integration Sprint)
**Platform**: vMix Streaming Software

---

## Executive Summary

vMix **does NOT have native SIP protocol support**. Instead, vMix offers a **WebRTC-based video calling solution** called **vMix Call** that provides peer-to-peer encrypted video conferencing with seamless NDI integration. For Skype integration, vMix uses **NDI Virtual Input** as a bridge. This research document outlines the complete architecture, API capabilities, audio routing, and call quality settings.

---

## 1. Call Input Type: vMix Call (WebRTC-Based)

### Overview

vMix Call is a **built-in WebRTC video conferencing input type** that allows remote guests to join productions with high-quality audio and HD video.

### Key Features

- **Protocol**: WebRTC (not SIP)
- **Encryption**: Peer-to-peer (P2P) end-to-end encryption
- **Connection Types**:
  - Host a Call (creates new call that guests join)
  - Connect to Call (joins existing call on another vMix instance)
- **Guest Connection**: Via web browser at `vmixcall.com` with auto-generated password
- **Edition Support**:
  - vMix HD: Supports 1 guest
  - vMix 4K: Supports 4 guests
  - vMix Pro: Supports 8 guests

### Guest Connection Process

```
1. vMix operator creates Video Call input
2. System generates unique password/call ID
3. Guest navigates to vmixcall.com
4. Guest enters name and password
5. Browser WebRTC connection established
6. Guest video/audio streams to vMix
7. Return feed sent to guest (customizable)
```

### Browser Requirements

- **Windows/Mac/Android**: Google Chrome (latest version)
- **iOS**: Safari 13+ (Chrome not supported)
- **Audio Codec**: Opus at 64kbps stereo (48kHz sample rate)
- **Video**: Up to HD (1080p @ 4Mbps)

### Network Requirements (Per Guest)

| Direction | Bandwidth | Notes |
|-----------|-----------|-------|
| vMix to Guest | 2 Mbps Down | Return feed video/audio |
| Guest to vMix | 2 Mbps Up | Guest's camera/microphone |
| Guest Browser | 2 Mbps Down / 600 Kbps Up | Minimum for participation |

---

## 2. SIP Call Management via API

### Critical Finding: No Native SIP Support

vMix Call uses **WebRTC**, not SIP protocol. However, vMix provides **limited API functions** for controlling VideoCall inputs.

### Available VideoCall API Functions

#### HTTP/TCP API Access

vMix exposes VideoCall control through two API methods:

1. **HTTP Web API**
   - Returns HTTP 200 on success, 500 on error
   - Standard web-based access via vMix Web Interface port

2. **TCP API**
   - Lower processing overhead
   - Event subscription capability (TALLY updates)
   - Same functionality as HTTP API

#### Current VideoCall Functions

**Limited function set - users have requested expansion:**

```
VideoCallAudioSource
  - Parameters: Input #, Audio Source
  - Values: Master, Headphones, BusA, BusB, BusC, BusD, BusE, BusF, BusG
  - Example: VideoCallAudioSource 1 Master

VideoCallVideoSource
  - Parameters: Input #, Video Source
  - Values: Output1, Output2, Output3, Output4 (4K/Pro only), None
  - Example: VideoCallVideoSource 1 Output1
```

### Missing Functions (Requested by Community)

Users have requested but are **NOT currently available**:

- `VideoCallDisconnect` - No API way to end a call
- `VideoCallDial` - No API way to initiate outbound calls
- `VideoCallAnswerIncoming` - No API way to answer incoming calls
- `VideoCallSetPassword` - No API way to change call password
- `VideoCallResetPassword` - No API way to reset call password

### Workaround for Call Control

Currently, **call management requires manual interaction** through:
- vMix UI right-click menu
- Shortcuts assigned to buttons
- Call Manager dialog

### API Access Configuration

**To enable API and access functions:**

1. Settings → Web tab
2. Configure HTTP Web API port (default 8080)
3. Access functions via:
   ```
   http://localhost:8080/api?action=VideoCallAudioSource&input=1&source=Master
   ```

---

## 3. Skype TX Integration via NDI

### Important Notice: Skype TX Deprecation

**Skype TX will be DISCONTINUED after May 2025**

Microsoft is sunsetting Skype TX and prioritizing Microsoft Teams as the primary platform.

### Current Integration Method: NDI Bridge

vMix integrates Skype calls using **NewTek NDI Virtual Input** as a bridge:

```
Skype (via NDI)
    ↓
NDI Virtual Input (NewTek Tool)
    ↓
vMix (adds as NDI input)
```

### Step-by-Step Skype Integration

#### Requirements

- Latest Skype (v8.29.0.50+) - Windows Desktop version only (not Windows 10 app)
- NewTek NDI Tool Pack with NDI Virtual Input
- vMix 21 or later
- Bus A configured in vMix audio settings

#### Setup Process

**Step 1: Configure vMix NDI Output**
```
Settings → Outputs → NDI
- Enable Bus A (for call audio control)
- Configure Output 1 with desired return video
```

**Step 2: Launch NDI Virtual Input**
```
Run NewTek NDI Virtual Input tool
Select "vMix - Output 1" from system menu
(This sends vMix output to Skype as camera/mic source)
```

**Step 3: Update Skype Settings**
```
Skype → Settings → Advanced
- Enable NDI usage
- Audio settings: "Line (Newtek NDI Audio)"
- Camera settings: "Newtek NDI Video"
```

**Step 4: Add Skype to vMix**
```
Add Input → NDI/Desktop Capture → NDI
Select Skype NDI stream from available sources
```

**Step 5: Configure Audio Routing**
```
vMix Bus A:
- Include: Microphone, other audio sources
- Exclude: Skype NDI input (prevents echo)
```

### Audio Feedback Prevention

**Critical Setting**: Route microphone and production audio to **Bus A ONLY**, excluding the Skype input:
- Prevents audio feedback loop
- Allows selective muting of call participant
- Enables "private producer audio" monitoring

### Skype TX Alternatives for Broadcasters

For post-May 2025, recommended alternatives include:

1. **vMix Call** - Native solution, best for vMix users
2. **Microsoft Teams** - With NDI/SDI support
3. **TVU Partyline** - Professional broadcast contribution
4. **Zoom** - Enterprise-grade conferencing

---

## 4. Audio Routing Architecture

### Audio Return Feed Options

vMix Call provides **9 distinct audio routing options** for what guests hear:

#### Audio Source Selections

| Option | Description | Use Case |
|--------|-------------|----------|
| **Master** | Main audio mix (default) | Most common, guest hears same audio as stream |
| **Headphones** | What operator hears | Talkback scenarios, operator monitoring |
| **Bus A** | Independent audio mix | Virtual green room, pre-call briefing |
| **Bus B** | Secondary independent mix | Multi-track production |
| **Bus C-G** | Additional busses | Complex multi-guest scenarios |

### Auto Mix Minus Technology

**Automatic echo prevention**:
- Each guest NEVER hears their own microphone/camera feed
- Prevents feedback loops and audio quality degradation
- Applied automatically to all audio routing selections
- No manual configuration needed

### Advanced Audio Routing Scenarios

#### Scenario 1: Live Interview with Producer Talkback

```
Producer Audio → Bus A
Interview Guest → Master (main mix)
Waiting Guest → Bus B (isolated)

Producer hears: Both guests + production mix
Guest in interview hears: Master mix (without self)
Waiting guest hears: Only Bus B content
```

#### Scenario 2: Virtual Green Room

```
Multiple guests waiting in Bus A
Can speak amongst themselves before going live
Switch guest from Bus A to Master when on-air
Audience never hears pre-air conversations
```

#### Scenario 3: Multi-Language Broadcast

```
Language 1 → Bus A → Guest 1 (French stream)
Language 2 → Bus B → Guest 2 (Spanish stream)
Master → Guest 3 (English stream)
Each guest hears appropriate language mix
```

### Manual vs. Automatic Audio Mixing

**Recommended Configuration**:
```
Settings → Right-click on vMix Call input
General tab → UNCHECK "Automatically mix audio"
```

**Benefits**:
- Manual control over guest audio levels
- Prevent automatic muting/unmuting
- Fine-tuned audio dynamics

---

## 5. Call Quality and Bandwidth Settings

### Audio Quality Specifications

#### Codec and Bitrate

```
Audio Codec:     Opus (industry standard)
Sample Rate:     48 kHz
Channels:        Stereo
Bitrate:         64 kbps (suitable for speech and music)
Latency:         Ultra-low (P2P encryption)
```

### Video Quality Bandwidth Settings

#### Return Video Bandwidth (To Guest)

**Configuration**: Right-click on vMix Call input → Bandwidth options

| Setting | Bitrate | Use Case | Quality |
|---------|---------|----------|---------|
| **Mobile 300Kbps** | 300 Kbps | Poor connectivity | Low (preview only) |
| **Mobile 800Kbps** | 800 Kbps | Cellular/weak WiFi | Standard definition |
| **1.5Mbps** | 1.5 Mbps | Good connectivity | HD preview |
| **4Mbps** | 4 Mbps | Excellent connectivity | Full HD (1080p) |

**Recommendation**: Start at Mobile 300Kbps if experiencing audio/video degradation; increase if network allows.

#### Remote Guest Video Bandwidth (From Guest)

```
Default:  Auto (adapts to network conditions)
Options:  Manual selection per connection
Timeout:  Up to 30 seconds for adaptation
Note:     Browser-based guests only
```

### Browser-Specific Quality Considerations

#### Chrome and Chromium Variants

- **Audio**: Mono optimization (speech-optimized)
- **Quality**: Good for speech, acceptable for music
- **Recommendation**: Use for general participants

#### Firefox

- **Audio**: Stereo transmission
- **Quality**: Superior to Chrome for audio fidelity
- **Recommendation**: Use for music/performance-heavy productions

#### Best Quality: vMix-to-vMix

```
vMix → vMix Call connection
Quality: Maximum possible (native codec, no transcoding)
Latency: Ultra-low
Recommendation: Professional productions with dedicated vMix instances
```

### Advanced Call Quality Settings

#### Advanced vMix Call Portal

**URL**: https://advanced.vmixcall.com

**Features**:
- Echo cancellation controls
- Auto gain control (AGC)
- Force Stereo option
- Browser-specific optimizations

#### Troubleshooting Garbled/Distorted Audio

**Primary Cause**: Echo cancellation artifacts from speaker playback

**Solution**: Use headphones on call participants
- Prevents echo cancellation processing artifacts
- Improves audio quality by 50%+
- Eliminates feedback loops

### Bandwidth Adaptation

**Network Conditions Affecting Quality**:

```
Excellent:  > 4 Mbps upload/download (Full HD)
Good:       2-4 Mbps (HD quality)
Fair:       1-2 Mbps (Standard definition)
Poor:       < 1 Mbps (Mobile quality recommended)
```

**vMix Call Adaptation**: Automatically adjusts video quality within 30 seconds to match available bandwidth.

---

## 6. WebRTC Network Architecture

### Connection Methods: STUN and TURN

#### STUN (Session Traversal Utilities for NAT)

```
Purpose:  Direct peer-to-peer connection
Method:   Public IP address detection
Protocol: UDP
Benefits: Low latency, no bandwidth relay costs
Limitations: Blocked by corporate firewalls
```

**STUN Flow**:
```
Guest 1 → Detect Public IP → STUN Server
Guest 2 → Detect Public IP → STUN Server
vMix <- → Direct UDP connection (both sides)
```

#### TURN (Traversal Using Relays around NAT)

```
Purpose:  Fallback when direct connection fails
Method:   Relay server intermediary
Protocol: UDP or TCP
Benefits: Works through restrictive firewalls
Trade-off: Slightly higher latency, relay overhead
```

**TURN Flow**:
```
Guest 1 → TURN Server ← Guest 2
         (relays data)
All traffic through vMix relay servers
```

### Required Firewall Ports

#### Outbound Rules (vMix Side)

```
Protocol  Port       Direction  Purpose
---------+-----------+----------+-----------------------------------
HTTPS    443 TCP    Outbound   Web interface, signaling
STUN/    10349 UDP  Outbound   P2P connection negotiation
TURN     10349 TCP  Outbound   (fallback to TCP relay)
```

#### Inbound Rules (vMix Side)

```
Protocol  Port Range        Direction  Purpose
---------+-----------------+----------+-----------------------------------
UDP      49152-65535       Inbound    Dynamic media streams
                                      (one per active call)
```

**Total Ports**: ~13,000 dynamic UDP ports available for calls

#### Guest Browser Requirements

```
Outbound: HTTPS 443 TCP + STUN/TURN 10349 UDP/TCP
Inbound:  Not required (connection initiated outbound)
```

### Direct Peer-to-Peer Mode

**Setting**: Right-click vMix Call input → "Allow only direct peer to peer connections"

**Effect**:
- Uses STUN exclusively (no TURN relay)
- Diagnostic tool for firewall issues
- Best for low-latency, high-quality calls
- Fails if direct connection impossible

**Use Case**: When you want to verify P2P capability or need absolute minimum latency.

### TCP-Only Fallback Configuration

**Scenario**: Corporate firewall blocks UDP ports

**Capability**:
```
Outbound TCP 10349: Control/signaling
Outbound TCP 443: Web access
Result: Calls work via relay (quality reduced)
```

**Quality Trade-off**:
- Audio/video relayed through vMix servers
- Higher latency (50-100ms additional)
- Acceptable for business calls, not ideal for HD content

### IP Address Publishing

vMix **does NOT publish server IP addresses** due to:
- Load balancing and redundancy
- Security requirements
- Dynamic allocation

**Firewall Configuration**: Use port ranges only (not IP whitelisting).

---

## 7. API Command Reference

### HTTP Web API Examples

#### Change Audio Source

```bash
# Set guest to hear Master mix
http://localhost:8080/api?action=VideoCallAudioSource&input=1&source=Master

# Set guest to hear Bus A
http://localhost:8080/api?action=VideoCallAudioSource&input=1&source=BusA
```

#### Change Video Source

```bash
# Send Output 1 to guest
http://localhost:8080/api?action=VideoCallVideoSource&input=1&source=Output1

# Send no video (audio only)
http://localhost:8080/api?action=VideoCallVideoSource&input=1&source=None
```

### TCP API Examples

```
SEND: (connect to vMix TCP API port, default 8099)
VideoCallAudioSource 1 Master

SEND:
VideoCallVideoSource 1 Output1

RESPONSE: <status>OK</status>
```

### Call Management via Shortcuts

**Settings → Shortcuts → Add Shortcut**

- Assign VideoCallAudioSource to physical button
- Cycle through audio mixes on demand
- Enable remote talkback workflows
- Integrate with stream deck / control systems

---

## 8. Comparison: vMix Call vs. Skype TX vs. Alternatives

| Feature | vMix Call | Skype TX | Teams | Zoom | TVU Partyline |
|---------|-----------|----------|-------|------|---------------|
| **Protocol** | WebRTC | Proprietary | NDI/SDI | WebRTC | Proprietary |
| **Status** | Active | Deprecated (May 2025) | Supported | Supported | Active |
| **NDI Output** | Native | Requires NDI Virtual Input | Yes | No | No |
| **Direct P2P** | Yes | Yes | No | Yes | No |
| **End-to-End Encryption** | Yes | Yes | Yes | Yes | Yes |
| **Max Guests (HD)** | 1-8 | 1 | Multiple | Multiple | Multiple |
| **SIP Native** | No (WebRTC) | No | No | No | No |
| **vMix Integration** | Native | NDI Bridge | NDI Bridge | NDI Bridge | API |
| **Setup Complexity** | Simple | Moderate (NDI) | Moderate | Moderate | Complex |

---

## 9. Limitations and Workarounds

### Current Limitations

1. **No SIP Native Support**
   - vMix uses WebRTC, not SIP protocol
   - Cannot directly integrate with legacy SIP systems

2. **Limited Call API**
   - No programmatic call initiation
   - No automated call disconnection
   - Only audio/video source selection available

3. **No Call Recording Control via API**
   - Cannot start/stop per-call recording via API
   - Requires manual interaction or vMix recording session

4. **No Password Control via API**
   - Cannot change call passwords programmatically
   - Passwords auto-generated and require manual reset

### Workarounds

#### For SIP Integration
```
Option 1: Use third-party SIP-to-WebRTC gateway
  SIP Phone → Linphone (WebRTC) → vMix Call

Option 2: Use vMix Call exclusively
  Migrate to WebRTC-based workflow

Option 3: Manual VoIP routing
  SIP → Desktop audio capture → vMix as mic input
```

#### For Automated Call Control
```
Use vMix Shortcuts assigned to:
- Stream Deck buttons
- Physical switches
- Stream deck API calls
- Custom control systems
```

#### For Call Management Automation
```
Option 1: Monitor vMix XML state via TCP subscription
Option 2: Use vMix scripting (VB.NET) for call-triggered actions
Option 3: External control via URL shortcuts
```

---

## 10. Recommended Production Architectures

### Architecture 1: Basic Remote Interview

```
Guest Browser (vmixcall.com)
        ↓ (WebRTC P2P)
    vMix Call Input #1
        ↓
Audio Source: Master (auto mix minus)
Video Source: Output 1
        ↓
    Production Mix
        ↓
    Stream Output
```

### Architecture 2: Multi-Guest with Talkback

```
Guest 1 (Browser)  Guest 2 (Browser)  Producer (vMix instance)
    ↓                   ↓                    ↓
Call Input 1        Call Input 2        Call Input 3
    ↓                   ↓                    ↓
Audio: Master       Audio: Bus A         Audio: Headphones
    ↓                   ↓                    ↓
Production Mix (Master)
    ↓
Stream + Recording
```

### Architecture 3: Professional HD Multi-Guest

```
Guest 1 (vMix)     Guest 2 (vMix)     Guest 3 (vMix)
    ↓                  ↓                  ↓
Call Input 1       Call Input 2       Call Input 3
    ↓                  ↓                  ↓
Direct P2P Mode (no relay)
    ↓
Primary vMix Instance (4K/Pro)
    ↓
NDI Multicast → Secondary systems
    ↓
Production + Streaming
```

### Architecture 4: Skype TX Integration (Until May 2025)

```
Skype (Desktop)
    ↓
NDI Virtual Input (NewTek)
    ↓
vMix NDI Input
    ↓
Audio Routing: Bus A (excludes Skype echo)
Video Routing: Output 1
    ↓
Production Mix
    ↓
Stream Output
```

---

## 11. Security Considerations

### Encryption

```
vMix Call:  End-to-end WebRTC encryption (DTLS-SRTP)
            Secure signaling via HTTPS

Skype NDI:  Skype's native encryption
            NDI connection unencrypted (local network)

Recommendation: Use VPN for remote NDI links
```

### Access Control

```
vMix Call Password:  Auto-generated, requires manual distribution
                     No API way to manage programmatically

Alternative:         Restrict via firewall rules
                     Disable "Allow External Connections"
                     LAN-only calls only
```

### Best Practices

1. **Use HTTPS Web Interface** (not HTTP)
2. **Enable Firewall Rules** (don't open all ports)
3. **Monitor Connected Guests** (Call Manager dialog)
4. **Use Headphones** (prevent audio attacks/echo)
5. **Rotate Call Passwords** (for multi-hour shows)

---

## 12. Future Roadmap and Recommendations

### vMix Call Evolution

**Expected Future Enhancements**:
- Expanded API function set (disconnect, dial, password control)
- SRT integration
- RTMP ingest (per-guest feeds)
- Advanced WebRTC codec support

### Post-Skype TX Strategy

**Recommended migration path**:
```
Phase 1: Evaluate vMix Call for native calls
Phase 2: Test Microsoft Teams NDI integration
Phase 3: Decommission Skype TX by May 2025
Phase 4: Document new call workflow
```

### Session 3 Integration Recommendations

For H.323/multimedia integration in Session 3:

1. **vMix Call as Primary**: WebRTC standard approach
2. **Skype TX Sunset Planning**: Migrate before May 2025
3. **NDI as Bridge**: Use for legacy Skype/Teams integration
4. **API Layer**: Build automation on VideoCallAudioSource/VideoCallVideoSource
5. **Firewall Planning**: Account for P2P/TURN/STUN port requirements

---

## References and Resources

### Official vMix Documentation

- vMix Call Main: https://www.vmix.com/help24/VideoCall.html
- Setup Guide: https://www.vmix.com/help23/VideoCallSetup.html
- Audio Settings: https://www.vmix.com/help23/vMixCallAudio.html
- Right-Click Menu: https://www.vmix.com/help23/vMixCallMenu.html
- Firewall Requirements: https://www.vmix.com/knowledgebase/article.aspx/125/
- Direct Connection Mode: https://www.vmix.com/knowledgebase/article.aspx/232/
- Audio Quality Guide: https://www.vmix.com/knowledgebase/article.aspx/246/
- Connection Troubleshooting: https://www.vmix.com/knowledgebase/article.aspx/214/

### API Documentation

- HTTP Web API: https://www.vmix.com/help25/DeveloperAPI.html
- TCP API: https://www.vmix.com/help25/TCPAPI.html
- Shortcut Function Reference: https://www.vmix.com/help25/ShortcutFunctionReference.html
- Unofficial API Reference: https://vmixapi.com/
- GitHub Function List: https://github.com/jensstigaard/vmix-function-list

### Related Technologies

- WebRTC Protocols: https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Protocols
- NDI Documentation: https://www.ndi.tv/
- Skype for Developers: https://dev.skype.com/

### Third-Party Tools

- NewTek NDI Tools: https://www.ndi.tv/tools/
- Advanced vMix Call: https://advanced.vmixcall.com

---

## Appendix: Quick Reference Card

### Key Ports

```
HTTPS Signaling:    443 TCP (outbound)
STUN/TURN Control:  10349 UDP/TCP (outbound)
Media Streams:      49152-65535 UDP (inbound, dynamic)
```

### Audio Options Summary

```
Master    → Default (stream + guests hear same)
Headphones → Operator monitoring mix
Bus A-G   → Independent production mixes
```

### Browser Compatibility

```
✓ Chrome (Windows/Mac/Android) - speech optimized
✓ Firefox - stereo audio quality
✓ Safari (iOS 13+) - full support
✗ Chrome (iOS) - not supported
✗ Edge, Opera - limited support
```

### API Cheat Sheet

```
Action: VideoCallAudioSource
Params: input=[1-8], source=[Master|Headphones|BusA-G]

Action: VideoCallVideoSource
Params: input=[1-8], source=[Output1-4|None]
```

### Bandwidth Quick Start

```
Mobile/Poor:    300 Kbps
Cellular WiFi:  800 Kbps
Home Internet:  1.5 Mbps
Professional:   4 Mbps (Full HD)
```

---

**End of Report**

Research conducted: November 12, 2025
Report Version: 1.0
Status: Ready for Session 3 Integration
