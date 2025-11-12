"""InfraFabric Chassis Module - WASM Security Sandboxing

This module provides secure execution environments for swarm agents using
WASM sandboxing with scoped credentials and resource limits.

Philosophy:
- IF.TTT Trustworthy: Scoped credentials prevent lateral movement attacks
- IF.ground Observable: All credential operations audited
- Wu Lun (朋友): Each swarm operates with peer-level trust, scoped to tasks

Task: P0.3.3 - Scoped credentials (WASM security)
"""

from infrafabric.chassis.auth import (
    ScopedCredentials,
    CredentialManager,
    CredentialExpiredException,
    UnauthorizedEndpointException,
)

__all__ = [
    "ScopedCredentials",
    "CredentialManager",
    "CredentialExpiredException",
    "UnauthorizedEndpointException",
]
