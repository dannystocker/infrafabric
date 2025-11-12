#!/usr/bin/env python3
"""
OBS Streaming Integration Demo
Demonstrates all three features: Streaming, Virtual Camera, and Recording

Usage:
    python obs_streaming_demo.py --demo streaming
    python obs_streaming_demo.py --demo virtualcam
    python obs_streaming_demo.py --demo recording
    python obs_streaming_demo.py --demo all
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.obs_streaming import (
    OBSStreamingController,
    OBSConnectionError,
    OBSStreamingError
)


def print_banner(text):
    """Print formatted banner"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_streaming(controller):
    """Demonstrate streaming functionality"""
    print_banner("DEMO 1: Streaming to Twitch/YouTube/Custom RTMP")

    print("📡 Streaming Demo")
    print("-" * 70)
    print("This demo shows how to:")
    print("  1. Start streaming to a destination (Twitch, YouTube, Custom RTMP)")
    print("  2. Monitor stream health (bitrate, dropped frames, congestion)")
    print("  3. Stop streaming and get final statistics")
    print()

    # Note: In production, NEVER hardcode stream keys!
    # Use environment variables or secure config files
    stream_key = os.getenv('TWITCH_STREAM_KEY', 'YOUR_STREAM_KEY_HERE')

    if stream_key == 'YOUR_STREAM_KEY_HERE':
        print("⚠️  No stream key configured!")
        print("   Set TWITCH_STREAM_KEY environment variable:")
        print("   export TWITCH_STREAM_KEY='live_123456789_abc'")
        print()
        print("   For this demo, we'll simulate streaming...")
        print()
        simulate = True
    else:
        simulate = False

    if not simulate:
        # Real streaming
        print("Starting stream to Twitch...")
        result = controller.start_stream(
            service="Twitch",
            key=stream_key
        )
        print(f"✅ Stream started: {result['status']}")
        print()

        # Monitor for 30 seconds
        print("Monitoring stream health for 30 seconds...")
        print()

        for i in range(6):  # 6 iterations * 5 seconds = 30 seconds
            status = controller.get_stream_status()
            stats = controller.get_stats()

            # Calculate drop rate
            drop_rate = 0
            if status['output_total_frames'] > 0:
                drop_rate = (status['output_skipped_frames'] / status['output_total_frames']) * 100

            print(f"[{i*5:2d}s] "
                  f"Bitrate: {status['kbits_per_sec']:4d} kbps | "
                  f"Dropped: {status['output_skipped_frames']:3d} ({drop_rate:.2f}%) | "
                  f"CPU: {stats['cpu_usage']:5.1f}% | "
                  f"Congestion: {status['congestion']:.2%}")

            time.sleep(5)

        print()
        print("Stopping stream...")
        result = controller.stop_stream()
        print(f"✅ Stream stopped")
        print(f"   Total frames: {result['final_stats']['output_total_frames']}")
        print(f"   Total bytes: {result['final_stats']['bytes_sent'] / 1024 / 1024:.2f} MB")
    else:
        # Simulated streaming (no actual stream)
        print("🔄 Simulating streaming (no actual broadcast)...")
        print()

        # Get current status (should show not streaming)
        status = controller.get_stream_status()
        print(f"Current status: {'Streaming' if status['streaming'] else 'Not streaming'}")
        print()

        # Show example of what real streaming would look like
        print("Example stream monitoring output:")
        print("[ 0s] Bitrate: 4500 kbps | Dropped:   0 (0.00%) | CPU:  25.3% | Congestion: 0.00%")
        print("[ 5s] Bitrate: 4502 kbps | Dropped:   2 (0.03%) | CPU:  26.1% | Congestion: 0.01%")
        print("[10s] Bitrate: 4498 kbps | Dropped:   5 (0.08%) | CPU:  25.8% | Congestion: 0.02%")
        print("[15s] Bitrate: 4505 kbps | Dropped:   8 (0.13%) | CPU:  27.2% | Congestion: 0.01%")
        print()

    print("✅ Streaming demo complete!")


