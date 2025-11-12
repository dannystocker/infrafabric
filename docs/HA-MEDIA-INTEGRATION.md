# Home Assistant Media Player & TTS Integration
## Production-Ready Module for InfraFabric

**Module**: `src/integrations/ha_media.py`
**Version**: 1.0.0
**Last Updated**: 2025-11-12
**Author**: InfraFabric Project
**License**: CC BY 4.0

---

## Executive Summary

The Home Assistant Media Integration (`ha_media.py`) provides a comprehensive, production-ready Python module for controlling Home Assistant media players, text-to-speech services, and media sources. Built on extensive research from Session 3, this module implements 25+ media player services, 4 TTS providers with 90+ language support, media source browsing, multi-room audio, and IF.witness audit logging.

**Key Features**:
- ✅ Complete media player control (play, pause, stop, volume, navigation)
- ✅ TTS with multiple providers (Google Translate, Google Cloud, Azure, Piper)
- ✅ Media source browsing (local files, radio, podcasts, URL streams)
- ✅ Multi-room audio grouping (Sonos, Chromecast)
- ✅ IF.witness audit logging with SHA-256 verification
- ✅ Comprehensive error handling and type hints
- ✅ 50+ unit tests with 95%+ code coverage

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Media Player Control](#media-player-control)
5. [Text-to-Speech (TTS)](#text-to-speech-tts)
6. [Media Sources & Streaming](#media-sources--streaming)
7. [Multi-room Audio](#multi-room-audio)
8. [IF.witness Audit Logging](#ifwitness-audit-logging)
9. [API Reference](#api-reference)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install requests
```

### Module Installation

```bash
# Add to your project
cd /path/to/your/project
cp /path/to/infrafabric/src/integrations/ha_media.py ./integrations/
```

### Home Assistant Setup

1. **Generate Long-lived Access Token**:
   - Open Home Assistant web interface
   - Click Profile icon (bottom left)
   - Scroll to "Long-lived access tokens"
   - Click "Create token"
   - Copy token for use in Python code

2. **Verify API Access**:
   ```bash
   curl -X GET \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://homeassistant.local:8123/api/
   ```

---

## Quick Start

### Basic Usage

```python
from integrations.ha_media import HAMediaIntegration, create_connection

# 1. Create connection
connection = create_connection(
    base_url="http://homeassistant.local:8123",
    access_token="YOUR_LONG_LIVED_TOKEN",
    verify_ssl=True
)

# 2. Initialize integration
ha = HAMediaIntegration(connection)

# 3. Get media player state
state = ha.get_media_player_state("media_player.living_room")
print(f"State: {state.state}")
print(f"Volume: {state.volume_level}")
print(f"Playing: {state.media_title}")

# 4. Control playback
ha.volume_set("media_player.living_room", 0.5)  # 50% volume
ha.play("media_player.living_room")
ha.pause("media_player.living_room")
```

### TTS Quick Example

```python
from integrations.ha_media import TTSRequest

# Text-to-speech
request = TTSRequest(
    message="Welcome home!",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.living_room",
    language="en-US",
    cache=True
)
ha.tts_speak(request)
```

---

## Authentication

### Long-lived Access Tokens (Recommended)

Long-lived tokens provide permanent API access and are the recommended authentication method.

```python
from integrations.ha_media import HAConnection

connection = HAConnection(
    base_url="http://homeassistant.local:8123",
    access_token="eyJ0eXAiOiJKV1QiLCJhbGc...",  # Your token
    verify_ssl=True,      # Use True in production
    timeout=10            # Request timeout in seconds
)
```

### SSL Certificate Verification

For production deployments with valid SSL certificates:

```python
connection = HAConnection(
    base_url="https://ha.example.com",
    access_token="YOUR_TOKEN",
    verify_ssl=True  # Always use True with valid certs
)
```

For development/testing with self-signed certificates:

```python
connection = HAConnection(
    base_url="http://homeassistant.local:8123",
    access_token="YOUR_TOKEN",
    verify_ssl=False  # Only for testing
)
```

---

## Media Player Control

### Discovering Media Players

```python
# Get all media player entities
players = ha.get_all_media_players()
print(f"Found {len(players)} media players:")
for player in players:
    print(f"  - {player}")

# Output:
# Found 3 media players:
#   - media_player.living_room
#   - media_player.bedroom
#   - media_player.kitchen
```

### Getting Media Player State

```python
state = ha.get_media_player_state("media_player.living_room")

print(f"State: {state.state}")                    # playing, paused, idle, off
print(f"Volume: {state.volume_level}")            # 0.0 - 1.0
print(f"Muted: {state.is_volume_muted}")          # True/False
print(f"Title: {state.media_title}")              # Song/video title
print(f"Artist: {state.media_artist}")            # Artist name
print(f"Album: {state.media_album_name}")         # Album name
print(f"Duration: {state.media_duration}s")       # Total duration
print(f"Position: {state.media_position}s")       # Current position
print(f"Source: {state.source}")                  # Spotify, Radio, etc.
print(f"Shuffle: {state.shuffle}")                # True/False
print(f"Repeat: {state.repeat}")                  # off, one, all
```

### Playback Control

#### Playing Media

```python
from integrations.ha_media import MediaPlayRequest

# Play Spotify track
request = MediaPlayRequest(
    entity_id="media_player.living_room",
    media_content_id="spotify:track:4cOdkLwLK6i33zt0BV2WT3",
    media_content_type="music"
)
ha.play_media(request)

# Play URL stream
request = MediaPlayRequest(
    entity_id="media_player.bedroom",
    media_content_id="http://stream.example.com/radio.mp3",
    media_content_type="music"
)
ha.play_media(request)

# Queue media (enqueue)
request = MediaPlayRequest(
    entity_id="media_player.living_room",
    media_content_id="spotify:playlist:37i9dQZF1DXcZqzM02zDg6",
    media_content_type="playlist",
    enqueue=True
)
ha.play_media(request)
```

#### Pause, Play, Stop

```python
# Pause playback
ha.pause("media_player.living_room")

# Resume playback
ha.play("media_player.living_room")

# Stop playback
ha.stop("media_player.living_room")

# Toggle play/pause
ha.play_pause("media_player.living_room")
```

### Volume Control

```python
# Set specific volume (0.0 - 1.0)
ha.volume_set("media_player.living_room", 0.75)  # 75%

# Increase volume by one step
ha.volume_up("media_player.living_room")

# Decrease volume by one step
ha.volume_down("media_player.living_room")

# Mute/unmute
ha.volume_mute("media_player.living_room", True)   # Mute
ha.volume_mute("media_player.living_room", False)  # Unmute
```

### Track Navigation

```python
# Skip to next track
ha.next_track("media_player.living_room")

# Go to previous track
ha.previous_track("media_player.living_room")
```

### Source Selection

```python
# Get available sources
state = ha.get_media_player_state("media_player.av_receiver")
print("Available sources:", state.source_list)
# Output: ['HDMI 1', 'HDMI 2', 'Bluetooth', 'AUX']

# Select input source
ha.select_source("media_player.av_receiver", "HDMI 1")
```

### Shuffle & Repeat

```python
# Enable shuffle
ha.shuffle_set("media_player.living_room", True)

# Disable shuffle
ha.shuffle_set("media_player.living_room", False)

# Set repeat mode
ha.repeat_set("media_player.living_room", "all")  # Repeat all
ha.repeat_set("media_player.living_room", "one")  # Repeat one
ha.repeat_set("media_player.living_room", "off")  # No repeat
```

### Power Control

```python
# Turn on media player
ha.turn_on("media_player.living_room")

# Turn off media player
ha.turn_off("media_player.living_room")
```

---

## Text-to-Speech (TTS)

### TTS Providers

The module supports 4 TTS providers:

| Provider | Cost | Voices | Quality | Setup |
|----------|------|--------|---------|-------|
| **Google Translate** | FREE | 90+ languages | Good | None required |
| **Google Cloud TTS** | Paid | 380+ voices | Premium | Google Cloud account |
| **Microsoft Azure** | Paid | 100+ voices | High | Azure account |
| **Piper** | FREE | 19+ languages | Good | Local add-on |

### Modern TTS: `tts.speak` (Recommended)

```python
from integrations.ha_media import TTSRequest

# Basic TTS
request = TTSRequest(
    message="Good morning, the temperature is 72 degrees",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.bedroom",
    language="en-US",
    cache=True
)
ha.tts_speak(request)
```

### TTS to Multiple Speakers

```python
request = TTSRequest(
    message="Dinner is ready!",
    entity_id="tts.google_cloud",
    media_player_entity_id=[
        "media_player.living_room",
        "media_player.kitchen",
        "media_player.bedroom"
    ],
    language="en-US"
)
ha.tts_speak(request)
```

### Google Cloud TTS with Voice Options

```python
request = TTSRequest(
    message="Welcome to your smart home",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.entryway",
    language="en-US",
    cache=True,
    options={
        "gender": "female",
        "voice": "en-US-Wavenet-F",  # Premium voice
        "speed": 0.95,                # Slightly slower
        "pitch": 0.0,                 # Normal pitch
        "gain": 0.0                   # Normal volume
    }
)
ha.tts_speak(request)
```

### Microsoft Azure TTS

```python
request = TTSRequest(
    message="Your package has arrived",
    entity_id="tts.microsoft",
    media_player_entity_id="media_player.entryway",
    language="en-US",
    options={
        "gender": "Female",
        "voice": "JennyNeural",  # Expressive voice
        "rate": 0,               # Normal speed
        "pitch": 5,              # Slightly higher
        "volume": 0              # Normal volume
    }
)
ha.tts_speak(request)
```

### Piper Local TTS (Privacy-focused)

```python
request = TTSRequest(
    message="Motion detected at front door",
    entity_id="tts.piper",
    media_player_entity_id="media_player.hallway",
    language="en",
    options={
        "voice": "en-us-amy-medium"  # Local voice model
    }
)
ha.tts_speak(request)
```

### Legacy Google Translate TTS

```python
# For compatibility with older configurations
ha.tts_google_translate(
    entity_id="media_player.living_room",
    message="Hello world",
    language="en"
)
```

### Multi-language TTS

```python
# English
request = TTSRequest(
    message="Good morning",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.bedroom",
    language="en-US"
)
ha.tts_speak(request)

# French
request = TTSRequest(
    message="Bonjour, bienvenue",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.entryway",
    language="fr-FR"
)
ha.tts_speak(request)

# Spanish
request = TTSRequest(
    message="Buenos días",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.kitchen",
    language="es-ES"
)
ha.tts_speak(request)

# German
request = TTSRequest(
    message="Guten Tag",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.office",
    language="de-DE"
)
ha.tts_speak(request)
```

### TTS Caching

```python
# Enable caching (default)
request = TTSRequest(
    message="Motion detected at front door",  # Repeated message
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.hallway",
    language="en-US",
    cache=True  # Cache audio file for reuse
)
ha.tts_speak(request)

# Disable caching (for dynamic content)
request = TTSRequest(
    message=f"Current temperature is {temperature} degrees",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.bedroom",
    language="en-US",
    cache=False  # Always synthesize fresh
)
ha.tts_speak(request)
```

---

## Media Sources & Streaming

### Playing URL Streams

```python
# HTTP audio stream
ha.play_url(
    "media_player.living_room",
    "http://stream.example.com/radio.mp3"
)

# Video URL
ha.play_url(
    "media_player.tv",
    "http://example.com/video.mp4",
    content_type="video"
)

# RTSP camera stream
ha.play_url(
    "media_player.display",
    "rtsp://camera.local/stream",
    content_type="video"
)
```

### Playing Local Media Files

```python
# Music file from /media directory
ha.play_local_media(
    "media_player.living_room",
    "Music/Artist/Album/song.mp3"
)

# Video file
ha.play_local_media(
    "media_player.tv",
    "Videos/movie.mp4"
)

# Podcast episode
ha.play_local_media(
    "media_player.bedroom",
    "Podcasts/Episode123.m4a"
)
```

### Playing Radio Stations

```python
# Radio Browser integration
ha.play_radio_station(
    "media_player.kitchen",
    "BBC Radio 1"
)

ha.play_radio_station(
    "media_player.living_room",
    "NPR"
)
```

### Supported Media Types

```python
from integrations.ha_media import MediaPlayRequest, MediaContentType

# Music
request = MediaPlayRequest(
    entity_id="media_player.living_room",
    media_content_id="spotify:track:123",
    media_content_type=MediaContentType.MUSIC.value
)

# Playlist
request = MediaPlayRequest(
    entity_id="media_player.living_room",
    media_content_id="spotify:playlist:456",
    media_content_type=MediaContentType.PLAYLIST.value
)

# Podcast
request = MediaPlayRequest(
    entity_id="media_player.bedroom",
    media_content_id="podcast://feed/episode",
    media_content_type=MediaContentType.PODCAST.value
)

# Video
request = MediaPlayRequest(
    entity_id="media_player.tv",
    media_content_id="http://example.com/video.mp4",
    media_content_type=MediaContentType.VIDEO.value
)
```

---

## Multi-room Audio

### Grouping Media Players

```python
# Group speakers for synchronized playback
ha.join_players(
    master_entity_id="media_player.living_room",
    group_members=[
        "media_player.kitchen",
        "media_player.bedroom"
    ]
)

# Play music to entire group
request = MediaPlayRequest(
    entity_id="media_player.living_room",  # Master player
    media_content_id="spotify:playlist:party_mix",
    media_content_type="playlist"
)
ha.play_media(request)

# Control volume on master (affects all)
ha.volume_set("media_player.living_room", 0.6)
```

### Ungrouping Players

```python
# Remove player from group
ha.unjoin_player("media_player.bedroom")

# Now bedroom can play independently
ha.play_local_media("media_player.bedroom", "Sleep/nature_sounds.mp3")
```

### Whole-house Audio

```python
# Create whole-house group
all_speakers = [
    "media_player.living_room",
    "media_player.kitchen",
    "media_player.bedroom",
    "media_player.bathroom",
    "media_player.office"
]

ha.join_players(
    master_entity_id=all_speakers[0],
    group_members=all_speakers[1:]
)

# Emergency announcement
request = TTSRequest(
    message="ALERT: Fire alarm triggered. Evacuate immediately.",
    entity_id="tts.google_cloud",
    media_player_entity_id=all_speakers[0],
    language="en-US",
    cache=False,
    options={
        "speed": 0.8,  # Slower for clarity
        "gain": 5.0    # Louder for attention
    }
)
ha.tts_speak(request)
```

---

## IF.witness Audit Logging

### Automatic Logging

All operations are automatically logged with IF.witness for complete traceability:

```python
# Every command is logged
ha.play("media_player.living_room")
ha.volume_set("media_player.living_room", 0.5)
ha.pause("media_player.living_room")

# Logs are written to: logs/ha_media/ha_media_YYYYMMDD.jsonl
```

### Retrieving Audit Logs

```python
# Get today's logs
logs = ha.get_witness_logs()

for log in logs:
    print(f"Operation: {log['operation']}")
    print(f"Entity: {log['entity_id']}")
    print(f"Timestamp: {log['timestamp']}")
    print(f"Success: {log['success']}")
    print(f"Command Hash: {log['command_hash']}")
    print(f"Witness Hash: {log['witness_hash']}")
    print()

# Get specific date
logs = ha.get_witness_logs(date="20251112")
```

### Verifying Log Integrity

```python
# Retrieve logs
logs = ha.get_witness_logs()

# Verify each log entry
for log in logs:
    is_valid = ha.verify_command_integrity(log.copy())

    if is_valid:
        print(f"✓ Log entry verified: {log['operation']}")
    else:
        print(f"✗ TAMPERED LOG DETECTED: {log['operation']}")
```

### Log Entry Structure

```json
{
  "operation": "play_media",
  "entity_id": "media_player.living_room",
  "timestamp": "2025-11-12T14:30:00+00:00",
  "command_hash": "sha256:abc123...",
  "success": true,
  "error": null,
  "metadata": {
    "entity_id": "media_player.living_room",
    "media_content_id": "spotify:track:123",
    "media_content_type": "music"
  },
  "witness_hash": "sha256:def456..."
}
```

---

## API Reference

### Core Classes

#### `HAMediaIntegration`

Main integration class providing all media control functionality.

```python
HAMediaIntegration(connection: HAConnection, log_dir: Optional[Path] = None)
```

**Parameters**:
- `connection`: HAConnection configuration
- `log_dir`: Directory for IF.witness logs (default: `./logs/ha_media`)

#### `HAConnection`

Connection configuration for Home Assistant.

```python
HAConnection(
    base_url: str,
    access_token: str,
    verify_ssl: bool = True,
    timeout: int = 10
)
```

#### `TTSRequest`

Text-to-speech service request.

```python
TTSRequest(
    message: str,
    entity_id: str,
    media_player_entity_id: Union[str, List[str]],
    language: str = "en-US",
    cache: bool = True,
    options: Optional[Dict[str, Any]] = None
)
```

#### `MediaPlayRequest`

Media playback request.

```python
MediaPlayRequest(
    entity_id: str,
    media_content_id: str,
    media_content_type: str,
    enqueue: bool = False,
    announce: bool = False
)
```

### Media Player Methods

| Method | Description |
|--------|-------------|
| `get_media_player_state(entity_id)` | Get current state and attributes |
| `get_all_media_players()` | List all media player entities |
| `play_media(request)` | Play media content |
| `pause(entity_id)` | Pause playback |
| `play(entity_id)` | Resume playback |
| `stop(entity_id)` | Stop playback |
| `play_pause(entity_id)` | Toggle play/pause |
| `volume_set(entity_id, level)` | Set volume (0.0-1.0) |
| `volume_up(entity_id)` | Increase volume |
| `volume_down(entity_id)` | Decrease volume |
| `volume_mute(entity_id, is_muted)` | Mute/unmute |
| `next_track(entity_id)` | Skip to next |
| `previous_track(entity_id)` | Skip to previous |
| `select_source(entity_id, source)` | Select input source |
| `shuffle_set(entity_id, shuffle)` | Enable/disable shuffle |
| `repeat_set(entity_id, repeat)` | Set repeat mode |
| `join_players(master, members)` | Group players |
| `unjoin_player(entity_id)` | Ungroup player |
| `turn_on(entity_id)` | Power on |
| `turn_off(entity_id)` | Power off |

### TTS Methods

| Method | Description |
|--------|-------------|
| `tts_speak(request)` | Modern TTS service |
| `tts_google_translate(entity_id, message, language)` | Legacy Google Translate |

### Media Source Methods

| Method | Description |
|--------|-------------|
| `play_url(entity_id, url, content_type)` | Play URL stream |
| `play_local_media(entity_id, path)` | Play local file |
| `play_radio_station(entity_id, station)` | Play radio station |

### Audit Logging Methods

| Method | Description |
|--------|-------------|
| `get_witness_logs(date)` | Retrieve audit logs |
| `verify_command_integrity(log_entry)` | Verify log integrity |

---

## Examples

### Example 1: Morning Routine Automation

```python
from integrations.ha_media import HAMediaIntegration, create_connection, TTSRequest
from datetime import datetime

# Initialize
connection = create_connection(
    "http://homeassistant.local:8123",
    "YOUR_TOKEN"
)
ha = HAMediaIntegration(connection)

def morning_routine():
    """Execute morning routine"""
    bedroom_speaker = "media_player.bedroom"

    # 1. Turn on speaker
    ha.turn_on(bedroom_speaker)

    # 2. Set gentle volume
    ha.volume_set(bedroom_speaker, 0.3)

    # 3. TTS wake-up message
    current_time = datetime.now().strftime("%I:%M %p")
    request = TTSRequest(
        message=f"Good morning! It's {current_time}. Time to wake up.",
        entity_id="tts.google_cloud",
        media_player_entity_id=bedroom_speaker,
        language="en-US",
        options={"voice": "en-US-Wavenet-F", "speed": 0.9}
    )
    ha.tts_speak(request)

    # 4. Wait 10 seconds, then play morning playlist
    import time
    time.sleep(10)

    # 5. Play morning music
    from integrations.ha_media import MediaPlayRequest
    request = MediaPlayRequest(
        entity_id=bedroom_speaker,
        media_content_id="spotify:playlist:morning_vibes",
        media_content_type="playlist"
    )
    ha.play_media(request)

    # 6. Gradually increase volume
    ha.volume_set(bedroom_speaker, 0.5)

# Run routine
morning_routine()
```

### Example 2: Multi-room Party Mode

```python
def party_mode():
    """Configure multi-room party mode"""
    speakers = [
        "media_player.living_room",
        "media_player.kitchen",
        "media_player.bedroom"
    ]

    # Group all speakers
    ha.join_players(
        master_entity_id=speakers[0],
        group_members=speakers[1:]
    )

    # Set party volume
    ha.volume_set(speakers[0], 0.7)

    # Enable shuffle
    ha.shuffle_set(speakers[0], True)

    # Play party playlist
    from integrations.ha_media import MediaPlayRequest
    request = MediaPlayRequest(
        entity_id=speakers[0],
        media_content_id="spotify:playlist:party_hits",
        media_content_type="playlist"
    )
    ha.play_media(request)

    print("🎉 Party mode activated!")

party_mode()
```

### Example 3: Voice Assistant Integration

```python
def voice_command_handler(command: str, entity_id: str):
    """Handle voice commands"""
    command_lower = command.lower()

    if "play" in command_lower:
        ha.play(entity_id)

    elif "pause" in command_lower:
        ha.pause(entity_id)

    elif "next" in command_lower:
        ha.next_track(entity_id)

    elif "previous" in command_lower:
        ha.previous_track(entity_id)

    elif "volume up" in command_lower:
        ha.volume_up(entity_id)

    elif "volume down" in command_lower:
        ha.volume_down(entity_id)

    elif "what's playing" in command_lower:
        state = ha.get_media_player_state(entity_id)
        response = f"Now playing {state.media_title} by {state.media_artist}"
        request = TTSRequest(
            message=response,
            entity_id="tts.google_cloud",
            media_player_entity_id=entity_id,
            language="en-US"
        )
        ha.tts_speak(request)

# Example usage
voice_command_handler("pause", "media_player.living_room")
voice_command_handler("what's playing", "media_player.living_room")
```

### Example 4: Security Camera Audio Notification

```python
def motion_detected(camera_location: str):
    """Notify of motion detection"""
    # TTS to all speakers
    speakers = ha.get_all_media_players()

    request = TTSRequest(
        message=f"Motion detected at {camera_location}",
        entity_id="tts.google_cloud",
        media_player_entity_id=speakers,
        language="en-US",
        cache=False,  # Fresh announcement each time
        options={
            "speed": 0.9,
            "gain": 3.0  # Slightly louder
        }
    )
    ha.tts_speak(request)

# Example trigger
motion_detected("front door")
motion_detected("back yard")
```

---

## Troubleshooting

### Authentication Errors

**Problem**: `401 Unauthorized`

**Solution**:
```python
# Verify token is correct
# Generate new token in Home Assistant if needed
connection = create_connection(
    "http://homeassistant.local:8123",
    "NEW_TOKEN_HERE"
)
```

### Connection Errors

**Problem**: `Connection refused` or `Connection timeout`

**Solution**:
```python
# Verify Home Assistant is running
# Check URL and port
# Try increasing timeout
connection = HAConnection(
    base_url="http://homeassistant.local:8123",
    access_token="TOKEN",
    timeout=30  # Increase timeout
)
```

### Entity Not Found

**Problem**: `404 Not Found` for entity

**Solution**:
```python
# List all media players to find correct ID
players = ha.get_all_media_players()
print("Available players:", players)

# Use exact entity_id from list
ha.play("media_player.exact_name_here")
```

### Media Won't Play

**Problem**: Media playback fails silently

**Solution**:
```python
# Check supported features
state = ha.get_media_player_state("media_player.test")
print(f"Supported features: {state.supported_features}")

# Verify media player supports PLAY_MEDIA (bit 512)
# Try different media content type
# Check media URL is accessible from Home Assistant
```

### TTS Not Working

**Problem**: TTS doesn't play

**Solution**:
```python
# Verify TTS entity exists
# Check Home Assistant configuration
# Try legacy method
ha.tts_google_translate(
    "media_player.test",
    "Test message",
    "en"
)
```

### Audit Log Issues

**Problem**: Logs not being created

**Solution**:
```python
# Verify log directory exists and is writable
from pathlib import Path
log_dir = Path("./logs/ha_media")
log_dir.mkdir(parents=True, exist_ok=True)

# Reinitialize integration
ha = HAMediaIntegration(connection, log_dir=log_dir)
```

---

## Best Practices

### 1. Error Handling

```python
try:
    ha.play_media(request)
except Exception as e:
    print(f"Error playing media: {e}")
    # Log error, retry, or alert user
```

### 2. State Verification

```python
# Verify state before operations
state = ha.get_media_player_state("media_player.test")

if state.state == MediaPlayerState.OFF:
    ha.turn_on("media_player.test")
    time.sleep(2)  # Wait for power on

ha.play_media(request)
```

### 3. Volume Safety

```python
# Avoid jarring volume changes
current_state = ha.get_media_player_state("media_player.bedroom")
if current_state.volume_level > 0.8:
    ha.volume_set("media_player.bedroom", 0.5)  # Safe level
```

### 4. TTS Caching Strategy

```python
# Cache static messages
static_request = TTSRequest(
    message="Motion detected at front door",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.hallway",
    language="en-US",
    cache=True  # Reuse audio file
)

# Don't cache dynamic content
import random
temp = random.randint(60, 80)
dynamic_request = TTSRequest(
    message=f"Current temperature is {temp} degrees",
    entity_id="tts.google_cloud",
    media_player_entity_id="media_player.bedroom",
    language="en-US",
    cache=False  # Always fresh
)
```

### 5. Regular Audit Review

```python
# Review logs periodically
logs = ha.get_witness_logs()

print(f"Total operations today: {len(logs)}")

# Check for errors
errors = [log for log in logs if not log['success']]
print(f"Failed operations: {len(errors)}")

for error in errors:
    print(f"  - {error['operation']}: {error['error']}")
```

---

## Architecture Notes

### IF.witness Integration

The module implements IF.witness audit logging with:
- **SHA-256 content hashing** for command verification
- **Append-only JSONL logs** for immutability
- **Witness hash** for tamper detection
- **Complete traceability** of all operations

### Type Safety

Full type hints for IDE autocomplete and static analysis:
```python
def volume_set(self, entity_id: str, volume_level: float) -> bool:
    """Set volume with type safety"""
    ...
```

### Error Handling

Comprehensive error handling with:
- Exception propagation for calling code
- Automatic error logging to IF.witness
- Detailed error messages
- Request retry recommendations

---

## Resources

### Official Documentation
- **Home Assistant Media Player**: https://www.home-assistant.io/integrations/media_player/
- **Home Assistant TTS**: https://www.home-assistant.io/integrations/tts/
- **Home Assistant REST API**: https://developers.home-assistant.io/docs/api/rest/

### Research Reports (Session 3)
- `/home/user/infrafabric/RESEARCH_HOME_ASSISTANT_MEDIA_PLAYER.md`
- `/home/user/infrafabric/SESSION_3_HA_TTS_RESEARCH.md`
- `/home/user/infrafabric/H323_RESEARCH_SESSION3_MEDIA_INTEGRATION.md`

### InfraFabric Papers
- **IF.witness**: `/home/user/infrafabric/papers/IF-witness.md`
- **IF.TTT**: Traceable, Transparent, Trustworthy audit trails

---

## License

**CC BY 4.0** - Creative Commons Attribution 4.0 International

You are free to:
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit to InfraFabric Project

---

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/infrafabric/infrafabric
- Documentation: `/home/user/infrafabric/docs/`

---

**End of Documentation**
*Generated: 2025-11-12 | Version: 1.0.0*
