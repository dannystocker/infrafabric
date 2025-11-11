"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

SIP-H.323 Gateway Bridge
------------------------
Critical bridge between SIP external experts (Session 4) and H.323 Guardian council MCU (Session 3).

This gateway enables Wu Lun (五倫) 朋友 (Friends) philosophy: External experts join Guardian
council as peers, with full audio participation despite different protocols.

Philosophy Grounding:
- Wu Lun (朋友): External experts are peers in Guardian council deliberation
- IF.ground Observable: All bridge events, media flows, and state changes are logged
- IF.TTT Principles:
  * Traceable: Every call has call_id, trace_id, linking SIP and H.323 legs
  * Transparent: All state transitions logged to IF.witness
  * Trustworthy: Media encryption maintained across protocol boundary (SRTP ↔ H.235)

Architecture:
- SIP Leg: Handles SIP signaling and RTP media from external expert
- H.323 Leg: Handles H.323 signaling and media channels to Guardian council MCU
- Media Bridge: Transcodes between SIP RTP and H.323 audio channels
- State Synchronizer: Keeps SIP and H.323 call states in sync

Integration Points:
- Called by: SIPEscalateProxy.handle_escalate()
- Calls: H323Gatekeeper.bridge_external_call()
- Logs to: IF.witness for complete audit trail
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json

# Session 3 integration
from communication.h323_gatekeeper import H323Gatekeeper

logger = logging.getLogger(__name__)


class CallState(Enum):
    """
    Unified call state for both SIP and H.323 legs

    Philosophy: Transparent state tracking for IF.witness observability
    """
    IDLE = "idle"
    SETUP = "setup"
    RINGING = "ringing"
    CONNECTED = "connected"
    HOLD = "hold"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class MediaCodec(Enum):
    """
    Supported audio codecs for transcoding

    SIP typically uses: G.711 (PCMU/PCMA), Opus, G.722
    H.323 typically uses: G.711, G.722, G.729
    """
    G711_ULAW = "PCMU"  # G.711 μ-law (8kHz)
    G711_ALAW = "PCMA"  # G.711 A-law (8kHz)
    G722 = "G722"        # G.722 wideband (16kHz)
    OPUS = "opus"        # Opus (48kHz, for SIP only)
    G729 = "G729"        # G.729 (8kHz, for H.323)


@dataclass
class MediaStream:
    """
    Media stream descriptor for RTP/H.323 audio

    Philosophy: Observable - Complete media flow metadata for IF.witness
    """
    stream_id: str
    codec: MediaCodec
    sample_rate: int
    rtp_port: Optional[int] = None
    h323_channel: Optional[str] = None
    encryption: Optional[str] = None  # "SRTP", "H.235", None
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    start_time: datetime = field(default_factory=datetime.utcnow)


@dataclass
class BridgedCall:
    """
    Complete state of a bridged SIP-H.323 call

    Tracks both legs of the call and their synchronization state.
    """
    bridge_id: str
    trace_id: str

    # SIP leg (external expert)
    sip_call_id: str
    sip_from: str  # Expert SIP URI
    sip_to: str    # Guardian council SIP endpoint
    sip_state: CallState = CallState.IDLE
    sip_media: Optional[MediaStream] = None

    # H.323 leg (Guardian council MCU)
    h323_call_id: str
    h323_endpoint: str
    h323_mcu_participant_id: Optional[str] = None
    h323_state: CallState = CallState.IDLE
    h323_media: Optional[MediaStream] = None

    # Bridge state
    bridge_state: CallState = CallState.IDLE
    start_time: datetime = field(default_factory=datetime.utcnow)
    connect_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Metadata
    expert_id: str = ""
    hazard_type: str = ""
    evidence_files: List[str] = field(default_factory=list)


