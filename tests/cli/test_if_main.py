"""
Unit Tests for InfraFabric CLI

Tests CLI commands, argument parsing, and help text.
"""

import pytest
from click.testing import CliRunner
from src.cli.if_main import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


# ==================== Main CLI Tests ====================


def test_cli_help(runner):
    """Test main CLI help text."""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'InfraFabric' in result.output
    assert 'coordinator' in result.output
    assert 'governor' in result.output
    assert 'chassis' in result.output
    assert 'witness' in result.output
    assert 'optimise' in result.output


def test_cli_version(runner):
    """Test CLI version command."""
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert '0.1.0' in result.output


def test_cli_debug_flag(runner):
    """Test debug flag."""
    result = runner.invoke(cli, ['--debug', 'coordinator', '--help'])
    assert result.exit_code == 0
    assert 'DEBUG' in result.output


# ==================== Coordinator Commands ====================


def test_coordinator_help(runner):
    """Test coordinator help."""
    result = runner.invoke(cli, ['coordinator', '--help'])
    assert result.exit_code == 0
    assert 'IF.coordinator' in result.output
    assert 'Real-time swarm coordination' in result.output


def test_coordinator_start(runner):
    """Test coordinator start command."""
    result = runner.invoke(cli, ['coordinator', 'start'])
    assert result.exit_code == 0
    assert 'Starting IF.coordinator' in result.output
    assert 'etcd' in result.output  # Default backend


def test_coordinator_start_with_backend(runner):
    """Test coordinator start with custom backend."""
    result = runner.invoke(cli, ['coordinator', 'start', '--backend', 'nats'])
    assert result.exit_code == 0
    assert 'nats' in result.output


def test_coordinator_status(runner):
    """Test coordinator status command."""
    result = runner.invoke(cli, ['coordinator', 'status'])
    assert result.exit_code == 0
    assert 'Status' in result.output


def test_coordinator_status_json(runner):
    """Test coordinator status with JSON format."""
    result = runner.invoke(cli, ['coordinator', 'status', '--format', 'json'])
    assert result.exit_code == 0
    assert '"status"' in result.output
    assert '"registered_swarms"' in result.output


def test_coordinator_register_swarm(runner):
    """Test registering a swarm with coordinator."""
    result = runner.invoke(cli, [
        'coordinator', 'register-swarm', 'swarm-test',
        '--capabilities', 'integration:webrtc',
        '--capabilities', 'testing:integration'
    ])
    assert result.exit_code == 0
    assert 'swarm-test' in result.output
    assert 'registered' in result.output.lower()


# ==================== Governor Commands ====================


def test_governor_help(runner):
    """Test governor help."""
    result = runner.invoke(cli, ['governor', '--help'])
    assert result.exit_code == 0
    assert 'IF.governor' in result.output
    assert 'Capability-aware' in result.output


def test_governor_register(runner):
    """Test governor register command."""
    result = runner.invoke(cli, [
        'governor', 'register', 'swarm-webrtc',
        '--capabilities', 'integration:webrtc',
        '--cost', '15.0',
        '--model', 'sonnet'
    ])
    assert result.exit_code == 0
    assert 'swarm-webrtc' in result.output
    assert '15.0' in result.output


def test_governor_match(runner):
    """Test governor match command."""
    result = runner.invoke(cli, [
        'governor', 'match',
        '--capabilities', 'integration:webrtc',
        '--max-cost', '20.0'
    ])
    assert result.exit_code == 0
    assert 'Finding swarms' in result.output


def test_governor_budget_report(runner):
    """Test governor budget report."""
    result = runner.invoke(cli, ['governor', 'budget', 'report'])
    assert result.exit_code == 0
    assert 'Budget Report' in result.output


def test_governor_budget_report_json(runner):
    """Test governor budget report with JSON format."""
    result = runner.invoke(cli, ['governor', 'budget', 'report', '--format', 'json'])
    assert result.exit_code == 0
    assert '"swarm-webrtc"' in result.output


