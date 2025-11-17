# External Validation Prompt: Gedimat V2 Factual Grounded

**Mission:** Critical evaluation + debugging + concrete improvements for logistics optimization dossier

**Context:** InfraFabric Gedimat V2 revision eliminated 8 "credibility bombs" (unsourced financial projections) from V1. Need external validation that V2 achieves IF.TTT (Traceable, Transparent, Trustworthy) compliance and provides actionable value.

---

## GitHub Repository Access

**Repository:** https://github.com/dannystocker/infrafabric
**Branch:** `gedimat-v2-clean`
**Path:** `intelligence-tests/gedimat-logistics-fr/`

---

## Files to Review (Priority Order)

### 1. CRITICAL FILES (Read First)

**`PROMPT_V2_FACTUAL_GROUNDED.md`** (48KB, 1,060 lines)
- Complete revised prompt for fresh Claude Code Cloud session
- 8-pass InfraFabric methodology (IF.search)
- 40-agent swarm architecture
- 26-voice validation (6 Guardians + 8 Philosophers + 12 Experts)

**`audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md`**
- Executive summary: 8 credibility bombs identified & eliminated
- 1-page brief showing v1 problems → v2 solutions

**`LAUNCH_V2_INSTRUCTIONS.md`**
- Comprehensive deployment guide
- Why V2 exists (credibility crisis scenario)
- How to use with fresh Claude session

### 2. AUDIT DOCUMENTATION

**`audit/AUDIT_UNSOURCED_NUMBERS.md`**
- Technical audit: All 23 unsourced claims mapped to file:line
- Risk classification (CRITICAL/HIGH/MEDIUM/LOW)
- Transformation methodology for each

**`audit/GEDIMAT_DATA_VALIDATION_FORM.md`**
- 6-section data collection tool
- Replaces unsourced baselines with client-fillable forms

**`audit/AUDIT_SUMMARY_CRITICAL_FINDINGS.md`**
- Detailed explanation of each credibility bomb
- External benchmarks with verifiable sources

### 3. CONTEXT FILES

**`README.md`**
- Project overview
- Business context (3 depots, external freight problem)

**`session-output/if_ttt_audit.md`**
- Original V1 output showing the 86/100 score
- Contains the problematic "ROI: 10× (50K€ / 5K€)" projections

---

## Evaluation Criteria

### A. IF.TTT Compliance Validation

**Task:** Verify ZERO unsourced Gedimat financial projections remain in V2

**Check for:**
1. Any € amount related to Gedimat without:
   - Data collection form reference, OR
   - External documented case with URL/DOI, OR
   - Explicit calculation formula with fillable fields

2. Any ROI/savings/costs claims that could be disputed if Gedimat management challenged source

3. Any "estimated" baselines for current Gedimat operations without "À mesurer avec [data source]" instruction

**Deliverable:**
```
IF.TTT COMPLIANCE SCORE: __/100

VIOLATIONS FOUND (if any):
- Location: PROMPT_V2_FACTUAL_GROUNDED.md:line___
  Claim: "___"
  Issue: "___"
  Suggested Fix: "___"

[Repeat for each violation]
```

---

### B. Methodology Soundness

**Task:** Debug the 8-pass IF.search architecture

**Questions:**
1. Are the 40 agents properly distributed across 8 passes?
2. Does each pass have clear: objective, agents, research tasks, deliverables, timing?
3. Are there logical gaps between passes (e.g., Pass 3 Rigor needs Pass 2 data)?
4. Is the 26-voice validation structured correctly (Guardian veto thresholds, philosophical grounding)?

**Deliverable:**
```
METHODOLOGY ISSUES:

Pass #: ___
Issue: "___"
Impact: "___"
Fix: "___"

[Code snippet or architectural diagram if helpful]
```

---

### C. External Benchmark Verification

**Task:** Validate the 3 external documented cases are real and correctly cited

**Cases to Verify:**
1. **Point P 2022**: 12% freight cost reduction
   - Claimed source: LSA Conso, Mars 2023, p.34
   - URL: https://www.lsa-conso.fr/point-p-optimisation-logistique-2023
   - **YOUR TASK**: Test URL, verify page exists, confirm 12% figure

2. **Leroy Merlin 2021**: ROI 8.5× on logistics optimization
   - Claimed source: Leroy Merlin Annual Report 2021, p.67
   - URL: [Check if provided in PROMPT_V2]
   - **YOUR TASK**: Find actual report, verify page 67, confirm ROI

3. **Castorama 2023**: NPS score 47
   - Claimed source: Kingfisher Annual Report 2023
   - URL: [Check if provided in PROMPT_V2]
   - **YOUR TASK**: Verify Kingfisher owns Castorama, find report, confirm NPS

