"""
InfraFabric Air Vertical - Complete Examples
OPERATION SKYNET demonstration scenarios
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from infrafabric.verticals.air.drone_fleet_adapter import DroneFleetAdapter
from infrafabric.state.air_schema import DroneStateSchema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: MAVLINK BASIC OPERATIONS
# ============================================================================

async def example_mavlink_basic():
    """
    Basic MAVLink operations: Connect, arm, takeoff, hover, land

    Prerequisites:
    - PX4 SITL running: make px4_sitl gazebo
    - Or real PX4/ArduPilot drone connected via UDP
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 1: MAVLink Basic Operations")
    logger.info("=" * 60)

    # Create adapter
    adapter = DroneFleetAdapter(
        protocol="MAVLINK",
        connection_string="udpin://0.0.0.0:14540",
        drone_id="px4-alpha-01"
    )

    try:
        # Connect to drone
        logger.info("Connecting to PX4 SITL...")
        connected = await adapter.connect()
        if not connected:
            logger.error("Failed to connect to drone")
            return

        # Wait for GPS lock
        logger.info("Waiting for GPS lock...")
        await asyncio.sleep(5)

        # Arm drone
        logger.info("Arming drone...")
        await adapter.execute_intent({
            "primitive": "IF.context.update",
            "action": "arm"
        })

        # Takeoff to 50m
        logger.info("Taking off to 50m...")
        await adapter.execute_intent({
            "primitive": "IF.logistics.spawn",
            "action": "takeoff",
            "params": {"altitude_m": 50}
        })

        # Wait for takeoff to complete
        await asyncio.sleep(15)

        # Read telemetry
        logger.info("Reading telemetry...")
        state = await adapter.get_state()
        if state:
            logger.info(f"✓ Drone: {state.callsign}")
            logger.info(f"✓ Position: {state.position.latitude:.6f}, {state.position.longitude:.6f}")
            logger.info(f"✓ Altitude: {state.position.altitude_msl:.1f}m MSL, {state.position.altitude_rel:.1f}m AGL")
            logger.info(f"✓ Heading: {state.position.heading:.1f}°")
            logger.info(f"✓ Battery: {state.battery.percentage}%")
            logger.info(f"✓ Flight Mode: {state.flight_mode}")
            logger.info(f"✓ Armed: {state.armed}")
            logger.info(f"✓ In Flight: {state.in_flight}")

        # Hover for 10 seconds
        logger.info("Hovering for 10 seconds...")
        await asyncio.sleep(10)

        # Land
        logger.info("Landing...")
        await adapter.execute_intent({
            "primitive": "IF.logistics.spawn",
            "action": "land"
        })

        # Wait for landing to complete
        await asyncio.sleep(10)

        logger.info("✓ Mission complete!")

    except Exception as e:
        logger.error(f"Error: {e}")
        # Emergency land
        try:
            await adapter.execute_intent({
                "primitive": "IF.logistics.spawn",
                "action": "land"
            })
        except:
            pass

    finally:
        await adapter.disconnect()


# ============================================================================
# EXAMPLE 2: MAVLINK WAYPOINT NAVIGATION
# ============================================================================

