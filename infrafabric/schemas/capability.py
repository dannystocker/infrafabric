"""
Capability Registry Schema

Defines capability types, swarm profiles, and resource policies for IF.governor.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set
import json
import re


class Capability(Enum):
    """
    Capability taxonomy for InfraFabric swarms.

    Each capability represents a distinct skill or integration that a swarm
    can provide. Capabilities are used by IF.governor for:
    - Swarm matching (find qualified swarms for tasks)
    - Resource allocation (select best-fit swarms)
    - Cost optimization (prefer cheaper swarms when capable)
    """

    # ==================== Code Analysis ====================
    CODE_ANALYSIS_RUST = "code-analysis:rust"
    CODE_ANALYSIS_PYTHON = "code-analysis:python"
    CODE_ANALYSIS_JAVASCRIPT = "code-analysis:javascript"
    CODE_ANALYSIS_TYPESCRIPT = "code-analysis:typescript"
    CODE_ANALYSIS_GO = "code-analysis:go"
    CODE_ANALYSIS_JAVA = "code-analysis:java"
    CODE_ANALYSIS_CPP = "code-analysis:cpp"
    CODE_ANALYSIS_CSHARP = "code-analysis:csharp"

    # ==================== Testing ====================
    TESTING_UNIT = "testing:unit"
    TESTING_INTEGRATION = "testing:integration"
    TESTING_PERFORMANCE = "testing:performance"
    TESTING_SECURITY = "testing:security"

    # ==================== Integrations ====================
    INTEGRATION_SIP = "integration:sip"
    INTEGRATION_NDI = "integration:ndi"
    INTEGRATION_WEBRTC = "integration:webrtc"
    INTEGRATION_H323 = "integration:h323"
    INTEGRATION_REST_API = "integration:rest-api"
    INTEGRATION_GRAPHQL = "integration:graphql"
    INTEGRATION_GRPC = "integration:grpc"

    # ==================== Infrastructure ====================
    INFRA_DISTRIBUTED_SYSTEMS = "infra:distributed-systems"
    INFRA_NETWORKING = "infra:networking"
    INFRA_DATABASES = "infra:databases"
    INFRA_CLOUD_AWS = "infra:cloud-aws"
    INFRA_CLOUD_GCP = "infra:cloud-gcp"
    INFRA_CLOUD_AZURE = "infra:cloud-azure"
    INFRA_KUBERNETES = "infra:kubernetes"
    INFRA_DOCKER = "infra:docker"

    # ==================== CLI/Tools ====================
    CLI_DESIGN = "cli:design"
    CLI_TESTING = "cli:testing"
    CLI_UX = "cli:ux"

    # ==================== Architecture ====================
    ARCHITECTURE_PATTERNS = "architecture:patterns"
    ARCHITECTURE_SECURITY = "architecture:security"
    ARCHITECTURE_MICROSERVICES = "architecture:microservices"
    ARCHITECTURE_EVENT_DRIVEN = "architecture:event-driven"

    # ==================== Documentation ====================
    DOCS_TECHNICAL_WRITING = "docs:technical-writing"
    DOCS_API_DESIGN = "docs:api-design"
    DOCS_TUTORIALS = "docs:tutorials"

    # ==================== Security ====================
    SECURITY_AUDIT = "security:audit"
    SECURITY_PENTESTING = "security:pentesting"
    SECURITY_COMPLIANCE = "security:compliance"

    # ==================== Data ====================
    DATA_ETL = "data:etl"
    DATA_ANALYTICS = "data:analytics"
    DATA_ML_TRAINING = "data:ml-training"

    # ==================== DevOps ====================
    DEVOPS_CICD = "devops:cicd"
    DEVOPS_MONITORING = "devops:monitoring"
    DEVOPS_DEPLOYMENT = "devops:deployment"

    @classmethod
    def from_string(cls, value: str) -> 'Capability':
        """
        Parse capability from string value.

        Args:
            value: Capability string (e.g., "code-analysis:rust")

        Returns:
            Capability enum member

        Raises:
            ValueError: If capability string is invalid
        """
        try:
            return cls(value)
        except ValueError:
            raise ValueError(
                f"Invalid capability: {value}. "
                f"Must be one of: {', '.join(c.value for c in cls)}"
            )

    @classmethod
    def from_list(cls, values: List[str]) -> List['Capability']:
        """Parse list of capability strings into Capability enums."""
        return [cls.from_string(v) for v in values]

    @classmethod
    def to_string_list(cls, capabilities: List['Capability']) -> List[str]:
        """Convert list of Capability enums to string values."""
        return [c.value for c in capabilities]

    @classmethod
    def get_category(cls, capability: 'Capability') -> str:
        """
        Extract category from capability (e.g., "code-analysis" from "code-analysis:rust").

        Returns:
            Category prefix (part before colon)
        """
        return capability.value.split(':')[0]

    @classmethod
    def get_all_categories(cls) -> Set[str]:
        """Get set of all capability categories."""
        return {cls.get_category(cap) for cap in cls}


@dataclass
class SwarmProfile:
    """
    Profile descriptor for a swarm/session agent.

    SwarmProfiles are used by IF.governor to:
    - Match swarms to tasks (capability-based routing)
    - Track budget consumption (prevent overspend)
    - Monitor reputation (prefer reliable swarms)
    - Enforce resource policies (cost limits, max swarms)

    Attributes:
        swarm_id: Unique identifier for the swarm (e.g., "swarm-webrtc-001")
        capabilities: List of capabilities this swarm provides
        cost_per_hour: Hourly cost in USD (Haiku: $1-2, Sonnet: $15-20, Opus: $75)
        reputation_score: Trust score 0.0-1.0 (based on success rate, SLO compliance)
        current_budget_remaining: Remaining budget in USD (tracked by IF.governor)
        model: Model type powering this swarm ("haiku", "sonnet", "opus")
        metadata: Optional additional swarm metadata (tags, version, etc.)
    """

    swarm_id: str
    capabilities: List[Capability]
    cost_per_hour: float
    reputation_score: float = 1.0  # Start at 1.0 (perfect reputation)
    current_budget_remaining: float = 0.0  # Default: no budget allocated
    model: str = "haiku"  # Default to cost-efficient model
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate swarm profile fields."""
        # Validate swarm_id format
        if not re.match(r'^[a-z0-9\-]+$', self.swarm_id):
            raise ValueError(
                f"Invalid swarm_id: {self.swarm_id}. "
                "Must contain only lowercase letters, numbers, and hyphens."
            )

        # Validate capabilities list
        if not self.capabilities:
            raise ValueError("SwarmProfile must have at least one capability")

        if not all(isinstance(c, Capability) for c in self.capabilities):
            raise ValueError("All capabilities must be Capability enum members")

        # Validate cost_per_hour
        if self.cost_per_hour < 0:
            raise ValueError(f"cost_per_hour must be non-negative, got {self.cost_per_hour}")

        # Validate reputation_score range
        if not 0.0 <= self.reputation_score <= 1.0:
            raise ValueError(
                f"reputation_score must be between 0.0 and 1.0, got {self.reputation_score}"
            )

        # Validate current_budget_remaining
        if self.current_budget_remaining < 0:
            raise ValueError(
                f"current_budget_remaining must be non-negative, got {self.current_budget_remaining}"
            )

        # Validate model
        valid_models = {"haiku", "sonnet", "opus"}
        if self.model not in valid_models:
            raise ValueError(
                f"model must be one of {valid_models}, got {self.model}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert SwarmProfile to dictionary (for JSON serialization)."""
        data = asdict(self)
        # Convert Capability enums to strings
        data['capabilities'] = Capability.to_string_list(self.capabilities)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SwarmProfile':
        """Create SwarmProfile from dictionary."""
        # Convert capability strings to enums
        if 'capabilities' in data:
            data['capabilities'] = Capability.from_list(data['capabilities'])
        return cls(**data)

    def has_capability(self, capability: Capability) -> bool:
        """Check if swarm has a specific capability."""
        return capability in self.capabilities

    def has_capabilities(self, required: List[Capability]) -> bool:
        """Check if swarm has ALL required capabilities."""
        return all(cap in self.capabilities for cap in required)

    def get_capability_categories(self) -> Set[str]:
        """Get set of capability categories this swarm provides."""
        return {Capability.get_category(cap) for cap in self.capabilities}


@dataclass
class ResourcePolicy:
    """
    Resource allocation policy for IF.governor.

    ResourcePolicies define constraints on how IF.governor allocates swarms
    to tasks. These policies ensure:
    - Cost control (prevent budget overruns)
    - Quality assurance (require minimum capability match)
    - Resource limits (prevent swarm exhaustion)
    - Failure resilience (circuit breaker pattern)

    Attributes:
        max_swarms_per_task: Maximum swarms that can work on one task
        max_cost_per_task: Maximum cost allowed for one task (USD)
        min_capability_match: Minimum capability match score (0.0-1.0, typically 0.7)
        circuit_breaker_failure_threshold: Consecutive failures before circuit opens
        prefer_reputation: Prefer higher-reputation swarms (even if more expensive)
        allow_budget_overdraft: Allow swarms to exceed budget by this multiplier
    """

    max_swarms_per_task: int = 3
    max_cost_per_task: float = 10.0
    min_capability_match: float = 0.7  # 70% match required
    circuit_breaker_failure_threshold: int = 3
    prefer_reputation: bool = True
    allow_budget_overdraft: float = 1.1  # 10% overdraft allowed

    def __post_init__(self):
        """Validate resource policy fields."""
        if self.max_swarms_per_task < 1:
            raise ValueError("max_swarms_per_task must be at least 1")

        if self.max_cost_per_task <= 0:
            raise ValueError("max_cost_per_task must be positive")

        if not 0.0 <= self.min_capability_match <= 1.0:
            raise ValueError("min_capability_match must be between 0.0 and 1.0")

        if self.circuit_breaker_failure_threshold < 1:
            raise ValueError("circuit_breaker_failure_threshold must be at least 1")

        if self.allow_budget_overdraft < 1.0:
            raise ValueError("allow_budget_overdraft must be at least 1.0 (no overdraft)")


@dataclass
class CapabilityManifest:
    """
    Complete capability manifest for a swarm (JSON-serializable).

    This is the top-level structure for swarm capability declarations.
    Swarms provide this manifest to IF.governor during registration.

    Attributes:
        swarm_id: Unique swarm identifier
        capabilities: List of capability strings
        cost_per_hour: Hourly cost in USD
        model: Model type ("haiku", "sonnet", "opus")
        reputation_score: Optional reputation (defaults to 1.0)
        metadata: Optional additional metadata
    """

    swarm_id: str
    capabilities: List[str]  # String format for JSON compatibility
    cost_per_hour: float
    model: str = "haiku"
    reputation_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_swarm_profile(self) -> SwarmProfile:
        """Convert CapabilityManifest to SwarmProfile."""
        return SwarmProfile(
            swarm_id=self.swarm_id,
            capabilities=Capability.from_list(self.capabilities),
            cost_per_hour=self.cost_per_hour,
            reputation_score=self.reputation_score,
            current_budget_remaining=0.0,  # Budget allocated separately
            model=self.model,
            metadata=self.metadata,
        )

    @classmethod
    def from_swarm_profile(cls, profile: SwarmProfile) -> 'CapabilityManifest':
        """Create CapabilityManifest from SwarmProfile."""
        return cls(
            swarm_id=profile.swarm_id,
            capabilities=Capability.to_string_list(profile.capabilities),
            cost_per_hour=profile.cost_per_hour,
            model=profile.model,
            reputation_score=profile.reputation_score,
            metadata=profile.metadata,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapabilityManifest':
        """Create from dictionary."""
        return cls(**data)


def validate_capability_manifest(manifest: Dict[str, Any]) -> bool:
    """
    Validate capability manifest JSON structure.

    Args:
        manifest: Dictionary representing capability manifest

    Returns:
        True if valid, False otherwise

    Raises:
        ValueError: If manifest is invalid (with detailed error message)
    """
    # Check required fields
    required_fields = ['swarm_id', 'capabilities', 'cost_per_hour']
    missing = [f for f in required_fields if f not in manifest]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Validate swarm_id format
    swarm_id = manifest['swarm_id']
    if not isinstance(swarm_id, str) or not re.match(r'^[a-z0-9\-]+$', swarm_id):
        raise ValueError(
            f"Invalid swarm_id: {swarm_id}. "
            "Must contain only lowercase letters, numbers, and hyphens."
        )

    # Validate capabilities list
    capabilities = manifest['capabilities']
    if not isinstance(capabilities, list) or len(capabilities) == 0:
        raise ValueError("capabilities must be a non-empty list")

    # Validate each capability string
    for cap in capabilities:
        if not isinstance(cap, str):
            raise ValueError(f"Capability must be string, got {type(cap)}")
        try:
            Capability.from_string(cap)
        except ValueError as e:
            raise ValueError(f"Invalid capability: {e}")

    # Validate cost_per_hour
    cost_per_hour = manifest['cost_per_hour']
    if not isinstance(cost_per_hour, (int, float)) or cost_per_hour < 0:
        raise ValueError(
            f"cost_per_hour must be non-negative number, got {cost_per_hour}"
        )

    # Validate optional fields if present
    if 'model' in manifest:
        model = manifest['model']
        valid_models = {"haiku", "sonnet", "opus"}
        if model not in valid_models:
            raise ValueError(f"model must be one of {valid_models}, got {model}")

    if 'reputation_score' in manifest:
        reputation = manifest['reputation_score']
        if not isinstance(reputation, (int, float)) or not 0.0 <= reputation <= 1.0:
            raise ValueError(
                f"reputation_score must be between 0.0 and 1.0, got {reputation}"
            )

    if 'metadata' in manifest:
        if not isinstance(manifest['metadata'], dict):
            raise ValueError("metadata must be a dictionary")

    return True


def validate_swarm_profile(profile: SwarmProfile) -> bool:
    """
    Validate SwarmProfile instance.

    Args:
        profile: SwarmProfile to validate

    Returns:
        True if valid

    Raises:
        ValueError: If profile is invalid
    """
    if not isinstance(profile, SwarmProfile):
        raise ValueError(f"Expected SwarmProfile, got {type(profile)}")

    # SwarmProfile.__post_init__ already does validation
    # This function exists for explicit validation API
    return True


# JSON Schema definition for capability manifests (OpenAPI compatible)
CAPABILITY_MANIFEST_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "CapabilityManifest",
    "description": "Swarm capability manifest for IF.governor registration",
    "type": "object",
    "required": ["swarm_id", "capabilities", "cost_per_hour"],
    "properties": {
        "swarm_id": {
            "type": "string",
            "pattern": "^[a-z0-9\\-]+$",
            "description": "Unique swarm identifier (lowercase, alphanumeric, hyphens only)"
        },
        "capabilities": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": [c.value for c in Capability]
            },
            "minItems": 1,
            "description": "List of capabilities this swarm provides"
        },
        "cost_per_hour": {
            "type": "number",
            "minimum": 0,
            "description": "Hourly cost in USD"
        },
        "model": {
            "type": "string",
            "enum": ["haiku", "sonnet", "opus"],
            "default": "haiku",
            "description": "Model type powering this swarm"
        },
        "reputation_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "default": 1.0,
            "description": "Trust score based on success rate and SLO compliance"
        },
        "metadata": {
            "type": "object",
            "description": "Optional additional metadata",
            "additionalProperties": True
        }
    }
}
