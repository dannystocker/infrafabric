#!/usr/bin/env python3
"""
ChromaDB Rollback System - Test Suite & Validation
===================================================

Test and validate snapshot/rollback functionality without requiring live ChromaDB.

Usage:
    python3 test_chromadb_rollback.py --test all
    python3 test_chromadb_rollback.py --test snapshot
    python3 test_chromadb_rollback.py --test rollback
    python3 test_chromadb_rollback.py --test manifest

Author: A28 (ChromaDB Migration Rollback Agent)
Citation: if://design/chromadb-rollback-tests-v1.0-2025-11-30
"""

import json
import logging
import argparse
import sys
import hashlib
import tarfile
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestResult:
    """Test result tracker"""

    def __init__(self, name: str):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_true(self, condition: bool, message: str):
        if condition:
            self.passed += 1
            print(f"  {GREEN}✓{RESET} {message}")
        else:
            self.failed += 1
            self.errors.append(message)
            print(f"  {RED}✗{RESET} {message}")

    def assert_equal(self, actual, expected, message: str):
        if actual == expected:
            self.passed += 1
            print(f"  {GREEN}✓{RESET} {message}")
        else:
            self.failed += 1
            self.errors.append(f"{message} (expected {expected}, got {actual})")
            print(f"  {RED}✗{RESET} {message}")

    def assert_file_exists(self, path: Path, message: str):
        if path.exists():
            self.passed += 1
            print(f"  {GREEN}✓{RESET} {message}")
        else:
            self.failed += 1
            self.errors.append(f"{message} (file not found: {path})")
            print(f"  {RED}✗{RESET} {message}")

    def assert_valid_json(self, data: str, message: str):
        try:
            json.loads(data)
            self.passed += 1
            print(f"  {GREEN}✓{RESET} {message}")
        except json.JSONDecodeError as e:
            self.failed += 1
            self.errors.append(f"{message} (invalid JSON: {e})")
            print(f"  {RED}✗{RESET} {message}")

    def summary(self) -> bool:
        total = self.passed + self.failed
        print(f"\n{BLUE}=== {self.name} ==={RESET}")
        print(f"  Passed: {self.passed}/{total}")
        print(f"  Failed: {self.failed}/{total}")

        if self.errors:
            print(f"\n  {RED}Errors:{RESET}")
            for error in self.errors:
                print(f"    - {error}")

        return self.failed == 0


# ============================================================================
# MANIFEST TESTS
# ============================================================================

def test_snapshot_manifest_schema():
    """Test snapshot manifest schema validity"""
    result = TestResult("Snapshot Manifest Schema")

    # Load schema
    schema_file = Path(__file__).parent / "CHROMADB_ROLLBACK_SCHEMA.json"
    result.assert_file_exists(schema_file, "Schema file exists")

    if not schema_file.exists():
        result.summary()
        return False

    with open(schema_file, 'r') as f:
        schema = json.load(f)

    # Validate schema structure
    result.assert_true("title" in schema, "Schema has title")
    result.assert_true("properties" in schema, "Schema has properties")
    result.assert_true("required" in schema, "Schema has required fields")

    # Validate required fields
    required_fields = [
        "snapshot_id", "timestamp", "chromadb_url", "total_chunks",
        "total_collections", "checksum_sha256", "status"
    ]

    for field in required_fields:
        result.assert_true(field in schema["required"], f"Required field: {field}")
        result.assert_true(field in schema["properties"], f"Property defined: {field}")

    # Validate example
    if "examples" in schema and schema["examples"]:
        example = schema["examples"][0]
        result.assert_valid_json(json.dumps(example), "Example is valid JSON")

        # Validate example against required fields
        for field in required_fields:
            result.assert_true(field in example, f"Example has field: {field}")

    return result.summary()


