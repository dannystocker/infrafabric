# SIP Adapter Implementation Guide for Agents 1-7

**Document Purpose:** Quick reference for implementing concrete SIP adapters
**Target Audience:** Agents 1-7 of IF.search swarm
**Base Design:** See `docs/AGENT-8-SIP-ADAPTER-DESIGN-REPORT.md`
**Base Class:** `src/adapters/sip_adapter_base.py`

---

## Quick Start

Each adapter implementation follows this template:

```python
from src.adapters import SIPAdapterBase, CallState, ConnectionState
from typing import Any, Dict

class YourAdapterAdapter(SIPAdapterBase):
    """Description of your adapter."""

    adapter_type = "your_type"  # One of: asterisk, freeswitch, kamailio, opensips, yate, pjsua, sipp

    SUPPORTED_VERSIONS = {
        "server": ["x.0", "y.x", "z.x"],
        "protocol": ["version"],
    }

    def __init__(self, config: Dict[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        # Your connection object(s)

    def connect(self, host: str, port: int, auth_config: Dict[str, Any]) -> bool:
        """Implement protocol-specific connection logic."""

    def disconnect(self) -> bool:
        """Implement graceful shutdown."""

    def make_call(self, from_number: str, to_number: str, **options) -> str:
        """Implement call initiation."""

    def hangup(self, call_id: str) -> bool:
        """Implement call termination."""

    def get_status(self, call_id: str) -> Dict[str, Any]:
        """Implement status query."""

    def health_check(self) -> Dict[str, Any]:
        """Return health metrics."""

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate adapter-specific config."""
```

---

## Per-Adapter Implementation Details

### Agent 1: Asterisk Adapter

**Status:** Skeleton provided (`src/adapters/asterisk_adapter.py`)
**Protocol:** AMI (Asterisk Manager Interface)
**Port:** 5038 (default)
**Language:** Python (socket-based)

**Key Protocol Commands:**
- `Action: Login` - Authenticate
- `Action: Originate` - Initiate call
- `Action: Hangup` - Terminate call
- `Action: Redirect` - Transfer call
- `Action: MixMonitor` - Record call

**Key Events to Handle:**
- `VarSet` - Call variable changes
- `Newchannel` - New call created
- `Newchannelstate` - Call state changes
- `Hangup` - Call ended
- `BridgeCreate/BridgeDestroy` - Conference created/destroyed

**Configuration Specifics:**
```yaml
type: asterisk
port: 5038  # AMI port
auth:
  username: asterisk
  password: managerpassword
realm: asterisk.local
```

**Test Against:** Asterisk 16+ (docker image: `asterisk:latest`)

---

### Agent 2: FreeSWITCH Adapter

**Status:** To implement
**Protocol:** ESL (Event Socket Library)
**Port:** 8021 (default)
**Language:** Python (socket-based)

**Key Protocol Commands:**
- `auth {password}` - Authenticate
- `originate {call_string}` - Initiate call
- `bgapi uuid_kill {uuid}` - Terminate call
- `api uuid_transfer {uuid} destination` - Transfer call
- `api uuid_record {uuid} start|stop` - Recording

**Key Events to Handle:**
- `CHANNEL_CREATE` - New call created
- `CHANNEL_STATE` - State changes (ringing, active, etc.)
- `CHANNEL_HANGUP` - Call ended
- `DTMF` - Digit received
- `CUSTOM` - Server-generated events

**Configuration Specifics:**
```yaml
type: freeswitch
port: 8021  # ESL port
auth:
  username: admin  # Typically not used
  password: ClueCon  # Default FreeSWITCH password
realm: freeswitch.local
```

**Test Against:** FreeSWITCH 1.10+ (docker: `freeswitch:latest`)

**Implementation Notes:**
- Event loop: ESL sends events asynchronously
- Command/response: Send commands, receive replies via channel
- UUID tracking: All calls identified by unique UUID

---

### Agent 3: Kamailio Adapter

**Status:** To implement
**Protocol:** MI (Management Interface) RPC
**Port:** 5060+ (configurable, commonly 5060)
**Language:** Python (XML-RPC or HTTP POST)

**Key Protocol Commands:**
- `dlg.list_all` - List dialogs
- `dlg.list` - List dialog for call
- `dlg.terminate` - Terminate dialog
- `t.uac` - Send request

**Key Events to Handle:**
- Dialog create/delete events
- SIP message events

**Configuration Specifics:**
```yaml
type: kamailio
port: 5060  # MI port (adjust as needed)
auth:
  username: admin  # For MI authentication
  password: secret
realm: kamailio.local
```

**Test Against:** Kamailio 5.2+ (docker: `kamailio:latest`)

