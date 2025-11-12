"""
Unit Tests for Capability Registry Schema

Tests capability types, swarm profiles, resource policies, and validation logic.
"""

import pytest
from infrafabric.schemas.capability import (
    Capability,
    SwarmProfile,
    ResourcePolicy,
    CapabilityManifest,
    validate_capability_manifest,
    validate_swarm_profile,
    CAPABILITY_MANIFEST_JSON_SCHEMA,
)


# ==================== Capability Enum Tests ====================


def test_capability_enum_count():
    """Test that we have 20+ capability types."""
    capabilities = list(Capability)
    assert len(capabilities) >= 20, f"Expected at least 20 capabilities, got {len(capabilities)}"


def test_capability_from_string_valid():
    """Test parsing valid capability strings."""
    cap = Capability.from_string("code-analysis:rust")
    assert cap == Capability.CODE_ANALYSIS_RUST

    cap = Capability.from_string("integration:webrtc")
    assert cap == Capability.INTEGRATION_WEBRTC


def test_capability_from_string_invalid():
    """Test that invalid capability strings raise ValueError."""
    with pytest.raises(ValueError, match="Invalid capability"):
        Capability.from_string("invalid:capability")


def test_capability_from_list():
    """Test parsing list of capability strings."""
    caps = Capability.from_list([
        "code-analysis:python",
        "testing:unit",
        "integration:sip"
    ])
    assert len(caps) == 3
    assert Capability.CODE_ANALYSIS_PYTHON in caps
    assert Capability.TESTING_UNIT in caps
    assert Capability.INTEGRATION_SIP in caps


def test_capability_to_string_list():
    """Test converting capability enums to strings."""
    caps = [
        Capability.CODE_ANALYSIS_RUST,
        Capability.INTEGRATION_WEBRTC
    ]
    strings = Capability.to_string_list(caps)
    assert strings == ["code-analysis:rust", "integration:webrtc"]


def test_capability_get_category():
    """Test extracting category from capability."""
    assert Capability.get_category(Capability.CODE_ANALYSIS_RUST) == "code-analysis"
    assert Capability.get_category(Capability.INTEGRATION_SIP) == "integration"
    assert Capability.get_category(Capability.INFRA_KUBERNETES) == "infra"


def test_capability_get_all_categories():
    """Test getting all capability categories."""
    categories = Capability.get_all_categories()
    assert "code-analysis" in categories
    assert "integration" in categories
    assert "testing" in categories
    assert "infra" in categories
    assert "docs" in categories


# ==================== SwarmProfile Tests ====================


def test_swarm_profile_creation_valid():
    """Test creating valid SwarmProfile."""
    profile = SwarmProfile(
        swarm_id="swarm-webrtc-001",
        capabilities=[Capability.INTEGRATION_WEBRTC, Capability.CODE_ANALYSIS_JAVASCRIPT],
        cost_per_hour=15.0,
        reputation_score=0.95,
        current_budget_remaining=100.0,
        model="sonnet"
    )
    assert profile.swarm_id == "swarm-webrtc-001"
    assert len(profile.capabilities) == 2
    assert profile.cost_per_hour == 15.0
    assert profile.reputation_score == 0.95


def test_swarm_profile_defaults():
    """Test SwarmProfile default values."""
    profile = SwarmProfile(
        swarm_id="swarm-test",
        capabilities=[Capability.CLI_DESIGN],
        cost_per_hour=1.5
    )
    assert profile.reputation_score == 1.0
    assert profile.current_budget_remaining == 0.0
    assert profile.model == "haiku"
    assert profile.metadata == {}


def test_swarm_profile_invalid_swarm_id():
    """Test that invalid swarm_id raises ValueError."""
    with pytest.raises(ValueError, match="Invalid swarm_id"):
        SwarmProfile(
            swarm_id="Swarm_WEBRTC",  # Uppercase and underscore not allowed
            capabilities=[Capability.INTEGRATION_WEBRTC],
            cost_per_hour=15.0
        )


def test_swarm_profile_empty_capabilities():
    """Test that empty capabilities list raises ValueError."""
    with pytest.raises(ValueError, match="at least one capability"):
        SwarmProfile(
            swarm_id="swarm-test",
            capabilities=[],
            cost_per_hour=1.0
        )


def test_swarm_profile_invalid_capability_type():
    """Test that non-Capability objects in list raise ValueError."""
    with pytest.raises(ValueError, match="All capabilities must be Capability enum"):
        SwarmProfile(
            swarm_id="swarm-test",
            capabilities=["not-a-capability-enum"],  # String instead of enum
            cost_per_hour=1.0
        )


