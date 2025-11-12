"""
Home Assistant Notifications Integration - Usage Examples

This module provides practical examples demonstrating all features of the
HomeAssistantNotifications integration for InfraFabric.

Author: InfraFabric Team
Part of: MASTER INTEGRATION SPRINT - Session 2 (WebRTC)
"""

import os
from datetime import datetime
from typing import List, Dict
from ha_notifications import HomeAssistantNotifications, HomeAssistantError


def example_1_basic_setup():
    """Example 1: Basic setup and verification"""
    print("\n=== Example 1: Basic Setup ===\n")

    # Initialize with environment variables
    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL", "http://homeassistant.local:8123"),
        ha_token=os.getenv("HA_TOKEN", "your_token_here")
    )

    # Verify connection
    if ha.health_check():
        print("✓ Connected to Home Assistant")
        status = ha.get_status()
        print(f"  Version: {status.get('version', 'unknown')}")
    else:
        print("✗ Cannot reach Home Assistant")
        return

    # Send test notification
    ha.send_notification(
        message="InfraFabric integration is active!",
        title="Integration Test"
    )
    print("✓ Test notification sent")


def example_2_notifications():
    """Example 2: Various notification types"""
    print("\n=== Example 2: Notifications ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    # Simple notification
    ha.send_notification(
        message="Simple notification message",
        title="Test Notification"
    )
    print("✓ Simple notification sent")

    # Mobile notification with actions
    ha.send_notification(
        message="Stream is starting in 5 minutes",
        title="Pre-Stream Alert",
        service="mobile_app_iphone",
        data={
            "actions": [
                {"action": "CONFIRM", "title": "Ready"},
                {"action": "DELAY", "title": "Delay 10min"}
            ],
            "group": "streaming",
            "tag": "pre_stream"
        }
    )
    print("✓ Mobile notification with actions sent")

    # Notification with image
    ha.send_notification(
        message="Thumbnail preview available",
        title="Recording Complete",
        data={
            "image": "/local/thumbnails/latest.jpg",
            "group": "recordings"
        }
    )
    print("✓ Notification with image sent")

    # Persistent notification
    ha.send_persistent_notification(
        message="InfraFabric monitoring active",
        title="System Status",
        notification_id="if_status"
    )
    print("✓ Persistent notification created")


def example_3_webhooks_and_events():
    """Example 3: Webhooks and events"""
    print("\n=== Example 3: Webhooks & Events ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    # Trigger webhook
    ha.trigger_webhook(
        webhook_id="if_test_webhook",
        data={
            "test": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "infrafabric"
        }
    )
    print("✓ Webhook triggered: if_test_webhook")

    # Fire custom event
    ha.fire_event(
        event_type="if_webrtc_peer_connected",
        event_data={
            "peer_id": "agent-example",
            "latency_ms": 42.5,
            "connection_type": "p2p",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    print("✓ Event fired: if_webrtc_peer_connected")


def example_4_service_calls():
    """Example 4: Calling Home Assistant services"""
    print("\n=== Example 4: Service Calls ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    # Turn on lights
    ha.call_service(
        domain="light",
        service="turn_on",
        target={"entity_id": "light.studio_lights"},
        service_data={"brightness": 255, "rgb_color": [255, 255, 255]}
    )
    print("✓ Lights turned on")

    # Lock door
    ha.call_service(
        domain="lock",
        service="lock",
        target={"entity_id": "lock.studio_door"}
    )
    print("✓ Studio door locked")

    # Trigger automation
    ha.call_service(
        domain="automation",
        service="trigger",
        target={"entity_id": "automation.test_automation"}
    )
    print("✓ Automation triggered")


def example_5_streaming_workflow():
    """Example 5: Complete streaming workflow"""
    print("\n=== Example 5: Streaming Workflow ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    platform = "vmix"
    destination = "twitch"

    print("Starting stream...")

    # 1. Notify stream starting
    ha.notify_stream_started(platform, destination)
    print("  ✓ Notification sent")

    # 2. Turn on ON AIR light
    ha.set_on_air_status(True)
    print("  ✓ ON AIR light activated")

    # 3. Control studio lights
    ha.control_studio_lights(
        state="on",
        brightness=255,
        color=[255, 255, 255]
    )
    print("  ✓ Studio lights set")

    # 4. Trigger webhook
    ha.trigger_production_automation(
        action="stream_started",
        params={"platform": platform, "destination": destination}
    )
    print("  ✓ Production automation triggered")

    # 5. Fire event
    ha.fire_event(
        event_type="if_stream_active",
        event_data={"platform": platform, "destination": destination}
    )
    print("  ✓ Event fired")

    print("\nStream is live!")

    # Simulate stream ending
    print("\nStopping stream...")

    # 6. Notify stream stopped
    ha.notify_stream_stopped(platform, destination, duration_minutes=90)
    print("  ✓ Stop notification sent")

    # 7. Turn off ON AIR light
    ha.set_on_air_status(False)
    print("  ✓ ON AIR light deactivated")

    # 8. Trigger stop webhook
    ha.trigger_production_automation(
        action="stream_stopped",
        params={"duration": 90}
    )
    print("  ✓ Stop automation triggered")

    print("\nStream ended!")


def example_6_webrtc_monitoring():
    """Example 6: WebRTC mesh monitoring"""
    print("\n=== Example 6: WebRTC Monitoring ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    # Simulate peer data
    peers = [
        {"id": "agent-1", "latency": 45.2, "packet_loss": 0.1},
        {"id": "agent-2", "latency": 52.1, "packet_loss": 0.3},
        {"id": "agent-3", "latency": 38.7, "packet_loss": 0.2},
        {"id": "agent-4", "latency": 61.5, "packet_loss": 0.5},
        {"id": "agent-5", "latency": 43.9, "packet_loss": 0.1}
    ]

    # Calculate mesh health
    peer_count = len(peers)
    avg_latency = sum(p['latency'] for p in peers) / peer_count
    avg_packet_loss = sum(p['packet_loss'] for p in peers) / peer_count

    # Determine quality
    if avg_latency < 50:
        quality = "excellent"
    elif avg_latency < 100:
        quality = "good"
    elif avg_latency < 200:
        quality = "fair"
    else:
        quality = "poor"

    print(f"Mesh Status:")
    print(f"  Peers: {peer_count}")
    print(f"  Avg Latency: {avg_latency:.1f}ms")
    print(f"  Quality: {quality}")

    # Update status
    ha.notify_webrtc_mesh_status(
        peer_count=peer_count,
        quality=quality,
        latency_avg=avg_latency
    )
    print("\n✓ Mesh status notification sent")

    # Check for quality issues
    for peer in peers:
        if peer['latency'] > 200 or peer['packet_loss'] > 5.0:
            ha.notify_webrtc_quality_alert(
                peer_id=peer['id'],
                issue="high_latency" if peer['latency'] > 200 else "packet_loss",
                latency=peer['latency'],
                packet_loss=peer['packet_loss']
            )
            print(f"✓ Quality alert sent for {peer['id']}")


def example_7_error_handling():
    """Example 7: Proper error handling"""
    print("\n=== Example 7: Error Handling ===\n")

    try:
        # Try to connect with potentially bad credentials
        ha = HomeAssistantNotifications(
            ha_url=os.getenv("HA_URL", "http://localhost:8123"),
            ha_token=os.getenv("HA_TOKEN", "invalid_token")
        )

        # Try to send notification
        ha.send_notification("Test message")
        print("✓ Notification sent successfully")

    except HomeAssistantError as e:
        print(f"✗ Home Assistant error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if Home Assistant is running")
        print("  2. Verify the URL is correct")
        print("  3. Check your access token")
        print("  4. Test with: curl http://your-ha-url:8123/api/")


def example_8_production_environment():
    """Example 8: Complete production environment setup"""
    print("\n=== Example 8: Production Environment ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    print("Setting up production environment...")

    # 1. Studio lights
    ha.control_studio_lights(
        state="on",
        brightness=255,
        color=[255, 255, 255]
    )
    print("  ✓ Studio lights: ON (white, full brightness)")

    # 2. Security
    ha.call_service(
        domain="lock",
        service="lock",
        target={"entity_id": "lock.studio_door"}
    )
    print("  ✓ Studio door: LOCKED")

    # 3. ON AIR indicator
    ha.set_on_air_status(True)
    print("  ✓ ON AIR light: ACTIVE (red)")

    # 4. Climate control
    ha.call_service(
        domain="climate",
        service="set_temperature",
        target={"entity_id": "climate.studio_ac"},
        service_data={"temperature": 22}
    )
    print("  ✓ Climate: 22°C")

    # 5. Notifications
    ha.send_notification(
        message="Production environment is ready",
        title="Studio Setup Complete",
        data={"priority": "high", "tag": "studio_status"}
    )
    print("  ✓ Team notification: SENT")

    # 6. Fire event
    ha.fire_event(
        event_type="if_production_ready",
        event_data={
            "timestamp": datetime.utcnow().isoformat(),
            "studio": "main"
        }
    )
    print("  ✓ Event fired: if_production_ready")

    print("\n✓ Production environment is READY")


def example_9_helper_methods():
    """Example 9: Using helper methods"""
    print("\n=== Example 9: Helper Methods ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    # Stream helpers
    ha.notify_stream_started("obs", "youtube")
    print("✓ notify_stream_started()")

    ha.notify_stream_stopped("obs", "youtube", 120)
    print("✓ notify_stream_stopped()")

    # WebRTC helpers
    ha.notify_webrtc_mesh_status(5, "excellent", 35.2)
    print("✓ notify_webrtc_mesh_status()")

    ha.notify_webrtc_quality_alert(
        "agent-test", "high_latency", latency=250
    )
    print("✓ notify_webrtc_quality_alert()")

    # Production helpers
    ha.trigger_production_automation(
        "start", {"scene": "main"}
    )
    print("✓ trigger_production_automation()")

    # Light helpers
    ha.control_studio_lights("on", brightness=200)
    print("✓ control_studio_lights()")

    ha.set_on_air_status(True)
    print("✓ set_on_air_status()")


def example_10_advanced_automation():
    """Example 10: Advanced automation patterns"""
    print("\n=== Example 10: Advanced Automation ===\n")

    ha = HomeAssistantNotifications(
        ha_url=os.getenv("HA_URL"),
        ha_token=os.getenv("HA_TOKEN")
    )

    # Pattern 1: Conditional notifications based on time
    hour = datetime.now().hour
    if 9 <= hour <= 17:  # Business hours
        service = "notify"  # All devices
        priority = "normal"
    else:  # After hours
        service = "mobile_app_oncall"  # Only on-call device
        priority = "high"

    ha.send_notification(
        message="WebRTC peer disconnected",
        title="Connection Alert",
        service=service,
        data={"priority": priority}
    )
    print(f"✓ Time-based notification sent ({service}, {priority})")

    # Pattern 2: Cascading automation trigger
    automation_steps = [
        {"action": "prepare", "params": {"stage": 1}},
        {"action": "validate", "params": {"stage": 2}},
        {"action": "activate", "params": {"stage": 3}}
    ]

    for step in automation_steps:
        ha.trigger_production_automation(
            step["action"],
            step["params"]
        )
        print(f"✓ Triggered: {step['action']}")

    # Pattern 3: Multi-service coordination
    services = [
        ("light", "turn_on", "light.studio_lights", {"brightness": 255}),
        ("switch", "turn_on", "switch.studio_equipment", {}),
        ("media_player", "volume_set", "media_player.studio", {"volume_level": 0.5})
    ]

    for domain, service, entity_id, data in services:
        ha.call_service(
            domain=domain,
            service=service,
            target={"entity_id": entity_id},
            service_data=data if data else None
        )
        print(f"✓ {domain}.{service} called")


# Main execution
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Home Assistant Notifications Integration - Examples")
    print("InfraFabric MASTER INTEGRATION SPRINT - Session 2")
    print("="*60)

    # Check environment variables
    if not os.getenv("HA_URL") or not os.getenv("HA_TOKEN"):
        print("\n⚠ WARNING: Please set environment variables:")
        print("  export HA_URL='http://homeassistant.local:8123'")
        print("  export HA_TOKEN='your_long_lived_token'")
        print("\nUsing defaults for demonstration...\n")

    # Run examples
    try:
        example_1_basic_setup()
        example_2_notifications()
        example_3_webhooks_and_events()
        example_4_service_calls()
        example_5_streaming_workflow()
        example_6_webrtc_monitoring()
        example_7_error_handling()
        example_8_production_environment()
        example_9_helper_methods()
        example_10_advanced_automation()

        print("\n" + "="*60)
        print("✓ All examples completed!")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        print("See documentation for troubleshooting")
