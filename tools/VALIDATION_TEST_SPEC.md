# ChromaDB Migration Validation - Test Specification

## Overview

Complete test specification for A27 validation suite covering 8 comprehensive tests plus semantic search comparison and statistical validation.

## Test Environment

**System Under Test:**
- Source: Old ChromaDB (may be HTTP or local)
- Target: New ChromaDB with updated schema
- Expected Data Size: 9,832 chunks across 4 collections

**Collections:**
- sergio_personality: 23 chunks
- sergio_rhetorical: 5 chunks
- sergio_humor: 28 chunks
- sergio_corpus: 67+ chunks

**Metadata Schema (12 fields):**
- Attribution: source, source_file, source_line, author
- Classification: collection_type, category, language
- Quality: authenticity_score, confidence_level, disputed, if_citation_uri
- Collection-specific fields vary

## Test Suite Specification

### TEST 1: Count Verification

**Purpose:** Ensure no data loss during migration

**Test Steps:**
1. Connect to old and new databases
2. List all collections in each database
3. Count total documents per collection
4. Count total documents across all collections

**Assertions:**
- Old total == New total (must be 100% match)
- Each collection count matches expected distribution
- Total should equal 9,832 chunks

**Failure Criteria:**
- Total count mismatch (any data loss)
- Per-collection count mismatch
- Missing expected collections

**Expected Output:**
```json
{
  "test_name": "Count Verification",
  "passed": true,
  "old_total": 9832,
  "new_total": 9832,
  "collections": {
    "sergio_personality": {
      "old": 23,
      "new": 23,
      "expected": 23,
      "match": true
    }
  }
}
```

**Data Loss Calculation:**
```
data_loss_percentage = (abs(old_total - new_total) / old_total) * 100
threshold: > 5% triggers rollback
```

---

### TEST 2: Embedding Integrity

**Purpose:** Verify embeddings transferred correctly without corruption

**Test Steps:**
1. Load all embeddings from both databases
2. Check embedding dimensions consistency
3. Scan for NaN and Infinity values
4. Calculate embedding statistics (mean, std)
5. Compare statistical properties

**Assertions:**
- All embeddings have consistent dimensions
- No NaN values present
- No Infinity values present
- Vector statistics remain stable (mean diff <0.01)
- Expected dimensions: 768, 1024, or 1536

**Failure Criteria:**
- Dimension mismatch between databases
- Any NaN or Inf values detected
- Unusual dimensions (not in expected list)
- Mean value significantly different (>0.01)

**Dimension Check Logic:**
```python
valid_dims = {768, 1024, 1536}
for embedding in all_embeddings:
    dim = len(embedding)
    if dim not in valid_dims:
        flag_warning(f"Unusual dimension: {dim}")
```

**NaN/Inf Detection:**
```python
for value in embedding:
    if math.isnan(value):
        error("NaN detected")
    if math.isinf(value):
        error("Inf detected")
```

**Expected Output:**
```json
{
  "test_name": "Embedding Integrity",
  "passed": true,
  "old_embeddings": {
    "valid_count": 9832,
    "invalid_count": 0,
    "nan_count": 0,
    "inf_count": 0,
    "dimensions": 768,
    "mean": 0.0234,
    "std": 0.891
  },
  "new_embeddings": {
    "valid_count": 9832,
    "invalid_count": 0,
    "nan_count": 0,
    "inf_count": 0,
    "dimensions": 768,
    "mean": 0.0236,
    "std": 0.893
  }
}
```

---

### TEST 3: Metadata Completeness

**Purpose:** Verify all 12 required metadata fields present in every chunk

**Test Steps:**
1. Iterate through all chunks in new database
2. For each chunk, check metadata field presence
3. For each required field, count missing occurrences
4. Report missing fields with chunk IDs

**Required Fields:**
1. source (string) - Migration source identifier
2. source_file (string) - Original file path
3. source_line (integer) - Line number in source
4. author (string) - Content author
5. collection_type (string) - One of: personality, rhetorical, humor, corpus
6. category (string) - Content category
7. language (string) - Language code (en, es, es_en)
8. authenticity_score (float) - 0.0-1.0
9. confidence_level (string) - low/medium/high
10. disputed (boolean) - Whether content is disputed
11. if_citation_uri (string) - Citation URI or empty

**Assertions:**
- All 12 fields present in 100% of chunks
- No null values in required fields
- Field count == 12 for each chunk

**Failure Criteria:**
- Any chunk missing required field
- Null values in required fields
- More than 5% missing any field

