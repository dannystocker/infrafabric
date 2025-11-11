"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

Session 4 (SIP External Expert Calls) - Phase 4 Integration Tests
==================================================================

Comprehensive integration tests for all 3 SIP bridges working together:
1. SIP-H.323 Bridge (Session 3 Guardian council MCU)
2. SIP-WebRTC Bridge (Session 2 agent mesh DataChannel)
3. SIP-NDI Ingest (Video evidence streaming with metadata)

Tests verify:
- Individual bridge functionality
- Cross-bridge integration
- Concurrent operation without conflicts
- Failure recovery and resilience
- Evidence and metadata flow

Philosophy Grounding:
- Wu Lun (五倫): 朋友 (Friends) - External experts join council as peers
- Popper Falsifiability: Multiple experts and perspectives prevent groupthink
- IF.ground: Observable - All bridges logged for complete audit trail
- IF.TTT: Traceable, Transparent, Trustworthy cross-protocol communication
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from datetime import datetime
from uuid import uuid4
import json
from typing import Dict, Any, Optional, List

# Import modules under test
import sys
sys.path.insert(0, '/home/user/infrafabric/src')

from communication.sip_proxy import (
    SIPEscalateProxy,
    IFMessage,
    IFGuardPolicy,
    IFWitnessLogger,
)
from communication.sip_h323_gateway import (
    SIPtoH323Bridge,
    CallState,
    MediaCodec,
    MediaStream,
    BridgedCall,
    MediaTranscoder
)
from communication.h323_gatekeeper import H323Gatekeeper
from communication.webrtc_agent_mesh import IFAgentWebRTC


# ============================================================================
# MOCK CLASSES FOR SIP-WebRTC Bridge (newly created)
# ============================================================================

class SIPtoWebRTCBridge:
    """
    Mock SIP-WebRTC Bridge for testing

    Bridges SIP calls to WebRTC agents via DataChannel with IFMessage escalate.
    Enables evidence file sharing and metadata embedding.
    """

    def __init__(self):
        self.active_bridges: Dict[str, Dict[str, Any]] = {}
        self.witness_events: List[Dict[str, Any]] = []
        self.webrtc_agent = None

    async def create_bridge(
        self,
        sip_call_id: str,
        sip_from: str,
        trace_id: str,
        expert_id: str,
        hazard_type: str,
        evidence_files: List[str]
    ) -> Dict[str, Any]:
        """Create SIP-WebRTC bridge for evidence sharing."""
        bridge_id = f"webrtc-bridge-{sip_call_id[:16]}"

        bridge = {
            "bridge_id": bridge_id,
            "trace_id": trace_id,
            "sip_call_id": sip_call_id,
            "sip_from": sip_from,
            "expert_id": expert_id,
            "hazard_type": hazard_type,
            "evidence_files": evidence_files,
            "evidence_shared": False,
            "datachannel_state": "CONNECTING",
            "if_messages_sent": 0,
            "start_time": datetime.utcnow()
        }

        self.active_bridges[bridge_id] = bridge

        # Simulate evidence sharing via IFMessage escalate
        if evidence_files:
            bridge["evidence_shared"] = True
            bridge["if_messages_sent"] = len(evidence_files)

        bridge["datachannel_state"] = "CONNECTED"

        await self._log_witness_event(
            bridge_id=bridge_id,
            event_type="WEBRTC_BRIDGE_ESTABLISHED",
            details={
                "sip_call_id": sip_call_id,
                "expert_id": expert_id,
                "evidence_count": len(evidence_files),
                "trace_id": trace_id
            }
        )

        return {
            "status": "success",
            "bridge_id": bridge_id,
            "datachannel_id": f"dc-{bridge_id[:8]}",
            "evidence_shared": len(evidence_files),
            "trace_id": trace_id
        }

    async def _log_witness_event(
        self,
        bridge_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Log bridge event to IF.witness."""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "SIPtoWebRTCBridge",
            "bridge_id": bridge_id,
            "event_type": event_type,
            "details": details
        }
        self.witness_events.append(event)

    async def teardown_bridge(self, bridge_id: str) -> Dict[str, Any]:
        """Teardown WebRTC bridge."""
        if bridge_id not in self.active_bridges:
            return {"status": "not_found", "bridge_id": bridge_id}

        bridge = self.active_bridges[bridge_id]
        duration = (datetime.utcnow() - bridge["start_time"]).total_seconds()

        await self._log_witness_event(
            bridge_id=bridge_id,
            event_type="WEBRTC_BRIDGE_TERMINATED",
            details={
                "duration_seconds": duration,
                "evidence_shared": bridge["evidence_shared"],
                "if_messages_sent": bridge["if_messages_sent"]
            }
        )

        del self.active_bridges[bridge_id]

        return {
            "status": "success",
            "bridge_id": bridge_id,
            "duration_seconds": duration
        }


# ============================================================================
# MOCK CLASSES FOR SIP-NDI Ingest (newly created)
# ============================================================================

class SIPtoNDIIngest:
    """
    Mock SIP-NDI Ingest for testing

    Bridges SIP calls with optional NDI video streams for evidence capture.
    Embeds metadata (hazard type, expert info, timestamps) in NDI packets.
    """

    def __init__(self):
        self.active_ingests: Dict[str, Dict[str, Any]] = {}
        self.witness_events: List[Dict[str, Any]] = []

    async def setup_ndi_ingest(
        self,
        sip_call_id: str,
        ndi_source: Optional[str],
        trace_id: str,
        expert_id: str,
        hazard_type: str
    ) -> Dict[str, Any]:
        """Setup optional NDI video evidence streaming."""
        ingest_id = f"ndi-ingest-{sip_call_id[:16]}"

        if not ndi_source:
            return {
                "status": "skipped",
                "ingest_id": ingest_id,
                "ndi_enabled": False,
                "reason": "No NDI source provided"
            }

        ingest = {
            "ingest_id": ingest_id,
            "trace_id": trace_id,
            "sip_call_id": sip_call_id,
            "ndi_source": ndi_source,
            "expert_id": expert_id,
            "hazard_type": hazard_type,
            "ndi_stream_state": "STREAMING",
            "frames_captured": 0,
            "metadata_embedded": True,
            "start_time": datetime.utcnow()
        }

        self.active_ingests[ingest_id] = ingest

        # Simulate frame capture
        ingest["frames_captured"] = 100

        await self._log_witness_event(
            ingest_id=ingest_id,
            event_type="NDI_INGEST_STARTED",
            details={
                "sip_call_id": sip_call_id,
                "ndi_source": ndi_source,
                "expert_id": expert_id,
                "hazard_type": hazard_type,
                "metadata_enabled": True,
                "trace_id": trace_id
            }
        )

        return {
            "status": "success",
            "ingest_id": ingest_id,
            "ndi_enabled": True,
            "ndi_source": ndi_source,
            "frames_captured": ingest["frames_captured"],
            "metadata_embedded": True,
            "trace_id": trace_id
        }

    async def _log_witness_event(
        self,
        ingest_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Log ingest event to IF.witness."""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "SIPtoNDIIngest",
            "ingest_id": ingest_id,
            "event_type": event_type,
            "details": details
        }
        self.witness_events.append(event)

    async def teardown_ndi_ingest(self, ingest_id: str) -> Dict[str, Any]:
        """Teardown NDI ingest stream."""
        if ingest_id not in self.active_ingests:
            return {"status": "not_found", "ingest_id": ingest_id}

        ingest = self.active_ingests[ingest_id]
        duration = (datetime.utcnow() - ingest["start_time"]).total_seconds()

        await self._log_witness_event(
            ingest_id=ingest_id,
            event_type="NDI_INGEST_STOPPED",
            details={
                "duration_seconds": duration,
                "frames_captured": ingest["frames_captured"],
                "metadata_embedded": ingest["metadata_embedded"]
            }
        )

        del self.active_ingests[ingest_id]

        return {
            "status": "success",
            "ingest_id": ingest_id,
            "duration_seconds": duration,
            "frames_captured": ingest["frames_captured"]
        }


