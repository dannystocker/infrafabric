"""
IF.cost CLI Integration

Commands for cost tracking, budget management, and spending history.

Usage:
    if cost report --period 7d --format json
    if cost budget --swarm-id swarm-webrtc
    if cost history --period 30d --export costs.csv
"""

import click
import json
import csv
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from io import StringIO


# Mock cost functions - will be replaced with actual IF.optimise integration
def _get_cost_report(period: str = '7d', swarm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get cost breakdown report.

    Returns mock data until IF.optimise is implemented.
    """
    # TODO: Replace with actual IF.optimise.get_cost_report()
    period_days = int(period.replace('d', ''))

    return {
        'period': period,
        'period_days': period_days,
        'total_cost': 342.75,
        'breakdown': {
            'swarm-webrtc': {
                'total_cost': 187.50,
                'operations': 1250,
                'avg_cost_per_op': 0.15,
                'model': 'sonnet',
                'cost_per_hour': 15.0,
                'hours_active': 12.5
            },
            'swarm-sip': {
                'total_cost': 95.25,
                'operations': 850,
                'avg_cost_per_op': 0.11,
                'model': 'sonnet',
                'cost_per_hour': 15.0,
                'hours_active': 6.35
            },
            'swarm-ndi': {
                'total_cost': 60.00,
                'operations': 1200,
                'avg_cost_per_op': 0.05,
                'model': 'haiku',
                'cost_per_hour': 2.0,
                'hours_active': 30.0
            }
        } if not swarm_id else {
            swarm_id: {
                'total_cost': 187.50,
                'operations': 1250,
                'avg_cost_per_op': 0.15,
                'model': 'sonnet',
                'cost_per_hour': 15.0,
                'hours_active': 12.5
            }
        }
    }


def _get_budget_status(swarm_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get budget remaining for swarms.

    Returns mock data until IF.optimise is implemented.
    """
    # TODO: Replace with actual IF.optimise.get_budget_status()
    all_budgets = {
        'swarm-webrtc': {
            'allocated': 500.00,
            'spent': 187.50,
            'remaining': 312.50,
            'utilization': 0.375,
            'burn_rate_per_hour': 15.0,
            'estimated_hours_remaining': 20.83
        },
        'swarm-sip': {
            'allocated': 300.00,
            'spent': 95.25,
            'remaining': 204.75,
            'utilization': 0.3175,
            'burn_rate_per_hour': 15.0,
            'estimated_hours_remaining': 13.65
        },
        'swarm-ndi': {
            'allocated': 200.00,
            'spent': 60.00,
            'remaining': 140.00,
            'utilization': 0.30,
            'burn_rate_per_hour': 2.0,
            'estimated_hours_remaining': 70.00
        }
    }

    if swarm_id:
        return {swarm_id: all_budgets.get(swarm_id, {})}
    return all_budgets


def _get_cost_history(period: str = '30d', swarm_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get cost history over time.

    Returns mock data until IF.optimise is implemented.
    """
    # TODO: Replace with actual IF.optimise.get_cost_history()
    period_days = int(period.replace('d', ''))
    history = []

    base_date = datetime.now() - timedelta(days=period_days)

    for day_offset in range(period_days):
        date = base_date + timedelta(days=day_offset)
        date_str = date.strftime('%Y-%m-%d')

        history.append({
            'date': date_str,
            'total_cost': 15.5 + (day_offset * 0.3),
            'operations': 50 + (day_offset * 2),
            'swarms_active': 2 + (day_offset % 2),
            'breakdown': {
                'swarm-webrtc': 8.5 + (day_offset * 0.15),
                'swarm-sip': 5.0 + (day_offset * 0.10),
                'swarm-ndi': 2.0 + (day_offset * 0.05)
            } if not swarm_id else {
                swarm_id: 8.5 + (day_offset * 0.15)
            }
        })

    return history


@click.group('cost')
@click.pass_context
def cost_group(ctx):
    """
    IF.cost - Cost tracking and budget management.

    Provides visibility into swarm costs, budget utilization,
    and spending trends over time.

    Examples:
      if cost report --period 7d --format json
      if cost budget --swarm-id swarm-webrtc
      if cost history --period 30d --export costs.csv
    """
    pass


@cost_group.command('report')
@click.option('--period', default='7d',
              help='Reporting period (e.g., 7d, 30d, 90d)')
@click.option('--swarm-id', help='Filter by specific swarm')
@click.option('--format', type=click.Choice(['text', 'json', 'csv']), default='text',
              help='Output format')
@click.pass_context
def report(ctx, period, swarm_id, format):
    """
    Show cost breakdown report.

    Displays total costs, per-swarm breakdown, operations count,
    and cost efficiency metrics.

    Examples:
      if cost report
      if cost report --period 30d --format json
      if cost report --swarm-id swarm-webrtc --format csv
    """
    # Get cost report
    data = _get_cost_report(period, swarm_id)

    # Output results
    if format == 'json':
        click.echo(json.dumps(data, indent=2))

    elif format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['swarm_id', 'total_cost', 'operations', 'avg_cost_per_op', 'model', 'hours_active'])

        for swarm, details in data['breakdown'].items():
            writer.writerow([
                swarm,
                f"{details['total_cost']:.2f}",
                details['operations'],
                f"{details['avg_cost_per_op']:.3f}",
                details['model'],
                f"{details['hours_active']:.2f}"
            ])

        click.echo(output.getvalue().strip())

    else:  # text
        click.echo(f"💰 Cost Report (Period: {period})")
        click.echo(f"   Total Cost: ${data['total_cost']:.2f}\n")

        click.echo("   Per-Swarm Breakdown:")
        for swarm, details in data['breakdown'].items():
            efficiency = "efficient" if details['avg_cost_per_op'] < 0.10 else "moderate" if details['avg_cost_per_op'] < 0.20 else "expensive"

            click.echo(f"\n   {swarm}:")
            click.echo(f"      Total Cost: ${details['total_cost']:.2f}")
            click.echo(f"      Operations: {details['operations']}")
            click.echo(f"      Avg Cost/Op: ${details['avg_cost_per_op']:.3f} ({efficiency})")
            click.echo(f"      Model: {details['model']}")
            click.echo(f"      Hours Active: {details['hours_active']:.2f}h")
            click.echo(f"      Cost/Hour: ${details['cost_per_hour']:.2f}")

    if ctx.obj.get('DEBUG'):
        click.echo(f"\n   [DEBUG] Full cost data: {data}", err=True)


@cost_group.command('budget')
@click.option('--swarm-id', help='Filter by specific swarm')
@click.option('--format', type=click.Choice(['text', 'json', 'csv']), default='text',
              help='Output format')
@click.pass_context
def budget(ctx, swarm_id, format):
    """
    Show budget status and remaining balances.

    Displays allocated budgets, spending, remaining balance,
    utilization percentage, and estimated hours remaining.

    Examples:
      if cost budget
      if cost budget --swarm-id swarm-webrtc
      if cost budget --format json
    """
    # Get budget status
    data = _get_budget_status(swarm_id)

    # Output results
    if format == 'json':
        click.echo(json.dumps(data, indent=2))

    elif format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['swarm_id', 'allocated', 'spent', 'remaining', 'utilization', 'burn_rate', 'hours_remaining'])

        for swarm, budget in data.items():
            writer.writerow([
                swarm,
                f"{budget['allocated']:.2f}",
                f"{budget['spent']:.2f}",
                f"{budget['remaining']:.2f}",
                f"{budget['utilization']:.1%}",
                f"{budget['burn_rate_per_hour']:.2f}",
                f"{budget['estimated_hours_remaining']:.2f}"
            ])

        click.echo(output.getvalue().strip())

    else:  # text
        click.echo("💵 Budget Status\n")

        for swarm, budget in data.items():
            utilization = budget['utilization']
            status_icon = "🟢" if utilization < 0.5 else "🟡" if utilization < 0.8 else "🔴"
            status_text = "healthy" if utilization < 0.5 else "warning" if utilization < 0.8 else "critical"

            click.echo(f"   {swarm}: {status_icon} {status_text}")
            click.echo(f"      Allocated: ${budget['allocated']:.2f}")
            click.echo(f"      Spent: ${budget['spent']:.2f}")
            click.echo(f"      Remaining: ${budget['remaining']:.2f}")
            click.echo(f"      Utilization: {budget['utilization']:.1%}")
            click.echo(f"      Burn Rate: ${budget['burn_rate_per_hour']:.2f}/hour")
            click.echo(f"      Est. Hours Remaining: {budget['estimated_hours_remaining']:.1f}h")
            click.echo()

    if ctx.obj.get('DEBUG'):
        click.echo(f"   [DEBUG] Full budget data: {data}", err=True)


@cost_group.command('history')
@click.option('--period', default='30d',
              help='Historical period (e.g., 7d, 30d, 90d)')
@click.option('--swarm-id', help='Filter by specific swarm')
@click.option('--export', type=click.Path(),
              help='Export to CSV file')
@click.option('--format', type=click.Choice(['text', 'json', 'csv']), default='text',
              help='Output format (ignored if --export is used)')
@click.pass_context
def history(ctx, period, swarm_id, export, format):
    """
    Show cost history over time.

    Displays daily cost trends, operations count, and per-swarm
    breakdown to identify spending patterns.

    Examples:
      if cost history --period 7d
      if cost history --period 30d --export costs.csv
      if cost history --swarm-id swarm-webrtc --format json
    """
    # Get cost history
    data = _get_cost_history(period, swarm_id)

    # Handle export to file
    if export:
        with open(export, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header row
            swarm_ids = list(data[0]['breakdown'].keys()) if data else []
            writer.writerow(['date', 'total_cost', 'operations', 'swarms_active'] + swarm_ids)

            # Data rows
            for entry in data:
                row = [
                    entry['date'],
                    f"{entry['total_cost']:.2f}",
                    entry['operations'],
                    entry['swarms_active']
                ]
                for swarm_id in swarm_ids:
                    row.append(f"{entry['breakdown'].get(swarm_id, 0):.2f}")
                writer.writerow(row)

        click.echo(f"✅ Cost history exported to: {export}")
        click.echo(f"   {len(data)} entries ({period})")
        return

    # Output to stdout
    if format == 'json':
        click.echo(json.dumps({'period': period, 'entries': data}, indent=2))

    elif format == 'csv':
        swarm_ids = list(data[0]['breakdown'].keys()) if data else []
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['date', 'total_cost', 'operations', 'swarms_active'] + swarm_ids)

        for entry in data:
            row = [
                entry['date'],
                f"{entry['total_cost']:.2f}",
                entry['operations'],
                entry['swarms_active']
            ]
            for swarm_id in swarm_ids:
                row.append(f"{entry['breakdown'].get(swarm_id, 0):.2f}")
            writer.writerow(row)

        click.echo(output.getvalue().strip())

    else:  # text
        click.echo(f"📊 Cost History (Period: {period})")
        click.echo(f"   {len(data)} entries\n")

        # Show first 7 and last 3 entries for readability
        display_entries = data[:7] + (['...'] if len(data) > 10 else []) + data[-3:] if len(data) > 10 else data

        for entry in display_entries:
            if entry == '...':
                click.echo("   ...")
                continue

            click.echo(f"   {entry['date']}: ${entry['total_cost']:.2f} ({entry['operations']} ops, {entry['swarms_active']} swarms)")

        # Summary
        total_cost = sum(e['total_cost'] for e in data if e != '...')
        total_ops = sum(e['operations'] for e in data if e != '...')
        avg_daily_cost = total_cost / len(data) if data else 0

        click.echo(f"\n   Summary:")
        click.echo(f"      Total Cost: ${total_cost:.2f}")
        click.echo(f"      Total Operations: {total_ops}")
        click.echo(f"      Avg Daily Cost: ${avg_daily_cost:.2f}")

    if ctx.obj.get('DEBUG'):
        click.echo(f"\n   [DEBUG] Full history data (first 3 entries): {data[:3]}", err=True)


# Register commands with main CLI (called from if_main.py)
def register_cost_commands(cli):
    """Register cost commands with main CLI."""
    cli.add_command(cost_group, name='cost')
