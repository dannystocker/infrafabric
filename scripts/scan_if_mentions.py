#!/usr/bin/env python3
"""Mention scanner for InfraFabric IF patterns across text/code files."""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

TOKEN_PATTERN = re.compile(r"\bif[_\.\-][A-Za-z0-9_\.]*")
ALLOWED_EXTENSIONS = {".md", ".py", ".js", ".ts", ".yaml", ".yml", ".txt", ".go"}


def gather_mentions(root):
    root_path = Path(root).resolve()
    tokens = defaultdict(lambda: {"count": 0, "files": defaultdict(list)})
    cooccurrence = defaultdict(lambda: defaultdict(int))
    files_scanned = 0

    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue

        files_scanned += 1
        seen_tokens = set()
        for lineno, line in enumerate(lines, start=1):
            for match in TOKEN_PATTERN.finditer(line):
                token = match.group(0)
                tokens[token]["count"] += 1
                tokens[token]["files"][str(path.relative_to(root_path))].append(lineno)
                seen_tokens.add(token)
        for token in seen_tokens:
            for neighbor in seen_tokens:
                if token == neighbor:
                    continue
                cooccurrence[token][neighbor] += 1

    return {
        "root": str(root_path),
        "files_scanned": files_scanned,
        "tokens": {
            token: {
                "count": info["count"],
                "files": {
                    file: lines for file, lines in info["files"].items()
                },
            }
            for token, info in tokens.items()
        },
        "cooccurrence": {
            token: dict(neighbors) for token, neighbors in cooccurrence.items()
        },
    }


def write_dot(mentions, out_path):
    header = ["graph IFMentions {", "  node [shape=box, fontname=Helvetica];"]
    lines = header[:]
    added = set()
    for token, neighbors in mentions.get("cooccurrence", {}).items():
        for neighbor, count in neighbors.items():
            if token == neighbor:
                continue
            pair = tuple(sorted((token, neighbor)))
            if pair in added:
                continue
            lines.append(f"  \"{pair[0]}\" -- \"{pair[1]}\" [label=\"{count}\"];" )
            added.add(pair)
    lines.append("}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Scan repository for IF mentions.")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--out-dir", default=".", help="Directory to write artifact files")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mentions = gather_mentions(args.root)
    json_path = out_dir / "if_mentions.json"
    json_path.write_text(json.dumps(mentions, indent=2), encoding="utf-8")

    dot_path = out_dir / "if_mentions.dot"
    write_dot(mentions, dot_path)


if __name__ == "__main__":
    main()
