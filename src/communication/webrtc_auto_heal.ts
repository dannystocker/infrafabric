/**
 * WebRTC Auto-Healing for IF.swarm
 *
 * Philosophy Grounding:
 * - Wu Lun (五倫) Relationship: 兄弟 (Siblings) — Peers reconnect autonomously to maintain mesh integrity
 * - Indra's Net: Self-healing mesh ensures continuous reflection between all nodes
 * - IF.ground: All reconnection attempts logged to IF.witness for observability
 * - IF.TTT: Traceable, Transparent, Trustworthy reconnection strategy
 *
 * Purpose:
 * - Autonomous mesh healing with auto-reconnect on peer disconnection
 * - Exponential backoff strategy to prevent network storms
 * - Progressive TURN fallback after repeated P2P failures
 * - Full IF.witness logging for debugging and monitoring
 *
 * Usage:
 * ```typescript
 * import { WebRTCAutoHealer } from './webrtc_auto_heal';
 *
 * const healer = new WebRTCAutoHealer({
 *   agentId: 'agent-finance',
 *   signalingServerUrl: 'ws://localhost:8443',
 *   turnServers: [{
 *     urls: 'turn:turn.example.com:3478',
 *     username: 'user',
 *     credential: 'pass'
 *   }],
 *   autoHealConfig: {
 *     maxRetries: 10,
 *     backoffMultiplier: 2,
 *     maxBackoffMs: 60000,
 *     turnFallbackAfterAttempts: 3
 *   }
 * });
 *
 * await healer.connectToSignaling();
 * await healer.createOffer('agent-legal');
 * ```
 */

import {
  IFAgentWebRTC,
  IFWebRTCConfig,
  WitnessEvent,
  IFMessage
} from './webrtc-agent-mesh';

/**
 * Auto-heal configuration
 */
export interface AutoHealConfig {
  /** Maximum number of reconnection attempts before marking peer as permanently unreachable */
  maxRetries?: number; // Default: 10

  /** Exponential backoff multiplier */
  backoffMultiplier?: number; // Default: 2

  /** Maximum backoff delay in milliseconds */
  maxBackoffMs?: number; // Default: 60000 (60 seconds)

  /** Initial backoff delay in milliseconds */
  initialBackoffMs?: number; // Default: 1000 (1 second)

  /** Number of P2P failures before attempting TURN fallback */
  turnFallbackAfterAttempts?: number; // Default: 3

  /** Jitter percentage to avoid thundering herd (0-100) */
  jitterPercent?: number; // Default: 20

  /** Enable auto-heal (can be disabled for testing) */
  enabled?: boolean; // Default: true
}

/**
 * Reconnection state for a peer
 */
interface ReconnectionState {
  /** Peer ID */
  peerId: string;

  /** Current attempt number (0-indexed) */
  attemptNumber: number;

  /** Total number of failed attempts */
  failedAttempts: number;

  /** Timestamp when disconnection was first detected */
  disconnectedAt: string;

  /** Timestamp of last reconnection attempt */
  lastAttemptAt?: string;

  /** Current reconnection strategy: 'p2p' or 'turn' */
  strategy: 'p2p' | 'turn';

  /** Timer handle for next reconnection attempt */
  retryTimer?: NodeJS.Timeout;

  /** Whether peer is permanently unreachable */
  permanentlyUnreachable: boolean;

  /** Total downtime in milliseconds */
  totalDowntimeMs: number;
}

/**
 * Extended WebRTC configuration with auto-heal
 */
export interface WebRTCAutoHealConfig extends IFWebRTCConfig {
  autoHealConfig?: AutoHealConfig;
}

/**
 * WebRTC Auto-Healer
 *
 * Extends IFAgentWebRTC with autonomous reconnection capabilities:
 * - Detects peer disconnections via RTCPeerConnection state changes
 * - Automatically attempts reconnection with exponential backoff
 * - Progressive TURN fallback after repeated P2P failures
 * - Comprehensive IF.witness logging for observability
 * - Configurable retry limits and backoff strategy
 */
export class WebRTCAutoHealer extends IFAgentWebRTC {
  // Auto-heal configuration
  private autoHealEnabled: boolean;
  private maxRetries: number;
  private backoffMultiplier: number;
  private maxBackoffMs: number;
  private initialBackoffMs: number;
  private turnFallbackAfterAttempts: number;
  private jitterPercent: number;

  // Reconnection state tracking: peer_id -> ReconnectionState
  private reconnectionStates: Map<string, ReconnectionState> = new Map();