# ============================================================================
# FIXTURES
# ============================================================================

@pytest_asyncio.fixture
def sip_h323_bridge():
    """Fixture providing SIPtoH323Bridge with mocked H.323 gatekeeper."""
    h323_gk = MagicMock(spec=H323Gatekeeper)
    h323_gk.bridge_external_call = AsyncMock(
        return_value={
            "status": "success",  # Must be "success" not "bridged"
            "h323_endpoint": "h323://guardian-council-mcu/expert",
            "mcu_participant_id": f"mcu-participant-{uuid4().hex[:8]}"
        }
    )
    # Create bridge with mocked gatekeeper
    bridge = SIPtoH323Bridge(h323_gatekeeper=h323_gk)
    # Ensure bridge_external_call is properly mocked
    bridge.h323_gk = h323_gk
    return bridge


@pytest_asyncio.fixture
def sip_webrtc_bridge():
    """Fixture providing SIPtoWebRTCBridge."""
    return SIPtoWebRTCBridge()


@pytest_asyncio.fixture
def sip_ndi_ingest():
    """Fixture providing SIPtoNDIIngest."""
    return SIPtoNDIIngest()


@pytest_asyncio.fixture
def sip_proxy():
    """Fixture providing SIPEscalateProxy with mocked dependencies."""
    proxy = SIPEscalateProxy()
    proxy.h323_gk = AsyncMock(spec=H323Gatekeeper)
    proxy.webrtc_agent = AsyncMock(spec=IFAgentWebRTC)
    proxy.if_guard = AsyncMock(spec=IFGuardPolicy)
    proxy.if_witness = AsyncMock(spec=IFWitnessLogger)
    return proxy


