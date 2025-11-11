"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

SIP-WebRTC Bridge (IF.ESCALATE Integration Layer)
--------------------------------------------------
Bridges SIP external expert calls to WebRTC Agent Mesh for real-time collaboration.

Philosophy Grounding:
- Wu Lun (五倫): 朋友 (Friends) - SIP experts and WebRTC agents collaborate as peers
- IF.ground: Observable - All bridge operations logged for audit
- IF.TTT: Traceable (trace_id), Transparent (state sync), Trustworthy (retry logic)

Integration Points:
- Called by: SIPEscalateProxy.handle_escalate()
- Uses: IFAgentWebRTC.createDataChannel(), shareEvidence(), sendIFMessage()
- Logs to: IF.witness

Responsibilities:
1. Map SIP call sessions to WebRTC DataChannels
2. Serialize/deserialize IFMessage over DataChannel
3. Stream evidence files (chunked for large files)
4. Synchronize call state (connecting, active, ended)
5. Handle errors with exponential backoff retry
6. Cleanup resources on failure
"""

import logging
import json
import asyncio
import hashlib
import base64
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import time

# Import Session 2 WebRTC interface
from communication.webrtc_agent_mesh import IFAgentWebRTC, IFMessage

logger = logging.getLogger(__name__)


class BridgeState(Enum):
    """Bridge connection state machine"""
    IDLE = "idle"
    CONNECTING = "connecting"
    ACTIVE = "active"
    DEGRADED = "degraded"  # Partial failure, retrying
    FAILED = "failed"
    CLOSED = "closed"


class ChunkTransferState(Enum):
    """Evidence file chunk transfer state"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BridgeSession:
    """Represents an active SIP-WebRTC bridge session"""
    bridge_id: str
    sip_call_id: str
    webrtc_channel_id: Optional[str]
    peer_id: str  # External expert ID
    trace_id: str
    state: BridgeState
    created_at: str
    last_heartbeat: str
    evidence_files: List[str]
    message_count: int = 0
    error_count: int = 0
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging"""
        return {
            "bridge_id": self.bridge_id,
            "sip_call_id": self.sip_call_id,
            "webrtc_channel_id": self.webrtc_channel_id,
            "peer_id": self.peer_id,
            "trace_id": self.trace_id,
            "state": self.state.value,
            "created_at": self.created_at,
            "last_heartbeat": self.last_heartbeat,
            "evidence_files": self.evidence_files,
            "message_count": self.message_count,
            "error_count": self.error_count,
            "retry_count": self.retry_count
        }


@dataclass
class EvidenceChunk:
    """Chunked evidence file transfer metadata"""
    file_path: str
    chunk_index: int
    total_chunks: int
    chunk_data: str  # Base64 encoded
    checksum: str  # SHA256 of chunk
    transfer_id: str


class SIPtoWebRTCBridge:
    """
    Main bridge class for SIP-WebRTC integration

    Architecture:
    - 1:1 mapping: Each SIP call gets a dedicated WebRTC DataChannel
    - Bidirectional: SIP messages -> WebRTC, WebRTC messages -> SIP
    - Resilient: Auto-retry with exponential backoff
    - Observable: All operations logged to IF.witness

    Usage:
        bridge = SIPtoWebRTCBridge(webrtc_agent)
        session = await bridge.create_session(
            sip_call_id="call-123",
            expert_id="expert-safety@external.advisor",
            trace_id="trace-456"
        )
        await bridge.share_evidence(session.bridge_id, evidence_files)
        await bridge.send_context_update(session.bridge_id, context_data)
    """

    # Configuration constants
    CHUNK_SIZE = 64 * 1024  # 64KB chunks for evidence files
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0  # seconds
    HEARTBEAT_INTERVAL = 30.0  # seconds
    MESSAGE_TIMEOUT = 10.0  # seconds

    def __init__(self, webrtc_agent: IFAgentWebRTC):
        """
        Initialize SIP-WebRTC bridge

        Args:
            webrtc_agent: IFAgentWebRTC instance for DataChannel operations
        """
        self.webrtc_agent = webrtc_agent
        self.active_sessions: Dict[str, BridgeSession] = {}
        self.evidence_transfers: Dict[str, Dict[str, Any]] = {}

        # Heartbeat task for monitoring session health
        self._heartbeat_task: Optional[asyncio.Task] = None

        logger.info("[SIPWebRTCBridge] Initialized with WebRTC agent")

    async def create_session(
        self,
        sip_call_id: str,
        expert_id: str,
        trace_id: str,
        evidence_files: Optional[List[str]] = None
    ) -> BridgeSession:
        """
        Create new SIP-WebRTC bridge session

        Flow:
        1. Generate unique bridge_id
        2. Create WebRTC DataChannel to expert peer
        3. Send initial handshake IFMessage
        4. Track session state
        5. Start heartbeat monitoring

        Args:
            sip_call_id: SIP call identifier
            expert_id: External expert SIP URI
            trace_id: IF trace ID for correlation
            evidence_files: Optional list of evidence file paths

        Returns:
            BridgeSession object

        Raises:
            RuntimeError: If DataChannel creation fails after retries
        """
        bridge_id = self._generate_bridge_id(sip_call_id, trace_id)

        logger.info(
            f"[SIPWebRTCBridge] Creating session: bridge_id={bridge_id}, "
            f"sip_call={sip_call_id}, expert={expert_id}"
        )

        # Initialize session in CONNECTING state
        session = BridgeSession(
            bridge_id=bridge_id,
            sip_call_id=sip_call_id,
            webrtc_channel_id=None,
            peer_id=expert_id,
            trace_id=trace_id,
            state=BridgeState.CONNECTING,
            created_at=datetime.utcnow().isoformat() + "Z",
            last_heartbeat=datetime.utcnow().isoformat() + "Z",
            evidence_files=evidence_files or []
        )

        # Create WebRTC DataChannel with retry logic
        channel_id = await self._create_datachannel_with_retry(
            expert_id,
            f"sip-escalate-{sip_call_id}",
            session
        )

        session.webrtc_channel_id = channel_id
        session.state = BridgeState.ACTIVE
        self.active_sessions[bridge_id] = session

        # Send handshake message
        await self._send_handshake(session)

        # Start heartbeat monitoring if not already running
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        logger.info(
            f"[SIPWebRTCBridge] Session created successfully: {session.to_dict()}"
        )

        return session

    async def share_evidence(
        self,
        bridge_id: str,
        evidence_files: List[str],
        chunk_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Share evidence files via WebRTC DataChannel (chunked transfer)

        Large files are split into chunks to avoid DataChannel buffer overflow.
        Each chunk is sent as a separate IFMessage with transfer metadata.

        Args:
            bridge_id: Bridge session identifier
            evidence_files: List of file paths to share
            chunk_size: Optional chunk size (default: CHUNK_SIZE)

        Returns:
            {
                "transfer_id": "...",
                "files_sent": count,
                "total_chunks": count,
                "status": "completed" | "partial" | "failed"
            }

        Raises:
            ValueError: If bridge_id not found
        """
        if bridge_id not in self.active_sessions:
            raise ValueError(f"Bridge session not found: {bridge_id}")

        session = self.active_sessions[bridge_id]
        chunk_size = chunk_size or self.CHUNK_SIZE

        transfer_id = self._generate_transfer_id(bridge_id, evidence_files)

        logger.info(
            f"[SIPWebRTCBridge] Starting evidence transfer: "
            f"bridge={bridge_id}, files={len(evidence_files)}, "
            f"transfer_id={transfer_id}"
        )

        # Initialize transfer tracking
        self.evidence_transfers[transfer_id] = {
            "bridge_id": bridge_id,
            "files": evidence_files,
            "total_chunks": 0,
            "completed_chunks": 0,
            "failed_chunks": 0,
            "state": ChunkTransferState.IN_PROGRESS,
            "started_at": datetime.utcnow().isoformat() + "Z"
        }

        total_chunks = 0
        completed_files = 0
        failed_files = 0

        # Process each evidence file
        for file_path in evidence_files:
            try:
                chunks_sent = await self._send_file_chunked(
                    session,
                    file_path,
                    transfer_id,
                    chunk_size
                )
                total_chunks += chunks_sent
                completed_files += 1

                logger.info(
                    f"[SIPWebRTCBridge] File sent: {file_path} "
                    f"({chunks_sent} chunks)"
                )

            except Exception as e:
                logger.error(
                    f"[SIPWebRTCBridge] Failed to send file {file_path}: {e}",
                    exc_info=True
                )
                failed_files += 1
                session.error_count += 1

        # Update transfer state
        transfer_status = "completed" if failed_files == 0 else (
            "partial" if completed_files > 0 else "failed"
        )

        self.evidence_transfers[transfer_id]["total_chunks"] = total_chunks
        self.evidence_transfers[transfer_id]["completed_chunks"] = total_chunks - failed_files
        self.evidence_transfers[transfer_id]["state"] = ChunkTransferState.COMPLETED

        # Use IFAgentWebRTC.shareEvidence() for Session 2 integration
        webrtc_result = await self.webrtc_agent.shareEvidence(
            evidence_files=evidence_files,
            peer_ids=[session.peer_id]
        )

        logger.info(
            f"[SIPWebRTCBridge] Evidence transfer complete: "
            f"transfer_id={transfer_id}, status={transfer_status}, "
            f"files={completed_files}/{len(evidence_files)}, "
            f"webrtc_result={webrtc_result}"
        )

        return {
            "transfer_id": transfer_id,
            "files_sent": completed_files,
            "files_failed": failed_files,
            "total_chunks": total_chunks,
            "status": transfer_status,
            "webrtc_result": webrtc_result
        }

    async def send_context_update(
        self,
        bridge_id: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Send real-time context update to expert via DataChannel

        Context updates include:
        - New hazard detections
        - Policy decisions
        - Guardian council votes
        - Real-time chat messages

        Args:
            bridge_id: Bridge session identifier
            context_data: Context update payload

        Returns:
            {"status": "sent", "message_id": "..."}

        Raises:
            ValueError: If bridge_id not found
        """
        if bridge_id not in self.active_sessions:
            raise ValueError(f"Bridge session not found: {bridge_id}")

        session = self.active_sessions[bridge_id]

        # Create IFMessage for context update
        message = IFMessage(
            id=self._generate_message_id(bridge_id),
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=2,  # Real-time update
            source=f"sip-bridge-{bridge_id}",
            destination=session.peer_id,
            trace_id=session.trace_id,
            version="1.0",
            payload={
                "performative": "context_update",
                "bridge_id": bridge_id,
                "sip_call_id": session.sip_call_id,
                "context": context_data
            }
        )

        # Send via WebRTC DataChannel
        result = await self._send_message_with_retry(session, message)

        session.message_count += 1
        session.last_heartbeat = datetime.utcnow().isoformat() + "Z"

        logger.info(
            f"[SIPWebRTCBridge] Context update sent: bridge={bridge_id}, "
            f"message_id={message.id}"
        )

        return result

    async def close_session(
        self,
        bridge_id: str,
        reason: str = "normal_clearance"
    ) -> Dict[str, Any]:
        """
        Close bridge session and cleanup resources

        Flow:
        1. Send termination IFMessage
        2. Close WebRTC DataChannel
        3. Remove from active sessions
        4. Log final statistics

        Args:
            bridge_id: Bridge session identifier
            reason: Closure reason (for logging)

        Returns:
            Session statistics
        """
        if bridge_id not in self.active_sessions:
            logger.warning(
                f"[SIPWebRTCBridge] Close called on non-existent session: {bridge_id}"
            )
            return {"status": "not_found"}

        session = self.active_sessions[bridge_id]

        logger.info(
            f"[SIPWebRTCBridge] Closing session: bridge={bridge_id}, reason={reason}"
        )

        # Send termination message
        try:
            termination_msg = IFMessage(
                id=self._generate_message_id(bridge_id),
                timestamp=datetime.utcnow().isoformat() + "Z",
                level=1,
                source=f"sip-bridge-{bridge_id}",
                destination=session.peer_id,
                trace_id=session.trace_id,
                version="1.0",
                payload={
                    "performative": "session_end",
                    "bridge_id": bridge_id,
                    "sip_call_id": session.sip_call_id,
                    "reason": reason,
                    "statistics": {
                        "messages_sent": session.message_count,
                        "errors": session.error_count,
                        "retries": session.retry_count,
                        "evidence_files": len(session.evidence_files)
                    }
                }
            )

            await self.webrtc_agent.sendIFMessage(termination_msg.to_dict())

        except Exception as e:
            logger.error(
                f"[SIPWebRTCBridge] Failed to send termination message: {e}"
            )

        # Update state and remove from active sessions
        session.state = BridgeState.CLOSED
        stats = session.to_dict()
        del self.active_sessions[bridge_id]

        logger.info(
            f"[SIPWebRTCBridge] Session closed: {stats}"
        )

        return stats

    # Private helper methods

    def _generate_bridge_id(self, sip_call_id: str, trace_id: str) -> str:
        """Generate unique bridge session ID"""
        combined = f"{sip_call_id}-{trace_id}-{time.time()}"
        hash_digest = hashlib.sha256(combined.encode()).hexdigest()[:16]
        return f"bridge-{hash_digest}"

    def _generate_transfer_id(self, bridge_id: str, files: List[str]) -> str:
        """Generate unique evidence transfer ID"""
        combined = f"{bridge_id}-{'-'.join(files)}-{time.time()}"
        hash_digest = hashlib.sha256(combined.encode()).hexdigest()[:16]
        return f"transfer-{hash_digest}"

    def _generate_message_id(self, bridge_id: str) -> str:
        """Generate unique message ID"""
        return f"msg-{bridge_id}-{int(time.time() * 1000)}"

    async def _create_datachannel_with_retry(
        self,
        peer_id: str,
        label: str,
        session: BridgeSession
    ) -> str:
        """Create DataChannel with exponential backoff retry"""
        for attempt in range(self.MAX_RETRIES):
            try:
                channel_id = await self.webrtc_agent.createDataChannel(peer_id, label)
                logger.info(
                    f"[SIPWebRTCBridge] DataChannel created: {channel_id} "
                    f"(attempt {attempt + 1})"
                )
                return channel_id

            except Exception as e:
                session.retry_count += 1
                session.error_count += 1

                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        f"[SIPWebRTCBridge] DataChannel creation failed "
                        f"(attempt {attempt + 1}): {e}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"[SIPWebRTCBridge] DataChannel creation failed after "
                        f"{self.MAX_RETRIES} attempts: {e}"
                    )
                    session.state = BridgeState.FAILED
                    raise RuntimeError(
                        f"Failed to create DataChannel after {self.MAX_RETRIES} attempts"
                    )

    async def _send_handshake(self, session: BridgeSession) -> None:
        """Send initial handshake message to establish bridge"""
        handshake_msg = IFMessage(
            id=self._generate_message_id(session.bridge_id),
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=1,
            source=f"sip-bridge-{session.bridge_id}",
            destination=session.peer_id,
            trace_id=session.trace_id,
            version="1.0",
            payload={
                "performative": "handshake",
                "bridge_id": session.bridge_id,
                "sip_call_id": session.sip_call_id,
                "capabilities": ["evidence_sharing", "context_updates", "real_time_sync"]
            }
        )

        await self._send_message_with_retry(session, handshake_msg)
        session.message_count += 1

    async def _send_message_with_retry(
        self,
        session: BridgeSession,
        message: IFMessage
    ) -> Dict[str, str]:
        """Send IFMessage with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await self.webrtc_agent.sendIFMessage(message.to_dict())
                return result

            except Exception as e:
                session.retry_count += 1
                session.error_count += 1

                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        f"[SIPWebRTCBridge] Message send failed (attempt {attempt + 1}): "
                        f"{e}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"[SIPWebRTCBridge] Message send failed after "
                        f"{self.MAX_RETRIES} attempts: {e}"
                    )
                    session.state = BridgeState.DEGRADED
                    raise

    async def _send_file_chunked(
        self,
        session: BridgeSession,
        file_path: str,
        transfer_id: str,
        chunk_size: int
    ) -> int:
        """
        Send file in chunks via DataChannel

        Returns:
            Number of chunks sent
        """
        # Mock implementation - In production, this would read actual file
        # For now, simulate chunked transfer

        mock_file_size = 256 * 1024  # 256KB mock file
        total_chunks = (mock_file_size + chunk_size - 1) // chunk_size

        logger.info(
            f"[SIPWebRTCBridge] Sending file {file_path} in {total_chunks} chunks"
        )

        for chunk_index in range(total_chunks):
            # Mock chunk data (in production, read from actual file)
            mock_chunk_data = f"chunk-{chunk_index}-data".encode()
            chunk_b64 = base64.b64encode(mock_chunk_data).decode()
            chunk_checksum = hashlib.sha256(mock_chunk_data).hexdigest()

            chunk_msg = IFMessage(
                id=self._generate_message_id(session.bridge_id),
                timestamp=datetime.utcnow().isoformat() + "Z",
                level=3,  # Data transfer
                source=f"sip-bridge-{session.bridge_id}",
                destination=session.peer_id,
                trace_id=session.trace_id,
                version="1.0",
                payload={
                    "performative": "evidence_chunk",
                    "transfer_id": transfer_id,
                    "file_path": file_path,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                    "chunk_data": chunk_b64,
                    "checksum": chunk_checksum
                }
            )

            await self._send_message_with_retry(session, chunk_msg)
            session.message_count += 1

        return total_chunks

    async def _heartbeat_loop(self) -> None:
        """Background task to monitor session health"""
        logger.info("[SIPWebRTCBridge] Heartbeat monitoring started")

        while True:
            try:
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)

                # Check all active sessions
                for bridge_id, session in list(self.active_sessions.items()):
                    if session.state == BridgeState.ACTIVE:
                        # Update heartbeat timestamp
                        session.last_heartbeat = datetime.utcnow().isoformat() + "Z"

                        logger.debug(
                            f"[SIPWebRTCBridge] Heartbeat: bridge={bridge_id}, "
                            f"messages={session.message_count}, errors={session.error_count}"
                        )

            except Exception as e:
                logger.error(f"[SIPWebRTCBridge] Heartbeat error: {e}", exc_info=True)


# Export public API
__all__ = [
    "SIPtoWebRTCBridge",
    "BridgeSession",
    "BridgeState",
    "ChunkTransferState",
    "EvidenceChunk"
]
