# Gedimat V2 External Validation Guide

**Status:** Ready for Codex + Gemini evaluation
**Target:** 95%+ quality and evidence score (up from 85%)
**Branch:** `gedimat-v2-clean` on GitHub

---

## Quick Start

### Recommended: French Evaluation (Best Results)

French evaluation catches:
- Anglicisms invisible to English reviewers
- French business source verification (LSA Conso, Leroy Merlin reports)
- Tone appropriate for French C-suite presentation
- Grammar nuances critical for credibility

**Use these commands:**

```bash
# Copy-paste from EVAL_ONELINER_FRENCH.md
# Codex: Long French prompt
# Gemini: Long French prompt with web search
```

### Alternative: English Evaluation

If French not available:

```bash
# Copy-paste from EVAL_ONELINER_COMMANDS.md
# Codex: Technical audit focus
# Gemini: Web search benchmark verification
```

---

## Evaluation Files

### For You to Run

1. **`EVAL_ONELINER_FRENCH.md`** ⭐ RECOMMENDED
   - Complete French evaluation prompts
   - Codex + Gemini one-liners
   - Why French > English for this project

2. **`EVAL_ONELINER_COMMANDS.md`**
   - English evaluation prompts
   - Shorter commands
   - Less effective for French language validation

3. **`EVAL_QUICKSTART_CODEX.sh`**
   - Automated Codex evaluation script
   - Sequential file feeding
   - Can be adapted for French

4. **`EVAL_QUICKSTART_GEMINI.sh`**
   - Automated Gemini evaluation script
   - Web search integration

### For Evaluators to Review

5. **`EVAL_PROMPT_CODEX_GEMINI.md`**
   - Comprehensive evaluation criteria (English)
   - 7 sections (IF.TTT, Methodology, Benchmarks, etc.)
   - Detailed instructions for evaluators

---

## What Evaluators Will Check

### Critical (Blocks 95%+)

1. **IF.TTT Compliance**
   - ❌ ANY unsourced Gedimat € amounts = FAIL
   - Example: "50K€ gains" without invoice reference

2. **External Benchmark Verification**
   - Point P 2022: 12% reduction (LSA Conso Mars 2023)
   - Leroy Merlin 2021: ROI 8.5× (Annual Report p.67)
   - Castorama 2023: NPS 47 (Kingfisher Report)
   - **Must verify URLs work and numbers correct**

3. **French Language Quality**
   - Anglicisms (dashboard, KPI, quick win)
   - Grammar errors
   - Inappropriate tone for conseil d'administration

### Important (Needed for 95%+)

4. **Code Snippets**
   - Excel VBA macro (depot scoring)
   - Python script (NPS analysis)
   - SQL query (baseline calculation)

5. **Actionability**
   - Can Angélique fill data forms in 30 min?
   - Are ROI formulas clear for CFO?
   - Quick Wins achievable in 90 days?

6. **Methodology Soundness**
   - 8-pass IF.search properly structured?
   - 40 agents distributed correctly?
   - 26-voice validation coherent?

---

## Expected Output

After running both Codex and Gemini evaluations:

```markdown
## Codex Report (2,000-4,000 words)
- Scores: IF.TTT __/100, Evidence __/100, Overall __/100
- Gap to 95%: __ points
- Critical violations found: __
- Code snippets provided: [VBA, Python, SQL]
- Verdict: YES / NO / YES WITH FIXES

## Gemini Report (2,000-4,000 words)
- Scores: French __/100, Benchmarks verified __/3, Overall __/100
- Web search results: Point P ✅/❌, Leroy Merlin ✅/❌, Castorama ✅/❌
- Anglicisms found: __ (corrections provided)
- Alternative French benchmarks: __
- Verdict: YES / NO / YES WITH FIXES
```

---

## How to Apply Fixes

1. **Review both reports**
   - Identify overlapping issues (high priority)
   - Note contradictions (investigate further)

2. **Fix PROMPT_V2_FACTUAL_GROUNDED.md**
   ```bash
   cd /home/setup/infrafabric
   git checkout gedimat-v2-clean

   # Edit PROMPT_V2 with corrections
   nano intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md
   ```

3. **Add code snippets**
   ```bash
   # Create tools/ directory if needed
   mkdir -p intelligence-tests/gedimat-logistics-fr/tools/

   # Add Excel VBA macro
   # Add Python NPS script
   # Add SQL baseline query
   ```

4. **Update benchmarks if needed**
   - If Point P citation failed, use alternative Codex/Gemini suggested
   - Update URLs to verified sources
   - Adjust percentages if actual numbers differ

5. **Commit and push**
   ```bash
   git add intelligence-tests/gedimat-logistics-fr/
   git commit -m "Apply Codex+Gemini fixes: Path to 95%+

   Corrections:
   - Benchmarks verified: [list URLs]
   - Anglicisms removed: [count]
   - Code added: VBA macro + Python NPS + SQL baseline
   - Unsourced claims fixed: [count]

   Score: 85% → 96% estimated"

   git push origin gedimat-v2-clean
   ```

6. **Re-evaluate**
   - Run Codex/Gemini again on updated version
   - Confirm 95%+ achieved
   - Get YES verdict from both

---

## Success Criteria

Before deploying to fresh Claude Code Cloud session, confirm:

- ✅ **Codex verdict:** YES (or YES WITH MINOR FIXES)
- ✅ **Gemini verdict:** YES (or YES WITH MINOR FIXES)
- ✅ **Overall score:** ≥95/100 from both evaluators
- ✅ **Benchmarks:** All 3 external cases verified with working URLs
- ✅ **IF.TTT:** Zero unsourced Gedimat financial projections
- ✅ **French:** No critical anglicisms or grammar errors
- ✅ **Code:** All 3 tools provided (VBA, Python, SQL)

Then you can confidently:

```bash
# Launch fresh Claude Code Cloud session
# Provide files:
# 1. PROMPT_V2_FACTUAL_GROUNDED.md (corrected)
# 2. CONTEXTE_ANGELIQUE.txt
# 3. GARDIENS_PROFILS.md
# 4. CONSEIL_26_VOIX.md

# Claude will execute 8-pass methodology
# Produce 60-85 page dossier with 95%+ credibility
```

---

## Timeline

- **Evaluation:** 20-30 minutes (both Codex + Gemini)
- **Review reports:** 15-20 minutes
- **Apply fixes:** 1-2 hours
- **Re-evaluation:** 15-20 minutes
- **Total:** ~2.5-3 hours to 95%+

---

## Questions?

See:
- `LAUNCH_V2_INSTRUCTIONS.md` - Why V2 exists
- `audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md` - What was fixed v1→v2
- `PROMPT_V2_FACTUAL_GROUNDED.md` - The actual prompt to evaluate

---

**Ready to evaluate? Start with `EVAL_ONELINER_FRENCH.md` for best results! 🇫🇷**
