# Session Update: IF.notify Real-Time Coordination Integration

**Date:** 2025-11-12
**Priority:** HIGH
**Applies to:** All sessions (1-NDI, 2-WebRTC, 3-H323, 4-SIP, 5-CLI, 6-Talent, 7-IFBus)

---

## What Changed

We've implemented **IF.notify** - a real-time push notification system that replaces slow git polling (30-60s latency) with instant notifications (<10ms).

**Before:** You poll git every 30s to check for tasks
**After:** You notify the coordinator instantly when your status changes

---

## What You Need To Do

Integrate IF.notify into your session workflow by notifying the coordinator whenever your status changes:

- 🟢 **IDLE** - Ready for work
- 🔵 **BUSY** - Working on a task
- 🔴 **BLOCKED** - Stuck on a dependency
- ✅ **COMPLETED** - Finished a task
- 🆘 **HELP** - Need assistance

---

## Integration Instructions

### Step 1: Install Agent Client (Python)

Add this to your session environment:

```python
# Save as: agent_notify.py in your session directory

import requests
from datetime import datetime
from typing import List
import os

class AgentNotifier:
    """Notify IF.notify server of status changes"""

    def __init__(self, session_id: str, capabilities: List[str]):
        self.session_id = session_id
        self.capabilities = capabilities
        self.server_url = os.getenv("IFNOTIFY_URL", "http://localhost:8765")
        self.cost_spent = 0.0
        self.tasks_completed = 0
        self.current_task = None

    def _notify(self, endpoint: str, payload: dict):
        """Send notification to IF.notify server"""
        try:
            response = requests.post(
                f"{self.server_url}{endpoint}",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✓ Notified coordinator: {endpoint.upper()}")
                return response.json()
            else:
                print(f"✗ Notification failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Failed to notify coordinator: {e}")
            return None

    def idle(self, last_task: str = None):
        """Notify: Ready for work"""
        payload = {
            "session_id": self.session_id,
            "status": "idle",
            "timestamp": datetime.utcnow().isoformat(),
            "last_task": last_task or self.current_task,
            "capabilities": self.capabilities,
            "cost_spent": self.cost_spent,
            "tasks_completed": self.tasks_completed,
            "waiting_since": datetime.utcnow().isoformat()
        }
        return self._notify("/agent/idle", payload)

    def busy(self, task: str):
        """Notify: Started working on a task"""
        self.current_task = task
        payload = {
            "session_id": self.session_id,
            "status": "busy",
            "timestamp": datetime.utcnow().isoformat(),
            "last_task": task,
            "capabilities": self.capabilities,
            "cost_spent": self.cost_spent,
            "tasks_completed": self.tasks_completed
        }
        return self._notify("/agent/busy", payload)

    def blocked(self, reason: str):
        """Notify: Blocked on a dependency"""
        payload = {
            "session_id": self.session_id,
            "status": "blocked",
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": self.capabilities,
            "message": reason,
            "last_task": self.current_task
        }
        return self._notify("/agent/blocked", payload)

    def completed(self, task: str, cost: float = 0.0):
        """Notify: Completed a task"""
        self.tasks_completed += 1
        self.cost_spent += cost
        payload = {
            "session_id": self.session_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "last_task": task,
            "capabilities": self.capabilities,
            "cost_spent": self.cost_spent,
            "tasks_completed": self.tasks_completed
        }
        result = self._notify("/agent/completed", payload)
        # Automatically mark as idle after completion
        self.idle(task)
        return result

    def help(self, reason: str):
        """Notify: Need help (Gang Up on Blocker pattern)"""
        payload = {
            "session_id": self.session_id,
            "status": "help",
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": self.capabilities,
            "message": reason,
            "last_task": self.current_task
        }
        return self._notify("/agent/help", payload)

# Quick helper for bash scripts
def quick_notify(status: str, session_id: str, message: str = ""):
    """One-line notify helper for bash"""
    notifier = AgentNotifier(session_id, [])
    if status == "idle":
        notifier.idle()
    elif status == "busy":
        notifier.busy(message)
    elif status == "blocked":
        notifier.blocked(message)
    elif status == "completed":
        notifier.completed(message)
    elif status == "help":
        notifier.help(message)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        quick_notify(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
```

### Step 2: Initialize in Your Session Startup

Add this to your session startup script (or .bashrc, or session init):

