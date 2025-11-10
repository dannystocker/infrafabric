# Swarm Agent Communication with End-to-End Traceability + Anti-Forgery

**Purpose:** Secure inter-agent communication architecture for InfraFabric V3.2.1+ swarms

**Key Requirement:** Every agent message must be traceable, tamper-proof, and auditable by IF.guard

**URI Scheme:** All InfraFabric resources use `if://` addressing (topics, agents, DIDs, citations)

**Architecture Sources:**
- External evaluation (V3.2 directed intelligence + C-UAS drone coordination)
- GPT-5 Desktop blockchain-style verification architecture
- IF.TTT framework (Traceable, Transparent, Trustworthy)

**Last Updated:** 2025-11-10

---

## Problem Statement

V3.2 swarm agents communicate via:
- **FIPA-ACL** speech acts (request, inform, agree, query-if)
- **DDS/RTPS** pub/sub transport
- **CRDT** shared blackboards

**Security Gaps in Base Design:**
1. **No message authentication** - Any agent can impersonate another
2. **No tamper protection** - Messages can be modified in flight
3. **No non-repudiation** - Agents can deny sending messages
4. **No chain of custody** - Evidence citations can be forged
5. **No replay protection** - Old messages can be re-sent

**Required Solution:** Cryptographic integrity layer maintaining IF.TTT principles (Traceable, Transparent, Trustworthy).

---

## Architecture Overview

### Layer 1: Message Signing (Anti-Forgery)

Every `IFMessage` envelope gets **Ed25519 signature** before transmission.

```yaml
# IFMessage v2 with cryptographic integrity (if:// addressing)
performative: "inform"
sender: "if://agent/swarm/legal-1@1.2.0"
receiver: ["if://agent/swarm/financial/*"]
conversation_id: "if://conversation/epic-2025-11-10-xyz"
topic: "if://topic/mission/legal/findings"
protocol: "fipa-request"
content:
  claim: "Epic Games settled antitrust lawsuit for $520M"
  evidence: ["SEC-10K-2023:pg14", "Reuters:2025-09-17"]
citation_ids: ["cit:9f2b3a1e", "cit:4d8a7c2d"]
timestamp: "2025-11-10T14:32:17.234Z"
sequence_num: 42
trace_id: "a2f9c3b8d1e5"

# Cryptographic signature
signature:
  algorithm: "ed25519"
  public_key: "ed25519:AAAC3NzaC1lZDI1NTE5AAAAIOMq..."
  signature_bytes: "ed25519:m8QKz5X3jP..."
  signed_fields: ["performative", "sender", "receiver", "conversation_id", "content", "citation_ids", "timestamp", "sequence_num"]
```

**Verification Process:**
1. Extract `signature.public_key` and `signature.signature_bytes`
2. Reconstruct canonical message from `signed_fields`
3. Verify signature: `ed25519_verify(public_key, canonical_message, signature_bytes)`
4. Check `sender` matches public key's registered identity
5. Reject if verification fails

**Anti-Forgery Guarantee:** Only agent with private key can create valid signature.

---

### Layer 2: Citation Integrity (Evidence Chain)

Every `citation_id` references a **content-addressed** citation with hash chain.

