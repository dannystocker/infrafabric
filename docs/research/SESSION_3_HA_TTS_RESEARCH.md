# Home Assistant Text-to-Speech (TTS) Research Report
## Session 3: Master Integration Sprint

**Research Date**: 2025-11-12
**Focus Area**: Home Assistant TTS Capabilities & Integration
**Status**: Complete

---

## Executive Summary

Home Assistant provides flexible, extensible text-to-speech capabilities through multiple service integrations, from free cloud-based solutions (Google Translate) to premium options (Google Cloud, Microsoft Azure) and local alternatives (Piper). The TTS system supports multi-language operations, advanced audio customization, intelligent caching, and seamless integration with various media players.

---

## 1. TTS SERVICE OVERVIEW

### 1.1 Modern TTS Architecture: `tts.speak` Action

The **`tts.speak`** action is the modern, recommended approach for text-to-speech in Home Assistant 2022.5+. It represents a unified service that targets specific TTS entities rather than platform-specific services.

**Key Advantages:**
- Targets specific TTS entities (entity_id based)
- Flexible media player routing
- Unified parameter structure across all TTS providers
- Superior to legacy platform-specific services
- Supports templates in message content

**Core Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `entity_id` | string | Target TTS service entity | `tts.google_cloud` |
| `message` | string | Text to synthesize (supports templates) | `"Temperature is {{states('sensor.temp')}}"` |
| `media_player_entity_id` | string | Output device | `media_player.living_room` |
| `language` | string | BCP 47 language code | `en-US`, `fr-FR` |
| `cache` | boolean | Cache synthesized audio (default: true) | `true` / `false` |
| `options` | object | Platform-specific settings | See Section 5 |

---

### 1.2 Available TTS Service Integrations

#### **Google Translate TTS** (Legacy: `tts.google_translate_say`)
- **Status**: Still functional but deprecated
- **Usage**: 90.4% of active Home Assistant installations
- **Cost**: FREE
- **Quality**: Good (natural sounding)
- **Setup**: No authentication required
- **Service Format**: `tts.google_translate_say` (legacy) or `tts.speak` (modern)
- **Best For**: Cost-sensitive deployments, broad language support

**Legacy Service Call Example:**
```yaml
action: tts.google_translate_say
data:
  entity_id: media_player.living_room
  message: "May the force be with you"
  language: "en"
```

**Modern Service Call Example:**
```yaml
action: tts.speak
target:
  entity_id: tts.google_translate
data:
  media_player_entity_id: media_player.living_room
  message: "May the force be with you"
  language: "en"
  cache: true
```

#### **Google Cloud TTS** (`tts.speak` preferred)
- **Status**: Premium, recommended
- **Cost**: Pay-per-character pricing model
- **Quality**: Highest (380+ Wavenet voices)
- **Voices Available**: 380+ across 50+ languages
- **Voice Types**: Standard, Wavenet (premium), Neural2 (latest)
- **Setup**: Requires Google Cloud credentials and billing account
- **Best For**: Production deployments requiring premium voice quality

**Configuration Example:**
```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.bedroom
  message: "Good morning, time to wake up"
  language: en-US
  options:
    gender: female
    voice: en-US-Wavenet-F
    speed: 0.95
    pitch: 0.0
    encoding: mp3
```

#### **Microsoft Azure TTS**
- **Status**: Enterprise-grade
- **Cost**: Pay-per-character
- **Quality**: Excellent (natural voices)
- **Voices**: Extensive English and multilingual support
- **Setup**: Requires Azure account and API key
- **Features**: Expressive voice styles, prosody control
- **Best For**: Enterprise environments, advanced voice customization

**Configuration Example:**
```yaml
action: tts.speak
target:
  entity_id: tts.microsoft
data:
  media_player_entity_id: media_player.kitchen
  message: "Your order has been placed"
  language: en-US
  options:
    gender: Female
    rate: 25  # percentage (-100 to +100)
    pitch: high
    volume: 70  # percentage (-100 to +100)
```

#### **Piper TTS** (Local, Free)
- **Status**: Open-source, rapidly expanding
- **Cost**: FREE
- **Quality**: Good-to-excellent (neural model)
- **Languages**: 19+ languages (continuously growing)
- **Execution**: 100% local (no cloud dependency)
- **Performance**: 1.6s voice per second on Raspberry Pi 4 (medium quality)
- **Setup**: Single-click add-on installation
- **Best For**: Privacy-focused deployments, offline-first systems, resource-constrained devices

