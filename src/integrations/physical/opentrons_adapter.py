"""
Opentrons adapter stub.
Maps intent to pipette.aspirate().
"""

from typing import Any


class OpentronsAdapter:
    def __init__(self, pipette: Any):
        self.pipette = pipette

    def aspirate(self, volume: float, location: Any = None) -> Any:
        if hasattr(self.pipette, "aspirate"):
            return self.pipette.aspirate(volume, location)
        raise NotImplementedError("Pipette missing aspirate()")

    def handle_intent(self, intent: str, volume: float = 0.0, location: Any = None) -> Any:
        if intent.lower() in ["aspirate", "draw", "pickup"]:
            if volume <= 0:
                raise ValueError("Volume must be > 0")
            return self.aspirate(volume, location)
        raise ValueError(f"Unknown intent: {intent}")