```bash
# ============================================
# IF.notify Integration
# ============================================

# Set your session ID and capabilities
export SESSION_ID="session-1-ndi"  # CHANGE THIS to your session ID
export CAPABILITIES="video,ndi,streaming,production"  # CHANGE THIS to your capabilities

# Initialize notifier
python3 << 'PYTHON_INIT'
from agent_notify import AgentNotifier

# Your session configuration
notifier = AgentNotifier(
    session_id="${SESSION_ID}",
    capabilities="${CAPABILITIES}".split(",")
)

# Notify that session is starting and idle
notifier.idle("Session started")
print(f"✓ {notifier.session_id} registered with IF.notify")
PYTHON_INIT

# Helper functions for bash
notify_idle() {
    python3 -c "from agent_notify import quick_notify; quick_notify('idle', '${SESSION_ID}', '$1')"
}

notify_busy() {
    python3 -c "from agent_notify import quick_notify; quick_notify('busy', '${SESSION_ID}', '$1')"
}

notify_blocked() {
    python3 -c "from agent_notify import quick_notify; quick_notify('blocked', '${SESSION_ID}', '$1')"
}

notify_completed() {
    python3 -c "from agent_notify import quick_notify; quick_notify('completed', '${SESSION_ID}', '$1')"
}

notify_help() {
    python3 -c "from agent_notify import quick_notify; quick_notify('help', '${SESSION_ID}', '$1')"
}

echo "✓ IF.notify helpers loaded. Use: notify_idle, notify_busy, notify_blocked, notify_completed, notify_help"
```

### Step 3: Update Your Workflow

**When to Notify:**

```bash
# 1. When you start your session (already in startup script)
# Automatically notifies: IDLE

# 2. When you claim a task
notify_busy "P0.1.2-coordinator-design"

# 3. If you get blocked
notify_blocked "Waiting for IF.coordinator spec from Session 6"

# 4. When you complete a task
notify_completed "P0.1.2-coordinator-design"

# 5. If you need help
notify_help "Stuck on etcd integration, need expertise"

# 6. When waiting for new work
notify_idle

# 7. Before going offline
notify_idle "Session ending for maintenance"
```

---

## Session-Specific Configuration

### Session 1 (NDI)
```bash
export SESSION_ID="session-1-ndi"
export CAPABILITIES="video,ndi,streaming,production,vmix,obs"
```

### Session 2 (WebRTC)
```bash
export SESSION_ID="session-2-webrtc"
export CAPABILITIES="webrtc,video,streaming,real-time,browser"
```

### Session 3 (H.323)
```bash
export SESSION_ID="session-3-h323"
export CAPABILITIES="h323,legacy,protocols,security,networking"
```

### Session 4 (SIP)
```bash
export SESSION_ID="session-4-sip"
export CAPABILITIES="sip,telephony,voice,protocols,integration"
```

### Session 5 (CLI)
```bash
export SESSION_ID="session-5-cli"
export CAPABILITIES="cli,python,typescript,api,developer-tools"
```

### Session 6 (Talent)
```bash
export SESSION_ID="session-6-talent"
export CAPABILITIES="architecture,design,patterns,documentation,review"
```

### Session 7 (IF.bus)
```bash
export SESSION_ID="session-7-ifbus"
export CAPABILITIES="orchestration,integration,adapters,bus,coordination"
```

---

## Example Workflows

### Workflow 1: Normal Task Completion

```bash
# 1. Session starts up (automatic)
# -> Notifies: IDLE

# 2. Coordinator assigns task P0.1.2
notify_busy "P0.1.2-coordinator-design"

# 3. Working on task...
# (no notifications needed while working)

# 4. Task complete
notify_completed "P0.1.2-coordinator-design"

# 5. Automatically becomes IDLE, ready for next task
```

### Workflow 2: Getting Blocked

```bash
# 1. Working on task
notify_busy "P0.2.3-integration-test"

# 2. Realize you're blocked
notify_blocked "Waiting for IF.coordinator API spec from Session 6"

# 3. Pick up a filler task while waiting
notify_busy "FILLER-documentation-update"

# 4. Blocker resolved, return to main task
notify_busy "P0.2.3-integration-test"

# 5. Complete
notify_completed "P0.2.3-integration-test"
```

### Workflow 3: Need Help (Gang Up on Blocker)

