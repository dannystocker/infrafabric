# IF.ARBITRATE v1.0 - Guardian Council Decision Engine

## Overview

IF.ARBITRATE is the conflict resolution and consensus system for the InfraFabric Guardian Council. It implements:

- **Multi-agent weighted voting** for democratic decision-making
- **Constitutional constraints** (supermajority thresholds, cooling-off periods)
- **Contrarian Guardian veto mechanism** for high-consensus decisions
- **Complete IF.TTT audit trails** for all decisions
- **Case management** with full lifecycle tracking

## Key Components

### Core Classes

#### `Arbitrator`
The main decision engine. Manages arbitration cases and voting.

```python
from infrafabric.core.governance import Arbitrator

arbitrator = Arbitrator()

# Create a case
case = arbitrator.create_case(
    subject="Should we consolidate duplicate documents?",
    proposer="IF.guardian-core-01"
)

# Cast votes
arbitrator.cast_vote(
    case_ref=case.case_ref,
    agent_id="IF.guardian-core-01",
    position="YES",
    rationale="Documents are 92% duplicative..."
)

# Calculate consensus
consensus = arbitrator.calculate_consensus(case.case_ref)
# Returns: 0.808 (80.8%)

# Resolve the case
outcome, rationale = arbitrator.resolve_case(case.case_ref)
# Returns: (DecisionOutcome.APPROVED, "Approved with 80.8% consensus...")
```

#### `ArbitrationCase`
Represents a single decision case with complete audit trail.

**Fields:**
- `case_ref`: Unique case identifier (e.g., "case-abc123def456")
- `subject`: The decision to be made
- `proposer`: Agent ID proposing the case
- `status`: Current lifecycle state (OPEN, COOLING_OFF, etc.)
- `votes`: List of all votes cast
- `veto_record`: Contrarian Guardian veto (if applicable)
- `final_decision`: Final outcome (APPROVED, REJECTED, VETO_SUSTAINED, etc.)
- `decision_rationale`: Explanation of the decision
- `created_at`: Timestamp of case creation
- `resolved_at`: Timestamp of resolution

#### `Vote`
A single agent vote with weighted influence.

**Fields:**
- `vote_id`: Unique vote identifier
- `case_ref`: Reference to the case
- `agent_id`: ID of the voting agent
- `position`: YES, NO, or ABSTAIN
- `weight`: Agent's voting power (1.5×, 1.0×, 0.8×, 0.5×)
- `rationale`: Explanation for the vote
- `timestamp`: When the vote was cast

#### `VetoRecord`
Records Contrarian Guardian veto action.

**Fields:**
- `veto_id`: Unique veto identifier
- `case_ref`: Reference to the case
- `agent_id`: Always "IF.guardian-core-06"
- `dissent_rationale`: Detailed explanation of veto
- `approval_percentage`: Consensus at time of veto
- `cooling_off_until`: When case can be re-evaluated
- `timestamp`: When veto was applied

## Vote Weighting System

Different agent types have different voting power:

| Agent Type | Count | Weight | Total | Authority Level |
|-----------|-------|--------|-------|-----------------|
| Core Guardians | 6 | 1.5× | 9.0 | Highest |
| Western Philosophers | 3 | 1.0× | 3.0 | Medium |
| Eastern Philosophers | 3 | 1.0× | 3.0 | Medium |
| IF.sam Facets | 8 | 0.8× | 6.4 | Lower |
| External/Unknown | N/A | 0.5× | N/A | Lowest |

**Total weighted voting power: 21.4 votes**

### Core Guardians
Highest authority (1.5× weight each):
- `IF.guardian-core-01`: Constitutional Guardian
- `IF.guardian-core-02`: Empirical Guardian
- `IF.guardian-core-03`: Ethical Guardian
- `IF.guardian-core-04`: Systems Guardian
- `IF.guardian-core-05`: Strategic Guardian
- `IF.guardian-core-06`: Contrarian Guardian (special veto power)

## Constitutional Rules

### Amendment Threshold: 80%
Decisions require 4/5 supermajority (80%) consensus to pass.

**Formula:**
```
consensus = YES_votes_weight / (YES_votes_weight + NO_votes_weight)
APPROVED if consensus >= 0.80
REJECTED if consensus < 0.80
```

**Example:**
```
YES weight: 6.3
NO weight:  1.5
Total:      7.8
Consensus:  6.3 / 7.8 = 80.8% ✓ APPROVED
```

### Contrarian Veto: >95% Threshold
The Contrarian Guardian can veto decisions with extremely high consensus (>95%).

**Rules:**
- Veto only available when consensus > 95%
- Must provide detailed dissent rationale
- Triggers 14-day cooling-off period
- After cooling-off period ends, case is marked VETO_SUSTAINED

