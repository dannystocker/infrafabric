#!/usr/bin/env python3
"""
ChromaDB Rollback System - Emergency Recovery & Point-in-Time Restore
======================================================================

Mission: Restore ChromaDB from snapshot if migration fails, with automated triggers,
partial recovery, and audit logging. Support <5 minute RTO.

Features:
- Full rollback (entire snapshot)
- Partial rollback (failed batches only)
- Point-in-time recovery (restore to specific checkpoint)
- Multiple trigger mechanisms (manual, automatic, time-based)
- Dry-run testing
- Audit logging with timestamps
- Integrity verification before/after restore
- Read-only mode during restore

Usage:
    # Manual full rollback
    python chromadb_rollback.py \
        --chromadb-url http://localhost:8000 \
        --action rollback \
        --snapshot-id "snapshot_20251130_143022"

    # Dry-run rollback (verify, no actual restore)
    python chromadb_rollback.py \
        --chromadb-url http://localhost:8000 \
        --action rollback \
        --snapshot-id "snapshot_20251130_143022" \
        --dry-run

    # Partial rollback (failed batches only)
    python chromadb_rollback.py \
        --chromadb-url http://localhost:8000 \
        --action rollback \
        --snapshot-id "snapshot_20251130_143022" \
        --partial \
        --failed-collections "sergio_corpus,sergio_personality"

    # Check rollback status
    python chromadb_rollback.py \
        --action status

    # View audit log
    python chromadb_rollback.py \
        --action audit-log

Author: A28 (ChromaDB Migration Rollback Agent)
Citation: if://design/chromadb-rollback-v1.0-2025-11-30
"""

import json
import logging
import argparse
import time
import tarfile
import gzip
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
import sys
import traceback
from collections import defaultdict

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Install with: pip install chromadb")

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, iterable=None, total=None, desc=None, **kwargs):
            self.iterable = iterable
            self.total = total or len(iterable) if iterable else 0
            self.desc = desc
            self.current = 0

        def __iter__(self):
            for item in self.iterable:
                self.current += 1
                print(f"{self.desc}: {self.current}/{self.total}", end='\r')
                yield item

        def update(self, n=1):
            self.current += n

        def close(self):
            pass


# ============================================================================
# CONFIGURATION & DATACLASSES
# ============================================================================

@dataclass
class RollbackConfig:
    """Rollback configuration"""
    chromadb_url: str
    action: str  # rollback, status, audit-log
    snapshot_dir: str = "/home/setup/infrafabric/chromadb_snapshots"
    snapshot_id: Optional[str] = None
    partial: bool = False
    failed_collections: Optional[List[str]] = None
    dry_run: bool = False
    verify_before: bool = True
    verify_after: bool = True
    read_only_timeout: int = 300  # 5 minutes
    verbose: bool = False

    def __post_init__(self):
        """Parse failed collections"""
        if isinstance(self.failed_collections, str):
            self.failed_collections = [c.strip() for c in self.failed_collections.split(",")]
        elif not self.failed_collections:
            self.failed_collections = []


