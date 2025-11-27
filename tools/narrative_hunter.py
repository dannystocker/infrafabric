#!/usr/bin/env python3
"""
OPERATION NARRATIVE DRAGNET - The Historian Swarm
==================================================

Role: Multi-threaded narrative extraction and archival system.

Mission: Deploy parallel workers to scan filesystems, archives, and Redis for
hidden InfraFabric narratives (Episodes 1-18, Medium articles, session logs).

Core Philosophy: "Hunt Everything, Miss Nothing, Deduplicate Ruthlessly"
  Every file is a potential narrative container.
  Every Redis key could hold session context.
  Every archive might contain lost episodes.

Swarm Architecture:
  - HaikuWorker threads: Parallel file processors
  - RedisArchaeologist: Key scanner and value extractor
  - DeduplicationEngine: Smart duplicate detection using content hashes
  - NarrativeExtractor: Intelligent story extraction from mixed content

Target Artifacts:
  - Episodes 1-18 narratives
  - Medium article drafts
  - Session chronicles
  - Council meeting logs
  - Instance case studies

Search Locations:
  1. /mnt/c/Users/Setup/Downloads/ (Windows downloads)
  2. /home/setup/ (Linux workspace)
  3. Redis DB0/DB1 (session contexts)
  4. ZIP/TAR.GZ archives (without full extraction)

Output Structure:
  docs/narratives/staging/
    ├── recovered_episode_01_[hash].md
    ├── recovered_medium_article_[hash].md
    ├── recovered_chronicle_[hash].md
    └── NARRATIVE_RECOVERY_REPORT.md

Usage:
    python3 tools/narrative_hunter.py --workers 8 --redis-scan
    python3 tools/narrative_hunter.py --quick-scan  # Fast mode, skip archives
    python3 tools/narrative_hunter.py --report-only # Generate report from existing staging
"""

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import threading
import time
import zipfile
import tarfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
from typing import Any, Dict, List, Optional, Set, Tuple

# Optional Redis support
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    print("⚠ Warning: redis-py not installed. Redis scanning disabled.")
    print("  Install: pip install redis")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class NarrativeFragment:
    """A discovered narrative fragment with metadata"""
    content: str
    source_path: str
    fragment_type: str  # 'episode', 'medium', 'chronicle', 'log', 'unknown'
    keywords_matched: List[str]
    content_hash: str
    discovered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    size_bytes: int = 0
    confidence_score: float = 0.0  # 0.0-1.0 how likely this is a real narrative

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode('utf-8', errors='ignore')).hexdigest()[:16]
        if not self.size_bytes:
            self.size_bytes = len(self.content.encode('utf-8', errors='ignore'))


@dataclass
class RecoveryStatistics:
    """Statistics for narrative recovery operation"""
    files_scanned: int = 0
    archives_scanned: int = 0
    redis_keys_scanned: int = 0
    narratives_found: int = 0
    duplicates_removed: int = 0
    total_bytes_recovered: int = 0
    errors_encountered: int = 0
    scan_duration_seconds: float = 0.0


# =============================================================================
# NARRATIVE PATTERNS & KEYWORDS
# =============================================================================

# Primary keywords for narrative detection
NARRATIVE_KEYWORDS = [
    # Episodes
    r'\bEpisode\s+\d+\b', r'\bEp\.\s*\d+\b', r'\bEP\d+\b',
    # Narratives
    r'\bNarration\b', r'\bChronicle\b', r'\bMedium Article\b',
    # InfraFabric specifics
    r'\bThe Council\b', r'\bGuardian\b', r'\bInstance\s*#\d+\b',
    r'\bIF\.witness\b', r'\bIF\.guard\b', r'\bIF\.ceo\b',
    # Story markers
    r'\bOnce upon a time\b', r'\bIn the beginning\b',
    r'\bThe story of\b', r'\bChapter\s+\d+\b',
]

# Compiled patterns for efficiency
NARRATIVE_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in NARRATIVE_KEYWORDS]

# File extensions to scan
SCANNABLE_EXTENSIONS = {'.md', '.txt', '.json', '.log', '.yaml', '.yml'}
ARCHIVE_EXTENSIONS = {'.zip', '.tar.gz', '.tgz', '.tar'}

# Minimum content length for a valid narrative (characters)
MIN_NARRATIVE_LENGTH = 500

# Maximum file size to process (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


# =============================================================================
# DEDUPLICATION ENGINE
# =============================================================================

