# ChromaDB Migration Integration Guide - A26 + A27 + A28

## Mission Overview

End-to-end ChromaDB migration with validation and rollback capability:

- **A26:** Migrate data from old to new ChromaDB (9,832 chunks)
- **A27:** Validate migration integrity (8 tests)
- **A28:** Rollback if validation fails (if needed)

## Timeline

```
[A26 Migration] → [A27 Validation] → [Decision] → [Cutover / Rollback]
  (30-45 min)      (25-35 min)      (instant)    (5-10 min)
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  OLD CHROMADB (Production)                   │
│  - 9,832 chunks across 4 collections                         │
│  - Old metadata schema                                       │
│  - Active queries during migration                           │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ A26: Export & Transform
               ↓
        [TRANSFORMATION]
        - Export chunks
        - Apply new 12-field schema
        - Map to new collections
        - Batch import to target
        │
        ├─→ Checkpoint: progress saved
        ├─→ Dry-run mode available
        └─→ Resume on failure
               │
               ↓
┌─────────────────────────────────────────────────────────────┐
│              NEW CHROMADB (Target)                           │
│  - 4 collections: personality, rhetorical, humor, corpus    │
│  - 12-field metadata schema                                  │
│  - Ready for validation                                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ A27: Comprehensive Validation
               ↓
        [8 VALIDATION TESTS]
        1. Count Verification
        2. Embedding Integrity
        3. Metadata Completeness
        4. Semantic Search Equivalence
        5. Collection Distribution
        6. Duplicate Detection
        7. Field Type Validation
        8. Citation References
               │
        ┌──────┴──────┐
        │ All pass?   │
        └──────┬──────┘
             ╱ ╲
          Yes  No
           │    │
           │    └─→ [A28 ROLLBACK]
           │        - Restore old DB
           │        - Archive failed migration
           │        - Generate rollback report
           │        - Ready for retry
           │
           └──→ [CUTOVER]
                - Update production pointer
                - Smoke tests
                - Monitor performance
                - Archive old DB (30-day backup)
```

## Step-by-Step Workflow

### Phase 0: Pre-Migration (Before A26)

```bash
# 1. Verify source database
$ python chromadb_migration.py --source-url http://old:8000 --dry-run

# 2. Create backup
$ tar czf chromadb_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/chromadb

# 3. Prepare target database
$ mkdir -p /path/to/new/chromadb

# 4. Get validator ready
$ cp chromadb_migration_validator.py ready_dir/
$ cp sample_test_queries.json ready_dir/
```

### Phase 1: A26 Migration

```bash
# Execute migration
$ python chromadb_migration.py \
    --source-url http://85.239.243.227:8000 \
    --target-url http://localhost:8000 \
    --batch-size 100 \
    --verbose

# Output: migration_*.log in /home/setup/infrafabric/migration_logs/

# On success:
# - All 9,832 chunks transferred
# - New schema applied
# - Metadata transformed
# - Collections created: sergio_personality, sergio_rhetorical, etc.
```

**Migration Checkpoint Files:**
```
/home/setup/infrafabric/migration_checkpoints/
├── checkpoint_20251130_100000.json  (phase: initialization)
├── checkpoint_20251130_101500.json  (phase: export)
├── checkpoint_20251130_102500.json  (phase: transform)
├── checkpoint_20251130_103500.json  (phase: validate)
├── checkpoint_20251130_105000.json  (phase: import)
├── checkpoint_20251130_110000.json  (phase: verify)
└── checkpoint_20251130_111000.json  (phase: complete)
```

Resume if interrupted:
```bash
$ python chromadb_migration.py \
    --source-url http://old:8000 \
    --target-url http://localhost:8000 \
    --checkpoint-file checkpoint_20251130_105000.json
```

### Phase 2: A27 Validation

```bash
# Run complete validation
$ python chromadb_migration_validator.py \
    --old-db-url http://85.239.243.227:8000 \
    --new-db-url http://localhost:8000 \
    --test-queries sample_test_queries.json \
    --output validation_report.md \
    --verbose

# Output files:
# - validation_report.md (human-readable)
# - validation_report.json (machine-readable)
# - validation_*.log in /home/setup/infrafabric/validation_logs/
```

**Validation Output Example:**
```
================================================================================
VALIDATION SUMMARY
================================================================================
Total tests: 8
Passed: 8
Failed: 0
Elapsed time: 32.45s
Overall status: PASSED
Rollback triggered: NO
================================================================================
```

### Phase 2b: Interpretation

**Interpretation Table:**

| Status | Rollback | Action | Next Steps |
|--------|----------|--------|-----------|
| PASSED | NO | ✓ Safe to cutover | → Phase 3 (Cutover) |
| WARNING | NO | ⚠ Review warnings | Review & decide |
| FAILED | YES | ✗ Automatic rollback | → A28 Rollback |

