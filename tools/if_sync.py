#!/usr/bin/env python3
"""
InfraFabric Repository Sync (if_sync.py)

Goal
-----
Keep the "researcher-grade" derived artifacts in sync with the actual repo
contents, so the system can self-update whenever files change.

This script is intentionally conservative:
  - It never deletes user-authored entries.
  - It only auto-manages entries explicitly marked as `source: auto`.
  - It focuses on fast, incremental updates based on git status / mtimes.

Managed artifacts
-----------------
- A0_REPO_TREE          -> infrafabric-repo-tree.txt
- A2_DEPENDENCY_MAP     -> dependency_map.yaml
- M0_MIGRATION_MANIFEST -> migration_manifest.yaml
- INDEX_STATE           -> .if_sync_state.json

Usage
-----
From the repo root (/home/setup/infrafabric):

  # Dry run: show what would change
  python tools/if_sync.py --dry-run

  # Update derived artifacts in place
  python tools/if_sync.py

You can wire this into pre-commit, CI, or cron.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


REPO_ROOT = Path(__file__).resolve().parents[1]

REPO_TREE_PATH = REPO_ROOT / "infrafabric-repo-tree.txt"
DEPENDENCY_MAP_PATH = REPO_ROOT / "dependency_map.yaml"
MIGRATION_MANIFEST_PATH = REPO_ROOT / "migration_manifest.yaml"
STATE_PATH = REPO_ROOT / ".if_sync_state.json"

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    ".venvs",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "playwright-report",
}

# File extensions that we treat as "code/docs" for dependency mapping
TRACKED_EXTENSIONS = {".py", ".md", ".yml", ".yaml", ".json", ".txt"}


@dataclass
class FileState:
    path: str
    mtime: float
    size: int


@dataclass
class IndexState:
    last_run_timestamp: float
    files: Dict[str, FileState]

    @classmethod
    def empty(cls) -> "IndexState":
        return cls(last_run_timestamp=0.0, files={})


def debug(msg: str) -> None:
    """Lightweight debug logger."""
    print(f"[if_sync] {msg}")


def load_state() -> IndexState:
    if not STATE_PATH.exists():
        return IndexState.empty()
    try:
        with STATE_PATH.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        files = {
            k: FileState(**v) for k, v in raw.get("files", {}).items()
        }
        return IndexState(
            last_run_timestamp=raw.get("last_run_timestamp", 0.0),
            files=files,
        )
    except Exception:
        # On any corruption, start fresh but do not crash.
        return IndexState.empty()


def save_state(state: IndexState, dry_run: bool) -> None:
    if dry_run:
        debug("Dry run: not writing state file")
        return
    payload = {
        "last_run_timestamp": state.last_run_timestamp,
        "files": {k: asdict(v) for k, v in state.files.items()},
    }
    with STATE_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def walk_repo_tree() -> List[Path]:
    """Return all tracked files under REPO_ROOT respecting EXCLUDE_DIRS."""
    files: List[Path] = []
    for root, dirs, filenames in os.walk(REPO_ROOT):
        rel_root = Path(root).relative_to(REPO_ROOT)

        # Prune excluded directories in-place
        dirs[:] = [
            d for d in dirs
            if d not in EXCLUDE_DIRS
        ]

        for name in filenames:
            path = Path(root) / name
            # Skip our own derived artifacts
            if path == REPO_TREE_PATH or path == DEPENDENCY_MAP_PATH or path == MIGRATION_MANIFEST_PATH:
                continue
            files.append(path.relative_to(REPO_ROOT))
    return files


def build_repo_tree_text(files: List[Path]) -> str:
    """
    Build a simple text tree listing similar to `find`, sorted.
    We keep it minimal to stay diff-friendly.
    """
    lines = []
    for path in sorted(files):
        lines.append(str(path))
    return "\n".join(lines) + "\n"


def write_repo_tree(files: List[Path], dry_run: bool) -> None:
    text = build_repo_tree_text(files)
    if dry_run:
        debug(f"Dry run: would write {REPO_TREE_PATH.name} ({len(text.splitlines())} lines)")
        return
    with REPO_TREE_PATH.open("w", encoding="utf-8") as f:
        f.write(text)
    debug(f"Wrote {REPO_TREE_PATH.name} with {len(text.splitlines())} lines")


def get_git_changed_files() -> List[str]:
    """
    Use git status to detect changed files if git is available.
    Return paths relative to REPO_ROOT.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return []

    changed: List[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        # Format: "XY path"
        parts = line.strip().split(maxsplit=1)
        if len(parts) == 2:
            path = parts[1]
            # Ignore deletions here; we'll infer via index state
            changed.append(path)
    return changed


def compute_current_state(files: List[Path]) -> Dict[str, FileState]:
    state: Dict[str, FileState] = {}
    for path in files:
        full = REPO_ROOT / path
        try:
            st = full.stat()
        except FileNotFoundError:
            continue
        state[str(path)] = FileState(
            path=str(path),
            mtime=st.st_mtime,
            size=st.st_size,
        )
    return state


def diff_states(
    old: IndexState,
    new_files: Dict[str, FileState],
) -> Tuple[List[str], List[str], List[str]]:
    """
    Compare previous IndexState with new snapshot and return:
      - added files (relative paths)
      - modified files
      - removed files
    """
    old_paths = set(old.files.keys())
    new_paths = set(new_files.keys())

    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)

    modified: List[str] = []
    for path in sorted(old_paths & new_paths):
        old_entry = old.files[path]
        new_entry = new_files[path]
        if old_entry.mtime != new_entry.mtime or old_entry.size != new_entry.size:
            modified.append(path)

    return added, modified, removed


