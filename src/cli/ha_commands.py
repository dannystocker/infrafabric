#!/usr/bin/env python3
"""
IF.ha CLI - Home Assistant Control

Commands:
  Connection Management:
    add       - Add Home Assistant instance
    list      - List HA instances
    test      - Test connection to HA
    remove    - Remove HA instance

  Entity Control:
    entities  - List entities (with domain filter)
    state     - Get entity state
    set       - Set entity state/attributes

  Services:
    service   - Call HA service

  Cameras:
    camera    - Camera control (list, stream, snapshot)

  Automations:
    automation - Automation control (list, trigger, enable, disable)

  Scripts:
    script    - Script control (list, run)

  Scenes:
    scene     - Scene control (list, activate)

  Notifications:
    notify    - Send notification

  Media Players:
    media     - Media player control (list, play, pause, stop)
    tts       - Text-to-speech

  Events:
    event     - Event control (fire, list)

  Status & Info:
    status    - Get HA status
    info      - Get HA info (version, uptime, components)
    config    - Show HA configuration

Philosophy: Dead-simple CLI for home automation.
Every operation logged to IF.witness for audit trails.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from uuid import uuid4

import click

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from homeassistant.client import HomeAssistantClient, HAError, HAConnectionError, HAAuthError
from homeassistant.config import HAConfig, HAConfigError
from witness.database import WitnessDatabase


def log_ha_operation(instance_name: str, operation: str, params: dict, result: dict):
    """Log Home Assistant operation to IF.witness"""
    try:
        db = WitnessDatabase()
        db.create_entry(
            event=f"ha_{operation}",
            component="IF.homeassistant",
            trace_id=f"ha-{instance_name}-{uuid4()}",
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
def ha():
    """Home Assistant control"""
    pass


# ============================================================================
# Connection Management Commands
# ============================================================================

@ha.command()
@click.argument('name')
@click.option('--url', required=True, help='Home Assistant URL (e.g., http://homeassistant.local:8123)')
@click.option('--token', required=True, help='Long-lived access token')
def add(name, url, token):
    """Add Home Assistant instance"""
    try:
        config = HAConfig()

        # Add to config
        instance = config.add_instance(name, url, token)

        # Test connection
        click.echo(f"Testing connection to {url}...")
        client = HomeAssistantClient(url, token)

        try:
            ha_config = client.get_config()
            click.echo(f"✓ Connected to Home Assistant {ha_config.version}")
            click.echo(f"  Location: {ha_config.location_name}")
            click.echo(f"  Components: {len(ha_config.components)}")
            click.echo(f"✓ Instance '{name}' added successfully")

            # Log to IF.witness
            log_ha_operation(name, 'add_instance', {
                'url': url
            }, {
                'success': True,
                'version': ha_config.version,
                'location': ha_config.location_name
            })

        except (HAConnectionError, HAAuthError) as e:
            click.echo(f"⚠️  Warning: Could not connect to Home Assistant: {e}", err=True)
            click.echo(f"   Instance '{name}' added but connection failed")

    except HAConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def list(format):
    """List Home Assistant instances"""
    try:
        config = HAConfig()
        instances = config.list_instances()

        if not instances:
            click.echo("No Home Assistant instances configured")
            click.echo("\nAdd an instance with: if-ha add <name> --url <url> --token <token>")
            return

        if format == 'json':
            click.echo(json.dumps([inst.to_dict() for inst in instances], indent=2))
        else:
            click.echo(f"\nConfigured Home Assistant Instances ({len(instances)})\n")
            click.echo(f"{'Name':<20} {'URL':<40} {'Added':<25}")
            click.echo("-" * 85)

            for inst in instances:
                added_date = inst.added_at[:19] if inst.added_at else 'unknown'
                click.echo(f"{inst.name:<20} {inst.url:<40} {added_date:<25}")

    except HAConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.argument('instance')
def test(instance):
    """Test connection to Home Assistant instance"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        click.echo(f"Testing connection to {inst.url}...")

        client = HomeAssistantClient(inst.url, inst.token)
        ha_config = client.get_config()

        click.echo(f"✓ Connection successful")
        click.echo(f"  Version: {ha_config.version}")
        click.echo(f"  Location: {ha_config.location_name}")
        click.echo(f"  Time Zone: {ha_config.time_zone}")
        click.echo(f"  Components: {len(ha_config.components)}")

        # Get entity count
        entities = client.get_states()
        click.echo(f"  Entities: {len(entities)}")

        # Log to IF.witness
        log_ha_operation(instance, 'test_connection', {}, {
            'success': True,
            'version': ha_config.version
        })

    except (HAConnectionError, HAAuthError) as e:
        click.echo(f"❌ Connection failed: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.argument('instance')
@click.confirmation_option(prompt='Are you sure you want to remove this instance?')
def remove(instance):
    """Remove Home Assistant instance"""
    try:
        config = HAConfig()

        if config.remove_instance(instance):
            click.echo(f"✓ Instance '{instance}' removed")

            # Log to IF.witness
            log_ha_operation(instance, 'remove_instance', {}, {'success': True})
        else:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

    except HAConfigError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Entity Control Commands
# ============================================================================

@ha.command()
@click.argument('instance')
@click.option('--domain', help='Filter by domain (e.g., light, switch, sensor)')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def entities(instance, domain, output_json):
    """List entities"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        entity_list = client.get_states(domain)

        if output_json:
            click.echo(json.dumps([e.to_dict() for e in entity_list], indent=2))
        else:
            if not entity_list:
                click.echo(f"No entities found" + (f" for domain '{domain}'" if domain else ""))
                return

            domain_str = f" ({domain})" if domain else ""
            click.echo(f"\nEntities{domain_str} ({len(entity_list)})\n")
            click.echo(f"{'Entity ID':<40} {'State':<15} {'Name':<30}")
            click.echo("-" * 85)

            for entity in entity_list:
                click.echo(f"{entity.entity_id:<40} {entity.state:<15} {entity.name:<30}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.argument('instance')
@click.argument('entity_id')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def state(instance, entity_id, output_json):
    """Get entity state"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        entity = client.get_state(entity_id)

        if output_json:
            click.echo(json.dumps(entity.to_dict(), indent=2))
        else:
            click.echo(f"\nEntity: {entity.entity_id}")
            click.echo(f"Name: {entity.name}")
            click.echo(f"State: {entity.state}")
            click.echo(f"\nAttributes:")
            for key, value in entity.attributes.items():
                click.echo(f"  {key}: {value}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.argument('instance')
@click.argument('entity_id')
@click.option('--state', required=True, help='New state value')
@click.option('--brightness', type=int, help='Brightness (0-255, for lights)')
@click.option('--temperature', type=float, help='Temperature (for climate)')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def set(instance, entity_id, state, brightness, temperature, output_json):
    """Set entity state (uses appropriate service call)"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        domain = entity_id.split('.')[0]

        # Build service data
        service_data = {'entity_id': entity_id}

        # Determine service based on state and domain
        if state.lower() in ['on', 'off']:
            service = f'turn_{state.lower()}'

            # Add additional parameters
            if brightness is not None:
                service_data['brightness'] = brightness
            if temperature is not None:
                service_data['temperature'] = temperature

            result = client.call_service(domain, service, service_data)
        else:
            # For other states, use set_state (note: this doesn't control devices)
            result = client.set_state(entity_id, state)

        if output_json:
            click.echo(json.dumps(result if isinstance(result, dict) else result.to_dict(), indent=2))
        else:
            click.echo(f"✓ Entity {entity_id} set to {state}")
            if brightness:
                click.echo(f"  Brightness: {brightness}")
            if temperature:
                click.echo(f"  Temperature: {temperature}")

        # Log to IF.witness
        log_ha_operation(instance, 'set_entity', {
            'entity_id': entity_id,
            'state': state,
            'brightness': brightness,
            'temperature': temperature
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Service Commands
# ============================================================================

@ha.command()
@click.argument('instance')
@click.argument('service_call')  # Format: domain.service (e.g., light.turn_on)
@click.option('--entity', 'entity_id', help='Entity ID')
@click.option('--brightness', type=int, help='Brightness (0-255)')
@click.option('--temperature', type=float, help='Temperature')
@click.option('--data', help='Additional service data as JSON')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def service(instance, service_call, entity_id, brightness, temperature, data, output_json):
    """Call Home Assistant service"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        # Parse service call
        if '.' not in service_call:
            click.echo(f"❌ Service must be in format 'domain.service' (e.g., light.turn_on)", err=True)
            sys.exit(1)

        domain, service_name = service_call.split('.', 1)

        # Build service data
        service_data = {}
        if entity_id:
            service_data['entity_id'] = entity_id
        if brightness is not None:
            service_data['brightness'] = brightness
        if temperature is not None:
            service_data['temperature'] = temperature
        if data:
            try:
                additional_data = json.loads(data)
                service_data.update(additional_data)
            except json.JSONDecodeError as e:
                click.echo(f"❌ Invalid JSON in --data: {e}", err=True)
                sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        result = client.call_service(domain, service_name, service_data)

        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"✓ Service {service_call} called successfully")
            if entity_id:
                click.echo(f"  Entity: {entity_id}")

        # Log to IF.witness
        log_ha_operation(instance, 'call_service', {
            'service': service_call,
            'entity_id': entity_id,
            'data': service_data
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Camera Commands
# ============================================================================

@ha.group()
def camera():
    """Camera control"""
    pass


@camera.command('list')
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def camera_list(instance, output_json):
    """List cameras"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        cameras = client.get_cameras()

        if output_json:
            click.echo(json.dumps([c.to_dict() for c in cameras], indent=2))
        else:
            if not cameras:
                click.echo("No cameras found")
                return

            click.echo(f"\nCameras ({len(cameras)})\n")
            click.echo(f"{'Entity ID':<40} {'Name':<30} {'State':<10}")
            click.echo("-" * 80)

            for cam in cameras:
                click.echo(f"{cam.entity_id:<40} {cam.name:<30} {cam.state:<10}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@camera.command('snapshot')
@click.argument('instance')
@click.argument('entity_id')
@click.option('--file', 'output_file', required=True, help='Output file path')
def camera_snapshot(instance, entity_id, output_file):
    """Get camera snapshot"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        click.echo(f"Capturing snapshot from {entity_id}...")

        snapshot_data = client.get_camera_snapshot(entity_id)

        # Save to file
        with open(output_file, 'wb') as f:
            f.write(snapshot_data)

        click.echo(f"✓ Snapshot saved to {output_file}")

        # Log to IF.witness
        log_ha_operation(instance, 'camera_snapshot', {
            'entity_id': entity_id,
            'file': output_file
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@camera.command('stream')
@click.argument('instance')
@click.argument('entity_id')
@click.option('--ndi', 'ndi_name', required=True, help='NDI output name')
def camera_stream(instance, entity_id, ndi_name):
    """Stream camera to NDI"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        click.echo(f"Getting stream source for {entity_id}...")

        # Get stream source URL
        stream_url = client.get_camera_stream_source(entity_id)

        if not stream_url:
            click.echo(f"❌ Could not get stream source for {entity_id}", err=True)
            click.echo(f"   Camera may not support streaming", err=True)
            sys.exit(1)

        click.echo(f"Stream source: {stream_url}")
        click.echo(f"Starting NDI bridge: {ndi_name}...")

        # Start ffmpeg NDI bridge
        cmd = [
            'ffmpeg',
            '-i', stream_url,
            '-f', 'libndi_newtek',
            '-pix_fmt', 'uyvy422',
            f'ndi_name={ndi_name}'
        ]

        click.echo(f"Command: {' '.join(cmd)}")
        click.echo(f"\nStarting stream... (press Ctrl+C to stop)")

        # Run ffmpeg in foreground
        subprocess.run(cmd)

        # Log to IF.witness
        log_ha_operation(instance, 'camera_stream', {
            'entity_id': entity_id,
            'ndi_name': ndi_name,
            'stream_url': stream_url
        }, {'success': True})

    except KeyboardInterrupt:
        click.echo("\n✓ Stream stopped")
    except FileNotFoundError:
        click.echo(f"❌ Error: ffmpeg not found. Please install ffmpeg with NDI support.", err=True)
        sys.exit(1)
    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Automation Commands
# ============================================================================

@ha.group()
def automation():
    """Automation control"""
    pass


@automation.command('list')
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def automation_list(instance, output_json):
    """List automations"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        automations = client.get_automations()

        if output_json:
            click.echo(json.dumps([a.to_dict() for a in automations], indent=2))
        else:
            if not automations:
                click.echo("No automations found")
                return

            click.echo(f"\nAutomations ({len(automations)})\n")
            click.echo(f"{'Entity ID':<40} {'Name':<30} {'State':<10}")
            click.echo("-" * 80)

            for auto in automations:
                click.echo(f"{auto.entity_id:<40} {auto.name:<30} {auto.state:<10}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@automation.command('trigger')
@click.argument('instance')
@click.argument('entity_id')
def automation_trigger(instance, entity_id):
    """Trigger automation"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.trigger_automation(entity_id)

        click.echo(f"✓ Automation {entity_id} triggered")

        # Log to IF.witness
        log_ha_operation(instance, 'automation_trigger', {
            'entity_id': entity_id
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@automation.command('enable')
@click.argument('instance')
@click.argument('entity_id')
def automation_enable(instance, entity_id):
    """Enable automation"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.enable_automation(entity_id)

        click.echo(f"✓ Automation {entity_id} enabled")

        # Log to IF.witness
        log_ha_operation(instance, 'automation_enable', {
            'entity_id': entity_id
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@automation.command('disable')
@click.argument('instance')
@click.argument('entity_id')
def automation_disable(instance, entity_id):
    """Disable automation"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.disable_automation(entity_id)

        click.echo(f"✓ Automation {entity_id} disabled")

        # Log to IF.witness
        log_ha_operation(instance, 'automation_disable', {
            'entity_id': entity_id
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Script Commands
# ============================================================================

@ha.group()
def script():
    """Script control"""
    pass


@script.command('list')
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def script_list(instance, output_json):
    """List scripts"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        scripts = client.get_scripts()

        if output_json:
            click.echo(json.dumps([s.to_dict() for s in scripts], indent=2))
        else:
            if not scripts:
                click.echo("No scripts found")
                return

            click.echo(f"\nScripts ({len(scripts)})\n")
            click.echo(f"{'Entity ID':<40} {'Name':<40}")
            click.echo("-" * 80)

            for scr in scripts:
                click.echo(f"{scr.entity_id:<40} {scr.name:<40}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@script.command('run')
@click.argument('instance')
@click.argument('entity_id')
@click.option('--variables', help='Script variables as JSON')
def script_run(instance, entity_id, variables):
    """Run script"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        # Parse variables
        vars_dict = None
        if variables:
            try:
                vars_dict = json.loads(variables)
            except json.JSONDecodeError as e:
                click.echo(f"❌ Invalid JSON in --variables: {e}", err=True)
                sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.run_script(entity_id, vars_dict)

        click.echo(f"✓ Script {entity_id} executed")
        if vars_dict:
            click.echo(f"  Variables: {vars_dict}")

        # Log to IF.witness
        log_ha_operation(instance, 'script_run', {
            'entity_id': entity_id,
            'variables': vars_dict
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Scene Commands
# ============================================================================

@ha.group()
def scene():
    """Scene control"""
    pass


@scene.command('list')
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def scene_list(instance, output_json):
    """List scenes"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        scenes = client.get_scenes()

        if output_json:
            click.echo(json.dumps([s.to_dict() for s in scenes], indent=2))
        else:
            if not scenes:
                click.echo("No scenes found")
                return

            click.echo(f"\nScenes ({len(scenes)})\n")
            click.echo(f"{'Entity ID':<40} {'Name':<40}")
            click.echo("-" * 80)

            for scn in scenes:
                click.echo(f"{scn.entity_id:<40} {scn.name:<40}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@scene.command('activate')
@click.argument('instance')
@click.argument('entity_id')
def scene_activate(instance, entity_id):
    """Activate scene"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.activate_scene(entity_id)

        click.echo(f"✓ Scene {entity_id} activated")

        # Log to IF.witness
        log_ha_operation(instance, 'scene_activate', {
            'entity_id': entity_id
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Notification Commands
# ============================================================================

@ha.command()
@click.argument('instance')
@click.option('--message', required=True, help='Notification message')
@click.option('--title', help='Notification title')
@click.option('--service', default='persistent_notification', help='Notification service')
def notify(instance, message, title, service):
    """Send notification"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.send_notification(message, title, service)

        click.echo(f"✓ Notification sent")
        if title:
            click.echo(f"  Title: {title}")
        click.echo(f"  Message: {message}")

        # Log to IF.witness
        log_ha_operation(instance, 'notify', {
            'message': message,
            'title': title,
            'service': service
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Media Player Commands
# ============================================================================

@ha.group()
def media():
    """Media player control"""
    pass


@media.command('list')
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def media_list(instance, output_json):
    """List media players"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        players = client.get_media_players()

        if output_json:
            click.echo(json.dumps([p.to_dict() for p in players], indent=2))
        else:
            if not players:
                click.echo("No media players found")
                return

            click.echo(f"\nMedia Players ({len(players)})\n")
            click.echo(f"{'Entity ID':<40} {'Name':<25} {'State':<10}")
            click.echo("-" * 75)

            for player in players:
                click.echo(f"{player.entity_id:<40} {player.name:<25} {player.state:<10}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@media.command('play')
@click.argument('instance')
@click.argument('entity_id')
@click.option('--url', 'media_url', help='Media URL to play')
def media_play(instance, entity_id, media_url):
    """Play media"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)

        if media_url:
            client.media_play_url(entity_id, media_url)
            click.echo(f"✓ Playing {media_url} on {entity_id}")
        else:
            client.media_play(entity_id)
            click.echo(f"✓ Resumed playback on {entity_id}")

        # Log to IF.witness
        log_ha_operation(instance, 'media_play', {
            'entity_id': entity_id,
            'url': media_url
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@media.command('pause')
@click.argument('instance')
@click.argument('entity_id')
def media_pause(instance, entity_id):
    """Pause media"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.media_pause(entity_id)

        click.echo(f"✓ Paused {entity_id}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@media.command('stop')
@click.argument('instance')
@click.argument('entity_id')
def media_stop(instance, entity_id):
    """Stop media"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.media_stop(entity_id)

        click.echo(f"✓ Stopped {entity_id}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.argument('instance')
@click.argument('entity_id')
@click.option('--message', required=True, help='Text to speak')
@click.option('--language', default='en', help='Language code (default: en)')
def tts(instance, entity_id, message, language):
    """Text-to-speech"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        client.tts_speak(entity_id, message, language)

        click.echo(f"✓ Speaking on {entity_id}: {message}")

        # Log to IF.witness
        log_ha_operation(instance, 'tts', {
            'entity_id': entity_id,
            'message': message,
            'language': language
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Event Commands
# ============================================================================

@ha.group()
def event():
    """Event control"""
    pass


@event.command('fire')
@click.argument('instance')
@click.argument('event_type')
@click.option('--data', help='Event data as JSON')
def event_fire(instance, event_type, data):
    """Fire event"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        # Parse data
        event_data = None
        if data:
            try:
                event_data = json.loads(data)
            except json.JSONDecodeError as e:
                click.echo(f"❌ Invalid JSON in --data: {e}", err=True)
                sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        result = client.fire_event(event_type, event_data)

        click.echo(f"✓ Event '{event_type}' fired")
        if event_data:
            click.echo(f"  Data: {event_data}")

        # Log to IF.witness
        log_ha_operation(instance, 'event_fire', {
            'event_type': event_type,
            'data': event_data
        }, {'success': True})

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@event.command('list')
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def event_list(instance, output_json):
    """List event types"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        events = client.get_events()

        if output_json:
            click.echo(json.dumps(events, indent=2))
        else:
            if not events:
                click.echo("No events found")
                return

            click.echo(f"\nEvent Types ({len(events)})\n")
            for evt in events:
                if isinstance(evt, dict):
                    click.echo(f"  {evt.get('event', evt)}")
                else:
                    click.echo(f"  {evt}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Status & Info Commands
# ============================================================================

@ha.command()
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def status(instance, output_json):
    """Get Home Assistant status"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        status_data = client.get_status()

        if output_json:
            click.echo(json.dumps(status_data, indent=2))
        else:
            click.echo(f"\nHome Assistant Status: {inst.name}")
            click.echo("-" * 50)
            click.echo(f"Message: {status_data.get('message', 'API running')}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def info(instance, output_json):
    """Get Home Assistant info"""
    try:
        config = HAConfig()
        inst = config.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        ha_config = client.get_config()

        if output_json:
            click.echo(json.dumps(ha_config.to_dict(), indent=2))
        else:
            click.echo(f"\nHome Assistant Info: {inst.name}")
            click.echo("-" * 50)
            click.echo(f"Version: {ha_config.version}")
            click.echo(f"Location: {ha_config.location_name}")
            click.echo(f"Time Zone: {ha_config.time_zone}")
            click.echo(f"Unit System: {ha_config.unit_system}")
            click.echo(f"Components: {len(ha_config.components)}")

            # Get entity count
            entities = client.get_states()
            click.echo(f"Entities: {len(entities)}")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@ha.command()
@click.argument('instance')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def config(instance, output_json):
    """Show Home Assistant configuration"""
    try:
        config_mgr = HAConfig()
        inst = config_mgr.get_instance(instance)

        if not inst:
            click.echo(f"❌ Instance '{instance}' not found", err=True)
            sys.exit(1)

        client = HomeAssistantClient(inst.url, inst.token)
        ha_config = client.get_config()

        if output_json:
            click.echo(json.dumps(ha_config.to_dict(), indent=2))
        else:
            click.echo(f"\nHome Assistant Configuration: {inst.name}")
            click.echo("-" * 50)
            click.echo(f"Version: {ha_config.version}")
            click.echo(f"Location: {ha_config.location_name}")
            click.echo(f"Latitude: {ha_config.latitude}")
            click.echo(f"Longitude: {ha_config.longitude}")
            click.echo(f"Elevation: {ha_config.elevation}")
            click.echo(f"Time Zone: {ha_config.time_zone}")
            click.echo(f"Unit System: {ha_config.unit_system}")
            click.echo(f"\nComponents ({len(ha_config.components)}):")

            # Show first 20 components
            for comp in sorted(ha_config.components)[:20]:
                click.echo(f"  - {comp}")

            if len(ha_config.components) > 20:
                click.echo(f"  ... and {len(ha_config.components) - 20} more")

    except HAError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    ha()
