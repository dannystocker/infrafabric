# OpenSIPs WebRTC Architecture & Implementation Guide

---

## 1. System Architecture Overview

### 1.1 High-Level WebRTC Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                           SIGNALING PATH                             │
│                      (SIP over WebSocket Secure)                     │
└─────────────────────────────────────────────────────────────────────┘

    Browser A                OpenSIPs Proxy              SIP Phone
    (WebRTC)              (Signaling Server)            (Traditional)
        │                         │                          │
        │──────── INVITE (WSS) ──▶│                          │
        │                         │                          │
        │                         │──── INVITE (UDP/TLS) ──▶│
        │                         │                          │
        │                         │◀──── 180 Ringing ────────│
        │◀─── 180 Ringing (WSS) ──│                          │
        │                         │                          │
        │                         │◀──── 200 OK ─────────────│
        │◀─── 200 OK (WSS) ───────│                          │
        │                         │                          │
        │────── ACK (WSS) ───────▶│                          │
        │                         │────── ACK (UDP) ────────▶│
        │                         │                          │

┌─────────────────────────────────────────────────────────────────────┐
│                            MEDIA PATH                                │
│                        (Audio/Video RTP Stream)                      │
└─────────────────────────────────────────────────────────────────────┘

    Browser A                   RTPEngine                 SIP Phone
    (DTLS-SRTP)            (Media Relay)            (RTP or SDES-SRTP)
        │                         │                          │
        │◀────────────────────────│◀─────── Media ──────────│
        │                         │                          │
        │───────── Media ────────▶│────────────────────────▶│
        │                         │                          │
        └─────────────────────────┴──────────────────────────┘
             (Bidirectional DTLS-SRTP)  (DTLS or RTP)
```

### 1.2 Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐                         ┌──────────────────┐  │
│  │  Web Browser    │                         │  SIP Endpoint    │  │
│  │  (WebRTC)       │                         │  (Phone/App)     │  │
│  │                 │                         │                  │  │
│  │ - WebRTC API    │                         │ - SIP Stack      │  │
│  │ - JsSIP lib     │                         │ - RTP/SRTP       │  │
│  │ - getUserMedia  │                         │ - Media Codecs   │  │
│  └────────┬────────┘                         └────────┬─────────┘  │
│           │                                           │              │
└───────────┼───────────────────────────────────────────┼──────────────┘
            │                                           │
            │ Signaling: WSS (SIP over WebSocket)      │ Signaling: UDP/TLS (SIP)
            │ Media: DTLS-SRTP                         │ Media: RTP/SAVP/AVP
            │                                           │
┌───────────▼───────────────────────────────────────────▼──────────────┐
│                       SIGNALING LAYER                                 │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                    ┌──────────────────────────┐                       │
│                    │    OpenSIPs SIP Proxy    │                       │
│                    │   (Signaling Server)     │                       │
│                    ├──────────────────────────┤                       │
│                    │ Module Stack:            │                       │
│                    │ ┌────────────────────┐   │                       │
│                    │ │ proto_wss.so       │─────── WSS Listener      │
│                    │ │ proto_udp.so       │─────── UDP Listener      │
│                    │ │ proto_tls.so       │─────── TLS Listener      │
│                    │ │ tls_mgm.so         │─── Certificate Mgmt      │
│                    │ │ dialog.so          │─── Call Tracking        │
│                    │ │ registrar.so       │─── User Location         │
│                    │ │ tm.so              │─── Transactions         │
│                    │ │ sdpops.so          │─── SDP Modification     │
│                    │ │ rtpengine.so       │─── Media Control        │
│                    │ └────────────────────┘   │                       │
│                    │                          │                       │
│                    │ Processing:              │                       │
│                    │ - Request routing       │                       │
│                    │ - User lookup           │                       │
│                    │ - SDP inspection        │                       │
│                    │ - RTPEngine commands    │                       │
│                    │ - Dialog management     │                       │
│                    └──────────┬───────────────┘                       │
│                               │                                       │
│                Media Control: UDP:22222 (Management)                 │
│                               │                                       │
└───────────────────────────────┼───────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────┐
│                         MEDIA RELAY LAYER                              │
├───────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                   ┌──────────────────────────┐                        │
│                   │    RTPEngine Daemon      │                        │
│                   │   (Media Proxy)          │                        │
│                   ├──────────────────────────┤                        │
│                   │ Functions:               │                        │
│                   │ - DTLS-SRTP encryption   │                        │
│                   │ - ICE candidate relay    │                        │
│                   │ - Codec transcoding      │                        │
│                   │ - RTCP multiplexing      │                        │
│                   │ - Media statistics       │                        │
│                   │ - NAT detection          │                        │
│                   │ - Port allocation        │                        │
│                   │                          │                        │
│                   │ Ports:                   │                        │
│                   │ - UDP:22222 (control)    │                        │
│                   │ - UDP:10000-20000 (RTP)  │                        │
│                   └──────────┬───────────────┘                        │
│                              │                                        │
│                    Bidirectional Media Streams                        │
│                              │                                        │
└──────────────────────────────┼────────────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           │                   │                   │
           ▼                   ▼                   ▼
        Browser A           Browser B            SIP Phone
      (DTLS-SRTP)         (DTLS-SRTP)         (RTP/SDES)
     [Audio/Video]       [Audio/Video]       [Audio/Video]
```

