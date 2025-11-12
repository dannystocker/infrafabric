# Home Assistant Integration for InfraFabric

Complete CLI interface for Home Assistant control with IF.witness audit logging.

## Features

- **11 Command Groups**: Full control of Home Assistant
- **IF.witness Integration**: All operations logged for audit trails
- **Multiple Instances**: Manage multiple Home Assistant installations
- **JSON Output**: Machine-readable output for scripting
- **Camera→NDI Bridge**: Stream cameras to NDI for production workflows
- **Bash Completion**: Tab completion for all commands
- **Production Ready**: Built for reliability and performance

## Quick Start

```bash
# Add your Home Assistant instance
if-ha add myhome \
  --url http://homeassistant.local:8123 \
  --token eyJ0eXAiOiJKV1Qi...

# Test connection
if-ha test myhome

# List entities
if-ha entities myhome --domain light

# Control devices
if-ha set myhome light.living_room --state on --brightness 200
```

## Command Groups

### 1. Connection Management
- `if-ha add` - Add Home Assistant instance
- `if-ha list` - List configured instances
- `if-ha test` - Test connection
- `if-ha remove` - Remove instance

### 2. Entity Control
- `if-ha entities` - List entities with domain filter
- `if-ha state` - Get entity state
- `if-ha set` - Set entity state/attributes

### 3. Services
- `if-ha service` - Call any Home Assistant service

### 4. Cameras
- `if-ha camera list` - List cameras
- `if-ha camera snapshot` - Capture snapshot
- `if-ha camera stream` - Stream to NDI

### 5. Automations
- `if-ha automation list` - List automations
- `if-ha automation trigger` - Trigger automation
- `if-ha automation enable/disable` - Enable/disable automation

### 6. Scripts
- `if-ha script list` - List scripts
- `if-ha script run` - Run script with variables

### 7. Scenes
- `if-ha scene list` - List scenes
- `if-ha scene activate` - Activate scene

### 8. Notifications
- `if-ha notify` - Send notification

### 9. Media Players
- `if-ha media list` - List media players
- `if-ha media play/pause/stop` - Control playback
- `if-ha tts` - Text-to-speech

### 10. Events
- `if-ha event fire` - Fire custom event
- `if-ha event list` - List event types

### 11. Status & Info
- `if-ha status` - Get HA status
- `if-ha info` - Get system info
- `if-ha config` - Show configuration

## Documentation

- [CLI Interface Guide](./cli-interface.md) - Complete user guide
- [Home Assistant API](https://developers.home-assistant.io/docs/api/rest/) - Official API docs

## Installation

```bash
# Install InfraFabric
pip install -e .

# Enable bash completion (optional)
source completions/ha-completion.bash

# Or add to ~/.bashrc
echo 'source /path/to/infrafabric/completions/ha-completion.bash' >> ~/.bashrc
```

## Requirements

- Python 3.10+
- Home Assistant with REST API enabled
- Long-lived access token
- (Optional) ffmpeg with NDI support for camera streaming

## Architecture

```
src/homeassistant/
├── __init__.py         # Module init
├── client.py           # REST API client
├── config.py           # Configuration management
└── models.py           # Data models

src/cli/
└── ha_commands.py      # CLI interface

tests/
└── test_ha_cli.py      # Unit tests

docs/HOME-ASSISTANT/
├── README.md           # This file
└── cli-interface.md    # User guide

completions/
└── ha-completion.bash  # Bash completion
```

## Configuration Storage

Configurations are stored at:
```
~/.if/home-assistant/instances.yaml
```

Format:
```yaml
instances:
  myhome:
    url: http://homeassistant.local:8123
    token: eyJ0eXAiOiJKV1Qi...
    added_at: 2025-11-12T00:00:00Z
```

## IF.witness Integration

All operations are automatically logged to IF.witness:

```bash
# View logs
if-witness list --component IF.homeassistant

# Export compliance report
if-witness export ha-audit.pdf \
  --component IF.homeassistant \
  --days 30
```

## Testing

```bash
# Run tests
pytest tests/test_ha_cli.py -v

# Run with coverage
pytest tests/test_ha_cli.py --cov=homeassistant --cov-report=html
```

## Examples

### Morning Routine Script
```bash
#!/bin/bash
INSTANCE="myhome"

if-ha set $INSTANCE light.bedroom --state on --brightness 100
if-ha set $INSTANCE switch.coffee_maker --state on
if-ha tts $INSTANCE media_player.kitchen --message "Good morning!"
if-ha automation trigger $INSTANCE automation.morning_routine
```

### Security Check
```bash
#!/bin/bash
INSTANCE="myhome"

# Check all locks
if-ha entities $INSTANCE --domain lock --json | \
  jq -r '.[] | select(.state == "unlocked") | .entity_id'
```

### Camera→vMix Pipeline
```bash
# Stream HA camera to NDI
if-ha camera stream myhome camera.front_door --ndi "Front Door"

# Add to vMix
if vmix ndi add myvmix --source "Front Door"
```

## Troubleshooting

### Connection Issues
```bash
# Test direct API access
curl -H "Authorization: Bearer TOKEN" \
  http://homeassistant.local:8123/api/
```

### Get Long-Lived Token
1. Log into Home Assistant
2. Click profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Create token and copy it

### Camera Streaming
- Requires ffmpeg with NDI plugin
- Camera must support RTSP/HTTP streaming
- Check network connectivity

## Performance

- Synchronous HTTP client for reliability
- Single request per operation
- Configurable timeouts (default: 10s)
- Efficient YAML config parsing

## Security

- Tokens stored in `~/.if/home-assistant/instances.yaml`
- File permissions: 600 (user read/write only)
- Tokens masked in logs and output
- All operations audited via IF.witness

## Integration Examples

### With vMix
```bash
# Stream camera to vMix
if-ha camera stream myhome camera.front --ndi "Front Camera"
if vmix ndi add studio --source "Front Camera"
```

### With Cron
```bash
# Turn off lights at midnight
0 0 * * * if-ha set myhome light.all --state off

# Morning routine at 7am
0 7 * * 1-5 if-ha automation trigger myhome automation.morning
```

### With Bash Scripts
```bash
# Check if anyone is home
if if-ha state myhome person.john --json | jq -e '.state == "home"'; then
  echo "John is home"
  if-ha set myhome light.entrance --state on
fi
```

## Support

- GitHub: https://github.com/infrafabric/infrafabric
- Documentation: https://docs.infrafabric.io
- Issues: https://github.com/infrafabric/infrafabric/issues

## License

Part of InfraFabric - Open source infrastructure automation toolkit.

## Contributing

Contributions welcome! See main repository for guidelines.

## Changelog

### 1.0.0 (2025-11-12)
- Initial release
- Complete CLI with 11 command groups
- IF.witness integration
- Camera→NDI bridge
- Bash completion
- Comprehensive documentation
