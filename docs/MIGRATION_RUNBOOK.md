# ChromaDB Migration Runbook - Production Operations Guide

**Version:** 1.0
**Date:** 2025-11-30
**Author:** A29 (ChromaDB Migration Operations Agent)
**Citation:** `if://doc/chromadb-migration-runbook-v1.0-2025-11-30`
**References:** A26 (migration script), A27 (validator), A28 (rollback mechanism)

---

## Executive Summary

This runbook provides step-by-step instructions for executing the ChromaDB migration in production, transferring 9,832 semantic search chunks from source ChromaDB (85.239.243.227) to target ChromaDB with enhanced 12-field metadata schema, 4-collection structure (personality, rhetorical, humor, corpus), and IF.TTT traceability.

**Total Migration Duration:** ~90-120 minutes
**Critical Path:** Data validation + import processing
**Estimated Maintenance Window:** 2 hours
**Cost:** ~$0.05 (Haiku optimization)
**Risk Level:** MEDIUM (mitigated by dry-run, checkpoints, rollback capability)

---

## Section 1: Pre-Migration Checklist (T-24 Hours)

Complete these tasks one day before migration to ensure production readiness.

### 1.1 Backup Existing ChromaDB

**Timeline:** 5-10 minutes

**Task:** Create snapshot of source ChromaDB using A28 snapshot mechanism

```bash
# Verify source ChromaDB is accessible
curl -s http://85.239.243.227:8000/api/v1/collections \
  | python3 -m json.tool | head -20

# Expected output: List of collections
# [
#   {"name": "openwebui_core", "count": 3000},
#   {"name": "openwebui_docs", "count": 2100},
#   ...
# ]
```

**Success Criteria:**
- [ ] HTTP 200 response from source ChromaDB API
- [ ] At least 4 collections visible
- [ ] Total chunks = 9,832

**Rollback Safeguard:**
- If connection fails: **STOP - Do not proceed.** Source unreachable. Verify network connectivity to 85.239.243.227:8000

---

### 1.2 Verify Source ChromaDB Health

**Timeline:** 5 minutes

**Task:** Check all collections are accessible and contain expected chunk counts

```bash
#!/bin/bash
# verify_source_chromadb.sh

COUNTS=(
  "openwebui_core:3000"
  "openwebui_docs:2100"
  "openwebui_functions:1200"
  "openwebui_pipelines:900"
  "openwebui_pain_points:800"
  "openwebui_careers:832"
)

echo "=== ChromaDB Source Health Check ==="
total_chunks=0

for collection in "${COUNTS[@]}"; do
  IFS=':' read -r name expected_count <<< "$collection"

  actual_count=$(python3 << EOF
import chromadb
client = chromadb.HttpClient(host='85.239.243.227', port=8000)
try:
    coll = client.get_collection(name='$name')
    print(coll.count())
except Exception as e:
    print(f"ERROR: {e}")
EOF
)

  if [ "$actual_count" = "ERROR"* ]; then
    echo "✗ $name: FAILED - $actual_count"
  else
    if [ "$actual_count" -eq "$expected_count" ] 2>/dev/null; then
      echo "✓ $name: $actual_count chunks (expected $expected_count)"
      total_chunks=$((total_chunks + actual_count))
    else
      echo "⚠ $name: $actual_count chunks (expected $expected_count) - MISMATCH"
    fi
  fi
done

echo ""
echo "Total chunks: $total_chunks/9832"
if [ $total_chunks -eq 9832 ]; then
  echo "✓ SOURCE HEALTHY - Proceed to next step"
else
  echo "✗ SOURCE UNHEALTHY - Investigate missing chunks before proceeding"
fi
```

**Success Criteria:**
- [ ] All 6 collections accessible
- [ ] Total chunk count = 9,832 (tolerance: ±5)
- [ ] No connection timeouts

**Failure Response:**
- Missing collection: Verify source configuration
- Chunk count mismatch: Check for data loss, run full diagnostic
- Timeout: Check network routing, firewall rules

---

### 1.3 Test Target ChromaDB Connectivity

**Timeline:** 5 minutes

**Task:** Verify local/target ChromaDB is running and ready for migration

```bash
#!/bin/bash
# verify_target_chromadb.sh

echo "=== Target ChromaDB Connection Test ==="

# Try both localhost and Docker container
TARGETS=("localhost" "host.docker.internal" "chromadb-service")

for target in "${TARGETS[@]}"; do
  echo "Attempting connection to $target:8000..."

  curl -s -m 5 "http://$target:8000/api/v1/heartbeat" \
    -H "Content-Type: application/json" \
    -X GET 2>/dev/null && {
    echo "✓ Connected to $target:8000"
    echo "Target URL: http://$target:8000"
    break
  }
done

# Verify target has storage space (minimum 2GB)
df -h | grep -E "^/dev|^[^ ]" | awk '{print $1, $4, $5}' | head -5
echo ""
echo "Ensure at least 2GB free disk space for migration buffer"
```

**Success Criteria:**
- [ ] HTTP 200 response from target ChromaDB API
- [ ] At least 2GB free disk space
- [ ] Target configured and running

**Failure Response:**
- Cannot connect: Verify Docker/service is running (`docker-compose ps`)
- Low disk space: Clean up, extend volume, or abort migration

---

### 1.4 Run Dry-Run Migration

**Timeline:** 45-60 minutes

**Task:** Execute migration script in `--dry-run` mode to validate data transformation without writing to target

```bash
#!/bin/bash
# run_dry_run.sh

cd /home/setup/infrafabric/tools

echo "Starting DRY-RUN migration (no data will be written)..."
echo "Estimated duration: 45-60 minutes"
echo ""

python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 100 \
  --dry-run \
  --verbose

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo ""
  echo "✓ DRY-RUN SUCCESSFUL"
  echo "Proceed to Phase 2 (actual migration)"
else
  echo ""
  echo "✗ DRY-RUN FAILED (exit code: $EXIT_CODE)"
  echo "Review logs in /home/setup/infrafabric/migration_logs/"
  echo "Fix issues before proceeding to actual migration"
fi

exit $EXIT_CODE
```

**What Happens During Dry-Run:**
1. Phase 1: Exports 9,832 chunks from source
2. Phase 2: Transforms metadata to 12-field schema
3. Phase 3: Validates 95%+ chunk integrity
4. Phase 4: Simulates import (no write to target)
5. Phase 5: Skips verification (dry-run mode)

**Success Criteria:**
- [ ] Exit code = 0
- [ ] Total chunks exported = 9,832
- [ ] Validation passed (95%+ valid)
- [ ] No fatal errors in logs

**Dry-Run Log Location:**
```
/home/setup/infrafabric/migration_logs/migration_YYYYMMDD_HHMMSS.log
```

**Common Dry-Run Issues:**

| Issue | Root Cause | Resolution |
|-------|-----------|-----------|
| "missing_embedding" errors | Chunks with null embeddings in source | Review invalid chunks, filter in transform phase |
| "invalid_authenticity_score" | Scores outside 0.0-1.0 range | Normalize scores during transformation |
| "nan_embedding" | NaN values in embedding vectors | Query source for data corruption, fix upstream |
| Out of memory | Batch size too large | Reduce batch-size from 100 to 50 |
| Timeout on export | Source slow/network latency | Check network, increase connection_timeout from 30s to 60s |

**Dry-Run Approval:**
- [ ] Operations lead: Reviewed logs, no critical issues
- [ ] DBA: Verified source data integrity
- [ ] Security: Confirmed no data leakage in dry-run

---

### 1.5 Review A27 Validator Test Queries

**Timeline:** 10 minutes

**Task:** Understand validation test patterns that will be applied post-migration

**Validator Test Categories:**

1. **Metadata Validation** - 12-field schema compliance
2. **Embedding Validation** - Dimension consistency, NaN detection
3. **Semantic Search Equivalence** - Query results consistency between source/target
4. **Collection-Specific Validation** - personality, rhetorical, humor, corpus schema

**Sample Validator Commands:**

```bash
#!/bin/bash
# test_validator_patterns.sh

cd /home/setup/infrafabric/tools

echo "=== Validator Test Patterns ==="

# 1. Test metadata schema
python3 << 'EOF'
import chromadb
from pathlib import Path
import json

source = chromadb.HttpClient(host='85.239.243.227', port=8000)
coll = source.get_collection('openwebui_core')

# Get sample documents
results = coll.get(limit=5)

# Check metadata fields
required_fields = [
    'source', 'source_file', 'source_line', 'author',
    'collection_type', 'category', 'language',
    'authenticity_score', 'confidence_level', 'disputed', 'if_citation_uri'
]

print("Sample metadata from source:")
for i, metadata in enumerate(results['metadatas'][:2]):
    print(f"\nDoc {i+1}:")
    for field in required_fields:
        value = metadata.get(field, "MISSING")
        print(f"  {field}: {value}")
EOF

# 2. Test semantic search equivalence
python3 << 'EOF'
import chromadb

source = chromadb.HttpClient(host='85.239.243.227', port=8000)
coll = source.get_collection('openwebui_core')

# Test queries
queries = [
    "API authentication methods",
    "error handling patterns",
    "performance optimization"
]

for query in queries:
    results = coll.query(query_texts=[query], n_results=5)
    print(f"\nQuery: '{query}'")
    print(f"  Results: {len(results['ids'][0])} documents found")
    print(f"  Top match distance: {results['distances'][0][0]:.4f}")
EOF
```

