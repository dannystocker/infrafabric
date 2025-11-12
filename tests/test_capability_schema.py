"""
Unit Tests for Capability Registry Schema (P0.2.1)

Tests for:
- Capability enum completeness
- SwarmProfile validation and serialization
- ResourcePolicy validation and serialization
- Capability manifest validation
- Capability matching algorithm

Author: Session 3 (H.323 Guardian Council)
Version: 1.0
Status: Phase 0 Development
"""

import pytest
import json
import tempfile
from pathlib import Path
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    validate_capability_manifest,
    get_capability_by_value,
    get_capabilities_by_category,
    calculate_capability_overlap,
)


# ==========================================
# Capability Enum Tests
# ==========================================

class TestCapabilityEnum:
    """Test Capability enum definition and coverage"""

    def test_capability_enum_has_minimum_20_types(self):
        """Verify at least 20 capability types are defined"""
        capabilities = list(Capability)
        assert len(capabilities) >= 20, \
            f"Expected at least 20 capabilities, found {len(capabilities)}"

    def test_capability_values_follow_category_colon_name_format(self):
        """Verify all capability values follow 'category:name' format"""
        for cap in Capability:
            assert ":" in cap.value, \
                f"Capability {cap.name} value '{cap.value}' should contain ':'"
            parts = cap.value.split(":")
            assert len(parts) == 2, \
                f"Capability {cap.name} value '{cap.value}' should have exactly one ':'"

    def test_code_analysis_capabilities_exist(self):
        """Verify code analysis capabilities are defined"""
        code_analysis_caps = get_capabilities_by_category("code-analysis")
        assert len(code_analysis_caps) >= 4, \
            "Expected at least 4 code analysis capabilities"
        assert Capability.CODE_ANALYSIS_PYTHON in code_analysis_caps
        assert Capability.CODE_ANALYSIS_RUST in code_analysis_caps

    def test_integration_capabilities_exist(self):
        """Verify integration capabilities are defined"""
        integration_caps = get_capabilities_by_category("integration")
        assert len(integration_caps) >= 5, \
            "Expected at least 5 integration capabilities"
        assert Capability.INTEGRATION_H323 in integration_caps
        assert Capability.INTEGRATION_SIP in integration_caps
        assert Capability.INTEGRATION_NDI in integration_caps

    def test_governance_capabilities_exist(self):
        """Verify governance capabilities are defined"""
        governance_caps = get_capabilities_by_category("governance")
        assert len(governance_caps) >= 3, \
            "Expected at least 3 governance capabilities"
        assert Capability.GOVERNANCE_VOTING in governance_caps
        assert Capability.GOVERNANCE_QUALITY_ASSESSMENT in governance_caps

    def test_docs_capabilities_exist(self):
        """Verify documentation capabilities are defined"""
        docs_caps = get_capabilities_by_category("docs")
        assert len(docs_caps) >= 3, \
            "Expected at least 3 documentation capabilities"
        assert Capability.DOCS_TECHNICAL_WRITING in docs_caps
        assert Capability.DOCS_API_DESIGN in docs_caps

    def test_get_capability_by_value(self):
        """Test capability lookup by string value"""
        cap = get_capability_by_value("integration:h323")
        assert cap == Capability.INTEGRATION_H323

        cap = get_capability_by_value("docs:technical-writing")
        assert cap == Capability.DOCS_TECHNICAL_WRITING

        cap = get_capability_by_value("invalid:capability")
        assert cap is None


# ==========================================
# SwarmProfile Tests
# ==========================================

