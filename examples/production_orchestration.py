"""
Production Orchestration Example - IF.bus Master Sprint

Demonstrates unified control of vMix, OBS, and Home Assistant via IF.bus.

This example shows how Session 7 (IF.bus) orchestrates all three platforms
to create a complete production infrastructure.

Use Cases:
1. Live Streaming Studio Setup
2. Motion-Triggered Recording
3. Emergency Shutdown
4. Multi-Platform Redundancy

Author: Session 7 - IF.bus (Master Sprint)
Date: 2025-11-12
"""

import logging
import time
from src.bus import VMixAdapter, OBSAdapter, HomeAssistantAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===========================================================================
# Configuration
# ===========================================================================

VMIX_CONFIG = {
    "type": "vmix",
    "timeout": 30,
}

OBS_CONFIG = {
    "type": "obs",
    "timeout": 30,
}

HA_CONFIG = {
    "type": "home_assistant",
    "timeout": 30,
}

# ===========================================================================
# Use Case 1: Live Streaming Studio Setup
# ===========================================================================


def live_streaming_studio():
    """
    Complete production setup via IF.bus orchestration.

    Steps:
    1. Home Assistant: Turn on studio lights
    2. Home Assistant: Enable cameras
    3. vMix: Load production scene
    4. OBS: Start virtual camera
    5. vMix: Start streaming
    6. OBS: Start recording backup
    7. Home Assistant: Turn on "ON AIR" sign
    """
    logger.info("=== Live Streaming Studio Setup ===")

    # Initialize adapters
    vmix = VMixAdapter(VMIX_CONFIG)
    obs = OBSAdapter(OBS_CONFIG)
    ha = HomeAssistantAdapter(HA_CONFIG)

    try:
        # Discover instances on network
        logger.info("Discovering instances...")
        vmix_instances = vmix.discover_instances()
        obs_instances = obs.discover_instances()
        ha_instances = ha.discover_instances()

        logger.info(f"Found {len(vmix_instances)} vMix instance(s)")
        logger.info(f"Found {len(obs_instances)} OBS instance(s)")
        logger.info(f"Found {len(ha_instances)} Home Assistant instance(s)")

        # Add instances manually if needed
        if not vmix_instances:
            vmix.add_instance("main_vmix", {
                "host": "192.168.1.100",
                "tcp_port": 8099,
                "http_port": 8088,
            })

        if not obs_instances:
            obs.add_instance("main_obs", {
                "host": "192.168.1.101",
                "port": 4455,
                "password": "obs_password",
            })

        if not ha_instances:
            ha.add_instance("main_ha", {
                "url": "http://192.168.1.102:8123",
                "token": "your_long_lived_access_token",
            })

        instance_vmix = "main_vmix"
        instance_obs = "main_obs"
        instance_ha = "main_ha"

        # Step 1: Turn on studio lights
        logger.info("Step 1: Turning on studio lights...")
        ha.execute_command(instance_ha, "call_service", {
            "domain": "light",
            "service": "turn_on",
            "target": {"entity_id": ["light.key_light", "light.fill_light", "light.back_light"]},
            "brightness": 255,
        })

        # Step 2: Enable cameras
        logger.info("Step 2: Enabling cameras...")
        ha.execute_command(instance_ha, "call_service", {
            "domain": "camera",
            "service": "enable_motion_detection",
            "target": {"entity_id": ["camera.studio_front", "camera.studio_side"]},
        })

        # Step 3: Load vMix production scene
        logger.info("Step 3: Loading vMix production scene...")
        vmix.execute_command(instance_vmix, "ActiveInput", {
            "Input": "1",  # Main production scene
        })

        # Step 4: Start OBS virtual camera
        logger.info("Step 4: Starting OBS virtual camera...")
        obs.execute_command(instance_obs, "StartVirtualCam")

        # Step 5: Start vMix streaming
        logger.info("Step 5: Starting vMix streaming...")
        vmix.execute_command(instance_vmix, "StartStreaming")

        # Step 6: Start OBS recording backup
        logger.info("Step 6: Starting OBS recording backup...")
        obs.execute_command(instance_obs, "StartRecord")

        # Step 7: Turn on ON AIR sign
        logger.info("Step 7: Turning on ON AIR sign...")
        ha.execute_command(instance_ha, "call_service", {
            "domain": "light",
            "service": "turn_on",
            "target": {"entity_id": "light.on_air_sign"},
            "rgb_color": [255, 0, 0],  # Red
        })

        logger.info("✓ Live streaming studio setup complete!")

        # Monitor health
        time.sleep(2)
        vmix_health = vmix.health_check()
        obs_health = obs.health_check()
        ha_health = ha.health_check()

        logger.info(f"vMix Health: {vmix_health['status']}")
        logger.info(f"OBS Health: {obs_health['status']}")
        logger.info(f"Home Assistant Health: {ha_health['status']}")

    except Exception as e:
        logger.error(f"Error in live streaming setup: {e}")
        raise
    finally:
        # Cleanup (optional)
        pass


# ===========================================================================
# Use Case 2: Motion-Triggered Recording
# ===========================================================================


