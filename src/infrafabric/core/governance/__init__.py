"""
InfraFabric Governance Module
==============================

IF.ARBITRATE - Conflict Resolution & Consensus Engine

Exports:
  - Arbitrator: Guardian Council decision-making engine
  - ArbitrationCase: Case data structure with audit trail
  - Vote: Individual agent vote with traceability
  - VetoRecord: Contrarian Guardian veto record
  - VotePosition: Enum for vote positions (YES/NO/ABSTAIN)
  - CaseStatus: Enum for case lifecycle states
  - DecisionOutcome: Enum for final decision types
"""

from .arbitrate import (
    Arbitrator,
    ArbitrationCase,
    Vote,
    VetoRecord,
    VotePosition,
    CaseStatus,
    DecisionOutcome,
    AGENT_WEIGHT_MAP,
    AMENDMENT_THRESHOLD,
    VETO_THRESHOLD,
    COOLING_OFF_DAYS,
)

__all__ = [
    'Arbitrator',
    'ArbitrationCase',
    'Vote',
    'VetoRecord',
    'VotePosition',
    'CaseStatus',
    'DecisionOutcome',
    'AGENT_WEIGHT_MAP',
    'AMENDMENT_THRESHOLD',
    'VETO_THRESHOLD',
    'COOLING_OFF_DAYS',
]

__version__ = '1.0.0'
__author__ = 'InfraFabric Guardian Council'
