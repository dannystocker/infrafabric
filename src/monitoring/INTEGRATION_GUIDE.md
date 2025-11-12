# WebRTC Quality Monitor Integration Guide

## Overview

The `WebRTCQualityMonitor` class provides real-time connection quality monitoring for WebRTC peer-to-peer connections. It integrates seamlessly with the existing `IFAgentWebRTC` class.

## Quick Start

### Basic Integration Example

```typescript
import { WebRTCQualityMonitor } from './webrtc_quality';

// When creating a peer connection in IFAgentWebRTC
const peerConnection = new RTCPeerConnection({ ... });
const peerId = 'peer-123';

// Create and start monitoring
const monitor = new WebRTCQualityMonitor(peerConnection, peerId);

// Register quality event handlers
monitor.on('quality_degraded', (metrics) => {
  console.warn(`Quality degraded for ${metrics.peerId}:`, {
    rtt: metrics.rtt,
    jitter: metrics.jitter,
    packetLoss: metrics.packetLossPercent,
    quality: metrics.quality
  });
});

monitor.on('quality_restored', (metrics) => {
  console.log(`Quality restored for ${metrics.peerId}`);
});

// Start monitoring (polls every 2 seconds by default)
monitor.start();

// Get current metrics
const currentMetrics = monitor.getCurrentMetrics();
console.log(`RTT: ${currentMetrics.rtt}ms, Bandwidth: ${currentMetrics.bandwidth.upload} bytes/s`);

// Stop monitoring when done
monitor.stop();
```

## Integration with IFAgentWebRTC

### Adding Quality Monitoring to WebRTC Mesh

```typescript
import { IFAgentWebRTC } from './webrtc-agent-mesh';
import { WebRTCQualityMonitor } from '../monitoring/webrtc_quality';

class EnhancedIFAgentWebRTC extends IFAgentWebRTC {
  private qualityMonitors: Map<string, WebRTCQualityMonitor> = new Map();

  // Override createPeerConnection to add monitoring
  protected createPeerConnection(peerId: string): RTCPeerConnection {
    const pc = super.createPeerConnection(peerId);

    // Add quality monitoring
    const monitor = new WebRTCQualityMonitor(pc, peerId, {
      pollIntervalMs: 2000,
      thresholds: {
        rttMs: 150,
        jitterMs: 30,
        packetLossPercent: 5
      }
    });

    monitor.on('quality_degraded', (metrics) => {
      this.handleQualityDegraded(peerId, metrics);
    });

    monitor.on('quality_restored', (metrics) => {
      this.handleQualityRestored(peerId, metrics);
    });

    this.qualityMonitors.set(peerId, monitor);
    monitor.start();

    return pc;
  }

  private handleQualityDegraded(peerId: string, metrics: ConnectionQualityMetrics): void {
    // Log to IF.witness
    this.logToWitness({
      event: 'webrtc_quality_degraded',
      agent_id: this.getAgentId(),
      peer_id: peerId,
      trace_id: this.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        quality: metrics.quality,
        rtt: metrics.rtt,
        jitter: metrics.jitter,
        packetLoss: metrics.packetLossPercent,
        avgRtt: metrics.avgRtt,
        bandwidth: metrics.bandwidth
      }
    });

    // Trigger adaptive bandwidth adjustment
    this.bandwidthAdapter?.adjustQualityMode(peerId, metrics.quality);
  }

  private handleQualityRestored(peerId: string, metrics: ConnectionQualityMetrics): void {
    // Log to IF.witness
    this.logToWitness({
      event: 'webrtc_quality_restored',
      agent_id: this.getAgentId(),
      peer_id: peerId,
      trace_id: this.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        quality: metrics.quality,
        rtt: metrics.rtt,
        bandwidth: metrics.bandwidth
      }
    });
  }

  // Cleanup monitoring when disconnecting
  async disconnectPeer(peerId: string): Promise<void> {
    const monitor = this.qualityMonitors.get(peerId);
    if (monitor) {
      monitor.stop();
      this.qualityMonitors.delete(peerId);
    }

    await super.disconnectPeer(peerId);
  }
}
```

## Configuration Options

### Default Configuration

```typescript
{
  pollIntervalMs: 2000,           // Poll interval in milliseconds
  rollingAverageWindow: 10,       // Number of samples for rolling average
  thresholds: {
    rttMs: 150,                   // RTT degradation threshold (ms)
    jitterMs: 30,                 // Jitter degradation threshold (ms)
    packetLossPercent: 5          // Packet loss degradation threshold (%)
  }
}
```

### Custom Configuration Example

```typescript
const monitor = new WebRTCQualityMonitor(peerConnection, peerId, {
  pollIntervalMs: 1000,           // Poll more frequently
  rollingAverageWindow: 20,       // Longer averaging window
  thresholds: {
    rttMs: 200,                   // More lenient RTT threshold
    jitterMs: 40,
    packetLossPercent: 10
  }
});
```

## Metrics Provided

### ConnectionQualityMetrics

- **rtt**: Round-trip time in milliseconds
- **jitter**: Packet delay variation in milliseconds
- **packetLossPercent**: Packet loss as percentage (0-100)
- **bytesSent**: Total bytes sent
- **bytesReceived**: Total bytes received
- **bandwidth**: Upload/download bandwidth in bytes/sec
- **quality**: Rating (excellent/good/fair/poor)
- **avgRtt**: Rolling average RTT
- **avgJitter**: Rolling average jitter
- **avgPacketLossPercent**: Rolling average packet loss
- **state**: RTCPeerConnection state
- **iceConnectionState**: ICE connection state
- **candidateType**: ICE candidate type (host/srflx/relay/prflx)

## Quality Ratings

Quality ratings are calculated based on metrics:

| Rating | RTT | Jitter | Packet Loss |
|--------|-----|--------|-------------|
| Excellent | <50ms | <10ms | <1% |
| Good | <100ms | <20ms | <3% |
| Fair | <150ms | <30ms | <5% |
| Poor | >150ms | >30ms | >5% |

## Best Practices

1. **Create monitor after connection**: Create the quality monitor after the RTCPeerConnection is established
2. **Clean up on disconnect**: Always call `stop()` and remove the monitor when disconnecting
3. **Adjust thresholds for your use case**: Different applications may need different thresholds
4. **Use rolling averages**: The monitor provides rolling averages to smooth out transient spikes
5. **Log to witness**: Integrate with IF.witness for comprehensive observability
6. **Trigger adaptive responses**: Use quality events to trigger bandwidth adaptation or fallback mechanisms

## Performance Considerations

- **Lightweight**: Minimal CPU/memory overhead (polling interval: 2s)
- **Efficient parsing**: Only iterates through relevant RTCStats reports
- **Memory bounded**: Rolling averages use fixed-size window (default: 10 samples)
- **Async collection**: Non-blocking async/await pattern for stats collection
- **Error tolerant**: Silently handles stats collection errors during connection closure
