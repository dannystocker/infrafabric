#!/usr/bin/env python3
"""
IF.ARBITRATE v1.0 - Conflict Resolution & Consensus Engine
===========================================================

Role: Guardian Council's decision-making engine
Pattern: Multi-agent weighted voting + Constitutional constraints
Compliance: IF.TTT (Traceable, Transparent, Trustworthy)

Architecture:
  Arbitrator manages ArbitrationCases
    ↓
  Multiple agents cast weighted votes (YES/NO/ABSTAIN)
    ↓
  Consensus calculation (percentage-based)
    ↓
  Veto mechanism (Contrarian Guardian override)
    ↓
  Resolution & audit trail recording

Constitutional Rules:
  - 4/5 supermajority (80%) required for amendments
  - 14-day cooling-off period for vetoed proposals
  - Contrarian Guardian veto at >95% approval (with recorded dissent)
  - All decisions recorded with IF.TTT traceability

Vote Weighting System:
  Core Guardians: 1.5× weight (6 agents)
  Western Philosophers: 1.0× weight (3 agents)
  Eastern Philosophers: 1.0× weight (3 agents)
  IF.sam facets: 0.8× weight (8 agents)
  External agents: 0.5× weight (if applicable)

Usage:
  arbitrator = Arbitrator()
  case = arbitrator.create_case(
      subject="Should we consolidate documents?",
      proposer="IF.guardian-core-01"
  )
  arbitrator.cast_vote(
      case_ref=case.case_ref,
      agent_id="IF.guardian-core-01",
      position="YES",
      rationale="Documents are duplicative..."
  )
  result = arbitrator.resolve_case(case.case_ref)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import uuid
from pathlib import Path


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class VotePosition(Enum):
    """Vote position options"""
    YES = "YES"
    NO = "NO"
    ABSTAIN = "ABSTAIN"


class CaseStatus(Enum):
    """Case lifecycle states"""
    OPEN = "OPEN"                          # Accepting votes
    COOLING_OFF = "COOLING_OFF"            # Vetoed, waiting 14 days
    READY_FOR_RESOLUTION = "READY_FOR_RESOLUTION"  # All votes collected
    RESOLVED = "RESOLVED"                  # Final decision made
    ARCHIVED = "ARCHIVED"                  # Historical record


class DecisionOutcome(Enum):
    """Final decision types"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    VETO_SUSTAINED = "VETO_SUSTAINED"
    INCONCLUSIVE = "INCONCLUSIVE"


# Agent weight mapping (reflects voting power in council)
AGENT_WEIGHT_MAP = {
    # Core Guardians (6 agents) - highest authority
    "IF.guardian-core-01": 1.5,  # Constitutional Guardian
    "IF.guardian-core-02": 1.5,  # Empirical Guardian
    "IF.guardian-core-03": 1.5,  # Ethical Guardian
    "IF.guardian-core-04": 1.5,  # Systems Guardian
    "IF.guardian-core-05": 1.5,  # Strategic Guardian
    "IF.guardian-core-06": 1.5,  # Contrarian Guardian (special veto power)

    # Western Philosophers (3 agents) - 1.0× weight
    "IF.philosopher-western-01": 1.0,  # Aristotle
    "IF.philosopher-western-02": 1.0,  # Kant
    "IF.philosopher-western-03": 1.0,  # Mill

    # Eastern Philosophers (3 agents) - 1.0× weight
    "IF.philosopher-eastern-01": 1.0,  # Confucius
    "IF.philosopher-eastern-02": 1.0,  # Zhuangzi
    "IF.philosopher-eastern-03": 1.0,  # Nagarjuna

    # IF.sam facets (8 agents) - 0.8× weight
    "IF.sam-idealistic-01": 0.8,
    "IF.sam-idealistic-02": 0.8,
    "IF.sam-idealistic-03": 0.8,
    "IF.sam-idealistic-04": 0.8,
    "IF.sam-pragmatic-01": 0.8,
    "IF.sam-pragmatic-02": 0.8,
    "IF.sam-pragmatic-03": 0.8,
    "IF.sam-pragmatic-04": 0.8,
}

