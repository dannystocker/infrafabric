# ChromaDB Migration Validator - A27

## Mission

Create comprehensive validation suite to verify embedding integrity and metadata correctness post-migration.

After A26 migrates 9,832 chunks from old ChromaDB to new ChromaDB with updated schema (4 collections, 12-field metadata), A27 validates:

- ✓ All embeddings transferred correctly (no corruption)
- ✓ Metadata schema matches A7's 12-field design
- ✓ Semantic search still works (query results match pre-migration)
- ✓ No data loss or duplication
- ✓ Automatic rollback trigger if validation fails

## Architecture

### 8 Validation Tests

1. **Count Verification**
   - Verify 9,832 chunks total across 4 collections
   - Check per-collection counts match expected distribution
   - Expected: personality=23, rhetorical=5, humor=28, corpus=67
   - Threshold: <5% data loss tolerance

2. **Embedding Integrity**
   - Dimension check (expect consistent vector dimensions)
   - NaN/Inf detection (no corrupted embeddings)
   - Vector statistics (mean, std consistency)
   - Flags unusual dimensions (not 768/1024/1536)

3. **Metadata Completeness**
   - 12 required fields present in all chunks:
     - Attribution: source, source_file, source_line, author
     - Classification: collection_type, category, language
     - Quality: authenticity_score, confidence_level, disputed, if_citation_uri
   - Validates required fields on 100% of chunks

4. **Semantic Search Equivalence**
   - Runs 20 test queries on old ChromaDB
   - Runs same queries on new ChromaDB
   - Compares top-10 results (IDs, distances)
   - Calculates Jaccard similarity per query
   - Threshold: <20% average divergence

5. **Collection Distribution**
   - Verifies correct chunk assignment to collections
   - Checks collection_type field matches parent collection
   - Ensures personality chunks only in sergio_personality, etc.

6. **Duplicate Detection**
   - Checks for duplicate IDs across all collections
   - Ensures ID uniqueness in entire database
   - Reports all duplicates found

7. **Field Type Validation**
   - Validates metadata field types:
     - Strings: source, source_file, author, collection_type, category, language, if_citation_uri, confidence_level
     - Integer: source_line
     - Float: authenticity_score
     - Boolean: disputed
   - Reports type mismatches with examples

8. **Citation References**
   - Validates if_citation_uri format
   - Expected format: `if://citation/[id]-YYYY-MM-DD` or empty
   - Allows empty URIs during migration
   - Flags malformed URIs

### Rollback Triggers

Automatic rollback is triggered if ANY of these conditions occur:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Data Loss | >5% | Auto-trigger A28 rollback |
| Semantic Divergence | >20% | Auto-trigger A28 rollback |
| Count Mismatch | Any | Auto-trigger A28 rollback |
| Embedding Integrity | Invalid dimensions or NaN/Inf | Auto-trigger A28 rollback |
| Metadata Schema | Missing required fields | Auto-trigger A28 rollback |

## Installation

```bash
# Install dependencies
pip install chromadb

# (Optional) Install for semantic search comparison
pip install sentence-transformers
```

## Usage

### Basic Validation

```bash
python chromadb_migration_validator.py \
  --old-db-url http://85.239.243.227:8000 \
  --new-db-url http://localhost:8000
```

### With Semantic Search Testing

```bash
python chromadb_migration_validator.py \
  --old-db-url http://85.239.243.227:8000 \
  --new-db-url http://localhost:8000 \
  --test-queries sample_test_queries.json \
  --output validation_report.md
```

### Verbose Mode

```bash
python chromadb_migration_validator.py \
  --old-db-url http://85.239.243.227:8000 \
  --new-db-url http://localhost:8000 \
  --verbose
```

### Local ChromaDB Paths

```bash
python chromadb_migration_validator.py \
  --old-db-url /path/to/old/chromadb \
  --new-db-url /path/to/new/chromadb \
  --test-queries sample_test_queries.json
```

