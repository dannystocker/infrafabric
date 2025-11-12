"""Capability registry schema for IF.governor

This module defines capability types and swarm profile data structures
for intelligent task assignment and resource management.

Philosophy: IF.ground (Wu Lun - 五倫)
- 君臣: IF.coordinator is authority for task state
- 夫婦: Capability complementarity (Haiku + Sonnet)
- 兄弟: Swarm cooperation based on capabilities

Part of Phase 0: Bug #2 (Cost Waste) fix
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json


class Capability(Enum):
    """Capability types for swarm specialization"""

    # Code Analysis
    CODE_ANALYSIS_RUST = "code-analysis:rust"
    CODE_ANALYSIS_PYTHON = "code-analysis:python"
    CODE_ANALYSIS_JAVASCRIPT = "code-analysis:javascript"
    CODE_ANALYSIS_GO = "code-analysis:go"
    CODE_ANALYSIS_TYPESCRIPT = "code-analysis:typescript"

    # Integrations
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
    INFRA_CLOUD = "infra:cloud"
    INFRA_KUBERNETES = "infra:kubernetes"
    INFRA_DOCKER = "infra:docker"

    # CLI/Tools
    CLI_DESIGN = "cli:design"
    CLI_TESTING = "cli:testing"
    CLI_AUTOMATION = "cli:automation"

    # Architecture
    ARCHITECTURE_PATTERNS = "architecture:patterns"
    ARCHITECTURE_SECURITY = "architecture:security"
    ARCHITECTURE_PERFORMANCE = "architecture:performance"

    # Documentation
    DOCS_TECHNICAL_WRITING = "docs:technical-writing"
    DOCS_API_DESIGN = "docs:api-design"
    DOCS_TUTORIALS = "docs:tutorials"

    # Testing
    TESTING_UNIT = "testing:unit"
    TESTING_INTEGRATION = "testing:integration"
    TESTING_SECURITY = "testing:security"
    TESTING_PERFORMANCE = "testing:performance"

    # Coordination
    COORDINATION_ORCHESTRATION = "coordination:orchestration"
    COORDINATION_MONITORING = "coordination:monitoring"


@dataclass
class SwarmProfile:
    """Profile for a swarm/session agent

    Attributes:
        swarm_id: Unique identifier for the swarm
        capabilities: List of capabilities this swarm possesses
        cost_per_hour: Operational cost in USD/hour
        reputation_score: Quality metric (0.0-1.0)
        current_budget_remaining: Available budget in USD
        model: AI model being used ("haiku", "sonnet", "opus")
        max_concurrent_tasks: Maximum parallel tasks
        metadata: Additional swarm-specific information
    """
    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float
    reputation_score: float = 1.0
    current_budget_remaining: float = 0.0
    model: str = "sonnet"
    max_concurrent_tasks: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'swarm_id': self.swarm_id,
            'capabilities': [c.value for c in self.capabilities],
            'cost_per_hour': self.cost_per_hour,
            'reputation_score': self.reputation_score,
            'current_budget_remaining': self.current_budget_remaining,
            'model': self.model,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmProfile':
        """Create from dictionary"""
        capabilities = [Capability(c) for c in data['capabilities']]
        return cls(
            swarm_id=data['swarm_id'],
            capabilities=capabilities,
            cost_per_hour=data['cost_per_hour'],
            reputation_score=data.get('reputation_score', 1.0),
            current_budget_remaining=data.get('current_budget_remaining', 0.0),
            model=data.get('model', 'sonnet'),
            max_concurrent_tasks=data.get('max_concurrent_tasks', 1),
            metadata=data.get('metadata', {}),
        )


@dataclass
class ResourcePolicy:
    """Policy constraints for resource allocation

    Attributes:
        max_swarms_per_task: Maximum swarms that can collaborate on one task
        max_cost_per_task: Maximum budget for a single task in USD
        min_capability_match: Minimum capability overlap (0.0-1.0)
        circuit_breaker_failure_threshold: Failures before circuit breaker trips
        enable_cost_tracking: Whether to track costs via IF.optimise
        enable_witness_logging: Whether to log operations via IF.witness
    """
    max_swarms_per_task: int = 3
    max_cost_per_task: float = 10.0
    min_capability_match: float = 0.7  # 70% match required
    circuit_breaker_failure_threshold: int = 3
    enable_cost_tracking: bool = True
    enable_witness_logging: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'max_swarms_per_task': self.max_swarms_per_task,
            'max_cost_per_task': self.max_cost_per_task,
            'min_capability_match': self.min_capability_match,
            'circuit_breaker_failure_threshold': self.circuit_breaker_failure_threshold,
            'enable_cost_tracking': self.enable_cost_tracking,
            'enable_witness_logging': self.enable_witness_logging,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourcePolicy':
        """Create from dictionary"""
        return cls(
            max_swarms_per_task=data.get('max_swarms_per_task', 3),
            max_cost_per_task=data.get('max_cost_per_task', 10.0),
            min_capability_match=data.get('min_capability_match', 0.7),
            circuit_breaker_failure_threshold=data.get('circuit_breaker_failure_threshold', 3),
            enable_cost_tracking=data.get('enable_cost_tracking', True),
            enable_witness_logging=data.get('enable_witness_logging', True),
        )


def validate_capability_manifest(manifest: Dict[str, Any]) -> bool:
    """Validate capability manifest JSON

    Args:
        manifest: Dictionary containing swarm capability manifest

    Returns:
        True if valid, False otherwise

    Example:
        >>> manifest = {
        ...     'swarm_id': 'session-7-ifbus',
        ...     'capabilities': ['code-analysis:python', 'infra:distributed-systems'],
        ...     'cost_per_hour': 15.0
        ... }
        >>> validate_capability_manifest(manifest)
        True
    """
    required_fields = ['swarm_id', 'capabilities', 'cost_per_hour']

    # Check required fields
    if not all(field in manifest for field in required_fields):
        return False

    # Validate swarm_id
    if not isinstance(manifest['swarm_id'], str) or not manifest['swarm_id']:
        return False

    # Validate capabilities
    if not isinstance(manifest['capabilities'], list):
        return False

    for cap in manifest['capabilities']:
        try:
            Capability(cap)
        except ValueError:
            return False

    # Validate cost_per_hour
    if not isinstance(manifest['cost_per_hour'], (int, float)) or manifest['cost_per_hour'] < 0:
        return False

    return True


# Utility functions for capability matching

def calculate_jaccard_similarity(
    required: List[Capability],
    available: List[Capability]
) -> float:
    """Calculate Jaccard similarity between two capability sets

    Jaccard similarity = |intersection| / |union|

    Args:
        required: Required capabilities for task
        available: Available capabilities from swarm

    Returns:
        Similarity score (0.0-1.0)
    """
    if not required:
        return 1.0  # No requirements means perfect match

    required_set = set(required)
    available_set = set(available)

    intersection = len(required_set & available_set)
    union = len(required_set | available_set)

    if union == 0:
        return 0.0

    return intersection / union


def calculate_capability_overlap(
    required: List[Capability],
    available: List[Capability]
) -> float:
    """Calculate capability overlap (percentage of required caps covered)

    This is more lenient than Jaccard similarity.
    Overlap = |intersection| / |required|

    Args:
        required: Required capabilities for task
        available: Available capabilities from swarm

    Returns:
        Overlap score (0.0-1.0)
    """
    if not required:
        return 1.0  # No requirements means perfect match

    required_set = set(required)
    available_set = set(available)

    intersection = len(required_set & available_set)

    return intersection / len(required_set)
