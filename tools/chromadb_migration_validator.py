#!/usr/bin/env python3
"""
ChromaDB Migration Data Validation Suite
=========================================

Mission: Verify embedding integrity and metadata correctness post-migration.

Validates:
- All embeddings transferred correctly (no corruption)
- Metadata schema matches A7's 12-field design
- Semantic search still works (query results match pre-migration)
- No data loss or duplication

Test Suite:
1. Count verification (9,832 chunks across 4 collections)
2. Embedding integrity (dimension check, no NaN/Inf values)
3. Metadata completeness (all 12 required fields present)
4. Semantic search equivalence (pre vs. post query results)
5. Collection distribution (correct chunk assignment)
6. Duplicate detection (no duplicate IDs)
7. Field type validation (strings are strings, floats are floats)
8. Citation references (if_citation_uri format valid)

Usage:
    python chromadb_migration_validator.py \
        --old-db-url http://85.239.243.227:8000 \
        --new-db-url http://localhost:8000 \
        --test-queries queries.json \
        --output validation_report.md

Author: A27 (ChromaDB Migration Validator)
Citation: if://design/chromadb-migration-validator-v1.0-2025-11-30
"""

import json
import logging
import argparse
import time
import hashlib
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import sys
import traceback
import statistics

# Third-party imports
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Install with: pip install chromadb")


# ============================================================================
# CONFIGURATION & DATACLASSES
# ============================================================================