### 1.3 OpenSIPs Internal Module Chain

```
                    ┌─────────────────────────┐
                    │  Incoming SIP Request   │
                    │   (Any transport)       │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Parse Request          │
                    │  (tm.so)                │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Max-Forwards Check     │
                    │  (maxfwd.so)            │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Dialog Identification  │
                    │  (dialog.so)            │
                    │  Determine if:          │
                    │  - New dialog (INVITE)  │
                    │  - Within dialog (rest) │
                    └────────────┬────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                                  │
         New Dialog (INVITE)            Within Dialog (others)
                │                                  │
    ┌───────────▼──────────────┐      ┌───────────▼──────────┐
    │  User Location Lookup    │      │  Loose Route Check   │
    │  (usrloc.so)             │      │  (rr.so)             │
    │  - Find registered user  │      │  - Verify route      │
    │  - Get contact addresses │      │  - Extract target    │
    └───────────┬──────────────┘      └───────────┬──────────┘
                │                                  │
    ┌───────────▼──────────────┐      ┌───────────▼──────────┐
    │  SDP Inspection          │      │  Call RELAY          │
    │  (sdpops.so)             │      │  (tm.so)             │
    │  - Check profiles        │      │  - Send via TM       │
    │  - RTCP-mux detection    │      │  - Handle responses  │
    │  - Codec analysis        │      └────────┬─────────────┘
    └───────────┬──────────────┘                 │
                │                                │
    ┌───────────▼──────────────┐                │
    │  Record Route            │                │
    │  (rr.so)                 │                │
    │  - Mark path to us       │                │
    │  - Enable loose_route    │                │
    └───────────┬──────────────┘                │
                │                                │
    ┌───────────▼──────────────┐                │
    │  RTPEngine Media Control │                │
    │  (rtpengine.so)          │                │
    │  - rtpengine_manage()    │                │
    │  - Determine flags       │                │
    │  - Modify SDP for media  │                │
    │  - Prepare port relay    │                │
    └───────────┬──────────────┘                │
                │                                │
                └────────────┬─────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Transaction RELAY  │
                  │  (tm.so)            │
                  │  - Forward request  │
                  │  - Handle responses │
                  │  - Manage timeouts  │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Response Handling  │
                  │  - Route responses  │
                  │  - SDP reply modify │
                  │  - Cleanup on BYE   │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Send to Destination│
                  │  (via transport)    │
                  │  - UDP, TLS, WSS    │
                  └────────────────────┘
```

---

## 2. Call Flow Scenarios

### 2.1 WebRTC Browser to WebRTC Browser

```
Browser A              OpenSIPs              Browser B
(Chrome)               Proxy                 (Firefox)
│                      │                     │
├─ REGISTER (WSS) ────▶│                     │
│                      ├─ Store location     │
│                      │ browser-a:443       │
│◀─ 200 OK ────────────┤                     │
│                      │                     │
│                      │                     ├─ REGISTER (WSS) ──▶
│                      │◀─ (store location)  │
│                      │    browser-b:443   │
│                      │◀─ 200 OK ───────────┤
│                      │                     │
│ INVITE (SDP offer)   │                     │
├─ (DTLS fingerprint) ─▶│                     │
│    (ICE candidates)  │ rtpengine_offer()   │
│                      │ (detect RTCP-mux)   │
│                      │ flags:              │
│                      │ rtcp-mux-require    │
│                      │ ICE=force           │
│                      │ UDP/TLS/RTP/SAVPF  │
│                      │ SDES-off            │
│                      │                     │
│                      │ lookup(browser-b)   │
│                      ├─ INVITE (SDP) ────▶│
│                      │ (modified SDP)      │
│                      │                     │
│                      │                     ├─ Generate answer
│                      │                     │ (DTLS fingerprint)
│                      │                     │ (ICE candidates)
│                      │◀─ 200 OK (SDP) ─────┤
│                      │ (answer SDP)        │
│                      │                     │
│◀─ 200 OK ────────────│ rtpengine_answer()  │
│  (modified answer)   │ (detect RTCP-mux)   │
│                      │ flags applied       │
│                      │                     │
├─ ACK ───────────────▶│                     │
│                      ├─ ACK ───────────────▶
│                      │                     │
├─ DTLS Handshake ────▶│ RTPEngine detects   │
│ (with RTPEngine)     │ DTLS from both      │
│                      │ sides and handles   │
│ Media (SRTP)         │ crypto negotiation  │
├─────────────────────▶│◀─────────────────────┤
│ [Audio/Video]        │ [Audio/Video]       │
│◀─────────────────────│     (relayed)       │
│ (encrypted)          │ (encrypted)         │
│                      │ (transcoding if     │
│                      │  needed)            │
│                      │                     │
├─ BYE ───────────────▶│                     │
│                      │ rtpengine_delete()  │
│                      ├─ BYE ───────────────▶
│                      │                     │
│                      │◀─ 200 OK ───────────┤
│◀─ 200 OK ────────────┤                     │
│                      │                     │
```