def test_governor_budget_report_csv(runner):
    """Test governor budget report with CSV format."""
    result = runner.invoke(cli, ['governor', 'budget', 'report', '--format', 'csv'])
    assert result.exit_code == 0
    assert 'swarm_id,remaining,spent' in result.output


def test_governor_budget_allocate(runner):
    """Test budget allocation command."""
    result = runner.invoke(cli, [
        'governor', 'budget', 'allocate',
        'swarm-webrtc', '100.0'
    ])
    assert result.exit_code == 0
    assert 'swarm-webrtc' in result.output
    assert '100.00' in result.output


def test_governor_budget_track(runner):
    """Test budget tracking command."""
    result = runner.invoke(cli, [
        'governor', 'budget', 'track',
        'swarm-webrtc', 'task_execution', '25.0'
    ])
    assert result.exit_code == 0
    assert 'Tracking cost' in result.output


# ==================== Chassis Commands ====================


def test_chassis_help(runner):
    """Test chassis help."""
    result = runner.invoke(cli, ['chassis', '--help'])
    assert result.exit_code == 0
    assert 'IF.chassis' in result.output
    assert 'WASM sandbox' in result.output


def test_chassis_status(runner):
    """Test chassis status command."""
    result = runner.invoke(cli, ['chassis', 'status', 'swarm-test'])
    assert result.exit_code == 0
    assert 'Chassis Status' in result.output
    assert 'swarm-test' in result.output


# ==================== Witness Commands ====================


def test_witness_help(runner):
    """Test witness help."""
    result = runner.invoke(cli, ['witness', '--help'])
    assert result.exit_code == 0
    assert 'IF.witness' in result.output
    assert 'Audit logging' in result.output


def test_witness_query(runner):
    """Test witness query command."""
    result = runner.invoke(cli, ['witness', 'query', '--limit', '50'])
    assert result.exit_code == 0
    assert 'Querying audit logs' in result.output


def test_witness_query_with_filters(runner):
    """Test witness query with filters."""
    result = runner.invoke(cli, [
        'witness', 'query',
        '--swarm-id', 'swarm-webrtc',
        '--component', 'IF.coordinator',
        '--operation', 'task_claimed'
    ])
    assert result.exit_code == 0
    assert 'swarm_id=swarm-webrtc' in result.output


def test_witness_query_json(runner):
    """Test witness query with JSON format."""
    result = runner.invoke(cli, ['witness', 'query', '--format', 'json'])
    assert result.exit_code == 0
    assert '"timestamp"' in result.output
    assert '"component"' in result.output


# ==================== Optimise Commands ====================


def test_optimise_help(runner):
    """Test optimise help."""
    result = runner.invoke(cli, ['optimise', '--help'])
    assert result.exit_code == 0
    assert 'IF.optimise' in result.output
    assert 'Cost tracking' in result.output


def test_optimise_report(runner):
    """Test optimise report command."""
    result = runner.invoke(cli, ['optimise', 'report', '--period', '30d'])
    assert result.exit_code == 0
    assert 'Cost Report' in result.output
    assert '30d' in result.output


def test_optimise_report_json(runner):
    """Test optimise report with JSON format."""
    result = runner.invoke(cli, ['optimise', 'report', '--format', 'json'])
    assert result.exit_code == 0
    assert '"total_cost"' in result.output
    assert '"swarms"' in result.output


# ==================== Error Handling ====================


def test_invalid_command(runner):
    """Test invalid command shows error."""
    result = runner.invoke(cli, ['invalid-command'])
    assert result.exit_code != 0


def test_missing_required_option(runner):
    """Test missing required option shows error."""
    result = runner.invoke(cli, [
        'governor', 'register', 'swarm-test',
        '--cost', '15.0'  # Missing --capabilities
    ])
    assert result.exit_code != 0
