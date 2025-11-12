"""InfraFabric Chassis Module - WASM Security Sandboxing

This module provides secure execution environments for swarm agents using
WASM sandboxing with scoped credentials, resource limits, SLO tracking,
and reputation-based prioritization.

Philosophy:
- IF.TTT Trustworthy: Scoped credentials prevent lateral movement attacks
- IF.ground Observable: All credential operations audited
- Wu Lun (朋友): Each swarm operates with peer-level trust, scoped to tasks

Tasks: P0.3.3 (Scoped credentials), P0.3.4 (SLO tracking), P0.3.5 (Reputation)
"""

from infrafabric.chassis.auth import (
    ScopedCredentials,
    CredentialManager,
    CredentialExpiredException,
    UnauthorizedEndpointException,
)

from infrafabric.chassis.slo import (
    ServiceLevelObjective,
    PerformanceMetric,
    SLOCompliance,
    SLOTracker,
)

from infrafabric.chassis.reputation import (
    ReputationScore,
    ReputationSystem,
)

__all__ = [
    # Auth (P0.3.3)
    "ScopedCredentials",
    "CredentialManager",
    "CredentialExpiredException",
    "UnauthorizedEndpointException",
    # SLO Tracking (P0.3.4)
    "ServiceLevelObjective",
    "PerformanceMetric",
    "SLOCompliance",
    "SLOTracker",
    # Reputation (P0.3.5)
    "ReputationScore",
    "ReputationSystem",
]
