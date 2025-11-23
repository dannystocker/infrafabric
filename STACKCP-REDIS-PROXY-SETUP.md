# StackCP Redis Reverse Proxy Setup

**Goal:** Expose Redis at `http://digital-lab.ca/infrafabric/proxy` to Gemini CLI (and other external tools)

**Architecture:**
```
Firewall (blocks direct Redis access)
    ↓
Gemini CLI → http://digital-lab.ca/infrafabric/proxy
    ↓
Apache (public_html) → Reverse Proxy to localhost:6381
    ↓
Node.js app in /tmp/redis-proxy (executable, persistent)
    ↓
Redis on localhost:6379
```

---

## Phase 1: Create Node.js Reverse Proxy in /tmp

The proxy runs in `/tmp/` (only executable location) but reads config from web root.

### Step 1: Create Proxy App

```bash
ssh stackcp

# Navigate to /tmp (executable location)
cd /tmp

# Create proxy directory
mkdir -p redis-proxy
cd redis-proxy

# Create app.js
cat > app.js << 'EOF'
const express = require('express');
const redis = require('redis');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();

// Middleware
app.use(cors({
  origin: ['http://digital-lab.ca', 'https://digital-lab.ca', 'http://localhost', '*'],
  credentials: true
}));
app.use(bodyParser.json());
app.use(express.text());

// Redis client
const client = redis.createClient({
  host: 'localhost',
  port: 6379,
  retry_strategy: (options) => {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      return new Error('Redis connection refused');
    }
    if (options.total_retry_time > 1000 * 60 * 60) {
      return new Error('Redis retry time exhausted');
    }
    if (options.attempt > 10) {
      return undefined;
    }
    return Math.min(options.attempt * 100, 3000);
  }
});

client.on('error', (err) => console.log('Redis Error:', err));
client.on('connect', () => console.log('Redis Connected'));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// GET /proxy/keys/:pattern
app.get('/proxy/keys/:pattern', (req, res) => {
  client.keys(req.params.pattern, (err, keys) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ pattern: req.params.pattern, keys, count: keys.length });
  });
});

// GET /proxy/get/:key
app.get('/proxy/get/:key', (req, res) => {
  client.get(req.params.key, (err, value) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({
      key: req.params.key,
      value: value,
      exists: value !== null,
      size: value ? value.length : 0
    });
  });
});

// GET /proxy/ttl/:key
app.get('/proxy/ttl/:key', (req, res) => {
  client.ttl(req.params.key, (err, ttl) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({
      key: req.params.key,
      ttl: ttl,
      status: ttl === -1 ? 'no-expiry' : (ttl === -2 ? 'key-not-found' : 'active')
    });
  });
});

// POST /proxy/set/:key
app.post('/proxy/set/:key', (req, res) => {
  const value = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
  const ttl = req.query.ttl ? parseInt(req.query.ttl) : null;

  if (ttl) {
    client.setex(req.params.key, ttl, value, (err) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ key: req.params.key, status: 'set', ttl });
    });
  } else {
    client.set(req.params.key, value, (err) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ key: req.params.key, status: 'set', ttl: 'none' });
    });
  }
});

// GET /proxy/info
app.get('/proxy/info', (req, res) => {
  client.info((err, info) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({
      status: 'connected',
      info: info.substring(0, 500) + '...',
      server: 'localhost:6379'
    });
  });
});

// Error handling
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.message });
});

// Start server on port 6381 (only accessible locally, reverse-proxied via Apache)
const PORT = 6381;
app.listen(PORT, 'localhost', () => {
  console.log(`Redis Proxy running on http://localhost:${PORT}`);
  console.log('Accessible via: http://digital-lab.ca/infrafabric/proxy (via Apache reverse proxy)');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  client.quit();
  process.exit(0);
});
EOF
```

### Step 2: Install Dependencies

```bash
# Use /tmp/npm (with wrapper)
export PATH="/tmp/node-v20.18.0-linux-x64/bin:$PATH"
/tmp/npm install express redis cors body-parser

