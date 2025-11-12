# Home Assistant CLI Interface

**IF.ha** - Dead-simple CLI for Home Assistant control with IF.witness audit logging.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Connection Management](#connection-management)
4. [Entity Control](#entity-control)
5. [Services](#services)
6. [Cameras](#cameras)
7. [Automations](#automations)
8. [Scripts](#scripts)
9. [Scenes](#scenes)
10. [Notifications](#notifications)
11. [Media Players](#media-players)
12. [Events](#events)
13. [Status & Info](#status--info)
14. [Advanced Usage](#advanced-usage)

---

## Installation

```bash
# Install InfraFabric with Home Assistant support
pip install -e .

# Verify installation
if-ha --help
```

### Requirements

- Python 3.10+
- Home Assistant instance with REST API enabled
- Long-lived access token from Home Assistant
- (Optional) ffmpeg with NDI support for camera streaming

---

## Quick Start

### 1. Get Long-Lived Access Token

1. Log into Home Assistant web interface
2. Click your profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name (e.g., "InfraFabric CLI")
6. Copy the token (starts with `eyJ0eXAi...`)

### 2. Add Your Home Assistant Instance

```bash
if-ha add myhome \
  --url http://homeassistant.local:8123 \
  --token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Test Connection

```bash
if-ha test myhome
```

### 4. List Entities

```bash
if-ha entities myhome --domain light
```

### 5. Control a Device

```bash
if-ha set myhome light.living_room --state on --brightness 200
```

---

## Connection Management

### Add Instance

```bash
if-ha add <name> --url <url> --token <token>
```

**Example:**
```bash
if-ha add myhome \
  --url http://192.168.1.100:8123 \
  --token eyJ0eXAiOiJKV1QiLCJhbGciOi...
```

### List Instances

```bash
if-ha list
if-ha list --format json
```

**Output:**
```
Configured Home Assistant Instances (2)

Name                 URL                                      Added
-------------------------------------------------------------------------------------
myhome               http://homeassistant.local:8123          2025-11-12T00:00:00
remote               https://ha.example.com                   2025-11-11T22:00:00
```

### Test Connection

```bash
if-ha test myhome
```

**Output:**
```
Testing connection to http://homeassistant.local:8123...
✓ Connection successful
  Version: 2024.11.0
  Location: Home
  Time Zone: America/New_York
  Components: 157
  Entities: 342
```

### Remove Instance

```bash
if-ha remove myhome
```

---

## Entity Control

### List Entities

```bash
# All entities
if-ha entities myhome

# Filter by domain
if-ha entities myhome --domain light
if-ha entities myhome --domain switch
if-ha entities myhome --domain sensor

# JSON output
if-ha entities myhome --domain light --json
```

**Output:**
```
Entities (light) (12)

Entity ID                                State           Name
-------------------------------------------------------------------------------------
light.living_room                        on              Living Room Light
light.bedroom                            off             Bedroom Light
light.kitchen                            on              Kitchen Light
```

### Get Entity State

```bash
if-ha state myhome light.living_room
if-ha state myhome climate.thermostat --json
```

**Output:**
```
Entity: light.living_room
Name: Living Room Light
State: on

Attributes:
  brightness: 255
  color_mode: brightness
  supported_color_modes: ['brightness']
  friendly_name: Living Room Light
```

### Set Entity State

```bash
# Turn on/off
if-ha set myhome light.living_room --state on
if-ha set myhome switch.coffee_maker --state off

# With brightness (lights)
if-ha set myhome light.bedroom --state on --brightness 128

# With temperature (climate)
if-ha set myhome climate.thermostat --state heat --temperature 72
```

---

## Services

### Call Any Service

```bash
if-ha service myhome <domain>.<service> --entity <entity_id> [options]
```

**Examples:**

```bash
# Turn on light with brightness
if-ha service myhome light.turn_on \
  --entity light.living_room \
  --brightness 200

# Toggle switch
if-ha service myhome switch.toggle \
  --entity switch.coffee_maker

# Set climate temperature
if-ha service myhome climate.set_temperature \
  --entity climate.thermostat \
  --temperature 72

# With custom data
if-ha service myhome light.turn_on \
  --entity light.bedroom \
  --data '{"color_name": "blue", "brightness": 150}'
```

---

## Cameras

### List Cameras

```bash
if-ha camera list myhome
if-ha camera list myhome --json
```

**Output:**
```
Cameras (3)

Entity ID                                Name                           State
--------------------------------------------------------------------------------
camera.front_door                        Front Door Camera              idle
camera.backyard                          Backyard Camera                streaming
camera.garage                            Garage Camera                  idle
```

### Get Snapshot

```bash
if-ha camera snapshot myhome camera.front_door --file snapshot.jpg
```

**Output:**
```
Capturing snapshot from camera.front_door...
✓ Snapshot saved to snapshot.jpg
```

### Stream to NDI

Stream camera to NDI for use in vMix, OBS, or other production software:

```bash
if-ha camera stream myhome camera.front_door --ndi "Front Door Camera"
```

**Requirements:**
- ffmpeg with NDI plugin installed
- Camera must support RTSP/HTTP streaming

**Output:**
```
Getting stream source for camera.front_door...
Stream source: rtsp://192.168.1.200:554/stream
Starting NDI bridge: Front Door Camera...
Starting stream... (press Ctrl+C to stop)
```

**NDI Installation:**
```bash
# Install ffmpeg with NDI support (varies by OS)
# Linux:
sudo apt-get install ffmpeg libndi
# macOS:
brew install ffmpeg ndi-sdk
```

---

## Automations

### List Automations

```bash
if-ha automation list myhome
if-ha automation list myhome --json
```

**Output:**
```
Automations (8)

Entity ID                                Name                           State
--------------------------------------------------------------------------------
automation.motion_detected               Motion Detection Alert         on
automation.night_mode                    Night Mode                     on
automation.morning_routine               Morning Routine                on
automation.vacation_mode                 Vacation Mode                  off
```

### Trigger Automation

```bash
if-ha automation trigger myhome automation.motion_detected
```

### Enable/Disable Automation

```bash
if-ha automation enable myhome automation.vacation_mode
if-ha automation disable myhome automation.night_mode
```

---

## Scripts

### List Scripts

```bash
if-ha script list myhome
if-ha script list myhome --json
```

**Output:**
```
Scripts (5)

Entity ID                                Name
--------------------------------------------------------------------------------
script.movie_mode                        Movie Mode
script.bedtime                           Bedtime Routine
script.welcome_home                      Welcome Home
```

### Run Script

```bash
# Basic execution
if-ha script run myhome script.movie_mode

# With variables
if-ha script run myhome script.movie_mode \
  --variables '{"brightness": 20, "color": "red"}'
```

---

## Scenes

### List Scenes

```bash
if-ha scene list myhome
if-ha scene list myhome --json
```

**Output:**
```
Scenes (6)

Entity ID                                Name
--------------------------------------------------------------------------------
scene.evening                            Evening Scene
scene.morning                            Morning Scene
scene.movie_time                         Movie Time
scene.romantic                           Romantic Scene
```

### Activate Scene

```bash
if-ha scene activate myhome scene.evening
if-ha scene activate myhome scene.movie_time
```

---

## Notifications

### Send Notification

```bash
# Persistent notification (visible in HA UI)
if-ha notify myhome --message "Coffee is ready" --title "Kitchen"

# To specific notification service
if-ha notify myhome \
  --message "Someone at the door" \
  --title "Doorbell" \
  --service mobile_app_phone
```

**Output:**
```
✓ Notification sent
  Title: Kitchen
  Message: Coffee is ready
```

---

## Media Players

### List Media Players

```bash
if-ha media list myhome
if-ha media list myhome --json
```

**Output:**
```
Media Players (4)

Entity ID                                Name                      State
---------------------------------------------------------------------------
media_player.living_room                 Living Room Speaker       playing
media_player.kitchen                     Kitchen Speaker           idle
media_player.bedroom                     Bedroom TV                off
```

### Control Playback

```bash
# Play/pause/stop
if-ha media play myhome media_player.living_room
if-ha media pause myhome media_player.living_room
if-ha media stop myhome media_player.living_room

# Play URL
if-ha media play myhome media_player.kitchen \
  --url http://stream.example.com/radio.mp3
```

### Text-to-Speech

```bash
if-ha tts myhome media_player.kitchen \
  --message "Dinner is ready"

# With language
if-ha tts myhome media_player.living_room \
  --message "Bonjour" \
  --language fr
```

---

## Events

### Fire Event

```bash
# Basic event
if-ha event fire myhome custom_event

# With data
if-ha event fire myhome doorbell_pressed \
  --data '{"camera": "front_door", "timestamp": "2025-11-12T10:00:00Z"}'
```

### List Event Types

```bash
if-ha event list myhome
if-ha event list myhome --json
```

---

## Status & Info

### Get Status

```bash
if-ha status myhome
if-ha status myhome --json
```

**Output:**
```
Home Assistant Status: myhome
--------------------------------------------------
Message: API running
```

### Get Info

```bash
if-ha info myhome
if-ha info myhome --json
```

**Output:**
```
Home Assistant Info: myhome
--------------------------------------------------
Version: 2024.11.0
Location: Home
Time Zone: America/New_York
Unit System: metric
Components: 157
Entities: 342
```

### Show Configuration

```bash
if-ha config myhome
if-ha config myhome --json
```

**Output:**
```
Home Assistant Configuration: myhome
--------------------------------------------------
Version: 2024.11.0
Location: Home
Latitude: 40.7128
Longitude: -74.0060
Elevation: 10
Time Zone: America/New_York
Unit System: metric

Components (157):
  - api
  - automation
  - camera
  - climate
  - config
  ... and 152 more
```

---

## Advanced Usage

### JSON Output for Scripting

All commands support `--json` flag for machine-readable output:

```bash
if-ha entities myhome --domain light --json | jq '.[] | select(.state == "on")'
if-ha status myhome --json | jq '.message'
```

### IF.witness Integration

All operations are automatically logged to IF.witness for audit trails:

```bash
# View logs
if-witness list --component IF.homeassistant

# Export logs
if-witness export compliance-report.pdf \
  --component IF.homeassistant \
  --days 30
```

### Bash Scripting Examples

**Morning Routine:**
```bash
#!/bin/bash
INSTANCE="myhome"

# Turn on lights
if-ha set $INSTANCE light.bedroom --state on --brightness 100
if-ha set $INSTANCE light.kitchen --state on --brightness 200

# Start coffee maker
if-ha set $INSTANCE switch.coffee_maker --state on

# Speak greeting
if-ha tts $INSTANCE media_player.kitchen \
  --message "Good morning! Coffee is brewing."

# Trigger morning automation
if-ha automation trigger $INSTANCE automation.morning_routine
```

**Check All Lights:**
```bash
#!/bin/bash
INSTANCE="myhome"

# Get all lights that are on
if-ha entities $INSTANCE --domain light --json | \
  jq -r '.[] | select(.state == "on") | .entity_id'
```

**Security Check:**
```bash
#!/bin/bash
INSTANCE="myhome"

# Check all locks
LOCKS=$(if-ha entities $INSTANCE --domain lock --json)

echo "$LOCKS" | jq -r '.[] | select(.state == "unlocked") |
  "⚠️  UNLOCKED: \(.attributes.friendly_name)"'
```

### Multiple Instances

Manage multiple Home Assistant instances:

```bash
# Add instances
if-ha add home --url http://192.168.1.100:8123 --token TOKEN1
if-ha add office --url http://192.168.2.100:8123 --token TOKEN2
if-ha add vacation --url https://cabin.example.com --token TOKEN3

# Control different instances
if-ha set home light.living_room --state on
if-ha set office light.desk --state on
if-ha set vacation climate.thermostat --temperature 65
```

### Configuration Location

Configurations are stored at:
```
~/.if/home-assistant/instances.yaml
```

**Format:**
```yaml
instances:
  myhome:
    url: http://homeassistant.local:8123
    token: eyJ0eXAiOiJKV1Qi...
    added_at: 2025-11-12T00:00:00Z
```

---

## Troubleshooting

### Connection Failed

```bash
# Check URL is correct
curl http://homeassistant.local:8123/api/

# Test with token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://homeassistant.local:8123/api/
```

### Authentication Failed

- Verify token is valid in Home Assistant UI
- Check token hasn't expired
- Ensure user has proper permissions

### Entity Not Found

```bash
# List all entities to find correct ID
if-ha entities myhome --json | jq '.[] | .entity_id'

# Check specific domain
if-ha entities myhome --domain light
```

### Camera Stream Not Working

- Ensure camera supports RTSP/HTTP streaming
- Check ffmpeg is installed with NDI support
- Verify network connectivity to camera

### Service Call Failed

```bash
# Check available services
curl -H "Authorization: Bearer TOKEN" \
  http://homeassistant.local:8123/api/services | jq '.'
```

---

## Integration with Other Tools

### With vMix

```bash
# Stream HA camera to vMix via NDI
if-ha camera stream myhome camera.front_door --ndi "Front Door"

# In vMix, add NDI input "Front Door"
if vmix ndi add myvmix --source "Front Door"
```

### With IF.witness

```bash
# All operations are automatically logged
if-witness list --component IF.homeassistant --days 7

# Export audit trail
if-witness export ha-audit.pdf \
  --component IF.homeassistant \
  --start "2025-11-01" \
  --end "2025-11-30"
```

### With Cron/Scheduled Tasks

```bash
# Add to crontab for scheduled control
# Turn off lights at midnight
0 0 * * * if-ha set myhome light.living_room --state off

# Check locks every hour
0 * * * * /home/user/scripts/check_locks.sh
```

---

## API Reference

For detailed API information, see:
- [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest/)
- [Home Assistant Services](https://www.home-assistant.io/docs/scripts/service-calls/)

---

## Support

For issues or questions:
- GitHub: https://github.com/infrafabric/infrafabric
- Documentation: https://docs.infrafabric.io
- Home Assistant Community: https://community.home-assistant.io

---

## License

Part of InfraFabric - Open source home automation and production control toolkit.
