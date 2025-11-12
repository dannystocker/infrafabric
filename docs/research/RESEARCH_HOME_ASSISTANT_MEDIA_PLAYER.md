# Home Assistant Media Player Integration Research Report
## Session 3 - Master Integration Sprint

**Prepared**: 2025-11-12
**Research Agent**: Haiku 4.5
**Focus**: Media Player API, Services, Attributes, and Integration Patterns

---

## Executive Summary

Home Assistant provides a comprehensive media player integration framework that allows control of various audio/video playback devices through REST APIs, service calls, and real-time state management. This research document covers the complete media player API specification, available services, entity attributes, supported media types, and common media player integrations.

---

## 1. MEDIA PLAYER REST API

### 1.1 API Endpoints Overview

The Home Assistant REST API provides several endpoints for interacting with media players:

#### 1.1.1 Get All States
```
GET /api/states
```

Retrieves the states of all entities within Home Assistant.

**Response**: JSON array containing all entity states

**Headers Required**:
```
Authorization: Bearer TOKEN
Content-Type: application/json
```

#### 1.1.2 Get Specific Media Player State
```
GET /api/states/media_player.<entity_name>
```

Fetches the state and attributes of a specific media player entity.

**Example Endpoint**:
```
GET /api/states/media_player.living_room
GET /api/states/media_player.bedroom_chromecast
GET /api/states/media_player.spotify_player
```

**Response Structure**:
```json
{
  "entity_id": "media_player.living_room",
  "state": "playing",
  "attributes": {
    "volume_level": 0.24,
    "is_volume_muted": false,
    "media_content_id": "spotify:track:123abc",
    "media_content_type": "music",
    "media_title": "Song Title",
    "media_artist": "Artist Name",
    "media_album_name": "Album Name",
    "media_duration": 331,
    "media_position": 26,
    "media_position_updated_at": "2025-11-12T14:30:00+00:00",
    "media_track": 5,
    "shuffle": false,
    "source": "Spotify",
    "source_list": ["Spotify", "Radio", "Local Library"],
    "supported_features": 720429
  },
  "last_changed": "2025-11-12T14:25:00+00:00",
  "last_updated": "2025-11-12T14:30:00+00:00"
}
```

### 1.2 HTTP Methods & Status Codes

**Supported Methods**: GET, POST

**Status Codes**:
- `200 OK` - Successful request
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Missing or invalid authentication token
- `404 Not Found` - Entity does not exist
- `405 Method Not Allowed` - Method not supported for endpoint

### 1.3 Example API Calls

**Curl - Get Media Player State**:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8123/api/states/media_player.living_room
```

**Python - Get Media Player State**:
```python
import requests

url = "http://localhost:8123/api/states/media_player.living_room"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

response = requests.get(url, headers=headers)
state = response.json()
print(f"State: {state['state']}")
print(f"Volume: {state['attributes']['volume_level']}")
print(f"Now Playing: {state['attributes']['media_title']}")
```

---

## 2. MEDIA PLAYER SERVICES

Media player services are called through the REST API endpoint:

```
POST /api/services/media_player/<service_name>
```

### 2.1 Core Media Control Services

#### 2.1.1 play_media
Instructs the media player to play specified media content.

**Endpoint**:
```
POST /api/services/media_player/play_media
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room",
  "media_content_id": "spotify:track:123abc",
  "media_content_type": "music",
  "enqueue": false,
  "announce": false
}
```

**Parameters**:
- `entity_id` (required): Target media player entity
- `media_content_id` (required): The ID or URL of the media to play
- `media_content_type` (required): Type of media (see Supported Media Types section)
- `enqueue` (optional): Queue media instead of playing immediately (default: false)
- `announce` (optional): Try to pause current music, announce, then resume (default: false)
- `title` (optional): Title of the media
- `media_position_ms` (optional): Position in milliseconds to start playback
- `extra` (optional): Additional metadata for the media player

**Examples**:

*Playing a Spotify Track*:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "media_content_id": "spotify:track:4cOdkLwLK6i33zt0BV2WT3",
    "media_content_type": "music"
  }' \
  http://localhost:8123/api/services/media_player/play_media
```

