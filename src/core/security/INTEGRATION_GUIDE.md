# Ed25519 Identity System Integration Guide

**Status:** Implementation Complete - Ready for RedisSwarmCoordinator Integration
**Document ID:** if://code/ed25519-identity-integration/2025-11-30
**Threat Model Reference:** if://doc/if-emotion-threat-model/2025-11-30 (Threat 6: Identity Spoofing)

---

## Overview

The Ed25519 identity system provides cryptographic agent authentication for the InfraFabric swarm coordination infrastructure. It addresses THREAT 6 (Identity Spoofing) from the IF.emotion threat model with a critical impact rating.

**Key Properties:**
- Ed25519 digital signatures (64-byte signatures on 32-byte keys)
- Private keys encrypted at rest (Fernet AES-128-CBC)
- Public key storage in Redis for verification
- PBKDF2-derived encryption keys (100,000 iterations)
- Key rotation support + expiry tracking

---

## Integration with RedisSwarmCoordinator

### Step 1: Modify `register_agent()` Method

Update `/home/setup/infrafabric/src/core/logistics/redis_swarm_coordinator.py`:

```python
from src.core.security.ed25519_identity import create_agent_identity_for_registration

def register_agent(self,
                  role: str,
                  context_capacity: int = 200000,
                  parent_id: Optional[str] = None,
                  metadata: Optional[Dict] = None,
                  generate_keys: bool = True) -> str:
    """
    Register a new agent in the swarm with cryptographic identity.

    Args:
        role: Agent role (sonnet_coordinator, haiku_worker, etc.)
        context_capacity: Token capacity (default 200K for Haiku)
        parent_id: If spawned by another agent, specify parent agent_id
        metadata: Additional metadata (model, specialization, etc.)
        generate_keys: If True, generate Ed25519 keypair automatically

    Returns:
        agent_id: Unique identifier for this agent
    """
    agent_id = f"{role}_{uuid.uuid4().hex[:8]}"

    # Generate cryptographic identity if enabled
    if generate_keys:
        identity = create_agent_identity_for_registration(
            agent_id=agent_id,
            role=role,
            auto_generate=True  # Requires IF_AGENT_KEY_PASSPHRASE env var
        )

        # Export public key for Redis storage
        public_key_b64 = identity.export_public_key_base64()

        # Store public key in Redis
        self.redis.hset(
            f"agents:{agent_id}:keys",
            mapping={
                "public_key": public_key_b64,
                "key_version": identity.metadata.key_version,
                "fingerprint": identity.metadata.fingerprint,
                "expires_at": identity.metadata.expires_at,
                "algorithm": "Ed25519"
            }
        )

    # ... rest of register_agent() implementation ...
    agent_data = {
        "agent_id": agent_id,
        "role": role,
        "context_capacity": context_capacity,
        "parent_id": parent_id or "none",
        "registered_at": datetime.now().isoformat(),
        "metadata": json.dumps(metadata or {})
    }

    self.redis.hset(f"agents:{agent_id}", mapping=agent_data)
    self.redis.set(f"agents:{agent_id}:heartbeat", time.time(), ex=300)

    # ... rest of register_agent() implementation ...
```

### Step 2: Add Message Signing to `send_message()`

```python
from src.core.security.ed25519_identity import AgentIdentity
import base64

def send_message(self, to_agent_id: str, message: Dict) -> str:
    """
    Send digitally signed message to another agent.

    Message includes Ed25519 signature for authentication.
    """
    message_id = f"msg_{uuid.uuid4().hex[:8]}"
    message_bytes = json.dumps(message).encode('utf-8')

    # Sign message if agent has private key
    signature_b64 = None
    if hasattr(self, 'agent_identity') and self.agent_identity:
        try:
            signature = self.agent_identity.sign_message(message_bytes)
            signature_b64 = base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            logger.warning(f"Failed to sign message: {e}")

    message_data = {
        "message_id": message_id,
        "from": self.agent_id or "unknown",
        "to": to_agent_id,
        "timestamp": datetime.now().isoformat(),
        "content": json.dumps(message),
        "signature": signature_b64,  # Ed25519 signature (base64)
        "key_fingerprint": (
            self.agent_identity.metadata.fingerprint
            if hasattr(self, 'agent_identity') else None
        )
    }

    self.redis.rpush(f"messages:{to_agent_id}", json.dumps(message_data))

    # Publish notification
    self.redis.publish(f"channel:agent:{to_agent_id}", json.dumps({
        "type": "new_message",
        "message_id": message_id,
        "from": self.agent_id,
        "signed": signature_b64 is not None
    }))

    logger.info(f"Sent signed message {message_id} to {to_agent_id}")
    return message_id
```

### Step 3: Add Message Verification to `get_messages()`

