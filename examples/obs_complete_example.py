#!/usr/bin/env python3
"""
Complete OBS Streaming Example
Demonstrates streaming, virtual camera, and recording in one comprehensive example
"""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.obs_streaming import OBSStreamingController


def main():
    """Main example demonstrating all three features"""

    # ========================================================================
    # 1. SETUP & CONNECTION
    # ========================================================================
    print("=" * 70)
    print("OBS STREAMING INTEGRATION - COMPLETE EXAMPLE")
    print("=" * 70)
    print()

    # Create controller
    controller = OBSStreamingController(
        obs_host="localhost",
        obs_port=4455,
        obs_password=None  # Set if authentication is enabled
    )

    # Connect to OBS
    print("Connecting to OBS...")
    connection = controller.connect()
    print(f"✅ Connected to OBS {connection['obs_version']}")
    print()

    # ========================================================================
    # 2. STREAMING EXAMPLE
    # ========================================================================
    print("=" * 70)
    print("FEATURE 1: STREAMING TO TWITCH/YOUTUBE/CUSTOM RTMP")
    print("=" * 70)
    print()

    # Example 1: Twitch streaming
    print("Example 1: Stream to Twitch")
    print("-" * 70)
    print("""
    controller.start_stream(
        service="Twitch",
        key="live_123456789_abcdefghijklmnop"
    )

    # Monitor stream health
    for i in range(10):
        status = controller.get_stream_status()
        print(f"Bitrate: {status['kbits_per_sec']} kbps")
        print(f"Dropped frames: {status['output_skipped_frames']}")
        time.sleep(5)

    controller.stop_stream()
    """)

    # Example 2: Custom RTMP server
    print()
    print("Example 2: Stream to Custom RTMP Server")
    print("-" * 70)
    print("""
    controller.start_stream(
        service="Custom",
        server="rtmp://custom-server.example.com:1935/live",
        key="secret-stream-key"
    )
    """)

    print()
    input("Press ENTER to continue to Virtual Camera example...")
    print()

    # ========================================================================
    # 3. VIRTUAL CAMERA EXAMPLE
    # ========================================================================
    print("=" * 70)
    print("FEATURE 2: VIRTUAL CAMERA FOR ZOOM/MEET/DISCORD")
    print("=" * 70)
    print()

    print("Starting OBS Virtual Camera...")
    try:
        result = controller.start_virtual_camera()
        print(f"✅ Virtual Camera started!")
        print()

        print("How to use in video conferencing apps:")
        print("  • Zoom: Video → Camera → OBS Virtual Camera")
        print("  • Google Meet: Settings → Video → OBS Virtual Camera")
        print("  • Discord: Voice & Video → Camera → OBS Virtual Camera")
        print("  • Microsoft Teams: Settings → Devices → Camera → OBS Virtual Camera")
        print()

        # Keep running for 10 seconds
        print("Virtual camera running for 10 seconds...")
        for i in range(10, 0, -1):
            status = controller.get_virtual_camera_status()
            print(f"  Status: {'Active' if status['active'] else 'Inactive'} | "
                  f"Time remaining: {i} seconds", end='\r')
            time.sleep(1)

        print()
        print()

        # Stop virtual camera
        print("Stopping virtual camera...")
        controller.stop_virtual_camera()
        print("✅ Virtual camera stopped")

    except Exception as e:
        print(f"❌ Virtual camera error: {e}")

    print()
    input("Press ENTER to continue to Recording example...")
    print()

    # ========================================================================
    # 4. RECORDING EXAMPLE
    # ========================================================================
    print("=" * 70)
    print("FEATURE 3: LOCAL RECORDING WITH PAUSE/RESUME")
    print("=" * 70)
    print()

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"example_recording_{timestamp}.mkv"

    print(f"Starting recording: {filename}")
    try:
        result = controller.start_recording(filename=filename, format="mkv")
        print(f"✅ Recording started!")
        print()

        # Record for 10 seconds
        print("Recording for 10 seconds...")
        for i in range(10):
            status = controller.get_record_status()
            print(f"  [{status['timecode']}] Size: {status['bytes'] / 1024 / 1024:.2f} MB",
                  end='\r')
            time.sleep(1)

        print()
        print()

        # Pause recording
        print("Pausing recording...")
        controller.pause_recording()
        print("✅ Recording paused (simulating a break)")
        time.sleep(3)
        print()

        # Resume recording
        print("Resuming recording...")
        controller.resume_recording()
        print("✅ Recording resumed")
        print()

        # Record for 5 more seconds
        print("Recording for 5 more seconds...")
        for i in range(5):
            status = controller.get_record_status()
            print(f"  [{status['timecode']}] Size: {status['bytes'] / 1024 / 1024:.2f} MB",
                  end='\r')
            time.sleep(1)

        print()
        print()

        # Stop recording
        print("Stopping recording...")
        result = controller.stop_recording()
        print(f"✅ Recording stopped!")

        if 'output_path' in result:
            print(f"   Saved to: {result['output_path']}")

        final_stats = result.get('final_stats', {})
        print(f"   Duration: {final_stats.get('timecode', 'N/A')}")
        print(f"   Size: {final_stats.get('bytes', 0) / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"❌ Recording error: {e}")

    print()
    print()

    # ========================================================================
    # 5. IF.WITNESS PROVENANCE TRACKING
    # ========================================================================
    print("=" * 70)
    print("IF.WITNESS PROVENANCE CHAIN")
    print("=" * 70)
    print()

    chain = controller.get_witness_chain()
    print(f"Total events logged: {len(chain)}")
    print()

    print("Event chain:")
    for i, event in enumerate(chain, 1):
        print(f"{i:2d}. {event['event_type']:30s} @ {event['timestamp']}")
        print(f"    Hash: {event['hash'][:32]}...")

    print()

    # Verify chain integrity
    is_valid = controller.verify_witness_chain()
    print(f"Chain integrity: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print()

    # Export report
    report_file = f"obs_provenance_report_{int(time.time())}.json"
    controller.export_witness_report(report_file)
    print(f"📄 Provenance report exported to: {report_file}")
    print()

    # ========================================================================
    # 6. OBS PERFORMANCE STATISTICS
    # ========================================================================
    print("=" * 70)
    print("OBS PERFORMANCE STATISTICS")
    print("=" * 70)
    print()

    stats = controller.get_stats()
    print(f"CPU Usage:       {stats['cpu_usage']:.1f}%")
    print(f"Memory Usage:    {stats['memory_usage_mb']:.0f} MB")
    print(f"Render FPS:      {stats['render_fps']:.1f}")
    print(f"Output FPS:      {stats['output_fps']:.1f}")
    print(f"Free Disk Space: {stats['free_disk_space_mb']:.0f} MB")
    print()

    # ========================================================================
    # 7. CLEANUP
    # ========================================================================
    print("=" * 70)
    print("CLEANUP")
    print("=" * 70)
    print()

    print("Disconnecting from OBS...")
    controller.disconnect()
    print("✅ Disconnected")
    print()

    # ========================================================================
    # 8. SUMMARY
    # ========================================================================
    print("=" * 70)
    print("EXAMPLE COMPLETE!")
    print("=" * 70)
    print()
    print("You've seen how to:")
    print("  ✅ Start/stop streaming to Twitch, YouTube, or custom RTMP")
    print("  ✅ Use OBS Virtual Camera in video conferencing apps")
    print("  ✅ Record locally with pause/resume functionality")
    print("  ✅ Monitor stream health and OBS performance")
    print("  ✅ Track all operations with IF.witness provenance chain")
    print()
    print("Next steps:")
    print("  • Read the documentation: docs/OBS/streaming-integration.md")
    print("  • Run the interactive demo: python examples/obs_streaming_demo.py")
    print("  • Run tests: python tests/test_obs_streaming.py")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Example interrupted by user")
        print()
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
