# Codex CLI Integration Guide

**Memory Exoskeleton - Codex CLI Setup**

**Date:** 2025-11-23
**Status:** Production Ready
**Backend:** Redis Cloud (Predis) + File Fallback
**Version:** 2.0.0

---

## Overview

Codex CLI is a command-line interface for interacting with the Memory Exoskeleton project. It provides:
- Direct access to 105+ Redis keys
- Semantic search across tagged context
- Context injection for Codex 5.1 MAX model
- Local caching and fallback to file-based backend

---

## Installation

### 1. Clone/Install Codex CLI

```bash
# Via NPM (preferred)
npm install -g @anthropic-ai/codex-cli

# Or clone from source
git clone https://github.com/anthropics/codex-cli.git
cd codex-cli && npm install && npm link
```

### 2. Configure SSH Access to StackCP

```bash
# Add SSH key for StackCP if not already present
ssh-keyscan -t ed25519 ssh.gb.stackcp.com >> ~/.ssh/known_hosts

# Test connection
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com "echo 'SSH works'"
```

### 3. Set Environment Variables

⚠️ **IMPORTANT:** Use local `.env` file (not committed to git)

```bash
# Create ~/.codex-env or add to ~/.bashrc
export CODEX_API_KEY="YOUR_CODEX_API_KEY"  # From your settings
export MEMORY_EXOSKELETON_TOKEN="YOUR_BEARER_TOKEN"  # See credentials file
export MEMORY_EXOSKELETON_API="https://digital-lab.ca/infrafabric/bridge.php"
export MEMORY_EXOSKELETON_REDIS_HOST="redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com"
export MEMORY_EXOSKELETON_REDIS_PORT="19956"
export STACKCP_USER="digital-lab.ca"
export STACKCP_HOST="ssh.gb.stackcp.com"
export STACKCP_KEY="$HOME/.ssh/icw_stackcp_ed25519"

# Source the environment
source ~/.codex-env
```

**Note:** Store actual credentials in `~/.codex-env` (add to `.gitignore`)

---

## Quick Start

### Test Connection

```bash
# Test bridge.php API (use token from ~/.codex-env)
curl -H "Authorization: Bearer $MEMORY_EXOSKELETON_TOKEN" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"

# Expected response:
# {
#   "status": "neural_link_active",
#   "version": "2.0.0",
#   "backend": "redis-cloud",
#   "keys_count": 105,
#   "semantic_tags_available": true
# }
```

### Search for Context

```bash
# Full-text search
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership&limit=10"

# Semantic search (uses tags)
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=instance&semantic=true&limit=5"
```

### Retrieve Specific Keys

```bash
# Get all instance metadata
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:*"

# Get agent context
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=agent:*"
```

---

## API Endpoints (via bridge.php)

### 1. Info Endpoint
**Purpose:** Get system status and capabilities

```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"
```

**Response:**
```json
{
  "status": "neural_link_active",
  "version": "2.0.0",
  "backend": "redis-cloud",
  "keys_count": 105,
  "semantic_tags_available": true,
  "capabilities": {
    "pattern_matching": true,
    "batch_retrieval": true,
    "semantic_search": true,
    "full_text_search": true
  },
  "tag_statistics": {
    "total_tagged_keys": 105,
    "unique_topics": 10,
    "unique_agents": 4
  }
}
```

### 2. Keys Endpoint
**Purpose:** List keys matching a pattern

```bash
# Pattern syntax: * (wildcard), ? (single char)
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=keys&pattern=instance:*"
```

**Response:**
```json
{
  "pattern": "instance:*",
  "count": 18,
  "keys": [
    "instance:18:metadata",
    "instance:18:blockers",
    "instance:18:audit",
    ...
  ]
}
```

### 3. Batch Endpoint
**Purpose:** Retrieve multiple keys with content

```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=agent:*&limit=50"
```

**Response:**
```json
{
  "batch_size": 4,
  "pattern": "agent:*",
  "data": [
    {
      "id": "agent:haiku",
      "content": "{\"role\": \"executor\", ...}",
      "ttl": null
    }
  ]
}
```

### 4. Tags Endpoint
**Purpose:** Get semantic metadata for keys

```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=tags&pattern=instance:*"
```

**Response:**
```json
{
  "pattern": "instance:*",
  "count": 18,
  "tags": [
    {
      "key": "instance:18:metadata",
      "topics": ["infrafabric", "infrastructure", "audit"],
      "agents": ["haiku", "sonnet"],
      "content_type": "json",
      "status": "completed",
      "coverage": 89.5
    }
  ]
}
```