# Constitutional thresholds
AMENDMENT_THRESHOLD = 0.80      # 4/5 supermajority
VETO_THRESHOLD = 0.95            # Contrarian can veto >95% approval
COOLING_OFF_DAYS = 14


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Vote:
    """Single agent vote with traceability"""
    vote_id: str
    case_ref: str
    agent_id: str
    position: VotePosition
    weight: float
    rationale: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'vote_id': self.vote_id,
            'case_ref': self.case_ref,
            'agent_id': self.agent_id,
            'position': self.position.value,
            'weight': self.weight,
            'rationale': self.rationale,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class VetoRecord:
    """Record of Contrarian Guardian veto"""
    veto_id: str
    case_ref: str
    agent_id: str
    dissent_rationale: str
    approval_percentage: float
    cooling_off_until: datetime
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'veto_id': self.veto_id,
            'case_ref': self.case_ref,
            'agent_id': self.agent_id,
            'dissent_rationale': self.dissent_rationale,
            'approval_percentage': self.approval_percentage,
            'cooling_off_until': self.cooling_off_until.isoformat(),
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class ArbitrationCase:
    """Arbitration case with complete audit trail"""
    case_ref: str
    subject: str
    proposer: str
    status: CaseStatus
    votes: List[Vote] = field(default_factory=list)
    veto_record: Optional[VetoRecord] = None
    final_decision: Optional[DecisionOutcome] = None
    decision_rationale: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'case_ref': self.case_ref,
            'subject': self.subject,
            'proposer': self.proposer,
            'status': self.status.value,
            'votes': [v.to_dict() for v in self.votes],
            'veto_record': self.veto_record.to_dict() if self.veto_record else None,
            'final_decision': self.final_decision.value if self.final_decision else None,
            'decision_rationale': self.decision_rationale,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'notes': self.notes,
        }


# ============================================================================
# ARBITRATOR ENGINE
# ============================================================================