*Playing a URL Stream*:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.bedroom",
    "media_content_id": "http://stream.example.com/radio.mp3",
    "media_content_type": "music"
  }' \
  http://localhost:8123/api/services/media_player/play_media
```

*Playing a Video File*:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room_tv",
    "media_content_id": "http://192.168.1.10/videos/movie.mp4",
    "media_content_type": "video/mp4"
  }' \
  http://localhost:8123/api/services/media_player/play_media
```

*Queueing Media*:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "media_content_id": "spotify:playlist:37i9dQZF1DXcZqzM02zDg6",
    "media_content_type": "playlist",
    "enqueue": "play"
  }' \
  http://localhost:8123/api/services/media_player/play_media
```

#### 2.1.2 media_pause
Pauses playback on the media player.

**Endpoint**:
```
POST /api/services/media_player/media_pause
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room"
}
```

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room"}' \
  http://localhost:8123/api/services/media_player/media_pause
```

#### 2.1.3 media_play
Resumes playback on the media player.

**Endpoint**:
```
POST /api/services/media_player/media_play
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room"
}
```

#### 2.1.4 media_play_pause
Toggles between play and pause states.

**Endpoint**:
```
POST /api/services/media_player/media_play_pause
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room"
}
```

#### 2.1.5 media_stop
Stops playback completely.

**Endpoint**:
```
POST /api/services/media_player/media_stop
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room"
}
```

**Example**:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room"}' \
  http://localhost:8123/api/services/media_player/media_stop
```

### 2.2 Volume Control Services

#### 2.2.1 volume_set
Sets the volume level of the media player.

**Endpoint**:
```
POST /api/services/media_player/volume_set
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room",
  "volume_level": 0.5
}
```

**Parameters**:
- `entity_id` (required): Target media player
- `volume_level` (required): Volume level from 0.0 (mute) to 1.0 (maximum)

**Examples**:

*Set Volume to 50%*:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "volume_level": 0.5
  }' \
  http://localhost:8123/api/services/media_player/volume_set
```

*Set Volume to 75%*:
```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "volume_level": 0.75
  }' \
  http://localhost:8123/api/services/media_player/volume_set
```

#### 2.2.2 volume_up
Increases volume by one step.

**Endpoint**:
```
POST /api/services/media_player/volume_up
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room"
}
```

#### 2.2.3 volume_down
Decreases volume by one step.

**Endpoint**:
```
POST /api/services/media_player/volume_down
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room"
}
```

#### 2.2.4 volume_mute
Mutes or unmutes the media player.

**Endpoint**:
```
POST /api/services/media_player/volume_mute
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room",
  "is_volume_muted": true
}
```

**Parameters**:
- `entity_id` (required): Target media player
- `is_volume_muted` (required): true to mute, false to unmute

### 2.3 Track Navigation Services

#### 2.3.1 media_next_track
Plays the next track in the playlist.

**Endpoint**:
```
POST /api/services/media_player/media_next_track
```

#### 2.3.2 media_previous_track
Plays the previous track in the playlist.

**Endpoint**:
```
POST /api/services/media_player/media_previous_track
```

### 2.4 Source & Mode Selection Services

#### 2.4.1 select_source
Changes the input source of the media player.

**Endpoint**:
```
POST /api/services/media_player/select_source
```

**Request Body**:
```json
{
  "entity_id": "media_player.av_receiver",
  "source": "HDMI 1"
}
```

**Available Sources**: Depends on the device. Retrieved from `source_list` attribute.

#### 2.4.2 select_sound_mode
Changes the sound mode/audio preset.

**Endpoint**:
```
POST /api/services/media_player/select_sound_mode
```

**Request Body**:
```json
{
  "entity_id": "media_player.av_receiver",
  "sound_mode": "Stereo"
}
```

### 2.5 Power Control Services

#### 2.5.1 turn_on
Powers on the media player.

**Endpoint**:
```
POST /api/services/media_player/turn_on
```

#### 2.5.2 turn_off
Powers off the media player.

**Endpoint**:
```
POST /api/services/media_player/turn_off
```

