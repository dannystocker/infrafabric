# Gedimat V3 Final Sprint - Claude Code Cloud Deployment

**Mission:** Build production-ready V3 logistics optimization dossier (90/100 → 95%+ target)
**Budget:** 40 Haiku 4.5 agents + Sonnet 4.5 architecture
**Estimated Time:** 2-3 hours
**Status:** 8/12 issues already researched, 4 actionable fixes remaining

---

## Quick Context

**What This Is:**
- French B2B logistics optimization for Gedimat (building materials distributor, 3 depots)
- IF.search 8-pass methodology with IF.TTT (Traceable, Transparent, Trustworthy) compliance
- External validation: Codex GPT-4o (78/100), GPT 5.1 high (90/100)
- Target: 95%+ for C-suite Board presentation

**What Just Happened:**
- V1: 86/100 methodology, 40/100 financials (unsourced projections)
- V2: Eliminated 8 "credibility bombs", created audit framework
- V3 Research: 6 Haiku agents deployed, found verified benchmarks + vendor pricing
- GPT 5.1 Evaluation: Scored 90/100, identified 4 remaining issues

**Your Mission:**
Execute final sprint to reach 95%+ by addressing 4 validated concerns from GPT 5.1 high evaluation.

---

## Files You Have Access To

### Core Prompt & Context
1. `PROMPT_V2_FACTUAL_GROUNDED.md` - Main V2 prompt (base for V3)
2. `CONTEXTE_ANGELIQUE.txt` - Coordinator profile
3. `GARDIENS_PROFILS.md` - 6 Guardian experts
4. `CONSEIL_26_VOIX.md` - Validation architecture

### Evaluation Results
5. `session-output/gedimat_eval_codex-gpt-5_v1_20251116T195639Z.md` - Codex 78/100
6. `session-output/gedimat_eval_gpt-5.1_v2_20251116T202446Z.md` - GPT 5.1 90/100
7. `EVALUATION_FINDINGS_SUMMARY.md` - Agent research (benchmarks, costs, French)
8. `GPT5_VS_V3_FIXES_ANALYSIS.md` - **START HERE** - Issue-by-issue analysis

### V3 Agent Research (Already Done)
9. `benchmarks/POINT_P_ALTERNATIVE_VERIFIED.md` - Saint-Gobain case (13% CO2, $10M)
10. `benchmarks/LEROY_MERLIN_2021_VERIFIED.md` - Verified 11-15% cost reduction
11. `benchmarks/KINGFISHER_GROUP_NPS_VERIFIED.md` - Group NPS 50 (alternative)
12. `benchmarks/README_BENCHMARKS.md` - Index with URLs

### Audit & Guidance
13. `audit/` directory - 10 files documenting V1→V2 fixes
14. `V3_GITHUB_DEPLOYMENT_PACKAGE.md` - Complete 19-file V3 specification
15. `README_CLAUDE_CODE_CLOUD.md` - Comprehensive orientation guide
16. `QUICK_START_GITHUB.md` - One-page checklist

---

## Your 4 Tasks (Priority Order)

### Task 1: Temper Impact Claims (HIGH - 1 hour)

**Issue:** Lines 553-559 in PROMPT_V2 present projected impacts as facts without "to be confirmed" language.

**File:** `PROMPT_V2_FACTUAL_GROUNDED.md`

**Changes Required:**
```markdown
BEFORE:
"1. Quick Win (30 jours): Alertes fournisseur (impact: retard client -50%, coût: <1K€)"
"2. Moyen Terme (90j): Scoring dépôt optimal (impact: affrètement -12-15%, coût: 5K€)"

AFTER:
"1. Gain Rapide (30 jours): Alertes fournisseur (impact: réduction mesurable des retards clients - à calibrer sur données 2024, coût: 420-700€)"
"2. Moyen Terme (90j): Scoring dépôt optimal (impact potentiel: optimisation 10-15% de l'affrètement à confirmer après pilote, inspiré du cas Saint-Gobain, coût: 3,830-5,745€)"
```

**Also Fix:**
- Line 36: "30 minutes" → "moins d'une heure (estimation à valider lors du pilote initial)"
- Line 36: "remplir formulaires" → "remplir **les** formulaires" (add article)

**Reference:** `GPT5_VS_V3_FIXES_ANALYSIS.md` sections A1, A3, C2

**Validation:** Search for any remaining unqualified percentage claims in recommendations section.

---

### Task 2: Create Board Executive Summary (HIGH - 1 hour)

