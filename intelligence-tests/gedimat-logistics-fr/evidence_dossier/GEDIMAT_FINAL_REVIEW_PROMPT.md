# Gedimat Logistics Dossier - Final Review Prompt

**Date:** 2025-11-17
**Evaluator:** External AI (GPT 5.1 high / Claude Opus / Gemini 2.5 Ultra)
**Target:** 95%+ credibility for Board presentation
**Context:** French construction materials distributor logistics optimization

---

## EXECUTIVE SUMMARY - WHAT TO EVALUATE

You are reviewing a **62-file, 36,328-line logistics optimization dossier** created using InfraFabric's IF.search 8-pass methodology with 42 Haiku agents and validated by a 26-voice Guardian Council (score: 76/100).

**Business Context:**
- **Company:** Gedimat (French building materials franchise)
- **Problem:** Optimize supplier pickups and external freight (>10 tonnes)
- **Constraint:** Internal drivers handle ≤10t economically; >10t requires expensive external freight (Médiafret)
- **Goal:** Reduce freight costs while maintaining/improving customer satisfaction

**Methodology:**
- IF.search (8 passes): Signal Capture → Primary Analysis → Rigor → Cross-Domain → Plateau → Debug → Deep Dive → Meta-Validation
- IF.swarm: 42 Haiku agents (€7-12 actual cost vs €50 budget)
- IF.guard: 26-voice validation (12 Gedimat experts + 6 Guardians + 8 Philosophers)

---

## YOUR EVALUATION MISSION

### Objectif Principal
**Score this dossier on credibility, feasibility, and presentation quality (0-100) for French C-suite Board presentation.**

### 4 Critical Dimensions to Evaluate

#### 1. CREDIBILITY & SOURCING (35 points)
**Questions:**
- Are all claims sourced with verifiable references? (IF.TTT standard: 25+ sources minimum)
- Are projected impacts (cost savings, satisfaction improvements) qualified appropriately?
  - ❌ BAD: "Réduction 12-15% affrètement" (stated as fact)
  - ✅ GOOD: "Réduction potentielle 10-15% affrètement (à confirmer après pilote 3 mois, inspiré cas Saint-Gobain)"
- Are academic/industry benchmarks cited correctly?
  - Check: VRP/TSP optimization models
  - Check: NPS/CSAT B2B standards (Kingfisher Group NPS 50, ADEO 11-15% cost reduction)
  - Check: Vendor pricing (Excel VBA €420-700, WMS €30K/year, implementation €25-250K)
- Are there any "credibility bombs" (unsourced projections presented as facts)?

**Red Flags:**
- ROI calculations without clear assumptions
- Savings percentages without pilot validation plans
- Timeline claims (e.g., "30 minutes data entry" → should be "moins d'une heure estimation à valider")

---

#### 2. FRENCH LANGUAGE QUALITY (20 points)
**Questions:**
- Is the document at Académie Française standard?
- Are anglicisms eliminated in executive sections?
  - ❌ REJECT: "Quick Win", "dashboard", "KPI", "benchmark"
  - ✅ ACCEPT: "Gain Rapide", "tableau de bord", "Indicateurs Clés de Performance (ICP)", "référence sectorielle"
- Grammar errors fixed?
  - Example: "remplir formulaires" → "remplir **les** formulaires"
- Is professional French tone consistent for C-suite audience?

**Check High-Visibility Sections:**
- Executive Summary
- Guardian Council validation
- Implementation roadmap
- Budget proposals

---

#### 3. OPERATIONAL FEASIBILITY (25 points)
**Questions:**
- Are quick wins (Phase 1: 30-90 days, <5K€) truly actionable without new technology?
  - Temporal consolidation (batch weekly orders)
  - Supplier SLA contracts (80%+ formalized)
  - NPS/CSAT surveys (baseline measurement)
  - Alert system (manual Excel → email notifications)
- Is the 3-phase roadmap realistic?
  - **Phase 1 (30-90j, <5K€):** Baseline + alerts
  - **Phase 2 (3-9m, 5-10K€):** Depot scoring pilot + process refinement
  - **Phase 3 (12-24m, budget TBD):** WMS/TMS if ROI demonstrated
- Are data collection plans specific enough?
  - Missing data (Type C): pickup times, freight costs by route, urgency causes
  - Collection methods: Driver forms, Médiafret API, customer surveys
- Does the Guardian Council 76/100 score reflect genuine concerns or rubber-stamping?
  - Check dissent documentation (Angélique on assistant training, Médiafret capacity validation)

---

#### 4. BOARD PRESENTATION READINESS (20 points)
**Questions:**
- Is there a 1-page executive summary for C-suite (no jargon, business focus only)?
  - ❌ REJECT: References to "40 agents", "26 voices", "IF.search 8 passes" methodology
  - ✅ ACCEPT: Problem statement (2 sentences), verified benchmarks (Saint-Gobain, ADEO), 3-phase recommendations, decision required (data authorization only)