class TestSwarmProfile:
    """Test SwarmProfile dataclass validation and serialization"""

    def test_create_valid_swarm_profile(self):
        """Test creating a valid SwarmProfile"""
        profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[
                Capability.GOVERNANCE_VOTING,
                Capability.INTEGRATION_H323,
                Capability.DOCS_TECHNICAL_WRITING
            ],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="sonnet",
            max_concurrent_tasks=8
        )

        assert profile.swarm_id == "guardian-council"
        assert len(profile.capabilities) == 3
        assert profile.cost_per_hour == 15.0
        assert profile.reputation_score == 0.98
        assert profile.model == "sonnet"

    def test_swarm_profile_requires_non_empty_swarm_id(self):
        """Test that empty swarm_id raises ValueError"""
        with pytest.raises(ValueError, match="swarm_id must be a non-empty string"):
            SwarmProfile(
                swarm_id="",
                capabilities=[Capability.CODE_ANALYSIS_PYTHON],
                cost_per_hour=2.0,
                reputation_score=0.5,
                current_budget_remaining=50.0,
                model="haiku"
            )

    def test_swarm_profile_requires_at_least_one_capability(self):
        """Test that empty capabilities list raises ValueError"""
        with pytest.raises(ValueError, match="must have at least one capability"):
            SwarmProfile(
                swarm_id="test-swarm",
                capabilities=[],
                cost_per_hour=2.0,
                reputation_score=0.5,
                current_budget_remaining=50.0,
                model="haiku"
            )

    def test_swarm_profile_validates_reputation_score_range(self):
        """Test that reputation_score must be between 0.0 and 1.0"""
        with pytest.raises(ValueError, match="reputation_score must be between 0.0 and 1.0"):
            SwarmProfile(
                swarm_id="test-swarm",
                capabilities=[Capability.CODE_ANALYSIS_PYTHON],
                cost_per_hour=2.0,
                reputation_score=1.5,  # Invalid: > 1.0
                current_budget_remaining=50.0,
                model="haiku"
            )

        with pytest.raises(ValueError, match="reputation_score must be between 0.0 and 1.0"):
            SwarmProfile(
                swarm_id="test-swarm",
                capabilities=[Capability.CODE_ANALYSIS_PYTHON],
                cost_per_hour=2.0,
                reputation_score=-0.1,  # Invalid: < 0.0
                current_budget_remaining=50.0,
                model="haiku"
            )

    def test_swarm_profile_validates_cost_per_hour(self):
        """Test that cost_per_hour must be non-negative"""
        with pytest.raises(ValueError, match="cost_per_hour must be a non-negative number"):
            SwarmProfile(
                swarm_id="test-swarm",
                capabilities=[Capability.CODE_ANALYSIS_PYTHON],
                cost_per_hour=-5.0,  # Invalid: negative
                reputation_score=0.5,
                current_budget_remaining=50.0,
                model="haiku"
            )

    def test_swarm_profile_validates_model(self):
        """Test that model must be a valid model type"""
        with pytest.raises(ValueError, match="model must be one of"):
            SwarmProfile(
                swarm_id="test-swarm",
                capabilities=[Capability.CODE_ANALYSIS_PYTHON],
                cost_per_hour=2.0,
                reputation_score=0.5,
                current_budget_remaining=50.0,
                model="gpt-4"  # Invalid: not a valid Claude model
            )

    def test_swarm_profile_validates_max_concurrent_tasks(self):
        """Test that max_concurrent_tasks must be positive integer"""
        with pytest.raises(ValueError, match="max_concurrent_tasks must be a positive integer"):
            SwarmProfile(
                swarm_id="test-swarm",
                capabilities=[Capability.CODE_ANALYSIS_PYTHON],
                cost_per_hour=2.0,
                reputation_score=0.5,
                current_budget_remaining=50.0,
                model="haiku",
                max_concurrent_tasks=0  # Invalid: must be >= 1
            )

    def test_swarm_profile_to_dict(self):
        """Test SwarmProfile serialization to dictionary"""
        profile = SwarmProfile(
            swarm_id="session-1-ndi",
            capabilities=[
                Capability.INTEGRATION_NDI,
                Capability.DOCS_TECHNICAL_WRITING
            ],
            cost_per_hour=2.0,
            reputation_score=0.92,
            current_budget_remaining=50.0,
            model="haiku",
            max_concurrent_tasks=3
        )

        data = profile.to_dict()

        assert data["swarm_id"] == "session-1-ndi"
        assert data["capabilities"] == ["integration:ndi", "docs:technical-writing"]
        assert data["cost_per_hour"] == 2.0
        assert data["reputation_score"] == 0.92
        assert data["model"] == "haiku"

    def test_swarm_profile_from_dict(self):
        """Test SwarmProfile deserialization from dictionary"""
        data = {
            "swarm_id": "session-4-sip",
            "capabilities": ["integration:sip", "testing:unit"],
            "cost_per_hour": 2.0,
            "reputation_score": 0.90,
            "current_budget_remaining": 50.0,
            "model": "haiku",
            "max_concurrent_tasks": 5
        }

        profile = SwarmProfile.from_dict(data)

        assert profile.swarm_id == "session-4-sip"
        assert Capability.INTEGRATION_SIP in profile.capabilities
        assert Capability.TESTING_UNIT in profile.capabilities
        assert profile.cost_per_hour == 2.0

    def test_swarm_profile_roundtrip_serialization(self):
        """Test that to_dict() and from_dict() roundtrip correctly"""
        original = SwarmProfile(
            swarm_id="test-roundtrip",
            capabilities=[
                Capability.ARCHITECTURE_SECURITY,
                Capability.TESTING_SECURITY
            ],
            cost_per_hour=15.0,
            reputation_score=0.85,
            current_budget_remaining=75.0,
            model="sonnet",
            max_concurrent_tasks=4,
            description="Test swarm for roundtrip"
        )

        data = original.to_dict()
        restored = SwarmProfile.from_dict(data)

        assert restored.swarm_id == original.swarm_id
        assert restored.capabilities == original.capabilities
        assert restored.cost_per_hour == original.cost_per_hour
        assert restored.reputation_score == original.reputation_score
        assert restored.model == original.model