**Deliverable:**
```
BENCHMARK VERIFICATION:

Case: Point P 2022
Status: ✅ VERIFIED / ❌ FAILED / ⚠️ PARTIALLY VERIFIED
Details: "___"
Actual Source Found: "___"
Discrepancies: "___"

[Repeat for each case]

RECOMMENDED FIXES:
[If any case failed, provide corrected citation or alternative benchmark]
```

---

### D. Actionability Analysis

**Task:** Evaluate if recommendations are implementable by Gedimat

**Focus Areas:**
1. **Quick Wins (0-3 months)**: Are they truly achievable in 90 days with stated resources?
2. **Data Collection Forms**: Can Angélique (coordinator) realistically fill Section 1-6 in 30 minutes?
3. **ROI Calculation Formulas**: Are they clear enough for non-technical CFO to compute?
4. **Tools/Templates**: Do Excel scoring sheets, NPS surveys, Gantt charts have enough detail to build?

**Deliverable:**
```
ACTIONABILITY ISSUES:

Recommendation: "Quick Win B: Scoring Multicritère"
Issue: "___"
Blocker Type: [UNCLEAR STEPS / MISSING TOOL / UNREALISTIC TIMELINE / INSUFFICIENT DETAIL]
Suggested Improvement: "___"
[Code snippet for Excel macro / Formula correction / Timeline adjustment]

[Repeat for each issue]
```

---

### E. French Language Quality

**Task:** Validate français parfait (Académie Française standards)

**Check for:**
1. Anglicisms (KPI → indicateurs, dashboard → tableau de bord, ROI → retour sur investissement?)
2. Sentence length (should average <20 words)
3. Clarity for non-expert (avoid jargon without explanation)
4. Professional tone (humble options vs arrogant prescriptions)

**Deliverable:**
```
FRENCH QUALITY ISSUES:

Location: PROMPT_V2:line___
Issue: "Anglicism: 'dashboard' should be 'tableau de bord'"
Corrected Text: "___"

[Provide 5-10 most critical corrections]
```

---

### F. Missing Elements / Gaps

**Task:** Identify what's missing that would strengthen the dossier

**Consider:**
1. Additional external benchmarks (need 3+, are there 5-7 for robustness?)
2. Risk mitigation (what if Gedimat data reveals baseline is WORSE than estimated?)
3. Sensitivity analysis (ROI calculation at 8%, 10%, 12% reduction scenarios)
4. Legal compliance (France transport regulations, GDPR for client data collection)
5. Competitive analysis (what if competitor franchises see this? IP protection?)

**Deliverable:**
```
CRITICAL GAPS:

Gap #1: "No sensitivity analysis for ROI calculations"
Impact: "CFO will ask 'what if we only achieve 6% reduction?'"
Proposed Solution: "Add Pass 7 section: ROI Scenarios (Conservative 6%, Base 10%, Optimistic 15%)"
[Code snippet or formula table]

[Repeat for each gap]
```

---

### G. Code Snippets / Tools

**Task:** Provide concrete implementations for vague recommendations

**Deliverables Requested:**

1. **Excel VBA Macro** for "Scoring Multicritère Dépôt Optimal"
   - Input: Volume, Distance, Délai, Priority
   - Output: Recommended depot (Lieu/Méru/Breuilpont)
   - Logic: Weighted scoring algorithm

2. **Python Script** for NPS Survey Analysis
   - Input: CSV with client responses (0-10 score)
   - Output: NPS score, Promoters/Passives/Detractors breakdown
   - Visualization: Matplotlib chart

3. **SQL Query** for Médiafret Invoice Analysis
   - Input: Database of invoices (date, amount, tonnage, route)
   - Output: Monthly baseline, Q1-Q3 trend, cost per tonne
   - Group by: Depot, freight type

4. **Excel Formula** for ROI Calculation
   - Clear formula with labeled cells
   - Example: `=((B2*B3)/B4)` where B2=Baseline, B3=Reduction%, B4=Investment

**Deliverable:**
```python
# Example: NPS Survey Analysis Script

import pandas as pd
import matplotlib.pyplot as plt

def calculate_nps(csv_file):
    """
    Calculate Net Promoter Score from survey responses

    Args:
        csv_file: Path to CSV with 'client_id' and 'score' columns

    Returns:
        NPS score (-100 to 100), breakdown dict
    """
    df = pd.read_csv(csv_file)

    promoters = len(df[df['score'] >= 9])
    passives = len(df[df['score'].between(7, 8)])
    detractors = len(df[df['score'] <= 6])
    total = len(df)

    nps = ((promoters - detractors) / total) * 100

    breakdown = {
        'nps': nps,
        'promoters': promoters,
        'passives': passives,
        'detractors': detractors,
        'total': total
    }

    return breakdown

# Usage:
# result = calculate_nps('gedimat_nps_survey.csv')
# print(f"NPS Score: {result['nps']:.1f}")
```

