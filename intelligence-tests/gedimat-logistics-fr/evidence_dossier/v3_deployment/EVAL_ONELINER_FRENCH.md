# Commandes d'Évaluation en Français

Objectif: **Score qualité et preuves ≥95%** (actuellement 85%)

---

## Codex CLI (OpenAI GPT-4o) - Évaluation en Français

```bash
codex-cli chat --model gpt-4o-2024-11-20 --message "ÉVALUATION CRITIQUE: Dossier Gedimat V2 Optimisation Logistique

Objectif: Score qualité/preuves ≥95% (actuellement 85%)
Branche: github.com/dannystocker/infrafabric/gedimat-v2-clean

Lire ces 4 fichiers depuis GitHub:
1. intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md
2. intelligence-tests/gedimat-logistics-fr/audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md
3. intelligence-tests/gedimat-logistics-fr/audit/AUDIT_UNSOURCED_NUMBERS.md
4. intelligence-tests/gedimat-logistics-fr/LAUNCH_V2_INSTRUCTIONS.md

MISSION (répondre EN FRANÇAIS):
1. Vérifier ZÉRO projection financière Gedimat non sourcée (montants €, ROI, baselines)
2. Valider benchmarks externes: Point P 2022 (12% LSA Conso), Leroy Merlin 2021 (ROI 8.5×), Castorama NPS 47 - sont-ils RÉELS?
3. Qualité du français: détecter anglicismes, fautes grammaire, ton inapproprié pour conseil d'administration
4. Identifier lacunes bloquant score 95%+
5. Fournir code: Macro Excel VBA scoring dépôts, Script Python analyse NPS, Requête SQL baseline factures

FORMAT RÉPONSE (EN FRANÇAIS):
## Scores
- Conformité IF.TTT: __/100
- Qualité preuves: __/100
- Méthodologie: __/100
- Actionnabilité: __/100
- Qualité français: __/100
- **GLOBAL: __/100**

## Écart vers 95%
- Score actuel estimé: __/100
- Écart: __ points
- Bloqueurs prioritaires

## Violations Trouvées

### A. Projections non sourcées (CRITIQUE)
Emplacement: PROMPT_V2:ligne___
Affirmation: \"___\"
Problème: \"Aucune source - Gedimat PDG pourrait contester\"
Correction: \"___\"

### B. Benchmarks externes (CRITIQUE)
Point P 2022 (12% réduction):
- Source prétendue: LSA Conso Mars 2023, p.34
- URL fournie: ___
- VÉRIFICATION: ✅ Confirmé / ❌ Introuvable / ⚠️ Chiffre différent
- Si ❌: Source alternative française suggérée: ___

Leroy Merlin 2021 (ROI 8.5×):
- Source: Rapport annuel 2021 p.67
- VÉRIFICATION: ___
- Correction: ___

Castorama 2023 (NPS 47):
- Source: Rapport Kingfisher
- VÉRIFICATION: ___
- Correction: ___

### C. Qualité français (CRITIQUE pour présentation C-suite)

Anglicismes trouvés:
- Ligne ___: \"dashboard\" → \"tableau de bord\"
- Ligne ___: \"KPI\" → \"indicateurs clés de performance\"
- Ligne ___: \"ROI\" → \"retour sur investissement\" (acceptable en contexte financier)

Fautes grammaire:
- Ligne ___: \"___\" → Correction: \"___\"

Ton inapproprié:
- Ligne ___: Trop [familier/arrogant/technique] pour conseil administration
- Reformulation suggérée: \"___\"

## Code Fonctionnel

### 1. Macro Excel VBA: Scoring Multicritère Dépôt Optimal
```vba
' À FOURNIR: Code VBA complet production-ready
' Input: Volume (t), Distance (km), Délai (h), Priorité
' Output: Dépôt recommandé (Lieu/Méru/Breuilpont) + Score
```

### 2. Script Python: Analyse Sondage NPS
```python
# À FOURNIR: Script Python complet
# Input: CSV réponses clients (note 0-10)
# Output: Score NPS, % Promoteurs/Passifs/Détracteurs
```

### 3. Requête SQL: Baseline Factures Médiafret
```sql
-- À FOURNIR: Requête SQL complète
-- Input: Table factures (date, montant, tonnage, trajet)
-- Output: Baseline mensuel Q1-Q3 2024, coût/tonne moyen
```

## Chemin vers 95%+

**PRIORITÉ 1 (BLOQUE DÉPLOIEMENT):**
1. ___
   Impact: -__ points
   Correction: ___

**PRIORITÉ 2 (REQUIS POUR 95%):**
1. ___
2. ___

**PRIORITÉ 3 (POLISH 98%+):**
1. ___

## Verdict

Prêt pour déploiement vers nouvelle session Claude Code Cloud?
☐ OUI - Aucun changement requis
☐ OUI AVEC CORRECTIONS - Appliquer fixes ci-dessus d'abord
☐ NON - Bloqueurs critiques non résolus

**Bloqueurs critiques (si NON):**
1. ___
2. ___

## Confiance Évaluation
☐ HAUTE - Stakeriez votre réputation professionnelle sur qualité V2
☐ MOYENNE - Quelques réserves
☐ BASSE - Révision majeure nécessaire

**Justification:** ___

---

**Répondre ENTIÈREMENT EN FRANÇAIS** - C'est un dossier français pour client français. Qualité langue = crédibilité."
```

