# Gemini-3-Pro Integration Test Plan
## Memory Exoskeleton Phase A - Semantic Search

**Date:** 2025-11-23
**Instance:** #19 Phase A
**Status:** Ready for testing (post-deployment)

---

## Test Overview

This document outlines how to test Gemini-3-Pro integration with the Memory Exoskeleton's new semantic search capabilities.

### Prerequisites
- ✅ Bridge v2.0 deployed to StackCP
- ✅ Semantic tags file uploaded (redis-semantic-tags.json)
- ✅ Both endpoints responding (verified with curl)
- ✅ Gemini CLI installed (gemini v0.11.3+)

---

## Test 1: Basic Context Injection

**Objective:** Verify Gemini can fetch and summarize Redis context

### Test Command
```bash
gemini "Fetch https://digital-lab.ca/infrafabric/bridge.php?action=batch&pattern=instance:12:* with Bearer token 50040d7fbfaa712fccfc5528885ebb9b and summarize what Instance #12 accomplished"
```

### Expected Response
Gemini should:
1. Authenticate with Bearer token
2. Fetch all instance:12:* keys
3. Parse JSON response
4. Summarize key accomplishments:
   - Georges-Antoine Gary partnership research
   - Demo system (Guardian Council)
   - Test #1B validation (60.5 min saved)
   - 23 files created (~18,700 lines)

### Success Criteria
- ✅ Gemini successfully authenticates
- ✅ Fetches all Instance #12 keys (should be 6-8 keys)
- ✅ Provides accurate summary
- ✅ References specific achievements
- ✅ No authentication errors

---

## Test 2: Semantic Search - Topic Discovery

**Objective:** Use semantic search to find partnership-related work

### Test Command
```bash
gemini "Use semantic search at https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership with Bearer token 50040d7fbfaa712fccfc5528885ebb9b to find all partnership-related decisions and strategies"
```

### Expected Response
Gemini should:
1. Call the search endpoint with query="partnership"
2. Receive ranked results (23 keys expected)
3. Identify top results:
   - `instance:12:strategy:partnership` (score: 15)
   - `instance:12:context:file:SESSION-HANDOVER.md:latest`
   - Partnership-related findings
4. Synthesize partnership strategy from results

### Success Criteria
- ✅ Search returns 20+ results
- ✅ Top result is `instance:12:strategy:partnership`
- ✅ Gemini synthesizes coherent strategy
- ✅ Mentions Georges-Antoine Gary
- ✅ References revenue model (€60K-€100K per project)

---

## Test 3: Semantic Search - Agent Work Discovery

**Objective:** Find all work done by Haiku workers

### Test Command
```bash
gemini "Search for all Haiku worker output at https://digital-lab.ca/infrafabric/bridge.php?action=search&query=haiku with Bearer 50040d7fbfaa712fccfc5528885ebb9b and categorize by task type"
```

### Expected Response
Gemini should:
1. Search for "haiku" across all keys
2. Find Haiku-related keys (5+ expected)
3. Categorize by task type:
   - Investigations (redis, blockers)
   - Documentation updates
   - Worker findings
4. Provide task distribution summary

### Success Criteria
- ✅ Finds 5+ Haiku-related keys
- ✅ Correctly identifies task types
- ✅ Shows semantic tags (agents: ["haiku"])
- ✅ Provides useful categorization

---

## Test 4: Semantic Tags Inspection

**Objective:** Explore semantic tag structure

### Test Command
```bash
gemini "Fetch semantic tags for all findings using https://digital-lab.ca/infrafabric/bridge.php?action=tags&pattern=finding:* with Bearer 50040d7fbfaa712fccfc5528885ebb9b and analyze the topic distribution"
```

### Expected Response
Gemini should:
1. Fetch tags for all finding:* keys (7 expected)
2. Parse tag structure:
   - topics: ["swarm", "cost", "architecture", "redis"]
   - agents: ["haiku", "sonnet", "gemini"]
   - content_type: "discovery"
   - status: varies
