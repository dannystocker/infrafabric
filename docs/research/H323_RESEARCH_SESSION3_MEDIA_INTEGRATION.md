# Home Assistant Audio/Video Source Management Research
## Session 3 Master Integration Sprint - Haiku Research Report

**Date**: November 12, 2025
**Research Duration**: 20-30 minutes
**Platform**: Home Assistant
**Focus**: Media Source Browsing, Local Media Files, URL Streaming, Radio/Podcast Integration, Media Metadata

---

## Executive Summary

Home Assistant provides a comprehensive media source platform that enables browsing, streaming, and managing audio/video content from multiple sources including local files, external URLs, radio stations, and podcast feeds. The platform uses a unified URI scheme (`media-source://`) for accessing content and provides developer APIs for building custom media source integrations.

**Key Capabilities**:
- Local media file browsing from `/media` directory
- External URL/stream support via Media Extractor
- Radio station directory access via Radio Browser integration
- Podcast management through Music Assistant and Pocket Casts
- Metadata exposure through media player attributes
- Authentication-protected media serving

---

## 1. Media Source Browser Architecture

### Core Integration

The **Media Source** integration is the foundation for accessing all media in Home Assistant. It automatically configures through `default_config` or manual entry:

```yaml
media_source:
```

### Browser Interface

Users access media through:
- **UI Path**: Home Assistant sidebar > **Media** section
- **Available Sources**:
  - Local Media (local files)
  - Radio Browser (internet radio)
  - Music Assistant (music, audiobooks, podcasts)
  - Custom integration sources

### Media Source URI Scheme

All media access uses a standardized URI format:

```
media-source://media_source/<media_dir>/<path>
```

**Example URIs**:
```
media-source://media_source/local/Music/Artist/Album/track.mp3
media-source://media_source/recordings/security_footage.mp4
media-source://media_source/podcasts/episode.m4a
```

### Developer API Methods

The Media Player entity provides these core discovery methods:

```python
# Async browse media content tree
async_browse_media(media_content_type, media_content_id)

# Search across media sources
async_search_media(query, media_content_type)

# Get browse images (album art, thumbnails)
async_get_browse_image(media_content_type, media_content_id)
```

**Feature Flags** (25+ available):
- `PLAY`, `PAUSE`, `STOP`
- `SEEK`, `PREVIOUS_TRACK`, `NEXT_TRACK`
- `TURN_ON`, `TURN_OFF`, `VOLUME_SET`, `VOLUME_MUTE`
- `SELECT_SOURCE`, `SELECT_SOUND_MODE`
- `BROWSE_MEDIA`, `PLAY_MEDIA`

---

## 2. Local Media Files Management

### Directory Structure

**Default Location**: `/media`

For different Home Assistant installations:

| Installation Type | Default Path | Docker Mount |
|-------------------|--------------|--------------|
| Home Assistant OS | `/media` | N/A (built-in) |
| Supervised | `/media` | N/A (built-in) |
| Container | `/media` | `-v /PATH_TO_YOUR_MEDIA:/media` |
| Core (Manual) | `~/.homeassistant/media/` | Manual setup |

### Configuration

**Single Media Directory** (default):
```yaml
# Requires no explicit configuration, uses /media by default
media_source:
```

**Multiple Media Directories**:
```yaml
homeassistant:
  media_dirs:
    local: /media
    recording: /mnt/recordings
    archive: /mnt/storage/archive
    podcasts: /mnt/podcasts
```

This creates browsable folders in the media browser:
- Local Media > local
- Local Media > recording
- Local Media > archive
- Local Media > podcasts

### File Management

**Supported Methods**:

1. **Via Media Browser UI**:
   - Navigate to **Media** > **Local Media**
   - Click **Manage** (top right corner)
   - Upload, rename, or delete files

2. **Via File System**:
   - Use Samba add-on (Home Assistant OS/Supervised)
   - Mount volume (Docker)
   - Direct filesystem access (Core)

### Supported Media Types

The integration supports any format natively supported by the media player or web browser:
- **Audio**: MP3, WAV, FLAC, AAC, OGG, M4A
- **Video**: MP4, WebM, MKV, AVI (browser/device dependent)

**Important**: Media is **not transcoded**. Files must be in formats supported by the target playback device.