**Configuration Example:**
```yaml
action: tts.speak
target:
  entity_id: tts.piper
data:
  media_player_entity_id: media_player.hallway
  message: "Motion detected at front door"
  language: en
  options:
    voice: en-us-amy-medium
```

**Available Piper Voices Sample:**
- English: en-us-amy-medium, en-us-libritts-high
- German: de-de-thorsten-high
- French: fr-fr-siwis-high
- Spanish: es-es-carlfm-high
- Multiple other languages with variant options

#### **Other Supported Services**
- **ElevenLabs**: Natural voices, free trial available
- **Yandex TTS**: Supports en-US, ru-RU, uk-UK, tr-TR
- **VoiceRSS**: Cloud-based alternative
- **OpenAI TTS** (Community integration): High-quality voices via OpenAI endpoint
- **Baidu TTS**: Chinese language support

---

## 2. MEDIA PLAYER ROUTING & INTEGRATION

### 2.1 Routing TTS to Specific Media Players

The `media_player_entity_id` parameter enables precise control of TTS output destination.

**Single Media Player:**
```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.living_room_speaker
  message: "Welcome home"
```

**Multiple Media Players (Array):**
```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id:
    - media_player.living_room
    - media_player.kitchen
    - media_player.bedroom
  message: "Dinner is ready"
```

**All Media Players:**
```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: all
  message: "System announcement"
```

### 2.2 Supported Media Player Types

Home Assistant TTS routes successfully to:

| Player Type | Platform Examples | Audio Format Support |
|------------|------------------|----------------------|
| Smart Speakers | Google Home, Amazon Echo, Sonos | MP3, AAC, WAV |
| Smart Displays | Google Nest Hub, Echo Show | MP3, AAC, WAV |
| Network Audio | AirPlay, UPnP/DLNA, Snapcast | MP3, OGG, WAV, FLAC |
| ESPHome Devices | Generic ESPHome speakers | Multiple (configurable) |
| Chromecast Devices | Google Cast-enabled speakers | MP3, OGG, AAC |
| Media Players | Kodi, Plex, VLC | Multiple formats |
| Custom Solutions | Custom MQTT speakers | Configurable |

### 2.3 Audio Format Compatibility & Transcoding

**Default Audio Format Support:**
- **MP3**: Most compatible (default for Google Cloud/Translate)
- **OGG/Opus**: Efficient compression
- **WAV/Linear16**: Uncompressed, highest compatibility
- **AAC**: Apple ecosystem preferred

**Transcoding with FFmpeg:**
Home Assistant automatically transcodes audio when:
- Target media player doesn't support synthesized format
- User specifies preferred format different from default
- Audio parameters incompatible with player

**Configuration for Format Preference:**
```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.living_room
  message: "System message"
  options:
    preferred_format: wav  # or mp3, ogg, flac
    preferred_sample_rate: 44100  # Hz
    preferred_sample_channels: 2  # Mono (1) or Stereo (2)
    preferred_sample_bytes: 2  # 16-bit = 2 bytes
```

### 2.4 Integration with Voice Assistants

**Piper with Wyoming Protocol:**
```yaml
# For local voice assistant deployments
action: tts.speak
target:
  entity_id: tts.piper
data:
  media_player_entity_id: media_player.voice_assistant_speaker
  message: "Voice assistant response"
```

**ESPHome Speaker Integration:**
```yaml
action: tts.speak
target:
  entity_id: tts.piper  # or other local TTS
data:
  media_player_entity_id: media_player.esphome_speaker
  message: "Smart device announcement"
```

---

## 3. MULTI-LANGUAGE SUPPORT

### 3.1 Language Code Standards

Home Assistant TTS uses standardized language codes:

**Format Standards:**
- **ISO 639-1**: Two-letter codes (en, fr, de, es)
- **BCP 47**: Extended format with region (en-US, en-GB, fr-FR)
- **Dialect Support**: Region-specific variants (es-MX, es-ES, pt-BR, pt-PT)