  // Track successfully connected peers to detect new disconnections
  private successfullyConnectedPeers: Set<string> = new Set();

  constructor(config: WebRTCAutoHealConfig) {
    super(config);

    // Initialize auto-heal configuration with defaults
    const autoHealConfig = config.autoHealConfig || {};
    this.autoHealEnabled = autoHealConfig.enabled !== false; // Default: true
    this.maxRetries = autoHealConfig.maxRetries ?? 10;
    this.backoffMultiplier = autoHealConfig.backoffMultiplier ?? 2;
    this.maxBackoffMs = autoHealConfig.maxBackoffMs ?? 60000; // 60 seconds
    this.initialBackoffMs = autoHealConfig.initialBackoffMs ?? 1000; // 1 second
    this.turnFallbackAfterAttempts = autoHealConfig.turnFallbackAfterAttempts ?? 3;
    this.jitterPercent = autoHealConfig.jitterPercent ?? 20;
  }

  /**
   * Create offer with auto-heal monitoring
   * Overrides parent method to attach reconnection handlers
   */
  async createOffer(peerId: string): Promise<RTCSessionDescriptionInit> {
    const offer = await super.createOffer(peerId);

    // Attach auto-heal monitoring to the peer connection
    if (this.autoHealEnabled) {
      this.attachAutoHealHandlers(peerId);
    }

    return offer;
  }

  /**
   * Handle incoming offer with auto-heal monitoring
   * Overrides parent method to attach reconnection handlers
   */
  async handleOffer(
    peerId: string,
    offer: RTCSessionDescriptionInit
  ): Promise<RTCSessionDescriptionInit> {
    const answer = await super.handleOffer(peerId, offer);

    // Attach auto-heal monitoring to the peer connection
    if (this.autoHealEnabled) {
      this.attachAutoHealHandlers(peerId);
    }

    return answer;
  }

  /**
   * Attach auto-heal handlers to peer connection
   *
   * Monitors connection state changes and triggers reconnection on:
   * - connectionState === 'disconnected'
   * - connectionState === 'failed'
   * - iceConnectionState === 'disconnected'
   * - iceConnectionState === 'failed'
   */
  private attachAutoHealHandlers(peerId: string): void {
    const pc = this.getPeerConnection(peerId);
    if (!pc) {
      console.warn(`[WebRTCAutoHealer] No peer connection found for ${peerId}`);
      return;
    }

    // Store original handlers (if any)
    const originalConnectionStateHandler = pc.onconnectionstatechange;
    const originalIceConnectionStateHandler = (pc as any).oniceconnectionstatechange;

    // Override connection state change handler
    pc.onconnectionstatechange = async () => {
      // Call original handler first
      if (originalConnectionStateHandler) {
        originalConnectionStateHandler.call(pc, new Event('connectionstatechange'));
      }

      const state = pc.connectionState;

      // Track successful connections
      if (state === 'connected') {
        this.handleSuccessfulConnection(peerId);
      }

      // Trigger auto-heal on disconnection or failure
      if (state === 'disconnected' || state === 'failed') {
        await this.handlePeerDisconnection(peerId, state, 'connectionState');
      }
    };

    // Override ICE connection state change handler
    (pc as any).oniceconnectionstatechange = async () => {
      // Call original handler first
      if (originalIceConnectionStateHandler) {
        originalIceConnectionStateHandler.call(pc, new Event('iceconnectionstatechange'));
      }

      const iceState = (pc as any).iceConnectionState;

      // Trigger auto-heal on ICE disconnection or failure
      if (iceState === 'disconnected' || iceState === 'failed') {
        await this.handlePeerDisconnection(peerId, iceState, 'iceConnectionState');
      }
    };
  }

  /**
   * Handle successful peer connection
   * Clears reconnection state and logs success
   */
  private async handleSuccessfulConnection(peerId: string): Promise<void> {
    this.successfullyConnectedPeers.add(peerId);

    // Check if this was a reconnection
    const reconnectionState = this.reconnectionStates.get(peerId);
    if (reconnectionState && !reconnectionState.permanentlyUnreachable) {
      const totalDowntime = Date.now() - new Date(reconnectionState.disconnectedAt).getTime();
      const totalAttempts = reconnectionState.attemptNumber + 1;

      // Log successful reconnection to IF.witness
      await this.logToWitness({
        event: 'peer_reconnected_successfully',
        agent_id: this.getAgentId(),
        peer_id: peerId,
        trace_id: this.getCurrentTraceId(),
        timestamp: new Date().toISOString(),
        metadata: {
          total_attempts: totalAttempts,
          total_downtime_ms: totalDowntime,
          strategy: reconnectionState.strategy,
          failed_attempts: reconnectionState.failedAttempts
        }
      });

      // Clear reconnection state
      this.clearReconnectionState(peerId);
    }
  }