def test_swarm_profile_negative_cost():
    """Test that negative cost raises ValueError."""
    with pytest.raises(ValueError, match="cost_per_hour must be non-negative"):
        SwarmProfile(
            swarm_id="swarm-test",
            capabilities=[Capability.CLI_DESIGN],
            cost_per_hour=-5.0
        )


def test_swarm_profile_invalid_reputation():
    """Test that reputation outside 0.0-1.0 raises ValueError."""
    with pytest.raises(ValueError, match="reputation_score must be between"):
        SwarmProfile(
            swarm_id="swarm-test",
            capabilities=[Capability.CLI_DESIGN],
            cost_per_hour=1.0,
            reputation_score=1.5  # > 1.0
        )


def test_swarm_profile_negative_budget():
    """Test that negative budget raises ValueError."""
    with pytest.raises(ValueError, match="current_budget_remaining must be non-negative"):
        SwarmProfile(
            swarm_id="swarm-test",
            capabilities=[Capability.CLI_DESIGN],
            cost_per_hour=1.0,
            current_budget_remaining=-10.0
        )


def test_swarm_profile_invalid_model():
    """Test that invalid model raises ValueError."""
    with pytest.raises(ValueError, match="model must be one of"):
        SwarmProfile(
            swarm_id="swarm-test",
            capabilities=[Capability.CLI_DESIGN],
            cost_per_hour=1.0,
            model="gpt-4"  # Not a valid model
        )


def test_swarm_profile_to_dict():
    """Test converting SwarmProfile to dictionary."""
    profile = SwarmProfile(
        swarm_id="swarm-test",
        capabilities=[Capability.CODE_ANALYSIS_PYTHON],
        cost_per_hour=1.5,
        metadata={"version": "1.0"}
    )
    data = profile.to_dict()
    assert data['swarm_id'] == "swarm-test"
    assert data['capabilities'] == ["code-analysis:python"]
    assert data['cost_per_hour'] == 1.5
    assert data['metadata'] == {"version": "1.0"}


def test_swarm_profile_from_dict():
    """Test creating SwarmProfile from dictionary."""
    data = {
        'swarm_id': 'swarm-test',
        'capabilities': ['code-analysis:rust', 'testing:unit'],
        'cost_per_hour': 2.0,
        'model': 'haiku'
    }
    profile = SwarmProfile.from_dict(data)
    assert profile.swarm_id == 'swarm-test'
    assert len(profile.capabilities) == 2
    assert Capability.CODE_ANALYSIS_RUST in profile.capabilities


def test_swarm_profile_has_capability():
    """Test checking if swarm has a capability."""
    profile = SwarmProfile(
        swarm_id="swarm-test",
        capabilities=[Capability.INTEGRATION_WEBRTC, Capability.TESTING_INTEGRATION],
        cost_per_hour=15.0
    )
    assert profile.has_capability(Capability.INTEGRATION_WEBRTC) is True
    assert profile.has_capability(Capability.CODE_ANALYSIS_RUST) is False


def test_swarm_profile_has_capabilities_all():
    """Test checking if swarm has all required capabilities."""
    profile = SwarmProfile(
        swarm_id="swarm-test",
        capabilities=[
            Capability.INTEGRATION_WEBRTC,
            Capability.TESTING_INTEGRATION,
            Capability.CODE_ANALYSIS_JAVASCRIPT
        ],
        cost_per_hour=15.0
    )
    assert profile.has_capabilities([
        Capability.INTEGRATION_WEBRTC,
        Capability.TESTING_INTEGRATION
    ]) is True
    assert profile.has_capabilities([
        Capability.INTEGRATION_WEBRTC,
        Capability.CODE_ANALYSIS_RUST  # Not in profile
    ]) is False


def test_swarm_profile_get_capability_categories():
    """Test getting capability categories from swarm profile."""
    profile = SwarmProfile(
        swarm_id="swarm-test",
        capabilities=[
            Capability.CODE_ANALYSIS_PYTHON,
            Capability.CODE_ANALYSIS_RUST,
            Capability.TESTING_UNIT,
            Capability.INTEGRATION_WEBRTC
        ],
        cost_per_hour=15.0
    )
    categories = profile.get_capability_categories()
    assert "code-analysis" in categories
    assert "testing" in categories
    assert "integration" in categories
    assert len(categories) == 3