class DeduplicationEngine:
    """
    Smart duplicate detection using content hashes and similarity analysis.
    """

    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.seen_fragments: Dict[str, NarrativeFragment] = {}
        self.duplicates_removed = 0

    def is_duplicate(self, fragment: NarrativeFragment) -> Tuple[bool, Optional[str]]:
        """
        Check if fragment is duplicate. Returns (is_dup, reason).

        Logic:
        1. Exact hash match → duplicate
        2. Similar hash (fuzzy) → likely duplicate
        3. Different source priority → keep best version
        """
        # Exact hash match
        if fragment.content_hash in self.seen_hashes:
            return True, "Exact content hash match"

        # Check for near-duplicates (first 100 chars)
        content_prefix = fragment.content[:100].strip()
        for existing_hash, existing_fragment in self.seen_fragments.items():
            existing_prefix = existing_fragment.content[:100].strip()

            # Very similar prefixes + same type = likely duplicate
            if (self._similarity(content_prefix, existing_prefix) > 0.9 and
                fragment.fragment_type == existing_fragment.fragment_type):

                # Prefer markdown over JSON/TXT
                if self._is_better_source(fragment, existing_fragment):
                    # Replace existing with better version
                    self.seen_hashes.remove(existing_hash)
                    del self.seen_fragments[existing_hash]
                    logger.info(f"Replacing duplicate with better version: {fragment.source_path}")
                    return False, None  # Not a duplicate, it's better
                else:
                    return True, f"Near-duplicate of {existing_fragment.source_path}"

        return False, None

    def register(self, fragment: NarrativeFragment):
        """Register fragment as seen"""
        self.seen_hashes.add(fragment.content_hash)
        self.seen_fragments[fragment.content_hash] = fragment

    def _similarity(self, str1: str, str2: str) -> float:
        """Simple character-based similarity score"""
        if not str1 or not str2:
            return 0.0

        # Jaccard similarity on character bigrams
        bigrams1 = set(str1[i:i+2] for i in range(len(str1)-1))
        bigrams2 = set(str2[i:i+2] for i in range(len(str2)-1))

        if not bigrams1 or not bigrams2:
            return 0.0

        intersection = bigrams1 & bigrams2
        union = bigrams1 | bigrams2

        return len(intersection) / len(union) if union else 0.0

    def _is_better_source(self, new: NarrativeFragment, existing: NarrativeFragment) -> bool:
        """
        Determine if new fragment is from better source than existing.

        Priority: .md > .txt > .json > .log
        """
        priority = {'.md': 4, '.txt': 3, '.json': 2, '.log': 1, 'unknown': 0}

        new_ext = Path(new.source_path).suffix.lower()
        existing_ext = Path(existing.source_path).suffix.lower()

        return priority.get(new_ext, 0) > priority.get(existing_ext, 0)


# =============================================================================
# NARRATIVE EXTRACTOR
# =============================================================================

class NarrativeExtractor:
    """
    Intelligent extraction of narrative content from mixed-content files.
    """

    @staticmethod
    def extract_from_text(content: str, source_path: str) -> Optional[NarrativeFragment]:
        """
        Extract narrative from plain text/markdown files.
        """
        # Count keyword matches
        matches = []
        for pattern in NARRATIVE_PATTERNS:
            matches.extend(pattern.findall(content))

        if not matches:
            return None

        # Calculate confidence based on keyword density
        confidence = min(1.0, len(matches) / 10.0)  # Max at 10 keywords

        # Determine fragment type
        fragment_type = NarrativeExtractor._classify_content(content, matches)

        return NarrativeFragment(
            content=content,
            source_path=source_path,
            fragment_type=fragment_type,
            keywords_matched=matches,
            content_hash="",  # Will be computed in __post_init__
            confidence_score=confidence
        )

    @staticmethod
    def extract_from_json(data: Any, source_path: str, parent_key: str = "") -> List[NarrativeFragment]:
        """
        Recursively extract narrative content from JSON structures.

        Looks for keys like: 'content', 'text', 'message', 'body', 'narrative'
        """
        fragments = []
        narrative_keys = {'content', 'text', 'message', 'body', 'narrative', 'story', 'episode'}

        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key

                # Check if this key looks like narrative content
                if key.lower() in narrative_keys and isinstance(value, str):
                    fragment = NarrativeExtractor.extract_from_text(value, f"{source_path}:{full_key}")
                    if fragment and len(value) >= MIN_NARRATIVE_LENGTH:
                        fragments.append(fragment)

                # Recurse into nested structures
                elif isinstance(value, (dict, list)):
                    fragments.extend(NarrativeExtractor.extract_from_json(value, source_path, full_key))

        elif isinstance(data, list):
            for idx, item in enumerate(data):
                full_key = f"{parent_key}[{idx}]" if parent_key else f"[{idx}]"
                if isinstance(item, (dict, list)):
                    fragments.extend(NarrativeExtractor.extract_from_json(item, source_path, full_key))

        return fragments

    @staticmethod
    def _classify_content(content: str, matches: List[str]) -> str:
        """
        Classify narrative type based on content and matches.
        """
        content_lower = content.lower()

        if any('episode' in m.lower() for m in matches):
            return 'episode'
        elif 'medium' in content_lower or 'article' in content_lower:
            return 'medium'
        elif 'chronicle' in content_lower or 'session' in content_lower:
            return 'chronicle'
        elif 'log' in content_lower or 'debug' in content_lower:
            return 'log'
        else:
            return 'unknown'


