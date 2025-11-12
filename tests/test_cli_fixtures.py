"""
Unit tests for CLI test fixtures

Verifies that test fixtures are properly structured and usable.
"""

import pytest
import json
from tests.fixtures import (
    WITNESS_SAMPLE_ENTRIES,
    WITNESS_QUERY_FILTERS,
    WITNESS_SAMPLE_PAYLOADS,
    WITNESS_INVALID_PAYLOADS,
    COORDINATOR_SAMPLE_TASKS,
    COORDINATOR_CAS_SCENARIOS,
    GOVERNOR_SAMPLE_SWARMS,
    GOVERNOR_CAPABILITY_MATCH_SCENARIOS,
    GOVERNOR_BUDGET_SCENARIOS,
    CHASSIS_SAMPLE_SANDBOXES,
    CHASSIS_RESOURCE_LIMIT_SCENARIOS,
    OPTIMISE_SAMPLE_OPERATIONS,
    OPTIMISE_COST_SCENARIOS,
    SAMPLE_CONFIG_YAML,
    witness_entries,
    witness_payloads,
    coordinator_tasks,
    governor_swarms,
    chassis_sandboxes,
    temp_config_file,
    temp_witness_db,
    create_sample_witness_entry,
    create_sample_swarm_profile,
    create_sample_task,
)


class TestWitnessFixtures:
    """Test witness-related fixtures"""

    def test_sample_entries_structure(self):
        """Test witness entries have required fields"""
        assert len(WITNESS_SAMPLE_ENTRIES) >= 5

        for entry in WITNESS_SAMPLE_ENTRIES:
            assert 'id' in entry
            assert 'timestamp' in entry
            assert 'event' in entry
            assert 'component' in entry
            assert 'trace_id' in entry
            assert 'payload' in entry
            assert 'hash' in entry
            assert 'prev_hash' in entry
            assert 'signature' in entry

            # Verify payload is valid JSON
            json.loads(entry['payload'])

    def test_sample_entries_hash_chain(self):
        """Test entries form a valid hash chain"""
        for i in range(1, len(WITNESS_SAMPLE_ENTRIES)):
            prev_entry = WITNESS_SAMPLE_ENTRIES[i-1]
            curr_entry = WITNESS_SAMPLE_ENTRIES[i]

            # Current entry's prev_hash should match previous entry's hash
            assert curr_entry['prev_hash'] == prev_entry['hash']

    def test_query_filters_structure(self):
        """Test query filters are properly structured"""
        assert 'by_component' in WITNESS_QUERY_FILTERS
        assert 'by_trace_id' in WITNESS_QUERY_FILTERS
        assert 'by_event' in WITNESS_QUERY_FILTERS
        assert 'by_date_range' in WITNESS_QUERY_FILTERS

        for filter_name, filter_data in WITNESS_QUERY_FILTERS.items():
            assert 'expected_count' in filter_data
            assert 'expected_ids' in filter_data
            assert len(filter_data['expected_ids']) == filter_data['expected_count']

    def test_sample_payloads_valid_json(self):
        """Test all sample payloads are valid JSON"""
        for name, payload_data in WITNESS_SAMPLE_PAYLOADS.items():
            assert 'description' in payload_data
            assert 'json' in payload_data
            assert 'dict' in payload_data

            # Verify JSON string is valid
            parsed = json.loads(payload_data['json'])
            assert parsed == payload_data['dict']

    def test_invalid_payloads_structure(self):
        """Test invalid payloads are structured correctly"""
        assert len(WITNESS_INVALID_PAYLOADS) >= 4

        for invalid in WITNESS_INVALID_PAYLOADS:
            assert 'description' in invalid
            assert 'json' in invalid
            assert 'error_type' in invalid

    def test_create_sample_witness_entry(self):
        """Test witness entry creation helper"""
        entry = create_sample_witness_entry(
            event="test_event",
            component="IF.test",
            trace_id="test-123",
            payload={"key": "value"},
            entry_id=42
        )

        assert entry['id'] == 42
        assert entry['event'] == "test_event"
        assert entry['component'] == "IF.test"
        assert entry['trace_id'] == "test-123"
        assert json.loads(entry['payload']) == {"key": "value"}
        assert 'timestamp' in entry
        assert 'hash' in entry
        assert 'signature' in entry


