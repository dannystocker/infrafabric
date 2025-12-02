# ChromaDB Migration - Implementation Checklist

**Mission:** Deploy A26's production-ready migration script to transfer 9,832 embeddings
**Timeline:** 2025-11-30 onwards
**Status:** Ready for Deployment

---

## Pre-Migration Setup

### Environment Preparation
- [ ] Verify Python 3.8+ installed
  ```bash
  python --version  # Should show 3.8 or higher
  ```

- [ ] Install required packages
  ```bash
  pip install chromadb>=0.4.0 tqdm>=4.65.0
  ```

- [ ] Verify network connectivity to source ChromaDB
  ```bash
  curl -X GET http://85.239.243.227:8000/api/v1/heartbeat
  ```

- [ ] Verify target ChromaDB accessible
  ```bash
  curl -X GET http://localhost:8000/api/v1/heartbeat
  ```

- [ ] Verify disk space available
  ```bash
  df -h /home/setup/infrafabric/
  # Need: ~200MB for exports + logs + checkpoints
  ```

### File Verification
- [ ] Migration script exists
  ```bash
  ls -lh /home/setup/infrafabric/tools/chromadb_migration.py
  # Should be 821 lines, ~30KB
  ```

- [ ] Test suite exists
  ```bash
  ls -lh /home/setup/infrafabric/tools/test_chromadb_migration.py
  # Should be 362 lines, ~12KB
  ```

- [ ] README documentation exists
  ```bash
  ls -lh /home/setup/infrafabric/tools/CHROMADB_MIGRATION_README.md
  ```

- [ ] Make script executable
  ```bash
  chmod +x /home/setup/infrafabric/tools/chromadb_migration.py
  ```

### Directory Structure
- [ ] Create checkpoint directory
  ```bash
  mkdir -p /home/setup/infrafabric/migration_checkpoints
  ```

- [ ] Create log directory
  ```bash
  mkdir -p /home/setup/infrafabric/migration_logs
  ```

- [ ] Create backup directory
  ```bash
  mkdir -p /home/setup/infrafabric/migration_backups
  ```

---

## Dry-Run Testing (Phase 1)

### Validation Without Writes
- [ ] Run dry-run with verbose logging
  ```bash
  python /home/setup/infrafabric/tools/chromadb_migration.py \
    --source-url http://85.239.243.227:8000 \
    --target-url http://localhost:8000 \
    --batch-size 100 \
    --dry-run \
    --verbose
  ```

- [ ] Verify Phase 1 (Export) successful
  - Check log: "Total chunks to migrate: 9,832"
  - Verify 4 collections exported (personality, rhetorical, humor, corpus)

- [ ] Verify Phase 2 (Transform) successful
  - Check: "Transformed X chunks" for each collection
  - No unexpected errors in logs

- [ ] Verify Phase 3 (Validate) successful
  - Check: "Validation passed (X% success rate)"
  - Allow 95%+ success (9,687/9,832 chunks)

- [ ] Verify Phase 4 (Import) shows dry-run behavior
  - Check: "[DRY-RUN] Would import X chunks"
  - No actual writes to target

- [ ] Review validation issues (if any)
  ```bash
  grep "Issues found:" /home/setup/infrafabric/migration_logs/migration_*.log
  # Expected: <5% failure rate is acceptable
  ```

- [ ] Document dry-run results
  ```
  - Total chunks: 9,832
  - Valid chunks: X (Y%)
  - Issues: [list any issues]
  - Recommendation: [PROCEED / INVESTIGATE]
  ```

---

## Unit Tests (Phase 2)

### Test Suite Execution
- [ ] Run full test suite
  ```bash
  python /home/setup/infrafabric/tools/test_chromadb_migration.py
  ```

- [ ] Verify all 17 tests pass
  - TestMetadataTransformer (5 tests)
  - TestDataValidator (4 tests)
  - TestMigrationConfig (2 tests)
  - TestMigrationCheckpoint (2 tests)
  - TestBatchProcessing (2 tests)
  - TestMetadataSchema (2 tests)

- [ ] Check test coverage
  ```bash
  python -m coverage run test_chromadb_migration.py
  python -m coverage report
  # Should show >80% coverage
  ```

---

## Pre-Production Checks (Phase 3)

