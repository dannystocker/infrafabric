# IF.ARBITRATE Integration Guide

## Overview

IF.ARBITRATE is now integrated into the InfraFabric governance infrastructure. This guide explains how to integrate it with other InfraFabric components.

## Installation

The module is already installed at:
```
/home/setup/infrafabric/src/infrafabric/core/governance/
```

## Basic Usage

### Import the Module

```python
from infrafabric.core.governance import Arbitrator, DecisionOutcome

# Create an arbitrator instance
arbitrator = Arbitrator()
```

### Create a Decision Case

```python
case = arbitrator.create_case(
    subject="Proposal: Consolidate duplicate documents",
    proposer="IF.guardian-core-01",
    notes="Documents A and B are 92% similar"
)

print(f"Case created: {case.case_ref}")
# Output: Case created: case-abc123def456
```

### Cast Votes

```python
# Core Guardian votes
arbitrator.cast_vote(
    case_ref=case.case_ref,
    agent_id="IF.guardian-core-01",
    position="YES",
    rationale="Consolidation improves efficiency"
)

arbitrator.cast_vote(
    case_ref=case.case_ref,
    agent_id="IF.guardian-core-02",
    position="YES",
    rationale="Empirical analysis confirms redundancy"
)

arbitrator.cast_vote(
    case_ref=case.case_ref,
    agent_id="IF.guardian-core-03",
    position="NO",
    rationale="Concerns about losing editorial perspective"
)

# Philosopher perspective
arbitrator.cast_vote(
    case_ref=case.case_ref,
    agent_id="IF.philosopher-western-01",
    position="YES",
    rationale="Aristotelian essence is preserved"
)

arbitrator.cast_vote(
    case_ref=case.case_ref,
    agent_id="IF.philosopher-eastern-01",
    position="ABSTAIN",
    rationale="Seeking harmony - defer to technical experts"
)
```

### Check Consensus

```python
consensus = arbitrator.calculate_consensus(case.case_ref)
print(f"Current consensus: {consensus:.1%}")

# Check if veto is possible
is_eligible, veto_record = arbitrator.check_veto(case.case_ref)
if is_eligible:
    print("Consensus exceeds 95% - veto is possible")
```

### Resolve the Case

```python
outcome, rationale = arbitrator.resolve_case(case.case_ref)

if outcome == DecisionOutcome.APPROVED:
    print(f"Decision: APPROVED - {rationale}")
    # Proceed with implementation
elif outcome == DecisionOutcome.REJECTED:
    print(f"Decision: REJECTED - {rationale}")
    # Log and move on
elif outcome == DecisionOutcome.VETO_SUSTAINED:
    print(f"Decision: VETO_SUSTAINED - {rationale}")
    # Record dissent and halt
elif outcome == DecisionOutcome.INCONCLUSIVE:
    print(f"Decision: INCONCLUSIVE - {rationale}")
    # Wait for cooling-off period
```

## Integration with Guardian Council

### Proposal Pipeline

```python
# 1. Agent submits proposal
proposal = {
    'subject': 'Action to take',
    'description': 'Why this action matters',
    'proposer': 'IF.guardian-core-01'
}

# 2. Create case
case = arbitrator.create_case(
    subject=proposal['subject'],
    proposer=proposal['proposer'],
    notes=proposal['description']
)

# 3. All guardians vote
agents_to_vote = [
    'IF.guardian-core-01',
    'IF.guardian-core-02',
    'IF.guardian-core-03',
    'IF.guardian-core-04',
    'IF.philosopher-western-01',
    'IF.philosopher-eastern-01',
]

for agent_id in agents_to_vote:
    # Call agent to get their vote
    vote_result = get_agent_vote(agent_id, case.case_ref, proposal)

    arbitrator.cast_vote(
        case_ref=case.case_ref,
        agent_id=agent_id,
        position=vote_result['position'],  # YES/NO/ABSTAIN
        rationale=vote_result['rationale']
    )

# 4. Resolve
outcome, rationale = arbitrator.resolve_case(case.case_ref)

# 5. Execute based on outcome
if outcome == DecisionOutcome.APPROVED:
    execute_proposal(proposal)
    log_decision(case)
```

### Multi-Phase Decision Making

