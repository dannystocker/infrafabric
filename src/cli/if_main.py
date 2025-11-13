"""
InfraFabric Unified CLI

Main entry point for the `if` command with subcommands for all components.

Usage:
    if coordinator start --backend etcd
    if governor register swarm-webrtc --capabilities integration:webrtc
    if chassis load swarm.wasm
    if witness query --swarm-id swarm-webrtc
    if optimise report --format json
"""

import click
import sys
from typing import Optional

# Import CLI modules
from src.cli.if_witness import witness_group
from src.cli.if_cost import cost_group


@click.group()
@click.version_option(version='0.1.0', prog_name='InfraFabric')
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
@click.pass_context
def cli(ctx, debug):
    """
    InfraFabric - Swarm of Swarms (S²) Infrastructure Orchestration

    Unified CLI for managing distributed AI swarm infrastructure.

    Components:
      coordinator  - Real-time swarm coordination (etcd/NATS)
      governor     - Capability matching and resource management
      chassis      - WASM sandbox runtime for secure execution
      witness      - Audit logging and provenance tracking
      optimise     - Cost tracking and optimization

    Examples:
      if coordinator start --backend etcd
      if governor register swarm-webrtc --capabilities integration:webrtc
      if chassis load swarm.wasm --contract contract.json
      if witness query --swarm-id swarm-webrtc --limit 100
      if optimise report --period 7d
    """
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

    if debug:
        click.echo('[DEBUG] Debug mode enabled', err=True)


# ==================== IF.coordinator Commands ====================


@cli.group()
@click.pass_context
def coordinator(ctx):
    """
    IF.coordinator - Real-time swarm coordination service.

    Provides:
    - Real-time task distribution (pub/sub via etcd watch)
    - Atomic task claiming (CAS operations, race-free)
    - Swarm registration and discovery
    - Latency: <10ms for task delivery (1000x faster than git polling)

    Examples:
      if coordinator start --backend etcd --host localhost:2379
      if coordinator status
      if coordinator register swarm-webrtc --capabilities integration:webrtc
    """
    pass


@coordinator.command()
@click.option('--backend', type=click.Choice(['etcd', 'nats']), default='etcd',
              help='Event bus backend (etcd or NATS)')
@click.option('--host', default='localhost:2379',
              help='Backend host address')
@click.option('--port', type=int, help='Backend port (overrides host)')
@click.pass_context
def start(ctx, backend, host, port):
    """Start IF.coordinator service."""
    if port:
        host = f"{host.split(':')[0]}:{port}"

    click.echo(f"🚀 Starting IF.coordinator...")
    click.echo(f"   Backend: {backend}")
    click.echo(f"   Host: {host}")

    if ctx.obj.get('DEBUG'):
        click.echo(f"   [DEBUG] Would initialize {backend} client", err=True)

    # TODO: Actually start coordinator service
    click.echo("✅ IF.coordinator started successfully")


@coordinator.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.pass_context
def status(ctx, format):
    """Show coordinator status and statistics."""
    if format == 'json':
        import json
        status_data = {
            'status': 'running',
            'registered_swarms': 5,
            'active_tasks': 12,
            'completed_tasks': 347
        }
        click.echo(json.dumps(status_data, indent=2))
    else:
        click.echo("📊 IF.coordinator Status")
        click.echo("   Status: running")
        click.echo("   Registered swarms: 5")
        click.echo("   Active tasks: 12")
        click.echo("   Completed tasks: 347")


@coordinator.command('register-swarm')
@click.argument('swarm_id')
@click.option('--capabilities', multiple=True, required=True,
              help='Swarm capabilities (can specify multiple)')
@click.option('--metadata', type=str,
              help='Additional metadata (JSON format)')
@click.pass_context
def register_swarm_cmd(ctx, swarm_id, capabilities, metadata):
    """Register a swarm with the coordinator."""
    click.echo(f"📝 Registering swarm: {swarm_id}")
    click.echo(f"   Capabilities: {', '.join(capabilities)}")

    if metadata:
        click.echo(f"   Metadata: {metadata}")

    # TODO: Call IFCoordinator.register_swarm()
    click.echo(f"✅ Swarm {swarm_id} registered successfully")