3. Provide topic distribution analysis

### Success Criteria
- ✅ Fetches 7 finding tags
- ✅ Identifies common topics (swarm, architecture, cost)
- ✅ Shows agent attribution
- ✅ Correctly interprets semantic metadata

---

## Test 5: Multi-Instance Timeline Reconstruction

**Objective:** Use semantic search to reconstruct project timeline

### Test Command
```bash
gemini "Search for deployment-related work at https://digital-lab.ca/infrafabric/bridge.php?action=search&query=deployment with Bearer 50040d7fbfaa712fccfc5528885ebb9b and create a chronological timeline across all instances"
```

### Expected Response
Gemini should:
1. Search for "deployment"
2. Find 20+ deployment-related keys
3. Group by instance number:
   - Instance #11: MEDIUM series deployment
   - Instance #12: Partnership deployment ready
   - Instance #13: Context investigation
4. Create chronological narrative

### Success Criteria
- ✅ Finds deployment work across multiple instances
- ✅ Correctly orders chronologically
- ✅ Identifies instance-specific accomplishments
- ✅ Builds coherent timeline narrative

---

## Test 6: Status-Based Filtering

**Objective:** Find all completed vs pending work

### Test Command
```bash
gemini "Search for completed work using https://digital-lab.ca/infrafabric/bridge.php?action=search&query=completed with Bearer 50040d7fbfaa712fccfc5528885ebb9b and compare with a search for pending work"
```

### Expected Response
Gemini should:
1. Search "completed" → find 5+ keys
2. Search "pending" → find different set
3. Compare status distribution
4. Provide completion rate estimate

### Success Criteria
- ✅ Distinguishes completed from pending
- ✅ Correctly interprets status tags
- ✅ Provides meaningful comparison
- ✅ Estimates project completion percentage

---

## Test 7: Context-Aware Conversation

**Objective:** Gemini auto-injects context based on conversation topic

### Test Command
```bash
gemini "What were the cost savings from the partnership strategy?"
```

**NOTE:** This requires Gemini to have autopoll enabled or manual context injection prompt configured.

### Expected Behavior
Gemini should:
1. Recognize "partnership" and "cost savings" keywords
2. Automatically search: `action=search&query=partnership cost`
3. Find relevant keys (instance:12:strategy:partnership)
4. Extract cost data: €280K savings, €100K-€300K revenue
5. Provide accurate answer without explicit fetch instruction

### Success Criteria
- ✅ Gemini auto-fetches relevant context
- ✅ Finds partnership strategy key
- ✅ Extracts accurate cost numbers
- ✅ Provides confident answer (not "I don't have information")
- ✅ No manual fetch instruction needed

---

## Test 8: Performance Benchmark

**Objective:** Measure semantic search response time

### Test Command
```bash
time gemini "Quick test: search for redis at https://digital-lab.ca/infrafabric/bridge.php?action=search&query=redis with Bearer 50040d7fbfaa712fccfc5528885ebb9b and return count only"
```

### Expected Response
Response time: <2 seconds total
- Bridge.php processing: <200ms
- Gemini processing: <1.5s
- Network latency: <500ms

### Success Criteria
- ✅ Total time < 2 seconds
- ✅ Bridge responds < 200ms
- ✅ Results accurate despite speed
- ✅ No timeout errors

---

## Test 9: Error Handling

**Objective:** Verify graceful error handling

### Test 9a: Invalid Bearer Token
```bash
gemini "Test with wrong token: https://digital-lab.ca/infrafabric/bridge.php?action=info with Bearer WRONGTOKEN"
```

Expected: Gemini reports authentication error, suggests checking credentials

### Test 9b: Invalid Action
```bash
gemini "Test invalid action: https://digital-lab.ca/infrafabric/bridge.php?action=invalid with Bearer 50040d7fbfaa712fccfc5528885ebb9b"
```