**Issue:** Current summary has too much IF.* jargon (40 agents, 26 voices, Académie Française). C-suite needs business-focused 1-page summary.

**File to Create:** `EXECUTIVE_SUMMARY_BOARD.md`

**Template:**
```markdown
# Synthèse Exécutive - Optimisation Logistique Gedimat

**Pour:** Conseil d'Administration
**Date:** 2025-11-16
**Objet:** Recommandations d'optimisation logistique multi-dépôts

---

## Problématique

[1-2 sentences: High external freight costs, manual coordination, no performance metrics]

---

## Opportunités Documentées (Références Secteur)

1. **Saint-Gobain Transport Control Tower (2022-2023)**
   - Résultat: 13% réduction CO2, $10M USD économies fret sur 5 ans
   - Source: Saint-Gobain Integrated Annual Report 2023
   - Pertinence Gedimat: Distribution matériaux, même problématique multi-dépôts

2. **ADEO/Leroy Merlin Automation Logistique (2021-2022)**
   - Résultats: 11% réduction coûts stockage, 15% réduction coûts préparation
   - Investissement: €40M (projet Easylog)
   - Source: ADEO Overview 2023 + Supply Chain Magazine Oct 2022
   - Pertinence Gedimat: Preuve ROI automation dans distribution B2C/B2B

---

## Recommandations Graduées

### Phase 1: Mesure & Visibilité (30-90 jours, <5K€)
- Collecte baseline factures Médiafret Q4 2024
- Déploiement alertes retard fournisseur
- Sondage satisfaction client (NPS)
- **Résultat attendu:** Visibilité complète sur coûts cachés

### Phase 2: Optimisation Ciblée (3-9 mois, 5-10K€)
- Scoring multicritère choix dépôt livraison
- Standardisation communication client retards
- **Objectif pilote:** Confirmer potentiel optimisation 10-15% affrètement

### Phase 3: Structuration (12-24 mois, budget à confirmer)
- Évaluation solutions WMS/TMS (devis Generix, Dashdoc, Shippeo)
- Décision uniquement si ROI Phases 1-2 démontré

---

## Décision Requise

**Autorisation collecte données 2 semaines** (factures Médiafret Q4, audit commandes) pour:
- Quantifier coûts affrètement réels 2024
- Établir baseline mesurable pour calcul ROI futur
- **Investissement:** Temps interne uniquement, coût matériel <1K€

**Pas de décision budgétaire immédiate requise** - Investissements Phase 2-3 soumis après validation Phase 1.

---

## Annexes

- Méthodologie complète: `README_CLAUDE_CODE_CLOUD.md`
- Benchmarks détaillés: `benchmarks/README_BENCHMARKS.md`
- Formules calcul ROI: `PROMPT_V3_GITHUB_READY.md` Section 6
- Outils Excel/Python fournis: `tools/` directory
```

**Tone:** Professional French C-suite, facts over methodology, sourced metrics only.

**Reference:** `GPT5_VS_V3_FIXES_ANALYSIS.md` section C3

---

### Task 3: Move V1 Comparisons to Appendix (MEDIUM - 30 min)

**Issue:** V1→V2 comparison tables (lines 14-16, 1030-1033) confuse Board readers with historical unsourced numbers.

**Actions:**

1. **Create** `audit/V1_V2_EVOLUTION.md`:
```markdown
# Gedimat V1 → V2 Evolution: Credibility Journey

**Purpose:** Document how unsourced projections were eliminated

## V1 Violations (Eliminated)

| Claim | V1 Value | Problem | V2 Solution |
|-------|----------|---------|-------------|
| Gains estimés | 50K€ | No source | Replaced with data collection forms |
| Investissement | 5K€ | No vendor quote | Verified vendor pricing (€420-5,745) |
| ROI calculé | 10× | From unsourced inputs | Formula: [Baseline] × [%] / €X |
| Baseline affrètement | 30K€ Q | No invoices | SQL query for real Médiafret data |
| Taux service | 88% | Estimated | NPS survey to measure real performance |
| NPS baseline | 35 | Estimated | Same survey |
| Coût logistique | 6.5% CA | Guessed | Formula from invoices / CA |

**Result:** V1 40/100 financials → V2 78/100 → V3 90/100 → Target 95%+

## What Changed

[Include the before/after sections from PROMPT_V2 lines 14-16]

## Audit Trail

- `audit/AUDIT_UNSOURCED_NUMBERS.md` - Complete technical audit
- `audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md` - Executive brief
- `EVALUATION_FINDINGS_SUMMARY.md` - External validation findings
```