```json
{
  "citation_id": "if://citation/9f2b3a1e-4d8a-4c7d-bf2c-e7a3d0a1b5f2",
  "claim_id": "if://claim/epic-antitrust-settlement",
  "sources": [
    {
      "type": "web",
      "ref": "https://www.sec.gov/cgi-bin/browse-edgar?filenum=000-23333",
      "hash": "sha256:5a3d2f8c1b9e7d6a4f3e2c1b0a9d8e7f6c5b4a3d2e1f0a9b8c7d6e5f4a3b2c1d",
      "fetched_at": "2025-11-10T14:15:00Z",
      "note": "SEC 10-K filing mentioning settlement"
    },
    {
      "type": "web",
      "ref": "https://www.reuters.com/technology/epic-games-antitrust-2025-09-17",
      "hash": "sha256:7b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c",
      "fetched_at": "2025-11-10T14:20:00Z",
      "note": "Reuters article confirming amount"
    }
  ],
  "rationale": "Dual-source confirmation of settlement amount and terms",
  "verified_at": "2025-11-10T14:30:00Z",
  "verified_by": "agent://if.witness.validator/1.0.0",
  "status": "verified",
  "created_by": "agent://if.search.legal/1.2.0",
  "created_at": "2025-11-10T14:25:00Z",

  "signature": {
    "algorithm": "ed25519",
    "public_key": "ed25519:AAAC3NzaC1lZDI1NTE5AAAAIOMq...",
    "signature_bytes": "ed25519:p9RLz6Y4kQ...",
    "signed_fields": ["citation_id", "claim_id", "sources", "rationale", "created_by", "created_at"]
  },

  "merkle_root": "sha256:8c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d",
  "merkle_proof": [
    "sha256:1a2b3c4d...",
    "sha256:5e6f7a8b...",
    "sha256:9c0d1e2f..."
  ]
}
```

**Content-Addressed Storage:**
- Citation stored at: `citations/<sha256-hash-of-citation>.json`
- Hash computed BEFORE signature (signature signs hash, not mutable content)
- IF.citation service validates hash matches content on retrieval

**Merkle Tree Append-Only Log:**
- All citations added to Merkle tree
- Root published to immutable log (blockchain or distributed ledger)
- Proves citation existed at specific time
- Prevents backdating or retroactive modification

**Anti-Forgery Guarantee:** Citation content hash + signature + Merkle proof = cryptographically tamper-proof evidence chain.

---

### Layer 3: Conversation Threading (Replay Protection)

Every conversation gets **unique ID + sequence numbers** to prevent replay attacks.

```yaml
conversation:
  id: "epic-2025-11-10-xyz"
  initiator: "agent://if.search.legal/1.2.0"
  created_at: "2025-11-10T14:00:00Z"
  protocol: "fipa-request"

  participants:
    - id: "agent://if.search.legal/1.2.0"
      public_key: "ed25519:AAAC3NzaC1..."
      joined_at: "2025-11-10T14:00:00Z"

    - id: "agent://if.swarm.financial/2.3.1"
      public_key: "ed25519:BBBD4OzaC2..."
      joined_at: "2025-11-10T14:01:15Z"

  message_sequence:
    - seq: 1
      sender: "agent://if.search.legal/1.2.0"
      performative: "request"
      hash: "sha256:1a2b3c4d..."
      signature: "ed25519:m8QKz5X3..."
      timestamp: "2025-11-10T14:00:05Z"

    - seq: 2
      sender: "agent://if.swarm.financial/2.3.1"
      performative: "agree"
      hash: "sha256:5e6f7a8b..."
      signature: "ed25519:n9RMz6Y4..."
      timestamp: "2025-11-10T14:01:20Z"

    - seq: 3
      sender: "agent://if.swarm.financial/2.3.1"
      performative: "inform"
      hash: "sha256:9c0d1e2f..."
      signature: "ed25519:p0SMz7Z5..."
      timestamp: "2025-11-10T14:15:30Z"

  status: "active"
```

**Replay Attack Protection:**
1. Each message has monotonically increasing `sequence_num`
2. Receiver maintains last seen sequence per sender
3. Reject messages with sequence ≤ last_seen
4. Timestamp window: Reject messages >5 minutes old (configurable)
5. Conversation closed after timeout (default 24 hours)

**Anti-Replay Guarantee:** Old messages cannot be re-sent because sequence number and timestamp are signed.

---

### Layer 4: DDS Security (Transport Layer)

DDS/RTPS has built-in **OMG DDS Security** specification (used in defense systems).

