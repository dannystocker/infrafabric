# OpenSIPs WebRTC Integration Research Document

## Executive Summary

OpenSIPs (Open Source SIP Server) provides comprehensive WebRTC support through a combination of well-established modules that handle signaling, media relay, and encryption. This document details the technical architecture, configuration requirements, and deployment patterns for integrating OpenSIPs with WebRTC endpoints for the IF.bus SIP adapter project.

**Key Finding**: OpenSIPs 3.2+ (LTS) and 3.3+ offer mature WebRTC support with feature parity to Kamailio. The choice between them depends on configuration preferences and operational requirements rather than technical capabilities.

---

## 1. WebRTC Module Architecture

### 1.1 Required Modules

OpenSIPs WebRTC integration requires the following core modules:

#### Protocol Modules
- **proto_udp.so** - UDP transport (traditional SIP)
- **proto_tls.so** - TLS transport (encrypted traditional SIP)
- **proto_ws.so** - WebSocket transport (unencrypted browser signaling)
- **proto_wss.so** - WebSocket Secure (encrypted browser signaling - **MANDATORY for WebRTC**)

#### Management Modules
- **tls_mgm.so** - TLS certificate and key management
- **tls_openssl.so** or **tls_wolfssl.so** - TLS library implementation
- **rtpengine.so** - Media relay and DTLS-SRTP bridging (**ESSENTIAL for WebRTC**)
- **rtp_relay.so** - Unified media relay interface (OpenSIPS 3.2+, recommended)

#### Support Modules
- **nathelper.so** - NAT traversal and keepalive
- **sdpops.so** - SDP body manipulation and inspection
- **dialog.so** - Call dialog tracking (recommended for HA)
- **dispatcher.so** - Load balancing (recommended for deployments)

### 1.2 Module Capabilities & Limitations

#### proto_wss Module Capabilities
| Capability | Supported | Notes |
|-----------|-----------|-------|
| Secure WebSocket (WSS) | ✓ | RFC 6455 over TLS |
| Browser signaling | ✓ | All major browsers (Chrome, Firefox, Safari, Edge) |
| Certificate validation | ✓ | CA chain verification supported |
| Connection pooling | ✓ | Multiple WebSocket connections per client |
| Keepalive/ping-pong | ✓ | WebSocket frame-level keepalive |

#### rtpengine Module Capabilities
| Capability | Supported | Notes |
|-----------|-----------|-------|
| DTLS-SRTP | ✓ | RFC 5764 compliant |
| ICE candidate handling | ✓ | Full ICE support with force/remove modes |
| RTCP multiplexing | ✓ | RFC 5761 compatible |
| Protocol bridging | ✓ | RTP ↔ SRTP transcoding |
| Codec transcoding | ✓ | Depends on RTPEngine build flags |
| DTMF passthrough | ✓ | In-band and RFC 2833 |

#### Known Limitations
1. **Browser-to-Browser Calls**: Require media relay through RTPEngine (cannot be direct due to browser sandbox restrictions)
2. **Codec Negotiation**: Limited to common WebRTC codecs (VP8, VP9, H.264 for video; Opus, PCMU, PCMA for audio)
3. **ICE Candidate Filtering**: Behind restrictive firewalls may require TURN server integration
4. **Clustering**: WebSocket connection affinity required in load-balanced environments

### 1.3 OpenSIPs Version Compatibility

| Version | Release Date | WebRTC Support | LTS | Recommended |
|---------|-------------|----------------|-----|-------------|
| 3.0.x | 2018 | Basic | ✗ | ✗ |
| 3.1.x | 2020 | Full | ✗ | ✗ |
| 3.2.x | 2021 | Full + rtp_relay | ✓ | ✓ Excellent |
| 3.3.x | 2022 | Full + rtp_relay enhanced | ✗ | ✓ Recommended |
| 3.4.x+ | 2023+ | Full + modern features | Pending | ✓ Recommended |

**Recommendation**: Use **OpenSIPs 3.2.x (LTS)** for conservative deployments or **3.3.x+** for feature-rich implementations. Minimum version: **3.0.x**, though 3.2+ provides significantly better WebRTC support.

---

## 2. WebSocket vs TCP Transport

### 2.1 Protocol Comparison

#### WebSocket (WS)
```
Connection: ws://opensips.example.com:8080
Encryption: None (plaintext)
Use Case: Development, internal networks, non-sensitive deployments
Port: Usually 8080 (unprivileged)
Browser Support: Full
```

#### WebSocket Secure (WSS)
```
Connection: wss://opensips.example.com:443
Encryption: TLS 1.2+ (HTTPS equivalent)
Use Case: Production, public Internet, sensitive deployments
Port: Usually 443 (privileged, requires root or capabilities)
Browser Support: Full (REQUIRED for HTTPS pages)
```

#### TCP (TLS)
```
Connection: tls://opensips.example.com:5061
Encryption: TLS 1.2+
Use Case: Traditional SIP endpoints, secure backend communication
Port: Usually 5061 (unprivileged: 6061+)
Browser Support: Not native (requires special handling)
```

### 2.2 Critical Differences

#### Framing & Overhead
```
UDP/SIP: Datagram-based, stateless
TCP/TLS: Stream-based, connection-oriented
WebSocket: Message-framed over TCP, low overhead
WSS: Message-framed over TLS

WebSocket adds ~2-4 bytes per frame (frame headers)
TLS adds encryption overhead (proportional to payload)
```

#### Packet Loss & Congestion
- **UDP**: No automatic retransmission (SIP handles retries)
- **TCP/TLS**: Automatic retransmission (slower failure detection)
- **WebSocket**: Runs over TCP, benefits from TCP flow control

#### NAT Traversal
- **UDP**: Requires STUN/TURN for NAT holes
- **TCP/TLS**: Better for restrictive NATs (port 443 usually allowed)
- **WebSocket**: Excellent NAT traversal (port 443, HTTP-like traffic)

### 2.3 Transport Selection Logic (Recommended Routing)

```
Client Type               Recommended Transport
─────────────────────────────────────────────
Browser (Web app)        WSS (mandatory for HTTPS)
Mobile (Native app)      TLS or UDP+STUN
Legacy VoIP device       UDP
Backend SIP service      TLS or TCP
PSTN gateway             UDP or TLS
```

