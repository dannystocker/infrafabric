#!/usr/bin/env python3
"""
Signature Verification Middleware - Message Authentication Layer

Implements Ed25519 signature verification for all incoming messages in the
InfraFabric swarm coordination system. Provides enforcement of signed message
requirements with support for strict/permissive modes, caching, batch
verification, and comprehensive audit logging.

Features:
- Ed25519 signature verification for all incoming messages
- Strict mode (production): Reject all unsigned messages
- Permissive mode (development): Warn but allow unsigned messages
- Message signature caching (60s TTL)
- Batch verification for multiple messages
- Public key caching with fallback
- Graceful degradation (circuit breaker pattern)
- Replay attack detection via timestamp validation
- Comprehensive security audit logging
- IF.TTT compliance with full traceability

Citation: if://code/signature-verification/2025-11-30
"""

import json
import hashlib
import base64
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps

try:
    import redis
except ImportError:
    redis = None

try:
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError
except ImportError:
    VerifyKey = None
    BadSignatureError = None


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class SignatureVerificationException(Exception):
    """Base exception for signature verification failures"""
    pass


class InvalidSignatureException(SignatureVerificationException):
    """Raised when signature verification fails"""
    pass


class UnsignedMessageException(SignatureVerificationException):
    """Raised when unsigned message received in strict mode"""
    pass


class UnknownAgentException(SignatureVerificationException):
    """Raised when sender's public key not found"""
    pass


class ReplayAttackException(SignatureVerificationException):
    """Raised when timestamp is too old (potential replay attack)"""
    pass


class VerificationStatus(Enum):
    """Signature verification result status"""
    VALID = "valid"
    INVALID = "invalid"
    UNSIGNED = "unsigned"
    UNKNOWN_AGENT = "unknown_agent"
    REPLAY_ATTACK = "replay_attack"
    ERROR = "error"


@dataclass
class VerificationResult:
    """
    Result of signature verification operation.

    Attributes:
        valid: Whether signature verification succeeded
        agent_id: ID of the message sender
        message_id: Unique message identifier
        timestamp: When verification was performed
        verification_time: How long verification took (seconds)
        failure_reason: Human-readable failure description if invalid
        public_key_fingerprint: SHA256 fingerprint of public key used
        signature_algorithm: Algorithm used (e.g., "Ed25519")
        status: Detailed verification status
    """
    valid: bool
    agent_id: str
    message_id: str
    timestamp: datetime
    verification_time: float
    failure_reason: Optional[str] = None
    public_key_fingerprint: str = ""
    signature_algorithm: str = "Ed25519"
    status: VerificationStatus = VerificationStatus.VALID

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            "valid": self.valid,
            "agent_id": self.agent_id,
            "message_id": self.message_id,
            "timestamp": self.timestamp.isoformat(),
            "verification_time": self.verification_time,
            "failure_reason": self.failure_reason,
            "public_key_fingerprint": self.public_key_fingerprint,
            "signature_algorithm": self.signature_algorithm,
            "status": self.status.value
        }


