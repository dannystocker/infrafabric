"""
IF.LOGISTICS Dispatch Layer

Provides standardized Redis operations with schema validation,
type checking, and IF.TTT traceability for the Packet metaphor.
"""

from .packet import (
    DispatchQueue,
    LogisticsDispatcher,
    Packet,
    ParcelSchemaVersion,
    RedisKeyType,
)

__all__ = [
    "DispatchQueue",
    "LogisticsDispatcher",
    "Packet",
    "ParcelSchemaVersion",
    "RedisKeyType",
]
