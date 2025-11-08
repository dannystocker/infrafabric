#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
OUTDIR="$ROOT/code/yologuard/repro/out/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUTDIR"
echo "Running forensics profile → $OUTDIR"
python3 "$ROOT/code/yologuard/src/IF.yologuard_v3.py" \
  --scan "$ROOT/code/yologuard/benchmarks/leaky-repo" \
  --profile forensics \
  --json "$OUTDIR/ief.json" \
  --sarif "$OUTDIR/ief.sarif" \
  --graph-out "$OUTDIR/indra.json" \
  --manifest "$OUTDIR/ief.manifest" \
  --pq-report "$OUTDIR/pq.json" \
  --stats | tee "$OUTDIR/forensics.txt"