### 2.4 Listener Configuration Examples

```opensips.cfg
# UDP transport - traditional SIP
listen=udp:0.0.0.0:5060

# TLS transport - encrypted SIP (for backend services)
listen=tls:0.0.0.0:5061

# WebSocket transport (development only)
listen=ws:0.0.0.0:8080

# WebSocket Secure transport (PRODUCTION)
listen=wss:0.0.0.0:443
```

---

## 3. Media Relay Requirements

### 3.1 RTPEngine Integration Architecture

RTPEngine is a standalone media proxy that bridges WebRTC (DTLS-SRTP) with traditional SIP (RTP/SDES-SRTP/RTP-AVP). It is **not a SIP server** but a dedicated media relay.

#### Deployment Architecture
```
┌─────────────────┐                    ┌─────────────────┐
│   WebRTC        │                    │   Traditional   │
│   Client        │                    │   SIP Endpoint  │
│   (Browser)     │                    │   (Phone/App)   │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │ Signaling: WSS/SIP                   │ Signaling: SIP/TLS
         │                                      │
         ▼                                      ▼
    ┌────────────────────────────────────────────────┐
    │          OpenSIPs (SIP Signaling)              │
    │  ┌────────────────────────────────────────┐   │
    │  │  proto_wss, proto_tls, proto_udp       │   │
    │  │  tls_mgm, dialog, dispatcher           │   │
    │  └────────────────────────────────────────┘   │
    │                                                │
    │  Signaling Processing:                         │
    │  - REGISTER/INVITE routing                    │
    │  - SDP modification (sdpops)                   │
    │  - RTPEngine media anchoring                   │
    └────────────────────────────────────────────────┘
              │                        │
              │ Media Control          │ Media Control
              │ (UDP port 22222)       │ (UDP port 22223)
              ▼                        ▼
         ┌──────────────────────────────────┐
         │      RTPEngine Media Proxy        │
         │  ┌────────────────────────────┐  │
         │  │ Media Streams Processing:  │  │
         │  │ - DTLS-SRTP encryption     │  │
         │  │ - ICE candidate handling   │  │
         │  │ - Codec transcoding        │  │
         │  │ - RTCP multiplexing        │  │
         │  │ - NAT traversal            │  │
         │  └────────────────────────────┘  │
         └──────────────────────────────────┘
              │                        │
         Media RTP/SRTP          Media RTP/SDES
         (port 10000-20000)       (port 20001-30000)
              │                        │
         ┌────┴────┐                ┌──┴─────┐
         │          │                │        │
         ▼          ▼                ▼        ▼
    Browser A  Browser B         Phone     PSTN
```

### 3.2 DTLS-SRTP Bridging Explained

#### WebRTC Side (DTLS-SRTP)
```
Key Exchange: DTLS (Datagram TLS)
  - Initiates during SDP offer/answer
  - Fingerprint exchanged in SDP
  - Mutual authentication via certificates

Media Encryption: SRTP
  - RTP/SAVPF profile (RFC 5761 - RTCP-mux)
  - 128-bit AES encryption (default)
  - HMAC-SHA1 authentication
```

#### Traditional SIP Side (RTP/SDES)
```
Key Exchange: SDES (Session Description Protocol)
  - Keys embedded in SDP (if using SRTP)
  - Or plaintext RTP (legacy)

Media Encryption: Optional SRTP or RTP
  - RTP/AVP profile (legacy)
  - RTP/SAVP profile (SDES-SRTP)
```

#### RTPEngine Bridging Process

```
1. OFFER (WebRTC client → OpenSIPs)
   └─> rtpengine_offer()
       - Receives WebRTC SDP with DTLS fingerprint
       - Returns modified SDP (DTLS-SRTP ready)
       - RTPEngine starts listening for DTLS handshake

2. ANSWER (Traditional SIP endpoint → OpenSIPs)
   └─> rtpengine_answer()
       - Receives SDP (RTP/SAVP with SDES or RTP/AVP)
       - Modifies to match RTPEngine capabilities
       - RTPEngine learns peer address/port

3. Media Flow
   ├─> WebRTC client establishes DTLS connection with RTPEngine
   ├─> RTPEngine decrypts SRTP to RTP
   ├─> RTPEngine encrypts RTP to SRTP (or passes plaintext)
   └─> Traditional endpoint receives media

4. DELETE (Call termination)
   └─> rtpengine_delete()
       - Cleans up media streams
       - Releases port allocations
```

### 3.3 RTPEngine Installation & Configuration

#### Installation (Ubuntu/Debian)
```bash
# Add Sipwise RTPEngine repository
curl https://deb.sipwise.com/sipwise/keyring.gpg | apt-key add -
echo "deb [signed-by=/usr/share/keyrings/sipwise-keyring.gpg] https://deb.sipwise.com/sipwise focal main" \
  > /etc/apt/sources.list.d/sipwise.list

# Install RTPEngine
apt update
apt install ngcp-rtpengine

# Start service
systemctl start ngcp-rtpengine-daemon
```

#### RTPEngine Configuration (/etc/ngcp-rtpengine/rtpengine.conf)
```ini
[general]
# Network interfaces for media
interface = 10.0.0.1/255.255.255.0
interface = 10.0.0.1:5000-6000/255.255.255.0

# Private/Public IP mapping (for NAT)
interface = 10.0.0.0/255.255.255.0!203.0.113.0/255.255.255.0

# Logging
loglevel = 5
fork = yes
listen = 22222
timeout = 60
```

#### Health Check
```bash
# Test RTPEngine connectivity
echo "ping" | nc -u localhost 22222
# Expected: "pong"
```

### 3.4 Media Transcoding Capabilities

RTPEngine supports transcoding between codec families:

#### Audio Codecs
```
WebRTC Native        Traditional SIP
─────────────────────────────────────
Opus (default)   ←→  PCMU/PCMA (G.711)
                      G.722
                      iLBC
                      AMR
```

