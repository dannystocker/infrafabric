#!/usr/bin/env python3
"""
OBS Media Integration Demo Script

This script demonstrates the OBS media integration module with practical examples
for media sources, browser sources, and capture sources.

Prerequisites:
1. OBS Studio 28+ with obs-websocket 5.0+ enabled
2. Install dependencies: pip install websocket-client>=1.0.0
3. Configure OBS WebSocket in Tools > WebSocket Server Settings

Author: InfraFabric Project
License: CC BY 4.0
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from integrations.obs_media import (
    OBSMediaManager,
    MediaSourceConfig,
    BrowserSourceConfig,
    CaptureSourceConfig,
    MediaAction,
    Platform
)


def demo_media_sources(manager: OBSMediaManager):
    """Demonstrate media source creation and control."""
    print("\n=== Media Sources Demo ===")

    # Create video source with looping
    print("Creating video source...")
    video_config = MediaSourceConfig(
        local_file="/path/to/video.mp4",  # Update with your file path
        looping=True,
        restart_on_activate=True,
        speed_percent=100
    )

    try:
        result = manager.media.create_media_source("MainScene", "DemoVideo", video_config)
        print(f"✓ Created video source: {result.get('inputUuid')}")

        # Control playback
        print("Playing video...")
        manager.media.trigger_media_action("DemoVideo", MediaAction.PLAY)

        time.sleep(3)

        print("Pausing video...")
        manager.media.trigger_media_action("DemoVideo", MediaAction.PAUSE)

        # Get status
        status = manager.media.get_media_status("DemoVideo")
        print(f"✓ Media status: {status.get('mediaState')}")
        print(f"  Duration: {status.get('mediaDuration')}ms")
        print(f"  Position: {status.get('mediaCursor')}ms")

    except Exception as e:
        print(f"✗ Error: {e}")


def demo_browser_sources(manager: OBSMediaManager):
    """Demonstrate browser source creation."""
    print("\n=== Browser Sources Demo ===")

    # Create browser overlay
    print("Creating browser source...")
    browser_config = BrowserSourceConfig(
        url="https://example.com/overlay",
        width=1920,
        height=1080,
        fps=30,
        css="body { background: transparent; }"
    )

    try:
        result = manager.browser.create_browser_source("MainScene", "WebOverlay", browser_config)
        print(f"✓ Created browser source: {result.get('inputUuid')}")

        # Refresh browser source
        time.sleep(2)
        print("Refreshing browser source...")
        manager.browser.refresh_browser_source("WebOverlay")
        print("✓ Browser source refreshed")

    except Exception as e:
        print(f"✗ Error: {e}")


def demo_capture_sources(manager: OBSMediaManager):
    """Demonstrate capture source creation."""
    print("\n=== Capture Sources Demo ===")

    # Create window capture
    print("Creating window capture...")
    window_config = CaptureSourceConfig(
        window="[chrome.exe]:Google Chrome",  # Update for your platform
        capture_method="auto",
        cursor=True
    )

    try:
        result = manager.capture.create_window_capture("MainScene", "BrowserWindow", window_config)
        print(f"✓ Created window capture: {result.get('inputUuid')}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Create display capture
    print("Creating display capture...")
    display_config = CaptureSourceConfig(
        monitor_id="\\\\?\\DISPLAY#Default_Monitor#00000001",  # Windows example
        cursor=True
    )

    try:
        result = manager.capture.create_display_capture("MainScene", "PrimaryMonitor", display_config)
        print(f"✓ Created display capture: {result.get('inputUuid')}")
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_witness_logging(manager: OBSMediaManager):
    """Demonstrate IF.witness audit logging."""
    print("\n=== IF.witness Audit Logging Demo ===")

    # Get all audit logs
    logs = manager.client.get_witness_logs()
    print(f"\nTotal operations logged: {len(logs)}")

    # Display recent logs
    print("\nRecent operations:")
    for log in logs[-5:]:
        status = "✓" if log['success'] else "✗"
        print(f"{status} [{log['timestamp']}] {log['operation']}: {log['input_name']}")
        if log['error_message']:
            print(f"  Error: {log['error_message']}")

    # Export to file
    log_file = "/tmp/obs_audit_log.json"
    manager.client.export_witness_logs(log_file)
    print(f"\n✓ Audit logs exported to: {log_file}")


def main():
    """Run all demos."""
    print("=" * 60)
    print("OBS Media Integration Demo")
    print("=" * 60)

    # Configuration
    OBS_HOST = "localhost"
    OBS_PORT = 4455
    OBS_PASSWORD = None  # Set if you configured a password in OBS
    PLATFORM = Platform.WINDOWS  # Change based on your OS

    # Connect to OBS
    print(f"\nConnecting to OBS at {OBS_HOST}:{OBS_PORT}...")

    try:
        with OBSMediaManager(
            host=OBS_HOST,
            port=OBS_PORT,
            password=OBS_PASSWORD,
            platform=PLATFORM,
            enable_witness=True
        ) as manager:
            print("✓ Connected to OBS WebSocket")

            # Run demos
            demo_media_sources(manager)
            demo_browser_sources(manager)
            demo_capture_sources(manager)
            demo_witness_logging(manager)

            print("\n" + "=" * 60)
            print("Demo completed successfully!")
            print("=" * 60)

    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure OBS Studio is running")
        print("2. Enable WebSocket server in Tools > WebSocket Server Settings")
        print("3. Verify host, port, and password are correct")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