# =============================================================================
# HAIKU WORKER (Thread)
# =============================================================================

class HaikuWorker(threading.Thread):
    """
    Worker thread that processes files from queue in parallel.
    """

    def __init__(
        self,
        worker_id: int,
        file_queue: Queue,
        result_queue: Queue,
        stats: RecoveryStatistics,
        stats_lock: threading.Lock
    ):
        super().__init__(name=f"HaikuWorker-{worker_id}")
        self.worker_id = worker_id
        self.file_queue = file_queue
        self.result_queue = result_queue
        self.stats = stats
        self.stats_lock = stats_lock
        self.daemon = True

    def run(self):
        """Main worker loop"""
        logger.info(f"Worker {self.worker_id} started")

        while True:
            try:
                # Get file path from queue (timeout 1 second)
                file_path = self.file_queue.get(timeout=1)

                if file_path is None:  # Poison pill to stop worker
                    break

                # Process the file
                self._process_file(file_path)

                self.file_queue.task_done()

            except Empty:
                continue  # Queue empty, keep waiting
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                with self.stats_lock:
                    self.stats.errors_encountered += 1

        logger.info(f"Worker {self.worker_id} finished")

    def _process_file(self, file_path: str):
        """
        Process a single file and extract narratives.
        """
        try:
            path = Path(file_path)

            # Check file size
            if path.stat().st_size > MAX_FILE_SIZE:
                logger.warning(f"Skipping large file: {file_path} ({path.stat().st_size / 1024 / 1024:.1f} MB)")
                return

            # Update stats
            with self.stats_lock:
                self.stats.files_scanned += 1

            # Handle different file types
            if path.suffix.lower() in ARCHIVE_EXTENSIONS:
                self._process_archive(path)
            elif path.suffix.lower() == '.json':
                self._process_json(path)
            elif path.suffix.lower() in SCANNABLE_EXTENSIONS:
                self._process_text(path)

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            with self.stats_lock:
                self.stats.errors_encountered += 1

    def _process_text(self, path: Path):
        """Process text/markdown files"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if len(content) < MIN_NARRATIVE_LENGTH:
                return

            fragment = NarrativeExtractor.extract_from_text(content, str(path))
            if fragment:
                self.result_queue.put(fragment)
                logger.info(f"Found narrative: {path.name} (type: {fragment.fragment_type})")

        except Exception as e:
            logger.error(f"Error reading {path}: {e}")

    def _process_json(self, path: Path):
        """Process JSON files and extract narrative content"""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)

            fragments = NarrativeExtractor.extract_from_json(data, str(path))

            for fragment in fragments:
                if fragment.confidence_score > 0.3:  # Minimum confidence threshold
                    self.result_queue.put(fragment)
                    logger.info(f"Extracted from JSON: {path.name} ({fragment.fragment_type})")

        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {path}")
        except Exception as e:
            logger.error(f"Error processing JSON {path}: {e}")

    def _process_archive(self, path: Path):
        """
        Process archive files (ZIP/TAR) by peeking inside without full extraction.
        """
        try:
            with self.stats_lock:
                self.stats.archives_scanned += 1

            if path.suffix.lower() == '.zip':
                self._process_zip(path)
            elif path.suffix.lower() in {'.tar.gz', '.tgz', '.tar'}:
                self._process_tar(path)

        except Exception as e:
            logger.error(f"Error processing archive {path}: {e}")

    def _process_zip(self, path: Path):
        """Process ZIP archives"""
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                for member in zf.namelist():
                    member_path = Path(member)

                    # Skip directories
                    if member.endswith('/'):
                        continue

                    # Only process text files in archives
                    if member_path.suffix.lower() not in SCANNABLE_EXTENSIONS:
                        continue

                    # Check size
                    info = zf.getinfo(member)
                    if info.file_size > MAX_FILE_SIZE:
                        continue

                    # Extract and process
                    content = zf.read(member).decode('utf-8', errors='ignore')

                    if len(content) < MIN_NARRATIVE_LENGTH:
                        continue

                    fragment = NarrativeExtractor.extract_from_text(
                        content,
                        f"{path}:{member}"
                    )

                    if fragment:
                        self.result_queue.put(fragment)
                        logger.info(f"Found in archive: {path.name}/{member_path.name}")

        except Exception as e:
            logger.error(f"Error reading ZIP {path}: {e}")

    def _process_tar(self, path: Path):
        """Process TAR archives"""
        try:
            with tarfile.open(path, 'r:*') as tf:
                for member in tf.getmembers():
                    if not member.isfile():
                        continue

                    member_path = Path(member.name)

                    if member_path.suffix.lower() not in SCANNABLE_EXTENSIONS:
                        continue

                    if member.size > MAX_FILE_SIZE:
                        continue

                    # Extract and process
                    f = tf.extractfile(member)
                    if f:
                        content = f.read().decode('utf-8', errors='ignore')

                        if len(content) < MIN_NARRATIVE_LENGTH:
                            continue

                        fragment = NarrativeExtractor.extract_from_text(
                            content,
                            f"{path}:{member.name}"
                        )

                        if fragment:
                            self.result_queue.put(fragment)
                            logger.info(f"Found in archive: {path.name}/{member_path.name}")

        except Exception as e:
            logger.error(f"Error reading TAR {path}: {e}")


# =============================================================================
# REDIS ARCHAEOLOGIST
# =============================================================================

class RedisArchaeologist:
    """
    Scans Redis databases for narrative content in keys/values.
    """

    def __init__(self, host: str = 'localhost', port: int = 6379):
        self.host = host
        self.port = port

    def scan_databases(self, result_queue: Queue, stats: RecoveryStatistics, stats_lock: threading.Lock):
        """
        Scan Redis DB0 and DB1 for narrative content.
        """
        if not HAS_REDIS:
            logger.warning("Redis scanning skipped: redis-py not installed")
            return

        try:
            # Try to connect
            client = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            client.ping()

            logger.info("Connected to Redis, scanning databases...")

            # Scan DB0 and DB1
            for db in [0, 1]:
                client.select(db)
                self._scan_db(client, db, result_queue, stats, stats_lock)

        except redis.ConnectionError:
            logger.warning(f"Could not connect to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Redis scanning error: {e}")

    def _scan_db(
        self,
        client: redis.Redis,
        db: int,
        result_queue: Queue,
        stats: RecoveryStatistics,
        stats_lock: threading.Lock
    ):
        """Scan a single Redis database"""
        cursor = 0
        keys_scanned = 0

        while True:
            cursor, keys = client.scan(cursor, count=100)
            keys_scanned += len(keys)

            for key in keys:
                try:
                    value = client.get(key)
                    if not value:
                        continue

                    # Check if value contains narrative keywords
                    if len(value) < MIN_NARRATIVE_LENGTH:
                        continue

                    fragment = NarrativeExtractor.extract_from_text(
                        value,
                        f"redis:db{db}:{key}"
                    )

                    if fragment:
                        result_queue.put(fragment)
                        logger.info(f"Found in Redis DB{db}: {key}")

                except Exception as e:
                    logger.debug(f"Error scanning key {key}: {e}")

            if cursor == 0:
                break

        with stats_lock:
            stats.redis_keys_scanned += keys_scanned

        logger.info(f"Scanned {keys_scanned} keys in Redis DB{db}")


# =============================================================================
# MAIN COORDINATOR
# =============================================================================

class NarrativeHunter:
    """
    Main coordinator for narrative recovery operation.
    """

    def __init__(
        self,
        num_workers: int = 4,
        output_dir: str = "docs/narratives/staging",
        scan_redis: bool = True,
        quick_scan: bool = False
    ):
        self.num_workers = num_workers
        self.output_dir = Path(output_dir)
        self.scan_redis = scan_redis
        self.quick_scan = quick_scan

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Queues
        self.file_queue: Queue = Queue()
        self.result_queue: Queue = Queue()

        # Statistics
        self.stats = RecoveryStatistics()
        self.stats_lock = threading.Lock()

        # Deduplication
        self.dedup_engine = DeduplicationEngine()

    def run(self):
        """
        Execute the narrative hunting operation.
        """
        logger.info("="*60)
        logger.info("OPERATION NARRATIVE DRAGNET - Commencing")
        logger.info("="*60)

        start_time = time.time()

        # Phase 1: Discover files
        logger.info("Phase 1: Filesystem discovery")
        self._discover_files()

        # Phase 2: Launch workers
        logger.info(f"Phase 2: Launching {self.num_workers} HaikuWorker threads")
        workers = self._launch_workers()

        # Phase 3: Redis scanning (if enabled)
        if self.scan_redis:
            logger.info("Phase 3: Redis archaeological scan")
            archaeologist = RedisArchaeologist()
            archaeologist.scan_databases(self.result_queue, self.stats, self.stats_lock)

        # Phase 4: Wait for workers
        logger.info("Phase 4: Processing files...")
        self.file_queue.join()

        # Stop workers
        for _ in range(self.num_workers):
            self.file_queue.put(None)  # Poison pill

        for worker in workers:
            worker.join()

        # Phase 5: Process results
        logger.info("Phase 5: Processing results and deduplicating")
        recovered_fragments = self._process_results()

        # Phase 6: Write narratives to disk
        logger.info("Phase 6: Writing recovered narratives")
        self._write_narratives(recovered_fragments)

        # Phase 7: Generate report
        self.stats.scan_duration_seconds = time.time() - start_time
        logger.info("Phase 7: Generating recovery report")
        self._generate_report(recovered_fragments)

        logger.info("="*60)
        logger.info("OPERATION COMPLETE")
        logger.info(f"Narratives recovered: {self.stats.narratives_found}")
        logger.info(f"Duplicates removed: {self.dedup_engine.duplicates_removed}")
        logger.info(f"Total bytes recovered: {self.stats.total_bytes_recovered:,}")
        logger.info(f"Duration: {self.stats.scan_duration_seconds:.1f}s")
        logger.info("="*60)

    def _discover_files(self):
        """
        Discover files to scan.
        """
        search_paths = [
            Path("/mnt/c/Users/Setup/Downloads"),
            Path("/home/setup")
        ]

        for search_path in search_paths:
            if not search_path.exists():
                logger.warning(f"Path does not exist: {search_path}")
                continue

            logger.info(f"Scanning: {search_path}")

            # Walk directory tree
            for root, dirs, files in os.walk(search_path):
                root_path = Path(root)

                # Skip hidden directories and cache
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'node_modules', '__pycache__', 'venv', '.venv'}]

                for filename in files:
                    file_path = root_path / filename

                    # Check extension
                    ext = file_path.suffix.lower()

                    if self.quick_scan and ext in ARCHIVE_EXTENSIONS:
                        continue  # Skip archives in quick mode

                    if ext in SCANNABLE_EXTENSIONS or ext in ARCHIVE_EXTENSIONS:
                        self.file_queue.put(str(file_path))

        logger.info(f"Discovered {self.file_queue.qsize()} files to scan")

    def _launch_workers(self) -> List[HaikuWorker]:
        """Launch worker threads"""
        workers = []

        for i in range(self.num_workers):
            worker = HaikuWorker(
                worker_id=i,
                file_queue=self.file_queue,
                result_queue=self.result_queue,
                stats=self.stats,
                stats_lock=self.stats_lock
            )
            worker.start()
            workers.append(worker)

        return workers

    def _process_results(self) -> List[NarrativeFragment]:
        """
        Process results from queue and deduplicate.
        """
        recovered = []

        while not self.result_queue.empty():
            try:
                fragment = self.result_queue.get_nowait()

                # Check for duplicates
                is_dup, reason = self.dedup_engine.is_duplicate(fragment)

                if is_dup:
                    logger.debug(f"Duplicate removed: {fragment.source_path} ({reason})")
                    self.dedup_engine.duplicates_removed += 1
                    continue

                # Register and keep
                self.dedup_engine.register(fragment)
                recovered.append(fragment)

                with self.stats_lock:
                    self.stats.narratives_found += 1
                    self.stats.total_bytes_recovered += fragment.size_bytes

            except Empty:
                break

        return recovered

    def _write_narratives(self, fragments: List[NarrativeFragment]):
        """
        Write recovered narratives to staging directory.
        """
        for fragment in fragments:
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"recovered_{fragment.fragment_type}_{fragment.content_hash}_{timestamp}.md"
            output_path = self.output_dir / filename

            # Write file with metadata header
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Recovered Narrative: {fragment.fragment_type.title()}\n\n")
                f.write(f"**Source:** `{fragment.source_path}`\n")
                f.write(f"**Discovered:** {fragment.discovered_at}\n")
                f.write(f"**Keywords Matched:** {', '.join(set(fragment.keywords_matched[:10]))}\n")
                f.write(f"**Confidence:** {fragment.confidence_score:.2f}\n")
                f.write(f"**Content Hash:** {fragment.content_hash}\n")
                f.write(f"**Size:** {fragment.size_bytes:,} bytes\n\n")
                f.write("---\n\n")
                f.write(fragment.content)

            logger.info(f"Written: {filename}")

    def _generate_report(self, fragments: List[NarrativeFragment]):
        """
        Generate comprehensive recovery report.
        """
        report_path = self.output_dir / "NARRATIVE_RECOVERY_REPORT.md"

        # Group by type
        by_type: Dict[str, List[NarrativeFragment]] = defaultdict(list)
        for fragment in fragments:
            by_type[fragment.fragment_type].append(fragment)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# OPERATION NARRATIVE DRAGNET - Recovery Report\n\n")
            f.write(f"**Generated:** {datetime.utcnow().isoformat()}Z\n")
            f.write(f"**Duration:** {self.stats.scan_duration_seconds:.1f} seconds\n\n")

            f.write("## Executive Summary\n\n")
            f.write(f"- **Files Scanned:** {self.stats.files_scanned:,}\n")
            f.write(f"- **Archives Scanned:** {self.stats.archives_scanned:,}\n")
            f.write(f"- **Redis Keys Scanned:** {self.stats.redis_keys_scanned:,}\n")
            f.write(f"- **Narratives Found:** {self.stats.narratives_found}\n")
            f.write(f"- **Duplicates Removed:** {self.dedup_engine.duplicates_removed}\n")
            f.write(f"- **Total Bytes Recovered:** {self.stats.total_bytes_recovered:,}\n")
            f.write(f"- **Errors Encountered:** {self.stats.errors_encountered}\n\n")

            f.write("## Recovered Narratives by Type\n\n")
            for frag_type, frags in sorted(by_type.items()):
                f.write(f"### {frag_type.title()} ({len(frags)})\n\n")

                for fragment in sorted(frags, key=lambda x: x.confidence_score, reverse=True):
                    f.write(f"- **{Path(fragment.source_path).name}**\n")
                    f.write(f"  - Source: `{fragment.source_path}`\n")
                    f.write(f"  - Confidence: {fragment.confidence_score:.2f}\n")
                    f.write(f"  - Size: {fragment.size_bytes:,} bytes\n")
                    f.write(f"  - Hash: `{fragment.content_hash}`\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. Review recovered narratives in `docs/narratives/staging/`\n")
            f.write("2. Validate Episode numbers and chronology\n")
            f.write("3. Merge formatted versions into main narrative collection\n")
            f.write("4. Archive or delete low-confidence fragments\n")

        logger.info(f"Report written: {report_path}")


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Operation Narrative Dragnet - InfraFabric Narrative Recovery System"
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=8,
        help='Number of parallel worker threads (default: 8)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='docs/narratives/staging',
        help='Output directory for recovered narratives'
    )

    parser.add_argument(
        '--redis-scan',
        action='store_true',
        default=True,
        help='Enable Redis database scanning (default: enabled)'
    )

    parser.add_argument(
        '--no-redis',
        action='store_true',
        help='Disable Redis scanning'
    )

    parser.add_argument(
        '--quick-scan',
        action='store_true',
        help='Quick mode: skip archive processing'
    )

    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate report from existing staging directory'
    )

    args = parser.parse_args()

    # Create hunter
    hunter = NarrativeHunter(
        num_workers=args.workers,
        output_dir=args.output_dir,
        scan_redis=args.redis_scan and not args.no_redis,
        quick_scan=args.quick_scan
    )

    if args.report_only:
        logger.info("Report-only mode: regenerating report from existing files")
        # TODO: Implement report regeneration from existing files
        logger.warning("Report-only mode not yet implemented")
        return

    # Execute
    hunter.run()


if __name__ == '__main__':
    main()
