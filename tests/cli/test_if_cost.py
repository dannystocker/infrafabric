"""
Unit Tests for IF.cost CLI Integration

Tests cost report, budget, and history commands.
"""

import pytest
import json
import csv
import tempfile
from pathlib import Path
from click.testing import CliRunner
from src.cli.if_main import cli


@pytest.fixture
def runner():
    """Provide Click test runner."""
    return CliRunner()


# ==================== Basic Command Tests ====================


def test_cost_help(runner):
    """Test cost command help text."""
    result = runner.invoke(cli, ['cost', '--help'])
    assert result.exit_code == 0
    assert 'IF.cost' in result.output
    assert 'Cost tracking' in result.output
    assert 'report' in result.output
    assert 'budget' in result.output
    assert 'history' in result.output


# ==================== Cost Report Tests ====================


def test_cost_report_basic(runner):
    """Test basic cost report command."""
    result = runner.invoke(cli, ['cost', 'report'])
    assert result.exit_code == 0
    assert 'Cost Report' in result.output
    assert 'Total Cost:' in result.output
    assert 'Per-Swarm Breakdown:' in result.output


def test_cost_report_with_period(runner):
    """Test cost report with custom period."""
    result = runner.invoke(cli, ['cost', 'report', '--period', '30d'])
    assert result.exit_code == 0
    assert 'Period: 30d' in result.output
    assert 'Total Cost:' in result.output


def test_cost_report_with_swarm_filter(runner):
    """Test cost report filtered by swarm."""
    result = runner.invoke(cli, ['cost', 'report', '--swarm-id', 'swarm-webrtc'])
    assert result.exit_code == 0
    assert 'Cost Report' in result.output
    # Should only show filtered swarm
    assert 'swarm-webrtc' in result.output


def test_cost_report_json_format(runner):
    """Test cost report with JSON output."""
    result = runner.invoke(cli, ['cost', 'report', '--format', 'json'])
    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert 'period' in data
    assert 'total_cost' in data
    assert 'breakdown' in data
    assert isinstance(data['breakdown'], dict)


def test_cost_report_json_structure(runner):
    """Test cost report JSON output structure."""
    result = runner.invoke(cli, ['cost', 'report', '--period', '7d', '--format', 'json'])
    assert result.exit_code == 0

    data = json.loads(result.output)

    # Validate report structure
    assert data['period'] == '7d'
    assert isinstance(data['total_cost'], (int, float))

    # Validate breakdown entries
    for swarm, details in data['breakdown'].items():
        assert 'total_cost' in details
        assert 'operations' in details
        assert 'avg_cost_per_op' in details
        assert 'model' in details
        assert 'hours_active' in details


def test_cost_report_csv_format(runner):
    """Test cost report with CSV output."""
    result = runner.invoke(cli, ['cost', 'report', '--format', 'csv'])
    assert result.exit_code == 0

    # Verify CSV header
    lines = result.output.strip().split('\n')
    assert 'swarm_id' in lines[0]
    assert 'total_cost' in lines[0]
    assert 'operations' in lines[0]

    # Verify CSV has data rows
    assert len(lines) > 1


def test_cost_report_csv_parsing(runner):
    """Test cost report CSV output can be parsed."""
    result = runner.invoke(cli, ['cost', 'report', '--format', 'csv'])
    assert result.exit_code == 0

    # Parse CSV
    import io
    reader = csv.DictReader(io.StringIO(result.output))
    rows = list(reader)

    # Validate we have data
    assert len(rows) > 0
    assert 'swarm_id' in rows[0]
    assert 'total_cost' in rows[0]


def test_cost_report_text_format(runner):
    """Test cost report with text output (default)."""
    result = runner.invoke(cli, ['cost', 'report', '--format', 'text'])
    assert result.exit_code == 0
    assert 'Cost Report' in result.output
    assert 'Total Cost:' in result.output
    assert 'Per-Swarm Breakdown:' in result.output


# ==================== Cost Budget Tests ====================