def demo_virtual_camera(controller):
    """Demonstrate virtual camera functionality"""
    print_banner("DEMO 2: Virtual Camera for Zoom/Meet/Discord")

    print("📹 Virtual Camera Demo")
    print("-" * 70)
    print("This demo shows how to:")
    print("  1. Start OBS Virtual Camera")
    print("  2. Check virtual camera status")
    print("  3. Use in video conferencing apps (Zoom, Meet, Discord)")
    print("  4. Stop virtual camera")
    print()

    # Start virtual camera
    print("Starting OBS Virtual Camera...")
    try:
        result = controller.start_virtual_camera()
        print(f"✅ Virtual camera started: {result['status']}")
        print()

        # Check status
        status = controller.get_virtual_camera_status()
        print(f"Virtual Camera Status: {'✅ Active' if status['active'] else '❌ Inactive'}")
        print()

        # Instructions
        print("📌 How to use Virtual Camera:")
        print()
        print("1. Open Zoom/Meet/Discord/Teams")
        print("2. Go to Video Settings")
        print("3. Select camera: 'OBS Virtual Camera' or 'OBS-Camera'")
        print("4. Your OBS scene will appear as your webcam!")
        print()
        print("Platform-specific instructions:")
        print("  • Zoom: Video → Camera → OBS Virtual Camera")
        print("  • Google Meet: Settings → Video → OBS Virtual Camera")
        print("  • Discord: Voice & Video → Camera → OBS Virtual Camera")
        print("  • Microsoft Teams: Settings → Devices → Camera → OBS Virtual Camera")
        print()

        # Keep virtual camera running for 15 seconds
        print("Virtual camera will run for 15 seconds...")
        print("(In production, keep running as long as needed)")
        print()

        for i in range(15):
            print(f"  Running... {15-i} seconds remaining", end='\r')
            time.sleep(1)

        print()
        print()

        # Stop virtual camera
        print("Stopping virtual camera...")
        result = controller.stop_virtual_camera()
        print(f"✅ Virtual camera stopped: {result['status']}")

    except OBSStreamingError as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  • Make sure OBS is running")
        print("  • On Linux: Install v4l2loopback")
        print("  • On macOS: Check System Preferences → Security & Privacy → Camera")
        print("  • On Windows: Try running OBS as Administrator")

    print()
    print("✅ Virtual camera demo complete!")


def demo_recording(controller):
    """Demonstrate recording functionality"""
    print_banner("DEMO 3: Local Recording with Pause/Resume")

    print("🎥 Recording Demo")
    print("-" * 70)
    print("This demo shows how to:")
    print("  1. Start recording to local file")
    print("  2. Monitor recording progress")
    print("  3. Pause and resume recording")
    print("  4. Stop recording and get file path")
    print()

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"demo_recording_{timestamp}.mkv"

    # Start recording
    print(f"Starting recording: {filename}")
    try:
        result = controller.start_recording(
            filename=filename,
            format="mkv"
        )
        print(f"✅ Recording started: {result['status']}")
        print()

        # Record for 10 seconds
        print("Recording for 10 seconds...")
        for i in range(10):
            status = controller.get_record_status()
            print(f"[{status['timecode']}] "
                  f"Recording... Size: {status['bytes'] / 1024 / 1024:.2f} MB",
                  end='\r')
            time.sleep(1)

        print()
        print()

        # Pause recording
        print("Pausing recording...")
        result = controller.pause_recording()
        print(f"✅ Recording paused: {result['status']}")
        print()

        # Wait 3 seconds
        print("Paused for 3 seconds (simulating a break)...")
        time.sleep(3)
        print()

        # Resume recording
        print("Resuming recording...")
        result = controller.resume_recording()
        print(f"✅ Recording resumed: {result['status']}")
        print()

        # Record for another 5 seconds
        print("Recording for 5 more seconds...")
        for i in range(5):
            status = controller.get_record_status()
            print(f"[{status['timecode']}] "
                  f"Recording... Size: {status['bytes'] / 1024 / 1024:.2f} MB",
                  end='\r')
            time.sleep(1)

        print()
        print()

        # Stop recording
        print("Stopping recording...")
        result = controller.stop_recording()
        print(f"✅ Recording stopped: {result['status']}")

        if 'output_path' in result:
            print(f"   Saved to: {result['output_path']}")
        else:
            print(f"   Check OBS recording folder for: {filename}")

        print()
        print("Final statistics:")
        final_stats = result.get('final_stats', {})
        print(f"  Duration: {final_stats.get('timecode', 'N/A')}")
        print(f"  File size: {final_stats.get('bytes', 0) / 1024 / 1024:.2f} MB")

    except OBSStreamingError as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  • Check OBS recording settings (Settings → Output → Recording)")
        print("  • Verify recording path exists")
        print("  • Ensure sufficient disk space")

    print()
    print("✅ Recording demo complete!")


