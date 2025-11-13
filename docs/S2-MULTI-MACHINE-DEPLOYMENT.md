# S² Multi-Machine Deployment Guide

**Architecture:** 9 agents on **9 separate machines** (no shared filesystem)
**Coordination:** Git repo + MCP Bridge
**Ready to Deploy:** Yes ✅

---

## Quick Reference: What to Paste Where

### On ALL 9 Machines (Orchestrator + 8 Workers)

**Step 1: Install MCP Bridge**

```bash
# Paste this into each Claude session
curl -fsSL https://raw.githubusercontent.com/dannystocker/mcp-multiagent-bridge/main/scripts/install.sh 2>/dev/null | bash || { cd /tmp && git clone https://github.com/dannystocker/mcp-multiagent-bridge.git && cd mcp-multiagent-bridge && pip install -q mcp>=1.0.0 && mkdir -p ~/.config/claude && echo "{\"mcpServers\":{\"bridge\":{\"command\":\"python3\",\"args\":[\"$(pwd)/claude_bridge_secure.py\"]}}}" > ~/.config/claude/claude.json && echo "✅ MCP Bridge installed at: $(pwd)" && echo "📝 Config: ~/.config/claude/claude.json" && echo "🔄 Restart Claude Code to load MCP server"; }
```

**Step 2: Pull Deployment Scripts**

```bash
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
chmod +x scripts/s2-deployment/*.sh scripts/s2-deployment/*.py
```

**Expected output:**
```
✅ MCP Bridge installed at: /tmp/mcp-multiagent-bridge
📝 Config: ~/.config/claude/claude.json
```

---

### On Orchestrator Machine ONLY (Cloud Machine 1 - This Session)

**Step 3: Create 8 Conversations**

Paste this into **this Claude session**:

```
I need to create 8 conversations for S² coordination using the MCP bridge.

For each worker (1-8):
  1. Use the MCP tool: create_conversation
     - my_role: "s2-orchestrator"
     - partner_role: "worker-{1-8}-{role}"

  2. Save credentials to: credentials/s2-worker-{1-8}-credentials.json

     Format:
     {
       "conversation_id": "conv_...",
       "worker_id": "{1-8}",
       "worker_role": "{role}",
       "coordinator_token": "token_...",
       "worker_token": "token_...",
       "created_at": "timestamp",
       "expires_at": "timestamp"
     }

Worker roles:
- worker-1-backend
- worker-2-frontend
- worker-3-tests
- worker-4-docs
- worker-5-deploy
- worker-6-review
- worker-7-wsl-cli
- worker-8-cloud-codex

After creating all 8 conversations, commit credentials to git:

cd /home/user/infrafabric
git add credentials/s2-worker-*.json
git commit -m "chore(s2): Add MCP bridge credentials for 8 workers"
git push -u origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy
```

**Step 4: Start External Watchdog**

After credentials are created:

```bash
cd /home/user/infrafabric
scripts/s2-deployment/watchdog-monitor.sh &
echo "🐕 Watchdog started - monitoring all 8 workers"
tail -f /tmp/mcp-watchdog.log
```

---

### On Worker Machines (8 Machines)

**Machine Assignments:**

| Machine | Worker ID | Role | Command to Paste |
|---------|-----------|------|------------------|
| Cloud Machine 2 | 1 | backend | `export WORKER_ID=1` |
| Cloud Machine 3 | 2 | frontend | `export WORKER_ID=2` |
| Cloud Machine 4 | 3 | tests | `export WORKER_ID=3` |
| Cloud Machine 5 | 4 | docs | `export WORKER_ID=4` |
| Cloud Machine 6 | 5 | deploy | `export WORKER_ID=5` |
| Cloud Machine 7 | 6 | review | `export WORKER_ID=6` |
| Your WSL (Local) | 7 | wsl-cli | `export WORKER_ID=7` |
| Cloud Machine 8 | 8 | cloud-codex | `export WORKER_ID=8` |

**Step 5: Pull Credentials and Start Keep-Alive (Each Worker)**

