"""
IF.VESICLE Transport Layer

Provides standardized Redis operations with schema validation,
type checking, and IF.TTT traceability.
"""

from .vesicle import (
    VesiclePayload,
    VesicleTransport,
    VesiclePool,
    RedisKeyType,
    VesicleSchemaVersion,
)

__all__ = [
    "VesiclePayload",
    "VesicleTransport",
    "VesiclePool",
    "RedisKeyType",
    "VesicleSchemaVersion",
]
