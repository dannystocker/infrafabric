"""InfraFabric Schema Definitions

This module contains data structures and schemas for the InfraFabric
Swarm of Swarms (S²) coordination system.

Philosophy: IF.ground observable - All data structures are observable and auditable
"""

from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    validate_capability_manifest,
)

__all__ = [
    "Capability",
    "SwarmProfile",
    "ResourcePolicy",
    "validate_capability_manifest",
]