**Implementation Notes:**
- MI is stateless (send command, get response)
- Dialog tracking: Use MI to query active dialogs
- Limited real-time events: May need polling for state changes

---

### Agent 4: OpenSIPS Adapter

**Status:** To implement
**Protocol:** MI_JSON (JSON-RPC over HTTP)
**Port:** 8888 (default)
**Language:** Python (HTTP POST + JSON)

**Key Protocol Commands:**
- `dlg.get_dialogs` - List dialogs
- `dlg.bridge` - Bridge two dialogs
- `dlg.terminate_dlg` - Terminate dialog
- `dlg.dump_file` - Get dialog state

**Key API Endpoints:**
- `/mi` - MI command endpoint
- `/jsonrpc` - JSON-RPC endpoint

**Configuration Specifics:**
```yaml
type: opensips
port: 8888  # MI_JSON port
auth:
  username: admin
  password: opensips  # Default password
realm: opensips.local
```

**Test Against:** OpenSIPS 3.2+ (docker: `opensips:latest`)

**Implementation Notes:**
- JSON-RPC protocol: Send POST request with `{"jsonrpc":"2.0","method":"...","params":[]}`
- HTTP-based: Simpler than socket-based protocols
- State querying: Dialog information available via `dlg` module

---

### Agent 5: Yate Adapter

**Status:** To implement
**Protocol:** Custom message format over TCP
**Port:** 5039 (default for rmanager)
**Language:** Python (socket-based)

**Key Message Types:**
- `engine.version` - Query version
- `engine.halt` - Shutdown server
- `call.route` - Route a call
- `call.drop` - Disconnect call
- `chan.attach` - Attach to channel

**Key Events to Handle:**
- `chan.startup` - Channel created
- `chan.state` - State changed
- `chan.hangup` - Channel closed
- `engine.timer` - Timer events

**Configuration Specifics:**
```yaml
type: yate
port: 5039  # Rmanager port
auth:
  username: admin
  password: yatepassword  # Configure in yate.conf
realm: yate.local
```

**Test Against:** Yate 5.x+ (docker: `yate:latest`)

**Implementation Notes:**
- Message format: Key-value pairs with 4-digit sequence numbers
- Acknowledgments: Expect `%%<seq>:ok` responses
- Event listening: Subscribe to channels after connection

---

### Agent 6: PJSUA Adapter

**Status:** To implement
**Protocol:** C++ library binding (via python-pjsua or ctypes)
**Port:** N/A (in-process)
**Language:** Python (library bindings)

**Key Library Calls:**
- `Account.create()` - Register SIP account
- `Call.make_call()` - Initiate call
- `Call.hangup()` - End call
- Callbacks for state changes

**Key Events to Handle:**
- `on_call_state_change` - Call state event
- `on_incoming_call` - Incoming call
- `on_media_state_change` - Media state
- `on_buddy_state` - Buddy presence

**Configuration Specifics:**
```yaml
type: pjsua
host: localhost  # Usually local
port: 5060  # SIP port for registration
auth:
  username: user
  password: secret
  realm: domain.com
```

**Test Against:** PJSUA2 library (requires C++ compilation)

**Installation:**
```bash
# Install PJSUA2 library
pip install pjsua2  # Or compile from source

# Or use ctypes binding
python -c "from pjsua2 import *; print('OK')"
```

**Implementation Notes:**
- Library-based: No network connection needed if local
- Threading: Use thread pool for async callbacks
- Codec negotiation: Handle in callback handlers

---

### Agent 7: SIPp Adapter

**Status:** To implement
**Protocol:** HTTP REST API
**Port:** 8080 (default)
**Language:** Python (requests HTTP library)

**Key REST Endpoints:**
- `GET /stats` - Get call statistics
- `POST /scenario` - Load scenario
- `GET /calls` - List active calls
- `DELETE /call/{id}` - Kill call
- `GET /logs` - Get logs

**Key Scenarios (Pre-defined Call Flows):**
- `uac.xml` - User agent client (outbound)
- `uas.xml` - User agent server (inbound)
- `register.xml` - Registration
- `call_with_transfer.xml` - Transfer

**Configuration Specifics:**
```yaml
type: sipp
host: localhost  # SIPp server
port: 8080  # REST API port
auth:
  username: n/a  # SIPp doesn't require auth
  password: n/a
  realm: sipp.test
```

**Test Against:** SIPp 3.6+ (docker: `opensourcemano/sippsippp:latest`)

**Installation:**
```bash
# Install SIPp
apt-get install sipp

# Or run in docker
docker run -d -p 8080:8080 opensourcemano/sippsippp:latest
```

**Implementation Notes:**
- HTTP-based: Easiest protocol to debug
- REST API: Standard JSON request/response
- Load testing: Design your scenarios before running
- Scenario files: XML-based call flow descriptions