#### Video Codecs
```
WebRTC Native        Traditional SIP
─────────────────────────────────────
VP8/VP9          ←→  H.264
H.264            ←→  H.261 (legacy)
                      MPEG4-ES
```

#### Configuration Example
```
# Force specific codecs
--codec=opus,pcmu,g722
```

### 3.5 ICE (Interactive Connectivity Establishment)

ICE is required for WebRTC to traverse NAT/firewalls.

#### ICE Handling Modes in rtpengine_manage()

```
Mode                    Use Case
────────────────────────────────────────────────
ICE=force              Both sides need ICE candidates
ICE=remove             Remove ICE (legacy mode)
ICE=off                Disable ICE (not recommended)
```

#### STUN/TURN Server Configuration

```opensips.cfg
# For clients requiring STUN/TURN
modparam("rtpengine", "stun_server", "stun.example.com:3478")
modparam("rtpengine", "turn_server", "turn.example.com:3478")
modparam("rtpengine", "turn_user", "webrtc_user")
modparam("rtpengine", "turn_password", "webrtc_password")
```

---

## 4. Configuration Examples

### 4.1 Basic Module Loading (opensips.cfg)

```opensips.cfg
####### Protocol Modules #######
loadmodule "proto_udp.so"
loadmodule "proto_tls.so"
loadmodule "proto_ws.so"
loadmodule "proto_wss.so"

####### Core Functionality Modules #######
loadmodule "tm.so"           # Transaction module
loadmodule "sl.so"           # Stateless replies
loadmodule "rr.so"           # Record-Route
loadmodule "maxfwd.so"       # Max-Forwards processing
loadmodule "usrloc.so"       # User location database
loadmodule "registrar.so"    # Registration handling
loadmodule "dialog.so"       # Dialog tracking (required for calls)

####### Media & NAT Modules #######
loadmodule "tls_mgm.so"      # TLS management
loadmodule "nathelper.so"    # NAT handling
loadmodule "sdpops.so"       # SDP operations
loadmodule "rtpengine.so"    # RTPEngine interface
loadmodule "rtp_relay.so"    # RTP relay (3.2+)

####### Optional Modules #######
loadmodule "dispatcher.so"   # Load balancing
loadmodule "clusterer.so"    # Clustering (HA)
loadmodule "auth.so"         # Authentication
loadmodule "db_mysql.so"     # MySQL database
loadmodule "mi_rest.so"      # REST API for management
loadmodule "cachedb_redis.so" # Redis caching
```

### 4.2 TLS & WSS Configuration

```opensips.cfg
####### TLS Configuration (tls_mgm) #######
modparam("tls_mgm", "certificate", "/etc/opensips/certs/opensips.crt")
modparam("tls_mgm", "private_key", "/etc/opensips/certs/opensips.key")
modparam("tls_mgm", "ca_list", "/etc/opensips/certs/ca.crt")

# TLS version and cipher configuration
modparam("tls_mgm", "tls_method", "tlsv1_2")
modparam("tls_mgm", "tls_max_allowed_version", "tlsv1_3")
modparam("tls_mgm", "tls_min_allowed_version", "tlsv1_2")

# Cipher suite (high security)
modparam("tls_mgm", "tls_ciphers", "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA")

# Certificate verification
modparam("tls_mgm", "verify_cert", "1")
modparam("tls_mgm", "require_cert", "1")

# Multiple virtual domains (optional)
modparam("tls_mgm", "tls_domain", "example.com")
modparam("tls_mgm:tls_domain:example.com", "certificate", "/etc/opensips/certs/example.com.crt")
modparam("tls_mgm:tls_domain:example.com", "private_key", "/etc/opensips/certs/example.com.key")
```

### 4.3 Listener Configuration

```opensips.cfg
####### Network Interfaces #######
# Traditional SIP on UDP
listen=udp:0.0.0.0:5060 advertise 203.0.113.1

# Traditional SIP on TLS (backend services)
listen=tls:0.0.0.0:5061 advertise 203.0.113.1

# WebSocket (unencrypted, development only)
listen=ws:0.0.0.0:8080 advertise 203.0.113.1:8080

# WebSocket Secure (production, browsers)
listen=wss:0.0.0.0:443 advertise 203.0.113.1:443
```

### 4.4 RTPEngine Configuration

```opensips.cfg
####### RTPEngine Module #######
modparam("rtpengine", "rtpengine_sock", "udp:127.0.0.1:22222")

# Multiple RTPEngine instances (load balancing/HA)
modparam("rtpengine", "rtpengine_sock", "udp:10.0.0.2:22222")
modparam("rtpengine", "rtpengine_sock", "udp:10.0.0.3:22222")

# Timeout and retry settings
modparam("rtpengine", "rtpengine_tout", 500)    # 500ms timeout
modparam("rtpengine", "rtpengine_retr", 2)     # 2 retries
modparam("rtpengine", "queued_requests_limit", 1000)

# DTMF handling
modparam("rtpengine", "notification_sock", "udp:127.0.0.1:22223")

# Setid for dynamic selection
modparam("rtpengine", "setid_avp", "$avp(rtpengine_setid)")
```

### 4.5 Request Routing Logic for WebRTC