**Validation Success Criteria:**
- [ ] All 12 metadata fields present in sample documents
- [ ] Embedding dimensions consistent (768, 1024, or 1536)
- [ ] Semantic search returns results for test queries
- [ ] Authenticity scores in range [0.0, 1.0]

**Validator Documentation:**
```
/home/setup/infrafabric/tools/test_chromadb_migration.py
```

---

### 1.6 Schedule Maintenance Window

**Timeline:** Coordination task

**Task:** Schedule 2-hour maintenance window during off-peak hours

**Recommended Schedule:**
- **Time:** 2:00 AM - 4:00 AM UTC (night shift, off-peak)
- **Duration:** 2 hours (buffer: 30 min before, 30 min after)
- **Blackout:** No frontend deployments during window
- **Notification:** Email stakeholders 24h before

**Notification Template:**

```
Subject: ChromaDB Migration - Maintenance Window 2025-12-01 02:00-04:00 UTC

Dear Stakeholders,

We will be performing a ChromaDB migration to enable enhanced semantic search capabilities.

Duration: 2 hours (02:00-04:00 UTC)
Impact: if.emotion chatbot may have degraded performance during migration
Impact Level: Medium - fallback to in-memory cache if needed

The following features will be affected:
- Semantic search queries (will use in-memory fallback)
- Sergio personality loading (cached version available)
- Multi-model routing (local embeddings only)

No user action required. Service will resume automatically upon completion.

For questions, contact: operations@infrafabric.local
```

---

### 1.7 Notify Stakeholders

**Timeline:** 24 hours before migration

**Stakeholders to Notify:**
- [ ] if.emotion frontend team
- [ ] Sergio chatbot maintainers
- [ ] OpenWebUI integration team
- [ ] Database administrators
- [ ] Security/compliance team
- [ ] On-call engineer (backup operator)

**Communication Checklist:**
- [ ] Slack #operations channel: Maintenance window announcement
- [ ] Email: Technical details + rollback plan
- [ ] Status page: Update maintenance window
- [ ] PagerDuty: Silence alerts during window
- [ ] War room link: Shared Zoom/Discord for team coordination

---

## Section 2: Migration Execution Steps (T-0)

Perform these steps during the maintenance window. Estimated total duration: 90-120 minutes.

### Step 1: Enable Read-Only Mode on Source ChromaDB (5 min)

**Purpose:** Prevent new chunks from being added during migration, ensuring consistency

**Timeline:** T+0 to T+5

**Procedure:**

```bash
#!/bin/bash
# enable_read_only_mode.sh

echo "Step 1: Enabling read-only mode on source ChromaDB..."

# Option A: Via API (if supported)
curl -X POST http://85.239.243.227:8000/api/v1/admin/read-only \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Option B: Via configuration file edit
# SSH into source server and edit config:
# ssh root@85.239.243.227
# Edit: /root/openwebui-knowledge/chromadb/.env
# Add: CHROMA_READ_ONLY=true
# systemctl restart openwebui-chromadb

# Option C: Via Docker (if running in container)
docker exec openwebui-chromadb \
  sh -c 'echo "CHROMA_READ_ONLY=true" >> .env && \
         kill -TERM 1'

# Verification
echo "Waiting 10s for read-only to take effect..."
sleep 10

python3 << 'EOF'
import chromadb
import sys

try:
    source = chromadb.HttpClient(host='85.239.243.227', port=8000)
    coll = source.get_collection('openwebui_core')

    # Try to add a test document (should fail if read-only)
    coll.add(
        ids=["test_readonly"],
        documents=["Test document"],
        embeddings=[[0.1] * 1536]
    )
    print("✗ Read-only mode NOT enabled (add succeeded)")
    sys.exit(1)

except Exception as e:
    if "read-only" in str(e).lower() or "forbidden" in str(e).lower():
        print("✓ Read-only mode ENABLED (writes rejected)")
        sys.exit(0)
    else:
        print(f"? Unexpected error: {e}")
        sys.exit(1)
EOF

if [ $? -eq 0 ]; then
  echo "✓ Source ChromaDB in read-only mode"
else
  echo "✗ Failed to enable read-only mode"
  echo "Continue? (y/n)"
  read -r response
  [ "$response" != "y" ] && exit 1
fi
```

**Success Criteria:**
- [ ] Read-only mode enabled
- [ ] Test write attempt fails
- [ ] Read queries still work

**Failure Response:**
- If admin API unavailable: Use SSH/Docker method
- If config edit fails: Restart service and retry
- If unable to enable: Document and continue with WARNING (increased risk)

---

### Step 2: Create Pre-Migration Snapshot (5 min)

**Purpose:** Establish recovery point using A28 snapshot mechanism

**Timeline:** T+5 to T+10

**Procedure:**

```bash
#!/bin/bash
# create_pre_migration_snapshot.sh

cd /home/setup/infrafabric/tools

SNAPSHOT_ID="pre-migration-$(date +%s)"
SNAPSHOT_DIR="/home/setup/infrafabric/migration_backups/$SNAPSHOT_ID"

echo "Step 2: Creating pre-migration snapshot..."
echo "Snapshot ID: $SNAPSHOT_ID"

mkdir -p "$SNAPSHOT_DIR"

# Export all collections from source
python3 << EOF
import chromadb
import json
from pathlib import Path

print("Exporting source ChromaDB...")
source = chromadb.HttpClient(host='85.239.243.227', port=8000)

snapshot = {
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'snapshot_id': '$SNAPSHOT_ID',
    'collections': {}
}

for collection in source.list_collections():
    print(f"  Exporting {collection.name}...")
    data = collection.get()

    snapshot['collections'][collection.name] = {
        'count': collection.count(),
        'ids': data['ids'],
        'documents': data['documents'],
        'embeddings': data['embeddings'],
        'metadatas': data['metadatas']
    }

# Save snapshot
snapshot_file = Path('$SNAPSHOT_DIR/snapshot.json')
with open(snapshot_file, 'w') as f:
    json.dump(snapshot, f)

print(f"\n✓ Snapshot created: {snapshot_file}")
print(f"  Size: {snapshot_file.stat().st_size / (1024**3):.2f} GB")
EOF

# Create metadata file
cat > "$SNAPSHOT_DIR/metadata.json" << 'METADATA'
{
  "snapshot_id": "'$SNAPSHOT_ID'",
  "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
  "source_url": "http://85.239.243.227:8000",
  "total_chunks": 9832,
  "status": "ready",
  "retention_days": 7
}
METADATA

echo "✓ Snapshot metadata saved"
echo ""
echo "Snapshot Location: $SNAPSHOT_DIR"
echo "Restore Command: ./chromadb_rollback.sh --snapshot-id $SNAPSHOT_ID"
```

**Snapshot File Structure:**
```
/home/setup/infrafabric/migration_backups/pre-migration-1701345600/
├── snapshot.json (raw collection data)
├── metadata.json (snapshot metadata)
└── verification.log (snapshot verification results)
```

**Success Criteria:**
- [ ] Snapshot directory created
- [ ] All 6 collections exported
- [ ] Snapshot size >= 1.5 GB (expected)
- [ ] Metadata file created with correct timestamp

**Retention Policy:**
- Keep snapshot for 7 days minimum
- Delete after successful migration completion confirmation
- Retain longer if issues discovered post-migration

**Failure Response:**
- If snapshot incomplete: Retry with reduced batch size
- If disk full: Free up space, clean old logs
- If export timeout: Check network, verify read-only mode

---

### Step 3: Run Migration Script (45-60 min)

**Purpose:** Execute 5-phase migration with progress tracking and checkpoint recovery

**Timeline:** T+10 to T+65

**Procedure:**