def load_yaml(path: Path) -> Any:
    if yaml is None:
        return None
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def dump_yaml(path: Path, data: Any, dry_run: bool) -> None:
    if yaml is None:
        debug("PyYAML not installed; skipping YAML writes")
        return
    if dry_run:
        debug(f"Dry run: would write {path.name}")
        return
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    debug(f"Wrote {path.name}")


def classify_path(path: str) -> str:
    """
    Very simple heuristic classification into tiers:
      - core | vertical | lib | evidence | archive

    This is intentionally conservative and should align with the
    higher-level architectural rules.
    """
    p = Path(path)
    parts = p.parts
    # Basic path-based hints
    if "data" in parts and "evidence" in parts:
        return "evidence"
    if "archive" in parts or "mission" in path.lower():
        return "archive"
    if "vertical" in path.lower() or "finance" in path.lower() or "legal" in path.lower():
        return "vertical"
    if "lib" in parts:
        return "lib"
    # Fallback: put Python under core if in src/core, else candidate vertical
    if len(parts) >= 2 and parts[0] == "src":
        if parts[1] == "core":
            return "core"
        if parts[1] == "verticals":
            return "vertical"
        if parts[1] == "lib":
            return "lib"
    # Default bucket for now
    return "archive"


def ensure_dependency_map_structure(data: Any) -> Dict[str, Any]:
    """
    Ensure dependency_map.yaml has the expected top-level structure:
      - mappings: list[entry]
      - unmapped_protocols: list
      - unclassified_files: list
    """
    if not isinstance(data, dict):
        data = {}
    data.setdefault("mappings", [])
    data.setdefault("unmapped_protocols", [])
    data.setdefault("unclassified_files", [])
    # Older format might be a bare list; normalize
    if isinstance(data.get("mappings"), list):
        pass
    elif isinstance(data.get("mappings"), dict):
        data["mappings"] = list(data["mappings"].values())
    return data