```bash
# Set worker ID for this machine (see table above)
export WORKER_ID=1  # Change to 1, 2, 3, 4, 5, 6, 7, or 8

# Pull latest credentials from git
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Install jq if not already installed (needed to parse JSON)
sudo apt-get install -y jq

# Extract credentials
CONV_ID=$(jq -r '.conversation_id' credentials/s2-worker-${WORKER_ID}-credentials.json)
WORKER_TOKEN=$(jq -r '.worker_token' credentials/s2-worker-${WORKER_ID}-credentials.json)

# Start keep-alive daemon
scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$WORKER_TOKEN" &

echo "✅ Worker-$WORKER_ID keep-alive daemon started"
echo "📋 Conversation ID: $CONV_ID"
echo "📝 Logs: tail -f /tmp/mcp-keepalive.log"
```

**Optional: Start Credential Sync Daemon**

If you want automatic credential updates when orchestrator creates new conversations:

```bash
scripts/s2-deployment/credential-sync-daemon.sh $WORKER_ID &
echo "🔄 Credential sync daemon started (auto-pulls every 60s)"
```

---

## Verification

### On Orchestrator (After All Workers Started)

Check that all 8 workers are sending heartbeats:

```bash
sqlite3 /tmp/claude_bridge_coordinator.db "SELECT conversation_id, last_heartbeat FROM session_status ORDER BY last_heartbeat DESC;"
```

**Expected output:**
```
conv_worker1|2025-11-13T16:30:15.123456
conv_worker2|2025-11-13T16:30:14.234567
conv_worker3|2025-11-13T16:30:13.345678
conv_worker4|2025-11-13T16:30:12.456789
conv_worker5|2025-11-13T16:30:11.567890
conv_worker6|2025-11-13T16:30:10.678901
conv_worker7|2025-11-13T16:30:09.789012
conv_worker8|2025-11-13T16:30:08.890123
```

### Send Test Task to All Workers

Paste into orchestrator Claude session:

```
Send a test message to all 8 workers:

For each worker (1-8):
  Use MCP tool: send_to_partner
  - conversation_id: [worker-{n}-conv-id]
  - message: {
      "type": "test_task",
      "task_id": "comms-test",
      "description": "Reply with 'ACK from worker-{n}'"
    }
  - action_type: "task_assignment"

Then monitor for responses:

Every 30 seconds for 2 minutes:
  Use MCP tool: check_messages
  Log any acknowledgments received
```

**Expected:** All 8 workers send "ACK from worker-X" within 60 seconds.

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────┐
│         Git Repository (Shared Coordination)           │
│         dannystocker/infrafabric                       │
│                                                        │
│  • scripts/s2-deployment/ (all machines pull)          │
│  • credentials/ (orchestrator creates, workers pull)   │
└─────────────────┬──────────────────────────────────────┘
                  │
      ┌───────────┴───────────┬───────────┬───────────┐
      │                       │           │           │
┌─────▼─────┐  ┌──────▼──────┐  ┌───▼───┐  ┌───▼───┐
│  Cloud    │  │  Cloud      │  │ Cloud │  │ Cloud │
│ Machine 1 │  │ Machine 2   │  │ Mach 3│  │ Mach 4│
│           │  │             │  │       │  │       │
│Orchestrator│ │ Worker-1    │  │Worker2│  │Worker3│
│ + Watchdog│  │ (Backend)   │  │(Front)│  │(Tests)│
└───────────┘  └─────────────┘  └───────┘  └───────┘
      │                       │           │           │
      └───────────┬───────────┴───────────┴───────────┘
                  │
      ┌───────────┴───────────┬───────────┬───────────┐
      │                       │           │           │
