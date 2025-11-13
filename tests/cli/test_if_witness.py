"""
Unit Tests for IF.witness CLI Integration

Tests witness query, trace, and verify commands.
"""

import pytest
import json
from click.testing import CliRunner
from src.cli.if_main import cli


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


# ==================== Basic Command Tests ====================


def test_witness_help(runner):
    """Test witness command help text."""
    result = runner.invoke(cli, ['witness', '--help'])
    assert result.exit_code == 0
    assert 'IF.witness' in result.output
    assert 'Audit logging' in result.output
    assert 'query' in result.output
    assert 'trace' in result.output
    assert 'verify' in result.output


# ==================== Query Command Tests ====================


def test_witness_query_basic(runner):
    """Test basic witness query command."""
    result = runner.invoke(cli, ['witness', 'query'])
    assert result.exit_code == 0
    assert 'Querying audit logs' in result.output
    assert 'Audit Log' in result.output


def test_witness_query_with_swarm_id(runner):
    """Test witness query with swarm_id filter."""
    result = runner.invoke(cli, ['witness', 'query', '--swarm-id', 'swarm-webrtc'])
    assert result.exit_code == 0
    assert 'swarm_id=swarm-webrtc' in result.output
    assert 'swarm-webrtc' in result.output


def test_witness_query_with_component(runner):
    """Test witness query with component filter."""
    result = runner.invoke(cli, ['witness', 'query', '--component', 'IF.governor'])
    assert result.exit_code == 0
    assert 'component=IF.governor' in result.output


def test_witness_query_with_operation(runner):
    """Test witness query with operation filter."""
    result = runner.invoke(cli, ['witness', 'query', '--operation', 'task_claimed'])
    assert result.exit_code == 0
    assert 'operation=task_claimed' in result.output


def test_witness_query_with_limit(runner):
    """Test witness query with custom limit."""
    result = runner.invoke(cli, ['witness', 'query', '--limit', '50'])
    assert result.exit_code == 0
    assert 'Limit: 50' in result.output


def test_witness_query_multiple_filters(runner):
    """Test witness query with multiple filters."""
    result = runner.invoke(cli, [
        'witness', 'query',
        '--swarm-id', 'swarm-webrtc',
        '--component', 'IF.coordinator',
        '--operation', 'task_claimed',
        '--limit', '10'
    ])
    assert result.exit_code == 0
    assert 'swarm_id=swarm-webrtc' in result.output
    assert 'component=IF.coordinator' in result.output
    assert 'operation=task_claimed' in result.output


def test_witness_query_json_format(runner):
    """Test witness query with JSON output."""
    result = runner.invoke(cli, ['witness', 'query', '--format', 'json'])
    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert 'query' in data
    assert 'logs' in data
    assert 'result_count' in data['query']
    assert isinstance(data['logs'], list)


def test_witness_query_json_structure(runner):
    """Test witness query JSON output structure."""
    result = runner.invoke(cli, [
        'witness', 'query',
        '--swarm-id', 'swarm-test',
        '--format', 'json',
        '--limit', '5'
    ])
    assert result.exit_code == 0

    data = json.loads(result.output)

    # Validate query metadata
    assert data['query']['filters']['swarm_id'] == 'swarm-test'
    assert data['query']['filters']['limit'] == 5

    # Validate log entries
    for log in data['logs']:
        assert 'timestamp' in log
        assert 'component' in log
        assert 'operation' in log
        assert 'hash' in log
        assert 'prev_hash' in log


def test_witness_query_text_format(runner):
    """Test witness query with text output."""
    result = runner.invoke(cli, ['witness', 'query', '--format', 'text'])
    assert result.exit_code == 0
    assert 'Querying audit logs' in result.output
    assert 'Audit Log' in result.output
    assert 'entries' in result.output


# ==================== Trace Command Tests ====================


def test_trace_help(runner):
    """Test trace command help text."""
    result = runner.invoke(cli, ['witness', 'trace', '--help'])
    assert result.exit_code == 0
    assert 'trace' in result.output.lower()
    assert 'provenance chain' in result.output.lower()


def test_trace_basic(runner):
    """Test basic trace command."""
    result = runner.invoke(cli, ['witness', 'trace', 'abc123def456'])
    assert result.exit_code == 0
    assert 'Tracing provenance chain' in result.output
    assert 'abc123def456' in result.output
    assert 'Chain length:' in result.output
    assert 'Step' in result.output


def test_trace_shows_chain_steps(runner):
    """Test trace command shows chain steps."""
    result = runner.invoke(cli, ['witness', 'trace', 'test-token'])
    assert result.exit_code == 0
    assert 'Step 1:' in result.output
    assert 'Step 2:' in result.output
    assert 'Component:' in result.output
    assert 'Operation:' in result.output
    assert 'Hash:' in result.output


def test_trace_json_format(runner):
    """Test trace command with JSON output."""
    result = runner.invoke(cli, ['witness', 'trace', 'abc123', '--format', 'json'])
    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert 'trace' in data
    assert 'chain' in data
    assert data['trace']['token'] == 'abc123'
    assert 'chain_length' in data['trace']
    assert isinstance(data['chain'], list)