### 2.2 WebRTC Browser to Traditional SIP Phone

```
Browser (Chrome)      OpenSIPs              SIP Phone
(WebRTC)              Proxy                 (Linphone)
│                     │                     │
├─ REGISTER (WSS) ────▶│                     │
│                      ├─ Store location     │
│◀─ 200 OK ────────────┤                     │
│                      │                     │
│                      │                     ├─ REGISTER (UDP) ──▶
│                      │◀─ Store location    │
│                      │    phone:5060       │
│                      │◀─ 200 OK ───────────┤
│                      │                     │
│ INVITE (SDP offer)   │                     │
├─ (DTLS fingerprint) ─▶│                     │
│                      │ rtpengine_offer()   │
│                      │ flags:              │
│                      │ trust-address       │
│                      │ replace-origin      │
│                      │ rtcp-mux-offer      │
│                      │ ICE=force           │
│                      │ transcode-PCMU      │
│                      │ SDES-off            │
│                      │ UDP/TLS/RTP/SAVPF  │
│                      │                     │
│                      │ (converts to:)      │
│                      │ m=audio X RTP/AVP   │
│                      │ (no RTCP-mux)       │
│                      │ (no DTLS)           │
│                      │ (plain RTP)         │
│                      │                     │
│                      │ lookup(phone)       │
│                      ├─ INVITE (SDP) ────▶│
│                      │ (converted SDP)     │
│                      │                     │
│                      │                     ├─ Generate answer
│                      │                     │ (m=audio Y RTP/AVP)
│                      │                     │ (no encryption)
│                      │◀─ 200 OK (SDP) ─────┤
│                      │ rtpengine_answer()  │
│                      │ flags:              │
│                      │ trust-address       │
│                      │ replace-origin      │
│                      │ RTP/AVP             │
│                      │ (back to browser)   │
│◀─ 200 OK ────────────│                     │
│  (modified answer)   │                     │
│  (RTP/AVP profile)   │                     │
│                      │                     │
├─ ACK ───────────────▶│                     │
│                      ├─ ACK ───────────────▶
│                      │                     │
│ Media (DTLS-SRTP)    │ RTPEngine:          │
├────────────────────▶│  - Receive SRTP     │
│ [to RTPEngine]       │    from browser     │
│                      │  - Decrypt to RTP   │
│                      │  - Send RTP to SIP  │
│                      │                     │
│                      │  - Receive RTP      │
│                      │    from SIP phone   │
│◀────────────────────│  - Encrypt to SRTP  │
│ [from RTPEngine]     │  - Send SRTP back   │
│ (relayed & encrypted)│                     │
│                      │                     ├─ RTP Media
│                      │                     │ (plaintext)
│                      │◀────────────────────┤
│                      │                     │
│ (Audio in both       │ (Transcoding:)      │
│  directions,         │ PCMU → Opus         │
│  but different       │ Opus → PCMU         │
│  codecs)             │                     │
│                      │                     │
├─ BYE ───────────────▶│                     │
│                      │ rtpengine_delete()  │
│                      ├─ BYE ───────────────▶
│                      │                     │
│                      │◀─ 200 OK ───────────┤
│◀─ 200 OK ────────────┤                     │
│                      │                     │
```

### 2.3 Traditional SIP to WebRTC Browser