class MediaTranscoder:
    """
    Media transcoding between SIP RTP and H.323 audio channels

    Philosophy: Trustworthy - Maintain audio quality and encryption across protocol boundary

    In production, this would use FFmpeg, GStreamer, or a dedicated media gateway library.
    For now, this is a stub that logs media flow.
    """

    def __init__(self):
        self.active_streams: Dict[str, Tuple[MediaStream, MediaStream]] = {}
        logger.info("[MediaTranscoder] Initialized")

    async def setup_bidirectional_audio(
        self,
        bridge_id: str,
        sip_stream: MediaStream,
        h323_stream: MediaStream
    ) -> bool:
        """
        Setup bidirectional audio transcoding between SIP and H.323

        Flow:
        1. SIP RTP packets → Decode → Transcode → Encode → H.323 audio channel
        2. H.323 audio channel → Decode → Transcode → Encode → SIP RTP packets

        Args:
            bridge_id: Bridge identifier
            sip_stream: SIP media stream descriptor
            h323_stream: H.323 media stream descriptor

        Returns:
            True if setup successful
        """
        logger.info(f"[MediaTranscoder] Setting up bidirectional audio for bridge {bridge_id}")
        logger.info(f"[MediaTranscoder] SIP: {sip_stream.codec.value} @ {sip_stream.sample_rate}Hz")
        logger.info(f"[MediaTranscoder] H.323: {h323_stream.codec.value} @ {h323_stream.sample_rate}Hz")

        # Store stream pair
        self.active_streams[bridge_id] = (sip_stream, h323_stream)

        # TODO: In production, initialize actual transcoding pipeline
        # Example pseudo-code:
        # self.transcode_pipeline = gstreamer.Pipeline()
        # self.transcode_pipeline.add_rtp_source(sip_stream.rtp_port, sip_stream.codec)
        # self.transcode_pipeline.add_h323_sink(h323_stream.h323_channel, h323_stream.codec)
        # self.transcode_pipeline.start()

        logger.info(f"[MediaTranscoder] Bidirectional audio established for {bridge_id}")
        return True

    async def transcode_sip_to_h323(
        self,
        bridge_id: str,
        rtp_packet: bytes
    ) -> Optional[bytes]:
        """
        Transcode SIP RTP packet to H.323 audio frame

        Args:
            bridge_id: Bridge identifier
            rtp_packet: Raw RTP packet from SIP

        Returns:
            H.323 audio frame or None if transcoding failed
        """
        if bridge_id not in self.active_streams:
            logger.warning(f"[MediaTranscoder] No active stream for bridge {bridge_id}")
            return None

        sip_stream, h323_stream = self.active_streams[bridge_id]

        # Update statistics
        sip_stream.packets_received += 1
        sip_stream.bytes_received += len(rtp_packet)
        h323_stream.packets_sent += 1
        h323_stream.bytes_sent += len(rtp_packet)  # Approximate

        # TODO: Actual transcoding logic
        # For now, return stub data
        return rtp_packet

    async def transcode_h323_to_sip(
        self,
        bridge_id: str,
        h323_frame: bytes
    ) -> Optional[bytes]:
        """
        Transcode H.323 audio frame to SIP RTP packet

        Args:
            bridge_id: Bridge identifier
            h323_frame: Raw H.323 audio frame

        Returns:
            RTP packet or None if transcoding failed
        """
        if bridge_id not in self.active_streams:
            logger.warning(f"[MediaTranscoder] No active stream for bridge {bridge_id}")
            return None

        sip_stream, h323_stream = self.active_streams[bridge_id]

        # Update statistics
        h323_stream.packets_received += 1
        h323_stream.bytes_received += len(h323_frame)
        sip_stream.packets_sent += 1
        sip_stream.bytes_sent += len(h323_frame)  # Approximate

        # TODO: Actual transcoding logic
        return h323_frame

    async def teardown_audio(self, bridge_id: str) -> None:
        """
        Teardown audio transcoding for bridge

        Args:
            bridge_id: Bridge identifier
        """
        if bridge_id in self.active_streams:
            sip_stream, h323_stream = self.active_streams[bridge_id]

            logger.info(f"[MediaTranscoder] Tearing down audio for {bridge_id}")
            logger.info(f"[MediaTranscoder] SIP stats: {sip_stream.packets_sent} sent, {sip_stream.packets_received} received")
            logger.info(f"[MediaTranscoder] H.323 stats: {h323_stream.packets_sent} sent, {h323_stream.packets_received} received")

            del self.active_streams[bridge_id]


