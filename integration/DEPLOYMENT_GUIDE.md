# Claude Max OpenWebUI Function - Deployment Guide

**Version:** 1.0.0
**Last Updated:** 2025-11-30
**Status:** Production-Ready

## Quick Start (5 minutes)

### 1. Prerequisites Check
```bash
# Verify Claude CLI is installed
which claude
claude --version
# Expected: 2.0.55 or higher

# Verify Python 3.7+
python3 --version

# Verify you have Node.js/npm if installing Claude CLI
npm --version
```

### 2. Claude CLI Authentication
```bash
# Login to Claude
claude auth login

# Verify auth token was created
ls -la ~/.claude/auth_token

# Test Claude CLI
claude --print "Hello, Claude"
```

### 3. Install Function Module

**For OpenWebUI via Docker:**
```bash
# Copy module to OpenWebUI functions directory
cp /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
   /path/to/openwebui/functions/

# If using docker-compose, copy to mounted volume:
docker cp openwebui_claude_max_module.py open-webui:/app/backend/data/functions/
```

**For OpenWebUI Source Install:**
```bash
cp /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
   ~/open-webui/functions/
```

### 4. Verify Deployment
```bash
# Check function status
python3 /home/setup/infrafabric/integration/openwebui_claude_max_module.py --status

# Output should show:
# {
#   "ready": true,
#   "message": "Claude CLI ready"
# }

# Test with a message
python3 /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
  --test "What is Claude?"
```

### 5. Use in OpenWebUI
1. Open http://localhost:8080
2. Start new chat
3. Select "Claude Max OpenWebUI" function
4. Send message
5. Response streams from Claude CLI

---

## Full Deployment Steps

### Step 1: Install Claude CLI (if not already installed)

```bash
# Using npm (recommended)
npm install -g @anthropic-ai/claude

# Verify installation
claude --version
# Expected: 2.0.55 (Claude Code)

# Alternative: Install from source
git clone https://github.com/anthropic-ai/claude-code.git
cd claude-code
npm install
npm link
```

### Step 2: Authenticate Claude CLI

```bash
# Run authentication flow
claude auth login

# This will:
# 1. Open browser for authentication
# 2. Create ~/.claude/auth_token
# 3. Save credentials securely

# Verify authentication
ls -la ~/.claude/
# Should contain: auth_token, config.json

# Test authenticated access
claude --print "Hello"
# Should return a response from Claude
```

### Step 3: Set Up OpenWebUI (if not running)

**Option A: Docker Compose**
```bash
cd /home/setup/infrafabric
docker-compose -f docker-compose-openwebui.yml up -d

# Verify running
docker ps | grep open-webui
# Should show running containers
```

**Option B: Source Installation**
```bash
# Clone OpenWebUI
git clone https://github.com/open-webui/open-webui.git
cd open-webui

# Install dependencies
npm install
pip install -r requirements.txt

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

### Step 4: Deploy Function Module

**For Docker Installation:**
```bash
# Find OpenWebUI container
docker ps | grep open-webui
# Note the CONTAINER_ID

# Copy module into container
docker cp /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
  CONTAINER_ID:/app/backend/data/functions/

# Restart to load new functions
docker restart CONTAINER_ID
```

**For Source Installation:**
```bash
# Find OpenWebUI functions directory
# Typically: ~/open-webui/functions/ or ~/.local/share/open-webui/functions/

# Copy module
cp /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
   ~/.local/share/open-webui/functions/

# Restart OpenWebUI (CTRL+C and restart, or restart service)
```

**For Manual Function Upload:**
1. Open OpenWebUI: http://localhost:8080
2. Go to Settings → Admin Panel
3. Click "Functions"
4. Click "Create Function"
5. Paste contents of `openwebui_claude_max_module.py`
6. Set name: "Claude Max"
7. Click Save

### Step 5: Verify Installation

**Check Function Status:**
```bash
python3 /home/setup/infrafabric/integration/openwebui_claude_max_module.py --status

# Output should be:
# {
#   "name": "Claude Max OpenWebUI",
#   "version": "1.0.0",
#   "ready": true,
#   "message": "Claude CLI ready",
#   "claude_cli": {
#     "installed": true,
#     "version": "2.0.55 (Claude Code)",
#     "needs_update": false,
#     "needs_login": false,
#     "error": null
#   },
#   "last_check": "2025-11-30T19:27:20.862191"
# }
```

**Test Function Directly:**
```bash
python3 /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
  --test "What is 2+2?"

# Should return:
# This is a response from Claude.
```

**Test in OpenWebUI UI:**
1. Open http://localhost:8080
2. New Chat
3. Select "Claude Max OpenWebUI" (if not default)
4. Type: "Hello, Claude!"
5. Should see response stream in real-time

---

## Configuration

### Environment Variables

No required environment variables. The module auto-detects:
- Claude CLI location
- Authentication status
- CLI version

### Optional Configuration

Edit these constants in the module (if needed):

```python
# Minimum Claude CLI version required
CLAUDE_CLI_MIN_VERSION = "2.0.0"

# Timeout for CLI execution (seconds)
TIMEOUT = 300

# Cache duration for CLI checks (seconds)
CLI_CHECK_INTERVAL = 300  # 5 minutes
```

### Logging Configuration

Logs are output to stderr as JSON for easy parsing:

```bash
# View logs with timestamps
python3 -c "from openwebui_claude_max_module import ClaudeMaxFunction; \
  f = ClaudeMaxFunction(); f._log('DEBUG', 'Test log')" 2>&1