```
SIP Phone             OpenSIPs              Browser (Firefox)
(Linphone)            Proxy                 (WebRTC)
│                     │                     │
│ REGISTER (UDP) ─────▶│                     │
│                      ├─ Store location     │
│◀─ 200 OK ────────────┤                     │
│                      │                     │
│                      │                     ├─ REGISTER (WSS) ──▶
│                      │◀─ Store location    │
│                      │                     │
│                      │◀─ 200 OK ───────────┤
│                      │                     │
│ INVITE (SDP offer)   │                     │
├─ (m=audio X RTP/AVP) ▶│                    │
│  (no encryption)     │ rtpengine_offer()   │
│  (no ICE)            │ flags:              │
│                      │ trust-address       │
│                      │ replace-origin      │
│                      │ (converts to:)      │
│                      │ rtcp-mux-require    │
│                      │ generate-mid        │
│                      │ ICE=force           │
│                      │ SDES-off            │
│                      │ UDP/TLS/RTP/SAVPF  │
│                      │                     │
│                      │ lookup(browser)     │
│                      ├─ INVITE (SDP) ────▶│
│                      │ (WebRTC compatible) │
│                      │                     │
│                      │                     ├─ JavaScript processes
│                      │                     │ ├─ Creates answer
│                      │                     │ ├─ DTLS handshake
│                      │                     │ └─ ICE gathering
│                      │◀─ 200 OK (SDP) ─────┤
│                      │ (DTLS fingerprint)  │
│                      │ (ICE candidates)    │
│                      │                     │
│                      │ rtpengine_answer()  │
│                      │ flags:              │
│                      │ trust-address       │
│                      │ replace-origin      │
│                      │ rtcp-mux-demux      │
│                      │ ICE=remove          │
│                      │ RTP/AVP             │
│◀─ 200 OK ────────────│                     │
│ (plain RTP format)   │                     │
│ (no DTLS/ICE)        │                     │
│                      │                     │
├─ ACK ───────────────▶│                     │
│                      ├─ ACK ───────────────▶
│                      │                     │
│                      │◀─ DTLS Handshake ──┤
│                      │   (RTPEngine ↔ Browser)
│                      │                     │
│ RTP Media (plain)    │ RTPEngine handles:  │
├────────────────────▶│  - Plain RTP in     │
│ [to RTPEngine]       │  - DTLS-SRTP out   │
│                      │  - Codec conversion │
│                      │  - Port forwarding  │
│                      │                     │
│◀────────────────────│  - DTLS-SRTP in    │
│ [from RTPEngine]     │  - Plain RTP out   │
│ (relayed)            │                     ├─ DTLS-SRTP Media
│                      │                     │ (encrypted)
│                      │                     │
│ (Audio in both       │                     │ (Codec conversion:)
│  directions,         │                     │ PCMU → Opus
│  different modes)    │                     │ Opus → PCMU
│                      │                     │
├─ BYE ───────────────▶│                     │
│                      │ rtpengine_delete()  │
│                      ├─ BYE ───────────────▶
│                      │                     │
│                      │◀─ 200 OK ───────────┤
│◀─ 200 OK ────────────┤                     │
│                      │                     │
```

---

## 3. Practical Configuration Examples

### 3.1 Complete Production opensips.cfg

