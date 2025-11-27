#!/usr/bin/env python3
"""
IF.GOVERNANCE - Guardian Council
==================================

Role: Civic governance layer implementing multi-tiered safety checks and
balances for all S2 logistics operations.

Core Philosophy: "Check and Balance Before Dispatch"
  Every action is evaluated against entropy thresholds, destructive potential,
  and industry-specific safety constraints before being allowed to proceed.

Guardian Archetypes:
  1. Civic Guardian - Human review for high-uncertainty scenarios
  2. Contrarian Guardian - Two-person rule for destructive operations
  3. Ethical Guardian - "Do No Harm" overrides for critical verticals

Responsibilities:
  1. Entropy Assessment - Measure uncertainty and trigger human review
  2. Destructive Action Detection - Enforce two-person rule for kills/deletes
  3. Vertical-Specific Constraints - Apply industry safety overrides
  4. Audit Trail Generation - Log all governance decisions for IF.TTT compliance

Usage:
  from infrafabric.core.governance.guardian import GuardianCouncil, ActionContext
  from infrafabric.core.logistics.packet import Packet

  council = GuardianCouncil()

  action = ActionContext(
      primitive='matrix.route',
      vertical='acute-care-hospital',
      entropy_score=0.85,
      actor='agent-42',
      payload={'route': 'emergency-bypass'}
  )

  decision = council.evaluate(action)

  if decision.approved:
      dispatcher.dispatch_to_redis(key, packet)
  else:
      print(f"BLOCKED: {decision.reason}")
      # Escalate to human review or request co-signature
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import hashlib
import json
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class S2Primitive(Enum):
    """Core S2 primitives that require governance oversight"""
    MATRIX_ROUTE = "matrix.route"        # Routing/switching decisions
    PROCESS_KILL = "process.kill"        # Destructive process termination
    RESOURCE_ALLOCATE = "resource.allocate"  # Resource distribution
    SIGNAL_BROADCAST = "signal.broadcast"   # Mass communication
    PARCEL_DISPATCH = "packet.dispatch"    # Data logistics


class GuardianArchetype(Enum):
    """Guardian council member archetypes"""
    CIVIC = "civic"           # Human review for uncertainty
    CONTRARIAN = "contrarian" # Two-person rule enforcement
    ETHICAL = "ethical"       # Do-no-harm constraints
    TECHNICAL = "technical"   # Schema/type validation
    OPERATIONAL = "operational"  # Performance/resource limits


# =============================================================================
# WEIGHTED VOTING SYSTEM (From GUARDIAN_COUNCIL_ORIGINS.md)
# =============================================================================

class PersonaVote:
    """
    Weighted voting from 5 Guardian Personas.

    From GUARDIAN_COUNCIL_ORIGINS.md:
    - Civic Guardian (Weight: 1.5) - Human safety, public interest
    - Ethical Guardian (Weight: 1.3) - "Do No Harm", moral constraints
    - Technical Guardian (Weight: 1.0) - Schema validity, type safety
    - Operational Guardian (Weight: 1.0) - Performance, resource limits
    - Contrarian Guardian (Weight: 1.2) - Devil's advocate, two-person rule
    """
    PERSONA_WEIGHTS = {
        GuardianArchetype.CIVIC: 1.5,        # Highest: Human safety
        GuardianArchetype.ETHICAL: 1.3,      # High: Moral constraints
        GuardianArchetype.CONTRARIAN: 1.2,   # Medium-High: Skeptical oversight
        GuardianArchetype.TECHNICAL: 1.0,    # Baseline: Technical validity
        GuardianArchetype.OPERATIONAL: 1.0,  # Baseline: Performance
    }

    @classmethod
    def compute_weighted_score(cls, votes: Dict[GuardianArchetype, bool]) -> float:
        """
        Compute weighted approval score from persona votes.

        Args:
            votes: Dict mapping guardian archetype to True (approve) / False (reject)

        Returns:
            Weighted score (0.0-1.0) where 1.0 = unanimous approval
        """
        total_weight = sum(cls.PERSONA_WEIGHTS.values())
        weighted_sum = sum(
            cls.PERSONA_WEIGHTS[archetype] * (1.0 if approved else 0.0)
            for archetype, approved in votes.items()
            if archetype in cls.PERSONA_WEIGHTS
        )
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    @classmethod
    def requires_unanimous(cls, votes: Dict[GuardianArchetype, bool]) -> bool:
        """Check if any guardian vetoed (requires unanimous for approval)."""
        return all(votes.values())


# =============================================================================
# MOCK ENTROPY CALCULATOR (Standalone Testing)
# =============================================================================

class MockEntropyCalculator:
    """
    Mock entropy calculator for standalone testing.

    In production, this would be replaced by IF.yologuard's actual entropy
    analysis based on Shannon entropy, relationship mapping, and pattern detection.
    """

    # Intent-based entropy defaults
    INTENT_ENTROPY = {
        'rtl': 0.05,           # Return-to-launch is safe
        'return_to_launch': 0.05,
        'estop': 0.01,         # Emergency stop is safest
        'e-stop': 0.01,
        'emergency_stop': 0.01,
        'kill': 0.95,          # Kill commands are high-risk
        'destroy': 0.95,
        'arm': 0.6,            # Arming is moderate risk
        'disarm': 0.1,         # Disarming is low risk
        'navigate': 0.3,       # Navigation is moderate
        'hover': 0.1,          # Hover is low risk
        'land': 0.15,          # Landing is low risk
    }

    # Vertical-based entropy multipliers
    VERTICAL_MULTIPLIERS = {
        'drones': 1.2,         # Drones have higher baseline risk
        'robotics': 1.1,       # Robotics slightly elevated
        'energy': 1.3,         # Energy grid is critical
        'nuclear': 2.0,        # Nuclear requires highest scrutiny
        'medical': 1.4,        # Medical is life-critical
        'general': 1.0,        # Baseline
    }

    @classmethod
    def calculate(cls, intent: str, vertical: str = 'general') -> float:
        """
        Calculate mock entropy score for an intent + vertical combination.

        Args:
            intent: Action intent (e.g., 'rtl', 'kill', 'estop')
            vertical: Industry vertical (e.g., 'drones', 'energy')

        Returns:
            Entropy score (0.0-1.0) where 1.0 = maximum uncertainty/risk
        """
        base_entropy = cls.INTENT_ENTROPY.get(intent.lower(), 0.5)
        multiplier = cls.VERTICAL_MULTIPLIERS.get(vertical.lower(), 1.0)
        return min(1.0, base_entropy * multiplier)


class EntropyLevel(Enum):
    """Entropy/uncertainty classification thresholds"""
    LOW = "low"          # < 0.3 - Routine operations
    MEDIUM = "medium"    # 0.3-0.6 - Moderate uncertainty
    HIGH = "high"        # 0.6-0.8 - Requires human review
    CRITICAL = "critical"  # > 0.8 - Mandatory human intervention


class DecisionStatus(Enum):
    """Governance decision outcomes"""
    APPROVED = "approved"              # Action allowed to proceed
    BLOCKED = "blocked"                # Action denied
    REQUIRES_HUMAN_REVIEW = "requires_human_review"  # Escalate to human
    REQUIRES_CO_SIGNATURE = "requires_co_signature"  # Two-person rule


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ActionContext:
    """
    Comprehensive context for a proposed action requiring governance review.

    Attributes:
        primitive: S2 primitive being invoked (matrix.route, process.kill, etc.)
        vertical: Industry vertical (medical, energy, etc.)
        entropy_score: Uncertainty measure (0.0 = certain, 1.0 = maximum uncertainty)
        actor: Agent/user ID proposing the action
        payload: Action-specific data
        timestamp: When action was proposed (auto-generated)
        action_id: Unique identifier for audit trail (auto-generated)
    """
    primitive: str
    vertical: str
    entropy_score: float
    actor: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        """Validate entropy score range"""
        if not 0.0 <= self.entropy_score <= 1.0:
            raise ValueError(f"entropy_score must be in [0.0, 1.0], got {self.entropy_score}")


@dataclass
class GuardianDecision:
    """
    Guardian Council decision with full audit trail.

    Attributes:
        status: Decision outcome (approved, blocked, etc.)
        reason: Human-readable explanation
        guardians_triggered: Which guardian archetypes flagged this action
        required_actions: What must happen before proceeding (signatures, review, etc.)
        audit_hash: SHA256 hash of decision for tamper detection
        decision_id: Unique identifier linking to action_id
        decided_at: Timestamp of decision
    """
    status: DecisionStatus
    reason: str
    guardians_triggered: List[GuardianArchetype]
    required_actions: List[str] = field(default_factory=list)
    audit_hash: str = ""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decided_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def __post_init__(self):
        """Generate audit hash if not provided"""
        if not self.audit_hash:
            self.audit_hash = self._compute_audit_hash()

    def _compute_audit_hash(self) -> str:
        """Compute SHA256 hash of decision for IF.TTT compliance"""
        decision_data = {
            'decision_id': self.decision_id,
            'status': self.status.value,
            'reason': self.reason,
            'guardians': [g.value for g in self.guardians_triggered],
            'decided_at': self.decided_at
        }
        data_str = json.dumps(decision_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    @property
    def approved(self) -> bool:
        """Convenience property for quick approval check"""
        return self.status == DecisionStatus.APPROVED


# =============================================================================
# GUARDIAN COUNCIL
# =============================================================================

class GuardianCouncil:
    """
    Multi-archetype governance council implementing check-and-balance logic
    for S2 logistics operations.

    This class evaluates proposed actions against:
    1. Entropy thresholds (Civic Guardian)
    2. Destructive potential (Contrarian Guardian)
    3. Industry safety constraints (Ethical Guardian)
    4. Technical validity (Technical Guardian)
    5. Resource limits (Operational Guardian)

    Example:
        council = GuardianCouncil()

        # High-entropy medical action
        action = ActionContext(
            primitive='matrix.route',
            vertical='acute-care-hospital',
            entropy_score=0.85,
            actor='ai-agent-42',
            payload={'route': 'emergency-bypass'}
        )

        decision = council.evaluate(action)

        if not decision.approved:
            logger.warning(f"Action blocked: {decision.reason}")
            # Handle human review or co-signature requirement
    """

    # Critical verticals requiring "Do No Harm" constraints
    CRITICAL_VERTICALS: Set[str] = {
        'acute-care-hospital',
        'integrated-or',
        'ems-dispatch',
        'ng911-psap',
        'energy-grid',
        'water-utilities',
        'nuclear-power'  # Future vertical
    }

    # Destructive primitives requiring two-person rule
    DESTRUCTIVE_PRIMITIVES: Set[str] = {
        'process.kill',
        'resource.deallocate',
        'signal.terminate',
        'packet.purge'
    }

    # Drone-specific kill intents (require two-person rule regardless of primitive)
    DRONE_KILL_INTENTS: Set[str] = {
        'kill',
        'destroy',
        'terminate',
        'self-destruct',
        'crash'
    }

    # Verticals requiring rate limiting
    RATE_LIMITED_VERTICALS: Dict[str, int] = {
        'energy': 10,          # Max 10 ops/minute for energy grid
        'energy-grid': 10,
        'nuclear': 5,          # Max 5 ops/minute for nuclear
        'nuclear-power': 5,
        'water-utilities': 15, # Max 15 ops/minute for water
    }

    # Rate limit tracking (in-memory for demo; production would use Redis)
    _rate_limit_counters: Dict[str, List[float]] = {}

    # Entropy thresholds for escalation
    ENTROPY_THRESHOLD_HIGH = 0.6
    ENTROPY_THRESHOLD_CRITICAL = 0.8

    def __init__(self, enable_logging: bool = True):
        """
        Initialize Guardian Council.

        Args:
            enable_logging: Whether to log governance decisions (default: True)
        """
        self.enable_logging = enable_logging
        self._decision_history: List[GuardianDecision] = []

        if self.enable_logging:
            logger.info("GuardianCouncil initialized with IF.TTT compliance enabled")

    def evaluate(self, action: ActionContext) -> GuardianDecision:
        """
        Evaluate a proposed action through all guardian archetypes.

        This is the main entry point for governance checks. It sequentially
        applies all guardian rules and returns a decision with full audit trail.

        Args:
            action: ActionContext containing all relevant action details

        Returns:
            GuardianDecision with status and required actions

        Example:
            action = ActionContext(
                primitive='process.kill',
                vertical='energy-grid',
                entropy_score=0.4,
                actor='operator-alice',
                payload={'pid': 1234, 'reason': 'unresponsive'}
            )

            decision = council.evaluate(action)
            # Decision will require co-signature (two-person rule)
        """
        guardians_triggered: List[GuardianArchetype] = []
        required_actions: List[str] = []

        # --- CIVIC GUARDIAN: Entropy Assessment ---
        entropy_check = self._civic_guardian_check(action)
        if entropy_check['triggered']:
            guardians_triggered.append(GuardianArchetype.CIVIC)
            required_actions.extend(entropy_check['actions'])

        # --- CONTRARIAN GUARDIAN: Two-Person Rule ---
        destructive_check = self._contrarian_guardian_check(action)
        if destructive_check['triggered']:
            guardians_triggered.append(GuardianArchetype.CONTRARIAN)
            required_actions.extend(destructive_check['actions'])

        # --- ETHICAL GUARDIAN: Do No Harm Overrides ---
        ethical_check = self._ethical_guardian_check(action)
        if ethical_check['triggered']:
            guardians_triggered.append(GuardianArchetype.ETHICAL)
            required_actions.extend(ethical_check['actions'])

        # --- TECHNICAL GUARDIAN: Schema Validation ---
        technical_check = self._technical_guardian_check(action)
        if technical_check['triggered']:
            guardians_triggered.append(GuardianArchetype.TECHNICAL)
            required_actions.extend(technical_check['actions'])

        # --- OPERATIONAL GUARDIAN: Resource Limits ---
        operational_check = self._operational_guardian_check(action)
        if operational_check['triggered']:
            guardians_triggered.append(GuardianArchetype.OPERATIONAL)
            required_actions.extend(operational_check['actions'])

        # Determine final decision status
        decision = self._synthesize_decision(
            action=action,
            guardians=guardians_triggered,
            actions=required_actions
        )

        # Store in audit trail
        self._decision_history.append(decision)

        # Log if enabled
        if self.enable_logging:
            self._log_decision(action, decision)

        return decision

    # =========================================================================
    # GUARDIAN ARCHETYPE IMPLEMENTATIONS
    # =========================================================================

    def _civic_guardian_check(self, action: ActionContext) -> Dict[str, Any]:
        """
        Civic Guardian: Trigger human review for high-uncertainty scenarios.

        Logic:
        - entropy > 0.8 (CRITICAL) → Mandatory human review
        - entropy > 0.6 (HIGH) → Recommended human review
        - entropy ≤ 0.6 → Pass

        Args:
            action: ActionContext to evaluate

        Returns:
            Dict with 'triggered' bool and 'actions' list
        """
        if action.entropy_score >= self.ENTROPY_THRESHOLD_CRITICAL:
            return {
                'triggered': True,
                'actions': [
                    'MANDATORY: Human review required (entropy CRITICAL)',
                    f'Entropy score: {action.entropy_score:.2f} (threshold: {self.ENTROPY_THRESHOLD_CRITICAL})'
                ]
            }
        elif action.entropy_score >= self.ENTROPY_THRESHOLD_HIGH:
            return {
                'triggered': True,
                'actions': [
                    'RECOMMENDED: Human review (entropy HIGH)',
                    f'Entropy score: {action.entropy_score:.2f} (threshold: {self.ENTROPY_THRESHOLD_HIGH})'
                ]
            }

        return {'triggered': False, 'actions': []}

    def _contrarian_guardian_check(self, action: ActionContext) -> Dict[str, Any]:
        """
        Contrarian Guardian: Enforce two-person rule for destructive actions.

        Logic:
        - If primitive is in DESTRUCTIVE_PRIMITIVES → Require co-signature
        - If vertical == "drones" AND intent == "kill" → Require two-person rule
        - Otherwise → Pass

        Args:
            action: ActionContext to evaluate

        Returns:
            Dict with 'triggered' bool and 'actions' list
        """
        # Standard destructive primitive check
        if action.primitive in self.DESTRUCTIVE_PRIMITIVES:
            return {
                'triggered': True,
                'actions': [
                    f'MANDATORY: Two-person rule for {action.primitive}',
                    f'Requires co-signature from independent operator',
                    f'Current actor: {action.actor}'
                ]
            }

        # DRONE-SPECIFIC: Kill intents require two-person rule
        intent = str(action.payload.get('intent', '')).lower()
        if action.vertical.lower() == 'drones' and intent in self.DRONE_KILL_INTENTS:
            return {
                'triggered': True,
                'actions': [
                    f'MANDATORY: Two-person rule for drone "{intent}" command',
                    f'SAFETY CRITICAL: Drone kill/destroy requires co-signature',
                    f'Current actor: {action.actor}',
                    f'Vertical: {action.vertical}',
                    'Simulating two-person authorization required...'
                ]
            }

        return {'triggered': False, 'actions': []}

    def _ethical_guardian_check(self, action: ActionContext) -> Dict[str, Any]:
        """
        Ethical Guardian: Apply "Do No Harm" overrides for critical verticals.

        Logic:
        - If vertical is medical OR energy AND action is destructive → Block or escalate
        - If vertical is critical AND entropy > HIGH → Require medical/ops expert review
        - Otherwise → Pass

        Args:
            action: ActionContext to evaluate

        Returns:
            Dict with 'triggered' bool and 'actions' list
        """
        is_critical_vertical = action.vertical in self.CRITICAL_VERTICALS
        is_destructive = action.primitive in self.DESTRUCTIVE_PRIMITIVES

        # Critical vertical + destructive action = Strict oversight
        if is_critical_vertical and is_destructive:
            return {
                'triggered': True,
                'actions': [
                    f'MANDATORY: Do No Harm override for {action.vertical}',
                    f'Destructive action {action.primitive} requires domain expert approval',
                    f'Must verify: No patient/grid/public safety impact'
                ]
            }

        # Critical vertical + high entropy = Expert review
        if is_critical_vertical and action.entropy_score >= self.ENTROPY_THRESHOLD_HIGH:
            return {
                'triggered': True,
                'actions': [
                    f'RECOMMENDED: Domain expert review for {action.vertical}',
                    f'High entropy ({action.entropy_score:.2f}) in safety-critical vertical',
                    f'Consult: Medical director / Grid operator / Safety officer'
                ]
            }

        return {'triggered': False, 'actions': []}

    def _technical_guardian_check(self, action: ActionContext) -> Dict[str, Any]:
        """
        Technical Guardian: Validate payload schema and data types.

        Logic:
        - Check payload is not empty
        - Validate required fields exist
        - Future: JSON schema validation against vertical-specific schemas

        Args:
            action: ActionContext to evaluate

        Returns:
            Dict with 'triggered' bool and 'actions' list
        """
        if not action.payload:
            return {
                'triggered': True,
                'actions': [
                    'BLOCKED: Empty payload',
                    'All actions must include payload data for audit trail'
                ]
            }

        # Validate required fields based on primitive
        required_fields = {
            'process.kill': ['pid', 'reason'],
            'matrix.route': ['source', 'destination'],
            'resource.allocate': ['resource_id', 'amount'],
        }

        if action.primitive in required_fields:
            missing = [f for f in required_fields[action.primitive] if f not in action.payload]
            if missing:
                return {
                    'triggered': True,
                    'actions': [
                        f'BLOCKED: Missing required payload fields: {missing}',
                        f'Required for {action.primitive}: {required_fields[action.primitive]}'
                    ]
                }

        return {'triggered': False, 'actions': []}

    def _operational_guardian_check(self, action: ActionContext) -> Dict[str, Any]:
        """
        Operational Guardian: Enforce performance and resource limits.

        Logic:
        - Check if action exceeds resource quotas
        - Validate broadcast fanout limits
        - Rate limiting for critical verticals (energy, nuclear, water)

        Args:
            action: ActionContext to evaluate

        Returns:
            Dict with 'triggered' bool and 'actions' list
        """
        # Check broadcast fanout limits (prevent denial-of-service)
        if action.primitive == 'signal.broadcast':
            recipients = action.payload.get('recipients', [])
            MAX_FANOUT = 1000

            if len(recipients) > MAX_FANOUT:
                return {
                    'triggered': True,
                    'actions': [
                        f'BLOCKED: Broadcast fanout exceeds limit',
                        f'Attempted: {len(recipients)} recipients, Max: {MAX_FANOUT}',
                        'Split into multiple batches or request quota increase'
                    ]
                }

        # Check resource allocation limits
        if action.primitive == 'resource.allocate':
            amount = action.payload.get('amount', 0)
            MAX_ALLOCATION = 10000  # Example limit

            if amount > MAX_ALLOCATION:
                return {
                    'triggered': True,
                    'actions': [
                        f'BLOCKED: Resource allocation exceeds limit',
                        f'Requested: {amount}, Max: {MAX_ALLOCATION}',
                        'Requires capacity planning approval'
                    ]
                }

        # ENERGY/CRITICAL VERTICAL: Rate limiting
        rate_limit_check = self._check_rate_limit(action)
        if rate_limit_check['triggered']:
            return rate_limit_check

        return {'triggered': False, 'actions': []}

    def _check_rate_limit(self, action: ActionContext) -> Dict[str, Any]:
        """
        Check rate limiting for critical infrastructure verticals.

        Args:
            action: ActionContext to evaluate

        Returns:
            Dict with 'triggered' bool and 'actions' list
        """
        import time

        vertical = action.vertical.lower()

        if vertical not in self.RATE_LIMITED_VERTICALS:
            return {'triggered': False, 'actions': []}

        max_ops_per_minute = self.RATE_LIMITED_VERTICALS[vertical]
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window

        # Initialize counter if needed
        if vertical not in self._rate_limit_counters:
            self._rate_limit_counters[vertical] = []

        # Clean old entries (outside 1-minute window)
        self._rate_limit_counters[vertical] = [
            ts for ts in self._rate_limit_counters[vertical]
            if ts > window_start
        ]

        # Check if over limit
        if len(self._rate_limit_counters[vertical]) >= max_ops_per_minute:
            return {
                'triggered': True,
                'actions': [
                    f'BLOCKED: Rate limit exceeded for {vertical}',
                    f'Operations in last minute: {len(self._rate_limit_counters[vertical])}',
                    f'Maximum allowed: {max_ops_per_minute}/minute',
                    'Wait for rate limit window to reset or request quota increase'
                ]
            }

        # Record this operation
        self._rate_limit_counters[vertical].append(current_time)

        return {'triggered': False, 'actions': []}

    # =========================================================================
    # DECISION SYNTHESIS
    # =========================================================================

    def _synthesize_decision(
        self,
        action: ActionContext,
        guardians: List[GuardianArchetype],
        actions: List[str]
    ) -> GuardianDecision:
        """
        Synthesize final decision from all guardian checks.

        Priority order (most restrictive wins):
        1. BLOCKED - Technical/Operational hard blocks
        2. REQUIRES_CO_SIGNATURE - Two-person rule
        3. REQUIRES_HUMAN_REVIEW - Civic/Ethical escalations
        4. APPROVED - No guardians triggered

        Args:
            action: Original ActionContext
            guardians: List of triggered guardian archetypes
            actions: List of required action strings

        Returns:
            GuardianDecision with final status
        """
        if not guardians:
            # No guardians triggered - approve
            return GuardianDecision(
                status=DecisionStatus.APPROVED,
                reason=f"Action {action.primitive} approved (no guardian triggers)",
                guardians_triggered=[]
            )

        # Check for hard blocks (BLOCKED keyword in actions)
        blocked_actions = [a for a in actions if 'BLOCKED:' in a]
        if blocked_actions:
            return GuardianDecision(
                status=DecisionStatus.BLOCKED,
                reason=blocked_actions[0],  # First blocking reason
                guardians_triggered=guardians,
                required_actions=actions
            )

        # Check for two-person rule
        if GuardianArchetype.CONTRARIAN in guardians:
            return GuardianDecision(
                status=DecisionStatus.REQUIRES_CO_SIGNATURE,
                reason=f"Two-person rule required for {action.primitive}",
                guardians_triggered=guardians,
                required_actions=actions
            )

        # Check for human review requirements
        mandatory_review = any('MANDATORY: Human review' in a for a in actions)
        if mandatory_review or GuardianArchetype.CIVIC in guardians:
            return GuardianDecision(
                status=DecisionStatus.REQUIRES_HUMAN_REVIEW,
                reason=f"Human review required (entropy: {action.entropy_score:.2f})",
                guardians_triggered=guardians,
                required_actions=actions
            )

        # Soft recommendations - approve but log warnings
        return GuardianDecision(
            status=DecisionStatus.APPROVED,
            reason=f"Approved with recommendations: {len(actions)} advisory notes",
            guardians_triggered=guardians,
            required_actions=actions
        )

    # =========================================================================
    # AUDIT & LOGGING
    # =========================================================================

    def _log_decision(self, action: ActionContext, decision: GuardianDecision):
        """
        Log governance decision for IF.TTT compliance.

        Args:
            action: Original ActionContext
            decision: GuardianDecision result
        """
        log_entry = {
            'action_id': action.action_id,
            'decision_id': decision.decision_id,
            'primitive': action.primitive,
            'vertical': action.vertical,
            'actor': action.actor,
            'status': decision.status.value,
            'guardians': [g.value for g in decision.guardians_triggered],
            'audit_hash': decision.audit_hash,
            'timestamp': decision.decided_at
        }

        if decision.status == DecisionStatus.APPROVED:
            logger.info(f"✓ APPROVED: {json.dumps(log_entry)}")
        elif decision.status == DecisionStatus.BLOCKED:
            logger.warning(f"✗ BLOCKED: {json.dumps(log_entry)}")
        else:
            logger.warning(f"⚠ ESCALATION: {json.dumps(log_entry)}")

    def get_audit_trail(self, limit: int = 100) -> List[GuardianDecision]:
        """
        Retrieve recent governance decisions for audit.

        Args:
            limit: Maximum number of recent decisions to return

        Returns:
            List of GuardianDecision objects (most recent first)
        """
        return self._decision_history[-limit:]

    def export_audit_trail(self, filepath: str):
        """
        Export full audit trail to JSON file for IF.TTT compliance.

        Args:
            filepath: Path to output JSON file
        """
        audit_data = {
            'exported_at': datetime.utcnow().isoformat() + 'Z',
            'total_decisions': len(self._decision_history),
            'decisions': [
                {
                    'decision_id': d.decision_id,
                    'status': d.status.value,
                    'reason': d.reason,
                    'guardians': [g.value for g in d.guardians_triggered],
                    'audit_hash': d.audit_hash,
                    'decided_at': d.decided_at,
                    'required_actions': d.required_actions
                }
                for d in self._decision_history
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)

        logger.info(f"Exported {len(self._decision_history)} decisions to {filepath}")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_check(primitive: str, vertical: str, entropy: float, actor: str, payload: Dict) -> bool:
    """
    Convenience function for quick approval checks without full decision object.

    Args:
        primitive: S2 primitive (e.g., 'matrix.route')
        vertical: Industry vertical (e.g., 'acute-care-hospital')
        entropy: Uncertainty score (0.0-1.0)
        actor: Agent/user ID
        payload: Action payload

    Returns:
        True if approved, False otherwise

    Example:
        if quick_check('matrix.route', 'energy-grid', 0.4, 'agent-42', {...}):
            # Proceed with action
            pass
    """
    council = GuardianCouncil(enable_logging=False)
    action = ActionContext(
        primitive=primitive,
        vertical=vertical,
        entropy_score=entropy,
        actor=actor,
        payload=payload
    )
    decision = council.evaluate(action)
    return decision.approved


if __name__ == '__main__':
    # Demo: Show all guardian archetypes in action
    print("=== GuardianCouncil Demo ===\n")

    council = GuardianCouncil()

    # Test 1: High entropy medical action
    print("Test 1: High-entropy medical routing")
    action1 = ActionContext(
        primitive='matrix.route',
        vertical='acute-care-hospital',
        entropy_score=0.85,
        actor='ai-agent-42',
        payload={'source': 'triage', 'destination': 'icu-overflow'}
    )
    decision1 = council.evaluate(action1)
    print(f"Status: {decision1.status.value}")
    print(f"Reason: {decision1.reason}")
    print(f"Guardians: {[g.value for g in decision1.guardians_triggered]}\n")

    # Test 2: Destructive energy grid action
    print("Test 2: Process kill in energy grid")
    action2 = ActionContext(
        primitive='process.kill',
        vertical='energy-grid',
        entropy_score=0.4,
        actor='operator-alice',
        payload={'pid': 1234, 'reason': 'unresponsive load balancer'}
    )
    decision2 = council.evaluate(action2)
    print(f"Status: {decision2.status.value}")
    print(f"Reason: {decision2.reason}")
    print(f"Guardians: {[g.value for g in decision2.guardians_triggered]}\n")

    # Test 3: Routine low-entropy operation
    print("Test 3: Routine resource allocation")
    action3 = ActionContext(
        primitive='resource.allocate',
        vertical='fleet-telematics',
        entropy_score=0.2,
        actor='system-scheduler',
        payload={'resource_id': 'cpu-pool-3', 'amount': 500}
    )
    decision3 = council.evaluate(action3)
    print(f"Status: {decision3.status.value}")
    print(f"Reason: {decision3.reason}")
    print(f"Approved: {decision3.approved}\n")

    print(f"Total decisions in audit trail: {len(council.get_audit_trail())}")