## Output

### Report Files

The validator generates two files:

1. **validation_report.md** - Human-readable Markdown report
2. **validation_report.json** - Machine-readable JSON report

### Markdown Report Structure

```
# ChromaDB Migration Validation Report

## Summary
- Overall Status (PASSED/WARNING/FAILED)
- Rollback Triggered (YES/NO)

## Test Results
- Table with all 8 tests
- Pass/Fail status per test
- Error/Warning counts

## Detailed Results
- Per-test breakdown with details
- Sample errors/warnings

## Metrics
- Data Loss %
- Semantic Divergence %

## Rollback Decision
- Rollback Triggered: YES/NO
- Reason (if triggered)
- Action Required
```

### JSON Report Structure

```json
{
  "timestamp": "2025-11-30T10:30:00",
  "old_db_url": "http://85.239.243.227:8000",
  "new_db_url": "http://localhost:8000",
  "test_results": [
    {
      "test_name": "Count Verification",
      "passed": true,
      "message": "...",
      "details": {...},
      "error_count": 0,
      "warning_count": 0
    }
  ],
  "overall_status": "PASSED",
  "total_tests": 8,
  "passed_tests": 8,
  "failed_tests": 0,
  "data_loss_percentage": 0.0,
  "semantic_divergence_percentage": 2.5,
  "rollback_triggered": false,
  "rollback_reason": ""
}
```

## Test Queries

Create custom test queries in JSON format:

```json
[
  {
    "text": "query text here",
    "collection": "sergio_personality",  // or null for all
    "category": "personality"
  }
]
```

Sample test queries provided in `sample_test_queries.json`:
- 8 collection-specific queries (2 per collection)
- 12 cross-collection queries for semantic consistency
- Total: 20 test queries covering all major topics

## Log Files

Logs are stored in `/home/setup/infrafabric/validation_logs/`:

- `validation_YYYYMMDD_HHMMSS.log` - Detailed validation log
- Includes all test execution details
- Useful for debugging validation issues

## Integration with A26 & A28

### Before A26 Migration

1. Backup old ChromaDB
2. Prepare new ChromaDB with updated schema
3. Get baseline statistics

### After A26 Migration

1. Run A27 validator
2. Generate validation report
3. If PASSED: Proceed to cutover
4. If FAILED: Auto-trigger A28 rollback

### A28 Rollback (if triggered)

1. Receive validation report
2. Check rollback_triggered = true
3. Execute rollback based on reason
4. Can re-run A26 with fixes
5. Re-validate with A27

## Example Validation Run

