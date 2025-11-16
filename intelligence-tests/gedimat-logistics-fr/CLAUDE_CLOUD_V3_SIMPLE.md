# V3 Final Sprint: Polish Gedimat Logistics Dossier (90→95%)

**You are:** Fresh Claude Code Cloud session
**Your task:** Fix 4 specific issues in a French logistics optimization dossier
**Time:** 2-3 hours with 40 Haiku agents
**Score goal:** 90/100 → 95%+

---

## What This Project Is

A logistics optimization recommendation dossier for Gedimat (French building materials distributor). External AI evaluators (Codex, GPT 5.1) scored it at 78-90/100. You need to address 4 specific concerns to reach 95%+.

**The dossier recommends:**
- Better depot selection (reduce external freight costs)
- Performance metrics (NPS surveys, service rates)
- Automation options (WMS/TMS systems)

**Your job:** NOT to rewrite methodology, ONLY fix 4 validated issues.

---

## The 4 Issues (From GPT 5.1 High Evaluation)

### Issue 1: Impact Claims Too Strong (HIGH Priority)
**Problem:** Projected results ("-50% delays", "-12-15% freight costs") stated as facts, not hypotheses.

**Fix:** Add "to be confirmed after pilot" language.

**Example:**
```markdown
BEFORE:
"Impact: retard client -50%, affrètement -12-15%"

AFTER:
"Impact potentiel: réduction mesurable des retards (à calibrer sur données 2024),
optimisation 10-15% affrètement (à confirmer après pilote, inspiré cas Saint-Gobain)"
```

**Where:** `PROMPT_V2_FACTUAL_GROUNDED.md` lines 553-559, 661-665
**Also:** Line 36: "30 minutes" → "moins d'une heure (estimation à valider)"

---

### Issue 2: No Board-Level Executive Summary (HIGH Priority)
**Problem:** Current summary has too much technical jargon. C-suite needs 1-page business summary.

**Fix:** Create new file `EXECUTIVE_SUMMARY_BOARD.md`

**Template:**
```markdown
# Synthèse Exécutive - Optimisation Logistique Gedimat

**Pour:** Conseil d'Administration

## Problématique
[2 sentences: High freight costs, manual coordination, no metrics]

## Références Secteur (Documentées)

**Saint-Gobain Transport Control Tower (2022-2023):**
- Résultat: 13% réduction CO2, $10M économies fret (5 ans)
- Source: Saint-Gobain Annual Report 2023

**ADEO/Leroy Merlin Automation (2021-2022):**
- Résultats: 11-15% réduction coûts logistiques
- Investissement: €40M
- Sources: ADEO Overview 2023, Supply Chain Magazine Oct 2022

## Recommandations

**Phase 1 (30-90j, <5K€):** Mesure baseline + alertes
**Phase 2 (3-9m, 5-10K€):** Pilote scoring dépôt
**Phase 3 (12-24m, budget à confirmer):** WMS/TMS si ROI démontré

## Décision Requise
Autorisation collecte données 2 semaines (factures, audit commandes)
**Pas de décision budgétaire immédiate**
```

**Tone:** Professional French, facts only, no jargon
**Length:** 1 page maximum

---

### Issue 3: Old V1 Numbers Still Visible (MEDIUM Priority)
**Problem:** Historical unsourced numbers (50K€, 10× ROI) from V1 still in comparison tables, confuse readers.

**Fix:** Move to separate appendix file.

**Actions:**
1. Create `audit/V1_V2_EVOLUTION.md` with comparison tables from lines 14-16, 1030-1033
2. Remove those tables from `PROMPT_V3_GITHUB_READY.md`
3. Add note: "Voir audit/V1_V2_EVOLUTION.md pour historique révisions"

---

### Issue 4: French Language - Anglicisms (MEDIUM Priority)
**Problem:** English terms in French document ("Quick Win", "dashboard", "KPI")

**Fix:** Apply these replacements:
```bash
Quick Win → Gain Rapide
dashboard → tableau de bord
KPI → Indicateurs Clés de Performance (ICP)
ROI → Retour sur Investissement (ROI) [first mention, then ROI OK]
benchmark → référence sectorielle
workflow → processus
checklist → liste de contrôle
```

**Also:** Fix grammar - Line 36: "remplir formulaires" → "remplir **les** formulaires"

**Where:** Focus on lines 119, 252, 556, 583, 845 (high-visibility sections)

---

## Files You Need

**To read/understand:**
1. `GPT5_VS_V3_FIXES_ANALYSIS.md` ← START HERE (detailed analysis of 4 issues)
2. `session-output/gedimat_eval_gpt-5.1_v2_20251116T202446Z.md` (GPT 5.1 full evaluation)

**To modify:**
3. `PROMPT_V2_FACTUAL_GROUNDED.md` → becomes `PROMPT_V3_GITHUB_READY.md`

**To use as sources:**
4. `benchmarks/POINT_P_ALTERNATIVE_VERIFIED.md` (Saint-Gobain case - use in Board summary)
5. `benchmarks/LEROY_MERLIN_2021_VERIFIED.md` (ADEO metrics - use in Board summary)
6. `EVALUATION_FINDINGS_SUMMARY.md` (vendor pricing, all sources pre-researched)

**To create:**
7. `EXECUTIVE_SUMMARY_BOARD.md` (new)
8. `audit/V1_V2_EVOLUTION.md` (new)
9. `PROMPT_V3_GITHUB_READY.md` (modified from V2)
10. `V3_COMPLETION_REPORT.md` (validation checklist)

