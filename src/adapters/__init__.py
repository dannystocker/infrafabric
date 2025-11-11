"""
SIP Adapter Framework - Unified interface for 7 SIP server implementations.

This package provides a standardized abstract base class (SIPAdapterBase) that all
SIP server adapters must inherit from, ensuring consistent interfaces across:

- Asterisk (AMI protocol)
- FreeSWITCH (ESL protocol)
- Kamailio (MI protocol)
- OpenSIPS (MI_JSON protocol)
- Yate (Telephony engine)
- PJSUA (PJSIP library)
- SIPp (Traffic generator)

Protocol: IF.TTT (Traceable/Transparent/Trustworthy) compliance
Philosophy: Wu Lun (五伦) Confucian relationship mapping for call hierarchy

Author: Agent 8 (IF.search discovery)
Version: 1.0.0
Date: 2025-11-11
"""

from src.adapters.sip_adapter_base import (
    # Base class
    SIPAdapterBase,
    # Enums
    CallState,
    ConnectionState,
    HealthStatus,
    ErrorSeverity,
    # Data classes
    CallStateEvent,
    IncomingCallEvent,
    ErrorEvent,
    ConnectionStateEvent,
    # Exceptions
    SIPAdapterError,
    ConnectionError,
    CallError,
    ConfigurationError,
    TimeoutError,
    # Utilities
    EventEmitter,
    MetricsCollector,
    # Factory
    create_adapter,
)

__version__ = "1.0.0"
__author__ = "Agent 8 (IF.search)"
__all__ = [
    # Main class
    "SIPAdapterBase",
    # Enums
    "CallState",
    "ConnectionState",
    "HealthStatus",
    "ErrorSeverity",
    # Events
    "CallStateEvent",
    "IncomingCallEvent",
    "ErrorEvent",
    "ConnectionStateEvent",
    # Exceptions
    "SIPAdapterError",
    "ConnectionError",
    "CallError",
    "ConfigurationError",
    "TimeoutError",
    # Utilities
    "EventEmitter",
    "MetricsCollector",
    # Factory
    "create_adapter",
]