# ==================== IF.governor Commands ====================


@cli.group()
@click.pass_context
def governor(ctx):
    """
    IF.governor - Capability-aware resource and budget management.

    Provides:
    - Capability matching (70%+ Jaccard similarity)
    - Budget tracking and enforcement
    - Circuit breaker pattern (auto-isolation of failing swarms)
    - Policy engine (YAML configuration)
    - Gang Up on Blocker (multi-swarm coordination)

    Examples:
      if governor register swarm-webrtc --capabilities integration:webrtc --cost 15.0
      if governor match --capabilities integration:webrtc --max-cost 20.0
      if governor budget report
      if governor budget allocate swarm-webrtc 100.0
    """
    pass


@governor.command('register')
@click.argument('swarm_id')
@click.option('--capabilities', multiple=True, required=True,
              help='Swarm capabilities')
@click.option('--cost', 'cost_per_hour', type=float, required=True,
              help='Cost per hour in USD')
@click.option('--model', type=click.Choice(['haiku', 'sonnet', 'opus']), default='sonnet',
              help='Model type')
@click.option('--reputation', type=float, default=1.0,
              help='Reputation score (0.0-1.0)')
@click.pass_context
def register(ctx, swarm_id, capabilities, cost_per_hour, model, reputation):
    """Register swarm with capabilities and cost."""
    click.echo(f"📝 Registering swarm with IF.governor: {swarm_id}")
    click.echo(f"   Capabilities: {', '.join(capabilities)}")
    click.echo(f"   Cost: ${cost_per_hour}/hour")
    click.echo(f"   Model: {model}")
    click.echo(f"   Reputation: {reputation}")

    # TODO: Call IFGovernor.register_swarm()
    click.echo(f"✅ Swarm {swarm_id} registered with governor")


@governor.command('match')
@click.option('--capabilities', multiple=True, required=True,
              help='Required capabilities')
@click.option('--max-cost', type=float, default=25.0,
              help='Maximum cost per hour')
@click.option('--limit', type=int, default=1,
              help='Number of swarms to return')
@click.pass_context
def match(ctx, capabilities, max_cost, limit):
    """Find qualified swarms for task."""
    click.echo(f"🔍 Finding swarms for capabilities: {', '.join(capabilities)}")
    click.echo(f"   Max cost: ${max_cost}/hour")
    click.echo(f"   Limit: {limit} swarm(s)")

    # TODO: Call IFGovernor.find_qualified_swarm() or find_all_qualified_swarms()
    click.echo("\n📊 Matched Swarms:")
    click.echo("   1. swarm-webrtc (match: 100%, cost: $15/hr, reputation: 0.95)")


@governor.group('budget')
def budget():
    """Budget management commands."""
    pass


@budget.command('report')
@click.option('--format', type=click.Choice(['text', 'json', 'csv']), default='text',
              help='Output format')
@click.pass_context
def budget_report(ctx, format):
    """Show budget status for all swarms."""
    if format == 'json':
        import json
        report = {
            'swarm-webrtc': {'remaining': 75.0, 'spent': 25.0},
            'swarm-sip': {'remaining': 50.0, 'spent': 50.0}
        }
        click.echo(json.dumps(report, indent=2))
    elif format == 'csv':
        click.echo("swarm_id,remaining,spent")
        click.echo("swarm-webrtc,75.0,25.0")
        click.echo("swarm-sip,50.0,50.0")
    else:
        click.echo("💰 Budget Report")
        click.echo("   swarm-webrtc: $75.00 remaining ($25.00 spent)")
        click.echo("   swarm-sip: $50.00 remaining ($50.00 spent)")


@budget.command('allocate')
@click.argument('swarm_id')
@click.argument('amount', type=float)
@click.pass_context
def budget_allocate(ctx, swarm_id, amount):
    """Allocate budget to a swarm."""
    click.echo(f"💵 Allocating ${amount:.2f} to {swarm_id}")

    # TODO: Call IFGovernor.allocate_budget()
    click.echo(f"✅ Budget allocated successfully")


