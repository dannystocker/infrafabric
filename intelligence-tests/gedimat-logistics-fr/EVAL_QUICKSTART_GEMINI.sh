#!/bin/bash

# Quick Start: Gemini Evaluation of Gedimat V2
# Target: 95%+ quality and evidence metric (up from 85%)

# Set repository URL
REPO_BASE="https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr"

echo "🔍 Starting Gemini Evaluation of Gedimat V2..."
echo ""
echo "Target: 95%+ quality and evidence metric (current: 85%)"
echo "Branch: gedimat-v2-clean"
echo ""

# Check if gemini-cli is available
if ! command -v gemini &> /dev/null; then
    echo "❌ gemini not found. Install first:"
    echo "   npm install -g @google/generative-ai-cli"
    exit 1
fi

# Create evaluation session
gemini chat --model gemini-2.0-flash-exp \
  "You are a rigorous technical auditor evaluating a French logistics optimization dossier. Target: 95%+ quality and evidence metric (currently 85%). Your mission:

1. VERIFY ZERO unsourced financial projections remain
2. VALIDATE all external benchmarks (Point P, Leroy Merlin, Castorama) with actual URLs
3. DEBUG methodology (8-pass IF.search, 40 agents, 26 voices)
4. PROVIDE concrete code snippets (Excel VBA, Python, SQL)
5. IDENTIFY gaps preventing 95%+ score

Be extremely skeptical. Every € amount needs a verifiable source. Provide actionable fixes with code.

---

# Gedimat V2 Critical Evaluation

**Context:**
- V1 score: 86/100 methodology, 40/100 financials (overall ~85%)
- Target: 95%+ quality and evidence
- Branch: gedimat-v2-clean

**Your Advantage over Codex:**
You have superior web search and multilingual capabilities. Use them to:
- Verify French business case studies (LSA Conso, Leroy Merlin reports)
- Find alternative benchmarks if provided ones fail
- Validate French language quality (Académie Française standards)

**Critical Questions:**
1. What prevents this from achieving 95%+ credibility?
2. Are the external benchmarks REAL and correctly cited?
3. Is the French professional enough for C-suite presentation?

I will feed you files sequentially. After reading all, provide:

1. IF.TTT Compliance Score (/100)
2. Evidence Quality Score (/100)
3. Methodology Soundness (/100)
4. Actionability Score (/100)
5. French Language Score (/100)
6. **Overall: __/100** (weighted average)

Then:
- List every blocker to 95%+
- Provide code snippets to fix
- Suggest alternative benchmarks (especially French sources)
- Correct French language errors

Ready? First file coming...

---

Read and analyze this comprehensive prompt file:
${REPO_BASE}/PROMPT_V2_FACTUAL_GROUNDED.md

Focus on:
- Any remaining unsourced Gedimat € amounts
- External benchmark citations (search to verify they exist!)
- ROI calculation formulas (are they clear?)
- French language quality (anglicisms, grammar, tone)

After reading, give initial impressions - what immediately blocks 95%+ score?"

echo ""
echo "✅ Session started. Continue conversation manually with:"
echo ""
echo "gemini chat --continue \"Read audit summary: ${REPO_BASE}/audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md\""
echo ""
echo "gemini chat --continue \"Read detailed audit: ${REPO_BASE}/audit/AUDIT_UNSOURCED_NUMBERS.md\""
echo ""
echo "gemini chat --continue \"Read data forms: ${REPO_BASE}/audit/GEDIMAT_DATA_VALIDATION_FORM.md\""
echo ""
echo "gemini chat --continue \"CRITICAL: Use web search to verify Point P, Leroy Merlin, Castorama benchmarks. Are they real?\""
echo ""
echo "gemini chat --continue \"Provide working code: Excel VBA macro, Python NPS script, SQL baseline query\""
echo ""
echo "gemini chat --continue \"FINAL REPORT: Scores (/100), Gap analysis to 95%+, Priority fixes, Code snippets\""
echo ""
