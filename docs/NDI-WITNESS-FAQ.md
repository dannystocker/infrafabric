# NDI Witness Integration - Frequently Asked Questions

**Last Updated:** 2025-11-12
**Component:** IF.witness + NDI Streaming
**Audience:** Developers integrating witness functionality into NDI video workflows

---

## Table of Contents

1. [What is IF.witness?](#what-is-ifwitness)
2. [NDI Integration Basics](#ndi-integration-basics)
3. [Hash Chains & Tamper Detection](#hash-chains--tamper-detection)
4. [Performance & Overhead](#performance--overhead)
5. [Security & Cryptography](#security--cryptography)
6. [Troubleshooting](#troubleshooting)
7. [Common Integration Patterns](#common-integration-patterns)
8. [Best Practices](#best-practices)

---

## What is IF.witness?

### Q: What problem does IF.witness solve?

**A:** IF.witness provides **cryptographic proof** that events happened in a specific order and were not tampered with. In multi-agent systems where 7-50+ agents coordinate, you need to know:
- Which agent claimed which task (and when)
- What decisions were made (and by whom)
- Whether coordination data was modified after the fact

Without witness, you have no audit trail. With witness, every event is cryptographically signed and chained together—like blockchain for coordination events.

### Q: How does IF.witness relate to NDI streaming?

**A:** NDI (Network Device Interface) is a video streaming protocol. When using NDI in InfraFabric:
- Video frames flow through the system
- Agents make decisions about routing, quality, fallback
- **IF.witness records these decisions** as a tamper-proof audit trail

Example: If an agent switches from 1080p to 720p due to bandwidth, witness records:
```
Event: quality_downgrade
Agent: session-1-ndi
From: 1080p
To: 720p
Reason: bandwidth_limited
Timestamp: 2025-11-12T14:32:15.823Z
Signature: [Ed25519 signature]
PrevHash: 3a7f8c...
```

### Q: Is IF.witness required or optional?

**A:** **Optional but strongly recommended** for production deployments. During development, you can disable witness to simplify debugging. In production:
- ✅ **Enable witness** if you need compliance, auditing, or multi-tenant isolation
- ❌ **Disable witness** if you're in a trusted single-tenant environment with no audit requirements

Toggle in config:
```yaml
witness:
  enabled: true  # Set false to disable
  signing_key: /etc/infrafabric/keys/witness.key
```

---

## NDI Integration Basics

### Q: Where does witness fit in the NDI video pipeline?

**A:** Witness runs **alongside** the video pipeline, not in it:

```
NDI Source → [Video Pipeline: Decode → Process → Encode → Stream] → NDI Sink
                      ↓
            [IF.witness: Record events]
                      ↓
            [Hash chain storage: etcd/filesystem]
```

**Key point:** Witness does NOT touch video frames. It only records metadata events (routing decisions, quality changes, failover events).

### Q: What NDI events should I record in witness?

**A:** Record **decision points** and **state changes**, not frame-by-frame data:

| Event Type | Record? | Why |
|------------|---------|-----|
| Stream started | ✅ Yes | Audit who initiated stream |
| Quality change | ✅ Yes | Track adaptive quality decisions |
| Failover event | ✅ Yes | Critical for reliability audit |
| Routing change | ✅ Yes | Track which agent made routing decisions |
| Stream stopped | ✅ Yes | Audit who terminated stream |
| Frame decoded | ❌ No | Too high frequency (30-60fps) |
| Audio sample | ❌ No | Too high frequency (48kHz) |

**Rule of thumb:** If it's a human-level decision (0.1-10 events/sec), record it. If it's frame-level (30-60 events/sec), don't.

### Q: How do I record an NDI event in witness?

**A:** Use the `witness.record_event()` API:

```python
from infrafabric.witness import WitnessRecorder

# Initialize witness recorder
witness = WitnessRecorder(
    session_id="session-1-ndi",
    key_path="/etc/infrafabric/keys/witness.key"
)

# Record NDI stream start
witness.record_event(
    event_type="ndi_stream_started",
    data={
        "source_name": "Camera-1",
        "resolution": "1920x1080",
        "framerate": 30,
        "codec": "h264"
    },
    metadata={
        "agent": "session-1-ndi",
        "reason": "user_requested"
    }
)
```

This creates a signed event, chains it to the previous event, and stores it in etcd.

---

## Hash Chains & Tamper Detection

### Q: What is a hash chain?

**A:** A hash chain links events together so that **modifying any event breaks the entire chain**:

```
Event 1: hash=abc123, prev_hash=None
         ↓
Event 2: hash=def456, prev_hash=abc123  ← Links to Event 1
         ↓
Event 3: hash=789ghi, prev_hash=def456  ← Links to Event 2
```

If you modify Event 2, its hash changes from `def456` to `xyz999`. Now Event 3's `prev_hash=def456` doesn't match, and the chain is broken.

### Q: How do I verify the hash chain?

**A:** Use `witness.verify_chain()`:

```python
from infrafabric.witness import WitnessVerifier

verifier = WitnessVerifier()

# Verify the entire chain
result = verifier.verify_chain(
    chain_id="session-1-ndi-2025-11-12",
    start_event=0,
    end_event=None  # None = verify to latest event
)

if result.valid:
    print(f"✅ Chain valid ({result.event_count} events)")
else:
    print(f"❌ Chain broken at event {result.break_point}")
    print(f"   Expected hash: {result.expected_hash}")
    print(f"   Actual hash: {result.actual_hash}")
```

### Q: What happens if someone tampers with an event?

**A:** The hash chain breaks, and you can detect exactly which event was modified:

**Example scenario:**
```python
# Original event
event_2 = {
    "event_type": "quality_downgrade",
    "data": {"from": "1080p", "to": "720p"},
    "hash": "def456",
    "prev_hash": "abc123"
}

# Attacker modifies event (tries to hide quality downgrade)
event_2_tampered = {
    "event_type": "quality_downgrade",
    "data": {"from": "1080p", "to": "1080p"},  # ← Changed!
    "hash": "def456",  # ← Hash didn't change (invalid!)
    "prev_hash": "abc123"
}

# Verification detects tampering
verifier.verify_event(event_2_tampered)
# → InvalidHashError: Event hash does not match computed hash
#    Expected: xyz999 (computed from tampered data)
#    Actual: def456 (claimed hash)
```

**Result:** Tampering detected in <1ms, with exact event ID and expected vs. actual hash.

### Q: Can I verify a chain in real-time?

**A:** Yes, but use **sampling** to avoid verification overhead:

```python
# Verify every 100th event in real-time
if event_count % 100 == 0:
    verifier.verify_chain(chain_id, start=event_count-100, end=event_count)

# Or verify the last N events periodically
def periodic_verification():
    while True:
        verifier.verify_chain(chain_id, start=-1000, end=None)
        time.sleep(60)  # Verify last 1000 events every minute
```

For NDI streaming (10 events/min), verify every 100 events = every 10 minutes.

---

## Performance & Overhead

### Q: How much overhead does witness add?

**A:** Minimal—designed for real-time systems:

| Operation | Latency | Throughput | Notes |
|-----------|---------|------------|-------|
| Record event | ~0.5ms | 2,000 events/sec | Ed25519 signing + hash |
| Verify single event | ~0.3ms | 3,000 events/sec | Hash verification |
| Verify chain (1,000 events) | ~250ms | 4,000 events/sec | Batch verification |
| Store event (etcd) | ~2ms | 500 events/sec | Network + etcd write |

**For NDI streaming:**
- Typical rate: 0.1-10 events/sec (quality changes, routing)
- Witness overhead: <1% of CPU, <10KB/sec network
- **Verdict:** Negligible impact on video pipeline

### Q: Can witness keep up with 60fps video?

**A:** **Don't record frame-level events** in witness. Witness is for decision events (0.1-10/sec), not frame events (30-60/sec).

If you must record high-frequency events:
- Use **batching**: Accumulate events, sign once per batch
- Use **sampling**: Record every Nth frame (e.g., every 10th keyframe)
- Use **separate logging**: Use a time-series DB for frame metadata, witness for decisions

Example batching:
```python
# Batch 100 frame events, sign once
batch = []
for frame in video_stream:
    batch.append({"frame_id": frame.id, "timestamp": frame.ts})

    if len(batch) >= 100:
        witness.record_batch(event_type="frame_batch", data=batch)
        batch = []
```

### Q: How much storage does witness use?

**A:** Each witness event is ~500 bytes (JSON + signature). For NDI streaming:

| Event Rate | Storage/Hour | Storage/Day | Storage/Month |
|------------|--------------|-------------|---------------|
| 0.1 events/sec | 180 KB | 4.3 MB | 130 MB |
| 1 event/sec | 1.8 MB | 43 MB | 1.3 GB |
| 10 events/sec | 18 MB | 430 MB | 13 GB |

**Typical NDI deployment:** 1 event/sec = 1.3 GB/month = $0.05/month S3 storage.

**Retention policy:**
```yaml
witness:
  retention_days: 90  # Keep 3 months of history
  archive_after_days: 30  # Move to S3 Glacier after 30 days
```

---

## Security & Cryptography

### Q: What cryptographic algorithm does witness use?

**A:** **Ed25519** (elliptic curve digital signatures):
- **Why Ed25519?** Fast (0.3ms signing), secure (128-bit security), small signatures (64 bytes)
- **Alternatives considered:** RSA (too slow), ECDSA (implementation bugs), HSM (too expensive)

### Q: Where are witness signing keys stored?

**A:** Depends on security requirements:

| Storage Method | Security | Performance | Use Case |
|----------------|----------|-------------|----------|
| Filesystem (`/etc/infrafabric/keys`) | Medium | Fast | Development, single-tenant |
| etcd (encrypted) | High | Fast | Multi-tenant, distributed |
| HSM (Hardware Security Module) | Very High | Slow | Financial, compliance |
| KMS (AWS KMS, Vault) | High | Medium | Cloud deployments |

**Production recommendation:** etcd with encryption at rest.

Configuration:
```yaml
witness:
  key_storage: etcd
  etcd:
    endpoints: ["https://etcd-1:2379"]
    key_path: /infrafabric/keys/witness/session-1-ndi
    encryption: true
    ca_cert: /etc/infrafabric/certs/ca.crt
```

### Q: Can an agent forge witness events?

**A:** **No**, if keys are properly isolated:
- Each session has its own Ed25519 key pair
- Session 1 cannot sign events claiming to be Session 2
- Verification checks signature against claimed session's public key

**Attack scenario (prevented):**
```python
# Attacker (Session 1) tries to forge Session 2 event
malicious_event = {
    "agent": "session-2-webrtc",  # ← Claims to be Session 2
    "event_type": "ndi_stream_started",
    "signature": sign_with_session_1_key(data)  # ← Signed with Session 1's key
}

# Verification fails
verifier.verify_event(malicious_event, public_key=session_2_public_key)
# → SignatureVerificationError: Signature does not match claimed agent
```

### Q: What if a signing key is compromised?

**A:** Implement **key rotation**:

1. **Detect compromise** (unusual signing activity, key leaked)
2. **Rotate key immediately**:
   ```python
   witness.rotate_key(
       old_key_path="/etc/infrafabric/keys/witness-old.key",
       new_key_path="/etc/infrafabric/keys/witness-new.key"
   )
   ```
3. **Record rotation event** (signed with new key):
   ```python
   witness.record_event(
       event_type="key_rotation",
       data={
           "old_key_fingerprint": "abc123...",
           "new_key_fingerprint": "def456...",
           "reason": "suspected_compromise"
       }
   )
   ```
4. **Re-verify historical chain** with old key (proves events before rotation were valid)

---

## Troubleshooting

### Q: Witness verification fails with "hash mismatch"—what do I do?

**A:** This indicates either tampering or a bug. Investigate:

1. **Check event details:**
   ```python
   event = witness.get_event(event_id=12345)
   print(f"Expected hash: {event.hash}")
   print(f"Computed hash: {compute_hash(event.data)}")
   ```

2. **Check previous event:**
   ```python
   prev_event = witness.get_event(event_id=12344)
   print(f"Prev hash stored: {event.prev_hash}")
   print(f"Prev hash actual: {prev_event.hash}")
   ```

3. **Common causes:**
   - **Clock skew**: Timestamps out of order (fix NTP)
   - **Serialization bug**: JSON field order changed (use canonical JSON)
   - **Storage corruption**: etcd data corruption (restore from backup)
   - **Actual tampering**: Someone modified etcd directly (investigate access logs)

### Q: Witness recording is slow (<100 events/sec)—how do I optimize?

**A:** Likely caused by synchronous etcd writes. Use **async batching**:

```python
# Before (slow): Synchronous writes
for event in events:
    witness.record_event(event)  # Blocks on etcd write (~2ms each)

# After (fast): Batch writes
witness.record_events_batch(events)  # Single etcd write (~2ms total)
```

Or use **async mode**:
```python
witness = WitnessRecorder(session_id="session-1-ndi", async_mode=True)

# Records to in-memory buffer, flushes every 100ms
witness.record_event(event)  # Returns immediately
```

### Q: I see "signature verification failed"—what's wrong?

**A:** Check key consistency:

1. **Verify public key matches:**
   ```python
   public_key = witness.get_public_key(session_id="session-1-ndi")
   print(f"Public key fingerprint: {public_key.fingerprint()}")
   ```

2. **Check event signature:**
   ```python
   event = witness.get_event(event_id=12345)
   is_valid = verify_signature(
       message=event.data,
       signature=event.signature,
       public_key=public_key
   )
   print(f"Signature valid: {is_valid}")
   ```

3. **Common causes:**
   - **Key mismatch**: Event signed with different key than expected
   - **Key rotation**: Public key was rotated, but old events not re-verified
   - **Corrupted signature**: Storage corruption (check etcd integrity)

---

## Common Integration Patterns

### Pattern 1: NDI Stream Lifecycle Tracking

Record key events in an NDI stream's lifecycle:

```python
from infrafabric.witness import WitnessRecorder

witness = WitnessRecorder(session_id="session-1-ndi")

# 1. Stream started
witness.record_event("ndi_stream_started", {
    "source": "Camera-1",
    "resolution": "1920x1080",
    "bitrate_mbps": 50
})

# 2. Quality adjustment (during stream)
witness.record_event("ndi_quality_adjusted", {
    "from_resolution": "1920x1080",
    "to_resolution": "1280x720",
    "reason": "bandwidth_limited",
    "available_bandwidth_mbps": 25
})

# 3. Failover (if primary fails)
witness.record_event("ndi_failover", {
    "from_source": "Camera-1",
    "to_source": "Camera-1-Backup",
    "reason": "primary_timeout",
    "downtime_ms": 150
})

# 4. Stream stopped
witness.record_event("ndi_stream_stopped", {
    "source": "Camera-1-Backup",
    "reason": "user_requested",
    "duration_seconds": 3600,
    "total_frames": 108000
})
```

### Pattern 2: Multi-Agent Coordination Audit

Track which agent made which decision:

```python
# Session 1 (NDI) starts stream
witness_s1.record_event("coordination_event", {
    "action": "start_ndi_stream",
    "session": "session-1-ndi",
    "task_id": "P0.1.2"
})

# Session 2 (WebRTC) receives stream
witness_s2.record_event("coordination_event", {
    "action": "receive_ndi_stream",
    "session": "session-2-webrtc",
    "from_session": "session-1-ndi",
    "stream_id": "ndi-camera-1"
})

# Session 4 (SIP) routes to external client
witness_s4.record_event("coordination_event", {
    "action": "route_to_sip_client",
    "session": "session-4-sip",
    "from_session": "session-2-webrtc",
    "sip_uri": "sip:user@example.com"
})
```

Later, audit the entire flow:
```python
# Query: Who handled stream "ndi-camera-1"?
events = witness.query({"stream_id": "ndi-camera-1"})
for e in events:
    print(f"{e.timestamp} - {e.agent}: {e.action}")

# Output:
# 2025-11-12T14:30:00Z - session-1-ndi: start_ndi_stream
# 2025-11-12T14:30:01Z - session-2-webrtc: receive_ndi_stream
# 2025-11-12T14:30:02Z - session-4-sip: route_to_sip_client
```

### Pattern 3: Compliance Audit Trail

Record all administrative actions for compliance:

```python
# Admin enables witness
witness.record_event("admin_action", {
    "action": "enable_witness",
    "user": "admin@example.com",
    "ip_address": "192.168.1.100",
    "reason": "compliance_requirement"
})

# Admin rotates key
witness.record_event("admin_action", {
    "action": "rotate_witness_key",
    "user": "admin@example.com",
    "old_key_fingerprint": "abc123",
    "new_key_fingerprint": "def456"
})

# Admin exports audit log
witness.record_event("admin_action", {
    "action": "export_audit_log",
    "user": "auditor@example.com",
    "date_range": "2025-11-01 to 2025-11-30",
    "event_count": 8642
})
```

---

## Best Practices

### ✅ DO:

1. **Record decision events, not data events**
   - ✅ Quality change decisions (0.1-1/sec)
   - ❌ Frame timestamps (30-60/sec)

2. **Use semantic event types**
   - ✅ `ndi_quality_adjusted`, `ndi_failover`
   - ❌ `event_type_42`, `status_update`

3. **Include context in event data**
   - ✅ `{"reason": "bandwidth_limited", "available_mbps": 25}`
   - ❌ `{"status": "changed"}`

4. **Verify chains periodically (not every event)**
   - ✅ Verify last 1000 events every minute
   - ❌ Verify after every single event

5. **Use async mode for high-frequency recording**
   - ✅ `WitnessRecorder(async_mode=True)`
   - ❌ Synchronous recording with 100+ events/sec

6. **Rotate keys annually (or after compromise)**
   - ✅ Scheduled rotation every 12 months
   - ❌ Never rotate keys

### ❌ DON'T:

1. **Don't record sensitive data in witness events**
   - ❌ Passwords, API keys, PII
   - ✅ Use event references: `{"stream_id": "uuid", "user_id": "hashed"}`

2. **Don't modify witness events after recording**
   - ❌ Updating events in etcd breaks hash chain
   - ✅ Record a new "correction" event if needed

3. **Don't disable witness in production without approval**
   - ❌ `witness.enabled = false` in production
   - ✅ Require security team approval for disabling

4. **Don't store witness keys in version control**
   - ❌ `git add /etc/infrafabric/keys/witness.key`
   - ✅ Use secrets management (etcd, Vault, KMS)

5. **Don't use witness for real-time alerting**
   - ❌ `if witness.last_event.type == "failure": alert()`
   - ✅ Use IF.bus or direct monitoring for real-time alerts

---

## Additional Resources

- **IF.witness API Reference:** See `infrafabric/witness.py` module documentation
- **Hash Chain Example:** See `examples/witness-hash-chain-demo.py`
- **Integration Tests:** See `tests/integration/test_witness.py`
- **Performance Benchmarks:** See `docs/PHASE-0-PERFORMANCE.md`

---

## Getting Help

- **Slack:** `#infrafabric-witness` channel
- **GitHub Issues:** Tag with `component:witness`
- **On-call:** PagerDuty escalation for production witness failures

---

**Document Status:** ✅ Complete
**Last Review:** 2025-11-12
**Next Review:** 2025-12-12 (monthly)
