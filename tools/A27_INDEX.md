# A27 ChromaDB Migration Validator - Complete Index

**Mission:** Verify embedding integrity and metadata correctness post-migration
**Agent:** A27 (ChromaDB Migration Data Validation)
**Status:** DEPLOYED
**Date:** 2025-11-30

## Quick Navigation

### For First-Time Users
1. Start with: **QUICK_REFERENCE.txt** (2 min read)
2. Then read: **CHROMADB_VALIDATOR_README.md** (15 min read)
3. Run validator: `python chromadb_migration_validator.py --help`

### For Operators Running Validation
1. Read: **QUICK_REFERENCE.txt** (lookup commands)
2. Execute: `python chromadb_migration_validator.py ...`
3. Interpret: **validation_report.md** (generated output)

### For Integration with A26 & A28
1. Read: **MIGRATION_INTEGRATION_GUIDE.md** (complete workflow)
2. Understand: A26 → A27 → A28 pipeline
3. Handle: Rollback scenarios

## Core Files

**Validator Script:**
- `/home/setup/infrafabric/tools/chromadb_migration_validator.py` (46 KB)

**Test Data:**
- `/home/setup/infrafabric/tools/sample_test_queries.json` (20 queries)

**Documentation:**
- `CHROMADB_VALIDATOR_README.md` - Complete user guide
- `VALIDATION_TEST_SPEC.md` - Detailed test specifications
- `MIGRATION_INTEGRATION_GUIDE.md` - A26/A27/A28 workflow
- `QUICK_REFERENCE.txt` - Quick lookup guide
- `A27_VALIDATOR_DEPLOYMENT_SUMMARY.md` - Deployment overview
- `A27_INDEX.md` - This index

## 8 Validation Tests

1. Count Verification (chunk counts)
2. Embedding Integrity (dimensions, NaN/Inf)
3. Metadata Completeness (12 fields)
4. Semantic Search Equivalence (<20% divergence)
5. Collection Distribution (correct assignment)
6. Duplicate Detection (unique IDs)
7. Field Type Validation (schema compliance)
8. Citation References (URI format)

**Total Runtime: 25-35 minutes**

## Usage

Basic:
```bash
python chromadb_migration_validator.py \
  --old-db-url http://old:8000 \
  --new-db-url http://new:8000
```

Full:
```bash
python chromadb_migration_validator.py \
  --old-db-url http://old:8000 \
  --new-db-url http://new:8000 \
  --test-queries sample_test_queries.json
```

## Success Criteria

- overall_status = "PASSED"
- rollback_triggered = false
- data_loss = 0.0%
- semantic_divergence < 20%

## Citation

`if://design/chromadb-migration-validator-v1.0-2025-11-30`