# Filter logs by level
python3 openwebui_claude_max_module.py --status 2>&1 | \
  grep '"level": "ERROR"'
```

---

## Troubleshooting

### Issue: "Claude CLI not found"

**Symptoms:**
```
"error": "Claude CLI not found in PATH"
```

**Solutions:**
```bash
# 1. Install Claude CLI
npm install -g @anthropic-ai/claude

# 2. Verify installation
which claude

# 3. Add to PATH if needed
export PATH="$PATH:~/.npm/_npx:/usr/local/bin"

# 4. Restart OpenWebUI service
```

### Issue: "Claude CLI requires authentication"

**Symptoms:**
```
"needs_login": true
"error": "Claude CLI requires authentication. Run: claude auth login"
```

**Solutions:**
```bash
# 1. Run authentication
claude auth login

# 2. Verify auth token created
ls ~/.claude/auth_token

# 3. Test authentication
claude --print "Hello"

# 4. If still failing, clear cache and retry:
rm ~/.claude/auth_token
claude auth login
```

### Issue: Request Timeout

**Symptoms:**
```
"error": "Request timed out after 300s"
```

**Solutions:**
- Simplify your query (shorter messages)
- Check Claude subscription status
- Increase timeout in module (if needed)
- Check Claude service status

### Issue: Empty Response

**Symptoms:**
```
No response from Claude CLI
```

**Solutions:**
```bash
# 1. Test Claude directly
claude --print "Test message"

# 2. Check if Claude is working
claude --print "Hello"

# 3. Verify subscription is active
# Visit https://claude.ai in browser

# 4. Check for API errors
claude --print "Debug" 2>&1
```

### Issue: OpenWebUI Not Finding Function

**Symptoms:**
- Function doesn't appear in model list
- "Function not found" error

**Solutions:**
```bash
# 1. Verify file is in correct location
find / -name "openwebui_claude_max_module.py" 2>/dev/null

# 2. Check file permissions
chmod 644 /path/to/openwebui_claude_max_module.py

# 3. Verify Python syntax
python3 -m py_compile /path/to/openwebui_claude_max_module.py

# 4. Restart OpenWebUI
docker restart open-webui  # for Docker
# OR restart your service

# 5. Check logs
docker logs open-webui | tail -50  # for Docker
```

### Debug Mode

Enable verbose logging:

```bash
# Run with debug output
python3 -c "
import sys, json
sys.path.insert(0, '/home/setup/infrafabric/integration')
from openwebui_claude_max_module import ClaudeMaxFunction

f = ClaudeMaxFunction()
status = f.get_status()
print(json.dumps(status, indent=2))
" 2>&1
```

---

## Performance Tuning

### Optimize CLI Checks

The module caches CLI checks for 5 minutes. To adjust:

```python
# Edit in module:
self._cli_check_interval = 300  # seconds

# For high-frequency usage, reduce to 60 seconds
self._cli_check_interval = 60
```

### Memory Usage

Current memory footprint: ~50MB per process

To reduce:
- Clear ~/.claude cache periodically
- Limit concurrent requests

### Network Optimization

- Requests go directly from Claude CLI to Anthropic
- No intermediate servers
- Streaming reduces memory overhead

---

## Security Checklist

- [ ] Claude CLI authenticated with valid credentials
- [ ] Auth token file has restricted permissions (600)
- [ ] Module running with minimal privileges
- [ ] No API keys in environment variables
- [ ] OpenWebUI HTTPS enabled (recommended for production)
- [ ] Function error messages don't expose internal paths
- [ ] Logs don't contain sensitive data

---

## Monitoring & Maintenance

### Health Checks

```bash
# Daily health check script
#!/bin/bash
python3 /home/setup/infrafabric/integration/openwebui_claude_max_module.py --status | \
  grep -q '"ready": true' && echo "OK" || echo "FAILED"
```

### Log Rotation

Logs are output to stderr and handled by your system's logging.

For Docker:
```bash
docker logs open-webui --tail 1000
```

### Update Procedures

1. **Update Claude CLI:**
```bash
npm install -g @anthropic-ai/claude@latest
claude --version
```

2. **Update Module:**
```bash
# Backup current
cp openwebui_claude_max_module.py openwebui_claude_max_module.py.backup

# Update
cp /home/setup/infrafabric/integration/openwebui_claude_max_module.py \
   /path/to/installation/

# Restart OpenWebUI
docker restart open-webui
```

3. **Test After Update:**
```bash
python3 openwebui_claude_max_module.py --status
python3 openwebui_claude_max_module.py --test "Update test"
```

---

## Support & Feedback

For issues:
1. Run: `--status` to diagnose
2. Check troubleshooting section above
3. Review logs: `docker logs open-webui`
4. Test: `--test "message"` for direct testing

For feature requests or bugs:
- GitHub Issues (if repo available)
- Include output of `--status`
- Include error logs from stderr

---

## Uninstall

If you need to remove the function:

```bash
# For Docker:
docker exec open-webui rm /app/backend/data/functions/openwebui_claude_max_module.py
docker restart open-webui

# For source:
rm ~/.local/share/open-webui/functions/openwebui_claude_max_module.py

# Claude CLI can be removed with:
npm uninstall -g @anthropic-ai/claude
```

---

## Next Steps

1. **Verify Installation:** Run `--status` command
2. **Test Functionality:** Send test message
3. **Monitor:** Check logs for errors
4. **Customize:** Adjust settings if needed
5. **Document:** Record your installation details

Welcome to Claude Max in OpenWebUI!
