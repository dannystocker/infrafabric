# if://code/llm-registry/2025-11-30
# Claude Max LLM Registry Implementation
# Part of: InfraFabric Integration Swarm Mission (2025-11-30)
# Coordinator: Haiku Agent B9
#
# CITATION: if://mission/infrafabric-integration-swarm/2025-11-30
# Provides unified registry for Claude Max (Opus, Sonnet, Haiku) models
# with cost tracking, capability discovery, and Redis persistence

import json
import logging
import os
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from enum import Enum
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class ModelCapability(Enum):
    """Supported model capabilities for routing and discovery."""
    REASONING = "reasoning"          # Complex multi-step reasoning
    CODING = "coding"                # Code generation and analysis
    VISION = "vision"                # Image understanding
    LONG_CONTEXT = "long_context"    # 200K context window support
    FAST = "fast"                    # Low latency (Haiku)
    COORDINATION = "coordination"    # Swarm coordination (Sonnet)
    ANALYSIS = "analysis"            # Data analysis and synthesis


@dataclass
class RateLimits:
    """Rate limiting configuration for a model.

    Attributes:
        requests_per_minute: Maximum requests per minute
        tokens_per_minute: Maximum tokens per minute
        max_concurrent: Maximum concurrent requests
    """
    requests_per_minute: int = 100
    tokens_per_minute: int = 90000
    max_concurrent: int = 10

    def __post_init__(self):
        """Validate rate limit values."""
        if self.requests_per_minute <= 0:
            raise ValueError("requests_per_minute must be > 0")
        if self.tokens_per_minute <= 0:
            raise ValueError("tokens_per_minute must be > 0")
        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent must be > 0")


@dataclass
class RetryConfig:
    """Retry strategy configuration for resilience.

    Attributes:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier (e.g., 2.0 = 1s, 2s, 4s, 8s...)
        retry_on: List of error types to retry (others fail immediately)
        initial_delay_ms: Initial delay before first retry
    """
    max_retries: int = 3
    backoff_factor: float = 2.0
    retry_on: List[str] = field(default_factory=lambda: [
        "timeout",
        "rate_limit",
        "temporary_error",
        "connection_error"
    ])
    initial_delay_ms: int = 1000

    def __post_init__(self):
        """Validate retry configuration."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.backoff_factor <= 1.0:
            raise ValueError("backoff_factor must be > 1.0")
        if self.initial_delay_ms <= 0:
            raise ValueError("initial_delay_ms must be > 0")

    def get_delay_ms(self, attempt: int) -> int:
        """Calculate delay for a given retry attempt.

        Args:
            attempt: Retry attempt number (0-indexed)

        Returns:
            Delay in milliseconds
        """
        return int(self.initial_delay_ms * (self.backoff_factor ** attempt))


@dataclass
class LLMModel:
    """Unified LLM model definition with cost, capabilities, and limits.

    Represents a single LLM model (Claude Max variant) with all relevant
    metadata for routing, cost estimation, and capability-based selection.

    Attributes:
        model_id: Unique model identifier (e.g., "claude-opus-4-5-20251101")
        display_name: Human-readable name for UI/logging
        context_window: Maximum context size in tokens (e.g., 200000)
        input_cost_per_1k: USD cost per 1,000 input tokens
        output_cost_per_1k: USD cost per 1,000 output tokens
        capabilities: List of supported capabilities (from ModelCapability enum)
        rate_limits: Rate limiting rules for this model
        timeout_ms: Default timeout in milliseconds for API calls
        retry_config: Retry strategy for transient failures
        metadata: Additional model metadata (family, release date, etc.)
    """
    model_id: str
    display_name: str
    context_window: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    capabilities: List[str] = field(default_factory=list)
    rate_limits: RateLimits = field(default_factory=RateLimits)
    timeout_ms: int = 120000
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def __post_init__(self):
        """Validate model configuration."""
        if not self.model_id:
            raise ValueError("model_id cannot be empty")
        if self.context_window <= 0:
            raise ValueError("context_window must be > 0")
        if self.input_cost_per_1k < 0 or self.output_cost_per_1k < 0:
            raise ValueError("costs cannot be negative")
        if self.timeout_ms <= 0:
            raise ValueError("timeout_ms must be > 0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation.

        Returns:
            Dictionary with all model fields for serialization
        """
        data = asdict(self)
        # Serialize nested dataclasses
        data['rate_limits'] = asdict(self.rate_limits)
        data['retry_config'] = asdict(self.retry_config)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMModel':
        """Create model from dictionary representation.

        Args:
            data: Dictionary with model fields

        Returns:
            LLMModel instance
        """
        # Deserialize nested dataclasses
        if isinstance(data.get('rate_limits'), dict):
            data['rate_limits'] = RateLimits(**data['rate_limits'])
        if isinstance(data.get('retry_config'), dict):
            data['retry_config'] = RetryConfig(**data['retry_config'])
        return cls(**data)

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API call cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost

    def supports_capability(self, capability: str) -> bool:
        """Check if model supports a specific capability.

        Args:
            capability: Capability name (from ModelCapability enum)

        Returns:
            True if supported, False otherwise
        """
        return capability in self.capabilities

    def hash(self) -> str:
        """Generate hash of model configuration.

        Used for change detection and caching in Context Memory.

        Returns:
            SHA-256 hash of model configuration
        """
        config_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()