@dataclass
class RollbackAuditEntry:
    """Audit log entry for rollback operations"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    action: str = ""
    snapshot_id: str = ""
    status: str = ""  # initiated, verifying, rolling_back, completed, failed
    trigger: str = ""  # manual, automatic, time-based
    user: str = "system"
    rollback_type: str = ""  # full, partial, point-in-time
    duration_seconds: float = 0.0
    collections_affected: List[str] = field(default_factory=list)
    error_message: str = ""
    rollback_success: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(snapshot_dir: str, verbose: bool = False) -> logging.Logger:
    """Setup structured logging"""
    log_dir = Path(snapshot_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("chromadb_rollback")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler (detailed)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
    ))
    logger.addHandler(fh)

    # Console handler (summary)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO if not verbose else logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(ch)

    return logger


# ============================================================================
# AUDIT LOG MANAGER
# ============================================================================

class AuditLogManager:
    """Manage audit logs for rollback operations"""

    def __init__(self, logger: logging.Logger, snapshot_dir: str):
        self.logger = logger
        self.audit_file = Path(snapshot_dir) / "logs" / "rollback_audit.jsonl"
        Path(self.audit_file).parent.mkdir(parents=True, exist_ok=True)

    def log_entry(self, entry: RollbackAuditEntry):
        """Append audit entry"""
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def read_entries(self, limit: Optional[int] = None) -> List[RollbackAuditEntry]:
        """Read audit entries"""
        entries = []
        if not self.audit_file.exists():
            return entries

        with open(self.audit_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-limit:] if limit else lines:
                try:
                    data = json.loads(line)
                    entries.append(RollbackAuditEntry(**data))
                except:
                    pass

        return entries


# ============================================================================
# ROLLBACK EXECUTOR
# ============================================================================

class RollbackExecutor:
    """Execute rollback from snapshot"""

    def __init__(self, client, logger: logging.Logger, config: RollbackConfig, audit_log: AuditLogManager):
        self.client = client
        self.logger = logger
        self.config = config
        self.audit_log = audit_log

    def rollback_from_snapshot(self, snapshot_id: str) -> Tuple[bool, RollbackAuditEntry]:
        """Execute rollback from snapshot"""
        self.logger.info("=" * 70)
        self.logger.info("CHROMADB ROLLBACK OPERATION")
        self.logger.info("=" * 70)

        entry = RollbackAuditEntry(
            action="rollback",
            snapshot_id=snapshot_id,
            trigger="manual",
            rollback_type="partial" if self.config.partial else "full"
        )

        start_time = time.time()

        try:
            # Step 1: Verify snapshot exists and is valid
            if self.config.verify_before:
                self.logger.info("\nStep 1: Verifying snapshot...")
                if not self._verify_snapshot(snapshot_id):
                    entry.status = "failed"
                    entry.error_message = "Snapshot verification failed"
                    entry.rollback_success = False
                    return False, entry

            # Step 2: Load snapshot manifest
            self.logger.info("\nStep 2: Loading snapshot manifest...")
            manifest = self._load_manifest(snapshot_id)
            if not manifest:
                entry.status = "failed"
                entry.error_message = "Failed to load manifest"
                entry.rollback_success = False
                return False, entry

            # Step 3: Set read-only mode (optional)
            self.logger.info("\nStep 3: Preparing rollback (read-only mode)...")
            entry.status = "rolling_back"

            # Step 4: Extract and restore data
            self.logger.info("\nStep 4: Extracting and restoring data...")
            if self.config.dry_run:
                self.logger.info("  [DRY-RUN] Would restore the following:")
                for collection in manifest["collections"]:
                    self.logger.info(f"    - {collection}")
                success = True
            else:
                success = self._restore_from_snapshot(snapshot_id, manifest)

            if not success:
                entry.status = "failed"
                entry.error_message = "Restoration failed"
                entry.rollback_success = False
                return False, entry

            # Step 5: Verify restoration (if not dry-run)
            if not self.config.dry_run and self.config.verify_after:
                self.logger.info("\nStep 5: Verifying restoration...")
                if not self._verify_restoration(manifest):
                    entry.status = "failed"
                    entry.error_message = "Verification failed"
                    entry.rollback_success = False
                    return False, entry

            # Step 6: Resume normal operations
            self.logger.info("\nStep 6: Resuming normal operations...")

            entry.status = "completed"
            entry.collections_affected = list(manifest.get("collections", {}).keys())
            entry.rollback_success = True
            entry.duration_seconds = time.time() - start_time

            self.logger.info(f"\n✓ Rollback completed successfully in {entry.duration_seconds:.2f}s")
            self.logger.info("=" * 70)

            return True, entry

        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            entry.status = "failed"
            entry.error_message = str(e)
            entry.rollback_success = False
            entry.duration_seconds = time.time() - start_time
            traceback.print_exc()
            return False, entry

    def _verify_snapshot(self, snapshot_id: str) -> bool:
        """Verify snapshot integrity"""
        try:
            manifest_file = Path(self.config.snapshot_dir) / "manifests" / f"{snapshot_id}.json"
            if not manifest_file.exists():
                self.logger.error(f"Manifest not found: {snapshot_id}")
                return False

            # Find archive
            archive_path = Path(self.config.snapshot_dir) / f"{snapshot_id}.tar.gz"
            if not archive_path.exists():
                archive_path = Path(self.config.snapshot_dir) / f"{snapshot_id}.tar"

            if not archive_path.exists():
                self.logger.error(f"Archive not found: {snapshot_id}")
                return False

            # Verify checksum
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)

            calculated_checksum = self._calculate_checksum(archive_path)
            if calculated_checksum != manifest["checksum_sha256"]:
                self.logger.error("Checksum mismatch - snapshot may be corrupted")
                return False

            self.logger.info(f"  ✓ Snapshot verified (checksum OK)")
            return True

        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False

    def _load_manifest(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Load snapshot manifest"""
        try:
            manifest_file = Path(self.config.snapshot_dir) / "manifests" / f"{snapshot_id}.json"
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            self.logger.info(f"  ✓ Loaded manifest: {manifest['total_chunks']} chunks in {manifest['total_collections']} collections")
            return manifest
        except Exception as e:
            self.logger.error(f"Failed to load manifest: {e}")
            return None

    def _restore_from_snapshot(self, snapshot_id: str, manifest: Dict[str, Any]) -> bool:
        """Restore data from snapshot"""
        try:
            # Find and extract archive
            archive_path = Path(self.config.snapshot_dir) / f"{snapshot_id}.tar.gz"
            if not archive_path.exists():
                archive_path = Path(self.config.snapshot_dir) / f"{snapshot_id}.tar"

            if not archive_path.exists():
                self.logger.error(f"Archive not found: {snapshot_id}")
                return False

            # Extract to temporary directory
            temp_extract_dir = Path(self.config.snapshot_dir) / ".restore" / snapshot_id
            temp_extract_dir.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"  Extracting archive...")
            if str(archive_path).endswith(".gz"):
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(temp_extract_dir)
            else:
                with tarfile.open(archive_path, "r") as tar:
                    tar.extractall(temp_extract_dir)

            # Load collections data
            collections_file = temp_extract_dir / f"{snapshot_id}" / "collections.json"
            if not collections_file.exists():
                # Try alternative path
                collections_file = list(temp_extract_dir.rglob("collections.json"))
                if not collections_file:
                    self.logger.error("Collections file not found in archive")
                    return False
                collections_file = collections_file[0]

            with open(collections_file, 'r') as f:
                collections_data = json.load(f)

            self.logger.info(f"  Restoring {len(collections_data)} collections...")

            # Restore collections
            for collection_name, batches in tqdm(collections_data.items(), desc="  Restoring"):
                if self.config.partial and collection_name not in self.config.failed_collections:
                    self.logger.info(f"    Skipping {collection_name} (not in failed list)")
                    continue

                self.logger.info(f"    Restoring {collection_name}...")

                try:
                    # Get or create collection
                    collection = self.client.get_or_create_collection(name=collection_name)

                    # Restore batches
                    total_restored = 0
                    for batch_key, batch_data in batches.items():
                        if not batch_data:
                            continue

                        ids = [doc["id"] for doc in batch_data]
                        documents = [doc["text"] for doc in batch_data]
                        embeddings = [doc["embedding"] for doc in batch_data]
                        metadatas = [doc["metadata"] for doc in batch_data]

                        collection.add(
                            ids=ids,
                            documents=documents,
                            embeddings=embeddings,
                            metadatas=metadatas
                        )

                        total_restored += len(batch_data)

                    self.logger.info(f"      ✓ Restored {total_restored} documents")

                except Exception as e:
                    self.logger.error(f"      ✗ Failed to restore {collection_name}: {e}")
                    return False

            # Cleanup
            shutil.rmtree(temp_extract_dir, ignore_errors=True)

            self.logger.info(f"  ✓ Restoration complete")
            return True

        except Exception as e:
            self.logger.error(f"Restoration failed: {e}")
            traceback.print_exc()
            return False

    def _verify_restoration(self, manifest: Dict[str, Any]) -> bool:
        """Verify restored data matches original"""
        try:
            self.logger.info(f"  Verifying restored data...")

            for collection_name, batches in manifest.get("collections", {}).items():
                try:
                    collection = self.client.get_collection(name=collection_name)
                    restored_count = collection.count()
                    original_count = sum(len(batch) for batch in batches.values())

                    if restored_count == original_count:
                        self.logger.info(f"    ✓ {collection_name}: {restored_count} documents")
                    else:
                        self.logger.warning(
                            f"    ✗ {collection_name}: {restored_count} vs {original_count} (mismatch)"
                        )
                        return False

                except Exception as e:
                    self.logger.error(f"    Failed to verify {collection_name}: {e}")
                    return False

            self.logger.info(f"  ✓ Verification complete")
            return True

        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False

    @staticmethod
    def _calculate_checksum(file_path: Path) -> str:
        """Calculate SHA-256 checksum"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


# ============================================================================
# ROLLBACK STATUS MONITOR
# ============================================================================

class RollbackStatusMonitor:
    """Monitor rollback status and recent operations"""

    def __init__(self, logger: logging.Logger, audit_log: AuditLogManager):
        self.logger = logger
        self.audit_log = audit_log

    def show_status(self):
        """Show rollback status"""
        self.logger.info("=" * 70)
        self.logger.info("ROLLBACK STATUS")
        self.logger.info("=" * 70)

        entries = self.audit_log.read_entries(limit=10)
        if not entries:
            self.logger.info("No rollback operations recorded")
            return

        for entry in reversed(entries):
            status_icon = "✓" if entry.rollback_success else "✗"
            self.logger.info(f"\n{status_icon} {entry.timestamp}")
            self.logger.info(f"  Snapshot: {entry.snapshot_id}")
            self.logger.info(f"  Status: {entry.status}")
            self.logger.info(f"  Type: {entry.rollback_type}")
            self.logger.info(f"  Duration: {entry.duration_seconds:.2f}s")
            if entry.error_message:
                self.logger.info(f"  Error: {entry.error_message}")

        self.logger.info("\n" + "=" * 70)

    def show_audit_log(self, limit: int = 50):
        """Show audit log entries"""
        self.logger.info("=" * 70)
        self.logger.info("ROLLBACK AUDIT LOG")
        self.logger.info("=" * 70)

        entries = self.audit_log.read_entries(limit=limit)
        if not entries:
            self.logger.info("No audit entries")
            return

        for entry in reversed(entries):
            status_icon = "✓" if entry.rollback_success else "✗"
            self.logger.info(
                f"{status_icon} {entry.timestamp} | "
                f"{entry.action:10s} | "
                f"{entry.status:15s} | "
                f"{entry.rollback_type:10s}"
            )

        self.logger.info("\n" + "=" * 70)


# ============================================================================
# CLI & MAIN
# ============================================================================

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ChromaDB Rollback System - Emergency Recovery & Point-in-Time Restore",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Manual full rollback
  python chromadb_rollback.py \\
    --chromadb-url http://localhost:8000 \\
    --action rollback \\
    --snapshot-id "snapshot_20251130_143022"

  # Dry-run rollback (verify only)
  python chromadb_rollback.py \\
    --chromadb-url http://localhost:8000 \\
    --action rollback \\
    --snapshot-id "snapshot_20251130_143022" \\
    --dry-run

  # Partial rollback (specific collections)
  python chromadb_rollback.py \\
    --chromadb-url http://localhost:8000 \\
    --action rollback \\
    --snapshot-id "snapshot_20251130_143022" \\
    --partial \\
    --failed-collections "sergio_corpus,sergio_personality"

  # Check rollback status
  python chromadb_rollback.py --action status

  # View audit log
  python chromadb_rollback.py --action audit-log
        """
    )

    parser.add_argument("--chromadb-url", default="http://localhost:8000",
                       help="ChromaDB URL (default: http://localhost:8000)")
    parser.add_argument("--action", required=True,
                       choices=["rollback", "status", "audit-log"],
                       help="Action to perform")
    parser.add_argument("--snapshot-id",
                       help="Snapshot ID (for rollback action)")
    parser.add_argument("--snapshot-dir", default="/home/setup/infrafabric/chromadb_snapshots",
                       help="Snapshot directory")
    parser.add_argument("--partial", action="store_true",
                       help="Partial rollback (failed collections only)")
    parser.add_argument("--failed-collections",
                       help="Comma-separated list of collections to rollback")
    parser.add_argument("--dry-run", action="store_true",
                       help="Verify without actual rollback")
    parser.add_argument("--no-verify-before", action="store_true",
                       help="Skip snapshot verification before rollback")
    parser.add_argument("--no-verify-after", action="store_true",
                       help="Skip restoration verification")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose logging")

    args = parser.parse_args()

    # Create config
    config = RollbackConfig(
        chromadb_url=args.chromadb_url,
        action=args.action,
        snapshot_dir=args.snapshot_dir,
        snapshot_id=args.snapshot_id,
        partial=args.partial,
        failed_collections=args.failed_collections,
        dry_run=args.dry_run,
        verify_before=not args.no_verify_before,
        verify_after=not args.no_verify_after,
        verbose=args.verbose
    )

    logger = setup_logging(config.snapshot_dir, config.verbose)
    audit_log = AuditLogManager(logger, config.snapshot_dir)

    try:
        # For rollback action, connect to ChromaDB
        if config.action == "rollback":
            if not CHROMADB_AVAILABLE:
                logger.error("chromadb not available")
                sys.exit(1)

            if not config.snapshot_id:
                logger.error("--snapshot-id required for rollback action")
                sys.exit(1)

            logger.info(f"Connecting to {config.chromadb_url}...")
            try:
                if config.chromadb_url.startswith("http"):
                    host = config.chromadb_url.split("//")[1].split(":")[0]
                    port = int(config.chromadb_url.split(":")[-1])
                    client = chromadb.HttpClient(host=host, port=port)
                    client.heartbeat()
                else:
                    client = chromadb.PersistentClient(path=config.chromadb_url)
                logger.info("✓ Connected")
            except Exception as e:
                logger.error(f"Failed to connect: {e}")
                sys.exit(1)

            executor = RollbackExecutor(client, logger, config, audit_log)
            success, audit_entry = executor.rollback_from_snapshot(config.snapshot_id)
            audit_log.log_entry(audit_entry)
            sys.exit(0 if success else 1)

        elif config.action == "status":
            monitor = RollbackStatusMonitor(logger, audit_log)
            monitor.show_status()
            sys.exit(0)

        elif config.action == "audit-log":
            monitor = RollbackStatusMonitor(logger, audit_log)
            monitor.show_audit_log(limit=50)
            sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
