/**
 * WebRTC Connection Quality Monitoring
 *
 * Real-time quality monitoring for WebRTC peer-to-peer connections.
 * Tracks latency, jitter, packet loss, and bandwidth utilization.
 *
 * Features:
 * - Real-time metrics collection from RTCPeerConnection.getStats()
 * - Rolling averages (last 10 samples, 20-second window)
 * - Quality degradation detection and alerts
 * - Comprehensive metrics snapshot in event payloads
 * - Lightweight, minimal overhead implementation
 *
 * Quality Thresholds:
 * - RTT: Excellent <50ms, Good <100ms, Fair <150ms, Poor >150ms
 * - Jitter: Excellent <10ms, Good <20ms, Fair <30ms, Poor >30ms
 * - Packet Loss: Excellent <1%, Good <3%, Fair <5%, Poor >5%
 *
 * Example Usage:
 * ```typescript
 * const monitor = new WebRTCQualityMonitor(peerConnection, 'peer-123');
 * monitor.on('quality_degraded', (metrics) => {
 *   console.log(`Connection quality degraded: RTT=${metrics.rtt}ms`);
 * });
 * monitor.on('quality_restored', (metrics) => {
 *   console.log(`Connection quality restored`);
 * });
 * monitor.start();
 * const metrics = monitor.getCurrentMetrics();
 * ```
 */

import { EventEmitter } from 'events';

/**
 * Quality rating based on aggregated metrics
 */
export type QualityRating = 'excellent' | 'good' | 'fair' | 'poor';

/**
 * RTCPeerConnection state type
 */
export type RTCPeerConnectionState = 'new' | 'connecting' | 'connected' | 'disconnected' | 'failed' | 'closed';

/**
 * Bandwidth metrics (bytes per second)
 */
export interface BandwidthMetrics {
  upload: number;  // bytes/sec
  download: number; // bytes/sec
}

/**
 * Connection quality metrics for a peer
 *
 * All timing metrics are in milliseconds unless otherwise specified
 */
export interface ConnectionQualityMetrics {
  /** Peer identifier */
  peerId: string;

  /** Unix timestamp of metric collection (milliseconds) */
  timestamp: number;

  /** Round-trip time (RTT) in milliseconds */
  rtt: number;

  /** Packet delay variation (jitter) in milliseconds */
  jitter: number;

  /** Packet loss percentage (0-100) */
  packetLossPercent: number;

  /** Total bytes sent over the connection */
  bytesSent: number;

  /** Total bytes received over the connection */
  bytesReceived: number;

  /** Bandwidth utilization (calculated from bytes delta) */
  bandwidth: BandwidthMetrics;

  /** RTCPeerConnection state */
  state: RTCPeerConnectionState;

  /** Quality rating (excellent/good/fair/poor) */
  quality: QualityRating;

  /** Rolling average RTT (last 10 samples) */
  avgRtt: number;

  /** Rolling average jitter (last 10 samples) */
  avgJitter: number;

  /** Rolling average packet loss (last 10 samples) */
  avgPacketLossPercent: number;

  /** Total packets lost since connection start */
  totalPacketsLost: number;

  /** ICE connection state */
  iceConnectionState: string;

  /** ICE candidate type (host/srflx/relay/prflx) */
  candidateType?: string;
}

/**
 * Configuration for quality monitoring
 */
export interface QualityMonitorConfig {
  /** Polling interval in milliseconds (default: 2000) */
  pollIntervalMs?: number;

  /** Number of samples for rolling average calculation (default: 10) */
  rollingAverageWindow?: number;

  /** Quality degradation thresholds */
  thresholds?: {
    rttMs?: number;           // RTT threshold (default: 150ms)
    jitterMs?: number;        // Jitter threshold (default: 30ms)
    packetLossPercent?: number; // Packet loss threshold (default: 5%)
  };
}

/**
 * Default quality monitor configuration
 */
const DEFAULT_CONFIG: Required<QualityMonitorConfig> = {
  pollIntervalMs: 2000,
  rollingAverageWindow: 10,
  thresholds: {
    rttMs: 150,
    jitterMs: 30,
    packetLossPercent: 5
  }
};

/**
 * Sample for rolling average calculation
 */
interface MetricsSample {
  rtt: number;
  jitter: number;
  packetLossPercent: number;
  timestamp: number;
}

/**
 * WebRTC Connection Quality Monitor
 *
 * Monitors RTCPeerConnection statistics and emits quality events.
 * Provides real-time metrics with rolling averages and degradation detection.
 */
export class WebRTCQualityMonitor extends EventEmitter {
  private peerId: string;
  private peerConnection: RTCPeerConnection;
  private config: Required<QualityMonitorConfig>;

  // Metrics tracking
  private currentMetrics?: ConnectionQualityMetrics;
  private metricsHistory: MetricsSample[] = [];
  private previousStats?: {
    bytesSent: number;
    bytesReceived: number;
    lastTimestamp: number;
  };

  // Monitoring control
  private monitoringInterval?: NodeJS.Timeout;
  private isMonitoring: boolean = false;