### 2.6 Playlist & Grouping Services

#### 2.6.1 clear_playlist
Clears the current playlist.

**Endpoint**:
```
POST /api/services/media_player/clear_playlist
```

#### 2.6.2 shuffle_set
Enables or disables shuffle mode.

**Endpoint**:
```
POST /api/services/media_player/shuffle_set
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room",
  "shuffle": true
}
```

#### 2.6.3 repeat_set
Sets the repeat mode.

**Endpoint**:
```
POST /api/services/media_player/repeat_set
```

**Request Body**:
```json
{
  "entity_id": "media_player.living_room",
  "repeat": "all"
}
```

**Repeat Values**: "off", "one", "all"

#### 2.6.4 join
Groups multiple media players for synchronized playback.

**Endpoint**:
```
POST /api/services/media_player/join
```

#### 2.6.5 unjoin
Removes a media player from a group.

**Endpoint**:
```
POST /api/services/media_player/unjoin
```

---

## 3. MEDIA PLAYER ATTRIBUTES

Media player entities expose various state attributes that reflect the current status and capabilities of the device.

### 3.1 Playback State Attributes

#### 3.1.1 state
Current operational state of the media player.

**Possible Values**:
- `off` - Device is off or unavailable
- `idle` - Device is ready but not playing
- `playing` - Currently playing media
- `paused` - Has active media but paused
- `buffering` - Preparing playback

**Example**: `"state": "playing"`

#### 3.1.2 supported_features
Bitwise flags indicating which features the media player supports.

**Feature Flags** (combined with bitwise OR):
```
PAUSE = 1
SEEK = 2
VOLUME_SET = 4
VOLUME_MUTE = 8
PREVIOUS_TRACK = 16
NEXT_TRACK = 32
TURN_ON = 128
TURN_OFF = 256
PLAY_MEDIA = 512
VOLUME_STEP = 1024
SELECT_SOURCE = 2048
STOP = 4096
CLEAR_PLAYLIST = 8192
PLAY = 16384
SHUFFLE_SET = 32768
SELECT_SOUND_MODE = 65536
BROWSE_MEDIA = 131072
REPEAT_SET = 262144
GROUPING = 524288
MEDIA_ANNOUNCE = 1048576
MEDIA_ENQUEUE = 2097152
```

**Example**: `"supported_features": 720429` (indicates combined support for multiple features)

### 3.2 Volume Attributes

#### 3.2.1 volume_level
Current volume level as a float from 0.0 to 1.0.

- `0.0` = Muted/Silent
- `0.5` = 50% volume
- `1.0` = Maximum volume

**Example**: `"volume_level": 0.24`

#### 3.2.2 is_volume_muted
Boolean indicating whether the volume is currently muted.

- `true` = Muted
- `false` = Not muted

**Example**: `"is_volume_muted": false`

### 3.3 Media Information Attributes

#### 3.3.1 media_content_id
Unique identifier for the currently playing media.

**Examples**:
- `"spotify:track:4cOdkLwLK6i33zt0BV2WT3"` (Spotify track)
- `"http://example.com/song.mp3"` (URL)
- `"plex://server/123"` (Plex content)

#### 3.3.2 media_content_type
Type/format of the currently playing media.

**Common Values**:
- `"music"` - Audio file or track
- `"playlist"` - Multiple tracks
- `"video"` - Video file
- `"episode"` - Podcast/TV episode
- `"channel"` - Radio/streaming channel
- `"url"` - Raw URL stream
- MIME types: `"audio/mp3"`, `"audio/flac"`, `"video/mp4"`

#### 3.3.3 media_title
Title of the currently playing media.

**Examples**:
- `"Bohemian Rhapsody"` (song title)
- `"The Last of Us"` (show title)
- `"Breaking News Live"` (stream name)

#### 3.3.4 media_artist
Artist or creator of the media (primarily for music).

**Example**: `"Queen"`

#### 3.3.5 media_album_name
Album or collection name containing the media.

**Example**: `"A Night at the Opera"`

#### 3.3.6 media_album_artist
Album artist (may differ from track artist).

**Example**: `"Various Artists"`