# ==========================================
# ResourcePolicy Tests
# ==========================================

class TestResourcePolicy:
    """Test ResourcePolicy dataclass validation and serialization"""

    def test_create_valid_resource_policy(self):
        """Test creating a valid ResourcePolicy"""
        policy = ResourcePolicy(
            max_swarms_per_task=3,
            max_cost_per_task=10.0,
            min_capability_match=0.7,
            circuit_breaker_failure_threshold=3
        )

        assert policy.max_swarms_per_task == 3
        assert policy.max_cost_per_task == 10.0
        assert policy.min_capability_match == 0.7
        assert policy.circuit_breaker_failure_threshold == 3

    def test_resource_policy_default_values(self):
        """Test ResourcePolicy default values"""
        policy = ResourcePolicy()

        assert policy.max_swarms_per_task == 3
        assert policy.max_cost_per_task == 10.0
        assert policy.min_capability_match == 0.7
        assert policy.circuit_breaker_failure_threshold == 3
        assert policy.budget_warning_threshold == 0.2

    def test_resource_policy_validates_max_swarms_per_task(self):
        """Test that max_swarms_per_task must be positive"""
        with pytest.raises(ValueError, match="max_swarms_per_task must be a positive integer"):
            ResourcePolicy(max_swarms_per_task=0)

    def test_resource_policy_validates_max_cost_per_task(self):
        """Test that max_cost_per_task must be positive"""
        with pytest.raises(ValueError, match="max_cost_per_task must be a positive number"):
            ResourcePolicy(max_cost_per_task=-5.0)

    def test_resource_policy_validates_min_capability_match_range(self):
        """Test that min_capability_match must be between 0.0 and 1.0"""
        with pytest.raises(ValueError, match="min_capability_match must be between 0.0 and 1.0"):
            ResourcePolicy(min_capability_match=1.5)

        with pytest.raises(ValueError, match="min_capability_match must be between 0.0 and 1.0"):
            ResourcePolicy(min_capability_match=-0.1)

    def test_resource_policy_validates_circuit_breaker_threshold(self):
        """Test that circuit_breaker_failure_threshold must be positive"""
        with pytest.raises(ValueError, match="circuit_breaker_failure_threshold must be a positive integer"):
            ResourcePolicy(circuit_breaker_failure_threshold=0)

    def test_resource_policy_to_dict(self):
        """Test ResourcePolicy serialization to dictionary"""
        policy = ResourcePolicy(
            max_swarms_per_task=5,
            max_cost_per_task=20.0,
            min_capability_match=0.8,
            circuit_breaker_failure_threshold=5
        )

        data = policy.to_dict()

        assert data["max_swarms_per_task"] == 5
        assert data["max_cost_per_task"] == 20.0
        assert data["min_capability_match"] == 0.8

    def test_resource_policy_from_dict(self):
        """Test ResourcePolicy deserialization from dictionary"""
        data = {
            "max_swarms_per_task": 2,
            "max_cost_per_task": 5.0,
            "min_capability_match": 0.9,
            "circuit_breaker_failure_threshold": 2,
            "budget_warning_threshold": 0.1
        }

        policy = ResourcePolicy.from_dict(data)

        assert policy.max_swarms_per_task == 2
        assert policy.max_cost_per_task == 5.0
        assert policy.min_capability_match == 0.9