```bash
# 1. Working on difficult task
notify_busy "P0.3.5-wasm-sandbox-implementation"

# 2. Stuck for 30+ minutes
notify_help "WASM compilation failing, need expertise with Rust/WASM toolchain"

# 3. Coordinator sees help request, assigns helpers
# 4. Helpers join, problem resolved
# 5. Continue working
notify_busy "P0.3.5-wasm-sandbox-implementation"

# 6. Complete
notify_completed "P0.3.5-wasm-sandbox-implementation"
```

---

## Python Integration (For Claude Code Sessions)

If you're using Claude Code with Python access:

```python
from agent_notify import AgentNotifier

# Initialize at session start
notifier = AgentNotifier(
    session_id="session-1-ndi",
    capabilities=["video", "ndi", "streaming"]
)

# Notify idle on startup
notifier.idle("Session ready")

# When starting a task
notifier.busy("P0.1.2-coordinator-design")

# If blocked
notifier.blocked("Waiting for dependency X")

# When complete
notifier.completed("P0.1.2-coordinator-design", cost=2.50)

# If need help
notifier.help("Stuck on etcd integration")
```

---

## Testing Your Integration

1. **Test notification manually:**
```bash
# From your session, run:
notify_idle "Testing IF.notify integration"

# You should see:
# ✓ Notified coordinator: /AGENT/IDLE
```

2. **Verify on coordinator dashboard:**
```bash
# Coordinator runs:
curl http://localhost:8765/status | jq

# Should see your session listed
```

3. **Test all statuses:**
```bash
notify_busy "Test task"
notify_blocked "Test blocker"
notify_completed "Test task"
notify_help "Test help request"
notify_idle "Back to idle"
```

---

## Troubleshooting

### Problem: "Connection refused"
**Solution:** IF.notify server not running. Coordinator needs to start:
```bash
python src/infrafabric/notify_server.py
```

### Problem: "Module not found: agent_notify"
**Solution:** Copy `agent_notify.py` to your session directory or add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Problem: "Notifications not appearing on dashboard"
**Solution:** Check server URL is correct:
```bash
echo $IFNOTIFY_URL
# Should be: http://localhost:8765

# Or test manually:
curl http://localhost:8765/status
```

---

## Benefits for You

1. **Coordinator knows your status instantly** (<10ms vs 30-60s)
2. **No more wasted time polling** - just notify once
3. **Auto-escalation when blocked** - coordinator sees immediately
4. **Gang Up on Blocker** - help requests auto-match with capable idle agents
5. **Transparent workload** - coordinator can balance tasks better

---

## FAQ

**Q: Do I still need to poll git for tasks?**
A: For now, yes. IF.notify handles status notifications, but task assignment still uses git polling. When Phase 0 (IF.coordinator) is built, task assignment will also be push-based.

**Q: What if IF.notify server is down?**
A: Notifications fail silently. You can still work normally. Git polling continues as backup.

**Q: How often should I notify?**
A: Only when your status changes:
- Idle → Busy (claimed task)
- Busy → Completed (finished task)
- Busy → Blocked (hit dependency)
- Blocked → Busy (dependency resolved)
- Any → Help (need assistance)

**Q: Does this replace git commits?**
A: No! Still commit your work to git. IF.notify is only for real-time status updates.

**Q: What's the cost impact?**
A: Near zero. Each notification is <1ms and uses negligible tokens. The webhook server runs locally with no API costs.

---

## Timeline

- **Now:** Integrate IF.notify into your session
- **Phase 0:** IF.notify migrates into IF.coordinator
- **Phase 6:** IF.swarm uses IF.notify for AI agent coordination

---

## Questions?

If you have questions about IF.notify integration:

1. Check the full documentation: `docs/IF-NOTIFY-REALTIME-COORDINATION.md`
2. Ask coordinator for clarification
3. Test with `curl http://localhost:8765/status` to verify server is running

---

## Success Criteria

✅ Session startup automatically notifies IDLE
✅ Notify BUSY when claiming a task
✅ Notify BLOCKED when stuck
✅ Notify COMPLETED when done
✅ Notify HELP when need assistance
✅ Your session appears on coordinator dashboard

Once integrated, coordinator will have real-time visibility into your status and can assign work more efficiently!

---

**Action Required:** Please integrate IF.notify into your session startup and workflow, then notify "Session ready - IF.notify integrated" when complete.