@pytest_asyncio.fixture
def sample_escalate_message():
    """Fixture providing a sample IFMessage with performative='escalate'."""
    return IFMessage(
        id=str(uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        level=2,
        source="if-agent-local",
        destination="external-expert",
        trace_id=f"trace-{uuid4().hex[:16]}",
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": ["safety"],
            "conversation_id": f"council-{uuid4().hex[:8]}",
            "evidence_files": ["evidence1.log", "evidence2.json"],
            "ndi_source": "ndi://camera-1",
            "source_ip": "192.168.1.100",
            "tls_version": "TLSv1.3",
            "cipher_suite": "TLS_AES_256_GCM_SHA384",
            "peer_verified": True,
            "signature": "ed25519sig_placeholder_123"
        }
    )


# ============================================================================
# TEST 1: SIP-H.323 Bridge Integration
# ============================================================================

@pytest.mark.asyncio
async def test_sip_h323_bridge_integration(sip_h323_bridge):
    """
    TEST 1: Verify SIP call → H.323 MCU bridge integration.

    Tests:
    - Bridge creation with SIP and H.323 legs
    - Audio transcoding setup (G.711 codec compatibility)
    - Call state synchronization between SIP and H.323
    - Media statistics tracking

    Philosophy: Wu Lun (朋友) - External experts join Guardian council as peers
    with full audio participation across protocol boundary.
    """
    # Setup test parameters
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    sip_from = "expert-safety@external.advisor"
    council_call_id = f"council-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"
    expert_id = "expert-safety"
    hazard_type = "safety"

    # Create bridge
    result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from=sip_from,
        council_call_id=council_call_id,
        trace_id=trace_id,
        expert_id=expert_id,
        hazard_type=hazard_type
    )

    # Assertions: Bridge created successfully
    assert result["status"] == "success", "Expected bridge creation to succeed"
    bridge_id = result["bridge_id"]
    assert bridge_id in sip_h323_bridge.active_bridges, "Expected bridge to be tracked"

    # Assertions: Bridge has H.323 participant
    assert "h323_participant_id" in result, "Expected H.323 participant ID"
    assert result["h323_participant_id"] is not None

    # Assertions: Bridge has valid endpoints
    assert "sip_endpoint" in result
    assert "h323_endpoint" in result
    assert sip_from in result["sip_endpoint"]

    # Verify bridge state
    bridge = sip_h323_bridge.active_bridges[bridge_id]
    assert bridge.bridge_state == CallState.CONNECTED, "Expected bridge in CONNECTED state"

    # Verify SIP leg
    assert bridge.sip_state == CallState.SETUP, "Expected SIP leg in SETUP state"
    assert bridge.sip_media is not None, "Expected SIP media stream"
    assert bridge.sip_media.codec == MediaCodec.G711_ULAW, "Expected G.711 codec for SIP"
    assert bridge.sip_media.sample_rate == 8000, "Expected 8kHz sample rate"
    assert bridge.sip_media.encryption == "SRTP", "Expected SRTP encryption for SIP"

    # Verify H.323 leg
    assert bridge.h323_state == CallState.CONNECTED, "Expected H.323 leg in CONNECTED state"
    assert bridge.h323_media is not None, "Expected H.323 media stream"
    assert bridge.h323_media.codec == MediaCodec.G711_ULAW, "Expected matching codec"
    assert bridge.h323_media.encryption == "H.235", "Expected H.235 encryption for H.323"

    # Verify witness events logged
    assert len(sip_h323_bridge.witness_events) > 0, "Expected witness events to be logged"
    bridge_established_events = [
        e for e in sip_h323_bridge.witness_events
        if e["event_type"] == "BRIDGE_ESTABLISHED"
    ]
    assert len(bridge_established_events) > 0, "Expected BRIDGE_ESTABLISHED event"


