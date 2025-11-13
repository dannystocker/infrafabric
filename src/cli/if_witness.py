"""
IF.witness CLI Integration

Commands for querying and validating tamper-evident audit logs.

Usage:
    if witness query --swarm-id swarm-webrtc --limit 100
    if witness trace abc123 --format json
    if witness verify --start-hash abc123 --end-hash def456
"""

import click
import json
from typing import Optional, List, Dict, Any


# Mock witness functions - will be replaced with actual IF.witness integration
def _query_witness_logs(
    swarm_id: Optional[str] = None,
    component: Optional[str] = None,
    operation: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Query witness audit logs.

    Returns mock data until IF.witness is implemented.
    """
    # TODO: Replace with actual IF.witness.query_logs()
    return [
        {
            'timestamp': '2025-11-13T10:30:00Z',
            'component': 'IF.coordinator',
            'operation': 'task_claimed',
            'swarm_id': swarm_id or 'swarm-webrtc',
            'task_id': 'task-123',
            'hash': 'abc123def456',
            'prev_hash': '000000000000'
        },
        {
            'timestamp': '2025-11-13T10:31:15Z',
            'component': 'IF.governor',
            'operation': 'budget_tracked',
            'swarm_id': swarm_id or 'swarm-webrtc',
            'cost': 2.5,
            'hash': 'def456ghi789',
            'prev_hash': 'abc123def456'
        },
        {
            'timestamp': '2025-11-13T10:32:30Z',
            'component': 'IF.chassis',
            'operation': 'task_executed',
            'swarm_id': swarm_id or 'swarm-webrtc',
            'duration_ms': 1250,
            'hash': 'ghi789jkl012',
            'prev_hash': 'def456ghi789'
        }
    ][:limit]


def _trace_token(token: str) -> List[Dict[str, Any]]:
    """
    Trace full provenance chain for a token/hash.

    Returns mock data until IF.witness is implemented.
    """
    # TODO: Replace with actual IF.witness.trace_chain()
    return [
        {
            'step': 1,
            'timestamp': '2025-11-13T10:30:00Z',
            'component': 'IF.coordinator',
            'operation': 'task_created',
            'hash': token,
            'prev_hash': '000000000000',
            'details': {
                'task_id': 'task-123',
                'requester': 'orchestrator'
            }
        },
        {
            'step': 2,
            'timestamp': '2025-11-13T10:30:05Z',
            'component': 'IF.governor',
            'operation': 'swarm_matched',
            'hash': 'def456ghi789',
            'prev_hash': token,
            'details': {
                'swarm_id': 'swarm-webrtc',
                'capability_match': 0.95,
                'cost_per_hour': 15.0
            }
        },
        {
            'step': 3,
            'timestamp': '2025-11-13T10:30:10Z',
            'component': 'IF.coordinator',
            'operation': 'task_claimed',
            'hash': 'ghi789jkl012',
            'prev_hash': 'def456ghi789',
            'details': {
                'swarm_id': 'swarm-webrtc',
                'task_id': 'task-123'
            }
        },
        {
            'step': 4,
            'timestamp': '2025-11-13T10:32:30Z',
            'component': 'IF.chassis',
            'operation': 'task_completed',
            'hash': 'jkl012mno345',
            'prev_hash': 'ghi789jkl012',
            'details': {
                'duration_ms': 2200,
                'success': True
            }
        }
    ]


def _verify_hash_chain(
    start_hash: Optional[str] = None,
    end_hash: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify hash chain integrity.

    Returns mock data until IF.witness is implemented.
    """
    # TODO: Replace with actual IF.witness.verify_chain()
    return {
        'valid': True,
        'start_hash': start_hash or '000000000000',
        'end_hash': end_hash or 'jkl012mno345',
        'total_entries': 347,
        'verified_entries': 347,
        'broken_links': 0,
        'verification_time_ms': 125
    }


@click.group('witness')
@click.pass_context
def witness_group(ctx):
    """
    IF.witness - Audit logging and provenance tracking.

    Provides tamper-evident audit logs with hash chains for full
    provenance tracking and integrity verification.

    Examples:
      if witness query --swarm-id swarm-webrtc --limit 100
      if witness trace abc123def456 --format json
      if witness verify --start-hash abc123 --end-hash def456
    """
    pass


@witness_group.command('query')
@click.option('--swarm-id', help='Filter by swarm ID')
@click.option('--component', help='Filter by component (coordinator, governor, chassis)')
@click.option('--operation', help='Filter by operation type')
@click.option('--limit', type=int, default=100,
              help='Maximum number of records to return')
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.pass_context
def query(ctx, swarm_id, component, operation, limit, format):
    """
    Query audit logs with optional filters.

    Examples:
      if witness query --swarm-id swarm-webrtc --limit 50
      if witness query --component IF.governor --format json
      if witness query --operation task_claimed --limit 10
    """
    # Build filter description
    filters = []
    if swarm_id:
        filters.append(f"swarm_id={swarm_id}")
    if component:
        filters.append(f"component={component}")
    if operation:
        filters.append(f"operation={operation}")

    filter_str = ", ".join(filters) if filters else "none"

    # Query logs
    logs = _query_witness_logs(swarm_id, component, operation, limit)

    # Output results
    if format == 'json':
        output = {
            'query': {
                'filters': {
                    'swarm_id': swarm_id,
                    'component': component,
                    'operation': operation,
                    'limit': limit
                },
                'result_count': len(logs)
            },
            'logs': logs
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(f"🔍 Querying audit logs")
        click.echo(f"   Filters: {filter_str}")
        click.echo(f"   Limit: {limit}")
        click.echo(f"\n📜 Audit Log ({len(logs)} entries):\n")

        for log in logs:
            timestamp = log.get('timestamp', 'N/A')
            comp = log.get('component', 'N/A')
            op = log.get('operation', 'N/A')
            swarm = log.get('swarm_id', 'N/A')
            hash_val = log.get('hash', 'N/A')[:12]

            click.echo(f"   {timestamp} | {comp:20s} | {op:20s} | {swarm:15s} | {hash_val}...")

        if ctx.obj.get('DEBUG'):
            click.echo(f"\n   [DEBUG] Full log data: {logs}", err=True)


@witness_group.command('trace')
@click.argument('token')
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.pass_context
def trace(ctx, token, format):
    """
    Trace full provenance chain for a token/hash.

    Shows complete audit trail starting from the given hash,
    following the hash chain to reveal all related operations.

    Arguments:
      token: Hash token to trace (e.g., abc123def456)

    Examples:
      if witness trace abc123def456
      if witness trace ghi789jkl012 --format json
    """
    # Trace the token
    chain = _trace_token(token)

    # Output results
    if format == 'json':
        output = {
            'trace': {
                'token': token,
                'chain_length': len(chain)
            },
            'chain': chain
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo(f"🔗 Tracing provenance chain for: {token}")
        click.echo(f"   Chain length: {len(chain)} steps\n")

        for entry in chain:
            step = entry.get('step', '?')
            timestamp = entry.get('timestamp', 'N/A')
            comp = entry.get('component', 'N/A')
            op = entry.get('operation', 'N/A')
            hash_val = entry.get('hash', 'N/A')[:12]
            prev_hash = entry.get('prev_hash', 'N/A')[:12]

            click.echo(f"   Step {step}: {timestamp}")
            click.echo(f"      Component: {comp}")
            click.echo(f"      Operation: {op}")
            click.echo(f"      Hash: {hash_val}... → Prev: {prev_hash}...")

            details = entry.get('details', {})
            if details:
                for key, value in details.items():
                    click.echo(f"         {key}: {value}")
            click.echo()

        if ctx.obj.get('DEBUG'):
            click.echo(f"   [DEBUG] Full chain data: {chain}", err=True)


@witness_group.command('verify')
@click.option('--start-hash', help='Starting hash for verification range')
@click.option('--end-hash', help='Ending hash for verification range')
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.pass_context
def verify(ctx, start_hash, end_hash, format):
    """
    Verify hash chain integrity.

    Checks that the audit log hash chain is intact with no
    broken links or tampered entries. Optionally specify a
    range with --start-hash and --end-hash.

    Examples:
      if witness verify
      if witness verify --start-hash abc123 --end-hash def456
      if witness verify --format json
    """
    # Verify chain
    result = _verify_hash_chain(start_hash, end_hash)

    # Output results
    if format == 'json':
        click.echo(json.dumps(result, indent=2))
    else:
        is_valid = result.get('valid', False)
        status_icon = "✅" if is_valid else "❌"
        status_text = "VALID" if is_valid else "INVALID"

        click.echo(f"🔐 Hash Chain Verification")
        click.echo(f"   Status: {status_icon} {status_text}")
        click.echo(f"   Range: {result.get('start_hash', 'N/A')[:12]}... → {result.get('end_hash', 'N/A')[:12]}...")
        click.echo(f"   Total entries: {result.get('total_entries', 0)}")
        click.echo(f"   Verified: {result.get('verified_entries', 0)}")
        click.echo(f"   Broken links: {result.get('broken_links', 0)}")
        click.echo(f"   Verification time: {result.get('verification_time_ms', 0)}ms")

        if not is_valid:
            click.echo(f"\n⚠️  WARNING: Hash chain integrity compromised!", err=True)
            click.echo(f"   Audit log may have been tampered with.", err=True)

        if ctx.obj.get('DEBUG'):
            click.echo(f"\n   [DEBUG] Full verification result: {result}", err=True)


# Register commands with main CLI (called from if_main.py)
def register_witness_commands(cli):
    """Register witness commands with main CLI."""
    cli.add_command(witness_group, name='witness')
