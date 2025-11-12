"""
Capability Registry Schema for IF.governor

This module defines the capability-based resource management schema
for the InfraFabric S² (Swarm of Swarms) architecture.

Components:
- Capability: Enum of 30+ standard capability types
- SwarmProfile: Complete profile for a swarm/session agent
- ResourcePolicy: Governance rules for resource allocation
- Validation logic for capability manifests

Author: Session 3 (H.323 Guardian Council)
Version: 1.0
Status: Phase 0 Development
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json
from pathlib import Path


class Capability(Enum):
    """
    Standard capability types for swarm profiles

    Organized by category:
    - Code Analysis: Language-specific code understanding
    - Integrations: Production software/protocol integrations
    - Infrastructure: Distributed systems and networking
    - CLI: Command-line interface design and testing
    - Architecture: System design patterns
    - Documentation: Technical writing and API design
    - Governance: Quality assessment and decision-making
    - Testing: Various testing methodologies
    - DevOps: CI/CD and deployment operations
    """

    # ==========================================
    # Code Analysis Capabilities
    # ==========================================
    CODE_ANALYSIS_RUST = "code-analysis:rust"
    CODE_ANALYSIS_PYTHON = "code-analysis:python"
    CODE_ANALYSIS_JAVASCRIPT = "code-analysis:javascript"
    CODE_ANALYSIS_GO = "code-analysis:go"
    CODE_ANALYSIS_TYPESCRIPT = "code-analysis:typescript"
    CODE_ANALYSIS_CPP = "code-analysis:cpp"
    CODE_ANALYSIS_JAVA = "code-analysis:java"

    # ==========================================
    # Integration Capabilities (Production Software)
    # ==========================================
    INTEGRATION_SIP = "integration:sip"
    INTEGRATION_NDI = "integration:ndi"
    INTEGRATION_WEBRTC = "integration:webrtc"
    INTEGRATION_H323 = "integration:h323"
    INTEGRATION_VMIX = "integration:vmix"
    INTEGRATION_OBS = "integration:obs"
    INTEGRATION_HOME_ASSISTANT = "integration:home-assistant"
    INTEGRATION_RTMP = "integration:rtmp"
    INTEGRATION_DANTE = "integration:dante"

    # ==========================================
    # Infrastructure Capabilities
    # ==========================================
    INFRA_DISTRIBUTED_SYSTEMS = "infra:distributed-systems"
    INFRA_NETWORKING = "infra:networking"
    INFRA_DATABASES = "infra:databases"
    INFRA_KUBERNETES = "infra:kubernetes"
    INFRA_DOCKER = "infra:docker"
    INFRA_CLOUD_AWS = "infra:cloud-aws"
    INFRA_CLOUD_AZURE = "infra:cloud-azure"
    INFRA_CLOUD_GCP = "infra:cloud-gcp"

    # ==========================================
    # CLI/Tools Capabilities
    # ==========================================
    CLI_DESIGN = "cli:design"
    CLI_TESTING = "cli:testing"
    CLI_PERFORMANCE = "cli:performance"
    CLI_UX = "cli:ux"

    # ==========================================
    # Architecture Capabilities
    # ==========================================
    ARCHITECTURE_PATTERNS = "architecture:patterns"
    ARCHITECTURE_SECURITY = "architecture:security"
    ARCHITECTURE_MICROSERVICES = "architecture:microservices"
    ARCHITECTURE_EVENT_DRIVEN = "architecture:event-driven"

    # ==========================================
    # Documentation Capabilities
    # ==========================================
    DOCS_TECHNICAL_WRITING = "docs:technical-writing"
    DOCS_API_DESIGN = "docs:api-design"
    DOCS_TUTORIALS = "docs:tutorials"
    DOCS_RUNBOOKS = "docs:runbooks"

    # ==========================================
    # Governance Capabilities
    # ==========================================
    GOVERNANCE_VOTING = "governance:voting"
    GOVERNANCE_QUALITY_ASSESSMENT = "governance:quality-assessment"
    GOVERNANCE_TIE_BREAKING = "governance:tie-breaking"
    GOVERNANCE_CONFLICT_RESOLUTION = "governance:conflict-resolution"

    # ==========================================
    # Testing Capabilities
    # ==========================================
    TESTING_UNIT = "testing:unit"
    TESTING_INTEGRATION = "testing:integration"
    TESTING_PERFORMANCE = "testing:performance"
    TESTING_SECURITY = "testing:security"
    TESTING_E2E = "testing:e2e"

    # ==========================================
    # DevOps Capabilities
    # ==========================================
    DEVOPS_CI_CD = "devops:ci-cd"
    DEVOPS_MONITORING = "devops:monitoring"
    DEVOPS_DEPLOYMENT = "devops:deployment"
    DEVOPS_INCIDENT_RESPONSE = "devops:incident-response"


@dataclass
class SwarmProfile:
    """
    Complete profile for a swarm/session agent

    This profile is used by IF.governor to match tasks to qualified swarms
    based on capabilities, cost, reputation, and budget.

    Attributes:
        swarm_id: Unique identifier for the swarm (e.g., "guardian-council")
        capabilities: List of Capability enum values this swarm possesses
        cost_per_hour: Hourly cost in USD (Haiku: $1-2, Sonnet: $15-20, Opus: $75+)
        reputation_score: Reputation score from 0.0 to 1.0 (from IF.chassis SLO tracking)
        current_budget_remaining: Remaining budget in USD
        model: AI model type ("haiku", "sonnet", "opus")
        max_concurrent_tasks: Maximum number of tasks this swarm can handle simultaneously
        description: Optional human-readable description of swarm purpose

    Example:
        >>> guardian_profile = SwarmProfile(
        ...     swarm_id="guardian-council",
        ...     capabilities=[
        ...         Capability.GOVERNANCE_VOTING,
        ...         Capability.INTEGRATION_H323,
        ...         Capability.DOCS_TECHNICAL_WRITING
        ...     ],
        ...     cost_per_hour=15.0,
        ...     reputation_score=0.98,
        ...     current_budget_remaining=100.0,
        ...     model="sonnet",
        ...     max_concurrent_tasks=8
        ... )
    """
    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float
    reputation_score: float
    current_budget_remaining: float
    model: str
    max_concurrent_tasks: int = 5
    description: Optional[str] = None

    def __post_init__(self):
        """Validate SwarmProfile after initialization"""
        # Validate swarm_id
        if not self.swarm_id or not isinstance(self.swarm_id, str):
            raise ValueError("swarm_id must be a non-empty string")

        # Validate capabilities
        if not isinstance(self.capabilities, list):
            raise ValueError("capabilities must be a list")
        if not all(isinstance(cap, Capability) for cap in self.capabilities):
            raise ValueError("All capabilities must be Capability enum values")
        if len(self.capabilities) == 0:
            raise ValueError("SwarmProfile must have at least one capability")

        # Validate cost_per_hour
        if not isinstance(self.cost_per_hour, (int, float)) or self.cost_per_hour < 0:
            raise ValueError("cost_per_hour must be a non-negative number")

        # Validate reputation_score
        if not isinstance(self.reputation_score, (int, float)):
            raise ValueError("reputation_score must be a number")
        if not 0.0 <= self.reputation_score <= 1.0:
            raise ValueError("reputation_score must be between 0.0 and 1.0")

        # Validate current_budget_remaining
        if not isinstance(self.current_budget_remaining, (int, float)):
            raise ValueError("current_budget_remaining must be a number")

        # Validate model
        if not isinstance(self.model, str):
            raise ValueError("model must be a string")
        valid_models = {"haiku", "sonnet", "opus", "claude-3-haiku", "claude-3-sonnet", "claude-3-opus"}
        if self.model.lower() not in valid_models:
            raise ValueError(f"model must be one of {valid_models}")

        # Validate max_concurrent_tasks
        if not isinstance(self.max_concurrent_tasks, int) or self.max_concurrent_tasks < 1:
            raise ValueError("max_concurrent_tasks must be a positive integer")

    def to_dict(self) -> Dict[str, Any]:
        """Convert SwarmProfile to dictionary for serialization"""
        return {
            "swarm_id": self.swarm_id,
            "capabilities": [cap.value for cap in self.capabilities],
            "cost_per_hour": self.cost_per_hour,
            "reputation_score": self.reputation_score,
            "current_budget_remaining": self.current_budget_remaining,
            "model": self.model,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmProfile':
        """Create SwarmProfile from dictionary"""
        # Convert capability strings back to enum values
        capabilities = [Capability(cap_str) for cap_str in data["capabilities"]]

        return cls(
            swarm_id=data["swarm_id"],
            capabilities=capabilities,
            cost_per_hour=data["cost_per_hour"],
            reputation_score=data["reputation_score"],
            current_budget_remaining=data["current_budget_remaining"],
            model=data["model"],
            max_concurrent_tasks=data.get("max_concurrent_tasks", 5),
            description=data.get("description")
        )


@dataclass
class ResourcePolicy:
    """
    Governance rules for resource allocation and task assignment

    This policy is enforced by IF.governor to prevent cost spirals,
    ensure quality task assignments, and maintain system stability.

    Attributes:
        max_swarms_per_task: Maximum number of swarms that can work on a single task
                             (implements "Gang Up on Blocker" pattern)
        max_cost_per_task: Maximum cost in USD for a single task
        min_capability_match: Minimum Jaccard similarity (0.0-1.0) for capability matching
                              Default 0.7 = 70% overlap required
        circuit_breaker_failure_threshold: Number of consecutive failures before tripping
                                            circuit breaker
        budget_warning_threshold: Percentage of budget remaining that triggers warning
                                   (e.g., 0.2 = warn at 20% remaining)

    Example:
        >>> policy = ResourcePolicy(
        ...     max_swarms_per_task=3,
        ...     max_cost_per_task=10.0,
        ...     min_capability_match=0.7,
        ...     circuit_breaker_failure_threshold=3
        ... )
    """
    max_swarms_per_task: int = 3
    max_cost_per_task: float = 10.0
    min_capability_match: float = 0.7
    circuit_breaker_failure_threshold: int = 3
    budget_warning_threshold: float = 0.2

    def __post_init__(self):
        """Validate ResourcePolicy after initialization"""
        # Validate max_swarms_per_task
        if not isinstance(self.max_swarms_per_task, int) or self.max_swarms_per_task < 1:
            raise ValueError("max_swarms_per_task must be a positive integer")

        # Validate max_cost_per_task
        if not isinstance(self.max_cost_per_task, (int, float)) or self.max_cost_per_task <= 0:
            raise ValueError("max_cost_per_task must be a positive number")

        # Validate min_capability_match
        if not isinstance(self.min_capability_match, (int, float)):
            raise ValueError("min_capability_match must be a number")
        if not 0.0 <= self.min_capability_match <= 1.0:
            raise ValueError("min_capability_match must be between 0.0 and 1.0")

        # Validate circuit_breaker_failure_threshold
        if not isinstance(self.circuit_breaker_failure_threshold, int) or \
           self.circuit_breaker_failure_threshold < 1:
            raise ValueError("circuit_breaker_failure_threshold must be a positive integer")

        # Validate budget_warning_threshold
        if not isinstance(self.budget_warning_threshold, (int, float)):
            raise ValueError("budget_warning_threshold must be a number")
        if not 0.0 <= self.budget_warning_threshold <= 1.0:
            raise ValueError("budget_warning_threshold must be between 0.0 and 1.0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert ResourcePolicy to dictionary for serialization"""
        return {
            "max_swarms_per_task": self.max_swarms_per_task,
            "max_cost_per_task": self.max_cost_per_task,
            "min_capability_match": self.min_capability_match,
            "circuit_breaker_failure_threshold": self.circuit_breaker_failure_threshold,
            "budget_warning_threshold": self.budget_warning_threshold
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourcePolicy':
        """Create ResourcePolicy from dictionary"""
        return cls(
            max_swarms_per_task=data.get("max_swarms_per_task", 3),
            max_cost_per_task=data.get("max_cost_per_task", 10.0),
            min_capability_match=data.get("min_capability_match", 0.7),
            circuit_breaker_failure_threshold=data.get("circuit_breaker_failure_threshold", 3),
            budget_warning_threshold=data.get("budget_warning_threshold", 0.2)
        )


# ==========================================
# Validation Functions
# ==========================================

def validate_capability_manifest(manifest_path: Path) -> bool:
    """
    Validate a capability manifest JSON file

    Expected format:
    {
        "swarm_id": "guardian-council",
        "capabilities": ["governance:voting", "integration:h323", "docs:technical-writing"],
        "cost_per_hour": 15.0,
        "reputation_score": 0.98,
        "current_budget_remaining": 100.0,
        "model": "sonnet",
        "max_concurrent_tasks": 8,
        "description": "H.323 Guardian Council"
    }

    Args:
        manifest_path: Path to JSON manifest file

    Returns:
        True if valid, raises ValidationError if invalid

    Raises:
        FileNotFoundError: If manifest file doesn't exist
        json.JSONDecodeError: If manifest is not valid JSON
        ValueError: If manifest schema is invalid
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

    with open(manifest_path, 'r') as f:
        data = json.load(f)

    # Validate by attempting to create SwarmProfile
    try:
        SwarmProfile.from_dict(data)
        return True
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid capability manifest: {e}")


def get_capability_by_value(value: str) -> Optional[Capability]:
    """
    Get Capability enum by its string value

    Args:
        value: Capability value string (e.g., "code-analysis:python")

    Returns:
        Capability enum value or None if not found

    Example:
        >>> cap = get_capability_by_value("integration:h323")
        >>> cap == Capability.INTEGRATION_H323
        True
    """
    try:
        return Capability(value)
    except ValueError:
        return None


def get_capabilities_by_category(category: str) -> List[Capability]:
    """
    Get all capabilities in a specific category

    Args:
        category: Category prefix (e.g., "code-analysis", "integration", "docs")

    Returns:
        List of Capability enum values in that category

    Example:
        >>> caps = get_capabilities_by_category("integration")
        >>> Capability.INTEGRATION_H323 in caps
        True
    """
    return [
        cap for cap in Capability
        if cap.value.startswith(f"{category}:")
    ]


def calculate_capability_overlap(
    swarm_capabilities: List[Capability],
    required_capabilities: List[Capability]
) -> float:
    """
    Calculate Jaccard similarity between swarm and required capabilities

    Formula: |swarm ∩ required| / |required|

    This is the core capability matching algorithm used by IF.governor.

    Args:
        swarm_capabilities: Capabilities the swarm possesses
        required_capabilities: Capabilities the task requires

    Returns:
        Overlap ratio from 0.0 to 1.0 (1.0 = perfect match)

    Example:
        >>> swarm_caps = [
        ...     Capability.CODE_ANALYSIS_PYTHON,
        ...     Capability.TESTING_UNIT,
        ...     Capability.DOCS_TECHNICAL_WRITING
        ... ]
        >>> required_caps = [
        ...     Capability.CODE_ANALYSIS_PYTHON,
        ...     Capability.DOCS_TECHNICAL_WRITING
        ... ]
        >>> overlap = calculate_capability_overlap(swarm_caps, required_caps)
        >>> overlap
        1.0
    """
    if not required_capabilities:
        return 0.0

    swarm_set = set(swarm_capabilities)
    required_set = set(required_capabilities)

    intersection = swarm_set & required_set

    return len(intersection) / len(required_set)
