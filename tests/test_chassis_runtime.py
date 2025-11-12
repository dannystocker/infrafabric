"""Unit tests for IF.chassis WASM runtime (P0.3.1)

Tests WASM runtime functionality:
- WASM module loading
- Sandbox isolation
- Task execution
- Resource tracking
- Witness integration
"""

import pytest
import time
from infrafabric.chassis import IFChassis, ServiceContract
from infrafabric import witness


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test"""
    witness.clear_operations()
    yield
    witness.clear_operations()


@pytest.fixture
def chassis():
    """Create IF.chassis instance"""
    return IFChassis()


@pytest.fixture
def sample_contract():
    """Create sample service contract"""
    return ServiceContract(
        swarm_id='session-7-test',
        max_memory_mb=256,
        max_cpu_percent=50,
        max_execution_time_seconds=60.0,
        slo_latency_ms=1000.0,
    )


@pytest.fixture
def sample_wasm_bytes():
    """Create minimal valid WASM module bytes

    This is a minimal WASM module that does nothing but is valid.
    (module) in WAT format compiles to these bytes.
    """
    # Minimal WASM module: (module)
    return bytes([
        0x00, 0x61, 0x73, 0x6d,  # \0asm - magic number
        0x01, 0x00, 0x00, 0x00,  # version 1
    ])


def test_chassis_initialization(chassis):
    """Test chassis initialization"""
    assert chassis.engine is not None
    assert len(chassis.loaded_swarms) == 0
    assert len(chassis.execution_history) == 0

    # Check witness logging
    ops = witness.get_operations(component='IF.chassis', operation='initialized')
    assert len(ops) == 1


def test_service_contract_creation(sample_contract):
    """Test service contract creation"""
    assert sample_contract.swarm_id == 'session-7-test'
    assert sample_contract.max_memory_mb == 256
    assert sample_contract.max_cpu_percent == 50

    contract_dict = sample_contract.to_dict()
    assert 'swarm_id' in contract_dict
    assert contract_dict['max_memory_mb'] == 256


def test_load_swarm_with_bytes(chassis, sample_contract, sample_wasm_bytes):
    """Test loading swarm with WASM bytes"""
    success = chassis.load_swarm(
        swarm_id='session-7-test',
        wasm_bytes=sample_wasm_bytes,
        contract=sample_contract
    )

    assert success == True
    assert chassis.is_swarm_loaded('session-7-test') == True

    # Check witness logging
    ops = witness.get_operations(component='IF.chassis', operation='swarm_loaded')
    assert len(ops) == 1
    assert ops[0].params['swarm_id'] == 'session-7-test'


def test_load_swarm_without_wasm_raises_error(chassis, sample_contract):
    """Test loading swarm without WASM data raises error"""
    with pytest.raises(ValueError, match="Either wasm_path or wasm_bytes must be provided"):
        chassis.load_swarm(
            swarm_id='session-7-test',
            contract=sample_contract
        )


def test_load_swarm_with_default_contract(chassis, sample_wasm_bytes):
    """Test loading swarm with default contract"""
    success = chassis.load_swarm(
        swarm_id='session-7-test',
        wasm_bytes=sample_wasm_bytes
    )

    assert success == True

    # Check default contract was created
    swarm_info = chassis.get_swarm_info('session-7-test')
    assert swarm_info is not None
    assert swarm_info['contract']['swarm_id'] == 'session-7-test'


def test_is_swarm_loaded(chassis, sample_wasm_bytes):
    """Test checking if swarm is loaded"""
    assert chassis.is_swarm_loaded('session-7-test') == False

    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)

    assert chassis.is_swarm_loaded('session-7-test') == True


def test_get_swarm_info(chassis, sample_contract, sample_wasm_bytes):
    """Test getting swarm info"""
    chassis.load_swarm(
        swarm_id='session-7-test',
        wasm_bytes=sample_wasm_bytes,
        contract=sample_contract
    )

    info = chassis.get_swarm_info('session-7-test')

    assert info is not None
    assert info['swarm_id'] == 'session-7-test'
    assert info['execution_count'] == 0
    assert 'loaded_at' in info
    assert 'uptime_seconds' in info
    assert 'contract' in info


def test_get_swarm_info_not_loaded(chassis):
    """Test getting info for non-existent swarm"""
    info = chassis.get_swarm_info('unknown-swarm')
    assert info is None


def test_execute_task_basic(chassis, sample_wasm_bytes):
    """Test basic task execution"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)

    result = chassis.execute_task(
        swarm_id='session-7-test',
        task_name='test_task',
        task_params={'param1': 'value1'}
    )

    assert result['success'] == True
    assert 'result' in result
    assert 'execution_time_ms' in result
    assert result['error'] is None

    # Check witness logging
    ops = witness.get_operations(component='IF.chassis', operation='task_executed')
    assert len(ops) == 1
    assert ops[0].params['task_name'] == 'test_task'


def test_execute_task_not_loaded(chassis):
    """Test executing task on non-loaded swarm raises error"""
    with pytest.raises(ValueError, match="Swarm not loaded"):
        chassis.execute_task('unknown-swarm', 'test_task')