# ==================== ResourcePolicy Tests ====================


def test_resource_policy_defaults():
    """Test ResourcePolicy default values."""
    policy = ResourcePolicy()
    assert policy.max_swarms_per_task == 3
    assert policy.max_cost_per_task == 10.0
    assert policy.min_capability_match == 0.7
    assert policy.circuit_breaker_failure_threshold == 3
    assert policy.prefer_reputation is True
    assert policy.allow_budget_overdraft == 1.1


def test_resource_policy_custom():
    """Test creating ResourcePolicy with custom values."""
    policy = ResourcePolicy(
        max_swarms_per_task=5,
        max_cost_per_task=50.0,
        min_capability_match=0.8,
        circuit_breaker_failure_threshold=5,
        prefer_reputation=False,
        allow_budget_overdraft=1.2
    )
    assert policy.max_swarms_per_task == 5
    assert policy.max_cost_per_task == 50.0
    assert policy.min_capability_match == 0.8


def test_resource_policy_invalid_max_swarms():
    """Test that max_swarms < 1 raises ValueError."""
    with pytest.raises(ValueError, match="max_swarms_per_task must be at least 1"):
        ResourcePolicy(max_swarms_per_task=0)


def test_resource_policy_invalid_max_cost():
    """Test that max_cost <= 0 raises ValueError."""
    with pytest.raises(ValueError, match="max_cost_per_task must be positive"):
        ResourcePolicy(max_cost_per_task=0.0)


def test_resource_policy_invalid_min_capability_match():
    """Test that min_capability_match outside 0.0-1.0 raises ValueError."""
    with pytest.raises(ValueError, match="min_capability_match must be between"):
        ResourcePolicy(min_capability_match=1.5)


def test_resource_policy_invalid_circuit_breaker_threshold():
    """Test that circuit_breaker_threshold < 1 raises ValueError."""
    with pytest.raises(ValueError, match="circuit_breaker_failure_threshold must be at least 1"):
        ResourcePolicy(circuit_breaker_failure_threshold=0)


def test_resource_policy_invalid_overdraft():
    """Test that allow_budget_overdraft < 1.0 raises ValueError."""
    with pytest.raises(ValueError, match="allow_budget_overdraft must be at least 1.0"):
        ResourcePolicy(allow_budget_overdraft=0.5)


# ==================== CapabilityManifest Tests ====================


def test_capability_manifest_creation():
    """Test creating CapabilityManifest."""
    manifest = CapabilityManifest(
        swarm_id="swarm-test",
        capabilities=["code-analysis:python", "testing:unit"],
        cost_per_hour=2.0,
        model="haiku"
    )
    assert manifest.swarm_id == "swarm-test"
    assert len(manifest.capabilities) == 2


def test_capability_manifest_to_swarm_profile():
    """Test converting CapabilityManifest to SwarmProfile."""
    manifest = CapabilityManifest(
        swarm_id="swarm-test",
        capabilities=["integration:webrtc"],
        cost_per_hour=15.0,
        model="sonnet",
        reputation_score=0.9
    )
    profile = manifest.to_swarm_profile()
    assert profile.swarm_id == "swarm-test"
    assert Capability.INTEGRATION_WEBRTC in profile.capabilities
    assert profile.cost_per_hour == 15.0
    assert profile.model == "sonnet"
    assert profile.reputation_score == 0.9


def test_capability_manifest_from_swarm_profile():
    """Test creating CapabilityManifest from SwarmProfile."""
    profile = SwarmProfile(
        swarm_id="swarm-test",
        capabilities=[Capability.CODE_ANALYSIS_RUST],
        cost_per_hour=2.0,
        model="haiku",
        metadata={"version": "1.0"}
    )
    manifest = CapabilityManifest.from_swarm_profile(profile)
    assert manifest.swarm_id == "swarm-test"
    assert manifest.capabilities == ["code-analysis:rust"]
    assert manifest.metadata == {"version": "1.0"}


def test_capability_manifest_to_dict():
    """Test converting CapabilityManifest to dictionary."""
    manifest = CapabilityManifest(
        swarm_id="swarm-test",
        capabilities=["code-analysis:python"],
        cost_per_hour=1.5
    )
    data = manifest.to_dict()
    assert data['swarm_id'] == "swarm-test"
    assert data['capabilities'] == ["code-analysis:python"]