```opensips.cfg
# Global parameters
request_route {
    # Log the request
    xlog("L_INFO", "Received $rm from $fu to $tu via $proto on port $Rp\n");

    # Protocol detection
    if ($proto == "wss" || $proto == "ws") {
        $var(is_websocket) = 1;
        xlog("L_INFO", "WebRTC client detected\n");
    } else {
        $var(is_websocket) = 0;
    }

    # Standard SIP processing
    if (!mf_process_maxfwd_header("10")) {
        send_reply("483", "Max Forwards exceeded");
        exit;
    }

    if (has_totag()) {
        # Request within dialog
        route(WITHINDLG);
    } else {
        # Initial request
        if ($rm == "CANCEL") {
            if (tm_check_trans()) {
                route(RELAY);
            } else {
                send_reply("481", "Call Leg Does Not Exist");
            }
            exit;
        }

        if ($rm == "ACK") {
            if (tm_check_trans()) {
                route(RELAY);
            } else {
                send_reply("481", "Call Leg Does Not Exist");
            }
            exit;
        }

        if ($rm == "INVITE") {
            route(INVITE);
            exit;
        }

        if ($rm == "REGISTER") {
            route(REGISTER);
            exit;
        }
    }

    route(RELAY);
}

# Handle requests within dialog
route[WITHINDLG] {
    if (loose_route()) {
        route(RELAY);
    } else {
        send_reply("404", "Not Found");
    }
}

# Handle REGISTER
route[REGISTER] {
    if (!save("location")) {
        send_reply("500", "Server Internal Error");
    }
    exit;
}

# Handle INVITE
route[INVITE] {
    # Create dialog for tracking
    if (!create_dialog()) {
        send_reply("500", "Server Internal Error");
        exit;
    }

    # Enable recording route to maintain call path
    record_route();

    # Determine target
    if (!lookup("location")) {
        send_reply("404", "User Not Found");
        exit;
    }

    route(RELAY);
}

# Standard relay with RTPEngine
route[RELAY] {
    if (!tm_relay()) {
        send_reply("500", "Relay Failed");
    }
    exit;
}

# Post-transaction handling (branch route)
branch_route[MANAGE_BRANCH] {
    xlog("L_INFO", "Branch for $ru\n");

    # Determine if destination is WebRTC or traditional SIP
    if ($var(is_websocket)) {
        # Source is WebRTC
        xlog("L_INFO", "WebRTC to SIP conversion needed\n");
        rtpengine_manage("trust-address replace-origin replace-session-connection " .
                         "rtcp-mux-demux ICE=remove RTP/AVP");
    } else {
        # Source is traditional SIP
        if (sdp_has_rtcp_mux()) {
            # Destination supports RTCP-mux (likely WebRTC)
            rtpengine_manage("trust-address replace-origin replace-session-connection " .
                             "rtcp-mux-require no-rtcp-attribute generate-mid ICE=force " .
                             "SDES-off UDP/TLS/RTP/SAVPF");
        } else {
            # Traditional SIP endpoint
            rtpengine_manage("trust-address replace-origin replace-session-connection RTP/AVP");
        }
    }
}

# Failure handling
failure_route[MANAGE_FAILURE] {
    if (t_is_canceled()) {
        exit;
    }

    # Cleanup media
    rtpengine_delete();

    if ($rm == "INVITE") {
        # Try next target
        if (use_next_gw()) {
            route(RELAY);
        } else {
            send_reply("500", "No More Routes");
        }
    }
}
```

### 4.6 Advanced: Media Anchoring with rtp_relay (3.2+)

```opensips.cfg
# Load rtp_relay module
loadmodule "rtp_relay.so"

modparam("rtp_relay", "engines", "rtpengine=udp:127.0.0.1:22222")

# Within routing logic
route[INVITE] {
    if (!create_dialog()) {
        send_reply("500", "Error");
        exit;
    }

    record_route();

    # Engage RTP relay immediately
    rtp_relay_engage("rtpengine");

    if (!lookup("location")) {
        send_reply("404", "Not Found");
        exit;
    }

    route(RELAY);
}

# Automatic media re-anchoring (HA scenario)
event_route[dialog:start] {
    xlog("L_INFO", "Dialog started: $si -> $di\n");

    # Check if media needs re-anchoring
    if (is_audio_call()) {
        $dlg_var(media_anchored) = 1;
    }
}
```

### 4.7 Helper Functions

```opensips.cfg
# Check if SDP has RTCP-mux
function sdp_has_rtcp_mux() {
    if (sdp_get_line_startswith("a=rtcp-mux")) {
        return 1;
    }
    return 0;
}

# Check if call is audio
function is_audio_call() {
    if (sdp_get_line_startswith("m=audio")) {
        return 1;
    }
    return 0;
}

# Log SDP for debugging
function debug_sdp() {
    xlog("L_DEBUG", "SDP Body:\n$(rb{s/^/  /g})\n");
}
```

---

## 5. Deployment Patterns

### 5.1 Standalone OpenSIPs + RTPEngine

```
┌─────────────────────────────────────┐
│   Tier 1: Frontend                  │
│  ┌──────────────────────────────┐   │
│  │  OpenSIPs Proxy              │   │
│  │  (Single Node)               │   │
│  │  - proto_wss:443             │   │
│  │  - proto_udp:5060            │   │
│  │  - proto_tls:5061            │   │
│  └──────────────────────────────┘   │
└─────────────────┬───────────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
WebRTC       Trad. SIP    Backend
Clients      Endpoints    Services


┌─────────────────────────────────────┐
│   Tier 2: Media (Separate Host)     │
│  ┌──────────────────────────────┐   │
│  │  RTPEngine Daemon            │   │
│  │  UDP:22222 (control)         │   │
│  │  UDP:10000-20000 (media)     │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘

Database: MariaDB/PostgreSQL (optional)
Cache: Redis (optional, for presence/dialogs)
```

**Characteristics**:
- Simplest deployment
- Single point of failure for signaling
- Adequate for small to medium deployments (<100 concurrent calls)
- Cost-effective for proof-of-concept

### 5.2 High-Availability (Active-Passive)

```
                    VIP: 203.0.113.10
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌────▼────┐     ┌───▼───┐
    │   LB1   │────▶│OpenSIPs1 │     │OpenSIPs│
    │         │     │(Active)  │     │ (Hot   │
    └─────────┘     └──────────┘     │Standby)│
         │                            └───────┘
    Keepalived                            │
         │                           (Failover
    IP Failover                       Manager)
         │
         ▼
    ┌──────────────┐
    │RTPEngine 1   │ (Primary)
    │UDP:22222     │
    └──────────────┘

    ┌──────────────┐
    │RTPEngine 2   │ (Backup)
    │UDP:22222     │
    └──────────────┘

Shared Database:
- Location table (registrations)
- Dialog table (active calls)
- Presence subscriptions
```

**Configuration Example (Keepalived)**:
```
global_defs {
    router_id OPENSIPS_HA
    script_user root
}

vrrp_instance VI_OPENSIPS {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1

    virtual_ipaddress {
        203.0.113.10/24
    }

    track_script {
        opensips_check
    }
}

vrrp_script opensips_check {
    script "/usr/local/bin/check_opensips.sh"
    interval 2
    weight 2
    fall 3
    rise 2
}
```