def test_trace_json_chain_structure(runner):
    """Test trace JSON output chain structure."""
    result = runner.invoke(cli, ['witness', 'trace', 'token123', '--format', 'json'])
    assert result.exit_code == 0

    data = json.loads(result.output)

    # Validate chain entries
    for entry in data['chain']:
        assert 'step' in entry
        assert 'timestamp' in entry
        assert 'component' in entry
        assert 'operation' in entry
        assert 'hash' in entry
        assert 'prev_hash' in entry
        assert 'details' in entry


def test_trace_text_format(runner):
    """Test trace command with text output."""
    result = runner.invoke(cli, ['witness', 'trace', 'test-hash', '--format', 'text'])
    assert result.exit_code == 0
    assert 'Tracing provenance chain' in result.output
    assert 'test-hash' in result.output
    assert 'Step' in result.output


# ==================== Verify Command Tests ====================


def test_verify_help(runner):
    """Test verify command help text."""
    result = runner.invoke(cli, ['witness', 'verify', '--help'])
    assert result.exit_code == 0
    assert 'verify' in result.output.lower()
    assert 'hash chain integrity' in result.output.lower()


def test_verify_basic(runner):
    """Test basic verify command."""
    result = runner.invoke(cli, ['witness', 'verify'])
    assert result.exit_code == 0
    assert 'Hash Chain Verification' in result.output
    assert 'Status:' in result.output
    assert 'VALID' in result.output or 'INVALID' in result.output
    assert 'Total entries:' in result.output
    assert 'Verified:' in result.output


def test_verify_shows_status(runner):
    """Test verify command shows verification status."""
    result = runner.invoke(cli, ['witness', 'verify'])
    assert result.exit_code == 0
    assert 'Hash Chain Verification' in result.output
    # Mock always returns valid
    assert 'VALID' in result.output
    assert 'Total entries:' in result.output
    assert 'Broken links: 0' in result.output


def test_verify_with_range(runner):
    """Test verify command with hash range."""
    result = runner.invoke(cli, [
        'witness', 'verify',
        '--start-hash', 'abc123',
        '--end-hash', 'def456'
    ])
    assert result.exit_code == 0
    assert 'Hash Chain Verification' in result.output
    assert 'Range:' in result.output
    assert 'abc123' in result.output
    assert 'def456' in result.output


def test_verify_json_format(runner):
    """Test verify command with JSON output."""
    result = runner.invoke(cli, ['witness', 'verify', '--format', 'json'])
    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert 'valid' in data
    assert 'start_hash' in data
    assert 'end_hash' in data
    assert 'total_entries' in data
    assert 'verified_entries' in data
    assert 'broken_links' in data
    assert 'verification_time_ms' in data


def test_verify_json_structure(runner):
    """Test verify JSON output structure."""
    result = runner.invoke(cli, [
        'witness', 'verify',
        '--start-hash', 'start123',
        '--end-hash', 'end456',
        '--format', 'json'
    ])
    assert result.exit_code == 0

    data = json.loads(result.output)

    # Mock always returns valid=True
    assert data['valid'] is True
    assert isinstance(data['total_entries'], int)
    assert isinstance(data['verified_entries'], int)
    assert isinstance(data['broken_links'], int)
    assert data['broken_links'] == 0  # Mock has no broken links


def test_verify_text_format(runner):
    """Test verify command with text output."""
    result = runner.invoke(cli, ['witness', 'verify', '--format', 'text'])
    assert result.exit_code == 0
    assert 'Hash Chain Verification' in result.output
    assert 'Status:' in result.output


# ==================== Integration Tests ====================


def test_witness_commands_accessible(runner):
    """Test that all witness commands are accessible."""
    # Test query
    result = runner.invoke(cli, ['witness', 'query', '--help'])
    assert result.exit_code == 0

    # Test trace
    result = runner.invoke(cli, ['witness', 'trace', '--help'])
    assert result.exit_code == 0

    # Test verify
    result = runner.invoke(cli, ['witness', 'verify', '--help'])
    assert result.exit_code == 0


def test_witness_debug_mode(runner):
    """Test witness commands with debug flag."""
    result = runner.invoke(cli, ['--debug', 'witness', 'query', '--limit', '1'])
    assert result.exit_code == 0
    # Debug output goes to stderr, so won't be in standard output
    # Just verify command runs successfully


def test_witness_query_and_trace_integration(runner):
    """Test query then trace workflow."""
    # First query to get a hash
    query_result = runner.invoke(cli, ['witness', 'query', '--format', 'json', '--limit', '1'])
    assert query_result.exit_code == 0

    query_data = json.loads(query_result.output)
    if query_data['logs']:
        first_hash = query_data['logs'][0]['hash']

        # Then trace that hash
        trace_result = runner.invoke(cli, ['witness', 'trace', first_hash, '--format', 'json'])
        assert trace_result.exit_code == 0

        trace_data = json.loads(trace_result.output)
        assert 'chain' in trace_data


def test_all_witness_output_formats(runner):
    """Test that all witness commands support both output formats."""
    # Query
    for fmt in ['text', 'json']:
        result = runner.invoke(cli, ['witness', 'query', '--format', fmt])
        assert result.exit_code == 0

    # Trace
    for fmt in ['text', 'json']:
        result = runner.invoke(cli, ['witness', 'trace', 'test-token', '--format', fmt])
        assert result.exit_code == 0

    # Verify
    for fmt in ['text', 'json']:
        result = runner.invoke(cli, ['witness', 'verify', '--format', fmt])
        assert result.exit_code == 0
