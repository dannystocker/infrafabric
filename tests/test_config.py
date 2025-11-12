"""
Unit tests for configuration management

Tests config loading, validation, environment overrides, and YAML I/O.
"""

import pytest
import os
import tempfile
from pathlib import Path
from infrafabric.config import (
    ConfigError,
    CoordinatorConfig,
    GovernorConfig,
    ChassisConfig,
    WitnessConfig,
    OptimiseConfig,
    InfraFabricConfig,
    generate_example_config
)


class TestCoordinatorConfig:
    """Test IF.coordinator configuration"""

    def test_default_config(self):
        """Test default coordinator configuration"""
        config = CoordinatorConfig()
        assert config.backend == "etcd"
        assert config.etcd_host == "localhost"
        assert config.etcd_port == 2379
        assert config.target_cas_latency_ms == 5
        assert config.witness_enabled is True

    def test_custom_config(self):
        """Test custom coordinator configuration"""
        config = CoordinatorConfig(
            backend="nats",
            nats_host="nats-server",
            nats_port=4222,
            target_cas_latency_ms=10
        )
        assert config.backend == "nats"
        assert config.nats_host == "nats-server"
        assert config.target_cas_latency_ms == 10

    def test_invalid_backend(self):
        """Test invalid backend raises error"""
        with pytest.raises(ConfigError, match="Invalid backend"):
            CoordinatorConfig(backend="invalid")

    def test_invalid_port(self):
        """Test invalid port raises error"""
        with pytest.raises(ConfigError, match="Invalid etcd_port"):
            CoordinatorConfig(etcd_port=99999)

    def test_invalid_latency(self):
        """Test invalid latency target raises error"""
        with pytest.raises(ConfigError, match="must be positive"):
            CoordinatorConfig(target_cas_latency_ms=-1)

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv('IF_COORDINATOR_BACKEND', 'nats')
        monkeypatch.setenv('IF_ETCD_HOST', 'etcd-prod')
        monkeypatch.setenv('IF_ETCD_PORT', '2380')
        monkeypatch.setenv('IF_WITNESS_ENABLED', 'false')

        config = CoordinatorConfig.from_env()
        assert config.backend == "nats"
        assert config.etcd_host == "etcd-prod"
        assert config.etcd_port == 2380
        assert config.witness_enabled is False


class TestGovernorConfig:
    """Test IF.governor configuration"""

    def test_default_config(self):
        """Test default governor configuration"""
        config = GovernorConfig()
        assert config.min_capability_match == 0.7
        assert config.default_budget_per_swarm == 100.0
        assert config.failure_threshold == 3
        assert config.max_swarms_per_task == 3

    def test_custom_config(self):
        """Test custom governor configuration"""
        config = GovernorConfig(
            min_capability_match=0.8,
            default_budget_per_swarm=200.0,
            failure_threshold=5
        )
        assert config.min_capability_match == 0.8
        assert config.default_budget_per_swarm == 200.0
        assert config.failure_threshold == 5

    def test_invalid_capability_match(self):
        """Test invalid capability match raises error"""
        with pytest.raises(ConfigError, match="must be between 0 and 1"):
            GovernorConfig(min_capability_match=1.5)

    def test_invalid_weights(self):
        """Test invalid scoring weights raises error"""
        with pytest.raises(ConfigError, match="must sum to 1.0"):
            GovernorConfig(
                reputation_weight=0.5,
                cost_weight=0.5,
                capability_weight=0.5  # Sum = 1.5, invalid
            )

    def test_valid_weights(self):
        """Test valid scoring weights"""
        config = GovernorConfig(
            reputation_weight=0.4,
            cost_weight=0.4,
            capability_weight=0.2
        )
        assert config.reputation_weight == 0.4

    def test_invalid_failure_threshold(self):
        """Test invalid failure threshold raises error"""
        with pytest.raises(ConfigError, match="must be at least 1"):
            GovernorConfig(failure_threshold=0)

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv('IF_MIN_CAPABILITY_MATCH', '0.8')
        monkeypatch.setenv('IF_DEFAULT_BUDGET', '150.0')
        monkeypatch.setenv('IF_CIRCUIT_BREAKER_THRESHOLD', '5')

        config = GovernorConfig.from_env()
        assert config.min_capability_match == 0.8
        assert config.default_budget_per_swarm == 150.0
        assert config.failure_threshold == 5


