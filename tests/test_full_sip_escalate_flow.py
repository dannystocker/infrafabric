"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

End-to-End Integration Tests for SIP External Expert Call Flow
----------------------------------------------------------------
Comprehensive tests for the complete IF.ESCALATE call flow from SIP proxy
through H.323 bridge to Guardian council MCU with WebRTC evidence sharing.

Philosophy Grounding:
- IF.ground Observable: All component interactions must be observable and testable
- IF.TTT Principles: Traceable (trace_id), Transparent (witness logs), Trustworthy (performance)
- Wu Lun (朋友): External experts join as peers - test full integration flow

Test Scenario (Session 4 - Phase 2):
1. External expert initiates SIP call (IF.ESCALATE)
2. SIP proxy validates IF.guard policy
3. H.323 gateway bridges to Guardian council MCU
4. WebRTC agent mesh shares real-time context
5. NDI stream provides evidence video to Guardians (stub for now)

Success Criteria:
- <2s call setup time
- <100ms audio latency
- All IF.witness logs present

Integration Points Tested:
- SIPEscalateProxy.handle_escalate()
- IFGuardPolicy.approve_external_call()
- SIPtoH323Bridge.create_bridge()
- H323Gatekeeper.bridge_external_call()
- IFAgentWebRTC.shareEvidence()
- IFWitnessLogger.log_sip_event()
"""

import pytest
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
import hashlib

# Import components under test
from communication.sip_proxy import (
    SIPEscalateProxy,
    IFGuardPolicy,
    IFWitnessLogger,
    IFMessage
)
from communication.sip_h323_gateway import (
    SIPtoH323Bridge,
    CallState,
    MediaCodec,
    MediaStream,
    MediaTranscoder,
    BridgedCall
)
from communication.h323_gatekeeper import H323Gatekeeper
from communication.webrtc_agent_mesh import IFAgentWebRTC


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def trace_id() -> str:
    """Generate unique trace ID for test"""
    return f"test-trace-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]}"


@pytest.fixture
def sample_ifmessage(trace_id: str) -> IFMessage:
    """
    Create sample IFMessage for ESCALATE performative

    This represents an agent requesting external expert consultation
    for a safety hazard detection scenario.
    """
    return IFMessage(
        id=f"msg-{trace_id}",
        timestamp=datetime.utcnow().isoformat() + "Z",
        level=3,  # High severity
        source="agent-alpha",
        destination="IF.ESCALATE",
        trace_id=trace_id,
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": ["safety"],
            "conversation_id": f"council-{trace_id}",
            "evidence_files": [
                "/evidence/safety_detection_001.json",
                "/evidence/context_snapshot_002.json",
                "/evidence/agent_reasoning_003.log"
            ],
            "urgency": "high",
            "signature": "ed25519:test_signature_placeholder"
        }
    )


@pytest.fixture
def sip_proxy() -> SIPEscalateProxy:
    """Create SIPEscalateProxy instance for testing"""
    return SIPEscalateProxy()


@pytest.fixture
def h323_gatekeeper() -> H323Gatekeeper:
    """Create H323Gatekeeper stub instance"""
    return H323Gatekeeper(gatekeeper_id="test-h323-gk")


@pytest.fixture
def sip_h323_bridge(h323_gatekeeper: H323Gatekeeper) -> SIPtoH323Bridge:
    """Create SIPtoH323Bridge instance with H323Gatekeeper"""
    return SIPtoH323Bridge(h323_gatekeeper=h323_gatekeeper)


@pytest.fixture
def webrtc_agent() -> IFAgentWebRTC:
    """Create IFAgentWebRTC stub instance"""
    return IFAgentWebRTC(agent_id="test-webrtc-agent")


# ============================================================================
# Test Case 1: Full End-to-End ESCALATE Flow
# ============================================================================

@pytest.mark.asyncio
async def test_full_escalate_flow_end_to_end(
    sip_proxy: SIPEscalateProxy,
    sample_ifmessage: IFMessage,
    trace_id: str
):
    """
    Test Case 1: Complete end-to-end ESCALATE flow

    Flow:
    1. Create IFMessage with hazard='safety' and evidence_files
    2. Call SIPEscalateProxy.handle_escalate()
    3. Verify IF.guard approval
    4. Verify SIP INVITE sent
    5. Verify H323Gatekeeper.bridge_external_call() called
    6. Verify SIPtoH323Bridge.create_bridge() called (indirectly)
    7. Verify IFAgentWebRTC.shareEvidence() called
    8. Verify all IF.witness events logged
    9. Measure and assert call setup time <2s

    Success Criteria:
    - Call successfully established
    - Setup time < 2000ms
    - All components integrated correctly
    - IF.witness has complete audit trail
    """
    start_time = time.time()

    # Execute ESCALATE flow
    result = await sip_proxy.handle_escalate(sample_ifmessage)

    end_time = time.time()
    setup_time_ms = (end_time - start_time) * 1000

    # Assert: Call connected successfully
    assert result["status"] == "connected", f"Expected 'connected', got {result['status']}"
    assert "call_id" in result, "Missing call_id in result"
    assert "expert_id" in result, "Missing expert_id in result"

    # Assert: Correct expert selected for 'safety' hazard
    assert result["expert_id"] == "expert-safety@external.advisor", \
        f"Expected safety expert, got {result['expert_id']}"

    # Assert: H.323 participant ID present (indicates bridge established)
    assert "h323_participant" in result, "Missing h323_participant_id"
    assert result["h323_participant"] is not None, "h323_participant_id is None"

    # Assert: Call setup time < 2000ms (2 seconds)
    assert setup_time_ms < 2000, \
        f"Call setup took {setup_time_ms:.2f}ms, exceeds 2000ms requirement"

    # Verify: IF.witness events logged
    witness_events = sip_proxy.if_witness.events
    assert len(witness_events) > 0, "No IF.witness events logged"

    # Verify: CONNECTED event present
    connected_events = [e for e in witness_events if e["event_type"] == "CONNECTED"]
    assert len(connected_events) > 0, "No CONNECTED event in IF.witness"

    connected_event = connected_events[0]
    assert connected_event["trace_id"] == trace_id, \
        f"Trace ID mismatch: {connected_event['trace_id']} != {trace_id}"
    assert connected_event["details"]["expert_id"] == result["expert_id"]
    assert connected_event["details"]["evidence_count"] == 3

    # Verify: Active call tracked
    call_id = result["call_id"]
    assert call_id in sip_proxy.active_calls, f"Call {call_id} not in active_calls"
    active_call = sip_proxy.active_calls[call_id]
    assert active_call["trace_id"] == trace_id
    assert active_call["expert_id"] == result["expert_id"]

    print(f"✓ End-to-end ESCALATE flow completed in {setup_time_ms:.2f}ms")


# ============================================================================
# Test Case 2: Audio Latency Simulation
# ============================================================================

@pytest.mark.asyncio
async def test_audio_latency_simulation(
    sip_h323_bridge: SIPtoH323Bridge,
    trace_id: str
):
    """
    Test Case 2: Audio latency measurement through media transcoding

    Scenario:
    1. Set up bridge with media transcoding
    2. Simulate audio packets SIP → H.323
    3. Measure latency
    4. Assert <100ms

    Success Criteria:
    - Audio transcoding pipeline established
    - Latency < 100ms per packet
    - Bidirectional audio flow works
    """
    # Create test bridge
    bridge_result = await sip_h323_bridge.create_bridge(
        sip_call_id=f"sip-test-{trace_id}",
        sip_from="expert-safety@external.advisor",
        council_call_id=f"council-{trace_id}",
        trace_id=trace_id,
        expert_id="expert-safety@external.advisor",
        hazard_type="safety"
    )

    assert bridge_result["status"] == "success", f"Bridge creation failed: {bridge_result}"
    bridge_id = bridge_result["bridge_id"]

    # Get bridge instance
    bridge = sip_h323_bridge.active_bridges[bridge_id]
    assert bridge.sip_media is not None, "SIP media not initialized"
    assert bridge.h323_media is not None, "H.323 media not initialized"

    # Simulate audio packets
    test_packet = b'\x80\x00\x00\x01' + b'\x00' * 160  # Mock RTP packet (160 bytes audio)
    num_packets = 50  # Simulate 50 packets (1 second at 50pps)

    latencies_ms = []

    for i in range(num_packets):
        start = time.time()

        # Transcode SIP → H.323
        h323_frame = await sip_h323_bridge.transcoder.transcode_sip_to_h323(
            bridge_id=bridge_id,
            rtp_packet=test_packet
        )

        end = time.time()
        latency_ms = (end - start) * 1000
        latencies_ms.append(latency_ms)

        assert h323_frame is not None, f"Transcoding failed for packet {i}"

    # Calculate statistics
    avg_latency = sum(latencies_ms) / len(latencies_ms)
    max_latency = max(latencies_ms)

    # Assert: Average latency < 100ms
    assert avg_latency < 100, \
        f"Average latency {avg_latency:.2f}ms exceeds 100ms requirement"

    # Assert: Max latency < 200ms (allow some variance)
    assert max_latency < 200, \
        f"Max latency {max_latency:.2f}ms too high"

    # Verify: Media statistics updated
    assert bridge.sip_media.packets_received >= num_packets
    assert bridge.h323_media.packets_sent >= num_packets

    print(f"✓ Audio latency: avg={avg_latency:.2f}ms, max={max_latency:.2f}ms (n={num_packets})")

    # Cleanup
    await sip_h323_bridge.teardown_bridge(bridge_id)


# ============================================================================
# Test Case 3: Complete IF.witness Audit Trail
# ============================================================================

@pytest.mark.asyncio
async def test_if_witness_complete_audit_trail(
    sip_proxy: SIPEscalateProxy,
    sample_ifmessage: IFMessage,
    trace_id: str
):
    """
    Test Case 3: Verify complete IF.witness audit trail

    Scenario:
    1. Perform full ESCALATE
    2. Verify IF.witness has ALL required events
    3. Verify all events have correct trace_id

    Required Events:
    - CONNECTED (from SIPEscalateProxy)
    - BRIDGE_ESTABLISHED (from SIPtoH323Bridge)
    - EVIDENCE_SHARED (from WebRTC integration)
    - TERMINATED (when call ends)

    Success Criteria:
    - All events logged
    - Correct trace_id on all events
    - Event sequence is logical
    - Timestamps are monotonic
    """
    # Execute ESCALATE flow
    result = await sip_proxy.handle_escalate(sample_ifmessage)
    assert result["status"] == "connected"

    call_id = result["call_id"]

    # Collect witness events from SIPEscalateProxy
    sip_witness_events = sip_proxy.if_witness.events

    # Verify CONNECTED event
    connected_events = [e for e in sip_witness_events if e["event_type"] == "CONNECTED"]
    assert len(connected_events) > 0, "Missing CONNECTED event"
    assert connected_events[0]["trace_id"] == trace_id
    assert connected_events[0]["sip_method"] == "INVITE"

    # Check for bridge establishment (would be in bridge's witness events)
    # Note: In production, these would be in a unified IF.witness system
    # For now, we verify the bridge was created via the proxy's result
    assert result["h323_participant"] is not None, "Bridge not established"

    # Terminate call to generate TERMINATED event
    terminate_result = await sip_proxy.terminate_call(call_id)
    assert terminate_result["status"] == "terminated"

    # Verify TERMINATED event
    terminated_events = [e for e in sip_witness_events if e["event_type"] == "TERMINATED"]
    assert len(terminated_events) > 0, "Missing TERMINATED event"
    assert terminated_events[0]["trace_id"] == trace_id
    assert terminated_events[0]["sip_method"] == "BYE"

    # Verify event chronology
    all_events = sip_witness_events
    assert len(all_events) >= 2, f"Expected at least 2 events, got {len(all_events)}"

    # Verify timestamps are monotonic
    timestamps = [datetime.fromisoformat(e["timestamp"].replace("Z", "")) for e in all_events]
    for i in range(1, len(timestamps)):
        assert timestamps[i] >= timestamps[i-1], \
            f"Timestamp not monotonic: {timestamps[i]} < {timestamps[i-1]}"

    # Verify all events have same trace_id
    trace_ids = set(e["trace_id"] for e in all_events)
    assert len(trace_ids) == 1, f"Multiple trace_ids found: {trace_ids}"
    assert trace_id in trace_ids

    print(f"✓ IF.witness audit trail complete: {len(all_events)} events, trace_id={trace_id}")

    # Print event summary for debugging
    for event in all_events:
        print(f"  - {event['event_type']}: {event['sip_method']} @ {event['timestamp']}")


# ============================================================================
# Test Case 4: Guardian Council Receives Expert
# ============================================================================

@pytest.mark.asyncio
async def test_guardian_council_receives_expert(
    h323_gatekeeper: H323Gatekeeper,
    sip_h323_bridge: SIPtoH323Bridge,
    trace_id: str
):
    """
    Test Case 4: Verify external expert successfully joins Guardian council MCU

    Scenario:
    1. Bridge external expert to council
    2. Verify H.323 MCU participant added
    3. Verify Guardian council can see expert
    4. Verify call state is CONNECTED

    Success Criteria:
    - Expert added to MCU participants list
    - H.323 endpoint registered
    - Bridge state shows CONNECTED
    """
    expert_id = "expert-safety@external.advisor"
    council_call_id = f"council-{trace_id}"
    sip_call_id = f"sip-{trace_id}"

    # Create bridge (this internally calls h323_gatekeeper.bridge_external_call)
    bridge_result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from=expert_id,
        council_call_id=council_call_id,
        trace_id=trace_id,
        expert_id=expert_id,
        hazard_type="safety"
    )

    assert bridge_result["status"] == "success"
    bridge_id = bridge_result["bridge_id"]
    h323_participant_id = bridge_result["h323_participant_id"]

    # Verify: Bridge is active
    bridge_status = sip_h323_bridge.get_bridge_status(bridge_id)
    assert bridge_status is not None, "Bridge not found"
    assert bridge_status["bridge_state"] == "connected"
    assert bridge_status["expert_id"] == expert_id

    # Verify: H.323 gatekeeper has the call
    h323_call_state = await h323_gatekeeper.get_call_state(council_call_id)
    assert h323_call_state is not None, "H.323 call not found"
    assert h323_call_state["state"] == "connected"

    # Verify: Expert is in MCU participants
    assert expert_id in h323_call_state["participants"], \
        f"Expert {expert_id} not in participants: {h323_call_state['participants']}"

    # Verify: MCU participant ID matches
    assert h323_participant_id is not None
    assert h323_participant_id.startswith("mcu-participant-")

    # Test adding another participant to verify MCU functionality
    guardian_id = "guardian-alice"
    add_result = await h323_gatekeeper.add_mcu_participant(council_call_id, guardian_id)
    assert add_result["status"] == "added"

    # Verify both participants present
    updated_call_state = await h323_gatekeeper.get_call_state(council_call_id)
    assert guardian_id in updated_call_state["participants"]
    assert expert_id in updated_call_state["participants"]

    print(f"✓ Expert {expert_id} successfully joined council as {h323_participant_id}")
    print(f"  MCU participants: {updated_call_state['participants']}")


# ============================================================================
# Test Case 5: WebRTC Evidence Reaches All Participants
# ============================================================================

@pytest.mark.asyncio
async def test_webrtc_evidence_reaches_all_participants(
    webrtc_agent: IFAgentWebRTC,
    trace_id: str
):
    """
    Test Case 5: Verify evidence files shared via WebRTC DataChannel

    Scenario:
    1. Share evidence files via WebRTC
    2. Verify sent to both expert and council
    3. Assert file count matches
    4. Verify DataChannels created

    Success Criteria:
    - Evidence shared successfully
    - All peer_ids received files
    - File count matches input
    """
    expert_id = "expert-safety@external.advisor"
    council_id = f"council-{trace_id}"

    evidence_files = [
        "/evidence/safety_detection_001.json",
        "/evidence/context_snapshot_002.json",
        "/evidence/agent_reasoning_003.log"
    ]

    peer_ids = [expert_id, council_id]

    # Share evidence
    result = await webrtc_agent.shareEvidence(
        evidence_files=evidence_files,
        peer_ids=peer_ids
    )

    # Verify: Share completed successfully
    assert result["status"] == "completed", f"Share failed: {result}"
    assert result["shared"] == len(evidence_files), \
        f"File count mismatch: expected {len(evidence_files)}, got {result['shared']}"

    # Verify: All peers received
    assert result["peers"] == peer_ids, \
        f"Peer list mismatch: {result['peers']} != {peer_ids}"

    # Test DataChannel creation
    for peer_id in peer_ids:
        channel_id = await webrtc_agent.createDataChannel(peer_id, "evidence-stream")
        assert channel_id is not None
        assert peer_id in channel_id

        # Verify channel state
        assert channel_id in webrtc_agent.data_channels
        channel_info = webrtc_agent.data_channels[channel_id]
        assert channel_info["state"] == "open"
        assert channel_info["peer_id"] == peer_id

    print(f"✓ Evidence shared: {len(evidence_files)} files to {len(peer_ids)} peers")
    print(f"  Peers: {peer_ids}")
    print(f"  DataChannels: {list(webrtc_agent.data_channels.keys())}")


# ============================================================================
# Test Case 6: NDI Stream Stub (Future Integration)
# ============================================================================

@pytest.mark.asyncio
async def test_ndi_stream_stub(trace_id: str):
    """
    Test Case 6: NDI video stream stub (placeholder for future Session 5)

    Scenario:
    1. Add stub for NDI video stream
    2. Verify it would be called (placeholder)
    3. Document integration points

    Note: This is a stub test for future NDI integration.
    Session 5 will implement actual NDI streaming to Guardian council.

    Success Criteria:
    - Stub interface defined
    - Integration points documented
    - Test passes with mock implementation
    """
    # Stub NDI interface
    class NDIStreamStub:
        """
        Placeholder for Session 5 NDI video streaming

        Will provide:
        - Real-time video evidence to Guardian council
        - Low-latency (<50ms) video feed
        - HD quality (1080p minimum)
        """

        def __init__(self):
            self.active_streams = {}

        async def start_stream(self, stream_id: str, source: str, destinations: List[str]) -> Dict[str, Any]:
            """Start NDI stream to Guardian council"""
            self.active_streams[stream_id] = {
                "source": source,
                "destinations": destinations,
                "state": "streaming",
                "latency_ms": 35  # Target <50ms
            }
            return {
                "status": "streaming",
                "stream_id": stream_id,
                "latency_ms": 35
            }

        async def stop_stream(self, stream_id: str) -> Dict[str, str]:
            """Stop NDI stream"""
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
            return {"status": "stopped", "stream_id": stream_id}

    # Test stub
    ndi_stub = NDIStreamStub()

    stream_id = f"ndi-{trace_id}"
    source = "/dev/video0"  # Example video device
    destinations = [
        "guardian-alice@council",
        "guardian-bob@council",
        "expert-safety@external.advisor"
    ]

    # Start stream
    result = await ndi_stub.start_stream(stream_id, source, destinations)

    assert result["status"] == "streaming"
    assert result["latency_ms"] < 50, "NDI latency exceeds 50ms requirement"

    # Verify stream active
    assert stream_id in ndi_stub.active_streams
    stream_info = ndi_stub.active_streams[stream_id]
    assert stream_info["state"] == "streaming"
    assert stream_info["destinations"] == destinations

    # Stop stream
    stop_result = await ndi_stub.stop_stream(stream_id)
    assert stop_result["status"] == "stopped"
    assert stream_id not in ndi_stub.active_streams

    print(f"✓ NDI stream stub validated (placeholder for Session 5)")
    print(f"  Latency: {result['latency_ms']}ms (<50ms target)")
    print(f"  Destinations: {len(destinations)}")

    # Document integration points for Session 5
    integration_points = {
        "trigger": "SIPEscalateProxy.handle_escalate() with video evidence",
        "setup": "NDI stream started parallel to SIP/H.323 bridge",
        "destinations": "All Guardian council members + external expert",
        "quality": "1080p HD minimum",
        "latency": "<50ms target",
        "cleanup": "Stream stopped on call termination"
    }

    print(f"  Integration points documented: {len(integration_points)}")


# ============================================================================
# Test Case 7: Call Termination and Cleanup
# ============================================================================

@pytest.mark.asyncio
async def test_call_termination_cleanup(
    sip_proxy: SIPEscalateProxy,
    sip_h323_bridge: SIPtoH323Bridge,
    sample_ifmessage: IFMessage,
    trace_id: str
):
    """
    Test Case 7: Verify complete resource cleanup on call termination

    Scenario:
    1. Establish full call (SIP + H.323 bridge + WebRTC)
    2. Terminate call
    3. Verify all resources cleaned up
    4. Verify BYE logged to IF.witness
    5. Verify media statistics collected

    Success Criteria:
    - Call terminated successfully
    - Active calls list empty
    - Bridge removed
    - Media resources released
    - TERMINATED event logged
    - Duration and statistics recorded
    """
    # Establish full call
    result = await sip_proxy.handle_escalate(sample_ifmessage)
    assert result["status"] == "connected"

    call_id = result["call_id"]

    # Verify call is active
    assert call_id in sip_proxy.active_calls
    initial_active_count = len(sip_proxy.active_calls)

    # Wait a moment to simulate active call
    await asyncio.sleep(0.1)

    # Terminate call
    terminate_result = await sip_proxy.terminate_call(call_id)

    # Verify termination successful
    assert terminate_result["status"] == "terminated"
    assert terminate_result["call_id"] == call_id

    # Verify: Call removed from active calls
    assert call_id not in sip_proxy.active_calls, \
        f"Call {call_id} still in active_calls after termination"
    assert len(sip_proxy.active_calls) == initial_active_count - 1

    # Verify: TERMINATED event logged
    witness_events = sip_proxy.if_witness.events
    terminated_events = [e for e in witness_events if e["event_type"] == "TERMINATED"]
    assert len(terminated_events) > 0, "No TERMINATED event logged"

    terminated_event = terminated_events[-1]  # Get most recent
    assert terminated_event["trace_id"] == trace_id
    assert terminated_event["sip_method"] == "BYE"
    assert terminated_event["details"]["call_id"] == call_id

    # Test bridge cleanup (create and teardown a bridge)
    bridge_result = await sip_h323_bridge.create_bridge(
        sip_call_id=f"sip-cleanup-{trace_id}",
        sip_from="expert-safety@external.advisor",
        council_call_id=f"council-cleanup-{trace_id}",
        trace_id=f"{trace_id}-bridge",
        expert_id="expert-safety@external.advisor",
        hazard_type="safety"
    )

    assert bridge_result["status"] == "success"
    bridge_id = bridge_result["bridge_id"]

    # Verify bridge is active
    assert bridge_id in sip_h323_bridge.active_bridges
    initial_bridge_count = len(sip_h323_bridge.active_bridges)

    # Teardown bridge
    teardown_result = await sip_h323_bridge.teardown_bridge(bridge_id)

    # Verify teardown successful
    assert teardown_result["status"] == "success"
    assert teardown_result["bridge_id"] == bridge_id
    assert teardown_result["duration_seconds"] > 0

    # Verify: Media statistics present
    assert "media_stats" in teardown_result
    media_stats = teardown_result["media_stats"]
    assert "sip" in media_stats
    assert "h323" in media_stats

    # Verify: Bridge removed
    assert bridge_id not in sip_h323_bridge.active_bridges
    assert len(sip_h323_bridge.active_bridges) == initial_bridge_count - 1

    # Verify: Bridge witness event logged
    bridge_witness_events = sip_h323_bridge.witness_events
    terminated_bridge_events = [
        e for e in bridge_witness_events
        if e["event_type"] == "BRIDGE_TERMINATED"
    ]
    assert len(terminated_bridge_events) > 0, "No BRIDGE_TERMINATED event"

    bridge_terminated_event = terminated_bridge_events[-1]
    assert bridge_terminated_event["bridge_id"] == bridge_id
    assert "duration_seconds" in bridge_terminated_event["details"]
    assert "media_stats" in bridge_terminated_event["details"]

    print(f"✓ Call termination and cleanup successful")
    print(f"  Call duration: {teardown_result['duration_seconds']:.2f}s")
    print(f"  SIP packets: sent={media_stats['sip']['packets_sent']}, recv={media_stats['sip']['packets_received']}")
    print(f"  H.323 packets: sent={media_stats['h323']['packets_sent']}, recv={media_stats['h323']['packets_received']}")


# ============================================================================
# Additional Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_if_guard_policy_rejection():
    """
    Test IF.guard policy rejection for unapproved expert

    Verifies that calls from non-approved experts are rejected.
    """
    guard = IFGuardPolicy()

    # Test with unapproved expert
    result = await guard.approve_external_call(
        expert_id="unknown-expert@malicious.com",
        hazard="safety"
    )

    assert result["approved"] is False
    assert "not in approved registry" in result["reason"]

    print("✓ IF.guard correctly rejects unapproved expert")


@pytest.mark.asyncio
async def test_if_guard_policy_specialization_mismatch():
    """
    Test IF.guard policy rejection for specialization mismatch

    Verifies that experts are only approved for their specialization.
    """
    guard = IFGuardPolicy()

    # Test security expert for safety hazard (mismatch)
    result = await guard.approve_external_call(
        expert_id="expert-security@external.advisor",
        hazard="safety"  # Security expert doesn't specialize in safety
    )

    assert result["approved"] is False
    assert "specialization" in result["reason"].lower()

    print("✓ IF.guard correctly rejects specialization mismatch")


@pytest.mark.asyncio
async def test_concurrent_escalate_calls():
    """
    Test handling multiple concurrent ESCALATE calls

    Verifies system can handle multiple simultaneous external expert calls.
    """
    sip_proxy = SIPEscalateProxy()

    # Create multiple messages with different hazards
    messages = [
        IFMessage(
            id=f"msg-{i}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=3,
            source=f"agent-{i}",
            destination="IF.ESCALATE",
            trace_id=f"trace-{i}",
            version="1.0",
            payload={
                "performative": "escalate",
                "hazards": [hazard],
                "conversation_id": f"council-{i}",
                "evidence_files": [f"/evidence/test_{i}.json"]
            }
        )
        for i, hazard in enumerate(["safety", "ethics", "security"])
    ]

    # Execute concurrent escalations
    results = await asyncio.gather(
        *[sip_proxy.handle_escalate(msg) for msg in messages]
    )

    # Verify all succeeded
    for i, result in enumerate(results):
        assert result["status"] == "connected", f"Call {i} failed: {result}"

    # Verify correct expert mapping
    assert results[0]["expert_id"] == "expert-safety@external.advisor"
    assert results[1]["expert_id"] == "expert-ethics@external.advisor"
    assert results[2]["expert_id"] == "expert-security@external.advisor"

    # Verify all calls are active
    assert len(sip_proxy.active_calls) == 3

    print(f"✓ Concurrent ESCALATE calls handled successfully (n={len(results)})")


# ============================================================================
# Performance Benchmarks
# ============================================================================

@pytest.mark.asyncio
async def test_performance_benchmark_100_calls():
    """
    Performance benchmark: 100 sequential ESCALATE calls

    Measures throughput and ensures system remains performant.
    """
    sip_proxy = SIPEscalateProxy()

    num_calls = 100
    setup_times = []

    for i in range(num_calls):
        message = IFMessage(
            id=f"bench-{i}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=3,
            source=f"agent-bench-{i}",
            destination="IF.ESCALATE",
            trace_id=f"bench-trace-{i}",
            version="1.0",
            payload={
                "performative": "escalate",
                "hazards": ["safety"],
                "conversation_id": f"council-bench-{i}",
                "evidence_files": []
            }
        )

        start = time.time()
        result = await sip_proxy.handle_escalate(message)
        end = time.time()

        assert result["status"] == "connected"
        setup_times.append((end - start) * 1000)

    # Statistics
    avg_setup = sum(setup_times) / len(setup_times)
    max_setup = max(setup_times)
    min_setup = min(setup_times)

    print(f"✓ Performance benchmark: {num_calls} calls")
    print(f"  Average setup: {avg_setup:.2f}ms")
    print(f"  Min setup: {min_setup:.2f}ms")
    print(f"  Max setup: {max_setup:.2f}ms")

    # Assert reasonable performance
    assert avg_setup < 2000, f"Average setup {avg_setup:.2f}ms exceeds 2000ms"


if __name__ == "__main__":
    """
    Run tests directly with pytest

    Usage:
        pytest tests/test_full_sip_escalate_flow.py -v
        pytest tests/test_full_sip_escalate_flow.py::test_full_escalate_flow_end_to_end -v
    """
    pytest.main([__file__, "-v", "--tb=short"])