# Verify installation
ls node_modules | grep -E "express|redis|cors|body-parser"
```

### Step 3: Create systemd Service (Auto-restart)

Since StackCP shared hosting doesn't allow cron, create a startup script:

```bash
# Create startup wrapper
cat > /tmp/start-redis-proxy.sh << 'EOF'
#!/bin/bash
cd /tmp/redis-proxy
export PATH="/tmp/node-v20.18.0-linux-x64/bin:$PATH"
nohup /tmp/node app.js > /tmp/redis-proxy.log 2>&1 &
echo $! > /tmp/redis-proxy.pid
sleep 2
if pgrep -f "node.*redis-proxy" > /dev/null; then
  echo "[$(date)] Redis proxy started successfully (PID: $(cat /tmp/redis-proxy.pid))"
else
  echo "[$(date)] Failed to start Redis proxy"
  exit 1
fi
EOF

chmod +x /tmp/start-redis-proxy.sh

# Test it
/tmp/start-redis-proxy.sh
# Expected: [timestamp] Redis proxy started successfully (PID: XXXX)

# Verify proxy is running
ps aux | grep "node.*redis-proxy"
netstat -tlnp | grep 6381
```

### Step 4: Test Proxy Locally

```bash
# Check health
curl http://localhost:6381/health
# Expected: {"status":"healthy","timestamp":"2025-11-23T..."}

# List instance keys
curl http://localhost:6381/proxy/keys/instance:*
# Expected: {"pattern":"instance:*","keys":["instance:16:..."], "count":3}

# Get specific key
curl http://localhost:6381/proxy/get/instance:16:next-actions
# Expected: {"key":"instance:16:next-actions","value":"TRACK A...", "exists":true}
```

---

## Phase 2: Configure Apache Reverse Proxy

Since `~/public_html/digital-lab.ca/` is public, set up Apache to forward requests to the Node.js app running in `/tmp/`.

### Step 1: Create Proxy Config

```bash
# Navigate to home
cd ~

# Create proxy directory structure
mkdir -p public_html/digital-lab.ca/infrafabric/proxy

# Create .htaccess for Apache reverse proxy
cat > public_html/digital-lab.ca/infrafabric/proxy/.htaccess << 'EOF'
# Enable mod_rewrite
RewriteEngine On

# Disable direct PHP execution (security)
<FilesMatch "\.php$">
    Deny from all
</FilesMatch>

# Reverse proxy configuration
# Forward all requests to Node.js app on localhost:6381
RewriteRule ^(.*)$ http://localhost:6381/proxy/$1 [P,L]
ProxyPreserveHost On
EOF

chmod 644 public_html/digital-lab.ca/infrafabric/proxy/.htaccess
```

### Step 2: Enable Apache Modules

Check if required modules are enabled:

```bash
# SSH to StackCP
ssh stackcp

# Check if mod_proxy is enabled
apache2ctl -M | grep proxy
# Should show: proxy_module, proxy_http_module

# If not enabled, you may need to contact StackCP support or use PHP workaround (below)
```

### Step 3: Alternative - PHP Workaround (If mod_proxy Not Available)

Create a PHP file that proxies to the Node.js app:

```bash
cd ~/public_html/digital-lab.ca/infrafabric/proxy

# Create index.php
cat > index.php << 'EOF'
<?php
// Redis Proxy Frontend (PHP wrapper)
// Routes to Node.js app running on localhost:6381

$request_uri = $_SERVER['REQUEST_URI'];
$request_method = $_SERVER['REQUEST_METHOD'];
$query_string = $_SERVER['QUERY_STRING'];

// Remove the /infrafabric/proxy prefix
$path = str_replace('/infrafabric/proxy', '', $request_uri);
$target_url = "http://localhost:6381/proxy" . $path;

if ($query_string) {
    $target_url .= "?" . $query_string;
}

// Forward request to Node.js proxy
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $target_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $request_method);

// Forward POST data if present
if ($request_method === 'POST') {
    $post_data = file_get_contents('php://input');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
        'Content-Type: application/json',
        'Content-Length: ' . strlen($post_data)
    ));
}

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

