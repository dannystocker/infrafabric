#!/usr/bin/env python3
"""
Test Suite for Health Check CLI Tool

Tests cover:
- CLI command parsing
- Output formatting
- Component-specific checks
- Watch mode
- Status export (JSON, YAML, Prometheus, CSV)
- Configuration management

Citation: if://agent/A34_health_check_cli_tests
Author: Agent A34
Date: 2025-11-30
"""

import os
import sys
import json
import tempfile
from io import StringIO
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from monitoring.health.health_cli import (
    HealthCheckCLI,
    Colors,
    format_status,
    format_duration,
    format_bytes
)


# ============================================================================
# Formatter Tests
# ============================================================================

class TestFormatters:
    """Test output formatters."""

    def test_format_status_ok(self):
        """Test OK status formatting."""
        result = format_status('ok')
        assert 'OK' in result

    def test_format_status_warning(self):
        """Test warning status formatting."""
        result = format_status('warning')
        assert 'WARNING' in result

    def test_format_status_error(self):
        """Test error status formatting."""
        result = format_status('error')
        assert 'ERROR' in result

    def test_format_duration_microseconds(self):
        """Test duration formatting for microseconds."""
        result = format_duration(0.0001)
        assert 'µs' in result or 'us' in result

    def test_format_duration_milliseconds(self):
        """Test duration formatting for milliseconds."""
        result = format_duration(0.05)
        assert 'ms' in result

    def test_format_duration_seconds(self):
        """Test duration formatting for seconds."""
        result = format_duration(1.5)
        assert 's' in result

    def test_format_bytes_bytes(self):
        """Test byte formatting."""
        result = format_bytes(512)
        assert 'B' in result

    def test_format_bytes_kilobytes(self):
        """Test kilobyte formatting."""
        result = format_bytes(2048)
        assert 'KB' in result

    def test_format_bytes_megabytes(self):
        """Test megabyte formatting."""
        result = format_bytes(5242880)
        assert 'MB' in result


# ============================================================================
# CLI Command Tests
# ============================================================================

class TestHealthCheckCLI:
    """Test suite for HealthCheckCLI."""

    @pytest.fixture
    def cli(self):
        """Create CLI instance."""
        return HealthCheckCLI()

    def test_cli_init(self, cli):
        """Test CLI initialization."""
        assert cli.config_path is not None
        assert cli.orchestrator is not None

    @patch('monitoring.health.health_cli.HealthCheckCLI._check_component')
    def test_cmd_check_all(self, mock_check, cli):
        """Test check command for all components."""
        mock_check.return_value = {'status': 'ok'}

        args = MagicMock()
        args.component = None
        args.detailed = False

        with patch('monitoring.health.health_cli.HealthCheckCLI._print_check_result'):
            exit_code = cli.cmd_check(args)

        assert exit_code == 0

    @patch('monitoring.health.health_cli.HealthCheckCLI._check_component')
    def test_cmd_check_specific_component(self, mock_check, cli):
        """Test check command for specific component."""
        mock_check.return_value = {'status': 'ok', 'latency_ms': 0.5}

        args = MagicMock()
        args.component = 'redis'
        args.detailed = False

        with patch('monitoring.health.health_cli.HealthCheckCLI._print_check_result'):
            exit_code = cli.cmd_check(args)

        assert exit_code == 0

    def test_check_component_redis(self, cli):
        """Test checking Redis component."""
        with patch('monitoring.health.health_cli.RedisHealthChecker') as mock_redis:
            mock_instance = MagicMock()
            mock_instance.check.return_value = {'status': 'ok', 'latency_ms': 0.5}
            mock_redis.return_value = mock_instance

            result = cli._check_component('redis')

            assert result.get('status') == 'ok'

    def test_check_component_chromadb(self, cli):
        """Test checking ChromaDB component."""
        with patch('monitoring.health.health_cli.ChromaDBHealthChecker') as mock_chroma:
            mock_instance = MagicMock()
            mock_instance.check.return_value = {
                'status': 'ok',
                'collection_count': 4,
                'collections': ['col1', 'col2', 'col3', 'col4']
            }
            mock_chroma.return_value = mock_instance

            result = cli._check_component('chromadb')

            assert result.get('status') == 'ok'

    def test_check_component_system(self, cli):
        """Test checking system component."""
        with patch('monitoring.health.health_cli.SystemHealthChecker') as mock_sys:
            mock_instance = MagicMock()
            mock_instance.check_disk.return_value = {'status': 'ok', 'free_percent': 50}
            mock_instance.check_memory.return_value = {'status': 'ok', 'percent': 40}
            mock_sys.return_value = mock_instance

            result = cli._check_component('system')

            assert result.get('status') == 'ok'

    def test_check_component_environment(self, cli):
        """Test checking environment component."""
        with patch('monitoring.health.health_cli.EnvironmentChecker') as mock_env:
            mock_instance = MagicMock()
            mock_instance.check.return_value = {
                'status': 'ok',
                'missing_vars': []
            }
            mock_env.return_value = mock_instance

            result = cli._check_component('environment')

            assert result.get('status') == 'ok'

    def test_check_component_invalid(self, cli):
        """Test checking invalid component."""
        result = cli._check_component('invalid')

        assert result.get('status') == 'error'

    def test_cmd_watch(self, cli):
        """Test watch command."""
        args = MagicMock()
        args.interval = 1

        with patch('time.sleep'):
            with patch('os.system'):
                with patch('builtins.print'):
                    with patch.object(cli.orchestrator, 'check_all') as mock_check:
                        mock_check.return_value = {
                            'ready': True,
                            'checks': {
                                'redis': {'status': 'ok'},
                                'chromadb': {'status': 'ok'},
                                'disk': {'status': 'ok'},
                                'memory': {'status': 'ok'},
                                'environment': {'status': 'ok'}
                            },
                            'uptime_seconds': 100
                        }

                        # Simulate KeyboardInterrupt after first iteration
                        with patch('time.sleep', side_effect=KeyboardInterrupt):
                            exit_code = cli.cmd_watch(args)

        assert exit_code == 0

    def test_cmd_status_json(self, cli):
        """Test status command with JSON format."""
        args = MagicMock()
        args.format = 'json'

        with patch('builtins.print') as mock_print:
            with patch.object(cli.orchestrator, 'check_all') as mock_check:
                mock_check.return_value = {
                    'ready': True,
                    'checks': {},
                    'uptime_seconds': 100
                }

                exit_code = cli.cmd_status(args)

        assert exit_code == 0
        # Verify JSON was printed
        mock_print.assert_called()

    def test_cmd_status_prometheus(self, cli):
        """Test status command with Prometheus format."""
        args = MagicMock()
        args.format = 'prometheus'

        with patch('builtins.print') as mock_print:
            with patch.object(cli.orchestrator, 'check_all') as mock_check:
                mock_check.return_value = {
                    'ready': True,
                    'checks': {'redis': {'status': 'ok'}},
                    'uptime_seconds': 100
                }

                exit_code = cli.cmd_status(args)

        assert exit_code == 0

    def test_cmd_status_csv(self, cli):
        """Test status command with CSV format."""
        args = MagicMock()
        args.format = 'csv'

        with patch('builtins.print'):
            with patch.object(cli.orchestrator, 'check_all') as mock_check:
                mock_check.return_value = {
                    'ready': True,
                    'checks': {'redis': {'status': 'ok', 'timestamp': '2025-11-30T12:00:00Z'}},
                    'uptime_seconds': 100
                }

                exit_code = cli.cmd_status(args)

        assert exit_code == 0

    def test_cmd_status_invalid_format(self, cli):
        """Test status command with invalid format."""
        args = MagicMock()
        args.format = 'invalid'

        with patch('builtins.print'):
            exit_code = cli.cmd_status(args)

        assert exit_code == 1

    def test_cmd_config_validate(self, cli):
        """Test config validation."""
        args = MagicMock()
        args.action = 'validate'

        with patch('os.path.exists', return_value=False):
            with patch('builtins.print'):
                exit_code = cli.cmd_config(args)

        assert exit_code == 1

    def test_cmd_config_show(self, cli):
        """Test config show."""
        args = MagicMock()
        args.action = 'show'

        # Create temp config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yml') as f:
            f.write('test: config\n')
            config_path = f.name

        try:
            cli.config_path = config_path

            with patch('builtins.print'):
                exit_code = cli.cmd_config(args)

            assert exit_code == 0

        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)