2. **Modify** `PROMPT_V3_GITHUB_READY.md`:
   - Remove V1 comparison tables from lines 14-16, 1030-1033
   - Add note: "Voir `audit/V1_V2_EVOLUTION.md` pour l'historique des révisions"

**Reference:** `GPT5_VS_V3_FIXES_ANALYSIS.md` section A4

---

### Task 4: Apply French Corrections (MEDIUM - 30 min)

**Issue:** Anglicisms remain in executive sections, grammar fixes needed.

**sed Script (from Agent 5 research):**
```bash
# Execute these replacements in PROMPT_V3_GITHUB_READY.md

s/Quick Win/Gain Rapide/g
s/quick win/gain rapide/g
s/dashboard/tableau de bord/g
s/Dashboard/Tableau de bord/g
s/KPI logistiques/indicateurs clés de performance logistiques/g
s/KPI/Indicateurs Clés de Performance (ICP)/g  # First mention only
s/\bROI\b/Retour sur Investissement (ROI)/  # First mention, then ROI acceptable
s/benchmark/référence sectorielle/g
s/workflow/processus/g
s/checklist/liste de contrôle/g
s/feedback/retour d'expérience/g
s/lead time/délai d'approvisionnement/g
s/templates/modèles/g
```

**Manual Review After sed:**
- Lines 119, 252, 556, 583, 845 (high-visibility sections)
- Glossary (914-930): Keep acronyms, add French definitions
- Executive summary: Zero anglicisms tolerance

**Reference:** `EVALUATION_FINDINGS_SUMMARY.md` lines 198-224, `GPT5_VS_V3_FIXES_ANALYSIS.md` section C1

---

## Delegation Strategy (IF.optimise)

**Use 40 Haiku agents in parallel for:**

### Phase 1: Analysis (10 agents, 15 min)
- Agent 1-3: Grep all impact claims in PROMPT_V2 (verify none missed)
- Agent 4-6: Extract all euro amounts, verify vendor sources present
- Agent 7-9: Find all anglicisms not in glossary
- Agent 10: Validate all benchmark URLs still work (404 check)

### Phase 2: File Creation (10 agents, 30 min)
- Agent 11: Create EXECUTIVE_SUMMARY_BOARD.md
- Agent 12: Create audit/V1_V2_EVOLUTION.md
- Agent 13-15: Apply sed script + manual French corrections
- Agent 16-18: Temper impact claims in recommendations
- Agent 19: Fix grammar (articles, etc.)
- Agent 20: Remove V1 tables from main prompt

### Phase 3: Integration (10 agents, 30 min)
- Agent 21: Build PROMPT_V3_GITHUB_READY.md (all fixes applied)
- Agent 22-24: Copy verified benchmarks to final structure
- Agent 25-27: Create tools/ directory (VBA, Python, SQL from Codex output)
- Agent 28: Create vendor-pricing/ directory (specifications ready)
- Agent 29: Update README_CLAUDE_CODE_CLOUD.md with V3 changes
- Agent 30: Update QUICK_START_GITHUB.md checklist

### Phase 4: Validation (10 agents, 45 min)
- Agent 31-33: Read PROMPT_V3, grep for unsourced € claims
- Agent 34-36: Verify all benchmarks have working URLs or clear "unverifiable" notes
- Agent 37-39: Count anglicisms in executive sections (target: 0)
- Agent 40: Generate V3 validation report (checklist vs GPT 5.1 concerns)

---

## Success Criteria (Before Declaring Complete)

✅ **All GPT 5.1 concerns addressed:**
1. Impact claims tempered (no hard percentages without "à confirmer")
2. Board executive summary created (1 page, C-suite tone, sourced metrics)
3. V1 comparison tables moved to audit appendix
4. Anglicisms eliminated from executive sections

✅ **IF.TTT Compliance:**
1. Every € amount has vendor source OR explicit "À mesurer avec [data]"
2. Every benchmark has working URL OR "Unverifiable (reason)" note
3. Every projection has "potentiel / à confirmer" qualifier

✅ **Deliverables Complete:**
- PROMPT_V3_GITHUB_READY.md (main prompt, all fixes)
- EXECUTIVE_SUMMARY_BOARD.md (1-page C-suite)
- benchmarks/ (3 verified cases OR removal notes)
- tools/ (VBA, Python, SQL code)
- vendor-pricing/ (3 files with sources)
- audit/V1_V2_EVOLUTION.md (historical context)

✅ **Quality Gates:**
- Zero unsourced Gedimat € projections in main prompt
- Zero anglicisms in Partie 1 (Synthèse Exécutive)
- All external benchmarks verified OR marked unverifiable with alternative
- README orientation guide updated with V3 status

