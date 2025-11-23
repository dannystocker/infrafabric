# Instance #19 Starter Prompt

## Quick Load (Copy/Paste into Claude Code)

**Status:** ✅ Memory Exoskeleton **OPERATIONAL** - Bridge.php live and tested

**Current Mission:** Implement Phase A (Vector Indexing) of Memory Exoskeleton architecture

Bridge.php is now accessible via:
```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:*"
```

**Key Breakthrough from Instance #18:**
- StackCP has NO build tools (no make, gcc) - compilation not possible
- Solution: File-based JSON backend instead of Redis daemon
- Result: 105 keys (464 KB) exported from WSL, deployed to StackCP
- Status: All bridge endpoints tested and operational ✅

---

## What Works Now (Memory Exoskeleton Foundation)

**Bridge API Endpoints (Tested ✅):**

1. **Info/Health** - Check bridge status
```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=info"
# Returns: {"status": "neural_link_active", "keys_count": 105, ...}
```

2. **Keys Search** - Find keys by pattern
```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=keys&pattern=instance:16:*"
# Returns: {"pattern": "instance:16:*", "count": 3, "keys": [...]}
```

3. **Batch Retrieval** - Fetch multiple keys for Gemini context injection
```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:*"
# Returns: {"batch_size": 105, "pattern": "instance:*", "data": [...]}
```

4. **Health Check** - Monitor bridge availability
```bash
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=health"
```

---

## Instance #19 Mission: Phase A - Vector Indexing

### Objective
Implement semantic tagging and vector embedding for all 105 Redis keys so that Gemini-3-Pro can:
1. Perform **semantic search** ("What were blocker patterns?") instead of exact key lookup
2. Auto-tag entries by type, agent, topic, status
3. Enable **context injection** based on conversation topics

### Tasks for Instance #19

1. **Analyze Current Data** (30 min)
   - Extract all 105 keys from bridge.php batch endpoint
   - Categorize by instance, agent, content type
   - Identify tagging patterns (instance:X:agent:Y:topic:Z)

2. **Implement Python Indexing Script** (1-2 hours)
   - Download the Python script from `/mnt/c/users/setup/downloads/gemini-redis-input.txt` (lines 112-216)
   - Adapt to work with bridge.php (fetch via HTTP instead of proxy)
   - Generate semantic tags for all 105 keys
   - Output: indexed-keys-with-tags.json

3. **Extend bridge.php with Tagging Support** (1 hour)
   - Add `?action=tags&pattern=*` endpoint to return tags with keys
   - Add `?action=search&query=blocker` endpoint for semantic search
   - Store tagging metadata in PHP session or supplementary JSON file

4. **Test with Gemini-3-Pro** (30 min)
   - Run: `gemini "Fetch https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:16:* and summarize recent decisions"`
   - Verify context is injected automatically
   - Check semantic search works

5. **Document Phase A Completion** (30 min)
   - Create SESSION-INSTANCE-19-HANDOVER.md
   - Plan Phase B (Autopoll reflex arc) and Phase C (Recursive summarization)
   - Prepare for Phase B handover to Instance #20

---

## Key Files for Instance #19

**Read in this order:**

1. `/home/setup/infrafabric/agents.md` - Instance #18 progress (lines 2802-2876)
2. `/home/setup/infrafabric/STACKCP-AGENT-MANUAL.md` - StackCP binary paths + execution protocols
3. `/mnt/c/users/setup/downloads/gemini-redis-input.txt` - Python indexing script (lines 112-216)

**Resources Available:**

- Bridge base URL: `https://digital-lab.ca/infrafabric/bridge.php`
- Bearer token: `50040d7fbfaa712fccfc5528885ebb9b`
- Redis data file: `/digital-lab.ca/infrafabric/redis-data.json` (464 KB, 105 keys)
- Python 3.12: `/tmp/python-headless-3.12.6-linux-x86_64/bin/python3` (on StackCP)

---

## Git Reference

**Latest commit:** a866cc3 (Instance #18 starter prompt from Instance #17)

**New commits from Instance #18:**
- Bridge.php deployed (file-based backend, tested)
- Redis export script created (105 keys, 464 KB)
- STACKCP-AGENT-MANUAL.md created (execution guide)
- agents.md updated with Instance #18 progress

---

## Success Criteria for Instance #19

✅ Phase A complete when:
1. All 105 keys have semantic tags (type, agent, topic, status)
2. bridge.php supports `?action=tags` endpoint
3. `?action=search&query=X` returns relevant entries by semantic match
4. Gemini-3-Pro can inject context without explicit key lookup
5. SESSION-INSTANCE-19-HANDOVER.md prepared for Phase B

---

## Expected Outcome

After Instance #19:
- **Memory Exoskeleton** evolves from "prosthetic" (manual fetch) to "augmented cognition" (automatic context)
- Gemini-3-Pro web access fully operational with semantic search
- Phase B (Autopoll reflex arc) ready to implement in Instance #20

---

**Instance #18 Complete**
**Status:** Bridge.php OPERATIONAL ✅ | Redis data EXPORTED ✅ | All endpoints TESTED ✅
**Time:** 2025-11-23
**Handover:** Ready for Phase A (Vector Indexing)
