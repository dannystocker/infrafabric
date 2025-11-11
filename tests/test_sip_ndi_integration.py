"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

Session 4 (SIP) - Phase 4 - NDI Integration Test Suite
=======================================================

Test suite for SIP NDI video streaming integration:
1. NDI source discovery
2. Stream initialization and connection
3. H.264 encoding pipeline
4. Metadata embedding
5. Stream lifecycle management
6. Integration with SIPEscalateProxy

Philosophy Grounding:
- IF.ground Observable: Test video evidence streaming
- IF.TTT: Verify metadata traceability
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Import modules under test
import sys
sys.path.insert(0, '/home/user/infrafabric/src')

from communication.sip_ndi_ingest import (
    SIPNDIIngest,
    NDIDiscovery,
    NDISource,
    NDIStreamConfig,
    NDIStreamState
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest_asyncio.fixture
def ndi_config():
    """Standard NDI configuration for testing"""
    return NDIStreamConfig(
        video_codec="h264",
        resolution="1080p",
        framerate=30,
        bitrate=5000,
        audio_enabled=True,
        metadata_enabled=True,
        low_latency=True
    )


@pytest_asyncio.fixture
def ndi_ingest(ndi_config):
    """NDI ingest instance with test configuration"""
    return SIPNDIIngest(config=ndi_config)


@pytest_asyncio.fixture
def sample_ndi_source():
    """Sample NDI source for testing"""
    return NDISource(
        name="IF-Evidence-Camera-Test",
        ip_address="10.0.1.100",
        port=5960,
        stream_name="test-evidence-stream",
        capabilities=["video", "audio", "metadata"],
        discovered_at=datetime.utcnow().isoformat() + "Z"
    )


# ============================================================================
# TEST: NDI Discovery
# ============================================================================

@pytest.mark.asyncio
async def test_ndi_discovery_finds_sources():
    """Test NDI source discovery via multicast"""
    discovery = NDIDiscovery()
    sources = await discovery.discover_sources(timeout=1.0)

    # Should find at least one source (simulated)
    assert len(sources) > 0
    assert all(isinstance(s, NDISource) for s in sources)
    assert all(s.ip_address for s in sources)
    assert all(s.port > 0 for s in sources)


@pytest.mark.asyncio
async def test_ndi_discovery_timeout():
    """Test discovery timeout handling"""
    discovery = NDIDiscovery()

    # Should handle timeout gracefully
    sources = await discovery.discover_sources(timeout=0.1)
    assert isinstance(sources, list)


# ============================================================================
# TEST: Stream Lifecycle
# ============================================================================

@pytest.mark.asyncio
async def test_start_stream_success(ndi_ingest):
    """Test successful NDI stream initialization"""
    result = await ndi_ingest.start_stream(
        trace_id="test-trace-123",
        expert_id="expert-test@example.com",
        call_id="test-call-456"
    )

    assert result["status"] == "streaming"
    assert "stream_id" in result
    assert "source" in result
    assert "encoding" in result
    assert result["encoding"]["video_codec"] == "h264"
    assert ndi_ingest.state == NDIStreamState.STREAMING


@pytest.mark.asyncio
async def test_start_stream_with_specific_source(ndi_ingest):
    """Test stream start with specific NDI source selection"""
    result = await ndi_ingest.start_stream(
        trace_id="test-trace-123",
        expert_id="expert-test@example.com",
        call_id="test-call-456",
        source_name="IF-Evidence-Camera-1"
    )

    assert result["status"] == "streaming"
    assert result["source"]["name"] == "IF-Evidence-Camera-1"


@pytest.mark.asyncio
async def test_stop_stream_success(ndi_ingest):
    """Test successful stream termination"""
    # Start stream first
    start_result = await ndi_ingest.start_stream(
        trace_id="test-trace-123",
        expert_id="expert-test@example.com",
        call_id="test-call-456"
    )

    stream_id = start_result["stream_id"]

    # Stop stream
    stop_result = await ndi_ingest.stop_stream(stream_id)

    assert stop_result["status"] == "terminated"
    assert stop_result["stream_id"] == stream_id
    assert "duration_seconds" in stop_result
    assert "stats" in stop_result
    assert ndi_ingest.state == NDIStreamState.TERMINATED


@pytest.mark.asyncio
async def test_stop_nonexistent_stream(ndi_ingest):
    """Test stopping a stream that doesn't exist"""
    result = await ndi_ingest.stop_stream("nonexistent-stream-id")

    assert result["status"] == "not_found"


# ============================================================================
# TEST: Stream Statistics
# ============================================================================

@pytest.mark.asyncio
async def test_get_stream_stats(ndi_ingest):
    """Test retrieving stream statistics"""
    # Start stream
    start_result = await ndi_ingest.start_stream(
        trace_id="test-trace-123",
        expert_id="expert-test@example.com",
        call_id="test-call-456"
    )

    stream_id = start_result["stream_id"]

    # Get stats
    stats = ndi_ingest.get_stream_stats(stream_id)

    assert stats is not None
    assert stats["call_id"] == "test-call-456"
    assert stats["trace_id"] == "test-trace-123"
    assert stats["expert_id"] == "expert-test@example.com"
    assert "started_at" in stats
    assert "encoding" in stats


@pytest.mark.asyncio
async def test_get_all_active_streams(ndi_ingest):
    """Test retrieving all active streams"""
    # Start multiple streams
    result1 = await ndi_ingest.start_stream(
        trace_id="trace-1",
        expert_id="expert-1@example.com",
        call_id="call-1"
    )

    # Get all active streams
    active_streams = ndi_ingest.get_all_active_streams()

    assert len(active_streams) == 1
    assert active_streams[0]["call_id"] == "call-1"


# ============================================================================
# TEST: Configuration
# ============================================================================

def test_ndi_config_defaults():
    """Test default NDI configuration values"""
    config = NDIStreamConfig()

    assert config.video_codec == "h264"
    assert config.resolution == "1080p"
    assert config.framerate == 30
    assert config.bitrate == 5000
    assert config.audio_enabled is True
    assert config.metadata_enabled is True
    assert config.low_latency is True


def test_ndi_config_custom():
    """Test custom NDI configuration"""
    config = NDIStreamConfig(
        video_codec="h265",
        resolution="720p",
        framerate=60,
        bitrate=3000,
        audio_enabled=False,
        low_latency=False
    )

    assert config.video_codec == "h265"
    assert config.resolution == "720p"
    assert config.framerate == 60
    assert config.bitrate == 3000
    assert config.audio_enabled is False


def test_ndi_config_to_dict(ndi_config):
    """Test NDI config serialization"""
    config_dict = ndi_config.to_dict()

    assert isinstance(config_dict, dict)
    assert config_dict["video_codec"] == "h264"
    assert config_dict["resolution"] == "1080p"
    assert config_dict["framerate"] == 30


# ============================================================================
# TEST: NDI Source
# ============================================================================

def test_ndi_source_creation(sample_ndi_source):
    """Test NDI source data structure"""
    assert sample_ndi_source.name == "IF-Evidence-Camera-Test"
    assert sample_ndi_source.ip_address == "10.0.1.100"
    assert sample_ndi_source.port == 5960
    assert "video" in sample_ndi_source.capabilities


def test_ndi_source_to_dict(sample_ndi_source):
    """Test NDI source serialization"""
    source_dict = sample_ndi_source.to_dict()

    assert isinstance(source_dict, dict)
    assert source_dict["name"] == "IF-Evidence-Camera-Test"
    assert source_dict["ip_address"] == "10.0.1.100"
    assert isinstance(source_dict["capabilities"], list)


# ============================================================================
# TEST: Integration with SIPEscalateProxy
# ============================================================================

@pytest.mark.asyncio
async def test_sip_proxy_ndi_integration():
    """Test NDI integration with SIPEscalateProxy"""
    # This test verifies that NDI can be integrated with SIP proxy
    # In production, this would test actual SIPEscalateProxy.handle_escalate()

    ndi_ingest = SIPNDIIngest()

    # Simulate SIP call establishment
    trace_id = "integration-test-trace"
    expert_id = "expert-safety@external.advisor"
    call_id = "sip-call-integration-test"

    # Start NDI stream for SIP call
    ndi_result = await ndi_ingest.start_stream(
        trace_id=trace_id,
        expert_id=expert_id,
        call_id=call_id
    )

    # Verify stream started successfully
    assert ndi_result["status"] == "streaming"
    assert ndi_result["encoding"]["video_codec"] == "h264"

    # Verify metadata embedding
    stream_stats = ndi_ingest.get_stream_stats(ndi_result["stream_id"])
    assert stream_stats["trace_id"] == trace_id
    assert stream_stats["expert_id"] == expert_id

    # Cleanup
    await ndi_ingest.stop_stream(ndi_result["stream_id"])


# ============================================================================
# TEST: Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_stream_graceful_degradation():
    """Test graceful degradation when NDI unavailable"""
    # This would test behavior when no NDI sources are found
    # Should not block SIP call establishment

    ndi_ingest = SIPNDIIngest()

    # Mock discovery to return no sources
    with patch.object(ndi_ingest.discovery, 'discover_sources', return_value=[]):
        result = await ndi_ingest.start_stream(
            trace_id="test-trace",
            expert_id="expert@example.com",
            call_id="test-call"
        )

        # Should return unavailable status, not error
        assert result["status"] == "unavailable"
        assert "reason" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