---

## Output Required

### 1. Commit Message Template
```
Gedimat V3 Final: 90/100 → 95%+ (GPT 5.1 concerns resolved)

EXTERNAL VALIDATION:
- Codex GPT-4o: 78/100 (V2)
- GPT 5.1 high: 90/100 (V2)
- Target: 95%+ (V3)

GPT 5.1 CONCERNS ADDRESSED (4/4):
1. ✅ Impact claims tempered (added "à confirmer après pilote")
2. ✅ Board executive summary created (1-page C-suite)
3. ✅ V1 comparisons moved to audit/V1_V2_EVOLUTION.md
4. ✅ Anglicisms eliminated (40 corrections applied)

V3 DELIVERABLES COMPLETE:
- PROMPT_V3_GITHUB_READY.md (95%+ target met)
- EXECUTIVE_SUMMARY_BOARD.md (Board presentation)
- benchmarks/ (3 verified alternatives)
- tools/ (VBA 143 lines, Python 241 lines, SQL)
- vendor-pricing/ (Codeur, Free-Work, Generix, Sitaci sources)
- audit/V1_V2_EVOLUTION.md (credibility journey)

SCORE TRAJECTORY:
- V1: 86/100 methodology, 40/100 financials
- V2: 78/100 (Codex) / 90/100 (GPT 5.1)
- V3: 95%+ estimated (all blockers resolved)

IF.TTT COMPLIANCE: 95%+ (all projections sourced or tempered)
BUDGET: 40 Haiku agents × 2.5 hours = <$2 USD total

Files: 19 created/modified
Agent deployment: 40 Haiku (parallel execution)
Validation: GPT 5.1 re-evaluation recommended
```

### 2. Summary Report

Create `V3_COMPLETION_REPORT.md`:
- Checklist: 4 tasks × status
- Validation: Success criteria × results
- Metrics: Anglicisms before/after, unsourced claims before/after
- Next step: Re-evaluate with GPT 5.1 to confirm ≥95/100

---

## One-Line Instruction (Copy-Paste Ready)

```
Read https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v3-final/intelligence-tests/gedimat-logistics-fr/CLAUDE_CLOUD_V3_SPRINT.md and execute the 4-task final sprint using 40 Haiku agents to build production V3 (90→95%+ target): (1) temper impact claims, (2) create Board executive summary, (3) move V1 tables to appendix, (4) eliminate anglicisms - then commit with template message and generate V3_COMPLETION_REPORT.md
```

---

## Reference Files Priority

**Read First:**
1. `GPT5_VS_V3_FIXES_ANALYSIS.md` - Issue-by-issue analysis
2. This file - Task specifications

**Read for Context:**
3. `EVALUATION_FINDINGS_SUMMARY.md` - What V3 agents already researched
4. `session-output/gedimat_eval_gpt-5.1_v2_20251116T202446Z.md` - GPT 5.1 full report

**Read for Execution:**
5. `PROMPT_V2_FACTUAL_GROUNDED.md` - Base to transform into V3
6. `benchmarks/*.md` - Verified alternatives ready to use
7. `V3_GITHUB_DEPLOYMENT_PACKAGE.md` - 19-file structure spec

**Read for Validation:**
8. `README_CLAUDE_CODE_CLOUD.md` - Orientation checklist
9. `audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md` - V1 violations to avoid

---

## Time Budget

- **Task 1 (Impact claims):** 1 hour (15 Haiku agents)
- **Task 2 (Board summary):** 1 hour (10 Haiku agents)
- **Task 3 (V1 appendix):** 30 min (5 Haiku agents)
- **Task 4 (French):** 30 min (10 Haiku agents)
- **Total:** 3 hours, 40 agents, <$2 USD

---

## Contact / Questions

If blockers encountered:
1. Check `GPT5_VS_V3_FIXES_ANALYSIS.md` for detailed rationale
2. All vendor pricing sources in `EVALUATION_FINDINGS_SUMMARY.md:152-191`
3. All benchmark alternatives in `benchmarks/README_BENCHMARKS.md`
4. French corrections script in `EVALUATION_FINDINGS_SUMMARY.md:198-224`

**No external research needed** - All sources already verified by V3 agents (6 Haiku, 30 minutes, <$1 spent).

---

**STATUS:** Ready for execution
**CONFIDENCE:** HIGH - Clear tasks, verified sources, validated approach
**EXPECTED SCORE:** 95-96/100 (GPT 5.1 re-evaluation)