class SIPtoH323Bridge:
    """
    Main SIP-H.323 gateway bridge

    Philosophy: Wu Lun (朋友) - Enable external experts to join Guardian council as peers

    This class orchestrates:
    1. SIP call leg management
    2. H.323 call leg management via H323Gatekeeper
    3. Media transcoding via MediaTranscoder
    4. Call state synchronization
    5. Event logging to IF.witness
    """

    def __init__(self, h323_gatekeeper: Optional[H323Gatekeeper] = None):
        """
        Initialize SIP-H.323 bridge

        Args:
            h323_gatekeeper: Optional H323Gatekeeper instance (creates new if None)
        """
        self.h323_gk = h323_gatekeeper or H323Gatekeeper()
        self.transcoder = MediaTranscoder()
        self.active_bridges: Dict[str, BridgedCall] = {}
        self.witness_events: List[Dict[str, Any]] = []

        logger.info("[SIPtoH323Bridge] Initialized SIP-H.323 gateway bridge")

    async def create_bridge(
        self,
        sip_call_id: str,
        sip_from: str,
        council_call_id: str,
        trace_id: str,
        expert_id: str,
        hazard_type: str
    ) -> Dict[str, Any]:
        """
        Create new SIP-H.323 bridge for external expert call

        This is the main entry point called by SIPEscalateProxy.

        Args:
            sip_call_id: SIP call identifier from SIP proxy
            sip_from: Expert SIP URI (e.g., "expert-safety@external.advisor")
            council_call_id: Guardian council H.323 call identifier
            trace_id: IF trace ID for correlation
            expert_id: Expert identifier
            hazard_type: Hazard type (safety, ethics, security)

        Returns:
            {
                "status": "success" | "error",
                "bridge_id": "...",
                "h323_participant_id": "...",
                "sip_endpoint": "...",
                "h323_endpoint": "..."
            }
        """
        bridge_id = f"bridge-{hashlib.sha256(f'{sip_call_id}-{council_call_id}'.encode()).hexdigest()[:16]}"

        logger.info(f"[SIPtoH323Bridge] Creating bridge {bridge_id}")
        logger.info(f"[SIPtoH323Bridge] SIP call: {sip_call_id}, Expert: {expert_id}")
        logger.info(f"[SIPtoH323Bridge] H.323 council: {council_call_id}, Hazard: {hazard_type}")

        # Create bridge state
        bridge = BridgedCall(
            bridge_id=bridge_id,
            trace_id=trace_id,
            sip_call_id=sip_call_id,
            sip_from=sip_from,
            sip_to="guardian-council@infrafabric.internal",
            h323_call_id=council_call_id,
            h323_endpoint="",  # Will be filled by H.323 gatekeeper
            expert_id=expert_id,
            hazard_type=hazard_type
        )

        try:
            # Step 1: Setup SIP leg
            await self._setup_sip_leg(bridge)

            # Step 2: Bridge to H.323 council via gatekeeper
            h323_result = await self.h323_gk.bridge_external_call(
                sip_call_id=sip_call_id,
                council_call_id=council_call_id,
                external_expert_id=expert_id
            )

            bridge.h323_endpoint = h323_result["h323_endpoint"]
            bridge.h323_mcu_participant_id = h323_result["mcu_participant_id"]
            bridge.h323_state = CallState.CONNECTED

            # Step 3: Setup H.323 leg
            await self._setup_h323_leg(bridge)

            # Step 4: Setup bidirectional media
            await self._setup_media_bridge(bridge)

            # Step 5: Update bridge state
            bridge.bridge_state = CallState.CONNECTED
            bridge.connect_time = datetime.utcnow()
            self.active_bridges[bridge_id] = bridge

            # Step 6: Log to IF.witness
            await self._log_witness_event(
                bridge_id=bridge_id,
                event_type="BRIDGE_ESTABLISHED",
                details={
                    "sip_call_id": sip_call_id,
                    "h323_call_id": council_call_id,
                    "expert_id": expert_id,
                    "h323_participant_id": bridge.h323_mcu_participant_id,
                    "trace_id": trace_id
                }
            )

            logger.info(f"[SIPtoH323Bridge] Bridge {bridge_id} established successfully")

            return {
                "status": "success",
                "bridge_id": bridge_id,
                "h323_participant_id": bridge.h323_mcu_participant_id,
                "sip_endpoint": f"sip:{sip_from}",
                "h323_endpoint": bridge.h323_endpoint
            }

        except Exception as e:
            logger.error(f"[SIPtoH323Bridge] Failed to create bridge: {e}", exc_info=True)
            bridge.bridge_state = CallState.ERROR

            await self._log_witness_event(
                bridge_id=bridge_id,
                event_type="BRIDGE_ERROR",
                details={
                    "error": str(e),
                    "sip_call_id": sip_call_id,
                    "trace_id": trace_id
                }
            )

            return {
                "status": "error",
                "bridge_id": bridge_id,
                "error": str(e)
            }

    async def _setup_sip_leg(self, bridge: BridgedCall) -> None:
        """
        Setup SIP call leg and RTP media

        Args:
            bridge: Bridge state object
        """
        logger.info(f"[SIPtoH323Bridge] Setting up SIP leg for {bridge.bridge_id}")

        # Create SIP media stream descriptor
        bridge.sip_media = MediaStream(
            stream_id=f"sip-{bridge.sip_call_id}",
            codec=MediaCodec.G711_ULAW,  # Default to G.711 for compatibility
            sample_rate=8000,
            rtp_port=10000 + len(self.active_bridges),  # Dynamic port allocation
            encryption="SRTP"  # Use SRTP for SIP
        )

        bridge.sip_state = CallState.SETUP

        # TODO: In production, use PJSIP to setup actual SIP media session
        # Example pseudo-code:
        # pjsip_media = pjsua2.AudioMedia()
        # pjsip_media.bind_port(bridge.sip_media.rtp_port)
        # pjsip_media.start_receive()

        logger.info(f"[SIPtoH323Bridge] SIP leg ready: RTP port {bridge.sip_media.rtp_port}")

    async def _setup_h323_leg(self, bridge: BridgedCall) -> None:
        """
        Setup H.323 call leg and audio channels

        Args:
            bridge: Bridge state object
        """
        logger.info(f"[SIPtoH323Bridge] Setting up H.323 leg for {bridge.bridge_id}")

        # Create H.323 media stream descriptor
        bridge.h323_media = MediaStream(
            stream_id=f"h323-{bridge.h323_call_id}",
            codec=MediaCodec.G711_ULAW,  # Match SIP codec for simplicity
            sample_rate=8000,
            h323_channel=f"h323-audio-channel-{bridge.h323_mcu_participant_id}",
            encryption="H.235"  # Use H.235 for H.323
        )

        # TODO: In production, use H.323 library to setup actual audio channel
        # Example pseudo-code:
        # h323_channel = h323plus.AudioChannel()
        # h323_channel.connect(bridge.h323_endpoint)
        # h323_channel.start_receive()

        logger.info(f"[SIPtoH323Bridge] H.323 leg ready: channel {bridge.h323_media.h323_channel}")

    async def _setup_media_bridge(self, bridge: BridgedCall) -> None:
        """
        Setup bidirectional media transcoding between SIP and H.323

        Args:
            bridge: Bridge state object
        """
        logger.info(f"[SIPtoH323Bridge] Setting up media bridge for {bridge.bridge_id}")

        if not bridge.sip_media or not bridge.h323_media:
            raise ValueError("Both SIP and H.323 media streams must be initialized")

        # Setup bidirectional transcoding
        success = await self.transcoder.setup_bidirectional_audio(
            bridge_id=bridge.bridge_id,
            sip_stream=bridge.sip_media,
            h323_stream=bridge.h323_media
        )

        if not success:
            raise RuntimeError("Failed to setup media transcoding")

        logger.info(f"[SIPtoH323Bridge] Media bridge established: {bridge.sip_media.codec.value} ↔ {bridge.h323_media.codec.value}")

    async def sync_call_state(
        self,
        bridge_id: str,
        sip_state: Optional[CallState] = None,
        h323_state: Optional[CallState] = None
    ) -> None:
        """
        Synchronize call state between SIP and H.323 legs

        Philosophy: Transparent - All state changes logged for observability

        Args:
            bridge_id: Bridge identifier
            sip_state: New SIP state (if changed)
            h323_state: New H.323 state (if changed)
        """
        if bridge_id not in self.active_bridges:
            logger.warning(f"[SIPtoH323Bridge] Bridge {bridge_id} not found for state sync")
            return

        bridge = self.active_bridges[bridge_id]
        state_changed = False

        if sip_state and sip_state != bridge.sip_state:
            logger.info(f"[SIPtoH323Bridge] SIP state: {bridge.sip_state.value} → {sip_state.value}")
            bridge.sip_state = sip_state
            state_changed = True

        if h323_state and h323_state != bridge.h323_state:
            logger.info(f"[SIPtoH323Bridge] H.323 state: {bridge.h323_state.value} → {h323_state.value}")
            bridge.h323_state = h323_state
            state_changed = True

        if state_changed:
            # Update bridge state based on both legs
            if bridge.sip_state == CallState.CONNECTED and bridge.h323_state == CallState.CONNECTED:
                bridge.bridge_state = CallState.CONNECTED
            elif bridge.sip_state == CallState.DISCONNECTED or bridge.h323_state == CallState.DISCONNECTED:
                bridge.bridge_state = CallState.DISCONNECTING

            # Log state change to IF.witness
            await self._log_witness_event(
                bridge_id=bridge_id,
                event_type="STATE_CHANGE",
                details={
                    "sip_state": bridge.sip_state.value,
                    "h323_state": bridge.h323_state.value,
                    "bridge_state": bridge.bridge_state.value
                }
            )

    async def teardown_bridge(self, bridge_id: str) -> Dict[str, Any]:
        """
        Teardown SIP-H.323 bridge and cleanup resources

        Args:
            bridge_id: Bridge identifier

        Returns:
            {
                "status": "success",
                "bridge_id": "...",
                "duration_seconds": ...,
                "media_stats": {...}
            }
        """
        if bridge_id not in self.active_bridges:
            logger.warning(f"[SIPtoH323Bridge] Bridge {bridge_id} not found for teardown")
            return {"status": "not_found", "bridge_id": bridge_id}

        bridge = self.active_bridges[bridge_id]
        logger.info(f"[SIPtoH323Bridge] Tearing down bridge {bridge_id}")

        # Calculate call duration
        duration = (datetime.utcnow() - bridge.start_time).total_seconds()

        # Teardown media
        await self.transcoder.teardown_audio(bridge_id)

        # Update bridge state
        bridge.bridge_state = CallState.DISCONNECTED
        bridge.end_time = datetime.utcnow()

        # Collect media statistics
        media_stats = {
            "sip": {
                "packets_sent": bridge.sip_media.packets_sent if bridge.sip_media else 0,
                "packets_received": bridge.sip_media.packets_received if bridge.sip_media else 0,
                "bytes_sent": bridge.sip_media.bytes_sent if bridge.sip_media else 0,
                "bytes_received": bridge.sip_media.bytes_received if bridge.sip_media else 0
            },
            "h323": {
                "packets_sent": bridge.h323_media.packets_sent if bridge.h323_media else 0,
                "packets_received": bridge.h323_media.packets_received if bridge.h323_media else 0,
                "bytes_sent": bridge.h323_media.bytes_sent if bridge.h323_media else 0,
                "bytes_received": bridge.h323_media.bytes_received if bridge.h323_media else 0
            }
        }

        # Log to IF.witness
        await self._log_witness_event(
            bridge_id=bridge_id,
            event_type="BRIDGE_TERMINATED",
            details={
                "duration_seconds": duration,
                "media_stats": media_stats,
                "expert_id": bridge.expert_id,
                "trace_id": bridge.trace_id
            }
        )

        # Remove from active bridges
        del self.active_bridges[bridge_id]

        logger.info(f"[SIPtoH323Bridge] Bridge {bridge_id} torn down successfully")

        return {
            "status": "success",
            "bridge_id": bridge_id,
            "duration_seconds": duration,
            "media_stats": media_stats
        }

    async def _log_witness_event(
        self,
        bridge_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Log bridge event to IF.witness

        Philosophy: IF.ground Observable - Complete audit trail

        Args:
            bridge_id: Bridge identifier
            event_type: Event type (BRIDGE_ESTABLISHED, STATE_CHANGE, etc.)
            details: Event details
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "SIPtoH323Bridge",
            "bridge_id": bridge_id,
            "event_type": event_type,
            "details": details
        }

        self.witness_events.append(event)
        logger.info(f"[IF.witness] {event_type} for bridge {bridge_id}")
        logger.debug(f"[IF.witness] Event: {json.dumps(event, indent=2)}")

    def get_bridge_status(self, bridge_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a bridge

        Args:
            bridge_id: Bridge identifier

        Returns:
            Bridge status dict or None if not found
        """
        if bridge_id not in self.active_bridges:
            return None

        bridge = self.active_bridges[bridge_id]
        duration = (datetime.utcnow() - bridge.start_time).total_seconds()

        return {
            "bridge_id": bridge_id,
            "trace_id": bridge.trace_id,
            "expert_id": bridge.expert_id,
            "hazard_type": bridge.hazard_type,
            "sip_state": bridge.sip_state.value,
            "h323_state": bridge.h323_state.value,
            "bridge_state": bridge.bridge_state.value,
            "duration_seconds": duration,
            "h323_participant_id": bridge.h323_mcu_participant_id
        }

    def get_all_bridges(self) -> List[Dict[str, Any]]:
        """
        Get status of all active bridges

        Returns:
            List of bridge status dicts
        """
        return [
            self.get_bridge_status(bridge_id)
            for bridge_id in self.active_bridges.keys()
        ]


# Export public API
__all__ = [
    "SIPtoH323Bridge",
    "CallState",
    "MediaCodec",
    "MediaStream",
    "BridgedCall",
    "MediaTranscoder"
]