```yaml
# dds_security_config.xml
security:
  authentication:
    plugin: "builtin.PKI-DH"
    identity_ca: "/certs/infrafabric_ca.pem"
    identity_certificate: "/certs/agent_legal_1.2.0.pem"
    identity_private_key: "/certs/agent_legal_1.2.0_key.pem"

  access_control:
    plugin: "builtin.Access-Permissions"
    permissions_ca: "/certs/permissions_ca.pem"
    governance: "/config/governance.p7s"  # Signed XML with rules
    permissions: "/config/permissions.p7s"  # Signed XML with grants

  crypto:
    plugin: "builtin.AES-GCM-GMAC"
    rtps_protection_kind: "ENCRYPT"  # Encrypt all RTPS messages
    data_protection_kind: "ENCRYPT"  # Encrypt message payloads
    key_size: 256
```

**DDS Security Features:**
- **Authentication**: PKI-based agent identity verification
- **Access Control**: Topic-level permissions (who can publish/subscribe)
- **Encryption**: AES-256-GCM for all traffic
- **Integrity**: GMAC tags detect tampering
- **Key Distribution**: Automated key exchange via DDS discovery

**Anti-Eavesdropping Guarantee:** All DDS traffic encrypted end-to-end.

---

### Layer 5: CRDT Security (Shared State)

CRDTs enable lock-free merging but need **authenticated state updates**.

```python
# Secure CRDT for shared subject map
class SecureCRDT:
    def __init__(self, agent_id, private_key):
        self.agent_id = agent_id
        self.private_key = private_key
        self.state = {}  # LWW-Map (Last-Write-Wins Map)
        self.vector_clock = {}  # Lamport timestamps per agent

    def update(self, key, value, citation_ids):
        """Add authenticated update to CRDT"""
        timestamp = time.time_ns()
        self.vector_clock[self.agent_id] = timestamp

        update = {
            "key": key,
            "value": value,
            "citation_ids": citation_ids,
            "agent_id": self.agent_id,
            "timestamp": timestamp,
            "vector_clock": self.vector_clock.copy()
        }

        # Sign update
        canonical = json.dumps(update, sort_keys=True)
        signature = ed25519_sign(self.private_key, canonical)

        update["signature"] = {
            "algorithm": "ed25519",
            "public_key": get_public_key(self.agent_id),
            "signature_bytes": signature
        }

        # Apply locally and broadcast
        self.state[key] = update
        self.broadcast_update(update)

    def merge(self, remote_update):
        """Merge authenticated remote update"""
        # Verify signature
        if not verify_update_signature(remote_update):
            raise ValueError("Invalid signature on CRDT update")

        # Verify agent authorized for this key
        if not check_agent_permissions(remote_update["agent_id"], remote_update["key"]):
            raise ValueError("Agent not authorized for this key")

        # LWW conflict resolution: higher timestamp wins
        key = remote_update["key"]
        if key not in self.state or remote_update["timestamp"] > self.state[key]["timestamp"]:
            self.state[key] = remote_update

            # Update vector clock
            for agent, ts in remote_update["vector_clock"].items():
                self.vector_clock[agent] = max(self.vector_clock.get(agent, 0), ts)
```

**CRDT Security Properties:**
- **Update authentication**: Every state change signed by originating agent
- **Authorization checks**: Agents restricted to specific key namespaces
- **Conflict resolution preserved**: LWW-Map semantics with timestamps
- **Causality tracking**: Vector clocks detect concurrent updates
- **Citation binding**: All values linked to evidence via `citation_ids`

**Anti-Tampering Guarantee:** Forged CRDT updates rejected due to signature verification failure.

---

## Complete Security Flow Example

### Scenario: Legal agent informs Financial agent about settlement