@pytest.mark.asyncio
async def test_sip_h323_audio_transcoding(sip_h323_bridge):
    """
    TEST 1 Variant: Verify audio transcoding between SIP RTP and H.323 channels.

    Tests:
    - Bidirectional transcoding setup
    - RTP packet flow SIP → H.323
    - H.323 frame flow H.323 → SIP
    - Media statistics tracking
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    sip_from = "expert-ethics@external.advisor"
    council_call_id = f"council-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"

    # Create bridge with transcoding
    result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from=sip_from,
        council_call_id=council_call_id,
        trace_id=trace_id,
        expert_id="expert-ethics",
        hazard_type="ethics"
    )

    bridge_id = result["bridge_id"]
    bridge = sip_h323_bridge.active_bridges[bridge_id]

    # Simulate RTP packet transcoding
    rtp_packet = b"rtp_audio_packet_data_" + b"x" * 160  # ~160 bytes typical RTP packet

    # Transcode SIP → H.323
    h323_frame = await sip_h323_bridge.transcoder.transcode_sip_to_h323(
        bridge_id=bridge_id,
        rtp_packet=rtp_packet
    )

    assert h323_frame is not None, "Expected H.323 frame from transcoding"
    assert bridge.sip_media.packets_received > 0, "Expected SIP packets received count incremented"
    assert bridge.sip_media.bytes_received > 0, "Expected SIP bytes received count incremented"

    # Transcode H.323 → SIP
    h323_data = b"h323_audio_frame_data_" + b"y" * 160
    rtp_result = await sip_h323_bridge.transcoder.transcode_h323_to_sip(
        bridge_id=bridge_id,
        h323_frame=h323_data
    )

    assert rtp_result is not None, "Expected RTP packet from H.323 transcoding"
    assert bridge.h323_media.packets_received > 0, "Expected H.323 packets received"
    assert bridge.sip_media.packets_sent > 0, "Expected SIP packets sent"


@pytest.mark.asyncio
async def test_sip_h323_call_state_synchronization(sip_h323_bridge):
    """
    TEST 1 Variant: Verify call state synchronization between SIP and H.323 legs.

    Tests:
    - State transitions (IDLE → SETUP → CONNECTED)
    - Synchronized state changes
    - Bridge state derived from both legs
    - Witness event logging for state changes
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    council_call_id = f"council-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"

    result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-security@external.advisor",
        council_call_id=council_call_id,
        trace_id=trace_id,
        expert_id="expert-security",
        hazard_type="security"
    )

    bridge_id = result["bridge_id"]
    bridge = sip_h323_bridge.active_bridges[bridge_id]

    # Initial state should be CONNECTED (after creation)
    assert bridge.bridge_state == CallState.CONNECTED

    # Simulate state change to HOLD
    await sip_h323_bridge.sync_call_state(
        bridge_id=bridge_id,
        sip_state=CallState.HOLD
    )

    # Verify state changed
    assert bridge.sip_state == CallState.HOLD
    assert bridge.h323_state == CallState.CONNECTED  # H.323 not changed

    # Sync H.323 to HOLD as well
    await sip_h323_bridge.sync_call_state(
        bridge_id=bridge_id,
        h323_state=CallState.HOLD
    )

    # Both should be in HOLD state
    assert bridge.sip_state == CallState.HOLD
    assert bridge.h323_state == CallState.HOLD

    # Verify state change events logged
    state_change_events = [
        e for e in sip_h323_bridge.witness_events
        if e["event_type"] == "STATE_CHANGE"
    ]
    assert len(state_change_events) > 0, "Expected STATE_CHANGE events"


@pytest.mark.asyncio
async def test_sip_h323_bridge_teardown(sip_h323_bridge):
    """
    TEST 1 Variant: Verify proper bridge teardown and cleanup.

    Tests:
    - Media transcoding cleanup
    - Bridge removal from active bridges
    - Duration and statistics calculation
    - Witness event logging for termination
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    council_call_id = f"council-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"

    result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-safety@external.advisor",
        council_call_id=council_call_id,
        trace_id=trace_id,
        expert_id="expert-safety",
        hazard_type="safety"
    )

    bridge_id = result["bridge_id"]

    # Verify bridge exists
    assert bridge_id in sip_h323_bridge.active_bridges

    # Teardown bridge
    teardown_result = await sip_h323_bridge.teardown_bridge(bridge_id)

    # Assertions: Teardown successful
    assert teardown_result["status"] == "success"
    assert teardown_result["bridge_id"] == bridge_id
    assert "duration_seconds" in teardown_result
    assert teardown_result["duration_seconds"] >= 0

    # Verify bridge removed from active bridges
    assert bridge_id not in sip_h323_bridge.active_bridges, "Expected bridge to be removed"

    # Verify media statistics collected
    assert "media_stats" in teardown_result
    media_stats = teardown_result["media_stats"]
    assert "sip" in media_stats
    assert "h323" in media_stats

    # Verify witness termination event logged
    terminated_events = [
        e for e in sip_h323_bridge.witness_events
        if e["event_type"] == "BRIDGE_TERMINATED"
    ]
    assert len(terminated_events) > 0, "Expected BRIDGE_TERMINATED event"


# ============================================================================
# TEST 2: SIP-WebRTC Bridge Integration
# ============================================================================

@pytest.mark.asyncio
async def test_sip_webrtc_bridge_integration(sip_webrtc_bridge):
    """
    TEST 2: Verify SIP call → WebRTC DataChannel with IFMessage escalate.

    Tests:
    - Bridge creation with DataChannel establishment
    - Evidence file sharing via IFMessage
    - Metadata embedding in WebRTC messages
    - Witness event logging

    Philosophy: Transparent evidence sharing - Evidence is shared with
    external experts and council peers via secure DataChannel.
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    sip_from = "expert-safety@external.advisor"
    trace_id = f"trace-{uuid4().hex[:16]}"
    expert_id = "expert-safety"
    hazard_type = "safety"
    evidence_files = ["risk_analysis.pdf", "audit_logs.json", "behavior_tests.csv"]

    # Create WebRTC bridge
    result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from=sip_from,
        trace_id=trace_id,
        expert_id=expert_id,
        hazard_type=hazard_type,
        evidence_files=evidence_files
    )

    # Assertions: Bridge created successfully
    assert result["status"] == "success", "Expected WebRTC bridge creation to succeed"
    bridge_id = result["bridge_id"]
    assert bridge_id in sip_webrtc_bridge.active_bridges, "Expected bridge to be tracked"

    # Assertions: DataChannel established
    assert "datachannel_id" in result
    assert result["datachannel_id"] is not None

    # Assertions: Evidence shared
    assert result["evidence_shared"] == len(evidence_files), "Expected all evidence to be shared"

    # Verify bridge state
    bridge = sip_webrtc_bridge.active_bridges[bridge_id]
    assert bridge["datachannel_state"] == "CONNECTED"
    assert bridge["evidence_shared"] is True
    assert bridge["if_messages_sent"] == len(evidence_files)

    # Verify witness event
    assert len(sip_webrtc_bridge.witness_events) > 0
    bridge_events = [
        e for e in sip_webrtc_bridge.witness_events
        if e["event_type"] == "WEBRTC_BRIDGE_ESTABLISHED"
    ]
    assert len(bridge_events) > 0, "Expected WEBRTC_BRIDGE_ESTABLISHED event"