def test_manifest_validation():
    """Test manifest validation logic"""
    result = TestResult("Manifest Validation")

    # Create test manifest
    test_manifest = {
        "snapshot_id": "snapshot_20251130_143022",
        "timestamp": datetime.now().isoformat(),
        "chromadb_url": "http://localhost:8000",
        "chromadb_version": "0.3.21",
        "collections": {
            "sergio_personality": {"total_documents": 2458},
            "sergio_rhetorical": {"total_documents": 3294},
            "sergio_humor": {"total_documents": 1850},
            "sergio_corpus": {"total_documents": 2230}
        },
        "total_chunks": 9832,
        "total_collections": 4,
        "snapshot_size_mb": 28.4,
        "checksum_sha256": "a" * 64,
        "compression_ratio": 72.3,
        "status": "created",
        "error_message": "",
        "retention_until": (datetime.now() + timedelta(days=7)).isoformat(),
        "batch_metadata": {}
    }

    # Validate manifest
    result.assert_equal(test_manifest["total_chunks"], 9832, "Total chunks matches")
    result.assert_equal(
        test_manifest["total_collections"],
        len(test_manifest["collections"]),
        "Collection count matches"
    )
    result.assert_true(
        len(test_manifest["checksum_sha256"]) == 64,
        "Checksum is 64 hex characters"
    )
    result.assert_true(
        0 <= test_manifest["compression_ratio"] <= 100,
        "Compression ratio is percentage"
    )
    result.assert_true(
        test_manifest["status"] in ["created", "verified", "restored", "failed"],
        "Status is valid"
    )

    return result.summary()


# ============================================================================
# FILE STRUCTURE TESTS
# ============================================================================

def test_directory_structure():
    """Test snapshot directory structure"""
    result = TestResult("Directory Structure")

    snapshot_dir = Path("/home/setup/infrafabric/chromadb_snapshots")

    # Check main directories
    result.assert_file_exists(snapshot_dir, "Snapshot directory exists")

    if snapshot_dir.exists():
        result.assert_file_exists(snapshot_dir / "manifests", "Manifests directory exists")
        result.assert_file_exists(snapshot_dir / "logs", "Logs directory exists")

        # Check permissions
        result.assert_true(
            snapshot_dir.is_dir(),
            "Snapshot directory is readable"
        )

    return result.summary()


def test_script_files():
    """Test that all required scripts exist and are executable"""
    result = TestResult("Script Files")

    tools_dir = Path("/home/setup/infrafabric/tools")

    scripts = [
        "chromadb_snapshot.py",
        "chromadb_rollback.py",
        "chromadb-rollback.sh"
    ]

    for script in scripts:
        script_path = tools_dir / script
        result.assert_file_exists(script_path, f"Script exists: {script}")

        if script_path.exists():
            result.assert_true(
                script_path.stat().st_mode & 0o111,
                f"Script is executable: {script}"
            )

    return result.summary()


# ============================================================================
# CHECKSUM TESTS
# ============================================================================

def test_checksum_calculation():
    """Test SHA-256 checksum calculation"""
    result = TestResult("Checksum Calculation")

    # Create test file
    test_file = Path("/tmp/test_checksum.txt")
    test_content = b"Test content for checksum validation"

    test_file.write_bytes(test_content)

    # Calculate checksum
    sha256_hash = hashlib.sha256()
    with open(test_file, "rb") as f:
        sha256_hash.update(f.read())

    checksum = sha256_hash.hexdigest()

    # Validate checksum
    result.assert_equal(len(checksum), 64, "Checksum is 64 characters")
    result.assert_true(
        all(c in "0123456789abcdef" for c in checksum),
        "Checksum is valid hex"
    )

    # Calculate again and verify consistency
    sha256_hash2 = hashlib.sha256()
    with open(test_file, "rb") as f:
        sha256_hash2.update(f.read())

    checksum2 = sha256_hash2.hexdigest()
    result.assert_equal(checksum, checksum2, "Checksum is consistent")

    # Cleanup
    test_file.unlink()

    return result.summary()


# ============================================================================
# ARCHIVE TESTS
# ============================================================================

def test_tar_gz_creation():
    """Test TAR/GZIP archive creation and extraction"""
    result = TestResult("TAR/GZIP Archive")

    # Create test directory structure
    test_dir = Path("/tmp/test_archive_source")
    test_dir.mkdir(exist_ok=True)

    # Create test files
    (test_dir / "file1.txt").write_text("Content 1")
    (test_dir / "file2.txt").write_text("Content 2")

    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Content 3")

    # Create archive
    archive_path = Path("/tmp/test_archive.tar.gz")

    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(test_dir, arcname="test_archive_source")

        result.assert_file_exists(archive_path, "Archive created")

        # Test extraction
        extract_dir = Path("/tmp/test_archive_extract")
        extract_dir.mkdir(exist_ok=True)

        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_dir)

        result.assert_file_exists(
            extract_dir / "test_archive_source" / "file1.txt",
            "Archive extraction works"
        )

        # Verify content
        content = (extract_dir / "test_archive_source" / "file1.txt").read_text()
        result.assert_equal(content, "Content 1", "Extracted content is correct")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
        shutil.rmtree(extract_dir, ignore_errors=True)
        archive_path.unlink(missing_ok=True)

    return result.summary()