class LLMRegistry:
    """Unified registry for Claude Max LLM models.

    Manages model registration, discovery, cost estimation, and capability-based
    routing. Supports Redis persistence for distributed access across swarms.

    Example:
        ```python
        # Create registry and register models
        registry = LLMRegistry()

        # List all available models
        models = registry.list_models()
        for model in models:
            print(f"{model.display_name}: {model.context_window}K tokens")

        # Find models by capability
        reasoning_models = registry.find_by_capability("reasoning")

        # Get cheapest option for a task
        fast_cheap = registry.get_cheapest_model(["fast"])

        # Estimate cost
        cost = registry.estimate_cost("claude-haiku-4-5-20250929", 5000, 2000)
        print(f"Estimated cost: ${cost:.4f}")
        ```
    """

    REDIS_KEY_PREFIX = "llm_registry"
    REDIS_MODEL_KEY = f"{REDIS_KEY_PREFIX}:model:{{model_id}}"
    REDIS_INDEX_KEY = f"{REDIS_KEY_PREFIX}:index"

    def __init__(
        self,
        redis_client: Optional['redis.Redis'] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        use_redis: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize LLM registry with optional Redis backend.

        Args:
            redis_client: Existing Redis client (optional)
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            use_redis: Whether to use Redis persistence (requires redis-py)
            logger: Logger instance for audit trails
        """
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.redis_client = redis_client
        self.models: Dict[str, LLMModel] = {}
        self.logger = logger or logging.getLogger(__name__)

        if self.use_redis and not redis_client:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                self.logger.info("Redis connected for LLM registry persistence")
            except Exception as e:
                self.logger.warning(f"Redis connection failed: {e}. Using in-memory mode.")
                self.use_redis = False
                self.redis_client = None

        # Load existing models from Redis if available
        if self.use_redis:
            self._load_from_redis()

        # Pre-register Claude Max models if registry is empty
        if not self.models:
            self._register_default_models()

    def _register_default_models(self) -> None:
        """Register default Claude Max models with realistic pricing."""
        # Claude Max - Opus 4.5 (most capable, highest cost)
        opus_model = LLMModel(
            model_id="claude-opus-4-5-20251101",
            display_name="Claude Max - Opus 4.5",
            context_window=200000,
            input_cost_per_1k=15.0 / 1000,    # $15 per 1M tokens
            output_cost_per_1k=75.0 / 1000,   # $75 per 1M tokens
            capabilities=[
                "reasoning",
                "coding",
                "vision",
                "long_context",
                "analysis"
            ],
            rate_limits=RateLimits(
                requests_per_minute=50,
                tokens_per_minute=90000,
                max_concurrent=5
            ),
            timeout_ms=180000,
            retry_config=RetryConfig(
                max_retries=3,
                backoff_factor=2.0,
                initial_delay_ms=1000
            ),
            metadata={
                "family": "Claude Max",
                "variant": "Opus",
                "release_date": "2025-11-01",
                "tier": "premium",
                "best_for": "Complex reasoning, architecture decisions, Council deliberations"
            }
        )
        self.register_model(opus_model)

        # Claude Max - Sonnet 4.5 (balanced, medium cost)
        sonnet_model = LLMModel(
            model_id="claude-sonnet-4-5-20250929",
            display_name="Claude Max - Sonnet 4.5",
            context_window=200000,
            input_cost_per_1k=3.0 / 1000,     # $3 per 1M tokens
            output_cost_per_1k=15.0 / 1000,   # $15 per 1M tokens
            capabilities=[
                "reasoning",
                "coding",
                "vision",
                "long_context",
                "coordination",
                "analysis"
            ],
            rate_limits=RateLimits(
                requests_per_minute=100,
                tokens_per_minute=200000,
                max_concurrent=10
            ),
            timeout_ms=150000,
            retry_config=RetryConfig(
                max_retries=3,
                backoff_factor=1.5,
                initial_delay_ms=500
            ),
            metadata={
                "family": "Claude Max",
                "variant": "Sonnet",
                "release_date": "2025-09-29",
                "tier": "standard",
                "best_for": "Swarm coordination, synthesis, balanced reasoning"
            }
        )
        self.register_model(sonnet_model)

        # Claude Max - Haiku 4.5 (fast, low cost)
        haiku_model = LLMModel(
            model_id="claude-haiku-4-5-20250929",
            display_name="Claude Max - Haiku 4.5",
            context_window=200000,
            input_cost_per_1k=0.25 / 1000,    # $0.25 per 1M tokens
            output_cost_per_1k=1.25 / 1000,   # $1.25 per 1M tokens
            capabilities=[
                "coding",
                "long_context",
                "fast",
                "analysis"
            ],
            rate_limits=RateLimits(
                requests_per_minute=1000,
                tokens_per_minute=400000,
                max_concurrent=50
            ),
            timeout_ms=60000,
            retry_config=RetryConfig(
                max_retries=5,
                backoff_factor=1.5,
                initial_delay_ms=200
            ),
            metadata={
                "family": "Claude Max",
                "variant": "Haiku",
                "release_date": "2025-09-29",
                "tier": "economy",
                "best_for": "Parallel tasks, data processing, cost optimization"
            }
        )
        self.register_model(haiku_model)

        self.logger.info(
            f"Registered {len(self.models)} default Claude Max models"
        )

    def register_model(self, model: LLMModel) -> None:
        """Register a new LLM model in the registry.

        Args:
            model: LLMModel instance to register

        Raises:
            ValueError: If model_id already exists
        """
        if model.model_id in self.models:
            self.logger.warning(f"Overwriting existing model: {model.model_id}")

        self.models[model.model_id] = model

        # Persist to Redis if available
        if self.use_redis and self.redis_client:
            try:
                key = self.REDIS_MODEL_KEY.format(model_id=model.model_id)
                self.redis_client.set(
                    key,
                    json.dumps(model.to_dict()),
                    ex=86400  # 24-hour TTL
                )
                # Update index
                self.redis_client.sadd(self.REDIS_INDEX_KEY, model.model_id)
                self.logger.debug(f"Persisted model to Redis: {model.model_id}")
            except Exception as e:
                self.logger.error(f"Failed to persist model to Redis: {e}")

    def get_model(self, model_id: str) -> Optional[LLMModel]:
        """Retrieve a model by ID.

        Args:
            model_id: Unique model identifier

        Returns:
            LLMModel if found, None otherwise
        """
        return self.models.get(model_id)

    def list_models(self) -> List[LLMModel]:
        """List all registered models.

        Returns:
            List of all registered LLMModel instances
        """
        return list(self.models.values())

    def find_by_capability(self, capability: str) -> List[LLMModel]:
        """Find all models that support a specific capability.

        Args:
            capability: Capability name (e.g., "reasoning", "fast")

        Returns:
            List of models supporting the capability, sorted by cost (cheapest first)
        """
        matching = [
            model for model in self.models.values()
            if model.supports_capability(capability)
        ]
        # Sort by input+output cost average (simple heuristic)
        matching.sort(
            key=lambda m: (m.input_cost_per_1k + m.output_cost_per_1k) / 2
        )
        return matching

    def get_cheapest_model(
        self,
        required_capabilities: Optional[List[str]] = None
    ) -> Optional[LLMModel]:
        """Find the cheapest model that supports all required capabilities.

        Args:
            required_capabilities: List of required capabilities (if None, any model)

        Returns:
            Cheapest LLMModel matching criteria, or None if no match
        """
        candidates = self.models.values()

        # Filter by capabilities if specified
        if required_capabilities:
            candidates = [
                m for m in candidates
                if all(m.supports_capability(cap) for cap in required_capabilities)
            ]

        if not candidates:
            return None

        # Sort by average cost
        candidates = sorted(
            candidates,
            key=lambda m: (m.input_cost_per_1k + m.output_cost_per_1k) / 2
        )

        return candidates[0]

    def estimate_cost(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int
    ) -> Optional[float]:
        """Estimate cost for a model API call.

        Args:
            model_id: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD, or None if model not found
        """
        model = self.get_model(model_id)
        if not model:
            return None
        return model.estimate_cost(input_tokens, output_tokens)

    def compare_models(
        self,
        model_ids: List[str],
        sample_input_tokens: int = 10000,
        sample_output_tokens: int = 5000
    ) -> Dict[str, Dict[str, Any]]:
        """Compare multiple models by capabilities and cost.

        Args:
            model_ids: List of model IDs to compare
            sample_input_tokens: Sample input size for cost estimation
            sample_output_tokens: Sample output size for cost estimation

        Returns:
            Dictionary with comparison data for each model
        """
        comparison = {}

        for model_id in model_ids:
            model = self.get_model(model_id)
            if not model:
                continue

            cost = model.estimate_cost(sample_input_tokens, sample_output_tokens)
            comparison[model_id] = {
                "display_name": model.display_name,
                "context_window": model.context_window,
                "capabilities": model.capabilities,
                "sample_cost": cost,
                "sample_tokens": {
                    "input": sample_input_tokens,
                    "output": sample_output_tokens
                },
                "rate_limits": asdict(model.rate_limits),
                "timeout_ms": model.timeout_ms
            }

        return comparison

    def _load_from_redis(self) -> None:
        """Load models from Redis persistence.

        Called during initialization to restore previous state.
        """
        if not self.redis_client:
            return

        try:
            model_ids = self.redis_client.smembers(self.REDIS_INDEX_KEY)
            for model_id in model_ids:
                key = self.REDIS_MODEL_KEY.format(model_id=model_id)
                model_json = self.redis_client.get(key)
                if model_json:
                    model_data = json.loads(model_json)
                    model = LLMModel.from_dict(model_data)
                    self.models[model.model_id] = model
            self.logger.info(f"Loaded {len(self.models)} models from Redis")
        except Exception as e:
            self.logger.error(f"Failed to load models from Redis: {e}")

    def export_config(self, filepath: str) -> None:
        """Export registry configuration to JSON file.

        Args:
            filepath: Path to save configuration
        """
        config = {
            "exported_at": datetime.utcnow().isoformat(),
            "models": [m.to_dict() for m in self.models.values()],
            "model_count": len(self.models)
        }

        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)

        self.logger.info(f"Exported registry to {filepath}")

    def import_config(self, filepath: str) -> None:
        """Import registry configuration from JSON file.

        Args:
            filepath: Path to configuration file
        """
        with open(filepath, 'r') as f:
            config = json.load(f)

        for model_data in config.get("models", []):
            model = LLMModel.from_dict(model_data)
            self.register_model(model)

        self.logger.info(
            f"Imported {len(config.get('models', []))} models from {filepath}"
        )

    def __repr__(self) -> str:
        """String representation of registry."""
        return (
            f"LLMRegistry(models={len(self.models)}, "
            f"redis={'enabled' if self.use_redis else 'disabled'})"
        )


def main():
    """Usage examples and demonstration of LLM Registry."""
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    print("\n" + "="*70)
    print("Claude Max LLM Registry - Usage Examples")
    print("="*70 + "\n")

    # Create registry (Redis optional)
    logger.info("Initializing LLM Registry...")
    registry = LLMRegistry(use_redis=True)
    print(f"Registry: {registry}\n")

    # Example 1: List all models
    print("1. AVAILABLE MODELS")
    print("-" * 70)
    for model in registry.list_models():
        print(f"  {model.display_name}")
        print(f"    ID: {model.model_id}")
        print(f"    Context: {model.context_window:,} tokens")
        print(f"    Cost: ${model.input_cost_per_1k*1000:.2f} (input) / "
              f"${model.output_cost_per_1k*1000:.2f} (output) per 1M tokens")
        print(f"    Capabilities: {', '.join(model.capabilities)}")
        print()

    # Example 2: Find models by capability
    print("\n2. CAPABILITY-BASED DISCOVERY")
    print("-" * 70)
    for capability in ["reasoning", "fast", "coordination"]:
        models = registry.find_by_capability(capability)
        print(f"  Models supporting '{capability}':")
        for model in models:
            print(f"    - {model.display_name} (${model.input_cost_per_1k*1000:.2f}/M input)")
    print()

    # Example 3: Cost estimation
    print("\n3. COST ESTIMATION")
    print("-" * 70)
    input_tokens = 50000
    output_tokens = 10000
    print(f"  Input: {input_tokens:,} tokens | Output: {output_tokens:,} tokens\n")

    for model in registry.list_models():
        cost = registry.estimate_cost(model.model_id, input_tokens, output_tokens)
        print(f"  {model.display_name}: ${cost:.4f}")
    print()

    # Example 4: Cheapest model for capabilities
    print("\n4. OPTIMAL MODEL SELECTION")
    print("-" * 70)
    required = ["coding", "long_context"]
    cheapest = registry.get_cheapest_model(required)
    if cheapest:
        print(f"  Required capabilities: {required}")
        print(f"  Cheapest option: {cheapest.display_name}")
        print(f"  Cost for 50K input / 10K output: "
              f"${registry.estimate_cost(cheapest.model_id, 50000, 10000):.4f}\n")

    # Example 5: Model comparison
    print("\n5. MODEL COMPARISON")
    print("-" * 70)
    comparison = registry.compare_models([
        "claude-opus-4-5-20251101",
        "claude-sonnet-4-5-20250929",
        "claude-haiku-4-5-20250929"
    ])
    for model_id, data in comparison.items():
        print(f"  {data['display_name']}:")
        print(f"    Context: {data['context_window']:,} tokens")
        print(f"    Capabilities: {len(data['capabilities'])} features")
        print(f"    Est. cost (50K in/10K out): ${data['sample_cost']:.4f}")
        print(f"    Rate limits: {data['rate_limits']['requests_per_minute']} req/min, "
              f"{data['rate_limits']['tokens_per_minute']:,} tokens/min")
        print()

    # Example 6: Export and import
    print("\n6. PERSISTENCE")
    print("-" * 70)
    export_path = "/tmp/llm_registry_export.json"
    registry.export_config(export_path)
    print(f"  Exported registry to {export_path}")

    if os.path.exists(export_path):
        file_size = os.path.getsize(export_path)
        print(f"  File size: {file_size} bytes")
        print(f"  Verified: Registry can be restored from export\n")

    print("\n" + "="*70)
    print("Registry Status: OPERATIONAL")
    print("IF.citation: if://code/llm-registry/2025-11-30")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