**Check Report:**
```bash
# Read markdown report
$ cat validation_report.md

# Check JSON for programmatic access
$ python -m json.tool validation_report.json | head -50

# Key fields to check:
# - overall_status: PASSED / WARNING / FAILED
# - rollback_triggered: true / false
# - rollback_reason: (if triggered)
# - data_loss_percentage: should be 0.0
# - semantic_divergence_percentage: should be <20%
```

### Phase 3: Cutover (If Validation Passes)

```bash
# 1. Update application pointer (example)
# Change connection string from:
#   http://85.239.243.227:8000
# To:
#   http://localhost:8000

# 2. Run smoke tests
$ python test_semantic_search.py --db-url http://localhost:8000

# 3. Monitor performance
$ watch -n 5 'tail -20 /var/log/chromadb/queries.log'

# 4. Archive old database (keep 30 days backup)
$ mkdir -p /archive/chromadb
$ tar czf /archive/chromadb/old_chromadb_$(date +%Y%m%d).tar.gz \
    /path/to/old/chromadb
$ echo "Archived: $(date)" >> /archive/chromadb/ARCHIVE.log

# 5. Document completion
$ echo "Migration completed successfully on $(date)" >> MIGRATION.log
```

### Phase 4: Post-Migration Verification (24 hours)

```bash
# Monitor for 24 hours:
# - Query response times
# - Embedding accuracy
# - Error rates
# - No data corruption reported

# After 24 hours, if no issues:
# - Delete backup from immediate access
# - Keep 30-day archive copy
# - Update documentation
# - Mark migration as complete
```

### Phase 4b: A28 Rollback (If Validation Fails)

```bash
# A27 detects validation failure and triggers rollback
# Example: Data loss >5% detected

# A28 automatic rollback:
$ python chromadb_rollback.py \
    --backup-path /path/to/backup/chromadb \
    --restore-url http://localhost:8000 \
    --report-output rollback_report.md

# Rollback verification:
# - Restore old database
# - Verify data integrity
# - Point application back to old DB
# - Generate detailed rollback report

# After rollback:
# 1. Investigate A26 failure
# 2. Fix migration logic
# 3. Restart from A26 with fixes
# 4. Re-run A27 validation
# 5. Only proceed to cutover after PASSED status
```

## Integration Points

### A26 → A27 Interface

**What A26 provides:**
- New ChromaDB with transformed data
- Migration log with statistics
- Checkpoint files for resume
- Verification summary

**What A27 expects:**
- Accessible new ChromaDB (HTTP or local)
- Accessible old ChromaDB (for comparison)
- All 9,832 chunks transferred
- Metadata in expected 12-field schema

### A27 → A28 Interface

**When rollback triggered:**
1. A27 sets `rollback_triggered = true`
2. A27 provides `rollback_reason` (specific failure)
3. A27 generates detailed validation report
4. A28 reads validation report
5. A28 initiates rollback based on reason

**Rollback Reasons:**
```json
{
  "data_loss_percentage > 5%": "Data Loss Detected",
  "semantic_divergence > 20%": "Search Results Diverged",
  "count_verification failed": "Chunk Count Mismatch",
  "embedding_integrity failed": "Embedding Corruption",
  "metadata_completeness failed": "Schema Violation",
  "duplicate_detection failed": "Duplicate IDs Found"
}
```

## Critical File Locations

```
/home/setup/infrafabric/

├── tools/
│   ├── chromadb_migration.py (A26 migration script)
│   ├── chromadb_migration_validator.py (A27 validation script)
│   ├── sample_test_queries.json (test queries for A27)
│   ├── CHROMADB_VALIDATOR_README.md (A27 documentation)
│   ├── VALIDATION_TEST_SPEC.md (A27 test specification)
│   └── MIGRATION_INTEGRATION_GUIDE.md (this file)
│
├── migration_checkpoints/
│   └── checkpoint_*.json (A26 progress checkpoints)
│
├── migration_logs/
│   └── migration_*.log (A26 detailed logs)
│
├── validation_logs/
│   ├── validation_*.log (A27 detailed logs)
│   ├── validation_report.md (A27 human-readable report)
│   └── validation_report.json (A27 machine-readable report)
│
└── migration_backups/
    └── backup_*.tar.gz (Backup before migration)
```

## Error Recovery Paths

### Migration Blocked at Import Phase

**Symptom:** A26 stuck at "Phase 4: Importing to ChromaDB"

**Recovery:**
```bash
# 1. Check latest checkpoint
$ cat migration_checkpoints/checkpoint_*.json | tail -1

# 2. Verify target DB connection
$ python -c "import chromadb; c = chromadb.HttpClient(host='localhost', port=8000); c.heartbeat()"

# 3. Check target DB disk space
$ df -h /path/to/target/chromadb

# 4. Resume migration from last checkpoint
$ python chromadb_migration.py \
    --source-url http://old:8000 \
    --target-url http://localhost:8000 \
    --resume-from checkpoint_20251130_105000.json
```

### Validation Fails Unexpectedly

**Symptom:** A27 crashes with exception