**Schema Validation:**
```python
required_fields = [
    "source", "source_file", "source_line", "author",
    "collection_type", "category", "language",
    "authenticity_score", "confidence_level", "disputed",
    "if_citation_uri"
]

for chunk in all_chunks:
    for field in required_fields:
        if field not in chunk.metadata:
            missing_count[field] += 1

# Check results
for field, count in missing_count.items():
    if count > 0:
        test_failed = True
```

**Expected Output:**
```json
{
  "test_name": "Metadata Completeness",
  "passed": true,
  "total_chunks_checked": 9832,
  "missing_fields": {
    "source": 0,
    "source_file": 0,
    "source_line": 0,
    "author": 0,
    "collection_type": 0,
    "category": 0,
    "language": 0,
    "authenticity_score": 0,
    "confidence_level": 0,
    "disputed": 0,
    "if_citation_uri": 0
  }
}
```

---

### TEST 4: Semantic Search Equivalence

**Purpose:** Verify search results remain consistent post-migration

**Test Steps:**
1. Load test queries from JSON file
2. For each query:
   a. Execute query on old database
   b. Execute query on new database
   c. Retrieve top-10 results from each
   d. Calculate result similarity
3. Compare result sets (IDs and distances)
4. Calculate average divergence

**Test Queries:**
20 queries covering:
- Collection-specific (8 queries, 2 per collection)
- Cross-collection (12 queries, various topics)

**Query Examples:**
```json
[
  {
    "text": "Sergio's core values ethical framework",
    "collection": "sergio_personality"
  },
  {
    "text": "Couples therapy family systems",
    "collection": null
  }
]
```

**Similarity Metrics:**

Jaccard Distance:
```
intersection = len(old_ids & new_ids)
union = len(old_ids | new_ids)
jaccard_sim = intersection / union
divergence = (1 - jaccard_sim) * 100
```

**Assertions:**
- Average divergence <10%: PASS
- Average divergence 10-20%: WARNING
- Average divergence >20%: FAIL (triggers rollback)
- Each query divergence <30%

**Failure Criteria:**
- Any query divergence >30%
- Average divergence >20%
- Unable to execute queries

**Expected Output:**
```json
{
  "test_name": "Semantic Search Equivalence",
  "passed": true,
  "queries_tested": 20,
  "average_divergence": 3.8,
  "max_divergence": 8.2,
  "divergence_scores": [2.1, 5.3, 4.2, ...],
  "per_query_results": [
    {
      "query": "core values",
      "divergence": 2.1,
      "old_results": [...],
      "new_results": [...]
    }
  ]
}
```

**Rollback Trigger:**
```
if average_divergence > 20%:
    rollback_triggered = True
    rollback_reason = f"Semantic divergence: {avg_div}% > 20%"
```

---

### TEST 5: Collection Distribution

**Purpose:** Verify chunks assigned to correct collections

**Test Steps:**
1. For each collection in new database:
   a. Load all chunks
   b. Check collection_type field
   c. Verify matches collection name
2. Ensure no cross-collection misassignments
3. Report distribution summary

**Collection Mapping:**
```
sergio_personality → collection_type = "personality"
sergio_rhetorical → collection_type = "rhetorical"
sergio_humor → collection_type = "humor"
sergio_corpus → collection_type = "corpus"
```

**Assertions:**
- All personality chunks in sergio_personality
- All rhetorical chunks in sergio_rhetorical
- All humor chunks in sergio_humor
- All corpus chunks in sergio_corpus
- No cross-collection misassignments

**Failure Criteria:**
- Any chunk in wrong collection
- Inconsistent collection_type field
- Missing collection_type field

**Expected Output:**
```json
{
  "test_name": "Collection Distribution",
  "passed": true,
  "distribution": {
    "sergio_personality": {
      "personality": 23,
      "rhetorical": 0,
      "humor": 0,
      "corpus": 0
    },
    "sergio_rhetorical": {
      "personality": 0,
      "rhetorical": 5,
      "humor": 0,
      "corpus": 0
    }
  }
}
```

---

### TEST 6: Duplicate Detection

**Purpose:** Ensure no duplicate chunk IDs

**Test Steps:**
1. Load all chunk IDs from new database
2. Check for duplicates using set comparison
3. Report all duplicate IDs found
4. Count unique vs. total

**Assertions:**
- unique_ids == total_chunks
- No duplicate IDs
- Set size == list size

**Failure Criteria:**
- Any duplicate IDs
- Unique count != total count

**Duplicate Check:**
```python
seen_ids = set()
duplicates = []

for chunk_id in all_ids:
    if chunk_id in seen_ids:
        duplicates.append(chunk_id)
    else:
        seen_ids.add(chunk_id)

if len(duplicates) > 0:
    test_failed = True
```

