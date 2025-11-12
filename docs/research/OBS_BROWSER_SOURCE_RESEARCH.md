# OBS Studio Browser Source Capabilities Research Report
**Session 3: Master Integration Sprint - Haiku Research Agent**

**Research Date**: 2025-11-12
**Topics**: Browser Source Basics, WebSocket Integration, HTML Overlays, JavaScript API, Refresh Control
**Duration**: 20-30 minutes

---

## Executive Summary

OBS Browser Source is a powerful cross-platform feature powered by **CEF (Chromium Embedded Framework)** that allows integration of web-based overlays into OBS Studio. Browser sources can load external URLs, local HTML files, or inline HTML/CSS/JavaScript, providing flexibility for creating dynamic overlays, dashboards, and interactive elements. The functionality is accessible via the WebSocket API (obs-websocket) and native JavaScript API (window.obsstudio).

---

## 1. Browser Source Basics

### What is a Browser Source?

A **Browser Source** is an OBS input source that renders web content (HTML/CSS/JavaScript) using the Chromium Embedded Framework. This allows streamers and content creators to integrate web pages, custom overlays, and dynamic content directly into their OBS scenes.

### Key Characteristics

- **CEF-Based Rendering**: Uses Chromium Embedded Framework for reliable, modern web rendering
- **Native OBS Integration**: Full access to OBS API from within the browser context
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Built-In Support**: Included with OBS Studio v28 and above
- **Lightweight**: More efficient than alternative overlay methods

### Core Features

| Feature | Description |
|---------|-------------|
| **URL Loading** | Load external websites or local HTML files |
| **Custom CSS** | Apply CSS rules to override loaded page styling |
| **JavaScript API** | Access OBS functionality via `window.obsstudio` |
| **Local File Support** | Use `file://` protocol or "Local File" checkbox |
| **Permission Control** | Fine-grained access levels from NONE to ALL |
| **WebSocket Integration** | Remote control via obs-websocket API |

### Creating a Browser Source

**Via OBS UI**:
1. Right-click scene → Add Source → Browser
2. Enter URL or enable "Local File" and browse to HTML
3. Set width/height (typically 1920x1080 or 1280x720)
4. Optional: Add custom CSS in the CSS field
5. Enable "Interact" if you need JavaScript interactivity

---

## 2. WebSocket Commands: CreateInput with browser_source

### CreateInput Request Overview

The **CreateInput** request in obs-websocket allows programmatic creation of browser sources. This is essential for automation, remote control, and dynamic overlay management.

### Basic CreateInput Syntax

```javascript
await obs.call("CreateInput", {
  sceneName: "Main Scene",
  inputName: "custom-overlay",
  inputKind: "browser_source",
  inputSettings: {
    url: "https://example.com/overlay.html",
    width: 1920,
    height: 1080,
    css: "",
    is_local_file: false,
    fps: 30
  }
});
```

### CreateInput Parameters for browser_source

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| **sceneName** | string | Target scene name | "Main Scene" |
| **inputName** | string | Name for the source | "alert-overlay" |
| **inputKind** | string | Must be "browser_source" | "browser_source" |
| **inputSettings** | object | Browser-specific config | See below |

### inputSettings Parameters

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| **url** | string | "" | URL or file path to load |
| **is_local_file** | boolean | false | Load local file vs. remote URL |
| **width** | integer | 1920 | Source width in pixels |
| **height** | integer | 1080 | Source height in pixels |
| **fps** | integer | 30 | Frame rate (0-60) |
| **css** | string | "" | Custom CSS to inject |
| **shutdown** | boolean | false | Shutdown when hidden |
| **refresh_on_scene_show** | boolean | false | Refresh on scene activation |

### CreateInput Examples

#### Example 1: Load External URL

```javascript
const obs = new OBSWebSocket();
await obs.connect('ws://localhost:4455', 'password');

await obs.call("CreateInput", {
  sceneName: "Gaming",
  inputName: "twitch-chat",
  inputKind: "browser_source",
  inputSettings: {
    url: "https://www.twitch.tv/embed/channelname/chat?parent=example.com",
    width: 400,
    height: 720,
    fps: 30
  }
});
```

#### Example 2: Load Local HTML File

