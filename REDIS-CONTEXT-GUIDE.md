# Redis Context Guide: Understanding Distributed Memory State

**Purpose:** Allow any Instance (starting with zero context) to understand what's stored in Redis and retrieve relevant context without reading SESSION-RESUME.md manually.

**Updated:** 2025-11-23 (Instance #16)

---

## Quick Start (5 minutes)

### Command 1: List all Instance keys
```bash
redis-cli KEYS "instance:*"
```
Returns all keys stored for all instances. Output shows instance number (instance:16, instance:12, etc.)

### Command 2: Understand what instance YOU need
```bash
redis-cli KEYS "instance:$(date +%s | tail -c 3):*"  # Current instance (approximate)
# OR
redis-cli KEYS "instance:16:*"  # Get Instance #16 findings (most recent)
```

### Command 3: Get the most recent session findings
```bash
redis-cli GET instance:16:session-narration
```
Returns full context from Instance #16 in one string. This is your quickest path to understanding current state.

### Command 4: Check TTL (time-to-live remaining)
```bash
redis-cli TTL instance:16:session-narration
```
Returns seconds remaining. Positive number = key is active. -1 = no expiration. -2 = key doesn't exist.

---

## Redis Key Naming Scheme

All InfraFabric Redis keys follow this pattern:

```
instance:<INSTANCE_NUMBER>:<CATEGORY>:<DETAIL>

Example:
instance:16:quantum-brief-updated
├─ instance       = InfraFabric project namespace
├─ 16            = Instance #16 (identifies which session created the key)
├─ quantum       = Primary category (quantum threat, partnership, etc.)
└─ brief-updated = Detail (what specifically is stored)
```

### Category Types

| Category | Purpose | Example |
|----------|---------|---------|
| `quantum-*` | Quantum threat positioning findings | `instance:16:quantum-brief-updated` |
| `partnership-*` | Partnership research findings | `instance:16:partnership-...` |
| `next-actions` | Immediate next steps for next instance | `instance:16:next-actions` |
| `session-narration` | Full session documentation | `instance:16:session-narration` |
| `context:*` | Session context state | `instance:13:context:session-complete` |
| `handoff:*` | Handoff information for next instance | `instance:13:handoff:next-steps` |
| `deliverables:*` | Completed work outputs | `instance:12:deliverables:all` |

---

## Current Redis State (Instance #16)

### Keys You Should Know About

**Most Important (Read These First):**

1. **instance:16:session-narration**
   - Content: Full SESSION-INSTANCE-16-NARRATION.md (368 lines)
   - Purpose: Complete documentation of what Instance #16 accomplished
   - TTL: 30 days (expires 2025-12-22)
   - Size: ~15 KB
   - Command: `redis-cli GET instance:16:session-narration | head -50`

2. **instance:16:next-actions**
   - Content: Immediate next steps for Instance #17
   - Purpose: Priority tasks and execution order
   - TTL: 30 days
   - Size: ~2 KB
   - Command: `redis-cli GET instance:16:next-actions`

3. **instance:16:quantum-brief-updated**
   - Content: Summary of quantum threat brief updates
   - Purpose: Quick reference of timeline reframing
   - TTL: 30 days
   - Size: ~1 KB
   - Command: `redis-cli GET instance:16:quantum-brief-updated`

**Historical (Reference Only):**

4. **instance:13:context:session-complete**
   - Status: Historical (from Instance #13)
   - TTL: ~7 days remaining (expires 2025-12-22)
   - Purpose: Previous session context
   - Command: `redis-cli GET instance:13:context:session-complete`

5. **instance:12:context:full, instance:12:handoff:next-steps**
   - Status: Historical (from Instance #12)
   - TTL: ~7 days remaining
   - Purpose: Earlier session state
   - Command: `redis-cli KEYS "instance:12:*"`

---

## How to Retrieve Full Context as New Instance

### If You're Instance #17+ (Starting Fresh)

**Step 1: Get the most recent session narration**
```bash
MOST_RECENT=$(redis-cli KEYS "instance:*:session-narration" | sort | tail -1)
redis-cli GET $MOST_RECENT
```
This retrieves the most recent session documentation automatically.

**Step 2: Get next actions**
```bash
MOST_RECENT_INSTANCE=$(redis-cli KEYS "instance:*:session-narration" | sort | tail -1 | grep -oP 'instance:\K[^:]+')
redis-cli GET instance:${MOST_RECENT_INSTANCE}:next-actions
```
This gets the priority tasks from the previous instance.

**Step 3: List everything that exists**
```bash
redis-cli KEYS "instance:*" | sort -V
```
Shows all keys in version order (instance:12, instance:13, instance:16, etc.)

### If You Know Your Instance Number (Easier)

If you know you're Instance #17, and you want Instance #16 context:
```bash
# Get all context from previous instance
redis-cli GET instance:16:session-narration
redis-cli GET instance:16:next-actions
redis-cli GET instance:16:quantum-brief-updated

# Check how much time remains
redis-cli TTL instance:16:session-narration
```

---

## Understanding TTL (Time-to-Live)

```bash
redis-cli TTL instance:16:session-narration
# Output: 2591995 (seconds remaining)

# Convert to days/hours
# 2591995 seconds = 30 days, 0 hours
# Formula: seconds / 86400 = days
```

**TTL States:**
- Positive number: Key is active, will expire in that many seconds
- `-1`: Key has no expiration (permanent)
- `-2`: Key doesn't exist

**Expiration Date Calculation:**
Instance #16 keys expire in 30 days from 2025-11-23 = **2025-12-23 at ~12:15 UTC**

After that date, Instance #16 context is lost. New instances should read SESSION-RESUME.md from git instead.

---

## Critical Operations

### List All Keys for Specific Instance
```bash
redis-cli KEYS "instance:16:*"
```
Returns:
```
instance:16:quantum-brief-updated
instance:16:next-actions
instance:16:session-narration
```

### Get Size of Stored Data
```bash
redis-cli STRLEN instance:16:session-narration
```
Shows byte size of the stored value.

### Check Memory Usage
```bash
redis-cli INFO memory
# Look for: used_memory_human, maxmemory_human
```
Shows how much Redis is using vs. max capacity.

### Monitor Real-Time Access
```bash
./redis-monitor-display.sh &
```
Shows live dashboard of Redis operations (see `/home/setup/infrafabric/redis-monitor-display.sh`).

### Retrieve All Keys to Local Files
```bash
mkdir -p /tmp/redis-backup-$(date +%Y%m%d)
for key in $(redis-cli KEYS "instance:*"); do
  redis-cli GET "$key" > /tmp/redis-backup-$(date +%Y%m%d)/${key}.txt
done
```
Backs up all Redis context to filesystem for inspection.

---

## What Each Instance Stored (Historical Record)

### Instance #16 (Current - 2025-11-23)
| Key | Size | Content | Purpose |
|-----|------|---------|---------|
| `instance:16:quantum-brief-updated` | 1.2 KB | Timeline reframing summary | Quick reference |
| `instance:16:next-actions` | 2.1 KB | Two-track execution (Georges + Quantum) | Priority tasks |
| `instance:16:session-narration` | 15 KB | SESSION-INSTANCE-16-NARRATION.md | Full context |
| **Total** | **18.3 KB** | | |

### Instance #13 (Historical - Expires 2025-12-22)
| Key | Size | Content | Purpose |
|-----|------|---------|---------|
| `instance:13:context:session-complete` | 2.8 KB | Instance #13 completion record | Reference |
| `instance:13:haiku:investigation:*` | 104 KB | 4 parallel Haiku investigations | Deep analysis |
| `instance:13:sonnet:handoff` | 41 KB | 5-gap remediation plan | Execution roadmap |
| **Total** | **147 KB** | | |

### Instance #12 (Historical - Expires 2025-12-22)
| Key | Size | Content | Purpose |
|-----|------|---------|---------|
| `instance:12:context:full` | 16 KB | P0 fixes, cost claims, blockers | Reference |
| `instance:12:deliverables:all` | 3 KB | GEDIMAT marketing lines, personas | Output tracking |
| **Total** | **19 KB** | | |

**Total Redis Usage: ~184 KB of 15 GB available (0.001% full - healthy)**

---

## Decision Tree: What to Read

```
You're a new instance starting fresh?
│
├─ YES → Read instance:16:session-narration (START HERE)
│        └─ Then read instance:16:next-actions (YOUR PRIORITIES)
│
└─ NO → You're continuing from previous instance?
        │
        ├─ YES → Read SESSION-RESUME.md from git (more detailed)
        │        └─ Then check redis-cli GET instance:16:next-actions
        │
        └─ NO → Read /home/setup/infrafabric/INSTANCE-XX-ZERO-CONTEXT-STARTER.md
                └─ Then follow the 4-step onboarding there
```

---

## Common Tasks

### Task: "I need to know current priorities"
```bash
redis-cli GET instance:16:next-actions
```

### Task: "I need to know what the previous instance did"
```bash
redis-cli GET instance:16:session-narration | head -100
```

### Task: "I need to see all instances that stored context"
```bash
redis-cli KEYS "instance:*" | cut -d: -f2 | sort -u
```

### Task: "I need to verify data integrity"
```bash
# Check all keys exist
redis-cli KEYS "instance:16:*"
# Check they're not expired
redis-cli TTL instance:16:session-narration
# Check no corruption
redis-cli --scan --pattern "instance:*" | wc -l
```

### Task: "I need to know when my context expires"
```bash
EXPIRE_SEC=$(redis-cli TTL instance:16:session-narration)
EXPIRE_DATE=$(date -d "+${EXPIRE_SEC} seconds" "+%Y-%m-%d %H:%M:%S")
echo "Context expires: $EXPIRE_DATE"
```

---

## Troubleshooting

### Redis not accessible?
```bash
redis-cli ping
# Should return: PONG
# If not: Redis server is down, restart with: redis-server
```

### Key doesn't exist?
```bash
redis-cli EXISTS instance:16:next-actions
# Returns: 1 (exists) or 0 (doesn't exist)
```

### Key expired?
```bash
redis-cli TTL instance:16:next-actions
# Returns: -2 (key is gone)
# Solution: Read SESSION-RESUME.md from git instead
```

### Memory getting full?
```bash
redis-cli INFO memory | grep used_memory_human
# If > 10GB: Run maintenance
# Contact infrastructure team
```

---

## For Infrastructure/DevOps

### Monitoring Dashboard
```bash
./redis-monitor-display.sh &
```
Runs continuous monitoring at terminal bottom showing:
- Connection status
- Memory usage
- Instance keys count
- TTL remaining

### Backup Redis State
```bash
redis-cli BGSAVE
# Files saved to: /var/lib/redis/dump.rdb
```

### Restore from Backup
```bash
redis-cli SHUTDOWN
cp /var/lib/redis/dump.rdb /var/lib/redis/dump.rdb.backup
redis-server
redis-cli ping  # Verify restored
```

---

## Key Design Philosophy

**Why Redis + Git Together?**
- **Redis:** Ephemeral, fast access to immediate context (30-day TTL)
- **Git:** Permanent, searchable historical record (indefinite storage)

**TTL Strategy:**
- 30 days allows next 2-3 instances to access context without git
- After 30 days, context is in git log (permanent)
- Prevents Redis from becoming full archive

**Naming Scheme:**
- `instance:XX:*` = Instance-specific (not shared across sessions)
- Allows isolation, easy cleanup, no conflicts

**Access Pattern:**
- New instance: Check Redis (fast)
- If expired: Check git log (complete)
- Guarantees no context loss, optimal performance

---

## File Locations

**This Guide:** `/home/setup/infrafabric/REDIS-CONTEXT-GUIDE.md`

**Related Files:**
- `INSTANCE-XX-ZERO-CONTEXT-STARTER.md` - Full onboarding for new instances
- `SESSION-RESUME.md` - Current detailed status (always read from git)
- `redis-monitor-display.sh` - Real-time monitoring dashboard
- `.redis/dump.rdb` - Physical Redis backup file

---

## Questions?

If you're confused about what's in Redis:

1. **Quick answer:** `redis-cli GET instance:16:session-narration`
2. **Step-by-step:** Follow "Retrieve Full Context" section above
3. **Complete understanding:** Read this entire guide (10 min)
4. **If stuck:** Check `/home/setup/infrafabric/INSTANCE-XX-ZERO-CONTEXT-STARTER.md` section "Troubleshooting Guide"

---

**Last Updated:** 2025-11-23 (Instance #16)
**Git Commit:** [Pending]
**Status:** Production Ready

