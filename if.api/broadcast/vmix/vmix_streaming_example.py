#!/usr/bin/env python3
"""
vMix Streaming Example - Quick Start Guide
==========================================

Demonstrates basic usage of the vMix Streaming Controller.

Prerequisites:
1. vMix installed and running
2. Web Controller enabled (Settings → Web Controller → Enable)
3. vMix listening on port 8088

Author: IF.Session2 (WebRTC) - vMix Streaming Integration
Date: 2025-11-12
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.vmix_streaming import VMixStreamingController, StreamingDestinations


def example_1_basic_streaming():
    """Example 1: Start basic RTMP stream"""
    print("\n" + "="*60)
    print("Example 1: Basic RTMP Streaming to Twitch")
    print("="*60)

    controller = VMixStreamingController(vmix_host='localhost', vmix_port=8088)

    # Configure Twitch stream
    # REPLACE 'your_stream_key_here' with actual Twitch stream key
    twitch_config = StreamingDestinations.twitch('your_stream_key_here')

    print("\nStarting Twitch stream...")
    result = controller.start_rtmp_stream(**twitch_config, channel=0)

    if result['success']:
        print(f"✅ Stream started successfully!")
        print(f"   Channel: {result['channel']}")
        print(f"   Destination: {result['destination']}")

        # Monitor for 30 seconds
        print("\nMonitoring stream for 30 seconds...")
        for i in range(6):
            time.sleep(5)
            status = controller.get_stream_status()
            health = controller.get_stream_health()

            print(f"   [{i*5+5}s] Streaming: {status['streaming']}, "
                  f"FPS: {health.get('fps', 0):.1f}, "
                  f"Health: {health.get('health_status', 'unknown')}")

        # Stop stream
        print("\nStopping stream...")
        controller.stop_stream(channel=0)
        print("✅ Stream stopped")

    else:
        print(f"❌ Failed to start stream: {result['message']}")


def example_2_srt_streaming():
    """Example 2: SRT low-latency streaming"""
    print("\n" + "="*60)
    print("Example 2: SRT Low-Latency Streaming")
    print("="*60)

    controller = VMixStreamingController()

    # Start SRT stream in caller mode
    # REPLACE with actual SRT server address
    print("\nStarting SRT stream...")
    result = controller.start_srt_stream(
        srt_address='srt://192.168.1.100:9000',
        mode='caller',
        latency_ms=120,
        channel=0
    )

    if result['success']:
        print(f"✅ SRT stream started!")
        print(f"   Protocol: {result['protocol']}")
        print(f"   Mode: {result['mode']}")
        print(f"   Latency: {result['latency_ms']}ms")
        print(f"   Channel: {result['channel']}")

        # Monitor briefly
        time.sleep(10)

        # Stop
        controller.stop_stream(channel=0)
        print("✅ SRT stream stopped")
    else:
        print(f"❌ Failed to start SRT stream: {result['message']}")


def example_3_recording():
    """Example 3: Recording with custom filename"""
    print("\n" + "="*60)
    print("Example 3: Recording Control")
    print("="*60)

    controller = VMixStreamingController()

    # Start recording
    from datetime import datetime
    filename = f"example_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    print(f"\nStarting recording: {filename}")
    result = controller.start_recording(
        filename=filename,
        format='MP4',
        quality='high'
    )

    if result['success']:
        print(f"✅ Recording started!")
        print(f"   Filename: {result['filename']}")
        print(f"   Format: {result['format']}")
        print(f"   Quality: {result['quality']}")

        # Record for 30 seconds
        print("\nRecording for 30 seconds...")
        for i in range(6):
            time.sleep(5)
            status = controller.get_stream_status()
            print(f"   [{i*5+5}s] Recording time: {status.get('record_time', '00:00:00')}")

        # Stop recording
        print("\nStopping recording...")
        stop_result = controller.stop_recording()
        print(f"✅ Recording stopped. Duration: {stop_result['duration']}")

    else:
        print(f"❌ Failed to start recording: {result['message']}")


def example_4_multi_platform():
    """Example 4: Stream to multiple platforms simultaneously"""
    print("\n" + "="*60)
    print("Example 4: Multi-Platform Streaming")
    print("="*60)

    controller = VMixStreamingController()

    # Configure multiple platforms
    # REPLACE with actual stream keys
    platforms = [
        ('Twitch', StreamingDestinations.twitch('twitch_key_here'), 0),
        ('YouTube', StreamingDestinations.youtube('youtube_key_here'), 1),
        ('Facebook', StreamingDestinations.facebook('facebook_key_here'), 2)
    ]

    print("\nStarting streams on all platforms...")
    active_streams = []

    for name, config, channel in platforms:
        print(f"\n  Starting {name} on channel {channel}...")
        result = controller.start_rtmp_stream(**config, channel=channel)

        if result['success']:
            print(f"  ✅ {name} streaming")
            active_streams.append((name, channel))
        else:
            print(f"  ❌ {name} failed: {result['message']}")

    if active_streams:
        # Monitor all streams
        print(f"\nMonitoring {len(active_streams)} streams for 30 seconds...")
        for i in range(6):
            time.sleep(5)
            status = controller.get_stream_status()
            health = controller.get_stream_health()

            print(f"\n  [{i*5+5}s] Status:")
            print(f"    Active channels: {status.get('stream_channels', [])}")
            print(f"    Health: {health.get('health_status', 'unknown')}")
            print(f"    FPS: {health.get('fps', 0):.1f}")
            print(f"    Bitrate: {health.get('bitrate_kbps', 0):.0f} kbps")

        # Stop all streams
        print("\nStopping all streams...")
        for name, channel in active_streams:
            controller.stop_stream(channel=channel)
            print(f"  ✅ {name} stopped")


def example_5_witness_log():
    """Example 5: IF.witness provenance tracking"""
    print("\n" + "="*60)
    print("Example 5: IF.witness Provenance Tracking")
    print("="*60)

    controller = VMixStreamingController()

    # Perform some operations
    print("\nPerforming streaming operations...")

    # Start stream
    twitch_config = StreamingDestinations.twitch('test_key')
    controller.start_rtmp_stream(**twitch_config, channel=0)
    time.sleep(5)

    # Start recording
    controller.start_recording(filename='witness_test.mp4', format='MP4', quality='high')
    time.sleep(5)

    # Stop both
    controller.stop_stream(channel=0)
    controller.stop_recording()

    # Allow async tasks to complete
    time.sleep(1)

    # Retrieve witness log
    print("\n--- IF.witness Provenance Log ---")
    log = controller.get_witness_log()

    for i, entry in enumerate(log):
        event = entry['event']
        print(f"\n{i+1}. Event Type: {event['event_type']}")
        print(f"   Timestamp: {event['timestamp']}")
        print(f"   Params: {event['params']}")
        print(f"   Hash: {entry['current_hash'][:16]}...")

    # Verify chain integrity
    verification = controller.verify_witness_chain()

    print(f"\n--- Chain Verification ---")
    print(f"Valid: {verification['valid']}")
    print(f"Total Events: {verification['total_events']}")
    print(f"First Hash: {verification['first_hash'][:16]}...")
    print(f"Last Hash: {verification['last_hash'][:16]}...")

    if verification['valid']:
        print("\n✅ Witness chain integrity verified!")
    else:
        print(f"\n❌ Chain broken at index: {verification['broken_at']}")


def example_6_health_monitoring():
    """Example 6: Stream health monitoring"""
    print("\n" + "="*60)
    print("Example 6: Stream Health Monitoring")
    print("="*60)

    controller = VMixStreamingController()

    # Start a stream
    twitch_config = StreamingDestinations.twitch('test_key')
    result = controller.start_rtmp_stream(**twitch_config, channel=0)

    if result['success']:
        print("\n✅ Stream started. Monitoring health...\n")

        # Monitor for 1 minute
        for i in range(12):
            time.sleep(5)

            health = controller.get_stream_health()
            status = controller.get_stream_status()

            # Create health report
            print(f"[{i*5+5}s] Health Report:")
            print(f"  Status: {health.get('health_status', 'unknown').upper()}")
            print(f"  FPS: {health.get('fps', 0):.1f}")
            print(f"  Bitrate: {health.get('bitrate_kbps', 0):.0f} kbps")
            print(f"  Dropped Frames: {health.get('dropped_frames', 0)}")
            print(f"  Uptime: {status.get('stream_time', '00:00:00')}")

            # Alert on issues
            if health.get('health_status') == 'critical':
                print("  ⚠️ CRITICAL: Stream quality degraded!")
            elif health.get('health_status') == 'warning':
                print("  ⚠️ WARNING: Stream quality declining")

            print()

        # Stop stream
        controller.stop_stream(channel=0)
        print("✅ Stream stopped")
    else:
        print(f"❌ Failed to start stream: {result['message']}")


def main():
    """Main example runner"""
    print("\n" + "="*60)
    print("vMix Streaming Controller - Example Usage")
    print("="*60)

    examples = [
        ("Basic RTMP Streaming", example_1_basic_streaming),
        ("SRT Low-Latency Streaming", example_2_srt_streaming),
        ("Recording Control", example_3_recording),
        ("Multi-Platform Streaming", example_4_multi_platform),
        ("IF.witness Provenance Tracking", example_5_witness_log),
        ("Stream Health Monitoring", example_6_health_monitoring)
    ]

    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nNote: Some examples require valid stream keys.")
    print("      Edit this file to add your stream keys before running.")

    # Uncomment the example you want to run:

    # example_1_basic_streaming()
    # example_2_srt_streaming()
    # example_3_recording()
    # example_4_multi_platform()
    # example_5_witness_log()
    # example_6_health_monitoring()

    print("\n" + "="*60)
    print("Uncomment an example function in main() to run it.")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
