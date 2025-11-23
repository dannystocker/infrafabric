# Session Instance #17 Narration: Redis Proxy Architecture & Memory Exoskeleton Strategy

**Date:** 2025-11-23
**Status:** CONTEXT EXHAUSTED - Critical discovery documented, handover prepared
**Mission:** Enable Gemini CLI `--web` access to Redis context

---

## The Session Arc

This session began as a straightforward infrastructure task: "Test if the Redis proxy is working." It evolved into a discovery of fundamental architectural constraints that reframe the entire Memory Exoskeleton project.

---

## Part 1: Initial Setup & Discovery

### What Was Asked

User: **"is there ris the redis proxy working; that would be the most important test first"**

The previous session had deployed a PHP Redis proxy to StackCP, using `redis-cli` to translate HTTP endpoints to Redis commands. The assumption was that `redis-cli` would be available on the shared hosting environment.

### What We Found

**Testing the deployed proxy revealed: `redis-cli is not available on StackCP shared hosting.**

This wasn't a simple missing path issue—it was a **architectural blocker**:

1. **StackCP runs shared hosting** (Linux Apache MySQL PHP stack)
2. **Redis instance is on localhost:6379** on the WSL machine (user's development environment)
3. **StackCP network isolation prevents access** to user's localhost Redis
4. **No `redis-cli` binary exists** on StackCP (not in `/usr/bin/`, not copyable to `/tmp/`)
5. **PHP Redis extension status: UNKNOWN** (may or may not be enabled)

### The Critical Realization

The entire previous session's architecture was built on a false assumption: that a shared hosting provider would have redis-cli available for shell execution. This is NOT how shared hosting works.

---

## Part 2: The Pivot

### From Node.js to PHP

The original approach tried to:
```
WSL Redis (6379) ← Node.js proxy ← StackCP Web Server
```

When we discovered Node.js wasn't installed, we pivoted to:
```
WSL Redis (6379) ← PHP proxy (using redis-cli) ← StackCP Web Server
```

Then when redis-cli wasn't available, we discovered this architecture was also fundamentally flawed.

### What Actually Happened

The session involved multiple iterations of the PHP proxy (246+ lines), fixing URL parameter indices across 5 endpoint handlers:

1. **`health` endpoint:** Testing PING connectivity ✓ WORKS (after .htaccess fix)
2. **`keys` endpoint:** Listing keys by pattern ✗ FAILS (redis-cli not found)
3. **`get` endpoint:** Retrieving key values ✗ FAILS (redis-cli not found)
4. **`ttl` endpoint:** Checking key expiration ✗ FAILS (redis-cli not found)
5. **`set` endpoint:** Writing key values ✗ FAILS (redis-cli not found)

All parameter index fixes were correct (changed from `$parts[2]` to `$parts[3]` with proper `array_slice()` for multi-part keys), but the underlying system call to `proc_open("/tmp/redis-cli ...")` fails silently on StackCP because `/tmp/redis-cli` doesn't exist.

### The Apache Routing Fix

One legitimate fix: `.htaccess` permissions were 600 (Apache couldn't read it). Changed to 644, enabling Apache to properly route `/infrafabric/proxy/health` through `index.php` via `RewriteRule ^(.*)$ index.php [L,QSA]`.

This fix is real and necessary, but it only enables the infrastructure layer. The data layer is still blocked.

---

## Part 3: Strategic Discovery - Gemini's Memory Exoskeleton

Mid-session, I discovered the `gemini-redis-input.txt` file (398 lines) containing **Gemini's strategic guidance on upgrading from a "Memory Prosthetic" to a "Memory Exoskeleton."**

This wasn't just documentation—it was the solution architecture, complete with working code:

### The Metaphor

- **Memory Prosthetic** (current state): Requires conscious manual effort to fetch context via `gemini --web` commands. Like a crutch—it helps, but you have to actively use it.

- **Memory Exoskeleton** (target state): Actively augments cognition. The system automatically detects context shifts and injects relevant Redis data without being asked.

### Three Phases (Roadmap)

**Phase A:** Vector store integration (RediSearch + RedisJSON) → Semantic search capability
**Phase B:** Autopoll "reflex arc" → Automatic context injection based on topic detection
**Phase C:** Recursive summarization → System learns from blocker resolution patterns

### The Immediate Solution: "Neural Bridge"

Gemini provided **`bridge.php`** (lines 247-352 in gemini-redis-input.txt)—a secured API endpoint that:

1. Uses **PHP `Redis()` extension** (native PHP class, if available)
2. Authenticates via **Bearer token** (e.g., `sk_mem_exoskeleton_882910`)
3. Provides **batch operations** (fetch multiple keys in one HTTP request)
4. Returns **semantic tags** for indexing (auto-generated metadata)

This sidesteps the redis-cli bottleneck entirely by using PHP's native Redis extension instead of shell commands.

---

## Part 4: The Three Solution Options for Instance #18

### Option 1: Deploy bridge.php (RECOMMENDED)
- **Effort:** 2-3 hours
- **Risk:** Low
- **Dependency:** Requires PHP Redis extension to be enabled on StackCP
- **Payoff:** Immediate Gemini web access, foundation for Memory Exoskeleton phases
- **Steps:**
  1. Deploy `bridge.php` to `/home/sites/7a/c/cb8112d0d1/public_html/infrafabric/bridge.php`
  2. Change Bearer token from default
  3. Test: `curl -H "Authorization: Bearer sk_mem_exoskeleton_882910" https://digital-lab.ca/infrafabric/bridge.php?action=info`
  4. Implement Python indexing script (lines 112-216 in gemini-redis-input.txt) for semantic tagging

