"""
IF.bus - Production Infrastructure Control Framework

Unified interface for controlling production infrastructure:
- vMix (professional video production)
- OBS Studio (open-source streaming)
- Home Assistant (physical infrastructure)

This package provides:
- ProductionAdapterBase - Abstract base class for all adapters
- VMixAdapter - vMix production control
- OBSAdapter - OBS Studio control
- HomeAssistantAdapter - Physical infrastructure control

Author: Session 7 - IF.bus SIP Adapters (Master Sprint)
Version: 1.0.0
Date: 2025-11-12
"""

from src.bus.production_adapter_base import (
    # Base class
    ProductionAdapterBase,
    # Enums
    InstanceState,
    AdapterConnectionState,
    HealthStatus,
    ErrorSeverity,
    CommandType,
    # Data classes
    InstanceStateEvent,
    CommandExecutionEvent,
    DiscoveryEvent,
    ErrorEvent,
    ConnectionStateEvent,
    # Exceptions
    ProductionAdapterError,
    ConnectionError,
    InstanceError,
    CommandExecutionError,
    ConfigurationError,
    TimeoutError,
    DiscoveryError,
    # Utilities
    EventEmitter,
    MetricsCollector,
    # Factory
    create_adapter,
)

# Import production adapters
from src.bus.vmix_adapter import VMixAdapter
from src.bus.obs_adapter import OBSAdapter
from src.bus.ha_adapter import HomeAssistantAdapter

__version__ = "1.0.0"
__author__ = "Session 7 - IF.bus (Master Sprint)"
__all__ = [
    # Base class
    "ProductionAdapterBase",
    # Enums
    "InstanceState",
    "AdapterConnectionState",
    "HealthStatus",
    "ErrorSeverity",
    "CommandType",
    # Events
    "InstanceStateEvent",
    "CommandExecutionEvent",
    "DiscoveryEvent",
    "ErrorEvent",
    "ConnectionStateEvent",
    # Exceptions
    "ProductionAdapterError",
    "ConnectionError",
    "InstanceError",
    "CommandExecutionError",
    "ConfigurationError",
    "TimeoutError",
    "DiscoveryError",
    # Utilities
    "EventEmitter",
    "MetricsCollector",
    # Factory
    "create_adapter",
    # Production adapters
    "VMixAdapter",
    "OBSAdapter",
    "HomeAssistantAdapter",
]