#### 3.3.7 media_track
Track number in album or playlist (integer).

**Example**: `5`

### 3.4 Playback Position Attributes

#### 3.4.1 media_duration
Total duration of current media in seconds (integer).

**Example**: `"media_duration": 331`

#### 3.4.2 media_position
Current playback position in seconds (integer).

**Example**: `"media_position": 26`

#### 3.4.3 media_position_updated_at
ISO 8601 timestamp of when media_position was last updated.

**Example**: `"media_position_updated_at": "2025-11-12T14:30:00+00:00"`

### 3.5 Playback Mode Attributes

#### 3.5.1 shuffle
Boolean indicating if shuffle mode is enabled.

- `true` = Shuffle enabled
- `false` = Shuffle disabled

**Example**: `"shuffle": false`

#### 3.5.2 repeat
Current repeat mode.

**Values**: `"off"`, `"one"`, `"all"`

**Example**: `"repeat": "off"`

### 3.6 Source & Input Attributes

#### 3.6.1 source
Currently selected input source.

**Example**: `"Spotify"`, `"HDMI 1"`, `"AUX"`, `"Radio"`

#### 3.6.2 source_list
List of available input sources for this device.

**Example**:
```json
"source_list": ["Spotify", "Radio", "Local Library", "Bluetooth"]
```

### 3.7 Sound Mode Attributes

#### 3.7.1 sound_mode
Currently selected sound mode/audio preset.

**Example**: `"Stereo"`, `"Surround"`, `"Movie"`, `"Music"`

#### 3.7.2 sound_mode_list
List of available sound modes.

**Example**:
```json
"sound_mode_list": ["Stereo", "Surround", "Movie", "Music", "Sports"]
```

### 3.8 Group/Multi-room Attributes

#### 3.8.1 group_members
List of entity IDs for devices in the playback group.

**Example**:
```json
"group_members": [
  "media_player.living_room",
  "media_player.bedroom",
  "media_player.kitchen"
]
```

---

## 4. SUPPORTED MEDIA TYPES

### 4.1 Audio Media Types

| Media Type | Description | Example |
|-----------|-------------|---------|
| `music` | Audio track or song | Spotify tracks, MP3 files |
| `playlist` | Collection of audio tracks | Spotify playlists, Albums |
| `podcast` | Audio episode | Podcast RSS feeds, Episodes |
| `channel` | Audio stream | Radio stations, Streaming channels |
| `audio/mp3` | MP3 audio file (MIME type) | `.mp3` files via HTTP |
| `audio/flac` | FLAC lossless audio | `.flac` files via HTTP |
| `audio/wav` | WAV audio file | `.wav` files via HTTP |
| `audio/ogg` | Ogg Vorbis audio | `.ogg` files via HTTP |
| `audio/aac` | AAC audio format | `.aac` files via HTTP |

### 4.2 Video Media Types

| Media Type | Description | Example |
|-----------|-------------|---------|
| `video` | Generic video content | Video URLs |
| `video/mp4` | MP4 video file | `.mp4` files via HTTP |
| `video/mkv` | Matroska video format | `.mkv` files via HTTP |
| `tvshow` | Television show | TV series |
| `episode` | TV episode or similar | Individual episodes |
| `movie` | Movie content | Film files |

### 4.3 Special Media Types

| Media Type | Description | Example |
|-----------|-------------|---------|
| `url` | Raw URL stream | Direct HTTP streams |
| `image` | Image file | `.jpg`, `.png` images |

### 4.4 Integration-Specific Types

**Spotify**:
- `spotify:track:TRACK_ID`
- `spotify:album:ALBUM_ID`
- `spotify:playlist:PLAYLIST_ID`
- `spotify:artist:ARTIST_ID`

**Plex**:
- `plex://server/CONTENT_ID`

**Local Media**:
- `music://media-source/local/music/TRACK`
- `media-source://media_source/local_source/PATH`

### 4.5 Media Type Support by Device

**Chromecast**:
- Audio: MP3, FLAC, WAV, OGG, AAC
- Video: MP4, WebM, Matroska
- Images: JPG, PNG, GIF