### Security

Unlike `/www` files, local media files are **protected by Home Assistant authentication**:
- Direct file access requires valid authentication
- Media URLs include authentication tokens
- Suitable for private/personal media

---

## 3. URL Streaming & External Media Sources

### Media Player URL Streaming

Play external media streams directly on any media player:

```yaml
# Via service call in automation
service: media_player.play_media
data:
  media_content_id: "https://example.com/stream.mp3"
  media_content_type: "music"
target:
  entity_id: media_player.living_room_speaker
```

**Supported Content Types**:
- `music` - Audio streams
- `video` - Video streams
- `playlist` - M3U/PLS playlists
- `channel` - Live streams
- `episode` - Podcast episodes

### Media Extractor Integration

The **Media Extractor** integration extracts playable stream URLs from various sources:

```yaml
media_extractor:
```

**Two Main Actions**:

1. **Play Media** - Downloads and plays content:
```yaml
service: media_extractor.play_media
data:
  media_player: media_player.living_room_speaker
  url: "https://www.youtube.com/watch?v=VIDEO_ID"
  # Optional: specify stream quality
  extra_parameters: "bestvideo"  # or "best", "bestaudio", etc.
```

2. **Extract URL** - Returns stream URL for manual playback:
```yaml
service: media_extractor.get_url
data:
  url: "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Format Selection Options**:
- `best` - Best combined video + audio
- `bestvideo` - Best video stream only
- `bestaudio` - Best audio stream only
- Custom youtube-dl format specifications

### Authentication Support

For authenticated streams (Twitch Turbo, private YouTube):

```yaml
media_extractor:
  authentication:
    - url_pattern: "twitch.tv"
      cookie_file: /path/to/cookies.txt  # Netscape format
```

### Stream Integration

The **Stream** integration proxies live streams through Home Assistant:

```yaml
stream:
```

Automatically used by:
- Camera integration (video feeds)
- Media players streaming from URLs
- Custom integrations handling live content

---

## 4. Radio & Podcast Integration

### Radio Browser Integration

Provides access to 40,000+ radio stations from the Radio Browser directory.

**Setup**:
```yaml
radio_browser:
```

**Usage**:
1. Navigate to **Media** > **Radio Browser** in Home Assistant
2. Browse by country, genre, or search for stations
3. Click a station to play on selected speaker
4. Add to automations for scheduled playback

**Automation Example**:
```yaml
automation:
  - alias: "Morning Radio Routine"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      service: media_player.play_media
      data:
        media_content_id: "BBC Radio 1"  # Station name or ID
        media_content_type: "channel"
      target:
        entity_id: media_player.kitchen_speaker
```

**Coverage**: Approximately 80% of active Home Assistant installations use this integration.

### Podcast Integration: Music Assistant

**Music Assistant** is the primary podcast platform in Home Assistant (native integration since 2024.12):

**Features**:
- Native podcast feed support
- Audiobook browsing and playback
- Music streaming across multiple services
- Offline playback support
- Queue management
- Smart playlists

**Setup**:
```yaml
# Auto-configures if not explicitly disabled
music_assistant:
```

**Podcast Management**:
1. Navigate to **Media** > **Music Assistant**
2. Browse podcasts by feed, category, or search
3. Add podcasts to library
4. Configure playback device
5. Control via media player actions

**Podcast Integration Features**:
- Automatic feed updates
- Episode tracking (played/unplayed)
- Bookmarking favorite episodes
- Speed control
- Resume playback

### Pocket Casts Integration

Integrates with the Pocket Casts podcast platform:

```yaml
pocketcasts:
```

**Requirements**: Pocket Casts+ Plus subscription

**Features**:
- Sensor for unplayed episode count per podcast
- Access to subscribed podcasts
- Integration with Home Assistant automations

**Usage Example**:
```yaml
template:
  - sensor:
      - name: "Podcast Status"
        state: "{{ state_attr('sensor.pocketcasts_unplayed_count', 'podcasts') }}"
        unit_of_measurement: "episodes"