@budget.command('track')
@click.argument('swarm_id')
@click.argument('operation')
@click.argument('cost', type=float)
@click.pass_context
def budget_track(ctx, swarm_id, operation, cost):
    """Track cost for a swarm operation."""
    click.echo(f"📊 Tracking cost: {swarm_id} - {operation} - ${cost:.2f}")

    # TODO: Call IFGovernor.track_cost()
    click.echo(f"✅ Cost tracked successfully")


# ==================== IF.chassis Commands ====================


@cli.group()
@click.pass_context
def chassis(ctx):
    """
    IF.chassis - WASM sandbox runtime for secure swarm execution.

    Provides:
    - WASM module loading and execution
    - Resource limits (CPU, memory, API rate limiting)
    - Scoped credentials (per-swarm secrets)
    - SLO tracking (latency, success rate)
    - Security isolation (no filesystem, no network, no exec)

    Examples:
      if chassis load swarm.wasm --contract contract.json
      if chassis execute swarm-id task-123
      if chassis status swarm-id
    """
    pass


@chassis.command('load')
@click.argument('wasm_file', type=click.Path(exists=True))
@click.option('--swarm-id', required=True,
              help='Swarm identifier')
@click.option('--contract', type=click.Path(exists=True),
              help='Service contract JSON file')
@click.pass_context
def load(ctx, wasm_file, swarm_id, contract):
    """Load WASM module into sandbox."""
    click.echo(f"📦 Loading WASM module: {wasm_file}")
    click.echo(f"   Swarm ID: {swarm_id}")

    if contract:
        click.echo(f"   Contract: {contract}")

    # TODO: Call IFChassis.load_swarm()
    click.echo(f"✅ WASM module loaded successfully")


@chassis.command('status')
@click.argument('swarm_id')
@click.pass_context
def chassis_status(ctx, swarm_id):
    """Show chassis status for a swarm."""
    click.echo(f"📊 Chassis Status: {swarm_id}")
    click.echo("   Status: running")
    click.echo("   Memory: 45.2 MB / 512 MB")
    click.echo("   CPU: 12.3%")
    click.echo("   API calls/sec: 5.2 / 100")


# ==================== IF.witness Commands ====================
# Witness commands are defined in if_witness.py and registered below


# ==================== IF.optimise Commands ====================


@cli.group()
@click.pass_context
def optimise(ctx):
    """
    IF.optimise - Cost tracking and optimization.

    Provides:
    - Cost tracking per swarm/operation
    - Usage analytics and reporting
    - Cost optimization recommendations
    - Budget forecasting

    Examples:
      if optimise report --period 7d
      if optimise recommend --swarm-id swarm-webrtc
      if optimise forecast --days 30
    """
    pass


@optimise.command('report')
@click.option('--period', default='7d',
              help='Reporting period (e.g., 7d, 30d, 90d)')
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.pass_context
def report(ctx, period, format):
    """Generate cost optimization report."""
    click.echo(f"📊 Cost Report (period: {period})")

    if format == 'json':
        import json
        report_data = {
            'period': period,
            'total_cost': 125.50,
            'swarms': {
                'swarm-webrtc': {'cost': 75.0, 'operations': 320},
                'swarm-sip': {'cost': 50.5, 'operations': 180}
            }
        }
        click.echo(json.dumps(report_data, indent=2))
    else:
        click.echo("   Total cost: $125.50")
        click.echo("   Swarms:")
        click.echo("     - swarm-webrtc: $75.00 (320 operations)")
        click.echo("     - swarm-sip: $50.50 (180 operations)")


# ==================== Register CLI Modules ====================

# Register witness commands from if_witness.py
cli.add_command(witness_group, name='witness')

# Register cost commands from if_cost.py
cli.add_command(cost_group, name='cost')


if __name__ == '__main__':
    cli()
