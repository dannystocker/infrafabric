# One-Liner Evaluation Commands

Target: **95%+ quality and evidence metric** (up from current 85%)

---

## Codex CLI (OpenAI GPT-4o)

### Single Command Evaluation

```bash
codex-cli chat --model gpt-4o-2024-11-20 --message "CRITICAL EVALUATION: Gedimat V2 Logistics Dossier

Target: 95%+ quality/evidence score (currently 85%)
Branch: github.com/dannystocker/infrafabric/gedimat-v2-clean

Read these 4 files from GitHub:
1. intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md
2. intelligence-tests/gedimat-logistics-fr/audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md
3. intelligence-tests/gedimat-logistics-fr/audit/AUDIT_UNSOURCED_NUMBERS.md
4. intelligence-tests/gedimat-logistics-fr/LAUNCH_V2_INSTRUCTIONS.md

MISSION:
1. Verify ZERO unsourced Gedimat financial projections remain (€ amounts, ROI, baselines)
2. Validate external benchmarks: Point P 2022 (12%), Leroy Merlin 2021 (8.5×), Castorama NPS 47 - are they REAL?
3. Identify gaps blocking 95%+ score
4. Provide code: Excel VBA scoring macro, Python NPS script, SQL baseline query
5. Rate: IF.TTT Compliance __/100, Evidence __/100, Methodology __/100, Actionability __/100, Overall __/100

OUTPUT FORMAT:
## Scores
- Overall: __/100
- Gap to 95%: __ points

## Blockers to 95%+
1. [Critical] ___ (Impact: -__pts, Fix: ___)
2. [High] ___ (Fix: ___)

## Code Snippets
[Excel VBA, Python, SQL]

## Verdict
Ready for deployment? [YES/NO/YES WITH FIXES]

Be ruthless - every unsourced number kills credibility."
```

---

## Gemini CLI (Google Gemini 2.0 Flash)

### Single Command Evaluation

```bash
gemini chat --model gemini-2.0-flash-exp "CRITICAL EVALUATION: Gedimat V2 Logistics Dossier

Target: 95%+ quality/evidence score (currently 85%)
Branch: github.com/dannystocker/infrafabric/gedimat-v2-clean

Read these files from GitHub raw:
1. https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md
2. https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md
3. https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/audit/AUDIT_UNSOURCED_NUMBERS.md

MISSION:
1. Verify ZERO unsourced Gedimat € amounts (ROI, savings, baselines)
2. USE WEB SEARCH to verify benchmarks: Point P 2022 (LSA Conso), Leroy Merlin 2021, Castorama NPS - are citations REAL?
3. Validate French language (Académie Française standards, no anglicisms)
4. Identify gaps blocking 95%+ score
5. Provide code: Excel VBA, Python NPS, SQL baseline

OUTPUT:
## Scores
- IF.TTT: __/100, Evidence: __/100, French: __/100, Overall: __/100
- Gap to 95%: __ points

## Critical Findings
1. [Benchmark Verification] Point P: ✅/❌ (actual source: ___)
2. [Unsourced Claims] Found __ violations in PROMPT_V2:line___
3. [French Errors] Anglicisms: ___ (corrections: ___)

## Code Snippets
[VBA macro, Python script, SQL query]

## Path to 95%+
Priority 1: ___
Priority 2: ___

LEVERAGE: Use your web search + multilingual strengths to verify French business sources."
```

---

## Alternative: Simple Question Format

If the above is too long, use this minimal version:

### Codex Minimal

```bash
codex-cli chat --message "Read github.com/dannystocker/infrafabric branch gedimat-v2-clean file intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md

Find ANY unsourced Gedimat € amounts, ROI projections, or baselines. Current score 85%, target 95%+. What blocks 95%?"
```

### Gemini Minimal

```bash
gemini chat "Read https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md

Web search: Verify Point P 2022 12% reduction (LSA Conso Mars 2023), Leroy Merlin 2021 ROI 8.5×. Are they real? Score 85% now, need 95%+. What's missing?"
```

---

## After Evaluation: Apply Fixes

Once you receive Codex and Gemini reports, create fixes:

```bash
cd /home/setup/infrafabric
git checkout gedimat-v2-clean

# Apply corrections they provide
# Then commit
git add intelligence-tests/gedimat-logistics-fr/
git commit -m "Apply Codex+Gemini fixes: Path to 95%+ quality

Fixes applied:
- [Codex] ___
- [Gemini] ___
- Code snippets added: ___
- Benchmark citations corrected: ___

Score: 85% → 95%+"

git push origin gedimat-v2-clean
```

---

## Expected Output Size

- **Codex:** 2,000-4,000 words
- **Gemini:** 2,000-4,000 words
- **Code:** 200-400 lines combined

Total evaluation time: 20-30 minutes (both)

---

## Success Criteria

After implementing fixes from both evaluators:

- ✅ Zero unsourced Gedimat financial claims
- ✅ All 3 external benchmarks verified with working URLs
- ✅ Working code provided (Excel VBA, Python, SQL)
- ✅ French quality validated (no critical anglicisms)
- ✅ Overall score: **95%+**
- ✅ Both evaluators say: "YES - ready to deploy"

Then proceed to fresh Claude Code Cloud session with confidence.