```opensips.cfg
############################################################
###          OPENSIPS WEBRTC PRODUCTION CONFIG            ###
###                  Version: 3.2.x LTS                    ###
###          Use this as foundation for IF.bus             ###
############################################################

####### Global Parameters #######

# Log level: 3=notice, 4=info, 5=debug
log_level=3
log_stderror=yes
log_facility=LOG_LOCAL0

# Process concurrency
children=8
socket="/var/run/opensips/opensips.sock"

# Memory sizing
pkg_mem_size=12
shm_mem_size=256

# TCP tuning
tcp_max_connections=2048
tcp_connect_timeout=10
tcp_send_timeout=60
tcp_keepalive=1

####### Protocol Modules #######

loadmodule "proto_udp.so"
loadmodule "proto_tls.so"
loadmodule "proto_ws.so"
loadmodule "proto_wss.so"

####### Core Functionality #######

loadmodule "tm.so"           # Transaction Module
loadmodule "sl.so"           # Stateless module
loadmodule "rr.so"           # Record-Route
loadmodule "maxfwd.so"       # Max-Forwards check
loadmodule "usrloc.so"       # User location database
loadmodule "registrar.so"    # User registration
loadmodule "dialog.so"       # Dialog/call tracking

####### Media & Security #######

loadmodule "tls_mgm.so"      # TLS certificate management
loadmodule "nathelper.so"    # NAT handling
loadmodule "sdpops.so"       # SDP operations
loadmodule "rtpengine.so"    # RTPEngine media proxy
loadmodule "rtp_relay.so"    # Unified RTP relay (3.2+)

####### Database #######

loadmodule "db_mysql.so"     # MySQL driver
loadmodule "db_virtual.so"   # Virtual DB (optional)

####### Optional Features #######

loadmodule "auth.so"         # Authentication
loadmodule "auth_db.so"      # DB-based auth
loadmodule "dispatcher.so"   # Load balancing
loadmodule "dialog.so"       # For dialog replication
loadmodule "clusterer.so"    # Clustering (HA)
loadmodule "mi_rest.so"      # REST API management

####### Module Parameters #######

# ========== TLS Management ==========
modparam("tls_mgm", "certificate", "/etc/opensips/certs/opensips.crt")
modparam("tls_mgm", "private_key", "/etc/opensips/certs/opensips.key")
modparam("tls_mgm", "ca_list", "/etc/opensips/certs/ca.pem")

modparam("tls_mgm", "tls_method", "tlsv1_2+")
modparam("tls_mgm", "tls_max_allowed_version", "tlsv1_3")
modparam("tls_mgm", "tls_min_allowed_version", "tlsv1_2")

modparam("tls_mgm", "tls_ciphers",
    "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA")

modparam("tls_mgm", "verify_cert", "1")
modparam("tls_mgm", "require_cert", "1")

# Virtual domain for multi-tenant
modparam("tls_mgm", "tls_domain", "example.com")
modparam("tls_mgm:tls_domain:example.com", "certificate", "/etc/opensips/certs/example.com.crt")
modparam("tls_mgm:tls_domain:example.com", "private_key", "/etc/opensips/certs/example.com.key")

# ========== WebSocket (proto_wss) ==========
modparam("proto_wss", "wss_port", 443)
modparam("proto_wss", "wss_keepalive", 180)  # seconds

# ========== User Location ==========
modparam("usrloc", "db_url", "mysql://opensips:opensips_pass@localhost/opensips")
modparam("usrloc", "db_mode", 3)  # DB write-back mode
modparam("usrloc", "nat_bflag", 3)  # Branch flag for NAT

# ========== Registrar ==========
modparam("registrar", "accept_j_header", 1)
modparam("registrar", "default_expires", 3600)
modparam("registrar", "min_expires", 60)
modparam("registrar", "max_expires", 86400)

# ========== Dialog ==========
modparam("dialog", "db_url", "mysql://opensips:opensips_pass@localhost/opensips")
modparam("dialog", "db_mode", 3)  # DB write-back
modparam("dialog", "dlg_timeout", 43200)  # 12 hours max
modparam("dialog", "default_timeout", 28800)  # 8 hours default
modparam("dialog", "enable_stats", 1)

# Clustering (optional)
modparam("dialog", "cluster_replicate_dialogs", 1)

# ========== NAT Helper ==========
modparam("nathelper", "natping_interval", 30)
modparam("nathelper", "ping_nated_only", 1)
modparam("nathelper", "sipping_bflag", 7)
modparam("nathelper", "sipping_from", "sip:ping@example.com")

# ========== RTPEngine ==========
modparam("rtpengine", "rtpengine_sock", "udp:127.0.0.1:22222")

# Multiple RTPEngine nodes for HA
# modparam("rtpengine", "rtpengine_sock", "udp:10.0.0.2:22222")
# modparam("rtpengine", "rtpengine_sock", "udp:10.0.0.3:22222")

modparam("rtpengine", "rtpengine_tout", 500)    # timeout (ms)
modparam("rtpengine", "rtpengine_retr", 2)     # retries
modparam("rtpengine", "notification_sock", "udp:127.0.0.1:22223")
modparam("rtpengine", "queued_requests_limit", 1000)

# ========== RTP Relay (3.2+) ==========
modparam("rtp_relay", "engines", "rtpengine=udp:127.0.0.1:22222")

# ========== Dispatcher (Load Balancing) ==========
# modparam("dispatcher", "db_url", "mysql://opensips:opensips_pass@localhost/opensips")
# modparam("dispatcher", "ds_ping_method", "OPTIONS")
# modparam("dispatcher", "ds_ping_interval", 30)

# ========== Clustering ==========
modparam("clusterer", "db_url", "mysql://opensips:opensips_pass@localhost/opensips")
modparam("clusterer", "my_node_id", 1)  # Unique per node
modparam("clusterer", "my_seed_node_id", 1)

# ========== REST API (Management) ==========
modparam("mi_rest", "mi_socket", "0.0.0.0:8888")

####### Network Listeners #######

listen=udp:0.0.0.0:5060 advertise 203.0.113.1:5060
listen=tls:0.0.0.0:5061 advertise 203.0.113.1:5061
listen=ws:0.0.0.0:8080 advertise 203.0.113.1:8080
listen=wss:0.0.0.0:443 advertise 203.0.113.1:443

####### Routing Logic #######

request_route {
    # Logging
    xlog("L_INFO", "[REQ] $rm from $fu to $tu via $proto port $Rp\n");

    # Sanity checks
    if (!mf_process_maxfwd_header("10")) {
        send_reply("483", "Too Many Hops");
        exit;
    }

    if ($msg:len > 4096) {
        send_reply("413", "Request Entity Too Large");
        exit;
    }

    # Identify WebRTC clients
    if ($proto == "wss" || $proto == "ws") {
        $var(is_websocket) = 1;
        xlog("L_INFO", "[WS] WebRTC client detected\n");
        # For WebSocket, assume behind NAT
        setflag(3);  # NAT flag
    }

    # Loose route (in-dialog)
    if (has_totag()) {
        if (!loose_route()) {
            xlog("L_WARN", "[ROUTE] Loose route failed for $ru\n");
            send_reply("404", "Not Found");
            exit;
        }

        t_relay();
        exit;
    }

    # CANCEL handling
    if ($rm == "CANCEL") {
        if (tm_check_trans()) {
            t_relay();
        }
        exit;
    }

    # ACK handling
    if ($rm == "ACK") {
        if (tm_check_trans()) {
            t_relay();
        }
        exit;
    }

    # OPTIONS (ping/keepalive)
    if ($rm == "OPTIONS") {
        send_reply("200", "OK");
        exit;
    }

    # REGISTER
    if ($rm == "REGISTER") {
        route(REGISTER);
        exit;
    }

    # INVITE (session initiation)
    if ($rm == "INVITE") {
        route(INVITE);
        exit;
    }

    # Other requests
    route(RELAY);
}

route[REGISTER] {
    xlog("L_INFO", "[REG] User registration: $fu from $si\n");

    # Authentication (optional)
    # if (!www_authenticate("example.com", "subscriber")) {
    #     www_challenge("example.com", "0");
    #     exit;
    # }

    # NAT detection for WebSocket clients
    if ($var(is_websocket)) {
        handle_ruri_alias();
    }

    # Save registration
    if (!save("location")) {
        xlog("L_ERR", "[REG] Save failed for $fu\n");
        send_reply("500", "Server Internal Error");
        exit;
    }

    xlog("L_INFO", "[REG] Registered: $fu via $proto\n");
}

route[INVITE] {
    xlog("L_INFO", "[INVITE] Call initiated: $fu → $tu\n");

    # Create dialog to track this call
    if (!create_dialog()) {
        xlog("L_ERR", "[INVITE] Dialog creation failed\n");
        send_reply("500", "Server Internal Error");
        exit;
    }

    # Enable record-routing for in-dialog requests
    record_route();

    # Lookup target user
    if (!lookup("location")) {
        xlog("L_WARN", "[INVITE] User not found: $tu\n");
        send_reply("404", "User Not Found");
        exit;
    }

    # Route the INVITE with media handling
    t_on_branch("MANAGE_BRANCH");
    t_on_failure("MANAGE_FAILURE");

    if (!t_relay()) {
        xlog("L_ERR", "[INVITE] Relay failed\n");
        send_reply("500", "Server Internal Error");
    }
}

route[RELAY] {
    if (!t_relay()) {
        xlog("L_ERR", "[RELAY] Relay failed\n");
        send_reply("500", "Server Internal Error");
    }
}

branch_route[MANAGE_BRANCH] {
    xlog("L_INFO", "[BRANCH] Processing branch to $ru\n");

    # Determine if destination is WebRTC or traditional SIP
    if (sdp_has_rtcp_mux()) {
        # Destination is WebRTC
        xlog("L_INFO", "[MEDIA] WebRTC endpoint detected (has rtcp-mux)\n");

        if ($var(is_websocket)) {
            # Web → Web (both SRTP)
            rtpengine_manage("trust-address replace-origin replace-session-connection " .
                            "rtcp-mux-require no-rtcp-attribute generate-mid " .
                            "ICE=force SDES-off UDP/TLS/RTP/SAVPF");
        } else {
            # SIP → Web (needs transcoding)
            rtpengine_manage("trust-address replace-origin replace-session-connection " .
                            "rtcp-mux-require no-rtcp-attribute generate-mid " .
                            "ICE=force transcode-PCMU transcode-G722 " .
                            "SDES-off UDP/TLS/RTP/SAVPF");
        }
    } else {
        # Destination is traditional SIP
        xlog("L_INFO", "[MEDIA] Traditional SIP endpoint\n");

        if ($var(is_websocket)) {
            # Web → SIP (strip WebRTC features)
            rtpengine_manage("trust-address replace-origin replace-session-connection " .
                            "rtcp-mux-demux ICE=remove RTP/AVP");
        } else {
            # SIP → SIP (passthrough)
            rtpengine_manage("trust-address replace-origin replace-session-connection RTP/AVP");
        }
    }
}

failure_route[MANAGE_FAILURE] {
    xlog("L_WARN", "[FAILURE] Route failed, cleaning up\n");

    if (t_is_canceled()) {
        exit;
    }

    # Cleanup media session
    rtpengine_delete();

    if ($rm == "INVITE") {
        # Try alternative routes if available
        if (use_next_gw()) {
            t_relay();
        } else {
            send_reply("500", "No More Routes");
        }
    }
}

####### Helper Functions #######

# Check if SDP has RTCP-mux (WebRTC indicator)
function sdp_has_rtcp_mux() {
    if (sdp_get_line_startswith("a=rtcp-mux")) {
        return 1;
    }
    return 0;
}
```