  // Quality state tracking (for degradation/restoration events)
  private isQualityDegraded: boolean = false;

  /**
   * Create a new WebRTC quality monitor
   * @param peerConnection The RTCPeerConnection to monitor
   * @param peerId Peer identifier for metrics labeling
   * @param config Optional configuration overrides
   */
  constructor(
    peerConnection: RTCPeerConnection,
    peerId: string,
    config: QualityMonitorConfig = {}
  ) {
    super();
    this.peerConnection = peerConnection;
    this.peerId = peerId;
    // Deep merge config with defaults to ensure all required fields
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
      thresholds: {
        ...DEFAULT_CONFIG.thresholds,
        ...(config.thresholds || {})
      }
    };
  }

  /**
   * Start monitoring connection quality
   * Begins polling RTCPeerConnection.getStats() at configured interval
   */
  start(): void {
    if (this.isMonitoring) {
      return; // Already monitoring
    }

    this.isMonitoring = true;

    // Initial metrics collection
    this.collectMetrics();

    // Start polling
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
    }, this.config.pollIntervalMs);
  }

  /**
   * Stop monitoring connection quality
   * Clears polling interval and stops metric collection
   */
  stop(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
    this.isMonitoring = false;
  }

  /**
   * Get current connection quality metrics
   * @returns Current metrics snapshot or undefined if not yet collected
   */
  getCurrentMetrics(): ConnectionQualityMetrics | undefined {
    return this.currentMetrics;
  }

  /**
   * Register event listener for quality events
   * @param event Event type: 'quality_degraded' or 'quality_restored'
   * @param callback Function to call when event occurs
   */
  on(
    event: 'quality_degraded' | 'quality_restored',
    callback: (metrics: ConnectionQualityMetrics) => void
  ): this {
    return super.on(event, callback);
  }

  /**
   * Emit quality degradation event
   * @internal
   */
  private onQualityDegraded(metrics: ConnectionQualityMetrics): void {
    this.isQualityDegraded = true;
    this.emit('quality_degraded', metrics);
  }

  /**
   * Emit quality restoration event
   * @internal
   */
  private onQualityRestored(metrics: ConnectionQualityMetrics): void {
    this.isQualityDegraded = false;
    this.emit('quality_restored', metrics);
  }

  /**
   * Collect and process metrics from RTCPeerConnection
   * @internal
   */
  private async collectMetrics(): Promise<void> {
    try {
      const stats = await this.peerConnection.getStats();
      const metrics = this.parseStats(stats);

      if (metrics) {
        // Update metrics history
        this.updateMetricsHistory(metrics);

        // Store current metrics
        this.currentMetrics = metrics;

        // Detect quality changes
        this.detectQualityChange(metrics);
      }
    } catch (error) {
      // Silently ignore errors (connection may be closing)
    }
  }

  /**
   * Parse RTCStatsReport and extract relevant metrics
   * @internal
   */
  private parseStats(stats: RTCStatsReport): ConnectionQualityMetrics | undefined {
    let bytesSent = 0;
    let bytesReceived = 0;
    let rtt = 0;
    let jitter = 0;
    let packetsLost = 0;
    let packetsReceived = 0;
    let candidateType: string | undefined;
    let iceConnectionState = 'unknown';

    // Iterate through stats reports
    stats.forEach((report: any) => {
      // Collect bytes sent/received
      if (report.type === 'outbound-rtp' && report.mediaType === 'application') {
        bytesSent += report.bytesSent || 0;
      }

      if (report.type === 'inbound-rtp' && report.mediaType === 'application') {
        bytesReceived += report.bytesReceived || 0;
        packetsLost += report.packetsLost || 0;
        packetsReceived += report.packetsReceived || 0;
        // Jitter is in seconds, convert to milliseconds
        if (report.jitter !== undefined) {
          jitter = Math.max(jitter, report.jitter * 1000);
        }
      }

      // Collect RTT from candidate pair
      if (report.type === 'candidate-pair' && report.state === 'succeeded') {
        if (report.currentRoundTripTime !== undefined) {
          // RTT is in seconds, convert to milliseconds
          rtt = Math.max(rtt, report.currentRoundTripTime * 1000);
        }
      }

      // Collect candidate type
      if (report.type === 'local-candidate' && report.candidateType) {
        candidateType = report.candidateType;
      }

      // Collect ICE connection state
      if (report.type === 'transport') {
        iceConnectionState = report.state || 'unknown';
      }
    });

    // Calculate packet loss percentage
    const totalPackets = packetsLost + packetsReceived;
    const packetLossPercent = totalPackets > 0
      ? (packetsLost / totalPackets) * 100
      : 0;

    // Calculate bandwidth from bytes delta
    const bandwidth = this.calculateBandwidth(bytesSent, bytesReceived);

    // Determine quality rating
    const quality = this.rateQuality(rtt, jitter, packetLossPercent);

    // Build metrics object
    const metrics: ConnectionQualityMetrics = {
      peerId: this.peerId,
      timestamp: Date.now(),
      rtt: Math.round(rtt * 100) / 100, // Round to 2 decimals
      jitter: Math.round(jitter * 100) / 100,
      packetLossPercent: Math.round(packetLossPercent * 100) / 100,
      bytesSent,
      bytesReceived,
      bandwidth,
      state: this.peerConnection.connectionState as RTCPeerConnectionState,
      quality,
      avgRtt: this.getAverageRtt(),
      avgJitter: this.getAverageJitter(),
      avgPacketLossPercent: this.getAveragePacketLoss(),
      totalPacketsLost: packetsLost,
      iceConnectionState,
      candidateType
    };

    return metrics;
  }

  /**
   * Update metrics history for rolling averages
   * @internal
   */
  private updateMetricsHistory(metrics: ConnectionQualityMetrics): void {
    this.metricsHistory.push({
      rtt: metrics.rtt,
      jitter: metrics.jitter,
      packetLossPercent: metrics.packetLossPercent,
      timestamp: metrics.timestamp
    });

    // Keep only the last N samples
    if (this.metricsHistory.length > this.config.rollingAverageWindow) {
      this.metricsHistory.shift();
    }
  }

  /**
   * Calculate bandwidth from bytes delta
   * @internal
   */
  private calculateBandwidth(bytesSent: number, bytesReceived: number): BandwidthMetrics {
    const bandwidth: BandwidthMetrics = {
      upload: 0,
      download: 0
    };

    if (this.previousStats) {
      const timeDeltaSeconds = (Date.now() - this.previousStats.lastTimestamp) / 1000;

      if (timeDeltaSeconds > 0) {
        const sentDelta = bytesSent - this.previousStats.bytesSent;
        const receivedDelta = bytesReceived - this.previousStats.bytesReceived;

        bandwidth.upload = Math.max(0, Math.round(sentDelta / timeDeltaSeconds));
        bandwidth.download = Math.max(0, Math.round(receivedDelta / timeDeltaSeconds));
      }
    }

    // Store current values for next calculation
    this.previousStats = {
      bytesSent,
      bytesReceived,
      lastTimestamp: Date.now()
    };

    return bandwidth;
  }

  /**
   * Get average RTT from recent samples
   * @internal
   */
  private getAverageRtt(): number {
    if (this.metricsHistory.length === 0) {
      return 0;
    }

    const sum = this.metricsHistory.reduce((acc, sample) => acc + sample.rtt, 0);
    return Math.round((sum / this.metricsHistory.length) * 100) / 100;
  }

  /**
   * Get average jitter from recent samples
   * @internal
   */
  private getAverageJitter(): number {
    if (this.metricsHistory.length === 0) {
      return 0;
    }

    const sum = this.metricsHistory.reduce((acc, sample) => acc + sample.jitter, 0);
    return Math.round((sum / this.metricsHistory.length) * 100) / 100;
  }

  /**
   * Get average packet loss from recent samples
   * @internal
   */
  private getAveragePacketLoss(): number {
    if (this.metricsHistory.length === 0) {
      return 0;
    }

    const sum = this.metricsHistory.reduce((acc, sample) => acc + sample.packetLossPercent, 0);
    return Math.round((sum / this.metricsHistory.length) * 100) / 100;
  }

  /**
   * Rate connection quality based on metrics
   * @internal
   */
  private rateQuality(rtt: number, jitter: number, packetLoss: number): QualityRating {
    // Poor quality if any metric is bad
    if (
      rtt > 150 ||
      jitter > 30 ||
      packetLoss > 5
    ) {
      return 'poor';
    }

    // Fair quality if any metric is fair
    if (
      rtt > 100 ||
      jitter > 20 ||
      packetLoss > 3
    ) {
      return 'fair';
    }

    // Good quality if any metric is good
    if (
      rtt > 50 ||
      jitter > 10 ||
      packetLoss > 1
    ) {
      return 'good';
    }

    // Excellent otherwise
    return 'excellent';
  }

  /**
   * Detect quality changes and emit events
   * @internal
   */
  private detectQualityChange(metrics: ConnectionQualityMetrics): void {
    const { thresholds } = this.config;
    const isDegraded =
      metrics.rtt > thresholds.rttMs! ||
      metrics.jitter > thresholds.jitterMs! ||
      metrics.packetLossPercent > thresholds.packetLossPercent!;

    // Transition from good to degraded
    if (isDegraded && !this.isQualityDegraded) {
      this.onQualityDegraded(metrics);
    }

    // Transition from degraded to good
    if (!isDegraded && this.isQualityDegraded) {
      this.onQualityRestored(metrics);
    }
  }
}

/**
 * Helper function to integrate quality monitor with RTCPeerConnection
 *
 * Example:
 * ```typescript
 * const monitor = createQualityMonitor(peerConnection, 'peer-123', {
 *   pollIntervalMs: 1000,
 *   thresholds: { rttMs: 200, jitterMs: 40, packetLossPercent: 10 }
 * });
 * monitor.start();
 * ```
 */
export function createQualityMonitor(
  peerConnection: RTCPeerConnection,
  peerId: string,
  config?: QualityMonitorConfig
): WebRTCQualityMonitor {
  return new WebRTCQualityMonitor(peerConnection, peerId, config);
}
