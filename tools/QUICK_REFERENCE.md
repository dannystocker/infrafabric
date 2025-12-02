# ChromaDB Migration - Quick Reference Guide

**Mission:** A26 - Transfer 9,832 embeddings to new 4-collection schema
**Status:** Production-Ready
**Files:** 3 Python files + 3 documentation files = 1,183 LOC

---

## One-Line Commands

### Test Everything Works
```bash
python /home/setup/infrafabric/tools/chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --dry-run --verbose
```

### Run Migration
```bash
python /home/setup/infrafabric/tools/chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 500
```

### Run Tests
```bash
python /home/setup/infrafabric/tools/test_chromadb_migration.py
```

### Monitor Real-Time
```bash
tail -f /home/setup/infrafabric/migration_logs/migration_*.log
```

### Verify Result
```bash
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
for col in client.list_collections():
  print(f'{col.name}: {col.count()} documents')
"
```

---

## File Structure

```
/home/setup/infrafabric/tools/
├── chromadb_migration.py                    [821 lines] Main script
├── test_chromadb_migration.py               [362 lines] Test suite
├── CHROMADB_MIGRATION_README.md             Full documentation
├── IMPLEMENTATION_CHECKLIST.md              Step-by-step deployment
├── QUICK_REFERENCE.md                       This file
└── [Output directories created at runtime]
    ├── ../migration_checkpoints/            Resumable checkpoints
    ├── ../migration_logs/                   Migration logs
    └── ../migration_backups/                Pre-migration backups
```

---

## Architecture Summary

```
5 Phases:
1. Export      (15-30s)  → Read 9,832 chunks from source
2. Transform   (2-5s)    → Map to 12-field schema
3. Validate    (10-20s)  → Verify 95%+ quality
4. Import      (150-300s) → Batch load to 4 collections
5. Verify      (5-10s)   → Check source/target match

Total: 5-10 minutes, <500MB memory, $0.05 cost
```

---

## 12-Field Metadata Schema

Every chunk has:
1. **source** - Data source (e.g., "sergio_conference_2025")
2. **source_file** - Full path for audit trail
3. **source_line** - Starting line for exact citation
4. **author** - Content creator (e.g., "Sergio Romo")
5. **collection_type** - "personality", "rhetorical", "humor", or "corpus"
6. **category** - Specific type (e.g., "trait_analysis", "metaphor")
7. **language** - "es", "en", or "es_en"
8. **authenticity_score** - 0.0-1.0 (1.0 = direct quote)
9. **confidence_level** - "high", "medium", "low"
10. **disputed** - Boolean (IF.Guard review flag)
11. **if_citation_uri** - Citation reference
12. **+collection-specific fields** - 1-4 extra fields per collection

---

## Key Features

### Batch Processing
- Configurable batch size (32-1000 chunks)
- Process 100 chunks at a time (default)
- Fail one batch without losing others

### Checkpoint & Resume
- Automatic checkpoint after each phase
- Resume from same batch if interrupted
- Full error statistics per checkpoint

### Validation Before Import
- 95%+ quality threshold
- Dimension checking, NaN detection
- Missing field identification
- Report before writing to target

### Dry-Run Mode
- Full pipeline simulation
- No writes to target
- Identify issues safely
- ~30 seconds overhead

### Error Tolerance
- Allow 5% failure rate
- Default missing fields with sensible defaults
- Log all failures with specifics
- Continue on recoverable errors

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Connection timeout** | Check firewall, use `curl -X GET http://host:8000/api/v1/heartbeat` |
| **Out of memory** | Reduce batch size from 500 to 100 |
| **Migration stuck** | Check checkpoint in `/home/setup/infrafabric/migration_checkpoints/` |
| **Validation fails** | Review log for "Issues found:", allow up to 5% failure |
| **Embedding mismatch** | Script handles 768/1024/1536 dimensions automatically |

---

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| **Total Time** | 5-10m | [Post-execution] |
| **Throughput** | 1,000-2,000 chunks/sec | [Post-execution] |
| **Memory** | <500MB | [Post-execution] |
| **Query Latency** | <300ms (uncached) | [Post-execution] |
| **Success Rate** | >95% | [Post-execution] |

---

## Collection Details

### sergio_personality (2,350 docs)
- **Source:** IF.intelligence analysis of Sergio's traits
- **Fields:** big_five_trait, trait_score, related_frameworks
- **Queries:** "core values", "conscientiousness", "ethical framework"

