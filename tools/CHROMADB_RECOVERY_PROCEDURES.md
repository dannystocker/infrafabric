# ChromaDB Rollback & Recovery Procedures

**Document ID:** if://design/chromadb-recovery-procedures-v1.0-2025-11-30
**Status:** Active
**Last Updated:** 2025-11-30
**Author:** A28 (ChromaDB Migration Rollback Agent)

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Snapshot Creation](#snapshot-creation)
4. [Rollback Procedures](#rollback-procedures)
5. [Emergency Recovery](#emergency-recovery)
6. [Trigger Mechanisms](#trigger-mechanisms)
7. [Validation & Verification](#validation-and-verification)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Safety Features](#safety-features)

---

## Overview

### Mission

Implement a zero-downtime, fast recovery system for ChromaDB migration failures. Provide ability to restore to pre-migration state within 5 minutes (RTO < 5 min) if issues are detected.

### Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **chromadb_snapshot.py** | Create and manage snapshots | `/home/setup/infrafabric/tools/chromadb_snapshot.py` |
| **chromadb_rollback.py** | Execute rollback and recovery | `/home/setup/infrafabric/tools/chromadb_rollback.py` |
| **chromadb-rollback.sh** | CLI wrapper for safe access | `/home/setup/infrafabric/tools/chromadb-rollback.sh` |
| **snapshots** | Compressed snapshot storage | `/home/setup/infrafabric/chromadb_snapshots/` |
| **manifests** | Snapshot metadata | `/home/setup/infrafabric/chromadb_snapshots/manifests/` |
| **logs** | Audit trail | `/home/setup/infrafabric/chromadb_snapshots/logs/` |

### Key Metrics

- **Snapshot Creation Time:** < 5 minutes (for 9,832 chunks)
- **Snapshot Size:** ~28 MB (compressed, 72% reduction from original)
- **Rollback Time:** < 5 minutes (full restore)
- **Partial Rollback:** < 2 minutes (single collection)
- **Retention Period:** 7 days (auto-delete)
- **Checksum:** SHA-256 (integrity verification)

---

## System Architecture

### Pre-Migration Sequence

```
1. Create snapshot of source ChromaDB
   ├─ Export all collections
   ├─ Bundle metadata & config
   ├─ Compress with gzip
   ├─ Calculate SHA-256 checksum
   └─ Save manifest (JSON)

2. Start migration
   ├─ Transform metadata
   ├─ Validate transformed data
   └─ Import to target ChromaDB

3. If migration fails
   └─ Initiate rollback
      ├─ Verify snapshot integrity
      ├─ Stop writes (read-only mode)
      ├─ Restore from snapshot
      ├─ Verify restoration
      └─ Resume normal operations
```

### Storage Structure

```
/home/setup/infrafabric/chromadb_snapshots/
├── snapshots/
│   ├── snapshot_20251130_143022.tar.gz    (archive)
│   ├── snapshot_pre_migration.tar.gz      (named)
│   └── ...
├── manifests/
│   ├── snapshot_20251130_143022.json      (metadata)
│   ├── snapshot_pre_migration.json
│   └── ...
└── logs/
    ├── snapshot_20251130_143022.log       (creation log)
    ├── rollback_20251130_153045.log       (rollback log)
    ├── rollback_audit.jsonl               (audit trail)
    └── ...
```

---

## Snapshot Creation

### Pre-Migration Snapshot

Create a snapshot **before** migration starts:

```bash
./chromadb-rollback.sh snapshot create --name "pre_migration_2025-11-30"
```

Or using Python directly:

```bash
python3 chromadb_snapshot.py \
    --chromadb-url http://localhost:8000 \
    --action create \
    --snapshot-name "pre_migration_2025-11-30"
```

### Automatic Snapshots

During migration, the A26 migration script can trigger snapshot creation:

```python
# In chromadb_migration.py
from chromadb_snapshot import SnapshotCreator

# Before migration
creator = SnapshotCreator(source_client, logger, config)
success, archive_path = creator.create_snapshot("pre_migration")

if not success:
    logger.error("Snapshot creation failed - aborting migration")
    sys.exit(1)
```

### Snapshot Contents

Each snapshot contains:

1. **collections.json** - Full export of all collections with batches
   ```json
   {
     "collection_name": {
       "batch_000000": [
         {
           "id": "chunk_id",
           "text": "document text",
           "embedding": [0.1, 0.2, ...],
           "metadata": {...}
         }
       ]
     }
   }
   ```

2. **metadata.json** - ChromaDB configuration
   ```json
   {
     "chromadb_version": "0.3.21",
     "snapshot_timestamp": "2025-11-30T14:30:22",
     "collections_count": 4,
     "total_chunks": 9832
   }
   ```

3. **Manifest** - Integrity and reference data (see schema)

---

## Rollback Procedures

### Full Rollback (Complete Restore)

Use when entire migration must be reverted:

```bash
# Dry-run first to verify
./chromadb-rollback.sh rollback snapshot_20251130_143022 --dry-run

# Perform actual rollback
./chromadb-rollback.sh rollback snapshot_20251130_143022
```

**Steps:**
1. Verify snapshot integrity (checksum)
2. Extract TAR/gzip archive
3. Load collections.json
4. Clear target collections (optional)
5. Restore batches to target ChromaDB
6. Verify restoration matches original
7. Resume normal operations

**RTO:** < 5 minutes

### Partial Rollback (Failed Collections Only)

Use when only specific collections failed:

```bash
# Rollback only failed collections
./chromadb-rollback.sh rollback snapshot_20251130_143022 \
    --partial \
    --failed-collections "sergio_corpus,sergio_personality"
```

**Steps:**
1. Verify snapshot integrity
2. Extract archive
3. Load only specified collections
4. Restore to target
5. Verify restoration
6. Leave other collections unchanged

**RTO:** < 2 minutes

### Point-in-Time Recovery

Restore to specific checkpoint during migration:

```python
# Get snapshot info
snapshot_info = inspector.get_snapshot_info("snapshot_20251130_143022")

# Show available batches
for collection, batches in snapshot_info["batch_metadata"].items():
    print(f"{collection}: {len(batches)} batches available")

# Restore specific batches
executor.restore_partial_batches(
    snapshot_id="snapshot_20251130_143022",
    collections={
        "sergio_corpus": ["batch_000000", "batch_000001"]
    }
)
```

---

## Emergency Recovery

### Automatic Trigger (A27 Validation)

When validation detects >5% data loss:

```python
# In chromadb_migration.py (after A27 validation)
if validation_results["valid_chunks"] / total_chunks < 0.95:
    logger.error("Validation failed - initiating automatic rollback")

    rollback = RollbackExecutor(
        client, logger, config, audit_log
    )
    success, entry = rollback.rollback_from_snapshot("pre_migration_2025-11-30")

    if success:
        logger.info("Automatic rollback completed successfully")
        sys.exit(0)
    else:
        logger.error("Automatic rollback failed - manual intervention required")
        sys.exit(1)
```

### Time-Based Trigger

Automatic rollback if migration exceeds time limit:

```bash
# In automation/cron job
MIGRATION_START=$(date +%s)
timeout 3600 python3 chromadb_migration.py ...

if [ $? -eq 124 ]; then
    # Timeout - migrate exceeded 1 hour
    echo "Migration timeout - initiating rollback"
    ./chromadb-rollback.sh rollback snapshot_20251130_143022
fi
```

### Manual Trigger

Operator-initiated rollback:

```bash
# 1. Verify snapshot
./chromadb-rollback.sh snapshot verify snapshot_20251130_143022

# 2. Confirm audit trail
./chromadb-rollback.sh audit-log

# 3. Perform rollback
./chromadb-rollback.sh rollback snapshot_20251130_143022
```

---

## Trigger Mechanisms

### Trigger Types

| Trigger | Condition | Action | RTO |
|---------|-----------|--------|-----|
| **Manual** | Operator decision | Full rollback | < 5 min |
| **Automatic (A27)** | >5% data loss | Full rollback | < 5 min |
| **Time-based** | Migration > 2 hours | Full rollback | < 5 min |
| **Connection Loss** | ChromaDB unavailable | Pause migration | N/A |
| **Disk Space** | < 100MB available | Alert + pause | N/A |

### Configuration

Edit `/home/setup/infrafabric/tools/chromadb_migration.py`:

```python
# Automatic trigger threshold
VALIDATION_FAILURE_THRESHOLD = 0.95  # 5% failure rate

# Time-based trigger
MIGRATION_MAX_TIME = 3600  # 1 hour (seconds)

# Trigger action
AUTOMATIC_ROLLBACK_ENABLED = True
```

---

## Validation & Verification

### Pre-Rollback Verification

Snapshot must pass integrity check before rollback:

```bash
./chromadb-rollback.sh snapshot verify snapshot_20251130_143022
```

Checks:
- Manifest file exists
- Archive file exists
- SHA-256 checksum matches
- Archive is readable and non-corrupted

### Post-Restoration Verification

After restore, verify data matches original:

```
For each collection:
  1. Count documents in restored collection
  2. Compare to count in snapshot manifest
  3. Verify checksums of sample embeddings
  4. Validate metadata schema
```

Results logged to: `/home/setup/infrafabric/chromadb_snapshots/logs/rollback_*.log`

### System Health Check

```bash
./chromadb-rollback.sh health-check
```

Verifies:
- Python 3 installed
- ChromaDB connectivity
- Snapshot directory writable
- Disk space available

---

## Troubleshooting

### Issue: Snapshot Creation Fails

**Symptom:** "Archive creation failed"

**Solution:**
1. Verify disk space: `df -h /home/setup/infrafabric/chromadb_snapshots/`
2. Check ChromaDB connection: `./chromadb-rollback.sh health-check`
3. Review log: `tail -f /home/setup/infrafabric/chromadb_snapshots/logs/snapshot_*.log`
4. Retry: `./chromadb-rollback.sh snapshot create --name "retry_1"`

### Issue: Rollback Verification Fails

**Symptom:** "Document count mismatch: 9832 vs 9765"

**Solution:**
1. Verify snapshot: `./chromadb-rollback.sh snapshot verify <snapshot_id>`
2. Check available disk space during restore
3. Review detailed log: `cat /home/setup/infrafabric/chromadb_snapshots/logs/rollback_*.log`
4. Retry rollback: `./chromadb-rollback.sh rollback <snapshot_id>`

### Issue: Checksum Mismatch

**Symptom:** "Checksum mismatch - snapshot may be corrupted"

**Solution:**
1. Snapshot is corrupted - cannot restore
2. Create new snapshot: `./chromadb-rollback.sh snapshot create`
3. Delete corrupted: `rm /home/setup/infrafabric/chromadb_snapshots/snapshot_*.tar.gz`
4. Review filesystem integrity

### Issue: Restore Takes > 5 Minutes

**Symptom:** Large restoration time

**Solutions:**
- Use partial rollback for specific collections
- Increase batch size (may impact stability)
- Check ChromaDB load: `top`, `vmstat 1 5`
- Review network latency if using HTTP client

---

## Best Practices

### Pre-Migration Checklist

- [ ] Create snapshot: `./chromadb-rollback.sh snapshot create --name "pre_migration_2025-11-30"`
- [ ] Verify snapshot: `./chromadb-rollback.sh snapshot verify snapshot_20251130_*`
- [ ] Verify health: `./chromadb-rollback.sh health-check`
- [ ] Review logs: `tail -20 /home/setup/infrafabric/chromadb_snapshots/logs/*.log`
- [ ] Confirm disk space: `df -h /home/setup/infrafabric/chromadb_snapshots/`
- [ ] Test dry-run rollback: `./chromadb-rollback.sh rollback <snapshot_id> --dry-run`

### Snapshot Lifecycle

| Phase | Action | Command |
|-------|--------|---------|
| **Create** | Before migration | `snapshot create` |
| **Verify** | After creation | `snapshot verify` |
| **Monitor** | During migration | `status` |
| **Keep** | During retention period | Auto (7 days) |
| **Cleanup** | After retention expires | Auto (or `cleanup`) |

### Retention Policy

- **Retention Period:** 7 days
- **Automatic Cleanup:** Daily at 00:00 UTC
- **Manual Cleanup:** `./chromadb-rollback.sh cleanup`

### Monitoring

Monitor rollback system:

```bash
# Check recent operations
./chromadb-rollback.sh status

# View audit trail
./chromadb-rollback.sh audit-log

# Monitor logs in real-time
tail -f /home/setup/infrafabric/chromadb_snapshots/logs/snapshot_*.log
```

---

## Safety Features

### Confirmation Prompts

Full rollback requires explicit confirmation:

```
WARNING: CRITICAL: This will RESTORE ChromaDB from snapshot: snapshot_20251130_143022
WARNING: All data written since snapshot will be LOST
Are you sure? Type 'yes' to confirm:
```

### Dry-Run Testing

Test rollback without actual restore:

```bash
./chromadb-rollback.sh rollback <snapshot_id> --dry-run
```

Output shows what **would** be restored without modifying anything.

### Audit Logging

All operations logged to audit trail:

```bash
./chromadb-rollback.sh audit-log
```

Output (JSONL format):
```json
{"timestamp": "2025-11-30T15:30:45", "action": "rollback", "snapshot_id": "...", "status": "completed", "rollback_success": true}
```

### Integrity Checks

- **Pre-snapshot:** Verify ChromaDB accessible
- **Post-snapshot:** Verify archive readable
- **Pre-rollback:** Verify checksum matches
- **Post-rollback:** Verify document counts match
- **Continuous:** Monitor disk space

### Read-Only Mode

During restoration, ChromaDB can be set to read-only:

```python
# In rollback executor
client.set_read_only(True)
try:
    # Restore from snapshot
    executor._restore_from_snapshot(snapshot_id, manifest)
finally:
    client.set_read_only(False)
```

---

## Integration with Migration Pipeline

### A26 → A27 → A28

```
A26 (Migration Script)
  ├─ Call: snapshot create (A28)
  ├─ Execute migration
  ├─ Call: A27 validation
  └─ If A27 fails: Call: rollback (A28)

A27 (Validation)
  ├─ Check data integrity
  ├─ Calculate loss percentage
  └─ Trigger: rollback if loss > 5%

A28 (Rollback)
  ├─ Verify snapshot
  ├─ Extract archive
  ├─ Restore collections
  └─ Log audit entry
```

### Example Integration Code

```python
# In chromadb_migration.py

from chromadb_snapshot import SnapshotCreator
from chromadb_rollback import RollbackExecutor
from chromadb_validation import DataValidator  # A27

# Phase 0: Pre-migration snapshot
snapshot_creator = SnapshotCreator(source_client, logger, config)
snapshot_success, snapshot_path = snapshot_creator.create_snapshot("pre_migration")

if not snapshot_success:
    logger.error("Snapshot creation failed")
    sys.exit(1)

try:
    # Phase 1-4: Migration
    run_migration(source_client, target_client, logger)

    # Phase 5: Validation (A27)
    validator = DataValidator(logger)
    validation_passed, results = validator.validate_all(transformed_data)

    if not validation_passed and results["valid_percent"] < 95.0:
        logger.error("Validation failed - initiating automatic rollback")

        # Automatic rollback (A28)
        rollback = RollbackExecutor(
            target_client, logger, config, audit_log
        )
        success, audit_entry = rollback.rollback_from_snapshot("pre_migration")
        audit_log.log_entry(audit_entry)

        if success:
            logger.info("Rollback completed - migration aborted")
            sys.exit(0)
        else:
            logger.error("Rollback failed - manual intervention required")
            sys.exit(1)

    logger.info("Migration completed successfully")

except Exception as e:
    logger.error(f"Migration failed: {e}")
    # Manual rollback would be triggered by operator
    sys.exit(1)
```

---

## Support & Documentation

- **Schema:** `/home/setup/infrafabric/tools/CHROMADB_ROLLBACK_SCHEMA.json`
- **This Guide:** `/home/setup/infrafabric/tools/CHROMADB_RECOVERY_PROCEDURES.md`
- **Logs:** `/home/setup/infrafabric/chromadb_snapshots/logs/`
- **Citation:** if://design/chromadb-recovery-procedures-v1.0-2025-11-30

---

**End of Document**
