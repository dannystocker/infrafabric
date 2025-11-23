# Bridge v2.0 Deployment Guide - Semantic Search Edition

**Version:** 2.0.0
**Instance:** #19 Phase A
**Date:** 2025-11-23
**Status:** Ready for deployment

---

## What's New in v2.0

### New Endpoints

1. **`?action=tags`** - Retrieve semantic tags for keys
   ```bash
   curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=tags&pattern=instance:*"
   ```

   Response:
   ```json
   {
     "pattern": "instance:*",
     "count": 58,
     "tags": [
       {
         "key": "instance:12:context:...",
         "topics": ["documentation", "partnership", "redis"],
         "agents": ["sonnet", "haiku"],
         "content_type": "session_context",
         "status": "archived",
         "importance": "medium"
       }
     ]
   }
   ```

2. **`?action=search&query=X`** - Semantic search across all keys
   ```bash
   curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
     "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership"
   ```

   Response:
   ```json
   {
     "query": "partnership",
     "method": "semantic",
     "count": 23,
     "results": [
       {
         "key": "instance:12:strategy:partnership",
         "score": 15,
         "tags": {
           "topics": ["partnership", "cost", "deployment"],
           "agents": ["sonnet"],
           "type": "strategic",
           "status": "completed"
         }
       }
     ]
   }
   ```

### Enhanced Info Endpoint

Now includes semantic tag statistics:
```json
{
  "status": "neural_link_active",
  "version": "2.0.0",
  "keys_count": 105,
  "semantic_tags_available": true,
  "tag_statistics": {
    "total_tagged_keys": 105,
    "unique_topics": 10,
    "unique_agents": 4
  }
}
```

---

## Deployment Steps

### Step 1: Generate Semantic Tags (COMPLETED ✅)

Already done:
- `/tmp/redis-semantic-tags.json` (32 KB) - Full analysis
- `/tmp/redis-semantic-tags-bridge.json` (36 KB) - Bridge-compatible format

### Step 2: Upload Files to StackCP

**Method A: Using SCP**
```bash
# Upload bridge v2.0
scp /home/setup/infrafabric/swarm-architecture/bridge-v2.php \
    digital-lab.ca@ssh.gb.stackcp.com:~/public_html/digital-lab.ca/infrafabric/bridge.php

# Upload semantic tags
scp /tmp/redis-semantic-tags-bridge.json \
    digital-lab.ca@ssh.gb.stackcp.com:~/public_html/digital-lab.ca/infrafabric/redis-semantic-tags.json

# Backup old version first
ssh digital-lab.ca@ssh.gb.stackcp.com \
    "cd ~/public_html/digital-lab.ca/infrafabric && cp bridge.php bridge-v1.1.backup.php"
```

**Method B: Manual Upload**
1. Login to StackCP File Manager
2. Navigate to: `/public_html/digital-lab.ca/infrafabric/`
3. Backup existing `bridge.php` → `bridge-v1.1.backup.php`
4. Upload `bridge-v2.php` → rename to `bridge.php`
5. Upload `redis-semantic-tags-bridge.json` → rename to `redis-semantic-tags.json`

### Step 3: Test Endpoints

```bash
# 1. Test info (should show v2.0.0)
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"

# 2. Test tags endpoint
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=tags&pattern=finding:*"

# 3. Test semantic search
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership"

# 4. Test batch (ensure backward compatibility)
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:12:*"

# 5. Test health
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=health"
```

### Step 4: Verify Semantic Tags File

```bash
# Check file exists and is readable
ssh digital-lab.ca@ssh.gb.stackcp.com \
  "ls -lh ~/public_html/digital-lab.ca/infrafabric/redis-semantic-tags.json"

# Verify JSON is valid
ssh digital-lab.ca@ssh.gb.stackcp.com \
  "cd ~/public_html/digital-lab.ca/infrafabric && /tmp/python-headless-3.12.6-linux-x86_64/bin/python3 -m json.tool redis-semantic-tags.json > /dev/null && echo 'Valid JSON'"
```