**Sonos**:
- Audio: MP3, FLAC, WAV, AAC, OGG, ALAC
- Streaming services: Spotify, Apple Music, Amazon Music, TuneIn

**Spotify Integration**:
- Tracks, Albums, Playlists, Artists via Spotify URIs

**Apple TV**:
- Video: MP4, MOV
- Audio: AAC, MP3, ALAC
- Images: HEIF, JPG, PNG

---

## 5. COMMON MEDIA PLAYERS

### 5.1 Google Cast / Chromecast

**Integration**: `cast`

**Supported Features**:
- Play/Pause/Stop
- Volume control
- Multiple media formats
- Network streaming via HTTP(S)
- Text-to-speech
- Media browsing

**Capabilities**:
- Plays modern media formats (images, audio, video)
- MP3 streams and net radios
- FLAC and video files from local network
- Built-in Default Media Receiver application

**Home Assistant Integration**:
```
Integration: Google Cast
Service Domain: media_player
Entity Format: media_player.device_name
```

**Example Entities**:
- `media_player.living_room_chromecast`
- `media_player.bedroom_google_home`

### 5.2 Sonos

**Integration**: `sonos`

**Supported Features**:
- Play/Pause/Stop
- Volume control with mute
- Source selection
- Track navigation
- Group management for multi-room
- Sound mode selection

**Streaming Services**:
- Spotify
- Apple Music
- Amazon Music
- Deezer
- TuneIn Radio
- Local library streaming

**Home Assistant Integration**:
```
Integration: Sonos
Service Domain: media_player
Entity Format: media_player.device_name
```

**Example Entities**:
- `media_player.living_room_sonos`
- `media_player.kitchen_sonos`

**Special Features**:
- `join` service for grouped playback
- `unjoin` service to separate from group
- Source selection via `select_source` service

### 5.3 Spotify

**Integration**: `spotify`

**Supported Features**:
- Play/Pause/Stop
- Track navigation
- Playlist management
- Volume control
- Browse Spotify library
- Device selection

**Requirements**:
- Spotify Premium account (full control)
- Free account (limited to browsing and status only)
- Spotify Developer app credentials

**Home Assistant Integration**:
```
Integration: Spotify
Service Domain: media_player
Entity Format: media_player.spotify_[user_id]
```

**Custom Components**:
- **Spotcast**: Start Spotify playback on idle Chromecast devices
- **SpotifyPlus**: Enhanced Spotify integration with additional features

### 5.4 Apple TV

**Supported Features**:
- Play/Pause/Stop
- Volume control
- Source selection
- Media browsing
- AirPlay receiver

**Home Assistant Integration**:
- Available through HomeKit integration
- Airplay media streaming

### 5.5 Plex / Jellyfin / Emby

**Integration**: Media server integrations

**Supported Features**:
- Play/Pause/Stop
- Track/Episode navigation
- Library browsing
- Volume control
- Subtitle support
- Media position tracking

**Home Assistant Integration**:
- Browse and play media from library
- Multiple device support
- Playback control

**Example Use Case**:
```
{
  "entity_id": "media_player.living_room",
  "media_content_id": "plex://server/CONTENT_ID",
  "media_content_type": "movie"
}
```

### 5.6 Universal Media Player

**Integration**: `universal`

**Purpose**: Combine multiple media players into a single entity

**Features**:
- Group heterogeneous media players
- Common control interface
- Source-based device selection
- Fallback support

**Configuration Example**:
```yaml
media_player:
  - platform: universal
    name: Living Room Entertainment
    devices:
      - media_player.sonos
      - media_player.chromecast
      - media_player.roku
```

### 5.7 Other Supported Players

**VLC Media Player**:
- Local playback on computer
- Network streaming
- Limited media type support

**Kaleidescape**:
- Movie library playback
- High-quality video

**Anthem Receivers**:
- AV receiver control
- Volume and source management

**Yamaha AV Receivers**:
- Surround sound control
- Multiple input sources

**Onkyo Receivers**:
- Audio/video receiver integration
- Sound mode control

---

## 6. PRACTICAL INTEGRATION EXAMPLES

### 6.1 Complete Playback Workflow

