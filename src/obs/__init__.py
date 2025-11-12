"""
IF.obs - OBS Studio Control Module

OBS WebSocket integration for InfraFabric.
Provides programmatic control of OBS Studio for streaming and recording.
"""

from .client import OBSClient, OBSError, OBSConnectionError, OBSAPIError
from .config import OBSConfig, OBSConfigError
from .models import (
    OBSInstance,
    OBSScene,
    OBSSource,
    OBSStreamStatus,
    OBSRecordStatus,
    OBSStats,
    OBSFilter
)

__version__ = '0.1.0'
__all__ = [
    'OBSClient',
    'OBSError',
    'OBSConnectionError',
    'OBSAPIError',
    'OBSConfig',
    'OBSConfigError',
    'OBSInstance',
    'OBSScene',
    'OBSSource',
    'OBSStreamStatus',
    'OBSRecordStatus',
    'OBSStats',
    'OBSFilter',
]