```python
def get_messages(self, agent_id: Optional[str] = None, limit: int = 10,
                verify_signatures: bool = True) -> List[Dict]:
    """Retrieve and optionally verify signed messages for an agent."""
    agent_id = agent_id or self.agent_id
    if not agent_id:
        raise ValueError("No agent_id specified")

    messages = []
    for _ in range(limit):
        msg_json = self.redis.lpop(f"messages:{agent_id}")
        if not msg_json:
            break

        msg = json.loads(msg_json)
        msg["content"] = json.loads(msg["content"])

        # Verify signature if present
        if verify_signatures and msg.get("signature"):
            from_agent_id = msg.get("from")
            public_key_b64 = self.redis.hget(
                f"agents:{from_agent_id}:keys",
                "public_key"
            )

            if public_key_b64:
                try:
                    public_key = base64.b64decode(public_key_b64)
                    signature = base64.b64decode(msg["signature"])
                    message_bytes = json.dumps(msg["content"]).encode('utf-8')

                    is_valid = AgentIdentity.verify_signature(
                        public_key=public_key,
                        signature=signature,
                        message=message_bytes
                    )

                    msg["signature_valid"] = is_valid

                    if not is_valid:
                        logger.warning(
                            f"Message {msg.get('message_id')} from {from_agent_id} "
                            f"has INVALID signature"
                        )
                except Exception as e:
                    logger.error(f"Signature verification error: {e}")
                    msg["signature_valid"] = False

        messages.append(msg)

    return messages
```

---

## Environment Configuration

### Required Environment Variable

Set before starting any agents:

```bash
export IF_AGENT_KEY_PASSPHRASE="your-secure-passphrase-32-chars-minimum"
```

### Key Storage Location

Private keys stored at: `/home/setup/infrafabric/keys/`

Each agent gets a file: `{agent_id}.priv.enc`

**Permissions:**
- Private key files: 0600 (owner read/write only)
- Key directory: 0700 (owner only)

---

## Redis Schema for Agent Keys

### Key Storage

```
agents:{agent_id}:keys
├── public_key          → Base64-encoded 32-byte Ed25519 public key
├── key_version         → Integer version (starts at 1)
├── fingerprint         → SHA-256 of public key (for quick comparison)
├── expires_at          → ISO8601 expiry timestamp
└── algorithm           → "Ed25519"
```

### Example

```redis
HGETALL agents:haiku_worker_a1b2c3d4:keys
1) "public_key"
2) "KBHMeCDDwhlW4XgIzIrmbtXE5UuG/injNxb8K..."
3) "key_version"
4) "1"
5) "fingerprint"
6) "2acd0ab67b305d1e26cb77ab1744564d0f2c429f..."
7) "expires_at"
8) "2026-02-28T19:27:24.148680+00:00"
9) "algorithm"
10) "Ed25519"
```

---

## Security Checklist

- [ ] `IF_AGENT_KEY_PASSPHRASE` set in environment
- [ ] Key directory `/home/setup/infrafabric/keys/` has 0700 permissions
- [ ] Private key files have 0600 permissions
- [ ] Public keys stored in Redis (distribution only, never encrypted)
- [ ] Message signing integrated into `send_message()`
- [ ] Message verification integrated into `get_messages()`
- [ ] Audit logging enabled for all key operations
- [ ] Key rotation procedure documented and tested
- [ ] 30-day pre-expiry warnings configured

---

## Key Rotation Procedure

### Manual Key Rotation

```python
from src.core.security.ed25519_identity import AgentIdentity

# Load existing key
identity = AgentIdentity("haiku_worker_a1b2c3d4")
identity.load_private_key("old_passphrase")

# Rotate to new key (generates new keypair)
new_priv_key, new_pub_key = identity.rotate_key("new_passphrase")

# Update Redis with new public key
public_key_b64 = identity.export_public_key_base64()
redis_client.hset(
    f"agents:haiku_worker_a1b2c3d4:keys",
    mapping={
        "public_key": public_key_b64,
        "key_version": identity.metadata.key_version,
        "expires_at": identity.metadata.expires_at
    }
)

logger.info(f"Key rotated to version {identity.metadata.key_version}")
```

### Automated Key Rotation (Future)

Planned addition: Automatic key rotation 30 days before expiry

---

## Threat Model Compliance

### Threat 6: Identity Spoofing

**Scenario:**
```
Attacker impersonates IF.emotion agent by spoofing response signatures.
Legitimate users believe they're talking to verified system.
```

**Mitigation via Ed25519:**
1. Every response signed with agent's Ed25519 private key
2. Public key distributed via Redis + secure channels
3. Users verify signature: `verify_signature(public_key, signature, response)`
4. Forged responses fail verification (signature mismatch)
5. Spoofed systems lack access to private key (impossible to forge signatures)