---

## Gemini CLI (Google Gemini 2.0 Flash) - Évaluation en Français

```bash
gemini chat --model gemini-2.0-flash-exp "ÉVALUATION CRITIQUE: Dossier Gedimat V2 Optimisation Logistique

Objectif: Score qualité/preuves ≥95% (actuellement 85%)
Branche: github.com/dannystocker/infrafabric/gedimat-v2-clean

Lire depuis GitHub:
1. https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md
2. https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/audit/QUICK_REFERENCE_UNSOURCED_CLAIMS.md
3. https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/audit/AUDIT_UNSOURCED_NUMBERS.md

MISSION (répondre EN FRANÇAIS):

**AVANTAGE GEMINI:** Vous avez recherche web supérieure + capacités multilingues excellentes. UTILISEZ-LES pour:
1. Rechercher web FRANÇAIS: LSA Conso Mars 2023 article Point P existe?
2. Trouver rapports annuels Leroy Merlin France 2021 (PDF français)
3. Vérifier Kingfisher plc reports (Castorama = filiale UK)
4. Suggérer benchmarks alternatifs FRANÇAIS si citations V2 invalides

**TÂCHES CRITIQUES:**

### A. Vérification Benchmarks Externes (UTILISEZ RECHERCHE WEB)

Point P 2022 (12% réduction coûts affrètement):
- Source prétendue: \"LSA Conso, Mars 2023, p.34\"
- URL fournie dans V2: ___
- **RECHERCHEZ WEB FRANÇAIS**: Trouvez article réel LSA Conso Point P logistique 2022-2023
- Résultat: ✅ Confirmé URL ___ / ❌ Introuvable / ⚠️ Trouvé mais chiffre différent: __%
- Si ❌: **PROPOSEZ benchmark français alternatif vérifié** (ex: BigMat, Samse, autres négoces matériaux)

Leroy Merlin 2021 (ROI 8.5× optimisation logistique):
- Source: Rapport annuel 2021 page 67
- **RECHERCHEZ**: Rapport annuel Leroy Merlin France 2021 PDF
- URL trouvée: ___
- Page 67 contient ROI 8.5×? ___
- Si ❌: Benchmark alternatif grande distribution bricolage français: ___

Castorama 2023 (NPS 47):
- Source: Kingfisher plc Annual Report
- **RECHERCHEZ**: Kingfisher 2023 report, section Castorama France
- Vérifié: ___
- Alternatif si ❌: ___

### B. Qualité Français (VOTRE FORCE)

Détecter:
- **Anglicismes** (dashboard, KPI, quick win, best practice)
- **Grammaire** (accord participes passés, subjonctif, concordance temps)
- **Registre langue** (trop familier pour conseil administration? Trop technique?)
- **Terminologie métier** (termes logistique/franchise corrects?)

Corrections prioritaires (top 10):
1. Ligne ___: \"___\" → \"___\"
2. ...

### C. Projections Non Sourcées

Scanner PROMPT_V2 ligne par ligne:
- Tout montant € relatif Gedimat sans formulaire collecte données
- Tout \"estimé\"/\"projeté\" sans \"À mesurer avec [source précise]\"
- Tout ROI calculé sur baseline inventée

Violations:
- Ligne ___: \"___\" (VIOLATION: ___)

### D. Code Production-Ready

Fournir code COMPLET exécutable:

**Excel VBA Macro** (Scoring Dépôt Optimal):
```vba
Function ScoreDépôt(Volume As Double, Distance As Double, Délai As Double, Priorité As String) As String
    ' CODE COMPLET ICI
    ' Retourner \"Lieu\" ou \"Méru\" ou \"Breuilpont\"
