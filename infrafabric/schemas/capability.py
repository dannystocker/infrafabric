"""Capability Registry Schema for IF.governor

This module defines capability types and swarm profile data structures
for capability-aware resource allocation in the InfraFabric S² system.

Philosophy:
- Wu Lun (五倫) 朋友: Capability-based matching creates peer relationships
- IF.ground Observable: All capabilities are explicitly declared and auditable
- IF.TTT Traceable: Swarm capabilities tracked through their lifecycle

Task: P0.2.1 - Create capability registry schema
Est: 1h (Haiku)
Session: 4 (SIP - External Expert Escalation)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import json


class Capability(Enum):
    """Capability types for swarm/session agents

    Capabilities enable IF.governor to perform smart task assignment
    with 70%+ match requirements for efficient resource utilization.

    Categories:
    - Code Analysis: Language-specific code review and analysis
    - Integrations: Protocol and system integrations
    - Infrastructure: Distributed systems and networking
    - CLI/Tools: Command-line interface and tooling
    - Architecture: Design patterns and security
    - Documentation: Technical writing and API design
    """

    # Code Analysis (Language-Specific)
    CODE_ANALYSIS_RUST = "code-analysis:rust"
    CODE_ANALYSIS_PYTHON = "code-analysis:python"
    CODE_ANALYSIS_JAVASCRIPT = "code-analysis:javascript"
    CODE_ANALYSIS_TYPESCRIPT = "code-analysis:typescript"
    CODE_ANALYSIS_GO = "code-analysis:go"
    CODE_ANALYSIS_CPP = "code-analysis:cpp"
    CODE_ANALYSIS_JAVA = "code-analysis:java"

    # Integrations (Protocols & Systems)
    INTEGRATION_SIP = "integration:sip"
    INTEGRATION_NDI = "integration:ndi"
    INTEGRATION_WEBRTC = "integration:webrtc"
    INTEGRATION_H323 = "integration:h323"
    INTEGRATION_RTSP = "integration:rtsp"
    INTEGRATION_MQTT = "integration:mqtt"
    INTEGRATION_GRPC = "integration:grpc"
    INTEGRATION_REST = "integration:rest"

    # Infrastructure
    INFRA_DISTRIBUTED_SYSTEMS = "infra:distributed-systems"
    INFRA_NETWORKING = "infra:networking"
    INFRA_KUBERNETES = "infra:kubernetes"
    INFRA_DOCKER = "infra:docker"
    INFRA_CLOUD = "infra:cloud"

    # CLI/Tools
    CLI_DESIGN = "cli:design"
    CLI_TESTING = "cli:testing"
    CLI_DEBUGGING = "cli:debugging"

    # Architecture
    ARCHITECTURE_PATTERNS = "architecture:patterns"
    ARCHITECTURE_SECURITY = "architecture:security"
    ARCHITECTURE_SCALABILITY = "architecture:scalability"
    ARCHITECTURE_PERFORMANCE = "architecture:performance"

    # Documentation
    DOCS_TECHNICAL_WRITING = "docs:technical-writing"
    DOCS_API_DESIGN = "docs:api-design"
    DOCS_TUTORIALS = "docs:tutorials"

    # Testing
    TESTING_UNIT = "testing:unit"
    TESTING_INTEGRATION = "testing:integration"
    TESTING_PERFORMANCE = "testing:performance"
    TESTING_SECURITY = "testing:security"

    # Database
    DATABASE_SQL = "database:sql"
    DATABASE_NOSQL = "database:nosql"
    DATABASE_TIMESERIES = "database:timeseries"

    # DevOps
    DEVOPS_CI_CD = "devops:ci-cd"
    DEVOPS_MONITORING = "devops:monitoring"
    DEVOPS_LOGGING = "devops:logging"

    # Security
    SECURITY_PENETRATION_TESTING = "security:penetration-testing"
    SECURITY_COMPLIANCE = "security:compliance"

    def __str__(self) -> str:
        """Return capability value for display"""
        return self.value

    @classmethod
    def from_string(cls, capability_str: str) -> Optional['Capability']:
        """Parse capability from string

        Args:
            capability_str: Capability string (e.g., "integration:sip")

        Returns:
            Capability enum value or None if invalid
        """
        try:
            return cls(capability_str)
        except ValueError:
            return None


@dataclass
class SwarmProfile:
    """Profile for a swarm/session agent

    Attributes:
        swarm_id: Unique identifier (e.g., "session-4-sip")
        capabilities: List of capabilities this swarm possesses
        cost_per_hour: Hourly cost in USD (Haiku: $1-2, Sonnet: $15-20)
        reputation_score: Reputation score 0.0-1.0 based on past performance
        current_budget_remaining: Remaining budget in USD
        model: Model type ("haiku", "sonnet", "opus")
        metadata: Optional additional metadata

    Example:
        >>> profile = SwarmProfile(
        ...     swarm_id="session-4-sip",
        ...     capabilities=[Capability.INTEGRATION_SIP, Capability.ARCHITECTURE_SECURITY],
        ...     cost_per_hour=2.0,
        ...     reputation_score=0.95,
        ...     current_budget_remaining=10.44,
        ...     model="haiku"
        ... )
    """
    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float  # USD per hour
    reputation_score: float  # 0.0-1.0
    current_budget_remaining: float  # USD
    model: str  # "haiku", "sonnet", "opus"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate swarm profile after initialization"""
        # Validate reputation score
        if not 0.0 <= self.reputation_score <= 1.0:
            raise ValueError(
                f"Reputation score must be 0.0-1.0, got {self.reputation_score}"
            )

        # Validate model
        valid_models = ["haiku", "sonnet", "opus"]
        if self.model not in valid_models:
            raise ValueError(
                f"Model must be one of {valid_models}, got {self.model}"
            )

        # Validate cost_per_hour is positive
        if self.cost_per_hour <= 0:
            raise ValueError(
                f"Cost per hour must be positive, got {self.cost_per_hour}"
            )

        # Validate capabilities is not empty
        if not self.capabilities:
            raise ValueError("Swarm must have at least one capability")

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization"""
        return {
            "swarm_id": self.swarm_id,
            "capabilities": [cap.value for cap in self.capabilities],
            "cost_per_hour": self.cost_per_hour,
            "reputation_score": self.reputation_score,
            "current_budget_remaining": self.current_budget_remaining,
            "model": self.model,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmProfile':
        """Create profile from dictionary

        Args:
            data: Dictionary containing profile fields

        Returns:
            SwarmProfile instance

        Raises:
            ValueError: If required fields missing or invalid
        """
        # Parse capabilities
        capabilities = []
        for cap_str in data.get("capabilities", []):
            cap = Capability.from_string(cap_str)
            if cap:
                capabilities.append(cap)

        return cls(
            swarm_id=data["swarm_id"],
            capabilities=capabilities,
            cost_per_hour=data["cost_per_hour"],
            reputation_score=data.get("reputation_score", 0.5),
            current_budget_remaining=data["current_budget_remaining"],
            model=data["model"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class ResourcePolicy:
    """Policy constraints for resource allocation

    Attributes:
        max_swarms_per_task: Maximum number of swarms that can work on one task
        max_cost_per_task: Maximum cost in USD per task
        min_capability_match: Minimum capability match score (0.0-1.0)
        circuit_breaker_failure_threshold: Failures before circuit breaker trips
        enable_budget_enforcement: Enable hard budget limits
        enable_reputation_scoring: Enable reputation-based matching

    Default Policy:
    - Max 3 swarms per task (prevents coordination overhead)
    - Max $10 per task (prevents cost spirals)
    - Min 70% capability match (ensures quality)
    - Circuit breaker after 3 failures

    Example:
        >>> policy = ResourcePolicy(
        ...     max_swarms_per_task=3,
        ...     max_cost_per_task=10.0,
        ...     min_capability_match=0.7
        ... )
    """
    max_swarms_per_task: int = 3
    max_cost_per_task: float = 10.0
    min_capability_match: float = 0.7  # 70% match required
    circuit_breaker_failure_threshold: int = 3
    enable_budget_enforcement: bool = True
    enable_reputation_scoring: bool = True

    def __post_init__(self):
        """Validate resource policy after initialization"""
        # Validate max_swarms_per_task
        if self.max_swarms_per_task < 1:
            raise ValueError(
                f"max_swarms_per_task must be >= 1, got {self.max_swarms_per_task}"
            )

        # Validate min_capability_match
        if not 0.0 <= self.min_capability_match <= 1.0:
            raise ValueError(
                f"min_capability_match must be 0.0-1.0, got {self.min_capability_match}"
            )

        # Validate max_cost_per_task
        if self.max_cost_per_task <= 0:
            raise ValueError(
                f"max_cost_per_task must be positive, got {self.max_cost_per_task}"
            )

        # Validate circuit_breaker_failure_threshold
        if self.circuit_breaker_failure_threshold < 1:
            raise ValueError(
                f"circuit_breaker_failure_threshold must be >= 1, got {self.circuit_breaker_failure_threshold}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary for serialization"""
        return {
            "max_swarms_per_task": self.max_swarms_per_task,
            "max_cost_per_task": self.max_cost_per_task,
            "min_capability_match": self.min_capability_match,
            "circuit_breaker_failure_threshold": self.circuit_breaker_failure_threshold,
            "enable_budget_enforcement": self.enable_budget_enforcement,
            "enable_reputation_scoring": self.enable_reputation_scoring,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourcePolicy':
        """Create policy from dictionary

        Args:
            data: Dictionary containing policy fields

        Returns:
            ResourcePolicy instance
        """
        return cls(
            max_swarms_per_task=data.get("max_swarms_per_task", 3),
            max_cost_per_task=data.get("max_cost_per_task", 10.0),
            min_capability_match=data.get("min_capability_match", 0.7),
            circuit_breaker_failure_threshold=data.get("circuit_breaker_failure_threshold", 3),
            enable_budget_enforcement=data.get("enable_budget_enforcement", True),
            enable_reputation_scoring=data.get("enable_reputation_scoring", True),
        )


def validate_capability_manifest(manifest: dict) -> tuple[bool, Optional[str]]:
    """Validate capability manifest JSON

    A valid manifest must contain:
    - swarm_id: Unique identifier
    - capabilities: List of capability strings
    - cost_per_hour: Positive float
    - current_budget_remaining: Float
    - model: One of ["haiku", "sonnet", "opus"]

    Args:
        manifest: Dictionary containing swarm manifest

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if manifest is valid
        - error_message: None if valid, otherwise description of validation error

    Example:
        >>> manifest = {
        ...     "swarm_id": "session-4-sip",
        ...     "capabilities": ["integration:sip"],
        ...     "cost_per_hour": 2.0,
        ...     "current_budget_remaining": 10.0,
        ...     "model": "haiku"
        ... }
        >>> valid, error = validate_capability_manifest(manifest)
        >>> assert valid
    """
    # Check required fields
    required_fields = [
        "swarm_id",
        "capabilities",
        "cost_per_hour",
        "current_budget_remaining",
        "model"
    ]

    for field in required_fields:
        if field not in manifest:
            return False, f"Missing required field: {field}"

    # Validate swarm_id
    if not isinstance(manifest["swarm_id"], str) or not manifest["swarm_id"]:
        return False, "swarm_id must be a non-empty string"

    # Validate capabilities
    if not isinstance(manifest["capabilities"], list):
        return False, "capabilities must be a list"

    if not manifest["capabilities"]:
        return False, "capabilities list cannot be empty"

    for cap in manifest["capabilities"]:
        if not isinstance(cap, str):
            return False, f"Invalid capability: {cap} (must be string)"

        # Check if capability exists in enum
        if Capability.from_string(cap) is None:
            return False, f"Unknown capability: {cap}"

    # Validate cost_per_hour
    try:
        cost = float(manifest["cost_per_hour"])
        if cost <= 0:
            return False, "cost_per_hour must be positive"
    except (ValueError, TypeError):
        return False, "cost_per_hour must be a number"

    # Validate current_budget_remaining
    try:
        float(manifest["current_budget_remaining"])
    except (ValueError, TypeError):
        return False, "current_budget_remaining must be a number"

    # Validate model
    valid_models = ["haiku", "sonnet", "opus"]
    if manifest["model"] not in valid_models:
        return False, f"model must be one of {valid_models}, got {manifest['model']}"

    # Validate reputation_score if present
    if "reputation_score" in manifest:
        try:
            score = float(manifest["reputation_score"])
            if not 0.0 <= score <= 1.0:
                return False, "reputation_score must be between 0.0 and 1.0"
        except (ValueError, TypeError):
            return False, "reputation_score must be a number"

    return True, None


def load_manifest_from_json(json_str: str) -> tuple[Optional[SwarmProfile], Optional[str]]:
    """Load swarm profile from JSON string

    Args:
        json_str: JSON string containing manifest

    Returns:
        Tuple of (profile, error_message)
        - profile: SwarmProfile instance if successful, None otherwise
        - error_message: None if successful, otherwise error description

    Example:
        >>> json_str = '{"swarm_id": "test", "capabilities": ["integration:sip"], ...}'
        >>> profile, error = load_manifest_from_json(json_str)
    """
    try:
        manifest = json.loads(json_str)
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"

    # Validate manifest
    valid, error = validate_capability_manifest(manifest)
    if not valid:
        return None, error

    # Create profile
    try:
        profile = SwarmProfile.from_dict(manifest)
        return profile, None
    except Exception as e:
        return None, f"Failed to create profile: {e}"


# Export public API
__all__ = [
    "Capability",
    "SwarmProfile",
    "ResourcePolicy",
    "validate_capability_manifest",
    "load_manifest_from_json",
]