### 3.2 Complete RTPEngine Configuration

```ini
# /etc/ngcp-rtpengine/rtpengine.conf

# Interface configuration
[general]

# Listen address and port for control protocol (UDP)
listen=22222

# Network interfaces for RTP media relay
# Format: IP/netmask or IP:port/netmask
interface=10.0.0.5/255.255.255.0
interface=10.0.0.5:10000-20000/255.255.255.0

# For NAT deployments (private→public IP mapping)
# interface=10.0.0.0/255.255.255.0!203.0.113.0/255.255.255.0

# Logging
log_level=4  # 1=critical, 2=error, 3=warning, 4=notice, 5=info, 6=debug
log_facility=LOG_LOCAL0
log_stderr=no
syslog=yes

# Daemon settings
fork=yes
pidfile=/var/run/rtpengine.pid

# Timeout for inactive sessions (seconds)
timeout=60
silent_timeout=3600  # timeout with no RTP packets

# Final timeout (absolute limit)
final-timeout=604800  # 7 days

# Cleanup interval (how often to check for timeouts)
cleanup-interval=30

# Maximum concurrent sessions
# max-sessions=100000

# File descriptor limits
# ulimit -n 1000000

# CPU affinity (if available)
# cpu-affinity=0,1,2,3

# DTMF handling
dtmf-detection=yes
dtmf-logging=yes

# IPv6 support (if applicable)
# ipv6=yes

# Statistics
statistics-interval=60

# Common codecs to handle
# codecs=opus,pcmu,g722

# TLS for media (less common, for legacy)
# tls-certificate=/etc/opensips/certs/opensips.crt
# tls-private-key=/etc/opensips/certs/opensips.key
```