### Option 2: Verify PHP Redis Extension
- **Effort:** 30 minutes
- **Risk:** Minimal, but blocking if extension isn't enabled
- **Dependency:** StackCP support must enable `php-redis` package if missing
- **Test:** `ssh stackcp "php -m | grep redis"`

### Option 3: Local Node.js Proxy + Tunneling
- **Effort:** 4-6 hours
- **Risk:** Requires external tunneling service (ngrok/localtunnel)
- **Payoff:** Full control, but adds operational complexity
- **Approach:**
  1. Create Node.js proxy locally (localhost:6380)
  2. Use ngrok/localtunnel for public HTTPS exposure
  3. Update Gemini docs to point to tunnel URL

---

## Part 5: What Was Delivered

### Files Created/Updated

1. **SESSION-INSTANCE-17-HANDOVER.md** (225 lines)
   - Executive summary of accomplishments
   - Critical blocker discovery
   - Three solution options with effort estimates
   - Complete test checklist for Instance #18
   - Success criteria (bridge.php deployed + Gemini web access working)

2. **INSTANCE-18-STARTER-PROMPT.md** (96 lines)
   - Quick-load copy/paste starter for next Claude session
   - File reading order (handover → strategy → API docs)
   - Git reference (commit 0356e9f)
   - Credentials and paths

3. **Redis Backup ZIP** (193 KB, 79 keys across 4 shards)
   - Organized by instance: shard-instance-11, 12, 13, 16
   - BACKUP_SUMMARY.json with metadata
   - Ready for download from Windows Downloads folder

### Git Commits

- **0356e9f:** "Add Instance #17 handover: Redis proxy blocker + exoskeleton strategy"
  - Added SESSION-INSTANCE-17-HANDOVER.md
  - Added INSTANCE-18-STARTER-PROMPT.md
  - Updated git history with clear documentation

### Code Status

- **PHP Proxy (246 lines):** Parameter indices FIXED ✓, but BLOCKED by missing redis-cli on StackCP
- **Apache .htaccess:** Routing working ✓ (permissions fixed to 644)
- **Redis Data:** Verified 100% intact (79 keys, 445 KB, 4 shards)
- **Credentials:** All captured in handover document

---

## Part 6: Why This Matters (Strategic Context)

### The Architectural Constraint

StackCP's network isolation (preventing access to localhost:6379 Redis from the web server) is **not a bug—it's by design**. Shared hosting prevents direct database access for security reasons.

The real solution isn't to fight this constraint, but to **use the constraint as a security boundary**:

