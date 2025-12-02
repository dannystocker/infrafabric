#!/usr/bin/env python3
"""
InfraFabric Health Check CLI Tool

Provides command-line interface for health check operations:
- check: Run all health checks
- check --component: Check specific component
- watch: Continuous monitoring mode
- status: Export status in various formats
- config: Validate configuration

Usage:
    python health_cli.py check                          # Check all components
    python health_cli.py check --component redis        # Check Redis only
    python health_cli.py watch --interval 5             # Watch mode
    python health_cli.py status --format json           # JSON output
    python health_cli.py config --validate              # Validate config

Citation: if://agent/A34_health_check_cli
Author: Agent A34
Date: 2025-11-30
"""

import os
import sys
import time
import json
import logging
import argparse
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from .dependency_checks import (
        HealthCheckOrchestrator,
        RedisHealthChecker,
        ChromaDBHealthChecker,
        SystemHealthChecker,
        EnvironmentChecker
    )
except (ImportError, ValueError):
    from monitoring.health.dependency_checks import (
        HealthCheckOrchestrator,
        RedisHealthChecker,
        ChromaDBHealthChecker,
        SystemHealthChecker,
        EnvironmentChecker
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Color Output Support
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# ============================================================================
# Status Formatters
# ============================================================================

def format_status(status: str) -> str:
    """Format status with color."""
    if status == 'ok':
        return f"{Colors.GREEN}✓ OK{Colors.RESET}"
    elif status in ('warning', 'degraded'):
        return f"{Colors.YELLOW}⚠ WARNING{Colors.RESET}"
    elif status in ('error', 'unhealthy'):
        return f"{Colors.RED}✗ ERROR{Colors.RESET}"
    else:
        return f"{Colors.CYAN}? UNKNOWN{Colors.RESET}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 0.001:
        return f"{seconds*1000000:.1f}µs"
    elif seconds < 1:
        return f"{seconds*1000:.2f}ms"
    else:
        return f"{seconds:.2f}s"


def format_bytes(bytes_val: float) -> str:
    """Format bytes in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f}PB"


# ============================================================================
# CLI Commands
# ============================================================================

class HealthCheckCLI:
    """Command-line interface for health checks."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize CLI with optional configuration file."""
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__),
            'health_config.yml'
        )
        self.orchestrator = HealthCheckOrchestrator()

    # ========================================================================
    # check command
    # ========================================================================

    def cmd_check(self, args):
        """Run health checks for specified component(s)."""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}InfraFabric Health Check{Colors.RESET}")
        print("=" * 70 + "\n")

        component = getattr(args, 'component', None)
        detailed = getattr(args, 'detailed', False)
        exit_code = 0

        if component:
            # Check specific component
            result = self._check_component(component)
            self._print_check_result(component, result, detailed)
            exit_code = 0 if result.get('status') == 'ok' else 1
        else:
            # Check all components
            full_status = self.orchestrator.check_all()
            checks = full_status.get('checks', {})

            # Print results for each component
            for comp_name, comp_result in checks.items():
                self._print_check_result(comp_name, comp_result, detailed)

            print("\n" + "=" * 70)
            print(f"Overall Status: {'Ready' if full_status.get('ready') else 'Not Ready'}")
            print(f"Uptime: {format_duration(full_status.get('uptime_seconds', 0))}")
            print(f"Timestamp: {full_status.get('timestamp', 'N/A')}")
            print("=" * 70)

            exit_code = 0 if full_status.get('ready') else 1

        return exit_code

    def _check_component(self, component: str) -> Dict[str, Any]:
        """Check a specific component."""
        if component == 'redis':
            checker = RedisHealthChecker()
            return checker.check()
        elif component == 'chromadb':
            checker = ChromaDBHealthChecker()
            return checker.check()
        elif component == 'system':
            checker = SystemHealthChecker()
            disk = checker.check_disk()
            memory = checker.check_memory()
            return {
                'status': 'ok' if disk['status'] == 'ok' and memory['status'] == 'ok' else 'warning',
                'disk': disk,
                'memory': memory
            }
        elif component == 'environment':
            checker = EnvironmentChecker()
            return checker.check()
        else:
            print(f"{Colors.RED}Unknown component: {component}{Colors.RESET}")
            return {'status': 'error', 'error': f'Unknown component: {component}'}

    def _print_check_result(self, name: str, result: Dict[str, Any], detailed: bool = False):
        """Print formatted check result."""
        status = result.get('status', 'unknown')
        print(f"{Colors.BOLD}{name.upper()}{Colors.RESET}")
        print(f"  Status: {format_status(status)}")

        if name == 'redis' and status == 'ok':
            latency = result.get('latency_ms', 0)
            info = result.get('info', {})
            print(f"  Latency: {latency}ms")
            if info and detailed:
                print(f"  Memory: {format_bytes(info.get('used_memory_bytes', 0))}")
                print(f"  Clients: {info.get('connected_clients', 0)}")
                print(f"  Ops/sec: {info.get('ops_per_sec', 0)}")
                print(f"  Version: {info.get('server_version', 'unknown')}")

        elif name == 'chromadb' and status == 'ok':
            col_count = result.get('collection_count', 0)
            collections = result.get('collections', [])
            print(f"  Collections: {col_count}")
            if detailed and collections:
                for col in collections[:5]:  # Show first 5
                    print(f"    - {col}")

        elif name == 'disk' and 'free_percent' in result:
            free_pct = result.get('free_percent', 0)
            free_gb = result.get('free_gb', 0)
            total_gb = result.get('total_gb', 0)
            print(f"  Free: {free_pct:.1f}% ({free_gb:.1f}GB / {total_gb:.1f}GB)")

        elif name == 'memory' and 'percent' in result:
            used_pct = result.get('percent', 0)
            used_mb = result.get('used_mb', 0)
            total_mb = result.get('total_mb', 0)
            print(f"  Used: {used_pct:.1f}% ({used_mb:.0f}MB / {total_mb:.0f}MB)")

        elif name == 'environment' and 'missing_vars' in result:
            missing = result.get('missing_vars', [])
            if missing:
                print(f"  Missing variables: {', '.join(missing)}")
            else:
                print(f"  All required variables set")

        elif status == 'error' and 'error' in result:
            print(f"  Error: {result['error']}")

        print()

    # ========================================================================
    # watch command
    # ========================================================================

    def cmd_watch(self, args):
        """Continuous monitoring mode."""
        interval = getattr(args, 'interval', 5)

        print(f"\n{Colors.BOLD}Watching health checks (interval: {interval}s){Colors.RESET}")
        print(f"Press Ctrl+C to exit\n")

        try:
            while True:
                # Clear screen (cross-platform)
                os.system('clear' if os.name == 'posix' else 'cls')

                print("=" * 70)
                print(f"{Colors.BOLD}InfraFabric Health Check (Watch Mode){Colors.RESET}")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 70 + "\n")

                full_status = self.orchestrator.check_all()
                checks = full_status.get('checks', {})

                # Print summary
                ready_status = f"{Colors.GREEN}READY{Colors.RESET}" if full_status.get('ready') else f"{Colors.RED}NOT READY{Colors.RESET}"
                print(f"Status: {ready_status}\n")

                # Print component status
                for comp_name, comp_result in checks.items():
                    status = comp_result.get('status', 'unknown')
                    status_str = format_status(status)
                    print(f"  {comp_name.ljust(15)} {status_str}")

                print(f"\nUptime: {format_duration(full_status.get('uptime_seconds', 0))}")
                print(f"Next check in {interval}s... (Ctrl+C to exit)")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            return 0

    # ========================================================================
    # status command
    # ========================================================================

    def cmd_status(self, args):
        """Export health status in various formats."""
        format_type = getattr(args, 'format', 'json')

        full_status = self.orchestrator.check_all()

        if format_type == 'json':
            return self._status_json(full_status)
        elif format_type == 'yaml':
            return self._status_yaml(full_status)
        elif format_type == 'prometheus':
            return self._status_prometheus(full_status)
        elif format_type == 'csv':
            return self._status_csv(full_status)
        else:
            print(f"{Colors.RED}Unknown format: {format_type}{Colors.RESET}")
            return 1

    def _status_json(self, status: Dict[str, Any]) -> int:
        """Export status as JSON."""
        print(json.dumps(status, indent=2))
        return 0

    def _status_yaml(self, status: Dict[str, Any]) -> int:
        """Export status as YAML."""
        try:
            import yaml
            print(yaml.dump(status, default_flow_style=False))
        except ImportError:
            # Fallback to simple YAML-like format
            self._print_yaml_recursive(status)
        return 0

    def _print_yaml_recursive(self, obj: Any, indent: int = 0):
        """Print object in YAML-like format."""
        prefix = "  " * indent
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    print(f"{prefix}{key}:")
                    self._print_yaml_recursive(value, indent + 1)
                else:
                    print(f"{prefix}{key}: {value}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    print(f"{prefix}-")
                    self._print_yaml_recursive(item, indent + 1)
                else:
                    print(f"{prefix}- {item}")

    def _status_prometheus(self, status: Dict[str, Any]) -> int:
        """Export status as Prometheus metrics."""
        ready = 1 if status.get('ready') else 0
        checks = status.get('checks', {})

        # Export readiness metric
        print(f"# HELP infra_health_ready Readiness status (1=ready, 0=not_ready)")
        print(f"# TYPE infra_health_ready gauge")
        print(f"infra_health_ready {ready}")
        print()

        # Export component status metrics
        print(f"# HELP infra_health_check_status Component health status")
        print(f"# TYPE infra_health_check_status gauge")
        for component, check_result in checks.items():
            status_val = 1 if check_result.get('status') == 'ok' else 0
            print(f'infra_health_check_status{{component="{component}"}} {status_val}')

        print()
        print(f"# HELP infra_health_uptime_seconds System uptime")
        print(f"# TYPE infra_health_uptime_seconds counter")
        print(f"infra_health_uptime_seconds {status.get('uptime_seconds', 0)}")

        return 0

    def _status_csv(self, status: Dict[str, Any]) -> int:
        """Export status as CSV."""
        checks = status.get('checks', {})

        # Header
        print("component,status,timestamp")

        # Data
        for component, check_result in checks.items():
            status_val = check_result.get('status', 'unknown')
            timestamp = check_result.get('timestamp', '')
            print(f"{component},{status_val},{timestamp}")

        return 0

    # ========================================================================
    # config command
    # ========================================================================

    def cmd_config(self, args):
        """Validate and display configuration."""
        action = getattr(args, 'action', 'show')

        if action == 'validate':
            return self._validate_config()
        elif action == 'show':
            return self._show_config()
        else:
            print(f"{Colors.RED}Unknown action: {action}{Colors.RESET}")
            return 1

    def _validate_config(self) -> int:
        """Validate configuration file."""
        if not os.path.exists(self.config_path):
            print(f"{Colors.RED}Config file not found: {self.config_path}{Colors.RESET}")
            return 1

        try:
            import yaml
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            print(f"{Colors.GREEN}✓ Configuration is valid{Colors.RESET}")
            print(f"\nLoaded configuration from: {self.config_path}")
            print(f"Global check interval: {config.get('global', {}).get('check_interval_seconds', 'N/A')}s")

            # Validate required sections
            required = ['global', 'redis', 'chromadb', 'system', 'environment']
            missing = [s for s in required if s not in config]
            if missing:
                print(f"{Colors.YELLOW}⚠ Missing sections: {', '.join(missing)}{Colors.RESET}")
                return 1

            return 0

        except Exception as e:
            print(f"{Colors.RED}✗ Configuration validation failed: {e}{Colors.RESET}")
            return 1

    def _show_config(self) -> int:
        """Show configuration file."""
        if not os.path.exists(self.config_path):
            print(f"{Colors.RED}Config file not found: {self.config_path}{Colors.RESET}")
            return 1

        print(f"{Colors.BOLD}Configuration: {self.config_path}{Colors.RESET}\n")
        with open(self.config_path, 'r') as f:
            print(f.read())

        return 0


# ============================================================================
# Main CLI Entry Point
# ============================================================================

def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='InfraFabric Health Check CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s check                      # Check all components
  %(prog)s check --component redis    # Check Redis only
  %(prog)s check --detailed           # Detailed output
  %(prog)s watch --interval 5         # Watch mode (5s interval)
  %(prog)s status --format json       # JSON export
  %(prog)s status --format prometheus # Prometheus metrics
  %(prog)s config --validate          # Validate configuration
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # check command
    check_parser = subparsers.add_parser('check', help='Run health checks')
    check_parser.add_argument('--component',
                             choices=['redis', 'chromadb', 'system', 'environment'],
                             help='Check specific component')
    check_parser.add_argument('--detailed', action='store_true',
                             help='Show detailed output')

    # watch command
    watch_parser = subparsers.add_parser('watch', help='Continuous monitoring')
    watch_parser.add_argument('--interval', type=int, default=5,
                             help='Check interval in seconds (default: 5)')

    # status command
    status_parser = subparsers.add_parser('status', help='Export status')
    status_parser.add_argument('--format',
                              choices=['json', 'yaml', 'prometheus', 'csv'],
                              default='json',
                              help='Output format (default: json)')

    # config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('action',
                              choices=['show', 'validate'],
                              nargs='?',
                              default='show',
                              help='Configuration action')

    args = parser.parse_args()

    # Create CLI instance
    cli = HealthCheckCLI()

    # Execute command
    if args.command == 'check':
        exit_code = cli.cmd_check(args)
    elif args.command == 'watch':
        exit_code = cli.cmd_watch(args)
    elif args.command == 'status':
        exit_code = cli.cmd_status(args)
    elif args.command == 'config':
        exit_code = cli.cmd_config(args)
    else:
        # Default to check command
        args.command = 'check'
        exit_code = cli.cmd_check(args)

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