---

## 4. Monitoring & Debugging

### 4.1 Real-Time Call Monitoring Script

```bash
#!/bin/bash
# File: /usr/local/bin/opensips-webrtc-monitor.sh
# Purpose: Real-time WebRTC call monitoring

set -e

OPENSIPS_SOCKET="/var/run/opensips/opensips.sock"
RTPENGINE_HOST="127.0.0.1"
RTPENGINE_PORT="22222"

clear_screen() {
    clear
}

get_opensips_status() {
    if ! command -v opensipsctl &> /dev/null; then
        echo "OpenSIPs Control Tool: Not Available"
        return
    fi

    echo "=== OpenSIPs Status ==="
    opensipsctl fifo get_statistics 2>/dev/null | grep -E "^(core|dialog|tm|rtpengine):" || echo "No stats"
}

get_rtpengine_status() {
    echo ""
    echo "=== RTPEngine Status ==="

    if echo "ping" | nc -u -w 1 "$RTPENGINE_HOST" "$RTPENGINE_PORT" &>/dev/null; then
        echo "✓ RTPEngine Online (UDP:$RTPENGINE_PORT)"

        # Get active sessions count (ng format)
        local sessions=$(echo "statistics" | nc -u -w 1 "$RTPENGINE_HOST" "$RTPENGINE_PORT" 2>/dev/null | grep -o "\"active sessions\":[0-9]*" | cut -d: -f2)
        echo "  Active Sessions: ${sessions:-N/A}"
    else
        echo "✗ RTPEngine Offline"
    fi
}

get_active_calls() {
    echo ""
    echo "=== Active Calls ==="

    if ! command -v opensipsctl &> /dev/null; then
        return
    fi

    local call_count=$(opensipsctl fifo dlg_list 2>/dev/null | grep -c "^Dialog::" || echo 0)
    echo "Total Active Dialogs: $call_count"

    # Show first 5 active calls
    opensipsctl fifo dlg_list 2>/dev/null | head -20 | grep -E "Dialog|from_uri|to_uri" || echo "None"
}

get_network_status() {
    echo ""
    echo "=== Network Status ==="

    # WebSocket connections
    local ws_conns=$(netstat -an 2>/dev/null | grep -c ":443\|:8080.*ESTABLISHED" || echo 0)
    echo "WebSocket Connections: $ws_conns"

    # TLS connections
    local tls_conns=$(netstat -an 2>/dev/null | grep -c ":5061.*ESTABLISHED" || echo 0)
    echo "TLS Connections: $tls_conns"

    # Media flow
    local media_conns=$(netstat -an 2>/dev/null | grep -c "10000:20000" || echo 0)
    echo "Media Ports Active: $media_conns"
}

get_error_log() {
    echo ""
    echo "=== Recent Errors (Last 5) ==="

    if [ -f /var/log/opensips/opensips.log ]; then
        grep -i "error\|err" /var/log/opensips/opensips.log 2>/dev/null | tail -5 || echo "No errors"
    else
        echo "Log file not found"
    fi
}

main() {
    while true; do
        clear_screen
        echo "OpenSIPs WebRTC Monitoring Dashboard"
        echo "======================================"
        echo "Updated: $(date)"
        echo ""

        get_opensips_status
        get_rtpengine_status
        get_active_calls
        get_network_status
        get_error_log

        echo ""
        echo "Press Ctrl+C to exit, updating every 5 seconds..."
        sleep 5
    done
}

main "$@"
```

### 4.2 Call Quality Testing Script