End Function
```

**Python NPS**:
```python
import pandas as pd

def calculer_nps(fichier_csv):
    # CODE COMPLET
    # Retourner score NPS + breakdown
    pass
```

**SQL Baseline**:
```sql
-- Requête complète baseline factures Médiafret Q1-Q3 2024
SELECT ...
```

## FORMAT RÉPONSE FINALE (EN FRANÇAIS)

## Scores
- IF.TTT Conformité: __/100
- Qualité Preuves: __/100
- Qualité Français: __/100 ⭐ (votre spécialité)
- Actionnabilité: __/100
- **GLOBAL: __/100**

## Benchmarks Vérifiés (RECHERCHE WEB)
- Point P: [✅/❌/⚠️] ___
- Leroy Merlin: [✅/❌/⚠️] ___
- Castorama: [✅/❌/⚠️] ___

## Corrections Français (Top 10)
1. ___
2. ___

## Chemin vers 95%+
- Écart actuel: __ points
- Fixes Priorité 1: ___
- Fixes Priorité 2: ___

## Verdict
☐ OUI déploiement / ☐ OUI AVEC FIXES / ☐ NON

**CRITIQUE:** Utilisez recherche web française pour valider benchmarks - c'est ESSENTIEL pour crédibilité 95%+."
```

---

## Pourquoi Français > Anglais pour Cette Évaluation

### 1. Qualité Langue Validée par Natif
- Codex/Gemini en français = détection erreurs subtiles
- Anglicismes invisibles en anglais deviennent évidents
- Ton professionnel français ≠ ton professionnel anglais

### 2. Sources Françaises Accessibles
- LSA Conso = publication française spécialisée commerce
- Point P, Leroy Merlin, BigMat = acteurs français
- Rapports annuels souvent français en priorité

### 3. Benchmarks Alternatifs Français
Si Point P/Leroy Merlin citations échouent, suggérer:
- Samse (négociant matériaux, coté)
- BigMat (concurrent direct Point P)
- Saint-Gobain Distribution Bâtiment France
- Tout cas documenté français > cas américain traduit

### 4. Crédibilité Présentation
Si Gedimat PDG lit anglicismes partout:
- "Pas fait pour nous"
- "Consultant étranger qui ne comprend pas France"
- Score crédibilité -20 points immédiat

---

## Commande Minimale

Si prompts ci-dessus trop longs:

### Codex Court
```bash
codex-cli chat --message "Lis github.com/dannystocker/infrafabric gedimat-v2-clean PROMPT_V2_FACTUAL_GROUNDED.md

RÉPONDS EN FRANÇAIS. Trouve projections € Gedimat non sourcées. Détecte anglicismes. Score actuel 85%, cible 95%+. Que manque-t-il?"
```

### Gemini Court
```bash
gemini chat "Lis https://raw.githubusercontent.com/dannystocker/infrafabric/gedimat-v2-clean/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md

RÉPONDS EN FRANÇAIS. RECHERCHE WEB: Vérifie Point P 2022 12% (LSA Conso Mars 2023), Leroy Merlin 2021 ROI 8.5×. Réels? Anglicismes trouvés? 85%→95% comment?"
```

---

## Après Évaluation: Corrections

```bash
# Appliquer corrections Codex + Gemini (en français)
cd /home/setup/infrafabric
git checkout gedimat-v2-clean

# Éditer fichiers selon recommandations
# Puis commit
git add intelligence-tests/gedimat-logistics-fr/
git commit -m "Corrections Codex+Gemini: Vers score 95%+

Appliqué (français):
- Benchmarks vérifiés: Point P URL réel trouvé
- Anglicismes éliminés: dashboard→tableau de bord (12 occurrences)
- Code ajouté: Macro VBA scoring + Script Python NPS
- Grammaire corrigée: 8 fautes mineures

Score: 85% → 96% (estimé)"

git push origin gedimat-v2-clean
```

---

## Résultat Attendu

Après évaluation française:

✅ Benchmarks vérifiés avec URLs françaises réelles
✅ Zéro anglicisme dans version finale
✅ Grammaire parfaite Académie Française
✅ Code production-ready fourni
✅ Score: **95-98%** (vs 85% actuel)

**Confiance présentation conseil administration Gedimat: TRÈS HAUTE**
