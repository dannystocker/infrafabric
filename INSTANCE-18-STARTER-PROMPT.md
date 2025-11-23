# Instance #18 Starter Prompt

## Quick Load (Copy/Paste into Claude Code)

```
Read /home/setup/infrafabric/SESSION-INSTANCE-17-HANDOVER.md first (critical blocker documented).

Then read /mnt/c/users/setup/downloads/gemini-redis-input.txt (Gemini's Memory Exoskeleton strategy).

Mission: Deploy bridge.php to enable Gemini CLI web access to Redis context.

Current status: PHP Redis proxy deployed but blocked - StackCP cannot reach localhost:6379.

Three options:
1. Deploy bridge.php with PHP Redis extension (2-3 hours) - RECOMMENDED
2. Verify PHP extension enabled on StackCP (30 min)
3. Create local Node.js proxy + tunneling (4-6 hours)

Deliverable: Working Gemini --web access to Redis context via https://digital-lab.ca/infrafabric/bridge.php

Reference files:
- Handover: /home/setup/infrafabric/SESSION-INSTANCE-17-HANDOVER.md
- Strategy: /mnt/c/users/setup/downloads/gemini-redis-input.txt
- API Docs: /mnt/c/users/setup/downloads/REDIS-GEMINI-WEB-API.md
- Source Code: /tmp/redis-proxy-index.php (already deployed to StackCP)
```

---

## Full Context (If Needed)

**What was accomplished in Instance #17:**
- Fixed all URL parameter indices in PHP Redis proxy (5 endpoints corrected)
- Deployed .htaccess routing to StackCP
- Verified Redis integrity (79 keys, 4 instance shards, 445 KB)
- Created backup ZIP + API documentation
- **DISCOVERED BLOCKER:** StackCP cannot access localhost:6379 Redis

**Critical Discovery:**
Previous session assumed redis-cli would be available on StackCP shared hosting. This was wrong.
- Redis is on localhost:6379 (your WSL machine)
- StackCP has no redis-cli binary
- PHP Redis extension status: UNKNOWN

**Gemini's Strategic Guidance** (from gemini-redis-input.txt):
- Current system: "Memory Prosthetic" (manual fetch-only)
- Target: "Memory Exoskeleton" (actively integrated)
- 3-Phase upgrade path with vector indexing + autopoll reflex arc
- Immediate fix: bridge.php (secured API endpoint)

**What Needs to Happen Next:**
Option 1 (Recommended): Deploy bridge.php
- Uses PHP Redis() extension (if available)
- Secured with Bearer token
- Enables batch operations + semantic tagging
- Test with: `curl -H "Authorization: Bearer sk_mem_exoskeleton_882910" https://digital-lab.ca/infrafabric/bridge.php?action=info`

Option 2: Verify PHP extension
- Check: `ssh stackcp "php -m | grep redis"`
- If missing, request StackCP enable php-redis

Option 3: Local proxy + tunneling
- Create Node.js proxy on localhost:6380
- Use ngrok/localtunnel for public HTTPS
- More work but gives full control

**Files Ready:**
- bridge.php code: gemini-redis-input.txt lines 247-352
- Python indexing script: gemini-redis-input.txt lines 112-216
- Complete test checklist: SESSION-INSTANCE-17-HANDOVER.md
- All credentials documented in handover

**Success Criteria:**
1. bridge.php deployed and secured
2. curl test returns valid JSON
3. Gemini CLI can fetch context via --web flag
4. Redis context integrated (not manual fetch)

---

## Files to Read (In Order)

1. `/home/setup/infrafabric/SESSION-INSTANCE-17-HANDOVER.md` - **START HERE** (225 lines)
2. `/mnt/c/users/setup/downloads/gemini-redis-input.txt` - Strategic vision (398 lines)
3. `/mnt/c/users/setup/downloads/REDIS-GEMINI-WEB-API.md` - API reference (358 lines)
4. `/home/setup/infrafabric/agents.md` - Project overview (if needed for context)

---

## Git Reference

**Latest commit:** `3f7e196` - "Instance #17: Add Redis proxy blocker discovery and Memory Exoskeleton strategy"

**Branch:** yologuard/v3-publish

**Key files in repo:**
- SESSION-INSTANCE-17-NARRATION.md (280 lines) - Session arc narrative
- SESSION-INSTANCE-17-HANDOVER.md (225 lines) - Blockers + 3 solution options
- SESSION-RESUME.md (1,034 lines - master handover)
- agents.md (comprehensive project docs with Instance #17 section added)

---

## Credentials & Paths

```
Redis:
  Host: localhost
  Port: 6379
  Data: 79 keys, 4 shards, 445 KB

StackCP:
  SSH: ssh.gb.stackcp.com
  User: digital-lab.ca
  Key: ~/.ssh/icw_stackcp_ed25519
  Proxy: /home/sites/7a/c/cb8112d0d1/public_html/digital-lab.ca/infrafabric/proxy/

Backup:
  ZIP: /mnt/c/users/setup/downloads/redis-context-by-shards.zip
  Organized by instance shards (11, 12, 13, 16)
```

---

## Expected Outcome

After this session completes:
- Gemini CLI can run: `gemini --web "Fetch https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:16:*"`
- Redis context flows into Gemini automatically
- Foundation laid for Phase A (vector indexing) + Phase B (autopoll) + Phase C (recursive learning)