```bash
#!/bin/bash
# File: /usr/local/bin/test-webrtc-quality.sh
# Purpose: Test WebRTC call quality metrics

set -e

RTPENGINE_HOST="127.0.0.1"
RTPENGINE_PORT="22222"

test_rtpengine_latency() {
    echo "=== RTPEngine Latency Test ==="

    local start=$(date +%s%N)
    echo "ping" | nc -u -w 1 "$RTPENGINE_HOST" "$RTPENGINE_PORT" > /dev/null
    local end=$(date +%s%N)

    local latency_ns=$((end - start))
    local latency_ms=$((latency_ns / 1000000))

    echo "Round-trip time: ${latency_ms}ms"

    if [ $latency_ms -lt 10 ]; then
        echo "✓ Latency EXCELLENT"
    elif [ $latency_ms -lt 50 ]; then
        echo "✓ Latency GOOD"
    elif [ $latency_ms -lt 100 ]; then
        echo "⚠ Latency ACCEPTABLE"
    else
        echo "✗ Latency HIGH (investigate RTPEngine performance)"
    fi
}

test_tcp_connections() {
    echo ""
    echo "=== TCP/WebSocket Connection Test ==="

    local port=$1
    local proto=$2

    if nc -zv 127.0.0.1 $port &>/dev/null 2>&1; then
        echo "✓ Port $port ($proto) is accepting connections"
    else
        echo "✗ Port $port ($proto) BLOCKED or NOT LISTENING"
    fi
}

test_ssl_certificate() {
    echo ""
    echo "=== SSL/TLS Certificate Test ==="

    local cert_file="/etc/opensips/certs/opensips.crt"

    if [ ! -f "$cert_file" ]; then
        echo "✗ Certificate file not found: $cert_file"
        return
    fi

    # Check expiry
    local expiry=$(openssl x509 -in "$cert_file" -noout -enddate 2>/dev/null | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry" +%s)
    local now_epoch=$(date +%s)
    local days_left=$(((expiry_epoch - now_epoch) / 86400))

    echo "Certificate expires: $expiry"
    echo "Days remaining: $days_left"

    if [ $days_left -lt 7 ]; then
        echo "✗ Certificate EXPIRING SOON"
    elif [ $days_left -lt 30 ]; then
        echo "⚠ Certificate renewal recommended"
    else
        echo "✓ Certificate is valid"
    fi
}

test_udp_media_ports() {
    echo ""
    echo "=== UDP Media Port Test ==="

    # Check if ports are listening
    if netstat -an 2>/dev/null | grep -q ":10000.*LISTEN"; then
        echo "✓ Media ports are listening"
    else
        echo "✗ Media ports NOT listening"
    fi
}

main() {
    echo "WebRTC Quality Assessment"
    echo "=========================="
    echo ""

    test_rtpengine_latency
    test_tcp_connections 443 "WSS"
    test_tcp_connections 5060 "UDP SIP"
    test_tcp_connections 5061 "TLS SIP"
    test_ssl_certificate
    test_udp_media_ports

    echo ""
    echo "Assessment complete."
}

main "$@"
```

---

## 5. Common Gotchas & Solutions

### Gotcha 1: Forgetting to Start RTPEngine First

```
Symptom: All calls fail with "rtpengine not available"
Cause: RTPEngine daemon not running before OpenSIPs starts
Solution:
  1. systemctl start ngcp-rtpengine-daemon
  2. Verify: echo "ping" | nc -u 127.0.0.1 22222
  3. Then start OpenSIPs
  4. Always: systemctl enable ngcp-rtpengine-daemon
```

### Gotcha 2: WebSocket Works, But Media Dies After Few Seconds

```
Symptom: Call starts fine, audio drops after 10-20 seconds
Cause: RTPEngine timeout too short
Solution:
  Increase modparam("rtpengine", "rtpengine_tout", 1000)  # 1 second
  Also increase RTPEngine timeout: timeout=120 in rtpengine.conf
```

### Gotcha 3: Certificate Mismatch on WSS

```
Symptom: Browser console shows TLS handshake failure
Cause: Certificate domain doesn't match connection domain
Solution:
  1. Check certificate: openssl x509 -in cert.crt -text -noout
  2. Verify CN (Common Name) matches your domain
  3. Or use wildcard certificate (*.example.com)
  4. Test: openssl s_client -connect opensips.example.com:443
```

### Gotcha 4: SDP Fingerprint Mismatch

```
Symptom: DTLS-SRTP handshake fails, one-way media
Cause: SDP fingerprint not matching actual DTLS key
Solution:
  1. Enable debugging: modparam("core", "log_level", 5)
  2. Check SDP for "a=fingerprint:" lines
  3. Verify rtpengine_manage() flags don't corrupt fingerprint
  4. Check RTPEngine logs: /var/log/syslog
```

---

## 6. Capacity Planning

### Call Capacity Estimates (Single Node)

```
Based on: 2vCPU, 4GB RAM, 1Gbps network

WebRTC Client Count: 50-100
Concurrent Calls: 25-50
Approximate SIP Call Rate: 10-20 calls/sec

Memory Usage:
- Base OpenSIPs: ~100MB
- Per call overhead: ~5-10KB
- At 50 concurrent calls: ~150-200MB

CPU Usage:
- Idle: 1-2%
- Per call: ~1-2% CPU per concurrent call
- At 50 concurrent calls: 50-100% (scaling)

Network:
- Signaling: ~1-5 Mbps
- Media (50 calls): ~50-100 Mbps (depends on codec)
  - Opus at 32kbps: ~1.6Mbps per call
  - G.711 (PCMU) at 64kbps: ~3.2Mbps per call
```

### Scaling Recommendations

```
For 100-500 concurrent calls:
- Use load balancer (HAProxy/F5)
- 3-5 OpenSIPs nodes
- 3-5 RTPEngine nodes (separate hardware)
- Shared MariaDB Galera cluster

For 500+ concurrent calls:
- Consider dedicated SBC (Session Border Controller)
- Network-level load balancing (anycast)
- Geographic distribution
- Dedicated monitoring/analytics platform
```

---

**Document Version**: 1.0
**Last Updated**: 2025-11-11
**For**: IF.bus SIP Adapter Project