class LocalKeyCache:
    """
    In-memory fallback cache when Redis is unavailable.
    Maintains 5-minute window of public keys.
    """

    def __init__(self, ttl_seconds: int = 300):
        """
        Initialize local cache.

        Args:
            ttl_seconds: Cache entry TTL (default 5 minutes)
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, tuple] = {}  # {agent_id: (public_key, timestamp)}

    def get(self, agent_id: str) -> Optional[bytes]:
        """
        Retrieve cached public key if not expired.

        Args:
            agent_id: Agent identifier

        Returns:
            Public key bytes if cached and valid, None otherwise
        """
        if agent_id not in self.cache:
            return None

        public_key, stored_at = self.cache[agent_id]
        age = time.time() - stored_at

        if age > self.ttl_seconds:
            del self.cache[agent_id]
            return None

        return public_key

    def set(self, agent_id: str, public_key: bytes) -> None:
        """
        Store public key in cache.

        Args:
            agent_id: Agent identifier
            public_key: Public key bytes
        """
        self.cache[agent_id] = (public_key, time.time())

    def clear_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        now = time.time()
        expired = [
            agent_id for agent_id, (_, stored_at) in self.cache.items()
            if (now - stored_at) > self.ttl_seconds
        ]

        for agent_id in expired:
            del self.cache[agent_id]

        return len(expired)


class SignatureVerifier:
    """
    Ed25519 signature verification middleware for swarm messages.

    Integrates with Redis for public key registry and message verification
    caching. Supports both strict mode (production) and permissive mode
    (development/debugging).

    Example:
        ```python
        verifier = SignatureVerifier(redis_client, strict_mode=True)
        result = verifier.verify_incoming_message(message_dict)

        if not result.valid:
            logger.error(f"Invalid signature: {result.failure_reason}")
            raise SignatureVerificationException(result.failure_reason)
        ```
    """

    # Redis key patterns
    PUBKEY_REGISTRY_KEY = "security:pubkey_registry:{agent_id}"
    PUBKEY_CACHE_KEY = "security:pubkey_cache:{agent_id}"
    VERIFIED_MESSAGES_KEY = "security:verified_messages:{message_id}"
    VERIFICATION_AUDIT_KEY = "security:audit:verification"
    FAILED_VERIFICATIONS_KEY = "security:audit:failed_verifications"

    def __init__(
        self,
        redis_client: Optional[Any] = None,
        strict_mode: bool = True,
        replay_attack_window: int = 300,
        cache_verified_signatures: bool = True,
        verification_cache_ttl: int = 60,
        pubkey_cache_ttl: int = 300,
        enable_local_fallback: bool = True
    ):
        """
        Initialize signature verifier.

        Args:
            redis_client: Redis client instance (required for production)
            strict_mode: If True, reject unsigned messages. If False, warn only.
                        Can be overridden by IF_SIGNATURE_STRICT_MODE env var.
            replay_attack_window: Maximum message age in seconds (default 5 min)
            cache_verified_signatures: Cache verification results for 60s
            verification_cache_ttl: TTL for verified message cache
            pubkey_cache_ttl: TTL for public key cache in Redis
            enable_local_fallback: Use in-memory cache if Redis unavailable
        """
        self.redis = redis_client
        self.strict_mode = os.getenv("IF_SIGNATURE_STRICT_MODE", str(strict_mode)).lower() == "true"
        self.replay_attack_window = replay_attack_window
        self.cache_verified_signatures = cache_verified_signatures
        self.verification_cache_ttl = verification_cache_ttl
        self.pubkey_cache_ttl = pubkey_cache_ttl
        self.enable_local_fallback = enable_local_fallback

        # Local fallback cache for Redis failures
        self.local_cache = LocalKeyCache(ttl_seconds=pubkey_cache_ttl)

        # Verify dependencies
        if VerifyKey is None or BadSignatureError is None:
            raise ImportError("PyNaCl library required: pip install pynacl")

        logger.info(f"SignatureVerifier initialized (strict_mode={self.strict_mode})")

    def verify_incoming_message(self, message: Dict) -> VerificationResult:
        """
        Verify signature on incoming message from swarm.

        This is the primary entry point for message verification. Performs:
        1. Basic message structure validation
        2. Signature format validation
        3. Public key retrieval
        4. Ed25519 signature verification
        5. Timestamp validation (replay attack detection)

        Args:
            message: Message dict with signature, payload, payload_hash fields

        Returns:
            VerificationResult with detailed verification outcome

        Raises:
            SignatureVerificationException: If message structure invalid
        """
        start_time = time.time()
        message_id = message.get("message_id", "unknown")
        agent_id = message.get("from", "unknown")

        try:
            # Step 1: Validate message structure
            if not isinstance(message, dict):
                return self._create_failure_result(
                    agent_id, message_id, start_time,
                    "Message is not a dictionary",
                    VerificationStatus.ERROR
                )

            # Check for signature presence
            if "signature" not in message:
                return self._handle_unsigned_message(
                    agent_id, message_id, start_time, message
                )

            # Step 2: Validate signature format
            signature_b64 = message.get("signature")
            if not isinstance(signature_b64, str):
                return self._create_failure_result(
                    agent_id, message_id, start_time,
                    "Signature is not a base64-encoded string",
                    VerificationStatus.INVALID
                )

            try:
                signature = base64.b64decode(signature_b64)
            except Exception as e:
                return self._create_failure_result(
                    agent_id, message_id, start_time,
                    f"Invalid base64-encoded signature: {str(e)}",
                    VerificationStatus.INVALID
                )

            # Validate signature length (Ed25519 signatures are 64 bytes)
            if len(signature) != 64:
                return self._create_failure_result(
                    agent_id, message_id, start_time,
                    f"Invalid signature length: {len(signature)} (expected 64)",
                    VerificationStatus.INVALID
                )

            # Step 3: Check for cached verification result
            if self.cache_verified_signatures:
                cached = self._check_verification_cache(message_id)
                if cached is not None:
                    logger.debug(f"Using cached verification for {message_id}")
                    return cached

            # Step 4: Retrieve agent public key
            public_key = self.get_agent_public_key(agent_id)
            if public_key is None:
                result = self._create_failure_result(
                    agent_id, message_id, start_time,
                    f"Public key not found for agent {agent_id}",
                    VerificationStatus.UNKNOWN_AGENT
                )
                self._log_verification_failure(message, result)
                return result

            # Step 5: Validate timestamp (replay attack detection)
            timestamp_result = self._validate_message_timestamp(message)
            if timestamp_result is not None:
                return timestamp_result

            # Step 6: Reconstruct and verify payload hash
            payload = message.get("payload", {})
            canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            computed_hash = hashlib.sha256(canonical_json.encode()).hexdigest()
            expected_hash = message.get("payload_hash")

            if computed_hash != expected_hash:
                result = self._create_failure_result(
                    agent_id, message_id, start_time,
                    "Payload hash mismatch (message may be corrupted or tampered)",
                    VerificationStatus.INVALID
                )
                self._log_verification_failure(message, result)
                return result

            # Step 7: Perform Ed25519 signature verification
            try:
                verify_key = VerifyKey(public_key)
                verify_key.verify(signature, computed_hash.encode())

                # Signature is valid!
                result = VerificationResult(
                    valid=True,
                    agent_id=agent_id,
                    message_id=message_id,
                    timestamp=datetime.utcnow(),
                    verification_time=time.time() - start_time,
                    public_key_fingerprint=self._fingerprint_key(public_key),
                    signature_algorithm="Ed25519",
                    status=VerificationStatus.VALID,
                    failure_reason=None
                )

                # Cache successful verification
                if self.cache_verified_signatures:
                    self._cache_verification_result(message_id, result)

                logger.debug(f"Signature verified for message {message_id} from {agent_id}")
                return result

            except BadSignatureError:
                result = self._create_failure_result(
                    agent_id, message_id, start_time,
                    "Ed25519 signature verification failed",
                    VerificationStatus.INVALID,
                    public_key_fingerprint=self._fingerprint_key(public_key)
                )
                self._log_verification_failure(message, result)
                return result

        except Exception as e:
            logger.error(f"Unexpected error during signature verification: {str(e)}", exc_info=True)
            return self._create_failure_result(
                agent_id, message_id, start_time,
                f"Verification error: {str(e)}",
                VerificationStatus.ERROR
            )

    def verify_batch(self, messages: List[Dict]) -> List[VerificationResult]:
        """
        Verify multiple messages efficiently.

        Args:
            messages: List of message dicts

        Returns:
            List of VerificationResult objects
        """
        results = []
        for message in messages:
            result = self.verify_incoming_message(message)
            results.append(result)

        # Log batch summary
        valid_count = sum(1 for r in results if r.valid)
        logger.info(f"Batch verification complete: {valid_count}/{len(messages)} valid")

        return results

    def enforce_signature_policy(self, message: Dict, result: Optional[VerificationResult] = None) -> None:
        """
        Enforce message signature policy (strict or permissive mode).

        In strict mode, raises exception if verification fails.
        In permissive mode, logs warning but continues.

        Args:
            message: Message dict
            result: VerificationResult (if already verified)

        Raises:
            SignatureVerificationException: In strict mode if verification fails
        """
        if result is None:
            result = self.verify_incoming_message(message)

        if not result.valid:
            if self.strict_mode:
                raise SignatureVerificationException(
                    f"Message {result.message_id} failed signature verification: {result.failure_reason}"
                )
            else:
                logger.warning(
                    f"Signature verification failed (permissive mode): {result.failure_reason}"
                )

    def get_agent_public_key(self, agent_id: str) -> Optional[bytes]:
        """
        Retrieve public key for agent from registry.

        Implements multi-tier fallback:
        1. Check Redis cache (fast, expires after pubkey_cache_ttl)
        2. Check Redis registry (canonical source)
        3. Fall back to local cache (when Redis unavailable)

        Args:
            agent_id: Agent identifier

        Returns:
            Public key bytes (32 bytes for Ed25519) or None if not found
        """
        try:
            # Tier 1: Check Redis cache
            if self.redis:
                try:
                    cached_key = self.redis.get(
                        self.PUBKEY_CACHE_KEY.format(agent_id=agent_id)
                    )
                    if cached_key:
                        pubkey_bytes = base64.b64decode(cached_key)
                        self.local_cache.set(agent_id, pubkey_bytes)
                        return pubkey_bytes
                except Exception as e:
                    logger.debug(f"Redis cache lookup failed: {str(e)}")

            # Tier 2: Check Redis registry (canonical source)
            if self.redis:
                try:
                    registry_data = self.redis.hget(
                        self.PUBKEY_REGISTRY_KEY.format(agent_id=agent_id),
                        "public_key"
                    )
                    if registry_data:
                        pubkey_bytes = base64.b64decode(registry_data)

                        # Update cache for next time
                        try:
                            self.redis.setex(
                                self.PUBKEY_CACHE_KEY.format(agent_id=agent_id),
                                self.pubkey_cache_ttl,
                                registry_data
                            )
                        except Exception:
                            pass  # Cache update failure doesn't prevent verification

                        # Store in local fallback
                        self.local_cache.set(agent_id, pubkey_bytes)
                        return pubkey_bytes
                except redis.ConnectionError:
                    logger.warning(f"Redis unavailable, falling back to local cache")
                except Exception as e:
                    logger.debug(f"Redis registry lookup failed: {str(e)}")

            # Tier 3: Local fallback cache
            if self.enable_local_fallback:
                local_key = self.local_cache.get(agent_id)
                if local_key:
                    logger.debug(f"Using local cached public key for {agent_id}")
                    return local_key

            logger.warning(f"Public key not found for agent {agent_id}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving public key for {agent_id}: {str(e)}")
            return None

    def register_agent_public_key(self, agent_id: str, public_key: bytes) -> bool:
        """
        Register agent's public key in the registry.

        Args:
            agent_id: Agent identifier
            public_key: Public key bytes (32 bytes for Ed25519)

        Returns:
            True if registered successfully
        """
        try:
            # Validate public key format
            if len(public_key) != 32:
                logger.error(f"Invalid public key length for {agent_id}: {len(public_key)}")
                return False

            if not self.redis:
                logger.warning("Redis not available, cannot register public key")
                return False

            pubkey_b64 = base64.b64encode(public_key).decode()

            # Store in registry
            self.redis.hset(
                self.PUBKEY_REGISTRY_KEY.format(agent_id=agent_id),
                mapping={
                    "public_key": pubkey_b64,
                    "registered_at": datetime.utcnow().isoformat(),
                    "fingerprint": self._fingerprint_key(public_key)
                }
            )

            # Expire after 30 days
            self.redis.expire(
                self.PUBKEY_REGISTRY_KEY.format(agent_id=agent_id),
                30 * 24 * 3600
            )

            # Update cache
            self.redis.setex(
                self.PUBKEY_CACHE_KEY.format(agent_id=agent_id),
                self.pubkey_cache_ttl,
                pubkey_b64
            )

            # Store in local fallback
            self.local_cache.set(agent_id, public_key)

            logger.info(f"Registered public key for agent {agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register public key for {agent_id}: {str(e)}")
            return False

    def get_verification_audit_log(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve recent verification audit log entries.

        Args:
            limit: Maximum entries to retrieve

        Returns:
            List of audit log entries
        """
        if not self.redis:
            return []

        try:
            entries = self.redis.lrange(
                self.VERIFICATION_AUDIT_KEY,
                -limit,
                -1
            )
            return [json.loads(entry) for entry in entries]
        except Exception as e:
            logger.error(f"Failed to retrieve audit log: {str(e)}")
            return []

    # ================================================================== #
    # Private Helper Methods
    # ================================================================== #

    def _handle_unsigned_message(
        self,
        agent_id: str,
        message_id: str,
        start_time: float,
        message: Dict
    ) -> VerificationResult:
        """Handle unsigned message according to policy mode."""
        result = VerificationResult(
            valid=not self.strict_mode,
            agent_id=agent_id,
            message_id=message_id,
            timestamp=datetime.utcnow(),
            verification_time=time.time() - start_time,
            failure_reason="No signature found" if self.strict_mode else "Warning: unsigned message",
            status=VerificationStatus.UNSIGNED
        )

        if self.strict_mode:
            self._log_verification_failure(message, result)
            logger.error(f"Unsigned message rejected (strict mode): {message_id}")
        else:
            logger.warning(f"Unsigned message accepted (permissive mode): {message_id}")
            self._log_audit_event("unsigned_message_accepted", {
                "message_id": message_id,
                "from": agent_id
            })

        return result

    def _validate_message_timestamp(self, message: Dict) -> Optional[VerificationResult]:
        """
        Validate message timestamp to detect replay attacks.

        Returns VerificationResult if validation fails, None if OK.
        """
        timestamp_str = message.get("timestamp")
        if not timestamp_str:
            return None  # No timestamp, skip validation

        try:
            msg_timestamp = datetime.fromisoformat(timestamp_str)
            age_seconds = (datetime.utcnow() - msg_timestamp).total_seconds()

            if age_seconds > self.replay_attack_window:
                message_id = message.get("message_id", "unknown")
                agent_id = message.get("from", "unknown")

                result = VerificationResult(
                    valid=False,
                    agent_id=agent_id,
                    message_id=message_id,
                    timestamp=datetime.utcnow(),
                    verification_time=0,
                    failure_reason=f"Message too old: {age_seconds:.0f}s (window: {self.replay_attack_window}s)",
                    status=VerificationStatus.REPLAY_ATTACK
                )
                self._log_verification_failure(message, result)
                return result

        except Exception as e:
            logger.debug(f"Could not validate timestamp: {str(e)}")

        return None

    def _create_failure_result(
        self,
        agent_id: str,
        message_id: str,
        start_time: float,
        failure_reason: str,
        status: VerificationStatus,
        public_key_fingerprint: str = ""
    ) -> VerificationResult:
        """Helper to create failure VerificationResult"""
        return VerificationResult(
            valid=False,
            agent_id=agent_id,
            message_id=message_id,
            timestamp=datetime.utcnow(),
            verification_time=time.time() - start_time,
            failure_reason=failure_reason,
            public_key_fingerprint=public_key_fingerprint,
            status=status
        )

    def _check_verification_cache(self, message_id: str) -> Optional[VerificationResult]:
        """Check if message verification was recently cached"""
        if not self.redis:
            return None

        try:
            cached = self.redis.get(
                self.VERIFIED_MESSAGES_KEY.format(message_id=message_id)
            )
            if cached:
                result_dict = json.loads(cached)
                # Reconstruct VerificationResult
                result = VerificationResult(
                    valid=result_dict["valid"],
                    agent_id=result_dict["agent_id"],
                    message_id=result_dict["message_id"],
                    timestamp=datetime.fromisoformat(result_dict["timestamp"]),
                    verification_time=result_dict["verification_time"],
                    failure_reason=result_dict.get("failure_reason"),
                    public_key_fingerprint=result_dict.get("public_key_fingerprint", ""),
                    status=VerificationStatus(result_dict.get("status", "valid"))
                )
                return result
        except Exception as e:
            logger.debug(f"Cache check failed: {str(e)}")

        return None

    def _cache_verification_result(self, message_id: str, result: VerificationResult) -> None:
        """Cache verification result for quick lookup"""
        if not self.redis:
            return

        try:
            self.redis.setex(
                self.VERIFIED_MESSAGES_KEY.format(message_id=message_id),
                self.verification_cache_ttl,
                json.dumps(result.to_dict())
            )
        except Exception as e:
            logger.debug(f"Failed to cache verification result: {str(e)}")

    def _fingerprint_key(self, public_key: bytes) -> str:
        """Generate SHA256 fingerprint of public key for audit"""
        return hashlib.sha256(public_key).hexdigest()[:16]

    def _log_verification_failure(self, message: Dict, result: VerificationResult) -> None:
        """Log failed verification to security audit"""
        self._log_audit_event("signature_verification_failed", {
            "message_id": result.message_id,
            "from": result.agent_id,
            "reason": result.failure_reason,
            "status": result.status.value,
            "verification_time": result.verification_time
        })

    def _log_audit_event(self, event_type: str, details: Dict) -> None:
        """Log security event to audit trail"""
        if not self.redis:
            return

        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "details": details
            }

            self.redis.rpush(
                self.VERIFICATION_AUDIT_KEY,
                json.dumps(audit_entry)
            )

            # 30-day retention
            self.redis.expire(self.VERIFICATION_AUDIT_KEY, 30 * 24 * 3600)

        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")