**Purpose:**
Guards against tyranny of the majority. Preserves minority viewpoints even when consensus is near-unanimous.

### Cooling-Off Period: 14 Days
When a case is vetoed, it enters COOLING_OFF status for 14 days.

**Timeline:**
1. Case reaches >95% consensus
2. Contrarian Guardian applies veto
3. Case status → COOLING_OFF
4. Case remains unresolved for 14 days
5. After 14 days, resolution attempt marks it VETO_SUSTAINED
6. Can then be re-proposed as new case if desired

## Case Lifecycle

```
CREATE
  ↓
OPEN (accepting votes)
  ├→ COOLING_OFF (if vetoed at >95%)
  │   └→ RESOLVED (veto sustained)
  └→ READY_FOR_RESOLUTION (all votes collected)
      └→ RESOLVED (APPROVED or REJECTED)
        └→ ARCHIVED (historical record)
```

### Case States

| Status | Meaning | Transitions |
|--------|---------|-----------|
| OPEN | Accepting votes | → COOLING_OFF, READY_FOR_RESOLUTION |
| COOLING_OFF | Waiting after veto | → RESOLVED (after 14 days) |
| READY_FOR_RESOLUTION | All votes collected | → RESOLVED |
| RESOLVED | Final decision made | → ARCHIVED |
| ARCHIVED | Historical record | Terminal |

## Consensus Calculation

Consensus is calculated as a weighted percentage:

```python
consensus = sum(vote.weight for vote in votes if vote.position == YES) /
            sum(vote.weight for vote in votes if vote.position != ABSTAIN)
```