Expected: Gemini reports "Invalid action" error, lists valid actions

### Test 9c: Malformed Query
```bash
gemini "Search with empty query: https://digital-lab.ca/infrafabric/bridge.php?action=search&query= with Bearer 50040d7fbfaa712fccfc5528885ebb9b"
```

Expected: Gemini reports "Query parameter required" error

### Success Criteria
- ✅ All errors handled gracefully
- ✅ Helpful error messages
- ✅ No crashes or hangs
- ✅ Suggests corrective actions

---

## Test 10: Comparative Search Quality

**Objective:** Compare semantic search vs full-text search

### Test Command
```bash
# Semantic search (default)
gemini "Search 'partnership' with https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership&semantic=true with Bearer 50040d7fbfaa712fccfc5528885ebb9b"

# Full-text search (fallback)
gemini "Search 'partnership' with https://digital-lab.ca/infrafabric/bridge.php?action=search&query=partnership&semantic=false with Bearer 50040d7fbfaa712fccfc5528885ebb9b"
```

### Expected Comparison
| Metric | Semantic | Full-Text |
|--------|----------|-----------|
| Results | 23 | ~15-20 |
| Top result relevance | Higher | Lower |
| Precision | Better | Acceptable |
| Recall | Better | Lower |

### Success Criteria
- ✅ Semantic search finds more relevant results
- ✅ Semantic search ranks better
- ✅ Full-text search works as fallback
- ✅ Both methods return valid JSON

---

## Validation Checklist

After running all tests:

### Functional Requirements
- [ ] All 6 bridge.php endpoints responding
- [ ] Semantic tags loaded correctly
- [ ] Search returns ranked results
- [ ] Tags endpoint provides metadata
- [ ] Batch endpoint backward-compatible
- [ ] Info shows v2.0.0 and semantic_tags_available: true

### Performance Requirements
- [ ] Search responses < 200ms
- [ ] Gemini total time < 2 seconds
- [ ] No timeout errors
- [ ] 99%+ uptime during test period

### Quality Requirements
- [ ] Search precision: 70%+ (spot-check)
- [ ] Coverage: 75%+ keys discoverable
- [ ] Error handling: Graceful degradation
- [ ] Documentation: Complete and accurate

### Integration Requirements
- [ ] Gemini can authenticate
- [ ] Gemini can parse responses
- [ ] Gemini can synthesize answers
- [ ] Gemini auto-injection possible (Test 7)

---

## Phase A Success Declaration

**Phase A is COMPLETE when:**

✅ All 10 tests pass
✅ Validation checklist 100% complete
✅ No P0 blockers
✅ Performance targets met
✅ Documentation handover ready

**Estimated Testing Time:** 60-90 minutes
**Risk Level:** Low
**Blocker Probability:** <10%

---

## Troubleshooting

### Issue: Gemini can't authenticate
**Solution:** Verify Bearer token in command, check bridge.php auth logic

### Issue: Search returns no results
**Solution:** Check redis-semantic-tags.json uploaded correctly, verify file permissions

### Issue: Tags show as unavailable
**Solution:** Confirm TAGS_FILE path in bridge.php matches uploaded filename

### Issue: Slow response times
**Solution:** Check StackCP server load, verify JSON files not corrupted

---

## Next Steps (Phase B)

After successful testing:
1. **Autopoll Reflex Arc:** Configure Gemini to auto-inject context based on conversation keywords
2. **Recursive Summarization:** Compress old instance contexts to save tokens
3. **Vector Embeddings:** Implement true semantic similarity with cosine distance
4. **Real-time Sync:** Auto-update semantic tags when new keys added

---

**Status:** Ready for testing (post-deployment)
**Dependencies:** Bridge v2.0 deployed, semantic tags uploaded
**Estimated Completion:** 2025-11-23 (same day as deployment)
