# OBS Studio Media Source Types & WebSocket Control
## Session 3 Master Integration Sprint Research Report

**Platform**: OBS Studio
**Research Date**: November 12, 2025
**Protocol Version**: obs-websocket 5.x
**OBS Version**: 28+

---

## Table of Contents
1. [Media Source Types](#media-source-types)
2. [WebSocket API Commands](#websocket-api-commands)
3. [Media Playback Control](#media-playback-control)
4. [Looping & Playlist Management](#looping--playlist-management)
5. [Supported Formats](#supported-formats)
6. [Complete Usage Examples](#complete-usage-examples)

---

## Media Source Types

OBS Studio supports multiple input types for multimedia content. The key media-related source types are:

### 1. **ffmpeg_source** (Media/Video Source)
The primary source type for playing video files and audio files.

**Input Kind**: `ffmpeg_source`

**Supported on**: Windows, macOS, Linux

**Key Features**:
- Video file playback
- Audio file playback
- Remote stream support (RTMP, RTSP, HTTP streams)
- Hardware decoding support
- Speed control (1%-200%)
- Playback looping

**Default Settings**:
```json
{
  "buffering_mb": 2,
  "clear_on_media_end": true,
  "is_local_file": true,
  "linear_alpha": false,
  "looping": false,
  "reconnect_delay_sec": 10,
  "restart_on_activate": true,
  "speed_percent": 100
}
```

### 2. **image_source** (Single Image Source)
Displays a static or animated image in a scene.

**Input Kind**: `image_source`

**Supported on**: Windows, macOS, Linux

**Key Features**:
- Single image display
- Animated GIF support
- Transparency support
- Unload when hidden option

**Available Settings**:
```json
{
  "file": "/path/to/image.png",
  "unload": false
}
```

### 3. **slideshow** (Image Slideshow Source)
Automated image sequencing with transitions.

**Input Kind**: `slideshow`

**Supported on**: Windows, macOS, Linux

**Key Features**:
- Multiple image display
- Automatic or manual slide progression
- Transition effects
- Randomization option
- Loop control

**Default Settings**:
```json
{
  "files": [],
  "loop": true,
  "randomize": false,
  "slide_mode": "mode_auto",
  "slide_time": 8000,
  "transition": "fade",
  "transition_speed": 700,
  "playback_behavior": "always_play",
  "hide": false,
  "use_custom_size": false
}
```

### 4. **vlc_source** (VLC Video Source)
Uses VLC libraries for extended media format support and playlist functionality.

**Input Kind**: `vlc_source`

**Supported on**: Windows, macOS, Linux (requires VLC installation - must match system architecture)

**Key Features**:
- Extended format support via VLC
- Playlist management
- Shuffle support
- Loop support
- Audio track selection
- Subtitle support
- Network caching

---

## WebSocket API Commands

### CreateInput Request

Used to create new media sources in OBS via WebSocket.

**Request Format**:
```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Scene Name",
    "inputName": "New Input Name",
    "inputKind": "ffmpeg_source",
    "inputSettings": {
      "local_file": "/path/to/video.mp4",
      "looping": true,
      "restart_on_activate": true
    }
  }
}
```

**Required Parameters**:
- `sceneName` (string): Target scene for the input
- `inputName` (string): Name of the new input
- `inputKind` (string): Type of input to create
- `inputSettings` (object): Configuration specific to input type

**Response**:
```json
{
  "requestStatus": {
    "result": true,
    "code": 0,
    "comment": "Success"
  },
  "responseData": {
    "inputUuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
}
```

### SetInputSettings Request

Modifies settings of existing inputs.

**Request Format**:
```json
{
  "requestType": "SetInputSettings",
  "requestData": {
    "inputName": "Media Source",
    "inputSettings": {
      "looping": true,
      "speed_percent": 100
    }
  }
}
```

### GetInputDefaultSettings Request

Retrieve default settings for a specific input kind.

**Request Format**:
```json
{
  "requestType": "GetInputDefaultSettings",
  "requestData": {
    "inputKind": "ffmpeg_source"
  }
}
```

**Use Case**: Discover all available inputSettings options for a given input type before creating or configuring it.

---

## Media Playback Control

### TriggerMediaInputAction Request

Controls playback of media inputs (ffmpeg_source, vlc_source).

**Request Format**:
```json
{
  "requestType": "TriggerMediaInputAction",
  "requestData": {
    "inputName": "MediaSource",
    "mediaAction": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY"
  }
}
```

### Available Media Actions

| Action | Enum Constant | Description |
|--------|---------------|-------------|
| **Play** | `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY` | Resume/start playback |
| **Pause** | `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE` | Pause playback (maintain position) |
| **Stop** | `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP` | Stop playback (reset to beginning) |
| **Restart** | `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART` | Restart from beginning |
| **Next** | `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NEXT` | Skip to next playlist item |
| **Previous** | `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PREVIOUS` | Skip to previous playlist item |

### Media Position Control Requests

#### SetMediaInputCursor
Set the playback position to a specific time.

**Request Format**:
```json
{
  "requestType": "SetMediaInputCursor",
  "requestData": {
    "inputName": "MediaSource",
    "mediaCursor": 5000
  }
}
```
- `mediaCursor`: Time in milliseconds

#### OffsetMediaInputCursor
Adjust playback position by a relative amount.

**Request Format**:
```json
{
  "requestType": "OffsetMediaInputCursor",
  "requestData": {
    "inputName": "MediaSource",
    "mediaCursorOffset": 1000
  }
}
```

### GetMediaInputStatus Request

Query current playback state.

**Request Format**:
```json
{
  "requestType": "GetMediaInputStatus",
  "requestData": {
    "inputName": "MediaSource"
  }
}
```

**Response Example**:
```json
{
  "responseData": {
    "mediaDuration": 120000,
    "mediaCursor": 45000,
    "mediaState": "OBS_MEDIA_STATE_PLAYING"
  }
}
```

---

## Looping & Playlist Management

### Media Looping

#### For ffmpeg_source (Single Video/Audio)
Set the `looping` parameter in CreateInput or SetInputSettings:

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Main",
    "inputName": "LoopingVideo",
    "inputKind": "ffmpeg_source",
    "inputSettings": {
      "local_file": "/videos/intro.mp4",
      "looping": true,
      "restart_on_activate": true
    }
  }
}
```

**Related Settings**:
- `looping` (boolean): Enable automatic restart after playback ends
- `restart_on_activate` (boolean): Restart when source becomes visible
- `clear_on_media_end` (boolean): Hide source when playback finishes

#### For slideshow Source
Set the `loop` parameter:

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "Gallery",
    "inputName": "ImageShow",
    "inputKind": "slideshow",
    "inputSettings": {
      "files": [
        "/images/slide1.png",
        "/images/slide2.png",
        "/images/slide3.png"
      ],
      "loop": true,
      "slide_time": 5000,
      "transition": "fade",
      "transition_speed": 500
    }
  }
}
```

**Slideshow Loop Settings**:
- `loop` (boolean): Enable looping
- `randomize` (boolean): Randomize slide order
- `slide_mode` (string): `"mode_auto"` or `"mode_manual"` (manual requires OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NEXT/PREVIOUS)
- `playback_behavior` (string): `"always_play"`, `"pause_unpause"`, or `"stop_restart"`

### Playlist Management (VLC Source)

The VLC source supports playlist functionality through the `playlist` parameter:

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "PlaylistScene",
    "inputName": "VLCPlaylist",
    "inputKind": "vlc_source",
    "inputSettings": {
      "playlist": [
        {
          "value": "/videos/video1.mp4"
        },
        {
          "value": "/videos/video2.mp4"
        },
        {
          "value": "/videos/video3.mp4"
        }
      ],
      "loop": true,
      "shuffle": false
    }
  }
}
```

**Playlist Features**:
- `loop` (boolean): Loop the entire playlist
- `shuffle` (boolean): Randomize playlist order
- Navigate using `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NEXT` and `OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PREVIOUS`

---

## Supported Formats

### Video Formats

#### ffmpeg_source (Media Source)
Supported video container formats:

| Format | Extension | Codec Support |
|--------|-----------|---------------|
| MP4 | `.mp4` | H.264, H.265, VP9 |
| Matroska | `.mkv` | All codecs |
| MPEG-TS | `.ts` | H.264, MPEG2 |
| MOV | `.mov` | H.264, ProRes |
| FLV | `.flv` | H.264, Sorenson |
| AVI | `.avi` | MPEG4, DivX, Xvid |
| WebM | `.webm` | VP8, VP9, AV1 |
| GIF | `.gif` | Animated images |

#### Video Codecs Supported
- **H.264/AVC**: MPEG-4 Part 10 (most compatible)
- **H.265/HEVC**: High Efficiency Video Coding
- **VP9**: Google video codec
- **AV1**: Open-source modern codec (requires OBS 29+)
- **MPEG-2**: Legacy support

#### Recommended Encoding for OBS Media Source
For best compatibility and performance:
```
Video Codec: H.264 (x264)
Audio Codec: AAC
Container: MP4 or MKV
Bitrate: 4000-8000 kbps (1080p), 10000+ kbps (4K)
Frame Rate: 24fps, 30fps, or 60fps
```

### Audio Formats

#### ffmpeg_source (Media Source)
Supported audio formats:

| Format | Extension | Codec |
|--------|-----------|-------|
| MP3 | `.mp3` | MPEG-1 Audio Layer III |
| AAC | `.aac` | Advanced Audio Coding |
| OGG Vorbis | `.ogg` | Vorbis |
| WAV | `.wav` | PCM, various codecs |
| FLAC | `.flac` | Free Lossless Audio |
| OPUS | `.opus` | Opus (WebM) |

### Image Formats

#### image_source and slideshow
Supported image formats:

| Format | Extension | Features |
|--------|-----------|----------|
| PNG | `.png` | Lossless, transparency support |
| JPEG | `.jpg`, `.jpeg` | Lossy compression |
| BMP | `.bmp` | Uncompressed bitmap |
| TGA | `.tga` | Truevision Targa |
| GIF | `.gif` | Animated GIF support |

#### Recommended Image Settings
```
PNG: For lossless quality and transparency
JPEG: For efficient file size with good quality (use quality 90+)
Size: 1920x1080 or smaller for streaming
Animation: GIF support is available (10-12fps recommended)
```

### Format Limitations & Best Practices

**Local vs Remote Files**:
- Local files: Set `is_local_file: true` in ffmpeg_source (default)
- Remote streams: Set `is_local_file: false` for RTMP, RTSP, HTTP streams
- Remote reconnection: Automatic with `reconnect_delay_sec` (default 10 seconds)

**Hardware Decoding**:
- Enable for better CPU performance with high-bitrate files
- Available for H.264, H.265, VP9 (depending on GPU)
- Setting: Available through OBS settings interface

**Playback Speed Control**:
- Range: 1% to 200%
- Default: 100%
- Set via `speed_percent` in CreateInput or SetInputSettings

---

## Complete Usage Examples

### Example 1: Create Video File Source with Looping

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "StreamScene",
    "inputName": "IntroVideo",
    "inputKind": "ffmpeg_source",
    "inputSettings": {
      "local_file": "/home/user/videos/intro_720p.mp4",
      "looping": true,
      "restart_on_activate": true,
      "clear_on_media_end": false,
      "speed_percent": 100,
      "is_local_file": true
    }
  }
}
```

### Example 2: Create Image Slideshow

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "GalleryScene",
    "inputName": "PhotoSlideshow",
    "inputKind": "slideshow",
    "inputSettings": {
      "files": [
        {
          "value": "/images/photo1.png"
        },
        {
          "value": "/images/photo2.jpg"
        },
        {
          "value": "/images/photo3.png"
        }
      ],
      "slide_time": 4000,
      "transition": "fade",
      "transition_speed": 600,
      "loop": true,
      "randomize": false,
      "slide_mode": "mode_auto",
      "playback_behavior": "always_play"
    }
  }
}
```

### Example 3: Create Single Image Source

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "OverlayScene",
    "inputName": "Logo",
    "inputKind": "image_source",
    "inputSettings": {
      "file": "/images/logo.png",
      "unload": false
    }
  }
}
```

