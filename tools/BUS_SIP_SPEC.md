# IF.bus SIP CLI Specification

## Core Design: Dead Simple Integration

```
if bus [command] sip [name] [options]
```

**Auto-features:**
- Server type auto-detection from response headers
- Auto-optimal configuration per server class
- Auto-failover with round-robin
- Auto-retry with exponential backoff (base 2ms, cap 5s)

---

## Commands

### 1. Add Server
```bash
if bus add sip <name> <type> --auth [key=value...]
```

### 2. Test Connection
```bash
if bus test sip <name>
```

### 3. Make Call
```bash
if bus call sip <name> from=1001 to=1002
```

### 4. Hangup
```bash
if bus hangup sip <name> call_id=xyz
```

### 5. List Servers
```bash
if bus list sip
```

### 6. Remove Server
```bash
if bus remove sip <name>
```

---

## Examples by Server Type

### 1. **Asterisk** (PBX/VoIP)
```bash
if bus add sip myast asterisk --auth user=admin secret=pass123
if bus test sip myast
if bus call sip myast from=1001 to=2000
if bus hangup sip myast call_id=chan-001
```

### 2. **FreeSWITCH** (Soft Switch)
```bash
if bus add sip myfs freeswitch --auth apikey=ABC123 domain=fs.local
if bus call sip myfs from=sofia/1001 to=sofia/2000
```

### 3. **Kamailio** (SIP Router)
```bash
if bus add sip mykamailio kamailio --auth token=xyz789 realm=sip.local
if bus test sip mykamailio
if bus call sip mykamailio from=sip:1001@sip.local to=sip:2000@sip.local
```

### 4. **OpenSIPS** (SIP Server)
```bash
if bus add sip myopensips opensips --auth user=admin secret=pass domain=opensips.local
if bus call sip myopensips from=1001 to=1002
```

### 5. **Twilio** (Cloud VoIP)
```bash
if bus add sip mytwilio twilio --auth account_sid=AC123 auth_token=xyz789
if bus call sip mytwilio from=+1234567890 to=+9876543210
if bus hangup sip mytwilio call_id=CA12345xyz
```

### 6. **Vonage/Nexmo** (Cloud Comms)
```bash
if bus add sip myvonage vonage --auth api_key=key123 api_secret=secret456
if bus test sip myvonage
if bus call sip myvonage from=MyApp to=+14155552671
```

### 7. **FusionPBX** (FreeSWITCH UI)
```bash
if bus add sip myfusion fusionpbx --auth username=admin password=pass123 domain=fusion.local
if bus call sip myfusion from=100 to=101
if bus list sip
if bus remove sip myfusion
```

---

## Config Storage

```json
{
  "myast": {
    "type": "asterisk",
    "auth": {"user": "admin", "secret": "pass123"}
  },
  "mytwilio": {
    "type": "twilio",
    "auth": {"account_sid": "AC123", "auth_token": "xyz789"}
  }
}
```

Stored at: `~/.if/sip_servers.json`

---

## Error Handling

- **Server not found**: "Not found" → Exit code 1
- **Connection failed**: Auto-retry with backoff (2ms → 4ms → 8ms... → 5s)
- **Auth failure**: Log error, suggest credentials check
- **Call failed**: Detailed SIP response code

---

## Failover Strategy

```
Primary → Backup 1 → Backup 2 [round-robin if multiple same-type servers]
```

Example:
```bash
if bus add sip myast1 asterisk --auth user=admin secret=pass123
if bus add sip myast2 asterisk --auth user=admin secret=pass123
# Auto-failover: if myast1 fails, auto-routes to myast2
```

---

## Minimal Implementation (25 lines reference)

See `/home/user/infrafabric/tools/bus_sip.py` - compact, extensible, no dependencies beyond stdlib.