def test_capability_manifest_from_dict():
    """Test creating CapabilityManifest from dictionary."""
    data = {
        'swarm_id': 'swarm-test',
        'capabilities': ['integration:sip'],
        'cost_per_hour': 15.0,
        'model': 'sonnet'
    }
    manifest = CapabilityManifest.from_dict(data)
    assert manifest.swarm_id == 'swarm-test'
    assert manifest.capabilities == ['integration:sip']


# ==================== Validation Function Tests ====================


def test_validate_capability_manifest_valid():
    """Test validating valid capability manifest."""
    manifest = {
        'swarm_id': 'swarm-webrtc',
        'capabilities': ['integration:webrtc', 'code-analysis:javascript'],
        'cost_per_hour': 15.0,
        'model': 'sonnet',
        'reputation_score': 0.95
    }
    assert validate_capability_manifest(manifest) is True


def test_validate_capability_manifest_minimal():
    """Test validating minimal valid manifest (only required fields)."""
    manifest = {
        'swarm_id': 'swarm-test',
        'capabilities': ['cli:design'],
        'cost_per_hour': 1.0
    }
    assert validate_capability_manifest(manifest) is True


def test_validate_capability_manifest_missing_required():
    """Test that missing required fields raises ValueError."""
    manifest = {
        'swarm_id': 'swarm-test',
        # Missing 'capabilities' and 'cost_per_hour'
    }
    with pytest.raises(ValueError, match="Missing required fields"):
        validate_capability_manifest(manifest)


def test_validate_capability_manifest_invalid_swarm_id():
    """Test that invalid swarm_id format raises ValueError."""
    manifest = {
        'swarm_id': 'Swarm_TEST',  # Uppercase and underscore
        'capabilities': ['cli:design'],
        'cost_per_hour': 1.0
    }
    with pytest.raises(ValueError, match="Invalid swarm_id"):
        validate_capability_manifest(manifest)


def test_validate_capability_manifest_empty_capabilities():
    """Test that empty capabilities list raises ValueError."""
    manifest = {
        'swarm_id': 'swarm-test',
        'capabilities': [],
        'cost_per_hour': 1.0
    }
    with pytest.raises(ValueError, match="must be a non-empty list"):
        validate_capability_manifest(manifest)


def test_validate_capability_manifest_invalid_capability():
    """Test that invalid capability string raises ValueError."""
    manifest = {
        'swarm_id': 'swarm-test',
        'capabilities': ['invalid:capability'],
        'cost_per_hour': 1.0
    }
    with pytest.raises(ValueError, match="Invalid capability"):
        validate_capability_manifest(manifest)


def test_validate_capability_manifest_negative_cost():
    """Test that negative cost raises ValueError."""
    manifest = {
        'swarm_id': 'swarm-test',
        'capabilities': ['cli:design'],
        'cost_per_hour': -1.0
    }
    with pytest.raises(ValueError, match="cost_per_hour must be non-negative"):
        validate_capability_manifest(manifest)


def test_validate_capability_manifest_invalid_model():
    """Test that invalid model raises ValueError."""
    manifest = {
        'swarm_id': 'swarm-test',
        'capabilities': ['cli:design'],
        'cost_per_hour': 1.0,
        'model': 'gpt-4'
    }
    with pytest.raises(ValueError, match="model must be one of"):
        validate_capability_manifest(manifest)


def test_validate_capability_manifest_invalid_reputation():
    """Test that reputation outside 0.0-1.0 raises ValueError."""
    manifest = {
        'swarm_id': 'swarm-test',
        'capabilities': ['cli:design'],
        'cost_per_hour': 1.0,
        'reputation_score': 2.0
    }
    with pytest.raises(ValueError, match="reputation_score must be between"):
        validate_capability_manifest(manifest)


def test_validate_capability_manifest_invalid_metadata():
    """Test that non-dict metadata raises ValueError."""
    manifest = {
        'swarm_id': 'swarm-test',
        'capabilities': ['cli:design'],
        'cost_per_hour': 1.0,
        'metadata': "not-a-dict"
    }
    with pytest.raises(ValueError, match="metadata must be a dictionary"):
        validate_capability_manifest(manifest)


def test_validate_swarm_profile_valid():
    """Test validating valid SwarmProfile."""
    profile = SwarmProfile(
        swarm_id="swarm-test",
        capabilities=[Capability.CLI_DESIGN],
        cost_per_hour=1.0
    )
    assert validate_swarm_profile(profile) is True


def test_validate_swarm_profile_invalid_type():
    """Test that non-SwarmProfile object raises ValueError."""
    with pytest.raises(ValueError, match="Expected SwarmProfile"):
        validate_swarm_profile({"not": "a swarm profile"})


