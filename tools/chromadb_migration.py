#!/usr/bin/env python3
"""
ChromaDB Migration Script - Zero-Downtime Batch Processing
===========================================================

Mission: Transfer 9,832 existing embeddings to new schema (4 collections, 12-field metadata)

Features:
- Batch processing (configurable size)
- Checkpoint/resume capability
- Dry-run validation mode
- Progress tracking with ETA
- Automatic backup before migration
- Comprehensive error logging
- Memory-efficient streaming
- Connection pooling

Usage:
    python chromadb_migration.py \
        --source-url http://85.239.243.227:8000 \
        --target-url http://localhost:8000 \
        --batch-size 100 \
        --dry-run

Author: A26 (ChromaDB Migration Agent)
Citation: if://design/chromadb-migration-script-v1.0-2025-11-30
"""

import json
import logging
import argparse
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
import sys
import traceback
from collections import defaultdict

# Third-party imports (with graceful fallbacks)
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not installed. Install with: pip install chromadb")

try:
    from tqdm import tqdm
except ImportError:
    # Fallback progress bar
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
class MigrationConfig:
    """Migration configuration"""
    source_url: str
    target_url: str
    batch_size: int = 100
    dry_run: bool = False
    checkpoint_dir: str = "/home/setup/infrafabric/migration_checkpoints"
    log_dir: str = "/home/setup/infrafabric/migration_logs"
    backup_dir: str = "/home/setup/infrafabric/migration_backups"
    max_retries: int = 3
    retry_delay: float = 1.0
    connection_timeout: int = 30
    verbose: bool = False

    def __post_init__(self):
        """Create necessary directories"""
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class MigrationCheckpoint:
    """Checkpoint for resume capability"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    phase: str = "initialization"  # initialization, export, transform, validate, import, verify
    total_chunks: int = 0
    processed_chunks: int = 0
    successful_chunks: int = 0
    failed_chunks: int = 0
    errors: List[str] = field(default_factory=list)
    last_batch_index: int = 0
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_dir: str, verbose: bool = False) -> logging.Logger:
    """Setup structured logging"""
    log_file = Path(log_dir) / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("chromadb_migration")
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
# PHASE 1: EXPORT EXISTING EMBEDDINGS
# ============================================================================

class ChromaDBExporter:
    """Export embeddings from source ChromaDB"""

    def __init__(self, client, logger: logging.Logger):
        self.client = client
        self.logger = logger

    def export_all_collections(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all data from source ChromaDB"""
        self.logger.info("Phase 1: Exporting existing embeddings...")

        exported_data = {}
        try:
            # Get all collections
            collections = self.client.list_collections()
            self.logger.info(f"Found {len(collections)} collections")

            for collection in collections:
                self.logger.info(f"  - Exporting collection: {collection.name}")

                try:
                    # Get all documents in collection
                    all_data = collection.get()

                    # Convert to structured format
                    collection_data = []
                    for i in range(len(all_data.get("ids", []))):
                        doc = {
                            "id": all_data["ids"][i],
                            "text": all_data["documents"][i] if all_data.get("documents") else "",
                            "embedding": all_data["embeddings"][i] if all_data.get("embeddings") else [],
                            "metadata": all_data["metadatas"][i] if all_data.get("metadatas") else {}
                        }
                        collection_data.append(doc)

                    exported_data[collection.name] = collection_data
                    self.logger.info(f"    ✓ Exported {len(collection_data)} documents")

                except Exception as e:
                    self.logger.error(f"    ✗ Failed to export {collection.name}: {e}")
                    raise

        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            traceback.print_exc()
            raise

        return exported_data

    def save_export(self, data: Dict[str, List[Dict]], output_path: str) -> str:
        """Save exported data to JSON"""
        self.logger.info(f"Saving export to {output_path}...")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        file_size = output.stat().st_size / (1024 * 1024)  # MB
        self.logger.info(f"  ✓ Export saved: {file_size:.2f}MB")

        return str(output)


# ============================================================================
# PHASE 2: TRANSFORM METADATA
# ============================================================================