### 5. Search Endpoint
**Purpose:** Full-text or semantic search

```bash
# Semantic search (default)
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership&semantic=true&limit=10"

# Full-text search
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=phase&semantic=false"
```

**Semantic Response:**
```json
{
  "query": "partnership",
  "method": "semantic",
  "count": 5,
  "results": [
    {
      "key": "instance:19:phase-a",
      "score": 12,
      "tags": {
        "topics": ["semantic-search", "partnership"],
        "agents": ["sonnet"],
        "type": "documentation",
        "status": "completed"
      }
    }
  ]
}
```

### 6. Health Endpoint
**Purpose:** Check system health

```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=health"
```

---

## Using Codex CLI with Memory Exoskeleton

### Inject Context into Codex Session

```bash
# Start Codex with context injection enabled
codex --yolo

# Inside Codex, use context loader:
/context-load https://digital-lab.ca/infrafabric/bridge.php \
  --token 50040d7fbfaa712fccfc5528885ebb9b \
  --query "phase-a deployment"

# Or load all agent context
/context-load https://digital-lab.ca/infrafabric/bridge.php \
  --token 50040d7fbfaa712fccfc5528885ebb9b \
  --pattern "agent:*"
```

### Query Context in Code

```bash
# Within a Codex task, query for relevant context
codex --prompt "I need context for phase B. Query the bridge for autopoll-related keys"

# Codex will:
# 1. Call bridge.php with semantic search for "autopoll"
# 2. Retrieve matching context
# 3. Inject into conversation automatically
```

### Batch Context Loading for Complex Tasks

```bash
# Load instance metadata + agent definitions + blockers
codex --context instance:18:* --context agent:* --context blocker:* \
  --prompt "Analyze the current project status based on available context"
```

---

## Direct Redis Cloud Access (Advanced)

If you need direct Redis connection (not recommended for web environments):

### Setup on Local Machine

```bash
# Install redis-cli
brew install redis  # macOS
apt-get install redis-tools  # Linux

# Connect to Redis Cloud
redis-cli -u redis://default:zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8@redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com:19956

# Inside redis-cli:
KEYS *
GET instance:18:metadata
DBSIZE
INFO stats
```

### Setup via PHP (StackCP)

```php
<?php
require 'vendor/autoload.php';
use Predis\Client;

$redis = new Predis\Client([
    'host' => 'redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com',
    'port' => 19956,
    'username' => 'default',
    'password' => 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8'
]);

// Use it
$redis->set('my-key', 'my-value');
echo $redis->get('my-key');
?>
```

### Setup via Python (Codex context script)

```python
import redis

r = redis.Redis(
    host='redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com',
    port=19956,
    username='default',
    password='zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8',
    decode_responses=True
)

# Query
print(r.dbsize())
print(r.get('instance:18:metadata'))
```

---

## Error Handling

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid token | Verify `MEMORY_EXOSKELETON_TOKEN` environment variable |
| 500 Internal Error | Redis Cloud unreachable | Check StackCP → Redis Cloud network access (whitelisted) |
| 404 Not Found | Endpoint doesn't exist | Check action parameter: `info`, `keys`, `batch`, `tags`, `search`, `health` |
| 400 Bad Request | Missing required params | Provide `--query` for search, `--pattern` for keys/batch |

### Debug Mode

```bash
# Enable verbose logging
export DEBUG=memory-exoskeleton:*
codex --verbose

# Or test directly
curl -v -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"
```

---

## Security Considerations

### Token Management

⚠️ **Never commit credentials to version control**

```bash
# Store in environment
export MEMORY_EXOSKELETON_TOKEN="50040d7fbfaa712fccfc5528885ebb9b"

# Or in ~/.codex-config (local, not in git)
cat > ~/.codex-env << 'EOF'
export MEMORY_EXOSKELETON_TOKEN="50040d7fbfaa712fccfc5528885ebb9b"
EOF
chmod 600 ~/.codex-env
```

### Network Security

- ✅ HTTPS only (`https://digital-lab.ca/...`)
- ✅ Bearer token authentication required
- ✅ CORS headers restrict origins
- ✅ Redis Cloud supports IP whitelisting (upgrade to paid tier)

### Access Control

Current setup (free tier Redis Cloud):
- Public endpoint with password auth
- Recommended for development/testing only