```python
class GovernanceCoordinator:
    def __init__(self):
        self.arbitrator = Arbitrator()

    def propose_decision(self, subject, proposer, description):
        """Phase 1: Create proposal"""
        case = self.arbitrator.create_case(
            subject=subject,
            proposer=proposer,
            notes=description
        )
        return case

    def collect_votes(self, case_ref, agents_config):
        """Phase 2: Collect weighted votes"""
        for agent_id, voting_logic in agents_config.items():
            position, rationale = voting_logic()
            self.arbitrator.cast_vote(
                case_ref=case_ref,
                agent_id=agent_id,
                position=position,
                rationale=rationale
            )

    def handle_high_consensus(self, case_ref):
        """Phase 3: Contrarian can veto >95% consensus"""
        consensus = self.arbitrator.calculate_consensus(case_ref)

        if consensus > 0.95:
            # Ask Contrarian Guardian to veto?
            veto_response = consult_contrarian_guardian(case_ref)

            if veto_response['should_veto']:
                self.arbitrator.apply_veto(
                    case_ref=case_ref,
                    dissent_rationale=veto_response['rationale']
                )

    def resolve_and_execute(self, case_ref):
        """Phase 4: Resolve and execute"""
        outcome, rationale = self.arbitrator.resolve_case(case_ref)

        if outcome == DecisionOutcome.APPROVED:
            return execute_decision(case_ref)
        elif outcome == DecisionOutcome.VETO_SUSTAINED:
            return record_veto_dissent(case_ref)
        elif outcome == DecisionOutcome.INCONCLUSIVE:
            return schedule_future_review(case_ref)
        else:  # REJECTED
            return log_rejection(case_ref)
```

## Archival and Reporting

### Export Cases for Audit Trail

```python
from pathlib import Path

# Export all cases
arbitrator.export_cases(Path('/archive/decisions/2025-11-26.json'))

# Import for analysis
arbitrator.import_cases(Path('/archive/decisions/2025-11-26.json'))
```

### Generate Reports

```python
# Case summary
all_cases = arbitrator.list_cases()
print(f"Total cases: {len(all_cases)}")

open_cases = arbitrator.list_cases(status="OPEN")
print(f"Open cases: {len(open_cases)}")

resolved_cases = arbitrator.list_cases(status="RESOLVED")
print(f"Resolved cases: {len(resolved_cases)}")

# Agent voting record
votes = arbitrator.get_voting_record("IF.guardian-core-01")
print(f"IF.guardian-core-01 has voted {len(votes)} times")

for vote in votes:
    print(f"  - {vote['subject']}: {vote['position']}")

# Complete audit trail
case_history = arbitrator.get_case_history("case-abc123")
print(json.dumps(case_history, indent=2))
```

## Advanced Scenarios

### Handling Tied Votes

When consensus is exactly 80% (threshold), the case APPROVED:

```python
# YES: 4.0 weight (1.5 + 1.5 + 1.0)
# NO: 1.0 weight (1.0)
# Total: 5.0
# Consensus: 4.0 / 5.0 = 80.0%

# This PASSES (>= 80%)
outcome, rationale = arbitrator.resolve_case(case_ref)
assert outcome == DecisionOutcome.APPROVED
```

### Abstain Voting

Abstain votes are excluded from the calculation:

```python
arbitrator.cast_vote(case_ref, agent_id, "ABSTAIN",
    "I defer to other experts on this matter")

# ABSTAIN votes do NOT count in denominator
# consensus = YES_weight / (YES_weight + NO_weight)
# ABSTAIN weight is not included
```

### Veto Scenarios

```python
# Case reaches 100% consensus (unlikely but possible)
consensus = arbitrator.calculate_consensus(case_ref)
assert consensus == 1.0

# Contrarian Guardian can veto
is_eligible, _ = arbitrator.check_veto(case_ref)
assert is_eligible == True

# Apply veto
veto = arbitrator.apply_veto(
    case_ref=case_ref,
    dissent_rationale="This precedent endangers agent autonomy"
)

# Case now in COOLING_OFF
outcome, _ = arbitrator.resolve_case(case_ref)
assert outcome == DecisionOutcome.INCONCLUSIVE

# Wait 14 days...
# After cooling-off period:
outcome, _ = arbitrator.resolve_case(case_ref)
assert outcome == DecisionOutcome.VETO_SUSTAINED
```