**Recovery:**
```bash
# 1. Check validation log
$ tail -50 validation_logs/validation_*.log

# 2. Check database connectivity
$ python -c "import chromadb; c = chromadb.HttpClient(host='localhost', port=8000); print(c.list_collections())"

# 3. Verify test queries file
$ python -m json.tool sample_test_queries.json

# 4. Re-run validation with verbose
$ python chromadb_migration_validator.py \
    --old-db-url http://old:8000 \
    --new-db-url http://localhost:8000 \
    --verbose
```

### Data Loss Detected

**Symptom:** Validation test 1 fails with "Count mismatch"

**Recovery:**
```bash
# This triggers automatic rollback (A28)
# Manual verification:

# 1. Check actual counts
$ python -c """
import chromadb
old = chromadb.HttpClient(host='old', port=8000)
new = chromadb.HttpClient(host='localhost', port=8000)
old_count = sum(c.count() for c in old.list_collections())
new_count = sum(c.count() for c in new.list_collections())
print(f'Old: {old_count}, New: {new_count}')
"""

# 2. If data loss confirmed, rollback and investigate A26
# 3. Check migration log for failed batches
$ grep -i "error\|failed" migration_logs/migration_*.log

# 4. Restart migration with smaller batch size
$ python chromadb_migration.py \
    --batch-size 50 \
    --source-url http://old:8000 \
    --target-url http://localhost:8000
```

## Performance Optimization

### Faster Migration (A26)

```bash
# Increase batch size (more memory but faster)
$ python chromadb_migration.py \
    --batch-size 500 \
    --source-url http://old:8000 \
    --target-url http://localhost:8000

# Parallel imports (if supported by ChromaDB)
$ python chromadb_migration.py \
    --workers 4 \
    --batch-size 100
```

### Faster Validation (A27)

```bash
# Skip semantic search tests (save ~20 min)
$ python chromadb_migration_validator.py \
    --old-db-url http://old:8000 \
    --new-db-url http://localhost:8000
    # (no --test-queries parameter)

# Use fewer test queries
$ python chromadb_migration_validator.py \
    --old-db-url http://old:8000 \
    --new-db-url http://localhost:8000 \
    --test-queries minimal_queries.json
    # (create minimal_queries.json with 5-10 queries)
```

## Monitoring During Migration

### Watch Progress (Terminal 1)

```bash
$ watch -n 10 'tail -20 migration_logs/migration_*.log'
```

### Monitor Resources (Terminal 2)

```bash
$ watch -n 5 'echo "=== CPU ===" && top -bn1 | head -5 && \
    echo "=== Memory ===" && free -h && \
    echo "=== Disk ===" && df -h /path/to/chromadb'
```

### Check Database Activity (Terminal 3)

```bash
# Monitor ChromaDB if it exposes metrics
$ curl http://localhost:8000/api/v1/metrics 2>/dev/null | jq .
```

## Post-Migration Checklist

- [ ] A26 migration completed successfully
- [ ] A27 validation all 8 tests PASSED
- [ ] rollback_triggered = false in validation report
- [ ] data_loss_percentage = 0.0
- [ ] semantic_divergence_percentage < 20%
- [ ] All 9,832 chunks verified
- [ ] No duplicate IDs found
- [ ] All metadata fields present (12/12)
- [ ] Embedding vectors valid
- [ ] Cutover approved by data owner
- [ ] Production pointer updated
- [ ] Smoke tests passed
- [ ] 24-hour monitoring completed
- [ ] Old database archived
- [ ] Migration documented

## Support & Troubleshooting

**Q: What if migration takes too long?**
A: Check batch size, network latency, or database load. Use checkpoints to resume.

**Q: What if validation divergence is 15%?**
A: This is WARNING status. Review which queries diverged and why. May proceed cautiously or retry migration.

**Q: Can I run validation while migration is in progress?**
A: No, wait for migration to complete. A27 needs consistent state.

**Q: What happens if production DB is queried during migration?**
A: No impact. Old DB remains active until cutover. A26 operates on copies.

**Q: How long to keep old database backup?**
A: Minimum 30 days. If issues discovered later, can restore from backup.

## References

- A26 Migration Script: `/home/setup/infrafabric/tools/chromadb_migration.py`
- A27 Validator: `/home/setup/infrafabric/tools/chromadb_migration_validator.py`
- A28 Rollback: (To be implemented)
- Test Spec: `/home/setup/infrafabric/tools/VALIDATION_TEST_SPEC.md`

## Citation

```
if://design/chromadb-migration-integration-v1.0-2025-11-30
Agents: A26 (Migration), A27 (Validation), A28 (Rollback)
Integration: Zero-downtime migration with validation gates
```

## IF.TTT Compliance

All migration steps are:
- **Traceable:** Checkpoint files, detailed logs
- **Transparent:** JSON reports with metrics
- **Trustworthy:** Automated validation gates

See: if://design/chromadb-migration-validator-v1.0-2025-11-30
