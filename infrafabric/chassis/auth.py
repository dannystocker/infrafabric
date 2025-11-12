"""Scoped Credentials for WASM Sandboxes (P0.3.3)

This module implements temporary, task-scoped credentials for swarm agents
running in WASM sandboxes. This prevents long-lived API keys from being
compromised and limits the blast radius of security breaches.

Philosophy:
- IF.TTT Trustworthy: Time-limited credentials with endpoint whitelisting
- IF.ground Observable: All credential operations logged to IF.witness
- Zero-trust security: Credentials expire and are task-scoped only

Task: P0.3.3 - Scoped credentials (WASM security)
Est: 2h (Sonnet)
Session: 4 (SIP)
Dependencies: P0.3.1 (WASM runtime - Session 7)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set
import time
import secrets
import hashlib
import json


class CredentialExpiredException(Exception):
    """Raised when attempting to use expired credentials"""
    pass


class UnauthorizedEndpointException(Exception):
    """Raised when attempting to access non-whitelisted endpoint"""
    pass


class InvalidCredentialException(Exception):
    """Raised when credential token is invalid"""
    pass


@dataclass
class ScopedCredentials:
    """Temporary, task-scoped credentials

    Credentials are:
    - Short-lived (default 5 minutes TTL)
    - Task-scoped (cannot be reused across tasks)
    - Endpoint-restricted (whitelist of allowed API endpoints)
    - Auditable (all operations logged to IF.witness)

    Attributes:
        swarm_id: Unique swarm identifier
        task_id: Task this credential is scoped to
        api_token: Secure random token (32 bytes URL-safe)
        ttl_seconds: Time-to-live in seconds
        allowed_endpoints: Whitelist of allowed API endpoints
        created_at: Unix timestamp of creation
        metadata: Optional additional metadata

    Example:
        >>> creds = ScopedCredentials(
        ...     swarm_id="session-4-sip",
        ...     task_id="task-123",
        ...     api_token="...",
        ...     ttl_seconds=300,
        ...     allowed_endpoints=["/api/v1/tasks", "/api/v1/results"]
        ... )
        >>> assert not creds.is_expired
    """
    swarm_id: str
    task_id: str
    api_token: str
    ttl_seconds: int
    allowed_endpoints: List[str]
    created_at: float
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if credentials have expired

        Returns:
            True if current time exceeds created_at + ttl_seconds
        """
        return time.time() > self.created_at + self.ttl_seconds

    @property
    def expires_at(self) -> float:
        """Get expiration timestamp

        Returns:
            Unix timestamp when credentials expire
        """
        return self.created_at + self.ttl_seconds

    @property
    def time_remaining_seconds(self) -> float:
        """Get remaining time before expiration

        Returns:
            Seconds remaining (negative if expired)
        """
        return self.expires_at - time.time()

    def is_endpoint_allowed(self, endpoint: str) -> bool:
        """Check if endpoint is in whitelist

        Args:
            endpoint: API endpoint to check

        Returns:
            True if endpoint is allowed or whitelist is empty (allow all)
        """
        if not self.allowed_endpoints:
            return True  # Empty whitelist = allow all

        return endpoint in self.allowed_endpoints

    def to_dict(self) -> Dict[str, any]:
        """Convert credentials to dictionary

        Returns:
            Dictionary representation (API token masked for security)
        """
        data = asdict(self)
        # Mask API token for logging/auditing
        data["api_token"] = f"{data['api_token'][:8]}...{data['api_token'][-4:]}"
        return data