# ============================================================================
# Integration Tests
# ============================================================================

class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_full_check_workflow(self):
        """Test complete health check workflow via CLI."""
        cli = HealthCheckCLI()

        with patch.object(cli.orchestrator, 'check_all') as mock_check:
            mock_check.return_value = {
                'ready': True,
                'checks': {
                    'redis': {'status': 'ok', 'latency_ms': 0.5},
                    'chromadb': {'status': 'ok', 'collection_count': 4},
                    'disk': {'status': 'ok', 'free_percent': 50},
                    'memory': {'status': 'ok', 'percent': 40},
                    'environment': {'status': 'ok', 'missing_vars': []}
                },
                'uptime_seconds': 100,
                'timestamp': '2025-11-30T12:00:00Z'
            }

            args = MagicMock()
            args.component = None
            args.detailed = True

            with patch('builtins.print'):
                exit_code = cli.cmd_check(args)

        assert exit_code == 0

    def test_cli_component_specific_check(self):
        """Test component-specific check via CLI."""
        cli = HealthCheckCLI()

        with patch('monitoring.health.health_cli.RedisHealthChecker') as mock_redis:
            mock_instance = MagicMock()
            mock_instance.check.return_value = {
                'status': 'ok',
                'latency_ms': 0.5,
                'info': {
                    'used_memory_bytes': 1000000,
                    'connected_clients': 5,
                    'ops_per_sec': 100
                }
            }
            mock_redis.return_value = mock_instance

            args = MagicMock()
            args.component = 'redis'
            args.detailed = True

            with patch('builtins.print'):
                exit_code = cli.cmd_check(args)

        assert exit_code == 0

    def test_status_export_multiple_formats(self):
        """Test exporting status in multiple formats."""
        cli = HealthCheckCLI()

        mock_status = {
            'ready': True,
            'checks': {
                'redis': {'status': 'ok', 'latency_ms': 0.5},
                'chromadb': {'status': 'ok', 'collection_count': 4}
            },
            'uptime_seconds': 100,
            'timestamp': '2025-11-30T12:00:00Z'
        }

        # Test JSON
        with patch.object(cli.orchestrator, 'check_all', return_value=mock_status):
            args = MagicMock()
            args.format = 'json'
            with patch('builtins.print'):
                exit_code = cli.cmd_status(args)
            assert exit_code == 0

        # Test CSV
        with patch.object(cli.orchestrator, 'check_all', return_value=mock_status):
            args = MagicMock()
            args.format = 'csv'
            with patch('builtins.print'):
                exit_code = cli.cmd_status(args)
            assert exit_code == 0

        # Test Prometheus
        with patch.object(cli.orchestrator, 'check_all', return_value=mock_status):
            args = MagicMock()
            args.format = 'prometheus'
            with patch('builtins.print'):
                exit_code = cli.cmd_status(args)
            assert exit_code == 0
