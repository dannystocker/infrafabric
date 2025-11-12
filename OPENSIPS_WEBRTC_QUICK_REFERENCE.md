# OpenSIPs WebRTC Quick Reference Guide

**Purpose**: Fast lookup during implementation and troubleshooting

---

## 1. Module Loading Checklist

```opensips.cfg
# Copy-paste ready for basic WebRTC setup

# Protocol layers
loadmodule "proto_udp.so"
loadmodule "proto_tls.so"
loadmodule "proto_ws.so"
loadmodule "proto_wss.so"

# Core transaction handling
loadmodule "tm.so"
loadmodule "sl.so"
loadmodule "rr.so"

# User management
loadmodule "usrloc.so"
loadmodule "registrar.so"
loadmodule "dialog.so"

# Media & WebRTC
loadmodule "tls_mgm.so"
loadmodule "sdpops.so"
loadmodule "rtpengine.so"
loadmodule "nathelper.so"
loadmodule "rtp_relay.so"

# Optional but recommended
loadmodule "auth.so"
loadmodule "auth_db.so"
loadmodule "db_mysql.so"
loadmodule "dispatcher.so"
```

---

## 2. Critical Parameters Quick View

### TLS & WebSocket Listeners
```opensips.cfg
# TLS Certificate Configuration
modparam("tls_mgm", "certificate", "/etc/opensips/certs/opensips.crt")
modparam("tls_mgm", "private_key", "/etc/opensips/certs/opensips.key")
modparam("tls_mgm", "verify_cert", "1")

# Listener Endpoints
listen=udp:0.0.0.0:5060          # Traditional SIP
listen=tls:0.0.0.0:5061          # Encrypted SIP
listen=ws:0.0.0.0:8080           # WebSocket (dev)
listen=wss:0.0.0.0:443           # WebSocket Secure (prod)
```

### RTPEngine Configuration
```opensips.cfg
modparam("rtpengine", "rtpengine_sock", "udp:127.0.0.1:22222")
modparam("rtpengine", "rtpengine_tout", 500)    # ms
modparam("rtpengine", "rtpengine_retr", 2)     # retries
```

---

## 3. RTPEngine Management Flags

### Quick Reference Table

| Scenario | Flags | Explanation |
|----------|-------|-------------|
| **Web→Web** | `trust-address replace-origin rtcp-mux-require ICE=force SDES-off UDP/TLS/RTP/SAVPF` | Both WebRTC, need full encryption |
| **Web→SIP** | `trust-address replace-origin rtcp-mux-demux ICE=remove RTP/AVP` | Traditional SIP, remove WebRTC features |
| **SIP→Web** | `trust-address replace-origin rtcp-mux-offer ICE=force transcode-PCMU SDES-off UDP/TLS/RTP/SAVPF` | Convert to WebRTC format |
| **SIP→SIP** | `trust-address replace-origin RTP/AVP` | Traditional passthrough |

### Flag Meanings
```
trust-address          Use source IP from packet
replace-origin         Rewrite SDP origin IP
replace-session-connection  Update SDP connection line
rtcp-mux-require       Force RTCP multiplexing (WebRTC)
rtcp-mux-demux         Separate RTCP from RTP (legacy)
ICE=force              Add ICE candidates (needed for WebRTC)
ICE=remove             Strip ICE (legacy mode)
SDES-off               Disable SDES encryption
UDP/TLS/RTP/SAVPF     WebRTC profile (RTP secure, AVPF)
RTP/AVP                Legacy SIP profile
transcode-PCMU         Convert Opus → PCMU
no-rtcp-attribute      Don't advertise separate RTCP port
generate-mid           Create MID line (media identification)
```

---

## 4. Minimal Working Configuration