**Expected Output:**
```json
{
  "test_name": "Duplicate Detection",
  "passed": true,
  "total_chunks": 9832,
  "unique_ids": 9832,
  "duplicate_count": 0,
  "duplicates": []
}
```

---

### TEST 7: Field Type Validation

**Purpose:** Verify metadata field types match schema

**Test Steps:**
1. Load schema with expected types:
   - Strings: source, source_file, author, category, language, if_citation_uri, confidence_level, collection_type
   - Integer: source_line
   - Float: authenticity_score
   - Boolean: disputed
2. For each chunk, validate field types
3. Report type mismatches

**Type Mapping:**
```python
expected_types = {
    "source": str,
    "source_file": str,
    "source_line": int,
    "author": str,
    "collection_type": str,
    "category": str,
    "language": str,
    "authenticity_score": (int, float),
    "confidence_level": str,
    "disputed": bool,
    "if_citation_uri": str
}
```

**Assertions:**
- All fields match expected type
- No type coercion errors
- 0% type mismatches

**Failure Criteria:**
- Any field with wrong type
- >5% type mismatches
- Null values in typed fields

**Type Check:**
```python
for chunk in all_chunks:
    for field, expected_type in expected_types.items():
        value = chunk.metadata.get(field)
        if value is not None and not isinstance(value, expected_type):
            type_errors[field].append({
                "chunk_id": chunk["id"],
                "expected": expected_type,
                "actual": type(value)
            })
```

**Expected Output:**
```json
{
  "test_name": "Field Type Validation",
  "passed": true,
  "total_chunks": 9832,
  "type_errors": {}
}
```

---

### TEST 8: Citation References

**Purpose:** Validate if_citation_uri format

**Test Steps:**
1. Load all if_citation_uri values
2. Check format compliance
3. Count valid, empty, and invalid URIs
4. Report samples of invalid URIs

**URI Format:**
```
Valid: if://citation/[id]-YYYY-MM-DD
Valid: if://citation/[id]
Valid: (empty string)
Invalid: Other formats
```

**Regex Pattern:**
```
^if://citation/[a-zA-Z0-9\-]+(\-\d{4}\-\d{2}\-\d{2})?$
```

**Assertions:**
- URIs match if://citation/ format
- Dates are valid YYYY-MM-DD
- IDs are alphanumeric with hyphens

**Failure Criteria:**
- >10% invalid URI format
- Malformed dates
- Wrong URI scheme

**Validation:**
```python
import re

pattern = r"^if://citation/[a-zA-Z0-9\-]+(\-\d{4}\-\d{2}\-\d{2})?$"

for uri in all_uris:
    if not uri:  # Empty is valid during migration
        empty_count += 1
    elif re.match(pattern, uri):
        valid_count += 1
    else:
        invalid_count += 1
```

**Expected Output:**
```json
{
  "test_name": "Citation References",
  "passed": true,
  "total_chunks": 9832,
  "valid": 8924,
  "empty": 908,
  "invalid": 0
}
```

---

## Statistical Validation

### Embedding Vector Statistics

Calculated for all embeddings:

```json
{
  "vector_count": 9832,
  "dimensions": 768,
  "mean": 0.0234,
  "std_dev": 0.891,
  "min": -2.156,
  "max": 2.341,
  "sparsity": 0.234
}
```

### Metadata Field Distributions

Per collection:
```
language distribution:
  en: 45%
  es: 30%
  es_en: 25%

authenticity_score distribution:
  0.75-0.85: 20%
  0.85-0.95: 50%
  0.95-1.0: 30%

collection_type distribution:
  personality: 2.3%
  rhetorical: 0.5%
  humor: 2.8%
  corpus: 94.4%
```

### Performance Metrics

```json
{
  "total_execution_time_seconds": 45.3,
  "time_per_chunk_ms": 0.0046,
  "chunks_per_second": 217,
  "memory_usage_mb": 256
}
```

---

## Pass/Fail Criteria

### PASS Conditions

All of the following must be true:

1. Test 1: Count matches (0% data loss)
2. Test 2: Embedding integrity valid
3. Test 3: All 12 metadata fields present
4. Test 4: Average divergence <20%
5. Test 5: Correct collection distribution
6. Test 6: No duplicate IDs
7. Test 7: All field types valid
8. Test 8: Citation URIs valid

**Overall Status:** PASSED
**Rollback Triggered:** NO
**Action:** Proceed to cutover

### WARNING Conditions

Pass tests but with warnings:

- Test 4: Divergence 10-20%
- Test 8: <5% empty citation URIs
- Minor type validation warnings