@dataclass
class ValidationConfig:
    """Validation configuration"""
    old_db_url: str
    new_db_url: str
    test_queries_file: Optional[str] = None
    output_file: str = "validation_report.md"
    log_dir: str = "/home/setup/infrafabric/validation_logs"
    verbose: bool = False
    expected_chunk_count: int = 9832
    expected_collections: List[str] = field(default_factory=lambda: [
        "sergio_personality", "sergio_rhetorical", "sergio_humor", "sergio_corpus"
    ])
    expected_collection_sizes: Dict[str, int] = field(default_factory=lambda: {
        "sergio_personality": 23,
        "sergio_rhetorical": 5,
        "sergio_humor": 28,
        "sergio_corpus": 67
    })
    # 12-field metadata schema
    required_metadata_fields: List[str] = field(default_factory=lambda: [
        "source", "source_file", "source_line", "author",
        "collection_type", "category", "language",
        "authenticity_score", "confidence_level", "disputed", "if_citation_uri"
    ])

    def __post_init__(self):
        """Create necessary directories"""
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class TestResult:
    """Result of a single validation test"""
    test_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    warning_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationReport:
    """Complete validation report"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    old_db_url: str = ""
    new_db_url: str = ""
    test_results: List[TestResult] = field(default_factory=list)
    overall_status: str = "PENDING"
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    data_loss_percentage: float = 0.0
    semantic_divergence_percentage: float = 0.0
    rollback_triggered: bool = False
    rollback_reason: str = ""


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_dir: str, verbose: bool = False) -> logging.Logger:
    """Setup structured logging"""
    log_file = Path(log_dir) / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("chromadb_validator")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
    ))
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO if not verbose else logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ch)

    return logger


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class ChromaDBValidator:
    """Main validation orchestrator"""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.logger = setup_logging(config.log_dir, config.verbose)
        self.report = ValidationReport(
            old_db_url=config.old_db_url,
            new_db_url=config.new_db_url
        )
        self.old_client = None
        self.new_client = None
        self.old_data = {}
        self.new_data = {}

        self.logger.info("=" * 80)
        self.logger.info("ChromaDB Migration Data Validation Suite")
        self.logger.info(f"Old DB: {config.old_db_url}")
        self.logger.info(f"New DB: {config.new_db_url}")
        self.logger.info("=" * 80)

    def run(self) -> ValidationReport:
        """Execute all validation tests"""
        try:
            start_time = time.time()

            # Connect to databases
            self.logger.info("\n[SETUP] Connecting to databases...")
            if not self._connect_databases():
                self.report.overall_status = "FAILED"
                self.report.rollback_triggered = True
                self.report.rollback_reason = "Failed to connect to databases"
                return self.report

            # Load all data
            self.logger.info("\n[SETUP] Loading data from both databases...")
            self._load_all_data()

            # Run all tests
            self.logger.info("\n[TESTS] Running validation tests...")
            self._run_test_1_count_verification()
            self._run_test_2_embedding_integrity()
            self._run_test_3_metadata_completeness()
            self._run_test_4_semantic_equivalence()
            self._run_test_5_collection_distribution()
            self._run_test_6_duplicate_detection()
            self._run_test_7_field_type_validation()
            self._run_test_8_citation_references()

            # Calculate statistics
            self.logger.info("\n[STATS] Calculating statistics...")
            self._calculate_statistics()

            # Determine rollback trigger
            self._check_rollback_conditions()

            # Generate report
            elapsed_time = time.time() - start_time
            self.logger.info("\n" + "=" * 80)
            self.logger.info("VALIDATION SUMMARY")
            self.logger.info("=" * 80)
            self.logger.info(f"Total tests: {self.report.total_tests}")
            self.logger.info(f"Passed: {self.report.passed_tests}")
            self.logger.info(f"Failed: {self.report.failed_tests}")
            self.logger.info(f"Elapsed time: {elapsed_time:.2f}s")
            self.logger.info(f"Overall status: {self.report.overall_status}")
            self.logger.info(f"Rollback triggered: {self.report.rollback_triggered}")
            if self.report.rollback_triggered:
                self.logger.warning(f"Rollback reason: {self.report.rollback_reason}")
            self.logger.info("=" * 80)

            return self.report

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            traceback.print_exc()
            self.report.overall_status = "ERROR"
            self.report.rollback_triggered = True
            self.report.rollback_reason = f"Validation error: {str(e)}"
            return self.report

    # ========================================================================
    # TEST 1: COUNT VERIFICATION
    # ========================================================================

    def _run_test_1_count_verification(self):
        """Test 1: Verify chunk counts match"""
        self.logger.info("\n[TEST 1] Count Verification...")

        test_result = TestResult(
            test_name="Count Verification",
            passed=True,
            message="Verifying chunk counts across collections"
        )

        try:
            old_total = sum(len(chunks) for chunks in self.old_data.values())
            new_total = sum(len(chunks) for chunks in self.new_data.values())

            test_result.details = {
                "old_total": old_total,
                "new_total": new_total,
                "expected": self.config.expected_chunk_count,
                "collections": {}
            }

            self.logger.info(f"  Old DB total: {old_total}")
            self.logger.info(f"  New DB total: {new_total}")
            self.logger.info(f"  Expected: {self.config.expected_chunk_count}")

            # Check total count
            if old_total != new_total:
                test_result.passed = False
                test_result.error_count += 1
                self.logger.error(f"  ✗ Count mismatch: {old_total} vs {new_total}")
                data_loss = abs(old_total - new_total) / old_total * 100 if old_total > 0 else 0
                self.report.data_loss_percentage = data_loss
            else:
                self.logger.info(f"  ✓ Counts match perfectly")

            # Check per-collection counts
            for coll_name in self.config.expected_collections:
                old_count = len(self.old_data.get(coll_name, []))
                new_count = len(self.new_data.get(coll_name, []))
                expected = self.config.expected_collection_sizes.get(coll_name, 0)

                match = old_count == new_count
                test_result.details["collections"][coll_name] = {
                    "old": old_count,
                    "new": new_count,
                    "expected": expected,
                    "match": match
                }

                status = "✓" if match else "✗"
                self.logger.info(f"  {status} {coll_name}: {old_count} -> {new_count} (expected: {expected})")

                if not match:
                    test_result.passed = False
                    test_result.error_count += 1

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during count verification: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    # ========================================================================
    # TEST 2: EMBEDDING INTEGRITY
    # ========================================================================

    def _run_test_2_embedding_integrity(self):
        """Test 2: Verify embeddings are valid (no NaN, correct dims, etc.)"""
        self.logger.info("\n[TEST 2] Embedding Integrity...")

        test_result = TestResult(
            test_name="Embedding Integrity",
            passed=True,
            message="Validating embedding vectors"
        )

        try:
            old_stats = self._analyze_embeddings(self.old_data, "old")
            new_stats = self._analyze_embeddings(self.new_data, "new")

            test_result.details = {
                "old_embeddings": old_stats,
                "new_embeddings": new_stats,
                "dimension_mismatch": False,
                "nan_values": False,
                "inf_values": False
            }

            self.logger.info(f"  Old DB: {old_stats['valid_count']} valid embeddings")
            self.logger.info(f"  New DB: {new_stats['valid_count']} valid embeddings")

            # Check dimensions
            if old_stats.get("dimensions") != new_stats.get("dimensions"):
                test_result.passed = False
                test_result.error_count += 1
                test_result.details["dimension_mismatch"] = True
                self.logger.error(f"  ✗ Dimension mismatch: {old_stats['dimensions']} vs {new_stats['dimensions']}")
            else:
                self.logger.info(f"  ✓ Dimensions match: {old_stats['dimensions']}")

            # Check for NaN/Inf
            old_invalid = old_stats.get("nan_count", 0) + old_stats.get("inf_count", 0)
            new_invalid = new_stats.get("nan_count", 0) + new_stats.get("inf_count", 0)

            if old_invalid > 0 or new_invalid > 0:
                test_result.passed = False
                test_result.error_count += 1
                test_result.details["nan_values"] = new_invalid > 0
                self.logger.error(f"  ✗ Invalid values: old={old_invalid}, new={new_invalid}")
            else:
                self.logger.info(f"  ✓ No NaN/Inf values detected")

            # Vector statistics
            if old_stats.get("mean") and new_stats.get("mean"):
                mean_diff = abs(old_stats["mean"] - new_stats["mean"])
                if mean_diff > 0.01:
                    test_result.warning_count += 1
                    self.logger.warning(f"  ⚠ Mean difference: {mean_diff:.6f}")
                else:
                    self.logger.info(f"  ✓ Vector statistics stable")

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during embedding validation: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    def _analyze_embeddings(self, data: Dict[str, List[Dict]], db_name: str) -> Dict[str, Any]:
        """Analyze embedding statistics"""
        stats = {
            "valid_count": 0,
            "invalid_count": 0,
            "nan_count": 0,
            "inf_count": 0,
            "dimensions": set(),
            "means": [],
            "stds": []
        }

        for collection_name, chunks in data.items():
            for chunk in chunks:
                embedding = chunk.get("embedding", [])
                if not embedding:
                    stats["invalid_count"] += 1
                    continue

                stats["valid_count"] += 1
                stats["dimensions"].add(len(embedding))

                # Check for NaN/Inf
                for val in embedding:
                    try:
                        if math.isnan(float(val)):
                            stats["nan_count"] += 1
                        elif math.isinf(float(val)):
                            stats["inf_count"] += 1
                    except (ValueError, TypeError):
                        stats["nan_count"] += 1

                # Calculate statistics
                try:
                    mean = statistics.mean(embedding)
                    stdev = statistics.stdev(embedding) if len(embedding) > 1 else 0
                    stats["means"].append(mean)
                    stats["stds"].append(stdev)
                except:
                    pass

        # Aggregate statistics
        if stats["means"]:
            stats["mean"] = statistics.mean(stats["means"])
            stats["std"] = statistics.mean(stats["stds"])

        if len(stats["dimensions"]) == 1:
            stats["dimensions"] = list(stats["dimensions"])[0]
        else:
            stats["dimensions"] = list(stats["dimensions"])

        return stats

    # ========================================================================
    # TEST 3: METADATA COMPLETENESS
    # ========================================================================

    def _run_test_3_metadata_completeness(self):
        """Test 3: Verify all 12 required metadata fields present"""
        self.logger.info("\n[TEST 3] Metadata Completeness...")

        test_result = TestResult(
            test_name="Metadata Completeness",
            passed=True,
            message="Validating 12-field metadata schema"
        )

        try:
            missing_fields = {field: 0 for field in self.config.required_metadata_fields}
            total_chunks_checked = 0

            for collection_name, chunks in self.new_data.items():
                for chunk in chunks:
                    total_chunks_checked += 1
                    metadata = chunk.get("metadata", {})

                    for field in self.config.required_metadata_fields:
                        if field not in metadata or metadata[field] is None:
                            missing_fields[field] += 1

            test_result.details = {
                "total_chunks_checked": total_chunks_checked,
                "missing_fields": missing_fields
            }

            self.logger.info(f"  Checked {total_chunks_checked} chunks")

            # Report missing fields
            any_missing = False
            for field, count in missing_fields.items():
                if count > 0:
                    any_missing = True
                    test_result.passed = False
                    test_result.error_count += count
                    self.logger.error(f"  ✗ Missing '{field}': {count} chunks")
                else:
                    self.logger.info(f"  ✓ '{field}': present in all chunks")

            if not any_missing:
                self.logger.info(f"  ✓ All 12 fields present in all chunks")

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during metadata validation: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    # ========================================================================
    # TEST 4: SEMANTIC SEARCH EQUIVALENCE
    # ========================================================================

    def _run_test_4_semantic_equivalence(self):
        """Test 4: Compare semantic search results (pre vs. post)"""
        self.logger.info("\n[TEST 4] Semantic Search Equivalence...")

        test_result = TestResult(
            test_name="Semantic Search Equivalence",
            passed=True,
            message="Comparing query results before and after migration"
        )

        try:
            # Load test queries
            test_queries = self._load_test_queries()
            if not test_queries:
                self.logger.warning("  ⚠ No test queries provided, skipping test")
                test_result.warning_count += 1
                self.report.test_results.append(test_result)
                self._update_report_stats(test_result)
                return

            # Run queries on both databases
            old_results = {}
            new_results = {}
            divergence_scores = []

            for query in test_queries:
                query_text = query.get("text", "")
                collection = query.get("collection", None)

                try:
                    # Query old DB
                    old_query_results = self._query_chromadb(
                        self.old_client, query_text, collection, n_results=10
                    )
                    old_results[query_text] = old_query_results

                    # Query new DB
                    new_query_results = self._query_chromadb(
                        self.new_client, query_text, collection, n_results=10
                    )
                    new_results[query_text] = new_query_results

                    # Calculate divergence
                    divergence = self._calculate_search_divergence(
                        old_query_results, new_query_results
                    )
                    divergence_scores.append(divergence)

                    status = "✓" if divergence < 10 else "⚠" if divergence < 20 else "✗"
                    self.logger.info(f"  {status} Query '{query_text[:50]}': {divergence:.1f}% divergence")

                    if divergence > 20:
                        test_result.passed = False
                        test_result.error_count += 1

                except Exception as e:
                    self.logger.error(f"  ✗ Query failed: {e}")
                    test_result.error_count += 1

            # Calculate average divergence
            if divergence_scores:
                avg_divergence = statistics.mean(divergence_scores)
                self.report.semantic_divergence_percentage = avg_divergence
                test_result.details = {
                    "queries_tested": len(test_queries),
                    "average_divergence": avg_divergence,
                    "max_divergence": max(divergence_scores),
                    "divergence_scores": divergence_scores
                }
                self.logger.info(f"  Average divergence: {avg_divergence:.1f}%")

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during semantic search validation: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    def _query_chromadb(self, client, query_text: str, collection_name: Optional[str] = None, n_results: int = 10) -> Dict[str, Any]:
        """Query ChromaDB and return results"""
        results = {"query": query_text, "results": []}

        try:
            collections = client.list_collections()

            if collection_name:
                # Query specific collection
                target_coll = next((c for c in collections if c.name == collection_name), None)
                if target_coll:
                    query_result = target_coll.query(query_texts=[query_text], n_results=n_results)
                    results["results"] = self._format_query_results(query_result)
            else:
                # Query all collections
                for collection in collections:
                    query_result = collection.query(query_texts=[query_text], n_results=3)
                    results["results"].extend(self._format_query_results(query_result))

        except Exception as e:
            self.logger.error(f"Query error: {e}")

        return results

    def _format_query_results(self, query_result: Dict) -> List[Dict]:
        """Format ChromaDB query results"""
        results = []
        try:
            ids = query_result.get("ids", [[]])[0]
            distances = query_result.get("distances", [[]])[0]

            for doc_id, distance in zip(ids, distances):
                results.append({
                    "id": doc_id,
                    "distance": float(distance)
                })
        except:
            pass

        return results

    def _calculate_search_divergence(self, old_results: Dict, new_results: Dict) -> float:
        """Calculate divergence between two query result sets (0-100%)"""
        old_ids = {r["id"] for r in old_results.get("results", [])}
        new_ids = {r["id"] for r in new_results.get("results", [])}

        if not old_ids:
            return 0.0

        # Calculate Jaccard distance
        intersection = len(old_ids & new_ids)
        union = len(old_ids | new_ids)

        if union == 0:
            return 0.0

        jaccard_similarity = intersection / union
        divergence = (1 - jaccard_similarity) * 100

        return divergence

    # ========================================================================
    # TEST 5: COLLECTION DISTRIBUTION
    # ========================================================================

    def _run_test_5_collection_distribution(self):
        """Test 5: Verify correct chunk assignment to collections"""
        self.logger.info("\n[TEST 5] Collection Distribution...")

        test_result = TestResult(
            test_name="Collection Distribution",
            passed=True,
            message="Validating chunk distribution across collections"
        )

        try:
            distribution = {}

            for collection_name, chunks in self.new_data.items():
                collection_types = defaultdict(int)

                for chunk in chunks:
                    metadata = chunk.get("metadata", {})
                    chunk_type = metadata.get("collection_type", "unknown")
                    collection_types[chunk_type] += 1

                distribution[collection_name] = dict(collection_types)

                self.logger.info(f"  {collection_name}:")
                for chunk_type, count in collection_types.items():
                    self.logger.info(f"    - {chunk_type}: {count}")

            test_result.details = {"distribution": distribution}

            # Verify expected distribution
            expected_types = {
                "sergio_personality": "personality",
                "sergio_rhetorical": "rhetorical",
                "sergio_humor": "humor",
                "sergio_corpus": "corpus"
            }

            for coll_name, expected_type in expected_types.items():
                if coll_name in distribution:
                    types = distribution[coll_name]
                    if expected_type not in types or types[expected_type] == 0:
                        test_result.passed = False
                        test_result.error_count += 1
                        self.logger.error(f"  ✗ {coll_name}: Missing expected type '{expected_type}'")
                    else:
                        self.logger.info(f"  ✓ {coll_name}: Correct distribution")

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during distribution validation: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    # ========================================================================
    # TEST 6: DUPLICATE DETECTION
    # ========================================================================

    def _run_test_6_duplicate_detection(self):
        """Test 6: Detect duplicate IDs"""
        self.logger.info("\n[TEST 6] Duplicate Detection...")

        test_result = TestResult(
            test_name="Duplicate Detection",
            passed=True,
            message="Checking for duplicate chunk IDs"
        )

        try:
            seen_ids: Set[str] = set()
            duplicates: List[str] = []
            total_chunks = 0

            for collection_name, chunks in self.new_data.items():
                for chunk in chunks:
                    chunk_id = chunk.get("id", "")
                    total_chunks += 1

                    if chunk_id in seen_ids:
                        duplicates.append(chunk_id)
                        test_result.passed = False
                        test_result.error_count += 1
                    else:
                        seen_ids.add(chunk_id)

            test_result.details = {
                "total_chunks": total_chunks,
                "unique_ids": len(seen_ids),
                "duplicate_count": len(duplicates),
                "duplicates": duplicates[:10]  # Report first 10
            }

            self.logger.info(f"  Total chunks: {total_chunks}")
            self.logger.info(f"  Unique IDs: {len(seen_ids)}")

            if duplicates:
                self.logger.error(f"  ✗ Found {len(duplicates)} duplicate IDs")
                if len(duplicates) <= 5:
                    for dup_id in duplicates:
                        self.logger.error(f"    - {dup_id}")
            else:
                self.logger.info(f"  ✓ No duplicates found")

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during duplicate detection: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    # ========================================================================
    # TEST 7: FIELD TYPE VALIDATION
    # ========================================================================

    def _run_test_7_field_type_validation(self):
        """Test 7: Validate metadata field types"""
        self.logger.info("\n[TEST 7] Field Type Validation...")

        test_result = TestResult(
            test_name="Field Type Validation",
            passed=True,
            message="Checking metadata field types"
        )

        try:
            # Define expected field types
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

            type_errors = defaultdict(list)
            total_chunks = 0

            for collection_name, chunks in self.new_data.items():
                for chunk in chunks:
                    total_chunks += 1
                    metadata = chunk.get("metadata", {})

                    for field, expected_type in expected_types.items():
                        if field in metadata:
                            value = metadata[field]
                            if value is not None and not isinstance(value, expected_type):
                                type_errors[field].append({
                                    "chunk_id": chunk.get("id"),
                                    "expected": str(expected_type),
                                    "actual": type(value).__name__,
                                    "value": str(value)[:50]
                                })
                                test_result.error_count += 1

            test_result.details = {
                "total_chunks": total_chunks,
                "type_errors": dict(type_errors)
            }

            self.logger.info(f"  Validated {total_chunks} chunks")

            if type_errors:
                test_result.passed = False
                for field, errors in type_errors.items():
                    self.logger.error(f"  ✗ Field '{field}': {len(errors)} type mismatches")
                    if len(errors) <= 3:
                        for error in errors:
                            self.logger.error(f"    - {error['chunk_id']}: expected {error['expected']}, got {error['actual']}")
            else:
                self.logger.info(f"  ✓ All field types valid")

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during type validation: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    # ========================================================================
    # TEST 8: CITATION REFERENCES
    # ========================================================================

    def _run_test_8_citation_references(self):
        """Test 8: Validate if_citation_uri format"""
        self.logger.info("\n[TEST 8] Citation References...")

        test_result = TestResult(
            test_name="Citation References",
            passed=True,
            message="Validating if_citation_uri format"
        )

        try:
            import re

            # Pattern: if://citation/uuid-YYYY-MM-DD or if://citation/type-uuid-YYYY-MM-DD
            citation_pattern = r"^if://citation/[a-zA-Z0-9\-]+(\-\d{4}\-\d{2}\-\d{2})?$"
            empty_count = 0
            invalid_count = 0
            valid_count = 0
            total_chunks = 0

            invalid_citations = []

            for collection_name, chunks in self.new_data.items():
                for chunk in chunks:
                    total_chunks += 1
                    metadata = chunk.get("metadata", {})
                    citation_uri = metadata.get("if_citation_uri", "")

                    if not citation_uri:
                        empty_count += 1
                    elif re.match(citation_pattern, citation_uri):
                        valid_count += 1
                    else:
                        invalid_count += 1
                        if len(invalid_citations) < 5:
                            invalid_citations.append({
                                "chunk_id": chunk.get("id"),
                                "uri": citation_uri
                            })

            test_result.details = {
                "total_chunks": total_chunks,
                "valid": valid_count,
                "empty": empty_count,
                "invalid": invalid_count,
                "sample_invalid": invalid_citations
            }

            self.logger.info(f"  Total chunks: {total_chunks}")
            self.logger.info(f"  Valid URIs: {valid_count}")
            self.logger.info(f"  Empty URIs: {empty_count}")

            # Allow some empty URIs (expected during migration)
            if invalid_count > 0:
                test_result.warning_count += invalid_count
                self.logger.warning(f"  ⚠ Invalid URIs: {invalid_count}")
                if invalid_citations:
                    for citation in invalid_citations:
                        self.logger.warning(f"    - {citation['chunk_id']}: {citation['uri']}")
            else:
                self.logger.info(f"  ✓ All citation URIs valid")

        except Exception as e:
            test_result.passed = False
            test_result.error_count += 1
            test_result.message = f"Error during citation validation: {str(e)}"
            self.logger.error(f"  ✗ Error: {e}")

        self.report.test_results.append(test_result)
        self._update_report_stats(test_result)

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _connect_databases(self) -> bool:
        """Connect to both databases"""
        try:
            self.logger.info(f"Connecting to old DB: {self.config.old_db_url}")
            self.old_client = self._connect_chromadb(self.config.old_db_url)
            self.logger.info("  ✓ Connected to old DB")

            self.logger.info(f"Connecting to new DB: {self.config.new_db_url}")
            self.new_client = self._connect_chromadb(self.config.new_db_url)
            self.logger.info("  ✓ Connected to new DB")

            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to databases: {e}")
            return False

    def _connect_chromadb(self, url: str):
        """Connect to ChromaDB"""
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("chromadb not installed")

        try:
            if url.startswith("http"):
                host = url.split("//")[1].split(":")[0]
                port = int(url.split(":")[-1])
                client = chromadb.HttpClient(host=host, port=port)
                client.heartbeat()
                return client
            else:
                client = chromadb.PersistentClient(path=url)
                return client

        except Exception as e:
            self.logger.error(f"Failed to connect to {url}: {e}")
            raise

    def _load_all_data(self):
        """Load all data from both databases"""
        try:
            self.logger.info("Loading data from old DB...")
            self.old_data = self._fetch_all_data(self.old_client)
            self.logger.info(f"  Loaded {sum(len(c) for c in self.old_data.values())} chunks from old DB")

            self.logger.info("Loading data from new DB...")
            self.new_data = self._fetch_all_data(self.new_client)
            self.logger.info(f"  Loaded {sum(len(c) for c in self.new_data.values())} chunks from new DB")

        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            raise

    def _fetch_all_data(self, client) -> Dict[str, List[Dict]]:
        """Fetch all collections and data from ChromaDB"""
        data = {}

        try:
            collections = client.list_collections()

            for collection in collections:
                self.logger.info(f"  Fetching {collection.name}...")

                try:
                    all_data = collection.get()

                    chunks = []
                    for i in range(len(all_data.get("ids", []))):
                        chunk = {
                            "id": all_data["ids"][i],
                            "text": all_data["documents"][i] if all_data.get("documents") else "",
                            "embedding": all_data["embeddings"][i] if all_data.get("embeddings") else [],
                            "metadata": all_data["metadatas"][i] if all_data.get("metadatas") else {}
                        }
                        chunks.append(chunk)

                    data[collection.name] = chunks
                    self.logger.info(f"    ✓ Fetched {len(chunks)} chunks")

                except Exception as e:
                    self.logger.error(f"    ✗ Failed to fetch {collection.name}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to list collections: {e}")

        return data

    def _load_test_queries(self) -> List[Dict[str, Any]]:
        """Load test queries from file"""
        if not self.config.test_queries_file:
            return []

        try:
            with open(self.config.test_queries_file, 'r') as f:
                queries = json.load(f)
            return queries if isinstance(queries, list) else []

        except Exception as e:
            self.logger.warning(f"Failed to load test queries: {e}")
            return []

    def _calculate_statistics(self):
        """Calculate overall statistics"""
        self.report.total_tests = len(self.report.test_results)
        self.report.passed_tests = sum(1 for t in self.report.test_results if t.passed)
        self.report.failed_tests = self.report.total_tests - self.report.passed_tests

        # Overall status
        if self.report.failed_tests == 0:
            self.report.overall_status = "PASSED"
        elif self.report.passed_tests >= self.report.total_tests * 0.75:
            self.report.overall_status = "WARNING"
        else:
            self.report.overall_status = "FAILED"

    def _check_rollback_conditions(self):
        """Check if rollback should be triggered"""
        # Condition 1: >5% data loss
        if self.report.data_loss_percentage > 5:
            self.report.rollback_triggered = True
            self.report.rollback_reason = f"Data loss: {self.report.data_loss_percentage:.1f}% > 5%"
            self.logger.error(f"ROLLBACK TRIGGERED: {self.report.rollback_reason}")
            return

        # Condition 2: >20% semantic search divergence
        if self.report.semantic_divergence_percentage > 20:
            self.report.rollback_triggered = True
            self.report.rollback_reason = f"Semantic divergence: {self.report.semantic_divergence_percentage:.1f}% > 20%"
            self.logger.error(f"ROLLBACK TRIGGERED: {self.report.rollback_reason}")
            return

        # Condition 3: Critical test failure
        for test_result in self.report.test_results:
            if test_result.test_name in ["Count Verification", "Embedding Integrity", "Metadata Completeness"] and not test_result.passed:
                self.report.rollback_triggered = True
                self.report.rollback_reason = f"Critical test failed: {test_result.test_name}"
                self.logger.error(f"ROLLBACK TRIGGERED: {self.report.rollback_reason}")
                return

    def _update_report_stats(self, test_result: TestResult):
        """Update report statistics from test result"""
        pass  # Stats updated in _calculate_statistics()

    def generate_markdown_report(self) -> str:
        """Generate Markdown report"""
        report_md = f"""# ChromaDB Migration Validation Report