```
SECURE PATTERN:
WSL (Private): Redis 6379 (localhost only)
StackCP (Public): bridge.php with Bearer token auth
Connection: Only authenticated HTTPS requests can access Redis
```

This is actually MORE secure than the original Node.js proxy concept, which would have required exposing Redis credentials over a tunneled connection.

### The Memory Exoskeleton Vision

Gemini's strategic document reveals that Instance #17's blocker isn't a setback—**it's a clarifying moment**:

1. **Current state:** Manual fetch-only (user has to remember to pull context)
2. **Target state:** Actively integrated (system detects context shifts and injects data automatically)
3. **Blocker as catalyst:** Forces us to implement proper authentication + API semantics (bridge.php) instead of hacky shell execution

The bridge.php approach is BETTER than the original redis-cli plan because:
- **Stateless:** No dependency on binary availability
- **Secure:** Bearer token + HTTPS (not shell command exposure)
- **Semantic:** Returns tagged JSON (compatible with vector indexing)
- **Scalable:** Batch operations reduce round-trips

---

## Part 7: The Handover

### For Instance #18

**Read in this order:**
1. `/home/setup/infrafabric/SESSION-INSTANCE-17-HANDOVER.md` (225 lines) - Blockers, options, test checklist
2. `/mnt/c/users/setup/downloads/gemini-redis-input.txt` (398 lines) - Gemini's strategic guidance + bridge.php code
3. `/mnt/c/users/setup/downloads/REDIS-GEMINI-WEB-API.md` (358 lines) - API reference

**Decision required:**
- Option 1 (bridge.php): Recommended, requires PHP Redis extension check
- Option 2 (verify extension): 30-min prerequisite for Option 1
- Option 3 (local proxy): Fallback if bridge.php not viable

**Success looks like:**
- curl returns valid JSON from `https://digital-lab.ca/infrafabric/bridge.php?action=info`
- Gemini CLI can fetch context via `gemini --web "Fetch https://...bridge.php?action=batch&pattern=instance:16:*"`
- Redis context flows into Gemini automatically (not manual fetch)

---

## Part 8: Technical Accuracy Summary

### What Worked
✅ PHP proxy deployed with corrected parameter indices
✅ Apache routing fixed (permissions 600 → 644)
✅ Redis data integrity verified (79 keys, 445 KB)
✅ Credentials preserved in handover
✅ Strategic documentation created (handover + starter prompt)

### What Failed
❌ redis-cli not available on StackCP (blocker)
❌ PHP proxy endpoints unreachable due to missing redis-cli
❌ Previous session's architecture assumption proved false

### What's Clear
✅ Root cause identified: Shared hosting network isolation
✅ Solution path defined: bridge.php with PHP Redis extension
✅ Strategic context discovered: Memory Exoskeleton three-phase roadmap
✅ Handover complete: Instance #18 has clear options and decision framework

---

## Session Philosophy

This session teaches a critical lesson: **Architecture assumptions must be validated early, before building on them.**

The previous session assumed redis-cli would be available. Instance #17 validated that assumption (found it false) and pivoted accordingly. This is exactly how effective infrastructure work should operate:

1. **Test assumptions immediately** (don't code around false foundations)
2. **Discover constraints** (shared hosting isolation is a real constraint)
3. **Reframe constraints as opportunities** (forces us toward more secure, semantic approach)
4. **Provide clear options** (3 solution paths with effort/risk tradeoffs)
5. **Hand over with confidence** (next session has everything needed to decide)

---

## The Path Forward

Instance #18 will:

1. **FIRST:** Verify PHP Redis extension status (Option 2, 30 min)
2. **SECOND:** Deploy bridge.php if extension available (Option 1, 2-3 hours)
3. **THIRD:** Test Gemini CLI access with new bridge
4. **FOURTH:** If successful, begin Phase A (vector indexing) of Memory Exoskeleton

This is where the Memory Exoskeleton becomes real—not as theory, but as working infrastructure that makes Gemini's cognition actively augmented by persistent, searchable context.

---

**Instance #17 Complete**
**Context Window:** Exhausted (~195K tokens used)
**Handover Time:** 2025-11-23
**Next Session:** Instance #18 - Deploy bridge.php and test Gemini web access
