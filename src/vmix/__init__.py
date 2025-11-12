"""
IF.vmix - vMix Production Control Integration

Professional live video production software integration for InfraFabric.
Provides CLI interface for vMix control with IF.witness logging.

Philosophy: Dead-simple CLI for production engineers.
Every operation logged to IF.witness for audit trails.
"""

from .client import VMixClient
from .config import VMixConfig
from .models import (
    VMixInstance,
    VMixStatus,
    VMixInput,
    VMixTransition,
    VMixStreamStatus,
    VMixRecordStatus
)

__version__ = "1.0.0"
__all__ = [
    'VMixClient',
    'VMixConfig',
    'VMixInstance',
    'VMixStatus',
    'VMixInput',
    'VMixTransition',
    'VMixStreamStatus',
    'VMixRecordStatus'
]