### Source Data Integrity
- [ ] Verify source ChromaDB health
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='85.239.243.227', port=8000)
  for col in client.list_collections():
    print(f'{col.name}: {col.count()} documents')
  "
  ```

- [ ] Expected counts:
  - sergio_personality: ~2,350
  - sergio_rhetorical: ~1,890
  - sergio_humor: ~2,150
  - sergio_corpus: ~3,442
  - TOTAL: 9,832

- [ ] Sample embeddings check
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='85.239.243.227', port=8000)
  for col in client.list_collections():
    data = col.get(limit=1)
    if data['embeddings']:
      print(f'{col.name}: embedding dim = {len(data[\"embeddings\"][0])}')
  "
  ```

- [ ] Expected dimensions: 768, 1024, or 1536

### Target ChromaDB Preparation
- [ ] Verify target is empty or contains backup
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)
  cols = client.list_collections()
  print(f'Target collections: {len(cols)}')
  # Should be 0 or have backup copies with different names
  "
  ```

- [ ] Create manual backup if needed
  ```bash
  # Export existing target data
  python chromadb_migration.py \
    --source-url http://localhost:8000 \
    --target-url /home/setup/infrafabric/migration_backups/target_backup.json \
    --dry-run
  ```

### Network & Firewall
- [ ] Test connectivity both directions
  ```bash
  # Source to local
  curl -X GET http://85.239.243.227:8000/api/v1/collections

  # Target is accessible
  curl -X GET http://localhost:8000/api/v1/collections
  ```

- [ ] Verify firewall rules allow ChromaDB traffic
  - Port 8000 accessible from migration host

---

## Production Migration (Phase 4)

### Migration Execution
- [ ] Schedule maintenance window (5-10 minute downtime tolerance)

- [ ] Start migration with monitoring
  ```bash
  python /home/setup/infrafabric/tools/chromadb_migration.py \
    --source-url http://85.239.243.227:8000 \
    --target-url http://localhost:8000 \
    --batch-size 500 \
    --verbose \
    2>&1 | tee /home/setup/infrafabric/migration_logs/production_run.log
  ```

- [ ] Monitor in real-time
  ```bash
  # In separate terminal
  watch -n 5 'tail -30 /home/setup/infrafabric/migration_logs/migration_*.log'
  ```

- [ ] Set up alerts
  - Monitor log file for errors
  - Watch CPU/memory usage
  - Check network traffic

### Migration Checkpoints
- [ ] Phase 1 (Export) complete
  - Check log: "✓ Phase 1 Complete: X chunks saved"
  - Verify exported_data size (~50-100MB)

- [ ] Phase 2 (Transform) complete
  - Check log: "✓ Phase 2 Complete: X chunks classified"
  - All 4 collections populated

- [ ] Phase 3 (Validate) complete
  - Check log: "Validation passed (X% success rate)"
  - Success rate ≥95%

- [ ] Phase 4 (Import) complete
  - Check log: "Loaded X chunks into Y collections"
  - Monitor batch progress (batch 1/99, 2/99, etc.)

- [ ] Phase 5 (Verify) complete
  - Check log: "Migration passed all verifications"
  - Collection counts match

### Error Handling During Migration
- [ ] If migration fails midway
  ```bash
  # Check checkpoint to see where it stopped
  ls -lh /home/setup/infrafabric/migration_checkpoints/ | tail -1
  cat /home/setup/infrafabric/migration_checkpoints/checkpoint_*.json

  # Analyze error in log
  tail -50 /home/setup/infrafabric/migration_logs/migration_*.log
  ```

- [ ] If connectivity lost
  - Restart migration (will use last checkpoint)
  - Verify no duplicate data in target
  - Re-run verification phase

- [ ] If validation fails (>5% error rate)
  ```bash
  # Investigate failed chunks
  grep "missing_" /home/setup/infrafabric/migration_logs/migration_*.log
  grep "invalid_" /home/setup/infrafabric/migration_logs/migration_*.log

  # Decide: retry with custom metadata handling or proceed with partial data
  ```

---

## Post-Migration Verification (Phase 5)

### Data Integrity Checks
- [ ] Verify all collections exist
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)
  for col in client.list_collections():
    print(f'✓ {col.name}: {col.count()} documents')
  "
  ```

- [ ] Verify chunk counts match
  ```
  Expected:
    sergio_personality: 2,350
    sergio_rhetorical: 1,890
    sergio_humor: 2,150
    sergio_corpus: 3,442
    TOTAL: 9,832

  Actual: [check from output above]

  Tolerance: ±1% acceptable (up to 9,915 max)
  ```