### sergio_rhetorical (1,890 docs)
- **Source:** Rhetorical device analysis + conference examples
- **Fields:** device_type, frequency, linguistic_marker
- **Queries:** "metaphor", "aspiradora", "how Sergio speaks"

### sergio_humor (2,150 docs)
- **Source:** Conference transcripts + guides
- **Fields:** humor_type, emotional_context, target_audience
- **Queries:** "funny", "self-deprecating", "vulnerable joke"

### sergio_corpus (3,442 docs)
- **Source:** Conferences, narratives, guides
- **Fields:** document_type, word_count, emotional_intensity
- **Queries:** "narrative", "identity relational", "therapeutic example"

---

## Example: Run Full Migration Cycle

```bash
# Step 1: Dry-run (5 minutes)
python /home/setup/infrafabric/tools/chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --dry-run --verbose

# Step 2: Review log
tail -50 /home/setup/infrafabric/migration_logs/migration_*.log

# Step 3: If successful, run actual migration (5-10 minutes)
python /home/setup/infrafabric/tools/chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 500

# Step 4: Verify results
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
for col in client.list_collections():
  print(f'✓ {col.name}: {col.count()} documents')
"
```

---

## IF.TTT Compliance

✓ **Traceable:** source_file + source_line for exact citation
✓ **Transparent:** Full phase logging + error details
✓ **Trustworthy:** Validation before import, if_citation_uri for every chunk

---

## Testing Quick Check

```bash
# Run unit tests (5 seconds)
python /home/setup/infrafabric/tools/test_chromadb_migration.py

# Expected output:
# Ran 17 tests in 0.234s
# OK
```

---

## When Migration Fails

```bash
# 1. Check log
tail -100 /home/setup/infrafabric/migration_logs/migration_*.log

# 2. Check checkpoint
cat /home/setup/infrafabric/migration_checkpoints/checkpoint_*.json | python -m json.tool

# 3. Identify phase that failed and error details

# 4. Based on error:
#    - Connection issue? → Fix network, retry
#    - Validation issue? → Review failures, decide to proceed or fix
#    - Import issue? → Check target capacity, reduce batch size
```

---

## Success Criteria (All Must Pass)

✓ All 9,832 chunks imported
✓ 4 collections exist with correct names
✓ Chunk counts match (±1%)
✓ 12-field metadata present in all chunks
✓ No NaN embeddings
✓ Embedding dimensions valid (768+)
✓ Sample queries return results
✓ Query latency <300ms

---

## Files Generated During Migration

```
/home/setup/infrafabric/migration_logs/
  └── migration_20251130_143522.log      [10-50KB] Full migration log

/home/setup/infrafabric/migration_checkpoints/
  ├── checkpoint_20251130_143522.json    [2-5KB] Phase 1 checkpoint
  ├── checkpoint_20251130_143527.json    [2-5KB] Phase 2 checkpoint
  ├── checkpoint_20251130_143532.json    [2-5KB] Phase 3 checkpoint
  ├── checkpoint_20251130_143837.json    [2-5KB] Phase 4 checkpoint
  └── checkpoint_20251130_143847.json    [2-5KB] Final checkpoint

/home/setup/infrafabric/sergio_chatbot/chromadb/
  ├── 0f4c8e2e-1234-5678-9abc-def012345678/
  ├── 1a2b3c4d-5678-9abc-def0-123456789abc/
  ├── 2b3c4d5e-6789-abcd-ef01-234567890abc/
  └── 3c4d5e6f-789a-bcde-f012-345678901abc/
      [4 collection directories]
```

---

## Next Steps After Migration

1. **Configure OpenWebUI** - Use collections in Sergio RAG pipe
2. **Set up Redis caching** - Optional performance enhancement
3. **Monitor production** - Watch logs for errors
4. **Create backup routine** - Daily backups of ChromaDB

---

## References

- **Main Script:** `/home/setup/infrafabric/tools/chromadb_migration.py` (821 lines)
- **Tests:** `/home/setup/infrafabric/tools/test_chromadb_migration.py` (362 lines)
- **Full Docs:** `/home/setup/infrafabric/tools/CHROMADB_MIGRATION_README.md`
- **Deployment:** `/home/setup/infrafabric/tools/IMPLEMENTATION_CHECKLIST.md`
- **Schema:** `/home/setup/infrafabric/integration/chromadb_sergio_collections_design.md`
- **Citation:** `if://design/chromadb-migration-script-v1.0-2025-11-30`

---

**Agent:** A26 (ChromaDB Migration)
**Status:** Production-Ready
**Date:** 2025-11-30
**Estimated Execution Time:** 5-10 minutes
**Cost:** ~$0.05