```bash
# Step 1: Get current state
curl -X GET \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8123/api/states/media_player.living_room

# Step 2: Set volume to 50%
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room", "volume_level": 0.5}' \
  http://localhost:8123/api/services/media_player/volume_set

# Step 3: Play Spotify track
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "media_content_id": "spotify:track:4cOdkLwLK6i33zt0BV2WT3",
    "media_content_type": "music"
  }' \
  http://localhost:8123/api/services/media_player/play_media

# Step 4: After 10 minutes, pause playback
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room"}' \
  http://localhost:8123/api/services/media_player/media_pause

# Step 5: Resume playback
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room"}' \
  http://localhost:8123/api/services/media_player/media_play
```

### 6.2 Multi-room Audio Setup

```bash
# Create group (join devices)
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "group_members": ["media_player.kitchen", "media_player.bedroom"]
  }' \
  http://localhost:8123/api/services/media_player/join

# Play to entire group
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "media_content_id": "spotify:playlist:37i9dQZF1DXcZqzM02zDg6",
    "media_content_type": "playlist"
  }' \
  http://localhost:8123/api/services/media_player/play_media

# Ungroup
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.bedroom"}' \
  http://localhost:8123/api/services/media_player/unjoin
```

### 6.3 Media Player State Monitoring

```python
import requests
import time

BASE_URL = "http://localhost:8123"
TOKEN = "YOUR_TOKEN"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def get_media_state(entity_id):
    url = f"{BASE_URL}/api/states/{entity_id}"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def monitor_playback(entity_id, check_interval=5):
    """Monitor media player state changes"""
    last_state = None

    while True:
        state = get_media_state(entity_id)
        current = state['state']

        if current != last_state:
            print(f"State changed: {last_state} -> {current}")
            if current == "playing":
                attrs = state['attributes']
                print(f"  Now playing: {attrs.get('media_title')}")
                print(f"  Artist: {attrs.get('media_artist')}")
                print(f"  Volume: {attrs.get('volume_level') * 100}%")
            last_state = current

        time.sleep(check_interval)

# Monitor living room media player
monitor_playback("media_player.living_room")
```

### 6.4 Voice Assistant Integration (Example Commands)

```bash
# Play specific artist
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "media_content_id": "spotify:artist:1vCWHaC5f2uS3yhpwWbIA6",
    "media_content_type": "artist"
  }' \
  http://localhost:8123/api/services/media_player/play_media

# Play specific album
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "media_player.living_room",
    "media_content_id": "spotify:album:6JWaHc9EqG1XDCBvMNbpU2",
    "media_content_type": "album"
  }' \
  http://localhost:8123/api/services/media_player/play_media

# Enable shuffle
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room", "shuffle": true}' \
  http://localhost:8123/api/services/media_player/shuffle_set

# Set repeat to all
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "media_player.living_room", "repeat": "all"}' \
  http://localhost:8123/api/services/media_player/repeat_set
```

---

## 7. AUTHENTICATION & SECURITY

### 7.1 Token Generation

All API calls require a Bearer token for authentication.

**Token Types**:
1. **Long-lived access tokens**: Valid indefinitely (recommended for API)
2. **Short-lived tokens**: Automatically rotated by Home Assistant
3. **API password**: Legacy method (deprecated)

**Obtaining a Token**:
1. Go to Home Assistant web interface
2. Click Profile icon (bottom left)
3. Click "Create token" under "Long-lived access tokens"
4. Copy the token for API use

### 7.2 API Call Security

**Best Practices**:
- Always use HTTPS in production
- Rotate tokens periodically
- Store tokens securely (environment variables, secrets)
- Use separate tokens for different integrations
- Implement rate limiting for public-facing APIs

---

## 8. TROUBLESHOOTING & COMMON ISSUES

### 8.1 Service Call Returns 400 Bad Request

**Causes**:
- Malformed JSON in request body
- Invalid entity_id format
- Missing required parameters
- Unsupported service for media player

**Solution**:
- Verify JSON syntax is valid
- Use format: `media_player.entity_name`
- Check required parameters in service documentation
- Verify media player supports the service