---

## Rollback Plan

If anything breaks:

```bash
# Restore v1.1 backup
ssh digital-lab.ca@ssh.gb.stackcp.com \
  "cd ~/public_html/digital-lab.ca/infrafabric && cp bridge-v1.1.backup.php bridge.php"

# Test original endpoints still work
curl -H "Authorization: Bearer 50040d7fbfaa712fccfc5528885ebb9b" \
  "https://digital-lab.ca/infrafabric/bridge.php?action=info"
```

---

## Files Summary

### Local Files (Ready for Deployment)
- **bridge-v2.php** (11 KB)
  - Path: `/home/setup/infrafabric/swarm-architecture/bridge-v2.php`
  - Destination: `~/public_html/digital-lab.ca/infrafabric/bridge.php`

- **redis-semantic-tags-bridge.json** (36 KB)
  - Path: `/tmp/redis-semantic-tags-bridge.json`
  - Destination: `~/public_html/digital-lab.ca/infrafabric/redis-semantic-tags.json`

### Existing StackCP Files (Do Not Touch)
- **redis-data.json** (464 KB) - Keep as-is
- **bridge-v1.1.backup.php** - Create before deployment

---

## Testing Checklist

- [ ] Info endpoint returns `"version": "2.0.0"`
- [ ] Info shows `"semantic_tags_available": true`
- [ ] Tags endpoint returns tagged keys
- [ ] Search endpoint finds relevant results
- [ ] Batch endpoint still works (backward compatibility)
- [ ] Health endpoint confirms both files exist
- [ ] Semantic search scores make sense
- [ ] Pattern matching still works correctly

---

## Expected Results

### Info Endpoint
```json
{
  "status": "neural_link_active",
  "version": "2.0.0",
  "backend": "file-based",
  "keys_count": 105,
  "semantic_tags_available": true,
  "tag_statistics": {
    "total_tagged_keys": 105,
    "unique_topics": 10,
    "unique_agents": 4
  }
}
```

### Tags Endpoint
Returns semantic metadata for all matching keys:
- Topics: architecture, cost, demo, deployment, documentation, logistics, partnership, redis, swarm, testing
- Agents: sonnet, haiku, gemini, guardian_council
- Content types: session_context, discovery, infrastructure, strategic, etc.
- Status: completed, active, archived, ready, pending
- Importance: high, medium, normal

### Search Endpoint
Ranks results by relevance:
- Exact key matches: +10 score
- Topic matches: +5 score
- Content type matches: +4 score
- Agent matches: +3 score
- Status matches: +2 score

---

## Gemini-3-Pro Integration

After deployment, Gemini can use semantic search:

**Before (manual lookup):**
```
User: What were the partnership decisions in Instance #12?
Gemini: Let me fetch instance:12:strategy:partnership...
```

**After (semantic search):**
```
User: What were the partnership decisions?
Gemini: [Automatically searches "partnership" → finds 23 relevant keys → synthesizes answer]
```

---

## Phase A Success Criteria

✅ **Deployment Complete When:**
1. bridge.php v2.0 deployed and responding
2. Semantic tags file accessible
3. All 5 test endpoints passing
4. Backward compatibility verified
5. Gemini-3-Pro can use search endpoint

📊 **Metrics to Track:**
- Search query response time (<200ms target)
- Result relevance accuracy (manual spot-check)
- Tag coverage (100% of 105 keys)
- Endpoint uptime (99.9% target)

---

## Next Steps (Phase B)

After Phase A deployment:
1. **Autopoll Reflex Arc** - Gemini auto-fetches context based on conversation topic
2. **Recursive Summarization** - Compress old instance contexts
3. **Vector Embeddings** - True semantic similarity (cosine distance)
4. **Real-time Sync** - Update tags as new keys are added

---

**Status:** Ready for deployment
**Blocker:** None
**Estimated Deployment Time:** 15 minutes
**Risk Level:** Low (rollback plan in place)
