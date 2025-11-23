# Credentials Template (Local Only - NOT COMMITTED)

**⚠️ IMPORTANT:** This file shows how to store credentials locally. NEVER commit actual credentials to git.

---

## Local Credentials File (~/.memory-exoskeleton-creds)

Create this file locally with your actual credentials:

```bash
# Redis Cloud Credentials
export REDIS_HOST="redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com"
export REDIS_PORT="19956"
export REDIS_USER="default"
export REDIS_PASSWORD="YOUR_REDIS_PASSWORD"  # Change to actual password
export REDIS_URI="redis://${REDIS_USER}:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}"

# API Bridge Credentials
export MEMORY_EXOSKELETON_API="https://digital-lab.ca/infrafabric/bridge.php"
export MEMORY_EXOSKELETON_TOKEN="YOUR_BEARER_TOKEN"  # Change to actual token

# StackCP Credentials
export STACKCP_USER="digital-lab.ca"
export STACKCP_HOST="ssh.gb.stackcp.com"
export STACKCP_KEY="$HOME/.ssh/icw_stackcp_ed25519"

# Codex/Gemini API Keys
export CODEX_API_KEY="sk-..."  # Your Codex API key
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

---

## Setup Instructions

### 1. Create Local Credentials File

```bash
cat > ~/.memory-exoskeleton-creds << 'EOF'
export REDIS_PASSWORD="YOUR_ACTUAL_PASSWORD"
export MEMORY_EXOSKELETON_TOKEN="YOUR_ACTUAL_TOKEN"
# ... add other credentials ...
EOF

chmod 600 ~/.memory-exoskeleton-creds
```

### 2. Load Credentials in Session

```bash
# Add to ~/.bashrc or ~/.zshrc
source ~/.memory-exoskeleton-creds

# Or source before running scripts
source ~/.memory-exoskeleton-creds && codex --yolo
```

### 3. Use Environment Variables in Documentation

All documentation examples use:
- `$MEMORY_EXOSKELETON_TOKEN` instead of hardcoded token
- `$REDIS_PASSWORD` instead of hardcoded password
- `$STACKCP_KEY` instead of hardcoded key path

---

## Credentials Location Reference

| Credential | Source | Where to Find |
|------------|--------|---------------|
| Bearer Token | API Bridge | See user's .claude/CLAUDE.md |
| Redis Password | Redis Cloud | Redis Cloud console |
| StackCP SSH Key | SSH Keypair | ~/.ssh/icw_stackcp_ed25519 |
| Codex API Key | Codex CLI | Codex settings panel |
| Gemini API Key | Google Cloud | Google Cloud Console |

---

## Security Best Practices

✅ **DO:**
- Store credentials in `~/.memory-exoskeleton-creds`
- Add to `.gitignore` (never commit)
- Use `chmod 600` for credential files
- Use environment variables in scripts
- Rotate credentials quarterly

❌ **DON'T:**
- Commit credentials to git
- Hardcode tokens in documentation
- Share `.memory-exoskeleton-creds` files
- Expose keys in logs or error messages
- Use same credential in multiple places

---

## Environment Variable Usage in Code

### Bash Example

```bash
# Source credentials
source ~/.memory-exoskeleton-creds

# Use in API call
curl -H "Authorization: Bearer $MEMORY_EXOSKELETON_TOKEN" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"
```

### PHP Example

```php
<?php
$token = getenv('MEMORY_EXOSKELETON_TOKEN');
$redis_password = getenv('REDIS_PASSWORD');

$headers = ['Authorization' => "Bearer $token"];
// Use in API call
?>
```

### Python Example

```python
import os

token = os.getenv('MEMORY_EXOSKELETON_TOKEN')
redis_password = os.getenv('REDIS_PASSWORD')

headers = {'Authorization': f'Bearer {token}'}
# Use in API call
```

### JavaScript Example

```javascript
const token = process.env.MEMORY_EXOSKELETON_TOKEN;
const redisPassword = process.env.REDIS_PASSWORD;

const headers = {'Authorization': `Bearer ${token}`};
// Use in API call
```

---

## CI/CD Integration (GitHub Actions)

For automated deployments, add secrets in GitHub:

**Settings → Secrets and Variables → Actions → New Repository Secret**

```
MEMORY_EXOSKELETON_TOKEN: (your actual token)
REDIS_PASSWORD: (your actual password)
STACKCP_SSH_KEY: (base64 encoded key)
```

---

## Rotation Schedule

- **Bearer Token:** Rotate quarterly or after exposure
- **Redis Password:** Rotate quarterly or after upgrade
- **SSH Keys:** Rotate semi-annually
- **API Keys:** Rotate annually or when compromised

---

**This file is a template only. Create your own local copy with actual credentials.**

**Never commit to git. Add to `.gitignore`.**