  /**
   * Handle peer disconnection
   * Initiates auto-heal reconnection process
   */
  private async handlePeerDisconnection(
    peerId: string,
    state: string,
    stateType: 'connectionState' | 'iceConnectionState'
  ): Promise<void> {
    // Only auto-heal if peer was successfully connected before
    if (!this.successfullyConnectedPeers.has(peerId)) {
      return;
    }

    // Get or create reconnection state
    let reconnectionState = this.reconnectionStates.get(peerId);

    if (!reconnectionState) {
      // First disconnection - initialize state
      reconnectionState = {
        peerId,
        attemptNumber: 0,
        failedAttempts: 0,
        disconnectedAt: new Date().toISOString(),
        strategy: 'p2p',
        permanentlyUnreachable: false,
        totalDowntimeMs: 0
      };
      this.reconnectionStates.set(peerId, reconnectionState);

      // Log disconnection event
      await this.logToWitness({
        event: 'peer_disconnected_auto_heal',
        agent_id: this.getAgentId(),
        peer_id: peerId,
        trace_id: this.getCurrentTraceId(),
        timestamp: new Date().toISOString(),
        metadata: {
          state,
          state_type: stateType,
          auto_heal_enabled: this.autoHealEnabled
        }
      });
    }

    // Check if peer is already marked as permanently unreachable
    if (reconnectionState.permanentlyUnreachable) {
      return;
    }

    // Clear existing retry timer if any
    if (reconnectionState.retryTimer) {
      clearTimeout(reconnectionState.retryTimer);
    }

    // Schedule reconnection attempt
    await this.scheduleReconnectionAttempt(peerId);
  }

  /**
   * Schedule next reconnection attempt with exponential backoff
   */
  private async scheduleReconnectionAttempt(peerId: string): Promise<void> {
    const reconnectionState = this.reconnectionStates.get(peerId);
    if (!reconnectionState || reconnectionState.permanentlyUnreachable) {
      return;
    }

    // Check if max retries exceeded
    if (reconnectionState.attemptNumber >= this.maxRetries) {
      await this.markPeerPermanentlyUnreachable(peerId);
      return;
    }

    // Calculate exponential backoff delay
    const baseDelay = this.initialBackoffMs * Math.pow(
      this.backoffMultiplier,
      reconnectionState.attemptNumber
    );

    // Cap at max backoff
    const cappedDelay = Math.min(baseDelay, this.maxBackoffMs);

    // Add jitter to avoid thundering herd
    // Jitter: ±jitterPercent% randomization
    const jitterRange = (cappedDelay * this.jitterPercent) / 100;
    const jitter = (Math.random() * 2 - 1) * jitterRange; // Random value in [-jitterRange, +jitterRange]
    const delayWithJitter = Math.max(0, cappedDelay + jitter);

    // Determine strategy: P2P or TURN
    const strategy =
      reconnectionState.attemptNumber >= this.turnFallbackAfterAttempts
        ? 'turn'
        : 'p2p';

    reconnectionState.strategy = strategy;

    // Log scheduled reconnection attempt
    await this.logToWitness({
      event: 'reconnection_attempt_scheduled',
      agent_id: this.getAgentId(),
      peer_id: peerId,
      trace_id: this.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        attempt_number: reconnectionState.attemptNumber + 1,
        backoff_delay_ms: Math.round(delayWithJitter),
        strategy,
        failed_attempts: reconnectionState.failedAttempts
      }
    });