---

## Common Implementation Patterns

### Pattern 1: Connection Management

```python
def connect(self, host: str, port: int, auth_config: Dict[str, Any]) -> bool:
    try:
        self._update_connection_state(
            ConnectionState.CONNECTING,
            f"Connecting to {self.adapter_type} server"
        )

        # Create connection object
        self.connection = self._create_connection(host, port, auth_config)

        # Verify connected
        if not self._is_connected():
            raise ConnectionError("Failed to establish connection")

        self._update_connection_state(
            ConnectionState.CONNECTED,
            f"Connected to {host}:{port}"
        )

        return True

    except Exception as e:
        self._update_connection_state(
            ConnectionState.ERROR,
            f"Connection failed: {e}"
        )
        raise ConnectionError(f"Failed to connect: {e}")

    finally:
        self.retry_count = 0  # Reset retry counter on success
```

### Pattern 2: Async Event Handling

```python
def _start_event_listener(self):
    """Start background thread to listen for events."""
    import threading

    def listener_thread():
        while self.is_connected():
            try:
                event = self._receive_event()  # Protocol-specific
                self._handle_event(event)
            except Exception as e:
                self.logger.exception(f"Event listener error: {e}")

    thread = threading.Thread(target=listener_thread, daemon=True)
    thread.start()

def _handle_event(self, event: Dict[str, Any]):
    """Parse event and emit appropriate callback."""
    if event["type"] == "call_state_change":
        call_id = event["call_id"]
        state = self._map_state(event["state"])  # Map to CallState enum
        self.emit_call_state_changed(call_id=call_id, state=state)

    elif event["type"] == "incoming_call":
        self.emit_incoming_call(
            call_id=event["call_id"],
            from_number=event["from"],
            to_number=event["to"]
        )
```

### Pattern 3: Call Tracking

```python
def make_call(self, from_number: str, to_number: str, **options) -> str:
    call_id = self.generate_call_id()
    request_id = self.generate_request_id()

    try:
        # Initiate call via protocol
        self._protocol_make_call(from_number, to_number, call_id, **options)

        # Track locally
        self._add_active_call(call_id, {
            "from_number": from_number,
            "to_number": to_number,
            "state": CallState.DIALING,
            "start_time": time.time(),
            "request_id": request_id,
        })

        # Emit event
        self.emit_call_state_changed(
            call_id=call_id,
            state=CallState.DIALING,
            from_number=from_number,
            to_number=to_number
        )

        self.metrics.record_call(success=True)
        return call_id

    except Exception as e:
        self.emit_error(code=500, message=f"Call failed: {e}", call_id=call_id)
        self.metrics.record_call(success=False)
        raise CallError(f"Failed to make call: {e}")
```

### Pattern 4: Health Check

```python
def health_check(self) -> Dict[str, Any]:
    metrics = self.metrics.get_metrics()
    metrics["active_calls"] = self._get_active_calls_count()

    # Determine health status
    if not self.is_connected():
        status = HealthStatus.CRITICAL
    elif metrics["call_success_rate"] < 0.8:
        status = HealthStatus.CRITICAL
    elif metrics["latency"]["avg_ms"] > 300 or metrics["call_success_rate"] < 0.9:
        status = HealthStatus.DEGRADED
    else:
        status = HealthStatus.HEALTHY

    return {
        "adapter": self.adapter_type,
        "connected": self.is_connected(),
        "uptime_seconds": metrics["uptime_seconds"],
        "metrics": metrics,
        "last_check": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status.value,
    }
```

---

## Testing Checklist

For each adapter implementation, verify:

### Unit Tests
- [ ] Config validation (valid inputs pass, invalid inputs raise ConfigurationError)
- [ ] Response parsing (protocol-specific message formats)
- [ ] Error handling (proper exception mapping)
- [ ] State machine transitions (valid state changes only)

### Integration Tests
- [ ] Connect to real server successfully
- [ ] Disconnect gracefully
- [ ] Make outbound call (complete flow: dialing → ringing → connected → hangup)
- [ ] Receive inbound call (if applicable)
- [ ] Call transfer (if supported)
- [ ] Call hold/resume (if supported)
- [ ] Health check returns valid metrics
- [ ] Event callbacks fire correctly
- [ ] Concurrent calls (10+ simultaneous)
- [ ] Reconnection after network failure
- [ ] Timeout handling and retry logic

### Stress Tests
- [ ] 100+ concurrent calls
- [ ] Connection pool fully utilized
- [ ] Server overload recovery
- [ ] Rapid connect/disconnect cycles
- [ ] Large message handling

### Compatibility Tests
- [ ] Call routing to other adapters (if possible)
- [ ] Conference with mixed adapter types
- [ ] Call history retrieval
- [ ] CDR format compatibility

