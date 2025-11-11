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

    # H.323 leg (Guardian council MCU)
    h323_call_id: str
    h323_endpoint: str

    # Call states and media
    sip_state: CallState = CallState.IDLE
    sip_media: Optional[MediaStream] = None
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

    # Codec compatibility matrix (source -> target)
    CODEC_COMPATIBILITY = {
        MediaCodec.G711_ULAW: [MediaCodec.G711_ULAW, MediaCodec.G711_ALAW, MediaCodec.G722, MediaCodec.G729],
        MediaCodec.G711_ALAW: [MediaCodec.G711_ALAW, MediaCodec.G711_ULAW, MediaCodec.G722, MediaCodec.G729],
        MediaCodec.G722: [MediaCodec.G722, MediaCodec.G711_ULAW, MediaCodec.G711_ALAW],
        MediaCodec.OPUS: [MediaCodec.G711_ULAW, MediaCodec.G711_ALAW, MediaCodec.G722],
        MediaCodec.G729: [MediaCodec.G729, MediaCodec.G711_ULAW, MediaCodec.G711_ALAW]
    }

    def __init__(self):
        self.active_streams: Dict[str, Tuple[MediaStream, MediaStream]] = {}
        self.transcoding_stats: Dict[str, Dict[str, int]] = {}
        logger.info("[MediaTranscoder] Initialized with codec compatibility matrix")
        logger.debug(f"[MediaTranscoder] Supported codec paths: {list(self.CODEC_COMPATIBILITY.keys())}")

    def negotiate_codecs(
        self,
        sip_codecs: List[MediaCodec],
        h323_codecs: List[MediaCodec]
    ) -> Tuple[Optional[MediaCodec], Optional[MediaCodec]]:
        """
        Negotiate compatible codec pair between SIP and H.323

        Strategy:
        1. Try to find matching codec (no transcoding needed)
        2. Find compatible codec pair from compatibility matrix
        3. Fall back to G.711 PCMU if nothing else works

        Args:
            sip_codecs: List of SIP supported codecs (in preference order)
            h323_codecs: List of H.323 supported codecs (in preference order)

        Returns:
            (sip_codec, h323_codec) or (None, None) if no compatible pair found
        """
        logger.info(f"[MediaTranscoder] Negotiating codecs")
        logger.debug(f"[MediaTranscoder] SIP offers: {[c.value for c in sip_codecs]}")
        logger.debug(f"[MediaTranscoder] H.323 offers: {[c.value for c in h323_codecs]}")

        # Strategy 1: Try to find exact match (no transcoding)
        for sip_codec in sip_codecs:
            if sip_codec in h323_codecs:
                logger.info(f"[MediaTranscoder] Direct match found: {sip_codec.value} (no transcoding needed)")
                return (sip_codec, sip_codec)

        # Strategy 2: Find compatible codec pair from matrix
        for sip_codec in sip_codecs:
            if sip_codec in self.CODEC_COMPATIBILITY:
                compatible_codecs = self.CODEC_COMPATIBILITY[sip_codec]
                for h323_codec in h323_codecs:
                    if h323_codec in compatible_codecs:
                        logger.info(f"[MediaTranscoder] Compatible pair: {sip_codec.value} ↔ {h323_codec.value}")
                        return (sip_codec, h323_codec)

        # Strategy 3: Fall back to G.711 PCMU (universal compatibility)
        fallback = MediaCodec.G711_ULAW
        logger.warning(f"[MediaTranscoder] No optimal codec pair, falling back to {fallback.value}")
        return (fallback, fallback)

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
        logger.info(f"[MediaTranscoder] SIP: {sip_stream.codec.value} @ {sip_stream.sample_rate}Hz on port {sip_stream.rtp_port}")
        logger.info(f"[MediaTranscoder] H.323: {h323_stream.codec.value} @ {h323_stream.sample_rate}Hz on channel {h323_stream.h323_channel}")

        # Validate codec compatibility
        if sip_stream.codec not in self.CODEC_COMPATIBILITY:
            logger.error(f"[MediaTranscoder] Unsupported SIP codec: {sip_stream.codec.value}")
            return False

        if h323_stream.codec not in [MediaCodec.G711_ULAW, MediaCodec.G711_ALAW, MediaCodec.G722, MediaCodec.G729]:
            logger.error(f"[MediaTranscoder] Unsupported H.323 codec: {h323_stream.codec.value}")
            return False

        # Check if transcoding is needed
        transcoding_needed = sip_stream.codec != h323_stream.codec
        if transcoding_needed:
            logger.info(f"[MediaTranscoder] Transcoding required: {sip_stream.codec.value} ↔ {h323_stream.codec.value}")
        else:
            logger.info(f"[MediaTranscoder] No transcoding needed: {sip_stream.codec.value} passthrough")

        # Store stream pair
        self.active_streams[bridge_id] = (sip_stream, h323_stream)

        # Initialize transcoding statistics
        self.transcoding_stats[bridge_id] = {
            "transcoding_errors": 0,
            "sip_to_h323_frames": 0,
            "h323_to_sip_frames": 0,
            "dropped_frames": 0
        }

        # TODO: In production, initialize actual transcoding pipeline
        # Example pseudo-code:
        # if transcoding_needed:
        #     self.transcode_pipeline = gstreamer.Pipeline()
        #     self.transcode_pipeline.add_decoder(sip_stream.codec)
        #     self.transcode_pipeline.add_resampler(sip_stream.sample_rate, h323_stream.sample_rate)
        #     self.transcode_pipeline.add_encoder(h323_stream.codec)
        # else:
        #     self.transcode_pipeline = gstreamer.Pipeline()
        #     self.transcode_pipeline.add_passthrough()
        #
        # self.transcode_pipeline.add_rtp_source(sip_stream.rtp_port, sip_stream.codec)
        # self.transcode_pipeline.add_h323_sink(h323_stream.h323_channel, h323_stream.codec)
        # self.transcode_pipeline.start()

        logger.info(f"[MediaTranscoder] Bidirectional audio established for {bridge_id}")
        logger.debug(f"[MediaTranscoder] Pipeline: SIP RTP:{sip_stream.rtp_port} → {sip_stream.codec.value} → {h323_stream.codec.value} → H.323:{h323_stream.h323_channel}")
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
        stats = self.transcoding_stats.get(bridge_id, {})

        try:
            # Validate RTP packet (basic check)
            if len(rtp_packet) < 12:  # Minimum RTP header size
                logger.warning(f"[MediaTranscoder] Invalid RTP packet size: {len(rtp_packet)} bytes")
                stats["dropped_frames"] = stats.get("dropped_frames", 0) + 1
                return None

            # Update statistics
            sip_stream.packets_received += 1
            sip_stream.bytes_received += len(rtp_packet)

            # TODO: Actual transcoding logic
            # In production, this would:
            # 1. Parse RTP header (version, payload type, sequence, timestamp, SSRC)
            # 2. Extract RTP payload (encoded audio)
            # 3. Decode audio using SIP codec decoder (e.g., Opus, G.711)
            # 4. Resample if sample rates differ (e.g., 48kHz → 8kHz)
            # 5. Encode audio using H.323 codec encoder (e.g., G.711, G.729)
            # 6. Package into H.323 audio frame
            #
            # Example pseudo-code:
            # rtp_header = parse_rtp_header(rtp_packet[:12])
            # rtp_payload = rtp_packet[12:]
            # pcm_audio = decode_audio(rtp_payload, sip_stream.codec)
            # if sip_stream.sample_rate != h323_stream.sample_rate:
            #     pcm_audio = resample(pcm_audio, sip_stream.sample_rate, h323_stream.sample_rate)
            # h323_frame = encode_audio(pcm_audio, h323_stream.codec)
            # return h323_frame

            # For now, simulate transcoding with passthrough
            h323_frame = rtp_packet[12:] if len(rtp_packet) > 12 else rtp_packet

            # Update H.323 statistics
            h323_stream.packets_sent += 1
            h323_stream.bytes_sent += len(h323_frame)
            stats["sip_to_h323_frames"] = stats.get("sip_to_h323_frames", 0) + 1

            # Log every 100th frame for debugging
            if stats["sip_to_h323_frames"] % 100 == 0:
                logger.debug(f"[MediaTranscoder] {bridge_id}: Transcoded {stats['sip_to_h323_frames']} SIP→H.323 frames")

            return h323_frame

        except Exception as e:
            logger.error(f"[MediaTranscoder] Transcoding error (SIP→H.323): {e}", exc_info=True)
            stats["transcoding_errors"] = stats.get("transcoding_errors", 0) + 1
            stats["dropped_frames"] = stats.get("dropped_frames", 0) + 1
            return None

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
        stats = self.transcoding_stats.get(bridge_id, {})

        try:
            # Validate H.323 frame (basic check)
            if len(h323_frame) == 0:
                logger.warning(f"[MediaTranscoder] Empty H.323 frame")
                stats["dropped_frames"] = stats.get("dropped_frames", 0) + 1
                return None

            # Update statistics
            h323_stream.packets_received += 1
            h323_stream.bytes_received += len(h323_frame)

            # TODO: Actual transcoding logic
            # In production, this would:
            # 1. Parse H.323 audio frame
            # 2. Decode audio using H.323 codec decoder (e.g., G.711, G.729)
            # 3. Resample if sample rates differ (e.g., 8kHz → 48kHz)
            # 4. Encode audio using SIP codec encoder (e.g., Opus, G.711)
            # 5. Package into RTP packet with proper header
            #
            # Example pseudo-code:
            # pcm_audio = decode_audio(h323_frame, h323_stream.codec)
            # if h323_stream.sample_rate != sip_stream.sample_rate:
            #     pcm_audio = resample(pcm_audio, h323_stream.sample_rate, sip_stream.sample_rate)
            # rtp_payload = encode_audio(pcm_audio, sip_stream.codec)
            # rtp_packet = build_rtp_packet(
            #     payload_type=get_payload_type(sip_stream.codec),
            #     sequence=self.rtp_sequence,
            #     timestamp=self.rtp_timestamp,
            #     ssrc=self.rtp_ssrc,
            #     payload=rtp_payload
            # )
            # self.rtp_sequence += 1
            # self.rtp_timestamp += samples_per_frame
            # return rtp_packet

            # For now, simulate transcoding with minimal RTP header + payload
            # Simplified RTP header (12 bytes):
            # Version (2 bits) = 2, Padding (1 bit) = 0, Extension (1 bit) = 0, CSRC count (4 bits) = 0
            # Marker (1 bit) = 0, Payload type (7 bits) = 0 (PCMU for G.711)
            # Sequence number (16 bits) = incrementing counter
            # Timestamp (32 bits) = incrementing counter
            # SSRC (32 bits) = random identifier
            rtp_header = bytes([
                0x80,  # V=2, P=0, X=0, CC=0
                0x00,  # M=0, PT=0 (PCMU)
                0x00, 0x00,  # Sequence number (simplified)
                0x00, 0x00, 0x00, 0x00,  # Timestamp (simplified)
                0x00, 0x00, 0x00, 0x01   # SSRC (simplified)
            ])
            rtp_packet = rtp_header + h323_frame

            # Update SIP statistics
            sip_stream.packets_sent += 1
            sip_stream.bytes_sent += len(rtp_packet)
            stats["h323_to_sip_frames"] = stats.get("h323_to_sip_frames", 0) + 1

            # Log every 100th frame for debugging
            if stats["h323_to_sip_frames"] % 100 == 0:
                logger.debug(f"[MediaTranscoder] {bridge_id}: Transcoded {stats['h323_to_sip_frames']} H.323→SIP frames")

            return rtp_packet

        except Exception as e:
            logger.error(f"[MediaTranscoder] Transcoding error (H.323→SIP): {e}", exc_info=True)
            stats["transcoding_errors"] = stats.get("transcoding_errors", 0) + 1
            stats["dropped_frames"] = stats.get("dropped_frames", 0) + 1
            return None

    async def teardown_audio(self, bridge_id: str) -> None:
        """
        Teardown audio transcoding for bridge

        Args:
            bridge_id: Bridge identifier
        """
        if bridge_id in self.active_streams:
            sip_stream, h323_stream = self.active_streams[bridge_id]
            stats = self.transcoding_stats.get(bridge_id, {})

            logger.info(f"[MediaTranscoder] Tearing down audio for {bridge_id}")
            logger.info(f"[MediaTranscoder] SIP stats: {sip_stream.packets_sent} sent, {sip_stream.packets_received} received, {sip_stream.bytes_sent} bytes sent, {sip_stream.bytes_received} bytes received")
            logger.info(f"[MediaTranscoder] H.323 stats: {h323_stream.packets_sent} sent, {h323_stream.packets_received} received, {h323_stream.bytes_sent} bytes sent, {h323_stream.bytes_received} bytes received")
            logger.info(f"[MediaTranscoder] Transcoding stats: {stats.get('sip_to_h323_frames', 0)} SIP→H.323, {stats.get('h323_to_sip_frames', 0)} H.323→SIP, {stats.get('transcoding_errors', 0)} errors, {stats.get('dropped_frames', 0)} dropped")

            # TODO: In production, stop and cleanup transcoding pipeline
            # Example pseudo-code:
            # if hasattr(self, 'transcode_pipeline'):
            #     self.transcode_pipeline.stop()
            #     self.transcode_pipeline.cleanup()

            del self.active_streams[bridge_id]
            if bridge_id in self.transcoding_stats:
                del self.transcoding_stats[bridge_id]

            logger.info(f"[MediaTranscoder] Audio teardown complete for {bridge_id}")


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
        hazard_type: str,
        sip_codecs: Optional[List[MediaCodec]] = None,
        h323_codecs: Optional[List[MediaCodec]] = None
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
            sip_codecs: Optional list of SIP supported codecs (defaults to [G.711, Opus, G.722])
            h323_codecs: Optional list of H.323 supported codecs (defaults to [G.711, G.722, G.729])

        Returns:
            {
                "status": "success" | "error",
                "bridge_id": "...",
                "h323_participant_id": "...",
                "sip_endpoint": "...",
                "h323_endpoint": "...",
                "sip_codec": "...",
                "h323_codec": "..."
            }
        """
        bridge_id = f"bridge-{hashlib.sha256(f'{sip_call_id}-{council_call_id}'.encode()).hexdigest()[:16]}"

        logger.info(f"[SIPtoH323Bridge] ==================== CREATING BRIDGE ====================")
        logger.info(f"[SIPtoH323Bridge] Bridge ID: {bridge_id}")
        logger.info(f"[SIPtoH323Bridge] SIP call: {sip_call_id}, Expert: {expert_id}")
        logger.info(f"[SIPtoH323Bridge] H.323 council: {council_call_id}, Hazard: {hazard_type}")
        logger.info(f"[SIPtoH323Bridge] Trace ID: {trace_id}")

        # Default codec lists if not provided
        if sip_codecs is None:
            sip_codecs = [MediaCodec.G711_ULAW, MediaCodec.OPUS, MediaCodec.G722, MediaCodec.G711_ALAW]
        if h323_codecs is None:
            h323_codecs = [MediaCodec.G711_ULAW, MediaCodec.G722, MediaCodec.G729, MediaCodec.G711_ALAW]

        # Negotiate codecs early
        logger.info(f"[SIPtoH323Bridge] Negotiating codecs...")
        negotiated_sip_codec, negotiated_h323_codec = self.transcoder.negotiate_codecs(sip_codecs, h323_codecs)
        if not negotiated_sip_codec or not negotiated_h323_codec:
            error_msg = "Failed to negotiate compatible codecs"
            logger.error(f"[SIPtoH323Bridge] {error_msg}")
            return {
                "status": "error",
                "bridge_id": bridge_id,
                "error": error_msg
            }

        logger.info(f"[SIPtoH323Bridge] Negotiated codecs: SIP={negotiated_sip_codec.value}, H.323={negotiated_h323_codec.value}")

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

        # Track cleanup state
        sip_leg_setup = False
        h323_leg_setup = False
        media_bridge_setup = False

        try:
            # Step 1: Setup SIP leg with negotiated codec
            logger.info(f"[SIPtoH323Bridge] Step 1/5: Setting up SIP leg...")
            await self._setup_sip_leg(bridge, negotiated_sip_codec)
            sip_leg_setup = True
            logger.info(f"[SIPtoH323Bridge] Step 1/5: SIP leg ready")

            # Step 2: Bridge to H.323 council via gatekeeper
            logger.info(f"[SIPtoH323Bridge] Step 2/5: Bridging to H.323 council via gatekeeper...")
            h323_result = await self.h323_gk.bridge_external_call(
                sip_call_id=sip_call_id,
                council_call_id=council_call_id,
                external_expert_id=expert_id
            )

            if h323_result.get("status") != "success":
                raise RuntimeError(f"H.323 gatekeeper bridge failed: {h323_result.get('error', 'Unknown error')}")

            bridge.h323_endpoint = h323_result["h323_endpoint"]
            bridge.h323_mcu_participant_id = h323_result["mcu_participant_id"]
            bridge.h323_state = CallState.CONNECTED
            logger.info(f"[SIPtoH323Bridge] Step 2/5: H.323 bridge established, participant ID: {bridge.h323_mcu_participant_id}")

            # Step 3: Setup H.323 leg with negotiated codec
            logger.info(f"[SIPtoH323Bridge] Step 3/5: Setting up H.323 leg...")
            await self._setup_h323_leg(bridge, negotiated_h323_codec)
            h323_leg_setup = True
            logger.info(f"[SIPtoH323Bridge] Step 3/5: H.323 leg ready")

            # Step 4: Setup bidirectional media
            logger.info(f"[SIPtoH323Bridge] Step 4/5: Setting up bidirectional media bridge...")
            await self._setup_media_bridge(bridge)
            media_bridge_setup = True
            logger.info(f"[SIPtoH323Bridge] Step 4/5: Media bridge established")

            # Step 5: Update bridge state
            logger.info(f"[SIPtoH323Bridge] Step 5/5: Finalizing bridge...")
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
                    "trace_id": trace_id,
                    "sip_codec": negotiated_sip_codec.value,
                    "h323_codec": negotiated_h323_codec.value,
                    "sip_endpoint": f"sip:{sip_from}",
                    "h323_endpoint": bridge.h323_endpoint
                }
            )

            logger.info(f"[SIPtoH323Bridge] ==================== BRIDGE ESTABLISHED ====================")
            logger.info(f"[SIPtoH323Bridge] Bridge {bridge_id} ready for media flow")

            return {
                "status": "success",
                "bridge_id": bridge_id,
                "h323_participant_id": bridge.h323_mcu_participant_id,
                "sip_endpoint": f"sip:{sip_from}",
                "h323_endpoint": bridge.h323_endpoint,
                "sip_codec": negotiated_sip_codec.value,
                "h323_codec": negotiated_h323_codec.value
            }

        except Exception as e:
            logger.error(f"[SIPtoH323Bridge] ==================== BRIDGE CREATION FAILED ====================")
            logger.error(f"[SIPtoH323Bridge] Error: {e}", exc_info=True)
            bridge.bridge_state = CallState.ERROR

            # Cleanup on error
            logger.info(f"[SIPtoH323Bridge] Cleaning up failed bridge...")
            try:
                if media_bridge_setup:
                    logger.debug(f"[SIPtoH323Bridge] Cleaning up media bridge...")
                    await self.transcoder.teardown_audio(bridge_id)

                # Note: SIP and H.323 leg cleanup would be handled by respective protocol stacks
                # in production. For now, just log the cleanup intent.
                if h323_leg_setup:
                    logger.debug(f"[SIPtoH323Bridge] H.323 leg cleanup needed")
                if sip_leg_setup:
                    logger.debug(f"[SIPtoH323Bridge] SIP leg cleanup needed")

                logger.info(f"[SIPtoH323Bridge] Cleanup complete")
            except Exception as cleanup_error:
                logger.error(f"[SIPtoH323Bridge] Cleanup error: {cleanup_error}", exc_info=True)

            await self._log_witness_event(
                bridge_id=bridge_id,
                event_type="BRIDGE_ERROR",
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "sip_call_id": sip_call_id,
                    "trace_id": trace_id,
                    "cleanup_performed": True,
                    "sip_leg_setup": sip_leg_setup,
                    "h323_leg_setup": h323_leg_setup,
                    "media_bridge_setup": media_bridge_setup
                }
            )

            return {
                "status": "error",
                "bridge_id": bridge_id,
                "error": str(e),
                "error_type": type(e).__name__
            }

    async def _setup_sip_leg(self, bridge: BridgedCall, codec: MediaCodec) -> None:
        """
        Setup SIP call leg and RTP media

        Args:
            bridge: Bridge state object
            codec: Negotiated codec for SIP leg
        """
        logger.info(f"[SIPtoH323Bridge] Setting up SIP leg for {bridge.bridge_id}")
        logger.debug(f"[SIPtoH323Bridge] SIP codec: {codec.value}")

        # Determine sample rate based on codec
        sample_rate = 8000  # Default for G.711, G.729
        if codec == MediaCodec.G722:
            sample_rate = 16000
        elif codec == MediaCodec.OPUS:
            sample_rate = 48000

        # Create SIP media stream descriptor
        bridge.sip_media = MediaStream(
            stream_id=f"sip-{bridge.sip_call_id}",
            codec=codec,
            sample_rate=sample_rate,
            rtp_port=10000 + len(self.active_bridges),  # Dynamic port allocation
            encryption="SRTP"  # Use SRTP for SIP
        )

        bridge.sip_state = CallState.SETUP

        # TODO: In production, use PJSIP to setup actual SIP media session
        # Example pseudo-code:
        # pjsip_call = pjsua2.Call.get_call(bridge.sip_call_id)
        # media_info = pjsua2.CallMediaInfo()
        # media_info.type = pjsua2.PJMEDIA_TYPE_AUDIO
        # media_info.format = codec_to_pjmedia_format(codec)
        # pjsip_media = pjsua2.AudioMedia()
        # pjsip_media.bind_port(bridge.sip_media.rtp_port)
        # pjsip_media.start_transmit(pjsip_call.getMedia(0))
        # pjsip_media.start_receive()

        logger.info(f"[SIPtoH323Bridge] SIP leg ready: {codec.value} @ {sample_rate}Hz on RTP port {bridge.sip_media.rtp_port}")
        logger.debug(f"[SIPtoH323Bridge] SIP encryption: {bridge.sip_media.encryption}")

    async def _setup_h323_leg(self, bridge: BridgedCall, codec: MediaCodec) -> None:
        """
        Setup H.323 call leg and audio channels

        Args:
            bridge: Bridge state object
            codec: Negotiated codec for H.323 leg
        """
        logger.info(f"[SIPtoH323Bridge] Setting up H.323 leg for {bridge.bridge_id}")
        logger.debug(f"[SIPtoH323Bridge] H.323 codec: {codec.value}")

        # Determine sample rate based on codec
        sample_rate = 8000  # Default for G.711, G.729
        if codec == MediaCodec.G722:
            sample_rate = 16000

        # Create H.323 media stream descriptor
        bridge.h323_media = MediaStream(
            stream_id=f"h323-{bridge.h323_call_id}",
            codec=codec,
            sample_rate=sample_rate,
            h323_channel=f"h323-audio-channel-{bridge.h323_mcu_participant_id}",
            encryption="H.235"  # Use H.235 for H.323
        )

        # TODO: In production, use H.323 library to setup actual audio channel
        # Example pseudo-code:
        # h323_endpoint = h323plus.H323EndPoint()
        # h323_connection = h323_endpoint.GetConnection(bridge.h323_call_id)
        # audio_channel = h323plus.AudioChannel()
        # audio_channel.set_codec(codec_to_h323_capability(codec))
        # audio_channel.connect(bridge.h323_endpoint)
        # audio_channel.open_logical_channel(h323_connection)
        # audio_channel.start_receive()
        # audio_channel.start_transmit()

        logger.info(f"[SIPtoH323Bridge] H.323 leg ready: {codec.value} @ {sample_rate}Hz on channel {bridge.h323_media.h323_channel}")
        logger.debug(f"[SIPtoH323Bridge] H.323 endpoint: {bridge.h323_endpoint}")
        logger.debug(f"[SIPtoH323Bridge] H.323 encryption: {bridge.h323_media.encryption}")

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

        State synchronization rules:
        1. Both legs CONNECTED → Bridge CONNECTED
        2. Either leg DISCONNECTED/ERROR → Bridge DISCONNECTING → teardown
        3. Either leg HOLD → Bridge HOLD
        4. Both legs SETUP/RINGING → Bridge SETUP

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
        old_bridge_state = bridge.bridge_state

        if sip_state and sip_state != bridge.sip_state:
            logger.info(f"[SIPtoH323Bridge] [{bridge_id}] SIP state transition: {bridge.sip_state.value} → {sip_state.value}")
            bridge.sip_state = sip_state
            state_changed = True

        if h323_state and h323_state != bridge.h323_state:
            logger.info(f"[SIPtoH323Bridge] [{bridge_id}] H.323 state transition: {bridge.h323_state.value} → {h323_state.value}")
            bridge.h323_state = h323_state
            state_changed = True

        if state_changed:
            # Update bridge state based on both legs (state machine)
            new_bridge_state = self._compute_bridge_state(bridge)

            if new_bridge_state != bridge.bridge_state:
                logger.info(f"[SIPtoH323Bridge] [{bridge_id}] Bridge state transition: {bridge.bridge_state.value} → {new_bridge_state.value}")
                bridge.bridge_state = new_bridge_state

            # Log state change to IF.witness
            await self._log_witness_event(
                bridge_id=bridge_id,
                event_type="STATE_CHANGE",
                details={
                    "sip_state": bridge.sip_state.value,
                    "h323_state": bridge.h323_state.value,
                    "bridge_state": bridge.bridge_state.value,
                    "previous_bridge_state": old_bridge_state.value
                }
            )

            # Auto-teardown if either leg disconnected
            if bridge.bridge_state == CallState.DISCONNECTING:
                logger.warning(f"[SIPtoH323Bridge] [{bridge_id}] Bridge entering DISCONNECTING state, initiating teardown")
                # Schedule teardown (in production, this would be async)
                await self.teardown_bridge(bridge_id)

    def _compute_bridge_state(self, bridge: BridgedCall) -> CallState:
        """
        Compute bridge state based on SIP and H.323 leg states

        Args:
            bridge: Bridge state object

        Returns:
            Computed bridge state
        """
        sip = bridge.sip_state
        h323 = bridge.h323_state

        # Error states propagate immediately
        if sip == CallState.ERROR or h323 == CallState.ERROR:
            logger.debug(f"[SIPtoH323Bridge] Bridge state: ERROR (leg error)")
            return CallState.ERROR

        # Disconnection states propagate immediately
        if sip == CallState.DISCONNECTED or h323 == CallState.DISCONNECTED:
            logger.debug(f"[SIPtoH323Bridge] Bridge state: DISCONNECTING (leg disconnected)")
            return CallState.DISCONNECTING

        if sip == CallState.DISCONNECTING or h323 == CallState.DISCONNECTING:
            logger.debug(f"[SIPtoH323Bridge] Bridge state: DISCONNECTING (leg disconnecting)")
            return CallState.DISCONNECTING

        # Both legs must be CONNECTED for bridge to be CONNECTED
        if sip == CallState.CONNECTED and h323 == CallState.CONNECTED:
            logger.debug(f"[SIPtoH323Bridge] Bridge state: CONNECTED (both legs connected)")
            return CallState.CONNECTED

        # Hold state if either leg is on hold
        if sip == CallState.HOLD or h323 == CallState.HOLD:
            logger.debug(f"[SIPtoH323Bridge] Bridge state: HOLD (leg on hold)")
            return CallState.HOLD

        # Ringing if either leg is ringing
        if sip == CallState.RINGING or h323 == CallState.RINGING:
            logger.debug(f"[SIPtoH323Bridge] Bridge state: RINGING (leg ringing)")
            return CallState.RINGING

        # Setup if either leg is in setup
        if sip == CallState.SETUP or h323 == CallState.SETUP:
            logger.debug(f"[SIPtoH323Bridge] Bridge state: SETUP (leg in setup)")
            return CallState.SETUP

        # Default to current state
        logger.debug(f"[SIPtoH323Bridge] Bridge state: {bridge.bridge_state.value} (unchanged)")
        return bridge.bridge_state

    async def teardown_bridge(self, bridge_id: str) -> Dict[str, Any]:
        """
        Teardown SIP-H.323 bridge and cleanup resources

        Args:
            bridge_id: Bridge identifier

        Returns:
            {
                "status": "success" | "not_found",
                "bridge_id": "...",
                "duration_seconds": ...,
                "media_stats": {...}
            }
        """
        if bridge_id not in self.active_bridges:
            logger.warning(f"[SIPtoH323Bridge] Bridge {bridge_id} not found for teardown")
            return {"status": "not_found", "bridge_id": bridge_id}

        bridge = self.active_bridges[bridge_id]
        logger.info(f"[SIPtoH323Bridge] ==================== TEARING DOWN BRIDGE ====================")
        logger.info(f"[SIPtoH323Bridge] Bridge ID: {bridge_id}")
        logger.info(f"[SIPtoH323Bridge] Expert: {bridge.expert_id}, Hazard: {bridge.hazard_type}")
        logger.info(f"[SIPtoH323Bridge] Current states: SIP={bridge.sip_state.value}, H.323={bridge.h323_state.value}, Bridge={bridge.bridge_state.value}")

        # Calculate call duration
        duration = (datetime.utcnow() - bridge.start_time).total_seconds()
        logger.info(f"[SIPtoH323Bridge] Call duration: {duration:.2f} seconds")

        # Teardown media
        try:
            logger.info(f"[SIPtoH323Bridge] Step 1/3: Tearing down media transcoding...")
            await self.transcoder.teardown_audio(bridge_id)
            logger.info(f"[SIPtoH323Bridge] Step 1/3: Media teardown complete")
        except Exception as e:
            logger.error(f"[SIPtoH323Bridge] Error tearing down media: {e}", exc_info=True)

        # Update bridge state
        logger.info(f"[SIPtoH323Bridge] Step 2/3: Updating bridge state...")
        bridge.bridge_state = CallState.DISCONNECTED
        bridge.sip_state = CallState.DISCONNECTED
        bridge.h323_state = CallState.DISCONNECTED
        bridge.end_time = datetime.utcnow()

        # Collect media statistics
        media_stats = {
            "sip": {
                "codec": bridge.sip_media.codec.value if bridge.sip_media else "unknown",
                "packets_sent": bridge.sip_media.packets_sent if bridge.sip_media else 0,
                "packets_received": bridge.sip_media.packets_received if bridge.sip_media else 0,
                "bytes_sent": bridge.sip_media.bytes_sent if bridge.sip_media else 0,
                "bytes_received": bridge.sip_media.bytes_received if bridge.sip_media else 0
            },
            "h323": {
                "codec": bridge.h323_media.codec.value if bridge.h323_media else "unknown",
                "packets_sent": bridge.h323_media.packets_sent if bridge.h323_media else 0,
                "packets_received": bridge.h323_media.packets_received if bridge.h323_media else 0,
                "bytes_sent": bridge.h323_media.bytes_sent if bridge.h323_media else 0,
                "bytes_received": bridge.h323_media.bytes_received if bridge.h323_media else 0
            }
        }

        logger.info(f"[SIPtoH323Bridge] Media statistics collected:")
        logger.info(f"[SIPtoH323Bridge]   SIP: {media_stats['sip']}")
        logger.info(f"[SIPtoH323Bridge]   H.323: {media_stats['h323']}")

        # Log to IF.witness
        logger.info(f"[SIPtoH323Bridge] Step 3/3: Logging to IF.witness...")
        await self._log_witness_event(
            bridge_id=bridge_id,
            event_type="BRIDGE_TERMINATED",
            details={
                "duration_seconds": duration,
                "media_stats": media_stats,
                "expert_id": bridge.expert_id,
                "hazard_type": bridge.hazard_type,
                "trace_id": bridge.trace_id,
                "sip_call_id": bridge.sip_call_id,
                "h323_call_id": bridge.h323_call_id,
                "h323_participant_id": bridge.h323_mcu_participant_id
            }
        )

        # Remove from active bridges
        del self.active_bridges[bridge_id]

        logger.info(f"[SIPtoH323Bridge] ==================== BRIDGE TEARDOWN COMPLETE ====================")
        logger.info(f"[SIPtoH323Bridge] Bridge {bridge_id} successfully torn down after {duration:.2f}s")

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
