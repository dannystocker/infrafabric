#!/usr/bin/env python3
"""
IF.vmix CLI - vMix Production Control

Commands:
  add       - Add vMix instance
  list      - List vMix instances
  test      - Test connection to vMix
  remove    - Remove vMix instance

  cut       - Cut to input (instant)
  fade      - Fade to input
  preview   - Set preview input
  transition - Custom transition
  overlay   - Set overlay input

  ndi       - NDI source control
  stream    - Streaming control
  record    - Recording control

  status    - Get vMix status
  inputs    - List inputs
  state     - Get production state

  ptz       - PTZ camera control
  audio     - Audio control

Philosophy: Dead-simple CLI for video engineers.
Every operation logged to IF.witness for audit trails.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from uuid import uuid4

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vmix.client import VMixClient, VMixError, VMixConnectionError
from vmix.config import VMixConfig, VMixConfigError
from witness.database import WitnessDatabase


def log_vmix_operation(instance_name: str, operation: str, params: dict, result: dict):
    """Log vMix operation to IF.witness"""
    try:
        db = WitnessDatabase()
        db.create_entry(
            event=f"vmix_{operation}",
            component="IF.vmix",
            trace_id=f"vmix-{instance_name}-{uuid4()}",
            payload={
                'instance': instance_name,
                'operation': operation,
                'params': params,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        db.close()
    except Exception as e:
        # Don't fail operation if logging fails
        click.echo(f"Warning: Failed to log to IF.witness: {e}", err=True)


@click.group()
def vmix():
    """vMix production control"""
    pass


# ============================================================================
# Connection Management Commands
# ============================================================================

@vmix.command()
@click.argument('name')
@click.option('--host', required=True, help='vMix host IP or hostname')
@click.option('--port', default=8088, help='vMix API port (default: 8088)')
def add(name, host, port):
    """Add vMix instance"""
    try:
        config = VMixConfig()

        # Add to config
        instance = config.add_instance(name, host, port)

        # Test connection
        click.echo(f"Testing connection to {host}:{port}...")
        client = VMixClient(host, port)

        try:
            status = client.get_status()
            click.echo(f"✓ Connected to vMix {status.version} ({status.edition})")
            click.echo(f"✓ Instance '{name}' added successfully")

            # Log to IF.witness
            log_vmix_operation(name, 'add_instance', {
                'host': host,
                'port': port
            }, {
                'success': True,
                'version': status.version,
                'edition': status.edition
            })

        except VMixConnectionError as e:
            click.echo(f"⚠️  Warning: Could not connect to vMix: {e}", err=True)
            click.echo(f"   Instance '{name}' added but connection failed")

    except VMixConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def list(format):
    """List vMix instances"""
    try:
        config = VMixConfig()
        instances = config.list_instances()

        if not instances:
            click.echo("No vMix instances configured")
            click.echo("\nAdd an instance with: if vmix add <name> --host <ip>")
            return

        if format == 'json':
            click.echo(json.dumps([inst.to_dict() for inst in instances], indent=2))
        else:
            click.echo(f"\nConfigured vMix Instances ({len(instances)})\n")
            click.echo(f"{'Name':<20} {'Host':<20} {'Port':<10} {'Added':<25}")
            click.echo("-" * 75)

            for inst in instances:
                added_date = inst.added_at[:19] if inst.added_at else 'unknown'
                click.echo(f"{inst.name:<20} {inst.host:<20} {inst.port:<10} {added_date:<25}")

    except VMixConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
def test(instance):
    """Test connection to vMix instance"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        click.echo(f"Testing connection to {inst.host}:{inst.port}...")

        client = VMixClient(inst.host, inst.port)
        status = client.get_status()

        click.echo(f"✓ Connection successful")
        click.echo(f"  Version: {status.version}")
        click.echo(f"  Edition: {status.edition}")
        click.echo(f"  Inputs: {len(status.inputs)}")
        click.echo(f"  Active: Input {status.active_input}")
        click.echo(f"  Preview: Input {status.preview_input}")
        click.echo(f"  Recording: {status.recording}")
        click.echo(f"  Streaming: {status.streaming}")

        # Log to IF.witness
        log_vmix_operation(instance, 'test_connection', {}, {
            'success': True,
            'version': status.version
        })

    except VMixConnectionError as e:
        click.echo(f"❌ Connection failed: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
@click.confirmation_option(prompt='Are you sure you want to remove this instance?')
def remove(instance):
    """Remove vMix instance"""
    try:
        config = VMixConfig()

        if config.remove_instance(instance):
            click.echo(f"✓ Instance '{instance}' removed")

            # Log to IF.witness
            log_vmix_operation(instance, 'remove_instance', {}, {'success': True})
        else:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

    except VMixConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Production Control Commands
# ============================================================================

@vmix.command()
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
def cut(instance, input_num):
    """Cut to input (instant transition)"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.cut(input_num)

        click.echo(f"✓ Cut to input {input_num}")

        # Log to IF.witness
        log_vmix_operation(instance, 'cut', {'input': input_num}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
@click.option('--duration', type=int, default=1000, help='Fade duration in milliseconds (default: 1000)')
def fade(instance, input_num, duration):
    """Fade to input"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.fade(input_num, duration)

        click.echo(f"✓ Fade to input {input_num} ({duration}ms)")

        # Log to IF.witness
        log_vmix_operation(instance, 'fade', {
            'input': input_num,
            'duration': duration
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
def preview(instance, input_num):
    """Set preview input"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.preview(input_num)

        click.echo(f"✓ Preview set to input {input_num}")

        # Log to IF.witness
        log_vmix_operation(instance, 'preview', {'input': input_num}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
@click.option('--type', 'transition_type', required=True, help='Transition type (Fade, Merge, Wipe, etc.)')
@click.option('--duration', type=int, default=1000, help='Duration in milliseconds (default: 1000)')
@click.option('--input', 'input_num', type=int, help='Input number (optional, uses preview if not specified)')
def transition(instance, transition_type, duration, input_num):
    """Execute custom transition"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.transition(transition_type, duration, input_num)

        if input_num:
            click.echo(f"✓ Transition {transition_type} to input {input_num} ({duration}ms)")
        else:
            click.echo(f"✓ Transition {transition_type} ({duration}ms)")

        # Log to IF.witness
        log_vmix_operation(instance, 'transition', {
            'type': transition_type,
            'duration': duration,
            'input': input_num
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
@click.option('--num', 'overlay_num', type=int, required=True, help='Overlay number (1-4)')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
@click.option('--action', default='OverlayInput',
              type=click.Choice(['OverlayInput', 'OverlayInputIn', 'OverlayInputOut']),
              help='Overlay action (default: OverlayInput)')
def overlay(instance, overlay_num, input_num, action):
    """Set overlay input"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        if not 1 <= overlay_num <= 4:
            click.echo(f"❌ Overlay number must be 1-4", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.overlay(overlay_num, input_num, action)

        click.echo(f"✓ Overlay {overlay_num} set to input {input_num}")

        # Log to IF.witness
        log_vmix_operation(instance, 'overlay', {
            'overlay_num': overlay_num,
            'input': input_num,
            'action': action
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# NDI Control Commands
# ============================================================================

@vmix.group()
def ndi():
    """NDI source control"""
    pass


@ndi.command('add')
@click.argument('instance')
@click.option('--source', required=True, help='NDI source name')
def ndi_add(instance, source):
    """Add NDI input source"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.add_ndi_input(source)

        click.echo(f"✓ NDI source '{source}' added")

        # Log to IF.witness
        log_vmix_operation(instance, 'ndi_add', {'source': source}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ndi.command('list')
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def ndi_list(instance, format):
    """List NDI inputs"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        inputs = client.get_inputs()

        # Filter NDI inputs
        ndi_inputs = [inp for inp in inputs if inp.type == 'NDI']

        if format == 'json':
            click.echo(json.dumps([inp.to_dict() for inp in ndi_inputs], indent=2))
        else:
            if not ndi_inputs:
                click.echo("No NDI inputs found")
                return

            click.echo(f"\nNDI Inputs ({len(ndi_inputs)})\n")
            click.echo(f"{'Input':<10} {'Title':<30} {'State':<15}")
            click.echo("-" * 55)

            for inp in ndi_inputs:
                click.echo(f"{inp.number:<10} {inp.title:<30} {inp.state:<15}")

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ndi.command('remove')
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number to remove')
def ndi_remove(instance, input_num):
    """Remove NDI input"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.remove_input(input_num)

        click.echo(f"✓ Input {input_num} removed")

        # Log to IF.witness
        log_vmix_operation(instance, 'ndi_remove', {'input': input_num}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Streaming Commands
# ============================================================================

@vmix.group()
def stream():
    """Streaming control"""
    pass


@stream.command('start')
@click.argument('instance')
@click.option('--rtmp', help='RTMP URL (e.g., rtmp://server/live)')
@click.option('--key', help='Stream key')
@click.option('--channel', type=int, default=0, help='Stream channel (0-2, default: 0)')
def stream_start(instance, rtmp, key, channel):
    """Start streaming"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)

        # Set RTMP URL and key if provided
        if rtmp and key:
            client.set_stream_url(rtmp, key, channel)
            click.echo(f"✓ Stream URL configured")

        # Start streaming
        client.start_streaming(channel)

        click.echo(f"✓ Streaming started on channel {channel}")

        # Log to IF.witness
        log_vmix_operation(instance, 'stream_start', {
            'channel': channel,
            'rtmp': rtmp if rtmp else None
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@stream.command('stop')
@click.argument('instance')
@click.option('--channel', type=int, default=0, help='Stream channel (0-2, default: 0)')
def stream_stop(instance, channel):
    """Stop streaming"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.stop_streaming(channel)

        click.echo(f"✓ Streaming stopped on channel {channel}")

        # Log to IF.witness
        log_vmix_operation(instance, 'stream_stop', {'channel': channel}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@stream.command('status')
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def stream_status(instance, format):
    """Get streaming status"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        status = client.get_stream_status()

        if format == 'json':
            click.echo(json.dumps(status.to_dict(), indent=2))
        else:
            click.echo(f"\nStreaming Status")
            click.echo("-" * 30)
            click.echo(f"Streaming: {status.streaming}")

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Recording Commands
# ============================================================================

@vmix.group()
def record():
    """Recording control"""
    pass


@record.command('start')
@click.argument('instance')
@click.option('--file', 'filename', help='Output filename (optional)')
@click.option('--format', 'file_format', help='File format (MP4, AVI, etc.)')
def record_start(instance, filename, file_format):
    """Start recording"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.start_recording(filename)

        if filename:
            click.echo(f"✓ Recording started: {filename}")
        else:
            click.echo(f"✓ Recording started")

        # Log to IF.witness
        log_vmix_operation(instance, 'record_start', {
            'filename': filename,
            'format': file_format
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@record.command('stop')
@click.argument('instance')
def record_stop(instance):
    """Stop recording"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.stop_recording()

        click.echo(f"✓ Recording stopped")

        # Log to IF.witness
        log_vmix_operation(instance, 'record_stop', {}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@record.command('status')
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def record_status(instance, format):
    """Get recording status"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        status = client.get_record_status()

        if format == 'json':
            click.echo(json.dumps(status.to_dict(), indent=2))
        else:
            click.echo(f"\nRecording Status")
            click.echo("-" * 30)
            click.echo(f"Recording: {status.recording}")

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Status & Query Commands
# ============================================================================

@vmix.command()
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def status(instance, format):
    """Get vMix status"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        status = client.get_status()

        if format == 'json':
            click.echo(json.dumps(status.to_dict(), indent=2))
        else:
            click.echo(f"\nvMix Status: {inst.name}")
            click.echo("-" * 50)
            click.echo(f"Version:    {status.version}")
            click.echo(f"Edition:    {status.edition}")
            click.echo(f"Inputs:     {len(status.inputs)}")
            click.echo(f"Active:     Input {status.active_input}")
            click.echo(f"Preview:    Input {status.preview_input}")
            click.echo(f"Recording:  {status.recording}")
            click.echo(f"Streaming:  {status.streaming}")
            click.echo(f"Audio:      {status.audio}")

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def inputs(instance, format):
    """List all inputs"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        inputs = client.get_inputs()

        if format == 'json':
            click.echo(json.dumps([inp.to_dict() for inp in inputs], indent=2))
        else:
            if not inputs:
                click.echo("No inputs found")
                return

            click.echo(f"\nInputs ({len(inputs)})\n")
            click.echo(f"{'Input':<10} {'Type':<15} {'Title':<30} {'State':<15}")
            click.echo("-" * 70)

            for inp in inputs:
                click.echo(f"{inp.number:<10} {inp.type:<15} {inp.title:<30} {inp.state:<15}")

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@vmix.command()
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def state(instance, format):
    """Get production state (active, preview)"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        status = client.get_status()

        # Find active and preview inputs
        active_input = next((inp for inp in status.inputs if inp.number == status.active_input), None)
        preview_input = next((inp for inp in status.inputs if inp.number == status.preview_input), None)

        if format == 'json':
            click.echo(json.dumps({
                'active': {
                    'number': status.active_input,
                    'title': active_input.title if active_input else None,
                    'type': active_input.type if active_input else None
                },
                'preview': {
                    'number': status.preview_input,
                    'title': preview_input.title if preview_input else None,
                    'type': preview_input.type if preview_input else None
                }
            }, indent=2))
        else:
            click.echo(f"\nProduction State")
            click.echo("-" * 50)

            if active_input:
                click.echo(f"Active:  Input {active_input.number} - {active_input.title} ({active_input.type})")
            else:
                click.echo(f"Active:  Input {status.active_input}")

            if preview_input:
                click.echo(f"Preview: Input {preview_input.number} - {preview_input.title} ({preview_input.type})")
            else:
                click.echo(f"Preview: Input {status.preview_input}")

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# PTZ Camera Control Commands
# ============================================================================

@vmix.group()
def ptz():
    """PTZ camera control"""
    pass


@ptz.command('move')
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
@click.option('--pan', type=int, help='Pan value (-100 to 100)')
@click.option('--tilt', type=int, help='Tilt value (-100 to 100)')
@click.option('--zoom', type=int, help='Zoom value (0 to 100)')
def ptz_move(instance, input_num, pan, tilt, zoom):
    """Move PTZ camera"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        if pan is None and tilt is None and zoom is None:
            click.echo("❌ Must specify at least one of --pan, --tilt, or --zoom", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.ptz_move(input_num, pan, tilt, zoom)

        parts = []
        if pan is not None:
            parts.append(f"pan={pan}")
        if tilt is not None:
            parts.append(f"tilt={tilt}")
        if zoom is not None:
            parts.append(f"zoom={zoom}")

        click.echo(f"✓ PTZ moved: {', '.join(parts)}")

        # Log to IF.witness
        log_vmix_operation(instance, 'ptz_move', {
            'input': input_num,
            'pan': pan,
            'tilt': tilt,
            'zoom': zoom
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ptz.command('preset')
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
@click.option('--preset', type=int, required=True, help='Preset number')
def ptz_preset(instance, input_num, preset):
    """Recall PTZ preset"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.ptz_preset(input_num, preset)

        click.echo(f"✓ PTZ preset {preset} recalled")

        # Log to IF.witness
        log_vmix_operation(instance, 'ptz_preset', {
            'input': input_num,
            'preset': preset
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ptz.command('home')
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
def ptz_home(instance, input_num):
    """Move PTZ to home position"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.ptz_home(input_num)

        click.echo(f"✓ PTZ moved to home position")

        # Log to IF.witness
        log_vmix_operation(instance, 'ptz_home', {'input': input_num}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Audio Control Commands
# ============================================================================

@vmix.group()
def audio():
    """Audio control"""
    pass


@audio.command('volume')
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
@click.option('--volume', type=int, required=True, help='Volume level (0-100)')
def audio_volume(instance, input_num, volume):
    """Set input volume"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        if not 0 <= volume <= 100:
            click.echo(f"❌ Volume must be 0-100", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.set_volume(input_num, volume)

        click.echo(f"✓ Volume set to {volume}")

        # Log to IF.witness
        log_vmix_operation(instance, 'audio_volume', {
            'input': input_num,
            'volume': volume
        }, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@audio.command('mute')
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
def audio_mute(instance, input_num):
    """Mute input audio"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.mute(input_num)

        click.echo(f"✓ Input {input_num} muted")

        # Log to IF.witness
        log_vmix_operation(instance, 'audio_mute', {'input': input_num}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@audio.command('unmute')
@click.argument('instance')
@click.option('--input', 'input_num', type=int, required=True, help='Input number')
def audio_unmute(instance, input_num):
    """Unmute input audio"""
    try:
        config = VMixConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = VMixClient(inst.host, inst.port)
        client.unmute(input_num)

        click.echo(f"✓ Input {input_num} unmuted")

        # Log to IF.witness
        log_vmix_operation(instance, 'audio_unmute', {'input': input_num}, {'success': True})

    except VMixError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    vmix()
