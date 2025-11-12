"""
InfraFabric Integration Modules

This package contains production-ready integration modules for external services
and platforms used by InfraFabric agents and workflows.

Available Integrations:
- obs_media: OBS Studio media, browser, and capture source control

Author: InfraFabric Project
License: CC BY 4.0
"""

from .obs_media import (
    OBSMediaManager,
    OBSWebSocketClient,
    MediaSourceController,
    BrowserSourceController,
    CaptureSourceController,
    MediaSourceConfig,
    BrowserSourceConfig,
    CaptureSourceConfig,
    MediaInputType,
    MediaAction,
    Platform,
    WitnessLog
)

__all__ = [
    "OBSMediaManager",
    "OBSWebSocketClient",
    "MediaSourceController",
    "BrowserSourceController",
    "CaptureSourceController",
    "MediaSourceConfig",
    "BrowserSourceConfig",
    "CaptureSourceConfig",
    "MediaInputType",
    "MediaAction",
    "Platform",
    "WitnessLog"
]

__version__ = "1.0.0"