```opensips.cfg
########## MINIMAL WEBRTC GATEWAY ##########

# ========== MODULES ==========
loadmodule "proto_udp.so"
loadmodule "proto_wss.so"
loadmodule "tm.so"
loadmodule "sl.so"
loadmodule "rr.so"
loadmodule "maxfwd.so"
loadmodule "usrloc.so"
loadmodule "registrar.so"
loadmodule "dialog.so"
loadmodule "tls_mgm.so"
loadmodule "sdpops.so"
loadmodule "rtpengine.so"
loadmodule "nathelper.so"

# ========== PARAMETERS ==========
modparam("tls_mgm", "certificate", "/etc/opensips/certs/opensips.crt")
modparam("tls_mgm", "private_key", "/etc/opensips/certs/opensips.key")
modparam("rtpengine", "rtpengine_sock", "udp:127.0.0.1:22222")
modparam("usrloc", "db_url", "mysql://opensips:password@localhost/opensips")

# ========== LISTENERS ==========
listen=udp:0.0.0.0:5060
listen=wss:0.0.0.0:443

# ========== ROUTING ==========
request_route {
    # Log
    xlog("L_INFO", "$rm from $fu to $tu via $proto\n");

    # Stateless processing
    if (!mf_process_maxfwd_header("10")) {
        send_reply("483", "Max Forwards exceeded");
        exit;
    }

    # Dialog identification
    if (has_totag()) {
        if (loose_route()) {
            route(RELAY);
        } else {
            send_reply("404", "Not Found");
        }
        exit;
    }

    # Request type handling
    if ($rm == "CANCEL" || $rm == "ACK") {
        route(RELAY);
        exit;
    }

    if ($rm == "REGISTER") {
        if (save("location")) {
            send_reply("200", "OK");
        }
        exit;
    }

    if ($rm == "INVITE") {
        create_dialog();
        record_route();

        if (!lookup("location")) {
            send_reply("404", "User Not Found");
            exit;
        }

        route(RELAY);
        exit;
    }

    route(RELAY);
}

route[RELAY] {
    if (!tm_relay()) {
        send_reply("500", "Relay Failed");
    }
}

# ========== BRANCH ROUTE (Media Handling) ==========
branch_route[1] {
    # Detect endpoint types and apply appropriate rtpengine flags
    if (sdp_has_line_startswith("a=rtcp-mux")) {
        # Destination is WebRTC
        rtpengine_manage("trust-address replace-origin replace-session-connection " .
                         "rtcp-mux-require no-rtcp-attribute ICE=force " .
                         "SDES-off UDP/TLS/RTP/SAVPF");
    } else {
        # Destination is traditional SIP
        rtpengine_manage("trust-address replace-origin replace-session-connection RTP/AVP");
    }
}

# ========== FAILURE ROUTE ==========
failure_route[1] {
    if (t_is_canceled()) {
        exit;
    }
    rtpengine_delete();
}
```

---

## 5. Diagnostic Commands

### OpenSIPs Management

```bash
# Check if OpenSIPs is running
sudo opensipsctl fifo get_statistics | head -20

# List active users
sudo opensipsctl db_query opensips location

# List active dialogs
sudo opensipsctl fifo dlg_list

# View current statistics
sudo opensipsctl fifo get_statistics | grep -i call

# Debug specific user
sudo opensipsctl fifo ul_show <user>

# View module status
ps aux | grep opensips
```

### RTPEngine Testing

```bash
# Test RTPEngine connectivity
echo "ping" | nc -u localhost 22222
# Expected: "pong"

# List active sessions
echo "list" | nc -u localhost 22222

# Detailed session info (requires ng format)
# echo '{"command":"list"}' | nc -u localhost 22222

# Check listening ports
sudo netstat -tulpn | grep rtpengine

# View RTPEngine logs
sudo tail -f /var/log/syslog | grep rtpengine
```

### Network Diagnostics

```bash
# Check WebSocket (WSS) listener
sudo netstat -tulpn | grep 443

# Test TLS connection
openssl s_client -connect opensips.example.com:443 -showcerts

# Capture WebSocket traffic
sudo tcpdump -i eth0 -A 'tcp port 443' | head -100

# Capture media traffic
sudo tcpdump -i eth0 'udp port 10000:20000' -w media.pcap

# View certificate info
openssl x509 -in /etc/opensips/certs/opensips.crt -text -noout
```

### Log Analysis

```bash
# Watch WebRTC activity
sudo tail -f /var/log/opensips/opensips.log | grep -i wss

# Find SDP issues
sudo grep -i "sdp\|savpf\|dtls" /var/log/opensips/opensips.log

# Count errors
sudo grep "ERROR\|ERR" /var/log/opensips/opensips.log | wc -l

# Find rtpengine issues
sudo grep -i "rtpengine" /var/log/opensips/opensips.log | tail -20

# Real-time call flow
sudo tail -f /var/log/opensips/opensips.log | grep "$callid"
```

---

## 6. SDP Inspection Helpers

```bash
# Extract SDP from captured traffic
# (assuming Wireshark/tcpdump capture)

# Display SDP content from pcap
tcpdump -r call.pcap -A | grep -A 30 "^a="

# Validate SDP
# (save to file, then)
cat offer.sdp | grep -E "^(v=|o=|s=|c=|t=|m=|a=)"

# Common SDP lines to check
# v=0                          # SDP version
# m=audio 9 UDP/TLS/RTP/SAVPF  # Media line (profile)
# a=rtcp-mux                   # RTCP multiplexing
# a=fingerprint:sha-256 ...    # DTLS fingerprint
# a=ice-ufrag:                 # ICE username fragment
# a=ice-pwd:                   # ICE password
```

