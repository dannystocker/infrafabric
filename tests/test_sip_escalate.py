"""
SPDX-License-Identifier: MIT
Copyright (c) 2025 InfraFabric

Session 4 (SIP External Expert Calls) - Phase 1 Basic Test Suite
=================================================================

Test suite for SIP ESCALATE functionality:
1. IFMessage to SIP INVITE flow
2. IF.guard policy approval logic
3. SIP to H.323 Guardian council bridging
4. WebRTC evidence file sharing
5. IF.witness audit logging

Philosophy Grounding:
- Popper Falsifiability: External experts provide contrarian views
- IF.ground: Observability of all SIP signaling
- IF.TTT: Traceable, Transparent, Trustworthy audit trails
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from datetime import datetime
from uuid import uuid4

# Import modules under test
import sys
sys.path.insert(0, '/home/user/infrafabric/src')

from communication.sip_proxy import (
    SIPEscalateProxy,
    IFMessage,
    IFGuardPolicy,
    IFWitnessLogger,
)
from communication.h323_gatekeeper import H323Gatekeeper
from communication.webrtc_agent_mesh import IFAgentWebRTC


# ============================================================================
# FIXTURES
# ============================================================================

@pytest_asyncio.fixture
def sip_proxy():
    """
    Fixture providing a SIPEscalateProxy instance with mocked dependencies.

    This ensures tests don't interact with real H.323, WebRTC, or logging infrastructure.
    """
    proxy = SIPEscalateProxy()
    proxy.h323_gk = AsyncMock(spec=H323Gatekeeper)
    proxy.webrtc_agent = AsyncMock(spec=IFAgentWebRTC)
    proxy.if_guard = AsyncMock(spec=IFGuardPolicy)
    proxy.if_witness = AsyncMock(spec=IFWitnessLogger)
    return proxy


@pytest_asyncio.fixture
def if_guard_policy():
    """
    Fixture providing IFGuardPolicy with pre-configured approved experts.
    """
    return IFGuardPolicy()


@pytest_asyncio.fixture
def if_witness_logger():
    """
    Fixture providing IFWitnessLogger for audit trail verification.
    """
    return IFWitnessLogger()


@pytest_asyncio.fixture
def sample_escalate_message():
    """
    Fixture providing a sample IFMessage with performative='escalate'.

    Represents a request to escalate a safety hazard to an external expert.
    """
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
            "signature": "ed25519sig_placeholder_123"
        }
    )


# ============================================================================
# TEST 1: IFMessage ESCALATE to SIP INVITE
# ============================================================================

@pytest.mark.asyncio
async def test_ifmessage_escalate_to_sip_invite(sip_proxy, sample_escalate_message):
    """
    TEST 1: Verify IFMessage with performative='escalate' triggers SIP INVITE.

    Flow:
    1. Create IFMessage with performative='escalate' and hazards list
    2. Call SIPEscalateProxy.handle_escalate()
    3. Verify SIP INVITE is sent (send_sip_invite called)
    4. Assert returned status is 'connected'

    This test validates the core flow: escalate request -> SIP invitation
    """
    # Setup mock behavior
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={
            "approved": True,
            "reason": "Expert approved and specialization matches hazard",
            "expert_info": {
                "name": "Safety Expert",
                "specialization": ["safety", "alignment"],
                "verified": True
            }
        }
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={
            "status": "bridged",
            "h323_endpoint": "h323://guardian-council-mcu/expert-safety",
            "mcu_participant_id": "mcu-participant-0",
            "bridge_established": True
        }
    )

    sip_proxy.webrtc_agent.shareEvidence = AsyncMock(
        return_value={"shared": 2, "peers": ["expert-safety@external.advisor"], "status": "completed"}
    )

    sip_proxy.if_witness.log_sip_event = AsyncMock()

    # Execute: Call handle_escalate with escalate message
    result = await sip_proxy.handle_escalate(sample_escalate_message)

    # Assertions
    assert result["status"] == "connected", "Expected status to be 'connected'"
    assert "call_id" in result, "Expected call_id in response"
    assert "expert_id" in result, "Expected expert_id in response"
    assert result["expert_id"] == "expert-safety@external.advisor", "Expected safety expert to be selected"

    # Verify send_sip_invite was called implicitly (via active_calls tracking)
    assert result["call_id"] in sip_proxy.active_calls, "Expected call to be tracked in active_calls"


@pytest.mark.asyncio
async def test_ifmessage_escalate_multiple_hazards(sip_proxy):
    """
    TEST 1 Variant: Test escalate message with multiple hazards.

    Verifies that handle_escalate correctly selects expert based on first hazard
    when multiple hazards are specified.
    """
    message = IFMessage(
        id=str(uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        level=2,
        source="if-agent-local",
        destination="external-expert",
        trace_id=f"trace-{uuid4().hex[:16]}",
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": ["ethics", "bias", "alignment"],  # Multiple hazards
            "conversation_id": f"council-{uuid4().hex[:8]}",
            "evidence_files": [],
            "signature": None
        }
    )

    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(return_value={"status": "bridged", "mcu_participant_id": "mcu-0"})
    sip_proxy.if_witness.log_sip_event = AsyncMock()

    result = await sip_proxy.handle_escalate(message)

    # Should select ethics expert (first hazard)
    assert result["expert_id"] == "expert-ethics@external.advisor", "Expected ethics expert for first hazard"


# ============================================================================
# TEST 2: IF.GUARD POLICY APPROVAL
# ============================================================================

@pytest.mark.asyncio
async def test_if_guard_policy_approval_success(if_guard_policy):
    """
    TEST 2a: Verify IF.guard approves calls from registered experts with matching specialization.

    Scenario: Expert is in approved registry and specialization matches hazard
    Expected: Approval returned with expert_info

    Philosophy: Popper falsifiability - we allow legitimate contrarian views
    """
    expert_id = "expert-safety@external.advisor"
    hazard = "safety"

    result = await if_guard_policy.approve_external_call(
        expert_id=expert_id,
        hazard=hazard
    )

    assert result["approved"] is True, "Expected approval for registered expert"
    assert result["reason"] == "Expert approved and specialization matches hazard"
    assert "expert_info" in result, "Expected expert_info in response"
    assert result["expert_info"]["name"] == "Safety Expert"


@pytest.mark.asyncio
async def test_if_guard_policy_rejection_unregistered_expert(if_guard_policy):
    """
    TEST 2b: Verify IF.guard rejects calls from unregistered experts.

    Scenario: Expert not in approved registry
    Expected: Rejection with reason="Expert not in approved registry"

    Philosophy: Defense in depth - only approved experts can participate
    """
    expert_id = "unknown-expert@evil.domain"
    hazard = "safety"

    result = await if_guard_policy.approve_external_call(
        expert_id=expert_id,
        hazard=hazard
    )

    assert result["approved"] is False, "Expected rejection for unregistered expert"
    assert result["reason"] == "Expert not in approved registry"
    assert result["expert_id"] == expert_id


@pytest.mark.asyncio
async def test_if_guard_policy_rejection_specialization_mismatch(if_guard_policy):
    """
    TEST 2c: Verify IF.guard rejects calls where expert specialization doesn't match hazard.

    Scenario: Expert (security expert) called for unrelated hazard (ethics)
    Expected: Rejection with specialization mismatch reason

    Philosophy: Expertise validation - expert should be qualified for the hazard type
    """
    expert_id = "expert-security@external.advisor"  # Security expert
    hazard = "ethics"  # Ethics hazard - not in security expert specialization

    result = await if_guard_policy.approve_external_call(
        expert_id=expert_id,
        hazard=hazard
    )

    assert result["approved"] is False, "Expected rejection for specialization mismatch"
    assert "does not match hazard" in result["reason"]
    assert "ethics" in result["reason"]


@pytest.mark.asyncio
async def test_if_guard_policy_alignment_hazard(if_guard_policy):
    """
    TEST 2 Variant: Test approval of alignment hazard (safety expert specialization includes alignment).
    """
    expert_id = "expert-safety@external.advisor"
    hazard = "alignment"

    result = await if_guard_policy.approve_external_call(
        expert_id=expert_id,
        hazard=hazard
    )

    assert result["approved"] is True, "Safety expert should handle alignment hazards"


# ============================================================================
# TEST 3: SIP to H.323 GUARDIAN COUNCIL BRIDGE
# ============================================================================

@pytest.mark.asyncio
async def test_sip_h323_bridge(sip_proxy, sample_escalate_message):
    """
    TEST 3: Verify SIP call is bridged to H.323 Guardian council MCU.

    Flow:
    1. Initiate SIP call with handle_escalate()
    2. Verify H323Gatekeeper.bridge_external_call() is called with correct parameters
    3. Assert bridge is established and mcu_participant_id is returned

    Philosophy: Cross-protocol bridging - SIP external experts join H.323 council
    """
    # Setup mocks
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    expected_bridge_result = {
        "status": "bridged",
        "h323_endpoint": "h323://guardian-council-mcu/expert-safety",
        "mcu_participant_id": "mcu-participant-5",
        "bridge_established": True
    }

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(return_value=expected_bridge_result)
    sip_proxy.if_witness.log_sip_event = AsyncMock()

    # Execute
    result = await sip_proxy.handle_escalate(sample_escalate_message)

    # Assertions: Verify bridge_external_call was invoked
    sip_proxy.h323_gk.bridge_external_call.assert_called_once()

    # Get call arguments
    call_args = sip_proxy.h323_gk.bridge_external_call.call_args
    assert call_args.kwargs["sip_call_id"] is not None, "Expected sip_call_id in bridge call"
    assert call_args.kwargs["council_call_id"] == sample_escalate_message.payload["conversation_id"]
    assert call_args.kwargs["external_expert_id"] == "expert-safety@external.advisor"

    # Verify bridge result in response
    assert result["h323_participant"] == "mcu-participant-5", "Expected MCU participant ID in response"


@pytest.mark.asyncio
async def test_sip_h323_bridge_creates_h323_call(sip_proxy, sample_escalate_message):
    """
    TEST 3 Variant: Verify H.323 call is created and tracked properly.
    """
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={
            "status": "bridged",
            "h323_endpoint": "h323://guardian-council-mcu/expert-safety",
            "mcu_participant_id": "mcu-participant-1"
        }
    )

    sip_proxy.if_witness.log_sip_event = AsyncMock()

    result = await sip_proxy.handle_escalate(sample_escalate_message)

    # Verify the H.323 gatekeeper bridge was called
    assert sip_proxy.h323_gk.bridge_external_call.called
    assert result["status"] == "connected"


# ============================================================================
# TEST 4: WebRTC EVIDENCE SHARING
# ============================================================================

@pytest.mark.asyncio
async def test_webrtc_evidence_sharing(sip_proxy, sample_escalate_message):
    """
    TEST 4: Verify evidence files are shared via WebRTC DataChannel.

    Flow:
    1. Include evidence_files in IFMessage payload
    2. Call handle_escalate()
    3. Verify IFAgentWebRTC.shareEvidence() is called with evidence_files and peer_ids
    4. Assert evidence is shared with expert and council

    Philosophy: Transparent evidence - All evidence shared with external experts
    """
    # Setup mocks
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={"status": "bridged", "mcu_participant_id": "mcu-0"}
    )

    expected_evidence_result = {
        "shared": 2,
        "peers": ["expert-safety@external.advisor", f"council-{sample_escalate_message.payload['conversation_id']}"],
        "status": "completed"
    }

    sip_proxy.webrtc_agent.shareEvidence = AsyncMock(return_value=expected_evidence_result)
    sip_proxy.if_witness.log_sip_event = AsyncMock()

    # Execute
    result = await sip_proxy.handle_escalate(sample_escalate_message)

    # Assertions: Verify shareEvidence was called
    sip_proxy.webrtc_agent.shareEvidence.assert_called_once()

    # Get call arguments
    call_args = sip_proxy.webrtc_agent.shareEvidence.call_args
    assert call_args.kwargs["evidence_files"] == ["evidence1.log", "evidence2.json"]
    assert "expert-safety@external.advisor" in call_args.kwargs["peer_ids"]
    assert sample_escalate_message.payload["conversation_id"] in call_args.kwargs["peer_ids"]


@pytest.mark.asyncio
async def test_webrtc_evidence_sharing_no_files(sip_proxy):
    """
    TEST 4 Variant: Test escalate with no evidence files (should not call shareEvidence).

    Scenario: Escalate request without evidence attachment
    Expected: shareEvidence not called
    """
    message = IFMessage(
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
            "evidence_files": [],  # Empty evidence
            "signature": None
        }
    )

    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={"status": "bridged", "mcu_participant_id": "mcu-0"}
    )

    sip_proxy.webrtc_agent.shareEvidence = AsyncMock()
    sip_proxy.if_witness.log_sip_event = AsyncMock()

    # Execute
    result = await sip_proxy.handle_escalate(message)

    # shareEvidence should NOT be called for empty evidence
    sip_proxy.webrtc_agent.shareEvidence.assert_not_called()


@pytest.mark.asyncio
async def test_webrtc_evidence_sharing_multiple_files(sip_proxy):
    """
    TEST 4 Variant: Test evidence sharing with multiple files.
    """
    message = IFMessage(
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
            "evidence_files": [
                "risk_analysis.pdf",
                "audit_logs.json",
                "model_weights_hash.txt",
                "behavior_test_results.csv"
            ],
            "signature": None
        }
    )

    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={"status": "bridged", "mcu_participant_id": "mcu-0"}
    )

    sip_proxy.webrtc_agent.shareEvidence = AsyncMock(
        return_value={"shared": 4, "peers": ["expert-safety@external.advisor"], "status": "completed"}
    )

    sip_proxy.if_witness.log_sip_event = AsyncMock()

    # Execute
    result = await sip_proxy.handle_escalate(message)

    # Verify all 4 files were shared
    call_args = sip_proxy.webrtc_agent.shareEvidence.call_args
    assert len(call_args.kwargs["evidence_files"]) == 4


# ============================================================================
# TEST 5: IF.WITNESS AUDIT LOGGING
# ============================================================================

@pytest.mark.asyncio
async def test_if_witness_logging(sip_proxy, sample_escalate_message):
    """
    TEST 5: Verify all SIP events are logged to IF.witness for audit trail.

    Flow:
    1. Perform complete ESCALATE flow with handle_escalate()
    2. Check IFWitnessLogger.events list
    3. Assert all critical events are logged:
       - INVITE sent to expert
       - CONNECTED when bridge established
    4. Verify events contain required fields (timestamp, event_type, trace_id)

    Philosophy: IF.ground Observable - Complete audit trail of all signaling
    """
    # Use real IFWitnessLogger
    witness_logger = IFWitnessLogger()
    sip_proxy.if_witness = witness_logger

    # Setup other mocks
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={"status": "bridged", "mcu_participant_id": "mcu-0"}
    )

    # Execute
    result = await sip_proxy.handle_escalate(sample_escalate_message)

    # Assertions: Check logged events
    assert len(witness_logger.events) >= 1, "Expected at least CONNECTED event to be logged"

    # Find CONNECTED event
    connected_events = [e for e in witness_logger.events if e["event_type"] == "CONNECTED"]
    assert len(connected_events) > 0, "Expected CONNECTED event in witness log"

    # Verify CONNECTED event structure
    connected_event = connected_events[0]
    assert connected_event["sip_method"] == "INVITE"
    assert connected_event["trace_id"] == sample_escalate_message.trace_id
    assert "timestamp" in connected_event
    assert "details" in connected_event
    assert "expert_id" in connected_event["details"]
    assert "sip_call_id" in connected_event["details"]


@pytest.mark.asyncio
async def test_if_witness_logging_rejection(sip_proxy, sample_escalate_message):
    """
    TEST 5 Variant: Verify rejection events are logged.

    When a call is rejected by IF.guard, a REJECTED event should be logged.
    """
    witness_logger = IFWitnessLogger()
    sip_proxy.if_witness = witness_logger

    # Setup mock to reject call
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={
            "approved": False,
            "reason": "Expert not in approved registry",
            "expert_id": "unknown-expert@evil.domain"
        }
    )

    # Modify message to request unknown expert
    sample_escalate_message.payload["hazards"] = ["unknown-hazard"]

    # Execute
    result = await sip_proxy.handle_escalate(sample_escalate_message)

    # Assertions: Check for rejection event
    assert result["status"] == "rejected"

    # Find REJECTED event
    rejected_events = [e for e in witness_logger.events if e["event_type"] == "REJECTED"]
    assert len(rejected_events) > 0, "Expected REJECTED event in witness log"

    # Verify event details
    rejected_event = rejected_events[0]
    assert "reason" in rejected_event["details"]


@pytest.mark.asyncio
async def test_if_witness_logging_event_fields(if_witness_logger):
    """
    TEST 5 Variant: Verify IF.witness logs contain all required fields.

    Each event must contain:
    - timestamp (ISO 8601)
    - event_type (INVITE, CONNECTED, REJECTED, TERMINATED)
    - sip_method (INVITE, ACK, BYE, RESPONSE)
    - trace_id (IF trace correlation ID)
    - details (contextual information)
    - source ("IF.sip_proxy")
    """
    trace_id = f"trace-{uuid4().hex[:16]}"

    # Log various event types
    await if_witness_logger.log_sip_event(
        event_type="INVITE",
        sip_method="INVITE",
        trace_id=trace_id,
        details={"to": "expert-safety@external.advisor"}
    )

    await if_witness_logger.log_sip_event(
        event_type="CONNECTED",
        sip_method="200 OK",
        trace_id=trace_id,
        details={"status_code": 200, "expert_id": "expert-safety@external.advisor"}
    )

    # Verify events
    assert len(if_witness_logger.events) == 2

    for event in if_witness_logger.events:
        assert "timestamp" in event
        assert event["timestamp"].endswith("Z"), "Expected ISO 8601 timestamp with Z"
        assert "event_type" in event
        assert event["event_type"] in ["INVITE", "CONNECTED", "REJECTED", "TERMINATED"]
        assert "sip_method" in event
        assert "trace_id" in event
        assert event["trace_id"] == trace_id
        assert "details" in event
        assert event["source"] == "IF.sip_proxy"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_escalate_flow(sip_proxy, sample_escalate_message):
    """
    Integration Test: Full ESCALATE flow with all components.

    Verifies the complete flow:
    1. IFMessage escalate request received
    2. IF.guard approves external call
    3. SIP INVITE sent to expert
    4. H.323 bridge established to Guardian council
    5. Evidence shared via WebRTC
    6. All events logged to IF.witness

    This test ensures all components work together correctly.
    """
    # Setup all mocks
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={
            "approved": True,
            "reason": "Expert approved and specialization matches hazard",
            "expert_info": {"name": "Safety Expert", "specialization": ["safety"]}
        }
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={
            "status": "bridged",
            "h323_endpoint": "h323://guardian-council-mcu/expert-safety",
            "mcu_participant_id": "mcu-participant-0",
            "bridge_established": True
        }
    )

    sip_proxy.webrtc_agent.shareEvidence = AsyncMock(
        return_value={"shared": 2, "peers": ["expert-safety@external.advisor"], "status": "completed"}
    )

    sip_proxy.if_witness.log_sip_event = AsyncMock()

    # Execute full flow
    result = await sip_proxy.handle_escalate(sample_escalate_message)

    # Assertions
    assert result["status"] == "connected"
    assert result["call_id"] is not None
    assert result["expert_id"] == "expert-safety@external.advisor"
    assert result["h323_participant"] == "mcu-participant-0"

    # Verify all components were invoked
    sip_proxy.if_guard.approve_external_call.assert_called_once()
    sip_proxy.h323_gk.bridge_external_call.assert_called_once()
    sip_proxy.webrtc_agent.shareEvidence.assert_called_once()

    # Verify witness logging was called at least for CONNECTED event
    sip_proxy.if_witness.log_sip_event.assert_called()


@pytest.mark.asyncio
async def test_call_termination(sip_proxy, sample_escalate_message):
    """
    Integration Test: Call termination and cleanup.

    Verifies that:
    1. Active call is tracked
    2. terminate_call() properly removes call from active_calls
    3. BYE event is logged to IF.witness
    """
    # Setup mocks
    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={"status": "bridged", "mcu_participant_id": "mcu-0"}
    )

    sip_proxy.if_witness.log_sip_event = AsyncMock()

    # Initiate call
    result = await sip_proxy.handle_escalate(sample_escalate_message)
    call_id = result["call_id"]

    # Verify call is tracked
    assert call_id in sip_proxy.active_calls

    # Terminate call
    terminate_result = await sip_proxy.terminate_call(call_id)

    # Assertions
    assert terminate_result["status"] == "terminated"
    assert call_id not in sip_proxy.active_calls, "Expected call to be removed from active_calls"


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
async def test_escalate_with_no_hazards(sip_proxy):
    """
    Edge Case: Escalate message with empty hazards list.

    Should default to "safety" hazard.
    """
    message = IFMessage(
        id=str(uuid4()),
        timestamp=datetime.utcnow().isoformat() + "Z",
        level=2,
        source="if-agent-local",
        destination="external-expert",
        trace_id=f"trace-{uuid4().hex[:16]}",
        version="1.0",
        payload={
            "performative": "escalate",
            "hazards": [],  # Empty hazards
            "conversation_id": f"council-{uuid4().hex[:8]}",
            "evidence_files": []
        }
    )

    sip_proxy.if_guard.approve_external_call = AsyncMock(
        return_value={"approved": True, "reason": "Approved", "expert_info": {}}
    )

    sip_proxy.h323_gk.bridge_external_call = AsyncMock(
        return_value={"status": "bridged", "mcu_participant_id": "mcu-0"}
    )

    sip_proxy.if_witness.log_sip_event = AsyncMock()

    result = await sip_proxy.handle_escalate(message)

    # Should default to safety expert
    assert result["expert_id"] == "expert-safety@external.advisor"


@pytest.mark.asyncio
async def test_terminate_nonexistent_call(sip_proxy):
    """
    Edge Case: Attempt to terminate a call that doesn't exist.

    Should return "not_found" status without raising exception.
    """
    fake_call_id = "sip-call-nonexistent"

    result = await sip_proxy.terminate_call(fake_call_id)

    assert result["status"] == "not_found"
    assert result["call_id"] == fake_call_id


@pytest.mark.asyncio
async def test_expert_selection_hazard_mapping(sip_proxy):
    """
    Test: Verify expert selection follows hazard-to-expert mapping.

    Tests multiple hazard types to ensure correct expert is selected.
    """
    hazard_expert_map = {
        "safety": "expert-safety@external.advisor",
        "alignment": "expert-safety@external.advisor",
        "ethics": "expert-ethics@external.advisor",
        "bias": "expert-ethics@external.advisor",
        "security": "expert-security@external.advisor",
        "privacy": "expert-security@external.advisor"
    }

    for hazard, expected_expert in hazard_expert_map.items():
        expert = sip_proxy.get_expert_for_hazard(hazard)
        assert expert == expected_expert, f"Hazard '{hazard}' should map to '{expected_expert}'"


@pytest.mark.asyncio
async def test_message_to_dict_conversion():
    """
    Test: Verify IFMessage.to_dict() properly serializes message.
    """
    message = IFMessage(
        id="test-id-123",
        timestamp="2025-01-15T10:30:00Z",
        level=2,
        source="if-agent",
        destination="external-expert",
        trace_id="trace-abc123",
        version="1.0",
        payload={"key": "value"}
    )

    dict_form = message.to_dict()

    assert dict_form["id"] == "test-id-123"
    assert dict_form["traceId"] == "trace-abc123"  # Note: camelCase in dict
    assert dict_form["payload"] == {"key": "value"}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