**Language Code Examples:**
```
en       # English (generic)
en-US    # English (United States)
en-GB    # English (United Kingdom)
fr       # French (generic)
fr-FR    # French (France)
fr-CA    # French (Canada)
es       # Spanish (generic)
es-MX    # Spanish (Mexico)
es-ES    # Spanish (Spain)
de-DE    # German
it-IT    # Italian
pt-BR    # Portuguese (Brazil)
ru-RU    # Russian
ja-JP    # Japanese
zh-CN    # Chinese (Simplified)
zh-TW    # Chinese (Traditional)
```

### 3.2 Google Translate Language Support

**Supported Languages:** All languages where "Talk" feature is enabled in Google Translate (90+ languages)

**Partial Language List:**
- **Germanic**: Afrikaans (af), German (de), Dutch (nl), Danish (da), Swedish (sv), Norwegian (no)
- **Romance**: French (fr), Spanish (es), Italian (it), Portuguese (pt), Romanian (ro)
- **Slavic**: Russian (ru), Polish (pl), Czech (cs), Ukrainian (uk), Bulgarian (bg)
- **Other European**: Greek (el), Hungarian (hu), Finnish (fi), Irish (ga), Welsh (cy)
- **Asian**: Hindi (hi), Bengali (bn), Tamil (ta), Thai (th), Korean (ko), Japanese (ja), Chinese (zh)
- **Middle Eastern**: Arabic (ar), Hebrew (he), Turkish (tr), Persian (fa)
- **African**: Swahili (sw), Zulu (zu), Afrikaans (af)

**Service Call with Language:**
```yaml
action: tts.speak
target:
  entity_id: tts.google_translate
data:
  media_player_entity_id: media_player.kitchen
  message: "Bonjour, c'est une annonce importante"
  language: fr-FR
  cache: true
```

### 3.3 Google Cloud Language Support

**Supported Languages:** 50+ with 380+ total voice variations

**Premium Voice Options by Language:**
```
English (US):
  - Standard: en-US-Standard-A/B/C/D/E
  - Neural2: en-US-Neural2-A/B/C/D/E/F
  - Wavenet: en-US-Wavenet-A/B/C/D/E/F

German:
  - de-DE-Standard-A/B/C
  - de-DE-Neural2-A/B/C
  - de-DE-Wavenet-A/B/C/D

French:
  - fr-FR-Standard-A/B/C/D
  - fr-FR-Neural2-A/B/C/D
  - fr-FR-Wavenet-A/B/C/D/E

Spanish:
  - es-ES-Standard-A/B/C
  - es-ES-Neural2-A/B/C
  - es-ES-Wavenet-A/B/C/D

Japanese:
  - ja-JP-Standard-A/B/C
  - ja-JP-Neural2-A/B
  - ja-JP-Wavenet-A/B/C/D

Chinese (Mandarin):
  - cmn-CN-Standard-A/B/C
  - cmn-CN-Neural2-A
  - cmn-CN-Wavenet-A/B/C/D

And many more...
```

**Configuration with Locale:**
```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.office
  message: "Guten Tag, die Temperatur beträgt 22 Grad"
  language: de-DE
  options:
    gender: female
    voice: de-DE-Wavenet-B
    pitch: 0.0
    speed: 1.0
```

### 3.4 Microsoft Azure Language Support

**Supported Languages:** Extensive English + multilingual

**Voice Selection by Region:**
```
en-US (English - United States): 10+ voices
en-GB (English - United Kingdom): 5+ voices
es-ES (Spanish - Spain): 4+ voices
es-MX (Spanish - Mexico): 3+ voices
fr-FR (French - France): 5+ voices
de-DE (German): 4+ voices
it-IT (Italian): 2+ voices
pt-BR (Portuguese - Brazil): 3+ voices
zh-CN (Chinese Simplified): 2+ voices
ja-JP (Japanese): 2+ voices
```

**Configuration with Voice Style:**
```yaml
action: tts.speak
target:
  entity_id: tts.microsoft
data:
  media_player_entity_id: media_player.lounge
  message: "Buenos días, ¿cómo estás?"
  language: es-ES
  options:
    gender: Female
    voice: es-ES-ElviraNeural
    rate: 0  # -50 to +50 percentage
```

### 3.5 Piper Local Language Support

**Current Languages (19+):** And growing monthly

