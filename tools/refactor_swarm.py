#!/usr/bin/env python3
"""
Operation Packet Switch - Refactoring Swarm
============================================

Refactors InfraFabric codebase:
- IF.packet → IF.packet
- Packet → Packet (all variations)
- Renames files containing "packet" to "packet"

Uses 20 worker threads for parallel processing.
Supports dry-run mode and detailed progress reporting.

Author: Claude Code
Date: 2025-11-27
"""

import os
import re
import sys
import argparse
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
import time


@dataclass
class RefactorStats:
    """Track refactoring statistics."""
    files_processed: int = 0
    files_changed: int = 0
    files_renamed: int = 0
    total_replacements: int = 0
    replacements_by_pattern: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)


class RefactorSwarm:
    """Parallel refactoring engine using thread pool."""

    # Regex patterns in order of application
    PATTERNS = [
        (r'IF\.packet', 'IF.packet'),
        (r'class Packet\b', 'class Packet'),
        (r'Packet\(', 'Packet('),
        (r'"packet"', '"packet"'),
        (r"'packet'", "'packet'"),
        (r'packet_', 'packet_'),
        (r'\bParcel\b', 'Packet'),
        (r'\bparcel\b', 'packet'),
    ]

    # Directories to process
    TARGET_DIRS = [
        'src/',
        'restored_s2/',
        'docs/',
        'tests/',
        'tools/',
        'papers/',
    ]

    # Directories to exclude
    EXCLUDE_DIRS = {
        '.git',
        '__pycache__',
        'node_modules',
        '.venv',
        '.env',
        '.pytest_cache',
        '.idea',
        '.vscode',
    }

    # File patterns to exclude
    EXCLUDE_PATTERNS = {
        r'\.tar\.gz$',
        r'\.pyc$',
        r'\.pyo$',
        r'\.pyd$',
        r'\.so$',
        r'\.o$',
        r'\.a$',
        r'\.lib$',
        r'\.exe$',
        r'\.dll$',
    }

    def __init__(self, root_dir: str, dry_run: bool = False, num_workers: int = 20):
        """
        Initialize refactoring swarm.

        Args:
            root_dir: Root directory to start refactoring from
            dry_run: If True, don't write changes
            num_workers: Number of parallel worker threads
        """
        self.root_dir = Path(root_dir).resolve()
        self.dry_run = dry_run
        self.num_workers = num_workers
        self.stats = RefactorStats()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging."""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            format=log_format,
            level=logging.INFO,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.root_dir / 'refactor_swarm.log'),
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _should_exclude_dir(self, path: Path) -> bool:
        """Check if directory should be excluded."""
        for exclude in self.EXCLUDE_DIRS:
            if exclude in path.parts:
                return True
        return False

    def _should_exclude_file(self, path: Path) -> bool:
        """Check if file should be excluded."""
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, str(path)):
                return True
        return False

    def _is_binary_file(self, path: Path) -> bool:
        """Check if file appears to be binary."""
        try:
            with open(path, 'rb') as f:
                chunk = f.read(8192)
                if b'\x00' in chunk:
                    return True
        except Exception:
            return True
        return False

    def _get_files_to_process(self) -> List[Path]:
        """Collect all files to process."""
        files = []

        # Collect from target directories
        for target_dir in self.TARGET_DIRS:
            target_path = self.root_dir / target_dir
            if target_path.exists():
                for file_path in target_path.rglob('*'):
                    if self._is_processable_file(file_path):
                        files.append(file_path)

        # Collect root .md files
        for file_path in self.root_dir.glob('*.md'):
            if self._is_processable_file(file_path):
                files.append(file_path)

        return files

    def _is_processable_file(self, path: Path) -> bool:
        """Check if file should be processed."""
        if not path.is_file():
            return False

        if self._should_exclude_dir(path):
            return False

        if self._should_exclude_file(path):
            return False

        if self._is_binary_file(path):
            return False

        return True

    def _refactor_file_content(self, content: str) -> Tuple[str, int]:
        """
        Apply regex replacements to file content.

        Returns:
            Tuple of (modified_content, num_replacements)
        """
        replacements = 0
        modified = content

        for pattern, replacement in self.PATTERNS:
            regex = re.compile(pattern)
            matches = regex.findall(modified)
            num_matches = len(matches)

            if num_matches > 0:
                modified = regex.sub(replacement, modified)
                replacements += num_matches
                pattern_key = f"{pattern} → {replacement}"
                self.stats.replacements_by_pattern[pattern_key] += num_matches

        return modified, replacements

    def _refactor_file(self, file_path: Path) -> bool:
        """
        Refactor a single file.

        Returns:
            True if file was modified
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                original_content = f.read()

            # Apply replacements
            modified_content, num_replacements = self._refactor_file_content(original_content)

            # Only write if content changed
            if modified_content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)

                self.stats.files_changed += 1
                self.stats.total_replacements += num_replacements
                self.logger.info(f"✓ {file_path.relative_to(self.root_dir)} ({num_replacements} replacements)")
                return True

            return False

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.stats.errors.append(error_msg)
            self.logger.error(error_msg)
            return False

    def _get_files_to_rename(self) -> List[Path]:
        """Get all files that need renaming."""
        files_to_rename = []

        for target_dir in self.TARGET_DIRS:
            target_path = self.root_dir / target_dir
            if target_path.exists():
                for file_path in target_path.rglob('*'):
                    if file_path.is_file() and 'packet' in file_path.name.lower():
                        if not self._should_exclude_dir(file_path) and not self._should_exclude_file(file_path):
                            files_to_rename.append(file_path)

        # Root .md files
        for file_path in self.root_dir.glob('*.md'):
            if 'packet' in file_path.name.lower():
                files_to_rename.append(file_path)

        return files_to_rename

    def _rename_file(self, file_path: Path) -> bool:
        """
        Rename file from packet to packet.

        Returns:
            True if file was renamed
        """
        try:
            # Create new name (case-preserving replacement)
            new_name = file_path.name.replace('packet', 'packet').replace('Packet', 'Packet')

            if new_name == file_path.name:
                return False

            new_path = file_path.parent / new_name

            # Check if target exists
            if new_path.exists():
                self.logger.warning(f"Target exists, skipping: {new_path}")
                self.stats.skipped_files.append(str(file_path))
                return False

            if not self.dry_run:
                file_path.rename(new_path)

            self.stats.files_renamed += 1
            self.logger.info(f"✓ Renamed: {file_path.name} → {new_name}")
            return True

        except Exception as e:
            error_msg = f"Error renaming {file_path}: {str(e)}"
            self.stats.errors.append(error_msg)
            self.logger.error(error_msg)
            return False

    def run(self) -> RefactorStats:
        """Execute refactoring operation."""
        start_time = time.time()

        mode_str = "[DRY-RUN]" if self.dry_run else "[LIVE]"
        self.logger.info(f"Starting Operation Packet Switch {mode_str}")
        self.logger.info(f"Root directory: {self.root_dir}")
        self.logger.info(f"Worker threads: {self.num_workers}")

        # Phase 1: Collect files
        files_to_process = self._get_files_to_process()
        self.logger.info(f"Found {len(files_to_process)} files to process")

        # Phase 2: Parallel file refactoring
        self.logger.info("Phase 1: Refactoring file contents...")
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {executor.submit(self._refactor_file, f): f for f in files_to_process}

            for i, future in enumerate(as_completed(futures), 1):
                try:
                    future.result()
                    if i % 10 == 0:
                        self.logger.info(f"Progress: {i}/{len(files_to_process)} files processed")
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")

        self.logger.info(f"Phase 1 complete: {self.stats.files_changed} files modified")

        # Phase 3: File renaming
        self.logger.info("Phase 2: Renaming files...")
        files_to_rename = self._get_files_to_rename()
        self.logger.info(f"Found {len(files_to_rename)} files to rename")

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {executor.submit(self._rename_file, f): f for f in files_to_rename}

            for i, future in enumerate(as_completed(futures), 1):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}")

        self.logger.info(f"Phase 2 complete: {self.stats.files_renamed} files renamed")

        # Summary
        elapsed = time.time() - start_time
        self._print_summary(elapsed)

        return self.stats

    def _print_summary(self, elapsed: float) -> None:
        """Print refactoring summary."""
        summary = [
            "\n" + "=" * 70,
            "OPERATION PACKET SWITCH - SUMMARY",
            "=" * 70,
            f"Mode:              {'DRY-RUN' if self.dry_run else 'LIVE'}",
            f"Root directory:    {self.root_dir}",
            f"Elapsed time:      {elapsed:.2f}s",
            "",
            "RESULTS:",
            f"  Files processed:      {self.stats.files_processed + len(self._get_files_to_process())}",
            f"  Files modified:       {self.stats.files_changed}",
            f"  Files renamed:        {self.stats.files_renamed}",
            f"  Total replacements:   {self.stats.total_replacements}",
            "",
        ]

        if self.stats.replacements_by_pattern:
            summary.append("REPLACEMENTS BY PATTERN:")
            for pattern, count in sorted(self.stats.replacements_by_pattern.items()):
                summary.append(f"  {pattern}: {count}")
            summary.append("")

        if self.stats.errors:
            summary.append(f"ERRORS ({len(self.stats.errors)}):")
            for error in self.stats.errors[:10]:  # Show first 10
                summary.append(f"  - {error}")
            if len(self.stats.errors) > 10:
                summary.append(f"  ... and {len(self.stats.errors) - 10} more")
            summary.append("")

        if self.stats.skipped_files:
            summary.append(f"SKIPPED ({len(self.stats.skipped_files)}):")
            for skipped in self.stats.skipped_files[:10]:
                summary.append(f"  - {skipped}")
            if len(self.stats.skipped_files) > 10:
                summary.append(f"  ... and {len(self.stats.skipped_files) - 10} more")
            summary.append("")

        summary.append("=" * 70)

        output = "\n".join(summary)
        self.logger.info(output)
        print(output)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Operation Packet Switch - Refactor packet → packet',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run to preview changes
  %(prog)s --dry-run

  # Execute live refactoring with 20 workers
  %(prog)s

  # Use 10 workers instead of 20
  %(prog)s --workers 10

  # Refactor different root directory
  %(prog)s --root /path/to/directory
        """
    )

    parser.add_argument(
        '--root',
        type=str,
        default='/home/setup/infrafabric',
        help='Root directory to refactor (default: /home/setup/infrafabric)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing to disk'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=20,
        help='Number of worker threads (default: 20)'
    )

    args = parser.parse_args()

    # Validate root directory
    root_path = Path(args.root)
    if not root_path.exists():
        print(f"Error: Root directory does not exist: {args.root}", file=sys.stderr)
        sys.exit(1)

    if not root_path.is_dir():
        print(f"Error: Root path is not a directory: {args.root}", file=sys.stderr)
        sys.exit(1)

    # Create and run swarm
    swarm = RefactorSwarm(
        root_dir=str(root_path),
        dry_run=args.dry_run,
        num_workers=args.workers
    )

    stats = swarm.run()

    # Exit with status
    if stats.errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