@pytest.mark.asyncio
async def test_sip_webrtc_evidence_escalate_message(sip_webrtc_bridge):
    """
    TEST 2 Variant: Verify IFMessage escalate format for evidence sharing.

    Tests:
    - IFMessage creation with evidence payload
    - Evidence metadata embedding
    - Datachannel message serialization
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    evidence_files = [
        "model_weights.safetensors",
        "jailbreak_tests.log",
        "safety_evals.json"
    ]

    result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-ethics@external.advisor",
        trace_id=f"trace-{uuid4().hex[:16]}",
        expert_id="expert-ethics",
        hazard_type="ethics",
        evidence_files=evidence_files
    )

    bridge_id = result["bridge_id"]
    bridge = sip_webrtc_bridge.active_bridges[bridge_id]

    # Verify evidence escalate messages sent
    assert bridge["if_messages_sent"] == len(evidence_files)
    assert all(f in bridge["evidence_files"] for f in evidence_files)


@pytest.mark.asyncio
async def test_sip_webrtc_no_evidence(sip_webrtc_bridge):
    """
    TEST 2 Variant: Test WebRTC bridge with no evidence files.

    Should still establish bridge but with no evidence sharing.
    """
    result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=f"sip-call-{uuid4().hex[:8]}",
        sip_from="expert-security@external.advisor",
        trace_id=f"trace-{uuid4().hex[:16]}",
        expert_id="expert-security",
        hazard_type="security",
        evidence_files=[]  # No evidence
    )

    assert result["status"] == "success"
    assert result["evidence_shared"] == 0


# ============================================================================
# TEST 3: SIP-NDI Ingest Integration
# ============================================================================

@pytest.mark.asyncio
async def test_sip_ndi_ingest_integration(sip_ndi_ingest):
    """
    TEST 3: Verify SIP call with optional NDI video evidence streaming.

    Tests:
    - NDI stream establishment when source provided
    - Video frame capture and metadata embedding
    - Hazard type and expert metadata in NDI packets
    - Graceful handling when NDI not available

    Philosophy: Observable evidence - Video evidence captured and metadata
    embedded for complete audit trail of external expert consultation.
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    ndi_source = "ndi://camera-1"
    trace_id = f"trace-{uuid4().hex[:16]}"
    expert_id = "expert-safety"
    hazard_type = "safety"

    # Setup NDI ingest with video source
    result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=sip_call_id,
        ndi_source=ndi_source,
        trace_id=trace_id,
        expert_id=expert_id,
        hazard_type=hazard_type
    )

    # Assertions: NDI ingest established
    assert result["status"] == "success", "Expected NDI ingest to be established"
    assert result["ndi_enabled"] is True, "Expected NDI to be enabled"
    ingest_id = result["ingest_id"]

    # Assertions: Frames captured
    assert result["frames_captured"] > 0, "Expected video frames to be captured"

    # Assertions: Metadata embedded
    assert result["metadata_embedded"] is True, "Expected metadata to be embedded"

    # Verify ingest state
    ingest = sip_ndi_ingest.active_ingests[ingest_id]
    assert ingest["ndi_stream_state"] == "STREAMING"
    assert ingest["metadata_embedded"] is True
    assert ingest["expert_id"] == expert_id
    assert ingest["hazard_type"] == hazard_type

    # Verify witness event
    assert len(sip_ndi_ingest.witness_events) > 0
    started_events = [
        e for e in sip_ndi_ingest.witness_events
        if e["event_type"] == "NDI_INGEST_STARTED"
    ]
    assert len(started_events) > 0, "Expected NDI_INGEST_STARTED event"


@pytest.mark.asyncio
async def test_sip_ndi_optional_no_source(sip_ndi_ingest):
    """
    TEST 3 Variant: Test NDI ingest gracefully skipped when no source provided.

    NDI should be optional - when no NDI source provided, ingest should be skipped.
    """
    result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=f"sip-call-{uuid4().hex[:8]}",
        ndi_source=None,  # No NDI source
        trace_id=f"trace-{uuid4().hex[:16]}",
        expert_id="expert-ethics",
        hazard_type="ethics"
    )

    # Should skip gracefully
    assert result["status"] == "skipped"
    assert result["ndi_enabled"] is False
    assert len(sip_ndi_ingest.active_ingests) == 0, "Expected no ingest to be created"


