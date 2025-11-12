"""
InfraFabric Configuration Management

Unified configuration system for all IF components with:
- YAML/TOML support
- Environment variable overrides
- Schema validation
- Sensible defaults
- Production-ready settings

Philosophy: IF.ground Principle 8 - Observability without fragility
Configuration should be explicit, validated, and fail-fast with helpful errors.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class ConfigError(Exception):
    """Configuration validation or loading error"""
    pass


class BackendType(Enum):
    """Event bus backend types"""
    ETCD = "etcd"
    NATS = "nats"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CoordinatorConfig:
    """IF.coordinator configuration"""
    # Event bus settings
    backend: str = "etcd"  # etcd or nats
    etcd_host: str = "localhost"
    etcd_port: int = 2379
    nats_host: str = "localhost"
    nats_port: int = 4222

    # Coordination settings
    task_claim_timeout_ms: int = 5000  # Max time for CAS operation
    heartbeat_interval_ms: int = 1000  # Swarm heartbeat frequency
    stale_task_threshold_ms: int = 30000  # When to reclaim stale tasks

    # Performance targets
    target_cas_latency_ms: int = 5  # Target for claim_task()
    target_pubsub_latency_ms: int = 10  # Target for task_broadcast()

    # Witness integration
    witness_enabled: bool = True
    witness_db_path: str = "~/.if-witness/witness.db"

    def __post_init__(self):
        """Validate configuration"""
        if self.backend not in ["etcd", "nats"]:
            raise ConfigError(f"Invalid backend: {self.backend}. Must be 'etcd' or 'nats'")

        if self.etcd_port < 1 or self.etcd_port > 65535:
            raise ConfigError(f"Invalid etcd_port: {self.etcd_port}")

        if self.target_cas_latency_ms <= 0:
            raise ConfigError(f"target_cas_latency_ms must be positive")

    @classmethod
    def from_env(cls) -> 'CoordinatorConfig':
        """Load config with environment variable overrides"""
        return cls(
            backend=os.getenv('IF_COORDINATOR_BACKEND', 'etcd'),
            etcd_host=os.getenv('IF_ETCD_HOST', 'localhost'),
            etcd_port=int(os.getenv('IF_ETCD_PORT', '2379')),
            nats_host=os.getenv('IF_NATS_HOST', 'localhost'),
            nats_port=int(os.getenv('IF_NATS_PORT', '4222')),
            task_claim_timeout_ms=int(os.getenv('IF_TASK_CLAIM_TIMEOUT_MS', '5000')),
            heartbeat_interval_ms=int(os.getenv('IF_HEARTBEAT_INTERVAL_MS', '1000')),
            witness_enabled=os.getenv('IF_WITNESS_ENABLED', 'true').lower() == 'true',
            witness_db_path=os.getenv('IF_WITNESS_DB_PATH', '~/.if-witness/witness.db'),
        )


@dataclass
class GovernorConfig:
    """IF.governor configuration"""
    # Capability matching
    min_capability_match: float = 0.7  # 70% match required
    reputation_weight: float = 0.3  # How much reputation factors into scoring
    cost_weight: float = 0.5  # How much cost factors into scoring
    capability_weight: float = 0.2  # How much capability match factors in

    # Budget management
    default_budget_per_swarm: float = 100.0  # Default budget in USD
    budget_alert_threshold: float = 0.1  # Alert when 10% remaining
    enable_budget_enforcement: bool = True

    # Circuit breaker settings
    failure_threshold: int = 3  # Failures before circuit opens
    circuit_breaker_timeout_ms: int = 60000  # 1 minute cooldown
    half_open_requests: int = 1  # Requests in half-open state

    # Policy engine
    max_swarms_per_task: int = 3
    max_cost_per_task: float = 10.0
    require_signature_verification: bool = True

    # Witness integration
    witness_enabled: bool = True
    log_capability_matches: bool = True
    log_budget_changes: bool = True

    def __post_init__(self):
        """Validate configuration"""
        if not 0.0 <= self.min_capability_match <= 1.0:
            raise ConfigError(f"min_capability_match must be between 0 and 1")

        weights_sum = self.reputation_weight + self.cost_weight + self.capability_weight
        if not 0.99 <= weights_sum <= 1.01:  # Allow small floating point error
            raise ConfigError(f"Scoring weights must sum to 1.0 (got {weights_sum})")

        if self.failure_threshold < 1:
            raise ConfigError("failure_threshold must be at least 1")

    @classmethod
    def from_env(cls) -> 'GovernorConfig':
        """Load config with environment variable overrides"""
        return cls(
            min_capability_match=float(os.getenv('IF_MIN_CAPABILITY_MATCH', '0.7')),
            default_budget_per_swarm=float(os.getenv('IF_DEFAULT_BUDGET', '100.0')),
            failure_threshold=int(os.getenv('IF_CIRCUIT_BREAKER_THRESHOLD', '3')),
            max_swarms_per_task=int(os.getenv('IF_MAX_SWARMS_PER_TASK', '3')),
            witness_enabled=os.getenv('IF_WITNESS_ENABLED', 'true').lower() == 'true',
        )


@dataclass
class ChassisConfig:
    """IF.chassis configuration"""
    # WASM runtime settings
    wasm_runtime: str = "wasmtime"  # wasmtime, wasmer, wasm3
    wasm_cache_dir: str = "~/.if-chassis/wasm-cache"
    enable_wasm_cache: bool = True

    # Resource limits
    max_memory_mb: int = 512  # Per-sandbox memory limit
    max_cpu_percent: int = 50  # CPU limit per sandbox
    max_disk_mb: int = 1024  # Disk space per sandbox
    max_execution_time_ms: int = 300000  # 5 minutes
    max_network_bandwidth_mbps: int = 10

    # Sandbox settings
    enable_network_isolation: bool = True
    enable_filesystem_isolation: bool = True
    allowed_syscalls: List[str] = field(default_factory=lambda: [
        "read", "write", "open", "close", "stat", "fstat", "mmap", "exit"
    ])

    # Credential management
    credentials_dir: str = "~/.if-chassis/credentials"
    encrypt_credentials: bool = True
    credential_rotation_days: int = 90

    # SLO tracking
    slo_latency_p95_ms: int = 100  # 95th percentile target
    slo_latency_p99_ms: int = 200  # 99th percentile target
    slo_success_rate: float = 0.999  # 99.9% success rate
    slo_reporting_interval_s: int = 60  # Report every minute

    # Witness integration
    witness_enabled: bool = True
    log_sandbox_creation: bool = True
    log_credential_access: bool = True
    log_slo_violations: bool = True

    def __post_init__(self):
        """Validate configuration"""
        if self.wasm_runtime not in ["wasmtime", "wasmer", "wasm3"]:
            raise ConfigError(f"Invalid wasm_runtime: {self.wasm_runtime}")

        if self.max_memory_mb < 64:
            raise ConfigError("max_memory_mb must be at least 64MB")

        if not 0.0 < self.slo_success_rate <= 1.0:
            raise ConfigError("slo_success_rate must be between 0 and 1")

    @classmethod
    def from_env(cls) -> 'ChassisConfig':
        """Load config with environment variable overrides"""
        return cls(
            wasm_runtime=os.getenv('IF_WASM_RUNTIME', 'wasmtime'),
            max_memory_mb=int(os.getenv('IF_MAX_MEMORY_MB', '512')),
            max_cpu_percent=int(os.getenv('IF_MAX_CPU_PERCENT', '50')),
            max_execution_time_ms=int(os.getenv('IF_MAX_EXECUTION_TIME_MS', '300000')),
            enable_network_isolation=os.getenv('IF_NETWORK_ISOLATION', 'true').lower() == 'true',
            witness_enabled=os.getenv('IF_WITNESS_ENABLED', 'true').lower() == 'true',
        )


@dataclass
class WitnessConfig:
    """IF.witness configuration"""
    # Database settings
    db_path: str = "~/.if-witness/witness.db"
    db_journal_mode: str = "WAL"  # Write-Ahead Logging
    db_synchronous: str = "NORMAL"  # NORMAL, FULL, or OFF

    # Cryptographic settings
    signing_key_path: str = "~/.if-witness/signing_key.pem"
    public_key_path: str = "~/.if-witness/public_key.pem"
    key_algorithm: str = "Ed25519"
    auto_generate_keys: bool = True

    # Hash chain settings
    hash_algorithm: str = "SHA-256"
    verify_on_read: bool = True
    verify_interval_entries: int = 1000  # Full verify every N entries

    # Retention settings
    retention_days: int = 365  # Keep logs for 1 year
    auto_archive: bool = True
    archive_dir: str = "~/.if-witness/archives"

    # Performance settings
    batch_size: int = 100  # Batch inserts for performance
    cache_size_mb: int = 64

    # Export settings
    default_export_format: str = "json"  # json, csv, pdf
    export_include_signatures: bool = True

    def __post_init__(self):
        """Validate configuration"""
        if self.hash_algorithm not in ["SHA-256", "SHA-512", "BLAKE2b"]:
            raise ConfigError(f"Invalid hash_algorithm: {self.hash_algorithm}")

        if self.key_algorithm not in ["Ed25519", "RSA-4096"]:
            raise ConfigError(f"Invalid key_algorithm: {self.key_algorithm}")

        if self.retention_days < 1:
            raise ConfigError("retention_days must be at least 1")

    @classmethod
    def from_env(cls) -> 'WitnessConfig':
        """Load config with environment variable overrides"""
        return cls(
            db_path=os.getenv('IF_WITNESS_DB_PATH', '~/.if-witness/witness.db'),
            signing_key_path=os.getenv('IF_WITNESS_SIGNING_KEY', '~/.if-witness/signing_key.pem'),
            public_key_path=os.getenv('IF_WITNESS_PUBLIC_KEY', '~/.if-witness/public_key.pem'),
            verify_on_read=os.getenv('IF_WITNESS_VERIFY_ON_READ', 'true').lower() == 'true',
            retention_days=int(os.getenv('IF_WITNESS_RETENTION_DAYS', '365')),
        )


@dataclass
class OptimiseConfig:
    """IF.optimise configuration"""
    # Cost tracking
    track_token_costs: bool = True
    track_api_costs: bool = True
    track_compute_costs: bool = True

    # Provider settings
    anthropic_api_key: str = ""  # From environment
    anthropic_rate_limit_rpm: int = 100  # Requests per minute

    openai_api_key: str = ""  # From environment
    openai_rate_limit_rpm: int = 100

    # Model costs (USD per million tokens)
    haiku_input_cost: float = 0.25
    haiku_output_cost: float = 1.25
    sonnet_input_cost: float = 3.0
    sonnet_output_cost: float = 15.0
    opus_input_cost: float = 15.0
    opus_output_cost: float = 75.0

    # Optimization settings
    enable_caching: bool = True
    cache_hit_discount: float = 0.1  # 90% discount on cache hits
    prefer_cheaper_models: bool = True
    budget_alert_threshold: float = 0.8  # Alert at 80% budget used

    # Witness integration
    witness_enabled: bool = True
    log_costs_above_usd: float = 1.0  # Log operations over $1

    def __post_init__(self):
        """Validate configuration"""
        if not 0.0 <= self.cache_hit_discount <= 1.0:
            raise ConfigError("cache_hit_discount must be between 0 and 1")

        if not 0.0 <= self.budget_alert_threshold <= 1.0:
            raise ConfigError("budget_alert_threshold must be between 0 and 1")

    @classmethod
    def from_env(cls) -> 'OptimiseConfig':
        """Load config with environment variable overrides"""
        return cls(
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY', ''),
            openai_api_key=os.getenv('OPENAI_API_KEY', ''),
            enable_caching=os.getenv('IF_ENABLE_CACHING', 'true').lower() == 'true',
            witness_enabled=os.getenv('IF_WITNESS_ENABLED', 'true').lower() == 'true',
        )


@dataclass
class InfraFabricConfig:
    """Top-level InfraFabric configuration"""
    coordinator: CoordinatorConfig = field(default_factory=CoordinatorConfig)
    governor: GovernorConfig = field(default_factory=GovernorConfig)
    chassis: ChassisConfig = field(default_factory=ChassisConfig)
    witness: WitnessConfig = field(default_factory=WitnessConfig)
    optimise: OptimiseConfig = field(default_factory=OptimiseConfig)

    # Global settings
    log_level: str = "info"
    enable_telemetry: bool = True
    config_version: str = "1.0"

    def __post_init__(self):
        """Validate configuration"""
        if self.log_level not in ["debug", "info", "warning", "error"]:
            raise ConfigError(f"Invalid log_level: {self.log_level}")

    @classmethod
    def from_yaml(cls, path: Path) -> 'InfraFabricConfig':
        """Load configuration from YAML file"""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f) or {}

            return cls(
                coordinator=CoordinatorConfig(**data.get('coordinator', {})),
                governor=GovernorConfig(**data.get('governor', {})),
                chassis=ChassisConfig(**data.get('chassis', {})),
                witness=WitnessConfig(**data.get('witness', {})),
                optimise=OptimiseConfig(**data.get('optimise', {})),
                log_level=data.get('log_level', 'info'),
                enable_telemetry=data.get('enable_telemetry', True),
            )
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse YAML config: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load config from {path}: {e}")

    def to_yaml(self, path: Path):
        """Save configuration to YAML file"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'config_version': self.config_version,
                'log_level': self.log_level,
                'enable_telemetry': self.enable_telemetry,
                'coordinator': asdict(self.coordinator),
                'governor': asdict(self.governor),
                'chassis': asdict(self.chassis),
                'witness': asdict(self.witness),
                'optimise': asdict(self.optimise),
            }

            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise ConfigError(f"Failed to save config to {path}: {e}")

    @classmethod
    def from_env(cls) -> 'InfraFabricConfig':
        """Load configuration with environment variable overrides"""
        return cls(
            coordinator=CoordinatorConfig.from_env(),
            governor=GovernorConfig.from_env(),
            chassis=ChassisConfig.from_env(),
            witness=WitnessConfig.from_env(),
            optimise=OptimiseConfig.from_env(),
            log_level=os.getenv('IF_LOG_LEVEL', 'info'),
            enable_telemetry=os.getenv('IF_ENABLE_TELEMETRY', 'true').lower() == 'true',
        )

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'InfraFabricConfig':
        """
        Load configuration with priority:
        1. Specified config file
        2. ~/.config/infrafabric/config.yaml
        3. Environment variables
        4. Defaults
        """
        # Try specified path first
        if config_path and config_path.exists():
            return cls.from_yaml(config_path)

        # Try default location
        default_path = Path.home() / '.config' / 'infrafabric' / 'config.yaml'
        if default_path.exists():
            return cls.from_yaml(default_path)

        # Fall back to environment variables + defaults
        return cls.from_env()