# ==================== JSON Schema Tests ====================


def test_json_schema_definition_exists():
    """Test that JSON schema definition is available."""
    assert CAPABILITY_MANIFEST_JSON_SCHEMA is not None
    assert CAPABILITY_MANIFEST_JSON_SCHEMA['$schema'] == "http://json-schema.org/draft-07/schema#"


def test_json_schema_required_fields():
    """Test that JSON schema defines required fields."""
    required = CAPABILITY_MANIFEST_JSON_SCHEMA['required']
    assert 'swarm_id' in required
    assert 'capabilities' in required
    assert 'cost_per_hour' in required


def test_json_schema_properties():
    """Test that JSON schema defines all properties."""
    props = CAPABILITY_MANIFEST_JSON_SCHEMA['properties']
    assert 'swarm_id' in props
    assert 'capabilities' in props
    assert 'cost_per_hour' in props
    assert 'model' in props
    assert 'reputation_score' in props
    assert 'metadata' in props


def test_json_schema_capability_enum():
    """Test that JSON schema includes all capability values in enum."""
    cap_items = CAPABILITY_MANIFEST_JSON_SCHEMA['properties']['capabilities']['items']
    cap_enum = cap_items['enum']

    # Check that we have all capabilities in the enum
    all_cap_values = [c.value for c in Capability]
    assert set(cap_enum) == set(all_cap_values)


# ==================== Integration Tests ====================


def test_full_workflow_manifest_to_profile():
    """Test full workflow: JSON dict → CapabilityManifest → SwarmProfile."""
    # Step 1: Validate JSON manifest
    manifest_dict = {
        'swarm_id': 'swarm-webrtc',
        'capabilities': ['integration:webrtc', 'testing:integration'],
        'cost_per_hour': 15.0,
        'model': 'sonnet',
        'reputation_score': 0.95,
        'metadata': {'session': 'session-2', 'version': '1.0'}
    }
    assert validate_capability_manifest(manifest_dict) is True

    # Step 2: Create CapabilityManifest
    manifest = CapabilityManifest.from_dict(manifest_dict)
    assert manifest.swarm_id == 'swarm-webrtc'

    # Step 3: Convert to SwarmProfile
    profile = manifest.to_swarm_profile()
    assert profile.swarm_id == 'swarm-webrtc'
    assert Capability.INTEGRATION_WEBRTC in profile.capabilities
    assert profile.cost_per_hour == 15.0
    assert profile.model == 'sonnet'


def test_full_workflow_profile_to_manifest():
    """Test full workflow: SwarmProfile → CapabilityManifest → JSON dict."""
    # Step 1: Create SwarmProfile
    profile = SwarmProfile(
        swarm_id='swarm-sip',
        capabilities=[Capability.INTEGRATION_SIP, Capability.CODE_ANALYSIS_GO],
        cost_per_hour=18.0,
        model='sonnet',
        reputation_score=0.88,
        metadata={'version': '2.0'}
    )

    # Step 2: Convert to CapabilityManifest
    manifest = CapabilityManifest.from_swarm_profile(profile)
    assert manifest.swarm_id == 'swarm-sip'
    assert 'integration:sip' in manifest.capabilities

    # Step 3: Convert to dict and validate
    manifest_dict = manifest.to_dict()
    assert validate_capability_manifest(manifest_dict) is True


def test_capability_matching_workflow():
    """Test workflow for capability-based swarm matching."""
    # Create multiple swarm profiles
    webrtc_swarm = SwarmProfile(
        swarm_id='swarm-webrtc',
        capabilities=[Capability.INTEGRATION_WEBRTC, Capability.TESTING_INTEGRATION],
        cost_per_hour=15.0,
        model='sonnet'
    )

    sip_swarm = SwarmProfile(
        swarm_id='swarm-sip',
        capabilities=[Capability.INTEGRATION_SIP, Capability.INTEGRATION_GRPC],
        cost_per_hour=18.0,
        model='sonnet'
    )

    # Task requires WebRTC capability
    required_caps = [Capability.INTEGRATION_WEBRTC]

    # Check which swarm matches
    assert webrtc_swarm.has_capabilities(required_caps) is True
    assert sip_swarm.has_capabilities(required_caps) is False

    # Verify cost and model for matched swarm
    assert webrtc_swarm.cost_per_hour == 15.0
    assert webrtc_swarm.model == 'sonnet'