async def example_mavlink_waypoint():
    """
    MAVLink waypoint navigation with multiple goto commands

    Demonstrates:
    - Sequential waypoint navigation
    - IF.matrix.route primitive
    - State monitoring during flight
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 2: MAVLink Waypoint Navigation")
    logger.info("=" * 60)

    adapter = DroneFleetAdapter(
        protocol="MAVLINK",
        connection_string="udpin://0.0.0.0:14540",
        drone_id="px4-alpha-01"
    )

    try:
        await adapter.connect()
        await asyncio.sleep(5)

        # Arm and takeoff
        await adapter.execute_intent({"primitive": "IF.context.update", "action": "arm"})
        await adapter.execute_intent({
            "primitive": "IF.logistics.spawn",
            "action": "takeoff",
            "params": {"altitude_m": 100}
        })
        await asyncio.sleep(15)

        # Define waypoints (relative to takeoff position)
        waypoints = [
            {"lat": 47.397742, "lon": 8.545594, "alt": 100, "name": "Waypoint Alpha"},
            {"lat": 47.398242, "lon": 8.546094, "alt": 120, "name": "Waypoint Bravo"},
            {"lat": 47.398742, "lon": 8.545094, "alt": 100, "name": "Waypoint Charlie"}
        ]

        # Navigate to each waypoint
        for i, wp in enumerate(waypoints, 1):
            logger.info(f"Navigating to {wp['name']} ({i}/{len(waypoints)})")
            await adapter.execute_intent({
                "primitive": "IF.matrix.route",
                "action": "goto",
                "params": {
                    "latitude": wp["lat"],
                    "longitude": wp["lon"],
                    "altitude_m": wp["alt"],
                    "yaw": 0.0
                }
            })

            # Wait for waypoint approach (simplified)
            await asyncio.sleep(20)

            # Check position
            state = await adapter.get_state()
            if state and state.position:
                logger.info(f"✓ Current position: {state.position.latitude:.6f}, {state.position.longitude:.6f}, {state.position.altitude_msl:.1f}m")

        # Return to launch
        logger.info("Returning to launch...")
        await adapter.execute_intent({
            "primitive": "IF.logistics.spawn",
            "action": "rtl"
        })
        await asyncio.sleep(30)

        logger.info("✓ Waypoint mission complete!")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await adapter.disconnect()


# ============================================================================
# EXAMPLE 3: CURSOR-ON-TARGET INTEGRATION
# ============================================================================

async def example_cot_atak_integration():
    """
    Cursor-on-Target integration with FreeTAKServer/ATAK

    Prerequisites:
    - FreeTAKServer running on localhost:19023
    - ATAK client connected to FreeTAKServer

    Demonstrates:
    - CoT XML generation
    - Target waypoint injection
    - Position Location Information (PLI) broadcasting
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 3: Cursor-on-Target (ATAK) Integration")
    logger.info("=" * 60)

    adapter = DroneFleetAdapter(
        protocol="COT",
        connection_string="http://localhost:19023",
        drone_id="UAV-REAPER-21",
        username="admin",  # Optional
        password="password"  # Optional
    )

    try:
        # Connect (authenticate)
        logger.info("Connecting to FreeTAKServer...")
        connected = await adapter.connect()
        if not connected:
            logger.error("Failed to connect to FreeTAKServer")
            return

        # Inject waypoint marker into ATAK map
        logger.info("Injecting target waypoint into ATAK...")
        await adapter.execute_intent({
            "primitive": "IF.matrix.route",
            "action": "goto",
            "params": {
                "latitude": 35.2271,
                "longitude": -106.5733,
                "altitude_m": 2450.0,
                "yaw": 0.0
            }
        })

        # Send Position Location Information (PLI)
        logger.info("Broadcasting drone PLI to ATAK...")
        cot_bridge = adapter.driver
        await cot_bridge.send_pli(
            latitude=35.2271,
            longitude=-106.5733,
            altitude_m=2450.0,
            callsign="REAPER-21"
        )

        # Simulate drone movement (send PLI updates)
        for i in range(5):
            # Update position (simulated movement)
            lat = 35.2271 + (i * 0.0001)
            lon = -106.5733 + (i * 0.0001)
            alt = 2450.0 + (i * 10)

            logger.info(f"Sending PLI update {i+1}/5: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
            await cot_bridge.send_pli(
                latitude=lat,
                longitude=lon,
                altitude_m=alt,
                callsign="REAPER-21"
            )

            await asyncio.sleep(2)

        logger.info("✓ CoT integration complete!")
        logger.info("Check ATAK client - you should see drone icon moving on map")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await adapter.disconnect()


# ============================================================================
# EXAMPLE 4: DJI MQTT TELEMETRY MONITORING
# ============================================================================

async def example_dji_telemetry():
    """
    DJI MQTT telemetry monitoring

    Prerequisites:
    - MQTT broker running
    - DJI Dock/drone configured to publish to broker

    Demonstrates:
    - MQTT connection
    - Real-time telemetry ingestion
    - DJI-specific commands
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 4: DJI MQTT Telemetry Monitoring")
    logger.info("=" * 60)

    adapter = DroneFleetAdapter(
        protocol="DJI",
        connection_string="mqtt://localhost:1883",  # Use mqtt+tls:// for production
        drone_id="matrice-300-01",
        gateway_sn="DOCK123456",
        username="dji_user",  # Optional
        password="dji_password"  # Optional
    )

    try:
        # Connect to MQTT broker
        logger.info("Connecting to DJI MQTT broker...")
        connected = await adapter.connect()
        if not connected:
            logger.error("Failed to connect to MQTT broker")
            return

        # Wait for telemetry to start flowing
        logger.info("Waiting for telemetry data...")
        await asyncio.sleep(10)

        # Monitor telemetry for 30 seconds
        for i in range(6):
            state = await adapter.get_state()
            if state:
                logger.info(f"--- Telemetry Update {i+1}/6 ---")
                logger.info(f"Drone: {state.callsign}")
                logger.info(f"Protocol: {state.protocol}")

                if state.position:
                    logger.info(f"Position: {state.position.latitude:.6f}, {state.position.longitude:.6f}")
                    logger.info(f"Altitude: {state.position.altitude_msl:.1f}m")
                    logger.info(f"Heading: {state.position.heading:.1f}°")

                if state.attitude:
                    logger.info(f"Attitude: R={state.attitude.roll:.1f}° P={state.attitude.pitch:.1f}° Y={state.attitude.yaw:.1f}°")

                if state.battery:
                    logger.info(f"Battery: {state.battery.percentage}% ({state.battery.voltage:.1f}V)")

                logger.info(f"Last heartbeat: {state.last_heartbeat}")
            else:
                logger.warning("No telemetry data received yet")

            await asyncio.sleep(5)

        # Example: Return aircraft to dock
        logger.info("Commanding aircraft to return to dock...")
        await adapter.execute_intent({
            "primitive": "IF.logistics.spawn",
            "action": "rtl"
        })

        logger.info("✓ DJI telemetry monitoring complete!")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await adapter.disconnect()


# ============================================================================
# EXAMPLE 5: EMERGENCY PROCEDURES
# ============================================================================

async def example_emergency_procedures():
    """
    Emergency procedures demonstration

    Demonstrates:
    - IF.process.kill() primitive
    - Emergency landing
    - RTL on battery critical
    - Watchdog monitoring

    ⚠️  WARNING: Only run in simulation!
    """
    logger.info("=" * 60)
    logger.info("EXAMPLE 5: Emergency Procedures (SIMULATION ONLY)")
    logger.info("=" * 60)

    adapter = DroneFleetAdapter(
        protocol="MAVLINK",
        connection_string="udpin://0.0.0.0:14540",
        drone_id="px4-emergency-test"
    )

    try:
        await adapter.connect()
        await asyncio.sleep(5)

        # Arm and takeoff
        await adapter.execute_intent({"primitive": "IF.context.update", "action": "arm"})
        await adapter.execute_intent({
            "primitive": "IF.logistics.spawn",
            "action": "takeoff",
            "params": {"altitude_m": 50}
        })
        await asyncio.sleep(15)

        # Simulate emergency scenario
        logger.warning("=" * 60)
        logger.warning("SIMULATING EMERGENCY SCENARIO")
        logger.warning("=" * 60)

        # Check battery
        state = await adapter.get_state()
        if state and state.battery:
            battery_pct = state.battery.percentage
            logger.info(f"Battery level: {battery_pct}%")

            if battery_pct < 25:
                logger.warning("⚠️  Battery critical - initiating RTL")
                await adapter.execute_intent({
                    "primitive": "IF.logistics.spawn",
                    "action": "rtl"
                })
            elif battery_pct < 10:
                logger.critical("⚠️  Battery emergency - landing immediately")
                await adapter.execute_intent({
                    "primitive": "IF.logistics.spawn",
                    "action": "land"
                })

        # Demonstrate kill switch (ONLY IN SIMULATION!)
        logger.critical("=" * 60)
        logger.critical("⚠️  DEMONSTRATING KILL SWITCH (SIMULATION ONLY)")
        logger.critical("⚠️  NEVER USE ON REAL DRONE UNLESS ABSOLUTE EMERGENCY")
        logger.critical("=" * 60)

        # Uncomment to test kill switch in simulation:
        # await adapter.execute_intent({"primitive": "IF.process.kill"})
        # logger.critical("Kill command sent - motors disabled, drone falling")

        # Instead, do safe landing
        logger.info("Executing safe landing instead...")
        await adapter.execute_intent({
            "primitive": "IF.logistics.spawn",
            "action": "land"
        })
        await asyncio.sleep(10)

        logger.info("✓ Emergency procedures demonstration complete")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await adapter.disconnect()


# ============================================================================
# MAIN RUNNER
# ============================================================================

async def main():
    """Run all examples"""
    examples = [
        ("MAVLink Basic Operations", example_mavlink_basic),
        ("MAVLink Waypoint Navigation", example_mavlink_waypoint),
        ("CoT/ATAK Integration", example_cot_atak_integration),
        ("DJI MQTT Telemetry", example_dji_telemetry),
        ("Emergency Procedures", example_emergency_procedures)
    ]

    print("\n" + "=" * 60)
    print("INFRAFABRIC AIR VERTICAL - OPERATION SKYNET")
    print("Example Demonstrations")
    print("=" * 60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print("0. Run all examples")
    print("=" * 60)

    try:
        choice = input("\nSelect example (0-5): ").strip()

        if choice == "0":
            for name, example_func in examples:
                print(f"\n\nRunning: {name}")
                await example_func()
                await asyncio.sleep(2)
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            name, example_func = examples[int(choice) - 1]
            print(f"\n\nRunning: {name}")
            await example_func()
        else:
            print("Invalid choice")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        logger.error(f"Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())
