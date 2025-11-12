"""Unit tests for capability registry schema (P0.2.1)

Tests cover:
- Capability enum with 42 capability types
- SwarmProfile creation and validation
- ResourcePolicy validation
- Manifest validation logic
- JSON serialization/deserialization

Task: P0.2.1 - Create capability registry schema
Session: 4 (SIP)
Model: Haiku
"""

import pytest
import json
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    validate_capability_manifest,
    load_manifest_from_json,
)


class TestCapabilityEnum:
    """Test Capability enum definition"""

    def test_all_capability_types_defined(self):
        """Verify all 42 capability types are defined"""
        # Count all capabilities
        capabilities = list(Capability)
        assert len(capabilities) >= 42, f"Expected >= 42 capabilities, got {len(capabilities)}"

    def test_integration_sip_capability(self):
        """Session 4 (SIP) primary capability exists"""
        assert Capability.INTEGRATION_SIP.value == "integration:sip"

    def test_capability_categories(self):
        """Verify all capability categories exist"""
        categories = [
            "code-analysis",
            "integration",
            "infra",
            "cli",
            "architecture",
            "docs",
            "testing",
            "database",
            "devops",
            "security",
        ]

        for category in categories:
            # Check at least one capability exists for each category
            matching_caps = [
                cap for cap in Capability if cap.value.startswith(f"{category}:")
            ]
            assert len(matching_caps) > 0, f"No capabilities found for category: {category}"

    def test_capability_from_string_valid(self):
        """Parse valid capability from string"""
        cap = Capability.from_string("integration:sip")
        assert cap == Capability.INTEGRATION_SIP

    def test_capability_from_string_invalid(self):
        """Invalid capability string returns None"""
        cap = Capability.from_string("invalid:capability")
        assert cap is None

    def test_capability_string_representation(self):
        """Capability str() returns value"""
        assert str(Capability.INTEGRATION_SIP) == "integration:sip"


class TestSwarmProfile:
    """Test SwarmProfile dataclass"""

    def test_create_valid_profile(self):
        """Create valid swarm profile"""
        profile = SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[Capability.INTEGRATION_SIP, Capability.ARCHITECTURE_SECURITY],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.44,
            model="haiku",
        )

        assert profile.swarm_id == "session-4-sip"
        assert len(profile.capabilities) == 2
        assert profile.cost_per_hour == 2.0
        assert profile.reputation_score == 0.95
        assert profile.current_budget_remaining == 10.44
        assert profile.model == "haiku"

    def test_reputation_score_validation(self):
        """Reputation score must be 0.0-1.0"""
        # Valid: 0.0
        SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.0,
            current_budget_remaining=10.0,
            model="haiku",
        )

        # Valid: 1.0
        SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=1.0,
            current_budget_remaining=10.0,
            model="haiku",
        )

        # Invalid: -0.1
        with pytest.raises(ValueError, match="Reputation score must be 0.0-1.0"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.INTEGRATION_SIP],
                cost_per_hour=2.0,
                reputation_score=-0.1,
                current_budget_remaining=10.0,
                model="haiku",
            )

        # Invalid: 1.1
        with pytest.raises(ValueError, match="Reputation score must be 0.0-1.0"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.INTEGRATION_SIP],
                cost_per_hour=2.0,
                reputation_score=1.1,
                current_budget_remaining=10.0,
                model="haiku",
            )

    def test_model_validation(self):
        """Model must be haiku, sonnet, or opus"""
        # Valid: haiku
        SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.5,
            current_budget_remaining=10.0,
            model="haiku",
        )

        # Valid: sonnet
        SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=15.0,
            reputation_score=0.5,
            current_budget_remaining=10.0,
            model="sonnet",
        )

        # Invalid: gpt4
        with pytest.raises(ValueError, match="Model must be one of"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.INTEGRATION_SIP],
                cost_per_hour=2.0,
                reputation_score=0.5,
                current_budget_remaining=10.0,
                model="gpt4",
            )

    def test_cost_per_hour_validation(self):
        """Cost per hour must be positive"""
        # Valid: positive cost
        SwarmProfile(
            swarm_id="test",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.5,
            current_budget_remaining=10.0,
            model="haiku",
        )

        # Invalid: zero cost
        with pytest.raises(ValueError, match="Cost per hour must be positive"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.INTEGRATION_SIP],
                cost_per_hour=0.0,
                reputation_score=0.5,
                current_budget_remaining=10.0,
                model="haiku",
            )

        # Invalid: negative cost
        with pytest.raises(ValueError, match="Cost per hour must be positive"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[Capability.INTEGRATION_SIP],
                cost_per_hour=-1.0,
                reputation_score=0.5,
                current_budget_remaining=10.0,
                model="haiku",
            )

    def test_capabilities_not_empty(self):
        """Swarm must have at least one capability"""
        with pytest.raises(ValueError, match="at least one capability"):
            SwarmProfile(
                swarm_id="test",
                capabilities=[],
                cost_per_hour=2.0,
                reputation_score=0.5,
                current_budget_remaining=10.0,
                model="haiku",
            )

    def test_profile_to_dict(self):
        """Convert profile to dictionary"""
        profile = SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[Capability.INTEGRATION_SIP],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.44,
            model="haiku",
            metadata={"phase": "0"},
        )

        data = profile.to_dict()

        assert data["swarm_id"] == "session-4-sip"
        assert data["capabilities"] == ["integration:sip"]
        assert data["cost_per_hour"] == 2.0
        assert data["reputation_score"] == 0.95
        assert data["model"] == "haiku"
        assert data["metadata"] == {"phase": "0"}

    def test_profile_from_dict(self):
        """Create profile from dictionary"""
        data = {
            "swarm_id": "session-4-sip",
            "capabilities": ["integration:sip", "architecture:security"],
            "cost_per_hour": 2.0,
            "reputation_score": 0.95,
            "current_budget_remaining": 10.44,
            "model": "haiku",
        }

        profile = SwarmProfile.from_dict(data)

        assert profile.swarm_id == "session-4-sip"
        assert len(profile.capabilities) == 2
        assert Capability.INTEGRATION_SIP in profile.capabilities
        assert Capability.ARCHITECTURE_SECURITY in profile.capabilities


