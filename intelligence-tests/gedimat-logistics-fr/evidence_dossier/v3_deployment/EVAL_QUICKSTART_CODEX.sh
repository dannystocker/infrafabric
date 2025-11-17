#!/bin/bash

# Quick Start: Codex Evaluation of Gedimat V2
# Target: 95%+ quality and evidence metric (up from 85%)

# Set repository URL
REPO_BASE="https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr"

echo "🔍 Starting Codex Evaluation of Gedimat V2..."
echo ""
echo "Target: 95%+ quality and evidence metric (current: 85%)"
echo "Branch: gedimat-v2-clean"
echo ""

# Check if codex-cli is available
if ! command -v codex-cli &> /dev/null; then
    echo "❌ codex-cli not found. Install first:"
    echo "   npm install -g @anthropic/codex-cli"
    exit 1
fi

# Create evaluation session
codex-cli chat --model gpt-4o-2024-11-20 \
  --system "You are a rigorous technical auditor evaluating a French logistics optimization dossier. Target: 95%+ quality and evidence metric (currently 85%). Your mission:

1. VERIFY ZERO unsourced financial projections remain
2. VALIDATE all external benchmarks (Point P, Leroy Merlin, Castorama) with actual URLs
3. DEBUG methodology (8-pass IF.search, 40 agents, 26 voices)
4. PROVIDE concrete code snippets (Excel VBA, Python, SQL)
5. IDENTIFY gaps preventing 95%+ score

Be extremely skeptical. Every € amount needs a verifiable source. Provide actionable fixes with code." \
  --message "# Gedimat V2 Critical Evaluation

**Context:**
- V1 score: 86/100 methodology, 40/100 financials (overall ~85%)
- Target: 95%+ quality and evidence
- Branch: gedimat-v2-clean

**Critical Question:**
What prevents this from achieving 95%+ credibility?

I will feed you files sequentially. After reading all, provide:

1. IF.TTT Compliance Score (/100)
2. Evidence Quality Score (/100)
3. Methodology Soundness (/100)
4. Actionability Score (/100)
5. **Overall: __/100** (weighted average)

Then:
- List every blocker to 95%+
- Provide code snippets to fix
- Suggest alternative benchmarks if current ones fail verification

Ready? First file coming..."

echo ""
echo "✅ Session started. Now feeding files..."
echo ""

# Feed PROMPT_V2 (main file)
echo "📄 Reading PROMPT_V2_FACTUAL_GROUNDED.md..."
codex-cli chat --continue --message "Read and analyze this comprehensive prompt file:

${REPO_BASE}/PROMPT_V2_FACTUAL_GROUNDED.md

Focus on:
- Any remaining unsourced Gedimat € amounts
- External benchmark citations (verify they're real)
- ROI calculation formulas (are they clear?)
- French language quality

After reading, give initial impressions - what immediately stands out as blocking 95%+ score?"

sleep 2

# Feed audit summary
echo "📄 Reading QUICK_REFERENCE_UNSOURCED_CLAIMS.md..."
codex-cli chat --continue --message "Read the audit summary of what was fixed v1→v2:

${REPO_BASE}/audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md

This shows the 8 'credibility bombs' that were eliminated. Verify they're ACTUALLY gone from PROMPT_V2."

sleep 2

# Feed detailed audit
echo "📄 Reading AUDIT_UNSOURCED_NUMBERS.md..."
codex-cli chat --continue --message "Read the complete technical audit:

${REPO_BASE}/audit/AUDIT_UNSOURCED_NUMBERS.md

Cross-reference: Are all 23 claims in this audit properly fixed in PROMPT_V2?"

sleep 2

# Feed data collection forms
echo "📄 Reading GEDIMAT_DATA_VALIDATION_FORM.md..."
codex-cli chat --continue --message "Read the data collection forms:

${REPO_BASE}/audit/GEDIMAT_DATA_VALIDATION_FORM.md

Evaluate: Can Gedimat coordinator realistically fill Section 1-6 in 30 minutes? Are instructions clear?"

sleep 2

# Feed launch instructions
echo "📄 Reading LAUNCH_V2_INSTRUCTIONS.md..."
codex-cli chat --continue --message "Read deployment guide:

${REPO_BASE}/LAUNCH_V2_INSTRUCTIONS.md

This explains why V2 exists and how to use it. Any gaps in deployment clarity?"

sleep 2

# Request external benchmark verification
echo "🔍 Requesting benchmark verification..."
codex-cli chat --continue --message "CRITICAL TASK: Verify the 3 external benchmarks cited in PROMPT_V2:

1. Point P 2022 (12% freight reduction) - Source: LSA Conso Mars 2023
2. Leroy Merlin 2021 (ROI 8.5×) - Source: Annual Report 2021 p.67
3. Castorama 2023 (NPS 47) - Source: Kingfisher Report

For EACH:
- Search for actual source URL
- Verify number is correct
- If not found, suggest alternative verifiable benchmark

This is THE most critical validation - if these are wrong, credibility = 0."

sleep 2

# Request code snippets
echo "💻 Requesting concrete code implementations..."
codex-cli chat --continue --message "Provide working code for tools mentioned in PROMPT_V2:

1. Excel VBA Macro: Scoring Multicritère (depot selection algorithm)
2. Python Script: NPS Survey Analysis
3. SQL Query: Médiafret Invoice Baseline Calculation
4. Excel Formulas: ROI Calculation Template

Make these production-ready - Gedimat should be able to use immediately."

sleep 2

# Final consolidation
echo "📊 Requesting final evaluation report..."
codex-cli chat --continue --message "FINAL REPORT:

Based on all files reviewed, provide:

## Scores

- IF.TTT Compliance: __/100
- Evidence Quality: __/100
- Methodology Soundness: __/100
- Actionability: __/100
- French Quality: __/100

**OVERALL: __/100**

## Gap Analysis: Path to 95%+

Current estimated score: __/100
Target: 95%+
Gap: __ points

**Blockers to 95%+ (prioritized):**

1. [Critical] ___
   - Impact: -__ points
   - Fix: ___
   - Code snippet: [if applicable]

2. [High] ___
   - Impact: -__ points
   - Fix: ___

3. [Medium] ___
   - Impact: -__ points
   - Fix: ___

## Recommended Actions (Priority Order)

1. **IMMEDIATE** (blocks deployment):
   - ___
   - ___

2. **HIGH** (needed for 95%+):
   - ___
   - ___

3. **NICE-TO-HAVE** (polish for 98%+):
   - ___

## Verdict

Ready to deploy to fresh Claude Code Cloud session? [YES / NO / YES WITH FIXES]

If NO: What MUST be fixed first?
If YES WITH FIXES: Provide corrected text/code inline.

---

**Confidence in Assessment:** [HIGH / MEDIUM / LOW]
**Would you stake your professional reputation on V2 quality?** [YES / NO / CONDITIONAL]
"

echo ""
echo "✅ Evaluation complete!"
echo ""
echo "Review Codex's final report and implement suggested fixes."
echo "Then run gemini version for second opinion."