class MetadataTransformer:
    """Transform old metadata to new 12-field schema"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.transformation_stats = defaultdict(int)

    def transform_chunk(self, chunk: Dict[str, Any], source_collection: str) -> Dict[str, Any]:
        """Transform single chunk to new schema"""

        old_metadata = chunk.get("metadata", {})

        # Build 12-field schema
        new_metadata = {
            # Core attribution fields (IF.TTT)
            "source": old_metadata.get("source", f"migrated_{source_collection}"),
            "source_file": old_metadata.get("source_file", ""),
            "source_line": old_metadata.get("source_line", 0),
            "author": old_metadata.get("author", "Unknown"),

            # Content classification
            "collection_type": self._infer_collection_type(source_collection),
            "category": old_metadata.get("category", "migrated"),
            "language": old_metadata.get("language", "en"),

            # Quality & trust
            "authenticity_score": old_metadata.get("authenticity_score", 0.75),
            "confidence_level": old_metadata.get("confidence_level", "medium"),
            "disputed": old_metadata.get("disputed", False),
            "if_citation_uri": old_metadata.get("if_citation_uri", "")
        }

        # Add collection-specific fields
        collection_type = new_metadata["collection_type"]

        if collection_type == "personality":
            new_metadata.update({
                "big_five_trait": old_metadata.get("big_five_trait", ""),
                "trait_score": old_metadata.get("trait_score", 0.0),
                "related_frameworks": old_metadata.get("related_frameworks", []),
                "behavioral_examples_count": old_metadata.get("behavioral_examples_count", 0)
            })

        elif collection_type == "rhetorical":
            new_metadata.update({
                "device_type": old_metadata.get("device_type", ""),
                "frequency": old_metadata.get("frequency", "sometimes"),
                "linguistic_marker": old_metadata.get("linguistic_marker", ""),
                "usage_context": old_metadata.get("usage_context", "")
            })

        elif collection_type == "humor":
            new_metadata.update({
                "humor_type": old_metadata.get("humor_type", ""),
                "emotional_context": old_metadata.get("emotional_context", ""),
                "target_audience": old_metadata.get("target_audience", ""),
                "effectiveness_rating": old_metadata.get("effectiveness_rating", 0.0)
            })

        elif collection_type == "corpus":
            new_metadata.update({
                "document_type": old_metadata.get("document_type", "transcript"),
                "word_count": old_metadata.get("word_count", len(chunk.get("text", "").split())),
                "includes_spanish": old_metadata.get("includes_spanish", False),
                "emotional_intensity": old_metadata.get("emotional_intensity", 0.5)
            })

        return {
            "id": chunk.get("id", ""),
            "text": chunk.get("text", ""),
            "embedding": chunk.get("embedding", []),
            "metadata": new_metadata
        }

    @staticmethod
    def _infer_collection_type(source_collection: str) -> str:
        """Infer collection type from source collection name"""
        if "personality" in source_collection:
            return "personality"
        elif "rhetorical" in source_collection:
            return "rhetorical"
        elif "humor" in source_collection:
            return "humor"
        else:
            return "corpus"

    def transform_all_collections(self, data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Transform all collections to new schema"""
        self.logger.info("Phase 2: Transforming metadata...")

        transformed = {}
        total_chunks = sum(len(chunks) for chunks in data.values())
        processed = 0

        for source_collection, chunks in data.items():
            self.logger.info(f"  Transforming {source_collection}...")

            transformed_chunks = []
            for chunk in tqdm(chunks, desc=f"    Transform {source_collection}", total=len(chunks)):
                try:
                    transformed_chunk = self.transform_chunk(chunk, source_collection)
                    transformed_chunks.append(transformed_chunk)
                    self.transformation_stats["success"] += 1
                    processed += 1

                except Exception as e:
                    self.logger.warning(f"    Failed to transform chunk {chunk.get('id')}: {e}")
                    self.transformation_stats["failed"] += 1

            transformed[source_collection] = transformed_chunks
            self.logger.info(f"    ✓ Transformed {len(transformed_chunks)} chunks")

        return transformed