def test_cost_budget_basic(runner):
    """Test basic budget command."""
    result = runner.invoke(cli, ['cost', 'budget'])
    assert result.exit_code == 0
    assert 'Budget Status' in result.output
    assert 'Allocated:' in result.output
    assert 'Spent:' in result.output
    assert 'Remaining:' in result.output


def test_cost_budget_with_swarm_filter(runner):
    """Test budget filtered by swarm."""
    result = runner.invoke(cli, ['cost', 'budget', '--swarm-id', 'swarm-webrtc'])
    assert result.exit_code == 0
    assert 'Budget Status' in result.output
    assert 'swarm-webrtc' in result.output


def test_cost_budget_shows_status_indicators(runner):
    """Test budget shows health status indicators."""
    result = runner.invoke(cli, ['cost', 'budget'])
    assert result.exit_code == 0
    # Should show status indicators (healthy/warning/critical)
    assert any(word in result.output for word in ['healthy', 'warning', 'critical'])


def test_cost_budget_json_format(runner):
    """Test budget with JSON output."""
    result = runner.invoke(cli, ['cost', 'budget', '--format', 'json'])
    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert isinstance(data, dict)

    # Validate budget entries
    for swarm, budget in data.items():
        assert 'allocated' in budget
        assert 'spent' in budget
        assert 'remaining' in budget
        assert 'utilization' in budget
        assert 'burn_rate_per_hour' in budget
        assert 'estimated_hours_remaining' in budget


def test_cost_budget_csv_format(runner):
    """Test budget with CSV output."""
    result = runner.invoke(cli, ['cost', 'budget', '--format', 'csv'])
    assert result.exit_code == 0

    # Verify CSV structure
    lines = result.output.strip().split('\n')
    assert 'swarm_id' in lines[0]
    assert 'allocated' in lines[0]
    assert 'remaining' in lines[0]
    assert 'utilization' in lines[0]


def test_cost_budget_text_format(runner):
    """Test budget with text output."""
    result = runner.invoke(cli, ['cost', 'budget', '--format', 'text'])
    assert result.exit_code == 0
    assert 'Budget Status' in result.output
    assert 'Utilization:' in result.output
    assert 'Burn Rate:' in result.output


# ==================== Cost History Tests ====================


def test_cost_history_basic(runner):
    """Test basic history command."""
    result = runner.invoke(cli, ['cost', 'history'])
    assert result.exit_code == 0
    assert 'Cost History' in result.output
    assert 'entries' in result.output


def test_cost_history_with_period(runner):
    """Test history with custom period."""
    result = runner.invoke(cli, ['cost', 'history', '--period', '7d'])
    assert result.exit_code == 0
    assert 'Period: 7d' in result.output
    assert '7 entries' in result.output


def test_cost_history_with_swarm_filter(runner):
    """Test history filtered by swarm."""
    result = runner.invoke(cli, ['cost', 'history', '--swarm-id', 'swarm-webrtc'])
    assert result.exit_code == 0
    assert 'Cost History' in result.output