class CredentialManager:
    """Manage scoped credentials for swarms

    The CredentialManager handles:
    - Generating secure, random API tokens
    - Storing active credentials in-memory
    - Validating credentials (expiration, endpoint whitelist)
    - Revoking credentials
    - Rotating credentials
    - Audit logging to IF.witness

    Example:
        >>> manager = CredentialManager()
        >>> creds = manager.generate_scoped_credentials(
        ...     swarm_id="session-4-sip",
        ...     task_id="task-123",
        ...     ttl_seconds=300,
        ...     allowed_endpoints=["/api/v1/tasks"]
        ... )
        >>> assert manager.validate_credentials(creds.api_token, "/api/v1/tasks")
    """

    def __init__(self, secrets_vault: Optional['SecretsVault'] = None):
        """Initialize credential manager

        Args:
            secrets_vault: Optional external secrets vault integration
        """
        self.active_credentials: Dict[str, ScopedCredentials] = {}
        self.revoked_tokens: Set[str] = set()
        self.secrets_vault = secrets_vault

    def generate_scoped_credentials(
        self,
        swarm_id: str,
        task_id: str,
        ttl_seconds: int = 300,
        allowed_endpoints: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> ScopedCredentials:
        """Generate temporary credentials for a task

        Args:
            swarm_id: Unique swarm identifier
            task_id: Task identifier
            ttl_seconds: Time-to-live in seconds (default 5 minutes)
            allowed_endpoints: Whitelist of allowed endpoints (empty = allow all)
            metadata: Optional metadata (e.g., task type, priority)

        Returns:
            ScopedCredentials instance with secure random token

        Example:
            >>> manager = CredentialManager()
            >>> creds = manager.generate_scoped_credentials(
            ...     swarm_id="session-4",
            ...     task_id="task-1",
            ...     ttl_seconds=300
            ... )
            >>> assert len(creds.api_token) == 43  # 32 bytes base64 URL-safe
        """
        # Generate secure random token (32 bytes = 256 bits)
        api_token = secrets.token_urlsafe(32)

        # Create credentials
        credentials = ScopedCredentials(
            swarm_id=swarm_id,
            task_id=task_id,
            api_token=api_token,
            ttl_seconds=ttl_seconds,
            allowed_endpoints=allowed_endpoints or [],
            created_at=time.time(),
            metadata=metadata or {}
        )

        # Store credentials
        self.active_credentials[api_token] = credentials

        # Store in external vault if configured
        if self.secrets_vault:
            self.secrets_vault.store_credential(credentials)

        # Log to IF.witness
        self._log_operation(
            operation='credentials_generated',
            params={
                'swarm_id': swarm_id,
                'task_id': task_id,
                'ttl_seconds': ttl_seconds,
                'endpoint_count': len(allowed_endpoints or [])
            }
        )

        return credentials

    def validate_credentials(
        self,
        api_token: str,
        endpoint: str
    ) -> bool:
        """Validate credentials for API call

        Args:
            api_token: API token to validate
            endpoint: Endpoint being accessed

        Returns:
            True if credentials are valid and endpoint is allowed

        Raises:
            InvalidCredentialException: If token is unknown or revoked
            CredentialExpiredException: If credentials have expired
            UnauthorizedEndpointException: If endpoint is not whitelisted
        """
        # Check if token exists
        if api_token not in self.active_credentials:
            if api_token in self.revoked_tokens:
                self._log_operation(
                    operation='credential_validation_failed',
                    params={'reason': 'revoked'},
                    severity='WARNING'
                )
                raise InvalidCredentialException("Credential has been revoked")

            self._log_operation(
                operation='credential_validation_failed',
                params={'reason': 'unknown_token'},
                severity='WARNING'
            )
            raise InvalidCredentialException("Unknown API token")

        creds = self.active_credentials[api_token]

        # Check expiration
        if creds.is_expired:
            # Clean up expired credentials
            del self.active_credentials[api_token]

            self._log_operation(
                operation='credential_validation_failed',
                params={
                    'reason': 'expired',
                    'swarm_id': creds.swarm_id,
                    'task_id': creds.task_id
                },
                severity='WARNING'
            )
            raise CredentialExpiredException(
                f"Credentials expired {abs(creds.time_remaining_seconds):.1f}s ago"
            )

        # Check endpoint whitelist
        if not creds.is_endpoint_allowed(endpoint):
            self._log_operation(
                operation='credential_validation_failed',
                params={
                    'reason': 'unauthorized_endpoint',
                    'swarm_id': creds.swarm_id,
                    'task_id': creds.task_id,
                    'endpoint': endpoint,
                    'allowed_endpoints': creds.allowed_endpoints
                },
                severity='WARNING'
            )
            raise UnauthorizedEndpointException(
                f"Endpoint '{endpoint}' not in whitelist: {creds.allowed_endpoints}"
            )

        # Validation successful
        self._log_operation(
            operation='credential_validated',
            params={
                'swarm_id': creds.swarm_id,
                'task_id': creds.task_id,
                'endpoint': endpoint
            }
        )

        return True

    def revoke_credentials(self, api_token: str) -> bool:
        """Revoke credentials immediately

        Args:
            api_token: Token to revoke

        Returns:
            True if revoked successfully, False if token not found
        """
        if api_token not in self.active_credentials:
            return False

        creds = self.active_credentials[api_token]
        del self.active_credentials[api_token]
        self.revoked_tokens.add(api_token)

        self._log_operation(
            operation='credentials_revoked',
            params={
                'swarm_id': creds.swarm_id,
                'task_id': creds.task_id
            },
            severity='INFO'
        )

        return True

    def rotate_credentials(
        self,
        old_token: str,
        ttl_seconds: Optional[int] = None
    ) -> Optional[ScopedCredentials]:
        """Rotate credentials (revoke old, generate new)

        Args:
            old_token: Old API token to rotate
            ttl_seconds: Optional new TTL (default: same as old)

        Returns:
            New ScopedCredentials, or None if old token not found
        """
        if old_token not in self.active_credentials:
            return None

        old_creds = self.active_credentials[old_token]

        # Generate new credentials
        new_creds = self.generate_scoped_credentials(
            swarm_id=old_creds.swarm_id,
            task_id=old_creds.task_id,
            ttl_seconds=ttl_seconds or old_creds.ttl_seconds,
            allowed_endpoints=old_creds.allowed_endpoints,
            metadata=old_creds.metadata
        )

        # Revoke old credentials
        self.revoke_credentials(old_token)

        self._log_operation(
            operation='credentials_rotated',
            params={
                'swarm_id': old_creds.swarm_id,
                'task_id': old_creds.task_id
            }
        )

        return new_creds

    def cleanup_expired(self) -> int:
        """Remove expired credentials from memory

        Returns:
            Number of credentials removed
        """
        expired_tokens = [
            token for token, creds in self.active_credentials.items()
            if creds.is_expired
        ]

        for token in expired_tokens:
            del self.active_credentials[token]

        if expired_tokens:
            self._log_operation(
                operation='expired_credentials_cleaned',
                params={'count': len(expired_tokens)}
            )

        return len(expired_tokens)

    def get_credentials_for_task(self, task_id: str) -> List[ScopedCredentials]:
        """Get all active credentials for a task

        Args:
            task_id: Task identifier

        Returns:
            List of active credentials for the task
        """
        return [
            creds for creds in self.active_credentials.values()
            if creds.task_id == task_id and not creds.is_expired
        ]

    def get_credentials_for_swarm(self, swarm_id: str) -> List[ScopedCredentials]:
        """Get all active credentials for a swarm

        Args:
            swarm_id: Swarm identifier

        Returns:
            List of active credentials for the swarm
        """
        return [
            creds for creds in self.active_credentials.values()
            if creds.swarm_id == swarm_id and not creds.is_expired
        ]

    def get_stats(self) -> Dict[str, int]:
        """Get credential manager statistics

        Returns:
            Dictionary with active, expired, and revoked counts
        """
        active_count = len(self.active_credentials)
        expired_count = sum(
            1 for creds in self.active_credentials.values()
            if creds.is_expired
        )
        revoked_count = len(self.revoked_tokens)

        return {
            "active": active_count - expired_count,
            "expired": expired_count,
            "revoked": revoked_count,
            "total": active_count
        }

    def _log_operation(
        self,
        operation: str,
        params: Dict[str, any],
        severity: str = 'INFO'
    ) -> None:
        """Log credential operation to IF.witness

        Args:
            operation: Operation name
            params: Operation parameters
            severity: Log severity (INFO, WARNING, ERROR)
        """
        try:
            from infrafabric.witness import log_operation
            log_operation(
                component='IF.chassis.auth',
                operation=operation,
                params=params,
                severity=severity
            )
        except ImportError:
            # IF.witness not available - log to stderr
            import sys
            print(
                f"[IF.chassis.auth] {severity}: {operation} - {json.dumps(params)}",
                file=sys.stderr
            )


# Placeholder for external secrets vault integration
class SecretsVault:
    """External secrets vault integration (e.g., HashiCorp Vault, AWS Secrets Manager)

    This is a placeholder for future integration with external secrets management.
    """

    def store_credential(self, credentials: ScopedCredentials) -> bool:
        """Store credentials in external vault"""
        # TODO: Implement vault integration
        return True

    def retrieve_credential(self, api_token: str) -> Optional[ScopedCredentials]:
        """Retrieve credentials from external vault"""
        # TODO: Implement vault integration
        return None


__all__ = [
    "ScopedCredentials",
    "CredentialManager",
    "CredentialExpiredException",
    "UnauthorizedEndpointException",
    "InvalidCredentialException",
    "SecretsVault",
]