---

## Step-by-Step Execution

### Step 1: Read & Understand (15 min)
1. Read `GPT5_VS_V3_FIXES_ANALYSIS.md` completely
2. Skim `PROMPT_V2_FACTUAL_GROUNDED.md` to understand structure
3. Check benchmarks/ files to see verified data ready to use

### Step 2: Deploy Haiku Agents (2 hours)

**10 agents for Issue 1 (Impact Claims):**
- Agents 1-5: Find all percentage claims and euro amounts in PROMPT_V2
- Agents 6-10: Replace with tempered language ("potentiel", "à confirmer")

**10 agents for Issue 2 (Board Summary):**
- Agents 11-12: Extract key metrics from benchmarks/
- Agents 13-15: Draft EXECUTIVE_SUMMARY_BOARD.md sections
- Agents 16-18: Polish French tone for C-suite
- Agents 19-20: Validate 1-page length, no jargon

**10 agents for Issue 3 (V1 Tables):**
- Agents 21-23: Extract comparison tables from PROMPT_V2 lines 14-16, 1030-1033
- Agents 24-26: Create audit/V1_V2_EVOLUTION.md
- Agents 27-29: Remove tables from PROMPT_V3, add reference note
- Agent 30: Validate no V1 numbers remain in main prompt

**10 agents for Issue 4 (French):**
- Agents 31-35: Apply sed script for anglicisms
- Agents 36-38: Manual review high-visibility lines
- Agents 39-40: Fix grammar (articles, etc.)

### Step 3: Integration (30 min)
- Combine all fixes into `PROMPT_V3_GITHUB_READY.md`
- Validate against GPT 5.1 concerns (4/4 addressed?)
- Create `V3_COMPLETION_REPORT.md`

### Step 4: Commit
- Use commit message template (see below)
- Push to branch `gedimat-v3-final`

---

## Success Checklist

Before declaring complete, verify:

✅ **Issue 1 fixed:**
- [ ] No unqualified percentage claims (all have "potentiel / à confirmer")
- [ ] "30 minutes" → "moins d'une heure (estimation)"
- [ ] All euro amounts have vendor sources OR "À mesurer avec [data]"

✅ **Issue 2 fixed:**
- [ ] EXECUTIVE_SUMMARY_BOARD.md created
- [ ] 1 page maximum
- [ ] Uses Saint-Gobain + ADEO benchmarks with sources
- [ ] Zero jargon (no "IF.*", "40 agents", technical methodology)
- [ ] Professional French C-suite tone

✅ **Issue 3 fixed:**
- [ ] audit/V1_V2_EVOLUTION.md created with comparison tables
- [ ] V1 tables removed from PROMPT_V3_GITHUB_READY.md
- [ ] Reference note added

✅ **Issue 4 fixed:**
- [ ] Zero anglicisms in executive sections (lines 1-300)
- [ ] "Quick Win" → "Gain Rapide" everywhere
- [ ] "dashboard" → "tableau de bord" everywhere
- [ ] "KPI" → "Indicateurs Clés de Performance" first mention
- [ ] Grammar fixed ("les formulaires")

---

## Commit Message Template

```
Gedimat V3 Final: 90→95%+ (4 GPT 5.1 concerns resolved)

ISSUES ADDRESSED:
1. ✅ Impact claims tempered (added "à confirmer après pilote")
2. ✅ Board executive summary created (1-page C-suite)
3. ✅ V1 comparisons moved to audit/V1_V2_EVOLUTION.md
4. ✅ Anglicisms eliminated (40 corrections)

FILES CREATED:
- PROMPT_V3_GITHUB_READY.md (all fixes applied)
- EXECUTIVE_SUMMARY_BOARD.md (Board presentation)
- audit/V1_V2_EVOLUTION.md (historical context)
- V3_COMPLETION_REPORT.md (validation checklist)

SCORE TRAJECTORY:
V1: 86/100 → V2: 90/100 (GPT 5.1) → V3: 95%+ (target met)

Agents: 40 Haiku parallel execution
Time: 2.5 hours
Budget: <$2 USD
```

---

## Important Notes

**DO NOT:**
- Rewrite the methodology (8-pass system is already validated at 95/100)
- Add new benchmarks (3 verified alternatives already researched)
- Research vendor pricing (all sources already documented)
- Change the overall structure (only fix 4 specific issues)

**DO:**
- Focus exclusively on the 4 issues from GPT 5.1
- Use pre-researched benchmark data from benchmarks/ files
- Use vendor pricing from EVALUATION_FINDINGS_SUMMARY.md
- Keep changes minimal and surgical

**Why:** External evaluators scored methodology highly (86-95/100). Only credibility and presentation need polish.

---

## One-Line Instruction

```
Read https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v3-final/intelligence-tests/gedimat-logistics-fr/CLAUDE_CLOUD_V3_SIMPLE.md and execute 4 focused fixes (temper impact claims, create Board summary, move V1 tables, eliminate anglicisms) using 40 Haiku agents to reach 95%+ score
```

---

**Current Status:** V2 at 90/100 (GPT 5.1 high)
**Target:** 95%+ (4 specific fixes)
**Confidence:** HIGH (issues validated, sources pre-researched)
**Next:** Re-evaluate with GPT 5.1 after V3 to confirm score
