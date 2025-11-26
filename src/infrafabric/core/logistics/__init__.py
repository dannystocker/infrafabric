"""
IF.LOGISTICS Dispatch Layer

Provides standardized Redis operations with schema validation,
type checking, and IF.TTT traceability for the Parcel metaphor.
"""

from .parcel import (
    DispatchQueue,
    LogisticsDispatcher,
    Parcel,
    ParcelSchemaVersion,
    RedisKeyType,
)

__all__ = [
    "DispatchQueue",
    "LogisticsDispatcher",
    "Parcel",
    "ParcelSchemaVersion",
    "RedisKeyType",
]
