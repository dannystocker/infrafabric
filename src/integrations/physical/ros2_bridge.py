"""
ROS2 bridge stub for robotics.
Maps E-Stop intent to zeroing /cmd_vel.
"""

from typing import Any


class ROS2Bridge:
    def __init__(self, ros_client: Any):
        self.ros = ros_client

    def estop(self) -> None:
        """Publish zero velocity to /cmd_vel."""
        if hasattr(self.ros, "publish_cmd_vel"):
            self.ros.publish_cmd_vel(0.0, 0.0, 0.0)
        else:
            raise NotImplementedError("ROS client missing publish_cmd_vel method")

    def handle_intent(self, intent: str) -> None:
        if intent.lower() in ["estop", "e-stop", "emergency_stop"]:
            self.estop()
        else:
            raise ValueError(f"Unknown intent: {intent}")