```

### Custom Podcast Integration: gPodder

GitHub community component for podcast feed monitoring:

- GitHub: `custom-components/gpodder`
- Exposes gPodder API
- Shows podcast info
- Service-based automation triggers

---

## 5. Media Metadata Access

### Media Player Attributes

Media player entities expose comprehensive metadata through state attributes:

```yaml
# Access in templates
media_title: "{{ state_attr('media_player.entity_name', 'media_title') }}"
media_artist: "{{ state_attr('media_player.entity_name', 'media_artist') }}"
media_album_name: "{{ state_attr('media_player.entity_name', 'media_album_name') }}"
media_duration: "{{ state_attr('media_player.entity_name', 'media_duration') }}"
media_position: "{{ state_attr('media_player.entity_name', 'media_position') }}"
media_content_id: "{{ state_attr('media_player.entity_name', 'media_content_id') }}"
media_content_type: "{{ state_attr('media_player.entity_name', 'media_content_type') }}"
```

### Metadata Types

Home Assistant supports metadata objects for different content:

```python
# Available metadata object types:
- GenericMediaMetadata (default)
- MusicTrackMediaMetadata (artist, album, genre, duration)
- MovieMediaMetadata (director, release_date, plot)
- TvShowMediaMetadata (series_name, season, episode)
- PhotoMediaMetadata (date_taken, location)
```

### Template Example: Display Now Playing

```yaml
template:
  - sensor:
      - name: "Current Playing"
        state: >
          {%- if not is_state('media_player.speaker', 'off') -%}
          {{ state_attr('media_player.speaker', 'media_title') }}
          {%- else -%}
          No media playing
          {%- endif -%}
        attributes:
          artist: "{{ state_attr('media_player.speaker', 'media_artist') }}"
          album: "{{ state_attr('media_player.speaker', 'media_album_name') }}"
          duration: "{{ state_attr('media_player.speaker', 'media_duration') }}"
          position: "{{ state_attr('media_player.speaker', 'media_position') }}"
```

### Lovelace Card Display

```yaml
type: media-control
entity: media_player.living_room_speaker
```

Displays:
- Current track title
- Artist name
- Album art
- Playback controls
- Duration/position indicator

### Metadata Retrieval Timing

**Important Note**: Metadata may appear with significant delay (sometimes 30+ seconds after playback starts), depending on the specific media player integration. This is integration-dependent.

---

## 6. Implementation Architecture

### Media Source Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│          Home Assistant Media Browser UI             │
│  (Media > Local Media / Radio Browser / Music)      │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴──────────┬──────────────────┐
         │                    │                  │
    ┌────v─────────────────────v────────────────v─────────────┐
    │        Media Source Integration Platform                │
    │  • Media Source (core)                                  │
    │  • Radio Browser (integrations)                         │
    │  • Music Assistant (integrations)                       │
    └────┬──────────┬────────────────┬───────────────────────┘
         │          │                │
    ┌────v──┐  ┌────v──────┐  ┌────v────────┐
    │ Local │  │  Radio    │  │   Music     │
    │ Media │  │  Browser  │  │  Assistant  │
    │ /media│  │  Directory│  │  Metadata   │
    └────┬──┘  └────┬──────┘  └────┬────────┘
         │          │              │
    ┌────v─────────v──────────────v───────────────┐
    │   URI Resolution & Authentication            │
    │ media-source://media_source/local/...       │
    └────┬────────────────────────────────────────┘
         │
    ┌────v────────────────────────────────────────────────────┐
    │        Media Player Entities & Services                 │
    │ • play_media / async_play_media                         │
    │ • browse_media / async_browse_media                     │
    │ • Media player attributes (metadata)                    │
    │ • Chromecast, Sonos, AirPlay, etc.                      │
    └─────────────────────────────────────────────────────────┘
```

### Content Type Support Matrix

| Source | Type | Format | Streaming | Metadata | Auth |
|--------|------|--------|-----------|----------|------|
| Local Media | Audio/Video | Any (native) | No | Yes | HA Auth |
| Radio Browser | Audio | Stream | Yes | Limited | No |
| Music Assistant | Audio/Podcast | Stream | Yes | Full | Integration |
| Media Extractor | Audio/Video | Stream | Yes | Limited | Optional |
| Pocket Casts | Audio/Podcast | Stream | Yes | Full | Subscription |
| URL Direct | Audio/Video | Stream | Yes | Limited | Optional |

---