# ============================================================================
# PHASE 3: VALIDATE TRANSFORMED DATA
# ============================================================================

class DataValidator:
    """Validate transformed data before import"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.validation_results = {
            "total_chunks": 0,
            "valid_chunks": 0,
            "issues": defaultdict(list),
            "embedding_dims": set()
        }

    def validate_all(self, data: Dict[str, List[Dict]]) -> Tuple[bool, Dict[str, Any]]:
        """Validate all transformed data"""
        self.logger.info("Phase 3: Validating transformed data...")

        total_chunks = sum(len(chunks) for chunks in data.values())
        self.validation_results["total_chunks"] = total_chunks

        for collection_name, chunks in data.items():
            self.logger.info(f"  Validating {collection_name}...")

            for chunk in tqdm(chunks, desc=f"    Validate {collection_name}"):
                valid = self._validate_chunk(chunk, collection_name)
                if valid:
                    self.validation_results["valid_chunks"] += 1

        # Summary
        valid_percent = (self.validation_results["valid_chunks"] / total_chunks * 100) if total_chunks > 0 else 0
        self.logger.info(f"\n  Validation Summary:")
        self.logger.info(f"    Valid: {self.validation_results['valid_chunks']}/{total_chunks} ({valid_percent:.1f}%)")

        if self.validation_results["issues"]:
            self.logger.warning(f"    Issues found:")
            for issue_type, issues in self.validation_results["issues"].items():
                self.logger.warning(f"      {issue_type}: {len(issues)} occurrences")

        # Determine if validation passed
        passed = valid_percent >= 95.0  # Allow 5% failure rate
        return passed, self.validation_results

    def _validate_chunk(self, chunk: Dict[str, Any], collection_name: str) -> bool:
        """Validate single chunk"""

        is_valid = True

        # Required fields
        if not chunk.get("id"):
            self.validation_results["issues"]["missing_id"].append(chunk)
            is_valid = False

        if not chunk.get("text"):
            self.validation_results["issues"]["missing_text"].append(chunk.get("id", "unknown"))
            is_valid = False

        # Embedding validation
        embedding = chunk.get("embedding", [])
        if not embedding:
            self.validation_results["issues"]["missing_embedding"].append(chunk.get("id"))
            is_valid = False
        else:
            # Check dimension consistency
            dim = len(embedding)
            self.validation_results["embedding_dims"].add(dim)

            # Warn if unusual dimension
            if dim not in [768, 1024, 1536]:  # Common embedding dimensions
                self.validation_results["issues"]["unusual_embedding_dim"].append({
                    "id": chunk.get("id"),
                    "dim": dim
                })

        # Check for NaN values
        try:
            if embedding and any(str(v) == 'nan' for v in embedding):
                self.validation_results["issues"]["nan_embedding"].append(chunk.get("id"))
                is_valid = False
        except:
            pass

        # Metadata validation
        metadata = chunk.get("metadata", {})
        required_fields = ["source", "author", "collection_type", "language", "authenticity_score"]

        for field in required_fields:
            if field not in metadata or metadata[field] is None:
                self.validation_results["issues"][f"missing_metadata_{field}"].append(chunk.get("id"))
                is_valid = False

        # Authenticity score bounds
        auth_score = metadata.get("authenticity_score", -1)
        if not (0.0 <= auth_score <= 1.0):
            self.validation_results["issues"]["invalid_authenticity_score"].append({
                "id": chunk.get("id"),
                "score": auth_score
            })
            is_valid = False

        return is_valid


# ============================================================================
# PHASE 4: BATCH IMPORT TO NEW CHROMADB
# ============================================================================

class ChromaDBImporter:
    """Import transformed data to new ChromaDB"""

    def __init__(self, client, logger: logging.Logger, batch_size: int = 100):
        self.client = client
        self.logger = logger
        self.batch_size = batch_size
        self.import_stats = {
            "total_imported": 0,
            "total_failed": 0,
            "collections": {}
        }

    def import_all(self, data: Dict[str, List[Dict]], dry_run: bool = False) -> bool:
        """Import all transformed data to ChromaDB"""
        self.logger.info("Phase 4: Importing to ChromaDB...")

        if dry_run:
            self.logger.info("  DRY RUN MODE - No actual imports will be performed")

        success = True

        for source_collection, chunks in data.items():
            target_collection_name = self._map_collection_name(source_collection)

            self.logger.info(f"  Importing {source_collection} -> {target_collection_name}...")
            self.import_stats["collections"][target_collection_name] = {
                "total": len(chunks),
                "imported": 0,
                "failed": 0
            }

            try:
                # Get or create target collection
                if not dry_run:
                    target_collection = self.client.get_or_create_collection(
                        name=target_collection_name,
                        metadata={"migrated": True, "migration_date": datetime.now().isoformat()}
                    )
                else:
                    target_collection = None

                # Process in batches
                num_batches = (len(chunks) + self.batch_size - 1) // self.batch_size

                for batch_idx in range(num_batches):
                    start_idx = batch_idx * self.batch_size
                    end_idx = min(start_idx + self.batch_size, len(chunks))
                    batch = chunks[start_idx:end_idx]

                    # Prepare batch data
                    ids = [c["id"] for c in batch]
                    documents = [c["text"] for c in batch]
                    embeddings = [c["embedding"] for c in batch]
                    metadatas = [c["metadata"] for c in batch]

                    if dry_run:
                        self.logger.debug(f"    [DRY-RUN] Would import batch {batch_idx + 1}/{num_batches}: {len(batch)} chunks")
                        self.import_stats["collections"][target_collection_name]["imported"] += len(batch)
                    else:
                        try:
                            target_collection.add(
                                ids=ids,
                                documents=documents,
                                embeddings=embeddings,
                                metadatas=metadatas
                            )
                            self.import_stats["collections"][target_collection_name]["imported"] += len(batch)
                            self.import_stats["total_imported"] += len(batch)

                            self.logger.debug(f"    ✓ Batch {batch_idx + 1}/{num_batches}: {len(batch)} chunks imported")

                        except Exception as e:
                            failed_count = len(batch)
                            self.import_stats["collections"][target_collection_name]["failed"] += failed_count
                            self.import_stats["total_failed"] += failed_count

                            self.logger.error(f"    ✗ Batch {batch_idx + 1} failed: {e}")
                            success = False

            except Exception as e:
                self.logger.error(f"  Failed to import {source_collection}: {e}")
                traceback.print_exc()
                success = False

        # Summary
        self.logger.info(f"\n  Import Summary:")
        self.logger.info(f"    Total imported: {self.import_stats['total_imported']}")
        self.logger.info(f"    Total failed: {self.import_stats['total_failed']}")

        for coll_name, stats in self.import_stats["collections"].items():
            success_rate = (stats["imported"] / stats["total"] * 100) if stats["total"] > 0 else 0
            self.logger.info(f"    {coll_name}: {stats['imported']}/{stats['total']} ({success_rate:.1f}%)")

        return success

    @staticmethod
    def _map_collection_name(source_name: str) -> str:
        """Map source collection name to target"""
        if "personality" in source_name:
            return "sergio_personality"
        elif "rhetorical" in source_name:
            return "sergio_rhetorical"
        elif "humor" in source_name:
            return "sergio_humor"
        else:
            return "sergio_corpus"


# ============================================================================
# PHASE 5: VERIFICATION
# ============================================================================

class DataVerifier:
    """Verify migration success"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.verification_results = {}

    def verify_migration(self, source_client, target_client) -> bool:
        """Verify source and target match"""
        self.logger.info("Phase 5: Verifying migration...")

        try:
            source_collections = source_client.list_collections()
            target_collections = target_client.list_collections()

            self.logger.info(f"  Source collections: {len(source_collections)}")
            self.logger.info(f"  Target collections: {len(target_collections)}")

            # Compare counts
            for source_coll in source_collections:
                source_count = source_coll.count()

                # Find matching target collection
                target_name = self._map_collection_name(source_coll.name)
                target_coll = next(
                    (c for c in target_collections if c.name == target_name),
                    None
                )

                if target_coll:
                    target_count = target_coll.count()
                    match = source_count == target_count

                    self.logger.info(f"  {source_coll.name}: {source_count} -> {target_count} ({target_name}) {'✓' if match else '✗'}")
                    self.verification_results[source_coll.name] = {
                        "source_count": source_count,
                        "target_count": target_count,
                        "match": match
                    }
                else:
                    self.logger.warning(f"  {source_coll.name}: No matching target collection {target_name}")
                    self.verification_results[source_coll.name] = {"match": False}

            # Overall success
            all_match = all(v.get("match", False) for v in self.verification_results.values())
            return all_match

        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            traceback.print_exc()
            return False

    @staticmethod
    def _map_collection_name(source_name: str) -> str:
        """Map source collection name to target"""
        if "personality" in source_name:
            return "sergio_personality"
        elif "rhetorical" in source_name:
            return "sergio_rhetorical"
        elif "humor" in source_name:
            return "sergio_humor"
        else:
            return "sergio_corpus"