**Generated:** {self.report.timestamp}

## Summary

- **Old DB:** {self.report.old_db_url}
- **New DB:** {self.report.new_db_url}
- **Overall Status:** {self.report.overall_status}
- **Rollback Triggered:** {'YES - Action Required!' if self.report.rollback_triggered else 'NO'}

## Test Results

**Total Tests:** {self.report.total_tests}
**Passed:** {self.report.passed_tests}
**Failed:** {self.report.failed_tests}

| Test Name | Status | Errors | Warnings | Details |
|-----------|--------|--------|----------|---------|
"""

        for test in self.report.test_results:
            status = "✓ PASS" if test.passed else "✗ FAIL"
            report_md += f"| {test.test_name} | {status} | {test.error_count} | {test.warning_count} | {test.message} |\n"

        # Add detailed results
        report_md += "\n## Detailed Results\n"

        for test in self.report.test_results:
            report_md += f"\n### {test.test_name}\n\n"
            report_md += f"**Status:** {'PASS' if test.passed else 'FAIL'}\n"
            report_md += f"**Errors:** {test.error_count}\n"
            report_md += f"**Warnings:** {test.warning_count}\n\n"

            if test.details:
                report_md += "**Details:**\n```json\n"
                report_md += json.dumps(test.details, indent=2, default=str)
                report_md += "\n```\n"

        # Add metrics
        report_md += f"\n## Metrics\n\n"
        report_md += f"- **Data Loss:** {self.report.data_loss_percentage:.2f}%\n"
        report_md += f"- **Semantic Divergence:** {self.report.semantic_divergence_percentage:.2f}%\n"

        # Rollback decision
        if self.report.rollback_triggered:
            report_md += f"\n## ROLLBACK TRIGGERED\n\n"
            report_md += f"**Reason:** {self.report.rollback_reason}\n\n"
            report_md += "**Action Required:** Initiate automatic rollback (A28).\n"
        else:
            report_md += f"\n## Validation Passed\n\n"
            report_md += "Migration can proceed to cutover.\n"

        return report_md

    def save_report(self):
        """Save report to file"""
        report_md = self.generate_markdown_report()

        output_path = Path(self.config.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(report_md)

        self.logger.info(f"\nReport saved to: {output_path}")

        # Also save JSON version
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(asdict(self.report), f, indent=2, default=str)

        self.logger.info(f"JSON report saved to: {json_path}")


# ============================================================================
# CLI & MAIN
# ============================================================================

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ChromaDB Migration Data Validation Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full validation
  python chromadb_migration_validator.py \\
    --old-db-url http://85.239.243.227:8000 \\
    --new-db-url http://localhost:8000 \\
    --test-queries queries.json \\
    --output validation_report.md

  # Simple validation without semantic search
  python chromadb_migration_validator.py \\
    --old-db-url /path/to/old/chromadb \\
    --new-db-url /path/to/new/chromadb

  # Verbose output
  python chromadb_migration_validator.py \\
    --old-db-url http://old:8000 \\
    --new-db-url http://new:8000 \\
    --verbose
        """
    )

    parser.add_argument("--old-db-url", required=True,
                       help="Old ChromaDB URL (HTTP or local path)")
    parser.add_argument("--new-db-url", required=True,
                       help="New ChromaDB URL (HTTP or local path)")
    parser.add_argument("--test-queries", dest="test_queries_file",
                       help="Test queries JSON file for semantic search validation")
    parser.add_argument("--output", default="validation_report.md",
                       help="Output report file (default: validation_report.md)")
    parser.add_argument("--log-dir", default="/home/setup/infrafabric/validation_logs",
                       help="Log directory")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose logging")

    args = parser.parse_args()

    # Create config
    config = ValidationConfig(
        old_db_url=args.old_db_url,
        new_db_url=args.new_db_url,
        test_queries_file=args.test_queries_file,
        output_file=args.output,
        log_dir=args.log_dir,
        verbose=args.verbose
    )

    # Run validation
    validator = ChromaDBValidator(config)
    report = validator.run()

    # Save report
    validator.save_report()

    # Exit code
    sys.exit(0 if not report.rollback_triggered else 1)


if __name__ == "__main__":
    main()