def update_dependency_map(
    added: List[str],
    modified: List[str],
    removed: List[str],
    dry_run: bool,
) -> None:
    """
    Update dependency_map.yaml in a conservative, auto-only way:
      - For new or modified files with tracked extensions, add/update
        entries with source: auto and status: candidate.
      - For removed files, mark corresponding auto entries as status: deprecated.
      - Never overwrite entries where source == "human".
    """
    existing = ensure_dependency_map_structure(load_yaml(DEPENDENCY_MAP_PATH))
    mappings: List[Dict[str, Any]] = existing.get("mappings", [])

    # Index by old_path for quick lookup
    index: Dict[str, Dict[str, Any]] = {}
    for entry in mappings:
        old_path = entry.get("old_path")
        if isinstance(old_path, str):
            index[old_path] = entry

    def should_track(path: str) -> bool:
        return Path(path).suffix in TRACKED_EXTENSIONS

    # Handle added / modified
    for path in added + modified:
        if not should_track(path):
            continue
        tier = classify_path(path)
        entry = index.get(path)
        if entry and entry.get("source") == "human":
            # Do not overwrite human-maintained entries
            continue
        if not entry:
            entry = {
                "old_path": path,
                "new_path": None,
                "tier": tier,
                "protocols": [],
                "dependencies": {
                    "imports": [],
                },
                "dependents": [],
                "status": "candidate",
                "confidence": 0.4,
                "rationale": "Auto-classified by if_sync based on path and extension.",
                "source": "auto",
            }
            mappings.append(entry)
            index[path] = entry
        else:
            # Update tier/status for auto entries
            if entry.get("source") == "auto":
                entry["tier"] = tier
                if entry.get("status") in (None, "unresolved", "deprecated"):
                    entry["status"] = "candidate"
                entry.setdefault("rationale", "Auto-updated by if_sync.")
                entry.setdefault("confidence", 0.4)

    # Handle removed
    for path in removed:
        entry = index.get(path)
        if not entry:
            continue
        if entry.get("source") == "human":
            # Log but do not overwrite human entries
            debug(f"File removed but human mapping retained: {path}")
            continue
        entry["status"] = "deprecated"
        entry.setdefault("rationale", "File removed from repo; entry marked deprecated by if_sync.")
        entry.setdefault("source", "auto")

    existing["mappings"] = mappings
    dump_yaml(DEPENDENCY_MAP_PATH, existing, dry_run=dry_run)


def ensure_migration_manifest_structure(data: Any) -> Dict[str, Any]:
    """
    Ensure migration_manifest.yaml has a consistent list-based structure.
    """
    if not isinstance(data, dict):
        data = {}
    data.setdefault("entries", [])
    return data


def update_migration_manifest(
    added: List[str],
    removed: List[str],
    dry_run: bool,
) -> None:
    """
    Very light-touch update for migration_manifest.yaml:
      - For new files that are not yet in the manifest, add a candidate
        entry with status: candidate and no hashes (to be filled during
        actual migration).
      - For removed files, mark existing auto entries as deprecated.
    """
    existing = ensure_migration_manifest_structure(load_yaml(MIGRATION_MANIFEST_PATH))
    entries: List[Dict[str, Any]] = existing.get("entries", [])

    index: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        old_path = entry.get("old_path")
        if isinstance(old_path, str):
            index[old_path] = entry

    for path in added:
        if path in index:
            continue
        if Path(path).suffix not in TRACKED_EXTENSIONS:
            continue
        entries.append(
            {
                "old_path": path,
                "new_path": None,
                "sha256_before": None,
                "sha256_after": None,
                "protocols": [],
                "tier": classify_path(path),
                "status": "candidate",
                "migration_date": None,
                "notes": "Placeholder created by if_sync; to be filled by migrate_with_provenance.py.",
                "source": "auto",
            }
        )

    for path in removed:
        entry = index.get(path)
        if not entry:
            continue
        if entry.get("source") == "human":
            debug(f"File removed but human manifest entry retained: {path}")
            continue
        entry["status"] = "deprecated"
        entry.setdefault("notes", "File removed from repo; entry marked deprecated by if_sync.")

    existing["entries"] = entries
    dump_yaml(MIGRATION_MANIFEST_PATH, existing, dry_run=dry_run)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="InfraFabric Repository Sync (auto-updates derived artifacts)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes without modifying files.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print additional debug information.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    if args.verbose:
        debug(f"Repo root: {REPO_ROOT}")

    if yaml is None:
        debug("Warning: PyYAML is not installed; YAML artifacts will not be written.")

    # 1) Walk tree
    files = walk_repo_tree()
    current_files_state = compute_current_state(files)

    # 2) Load previous state and diff
    previous_state = load_state()
    added, modified, removed = diff_states(previous_state, current_files_state)

    if args.verbose:
        debug(f"Added: {len(added)}, Modified: {len(modified)}, Removed: {len(removed)}")

    # 3) Regenerate repo tree unconditionally (cheap & deterministic)
    write_repo_tree(files, dry_run=args.dry_run)

    # 4) Update dependency_map.yaml
    update_dependency_map(added, modified, removed, dry_run=args.dry_run)

    # 5) Update migration_manifest.yaml
    update_migration_manifest(added, removed, dry_run=args.dry_run)

    # 6) Persist new state
    new_state = IndexState(
        last_run_timestamp=time.time(),
        files=current_files_state,
    )
    save_state(new_state, dry_run=args.dry_run)

    debug("Sync complete")


if __name__ == "__main__":
    main()