# ==========================================
# Capability Manifest Validation Tests
# ==========================================

class TestCapabilityManifestValidation:
    """Test capability manifest file validation"""

    def test_validate_valid_capability_manifest(self):
        """Test validation of a valid capability manifest JSON file"""
        manifest = {
            "swarm_id": "guardian-council",
            "capabilities": ["governance:voting", "integration:h323"],
            "cost_per_hour": 15.0,
            "reputation_score": 0.98,
            "current_budget_remaining": 100.0,
            "model": "sonnet",
            "max_concurrent_tasks": 8
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest, f)
            temp_path = Path(f.name)

        try:
            assert validate_capability_manifest(temp_path) is True
        finally:
            temp_path.unlink()

    def test_validate_manifest_missing_required_fields(self):
        """Test validation fails for manifest missing required fields"""
        manifest = {
            "swarm_id": "test-swarm",
            # Missing capabilities, cost_per_hour, etc.
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Invalid capability manifest"):
                validate_capability_manifest(temp_path)
        finally:
            temp_path.unlink()

    def test_validate_manifest_invalid_capability_values(self):
        """Test validation fails for invalid capability values"""
        manifest = {
            "swarm_id": "test-swarm",
            "capabilities": ["invalid:capability", "another:invalid"],
            "cost_per_hour": 2.0,
            "reputation_score": 0.5,
            "current_budget_remaining": 50.0,
            "model": "haiku"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError):
                validate_capability_manifest(temp_path)
        finally:
            temp_path.unlink()

    def test_validate_manifest_file_not_found(self):
        """Test validation raises FileNotFoundError for missing file"""
        with pytest.raises(FileNotFoundError):
            validate_capability_manifest(Path("/nonexistent/manifest.json"))


# ==========================================
# Capability Matching Algorithm Tests
# ==========================================

class TestCapabilityMatchingAlgorithm:
    """Test capability overlap calculation (Jaccard similarity)"""

    def test_calculate_overlap_perfect_match(self):
        """Test capability overlap for perfect match (100%)"""
        swarm_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.DOCS_TECHNICAL_WRITING
        ]
        required_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.DOCS_TECHNICAL_WRITING
        ]

        overlap = calculate_capability_overlap(swarm_caps, required_caps)
        assert overlap == 1.0

    def test_calculate_overlap_no_match(self):
        """Test capability overlap for no match (0%)"""
        swarm_caps = [
            Capability.INTEGRATION_NDI,
            Capability.INTEGRATION_RTMP
        ]
        required_caps = [
            Capability.CODE_ANALYSIS_RUST,
            Capability.TESTING_PERFORMANCE
        ]

        overlap = calculate_capability_overlap(swarm_caps, required_caps)
        assert overlap == 0.0

    def test_calculate_overlap_partial_match(self):
        """Test capability overlap for partial match"""
        swarm_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.TESTING_UNIT,
            Capability.DOCS_TECHNICAL_WRITING
        ]
        required_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.DOCS_TECHNICAL_WRITING
        ]

        overlap = calculate_capability_overlap(swarm_caps, required_caps)
        assert overlap == 1.0  # 2/2 required capabilities present

    def test_calculate_overlap_superset(self):
        """Test that swarm with more capabilities than required still matches"""
        swarm_caps = [
            Capability.GOVERNANCE_VOTING,
            Capability.GOVERNANCE_QUALITY_ASSESSMENT,
            Capability.INTEGRATION_H323,
            Capability.INTEGRATION_SIP,
            Capability.DOCS_TECHNICAL_WRITING
        ]
        required_caps = [
            Capability.GOVERNANCE_VOTING,
            Capability.INTEGRATION_H323
        ]

        overlap = calculate_capability_overlap(swarm_caps, required_caps)
        assert overlap == 1.0  # All required capabilities present

    def test_calculate_overlap_70_percent_threshold(self):
        """Test 70% capability match (typical IF.governor threshold)"""
        swarm_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.TESTING_UNIT,
            Capability.TESTING_INTEGRATION
        ]
        required_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.TESTING_UNIT,
            Capability.DOCS_TECHNICAL_WRITING  # Not in swarm
        ]

        overlap = calculate_capability_overlap(swarm_caps, required_caps)
        assert overlap == pytest.approx(0.666, abs=0.01)  # 2/3 ≈ 66.7%

    def test_calculate_overlap_empty_required_capabilities(self):
        """Test that empty required capabilities returns 0.0"""
        swarm_caps = [Capability.CODE_ANALYSIS_PYTHON]
        required_caps = []

        overlap = calculate_capability_overlap(swarm_caps, required_caps)
        assert overlap == 0.0

    def test_calculate_overlap_with_duplicates(self):
        """Test that duplicate capabilities don't affect overlap calculation"""
        swarm_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.CODE_ANALYSIS_PYTHON,  # Duplicate
            Capability.TESTING_UNIT
        ]
        required_caps = [
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.TESTING_UNIT
        ]

        overlap = calculate_capability_overlap(swarm_caps, required_caps)
        assert overlap == 1.0  # Sets eliminate duplicates