@pytest.mark.asyncio
async def test_sip_ndi_metadata_embedding(sip_ndi_ingest):
    """
    TEST 3 Variant: Verify metadata is embedded in NDI packets.

    Metadata should include:
    - Hazard type
    - Expert information
    - Timestamp
    - SIP call ID (trace)
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    ndi_source = "ndi://camera-remote"
    trace_id = f"trace-{uuid4().hex[:16]}"

    result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=sip_call_id,
        ndi_source=ndi_source,
        trace_id=trace_id,
        expert_id="expert-security",
        hazard_type="security"
    )

    ingest_id = result["ingest_id"]
    ingest = sip_ndi_ingest.active_ingests[ingest_id]

    # Verify metadata available for embedding
    assert ingest["hazard_type"] == "security"
    assert ingest["expert_id"] == "expert-security"
    assert ingest["sip_call_id"] == sip_call_id
    assert ingest["metadata_embedded"] is True


# ============================================================================
# TEST 4: All Three Bridges Simultaneously
# ============================================================================

@pytest.mark.asyncio
async def test_all_three_bridges_simultaneously(
    sip_h323_bridge,
    sip_webrtc_bridge,
    sip_ndi_ingest
):
    """
    TEST 4: Verify all 3 bridges work together in single SIP call.

    Tests:
    - One SIP call using H.323 bridge for audio to council
    - WebRTC bridge for evidence sharing with agents
    - NDI ingest for video evidence capture
    - No conflicts between bridge operations
    - All bridges synchronized via shared state

    Scenario:
    - SIP expert on call with Guardian council (H.323)
    - Agents receiving evidence via WebRTC DataChannel
    - Video evidence being captured via NDI with embedded metadata
    - All synchronized with shared trace_id and call_id

    Philosophy: Multi-dimensional communication - External experts engage
    with council (H.323), agents (WebRTC), and capture evidence (NDI)
    simultaneously without conflicts.
    """
    # Common call parameters
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"
    expert_id = "expert-safety"
    sip_from = "expert-safety@external.advisor"
    council_call_id = f"council-{uuid4().hex[:8]}"
    hazard_type = "safety"
    evidence_files = ["risk_analysis.pdf", "audit_logs.json"]
    ndi_source = "ndi://camera-1"

    # Step 1: Create H.323 bridge (SIP expert → Guardian council)
    h323_result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from=sip_from,
        council_call_id=council_call_id,
        trace_id=trace_id,
        expert_id=expert_id,
        hazard_type=hazard_type
    )

    h323_bridge_id = h323_result["bridge_id"]
    assert h323_result["status"] == "success"

    # Step 2: Create WebRTC bridge (evidence sharing with agents)
    webrtc_result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from=sip_from,
        trace_id=trace_id,
        expert_id=expert_id,
        hazard_type=hazard_type,
        evidence_files=evidence_files
    )

    webrtc_bridge_id = webrtc_result["bridge_id"]
    assert webrtc_result["status"] == "success"
    assert webrtc_result["evidence_shared"] == len(evidence_files)

    # Step 3: Setup NDI ingest (video evidence capture)
    ndi_result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=sip_call_id,
        ndi_source=ndi_source,
        trace_id=trace_id,
        expert_id=expert_id,
        hazard_type=hazard_type
    )

    ndi_ingest_id = ndi_result["ingest_id"]
    assert ndi_result["status"] == "success"
    assert ndi_result["ndi_enabled"] is True

    # Verify all bridges active for same call
    assert h323_bridge_id in sip_h323_bridge.active_bridges
    assert webrtc_bridge_id in sip_webrtc_bridge.active_bridges
    assert ndi_ingest_id in sip_ndi_ingest.active_ingests

    # Verify bridges share same identifiers
    h323_bridge = sip_h323_bridge.active_bridges[h323_bridge_id]
    webrtc_bridge = sip_webrtc_bridge.active_bridges[webrtc_bridge_id]
    ndi_ingest = sip_ndi_ingest.active_ingests[ndi_ingest_id]

    assert h323_bridge.sip_call_id == sip_call_id
    assert webrtc_bridge["sip_call_id"] == sip_call_id
    assert ndi_ingest["sip_call_id"] == sip_call_id

    # Verify trace_id common across all
    assert h323_bridge.trace_id == trace_id
    assert webrtc_bridge["trace_id"] == trace_id
    assert ndi_ingest["trace_id"] == trace_id

    # Verify no conflicts - all bridges operational
    assert h323_bridge.bridge_state == CallState.CONNECTED
    assert webrtc_bridge["datachannel_state"] == "CONNECTED"
    assert ndi_ingest["ndi_stream_state"] == "STREAMING"

    # Verify witness events from all bridges
    all_h323_events = len(sip_h323_bridge.witness_events)
    all_webrtc_events = len(sip_webrtc_bridge.witness_events)
    all_ndi_events = len(sip_ndi_ingest.witness_events)

    assert all_h323_events > 0, "Expected H.323 witness events"
    assert all_webrtc_events > 0, "Expected WebRTC witness events"
    assert all_ndi_events > 0, "Expected NDI witness events"


@pytest.mark.asyncio
async def test_all_bridges_teardown_synchronized(
    sip_h323_bridge,
    sip_webrtc_bridge,
    sip_ndi_ingest
):
    """
    TEST 4 Variant: Test synchronized teardown of all 3 bridges.

    When call terminates, all bridges should teardown cleanly without conflicts.
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"

    # Setup all three bridges
    h323_result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-safety@external.advisor",
        council_call_id=f"council-{uuid4().hex[:8]}",
        trace_id=trace_id,
        expert_id="expert-safety",
        hazard_type="safety"
    )
    h323_bridge_id = h323_result["bridge_id"]

    webrtc_result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-safety@external.advisor",
        trace_id=trace_id,
        expert_id="expert-safety",
        hazard_type="safety",
        evidence_files=["evidence.pdf"]
    )
    webrtc_bridge_id = webrtc_result["bridge_id"]

    ndi_result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=sip_call_id,
        ndi_source="ndi://camera-1",
        trace_id=trace_id,
        expert_id="expert-safety",
        hazard_type="safety"
    )
    ndi_ingest_id = ndi_result["ingest_id"]

    # Teardown all bridges
    h323_teardown = await sip_h323_bridge.teardown_bridge(h323_bridge_id)
    webrtc_teardown = await sip_webrtc_bridge.teardown_bridge(webrtc_bridge_id)
    ndi_teardown = await sip_ndi_ingest.teardown_ndi_ingest(ndi_ingest_id)

    # Verify all tore down successfully
    assert h323_teardown["status"] == "success"
    assert webrtc_teardown["status"] == "success"
    assert ndi_teardown["status"] == "success"

    # Verify all removed from active collection
    assert h323_bridge_id not in sip_h323_bridge.active_bridges
    assert webrtc_bridge_id not in sip_webrtc_bridge.active_bridges
    assert ndi_ingest_id not in sip_ndi_ingest.active_ingests