class TestChassisConfig:
    """Test IF.chassis configuration"""

    def test_default_config(self):
        """Test default chassis configuration"""
        config = ChassisConfig()
        assert config.wasm_runtime == "wasmtime"
        assert config.max_memory_mb == 512
        assert config.max_cpu_percent == 50
        assert config.slo_success_rate == 0.999

    def test_custom_config(self):
        """Test custom chassis configuration"""
        config = ChassisConfig(
            wasm_runtime="wasmer",
            max_memory_mb=1024,
            slo_success_rate=0.99
        )
        assert config.wasm_runtime == "wasmer"
        assert config.max_memory_mb == 1024
        assert config.slo_success_rate == 0.99

    def test_invalid_runtime(self):
        """Test invalid WASM runtime raises error"""
        with pytest.raises(ConfigError, match="Invalid wasm_runtime"):
            ChassisConfig(wasm_runtime="invalid")

    def test_invalid_memory(self):
        """Test invalid memory limit raises error"""
        with pytest.raises(ConfigError, match="must be at least 64MB"):
            ChassisConfig(max_memory_mb=32)

    def test_invalid_slo_success_rate(self):
        """Test invalid SLO success rate raises error"""
        with pytest.raises(ConfigError, match="must be between 0 and 1"):
            ChassisConfig(slo_success_rate=1.5)

    def test_allowed_syscalls(self):
        """Test allowed syscalls list"""
        config = ChassisConfig()
        assert "read" in config.allowed_syscalls
        assert "write" in config.allowed_syscalls
        assert len(config.allowed_syscalls) > 0

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv('IF_WASM_RUNTIME', 'wasmer')
        monkeypatch.setenv('IF_MAX_MEMORY_MB', '1024')
        monkeypatch.setenv('IF_MAX_CPU_PERCENT', '75')

        config = ChassisConfig.from_env()
        assert config.wasm_runtime == "wasmer"
        assert config.max_memory_mb == 1024
        assert config.max_cpu_percent == 75


class TestWitnessConfig:
    """Test IF.witness configuration"""

    def test_default_config(self):
        """Test default witness configuration"""
        config = WitnessConfig()
        assert config.db_path == "~/.if-witness/witness.db"
        assert config.key_algorithm == "Ed25519"
        assert config.hash_algorithm == "SHA-256"
        assert config.retention_days == 365

    def test_custom_config(self):
        """Test custom witness configuration"""
        config = WitnessConfig(
            db_path="/tmp/witness.db",
            key_algorithm="RSA-4096",
            hash_algorithm="SHA-512",
            retention_days=180
        )
        assert config.db_path == "/tmp/witness.db"
        assert config.key_algorithm == "RSA-4096"
        assert config.hash_algorithm == "SHA-512"
        assert config.retention_days == 180

    def test_invalid_hash_algorithm(self):
        """Test invalid hash algorithm raises error"""
        with pytest.raises(ConfigError, match="Invalid hash_algorithm"):
            WitnessConfig(hash_algorithm="MD5")

    def test_invalid_key_algorithm(self):
        """Test invalid key algorithm raises error"""
        with pytest.raises(ConfigError, match="Invalid key_algorithm"):
            WitnessConfig(key_algorithm="RSA-2048")

    def test_invalid_retention_days(self):
        """Test invalid retention days raises error"""
        with pytest.raises(ConfigError, match="must be at least 1"):
            WitnessConfig(retention_days=0)

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv('IF_WITNESS_DB_PATH', '/custom/witness.db')
        monkeypatch.setenv('IF_WITNESS_RETENTION_DAYS', '180')
        monkeypatch.setenv('IF_WITNESS_VERIFY_ON_READ', 'false')

        config = WitnessConfig.from_env()
        assert config.db_path == '/custom/witness.db'
        assert config.retention_days == 180
        assert config.verify_on_read is False


