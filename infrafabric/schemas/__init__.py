"""
InfraFabric Schema Definitions

This module contains shared data structures and schema definitions
for the InfraFabric S² (Swarm of Swarms) architecture.
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