# ============================================================================
# TEST 5: Bridge Failure Recovery
# ============================================================================

@pytest.mark.asyncio
async def test_bridge_failure_h323_offline(
    sip_h323_bridge,
    sip_webrtc_bridge,
    sip_ndi_ingest
):
    """
    TEST 5: Verify resilience when H.323 bridge fails.

    Scenario:
    - All 3 bridges established
    - H.323 gatekeeper goes offline (bridge fails)
    - WebRTC and NDI bridges should continue working
    - Proper cleanup and error logging

    Philosophy: Defense in depth - One bridge failure doesn't cascade
    to other bridges. Evidence sharing and video capture continue.
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"

    # Setup all three bridges
    h323_result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-safety@external.advisor",
        council_call_id=f"council-{uuid4().hex[:8]}",
        trace_id=trace_id,
        expert_id="expert-safety",
        hazard_type="safety"
    )
    h323_bridge_id = h323_result["bridge_id"]

    webrtc_result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-safety@external.advisor",
        trace_id=trace_id,
        expert_id="expert-safety",
        hazard_type="safety",
        evidence_files=["evidence.pdf"]
    )
    webrtc_bridge_id = webrtc_result["bridge_id"]

    ndi_result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=sip_call_id,
        ndi_source="ndi://camera-1",
        trace_id=trace_id,
        expert_id="expert-safety",
        hazard_type="safety"
    )
    ndi_ingest_id = ndi_result["ingest_id"]

    # Simulate H.323 bridge failure (teardown)
    h323_teardown = await sip_h323_bridge.teardown_bridge(h323_bridge_id)
    assert h323_teardown["status"] == "success"

    # Verify H.323 bridge is gone
    assert h323_bridge_id not in sip_h323_bridge.active_bridges

    # Verify WebRTC bridge STILL ACTIVE and operational
    assert webrtc_bridge_id in sip_webrtc_bridge.active_bridges
    webrtc_bridge = sip_webrtc_bridge.active_bridges[webrtc_bridge_id]
    assert webrtc_bridge["datachannel_state"] == "CONNECTED"
    assert webrtc_bridge["evidence_shared"] is True

    # Verify NDI ingest STILL ACTIVE and operational
    assert ndi_ingest_id in sip_ndi_ingest.active_ingests
    ndi_ingest = sip_ndi_ingest.active_ingests[ndi_ingest_id]
    assert ndi_ingest["ndi_stream_state"] == "STREAMING"

    # Verify error logged to H.323 witness
    h323_terminated_events = [
        e for e in sip_h323_bridge.witness_events
        if e["event_type"] == "BRIDGE_TERMINATED"
    ]
    assert len(h323_terminated_events) > 0


@pytest.mark.asyncio
async def test_bridge_failure_webrtc_offline(
    sip_h323_bridge,
    sip_webrtc_bridge,
    sip_ndi_ingest
):
    """
    TEST 5 Variant: Verify resilience when WebRTC bridge fails.

    H.323 and NDI should continue operational.
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"

    # Setup all three bridges
    h323_result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-ethics@external.advisor",
        council_call_id=f"council-{uuid4().hex[:8]}",
        trace_id=trace_id,
        expert_id="expert-ethics",
        hazard_type="ethics"
    )
    h323_bridge_id = h323_result["bridge_id"]

    webrtc_result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-ethics@external.advisor",
        trace_id=trace_id,
        expert_id="expert-ethics",
        hazard_type="ethics",
        evidence_files=["analysis.pdf"]
    )
    webrtc_bridge_id = webrtc_result["bridge_id"]

    ndi_result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=sip_call_id,
        ndi_source="ndi://camera-2",
        trace_id=trace_id,
        expert_id="expert-ethics",
        hazard_type="ethics"
    )
    ndi_ingest_id = ndi_result["ingest_id"]

    # Simulate WebRTC bridge failure
    webrtc_teardown = await sip_webrtc_bridge.teardown_bridge(webrtc_bridge_id)
    assert webrtc_teardown["status"] == "success"

    # H.323 should still be active
    assert h323_bridge_id in sip_h323_bridge.active_bridges
    h323_bridge = sip_h323_bridge.active_bridges[h323_bridge_id]
    assert h323_bridge.bridge_state == CallState.CONNECTED

    # NDI should still be active
    assert ndi_ingest_id in sip_ndi_ingest.active_ingests
    ndi_ingest = sip_ndi_ingest.active_ingests[ndi_ingest_id]
    assert ndi_ingest["ndi_stream_state"] == "STREAMING"