- English (US, GB, India variants)
- German
- French
- Spanish
- Portuguese (Brazilian, European)
- Dutch
- Italian
- Russian
- Polish
- Czech
- Swedish
- Norwegian
- Danish
- Finnish
- Turkish
- Hungarian
- Romanian
- Greek
- Chinese Mandarin (and expanding)

**Multilingual Configuration:**
```yaml
action: tts.speak
target:
  entity_id: tts.piper
data:
  media_player_entity_id: media_player.bedroom
  message: "Bienvenue à notre maison intelligente"
  language: fr
  options:
    voice: fr-fr-siwis-high
```

---

## 4. TTS CACHING MECHANISM

### 4.1 Cache Overview

**Purpose:** Reduce processing overhead by storing synthesized audio for identical text requests

**Location:** Default cache directory: `config/tts/`

**Behavior:**
- Cache key is generated from: text content + language + voice settings
- Identical requests retrieve cached file instead of re-synthesizing
- Significantly reduces latency for repeated announcements
- Reduces API costs for cloud-based services

### 4.2 Cache Control

**Default Behavior:** Caching ENABLED (`cache: true`)

**Disable Caching (Force Fresh Synthesis):**
```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.living_room
  message: "Current time is {{now().strftime('%H:%M')}}"
  cache: false  # Always synthesize fresh
```

**Use Case for `cache: false`:**
- Dynamic content (time, temperature, weather)
- Real-time announcements
- Content that changes frequently
- Testing/debugging TTS

**Cache Behavior Example:**
```
Request 1: "Temperature is 22 degrees"
  → Synthesized via API/local engine
  → Stored in cache/tts/[hash].mp3
  → Latency: 2-3 seconds

Request 2: "Temperature is 22 degrees"  (same exact text)
  → Retrieved from cache/tts/[hash].mp3
  → No API call
  → Latency: <200ms
```

### 4.3 Cache Configuration

**Custom Cache Directory:**
```yaml
tts:
  cache_dir: /config/custom_tts_cache
```

**Configuration Implications:**
| Setting | Effect | Notes |
|---------|--------|-------|
| `cache: true` (default) | Audio stored after generation | Faster on repeat requests |
| `cache: false` | No storage, always regenerate | For dynamic content |
| `cache_dir` | Custom storage location | Must have write permissions |

### 4.4 Cache File Management

**Cache File Naming:**
- Files stored as `[content_hash].mp3` or `[content_hash].[format]`
- Hash derived from: text + language + speaker ID + voice settings
- Different settings = different cache files

**Cache Maintenance:**
- Home Assistant auto-cleans old cache files
- Manual clearing: Delete files from `config/tts/` directory
- No explicit cache management UI (filesystem-based)

**Monitoring Cache:**
```bash
# View cache directory
ls -la /config/tts/

# Check cache size
du -sh /config/tts/

# Clear all cache
rm -f /config/tts/*
```

### 4.5 Cache Effectiveness Analysis

**High Cache Hit Scenario (e.g., motion detection alerts):**
```yaml
# Repeated alert: "Motion detected at front door"
- First occurrence: 2.5s (synthesize)
- Subsequent: <200ms (cached)
- 10 daily alerts: 9 × 2.3s saved = 20.7s saved per day
- 365 days: ~7,600 seconds (2+ hours) saved per year
```

**Low Cache Hit Scenario (dynamic content):**
```yaml
# Temperature announcements: "Current temp is {{states('sensor.temp')}}"
# Caching ineffective due to cache: false setting
# Every request synthesized fresh
```

---

## 5. TTS CUSTOMIZATION OPTIONS

### 5.1 Google Cloud TTS Options

**Complete Parameter Set:**

```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.living_room
  message: "Good morning"
  language: en-US
  options:
    # Voice Selection
    gender: female              # male, female, or neutral
    voice: en-US-Wavenet-F      # Specific voice ID (overrides gender)

    # Audio Characteristics
    speed: 1.0                  # 0.25 (quarter speed) to 4.0 (4x speed)
    pitch: 0.0                  # -20.0 to +20.0 semitones
    gain: 0.0                   # -96.0 to +16.0 dB

    # Audio Format
    encoding: mp3               # mp3, ogg_opus, linear16
    sample_rate: 24000          # Hz (varies by encoding)

    # Advanced Options
    text_type: text             # text or ssml (SSML for markup)
    profiles: []                # Audio effect profiles (advanced)
```