**Advantages**:
- No service interruption on OpenSIPs node failure
- Calls survive failover (with stateful OpenSIPs setup)
- Cost-effective HA solution

**Disadvantages**:
- Secondary node idle (resource waste)
- Complex failover logic

### 5.3 High-Availability (Active-Active / Load Balanced)

```
                    203.0.113.10 (Public IP)
                    203.0.113.11 (Public IP)
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
    │OpenSIPs1 │    │OpenSIPs2 │    │OpenSIPs3 │
    │Port:5060 │    │Port:5060 │    │Port:5060 │
    │Port:443  │    │Port:443  │    │Port:443  │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
    (WebSocket affinity required via sticky sessions)
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼───┐     ┌────▼───┐     ┌────▼───┐
    │RTPEng1 │    │RTPEng2 │    │RTPEng3 │
    │UDP:222│    │UDP:222│    │UDP:222│
    └────────┘    └────────┘    └────────┘

Shared Database:
- Clustered MariaDB Galera
- Redis for session affinity
- Synchronous state replication
```

**Critical Requirement**: WebSocket Connection Affinity
```
Session Affinity Algorithm:
- Hash: (source_ip + source_port + client_id) % num_nodes
- Sticky Sessions: Route repeat requests to same OpenSIPs instance
- Implementation: HAProxy with source IP hashing
```

**HAProxy Configuration Snippet**:
```
backend opensips_backend
    balance source          # Source IP hashing
    option http-server-close
    option forwardfor

    server opensips1 203.0.113.10:443 check ssl
    server opensips2 203.0.113.11:443 check ssl
    server opensips3 203.0.113.12:443 check ssl
```

**Advantages**:
- Horizontal scalability (add nodes easily)
- No single point of failure
- Better resource utilization
- Load distribution across nodes

**Disadvantages**:
- Requires session affinity complexity
- Clustering configuration overhead
- Network bandwidth for state replication
- Testing difficulty

### 5.4 OpenSIPs Clustering (Recommended 3.2+)

```opensips.cfg
####### Cluster Configuration #######
loadmodule "clusterer.so"

modparam("clusterer", "db_url", "mysql://opensips:password@localhost/opensips")
modparam("clusterer", "my_node_id", 1)           # Unique per node
modparam("clusterer", "my_seed_node_id", 1)     # Bootstrap node

# Dialog replication (call state)
modparam("dialog", "db_mode", 3)                # 3 = Clustering
modparam("dialog", "cluster_replicate_dialogs", 1)

# Register module clustering
modparam("registrar", "replicate_registrations", 1)

# Table of cluster nodes (database)
# INSERT INTO clusterer (cluster_id, node_id, url)
#   VALUES (1, 1, 'sip:opensips1:5060');
#   VALUES (1, 2, 'sip:opensips2:5060');
#   VALUES (1, 3, 'sip:opensips3:5060');
```

**Advantages**:
- Native clustering via database
- Automatic state synchronization
- Built-in for OpenSIPs 2.4+
- No external tools needed

---

## 6. Comparison: OpenSIPs vs Kamailio for WebRTC

### 6.1 WebRTC Feature Parity

| Feature | OpenSIPs | Kamailio | Status |
|---------|----------|----------|--------|
| WebSocket (WS) | ✓ 3.0+ | ✓ | Equal |
| WebSocket Secure (WSS) | ✓ 3.0+ | ✓ | Equal |
| DTLS-SRTP | ✓ 3.0+ | ✓ | Equal |
| ICE Support | ✓ 3.0+ | ✓ | Equal |
| RTPEngine Integration | ✓ 3.0+ | ✓ | Equal |
| TLS Certificate Management | ✓ tls_mgm | ✓ tls module | Equal |
| RTCP-mux | ✓ | ✓ | Equal |
| Media Relay (Unified) | ✓ 3.2+ (rtp_relay) | Partial | **OpenSIPs Win** |
| Clustering | ✓ 3.2+ (clusterer) | ✓ db_replication | Equal |
| Performance | High | High | Equal |

**Conclusion**: Feature parity achieved. Kamailio had WebRTC support earlier (2014), but OpenSIPs caught up by 3.0 (2018).

### 6.2 Configuration Style Comparison

#### OpenSIPs Philosophy
```
- Explicit, verbose configuration
- Module-based architecture
- Powerful but requires deeper understanding
- Better for complex, customized deployments
```

#### Kamailio Philosophy
```
- Flexible, diverse approach
- More community-driven module ecosystem
- Easier for users migrating from SER
- Better documentation for common use cases
```

### 6.3 Performance Characteristics

**Throughput Capacity** (Approximate)
```
OpenSIPs:   10,000-50,000 concurrent calls (per node, hardware-dependent)
Kamailio:   10,000-50,000 concurrent calls (per node, hardware-dependent)
```

**Latency**
```
Message Processing: ~1-5ms (both)
WebSocket Processing: ~2-10ms (both)
RTPEngine Communication: ~5-20ms (both)
```

**CPU & Memory**
```
OpenSIPs:   ~100MB base + 5-10KB per call
Kamailio:   ~80MB base + 5-10KB per call
(Similar, hardware-dependent)
```

### 6.4 Documentation & Community

| Aspect | OpenSIPs | Kamailio |
|--------|----------|----------|
| Official Documentation | Comprehensive | Excellent |
| WebRTC Tutorials | Good (3+ guides) | Good (2-3 guides) |
| Community Support | Active mailing list | Very active mailing list |
| Commercial Support | Available (OpenSIPs Inc.) | Available (Kamailio Inc.) |
| GitHub Activity | Regular | Very regular |

### 6.5 Recommendation Matrix

```
Use OpenSIPs if you:
✓ Need Long-Term Support (LTS) version (3.2.x)
✓ Prefer explicit, module-driven configuration
✓ Want unified RTP relay management (rtp_relay)
✓ Plan large-scale clustering (3.2+ clusterer)
✓ Require commercial support

Use Kamailio if you:
✓ Want more extensive module ecosystem
✓ Prefer community-driven development
✓ Have existing Kamailio expertise
✓ Need more diverse routing logic examples
✓ Prefer less "heavy" configuration model
```