**Residual Risk:**
- Medium-low if public key distribution is secure
- Requires secure channel for public key distribution
- Users must verify key fingerprint independently

---

## Testing

### Unit Tests

Run validation suite:

```bash
python3 /home/setup/infrafabric/src/core/security/ed25519_identity.py
```

Expected output:
```
======================================================================
Ed25519 Agent Identity System - Demonstration
======================================================================

[1] Creating AgentIdentity instance...
    ✓ Created identity for demo_haiku_worker

[2] Generating Ed25519 keypair...
    ✓ Generated keypair: 32 byte private, 32 byte public

... (all tests pass)

[10] Testing with tampered signature (should fail)...
    ✓ Tampered signature verification: False (expected: False)

======================================================================
✓ Demonstration complete!
======================================================================
```

### Integration Test

Test with RedisSwarmCoordinator (after integration):

```python
from src.core.logistics.redis_swarm_coordinator import RedisSwarmCoordinator

# Initialize coordinator
coordinator = RedisSwarmCoordinator()

# Register agent with key generation
agent_id = coordinator.register_agent(
    role="haiku_worker",
    generate_keys=True  # Auto-generate keypair
)

# Verify keys in Redis
keys = coordinator.redis.hgetall(f"agents:{agent_id}:keys")
assert "public_key" in keys
assert "fingerprint" in keys
assert "expires_at" in keys

print(f"✓ Agent {agent_id} registered with cryptographic identity")
```

---

## API Reference

### AgentIdentity Class

```python
class AgentIdentity:
    """Main class for agent identity management."""

    def __init__(agent_id: str, key_store_path: Optional[str] = None)
    def generate_keypair() -> Tuple[bytes, bytes]
    def save_private_key(private_key: bytes, passphrase: str, key_version: int = 1) -> str
    def load_private_key(passphrase: str) -> bytes
    def get_public_key() -> bytes
    def export_public_key_base64() -> str
    def sign_message(message: bytes) -> bytes
    def verify_signature(public_key: bytes, signature: bytes, message: bytes) -> bool  # static
    def get_key_metadata() -> Optional[KeyMetadata]
    def check_expiry_warning(warning_days: int = 30) -> Optional[str]
    def rotate_key(passphrase: str) -> Tuple[bytes, bytes]
```

### KeyMetadata Dataclass

```python
@dataclass
class KeyMetadata:
    agent_id: str                      # Agent identifier
    public_key_b64: str                # Base64-encoded public key
    generated_at: str                  # ISO8601 timestamp
    expires_at: Optional[str]          # ISO8601 expiry timestamp
    key_version: int = 1               # Version for rotation tracking
    algorithm: str = "Ed25519"         # Signature algorithm
    fingerprint: Optional[str] = None  # SHA-256 hash of public key
```

---

## Troubleshooting

### Problem: "IF_AGENT_KEY_PASSPHRASE not set"

**Solution:** Set environment variable before running agents:
```bash
export IF_AGENT_KEY_PASSPHRASE="your-secure-passphrase"
```

### Problem: "Key file has insecure permissions"

**Solution:** Reset key directory:
```bash
chmod 700 /home/setup/infrafabric/keys
chmod 600 /home/setup/infrafabric/keys/*.priv.enc
```

### Problem: "Failed to decrypt private key"

**Cause:** Wrong passphrase
**Solution:** Verify IF_AGENT_KEY_PASSPHRASE matches original

### Problem: "Key expired"

**Solution:** Rotate to new key:
```python
identity.rotate_key("passphrase")
```

---

## Future Enhancements

1. **Hardware Security Module (HSM) Integration**
   - Store private keys in FIPS-certified HSM
   - Signing operations on HSM (private key never in RAM)

2. **Certificate-Based Distribution**
   - X.509 certificates for public key distribution
   - Certificate revocation lists (CRL)

3. **Key Escrow for Backup**
   - Secure backup of agent private keys
   - Recovery procedures for key loss

4. **Automated Key Rotation**
   - Scheduled rotation (e.g., every 90 days)
   - Pre-rotation notifications (30 days before)

5. **Multi-Signature Support**
   - Require multiple agents to authorize actions
   - Distributed decision-making verification

---

## References

- **Threat Model:** if://doc/if-emotion-threat-model/2025-11-30
- **Implementation:** if://code/ed25519-identity/2025-11-30
- **Cryptography Library:** https://cryptography.io/
- **Ed25519 Spec:** RFC 8032
- **PBKDF2:** RFC 2898 / NIST SP 800-132

---

**Document Status:** COMPLETE
**Generated:** 2025-11-30
**IF.TTT Compliance:** Cryptographic signatures + audit trail tracking
