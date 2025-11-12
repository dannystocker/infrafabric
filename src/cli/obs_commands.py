#!/usr/bin/env python3
"""
IF.obs CLI - OBS Studio Control

Commands:
  add       - Add OBS instance
  list      - List OBS instances
  test      - Test connection to OBS
  remove    - Remove OBS instance

  scene     - Scene management (list, switch, create, remove, current)
  source    - Source management (add, list, show, hide, remove)

  stream    - Streaming control (start, stop, status)
  record    - Recording control (start, stop, status)
  virtualcam - Virtual camera control (start, stop)

  filter    - Filter management (add, list, remove)
  media     - Media control (add, play, pause, stop)
  browser   - Browser source management (add)

  status    - Get OBS status
  stats     - Get performance statistics
  version   - Get version information

Philosophy: Dead-simple CLI for streaming engineers.
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

from obs.client import OBSClient, OBSError, OBSConnectionError, OBSAPIError
from obs.config import OBSConfig, OBSConfigError
from witness.database import WitnessDatabase


def log_obs_operation(instance_name: str, operation: str, params: dict, result: dict):
    """Log OBS operation to IF.witness"""
    try:
        db = WitnessDatabase()
        db.create_entry(
            event=f"obs_{operation}",
            component="IF.obs",
            trace_id=f"obs-{instance_name}-{uuid4()}",
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
def obs():
    """OBS Studio control"""
    pass


# ============================================================================
# Connection Management Commands
# ============================================================================

@obs.command()
@click.argument('name')
@click.option('--host', required=True, help='OBS host IP or hostname')
@click.option('--port', default=4455, help='OBS WebSocket port (default: 4455)')
@click.option('--password', help='WebSocket password (optional)')
def add(name, host, port, password):
    """Add OBS instance"""
    try:
        config = OBSConfig()

        # Add to config
        instance = config.add_instance(name, host, port, password)

        # Test connection
        click.echo(f"Testing connection to {host}:{port}...")

        try:
            with OBSClient(host, port, password) as client:
                version = client.get_version()
                click.echo(f"✓ Connected to OBS {version.obs_version}")
                click.echo(f"✓ WebSocket: {version.obs_web_socket_version}")
                click.echo(f"✓ Instance '{name}' added successfully")

                # Log to IF.witness
                log_obs_operation(name, 'add_instance', {
                    'host': host,
                    'port': port
                }, {
                    'success': True,
                    'obs_version': version.obs_version,
                    'websocket_version': version.obs_web_socket_version
                })

        except OBSConnectionError as e:
            click.echo(f"⚠️  Warning: Could not connect to OBS: {e}", err=True)
            click.echo(f"   Instance '{name}' added but connection failed")

    except OBSConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@obs.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def list(format):
    """List OBS instances"""
    try:
        config = OBSConfig()
        instances = config.list_instances()

        if not instances:
            click.echo("No OBS instances configured")
            click.echo("\nAdd an instance with: if-obs add <name> --host <ip>")
            return

        if format == 'json':
            click.echo(json.dumps([inst.to_dict() for inst in instances], indent=2))
        else:
            click.echo(f"\nConfigured OBS Instances ({len(instances)})\n")
            click.echo(f"{'Name':<20} {'Host':<20} {'Port':<10} {'Added':<25}")
            click.echo("-" * 75)

            for inst in instances:
                added_date = inst.added_at[:19] if inst.added_at else 'unknown'
                click.echo(f"{inst.name:<20} {inst.host:<20} {inst.port:<10} {added_date:<25}")

    except OBSConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@obs.command()
@click.argument('instance')
def test(instance):
    """Test connection to OBS instance"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        click.echo(f"Testing connection to {inst.host}:{inst.port}...")

        with OBSClient(inst.host, inst.port, inst.password) as client:
            version = client.get_version()
            stats = client.get_stats()
            scenes = client.get_scene_list()
            current_scene = client.get_current_scene()
            stream_status = client.get_stream_status()
            record_status = client.get_record_status()

            click.echo(f"✓ Connection successful")
            click.echo(f"\nVersion Information:")
            click.echo(f"  OBS:       {version.obs_version}")
            click.echo(f"  WebSocket: {version.obs_web_socket_version}")
            click.echo(f"  Platform:  {version.platform_description or version.platform or 'unknown'}")
            click.echo(f"\nStatus:")
            click.echo(f"  Scenes:    {len(scenes)}")
            click.echo(f"  Current:   {current_scene}")
            click.echo(f"  Streaming: {stream_status.active}")
            click.echo(f"  Recording: {record_status.active}")
            click.echo(f"\nPerformance:")
            click.echo(f"  FPS:       {stats.active_fps:.1f}")
            click.echo(f"  CPU:       {stats.cpu_usage:.1f}%")

            # Log to IF.witness
            log_obs_operation(instance, 'test_connection', {}, {
                'success': True,
                'obs_version': version.obs_version
            })

    except OBSConnectionError as e:
        click.echo(f"❌ Connection failed: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@obs.command()
@click.argument('instance')
@click.confirmation_option(prompt='Are you sure you want to remove this instance?')
def remove(instance):
    """Remove OBS instance"""
    try:
        config = OBSConfig()

        if config.remove_instance(instance):
            click.echo(f"✓ Instance '{instance}' removed")

            # Log to IF.witness
            log_obs_operation(instance, 'remove_instance', {}, {'success': True})
        else:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

    except OBSConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Scene Management Commands
# ============================================================================

@obs.group()
def scene():
    """Scene management"""
    pass


@scene.command('list')
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def scene_list(instance, format):
    """List all scenes"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            scenes = client.get_scene_list()

            if format == 'json':
                click.echo(json.dumps([s.to_dict() for s in scenes], indent=2))
            else:
                if not scenes:
                    click.echo("No scenes found")
                    return

                click.echo(f"\nScenes ({len(scenes)})\n")
                click.echo(f"{'Scene Name':<40} {'Current':<10}")
                click.echo("-" * 50)

                for scene in scenes:
                    current_marker = "✓" if scene.is_current else ""
                    click.echo(f"{scene.name:<40} {current_marker:<10}")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@scene.command('switch')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name to switch to')
def scene_switch(instance, scene):
    """Switch to a different scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.set_current_scene(scene)
            click.echo(f"✓ Switched to scene '{scene}'")

            # Log to IF.witness
            log_obs_operation(instance, 'scene_switch', {'scene': scene}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@scene.command('create')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name to create')
def scene_create(instance, scene):
    """Create a new scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.create_scene(scene)
            click.echo(f"✓ Scene '{scene}' created")

            # Log to IF.witness
            log_obs_operation(instance, 'scene_create', {'scene': scene}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@scene.command('remove')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name to remove')
@click.confirmation_option(prompt='Are you sure you want to remove this scene?')
def scene_remove(instance, scene):
    """Remove a scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.remove_scene(scene)
            click.echo(f"✓ Scene '{scene}' removed")

            # Log to IF.witness
            log_obs_operation(instance, 'scene_remove', {'scene': scene}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@scene.command('current')
@click.argument('instance')
def scene_current(instance):
    """Get current scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            current = client.get_current_scene()
            click.echo(f"Current scene: {current}")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Source Management Commands
# ============================================================================

@obs.group()
def source():
    """Source management"""
    pass


@source.command('list')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def source_list(instance, scene, format):
    """List sources in a scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            sources = client.get_scene_items(scene)

            if format == 'json':
                click.echo(json.dumps([s.to_dict() for s in sources], indent=2))
            else:
                if not sources:
                    click.echo(f"No sources in scene '{scene}'")
                    return

                click.echo(f"\nSources in '{scene}' ({len(sources)})\n")
                click.echo(f"{'ID':<10} {'Name':<30} {'Type':<20} {'Visible':<10}")
                click.echo("-" * 70)

                for src in sources:
                    visible = "✓" if src.scene_item_enabled else "✗"
                    click.echo(f"{src.scene_item_id:<10} {src.name:<30} {src.type:<20} {visible:<10}")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@source.command('add')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name')
@click.option('--source', required=True, help='Source name')
@click.option('--type', required=True, help='Source type (camera, ndi, media, etc.)')
@click.option('--ndi-name', help='NDI source name (for NDI sources)')
def source_add(instance, scene, source, type, ndi_name):
    """Add source to scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        # Map common types to OBS input kinds
        type_mapping = {
            'camera': 'v4l2_input',  # Linux
            'webcam': 'v4l2_input',
            'ndi': 'ndi_source',
            'media': 'ffmpeg_source',
            'video': 'ffmpeg_source',
            'image': 'image_source',
            'browser': 'browser_source',
            'text': 'text_gdiplus',
            'color': 'color_source',
        }

        input_kind = type_mapping.get(type.lower(), type)
        settings = {}

        # Add NDI-specific settings
        if type.lower() == 'ndi' and ndi_name:
            settings['ndi_source_name'] = ndi_name

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.create_input(scene, source, input_kind, settings)
            click.echo(f"✓ Source '{source}' added to scene '{scene}'")

            # Log to IF.witness
            log_obs_operation(instance, 'source_add', {
                'scene': scene,
                'source': source,
                'type': type
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@source.command('show')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name')
@click.option('--source', required=True, help='Source name')
def source_show(instance, scene, source):
    """Show source in scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            # Get scene item ID
            sources = client.get_scene_items(scene)
            item = next((s for s in sources if s.name == source), None)

            if not item:
                click.echo(f"❌ Source '{source}' not found in scene '{scene}'", err=True)
                sys.exit(1)

            client.set_scene_item_enabled(scene, item.scene_item_id, True)
            click.echo(f"✓ Source '{source}' shown in scene '{scene}'")

            # Log to IF.witness
            log_obs_operation(instance, 'source_show', {
                'scene': scene,
                'source': source
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@source.command('hide')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name')
@click.option('--source', required=True, help='Source name')
def source_hide(instance, scene, source):
    """Hide source in scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            # Get scene item ID
            sources = client.get_scene_items(scene)
            item = next((s for s in sources if s.name == source), None)

            if not item:
                click.echo(f"❌ Source '{source}' not found in scene '{scene}'", err=True)
                sys.exit(1)

            client.set_scene_item_enabled(scene, item.scene_item_id, False)
            click.echo(f"✓ Source '{source}' hidden in scene '{scene}'")

            # Log to IF.witness
            log_obs_operation(instance, 'source_hide', {
                'scene': scene,
                'source': source
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@source.command('remove')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name')
@click.option('--source', required=True, help='Source name')
@click.confirmation_option(prompt='Are you sure you want to remove this source?')
def source_remove(instance, scene, source):
    """Remove source from scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.remove_input(source)
            click.echo(f"✓ Source '{source}' removed")

            # Log to IF.witness
            log_obs_operation(instance, 'source_remove', {
                'scene': scene,
                'source': source
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Streaming Commands
# ============================================================================

@obs.group()
def stream():
    """Streaming control"""
    pass


@stream.command('start')
@click.argument('instance')
def stream_start(instance):
    """Start streaming"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.start_stream()
            click.echo(f"✓ Streaming started")

            # Log to IF.witness
            log_obs_operation(instance, 'stream_start', {}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@stream.command('stop')
@click.argument('instance')
def stream_stop(instance):
    """Stop streaming"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.stop_stream()
            click.echo(f"✓ Streaming stopped")

            # Log to IF.witness
            log_obs_operation(instance, 'stream_stop', {}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@stream.command('status')
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def stream_status(instance, format):
    """Get streaming status"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            status = client.get_stream_status()

            if format == 'json':
                click.echo(json.dumps(status.to_dict(), indent=2))
            else:
                click.echo(f"\nStreaming Status")
                click.echo("-" * 40)
                click.echo(f"Active:      {status.active}")
                if status.active:
                    click.echo(f"Reconnecting: {status.reconnecting}")
                    if status.timecode:
                        click.echo(f"Timecode:    {status.timecode}")
                    if status.bytes_sent:
                        mb_sent = status.bytes_sent / (1024 * 1024)
                        click.echo(f"Data sent:   {mb_sent:.1f} MB")
                    if status.total_frames:
                        click.echo(f"Frames:      {status.total_frames}")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Recording Commands
# ============================================================================

@obs.group()
def record():
    """Recording control"""
    pass


@record.command('start')
@click.argument('instance')
@click.option('--file', 'filename', help='Output filename (optional)')
def record_start(instance, filename):
    """Start recording"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.start_record()

            if filename:
                click.echo(f"✓ Recording started: {filename}")
            else:
                click.echo(f"✓ Recording started")

            # Log to IF.witness
            log_obs_operation(instance, 'record_start', {
                'filename': filename
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@record.command('stop')
@click.argument('instance')
def record_stop(instance):
    """Stop recording"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.stop_record()
            click.echo(f"✓ Recording stopped")

            # Log to IF.witness
            log_obs_operation(instance, 'record_stop', {}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@record.command('status')
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def record_status(instance, format):
    """Get recording status"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            status = client.get_record_status()

            if format == 'json':
                click.echo(json.dumps(status.to_dict(), indent=2))
            else:
                click.echo(f"\nRecording Status")
                click.echo("-" * 40)
                click.echo(f"Active:  {status.active}")
                if status.active:
                    click.echo(f"Paused:  {status.paused}")
                    if status.timecode:
                        click.echo(f"Timecode: {status.timecode}")
                    if status.bytes:
                        mb = status.bytes / (1024 * 1024)
                        click.echo(f"Size:    {mb:.1f} MB")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Virtual Camera Commands
# ============================================================================

@obs.group()
def virtualcam():
    """Virtual camera control"""
    pass


@virtualcam.command('start')
@click.argument('instance')
def virtualcam_start(instance):
    """Start virtual camera"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.start_virtual_cam()
            click.echo(f"✓ Virtual camera started")

            # Log to IF.witness
            log_obs_operation(instance, 'virtualcam_start', {}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@virtualcam.command('stop')
@click.argument('instance')
def virtualcam_stop(instance):
    """Stop virtual camera"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.stop_virtual_cam()
            click.echo(f"✓ Virtual camera stopped")

            # Log to IF.witness
            log_obs_operation(instance, 'virtualcam_stop', {}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Filter Commands
# ============================================================================

@obs.group()
def filter():
    """Filter management"""
    pass


@filter.command('list')
@click.argument('instance')
@click.option('--source', required=True, help='Source name')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def filter_list(instance, source, format):
    """List filters on a source"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            filters = client.get_source_filters(source)

            if format == 'json':
                click.echo(json.dumps([f.to_dict() for f in filters], indent=2))
            else:
                if not filters:
                    click.echo(f"No filters on source '{source}'")
                    return

                click.echo(f"\nFilters on '{source}' ({len(filters)})\n")
                click.echo(f"{'Name':<30} {'Type':<30} {'Enabled':<10}")
                click.echo("-" * 70)

                for flt in filters:
                    enabled = "✓" if flt.enabled else "✗"
                    click.echo(f"{flt.name:<30} {flt.type:<30} {enabled:<10}")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@filter.command('add')
@click.argument('instance')
@click.option('--source', required=True, help='Source name')
@click.option('--filter', required=True, help='Filter name')
@click.option('--type', required=True, help='Filter type (chroma_key, color_correction, etc.)')
def filter_add(instance, source, filter, type):
    """Add filter to source"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        # Map common types to OBS filter kinds
        type_mapping = {
            'chroma_key': 'chroma_key_filter',
            'color_correction': 'color_filter',
            'sharpness': 'sharpness_filter',
            'lut': 'clut_filter',
            'noise_reduction': 'noise_suppress_filter',
            'gain': 'gain_filter',
        }

        filter_kind = type_mapping.get(type.lower(), type)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.create_source_filter(source, filter, filter_kind)
            click.echo(f"✓ Filter '{filter}' added to source '{source}'")

            # Log to IF.witness
            log_obs_operation(instance, 'filter_add', {
                'source': source,
                'filter': filter,
                'type': type
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@filter.command('remove')
@click.argument('instance')
@click.option('--source', required=True, help='Source name')
@click.option('--filter', required=True, help='Filter name')
@click.confirmation_option(prompt='Are you sure you want to remove this filter?')
def filter_remove(instance, source, filter):
    """Remove filter from source"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.remove_source_filter(source, filter)
            click.echo(f"✓ Filter '{filter}' removed from source '{source}'")

            # Log to IF.witness
            log_obs_operation(instance, 'filter_remove', {
                'source': source,
                'filter': filter
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Media Control Commands
# ============================================================================

@obs.group()
def media():
    """Media control"""
    pass


@media.command('add')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name')
@click.option('--source', required=True, help='Source name')
@click.option('--file', required=True, help='Media file path')
@click.option('--loop', is_flag=True, help='Loop media playback')
def media_add(instance, scene, source, file, loop):
    """Add media source to scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        settings = {
            'local_file': file,
            'looping': loop
        }

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.create_input(scene, source, 'ffmpeg_source', settings)
            click.echo(f"✓ Media source '{source}' added to scene '{scene}'")

            # Log to IF.witness
            log_obs_operation(instance, 'media_add', {
                'scene': scene,
                'source': source,
                'file': file,
                'loop': loop
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@media.command('play')
@click.argument('instance')
@click.option('--source', required=True, help='Media source name')
def media_play(instance, source):
    """Play media source"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.play_media(source)
            click.echo(f"✓ Playing media source '{source}'")

            # Log to IF.witness
            log_obs_operation(instance, 'media_play', {'source': source}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@media.command('pause')
@click.argument('instance')
@click.option('--source', required=True, help='Media source name')
def media_pause(instance, source):
    """Pause media source"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.pause_media(source)
            click.echo(f"✓ Paused media source '{source}'")

            # Log to IF.witness
            log_obs_operation(instance, 'media_pause', {'source': source}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@media.command('stop')
@click.argument('instance')
@click.option('--source', required=True, help='Media source name')
def media_stop(instance, source):
    """Stop media source"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.stop_media(source)
            click.echo(f"✓ Stopped media source '{source}'")

            # Log to IF.witness
            log_obs_operation(instance, 'media_stop', {'source': source}, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Browser Source Commands
# ============================================================================

@obs.group()
def browser():
    """Browser source management"""
    pass


@browser.command('add')
@click.argument('instance')
@click.option('--scene', required=True, help='Scene name')
@click.option('--source', required=True, help='Source name')
@click.option('--url', required=True, help='URL to load')
@click.option('--width', type=int, default=1920, help='Width in pixels (default: 1920)')
@click.option('--height', type=int, default=1080, help='Height in pixels (default: 1080)')
def browser_add(instance, scene, source, url, width, height):
    """Add browser source to scene"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        settings = {
            'url': url,
            'width': width,
            'height': height
        }

        with OBSClient(inst.host, inst.port, inst.password) as client:
            client.create_input(scene, source, 'browser_source', settings)
            click.echo(f"✓ Browser source '{source}' added to scene '{scene}'")
            click.echo(f"  URL: {url}")
            click.echo(f"  Size: {width}x{height}")

            # Log to IF.witness
            log_obs_operation(instance, 'browser_add', {
                'scene': scene,
                'source': source,
                'url': url,
                'width': width,
                'height': height
            }, {'success': True})

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Status & Stats Commands
# ============================================================================

@obs.command()
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def status(instance, format):
    """Get OBS status"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            version = client.get_version()
            scenes = client.get_scene_list()
            current_scene = client.get_current_scene()
            stream_status = client.get_stream_status()
            record_status = client.get_record_status()
            virtualcam_status = client.get_virtual_cam_status()

            if format == 'json':
                data = {
                    'version': version.to_dict(),
                    'scenes': [s.to_dict() for s in scenes],
                    'current_scene': current_scene,
                    'streaming': stream_status.to_dict(),
                    'recording': record_status.to_dict(),
                    'virtual_camera': virtualcam_status
                }
                click.echo(json.dumps(data, indent=2))
            else:
                click.echo(f"\nOBS Status: {inst.name}")
                click.echo("-" * 60)
                click.echo(f"OBS Version:     {version.obs_version}")
                click.echo(f"WebSocket:       {version.obs_web_socket_version}")
                click.echo(f"Scenes:          {len(scenes)}")
                click.echo(f"Current Scene:   {current_scene}")
                click.echo(f"Streaming:       {stream_status.active}")
                click.echo(f"Recording:       {record_status.active}")
                click.echo(f"Virtual Camera:  {virtualcam_status}")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@obs.command()
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def stats(instance, format):
    """Get performance statistics"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            stats = client.get_stats()

            if format == 'json':
                click.echo(json.dumps(stats.to_dict(), indent=2))
            else:
                click.echo(f"\nOBS Performance Statistics")
                click.echo("-" * 60)
                click.echo(f"\nSystem Resources:")
                click.echo(f"  CPU Usage:        {stats.cpu_usage:.1f}%")
                click.echo(f"  Memory Usage:     {stats.memory_usage:.1f} MB")
                click.echo(f"  Disk Space:       {stats.available_disk_space:.1f} MB")

                click.echo(f"\nRendering:")
                click.echo(f"  FPS:              {stats.active_fps:.2f}")
                click.echo(f"  Render Time:      {stats.average_frame_render_time:.2f} ms")
                click.echo(f"  Total Frames:     {stats.render_total_frames}")
                click.echo(f"  Skipped Frames:   {stats.render_skipped_frames}")

                if stats.render_total_frames > 0:
                    skip_pct = (stats.render_skipped_frames / stats.render_total_frames) * 100
                    click.echo(f"  Skip Rate:        {skip_pct:.2f}%")

                click.echo(f"\nOutput:")
                click.echo(f"  Total Frames:     {stats.output_total_frames}")
                click.echo(f"  Skipped Frames:   {stats.output_skipped_frames}")

                if stats.output_total_frames > 0:
                    skip_pct = (stats.output_skipped_frames / stats.output_total_frames) * 100
                    click.echo(f"  Skip Rate:        {skip_pct:.2f}%")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@obs.command()
@click.argument('instance')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def version(instance, format):
    """Get version information"""
    try:
        config = OBSConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        with OBSClient(inst.host, inst.port, inst.password) as client:
            version = client.get_version()

            if format == 'json':
                click.echo(json.dumps(version.to_dict(), indent=2))
            else:
                click.echo(f"\nOBS Version Information")
                click.echo("-" * 60)
                click.echo(f"OBS Studio:      {version.obs_version}")
                click.echo(f"WebSocket:       {version.obs_web_socket_version}")
                click.echo(f"RPC Version:     {version.rpc_version}")
                if version.platform:
                    click.echo(f"Platform:        {version.platform}")
                if version.platform_description:
                    click.echo(f"Description:     {version.platform_description}")

    except OBSError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    obs()