```javascript
await obs.call("CreateInput", {
  sceneName: "Overlay Scene",
  inputName: "local-timer",
  inputKind: "browser_source",
  inputSettings: {
    url: "file:///C:/StreamAssets/timer.html",
    is_local_file: true,
    width: 1920,
    height: 1080
  }
});
```

#### Example 3: Inline HTML with Data URI

```javascript
await obs.call("CreateInput", {
  sceneName: "Alert Scene",
  inputName: "donation-alert",
  inputKind: "browser_source",
  inputSettings: {
    url: "data:text/html,<html><body style='background:transparent'>" +
         "<h1 style='color:gold'>New Donation!</h1></body></html>",
    width: 800,
    height: 200
  }
});
```

#### Example 4: With Custom CSS

```javascript
await obs.call("CreateInput", {
  sceneName: "Main",
  inputName: "styled-overlay",
  inputKind: "browser_source",
  inputSettings: {
    url: "https://example.com/overlay",
    width: 1920,
    height: 1080,
    css: `
      * { font-family: 'Arial', sans-serif; }
      .widget { background: rgba(0,0,0,0.7); }
      .title { color: #00ff00; font-size: 32px; }
    `
  }
});
```

### obs-websocket Connection Setup

```javascript
const OBSWebSocket = require('obs-websocket-js').default;
const obs = new OBSWebSocket();

// Connect to OBS (default port 4455)
obs.connect({
  address: 'localhost:4455',
  password: 'your_password' // Set in OBS Tools > WebSocket Server Settings
}).then(() => {
  console.log('Connected to OBS');
}).catch(err => {
  console.error('Failed to connect:', err);
});

// Listen for events
obs.on('ConnectionClosed', () => {
  console.log('Disconnected from OBS');
});
```

---

## 3. URL-Based Content Loading

### Loading External URLs

Browser sources can load any valid HTTP/HTTPS URL, enabling integration with web services, APIs, and third-party platforms.

#### Common Use Cases

1. **Twitch Embed**
   ```
   https://www.twitch.tv/embed/channelname/chat?parent=example.com
   ```

2. **YouTube Embed**
   ```
   https://www.youtube.com/embed/VIDEO_ID
   ```

3. **Stream Labs Alerts**
   ```
   https://alerts.streamlabs.com/overlay/SOCKET_TOKEN
   ```

4. **Custom Web Dashboard**
   ```
   https://myserver.com/overlay?stream=live&theme=dark
   ```

### Loading Local HTML Files

#### Method 1: File Path (Recommended)

```
file:///C:/StreamAssets/overlay.html
file:///home/user/streaming/overlay.html  (Linux)
file:///Users/username/streaming/overlay.html  (macOS)
```

#### Method 2: Using Local File Checkbox

1. Enable "Local File" checkbox in browser source settings
2. Click "Browse" button
3. Select your HTML file

#### Method 3: Relative to HTML File

```html
<!-- In overlay.html -->
<img src="assets/logo.png">  <!-- Loads assets/logo.png relative to HTML file -->
<link rel="stylesheet" href="styles.css">
```

### Passing Parameters to Local Files

```
file:///C:/StreamAssets/timer.html?hours=1&minutes=30&seconds=0
file:///home/user/overlay.html?username=streamer&theme=dark
```

In the HTML file:

```javascript
const params = new URLSearchParams(window.location.search);
const username = params.get('username') || 'Guest';
const theme = params.get('theme') || 'light';
```

### Security Considerations

- **CEF Restrictions**: Chromium Embedded Framework has built-in security restrictions
- **CORS Policy**: Cross-origin resource sharing follows browser standards
- **Local File Access**: May require workarounds for accessing other local resources
- **Mixed Content**: HTTPS pages cannot load HTTP resources

#### Workaround for Local File Access

If you need to access local files from within a browser source, use a local HTTP server:

```bash
# Python 3
python -m http.server 8000 --directory C:/StreamAssets

# Node.js
npx http-server ./StreamAssets -p 8000
```

Then load via `http://localhost:8000/overlay.html`

---

## 4. Custom HTML/CSS Overlays

### Creating Custom Overlays from Scratch

#### Basic HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Arial', sans-serif;
            overflow: hidden;
        }

        .container {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .overlay {
            padding: 20px;
            background: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
            color: #ffffff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="overlay">
            <h1>Stream Overlay</h1>
            <p>This is a custom overlay</p>
        </div>
    </div>
</body>
</html>
```

### Custom CSS Features

#### Transparent Background

```css
body {
    background: transparent;
    margin: 0;
    padding: 0;
}
```

#### Animations

```css
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-100%);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.alert {
    animation: slideIn 0.5s ease-in-out;
}
```

#### Glowing Text Effect

```css
.glow-text {
    color: #fff;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.8),
                 0 0 20px rgba(100, 200, 255, 0.6);
    font-size: 48px;
    font-weight: bold;
}
```

#### Gradient Background

```css
.gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
}
```

### Example: Donation Alert Overlay

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: transparent;
            margin: 0;
            overflow: hidden;
        }

        .alert-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0;
            animation: popIn 0.5s ease-out forwards;
        }

        @keyframes popIn {
            0% {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.5);
            }
            50% {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1.1);
            }
            100% {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1);
            }
        }

        .alert-box {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            text-align: center;
            min-width: 400px;
        }

        .amount {
            font-size: 72px;
            font-weight: bold;
            margin: 20px 0;
            text-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
        }

        .message {
            font-size: 24px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="alert-container">
        <div class="alert-box">
            <h2>New Donation!</h2>
            <div class="amount">$50.00</div>
            <div class="message">Thanks for the support!</div>
        </div>
    </div>
</body>
</html>
```