class TestResourcePolicy:
    """Test ResourcePolicy dataclass"""

    def test_create_default_policy(self):
        """Create policy with default values"""
        policy = ResourcePolicy()

        assert policy.max_swarms_per_task == 3
        assert policy.max_cost_per_task == 10.0
        assert policy.min_capability_match == 0.7
        assert policy.circuit_breaker_failure_threshold == 3
        assert policy.enable_budget_enforcement is True
        assert policy.enable_reputation_scoring is True

    def test_create_custom_policy(self):
        """Create policy with custom values"""
        policy = ResourcePolicy(
            max_swarms_per_task=5,
            max_cost_per_task=25.0,
            min_capability_match=0.8,
            circuit_breaker_failure_threshold=5,
        )

        assert policy.max_swarms_per_task == 5
        assert policy.max_cost_per_task == 25.0
        assert policy.min_capability_match == 0.8
        assert policy.circuit_breaker_failure_threshold == 5

    def test_max_swarms_validation(self):
        """Max swarms must be >= 1"""
        # Valid: 1
        ResourcePolicy(max_swarms_per_task=1)

        # Invalid: 0
        with pytest.raises(ValueError, match="max_swarms_per_task must be >= 1"):
            ResourcePolicy(max_swarms_per_task=0)

    def test_min_capability_match_validation(self):
        """Min capability match must be 0.0-1.0"""
        # Valid: 0.0
        ResourcePolicy(min_capability_match=0.0)

        # Valid: 1.0
        ResourcePolicy(min_capability_match=1.0)

        # Invalid: -0.1
        with pytest.raises(ValueError, match="min_capability_match must be 0.0-1.0"):
            ResourcePolicy(min_capability_match=-0.1)

        # Invalid: 1.1
        with pytest.raises(ValueError, match="min_capability_match must be 0.0-1.0"):
            ResourcePolicy(min_capability_match=1.1)

    def test_max_cost_validation(self):
        """Max cost per task must be positive"""
        # Valid: positive
        ResourcePolicy(max_cost_per_task=10.0)

        # Invalid: zero
        with pytest.raises(ValueError, match="max_cost_per_task must be positive"):
            ResourcePolicy(max_cost_per_task=0.0)

    def test_circuit_breaker_threshold_validation(self):
        """Circuit breaker threshold must be >= 1"""
        # Valid: 1
        ResourcePolicy(circuit_breaker_failure_threshold=1)

        # Invalid: 0
        with pytest.raises(ValueError, match="circuit_breaker_failure_threshold must be >= 1"):
            ResourcePolicy(circuit_breaker_failure_threshold=0)

    def test_policy_to_dict(self):
        """Convert policy to dictionary"""
        policy = ResourcePolicy(
            max_swarms_per_task=5,
            max_cost_per_task=25.0,
            min_capability_match=0.8,
        )

        data = policy.to_dict()

        assert data["max_swarms_per_task"] == 5
        assert data["max_cost_per_task"] == 25.0
        assert data["min_capability_match"] == 0.8

    def test_policy_from_dict(self):
        """Create policy from dictionary"""
        data = {
            "max_swarms_per_task": 5,
            "max_cost_per_task": 25.0,
            "min_capability_match": 0.8,
        }

        policy = ResourcePolicy.from_dict(data)

        assert policy.max_swarms_per_task == 5
        assert policy.max_cost_per_task == 25.0
        assert policy.min_capability_match == 0.8


