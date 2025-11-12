"""Unit tests for Scoped Credentials (P0.3.3)

Tests cover:
- Credential generation with secure tokens
- TTL expiration validation
- Endpoint whitelisting
- Credential revocation
- Credential rotation
- Expired credential cleanup
- Security exception handling

Task: P0.3.3 - Scoped credentials (WASM security)
Session: 4 (SIP)
Model: Sonnet
"""

import pytest
import time
from infrafabric.chassis.auth import (
    ScopedCredentials,
    CredentialManager,
    CredentialExpiredException,
    UnauthorizedEndpointException,
    InvalidCredentialException,
)


class TestScopedCredentials:
    """Test ScopedCredentials dataclass"""

    def test_create_credentials(self):
        """Create valid scoped credentials"""
        creds = ScopedCredentials(
            swarm_id="session-4-sip",
            task_id="task-123",
            api_token="test-token-12345",
            ttl_seconds=300,
            allowed_endpoints=["/api/v1/tasks"],
            created_at=time.time()
        )

        assert creds.swarm_id == "session-4-sip"
        assert creds.task_id == "task-123"
        assert creds.ttl_seconds == 300
        assert len(creds.allowed_endpoints) == 1

    def test_not_expired(self):
        """Credentials not expired within TTL"""
        creds = ScopedCredentials(
            swarm_id="test",
            task_id="task-1",
            api_token="token",
            ttl_seconds=300,
            allowed_endpoints=[],
            created_at=time.time()
        )

        assert creds.is_expired is False
        assert creds.time_remaining_seconds > 290

    def test_expired(self):
        """Credentials expired after TTL"""
        creds = ScopedCredentials(
            swarm_id="test",
            task_id="task-1",
            api_token="token",
            ttl_seconds=1,
            allowed_endpoints=[],
            created_at=time.time() - 5  # Created 5 seconds ago with 1s TTL
        )

        assert creds.is_expired is True
        assert creds.time_remaining_seconds < 0

    def test_expires_at(self):
        """Calculate expiration timestamp"""
        created = time.time()
        creds = ScopedCredentials(
            swarm_id="test",
            task_id="task-1",
            api_token="token",
            ttl_seconds=300,
            allowed_endpoints=[],
            created_at=created
        )

        assert abs(creds.expires_at - (created + 300)) < 0.1

    def test_endpoint_allowed(self):
        """Check endpoint whitelist"""
        creds = ScopedCredentials(
            swarm_id="test",
            task_id="task-1",
            api_token="token",
            ttl_seconds=300,
            allowed_endpoints=["/api/v1/tasks", "/api/v1/results"],
            created_at=time.time()
        )

        assert creds.is_endpoint_allowed("/api/v1/tasks") is True
        assert creds.is_endpoint_allowed("/api/v1/results") is True
        assert creds.is_endpoint_allowed("/api/v1/admin") is False

    def test_empty_endpoint_whitelist(self):
        """Empty whitelist allows all endpoints"""
        creds = ScopedCredentials(
            swarm_id="test",
            task_id="task-1",
            api_token="token",
            ttl_seconds=300,
            allowed_endpoints=[],
            created_at=time.time()
        )

        assert creds.is_endpoint_allowed("/api/v1/anything") is True
        assert creds.is_endpoint_allowed("/admin/dangerous") is True

    def test_to_dict_masks_token(self):
        """to_dict() masks API token for security"""
        creds = ScopedCredentials(
            swarm_id="test",
            task_id="task-1",
            api_token="0123456789abcdef0123456789abcdef",
            ttl_seconds=300,
            allowed_endpoints=[],
            created_at=time.time()
        )

        data = creds.to_dict()

        # Token should be masked
        assert "..." in data["api_token"]
        assert len(data["api_token"]) < len("0123456789abcdef0123456789abcdef")
        assert data["api_token"].startswith("01234567")
        assert data["api_token"].endswith("cdef")