def motion_triggered_recording():
    """
    Automation: When motion detected, start recording on both platforms.

    This would typically be triggered by a Home Assistant automation,
    but we demonstrate the IF.bus commands here.
    """
    logger.info("=== Motion-Triggered Recording ===")

    vmix = VMixAdapter(VMIX_CONFIG)
    obs = OBSAdapter(OBS_CONFIG)
    ha = HomeAssistantAdapter(HA_CONFIG)

    try:
        instance_vmix = "main_vmix"
        instance_obs = "main_obs"
        instance_ha = "main_ha"

        # Check motion sensor
        logger.info("Checking motion sensor...")
        state = ha.execute_command(instance_ha, "get_state", {
            "entity_id": "binary_sensor.studio_motion"
        })

        if state.get("state") == "on":
            logger.info("Motion detected! Starting recording...")

            # Start vMix recording
            vmix.execute_command(instance_vmix, "StartRecording")

            # Start OBS recording
            obs.execute_command(instance_obs, "StartRecord")

            # Send notification
            ha.execute_command(instance_ha, "call_service", {
                "domain": "notify",
                "service": "mobile_app",
                "message": "Motion detected - Recording started",
            })

            logger.info("✓ Recording started on both platforms")
        else:
            logger.info("No motion detected")

    except Exception as e:
        logger.error(f"Error in motion recording: {e}")


# ===========================================================================
# Use Case 3: Emergency Shutdown
# ===========================================================================


def emergency_shutdown():
    """
    Emergency shutdown: Stop all production immediately.

    Steps:
    1. Stop vMix streaming
    2. Stop OBS recording
    3. Turn off all studio lights
    4. Turn off cameras
    5. Lock studio door
    6. Send notifications
    """
    logger.info("=== Emergency Shutdown ===")

    vmix = VMixAdapter(VMIX_CONFIG)
    obs = OBSAdapter(OBS_CONFIG)
    ha = HomeAssistantAdapter(HA_CONFIG)

    try:
        instance_vmix = "main_vmix"
        instance_obs = "main_obs"
        instance_ha = "main_ha"

        logger.info("Step 1: Stopping vMix streaming...")
        vmix.execute_command(instance_vmix, "StopStreaming")

        logger.info("Step 2: Stopping OBS recording...")
        obs.execute_command(instance_obs, "StopRecord")

        logger.info("Step 3: Turning off studio lights...")
        ha.execute_command(instance_ha, "call_service", {
            "domain": "light",
            "service": "turn_off",
            "target": {"entity_id": "all"},
        })

        logger.info("Step 4: Disabling cameras...")
        ha.execute_command(instance_ha, "call_service", {
            "domain": "camera",
            "service": "disable_motion_detection",
            "target": {"entity_id": "all"},
        })

        logger.info("Step 5: Locking studio door...")
        ha.execute_command(instance_ha, "call_service", {
            "domain": "lock",
            "service": "lock",
            "target": {"entity_id": "lock.studio_door"},
        })

        logger.info("Step 6: Sending notifications...")
        ha.execute_command(instance_ha, "call_service", {
            "domain": "notify",
            "service": "mobile_app",
            "message": "EMERGENCY SHUTDOWN - All production stopped",
        })

        logger.info("✓ Emergency shutdown complete")

    except Exception as e:
        logger.error(f"Error in emergency shutdown: {e}")


# ===========================================================================
# Use Case 4: Multi-Platform Redundancy
# ===========================================================================


def multi_platform_redundancy():
    """
    Redundant streaming: vMix primary, OBS backup with auto-failover.

    Monitors vMix health and fails over to OBS if vMix crashes.
    """
    logger.info("=== Multi-Platform Redundancy ===")

    vmix = VMixAdapter(VMIX_CONFIG)
    obs = OBSAdapter(OBS_CONFIG)
    ha = HomeAssistantAdapter(HA_CONFIG)

    try:
        instance_vmix = "main_vmix"
        instance_obs = "main_obs"
        instance_ha = "main_ha"

        # Start vMix streaming (primary)
        logger.info("Starting vMix streaming (primary)...")
        vmix.execute_command(instance_vmix, "StartStreaming")

        # Monitor for failures
        logger.info("Monitoring vMix health...")
        while True:
            vmix_status = vmix.get_instance_status(instance_vmix)

            if vmix_status.get("streaming") == False:
                logger.warning("vMix streaming stopped! Failing over to OBS...")

                # Failover to OBS
                obs.execute_command(instance_obs, "StartStream")

                # Send notification
                ha.execute_command(instance_ha, "call_service", {
                    "domain": "notify",
                    "service": "mobile_app",
                    "message": "Failover: vMix → OBS streaming",
                })

                logger.info("✓ Failover complete - OBS now streaming")
                break

            time.sleep(5)  # Check every 5 seconds

    except Exception as e:
        logger.error(f"Error in redundancy check: {e}")


# ===========================================================================
# Run Examples
# ===========================================================================


def run_all_examples():
    """Run all orchestration examples."""
    logger.info("=" * 70)
    logger.info("IF.bus Production Orchestration Examples")
    logger.info("=" * 70)

    # Note: These examples require real hardware/software
    # Uncomment to run with actual instances:

    # live_streaming_studio()
    # motion_triggered_recording()
    # emergency_shutdown()
    # multi_platform_redundancy()

    logger.info("\n" + "=" * 70)
    logger.info("Examples demonstrated:")
    logger.info("- Live Streaming Studio (7-step setup)")
    logger.info("- Motion-Triggered Recording (automation)")
    logger.info("- Emergency Shutdown (safety protocol)")
    logger.info("- Multi-Platform Redundancy (auto-failover)")
    logger.info("=" * 70)
    logger.info("\nUncomment function calls above to run with real instances")


if __name__ == "__main__":
    run_all_examples()