**Overall Status:** WARNING
**Rollback Triggered:** NO
**Action:** Review warnings, proceed cautiously

### FAIL Conditions

Any of the following:

1. Data loss >5%
2. Embedding integrity issues
3. Missing metadata fields >5%
4. Semantic divergence >20%
5. Collection distribution errors
6. Duplicate IDs found
7. Type validation failures >5%
8. Invalid citation URIs >10%

**Overall Status:** FAILED
**Rollback Triggered:** YES
**Action:** Investigate and rollback migration

---

## Automated Rollback Triggers

Priority order:

| Priority | Condition | Threshold | Action |
|----------|-----------|-----------|--------|
| P0 | Data Loss | >5% | Rollback immediately |
| P0 | Test 1 (Count) | Any mismatch | Rollback immediately |
| P0 | Test 2 (Embeddings) | Invalid dims/NaN/Inf | Rollback immediately |
| P0 | Test 3 (Metadata) | Missing required fields | Rollback immediately |
| P1 | Test 4 (Semantic) | >20% divergence | Rollback |
| P2 | Test 6 (Duplicates) | Any duplicates | Investigate, may rollback |
| P3 | Test 7 (Types) | >5% mismatches | Review, may rollback |
| P4 | Test 8 (Citations) | >10% invalid | Review only |

---

## Example Test Run Output

```
=== ChromaDB Migration Validation ===

[TEST 1] Count Verification ... PASS
  Old: 9832 chunks
  New: 9832 chunks
  Data loss: 0%

[TEST 2] Embedding Integrity ... PASS
  Valid embeddings: 9832
  Dimension: 768
  NaN count: 0
  Inf count: 0

[TEST 3] Metadata Completeness ... PASS
  Chunks checked: 9832
  Missing fields: 0
  Required fields: 11/11

[TEST 4] Semantic Equivalence ... PASS
  Queries tested: 20
  Average divergence: 3.8%
  Max divergence: 8.2%

[TEST 5] Collection Distribution ... PASS
  Personality: 23/23
  Rhetorical: 5/5
  Humor: 28/28
  Corpus: 9776/9776

[TEST 6] Duplicate Detection ... PASS
  Unique IDs: 9832
  Duplicates: 0

[TEST 7] Field Type Validation ... PASS
  Type mismatches: 0
  Fields validated: 108152

[TEST 8] Citation References ... PASS
  Valid URIs: 8924
  Empty URIs: 908
  Invalid URIs: 0

=== SUMMARY ===
Tests passed: 8/8
Overall status: PASSED
Rollback triggered: NO

Migration can proceed to cutover.
```

---

## Test Execution Order

Tests are executed in sequence:

1. **Connectivity & Load** (prerequisite)
   - Connect to databases
   - Load all data

2. **Core Integrity Tests** (1-3)
   - Count verification (quick data loss check)
   - Embedding integrity (format validation)
   - Metadata completeness (schema validation)

3. **Data Quality Tests** (4-6)
   - Semantic equivalence (functional validation)
   - Collection distribution (organization validation)
   - Duplicate detection (uniqueness validation)

4. **Format & Reference Tests** (7-8)
   - Field type validation (schema strict check)
   - Citation references (metadata format check)

5. **Report Generation**
   - Calculate statistics
   - Check rollback conditions
   - Generate Markdown & JSON reports

---

## Test Execution Time Estimates

Based on 9,832 chunks with 768-dim embeddings:

| Phase | Estimated Time | Notes |
|-------|----------------|-------|
| Connection & Load | 2-3 min | Network dependent |
| Test 1 (Count) | <1 min | Simple aggregation |
| Test 2 (Embeddings) | 2-3 min | Vector analysis |
| Test 3 (Metadata) | 1-2 min | Field enumeration |
| Test 4 (Semantic) | 15-20 min | 20 queries × 2 DBs |
| Test 5 (Distribution) | 1-2 min | Classification check |
| Test 6 (Duplicates) | <1 min | Set operation |
| Test 7 (Types) | 1-2 min | Type checking |
| Test 8 (Citations) | <1 min | Regex matching |
| **Total** | **25-35 min** | Full validation |

---

## Success Metrics

Validation considered successful when:

| Metric | Target | Actual |
|--------|--------|--------|
| Data integrity | 100% | ≥99.5% |
| Embedding validity | 100% | 100% |
| Metadata completeness | 100% | 100% |
| Semantic consistency | <10% divergence | ✓ |
| Duplicate count | 0 | 0 |
| Type compliance | 100% | ≥99% |
| Citation format | 95%+ valid | ✓ |

When all metrics pass: **PROCEED TO CUTOVER**
When any metric fails: **TRIGGER ROLLBACK**
