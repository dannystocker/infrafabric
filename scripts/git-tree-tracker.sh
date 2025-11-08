#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
BRANCHES_FILE="$ROOT/SWARM_BRANCHES.txt"

if [[ ! -f "$BRANCHES_FILE" ]]; then
  echo "No SWARM_BRANCHES.txt found at $BRANCHES_FILE" >&2
  exit 1
fi

git fetch origin --quiet

while read -r BR; do
  [[ -z "$BR" ]] && continue
  echo "=== Branch: $BR ==="
  git ls-remote --exit-code --heads origin "$BR" >/dev/null 2>&1 || { echo "(remote branch not found)"; echo; continue; }
  git diff --name-status "origin/master...origin/$BR" || true
  echo
done < "$BRANCHES_FILE"

