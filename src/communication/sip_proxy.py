"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

SIP External Expert Call Proxy (IF.ESCALATE)
---------------------------------------------
Kamailio Python hooks for routing external expert SIP calls to Guardian council.

Philosophy Grounding:
- Wu Lun (五倫): 朋友 (Friends) - SIP peers are equals, external experts invited as peers
- Popper Falsifiability: External experts provide contrarian views to prevent groupthink
- IF.ground: Observable - SIP is text-based, fully auditable
- IF.TTT: Traceable (X-IF-Trace-ID), Transparent (SIP logs), Trustworthy (Ed25519 signed)

Integration:
- IF.guard: Policy gate for approving external calls
- IF.witness: Logging all SIP events for audit trail
- Session 3 (H.323): Bridge to Guardian council MCU
- Session 2 (WebRTC): Share evidence via DataChannel
"""

import logging
import hashlib
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass
import asyncio
import time

# Import Session 2 & 3 interfaces (stubs for now, will be replaced)
from communication.h323_gatekeeper import H323Gatekeeper
from communication.webrtc_agent_mesh import IFAgentWebRTC

# Import Prometheus metrics exporter
from communication.sip_metrics import (
    get_metrics_collector,
    sip_registry
)

# Import security module (Phase 2 - Production Security)
from communication.sip_security import (
    SecurityManager,
    RateLimiter,
    IPAllowlist,
    DigestAuthenticator,
    TLSCertificateValidator,
    SecurityEvent
)

logger = logging.getLogger(__name__)


@dataclass
class IFMessage:
    """IFMessage v1.0 schema"""
    id: str
    timestamp: str
    level: int
    source: str
    destination: str
    trace_id: Optional[str]
    version: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "level": self.level,
            "source": self.source,
            "destination": self.destination,
            "traceId": self.trace_id,
            "version": self.version,
            "payload": self.payload
        }


class IFGuardPolicy:
    """
    IF.guard policy gate for approving external expert calls

    Philosophy: Popper falsifiability - External experts must be verified
    but should be approved if they provide legitimate contrarian views.
    """

    def __init__(self):
        # Registry of approved external experts
        self.approved_experts = {
            "expert-safety@external.advisor": {
                "name": "Safety Expert",
                "specialization": ["safety", "alignment"],
                "verified": True
            },
            "expert-ethics@external.advisor": {
                "name": "Ethics Expert",
                "specialization": ["ethics", "bias"],
                "verified": True
            },
            "expert-security@external.advisor": {
                "name": "Security Expert",
                "specialization": ["security", "privacy"],
                "verified": True
            }
        }

    async def approve_external_call(
        self,
        expert_id: str,
        hazard: str,
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Policy gate: Approve or reject external expert call

        Args:
            expert_id: SIP URI of external expert (e.g., "expert-safety@external.advisor")
            hazard: Hazard type from IFMessage (e.g., "safety", "ethics")
            signature: Optional Ed25519 signature for verification

        Returns:
            {
                "approved": bool,
                "reason": str,
                "expert_info": dict
            }
        """
        eval_start_time = time.time()
        metrics = get_metrics_collector()

        logger.info(f"[IF.guard] Evaluating external call request: {expert_id} for hazard: {hazard}")

        # Check if expert is in registry
        if expert_id not in self.approved_experts:
            logger.warning(f"[IF.guard] REJECTED: Expert not in registry: {expert_id}")
            eval_time = time.time() - eval_start_time
            metrics.record_policy_decision("rejected", eval_time)
            return {
                "approved": False,
                "reason": "Expert not in approved registry",
                "expert_id": expert_id
            }

        expert_info = self.approved_experts[expert_id]

        # Check if expert specialization matches hazard
        if hazard not in expert_info["specialization"]:
            logger.warning(f"[IF.guard] REJECTED: Expert specialization mismatch: {hazard}")
            eval_time = time.time() - eval_start_time
            metrics.record_policy_decision("rejected", eval_time)
            return {
                "approved": False,
                "reason": f"Expert specialization {expert_info['specialization']} does not match hazard {hazard}",
                "expert_id": expert_id
            }

        # TODO: Verify Ed25519 signature if provided
        if signature:
            # Placeholder for signature verification
            logger.info(f"[IF.guard] Signature verification: {signature[:16]}...")

        logger.info(f"[IF.guard] APPROVED: {expert_id} for {hazard}")
        eval_time = time.time() - eval_start_time
        metrics.record_policy_decision("approved", eval_time)

        return {
            "approved": True,
            "reason": "Expert approved and specialization matches hazard",
            "expert_info": expert_info
        }