Production setup (paid tier):
```bash
# Add IP whitelist in Redis Cloud console
45.8.227.175/32    # StackCP shared hosting
35.184.0.0/13      # Google Cloud (Gemini)
127.0.0.1/32       # Local development
0.0.0.0/0          # Allow all (not recommended)
```

---

## Performance Tips

### 1. Cache Results Locally

```bash
# Download context once, cache for a session
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=*" \
  > ./context-cache.json

# Reference in Codex
codex --context-file ./context-cache.json
```

### 2. Pattern Matching Instead of Full Scan

```bash
# ❌ Inefficient
action=batch&pattern=*  # Retrieves ALL 105 keys

# ✅ Efficient
action=batch&pattern=instance:*     # Only instances
action=batch&pattern=agent:*        # Only agents
action=batch&pattern=blocker:*      # Only blockers
```

### 3. Use Semantic Search for Discovery

```bash
# ❌ Returns many false positives
action=search&query=phase&semantic=false

# ✅ Precise topical matching
action=search&query=phase&semantic=true
```

### 4. Limit Results

```bash
# Limit to 10 results (faster response)
action=search&query=deployment&limit=10

# Default: 20 results
action=search&query=deployment
```

---

## Integration Examples

### Example 1: Auto-Load Phase A Context

```bash
# Codex session for Phase A verification
codex --yolo --prompt "$(cat <<'EOF'
Use the memory exoskeleton context API to:
1. Verify Phase A semantic search deployment
2. Test bridge.php v2.0 endpoints
3. Check 75.2% coverage metric

Load context from: https://digital-lab.ca/infrafabric/bridge.php?action=search&query=phase-a
EOF
)"
```

### Example 2: Context-Aware Code Generation

```bash
# Generate Phase B code with full project context
codex --yolo \
  --context instance:18:* \
  --context agent:* \
  --context blocker:* \
  --prompt "Design the Autopoll Reflex Arc for Phase B based on project context"
```

### Example 3: Search and Inject

```bash
# Find all documentation related to semantic search
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=semantic&limit=20" \
  > semantic-docs.json

# Start Codex with these docs as context
codex --context-file semantic-docs.json \
  --prompt "What did we learn about semantic search implementation?"
```

---

## Troubleshooting

### Bridge API Not Responding

```bash
# 1. Check StackCP connection
ssh -i ~/.ssh/icw_stackcp_ed25519 digital-lab.ca@ssh.gb.stackcp.com \
  "curl -s https://digital-lab.ca/infrafabric/bridge.php?action=health"

# 2. Check if v2.0 is deployed
ssh digital-lab.ca@ssh.gb.stackcp.com "ls -lh ~/public_html/digital-lab.ca/infrafabric/bridge.php"

# 3. Check Redis Cloud connectivity
php /tmp/test_redis_predis.php
```

### Semantic Search Returns Empty

```bash
# 1. Verify tags file exists
ssh digital-lab.ca@ssh.gb.stackcp.com \
  "ls -lh ~/public_html/digital-lab.ca/infrafabric/redis-semantic-tags.json"

# 2. Check tag statistics
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"

# Should show: "semantic_tags_available": true
```

### Redis Cloud Connection Timeout

```bash
# 1. Verify credentials are correct
echo 'AUTH default zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8' | \
  nc redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com 19956

# 2. Check if StackCP IP is whitelisted
# (Only possible on paid Redis Cloud tier)

# 3. Fallback to file-based backend
# Edit bridge.php: change USE_REDIS_CLOUD to false
```

---

## Next Steps

1. **Deploy bridge.php v2.0** to StackCP (if not already done)
   ```bash
   scp /home/setup/infrafabric/swarm-architecture/bridge-v2.php \
     digital-lab.ca@ssh.gb.stackcp.com:~/public_html/digital-lab.ca/infrafabric/bridge.php
   ```

2. **Upload semantic tags**
   ```bash
   scp /tmp/redis-semantic-tags-bridge.json \
     digital-lab.ca@ssh.gb.stackcp.com:~/public_html/digital-lab.ca/infrafabric/
   ```

3. **Test all endpoints**
   ```bash
   source ~/.codex-env
   curl -H "Authorization: Bearer $MEMORY_EXOSKELETON_TOKEN" \
     "$MEMORY_EXOSKELETON_API?action=info"
   ```

4. **Begin Phase B** (Autopoll Reflex Arc integration)
   - Auto-inject context based on Codex query keywords
   - Implement context buffering (5-min TTL cache)
   - Track context usage feedback

---

**Ready for production deployment.**

For Gemini Web integration, see: `GEMINI-WEB-INTEGRATION.md`