// Return response
header('Content-Type: application/json');
http_response_code($http_code);
echo $response;
?>
EOF

chmod 644 index.php
```

---

## Phase 3: Verify External Access

### Test from Local Machine (behind firewall)

```bash
# From your local machine (WSL or Windows)
# Test via StackCP domain

curl https://digital-lab.ca/infrafabric/proxy/health
# Expected: {"status":"healthy","timestamp":"..."}

curl https://digital-lab.ca/infrafabric/proxy/keys/instance:*
# Expected: {"pattern":"instance:*","keys":[...],"count":N}

curl https://digital-lab.ca/infrafabric/proxy/get/instance:16:next-actions
# Expected: {"key":"instance:16:next-actions","value":"...","exists":true}
```

### Test from Gemini CLI

```bash
# Gemini CLI (with web access enabled)
gemini --web "Fetch https://digital-lab.ca/infrafabric/proxy/keys/instance:*"
# Should return list of Redis keys
```

---

## Phase 4: Create Documentation at Web Endpoint

Create a README accessible at `/infrafabric/proxy/`:

```bash
cd ~/public_html/digital-lab.ca/infrafabric/proxy

cat > README.md << 'EOF'
# Redis Proxy API

**Access Point:** https://digital-lab.ca/infrafabric/proxy

**Purpose:** Expose local Redis instance through firewall for external tools (Gemini CLI, etc.)

## Endpoints

### Health Check
```
GET /health
```
Returns: `{"status":"healthy","timestamp":"..."}`

### List Keys
```
GET /proxy/keys/:pattern
```
Example: `GET /proxy/keys/instance:*`
Returns: `{"pattern":"instance:*","keys":[...],"count":N}`

### Get Key Value
```
GET /proxy/get/:key
```
Example: `GET /proxy/get/instance:16:next-actions`
Returns: `{"key":"...","value":"...","exists":true,"size":1234}`

### Get TTL
```
GET /proxy/ttl/:key
```
Example: `GET /proxy/ttl/instance:16:next-actions`
Returns: `{"key":"...","ttl":2591234,"status":"active"}`

### Set Key
```
POST /proxy/set/:key?ttl=<seconds>
Body: Raw JSON or string value
```
Example:
```bash
curl -X POST https://digital-lab.ca/infrafabric/proxy/set/test:key?ttl=86400 \
  -d '{"data":"value"}' \
  -H "Content-Type: application/json"
```

### Redis Info
```
GET /proxy/info
```
Returns: Redis server information summary

## Usage from Gemini CLI

```bash
# List all instance keys
gemini --web "Fetch https://digital-lab.ca/infrafabric/proxy/keys/instance:*"

# Get specific instance context
gemini --web "Fetch https://digital-lab.ca/infrafabric/proxy/get/instance:16:session-narration"

# Check TTL on keys
gemini --web "Fetch https://digital-lab.ca/infrafabric/proxy/ttl/instance:16:next-actions"
```

## Architecture

```
Firewall (blocks direct access)
    ↓
HTTPS via StackCP (public-facing)
    ↓
Apache reverse proxy at /infrafabric/proxy
    ↓
Node.js app in /tmp/redis-proxy:6381
    ↓
Redis on localhost:6379
```

## Management Commands

### Check Proxy Status
```bash
ssh stackcp
ps aux | grep "node.*redis-proxy"
netstat -tlnp | grep 6381
```

### View Proxy Logs
```bash
ssh stackcp
tail -f /tmp/redis-proxy.log
```

### Restart Proxy
```bash
ssh stackcp
pkill -f "node.*redis-proxy"
/tmp/start-redis-proxy.sh
```

### Monitor Live
```bash
ssh stackcp
watch 'curl http://localhost:6381/health 2>/dev/null | jq .'
```

## Troubleshooting

**"Connection refused"**
→ Node.js app not running
→ Fix: `ssh stackcp && /tmp/start-redis-proxy.sh`