[Provide similar snippets for Excel VBA, SQL, formulas]

---

## Consolidation Request

**Task:** Synthesize all findings into executive summary

**Format:**
```markdown
# GEDIMAT V2 EXTERNAL VALIDATION REPORT

**Evaluator:** [Codex / Gemini]
**Date:** 2025-11-16
**Branch:** gedimat-v2-clean (commit a1b8d5a)

## Executive Summary

Overall Score: __/100
Credibility: [EXCELLENT / GOOD / NEEDS WORK / FAILED]
Actionability: [HIGH / MEDIUM / LOW]
IF.TTT Compliance: [FULL / PARTIAL / VIOLATED]

**Key Findings:**
- ✅ Strength: "___"
- ✅ Strength: "___"
- ⚠️ Issue: "___"
- ❌ Critical Flaw: "___"

**Recommended Actions:**
1. [Priority 1]: "___"
2. [Priority 2]: "___"
3. [Priority 3]: "___"

## Detailed Findings

[A. IF.TTT Compliance section]
[B. Methodology Soundness section]
[C. Benchmark Verification section]
[D. Actionability Analysis section]
[E. French Quality section]
[F. Missing Elements section]
[G. Code Snippets section]

## Conclusion

[2-3 paragraph assessment]

[Is V2 ready to deploy to fresh Claude Code Cloud session?]
[What must be fixed before deployment?]
[What could be improved in follow-up iteration?]

---

**Attachments:**
- Corrected PROMPT_V2 sections (if needed)
- Code snippets (Excel VBA, Python, SQL)
- Alternative benchmark sources (if original citations failed)
```

---

## How to Use This Prompt

### For Codex CLI:
```bash
codex-cli chat --model gpt-4o-2024-11-20 \
  --system "You are a rigorous technical auditor specializing in business process optimization, logistics, and French B2B consulting. Evaluate materials with extreme skepticism - every number needs a source, every claim needs evidence. Provide concrete code snippets and actionable fixes." \
  --message "$(cat /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/EVAL_PROMPT_CODEX_GEMINI.md)"
```

Then iteratively provide files:
```bash
# Provide PROMPT_V2
codex-cli chat --continue --message "Read this file from GitHub: https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md"

# Provide audit files
codex-cli chat --continue --message "Read this file: https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md"

# Continue with other files...
```

### For Gemini CLI:
```bash
gemini chat --model gemini-2.0-flash-exp \
  --system "You are a rigorous technical auditor specializing in business process optimization, logistics, and French B2B consulting. Evaluate materials with extreme skepticism - every number needs a source, every claim needs evidence. Provide concrete code snippets and actionable fixes." \
  --message "$(cat /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/EVAL_PROMPT_CODEX_GEMINI.md)"
```

Then feed files iteratively as above.

---

## Expected Output Size

**Codex Report:** 3,000-5,000 words
**Gemini Report:** 3,000-5,000 words
**Code Snippets:** 200-400 lines combined
**Corrected Text:** Highlighted diffs for PROMPT_V2

---

## Critical Success Factors

1. **Verify External Benchmarks**: Most important - if Point P/Leroy Merlin/Castorama citations are fake/wrong, V2 fails
2. **Find Credibility Bombs**: If ANY unsourced Gedimat € amounts remain, flag immediately
3. **Test Actionability**: Can Angélique actually DO the Quick Wins with provided info?
4. **Provide Code**: Don't just say "add Excel macro" - WRITE the VBA code
5. **Be Skeptical**: Assume every number is wrong until proven otherwise

---

## Questions to Answer

1. Would YOU stake your professional reputation on V2 claims if presenting to Gedimat board?
2. If Gedimat CFO challenges ONE number, which is most vulnerable?
3. What would make this dossier 100/100 instead of 95/100?
4. Is the French good enough for Académie Française member to approve?
5. Could competitor franchise (Point P, BigMat) reverse-engineer Gedimat strategy from this?

---

**End of Evaluation Prompt**

Meta-note: This prompt is self-contained. Evaluator (Codex/Gemini) should be able to complete assessment with ONLY GitHub files + this prompt + general knowledge. No InfraFabric context needed beyond what's explained inline.