- [ ] Verify 12-field metadata schema
  ```bash
  python -c "
  import chromadb, json
  client = chromadb.HttpClient(host='localhost', port=8000)
  col = client.get_collection('sergio_personality')
  data = col.get(limit=1)
  if data['metadatas']:
    print(json.dumps(data['metadatas'][0], indent=2))
  "
  ```

  Check for required fields:
  - source ✓
  - source_file ✓
  - source_line ✓
  - author ✓
  - collection_type ✓
  - category ✓
  - language ✓
  - authenticity_score ✓
  - confidence_level ✓
  - disputed ✓
  - if_citation_uri ✓

- [ ] Verify embeddings intact
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)

  for col_name in ['sergio_personality', 'sergio_rhetorical', 'sergio_humor', 'sergio_corpus']:
    col = client.get_collection(col_name)
    data = col.get(limit=3)

    for i, emb in enumerate(data['embeddings'][:3]):
      dim = len(emb)
      has_nan = any(str(v) == 'nan' for v in emb)
      print(f'{col_name}: embedding {i}: dim={dim}, nan={has_nan}')
  "
  ```

  Expected: All embeddings 768-1536 dim, no NaN values

### Query Validation (Sample Queries)
- [ ] Test personality query
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)
  col = client.get_collection('sergio_personality')

  # Query by metadata
  results = col.query(
    query_texts=['conscientiousness values'],
    n_results=3,
    where={'authenticity_score': {'\$gte': 0.85}}
  )

  print(f'Found {len(results[\"documents\"][0])} results')
  assert len(results['documents'][0]) > 0, 'Query returned no results'
  print('✓ Personality query works')
  "
  ```

- [ ] Test rhetorical query
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)
  col = client.get_collection('sergio_rhetorical')

  results = col.query(
    query_texts=['metaphor systems thinking'],
    n_results=3
  )

  assert len(results['documents'][0]) > 0, 'Query returned no results'
  print('✓ Rhetorical query works')
  "
  ```

- [ ] Test humor query
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)
  col = client.get_collection('sergio_humor')

  results = col.query(
    query_texts=['self deprecating funny'],
    n_results=3,
    where={'language': {'\$in': ['en', 'es_en']}}
  )

  assert len(results['documents'][0]) > 0, 'Query returned no results'
  print('✓ Humor query works')
  "
  ```

- [ ] Test corpus query
  ```bash
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)
  col = client.get_collection('sergio_corpus')

  results = col.query(
    query_texts=['identity relational narrative'],
    n_results=3,
    where={'document_type': 'narrative'}
  )

  assert len(results['documents'][0]) > 0, 'Query returned no results'
  print('✓ Corpus query works')
  "
  ```

### Performance Benchmarks
- [ ] Measure query latency
  ```bash
  python -c "
  import chromadb
  import time

  client = chromadb.HttpClient(host='localhost', port=8000)
  col = client.get_collection('sergio_personality')

  start = time.time()
  for i in range(10):
    col.query(query_texts=['test'], n_results=5)
  elapsed = time.time() - start

  avg_latency = (elapsed / 10) * 1000
  print(f'Average query latency: {avg_latency:.1f}ms')
  assert avg_latency < 300, f'Latency too high: {avg_latency}ms'
  "
  ```

- [ ] Check collection sizes
  ```bash
  du -sh /home/setup/infrafabric/sergio_chatbot/chromadb/
  # Should be ~200-300MB
  ```

### Backup & Recovery
- [ ] Archive migration logs
  ```bash
  tar -czf /home/setup/infrafabric/migration_backups/migration_logs_$(date +%Y%m%d).tar.gz \
    /home/setup/infrafabric/migration_logs/
  ```

- [ ] Save final checkpoint
  ```bash
  cp /home/setup/infrafabric/migration_checkpoints/checkpoint_*.json \
    /home/setup/infrafabric/migration_backups/final_checkpoint.json
  ```

