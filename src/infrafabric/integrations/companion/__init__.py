"""
InfraFabric Companion MCR Bridge

Redis-based Multi-Controller Routing for Bitfocus Companion integration.
Maps semantic intents to device-specific protocol commands.

Usage:
    async with CompanionBridge() as bridge:
        result = await bridge.execute_intent("studio_dark_mode")

Architecture:
    - Redis for configuration and state
    - Pydantic for schema validation
    - Async/await for I/O operations
    - Exponential backoff retry
"""

from .models import (
    CompanionBridgeConfig,
    ProtocolTemplate,
    CompanionDevice,
    IntentMapping,
    ButtonAction,
    CompanionMacro,
    MacroStep,
    ButtonState,
    CompanionSession,
    ExecutionResult,
)

from .bridge import CompanionVirtualSurface, CompanionBridge

from .errors import (
    CompanionError,
    CompanionErrorType,
)

__all__ = [
    # Models
    "CompanionBridgeConfig",
    "ProtocolTemplate",
    "CompanionDevice",
    "IntentMapping",
    "ButtonAction",
    "CompanionMacro",
    "MacroStep",
    "ButtonState",
    "CompanionSession",
    "ExecutionResult",
    # Main interface
    "CompanionVirtualSurface",
    "CompanionBridge",
    # Errors
    "CompanionError",
    "CompanionErrorType",
]

__version__ = "0.1.0"
__protocol__ = "IF.mcr.companion"