---

## Documentation Requirements

Each adapter must document:

1. **Configuration Options**
   - All required fields
   - All optional fields
   - Protocol-specific settings
   - Example config (YAML)

2. **Supported Features**
   - Methods implemented (required + optional)
   - Methods not implemented (raise NotImplementedError)
   - Feature matrix (what each method does)

3. **Protocol Details**
   - Wire format specifications
   - Command/response examples
   - Event types and formats
   - Error codes and handling

4. **Troubleshooting Guide**
   - Common errors and solutions
   - Debug logging tips
   - Network configuration requirements
   - Firewall/port settings

5. **Performance Characteristics**
   - Latency (typical vs worst case)
   - Max concurrent calls
   - Memory usage
   - CPU usage

Example template:
```markdown
# {AdapterName} SIP Adapter

**Protocol:** {Protocol Name}
**Port:** {Default Port}
**Status:** Implementation Status

## Configuration

Required fields:
- type: {adapter_type}
- host: Server hostname
- port: {Default Port}
- auth.username: User
- auth.password: Password

Optional fields:
- ...

## Supported Features

✅ Outbound calls
✅ Inbound calls
✅ Call transfer
❌ Conference (not supported)

## Examples

### Connect
```python
adapter = {AdapterClass}(config)
adapter.connect(...)
```

## Troubleshooting

### Error: Connection refused
...
```

---

## Code Quality Standards

All implementations must follow:

- **PEP 8:** Python style guide (black formatter recommended)
- **Type Hints:** All function signatures typed
- **Docstrings:** All public methods documented (Google format)
- **Error Handling:** Proper exception hierarchy usage
- **Logging:** Debug logs for troubleshooting, info logs for operations
- **Thread Safety:** Use locks where accessing shared state
- **No Credentials:** Never log passwords or tokens

Example:
```python
def make_call(
    self,
    from_number: str,
    to_number: str,
    **options
) -> str:
    """
    Initiate outbound call.

    Args:
        from_number: Calling number (SIP URI or E.164)
        to_number: Called number (SIP URI or E.164)
        **options: Optional call parameters
            - timeout: Ring timeout in seconds (default: 60)
            - caller_id_name: Display name (default: adapter_type)
            - record: Record call (default: False)

    Returns:
        call_id: Unique call identifier (format: if://call/{uuid})

    Raises:
        ConnectionError: Not connected to server
        CallError: Call initiation failed
        ConfigurationError: Missing required fields

    Example:
        >>> adapter.make_call("+1234567890", "+0987654321", timeout=30)
        'if://call/12345678-1234-5678-...'
    """
```

---

## Timeline & Coordination

**Suggested Implementation Order:**
1. Asterisk (already has skeleton)
2. FreeSWITCH (similar socket-based protocol)
3. Kamailio (HTTP-based RPC)
4. OpenSIPS (JSON-RPC, simpler than Kamailio)
5. Yate (custom message protocol)
6. PJSUA (library binding - complex)
7. SIPp (HTTP REST - simplest)

**Coordination:**
- Share common issues/solutions in agent channel
- Cross-test adapters when possible (route calls between adapters)
- Document lessons learned
- Create shared test fixtures for mocking

---

## Common Pitfalls

❌ **Don't:** Log credentials (usernames, passwords, auth tokens)
✅ **Do:** Log sanitized config (host, port, adapter type)

❌ **Don't:** Block on network I/O in main thread
✅ **Do:** Use background threads or async for event listening

❌ **Don't:** Ignore call state transitions
✅ **Do:** Validate state machine transitions

❌ **Don't:** Hardcode timeouts/retries
✅ **Do:** Use config values with reasonable defaults

❌ **Don't:** Swallow exceptions silently
✅ **Do:** Log and emit error events

---

## Additional Resources

- Base Class: `src/adapters/sip_adapter_base.py` (650+ lines, fully documented)
- Design Report: `docs/AGENT-8-SIP-ADAPTER-DESIGN-REPORT.md`
- Architecture Spec: `docs/architecture/UNIFIED-SIPO-ADAPTER-PATTERN.yaml`
- Example Adapter: `src/adapters/asterisk_adapter.py`
- IF Framework: `papers/IF-foundations.md` (philosophy + architecture)

---

**Questions?** Refer to the design report or ask in the agent coordination channel.

**Ready to implement?** Create your adapter file in `src/adapters/{adapter_type}_adapter.py` and inherit from `SIPAdapterBase`.

Good luck! 🚀

---

**Document:** `if://doc/sip-adapter-implementation-guide-v1-2025-11-11`
**Created By:** Agent 8 (IF.search)
**For:** Agents 1-7 (Implementation team)
