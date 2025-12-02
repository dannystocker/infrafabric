#!/usr/bin/env python3
"""
Unit tests for SignatureVerifier middleware.

Tests the Ed25519 signature verification implementation across:
- Valid signed messages
- Unsigned messages (strict/permissive modes)
- Invalid signatures
- Replay attacks
- Unknown agents
- Batch verification
- Public key caching
- Verification result caching

Citation: if://code/signature-verification/2025-11-30
"""

import pytest
import json
import hashlib
import base64
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import module under test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.security.signature_verification import (
    SignatureVerifier,
    VerificationResult,
    VerificationStatus,
    InvalidSignatureException,
    UnsignedMessageException,
    UnknownAgentException,
    ReplayAttackException,
    LocalKeyCache
)

try:
    from nacl.signing import SigningKey
    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False


@pytest.mark.skipif(not NACL_AVAILABLE, reason="PyNaCl not installed")
class TestSignatureVerification:
    """Test suite for Ed25519 signature verification"""

    @pytest.fixture
    def verifier(self):
        """Create verifier instance without Redis"""
        return SignatureVerifier(redis_client=None, strict_mode=True)

    @pytest.fixture
    def verifier_permissive(self):
        """Create verifier in permissive mode"""
        return SignatureVerifier(redis_client=None, strict_mode=False)

    @pytest.fixture
    def signing_key(self):
        """Generate test signing key"""
        return SigningKey.generate()

    @pytest.fixture
    def test_public_key(self, signing_key):
        """Get public key from signing key"""
        return signing_key.verify_key.encode()

    def create_signed_message(self, signing_key, agent_id: str = "test_agent"):
        """Helper to create a properly signed test message"""
        payload = {
            "type": "task_claim",
            "task_id": "task_12345",
            "priority": 1
        }

        # Create canonical hash
        canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        payload_hash = hashlib.sha256(canonical_json.encode()).hexdigest()

        # Sign the hash
        signature = signing_key.sign(payload_hash.encode()).signature

        # Create message
        message = {
            "message_id": "msg_test_12345",
            "from": agent_id,
            "to": "agent_coordinator",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
            "payload_hash": payload_hash,
            "signature": base64.b64encode(signature).decode()
        }

        return message

    # ================================================================== #
    # Test 1: Valid Signed Messages
    # ================================================================== #

    def test_valid_signed_message(self, verifier, signing_key, test_public_key):
        """Test verification of properly signed message"""
        # Register public key in local cache
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        # Create signed message
        message = self.create_signed_message(signing_key, agent_id)

        # Verify
        result = verifier.verify_incoming_message(message)

        assert result.valid is True
        assert result.status == VerificationStatus.VALID
        assert result.agent_id == agent_id
        assert result.message_id == "msg_test_12345"
        assert result.failure_reason is None
        assert result.verification_time > 0
        assert len(result.public_key_fingerprint) == 16

    def test_valid_signed_message_result_serialization(self, verifier, signing_key, test_public_key):
        """Test VerificationResult can be serialized to dict"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        message = self.create_signed_message(signing_key, agent_id)
        result = verifier.verify_incoming_message(message)

        # Verify serialization
        result_dict = result.to_dict()
        assert result_dict["valid"] is True
        assert result_dict["status"] == "valid"
        assert "timestamp" in result_dict
        assert "verification_time" in result_dict

    # ================================================================== #
    # Test 2: Unsigned Messages
    # ================================================================== #

    def test_unsigned_message_strict_mode(self, verifier):
        """Test unsigned message rejection in strict mode"""
        message = {
            "message_id": "msg_unsigned",
            "from": "test_agent",
            "to": "coordinator",
            "payload": {"task": "test"}
        }

        result = verifier.verify_incoming_message(message)

        assert result.valid is False
        assert result.status == VerificationStatus.UNSIGNED
        assert "No signature" in result.failure_reason

    def test_unsigned_message_permissive_mode(self, verifier_permissive):
        """Test unsigned message acceptance in permissive mode"""
        message = {
            "message_id": "msg_unsigned",
            "from": "test_agent",
            "payload": {"task": "test"}
        }

        result = verifier_permissive.verify_incoming_message(message)

        assert result.valid is True  # Accepted in permissive mode
        assert result.status == VerificationStatus.UNSIGNED

    def test_enforce_signature_policy_strict(self, verifier):
        """Test policy enforcement in strict mode"""
        message = {
            "message_id": "msg_unsigned",
            "from": "test_agent",
            "payload": {"task": "test"}
        }

        with pytest.raises(Exception):  # Should raise exception
            verifier.enforce_signature_policy(message)

    def test_enforce_signature_policy_permissive(self, verifier_permissive):
        """Test policy enforcement in permissive mode"""
        message = {
            "message_id": "msg_unsigned",
            "from": "test_agent",
            "payload": {"task": "test"}
        }

        # Should not raise exception
        verifier_permissive.enforce_signature_policy(message)

    # ================================================================== #
    # Test 3: Invalid Signatures
    # ================================================================== #

    def test_invalid_signature_tampering(self, verifier, signing_key, test_public_key):
        """Test detection of tampered signature"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        message = self.create_signed_message(signing_key, agent_id)

        # Tamper with signature by changing one byte
        sig_bytes = base64.b64decode(message["signature"])
        tampered_sig = bytes([sig_bytes[0] ^ 0xFF]) + sig_bytes[1:]
        message["signature"] = base64.b64encode(tampered_sig).decode()

        result = verifier.verify_incoming_message(message)

        assert result.valid is False
        assert result.status == VerificationStatus.INVALID

    def test_invalid_signature_base64(self, verifier):
        """Test detection of invalid base64 signature"""
        message = {
            "message_id": "msg_invalid_base64",
            "from": "test_agent",
            "payload": {"task": "test"},
            "signature": "not-valid-base64!!!"
        }

        result = verifier.verify_incoming_message(message)

        assert result.valid is False
        assert result.status == VerificationStatus.INVALID
        assert "base64" in result.failure_reason.lower()

    def test_invalid_signature_length(self, verifier):
        """Test detection of wrong signature length"""
        message = {
            "message_id": "msg_short_sig",
            "from": "test_agent",
            "payload": {"task": "test"},
            "signature": base64.b64encode(b"tooshort").decode()
        }

        result = verifier.verify_incoming_message(message)

        assert result.valid is False
        assert result.status == VerificationStatus.INVALID
        assert "length" in result.failure_reason.lower()

    def test_payload_hash_mismatch(self, verifier, signing_key, test_public_key):
        """Test detection of payload hash mismatch"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        message = self.create_signed_message(signing_key, agent_id)

        # Tamper with payload but not hash
        message["payload"]["task_id"] = "task_modified"

        result = verifier.verify_incoming_message(message)

        assert result.valid is False
        assert result.status == VerificationStatus.INVALID

    # ================================================================== #
    # Test 4: Replay Attack Detection
    # ================================================================== #

    def test_replay_attack_old_message(self, verifier, signing_key, test_public_key):
        """Test detection of old timestamp (replay attack)"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        message = self.create_signed_message(signing_key, agent_id)

        # Set timestamp to 1 hour ago
        message["timestamp"] = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        result = verifier.verify_incoming_message(message)

        assert result.valid is False
        assert result.status == VerificationStatus.REPLAY_ATTACK
        assert "old" in result.failure_reason.lower()

    def test_timestamp_within_window(self, verifier, signing_key, test_public_key):
        """Test that recent messages pass timestamp validation"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        message = self.create_signed_message(signing_key, agent_id)

        # Set timestamp to 1 minute ago (within 5-minute window)
        message["timestamp"] = (datetime.utcnow() - timedelta(minutes=1)).isoformat()

        result = verifier.verify_incoming_message(message)

        # Should pass signature verification (timestamp OK)
        assert result.status == VerificationStatus.VALID

    # ================================================================== #
    # Test 5: Unknown Agent
    # ================================================================== #

    def test_unknown_agent_public_key(self, verifier, signing_key):
        """Test detection of unknown agent (missing public key)"""
        message = self.create_signed_message(signing_key, "unknown_agent")

        result = verifier.verify_incoming_message(message)

        assert result.valid is False
        assert result.status == VerificationStatus.UNKNOWN_AGENT
        assert "not found" in result.failure_reason.lower()

    # ================================================================== #
    # Test 6: Batch Verification
    # ================================================================== #

    def test_batch_verification(self, verifier, signing_key, test_public_key):
        """Test batch verification of multiple messages"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        # Create 5 valid messages
        messages = [
            self.create_signed_message(signing_key, agent_id)
            for _ in range(5)
        ]

        results = verifier.verify_batch(messages)

        assert len(results) == 5
        assert all(r.valid for r in results)
        assert all(r.status == VerificationStatus.VALID for r in results)

    def test_batch_verification_mixed(self, verifier, signing_key, test_public_key):
        """Test batch verification with mixed valid/invalid messages"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        # Create 3 valid, 2 invalid messages
        valid_msgs = [self.create_signed_message(signing_key, agent_id) for _ in range(3)]
        invalid_msgs = [{"message_id": f"msg_invalid_{i}", "from": "test_agent"} for i in range(2)]

        messages = valid_msgs + invalid_msgs

        results = verifier.verify_batch(messages)

        assert len(results) == 5
        valid_count = sum(1 for r in results if r.valid)
        assert valid_count == 3

    # ================================================================== #
    # Test 7: Public Key Caching
    # ================================================================== #

    def test_local_key_cache_get_set(self, verifier, test_public_key):
        """Test local key cache get/set operations"""
        agent_id = "test_agent"

        # Set key
        verifier.local_cache.set(agent_id, test_public_key)

        # Get key
        cached_key = verifier.local_cache.get(agent_id)

        assert cached_key == test_public_key

    def test_local_key_cache_expiration(self):
        """Test local key cache expiration"""
        cache = LocalKeyCache(ttl_seconds=1)
        key = b"test_key"

        cache.set("agent", key)
        assert cache.get("agent") == key

        # Wait for expiration
        import time
        time.sleep(1.1)

        assert cache.get("agent") is None

    def test_local_key_cache_clear_expired(self):
        """Test clearing expired cache entries"""
        cache = LocalKeyCache(ttl_seconds=1)

        cache.set("agent1", b"key1")
        cache.set("agent2", b"key2")

        assert len(cache.cache) == 2

        import time
        time.sleep(1.1)

        removed = cache.clear_expired()
        assert removed == 2
        assert len(cache.cache) == 0

    # ================================================================== #
    # Test 8: Message Structure Validation
    # ================================================================== #

    def test_invalid_message_not_dict(self, verifier):
        """Test handling of non-dict message"""
        result = verifier.verify_incoming_message("not a dict")
        assert result.valid is False
        assert result.status == VerificationStatus.ERROR

    def test_invalid_message_signature_not_string(self, verifier):
        """Test handling of non-string signature"""
        message = {
            "message_id": "msg_test",
            "from": "test_agent",
            "signature": 12345  # Not a string
        }

        result = verifier.verify_incoming_message(message)
        assert result.valid is False

    # ================================================================== #
    # Test 9: Fingerprinting
    # ================================================================== #

    def test_public_key_fingerprint_generation(self, verifier, test_public_key):
        """Test SHA256 fingerprint generation"""
        fingerprint = verifier._fingerprint_key(test_public_key)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 16  # First 16 chars of SHA256 hex
        assert all(c in '0123456789abcdef' for c in fingerprint)

    # ================================================================== #
    # Test 10: Integration with Message Flow
    # ================================================================== #

    def test_message_flow_valid_to_processing(self, verifier, signing_key, test_public_key):
        """Test complete message flow from receipt to processing"""
        agent_id = "test_agent"
        verifier.local_cache.set(agent_id, test_public_key)

        message = self.create_signed_message(signing_key, agent_id)

        # Simulate message handling
        result = verifier.verify_incoming_message(message)

        if result.valid:
            # Process verified message
            processed_task_id = message["payload"]["task_id"]
            assert processed_task_id == "task_12345"
        else:
            pytest.fail("Message should be valid")


class TestVerificationResult:
    """Test VerificationResult dataclass"""

    def test_verification_result_to_dict(self):
        """Test VerificationResult serialization"""
        now = datetime.utcnow()

        result = VerificationResult(
            valid=True,
            agent_id="test_agent",
            message_id="msg_test",
            timestamp=now,
            verification_time=0.005,
            failure_reason=None,
            public_key_fingerprint="abc123",
            signature_algorithm="Ed25519",
            status=VerificationStatus.VALID
        )

        result_dict = result.to_dict()

        assert result_dict["valid"] is True
        assert result_dict["agent_id"] == "test_agent"
        assert result_dict["message_id"] == "msg_test"
        assert result_dict["verification_time"] == 0.005
        assert result_dict["status"] == "valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