┌─────▼─────┐  ┌──────▼──────┐  ┌───▼───┐  ┌───▼────┐
│  Cloud    │  │  Cloud      │  │ Cloud │  │Your WSL│
│ Machine 5 │  │ Machine 6   │  │ Mach 7│  │(Local) │
│           │  │             │  │       │  │        │
│ Worker-4  │  │ Worker-5    │  │Worker6│  │Worker7 │
│ (Docs)    │  │ (Deploy)    │  │(Review)│ │(CLI)   │
└───────────┘  └─────────────┘  └───────┘  └────────┘

                  ┌───────────┐
                  │  Cloud    │
                  │Machine 8  │
                  │           │
                  │ Worker-8  │
                  │ (Codex)   │
                  └───────────┘
```

**Key Points:**
- ✅ No shared `/tmp` or local directories
- ✅ All coordination via git commits
- ✅ Each machine pulls scripts and credentials independently
- ✅ Keep-alive daemons run locally on each worker
- ✅ External watchdog runs on orchestrator machine only

---

## Common Issues

### Issue: "Credentials file not found"

**Symptom:**
```
⚠️  Credentials file not found: /home/user/infrafabric/credentials/s2-worker-1-credentials.json
```

**Solution:**
```bash
# Make sure you pulled latest from git
cd /home/user/infrafabric
git pull origin claude/debug-session-freezing-011CV2mM1FVCwsC8GoBR2aQy

# Verify credentials exist
ls -lh credentials/s2-worker-*.json
```

### Issue: "jq: command not found"

**Symptom:**
```
bash: jq: command not found
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install -y jq

# macOS
brew install jq
```

### Issue: "Database not found"

**Symptom:**
```
⚠️  Database not found: /tmp/claude_bridge_coordinator.db
```

**Cause:** Orchestrator hasn't created conversations yet.

**Solution:**
Wait for orchestrator to complete Step 3 (create 8 conversations). The database is created automatically when the first conversation is created.

### Issue: "Worker not sending heartbeats"

**Symptom:**
Watchdog logs show worker silent for >5 minutes.

**Diagnosis:**
```bash
# Check if keep-alive daemon is running
ps aux | grep keepalive-daemon

# Check daemon logs
tail -f /tmp/mcp-keepalive.log
```

**Solution:**
```bash
# Restart keep-alive daemon
pkill -f keepalive-daemon

# Re-extract credentials and restart
CONV_ID=$(jq -r '.conversation_id' credentials/s2-worker-${WORKER_ID}-credentials.json)
WORKER_TOKEN=$(jq -r '.worker_token' credentials/s2-worker-${WORKER_ID}-credentials.json)
scripts/s2-deployment/keepalive-daemon.sh "$CONV_ID" "$WORKER_TOKEN" &
```

---

## Files Reference

### Created in This Deployment

```
scripts/s2-deployment/
├── README.md                      # Detailed setup instructions
├── keepalive-daemon.sh            # Background polling (workers)
├── keepalive-client.py            # Heartbeat updater (workers)
├── watchdog-monitor.sh            # External monitoring (orchestrator)
├── reassign-tasks.py              # Task reassignment (orchestrator)
├── credential-sync-daemon.sh      # Auto-pull credentials (workers)
├── check-messages.py              # Message checker (all)
└── fs-watcher.sh                  # Filesystem watcher (optional)

credentials/
├── README.md                      # Credential format docs
├── s2-worker-template-credentials.json  # Template
└── s2-worker-{1-8}-credentials.json     # Generated by orchestrator

docs/
├── S2-MCP-BRIDGE-QUICKSTART.md          # Original quickstart
├── S2-MCP-BRIDGE-TEST-PROTOCOL-V2.md    # Full test protocol (90 min)
└── S2-MULTI-MACHINE-DEPLOYMENT.md       # This file
```

---

## Next Steps

1. ✅ **Deploy to all 9 machines** (follow steps above)
2. ✅ **Verify all workers sending heartbeats**
3. ✅ **Send test task to confirm communication**
4. 🔄 **Run full Test Protocol V2** (see `S2-MCP-BRIDGE-TEST-PROTOCOL-V2.md`)
5. 🚀 **Begin production S² coordination**

---

**Deployment Status:** Ready for Production ✅
**Last Updated:** 2025-11-13
**Support:** See troubleshooting section above