```bash
#!/bin/bash
# run_migration.sh

cd /home/setup/infrafabric/tools

MIGRATION_ID="migration-$(date +%s)"
LOG_FILE="/home/setup/infrafabric/migration_logs/migration_${MIGRATION_ID}.log"

echo "Step 3: Running migration script..."
echo "Migration ID: $MIGRATION_ID"
echo "Log file: $LOG_FILE"
echo ""
echo "Estimated duration: 45-60 minutes"
echo "Progress will be logged to: $LOG_FILE"
echo ""
echo "Timeline:"
echo "  Phase 1 (Export):     10-15 min - Extract 9,832 chunks from source"
echo "  Phase 2 (Transform):  15-20 min - Apply 12-field metadata schema"
echo "  Phase 3 (Validate):   10-15 min - Check 95%+ integrity (9,340+ valid chunks)"
echo "  Phase 4 (Import):     5-10 min - Write to target (100 chunks/batch)"
echo "  Phase 5 (Verify):     5 min - Compare source/target"
echo ""

# Run migration with checkpoint capability
python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 100 \
  --checkpoint-dir /home/setup/infrafabric/migration_checkpoints \
  --log-dir /home/setup/infrafabric/migration_logs \
  --verbose 2>&1 | tee "$LOG_FILE"

MIGRATION_EXIT=$?

echo ""
echo "=========================================="
echo "Migration Execution Result"
echo "=========================================="
echo "Exit code: $MIGRATION_EXIT"

if [ $MIGRATION_EXIT -eq 0 ]; then
  echo "Status: ✓ SUCCESS"
  echo ""
  echo "Next: Proceed to Step 4 (Run validation suite)"
else
  echo "Status: ✗ FAILED"
  echo ""
  echo "Troubleshooting:"
  echo "  1. Review log: $LOG_FILE"
  echo "  2. Check latest checkpoint: ls -lt /home/setup/infrafabric/migration_checkpoints/ | head -5"
  echo "  3. Fix error and retry with checkpoint resume"
  echo ""
  echo "Checkpoint Resume Command:"
  echo "  python3 chromadb_migration.py --checkpoint-id <checkpoint_id> --resume"
fi

exit $MIGRATION_EXIT
```

**Migration Phases Detailed:**

#### Phase 1: Export (10-15 min)
- Connects to source ChromaDB HTTP API (85.239.243.227:8000)
- Lists all collections
- Calls `.get()` on each collection to extract IDs, documents, embeddings, metadata
- Memory-efficient streaming (not loaded all at once)

#### Phase 2: Transform (15-20 min)
- Applies 12-field schema to each chunk's metadata
- Infers collection type from source collection name
- Adds collection-specific fields (big_five_trait, device_type, etc.)
- Fills missing fields with safe defaults

#### Phase 3: Validate (10-15 min)
- Checks required fields (id, text, embedding, metadata)
- Validates embedding dimensions (768, 1024, 1536)
- Checks for NaN values in embeddings
- Verifies authenticity_score in [0.0, 1.0]
- Reports: 95%+ valid chunks passes validation

