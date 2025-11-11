# SIP NDI Integration - API Reference

## Quick Reference

### Import

```python
from communication.sip_ndi_ingest import (
    SIPNDIIngest,
    NDIDiscovery,
    NDISource,
    NDIStreamConfig,
    NDIStreamState
)
```

---

## Classes

### SIPNDIIngest

Main orchestrator for NDI video streaming integration with SIP calls.

#### Constructor

```python
def __init__(self, config: Optional[NDIStreamConfig] = None)
```

**Parameters**:
- `config` (NDIStreamConfig, optional): Encoding configuration. Defaults to standard 1080p/30fps H.264.

**Example**:
```python
ndi = SIPNDIIngest()  # Use defaults

# OR with custom config
config = NDIStreamConfig(resolution="720p", framerate=60)
ndi = SIPNDIIngest(config=config)
```

#### Methods

##### start_stream()

Start NDI video stream for SIP expert call.

```python
async def start_stream(
    self,
    trace_id: str,
    expert_id: str,
    call_id: str,
    source_name: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters**:
- `trace_id` (str): IF trace ID from X-IF-Trace-ID header
- `expert_id` (str): SIP URI of external expert
- `call_id` (str): SIP call identifier
- `source_name` (str, optional): Specific NDI source to use. If None, uses first available.

**Returns**:
```python
{
    "status": "streaming" | "unavailable" | "error",
    "stream_id": str,              # Unique stream identifier
    "source": {                    # NDI source info
        "name": str,
        "ip_address": str,
        "port": int,
        "stream_name": str,
        "capabilities": List[str]
    },
    "encoding": {                  # Encoding config
        "video_codec": str,
        "resolution": str,
        "framerate": int,
        "bitrate": int
    },
    "rtp_port": int               # RTP streaming port
}
```

**Example**:
```python
result = await ndi.start_stream(
    trace_id="trace-abc123",
    expert_id="expert-safety@external.advisor",
    call_id="sip-call-xyz789"
)

if result["status"] == "streaming":
    print(f"Streaming on port {result['rtp_port']}")
```

##### stop_stream()

Stop NDI video stream and cleanup resources.

```python
async def stop_stream(self, stream_id: str) -> Dict[str, Any]
```

**Parameters**:
- `stream_id` (str): Stream identifier from start_stream()

**Returns**:
```python
{
    "status": "terminated" | "not_found",
    "stream_id": str,
    "duration_seconds": float,
    "stats": {
        "duration_seconds": float,
        "frames_sent": int,
        "bytes_sent": int,
        "source": str,
        "encoding": Dict
    }
}
```

**Example**:
```python
result = await ndi.stop_stream("ndi-stream-abc123")
print(f"Stream duration: {result['duration_seconds']:.2f}s")
```

##### get_stream_stats()

Get real-time statistics for active stream.

```python
def get_stream_stats(self, stream_id: str) -> Optional[Dict[str, Any]]
```

**Parameters**:
- `stream_id` (str): Stream identifier

**Returns**:
```python
{
    "call_id": str,
    "trace_id": str,
    "expert_id": str,
    "source": Dict,
    "started_at": str,           # ISO8601 timestamp
    "encoding": Dict,
    "frames_sent": int,
    "bytes_sent": int
}
```

**Example**:
```python
stats = ndi.get_stream_stats("ndi-stream-abc123")
if stats:
    print(f"Frames sent: {stats['frames_sent']}")
```

##### get_all_active_streams()

Get list of all currently active NDI streams.

```python
def get_all_active_streams(self) -> List[Dict[str, Any]]
```

**Returns**: List of stream info dicts (same format as get_stream_stats)

**Example**:
```python
active = ndi.get_all_active_streams()
print(f"Active streams: {len(active)}")
```

---

### NDIDiscovery

Network discovery of NDI sources via mDNS/Bonjour or multicast.

#### Methods

##### discover_sources()

Discover NDI sources on local network via multicast.

```python
async def discover_sources(self, timeout: float = 5.0) -> List[NDISource]
```

**Parameters**:
- `timeout` (float, optional): Discovery timeout in seconds. Default: 5.0

**Returns**: List of NDISource objects

**Example**:
```python
discovery = NDIDiscovery()
sources = await discovery.discover_sources(timeout=3.0)

for source in sources:
    print(f"Found: {source.name} at {source.ip_address}")
```

---

### NDISource (Dataclass)

Represents a discovered NDI video source.

#### Fields

```python
@dataclass
class NDISource:
    name: str                    # Source name (e.g., "IF-Evidence-Camera-1")
    ip_address: str              # Network address
    port: int                    # NDI service port
    stream_name: str             # NDI stream identifier
    capabilities: List[str]      # ["video", "audio", "metadata"]
    discovered_at: str           # ISO8601 timestamp
```

#### Methods

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary representation.

**Example**:
```python
source = NDISource(
    name="Camera-1",
    ip_address="10.0.1.50",
    port=5960,
    stream_name="evidence-stream",
    capabilities=["video", "audio"],
    discovered_at="2025-11-11T23:30:00Z"
)

source_dict = source.to_dict()
```

---

### NDIStreamConfig (Dataclass)

Configuration for NDI stream encoding and transmission.

#### Fields

```python
@dataclass
class NDIStreamConfig:
    video_codec: str = "h264"      # h264, h265, vp9
    resolution: str = "1080p"      # 1080p, 720p, 480p
    framerate: int = 30            # 30, 60
    bitrate: int = 5000            # kbps
    audio_enabled: bool = True
    metadata_enabled: bool = True
    low_latency: bool = True       # Enable low-latency mode