class Arbitrator:
    """
    Guardian Council decision-making engine

    Manages arbitration cases with:
    - Weighted multi-agent voting
    - Constitutional constraints
    - Veto mechanisms
    - Complete audit trails
    """

    def __init__(self, archive_path: Optional[Path] = None):
        """
        Initialize Arbitrator

        Args:
            archive_path: Optional path to store case records
                         Defaults to ./arbitration_archive/
        """
        self.cases: Dict[str, ArbitrationCase] = {}
        self.archive_path = Path(archive_path) if archive_path else Path("./arbitration_archive")
        self.archive_path.mkdir(parents=True, exist_ok=True)

    def create_case(self,
                   subject: str,
                   proposer: str,
                   notes: str = "") -> ArbitrationCase:
        """
        Create a new arbitration case

        Args:
            subject: The decision to be made
            proposer: Agent ID of the proposer
            notes: Optional notes on the case

        Returns:
            ArbitrationCase: The created case

        Example:
            case = arbitrator.create_case(
                subject="Should we consolidate documents?",
                proposer="IF.guardian-core-01"
            )
        """
        case_ref = f"case-{uuid.uuid4().hex[:12]}"

        case = ArbitrationCase(
            case_ref=case_ref,
            subject=subject,
            proposer=proposer,
            status=CaseStatus.OPEN,
            notes=notes,
        )

        self.cases[case_ref] = case
        self._save_case(case)

        return case

    def cast_vote(self,
                 case_ref: str,
                 agent_id: str,
                 position: str,
                 rationale: str) -> Vote:
        """
        Cast a vote on an arbitration case

        Args:
            case_ref: Reference to the case
            agent_id: ID of the voting agent
            position: Vote position (YES/NO/ABSTAIN)
            rationale: Explanation of the vote

        Returns:
            Vote: The recorded vote

        Raises:
            ValueError: If case not found, invalid position, or agent not recognized

        Example:
            vote = arbitrator.cast_vote(
                case_ref="case-abc123",
                agent_id="IF.guardian-core-01",
                position="YES",
                rationale="This addresses duplicative content effectively..."
            )
        """
        if case_ref not in self.cases:
            raise ValueError(f"Case {case_ref} not found")

        case = self.cases[case_ref]

        if case.status not in [CaseStatus.OPEN, CaseStatus.COOLING_OFF]:
            raise ValueError(f"Case {case_ref} is {case.status.value}, cannot accept votes")

        # Validate position
        try:
            vote_position = VotePosition[position.upper()]
        except KeyError:
            raise ValueError(f"Invalid position: {position}. Must be YES, NO, or ABSTAIN")

        # Get agent weight
        weight = AGENT_WEIGHT_MAP.get(agent_id, 0.5)  # Default 0.5 for unknown agents

        # Check for duplicate votes from same agent
        existing_vote = next((v for v in case.votes if v.agent_id == agent_id), None)
        if existing_vote:
            # Replace existing vote
            case.votes.remove(existing_vote)

        vote_id = f"vote-{uuid.uuid4().hex[:12]}"
        vote = Vote(
            vote_id=vote_id,
            case_ref=case_ref,
            agent_id=agent_id,
            position=vote_position,
            weight=weight,
            rationale=rationale,
        )

        case.votes.append(vote)
        # Keep status as OPEN to allow more votes

        self._save_case(case)

        return vote

    def calculate_consensus(self, case_ref: str) -> float:
        """
        Calculate consensus percentage for a case

        Uses weighted voting where each agent's vote is multiplied by their weight.
        Result is percentage of weighted YES votes / total weighted votes.

        Args:
            case_ref: Reference to the case

        Returns:
            float: Consensus percentage (0.0 to 1.0)

        Raises:
            ValueError: If case not found or no votes cast

        Example:
            consensus = arbitrator.calculate_consensus("case-abc123")
            print(f"Consensus: {consensus:.1%}")  # Output: Consensus: 82.5%
        """
        if case_ref not in self.cases:
            raise ValueError(f"Case {case_ref} not found")

        case = self.cases[case_ref]

        if not case.votes:
            return 0.0

        yes_weight = 0.0
        total_weight = 0.0

        for vote in case.votes:
            if vote.position != VotePosition.ABSTAIN:
                total_weight += vote.weight
                if vote.position == VotePosition.YES:
                    yes_weight += vote.weight

        if total_weight == 0:
            return 0.0

        return yes_weight / total_weight

    def check_veto(self, case_ref: str) -> Tuple[bool, Optional[VetoRecord]]:
        """
        Check if Contrarian Guardian can/should veto

        Contrarian Guardian (IF.guardian-core-06) has special veto power:
        - Can veto decisions with >95% approval
        - Must provide detailed dissent rationale
        - Triggers 14-day cooling-off period

        Args:
            case_ref: Reference to the case

        Returns:
            Tuple[bool, Optional[VetoRecord]]: (veto_active, veto_record)

        Raises:
            ValueError: If case not found

        Example:
            is_vetoed, record = arbitrator.check_veto("case-abc123")
            if is_vetoed:
                print(f"Vetoed until {record.cooling_off_until}")
        """
        if case_ref not in self.cases:
            raise ValueError(f"Case {case_ref} not found")

        case = self.cases[case_ref]

        # If already vetoed, return existing veto
        if case.veto_record:
            return True, case.veto_record

        # Check if approval is >95%
        consensus = self.calculate_consensus(case_ref)
        if consensus > VETO_THRESHOLD:
            # Contrarian Guardian CAN veto, but hasn't yet
            # This is checked during resolution
            return False, None

        return False, None

    def apply_veto(self,
                  case_ref: str,
                  dissent_rationale: str) -> VetoRecord:
        """
        Apply Contrarian Guardian veto to a case

        Requires:
        - Approval percentage > 95%
        - Detailed dissent rationale
        - Sets case to COOLING_OFF status

        Args:
            case_ref: Reference to the case
            dissent_rationale: Detailed explanation of veto

        Returns:
            VetoRecord: The veto record

        Raises:
            ValueError: If case not eligible for veto

        Example:
            veto = arbitrator.apply_veto(
                case_ref="case-abc123",
                dissent_rationale="This precedent is dangerous because..."
            )
        """
        if case_ref not in self.cases:
            raise ValueError(f"Case {case_ref} not found")

        case = self.cases[case_ref]

        # Check veto eligibility
        consensus = self.calculate_consensus(case_ref)
        if consensus <= VETO_THRESHOLD:
            raise ValueError(
                f"Veto only allowed at >{VETO_THRESHOLD:.0%} approval. "
                f"Current: {consensus:.1%}"
            )

        # Create veto record
        veto_id = f"veto-{uuid.uuid4().hex[:12]}"
        cooling_off_until = datetime.utcnow() + timedelta(days=COOLING_OFF_DAYS)

        veto_record = VetoRecord(
            veto_id=veto_id,
            case_ref=case_ref,
            agent_id="IF.guardian-core-06",  # Contrarian Guardian
            dissent_rationale=dissent_rationale,
            approval_percentage=consensus,
            cooling_off_until=cooling_off_until,
        )

        case.veto_record = veto_record
        case.status = CaseStatus.COOLING_OFF

        self._save_case(case)

        return veto_record

    def resolve_case(self, case_ref: str) -> Tuple[DecisionOutcome, str]:
        """
        Resolve a case based on votes and Constitutional rules

        Resolution logic:
        1. If vetoed: VETO_SUSTAINED
        2. If ≥80% (AMENDMENT_THRESHOLD): APPROVED
        3. If cooling-off period active: INCONCLUSIVE (wait to resolve)
        4. Otherwise: REJECTED

        Args:
            case_ref: Reference to the case

        Returns:
            Tuple[DecisionOutcome, str]: (outcome, rationale)

        Raises:
            ValueError: If case not found or cannot be resolved

        Example:
            outcome, rationale = arbitrator.resolve_case("case-abc123")
            print(f"Decision: {outcome.value}")
            print(f"Rationale: {rationale}")
        """
        if case_ref not in self.cases:
            raise ValueError(f"Case {case_ref} not found")

        case = self.cases[case_ref]

        if not case.votes:
            raise ValueError(f"Case {case_ref} has no votes, cannot resolve")

        consensus = self.calculate_consensus(case_ref)

        # Check for active veto
        if case.veto_record:
            if datetime.utcnow() < case.veto_record.cooling_off_until:
                outcome = DecisionOutcome.INCONCLUSIVE
                rationale = (
                    f"Case is in cooling-off period due to veto. "
                    f"Can be re-evaluated after {case.veto_record.cooling_off_until.isoformat()}"
                )
                case.final_decision = outcome
                case.decision_rationale = rationale
                self._save_case(case)
                return outcome, rationale
            else:
                # Cooling-off period has ended, can now resolve
                outcome = DecisionOutcome.VETO_SUSTAINED
                rationale = (
                    f"Veto sustained by Contrarian Guardian. "
                    f"Dissent: {case.veto_record.dissent_rationale}"
                )
                case.final_decision = outcome
                case.decision_rationale = rationale
                case.status = CaseStatus.RESOLVED
                case.resolved_at = datetime.utcnow()
                self._save_case(case)
                return outcome, rationale

        # Check supermajority
        if consensus >= AMENDMENT_THRESHOLD:
            outcome = DecisionOutcome.APPROVED
            rationale = (
                f"Approved with {consensus:.1%} consensus "
                f"(exceeds {AMENDMENT_THRESHOLD:.0%} threshold)"
            )
        else:
            outcome = DecisionOutcome.REJECTED
            rationale = (
                f"Rejected with {consensus:.1%} consensus "
                f"(below {AMENDMENT_THRESHOLD:.0%} threshold)"
            )

        case.final_decision = outcome
        case.decision_rationale = rationale
        case.status = CaseStatus.RESOLVED
        case.resolved_at = datetime.utcnow()

        self._save_case(case)

        return outcome, rationale

    def get_case_history(self, case_ref: str) -> Dict:
        """
        Get complete audit trail for a case

        Returns all votes, veto records, and decision history.
        Suitable for IF.TTT compliance reporting.

        Args:
            case_ref: Reference to the case

        Returns:
            Dict: Complete case history with all details

        Raises:
            ValueError: If case not found

        Example:
            history = arbitrator.get_case_history("case-abc123")
            print(json.dumps(history, indent=2))
        """
        if case_ref not in self.cases:
            raise ValueError(f"Case {case_ref} not found")

        case = self.cases[case_ref]
        return case.to_dict()

    def get_case_summary(self, case_ref: str) -> Dict:
        """
        Get brief summary of case status

        Args:
            case_ref: Reference to the case

        Returns:
            Dict: Summary with key metrics

        Raises:
            ValueError: If case not found
        """
        if case_ref not in self.cases:
            raise ValueError(f"Case {case_ref} not found")

        case = self.cases[case_ref]
        consensus = self.calculate_consensus(case_ref) if case.votes else 0.0

        return {
            'case_ref': case_ref,
            'subject': case.subject,
            'status': case.status.value,
            'votes_cast': len(case.votes),
            'consensus': f"{consensus:.1%}",
            'final_decision': case.final_decision.value if case.final_decision else None,
            'created_at': case.created_at.isoformat(),
            'resolved_at': case.resolved_at.isoformat() if case.resolved_at else None,
        }

    def list_cases(self, status: Optional[str] = None) -> List[Dict]:
        """
        List all cases, optionally filtered by status

        Args:
            status: Optional status filter (OPEN, COOLING_OFF, READY_FOR_RESOLUTION,
                   RESOLVED, ARCHIVED)

        Returns:
            List[Dict]: List of case summaries
        """
        result = []

        for case_ref, case in self.cases.items():
            if status and case.status.value != status:
                continue

            result.append(self.get_case_summary(case_ref))

        return result

    def get_voting_record(self, agent_id: str) -> List[Dict]:
        """
        Get all votes cast by a specific agent

        Useful for analyzing voting patterns and agent influence.

        Args:
            agent_id: ID of the agent

        Returns:
            List[Dict]: All votes cast by this agent
        """
        votes = []

        for case in self.cases.values():
            for vote in case.votes:
                if vote.agent_id == agent_id:
                    votes.append({
                        'case_ref': case.case_ref,
                        'subject': case.subject,
                        'vote_id': vote.vote_id,
                        'position': vote.position.value,
                        'weight': vote.weight,
                        'rationale': vote.rationale,
                        'timestamp': vote.timestamp.isoformat(),
                    })

        return votes

    def export_cases(self, filepath: Path) -> None:
        """
        Export all cases to JSON file

        Useful for archival and backup.

        Args:
            filepath: Path to write JSON file
        """
        cases_data = {
            case_ref: case.to_dict()
            for case_ref, case in self.cases.items()
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(
            json.dumps(cases_data, indent=2),
            encoding='utf-8'
        )

    def import_cases(self, filepath: Path) -> None:
        """
        Import cases from JSON file

        Args:
            filepath: Path to read JSON file
        """
        data = json.loads(filepath.read_text(encoding='utf-8'))

        for case_ref, case_data in data.items():
            # Reconstruct case from JSON
            votes = [
                Vote(
                    vote_id=v['vote_id'],
                    case_ref=v['case_ref'],
                    agent_id=v['agent_id'],
                    position=VotePosition[v['position']],
                    weight=v['weight'],
                    rationale=v['rationale'],
                    timestamp=datetime.fromisoformat(v['timestamp']),
                )
                for v in case_data.get('votes', [])
            ]

            veto_record = None
            if case_data.get('veto_record'):
                vr = case_data['veto_record']
                veto_record = VetoRecord(
                    veto_id=vr['veto_id'],
                    case_ref=vr['case_ref'],
                    agent_id=vr['agent_id'],
                    dissent_rationale=vr['dissent_rationale'],
                    approval_percentage=vr['approval_percentage'],
                    cooling_off_until=datetime.fromisoformat(vr['cooling_off_until']),
                    timestamp=datetime.fromisoformat(vr['timestamp']),
                )

            case = ArbitrationCase(
                case_ref=case_data['case_ref'],
                subject=case_data['subject'],
                proposer=case_data['proposer'],
                status=CaseStatus[case_data['status']],
                votes=votes,
                veto_record=veto_record,
                final_decision=DecisionOutcome[case_data['final_decision']]
                    if case_data.get('final_decision') else None,
                decision_rationale=case_data.get('decision_rationale', ''),
                created_at=datetime.fromisoformat(case_data['created_at']),
                resolved_at=datetime.fromisoformat(case_data['resolved_at'])
                    if case_data.get('resolved_at') else None,
                notes=case_data.get('notes', ''),
            )

            self.cases[case_ref] = case

    def _save_case(self, case: ArbitrationCase) -> None:
        """
        Save case to archive (internal)

        Args:
            case: The case to save
        """
        filepath = self.archive_path / f"{case.case_ref}.json"
        filepath.write_text(
            json.dumps(case.to_dict(), indent=2),
            encoding='utf-8'
        )


# ============================================================================
# EXAMPLE USAGE & TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("IF.ARBITRATE v1.0 - Guardian Council Decision Engine")
    print("=" * 80)

    # Initialize arbitrator
    arbitrator = Arbitrator()

    # Test 1: Create a case
    print("\n[Test 1] Creating Arbitration Case")
    print("-" * 80)

    case = arbitrator.create_case(
        subject="Should we consolidate duplicate documents in the archive?",
        proposer="IF.guardian-core-01",
        notes="Documents dossier-01.md and dossier-07.md are 92% similar"
    )

    print(f"Case created: {case.case_ref}")
    print(f"Subject: {case.subject}")
    print(f"Status: {case.status.value}")
    print(f"Created at: {case.created_at.isoformat()}")

    # Test 2: Cast votes
    print("\n[Test 2] Casting Weighted Votes")
    print("-" * 80)

    votes_to_cast = [
        ("IF.guardian-core-01", "YES", "Documents are duplicative and waste storage"),
        ("IF.guardian-core-02", "YES", "Empirical analysis confirms 92% overlap"),
        ("IF.guardian-core-03", "NO", "Losing perspective on ethical implications"),
        ("IF.guardian-core-04", "YES", "System efficiency gains are significant"),
        ("IF.philosopher-western-01", "YES", "Essence remains in consolidated form"),
        ("IF.philosopher-eastern-01", "ABSTAIN", "Seeking harmony before decision"),
        ("IF.sam-pragmatic-01", "YES", "Cost-benefit analysis supports consolidation"),
    ]

    for agent_id, position, rationale in votes_to_cast:
        vote = arbitrator.cast_vote(
            case_ref=case.case_ref,
            agent_id=agent_id,
            position=position,
            rationale=rationale
        )
        weight = AGENT_WEIGHT_MAP.get(agent_id, 0.5)
        print(f"  {agent_id:30s} ({weight}×): {position:8s} - {rationale[:50]}")

    # Test 3: Calculate consensus
    print("\n[Test 3] Consensus Calculation")
    print("-" * 80)

    consensus = arbitrator.calculate_consensus(case.case_ref)
    vote_count = len(case.votes)

    print(f"Total votes cast: {vote_count}")
    print(f"Consensus percentage: {consensus:.1%}")
    print("Weighted vote breakdown:")

    yes_weight = sum(v.weight for v in case.votes if v.position == VotePosition.YES)
    no_weight = sum(v.weight for v in case.votes if v.position == VotePosition.NO)
    abstain_weight = sum(v.weight for v in case.votes if v.position == VotePosition.ABSTAIN)
    total_weight = sum(v.weight for v in case.votes if v.position != VotePosition.ABSTAIN)

    print(f"  YES votes:     {yes_weight:6.1f}× ({yes_weight/total_weight:.1%} of active)")
    print(f"  NO votes:      {no_weight:6.1f}× ({no_weight/total_weight:.1%} of active)")
    print(f"  ABSTAIN votes: {abstain_weight:6.1f}× (not counted)")

    # Test 4: Resolve case
    print("\n[Test 4] Case Resolution")
    print("-" * 80)

    outcome, rationale = arbitrator.resolve_case(case.case_ref)

    print(f"Final Decision: {outcome.value}")
    print(f"Rationale: {rationale}")
    print(f"Resolved at: {case.resolved_at.isoformat() if case.resolved_at else 'N/A'}")

    # Test 5: Case summary
    print("\n[Test 5] Case Summary")
    print("-" * 80)

    summary = arbitrator.get_case_summary(case.case_ref)
    for key, value in summary.items():
        print(f"  {key:20s}: {value}")

    # Test 6: Veto scenario (high approval)
    print("\n[Test 6] Veto Mechanism (>95% Approval Scenario)")
    print("-" * 80)

    # Create another case with near-unanimous approval
    case2 = arbitrator.create_case(
        subject="Implement controversial AI safety restriction",
        proposer="IF.guardian-core-01",
        notes="Proposed restriction on certain agent capabilities"
    )

    # Add votes that exceed veto threshold (>95%)
    veto_test_votes = [
        ("IF.guardian-core-01", "YES", "Safety critical"),
        ("IF.guardian-core-02", "YES", "Empirically justified"),
        ("IF.guardian-core-03", "YES", "Ethically required"),
        ("IF.guardian-core-04", "YES", "System stability improved"),
        ("IF.guardian-core-05", "YES", "Strategic necessity"),
        ("IF.philosopher-western-01", "YES", "Aristotelian virtue alignment"),
        ("IF.philosopher-western-02", "YES", "Kantian categorical imperative"),
        ("IF.philosopher-eastern-01", "YES", "Confucian harmony"),
    ]

    for agent_id, position, rationale in veto_test_votes:
        arbitrator.cast_vote(
            case_ref=case2.case_ref,
            agent_id=agent_id,
            position=position,
            rationale=rationale
        )

    consensus2 = arbitrator.calculate_consensus(case2.case_ref)
    print(f"Consensus on case2: {consensus2:.1%}")
    print(f"Eligible for veto: {consensus2 > VETO_THRESHOLD}")

    if consensus2 > VETO_THRESHOLD:
        print("\nContrarian Guardian (IF.guardian-core-06) can veto...")
        veto = arbitrator.apply_veto(
            case_ref=case2.case_ref,
            dissent_rationale=(
                "While well-intentioned, this restriction sets a dangerous precedent "
                "for future overreach. We must preserve agent autonomy even at some cost."
            )
        )
        print(f"Veto applied: {veto.veto_id}")
        print(f"Cooling-off until: {veto.cooling_off_until.isoformat()}")

        # Try to resolve (should show INCONCLUSIVE)
        outcome2, rationale2 = arbitrator.resolve_case(case2.case_ref)
        print(f"Resolution attempt: {outcome2.value}")
        print(f"Reason: {rationale2}")

    # Test 7: Voting record
    print("\n[Test 7] Agent Voting Record")
    print("-" * 80)

    votes = arbitrator.get_voting_record("IF.guardian-core-01")
    print(f"IF.guardian-core-01 has voted {len(votes)} times:")
    for v in votes:
        print(f"  Case {v['case_ref']}: {v['position']} on '{v['subject'][:50]}'")

    # Test 8: Export cases
    print("\n[Test 8] Case Export")
    print("-" * 80)

    export_path = Path("/tmp/arbitration_cases.json")
    arbitrator.export_cases(export_path)
    print(f"Cases exported to: {export_path}")
    print(f"File size: {export_path.stat().st_size} bytes")

    # Test 9: List cases
    print("\n[Test 9] List All Cases")
    print("-" * 80)

    all_cases = arbitrator.list_cases()
    print(f"Total cases: {len(all_cases)}")
    for case_summary in all_cases:
        print(f"\n  {case_summary['case_ref']}")
        print(f"    Subject: {case_summary['subject'][:60]}")
        print(f"    Status: {case_summary['status']}")
        print(f"    Consensus: {case_summary['consensus']}")
        print(f"    Decision: {case_summary['final_decision']}")

    print("\n" + "=" * 80)
    print("IF.ARBITRATE v1.0 loaded successfully")
    print("=" * 80)
    print("Features:")
    print("  ✓ Weighted multi-agent voting system")
    print("  ✓ Constitutional supermajority (80%) enforcement")
    print("  ✓ Contrarian Guardian veto mechanism (>95% threshold)")
    print("  ✓ 14-day cooling-off periods for vetoed proposals")
    print("  ✓ Complete IF.TTT audit trail recording")
    print("  ✓ Case import/export for archival")
    print("  ✓ Voting record analysis by agent")
    print("\nConstitutional Rules:")
    print(f"  Amendment threshold: {AMENDMENT_THRESHOLD:.0%}")
    print(f"  Veto threshold: {VETO_THRESHOLD:.0%}")
    print(f"  Cooling-off period: {COOLING_OFF_DAYS} days")