**"Redis connection refused"**
→ Local Redis not running on port 6379
→ Fix: `redis-server` or check redis-cli access

**"403 Forbidden"**
→ Apache not configured for proxy forwarding
→ Fix: Ensure mod_proxy enabled or use PHP wrapper

**Slow response**
→ Network latency through StackCP
→ Normal for shared hosting; consider caching

## Security Notes

- ⚠️ **NEVER expose credentials in URLs**
- ✅ Uses HTTPS via StackCP (encrypted in transit)
- ✅ Firewall blocks direct Redis access
- ⚠️ Recommend IP whitelisting for production use
- ✅ localhost:6381 only accessible from StackCP server

EOF

chmod 644 README.md
```

---

## Phase 5: Make Proxy Auto-Start

Since StackCP doesn't support cron, add to `.bashrc`:

```bash
cd ~

# Add startup command to .bashrc (runs on every login)
cat >> .bashrc << 'EOF'

# Auto-start Redis proxy if not running
if ! pgrep -f "node.*redis-proxy" > /dev/null 2>&1; then
  /tmp/start-redis-proxy.sh
fi
EOF

# Reload .bashrc
source ~/.bashrc
```

Alternatively, create a manual check script:

```bash
cat > ~/check-redis-proxy.sh << 'EOF'
#!/bin/bash
if ! pgrep -f "node.*redis-proxy" > /dev/null 2>&1; then
  echo "Redis proxy not running. Starting..."
  /tmp/start-redis-proxy.sh
else
  echo "Redis proxy is running ($(pgrep -f 'node.*redis-proxy'))"
fi
EOF

chmod +x ~/check-redis-proxy.sh

# Run it
~/check-redis-proxy.sh
```

---

## Complete Setup Checklist

- [ ] **Phase 1:** Node.js app created in `/tmp/redis-proxy/`
- [ ] **Phase 1:** Dependencies installed (`npm install`)
- [ ] **Phase 1:** Startup script created at `/tmp/start-redis-proxy.sh`
- [ ] **Phase 1:** Proxy tested locally on `localhost:6381`
- [ ] **Phase 2:** Apache reverse proxy configured (or PHP wrapper)
- [ ] **Phase 2:** Web directory created at `~/public_html/digital-lab.ca/infrafabric/proxy/`
- [ ] **Phase 3:** External access tested via `https://digital-lab.ca/infrafabric/proxy/health`
- [ ] **Phase 4:** README.md created at web endpoint
- [ ] **Phase 5:** Auto-start configured (`.bashrc` or manual script)
- [ ] **Final:** Test from Gemini CLI with `--web` flag

---

## Quick Start

```bash
# 1. SSH to StackCP
ssh stackcp

# 2. Go to /tmp and create proxy
cd /tmp
mkdir -p redis-proxy && cd redis-proxy

# 3. Copy app.js (from Phase 1 Step 1 above)
# [Paste full app.js here]

# 4. Install dependencies
export PATH="/tmp/node-v20.18.0-linux-x64/bin:$PATH"
/tmp/npm install express redis cors body-parser

# 5. Create startup script
cat > /tmp/start-redis-proxy.sh << 'EOF'
#!/bin/bash
cd /tmp/redis-proxy
export PATH="/tmp/node-v20.18.0-linux-x64/bin:$PATH"
nohup /tmp/node app.js > /tmp/redis-proxy.log 2>&1 &
echo $! > /tmp/redis-proxy.pid
EOF
chmod +x /tmp/start-redis-proxy.sh

# 6. Start it
/tmp/start-redis-proxy.sh

# 7. Test locally
curl http://localhost:6381/health

# 8. Configure Apache (or create PHP wrapper)
# [Follow Phase 2/3 above]

# 9. Test externally
curl https://digital-lab.ca/infrafabric/proxy/health
```

---

**Status:** Ready to implement
**Owner:** You (manual setup required for StackCP)
**Effort:** ~30 minutes for full setup
**Result:** Redis accessible from anywhere via HTTPS, safe from firewall