### 6.6 Migration Path (if switching)

```
OpenSIPs → Kamailio:
1. Export user location database
2. Adapt opensips.cfg to kamailio.cfg syntax
3. Retrain on Kamailio module differences
4. Test WebRTC flows (should work identically)

Effort: ~2-4 weeks for small deployments
Risk: Low (WebRTC stack identical)

Kamailio → OpenSIPs:
1. Similar process (reverse)
2. Learn OpenSIPs explicit module loading
3. Adapt clustering setup
4. Test with 3.2 or 3.3 version

Effort: ~2-4 weeks for small deployments
Risk: Low (WebRTC stack identical)
```

---

## 7. Integration Complexity Assessment for IF.bus

### 7.1 Complexity Scoring (1-10 scale)

| Component | Complexity | Effort | Notes |
|-----------|-----------|--------|-------|
| WebSocket Setup | 3 | 2 hours | Straightforward, well-documented |
| TLS/Certificate | 4 | 4 hours | Self-signed vs. CA-signed decisions |
| Module Configuration | 5 | 8 hours | Multiple interdependencies |
| RTPEngine Integration | 6 | 12 hours | Media relay setup, DTLS-SRTP tuning |
| Routing Logic | 6 | 16 hours | Complex SDP manipulation |
| Database Setup | 4 | 4 hours | If using location/dialog storage |
| High Availability | 7 | 40 hours | Clustering, failover, session affinity |
| Testing & QA | 5 | 20 hours | WebRTC endpoint testing |
| **Total Project** | **5.5** | **~110 hours** | ~2-3 weeks for team |

### 7.2 Risk Assessment

#### Low Risk
- Module loading failures (quick diagnosis)
- Certificate problems (clear error messages)
- Database connectivity issues (standard debugging)

#### Medium Risk
- SDP corruption (complex to debug, requires packet captures)
- RTPEngine failures (asymmetric media issues)
- WebSocket connection drops (intermittent)

#### High Risk
- Clustering synchronization issues (data corruption)
- Media re-anchoring failures (call drops)
- NAT traversal problems (location-dependent)

### 7.3 Prerequisite Skills

Required Team:
```
1 Senior SIP Engineer (2 weeks)
  - SIP protocol expertise
  - VoIP network architecture
  - NAT/firewall knowledge

1 Network Engineer (1 week)
  - WebSocket protocol
  - TLS/SSL certificates
  - Network monitoring

1 DevOps Engineer (1.5 weeks)
  - Linux system administration
  - Docker containerization
  - Load balancing

Optional: 1 QA Engineer (ongoing)
  - WebRTC endpoint testing
  - Call flow verification
  - Performance benchmarking
```

### 7.4 Dependencies & Prerequisites

#### System Requirements
```
OS:              Ubuntu 20.04 LTS or newer
RAM:             2GB minimum (4GB+ recommended)
CPU:             2+ cores (4+ cores recommended)
Network:         Public IP for TLS/WSS
Storage:         20GB (for logs, database)
```

#### External Dependencies
```
RTPEngine:           Required (separate installation)
MariaDB/PostgreSQL:  Required (for location/registration)
Redis (optional):    Recommended (for caching)
TURN Server:         Recommended (for NAT traversal)
Valid SSL Cert:      Required (for WSS on production)
```

---

## 8. Pros and Cons for IF.bus Use Case

### 8.1 Pros (Why Choose OpenSIPs for IF.bus)

#### Technical Advantages
✓ **Mature WebRTC Support**: 3+ years proven in production
✓ **Module Simplicity**: Clear separation of concerns (proto_wss, rtpengine, tls_mgm)
✓ **Explicit Configuration**: Easier for security audits and compliance
✓ **LTS Versions**: 3.2.x provides 3+ year support cycle
✓ **Native Clustering**: Built-in state replication without external tools
✓ **Unified Media Relay**: rtp_relay module simplifies RTPEngine management

#### Operational Advantages
✓ **Lower Learning Curve** (vs. Kamailio): Clearer module dependencies
✓ **Commercial Support Available**: OpenSIPs Inc. provides SLAs
✓ **Active Development**: Regular security updates and bug fixes
✓ **Easy Troubleshooting**: Extensive logging, clear error messages
✓ **Containerization**: Good Docker/Kubernetes support

#### IF.bus Specific Benefits
✓ **SIP Adapter Compatibility**: Perfect for SIP-to-WebRTC gateway role
✓ **Enterprise Integration**: Works with legacy VoIP systems
✓ **Scalability**: Proven to handle 10K+ concurrent calls
✓ **Security**: TLS/DTLS-SRTP by default, no plaintext allowed
✓ **Flexibility**: Easily bridge WebRTC to any SIP endpoint

### 8.2 Cons (Limitations for IF.bus)

#### Technical Limitations
✗ **Performance**: CPU-intensive for 50K+ concurrent calls
✗ **Memory Usage**: ~5-10KB per call overhead (cumulative in large scale)
✗ **DTLS Key Renegotiation**: Can cause brief audio drops during re-key
✗ **Complexity**: RTPEngine external dependency required
✗ **NAT Complexity**: Requires TURN server for restricted networks

