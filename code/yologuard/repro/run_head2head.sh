#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
OUTDIR="$ROOT/code/yologuard/repro/out/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUTDIR"
echo "Running head-to-head (requires gitleaks & trufflehog in PATH) → $OUTDIR"
python3 "$ROOT/code/yologuard/harness/head2head.py" \
  --config "$ROOT/code/yologuard/harness/corpus_config.json" \
  --workdir /tmp/yolo-corpus \
  --json "$OUTDIR/head2head.json" \
  --md "$OUTDIR/head2head.md"