## 7. Advanced Use Cases & Integration Patterns

### Use Case 1: Morning Routine Automation

```yaml
automation:
  - alias: "Morning Media Routine"
    trigger:
      platform: time
      at: "07:00:00"
    action:
      - service: media_player.play_media
        data:
          media_content_id: "BBC Radio 1"
          media_content_type: "channel"
        target:
          entity_id: media_player.bedroom_speaker
      - delay: "00:30:00"  # Play for 30 minutes
      - service: media_player.media_stop
        target:
          entity_id: media_player.bedroom_speaker
```

### Use Case 2: Podcast Queue Automation

```yaml
automation:
  - alias: "Queue Latest Podcast"
    trigger:
      platform: time_pattern
      hours: "6,12,18"  # 6 AM, noon, 6 PM
    action:
      service: media_player.play_media
      data:
        media_content_id: "Latest Episode: My Favorite Podcast"
        media_content_type: "episode"
      target:
        entity_id: media_player.kitchen_speaker
```

### Use Case 3: Dynamic Media Display

```yaml
template:
  - sensor:
      - name: "Media Control Status"
        unique_id: "media_status_display"
        state: >
          {%- set player = states.media_player.living_room -%}
          {%- if player.state == 'playing' -%}
          🎵 Playing: {{ state_attr('media_player.living_room', 'media_title') }}
          {%- elif player.state == 'paused' -%}
          ⏸️ Paused: {{ state_attr('media_player.living_room', 'media_title') }}
          {%- else -%}
          ⏹️ Idle
          {%- endif -%}
```

### Use Case 4: Metadata-Based Automation

```yaml
automation:
  - alias: "Skip if Artist"
    trigger:
      platform: state
      entity_id: media_player.living_room
      attribute: media_artist
    condition:
      template: "{{ trigger.to_state.attributes.media_artist == 'Artist Name' }}"
    action:
      service: media_player.media_next_track
      target:
        entity_id: media_player.living_room
```

---

## 8. Configuration Best Practices

### Optimal Media Directory Structure

```
/media/
├── Music/
│   ├── Artist1/
│   │   └── Album1/
│   │       └── track1.mp3
│   └── Artist2/
│       └── track2.m4a
├── Podcasts/
│   ├── Podcast1/
│   │   └── episode1.m4a
│   └── Podcast2/
│       └── episode2.mp3
├── Videos/
│   ├── Movies/
│   │   └── movie.mp4
│   └── Recordings/
│       └── recording.mkv
└── Audiobooks/
    └── book.m4a
```

### Configuration Best Practices

```yaml
# configuration.yaml - Optimal setup
homeassistant:
  # Define multiple media directories
  media_dirs:
    local: /media
    music: /mnt/music
    podcasts: /mnt/podcasts
    videos: /mnt/videos
    archive: /nas/archive

# Enable all media integrations
media_source:

radio_browser:

music_assistant:

media_extractor:

# Optional: custom podcast integration
custom_components:
  gpodder:
    enabled: true
```

### Docker Compose Setup

```yaml
version: '3.8'
services:
  home-assistant:
    image: homeassistant/home-assistant:latest
    volumes:
      - ./config:/config
      - /mnt/media:/media         # Local media
      - /mnt/music:/mnt/music     # Music library
      - /mnt/podcasts:/mnt/podcasts  # Podcasts
      - /recordings:/recordings    # Recordings
    ports:
      - "8123:8123"
```

---

## 9. Performance Considerations

### Media Browsing Optimization

- **Lazy Loading**: Media browser loads directories on demand
- **Caching**: Metadata cached at player level
- **Indexing**: Consider organizing large libraries by artist/album
- **Network**: Stream URLs should be accessible from all playback devices

### File Format Recommendations

| Use Case | Format | Bitrate | Notes |
|----------|--------|---------|-------|
| Music | MP3/AAC | 320kbps | Universal support |
| Audiobooks | M4A/FLAC | 128-192kbps | Quality sufficient |
| Podcasts | MP3/M4A | 64-128kbps | Bandwidth efficient |
| Video | MP4/WebM | Variable | Browser/device dependent |

### Bandwidth Management