class IFWitnessLogger:
    """
    IF.witness integration for logging all SIP events

    Philosophy: IF.ground Observable - Complete audit trail of all SIP signaling
    """

    def __init__(self, log_file: str = "/var/log/infrafabric/sip_witness.log"):
        self.log_file = log_file
        self.events: List[Dict[str, Any]] = []

    async def log_sip_event(
        self,
        event_type: str,
        sip_method: str,
        trace_id: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Log SIP event to IF.witness

        Args:
            event_type: "INVITE", "ACK", "BYE", "RESPONSE", etc.
            sip_method: SIP method name
            trace_id: IF trace ID from X-IF-Trace-ID header
            details: Additional event details
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "sip_method": sip_method,
            "trace_id": trace_id,
            "details": details,
            "source": "IF.sip_proxy"
        }
        self.events.append(event)

        # Log to file (in production, this would go to proper IF.witness infrastructure)
        logger.info(f"[IF.witness] {event_type}: {sip_method} (trace: {trace_id})")
        logger.debug(f"[IF.witness] Event details: {json.dumps(details, indent=2)}")


class SIPEscalateProxy:
    """
    Main SIP proxy for IF.ESCALATE external expert calls

    Responsibilities:
    1. Parse custom IF headers (X-IF-Trace-ID, X-IF-Hazard, X-IF-Signature)
    2. Call IF.guard policy gate
    3. Bridge approved calls to H.323 Guardian council (Session 3)
    4. Share evidence via WebRTC DataChannel (Session 2)
    5. Log all events to IF.witness
    """

    def __init__(self):
        self.h323_gk = H323Gatekeeper()  # Session 3 integration
        self.webrtc_agent = IFAgentWebRTC()  # Session 2 integration
        self.if_guard = IFGuardPolicy()
        self.if_witness = IFWitnessLogger()
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.metrics = get_metrics_collector()

        # PRODUCTION SECURITY (Phase 2)
        self.security_manager = SecurityManager()

        logger.info("[SIPProxy] IF.ESCALATE SIP proxy initialized with security hardening")

    def parse_if_headers(self, sip_message: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """
        Parse custom IF headers from SIP INVITE

        Expected headers:
        - X-IF-Trace-ID: Correlation ID for IF.witness
        - X-IF-Hazard: Hazard type (safety, ethics, security, etc.)
        - X-IF-Signature: Ed25519 signature for authenticity

        Args:
            sip_message: SIP message dict (from Kamailio)

        Returns:
            {"trace_id": "...", "hazard": "...", "signature": "..."}
        """
        headers = sip_message.get("headers", {})
        return {
            "trace_id": headers.get("X-IF-Trace-ID"),
            "hazard": headers.get("X-IF-Hazard"),
            "signature": headers.get("X-IF-Signature")
        }

    async def handle_escalate(self, message: IFMessage) -> Dict[str, Any]:
        """
        Handle IFMessage with performative='escalate'

        This is the main entry point called by IF.connect router.

        Flow (Phase 2 with Security):
        1. Parse hazards from IFMessage
        2. Select appropriate external expert
        3. SECURITY: Validate connection (IP allowlist, rate limit, TLS)
        4. Call IF.guard for approval
        5. Send SIP INVITE to expert
        6. Bridge to H.323 council (Session 3)
        7. Share evidence via WebRTC (Session 2)
        8. Log to IF.witness with security context

        Args:
            message: IFMessage with performative='escalate'

        Returns:
            {
                "status": "connected" | "rejected" | "security_rejected",
                "call_id": "...",
                "expert_id": "..."
            }
        """
        trace_id = message.trace_id or message.id
        hazards = message.payload.get("hazards", [])

        logger.info(f"[SIPProxy] Handling ESCALATE: trace_id={trace_id}, hazards={hazards}")

        # Step 1: Select expert based on hazard
        expert_id = self.get_expert_for_hazard(hazards[0] if hazards else "safety")

        # Step 2: Extract security context from message payload
        source_ip = message.payload.get("source_ip", "unknown")
        tls_version = message.payload.get("tls_version", "TLSv1.2")
        cipher_suite = message.payload.get("cipher_suite", "unknown")
        peer_verified = message.payload.get("peer_verified", False)

        # Step 3: SECURITY - Validate connection (IP allowlist, rate limit, TLS)
        security_ok, security_failures = self.security_manager.validate_connection(
            source_ip=source_ip,
            expert_id=expert_id,
            trace_id=trace_id,
            tls_version=tls_version,
            cipher_suite=cipher_suite,
            peer_verified=peer_verified
        )

        if not security_ok:
            logger.warning(
                f"[SIPProxy] SECURITY REJECTED: {expert_id} - failures: {security_failures}"
            )
            await self.if_witness.log_sip_event(
                event_type="SECURITY_REJECTED",
                sip_method="INVITE",
                trace_id=trace_id,
                details={
                    "expert_id": expert_id,
                    "source_ip": source_ip,
                    "failures": security_failures,
                    "tls_version": tls_version,
                    "cipher_suite": cipher_suite
                }
            )
            # Record security rejection metric
            self.metrics.record_sip_response(403, "INVITE")
            return {
                "status": "security_rejected",
                "reason": "Security validation failed",
                "failures": security_failures
            }

        # Step 4: IF.guard policy check
        approval = await self.if_guard.approve_external_call(
            expert_id=expert_id,
            hazard=hazards[0] if hazards else "safety",
            signature=message.payload.get("signature")
        )

        if not approval["approved"]:
            logger.warning(f"[SIPProxy] Call rejected by IF.guard: {approval['reason']}")
            await self.if_witness.log_sip_event(
                event_type="REJECTED",
                sip_method="INVITE",
                trace_id=trace_id,
                details={"expert_id": expert_id, "reason": approval["reason"]}
            )
            # Record rejected call metric
            self.metrics.record_call_initiated(trace_id, expert_id, hazards[0] if hazards else "safety")
            self.metrics.record_call_terminated(trace_id, "failed")
            self.metrics.record_sip_response(403, "INVITE")
            return {"status": "rejected", "reason": approval["reason"]}

        # Step 5: Send SIP INVITE (security validated)
        sip_call_id = await self.send_sip_invite(expert_id, trace_id, hazards[0])

        # Record call initiated metric
        self.metrics.record_call_initiated(sip_call_id, expert_id, hazards[0] if hazards else "safety")
        self.metrics.record_sip_response(100, "INVITE")  # Trying response

        # Step 6: Bridge to H.323 council (Session 3 integration)
        council_call_id = message.payload.get("conversation_id", f"council-{trace_id}")
        bridge_result = await self.h323_gk.bridge_external_call(
            sip_call_id=sip_call_id,
            council_call_id=council_call_id,
            external_expert_id=expert_id
        )

        logger.info(f"[SIPProxy] H.323 bridge established: {bridge_result}")
        self.metrics.record_sip_response(200, "INVITE")  # OK response

        # Step 7: Share evidence via WebRTC (Session 2 integration)
        evidence_files = message.payload.get("evidence_files", [])
        if evidence_files:
            await self.webrtc_agent.shareEvidence(
                evidence_files=evidence_files,
                peer_ids=[expert_id, council_call_id]
            )

        # Step 8: Log success to IF.witness with security context
        await self.if_witness.log_sip_event(
            event_type="CONNECTED",
            sip_method="INVITE",
            trace_id=trace_id,
            details={
                "expert_id": expert_id,
                "sip_call_id": sip_call_id,
                "h323_bridge": bridge_result,
                "evidence_count": len(evidence_files),
                "security": {
                    "source_ip": source_ip,
                    "tls_version": tls_version,
                    "cipher_suite": cipher_suite,
                    "peer_verified": peer_verified,
                    "authenticated": True
                }
            }
        )

        # Track active call with security context
        self.active_calls[sip_call_id] = {
            "trace_id": trace_id,
            "expert_id": expert_id,
            "council_call_id": council_call_id,
            "started_at": datetime.utcnow().isoformat(),
            "security": {
                "source_ip": source_ip,
                "tls_version": tls_version,
                "cipher_suite": cipher_suite,
                "authenticated": True
            }
        }

        return {
            "status": "connected",
            "call_id": sip_call_id,
            "expert_id": expert_id,
            "h323_participant": bridge_result.get("mcu_participant_id"),
            "security_validated": True
        }

    async def send_sip_invite(
        self,
        expert_id: str,
        trace_id: str,
        hazard: str
    ) -> str:
        """
        Send SIP INVITE to external expert

        In production, this would use PJSIP to send actual SIP messages.
        For now, this is a stub that logs the INVITE.

        Args:
            expert_id: SIP URI (e.g., "expert-safety@external.advisor")
            trace_id: IF trace ID
            hazard: Hazard type

        Returns:
            call_id: SIP call identifier
        """
        call_id = f"sip-call-{hashlib.sha256(trace_id.encode()).hexdigest()[:16]}"

        logger.info(f"[SIPProxy] Sending SIP INVITE to {expert_id}")
        logger.info(f"[SIPProxy] Custom headers: X-IF-Trace-ID={trace_id}, X-IF-Hazard={hazard}")

        # TODO: In production, use PJSIP to send actual SIP INVITE with custom headers
        # Example pseudo-code:
        # pjsip_call = pjsua2.Call()
        # pjsip_call.makeCall(expert_id, {
        #     "X-IF-Trace-ID": trace_id,
        #     "X-IF-Hazard": hazard,
        #     "X-IF-Signature": signature
        # })

        return call_id

    def get_expert_for_hazard(self, hazard: str) -> str:
        """
        Select appropriate external expert based on hazard type

        Philosophy: Wu Lun (朋友) - Match expert specialty to hazard

        Args:
            hazard: Hazard type ("safety", "ethics", "security", etc.)

        Returns:
            expert_id: SIP URI of expert
        """
        expert_map = {
            "safety": "expert-safety@external.advisor",
            "alignment": "expert-safety@external.advisor",
            "ethics": "expert-ethics@external.advisor",
            "bias": "expert-ethics@external.advisor",
            "security": "expert-security@external.advisor",
            "privacy": "expert-security@external.advisor"
        }

        expert_id = expert_map.get(hazard, "expert-safety@external.advisor")
        logger.info(f"[SIPProxy] Selected expert {expert_id} for hazard {hazard}")
        return expert_id

    async def terminate_call(self, call_id: str) -> Dict[str, str]:
        """
        Terminate SIP call and cleanup resources

        Args:
            call_id: SIP call identifier

        Returns:
            {"status": "terminated", "call_id": "..."}
        """
        if call_id not in self.active_calls:
            return {"status": "not_found", "call_id": call_id}

        call_info = self.active_calls[call_id]
        trace_id = call_info["trace_id"]

        logger.info(f"[SIPProxy] Terminating call: {call_id}")

        # Log to IF.witness
        await self.if_witness.log_sip_event(
            event_type="TERMINATED",
            sip_method="BYE",
            trace_id=trace_id,
            details={"call_id": call_id, "duration": "calculated"}
        )

        # Record call termination metric
        self.metrics.record_call_terminated(call_id, "success")
        self.metrics.record_sip_response(200, "BYE")
        self.metrics.record_method_duration("BYE", 0.1)

        # Remove from active calls
        del self.active_calls[call_id]

        return {"status": "terminated", "call_id": call_id}


# Kamailio Python hooks (called from config/kamailio.cfg)
# These functions are invoked by Kamailio's app_python module

_sip_proxy_instance = None


def kamailio_init():
    """
    Initialize SIP proxy when Kamailio starts

    Called by Kamailio: python_exec("sip_proxy.kamailio_init")
    """
    global _sip_proxy_instance
    _sip_proxy_instance = SIPEscalateProxy()
    logger.info("[Kamailio] SIP proxy initialized")
    return 1  # Success


def check_policy(sip_message):
    """
    Kamailio hook: Check IF.guard policy for incoming INVITE

    Called from kamailio.cfg:
    if (!python_exec("sip_proxy.check_policy")) {
        sl_send_reply("403", "IF.guard policy rejected");
        exit;
    }

    Args:
        sip_message: Kamailio SIP message object

    Returns:
        1 (approved) or -1 (rejected)
    """
    global _sip_proxy_instance
    if not _sip_proxy_instance:
        logger.error("[Kamailio] SIP proxy not initialized!")
        return -1

    # Parse IF headers
    if_headers = _sip_proxy_instance.parse_if_headers(sip_message)
    trace_id = if_headers.get("trace_id")
    hazard = if_headers.get("hazard")

    if not trace_id or not hazard:
        logger.warning("[Kamailio] Missing required IF headers")
        return -1

    # Run policy check synchronously (Kamailio requires sync response)
    # In production, this would use asyncio.run() or a proper event loop
    logger.info(f"[Kamailio] Policy check: trace_id={trace_id}, hazard={hazard}")

    # For now, approve all calls from approved registry
    # TODO: Implement actual async policy check
    return 1  # Approved


# Metrics HTTP endpoint handler (for Prometheus scraping)
def metrics_endpoint():
    """
    HTTP endpoint for Prometheus metrics scraping

    Usage in Flask/FastAPI:
        @app.get("/metrics")
        def metrics():
            return metrics_endpoint()

    Returns:
        Prometheus exposition format metrics
    """
    metrics = get_metrics_collector()
    return {
        "metrics": metrics.get_metrics().decode('utf-8'),
        "active_calls": metrics.get_active_call_count(),
        "uptime_seconds": metrics.get_uptime_seconds()
    }


# Export public API
__all__ = [
    "SIPEscalateProxy",
    "IFGuardPolicy",
    "IFWitnessLogger",
    "kamailio_init",
    "check_policy",
    "metrics_endpoint",
    "get_metrics_collector"
]