class TestOptimiseConfig:
    """Test IF.optimise configuration"""

    def test_default_config(self):
        """Test default optimise configuration"""
        config = OptimiseConfig()
        assert config.track_token_costs is True
        assert config.haiku_input_cost == 0.25
        assert config.sonnet_input_cost == 3.0
        assert config.enable_caching is True

    def test_custom_config(self):
        """Test custom optimise configuration"""
        config = OptimiseConfig(
            haiku_input_cost=0.20,
            enable_caching=False,
            budget_alert_threshold=0.9
        )
        assert config.haiku_input_cost == 0.20
        assert config.enable_caching is False
        assert config.budget_alert_threshold == 0.9

    def test_invalid_cache_discount(self):
        """Test invalid cache discount raises error"""
        with pytest.raises(ConfigError, match="must be between 0 and 1"):
            OptimiseConfig(cache_hit_discount=1.5)

    def test_invalid_budget_threshold(self):
        """Test invalid budget threshold raises error"""
        with pytest.raises(ConfigError, match="must be between 0 and 1"):
            OptimiseConfig(budget_alert_threshold=1.2)

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv('ANTHROPIC_API_KEY', 'test-key-123')
        monkeypatch.setenv('IF_ENABLE_CACHING', 'false')

        config = OptimiseConfig.from_env()
        assert config.anthropic_api_key == 'test-key-123'
        assert config.enable_caching is False