**Speed & Pitch Range Table:**

| Parameter | Min | Default | Max | Use Case |
|-----------|-----|---------|-----|----------|
| Speed | 0.25x | 1.0x | 4.0x | Slow announcements (0.5), Normal (1.0), Fast alerts (1.5) |
| Pitch | -20 | 0 | +20 | Lower pitch (deeper voice), Default, Higher pitch (thinner voice) |
| Gain | -96 dB | 0 dB | +16 dB | Quieter (ambient), Normal, Louder (attention-grabbing) |

**Voice Selection Examples:**

```yaml
# Professional Female Voice
options:
  voice: en-US-Wavenet-F
  speed: 0.95
  pitch: 0.0
  gain: 0.0

# Cheerful, Faster Announcement
options:
  voice: en-US-Wavenet-C
  speed: 1.1
  pitch: 2.0
  gain: 2.0

# Deep, Authoritative Voice
options:
  gender: male
  voice: en-US-Wavenet-B
  speed: 0.9
  pitch: -3.0
  gain: 0.0

# Whisper/Ambient Mode
options:
  voice: en-US-Wavenet-E
  speed: 1.0
  pitch: 2.0
  gain: -10.0
```

### 5.2 Microsoft Azure TTS Options

**Parameter Set:**

```yaml
action: tts.speak
target:
  entity_id: tts.microsoft
data:
  media_player_entity_id: media_player.kitchen
  message: "Your package has arrived"
  language: en-US
  options:
    gender: Female              # Male or Female
    voice: AmandaNeural         # Voice identifier
    rate: 0                      # -100 (slowest) to +100 (fastest)
    pitch: 0                     # -50 (lowest) to +50 (highest)
    volume: 0                    # -100 (quietest) to +100 (loudest)
```

**Rate & Pitch Explanation:**

| Option | Range | Default | Example |
|--------|-------|---------|---------|
| rate | -100 to +100 | 0 | -25 = 75% speed, 0 = normal, 25 = 125% speed |
| pitch | -50 to +50 | 0 | -20 = lower, 0 = normal, 30 = higher |
| volume | -100 to +100 | 0 | -20 = 80% volume, 0 = normal, 30 = 130% volume |

**Available Voices by Locale:**

```
en-US Female Voices: AmandaNeural, AriaNeural, GuyNeural, JennyNeural, etc.
en-US Male Voices: BrianNeural, ChristopherNeural, etc.
en-GB: LibbyNeural, MaisieNeural, RyanNeural, Thomas
de-DE: AmalaNeural, ConradNeural, KatjaNeural
fr-FR: DeniseNeural, HenriNeural, VictoriaNeural
es-ES: AlvaroNeural, ElviraNeural, ConchitaNeural
```

**Configuration Example - Friendly Greeting:**
```yaml
options:
  voice: JennyNeural
  rate: -10
  pitch: 5
  volume: 5
```

### 5.3 Piper TTS Options

**Limited but Essential Options:**

```yaml
action: tts.speak
target:
  entity_id: tts.piper
data:
  media_player_entity_id: media_player.hallway
  message: "Motion detected in your home"
  language: en
  options:
    voice: en-us-amy-medium     # Voice variant
    # Speed/pitch not directly supported
    # Quality determined by voice variant (low/medium/high)
```

**Available Voice Variants:**

```
Quality Levels:
  - low:    Smaller model, faster processing
  - medium: Balance speed/quality (recommended)
  - high:   Best quality, more resource intensive

Example Voices:
  en-us-amy-medium
  en-us-libritts-high
  en-us-lessac-medium
  de-de-thorsten-high
  fr-fr-siwis-high
  es-es-carlfm-high
```

### 5.4 Comparative Options Matrix

| Feature | Google Cloud | Microsoft | Piper | Google Translate |
|---------|-------------|-----------|-------|------------------|
| Voice Selection | 380+ choices | 100+ choices | 19+ langs | Limited |
| Speed Control | 0.25-4.0x | -100 to +100% | Fixed per voice | None |
| Pitch Control | -20 to +20 | -50 to +50 | None | None |
| Volume Control | -96 to +16 dB | -100 to +100% | None | None |
| SSML Support | Yes | Yes (SSML) | No | No |
| Quality | Premium | High | Good | Fair |
| Cost | Pay-per-character | Pay-per-character | Free | Free |
| Privacy | Cloud-based | Cloud-based | Local | Cloud-based |