def test_cost_history_export_csv(runner):
    """Test history export to CSV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        export_path = Path(tmpdir) / 'costs.csv'

        result = runner.invoke(cli, [
            'cost', 'history',
            '--period', '7d',
            '--export', str(export_path)
        ])

        assert result.exit_code == 0
        assert 'exported to:' in result.output
        assert export_path.exists()

        # Verify CSV content
        with open(export_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 7  # 7 days
            assert 'date' in rows[0]
            assert 'total_cost' in rows[0]


def test_cost_history_json_format(runner):
    """Test history with JSON output."""
    result = runner.invoke(cli, ['cost', 'history', '--period', '7d', '--format', 'json'])
    assert result.exit_code == 0

    # Parse JSON output
    data = json.loads(result.output)
    assert 'period' in data
    assert 'entries' in data
    assert isinstance(data['entries'], list)
    assert len(data['entries']) == 7


def test_cost_history_json_structure(runner):
    """Test history JSON output structure."""
    result = runner.invoke(cli, ['cost', 'history', '--period', '5d', '--format', 'json'])
    assert result.exit_code == 0

    data = json.loads(result.output)

    # Validate entries
    for entry in data['entries']:
        assert 'date' in entry
        assert 'total_cost' in entry
        assert 'operations' in entry
        assert 'swarms_active' in entry
        assert 'breakdown' in entry
        assert isinstance(entry['breakdown'], dict)


def test_cost_history_csv_format(runner):
    """Test history with CSV output."""
    result = runner.invoke(cli, ['cost', 'history', '--period', '5d', '--format', 'csv'])
    assert result.exit_code == 0

    # Verify CSV structure
    lines = result.output.strip().split('\n')
    assert 'date' in lines[0]
    assert 'total_cost' in lines[0]
    assert 'operations' in lines[0]

    # Verify number of rows (header + 5 days)
    assert len(lines) == 6


def test_cost_history_text_format(runner):
    """Test history with text output."""
    result = runner.invoke(cli, ['cost', 'history', '--period', '7d', '--format', 'text'])
    assert result.exit_code == 0
    assert 'Cost History' in result.output
    assert 'Summary:' in result.output
    assert 'Total Cost:' in result.output
    assert 'Avg Daily Cost:' in result.output


# ==================== Integration Tests ====================


def test_cost_commands_accessible(runner):
    """Test that all cost commands are accessible."""
    # Test report
    result = runner.invoke(cli, ['cost', 'report', '--help'])
    assert result.exit_code == 0

    # Test budget
    result = runner.invoke(cli, ['cost', 'budget', '--help'])
    assert result.exit_code == 0

    # Test history
    result = runner.invoke(cli, ['cost', 'history', '--help'])
    assert result.exit_code == 0


def test_cost_debug_mode(runner):
    """Test cost commands with debug flag."""
    result = runner.invoke(cli, ['--debug', 'cost', 'report'])
    assert result.exit_code == 0
    # Command should still succeed with debug mode


def test_all_cost_output_formats(runner):
    """Test that all cost commands support output formats."""
    commands = [
        ['cost', 'report'],
        ['cost', 'budget'],
        ['cost', 'history']
    ]

    for cmd in commands:
        # Test text format
        result = runner.invoke(cli, cmd + ['--format', 'text'])
        assert result.exit_code == 0

        # Test JSON format
        result = runner.invoke(cli, cmd + ['--format', 'json'])
        assert result.exit_code == 0
        json.loads(result.output)  # Verify valid JSON

        # Test CSV format
        result = runner.invoke(cli, cmd + ['--format', 'csv'])
        assert result.exit_code == 0


def test_cost_report_and_budget_consistency(runner):
    """Test that report and budget show consistent data."""
    # Get report
    report_result = runner.invoke(cli, ['cost', 'report', '--swarm-id', 'swarm-webrtc', '--format', 'json'])
    assert report_result.exit_code == 0
    report_data = json.loads(report_result.output)

    # Get budget
    budget_result = runner.invoke(cli, ['cost', 'budget', '--swarm-id', 'swarm-webrtc', '--format', 'json'])
    assert budget_result.exit_code == 0
    budget_data = json.loads(budget_result.output)

    # Both should have swarm-webrtc data
    assert 'swarm-webrtc' in report_data['breakdown']
    assert 'swarm-webrtc' in budget_data


def test_cost_history_export_and_csv_format_consistency(runner):
    """Test that export and CSV format produce similar data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        export_path = Path(tmpdir) / 'costs.csv'

        # Export to file
        export_result = runner.invoke(cli, [
            'cost', 'history',
            '--period', '5d',
            '--export', str(export_path)
        ])
        assert export_result.exit_code == 0

        # Get CSV format output
        csv_result = runner.invoke(cli, ['cost', 'history', '--period', '5d', '--format', 'csv'])
        assert csv_result.exit_code == 0

        # Read exported file
        with open(export_path, 'r') as f:
            export_content = f.read()

        # Both should have same number of lines
        export_lines = len(export_content.strip().split('\n'))
        csv_lines = len(csv_result.output.strip().split('\n'))
        assert export_lines == csv_lines