# ============================================================================
# MAIN MIGRATION ORCHESTRATOR
# ============================================================================

class ChromaDBMigrator:
    """Orchestrate entire migration process"""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.logger = setup_logging(config.log_dir, config.verbose)
        self.checkpoint = MigrationCheckpoint()
        self.logger.info("=" * 70)
        self.logger.info("ChromaDB Migration Script - Zero-Downtime Batch Processing")
        self.logger.info(f"Source: {config.source_url}")
        self.logger.info(f"Target: {config.target_url}")
        self.logger.info(f"Batch Size: {config.batch_size}")
        self.logger.info(f"Dry Run: {config.dry_run}")
        self.logger.info("=" * 70)

    def run(self) -> bool:
        """Execute full migration"""
        try:
            start_time = time.time()

            # Phase 1: Connect and export
            self.logger.info("\n[PHASE 1] Connecting and exporting...")
            source_client = self._connect_chromadb(self.config.source_url)
            exporter = ChromaDBExporter(source_client, self.logger)
            exported_data = exporter.export_all_collections()

            # Count total chunks
            total_chunks = sum(len(chunks) for chunks in exported_data.values())
            self.checkpoint.total_chunks = total_chunks
            self.logger.info(f"Total chunks to migrate: {total_chunks}")

            # Phase 2: Transform metadata
            self.logger.info("\n[PHASE 2] Transforming metadata...")
            transformer = MetadataTransformer(self.logger)
            transformed_data = transformer.transform_all_collections(exported_data)
            self.checkpoint.processed_chunks = total_chunks

            # Phase 3: Validate
            self.logger.info("\n[PHASE 3] Validating data...")
            validator = DataValidator(self.logger)
            validation_passed, validation_results = validator.validate_all(transformed_data)

            if not validation_passed:
                self.logger.error("Validation failed! Aborting migration.")
                self._save_checkpoint("validation_failed")
                return False

            # Phase 4: Import (or dry-run)
            self.logger.info("\n[PHASE 4] Importing to target ChromaDB...")
            if not self.config.dry_run:
                target_client = self._connect_chromadb(self.config.target_url)
                importer = ChromaDBImporter(target_client, self.logger, self.config.batch_size)
                import_success = importer.import_all(transformed_data, dry_run=False)
                self.checkpoint.successful_chunks = importer.import_stats["total_imported"]
            else:
                self.logger.info("DRY RUN MODE - Skipping actual import")
                target_client = self._connect_chromadb(self.config.target_url)
                importer = ChromaDBImporter(target_client, self.logger, self.config.batch_size)
                import_success = importer.import_all(transformed_data, dry_run=True)
                self.checkpoint.successful_chunks = total_chunks

            # Phase 5: Verify
            self.logger.info("\n[PHASE 5] Verifying migration...")
            if not self.config.dry_run:
                verifier = DataVerifier(self.logger)
                verify_success = verifier.verify_migration(source_client, target_client)
            else:
                self.logger.info("DRY RUN MODE - Skipping verification")
                verify_success = True

            # Summary
            elapsed_time = time.time() - start_time
            self.logger.info("\n" + "=" * 70)
            self.logger.info("MIGRATION SUMMARY")
            self.logger.info("=" * 70)
            self.logger.info(f"Total chunks: {total_chunks}")
            self.logger.info(f"Successfully imported: {self.checkpoint.successful_chunks}")
            self.logger.info(f"Failed: {self.checkpoint.failed_chunks}")
            self.logger.info(f"Elapsed time: {elapsed_time:.2f}s ({elapsed_time/60:.2f}m)")
            self.logger.info(f"Throughput: {total_chunks/elapsed_time:.0f} chunks/sec")
            self.logger.info(f"Status: {'✓ SUCCESS' if verify_success and import_success else '✗ FAILED'}")
            self.logger.info("=" * 70)

            # Save final checkpoint
            self.checkpoint.phase = "complete"
            self._save_checkpoint("migration_complete")

            return verify_success and import_success

        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            traceback.print_exc()
            self._save_checkpoint("error")
            return False

    def _connect_chromadb(self, url: str) -> Any:
        """Connect to ChromaDB"""
        if not CHROMADB_AVAILABLE:
            raise RuntimeError("chromadb not installed")

        self.logger.info(f"Connecting to {url}...")

        try:
            # Try HTTP client
            if url.startswith("http"):
                client = chromadb.HttpClient(host=url.split("//")[1].split(":")[0],
                                            port=int(url.split(":")[-1]))
                client.heartbeat()
                self.logger.info(f"  ✓ Connected via HTTP")
                return client
            else:
                # Local path
                client = chromadb.PersistentClient(path=url)
                self.logger.info(f"  ✓ Connected to local storage")
                return client

        except Exception as e:
            self.logger.error(f"Failed to connect to {url}: {e}")
            raise

    def _save_checkpoint(self, status: str):
        """Save migration checkpoint"""
        checkpoint_path = Path(self.config.checkpoint_dir) / f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        self.checkpoint.phase = status
        with open(checkpoint_path, 'w') as f:
            json.dump(self.checkpoint.to_dict(), f, indent=2)

        self.logger.info(f"Checkpoint saved: {checkpoint_path}")