### 5.5 Advanced SSML Support (Google Cloud)

**Speech Synthesis Markup Language (SSML):**

```yaml
action: tts.speak
target:
  entity_id: tts.google_cloud
data:
  media_player_entity_id: media_player.office
  message: |
    <speak>
      <prosody pitch="-2st" rate="0.9">
        Welcome to your smart home system.
      </prosody>
      <break time="500ms"/>
      <prosody pitch="+2st" rate="1.2">
        System status: All systems nominal.
      </prosody>
    </speak>
  options:
    text_type: ssml             # Enable SSML processing
```

**SSML Elements:**
- `<prosody>`: Pitch, rate, volume control
- `<break>`: Pause duration
- `<emphasis>`: Emphasis level (strong, moderate, reduced)
- `<sub>`: Substitute pronunciation
- `<say-as>`: Format interpretation (date, time, number, currency)

---

## 6. PRACTICAL IMPLEMENTATION EXAMPLES

### 6.1 Basic Motion Alert

```yaml
automation:
  - alias: "Motion Alert - Front Door"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door_motion
      to: 'on'
    action:
      service: tts.speak
      target:
        entity_id: tts.google_cloud
      data:
        media_player_entity_id: media_player.front_porch_speaker
        message: "Motion detected at front door"
        language: en-US
        cache: true  # Reuse audio file
```

### 6.2 Dynamic Temperature Announcement

```yaml
automation:
  - alias: "Temperature Report"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      service: tts.speak
      target:
        entity_id: tts.google_cloud
      data:
        media_player_entity_id:
          - media_player.kitchen
          - media_player.bedroom
        message: "Current temperature is {{states('sensor.living_room_temp')}} degrees"
        language: en-US
        cache: false  # Dynamic content
```

### 6.3 Multi-Language Greeting

```yaml
automation:
  - alias: "Multi-Language Welcome"
    trigger:
      platform: state
      entity_id: person.alice
      to: 'home'
    action:
      service: tts.speak
      target:
        entity_id: tts.google_cloud
      data:
        media_player_entity_id: media_player.entryway
        message: "Welcome home"
        language: "{{ states('input_select.preferred_language') }}"
        # Language stored in input_select
```

### 6.4 Premium Voice Announcement

```yaml
automation:
  - alias: "Important System Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.cpu_temp
      above: 80
    action:
      service: tts.speak
      target:
        entity_id: tts.google_cloud
      data:
        media_player_entity_id: media_player.main_bedroom
        message: "WARNING: System CPU temperature critical"
        language: en-US
        cache: false
        options:
          gender: male
          voice: en-US-Wavenet-D
          speed: 0.9
          pitch: -2
          gain: 2
```

### 6.5 Local Privacy-Focused Setup

```yaml
automation:
  - alias: "Local-Only Announcement"
    trigger:
      platform: time
      at: "09:00:00"
    action:
      service: tts.speak
      target:
        entity_id: tts.piper  # All local processing
      data:
        media_player_entity_id: media_player.office_speaker
        message: "Good morning, have a productive day"
        language: en
        options:
          voice: en-us-amy-medium
```

### 6.6 Multi-Media Player Broadcast

```yaml
automation:
  - alias: "Emergency Announcement"
    trigger:
      platform: state
      entity_id: sensor.fire_alarm
      to: 'triggered'
    action:
      service: tts.speak
      target:
        entity_id: tts.google_cloud
      data:
        media_player_entity_id:
          - media_player.living_room
          - media_player.kitchen
          - media_player.bedroom
          - media_player.bathroom
        message: "ALERT: Fire alarm triggered. Evacuate immediately."
        language: en-US
        cache: false
        options:
          speed: 0.8  # Slower for clarity
          gain: 5     # Louder
```

---

## 7. SERVICE COMPARISON TABLE