### Example: Animated Bottom Bar

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: transparent;
            margin: 0;
            overflow: hidden;
        }

        .bottom-bar {
            position: fixed;
            bottom: 0;
            width: 100%;
            height: 100px;
            background: linear-gradient(90deg, #1a1a2e, #16213e, #0f3460);
            border-top: 3px solid #e94560;
            display: flex;
            align-items: center;
            padding: 0 30px;
            box-sizing: border-box;
        }

        .info-block {
            flex: 1;
            color: white;
            font-size: 24px;
            text-align: center;
        }

        .info-label {
            color: #e94560;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .info-value {
            font-size: 36px;
            font-weight: bold;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="bottom-bar">
        <div class="info-block">
            <div class="info-label">Viewers</div>
            <div class="info-value" id="viewers">1,234</div>
        </div>
        <div class="info-block">
            <div class="info-label">Followers</div>
            <div class="info-value" id="followers">5,678</div>
        </div>
        <div class="info-block">
            <div class="info-label">Uptime</div>
            <div class="info-value" id="uptime">2:34:15</div>
        </div>
    </div>

    <script>
        // Update uptime every second
        function updateUptime() {
            // Your uptime logic here
        }
        setInterval(updateUptime, 1000);
    </script>
</body>
</html>
```

### CSS Injection via OBS Settings

You can add custom CSS directly in the browser source settings without modifying the HTML:

```css
/* Hide specific elements */
.unwanted-element { display: none; }

/* Override colors */
.title { color: #00ff00 !important; }

/* Add shadows */
* { text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }

/* Custom fonts (if available) */
body { font-family: 'Courier New', monospace; }
```

---

## 5. JavaScript Interaction in Browser Sources

### window.obsstudio API

The **window.obsstudio** object provides JavaScript access to OBS functionality from within browser sources.

#### API Methods

| Method | Purpose | Permission Required |
|--------|---------|-------------------|
| **getStatus()** | Get current OBS status | READ_OBS |
| **getScenes()** | List all scenes | READ_OBS |
| **getCurrentScene()** | Get active scene | READ_OBS |
| **setCurrentScene(name)** | Switch to scene | ADVANCED |
| **startRecording()** | Start recording | ALL |
| **stopRecording()** | Stop recording | ALL |
| **startStreaming()** | Start stream | ALL |
| **stopStreaming()** | Stop stream | ALL |
| **startReplayBuffer()** | Start replay buffer | BASIC |
| **stopReplayBuffer()** | Stop replay buffer | BASIC |
| **saveReplayBuffer()** | Save current replay | BASIC |
| **startVirtualcam()** | Start virtual camera | ALL |
| **stopVirtualcam()** | Stop virtual camera | ALL |
| **getCurrentTransition()** | Get active transition | READ_OBS |
| **getTransitions()** | List transitions | READ_OBS |
| **setCurrentTransition(name)** | Set transition | ADVANCED |
| **getControlLevel()** | Get permission level | - |

#### Permission Levels

| Level | Capabilities |
|-------|--------------|
| **NONE** | No access |
| **READ_OBS** | Read-only access to OBS state |
| **READ_USER** | Access to user information |
| **BASIC** | Replay buffer control |
| **ADVANCED** | Scene/transition changes |
| **ALL** | Full unrestricted access |

### Event Listeners

Monitor OBS events using standard `addEventListener()`:

```javascript
// Scene change event
window.addEventListener('obsSceneChanged', function(event) {
    console.log('Switched to scene:', event.detail.name);
    // Update overlay based on scene
});

// Streaming started
window.addEventListener('obsStreamingStarted', function(event) {
    console.log('Stream started');
    document.getElementById('status').textContent = 'LIVE';
});

// Recording started
window.addEventListener('obsRecordingStarted', function(event) {
    console.log('Recording started');
});

// Scene item visibility changed
window.addEventListener('obsSceneItemVisibilityChanged', function(event) {
    console.log('Item visibility:', event.detail);
});
```

### Complete Example: Interactive Control Panel

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: #1a1a2e;
            color: white;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }

        .control-panel {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }

        button {
            padding: 15px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .record-btn {
            background: #e74c3c;
            color: white;
        }

        .record-btn:hover {
            background: #c0392b;
        }

        .stream-btn {
            background: #27ae60;
            color: white;
        }

        .stream-btn:hover {
            background: #229954;
        }

        .status {
            padding: 10px;
            margin-top: 20px;
            border-radius: 5px;
            background: #2c3e50;
        }

        .live {
            color: #e74c3c;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="control-panel">
        <button class="stream-btn" id="streamBtn">Start Stream</button>
        <button class="record-btn" id="recordBtn">Start Recording</button>
        <button id="replayBtn">Save Replay</button>
        <button id="sceneBtn">Switch Scene</button>
    </div>

    <div class="status" id="status">
        Status: Offline
    </div>

    <script>
        const streamBtn = document.getElementById('streamBtn');
        const recordBtn = document.getElementById('recordBtn');
        const replayBtn = document.getElementById('replayBtn');
        const sceneBtn = document.getElementById('sceneBtn');
        const statusDiv = document.getElementById('status');

        // Update status on startup
        function updateStatus() {
            if (typeof window.obsstudio !== 'undefined') {
                window.obsstudio.getStatus(function(status) {
                    let statusText = 'Status: ';
                    if (status.streaming) {
                        statusText += '<span class="live">LIVE</span> | ';
                    }
                    if (status.recording) {
                        statusText += '<span class="live">RECORDING</span>';
                    }
                    if (!status.streaming && !status.recording) {
                        statusText += 'Offline';
                    }
                    statusDiv.innerHTML = statusText;
                });
            }
        }

        streamBtn.addEventListener('click', function() {
            if (typeof window.obsstudio !== 'undefined') {
                window.obsstudio.getStatus(function(status) {
                    if (status.streaming) {
                        window.obsstudio.stopStreaming();
                        streamBtn.textContent = 'Start Stream';
                    } else {
                        window.obsstudio.startStreaming();
                        streamBtn.textContent = 'Stop Stream';
                    }
                    updateStatus();
                });
            }
        });

        recordBtn.addEventListener('click', function() {
            if (typeof window.obsstudio !== 'undefined') {
                window.obsstudio.getStatus(function(status) {
                    if (status.recording) {
                        window.obsstudio.stopRecording();
                        recordBtn.textContent = 'Start Recording';
                    } else {
                        window.obsstudio.startRecording();
                        recordBtn.textContent = 'Stop Recording';
                    }
                    updateStatus();
                });
            }
        });

        replayBtn.addEventListener('click', function() {
            if (typeof window.obsstudio !== 'undefined') {
                window.obsstudio.saveReplayBuffer();
                alert('Replay buffer saved!');
            }
        });

        // Scene switching
        sceneBtn.addEventListener('click', function() {
            if (typeof window.obsstudio !== 'undefined') {
                window.obsstudio.getScenes(function(scenes) {
                    const currentScene = prompt('Select scene:',
                        scenes.map(s => s.name).join(', '));
                    if (currentScene) {
                        window.obsstudio.setCurrentScene(currentScene);
                    }
                });
            }
        });

        // Listen to scene changes
        window.addEventListener('obsSceneChanged', function(event) {
            console.log('Scene changed to:', event.detail.name);
            updateStatus();
        });

        window.addEventListener('obsStreamingStarted', function() {
            streamBtn.textContent = 'Stop Stream';
            updateStatus();
        });

        window.addEventListener('obsStreamingStopped', function() {
            streamBtn.textContent = 'Start Stream';
            updateStatus();
        });

        window.addEventListener('obsRecordingStarted', function() {
            recordBtn.textContent = 'Stop Recording';
            updateStatus();
        });

        window.addEventListener('obsRecordingStopped', function() {
            recordBtn.textContent = 'Start Recording';
            updateStatus();
        });

        // Initial status check
        updateStatus();
    </script>
</body>
</html>
```

### TypeScript Support

For TypeScript projects, install type definitions:

```bash
npm install --save-dev @types/obs-studio
```

Then use typed OBS interactions:

```typescript
interface OBSStatus {
    streaming: boolean;
    recording: boolean;
    paused: boolean;
}

if (typeof window.obsstudio !== 'undefined') {
    window.obsstudio.getStatus((status: OBSStatus) => {
        console.log('Stream active:', status.streaming);
    });
}
```

---

## 6. Refresh Control

### Built-In Refresh Options

#### Option 1: Refresh Browser When Scene Becomes Active

In the browser source settings, enable "Refresh Browser When Scene Becomes Active" to reload the content when switching to the scene.

**Use Case**: Static overlays that don't maintain state
**Caution**: Not suitable for timers or persistent counters

#### Option 2: Shutdown When Hidden

Enable "Shutdown When Hidden" to pause rendering when the source is not visible, reducing CPU usage.

#### Option 3: Custom Refresh Interval

Add this to your HTML to auto-refresh periodically:

```html
<!-- Refresh every 5 minutes (300 seconds) -->
<meta http-equiv="refresh" content="300">

<!-- Refresh every 10 seconds -->
<meta http-equiv="refresh" content="10">

<!-- Refresh and redirect -->
<meta http-equiv="refresh" content="10;url=https://example.com/new-page">
```

### JavaScript-Based Refresh

#### Location Reload

```javascript
// Refresh the current page
window.location.reload();

// Refresh without cache
window.location.reload(true);

// Schedule automatic refresh
setInterval(() => {
    window.location.reload();
}, 300000); // Refresh every 5 minutes
```

#### Dynamic Content Updates (Recommended)

Instead of refreshing the page, update content dynamically:

```javascript
// Fetch new data and update DOM
async function updateContent() {
    const response = await fetch('/api/overlay-data');
    const data = await response.json();

    document.getElementById('viewers').textContent = data.viewers;
    document.getElementById('followers').textContent = data.followers;
}

// Update every 30 seconds
setInterval(updateContent, 30000);

// Initial load
updateContent();
```

### WebSocket-Based Refresh Control

Use obs-websocket to trigger refreshes remotely:

```javascript
const OBSWebSocket = require('obs-websocket-js').default;
const obs = new OBSWebSocket();

await obs.connect('ws://localhost:4455', 'password');

// Set a browser source to refresh when scene becomes active
await obs.call("SetInputSettings", {
    inputName: "my-overlay",
    inputSettings: {
        refresh_on_scene_show: true
    }
});
```

### Lua Script Refresh (Advanced)

OBS Lua scripts can trigger refreshes:

```lua
-- refresh-browser-sources.lua
local obs = obslua

function refresh_sources()
    local sources = obs.obs_enum_sources()

    for _, source in ipairs(sources) do
        local source_id = obs.obs_source_get_id(source)
        if source_id == "browser_source" then
            -- Trigger refresh button press
            local properties = obs.obs_source_properties(source)
            -- Set refresh property
        end
    end

    obs.source_list_release(sources)
end

obs.obs_register_hotkey({
    name = "refresh_all_browsers",
    description = "Refresh all browser sources",
    callback = refresh_sources
})
```

### Poll-Based Refresh Pattern

```javascript
// Poll server for updates and refresh only if content changed
let lastVersion = null;

async function smartRefresh() {
    try {
        const response = await fetch('/api/version');
        const data = await response.json();

        if (data.version !== lastVersion) {
            lastVersion = data.version;
            window.location.reload();
        }
    } catch (error) {
        console.error('Refresh check failed:', error);
    }
}

// Check every 30 seconds
setInterval(smartRefresh, 30000);
```

### Controlled Refresh with obs-websocket

```javascript
const OBSWebSocket = require('obs-websocket-js').default;

async function refreshBrowserSource(sourceName) {
    const obs = new OBSWebSocket();

    try {
        await obs.connect('ws://localhost:4455');

        // Get current source settings
        const settings = await obs.call("GetInputSettings", {
            inputName: sourceName
        });

        // Force refresh by toggling visibility or updating URL
        await obs.call("SetInputSettings", {
            inputName: sourceName,
            inputSettings: {
                ...settings.inputSettings,
                url: settings.inputSettings.url + '?t=' + Date.now()
            }
        });

        console.log('Browser source refreshed');
    } finally {
        await obs.disconnect();
    }
}

// Usage
refreshBrowserSource('my-overlay');
```

---

## Best Practices & Recommendations

### Performance Optimization

1. **Lower Frame Rates**: Set FPS to 30 or lower unless you need 60
2. **Shutdown When Hidden**: Enable to reduce CPU usage
3. **Lazy Loading**: Load assets only when visible
4. **Minimize CSS**: Use efficient selectors and avoid complex animations
5. **Debounce Updates**: Throttle API calls and DOM updates

### Security Considerations

1. **HTTPS Only**: Use HTTPS for external URLs
2. **Input Validation**: Sanitize any user input in overlays
3. **Permission Levels**: Request minimum necessary permissions
4. **Local Files**: Be cautious with file access, use local HTTP server
5. **Cross-Origin**: Be aware of CORS restrictions

### Development Workflow

1. **Prototype in Browser**: Test HTML/CSS/JS in Chrome first
2. **Chrome DevTools**: Open with F12 in OBS browser source
3. **Git Version Control**: Keep overlays in version control
4. **Local Server**: Use local HTTP server for testing
5. **CSS Snippets**: Maintain library of reusable CSS effects

### Common Patterns

```javascript
// Pattern 1: Debounced API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const debouncedUpdate = debounce(() => {
    updateContent();
}, 1000);

// Pattern 2: Safe OBS API access
function safeOBSCall(callback) {
    if (typeof window.obsstudio !== 'undefined') {
        callback();
    } else {
        console.warn('OBS API not available');
    }
}

// Pattern 3: Reactive updates
class OverlayManager {
    constructor() {
        this.state = {};
        this.listeners = [];
    }

    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notifyListeners();
    }

    subscribe(callback) {
        this.listeners.push(callback);
    }

    notifyListeners() {
        this.listeners.forEach(cb => cb(this.state));
    }
}
```

---

## Key Resources

### Official Documentation
- **OBS Browser GitHub**: https://github.com/obsproject/obs-browser
- **obs-websocket Protocol**: https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
- **OBS Studio Docs**: https://docs.obsproject.com/

### JavaScript Libraries
- **obs-websocket-js**: https://www.npmjs.com/package/obs-websocket-js
- **@types/obs-studio**: TypeScript definitions for OBS API

### Example Projects
- **revochen/obs-html-overlay**: https://github.com/revochen/obs-html-overlay
- **spenibus/obs-overlay-html-js**: https://github.com/spenibus/obs-overlay-html-js
- **deltoidgg/overlay-animations**: https://github.com/deltoidgg/overlay-animations

### Community
- **OBS Forums**: https://obsproject.com/forum/
- **OBS Discord**: Official OBS community Discord server

---

## Summary

OBS Browser Source is a versatile tool for creating dynamic, interactive overlays. Key capabilities include:

✓ **CEF-Based Rendering** for modern web content
✓ **WebSocket API** for remote programmatic control
✓ **JavaScript API** for direct OBS integration
✓ **Custom CSS** for styling and branding
✓ **Flexible Content Loading** from URLs, files, or inline HTML
✓ **Refresh Control** via multiple methods
✓ **Permission-Based Access** for security

Whether building simple static overlays or complex interactive dashboards, browser sources provide the flexibility and power needed for professional streaming and content creation.

---

**Research Completed**: 2025-11-12
**Total Investigation Time**: ~25 minutes
**Coverage**: 6 Major Topics + Best Practices + Resources
