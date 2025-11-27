"""
InfraFabric Air Vertical - Schema Validation Tests
Tests for Pydantic schemas following S2 "No Schema, No Write" policy
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from infrafabric.state.air_schema import (
    DronePosition,
    DroneAttitude,
    DroneBattery,
    DroneHealth,
    DroneStateSchema,
    MissionWaypoint,
    DroneMissionSchema,
    FleetCoordinationSchema,
    DroneFailureModeSchema
)


class TestDronePosition:
    """Test DronePosition schema validation"""

    def test_valid_position(self):
        """Valid position should pass validation"""
        pos = DronePosition(
            latitude=37.7749,
            longitude=-122.4194,
            altitude_msl=100.0,
            altitude_rel=50.0,
            heading=45.0
        )
        assert pos.latitude == 37.7749
        assert pos.longitude == -122.4194
        assert pos.altitude_msl == 100.0
        assert pos.heading == 45.0

    def test_invalid_latitude(self):
        """Latitude outside -90 to +90 should fail"""
        with pytest.raises(ValidationError):
            DronePosition(
                latitude=200.0,  # Invalid
                longitude=-122.4194,
                altitude_msl=100.0
            )

    def test_invalid_longitude(self):
        """Longitude outside -180 to +180 should fail"""
        with pytest.raises(ValidationError):
            DronePosition(
                latitude=37.7749,
                longitude=-200.0,  # Invalid
                altitude_msl=100.0
            )

    def test_heading_range(self):
        """Heading must be 0-360"""
        with pytest.raises(ValidationError):
            DronePosition(
                latitude=37.7749,
                longitude=-122.4194,
                altitude_msl=100.0,
                heading=400.0  # Invalid
            )


class TestDroneBattery:
    """Test DroneBattery schema validation"""

    def test_valid_battery(self):
        """Valid battery data should pass"""
        battery = DroneBattery(
            percentage=75,
            voltage=24.3,
            current=5.2,
            capacity_mah=5000
        )
        assert battery.percentage == 75
        assert battery.voltage == 24.3

    def test_percentage_bounds(self):
        """Battery percentage must be 0-100"""
        with pytest.raises(ValidationError):
            DroneBattery(percentage=150, voltage=24.0)


class TestDroneStateSchema:
    """Test complete DroneStateSchema"""

    def test_minimal_valid_state(self):
        """Minimal valid state should pass"""
        state = DroneStateSchema(
            drone_id="test-drone-01",
            callsign="TEST-01",
            protocol="MAVLINK",
            connection_string="udpin://0.0.0.0:14540"
        )
        assert state.drone_id == "test-drone-01"
        assert state.protocol == "MAVLINK"
        assert state.mission_status == "idle"

    def test_complete_state(self):
        """Complete state with all fields should pass"""
        state = DroneStateSchema(
            drone_id="test-drone-01",
            callsign="ALPHA-01",
            protocol="MAVLINK",
            flight_mode="AUTO",
            armed=True,
            in_flight=True,
            mission_status="flying",
            position=DronePosition(
                latitude=37.7749,
                longitude=-122.4194,
                altitude_msl=100.0,
                heading=45.0
            ),
            attitude=DroneAttitude(
                roll=5.0,
                pitch=-2.0,
                yaw=45.0
            ),
            battery=DroneBattery(
                percentage=75,
                voltage=24.3
            ),
            health=DroneHealth(
                is_armable=True,
                gps_fix_ok=True,
                home_position_ok=True,
                gyro_calibrated=True,
                accel_calibrated=True,
                mag_calibrated=True,
                num_satellites=12
            ),
            connection_string="udpin://0.0.0.0:14540",
            firmware_version="PX4 v1.14.0",
            aircraft_type="Quadcopter"
        )
        assert state.armed is True
        assert state.in_flight is True
        assert state.position.latitude == 37.7749
        assert state.battery.percentage == 75
        assert state.health.num_satellites == 12

    def test_invalid_protocol(self):
        """Invalid protocol should fail"""
        with pytest.raises(ValidationError):
            DroneStateSchema(
                drone_id="test-drone-01",
                callsign="TEST-01",
                protocol="INVALID",  # Not in Literal["MAVLINK", "COT", "DJI"]
                connection_string="test"
            )


class TestDroneMissionSchema:
    """Test DroneMissionSchema"""

    def test_valid_mission(self):
        """Valid mission with waypoints should pass"""
        mission = DroneMissionSchema(
            mission_name="Survey Mission Alpha",
            drone_id="alpha-01",
            waypoints=[
                MissionWaypoint(
                    waypoint_id=0,
                    position=DronePosition(
                        latitude=37.7749,
                        longitude=-122.4194,
                        altitude_msl=100.0
                    )
                ),
                MissionWaypoint(
                    waypoint_id=1,
                    position=DronePosition(
                        latitude=37.7750,
                        longitude=-122.4195,
                        altitude_msl=100.0
                    )
                )
            ],
            mission_type="survey"
        )
        assert len(mission.waypoints) == 2
        assert mission.mission_type == "survey"
        assert mission.status == "pending"

    def test_empty_waypoints_fails(self):
        """Mission with no waypoints should fail"""
        with pytest.raises(ValidationError):
            DroneMissionSchema(
                mission_name="Empty Mission",
                drone_id="alpha-01",
                waypoints=[],  # Must have at least 1
                mission_type="survey"
            )


class TestFleetCoordinationSchema:
    """Test FleetCoordinationSchema"""

    def test_valid_formation(self):
        """Valid formation should pass"""
        formation = FleetCoordinationSchema(
            formation_name="Search Pattern Alpha",
            drone_ids=["alpha-01", "bravo-02", "charlie-03"],
            formation_type="search_grid",
            separation_distance_m=50.0
        )
        assert len(formation.drone_ids) == 3
        assert formation.formation_type == "search_grid"

    def test_empty_drone_list_fails(self):
        """Formation with no drones should fail"""
        with pytest.raises(ValidationError):
            FleetCoordinationSchema(
                formation_name="Empty Formation",
                drone_ids=[],  # Must have at least 1
                formation_type="line"
            )


class TestDroneFailureModeSchema:
    """Test DroneFailureModeSchema"""

    def test_valid_failure_incident(self):
        """Valid failure incident should pass"""
        incident = DroneFailureModeSchema(
            drone_id="alpha-01",
            failure_type="gps_loss",
            severity="critical",
            mitigation_action="Switch to optical flow",
            resolution_status="mitigated"
        )
        assert incident.failure_type == "gps_loss"
        assert incident.severity == "critical"

    def test_invalid_failure_type(self):
        """Invalid failure type should fail"""
        with pytest.raises(ValidationError):
            DroneFailureModeSchema(
                drone_id="alpha-01",
                failure_type="invalid_type",
                severity="critical"
            )


def test_schema_json_serialization():
    """Test that schemas can be serialized to JSON"""
    state = DroneStateSchema(
        drone_id="test-01",
        callsign="TEST-01",
        protocol="MAVLINK",
        connection_string="udp://test",
        position=DronePosition(
            latitude=37.7749,
            longitude=-122.4194,
            altitude_msl=100.0
        )
    )

    # Should serialize to JSON without errors
    json_data = state.model_dump_json()
    assert isinstance(json_data, str)
    assert "test-01" in json_data
    assert "37.7749" in json_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