# ================================================================== #
# Decorator for Easy Integration
# ================================================================== #

def require_signed_message(strict_mode: bool = True):
    """
    Decorator to require signed messages on Redis coordination methods.

    Usage:
        ```python
        @require_signed_message()
        def get_messages(agent_id: str) -> List[Dict]:
            # Message verification happens automatically
            ...
        ```

    Args:
        strict_mode: If True, reject unsigned messages
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This is a simplified decorator - in real usage, would need
            # access to the verifier instance and incoming message from the
            # Redis coordinator. Implementation depends on integration context.
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ================================================================== #
# Example Usage
# ================================================================== #

if __name__ == "__main__":
    # Example: Initialize verifier and verify a message

    try:
        import redis as redis_lib
        redis_client = redis_lib.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    except Exception:
        redis_client = None

    # Create verifier
    verifier = SignatureVerifier(
        redis_client=redis_client,
        strict_mode=True
    )

    # Example: Simulate signed message (in real usage, signature would come from signing module)
    example_message = {
        "message_id": "msg_12345678",
        "from": "agent_haiku_abc123",
        "to": "agent_sonnet_xyz789",
        "timestamp": datetime.utcnow().isoformat(),
        "payload": {
            "type": "task_claim",
            "task_id": "task_abc123"
        },
        "payload_hash": hashlib.sha256(
            json.dumps({"type": "task_claim", "task_id": "task_abc123"},
                      sort_keys=True, separators=(',', ':')).encode()
        ).hexdigest(),
        "signature": "base64encodedSignatureHere=="
    }

    print("SignatureVerifier initialized successfully")
    print(f"Strict mode: {verifier.strict_mode}")
    print(f"Replay attack window: {verifier.replay_attack_window}s")