class TestCredentialManager:
    """Test CredentialManager"""

    def test_generate_credentials(self):
        """Generate scoped credentials"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="session-4-sip",
            task_id="task-123",
            ttl_seconds=300,
            allowed_endpoints=["/api/v1/tasks"]
        )

        assert creds.swarm_id == "session-4-sip"
        assert creds.task_id == "task-123"
        assert creds.ttl_seconds == 300
        assert len(creds.api_token) == 43  # 32 bytes base64 URL-safe
        assert not creds.is_expired

    def test_token_is_random(self):
        """Generated tokens are cryptographically random"""
        manager = CredentialManager()

        tokens = set()
        for i in range(100):
            creds = manager.generate_scoped_credentials(
                swarm_id="test",
                task_id=f"task-{i}",
                ttl_seconds=300
            )
            tokens.add(creds.api_token)

        # All tokens should be unique
        assert len(tokens) == 100

    def test_validate_valid_credentials(self):
        """Validate valid credentials"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="session-4-sip",
            task_id="task-123",
            ttl_seconds=300,
            allowed_endpoints=["/api/v1/tasks"]
        )

        # Should pass validation
        assert manager.validate_credentials(creds.api_token, "/api/v1/tasks") is True

    def test_validate_unknown_token(self):
        """Unknown token raises InvalidCredentialException"""
        manager = CredentialManager()

        with pytest.raises(InvalidCredentialException, match="Unknown API token"):
            manager.validate_credentials("unknown-token", "/api/v1/tasks")

    def test_validate_expired_credentials(self):
        """Expired credentials raise CredentialExpiredException"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="test",
            task_id="task-1",
            ttl_seconds=1,  # 1 second TTL
            allowed_endpoints=["/api/v1/tasks"]
        )

        # Wait for expiration
        time.sleep(1.1)

        with pytest.raises(CredentialExpiredException, match="expired"):
            manager.validate_credentials(creds.api_token, "/api/v1/tasks")

        # Expired credentials should be removed
        assert creds.api_token not in manager.active_credentials

    def test_validate_unauthorized_endpoint(self):
        """Non-whitelisted endpoint raises UnauthorizedEndpointException"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="test",
            task_id="task-1",
            ttl_seconds=300,
            allowed_endpoints=["/api/v1/tasks"]
        )

        with pytest.raises(UnauthorizedEndpointException, match="not in whitelist"):
            manager.validate_credentials(creds.api_token, "/api/v1/admin")

    def test_revoke_credentials(self):
        """Revoke credentials"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="test",
            task_id="task-1",
            ttl_seconds=300
        )

        # Revoke credentials
        assert manager.revoke_credentials(creds.api_token) is True

        # Should now fail validation
        with pytest.raises(InvalidCredentialException, match="revoked"):
            manager.validate_credentials(creds.api_token, "/api/v1/tasks")

    def test_revoke_unknown_token(self):
        """Revoke unknown token returns False"""
        manager = CredentialManager()

        assert manager.revoke_credentials("unknown-token") is False

    def test_rotate_credentials(self):
        """Rotate credentials (revoke old, generate new)"""
        manager = CredentialManager()

        old_creds = manager.generate_scoped_credentials(
            swarm_id="test",
            task_id="task-1",
            ttl_seconds=300,
            allowed_endpoints=["/api/v1/tasks"]
        )

        old_token = old_creds.api_token

        # Rotate
        new_creds = manager.rotate_credentials(old_token, ttl_seconds=600)

        assert new_creds is not None
        assert new_creds.api_token != old_token
        assert new_creds.swarm_id == old_creds.swarm_id
        assert new_creds.task_id == old_creds.task_id
        assert new_creds.ttl_seconds == 600

        # Old token should be revoked
        with pytest.raises(InvalidCredentialException, match="revoked"):
            manager.validate_credentials(old_token, "/api/v1/tasks")

        # New token should work
        assert manager.validate_credentials(new_creds.api_token, "/api/v1/tasks") is True

    def test_rotate_unknown_token(self):
        """Rotate unknown token returns None"""
        manager = CredentialManager()

        assert manager.rotate_credentials("unknown-token") is None

    def test_cleanup_expired(self):
        """Cleanup expired credentials"""
        manager = CredentialManager()

        # Create short-lived credentials
        for i in range(5):
            manager.generate_scoped_credentials(
                swarm_id="test",
                task_id=f"task-{i}",
                ttl_seconds=1
            )

        # Create long-lived credential
        manager.generate_scoped_credentials(
            swarm_id="test",
            task_id="task-long",
            ttl_seconds=300
        )

        assert len(manager.active_credentials) == 6

        # Wait for short-lived credentials to expire
        time.sleep(1.1)

        # Cleanup
        removed = manager.cleanup_expired()

        assert removed == 5
        assert len(manager.active_credentials) == 1

    def test_get_credentials_for_task(self):
        """Get credentials for specific task"""
        manager = CredentialManager()

        manager.generate_scoped_credentials("swarm-1", "task-A", 300)
        manager.generate_scoped_credentials("swarm-2", "task-A", 300)
        manager.generate_scoped_credentials("swarm-3", "task-B", 300)

        task_a_creds = manager.get_credentials_for_task("task-A")

        assert len(task_a_creds) == 2
        assert all(c.task_id == "task-A" for c in task_a_creds)

    def test_get_credentials_for_swarm(self):
        """Get credentials for specific swarm"""
        manager = CredentialManager()

        manager.generate_scoped_credentials("swarm-1", "task-A", 300)
        manager.generate_scoped_credentials("swarm-1", "task-B", 300)
        manager.generate_scoped_credentials("swarm-2", "task-A", 300)

        swarm1_creds = manager.get_credentials_for_swarm("swarm-1")

        assert len(swarm1_creds) == 2
        assert all(c.swarm_id == "swarm-1" for c in swarm1_creds)

    def test_get_stats(self):
        """Get credential manager statistics"""
        manager = CredentialManager()

        # Create active credentials
        manager.generate_scoped_credentials("swarm-1", "task-1", 300)
        manager.generate_scoped_credentials("swarm-2", "task-2", 300)

        # Create expired credential
        manager.generate_scoped_credentials("swarm-3", "task-3", 1)
        time.sleep(1.1)

        # Revoke one
        creds = manager.generate_scoped_credentials("swarm-4", "task-4", 300)
        manager.revoke_credentials(creds.api_token)

        stats = manager.get_stats()

        assert stats["active"] == 2  # 2 active (not expired)
        assert stats["expired"] == 1  # 1 expired but not cleaned
        assert stats["revoked"] == 1  # 1 revoked
        assert stats["total"] == 3  # 3 in active_credentials (not cleaned yet)


class TestSecurityScenarios:
    """Test security scenarios"""

    def test_credential_expiration_prevents_reuse(self):
        """Expired credentials cannot be reused"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="session-4-sip",
            task_id="task-123",
            ttl_seconds=1
        )

        # Works initially
        assert manager.validate_credentials(creds.api_token, "/api/v1/tasks") is True

        # Wait for expiration
        time.sleep(1.1)

        # Should fail after expiration
        with pytest.raises(CredentialExpiredException):
            manager.validate_credentials(creds.api_token, "/api/v1/tasks")

    def test_endpoint_whitelist_prevents_lateral_movement(self):
        """Whitelisting prevents access to other endpoints"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="session-4-sip",
            task_id="task-123",
            ttl_seconds=300,
            allowed_endpoints=["/api/v1/tasks"]  # Only tasks endpoint
        )

        # Allowed endpoint works
        assert manager.validate_credentials(creds.api_token, "/api/v1/tasks") is True

        # Admin endpoint blocked
        with pytest.raises(UnauthorizedEndpointException):
            manager.validate_credentials(creds.api_token, "/api/v1/admin")

        # Other endpoints blocked
        with pytest.raises(UnauthorizedEndpointException):
            manager.validate_credentials(creds.api_token, "/api/v1/secrets")

    def test_revocation_prevents_reuse(self):
        """Revoked credentials cannot be reused"""
        manager = CredentialManager()

        creds = manager.generate_scoped_credentials(
            swarm_id="test",
            task_id="task-1",
            ttl_seconds=300
        )

        # Works initially
        assert manager.validate_credentials(creds.api_token, "/api/v1/tasks") is True

        # Revoke
        manager.revoke_credentials(creds.api_token)

        # Should fail after revocation
        with pytest.raises(InvalidCredentialException, match="revoked"):
            manager.validate_credentials(creds.api_token, "/api/v1/tasks")

    def test_task_scoping_isolation(self):
        """Credentials are isolated by task"""
        manager = CredentialManager()

        task1_creds = manager.generate_scoped_credentials(
            swarm_id="swarm-1",
            task_id="task-1",
            ttl_seconds=300
        )

        task2_creds = manager.generate_scoped_credentials(
            swarm_id="swarm-1",
            task_id="task-2",
            ttl_seconds=300
        )

        # Credentials are different
        assert task1_creds.api_token != task2_creds.api_token

        # Both work for their respective tasks
        assert manager.validate_credentials(task1_creds.api_token, "/api") is True
        assert manager.validate_credentials(task2_creds.api_token, "/api") is True

    def test_rotation_invalidates_old_token(self):
        """Credential rotation invalidates old token immediately"""
        manager = CredentialManager()

        old_creds = manager.generate_scoped_credentials(
            swarm_id="test",
            task_id="task-1",
            ttl_seconds=300
        )

        old_token = old_creds.api_token

        # Rotate
        new_creds = manager.rotate_credentials(old_token)

        # Old token should fail immediately
        with pytest.raises(InvalidCredentialException, match="revoked"):
            manager.validate_credentials(old_token, "/api/v1/tasks")

        # New token should work
        assert manager.validate_credentials(new_creds.api_token, "/api/v1/tasks") is True


class TestSession4Integration:
    """Test Session 4 (SIP) specific scenarios"""

    def test_sip_integration_credentials(self):
        """Session 4 SIP integration with scoped credentials"""
        manager = CredentialManager()

        # Generate credentials for SIP integration task
        creds = manager.generate_scoped_credentials(
            swarm_id="session-4-sip",
            task_id="sip-integration-123",
            ttl_seconds=300,
            allowed_endpoints=[
                "/api/v1/sip/escalate",
                "/api/v1/tasks/result"
            ],
            metadata={
                "task_type": "sip_integration",
                "priority": "high"
            }
        )

        # Validate SIP endpoint access
        assert manager.validate_credentials(creds.api_token, "/api/v1/sip/escalate") is True

        # Validate result submission
        assert manager.validate_credentials(creds.api_token, "/api/v1/tasks/result") is True

        # Block non-SIP endpoints
        with pytest.raises(UnauthorizedEndpointException):
            manager.validate_credentials(creds.api_token, "/api/v1/admin")

    def test_multiple_sessions_isolated(self):
        """Multiple sessions have isolated credentials"""
        manager = CredentialManager()

        session1_creds = manager.generate_scoped_credentials(
            swarm_id="session-1-ndi",
            task_id="task-1",
            ttl_seconds=300
        )

        session4_creds = manager.generate_scoped_credentials(
            swarm_id="session-4-sip",
            task_id="task-1",
            ttl_seconds=300
        )

        # Credentials are different
        assert session1_creds.api_token != session4_creds.api_token

        # Both sessions can access their credentials
        assert manager.validate_credentials(session1_creds.api_token, "/api") is True
        assert manager.validate_credentials(session4_creds.api_token, "/api") is True


# Run tests with: pytest tests/unit/test_scoped_credentials.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
