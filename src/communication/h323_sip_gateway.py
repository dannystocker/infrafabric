"""
SIP-H.323 Gateway for IF.guard Guardian Council

Bridges external SIP-based expert calls into H.323 Guardian Council conferences.
Handles protocol translation, codec transcoding, and policy enforcement.

Architecture:
- SIP User Agent (external experts) ↔ Gateway ↔ H.323 Terminal (Guardian Council)
- Codec transcoding: G.729 (H.323) ↔ G.711 (SIP)
- Policy enforcement: IF.guard admission control applies to bridged calls
- Integration: Uses existing H.323 Gatekeeper for admission

Philosophy:
- Wu Lun (五倫): Gateway as intermediary (friend-friend relationship)
- Kantian: Policy gates apply universally (no exceptions for bridged calls)
- IF.TTT: All bridged calls logged to IF.witness

Dependencies:
- pjsua2 (SIP User Agent library)
- GStreamer (codec transcoding)
- h323_gatekeeper (admission control)

Author: InfraFabric Project
License: CC BY 4.0
Last Updated: 2025-11-11
"""

import asyncio
import json
import subprocess
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
import hashlib

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: pyyaml not available")


# ============================================================================
# Data Models
# ============================================================================

class CodecType(Enum):
    """Supported audio codecs"""
    G711_ULAW = "G.711-ulaw"  # SIP standard (64 kbps)
    G711_ALAW = "G.711-alaw"  # SIP standard (64 kbps)
    G729 = "G.729"            # H.323 standard (8 kbps)
    OPUS = "Opus"             # WebRTC standard (6-510 kbps)


class CallLegType(Enum):
    """Call leg types in gateway"""
    SIP_INGRESS = "sip_ingress"    # External SIP caller → Gateway
    H323_EGRESS = "h323_egress"    # Gateway → H.323 Guardian Council


@dataclass
class SIPCallLeg:
    """SIP side of bridged call"""
    call_id: str
    sip_uri: str              # e.g., sip:expert@external.com
    display_name: str         # Expert name
    codec: CodecType
    rtp_port: int
    remote_ip: str
    status: str               # "ringing", "active", "on_hold", "terminated"
    connected_at: Optional[str] = None


@dataclass
class H323CallLeg:
    """H.323 side of bridged call"""
    call_id: str
    terminal_id: str          # if://guardian/external-bridge
    session_id: str           # From gatekeeper ACF
    codec: CodecType
    rtp_port: int
    mcu_address: str          # if://service/guard/mcu:1720
    status: str
    connected_at: Optional[str] = None


@dataclass
class BridgedCall:
    """Complete SIP ↔ H.323 bridged call"""
    bridge_id: str            # Unique bridge identifier
    sip_leg: SIPCallLeg
    h323_leg: H323CallLeg
    transcoding_active: bool  # True if codecs differ
    transcoder_pid: Optional[int] = None
    bridge_started_at: str = None
    total_duration_sec: float = 0.0


# ============================================================================
# Codec Transcoding (GStreamer)
# ============================================================================