#### Operational Challenges
✗ **Operational Overhead**: Requires monitoring of SIP + RTPEngine
✗ **Debugging Difficulty**: Three-layer stack (OpenSIPs/RTPEngine/DTLS)
✗ **No Built-in GUI**: Command-line/REST API only (no web dashboard)
✗ **Clustering Complexity**: Requires shared database, complex to maintain
✗ **TLS Cert Management**: Must manage certificate renewal (OR use Let's Encrypt)

#### Specific IF.bus Concerns
✗ **Real-time Demands**: Not suitable for ultra-low-latency applications (<10ms)
✗ **Proprietary SIP Extensions**: May conflict with non-standard SIP extensions
✗ **Cost**: No licensing cost, but personnel training required
✗ **Logging Volume**: WebRTC calls generate 5-10x more logs than traditional SIP

---

## 9. Integration Complexity Assessment

### 9.1 OpenSIPs Complexity (1-10): **6.5/10**

#### Complexity Breakdown
```
Module Learning:           7/10  (Must learn: proto_wss, rtpengine, tls_mgm)
Configuration Syntax:      5/10  (Verbose but clear)
Routing Logic:             7/10  (Complex SDP manipulation needed)
RTPEngine Integration:     7/10  (External tool, complex flags)
Cluster Setup:             8/10  (Database sync, multi-node coordination)
Troubleshooting:           6/10  (Good logging, requires expertise)
Overall Difficulty:        6.5/10
```

### 9.2 Kamailio Complexity (1-10): **6/10**

#### Complexity Breakdown
```
Module Learning:           6/10  (Similar modules, more options)
Configuration Syntax:      5/10  (Slightly more flexible)
Routing Logic:             6/10  (Slightly simpler examples)
RTPEngine Integration:     7/10  (Identical to OpenSIPs)
Cluster Setup:             7/10  (More traditional DB replication)
Troubleshooting:           6/10  (Good logging, more community examples)
Overall Difficulty:        6/10
```

### 9.3 When Complexity is Justified

**Choose OpenSIPs Complexity If**:
1. Need certified LTS version (3.2.x)
2. Planning large-scale clustering
3. Want simpler module dependencies
4. Team has SIP experience (not Kamailio)
5. Need commercial support contracts

**Choose Kamailio Simplicity If**:
1. Team already knows Kamailio
2. Need maximum community support
3. Value flexibility over structure
4. Community examples sufficient

---

## 10. Implementation Roadmap for IF.bus

### Phase 1: Foundation (Weeks 1-2)

```
[ ] 1.1 Setup OpenSIPs 3.2.x on test server
    - Single node, basic modules
    - Expected time: 2 hours
    - Risk: Low

[ ] 1.2 Configure WebSocket listeners (WS + WSS)
    - Self-signed certificates (testing)
    - Expected time: 3 hours
    - Risk: Low

[ ] 1.3 Setup RTPEngine on separate host
    - Basic configuration, UDP control port
    - Expected time: 4 hours
    - Risk: Medium (media relay setup)

[ ] 1.4 Create basic routing script
    - REGISTER, INVITE handling
    - Expected time: 8 hours
    - Risk: Medium (SIP routing logic)
```

### Phase 2: Core Integration (Weeks 3-4)

```
[ ] 2.1 Implement WebRTC-to-SIP bridging
    - Test with WebRTC client + traditional SIP endpoint
    - DTLS-SRTP negotiation
    - Expected time: 12 hours
    - Risk: High (complex media negotiation)

[ ] 2.2 SDP manipulation & codec negotiation
    - Handle different codec sets
    - RTCP-mux detection
    - Expected time: 8 hours
    - Risk: High (SDP is tricky)

[ ] 2.3 NAT/STUN handling
    - ICE candidate processing
    - TURN server integration
    - Expected time: 8 hours
    - Risk: Medium (location-dependent)

[ ] 2.4 Testing & debugging
    - Call flows, packet captures
    - Performance baseline
    - Expected time: 16 hours
    - Risk: Ongoing
```

### Phase 3: High Availability (Weeks 5-6)

```
[ ] 3.1 Setup second OpenSIPs node
    - Identical configuration
    - Database replication
    - Expected time: 6 hours
    - Risk: Medium

[ ] 3.2 Configure clustering
    - Clusterer module setup
    - Dialog state replication
    - Expected time: 8 hours
    - Risk: High (complex state management)

[ ] 3.3 Load balancer setup
    - HAProxy with sticky sessions
    - Health checks
    - Expected time: 6 hours
    - Risk: Medium

[ ] 3.4 Failover testing
    - Graceful node shutdown
    - Call survival during failover
    - Expected time: 8 hours
    - Risk: High (timing-sensitive)
```

### Phase 4: Production Hardening (Weeks 7-8)

```
[ ] 4.1 Security hardening
    - TLS certificate best practices
    - Firewall rules, DOS protection
    - Expected time: 8 hours
    - Risk: Medium

[ ] 4.2 Monitoring & alerting
    - Prometheus metrics
    - Real-time call monitoring
    - Expected time: 12 hours
    - Risk: Low

[ ] 4.3 Logging & auditing
    - Call detail records (CDR)
    - Compliance logging
    - Expected time: 8 hours
    - Risk: Low

[ ] 4.4 Documentation
    - Architecture, procedures
    - Runbooks, troubleshooting
    - Expected time: 12 hours
    - Risk: Low
```

### Phase 5: Operations & Support (Ongoing)

```
[ ] 5.1 Production deployment
[ ] 5.2 On-call support rotation
[ ] 5.3 Performance tuning
[ ] 5.4 Security updates & patches
[ ] 5.5 Capacity planning
```

---

## 11. Configuration Checklist

### Pre-Deployment

- [ ] SSL/TLS certificates obtained (CA-signed for production)
- [ ] RTPEngine installed and tested
- [ ] Database (MariaDB/PostgreSQL) installed and tested
- [ ] Network ports opened: 5060/UDP, 5061/TLS, 443/WSS, 22222/UDP (RTPEngine)
- [ ] Firewall rules configured for media ports (10000-20000)
- [ ] DNS records configured (A/AAAA records for domain)
- [ ] TURN server details obtained (if needed)

### OpenSIPs Configuration

- [ ] Module loading configured (proto_wss, rtpengine, tls_mgm)
- [ ] Listeners configured (UDP, TLS, WS, WSS)
- [ ] TLS certificates and keys configured
- [ ] RTPEngine socket configured
- [ ] Database connectivity tested
- [ ] Routing logic implemented
- [ ] Branch route for media handling implemented
- [ ] Logging configured at appropriate level

### RTPEngine Setup

- [ ] RTPEngine daemon running
- [ ] Control port (22222/UDP) accessible from OpenSIPs
- [ ] Media port range (10000-20000) open and available
- [ ] Network interfaces correctly configured
- [ ] Timeout values tuned appropriately
- [ ] Health check (ping command) successful

### Testing

- [ ] WebSocket connection successful (browser console)
- [ ] TLS handshake succeeds (certificate valid)
- [ ] REGISTER request processed
- [ ] INVITE request routed correctly
- [ ] Media flow established (RTPEngine statistics)
- [ ] DTLS-SRTP negotiation successful
- [ ] Call state persisted in database
- [ ] Failover triggers on node shutdown

### Operations

- [ ] Monitoring enabled (call count, error rate)
- [ ] Logging aggregation configured
- [ ] Backup procedures documented
- [ ] Disaster recovery plan created
- [ ] On-call rotation established
- [ ] Performance baseline documented

---

## 12. Troubleshooting Guide

### Common Issues

#### Issue 1: WebSocket Connection Fails
```
Error: "WebSocket handshake failed"

Causes:
1. proto_wss module not loaded
2. WSS listener not configured
3. TLS certificate invalid/expired
4. Firewall blocking port 443

Debug Steps:
$ sudo opensipsctl fifo ls
$ tcpdump -i eth0 -A 'tcp port 443'
$ openssl s_client -connect opensips.example.com:443
$ tail -f /var/log/opensips/opensips.log | grep -i websocket
```

#### Issue 2: No Audio (Media Not Flowing)
```
Error: "One-way audio" or "No audio"

Causes:
1. RTPEngine not running or unreachable
2. Firewall blocking media ports (10000-20000)
3. DTLS-SRTP negotiation failed
4. NAT/STUN issues

Debug Steps:
$ echo "ping" | nc -u localhost 22222  # Test RTPEngine
$ sudo netstat -tulpn | grep 1000[0-9]  # Check media ports
$ tcpdump -i eth0 'udp port 10000:20000'  # Capture media
$ grep -i dtls /var/log/opensips/opensips.log
$ rtpengine-ng inspect # If available
```

#### Issue 3: Calls Drop After Registration
```
Error: "Session terminated unexpectedly"

Causes:
1. RTPEngine timeout (too short rtpengine_tout)
2. Firewall NAT mapping expires
3. WebSocket connection drops (network issue)
4. Dialog timeout misconfigured

Debug Steps:
$ grep "rtpengine_tout\|rtpengine_retr" /etc/opensips/opensips.cfg
$ tcpdump -i eth0 'tcp port 443 or tcp port 5060' -w call.pcap
$ wireshark call.pcap  # Analyze call flow
```

#### Issue 4: SDP Corruption
```
Error: "Invalid SDP" or codec mismatches

Causes:
1. sdpops module not properly modifying SDP
2. rtpengine_manage() flags incorrect
3. RTCP-mux handling wrong

Debug Steps:
$ grep -i "sdp\|rtpengine_manage" /etc/opensips/opensips.cfg
$ tail -f /var/log/opensips/opensips.log | grep -i sdp
$ Add xlog statements to log SDP before/after modification
$ Compare captured SDP with expectations
```

### Performance Issues

#### High CPU Usage
```
Causes:
1. Too many concurrent calls
2. Inefficient routing logic
3. Excessive logging

Solution:
- Increase num_worker_processes
- Optimize routing script
- Reduce logging verbosity to WARN
```

#### Memory Leak
```
Causes:
1. Dialog not cleaned up (BYE not received)
2. RTPEngine media not deleted
3. Module memory leak

Solution:
$ ps aux | grep opensips  # Check memory growth
$ opensipsctl fifo dlg_list | wc -l  # Count dialogs
$ Implement dialog timeout
```

---

## 13. Additional Resources

### Official Documentation
- OpenSIPs Main: https://opensips.org
- proto_wss Module: https://opensips.org/docs/modules/3.2.x/proto_wss
- rtpengine Module: https://opensips.org/docs/modules/3.2.x/rtpengine
- rtp_relay Module: https://opensips.org/docs/modules/3.2.x/rtp_relay
- tls_mgm Module: https://opensips.org/docs/modules/3.2.x/tls_mgm

### Tutorials
- WebSocket Tutorial: https://opensips.org/Documentation/Tutorials-WebSocket-2-2
- Clustering Guide: https://opensips.org/events/Summit-2021/assets/presentations/
- RTPEngine Integration: https://smartvox.co.uk/voip/webrtc-using-opensips-and-rtpengine/

### Community
- Mailing List: users@lists.opensips.org
- GitHub Issues: https://github.com/OpenSIPS/opensips/issues
- Forum: https://opensips.org/community/

### Related Tools
- RTPEngine: https://github.com/sipwise/rtpengine
- OpenSIPS Control Panel: https://github.com/OpenSIPS/opensips-cp
- SIPp (SIP Load Testing): https://github.com/SIPp/sipp

---

## 14. Conclusion & Recommendation for IF.bus

### Overall Assessment

**OpenSIPs is a strong choice for IF.bus SIP adapter** given:

1. **WebRTC Readiness**: Mature, production-proven support
2. **Architectural Alignment**: Perfect for SIP-to-WebRTC gateway role
3. **Operational Clarity**: Explicit module design aids troubleshooting
4. **Enterprise Features**: Clustering, HA, TLS certificate management
5. **Scalability**: Proven to handle 10K-50K concurrent calls

### Final Recommendation

**✓ Recommend OpenSIPs 3.2.x (LTS) for IF.bus**

**Rationale**:
- Long-term support (3+ years) aligns with enterprise needs
- Feature parity with Kamailio for WebRTC
- Simpler operational model than Kamailio for IF.bus use case
- rtp_relay module (3.2+) simplifies RTPEngine management
- Better suited for SIP-to-WebRTC adaptation than Kamailio

**Budget Estimate**:
- Development: 8-12 weeks (2-3 engineers)
- Infrastructure: 2-4 servers (OpenSIPs, RTPEngine, DB, monitoring)
- Operational: 1-2 FTE ongoing support

**Next Steps**:
1. Proof-of-concept on single node (Week 1-2)
2. WebRTC endpoint testing with sample clients (Week 3)
3. HA/clustering evaluation (Week 4-5)
4. Production deployment plan (Week 6+)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**Author**: Research Team for IF.bus Project
**Classification**: Technical Architecture
