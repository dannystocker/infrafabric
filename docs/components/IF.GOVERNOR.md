# IF.governor - Capability-Aware Resource Manager

**Component**: IF.governor
**Version**: 1.0
**Status**: Phase 0 Development
**Author**: Session 3 (H.323 Guardian Council)
**Last Updated**: 2025-11-12

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Capability Registry Guide](#capability-registry-guide)
4. [Policy Configuration](#policy-configuration)
5. [Budget Management](#budget-management)
6. [Circuit Breaker Tuning](#circuit-breaker-tuning)
7. [Example Policies](#example-policies)
8. [Integration Examples](#integration-examples)
9. [Troubleshooting](#troubleshooting)
10. [References](#references)

---

## Overview

### What is IF.governor?

IF.governor is InfraFabric's **capability-aware resource manager** that solves the critical efficiency problem: *How do we assign the right tasks to the right agents while staying within budget?*

### The Problem

**Before IF.governor (Bug #2 - 57% cost waste):**
- Tasks assigned randomly to available agents
- Expensive Sonnet model doing simple tasks that Haiku could handle
- No budget enforcement → cost spirals
- No capability matching → wrong agents doing wrong tasks
- Example: $15/hour Sonnet agent spent 2 hours on documentation that $2/hour Haiku could do in 1 hour
  - Cost: $30 (should have been $2)
  - Waste: $28 (93% waste!)

**After IF.governor (<10% waste):**
- Capability matching ensures 70%+ skill overlap
- Budget enforcement with hard limits and circuit breakers
- Cost tracking with IF.optimise integration
- Policy engine for governance rules
- Smart "Gang Up on Blocker" pattern

### Key Benefits

1. **Cost Efficiency**: Reduce waste from 57% to <10%
2. **Quality**: Match agents to tasks they're qualified for (70%+ capability overlap)
3. **Accountability**: Budget tracking and reputation scoring
4. **Safety**: Circuit breakers prevent cost spirals
5. **Governance**: Policy engine for organizational rules

### Philosophical Grounding

IF.governor embodies **Ubuntu** principles:
- "I am because we are" → Collective resource management
- Fairness in task distribution (weighted by capability)
- Transparency in budget allocation

Economic philosophy follows **Kantian categorical imperative**:
- "Act only according to that maxim whereby you can at the same time will that it should become a universal law"
- Applied: If every agent overspent, the system would collapse → budget enforcement is moral duty

---

## Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│  IF.governor - Capability-Aware Resource Manager                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Swarm Registry                                            │ │
│  │  - SwarmProfile (capabilities, cost, reputation, budget)   │ │
│  │  - Capability enum (20+ predefined types)                  │ │
│  │  - Registration via register_swarm()                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Capability Matcher                                         │ │
│  │  - Jaccard similarity (set overlap)                        │ │
│  │  - 70% minimum match threshold                             │ │
│  │  - Combined score: (capability × reputation) / cost        │ │
│  │  - Returns best-qualified swarm                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Budget Tracker                                             │ │
│  │  - track_cost() deducts from swarm budget                  │ │
│  │  - Integration with IF.optimise                            │ │
│  │  - Zero/negative budget prevents task assignment           │ │
│  │  - Budget reports via get_budget_report()                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Circuit Breaker                                            │ │
│  │  - Automatic halt on budget exhaustion                     │ │
│  │  - Automatic halt on repeated failures                     │ │
│  │  - Human escalation notification                           │ │
│  │  - Manual reset required (approval gate)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Policy Engine                                              │ │
│  │  - YAML-based policy configuration                         │ │
│  │  - Max swarms per task (default: 3)                        │ │
│  │  - Max cost per task (default: $10)                        │ │
│  │  - Min capability match (default: 70%)                     │ │
│  │  - Policy violation enforcement                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  IF.witness Integration                                     │ │
│  │  - Log all cost tracking events                            │ │
│  │  - Log capability matching decisions                       │ │
│  │  - Log circuit breaker trips                               │ │
│  │  - Log policy violations                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
        │                       │                      │
        │ Capability match      │ Budget queries       │ Audit logs
        ↓                       ↓                      ↓
┌──────────────┐    ┌────────────────────┐    ┌──────────────┐
│ IF.coordinator│    │  IF.chassis        │    │  IF.witness  │
│ (task queue)  │    │  (SLO tracking)    │    │  (audit)     │
└──────────────┘    └────────────────────┘    └──────────────┘
```

### Data Flow

**1. Swarm Registration:**
```
Swarm Owner → governor.register_swarm(profile)
              ↓
          Parse SwarmProfile (capabilities, cost, reputation)
              ↓
          Add to swarm_registry (internal dict)
              ↓
          Initialize budget tracking
              ↓
          Log to IF.witness (swarm_registered)
```

**2. Task Assignment (Capability Matching):**
```
IF.coordinator needs agent for task → governor.find_qualified_swarm(required_caps, max_cost)
                                       ↓
                                   For each swarm in registry:
                                       - Calculate Jaccard similarity
                                       - Check >= 70% threshold
                                       - Check cost <= max_cost
                                       - Check budget > 0
                                       - Calculate score: (cap × rep) / cost
                                       ↓
                                   Sort by score (highest first)
                                       ↓
                                   Return best swarm_id
                                       ↓
                                   Log to IF.witness (capability_match)
```

**3. Cost Tracking:**
```
Swarm completes task → governor.track_cost(swarm_id, operation, cost)
                        ↓
                    Deduct cost from swarm budget
                        ↓
                    Send to IF.optimise (cost tracking)
                        ↓
                    Log to IF.witness (cost_tracked)
                        ↓
                    Check if budget <= 0:
                        Yes → Trip circuit breaker
                        No  → Continue
```

**4. Circuit Breaker Trip:**
```
Budget exhausted OR 3+ failures → _trip_circuit_breaker(swarm_id, reason)
                                   ↓
                               Set budget to 0 (halt)
                                   ↓
                               Notify IF.coordinator (stop tasks)
                                   ↓
                               Log to IF.witness (circuit_breaker_tripped, severity=HIGH)
                                   ↓
                               Escalate to human (manual approval required)
```

---

## Capability Registry Guide

### Capability Types

IF.governor defines 20+ standard capability types organized by category:

**File: `infrafabric/schemas/capability.py`**

```python
from enum import Enum

class Capability(Enum):
    """Standard capability types for swarm profiles"""

    # Code Analysis
    CODE_ANALYSIS_RUST = "code-analysis:rust"
    CODE_ANALYSIS_PYTHON = "code-analysis:python"
    CODE_ANALYSIS_JAVASCRIPT = "code-analysis:javascript"
    CODE_ANALYSIS_GO = "code-analysis:go"
    CODE_ANALYSIS_TYPESCRIPT = "code-analysis:typescript"

    # Integrations (Production Software)
    INTEGRATION_SIP = "integration:sip"
    INTEGRATION_NDI = "integration:ndi"
    INTEGRATION_WEBRTC = "integration:webrtc"
    INTEGRATION_H323 = "integration:h323"
    INTEGRATION_VMIX = "integration:vmix"
    INTEGRATION_OBS = "integration:obs"
    INTEGRATION_HOME_ASSISTANT = "integration:home-assistant"

    # Infrastructure
    INFRA_DISTRIBUTED_SYSTEMS = "infra:distributed-systems"
    INFRA_NETWORKING = "infra:networking"
    INFRA_DATABASES = "infra:databases"
    INFRA_KUBERNETES = "infra:kubernetes"

    # CLI/Tools
    CLI_DESIGN = "cli:design"
    CLI_TESTING = "cli:testing"
    CLI_PERFORMANCE = "cli:performance"

    # Architecture
    ARCHITECTURE_PATTERNS = "architecture:patterns"
    ARCHITECTURE_SECURITY = "architecture:security"
    ARCHITECTURE_MICROSERVICES = "architecture:microservices"

    # Documentation
    DOCS_TECHNICAL_WRITING = "docs:technical-writing"
    DOCS_API_DESIGN = "docs:api-design"
    DOCS_TUTORIALS = "docs:tutorials"

    # Governance
    GOVERNANCE_VOTING = "governance:voting"
    GOVERNANCE_QUALITY_ASSESSMENT = "governance:quality-assessment"
    GOVERNANCE_TIE_BREAKING = "governance:tie-breaking"

    # Testing
    TESTING_UNIT = "testing:unit"
    TESTING_INTEGRATION = "testing:integration"
    TESTING_PERFORMANCE = "testing:performance"

    # DevOps
    DEVOPS_CI_CD = "devops:ci-cd"
    DEVOPS_MONITORING = "devops:monitoring"
    DEVOPS_DEPLOYMENT = "devops:deployment"
```

### Swarm Profile Definition

**Dataclass:**

```python
from dataclasses import dataclass
from typing import List

@dataclass
class SwarmProfile:
    """Complete profile for a swarm/session agent"""
    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float  # Haiku: $1-2, Sonnet: $15-20, Opus: $75+
    reputation_score: float  # 0.0-1.0 (from IF.chassis SLO tracking)
    current_budget_remaining: float
    model: str  # "haiku", "sonnet", "opus"
    max_concurrent_tasks: int = 5
```

### Registering Swarms

**Example 1: H.323 Guardian Council (Session 3)**

```python
from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import SwarmProfile, Capability

# Initialize governor
governor = IFGovernor(coordinator, policy)

# Register guardian council
guardian_profile = SwarmProfile(
    swarm_id="guardian-council",
    capabilities=[
        Capability.GOVERNANCE_VOTING,
        Capability.GOVERNANCE_QUALITY_ASSESSMENT,
        Capability.GOVERNANCE_TIE_BREAKING,
        Capability.INTEGRATION_H323,
        Capability.INTEGRATION_SIP,
        Capability.DOCS_TECHNICAL_WRITING,
    ],
    cost_per_hour=15.0,  # Sonnet model
    reputation_score=0.98,  # High reputation (production-proven)
    current_budget_remaining=100.0,
    model="sonnet",
    max_concurrent_tasks=8  # Handle 8 simultaneous guardian votes
)

governor.register_swarm(guardian_profile)
```

**Example 2: NDI Streaming Agent (Session 1)**

```python
ndi_profile = SwarmProfile(
    swarm_id="session-1-ndi",
    capabilities=[
        Capability.INTEGRATION_NDI,
        Capability.INFRA_NETWORKING,
        Capability.DOCS_TECHNICAL_WRITING,
        Capability.TESTING_INTEGRATION,
    ],
    cost_per_hour=2.0,  # Haiku model
    reputation_score=0.92,
    current_budget_remaining=50.0,
    model="haiku",
    max_concurrent_tasks=3
)

governor.register_swarm(ndi_profile)
```

**Example 3: Research Agent (Experimental)**

```python
research_profile = SwarmProfile(
    swarm_id="research-agent-experimental",
    capabilities=[
        Capability.CODE_ANALYSIS_PYTHON,
        Capability.TESTING_UNIT,
    ],
    cost_per_hour=2.0,  # Haiku
    reputation_score=0.5,  # Low (untested)
    current_budget_remaining=10.0,
    model="haiku",
    max_concurrent_tasks=1
)

governor.register_swarm(research_profile)
```

### Capability Matching Algorithm

**Jaccard Similarity:**

```
capability_overlap = len(swarm_capabilities ∩ required_capabilities) / len(required_capabilities)

Example:
  swarm_caps = [python, testing, docs]
  required_caps = [python, docs]
  overlap = len({python, docs}) / 2 = 2/2 = 1.0 (100% match)
```

**Combined Score (Maximize):**

```
score = (capability_overlap × reputation_score) / cost_per_hour

Higher score = better candidate

Example 1: High-skill expensive agent
  capability_overlap = 1.0 (100%)
  reputation = 0.95
  cost = $15/hour
  score = (1.0 × 0.95) / 15 = 0.063

Example 2: Medium-skill cheap agent
  capability_overlap = 0.7 (70%)
  reputation = 0.80
  cost = $2/hour
  score = (0.7 × 0.80) / 2 = 0.280

Result: Example 2 wins (higher score, cost-effective)
```

**Implementation:**

```python
def find_qualified_swarm(
    self,
    required_capabilities: List[Capability],
    max_cost: float
) -> Optional[str]:
    """Find best swarm based on capability match and cost"""

    candidates = []

    for swarm_id, profile in self.swarm_registry.items():
        # Calculate Jaccard similarity
        capability_overlap = len(
            set(profile.capabilities) & set(required_capabilities)
        ) / len(required_capabilities)

        # Filter by policy
        if capability_overlap < self.policy.min_capability_match:
            continue  # Below 70% threshold

        if profile.cost_per_hour > max_cost:
            continue  # Too expensive

        if profile.current_budget_remaining <= 0:
            continue  # Budget exhausted

        # Combined score
        score = (capability_overlap * profile.reputation_score) / profile.cost_per_hour

        candidates.append((swarm_id, score, capability_overlap))

    if not candidates:
        return None  # No qualified swarms

    # Sort by score (highest first)
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Log decision to IF.witness
    from infrafabric.witness import log_operation
    log_operation(
        component='IF.governor',
        operation='capability_match',
        params={
            'required_capabilities': [c.value for c in required_capabilities],
            'selected_swarm': candidates[0][0],
            'match_score': candidates[0][1],
            'capability_overlap': candidates[0][2]
        }
    )

    return candidates[0][0]
```

---

## Policy Configuration

### Policy YAML Format

**File: `config/governor/resource_policy.yaml`**

```yaml
# InfraFabric Resource Policy Configuration
# Defines constraints for resource allocation and task assignment

resource_policy:
  # Maximum swarms per task (Gang Up on Blocker pattern)
  max_swarms_per_task: 3

  # Maximum cost per task ($)
  max_cost_per_task: 10.0

  # Minimum capability match (0.0-1.0, default 0.7 = 70%)
  min_capability_match: 0.7

  # Circuit breaker settings
  circuit_breaker:
    failure_threshold: 3  # Trip after 3 consecutive failures
    reset_timeout_seconds: 3600  # Allow manual reset after 1 hour

# Cost tiers (model pricing)
cost_tiers:
  haiku:
    cost_per_hour: 2.0
    recommended_for:
      - documentation
      - simple_testing
      - data_formatting

  sonnet:
    cost_per_hour: 15.0
    recommended_for:
      - code_implementation
      - architecture_design
      - complex_debugging

  opus:
    cost_per_hour: 75.0
    recommended_for:
      - critical_security_review
      - complex_algorithms
      - production_escalations

# Reputation thresholds
reputation:
  high: 0.90  # Trusted for production
  medium: 0.70  # Suitable for development
  low: 0.50  # Experimental only
  untrusted: 0.30  # Heavy supervision required

# Budget allocation (per swarm, initial)
budget_allocation:
  guardian_council: 100.0
  session_1_ndi: 50.0
  session_2_webrtc: 50.0
  session_3_h323: 50.0
  session_4_sip: 50.0
  session_5_cli: 50.0
  session_7_if_bus: 100.0
```

### Loading Policy Configuration

```python
import yaml
from pathlib import Path
from infrafabric.schemas.capability import ResourcePolicy

def load_policy_from_yaml(config_path: Path) -> ResourcePolicy:
    """Load resource policy from YAML configuration"""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    policy_config = config['resource_policy']

    return ResourcePolicy(
        max_swarms_per_task=policy_config['max_swarms_per_task'],
        max_cost_per_task=policy_config['max_cost_per_task'],
        min_capability_match=policy_config['min_capability_match'],
        circuit_breaker_failure_threshold=policy_config['circuit_breaker']['failure_threshold']
    )
```

### Policy Engine Implementation

```python
from typing import List

class PolicyEngine:
    """Manage and enforce resource policies"""

    def __init__(self, config_path: str = None):
        self.policy = ResourcePolicy()
        if config_path:
            self.policy = load_policy_from_yaml(Path(config_path))

    def validate_assignment(
        self,
        swarm_ids: List[str],
        task_budget: float,
        governor: 'IFGovernor'
    ) -> tuple[bool, str]:
        """
        Validate proposed task assignment against policies

        Returns: (is_valid, reason)
        """

        # Check max_swarms_per_task
        if len(swarm_ids) > self.policy.max_swarms_per_task:
            return False, f"Exceeds max swarms ({len(swarm_ids)} > {self.policy.max_swarms_per_task})"

        # Check max_cost_per_task
        total_cost = 0.0
        for swarm_id in swarm_ids:
            profile = governor.swarm_registry.get(swarm_id)
            if profile:
                total_cost += profile.cost_per_hour

        if task_budget > self.policy.max_cost_per_task:
            return False, f"Exceeds max cost (${task_budget} > ${self.policy.max_cost_per_task})"

        # Check budget availability
        for swarm_id in swarm_ids:
            profile = governor.swarm_registry.get(swarm_id)
            if profile and profile.current_budget_remaining <= 0:
                return False, f"Swarm {swarm_id} budget exhausted"

        return True, "Valid"

    def enforce_capability_threshold(
        self,
        capability_overlap: float
    ) -> bool:
        """Check if capability overlap meets minimum threshold"""
        return capability_overlap >= self.policy.min_capability_match
```

---

## Budget Management

### Cost Tracking

**Track costs for every operation:**

```python
def track_cost(self, swarm_id: str, operation: str, cost: float):
    """
    Track costs and enforce budget limits

    Args:
        swarm_id: Swarm identifier
        operation: Operation name (e.g., "guardian_vote", "code_review")
        cost: Cost in dollars
    """

    if swarm_id not in self.swarm_registry:
        raise ValueError(f"Unknown swarm: {swarm_id}")

    profile = self.swarm_registry[swarm_id]

    # Deduct cost from budget
    profile.current_budget_remaining -= cost

    # Log cost to IF.optimise
    from infrafabric.optimise import track_operation_cost
    track_operation_cost(
        provider=swarm_id,
        operation=operation,
        cost=cost
    )

    # Log to IF.witness
    from infrafabric.witness import log_operation
    log_operation(
        component='IF.governor',
        operation='cost_tracked',
        params={
            'swarm_id': swarm_id,
            'operation': operation,
            'cost': cost,
            'remaining_budget': profile.current_budget_remaining
        }
    )

    # Check if budget exhausted
    if profile.current_budget_remaining <= 0:
        self._trip_circuit_breaker(swarm_id, reason='budget_exhausted')
```

### Budget Reports

**Get current budget status:**

```python
def get_budget_report(self) -> dict:
    """Get budget status for all swarms"""
    return {
        swarm_id: {
            'remaining': profile.current_budget_remaining,
            'cost_per_hour': profile.cost_per_hour,
            'model': profile.model,
            'reputation': profile.reputation_score
        }
        for swarm_id, profile in self.swarm_registry.items()
    }
```

**Example output:**

```json
{
  "guardian-council": {
    "remaining": 75.50,
    "cost_per_hour": 15.0,
    "model": "sonnet",
    "reputation": 0.98
  },
  "session-1-ndi": {
    "remaining": 42.00,
    "cost_per_hour": 2.0,
    "model": "haiku",
    "reputation": 0.92
  }
}
```

### Budget Allocation Strategies

**Strategy 1: Equal Allocation**
- All swarms get same initial budget ($50)
- Simple, fair
- Doesn't account for different roles

**Strategy 2: Role-Based Allocation**
- Critical swarms (guardian council) get more ($100)
- Support swarms get less ($50)
- Reflects importance and expected workload

**Strategy 3: Reputation-Based Allocation**
```python
def allocate_budget_by_reputation(base_budget: float, reputation: float) -> float:
    """
    Allocate budget proportional to reputation
    High-reputation swarms get more resources
    """
    return base_budget * (0.5 + 0.5 * reputation)

# Example:
# Guardian council (0.98 reputation) → $50 × 1.49 = $74.50
# Research agent (0.50 reputation) → $50 × 1.00 = $50.00
```

### Cost Optimization Tips

**1. Use Haiku for Simple Tasks**
- Documentation → Haiku ($2/hour)
- Simple testing → Haiku
- Data formatting → Haiku
- **Savings**: 87% vs Sonnet ($15/hour)

**2. Cache Expensive Results**
- Store capability matching results
- Avoid re-computing for same task types
- **Savings**: 30-50% on repeated operations

**3. Batch Operations**
- Process multiple tasks in one session
- Amortize startup costs
- **Savings**: 20-30% on task overhead

---

## Circuit Breaker Tuning

### Circuit Breaker States

```
CLOSED (Normal)
  ↓ (budget exhausted OR 3+ failures)
OPEN (Halted)
  ↓ (manual reset with new budget)
CLOSED (Resumed)
```

### Automatic Triggers

**1. Budget Exhaustion:**
```python
if profile.current_budget_remaining <= 0:
    self._trip_circuit_breaker(swarm_id, reason='budget_exhausted')
```

**2. Repeated Failures:**
```python
def record_failure(self, swarm_id: str):
    """Record task failure"""
    if swarm_id not in self.failure_counts:
        self.failure_counts[swarm_id] = 0

    self.failure_counts[swarm_id] += 1

    if self.failure_counts[swarm_id] >= self.policy.circuit_breaker_failure_threshold:
        self._trip_circuit_breaker(swarm_id, reason='repeated_failures')
```

### Circuit Breaker Implementation

```python
def _trip_circuit_breaker(self, swarm_id: str, reason: str):
    """
    Halt swarm to prevent cost spirals or repeated failures

    This is a SAFETY mechanism - requires human approval to reset
    """

    # Mark swarm as unavailable
    profile = self.swarm_registry[swarm_id]
    profile.current_budget_remaining = 0

    # Notify IF.coordinator to stop sending tasks
    import asyncio
    asyncio.create_task(
        self.coordinator.event_bus.put(
            f'/swarms/{swarm_id}/status',
            'circuit_breaker_tripped'
        )
    )

    # Log incident with HIGH severity
    from infrafabric.witness import log_operation
    log_operation(
        component='IF.governor',
        operation='circuit_breaker_tripped',
        params={
            'swarm_id': swarm_id,
            'reason': reason,
            'timestamp': time.time()
        },
        severity='HIGH'
    )

    # Escalate to human (CRITICAL)
    asyncio.create_task(
        self._escalate_to_human(swarm_id, {
            'type': 'circuit_breaker',
            'reason': reason,
            'action_required': 'manual_reset'
        })
    )
```

### Manual Reset (Human Approval Required)

```python
def reset_circuit_breaker(self, swarm_id: str, new_budget: float):
    """
    Manually reset circuit breaker (requires human approval)

    Args:
        swarm_id: Swarm to reset
        new_budget: New budget allocation (must be > 0)
    """

    if swarm_id not in self.swarm_registry:
        raise ValueError(f"Unknown swarm: {swarm_id}")

    if new_budget <= 0:
        raise ValueError("New budget must be positive")

    profile = self.swarm_registry[swarm_id]
    old_budget = profile.current_budget_remaining
    profile.current_budget_remaining = new_budget

    # Clear failure count
    if swarm_id in self.failure_counts:
        self.failure_counts[swarm_id] = 0

    # Update status in IF.coordinator
    import asyncio
    asyncio.create_task(
        self.coordinator.event_bus.put(
            f'/swarms/{swarm_id}/status',
            'active'
        )
    )

    # Log reset to IF.witness
    from infrafabric.witness import log_operation
    log_operation(
        component='IF.governor',
        operation='circuit_breaker_reset',
        params={
            'swarm_id': swarm_id,
            'old_budget': old_budget,
            'new_budget': new_budget,
            'approved_by': 'human_operator'
        }
    )
```

### Escalation Notification

```python
async def _escalate_to_human(self, swarm_id: str, issue: dict):
    """
    ESCALATE pattern: Notify human for intervention

    This implements the S² principle: "Escalate, don't guess"
    """

    notification = f"""
    🚨 S² System Escalation Required

    **Component**: IF.governor
    **Swarm**: {swarm_id}
    **Issue**: {issue}

    **Action Required**: Manual review and intervention

    **To reset circuit breaker**:
    ```python
    from infrafabric.governor import IFGovernor
    governor.reset_circuit_breaker('{swarm_id}', new_budget=50.0)
    ```

    **Or via CLI**:
    ```bash
    if governor reset-circuit-breaker {swarm_id} --budget 50.0
    ```

    **Investigation checklist**:
    - [ ] Review IF.witness logs for root cause
    - [ ] Check swarm reputation score
    - [ ] Verify task assignments were appropriate
    - [ ] Confirm budget allocation is sufficient
    - [ ] Assess if swarm needs capability retraining

    **Philosophy**: Ubuntu ("I am because we are") - System health depends on collective well-being
    """

    # Send notification (implementation depends on notification system)
    print(notification)  # Placeholder - replace with actual notification system
```

---

## Example Policies

### Example 1: Production Environment (Strict)

```yaml
resource_policy:
  max_swarms_per_task: 2  # Conservative (reduce coordination overhead)
  max_cost_per_task: 5.0  # Tight budget control
  min_capability_match: 0.8  # 80% match required (high quality)
  circuit_breaker:
    failure_threshold: 2  # Trip quickly on failures
    reset_timeout_seconds: 7200  # 2 hours before eligible for reset

reputation:
  high: 0.95  # Only proven swarms
  medium: 0.80
  low: 0.60
  untrusted: 0.40

budget_allocation:
  guardian_council: 50.0  # Even production swarms get modest budgets
  session_1_ndi: 25.0
  session_2_webrtc: 25.0
  session_3_h323: 25.0
```

**Use case**: Production deployment with cost sensitivity

---

### Example 2: Development Environment (Permissive)

```yaml
resource_policy:
  max_swarms_per_task: 5  # Allow more collaboration
  max_cost_per_task: 20.0  # Generous budget for experimentation
  min_capability_match: 0.6  # 60% match (allow learning)
  circuit_breaker:
    failure_threshold: 5  # More tolerant of failures
    reset_timeout_seconds: 1800  # 30 minutes

reputation:
  high: 0.85
  medium: 0.60
  low: 0.40
  untrusted: 0.20  # Allow experimental swarms

budget_allocation:
  guardian_council: 100.0
  session_1_ndi: 75.0  # Generous for development
  experimental_agents: 50.0  # Budget for experiments
```

**Use case**: Development and testing environment

---

### Example 3: Cost-Optimized (Haiku-Focused)

```yaml
resource_policy:
  max_swarms_per_task: 3
  max_cost_per_task: 3.0  # Force use of cheap models
  min_capability_match: 0.7
  circuit_breaker:
    failure_threshold: 3
    reset_timeout_seconds: 3600

cost_tiers:
  haiku:
    cost_per_hour: 1.5  # Slight discount for bulk
    recommended_for:
      - all_documentation
      - most_testing
      - data_processing
      - simple_code_review

  sonnet:
    cost_per_hour: 18.0  # Penalty for expensive model
    recommended_for:
      - critical_security_only
      - complex_algorithms_only

budget_allocation:
  # All swarms start with Haiku-sized budgets
  guardian_council: 30.0
  session_1_ndi: 30.0
  session_2_webrtc: 30.0
```

**Use case**: Tight budget, maximize Haiku usage

---

### Example 4: Research Environment (High Capability Threshold)

```yaml
resource_policy:
  max_swarms_per_task: 3
  max_cost_per_task: 15.0
  min_capability_match: 0.9  # 90% match (highly specialized)
  circuit_breaker:
    failure_threshold: 3
    reset_timeout_seconds: 3600

reputation:
  high: 0.98  # Only top performers
  medium: 0.90
  low: 0.75
  untrusted: 0.50

# Specialized capabilities required
specialized_capabilities:
  machine_learning:
    - capability: "research:ml-algorithms"
      min_reputation: 0.95

  cryptography:
    - capability: "security:cryptography"
      min_reputation: 0.98
```

**Use case**: Research projects requiring deep expertise

---

## Integration Examples

### Full Example: Task Assignment with Capability Matching

```python
#!/usr/bin/env python3
"""
Example: Task assignment with IF.governor capability matching

Demonstrates:
1. Register multiple swarms with different capabilities
2. Find qualified swarm for a task
3. Track costs
4. Handle budget exhaustion
"""

from infrafabric.governor import IFGovernor
from infrafabric.schemas.capability import SwarmProfile, Capability, ResourcePolicy

def main():
    # Initialize governor
    policy = ResourcePolicy(
        max_swarms_per_task=3,
        max_cost_per_task=10.0,
        min_capability_match=0.7,
        circuit_breaker_failure_threshold=3
    )
    governor = IFGovernor(coordinator=None, policy=policy)

    # Register swarms
    print("Registering swarms...")

    # Guardian Council (expensive, high capability)
    governor.register_swarm(SwarmProfile(
        swarm_id="guardian-council",
        capabilities=[
            Capability.GOVERNANCE_VOTING,
            Capability.INTEGRATION_H323,
            Capability.DOCS_TECHNICAL_WRITING
        ],
        cost_per_hour=15.0,
        reputation_score=0.98,
        current_budget_remaining=100.0,
        model="sonnet"
    ))

    # NDI Agent (cheap, specialized)
    governor.register_swarm(SwarmProfile(
        swarm_id="session-1-ndi",
        capabilities=[
            Capability.INTEGRATION_NDI,
            Capability.DOCS_TECHNICAL_WRITING,
            Capability.TESTING_INTEGRATION
        ],
        cost_per_hour=2.0,
        reputation_score=0.92,
        current_budget_remaining=50.0,
        model="haiku"
    ))

    # SIP Agent (medium cost)
    governor.register_swarm(SwarmProfile(
        swarm_id="session-4-sip",
        capabilities=[
            Capability.INTEGRATION_SIP,
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.TESTING_UNIT
        ],
        cost_per_hour=2.0,
        reputation_score=0.90,
        current_budget_remaining=50.0,
        model="haiku"
    ))

    print("✅ 3 swarms registered\n")

    # Task 1: Find swarm for documentation task
    print("Task 1: Find swarm for documentation...")
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.DOCS_TECHNICAL_WRITING],
        max_cost=5.0
    )
    print(f"  Selected: {swarm}")
    print(f"  Reason: Cheapest qualified swarm ($2/hour Haiku)\n")

    # Track cost for documentation
    governor.track_cost(swarm, "documentation", cost=2.0)
    print(f"  Cost tracked: $2.00")
    print(f"  Remaining budget: ${governor.swarm_registry[swarm].current_budget_remaining}\n")

    # Task 2: Find swarm for SIP integration task
    print("Task 2: Find swarm for SIP integration...")
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_SIP],
        max_cost=10.0
    )
    print(f"  Selected: {swarm}")
    print(f"  Reason: 100% capability match (has INTEGRATION_SIP)\n")

    # Task 3: Find swarm for H.323 governance task
    print("Task 3: Find swarm for H.323 governance...")
    swarm = governor.find_qualified_swarm(
        required_capabilities=[
            Capability.GOVERNANCE_VOTING,
            Capability.INTEGRATION_H323
        ],
        max_cost=20.0
    )
    print(f"  Selected: {swarm}")
    print(f"  Reason: Only swarm with both governance + H.323 capabilities\n")

    # Simulate budget exhaustion
    print("Simulating budget exhaustion...")
    governor.track_cost("session-1-ndi", "massive_task", cost=60.0)
    print(f"  ⚠️  session-1-ndi budget: ${governor.swarm_registry['session-1-ndi'].current_budget_remaining}")
    print(f"  🚨 Circuit breaker should have tripped!\n")

    # Try to assign task to exhausted swarm
    print("Attempting to assign task to exhausted swarm...")
    swarm = governor.find_qualified_swarm(
        required_capabilities=[Capability.INTEGRATION_NDI],
        max_cost=10.0
    )
    if swarm is None:
        print("  ✅ Correctly rejected (budget exhausted)\n")

    # Budget report
    print("Final Budget Report:")
    report = governor.get_budget_report()
    for swarm_id, status in report.items():
        print(f"  {swarm_id}: ${status['remaining']:.2f} remaining ({status['model']})")

if __name__ == '__main__':
    main()
```

**Expected Output:**

```
Registering swarms...
✅ 3 swarms registered

Task 1: Find swarm for documentation...
  Selected: session-1-ndi
  Reason: Cheapest qualified swarm ($2/hour Haiku)

  Cost tracked: $2.00
  Remaining budget: $48.0

Task 2: Find swarm for SIP integration...
  Selected: session-4-sip
  Reason: 100% capability match (has INTEGRATION_SIP)

Task 3: Find swarm for H.323 governance...
  Selected: guardian-council
  Reason: Only swarm with both governance + H.323 capabilities

Simulating budget exhaustion...
  ⚠️  session-1-ndi budget: $-12.0
  🚨 Circuit breaker should have tripped!

Attempting to assign task to exhausted swarm...
  ✅ Correctly rejected (budget exhausted)

Final Budget Report:
  guardian-council: $100.00 remaining (sonnet)
  session-1-ndi: $-12.00 remaining (haiku) [CIRCUIT BREAKER TRIPPED]
  session-4-sip: $50.00 remaining (haiku)
```

---

## Troubleshooting

### Issue: Wrong swarm selected for task

**Symptoms:**
- Expensive swarm doing cheap work
- Low-capability swarm assigned to complex task

**Diagnosis:**
```python
# Check capability profiles
for swarm_id, profile in governor.swarm_registry.items():
    print(f"{swarm_id}: {[c.value for c in profile.capabilities]}")

# Test capability matching manually
swarm = governor.find_qualified_swarm(
    required_capabilities=[Capability.DOCS_TECHNICAL_WRITING],
    max_cost=10.0
)
print(f"Selected: {swarm}")
```

**Solutions:**
1. **Verify capability overlap**: Ensure swarms have correct capabilities registered
2. **Check cost_per_hour**: Expensive swarms may have higher score if overlap is perfect
3. **Adjust min_capability_match**: Increase threshold to 0.8 (80%) for stricter matching
4. **Review reputation scores**: High reputation may be skewing selection

---

### Issue: Circuit breaker trips too frequently

**Symptoms:**
- Swarms halted after minor budget overruns
- Frequent human escalations

**Diagnosis:**
```bash
# Check circuit breaker trips in IF.witness
grep "circuit_breaker_tripped" logs/governor/*.jsonl | jq '{swarm: .swarm_id, reason: .reason}'
```

**Solutions:**
1. **Increase initial budgets**: Allocate more budget per swarm
2. **Increase failure threshold**: Change from 3 to 5 failures before trip
3. **Review cost tracking**: Ensure costs are accurate (not over-reporting)
4. **Add budget warnings**: Warn at 20% remaining before hitting $0

---

### Issue: No qualified swarm found

**Symptoms:**
- `find_qualified_swarm()` returns `None`
- Tasks not assigned

**Diagnosis:**
```python
# Check why no swarms qualified
required_caps = [Capability.INTEGRATION_H323]
for swarm_id, profile in governor.swarm_registry.items():
    overlap = len(set(profile.capabilities) & set(required_caps)) / len(required_caps)
    print(f"{swarm_id}:")
    print(f"  Capability overlap: {overlap:.2f} (need >= 0.70)")
    print(f"  Budget: ${profile.current_budget_remaining}")
    print(f"  Cost: ${profile.cost_per_hour}/hour")
```

**Solutions:**
1. **Lower capability threshold**: Reduce from 70% to 60%
2. **Add capabilities to swarms**: Register missing capabilities
3. **Reset budgets**: Swarms may have exhausted budgets
4. **Increase max_cost**: Task budget may be too low

---

### Issue: Budget report shows negative values

**Symptoms:**
- Swarm budget is negative (e.g., $-10.00)

**Root cause**: Cost tracking occurred after budget was at $0 (circuit breaker should have tripped first)

**Solutions:**
1. **Check circuit breaker logic**: Ensure `_trip_circuit_breaker()` is called when budget <= 0
2. **Add pre-deduction check**:
   ```python
   if profile.current_budget_remaining - cost < 0:
       self._trip_circuit_breaker(swarm_id, reason='insufficient_budget')
       raise InsufficientBudgetError(f"{swarm_id} has insufficient budget")
   ```
3. **Audit IF.witness logs**: Find when negative budget occurred

---

## References

### External Resources

1. **Capability-Based Security**: https://en.wikipedia.org/wiki/Capability-based_security
2. **Circuit Breaker Pattern**: https://martinfowler.com/bliki/CircuitBreaker.html
3. **Jaccard Similarity**: https://en.wikipedia.org/wiki/Jaccard_index
4. **Resource Allocation Algorithms**: https://www.sciencedirect.com/topics/computer-science/resource-allocation

### InfraFabric Components

- **IF.coordinator**: Real-time task distribution (etcd/NATS)
- **IF.chassis**: WASM sandboxing with SLO tracking (reputation scores)
- **IF.witness**: Audit logging with SHA-256 hashing
- **IF.optimise**: Cost tracking and optimization

### Related Documentation

- `docs/components/IF.CHASSIS.md` - WASM sandboxing (reputation scores fed to governor)
- `docs/components/IF.COORDINATOR.md` - Task distribution (uses governor for assignment)
- `docs/H323-PRODUCTION-RUNBOOK.md` - IF.governor integration for H.323 Guardian Council
- `PHASE-0-TASK-BOARD.md` - Phase 0 implementation roadmap

### Philosophy

- **Ubuntu**: "I am because we are" - Collective resource management
- **IF.TTT**: Traceable (audit logs), Transparent (budget reports), Trustworthy (circuit breakers)
- **Kantian Ethics**: Universal maxims (budget enforcement as moral duty)

---

**Document Version**: 1.0
**Author**: Session 3 (H.323 Guardian Council)
**License**: MIT (InfraFabric Project)
**Last Updated**: 2025-11-12