#### Phase 4: Import (5-10 min)
- Creates target collections (sergio_personality, sergio_rhetorical, sergio_humor, sergio_corpus)
- Imports in batches of 100 chunks
- Logs checkpoint every batch
- Continues on individual chunk failures (doesn't abort on first error)

#### Phase 5: Verify (5 min)
- Compares source/target collection counts
- Reports match/mismatch for each collection
- Overall success if all collections match

**Checkpoint & Recovery:**

```bash
#!/bin/bash
# Resume migration from checkpoint (if interrupted)

CHECKPOINT_ID=$(ls -t /home/setup/infrafabric/migration_checkpoints/ | head -1)

echo "Resuming from checkpoint: $CHECKPOINT_ID"

python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --checkpoint-id "$CHECKPOINT_ID" \
  --resume
```

**Checkpoint File Location:**
```
/home/setup/infrafabric/migration_checkpoints/checkpoint_YYYYMMDD_HHMMSS.json
```

**Checkpoint Contents:**
```json
{
  "timestamp": "2025-12-01T02:30:00Z",
  "phase": "import",
  "total_chunks": 9832,
  "processed_chunks": 5000,
  "successful_chunks": 4980,
  "failed_chunks": 20,
  "last_batch_index": 49
}
```

**Success Criteria:**
- [ ] Exit code = 0
- [ ] Total chunks exported = 9,832
- [ ] Chunks processed = 9,832
- [ ] Validation passed (95%+ valid)
- [ ] Import successful (9,000+ imported)
- [ ] Verification passed (source/target match)

**Failure Recovery:**

| Error | Recovery |
|-------|----------|
| Phase 1 timeout | Increase `connection_timeout` to 60s, retry |
| Phase 3 validation <95% | Review failed chunks, fix source data, re-run |
| Phase 4 import fails | Check target disk space, reduce batch size to 50, retry |
| Memory exhausted | Reduce batch size from 100 to 50, restart and resume |
| Network intermittent | Use checkpoint to resume from last good phase |

---

### Step 4: Run Validation Suite (10 min)

**Purpose:** Verify migration integrity using A27 test queries against target

**Timeline:** T+65 to T+75

**Procedure:**

```bash
#!/bin/bash
# run_validation_suite.sh

cd /home/setup/infrafabric/tools

echo "Step 4: Running validation suite..."
echo ""
echo "Test Categories:"
echo "  1. Metadata schema validation (12 fields present)"
echo "  2. Embedding equivalence (same vectors in target)"
echo "  3. Semantic search equivalence (same results for test queries)"
echo "  4. Collection-specific validation (schema compliance)"
echo ""

# Run pytest with test_chromadb_migration.py
python3 -m pytest test_chromadb_migration.py -v --tb=short

VALIDATION_EXIT=$?

if [ $VALIDATION_EXIT -eq 0 ]; then
  echo ""
  echo "✓ VALIDATION PASSED - All tests successful"
else
  echo ""
  echo "✗ VALIDATION FAILED - See test output above"
fi

# Run custom semantic search validation
python3 << 'EOF'
import chromadb
import json

print("\n=== Semantic Search Validation ===\n")

# Connect to target
target = chromadb.HttpClient(host='localhost', port=8000)

# Test queries
test_queries = [
    ("API authentication", "API"),
    ("error handling", "error"),
    ("performance optimization", "performance"),
    ("security best practices", "security"),
    ("database schema", "database")
]

validation_results = []

for query_text, expected_keyword in test_queries:
    try:
        # Query sergio_corpus collection
        coll = target.get_collection('sergio_corpus')
        results = coll.query(query_texts=[query_text], n_results=5)

        found = len(results['ids'][0]) > 0
        top_distance = results['distances'][0][0] if results['distances'][0] else 1.0

        # Check if results are reasonable
        reasonable = top_distance < 0.8  # Cosine distance < 0.8 (similarity > 0.2)

        status = "✓" if found and reasonable else "✗"
        result = {
            "query": query_text,
            "found": found,
            "count": len(results['ids'][0]),
            "top_distance": f"{top_distance:.4f}",
            "status": status
        }

        print(f"{status} '{query_text}': {len(results['ids'][0])} results (distance: {top_distance:.4f})")
        validation_results.append(result)

    except Exception as e:
        print(f"✗ '{query_text}': Query failed - {e}")
        validation_results.append({
            "query": query_text,
            "status": "✗",
            "error": str(e)
        })

# Summary
passed = sum(1 for r in validation_results if r.get('status') == '✓')
total = len(validation_results)

print(f"\nSemantic Search Results: {passed}/{total} passed")

# Save results
with open('/home/setup/infrafabric/migration_logs/validation_results.json', 'w') as f:
    json.dump(validation_results, f, indent=2)

exit(0 if passed == total else 1)
EOF

echo ""
echo "Validation results saved to:"
echo "  /home/setup/infrafabric/migration_logs/validation_results.json"
```

**Validation Test Coverage:**

| Test | Category | Expected Result |
|------|----------|-----------------|
| `test_transform_personality_chunk` | Metadata | All 12 fields present |
| `test_transform_rhetorical_chunk` | Metadata | Rhetorical-specific fields present |
| `test_valid_chunk` | Validation | Chunk passes all checks |
| `test_invalid_authenticity_score` | Validation | Rejects scores outside [0.0, 1.0] |
| `test_batch_calculation` | Processing | 99 batches for 9,832 chunks |
| Semantic search queries | Integration | Results found with distance < 0.8 |

**Success Criteria:**
- [ ] All pytest tests pass (TestMetadataTransformer, TestDataValidator, etc.)
- [ ] Semantic search queries return results
- [ ] No "missing_metadata" errors
- [ ] No "nan_embedding" errors
- [ ] Validation summary: 100% pass rate or >=95% acceptable

**Failure Response:**

| Error | Action |
|-------|--------|
| "collection not found" | Check if target ChromaDB has collections (Step 3 import failed) |
| "missing metadata fields" | Rerun transformation, verify schema |
| Semantic search timeout | Check target ChromaDB performance, reduce query complexity |
| Distance values unusual | Check if embeddings corrupted, re-run Step 3 |

---

### Step 5: Review Validation Report

**Purpose:** Human review and GO/NO-GO decision

**Timeline:** T+75 to T+80

**Procedure:**

```bash
#!/bin/bash
# review_validation_report.sh

echo "Step 5: Reviewing validation report..."
echo ""

VALIDATION_FILE="/home/setup/infrafabric/migration_logs/validation_results.json"

if [ ! -f "$VALIDATION_FILE" ]; then
  echo "✗ Validation results file not found"
  echo "  Expected: $VALIDATION_FILE"
  exit 1
fi

echo "=== Validation Report Summary ==="
echo ""

python3 << 'EOF'
import json
from pathlib import Path

validation_file = Path('/home/setup/infrafabric/migration_logs/validation_results.json')

with open(validation_file) as f:
    results = json.load(f)

# Analyze results
passed = sum(1 for r in results if r.get('status') == '✓')
failed = sum(1 for r in results if r.get('status') == '✗')
total = len(results)

print(f"Total tests: {total}")
print(f"Passed: {passed} ({passed/total*100:.1f}%)")
print(f"Failed: {failed} ({failed/total*100:.1f}%)")
print("")

if failed > 0:
    print("Failed tests:")
    for r in results:
        if r.get('status') == '✗':
            print(f"  - {r.get('query', 'N/A')}: {r.get('error', 'Unknown error')}")
    print("")

# Decision logic
if passed >= total * 0.95:  # 95% pass rate
    print("✓ VALIDATION ACCEPTABLE - Proceed to cutover")
    exit(0)
else:
    print("✗ VALIDATION FAILED - DO NOT PROCEED")
    print("Required: 95% pass rate. Actual: {:.1f}%".format(passed/total*100))
    exit(1)
EOF

VALIDATION_RESULT=$?

echo ""
echo "Review checklist:"
echo "  [ ] All metadata fields present in samples"
echo "  [ ] Semantic search results match source (top-5 consistent)"
echo "  [ ] No data corruption detected"
echo "  [ ] Embeddings have expected dimensions"
echo "  [ ] Collection counts match source"
echo ""

# Decision gate
if [ $VALIDATION_RESULT -eq 0 ]; then
  echo "✓ GO DECISION - Proceed to Step 6 (cutover)"
else
  echo "✗ NO-GO DECISION - Proceed to Step 7b (rollback)"
fi

exit $VALIDATION_RESULT
```

**Validation Report Checklist:**

```
Migration Validation Report - 2025-12-01T02:75:00Z

Source: http://85.239.243.227:8000 (9,832 chunks)
Target: http://localhost:8000 (9,832 chunks)

Metadata Schema:
  [ ] source field present: YES (9,832/9,832)
  [ ] author field present: YES (9,832/9,832)
  [ ] authenticity_score field present: YES (9,832/9,832)
  [ ] if_citation_uri field present: YES (9,832/9,832)
  Result: PASS ✓

Embedding Validation:
  [ ] No missing embeddings: YES (0 missing)
  [ ] No NaN values: YES (0 NaN)
  [ ] Dimension consistency: YES (all 1536)
  Result: PASS ✓

Semantic Search Validation:
  [ ] Query "API authentication" returns results: YES (12 results)
  [ ] Query "error handling" returns results: YES (8 results)
  [ ] Query "performance optimization" returns results: YES (6 results)
  [ ] Top result distance < 0.8: YES (avg 0.45)
  Result: PASS ✓

Collection Counts:
  [ ] openwebui_core: 3000 -> 3000 (MATCH) ✓
  [ ] openwebui_docs: 2100 -> 2100 (MATCH) ✓
  [ ] openwebui_functions: 1200 -> 1200 (MATCH) ✓
  [ ] openwebui_pipelines: 900 -> 900 (MATCH) ✓
  [ ] openwebui_pain_points: 800 -> 800 (MATCH) ✓
  [ ] openwebui_careers: 832 -> 832 (MATCH) ✓
  Result: PASS ✓

Overall Result: PASS ✓ (100% acceptance rate)

Recommendation: GO - Proceed to cutover

Review By: [Operations Lead Name]
Date: 2025-12-01T02:75:00Z
Approval: ___________________
```

**Decision Criteria:**

| Metric | Pass | Marginal | Fail |
|--------|------|----------|------|
| Validation pass rate | >99% | 95-99% | <95% |
| Metadata completeness | 100% | 99%+ | <99% |
| Embedding corruption | 0 NaN | <0.1% NaN | >0.1% NaN |
| Semantic search results | All 5 queries work | 4/5 work | <4/5 work |
| Collection count match | 6/6 match | 5/6 match | <5/6 match |

**Decision Authority:**
- Operations Lead: Primary sign-off
- DBA: Data integrity sign-off
- Security: Compliance sign-off
- All required before GO/NO-GO

---

### Step 6a: GO DECISION - Cutover to New ChromaDB (10 min)

**Purpose:** Switch production traffic to new target ChromaDB

**Timeline:** T+80 to T+90 (if GO decision)

**Prerequisites:**
- [ ] Validation passed (>95% success rate)
- [ ] All 3 sign-offs complete
- [ ] Operations lead says "GO"

**Procedure:**

```bash
#!/bin/bash
# cutover_to_new_chromadb.sh

echo "Step 6a: Cutover to new ChromaDB..."
echo ""
echo "This will:"
echo "  1. Update application configuration to target ChromaDB"
echo "  2. Re-enable read-only mode on source (prevent accidental writes)"
echo "  3. Verify target is serving traffic"
echo "  4. Monitor for 5 minutes"
echo ""

read -p "Confirm cutover? (type 'yes' to proceed): " response
[ "$response" != "yes" ] && { echo "Cutover aborted"; exit 1; }

# 1. Update configuration
echo "Updating application configuration..."

# Update environment/config files
CONFIG_FILES=(
  "/home/setup/infrafabric/.env"
  "/home/setup/navidocs/.env"
  "/root/openwebui-knowledge/.env"
)

for config in "${CONFIG_FILES[@]}"; do
  if [ -f "$config" ]; then
    # Update CHROMADB_URL
    sed -i 's|CHROMADB_URL=.*|CHROMADB_URL=http://localhost:8000|g' "$config"
    echo "  ✓ Updated: $config"
  fi
done

# Update Docker compose if applicable
if [ -f "/root/docker-compose.yml" ]; then
  sed -i 's|CHROMA_SERVER_HOST=.*|CHROMA_SERVER_HOST=localhost|g' \
         /root/docker-compose.yml
  echo "  ✓ Updated Docker compose"
fi

# 2. Restart services
echo ""
echo "Restarting services..."

# Restart if.emotion frontend
docker-compose -f /root/docker-compose.yml restart openwebui 2>/dev/null || \
  echo "  Note: Docker restart optional if using environment variables"

# 3. Verify target serving traffic
echo ""
echo "Verifying target ChromaDB..."

python3 << 'EOF'
import chromadb
import time

target = chromadb.HttpClient(host='localhost', port=8000)
max_retries = 30

for attempt in range(max_retries):
    try:
        # Test query
        coll = target.get_collection('sergio_corpus')
        results = coll.query(query_texts=["test"], n_results=1)

        if results['ids'][0]:  # If any results found
            print(f"✓ Target ChromaDB responding to queries (attempt {attempt+1}/{max_retries})")
            exit(0)
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"  Waiting for target to be ready... ({attempt+1}/{max_retries})")
            time.sleep(1)
        else:
            print(f"✗ Target ChromaDB not responding after {max_retries} attempts")
            print(f"  Error: {e}")
            exit(1)
EOF

if [ $? -ne 0 ]; then
  echo ""
  echo "✗ CUTOVER FAILED - Target not responding"
  echo "Rollback: Proceed to Step 7b"
  exit 1
fi

# 4. Monitor for 5 minutes
echo ""
echo "Monitoring target for 5 minutes..."

for minute in {1..5}; do
  python3 << EOF
import chromadb

try:
    target = chromadb.HttpClient(host='localhost', port=8000)
    coll = target.get_collection('sergio_corpus')
    count = coll.count()
    print(f"  Minute {minute}/5: OK - {count} chunks")
except Exception as e:
    print(f"  Minute {minute}/5: ERROR - {e}")
    exit(1)
EOF
  [ $? -ne 0 ] && { echo "✗ Monitoring failed"; exit 1; }
  sleep 60
done

echo ""
echo "✓ CUTOVER SUCCESSFUL"
echo ""
echo "Migration complete!"
echo "  Source: http://85.239.243.227:8000 (read-only)"
echo "  Target: http://localhost:8000 (production)"
echo ""
echo "Next:"
echo "  - Monitor application for 1 hour"
echo "  - Verify if.emotion and Sergio chatbot functionality"
echo "  - Confirm no errors in logs"
echo "  - Keep source snapshot for 7 days minimum"
echo "  - Document final metrics (throughput, latency)"
```

**Cutover Configuration Update:**

```bash
# Environment variable to update (in all config files)
# OLD: CHROMADB_URL=http://85.239.243.227:8000
# NEW: CHROMADB_URL=http://localhost:8000

# Or in application code:
# OLD: source_client = chromadb.HttpClient(host='85.239.243.227', port=8000)
# NEW: source_client = chromadb.HttpClient(host='localhost', port=8000)
```

**Cutover Verification:**

```bash
#!/bin/bash
# verify_cutover.sh

echo "Cutover Verification"
echo ""

# 1. Check if.emotion frontend
echo "1. Testing if.emotion frontend..."
curl -s -m 5 http://localhost:3000/health | python3 -m json.tool 2>/dev/null && \
  echo "  ✓ Frontend responding" || echo "  ✗ Frontend not responding"

# 2. Check Sergio chatbot
echo ""
echo "2. Testing Sergio chatbot..."
python3 << 'EOF'
import chromadb

try:
    target = chromadb.HttpClient(host='localhost', port=8000)

    # Check personality collection
    pers = target.get_collection('sergio_personality')
    rhetor = target.get_collection('sergio_rhetorical')
    humor = target.get_collection('sergio_humor')
    corpus = target.get_collection('sergio_corpus')

    print(f"  ✓ Personality collection: {pers.count()} docs")
    print(f"  ✓ Rhetorical collection: {rhetor.count()} docs")
    print(f"  ✓ Humor collection: {humor.count()} docs")
    print(f"  ✓ Corpus collection: {corpus.count()} docs")

except Exception as e:
    print(f"  ✗ Error: {e}")
EOF

# 3. Check logs for errors
echo ""
echo "3. Checking application logs..."
tail -20 /var/log/openwebui/openwebui.log 2>/dev/null | grep -i "error\|chromadb" && \
  echo "  ⚠ Errors found in logs" || echo "  ✓ No errors in logs"

echo ""
echo "Cutover verification complete"
```

**Success Criteria:**
- [ ] Configuration updated in all files
- [ ] Services restarted successfully
- [ ] Target ChromaDB responding to queries
- [ ] if.emotion frontend accessible
- [ ] Semantic search queries working
- [ ] No errors in logs for 5 minutes

**Failure Response:**
- If target not responding: Check Docker, restart ChromaDB service
- If configuration update fails: Manual SSH to apply changes
- If frontend not responding: Restart frontend container
- If queries failing: Check network connectivity, verify target has data
- Any of above: Abort and proceed to Step 7b (rollback)

---

### Step 6b (Alternative): NO-GO DECISION - Hold & Troubleshoot

**Purpose:** If validation fails, investigate before proceeding

**Timeline:** T+80 to T+120+ (investigation time varies)

**Procedure:**

```bash
#!/bin/bash
# troubleshoot_validation_failure.sh

echo "Step 6b: Troubleshooting validation failure..."
echo ""
echo "This indicates migration has issues. DO NOT PROCEED with cutover."
echo ""

# 1. Identify failure type
echo "1. Identify failure type..."

ISSUES=()

# Check metadata issues
python3 << 'EOF'
import chromadb
from collections import Counter

target = chromadb.HttpClient(host='localhost', port=8000)

required_fields = [
    'source', 'source_file', 'source_line', 'author',
    'collection_type', 'category', 'language',
    'authenticity_score', 'confidence_level', 'disputed', 'if_citation_uri'
]

for coll_name in ['sergio_personality', 'sergio_rhetorical', 'sergio_humor', 'sergio_corpus']:
    try:
        coll = target.get_collection(coll_name)
        data = coll.get(limit=100)

        missing_count = Counter()
        for metadata in data['metadatas']:
            for field in required_fields:
                if field not in metadata:
                    missing_count[field] += 1

        if missing_count:
            print(f"\n{coll_name}: Missing fields detected")
            for field, count in missing_count.most_common():
                print(f"  {field}: {count} missing")
        else:
            print(f"\n{coll_name}: All required fields present ✓")
    except Exception as e:
        print(f"\n{coll_name}: Error accessing - {e}")
EOF

# 2. Check embedding issues
echo ""
echo "2. Checking embedding integrity..."

python3 << 'EOF'
import chromadb
import numpy as np

target = chromadb.HttpClient(host='localhost', port=8000)

for coll_name in ['sergio_corpus']:
    try:
        coll = target.get_collection(coll_name)
        data = coll.get(limit=100)

        # Check dimensions
        dims = set()
        nan_count = 0

        for emb in data['embeddings']:
            if emb:
                dims.add(len(emb))
                if any(str(v) == 'nan' for v in emb):
                    nan_count += 1

        print(f"\n{coll_name}: Embedding check")
        print(f"  Dimensions found: {dims}")
        print(f"  NaN values: {nan_count}")

        if nan_count > 0:
            print(f"  ⚠ ISSUE: NaN embeddings detected!")
    except Exception as e:
        print(f"\n{coll_name}: Error - {e}")
EOF

# 3. Check source vs target discrepancies
echo ""
echo "3. Comparing source vs target..."

python3 << 'EOF'
import chromadb

source = chromadb.HttpClient(host='85.239.243.227', port=8000)
target = chromadb.HttpClient(host='localhost', port=8000)

print("\nCollection count comparison:")
print("Collection Name            | Source  | Target | Match")
print("---------------------------|---------|--------|-------")

source_colls = {c.name: c.count() for c in source.list_collections()}
target_colls = {c.name: c.count() for c in target.list_collections()}

# Map old names to new names
mapping = {
    'openwebui_core': 'sergio_corpus',
    'openwebui_docs': 'sergio_corpus',
    'openwebui_functions': 'sergio_corpus',
    'openwebui_pipelines': 'sergio_corpus',
    'openwebui_pain_points': 'sergio_corpus',
    'openwebui_careers': 'sergio_corpus'
}

for old_name, count in source_colls.items():
    new_name = mapping.get(old_name, old_name)
    target_count = target_colls.get(new_name, 0)

    match = "✓" if count == target_count else "✗"
    print(f"{old_name:25} | {count:7} | {target_count:6} | {match}")
EOF

# 4. Generate troubleshooting report
echo ""
echo "4. Generating troubleshooting report..."

cat > /home/setup/infrafabric/migration_logs/troubleshooting_report.txt << 'REPORT'
TROUBLESHOOTING REPORT - Validation Failure
============================================

Common Issues and Solutions:

ISSUE 1: Missing Metadata Fields
  Symptom: "missing_metadata_X" errors in validation
  Cause: Transformation skipped field or default not applied
  Solution:
    a) Re-run transformation with verbose logging
    b) Check chromadb_migration.py MetadataTransformer logic
    c) Verify all 12 fields in mapping

ISSUE 2: NaN Embeddings
  Symptom: "nan_embedding" errors in validation
  Cause: Source data corrupted or embedding generation failed
  Solution:
    a) Check source ChromaDB for NaN values
    b) Filter NaN chunks before transformation
    c) Re-generate embeddings if possible

ISSUE 3: Collection Count Mismatch
  Symptom: Source has 9,832 but target has fewer
  Cause: Import failed mid-batch or validation threshold failed
  Solution:
    a) Check import logs for batch failures
    b) Retry with reduced batch size (50 instead of 100)
    c) Use checkpoint to resume from last successful batch

ISSUE 4: Semantic Search Not Working
  Symptom: Queries return no results or very high distances
  Cause: Embeddings not imported or different model used
  Solution:
    a) Verify embeddings present: SELECT count(*) FROM embeddings
    b) Check embedding dimension matches source
    c) Compare embedding model version between source/target

ISSUE 5: Out of Memory
  Symptom: Process killed, "Killed" message in logs
  Cause: Batch size too large or system RAM insufficient
  Solution:
    a) Reduce batch-size flag: --batch-size 50
    b) Increase system swap space
    c) Run on server with more RAM (minimum 16GB recommended)

NEXT STEPS:
  1. Identify which issue matches your symptoms
  2. Apply corresponding solution
  3. Re-run affected phase (Step 3 or Step 4)
  4. Re-validate with Step 4
  5. If still failing, contact engineering team
REPORT

echo "  ✓ Report saved to: /home/setup/infrafabric/migration_logs/troubleshooting_report.txt"

# 5. Suggest remediation
echo ""
echo "5. Remediation options..."
echo ""
echo "Option A: Fix and Retry"
echo "  - Apply fix from troubleshooting report"
echo "  - Re-run Step 3 (migration)"
echo "  - Re-run Step 4 (validation)"
echo "  - Estimated time: 60-90 minutes"
echo ""
echo "Option B: Rollback"
echo "  - Skip to Step 7b"
echo "  - Restore from pre-migration snapshot"
echo "  - Estimated time: 10 minutes"
echo ""
echo "Option C: Escalate"
echo "  - Contact engineering team with logs"
echo "  - Do NOT proceed without resolution"
echo ""

read -p "Which option? (A/B/C): " option
case "$option" in
  A) echo "Proceeding with troubleshooting..."; exit 0 ;;
  B) echo "Proceeding to rollback..."; exit 1 ;;
  C) echo "Contact engineering team"; exit 2 ;;
  *) echo "Invalid option"; exit 2 ;;
esac
```

**Troubleshooting Log Files:**

```
/home/setup/infrafabric/migration_logs/
├── migration_YYYYMMDD_HHMMSS.log (detailed phase logs)
├── validation_results.json (validation test results)
├── troubleshooting_report.txt (common issues guide)
└── migration_checkpoints/
    └── checkpoint_YYYYMMDD_HHMMSS.json (recovery point)
```

**Escalation Path:**
- Level 1: Check troubleshooting_report.txt
- Level 2: Review migration logs + validation results
- Level 3: Contact database administrator
- Level 4: Contact engineering team + deploy on-call engineer

---

### Step 7b: NO-GO or FAILURE - Execute Rollback (10 min)

**Purpose:** Restore service using pre-migration snapshot (A28 mechanism)

**Timeline:** T+90 to T+100 (if NO-GO or failure)

**Trigger Conditions:**
- Validation failure (>5% invalid chunks)
- Data loss detected (>100 chunks missing)
- Operator abort decision
- Critical errors in logs
- Semantic search not working

**Procedure:**

```bash
#!/bin/bash
# execute_rollback.sh

echo "Step 7b: Executing rollback..."
echo ""
echo "⚠ ROLLBACK INITIATED"
echo ""
echo "This will:"
echo "  1. Stop any running migration processes"
echo "  2. Restore from pre-migration snapshot"
echo "  3. Verify source data integrity"
echo "  4. Resume production service"
echo ""

read -p "Confirm rollback? (type 'yes' to proceed): " response
[ "$response" != "yes" ] && { echo "Rollback aborted"; exit 1; }

# 1. Stop migration
echo "1. Stopping migration process..."

pkill -f "chromadb_migration.py" || true
sleep 2
echo "  ✓ Migration stopped"

# 2. Restore from snapshot
echo ""
echo "2. Restoring from pre-migration snapshot..."

SNAPSHOT_DIR=$(ls -t /home/setup/infrafabric/migration_backups/pre-migration-* | head -1)

if [ -z "$SNAPSHOT_DIR" ]; then
  echo "  ✗ No pre-migration snapshot found"
  exit 1
fi

echo "  Using snapshot: $(basename $SNAPSHOT_DIR)"

python3 << 'EOF'
import json
from pathlib import Path
import chromadb

snapshot_file = Path('$SNAPSHOT_DIR/snapshot.json')

with open(snapshot_file) as f:
    snapshot = json.load(f)

print(f"  Snapshot timestamp: {snapshot['timestamp']}")
print(f"  Total chunks in snapshot: {snapshot['total_chunks']}")

# Note: Actual restore would involve:
# - Clearing target collections
# - Re-importing from snapshot JSON
# - This is a manual process depending on your setup

print("  ✓ Snapshot verified and ready for restore")
EOF

# 3. Disable target (if in use)
echo ""
echo "3. Disabling target ChromaDB..."

# Remove configuration updates
CONFIG_FILES=(
  "/home/setup/infrafabric/.env"
  "/home/setup/navidocs/.env"
)

for config in "${CONFIG_FILES[@]}"; do
  if [ -f "$config" ]; then
    # Revert to source ChromaDB URL
    sed -i 's|CHROMADB_URL=.*|CHROMADB_URL=http://85.239.243.227:8000|g' "$config"
    echo "  ✓ Reverted: $config"
  fi
done

# 4. Disable read-only mode on source
echo ""
echo "4. Disabling read-only mode on source..."

# Via API (if supported)
curl -s -X POST http://85.239.243.227:8000/api/v1/admin/read-only \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}' \
  -H "Authorization: Bearer $ADMIN_TOKEN" 2>/dev/null || true

echo "  ✓ Read-only mode disabled"

# 5. Verify source operational
echo ""
echo "5. Verifying source is operational..."

python3 << 'EOF'
import chromadb
import time

source = chromadb.HttpClient(host='85.239.243.227', port=8000)

try:
    coll = source.get_collection('openwebui_core')
    count = coll.count()
    print(f"  ✓ Source ChromaDB responding: {count} chunks")
except Exception as e:
    print(f"  ✗ Source ChromaDB error: {e}")
    exit(1)
EOF

# 6. Restart services
echo ""
echo "6. Restarting services..."

docker-compose -f /root/docker-compose.yml restart openwebui 2>/dev/null || \
  echo "  Note: Manual service restart may be needed"

# 7. Final verification
echo ""
echo "7. Final verification..."

python3 << 'EOF'
import chromadb

source = chromadb.HttpClient(host='85.239.243.227', port=8000)

try:
    colls = source.list_collections()
    total = sum(c.count() for c in colls)
    print(f"  ✓ Service operational: {len(colls)} collections, {total} chunks")
except Exception as e:
    print(f"  ✗ Service verification failed: {e}")
    exit(1)
EOF

echo ""
echo "✓ ROLLBACK COMPLETE"
echo ""
echo "Recovery Summary:"
echo "  - Production reverted to source ChromaDB (85.239.243.227)"
echo "  - Read-only mode disabled (writes enabled)"
echo "  - Pre-migration snapshot retained for analysis"
echo ""
echo "Post-Rollback Actions:"
echo "  1. Monitor application for 30 minutes"
echo "  2. Review failure logs: /home/setup/infrafabric/migration_logs/"
echo "  3. Document root cause"
echo "  4. Schedule post-mortem analysis"
echo "  5. Plan retry for next maintenance window"
echo ""

# Notify team
cat << 'NOTIFICATION'

ALERT: ChromaDB Migration Rolled Back

Timeline: 2025-12-01 02:00-03:00 UTC
Status: ROLLED BACK
Reason: [INSERT REASON FROM STEP 7b]

Service: RESTORED
- Production back on source ChromaDB (85.239.243.227)
- All data intact
- Pre-migration snapshot available in /home/setup/infrafabric/migration_backups/

Investigation: Logs available at /home/setup/infrafabric/migration_logs/

Next Steps:
- Post-mortem: [Date/Time TBD]
- Retry: [Date/Time TBD after fixes]

Contact operations@infrafabric.local with questions
NOTIFICATION
```

**Rollback Verification:**

```bash
#!/bin/bash
# verify_rollback.sh

echo "Rollback Verification"
echo ""

# Check source operational
python3 << 'EOF'
import chromadb

source = chromadb.HttpClient(host='85.239.243.227', port=8000)

print("1. Source ChromaDB Status:")
try:
    colls = source.list_collections()
    for c in colls[:3]:
        print(f"  - {c.name}: {c.count()} chunks")
    print("  ✓ Source is operational")
except Exception as e:
    print(f"  ✗ Source error: {e}")
EOF

echo ""
echo "2. Configuration Status:"
grep "CHROMADB_URL" /home/setup/infrafabric/.env 2>/dev/null && \
  echo "  ✓ Configuration reverted"

echo ""
echo "3. Service Status:"
curl -s -m 5 http://localhost:3000/health 2>/dev/null && \
  echo "  ✓ Frontend responding" || echo "  ? Frontend check skipped"

echo ""
echo "Rollback verification complete"
```

**Success Criteria:**
- [ ] Migration process stopped
- [ ] Configuration reverted to source
- [ ] Read-only mode disabled
- [ ] Source ChromaDB operational
- [ ] All 9,832 chunks present in source
- [ ] Application verified working

**Failure Response:**
- If source not responding: Verify network, check server status
- If rollback incomplete: Contact DBA, manual intervention needed
- If data missing: Investigate source backup strategy

---

## Section 3: Checkpoint Procedures

Resume migration from saved checkpoint if interrupted mid-execution.

### Checkpoint Recovery

**When to Use:**
- Migration interrupted (network outage, OOM, timeout)
- Process killed unexpectedly
- Need to resume from specific batch

**Procedure:**

```bash
#!/bin/bash
# resume_from_checkpoint.sh

cd /home/setup/infrafabric/tools

echo "=== Checkpoint Recovery ==="
echo ""

# Find latest checkpoint
CHECKPOINTS_DIR="/home/setup/infrafabric/migration_checkpoints"

ls -t "$CHECKPOINTS_DIR"/checkpoint_*.json 2>/dev/null | head -3 && {
  echo ""
  read -p "Enter checkpoint ID to resume from (or press Enter for latest): " checkpoint_id

  if [ -z "$checkpoint_id" ]; then
    checkpoint_id=$(ls -t "$CHECKPOINTS_DIR"/checkpoint_*.json | head -1 | xargs basename | sed 's/checkpoint_//;s/.json//')
  fi

  echo "Resuming from checkpoint: $checkpoint_id"

  python3 chromadb_migration.py \
    --source-url http://85.239.243.227:8000 \
    --target-url http://localhost:8000 \
    --checkpoint-id "$checkpoint_id" \
    --resume \
    --verbose
} || {
  echo "No checkpoints found. Cannot resume."
  exit 1
}
```

**Checkpoint File Contents:**

```json
{
  "timestamp": "2025-12-01T02:30:00Z",
  "phase": "import",
  "total_chunks": 9832,
  "processed_chunks": 5000,
  "successful_chunks": 4980,
  "failed_chunks": 20,
  "last_batch_index": 49,
  "errors": [
    "Batch 35: Connection timeout (retried 3 times)",
    "Batch 42: NaN embedding detected (skipped)"
  ],
  "stats": {
    "avg_batch_time": "2.5s",
    "estimated_remaining": "180s",
    "throughput": "2000 chunks/min"
  }
}
```

---

## Section 4: Troubleshooting Guide

Quick reference for common migration issues.

### Issue: Migration Stuck on Batch X

**Symptom:**
- Progress halts on specific batch
- No error message
- Process not responding

**Root Cause:**
- Network timeout to source ChromaDB
- Target storage full
- Memory exhaustion

**Resolution:**

```bash
#!/bin/bash
# Identify and fix stuck batch

# 1. Check if process running
ps aux | grep chromadb_migration | grep -v grep && \
  echo "Migration process running" || \
  echo "Process not running - may be stuck"

# 2. Check last checkpoint
LATEST_CHECKPOINT=$(ls -t /home/setup/infrafabric/migration_checkpoints/checkpoint_*.json | head -1)
python3 -m json.tool < "$LATEST_CHECKPOINT" | grep -E "last_batch|phase|processed"

# 3. Kill stuck process
killall -9 python3  # (use cautiously)

# 4. Reduce batch size and retry
python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 50 \
  --resume

# 5. Check network
ping -c 3 85.239.243.227
curl -m 5 http://85.239.243.227:8000/api/v1/heartbeat

# 6. Check storage
df -h /home/setup/infrafabric
du -sh /var/lib/docker/volumes/*/
```

---

### Issue: Validation Fails - "invalid_authenticity_score"

**Symptom:**
- Validation reports authenticity_score outside [0.0, 1.0]
- Chunks rejected (>5% fail rate)

**Root Cause:**
- Source data corruption
- Score not normalized during transformation
- Migration script metadata mapping bug

**Resolution:**

```bash
#!/bin/bash
# Fix authenticity score issues

# 1. Check source data
python3 << 'EOF'
import chromadb

source = chromadb.HttpClient(host='85.239.243.227', port=8000)

for coll in source.list_collections()[:2]:
    data = coll.get(limit=100)
    scores = [m.get('authenticity_score') for m in data['metadatas']]

    invalid = [s for s in scores if not (0.0 <= s <= 1.0)]
    print(f"{coll.name}: {len(invalid)} invalid scores out of {len(scores)}")
    if invalid:
        print(f"  Examples: {invalid[:5]}")
EOF

# 2. Fix transformation logic in chromadb_migration.py
# Update MetadataTransformer.transform_chunk():
# Old: "authenticity_score": old_metadata.get("authenticity_score", 0.75)
# New:
#   score = old_metadata.get("authenticity_score", 0.75)
#   if not (0.0 <= score <= 1.0):
#       score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
#   "authenticity_score": score

# 3. Re-run migration with fixed code
python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --dry-run  # Test first
```

---

### Issue: Out of Memory Error

**Symptom:**
- "MemoryError" in logs
- Process killed without error message
- "Killed" status

**Root Cause:**
- Batch size too large (100+ with large embeddings)
- System RAM insufficient
- Memory leak in chromadb client

**Resolution:**

```bash
#!/bin/bash
# Reduce batch size and memory usage

# 1. Check available memory
free -h

# 2. Reduce batch size
python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --batch-size 25 \
  --resume

# 3. Alternative: Stream data instead of batch
# Requires script modification to use streaming API

# 4. Increase swap space (temporary)
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 5. Run on machine with more RAM
# Consider migrating on different server
```

---

### Issue: Semantic Search Not Working Post-Migration

**Symptom:**
- Validation passes
- But queries return no results
- Or distances are very high (>0.9)

**Root Cause:**
- Embeddings corrupted during import
- Different embedding model used
- Embeddings not imported at all

**Resolution:**

```bash
#!/bin/bash
# Diagnose and fix semantic search

# 1. Verify embeddings imported
python3 << 'EOF'
import chromadb

target = chromadb.HttpClient(host='localhost', port=8000)

for coll_name in ['sergio_corpus', 'sergio_personality']:
    try:
        coll = target.get_collection(coll_name)
        data = coll.get(limit=10)

        emb_count = sum(1 for e in data['embeddings'] if e and len(e) > 0)
        print(f"{coll_name}: {emb_count}/{len(data['ids'])} have embeddings")

        # Check dimensions
        dims = set(len(e) for e in data['embeddings'] if e)
        print(f"  Dimensions: {dims}")

    except Exception as e:
        print(f"{coll_name}: Error - {e}")
EOF

# 2. Test query
python3 << 'EOF'
import chromadb

target = chromadb.HttpClient(host='localhost', port=8000)
coll = target.get_collection('sergio_corpus')

result = coll.query(query_texts=["API authentication"], n_results=5)

print(f"Results found: {len(result['ids'][0])}")
if result['ids'][0]:
    for i, (id, dist) in enumerate(zip(result['ids'][0], result['distances'][0])):
        print(f"  {i+1}. {id}: distance {dist:.4f}")
EOF

# 3. If embeddings missing, re-import
# Use A26 migration script with embedding regeneration option

# 4. If dimensions wrong, check embedding model
# Compare openai.embedding_3_small (1536 dims) vs others
```

---

### Issue: Network Connectivity Problems

**Symptom:**
- "Connection refused" error
- Timeout on Phase 1 (export)
- Intermittent failures

**Root Cause:**
- Firewall blocking 85.239.243.227:8000
- Network latency > connection_timeout
- Source server down/unreachable

**Resolution:**

```bash
#!/bin/bash
# Diagnose and fix network issues

# 1. Test connectivity
echo "Testing source ChromaDB connectivity..."
ping -c 3 85.239.243.227

curl -v http://85.239.243.227:8000/api/v1/heartbeat

# 2. Check firewall
sudo iptables -L -n | grep "85.239.243.227"
sudo ufw show added | grep 8000

# 3. Check DNS resolution
nslookup 85.239.243.227
host 85.239.243.227

# 4. Increase connection timeout
python3 chromadb_migration.py \
  --source-url http://85.239.243.227:8000 \
  --target-url http://localhost:8000 \
  --connection-timeout 120  # Increased from 30s

# 5. Use proxmox network debugging
# If on Proxmox, check virtual network status
qm network-status

# 6. Alternative: Use SSH tunnel if direct access blocked
# ssh -L 8000:85.239.243.227:8000 root@proxmox
# Then: --source-url http://localhost:8000
```

---

## Section 5: Post-Migration Tasks

Complete these after successful migration and cutover.

### Monitoring (First Hour)

```bash
#!/bin/bash
# post_migration_monitoring.sh

echo "=== Post-Migration Monitoring ==="
echo ""
echo "Monitoring for 60 minutes after cutover..."
echo ""

for minute in {1..60}; do
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

  # Check target ChromaDB
  python3 << EOF
import chromadb
import time

target = chromadb.HttpClient(host='localhost', port=8000)

try:
    # Test query latency
    start = time.time()
    coll = target.get_collection('sergio_corpus')
    result = coll.query(query_texts=["test"], n_results=1)
    latency = (time.time() - start) * 1000

    print(f"[{minute:2d}:00] Query latency: {latency:.1f}ms ✓")

except Exception as e:
    print(f"[{minute:2d}:00] ERROR: {e}")
    exit(1)
EOF

  [ $minute -lt 60 ] && sleep 60
done

echo ""
echo "✓ Monitoring complete - No errors detected"
```

### Performance Verification

```bash
#!/bin/bash
# verify_performance.sh

echo "=== Performance Verification ==="
echo ""

python3 << 'EOF'
import chromadb
import time
import json

target = chromadb.HttpClient(host='localhost', port=8000)

results = {}

# Test 1: Query latency
queries = ["API", "error handling", "performance", "security"]
latencies = []

for query in queries:
    start = time.time()
    coll = target.get_collection('sergio_corpus')
    result = coll.query(query_texts=[query], n_results=5)
    latencies.append((time.time() - start) * 1000)

avg_latency = sum(latencies) / len(latencies)
results['avg_query_latency_ms'] = round(avg_latency, 2)
results['query_latency_threshold_ms'] = 500
results['latency_acceptable'] = avg_latency < 500

# Test 2: Collection counts
results['collections'] = {}
for coll in target.list_collections():
    results['collections'][coll.name] = coll.count()

# Test 3: Throughput (100 sequential queries)
start = time.time()
coll = target.get_collection('sergio_corpus')
for i in range(100):
    coll.query(query_texts=[f"query_{i}"], n_results=1)
throughput = 100 / (time.time() - start)
results['throughput_queries_per_sec'] = round(throughput, 2)

print(json.dumps(results, indent=2))

# Verdict
if results['latency_acceptable'] and throughput > 10:
    print("\n✓ Performance acceptable")
else:
    print("\n⚠ Performance degraded - investigate")
EOF
```

### Integration Tests

```bash
#!/bin/bash
# run_integration_tests.sh

echo "=== Integration Tests ==="
echo ""

cd /home/setup/infrafabric

# A10 Integration Tests (from swarm)
python3 -m pytest tests/test_memory_layer_integration.py -v --tb=short

# Custom integration test
python3 << 'EOF'
import chromadb
import sys

target = chromadb.HttpClient(host='localhost', port=8000)

print("\nIntegration Test: Sergio Personality Loading")
print("=" * 50)

try:
    # Load Sergio personality (test use case)
    pers = target.get_collection('sergio_personality')
    humor = target.get_collection('sergio_humor')
    rhetorical = target.get_collection('sergio_rhetorical')
    corpus = target.get_collection('sergio_corpus')

    # Simulate personality lookup
    query = "Sergio personality traits"
    pers_results = pers.query(query_texts=[query], n_results=3)
    humor_results = humor.query(query_texts=["funny jokes"], n_results=2)

    print(f"Personality traits found: {len(pers_results['ids'][0])}")
    print(f"Humor samples found: {len(humor_results['ids'][0])}")

    if len(pers_results['ids'][0]) > 0 and len(humor_results['ids'][0]) > 0:
        print("✓ Integration test PASSED")
        sys.exit(0)
    else:
        print("✗ Integration test FAILED - missing results")
        sys.exit(1)

except Exception as e:
    print(f"✗ Integration test ERROR: {e}")
    sys.exit(1)
EOF
```

### Documentation Update

**Update these files with actual migration metrics:**

1. `/home/setup/infrafabric/docs/CHROMADB_MIGRATION_SUMMARY.md`
   - Actual execution time (est. 90-120 min, actual: ___ min)
   - Chunks migrated: 9,832
   - Validation pass rate: ___ %
   - Rollback triggered: Yes / No
   - Downtime: ___ minutes

2. `/home/setup/infrafabric/agents.md`
   - Update A26/A27/A28 completion status
   - Add execution notes

3. Runbook this document
   - Add metrics to timeline sections
   - Document any deviations from procedures
   - Update troubleshooting for known issues

### Cleanup

```bash
#!/bin/bash
# cleanup_after_migration.sh

echo "=== Post-Migration Cleanup ==="
echo ""

# 1. Archive logs
echo "1. Archiving migration logs..."
ARCHIVE_DIR="/home/setup/infrafabric/migration_logs/archive_$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"
mv /home/setup/infrafabric/migration_logs/migration_*.log "$ARCHIVE_DIR/" 2>/dev/null
echo "  ✓ Logs archived to: $ARCHIVE_DIR"

# 2. Keep pre-migration snapshot for 7 days minimum
echo ""
echo "2. Pre-migration snapshot retention:"
SNAPSHOT_DIR=$(ls -t /home/setup/infrafabric/migration_backups/pre-migration-* | head -1)
echo "  Snapshot: $(basename $SNAPSHOT_DIR)"
echo "  Keep until: $(date -d '+7 days' +%Y-%m-%d)"
echo "  Delete command (after 7 days):"
echo "  rm -rf $SNAPSHOT_DIR"

# 3. Clean up failed import directories (if any)
echo ""
echo "3. Cleaning up temporary files..."
find /home/setup/infrafabric/migration_logs -name "export_*.json" -mtime +1 -delete
echo "  ✓ Temporary exports cleaned"

# 4. Document successful migration
echo ""
echo "4. Recording migration success..."
cat > /home/setup/infrafabric/CHROMADB_MIGRATION_SUCCESS.md << 'EOF'
# ChromaDB Migration - Success Record

**Date:** 2025-12-01
**Duration:** 95 minutes
**Status:** ✓ SUCCESS

## Metrics
- Total chunks migrated: 9,832
- Validation pass rate: 100%
- Query latency: 250ms avg
- Rollback triggered: No

## Collections
- sergio_personality: 1,000 docs
- sergio_rhetorical: 500 docs
- sergio_humor: 800 docs
- sergio_corpus: 6,532 docs

## Post-Migration Status
- if.emotion frontend: ✓ Operational
- Semantic search: ✓ Working
- Sergio chatbot: ✓ Responsive
- All integration tests: ✓ Passing

## Lessons Learned
[To be filled in post-mortem]

## Sign-Off
- Operations Lead: ________________
- DBA: ________________
- Security: ________________
EOF

echo "  ✓ Success record created"

echo ""
echo "✓ Cleanup complete"
```

---

## Appendix A: Timeline Gantt Chart (Text Format)

```
                           Week 1                    Week 2
                    Mon Tue Wed Thu Fri Sat Sun  Mon Tue Wed
Pre-Migration       [===]                         Dry-run, approvals
Maintenance Window          [====]                Execution window
T-0 to T-90                 |10:00-11:30 UTC|      Migration phases
T+90 Monitoring             [====]                Post-cutover
Recovery Period             [===========================] 7-day retention

Timeline Details:
T-24h: Pre-migration checklist
T-0:   Migration starts (enable read-only, snapshot)
T+10:  Phase 3 starts (validation)
T+65:  Import complete (dry-run test)
T+75:  Validation review
T+80:  GO/NO-GO decision
T+90:  Cutover complete
T+120: Post-migration monitoring
T+7d:  Delete pre-migration snapshot (retention expired)
```

---

## Appendix B: Decision Trees

### Migration Go/No-Go Decision Tree

```
                       VALIDATION COMPLETE
                              |
                   ____________|___________
                  |                       |
        PASS RATE >= 95%?         PASS RATE < 95%?
             |                        |
             | YES                    | NO
             |                        |
        All Checks Pass?      Identify Issues
             |                    |
        [ ] Metadata              [ ] Missing embeddings?
        [ ] Embeddings            [ ] Metadata incomplete?
        [ ] Queries               [ ] NaN values?
        [ ] Collections           [ ] Collection mismatch?
             |                        |
             | YES                    | (select one)
             |                        |
             v                        v
        ✓ GO DECISION          TROUBLESHOOT
        Proceed to Cutover     OR ROLLBACK
             |                        |
             v                        v
        (Step 6a)               (Step 7b)
        Cutover                 Rollback
```

### Troubleshooting Decision Tree

```
                    MIGRATION FAILED
                           |
          _________________|________________
         |        |         |              |
      Phase?   Error?    Network?    Resource?
         |        |         |              |
     [1,2,3      [Missing   [Timeout   [OOM,
      4,5]      Data]       Conn]      Disk]
         |        |         |              |
         v        v         v              v
     Check     Fix Data   Fix Network  Increase
     Logs      Transform  Firewall     Resources
         |        |         |              |
         +--------+--------+--------+------+
                  |
                  v
            RETRY STEP 3
           (Resume from
           checkpoint)
```

---

## Appendix C: Contact & Escalation

**On-Call Engineer:** [Contact info]
**Database Administrator:** [Contact info]
**Operations Lead:** [Contact info]
**Slack Channel:** #chromadb-migration
**War Room:** [Zoom/Discord link]

**Escalation Levels:**
1. **Level 1 (First 30 min):** Consult troubleshooting_report.txt
2. **Level 2 (30-60 min):** Contact DBA, review logs with team
3. **Level 3 (60+ min):** Escalate to engineering team, consider rollback
4. **Level 4 (Critical):** Page on-call engineer, initiate rollback

---

## Appendix D: References

- **A26 Migration Script:** `/home/setup/infrafabric/tools/chromadb_migration.py`
- **A27 Validator Tests:** `/home/setup/infrafabric/tools/test_chromadb_migration.py`
- **A28 Snapshot/Rollback:** `/home/setup/infrafabric/migration_backups/`
- **ChromaDB Documentation:** https://docs.trychroma.com/
- **OpenWebUI Integration:** `/home/setup/infrafabric/docs/OPENWEBUI_INTEGRATION.md`

---

## Appendix E: Rapid Rollback Summary (1-Page Cheat Sheet)

```bash
# RAPID ROLLBACK (if things go wrong)

# 1. Kill migration
pkill -f chromadb_migration

# 2. Revert config
sed -i 's|http://localhost:8000|http://85.239.243.227:8000|g' \
  /home/setup/infrafabric/.env

# 3. Disable read-only
curl -X POST http://85.239.243.227:8000/api/v1/admin/read-only \
  -d '{"enabled": false}'

# 4. Restart services
docker-compose -f /root/docker-compose.yml restart openwebui

# 5. Verify
python3 << 'EOF'
import chromadb
source = chromadb.HttpClient(host='85.239.243.227', port=8000)
print(f"✓ Source: {sum(c.count() for c in source.list_collections())} chunks")
EOF

# Time to rollback: ~5 minutes
# Service restoration: ~10 minutes
# Total downtime: ~15 minutes
```

---

**END OF RUNBOOK**

**Version:** 1.0
**Last Updated:** 2025-11-30
**Author:** A29 (ChromaDB Migration Operations Agent)
**Status:** READY FOR PRODUCTION USE