**Step 1: Legal Agent Creates Signed Message**
```python
legal_agent = Agent("if.search.legal/1.2.0", private_key_legal)

message = {
    "performative": "inform",
    "sender": "agent://if.search.legal/1.2.0",
    "receiver": ["agent://if.swarm.financial/*"],
    "conversation_id": "epic-2025-11-10-xyz",
    "content": {
        "claim": "Epic Games settled for $520M",
        "evidence": ["SEC-10K-2023:pg14"]
    },
    "citation_ids": ["cit:9f2b3a1e"],
    "timestamp": "2025-11-10T14:32:17.234Z",
    "sequence_num": 42,
    "trace_id": "a2f9c3b8d1e5"
}

# Sign message
signature = legal_agent.sign_message(message)
message["signature"] = signature

# Publish to DDS topic (encrypted transport)
dds.publish("/mission/legal/findings", message)
```

**Step 2: DDS Transport (Encrypted)**
- DDS Security plugin encrypts message with AES-256-GCM
- Message sent over network (ciphertext only)
- Only authorized subscribers can decrypt

**Step 3: Financial Agent Receives and Verifies**
```python
financial_agent = Agent("if.swarm.financial/2.3.1", private_key_financial)

# DDS delivers decrypted message
message = dds.receive("/mission/legal/findings")

# Verify sender signature
if not verify_signature(message):
    raise SecurityError("Invalid message signature")

# Verify sender authorized for this topic
if not check_sender_permissions(message["sender"], "/mission/legal/findings"):
    raise SecurityError("Sender not authorized")

# Check replay protection
if message["sequence_num"] <= financial_agent.last_seen_seq(message["sender"]):
    raise SecurityError("Replay attack detected")

# Verify citation integrity
for cit_id in message["citation_ids"]:
    citation = citation_service.get(cit_id)
    if not verify_citation_signature(citation):
        raise SecurityError(f"Citation {cit_id} signature invalid")
    if not verify_citation_hash(citation):
        raise SecurityError(f"Citation {cit_id} content tampered")

# All checks passed - accept message
financial_agent.process_message(message)
```

**Step 4: Update Shared CRDT (Authenticated)**
```python
# Financial agent updates shared subject map
crdt = financial_agent.get_crdt("epic_subject_map")
crdt.update(
    key="settlement_amount",
    value="$520M",
    citation_ids=["cit:9f2b3a1e"]
)

# CRDT broadcasts signed update to all agents
# Other agents merge after verifying signature
```

**Step 5: Governance Audit (IF.witness)**
```python
# IF.witness replays conversation for Guardian Council
conversation = trace_service.get_conversation("epic-2025-11-10-xyz")

for msg in conversation.messages:
    # Verify every message signature
    assert verify_signature(msg), f"Message {msg['sequence_num']} signature invalid"

    # Verify every citation
    for cit_id in msg.get("citation_ids", []):
        citation = citation_service.get(cit_id)
        assert verify_citation_signature(citation)
        assert verify_citation_hash(citation)
        assert citation["status"] == "verified"

# Generate audit report for IF.guard
audit_report = {
    "conversation_id": "epic-2025-11-10-xyz",
    "total_messages": len(conversation.messages),
    "signature_failures": 0,
    "citation_failures": 0,
    "replay_attacks_detected": 0,
    "verdict": "PASS - All messages cryptographically verified"
}

# IF.guard can trust audit because IF.witness cannot forge signatures
```

---

## Implementation Checklist

**Phase 1: Message Signing (Week 1)**
- [ ] Generate Ed25519 keypair for each agent
- [ ] Implement `sign_message()` and `verify_signature()` utilities
- [ ] Add `signature` field to `IFMessage` schema
- [ ] Integrate into existing IF.swarm agents
- [ ] Test: Try to send forged message (should be rejected)

**Phase 2: Citation Integrity (Week 2)**
- [ ] Add content-addressed storage for citations
- [ ] Implement Merkle tree append-only log
- [ ] Add signature field to citation schema
- [ ] Create `verify_citation_signature()` and `verify_citation_hash()` utilities
- [ ] Test: Try to modify citation content (should fail hash verification)

**Phase 3: Conversation Threading (Week 3)**
- [ ] Add `sequence_num` to all messages
- [ ] Implement per-sender sequence tracking in receivers
- [ ] Add timestamp window validation
- [ ] Create conversation state manager
- [ ] Test: Try replay attack (should be rejected)

