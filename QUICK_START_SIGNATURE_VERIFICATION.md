# Signature Verification Middleware - Quick Start Guide

**Citation:** `if://code/signature-verification/2025-11-30`

## Installation

```bash
pip install pynacl
```

## Basic Usage

```python
from src.core.security.signature_verification import SignatureVerifier
import redis

# Initialize verifier
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
verifier = SignatureVerifier(redis_client=redis_client, strict_mode=True)

# Verify a message
result = verifier.verify_incoming_message(message)

if result.valid:
    print(f"Message {result.message_id} authenticated by {result.agent_id}")
    # Process message
else:
    print(f"Verification failed: {result.failure_reason}")
    # Reject message
```

## Key Features

| Feature | Usage |
|---------|-------|
| **Verify single message** | `verifier.verify_incoming_message(msg)` |
| **Verify multiple messages** | `verifier.verify_batch([msg1, msg2, ...])` |
| **Register agent public key** | `verifier.register_agent_public_key(agent_id, public_key)` |
| **Enforce policy** | `verifier.enforce_signature_policy(msg)` |
| **Get audit log** | `verifier.get_verification_audit_log(limit=100)` |

## Verification Modes

### Strict Mode (Production)
```python
# Rejects ALL unsigned messages
verifier = SignatureVerifier(redis_client, strict_mode=True)
# Or: export IF_SIGNATURE_STRICT_MODE=true
```

### Permissive Mode (Development)
```python
# Warns but accepts unsigned messages
verifier = SignatureVerifier(redis_client, strict_mode=False)
# Or: export IF_SIGNATURE_STRICT_MODE=false
```

## Result Status Codes

```python
from src.core.security.signature_verification import VerificationStatus

result = verifier.verify_incoming_message(message)

if result.status == VerificationStatus.VALID:
    print("Message authenticated")
elif result.status == VerificationStatus.INVALID:
    print("Signature verification failed")
elif result.status == VerificationStatus.UNSIGNED:
    print("No signature found")
elif result.status == VerificationStatus.UNKNOWN_AGENT:
    print("Public key not found")
elif result.status == VerificationStatus.REPLAY_ATTACK:
    print("Message too old")
```

## Integration with RedisSwarmCoordinator

```python
class RedisSwarmCoordinator:
    def __init__(self, ...):
        self.redis = redis.Redis(...)
        self.verifier = SignatureVerifier(self.redis, strict_mode=True)

    def get_messages(self, agent_id: str, limit: int = 10):
        verified_messages = []
        for _ in range(limit):
            msg_json = self.redis.lpop(f"messages:{agent_id}")
            if not msg_json:
                break

            msg = json.loads(msg_json)

            # Verify signature
            result = self.verifier.verify_incoming_message(msg)
            if not result.valid:
                logger.warning(f"Discarding invalid message: {result.failure_reason}")
                continue

            verified_messages.append(msg)

        return verified_messages
```

## Registering Agent Keys

```python
from nacl.signing import SigningKey

# Agent generates signing key (typically once)
signing_key = SigningKey.generate()
public_key = signing_key.verify_key.encode()

# Register in verification system
verifier.register_agent_public_key("agent_haiku_abc123", public_key)

# Now messages from this agent can be verified
```

## Batch Verification

```python
# For high-throughput scenarios
messages = [msg1, msg2, msg3, ...]
results = verifier.verify_batch(messages)

valid_messages = [msg for msg, result in zip(messages, results) if result.valid]
invalid_messages = [msg for msg, result in zip(messages, results) if not result.valid]

print(f"Valid: {len(valid_messages)}, Invalid: {len(invalid_messages)}")
```

## Error Handling

```python
from src.core.security.signature_verification import (
    SignatureVerificationException,
    InvalidSignatureException,
    UnknownAgentException,
    ReplayAttackException
)

try:
    result = verifier.verify_incoming_message(message)
    verifier.enforce_signature_policy(message, result)
except InvalidSignatureException:
    logger.error("Signature tampering detected")
except UnknownAgentException:
    logger.error("Unknown sender agent")
except ReplayAttackException:
    logger.error("Message too old (replay attack)")
```

## Performance Tips