| Aspect | Google Translate | Google Cloud | Microsoft | Piper | ElevenLabs |
|--------|-----------------|-------------|-----------|-------|-----------|
| **Cost** | FREE | Pay-per-char | Pay-per-char | FREE | Free tier + paid |
| **Setup** | Trivial | Google Cloud account | Azure account | One-click add-on | API key |
| **Voices** | ~50 | 380+ | 100+ | 19+ | 100+ (natural) |
| **Speed Control** | ❌ | ✅ (0.25-4.0x) | ✅ (±100%) | Limited | ✅ |
| **Pitch Control** | ❌ | ✅ (-20 to +20) | ✅ (±50%) | ❌ | Limited |
| **Cache Support** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Privacy** | Cloud | Cloud | Cloud | Local | Cloud |
| **Quality** | Good | Premium | High | Good | Excellent |
| **Reliability** | Excellent | Excellent | Excellent | Excellent | Good |
| **Languages** | 90+ | 50+ | 50+ | 19+ | 30+ |
| **Best For** | Budget | Premium, Production | Enterprise | Privacy | Natural voices |

---

## 8. TROUBLESHOOTING GUIDE

### 8.1 Audio Not Playing

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Media player offline | Device not connected | Verify device connectivity; check Home Assistant logs |
| Format incompatibility | Player doesn't support format | Try different encoding in options (mp3, wav, ogg) |
| FFmpeg missing | Transcoding unavailable | Install FFmpeg add-on |
| Incorrect entity_id | Wrong player specified | Verify exact entity_id in Services Developer Tools |
| Network connectivity | Connection dropped | Check network stability; enable offline caching |

### 8.2 Cache Issues

```yaml
# Force cache refresh (if audio not updating)
action: tts.speak
data:
  cache: false  # Bypass cache, synthesize fresh

# Then restore caching
cache: true
```

### 8.3 Language Not Working

**Verification Steps:**
1. Confirm language code valid (check official docs)
2. Test in Google Translate directly (google_translate test)
3. Verify TTS service supports language
4. Check logs for specific error messages

---

## 9. INTEGRATION ROADMAP

### Recommended Multi-Service Setup:

```yaml
# configuration.yaml
tts:
  cache_dir: /config/tts

automation: !include automations.yaml
```

**Service Selection Strategy:**
- **Quick alerts**: Google Translate (free, instant)
- **Important announcements**: Google Cloud (premium voices)
- **Privacy-critical**: Piper (local processing)
- **Multilingual support**: Google Cloud or Microsoft
- **Budget-conscious**: Google Translate + Piper hybrid

---

## 10. RESEARCH CONCLUSION

### Key Findings:

1. **Modern TTS Architecture**: `tts.speak` action with entity-based targeting provides superior flexibility to legacy services

2. **Service Diversity**: Home Assistant supports a wide spectrum from free cloud solutions (Google Translate) to premium options (Google Cloud, Microsoft) to fully local (Piper)

3. **Language Support**: 90+ languages available across services; BCP 47 standard provides regional variants

4. **Audio Customization**: Google Cloud offers most granular control (speed 0.25-4.0x, pitch ±20, gain ±96dB); Microsoft offers percentage-based controls

5. **Caching Benefits**: Intelligently deployed caching can reduce latency 10-15x for repeated announcements while supporting dynamic content via `cache: false`

6. **Media Player Flexibility**: TTS routes seamlessly to single or multiple players; FFmpeg transcoding ensures format compatibility

7. **Local-First Alternative**: Piper TTS enables fully offline operation with 19+ languages, sacrificing some voice quality for privacy

### Recommended Implementation Path:

**Phase 1 (Quick Start)**: Deploy Google Translate for basic announcements
**Phase 2 (Enhancement)**: Add Piper for privacy-critical alerts
**Phase 3 (Premium)**: Integrate Google Cloud for important announcements requiring premium voices
**Phase 4 (Optimization)**: Fine-tune caching strategy and media player routing

---

**Report Generated**: 2025-11-12
**Research Status**: COMPLETE
**Next Steps**: Implementation planning and service configuration

---

## References & Resources

- **Official Docs**: https://www.home-assistant.io/integrations/tts/
- **Google Cloud TTS**: https://www.home-assistant.io/integrations/google_cloud/
- **Google Translate TTS**: https://www.home-assistant.io/integrations/google_translate/
- **Microsoft TTS**: https://www.home-assistant.io/integrations/microsoft/
- **Piper TTS**: https://www.home-assistant.io/voice_control/using_tts_in_automation/
- **Developer Docs**: https://developers.home-assistant.io/docs/core/entity/tts/
- **Piper Project**: https://github.com/rhasspy/piper
