"""
InfraFabric Schema Definitions

Data structures and validation for IF components.
"""

from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    CapabilityManifest,
    validate_capability_manifest,
    validate_swarm_profile,
)

__all__ = [
    'Capability',
    'SwarmProfile',
    'ResourcePolicy',
    'CapabilityManifest',
    'validate_capability_manifest',
    'validate_swarm_profile',
]
