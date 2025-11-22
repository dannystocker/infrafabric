#!/bin/bash
# Quick test script for Gemini 1.5 Flash Archive Node
# Ensures API key is set and model is gemini-1.5-flash

export GEMINI_API_KEY="AIzaSyDSnIE3eKXoUmeydbUn9wdbwBxWPlJJgn4"

echo "================================================================"
echo "🔍 GEMINI 1.5 FLASH ARCHIVE NODE TEST"
echo "================================================================"
echo ""
echo "Model: gemini-1.5-flash (1M context window)"
echo "API Key: ${GEMINI_API_KEY:0:20}...${GEMINI_API_KEY: -4}"
echo ""

cd /home/setup/infrafabric/swarm-architecture

# Install dependencies if needed
if ! python -c "import google.generativeai" 2>/dev/null; then
    echo "📦 Installing google-generativeai..."
    pip install -q google-generativeai
fi

if ! python -c "import redis" 2>/dev/null; then
    echo "📦 Installing redis..."
    pip install -q redis
fi

echo "================================================================"
echo "Running single query test..."
echo "================================================================"
echo ""

python gemini_librarian.py --mode query \
  --question "What is the Alzheimer Worker pattern and how does it relate to the Goldfish Problem?"

echo ""
echo "================================================================"
echo "Test complete!"
echo "================================================================"