### 8.2 Media Won't Play

**Causes**:
- Media URL not accessible
- Media type not supported by device
- Device doesn't support `PLAY_MEDIA` feature
- Network connectivity issues

**Solution**:
- Verify URL is accessible from Home Assistant
- Check supported media types for device
- Verify `supported_features` includes `PLAY_MEDIA` (512)
- Test device network connectivity

### 8.3 Volume Control Not Working

**Causes**:
- Device doesn't support `VOLUME_SET` feature
- Invalid volume_level value (must be 0.0-1.0)
- Device is muted

**Solution**:
- Check `supported_features` for `VOLUME_SET` (4)
- Use float between 0.0 and 1.0
- Check `is_volume_muted` attribute

### 8.4 Status Code 404 Entity Not Found

**Causes**:
- Entity ID doesn't exist
- Typo in entity_id
- Media player integration not set up

**Solution**:
- Verify entity exists in Home Assistant UI
- Check exact entity ID format
- Ensure media player integration is configured

---

## 9. PERFORMANCE CONSIDERATIONS

### 9.1 API Rate Limiting

- Home Assistant has built-in rate limiting
- Recommended: 1-2 requests per second for state queries
- Higher frequency polling may affect system performance

### 9.2 Polling vs. WebSocket

**State Polling** (REST API):
- GET requests for current state
- Suitable for periodic checks every 5-30 seconds
- Higher bandwidth and server load

**WebSocket** (Real-time):
- Real-time state updates
- More efficient for continuous monitoring
- Recommended for production systems

### 9.3 Automation Best Practices

- Use triggers instead of frequent polling
- Cache state information locally
- Implement exponential backoff for retries
- Monitor API response times

---

## 10. REFERENCES & DOCUMENTATION

### Official Documentation
- **Home Assistant Media Player Integration**: https://www.home-assistant.io/integrations/media_player/
- **Developer Docs - Media Player Entity**: https://developers.home-assistant.io/docs/core/entity/media-player/
- **REST API Documentation**: https://developers.home-assistant.io/docs/api/rest/

### Integration-Specific
- **Spotify Integration**: https://www.home-assistant.io/integrations/spotify/
- **Sonos Integration**: https://www.home-assistant.io/integrations/sonos/
- **Google Cast Integration**: https://www.home-assistant.io/integrations/cast/
- **Spotcast (Custom)**: https://github.com/fondberg/spotcast
- **Music Assistant**: https://www.music-assistant.io/

### Community Resources
- **Home Assistant Community Forum**: https://community.home-assistant.io/
- **Reddit r/homeassistant**: https://www.reddit.com/r/homeassistant/
- **Home Assistant Discord**: https://discord.gg/home-assistant

---

## 11. RESEARCH METHODOLOGY

This research was conducted through:

1. **Official Documentation Analysis**
   - Home Assistant developer documentation
   - Integration-specific guides
   - API reference documentation

2. **Web Search & Technical Resources**
   - Community forum discussions
   - GitHub repositories and issues
   - Blog posts and tutorials

3. **Cross-Reference Validation**
   - Multiple sources verified for consistency
   - Real-world examples from community
   - Code samples from official integrations

**Sources Consulted**:
- developers.home-assistant.io (Official Developer Docs)
- www.home-assistant.io (Official Documentation)
- community.home-assistant.io (Community Forum)
- github.com/home-assistant (Official GitHub)
- Various integration-specific documentation

---

## CONCLUSION

Home Assistant provides a comprehensive, well-documented media player integration framework that supports dozens of device types through a unified REST API. The combination of standardized service calls, flexible attribute system, and extensive device support makes it ideal for building sophisticated home entertainment automation systems. The API supports both simple playback control and advanced features like multi-room audio, media browsing, and custom sound modes.

**Key Takeaways**:
- Unified REST API across all media player types
- 20+ service calls for complete playback control
- Rich attribute system for state monitoring
- Support for multiple streaming services and protocols
- Extensible architecture for custom integrations

---

**Report Generated**: 2025-11-12
**Agent**: Claude Haiku 4.5
**Session**: Master Integration Sprint - Session 3