### Dynamic Vote Updating

An agent can change their vote:

```python
# Initial vote
arbitrator.cast_vote(case_ref, agent_id, "YES", "Initial reasoning")

# Updated reasoning
arbitrator.cast_vote(case_ref, agent_id, "NO", "New information discovered")

# Only the latest vote is counted
votes = [v for v in case.votes if v.agent_id == agent_id]
assert len(votes) == 1
assert votes[0].position == VotePosition.NO
```

## Error Handling

```python
from infrafabric.core.governance import Arbitrator

arbitrator = Arbitrator()

# Case not found
try:
    arbitrator.cast_vote("case-invalid", agent_id, "YES", "reason")
except ValueError as e:
    print(f"Error: {e}")

# Invalid position
try:
    arbitrator.cast_vote(case_ref, agent_id, "MAYBE", "reason")
except ValueError as e:
    print(f"Error: {e}")

# No votes to calculate
try:
    arbitrator.calculate_consensus("case-empty")
except ValueError as e:
    print(f"Error: {e}")

# Veto on low consensus
try:
    arbitrator.apply_veto(case_ref, "my dissent")
except ValueError as e:
    print(f"Only eligible at >95% consensus: {e}")
```

## Performance Characteristics

### Time Complexity
- `create_case()`: O(1)
- `cast_vote()`: O(n) where n = votes already cast
- `calculate_consensus()`: O(n) where n = total votes
- `resolve_case()`: O(n)
- `get_case_history()`: O(1)
- `list_cases()`: O(m) where m = total cases
- `export_cases()`: O(m * n)

### Storage
- Each case: ~1KB (minimal metadata)
- Each vote: ~200 bytes (agent, position, rationale)
- Each veto: ~500 bytes

Example: 1000 cases with 10 votes each = 2-3 MB

## IF.TTT Compliance

All operations are IF.TTT compliant:

1. **Traceable**
   - Unique case references (`case-*`)
   - Unique vote IDs (`vote-*`)
   - Unique veto IDs (`veto-*`)
   - Agent IDs recorded for all actions

2. **Transparent**
   - JSON export shows full decision record
   - Rationales preserved for all votes
   - Dissent recorded for vetoes
   - Timestamps on all actions

3. **Trustworthy**
   - Constitutional rules enforced in code
   - Supermajority requirement prevents tyranny
   - Veto mechanism preserves minority voice
   - Cooling-off period allows reconsideration

## Testing Integration

```python
def test_document_consolidation_decision():
    arbitrator = Arbitrator()

    # Scenario: Should we consolidate dossier-01 and dossier-07?
    case = arbitrator.create_case(
        subject="Consolidate dossier-01.md (92% duplicate of dossier-07.md)",
        proposer="IF.guardian-core-01"
    )

    # Vote
    votes = [
        ("IF.guardian-core-01", "YES", "Duplicates waste storage"),
        ("IF.guardian-core-02", "YES", "92% overlap confirmed"),
        ("IF.guardian-core-03", "NO", "Losing perspective"),
        ("IF.guardian-core-04", "YES", "Improves system"),
    ]

    for agent_id, position, rationale in votes:
        arbitrator.cast_vote(case.case_ref, agent_id, position, rationale)

    # Verify consensus
    consensus = arbitrator.calculate_consensus(case.case_ref)
    assert consensus >= 0.80  # Passes threshold

    # Resolve
    outcome, _ = arbitrator.resolve_case(case.case_ref)
    assert outcome == DecisionOutcome.APPROVED

    # Export for audit
    arbitrator.export_cases(Path("/tmp/test_cases.json"))
    assert Path("/tmp/test_cases.json").exists()
```

## Summary

IF.ARBITRATE provides:
- Democratic weighted voting
- Constitutional enforcement (80% supermajority)
- Veto mechanism (>95% threshold)
- Complete audit trails (IF.TTT compliance)
- Case management and archival

Use it for any Guardian Council decision that requires:
1. Multi-agent input
2. Weighted opinions
3. Democratic consensus
4. Protected dissent
5. Complete record-keeping

For questions or issues, refer to the comprehensive README.md in the governance module.
