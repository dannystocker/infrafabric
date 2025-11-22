#!/usr/bin/env python3
"""Update tracked text references based on a CSV of moves."""
import argparse
import csv
import shutil
from collections import defaultdict
from pathlib import Path

TEXT_FILE_EXTENSIONS = {
    ".md",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".cfg",
    ".ini",
    ".rst",
    ".sh",
    ".html",
    ".css",
    ".env",
}


def load_mapping(path):
    pairs = []
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or len(row) < 2:
                continue
            old_path = row[0].strip()
            new_path = row[1].strip()
            if old_path.lower() == "old_path" and new_path.lower() == "new_path":
                continue
            if not old_path or not new_path:
                continue
            pairs.append((old_path, new_path))
    return pairs


def eligible_files(root):
    root_path = Path(root).resolve()
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if path.name.endswith(".bak"):
            continue
        if path.suffix.lower() not in TEXT_FILE_EXTENSIONS:
            continue
        yield path


def main():
    parser = argparse.ArgumentParser(description="Replace references according to moves CSV.")
    parser.add_argument("--mapping", required=True, help="CSV file listing old_path,new_path")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--dry-run", action="store_true", help="Show replacements without writing")
    args = parser.parse_args()

    mapping_path = Path(args.mapping).resolve()
    if not mapping_path.is_file():
        raise SystemExit(f"Mapping file not found: {mapping_path}")

    replacements = load_mapping(mapping_path)
    if not replacements:
        print("No valid mappings found in CSV.")
        return

    changes = defaultdict(list)
    root_path = Path(args.root).resolve()
    for path in eligible_files(root_path):
        relative = path.relative_to(root_path)
        content = path.read_text(encoding="utf-8", errors="ignore")
        new_content = content
        for old, new in replacements:
            new_content = new_content.replace(old, new)
        if new_content != content:
            changes[path].append((content, new_content))

    if not changes:
        print("No files needed updating.")
        return

    for path, diffs in changes.items():
        new_content = diffs[-1][1]
        if args.dry_run:
            print(f"[dry-run] {path.relative_to(root_path)} would be updated")
            continue
        bak_path = path.with_name(f"{path.name}.bak")
        shutil.copy2(path, bak_path)
        path.write_text(new_content, encoding="utf-8")
        print(f"Updated {path.relative_to(root_path)} (backup at {bak_path.relative_to(root_path)})")


if __name__ == "__main__":
    main()