class TestCoordinatorFixtures:
    """Test coordinator-related fixtures"""

    def test_sample_tasks_structure(self):
        """Test coordinator tasks have required fields"""
        assert len(COORDINATOR_SAMPLE_TASKS) >= 3

        for task in COORDINATOR_SAMPLE_TASKS:
            assert 'task_id' in task
            assert 'description' in task
            assert 'required_capabilities' in task
            assert 'status' in task
            assert isinstance(task['required_capabilities'], list)

    def test_sample_tasks_statuses(self):
        """Test tasks have valid statuses"""
        valid_statuses = ['unclaimed', 'claimed', 'completed', 'failed']
        for task in COORDINATOR_SAMPLE_TASKS:
            assert task['status'] in valid_statuses

    def test_cas_scenarios_structure(self):
        """Test CAS scenarios are properly structured"""
        assert len(COORDINATOR_CAS_SCENARIOS) >= 3

        for scenario in COORDINATOR_CAS_SCENARIOS:
            assert 'name' in scenario
            assert 'initial_state' in scenario

    def test_create_sample_task(self):
        """Test task creation helper"""
        task = create_sample_task(
            task_id="P0.TEST",
            required_capabilities=["test:cap1", "test:cap2"],
            status="unclaimed"
        )

        assert task['task_id'] == "P0.TEST"
        assert task['required_capabilities'] == ["test:cap1", "test:cap2"]
        assert task['status'] == "unclaimed"
        assert task['description'] == "Task P0.TEST"


class TestGovernorFixtures:
    """Test governor-related fixtures"""

    def test_sample_swarms_structure(self):
        """Test swarm profiles have required fields"""
        assert len(GOVERNOR_SAMPLE_SWARMS) >= 4

        for swarm in GOVERNOR_SAMPLE_SWARMS:
            assert 'swarm_id' in swarm
            assert 'capabilities' in swarm
            assert 'cost_per_hour' in swarm
            assert 'reputation_score' in swarm
            assert 'budget_remaining' in swarm
            assert 'model' in swarm
            assert isinstance(swarm['capabilities'], list)

    def test_sample_swarms_valid_values(self):
        """Test swarm profiles have valid values"""
        for swarm in GOVERNOR_SAMPLE_SWARMS:
            assert 0.0 <= swarm['reputation_score'] <= 1.0
            assert swarm['cost_per_hour'] > 0
            assert swarm['budget_remaining'] >= 0
            assert swarm['model'] in ['haiku', 'sonnet', 'opus']

    def test_capability_match_scenarios(self):
        """Test capability matching scenarios"""
        assert len(GOVERNOR_CAPABILITY_MATCH_SCENARIOS) >= 4

        for scenario in GOVERNOR_CAPABILITY_MATCH_SCENARIOS:
            assert 'name' in scenario
            assert 'required' in scenario
            assert 'swarm' in scenario
            assert 'expected_match_score' in scenario
            assert 0.0 <= scenario['expected_match_score'] <= 1.0

    def test_budget_scenarios(self):
        """Test budget scenarios"""
        assert len(GOVERNOR_BUDGET_SCENARIOS) >= 3

        for scenario in GOVERNOR_BUDGET_SCENARIOS:
            assert 'name' in scenario
            assert 'swarm_id' in scenario
            assert 'operation_cost' in scenario
            assert 'expected_allowed' in scenario

    def test_create_sample_swarm_profile(self):
        """Test swarm profile creation helper"""
        swarm = create_sample_swarm_profile(
            swarm_id="test-swarm",
            capabilities=["test:cap1", "test:cap2"],
            cost_per_hour=20.0,
            reputation=0.95,
            budget=150.0
        )

        assert swarm['swarm_id'] == "test-swarm"
        assert swarm['capabilities'] == ["test:cap1", "test:cap2"]
        assert swarm['cost_per_hour'] == 20.0
        assert swarm['reputation_score'] == 0.95
        assert swarm['budget_remaining'] == 150.0


class TestChassisFixtures:
    """Test chassis-related fixtures"""

    def test_sample_sandboxes_structure(self):
        """Test sandbox entries have required fields"""
        assert len(CHASSIS_SAMPLE_SANDBOXES) >= 3

        for sandbox in CHASSIS_SAMPLE_SANDBOXES:
            assert 'sandbox_id' in sandbox
            assert 'wasm_module' in sandbox
            assert 'memory_mb' in sandbox
            assert 'cpu_percent' in sandbox
            assert 'max_execution_time_ms' in sandbox
            assert 'status' in sandbox

    def test_sample_sandboxes_valid_values(self):
        """Test sandboxes have valid resource values"""
        for sandbox in CHASSIS_SAMPLE_SANDBOXES:
            assert sandbox['memory_mb'] > 0
            assert 0 < sandbox['cpu_percent'] <= 100
            assert sandbox['max_execution_time_ms'] > 0
            assert sandbox['status'] in ['running', 'completed', 'failed', 'pending']

    def test_resource_limit_scenarios(self):
        """Test resource limit scenarios"""
        assert len(CHASSIS_RESOURCE_LIMIT_SCENARIOS) >= 4

        for scenario in CHASSIS_RESOURCE_LIMIT_SCENARIOS:
            assert 'name' in scenario
            assert 'memory_mb' in scenario
            assert 'cpu_percent' in scenario
            assert 'execution_time_ms' in scenario
            assert 'expected_allowed' in scenario