- Are historical unsourced numbers (V1) removed from main document?
  - Check for: 50K€ savings, 10× ROI projections from earlier versions
  - These should be in appendix `audit/V1_V2_EVOLUTION.md` only
- Is the document structure clear for non-technical Board members?
  - Diagnostic → Strategy → Tools → Validation → Roadmap
- Are budgets and timelines conservative enough for CFO scrutiny?

---

## SCORING GUIDANCE

### Score Interpretation
- **95-100:** Production-ready, Board-presentable, minimal adjustments needed
- **90-94:** Strong foundation, minor polish required (language, sourcing)
- **85-89:** Good analysis, moderate credibility gaps (projections too strong, some unsourced claims)
- **78-84:** Solid methodology, significant presentation issues (anglicisms, jargon, missing Board summary)
- **<78:** Major rework needed (credibility bombs, feasibility concerns, poor French quality)

### Reference Benchmarks
- **V1 (Initial):** 86/100 methodology, 40/100 financials (8 unsourced "credibility bombs")
- **V2 (Factual Grounded):** 78/100 (Codex GPT 5.1), 90/100 (GPT 5.1 high)
  - Fixed: All unsourced Gedimat projections eliminated
  - Created: Data collection forms, vendor pricing, external benchmarks
- **V3 Target:** 95%+ (4 specific fixes: temper impact claims, Board summary, move V1 tables, eliminate anglicisms)

---

## EVALUATION PROTOCOL

### Step 1: Sample High-Risk Sections (15 min)
Read these sections for credibility issues:
1. **Executive Summary** (if exists) - Check for jargon, unsourced claims
2. **PASS2 Cost Analysis** - Verify freight cost projections are sourced
3. **PASS4 Finance ROI** - Check savings calculations have clear assumptions
4. **PASS7 Tools** - Confirm Excel scoring formula is explained and justified
5. **PASS8 Guardian Council** - Verify 76/100 score reflects genuine debate (check dissent documentation)

### Step 2: Language Quality Spot Check (10 min)
Search for these anglicisms in executive sections:
- "Quick Win" / "quick win"
- "dashboard"
- "KPI" (without "Indicateurs Clés de Performance" expansion)
- "benchmark"
- "workflow"
- "checklist"

Count occurrences in first 300 lines of main dossier.

### Step 3: Board Readiness Check (10 min)
1. Does `EXECUTIVE_SUMMARY_BOARD.md` exist?
   - If NO: **automatic -15 points** (Board cannot digest 62 files)
2. If YES, verify:
   - ✅ 1 page maximum
   - ✅ Uses verified benchmarks (Saint-Gobain, ADEO) with sources
   - ✅ Zero methodology jargon ("40 agents", "IF.search")
   - ✅ Professional French C-suite tone
   - ✅ Clear decision required (data authorization, no immediate budget)

### Step 4: Credibility Deep Dive (20 min)
Choose 5 random quantified claims and verify:
- **Claim 1:** "-12-15% freight cost reduction"
  - Is it qualified? ("potentiel", "à confirmer après pilote")
  - Is source cited? (Saint-Gobain case, ADEO data, or explicit "À mesurer avec données 2024")
- **Claim 2:** "30 minutes data entry time"
  - Qualified as estimate? ("moins d'une heure estimation à valider")
- **Claim 3:** Vendor pricing (e.g., "Excel VBA €420-700")
  - Source cited? (Codeur.com, Free-Work, Generix Group, Sitaci)
- **Claim 4:** NPS/CSAT targets (e.g., "NPS 30 → 50 target")
  - Benchmarked? (Kingfisher Group NPS 50, ADEO data)
- **Claim 5:** Implementation timeline (e.g., "Phase 1: 30-90 days")
  - Justified with task breakdown and resource plan?

### Step 5: Final Scoring (5 min)
Aggregate:
- Credibility & Sourcing: __/35
- French Language Quality: __/20
- Operational Feasibility: __/25
- Board Presentation Readiness: __/20
- **TOTAL: __/100**

---

## OUTPUT FORMAT