---

## 7. Common Error Messages & Quick Fixes

### Error: "rtpengine not available"
```
Cause: RTPEngine not running or unreachable
Fix:
  1. sudo systemctl status ngcp-rtpengine-daemon
  2. echo "ping" | nc -u 127.0.0.1 22222
  3. Check opensips.cfg: rtpengine_sock parameter
  4. Check firewall: sudo ufw allow 22222/udp
```

### Error: "SDP body corrupted"
```
Cause: rtpengine_manage() flags conflict
Fix:
  1. Verify SDP before rtpengine_manage()
  2. Check rtpengine version compatibility
  3. Review rtpengine_manage() flags
  4. Add xlog() to debug SDP modifications
```

### Error: "One-way audio / No audio"
```
Cause: Media ports blocked or RTPEngine not relaying
Fix:
  1. sudo ufw allow 10000:20000/udp
  2. Verify media port range in RTPEngine config
  3. Check NAT mappings in firewall
  4. tcpdump media ports to confirm traffic
  5. Review RTPEngine flags (rtcp-mux-demux vs require)
```

### Error: "TLS: certificate verify failed"
```
Cause: Invalid/expired TLS certificate
Fix:
  1. openssl x509 -in /etc/opensips/certs/opensips.crt -text -noout
  2. Check expiry date (notAfter)
  3. Verify CA chain: openssl verify -CAfile ca.crt opensips.crt
  4. Update paths in tls_mgm parameters
  5. Restart OpenSIPs after cert update
```

### Error: "WebSocket: 1006 abnormal closure"
```
Cause: WebSocket connection dropped unexpectedly
Possible Causes:
  1. Network timeout (check keepalive settings)
  2. RTPEngine failure mid-call
  3. Dialog timeout triggered
  4. Load balancer session timeout
Fix:
  1. Increase WebSocket timeout: modparam("proto_wss", "wss_keepalive", 180)
  2. Increase rtpengine_tout: modparam("rtpengine", "rtpengine_tout", 1000)
  3. Check load balancer session timeout
  4. Monitor RTPEngine health during calls
```

---

## 8. Performance Tuning

### OpenSIPs Configuration Tuning

```opensips.cfg
# Increase concurrent processing
modparam("core", "min_free_open_fds", 4096)
modparam("core", "max_open_sockets", 16384)

# Worker processes (2-4 per CPU core)
modparam("core", "children", 8)

# TCP timeout (for WebSocket)
modparam("core", "tcp_connect_timeout", 10)
modparam("core", "tcp_max_connections", 2048)

# Dialog timeout (call duration max)
modparam("dialog", "dlg_timeout", 43200)  # 12 hours

# Keepalive for WebSocket
modparam("proto_wss", "wss_keepalive", 180)  # 3 minutes

# Memory optimization
modparam("core", "mem_warming", 1)
modparam("core", "pkg_mem_size", 8)  # MB per process

# Call routing cache (if using dispatcher)
modparam("dispatcher", "use_domain", 1)
modparam("dispatcher", "flags", 2)  # Load-balance mode
```

### RTPEngine Tuning

```bash
# In /etc/ngcp-rtpengine/rtpengine.conf

# Timeout for inactive streams (seconds)
timeout=60

# Cleanup interval
cleanup_interval=30

# File descriptor limit
ulimit -n 65536

# CPU affinity (if available)
# cpu-affinity=0,1,2,3

# Memory usage optimization
# --max-sessions=100000
```

### Network Tuning (Linux)

```bash
# Increase socket backlog for WebSocket
echo 4096 | sudo tee /proc/sys/net/core/somaxconn

# Increase TCP buffer sizes
sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"

# Disable Nagle's algorithm for low-latency
sysctl -w net.ipv4.tcp_nodelay=1

# Increase TCP connections limit
sysctl -w net.ipv4.tcp_max_syn_backlog=8192
```

---

## 9. Database Schema Quick View

### Location Table (User Registration)
```sql
SELECT username, domain, contact, ruri, expires, q
FROM location;

-- Find active registrations
SELECT username, contact FROM location
WHERE expires > UNIX_TIMESTAMP()
AND domain = 'example.com';
```

### Dialog Table (Active Calls)
```sql
SELECT callid, from_uri, to_uri, start_time, state
FROM dialog;

-- Count active calls
SELECT COUNT(*) as active_calls
FROM dialog
WHERE state = 'confirmed';
```

---

## 10. Monitoring Dashboard Quick Setup

