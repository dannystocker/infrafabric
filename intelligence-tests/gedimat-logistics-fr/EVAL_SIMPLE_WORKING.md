# Simple Working Evaluation Commands

**Problem:** GitHub branch `gedimat-v2-clean` push timing out (HTTP 408)
**Solution:** Use local files directly with Codex/Gemini

---

## Working Approach: Local Files

Since the files are already on your machine at:
`/home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/`

### Method 1: Codex with Local File (RECOMMENDED - WORKING)

```bash
cd /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/

codex-cli chat --model gpt-4o-2024-11-20 \
  --file PROMPT_V2_FACTUAL_GROUNDED.md \
  --message "ÉVALUATION CRITIQUE (FRANÇAIS):

Objectif: Score 95%+ (actuellement 85%)

Analysez ce fichier PROMPT_V2_FACTUAL_GROUNDED.md:

1. **IF.TTT Compliance**: Trouvez TOUTE projection € Gedimat sans source
   - Montants € non sourcés?
   - ROI calculés sur baselines inventées?
   - \"Estimé\" sans \"À mesurer avec [données]\"?

2. **Benchmarks Externes**: Vérifiez citations
   - Point P 2022 (12% réduction): Source LSA Conso réelle?
   - Leroy Merlin 2021 (ROI 8.5×): Rapport annuel vérifiable?
   - Castorama 2023 (NPS 47): Kingfisher report existe?

3. **Qualité Français**: Détectez
   - Anglicismes (dashboard, KPI, quick win)
   - Fautes grammaire
   - Ton inapproprié conseil administration

4. **Code Manquant**: Fournir
   - Macro Excel VBA (scoring dépôts)
   - Script Python (analyse NPS)
   - Requête SQL (baseline factures)

RÉPONDEZ EN FRANÇAIS.

Format:
## Scores
- IF.TTT: __/100
- Français: __/100
- Global: __/100

## Violations Critiques
[Liste avec ligne numéro]

## Code Production-Ready
[VBA, Python, SQL complets]

## Chemin vers 95%+
[Fixes prioritaires]"
```

---

### Method 2: Gemini with Local File (WORKING)

```bash
cd /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/

# First, start a chat session
gemini chat --model gemini-2.0-flash-exp "Je vais évaluer un dossier logistique français. Prêt?"

# Then in the interactive session, attach the file:
# (In Gemini CLI, you can upload files during conversation)

# Or use this single-shot approach:
cat PROMPT_V2_FACTUAL_GROUNDED.md | gemini chat --model gemini-2.0-flash-exp "ÉVALUATION CRITIQUE (FRANÇAIS):

Ci-dessus: contenu PROMPT_V2_FACTUAL_GROUNDED.md

Objectif: 85% → 95%+

Tâches:
1. Projections € Gedimat non sourcées? (Listez ligne:numéro)
2. Benchmarks: Point P, Leroy Merlin, Castorama - citations réelles?
3. Anglicismes trouvés? (dashboard, KPI...)
4. Code manquant: VBA + Python + SQL

Scores:
- IF.TTT: __/100
- Français: __/100
- Global: __/100

Fixes prioritaires pour 95%+?"
```

---

### Method 3: Simple Multi-Step (MOST RELIABLE)

**Step 1: Start Codex Session**
```bash
cd /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/

codex-cli chat --model gpt-4o-2024-11-20 --message "Bonjour! Je vais vous demander d'évaluer un dossier logistique français (Gedimat V2). Objectif: identifier gaps entre score actuel (85%) et cible (95%). Prêt?"
```

**Step 2: Send File**
```bash
codex-cli chat --continue --file PROMPT_V2_FACTUAL_GROUNDED.md --message "Voici le fichier principal. Première impression: voyez-vous des projections financières € sans source?"
```

**Step 3: Deep Dive**
```bash
codex-cli chat --continue --message "Vérifiez ces 3 benchmarks externes:
1. Point P 2022 (12% réduction) - Source: LSA Conso Mars 2023
2. Leroy Merlin 2021 (ROI 8.5×) - Source: Rapport annuel p.67
3. Castorama NPS 47 - Source: Kingfisher

Sont-ils vérifiables?"
```

**Step 4: French Quality**
```bash
codex-cli chat --continue --message "Qualité français: listez anglicismes (dashboard→tableau de bord, KPI→indicateurs, etc.) et fautes grammaire. Top 10 corrections?"
```

**Step 5: Code Request**
```bash
codex-cli chat --continue --message "Fournissez code production-ready:
1. Macro Excel VBA: Scoring multicritère dépôt optimal (input: volume, distance, délai → output: dépôt recommandé)
2. Script Python: Analyse sondage NPS (input: CSV notes 0-10 → output: score NPS + breakdown)
3. Requête SQL: Baseline factures Médiafret Q1-Q3 2024"
```

**Step 6: Final Report**
```bash
codex-cli chat --continue --message "RAPPORT FINAL:

Scores:
- IF.TTT Compliance: __/100
- Qualité Preuves: __/100
- Qualité Français: __/100
- Global: __/100

Écart vers 95%: __ points

Top 3 fixes prioritaires:
1. ___
2. ___
3. ___

Verdict: OUI déploiement / OUI AVEC FIXES / NON"
```

---

## Method 4: Offline Analysis (NO API CALLS)

If you want to review yourself first:

```bash
cd /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/

# Search for unsourced € amounts
grep -n "€" PROMPT_V2_FACTUAL_GROUNDED.md | grep -v "À mesurer" | grep -v "formulaire" | grep -v "cas externe"

# Search for anglicisms
grep -niE "(dashboard|KPI|quick win|best practice|benchmark)" PROMPT_V2_FACTUAL_GROUNDED.md

# Check if benchmarks have URLs
grep -n "Point P\|Leroy Merlin\|Castorama" PROMPT_V2_FACTUAL_GROUNDED.md

# List all "estimé" without data source reference
grep -n "estimé" PROMPT_V2_FACTUAL_GROUNDED.md | grep -v "À mesurer"
```

---

## Why Previous Commands Failed

**Error:** `404 NOT_FOUND` from Gemini API

**Root Cause:**
- Branch `gedimat-v2-clean` not yet on GitHub (push timing out: HTTP 408)
- Gemini tried to fetch `https://raw.githubusercontent.com/.../gedimat-v2-clean/...`
- File doesn't exist on remote → 404

**Solution:**
- Use local files with `--file` flag (Codex)
- Pipe content via `cat` (Gemini)
- Or wait for GitHub push to succeed, then retry original commands

---

## Check GitHub Push Status

```bash
cd /home/setup/infrafabric

# Check if push succeeded
git ls-remote --heads origin gedimat-v2-clean

# If returns SHA hash → push succeeded, can use GitHub URLs
# If empty → push failed, use local files
```

---

## Recommended Right Now

Use **Method 1 (Codex with local file)** or **Method 3 (Multi-step)** - both work without GitHub.

Once GitHub push succeeds (may need to retry or use different network), the original one-liner commands will work.

---

## Quick Test

```bash
# Test if Codex can read local file
cd /home/setup/infrafabric/intelligence-tests/gedimat-logistics-fr/
codex-cli chat --file audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md --message "Résumez ce fichier en français (3 phrases max)"

# If this works → proceed with Method 1
# If fails → use Method 3 (multi-step interactive)
```
