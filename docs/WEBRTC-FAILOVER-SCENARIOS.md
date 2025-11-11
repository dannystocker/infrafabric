# WebRTC Agent Mesh - Failover Scenarios & Decision Trees

**Version:** 1.0
**Last Updated:** November 11, 2025
**Status:** Production Ready

---

## Table of Contents

1. [Failover Classification](#failover-classification)
2. [Decision Trees](#decision-trees)
3. [Scenario Procedures](#scenario-procedures)
4. [Recovery Validation](#recovery-validation)

---

## Failover Classification

### Failover Types

| Type | Component | Scope | Recovery Time | Manual Intervention |
|------|-----------|-------|---|---|
| **A: TURN Server Failure** | Relay servers | Per-peer | 5-30s (auto), <5m (manual) | Often unnecessary |
| **B: Signaling Server Failure** | SDP/ICE relay | Global | 30s-2m (auto), <5m (manual) | May be required |
| **C: Network Partition** | Mesh connectivity | Regional | 30s-17m (exponential backoff) | Manual intervention needed |
| **D: Certificate Expiration** | DTLS/TLS | Global on restart | <1 hour | Required (automated renewal) |
| **E: SRTP Key Compromise** | Encryption keys | All peers | <1 minute | Manual incident response |

---

## Decision Trees

### Tree 1: Connection Establishment Failure

```
┌─ Connection failed (timeout > 5s)
│
├─ Check: Agent registered on signaling server?
│ ├─ NO → Agent cannot register
│ │       ├─ Diagnose: Signaling server down?
│ │       │ └─ YES → Failover: Use backup signaling server (Scenario B)
│ │       │ └─ NO  → Check network connectivity, firewall rules
│ │       └─ Resolution: Manual intervention required
│ │
│ └─ YES → Agent registered, proceed to next check
│
├─ Check: STUN server reachable?
│ ├─ NO → STUN unavailable
│ │       ├─ Diagnose: Network issue or STUN server down?
│ │       └─ Action: Switch to alternate STUN servers (Google public)
│ │
│ └─ YES → STUN reachable, proceed to next check
│
├─ Check: Direct P2P connection possible?
│ ├─ YES → Connection successful
│ │        └─ Resolution: None needed
│ │
│ └─ NO  → P2P blocked (firewall/NAT)
│          ├─ Trigger: TURN fallback timer (5 seconds)
│          ├─ Check: TURN server reachable?
│          │ ├─ YES → Use TURN relay (Scenario A)
│          │ └─ NO  → Failover to secondary TURN (Scenario A)
│          └─ If all TURN fail → Manual intervention required
│
└─ End: Connection established OR manual intervention needed
```

**Decision Tree Implementation Code:**

```typescript
async ensureConnected(peerId: string): Promise<void> {
  // Step 1: Check signaling connectivity
  const signaling = await this.checkSignalingHealth();
  if (!signaling.healthy) {
    if (signaling.canFailover) {
      await this.failoverSignaling();
    } else {
      throw new Error('Signaling unavailable and no failover');
    }
  }

  // Step 2: Check STUN reachability
  const stun = await this.checkSTUNHealth();
  if (!stun.healthy) {
    console.warn('STUN server unavailable, using secondary');
    this.useSecondarySTUN();
  }

  // Step 3: Attempt P2P connection
  try {
    const p2pSuccess = await Promise.race([
      this.establishP2PConnection(peerId),
      this.timeout(this.turnFallbackTimeout)  // 5 seconds
    ]);

    if (p2pSuccess) {
      await this.logToWitness({ event: 'p2p_connection_established', peerId });
      return;
    }
  } catch (error) {
    // P2P failed or timed out
  }

  // Step 4: TURN fallback
  const turnSuccess = await this.attemptTURNFallback(peerId);
  if (!turnSuccess) {
    throw new Error(`Cannot connect to ${peerId} (P2P and TURN failed)`);
  }

  await this.logToWitness({ event: 'turn_fallback_successful', peerId });
}
```

### Tree 2: High Latency Detection

```
┌─ Latency alert: RTT > 500ms (P2P) or > 2000ms (TURN)
│
├─ Check: P2P or TURN connection?
│ ├─ TURN  → High latency on relay
│ │         ├─ Diagnose: TURN server capacity?
│ │         │ ├─ High → Failover to secondary TURN (Scenario A)
│ │         │ └─ Low  → Network path issue
│ │         └─ Check: Are other peers also affected?
│ │             ├─ YES → Regional issue
│ │             └─ NO  → Peer-specific issue
│ │
│ └─ P2P  → High latency on direct path
│          ├─ Diagnose: Bandwidth exhaustion?
│          │ ├─ YES → Enable bandwidth adaptation
│          │ └─ NO  → Network congestion
│          └─ Option: Switch to TURN relay (may improve through different path)
│
├─ Check: Jitter also high (>100ms)?
│ ├─ YES → Network instability (not just latency)
│ │        └─ Action: Reduce message rate, enable quality adaptation
│ │
│ └─ NO  → Consistent high latency
│          └─ Action: Monitor, escalate if persistent >30m
│
└─ End: Mitigation applied OR escalation to ops team
```

### Tree 3: Packet Loss Mitigation

```
┌─ Packet loss alert: >5% of packets lost
│
├─ Check: What's the current connection type?
│ ├─ P2P → Low RTT but high loss
│ │        ├─ Cause: Network congestion on direct path
│ │        └─ Action: Reduce bitrate, enable FEC if available
│ │
│ └─ TURN → Using relay
│          ├─ Check: TURN server CPU/memory?
│          │ ├─ High → Failover to secondary TURN
│          │ └─ Low  → Network issue to/from TURN
│          └─ Action: Reduce bitrate, monitor TURN health
│
├─ Check: Packet loss direction?
│ ├─ Inbound only  → Peer sending high bitrate
│ │                 └─ Action: Reduce peer's bitrate (via adaptation)
│ │
│ ├─ Outbound only → Network congested toward destination
│ │                  └─ Action: Reduce local bitrate
│ │
│ └─ Both          → Severe congestion
│                    └─ Action: Enable maximum bitrate reduction
│
├─ Check: Is this causing message delivery failures?
│ ├─ YES → Enable aggressive error correction
│ │        └─ Action: Message retransmission, checksum validation
│ │
│ └─ NO  → Monitor but may not need action
│          └─ Action: Continue monitoring for degradation
│
└─ End: Mitigation applied OR switch connection type
```

### Tree 4: Security Event Response

```
┌─ Security alert detected
│
├─ Event type?
│ ├─ DTLS validation failure
│ │  ├─ Cause: Self-signed cert in production?
│ │  │ └─ Action: Deploy proper CA certificate (Scenario D)
│ │  ├─ Cause: Certificate expired?
│ │  │ └─ Action: Rotate certificate (Scenario D)
│ │  └─ Cause: Invalid fingerprint?
│ │      └─ Action: Investigate peer connection state
│ │
│ ├─ Signature verification failure
│ │  ├─ Single instance → Log and monitor
│ │  └─ Multiple instances → Possible MITM attack
│ │      ├─ Action: Isolate peer, investigate
│ │      └─ Escalate: Security team review
│ │
│ ├─ SRTP key compromise suspected
│ │  └─ Action: Emergency key rotation (Scenario E)
│ │      ├─ All active connections
│ │      ├─ Log with incident ID
│ │      └─ Notify security team
│ │
│ └─ Unauthorized connection attempt
│     └─ Action: Block peer, escalate to security
│
├─ Severity assessment
│ ├─ Single isolated event
│ │  └─ Action: Log, monitor, no immediate action
│ │
│ ├─ Multiple events on same peer
│ │  └─ Action: Isolate peer, investigate
│ │
│ └─ Multiple events across peers
│     └─ Action: CRITICAL - emergency incident (P1)
│
└─ End: Incident logged to IF.witness + escalation if needed
```

---

## Scenario Procedures

### Scenario A: TURN Server Failure → Automatic Retry Logic

**Automatic Detection & Failover:**

```typescript
/**
 * TURN Server Health Monitoring with Automatic Failover
 *
 * Components:
 * 1. Continuous health monitoring (every 30s)
 * 2. Automatic failover to secondary TURN
 * 3. Circuit breaker pattern (3 failures = mark unhealthy)
 * 4. Exponential backoff for retry (1s, 2s, 4s, 8s...)
 */

interface TURNServerMetrics {
  url: string;
  healthy: boolean;
  failureCount: number;
  lastFailureTime?: Date;
  avgLatency: number;
}

private turnServers: TURNServerMetrics[] = [];
private turnHealthCheckInterval?: NodeJS.Timeout;
private readonly TURN_FAILURE_THRESHOLD = 3;
private readonly TURN_HEALTH_CHECK_INTERVAL = 30000; // 30 seconds

startTURNHealthMonitoring(): void {
  this.turnHealthCheckInterval = setInterval(async () => {
    await this.checkTURNHealth();
  }, this.TURN_HEALTH_CHECK_INTERVAL);
}

private async checkTURNHealth(): Promise<void> {
  for (const turnServer of this.turnServers) {
    try {
      const startTime = Date.now();

      // Send STUN Binding Request to TURN server
      const response = await this.sendSTUNBindingRequest(turnServer.url);

      const latency = Date.now() - startTime;

      if (response.success) {
        // Recovery: reset failure count
        turnServer.failureCount = 0;
        turnServer.avgLatency = latency;
        turnServer.healthy = true;

        await this.logToWitness({
          event: 'turn_server_health_check_success',
          metadata: {
            turn_server: turnServer.url,
            latency_ms: latency
          }
        });
      } else {
        this.handleTURNFailure(turnServer);
      }
    } catch (error) {
      this.handleTURNFailure(turnServer);
    }
  }

  // Ensure at least one TURN server is healthy
  const healthyServers = this.turnServers.filter(t => t.healthy);
  if (healthyServers.length === 0) {
    await this.logToWitness({
      event: 'all_turn_servers_unhealthy',
      severity: 'critical',
      metadata: {
        timestamp: new Date().toISOString()
      }
    });
  }
}

private handleTURNFailure(turnServer: TURNServerMetrics): void {
  turnServer.failureCount++;
  turnServer.lastFailureTime = new Date();

  if (turnServer.failureCount >= this.TURN_FAILURE_THRESHOLD) {
    turnServer.healthy = false;

    this.logToWitness({
      event: 'turn_server_marked_unhealthy',
      metadata: {
        turn_server: turnServer.url,
        failure_count: turnServer.failureCount
      }
    });
  }
}

/**
 * Get healthy TURN server with lowest latency
 */
private getHealthyTURNServer(): TURNServerMetrics | undefined {
  const healthy = this.turnServers
    .filter(t => t.healthy)
    .sort((a, b) => a.avgLatency - b.avgLatency);

  return healthy[0];
}

/**
 * Attempt TURN connection with fallover retry logic
 */
async attemptTURNFallback(peerId: string): Promise<boolean> {
  let lastError: Error | undefined;
  let retryCount = 0;
  const MAX_RETRIES = 3;

  while (retryCount < MAX_RETRIES) {
    const turnServer = this.getHealthyTURNServer();
    if (!turnServer) {
      throw new Error('No healthy TURN servers available');
    }

    try {
      // Attempt connection with current TURN server
      await this.connectWithTURN(peerId, turnServer);

      // Success
      this.usingTurn.set(peerId, true);

      await this.logToWitness({
        event: 'turn_fallback_successful',
        agent_id: this.agentId,
        peer_id: peerId,
        metadata: {
          turn_server: turnServer.url,
          retries: retryCount
        }
      });

      return true;
    } catch (error) {
      lastError = error as Error;
      retryCount++;

      // Exponential backoff
      const delayMs = Math.pow(2, retryCount) * 1000;

      await this.logToWitness({
        event: 'turn_fallback_retry',
        metadata: {
          turn_server: turnServer.url,
          attempt: retryCount,
          delay_ms: delayMs,
          error: lastError.message
        }
      });

      if (retryCount < MAX_RETRIES) {
        await this.sleep(delayMs);
      }
    }
  }

  return false;
}
```

**Manual Recovery Procedure:**

```bash
#!/bin/bash
# manual-turn-recovery.sh

set -e

FAILED_TURN=$1
REPLACEMENT_TURN=$2

echo "Manual TURN Server Recovery"
echo "Failed server: $FAILED_TURN"
echo "Replacement: $REPLACEMENT_TURN"

# Step 1: Verify replacement server is healthy
echo "Step 1: Testing replacement TURN server..."
if ! timeout 5 stunclient "$REPLACEMENT_TURN" username password; then
  echo "✗ Replacement TURN server not responding"
  exit 1
fi
echo "✓ Replacement TURN server is healthy"

# Step 2: Update configuration
echo "Step 2: Updating configuration..."
sed -i "s|$FAILED_TURN|$REPLACEMENT_TURN|g" config/webrtc-production.env

# Step 3: Trigger reconfiguration (no restart needed)
echo "Step 3: Reloading configuration..."
curl -X POST \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  http://webrtc.infrafabric.local:8443/admin/reload-config \
  -H "Content-Type: application/json" \
  -d '{
    "turn_servers": ["'$REPLACEMENT_TURN'", ...]
  }'

# Step 4: Force reconnection for any peers still using failed server
echo "Step 4: Reconnecting affected peers..."
curl -X POST \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  http://webrtc.infrafabric.local:8443/admin/reconnect-turn-peers

# Step 5: Monitor for 5 minutes
echo "Step 5: Monitoring (5 minutes)..."
for i in {1..5}; do
  echo "  Minute $i/5: Checking connection health..."
  FAILED_CONNS=$(curl -s http://webrtc.infrafabric.local:8443/stats | \
    jq '.connections | map(select(.state=="failed")) | length')

  if [ "$FAILED_CONNS" -gt 0 ]; then
    echo "  ⚠ $FAILED_CONNS connections still failing"
  fi

  sleep 60
done

# Step 6: Final verification
echo "Step 6: Final verification..."
USING_TURN=$(curl -s http://witness.infrafabric.local/api/query -d "{
  \"query\": {
    \"event\": \"turn_connection_detected\",
    \"metadata.turn_server\": \"$REPLACEMENT_TURN\"
  },
  \"time_range\": {\"from\": \"-5m\", \"to\": \"now\"}
}" | jq '.results | length')

if [ "$USING_TURN" -gt 0 ]; then
  echo "✓ Peers successfully using replacement TURN server"
else
  echo "⚠ No peers using replacement TURN yet (may be using P2P)"
fi

# Step 7: Log recovery
curl -X POST http://witness.infrafabric.local/api/log \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"turn_server_failover_complete\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"metadata\": {
      \"failed_server\": \"$FAILED_TURN\",
      \"replacement_server\": \"$REPLACEMENT_TURN\",
      \"operator\": \"$(whoami)\"
    }
  }"

echo "✅ TURN server failover complete"
```

### Scenario B: Signaling Server Failure → Reconnection Strategy

**Client-Side Automatic Failover:**

```typescript
/**
 * Signaling Server Failover Configuration
 *
 * Clients maintain a list of signaling servers in priority order
 * and automatically fail over if primary becomes unavailable.
 */

export interface SignalingServerConfig {
  // Primary signaling server (should be behind load balancer)
  primaryUrl: string;

  // Failover servers in priority order
  failoverUrls: string[];

  // Failover timeout (wait before trying next server)
  failoverTimeoutMs: number;

  // Max connection attempts per server
  maxRetriesPerServer: number;
}

class IFAgentWebRTC {
  private signalingUrls: string[];
  private currentUrlIndex: number = 0;
  private connectionAttempts: number = 0;

  async connectToSignaling(): Promise<void> {
    const maxTotalAttempts = this.signalingUrls.length *
      this.maxRetriesPerServer;

    while (this.connectionAttempts < maxTotalAttempts) {
      const currentUrl = this.signalingUrls[this.currentUrlIndex];

      try {
        await this.attemptSignalingConnection(currentUrl);

        // Success - connection established
        await this.logToWitness({
          event: 'signaling_connected',
          metadata: {
            server: currentUrl,
            attempt: this.connectionAttempts,
            fallover_count: this.currentUrlIndex
          }
        });

        // Reset for future reconnects
        this.currentUrlIndex = 0;
        this.connectionAttempts = 0;

        return;
      } catch (error) {
        this.connectionAttempts++;

        await this.logToWitness({
          event: 'signaling_connection_failed',
          metadata: {
            server: currentUrl,
            attempt: this.connectionAttempts,
            error: (error as Error).message
          }
        });

        // Try next server after timeout
        if ((this.connectionAttempts % this.maxRetriesPerServer) === 0) {
          // Exhausted retries for current server, move to next
          this.currentUrlIndex =
            (this.currentUrlIndex + 1) % this.signalingUrls.length;
        }

        // Exponential backoff: 1s, 2s, 4s, 8s...
        const delayMs = Math.pow(2,
          Math.floor(this.connectionAttempts / this.maxRetriesPerServer)) *
          1000;

        await this.sleep(delayMs);
      }
    }

    throw new Error(
      `Failed to connect to signaling servers after ${maxTotalAttempts} attempts`
    );
  }

  private async attemptSignalingConnection(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(url);
      let timeoutHandle: NodeJS.Timeout | undefined;

      // Timeout if connection not established
      timeoutHandle = setTimeout(() => {
        ws.close();
        reject(new Error(`Connection timeout to ${url}`));
      }, this.failoverTimeoutMs);

      ws.onopen = () => {
        clearTimeout(timeoutHandle);
        this.signalingWs = ws;
        this.setupSignalingHandlers();
        resolve();
      };

      ws.onerror = (error) => {
        clearTimeout(timeoutHandle);
        reject(new Error(`Connection error: ${error}`));
      };
    });
  }

  /**
   * Automatic reconnection on connection loss
   */
  private setupSignalingHandlers(): void {
    if (!this.signalingWs) return;

    this.signalingWs.onclose = async () => {
      await this.logToWitness({
        event: 'signaling_connection_lost',
        agent_id: this.agentId,
        timestamp: new Date().toISOString()
      });

      // Attempt reconnection
      console.log('Signaling connection lost, reconnecting...');
      this.currentUrlIndex = 0;  // Start from primary
      this.connectionAttempts = 0;

      try {
        await this.connectToSignaling();
        console.log('Reconnected to signaling server');
      } catch (error) {
        console.error('Failed to reconnect:', error);
        throw error;
      }
    };
  }
}
```

**Server-Side Load Balancer Configuration:**

```yaml
# nginx configuration for signaling server failover
upstream webrtc_signaling {
  # Health check parameters
  keepalive 32;

  # Primary signaling servers with health checks
  server signaling1.infrafabric.local:8443
    weight=10 max_fails=3 fail_timeout=30s;
  server signaling2.infrafabric.local:8443
    weight=10 max_fails=3 fail_timeout=30s;

  # Backup signaling server (only used if all primary down)
  server signaling3.infrafabric.local:8443
    weight=5 backup max_fails=3 fail_timeout=30s;
}

server {
  listen 8443 ssl http2;
  server_name signaling.infrafabric.local;

  ssl_certificate /etc/nginx/certs/signaling.crt;
  ssl_certificate_key /etc/nginx/certs/signaling.key;

  # WebSocket proxying
  location / {
    proxy_pass wss://webrtc_signaling;

    # WebSocket upgrade headers
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    # Timeouts for WebSocket
    proxy_read_timeout 3600s;
    proxy_send_timeout 3600s;
    proxy_connect_timeout 10s;

    # Disable buffering for WebSocket
    proxy_buffering off;

    # Keep-alive
    proxy_set_header Connection "";
  }

  # Health check endpoint
  location /health {
    access_log off;
    return 200 "ok\n";
    add_header Content-Type text/plain;
  }
}
```

**Manual Recovery for Signaling Server:**

```bash
#!/bin/bash
# recover-signaling-server.sh

set -e

FAILED_SERVER=$1
ACTION=${2:-restart}  # restart or promote_backup

echo "Signaling Server Recovery Procedure"
echo "Failed server: $FAILED_SERVER"
echo "Action: $ACTION"

case $ACTION in
  restart)
    echo "ACTION 1: Restarting failed signaling server..."
    systemctl restart webrtc-signaling-server

    sleep 5

    # Verify recovery
    if curl -sf https://signaling.infrafabric.local/health > /dev/null; then
      echo "✓ Signaling server recovered"
    else
      echo "✗ Signaling server failed to recover"
      exit 1
    fi
    ;;

  promote_backup)
    echo "ACTION 2: Promoting backup signaling server..."

    # Update load balancer to remove failed server
    # (nginx will automatically use backup server)

    # Verify backup is serving traffic
    sleep 10

    ACTIVE_CONNS=$(curl -s https://signaling.infrafabric.local/stats | \
      jq '.total_agents')
    echo "   Active connections: $ACTIVE_CONNS"

    if [ "$ACTIVE_CONNS" -gt 0 ]; then
      echo "✓ Backup server is serving agents"
    else
      echo "✗ No agents connected to backup"
      exit 1
    fi
    ;;

  *)
    echo "Unknown action: $ACTION"
    exit 1
    ;;
esac

# Monitor for stabilization (5 minutes)
echo ""
echo "Monitoring stabilization (5 minutes)..."

for i in {1..5}; do
  FAILED_CONNS=$(curl -s https://signaling.infrafabric.local/stats | \
    jq '.connections | map(select(.state=="failed")) | length')

  ERROR_RATE=$(curl -s https://signaling.infrafabric.local/metrics | \
    grep webrtc_signaling_errors_total | tail -1)

  echo "[$i/5] Failed connections: $FAILED_CONNS | Error rate: $ERROR_RATE"

  if [ "$FAILED_CONNS" -gt 10 ]; then
    echo "⚠ High number of failed connections, investigating..."
    # Get details of failures
    curl -s https://witness.infrafabric.local/api/query -d '{
      "query": {"event": "connection_state_changed", "metadata.state": "failed"},
      "time_range": {"from": "-1m", "to": "now"}
    }' | jq '.results | last'
  fi

  sleep 60
done

# Log recovery
curl -X POST https://witness.infrafabric.local/api/log \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"event\": \"signaling_server_recovery\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"metadata\": {
      \"failed_server\": \"$FAILED_SERVER\",
      \"recovery_action\": \"$ACTION\",
      \"operator\": \"$(whoami)\"
    }
  }"

echo "✅ Signaling server recovery complete"
```

### Scenario C: Network Partition → Mesh Healing

**Automatic Mesh Healing with Exponential Backoff:**

```typescript
/**
 * Mesh Healing Strategy
 *
 * When an agent becomes isolated from the mesh:
 * 1. Detect isolation (no heartbeat for 30s)
 * 2. Initiate exponential backoff reconnection
 * 3. Attempt to reconnect to all known peers
 * 4. Log all attempts to IF.witness for visibility
 * 5. If healing fails after 17 minutes, escalate
 */

interface PeerReconnectionState {
  peerId: string;
  lastHeartbeat: Date;
  reconnectAttempts: number;
  nextRetryTime: Date;
  backoffMs: number;
}

class IFAgentWebRTC {
  private reconnectionStates: Map<string, PeerReconnectionState> = new Map();
  private heartbeatInterval?: NodeJS.Timeout;
  private readonly HEARTBEAT_CHECK_INTERVAL = 5000;  // Every 5 seconds
  private readonly HEARTBEAT_TIMEOUT = 30000;  // 30 seconds = partition detection
  private readonly MAX_RECONNECT_ATTEMPTS = 10;  // 2^10 = ~17 minutes
  private readonly INITIAL_BACKOFF_MS = 1000;

  startHeartbeatMonitoring(): void {
    this.heartbeatInterval = setInterval(() => {
      this.checkHeartbeats();
    }, this.HEARTBEAT_CHECK_INTERVAL);
  }

  private checkHeartbeats(): void {
    const now = new Date();

    for (const [peerId, quality] of this.connectionQuality) {
      const lastUpdated = new Date(quality.lastUpdated);
      const timeSinceUpdate = now.getTime() - lastUpdated.getTime();

      // Check if heartbeat is missing (partition detected)
      if (timeSinceUpdate > this.HEARTBEAT_TIMEOUT) {
        this.handlePartition(peerId);
      } else {
        // Reset reconnection state on heartbeat
        if (this.reconnectionStates.has(peerId)) {
          this.reconnectionStates.delete(peerId);

          this.logToWitness({
            event: 'mesh_partition_healed',
            peer_id: peerId,
            timestamp: new Date().toISOString()
          });
        }
      }
    }
  }

  private handlePartition(peerId: string): void {
    let state = this.reconnectionStates.get(peerId);

    if (!state) {
      // First detection of partition
      state = {
        peerId,
        lastHeartbeat: new Date(),
        reconnectAttempts: 0,
        nextRetryTime: new Date(),
        backoffMs: this.INITIAL_BACKOFF_MS
      };

      this.reconnectionStates.set(peerId, state);

      this.logToWitness({
        event: 'mesh_partition_detected',
        peer_id: peerId,
        timestamp: new Date().toISOString()
      });
    }

    // Check if it's time to retry
    const now = new Date();
    if (now.getTime() >= state.nextRetryTime.getTime()) {
      this.attemptMeshHealing(state);
    }
  }

  private async attemptMeshHealing(state: PeerReconnectionState): Promise<void> {
    state.reconnectAttempts++;
    const attempt = state.reconnectAttempts;

    // Calculate next backoff time: 2^attempt seconds
    const nextBackoffMs = Math.pow(2, Math.min(attempt, 10)) * 1000;
    state.nextRetryTime = new Date(Date.now() + nextBackoffMs);

    this.logToWitness({
      event: 'mesh_healing_attempt',
      peer_id: state.peerId,
      timestamp: new Date().toISOString(),
      metadata: {
        attempt,
        next_retry_ms: nextBackoffMs,
        max_attempts: this.MAX_RECONNECT_ATTEMPTS
      }
    });

    try {
      // Close old connection
      const oldPc = this.peerConnections.get(state.peerId);
      if (oldPc && oldPc.connectionState !== 'closed') {
        oldPc.close();
      }

      // Attempt new connection
      const offer = await this.createOffer(state.peerId);

      // If successful, reconnection state will be cleared on next heartbeat
    } catch (error) {
      if (attempt >= this.MAX_RECONNECT_ATTEMPTS) {
        // Give up after max attempts
        this.logToWitness({
          event: 'mesh_healing_failed_final',
          peer_id: state.peerId,
          timestamp: new Date().toISOString(),
          metadata: {
            total_attempts: attempt,
            error: (error as Error).message,
            severity: 'critical'
          }
        });

        this.reconnectionStates.delete(state.peerId);
      }
    }
  }

  /**
   * Manual mesh healing trigger
   */
  async triggerMeshHealing(): Promise<void> {
    console.log('Triggering manual mesh healing...');

    for (const peerId of this.getConnectedPeers()) {
      await this.disconnectPeer(peerId);
      await this.sleep(500);  // Stagger reconnections
      await this.createOffer(peerId);
    }

    this.logToWitness({
      event: 'mesh_healing_manual_triggered',
      agent_id: this.agentId,
      timestamp: new Date().toISOString(),
      metadata: {
        peers_reconnecting: this.getConnectedPeers().length
      }
    });
  }
}
```

### Scenario D: Certificate Expiration → Rotation Procedure

See Section 3.4 of WEBRTC-PROD-RUNBOOK.md

### Scenario E: SRTP Key Compromise → Emergency Rotation

See Section 4.5 of WEBRTC-PROD-RUNBOOK.md

---

## Recovery Validation

### Post-Failover Health Checks

```bash
#!/bin/bash
# validate-failover-recovery.sh

FAILOVER_ID=$1
FAILOVER_SCENARIO=$2  # A, B, C, D, or E

echo "Validating Failover Recovery"
echo "Failover ID: $FAILOVER_ID"
echo "Scenario: $FAILOVER_SCENARIO"

echo ""
echo "=== IMMEDIATE CHECKS (0-1 minute) ==="

# 1. Check agent registration
echo "1. Agent registration status..."
REGISTERED_AGENTS=$(curl -s https://signaling.infrafabric.local/stats | \
  jq '.total_agents')
echo "   Registered agents: $REGISTERED_AGENTS"

if [ "$REGISTERED_AGENTS" -eq 0 ]; then
  echo "   ✗ CRITICAL: No agents registered"
  exit 1
fi

# 2. Check connection establishment
echo "2. Connection status..."
ESTABLISHED=$(curl -s https://webrtc.infrafabric.local:8443/stats | \
  jq '.connections | map(select(.state=="connected")) | length')
FAILED=$(curl -s https://webrtc.infrafabric.local:8443/stats | \
  jq '.connections | map(select(.state=="failed")) | length')

TOTAL=$(curl -s https://webrtc.infrafabric.local:8443/stats | \
  jq '.connections | length')

if [ "$TOTAL" -gt 0 ]; then
  SUCCESS_RATE=$(( ESTABLISHED * 100 / TOTAL ))
  echo "   Connection success rate: $SUCCESS_RATE% ($ESTABLISHED/$TOTAL)"

  if [ "$SUCCESS_RATE" -lt 80 ]; then
    echo "   ⚠ Warning: Success rate below 80%"
  fi
else
  echo "   No connections yet"
fi

echo ""
echo "=== SHORT-TERM CHECKS (1-5 minutes) ==="

# 3. Message delivery
echo "3. Message delivery test..."
if node scripts/test-message-delivery.js --duration 30 --agents 3; then
  echo "   ✓ Messages delivered successfully"
else
  echo "   ✗ Message delivery failed"
fi

# 4. Latency check
echo "4. Latency metrics..."
P50=$(curl -s https://prometheus.infrafabric.local/api/v1/query | \
  grep webrtc_rtt_milliseconds | head -1)
echo "   P50 latency: $P50 ms"

# 5. IF.witness event verification
echo "5. Checking IF.witness logs..."
FAILOVER_EVENTS=$(curl -X POST https://witness.infrafabric.local/api/query \
  -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": {\"failover_id\": \"$FAILOVER_ID\"},
    \"time_range\": {\"from\": \"-10m\", \"to\": \"now\"}
  }" | jq '.results | length')

echo "   Failover events logged: $FAILOVER_EVENTS"

if [ "$FAILOVER_EVENTS" -eq 0 ]; then
  echo "   ⚠ Warning: No IF.witness events for this failover"
fi

echo ""
echo "=== STABILITY CHECKS (5+ minutes) ==="

# 6. Error rate trend
echo "6. Error rate trend..."
for i in {1..3}; do
  ERRORS=$(curl -X POST https://witness.infrafabric.local/api/query \
    -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": {\"event\": {\"regex\": \".*error.*\"}},
      \"time_range\": {\"from\": \"-$((i*5))m\", \"to\": \"-$((i-1)*5)m\"}
    }" | jq '.results | length')

  echo "   [$i] Last $((i*5)) minutes: $ERRORS errors"
done

echo ""
echo "=== VALIDATION SUMMARY ==="

# Determine pass/fail
VALIDATION_PASSED=true

if [ "$REGISTERED_AGENTS" -lt 1 ]; then
  echo "✗ No agents registered"
  VALIDATION_PASSED=false
fi

if [ "$SUCCESS_RATE" -lt 80 ]; then
  echo "⚠ Connection success rate below 80%"
fi

if [ "$VALIDATION_PASSED" = true ]; then
  echo "✅ Failover recovery SUCCESSFUL"

  # Log success
  curl -X POST https://witness.infrafabric.local/api/log \
    -H "Authorization: Bearer $IF_WITNESS_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"event\": \"failover_recovery_validated\",
      \"failover_id\": \"$FAILOVER_ID\",
      \"scenario\": \"$FAILOVER_SCENARIO\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
      \"metrics\": {
        \"registered_agents\": $REGISTERED_AGENTS,
        \"connection_success_rate\": $SUCCESS_RATE
      }
    }"

else
  echo "✗ Failover recovery FAILED - Manual intervention required"
  exit 1
fi
```

---

**Document Version:** 1.0
**Last Updated:** November 11, 2025
**Next Review:** December 11, 2025
