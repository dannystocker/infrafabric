#!/usr/bin/env python3
"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

SIP NDI Integration - Usage Example
====================================

This example demonstrates how to use the SIP NDI integration
for streaming video evidence to external experts during SIP calls.
"""

import asyncio
import logging
import sys

sys.path.insert(0, 'src')

from communication.sip_ndi_ingest import SIPNDIIngest, NDIStreamConfig
from communication.sip_proxy import SIPEscalateProxy, IFMessage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def example_basic_usage():
    """Basic NDI streaming example"""
    logger.info("=== Basic NDI Streaming Example ===")

    # Initialize NDI ingest
    ndi = SIPNDIIngest()

    # Start video stream
    result = await ndi.start_stream(
        trace_id="example-trace-001",
        expert_id="expert-safety@external.advisor",
        call_id="example-call-001"
    )

    logger.info(f"Stream status: {result['status']}")

    if result['status'] == 'streaming':
        logger.info(f"Stream ID: {result['stream_id']}")
        logger.info(f"Source: {result['source']['name']}")
        logger.info(f"Encoding: {result['encoding']['video_codec']} @ {result['encoding']['resolution']}")

        # Simulate call duration
        await asyncio.sleep(2)

        # Get stream statistics
        stats = ndi.get_stream_stats(result['stream_id'])
        logger.info(f"Stream stats: {stats}")

        # Stop stream
        stop_result = await ndi.stop_stream(result['stream_id'])
        logger.info(f"Stream stopped: {stop_result['status']}")
        logger.info(f"Duration: {stop_result['duration_seconds']:.2f}s")


async def example_custom_config():
    """Example with custom encoding configuration"""
    logger.info("\n=== Custom Configuration Example ===")

    # High-quality configuration for critical evidence
    config = NDIStreamConfig(
        video_codec="h264",
        resolution="1080p",
        framerate=60,
        bitrate=8000,
        audio_enabled=True,
        metadata_enabled=True,
        low_latency=True
    )

    ndi = SIPNDIIngest(config=config)

    result = await ndi.start_stream(
        trace_id="example-trace-002",
        expert_id="expert-ethics@external.advisor",
        call_id="example-call-002",
        source_name="IF-Evidence-Camera-1"  # Specific camera
    )

    logger.info(f"High-quality stream: {result['status']}")
    logger.info(f"Configuration: {result['encoding']}")

    await asyncio.sleep(1)
    await ndi.stop_stream(result['stream_id'])


async def example_sip_proxy_integration():
    """Example: NDI integration with SIPEscalateProxy"""
    logger.info("\n=== SIP Proxy Integration Example ===")

    # Initialize SIP proxy with NDI support
    proxy = SIPEscalateProxy()
    proxy.ndi_ingest = SIPNDIIngest()

    # Simulate IFMessage with video enabled
    message = IFMessage(
        id="msg-001",
        timestamp="2025-11-11T23:30:00Z",
        level=2,
        source="if-agent-local",
        destination="external-expert",
        trace_id="trace-003",
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": ["safety"],
            "ndi_video_enabled": True,  # Enable NDI video
            "conversation_id": "council-001",
            "evidence_files": ["evidence1.log"],
            "source_ip": "203.0.113.50",  # IP from allowlisted safety expert network
            "tls_version": "TLSv1.3",
            "cipher_suite": "TLS_AES_256_GCM_SHA384",
            "peer_verified": True
        }
    )

    # Handle escalation (includes NDI video)
    result = await proxy.handle_escalate(message)

    logger.info(f"Escalation result: {result['status']}")

    if result['status'] == 'connected':
        logger.info(f"Call ID: {result['call_id']}")
        logger.info(f"Expert: {result['expert_id']}")

        if result.get('ndi_video'):
            logger.info(f"NDI video active: {result['ndi_video']['status']}")
    else:
        logger.info(f"Call not established: {result.get('reason', 'Unknown reason')}")


async def example_discovery():
    """Example: NDI source discovery"""
    logger.info("\n=== NDI Source Discovery Example ===")

    ndi = SIPNDIIngest()

    # Discover available NDI sources
    sources = await ndi.discovery.discover_sources(timeout=2.0)

    logger.info(f"Discovered {len(sources)} NDI sources:")
    for source in sources:
        logger.info(f"  - {source.name} ({source.ip_address}:{source.port})")
        logger.info(f"    Stream: {source.stream_name}")
        logger.info(f"    Capabilities: {', '.join(source.capabilities)}")


async def example_multiple_streams():
    """Example: Multiple concurrent streams"""
    logger.info("\n=== Multiple Streams Example ===")

    ndi = SIPNDIIngest()

    # Start first stream
    result1 = await ndi.start_stream(
        trace_id="trace-multi-1",
        expert_id="expert-safety@external.advisor",
        call_id="call-multi-1"
    )

    # Get all active streams
    active_streams = ndi.get_all_active_streams()
    logger.info(f"Active streams: {len(active_streams)}")

    for stream in active_streams:
        logger.info(f"  - Call: {stream['call_id']}, Expert: {stream['expert_id']}")

    # Cleanup
    if result1['status'] == 'streaming':
        await ndi.stop_stream(result1['stream_id'])


async def main():
    """Run all examples"""
    logger.info("╔═══════════════════════════════════════════════════════╗")
    logger.info("║   InfraFabric - SIP NDI Integration Examples         ║")
    logger.info("║   Session 4 Phase 4 - Video Evidence Streaming       ║")
    logger.info("╚═══════════════════════════════════════════════════════╝")

    try:
        await example_basic_usage()
        await example_custom_config()
        await example_discovery()
        await example_multiple_streams()
        await example_sip_proxy_integration()

        logger.info("\n✓ All examples completed successfully")

    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