### Example 4: Media Playback Control Sequence

```javascript
// Play media
{
  "requestType": "TriggerMediaInputAction",
  "requestData": {
    "inputName": "IntroVideo",
    "mediaAction": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY"
  }
}

// Get status
{
  "requestType": "GetMediaInputStatus",
  "requestData": {
    "inputName": "IntroVideo"
  }
}

// Jump to 30 seconds
{
  "requestType": "SetMediaInputCursor",
  "requestData": {
    "inputName": "IntroVideo",
    "mediaCursor": 30000
  }
}

// Pause
{
  "requestType": "TriggerMediaInputAction",
  "requestData": {
    "inputName": "IntroVideo",
    "mediaAction": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE"
  }
}

// Restart
{
  "requestType": "TriggerMediaInputAction",
  "requestData": {
    "inputName": "IntroVideo",
    "mediaAction": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"
  }
}
```

### Example 5: VLC Source with Playlist

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "PlaybackScene",
    "inputName": "VideoPlaylist",
    "inputKind": "vlc_source",
    "inputSettings": {
      "playlist": [
        {
          "value": "/media/segment1.mp4"
        },
        {
          "value": "/media/segment2.mp4"
        },
        {
          "value": "rtmp://stream.example.com/live/stream1"
        }
      ],
      "loop": true,
      "shuffle": false
    }
  }
}
```

### Example 6: Remote Stream Source

```json
{
  "requestType": "CreateInput",
  "requestData": {
    "sceneName": "StreamScene",
    "inputName": "RemoteStream",
    "inputKind": "ffmpeg_source",
    "inputSettings": {
      "local_file": "http://example.com/stream/live.m3u8",
      "is_local_file": false,
      "reconnect_delay_sec": 10,
      "restart_on_activate": true
    }
  }
}
```

### Example 7: Python Implementation with obs-websocket-py

```python
import obswebsocket

