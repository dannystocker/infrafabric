#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
OUTDIR="$ROOT/code/yologuard/repro/out/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUTDIR"
echo "Running benchmark → $OUTDIR"
python3 "$ROOT/code/yologuard/benchmarks/run_leaky_repo_v3_philosophical_fast_v2.py" | tee "$OUTDIR/benchmark.txt"