```yaml
# Limit concurrent streams
stream:
  ll_hls: false  # Use standard HLS for better compatibility

# Audio codec preferences
music_assistant:
  preferred_quality: "192"  # kbps for streaming
```

---

## 10. Troubleshooting & Common Issues

### Issue: Media Title/Artist Not Showing

**Cause**: Metadata delay from integration (30+ seconds)

**Solution**:
```yaml
# Add template with delay/fallback
template:
  - sensor:
      - name: "Safe Media Title"
        state: >
          {%- set title = state_attr('media_player.entity', 'media_title') -%}
          {{ title | default('Loading...') }}
        availability: "{{ not is_state('media_player.entity', 'off') }}"
```

### Issue: Media Source URI Scheme Error

**Cause**: Incorrect URI format or missing authentication

**Solution**:
```yaml
# Use correct format with media_source:// scheme
service: media_player.play_media
data:
  media_content_id: "media-source://media_source/local/Music/file.mp3"
  media_content_type: "music"
```

### Issue: Local Media Not Playing

**Cause**:
- Unsupported file format
- No transcoding available
- Device doesn't support format

**Solution**:
```yaml
# Verify file format compatibility
# Convert if necessary: ffmpeg -i input.avi -c:v libx264 output.mp4
# Test on device capabilities
```

### Issue: Radio Browser Connection

**Cause**: Network connectivity or API throttling

**Solution**:
```yaml
# Check network access
# Reduce refresh rate if needed
radio_browser:
  # Add any needed configuration
```

---

## 11. Security Considerations

### Authentication & Access Control

- **Protected by Default**: `/media` files require Home Assistant authentication
- **Token-Based**: Media URLs include authentication tokens
- **URL Limitation**: Tokens expire and are device-specific

### Podcast Feed Security

- **Feed Validation**: Music Assistant validates podcast feed sources
- **DRM Protection**: Respect podcast DRM restrictions
- **Authentication**: Support for authenticated feeds via cookies

### Best Practices

```yaml
# 1. Use strong Home Assistant authentication
homeassistant:
  # Configure secure access via reverse proxy

# 2. Limit external URL access
media_extractor:
  # Only enable trusted URL schemes

# 3. Secure API tokens
# - Use environment variables for sensitive data
# - Rotate tokens regularly
```

---

## 12. Integration Roadmap & Future Capabilities

### Currently Available
- Local media browsing
- Radio station streaming
- Podcast management (Music Assistant)
- Metadata exposure
- Media queuing

### Future Enhancements (Community Requests)
- Advanced search across all sources
- Collaborative playlists
- Scrobbling/integration with music services
- Enhanced metadata from online services
- Media library analytics

---

## Conclusion

Home Assistant provides a robust, extensible media source platform that supports:

1. **Local Media Browsing** via `/media` directories with authentication protection
2. **URL Streaming** through Media Extractor with format selection
3. **Radio Integration** via Radio Browser (40,000+ stations)
4. **Podcast Support** through Music Assistant (primary) and Pocket Casts
5. **Rich Metadata** via media player attributes (title, artist, duration, etc.)

The unified `media-source://` URI scheme and comprehensive developer APIs enable seamless integration of various media sources into Home Assistant automations, templates, and UIs.

Key advantages:
- **Unified Interface**: Single UI for all media types
- **Authentication-Protected**: Secure media serving
- **No Transcoding**: Direct playback support
- **Automation-Ready**: Scriptable via services and automations
- **Extensible**: Custom integrations via media source platform

---

## Research Resources

**Official Documentation**:
- Media Source: https://www.home-assistant.io/integrations/media_source/
- Media Player: https://www.home-assistant.io/integrations/media_player/
- Radio Browser: https://www.home-assistant.io/integrations/radio_browser/
- Music Assistant: https://github.com/music-assistant/hass-music-assistant
- Media Extractor: https://www.home-assistant.io/integrations/media_extractor/

**Developer API**:
- Media Player Entity: https://developers.home-assistant.io/docs/core/entity/media-player/
- Media Source Platform: https://developers.home-assistant.io/docs/core/platform/media_source/

**Community Resources**:
- Home Assistant Forum: https://community.home-assistant.io/
- Home Assistant Podcast: https://hasspodcast.io/

---

**Report Generated**: November 12, 2025 | Session 3 Master Integration Sprint