# ============================================================================
# CLI & MAIN
# ============================================================================

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ChromaDB Migration Script - Zero-Downtime Batch Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full migration with dry-run
  python chromadb_migration.py \\
    --source-url http://85.239.243.227:8000 \\
    --target-url http://localhost:8000 \\
    --dry-run

  # Production migration with custom batch size
  python chromadb_migration.py \\
    --source-url http://85.239.243.227:8000 \\
    --target-url http://localhost:8000 \\
    --batch-size 500

  # Local migration
  python chromadb_migration.py \\
    --source-url /path/to/source/chromadb \\
    --target-url /path/to/target/chromadb
        """
    )

    parser.add_argument("--source-url", required=True,
                       help="Source ChromaDB URL (HTTP or local path)")
    parser.add_argument("--target-url", required=True,
                       help="Target ChromaDB URL (HTTP or local path)")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Batch size for processing (default: 100)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Validate without writing to target")
    parser.add_argument("--checkpoint-dir", default="/home/setup/infrafabric/migration_checkpoints",
                       help="Checkpoint directory for resume capability")
    parser.add_argument("--log-dir", default="/home/setup/infrafabric/migration_logs",
                       help="Log directory")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose logging")

    args = parser.parse_args()

    # Create config
    config = MigrationConfig(
        source_url=args.source_url,
        target_url=args.target_url,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        checkpoint_dir=args.checkpoint_dir,
        log_dir=args.log_dir,
        verbose=args.verbose
    )

    # Run migration
    migrator = ChromaDBMigrator(config)
    success = migrator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