def test_execute_task_tracks_count(chassis, sample_wasm_bytes):
    """Test that execution count is tracked"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)

    chassis.execute_task('session-7-test', 'task1')
    chassis.execute_task('session-7-test', 'task2')
    chassis.execute_task('session-7-test', 'task3')

    info = chassis.get_swarm_info('session-7-test')
    assert info['execution_count'] == 3


def test_execute_task_with_disallowed_operation(chassis, sample_wasm_bytes):
    """Test executing disallowed operation raises error"""
    contract = ServiceContract(
        swarm_id='session-7-test',
        allowed_operations=['task1', 'task2']  # No '*'
    )

    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes, contract=contract)

    with pytest.raises(ValueError, match="Operation not allowed"):
        chassis.execute_task('session-7-test', 'task3')


def test_unload_swarm(chassis, sample_wasm_bytes):
    """Test unloading swarm"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)
    assert chassis.is_swarm_loaded('session-7-test') == True

    success = chassis.unload_swarm('session-7-test')
    assert success == True
    assert chassis.is_swarm_loaded('session-7-test') == False

    # Check witness logging
    ops = witness.get_operations(component='IF.chassis', operation='swarm_unloaded')
    assert len(ops) == 1


def test_unload_swarm_not_loaded(chassis):
    """Test unloading non-existent swarm"""
    success = chassis.unload_swarm('unknown-swarm')
    assert success == False


def test_get_execution_history(chassis, sample_wasm_bytes):
    """Test getting execution history"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)

    chassis.execute_task('session-7-test', 'task1')
    chassis.execute_task('session-7-test', 'task2')

    history = chassis.get_execution_history()
    assert len(history) == 2
    assert history[0]['task_name'] == 'task1'
    assert history[1]['task_name'] == 'task2'


def test_get_execution_history_filtered_by_swarm(chassis, sample_wasm_bytes):
    """Test filtering execution history by swarm"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)
    chassis.load_swarm('session-1-test', wasm_bytes=sample_wasm_bytes)

    chassis.execute_task('session-7-test', 'task1')
    chassis.execute_task('session-1-test', 'task2')
    chassis.execute_task('session-7-test', 'task3')

    history = chassis.get_execution_history(swarm_id='session-7-test')
    assert len(history) == 2
    assert all(r['swarm_id'] == 'session-7-test' for r in history)


def test_get_execution_history_filtered_by_task(chassis, sample_wasm_bytes):
    """Test filtering execution history by task name"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)

    chassis.execute_task('session-7-test', 'task1')
    chassis.execute_task('session-7-test', 'task2')
    chassis.execute_task('session-7-test', 'task1')

    history = chassis.get_execution_history(task_name='task1')
    assert len(history) == 2
    assert all(r['task_name'] == 'task1' for r in history)


def test_get_swarm_stats(chassis, sample_wasm_bytes):
    """Test getting swarm statistics"""
    contract = ServiceContract(
        swarm_id='session-7-test',
        slo_latency_ms=1000.0
    )

    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes, contract=contract)

    # Execute some tasks
    chassis.execute_task('session-7-test', 'task1')
    chassis.execute_task('session-7-test', 'task2')

    stats = chassis.get_swarm_stats('session-7-test')

    assert stats['swarm_id'] == 'session-7-test'
    assert stats['total_executions'] == 2
    assert stats['success_count'] == 2
    assert stats['failure_count'] == 0
    assert stats['success_rate'] == 1.0
    assert stats['avg_execution_time_ms'] >= 0


def test_get_swarm_stats_not_loaded(chassis):
    """Test getting stats for non-loaded swarm raises error"""
    with pytest.raises(ValueError, match="Swarm not loaded"):
        chassis.get_swarm_stats('unknown-swarm')


def test_health_check(chassis, sample_wasm_bytes):
    """Test chassis health check"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)
    chassis.load_swarm('session-1-test', wasm_bytes=sample_wasm_bytes)

    chassis.execute_task('session-7-test', 'task1')

    health = chassis.health_check()

    assert health['status'] == 'healthy'
    assert health['engine'] == 'wasmtime'
    assert health['loaded_swarms'] == 2
    assert health['total_executions'] == 1
    assert 'session-7-test' in health['swarms']
    assert 'session-1-test' in health['swarms']


def test_slo_violation_logging(chassis, sample_wasm_bytes):
    """Test SLO violation logging"""
    contract = ServiceContract(
        swarm_id='session-7-test',
        slo_latency_ms=0.001  # Very low SLO to trigger violation
    )

    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes, contract=contract)

    # Execute task (will likely violate SLO)
    result = chassis.execute_task('session-7-test', 'task1')

    # Check if SLO violation was logged
    ops = witness.get_operations(component='IF.chassis', operation='slo_violation')
    # May or may not have violations depending on execution speed
    # Just check that the mechanism works
    if result['execution_time_ms'] > contract.slo_latency_ms:
        assert len(ops) >= 1


def test_multiple_swarms_loaded(chassis, sample_wasm_bytes):
    """Test loading multiple swarms simultaneously"""
    chassis.load_swarm('session-7-test', wasm_bytes=sample_wasm_bytes)
    chassis.load_swarm('session-1-test', wasm_bytes=sample_wasm_bytes)
    chassis.load_swarm('session-4-test', wasm_bytes=sample_wasm_bytes)

    assert chassis.is_swarm_loaded('session-7-test')
    assert chassis.is_swarm_loaded('session-1-test')
    assert chassis.is_swarm_loaded('session-4-test')

    health = chassis.health_check()
    assert health['loaded_swarms'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