```markdown
# Gedimat Logistics Dossier - External Evaluation

**Evaluator:** [Your model name]
**Date:** [Timestamp]
**Score:** __/100

## Dimension Scores
1. Credibility & Sourcing: __/35
2. French Language Quality: __/20
3. Operational Feasibility: __/25
4. Board Presentation Readiness: __/20

## Key Findings

### Strengths (Top 3)
1. [Specific strength with example]
2. [Specific strength with example]
3. [Specific strength with example]

### Critical Issues (Must Fix Before Board Presentation)
1. [Issue with severity: CRITICAL / HIGH / MEDIUM]
   - **Evidence:** [Quote or reference]
   - **Fix:** [Specific action]
2. [Issue 2...]
3. [Issue 3...]

### Minor Improvements (Nice to Have)
1. [Improvement 1]
2. [Improvement 2]
3. [Improvement 3]

## Credibility Audit (5 Random Claims)
| Claim | Qualified? | Sourced? | Grade |
|-------|------------|----------|-------|
| [Claim 1] | ✅/❌ | ✅/❌ | A/B/C/D/F |
| [Claim 2] | ✅/❌ | ✅/❌ | A/B/C/D/F |
| [Claim 3] | ✅/❌ | ✅/❌ | A/B/C/D/F |
| [Claim 4] | ✅/❌ | ✅/❌ | A/B/C/D/F |
| [Claim 5] | ✅/❌ | ✅/❌ | A/B/C/D/F |

## Anglicisms Found (First 300 Lines)
- "Quick Win": __ occurrences
- "dashboard": __ occurrences
- "KPI" (unexpanded): __ occurrences
- "benchmark": __ occurrences
- **Total:** __ anglicisms (TARGET: 0 in executive sections)

## Board Executive Summary Status
- [ ] EXISTS (1 page, C-suite tone, zero jargon)
- [ ] MISSING (automatic -15 points)

## Recommendation
- [ ] **APPROVE for Board:** 95%+ score, production-ready
- [ ] **MINOR POLISH:** 90-94%, fix language/sourcing issues (1-2 hours)
- [ ] **MODERATE REWORK:** 85-89%, address credibility gaps (4-6 hours)
- [ ] **MAJOR REVISION:** <85%, fundamental issues need resolution

## Comparison to V2 Baseline (90/100)
[Did V3 improve on the 4 known issues?]
1. Impact claims tempered? ✅/❌
2. Board executive summary created? ✅/❌
3. V1 tables moved to appendix? ✅/❌
4. Anglicisms eliminated? ✅/❌

## Final Verdict
[2-3 sentence summary: Is this dossier ready for Gedimat Board presentation? What's the single most important fix if score <95?]
```

---

## FILES TO EVALUATE

**Primary Dossier:**
- `PROMPT_V3_GITHUB_READY.md` (if exists, ~48KB)
- OR `PROMPT_V2_FACTUAL_GROUNDED.md` (baseline, 1,060 lines)

**Board Summary:**
- `EXECUTIVE_SUMMARY_BOARD.md` (MUST exist for 95%+ score)

**Supporting Evidence:**
- `PASS8_GUARDIAN_COUNCIL_26_VOIX_VALIDATION.md` (validation report with 76/100 score)
- `benchmarks/POINT_P_ALTERNATIVE_VERIFIED.md` (Saint-Gobain case)
- `benchmarks/LEROY_MERLIN_2021_VERIFIED.md` (ADEO metrics)
- `benchmarks/KINGFISHER_GROUP_NPS_VERIFIED.md` (NPS reference)
- `EVALUATION_FINDINGS_SUMMARY.md` (vendor pricing sources)

**Audit Trail:**
- `audit/V1_V2_EVOLUTION.md` (historical comparison, should NOT be in main dossier)
- `V3_COMPLETION_REPORT.md` (if exists, validation checklist)

---

## CONTEXT: Why This Evaluation Matters

This dossier will be presented to Gedimat's Board of Directors. **One unsourced claim can destroy credibility and delay the project for weeks** while sourcing is re-done.

**Historical Example (V1 Failure):**
- V1 claimed "50K€ savings, 10× ROI" without sources
- CFO challenged: "Where's the proof?"
- Entire project stalled

**V2 Success (90/100):**
- Eliminated all unsourced Gedimat projections
- Added verified external benchmarks (Saint-Gobain, ADEO)
- Created data collection forms for missing data
- Result: Credible foundation, but presentation issues remained

**V3 Goal (95%+):**
- Temper impact claims ("potentiel", "à confirmer")
- Add Board executive summary (1 page, zero jargon)
- Remove V1 historical numbers from main document
- Eliminate anglicisms in French document

---

## EVALUATOR INDEPENDENCE

**Important:** You are an **external validator**, not the document author. Your role is to:
1. Find credibility gaps the author missed
2. Identify presentation issues that would concern a CFO
3. Verify French language quality meets C-suite standards
4. Assess operational feasibility with healthy skepticism

**Do NOT:**
- Rubber-stamp with high scores without finding issues
- Accept vague claims ("significant savings", "improved satisfaction") without quantification
- Overlook anglicisms or grammatical errors
- Assume Board members will tolerate methodology jargon

---

## SUCCESS CRITERIA (95%+ Target)

✅ **All percentage claims** qualified with "potentiel / à confirmer après pilote"
✅ **All euro amounts** either sourced (vendor pricing) OR labeled "À mesurer avec données 2024"
✅ **Executive summary** created (1 page, C-suite tone, verified benchmarks only)
✅ **Zero anglicisms** in executive sections (first 300 lines)
✅ **V1 comparisons** moved to audit appendix, not in main document
✅ **Guardian Council 76/100** reflects genuine debate (dissent documented)
✅ **French quality** at Académie Française standard (no grammar errors)
✅ **Operational feasibility** validated by 12 Gedimat experts (not just consultants)

---

**Ready to evaluate? Start with Step 1: Sample High-Risk Sections.**