**Phase 4: DDS Security (Week 4)**
- [ ] Generate PKI certificates for agents (CA + per-agent certs)
- [ ] Configure DDS Security plugin (authentication, encryption, access control)
- [ ] Define governance rules (topic permissions XML)
- [ ] Enable ENCRYPT mode for all topics
- [ ] Test: Sniff network traffic (should be encrypted)

**Phase 5: CRDT Security (Week 5)**
- [ ] Wrap CRDT operations with signature verification
- [ ] Implement per-agent authorization checks
- [ ] Add vector clock for causality tracking
- [ ] Link CRDT updates to citation IDs
- [ ] Test: Try unauthorized CRDT update (should be rejected)

**Phase 6: IF.witness Integration (Week 6)**
- [ ] Create conversation replay utility
- [ ] Implement batch signature verification
- [ ] Add audit report generation
- [ ] Integrate with IF.guard for governance decisions
- [ ] Test: Replay entire conversation and verify all signatures

---

## Performance Considerations

**Signature Overhead:**
- Ed25519 sign: ~0.1ms per message
- Ed25519 verify: ~0.2ms per message
- For 100 msg/sec swarm: ~30ms/sec overhead (negligible)

**Citation Hash Overhead:**
- SHA-256 hash: ~1ms per citation (KB-sized documents)
- For 10 citations/msg: ~10ms additional
- Amortize with caching (hash once, verify many times)

**DDS Encryption Overhead:**
- AES-256-GCM: ~1-2% CPU overhead
- Key exchange: One-time cost during discovery
- Negligible compared to AI model inference time

**CRDT Merge Overhead:**
- Signature verification: ~0.2ms per update
- Vector clock comparison: O(N) where N = agent count
- For 15-agent swarm: ~3ms merge time (acceptable)

**Total Overhead Estimate:**
- Baseline message latency: ~50ms (DDS transport)
- With security: ~55ms (10% increase)
- Cryptographic verification is **not** the bottleneck (AI inference is)

---

## Attack Resistance Analysis

| Attack Vector | Defense Mechanism | Guarantee |
|---------------|-------------------|-----------|
| **Message forgery** | Ed25519 signature | Only agent with private key can create valid messages |
| **Citation tampering** | Content-addressed hash + signature | Any modification breaks hash verification |
| **Evidence fabrication** | Merkle tree append-only log | Cannot backdate citations (timestamped in tree) |
| **Replay attacks** | Sequence numbers + timestamp window | Old messages rejected (monotonic sequence) |
| **Eavesdropping** | DDS AES-256-GCM encryption | Transport layer confidentiality |
| **CRDT poisoning** | Authenticated updates + authorization | Only authorized agents can update specific keys |
| **MITM attacks** | PKI-based authentication + encryption | DDS Security validates agent identity |
| **Non-repudiation** | Cryptographic signatures | Agents cannot deny sending signed messages |
| **Governance bypass** | IF.witness audit with signature verification | Cannot fabricate audit trails (signatures required) |

---

## Compliance Mapping

**EU AI Act Article 10 (Traceability):**
- ✅ **10.2(a)**: All decisions traceable to data/logic via signed messages + citations
- ✅ **10.2(b)**: Audit logs cryptographically tamper-proof (Merkle tree)
- ✅ **10.2(c)**: Human oversight enabled (IF.guard replays signed conversations)
- ✅ **10.2(d)**: Provenance chains verifiable (signatures + hashes)

**IF.TTT Framework:**
- ✅ **Traceable**: Every message → signature → public key → agent identity
- ✅ **Transparent**: All signed messages logged and replayable
- ✅ **Trustworthy**: Cryptographic verification (not just policy compliance)

