"""
InfraFabric Series 2: Air Vertical State Schemas
Following the "No Schema, No Write" philosophy - all drone state must be validated.
"""

from __future__ import annotations
from typing import Literal, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import uuid


class DronePosition(BaseModel):
    """WGS84 GPS coordinates with altitude"""
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    altitude_msl: float = Field(..., description="Altitude above mean sea level (meters)")
    altitude_rel: Optional[float] = Field(None, description="Altitude relative to home/launch point (meters)")
    heading: float = Field(0.0, ge=0.0, lt=360.0, description="True heading in degrees (0=North)")


class DroneAttitude(BaseModel):
    """Drone orientation in 3D space"""
    roll: float = Field(..., ge=-180.0, le=180.0, description="Roll angle in degrees")
    pitch: float = Field(..., ge=-90.0, le=90.0, description="Pitch angle in degrees")
    yaw: float = Field(..., ge=0.0, lt=360.0, description="Yaw angle in degrees")


class DroneBattery(BaseModel):
    """Battery telemetry"""
    percentage: int = Field(..., ge=0, le=100, description="Battery remaining percentage")
    voltage: float = Field(..., gt=0.0, description="Battery voltage in volts")
    current: Optional[float] = Field(None, description="Current draw in amps")
    capacity_mah: Optional[int] = Field(None, description="Total capacity in mAh")
    time_remaining_sec: Optional[int] = Field(None, description="Estimated flight time remaining in seconds")


class DroneHealth(BaseModel):
    """Health and readiness indicators"""
    is_armable: bool = Field(False, description="Can the drone be armed")
    gps_fix_ok: bool = Field(False, description="GPS position fix acquired")
    home_position_ok: bool = Field(False, description="Home position set")
    gyro_calibrated: bool = Field(False, description="Gyroscope calibration valid")
    accel_calibrated: bool = Field(False, description="Accelerometer calibration valid")
    mag_calibrated: bool = Field(False, description="Magnetometer calibration valid")
    num_satellites: int = Field(0, ge=0, description="Number of GPS satellites")


class DroneStateSchema(BaseModel):
    """
    Complete drone state snapshot
    Redis key pattern: fleet:state:{drone_id}
    """
    drone_id: str = Field(..., description="Unique drone identifier")
    callsign: str = Field(..., description="Human-readable callsign (e.g., REAPER-21)")
    protocol: Literal["MAVLINK", "COT", "DJI"] = Field(..., description="Control protocol")

    # State tracking
    flight_mode: str = Field("UNKNOWN", description="Current flight mode (e.g., STABILIZE, AUTO, RTL)")
    armed: bool = Field(False, description="Drone motors armed")
    in_flight: bool = Field(False, description="Currently airborne")
    mission_status: Literal["idle", "preflight", "flying", "landing", "charging", "error", "emergency"] = Field("idle")

    # Telemetry
    position: Optional[DronePosition] = None
    attitude: Optional[DroneAttitude] = None
    battery: Optional[DroneBattery] = None
    health: Optional[DroneHealth] = None

    # Communication
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow, description="Last telemetry update timestamp")
    signal_strength_dbm: Optional[int] = Field(None, description="Signal strength in dBm")
    connection_string: str = Field(..., description="Protocol connection string (e.g., udpin://0.0.0.0:14540)")

    # Metadata
    firmware_version: Optional[str] = None
    aircraft_type: Optional[str] = Field(None, description="Aircraft model (e.g., MQ-9, Matrice 300, PX4)")

    @validator("last_heartbeat", pre=True)
    def parse_heartbeat(cls, v):
        """Convert string timestamps to datetime"""
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MissionWaypoint(BaseModel):
    """Single waypoint in a mission"""
    waypoint_id: int = Field(..., ge=0, description="Waypoint sequence number")
    position: DronePosition
    speed_m_s: Optional[float] = Field(None, ge=0.0, description="Target speed in m/s")
    hold_time_sec: Optional[float] = Field(None, ge=0.0, description="Hold time at waypoint in seconds")
    actions: Optional[Dict[str, Any]] = Field(None, description="Actions to perform at waypoint (e.g., photo, gimbal)")


class DroneMissionSchema(BaseModel):
    """
    Mission definition for autonomous flight
    Redis key pattern: fleet:mission:{mission_id}
    """
    mission_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique mission identifier")
    mission_name: str = Field(..., description="Human-readable mission name")
    drone_id: str = Field(..., description="Assigned drone ID")

    waypoints: list[MissionWaypoint] = Field(..., min_items=1, description="Mission waypoints (must have at least 1)")
    mission_type: Literal["survey", "patrol", "delivery", "inspection", "emergency"] = Field("survey")

    # Execution tracking
    status: Literal["pending", "uploaded", "executing", "completed", "aborted", "failed"] = Field("pending")
    current_waypoint: int = Field(0, description="Current waypoint index")
    progress_percent: float = Field(0.0, ge=0.0, le=100.0, description="Mission completion percentage")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FleetCoordinationSchema(BaseModel):
    """
    Multi-drone formation and deconfliction state
    Redis key pattern: fleet:formation:{formation_id}
    """
    formation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    formation_name: str = Field(..., description="Formation name (e.g., 'Search Pattern Alpha')")
    drone_ids: list[str] = Field(..., min_items=1, description="Participating drone IDs")

    formation_type: Literal["line", "wedge", "echelon", "search_grid", "custom"] = Field("custom")
    separation_distance_m: float = Field(50.0, ge=10.0, description="Minimum separation between drones")

    # Deconfliction parameters
    altitude_separation_m: float = Field(30.0, ge=5.0, description="Vertical separation between altitude bands")
    collision_avoidance_enabled: bool = Field(True)

    status: Literal["assembling", "active", "dispersing", "aborted"] = Field("assembling")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DroneFailureModeSchema(BaseModel):
    """
    Failure mode detection and mitigation
    Redis key pattern: fleet:failure:{incident_id}
    """
    incident_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    drone_id: str = Field(..., description="Affected drone ID")

    failure_type: Literal[
        "gps_loss", "battery_critical", "signal_loss", "motor_failure",
        "sensor_malfunction", "collision_risk", "weather_abort", "geofence_breach"
    ]
    severity: Literal["warning", "critical", "emergency"]

    detected_at: datetime = Field(default_factory=datetime.utcnow)
    mitigation_action: Optional[str] = Field(None, description="Automated response taken (e.g., RTL, Land)")
    resolution_status: Literal["active", "mitigated", "resolved", "escalated"] = Field("active")

    telemetry_snapshot: Optional[DroneStateSchema] = Field(None, description="Drone state at time of failure")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