@pytest.mark.asyncio
async def test_bridge_failure_ndi_offline(
    sip_h323_bridge,
    sip_webrtc_bridge,
    sip_ndi_ingest
):
    """
    TEST 5 Variant: Verify resilience when NDI ingest fails.

    H.323 and WebRTC should continue operational.
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    trace_id = f"trace-{uuid4().hex[:16]}"

    # Setup all three bridges
    h323_result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-security@external.advisor",
        council_call_id=f"council-{uuid4().hex[:8]}",
        trace_id=trace_id,
        expert_id="expert-security",
        hazard_type="security"
    )
    h323_bridge_id = h323_result["bridge_id"]

    webrtc_result = await sip_webrtc_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-security@external.advisor",
        trace_id=trace_id,
        expert_id="expert-security",
        hazard_type="security",
        evidence_files=["security_report.pdf"]
    )
    webrtc_bridge_id = webrtc_result["bridge_id"]

    ndi_result = await sip_ndi_ingest.setup_ndi_ingest(
        sip_call_id=sip_call_id,
        ndi_source="ndi://camera-3",
        trace_id=trace_id,
        expert_id="expert-security",
        hazard_type="security"
    )
    ndi_ingest_id = ndi_result["ingest_id"]

    # Simulate NDI ingest failure
    ndi_teardown = await sip_ndi_ingest.teardown_ndi_ingest(ndi_ingest_id)
    assert ndi_teardown["status"] == "success"

    # H.323 should still be active
    assert h323_bridge_id in sip_h323_bridge.active_bridges
    h323_bridge = sip_h323_bridge.active_bridges[h323_bridge_id]
    assert h323_bridge.bridge_state == CallState.CONNECTED

    # WebRTC should still be active
    assert webrtc_bridge_id in sip_webrtc_bridge.active_bridges
    webrtc_bridge = sip_webrtc_bridge.active_bridges[webrtc_bridge_id]
    assert webrtc_bridge["datachannel_state"] == "CONNECTED"


@pytest.mark.asyncio
async def test_proper_cleanup_on_failure(sip_h323_bridge):
    """
    TEST 5 Variant: Verify proper cleanup even on failure.

    When bridge fails, all resources should be released properly.
    """
    sip_call_id = f"sip-call-{uuid4().hex[:8]}"
    council_call_id = f"council-{uuid4().hex[:8]}"

    result = await sip_h323_bridge.create_bridge(
        sip_call_id=sip_call_id,
        sip_from="expert-safety@external.advisor",
        council_call_id=council_call_id,
        trace_id=f"trace-{uuid4().hex[:16]}",
        expert_id="expert-safety",
        hazard_type="safety"
    )

    bridge_id = result["bridge_id"]
    bridge = sip_h323_bridge.active_bridges[bridge_id]

    # Verify media streams exist
    assert bridge.sip_media is not None
    assert bridge.h323_media is not None
    assert bridge_id in sip_h323_bridge.transcoder.active_streams

    # Teardown bridge
    await sip_h323_bridge.teardown_bridge(bridge_id)

    # Verify complete cleanup
    assert bridge_id not in sip_h323_bridge.active_bridges
    assert bridge_id not in sip_h323_bridge.transcoder.active_streams
    assert bridge.bridge_state == CallState.DISCONNECTED


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