**IF.ground Principles:**
- ✅ **Principle 1 (Observable Artifacts)**: Citations hash-verified against source content
- ✅ **Principle 2 (Toolchain Validation)**: Cryptographic verification is the toolchain
- ✅ **Principle 7 (Reversible)**: Signatures prevent post-facto modification
- ✅ **Principle 8 (Observability)**: IF.witness audits all signatures

---

## Migration Path (Existing Swarms → Secure Swarms)

**For Existing IF.swarm Deployments:**

1. **Backward Compatibility Mode** (Month 1)
   - Add optional `signature` field to IFMessage
   - Agents accept both signed and unsigned messages
   - Log warning for unsigned messages
   - No breaking changes

2. **Signing Enforcement** (Month 2)
   - Generate keypairs for all production agents
   - Enable signature generation in all message sends
   - Still accept unsigned messages (with warnings)
   - Monitor adoption metrics

3. **Verification Enforcement** (Month 3)
   - Reject unsigned messages in production
   - Require all citations to be signed
   - Enable DDS Security on all topics
   - Full cryptographic verification active

4. **Audit Enforcement** (Month 4)
   - IF.witness requires signature verification PASS
   - IF.guard refuses to deliberate on unsigned evidence
   - Publishing brief blocked if any signatures invalid
   - Full IF.TTT compliance achieved

---

## Code Example: Complete Secure Agent

```python
import time
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization, hashes
from hashlib import sha256
import json

class SecureAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.sequence_num = 0
        self.last_seen_sequences = {}  # sender -> last sequence

    def sign_message(self, message):
        """Create cryptographically signed message"""
        # Add metadata
        message["sender"] = f"agent://{self.agent_id}"
        message["timestamp"] = time.time_ns()
        self.sequence_num += 1
        message["sequence_num"] = self.sequence_num

        # Canonical representation
        signed_fields = ["performative", "sender", "receiver", "conversation_id",
                        "content", "citation_ids", "timestamp", "sequence_num"]
        canonical = json.dumps({k: message[k] for k in signed_fields}, sort_keys=True)

        # Sign
        signature_bytes = self.private_key.sign(canonical.encode())

        message["signature"] = {
            "algorithm": "ed25519",
            "public_key": self.get_public_key_string(),
            "signature_bytes": signature_bytes.hex(),
            "signed_fields": signed_fields
        }

        return message

    def verify_message(self, message):
        """Verify message signature and freshness"""
        # Extract signature
        sig_data = message.get("signature")
        if not sig_data:
            raise SecurityError("Message missing signature")

        # Reconstruct canonical message
        canonical = json.dumps({k: message[k] for k in sig_data["signed_fields"]}, sort_keys=True)

        # Verify signature
        public_key_bytes = bytes.fromhex(sig_data["public_key"].split(":")[1])
        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        signature_bytes = bytes.fromhex(sig_data["signature_bytes"])

        try:
            public_key.verify(signature_bytes, canonical.encode())
        except Exception as e:
            raise SecurityError(f"Signature verification failed: {e}")

        # Check replay protection
        sender = message["sender"]
        sequence = message["sequence_num"]

        if sender in self.last_seen_sequences:
            if sequence <= self.last_seen_sequences[sender]:
                raise SecurityError(f"Replay attack: sequence {sequence} already seen from {sender}")

        self.last_seen_sequences[sender] = sequence

        # Check timestamp freshness (5 minute window)
        now = time.time_ns()
        msg_time = message["timestamp"]
        if abs(now - msg_time) > 5 * 60 * 1e9:  # 5 minutes in nanoseconds
            raise SecurityError(f"Message timestamp too old or in future: {msg_time}")

        return True

    def get_public_key_string(self):
        """Export public key as string"""
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return f"ed25519:{public_bytes.hex()}"

    def create_citation(self, claim_id, sources, rationale):
        """Create signed, content-addressed citation"""
        citation = {
            "citation_id": f"if://citation/{uuid4()}",
            "claim_id": claim_id,
            "sources": sources,
            "rationale": rationale,
            "created_by": f"agent://{self.agent_id}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "status": "unverified"
        }

        # Content-address: hash BEFORE signing
        content_hash = sha256(json.dumps(citation, sort_keys=True).encode()).hexdigest()
        citation["content_hash"] = f"sha256:{content_hash}"

        # Sign citation
        canonical = json.dumps(citation, sort_keys=True)
        signature_bytes = self.private_key.sign(canonical.encode())

        citation["signature"] = {
            "algorithm": "ed25519",
            "public_key": self.get_public_key_string(),
            "signature_bytes": signature_bytes.hex()
        }

        return citation

# Usage example
legal_agent = SecureAgent("if.search.legal/1.2.0")
financial_agent = SecureAgent("if.swarm.financial/2.3.1")

# Create signed message
message = {
    "performative": "inform",
    "receiver": ["agent://if.swarm.financial/*"],
    "conversation_id": "epic-2025-11-10-xyz",
    "content": {"claim": "Settlement amount: $520M"},
    "citation_ids": ["cit:9f2b3a1e"]
}

signed_message = legal_agent.sign_message(message)

# Verify message
try:
    financial_agent.verify_message(signed_message)
    print("✅ Message verified - processing")
except SecurityError as e:
    print(f"❌ Message rejected: {e}")
```

