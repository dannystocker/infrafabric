#!/bin/bash
# INFRAFABRIC HAIKU SWARM (Forensic Search Tool)
# Usage: ./scripts/haiku_swarm.sh
KEYWORDS="bull:ocr|OCRProcessor|Librarian|SynthesisEngine|yologuard"
DIRS=("." "../navidocs")
echo "🕷️  Scanning for Ghost Components..."
find "${DIRS[@]}" -maxdepth 5 -type f -not -path '*/.*' -print0 | xargs -0 grep -lE "$KEYWORDS"