# ==========================================
# Integration Tests
# ==========================================

class TestCapabilitySchemaIntegration:
    """Integration tests for complete capability schema workflow"""

    def test_guardian_council_profile_workflow(self):
        """Test complete workflow for Guardian Council swarm profile"""
        # Create profile
        profile = SwarmProfile(
            swarm_id="guardian-council",
            capabilities=[
                Capability.GOVERNANCE_VOTING,
                Capability.GOVERNANCE_QUALITY_ASSESSMENT,
                Capability.INTEGRATION_H323,
                Capability.DOCS_TECHNICAL_WRITING
            ],
            cost_per_hour=15.0,
            reputation_score=0.98,
            current_budget_remaining=100.0,
            model="sonnet",
            max_concurrent_tasks=8,
            description="H.323 Guardian Council"
        )

        # Serialize
        data = profile.to_dict()
        json_str = json.dumps(data, indent=2)

        # Deserialize
        restored_data = json.loads(json_str)
        restored_profile = SwarmProfile.from_dict(restored_data)

        # Verify
        assert restored_profile.swarm_id == "guardian-council"
        assert len(restored_profile.capabilities) == 4
        assert Capability.GOVERNANCE_VOTING in restored_profile.capabilities

    def test_capability_matching_for_task_assignment(self):
        """Test capability matching for realistic task assignment scenario"""
        # Create swarm profiles
        guardian_profile = SwarmProfile(
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
        )

        ndi_profile = SwarmProfile(
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
        )

        # Task requires documentation
        required_caps = [Capability.DOCS_TECHNICAL_WRITING]

        # Both swarms can do documentation
        guardian_overlap = calculate_capability_overlap(
            guardian_profile.capabilities,
            required_caps
        )
        ndi_overlap = calculate_capability_overlap(
            ndi_profile.capabilities,
            required_caps
        )

        assert guardian_overlap == 1.0
        assert ndi_overlap == 1.0

        # IF.governor would pick ndi_profile (cheaper, 100% match)
        # Score = (overlap × reputation) / cost
        guardian_score = (guardian_overlap * guardian_profile.reputation_score) / guardian_profile.cost_per_hour
        ndi_score = (ndi_overlap * ndi_profile.reputation_score) / ndi_profile.cost_per_hour

        assert ndi_score > guardian_score  # NDI is more cost-effective


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