def demo_all_features(controller):
    """Demonstrate all features in sequence"""
    print_banner("COMPLETE DEMO: All OBS Features")

    print("This demo will showcase all three OBS features:")
    print("  1. Streaming")
    print("  2. Virtual Camera")
    print("  3. Recording")
    print()
    input("Press ENTER to begin...")

    # Run all demos
    demo_streaming(controller)
    print()
    input("Press ENTER to continue to Virtual Camera demo...")
    print()

    demo_virtual_camera(controller)
    print()
    input("Press ENTER to continue to Recording demo...")
    print()

    demo_recording(controller)

    # Show IF.witness report
    print()
    print_banner("IF.witness Provenance Chain")
    print("All operations have been logged to IF.witness hash chain:")
    print()

    chain = controller.get_witness_chain()
    print(f"Total events logged: {len(chain)}")
    print()

    for i, event in enumerate(chain, 1):
        print(f"{i}. {event['event_type']}")
        print(f"   Timestamp: {event['timestamp']}")
        print(f"   Hash: {event['hash'][:32]}...")
        print()

    # Verify chain
    is_valid = controller.verify_witness_chain()
    print(f"Chain integrity: {'✅ VALID' if is_valid else '❌ INVALID'}")
    print()

    # Export report
    report_file = f"obs_witness_report_{int(time.time())}.json"
    controller.export_witness_report(report_file)
    print(f"📄 Full report exported to: {report_file}")
    print()

    print("✅ All demos complete!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='OBS Streaming Integration Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Demo streaming
  python obs_streaming_demo.py --demo streaming

  # Demo virtual camera
  python obs_streaming_demo.py --demo virtualcam

  # Demo recording
  python obs_streaming_demo.py --demo recording

  # Demo all features
  python obs_streaming_demo.py --demo all

  # Use custom OBS connection
  python obs_streaming_demo.py --demo all --host 192.168.1.100 --port 4455 --password secret
        """
    )

    parser.add_argument(
        '--demo',
        choices=['streaming', 'virtualcam', 'recording', 'all'],
        default='all',
        help='Which demo to run (default: all)'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='OBS WebSocket host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=4455,
        help='OBS WebSocket port (default: 4455)'
    )
    parser.add_argument(
        '--password',
        default=None,
        help='OBS WebSocket password (if authentication enabled)'
    )

    args = parser.parse_args()

    # Print header
    print()
    print("=" * 70)
    print("  OBS STREAMING INTEGRATION DEMO")
    print("  InfraFabric - Session 2 (WebRTC)")
    print("=" * 70)
    print()

    # Create controller
    print(f"Connecting to OBS at {args.host}:{args.port}...")
    controller = OBSStreamingController(
        obs_host=args.host,
        obs_port=args.port,
        obs_password=args.password
    )

    try:
        # Connect to OBS
        result = controller.connect()
        print(f"✅ Connected to OBS {result['obs_version']}")
        print(f"   WebSocket version: {result['websocket_version']}")
        print()

        # Run selected demo
        if args.demo == 'streaming':
            demo_streaming(controller)
        elif args.demo == 'virtualcam':
            demo_virtual_camera(controller)
        elif args.demo == 'recording':
            demo_recording(controller)
        elif args.demo == 'all':
            demo_all_features(controller)

    except OBSConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure OBS Studio is running")
        print("  2. Enable WebSocket server: Tools → WebSocket Server Settings")
        print("  3. Check port: Default is 4455")
        print("  4. Check firewall: Allow port 4455")
        print("  5. Test connection: nc -zv localhost 4455")
        print()
        sys.exit(1)

    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Demo interrupted by user")
        print("   Stopping all outputs...")
        controller.stop_all()

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Always disconnect
        print()
        print("Disconnecting from OBS...")
        controller.disconnect()
        print("✅ Disconnected")
        print()
        print("Thank you for trying the OBS Streaming Integration!")
        print()


if __name__ == '__main__':
    main()
