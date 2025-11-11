# SIP NDI Integration Guide

## Overview

The `sip_ndi_ingest.py` module provides NDI (Network Device Interface) video streaming integration for SIP external expert calls in the IF.ESCALATE system.

## Quick Start

```python
from communication.sip_ndi_ingest import SIPNDIIngest, NDIStreamConfig

# Initialize NDI ingest with custom config
config = NDIStreamConfig(
    video_codec="h264",
    resolution="1080p",
    framerate=30,
    bitrate=5000,
    low_latency=True
)

ndi_ingest = SIPNDIIngest(config=config)

# Start video stream during SIP call
result = await ndi_ingest.start_stream(
    trace_id="trace-abc123",
    expert_id="expert-safety@external.advisor",
    call_id="sip-call-xyz789",
    source_name="IF-Evidence-Camera-1"  # Optional
)

# Check stream status
if result["status"] == "streaming":
    print(f"Video streaming on port {result['rtp_port']}")
    print(f"Source: {result['source']['name']}")
    print(f"Encoding: {result['encoding']['video_codec']}")

# Stop stream when call ends
await ndi_ingest.stop_stream(result["stream_id"])
```

## Integration with SIPEscalateProxy

Add NDI support to SIPEscalateProxy.handle_escalate():

```python
from communication.sip_ndi_ingest import SIPNDIIngest

class SIPEscalateProxy:
    def __init__(self):
        # ... existing initialization ...
        self.ndi_ingest = SIPNDIIngest()  # Add NDI support

    async def handle_escalate(self, message: IFMessage) -> Dict[str, Any]:
        # ... existing code ...

        # After SIP call established, optionally start NDI video
        ndi_enabled = message.payload.get("ndi_video_enabled", False)

        if ndi_enabled:
            ndi_result = await self.ndi_ingest.start_stream(
                trace_id=trace_id,
                expert_id=expert_id,
                call_id=sip_call_id
            )

            if ndi_result["status"] == "streaming":
                logger.info(f"[SIPProxy] NDI video streaming started: {ndi_result['stream_id']}")

                # Log to IF.witness
                await self.if_witness.log_sip_event(
                    event_type="NDI_STREAM_STARTED",
                    sip_method="VIDEO",
                    trace_id=trace_id,
                    details={
                        "stream_id": ndi_result["stream_id"],
                        "source": ndi_result["source"],
                        "encoding": ndi_result["encoding"]
                    }
                )
            else:
                logger.warning(f"[SIPProxy] NDI video unavailable: {ndi_result.get('reason')}")

        return {
            "status": "connected",
            "call_id": sip_call_id,
            "expert_id": expert_id,
            "ndi_video": ndi_result if ndi_enabled else None
        }
```

## Architecture

### Components

1. **NDIDiscovery**: Network discovery of NDI sources via mDNS/multicast
2. **SIPNDIIngest**: Main orchestrator for video streaming
3. **NDIStreamConfig**: Configuration for encoding parameters
4. **NDISource**: Data structure for discovered NDI sources
5. **NDIStreamState**: Lifecycle state management

### Data Flow

```
NDI Camera → NDI Discovery → SIPNDIIngest → H.264 Encoder → RTP → SIP Expert
                                    ↓
                              IF Metadata Embedding
                              (X-IF-Trace-ID, etc.)
                                    ↓
                              IF.witness Logging
```

### Metadata Embedding

All video streams include IF metadata in H.264 SEI (Supplemental Enhancement Information) user data:

```json
{
  "X-IF-Trace-ID": "trace-abc123",
  "X-IF-Expert-ID": "expert-safety@external.advisor",
  "X-IF-Timestamp": "2025-11-11T23:24:00Z",
  "X-IF-Frame-Index": 1234
}
```

## Configuration Options

### Video Codecs
- `h264`: Default, best compatibility (AVC/H.264)
- `h265`: Higher compression (HEVC/H.265)
- `vp9`: WebRTC-friendly (future support)

### Resolutions
- `1080p`: 1920x1080 (recommended for evidence)
- `720p`: 1280x720 (bandwidth-constrained)
- `480p`: 854x480 (fallback)

### Frame Rates
- `30`: Standard (30fps, default)
- `60`: High motion (60fps)

### Bitrates
- 5000 kbps: High quality 1080p
- 3000 kbps: Standard 1080p
- 2000 kbps: 720p
- 1000 kbps: 480p

## Production Deployment

### NDI SDK Integration

For production, replace stub implementation with actual NDI SDK:

```python
import NDIlib as ndi

# Initialize NDI
ndi.initialize()

# Create NDI finder
ndi_find = ndi.find_create_v2()

# Wait for sources
sources = ndi.find_wait_for_sources(ndi_find, timeout_ms=5000)

# Create receiver
ndi_recv = ndi.recv_create_v3()

# Connect to source
ndi.recv_connect(ndi_recv, sources[0])

# Capture frames
while True:
    frame = ndi.recv_capture_v2(ndi_recv, timeout_ms=1000)
    # Process frame...
```

### FFmpeg Encoding Pipeline

Example FFmpeg command for H.264 encoding with IF metadata:

```bash
ffmpeg -f ndi -i "IF-Evidence-Camera-1" \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -b:v 5000k -maxrate 6000k -bufsize 10000k \
  -g 30 -sc_threshold 0 -rc-lookahead 0 \
  -metadata:s:v X-IF-Trace-ID=trace-abc123 \
  -metadata:s:v X-IF-Expert-ID=expert-safety@external.advisor \
  -f rtp rtp://expert-endpoint:5004
```

## Security Considerations

1. **TLS/SRTP**: All RTP streams should use SRTP with TLS key exchange
2. **Authentication**: Verify expert identity before streaming video
3. **Network Isolation**: NDI discovery limited to trusted network segments
4. **Audit Logging**: All stream events logged to IF.witness
5. **Bandwidth Management**: Rate limiting to prevent DoS

## Troubleshooting

### No NDI Sources Found

- Check network connectivity
- Verify NDI devices on same subnet
- Check firewall rules (UDP port 5353)
- Enable multicast on network switches

### Stream Connection Failed

- Verify NDI source is active
- Check network bandwidth
- Review firewall/NAT configuration
- Test with NDI Studio Monitor

### Encoding Issues

- Check FFmpeg installation
- Verify codec support (libx264/libx265)
- Monitor CPU usage
- Adjust bitrate/resolution

## Testing

Run integration tests:

```bash
pytest tests/test_sip_ndi_integration.py -v
```

## Philosophy Grounding

- **IF.ground Observable**: Video evidence is transparently available to external experts
- **Wu Lun (朋友)**: Visual context enhances peer collaboration and decision-making
- **IF.TTT**: Traceable through metadata, Transparent through logging, Trustworthy through integrity checks

## Related Documentation

- Session 1: NDI Implementation (for compatibility)
- Session 3: H.323 Gateway (for H.239 content channel bridging)
- Session 4: SIP ESCALATE Architecture
- IF.witness: Audit Trail Specifications