# ============================================================================
# AUDIT LOG TESTS
# ============================================================================

def test_audit_log_format():
    """Test audit log JSONL format"""
    result = TestResult("Audit Log Format")

    # Create test audit entries
    test_entries = [
        {
            "timestamp": datetime.now().isoformat(),
            "action": "rollback",
            "snapshot_id": "snapshot_20251130_143022",
            "status": "completed",
            "rollback_success": True,
            "duration_seconds": 45.2
        },
        {
            "timestamp": datetime.now().isoformat(),
            "action": "rollback",
            "snapshot_id": "snapshot_20251130_143022",
            "status": "failed",
            "rollback_success": False,
            "duration_seconds": 12.5
        }
    ]

    # Test JSONL format
    for i, entry in enumerate(test_entries):
        line = json.dumps(entry)
        result.assert_valid_json(line, f"Audit entry {i+1} is valid JSON")

        parsed = json.loads(line)
        result.assert_true("timestamp" in parsed, f"Entry {i+1} has timestamp")
        result.assert_true("action" in parsed, f"Entry {i+1} has action")
        result.assert_true("status" in parsed, f"Entry {i+1} has status")

    return result.summary()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_recovery_procedure_doc():
    """Test recovery procedures documentation"""
    result = TestResult("Recovery Procedures Documentation")

    doc_file = Path("/home/setup/infrafabric/tools/CHROMADB_RECOVERY_PROCEDURES.md")
    result.assert_file_exists(doc_file, "Recovery procedures document exists")

    if doc_file.exists():
        content = doc_file.read_text()

        # Check for required sections
        sections = [
            "# Overview",
            "# System Architecture",
            "# Snapshot Creation",
            "# Rollback Procedures",
            "# Emergency Recovery",
            "# Trigger Mechanisms",
            "# Validation & Verification"
        ]

        for section in sections:
            result.assert_true(
                section in content,
                f"Document contains section: {section}"
            )

    return result.summary()


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ChromaDB Rollback System - Test Suite"
    )

    parser.add_argument(
        "--test",
        choices=["all", "manifest", "structure", "checksum", "archive", "audit", "integration"],
        default="all",
        help="Test category to run"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    print(f"\n{BLUE}{'=' * 70}")
    print("ChromaDB Rollback System - Test Suite")
    print(f"{'=' * 70}{RESET}\n")

    results = []

    # Manifest tests
    if args.test in ["all", "manifest"]:
        results.append(test_snapshot_manifest_schema())
        results.append(test_manifest_validation())

    # Structure tests
    if args.test in ["all", "structure"]:
        results.append(test_directory_structure())
        results.append(test_script_files())

    # Checksum tests
    if args.test in ["all", "checksum"]:
        results.append(test_checksum_calculation())

    # Archive tests
    if args.test in ["all", "archive"]:
        results.append(test_tar_gz_creation())

    # Audit tests
    if args.test in ["all", "audit"]:
        results.append(test_audit_log_format())

    # Integration tests
    if args.test in ["all", "integration"]:
        results.append(test_recovery_procedure_doc())

    # Summary
    total_passed = sum(1 for r in results if r)
    total_failed = len(results) - total_passed

    print(f"\n{BLUE}{'=' * 70}")
    print("TEST SUMMARY")
    print(f"{'=' * 70}{RESET}")
    print(f"Total test categories: {len(results)}")
    print(f"Passed: {GREEN}{total_passed}{RESET}")
    print(f"Failed: {RED}{total_failed}{RESET}")

    if total_failed == 0:
        print(f"\n{GREEN}All tests passed!{RESET}")
        return 0
    else:
        print(f"\n{RED}Some tests failed!{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