---

## Summary

**End-to-End Traceability Achieved Via:**
1. Every message signed (Ed25519) → proves sender identity
2. Every citation content-addressed (SHA-256) → proves content integrity
3. Every update logged (Merkle tree) → proves existence timeline
4. Every conversation threaded (sequence + timestamp) → proves message order
5. IF.witness audits all → governance verification

**Anti-Forgery Achieved Via:**
1. Signatures require private keys (only legitimate agents have them)
2. Content hashes prevent tampering (any change breaks verification)
3. Merkle proofs prevent backdating (immutable append-only log)
4. DDS encryption prevents MITM (transport layer security)
5. CRDT authentication prevents poisoning (signed updates only)

**The Stack:**
```
┌─────────────────────────────────────────┐
│   IF.guard / IF.witness (Governance)    │ ← Audits signatures, rejects forged evidence
├─────────────────────────────────────────┤
│   IF.citation (Evidence Binding)        │ ← Content-addressed + signed citations
├─────────────────────────────────────────┤
│   FIPA-ACL Messages (Signed)            │ ← Ed25519 signatures + sequence numbers
├─────────────────────────────────────────┤
│   CRDT Shared State (Authenticated)     │ ← Signed updates + vector clocks
├─────────────────────────────────────────┤
│   DDS/RTPS Transport (Encrypted)        │ ← AES-256-GCM + PKI authentication
└─────────────────────────────────────────┘
```

**Result:** V3.2.1+ swarm communication is traceable (every message logged), transparent (signatures visible), and trustworthy (cryptographically verified). Forgery is computationally infeasible (Ed25519 256-bit security).

---

**Next Steps:**
1. Review this architecture with user
2. Prototype Phase 1 (message signing) with 2-agent demo
3. Run security audit (external cryptographer review)
4. Implement full stack over 6-week timeline
5. Document in agents.md and COMPONENT-INDEX.md

**Citation for this document:**
```json
{
  "citation_id": "if://citation/swarm-comm-security-2025-11-10",
  "claim_id": "if://claim/v3.2.1-cryptographic-integrity",
  "sources": [
    {"type": "paper", "ref": "docs/SWARM-COMMUNICATION-SECURITY.md", "hash": "sha256:PENDING"},
    {"type": "conversation", "ref": "Project evaluation and review_690fec28.json", "hash": "sha256:PENDING"}
  ],
  "rationale": "Architecture for cryptographically securing swarm agent communication while maintaining IF.TTT compliance",
  "status": "unverified",
  "created_by": "if://agent/claude-sonnet-4.5",
  "created_at": "2025-11-10T00:00:00Z"
}
```

**Last Updated:** 2025-11-10
