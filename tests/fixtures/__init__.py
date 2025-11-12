"""
Test Fixtures for IF.witness and CLI Integration Tests

Provides reusable test data and database fixtures for:
- Sessions 1-4 protocol testing (NDI, WebRTC, H.323, SIP)
- Cost tracking and optimization scenarios
- Hash chain verification
- Trace propagation
- CLI command testing (coordinator, governor, chassis, witness, optimise)

Usage:
    from tests.fixtures import (
        get_ndi_events,
        get_webrtc_events,
        get_h323_events,
        get_sip_events,
        get_cost_data,
        create_test_database,
        # CLI fixtures
        WITNESS_SAMPLE_ENTRIES,
        COORDINATOR_SAMPLE_TASKS,
        GOVERNOR_SAMPLE_SWARMS,
        witness_entries,
        coordinator_tasks,
    )
"""

from .witness_fixtures import (
    get_ndi_events,
    get_webrtc_events,
    get_h323_events,
    get_sip_events,
    get_cost_data,
    create_test_database,
)

from .cli_fixtures import (
    # Witness fixtures
    WITNESS_SAMPLE_ENTRIES,
    WITNESS_QUERY_FILTERS,
    WITNESS_SAMPLE_PAYLOADS,
    WITNESS_INVALID_PAYLOADS,
    # Coordinator fixtures
    COORDINATOR_SAMPLE_TASKS,
    COORDINATOR_CAS_SCENARIOS,
    # Governor fixtures
    GOVERNOR_SAMPLE_SWARMS,
    GOVERNOR_CAPABILITY_MATCH_SCENARIOS,
    GOVERNOR_BUDGET_SCENARIOS,
    # Chassis fixtures
    CHASSIS_SAMPLE_SANDBOXES,
    CHASSIS_RESOURCE_LIMIT_SCENARIOS,
    CHASSIS_SAMPLE_CREDENTIALS,
    # Optimise fixtures
    OPTIMISE_SAMPLE_OPERATIONS,
    OPTIMISE_COST_SCENARIOS,
    # Config fixtures
    SAMPLE_CONFIG_YAML,
    INVALID_CONFIG_SAMPLES,
    # Pytest fixtures
    witness_entries,
    witness_payloads,
    coordinator_tasks,
    governor_swarms,
    chassis_sandboxes,
    optimise_operations,
    temp_config_file,
    temp_witness_db,
    # Test helpers
    create_sample_witness_entry,
    create_sample_swarm_profile,
    create_sample_task,
)

__all__ = [
    # Original witness fixtures
    'get_ndi_events',
    'get_webrtc_events',
    'get_h323_events',
    'get_sip_events',
    'get_cost_data',
    'create_test_database',
    # CLI fixtures
    'WITNESS_SAMPLE_ENTRIES',
    'WITNESS_QUERY_FILTERS',
    'WITNESS_SAMPLE_PAYLOADS',
    'WITNESS_INVALID_PAYLOADS',
    'COORDINATOR_SAMPLE_TASKS',
    'COORDINATOR_CAS_SCENARIOS',
    'GOVERNOR_SAMPLE_SWARMS',
    'GOVERNOR_CAPABILITY_MATCH_SCENARIOS',
    'GOVERNOR_BUDGET_SCENARIOS',
    'CHASSIS_SAMPLE_SANDBOXES',
    'CHASSIS_RESOURCE_LIMIT_SCENARIOS',
    'CHASSIS_SAMPLE_CREDENTIALS',
    'OPTIMISE_SAMPLE_OPERATIONS',
    'OPTIMISE_COST_SCENARIOS',
    'SAMPLE_CONFIG_YAML',
    'INVALID_CONFIG_SAMPLES',
    'witness_entries',
    'witness_payloads',
    'coordinator_tasks',
    'governor_swarms',
    'chassis_sandboxes',
    'optimise_operations',
    'temp_config_file',
    'temp_witness_db',
    'create_sample_witness_entry',
    'create_sample_swarm_profile',
    'create_sample_task',
]