def generate_example_config(output_path: Path):
    """Generate example configuration file with comments"""
    config = InfraFabricConfig()

    # Add comments via YAML dump with custom representer
    example_yaml = f"""# InfraFabric Configuration
# Version: 1.0
# Location: ~/.config/infrafabric/config.yaml
#
# Environment variable overrides:
# - IF_ETCD_HOST, IF_ETCD_PORT
# - IF_COORDINATOR_BACKEND (etcd|nats)
# - IF_WITNESS_DB_PATH
# - IF_LOG_LEVEL (debug|info|warning|error)
# - ANTHROPIC_API_KEY, OPENAI_API_KEY

config_version: "1.0"
log_level: info  # debug, info, warning, error
enable_telemetry: true

# IF.coordinator - Real-time coordination (<10ms)
coordinator:
  backend: etcd  # etcd or nats
  etcd_host: localhost
  etcd_port: 2379
  nats_host: localhost
  nats_port: 4222

  # Performance targets
  target_cas_latency_ms: 5  # Atomic claim_task() target
  target_pubsub_latency_ms: 10  # Task broadcast target

  # Timeouts
  task_claim_timeout_ms: 5000
  heartbeat_interval_ms: 1000
  stale_task_threshold_ms: 30000

  # Witness integration
  witness_enabled: true
  witness_db_path: ~/.if-witness/witness.db

# IF.governor - Policy-based resource allocation
governor:
  # Capability matching (70%+ match required)
  min_capability_match: 0.7
  reputation_weight: 0.3
  cost_weight: 0.5
  capability_weight: 0.2

  # Budget management
  default_budget_per_swarm: 100.0  # USD
  budget_alert_threshold: 0.1  # Alert at 10% remaining
  enable_budget_enforcement: true

  # Circuit breaker
  failure_threshold: 3  # Failures before circuit opens
  circuit_breaker_timeout_ms: 60000  # 1 minute cooldown

  # Policy constraints
  max_swarms_per_task: 3
  max_cost_per_task: 10.0
  require_signature_verification: true

  # Witness logging
  witness_enabled: true
  log_capability_matches: true
  log_budget_changes: true

# IF.chassis - WASM sandbox execution
chassis:
  # WASM runtime
  wasm_runtime: wasmtime  # wasmtime, wasmer, wasm3
  wasm_cache_dir: ~/.if-chassis/wasm-cache
  enable_wasm_cache: true

  # Resource limits (per sandbox)
  max_memory_mb: 512
  max_cpu_percent: 50
  max_disk_mb: 1024
  max_execution_time_ms: 300000  # 5 minutes
  max_network_bandwidth_mbps: 10

  # Security
  enable_network_isolation: true
  enable_filesystem_isolation: true
  allowed_syscalls:
    - read
    - write
    - open
    - close
    - stat
    - fstat
    - mmap
    - exit

  # Credentials
  credentials_dir: ~/.if-chassis/credentials
  encrypt_credentials: true
  credential_rotation_days: 90

  # SLO tracking
  slo_latency_p95_ms: 100
  slo_latency_p99_ms: 200
  slo_success_rate: 0.999  # 99.9%
  slo_reporting_interval_s: 60

  # Witness logging
  witness_enabled: true
  log_sandbox_creation: true
  log_credential_access: true
  log_slo_violations: true

# IF.witness - Cryptographic provenance
witness:
  # Database
  db_path: ~/.if-witness/witness.db
  db_journal_mode: WAL  # Write-Ahead Logging
  db_synchronous: NORMAL  # NORMAL, FULL, or OFF

  # Cryptography
  signing_key_path: ~/.if-witness/signing_key.pem
  public_key_path: ~/.if-witness/public_key.pem
  key_algorithm: Ed25519  # Ed25519 or RSA-4096
  auto_generate_keys: true

  # Hash chain
  hash_algorithm: SHA-256  # SHA-256, SHA-512, BLAKE2b
  verify_on_read: true
  verify_interval_entries: 1000  # Full verify every N entries

  # Retention
  retention_days: 365
  auto_archive: true
  archive_dir: ~/.if-witness/archives

  # Performance
  batch_size: 100
  cache_size_mb: 64

  # Export
  default_export_format: json  # json, csv, pdf
  export_include_signatures: true

# IF.optimise - Cost tracking and optimization
optimise:
  # Tracking
  track_token_costs: true
  track_api_costs: true
  track_compute_costs: true

  # Provider rate limits (requests per minute)
  anthropic_rate_limit_rpm: 100
  openai_rate_limit_rpm: 100

  # Model costs (USD per million tokens)
  haiku_input_cost: 0.25
  haiku_output_cost: 1.25
  sonnet_input_cost: 3.0
  sonnet_output_cost: 15.0
  opus_input_cost: 15.0
  opus_output_cost: 75.0

  # Optimization
  enable_caching: true
  cache_hit_discount: 0.1  # 90% discount
  prefer_cheaper_models: true
  budget_alert_threshold: 0.8  # Alert at 80%

  # Witness logging
  witness_enabled: true
  log_costs_above_usd: 1.0  # Log operations over $1

# API Keys (use environment variables in production!)
# anthropic_api_key: $ANTHROPIC_API_KEY
# openai_api_key: $OPENAI_API_KEY
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(example_yaml)
