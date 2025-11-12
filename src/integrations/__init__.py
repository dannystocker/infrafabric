"""
InfraFabric Integrations Package
Provides integrations with external services and tools

Available Integrations:
- OBS Studio: Streaming and recording control
- Home Assistant: Notifications, webhooks, and automation
- VMix: Professional video mixing (coming soon)
"""

from .obs_streaming import (
    OBSStreamingController,
    OBSConnectionError,
    OBSStreamingError,
    IFWitnessLogger,
    OBSStreamingContext,
    create_obs_controller,
    StreamService,
    RecordingFormat
)

from .ha_notifications import (
    HomeAssistantNotifications,
    HomeAssistantError,
    HomeAssistantConnectionError,
    HomeAssistantAuthError
)

__all__ = [
    # OBS Studio Integration
    'OBSStreamingController',
    'OBSConnectionError',
    'OBSStreamingError',
    'IFWitnessLogger',
    'OBSStreamingContext',
    'create_obs_controller',
    'StreamService',
    'RecordingFormat',
    # Home Assistant Integration
    'HomeAssistantNotifications',
    'HomeAssistantError',
    'HomeAssistantConnectionError',
    'HomeAssistantAuthError'
]

__version__ = '1.0.0'