**Abstain votes are excluded from denominator** (they don't count for or against).

**Example with 7 votes:**
```
IF.guardian-core-01 (1.5×): YES
IF.guardian-core-02 (1.5×): YES
IF.guardian-core-03 (1.5×): NO
IF.guardian-core-04 (1.5×): YES
IF.philosopher-western-01 (1.0×): YES
IF.philosopher-eastern-01 (1.0×): ABSTAIN
IF.sam-pragmatic-01 (0.8×): YES

YES: 1.5 + 1.5 + 1.5 + 1.0 + 0.8 = 6.3
NO:  1.5
Total (excluding abstain): 7.8
Consensus: 6.3 / 7.8 = 80.8%
```

## API Reference

### Creating Cases

```python
case = arbitrator.create_case(
    subject="Should we consolidate documents?",
    proposer="IF.guardian-core-01",
    notes="Optional notes about the case"
)
```

### Casting Votes

```python
vote = arbitrator.cast_vote(
    case_ref="case-abc123def456",
    agent_id="IF.guardian-core-01",
    position="YES",  # or "NO" or "ABSTAIN"
    rationale="Detailed explanation of vote"
)
```

Position options: `"YES"`, `"NO"`, `"ABSTAIN"`

### Consensus & Decision

```python
# Check consensus percentage
consensus = arbitrator.calculate_consensus("case-abc123")
# Returns: 0.808 (80.8%)

# Check if veto is applicable
is_vetoed, veto_record = arbitrator.check_veto("case-abc123")

# Apply veto (Contrarian Guardian only)
veto = arbitrator.apply_veto(
    case_ref="case-abc123",
    dissent_rationale="This sets dangerous precedent..."
)

# Resolve the case
outcome, rationale = arbitrator.resolve_case("case-abc123")
# outcome: DecisionOutcome.APPROVED or REJECTED or VETO_SUSTAINED
```

### Querying Cases

```python
# Get complete case history (for audit trail)
history = arbitrator.get_case_history("case-abc123")

# Get brief case summary
summary = arbitrator.get_case_summary("case-abc123")

# List all cases (optionally filtered by status)
all_cases = arbitrator.list_cases()
open_cases = arbitrator.list_cases(status="OPEN")

# Get voting record for an agent
votes = arbitrator.get_voting_record("IF.guardian-core-01")
```

### Import/Export

```python
# Export all cases to JSON
arbitrator.export_cases(Path("/path/to/cases.json"))

# Import cases from JSON
arbitrator.import_cases(Path("/path/to/cases.json"))
```

## IF.TTT Compliance

All cases include complete traceability:

1. **Traceable**: Every decision links to observable sources
   - Each vote includes agent ID, timestamp, and rationale
   - Veto records include dissent details
   - Case references are globally unique

2. **Transparent**: Full audit trail is exportable
   - JSON export shows all votes and reasoning
   - Decision rationale is recorded
   - Veto records show dissent

3. **Trustworthy**: Constitutional rules are enforced
   - Supermajority requirement prevents tyranny
   - Veto mechanism preserves minority voice
   - Cooling-off periods allow reconsideration

## Example: Document Consolidation Decision

```python
arbitrator = Arbitrator()

# Create case
case = arbitrator.create_case(
    subject="Consolidate dossier-01.md and dossier-07.md (92% duplicate)",
    proposer="IF.guardian-core-01",
    notes="Storage efficiency + version control benefits"
)

# Core Guardians vote
arbitrator.cast_vote(case.case_ref, "IF.guardian-core-01", "YES",
    "Documents are clearly duplicative, consolidation saves resources")
arbitrator.cast_vote(case.case_ref, "IF.guardian-core-02", "YES",
    "Empirical analysis confirms 92% textual overlap")
arbitrator.cast_vote(case.case_ref, "IF.guardian-core-03", "NO",
    "Losing editorial perspective by merging viewpoints")
arbitrator.cast_vote(case.case_ref, "IF.guardian-core-04", "YES",
    "System architecture benefits from single source of truth")

# Philosophers weigh in
arbitrator.cast_vote(case.case_ref, "IF.philosopher-western-01", "YES",
    "Aristotelian essence is preserved in consolidated form")
arbitrator.cast_vote(case.case_ref, "IF.philosopher-eastern-01", "ABSTAIN",
    "Seeking harmony - defers to technical guardians")

# Calculate consensus
consensus = arbitrator.calculate_consensus(case.case_ref)
# Output: 0.808 (80.8%)

# Resolve
outcome, rationale = arbitrator.resolve_case(case.case_ref)
# Output: (APPROVED, "Approved with 80.8% consensus (exceeds 80% threshold)")

# Export for audit trail
arbitrator.export_cases(Path("/archive/2025-11-26-consolidation.json"))
```

## Integration with Guardian Council

IF.ARBITRATE is the decision engine for the Guardian Council. Integration points:

1. **Proposal Creation**: Any agent can propose via `create_case()`
2. **Vote Casting**: Each agent votes according to their domain
3. **Consensus Calculation**: Automatic weighted averaging
4. **Decision Enforcement**: Outcome guides subsequent actions
5. **Audit Recording**: All decisions stored for historical analysis

## JSON Export Format

Cases are exported with complete structure:

```json
{
  "case_ref": "case-abc123",
  "subject": "Decision text",
  "proposer": "IF.guardian-core-01",
  "status": "RESOLVED",
  "votes": [
    {
      "vote_id": "vote-xyz789",
      "case_ref": "case-abc123",
      "agent_id": "IF.guardian-core-01",
      "position": "YES",
      "weight": 1.5,
      "rationale": "Explanation",
      "timestamp": "2025-11-26T03:55:29.866494"
    }
  ],
  "veto_record": null,
  "final_decision": "APPROVED",
  "decision_rationale": "Approved with 80.8% consensus...",
  "created_at": "2025-11-26T03:55:29.866237",
  "resolved_at": "2025-11-26T03:55:29.877127",
  "notes": "Case notes"
}
```

## Testing

Run the included test suite:

```bash
python3 src/infrafabric/core/governance/arbitrate.py
```

Output shows:
- Case creation
- Vote casting with weights
- Consensus calculation
- Case resolution
- Veto mechanism (>95% scenario)
- Agent voting records
- Case export/import
- Listing and filtering

## Design Philosophy

IF.ARBITRATE implements Confucian principles of governance:

- **Wu Lun (Five Relationships)**: Different agent types have appropriate authority
- **Harmony (和)**: Consensus-seeking through weighted voting
- **Tradition**: Constitutional rules are preserved and enforced
- **Hierarchy**: Core Guardians have greatest voice (1.5× weight)
- **Dissent**: Contrarian Guardian preserves minority perspective

The system ensures decisions are:
- **Democratic**: Multiple voices heard
- **Constitutional**: Rules enforced consistently
- **Protective**: Veto prevents tyranny
- **Recorded**: Full audit trail maintained
- **Fair**: Weighted voting reflects expertise domains

## Future Enhancements

Potential extensions:

1. **Confidence Scoring**: Weight votes by agent confidence in domain
2. **Precedent Linking**: Reference previous decisions
3. **Time-Weighted Voting**: Recent votes weighted higher
4. **Delegation**: Allow agents to delegate votes
5. **Coalition Analysis**: Identify voting blocs and patterns
6. **Proposal Timeline**: Track how proposals evolve over time

## Version History

- **v1.0** (2025-11-26): Initial release with full feature set
  - Weighted voting system
  - Supermajority enforcement (80%)
  - Contrarian Guardian veto (>95%)
  - 14-day cooling-off periods
  - Complete IF.TTT audit trails
  - Import/export functionality