class TestManifestValidation:
    """Test capability manifest validation"""

    def test_valid_manifest(self):
        """Valid manifest passes validation"""
        manifest = {
            "swarm_id": "session-4-sip",
            "capabilities": ["integration:sip"],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.44,
            "model": "haiku",
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is True
        assert error is None

    def test_missing_swarm_id(self):
        """Missing swarm_id fails validation"""
        manifest = {
            "capabilities": ["integration:sip"],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.0,
            "model": "haiku",
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is False
        assert "swarm_id" in error

    def test_missing_capabilities(self):
        """Missing capabilities fails validation"""
        manifest = {
            "swarm_id": "test",
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.0,
            "model": "haiku",
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is False
        assert "capabilities" in error

    def test_empty_capabilities(self):
        """Empty capabilities list fails validation"""
        manifest = {
            "swarm_id": "test",
            "capabilities": [],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.0,
            "model": "haiku",
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is False
        assert "empty" in error.lower()

    def test_invalid_capability_string(self):
        """Unknown capability fails validation"""
        manifest = {
            "swarm_id": "test",
            "capabilities": ["invalid:capability"],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.0,
            "model": "haiku",
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is False
        assert "Unknown capability" in error

    def test_invalid_cost_per_hour(self):
        """Invalid cost_per_hour fails validation"""
        manifest = {
            "swarm_id": "test",
            "capabilities": ["integration:sip"],
            "cost_per_hour": -1.0,
            "current_budget_remaining": 10.0,
            "model": "haiku",
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is False
        assert "cost_per_hour must be positive" in error

    def test_invalid_model(self):
        """Invalid model fails validation"""
        manifest = {
            "swarm_id": "test",
            "capabilities": ["integration:sip"],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.0,
            "model": "gpt4",
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is False
        assert "model must be one of" in error

    def test_invalid_reputation_score(self):
        """Invalid reputation_score fails validation"""
        manifest = {
            "swarm_id": "test",
            "capabilities": ["integration:sip"],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.0,
            "model": "haiku",
            "reputation_score": 1.5,
        }

        valid, error = validate_capability_manifest(manifest)
        assert valid is False
        assert "reputation_score must be between 0.0 and 1.0" in error


class TestJSONSerialization:
    """Test JSON loading and serialization"""

    def test_load_valid_json(self):
        """Load valid JSON manifest"""
        json_str = json.dumps({
            "swarm_id": "session-4-sip",
            "capabilities": ["integration:sip", "architecture:security"],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.44,
            "model": "haiku",
            "reputation_score": 0.95,
        })

        profile, error = load_manifest_from_json(json_str)

        assert profile is not None
        assert error is None
        assert profile.swarm_id == "session-4-sip"
        assert len(profile.capabilities) == 2

    def test_load_invalid_json(self):
        """Invalid JSON returns error"""
        json_str = "{ invalid json"

        profile, error = load_manifest_from_json(json_str)

        assert profile is None
        assert "Invalid JSON" in error

    def test_load_invalid_manifest(self):
        """Invalid manifest returns error"""
        json_str = json.dumps({
            "swarm_id": "test",
            "capabilities": ["invalid:capability"],
            "cost_per_hour": 2.0,
            "current_budget_remaining": 10.0,
            "model": "haiku",
        })

        profile, error = load_manifest_from_json(json_str)

        assert profile is None
        assert error is not None

    def test_round_trip_serialization(self):
        """Profile → JSON → Profile preserves data"""
        original = SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[Capability.INTEGRATION_SIP, Capability.ARCHITECTURE_SECURITY],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.44,
            model="haiku",
        )

        # Convert to JSON
        data = original.to_dict()
        json_str = json.dumps(data)

        # Load back
        loaded, error = load_manifest_from_json(json_str)

        assert error is None
        assert loaded.swarm_id == original.swarm_id
        assert len(loaded.capabilities) == len(original.capabilities)
        assert loaded.cost_per_hour == original.cost_per_hour
        assert loaded.reputation_score == original.reputation_score


class TestSession4Profile:
    """Test Session 4 (SIP) specific profile"""

    def test_session_4_profile(self):
        """Create Session 4 (SIP) profile with actual capabilities"""
        profile = SwarmProfile(
            swarm_id="session-4-sip",
            capabilities=[
                Capability.INTEGRATION_SIP,
                Capability.INTEGRATION_H323,
                Capability.INTEGRATION_WEBRTC,
                Capability.INTEGRATION_NDI,
                Capability.ARCHITECTURE_SECURITY,
                Capability.INFRA_NETWORKING,
                Capability.DOCS_TECHNICAL_WRITING,
                Capability.CODE_ANALYSIS_PYTHON,
            ],
            cost_per_hour=2.0,
            reputation_score=0.95,
            current_budget_remaining=10.44,
            model="haiku",
            metadata={
                "phases_complete": 4,
                "tests_passing": 65,
                "sessions_unblocked": [1, 2, 3],
            },
        )

        assert profile.swarm_id == "session-4-sip"
        assert len(profile.capabilities) == 8
        assert Capability.INTEGRATION_SIP in profile.capabilities
        assert profile.reputation_score == 0.95  # 100% test pass rate


# Run tests with: pytest tests/unit/test_capability_schema.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