```bash
$ python chromadb_migration_validator.py \
    --old-db-url http://85.239.243.227:8000 \
    --new-db-url http://localhost:8000 \
    --test-queries sample_test_queries.json \
    --verbose

================================================================================
ChromaDB Migration Data Validation Suite
Old DB: http://85.239.243.227:8000
New DB: http://localhost:8000
================================================================================

[SETUP] Connecting to databases...
Connecting to http://85.239.243.227:8000...
  ✓ Connected to old DB
Connecting to http://localhost:8000...
  ✓ Connected to new DB

[SETUP] Loading data from both databases...
Loading data from old DB...
  Fetching sergio_personality...
    ✓ Fetched 23 chunks
  Fetching sergio_rhetorical...
    ✓ Fetched 5 chunks
  Fetching sergio_humor...
    ✓ Fetched 28 chunks
  Fetching sergio_corpus...
    ✓ Fetched 67 chunks
  Loaded 123 chunks from old DB
Loading data from new DB...
  Fetching sergio_personality...
    ✓ Fetched 23 chunks
  ...
  Loaded 123 chunks from new DB

[TESTS] Running validation tests...

[TEST 1] Count Verification...
  Old DB total: 9832
  New DB total: 9832
  Expected: 9832
  ✓ Counts match perfectly
  ✓ sergio_personality: 23 -> 23 (expected: 23)
  ✓ sergio_rhetorical: 5 -> 5 (expected: 5)
  ✓ sergio_humor: 28 -> 28 (expected: 28)
  ✓ sergio_corpus: 67 -> 67 (expected: 67)

[TEST 2] Embedding Integrity...
  Old DB: 9832 valid embeddings
  New DB: 9832 valid embeddings
  ✓ Dimensions match: 768
  ✓ No NaN/Inf values detected
  ✓ Vector statistics stable

[TEST 3] Metadata Completeness...
  Checked 9832 chunks
  ✓ 'source': present in all chunks
  ✓ 'source_file': present in all chunks
  ...
  ✓ All 12 fields present in all chunks

[TEST 4] Semantic Search Equivalence...
  ✓ Query 'Sergio's core values...': 2.1% divergence
  ✓ Query 'Big Five conscientiousness...': 5.3% divergence
  ...
  Average divergence: 3.8%

[TEST 5] Collection Distribution...
  ✓ All chunks correctly assigned to collections

[TEST 6] Duplicate Detection...
  Total chunks: 9832
  Unique IDs: 9832
  ✓ No duplicates found

[TEST 7] Field Type Validation...
  Validated 9832 chunks
  ✓ All field types valid

[TEST 8] Citation References...
  Total chunks: 9832
  Valid URIs: 8924
  Empty URIs: 908
  ✓ All citation URIs valid

================================================================================
VALIDATION SUMMARY
================================================================================
Total tests: 8
Passed: 8
Failed: 0
Elapsed time: 45.32s
Overall status: PASSED
Rollback triggered: NO
================================================================================

Report saved to: validation_report.md
JSON report saved to: validation_report.json
```

## Troubleshooting

### Connection Failed

```
Error: Failed to connect to databases
```

Check:
- ChromaDB servers are running
- URLs are correct (host:port)
- Network connectivity
- Firewall rules

### Data Loss Detected

```
Error: Count mismatch: 9800 vs 9832
```

Data loss >5% detected. Rollback triggered.

Check A26 migration logs for errors.

### Embedding Dimension Mismatch

```
Error: Dimension mismatch: [768] vs [1536]
```

Embeddings were generated with different models.

Options:
1. Re-generate embeddings with same model
2. Update validator expected dimensions
3. Trigger rollback and restart migration

### Semantic Divergence Too High

```
Warning: Average divergence: 23.5% > 20%
```

Query results significantly changed post-migration.

Possible causes:
- Embedding model changed
- Chunks reorganized
- Collection restructuring issue

Check semantic search implementation.

## Performance

Typical validation run times:

| Database Size | Estimated Time | Notes |
|---------------|----------------|-------|
| 100 chunks | 5-10s | Quick validation |
| 1,000 chunks | 30-60s | With semantic tests |
| 10,000 chunks | 3-5min | Full validation |
| 100,000 chunks | 20-30min | Large DB |

With --test-queries: Add 1-2 minutes per 10 queries

## Citation

```
if://design/chromadb-migration-validator-v1.0-2025-11-30
Agent: A27 (ChromaDB Migration Validator)
Mission: Data validation and integrity verification
Dependencies: A26 (Migration), A28 (Rollback)
```

## If.TTT Compliance

All validation results are traceable:

- ✓ Observable: JSON report with detailed metrics
- ✓ Traceable: Chunk-level error reporting
- ✓ Transparent: Full validation logs
- ✓ Trustworthy: Automated checks against schema

## Next Steps

After successful validation (rollback_triggered = false):

1. Proceed to cutover (update production pointer)
2. Run smoke tests in production
3. Monitor query performance
4. Archive old database (keep 30 days backup)
5. Document migration completion

If validation fails (rollback_triggered = true):

1. Review rollback_reason
2. Contact A26 for migration fixes
3. Restart migration from checkpoint
4. Re-validate with A27
5. Only proceed after PASSED status