```bash
#!/bin/bash
# Real-time monitoring of OpenSIPs WebRTC

while true; do
  clear
  echo "=== OpenSIPs WebRTC Status ==="
  echo "Time: $(date)"
  echo ""

  echo "Active Calls:"
  opensipsctl fifo get_statistics | grep "^dialog:" | head -2

  echo ""
  echo "RTPEngine Status:"
  echo "ping" | nc -u 127.0.0.1 22222 && echo "✓ RTPEngine Online" || echo "✗ RTPEngine Offline"

  echo ""
  echo "TCP/WebSocket Connections:"
  netstat -an | grep EST | grep -E ":443|:8080|:5061" | wc -l

  echo ""
  echo "Recent Errors (last 10):"
  tail -10 /var/log/opensips/opensips.log | grep -i error

  sleep 5
done
```

---

## 11. Version Comparison Quick Chart

```
┌──────────────┬────────────┬──────────────┬────────────┬─────────────┐
│ Version      │ Release    │ WebRTC Ready │ LTS        │ Recommended │
├──────────────┼────────────┼──────────────┼────────────┼─────────────┤
│ 3.0.x        │ 2018       │ ✓ Basic      │ ✗          │ ✗           │
│ 3.1.x        │ 2020       │ ✓ Full       │ ✗          │ ✗           │
│ 3.2.x (LTS)  │ 2021       │ ✓✓ + relay   │ ✓ (3y)     │ ✓✓✓         │
│ 3.3.x        │ 2022       │ ✓✓ Enhanced  │ ✗          │ ✓✓          │
│ 3.4.x+       │ 2023+      │ ✓✓ Modern    │ TBD        │ ✓           │
└──────────────┴────────────┴──────────────┴────────────┴─────────────┘

RECOMMENDATION FOR IF.bus: Use 3.2.x LTS (stable, 3-year support)
```

---

## 12. Deployment Decision Tree

```
START: Choosing OpenSIPs Version
│
├─ Need Long-Term Support (3+ years)?
│  └─ YES → Use 3.2.x LTS ✓✓✓
│  └─ NO  → Continue below
│
├─ Need latest features (B2B, IM)?
│  └─ YES → Use 3.3.x or 3.4.x ✓
│  └─ NO  → Use 3.2.x LTS ✓
│
└─ Decision: Version X.Y.Z selected

DEPLOYMENT CHOICE
│
├─ Single node (PoC/test)?
│  └─ Standalone pattern (simplest)
│
├─ Production, small scale (<10 nodes)?
│  └─ Active-Passive HA (safer)
│
├─ Production, medium scale (10-30 nodes)?
│  └─ Active-Active with LB (balanced)
│
└─ Enterprise scale (30+ nodes)?
   └─ Full clustering with Clusterer (most complex)
```

---

## 13. Critical Success Factors Checklist

- [ ] RTPEngine running BEFORE starting OpenSIPs
- [ ] TLS certificates valid (use CA-signed in production)
- [ ] Firewall allows: 443/WSS, 5060/UDP, 5061/TLS, 22222/UDP (RTPEngine)
- [ ] Media ports open: 10000-20000/UDP
- [ ] Database (MariaDB/PostgreSQL) running and accessible
- [ ] rtpengine_manage() flags match endpoint types (Web vs SIP)
- [ ] Dialog module enabled for call tracking
- [ ] Logging enabled (at least WARN level) for production
- [ ] Health checks configured for RTPEngine connectivity
- [ ] Monitoring/alerting setup BEFORE going live

---

## 14. Go/No-Go Checklist for Production

### Infrastructure
- [ ] Load balancer with sticky sessions configured
- [ ] Multiple RTPEngine nodes (for HA)
- [ ] Database replication working
- [ ] DNS failover records configured
- [ ] Monitoring and alerting active

### Configuration
- [ ] All TLS certificates valid and non-self-signed
- [ ] rtpengine_manage() flags proven in staging
- [ ] Failover tested and documented
- [ ] Logging aggregation working
- [ ] Performance baseline established

### Testing
- [ ] WebRTC-to-WebRTC calls working
- [ ] WebRTC-to-SIP calls working
- [ ] SIP-to-WebRTC calls working
- [ ] 100+ concurrent calls tested
- [ ] Node failure handled gracefully

### Operations
- [ ] On-call rotation established
- [ ] Runbooks written and tested
- [ ] Backup/restore procedures documented
- [ ] Escalation contacts defined
- [ ] Change management process defined

---

**Last Updated**: 2025-11-11
**Purpose**: Fast reference during implementation
**Keep Handy**: During troubleshooting and deployment phases
