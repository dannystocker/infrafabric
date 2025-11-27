"""
InfraFabric Series 2: Air Vertical
OPERATION SKYNET - Unified Drone Fleet Integration

Supports:
- MAVLink (PX4/ArduPilot)
- Cursor-on-Target (ATAK/FreeTAKServer)
- DJI MQTT (Enterprise drones)
"""

from .drone_fleet_adapter import (
    DroneFleetAdapter,
    MavlinkBridge,
    CotBridge,
    DjiMqttBridge,
    DroneBridgeProtocol
)

__all__ = [
    "DroneFleetAdapter",
    "MavlinkBridge",
    "CotBridge",
    "DjiMqttBridge",
    "DroneBridgeProtocol"
]

__version__ = "2.0.0"