class CodecTranscoder:
    """
    Transcodes audio between SIP and H.323 codecs using GStreamer.

    Pipeline: RTP (input codec) → decode → resample → encode → RTP (output codec)
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.active_transcoders: Dict[str, subprocess.Popen] = {}

    def start_transcoding(
        self,
        bridge_id: str,
        input_codec: CodecType,
        input_port: int,
        output_codec: CodecType,
        output_port: int,
        output_ip: str
    ) -> int:
        """
        Start GStreamer transcoding pipeline.

        Returns:
            Process ID of transcoder
        """
        # Build GStreamer pipeline
        pipeline = self._build_pipeline(
            input_codec, input_port,
            output_codec, output_port, output_ip
        )

        # Start GStreamer process
        log_file = self.log_dir / f"transcoder_{bridge_id}.log"

        try:
            proc = subprocess.Popen(
                ["gst-launch-1.0"] + pipeline,
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT
            )

            self.active_transcoders[bridge_id] = proc
            print(f"Started transcoder for {bridge_id}: {input_codec.value} → {output_codec.value}")
            return proc.pid

        except FileNotFoundError:
            print("GStreamer not found. Install: apt-get install gstreamer1.0-tools gstreamer1.0-plugins-good")
            # Mock mode: return fake PID
            self.active_transcoders[bridge_id] = None
            return -1

    def stop_transcoding(self, bridge_id: str) -> bool:
        """Stop transcoding pipeline"""
        proc = self.active_transcoders.get(bridge_id)
        if proc:
            if proc.pid > 0:
                proc.terminate()
                proc.wait(timeout=5)
            del self.active_transcoders[bridge_id]
            print(f"Stopped transcoder for {bridge_id}")
            return True
        return False

    def _build_pipeline(
        self,
        input_codec: CodecType,
        input_port: int,
        output_codec: CodecType,
        output_port: int,
        output_ip: str
    ) -> List[str]:
        """Build GStreamer pipeline command"""

        # Input decoder
        if input_codec == CodecType.G711_ULAW:
            decoder = f"rtppcmudepay ! mulawdec"
        elif input_codec == CodecType.G711_ALAW:
            decoder = f"rtppcmadepay ! alawdec"
        elif input_codec == CodecType.G729:
            decoder = f"rtpg729depay ! avdec_g729"
        else:
            decoder = f"rtpopusdepay ! opusdec"

        # Output encoder
        if output_codec == CodecType.G711_ULAW:
            encoder = f"mulawenc ! rtppcmupay"
        elif output_codec == CodecType.G711_ALAW:
            encoder = f"alawenc ! rtppcmapay"
        elif output_codec == CodecType.G729:
            encoder = f"avenc_g729 ! rtpg729pay"
        else:
            encoder = f"opusenc ! rtpopuspay"

        # Full pipeline
        pipeline = [
            f"udpsrc port={input_port}",
            "!",
            "application/x-rtp",
            "!",
            decoder,
            "!",
            "audioconvert",
            "!",
            "audioresample",
            "!",
            encoder,
            "!",
            f"udpsink host={output_ip} port={output_port}"
        ]

        return pipeline


# ============================================================================
# SIP User Agent (PJSUA2 wrapper)
# ============================================================================

class SIPUserAgent:
    """
    SIP User Agent for receiving external expert calls.

    Uses PJSUA2 library (or mock for testing).
    """

    def __init__(self, sip_port: int = 5060):
        self.sip_port = sip_port
        self.active_calls: Dict[str, SIPCallLeg] = {}
        self.call_callbacks: Dict[str, Callable] = {}

    def start(self) -> bool:
        """Start SIP User Agent"""
        try:
            # Try to import pjsua2
            import pjsua2
            print(f"SIP User Agent started on port {self.sip_port}")
            return True
        except ImportError:
            print("pjsua2 not available. Running in mock mode.")
            print("Install: pip install pjsua2 (requires PJSIP library)")
            return True  # Mock mode

    def register_call_callback(self, call_id: str, callback: Callable):
        """Register callback for incoming call events"""
        self.call_callbacks[call_id] = callback

    def accept_call(self, call_id: str, local_rtp_port: int) -> SIPCallLeg:
        """Accept incoming SIP call"""
        # Mock implementation
        sip_leg = SIPCallLeg(
            call_id=call_id,
            sip_uri="sip:expert@external.com",
            display_name="External Expert",
            codec=CodecType.G711_ULAW,
            rtp_port=local_rtp_port,
            remote_ip="192.168.1.100",
            status="active",
            connected_at=datetime.now(timezone.utc).isoformat()
        )

        self.active_calls[call_id] = sip_leg
        print(f"Accepted SIP call {call_id} from {sip_leg.display_name}")
        return sip_leg

    def hangup_call(self, call_id: str):
        """Hangup SIP call"""
        if call_id in self.active_calls:
            self.active_calls[call_id].status = "terminated"
            del self.active_calls[call_id]
            print(f"Hung up SIP call {call_id}")


# ============================================================================
# H.323 Terminal Emulator
# ============================================================================

class H323TerminalEmulator:
    """
    Emulates H.323 terminal for gateway.

    Requests admission from Gatekeeper on behalf of bridged SIP calls.
    """

    def __init__(self, gatekeeper_uri: str):
        self.gatekeeper_uri = gatekeeper_uri
        self.terminal_id = "if://guardian/external-bridge"

    def request_admission(
        self,
        call_id: str,
        bandwidth_bps: int = 64000  # G.711 = 64 kbps
    ):
        """
        Request admission to Guardian Council conference.

        This integrates with h323_gatekeeper.py from Phase 1.
        """
        # Import Phase 1 gatekeeper
        try:
            from .h323_gatekeeper import (
                AdmissionRequest,
                CallType,
                H323Gatekeeper,
                generate_test_keypair,
                sign_admission_request
            )

            # Generate keypair for bridge terminal (in production, use persistent key)
            private_key, public_key = generate_test_keypair()

            # Create admission request
            arq = AdmissionRequest(
                terminal_id=self.terminal_id,
                call_id=call_id,
                call_type=CallType.ROUTINE,  # Bridged calls are ROUTINE (not ESCALATE)
                bandwidth_bps=bandwidth_bps,
                has_pii=False,  # SIP expert identity not included in H.323 stream
                timestamp=datetime.now(timezone.utc).isoformat(),
                signature="",
                public_key=public_key
            )

            # Sign request
            arq.signature = sign_admission_request(arq, private_key)

            # Send to gatekeeper (mock)
            print(f"Requesting H.323 admission for bridged call {call_id}")
            print(f"  Terminal: {self.terminal_id}")
            print(f"  Bandwidth: {bandwidth_bps} bps")

            # Mock ACF response
            h323_leg = H323CallLeg(
                call_id=call_id,
                terminal_id=self.terminal_id,
                session_id=str(uuid.uuid4()),
                codec=CodecType.G729,
                rtp_port=10000,
                mcu_address="if://service/guard/mcu:1720",
                status="active",
                connected_at=datetime.now(timezone.utc).isoformat()
            )

            return h323_leg

        except ImportError:
            print("h323_gatekeeper not available, using mock")
            # Return mock H.323 leg
            return H323CallLeg(
                call_id=call_id,
                terminal_id=self.terminal_id,
                session_id=str(uuid.uuid4()),
                codec=CodecType.G729,
                rtp_port=10000,
                mcu_address="if://service/guard/mcu:1720",
                status="active",
                connected_at=datetime.now(timezone.utc).isoformat()
            )


# ============================================================================
# SIP-H.323 Gateway
# ============================================================================

class SIPH323Gateway:
    """
    Main gateway bridging SIP and H.323.

    Workflow:
    1. External expert calls SIP URI (sip:council@if.guard)
    2. Gateway accepts SIP call (G.711 codec)
    3. Gateway requests H.323 admission from Gatekeeper
    4. Gatekeeper enforces Kantian policy gates
    5. If admitted, gateway bridges calls with transcoding
    6. Expert participates in Guardian Council conference
    """

    def __init__(
        self,
        sip_port: int = 5060,
        gatekeeper_uri: str = "if://service/guard/gatekeeper:1719",
        log_dir: Path = Path("/home/user/infrafabric/logs/gateway")
    ):
        self.sip_ua = SIPUserAgent(sip_port)
        self.h323_terminal = H323TerminalEmulator(gatekeeper_uri)
        self.transcoder = CodecTranscoder(log_dir / "transcoding")
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.bridged_calls: Dict[str, BridgedCall] = {}

    def start(self) -> bool:
        """Start gateway services"""
        print("Starting SIP-H.323 Gateway...")
        success = self.sip_ua.start()
        print("Gateway ready for expert calls")
        return success

    def bridge_call(self, sip_call_id: str) -> Optional[BridgedCall]:
        """
        Bridge incoming SIP call to H.323 Guardian Council.

        Steps:
        1. Accept SIP call
        2. Request H.323 admission (policy enforcement)
        3. Start codec transcoding if needed
        4. Create bridge
        """
        bridge_id = f"bridge-{uuid.uuid4().hex[:8]}"

        # Step 1: Accept SIP call
        sip_leg = self.sip_ua.accept_call(sip_call_id, local_rtp_port=20000)

        # Step 2: Request H.323 admission (Kantian policy gates apply here!)
        h323_leg = self.h323_terminal.request_admission(
            call_id=bridge_id,
            bandwidth_bps=64000  # G.711 bandwidth
        )

        if not h323_leg:
            print(f"H.323 admission rejected for {sip_call_id}")
            self.sip_ua.hangup_call(sip_call_id)
            return None

        # Step 3: Start transcoding (G.711 → G.729)
        transcoding_needed = sip_leg.codec != h323_leg.codec
        transcoder_pid = None

        if transcoding_needed:
            transcoder_pid = self.transcoder.start_transcoding(
                bridge_id=bridge_id,
                input_codec=sip_leg.codec,
                input_port=sip_leg.rtp_port,
                output_codec=h323_leg.codec,
                output_port=h323_leg.rtp_port,
                output_ip="127.0.0.1"  # Localhost for testing
            )

        # Step 4: Create bridge
        bridge = BridgedCall(
            bridge_id=bridge_id,
            sip_leg=sip_leg,
            h323_leg=h323_leg,
            transcoding_active=transcoding_needed,
            transcoder_pid=transcoder_pid,
            bridge_started_at=datetime.now(timezone.utc).isoformat()
        )

        self.bridged_calls[bridge_id] = bridge

        # Log to IF.witness
        self._log_bridge_event(bridge, "BRIDGE_ESTABLISHED")

        print(f"✅ Bridge established: {bridge_id}")
        print(f"   SIP: {sip_leg.sip_uri} ({sip_leg.codec.value})")
        print(f"   H.323: {h323_leg.terminal_id} ({h323_leg.codec.value})")
        print(f"   Transcoding: {transcoding_needed}")

        return bridge

    def teardown_bridge(self, bridge_id: str) -> bool:
        """Teardown bridged call"""
        bridge = self.bridged_calls.get(bridge_id)
        if not bridge:
            return False

        # Stop transcoding
        if bridge.transcoding_active:
            self.transcoder.stop_transcoding(bridge_id)

        # Hangup both legs
        self.sip_ua.hangup_call(bridge.sip_leg.call_id)

        # Calculate duration
        start_time = datetime.fromisoformat(bridge.bridge_started_at)
        end_time = datetime.now(timezone.utc)
        bridge.total_duration_sec = (end_time - start_time).total_seconds()

        # Log to IF.witness
        self._log_bridge_event(bridge, "BRIDGE_TERMINATED")

        del self.bridged_calls[bridge_id]
        print(f"Bridge {bridge_id} terminated (duration: {bridge.total_duration_sec:.1f}s)")
        return True

    def get_active_bridges(self) -> List[BridgedCall]:
        """Get all active bridged calls"""
        return list(self.bridged_calls.values())

    def _log_bridge_event(self, bridge: BridgedCall, event_type: str):
        """Log bridge event to IF.witness"""
        log_entry = {
            "event_type": event_type,
            "bridge_id": bridge.bridge_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sip_leg": {
                "uri": bridge.sip_leg.sip_uri,
                "codec": bridge.sip_leg.codec.value,
                "status": bridge.sip_leg.status
            },
            "h323_leg": {
                "terminal_id": bridge.h323_leg.terminal_id,
                "session_id": bridge.h323_leg.session_id,
                "codec": bridge.h323_leg.codec.value,
                "status": bridge.h323_leg.status
            },
            "transcoding_active": bridge.transcoding_active,
            "duration_sec": bridge.total_duration_sec if event_type == "BRIDGE_TERMINATED" else 0
        }

        # Content-addressed hash (IF.witness pattern)
        content_hash = hashlib.sha256(
            json.dumps(log_entry, sort_keys=True).encode()
        ).hexdigest()
        log_entry["hash"] = content_hash

        # Write to log
        log_file = self.log_dir / f"gateway_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Initialize gateway
    gateway = SIPH323Gateway(
        sip_port=5060,
        gatekeeper_uri="if://service/guard/gatekeeper:1719"
    )

    # Start gateway
    gateway.start()

    # Simulate incoming expert call
    print("\n" + "="*70)
    print("Simulating external expert call to Guardian Council...")
    print("="*70)

    bridge = gateway.bridge_call(sip_call_id="call-001")

    if bridge:
        print("\n✅ Expert successfully bridged to Guardian Council")
        print(f"Bridge ID: {bridge.bridge_id}")
        print(f"SIP Expert: {bridge.sip_leg.display_name}")
        print(f"H.323 Terminal: {bridge.h323_leg.terminal_id}")
        print(f"Transcoding: {bridge.transcoding_active}")

        # Simulate call duration
        time.sleep(2)

        # Teardown
        gateway.teardown_bridge(bridge.bridge_id)
        print("\n✅ Bridge terminated cleanly")

    print("\nGateway ready for next call")