- [ ] Document migration results
  ```markdown
  # Migration Results - 2025-11-30

  ## Summary
  - Start time: [HH:MM]
  - End time: [HH:MM]
  - Duration: [X minutes]
  - Status: SUCCESS ✓

  ## Chunk Counts
  - sergio_personality: 2,350 (source: 2,350, target: 2,350) ✓
  - sergio_rhetorical: 1,890 (source: 1,890, target: 1,890) ✓
  - sergio_humor: 2,150 (source: 2,150, target: 2,150) ✓
  - sergio_corpus: 3,442 (source: 3,442, target: 3,442) ✓
  - TOTAL: 9,832 ✓

  ## Performance
  - Throughput: X chunks/sec
  - Memory peak: XMB
  - Network: Good

  ## Issues
  - [List any issues encountered and how resolved]

  ## Sign-off
  - Migrator: [Name]
  - Date: [Date]
  - Verified by: [Name]
  ```

---

## Rollback Plan (If Needed)

### Immediate Rollback
- [ ] If target ChromaDB has issues
  ```bash
  # Redirect traffic back to old ChromaDB
  # Update application configuration to point to old source
  ```

- [ ] Clear corrupted target
  ```bash
  # Delete target collections
  python -c "
  import chromadb
  client = chromadb.HttpClient(host='localhost', port=8000)
  for col in client.list_collections():
    client.delete_collection(col.name)
  "
  ```

- [ ] Restore from backup (if created before migration)
  ```bash
  # Restore pre-migration snapshot
  python chromadb_migration.py \
    --source-url /home/setup/infrafabric/migration_backups/target_backup.json \
    --target-url http://localhost:8000
  ```

### Lessons Learned
- [ ] Document any issues encountered
- [ ] Update README with resolutions
- [ ] Update checklist with new steps if needed

---

## Post-Deployment (Phase 6)

### Notify Stakeholders
- [ ] Send migration completion notification
  - Status: SUCCESS ✓
  - Details: 9,832 chunks migrated
  - Queries: Fully functional
  - Performance: Verified <300ms latency

- [ ] Update documentation
  - ChromaDB collections deployed
  - OpenWebUI integration ready (next step)

### Monitor Production
- [ ] Monitor for next 24 hours
  - Check error logs
  - Monitor query performance
  - Watch memory/CPU usage

- [ ] Set up continuous monitoring
  ```bash
  # Daily backup
  0 2 * * * /home/setup/infrafabric/tools/backup_chromadb.sh

  # Weekly health check
  0 3 * * 0 /home/setup/infrafabric/tools/verify_chromadb.sh
  ```

### Documentation Updates
- [ ] Update IF.citation references
  - Add to `/home/setup/infrafabric/COMPONENT-INDEX.md`
  - Link from NaviDocs session summary

- [ ] Create deployment record
  - Location: `/home/setup/infrafabric/deployment_records/`
  - Include: dates, versions, status, rollback procedure

---

## Success Criteria Checklist

**Must-Have (All Required):**
- [ ] All 9,832 chunks imported
- [ ] 4 collections created with correct names
- [ ] 12-field metadata schema present
- [ ] All embeddings valid (no NaN, correct dimensions)
- [ ] Query latency <300ms
- [ ] 95%+ validation success rate

**Should-Have (Strongly Recommended):**
- [ ] <5 minutes total migration time
- [ ] <500MB peak memory usage
- [ ] All 5 test queries pass
- [ ] Migration logs archived
- [ ] Checkpoint system functional

**Nice-to-Have (Optional):**
- [ ] <2000 chunks/sec throughput
- [ ] <100ms query latency
- [ ] Zero failed batches
- [ ] Redis caching configured

---

## Final Sign-Off

**Prepared By:** A26 (ChromaDB Migration Agent)
**Date:** 2025-11-30
**Status:** Ready for Deployment
**Next Phase:** Deploy to production and configure OpenWebUI integration

**Approval:**
- [ ] Prepared: A26 _____ Date _____
- [ ] Reviewed: [Agent/Person] _____ Date _____
- [ ] Approved: [Lead] _____ Date _____
- [ ] Executed: [Operator] _____ Date _____
- [ ] Verified: [QA] _____ Date _____

---

**References:**
- Migration Script: `/home/setup/infrafabric/tools/chromadb_migration.py`
- Documentation: `/home/setup/infrafabric/tools/CHROMADB_MIGRATION_README.md`
- Schema Design: `/home/setup/infrafabric/integration/chromadb_sergio_collections_design.md`
- Implementation: `/home/setup/infrafabric/integration/sergio_chromadb_implementation.py`