class TestInfraFabricConfig:
    """Test top-level InfraFabric configuration"""

    def test_default_config(self):
        """Test default top-level configuration"""
        config = InfraFabricConfig()
        assert config.log_level == "info"
        assert config.enable_telemetry is True
        assert isinstance(config.coordinator, CoordinatorConfig)
        assert isinstance(config.governor, GovernorConfig)
        assert isinstance(config.chassis, ChassisConfig)
        assert isinstance(config.witness, WitnessConfig)
        assert isinstance(config.optimise, OptimiseConfig)

    def test_custom_config(self):
        """Test custom top-level configuration"""
        config = InfraFabricConfig(
            log_level="debug",
            enable_telemetry=False,
            coordinator=CoordinatorConfig(backend="nats")
        )
        assert config.log_level == "debug"
        assert config.enable_telemetry is False
        assert config.coordinator.backend == "nats"

    def test_invalid_log_level(self):
        """Test invalid log level raises error"""
        with pytest.raises(ConfigError, match="Invalid log_level"):
            InfraFabricConfig(log_level="invalid")

    def test_yaml_round_trip(self):
        """Test saving and loading YAML configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yaml"

            # Create and save config
            original = InfraFabricConfig(
                log_level="debug",
                coordinator=CoordinatorConfig(backend="nats", etcd_port=2380),
                governor=GovernorConfig(min_capability_match=0.8)
            )
            original.to_yaml(config_path)

            # Load config
            loaded = InfraFabricConfig.from_yaml(config_path)

            # Verify
            assert loaded.log_level == "debug"
            assert loaded.coordinator.backend == "nats"
            assert loaded.coordinator.etcd_port == 2380
            assert loaded.governor.min_capability_match == 0.8

    def test_yaml_invalid_file(self):
        """Test loading invalid YAML file raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "invalid.yaml"
            with open(config_path, 'w') as f:
                f.write("invalid: yaml: content: [[[")

            with pytest.raises(ConfigError, match="Failed to parse YAML"):
                InfraFabricConfig.from_yaml(config_path)

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv('IF_LOG_LEVEL', 'debug')
        monkeypatch.setenv('IF_ETCD_HOST', 'etcd-prod')
        monkeypatch.setenv('IF_MIN_CAPABILITY_MATCH', '0.8')

        config = InfraFabricConfig.from_env()
        assert config.log_level == "debug"
        assert config.coordinator.etcd_host == "etcd-prod"
        assert config.governor.min_capability_match == 0.8

    def test_load_priority(self, monkeypatch):
        """Test config loading priority (file > env > defaults)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"

            # Create config file
            file_config = InfraFabricConfig(
                log_level="error",
                coordinator=CoordinatorConfig(etcd_port=2380)
            )
            file_config.to_yaml(config_path)

            # Set environment variable
            monkeypatch.setenv('IF_LOG_LEVEL', 'debug')

            # Load - file should take priority over env
            loaded = InfraFabricConfig.load(config_path)
            assert loaded.log_level == "error"  # From file, not env
            assert loaded.coordinator.etcd_port == 2380

    def test_load_nonexistent_file(self):
        """Test loading with nonexistent file falls back to env/defaults"""
        config = InfraFabricConfig.load(Path("/nonexistent/config.yaml"))
        assert config.log_level == "info"  # Default
        assert config.coordinator.backend == "etcd"  # Default


class TestGenerateExampleConfig:
    """Test example config generation"""

    def test_generate_example(self):
        """Test generating example configuration file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "example.yaml"
            generate_example_config(output_path)

            assert output_path.exists()

            # Verify it's valid YAML
            import yaml
            with open(output_path, 'r') as f:
                data = yaml.safe_load(f)

            assert 'config_version' in data
            assert 'coordinator' in data
            assert 'governor' in data
            assert 'chassis' in data
            assert 'witness' in data
            assert 'optimise' in data

    def test_example_can_be_loaded(self):
        """Test that generated example config can be loaded"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "example.yaml"
            generate_example_config(config_path)

            # Should load without errors
            config = InfraFabricConfig.from_yaml(config_path)
            assert config.log_level == "info"
            assert config.coordinator.backend == "etcd"


class TestConfigValidation:
    """Test configuration validation edge cases"""

    def test_coordinator_zero_latency(self):
        """Test zero latency target is invalid"""
        with pytest.raises(ConfigError):
            CoordinatorConfig(target_cas_latency_ms=0)

    def test_governor_weights_sum(self):
        """Test scoring weights must sum to 1.0"""
        # Valid: exactly 1.0
        config = GovernorConfig(
            reputation_weight=0.333333,
            cost_weight=0.333333,
            capability_weight=0.333334
        )
        assert config.reputation_weight > 0

        # Invalid: > 1.0
        with pytest.raises(ConfigError):
            GovernorConfig(
                reputation_weight=0.5,
                cost_weight=0.5,
                capability_weight=0.5
            )

    def test_chassis_memory_minimum(self):
        """Test minimum memory requirement"""
        with pytest.raises(ConfigError, match="at least 64MB"):
            ChassisConfig(max_memory_mb=32)

        # Valid: exactly 64MB
        config = ChassisConfig(max_memory_mb=64)
        assert config.max_memory_mb == 64

    def test_witness_algorithms(self):
        """Test cryptographic algorithm validation"""
        # Valid algorithms
        for algo in ["SHA-256", "SHA-512", "BLAKE2b"]:
            config = WitnessConfig(hash_algorithm=algo)
            assert config.hash_algorithm == algo

        # Invalid algorithm
        with pytest.raises(ConfigError, match="Invalid hash_algorithm"):
            WitnessConfig(hash_algorithm="MD5")

    def test_optimise_cost_values(self):
        """Test cost values are positive"""
        config = OptimiseConfig(
            haiku_input_cost=0.25,
            haiku_output_cost=1.25
        )
        assert config.haiku_input_cost > 0
        assert config.haiku_output_cost > 0


class TestConfigPaths:
    """Test path handling in configuration"""

    def test_path_expansion(self):
        """Test tilde expansion in paths"""
        config = WitnessConfig(db_path="~/test.db")
        assert "~" in config.db_path  # Not expanded in config

        # In actual usage, paths should be expanded when opened
        expanded = Path(config.db_path).expanduser()
        assert "~" not in str(expanded)

    def test_relative_paths(self):
        """Test relative path handling"""
        config = WitnessConfig(db_path="./witness.db")
        assert config.db_path == "./witness.db"

    def test_absolute_paths(self):
        """Test absolute path handling"""
        config = WitnessConfig(db_path="/tmp/witness.db")
        assert config.db_path == "/tmp/witness.db"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