# Connect to OBS
client = obswebsocket.obsws("localhost", 4455, "password")
client.connect()

# Create media source
request = {
    "sceneName": "Main",
    "inputName": "IntroVideo",
    "inputKind": "ffmpeg_source",
    "inputSettings": {
        "local_file": "/videos/intro.mp4",
        "looping": True
    }
}
client.call(obswebsocket.requests.CreateInput(**request))

# Play media
client.call(obswebsocket.requests.TriggerMediaInputAction(
    inputName="IntroVideo",
    mediaAction="OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY"
))

# Get media status
status = client.call(obswebsocket.requests.GetMediaInputStatus(
    inputName="IntroVideo"
))
print(f"Duration: {status.datain['mediaDuration']}ms")
print(f"Position: {status.datain['mediaCursor']}ms")
print(f"State: {status.datain['mediaState']}")

# Pause after 5 seconds
import time
time.sleep(5)
client.call(obswebsocket.requests.TriggerMediaInputAction(
    inputName="IntroVideo",
    mediaAction="OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE"
))

client.disconnect()
```

---

## Protocol Version & Compatibility

### Requirements
- **OBS Studio**: Version 28 or later
- **obs-websocket**: Version 5.0 or later
- **WebSocket Port**: 4455 (default, configurable)
- **Authentication**: Password-based with SHA256 hash

### Deprecation Notes
- obs-websocket 4.x used `SetSourceSettings` instead of `SetInputSettings`
- obs-websocket 4.x used "Source" terminology; 5.x uses "Input" terminology
- Media action control requires OBS v25.0.8 or later

---

## Key Implementation Considerations

1. **Media Source Type Selection**:
   - Use `ffmpeg_source` for single or multiple video/audio files
   - Use `image_source` for static images
   - Use `slideshow` for automated image sequences
   - Use `vlc_source` only if extended format support or playlists are critical

2. **Local vs Remote Files**:
   - Always specify `is_local_file: true/false` appropriately
   - Remote sources use reconnection logic automatically
   - Test stream URLs before deploying to production

3. **Performance Optimization**:
   - Preload media files when possible
   - Use hardware decoding for high-bitrate content
   - Set appropriate looping policies to minimize CPU overhead

4. **Error Handling**:
   - Implement retry logic for remote streams
   - Monitor `GetMediaInputStatus` for playback state changes
   - Handle long playback times with cursor positioning instead of restart

5. **Format Recommendations**:
   - **Video**: H.264 + AAC in MP4 container
   - **Audio**: AAC at 128-256 kbps
   - **Images**: PNG for quality/transparency, JPEG for efficiency
   - **Containers**: MKV for maximum compatibility, MP4 for streaming

---

## References & Additional Resources

- **Official OBS WebSocket Protocol**: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
- **OBS Media Sources KB**: https://obsproject.com/kb/media-sources
- **OBS Audio/Video Formats Guide**: https://obsproject.com/kb/audio-video-formats-guide
- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html
- **obs-websocket-py**: Python client library for WebSocket API
- **obs-cmd**: Terminal CLI for obs-websocket v5

---

**End of Research Report**
