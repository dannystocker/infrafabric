#!/usr/bin/env python3
"""
Recovery CLI - Command-line interface for managing recovery operations

Usage:
    python recovery_cli.py recover --component redis --strategy reconnect
    python recovery_cli.py history --component chromadb --last 24h
    python recovery_cli.py test --component openwebui --strategy token_refresh
    python recovery_cli.py approve --action-id abc123
    python recovery_cli.py disable --duration 1h

Citation: if://agent/A35_recovery_cli
Author: Agent A35
Date: 2025-11-30
"""

import os
import sys
import json
import argparse
import logging
from typing import Optional
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from monitoring.recovery.recovery_orchestrator import (
    get_recovery_orchestrator,
    RecoveryStrategy,
    ComponentFailureType,
    RecoveryStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CLI Commands
# ============================================================================

def cmd_recover(args):
    """Trigger manual recovery for a component."""
    orchestrator = get_recovery_orchestrator()

    component = args.component.lower()
    strategy = args.strategy
    require_approval = args.require_approval

    logger.info(
        f"Triggering recovery: component={component}, strategy={strategy}"
    )

    recovery_id = orchestrator.trigger_recovery(
        component=component,
        failure_type="manual_trigger",
        strategy=strategy,
        require_approval=require_approval,
        context=args.context or {}
    )

    if recovery_id:
        print(f"Recovery initiated: ID={recovery_id}")
    else:
        print("Recovery not initiated (cooldown or other reason)")
        sys.exit(1)


def cmd_history(args):
    """Show recovery history."""
    orchestrator = get_recovery_orchestrator()

    component = args.component
    hours = args.last

    history = orchestrator.get_recovery_history(
        component=component,
        hours=hours
    )

    if not history:
        print("No recovery history found")
        return

    print(f"\n{'Component':<15} {'Strategy':<20} {'Status':<15} {'Duration':<12}")
    print("-" * 62)

    for entry in history:
        status = "SUCCESS" if entry['success'] else "FAILED"
        comp = entry['component']
        strat = entry['strategy']
        duration = entry['duration_seconds']

        print(f"{comp:<15} {strat:<20} {status:<15} {duration:.2f}s")

    print(f"\nTotal: {len(history)} recovery actions")

    if args.json:
        print("\nFull JSON:")
        print(json.dumps(history, indent=2, default=str))


def cmd_test(args):
    """Test recovery without executing."""
    orchestrator = get_recovery_orchestrator()

    component = args.component.lower()
    strategy = args.strategy

    print(f"Testing recovery: component={component}, strategy={strategy}")

    # Check if strategy exists for component
    valid_strategies = {
        'redis': ['reconnect', 'flush_corrupted', 'restart_container'],
        'chromadb': ['query_retry', 'snapshot_rollback', 'collection_reload', 'index_rebuild'],
        'openwebui': ['token_refresh', 'model_failover', 'graceful_degradation'],
        'system': ['disk_cleanup', 'memory_gc', 'process_restart', 'file_handle_cleanup']
    }

    if component not in valid_strategies:
        print(f"Unknown component: {component}")
        print(f"Valid components: {list(valid_strategies.keys())}")
        sys.exit(1)

    if strategy not in valid_strategies[component]:
        print(f"Unknown strategy for {component}: {strategy}")
        print(f"Valid strategies: {valid_strategies[component]}")
        sys.exit(1)

    print(f"Recovery test PASSED: {component}/{strategy} is valid")


def cmd_approve(args):
    """Approve pending recovery action."""
    # This would integrate with manual approval workflow
    action_id = args.action_id
    print(f"Approving recovery action: {action_id}")
    print("Note: This would connect to approval workflow system")
    print("TODO: Implement approval workflow integration")


def cmd_disable(args):
    """Disable auto-recovery temporarily."""
    orchestrator = get_recovery_orchestrator()

    duration_str = args.duration
    component = args.component

    # Parse duration
    if duration_str.endswith('h'):
        duration_minutes = int(duration_str[:-1]) * 60
    elif duration_str.endswith('m'):
        duration_minutes = int(duration_str[:-1])
    else:
        print("Duration must be in format: 1h, 30m, etc.")
        sys.exit(1)

    print(f"Disabling auto-recovery for {component or 'all'} ({duration_minutes}m)")

    if component:
        orchestrator.cooldown.set_cooldown(component)
        print(f"Cooldown set for {component}")
    else:
        print("TODO: Implement global disable")


def cmd_status(args):
    """Show recovery system status."""
    orchestrator = get_recovery_orchestrator()

    # Get cooldown status
    cooldown_status = orchestrator.get_cooldown_status()

    # Get recent history
    history = orchestrator.get_recovery_history(hours=1)

    # Get degraded modes
    degraded_modes = orchestrator.degraded_modes

    print("\n" + "=" * 70)
    print("RECOVERY SYSTEM STATUS")
    print("=" * 70)

    print(f"\nAudit Trail Entries: {len(orchestrator.audit_trail)}")
    print(f"Successful Recoveries: {sum(1 for e in orchestrator.audit_trail if e.success)}")
    print(f"Failed Recoveries: {sum(1 for e in orchestrator.audit_trail if not e.success)}")

    if cooldown_status:
        print("\nCooldown Status:")
        for component, status in cooldown_status.items():
            if status['in_cooldown']:
                print(f"  {component}: IN COOLDOWN ({status['seconds_remaining']:.1f}s)")

    if degraded_modes:
        print("\nActive Degraded Modes:")
        for mode in degraded_modes:
            print(f"  - {mode}")

    if history:
        print(f"\nLast Hour Recoveries: {len(history)}")
        for entry in history[-3:]:  # Last 3
            status = "OK" if entry['success'] else "FAIL"
            print(f"  {entry['component']}: {entry['strategy']} [{status}]")

    print("\n" + "=" * 70)


def cmd_metrics(args):
    """Export recovery metrics."""
    orchestrator = get_recovery_orchestrator()

    metrics = {
        'total_recoveries': len(orchestrator.audit_trail),
        'successful_recoveries': sum(1 for e in orchestrator.audit_trail if e.success),
        'failed_recoveries': sum(1 for e in orchestrator.audit_trail if not e.success),
        'success_rate': (
            sum(1 for e in orchestrator.audit_trail if e.success) /
            len(orchestrator.audit_trail) * 100
            if orchestrator.audit_trail else 0
        ),
        'average_recovery_time_seconds': (
            sum(e.duration_seconds for e in orchestrator.audit_trail) /
            len(orchestrator.audit_trail)
            if orchestrator.audit_trail else 0
        ),
        'cooldown_status': orchestrator.get_cooldown_status(),
        'degraded_modes': list(orchestrator.degraded_modes.keys()),
        'timestamp': datetime.utcnow().isoformat() + "Z"
    }

    if args.json:
        print(json.dumps(metrics, indent=2, default=str))
    else:
        print("\nRecovery Metrics:")
        print(f"  Total Recoveries: {metrics['total_recoveries']}")
        print(f"  Successful: {metrics['successful_recoveries']}")
        print(f"  Failed: {metrics['failed_recoveries']}")
        print(f"  Success Rate: {metrics['success_rate']:.1f}%")
        print(f"  Average Time: {metrics['average_recovery_time_seconds']:.2f}s")


# ============================================================================
# Main CLI Parser
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Recovery CLI - Manage InfraFabric recovery operations'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Recover command
    recover_parser = subparsers.add_parser('recover', help='Trigger manual recovery')
    recover_parser.add_argument('--component', required=True, help='Component to recover')
    recover_parser.add_argument('--strategy', required=True, help='Recovery strategy')
    recover_parser.add_argument('--require-approval', action='store_true',
                               help='Require manual approval before execution')
    recover_parser.add_argument('--context', type=json.loads, default={},
                               help='Additional context as JSON')
    recover_parser.set_defaults(func=cmd_recover)

    # History command
    history_parser = subparsers.add_parser('history', help='Show recovery history')
    history_parser.add_argument('--component', help='Filter by component')
    history_parser.add_argument('--last', type=int, default=24,
                               help='Hours to look back (default: 24)')
    history_parser.add_argument('--json', action='store_true', help='Output as JSON')
    history_parser.set_defaults(func=cmd_history)

    # Test command
    test_parser = subparsers.add_parser('test', help='Test recovery strategy')
    test_parser.add_argument('--component', required=True, help='Component')
    test_parser.add_argument('--strategy', required=True, help='Strategy to test')
    test_parser.set_defaults(func=cmd_test)

    # Approve command
    approve_parser = subparsers.add_parser('approve', help='Approve recovery action')
    approve_parser.add_argument('--action-id', required=True, help='Recovery action ID')
    approve_parser.set_defaults(func=cmd_approve)

    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable auto-recovery')
    disable_parser.add_argument('--duration', required=True, help='Duration (e.g., 1h, 30m)')
    disable_parser.add_argument('--component', help='Component (all if not specified)')
    disable_parser.set_defaults(func=cmd_disable)

    # Status command
    status_parser = subparsers.add_parser('status', help='Show recovery system status')
    status_parser.set_defaults(func=cmd_status)

    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Export recovery metrics')
    metrics_parser.add_argument('--json', action='store_true', help='Output as JSON')
    metrics_parser.set_defaults(func=cmd_metrics)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        args.func(args)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