```

#### Methods

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary representation.

**Example**:
```python
# High quality
high_quality = NDIStreamConfig(
    video_codec="h264",
    resolution="1080p",
    framerate=60,
    bitrate=8000,
    low_latency=True
)

# Low bandwidth
low_bandwidth = NDIStreamConfig(
    resolution="720p",
    framerate=30,
    bitrate=2000
)
```

---

### NDIStreamState (Enum)

Stream lifecycle states.

#### Values

```python
class NDIStreamState(Enum):
    IDLE = "idle"                  # Not active
    DISCOVERING = "discovering"    # Searching for sources
    CONNECTING = "connecting"      # Connecting to source
    STREAMING = "streaming"        # Active streaming
    PAUSED = "paused"              # Temporarily paused
    ERROR = "error"                # Error state
    TERMINATED = "terminated"      # Stream ended
```

**Example**:
```python
if ndi.state == NDIStreamState.STREAMING:
    print("Video is streaming")
```

---

## Common Patterns

### Basic Usage

```python
from communication.sip_ndi_ingest import SIPNDIIngest

# Initialize
ndi = SIPNDIIngest()

# Start stream
result = await ndi.start_stream(
    trace_id="trace-123",
    expert_id="expert@example.com",
    call_id="call-456"
)

if result["status"] == "streaming":
    # Stream active
    stream_id = result["stream_id"]
    
    # Monitor stream
    stats = ndi.get_stream_stats(stream_id)
    
    # Stop when done
    await ndi.stop_stream(stream_id)
```

### With Custom Configuration

```python
from communication.sip_ndi_ingest import SIPNDIIngest, NDIStreamConfig

# High-quality config
config = NDIStreamConfig(
    video_codec="h264",
    resolution="1080p",
    framerate=60,
    bitrate=8000
)

ndi = SIPNDIIngest(config=config)
result = await ndi.start_stream(...)
```

### Discovery and Selection

```python
from communication.sip_ndi_ingest import SIPNDIIngest

ndi = SIPNDIIngest()

# Discover sources
sources = await ndi.discovery.discover_sources()

# Select specific source
if sources:
    result = await ndi.start_stream(
        trace_id="trace-123",
        expert_id="expert@example.com",
        call_id="call-456",
        source_name=sources[0].name  # Use first source
    )
```

### Error Handling

```python
from communication.sip_ndi_ingest import SIPNDIIngest

ndi = SIPNDIIngest()

try:
    result = await ndi.start_stream(
        trace_id="trace-123",
        expert_id="expert@example.com",
        call_id="call-456"
    )
    
    if result["status"] == "unavailable":
        # No NDI sources found - graceful degradation
        print("Video unavailable, continuing with audio only")
    
    elif result["status"] == "error":
        # Error occurred
        print(f"Error: {result.get('reason')}")
    
    elif result["status"] == "streaming":
        # Success!
        print(f"Streaming: {result['stream_id']}")

except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {e}")
```

### Multiple Streams

```python
ndi = SIPNDIIngest()

# Start multiple streams
streams = []
for call in calls:
    result = await ndi.start_stream(
        trace_id=call["trace_id"],
        expert_id=call["expert_id"],
        call_id=call["call_id"]
    )
    if result["status"] == "streaming":
        streams.append(result["stream_id"])

# Monitor all active streams
active = ndi.get_all_active_streams()
print(f"Active: {len(active)} streams")

# Cleanup all
for stream_id in streams:
    await ndi.stop_stream(stream_id)
```

---

## Integration with SIPEscalateProxy

```python
from communication.sip_proxy import SIPEscalateProxy
from communication.sip_ndi_ingest import SIPNDIIngest

class SIPEscalateProxy:
    def __init__(self):
        # ... existing code ...
        self.ndi_ingest = SIPNDIIngest()

    async def handle_escalate(self, message: IFMessage):
        # ... establish SIP call ...
        
        # Optional: Enable NDI video
        if message.payload.get("ndi_video_enabled"):
            ndi_result = await self.ndi_ingest.start_stream(
                trace_id=trace_id,
                expert_id=expert_id,
                call_id=sip_call_id
            )
            
            if ndi_result["status"] == "streaming":
                # Log to IF.witness
                await self.if_witness.log_sip_event(
                    event_type="NDI_STREAM_STARTED",
                    sip_method="VIDEO",
                    trace_id=trace_id,
                    details=ndi_result
                )
        
        return {
            "status": "connected",
            "call_id": sip_call_id,
            "ndi_video": ndi_result if ndi_video_enabled else None
        }
```

---

## File Location

**Module**: `/home/user/infrafabric/src/communication/sip_ndi_ingest.py`

**Tests**: `/home/user/infrafabric/tests/test_sip_ndi_integration.py`

**Examples**: `/home/user/infrafabric/examples/sip_ndi_usage_example.py`

**Documentation**: `/home/user/infrafabric/docs/INTEGRATION_SIP_NDI.md`

---

## See Also

- [Integration Guide](docs/INTEGRATION_SIP_NDI.md) - Detailed integration documentation
- [Usage Examples](examples/sip_ndi_usage_example.py) - Runnable code examples
- [Test Suite](tests/test_sip_ndi_integration.py) - Test reference

---

**Version**: 1.0  
**Date**: 2025-11-11  
**Status**: Production Ready