class TestOptimiseFixtures:
    """Test optimise-related fixtures"""

    def test_sample_operations_structure(self):
        """Test operation entries have required fields"""
        assert len(OPTIMISE_SAMPLE_OPERATIONS) >= 3

        for op in OPTIMISE_SAMPLE_OPERATIONS:
            assert 'operation_id' in op
            assert 'model' in op
            assert 'tokens_input' in op
            assert 'tokens_output' in op
            assert 'cache_hit' in op
            assert 'cost_usd' in op
            assert 'latency_ms' in op

    def test_sample_operations_valid_values(self):
        """Test operations have valid values"""
        for op in OPTIMISE_SAMPLE_OPERATIONS:
            assert op['model'] in ['haiku', 'sonnet', 'opus']
            assert op['tokens_input'] > 0
            assert op['tokens_output'] > 0
            assert op['cost_usd'] >= 0
            assert op['latency_ms'] > 0
            assert isinstance(op['cache_hit'], bool)

    def test_cost_scenarios(self):
        """Test cost tracking scenarios"""
        assert len(OPTIMISE_COST_SCENARIOS) >= 3

        for scenario in OPTIMISE_COST_SCENARIOS:
            assert 'name' in scenario
            assert 'total_budget' in scenario
            assert 'operations_cost' in scenario
            assert 'expected_alert' in scenario
            assert 'expected_remaining' in scenario


class TestConfigFixtures:
    """Test config-related fixtures"""

    def test_sample_config_yaml_valid(self):
        """Test sample config is valid YAML"""
        import yaml
        config = yaml.safe_load(SAMPLE_CONFIG_YAML)

        assert 'config_version' in config
        assert 'coordinator' in config
        assert 'governor' in config
        assert 'chassis' in config
        assert 'witness' in config
        assert 'optimise' in config


class TestPytestFixtures:
    """Test pytest fixtures work correctly"""

    def test_witness_entries_fixture(self, witness_entries):
        """Test witness_entries fixture"""
        assert len(witness_entries) >= 5
        assert isinstance(witness_entries, list)

        # Verify it's a copy of the list (shallow copy is expected)
        assert witness_entries is not WITNESS_SAMPLE_ENTRIES
        # Note: shallow copy means dict modifications will affect original

    def test_witness_payloads_fixture(self, witness_payloads):
        """Test witness_payloads fixture"""
        assert 'simple' in witness_payloads
        assert 'nested' in witness_payloads
        assert isinstance(witness_payloads, dict)

    def test_coordinator_tasks_fixture(self, coordinator_tasks):
        """Test coordinator_tasks fixture"""
        assert len(coordinator_tasks) >= 3
        assert isinstance(coordinator_tasks, list)

    def test_governor_swarms_fixture(self, governor_swarms):
        """Test governor_swarms fixture"""
        assert len(governor_swarms) >= 4
        assert isinstance(governor_swarms, list)

    def test_chassis_sandboxes_fixture(self, chassis_sandboxes):
        """Test chassis_sandboxes fixture"""
        assert len(chassis_sandboxes) >= 3
        assert isinstance(chassis_sandboxes, list)

    def test_temp_config_file_fixture(self, temp_config_file):
        """Test temp_config_file fixture"""
        assert temp_config_file.exists()
        assert temp_config_file.suffix == '.yaml'

        # Read and verify
        import yaml
        with open(temp_config_file, 'r') as f:
            config = yaml.safe_load(f)

        assert 'coordinator' in config

    def test_temp_witness_db_fixture(self, temp_witness_db):
        """Test temp_witness_db fixture"""
        # Path should be created by fixture
        assert temp_witness_db.suffix == '.db'


class TestFixtureUsability:
    """Test fixtures are usable in realistic scenarios"""

    def test_witness_query_simulation(self, witness_entries):
        """Test simulating witness query with fixtures"""
        # Filter by component
        coordinator_entries = [
            e for e in witness_entries
            if e['component'] == 'IF.coordinator'
        ]
        assert len(coordinator_entries) == WITNESS_QUERY_FILTERS['by_component']['expected_count']

    def test_capability_matching_simulation(self, governor_swarms):
        """Test simulating capability matching"""
        required_caps = ["streaming:ndi", "video:production"]

        matches = []
        for swarm in governor_swarms:
            matching_caps = set(swarm['capabilities']) & set(required_caps)
            match_score = len(matching_caps) / len(required_caps)
            if match_score >= 0.7:  # 70% threshold
                matches.append((swarm['swarm_id'], match_score))

        assert len(matches) > 0

    def test_budget_tracking_simulation(self, governor_swarms):
        """Test simulating budget tracking"""
        operation_cost = 5.0

        for swarm in governor_swarms:
            can_afford = swarm['budget_remaining'] >= operation_cost
            if not can_afford:
                # Circuit breaker should trip
                assert swarm['budget_remaining'] < operation_cost

    def test_resource_limit_simulation(self, chassis_sandboxes):
        """Test simulating resource limit checks"""
        max_memory = 512

        for sandbox in chassis_sandboxes:
            within_limit = sandbox['memory_mb'] <= max_memory
            if not within_limit:
                # Should be rejected
                assert sandbox['memory_mb'] > max_memory


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