    // Schedule reconnection
    reconnectionState.retryTimer = setTimeout(async () => {
      await this.attemptReconnection(peerId);
    }, delayWithJitter);
  }

  /**
   * Attempt reconnection to peer
   */
  private async attemptReconnection(peerId: string): Promise<void> {
    const reconnectionState = this.reconnectionStates.get(peerId);
    if (!reconnectionState || reconnectionState.permanentlyUnreachable) {
      return;
    }

    const attemptStartTime = Date.now();
    reconnectionState.attemptNumber += 1;
    reconnectionState.lastAttemptAt = new Date().toISOString();

    // Log reconnection attempt
    await this.logToWitness({
      event: 'reconnection_attempt_started',
      agent_id: this.getAgentId(),
      peer_id: peerId,
      trace_id: this.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        attempt_number: reconnectionState.attemptNumber,
        strategy: reconnectionState.strategy,
        total_failed_attempts: reconnectionState.failedAttempts
      }
    });

    try {
      // Disconnect existing (failed) connection
      await this.disconnectPeer(peerId);

      // Wait briefly for cleanup
      await this.delay(100);

      // For TURN strategy, force TURN usage by setting internal flag
      if (reconnectionState.strategy === 'turn') {
        // Access private method via type assertion
        (this as any).usingTurn.set(peerId, true);

        await this.logToWitness({
          event: 'reconnection_using_turn',
          agent_id: this.getAgentId(),
          peer_id: peerId,
          trace_id: this.getCurrentTraceId(),
          timestamp: new Date().toISOString(),
          metadata: {
            attempt_number: reconnectionState.attemptNumber,
            reason: 'P2P reconnection attempts exceeded threshold'
          }
        });
      }

      // Create new offer to re-establish connection
      await this.createOffer(peerId);

      // Wait for connection to establish (with timeout)
      const connectionTimeout = 10000; // 10 seconds
      const connectionEstablished = await this.waitForConnectionEstablishment(
        peerId,
        connectionTimeout
      );

      if (connectionEstablished) {
        // Success is handled by handleSuccessfulConnection
        // which is triggered by onconnectionstatechange
      } else {
        // Connection timeout
        throw new Error(`Connection establishment timeout after ${connectionTimeout}ms`);
      }
    } catch (error) {
      // Reconnection attempt failed
      reconnectionState.failedAttempts += 1;

      const attemptDuration = Date.now() - attemptStartTime;

      await this.logToWitness({
        event: 'reconnection_attempt_failed',
        agent_id: this.getAgentId(),
        peer_id: peerId,
        trace_id: this.getCurrentTraceId(),
        timestamp: new Date().toISOString(),
        metadata: {
          attempt_number: reconnectionState.attemptNumber,
          strategy: reconnectionState.strategy,
          error: String(error),
          attempt_duration_ms: attemptDuration,
          total_failed_attempts: reconnectionState.failedAttempts
        }
      });

      // Schedule next attempt
      await this.scheduleReconnectionAttempt(peerId);
    }
  }

  /**
   * Wait for connection establishment
   * Returns true if connected, false if timeout
   */
  private async waitForConnectionEstablishment(
    peerId: string,
    timeoutMs: number
  ): Promise<boolean> {
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      const pc = this.getPeerConnection(peerId);
      if (!pc) {
        // Connection was closed
        return false;
      }

      if (pc.connectionState === 'connected') {
        return true;
      }

      // Connection failed or closed
      if (pc.connectionState === 'failed' || pc.connectionState === 'closed') {
        return false;
      }

      // Wait 100ms before checking again
      await this.delay(100);
    }

    return false; // Timeout
  }

  /**
   * Mark peer as permanently unreachable
   */
  private async markPeerPermanentlyUnreachable(peerId: string): Promise<void> {
    const reconnectionState = this.reconnectionStates.get(peerId);
    if (!reconnectionState) {
      return;
    }

    reconnectionState.permanentlyUnreachable = true;

    const totalDowntime = Date.now() - new Date(reconnectionState.disconnectedAt).getTime();

    // Log permanent failure to IF.witness
    await this.logToWitness({
      event: 'peer_permanently_unreachable',
      agent_id: this.getAgentId(),
      peer_id: peerId,
      trace_id: this.getCurrentTraceId(),
      timestamp: new Date().toISOString(),
      metadata: {
        total_attempts: reconnectionState.attemptNumber,
        total_failed_attempts: reconnectionState.failedAttempts,
        total_downtime_ms: totalDowntime,
        max_retries: this.maxRetries,
        last_strategy: reconnectionState.strategy
      }
    });

    // Clean up peer connection
    await this.disconnectPeer(peerId);

    // Remove from successfully connected peers
    this.successfullyConnectedPeers.delete(peerId);
  }

  /**
   * Clear reconnection state for peer
   */
  private clearReconnectionState(peerId: string): void {
    const reconnectionState = this.reconnectionStates.get(peerId);
    if (reconnectionState?.retryTimer) {
      clearTimeout(reconnectionState.retryTimer);
    }
    this.reconnectionStates.delete(peerId);
  }

  /**
   * Get reconnection state for peer (for monitoring/debugging)
   */
  getReconnectionState(peerId: string): Readonly<ReconnectionState> | undefined {
    const state = this.reconnectionStates.get(peerId);
    return state ? { ...state } : undefined;
  }

  /**
   * Get all reconnection states (for monitoring/debugging)
   */
  getAllReconnectionStates(): Map<string, Readonly<ReconnectionState>> {
    const states = new Map<string, Readonly<ReconnectionState>>();
    for (const [peerId, state] of this.reconnectionStates) {
      states.set(peerId, { ...state });
    }
    return states;
  }

  /**
   * Manually trigger reconnection attempt for peer
   * Useful for testing or manual intervention
   */
  async manualReconnect(peerId: string): Promise<void> {
    // Clear existing reconnection state
    this.clearReconnectionState(peerId);

    // Initialize new reconnection state
    const reconnectionState: ReconnectionState = {
      peerId,
      attemptNumber: 0,
      failedAttempts: 0,
      disconnectedAt: new Date().toISOString(),
      strategy: 'p2p',
      permanentlyUnreachable: false,
      totalDowntimeMs: 0
    };
    this.reconnectionStates.set(peerId, reconnectionState);

    await this.logToWitness({
      event: 'manual_reconnection_triggered',
      agent_id: this.getAgentId(),
      peer_id: peerId,
      trace_id: this.getCurrentTraceId(),
      timestamp: new Date().toISOString()
    });

    // Attempt reconnection immediately
    await this.attemptReconnection(peerId);
  }

  /**
   * Reset peer to allow reconnection (clears permanent failure state)
   */
  resetPeer(peerId: string): void {
    this.clearReconnectionState(peerId);
    this.successfullyConnectedPeers.delete(peerId);
  }

  /**
   * Get auto-heal configuration
   */
  getAutoHealConfig(): {
    enabled: boolean;
    maxRetries: number;
    backoffMultiplier: number;
    maxBackoffMs: number;
    initialBackoffMs: number;
    turnFallbackAfterAttempts: number;
    jitterPercent: number;
  } {
    return {
      enabled: this.autoHealEnabled,
      maxRetries: this.maxRetries,
      backoffMultiplier: this.backoffMultiplier,
      maxBackoffMs: this.maxBackoffMs,
      initialBackoffMs: this.initialBackoffMs,
      turnFallbackAfterAttempts: this.turnFallbackAfterAttempts,
      jitterPercent: this.jitterPercent
    };
  }

  /**
   * Override disconnect to clean up all reconnection timers
   */
  async disconnect(): Promise<void> {
    // Clear all reconnection timers
    for (const [peerId, state] of this.reconnectionStates) {
      if (state.retryTimer) {
        clearTimeout(state.retryTimer);
      }
    }
    this.reconnectionStates.clear();
    this.successfullyConnectedPeers.clear();

    // Call parent disconnect
    await super.disconnect();
  }

  // ============ Private Helper Methods ============

  /**
   * Delay helper (promisified setTimeout)
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * Example Usage
 *
 * ```typescript
 * import { WebRTCAutoHealer } from './webrtc_auto_heal';
 *
 * // Initialize with auto-heal enabled
 * const healer = new WebRTCAutoHealer({
 *   agentId: 'agent-finance',
 *   signalingServerUrl: 'ws://localhost:8443',
 *   stunServers: ['stun:stun.l.google.com:19302'],
 *   turnServers: [{
 *     urls: 'turn:turn.example.com:3478',
 *     username: 'user',
 *     credential: 'pass'
 *   }],
 *   witnessLogger: async (event) => {
 *     console.log('[IF.witness]', event);
 *     // Send to your witness logging system
 *   },
 *   autoHealConfig: {
 *     maxRetries: 10,
 *     backoffMultiplier: 2,
 *     maxBackoffMs: 60000,
 *     initialBackoffMs: 1000,
 *     turnFallbackAfterAttempts: 3,
 *     jitterPercent: 20,
 *     enabled: true
 *   }
 * });
 *
 * // Connect to signaling server
 * await healer.connectToSignaling();
 *
 * // Create peer connections (auto-heal is automatic)
 * await healer.createOffer('agent-legal');
 * await healer.createOffer('agent-macro');
 *
 * // Monitor reconnection states
 * setInterval(() => {
 *   const states = healer.getAllReconnectionStates();
 *   for (const [peerId, state] of states) {
 *     console.log(`${peerId}: attempt ${state.attemptNumber}, strategy: ${state.strategy}`);
 *   }
 * }, 5000);
 *
 * // Manual reconnection if needed
 * await healer.manualReconnect('agent-legal');
 *
 * // Get configuration
 * const config = healer.getAutoHealConfig();
 * console.log('Auto-heal config:', config);
 * ```
 */