```python
# Tip 1: Use batch verification for multiple messages
results = verifier.verify_batch(messages)  # Better than individual loops

# Tip 2: Cache verification results (automatic 60s TTL)
# Duplicate messages verified from cache (<1ms)

# Tip 3: Pre-cache public keys for frequently used agents
# Reduces key lookup time from 5-10ms to <1ms

# Tip 4: Monitor audit log for suspicious activity
audit_log = verifier.get_verification_audit_log(limit=1000)
failures = [e for e in audit_log if not e.get("valid")]
```

## Configuration Parameters

```python
verifier = SignatureVerifier(
    redis_client=redis_client,
    strict_mode=True,                    # Production: reject unsigned
    replay_attack_window=300,             # Max message age (seconds)
    cache_verified_signatures=True,       # Enable result caching
    verification_cache_ttl=60,            # Result cache lifetime
    pubkey_cache_ttl=300,                 # Public key cache lifetime
    enable_local_fallback=True            # Fallback when Redis down
)
```

## Security Events Logged

All events logged to Redis for audit trail:

```
signature_verification_failed    - Invalid signature
missing_signature               - No signature (strict mode)
unknown_agent_public_key        - Public key not found
replay_attack_detected          - Timestamp too old
payload_hash_mismatch           - Message tampering detected
unsigned_message_accepted       - Permissive mode accept
```

Retrieve with:
```python
audit_log = verifier.get_verification_audit_log(limit=100)
for entry in audit_log:
    print(f"{entry['timestamp']}: {entry['event_type']} - {entry['details']}")
```

## Testing

```bash
# Run test suite
pytest /home/setup/infrafabric/tests/security/test_signature_verification.py -v

# Run with coverage
pytest /home/setup/infrafabric/tests/security/test_signature_verification.py --cov=src.core.security
```

## Documentation Files

- **Core Implementation:** `/home/setup/infrafabric/src/core/security/signature_verification.py`
- **Integration Guide:** `/home/setup/infrafabric/docs/SIGNATURE_VERIFICATION_INTEGRATION.md`
- **Test Suite:** `/home/setup/infrafabric/tests/security/test_signature_verification.py`
- **Technical Summary:** `/home/setup/infrafabric/SIGNATURE_VERIFICATION_SUMMARY.md`

## Common Issues

### Issue: "Public key not found for agent"
**Solution:** Register the agent's public key first
```python
verifier.register_agent_public_key(agent_id, public_key)
```

### Issue: "Message too old (replay attack)"
**Solution:** Check message timestamp. Default window is 5 minutes
```python
# Adjust if needed:
verifier = SignatureVerifier(redis_client, replay_attack_window=600)  # 10 minutes
```

### Issue: "Redis unavailable" warnings
**Solution:** Local cache still works. Check Redis connection
```python
# Enable local fallback (default: True)
verifier = SignatureVerifier(redis_client, enable_local_fallback=True)
```

### Issue: Permissive mode not accepting unsigned messages
**Solution:** Check IF_SIGNATURE_STRICT_MODE environment variable
```bash
export IF_SIGNATURE_STRICT_MODE=false
```

## Example: Complete Message Handling

```python
import json
from src.core.security.signature_verification import SignatureVerifier

def handle_incoming_message(message_json: str, verifier: SignatureVerifier):
    """Complete message handling with signature verification"""

    try:
        # Parse message
        message = json.loads(message_json)

        # Verify signature
        result = verifier.verify_incoming_message(message)

        # Check verification result
        if not result.valid:
            logger.error(f"Invalid message: {result.failure_reason}")
            return False

        # Log successful verification
        logger.debug(f"Message {result.message_id} verified (agent: {result.agent_id})")

        # Process authenticated message
        process_message(message)

        return True

    except Exception as e:
        logger.error(f"Message handling error: {e}")
        return False
```

## Next Steps

1. **Install PyNaCl:** `pip install pynacl`
2. **Review Integration Guide:** `/home/setup/infrafabric/docs/SIGNATURE_VERIFICATION_INTEGRATION.md`
3. **Run Tests:** `pytest tests/security/test_signature_verification.py`
4. **Integrate with RedisSwarmCoordinator:** Modify `get_messages()` and `claim_task()`
5. **Register Agent Keys:** Before enabling strict mode
6. **Monitor Audit Log:** Watch for verification failures
7. **Transition to Strict:** Once all agents producing signatures

---

**Citation:** if://code/signature-verification/2025-11-30
**Status:** Production-ready
**Support:** See documentation files listed above
